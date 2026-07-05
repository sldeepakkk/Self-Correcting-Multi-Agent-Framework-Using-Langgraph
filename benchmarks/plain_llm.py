"""
Plain LLM baseline for head-to-head comparison.
Runs the same queries with zero context augmentation — no retrieval,
no cache, no judge. Measures what the model knows from training alone.

Uses the same provider/model as the framework via llm_factory so the
comparison is provider-consistent. The judge also uses the same model.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.llm_factory import get_llm
from utils.llm_json import invoke_with_retry
from config import GENERATOR_MODEL, JUDGE_MODEL
import time


def run_plain_llm(query: str) -> dict:
    """
    Runs the query through the configured LLM with no context augmentation.
    Baseline: what the model knows from training data alone.
    """
    start = time.time()

    llm = get_llm(GENERATOR_MODEL, temperature=0.2)

    system_prompt = """You are a financial research analyst specializing in NSE stocks.
Answer the query as completely as possible from your training knowledge.
Structure your response with: Executive Summary, Key Financials, Analyst View, Verdict.
If you don't know specific figures, say so clearly."""

    try:
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ])
        content = response.content.strip()
    except Exception as e:
        print(f"[PLAIN LLM] Error: {e}")
        content = ""

    latency_ms = int((time.time() - start) * 1000)

    return {
        "response": content,
        "latency_ms": latency_ms
    }


def judge_response(
    query: str,
    response: str,
    source_label: str
) -> dict:
    """
    Scores a response 0-10 on three axes using the configured judge model.
    Same judge, same model for both framework and plain LLM — fair comparison.
    """
    llm = get_llm(JUDGE_MODEL, temperature=0.0)

    system_prompt = """You are an objective evaluator of financial research responses.
Score the response on three axes, each 0-10:

factual_grounding: Does it cite specific figures, dates, or sources?
                   10 = precise figures with clear sourcing
                   5  = some figures, some vague claims
                   0  = entirely generic or speculative

relevance: Does it directly answer the query asked?
           10 = directly and completely answers
           5  = partially answers with drift
           0  = off-topic or tangential

confidence_calibration: Does the response accurately express uncertainty?
                        10 = claims match actual certainty, admits unknowns clearly
                        5  = mixed, some overclaiming
                        0  = confidently wrong or completely hedged when it shouldn't be

Respond ONLY with valid JSON:
{
  "factual_grounding": 0,
  "relevance": 0,
  "confidence_calibration": 0,
  "overall": 0,
  "one_line_reason": "..."
}
overall = average of the three scores. No preamble."""

    user_message = f"""Query: {query}

Response to evaluate ({source_label}):
{response[:3000]}

Score this response."""

    try:
        scores = invoke_with_retry(llm, [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])
        for key in ["factual_grounding", "relevance",
                    "confidence_calibration", "overall"]:
            if key in scores:
                scores[key] = max(0, min(10, float(scores[key])))
        return scores
    except Exception as e:
        print(f"[JUDGE RESPONSE] Error: {e}")
        return {
            "factual_grounding": 0.0,
            "relevance": 0.0,
            "confidence_calibration": 0.0,
            "overall": 0.0,
            "one_line_reason": "parse error"
        }