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

# # ── Node 3: Gate 1 ────────────────────────────────────────────────────────────

# def gate1_node(state: AgentState) -> dict:
#     docs = state.get("retrieved_docs", [])
#     top_score = docs[0].get("score", 0.0) if docs else 0.0
#     sources = [d.get("source", "") for d in docs]
#     unique_sources = len(set(sources))
    
#     # NEW LOGIC: Use the length of the sub_queries list. 
#     # If the planner generated more than 1 sub-query, it's compound.
#     sub_queries = state.get("sub_queries", [])
#     is_compound = len(sub_queries) > 1 

#     if is_compound:
#         passed = False
#         reason = f"Compound query detected ({len(sub_queries)} sub-queries) — forcing adversarial Judge evaluation."
#     else:
#         passed = (
#             top_score >= 0.65 and
#             len(docs) >= 2 and
#             unique_sources >= 2
#         )
#         reason = "Single-topic heuristic check."

#     return {
#         "gate1_passed": passed,
#         "trace": [{
#             "node": "gate1",
#             "passed": passed,
#             "top_score": top_score,
#             "doc_count": len(docs),
#             "unique_sources": unique_sources,
#             "reason": reason
#         }]
#     }


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
        preserved_docs = [
            d for d in retrieved_docs
            if d.get("score", 0.0) >= MIN_PRESERVE_SCORE
        ]
        if preserved_docs:
            preserved_context = "\n\n".join([
                f"[Vector Store — {d.get('source', 'unknown')}]\n{d.get('content', '')}"
                for d in preserved_docs[:3]
            ])
            print(f"[NODE: CRAG] Compound query — preserving {len(preserved_docs)} "
                  f"vector store docs (score >= {MIN_PRESERVE_SCORE})")

    refined_context, prefilter_passed = run_crag_fallback(
        query=state["query"],
        sub_queries=state["sub_queries"],
        judge_score=state.get("judge_score", 0.0)
    )

    if preserved_context and refined_context:
        combined_context = (
            f"## Web Search Context\n{refined_context}"
            f"\n\n## Vector Store Context\n{preserved_context}"
        )
    elif refined_context:
        combined_context = refined_context
    elif preserved_context:
        combined_context = preserved_context
        print(f"[NODE: CRAG] Web failed — using preserved vector context only")
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


# ── Node 6: Post-CRAG Judge ───────────────────────────────────────────────────

# def post_crag_judge_node(state: AgentState) -> dict:
#     """
#     Judges the CRAG-refined web context using the same adversarial rubric
#     applied to vector store retrieval. Closes the architectural gap where
#     CRAG recovery was previously trusted on a cheap heuristic alone.

#     recovery_succeeded is set HERE, based on a real judge score.
#     """
#     print(f"\n[NODE: POST-CRAG JUDGE] Evaluating refined web context...")

#     refined_context = state.get("final_context", "")

#     if not refined_context:
#         print("[NODE: POST-CRAG JUDGE] No refined context to judge — auto-fail")
#         return {
#             "recovery_succeeded": False,
#             "trace": [{
#                 "node": "post_crag_judge",
#                 "score": 0.0,
#                 "verdict": "FAIL",
#                 "reasoning": "No refined context available"
#             }]
#         }

#     result = run_judge_on_text(
#         query=state["query"],
#         text=refined_context,
#         source_label="web_search_refined"
#     )

#     recovery_succeeded = result.score >= JUDGE_RELEVANCE_THRESHOLD

#     print(f"[NODE: POST-CRAG JUDGE] Score: {result.score:.4f} | "
#           f"Recovery: {'SUCCESS' if recovery_succeeded else 'FAILED'}")
#     print(f"[NODE: POST-CRAG JUDGE] Reasoning: {result.reasoning}")

#     return {
#         "recovery_succeeded": recovery_succeeded,
#         "judge_score": result.score,
#         "trace": [{
#             "node": "post_crag_judge",
#             "score": result.score,
#             "verdict": result.verdict,
#             "reasoning": result.reasoning,
#             "recovery_succeeded": recovery_succeeded
#         }]
#     }


# def post_crag_judge_node(state: AgentState) -> dict:
#     """
#     Judges the CRAG-refined web context using the same adversarial rubric
#     applied to vector store retrieval.

#     UPDATED: now stores missing_information to crag_missing_info in state,
#     so route_after_crag_judge → crag_retry_node can use it for a corrective
#     second attempt instead of giving up after one search.
#     """
#     print(f"\n[NODE: POST-CRAG JUDGE] Evaluating refined web context...")

#     refined_context = state.get("final_context", "")

#     if not refined_context:
#         print("[NODE: POST-CRAG JUDGE] No refined context to judge — auto-fail")
#         return {
#             "recovery_succeeded": False,
#             "crag_missing_info": ["No content was retrieved at all"],
#             "trace": [{
#                 "node": "post_crag_judge",
#                 "score": 0.0,
#                 "verdict": "FAIL",
#                 "reasoning": "No refined context available"
#             }]
#         }

#     result = run_judge_on_text(
#         query=state["query"],
#         text=refined_context,
#         source_label="web_search_refined"
#     )

#     recovery_succeeded = result.score >= JUDGE_RELEVANCE_THRESHOLD

#     print(f"[NODE: POST-CRAG JUDGE] Score: {result.score:.4f} | "
#           f"Recovery: {'SUCCESS' if recovery_succeeded else 'FAILED'}")
#     print(f"[NODE: POST-CRAG JUDGE] Reasoning: {result.reasoning}")

#     return {
#         "recovery_succeeded": recovery_succeeded,
#         "judge_score": result.score,
#         "crag_missing_info": result.missing_information,
#         "trace": [{
#             "node": "post_crag_judge",
#             "score": result.score,
#             "verdict": result.verdict,
#             "reasoning": result.reasoning,
#             "recovery_succeeded": recovery_succeeded,
#             "missing_information": result.missing_information
#         }]
#     }

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
        fail_aspect = {"score": 0.0, "present": False, "gap": "no content"}
        return {
            "recovery_succeeded": False,
            "judge_score": 0.0,
            "judge_aspect_scores": {
                "topic_a": fail_aspect,
                "topic_b": fail_aspect,
                "factual_density": fail_aspect,
                "synthesis_ready": False,
                "retry_focus": [state.get("query", "")]
            },
            "trace": [{"node": "post_crag_judge", "score": 0.0,
                       "verdict": "FAIL", "reasoning": "No context"}]
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


# ── Node: CRAG Retry (NEW) ────────────────────────────────────────────────────

# def crag_retry_node(state: AgentState) -> dict:
#     """
#     The actual self-correction step. Uses missing_information from the failed
#     post_crag_judge pass to reformulate and retry the web search once.

#     This closes the gap where CRAG produced structured failure feedback
#     (missing_information) but never used it — it was being logged and discarded.
#     Now it directly drives a second, better-targeted search attempt.
#     """
#     print(f"\n[NODE: CRAG RETRY] Attempting corrective retry...")

#     missing_info = state.get("crag_missing_info", [])

#     refined_context, prefilter_passed = run_crag_retry(
#         query=state["query"],
#         missing_information=missing_info
#     )

#     return {
#         "final_context": refined_context,
#         "crag_retry_count": state.get("crag_retry_count", 0) + 1,
#         "trace": [{
#             "node": "crag_retry",
#             "missing_info_used": missing_info,
#             "prefilter_passed": prefilter_passed,
#             "context_length": len(refined_context)
#         }]
#     }

# def crag_retry_node(state: AgentState) -> dict:
#     """
#     Corrective retry using aspect-based feedback.
#     retry_focus comes from the web judge's structured aspect evaluation —
#     these are targeted queries for the specific missing dimension,
#     not a generic rerun of the original sub-queries.
#     """
#     print(f"\n[NODE: CRAG RETRY] Targeted retry using aspect-based feedback...")

#     aspect_scores = state.get("judge_aspect_scores", {})
#     retry_focus = aspect_scores.get("retry_focus", [])

#     if not retry_focus:
#         retry_focus = state.get("crag_missing_info", [state.get("query", "")])

#     print(f"[NODE: CRAG RETRY] Retry queries from aspect feedback: {retry_focus}")

#     refined_context, prefilter_passed = run_crag_retry(
#         query=state["query"],
#         missing_information=retry_focus
#     )

#     return {
#         "final_context": refined_context,
#         "crag_retry_count": state.get("crag_retry_count", 0) + 1,
#         "trace": [{
#             "node": "crag_retry",
#             "retry_queries": retry_focus,
#             "prefilter_passed": prefilter_passed,
#             "context_length": len(refined_context)
#         }]
#     }

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

# def generator_node(state: AgentState) -> dict:
#     """
#     Synthesizes the final research report from verified context.
#     Handles all three path outcomes: clean, CRAG success, CRAG failure.
#     CRAG failure returns calibrated insufficient-data response.
#     """
#     print(f"\n[NODE: GENERATOR] Synthesizing report...")
#     print(f"  CRAG triggered: {state.get('crag_triggered', False)}")
#     print(f"  Recovery succeeded: {state.get('recovery_succeeded', False)}")
#     print(f"  Context length: {len(state.get('final_context', ''))} chars")

#     response = run_generator(
#         query=state["query"],
#         final_context=state.get("final_context", ""),
#         crag_triggered=state.get("crag_triggered", False),
#         recovery_succeeded=state.get("recovery_succeeded", False),
#         episodic_lessons=state.get("episodic_lessons", [])
#     )

#     crag = state.get("crag_triggered", False)
#     recovery = state.get("recovery_succeeded", False)

#     if not crag:
#         path = "medium"
#     elif crag and recovery:
#         path = "slow"
#     else:
#         path = "slow_failed"

#     print(f"[NODE: GENERATOR] Done — path={path}, "
#           f"response={len(response)} chars")

#     return {
#         "response": response,
#         "path_taken": path,
#         "trace": [{
#             "node": "generator",
#             "path": path,
#             "response_length": len(response),
#             "context_source": "web" if crag and recovery else
#                               "insufficient" if crag and not recovery else
#                               "vector_store"
#         }]
#     }

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

    # Fast-fail short-circuit: Do not invoke the 70B model if context is dead
    if crag and not recovery:
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
        missing_info=state.get("crag_missing_info", []),     # INJECTED: Traceability from Judge retry
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