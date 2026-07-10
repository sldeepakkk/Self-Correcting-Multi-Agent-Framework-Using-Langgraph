from graph import state
from graph.state import AgentState
from agents.planner import run_planner
from agents.judge import run_judge, run_judge_on_text, run_web_judge
from agents.generator import run_generator
from agents.reflector import run_reflector
from retrieval.vector_store import VectorStore
from retrieval.crag import run_crag_fallback
from memory.episodic import write_lesson
from config import JUDGE_RELEVANCE_THRESHOLD
from retrieval.crag import run_crag_fallback, run_crag_retry
import uuid

# initialise once at import — loaded from disk, not rebuilt each call
_vector_store = VectorStore()


# ── Node 1: Planner ───────────────────────────────────────────────────────────

def planner_node(state: AgentState) -> dict:
    """
    Decomposes the raw query into 2-3 sub-queries.
    Loads episodic lessons as priors — policy improvement manifests here.
    Detects compound queries and logs is_compound flag to trace.
    """
    print(f"\n[NODE: PLANNER] Query: {state['query'][:80]}...")

    lessons = state.get("episodic_lessons", [])
    if lessons:
        print(f"[NODE: PLANNER] Loaded {len(lessons)} episodic lessons as priors")

    result = run_planner(
        query=state["query"],
        episodic_lessons=lessons
    )

    print(f"[NODE: PLANNER] Compound query: {result.is_compound}")
    print(f"[NODE: PLANNER] Sub-queries: {result.sub_queries}")
    print(f"[NODE: PLANNER] Reasoning: {result.reasoning}")

    return {
        "sub_queries": result.sub_queries,
        "is_compound_query": result.is_compound,
        "trace": [{
            "node": "planner",
            "is_compound_query": result.is_compound,
            "sub_queries": result.sub_queries,
            "reasoning": result.reasoning,
            "is_compound": result.is_compound,
            "lessons_applied": len(lessons)
        }]
    }


# ── Node 2: Retriever ─────────────────────────────────────────────────────────

def retriever_node(state: AgentState) -> dict:
    """
    Searches the FAISS vector store with each sub-query.
    Merges and deduplicates results.
    """
    print(f"\n[NODE: RETRIEVER] Searching {len(state['sub_queries'])} sub-queries...")

    docs = _vector_store.search_multi(
        sub_queries=state["sub_queries"],
        top_k_per_query=5
    )

    print(f"[NODE: RETRIEVER] Retrieved {len(docs)} unique documents")
    for doc in docs:
        print(f"  score={doc['score']:.4f} | {doc['source']}")

    return {
        "retrieved_docs": docs,
        "trace": [{
            "node": "retriever",
            "doc_count": len(docs),
            "sources": [d["source"] for d in docs],
            "top_score": docs[0]["score"] if docs else 0.0
        }]
    }


# ── Node 3: Gate 1 ────────────────────────────────────────────────────────────

def gate1_node(state: AgentState) -> dict:
    """
    Cheap heuristic filter. Sets gate1_passed.
    Routing decision is made in edges.py gate1_check().
    """
    docs = state.get("retrieved_docs", [])
    top_score = docs[0].get("score", 0.0) if docs else 0.0
    sources = [d.get("source", "") for d in docs]
    unique_sources = len(set(sources))

    passed = (
        top_score >= 0.65 and
        len(docs) >= 2 and
        unique_sources >= 2
    )

    return {
        "gate1_passed": passed,
        "trace": [{
            "node": "gate1",
            "passed": passed,
            "top_score": top_score,
            "doc_count": len(docs),
            "unique_sources": unique_sources
        }]
    }



# ── Node 4: Judge ─────────────────────────────────────────────────────────────

def judge_node(state: AgentState) -> dict:
    """
    Adversarial LLM evaluation of retrieved docs against the query.
    Separate objective from generator. Score < threshold → CRAG.
    """
    print(f"\n[NODE: JUDGE] Evaluating {len(state['retrieved_docs'])} docs...")

    result = run_judge(
        query=state["query"],
        retrieved_docs=state["retrieved_docs"][:3] # ONLY pass top 3
    )

    print(f"[NODE: JUDGE] Score: {result.score:.4f} | Verdict: {result.verdict}")
    print(f"[NODE: JUDGE] Reasoning: {result.reasoning}")
    if result.missing_information:
        print(f"[NODE: JUDGE] Missing: {result.missing_information}")

    return {
        "judge_score": result.score,
        "judge_reasoning": result.reasoning,
        "trace": [{
            "node": "judge",
            "score": result.score,
            "verdict": result.verdict,
            "reasoning": result.reasoning,
            "missing_information": result.missing_information
        }]
    }


# ── Node 5: CRAG ──────────────────────────────────────────────────────────────

def crag_node(state: AgentState) -> dict:
    print(f"\n[NODE: CRAG] Fallback triggered — running web search...")

    is_compound = state.get("is_compound_query", False)
    retrieved_docs = state.get("retrieved_docs", [])

    preserved_context = ""
    if is_compound and retrieved_docs:
        MIN_PRESERVE_SCORE = 0.30
        preserved_docs = [d for d in retrieved_docs if d.get("score", 0.0) >= MIN_PRESERVE_SCORE]
        if preserved_docs:
            preserved_context = "\n\n".join([
                f"[Vector Store — {d.get('source', 'unknown')}]\n{d.get('content', '')}"
                for d in preserved_docs[:3]
            ])

    refined_context, prefilter_passed = run_crag_fallback(
        query=state["query"],
        sub_queries=state["sub_queries"],
        judge_score=state.get("judge_score", 0.0)
    )

    # If the refiner itself flagged failure, do NOT trust refined_context's
    # content even if preserved vector docs exist alongside it — but DO still
    # allow preserved_context alone to go to the judge, since that's real
    # vector store data, not refiner-flagged garbage.
    if not prefilter_passed:
        print(f"[NODE: CRAG] Refiner flagged failure — discarding web content, "
              f"keeping only preserved vector context (if any)")
        refined_context = ""   # discard the flagged-bad web content entirely

    if preserved_context and refined_context:
        combined_context = f"## Web Search Context\n{refined_context}\n\n## Vector Store Context\n{preserved_context}"
    elif refined_context:
        combined_context = refined_context
    elif preserved_context:
        combined_context = preserved_context
    else:
        combined_context = ""

    return {
        "final_context": combined_context,
        "crag_triggered": True,
        "web_search_results": [],
        "trace": [{
            "node": "crag",
            "triggered": True,
            "prefilter_passed": prefilter_passed,
            "is_compound": is_compound,
            "context_length": len(combined_context)
        }]
    }

def post_crag_judge_node(state: AgentState) -> dict:
    """
    Aspect-based evaluation of CRAG-refined web context.
    Uses synthesis-aware rubric — evaluates raw ingredients for synthesis,
    not whether any single source already answers the query.
    Stores structured aspect scores in state for targeted retry.
    """
    from agents.judge import run_web_judge

    print(f"\n[NODE: POST-CRAG JUDGE] Aspect-based evaluation of web context...")

    refined_context = state.get("final_context", "")
    is_compound = state.get("is_compound_query", False)

    if not refined_context:
        print("[NODE: POST-CRAG JUDGE] No refined context to judge — auto-fail")
        # Use the planner's existing decomposed sub_queries as retry material,
        # not the raw original query — sub_queries are already properly atomic.
        fallback_retry = state.get("sub_queries", [state.get("query", "")])[:3]
        fail_aspect = {"score": 0.0, "present": False, "gap": "no content"}
        return {
            "recovery_succeeded": False,
            "judge_score": 0.0,
            "judge_aspect_scores": {
            "topic_a": fail_aspect,
            "topic_b": fail_aspect,
            "factual_density": fail_aspect,
            "synthesis_ready": False,
            "retry_focus": fallback_retry
        },
        "crag_missing_info": fallback_retry,
        "trace": [{"node": "post_crag_judge", "score": 0.0,
                   "verdict": "FAIL", "reasoning": "No content"}]
    }

    result = run_web_judge(
        query=state["query"],
        text=refined_context,
        is_compound=is_compound
    )

    print(f"[NODE: POST-CRAG JUDGE] topic_a={result.topic_a.score:.2f} "
          f"topic_b={result.topic_b.score:.2f} "
          f"factual={result.factual_density.score:.2f}")
    print(f"[NODE: POST-CRAG JUDGE] synthesis_ready={result.synthesis_ready} "
          f"| overall={result.overall_score:.2f}")

    if not result.synthesis_ready:
        gaps = []
        if not result.topic_a.present:
            gaps.append(f"topic_a: {result.topic_a.gap}")
        if not result.topic_b.present:
            gaps.append(f"topic_b: {result.topic_b.gap}")
        if not result.factual_density.present:
            gaps.append(f"factual: {result.factual_density.gap}")
        print(f"[NODE: POST-CRAG JUDGE] Gaps: {gaps}")
        print(f"[NODE: POST-CRAG JUDGE] Retry focus: {result.retry_focus}")

    aspect_scores = {
        "topic_a": result.topic_a.dict(),
        "topic_b": result.topic_b.dict(),
        "factual_density": result.factual_density.dict(),
        "synthesis_ready": result.synthesis_ready,
        "retry_focus": result.retry_focus
    }

    return {
        "recovery_succeeded": result.synthesis_ready,
        "judge_score": result.overall_score,
        "judge_aspect_scores": aspect_scores,
        "crag_missing_info": result.retry_focus,
        "trace": [{
            "node": "post_crag_judge",
            "score": result.overall_score,
            "verdict": result.verdict,
            "synthesis_ready": result.synthesis_ready,
            "topic_a_score": result.topic_a.score,
            "topic_b_score": result.topic_b.score,
            "factual_density_score": result.factual_density.score,
            "retry_focus": result.retry_focus
        }]
    }


# ── Node 7: Assemble Context (medium path) ────────────────────────────────────

def assemble_context_node(state: AgentState) -> dict:
    """
    Assembles final_context from vector store docs on clean path.
    Generator always reads from final_context regardless of path.
    """
    docs = state.get("retrieved_docs", [])
    context = "\n\n".join([
        f"[Source: {d.get('source', 'unknown')}]\n{d.get('content', '')}"
        for d in docs
    ])

    return {
        "final_context": context,
        "crag_triggered": False,
        "trace": [{
            "node": "assemble_context",
            "source": "vector_store",
            "doc_count": len(docs),
            "context_length": len(context)
        }]
    }

def crag_retry_node(state: AgentState) -> dict:
    """
    Corrective retry using aspect-based feedback.
    retry_focus comes from the web judge's structured aspect evaluation.

    If web retry fails, explicitly preserves the existing final_context
    (which may contain hybrid vector store content from crag_node) rather
    than overwriting it with an empty string. This makes the fallback
    path explicit and traceable instead of accidental.
    """
    print(f"\n[NODE: CRAG RETRY] Targeted retry using aspect-based feedback...")

    aspect_scores = state.get("judge_aspect_scores", {})
    retry_focus = aspect_scores.get("retry_focus", [])

    if not retry_focus:
        retry_focus = state.get("crag_missing_info", [state.get("query", "")])

    print(f"[NODE: CRAG RETRY] Retry queries from aspect feedback: {retry_focus}")

    refined_context, prefilter_passed = run_crag_retry(
        query=state["query"],
        missing_information=retry_focus
    )

    if prefilter_passed and refined_context:
        # Web retry succeeded — use fresh web context
        final_context = refined_context
        context_source = "web_retry"
        print(f"[NODE: CRAG RETRY] Web retry succeeded — "
              f"{len(refined_context)} chars of fresh context")
    else:
        # Web retry failed — explicitly preserve whatever is already in state
        # This is typically the hybrid context (preserved vector docs) that
        # crag_node assembled. Overwriting with empty would lose that content.
        final_context = state.get("final_context", "")
        context_source = "preserved_from_crag_node"
        if final_context:
            print(f"[NODE: CRAG RETRY] Web retry failed — preserving existing "
                  f"context ({len(final_context)} chars) from crag_node for judge")
        else:
            print(f"[NODE: CRAG RETRY] Web retry failed — no existing context "
                  f"to fall back to, final fallback will be insufficient-data response")

    return {
        "final_context": final_context,
        "crag_retry_count": state.get("crag_retry_count", 0) + 1,
        "trace": [{
            "node": "crag_retry",
            "retry_queries": retry_focus,
            "prefilter_passed": prefilter_passed,
            "context_source": context_source,
            "context_length": len(final_context)
        }]
    }


# ── Node 8: Generator ─────────────────────────────────────────────────────────

def generator_node(state: AgentState) -> dict:
    """
    Synthesizes the final research report from verified context.
    Handles all three path outcomes: clean, CRAG success, CRAG failure.
    CRAG failure returns calibrated insufficient-data response.
    """
    print(f"\n[NODE: GENERATOR] Synthesizing report...")
    print(f"  CRAG triggered: {state.get('crag_triggered', False)}")
    print(f"  Recovery succeeded: {state.get('recovery_succeeded', False)}")
    print(f"  Context length: {len(state.get('final_context', ''))} chars")

    crag = state.get("crag_triggered", False)
    recovery = state.get("recovery_succeeded", False)
    judge_score = state.get("judge_score", 0.0)

    # Partial case: retry exhausted, score close to threshold with strong core aspects
    is_partial = (crag and not recovery and judge_score >= 0.65 and
                  state.get("crag_retry_count", 0) >= 1)

    # Fast-fail short-circuit: Do not invoke the 70B model if context is dead
    if crag and not recovery and not is_partial:
        path = "slow_failed"
        response = "## Research Report — Insufficient Data\n\n**Status:** This query requires current information that could not be retrieved reliably. The vector store did not contain relevant documents, and web search did not return financially usable content.\n\n**Confidence:** Low — no synthesis attempted to avoid hallucination."
        
        print(f"[NODE: GENERATOR] Done — path={path} (Fast-Fail)")
        return {
            "response": response,
            "path_taken": path,
            "trace": [{
                "node": "generator",
                "path": path,
                "response_length": len(response),
                "context_source": "insufficient"
            }]
        }

    # Clean path or successful CRAG recovery
    path = "slow" if crag else "medium"
    
    response = run_generator(
        query=state["query"],
        final_context=state.get("final_context", ""),
        sub_queries=state.get("sub_queries", []),            # INJECTED: Traceability from Planner
        missing_info=state.get("crag_missing_info", []),
        premise_correction=state.get("premise_correction", ""),     # INJECTED: Traceability from Judge retry
        crag_triggered=crag,
        recovery_succeeded=recovery,
        episodic_lessons=state.get("episodic_lessons", [])
    )

    print(f"[NODE: GENERATOR] Done — path={path}, response={len(response)} chars")

    return {
        "response": response,
        "path_taken": path,
        "trace": [{
            "node": "generator",
            "path": path,
            "response_length": len(response),
            "context_source": "web" if crag else "vector_store"
        }]
    }



def thesis_critic_node(state: AgentState) -> dict:
    """
    Reasoning-loop critic — evaluates the GENERATOR'S OWN ARGUMENT, distinct
    from the retrieval judge which only evaluates source material adequacy.
    Skipped entirely for slow_failed — a refusal message has no thesis
    to critique.
    """
    if state.get("path_taken") == "slow_failed":
        return {
            "thesis_critique": {"thesis_sound": True},
            "trace": [{"node": "thesis_critic", "skipped": True, "reason": "slow_failed"}]
        }

    from agents.critic import run_thesis_critic
    print(f"\n[NODE: THESIS CRITIC] Evaluating response argument...")

    result = run_thesis_critic(
        query=state["query"],
        response=state.get("response", ""),
        context=state.get("final_context", "")
    )

    print(f"[NODE: THESIS CRITIC] thesis_sound={result.thesis_sound}")
    if not result.thesis_sound:
        print(f"[NODE: THESIS CRITIC] premise_issues={result.premise_issues}")
        print(f"[NODE: THESIS CRITIC] unsupported_claims={result.unsupported_claims}")
        print(f"[NODE: THESIS CRITIC] overconfidence_flags={result.overconfidence_flags}")
        print(f"[NODE: THESIS CRITIC] revision_instructions={result.revision_instructions}")

    initial_snapshot = state.get("initial_reasoning_state", {})
    if not initial_snapshot:
        # First critic pass this run — snapshot everything the reflector
        # will need later, decoupled from the live critique schema.
        initial_snapshot = {
            "thesis_sound": result.thesis_sound,
            "premise_issues": result.premise_issues,
            "unsupported_claims": result.unsupported_claims,
            "overconfidence_flags": result.overconfidence_flags,
            "missing_requirements": result.missing_requirements,
            "original_response": state.get("response", ""),
        }

    return {
        "thesis_critique": result.dict(),
        "prev_thesis_critique": state.get("thesis_critique", {}),
        "initial_reasoning_state": initial_snapshot,
        "trace": [{
            "node": "thesis_critic",
            "thesis_sound": result.thesis_sound,
            "premise_issues": result.premise_issues,
            "unsupported_claims": result.unsupported_claims,
            "overconfidence_flags": result.overconfidence_flags
        }]
    }

# ── Node : Revise ─────────────────────────────────────────────────────────
def generator_revise_node(state: AgentState) -> dict:
    from agents.generator import run_generator_revision
    print(f"\n[NODE: GENERATOR REVISE] Revising based on critique...")

    final_context = state.get("final_context", "")

    # If critic_search just ran, flag that fresh evidence was appended so
    # the revision prompt explicitly knows to use it, not just rephrase
    # the same argument around unchanged context.
    if state.get("critic_search_used", False) and "## Critic-Requested Evidence" in final_context:
        print(f"[NODE: GENERATOR REVISE] Fresh critic-directed evidence present in context")

    revised = run_generator_revision(
        query=state["query"],
        original_response=state.get("response", ""),
        critique=state.get("thesis_critique", {}),
        final_context=state.get("final_context", "")
    )

    new_count = state.get("thesis_revision_count", 0) + 1
    print(f"[NODE: GENERATOR REVISE] Revision {new_count} complete, "
          f"response={len(revised)} chars")

    return {
        "response": revised,
        "thesis_revision_count": new_count,
        "trace": [{"node": "generator_revise", "revision_count": new_count}]
    }

# ── Node : Revise search ─────────────────────────────────────────────────────────
 
def critic_search_node(state: AgentState) -> dict:
    """
    Fires once when the critic flags a specific, searchable gap.
    Fetches targeted evidence, then — same as the main CRAG path —
    routes it through the aspect-based judge before trusting it as
    usable evidence, rather than only checking the cheap pre-filter.
    This closes the geography-mismatch gap using the same reasoning-
    based verification the rest of the pipeline already relies on,
    instead of a new keyword blocklist.
    """
    from retrieval.crag import run_critic_directed_search
    from agents.judge import run_web_judge

    critique = state.get("thesis_critique", {})
    claim = critique.get("needs_evidence", "")

    print(f"\n[NODE: CRITIC SEARCH] Fetching evidence: '{claim}'")

    evidence, prefilter_passed = run_critic_directed_search(claim)
    existing_context = state.get("final_context", "")

    if not prefilter_passed or not evidence:
        print(f"[NODE: CRITIC SEARCH] Pre-filter failed — no usable evidence")
        return {
            "final_context": existing_context,
            "critic_search_used": True,
            "trace": [{"node": "critic_search", "claim": claim,
                       "evidence_found": False}]
        }
    judged = run_web_judge(query=state["query"], text=evidence, is_compound=False)

    if judged.overall_score >= 0.5:
        new_context = f"{existing_context}\n\n## Critic-Requested Evidence\n{evidence}"
        print(f"[NODE: CRITIC SEARCH] Evidence judged relevant "
              f"(score={judged.overall_score:.2f}) — appended")
        found = True
    else:
        new_context = existing_context
        print(f"[NODE: CRITIC SEARCH] Evidence judged irrelevant to original query "
              f"(score={judged.overall_score:.2f}, likely off-topic/wrong entity) — discarded")
        found = False

    return {
        "final_context": new_context,
        "critic_search_used": True,
        "trace": [{
            "node": "critic_search",
            "claim": claim,
            "evidence_found": found,
            "judge_score": judged.overall_score
        }]
    }

# ── Node 9: Reflector ─────────────────────────────────────────────────────────

def reflector_node(state: AgentState) -> dict:
    """
    Reads the full execution trace and produces one compressed policy lesson.
    Gate 3 lives in episodic.write_lesson() — confidence filter applied there.
    Only called when Gate 2 fires: crag_triggered AND recovery_succeeded.

    If run_reflector returns None (parse failure after retries), the lesson
    write is skipped entirely — no fabricated lesson enters episodic memory.
    """
    print(f"\n[NODE: REFLECTOR] Distilling lesson from trace...")

    run_id = str(uuid.uuid4())[:8]

    result = run_reflector(
        query=state["query"],
        sub_queries=state.get("sub_queries", []),
        trace=state.get("trace", []),
        judge_score=state.get("judge_score", 0.0),
        recovery_succeeded=state.get("recovery_succeeded", False)
    )

    if result is None:
        print(f"[NODE: REFLECTOR] No lesson written — reflector failed to produce valid output")
        return {
            "trace": [{
                "node": "reflector",
                "run_id": run_id,
                "status": "skipped_parse_failure"
            }]
        }

    print(f"[NODE: REFLECTOR] Category: {result.query_category}")
    print(f"[NODE: REFLECTOR] Confidence: {result.confidence:.2f}")
    print(f"[NODE: REFLECTOR] Lesson: {result.lesson}")
    print(f"[NODE: REFLECTOR] Routing rec: {result.routing_recommendation}")

    written = write_lesson(
        query=state["query"],
        query_category=result.query_category,
        lesson=result.lesson,
        confidence=result.confidence,
        routing_recommendation=result.routing_recommendation,
        run_id=run_id
    )

    return {
        "trace": [{
            "node": "reflector",
            "run_id": run_id,
            "lesson": result.lesson,
            "category": result.query_category,
            "confidence": result.confidence,
            "gate3_status": written["status"]
        }]
    }


def premise_check_node(state: AgentState) -> dict:
    """
    Runs immediately after the planner, before retrieval or generation.
    Cheap plain-text check for institutional/personnel misattribution —
    catches cases like "SEBI, chaired by Shaktikanta Das" deterministically,
    upstream of the fragile thesis critic. This is the structural fix:
    premise correction no longer depends on a post-hoc JSON call succeeding.
    """
    from agents.critic import run_premise_check
    print(f"\n[NODE: PREMISE CHECK] Screening query for institutional errors...")

    result = run_premise_check(state["query"])

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

def reasoning_reflector_node(state: AgentState) -> dict:
    """
    Gate lives INSIDE this node (mirrors reasoning_gate2_check discussed
    earlier, but implemented here to keep the graph edge simple — this
    node always runs after thesis_critic terminates, and internally
    decides whether a lesson is warranted).
    """
    from agents.reasoning_reflector import run_reasoning_reflector, compute_reasoning_confidence
    from memory.episodic import write_reasoning_lesson

    initial = state.get("initial_reasoning_state", {})
    final_critique = state.get("thesis_critique", {})
    revision_count = state.get("thesis_revision_count", 0)

    if not initial:
        return {"trace": [{"node": "reasoning_reflector", "status": "no_initial_critique"}]}

    defect_found = (not initial.get("thesis_sound", True)) or bool(initial.get("unsupported_claims")) or bool(initial.get("overconfidence_flags"))
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
        critic_search_used=state.get("critic_search_used", False),
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