# from langchain_groq import ChatGroq
from utils.llm_factory import get_llm
from pydantic import BaseModel, Field
# from config import GROQ_API_KEY, REFLECTOR_MODEL
from config import REFLECTOR_MODEL
from utils.llm_json import invoke_with_retry


class ReflectorOutput(BaseModel):
    lesson: str = Field(
        description="One to two sentences. A specific, actionable routing or decomposition "
                    "improvement for this query category. Must be concrete enough to change "
                    "future planner or routing behaviour. Not a summary of what happened."
    )
    confidence: float = Field(
        description="Confidence that this lesson is reliable and should be applied to future runs. "
                    "0.0 = uncertain, 1.0 = highly confident. "
                    "Penalise if recovery also produced weak content. "
                    "Penalise if this is the first time this pattern was observed.",
        ge=0.0,
        le=1.0
    )
    query_category: str = Field(
        description="Category label for this query type. "
                    "Examples: large_cap_it_earnings, macro_rbi_rates, sector_defence, "
                    "nifty50_valuation, smallcap_fundamentals, fx_impact"
    )
    routing_recommendation: str = Field(
        description="One of: vector_store_sufficient | web_search_preferred | mixed"
    )


def run_reflector(
    query: str,
    sub_queries: list[str],
    trace: list[dict],
    judge_score: float,
    recovery_succeeded: bool
) -> ReflectorOutput | None:
    """
    Reads the execution trace and distills one compressed, actionable lesson.

    Returns None on parse failure after retries — the caller (reflector_node)
    must check for None and skip writing a lesson entirely. Unlike the judge,
    there is no safe "fabricated lesson" to fall back to here: a guessed
    lesson written to episodic memory would pollute future planner behaviour
    with content nobody actually verified. Silence is the correct failure
    mode, consistent with Gate 2's existing principle that no signal is
    better than a bad signal.

    Only called when Gate 2 fires: crag_triggered=True AND recovery_succeeded=True.
    """

    trace_block = ""
    for entry in trace:
        node = entry.get("node", "unknown")
        trace_block += f"\n[{node.upper()}]\n"
        for k, v in entry.items():
            if k != "node":
                trace_block += f"  {k}: {v}\n"

    system_prompt = """You are an execution policy optimizer for a multi-agent NSE research system.

You receive the full execution trace of a failed-and-recovered research run.
A run reaches you ONLY when: vector store retrieval failed → judge scored low → 
web search fallback succeeded → response was generated.

Your job: identify ONE specific thing that should change in future runs for this query category.

Focus on:
- Should this query category skip vector store entirely and go straight to web?
- Was the sub-query decomposition wrong — too broad, wrong angle, wrong number?
- Should a different decomposition strategy be used for this category next time?

Do NOT write:
- A summary of what happened ("The system retrieved documents...")
- Generic advice ("Use better queries")
- Multiple lessons — one lesson only

Write:
- One actionable routing or decomposition policy change
- Specific to this query category
- Concrete enough that a planner reading it changes its behaviour

Example of a good lesson:
"For macro_rbi_rates queries, vector store consistently scores below 0.4. 
Route directly to web search. Decompose into: specific policy statement + 
equity market impact."

Example of a bad lesson:
"The retrieval failed because the documents were not relevant to the query."

Respond ONLY with valid JSON:
{
  "lesson": "...",
  "confidence": 0.0,
  "query_category": "...",
  "routing_recommendation": "..."
}"""

    user_message = f"""Query: {query}
Sub-queries used: {sub_queries}
Judge score: {judge_score:.4f}
Recovery succeeded: {recovery_succeeded}

Execution Trace:
{trace_block}

Produce one actionable policy lesson for this query category."""

    # llm = ChatGroq(
    #     api_key=GROQ_API_KEY,
    #     model=REFLECTOR_MODEL,
    #     temperature=0.1
    # )
    llm = get_llm(REFLECTOR_MODEL, temperature=0.1)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])
    except Exception as e:
        print(f"[REFLECTOR] All retries failed: {e}. Skipping lesson write for this run.")
        return None

    parsed["confidence"] = max(0.0, min(1.0, float(parsed["confidence"])))

    valid_routing = {"vector_store_sufficient", "web_search_preferred", "mixed"}
    if parsed.get("routing_recommendation") not in valid_routing:
        parsed["routing_recommendation"] = "mixed"

    try:
        return ReflectorOutput(**parsed)
    except Exception as e:
        print(f"[REFLECTOR] Output validation failed: {e}. Skipping lesson write for this run.")
        return None