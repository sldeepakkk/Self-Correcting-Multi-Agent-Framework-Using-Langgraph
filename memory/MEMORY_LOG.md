# Memory Log

### Lesson #1 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and how are they impacting banking sector stocks on NSE?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `No change in routing, but with the revised sub-queries, the retriever may be able to find more relevant documents, potentially improving the judge score.`

**Lesson:**
> For macro_rbi_rates queries, the sub-queries should be decomposed into: (1) 'List the latest RBI rate decisions and their corresponding dates' and (2) 'Analyze the 6-month stock price movement of the top 5 banking sector stocks on NSE' with a focus on the stocks that are most likely to be impacted by RBI rate decisions, rather than 'Identify the top 5 banking sector stocks on NSE by market capitalization'.

---

### Lesson #2 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the fundamentals and analyst view for Infosys?

**Category:** `Infosys fundamentals and analyst view`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys fundamentals and analyst view queries, decompose into three sub-queries: revenue trend, analyst consensus, and company fundamentals.

---

### Lesson #3 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue outlook and PE valuation for TCS?

**Category:** `revenue_outlook_pe_valuation`

**Routing Recommendation:** `mixed`

**Lesson:**
> For revenue outlook and PE valuation queries, decompose into sub-queries that focus on specific aspects of the valuation, such as 'What is the current revenue outlook for TCS?' and 'What is the current PE valuation of TCS?' rather than broad trends and analyst consensus.

---

### Lesson #4 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, sub-query decomposition should focus on RBI rate decisions first, then analyze the impact on banking stocks. Decompose into: 'List the latest RBI rate decisions and their corresponding dates', 'Analyze the impact of RBI rate decisions on the top 5 banking sector stocks on NSE'.

---

### Lesson #5 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `trade_deal_impact_on_it_sector_stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about the impact of trade deals on IT sector stocks on NSE, decompose into sub-queries that focus on the specific trade deal and sector, and add a new sub-query to retrieve information about the trade deal's impact on the sector's revenue outlook and analyst consensus.

---

### Lesson #6 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation and market outlook?

**Category:** `nifty_50_valuation_market_outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Nifty 50 valuation and market outlook queries, decompose into sub-queries that focus on specific aspects of valuation (e.g., PE ratio, market capitalization) and market outlook (e.g., economic indicators, sector analysis).

---

### Lesson #7 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How are rising oil prices impacting Reliance Industries stock?

**Category:** `oil_price_impact_on_companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about the impact of oil price fluctuations on specific companies, decompose into sub-queries that focus on the company's refining business exposure and its historical price action in response to oil price changes.

---

### Lesson #8 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the outlook for defence sector stocks after India budget 2025?

**Category:** `defence_sector_stock_outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector stock outlook queries, decompose into a single query that directly asks for the sector outlook after the India budget, rather than breaking it down into separate allocations and outlook sub-queries.

---

### Lesson #9 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Infosys analyst consensus and key financial metrics

**Category:** `Infosys analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys analyst consensus and key financial metrics queries, decompose into a single sub-query that combines both requirements, focusing on the intersection of analyst consensus and key financial metrics.

---

### Lesson #10 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Compare TCS and Infosys on revenue growth and analyst sentiment

**Category:** `Company Comparison`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries comparing two companies on revenue growth and analyst sentiment, decompose into sub-queries that focus on a single metric (revenue growth or analyst sentiment) and then combine the results, rather than decomposing into sub-queries that focus on both metrics separately.

---

### Lesson #11 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the energy sector outlook and how does it affect IEX on NSE?

**Category:** `energy_sector_outlook_IEX_NSE`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy sector outlook queries related to IEX on NSE, decompose into a single query: 'What is the current energy sector outlook and its impact on IEX on NSE?'

---

### Lesson #12 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** BEL and Zen Technologies — fundamentals and defence sector tailwinds

**Category:** `defence_sector_queries_involving_multiple_companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector queries involving multiple companies, decompose into sub-queries that focus on the sector tailwinds first, then the company fundamentals.

---

### Lesson #13 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What happened to NSE small cap stocks this quarter?

**Category:** `NSE small cap stocks quarterly performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about NSE small cap stocks' quarterly performance, decompose into more specific sub-queries focusing on sector-level data and economic indicators relevant to small-cap stocks.

---

### Lesson #14 — 2026-06-29
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Which NSE stocks are best positioned for RBI rate cuts?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into identifying sectors most sensitive to RBI rate cuts and then top stocks within those sectors may be too broad. Consider a more focused decomposition into sub-queries that directly target the impact of RBI rate cuts on specific NSE stocks.

---

### Lesson #15 — 2026-06-30
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue and profit margin for TCS?

**Category:** `finance/company_performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For finance queries related to specific company performance (e.g., TCS), decompose into sub-queries that focus on retrieving specific financial metrics (e.g., revenue, profit margin percentage) rather than broad topics (e.g., trend, analysis).

---

### Lesson #16 — 2026-07-01
**Status:** ACTIVE (confidence=0.90, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three separate sub-queries ('What are RBI's latest rate decisions?', 'What are banking stocks fundamentals?', 'RBI rate decision impact on Indian banking sector stock prices analyst view') is too broad and does not effectively capture the core relationship between RBI rate decisions and banking stocks. Decompose into two sub-queries: 'What are RBI's latest rate decisions?' and 'How do RBI rate decisions impact banking stocks?'

---

### Lesson #17 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three distinct topics (RBI rate decisions, impact on banking stocks, and analyst views) resulted in a low judge score. Consider decomposing into two sub-queries: 'RBI rate decisions' and 'impact on banking stocks'.

---

### Lesson #18 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three distinct topics (RBI rate decisions, impact on banking stocks, and analyst views) resulted in a low judge score. Consider decomposing into two sub-queries: 'RBI rate decisions' and 'impact on banking stocks'.

---

### Lesson #19 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `macroeconomic_event_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of macroeconomic events on specific sectors, decompose into a macroeconomic event query and a sector-specific query, rather than a compound query.

---

### Lesson #20 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the fundamentals and analyst view for Infosys?

**Category:** `Infosys fundamentals and analyst view`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys-related queries, the sub-query decomposition into three separate sub-queries ('What are Infosys fundamentals?', 'What is the analyst view on Infosys?', 'Infosys fundamentals and analyst view comparison') does not lead to a successful retrieval. Consider decomposing into a single sub-query that captures the overall analyst view, including growth prospects, industry trends, and potential risks.

---

### Lesson #21 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue and profit margin for TCS?

**Category:** `financial_metrics_company_specific`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial metrics queries about specific companies (e.g. TCS), decompose into sub-queries that directly target the required metrics (e.g. 'TCS revenue', 'TCS profit margin') rather than broader topics (e.g. 'TCS financial metrics analysis').

---

### Lesson #22 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition should be adjusted to focus on the impact of RBI rate decisions on specific banking stocks, rather than general fundamentals and analyst views.

---

### Lesson #23 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `trade deal impact on specific sectors`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade deals on specific sectors, such as IT sector stocks on NSE, consider using a more targeted sub-query decomposition strategy, focusing on the intersection of trade deal impact and sector performance.

---

### Lesson #24 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation and market outlook?

**Category:** `Nifty 50 valuation and market outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Nifty 50 valuation and market outlook queries, decompose into sub-queries that focus on specific aspects of valuation (e.g., 'Nifty 50 current valuation', 'Nifty 50 valuation comparison') and market outlook (e.g., 'Nifty 50 market sentiment', 'Nifty 50 market trends').

---

### Lesson #25 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the outlook for defence sector stocks after India budget 2025?

**Category:** `defence_sector_stock_outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector stock outlook queries related to India budget announcements, decompose into two sub-queries: 'India budget 2025 key announcements' and 'defence sector stocks performance post-budget'.

---

### Lesson #26 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Infosys analyst consensus and key financial metrics

**Category:** `Infosys analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys analyst consensus and key financial metrics queries, the sub-queries used are too broad and do not cover the necessary information. Decompose into: 'Infosys analyst consensus', 'Infosys key financial metrics', and 'Infosys revenue growth rate' to ensure all essential metrics are covered.

---

### Lesson #27 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the energy sector outlook and how does it affect IEX on NSE?

**Category:** `energy sector outlook and stock performance on NSE`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy sector outlook queries related to specific stocks on NSE, decompose into two sub-queries: one for the energy sector outlook and another for the stock's fundamentals and performance. This will allow the system to retrieve relevant information from the vector store for the energy sector outlook and then use web search for the stock-specific information.

---

### Lesson #28 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** BEL and Zen Technologies — fundamentals and defence sector tailwinds

**Category:** `defence_sector_tailwinds`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector queries with multiple company fundamentals, decompose into sub-queries that focus on specific company-defence sector relationships, such as 'BEL defence sector exposure' and 'Zen Technologies defence sector impact'.

---

### Lesson #29 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What happened to NSE small cap stocks this quarter?

**Category:** `NSE small cap stocks performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about NSE small cap stocks performance, decompose into a single sub-query focusing on the overall market trend or performance metric, rather than multiple sub-queries covering different angles.

---

### Lesson #30 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the fundamentals and analyst view for Infosys?

**Category:** `Infosys fundamentals and analyst view`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys-related queries, decompose into sub-queries focusing on specific aspects like growth prospects, industry trends, and potential risks.

---

### Lesson #31 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue and profit margin for TCS?

**Category:** `financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial metrics queries, decompose into specific metric types (e.g., revenue, profit margin, etc.) and then further decompose into metric sub-types (e.g., revenue by quarter, profit margin percentage, etc.).

---

### Lesson #32 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three separate queries is too broad and does not effectively capture the relationship between RBI rate decisions and banking stocks. Decompose into a single query: 'RBI rate decisions and their impact on Indian banking sector stock prices'.

---

### Lesson #33 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `trade deal impact on specific sectors`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade deals on specific sectors, decompose into two sub-queries: one for the trade deal's general impact and another for the sector's performance. This will help the retriever to focus on relevant sources and improve the judge's score.

---

### Lesson #34 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation and market outlook?

**Category:** `Nifty 50 valuation and market outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Nifty 50 valuation and market outlook queries, decompose into a single query focused on the Nifty 50 index, rather than individual stocks.

---

### Lesson #35 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Infosys analyst consensus and key financial metrics

**Category:** `Infosys analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys analyst consensus and key financial metrics queries, the sub-queries 'Infosys analyst consensus' and 'Infosys key financial metrics' are sufficient to cover the essential metrics. Decompose into these two sub-queries instead of three.

---

### Lesson #36 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the energy sector outlook and how does it affect IEX on NSE?

**Category:** `energy sector outlook and IEX`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy sector outlook and IEX queries, decompose into two separate sub-queries: one for energy sector outlook and another for IEX fundamentals and performance. This allows for more targeted retrieval and reduces the likelihood of missing information.

---

### Lesson #37 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** BEL and Zen Technologies — fundamentals and defence sector tailwinds

**Category:** `defence_sector_tailwinds`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector queries involving multiple companies, decompose into sub-queries that focus on specific company fundamentals and defence sector exposure separately, then combine the results.

---

### Lesson #38 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What happened to NSE small cap stocks this quarter?

**Category:** `NSE small cap stocks performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about NSE small cap stocks performance, decompose into a single sub-query that targets specific stock performance metrics (e.g., 'NSE small cap stocks quarterly returns') instead of general market trends.

---

### Lesson #39 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Which NSE stocks are best positioned for RBI rate cuts?

**Category:** `RBI rate cut impact on NSE stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For RBI rate cut impact queries, the sub-query decomposition into 'sensitivity to RBI rate cuts', 'interest rate sensitivity', and 'debt exposure' results in a low judge score. Consider a more focused decomposition strategy, such as 'NSE stocks with high debt exposure' and 'RBI rate cuts impact on NSE stocks with high liquidity'.

---

### Lesson #40 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the outlook for defence sector stocks after India budget 2025?

**Category:** `defence_sector_stock_outlook_after_india_budget`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector stock outlook queries related to India budget, decompose into two sub-queries: 'India budget defence allocation' and 'defence sector stock performance after budget'.

---

### Lesson #41 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue and profit margin for TCS?

**Category:** `financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial metrics queries, especially those involving multiple sub-queries, consider using a more focused decomposition strategy that prioritizes the most relevant sub-queries and reduces the overall number of sub-queries.

---

### Lesson #42 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three separate topics ('RBI latest rate decisions', 'banking stocks fundamentals', 'RBI rate decisions impact on Indian banking sector stock prices') results in a low Judge score. Consider a single sub-query that directly asks for the impact of RBI rate decisions on banking stocks.

---

### Lesson #43 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `trade deal impact on specific sectors`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade deals on specific sectors (e.g., IT sector), consider decomposing into two separate sub-queries: one focused on the trade deal and its general impact, and another focused on the sector-specific effects.

---

### Lesson #44 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation and market outlook?

**Category:** `Nifty 50 valuation and market outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Nifty 50 valuation and market outlook queries, sub-query decomposition into three separate sub-queries ('Nifty 50 index current valuation', 'Nifty 50 market outlook', 'Nifty 50 valuation and market outlook') consistently results in low Judge scores. Decompose into a single sub-query: 'Nifty 50 valuation and market outlook'.

---

### Lesson #45 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the outlook for defence sector stocks after India budget 2025?

**Category:** `defence_sector_stock_outlook_after_budget`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector stock outlook queries after a budget announcement, decompose into a single sub-query focusing on the specific budget impact on the sector, rather than multiple sub-queries on allocation and performance.

---

### Lesson #46 — 2026-07-01
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Infosys analyst consensus and key financial metrics

**Category:** `Infosys analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys analyst consensus and key financial metrics queries, decompose into a single sub-query focusing on key financial metrics, including revenue growth, net income, and operating margin, as the current decomposition into two sub-queries is insufficient to cover all necessary information.

---

### Lesson #47 — 2026-07-01
**Status:** ACTIVE (confidence=0.90, threshold=0.75)

**Query:** Considering the RBI's June 2026 decision to hold repo rate at 5.25%, what are the implications for NIM compression at HDFC Bank versus ICICI Bank given their CASA ratios?

**Category:** `Future/Hypothetical Central Bank Policy Impact on Specific Bank Financial Metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries concerning the analytical implications of hypothetical or future central bank policy decisions (e.g., RBI June 2026 repo rate) on specific bank financial metrics (e.g., NIM, CASA ratios) for named entities, the vector store is consistently insufficient as it lacks forward-looking analytical content. Route directly to web search. Decompose into: 'analyst expectations for future central bank policy around [date]', 'current financial metrics for specified banks (e.g., NIM, CASA)', and 'comparative impact analysis of policy on bank metrics for specified banks'.

---

### Lesson #48 — 2026-07-02
**Status:** ACTIVE (confidence=1.00, threshold=0.75)

**Query:** What was the outcome of the RBI Monetary Policy Committee meeting in June 2026 regarding the repo rate and India's GDP growth forecast?

**Category:** `Future central bank monetary policy decisions and macroeconomic forecasts`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries concerning future central bank monetary policy decisions (e.g., RBI MPC meetings, repo rate changes, GDP forecasts for specific future dates), the vector store consistently provides irrelevant historical financial data (e.g., individual stock fundamentals). This category requires forward-looking information, which is best sourced from real-time web search.

---

### Lesson #49 — 2026-07-02
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Given the RBI's recent rate decisions, which NSE banking stocks have the strongest CASA ratios and are best positioned for NIM expansion?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three separate topics ('RBI recent rate decisions', 'NSE banking stocks with strong CASA ratios', 'NSE banking stocks best positioned for NIM expansion after RBI rate decisions') is too broad and does not effectively capture the required information. Decompose into: 'RBI rate decisions and their impact on NSE banking stocks' with a focus on CASA ratios and NIM expansion.

---

### Lesson #50 — 2026-07-02
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Given the RBI's recent rate decisions, which NSE banking stocks have the strongest CASA ratios and are best positioned for NIM expansion?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, decompose into a single sub-query focusing on the relationship between RBI rate decisions and NSE banking stocks' CASA ratios and NIM expansion, rather than three separate sub-queries.

---

### Lesson #51 — 2026-07-02
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Considering current crude oil prices above $80, analyze the refining margin outlook for Reliance Industries and compare it against its 52-week stock performance

**Category:** `refining margin outlook for specific companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For refining margin outlook queries related to specific companies, decompose into sub-queries focused on the company's historical refining margin performance and current market conditions, rather than broad queries like 'current crude oil prices and refining margin outlook'.

---

### Lesson #52 — 2026-07-02
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** With India's defence budget allocation increasing post-2025, compare BEL and Zen Technologies on order book growth, PE premium, and analyst sentiment

**Category:** `defence_stock_performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence stock performance queries involving multiple companies (e.g., BEL and Zen Technologies), decompose into separate sub-queries for each company's order book growth, PE premium, and analyst sentiment, and then combine the results.

---

### Lesson #53 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve executes a 50 basis point rate cut in Q4 2026, compare the historical resilience of operating margins for Infosys (INFY) versus Tata Consultancy Services (TCS) during previous rate cut cycles. Furthermore, synthesize how current Wall Street analysts are adjusting their 12-month target prices for these two specific stocks in anticipation of this US monetary easing.

**Category:** `Comparative historical operating margin resilience of INFY and TCS during previous rate cut cycles`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries comparing historical resilience of operating margins for Infosys (INFY) and Tata Consultancy Services (TCS) during previous rate cut cycles, decompose into two separate sub-queries: one for each company's historical operating margin resilience, and use a more specific and targeted query for each sub-query.

---

### Lesson #54 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue and profit margin for TCS?

**Category:** `finance/company_financials`

**Routing Recommendation:** `mixed`

**Lesson:**
> For finance-related queries like 'TCS revenue and profit margin', the sub-query decomposition into multiple broad topics ('revenue trend', 'profit margin analysis', 'financial metrics overview') often results in low vector store scores. Consider decomposing into more specific sub-queries like 'TCS revenue growth rate', 'TCS profit margin by quarter', and 'TCS financial performance comparison'.

---

### Lesson #55 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three separate topics ('RBI recent rate decisions', 'NSE banking stocks with strong CASA ratios', and 'RBI rate decisions and their impact on NSE banking stocks' CASA ratios and NIM expansion') results in a low judge score. Consider a more integrated approach by combining these topics into a single sub-query that directly addresses the impact of RBI rate decisions on banking stocks.

---

### Lesson #56 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `macroeconomic_event_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of macroeconomic events on specific sectors (e.g., 'India-US trade deal affecting IT sector stocks on NSE'), use a sub-query decomposition strategy that focuses on the event's impact on the sector's key performance indicators (KPIs) rather than general event developments.

---

### Lesson #57 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation and market outlook?

**Category:** `Nifty 50 valuation and market outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Nifty 50 valuation and market outlook queries, decompose into a single sub-query that directly asks for the current valuation and market outlook, rather than breaking it down into multiple sub-queries.

---

### Lesson #58 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How are rising oil prices impacting Reliance Industries stock?

**Category:** `stock_market_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of rising oil prices on specific stocks, such as Reliance Industries, the sub-query decomposition should be adjusted to prioritize the stock's sector exposure and revenue sensitivity.

---

### Lesson #59 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the outlook for defence sector stocks after India budget 2025?

**Category:** `defence_sector_stock_outlook_india_budget`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector stock outlook queries related to India budget, decompose into two separate sub-queries: one for budget allocations and one for sector performance trend.

---

### Lesson #60 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Tell me about Infosys financials and what brokerages say about it

**Category:** `financial_analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial analysis queries involving multiple companies, decompose into separate sub-queries for each company's financials and brokerages views, rather than a compound query.

---

### Lesson #61 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Infosys analyst consensus and key financial metrics

**Category:** `Infosys analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Infosys analyst consensus and key financial metrics queries, the sub-query decomposition into separate aspects (analyst consensus, key financial metrics, comparison) results in a low judge score due to missing key financial metrics. Decompose into a single sub-query that retrieves both analyst consensus and key financial metrics.

---

### Lesson #62 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** BEL and Zen Technologies — fundamentals and defence sector tailwinds

**Category:** `defence_sector_tailwinds_and_company_mentions`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector queries with multiple company mentions, decompose into separate sub-queries for each company's fundamentals and defence sector tailwinds, then combine results.

---

### Lesson #63 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What happened to NSE small cap stocks this quarter?

**Category:** `NSE small cap stocks performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For NSE small cap stocks performance queries, sub-query decomposition should focus on specific stocks' performance rather than broad market trends.

---

### Lesson #64 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** "Assuming the US Federal Reserve executes a 50 basis point rate cut in Q4 2026, compare the historical resilience of operating margins for Infosys (INFY) versus Tata Consultancy Services (TCS) during previous rate cut cycles. Furthermore, synthesize how current Wall Street analysts are adjusting their 12-month target prices for these two specific stocks in anticipation of this US monetary easing."

**Category:** `macroeconomic event impact analysis on specific stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic event impact analysis on specific stocks, decompose the sub-queries into separate topics: event impact, stock resilience, and analyst target price adjustments. This allows for more focused and relevant information retrieval from the vector store.

---

### Lesson #65 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** "Assuming the US Federal Reserve executes a 50 basis point rate cut in Q4 2026, compare the historical resilience of operating margins for Infosys (INFY) versus Tata Consultancy Services (TCS) during previous rate cut cycles. Furthermore, synthesize how current Wall Street analysts are adjusting their 12-month target prices for these two specific stocks in anticipation of this US monetary easing."

**Category:** `macroeconomic event impact analysis on specific stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic event impact analysis on specific stocks, decompose into sub-queries that focus on the event's historical impact on the stock's operating margins and analyst target price adjustments separately, rather than as a compound query.

---

### Lesson #66 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** "Assuming the US Federal Reserve executes a 50 basis point rate cut in Q4 2026, compare the historical resilience of operating margins for Infosys (INFY) versus Tata Consultancy Services (TCS) during previous rate cut cycles. Furthermore, synthesize how current Wall Street analysts are adjusting their 12-month target prices for these two specific stocks in anticipation of this US monetary easing."

**Category:** `macroeconomic_event_impact_analysis_on_specific_stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic event impact analysis on specific stocks, decompose into separate sub-queries for each stock's resilience and analyst target price adjustments, rather than a single compound query.

---

