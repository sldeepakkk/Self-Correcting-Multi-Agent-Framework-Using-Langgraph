import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ── Provider Switch — change this one line only ──────────────────────────────
PROVIDER = "groq"          # "groq" or "gemini" or "mixed" (planner/judge/reflector = llama, generator = gemini)

# ── Models ────────────────────────────────────────────────────────────────────
if PROVIDER == "gemini":
    PLANNER_MODEL   = "gemini-2.5-flash"
    CRITIC_MODEL    = "gemini-2.5-flash-preview-04-17"
    JUDGE_MODEL     = "gemini-2.5-flash"
    REFLECTOR_MODEL = "gemini-2.5-flash"
    GENERATOR_MODEL = "gemini-2.5-flash"

elif PROVIDER == "mixed":
    PLANNER_MODEL   = "llama-3.3-70b-versatile"
    JUDGE_MODEL     = "llama-3.3-70b-versatile"
    CRITIC_MODEL    = "llama-3.1-8b-instant"
    REFLECTOR_MODEL = "llama-3.1-8b-instant"
    GENERATOR_MODEL = "gemini-2.5-flash" 
else:  # groq
    PLANNER_MODEL   = "llama-3.3-70b-versatile"
    JUDGE_MODEL     = "llama-3.1-8b-instant"
    CRITIC_MODEL    = "llama-3.1-8b-instant"
    REFLECTOR_MODEL = "llama-3.1-8b-instant"
    GENERATOR_MODEL = "llama-3.3-70b-versatile"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"    # always local, never changes

# --- Thresholds ---
SEMANTIC_CACHE_THRESHOLD = 0.92     # cosine similarity for cache hit
JUDGE_RELEVANCE_THRESHOLD = 0.6     # below this triggers CRAG fallback
REFLECTION_CONFIDENCE_MIN = 0.75    # below this quarantines the lesson

# --- Gate 1 Heuristics ---
GATE1_MIN_RESPONSE_LENGTH = 100          # chars — too short = suspicious
GATE1_UNCERTAINTY_MARKER_LIMIT = 3       # too many hedges = suspicious
GATE1_UNCERTAINTY_MARKERS = [
    "i think", "i believe", "i'm not sure", "approximately",
    "it may be", "it might be", "unclear", "i cannot confirm",
    "i don't know", "uncertain"
]

# --- Paths ---
CACHE_INDEX_PATH = "cache/cache.index"
CACHE_STORE_PATH = "cache/cache_store.json"
EPISODIC_MEMORY_DB = "memory/episodic.db"
MEMORY_LOG_PATH = "memory/MEMORY_LOG.md"
NSE_DOCS_PATH = "data/nse_docs/"
VECTOR_STORE_PATH = "data/vector_store.index"
VECTOR_STORE_DOCS_PATH = "data/vector_store_docs.json"
BENCHMARK_RESULTS_PATH = "benchmarks/results/"