from retrieval.web_search import search_web, knowledge_refine
from config import JUDGE_RELEVANCE_THRESHOLD

def run_evidence_search(query: str, search_terms: list[str]) -> tuple[str, bool]:
    """
    Single, ungated web search. No aspect judge scoring the result —
    the reasoning critic downstream decides if it's good enough. This
    replaces CRAG + CRAG retry + the post-CRAG aspect judge entirely.
    """
    raw_results = search_web(search_terms, max_results_per_query=5)
    if not raw_results:
        return "", False
    refined, success = knowledge_refine(query, search_terms, raw_results)
    return refined, success