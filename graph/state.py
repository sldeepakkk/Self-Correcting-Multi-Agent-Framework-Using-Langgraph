from typing import Annotated, Optional, Any
from typing_extensions import TypedDict
import operator


class AgentState(TypedDict):
    query: str
    sub_queries: list[str]
    is_compound_query: bool
    premise_correction: str
    final_context: str
    evidence_confidence: str
    response: str
    path_taken: str
    trace: Annotated[list[dict], operator.add]
    episodic_lessons: list[str]
    cache_hit: bool
    thesis_critique: dict
    prev_thesis_critique: dict
    initial_reasoning_state: dict
    thesis_revision_count: int
    search_count: int