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
| **00:15 – 00:35** | **2. Claude Desktop Live Interaction** | Claude Desktop chat UI with hammer tool icon: typing natural language prompts | Asking for top 10 market cap coins (live $USDT/$USDC rankings) & market brief |
| **00:35 – 00:52** | **3. Web3 Content Drafter in Claude** | Claude invoking `draft_tweet()` tool live in chat | Single tweet & 3-tweet thread generation under 280 chars with real spot stats |
| **00:52 – 01:10** | **4. CLI Engine & Risk Dashboard** | Terminal running CLI + Browser opening dark-mode HTML dashboard | Multi-factor risk engine (concentration >35%, volatility flags, cash buffer) |
| **01:10 – 01:22** | **5. Judge Summary & Wrap-Up** | Terminal test suite (15/15 passing in 0.03s) + GitHub repo screen | Zero-key judge experience, 8 MCP tools, 100% test coverage |

---

## 🎙️ Detailed Scene-by-Scene Script & Storyboard

---

### 🟢 SCENE 1: The Hook & Binance Agent OS Connection (00:00 – 00:15)

#### 🖥️ What Displays Onscreen:
1. Start on **VS Code** showing `mcp_config.json`:
   - Highlight line pointing to the official Binance MCP endpoint:
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
   What are the top 10 cryptocurrencies by market cap on Binance? Include prices and 24h change.
   ```
2. **Claude Desktop Action**:
   - Claude shows: *"Using tool: `get_top_by_market_cap`"*.
   - In ~1.5 seconds, Claude renders a beautiful, clean Markdown table:
     - **#1 BTC** (~$1.58T MCAP, ~$78,600)
     - **#2 ETH** (~$304B MCAP, ~$2,490)
     - **#3 USDT** (~$183B MCAP, $1.00)
     - **#4 BNB** (~$100B MCAP, ~$753)
     - **#5 XRP** (~$89B MCAP, $1.43)
     - **#6 USDC** (~$74B MCAP, $1.00)
     - **#7 SOL** (~$60B MCAP, ~$104)
     - **#8 TRX**, **#9 ZEC**, **#10 DOGE**
3. Cursor highlights that stablecoins (**USDT** & **USDC**) are properly ranked with exact circulating valuations pulled live from Binance.

#### 🗣️ Spoken Voiceover:
> *"Let's test it live in Claude Desktop. When we ask for the top 10 coins by market cap, the agent invokes `get_top_by_market_cap` directly against Binance's composite market feed.
>
> In under two seconds, it returns verified circulating valuations—placing Bitcoin at 1.58 trillion dollars, Ethereum second, and Tether third at 183 billion. Zero mocks, zero guesses—100% live Binance data."*

---

### 🟢 SCENE 3: Social Drafter & Market Brief in Claude (00:35 – 00:52)

#### 🖥️ What Displays Onscreen:
1. In the same **Claude Desktop** conversation, type:
   ```text
   Draft a punchy, publication-ready tweet about today's crypto market action using PortfolioPulse. Include tickers and hashtags.
   ```
2. **Claude Desktop Action**:
   - Claude calls `draft_tweet(topic="market", style="single")`.
   - Claude outputs the ready-to-post tweet:
     ```text
     ⚡ MARKET UPDATE: Bitcoin holds near $78,586 (-0.6%) as selective altcoins decouple.

     Key movers: $SOPH (+33.4%) & $QKC (+27.3%).
     Tracked 24h volume stands at $7.8B on Binance spot.

     #Bitcoin #Crypto #Binance
     ```
   - Highlight the character counter tag: `[218/280 characters — Verified Twitter/X Compliant]`.

#### 🗣️ Spoken Voiceover:
> *"Next, let's ask Claude to draft a publication-ready market tweet. 
>
> PortfolioPulse analyzes real-time spot movers across Binance, verifies Bitcoin's price trajectory with truthful editorial phrasing, and formats a Cointelegraph-style update strictly under 280 characters—ready to post in one click."*

---

### 🟢 SCENE 4: CLI Engine & Risk Dashboard (00:52 – 01:10)

#### 🖥️ What Displays Onscreen:
1. Switch to **Terminal**. Run:
   ```bash
   python3 run_agent.py --brief portfolio --format all
   ```
   - Terminal prints live portfolio metrics, concentration flags, and generated report links.
2. Open the generated **interactive dark-mode HTML report** in Google Chrome (`sample_reports/sample_report.html`):
   - Hover over the **Risk Assessment Cards**:
     - 🚨 `CRITICAL: Single-Asset Concentration (>35%) — BTC at 55.1%`
     - ⚠️ `WARNING: Volatility Anomaly — High-beta asset swing`
     - ⚠️ `CAUTION: Stablecoin Buffer — Reserves under 10%`
   - Scroll down to the **Structured Financial Brief**:
     - *1. What Happened*
     - *2. What to Watch*
     - *3. Actionable Next Steps*

#### 🗣️ Spoken Voiceover:
> *"For quantitative research outside the chat UI, PortfolioPulse runs as a standalone CLI. 
>
> Our multi-factor risk engine immediately audits asset concentration, volatility anomalies, and cash reserve depletion, generating this institutional dark-mode HTML dashboard with structured 'What Happened, What to Watch, and Risk' commentary."*

---

### 🟢 SCENE 5: Zero-Key Judge Experience & Wrap-Up (01:10 – 01:22)

#### 🖥️ What Displays Onscreen:
1. In Terminal, run the test suite:
   ```bash
   python3 -m unittest discover -s tests -v
   ```
   - Shows: `Ran 15 tests in 0.037s ... OK`.
2. Switch to the **GitHub Repository** page (`https://github.com/EAZITECH1/binance-portfolio-pulse`):
   - Scroll through the clean README, 8 documented MCP tools, and sample reports.
3. Fade to end title screen:
   - **Binance PortfolioPulse AI**
   - *Built for the Binance Agent OS Hackathon (Track A)*
   - GitHub: `github.com/EAZITECH1/binance-portfolio-pulse`

#### 🗣️ Spoken Voiceover:
> *"Finally, the entire repository offers a zero-key judge experience with 15 passing hermetic unit tests running in 37 milliseconds.
>
> Binance PortfolioPulse AI: Autonomous, non-custodial, and 100% verified Binance intelligence. Check it out on GitHub!"*

---

## 📋 Pro-Recording Tips & Checklist

1. **Window Setup Before Recording**:
   - **Left / Main:** Claude Desktop (set font size to 110% or Zoom In with `Cmd + +` so judges can easily read the chat).
   - **Right / Background:** VS Code with `mcp_config.json` and Terminal with clear prompt.
   - **Browser Tab:** Pre-open `sample_reports/sample_report.html` so you can switch to it with a single `Cmd + Tab`.
2. **Claude Desktop Preparation**:
   - Make sure your Claude Desktop is open and has the hammer icon showing the 8 tools.
   - Pre-copy the two prompts into a notepad so you can paste them instantly without typing errors.
3. **Pacing & Energy**:
   - Speak at an energetic, confident, conversational tempo.
   - Total word count is ~200 words, which naturally speaks in ~75 seconds.
4. **Resolution**:
   - Record in **1920x1080 (1080p, 60 FPS)** for crisp text rendering.
