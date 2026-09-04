# 📊 Binance PortfolioPulse AI

> **Autonomous Crypto Portfolio & Risk Intelligence Agent powered by Binance Agent OS (Track A – Data Analysis)**

[![Binance Agent OS](https://img.shields.io/badge/Binance-Agent%20OS-F0B90B?logo=binance&logoColor=black)](https://developers.binance.com)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol%202024--11--05-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/tests-passing-success)](tests/)

Binance PortfolioPulse AI is an intelligent data analysis agent built for the **Binance Agent OS Mini Hackathon (Track A)**. It connects to Binance via the **Model Context Protocol (MCP)** and Exchange APIs, analyzes held assets and 7-day candlestick trends, computes multi-factor quantitative risk flags, and translates complex financial data into plain-language daily intelligence reports.

---

## 🌟 Key Features

- 🔌 **Native Binance Agent OS Integration:** Direct connectivity with the official Binance MCP server (`https://agent.binance.com/mcp/agentic`) over HTTP/SSE.
- 🛡️ **Multi-Factor Risk Engine:** Automatically detects single-asset concentration (>35%), 24h volatility anomalies (>8%), sharp pullbacks, and depleted cash buffers.
- 💡 **Plain-Language AI Financial Intelligence:** Synthesizes portfolio performance into clear, conversational summaries designed for beginners and non-traders without confusing technical jargon.
- 🎨 **Multi-Format Reporting:** Generates GitHub-flavored Markdown (`.md`), interactive responsive dark-mode HTML dashboards (`.html`), and machine-readable JSON (`.json`) with a single command.
- ⚡ **Zero-Key Judge Experience:** Bundles a high-fidelity mock engine so hackathon reviewers can test the entire pipeline end-to-end without needing Binance API credentials.
- ⏰ **Scheduled & Cron-Ready:** Supports on-demand CLI queries as well as automated daemon loops (`--schedule daily` or `--interval-minutes N`).
- 🔒 **Bank-Grade Safety:** Connects strictly to isolated Agentic sub-accounts with zero external withdrawal permissions.

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
|   | Data Ingestion Layer: MCP Client • REST API Connector • High-Fidelity Mock      |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Quantitative Analytics Engine: Valuation • Asset Allocation • 7d Momentum (SMA) |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Risk & Vulnerability Analyzer: Concentration • Volatility • Cash Cushion Buffer  |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Plain-Language AI Synthesizer: Conversational Headlines • Actionable Advice     |   |
|   +---------------------------------------------------------------------------------+   |
|                                             |                                           |
|                                             v                                           |
|   +---------------------------------------------------------------------------------+   |
|   | Multi-Format Exporters: Markdown Report (.md) • HTML Dashboard • JSON Payload   |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
                                              |
                   +--------------------------+--------------------------+
                   |                                                     |
                   v                                                     v
          [sample_report.html]                                  [sample_report.md]
     Interactive Dark-Mode Dashboard                       Clean GitHub-Flavored Report
```

---

## 🚀 Quickstart (10-Second Demo)

PortfolioPulse runs with standard Python 3.9+ with **zero mandatory external dependencies**:

```bash
# 1. Clone the repository
git clone https://github.com/EAZITECH1/binance-portfolio-pulse.git
cd binance-portfolio-pulse

# 2. Run the agent in zero-key demonstration mode
python3 run_agent.py --mode mock --format all --output-dir sample_reports/
```

### Terminal Output Example:

```text
[2026-09-04 18:16:18] [INFO ] Starting Binance PortfolioPulse analysis in [MOCK] mode...
[2026-09-04 18:16:18] [INFO ] Portfolio Valued: $71,980.53 USD across 6 assets.
[2026-09-04 18:16:18] [INFO ] Risk Evaluated: Level = [HIGH] (Score 10/10, 4 flags).
[2026-09-04 18:16:18] [INFO ] Markdown report generated -> sample_reports/binance_portfolio_2026-09-04.md
[2026-09-04 18:16:18] [INFO ] HTML dashboard generated -> sample_reports/binance_portfolio_2026-09-04.html
[2026-09-04 18:16:18] [INFO ] JSON data payload generated -> sample_reports/binance_portfolio_2026-09-04.json

================================================================
 🚀 BINANCE PORTFOLIOPULSE AI - DAILY ANALYSIS SUMMARY
================================================================
 • Total Portfolio Value:   $71,980.53
 • 24h Net Movement:        +$1,464.58 (+2.08%)
 • Risk Assessment:         HIGH (Score: 10/10)
 • Active Risk Flags:       4 identified
 • Cash / Stable Reserve:   $3,850.00 (5.3%)

 💡 Executive Takeaway:
   "Your portfolio climbed 2.1% (+$1,464.58) today, powered by a surge in SOL (+9.4%)."
----------------------------------------------------------------
 📁 Generated Reports:
   [MD] sample_reports/binance_portfolio_2026-09-04.md
   [HTML] sample_reports/binance_portfolio_2026-09-04.html
   [JSON] sample_reports/binance_portfolio_2026-09-04.json
================================================================
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

### Method 3: Direct API & Sub-Account Mode (Optional)
If you prefer direct Binance API connectivity:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your read-only Spot API keys:
   ```ini
   AGENT_MODE=api
   BINANCE_API_KEY=your_read_only_key_here
   BINANCE_API_SECRET=your_read_only_secret_here
   ```
   *(Note: Never enable withdrawal permissions. The agent only requires read permissions).*

---

## 💻 CLI Usage & Commands

```bash
# Generate all report formats (Markdown, HTML, JSON) in mock mode
python3 run_agent.py --mode mock --format all

# Run using live Binance MCP Server
python3 run_agent.py --mode mcp --format all

# Run using direct Binance REST API
python3 run_agent.py --mode api --format md

# Generate report into custom folder
python3 run_agent.py --output-dir /path/to/my_reports/

# Run in automated daily daemon mode (runs every 24 hours)
python3 run_agent.py --schedule daily

# Run on custom recurring interval (e.g., every 60 minutes)
python3 run_agent.py --interval-minutes 60

# Enable verbose network and mathematical calculation logs
python3 run_agent.py -v
```

---

## 📋 Sample Reports Preview

Pre-generated reports are included in the repository for review:

| Report Format | File Link | Description |
| :--- | :--- | :--- |
| **HTML Dashboard** | [`sample_reports/sample_report.html`](sample_reports/sample_report.html) | Responsive dark-mode UI with asset allocation bars, risk cards, and Binance styling. |
| **Markdown Report** | [`sample_reports/sample_report.md`](sample_reports/sample_report.md) | Formatted tables, risk badges, and actionable next steps. |
| **Structured JSON** | [`sample_reports/sample_report.json`](sample_reports/sample_report.json) | Complete machine-readable payload for bots and pipelines. |

---

## 🧪 Automated Testing

Run the automated test suite with Python's built-in `unittest` runner:

```bash
python3 -m unittest discover -s tests -v
```

All 5 core unit tests validate portfolio valuation, asset allocation percentages, risk flag threshold detection, and report rendering integrity.

---

## 📁 Repository Structure

```
binance-agent-os-reporter/
├── .env.example              # Template environment file
├── .gitignore                # Protects secrets, cache, and logs
├── LICENSE                   # MIT License
├── README.md                 # Project guide and documentation
├── DEMO_SCRIPT.md            # 60–90s demo video recording storyboard
├── SUBMISSION.md             # Hackathon Track A submission & social copy
├── requirements.txt          # Optional package dependencies
├── mcp_config.json           # Model Context Protocol server configuration
├── run_agent.py              # CLI entrypoint and scheduling daemon
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration loader with fallback
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── mcp_client.py     # Binance Agent OS MCP client & stdio bridge
│   │   ├── binance_api.py    # Binance REST API connector with SSL fallback
│   │   └── mock_provider.py  # Realistic multi-asset simulation engine
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── portfolio.py      # Valuation and allocation calculations
│   │   ├── market_trends.py  # 24h momentum, 7d SMA, volatility
│   │   ├── risk_analyzer.py  # Multi-factor risk engine (concentration, swings)
│   │   └── ai_summary.py     # Plain-language beginner financial synthesizer
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── markdown_reporter.py
│   │   ├── html_reporter.py
│   │   └── json_reporter.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py         # Formatted terminal logger
├── sample_reports/           # Pre-rendered sample reports
│   ├── sample_report.html
│   ├── sample_report.md
│   └── sample_report.json
└── tests/
    ├── __init__.py
    └── test_analytics.py     # Automated test suite
```

---

## 🛡️ Security & Non-Custodial Safety

- **Zero External Withdrawal Scope:** The Binance Agent OS MCP server architecture enforces strict sub-account boundaries and cannot execute withdrawals to external wallets.
- **Credential Protection:** Secrets are never hardcoded and loaded strictly from local `.env` which is excluded via `.gitignore`.
- **Read-Only Operation:** Even when using Direct REST mode, the agent functions entirely with read-only scopes.

---

## 🏆 Hackathon Details

- **Event:** Binance Agent OS Mini Hackathon
- **Track:** Track A – Agent Creation (Data Analysis Theme)
- **Deadline:** Sept 8, 2026, 23:59 UTC
- **Video Demo Script:** See [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) for scene-by-scene script.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
