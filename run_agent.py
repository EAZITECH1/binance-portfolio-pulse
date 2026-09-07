#!/usr/bin/env python3
"""
Binance PortfolioPulse AI - CLI and Scheduling Runner
Autonomous AI Agent for Binance Agent OS Mini Hackathon (Track A - Agent Creation).

Connects to Binance via Model Context Protocol (MCP) or Exchange API,
analyzes portfolio metrics, detects risk vulnerabilities, and generates
plain-language daily analysis reports in Markdown, HTML, and JSON.
"""
import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Ensure local source tree is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import config
from src.utils.logger import setup_logger, logger
from src.connectors.mock_provider import MockDataProvider
from src.connectors.binance_api import BinanceAPIClient
from src.connectors.mcp_client import BinanceMCPClient
from src.analytics.portfolio import PortfolioAnalyzer
from src.analytics.market_trends import MarketTrendAnalyzer, MarketTrendHighlight
from src.analytics.risk_analyzer import RiskAnalyzer
from src.analytics.ai_summary import AISummaryGenerator
from src.analytics.market_brief import MarketBriefGenerator
from src.content.tweet_drafter import TweetDrafter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.html_reporter import HTMLReporter
from src.reporters.json_reporter import JSONReporter


def generate_portfolio_report(
    mode: str = "mock",
    output_dir: str = "reports",
    formats: List[str] = None,
    output_filename_prefix: str = None,
    draft_tweet: bool = False,
    tweet_style: str = "single",
) -> Dict[str, str]:
    """
    Executes an end-to-end portfolio analysis and generates requested report files.
    Returns a dictionary of generated filepaths keyed by format.
    """
    formats = formats or ["md", "html", "json"]
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    prefix = output_filename_prefix or f"binance_portfolio_{date_str}"

    logger.info(f"Starting Binance PortfolioPulse analysis in [{mode.upper()}] mode...")

    # 1. Data Ingestion
    raw_balances = []
    source_label = "Binance Agent OS (MCP)"
    tickers: Dict[str, Dict[str, Any]] = {}
    trends: Dict[str, MarketTrendHighlight] = {}

    try:
        if mode == "mcp":
            logger.info(f"Connecting to Binance Agent OS MCP at {config.mcp_endpoint}...")
            mcp = BinanceMCPClient(
                endpoint_url=config.mcp_endpoint,
                auth_token=config.mcp_auth_token,
                fallback_to_api=True,
                api_client=BinanceAPIClient(
                    api_key=config.api_key,
                    api_secret=config.api_secret,
                    base_url=config.base_url,
                ),
            )
            raw_balances = mcp.call_tool("get_account_balances", {})
            source_label = "Binance Agent OS (MCP Server)"

            # Fetch market data for each held asset
            for item in raw_balances:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                try:
                    ticker = mcp.call_tool("get_ticker_24hr", {"symbol": sym})
                    tickers[sym] = ticker
                    klines = mcp.call_tool("get_klines", {"symbol": sym, "limit": 7})
                    trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)
                except Exception as e:
                    logger.warning(f"MCP ticker query failed for {sym}: {e}. Using benchmark market data.")
                    mock = MockDataProvider()
                    ticker = mock.get_ticker_24hr(sym)
                    tickers[sym] = ticker
                    klines = mock.get_klines_history(sym, limit=7)
                    trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)

        elif mode == "api":
            logger.info(f"Connecting to Binance REST API at {config.base_url}...")
            api = BinanceAPIClient(
                api_key=config.api_key,
                api_secret=config.api_secret,
                base_url=config.base_url,
            )
            source_label = "Binance Direct Exchange API"
            
            # If keys provided, fetch live account; otherwise fallback gracefully
            if config.api_key and config.api_secret:
                try:
                    raw_balances = api.get_account_balances()
                except Exception as e:
                    logger.error(f"Failed to fetch private balances: {e}. Using demonstration balance set.")
                    mock = MockDataProvider()
                    raw_balances = mock.get_account_balances()
                    source_label = "Binance REST (Live Market + Demo Portfolio)"
            else:
                logger.info("No API keys configured. Using demonstration portfolio with live market prices.")
                mock = MockDataProvider()
                raw_balances = mock.get_account_balances()
                source_label = "Binance REST (Live Market + Demo Portfolio)"

            # Fetch live market data
            for item in raw_balances:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                try:
                    ticker = api.get_ticker_24hr(sym)
                    tickers[sym] = ticker
                    klines = api.get_klines(sym, interval="1d", limit=7)
                    trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)
                except Exception as e:
                    logger.warning(f"Live ticker query failed for {sym}: {e}. Using benchmark market data.")
                    mock = MockDataProvider()
                    ticker = mock.get_ticker_24hr(sym)
                    tickers[sym] = ticker
                    klines = mock.get_klines_history(sym, limit=7)
                    trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)

        else:  # 'mock'
            logger.info("Operating in Mock / Sandbox demo mode (Zero keys required).")
            mock = MockDataProvider()
            raw_balances = mock.get_account_balances()
            source_label = "Binance Sandbox Demo (High-Fidelity Mock)"

            for item in raw_balances:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                ticker = mock.get_ticker_24hr(sym)
                tickers[sym] = ticker
                klines = mock.get_klines_history(sym, limit=7)
                trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)

    except Exception as e:
        logger.error(f"Data ingestion error: {e}. Falling back to safe mock provider.")
        mock = MockDataProvider()
        raw_balances = mock.get_account_balances()
        source_label = "Binance Fallback Sandbox"
        for item in raw_balances:
            asset = item.get("asset", "").upper()
            if asset in ("USDT", "USDC", "FDUSD"):
                continue
            sym = f"{asset}USDT"
            tickers[sym] = mock.get_ticker_24hr(sym)
            trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(
                asset, tickers[sym], mock.get_klines_history(sym)
            )

    # 2. Portfolio Quantitative Valuation
    summary = PortfolioAnalyzer.analyze(raw_balances, tickers)
    logger.info(
        f"Portfolio Valued: ${summary.total_value_usd:,.2f} USD across {summary.asset_count} assets."
    )

    # 3. Risk & Volatility Assessment
    risk = RiskAnalyzer.evaluate(
        summary=summary,
        trends=trends,
        concentration_threshold=config.risk_concentration_threshold,
        volatility_threshold=config.risk_volatility_threshold,
        min_stablecoin_buffer=config.min_stablecoin_buffer,
    )
    logger.info(
        f"Risk Evaluated: Level = [{risk.risk_level}] (Score {risk.overall_score}/10, {len(risk.flags)} flags)."
    )

    # 4. Plain-Language AI Synthesis
    ai_summary = AISummaryGenerator.generate(
        summary=summary,
        risk=risk,
        trends=trends,
        gemini_api_key=config.gemini_api_key,
        openai_api_key=config.openai_api_key,
    )

    # 5. Render Requested Formats
    generated_files = {}

    if "md" in formats or "all" in formats:
        md_content = MarkdownReporter.render(summary, risk, trends, ai_summary, source_label)
        md_path = out_path / f"{prefix}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        generated_files["md"] = str(md_path)
        logger.info(f"Markdown report generated -> {md_path}")

    if "html" in formats or "all" in formats:
        html_content = HTMLReporter.render(summary, risk, trends, ai_summary, source_label)
        html_path = out_path / f"{prefix}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_files["html"] = str(html_path)
        logger.info(f"HTML dashboard generated -> {html_path}")

    if "json" in formats or "all" in formats:
        json_content = JSONReporter.render(summary, risk, trends, ai_summary, source_label)
        json_path = out_path / f"{prefix}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_content)
        generated_files["json"] = str(json_path)
        logger.info(f"JSON data payload generated -> {json_path}")

    # Optional: Draft portfolio tweet if requested
    if draft_tweet:
        draft = TweetDrafter.draft_portfolio_tweet(summary, ai_summary, style=tweet_style)
        tweet_path = out_path / f"{prefix}_tweet.md"
        with open(tweet_path, "w", encoding="utf-8") as f:
            f.write(f"# 🐦 Ready-to-Post Portfolio Tweet ({tweet_style.upper()})\n\n{draft.formatted_preview}\n")
        generated_files["tweet"] = str(tweet_path)
        logger.info(f"Drafted tweet saved -> {tweet_path}")
        print("\n" + "-" * 64)
        print(f" 🐦 DRAFTED PORTFOLIO TWEET ({tweet_style.upper()} - {draft.total_tweets} post(s)):")
        print("-" * 64)
        for i, t in enumerate(draft.tweets):
            print(f"[{i+1}/{draft.total_tweets}] ({len(t)}/280 chars):\n{t}\n")
        print("-" * 64)

    # Terminal Highlights Summary
    pnl_sign = "+" if summary.total_24h_pnl_usd >= 0 else "-"
    print("\n" + "=" * 64)
    print(" 🚀 BINANCE PORTFOLIOPULSE AI - DAILY ANALYSIS SUMMARY")
    print("=" * 64)
    print(f" • Total Portfolio Value:   ${summary.total_value_usd:,.2f}")
    print(f" • 24h Net Movement:        {pnl_sign}${abs(summary.total_24h_pnl_usd):,.2f} ({pnl_sign}{abs(summary.total_24h_pnl_pct):.2f}%)")
    print(f" • Risk Assessment:         {risk.risk_level} (Score: {risk.overall_score}/10)")
    print(f" • Active Risk Flags:       {len(risk.flags)} identified")
    print(f" • Cash / Stable Reserve:   ${summary.stablecoin_value_usd:,.2f} ({summary.stablecoin_pct:.1f}%)")
    print(f"\n 💡 Executive Takeaway:\n   \"{ai_summary.headline}\"")
    print("-" * 64)
    print(" 📁 Generated Reports:")
    for fmt, fpath in generated_files.items():
        print(f"   [{fmt.upper()}] {fpath}")
    print("=" * 64 + "\n")

    return generated_files


def generate_market_brief_report(
    mode: str = "mock",
    output_dir: str = "reports",
    watchlist: List[str] = None,
    draft_tweet: bool = False,
    tweet_style: str = "single",
) -> Dict[str, str]:
    """
    Generates a standalone market intelligence brief + optional tweet draft.
    """
    import json
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    prefix = f"binance_market_brief_{date_str}"

    logger.info(f"Generating Market Intelligence Brief in [{mode.upper()}] mode...")
    brief = MarketBriefGenerator.generate(watchlist=watchlist, mode=mode)

    generated_files = {}

    # 1. Save Markdown
    md_path = out_path / f"{prefix}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(brief.to_markdown())
    generated_files["md"] = str(md_path)
    logger.info(f"Market brief markdown -> {md_path}")

    # 2. Save JSON
    json_path = out_path / f"{prefix}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(brief.to_dict(), indent=2))
    generated_files["json"] = str(json_path)
    logger.info(f"Market brief json -> {json_path}")

    # 3. Optional: Draft Tweet
    if draft_tweet:
        draft = TweetDrafter.draft_market_tweet(brief, style=tweet_style)
        tweet_path = out_path / f"{prefix}_tweet.md"
        with open(tweet_path, "w", encoding="utf-8") as f:
            f.write(f"# 🐦 Ready-to-Post Market Tweet ({tweet_style.upper()})\n\n{draft.formatted_preview}\n")
        generated_files["tweet"] = str(tweet_path)
        logger.info(f"Drafted market tweet saved -> {tweet_path}")
        print("\n" + "-" * 64)
        print(f" 🐦 DRAFTED MARKET TWEET ({tweet_style.upper()} - {draft.total_tweets} post(s)):")
        print("-" * 64)
        for i, t in enumerate(draft.tweets):
            print(f"[{i+1}/{draft.total_tweets}] ({len(t)}/280 chars):\n{t}\n")
        print("-" * 64)

    # Console display
    print("\n" + "=" * 64)
    print(" 🌐 BINANCE AGENT OS - MARKET INTELLIGENCE BRIEF")
    print("=" * 64)
    print(f" • Headline:  {brief.headline}")
    print(f" • Sentiment: {brief.sentiment}")
    print("\n 📌 Key Points:")
    for pt in brief.key_points[:3]:
        print(f"   - {pt}")
    print("\n 📁 Generated Files:")
    for fmt, fpath in generated_files.items():
        print(f"   [{fmt.upper()}] {fpath}")
    print("=" * 64 + "\n")

    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description="Binance PortfolioPulse AI - Agent OS Market Intelligence & Portfolio Reporter"
    )
    parser.add_argument(
        "--mode",
        choices=["mock", "mcp", "api"],
        default=config.mode,
        help="Data ingestion mode: 'mock' (default, no keys required), 'mcp' (Binance Agent OS MCP), 'api' (Direct REST API)",
    )
    parser.add_argument(
        "--brief",
        choices=["portfolio", "market"],
        default="portfolio",
        help="Type of analysis brief to produce: 'portfolio' (default) or 'market' (general market update)",
    )
    parser.add_argument(
        "--format",
        choices=["all", "md", "html", "json"],
        default="all",
        help="Output report formats to produce (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        default=config.output_dir,
        help="Directory where generated reports will be stored (default: reports/)",
    )
    parser.add_argument(
        "--draft-tweet",
        action="store_true",
        help="Draft publication-ready tweet/thread in crypto-media style",
    )
    parser.add_argument(
        "--tweet-style",
        choices=["single", "thread"],
        default="single",
        help="Style for drafted tweet: 'single' (<=280 chars) or 'thread' (3 tweets)",
    )
    parser.add_argument(
        "--watchlist",
        type=str,
        default=None,
        help="Comma-separated watchlist of assets for market brief (e.g. 'BTC,ETH,SOL,BNB,SUI')",
    )
    parser.add_argument(
        "--schedule",
        choices=["once", "daily", "hourly"],
        default="once",
        help="Run frequency: 'once' (default), 'daily' (every 24h), or 'hourly'",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=None,
        help="Custom interval in minutes between runs for daemon/cron mode",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed debug logs",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(10)

    watchlist = [w.strip().upper() for w in args.watchlist.split(",")] if args.watchlist else None

    # Determine interval for recurring schedule
    interval_seconds = None
    if args.interval_minutes:
        interval_seconds = args.interval_minutes * 60
    elif args.schedule == "daily":
        interval_seconds = 86400
    elif args.schedule == "hourly":
        interval_seconds = 3600

    formats = ["md", "html", "json"] if args.format == "all" else [args.format]

    def execute_cycle():
        if args.brief == "market":
            generate_market_brief_report(
                mode=args.mode,
                output_dir=args.output_dir,
                watchlist=watchlist,
                draft_tweet=args.draft_tweet,
                tweet_style=args.tweet_style,
            )
        else:
            generate_portfolio_report(
                mode=args.mode,
                output_dir=args.output_dir,
                formats=formats,
                draft_tweet=args.draft_tweet,
                tweet_style=args.tweet_style,
            )

    if not interval_seconds:
        # Run single on-demand execution
        execute_cycle()
    else:
        logger.info(
            f"Starting scheduler loop. Runs every {interval_seconds // 60} minutes. Press Ctrl+C to stop."
        )
        try:
            while True:
                execute_cycle()
                logger.info(f"Sleeping for {interval_seconds // 60} minutes until next cycle...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")


if __name__ == "__main__":
    main()
