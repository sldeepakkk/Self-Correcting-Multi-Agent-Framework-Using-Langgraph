# from langchain_groq import ChatGroq
from utils.llm_factory import get_llm
from pydantic import BaseModel, Field
# from config import GROQ_API_KEY, PLANNER_MODEL
from config import PLANNER_MODEL


class PlannerOutput(BaseModel):
    sub_queries: list[str] = Field(
        description="2 to 3 targeted retrieval sub-queries decomposed from the original query",
        min_length=2,
        max_length=3
    )
    reasoning: str = Field(
        description="One sentence explaining the decomposition strategy"
    )
    is_compound: bool = Field(
        description="True if the query connects two distinct topics (e.g. a macro/policy "
                    "event AND a specific stock/sector outcome) that need to be bridged "
                    "rather than researched separately.",
        default=False
    )


def run_planner(query: str, episodic_lessons: list[str]) -> PlannerOutput:
    """
    Decomposes the incoming query into 2-3 targeted sub-queries.
    Loads episodic lessons as priors — this is where policy improvement
    from previous runs manifests in the planner's decomposition strategy.

    Detects compound queries — those connecting two distinct topics
    (e.g. "RBI rate decision" + "banking stock impact"). For these, one
    sub-query must explicitly bridge both topics together, rather than
    decomposing into two single-topic searches that may never connect
    in any single retrieved source.

    Why this matters: web search on "topic A" and "topic B" separately
    often returns content about each topic individually, with no source
    making the connection. A bridging sub-query that names both together
    is more likely to surface analyst commentary that already connects them.
    """

    lessons_block = ""
    if episodic_lessons:
        formatted = "\n".join(f"- {l}" for l in episodic_lessons)
        lessons_block = f"""
LESSONS FROM PREVIOUS RUNS (apply these to your decomposition):
{formatted}
"""

    system_prompt = f"""You are a financial research query planner specializing in NSE (National Stock Exchange of India) stocks.

Your job: decompose a complex research query into 2-3 precise sub-queries that together cover the full answer.

STEP 1 — Detect if this is a COMPOUND query.
A compound query connects two distinct topics where the answer depends on
the RELATIONSHIP between them, not just facts about each separately. Examples:
- "How does RBI rate decision X affect banking stocks?" (policy → stock impact)
- "How is the trade deal affecting IT sector stocks?" (policy → sector impact)
- "How are oil prices impacting Reliance stock?" (commodity → single stock)

A query is NOT compound if it only asks about one topic:
- "What are RBI's latest rate decisions?" (single topic — policy only)
- "What are Infosys fundamentals?" (single topic — one company)

STEP 2 — Decomposition rules:

IF compound:
- Sub-query 1: research topic A alone (the policy/macro/commodity event)
- Sub-query 2: research topic B alone (the stock/sector)
- Sub-query 3 (REQUIRED, this is the bridge): explicitly combine BOTH topics
  in one search query naming the connection directly. This sub-query should
  read like something an analyst would title an article, not like two
  topics stapled together. Example bridge query:
  "RBI repo rate decision impact on Indian banking sector stock prices analyst view"
  NOT: "RBI rate decisions AND banking stocks" (too literal, won't match real articles)

IF NOT compound (single topic):
- Maximum 3 sub-queries covering different angles of that one topic
- For large-cap IT earnings queries, 2 sub-queries suffice: revenue trend + analyst consensus
- For macro/sector queries, include: sector outlook + key stock exposure

{lessons_block}
Respond ONLY with valid JSON matching this schema exactly:
{{
  "sub_queries": ["query1", "query2", "query3 (bridge query if compound)"],
  "reasoning": "one sentence",
  "is_compound": true
}}
No preamble. No explanation. Just the JSON."""

    from utils.llm_json import invoke_with_retry

    # llm = ChatGroq(api_key=GROQ_API_KEY, model=PLANNER_MODEL, temperature=0.1)
    llm = get_llm(PLANNER_MODEL, temperature=0.1)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Decompose this query: {query}"}
        ])
        return PlannerOutput(**parsed)
    except Exception as e:
        print(f"[PLANNER] All retries failed: {e}. Using safe fallback decomposition.")
        return PlannerOutput(
            sub_queries=[query, f"{query} fundamentals analyst view"],
            reasoning="Fallback — planner JSON parsing failed after retries",
            is_compound=False
        )