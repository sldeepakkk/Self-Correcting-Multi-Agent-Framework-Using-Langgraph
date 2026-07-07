from pydantic import BaseModel, Field
from utils.llm_factory import get_llm
from utils.llm_json import invoke_with_retry
from config import CRITIC_MODEL


class ThesisCritique(BaseModel):
    """
    The output of the reasoning-loop critic. Distinct from the retrieval judge:
    this evaluates the GENERATOR'S OWN ARGUMENT, not source material adequacy.

    Float scores are treated as coarse signals only — small models anchor to
    canonical values, so a 0.74 vs 0.79 shift is noise. The concrete lists
    (unsupported_claims, missing_requirements, etc.) are the trustworthy signal;
    convergence is measured by whether these lists shrink, not by score deltas.
    """
    grounding_score: float = Field(ge=0.0, le=1.0, default=1.0)
    completeness_score: float = Field(ge=0.0, le=1.0, default=1.0)
    reasoning_score: float = Field(ge=0.0, le=1.0, default=1.0)
    hallucination_risk: float = Field(ge=0.0, le=1.0, default=0.0)
    query_coverage: float = Field(ge=0.0, le=1.0, default=1.0)

    premise_issues: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    overconfidence_flags: list[str] = Field(default_factory=list)

    thesis_sound: bool = True
    revision_instructions: str = ""
    weakest_dimension: str = ""
    needs_evidence: str = ""


def run_thesis_critic(query: str, response: str, context: str) -> ThesisCritique:
    """
    Adversarial critique of the response's ARGUMENT — checks things the
    retrieval judge structurally cannot, because it never sees the final answer.
    Fails OPEN (thesis_sound=True) on parse failure — this is a quality layer,
    not a safety gate; a critic failure should never block an existing answer.
    """
    system_prompt = """You are an adversarial reasoning critic. A separate system
already checked whether retrieval/search was adequate — you do NOT re-check that.
You check whether the FINAL WRITTEN RESPONSE'S ARGUMENT is sound.

Score five dimensions from 0.0 to 1.0:
- grounding_score: does every claim trace to the provided context?
- completeness_score: does the response address every part of the query?
- reasoning_score: is the argument internally consistent, not contradictory?
- hallucination_risk: how much does the response state as fact without support? (higher = worse)
- query_coverage: fraction of explicit query requirements actually answered

Also identify, as concrete short items (not scores):
- premise_issues: does the ORIGINAL QUERY assert something factually wrong that the
  RESPONSE FAILED TO CORRECT? Only list issues the response did NOT already address.
  If the response already corrects a false premise, leave this empty.
- unsupported_claims: specific claims stated as fact with no basis in the context
- missing_requirements: specific parts of the query never actually answered
- overconfidence_flags: definitive verdicts given despite thin/mixed evidence

weakest_dimension: name the ONE dimension above (grounding, completeness, reasoning,
hallucination_risk, or query_coverage) that most needs fixing. This targets the next
revision at the single biggest problem, not everything at once.

needs_evidence: if unsupported_claims or missing_requirements point to something
SPECIFIC and SEARCHABLE (a fact, a figure, an analyst statement) that could be
verified or filled by one targeted web search, state it as a single concrete
search query. Leave empty if the issue is about reasoning/tone/structure rather
than a missing fact.

thesis_sound = true only if hallucination_risk <= 0.3 AND all four concrete lists are empty.
revision_instructions: if not sound, ONE concise instruction for the rewrite.

IMPORTANT: Never include double-quote characters inside any string value.
Paraphrase text from the query or response instead of quoting it verbatim.
Keep every list item under 15 words.

Respond ONLY with valid JSON:
{
  "grounding_score": 0.0, "completeness_score": 0.0, "reasoning_score": 0.0,
  "hallucination_risk": 0.0, "query_coverage": 0.0,
  "premise_issues": [], "unsupported_claims": [], "missing_requirements": [],
  "overconfidence_flags": [], "thesis_sound": true,
  "revision_instructions": "", "weakest_dimension": "", "needs_evidence": ""
}"""

    user_message = f"""Original Query: {query}

Context Provided to Generator:
{context[:2000]}

Generator's Response:
{response}

Critique this response's argument."""

    llm = get_llm(CRITIC_MODEL, temperature=0.20)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])
        return ThesisCritique(**parsed)
    except Exception as e:
        print(f"[CRITIC] Parse failed: {e}. Failing open — treating thesis as sound.")
        return ThesisCritique(thesis_sound=True)


def build_revision_instruction(critique: dict) -> str:
    """
    Boosting-style targeting: fix the single worst dimension this round,
    not everything at once. Same principle as a boosting model's next tree
    targeting the largest residual error instead of re-fitting everything.
    """
    weakest = critique.get("weakest_dimension", "")
    scores = {
        "grounding": critique.get("grounding_score", 1.0),
        "completeness": critique.get("completeness_score", 1.0),
        "reasoning": critique.get("reasoning_score", 1.0),
        "hallucination_risk": 1.0 - critique.get("hallucination_risk", 0.0),
        "query_coverage": critique.get("query_coverage", 1.0),
    }
    if weakest not in scores:
        weakest = min(scores, key=scores.get)

    instructions = {
        "grounding": "Every claim must trace to the provided context. Remove or hedge anything that doesn't.",
        "completeness": f"Missing requirements not addressed: {critique.get('missing_requirements', [])}",
        "reasoning": "The argument has an internal inconsistency — fix the logical flow, don't just restate facts.",
        "hallucination_risk": f"Unsupported claims to remove: {critique.get('unsupported_claims', [])}",
        "query_coverage": f"Parts of the original query never answered: {critique.get('missing_requirements', [])}",
    }
    return instructions.get(weakest, critique.get("revision_instructions", ""))


def has_converged(prev_critique: dict, new_critique: dict) -> bool:
    """
    Convergence uses ISSUE COUNTS, not raw float scores — small models anchor
    on scores, so a 0.74 to 0.79 shift is noise. A concrete list shrinking
    from 3 items to 1 is real signal. Mirrors early stopping in boosting:
    stop when the residual (issue count) stops shrinking.
    """
    def issue_count(c):
        return (len(c.get("unsupported_claims", [])) +
                len(c.get("missing_requirements", [])) +
                len(c.get("overconfidence_flags", [])) +
                len(c.get("premise_issues", [])))

    if new_critique.get("hallucination_risk", 0.0) > 0.3:
        return False

    prev_issues = issue_count(prev_critique)
    new_issues = issue_count(new_critique)

    return new_issues == 0 or new_issues >= prev_issues

def run_premise_check(query: str) -> dict:
    """
    Cheap, early, plain-text (NOT JSON) check for institutional/personnel
    misattribution in the raw query — e.g. wrong regulator, wrong chair,
    wrong authority for a decision. Runs BEFORE retrieval/generation, so a
    caught false premise is baked into context deterministically, not
    contingent on the downstream thesis critic's JSON call succeeding.

    Deliberately avoids JSON: the exact failure that crashed the thesis
    critic (unescaped quotes in a string value) can't happen with simple
    line-based parsing. This is the primary fix for false premises —
    the thesis critic's premise_issues field becomes a backup, not the
    only line of defense.
    """
    system_prompt = """You are a fast fact-checker. Check ONLY for one narrow
class of error: verifiable institutional or personnel misattribution — wrong
chairperson/governor for an organization, wrong regulator or authority for a
decision, wrong country's central bank for a policy action.

Do NOT check market opinions, predictions, or subjective claims. ONLY check
WHO or WHICH ORGANIZATION is stated to have done something.

Respond in EXACTLY this format, nothing else, no markdown:
FLAG: YES or NO
CORRECTION: one plain sentence if FLAG is YES, or NONE if FLAG is NO"""

    user_message = f"Query: {query}\n\nCheck for institutional/personnel errors."

    llm = get_llm(CRITIC_MODEL, temperature=0.0)
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    raw = response.content.strip()
    flag = False
    correction = ""
    for line in raw.split("\n"):
        line = line.strip()
        if line.upper().startswith("FLAG:"):
            flag = "yes" in line.lower()
        elif line.upper().startswith("CORRECTION:"):
            correction = line.split(":", 1)[1].strip()
            if correction.upper() == "NONE":
                correction = ""

    return {"premise_flag": flag, "premise_correction": correction}