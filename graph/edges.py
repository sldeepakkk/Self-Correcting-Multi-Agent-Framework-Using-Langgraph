from graph.state import AgentState
from config import (
    JUDGE_RELEVANCE_THRESHOLD,
    GATE1_MIN_RESPONSE_LENGTH,
    GATE1_UNCERTAINTY_MARKER_LIMIT,
    GATE1_UNCERTAINTY_MARKERS
)


# ── Gate 1 ────────────────────────────────────────────────────────────────────
# Cheap heuristic filter. Runs before the judge.
# Pass → skip judge, go straight to generator (medium path)
# Fail → invoke judge (judge decides between medium and slow path)

def gate1_check(state: AgentState) -> str:
    """
    Three cheap heuristics on retrieved docs.
    Returns "generator" (skip judge) or "judge" (invoke judge).

    Heuristic 1: top retrieval score — below 0.65 is suspicious
    Heuristic 2: doc count — fewer than 2 means thin retrieval
    Heuristic 3: source diversity — all same source = no corroboration
    """
    docs = state.get("retrieved_docs", [])

    if not docs:
        print("[GATE 1] FAIL — no documents retrieved")
        return "judge"

    top_score = docs[0].get("score", 0.0)
    sources = [d.get("source", "") for d in docs]
    unique_sources = len(set(sources))
    doc_count = len(docs)

    failures = []

    if top_score < 0.65:
        failures.append(f"top_score={top_score:.4f} < 0.65")

    if doc_count < 2:
        failures.append(f"doc_count={doc_count} < 2")

    if unique_sources < 2:
        failures.append(f"source_diversity={unique_sources} — all from same source")

    if failures:
        print(f"[GATE 1] FAIL — {' | '.join(failures)} → invoking judge")
        return "judge"

    print(f"[GATE 1] PASS — top_score={top_score:.4f}, docs={doc_count}, sources={unique_sources} → skipping judge")
    return "generator"


# ── After Judge ───────────────────────────────────────────────────────────────

def route_after_judge(state: AgentState) -> str:
    """
    Routes based on judge score.
    Above threshold → generator (medium path — retrieval was adequate)
    Below threshold → crag (slow path — discard and search web)
    """
    score = state.get("judge_score", 0.0)

    if score >= JUDGE_RELEVANCE_THRESHOLD:
        print(f"[ROUTE] Judge score {score:.4f} >= {JUDGE_RELEVANCE_THRESHOLD} → generator")
        return "generator"
    else:
        print(f"[ROUTE] Judge score {score:.4f} < {JUDGE_RELEVANCE_THRESHOLD} → CRAG fallback")
        return "crag"


# ── Gate 2 ────────────────────────────────────────────────────────────────────
# Conditional reflection trigger.
# Only fires if a full failure+recovery cycle occurred.
# Silence (no memory write) is the correct output for clean runs.

# In gate2_check — edges.py
def gate2_check(state: AgentState) -> str:
    crag_triggered = state.get("crag_triggered", False)
    recovery_succeeded = state.get("recovery_succeeded", False)
    judge_score = state.get("judge_score", 0.0)

    # Only write lessons when recovery succeeded AND context quality was meaningful
    if crag_triggered and recovery_succeeded and judge_score >= 0.7:
        return "reflector"

    return "end"


def route_after_crag_judge(state: AgentState) -> str:
    """
    Routes after post_crag_judge evaluates web context.

    recovery_succeeded=True  → generator (answer the query)
    recovery_succeeded=False AND no retry used yet → crag_retry (self-correct)
    recovery_succeeded=False AND retry already used → generator
        (generator_node already handles this gracefully via the
        insufficient-data response — this is the genuine final fallback,
        reached only after the system has actually tried to correct itself)
    """
    recovery_succeeded = state.get("recovery_succeeded", False)
    retry_count = state.get("crag_retry_count", 0)

    if recovery_succeeded:
        print("[ROUTE] Recovery succeeded → generator")
        return "generator"

    if retry_count < 1:
        print(f"[ROUTE] Recovery failed, retry_count={retry_count} → crag_retry")
        return "crag_retry"

    print(f"[ROUTE] Recovery failed after retry — final fallback → generator (insufficient data)")
    return "generator"

# ── Web-First Query Classifier ────────────────────────────────────────────────

# Patterns that signal the answer lives on the web, not in the vector store.
# These queries require current/global data that yfinance and macro seeds don't cover.
WEB_FIRST_PATTERNS = [
    # US/Global macro
    "federal reserve", "fed ", "fomc", "wall street",
    "us macro", "global ai", "us monetary", "rate cut cycle",
    "international market", "s&p 500", "nasdaq", "dow jones",
    # Forward-looking / hypothetical
    "assuming ", "if the fed", "in q4 2026", "next quarter",
    "forecast for", "projected", "expected to",
    # Explicitly current/real-time
    "this week", "today", "latest news", "breaking",
    "just announced", "recently announced"
]


def should_route_web_first(state: AgentState) -> str:
    """
    Lightweight classifier — runs before retriever, costs zero LLM calls.
    If the query matches web-first patterns, skip vector retrieval entirely
    and go straight to CRAG web search.

    This prevents the expensive and predictably-failing path:
    vector retrieval → judge fail → CRAG
    For queries the vector store structurally cannot answer.

    Returns "web_first" or "retrieve" for the planner conditional edge.
    """
    query = state.get("query", "").lower()

    matched = [p for p in WEB_FIRST_PATTERNS if p in query]

    if matched:
        print(f"[ROUTE] Web-first patterns matched: {matched} → skipping vector store")
        return "web_first"

    print(f"[ROUTE] No web-first patterns → standard retrieval")
    return "retrieve"