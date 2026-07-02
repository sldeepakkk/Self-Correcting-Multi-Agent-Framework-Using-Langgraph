"""
Run once: python data/nse_docs/seed_macro_data.py

Seeds the vector store with macro/policy content (RBI, budget, trade policy,
sector outlook) so common macro queries don't need a CRAG cycle every time.

Reuses the existing search_web() + knowledge_refine() pipeline rather than
hand-writing stale facts — this content should be re-run periodically since
macro facts (rates, policy) change faster than company fundamentals.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from retrieval.vector_store import VectorStore
from retrieval.web_search import search_web, knowledge_refine
from datetime import datetime, timezone

MACRO_TOPICS = [
    ("RBI repo rate decision latest monetary policy", "macro_rbi_rates"),
    ("India US trade deal impact IT sector", "macro_trade_policy"),
    ("Nifty 50 valuation market outlook analyst view", "macro_nifty_valuation"),
    ("India union budget defence sector allocation", "macro_budget_defence"),
    ("crude oil price impact Indian energy stocks", "macro_oil_energy"),
    ("India GDP growth forecast economic outlook", "macro_gdp_growth"),
    ("RBI inflation outlook CPI India", "macro_inflation"),
    ("NSE small cap mid cap market trend", "macro_smallcap_trend"),
]


def seed_macro_documents():
    store = VectorStore()
    timestamp = datetime.now(timezone.utc).isoformat()

    new_docs = []
    for topic, category in MACRO_TOPICS:
        print(f"\n[MACRO SEED] Fetching: {topic}")
        raw_results = search_web([topic], max_results_per_query=5)

        if not raw_results:
            print(f"  → No results found, skipping")
            continue

        refined, success = knowledge_refine(
            query=topic,
            sub_queries=[topic],
            raw_results=raw_results
        )

        if not success:
            print(f"  → Refinement failed, skipping")
            continue

        new_docs.append({
            "content": refined,
            "source": f"tavily_macro_seed/{category}",
            "ticker": "MACRO",
            "category": category,
            "seeded_at": timestamp
        })
        print(f"  → Seeded {len(refined)} chars under category '{category}'")

    if new_docs:
        store.add_documents(new_docs)
        print(f"\n[MACRO SEED COMPLETE] {len(new_docs)} macro documents added")
        print(f"Total vector store size: {store.size}")
        print(f"\nNote: macro content seeded at {timestamp}. "
              f"Re-run this script periodically — unlike company fundamentals, "
              f"policy/rate data goes stale faster.")
    else:
        print("\n[MACRO SEED] No documents were successfully seeded")


if __name__ == "__main__":
    seed_macro_documents()