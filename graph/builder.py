from langgraph.graph import StateGraph, END
from graph.edges import gate1_check, route_after_judge, route_after_crag_judge, gate2_check, route_after_thesis_critique, should_route_web_first, route_after_thesis_critique
from graph.state import AgentState
from graph.nodes import (
    generator_revise_node,
    planner_node,
    retriever_node,
    gate1_node,
    judge_node,
    crag_node,
    crag_retry_node,
    post_crag_judge_node,
    assemble_context_node,
    generator_node,
    thesis_critic_node,
    generator_revise_node,
    critic_search_node,
    premise_check_node,
    reasoning_reflector_node,
    reflector_node
)


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

    graph.set_entry_point("planner")
    graph.add_node("premise_check", premise_check_node)
    graph.add_edge("planner", "premise_check")

    graph.add_conditional_edges(
        "premise_check",
        should_route_web_first,
        {"retrieve": "retriever", "web_first": "crag"}
    )

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

    graph.add_conditional_edges(
        "post_crag_judge", route_after_crag_judge,
        {"generator": "generator", "crag_retry": "crag_retry", "generator_partial": "generator"}
    )

    graph.add_node("critic_search", critic_search_node)
    graph.add_edge("critic_search", "generator_revise")
    graph.add_edge("reflector", END)

    graph.add_edge("assemble_context", "generator")

    graph.add_node("thesis_critic", thesis_critic_node)
    graph.add_node("generator_revise", generator_revise_node)

    graph.add_edge("generator", "thesis_critic")
    graph.add_edge("generator_revise", "thesis_critic")

    graph.add_node("reasoning_reflector", reasoning_reflector_node)

    graph.add_conditional_edges(
        "thesis_critic",
        route_after_thesis_critique,
        {"revise": "generator_revise", "critic_search": "critic_search", "reasoning_check": "reasoning_reflector"}
    )

    graph.add_conditional_edges(
        "reasoning_reflector",
        gate2_check,
        {"reflector": "reflector", "end": END}
    )

    return graph.compile()


# singleton — import this everywhere
research_graph = build_graph()