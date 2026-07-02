from tavily import TavilyClient
from utils.llm_factory import get_llm
# from langchain_groq import ChatGroq
from config import TAVILY_API_KEY, GROQ_API_KEY, JUDGE_MODEL
import json
import re
from datetime import datetime


_tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Keywords that signal a macro/policy query rather than a ticker-specific one.
# If a sub-query hits none of these, it's treated as ticker-specific and
# keeps the original stock-market anchor.
MACRO_KEYWORDS = [
    "rbi", "reserve bank", "interest rate", "repo rate", "inflation",
    "gdp", "trade deal", "tariff", "policy", "budget", "fiscal",
    "monetary", "regulation", "government", "macro", "sector outlook",
    "nifty", "sensex", "market valuation", "fii", "dii", "fpi"
]


def _classify_subquery(sub_query: str) -> str:
    """
    Lightweight keyword classifier — no LLM call, instant.
    Returns "macro" or "ticker" based on presence of macro/policy terms.
    Macro keywords take priority since over-anchoring macro queries to
    "stock" terms was the original problem this fix addresses.
    """
    lowered = sub_query.lower()
    if any(kw in lowered for kw in MACRO_KEYWORDS):
        return "macro"
    return "ticker"


def _build_search_query(sub_query: str) -> str:
    """
    Builds the actual Tavily query string based on classification.

    Ticker queries: keep the "NSE India stock" anchor — correctly biases
    toward Indian equity-market sources for company-specific asks.

    Macro queries: drop the stock anchor, add a recency anchor instead.
    "NSE India stock" was diluting policy/macro searches toward
    market-commentary sites instead of primary policy sources.
    """
    category = _classify_subquery(sub_query)
    current_year = datetime.now().year

    if category == "macro":
        return f"{sub_query} India {current_year} latest"
    else:
        return f"{sub_query} NSE India stock"


def search_web(sub_queries: list[str], max_results_per_query: int = 5) -> list[dict]:
    """
    Run Tavily search on each sub-query.
    Query construction adapts per sub-query — macro queries get a
    recency anchor + news topic, ticker queries keep the stock-market
    anchor + general topic.
    """
    all_results = []
    seen_urls = set()

    for sub_query in sub_queries:
        search_query = _build_search_query(sub_query)
        category = _classify_subquery(sub_query)

        try:
            response = _tavily.search(
                query=search_query,
                max_results=max_results_per_query,
                search_depth="advanced",
                topic="news" if category == "macro" else "general"
            )
            print(f"[WEB SEARCH] [{category}] '{search_query}'")

            for result in response.get("results", []):
                url = result.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                        "sub_query": sub_query,
                        "category": category
                    })
        except Exception as e:
            print(f"[WEB SEARCH] Tavily error on '{sub_query}': {e}")

    print(f"[WEB SEARCH] Retrieved {len(all_results)} raw results across {len(sub_queries)} sub-queries")
    return all_results


def _has_substantive_content(text: str) -> bool:
    """
    Checks for numbers AND financial terms — signals real data, not vague prose.
    A passing refinement must contain at least one digit and one financial marker.
    Catches "technically not empty but useless" refined content.
    """
    has_numbers = bool(re.search(r'\d', text))
    has_financial_terms = any(
        term in text.lower() for term in
        ['%', 'crore', 'lakh', '₹', 'rs.', 'usd', 'price', 'rate', 'target',
         'revenue', 'profit', 'growth', 'basis points', 'bps', 'q1', 'q2',
         'q3', 'q4', 'fy2', 'fy26', 'fy25']
    )
    return has_numbers and has_financial_terms


def knowledge_refine(
    query: str,
    sub_queries: list[str],
    raw_results: list[dict],
    focus_items: list[str] = None
) -> tuple[str, bool]:
    """
    Strip noise from raw Tavily results and produce clean, structured context.

    focus_items (optional): specific gaps identified by a previous judge pass
    (e.g. ["concrete % impact on bank stock prices"]). When provided, the
    refiner is instructed to prioritize content addressing these specific
    gaps over general topic coverage. Used by the CRAG retry path.
    """

    if not raw_results:
        return "", False

    raw_block = ""
    for i, r in enumerate(raw_results[:8]):
        raw_block += f"\n[Source {i+1}: {r['title']}]\n"
        raw_block += f"URL: {r['url']}\n"
        raw_block += f"{r['content'][:600]}\n"

    focus_block = ""
    if focus_items:
        formatted = "\n".join(f"- {item}" for item in focus_items)
        focus_block = f"""
PRIORITY — A previous attempt was missing this specific information. 
Actively look for and prioritize anything in the sources below that addresses:
{formatted}
"""

    system_prompt = f"""You are a financial research context refiner.

You receive raw web search results for an NSE stock research query.
Your job: extract only financially relevant information and structure it cleanly.
{focus_block}
Rules:
- Remove all navigation text, ads, cookie notices, unrelated content
- Keep: financial figures, analyst opinions, revenue data, price targets, macro context
- ALWAYS include specific numbers, dates, percentages where present in the sources
- Structure output as: Company Overview | Key Financials | Analyst View | Recent Developments
- If a source contains nothing financially relevant, skip it entirely
- Be concise — the output feeds a research generator, not a human reader
- Prioritize sources with concrete figures over sources with only narrative/opinion

If the results contain no useful financial information, respond with exactly: NO_USEFUL_CONTENT"""

    user_message = f"""Original Query: {query}
Sub-queries searched: {sub_queries}

Raw Web Results:
{raw_block}

Extract and structure the financially relevant information. Prioritize concrete figures."""

    # llm = ChatGroq(
    #     api_key=GROQ_API_KEY,
    #     model=JUDGE_MODEL,
    #     temperature=0.0
    # )
    llm = get_llm(JUDGE_MODEL, temperature=0.0)

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    refined = response.content.strip()

    if "NO_USEFUL_CONTENT" in refined or len(refined) < 100:
        print("[KNOWLEDGE REFINE] Failed — flagged as no useful content or too short")
        return refined, False

    if not _has_substantive_content(refined):
        print("[KNOWLEDGE REFINE] Failed — passed length check but lacks "
              "substantive numbers/financial terms")
        return refined, False

    print(f"[KNOWLEDGE REFINE] Pre-filter passed — {len(refined)} chars, "
          f"substantive content confirmed.")
    return refined, True