# 📊 Binance PortfolioPulse AI

> **Autonomous Market Intelligence, Web3 Social Content Creator & Portfolio Risk Agent powered by Binance Agent OS (Track A – Data Analysis)**

[![Binance Agent OS](https://img.shields.io/badge/Binance-Agent%20OS-F0B90B?logo=binance&logoColor=black)](https://developers.binance.com)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol%202024--11--05-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/tests-12%2F12%20passing-success)](tests/)

Binance PortfolioPulse AI is an agentic finance and social intelligence system built for the **Binance Agent OS Mini Hackathon (Track A – Agent Creation, Data Analysis theme)**.

It bridges the **Binance Model Context Protocol (MCP)** server, Exchange APIs, and on-chain metrics with an autonomous editorial workflow. Whenever a connected agent (Claude, Codex, Cursor, Grok) or creator asks for *"a market update"*, the agent analyzes market-wide momentum, pulls multi-chain activity, evaluates risk vulnerabilities, and drafts ready-to-post, Cointelegraph/CoinMarketCap-style tweets and threads.

---

## 🌟 Key Features

- 🌐 **Market-Wide Intelligence Briefs:** Tracks top movers, volume leaders, and macro sentiment across a customizable watchlist (BTC, ETH, SOL, BNB, SUI, NEAR, AVAX, DOGE, PEPE), independent of portfolio holdings.
- ⛓️ **On-Chain & Multi-Chain Pulse:** Ingests gas metrics (BNB Chain, Ethereum), 24h DEX volumes, active wallet counts, DeFi Total Value Locked (TVL), and institutional whale exchange flows.
- 🐦 **Crypto-Media Tweet & Thread Drafter:** Generates publication-ready social posts in crisp crypto-journalism style. Supports single tweets and 3-part threads, strictly adhering to Twitter/X's 280-character ceiling.
- 🔌 **Native Binance Agent OS MCP Integration:** Implements the Model Context Protocol over HTTP/SSE (`https://agent.binance.com/mcp/agentic`) and interactive stdio for AI client pairing.
- 🛡️ **Quantitative Portfolio Risk Engine:** Automatically detects single-asset concentration (>35%), 24h volatility anomalies (>8%), sharp pullbacks, and depleted cash buffers.
- 🎨 **Multi-Format Reporting:** Produces Markdown briefs, dark-mode HTML dashboards, machine-readable JSON payloads, and drafted tweets.
- ⚡ **Zero-Key Judge Experience:** Bundles a high-fidelity mock engine so hackathon reviewers can test the entire pipeline end-to-end without needing Binance API keys.
- ⏰ **Cron & Daemon Ready:** Supports on-demand queries as well as automated recurring runs (`--schedule daily` or `--interval-minutes N`).

---

## 🤖 Example Prompts for Connected AI Agents

When PortfolioPulse is registered as an MCP server in **Claude Code**, **Claude Desktop**, **Cursor**, or **Codex**, users can interact with natural language prompts:

| User Prompt | Agent Action & MCP Tool Called | Resulting Output |
| :--- | :--- | :--- |
| *"Give me a quick market update on what's moving today"* | `generate_market_brief()` | Standalone brief with macro trends, top gainers/losers, and on-chain pulse. |
| *"Draft a tweet about today's crypto market"* | `draft_tweet(topic="market", style="single")` | Ready-to-post Cointelegraph-style tweet under 280 characters with stats and hashtags. |
| *"Create a 3-part thread breaking down today's altcoin action and on-chain metrics"* | `draft_tweet(topic="market", style="thread")` | Numbered 3-tweet thread (`1/3`, `2/3`, `3/3`) with hook, data, and takeaway. |
| *"Summarize my Binance portfolio and draft a tweet about it"* | `get_account_balances()` + `draft_tweet(topic="portfolio")` | Comprehensive valuation, risk flags, and an allocation update post. |
| *"What's the gas fee and transaction volume on BNB Chain right now?"* | `get_onchain_snapshot()` | Real-time BNB Chain gas in Gwei, daily transactions, and DEX volume. |

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
|   | Ingestion: Binance MCP Client • REST API • On-Chain Provider • Benchmark Mock   |   |
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

## 🚀 Quickstart (Zero-Key Demonstration)

PortfolioPulse runs out-of-the-box with standard Python 3.9+ and **zero required external packages**:

```bash
# 1. Clone the repository
git clone https://github.com/EAZITECH1/binance-portfolio-pulse.git
cd binance-portfolio-pulse

# 2. Generate a market brief and draft a ready-to-post tweet thread
python3 run_agent.py --brief market --draft-tweet --tweet-style thread

# 3. Generate a full portfolio analysis report with dark-mode HTML dashboard
python3 run_agent.py --brief portfolio --format all --output-dir reports/
```

### Market Brief & Tweet Output Example:

```text
[2026-09-07 03:19:14] [INFO ] Generating Market Intelligence Brief in [MOCK] mode...
[2026-09-07 03:19:14] [INFO ] Market brief markdown -> sample_reports/binance_market_brief_2026-09-07.md
[2026-09-07 03:19:14] [INFO ] Drafted market tweet saved -> sample_reports/binance_market_brief_2026-09-07_tweet.md

----------------------------------------------------------------
 🐦 DRAFTED MARKET TWEET (THREAD - 3 post(s)):
----------------------------------------------------------------
[1/3] (223/280 chars):
🚨 MARKET PULSE: Crypto pushes higher as Bitcoin holds steady above $63,450 (+3.1%).

Selective altcoins are leading the charge today, with SUI and $SOL seeing heavy spot inflows.

Here's what you need to know today 🧵👇 (1/3)

[2/3] (203/280 chars):
📊 KEY MOVERS & ON-CHAIN:

• $SOL: $164.80 (+9.4%)
• $SUI: +14.7%
• Total DeFi TVL: $94.5B
• Whale flow: NET_OUTFLOW ($320M)

Institutional accumulation signals remain active across major exchanges. (2/3)

[3/3] (199/280 chars):
💡 TAKEAWAY: Capital is rotating into high-beta layer-1s while BTC builds liquidity above support.

Are you taking profits into stables or riding the momentum?

#Bitcoin #Solana #Crypto #Binance (3/3)
----------------------------------------------------------------
```

---

## 🔑 Binance Agent OS & MCP Setup

Binance Agent OS standardizes how AI agents communicate with Binance's trading infrastructure without local API key management or withdrawal risks.

### Method 1: Claude Code CLI
To register the Binance MCP server in Claude Code:
```bash
claude mcp add binance-mcp-server --transport http https://agent.binance.com/mcp/agentic
```
Open your agent session (type `/mcp`) and complete the browser-based OAuth authorization to link your Binance account.

### Method 2: Claude Desktop / Cursor / Codex Configuration
Add the server definition from [`mcp_config.json`](mcp_config.json) to your AI client configuration:

```json
{
  "mcpServers": {
    "binance-agent-os": {
      "command": "python3",
      "args": ["-m", "src.connectors.mcp_client", "--stdio"]
    },
    "binance-official-hosted": {
      "url": "https://agent.binance.com/mcp/agentic"
    }
  }
}
```

### Callable MCP Tools Exposed:
1. `get_market_overview(watchlist=[...])`: Pulls prices, 24h change %, volume, and top movers across custom or default tokens.
2. `get_onchain_snapshot()`: Ingests BNB Chain gas, Ethereum gas, DEX volumes, TVL, and oracle status.
3. `generate_market_brief(watchlist=[...])`: Generates a cohesive market update (headline + 5 key points).
4. `draft_tweet(topic="market"|"portfolio", style="single"|"thread")`: Formats verified intelligence into a publication-ready post.
5. `get_account_balances()`: Fetches spot balances from Binance Agentic sub-account.
6. `get_ticker_24hr(symbol)`: Rolling 24h price and volume statistics.
7. `get_klines(symbol, interval, limit)`: Historical candlesticks for trend analysis.

---

## 💻 CLI Usage & Commands

```bash
# 1. Market Intelligence & Social Content
python3 run_agent.py --brief market                                         # Market brief
python3 run_agent.py --brief market --draft-tweet --tweet-style single      # Single tweet (<=280 chars)
python3 run_agent.py --brief market --draft-tweet --tweet-style thread      # 3-tweet thread
python3 run_agent.py --brief market --watchlist "BTC,ETH,SOL,BNB,SUI,AVAX"  # Custom watchlist

# 2. Portfolio Risk Analysis
python3 run_agent.py --brief portfolio --format all                         # Full portfolio report (MD, HTML, JSON)
python3 run_agent.py --brief portfolio --draft-tweet                        # Portfolio report + drafted tweet

# 3. Connectivity Modes
python3 run_agent.py --mode mock --brief market                             # Zero-key demonstration
python3 run_agent.py --mode mcp --brief market                              # Live Binance Agent OS MCP
python3 run_agent.py --mode api --brief market                              # Direct Binance Exchange REST

# 4. Automation & Daemon Scheduling
python3 run_agent.py --brief market --schedule daily                        # Automated daily brief
python3 run_agent.py --brief market --interval-minutes 60                   # Hourly recurring market monitor
```

---

## 📋 Sample Outputs in Repository

| Category | File Link | Description |
| :--- | :--- | :--- |
| **Market Brief** | [`sample_reports/sample_market_brief.md`](sample_reports/sample_market_brief.md) | Macro overview, top movers, and on-chain highlights. |
| **Market Tweet (Thread)** | [`sample_reports/sample_market_tweet.md`](sample_reports/sample_market_tweet.md) | Ready-to-post 3-part thread breaking down market movers & on-chain stats. |
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

**12 unit tests covering:**
- Character count validation on single tweets (`<= 280` chars)
- Thread sequence validation (`1/3`, `2/3`, `3/3`)
- Multi-chain on-chain metrics & gas fee checks
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
├── DEMO_SCRIPT.md            # 60–90s demo video recording storyboard
├── SUBMISSION.md             # Hackathon Track A submission & social copy
├── requirements.txt          # Optional dependencies (dotenv, requests)
├── mcp_config.json           # Model Context Protocol server configuration
├── run_agent.py              # Central CLI and recurring scheduling daemon
├── src/
│   ├── config.py             # Configuration loader with fallback
│   ├── connectors/
│   │   ├── mcp_client.py     # Binance Agent OS MCP client & stdio bridge
│   │   ├── binance_api.py    # Binance REST API connector with resilient SSL handling
│   │   ├── onchain_data.py   # Multi-chain gas, DEX volume, TVL, and oracle data
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
    ├── test_onchain.py       # On-chain metrics and watchlist tests
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
