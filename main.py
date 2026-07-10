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
5. Add query + response to semantic cache
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

from cache.semantic_cache import SemanticCache
from memory.episodic import load_lessons
from graph.builder import research_graph
from graph.state import AgentState

# ── Constants ─────────────────────────────────────────────────────────────────

RUN_LOG_PATH = "run_logs/runs.jsonl"

# ── Module-level singletons ───────────────────────────────────────────────────
# Loaded once at import. Not rebuilt per query.

_cache = SemanticCache()


# ── Core ──────────────────────────────────────────────────────────────────────

def run_query(query: str, verbose: bool = True) -> dict:
    """
    Main entry point. Accepts a raw NSE research query.
    Returns a result dict with response, path_taken, latency_ms, and full state.

    Fast path (cache hit):
        latency ~50-150ms, zero LLM cost, zero graph invocation

    Medium path (clean retrieval):
        single LLM call chain, vector store hit, no CRAG

    Slow path (CRAG triggered, recovery succeeded):
        full pipeline, web search, reflection, episodic memory write

    Slow failed path (CRAG triggered, recovery failed):
        honest insufficient-data response returned
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
            "judge_score": 0.0,
            "crag_triggered": False,
            "recovery_succeeded": False,
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
        "retrieved_docs": [],
        "gate1_passed": False,
        "judge_score": 0.0,
        "judge_reasoning": "",
        "crag_triggered": False,
        "is_compound_query": False,     
        "judge_aspect_scores": {},      
        "crag_retry_count": 0,
        "crag_missing_info": [],
        "web_search_results": [],
        "recovery_succeeded": False,
        "final_context": "",
        "response": "",
        "path_taken": "",
        "trace": [],
        "episodic_lessons": lessons,
        "thesis_revision_count": 0,
        "thesis_critique": {},
        "critic_search_used": False,
        "premise_correction": "",
        "initial_reasoning_state": {},
        "cache_hit": False
    }

    # ── Step 4: Invoke graph ──────────────────────────────────────────────────
    if verbose:
        print(f"[MAIN] Cache miss — invoking graph...")

    final_state = research_graph.invoke(state)

    latency_ms = int((time.time() - start_time) * 1000)

    # ── Step 5: Populate cache ────────────────────────────────────────────────
    # Only cache successful responses — not slow_failed path
    if final_state["path_taken"] != "slow_failed":
        _cache.add(
            query=query,
            response=final_state["response"],
            path_taken=final_state["path_taken"]
        )
    else:
        if verbose:
            print(f"[MAIN] Skipping cache write — slow_failed path, "
                  f"response unreliable")

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
        "judge_score": final_state.get("judge_score", 0.0),
        "crag_triggered": final_state.get("crag_triggered", False),
        "recovery_succeeded": final_state.get("recovery_succeeded", False),
        "latency_ms": latency_ms,
        "trace": trace_nodes,
        "lessons_applied": len(lessons)
    }

    _log_run(result, final_context=final_state.get("final_context", ""))

    if verbose:
        print(f"\n[MAIN] Done — path={result['path_taken']}, "
              f"latency={latency_ms}ms")
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
    Day 6 benchmark script reads this file.
    """
    os.makedirs(os.path.dirname(RUN_LOG_PATH), exist_ok=True)

    log_entry = {
        "run_id": result["run_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": result["query"],
        "path_taken": result["path_taken"],
        "cache_hit": result["cache_hit"],
        "judge_score": result["judge_score"],
        "crag_triggered": result["crag_triggered"],
        "recovery_succeeded": result["recovery_succeeded"],
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
    print(f"\n{'─'*60}")
    print(f"Run ID:      {result['run_id']}")
    print(f"Path:        {result['path_taken']}")
    print(f"Cache hit:   {result['cache_hit']}")
    print(f"Latency:     {result['latency_ms']}ms")
    print(f"CRAG:        {result['crag_triggered']}")
    print(f"Judge score: {result['judge_score']:.4f}")
    print(f"Lessons:     {result['lessons_applied']}")
    print(f"Trace:       {result['trace']}")
    print(f"{'─'*60}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your NSE research query\"")
        print("Example: python main.py \"What is the outlook for TCS given current IT sector macro?\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = run_query(query)
    _print_summary(result)