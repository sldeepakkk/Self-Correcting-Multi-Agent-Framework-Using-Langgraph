from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import (
    planner_node,
    retriever_node,
    gate1_node,
    judge_node,
    crag_node,
    crag_retry_node,
    post_crag_judge_node,
    assemble_context_node,
    generator_node,
    reflector_node
)
from graph.edges import gate1_check, route_after_judge, route_after_crag_judge, gate2_check


def build_graph():
    """
    Assembles the full LangGraph StateGraph.

    Flow:
    planner → retriever → gate1 → [gate1_check]
                                        ↓ pass              ↓ fail
                               assemble_context          judge
                                        ↓           [route_after_judge]
                                    generator        ↓ pass    ↓ fail
                                        ↓       assemble   crag
                               [gate2_check]         ↓        ↓
                                ↓ fire    ↓ skip  generator  generator
                            reflector    END          ↓
                                ↓               [gate2_check]
                               END               ↓ fire  ↓ skip
                                             reflector   END
    """

    graph = StateGraph(AgentState)

    # register nodes
    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("gate1", gate1_node)
    graph.add_node("judge", judge_node)
    graph.add_node("crag", crag_node)
    graph.add_node("crag_retry", crag_retry_node)
    graph.add_node("post_crag_judge", post_crag_judge_node)
    graph.add_node("assemble_context", assemble_context_node)
    graph.add_node("generator", generator_node)
    graph.add_node("reflector", reflector_node)

    # fixed edges — always go here next
    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "gate1")
    graph.add_edge("crag", "post_crag_judge") 
    graph.add_edge("crag_retry", "post_crag_judge")

    # conditional edges — routing decisions
    graph.add_conditional_edges(
        "gate1",
        gate1_check,
        {
            "generator": "assemble_context",    # pass → skip judge
            "judge": "judge"                    # fail → invoke judge
        }
    )

    graph.add_conditional_edges(
        "judge",
        route_after_judge,
        {
            "generator": "assemble_context",    # score >= threshold
            "crag": "crag"                      # score < threshold
        }
    )

    graph.add_edge("assemble_context", "generator")

    graph.add_conditional_edges(
    "post_crag_judge",
    route_after_crag_judge,
    {"generator": "generator", "crag_retry": "crag_retry"}
    )

    graph.add_conditional_edges(
        "generator",
        gate2_check,
        {
            "reflector": "reflector",           # failure+recovery cycle
            "end": END                          # clean run
        }
    )

    graph.add_edge("reflector", END)

    return graph.compile()


# singleton — import this everywhere
research_graph = build_graph()