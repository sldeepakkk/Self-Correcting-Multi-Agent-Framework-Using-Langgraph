import json
import time
import random

def parse_llm_json(raw: str) -> dict:
    """Strips markdown fences and parses JSON. Raises on failure."""
    raw = raw.strip()
    if raw.startswith("```"):
        # Improved parsing for multiple code block styles
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)

def invoke_with_retry(llm, messages: list[dict], max_retries: int = 4) -> dict:
    """
    Unified retry wrapper: Handles both JSON parsing errors AND Groq Rate Limits (429).
    Uses exponential backoff with jitter to ensure the token bucket refills.
    """
    last_error = None
    delay = 1.0  # Initial backoff in seconds

    for attempt in range(max_retries + 1):
        try:
            response = llm.invoke(messages)
            return parse_llm_json(response.content)
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Case A: Groq Rate Limit (429)
            if "rate limit" in error_str or "429" in error_str:
                last_error = e
                # Add jitter (0.1 to 0.5s) to prevent sync-retry collisions
                sleep_time = delay + random.uniform(0.1, 0.5)
                print(f"[RATE LIMIT] 429 hit. Backing off for {sleep_time:.2f}s (Attempt {attempt+1}/{max_retries})")
                time.sleep(sleep_time)
                delay *= 2  # Exponential growth
                continue
            
            # Case B: JSON/Parsing Error
            elif isinstance(e, (json.JSONDecodeError, IndexError, KeyError)):
                last_error = e
                if attempt < max_retries:
                    print(f"[JSON RETRY] Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(1.0)
                    continue
            
            # Case C: Unknown/Fatal Error (e.g., API key expiry)
            else:
                raise e

    print(f"[FATAL] Max retries exceeded. Last error: {last_error}")
    raise last_error