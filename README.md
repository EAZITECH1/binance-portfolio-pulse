# 📊 Binance PortfolioPulse AI

> **Autonomous Market Intelligence, Web3 Social Content Creator & Portfolio Risk Agent powered by Binance Agent OS (Track A – Data Analysis)**

[![Binance Agent OS](https://img.shields.io/badge/Binance-Agent%20OS-F0B90B?logo=binance&logoColor=black)](https://developers.binance.com)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol%202024--11--05-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/tests-15%2F15%20passing-success)](tests/)
[![X (Twitter) Video](https://img.shields.io/badge/X-Public%20Video%20Demo-black?logo=x&logoColor=white)](https://x.com/eazitechh/status/2097412347803435075)

Binance PortfolioPulse AI is an agentic finance and social intelligence system built for the **Binance Agent OS Mini Hackathon (Track A – Agent Creation, Data Analysis theme)**.

> 🎥 **Public Video Demo & Walkthrough on X (Twitter):**  
> 🔗 [https://x.com/eazitechh/status/2097412347803435075](https://x.com/eazitechh/status/2097412347803435075)

It bridges the **Binance Model Context Protocol (MCP)** server and Binance Exchange APIs with an autonomous editorial workflow. Whenever a connected agent (Claude, Codex, Cursor, Grok) or creator asks for *"a market update"*, the agent analyzes real-time market-wide momentum, pulls verified Binance market indicators, evaluates risk vulnerabilities, and drafts ready-to-post, Cointelegraph/CoinMarketCap-style tweets and threads.

---

## 🎯 The Problem

Crypto users, traders, and content creators are bombarded daily by rapid headlines, fragmented charts, price spikes, and volatile social media noise. Making sense of the market is broken:
- **Information Fragmentation:** Critical data is scattered across exchange order books, external pricing trackers, wallet balances, and disparate news feeds.
- **Impulsive Reactions Without Context:** Traders react to localized price pumps without understanding exchange-wide liquidity, underlying market momentum, or their personal exposure.
- **The Web3 Writer's Dilemma:** Web3 journalists, social media managers, and crypto creators spend hours manually pulling numbers from exchange interfaces, calculating percentage deltas, verifying active ticker status, and formatting tweets—often struggling to keep updates factual, timely, and compliant with Twitter/X character limits.

---

## 💡 The Solution

**Binance PortfolioPulse AI** bridges the **Binance Agent OS Model Context Protocol (MCP)** and live Binance exchange feeds into an autonomous, non-custodial intelligence and editorial engine:
1. **Evidence-Based Market Synthesis:** Directly queries official Binance MCP tools and composite marketing feeds to track genuine exchange-wide volume ($8B+ USD), calculate true market cap rankings (including $USDT and $USDC), and identify active top movers while filtering out halted or illiquid pairs.
2. **Quantitative Risk & Portfolio Intelligence:** Continuously audits portfolio health by flagging single-asset concentration (>35%), 24h volatility anomalies, and cash reserve depletion.
3. **Scenario-Based Decision Support:** Delivers clear, institutional commentary (*"What Happened / What to Watch / Risks"*) to help users navigate market conditions without executing trades or giving financial advice.

---

## ✍️ How PortfolioPulse Empowers Web3 Content Writers & Creators

In fast-paced Web3 media, timing and factual accuracy are everything. PortfolioPulse acts as an **autonomous editorial co-pilot** specifically designed for crypto writers, analysts, and social media managers:

- **⚡ Instant 1-Click Publishing:** Transforms complex, multi-asset Binance spot data and ticker metrics into ready-to-post, Cointelegraph and CoinMarketCap-style updates in seconds.
- **📏 Strict Twitter/X Character Compliance:** Automatically formats and validates single tweets and 3-part threads (`1/3`, `2/3`, `3/3`) to ensure every post strictly adheres to Twitter's 280-character limit—eliminating manual editing and word trimming.
- **🛡️ Truthful Editorial Phrasing:** Decouples individual asset movements from broad market trends. For example, if Bitcoin is down -0.3% while selective altcoins rally, the agent truthfully phrases it as *"Bitcoin holds near $78,500 (-0.3%) as selective altcoins decouple"* rather than falsely claiming Bitcoin is "advancing".
- **🔍 100% Verified On-Exchange Data:** Automatically filters out delisted, halted, or frozen pairs (`status: BREAK`) and leveraged tokens, protecting writers from publishing misleading stats or false pump data.
- **🧵 Automated Multi-Part Editorial Threads:** Structures posts into proven editorial flows:
  - **Tweet 1 (The Hook):** Macro headline and market sentiment.
  - **Tweet 2 (The Data):** Verified top gainers, laggards, and tracked Binance spot volume.
  - **Tweet 3 (The Takeaway):** Actionable summary, community engagement question, and relevant tickers/hashtags.

---

## 🌟 Key Features

- 🌐 **Real-Time Market-Wide Intelligence:** Tracks top movers, volume leaders, and macro sentiment across a customizable watchlist (BTC, ETH, SOL, BNB, SUI, NEAR, AVAX, DOGE, PEPE), using 100% genuine live Binance spot exchange data.
- 📊 **Verified Binance Market Indicators & Volume Tracking:** Ingests live 24h ticker metrics, tracked exchange volumes, top gainers, and market sentiment directly from Binance spot markets. Zero deceptive mock data.
- 🐦 **Crypto-Media Tweet & Thread Drafter:** Generates publication-ready social posts in crisp crypto-journalism style. Supports single tweets and 3-part threads, strictly adhering to Twitter/X's 280-character ceiling.
- 🔌 **Native Binance Agent OS MCP Integration:** Implements the Model Context Protocol over HTTP/SSE (`https://agent.binance.com/mcp/agentic`) and interactive stdio for AI client pairing.
- 🛡️ **Quantitative Portfolio Risk Engine:** Automatically detects single-asset concentration (>35%), 24h volatility anomalies (>8%), sharp pullbacks, and depleted cash buffers.
- 🎨 **Multi-Format Reporting:** Produces Markdown briefs, dark-mode HTML dashboards, machine-readable JSON payloads, and drafted tweets.
- 🔐 **Transparent Security & Authentication:** Live market updates require zero keys. Private account portfolio tracking requires read-only Binance Spot API credentials.
- ⏰ **Cron & Daemon Ready:** Supports on-demand queries as well as automated recurring runs (`--schedule daily` or `--interval-minutes N`).

---

## 🤖 Example Prompts for Connected AI Agents

When PortfolioPulse is registered as an MCP server in **Claude Code**, **Claude Desktop**, **Cursor**, or **Codex**, users can interact with natural language prompts:

| User Prompt | Agent Action & MCP Tool Called | Resulting Output |
| :--- | :--- | :--- |
| *"Give me a quick market update on what's moving today"* | `generate_market_brief()` | Standalone brief with macro trends, top gainers/losers, and market indicators. |
| *"Draft a tweet about today's crypto market"* | `draft_tweet(topic="market", style="single")` | Ready-to-post Cointelegraph-style tweet under 280 characters with stats and hashtags. |
| *"Create a 3-part thread breaking down today's altcoin action and market data"* | `draft_tweet(topic="market", style="thread")` | Numbered 3-tweet thread (`1/3`, `2/3`, `3/3`) with hook, data, and takeaway. |
| *"Summarize my Binance portfolio and draft a tweet about it"* | `get_account_balances()` + `draft_tweet(topic="portfolio")` | Comprehensive valuation, risk flags, and an allocation update post. |
| *"Show me top market movers and volume across the crypto watchlist"* | `get_market_overview()` | Real-time Binance spot prices, 24h gainers/losers, and aggregated quote volume. |
| *"What are the top 10 coins by market cap?"* | `get_top_by_market_cap(limit=10)` | Live market cap rankings, USD valuations, prices, and 24h change from Binance official feed. |
| *"Why is ETH moving today, and what should I watch?"* | `get_ticker_24hr("ETHUSDT")` + `ask_portfoliopulse()` | Real-time ETH spot metrics, 24h trading range, Binance volume, why it's moving, and key levels to watch. |

---

## 🏗️ Architecture

```
                                  +---------------------------------------+
                                  |         Binance Agent OS              |
                                  |    (https://agent.binance.com)        |
                                  +---------------------------------------+
                                                      |
                                          (Model Context Protocol)
                                                      |
                                                      v
+-----------------------------------------------------------------------------------------+
|                                Binance PortfolioPulse AI                                |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   | Ingestion: Binance MCP Client • REST API • Price Feed Provider • Mock Engine    |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Analytics & Intelligence: Portfolio Valuation • Market Brief • Multi-Factor Risk |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Social Content Creation: Cointelegraph-Style Tweet & Thread Drafter (<=280 chr) |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Multi-Format Exporters: Markdown Brief • HTML Dashboard • JSON • Tweet Markdown |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
                    |                                                     |
                    v                                                     v
          [sample_market_tweet.md]                              [sample_market_brief.md]
        Ready-to-Post Viral Thread                            Comprehensive Intelligence
```

---

## 🚀 Quickstart (Real-Time Live Binance Market Intelligence)

PortfolioPulse connects directly to live Binance spot markets out-of-the-box with standard Python 3.9+ and **zero required external packages**:

```bash
# 1. Clone the repository
git clone https://github.com/EAZITECH1/binance-portfolio-pulse.git
cd binance-portfolio-pulse

# 2. Generate a live market brief and draft a ready-to-post tweet thread from real Binance prices
python3 run_agent.py --brief market --draft-tweet --tweet-style thread

# 3. Ask any question about real market momentum or asset movements
python3 run_agent.py --ask "Give me an executive market briefing on Bitcoin and Solana"

# 4. (Optional) For private wallet portfolio reports, add read-only keys to .env:
#    python3 run_agent.py --brief portfolio --format all --output-dir reports/
```

### Market Brief & Tweet Output Example (Live Binance Exchange Data):

```text
[2026-09-12 03:16:11] [INFO ] Generating Market Intelligence Brief in [API] mode...
[2026-09-12 03:16:19] [INFO ] Market brief markdown -> reports/binance_market_brief_2026-09-12.md
[2026-09-12 03:16:19] [INFO ] Market brief json -> reports/binance_market_brief_2026-09-12.json
[2026-09-12 03:16:19] [INFO ] Drafted market tweet saved -> reports/binance_market_brief_2026-09-12_tweet.md

----------------------------------------------------------------
 🐦 DRAFTED MARKET TWEET (THREAD - 3 post(s)):
----------------------------------------------------------------
[1/3] (227/280 chars):
🚨 MARKET PULSE: Crypto consolidates with Bitcoin steady near $77,306 (+0.5%).

Range-bound action dominates today, while $LSK (+51.2%) & $VTHO (+24.9%) highlights selective rotation.

Here's what you need to know today 🧵👇 (1/3)

[2/3] (204/280 chars):
📊 KEY MOVERS & BINANCE SPOT ACTIVITY:

• $LSK: +51.2%
• $VTHO: +24.9%
• Tracked 24h Volume: $9.6B USD
• Watchlist Avg Movement: +1.89%

Spot order flow shows sustained liquidity across active pairs. (2/3)

[3/3] (186/280 chars):
💡 TAKEAWAY: Selective rotation underway as traders await directional macro breakout.

Are you accumulating dips into stables or waiting for confirmation?

#Bitcoin #Crypto #Binance (3/3)
----------------------------------------------------------------
```

---

---

## ⚡ Two Ways to Use PortfolioPulse

PortfolioPulse is designed to be versatile: you can interact with it conversationally inside an AI interface or run it independently as an automated CLI tool.

| Usage Mode | How It Works | Best For |
| :--- | :--- | :--- |
| **1. Claude Desktop / MCP Mode** | PortfolioPulse registers as an MCP server. Claude calls tools dynamically to answer questions, analyze risk, and draft tweets. | Interactive research, conversational inquiries, custom content drafting. |
| **2. Standalone CLI Mode** | Run commands from terminal or cron (`--brief`, `--ask`, `--draft-tweet`, `--schedule`). Optional LLM enhancement via Claude Sonnet. | Scheduled daily reports, background daemons, headless automation, zero-setup testing. |

---

## 🖥️ Claude Desktop Setup (Step-by-Step)

Connect PortfolioPulse to **Claude Desktop** to chat directly with your portfolio and market intelligence engine using natural language.

### Step 1: Locate your Claude Desktop configuration file
Find or create `claude_desktop_config.json` on your system:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add the PortfolioPulse MCP server entry
Add the following entry under `mcpServers` (replace `/ABSOLUTE/PATH/TO/binance-portfolio-pulse` with the actual path to your cloned repository):

```json
{
  "mcpServers": {
    "binance-portfoliopulse": {
      "command": "python3",
      "args": ["-m", "src.connectors.mcp_client", "--stdio"],
      "env": {
        "PYTHONPATH": "/ABSOLUTE/PATH/TO/binance-portfolio-pulse"
      }
    }
  }
}
```

> **Tip:** You can also copy this directly from [`mcp_config.json`](mcp_config.json). If `python3` is in a virtual environment, specify the full path to that python binary.

### Step 3: Restart Claude Desktop
Completely quit Claude Desktop (**Cmd + Q** on macOS or **File > Exit** on Windows) and relaunch the app.

### Step 4: Verify MCP tool discovery
Open any chat in Claude Desktop. Look for the 🔨 **hammer (tools) icon** near the input field. You should see `binance-portfoliopulse` listed with all 8 exposed tools active and ready!

### Step 5: Try these prompt examples in Claude Desktop
Type any of these prompts directly into Claude:

1. 💬 *"Use PortfolioPulse to give me a market update and draft a tweet about it."*
2. 💬 *"What is my highest risk asset in PortfolioPulse?"*
3. 💬 *"Analyze today's top gainers and market overview on Binance."*
4. 💬 *"Create a 3-part Twitter thread breaking down today's altcoin action and Binance spot volume."*
5. 💬 *"Why is ETH moving today, and what should I watch?"*

---

## 🔌 Callable MCP Tools Exposed

PortfolioPulse exposes 8 high-level and granular tools conforming to the Model Context Protocol standard:

1. `ask_portfoliopulse(prompt)`: Central natural language orchestrator that answers free-form questions about portfolio health, risk exposures, and market conditions.
2. `get_top_by_market_cap(limit=10, include_stables=True)`: Live market capitalization rankings, circulating supply, and prices sourced directly and exclusively from Binance's composite market data endpoint, including major stablecoins (USDT, USDC).
3. `get_market_overview(watchlist=[...])`: Ingests real-time prices, 24h change %, volume, and top movers across custom or default tokens directly from Binance spot tickers.
4. `generate_market_brief(watchlist=[...])`: Generates a cohesive market update (executive summary + 5 structured analytical points) from verified Binance exchange data.
5. `draft_tweet(topic="market"|"portfolio", style="single"|"thread")`: Drafts publication-ready crypto-journalism posts strictly under 280 characters.
6. `get_account_balances()`: Fetches spot balances and asset values.
7. `get_ticker_24hr(symbol)`: Rolling 24h price, high/low, and volume statistics for a given pair.
8. `get_klines(symbol, interval, limit)`: Historical candlesticks for technical trend and moving average analysis.

---

## 💻 Standalone CLI Usage & LLM Synthesis

When running outside Claude Desktop, PortfolioPulse operates as a powerful standalone CLI with an optional LLM generation layer allowing anyone to plug in their own preferred model and API key.

```bash
# 1. Ask natural language questions via CLI
python3 run_agent.py --ask "What is my highest risk asset?"
python3 run_agent.py --ask "Give me a quick market summary and draft a tweet"
python3 run_agent.py --ask "Why is ETH moving today, and what should I watch?"

# 2. Market Intelligence & Social Content
python3 run_agent.py --brief market                                         # Market brief
python3 run_agent.py --brief market --draft-tweet --tweet-style single      # Single tweet (<=280 chars)
python3 run_agent.py --brief market --draft-tweet --tweet-style thread      # 3-tweet thread
python3 run_agent.py --brief market --watchlist "BTC,ETH,SOL,BNB,SUI,AVAX"  # Custom watchlist

# 3. Portfolio Risk Analysis & Dashboards
python3 run_agent.py --brief portfolio --format all                         # Full portfolio report (MD, HTML, JSON)
python3 run_agent.py --brief portfolio --draft-tweet                        # Portfolio report + drafted tweet

# 4. Connectivity Modes
python3 run_agent.py --mode mock --brief market                             # Zero-key offline demonstration
python3 run_agent.py --mode mcp --brief market                              # Live Binance Agent OS MCP
python3 run_agent.py --mode api --brief market                              # Direct Binance Exchange REST

# 5. Recurring Automation & Daemon Scheduling
python3 run_agent.py --brief market --schedule daily                        # Automated daily brief
python3 run_agent.py --brief market --interval-minutes 60                   # Hourly recurring market monitor
```

### 🧠 Optional LLM-Powered Generation (Model-Agnostic)
By default, PortfolioPulse uses an intelligent deterministic financial rule engine that requires **zero external LLM API keys**.

To upgrade standalone CLI outputs with your own generative model (e.g. Claude, GPT, DeepSeek, or any custom endpoint):
1. In your `.env` file, simply provide your model name and key:
   ```bash
   LLM_API_KEY=your_api_key_here
   LLM_MODEL=your-model-name-here
   # Optional custom endpoint / proxy URL:
   # LLM_BASE_URL=https://api.your-provider.com/v1
   ```
2. Any market brief, portfolio summary, or drafted tweet will automatically synthesize commentary using your specified model. If left unconfigured or set to the default placeholder, PortfolioPulse gracefully executes via its built-in quantitative financial reasoning engine.

---

## 📋 Sample Outputs in Repository

| Category | File Link | Description |
| :--- | :--- | :--- |
| **Market Brief** | [`sample_reports/sample_market_brief.md`](sample_reports/sample_market_brief.md) | Macro overview, top movers, and network indicator highlights. |
| **Market Tweet (Thread)** | [`sample_reports/sample_market_tweet.md`](sample_reports/sample_market_tweet.md) | Ready-to-post 3-part thread breaking down market movers & network stats. |
| **Portfolio Tweet (Single)** | [`sample_reports/sample_portfolio_tweet.md`](sample_reports/sample_portfolio_tweet.md) | Single post sharing 24h P&L and asset allocation under 280 chars. |
| **HTML Dashboard** | [`sample_reports/sample_report.html`](sample_reports/sample_report.html) | Interactive dark-mode dashboard with asset allocation bars and risk cards. |
| **Markdown Report** | [`sample_reports/sample_report.md`](sample_reports/sample_report.md) | Full personal portfolio report with quantitative risk badges. |
| **Structured JSON** | [`sample_reports/sample_market_brief.json`](sample_reports/sample_market_brief.json) | Complete machine-readable market data payload for bots. |

---

## 🧪 Automated Testing

Run the test suite with Python's built-in `unittest` runner:

```bash
python3 -m unittest discover -s tests -v
```

**13 unit tests covering:**
- Character count validation on single tweets (`<= 280` chars)
- Thread sequence validation (`1/3`, `2/3`, `3/3`)
- Watchlist market overview, top movers ranking, and volume aggregation
- Market brief synthesis independent of portfolio data
- Portfolio valuation, asset allocation, and concentration risk thresholds

---

## 📁 Repository Structure

```
binance-portfolio-pulse/
├── .env.example              # Template environment file
├── .gitignore                # Protects secrets, cache, and logs
├── LICENSE                   # MIT License
├── README.md                 # Project guide and documentation
├── SUBMISSION.md             # Hackathon Track A submission & social copy
├── requirements.txt          # Optional dependencies (dotenv, requests)
├── mcp_config.json           # Model Context Protocol server configuration
├── run_agent.py              # Central CLI and recurring scheduling daemon
├── src/
│   ├── config.py             # Configuration loader with fallback
│   ├── connectors/
│   │   ├── mcp_client.py     # Binance Agent OS MCP client & stdio bridge
│   │   ├── binance_api.py    # Binance REST API connector with resilient SSL handling
│   │   └── mock_provider.py  # Realistic multi-asset simulation engine
│   ├── analytics/
│   │   ├── market_brief.py   # Macro market intelligence generator
│   │   ├── portfolio.py      # Valuation and allocation calculations
│   │   ├── market_trends.py  # 24h momentum, 7d SMA, volatility
│   │   ├── risk_analyzer.py  # Multi-factor risk engine (concentration, swings)
│   │   └── ai_summary.py     # Plain-language beginner financial synthesizer
│   ├── content/
│   │   └── tweet_drafter.py  # Crypto-media tweet and thread generator (<=280 chars)
│   ├── reporters/
│   │   ├── markdown_reporter.py
│   │   ├── html_reporter.py
│   │   └── json_reporter.py
│   └── utils/
│       └── logger.py         # Formatted terminal logger
├── sample_reports/           # Pre-rendered sample reports and tweets
│   ├── sample_market_brief.md
│   ├── sample_market_brief.json
│   ├── sample_market_tweet.md
│   ├── sample_portfolio_tweet.md
│   ├── sample_report.html
│   ├── sample_report.md
│   └── sample_report.json
└── tests/
    ├── test_content.py       # Tweet length and market brief tests
    ├── test_price_feeds.py   # Market overview, watchlist, and MCP catalog tests
    └── test_analytics.py     # Portfolio and risk engine tests
```


---

## 🛡️ Security & Non-Custodial Safety

- **Zero External Withdrawal Scope:** The Binance Agent OS MCP server architecture enforces strict sub-account boundaries and cannot execute withdrawals to external wallets.
- **Credential Protection:** Secrets are never hardcoded and loaded strictly from local `.env` which is excluded via `.gitignore`.
- **Read-Only Operation:** Even when using Direct REST mode, the agent functions entirely with read-only scopes.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
