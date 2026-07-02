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

def gate2_check(state: AgentState) -> str:
    """
    Decides whether to invoke the reflector after a run.

    Reflector fires ONLY when:
    - CRAG was triggered (retrieval failed)
    - AND recovery succeeded (web search found usable content)

    If CRAG was triggered but recovery failed → don't write a lesson,
    there's nothing reliable to learn from.

    If retrieval was clean → don't write anything, no lesson exists.
    """
    crag_triggered = state.get("crag_triggered", False)
    recovery_succeeded = state.get("recovery_succeeded", False)

    if crag_triggered and recovery_succeeded:
        print("[GATE 2] FIRE — CRAG triggered and recovery succeeded → reflector")
        return "reflector"

    if crag_triggered and not recovery_succeeded:
        print("[GATE 2] SKIP — CRAG triggered but recovery failed → nothing to learn")
        return "end"

    print("[GATE 2] SKIP — clean run, no failure cycle occurred → end")
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