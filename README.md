# Self-Correcting Reasoning Agent

> A modular agentic AI framework for evidence-grounded reasoning using adaptive retrieval, self-critique, iterative revision, and long-term learning.

Rather than relying on a single LLM response, this framework decomposes complex problems into specialized reasoning stages. It retrieves evidence, validates information, critiques its own conclusions, revises weak arguments, and learns reusable reasoning strategies across executions.

---

# Overview

Traditional LLM applications typically generate a response in a single pass.

This framework instead treats reasoning as an iterative process by combining multiple specialized agents that collaboratively:

- Plan complex queries
- Retrieve supporting evidence
- Validate evidence quality
- Generate an initial response
- Critique reasoning quality
- Revise unsupported conclusions
- Learn reusable reasoning patterns

The objective is not simply to generate answers, but to improve the reasoning process itself.

---

# System Architecture

```text
                                          ┌─────────────────────────┐
                                          │       User Query        │
                                          └────────────┬────────────┘
                                                       │
                                                       ▼
                                          ┌─────────────────────────┐
                                          │     Planner Agent       │
                                          │  Query Decomposition    │
                                          └────────────┬────────────┘
                                                       │
                                                       ▼
                                            ◇ Retrieval Strategy? ◇
                                             /                  \
                                            /                    \
                                      Web-first               Vector-first
                                           │                       │
                                           │                       ▼
                                           │         ┌────────────────────────┐
                                           │         │   Vector Retrieval      │
                                           │         └──────────┬─────────────┘
                                           │                    │
                                           │                    ▼
                                           │         ◇ Fast Retrieval Filter? ◇
                                           │              /               \
                                           │           Pass               Fail
                                           │             │                 │
                                           │             ▼                 ▼
                                           │     ┌────────────────┐   ┌────────────────────┐
                                           │     │ Retrieval Judge │   │ CRAG Web Search    │
                                           │     └───────┬────────┘   └──────────┬─────────┘
                                           │             │                       │
                                           │      Pass   │   Fail                │
                                           │             ▼                       │
                                           └──────────►┌─────────────────────────┐
                                                       │   CRAG Web Search       │
                                                       └──────────┬──────────────┘
                                                                  │
                                                                  ▼
                                                ┌────────────────────────────────┐
                                                │ Evidence Refinement & Validation│
                                                └──────────────┬─────────────────┘
                                                               │
                                                               ▼
                                                  ┌────────────────────────────┐
                                                  │ Evidence Quality Judge      │
                                                  └─────────────┬──────────────┘
                                                                │
                                                 Pass           │           Retry
                                                   │            │
                                                   ▼            ▼
                                        ┌────────────────┐   ┌────────────────────┐
                                        │ Generator Agent│◄──│ CRAG Retry Search  │
                                        └───────┬────────┘   │   (max 1 retry)     │
                                                │            └────────────────────┘
                                                ▼
                                   ┌────────────────────────────────┐
                                   │      Reasoning Critic          │
                                   └───────────────┬────────────────┘
                                                   │
                          ┌────────────────────────┼────────────────────────┐
                          │                        │                        │
                          ▼                        ▼                        ▼
                  Accept Response       Revise Existing Answer    Retrieve More Evidence
                          │                        │                        │
                          │                        ▼                        ▼
                          │              ┌────────────────┐      ┌────────────────────┐
                          │              │ Generator      │      │ Targeted Web Search│
                          │              │ Revision       │      └─────────┬──────────┘
                          │              └────────┬───────┘                │
                          │                       │                        │
                          └───────────────────────┴─────────────┐          │
                                                               ▼          │
                                                     ┌────────────────────┐
                                                     │ Reasoning Critic   │
                                                     │   (max 1 loop)     │
                                                     └─────────┬──────────┘
                                                               │
                                                               ▼
                                            ┌────────────────────────────────┐
                                            │ Reflection & Episodic Memory   │
                                            └──────────────┬─────────────────┘
                                                           │
                                                           ▼
                                              ┌─────────────────────────┐
                                              │     Final Response      │
                                              └─────────────────────────┘
```

---

# Core Components

### Planner

Decomposes complex queries into targeted reasoning tasks.

### Adaptive Retrieval

Routes requests between vector retrieval and live web search depending on the information required.

### Retrieval Validation

Evaluates retrieval quality before allowing generation.

### Corrective Retrieval (CRAG)

Performs iterative web retrieval when the initial evidence is insufficient.

### Generator

Synthesizes a structured response using only validated evidence.

### Reasoning Critic

Evaluates generated responses for:

- Unsupported claims
- Incorrect assumptions
- Missing evidence
- Overconfidence
- Reasoning consistency

The critic can either accept the response, request targeted evidence, or trigger a revision.

### Reflection & Episodic Memory

Stores reusable reasoning lessons that influence future executions.

---

# Reasoning Pipeline

1. Query decomposition
2. Adaptive retrieval
3. Retrieval validation
4. Corrective retrieval
5. Evidence refinement
6. Response generation
7. Reasoning critique
8. Iterative revision
9. Reflection
10. Episodic memory update

---

# Design Principles

- Adaptive retrieval over static retrieval
- Evidence before generation
- Every answer critiques itself
- Iterative reasoning instead of one-shot prompting
- Long-term learning through reflection

---

# Tech Stack

**Agent Orchestration**

- LangGraph
- LangChain

**Language Models**

- Llama 3.3 70B
- Llama 3.1 8B
- Gemini 2.5 Flash

**Retrieval**

- FAISS
- Sentence Transformers
- Tavily Search
- CRAG

**Interface**

- Streamlit

---

# Current Capabilities

- Multi-agent reasoning
- Multi-hop question decomposition
- Adaptive retrieval
- Evidence-grounded synthesis
- Self-correcting generation
- Critique-driven revision
- Execution tracing
- Long-term learning through episodic memory

The current implementation demonstrates these capabilities using financial reasoning tasks, but the underlying architecture is domain-agnostic.

---

# Why This Project?

This project explores an alternative to one-shot prompting by treating reasoning as an iterative process.

Instead of generating a single response, multiple specialized agents collaborate to retrieve evidence, validate information, critique reasoning, revise conclusions, and learn from successful executions before producing the final answer.
