from retrieval.web_search import search_web, knowledge_refine
from config import JUDGE_RELEVANCE_THRESHOLD


def run_crag_fallback(
    query: str,
    sub_queries: list[str],
    judge_score: float
) -> tuple[str, bool]:
    """
    Initial CRAG fallback.
    Triggered when judge score < JUDGE_RELEVANCE_THRESHOLD on vector retrieval.

    Cleans conversational question words from sub-queries before passing
    to web_search.py so the internal classifier works cleanly.
    """
    print(f"[CRAG] Fallback triggered — judge score {judge_score:.4f} < {JUDGE_RELEVANCE_THRESHOLD}")
    print(f"[CRAG] Discarding vector store results. Cleaning sub-queries for web_search engine...")

    cleaned_sub_queries = []
    for sq in sub_queries:
        clean_sq = (
            sq.replace("What are", "")
              .replace("What is", "")
              .replace("How do", "")
              .replace("How are", "")
              .replace("?", "")
              .strip()
        )
        if clean_sq:
            cleaned_sub_queries.append(clean_sq)

    if not cleaned_sub_queries:
        cleaned_sub_queries = sub_queries

    raw_results = search_web(cleaned_sub_queries, max_results_per_query=5)

    if not raw_results:
        print("[CRAG] Web search returned no results — recovery failed")
        return "", False

    refined_context, success = knowledge_refine(query, cleaned_sub_queries, raw_results)

    if success:
        print(f"[CRAG] Pre-filter passed — clean context ready for post-CRAG judge")
    else:
        print(f"[CRAG] Pre-filter failed — web results had no useful content")

    return refined_context, success


def run_crag_retry(
    query: str,
    missing_information: list[str]
) -> tuple[str, bool]:
    """
    Corrective retry — uses isolated atomic search queries based on judge feedback.

    Takes retry_focus items directly as search queries — they were generated
    by the aspect judge specifically as targeted search strings.
    No prefix injection — web_search.py classifier handles routing correctly.
    """
    if not missing_information:
        print("[CRAG RETRY] No missing_information to retry with — skipping retry")
        return "", False

    print(f"[CRAG RETRY] Reformulating search using judge feedback: {missing_information}")

    retry_queries = []
    for item in missing_information[:3]:
        clean_item = (
            item.replace("topic_a:", "")
                .replace("topic_b:", "")
                .replace("Gaps:", "")
                .replace("-", "")
                .strip()
        )
        if clean_item:
            retry_queries.append(clean_item)

    if not retry_queries:
        retry_queries = [query]    # last resort — use original query

    print(f"[CRAG RETRY] Dispatching atomic topics to web_search: {retry_queries}")
    raw_results = search_web(retry_queries, max_results_per_query=5)

    if not raw_results:
        print("[CRAG RETRY] Web search returned no results — retry failed")
        return "", False

    refined_context, success = knowledge_refine(
        query=query,
        sub_queries=retry_queries,
        raw_results=raw_results,
        focus_items=missing_information
    )

    if success:
        print(f"[CRAG RETRY] Retry pre-filter passed — re-judging")
    else:
        print(f"[CRAG RETRY] Retry pre-filter failed")

    return refined_context, success