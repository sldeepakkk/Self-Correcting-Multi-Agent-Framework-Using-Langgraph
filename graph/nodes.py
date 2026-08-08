from graph.state import AgentState
from agents.planner import run_planner
from agents.generator import run_generator, run_generator_revision, compute_evidence_confidence
from agents.critic import run_thesis_critic, run_premise_check
from agents.reasoning_reflector import run_reasoning_reflector, compute_reasoning_confidence
from retrieval.vector_store import VectorStore
from retrieval.crag import run_evidence_search
from retrieval.web_search import _has_substantive_content
from memory.episodic import load_reasoning_lessons, write_reasoning_lesson

# initialise once at import — loaded from disk, not rebuilt each call
_vector_store = VectorStore()


# ── Node 1: Planner ───────────────────────────────────────────────────────────

def planner_node(state: AgentState) -> dict:
    print(f"\n[NODE: PLANNER] Query: {state['query'][:80]}...")

    lessons = state.get("episodic_lessons", [])
    if lessons:
        print(f"[NODE: PLANNER] Loaded {len(lessons)} episodic lessons as priors")

    result = run_planner(query=state["query"], episodic_lessons=lessons)

    print(f"[NODE: PLANNER] Compound query: {result.is_compound}")
    print(f"[NODE: PLANNER] Sub-queries: {result.sub_queries}")
    print(f"[NODE: PLANNER] Reasoning: {result.reasoning}")

    return {
        "sub_queries": result.sub_queries,
        "is_compound_query": result.is_compound,
        "trace": [{
            "node": "planner",
            "sub_queries": result.sub_queries,
            "reasoning": result.reasoning,
            "is_compound": result.is_compound,
            "lessons_applied": len(lessons)
        }]
    }


# ── Node 2: Premise Check ─────────────────────────────────────────────────────

def premise_check_node(state: AgentState) -> dict:
    print(f"\n[NODE: PREMISE CHECK] Screening query for institutional errors...")

    reasoning_lessons = load_reasoning_lessons(limit=5)
    result = run_premise_check(state["query"], reasoning_lessons=reasoning_lessons)

    if result["premise_flag"]:
        print(f"[NODE: PREMISE CHECK] Flagged: {result['premise_correction']}")
    else:
        print(f"[NODE: PREMISE CHECK] No institutional errors detected")

    return {
        "premise_correction": result["premise_correction"],
        "trace": [{
            "node": "premise_check",
            "flagged": result["premise_flag"],
            "correction": result["premise_correction"]
        }]
    }


# ── Node 3: Retriever ─────────────────────────────────────────────────────────

def retriever_node(state: AgentState) -> dict:
    """
    Hybrid retriever: searches internal vector store for company filings and
    domain documents, and augments with real-time web search when local context
    is insufficient or when the query requires recent/live market data.
    """
    sub_queries = state.get("sub_queries", []) or [state["query"]]
    print(f"\n[NODE: RETRIEVER] Searching {len(sub_queries)} sub-queries...")

    docs = _vector_store.search_multi(sub_queries=sub_queries, top_k_per_query=4)
    high_quality_docs = [d for d in docs if d.get("score", 0.0) >= 0.58]

    context_parts = []
    if high_quality_docs:
        local_context = "\n\n".join(
            f"[Source: {d.get('source', 'internal_filing')}]\n{d.get('content', '')}"
            for d in high_quality_docs
        )
        context_parts.append(local_context)
        print(f"[NODE: RETRIEVER] Found {len(high_quality_docs)} high-relevance local docs")
    else:
        print(f"[NODE: RETRIEVER] Local vector store has sparse context for this query")

    # Check if local context is rich and contains substantive financial figures
    top_score = max((d.get("score", 0.0) for d in high_quality_docs), default=0.0)
    has_substantive_local = bool(context_parts) and _has_substantive_content(context_parts[0])

    web_searched = False
    # Augment with live web search if local context is sparse, lacks substantive financial data, or has low match score
    if len(high_quality_docs) < 3 or not has_substantive_local or top_score < 0.70:
        print(f"[NODE: RETRIEVER] Local context insufficient (docs={len(high_quality_docs)}, top_score={top_score:.2f}, substantive={has_substantive_local}). Augmenting with live web search...")
        refined, success = run_evidence_search(state["query"], sub_queries)
        if success and refined:
            context_parts.append(f"## Live Market & Research Context\n{refined}")
            web_searched = True
            print(f"[NODE: RETRIEVER] Web search added {len(refined)} chars of structured evidence")

    combined_context = "\n\n".join(context_parts) if context_parts else "\n\n".join(
        f"[Source: {d.get('source', 'unknown')}]\n{d.get('content', '')}" for d in docs
    )

    print(f"[NODE: RETRIEVER] Total context: {len(combined_context)} chars (web_augmented={web_searched})")

    return {
        "final_context": combined_context,
        "search_count": 1 if web_searched else 0,
        "trace": [{
            "node": "retriever",
            "doc_count": len(high_quality_docs),
            "web_augmented": web_searched,
            "context_length": len(combined_context)
        }]
    }


# ── Node 4: Generator ─────────────────────────────────────────────────────────

def generator_node(state: AgentState) -> dict:
    print(f"\n[NODE: GENERATOR] Synthesizing answer...")
    print(f"  Context length: {len(state.get('final_context', ''))} chars")

    confidence = compute_evidence_confidence(state)
    print(f"[NODE: GENERATOR] Evidence confidence: {confidence}")

    response = run_generator(
        query=state["query"],
        final_context=state.get("final_context", ""),
        sub_queries=state.get("sub_queries", []),
        premise_correction=state.get("premise_correction", ""),
        evidence_confidence=confidence,
        episodic_lessons=state.get("episodic_lessons", [])
    )

    path = "low_confidence" if confidence == "low" else "generated"
    print(f"[NODE: GENERATOR] Done — path={path}, response={len(response)} chars")

    return {
        "response": response,
        "path_taken": path,
        "evidence_confidence": confidence,
        "trace": [{
            "node": "generator",
            "path": path,
            "evidence_confidence": confidence,
            "response_length": len(response)
        }]
    }


# ── Node 5: Thesis Critic ─────────────────────────────────────────────────────

def thesis_critic_node(state: AgentState) -> dict:
    """
    ONE evaluation step of the critic — produces a ThesisCritique and stores it
    in state. Routing after this node (evidence_search / revise / reasoning_check)
    is handled by route_after_thesis_critique in edges.py as a real LangGraph
    conditional edge, so each loop iteration is visible to LangGraph's
    checkpointing and observability rather than hidden inside a Python for-loop.
    """
    print(f"\n[NODE: THESIS CRITIC] Evaluating response (revision={state.get('thesis_revision_count', 0)})...")

    reasoning_lessons = load_reasoning_lessons(limit=5)
    critique = run_thesis_critic(
        query=state["query"],
        response=state.get("response", ""),
        context=state.get("final_context", ""),
        is_compound=state.get("is_compound_query", False),
        evidence_confidence=state.get("evidence_confidence", "medium"),
        reasoning_lessons=reasoning_lessons
    )

    print(f"[NODE: THESIS CRITIC] Sound={critique.thesis_sound}, "
          f"needs_evidence={bool(critique.needs_evidence)}, "
          f"weakest={critique.weakest_dimension}")

    # Snapshot current critique as prev before overwriting, so the convergence
    # check in route_after_thesis_critique can compare adjacent iterations.
    prev_critique = state.get("thesis_critique", {})
    critique_dict = critique.model_dump()

    # Capture initial state only on the very first critic pass so the reasoning
    # reflector can compare before-vs-after across the full revision loop.
    updates: dict = {
        "thesis_critique": critique_dict,
        "prev_thesis_critique": prev_critique,
        "trace": [{
            "node": "thesis_critic",
            "revision_pass": state.get("thesis_revision_count", 0),
            "thesis_sound": critique.thesis_sound,
            "needs_evidence": critique.needs_evidence,
            "weakest_dimension": critique.weakest_dimension
        }]
    }

    if not state.get("initial_reasoning_state"):
        updates["initial_reasoning_state"] = {
            "thesis_sound": critique.thesis_sound,
            "original_response": state.get("response", ""),
            "unsupported_claims": critique.unsupported_claims,
            "overconfidence_flags": critique.overconfidence_flags,
            "premise_issues": critique.premise_issues,
            "revision_count_signal": 0
        }

    return updates


# ── Node 6: Evidence Search (critic-directed) ─────────────────────────────────

def evidence_search_node(state: AgentState) -> dict:
    """
    Fetches one targeted web search based on the critic's needs_evidence field.
    Appends results to final_context so the subsequent revise_node and the next
    thesis_critic pass both see the new evidence. Increments search_count so
    route_after_thesis_critique can enforce the MAX_SEARCHES cap.
    """
    critique = state.get("thesis_critique", {})
    search_query = critique.get("needs_evidence") or state["query"]

    print(f"\n[NODE: EVIDENCE SEARCH] Critic-directed search: '{search_query[:80]}'")

    refined, success = run_evidence_search(state["query"], [search_query])

    new_context = state.get("final_context", "")
    if success and refined:
        new_context = f"{new_context}\n\n## Critic-Requested Evidence\n{refined}"

    print(f"[NODE: EVIDENCE SEARCH] {'Succeeded' if success else 'Failed'} — "
          f"context now {len(new_context)} chars")

    return {
        "final_context": new_context,
        "search_count": state.get("search_count", 0) + 1,
        "trace": [{
            "node": "evidence_search",
            "query": search_query,
            "found": success,
            "context_length": len(new_context)
        }]
    }


# ── Node 7: Revise ────────────────────────────────────────────────────────────

def revise_node(state: AgentState) -> dict:
    """
    Rewrites the current response using the critic's structured feedback.
    Increments thesis_revision_count so route_after_thesis_critique can enforce
    the MAX_REVISIONS cap and the convergence check in has_converged() fires.
    """
    critique = state.get("thesis_critique", {})
    revision_number = state.get("thesis_revision_count", 0) + 1

    print(f"\n[NODE: REVISE] Revision #{revision_number} — "
          f"weakest={critique.get('weakest_dimension', 'n/a')}")

    revised = run_generator_revision(
        query=state["query"],
        original_response=state.get("response", ""),
        critique=critique,
        final_context=state.get("final_context", "")
    )

    print(f"[NODE: REVISE] Done — {len(revised)} chars")

    return {
        "response": revised,
        "thesis_revision_count": revision_number,
        "trace": [{
            "node": "revise",
            "revision_number": revision_number,
            "response_length": len(revised)
        }]
    }

# ── Node 8: Reasoning Reflector ───────────────────────────────────────────────

def reasoning_reflector_node(state: AgentState) -> dict:
    initial = state.get("initial_reasoning_state", {})
    final_critique = state.get("thesis_critique", {})
    revision_count = state.get("thesis_revision_count", 0)

    if not initial:
        return {"trace": [{"node": "reasoning_reflector", "status": "no_initial_critique"}]}

    defect_found = (
        (not initial.get("thesis_sound", True))
        or bool(initial.get("unsupported_claims"))
        or bool(initial.get("overconfidence_flags"))
        or bool(initial.get("missing_requirements"))
        or bool(initial.get("premise_issues"))
    )
    actually_revised = revision_count > 0
    genuinely_resolved = final_critique.get("thesis_sound", False)

    if not (defect_found and actually_revised and genuinely_resolved):
        print(f"[NODE: REASONING REFLECTOR] Gate not met — skipping")
        return {"trace": [{"node": "reasoning_reflector", "status": "gate_not_met"}]}

    print(f"\n[NODE: REASONING REFLECTOR] Defect resolved — distilling lesson...")

    result = run_reasoning_reflector(
        query=state["query"],
        original_response=initial.get("original_response", ""),
        first_critique=initial,
        revised_response=state.get("response", ""),
        final_critique=final_critique
    )

    if result is None:
        return {"trace": [{"node": "reasoning_reflector", "status": "parse_failed"}]}

    confidence = compute_reasoning_confidence(
        initial, final_critique,
        critic_search_used=state.get("search_count", 0) > 0,
        revision_count=revision_count
    )

    written = write_reasoning_lesson(
        query=state["query"], lesson=result.lesson,
        defect_category=result.defect_category,
        applies_to=result.applies_to, confidence=confidence
    )

    return {
        "trace": [{
            "node": "reasoning_reflector",
            "lesson": result.lesson,
            "defect_category": result.defect_category,
            "confidence": confidence,
            "status": written.get("status")
        }]
    }