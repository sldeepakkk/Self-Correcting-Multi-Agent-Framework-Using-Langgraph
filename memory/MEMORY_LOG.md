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

### Lesson #67 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the revenue and profit margin for TCS?

**Category:** `company_financials`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial metrics queries about a single company, decompose into sub-queries that focus on a specific aspect of the company's financials, rather than broad topics like 'financial metrics comparison'.

---

### Lesson #68 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three separate sub-queries ('What are RBI's latest rate decisions?', 'What are banking stocks fundamentals?', 'RBI rate decision impact on Indian banking sector stock prices analyst view') is too broad and does not effectively capture the relationship between RBI rate decisions and banking stocks. Decompose into: 'What are RBI's latest rate decisions?' + 'What is the impact of RBI rate decisions on banking stocks?'

---

### Lesson #69 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade deal affecting IT sector stocks on NSE?

**Category:** `trade_deal_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade deals on specific sectors, decompose into two separate sub-queries: one for the trade deal terms and another for the sector fundamentals.

---

### Lesson #70 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation and market outlook?

**Category:** `market_outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For market outlook queries, especially those involving compound queries like 'What is the current Nifty 50 valuation and market outlook?', decompose into separate sub-queries for 'market outlook' and 'valuation' and then combine the results.

---

### Lesson #71 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the outlook for defence sector stocks after India budget 2025?

**Category:** `defence_sector_stock_outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector stock outlook queries related to India budget announcements, decompose into two separate sub-queries: one for the budget announcements and one for the defence sector stock outlook. This will allow for more targeted and relevant information retrieval.

---

### Lesson #72 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** BEL and Zen Technologies — fundamentals and defence sector tailwinds

**Category:** `defence_sector_multiple_companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence sector queries involving multiple companies (e.g., BEL and Zen Technologies), use a more focused sub-query decomposition strategy that prioritizes specific company fundamentals and tailwinds over broad bridge queries.

---

### Lesson #73 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What happened to NSE small cap stocks this quarter?

**Category:** `NSE small cap stocks performance`

**Routing Recommendation:** `mixed`

**Lesson:**
> For NSE small cap stocks performance queries, sub-query decomposition should focus on specific performance metrics (e.g., returns, volatility) rather than broad topics (e.g., market trends, performance analysis).

---

### Lesson #74 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Which NSE stocks are best positioned for RBI rate cuts?

**Category:** `NSE stocks best positioned for RBI rate cuts`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about RBI rate cuts and NSE stocks, decompose into sub-queries that focus on specific stocks' interest rate sensitivity and historical repo rate change impact.

---

### Lesson #75 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.

**Category:** `financial_analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial analysis queries focusing on multiple aspects of a company's performance, such as revenue growth, operating margins, and analyst outlook, consider using a compound query decomposition strategy to retrieve relevant information from vector store in a single step.

---

### Lesson #76 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI policy decisions and their impact on Indian banking stocks?

**Category:** `RBI policy impact on Indian banking stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For RBI policy impact on Indian banking stocks queries, decompose into two separate sub-queries: one for RBI policy decisions and another for Indian banking stocks fundamentals.

---

### Lesson #77 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?

**Category:** `trade_agreement_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade agreements on specific sectors, decompose into a more focused sub-query on the sector's fundamentals and a separate sub-query on the trade agreement's terms.

---

### Lesson #78 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation relative to historical averages, and what are analysts expecting next?

**Category:** `valuation`

**Routing Recommendation:** `mixed`

**Lesson:**
> For valuation-related queries like 'Nifty 50 valuation', decompose into sub-queries that focus on specific metrics (e.g., 'Nifty 50 current valuation' and 'Nifty 50 historical valuation averages') and include analyst expectations in the sub-queries to improve retrieval scores.

---

### Lesson #79 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the analyst consensus on Infosys and how strong are its key financial metrics?

**Category:** `analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For analyst consensus and key financial metrics queries, consider a more focused sub-query decomposition strategy, breaking down the query into a single sub-query that targets specific analyst consensus strength and industry peer comparison metrics.

---

### Lesson #80 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How does the current energy market outlook affect IEX and related NSE energy companies?

**Category:** `energy market outlook affecting IEX and related NSE energy companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy market outlook queries related to specific NSE energy companies, decompose into two sub-queries: one for the general energy market outlook and another for the company-specific impact analysis.

---

### Lesson #81 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze BEL and Zen Technologies in the context of India's defence spending trends and future opportunities.

**Category:** `defence-related company analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence-related queries involving specific companies (e.g., BEL and Zen Technologies), decompose into a single sub-query focusing on the company fundamentals and performance analysis, and a separate sub-query on the broader defence spending trends and future opportunities. This will allow for more targeted and relevant information retrieval.

---

### Lesson #82 — 2026-07-03
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming India increases defence spending by 20% next year, which listed defence companies would benefit most and why?

**Category:** `defence spending impact analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence spending impact analysis queries, decompose into two separate sub-queries: 'defence spending trends and future opportunities in India' and 'listed defence companies in India fundamentals and performance analysis'. Then, use a bridge query to combine the results of these two sub-queries, rather than a single compound query.

---

### Lesson #83 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade agreement expected to affect Indian IT companies over the next year?

**Category:** `trade_agreement_industry_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade agreements on specific industries (e.g., 'India-US trade agreement expected impact on Indian IT companies'), decompose into a single sub-query focused on the trade agreement's terms and impact, and a separate sub-query focused on the industry's fundamentals and performance analysis.

---

### Lesson #84 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the analyst consensus on Infosys and how strong are its key financial metrics?

**Category:** `analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For analyst consensus and key financial metrics queries, decompose into separate sub-queries for analyst consensus strength and key financial metrics analysis, then combine the results.

---

### Lesson #85 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.

**Category:** `TCS financial performance analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries involving TCS financial performance, use a sub-query decomposition strategy that focuses on retrieving specific financial metrics (e.g., revenue growth, operating margins, analyst outlook) separately, rather than a compound query that attempts to retrieve all relevant information in a single step.

---

### Lesson #86 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI policy decisions and their impact on Indian banking stocks?

**Category:** `RBI policy decisions and their impact on Indian banking stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For RBI policy and banking stocks queries, the sub-query decomposition should be adjusted to focus on the most recent RBI policy decisions and their direct impact on banking stocks, rather than relying on analyst views and financial information.

---

### Lesson #87 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?

**Category:** `trade_agreement_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about the impact of trade agreements on specific sectors, decompose into a broad overview of the agreement and its expected effects, and a detailed analysis of the sector's fundamentals and performance. Specifically, for queries like 'India-US trade agreement expected impact on Indian IT companies', decompose into 'India-US trade agreement terms and impact on Indian IT sector' and 'Indian IT sector fundamentals and performance analysis over the next 12 months'.

---

### Lesson #88 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation relative to historical averages, and what are analysts expecting next?

**Category:** `valuation`

**Routing Recommendation:** `mixed`

**Lesson:**
> For valuation-related queries, especially those requiring multiple sub-queries, consider using a more focused sub-query decomposition strategy, such as retrieving the most relevant sub-queries first and then combining them.

---

### Lesson #89 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact analysis queries, specifically those involving rate cuts and sectoral analysis, decompose into a two-stage approach: first, retrieve general information on the rate cut's global impact, and second, use this information to inform a more targeted search for sector-specific effects.

---

### Lesson #90 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the analyst consensus on Infosys and how strong are its key financial metrics?

**Category:** `analyst consensus and key financial metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For analyst consensus and key financial metrics queries, consider using a single sub-query that combines both topics, rather than decomposing into separate sub-queries.

---

### Lesson #91 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Compare TCS and Infosys on growth, margins, and analyst sentiment, and identify which appears stronger today.

**Category:** `Company comparison`

**Routing Recommendation:** `mixed`

**Lesson:**
> For comparison queries between two companies (e.g., TCS and Infosys), decompose into separate sub-queries for each company's growth, margins, and analyst sentiment, but also include a sub-query for a combined analysis of both companies' growth and margins to provide a more comprehensive comparison.

---

### Lesson #92 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How does the current energy market outlook affect IEX and related NSE energy companies?

**Category:** `energy market outlook and impact on NSE listed energy companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy market outlook queries related to specific NSE energy companies, decompose into a broader energy market outlook sub-query and a company-specific sub-query, rather than a compound query connecting two distinct topics.

---

### Lesson #93 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze BEL and Zen Technologies in the context of India's defence spending trends and future opportunities.

**Category:** `defence spending trend analysis involving specific companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence spending trend analysis queries involving specific companies, decompose into a macro topic query and a company-specific query, and use a bridge query to connect the two topics.

---

### Lesson #94 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Compare the likely winners and losers on NSE if RBI cuts rates twice over the next year.

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition should be adjusted to focus on the impact of rate cuts on specific sectors and companies, rather than broad topics like 'RBI rate cut impact on Indian banking sector stock prices'.

---

### Lesson #95 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?

**Category:** `trade_agreement_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to the impact of trade agreements on specific sectors, such as 'India-US trade agreement expected impact on Indian IT companies', consider using a more focused sub-query decomposition strategy, breaking down the query into smaller, more targeted sub-queries that directly address the missing information identified by the judge, e.g., 'trade agreement impact' and 'expected effect'.

---

### Lesson #96 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?

**Category:** `trade_agreement_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about the impact of trade agreements on specific sectors, decompose into a broad overview of the agreement and its expected effects, and a detailed analysis of the sector's fundamentals and performance.

---

### Lesson #97 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact analysis queries, specifically those involving rate cuts and their effects on Indian sectors, consider decomposing into two separate sub-queries: one focusing on the rate cut's global impact and another on the sector-specific effects in India. This can help improve vector store retrieval and reduce the complexity of the compound query.

---

### Lesson #98 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Compare TCS and Infosys on growth, margins, and analyst sentiment, and identify which appears stronger today.

**Category:** `growth comparison`

**Routing Recommendation:** `mixed`

**Lesson:**
> For growth comparison queries involving multiple companies, decompose into separate sub-queries for each company's growth analysis, and then use a different sub-query for the comparison, rather than a single compound query.

---

### Lesson #99 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How does the current energy market outlook affect IEX and related NSE energy companies?

**Category:** `energy market outlook and NSE energy companies`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy market outlook queries related to specific NSE energy companies, decompose into a single query focusing on the company's energy market exposure and its impact on the company's performance.

---

### Lesson #100 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming India increases defence spending by 20% next year, which listed defence companies would benefit most and why?

**Category:** `defence spending trend analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For defence spending trend analysis queries, decompose into separate sub-queries for 'defence spending trend analysis' and 'NSE listed defence companies' to improve vector store retrieval. Then, use a bridge query to connect the results and determine which companies would benefit most.

---

### Lesson #101 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.

**Category:** `financial_performance_and_outlook`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial performance and outlook queries about a specific company, decompose into sub-queries that focus on the company's financial statements and analyst reports, rather than broad topic-based sub-queries.

---

### Lesson #102 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI policy decisions and their impact on Indian banking stocks?

**Category:** `RBI policy decisions and their impact on Indian banking stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For RBI policy-related queries with a compound structure, consider using a more focused sub-query decomposition strategy, such as using a bridge query to directly retrieve RBI policy decisions and their impact on Indian banking stocks, rather than decomposing into separate sub-queries.

---

### Lesson #103 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What is the current Nifty 50 valuation relative to historical averages, and what are analysts expecting next?

**Category:** `Nifty 50 valuation`

**Routing Recommendation:** `mixed`

**Lesson:**
> For Nifty 50 valuation queries, sub-query decomposition into three separate sub-queries ('Nifty 50 current valuation', 'Nifty 50 historical valuation averages', 'Nifty 50 analyst expectations') does not yield sufficient relevant information. Decompose into a single sub-query focused on Nifty 50 valuation and analysts' expectations.

---

### Lesson #104 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How are recent oil price movements affecting Reliance Industries and other energy-linked NSE stocks?

**Category:** `energy-linked NSE stock queries`

**Routing Recommendation:** `mixed`

**Lesson:**
> For energy-linked NSE stock queries, decompose into sub-queries that focus on specific stocks and their direct relationships with oil price movements, rather than broad topics like 'oil price impact on NSE energy-linked stocks'.

---

### Lesson #105 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?What are Infosys's fundamentals, valuation, and analyst sentiment, and how do they compare with its historical averages?

**Category:** `US Federal Reserve rate cut impact on Indian sectors`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about the impact of US Federal Reserve rate cuts on Indian sectors, decompose into two separate sub-queries: one focused on the macroeconomic impact of rate cuts and another on the specific sectors likely to benefit.

---

### Lesson #106 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.

**Category:** `company_financial_metrics`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about company-specific financial metrics (e.g., revenue growth, operating margins, analyst outlook), decompose into sub-queries that target specific financial statements (e.g., income statement, balance sheet, cash flow statement).

---

### Lesson #107 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI policy decisions and their impact on Indian banking stocks?

**Category:** `RBI policy decisions and their impact on Indian banking stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For RBI policy decisions and their impact on Indian banking stocks queries, the sub-query decomposition into three separate topics ('RBI latest policy decisions', 'Indian banking stocks fundamentals', 'RBI policy decisions impact on Indian banking sector stock prices') results in a low judge score due to missing information. Decompose into two topics: 'RBI policy decisions' and 'Indian banking stocks impact', and use a bridge query to combine both topics.

---

### Lesson #108 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** How is the India-US trade agreement expected to affect Indian IT companies over the next 12 months?

**Category:** `trade_agreement_sector_impact`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries about the impact of trade agreements on specific sectors, decompose into sub-queries that focus on the agreement details and sector fundamentals separately, then combine the results.

---

### Lesson #109 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?What are Infosys's fundamentals, valuation, and analyst sentiment, and how do they compare with its historical averages?

**Category:** `macroeconomic impact and sector analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact and sector analysis queries, decompose into sub-queries focusing on specific sectors (e.g., IT, manufacturing, agriculture) rather than broad categories (e.g., Indian sectors).

---

### Lesson #110 — 2026-07-04
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Analyze TCS revenue growth, operating margins, and analyst outlook over the last year.

**Category:** `business_performance_analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For business performance analysis queries like 'TCS revenue growth, operating margins, and analyst outlook', decompose into a single sub-query that combines all aspects, rather than separate sub-queries for each.

---

### Lesson #111 — 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact analysis queries, specifically those involving rate cuts and sectoral analysis, decompose into two sub-queries: 'US Federal Reserve rate cut impact on Indian economy' and 'Indian sectors likely to benefit from rate cuts'. Then, use a compound query strategy to combine the results of these two sub-queries, focusing on the intersection of their topics.

---

### Lesson #112 — 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact of rate cuts`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact queries involving rate cuts, decompose into two sub-queries: 'rate cut impact on economy' and 'sector-specific impact', rather than a single compound query.

---

### Lesson #113 — 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact of rate cuts on specific sectors`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact queries involving rate cuts, decompose into a single sub-query focusing on the sector-level impact, rather than a compound query with multiple sub-queries.

---

### Lesson #114 — 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact analysis queries, specifically those involving rate cuts and their effects on Indian sectors, decompose into two separate sub-queries: one for the rate cut's impact on the Indian economy and another for identifying sectors likely to benefit. This will allow for more targeted and efficient retrieval from the vector store.

---

### Lesson #115 — 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition should be adjusted to focus on the latest RBI rate decisions and their direct impact on banking stocks, rather than tangentially related topics. Decompose into: 'latest RBI rate decisions', 'repo rate change', 'banking stock impact analysis'.

---

### Lesson #117 â€” 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** "Screen all NSE-listed companies with a market capitalization above â‚¹10,000 crore that have delivered CAGR revenue growth above 15% and CAGR EPS growth above 18% over the last five financial years, while maintaining ROCE above 20% in each of the last three years and debt-to-equity below 0.5. Exclude banks, NBFCs, insurance companies, and newly listed companies with less than five years of financial history. Rank the remaining companies using a weighted score (40% earnings growth, 30% ROCE consistency, 20% operating cash flow growth, and 10% valuation discount relative to their 5-year median P/E). For the top 10, explain the key growth drivers, major risks, upcoming corporate events (results, dividends, splits, bonuses, or mergers), promoter holding trends, and whether the current valuation appears justified compared with industry peers. Finally, construct a diversified â‚¹10 lakh portfolio with position sizing based on volatility and maximum 25% sector exposure, and estimate expected annual return and downside under bull, base, and bear scenarios."

**Category:** `financial_analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial analysis queries with multiple sub-queries, consider using a more hierarchical decomposition strategy, where each sub-query is further decomposed into smaller, more focused sub-queries that retrieve specific financial metrics, rather than a flat decomposition into multiple sub-queries that retrieve a wide range of metrics.

---

### Lesson #118 â€” 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** "Find NSE stocks suitable for a long-term portfolio that have P/E below their 10-year median, revenue CAGR above 20% over five years, ROE above 18%, and debt-to-equity below 0.3. However, exclude any company whose stock has outperformed the NIFTY 500 by more than 50% over the last two years. Explain why each stock still qualifies despite the conflicting value and growth requirements."

**Category:** `long-term portfolio queries with multiple financial criteria`

**Routing Recommendation:** `mixed`

**Lesson:**
> For long-term portfolio queries with multiple financial criteria, consider using a more granular sub-query decomposition strategy, such as breaking down the query into smaller, more focused sub-queries that target specific financial metrics (e.g., P/E ratio, revenue CAGR, ROE, debt-to-equity ratio) and then combining the results using a bridge query.

---

### Lesson #119 â€” 2026-07-05
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Research whether India's semiconductor manufacturing ambitions are realistically achievable by 2030. Use government announcements, analyst reports, company statements, and international semiconductor industry research. Identify where sources disagree, explain why they disagree, distinguish between confirmed facts and optimistic projections, and conclude with your own evidence-weighted assessment.

**Category:** `India's semiconductor manufacturing ambitions`

**Routing Recommendation:** `mixed`

**Lesson:**
> For queries related to India's semiconductor manufacturing ambitions, decompose into sub-queries that focus on specific government initiatives and international semiconductor industry research, rather than broad topics like 'global semiconductor industry trends and challenges'.

---

### Lesson #120 â€” 2026-07-06
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** "What is the exact quarterly EPS for Wipro for Q1, Q2, Q3, and Q4 of FY2026, and how does each quarter compare to the same quarter in FY2025? Also state the exact dividend payout ratio and free cash flow conversion for FY2026."

**Category:** `financial_statements`

**Routing Recommendation:** `mixed`

**Lesson:**
> For financial statement queries requiring specific quarterly EPS figures and dividend payout ratios, decompose into sub-queries focusing on individual quarters (e.g., 'Wipro Q1 FY2026 EPS') rather than broad fiscal year queries.

---

### Lesson #121 â€” 2026-07-06
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** You are an autonomous market analyst. Your objective is not to predict the market, but to determine whether a prediction is even justified.

Analyze today's NSE session using:

Nifty and sector indices
Options chain
India VIX
FII/DII flows
Advance/decline ratio
Delivery percentage
Block and bulk deals
Corporate announcements
Relevant macro news

Perform the following loop:

Generate an initial market thesis.
Search for evidence against it.
Identify hidden assumptions.
Revise the thesis.
Repeat until no major contradictions remain or confidence stops improving.

In the final answer:

Separate facts from assumptions.
Assign confidence to every major conclusion.
Explicitly list what additional data would most change your view.
If the evidence is insufficient, state that no reliable directional conclusion can be made instead of forcing a prediction.

**Category:** `comprehensive market analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For comprehensive market analysis queries, prioritize sector indices and NSE session data over individual stock fundamentals. Decompose into: sector index analysis for market sentiment + NSE session data for overall market context.

---

### Lesson #122 â€” 2026-07-07
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** Assuming the US Federal Reserve cuts rates by 50 basis points, which Indian sectors are likely to benefit the most and why?

**Category:** `macroeconomic impact analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macroeconomic impact analysis queries, specifically those involving the US Federal Reserve's rate decisions and their effects on Indian sectors, consider decomposing the query into two separate sub-queries: one focusing on the US Federal Reserve's rate decision and its global market impact, and another on the Indian sectors sensitive to interest rate changes. This will allow for more accurate and relevant information to be retrieved from the vector store.

---

### Lesson #123 â€” 2026-07-07
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition into three distinct topics (rate decisions, banking stocks fundamentals, and rate decision impact) consistently results in low vector store scores. Consider decomposing into two topics: RBI rate decisions and their impact on banking stocks, and then use a bridge query to connect the two.

---

### Lesson #124 â€” 2026-07-07
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `macro_rbi_rates`

**Routing Recommendation:** `mixed`

**Lesson:**
> For macro_rbi_rates queries, the sub-query decomposition should be revised to focus on the specific impact of RBI rate decisions on banking stocks, rather than decomposing into separate sub-queries for rate decisions and stock fundamentals.

---

### Lesson #125 â€” 2026-07-07
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** What are the latest RBI rate decisions and impact on banking stocks?

**Category:** `RBI rate decision impact on banking stocks`

**Routing Recommendation:** `mixed`

**Lesson:**
> For RBI rate decision impact queries, decompose into sub-queries that focus on the rate decision itself and its direct impact on banking stocks, rather than trying to bridge two distinct topics.

---

### Lesson #126 â€” 2026-07-07
**Status:** ACTIVE (confidence=0.80, threshold=0.75)

**Query:** You are an evidence-driven analyst, not a prediction engine.

Your task is to determine whether the market's reaction to today's biggest Indian stock market news is rational.

Rules:

Identify the single most market-moving news event from today.
Explain why you selected it over other news.
Identify every listed company that could reasonably be affected directly or indirectly.
Collect relevant evidence including price movement, trading volume, sector performance, options activity (if available), corporate announcements, analyst commentary, and macroeconomic context.
Construct two competing explanations for the market reaction.
Explanation A: The reaction is fundamentally justified.
Explanation B: The reaction is primarily driven by sentiment, speculation, liquidity, or short-term positioning.
For each explanation:
List supporting evidence.
List contradicting evidence.
Identify hidden assumptions.
Estimate confidence.
Attempt to disprove the explanation with the higher confidence by searching for additional evidence.
If new evidence changes your conclusion, revise it and explain exactly what changed your mind.
Produce a final verdict that clearly separates:
Facts
Reasonable inferences
Assumptions
Speculation
Unknowns
If the available evidence is insufficient or contradictory, explicitly state that no reliable conclusion can be reached instead of forcing one.

Restrictions:

Never invent missing data.
Never assume causation from correlation without justification.
Every conclusion must be traceable to evidence.
If two sources disagree, explain why instead of choosing one without justification.
Confidence must decrease when evidence conflicts.
Your goal is not to sound confident; your goal is to be correct.

**Category:** `market-moving news event analysis`

**Routing Recommendation:** `mixed`

**Lesson:**
> For market-moving news event analysis, decompose the query into sub-queries that focus on identifying the single most significant news event, affected companies, and relevant evidence, and then construct competing explanations for the market reaction. Specifically, for this query category, break down the problem into sub-queries that focus on the news event, affected companies, and explanations for the market reaction, and ensure that each sub-query is analyzed independently before synthesizing the results.

---

