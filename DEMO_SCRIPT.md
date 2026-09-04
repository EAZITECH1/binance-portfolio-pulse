# 🎬 Binance PortfolioPulse AI — Demo Video Script & Storyboard

**Hackathon Track:** Binance Agent OS Mini Hackathon (Track A – Agent Creation, Data Analysis)  
**Target Video Duration:** 75 Seconds (60–90s limit)  
**Presenter:** Screen recording with voiceover (Terminal + Browser)

---

## ⏱️ Video Breakdown & Storyboard

```
+------------------+----------------------------------------------------------------------+
| Timestamp        | On-Screen Action & Visual                                            |
+------------------+----------------------------------------------------------------------+
| 00:00 - 00:12    | Title Slide & Terminal Intro                                         |
|                  | Show project repository with Binance Agent OS badge.                 |
| 00:12 - 00:28    | Connecting Binance Agent OS via MCP & Zero-Key Setup                 |
|                  | Run `claude mcp add` / inspect `mcp_config.json` & run agent CLI.   |
| 00:28 - 00:48    | Real-Time Ingestion & Plain-Language AI Synthesis                    |
|                  | Terminal outputs live valuation, 24h P&L, risk score, and summary.  |
| 00:48 - 01:05    | Interactive Dark-Mode HTML Dashboard Walkthrough                     |
|                  | Switch to Chrome: show allocation bar, risk flags, and actions.      |
| 01:05 - 01:15    | Autonomous Scheduling & Closing Call to Action                       |
|                  | Terminal showing cron/daemon loop + Binance Hackathon submission.    |
+------------------+----------------------------------------------------------------------+
```

---

### Scene 1: Introduction & Problem Statement (00:00 – 00:12)
* **Visual:** Full-screen title card with **Binance PortfolioPulse AI** logo, followed by a clean split-screen showing VS Code and Terminal.
* **On-Screen Text Overlay:** *"Binance PortfolioPulse AI — Agent OS Track A"*
* **Voiceover:**
  > "Crypto portfolios move 24/7, but most traders and non-technical holders struggle to parse sudden price swings, hidden concentration risks, and complex wallet data. Welcome to **Binance PortfolioPulse AI**—an autonomous agent built on Binance Agent OS that transforms raw exchange data into clear, plain-language intelligence."

---

### Scene 2: Binance Agent OS MCP Integration (00:12 – 00:28)
* **Visual:** Terminal window. Highlight `mcp_config.json` and show connecting to the official Binance Agent OS MCP Server (`https://agent.binance.com/mcp/agentic`).
* **On-Screen Action:**
  Type and execute:
  ```bash
  python3 run_agent.py --mode mock --format all
  ```
* **Voiceover:**
  > "Using the Model Context Protocol, our agent seamlessly bridges to Binance Agent OS. It connects to isolated Agentic sub-accounts with zero external withdrawal risk, ensuring bank-grade safety. For hackathon judges, our zero-key mode lets anyone clone and test the agent instantly with one simple terminal command."

---

### Scene 3: Intelligent Analysis & Risk Detection (00:28 – 00:48)
* **Visual:** Terminal streams execution logs:
  - Ingestion of holdings (BTC, ETH, SOL, BNB, NEAR, USDT)
  - Market momentum calculation from 7-day klines
  - Risk engine evaluating concentration and volatility
  - Clean summary card printed in terminal.
* **Voiceover:**
  > "In seconds, the agent calculates full portfolio valuation, 24-hour P&L, and technical momentum. But it doesn't stop at numbers: our quantitative risk engine automatically flags critical vulnerabilities—like a 55% over-concentration in Bitcoin and sharp volatility in Solana—before generating an executive summary a beginner can understand."

---

### Scene 4: The Interactive HTML & Markdown Dashboard (00:48 – 01:05)
* **Visual:** Switch smoothly to the browser displaying `sample_reports/sample_report.html` in dark mode.
  - Hover over the **Asset Allocation visual bar**.
  - Scroll past the **AI Financial Intelligence banner**.
  - Highlight the **Risk Flags cards** (Critical concentration alert + suggested actions).
* **Voiceover:**
  > "The output is multi-format: clean JSON for bot integrations, Markdown for messaging webhooks, and this stunning, responsive HTML dashboard inspired by Binance's design system. Non-traders get immediate clarity on why their balance moved, what drove the gains, and concrete steps to protect capital."

---

### Scene 5: Autonomous Scheduling & Wrap-Up (01:05 – 01:15)
* **Visual:** Quick return to terminal showing `--schedule daily` or cron mode, then final screen with GitHub repo link and Binance Agent OS Hackathon Track A badge.
* **Voiceover:**
  > "PortfolioPulse runs on-demand or as a daily automated daemon. It's modular, secure, and production-ready for the Binance Agent OS ecosystem. Check out our open-source repo on GitHub!"

---

## 🛠️ Recording Checklist for Presenter

1. **Terminal Setup:**
   - Font size: 16–18pt (high readability on mobile & 1080p).
   - Shell: Clear screen (`clear`) before running `python3 run_agent.py --mode mock --format all`.
2. **Browser Setup:**
   - Open `sample_reports/sample_report.html` in full screen Chrome or Brave.
   - Zoom level: 110%–125% for clean text presentation.
3. **Audio:**
   - Use crisp microphone audio; speak at an engaging, steady pace.
4. **Export Specs:**
   - Resolution: 1920x1080 (1080p) or 4K.
   - Framerate: 30 or 60 FPS.
   - Format: MP4 (H.264).
