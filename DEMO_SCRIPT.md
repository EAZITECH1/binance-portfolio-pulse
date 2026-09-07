# 🎬 Binance PortfolioPulse AI — Demo Video Script & Storyboard

**Hackathon Track:** Binance Agent OS Mini Hackathon (Track A – Agent Creation, Data Analysis)  
**Target Video Duration:** 75 Seconds (60–90s limit)  
**Presenter:** Screen recording with voiceover (IDE / Terminal / Browser)  
**Core Theme:** Autonomous Market Intelligence & Portfolio Risk Engine powered by Binance Agent OS MCP

---

## ⏱️ Video Breakdown & Storyboard

```
+------------------+-----------------------------------------------------------------------------+
| Timestamp        | On-Screen Action & Visual Focus                                             |
+------------------+-----------------------------------------------------------------------------+
| 00:00 - 00:15    | SCENE 1: The Binance Agent OS Connection (The "Agent OS Moment")           |
|                  | Showing mcp_config.json / OAuth handshake connecting via Binance Agent OS.  |
|                  | [DISCLAIMER OVERLAY: Research & Analysis Agent — NOT an Auto-Trading Bot]   |
| 00:15 - 00:32    | SCENE 2: Live Ingestion via Binance Agent OS MCP (--mode mcp)               |
|                  | Live portfolio balances & market feeds streamed via Binance MCP server.     |
| 00:32 - 00:48    | SCENE 3: Quantitative Risk Flags Firing from Live Data                      |
|                  | Multi-factor risk engine: asset concentration (>50%), volatility anomalies. |
| 00:48 - 01:05    | SCENE 4: Institutional Structured Brief Rendering                           |
|                  | "What Happened / What to Watch / Risks" synthesis & dark-mode dashboard.   |
| 01:05 - 01:15    | SCENE 5: Bonus Output (draft_tweet) & Hackathon Wrap-Up                     |
|                  | Secondary output: 1-click verified tweet (<280 chars) + GitHub repo link.   |
+------------------+-----------------------------------------------------------------------------+
```

---

### Scene 1: The Binance Agent OS Connection — The "Agent OS Moment" (00:00 – 00:15)
* **Visual:** Clean split-screen in VS Code highlighting [`mcp_config.json`](mcp_config.json) pointing to `https://agent.binance.com/mcp/agentic` and the Claude Desktop MCP configuration.
* **On-Screen Graphic / Badge:** 
  🟡 **BINANCE AGENT OS CONNECTED (Model Context Protocol)**  
  ⚠️ **RESEARCH & ANALYSIS AGENT ONLY — NOT AN AUTO-TRADING BOT**
* **Caption Cue:** `[Connecting via Binance Agent OS MCP Server: agent.binance.com/mcp/agentic]`
* **Voiceover:**
  > "Welcome to **Binance PortfolioPulse AI**. Right here in `mcp_config.json`, our agent registers with the official **Binance Agent OS Model Context Protocol** server. Before we begin, an important note: PortfolioPulse is strictly an autonomous research and data intelligence tool—not an automated trading bot or execution script. By connecting via Binance Agent OS MCP, any AI client or researcher can securely query verified exchange and market intelligence without managing API keys or exposing withdrawal risks."

---

### Scene 2: Live Ingestion via Binance Agent OS MCP (00:15 – 00:32)
* **Visual:** Terminal window. Clear screen and execute:
  ```bash
  python3 run_agent.py --mode mcp --brief portfolio
  ```
* **On-Screen Action:**
  Terminal logs show live handshake and data stream:
  ```text
  [INFO] Initializing Binance Agent OS MCP client...
  [INFO] Connected to Binance MCP server: https://agent.binance.com/mcp/agentic
  [INFO] Invoking MCP tool: get_account_balances() -> Received 4 active spot balances
  [INFO] Invoking MCP tool: get_ticker_24hr() & get_market_overview()
  [INFO] Valuation complete: Total Portfolio Value $71,980.53 | 24h P&L: +$1,464.58 (+2.08%)
  ```
* **Caption Cue:** `[Live MCP data pull: Real account balances & market tickers ingested via Binance Agent OS]`
* **Voiceover:**
  > "Watch what happens when we run in MCP mode. Connecting via Binance Agent OS MCP, the agent directly invokes live protocol tools—retrieving real spot balances and live market feeds. There are no static hardcoded numbers or insecure local secrets here: live data streams straight into the agent's analytics pipeline."

---

### Scene 3: Quantitative Risk Flags Firing from Real Data (00:32 – 00:48)
* **Visual:** Terminal highlights the **Portfolio Risk Assessment** output, then seamlessly transitions to the browser showing the interactive dark-mode HTML dashboard (`sample_reports/sample_report.html`).
* **On-Screen Action:**
  Zoom in on the colored Risk Flags cards:
  - 🚨 `CRITICAL: Single-Asset Concentration (>35%) — Bitcoin represents 55.1% of portfolio`
  - ⚠️ `WARNING: Elevated Volatility — High-beta asset NEAR showing 11.2% daily swing`
  - ⚠️ `CAUTION: Stablecoin Buffer — Liquid cash at 5.3% (below recommended 10% reserve)`
* **Caption Cue:** `[Risk Engine: Quantitative multi-factor risk detection on live portfolio]`
* **Voiceover:**
  > "Instantly, our quantitative risk engine processes the live portfolio. It detects that Bitcoin makes up over 55% of total capital, triggering a high-concentration alert. It also flags volatility spikes on high-beta holdings and warns that liquid stablecoin reserves have dropped below safe thresholds."

---

### Scene 4: Structured Brief Rendering: What Happened / What to Watch / Risks (00:48 – 01:05)
* **Visual:** Scroll to the **Structured Intelligence Brief** section in the report dashboard.
* **On-Screen Text Layout:**
  - **1. What Happened:** Portfolio rose +2.1% (+$1,464.58), driven primarily by a +9.4% move in Solana.
  - **2. What to Watch:** Tracked Binance 24h volume tops $2.5B USD; selective altcoins showing strong momentum against Bitcoin consolidation.
  - **3. Key Risks & Actionable Next Steps:** Rebalance 10% of BTC into stablecoins to restore cash buffers and mitigate downside slippage.
* **Caption Cue:** `[Structured Brief: "What Happened / What to Watch / Risks" institutional synthesis]`
* **Voiceover:**
  > "PortfolioPulse turns this complex telemetry into an institutional-grade brief with three clear pillars: **What Happened**, **What to Watch**, and **Key Risks**. Instead of drowning in endless charts, researchers and traders get clear, structured financial commentary on what drove performance and what to monitor next."

---

### Scene 5: Bonus Output (`draft_tweet`) & Wrap-Up (01:05 – 01:15)
* **Visual:** Terminal window. Execute the secondary content drafter:
  ```bash
  python3 run_agent.py --brief market --draft-tweet --tweet-style single
  ```
* **On-Screen Action:**
  Terminal displays the drafted tweet under 280 characters with stats, hashtags, and character count verification (`[223/280 chars]`). Final screen shows GitHub repository URL.
* **Caption Cue:** `[Bonus Feature: 1-click Cointelegraph-style tweet draft (<280 chars) generated from brief]`
* **Voiceover:**
  > "As an editorial bonus for Web3 creators, the agent can also call `draft_tweet()` to compress that verified brief into a publication-ready post strictly under 280 characters. 7 MCP tools, 100% test coverage, and completely open source. Build with Binance PortfolioPulse on GitHub!"

---

## 🛠️ Recording & Production Checklist

1. **On-Screen Prominence for Binance Agent OS:**
   - Keep the `agent.binance.com/mcp/agentic` endpoint visible during Scene 1.
   - Use the caption overlay: `[Connecting via Binance Agent OS MCP]`.
2. **Disclaimer Prominence:**
   - Ensure the disclaimer banner is clearly visible during the intro:
     *“Autonomous Market Research & Analysis Tool — Not Financial Advice / Not an Automated Trading Bot.”*
3. **Live Execution:**
   - Run `--mode mcp` to demonstrate native Model Context Protocol communication.
4. **Video Specs:**
   - **Resolution:** 1920x1080 (Full HD, 60fps)
   - **Target Duration:** Exactly 70–75 seconds (well inside the 60–90 second limit).
   - **Audio:** Clear vocal delivery synced with terminal commands.
