# Self-Correcting Reasoning Agent

> A modular agentic AI framework for evidence-grounded reasoning using adaptive retrieval, self-critique, iterative revision, and long-term learning.

Rather than relying on a single LLM response, this framework decomposes complex problems into specialized reasoning stages. It retrieves evidence, validates information, critiques its own conclusions, revises weak arguments, and learns reusable reasoning strategies across executions.

---

## Overview

Traditional LLM applications typically generate a response in a single pass.

This framework instead treats reasoning as an iterative process by combining multiple specialized agents that collaboratively:

- **Plan complex queries** into structured sub-tasks
- **Validate the query itself** for factual premise errors before retrieval
- **Retrieve supporting evidence** via hybrid vector search and live web search
- **Generate initial responses** grounded in empirical evidence
- **Critique reasoning quality** with a dedicated thesis acceptance checker
- **Revise unsupported conclusions** through iterative refinement
- **Learn reusable reasoning patterns** stored in episodic memory

The objective is not simply to generate answers, but to improve the reasoning process itself.

---

## System Architecture

```text
┌─────────┐
│  start  │
└────┬────┘
     ▼
┌─────────┐
│ planner │
└────┬────┘
     ▼
┌────────────────┐
│  premise_check │
└────────┬───────┘
         ▼
┌───────────┐
│ retriever │
└─────┬─────┘
      ▼
┌───────────┐
│ generator │
└─────┬─────┘
      │ solid
      ▼
┌─────────────────────┐
│    thesis_critic     │◀─────────────────────┐
└──┬────────┬──────┬───┘                       │
   │dashed  │dashed│dashed "reasoning_check"   │
   ▼        ▼      ▼                           │
┌──────┐ ┌───────┐ ┌────────────────────┐      │
│evid.  │ │revise │ │reasoning_reflector │     │
│search │ │       │ │                    │     │
└───┬───┘ └───┬───┘ └─────────┬──────────┘     │
    │solid    │solid          │solid           │
    └────┬────┘               ▼                │
         │                ┌───────┐            │
         └────────────────│  end  │            │
                          └───────┘            │
                               ▲               │
                               └───────────────┘
```

---

## Core Components

- **Planner Agent (`agents/planner.py`)**: Decomposes complex queries into 2–3 targeted sub-queries. Detects compound queries (those connecting two distinct topics) and generates a bridging sub-query that explicitly names the relationship. Loads episodic lessons as priors.
- **Premise Check (`agents/critic.py`)**: A fast, focused pre-retrieval check for institutional or personnel misattribution in the query itself (e.g., wrong central bank, wrong governor). Runs before any retrieval to avoid propagating false premises into the evidence search.
- **Hybrid Retriever (`retrieval/`)**: Searches a local FAISS vector store first, then augments with live Tavily web search when local context is sparse, lacks quantitative data, or scores below threshold. Sub-queries are classified (macro vs. ticker) to apply the correct search anchor.
- **Generator Agent (`agents/generator.py`)**: Synthesizes responses in whatever structure best serves the question — not a fixed template. Adapts output based on evidence confidence (low/medium/high). Loads episodic lessons as stylistic priors.
- **Thesis Critic (`agents/critic.py`)**: An acceptance checker, not a flaw-hunter. Default assumption: the response is acceptable. Rejects only against seven named bars (fabrication, uncalibrated certainty, contradiction, missing evidence, etc.). Outputs a structured `ThesisCritique`.
- **Evidence Search (`retrieval/crag.py`)**: Critic-directed targeted web search. Only triggered when the critic identifies a specific, searchable missing fact (`needs_evidence` field).
- **Revision Agent (`agents/generator.py`)**: Rewrites the response addressing every flagged issue. Uses boosting-style targeting — focuses the revision instruction on the single weakest critique dimension.
- **Reasoning Reflector (`agents/reasoning_reflector.py`)**: Distills a resolved defect into a reusable abstract lesson (no proper nouns, no specific figures). Only fires when a genuine defect-and-recovery cycle occurred.
- **Episodic Memory (`memory/episodic.py`)**: SQLite-backed store. Lessons are written with confidence gating (≥ 0.75 = active, below = quarantined) and cosine-similarity deduplication (≥ 0.9 = skip). Active lessons are injected as priors into the Planner, Premise Checker, and Critic on every subsequent run.
- **Semantic Cache (`cache/semantic_cache.py`)**: FAISS-powered query cache (cosine similarity ≥ 0.92 threshold). Serves instant responses for semantically similar queries. Low-confidence answers are never cached.

---

## Repository Structure

```text
├── agents/                      # Multi-agent implementations
│   ├── critic.py                # Premise check, thesis critique & revision instruction builder
│   ├── generator.py             # Response generation & iterative revision
│   ├── planner.py               # Multi-hop query decomposition
│   └── reasoning_reflector.py  # Lesson extraction from resolved defects
├── graph/                       # LangGraph workflow orchestration
│   ├── builder.py               # StateGraph assembly & compilation
│   ├── edges.py                 # Conditional routing logic (route_after_thesis_critique)
│   ├── nodes.py                 # Node execution functions
│   └── state.py                 # Shared AgentState TypedDict
├── retrieval/                   # Hybrid retrieval subsystem
│   ├── crag.py                  # run_evidence_search — single ungated web search
│   ├── vector_store.py          # FAISS local vector store & embeddings
│   └── web_search.py            # Tavily parallel search & LLM-based knowledge refinement
├── memory/                      # Long-term learning & episodic store
│   ├── episodic.py              # SQLite episodic memory engine & cosine deduplication
│   └── MEMORY_LOG.md            # Human-readable log of every lesson written
├── cache/                       # Performance layer
│   └── semantic_cache.py        # FAISS-powered semantic query cache
├── data/                        # Dataset & vector store seeders
│   └── nse_docs/                # Seeding scripts (yfinance financial metrics & macro)
├── scripts/                     # Utility & evaluation scripts
│   └── run_benchmark.py         # 3-query deep comparative evaluation script
├── utils/                       # Shared utilities
│   ├── llm_factory.py           # Multi-provider LLM factory (Groq, Gemini)
│   └── llm_json.py              # Robust JSON parsing with retry & rate-limit backoff
├── app.py                       # Streamlit interactive web application
├── main.py                      # CLI & Python API entry point (run_query)
├── config.py                    # Centralized configuration & model selection
└── requirements.txt             # Project dependencies
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Groq API Key (default) or Google Gemini API Key
- Tavily API Key (for web search)

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/your-username/nse-research-agent.git
cd nse-research-agent

# Create and activate virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and provide your API keys:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
GEMINI_API_KEY=...
```

### 5. Seed Vector Store (Optional but Recommended)
Populate the local FAISS vector store with initial NSE company fundamentals:
```bash
python data/nse_docs/seed_data.py
python data/nse_docs/seed_macro_data.py
```

### 6. Run the Agent

**Via Command Line (CLI):**
```bash
python main.py "What are the fundamentals for Infosys?"
```

**Via Streamlit UI:**
```bash
streamlit run app.py
```

---

## Tech Stack

- **Agent Orchestration**: LangGraph, LangChain
- **Language Models**: Llama 3.3 70B, Llama 3.1 8B, Gemini 2.5 Flash (configurable via `config.py`)
- **Embeddings & Vector Store**: FAISS, Sentence Transformers (`all-MiniLM-L6-v2`)
- **Live Search & Market Data**: Tavily Search, yfinance
- **Web UI**: Streamlit
- **Long-Term Memory**: SQLite (episodic memory with confidence gating & cosine-similarity deduplication)
