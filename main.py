"""
NSE Research Agent — Main Entry Point

Single function: run_query(query) → dict

Execution order:
1. Load active episodic lessons from SQLite
2. Check semantic cache (cosine similarity >= 0.92)
   → Hit:  return immediately, log fast path, done
   → Miss: continue
3. Build AgentState with lessons as priors
4. Invoke LangGraph graph
5. Add query + response to semantic cache (skipped if evidence_confidence == "low")
6. Log run to run_logs/runs.jsonl
7. Return result dict

Usage:
    python main.py "What are the fundamentals for Infosys?"

    Or import and call:
    from main import run_query
    result = run_query("What is the outlook for TCS?")
"""

import sys
import os
import time
import json
import uuid
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from cache.semantic_cache import SemanticCache
from memory.episodic import load_lessons
from graph.builder import research_graph
from graph.state import AgentState

# ── Constants ─────────────────────────────────────────────────────────────────

RUN_LOG_PATH = "run_logs/runs.jsonl"

# ── Module-level singletons ───────────────────────────────────────────────────

_cache = SemanticCache()


# ── Core ──────────────────────────────────────────────────────────────────────

def run_query(query: str, verbose: bool = True) -> dict:
    """
    Main entry point. Accepts a raw NSE research query.
    Returns a result dict with response, path_taken, latency_ms, evidence_confidence.

    Fast path (cache hit): served instantly from semantic cache.
    generated path: normal reasoning-critic loop completed cleanly.
    low_confidence path: generator produced an answer but evidence
        confidence was low — explicit inference labeling applies,
        response is not cached.
    """

    run_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    if verbose:
        print(f"\n{'='*60}")
        print(f"[RUN {run_id}] Query: {query[:80]}...")
        print(f"{'='*60}")

    # ── Step 1: Load episodic lessons ─────────────────────────────────────────
    lessons = load_lessons()
    if verbose and lessons:
        print(f"[MAIN] Loaded {len(lessons)} active episodic lessons")

    # ── Step 2: Semantic cache check ──────────────────────────────────────────
    cached = _cache.get(query)

    if cached is not None:
        latency_ms = int((time.time() - start_time) * 1000)

        if verbose:
            print(f"[MAIN] FAST PATH — cache hit in {latency_ms}ms")
            print(f"\n--- CACHED RESPONSE ---\n{cached['response'][:400]}...\n")

        result = {
            "run_id": run_id,
            "query": query,
            "response": cached["response"],
            "path_taken": "fast",
            "cache_hit": True,
            "evidence_confidence": "cached",
            "latency_ms": latency_ms,
            "trace": [],
            "lessons_applied": len(lessons)
        }

        _log_run(result, final_context="")
        return result

    # ── Step 3: Build AgentState ──────────────────────────────────────────────
    state: AgentState = {
        "query": query,
        "sub_queries": [],
        "is_compound_query": False,
        "premise_correction": "",
        "final_context": "",
        "evidence_confidence": "medium",
        "response": "",
        "path_taken": "",
        "trace": [],
        "episodic_lessons": lessons,
        "cache_hit": False,
        "thesis_critique": {},
        "prev_thesis_critique": {},
        "initial_reasoning_state": {},
        "thesis_revision_count": 0,
        "search_count": 0
    }

    # ── Step 4: Invoke graph ──────────────────────────────────────────────────
    if verbose:
        print(f"[MAIN] Cache miss — invoking graph...")

    final_state = research_graph.invoke(state)

    latency_ms = int((time.time() - start_time) * 1000)

    # ── Step 5: Populate cache ────────────────────────────────────────────────
    # Don't cache low-confidence, inference-heavy answers — they're query-
    # specific hedged reasoning, not a stable fact worth reusing verbatim.
    evidence_confidence = final_state.get("evidence_confidence", "medium")
    if evidence_confidence != "low":
        _cache.add(
            query=query,
            response=final_state["response"],
            path_taken=final_state["path_taken"]
        )
    else:
        print(f"[MAIN] Skipping cache write — low evidence confidence, "
              f"avoiding caching an inference-heavy answer")

    # ── Step 6: Build result ──────────────────────────────────────────────────
    trace_nodes = [
        t if isinstance(t, dict) else {"node": str(t), "status": "success"}
        for t in final_state.get("trace", [])
    ]

    result = {
        "run_id": run_id,
        "query": query,
        "response": final_state["response"],
        "path_taken": final_state["path_taken"],
        "cache_hit": False,
        "evidence_confidence": evidence_confidence,
        "latency_ms": latency_ms,
        "trace": trace_nodes,
        "lessons_applied": len(lessons)
    }

    _log_run(result, final_context=final_state.get("final_context", ""))

    if verbose:
        print(f"\n[MAIN] Done — path={result['path_taken']}, "
              f"confidence={evidence_confidence}, latency={latency_ms}ms")
        print(f"\n{'='*60}")
        print("RESPONSE")
        print(f"{'='*60}")
        print(final_state["response"])

    return result


# ── Logging ───────────────────────────────────────────────────────────────────

def _log_run(result: dict, final_context: str = "") -> None:
    """
    Appends one JSON line to run_logs/runs.jsonl.
    Each line is one complete run record.
    """
    os.makedirs(os.path.dirname(RUN_LOG_PATH), exist_ok=True)

    log_entry = {
        "run_id": result["run_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": result["query"],
        "path_taken": result["path_taken"],
        "cache_hit": result["cache_hit"],
        "evidence_confidence": result.get("evidence_confidence", "medium"),
        "latency_ms": result["latency_ms"],
        "response_length": len(result.get("response", "")),
        "trace_nodes": result.get("trace", []),
        "lessons_applied": result.get("lessons_applied", 0),
        "context_preview": final_context[:2000],
        "context_length": len(final_context)
    }

    with open(RUN_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_summary(result: dict) -> None:
    print(f"\n{'-'*60}")
    print(f"Run ID:      {result['run_id']}")
    print(f"Path:        {result['path_taken']}")
    print(f"Cache hit:   {result['cache_hit']}")
    print(f"Confidence:  {result.get('evidence_confidence', 'n/a')}")
    print(f"Latency:     {result['latency_ms']}ms")
    print(f"Lessons:     {result['lessons_applied']}")
    print(f"{'-'*60}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your NSE research query\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = run_query(query)
    _print_summary(result)