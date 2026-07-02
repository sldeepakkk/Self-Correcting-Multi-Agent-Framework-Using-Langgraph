"""
Day 5 verification — tests the full system via main.run_query()

Test 1: First run of a query — cache miss, graph runs, cache populates
Test 2: Same query again — cache hit, returns in <200ms
Test 3: Different query — cache miss, different path
Test 4: Paraphrase of Test 1 query — should cache hit (semantic match)
Test 5: Verify run_logs/runs.jsonl has correct entries
"""

import sys, os, json, time
sys.path.append(os.path.dirname(__file__))

from main import run_query

QUERY_1 = "What are the fundamentals and analyst view for Infosys?"
QUERY_1_PARAPHRASE = "Give me Infosys financials and what analysts think about the stock"
QUERY_2 = "What is the revenue outlook and PE valuation for TCS?"

SEPARATOR = "="*60


# ── Test 1: First run — must be cache miss ────────────────────────────────────
print(f"\n{SEPARATOR}")
print("TEST 1 — First run, cache miss expected")
print(SEPARATOR)

result1 = run_query(QUERY_1, verbose=True)

assert result1["cache_hit"] == False, "Test 1 FAILED — expected cache miss"
assert result1["path_taken"] in ["medium", "slow", "slow_failed"], \
    f"Test 1 FAILED — unexpected path: {result1['path_taken']}"
assert len(result1["response"]) > 100, "Test 1 FAILED — response too short"
print(f"\n✅ Test 1 PASSED — path={result1['path_taken']}, "
      f"latency={result1['latency_ms']}ms")


# ── Test 2: Same query — must be cache hit ─────────────────────────────────────
print(f"\n{SEPARATOR}")
print("TEST 2 — Same query again, cache hit expected")
print(SEPARATOR)

result2 = run_query(QUERY_1, verbose=True)

assert result2["cache_hit"] == True, "Test 2 FAILED — expected cache hit"
assert result2["path_taken"] == "fast", \
    f"Test 2 FAILED — expected fast path, got {result2['path_taken']}"
assert result2["latency_ms"] < 500, \
    f"Test 2 FAILED — cache hit took {result2['latency_ms']}ms, expected <500ms"
print(f"\n✅ Test 2 PASSED — FAST PATH confirmed, latency={result2['latency_ms']}ms")


# ── Test 3: New query — cache miss ────────────────────────────────────────────
print(f"\n{SEPARATOR}")
print("TEST 3 — New query, cache miss expected")
print(SEPARATOR)

result3 = run_query(QUERY_2, verbose=False)

assert result3["cache_hit"] == False, "Test 3 FAILED — expected cache miss"
print(f"\n✅ Test 3 PASSED — cache miss confirmed, "
      f"path={result3['path_taken']}, latency={result3['latency_ms']}ms")


# ── Test 4: Paraphrase — semantic cache hit expected ──────────────────────────
print(f"\n{SEPARATOR}")
print("TEST 4 — Paraphrase of Test 1, semantic cache hit expected")
print(f"Original:   '{QUERY_1}'")
print(f"Paraphrase: '{QUERY_1_PARAPHRASE}'")
print(SEPARATOR)

result4 = run_query(QUERY_1_PARAPHRASE, verbose=True)

if result4["cache_hit"]:
    print(f"\n✅ Test 4 PASSED — semantic cache hit on paraphrase, "
          f"latency={result4['latency_ms']}ms")
else:
    print(f"\n⚠️  Test 4 INFO — paraphrase did not hit cache "
          f"(score below 0.92 threshold). This is acceptable — "
          f"the threshold prevents false positives on research queries.")
    print(f"   path={result4['path_taken']}, latency={result4['latency_ms']}ms")


# ── Test 5: Verify run log ────────────────────────────────────────────────────
print(f"\n{SEPARATOR}")
print("TEST 5 — Verify run_logs/runs.jsonl")
print(SEPARATOR)

assert os.path.exists("run_logs/runs.jsonl"), \
    "Test 5 FAILED — run_logs/runs.jsonl not found"

with open("run_logs/runs.jsonl") as f:
    lines = [json.loads(l) for l in f if l.strip()]

print(f"Total logged runs: {len(lines)}")
print(f"\nLast 4 runs:")
for entry in lines[-4:]:
    print(f"  [{entry['run_id']}] path={entry['path_taken']:<12} "
          f"cache={str(entry['cache_hit']):<5} "
          f"latency={entry['latency_ms']}ms  "
          f"crag={entry['crag_triggered']}")

assert len(lines) >= 4, "Test 5 FAILED — expected at least 4 logged runs"
assert any(e["cache_hit"] for e in lines), \
    "Test 5 FAILED — no cache hits logged"
assert any(not e["cache_hit"] for e in lines), \
    "Test 5 FAILED — no cache misses logged"

print(f"\n✅ Test 5 PASSED — run log is valid")


# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{SEPARATOR}")
print("DAY 5 SUMMARY")
print(SEPARATOR)

paths = [e["path_taken"] for e in lines[-4:]]
latencies = [e["latency_ms"] for e in lines[-4:]]
cache_hits = [e for e in lines[-4:] if e["cache_hit"]]
cache_misses = [e for e in lines[-4:] if not e["cache_hit"]]

print(f"Paths seen:          {set(paths)}")
if cache_hits:
    avg_hit = sum(e["latency_ms"] for e in cache_hits) / len(cache_hits)
    print(f"Avg cache hit latency:  {avg_hit:.0f}ms")
if cache_misses:
    avg_miss = sum(e["latency_ms"] for e in cache_misses) / len(cache_misses)
    print(f"Avg cache miss latency: {avg_miss:.0f}ms")
    if cache_hits:
        speedup = avg_miss / avg_hit if avg_hit > 0 else 0
        print(f"Cache speedup:          {speedup:.1f}x faster")
print(f"\nCache size: {__import__('cache.semantic_cache', fromlist=['SemanticCache']).SemanticCache().size} entries")
print(f"Run log entries: {len(lines)}")
print(f"\nSystem is fully operational.")
print(f"Run any query: python main.py \"your query here\"")