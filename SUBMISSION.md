# 🏆 Binance Agent OS Mini Hackathon — Submission Package

**Project Name:** Binance PortfolioPulse AI  
**Track:** Track A – Agent Creation (Data Analysis Theme)  
**Submission Deadline:** Sept 8, 2026, 23:59 UTC  
**Public Video Post on X (Twitter):** [https://x.com/eazitechh/status/2097412347803435075](https://x.com/eazitechh/status/2097412347803435075)  

---

## 📱 Short Project Description for Submission Post on X (Twitter)

> 🚀 Excited to submit **Binance PortfolioPulse AI** for the @Binance Agent OS Mini Hackathon (Track A – Data Analysis)!
> 
> PortfolioPulse is an autonomous market intelligence & content creation agent powered by Binance Agent OS MCP. Connected AI agents (Claude, Codex, Cursor) can ask for "a market update" or "draft a tweet" to pull live exchange data, detect portfolio risk flags, and generate publication-ready, Cointelegraph-style tweets & threads (<280 chars) plus full dark-mode HTML dashboards. Built for Web3 creators and quants—secure, cron-ready, and zero-key testable! 🤖📊🟡🐦
> 
> 🔗 GitHub: [https://github.com/EAZITECH1/binance-portfolio-pulse](https://github.com/EAZITECH1/binance-portfolio-pulse)  
> #Binance #AgentOS #BuildOnBinance #AIagents #MCP #CryptoAnalytics #Web3

*(Character count: ~680 chars / punchy social post, perfectly formatted for a multi-media hackathon video announcement on X)*

---

## 🌟 Hackathon Track A Highlights

PortfolioPulse is usable directly inside Claude Desktop as a set of MCP tools, and also runs standalone via CLI with optional LLM-powered summaries.

1. **Native Binance Agent OS MCP Integration & Dual Usage Modes:**
   - Implements full client connectivity to the official Binance MCP Server endpoint (`https://agent.binance.com/mcp/agentic`) and interactive local stdio server.
   - Exposes 14 MCP tools: `ask_portfoliopulse`, `get_top_by_market_cap`, `get_order_book`, `get_my_trades`, `get_deposit_history`, `get_withdraw_history`, `get_futures_account`, `get_predictive_balance`, `get_market_overview`, `generate_market_brief`, `draft_tweet`, `get_account_balances`, `get_ticker_24hr`, and `get_klines`.
   - Verified live in Claude Desktop, Claude Code, Cursor, and Codex workflows via `mcp_config.json`.
   - **Strictly read-only & non-custodial:** Zero order placement or trading capabilities; zero external withdrawal scope.

2. **Verified Binance Market Intelligence & Order Book Liquidity:**
   - Standalone market briefs tracking top movers (BTC, ETH, SOL, BNB, SUI, AVAX, DOGE, PEPE), 24h spot volumes, and market sentiment.
   - Real-time exchange indicators across Binance spot markets (tracked USD volume, 24h price changes, and top gainer/loser rankings).
   - Real-time Order Book market depth, best bid/ask, spread in USD and basis points (bps), and order imbalance ratios.
   - Live market cap rankings via Binance's composite marketing API with circulating supply and true USD valuations.

3. **Web3 Content Creator Social Drafter:**
   - Transforms complex raw data into publication-ready tweets and 3-part threads in crypto-journalism style (Cointelegraph / CoinMarketCap).
   - Strictly validates Twitter/X 280-character limits per tweet.

4. **Quantitative Risk, Transfers, & Portfolio Intelligence:**
   - Multi-factor risk engine detects single-asset concentration (>35%), 24h volatility anomalies (>8%), sharp drawdowns, and cash buffer depletion.
   - Ingests past filled spot orders (myTrades) on any pair, computing average fill prices, trade counts, and commissions paid (Read-Only).
   - Tracks crypto & fiat deposit and withdrawal history with net asset cash flow calculations.
   - Ingests USDT-M Futures derivatives margin balances and leverage (reporting spot-only mode when disabled).
   - Quantitative predictive balance engine with empirical beta calculations and 30-day VaR stress tests.
   - Generates responsive dark-mode HTML dashboards, Markdown briefs, and machine-readable JSON payloads.

5. **Zero-Key Judge Experience:**
   - Reviewers can clone the repository and immediately execute `python3 run_agent.py --brief market --draft-tweet`, `python3 run_agent.py --orderbook BTCUSDT`, or `python3 run_agent.py --brief portfolio --format all` without configuring API keys.
   - Resilient offline/sandboxed fallback with comprehensive test suite (33/33 passing).

---

## 📦 Deliverables Checklist

- [x] Full working codebase in clean, modular repository structure
- [x] Comprehensive `README.md` with setup, MCP auth walkthrough, and natural language prompt catalog
- [x] Sample generated market briefs, drafted tweets, and HTML dashboards in `sample_reports/`
- [x] 60–90 second demo video walkthrough & live demonstration
- [x] Public demo video post on X (Twitter): [https://x.com/eazitechh/status/2097412347803435075](https://x.com/eazitechh/status/2097412347803435075)
- [x] Automated test suite passing 100% (33/33 unit tests across all analytical modules)
- [x] Open-source MIT License (`LICENSE`)
