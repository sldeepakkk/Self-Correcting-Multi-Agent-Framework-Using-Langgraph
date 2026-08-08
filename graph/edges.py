from graph.state import AgentState
from agents.critic import has_converged
from config import (
    JUDGE_RELEVANCE_THRESHOLD,
    GATE1_MIN_RESPONSE_LENGTH,
    GATE1_UNCERTAINTY_MARKER_LIMIT,
    GATE1_UNCERTAINTY_MARKERS
)

# ─────────────────────────────────────────────────
MAX_REVISIONS = 2
MAX_SEARCHES = 1

def route_after_thesis_critique(state: AgentState) -> str:
    critique = state.get("thesis_critique", {})
    prev = state.get("prev_thesis_critique", {})
    revisions = state.get("thesis_revision_count", 0)
    searches = state.get("search_count", 0)

    if prev and has_converged(prev, critique):
        return "reasoning_check"
    if revisions >= MAX_REVISIONS:
        return "reasoning_check"
    if not critique.get("thesis_sound", True):
        if critique.get("needs_evidence") and searches < MAX_SEARCHES:
            return "evidence_search"
        return "revise"
    return "reasoning_check"
