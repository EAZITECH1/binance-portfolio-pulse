# 🏆 Binance Agent OS Mini Hackathon — Submission Package

**Project Name:** Binance PortfolioPulse AI  
**Track:** Track A – Agent Creation (Data Analysis Theme)  
**Submission Deadline:** Sept 8, 2026, 23:59 UTC  

---

## 📱 Short Project Description for Submission Post on X (Twitter)

> 🚀 Excited to submit **Binance PortfolioPulse AI** for the @Binance Agent OS Mini Hackathon (Track A – Data Analysis)!
> 
> PortfolioPulse is an autonomous market intelligence & content creation agent powered by Binance Agent OS MCP. Connected AI agents (Claude, Codex, Cursor) can ask for "a market update" or "draft a tweet" to pull live exchange + market price feed metrics, detect portfolio risk flags, and generate publication-ready, Cointelegraph-style tweets & threads (<280 chars) plus full dark-mode HTML dashboards. Built for Web3 creators and quants—secure, cron-ready, and zero-key testable! 🤖📊🟡🐦
> 
> 🔗 GitHub: [https://github.com/EAZITECH1/binance-portfolio-pulse](https://github.com/EAZITECH1/binance-portfolio-pulse)  
> #Binance #AgentOS #BuildOnBinance #AIagents #MCP #CryptoAnalytics #Web3

*(Character count: ~680 chars / punchy social post, perfectly formatted for a multi-media hackathon video announcement on X)*

---

## 🌟 Hackathon Track A Highlights

1. **Native Binance Agent OS MCP Integration:**
   - Implements full client connectivity to the official Binance MCP Server endpoint (`https://agent.binance.com/mcp/agentic`).
   - Exposes 7 MCP tools: `get_market_overview`, `get_price_feed_snapshot`, `generate_market_brief`, `draft_tweet`, `get_account_balances`, `get_ticker_24hr`, and `get_klines`.
   - Compatible with Claude Desktop, Claude Code, Cursor, and Codex workflows via `mcp_config.json`.
   - Strictly non-custodial with zero external withdrawal scope.

2. **Market Intelligence & Price Feed Analysis:**
   - Standalone market briefs tracking top movers (BTC, ETH, SOL, BNB, SUI, AVAX, DOGE, PEPE), 24h quote volumes, and sentiment.
   - Market indicators and price feeds across BNB Chain, Ethereum, and Solana (gas in Gwei, DEX volume, daily tx benchmarks, DeFi TVL, and institutional exchange flow signals).

3. **Web3 Content Creator Social Drafter:**
   - Transforms complex raw data into publication-ready tweets and 3-part threads in crypto-journalism style (Cointelegraph / CoinMarketCap).
   - Strictly validates Twitter/X 280-character limits per tweet.

4. **Quantitative Risk & Portfolio Intelligence:**
   - Multi-factor risk engine detects single-asset concentration (>35%), 24h volatility anomalies (>8%), sharp drawdowns, and cash buffer depletion.
   - Generates responsive dark-mode HTML dashboards, Markdown briefs, and machine-readable JSON payloads.

5. **Zero-Key Judge Experience:**
   - Reviewers can clone the repository and immediately execute `python3 run_agent.py --brief market --draft-tweet` or `python3 run_agent.py --brief portfolio --format all` without configuring API keys.
   - Resilient offline/sandboxed fallback with comprehensive test suite (13/13 passing).

---

## 📦 Deliverables Checklist

- [x] Full working codebase in clean, modular repository structure
- [x] Comprehensive `README.md` with setup, MCP auth walkthrough, and natural language prompt catalog
- [x] Sample generated market briefs, drafted tweets, and HTML dashboards in `sample_reports/`
- [x] 60–90 second demo video script & storyboard (`DEMO_SCRIPT.md`)
- [x] Automated test suite passing 100% (13/13 unit tests across `test_analytics.py`, `test_content.py`, `test_price_feeds.py`)
- [x] Open-source MIT License (`LICENSE`)
