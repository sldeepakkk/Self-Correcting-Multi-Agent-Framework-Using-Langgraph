import sys, os
sys.path.append(os.path.dirname(__file__))

from graph.state import AgentState
from graph.nodes import planner_node, retriever_node

# build a minimal state
state: AgentState = {
    "query": "What is the revenue growth trend for Infosys and what do analysts recommend?",
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
    "episodic_lessons": [
        "For large-cap IT earnings queries, 2 sub-queries suffice: revenue trend + analyst consensus"
    ],
    "cache_hit": False
}

# Run planner node
state.update(planner_node(state))
print(f"\nSub-queries: {state['sub_queries']}")

# Run retriever node
state.update(retriever_node(state))
print(f"\nRetrieved docs: {len(state['retrieved_docs'])}")
print(f"Trace so far: {[t['node'] for t in state['trace']]}")