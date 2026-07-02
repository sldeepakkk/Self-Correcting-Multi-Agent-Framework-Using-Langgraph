"""
Run once: python data/nse_docs/seed_data.py
Pulls real data from yfinance for key NSE tickers and seeds the vector store.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import yfinance as yf
from retrieval.vector_store import VectorStore


# NSE tickers — yfinance uses .NS suffix
TICKERS = [
    "INFY.NS",      # Infosys
    "TCS.NS",       # TCS
    "RELIANCE.NS",  # Reliance
    "HDFCBANK.NS",  # HDFC Bank
    "WIPRO.NS",     # Wipro
    "IEX.NS",       # Indian Energy Exchange
    "BEL.NS",       # Bharat Electronics
    "ZENT.NS",      # Zen Technologies
    "HCLTECH.NS",   # HCL Technologies
    "ICICIBANK.NS",   # ICICI Bank
    "AXISBANK.NS",    # Axis Bank  
    "HCLTECH.NS",    # HCL Technologies
    "TECHM.NS"       # Tech Mahindra
]


def build_document(ticker: str, info: dict, hist_summary: str) -> list[dict]:
    """Build document chunks from yfinance data."""
    documents = []
    name = info.get("longName", ticker)
    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")
    country = info.get("country", "India")
    market_cap = info.get("marketCap", "N/A")
    pe_ratio = info.get("trailingPE", "N/A")
    revenue = info.get("totalRevenue", "N/A")
    profit_margins = info.get("profitMargins", "N/A")
    week52_high = info.get("fiftyTwoWeekHigh", "N/A")
    week52_low = info.get("fiftyTwoWeekLow", "N/A")
    analyst_target = info.get("targetMeanPrice", "N/A")
    recommendation = info.get("recommendationKey", "N/A")
    summary = info.get("longBusinessSummary", "")[:500]

    # Chunk 1 — fundamentals
    documents.append({
        "content": f"{name} ({ticker}) fundamentals: Sector: {sector}, Industry: {industry}. "
                   f"Market Cap: {market_cap}. Trailing PE: {pe_ratio}. "
                   f"Total Revenue: {revenue}. Profit Margins: {profit_margins}. "
                   f"52-week range: {week52_low} - {week52_high}.",
        "source": f"yfinance/{ticker}/fundamentals",
        "ticker": ticker.replace(".NS", "")
    })

    # Chunk 2 — analyst sentiment
    documents.append({
        "content": f"{name} ({ticker}) analyst view: Recommendation: {recommendation}. "
                   f"Mean analyst price target: {analyst_target}. "
                   f"Business: {summary}",
        "source": f"yfinance/{ticker}/analyst",
        "ticker": ticker.replace(".NS", "")
    })

    # Chunk 3 — price history summary
    if hist_summary:
        documents.append({
            "content": f"{name} ({ticker}) recent price action: {hist_summary}",
            "source": f"yfinance/{ticker}/price_history",
            "ticker": ticker.replace(".NS", "")
        })

    return documents


def summarise_history(ticker_obj) -> str:
    """Pull 3-month price history and summarise as text."""
    try:
        hist = ticker_obj.history(period="3mo")
        if hist.empty:
            return ""
        start_price = round(hist["Close"].iloc[0], 2)
        end_price = round(hist["Close"].iloc[-1], 2)
        high = round(hist["Close"].max(), 2)
        low = round(hist["Close"].min(), 2)
        change_pct = round(((end_price - start_price) / start_price) * 100, 2)
        return (f"Over the last 3 months: opened at {start_price}, "
                f"currently at {end_price} ({change_pct}% change). "
                f"3-month high: {high}, low: {low}.")
    except Exception:
        return ""


if __name__ == "__main__":
    store = VectorStore()

    if store.size > 0:
        print(f"[SEED] Vector store already has {store.size} docs. Skipping.")
        print("[SEED] Delete data/vector_store.index and data/vector_store_docs.json to reseed.")
    else:
        all_docs = []
        for ticker in TICKERS:
            print(f"[SEED] Fetching {ticker}...")
            try:
                t = yf.Ticker(ticker)
                info = t.info
                hist_summary = summarise_history(t)
                docs = build_document(ticker, info, hist_summary)
                all_docs.extend(docs)
                print(f"  → {len(docs)} chunks built")
            except Exception as e:
                print(f"  → Failed: {e}")

        store.add_documents(all_docs)
        print(f"\n[SEED COMPLETE] {store.size} total documents in vector store")