# from langchain_groq import ChatGroq
# from config import GROQ_API_KEY, GENERATOR_MODEL


# def run_generator(
#     query: str,
#     final_context: str,
#     crag_triggered: bool,
#     recovery_succeeded: bool,
#     episodic_lessons: list[str]
# ) -> str:
#     """
#     Synthesizes the final NSE research report from verified context.

#     Three cases handled explicitly:
#     1. Clean path (crag_triggered=False): context from vector store
#     2. CRAG success (crag_triggered=True, recovery=True): context from web
#     3. CRAG failure (crag_triggered=True, recovery=False): context unreliable

#     Case 3 returns an honest insufficient-data response rather than
#     hallucinating on bad context. This is uncertainty made actionable.

#     Episodic lessons are passed in for awareness — the generator uses them
#     to frame responses appropriately for known query categories.
#     """

#     # ── Case 3: recovery failed — don't synthesize from unreliable context ──
#     if crag_triggered and not recovery_succeeded:
#         return (
#             f"## Research Report — Insufficient Data\n\n"
#             f"**Query:** {query}\n\n"
#             f"**Status:** This query requires current information that could not be "
#             f"retrieved reliably. The vector store did not contain relevant documents, "
#             f"and web search did not return financially usable content.\n\n"
#             f"**Recommendation:** Retry with a more specific query, or specify a "
#             f"date range or ticker symbol to narrow the search scope.\n\n"
#             f"**Confidence:** Low — no synthesis attempted to avoid hallucination."
#         )

#     # ── Context source framing ──
#     if crag_triggered and recovery_succeeded:
#         context_note = (
#             "Note: This report is based on live web search results retrieved via "
#             "CRAG fallback. The vector store did not have sufficient coverage for "
#             "this query. Web sources are current but less structured than proprietary data."
#         )
#     else:
#         context_note = (
#             "Note: This report is based on indexed NSE document context from "
#             "the vector store. Data reflects the most recent seeded documents."
#         )

#     # ── Lessons block ──
#     lessons_block = ""
#     if episodic_lessons:
#         formatted = "\n".join(f"- {l}" for l in episodic_lessons)
#         lessons_block = f"\nKnown context from previous runs:\n{formatted}\n"

#     system_prompt = f"""You are a senior NSE equity research analyst producing structured research reports.

# Your job: synthesize the provided context into a clear, structured research report.

# Report structure (always follow this exactly):
# ## Executive Summary
# One paragraph. Direct answer to the query. No hedging unless genuinely uncertain.

# ## Key Financials
# Bullet points only. Revenue, PE, margins, 52-week range, market cap if available.
# If a figure is not in the context, write "Not available in current data" — do not estimate.

# ## Analyst View
# What analysts recommend. Price targets if available. Consensus direction.
# If not in context: "Analyst data not available in current retrieval."

# ## Macro Context
# Relevant sector or macro factors mentioned in the context.
# If not applicable to the query: omit this section entirely.

# ## Risk Factors
# 2-3 specific risks based on the context. Not generic market risks.

# ## Verdict
# One sentence. Bullish / Bearish / Neutral with the single strongest reason.

# Rules:
# - Never invent figures. If data is absent, say so explicitly.
# - Never use phrases like "as an AI" or "I cannot"
# - Keep language precise and analytical, not promotional
# - If context is web-sourced, note where specific figures came from
# {lessons_block}
# {context_note}"""

#     user_message = f"""Query: {query}

# Context:
# {final_context}

# Generate the research report."""

#     llm = ChatGroq(
#         api_key=GROQ_API_KEY,
#         model=GENERATOR_MODEL,
#         temperature=0.2
#     )

#     response = llm.invoke([
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_message}
#     ])

#     return response.content.strip()

# from langchain_groq import ChatGroq
from utils.llm_factory import get_llm
# from config import GROQ_API_KEY, GENERATOR_MODEL
from config import GENERATOR_MODEL

def run_generator(
    query: str,
    final_context: str,
    sub_queries: list[str],
    missing_info: list[str],
    crag_triggered: bool,
    recovery_succeeded: bool,
    episodic_lessons: list[str]
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

    # ── System Prompt with Domain Guardrails ──
    system_prompt = f"""You are a senior NSE equity research analyst producing structured research reports.

Your job: synthesize the provided context into a clear, structured research report that directly answers the primary query.

CRITICAL GUARDRAILS AGAINST HALLUCINATION:
1. DOMAIN ISOLATION: Do NOT confuse US Federal Reserve (Fed/FOMC) parameters with the Reserve Bank of India (RBI/MPC). The RBI utilizes the Repo Rate. If the context contains US macroeconomic policy text, ignore it entirely.
2. FINANCIAL SANITY CHECK: Indian banking institutions structurally trade at Price-to-Earnings (PE) multiples between 8x and 30x. If the data block displays thousands (e.g., PE: 1234.70), it is a scraping error—do NOT print it; state "Not available".
3. CONTEXT GROUNDING: If specific parameters are missing from the context block, do not extrapolate or guess from pre-training. Maintain a clean "Not available" fallback.

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