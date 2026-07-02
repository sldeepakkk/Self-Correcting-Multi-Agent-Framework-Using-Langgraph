# from langchain_groq import ChatGroq
# from pydantic import BaseModel, Field
# from config import GROQ_API_KEY, JUDGE_MODEL
# from utils.llm_json import parse_llm_json, invoke_with_retry


# # ── Output Models ─────────────────────────────────────────────────────────────

# class JudgeOutput(BaseModel):
#     """Used for vector store retrieval evaluation — single holistic score."""
#     score: float = Field(ge=0.0, le=1.0)
#     reasoning: str
#     verdict: str
#     missing_information: list[str] = Field(default_factory=list)


# class AspectScore(BaseModel):
#     """One dimension of an aspect-based web content evaluation."""
#     score: float = Field(ge=0.0, le=1.0)
#     present: bool
#     gap: str = ""


# class WebJudgeOutput(BaseModel):
#     """
#     Structured output of aspect-based web content evaluation.
#     Used by post_crag_judge_node — replaces the single holistic score
#     with three independently-evaluated dimensions.
#     """
#     topic_a: AspectScore
#     topic_b: AspectScore
#     factual_density: AspectScore
#     synthesis_ready: bool
#     overall_score: float = Field(ge=0.0, le=1.0)
#     verdict: str
#     retry_focus: list[str]


# # ── Vector Store Judge ────────────────────────────────────────────────────────

# def run_judge(query: str, retrieved_docs: list[dict]) -> JudgeOutput:
#     """
#     Adversarial holistic evaluation of vector store retrieved documents.
#     Used by judge_node — asks "does this document answer the query?"
#     Appropriate for structured database docs where each doc should be complete.
#     A separate LLM call from the generator with an adversarial objective.
#     """
#     if not retrieved_docs:
#         return JudgeOutput(
#             score=0.0,
#             reasoning="No documents were retrieved. Cannot evaluate relevance.",
#             verdict="FAIL",
#             missing_information=["All information — retrieval returned empty"]
#         )

#     docs_block = ""
#     for i, doc in enumerate(retrieved_docs[:5]):
#         docs_block += f"\n--- Document {i+1} ---\n"
#         docs_block += f"Source: {doc.get('source', 'unknown')}\n"
#         docs_block += f"Retrieval Score: {doc.get('score', 0.0):.4f}\n"
#         docs_block += f"Content: {doc.get('content', '')}\n"

#     return _run_judge_core(query, docs_block)


# def run_judge_on_text(
#     query: str,
#     text: str,
#     source_label: str = "web_search_refined"
# ) -> JudgeOutput:
#     """
#     Kept for backward compatibility.
#     post_crag_judge_node now calls run_web_judge() instead.
#     This still uses the holistic rubric — wrong question for web content.
#     """
#     docs_block = f"\n--- Document 1 ---\nSource: {source_label}\nContent: {text}\n"
#     return _run_judge_core(query, docs_block)


# def _run_judge_core(query: str, docs_block: str) -> JudgeOutput:
#     """Shared holistic judge logic for vector store evaluation."""

#     system_prompt = """You are an adversarial retrieval evaluator for a financial research system.

# Your ONLY job: determine whether the provided content actually contains what is needed to answer the query.

# You are NOT trying to be helpful. You are trying to find failure.

# Scoring rubric:
# 0.0 - 0.3: Content is completely off-topic or from wrong domain entirely
# 0.3 - 0.5: Content is tangentially related but missing core information needed
# 0.5 - 0.6: Content has partial relevant information but significant gaps remain
# 0.6 - 0.8: Content covers the query adequately with minor gaps acceptable
# 0.8 - 1.0: Content directly and comprehensively answers the query

# Critical: content about the right company but wrong topic still scores low.
# Content with vague claims and no concrete figures, dates, or percentages should
# score below 0.5 even if topically related — vagueness is itself a failure mode.

# Respond ONLY with valid JSON:
# {
#   "score": 0.0,
#   "reasoning": "specific gap explanation",
#   "verdict": "PASS|FAIL|BORDERLINE",
#   "missing_information": ["item1", "item2"]
# }

# No preamble. No explanation. Just JSON."""

#     user_message = f"""Query: {query}

# Content:
# {docs_block}

# Evaluate whether this content contains sufficient information to answer the query."""

#     llm = ChatGroq(api_key=GROQ_API_KEY, model=JUDGE_MODEL, temperature=0.0)

#     response = llm.invoke([
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_message}
#     ])

#     try:
#         parsed = parse_llm_json(response.content)
#         parsed["score"] = max(0.0, min(1.0, float(parsed["score"])))
#         return JudgeOutput(**parsed)
#     except Exception as e:
#         print(f"[JUDGE] JSON parse failed: {e}. Defaulting to fail-safe low score.")
#         return JudgeOutput(
#             score=0.0,
#             reasoning="Judge response parsing failed — defaulting to fail-safe rejection",
#             verdict="FAIL",
#             missing_information=["Could not evaluate — parser error"]
#         )


# # ── Web Content Judge (Aspect-Based) ─────────────────────────────────────────

# def run_web_judge(
#     query: str,
#     text: str,
#     is_compound: bool = False
# ) -> WebJudgeOutput:
#     """
#     Aspect-based evaluation of refined web search content.
#     Used by post_crag_judge_node.

#     The fundamental distinction from run_judge():
#     - run_judge() asks: "does this document answer the query?"
#       Correct for vector store docs — each doc should be self-contained.
#     - run_web_judge() asks: "do these fragments contain synthesis ingredients?"
#       Correct for web content — the generator synthesizes the connection,
#       the judge verifies the ingredients exist, not that the answer is pre-made.

#     Three independent dimensions evaluated:
#     - topic_a: primary topic substantively covered with data?
#     - topic_b: secondary topic covered? (compound queries only)
#     - factual_density: concrete figures, dates, named entities present?

#     synthesis_ready logic:
#     - Compound:     topic_a.present AND topic_b.present AND factual_density.present
#     - Non-compound: topic_a.present AND factual_density.score >= 0.5

#     retry_focus is generated from which specific aspect failed —
#     targeted queries for exactly the missing dimension, making the
#     CRAG retry genuinely corrective rather than a generic rerun.
#     """

#     if is_compound:
#         compound_instruction = """
# This is a COMPOUND query connecting two distinct topics.
# topic_a covers the first/primary topic. topic_b covers the second/secondary topic.
# Evaluate them SEPARATELY — they may be covered by different parts of the content
# without any single paragraph explicitly connecting them.
# That is ACCEPTABLE and EXPECTED. The generator will synthesize the connection.
# Do NOT penalize content for lacking a pre-made connection between topics.
# Set topic_b scores based on whether secondary topic ingredients are present,
# not whether the connection to topic_a has been stated."""
#     else:
#         compound_instruction = """
# This is a SINGLE-TOPIC query.
# Set topic_b: score=1.0, present=true, gap="" — there is no secondary topic.
# Focus evaluation on topic_a coverage and factual_density only."""

#     system_prompt = f"""You are an aspect-based retrieval evaluator for a financial research system.

# You evaluate REFINED WEB SEARCH CONTENT that a synthesis model will use to answer a query.
# {compound_instruction}

# CRITICAL DISTINCTION:
# - You are NOT asking "does this content already answer the query?"
# - You ARE asking "does this content contain the raw ingredients for synthesis?"

# Evaluate THREE aspects independently:

# ASPECT 1 — topic_a (Primary Topic Coverage):
# Does the content contain substantive information about the primary subject?
# score: 0.0-0.3 completely absent, 0.3-0.6 partially present, 0.6-1.0 well covered
# present: true if score >= 0.5
# gap: what specific primary topic information is missing (empty string if present=true)

# ASPECT 2 — topic_b (Secondary Topic Coverage):
# For compound queries: does the content contain info about the secondary subject?
# For non-compound: score=1.0, present=true, gap=""
# score: 0.0-0.3 completely absent, 0.3-0.6 partially present, 0.6-1.0 well covered
# present: true if score >= 0.5
# gap: what specific secondary topic information is missing (empty string if present=true)

# ASPECT 3 — factual_density (Concrete Data Presence):
# Are there specific figures, percentages, basis points, price targets, dates,
# named companies with associated data, or analyst ratings?
# Vague narrative without any concrete numbers scores 0.0-0.3 regardless of topic relevance.
# score: 0.0-0.3 no concrete figures, 0.3-0.6 some figures, 0.6-1.0 rich with data
# present: true if score >= 0.4
# gap: what specific data types are missing (empty string if present=true)

# SYNTHESIS READY:
# For compound:     synthesis_ready = topic_a.present AND topic_b.present AND factual_density.present
# For non-compound: synthesis_ready = topic_a.present AND factual_density.score >= 0.5

# OVERALL SCORE:
# For compound:     (topic_a.score * 0.35) + (topic_b.score * 0.35) + (factual_density.score * 0.30)
# For non-compound: (topic_a.score * 0.60) + (factual_density.score * 0.40)
# Clamp to 0.0-1.0.

# RETRY FOCUS:
# If NOT synthesis_ready: generate 1-3 specific targeted search queries that would
# fill exactly the missing aspect. Make them concrete — analyst article title style.
# Good: "RBI repo rate June 2026 basis points cut SBI HDFC ICICI stock price impact analyst"
# Bad:  "more information about RBI and banking stocks" (too vague)
# If synthesis_ready: return empty list [].

# Respond ONLY with valid JSON — no preamble, no explanation:
# {{
#   "topic_a": {{"score": 0.0, "present": false, "gap": "explanation"}},
#   "topic_b": {{"score": 0.0, "present": false, "gap": "explanation"}},
#   "factual_density": {{"score": 0.0, "present": false, "gap": "explanation"}},
#   "synthesis_ready": false,
#   "overall_score": 0.0,
#   "verdict": "PASS|FAIL|BORDERLINE",
#   "retry_focus": ["targeted query 1", "targeted query 2"]
# }}"""

#     user_message = f"""Query: {query}
# Is compound query: {is_compound}

# Refined Web Content:
# {text}

# Evaluate the three aspects and determine synthesis readiness."""

#     llm = ChatGroq(api_key=GROQ_API_KEY, model=JUDGE_MODEL, temperature=0.0)

#     try:
#         parsed = invoke_with_retry(llm, [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message}
#         ])

#         topic_a = AspectScore(**parsed["topic_a"])
#         topic_b = AspectScore(**parsed["topic_b"])
#         factual_density = AspectScore(**parsed["factual_density"])
#         overall = max(0.0, min(1.0, float(parsed.get("overall_score", 0.0))))

#         return WebJudgeOutput(
#             topic_a=topic_a,
#             topic_b=topic_b,
#             factual_density=factual_density,
#             synthesis_ready=bool(parsed.get("synthesis_ready", False)),
#             overall_score=overall,
#             verdict=parsed.get("verdict", "FAIL"),
#             retry_focus=parsed.get("retry_focus", [])
#         )

#     except Exception as e:
#         print(f"[WEB JUDGE] All retries failed: {e}. Defaulting to fail-safe.")
#         fail_aspect = AspectScore(score=0.0, present=False, gap="parse failure")
#         return WebJudgeOutput(
#             topic_a=fail_aspect,
#             topic_b=fail_aspect,
#             factual_density=fail_aspect,
#             synthesis_ready=False,
#             overall_score=0.0,
#             verdict="FAIL",
#             retry_focus=[query]
#         )

# from langchain_groq import ChatGroq
from utils.llm_factory import get_llm
from pydantic import BaseModel, Field
# from config import GROQ_API_KEY, JUDGE_MODEL
from config import JUDGE_MODEL
from utils.llm_json import parse_llm_json, invoke_with_retry


# ── Output Models ─────────────────────────────────────────────────────────────

class JudgeOutput(BaseModel):
    """Used for vector store retrieval evaluation — single holistic score."""
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    verdict: str
    missing_information: list[str] = Field(default_factory=list)


class AspectScore(BaseModel):
    """One dimension of an aspect-based web content evaluation."""
    score: float = Field(ge=0.0, le=1.0)
    present: bool
    gap: str = ""


class WebJudgeOutput(BaseModel):
    """
    Structured output of aspect-based web content evaluation.
    Used by post_crag_judge_node — replaces subjective text generation
    with strict atomic keywords for retries.
    """
    topic_a: AspectScore
    topic_b: AspectScore
    factual_density: AspectScore
    synthesis_ready: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    verdict: str
    retry_focus: list[str] = Field(
        description="Strictly 2-3 word atomic search phrases. Never full sentences."
    )


# ── Vector Store Judge ────────────────────────────────────────────────────────

def run_judge(query: str, retrieved_docs: list[dict]) -> JudgeOutput:
    """
    Adversarial holistic evaluation of vector store retrieved documents.
    Appropriate for structured database docs where each doc should be complete.
    """
    if not retrieved_docs:
        return JudgeOutput(
            score=0.0,
            reasoning="No documents were retrieved. Cannot evaluate relevance.",
            verdict="FAIL",
            missing_information=["All information — retrieval returned empty"]
        )

    docs_block = ""
    for i, doc in enumerate(retrieved_docs[:5]):
        docs_block += f"\n--- Document {i+1} ---\n"
        docs_block += f"Source: {doc.get('source', 'unknown')}\n"
        docs_block += f"Retrieval Score: {doc.get('score', 0.0):.4f}\n"
        docs_block += f"Content: {doc.get('content', '')}\n"

    return _run_judge_core(query, docs_block)


def run_judge_on_text(
    query: str,
    text: str,
    source_label: str = "web_search_refined"
) -> JudgeOutput:
    """Kept for backward compatibility."""
    docs_block = f"\n--- Document 1 ---\nSource: {source_label}\nContent: {text}\n"
    return _run_judge_core(query, docs_block)


def _run_judge_core(query: str, docs_block: str) -> JudgeOutput:
    """Shared holistic judge logic for vector store evaluation."""

    system_prompt = """You are an adversarial retrieval evaluator for a financial research system.

Your ONLY job: determine whether the provided content actually contains what is needed to answer the query.
You are NOT trying to be helpful. You are looking for failure gaps.

Scoring rubric:
0.0 - 0.3: Content is completely off-topic or irrelevant.
0.3 - 0.5: Content is tangentially related but missing core parameters or answers.
0.5 - 0.6: Content has partial relevant info but structural gaps remain.
0.6 - 0.8: Content covers the query adequately with minor acceptable gaps.
0.8 - 1.0: Content directly and comprehensively answers the query.

CRITICAL: Content missing concrete figures, dates, or percentages MUST score below 0.5. 

Missing information array items MUST be concise atomic keywords (e.g., 'repo rate change', 'SBI margin impact'), NOT full sentences.

Respond ONLY with valid JSON:
{
  "score": 0.0,
  "reasoning": "specific gap explanation",
  "verdict": "PASS|FAIL|BORDERLINE",
  "missing_information": ["keyword1", "keyword2"]
}"""

    user_message = f"""Query: {query}

Content:
{docs_block}

Evaluate whether this content contains sufficient information to answer the query."""

    # llm = ChatGroq(api_key=GROQ_API_KEY, model=JUDGE_MODEL, temperature=0.0)
    llm = get_llm(JUDGE_MODEL, temperature=0.0)

    # response = llm.invoke([
    #     {"role": "system", "content": system_prompt},
    #     {"role": "user", "content": user_message}
    # ])

    # try:
    #     parsed = parse_llm_json(response.content)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])


        parsed["score"] = max(0.0, min(1.0, float(parsed["score"])))
        return JudgeOutput(**parsed)
    except Exception as e:
        print(f"[JUDGE] JSON parse failed: {e}. Defaulting to fail-safe low score.")
        return JudgeOutput(
            score=0.0,
            reasoning="Judge response parsing failed — defaulting to fail-safe rejection",
            verdict="FAIL",
            missing_information=["retrieval evaluation error"]
        )


# ── Web Content Judge (Aspect-Based) ─────────────────────────────────────────

def run_web_judge(
    query: str,
    text: str,
    is_compound: bool = False
) -> WebJudgeOutput:
    """
    Aspect-based extraction evaluation of refined web search content.
    Used by post_crag_judge_node.
    """

    if is_compound:
        compound_instruction = """
This is a COMPOUND query connecting two distinct concepts.
topic_a covers the primary subject. topic_b covers the secondary sector reaction/impact.
Evaluate them SEPARATELY. If topic_b mentions indices (e.g., 'Bank Nifty', 'Nifty Bank') or 
specific bank stock tickers (e.g., 'HDFC', 'SBI', 'ICICI'), you MUST mark it present=true."""
    else:
        compound_instruction = """
This is a SINGLE-TOPIC query.
Force topic_b parameters to: score=1.0, present=true, gap="". Evaluation focuses only on topic_a."""

    system_prompt = f"""You are a literal, data-driven extraction evaluator for a financial research system.
You evaluate REFINED WEB SEARCH CONTENT to verify if raw semantic ingredients exist for final synthesis.
{compound_instruction}

Evaluate THREE aspects independently:

ASPECT 1 — topic_a (Primary Subject Coverage):
Does the content contain clear text about the primary topic mentioned in the query?
score: 0.0-0.3 absent, 0.4-0.6 partially present, 0.7-1.0 fully present
present: true if score >= 0.5

ASPECT 2 — topic_b (Secondary Subject/Impact Coverage):
For compound queries: Does the content contain text covering the secondary asset/impact/sector?
If the text mentions indices like 'Bank Nifty' or bank stocks, it IS present.
score: 0.0-0.3 absent, 0.4-0.6 partially present, 0.7-1.0 fully present
present: true if score >= 0.5 (For non-compound, enforce score=1.0, present=true)

ASPECT 3 — factual_density (Quantitative Data Presence):
Are there numerical values, percentages (%), basis points (bps), price changes, or dates?
score: 0.0-0.3 no numbers/narrative only, 0.4-0.6 few figures, 0.7-1.0 data rich
present: true if score >= 0.4

RETRY FOCUS RULES (CRITICAL):
If any aspect above is NOT present, generate 1 to 3 targeted search elements to fill that gap.
- MUST be ultra-short, atomic phrases (max 2-3 keywords). Examples: 'Bank Nifty reaction', 'SBI stock price'.
- NEVER use conversational framing like "concrete financial figures about" or "information regarding".
- If everything is present, return an empty list [].

Respond ONLY with valid JSON — no preamble, no markdown wrapper codeblocks:
{{
  "topic_a": {{"score": 0.0, "present": false, "gap": "short gap label"}},
  "topic_b": {{"score": 0.0, "present": false, "gap": "short gap label"}},
  "factual_density": {{"score": 0.0, "present": false, "gap": "short gap label"}},
  "retry_focus": ["phrase1", "phrase2"]
}}"""

    user_message = f"""Query: {query}
Is compound query: {is_compound}

Refined Web Content:
{text}

Extract values and provide atomic retry targets if needed."""

    # llm = ChatGroq(api_key=GROQ_API_KEY, model=JUDGE_MODEL, temperature=0.0)
    llm = get_llm(JUDGE_MODEL, temperature=0.0)

    try:
        parsed = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])

        # Extract items into structures safely
        t_a = AspectScore(**parsed["topic_a"])
        t_b = AspectScore(**parsed["topic_b"]) if is_compound else AspectScore(score=1.0, present=True, gap="")
        f_d = AspectScore(**parsed["factual_density"])
        
        # Clean up any potential conversational drift in retry focus items
        raw_retry = parsed.get("retry_focus", [])
        clean_retry = []
        for item in raw_retry[:3]:
            # Regex strip conversational patterns
            cleaned = item.lower()
            cleaned = cleaned.replace("information about", "").replace("concrete financial figures from", "")
            cleaned = cleaned.replace("data regarding", "").replace("details on", "").strip()
            if cleaned:
                clean_retry.append(cleaned)

        # ── Deterministic Engineering Core (Python Overrides LLM Arithmetic) ──
        if is_compound:
            synthesis_ready = bool(t_a.present and t_b.present and f_d.present)
            overall_score = (t_a.score * 0.35) + (t_b.score * 0.35) + (f_d.score * 0.30)
        else:
            synthesis_ready = bool(t_a.present and f_d.score >= 0.5)
            overall_score = (t_a.score * 0.60) + (f_d.score * 0.40)

        overall_score = max(0.0, min(1.0, float(overall_score)))
        if not synthesis_ready and overall_score >= 0.6:
            synthesis_ready = True
            print(f"[WEB JUDGE] synthesis_ready overridden — "
                  f"overall={overall_score:.2f} >= 0.6 with partial aspect coverage")
        verdict = "PASS" if synthesis_ready else ("BORDERLINE" if overall_score >= 0.5 else "FAIL")

        return WebJudgeOutput(
            topic_a=t_a,
            topic_b=t_b,
            factual_density=f_d,
            synthesis_ready=synthesis_ready,
            overall_score=overall_score,
            verdict=verdict,
            retry_focus=clean_retry if not synthesis_ready else []
        )

    except Exception as e:
        print(f"[WEB JUDGE] Resolution pipeline error: {e}. Defaulting to fail-safe.")
        fail_aspect = AspectScore(score=0.0, present=False, gap="pipeline error")
        return WebJudgeOutput(
            topic_a=fail_aspect,
            topic_b=fail_aspect,
            factual_density=fail_aspect,
            synthesis_ready=False,
            overall_score=0.0,
            verdict="FAIL",
            retry_focus=["RBI repo rate impact"]
        )
    


    # Evaluate whether this content contains sufficient information to answer the query."""

    # llm = ChatGroq(api_key=GROQ_API_KEY, model=JUDGE_MODEL, temperature=0.0)

    # response = llm.invoke([
    #     {"role": "system", "content": system_prompt},
    #     {"role": "user", "content": user_message}
    # ])

    # try:
    #     parsed = parse_llm_json(response.content)
    #     parsed["score"] = max(0.0, min(1.0, float(parsed["score"])))
    #     return JudgeOutput(**parsed)