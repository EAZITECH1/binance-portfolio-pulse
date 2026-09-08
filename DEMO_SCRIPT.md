# 🎬 Binance PortfolioPulse AI — Demo Video Script & Storyboard

**Hackathon Track:** Binance Agent OS Mini Hackathon (Track A – Agent Creation, Data Analysis)  
**Target Video Duration:** 75–85 Seconds (Strictly within 60–90s Hackathon Limit)  
**Presenter:** Screen recording with voiceover (Claude Desktop / Terminal / Browser)  
**Core Theme:** Autonomous Market Intelligence, Portfolio Risk Engine, and Social Drafter powered by Binance Agent OS MCP  

---

## ⏱️ Video Structure Overview

| Timestamp | Scene | Key Visual Focus | Spoken Focus |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:15** | **1. The Hook & Agent OS Connection** | Split screen: VS Code (`mcp_config.json`) & Claude Desktop showing Binance MCP tools loaded | Introduction, Binance Agent OS MCP architecture, non-custodial disclaimer |
| **00:15 – 00:35** | **2. Claude Desktop Live Market Intelligence** | Claude Desktop chat UI with hammer tool icon: prompting top market movers | Asking for top movers and volume across watchlist; live Binance spot data |
| **00:35 – 00:52** | **3. Web3 Content Drafter in Claude** | Claude invoking `draft_tweet()` tool live in chat | Single tweet generation under 280 chars with real spot stats & tickers |
| **00:52 – 01:10** | **4. Terminal Thread Drafter & Dashboard** | Terminal running CLI thread drafter + Browser showing dark-mode HTML report | 3-part Twitter thread (<280 chars each) + multi-factor risk dashboard |
| **01:10 – 01:22** | **5. Security & GitHub Wrap-Up** | Terminal test suite (15/15 passing in 0.03s) + GitHub repo screen | Verified test suite, non-custodial architecture, GitHub repository |

---

## 🎙️ Detailed Scene-by-Scene Script & Storyboard

---

### 🟢 SCENE 1: The Hook & Binance Agent OS Connection (00:00 – 00:15)

#### 🖥️ What Displays Onscreen:
1. Start on **VS Code** showing [`mcp_config.json`](mcp_config.json):
   - Highlight the line pointing to the official Binance MCP endpoint:
     `"https://agent.binance.com/mcp/agentic"`
   - Highlight the local stdio command `python3 -m src.connectors.mcp_client --stdio`.
2. Transition smoothly to **Claude Desktop**:
   - Open a fresh chat.
   - Click the small **hammer icon** (tools menu) at the bottom-right of the Claude chat box.
   - Show the **8 active PortfolioPulse tools**: `ask_portfoliopulse`, `get_top_by_market_cap`, `get_market_overview`, `generate_market_brief`, `draft_tweet`, `get_account_balances`, `get_ticker_24hr`, `get_klines`.
3. Subtle overlay at the bottom:  
   *⚠️ Autonomous Research & Analysis Tool — Strictly Non-Custodial (No Auto-Trading / No Withdrawal Scopes)*

#### 🗣️ Spoken Voiceover:
> *"Welcome to **Binance PortfolioPulse AI**—an autonomous market intelligence and portfolio risk engine built on the **Binance Agent OS Model Context Protocol**.
>
> Right here in Claude Desktop, PortfolioPulse connects directly via Binance Agent OS MCP, exposing 8 institutional tools without requiring custody or manual API key exposure."*

---

### 🟢 SCENE 2: Claude Desktop Live Market Intelligence (00:15 – 00:35)

#### 🖥️ What Displays Onscreen:
1. In **Claude Desktop**, type this exact prompt into the chat bar and hit enter:
   ```text
   Show me the top market movers and volume across the crypto watchlist
   ```
2. **Claude Desktop Action**:
   - Claude shows: *"Using tool: `ask_portfoliopulse`"* (or `get_market_overview`).
   - In ~1.5 seconds, Claude renders real-time market intelligence:
     - **Headline**: *Market Choppiness: BTC Tests $78,504 While Selective Alts Rally*
     - **Sentiment**: `MODERATE RISK ON`
     - **24h Tracked Volume**: ~$8.0B USD across active Binance spot markets
     - **Top Gainers**: Genuine active runners (`$SOPH +29.6%`, `$QKC +18.5%`, `$FORM +18.5%`)
     - **Top Losers**: Genuine active pullbacks (`$MARSCOIN -11.5%`, `$ORCA -7.7%`)
     - **Live Observations**: BTC consolidating near $78.5k with active liquidity metrics
3. Mouse cursor briefly highlights the tracked $8.0B spot volume and verified top gainers.

#### 🗣️ Spoken Voiceover:
> *"Let's test it live in Claude Desktop. When we ask for top market movers and volume across the watchlist, the agent scans Binance spot markets in real time.
>
> In under two seconds, it tracks over 8 billion dollars in spot volume, identifies genuine runners like SOPH and QKC, and filters out halted pairs—giving traders 100% verified exchange intelligence."*

---

### 🟢 SCENE 3: Web3 Content Drafter in Claude (00:35 – 00:52)

#### 🖥️ What Displays Onscreen:
1. In the same **Claude Desktop** conversation, type:
   ```text
   Draft a punchy, publication-ready tweet about today's crypto market action using PortfolioPulse. Include tickers and hashtags.
   ```
2. **Claude Desktop Action**:
   - Claude calls `draft_tweet(topic="market", style="single")`.
   - Claude outputs the ready-to-post tweet:
     ```text
     ⚡ MARKET UPDATE: Bitcoin holds near $78,548 (-0.8%) as selective altcoins decouple.

     Key movers: $SOPH (+31.2%) & $QKC (+18.9%).
     Tracked 24h volume stands at $8.0B on Binance spot.

     #Bitcoin #Crypto #Binance
     ```
   - Highlight the character counter tag: `[218/280 characters — Verified Twitter/X Compliant]`.

#### 🗣️ Spoken Voiceover:
> *"Next, let's ask Claude to draft a publication-ready market tweet. 
>
> PortfolioPulse analyzes real-time spot movers across Binance, verifies Bitcoin's price trajectory with truthful editorial phrasing, and formats a Cointelegraph-style update strictly under 280 characters—ready to post in one click."*

---

### 🟢 SCENE 4: Terminal Thread Drafter & Risk Dashboard (00:52 – 01:10)

#### 🖥️ What Displays Onscreen:
1. Switch to **Terminal** and run this exact command:
   ```bash
   python3 run_agent.py --brief market --draft-tweet --tweet-style thread
   ```
   - Terminal immediately prints a structured 3-part thread:
     - `[1/3] (227/280 chars): 🚨 MARKET PULSE: Crypto consolidates with Bitcoin steady near $78,548...`
     - `[2/3] (204/280 chars): 📊 KEY MOVERS & BINANCE SPOT ACTIVITY: $SOPH, $QKC, $8.0B volume...`
     - `[3/3] (186/280 chars): 💡 TAKEAWAY: Selective rotation underway... #Bitcoin #Crypto #Binance`
2. Quick switch (`Cmd + Tab`) to **Google Chrome** showing [`sample_reports/sample_report.html`](sample_reports/sample_report.html):
   - Hover over the **Risk Assessment Cards**:
     - 🚨 `CRITICAL: Single-Asset Concentration (>35%) — Bitcoin represents 55.1%`
     - ⚠️ `WARNING: Elevated Volatility — High-beta swing detected`
     - ⚠️ `CAUTION: Stablecoin Buffer — Liquid cash at 5.3%`
   - Show the **Institutional Structured Brief** (*What Happened / What to Watch / Risks*).

#### 🗣️ Spoken Voiceover:
> *"Beyond single tweets, PortfolioPulse runs as a standalone CLI to generate complete 3-part analytical threads—with every post verified under 280 characters.
>
> Simultaneously, our quantitative risk engine audits asset concentration, volatility anomalies, and cash reserve depletion, producing institutional dark-mode HTML reports."*

---

### 🟢 SCENE 5: Security Architecture & Wrap-Up (01:10 – 01:22)

#### 🖥️ What Displays Onscreen:
1. In Terminal, run the test suite:
   ```bash
   python3 -m unittest discover -s tests -v
   ```
   - Terminal prints: `Ran 15 tests in 0.037s ... OK`.
2. Switch to the **GitHub Repository** page (`https://github.com/EAZITECH1/binance-portfolio-pulse`):
   - Scroll across the clean architecture, 8 documented MCP tools, and sample reports.
3. Fade to end title screen:
   - **Binance PortfolioPulse AI**
   - *Binance Agent OS Mini Hackathon — Track A*
   - GitHub: `github.com/EAZITECH1/binance-portfolio-pulse`

#### 🗣️ Spoken Voiceover:
> *"With 15 passing hermetic unit tests, strict non-custodial safety, and native Binance Agent OS integration, PortfolioPulse brings institutional intelligence to any AI workflow.
>
> Build with Binance PortfolioPulse on GitHub!"*

---

## 📋 Pro-Recording Tips & Checklist

1. **Window Setup Before Recording**:
   - **Left / Main:** Claude Desktop (set zoom to 110% with `Cmd + +` so judges can easily read the chat).
   - **Right / Background:** VS Code with `mcp_config.json` and Terminal with clear prompt.
   - **Browser Tab:** Pre-open `sample_reports/sample_report.html` so you can switch to it with a single `Cmd + Tab`.
2. **Claude Desktop Preparation**:
   - Open Claude Desktop and confirm the hammer icon displays the 8 tools.
   - Pre-copy the two prompts so you can paste them instantly without typing mistakes:
     - Prompt 1: `Show me the top market movers and volume across the crypto watchlist`
     - Prompt 2: `Draft a punchy, publication-ready tweet about today's crypto market action using PortfolioPulse. Include tickers and hashtags.`
3. **Pacing & Timing**:
   - Total word count is **~210 words**, which naturally takes **75 seconds** at a conversational tempo.
   - This leaves you a 15-second buffer before the 90-second cutoff.
4. **Resolution**:
   - Record in **1920x1080 (1080p, 60 FPS)** for razor-sharp text and dashboard graphics.
