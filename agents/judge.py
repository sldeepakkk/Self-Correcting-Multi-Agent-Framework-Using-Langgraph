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
This is a COMPOUND query connecting two distinct topics.
Your job: identify what the TWO topics actually are from the query itself,
then evaluate whether each topic is covered.

Common compound query types and how to assign topics:
- COMPARISON (e.g. "Compare TCS and Infosys"): topic_a = first entity, topic_b = second entity
- CAUSAL (e.g. "How does X affect Y"): topic_a = the cause/event, topic_b = the affected asset/sector
- MACRO-TO-EQUITY (e.g. "RBI cuts → banking stocks"): topic_a = macro event, topic_b = equity impact

Evaluate topic_a and topic_b based on what the QUERY is actually asking about.
Do NOT default to banking or index terms unless the query explicitly involves banking.
The two topics must be derived from the query text, not from examples.

Evaluate them SEPARATELY — they may be covered by different parts of the content
without any single paragraph explicitly connecting them. That is acceptable.
The generator will synthesize the connection."""
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

ASPECT 2 — topic_b (Secondary Subject Coverage):
For compound queries: identify topic_b from the query type:
  - COMPARISON query ("compare X and Y", "X vs Y"): topic_b = the second entity being compared
  - CAUSAL query ("how does X affect Y"): topic_b = the affected asset, sector, or metric
  - MACRO query ("X impact on NSE"): topic_b = the equity or sector reaction

Do NOT default to banking terms (Bank Nifty, SBI, HDFC) unless the query explicitly
names these entities. Derive topic_b from the query text only.

For non-compound queries: enforce score=1.0, present=true, gap=""
score: 0.0-0.3 absent, 0.4-0.6 partially present, 0.7-1.0 fully present
present: true if score >= 0.5

ASPECT 3 — factual_density (Quantitative Data Presence):
Are there numerical values, percentages (%), basis points (bps), price changes, or dates?
score: 0.0-0.3 no numbers/narrative only, 0.4-0.6 few figures, 0.7-1.0 data rich
present: true if score >= 0.4

RETRY FOCUS RULES (CRITICAL):
If any aspect above is NOT present, generate 1 to 3 targeted search queries
to fill exactly the missing aspect.
- Derive retry queries from the QUERY TEXT and the specific gap identified above
- NEVER use generic financial terms unless the query explicitly mentions those entities
- Make queries concrete and domain-specific to what the query actually asks about
- Format: short atomic phrases (2-4 words maximum per phrase)
- Examples of good retry focus: "tcs operating margins 2026", "infosys analyst targets"
- Examples of bad retry focus: "bank nifty reaction", "statistical significance stock price"
- If everything is present, return an empty list [].

Respond ONLY with valid JSON — no preamble, no markdown wrapper codeblocks:
{{
  "topic_a": {{"score": 0.0, "present": false, "gap": "short gap label from query terms"}},
  "topic_b": {{"score": 0.0, "present": false, "gap": "short gap label from query terms"}},
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
            retry_focus=["missing financial data"]
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