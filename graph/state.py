from typing import TypedDict, Annotated, Optional
import operator


class AgentState(TypedDict):
    """
    The single object passed between every node in the LangGraph graph.
    Every node reads from this, returns a dict of only the fields it changed.
    LangGraph merges the returned dict back into the full state.

    trace is the only append-only field — Annotated with operator.add
    tells LangGraph to append to the list rather than replace it.
    Every node that wants to log something appends one dict entry to trace.
    The reflector reads the full trace at the end of a slow path run.
    """

    # --- Input ---
    query: str                          # the raw incoming query

    # --- Planner output ---
    sub_queries: list[str]              # 2-3 decomposed retrieval targets

    # --- Retrieval ---
    retrieved_docs: list[dict]          # raw docs from FAISS vector store
                                        # each: {"content": str, "source": str, "score": float}

    # --- Gate 1 ---
    gate1_passed: bool                  # True = skip judge, go to generator

    # --- Judge ---
    judge_score: float                  # 0.0 to 1.0
    judge_reasoning: str                # structured reasoning from judge LLM

    # --- CRAG ---
    crag_triggered: bool                # True = vector retrieval was discarded
    web_search_results: list[dict]      # results from Tavily
    recovery_succeeded: bool            # True = web search gave usable context

    # --- Generator ---
    final_context: str                  # verified context passed to generator
    response: str                       # the final synthesized research report

    # --- Execution tracking ---
    path_taken: str                     # "fast" | "medium" | "slow"
    trace: Annotated[list[dict], operator.add]  # append-only execution log
                                                # every node appends one entry
                                                # {"node": str, "detail": str}

    # --- Memory ---
    episodic_lessons: list[str]         # active lessons loaded from SQLite at run start
    cache_hit: bool                     # True = served from semantic cache

    # --- CRAG retry ---
    crag_retry_count: int                # tracks how many retry attempts made (max 1)
    crag_missing_info: list[str]         # missing_information from failed post_crag_judge,
                                          # used to reformulate the retry search


    is_compound_query: bool           # set by planner_node from PlannerOutput.is_compound
                                  # read by post_crag_judge_node to choose rubric

    judge_aspect_scores: dict         # structured aspect breakdown from web judge
                                  # keys: topic_a, topic_b, factual_density,
                                  #       synthesis_ready, retry_focus
                                  # read by crag_retry_node for targeted search
    thesis_revision_count: int
    thesis_critique: dict
    prev_thesis_critique: dict
    critic_search_used: bool
    premise_correction: str

    initial_reasoning_state: dict