from tavily import TavilyClient
import asyncio
from concurrent.futures import ThreadPoolExecutor
from utils.llm_factory import get_llm
# from langchain_groq import ChatGroq
from config import TAVILY_API_KEY, JUDGE_MODEL
import json
import re
import sys
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


_tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Keywords that signal a macro/policy query rather than a ticker-specific one.
# If a sub-query hits none of these, it's treated as ticker-specific and
# keeps the original stock-market anchor.
MACRO_KEYWORDS = [
    "rbi", "reserve bank", "interest rate", "repo rate", "inflation",
    "gdp", "trade deal", "tariff", "policy", "budget", "fiscal",
    "monetary", "regulation", "government", "macro", "sector outlook",
    "nifty", "sensex", "market valuation", "fii", "dii", "fpi",
    "federal reserve", "fed ", "fomc", "rate cut", "rate hike",
    "basis points", "central bank", "fed rate"
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


def _search_single(args):
    sub_query, max_results = args
    search_query = _build_search_query(sub_query)
    category = _classify_subquery(sub_query)
    try:
        response = _tavily.search(
            query=search_query,
            max_results=max_results,
            search_depth="advanced",
            topic="news" if category == "macro" else "general"
        )
        print(f"[WEB SEARCH] [{category}] '{search_query}'")
        return response.get("results", []), sub_query, category
    except Exception as e:
        print(f"[WEB SEARCH] Tavily error on '{sub_query}': {e}")
        return [], sub_query, category


def search_web(sub_queries: list[str], max_results_per_query: int = 5) -> list[dict]:
    all_results = []
    seen_urls = set()

    # Run all Tavily searches in parallel
    with ThreadPoolExecutor(max_workers=len(sub_queries)) as executor:
        args = [(sq, max_results_per_query) for sq in sub_queries]
        futures = list(executor.map(_search_single, args))

    for results, sub_query, category in futures:
        for result in results:
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
    print(f"[DEBUG] Sample titles: {[r['title'] for r in all_results[:5]]}")
    print(f"[WEB SEARCH] Retrieved {len(all_results)} raw results across {len(sub_queries)} sub-queries")
    return all_results
    



def _has_substantive_content(text: str) -> bool:
    """
    Checks for numbers AND financial terms — signals real data, not vague prose.
    """
    has_numbers = bool(re.search(r'\d', text))
    has_financial_terms = any(
        term in text.lower() for term in
        ['%', 'crore', 'lakh', '₹', 'rs.', 'usd', 'price', 'rate', 'target',
         'revenue', 'profit', 'growth', 'basis points', 'bps', 'q1', 'q2',
         'q3', 'q4', 'fy2', 'fy26', 'fy25', 'gdp', 'inflation', 'fed',
         'sector', 'index', 'nifty', 'sensex']
    )
    return has_numbers and has_financial_terms


def _strip_inapplicable_sections(refined: str) -> str:
    """
    Removes individual sections flagged as NO_USEFUL_CONTENT rather than
    rejecting the entire refinement. A macro query legitimately has no
    Company Overview or Key Financials — that's expected, not a failure.
    Only the genuinely empty sections are stripped; real content in other
    sections is preserved.
    """
    import re as re_module
    # Remove any section header immediately followed by the NO_USEFUL_CONTENT flag
    cleaned = re_module.sub(
        r'\*\*[^*]+\*\*\s*\nNO_USEFUL_CONTENT\n*',
        '',
        refined
    )
    return cleaned.strip()


def knowledge_refine(
    query: str,
    sub_queries: list[str],
    raw_results: list[dict],
    focus_items: list[str] = None
) -> tuple[str, bool]:
    """
    Strip noise from raw Tavily results and produce clean, structured context.
    Template adapts based on whether the query is company-specific or
    macro/sector-level — this prevents forcing irrelevant sections that
    then trigger false-positive rejection.
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
- If the query is about a SPECIFIC COMPANY, structure as:
  Company Overview | Key Financials | Analyst View | Recent Developments
- If the query is about a SECTOR, MACRO TREND, or MULTIPLE ENTITIES with no
  single company focus, structure as:
  Macro/Sector Context | Key Data Points | Market Reaction | Analyst Commentary
- Only include sections that are relevant to the query type. Do NOT write
  placeholder sections for a category that doesn't apply — simply omit them.
- If a source contains nothing financially relevant, skip it entirely
- Be concise — the output feeds a research generator, not a human reader
- Prioritize sources with concrete figures over sources with only narrative/opinion

If NONE of the sources contain any useful financial or economic information at all,
respond with exactly: NO_USEFUL_CONTENT
(Only use this if the ENTIRE result set is irrelevant — not for individual
sections that don't apply to this query type.)"""

    user_message = f"""Original Query: {query}
Sub-queries searched: {sub_queries}

Raw Web Results:
{raw_block}

Extract and structure the financially relevant information. Prioritize concrete figures.
Choose the appropriate template (company-specific or macro/sector) based on the query."""

    llm = get_llm(JUDGE_MODEL, temperature=0.0)

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    refined = response.content.strip()

    # Only reject outright if the ENTIRE response is the flag, not if it
    # merely appears somewhere inside an otherwise-useful structured response.
    if refined.strip() == "NO_USEFUL_CONTENT" or len(refined) < 100:
        print("[KNOWLEDGE REFINE] Failed — entire response flagged as no useful content or too short")
        return refined, False

    # Strip any individually-flagged inapplicable sections, keep the rest
    refined = _strip_inapplicable_sections(refined)

    if len(refined) < 100:
        print("[KNOWLEDGE REFINE] Failed — after stripping inapplicable sections, nothing substantive remains")
        return refined, False

    if not _has_substantive_content(refined):
        print("[KNOWLEDGE REFINE] Failed — passed length check but lacks "
              "substantive numbers/financial terms")
        return refined, False

    print(f"[KNOWLEDGE REFINE] Pre-filter passed — {len(refined)} chars, "
          f"substantive content confirmed.")
    return refined, True