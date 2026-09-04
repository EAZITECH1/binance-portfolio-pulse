# 🏆 Binance Agent OS Mini Hackathon — Submission Package

**Project Name:** Binance PortfolioPulse AI  
**Track:** Track A – Agent Creation (Data Analysis Theme)  
**Submission Deadline:** Sept 8, 2026, 23:59 UTC  

---

## 📱 Short Project Description for Submission Post on X (Twitter)

> 🚀 Excited to submit **Binance PortfolioPulse AI** for the @Binance Agent OS Mini Hackathon (Track A – Data Analysis)!
> 
> PortfolioPulse is an autonomous AI agent powered by Binance Agent OS MCP that bridges crypto exchange infrastructure with intelligent data analytics. It tracks live portfolio holdings and 7-day market momentum, detects hidden risk vulnerabilities (like asset concentration and volatility spikes), and translates complex market movements into plain-language daily intelligence reports in Markdown, JSON, and interactive dark-mode HTML. Built for both non-traders and quants—secure, cron-ready, and zero-key testable! 🤖📊🟡
> 
> 🔗 GitHub: [https://github.com/EAZITECH1/binance-portfolio-pulse](https://github.com/EAZITECH1/binance-portfolio-pulse)  
> #Binance #AgentOS #BuildOnBinance #AIagents #MCP #CryptoAnalytics

*(Character count: ~560 chars / 3-5 punchy sentences, perfectly suited for a multi-media hackathon post on X with video attachment)*

---

## 🌟 Hackathon Track A Highlights

1. **Native Binance Agent OS Integration:**
   - Implements client connectivity to the official Binance MCP Server endpoint (`https://agent.binance.com/mcp/agentic`).
   - Supports Claude Desktop, Claude Code, Cursor, and Codex workflows with pre-packaged `mcp_config.json`.
   - Strictly non-custodial and read-only: adheres to Agent OS security standards with zero external withdrawal scope.

2. **Advanced Quantitative Risk & Market Trend Analytics:**
   - Multi-factor risk engine detects single-asset concentration (>35%), 24h volatility anomalies (>8%), sharp drawdowns, and cash buffer depletion.
   - Computes 7-day Simple Moving Averages (SMA) and historical volatility from candlestick klines.

3. **Plain-Language AI Financial Intelligence:**
   - Built-in financial synthesis engine explains daily crypto swings in plain English without trader jargon.
   - Produces three synchronized outputs: GitHub-flavored Markdown (`.md`), interactive responsive dark-mode HTML dashboard (`.html`), and machine-readable JSON (`.json`).

4. **Zero-Key Judge Experience:**
   - Reviewers can clone the repository and immediately execute `python3 run_agent.py --mode mock` to inspect end-to-end functionality without configuring API keys.
   - Includes full fallback resilience for offline or sandboxed test environments.

---

## 📦 Deliverables Checklist

- [x] Full working codebase in clean, modular repository structure
- [x] Comprehensive `README.md` with setup, MCP auth walkthrough, and usage instructions
- [x] Sample generated reports (`sample_reports/sample_report.html`, `sample_report.md`, `sample_report.json`)
- [x] 60–90 second demo video script & storyboard (`DEMO_SCRIPT.md`)
- [x] Automated test suite passing 100% (`tests/test_analytics.py`)
- [x] Open-source MIT License (`LICENSE`)
