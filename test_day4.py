import sys, os
sys.path.append(os.path.dirname(__file__))

from graph.builder import research_graph
from graph.state import AgentState
from memory.episodic import load_lessons, get_lesson_count


def make_state(query: str) -> AgentState:
    # load real lessons from SQLite each time
    lessons = load_lessons()
    return {
        "query": query,
        "sub_queries": [],
        "retrieved_docs": [],
        "gate1_passed": False,
        "judge_score": 0.0,
        "judge_reasoning": "",
        "crag_triggered": False,
        "web_search_results": [],
        "recovery_succeeded": False,
        "final_context": "",
        "response": "",
        "path_taken": "",
        "trace": [],
        "episodic_lessons": lessons,
        "cache_hit": False
    }


# ── Test 1: Medium path — vector store coverage ───────────────────────────────
print("\n" + "="*60)
print("TEST 1 — Infosys fundamentals (vector store should cover)")
print("Expected: medium path, no reflection")
print("="*60)

result1 = research_graph.invoke(
    make_state("What are the fundamentals and analyst view for Infosys?")
)
print(f"\nPath: {result1['path_taken']}")
print(f"CRAG: {result1['crag_triggered']}")
print(f"Trace nodes: {[t['node'] for t in result1['trace']]}")
print(f"\n--- RESPONSE ---\n{result1['response'][:800]}\n")


# ── Test 2: Slow path — CRAG triggered ────────────────────────────────────────
print("\n" + "="*60)
print("TEST 2 — RBI macro query (vector store won't cover this)")
print("Expected: slow path, CRAG triggered, reflector fires if recovery succeeds")
print("="*60)

result2 = research_graph.invoke(
    make_state(
        "What are the latest RBI rate decisions and "
        "how are they impacting banking sector stocks on NSE?"
    )
)
print(f"\nPath: {result2['path_taken']}")
print(f"CRAG: {result2['crag_triggered']}")
print(f"Recovery: {result2['recovery_succeeded']}")
print(f"Judge score: {result2['judge_score']:.4f}")
print(f"Trace nodes: {[t['node'] for t in result2['trace']]}")
print(f"\n--- RESPONSE ---\n{result2['response'][:800]}\n")


# ── Memory state after both runs ──────────────────────────────────────────────
print("\n" + "="*60)
print("EPISODIC MEMORY STATE")
print("="*60)

counts = get_lesson_count()
print(f"Total lessons: {counts['total']}")
print(f"Active lessons: {counts['active']}")
print(f"Quarantined: {counts['quarantined']}")

active = load_lessons()
if active:
    print(f"\nActive lessons loaded for next run:")
    for i, l in enumerate(active):
        print(f"  {i+1}. {l}")
else:
    print("\nNo active lessons yet")