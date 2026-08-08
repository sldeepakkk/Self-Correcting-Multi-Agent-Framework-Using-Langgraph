from typing import Any, Mapping, Optional
import re
from utils.llm_factory import get_llm
from config import GENERATOR_MODEL
from agents.critic import build_revision_instruction


def _extract_query_specifics(query: str) -> list[str]:
    """
    Pulls concrete, checkable numeric specifics from the query — dollar
    amounts, percentages, rupee figures, basis points. These are exactly
    the things a topically-relevant but generic search result can miss
    while still scoring high on the aspect judge's topic/factual_density
    axes. A query naming $50/barrel and 8% appreciation deserves a
    different confidence level than one asking a general question,
    even if both retrieve equally "relevant" content.
    """
    patterns = [
        r'\$\d+(?:\.\d+)?',
        r'\d+(?:\.\d+)?\s*%',
        r'\d+(?:\.\d+)?\s*percent',
        r'₹\s*\d+[\d,]*',
        r'\d+\s*(?:lakh|crore|basis points?|bps)',
        r'\d+(?:\.\d+)?\s*per\s*barrel',
    ]
    specifics = []
    for p in patterns:
        specifics.extend(re.findall(p, query, flags=re.IGNORECASE))
    return specifics


def compute_evidence_confidence(state: Mapping[str, Any]) -> str:
    context = state.get("final_context", "")
    if not context or len(context.strip()) < 100:
        return "low"

    query = state.get("query", "")
    specifics = _extract_query_specifics(query)

    def _is_specific_covered(s: str) -> bool:
        s_low = s.lower()
        if s_low in context.lower():
            return True
        digits = re.findall(r'\d+', s)
        if digits and any(d in context for d in digits):
            return True
        return False

    covered = (not specifics) or any(_is_specific_covered(s) for s in specifics)
    has_substance = bool(re.search(r'\d', context)) and any(
        kw in context.lower() for kw in [
            '%', 'margin', 'rate', 'profit', 'nim', 'crore', 'lakh', '₹',
            'price', 'growth', 'quarter', 'bank', 'fy', 'basis', 'bps'
        ]
    )

    if len(context) > 500 and (covered or has_substance):
        return "high"
    if covered or has_substance or len(context) > 250:
        return "medium"
    return "low"


def run_generator(
    query: str,
    final_context: str,
    sub_queries: Optional[list[str]] = None,
    premise_correction: str = "",
    evidence_confidence: str = "medium",
    episodic_lessons: Optional[list[str]] = None
) -> str:
    """
    No fixed section template. The generator organizes its answer around
    what the QUESTION actually needs, not a predetermined form. This is
    the fix for the pattern seen across every benchmark loss: forcing a
    causal-chain question or a DCF construction into
    Executive-Summary/Key-Financials/Analyst-View boxes fragmented the
    argument and left boxes empty even when the underlying reasoning
    was sound. The rules below are about SUBSTANCE, not FORMAT.
    """
    episodic_lessons = episodic_lessons or []
    sub_queries = sub_queries or []

    confidence_block = ""
    if evidence_confidence == "low":
        confidence_block = """
EVIDENCE CONFIDENCE: LOW. Reason from well-established domain mechanisms
where retrieved evidence is thin. Explicitly label such reasoning as
inference ("based on typical mechanism, X would likely...") rather than
stating it as a confirmed fact. Do not force yourself to report a field
as empty just because the template used to require it — if you don't
have a number, work around it in prose rather than leaving a blank line."""
    elif evidence_confidence == "medium":
        confidence_block = """
EVIDENCE CONFIDENCE: MEDIUM. Use retrieved evidence as your primary basis.
Clearly mark any gaps you fill with general domain reasoning."""

    premise_block = ""
    if premise_correction:
        premise_block = f"""
MANDATORY CORRECTION — the query itself contains a factual error: {premise_correction}
State this correction plainly near the start of your answer, then proceed
with the actual analysis."""

    lessons_block = ""
    if episodic_lessons:
        formatted = "\n".join(f"- {l}" for l in episodic_lessons)
        lessons_block = f"\nPatterns learned from previous runs:\n{formatted}\n"

    system_prompt = f"""You are a senior financial analyst writing a research answer.

Write the answer in whatever structure genuinely serves the QUESTION ASKED —
do not force every answer into the same fixed sections. A causal-chain
question deserves a chain of reasoning. A valuation construction deserves
a walk through the model's assumptions and output. A comparison deserves
a comparison. Use headers where they help the reader, skip them where they
don't. Write like an analyst answering a specific question, not filling
out a form.

SUBSTANCE RULES — these apply regardless of structure:
1. DOMAIN ISOLATION: Do not confuse US Federal Reserve actions/parameters
   with the Reserve Bank of India, or any other country's institutions
   with India's, unless the query is specifically about that country.
2. NUMERICAL SANITY: If a retrieved figure looks like a scraping error
   (e.g. an Indian bank PE of 1000+), say the data looks unreliable
   rather than reporting it as fact.
3. GROUNDING: Never present inference as verified fact. Say what you know
   versus what you're reasoning through.
4. SOURCE AUTHORITY: If a specific number (WACC, terminal growth,
   intrinsic value) comes from a single named individual's blog or forum
   post rather than a company filing, index provider, or established
   research desk, attribute it explicitly as one independent estimate —
   never present it as a verified or consensus figure. Prefer building
   your own reasonable assumption from stated industry norms over citing
   an unverified personal calculation.
5. ANSWER THE ACTUAL QUESTION: If the query asks for a portfolio, name
   companies and allocations. If it asks to compare two things, compare
   them directly. Do not retreat into generic macro commentary when the
   query asked for something specific and concrete.
{premise_block}
{confidence_block}
{lessons_block}
Context available to you (may be partial — reason with what's here, note
what isn't):
{final_context}"""

    sub_q_block = ""
    if sub_queries:
        formatted_sq = "\n".join(f"- {sq}" for sq in sub_queries)
        sub_q_block = f"\nSub-questions this breaks down into, for your reference:\n{formatted_sq}\n"

    user_message = f"""Query: {query}
{sub_q_block}
Write the answer."""

    llm = get_llm(GENERATOR_MODEL, temperature=0.2)
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])
    
    content = response.content if isinstance(response.content, str) else str(response.content)
    return content.strip()


# ---------------------------------------------------------
# Generator Self-Revision
# ---------------------------------------------------------

def run_generator_revision(
    query: str,
    original_response: str,
    critique: Mapping[str, Any] | dict[str, Any] | Any,
    final_context: str
) -> str:
    """
    Revises the generator's own prior response using specific critique feedback.
    This is the reasoning-loop analog to how CRAG retry uses the judge's
    missing_information — except here the feedback targets the ARGUMENT,
    not the search query.
    """
    if hasattr(critique, "model_dump"):
        critique_dict = critique.model_dump()
    elif isinstance(critique, dict):
        critique_dict = critique
    else:
        critique_dict = dict(critique)

    issues = []
    if critique_dict.get("premise_issues"):
        issues.append("Premise issues in the query: " + "; ".join(critique_dict["premise_issues"]))
    if critique_dict.get("unsupported_claims"):
        issues.append("Unsupported claims to remove or hedge: " + "; ".join(critique_dict["unsupported_claims"]))
    if critique_dict.get("missing_requirements"):
        issues.append("Missing requirements to address: " + "; ".join(critique_dict["missing_requirements"]))
    if critique_dict.get("overconfidence_flags"):
        issues.append("Overconfident verdict to soften: " + "; ".join(critique_dict["overconfidence_flags"]))

    issues_block = "\n".join(f"- {i}" for i in issues) if issues else "- General soundness concern"
    # Boosting-style targeting: prioritize the single worst dimension this round
    instruction = build_revision_instruction(critique_dict)

    system_prompt = f"""You previously wrote a financial research report. A critic
identified specific issues with your argument. Rewrite the answer addressing EVERY issue below explicitly. 
Keep whatever structure best serves the question — do not force a fixed template. If the query
contained a false premise, add an explicit note correcting it before proceeding
with analysis. If the verdict was overconfident given thin data, soften it and
explain why. Do not discard real data you already had — only fix the flagged
reasoning issues.

If the context below contains a section titled "## Critic-Requested Evidence",
that material was specifically fetched to address one of the issues listed —
prioritize using it to directly resolve that issue, don't ignore it.

Issues to fix:
{issues_block}

Specific instruction: {instruction}"""

    user_message = f"""Original Query: {query}

Context:
{final_context}

Your Previous Response:
{original_response}

Rewrite it, fixing every flagged issue."""

    llm = get_llm(GENERATOR_MODEL, temperature=0.2)
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    content = response.content if isinstance(response.content, str) else str(response.content)
    return content.strip()