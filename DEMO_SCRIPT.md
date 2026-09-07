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
| 00:00 - 00:12    | Title Slide & Introduction                                           |
|                  | Web3 creator + quant use case with Binance Agent OS MCP badge.       |
| 00:12 - 00:28    | "Give me a market update" (Market Intelligence Brief)                |
|                  | MCP pulls top gainers (SUI, SOL) & price feed indicators (BNB, ETH gas). |
| 00:28 - 00:45    | "Draft a tweet about today's market" (Viral Tweet & Thread Drafter)  |
|                  | Generates publication-ready post (<280 chars) & 3-part thread.       |
| 00:45 - 01:03    | Portfolio Risk Intelligence & Dark-Mode HTML Dashboard               |
|                  | Interactive HTML dashboard: allocation bar, risk flags, and actions. |
| 01:03 - 01:15    | Autonomous Scheduling & Closing Call to Action                       |
|                  | Terminal showing cron/daemon loop + Binance Hackathon submission.    |
+------------------+----------------------------------------------------------------------+
```

---

### Scene 1: Introduction & The Web3 Creator Problem (00:00 – 00:12)
* **Visual:** Clean split-screen showing VS Code, Terminal, and the **Binance PortfolioPulse AI** logo banner.
* **On-Screen Text Overlay:** *"Binance PortfolioPulse AI — Agent OS Market Intelligence & Content Creator"*
* **Voiceover:**
  > "Crypto moves 24/7. Whether you're a Web3 content creator looking to publish timely market updates or a trader tracking portfolio risk, manual analysis takes hours. Meet **Binance PortfolioPulse AI**—an autonomous agent built on Binance Agent OS that turns live exchange and market price feed data into instant market briefs, viral tweets, and risk reports."

---

### Scene 2: Live Market Brief via Binance MCP (00:12 – 00:28)
* **Visual:** Terminal window. Type and execute:
  ```bash
  python3 run_agent.py --brief market
  ```
* **On-Screen Action:**
  Terminal streams market intelligence:
  - Top gainers: $SUI (+14.7%), $SOL (+9.4%)
  - Price feed indicators: BNB Chain 4.2M daily txs (3.0 Gwei), Ethereum gas, DeFi TVL ($94.5B)
  - Whale flow signal: $320M net exchange outflow.
* **Voiceover:**
  > "Ask any connected agent—like Claude or Codex—for a market update, and PortfolioPulse queries Binance Agent OS MCP and market price feeds. In seconds, it synthesizes macro momentum, top movers, and network activity into a structured intelligence brief."

---

### Scene 3: Cointelegraph-Style Tweet & Thread Drafter (00:28 – 00:45)
* **Visual:** Execute:
  ```bash
  python3 run_agent.py --brief market --draft-tweet --tweet-style thread
  ```
* **On-Screen Action:**
  Highlight drafted 3-part thread formatted under 280 characters with verified stats, emojis, and hashtags (`#Bitcoin #Solana #Binance`).
* **Voiceover:**
  > "Next, ask the agent to draft a tweet. Using editorial heuristics inspired by Cointelegraph and CoinMarketCap, it generates publication-ready single posts or numbered threads—strictly validated under 280 characters with verified stats and hashtags ready for X."

---

### Scene 4: Personal Portfolio Risk & Dark-Mode Dashboard (00:45 – 01:03)
* **Visual:** Switch smoothly to the browser displaying `sample_reports/sample_report.html` in dark mode.
  - Hover over the **Asset Allocation visual progress bar**.
  - Highlight the **Risk Flags cards** (BTC concentration >50% warning + suggested action).
* **Voiceover:**
  > "For personal portfolios, our quantitative risk engine flags over-concentration and volatility spikes, presenting everything in this sleek, responsive dark-mode HTML dashboard inspired by Binance's design language."

---

### Scene 5: Scheduling & Hackathon Wrap-Up (01:03 – 01:15)
* **Visual:** Quick return to terminal showing `--schedule daily` daemon mode, followed by final screen with GitHub repo link `github.com/EAZITECH1/binance-portfolio-pulse`.
* **Voiceover:**
  > "PortfolioPulse runs on-demand or as an autonomous daily daemon. It exposes 7 MCP tools, has 100% test coverage, and works zero-key out of the box. Check out our open-source repo on GitHub!"

---

## 🛠️ Recording Checklist for Presenter

1. **Terminal Setup:**
   - Font size: 16–18pt (high readability on mobile & 1080p).
   - Shell: Clear screen (`clear`) before each command.
2. **Browser Setup:**
   - Open `sample_reports/sample_report.html` in full screen Chrome/Brave.
   - Zoom level: 110%–125% for clean layout presentation.
3. **Audio:**
   - Use crisp microphone audio; speak at an engaging, steady pace.
4. **Export Specs:**
   - Resolution: 1920x1080 (1080p) or 4K.
   - Framerate: 30 or 60 FPS.
   - Format: MP4 (H.264).
