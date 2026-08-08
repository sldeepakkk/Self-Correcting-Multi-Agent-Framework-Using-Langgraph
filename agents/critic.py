from pydantic import BaseModel, Field
from utils.llm_factory import get_llm
from utils.llm_json import invoke_with_retry
from config import CRITIC_MODEL


class ThesisCritique(BaseModel):
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


def run_premise_check(query: str, reasoning_lessons: list[str] = None) -> dict:
    """
    Cheap, early, plain-text (NOT JSON) check for institutional/personnel
    misattribution. Runs before retrieval/generation. Now loads reasoning
    lessons as priors — accumulated patterns from past corrections inform
    what to watch for on this run.
    """
    lessons_block = ""
    if reasoning_lessons:
        formatted = "\n".join(f"- {l}" for l in reasoning_lessons)
        lessons_block = f"""
PATTERNS LEARNED FROM PREVIOUS CORRECTIONS (apply these when relevant):
{formatted}
"""

    system_prompt = f"""You are a fast fact-checker. Check ONLY for one narrow
class of error: verifiable institutional or personnel misattribution — wrong
chairperson/governor for an organization, wrong regulator or authority for a
decision, wrong country's central bank for a policy action.

Do NOT check market opinions, predictions, or subjective claims. ONLY check
WHO or WHICH ORGANIZATION is stated to have done something.
{lessons_block}
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


def run_thesis_critic(
    query: str,
    response: str,
    context: str,
    is_compound: bool = False,
    evidence_confidence: str = "medium",
    reasoning_lessons: list[str] = None
) -> ThesisCritique:
    """
    Acceptance-checker, not flaw-hunter. Default assumption: response is
    acceptable. Rejects only against four named bars. Now loads reasoning
    lessons as priors — patterns distilled from past resolved defects.
    """
    lessons_block = ""
    if reasoning_lessons:
        formatted = "\n".join(f"- {l}" for l in reasoning_lessons)
        lessons_block = f"""
PATTERNS LEARNED FROM PREVIOUS RESOLVED DEFECTS (weight these when checking):
{formatted}
"""

    system_prompt = f"""You are a reasoning ACCEPTANCE CHECKER, not a flaw-hunter.
Your default assumption is that the response is ACCEPTABLE. You only reject it
if it fails one of four specific, concrete bars below. If none of these bars
are failed, you MUST set thesis_sound=true, even if the writing could
theoretically be more rigorous.

ACCEPTANCE BARS — reject ONLY if:
1. PREMISE: the query contained a factual institutional/personnel error the
   response did NOT correct. If the response already states the correction
   (e.g. "X is actually Y, not Z"), this bar is PASSED — leave premise_issues
   EMPTY, do not describe the correction itself as an issue.
2. FABRICATION: the response states a SPECIFIC NUMBER, DATE, or NAMED FACT
   that has NO corresponding basis anywhere in the provided context.
   Reasonable characterizations of real data (e.g. "strong fundamentals"
   when a real PE ratio and revenue figure support that framing) PASS this bar.
3. CONTRADICTION: the verdict directly ignores or contradicts specific
   evidence present elsewhere in the same response's own context.
4. UNCALIBRATED CERTAINTY: the response gives an unqualified directional
   verdict (pure "Bullish"/"Bearish" with no hedge at all) while more than
   half of requested data fields were unavailable. A verdict that already
   contains ANY hedge language ("may", "likely", "depends on", "however")
   PASSES this bar regardless of remaining uncertainty in the topic.
5. MISSING CRITICAL DATA: the response explicitly states that key financial metrics,
   trend data, or recent figures are missing/unavailable (e.g., "without recent data, it is
   challenging to provide a precise trend analysis"), but that data is concrete and findable via web search.
   If so, set needs_evidence to a single concrete search query (e.g. "HDFC Bank recent net interest margin trend")
   and thesis_sound=false.
6. UNLABELED INFERENCE: if evidence confidence for this run was LOW, the
   response must clearly flag which claims are inference vs verified. If
   it presents inferred reasoning as settled fact with no hedge, this bar
   is FAILED. If evidence confidence was HIGH or MEDIUM, this bar
   automatically PASSES regardless of hedging style.
7. UNAUTHORITATIVE SOURCING: the response presents a specific number as
   fact when it originates from a named individual blogger/forum
   contributor's personal calculation, without clearly labeling it as
   one independent estimate rather than a verified figure.

Do NOT flag: normal analytical confidence, reasonable data-grounded
characterizations, writing style, or requests for "more detail." Those are
not defects. A response that already hedges once is calibrated enough.

The response may be in any structure — do not penalize it for lacking
specific section headers. Judge only the SUBSTANCE against the bars below.

thesis_sound = true unless a SPECIFIC bar above is failed with a named reason.
If you cannot name which of the numbered bars was violated, thesis_sound
MUST be true.
{lessons_block}
needs_evidence: if unsupported_claims or missing_requirements point to
something SPECIFIC and SEARCHABLE that could be verified by one targeted
web search, state it as a single concrete search query. Leave empty otherwise.

Respond ONLY with valid JSON:
{{
  "grounding_score": 0.0, "completeness_score": 0.0, "reasoning_score": 0.0,
  "hallucination_risk": 0.0, "query_coverage": 0.0,
  "premise_issues": [], "unsupported_claims": [], "missing_requirements": [],
  "overconfidence_flags": [], "thesis_sound": true,
  "revision_instructions": "", "weakest_dimension": "", "needs_evidence": ""
}}"""
    
    
    user_message = f"""Evidence confidence for this run: {evidence_confidence}

Original Query: {query}

Context Provided to Generator:
{context}

Generator's Response:
{response}

Check this response against the acceptance bars."""

    llm = get_llm(CRITIC_MODEL, temperature=0.15)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])
        return ThesisCritique(**parsed)
    except Exception as e:
        print(f"[CRITIC] Parse failed: {e}. Failing open — treating thesis as sound.")
        return ThesisCritique(thesis_sound=True)


# ── Revision instruction builder for the weakest critique dimension ───────────

def build_revision_instruction(critique: dict) -> str:
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


from utils.llm_factory import get_groq_client  # raw client needed for tool calling, not the langchain wrapper
from config import CRITIC_MODEL
import json


CRITIC_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_for_evidence",
            "description": (
                "Search the web for one specific missing fact needed to "
                "support a claim in the response. Use this ONLY when the "
                "response is missing a concrete, findable piece of evidence — "
                "not for improving wording or tone."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "A specific, concrete search query — not a vague topic"
                    },
                    "reason": {
                        "type": "string",
                        "description": "What claim in the response this evidence would support or correct"
                    }
                },
                "required": ["search_query", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "revise_response",
            "description": (
                "Rewrite the response to fix a reasoning defect that does NOT "
                "require new evidence — e.g. an unaddressed false premise in "
                "the query, an overconfident verdict given thin data, an "
                "unsupported claim that should be hedged or removed, or "
                "citing a non-authoritative source as fact."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "instructions": {
                        "type": "string",
                        "description": "Precise instructions for what to fix and how"
                    }
                },
                "required": ["instructions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "accept_response",
            "description": (
                "The response is sound: no unaddressed false premises, no "
                "unsupported claims stated as fact, confidence matches the "
                "evidence available, and it actually answers the question asked. "
                "Call this when no further action is needed."
            ),
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def run_agentic_critic_step(
    query: str,
    response: str,
    context: str,
    evidence_confidence: str,
    reasoning_lessons: list[str],
    conversation_history: list[dict]
) -> dict:
    """
    ONE step of the agentic loop. The model itself chooses which tool to
    call — the decision of what to do next lives in the model's own
    reasoning, not in a Python if/elif chain reading a JSON verdict.

    Returns: {"tool_name": str, "tool_args": dict, "raw_message": dict}
    conversation_history accumulates across steps so the model has memory
    of what it already tried this run (e.g. don't search for the same
    thing twice).
    """
    lessons_block = ""
    if reasoning_lessons:
        formatted = "\n".join(f"- {l}" for l in reasoning_lessons)
        lessons_block = f"\nPatterns learned from previous resolved defects:\n{formatted}\n"

    system_prompt = f"""You are a reasoning critic for a financial research system.
You decide what action to take next — you are not filling out a form, you
are choosing a tool to call based on your own judgment.

Evidence confidence for this run: {evidence_confidence}
{lessons_block}
Evaluate the response against these standards:
1. PREMISE: did the query contain a factual institutional/personnel error
   the response failed to correct?
2. FABRICATION: does the response state a specific number/date/fact with
   no basis in the context?
3. CONTRADICTION: does the verdict ignore evidence present elsewhere in
   the same context?
4. CALIBRATION: is confidence appropriate given how much evidence exists?
5. SOURCE AUTHORITY: is a personal blogger's calculation cited as if it
   were a verified figure?

Based on what you find, call exactly ONE tool:
- search_for_evidence: only if a SPECIFIC, findable fact is missing
- revise_response: if the fix doesn't need new evidence, just better reasoning
- accept_response: if none of the five issues above apply

Do not call search_for_evidence more than once per conversation — check
the history below first."""

    query_context = f"""Original Query: {query}

Context available to the response:
{context}

Response to evaluate:
{response}"""

    messages = [{"role": "system", "content": system_prompt}]
    if not conversation_history:
        messages.append({"role": "user", "content": query_context})
    else:
        messages.append({"role": "user", "content": query_context})
        messages.extend(conversation_history)

    client = get_groq_client()
    completion = client.chat.completions.create(
        model=CRITIC_MODEL,
        messages=messages,
        tools=CRITIC_TOOLS,
        tool_choice="required",
        temperature=0.1
    )

    msg = completion.choices[0].message

    if not msg.tool_calls:
        # Model failed to call a tool — fail safe to accept, same
        # fail-open principle used everywhere else in this codebase
        return {"tool_name": "accept_response", "tool_args": {}, "raw_message": None}

    call = msg.tool_calls[0]
    return {
        "tool_name": call.function.name,
        "tool_args": json.loads(call.function.arguments),
        "raw_message": msg,
        "tool_call_id": call.id
    }