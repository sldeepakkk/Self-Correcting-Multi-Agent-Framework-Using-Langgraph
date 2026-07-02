import sys, os
sys.path.append(os.path.dirname(__file__))

from graph.builder import research_graph
from graph.state import AgentState


def make_state(query: str, lessons: list[str] = []) -> AgentState:
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


print("\n" + "="*60)
print("TEST 1 — Query with strong vector store coverage")
print("Expected: Gate 1 PASS → assemble_context → generator → END")
print("="*60)

state1 = make_state("What are the fundamentals and analyst view for Infosys?")
result1 = research_graph.invoke(state1)
print(f"\nPath taken: {result1['path_taken']}")
print(f"CRAG triggered: {result1['crag_triggered']}")
print(f"Trace nodes: {[t['node'] for t in result1['trace']]}")

print("\n" + "="*60)
print("TEST 2 — Query with weak vector store coverage")
print("Expected: Gate 1 or Judge FAIL → CRAG → generator → reflector")
print("="*60)

state2 = make_state(
    "What did the RBI governor say about interest rates this week "
    "and how does it affect Nifty 50 valuations?"
)
result2 = research_graph.invoke(state2)
print(f"\nPath taken: {result2['path_taken']}")
print(f"CRAG triggered: {result2['crag_triggered']}")
print(f"Recovery succeeded: {result2['recovery_succeeded']}")
print(f"Judge score: {result2['judge_score']:.4f}")
print(f"Trace nodes: {[t['node'] for t in result2['trace']]}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Test 1 response snippet: {result1['response'][:120]}")
print(f"Test 2 response snippet: {result2['response'][:120]}")