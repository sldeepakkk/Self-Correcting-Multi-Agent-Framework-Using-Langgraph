from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import (
    planner_node, premise_check_node, retriever_node, generator_node,
    thesis_critic_node, evidence_search_node, revise_node,
    reasoning_reflector_node
)
from graph.edges import route_after_thesis_critique


def build_graph():
    graph = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("planner", planner_node)
    graph.add_node("premise_check", premise_check_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("generator", generator_node)
    graph.add_node("thesis_critic", thesis_critic_node)
    graph.add_node("evidence_search", evidence_search_node)   # critic-directed fetch
    graph.add_node("revise", revise_node)                     # critic-directed rewrite
    graph.add_node("reasoning_reflector", reasoning_reflector_node)

    # ── Linear pipeline ───────────────────────────────────────────────────────
    graph.set_entry_point("planner")
    graph.add_edge("planner", "premise_check")
    graph.add_edge("premise_check", "retriever")
    graph.add_edge("retriever", "generator")
    graph.add_edge("generator", "thesis_critic")

    # ── Critic loop — now a real LangGraph conditional branch ─────────────────
    # Each iteration of thesis_critic routes to one of three destinations:
    #   "evidence_search" → web-fetch the missing fact, then re-evaluate
    #   "revise"          → rewrite the response, then re-evaluate
    #   "reasoning_check" → exit the loop, write a lesson if one was earned
    graph.add_conditional_edges(
        "thesis_critic",
        route_after_thesis_critique,
        {
            "evidence_search": "evidence_search",
            "revise": "revise",
            "reasoning_check": "reasoning_reflector"
        }
    )

    # evidence_search and revise both loop back for another critic evaluation
    graph.add_edge("evidence_search", "thesis_critic")
    graph.add_edge("revise", "thesis_critic")

    # Final node — writes a lesson if a genuine defect was found and resolved
    graph.add_edge("reasoning_reflector", END)

    return graph.compile()


research_graph = build_graph()