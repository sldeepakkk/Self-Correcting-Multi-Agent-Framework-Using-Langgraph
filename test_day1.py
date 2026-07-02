from config import SEMANTIC_CACHE_THRESHOLD, GENERATOR_MODEL, GROQ_API_KEY
from graph.state import AgentState
from cache.semantic_cache import SemanticCache

# 1. Config check
print(f"Cache threshold: {SEMANTIC_CACHE_THRESHOLD}")
print(f"Generator model: {GENERATOR_MODEL}")
print(f"Groq key loaded: {'yes' if GROQ_API_KEY else 'NO - CHECK .env'}")

# 2. State check — just instantiate a minimal one
state: AgentState = {
    "query": "What is the outlook for Infosys Q4?",
    "sub_queries": [],
    "retrieved_docs": [],
    "gate1_passed": False,
    "judge_score": 0.0,
    "judge_reasoning": "",
    "crag_triggered": False,
    "web_search_results": [],
    "recovery_succeeded": False,
    "final_context": "",
    "response": "",
    "path_taken": "",
    "trace": [],
    "episodic_lessons": [],
    "cache_hit": False
}
print(f"State keys: {list(state.keys())}")

# 3. Cache check
# 3. Cache check
cache = SemanticCache()

# Add a query
cache.add("What is Infosys Q4 revenue?", "Infosys Q4 revenue was X.", "medium")

# Test 1 — near identical, SHOULD hit
result1 = cache.get("What is the Infosys Q4 revenue?")
print(f"Near-identical hit: {result1 is not None}")   # should be True

# Test 2 — genuine paraphrase, borderline
result2 = cache.get("Infosys earnings last quarter")
print(f"Paraphrase hit: {result2 is not None}")        # may be False — that's fine

# Test 3 — unrelated, SHOULD miss
result3 = cache.get("What is the weather in Chennai?")
print(f"Unrelated miss: {result3 is None}")            # should be True