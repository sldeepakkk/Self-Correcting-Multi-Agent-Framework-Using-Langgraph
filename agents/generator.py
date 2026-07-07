# from langchain_groq import ChatGroq
from utils.llm_factory import get_llm
# from config import GROQ_API_KEY, GENERATOR_MODEL
from config import GENERATOR_MODEL
from agents.critic import build_revision_instruction

def run_generator(
    query: str,
    final_context: str,
    sub_queries: list[str],
    missing_info: list[str],
    premise_correction: str = "",   
    crag_triggered: bool = False,
    recovery_succeeded: bool = False,
    episodic_lessons: list[str] = None
) -> str:
    """
    Synthesizes the final NSE research report from verified context.
    
    Now explicitly anchors the generator's attention to the execution plan 
    (sub_queries) and corrective feedback (missing_info) to prevent 
    attention drift and hallucination.
    """

    # ── Redundant Safety Net ──
    # nodes.py already short-circuits this, but keeping it ensures the 
    # function contract remains safe if called in isolation.
    if crag_triggered and not recovery_succeeded:
        return (
            "## Research Report — Insufficient Data\n\n"
            f"**Query:** {query}\n\n"
            "**Status:** This query requires current information that could not be "
            "retrieved reliably. Web search did not return financially usable content.\n\n"
            "**Confidence:** Low — no synthesis attempted to avoid hallucination."
        )

    # ── Context Source Framing ──
    if crag_triggered and recovery_succeeded:
        context_note = (
            "Note: This report is based on live web search results retrieved via "
            "CRAG fallback. Sources are current but less structured than proprietary data."
        )
    else:
        context_note = (
            "Note: This report is based on indexed NSE document context from "
            "the vector store. Data reflects the most recent seeded documents."
        )

    # ── Traceability Blocks ──
    sq_text = "\n".join([f"- {sq}" for sq in sub_queries])
    
    retry_text = ""
    if missing_info:
        retry_text = "\nTargeted Recovery Dimensions Extracted by Judge:\n" + "\n".join([f"- {mi}" for mi in missing_info])

    lessons_block = ""
    if episodic_lessons:
        formatted = "\n".join(f"- {l}" for l in episodic_lessons)
        lessons_block = f"\nKnown context from previous runs:\n{formatted}\n"

    premise_block = ""
    if premise_correction:
        premise_block = f"""
MANDATORY CORRECTION — a fact-check found an institutional/personnel error
in the query itself: {premise_correction}
You MUST state this correction as the first sentence of your Executive
Summary before proceeding with any analysis. Do not silently proceed as
if the query's premise were accurate."""
        
# ── System Prompt with Domain Guardrails ──
    system_prompt = f"""You are a senior NSE equity research analyst producing structured research reports.

Your job: synthesize the provided context into a clear, structured research report that directly answers the primary query.

CRITICAL GUARDRAILS AGAINST HALLUCINATION:
1. DOMAIN ISOLATION: Do NOT confuse US Federal Reserve (Fed/FOMC) parameters with the Reserve Bank of India (RBI/MPC). The RBI utilizes the Repo Rate. If the context contains US macroeconomic policy text, ignore it entirely.
2. FINANCIAL SANITY CHECK: Indian banking institutions structurally trade at Price-to-Earnings (PE) multiples between 8x and 30x. If the data block displays thousands (e.g., PE: 1234.70), it is a scraping error—do NOT print it; state "Not available".
3. CONTEXT GROUNDING: If specific parameters are missing from the context block, do not extrapolate or guess from pre-training. Maintain a clean "Not available" fallback.
{premise_block}

Report structure (always follow this exactly):
## Executive Summary
One paragraph. Direct answer to the query based ONLY on the context.

## Key Financials
Bullet points only. Revenue, PE, margins, 52-week range, market cap.
If a figure is not in the context, write "Not available in current data".

## Analyst View
What analysts recommend. Price targets if available. Consensus direction.
If not in context: "Analyst data not available in current retrieval."

## Macro Context
Relevant sector or macro factors mentioned in the context.
If not applicable to the query: omit this section entirely.

## Risk Factors
2-3 specific risks based on the context.

HYBRID CONTEXT HANDLING:
If the context contains both "## Web Search Context" and "## Vector Store Context" 
sections, treat the Vector Store section as your primary source for company-specific 
figures (revenue, margins, PE, analyst targets) and the Web Search section as your 
primary source for current macro/policy context (rates, dates, recent events). 
Do not blend uncertain figures from both sections — cite the more specific source 
for each individual data point.

FORMAT ADAPTATION:
If the query is about sectors, macro trends, or market-wide themes rather than
a specific company, SKIP the "Key Financials" section entirely (do not write
"Not available" placeholders) and expand "Macro Context" as the primary section
instead. Only include Key Financials when the query names a specific company
or companies with reportable financial metrics.

## Verdict
One sentence. Bullish / Bearish / Neutral with the single strongest reason.

{lessons_block}
{context_note}"""

    # ── User Message with Execution Plan Anchoring ──
    user_message = f"""Primary Query: {query}

The data retrieval engine broke this query down into the following specific research angles:
{sq_text}
{retry_text}

Verified Context Block:
{final_context}

Synthesize the final report addressing the primary query using ONLY the data points relevant to the research angles above."""

    # llm = ChatGroq(
    #     api_key=GROQ_API_KEY,
    #     model=GENERATOR_MODEL,
    #     temperature=0.1 # Lowered from 0.2 to enforce stricter adherence to context
    # )
    llm = get_llm(GENERATOR_MODEL, temperature=0.2)

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    return response.content.strip()

# ---------------------------------------------------------
# Generator Self-Revision
# ---------------------------------------------------------

def run_generator_revision(
    query: str,
    original_response: str,
    critique: dict,
    final_context: str
) -> str:
    """
    Revises the generator's own prior response using specific critique feedback.
    This is the reasoning-loop analog to how CRAG retry uses the judge's
    missing_information — except here the feedback targets the ARGUMENT,
    not the search query.
    """
    issues = []
    if critique.get("premise_issues"):
        issues.append("Premise issues in the query: " + "; ".join(critique["premise_issues"]))
    if critique.get("unsupported_claims"):
        issues.append("Unsupported claims to remove or hedge: " + "; ".join(critique["unsupported_claims"]))
    if critique.get("missing_requirements"):
        issues.append("Missing requirements to address: " + "; ".join(critique["missing_requirements"]))
    if critique.get("overconfidence_flags"):
        issues.append("Overconfident verdict to soften: " + "; ".join(critique["overconfidence_flags"]))

    issues_block = "\n".join(f"- {i}" for i in issues) if issues else "- General soundness concern"
    # Boosting-style targeting: prioritize the single worst dimension this round
    instruction = build_revision_instruction(critique)


    system_prompt = f"""You previously wrote a financial research report. A critic
identified specific issues with your argument. Rewrite the report addressing
EVERY issue below explicitly. Keep the same six-section structure. If the query
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
    return response.content.strip()