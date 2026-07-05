"""
NSE Research Agent — Full Benchmark Suite
==========================================
Runs 20 diverse NSE queries across:
  A) Plain LLM (no context, no cache, no judge)
  B) Our Framework (full pipeline)

Measures and plots:
  1. Head-to-head judge scores (framework vs plain LLM)
  2. Cache hit rate warming curve over 20 runs
  3. Latency distribution (fast / medium / slow paths)
  4. Path distribution + CRAG trigger rate
  5. Judge score distribution across runs

Outputs to benchmarks/results/
Run: python benchmarks/run_benchmark.py
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import time
import matplotlib
matplotlib.use("Agg")       # no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from main import run_query
from benchmarks.plain_llm import run_plain_llm, judge_response

# ── Query Set ─────────────────────────────────────────────────────────────────
# 20 queries: mix of ticker-specific (vector store covers),
# macro/current (CRAG should trigger), and repeats (cache should hit)

QUERIES = [
    "Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?",
    "What are the fundamentals and analyst view for Infosys?",
    "What are the latest RBI rate decisions and impact on banking stocks?",
    "Compare TCS and Infosys on growth, margins, and analyst sentiment, and identify which appears stronger today.",
    "What is the analyst consensus on Infosys and how strong are its key financial metrics?"


    # #10 queries to benchmark
    # "What are Infosys's fundamentals, valuation, and analyst sentiment, and how do they compare with its historical averages?",
    # "Compare Reliance Industries' valuation metrics and business segments to determine key investment drivers.",
    # "How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?",
    # "Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?",
    # "What are Infosys's fundamentals, valuation, and analyst sentiment, and how do they compare with its historical averages?",
    # "Summarize Infosys financial performance and what analysts currently think about the stock.",
    # "What is the analyst consensus on Infosys and how strong are its key financial metrics?",
    # "Compare TCS and Infosys on growth, margins, and analyst sentiment, and identify which appears stronger today.",
    # "How does the current energy market outlook affect IEX and related NSE energy companies?",
    # "Assuming India increases defence spending by 20% next year, which listed defence companies would benefit most and why?",

    # # Vector store coverage — medium path expected
    # "What are Infosys's fundamentals, valuation, and analyst sentiment, and how do they compare with its historical averages?",
    # "Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.",
    # "Compare Reliance Industries' valuation metrics and business segments to determine key investment drivers.",
    # "What are the strengths and risks of HDFC Bank based on fundamentals and analyst sentiment?",
    # "Compare Wipro and Infosys on profitability, growth, and analyst expectations.",

    # # Macro / current events — CRAG + web-first expected
    # "What are the latest RBI policy decisions and their impact on Indian banking stocks?",
    # "How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?",
    # "What is the current Nifty 50 valuation relative to historical averages, and what are analysts expecting next?",
    # "How are recent oil price movements affecting Reliance Industries and other energy-linked NSE stocks?",
    # "Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?",

    # # Repeat queries — cache hits expected after first run
    # "What are Infosys's fundamentals, valuation, and analyst sentiment, and how do they compare with its historical averages?",
    # "What are the latest RBI policy decisions and their impact on Indian banking stocks?",
    # "Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.",

    # # Paraphrases — semantic cache should catch these
    # "Summarize Infosys financial performance and what analysts currently think about the stock.",
    # "What is the analyst consensus on Infosys and how strong are its key financial metrics?",

    # # Mixed — partial vector store + CRAG coverage
    # "Compare TCS and Infosys on growth, margins, and analyst sentiment, and identify which appears stronger today.",
    # "How does the current energy market outlook affect IEX and related NSE energy companies?",
    # "Analyze BEL and Zen Technologies in the context of India's defence spending trends and future opportunities.",

    # # Edge cases
    # "Assuming India increases defence spending by 20% next year, which listed defence companies would benefit most and why?",
    # "Compare the likely winners and losers on NSE if RBI cuts rates twice over the next year.",
]

RESULTS_DIR = "benchmarks/results"
os.makedirs(RESULTS_DIR, exist_ok=True)


# ── Run Framework ─────────────────────────────────────────────────────────────

def run_all_framework(queries: list[str]) -> list[dict]:
    print("\n" + "="*60)
    print("PHASE 1 — Running all queries through framework")
    print("="*60)

    results = []
    for i, query in enumerate(queries):
        print(f"\n[{i+1}/{len(queries)}] {query[:70]}...")
        try:
            result = run_query(query, verbose=False)
            results.append(result)
            print(f"  → path={result['path_taken']}, "
                  f"cache={result['cache_hit']}, "
                  f"latency={result['latency_ms']}ms, "
                  f"crag={result['crag_triggered']}")
        except Exception as e:
            print(f"  → ERROR: {e}")
            results.append({
                "query": query,
                "path_taken": "error",
                "cache_hit": False,
                "latency_ms": 0,
                "crag_triggered": False,
                "recovery_succeeded": False,
                "judge_score": 0.0,
                "response": "",
                "lessons_applied": 0
            })
        time.sleep(0.5)     # rate limit buffer

    return results


# ── Run Plain LLM ─────────────────────────────────────────────────────────────

def run_all_plain(queries: list[str]) -> list[dict]:
    print("\n" + "="*60)
    print("PHASE 2 — Running queries through plain LLM (baseline)")
    print("="*60)

    # Only run first 10 unique queries for comparison
    # (no point running repeats/paraphrases through plain LLM)
    unique_queries = queries[:5]
    results = []

    for i, query in enumerate(unique_queries):
        print(f"\n[{i+1}/{len(unique_queries)}] {query[:70]}...")
        try:
            result = run_plain_llm(query)
            result["query"] = query
            results.append(result)
            print(f"  → latency={result['latency_ms']}ms, "
                  f"response={len(result['response'])} chars")
        except Exception as e:
            print(f"  → ERROR: {e}")
            results.append({
                "query": query,
                "response": "",
                "latency_ms": 0
            })
        time.sleep(0.5)

    return results


# ── Head-to-Head Judge Scoring ────────────────────────────────────────────────

def run_judge_comparison(
    framework_results: list[dict],
    plain_results: list[dict]
) -> list[dict]:
    print("\n" + "="*60)
    print("PHASE 3 — Judge scoring head-to-head (first 10 queries)")
    print("="*60)

    comparisons = []
    for i in range(min(10, len(plain_results))):
        query = QUERIES[i]
        fw_response = framework_results[i].get("response", "")
        pl_response = plain_results[i].get("response", "")

        if not fw_response or not pl_response:
            continue

        print(f"\n[{i+1}/10] Judging: {query[:60]}...")

        fw_scores = judge_response(query, fw_response, "framework")
        time.sleep(0.3)
        pl_scores = judge_response(query, pl_response, "plain_llm")
        time.sleep(0.3)

        comparisons.append({
            "query": query,
            "framework": fw_scores,
            "plain_llm": pl_scores,
            "framework_wins": fw_scores["overall"] > pl_scores["overall"]
        })

        print(f"  Framework: {fw_scores['overall']:.1f}/10 — "
              f"{fw_scores.get('one_line_reason', '')[:60]}")
        print(f"  Plain LLM: {pl_scores['overall']:.1f}/10 — "
              f"{pl_scores.get('one_line_reason', '')[:60]}")

    return comparisons


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_head_to_head(comparisons: list[dict]) -> None:
    """Bar chart: framework vs plain LLM across three scoring axes."""
    if not comparisons:
        return

    axes = ["factual_grounding", "relevance", "confidence_calibration", "overall"]
    labels = ["Factual\nGrounding", "Relevance", "Confidence\nCalibration", "Overall"]

    fw_means = [
        np.mean([c["framework"].get(a, 0) for c in comparisons])
        for a in axes
    ]
    pl_means = [
        np.mean([c["plain_llm"].get(a, 0) for c in comparisons])
        for a in axes
    ]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, fw_means, width,
                   label="Framework (CRAG + Judge + Cache)",
                   color="#2563eb", alpha=0.85)
    bars2 = ax.bar(x + width/2, pl_means, width,
                   label="Plain LLM (no context)",
                   color="#dc2626", alpha=0.85)

    ax.set_ylim(0, 10)
    ax.set_ylabel("Judge Score (0–10)", fontsize=12)
    ax.set_title("Framework vs Plain LLM — Judge Evaluation\n(10 NSE Research Queries)",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(y=5, color="gray", linestyle="--", alpha=0.4, linewidth=1)

    # value labels on bars
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#2563eb")
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#dc2626")

    plt.tight_layout()
    path = f"{RESULTS_DIR}/01_head_to_head.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_cache_warming(framework_results: list[dict]) -> None:
    """Line chart: cumulative cache hit rate over 20 runs."""
    hits = [r["cache_hit"] for r in framework_results]
    cumulative_rate = []
    running_hits = 0

    for i, hit in enumerate(hits):
        if hit:
            running_hits += 1
        cumulative_rate.append((running_hits / (i + 1)) * 100)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(1, len(hits) + 1), cumulative_rate,
            color="#2563eb", linewidth=2.5, marker="o",
            markersize=5, label="Cache hit rate %")

    # Mark individual hits
    for i, hit in enumerate(hits):
        if hit:
            ax.axvline(x=i+1, color="#16a34a", alpha=0.2, linewidth=8)

    ax.set_xlabel("Run Number", fontsize=12)
    ax.set_ylabel("Cumulative Cache Hit Rate (%)", fontsize=12)
    ax.set_title("Semantic Cache Warming Curve\n"
                 "(green bands = cache hit runs)",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_xlim(1, len(hits))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    path = f"{RESULTS_DIR}/02_cache_warming.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_latency_distribution(framework_results: list[dict]) -> None:
    """Box plot + scatter: latency by path type."""
    path_latencies = {"fast": [], "medium": [], "slow": [], "slow_failed": []}

    for r in framework_results:
        path = r.get("path_taken", "medium")
        latency = r.get("latency_ms", 0)
        if path in path_latencies and latency > 0:
            path_latencies[path].append(latency)

    # Remove empty paths
    path_latencies = {k: v for k, v in path_latencies.items() if v}

    if not path_latencies:
        return

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {
        "fast": "#16a34a",
        "medium": "#2563eb",
        "slow": "#d97706",
        "slow_failed": "#dc2626"
    }

    positions = []
    labels = []
    data = []
    plot_colors = []

    for i, (path, latencies) in enumerate(path_latencies.items()):
        positions.append(i + 1)
        labels.append(f"{path}\n(n={len(latencies)})")
        data.append(latencies)
        plot_colors.append(colors.get(path, "#666"))

    bp = ax.boxplot(data, positions=positions, patch_artist=True,
                    widths=0.5, showfliers=True)

    for patch, color in zip(bp["boxes"], plot_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Overlay scatter points
    for i, (latencies, color) in enumerate(zip(data, plot_colors)):
        jitter = np.random.normal(0, 0.06, len(latencies))
        ax.scatter([positions[i] + j for j in jitter], latencies,
                   color=color, alpha=0.6, s=40, zorder=5)

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Latency (ms)", fontsize=12)
    ax.set_title("Latency Distribution by Execution Path",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path_out = f"{RESULTS_DIR}/03_latency_distribution.png"
    plt.savefig(path_out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path_out}")


def plot_path_distribution(framework_results: list[dict]) -> None:
    """Pie + bar: execution path breakdown and CRAG stats."""
    from collections import Counter

    paths = [r.get("path_taken", "medium") for r in framework_results]
    path_counts = Counter(paths)

    crag_total = sum(1 for r in framework_results if r.get("crag_triggered"))
    crag_recovered = sum(1 for r in framework_results
                         if r.get("crag_triggered") and r.get("recovery_succeeded"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Pie chart — path distribution
    colors_map = {
        "fast": "#16a34a",
        "medium": "#2563eb",
        "slow": "#d97706",
        "slow_failed": "#dc2626",
        "error": "#9ca3af"
    }
    pie_colors = [colors_map.get(p, "#666") for p in path_counts.keys()]

    wedges, texts, autotexts = ax1.pie(
        path_counts.values(),
        labels=[f"{k}\n({v} runs)" for k, v in path_counts.items()],
        colors=pie_colors,
        autopct="%1.0f%%",
        startangle=90,
        textprops={"fontsize": 10}
    )
    for at in autotexts:
        at.set_fontweight("bold")

    ax1.set_title("Execution Path Distribution\n(20 queries)",
                  fontsize=13, fontweight="bold")

    # Bar chart — CRAG stats
    crag_labels = ["Total Runs", "CRAG Triggered", "Recovery\nSucceeded"]
    crag_values = [len(framework_results), crag_total, crag_recovered]
    bar_colors = ["#2563eb", "#d97706", "#16a34a"]

    bars = ax2.bar(crag_labels, crag_values,
                   color=bar_colors, alpha=0.85, width=0.5)
    ax2.set_ylabel("Count", fontsize=12)
    ax2.set_title("CRAG Fallback Statistics",
                  fontsize=13, fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)

    for bar, val in zip(bars, crag_values):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.2,
                 str(val), ha="center", fontweight="bold", fontsize=12)

    plt.tight_layout()
    path_out = f"{RESULTS_DIR}/04_path_distribution.png"
    plt.savefig(path_out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path_out}")


# ── Summary JSON ──────────────────────────────────────────────────────────────

def build_summary(
    framework_results: list[dict],
    comparisons: list[dict]
) -> dict:
    """Builds the README benchmark table as a JSON dict."""
    from collections import Counter

    paths = Counter(r.get("path_taken", "medium") for r in framework_results)
    cache_hits = [r for r in framework_results if r.get("cache_hit")]
    cache_misses = [r for r in framework_results if not r.get("cache_hit")]
    crag_runs = [r for r in framework_results if r.get("crag_triggered")]
    crag_recovered = [r for r in crag_runs if r.get("recovery_succeeded")]

    avg_hit_latency = (
        int(np.mean([r["latency_ms"] for r in cache_hits]))
        if cache_hits else 0
    )
    avg_miss_latency = (
        int(np.mean([r["latency_ms"] for r in cache_misses]))
        if cache_misses else 0
    )
        # NEW — median alongside mean, less sensitive to outlier queries
    median_hit_latency = (
        int(np.median([r["latency_ms"] for r in cache_hits]))
        if cache_hits else 0
    )
    median_miss_latency = (
        int(np.median([r["latency_ms"] for r in cache_misses]))
        if cache_misses else 0
    )
    speedup = (
        round(avg_miss_latency / avg_hit_latency, 1)
        if avg_hit_latency > 0 else 0
    )

    fw_overall = np.mean([c["framework"]["overall"] for c in comparisons]) if comparisons else 0
    pl_overall = np.mean([c["plain_llm"]["overall"] for c in comparisons]) if comparisons else 0
    fw_factual = np.mean([c["framework"]["factual_grounding"] for c in comparisons]) if comparisons else 0
    pl_factual = np.mean([c["plain_llm"]["factual_grounding"] for c in comparisons]) if comparisons else 0

    summary = {
        "total_runs": len(framework_results),
        "path_distribution": dict(paths),
        "cache_hit_rate_pct": round(len(cache_hits) / len(framework_results) * 100, 1),
        "avg_cache_hit_latency_ms": avg_hit_latency,
        "avg_cache_miss_latency_ms": avg_miss_latency,
        "median_cache_hit_latency_ms": median_hit_latency,
        "median_cache_miss_latency_ms": median_miss_latency,
        "cache_speedup_x": speedup,
        "crag_trigger_rate_pct": round(len(crag_runs) / len(framework_results) * 100, 1),
        "crag_recovery_rate_pct": (
            round(len(crag_recovered) / len(crag_runs) * 100, 1)
            if crag_runs else 0
        ),
        "framework_avg_judge_score": round(fw_overall, 2),
        "plain_llm_avg_judge_score": round(pl_overall, 2),
        "framework_factual_grounding": round(fw_factual, 2),
        "plain_llm_factual_grounding": round(pl_factual, 2),
        "framework_wins_pct": round(
            sum(1 for c in comparisons if c["framework_wins"]) /
            len(comparisons) * 100, 1
        ) if comparisons else 0
    }

    path_out = f"{RESULTS_DIR}/summary.json"
    with open(path_out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[SUMMARY] Saved: {path_out}")

    return summary


def print_readme_table(summary: dict) -> None:
    """Prints the exact table to paste into README.md."""
    print(f"""
{'='*60}
README BENCHMARK TABLE
{'='*60}

| Metric | Value |
|--------|-------|
| Total runs | {summary['total_runs']} |
| Cache hit rate | {summary['cache_hit_rate_pct']}% |
| Avg cache hit latency | {summary['avg_cache_hit_latency_ms']}ms |
| Avg cache miss latency | {summary['avg_cache_miss_latency_ms']}ms |
| Cache speedup | {summary['cache_speedup_x']}x faster |
| CRAG trigger rate | {summary['crag_trigger_rate_pct']}% |
| CRAG recovery rate | {summary['crag_recovery_rate_pct']}% |
| Framework judge score | {summary['framework_avg_judge_score']}/10 |
| Plain LLM judge score | {summary['plain_llm_avg_judge_score']}/10 |
| Factual grounding (framework) | {summary['framework_factual_grounding']}/10 |
| Factual grounding (plain LLM) | {summary['plain_llm_factual_grounding']}/10 |
| Framework win rate | {summary['framework_wins_pct']}% of queries |
| Path distribution | {summary['path_distribution']} |
""")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nNSE Research Agent — Full Benchmark Suite")
    print("This will run 20 queries + baseline comparison.")
    print("Estimated time: 8-15 minutes (API calls + rate limits)\n")

    # Phase 1 — Framework
    framework_results = run_all_framework(QUERIES)

    # Phase 2 — Plain LLM baseline
    plain_results = run_all_plain(QUERIES)

    # Phase 3 — Judge comparison
    comparisons = run_judge_comparison(framework_results, plain_results)

    # Phase 4 — Plots
    print("\n" + "="*60)
    print("PHASE 4 — Generating plots")
    print("="*60)
    plot_head_to_head(comparisons)
    plot_cache_warming(framework_results)
    plot_latency_distribution(framework_results)
    plot_path_distribution(framework_results)

    # Phase 5 — Summary
    print("\n" + "="*60)
    print("PHASE 5 — Summary")
    print("="*60)
    summary = build_summary(framework_results, comparisons)
    print_readme_table(summary)

    print(f"\nAll outputs in: {RESULTS_DIR}/")
    print("01_head_to_head.png  — framework vs plain LLM")
    print("02_cache_warming.png — cache hit rate over runs")
    print("03_latency_distribution.png — latency by path")
    print("04_path_distribution.png — path breakdown + CRAG stats")
    print("summary.json — all numbers for README")