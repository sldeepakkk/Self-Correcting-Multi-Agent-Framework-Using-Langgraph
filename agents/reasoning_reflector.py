from pydantic import BaseModel, Field
from utils.llm_factory import get_llm
from utils.llm_json import invoke_with_retry
from config import REFLECTOR_MODEL


class ReasoningLesson(BaseModel):
    """No confidence field — engineering computes that mechanically,
    exactly like the web judge's overall_score is computed, not LLM-guessed."""
    lesson: str
    defect_category: str
    applies_to: str


def run_reasoning_reflector(
    query: str,
    original_response: str,
    first_critique: dict,
    revised_response: str,
    final_critique: dict
) -> ReasoningLesson | None:
    """
    Distills a genuinely-resolved reasoning defect into an abstract lesson.
    Sees the FULL before/after — not just the two critiques — so it can
    observe what textual change actually closed the gap, not just that
    something changed.
    """
    system_prompt = """You distill a resolved reasoning defect into a reusable
policy lesson for a financial research system.

CRITICAL RULE: Never mention specific names, companies, numbers, or facts
from this run. If you write a proper noun or a specific figure, delete it
and describe the PATTERN instead.

Bad:  "Jerome Powell isn't RBI governor"
Good: "Queries embedding a named official's title alongside an institution
       should be checked for institutional misattribution"

Look at what changed between the original and revised response to understand
WHY the fix worked, not just that the critique score improved.

Respond ONLY with valid JSON:
{"lesson": "...", "defect_category": "...", "applies_to": "..."}"""

    user_message = f"""Query: {query}

Original response:
{original_response[:1200]}

Initial critique (defect found):
{first_critique}

Revised response:
{revised_response[:1200]}

Final critique (defect resolved):
{final_critique}

Distill ONE abstract, reusable reasoning policy lesson explaining what
changed and why it fixed the defect."""

    llm = get_llm(REFLECTOR_MODEL, temperature=0.1)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])
        return ReasoningLesson(**parsed)
    except Exception as e:
        print(f"[REASONING REFLECTOR] Failed: {e}. Skipping lesson write.")
        return None


def compute_reasoning_confidence(initial: dict, final: dict, critic_search_used: bool, revision_count: int) -> float:
    initial_issues = (
        len(initial.get("unsupported_claims", [])) +
        len(initial.get("overconfidence_flags", [])) +
        len(initial.get("premise_issues", []))
    )
    substance = min(1.0, initial_issues / 3.0)
    evidence_bonus = 0.1 if critic_search_used else 0.0
    revision_penalty = -0.05 * max(0, revision_count - 1)
    return round(max(0.0, min(1.0, substance + evidence_bonus + revision_penalty)), 2)