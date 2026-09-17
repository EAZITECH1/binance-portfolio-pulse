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
from datetime import datetime, timezone
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
from src.analytics.futures import FuturesAnalyzer
from src.analytics.predictive import PredictiveBalanceEngine


def generate_portfolio_report(
    mode: str = "api",
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

    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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
            if not raw_balances or (isinstance(raw_balances, dict) and "error" in raw_balances):
                print("\n" + "=" * 64)
                print(" 🔐 BINANCE API CREDENTIALS REQUIRED FOR PORTFOLIO ANALYSIS")
                print("=" * 64)
                print(" Real portfolio tracking requires read-only Binance Spot API keys.")
                print(" 1. Add BINANCE_API_KEY and BINANCE_API_SECRET to your .env file.")
                print(" 2. Ensure only 'Read Info' or 'Enable Reading' permissions are granted.")
                print("\n 💡 Want real-time Binance market intelligence without credentials?")
                print("    Run: python3 run_agent.py --brief market")
                print("=" * 64 + "\n")
                return {}
            source_label = "Binance Agent OS (MCP Server)"

            # Batch fetch tickers for all non-stable held assets in 1 MCP tool call
            held_non_stables = [
                item.get("asset", "").upper()
                for item in raw_balances
                if item.get("asset", "").upper() not in ("USDT", "USDC", "FDUSD")
            ]
            symbols_to_fetch = [f"{a}USDT" for a in held_non_stables]
            try:
                batch_res = mcp.call_tool("get_ticker_24hr", {"symbols": symbols_to_fetch})
                batch_map = {t["symbol"]: t for t in batch_res if isinstance(t, dict) and "symbol" in t}
            except Exception:
                batch_map = {}

            for asset in held_non_stables:
                sym = f"{asset}USDT"
                ticker = batch_map.get(sym)
                if not ticker:
                    logger.info(f"No active Binance spot pair for {sym}. Valued at $0.00.")
                    ticker = {"symbol": sym, "lastPrice": "0.00", "priceChangePercent": "0.00"}
                tickers[sym] = ticker
                if float(ticker.get("lastPrice", 0.0)) > 0:
                    try:
                        klines = mcp.call_tool("get_klines", {"symbol": sym, "limit": 7})
                        trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)
                    except Exception as e:
                        logger.warning(f"Failed to fetch klines for {sym}: {e}")

        elif mode == "api":
            logger.info(f"Connecting to Binance REST API at {config.base_url}...")
            api = BinanceAPIClient(
                api_key=config.api_key,
                api_secret=config.api_secret,
                base_url=config.base_url,
            )
            source_label = "Binance Direct Exchange API"
            
            # If keys provided, fetch live account; otherwise prompt transparently
            if config.api_key and config.api_secret:
                try:
                    raw_balances = api.get_account_balances()
                except Exception as e:
                    logger.error(f"Failed to fetch private balances: {e}.")
                    raise ConnectionError(f"Failed to fetch private Binance account balances: {e}")
            else:
                logger.warning("No Binance API credentials configured in .env.")
                print("\n" + "=" * 64)
                print(" 🔐 BINANCE API CREDENTIALS REQUIRED FOR PORTFOLIO ANALYSIS")
                print("=" * 64)
                print(" Real portfolio tracking requires read-only Binance Spot API keys.")
                print(" 1. Add BINANCE_API_KEY and BINANCE_API_SECRET to your .env file.")
                print(" 2. Ensure only 'Read Info' or 'Enable Reading' permissions are granted.")
                print("\n 💡 Want real-time Binance market intelligence without credentials?")
                print("    Run: python3 run_agent.py --brief market")
                print("=" * 64 + "\n")
                return {}

            # Batch fetch 24hr tickers for all non-stable assets in 1 single HTTP request
            held_non_stables = [
                item.get("asset", "").upper()
                for item in raw_balances
                if item.get("asset", "").upper() not in ("USDT", "USDC", "FDUSD")
            ]
            symbols_to_fetch = [f"{a}USDT" for a in held_non_stables]
            batch_res = api.get_tickers_batch(symbols_to_fetch)
            batch_map = {t["symbol"]: t for t in batch_res if isinstance(t, dict) and "symbol" in t}

            for asset in held_non_stables:
                sym = f"{asset}USDT"
                ticker = batch_map.get(sym)
                if not ticker:
                    logger.info(f"No active Binance spot pair for {sym}. Valued at $0.00.")
                    ticker = {"symbol": sym, "lastPrice": "0.00", "priceChangePercent": "0.00"}
                tickers[sym] = ticker
                if float(ticker.get("lastPrice", 0.0)) > 0:
                    try:
                        klines = api.get_klines(sym, interval="1d", limit=7)
                        trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, ticker, klines)
                    except Exception as e:
                        logger.warning(f"Failed to fetch klines for {sym}: {e}")

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

    # 2. Futures Derivatives Data Ingestion & Analysis
    raw_futures = None
    mark_prices = []
    api_client_for_futures = None
    if mode in ("api", "mcp"):
        api_client_for_futures = BinanceAPIClient(api_key=config.api_key, api_secret=config.api_secret, base_url=config.base_url)

    if api_client_for_futures and config.api_key and config.api_secret:
        try:
            raw_futures = api_client_for_futures.get_futures_account()
            if raw_futures and isinstance(raw_futures, dict):
                raw_futures["is_active"] = True
                raw_futures["status_message"] = "Futures trading active"
        except Exception as e:
            logger.info(f"Live futures account query: {e}. (User does not use Futures / permissions not enabled).")
            raw_futures = {
                "is_active": False,
                "status_message": "Futures not in use / not enabled on this API key",
                "totalMarginBalance": "0.00",
                "totalWalletBalance": "0.00",
                "totalUnrealizedProfit": "0.00",
                "totalMaintMargin": "0.00",
                "totalInitialMargin": "0.00",
                "availableBalance": "0.00",
                "positions": [],
            }
    elif mode == "mock":
        raw_futures = MockDataProvider().get_futures_account()
        if raw_futures and isinstance(raw_futures, dict):
            raw_futures["is_active"] = True
            raw_futures["status_message"] = "Futures sandbox simulation active"
    else:
        raw_futures = {
            "is_active": False,
            "status_message": "Futures not in use",
            "totalMarginBalance": "0.00",
            "totalWalletBalance": "0.00",
            "totalUnrealizedProfit": "0.00",
            "totalMaintMargin": "0.00",
            "totalInitialMargin": "0.00",
            "availableBalance": "0.00",
            "positions": [],
        }

    try:
        if api_client_for_futures:
            mark_prices = api_client_for_futures.get_futures_mark_prices()
        elif mode == "mock":
            mark_prices = MockDataProvider().get_futures_mark_prices()
    except Exception as e:
        logger.debug(f"Futures mark prices query: {e}")
        if mode == "mock":
            mark_prices = MockDataProvider().get_futures_mark_prices()

    futures_summary = FuturesAnalyzer.analyze(raw_futures, mark_prices=mark_prices)
    if futures_summary.is_active and (futures_summary.total_margin_balance_usd > 0 or futures_summary.positions):
        logger.info(
            f"Futures Derivatives Analyzed: Margin Balance = ${futures_summary.total_margin_balance_usd:,.2f}, Margin Ratio = {futures_summary.margin_ratio_pct:.1f}% ({futures_summary.risk_status})."
        )
    else:
        logger.info("Futures Derivatives: Not in use (No active futures positions or permissions).")

    # 3. Portfolio Quantitative Valuation
    summary = PortfolioAnalyzer.analyze(raw_balances, tickers)
    logger.info(
        f"Portfolio Valued: ${summary.total_value_usd:,.2f} USD across {summary.asset_count} assets."
    )

    # 4. Predictive Future Balance Engine (Real 30d Historical Klines & Beta Analysis)
    held_symbols = [f"{p.asset}USDT" for p in summary.positions if not p.is_stablecoin and p.current_price > 0]
    all_syms = list(set(["BTCUSDT"] + held_symbols))
    klines_batch = {}
    if api_client_for_futures:
        try:
            klines_batch = api_client_for_futures.get_historical_klines_batch(all_syms, limit=30)
        except Exception as e:
            logger.debug(f"Historical klines batch query: {e}")
    elif mode == "mock":
        klines_batch = MockDataProvider().get_historical_klines_batch(all_syms, limit=30)

    predictive_report = PredictiveBalanceEngine.forecast(summary, futures_summary, klines_batch)
    logger.info(
        f"Predictive Balance Modeled: 7D Expected = ${predictive_report.projected_7d_base_usd:,.2f}, 7D 95% VaR = ${predictive_report.var_95_7d_usd:,.2f} ({predictive_report.var_95_7d_pct:.1f}%)."
    )

    # 5. Risk & Volatility Assessment
    risk = RiskAnalyzer.evaluate(
        summary=summary,
        trends=trends,
        concentration_threshold=config.risk_concentration_threshold,
        volatility_threshold=config.risk_volatility_threshold,
        min_stablecoin_buffer=config.min_stablecoin_buffer,
        futures_summary=futures_summary,
        predictive_report=predictive_report,
    )
    logger.info(
        f"Risk Evaluated: Level = [{risk.risk_level}] (Score {risk.overall_score}/10, {len(risk.flags)} flags)."
    )

    # 6. Plain-Language AI Synthesis
    ai_summary = AISummaryGenerator.generate(
        summary=summary,
        risk=risk,
        trends=trends,
        llm_api_key=config.llm_api_key,
        llm_model=config.llm_model,
        anthropic_api_key=config.anthropic_api_key,
        gemini_api_key=config.gemini_api_key,
        openai_api_key=config.openai_api_key,
        futures_summary=futures_summary,
        predictive_report=predictive_report,
    )

    # 7. Render Requested Formats
    generated_files = {}

    if "md" in formats or "all" in formats:
        md_content = MarkdownReporter.render(
            summary, risk, trends, ai_summary, source_label,
            futures_summary=futures_summary,
            predictive_report=predictive_report,
        )
        md_path = out_path / f"{prefix}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        generated_files["md"] = str(md_path)
        logger.info(f"Markdown report generated -> {md_path}")

    if "html" in formats or "all" in formats:
        html_content = HTMLReporter.render(
            summary, risk, trends, ai_summary, source_label,
            futures_summary=futures_summary,
            predictive_report=predictive_report,
        )
        html_path = out_path / f"{prefix}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_files["html"] = str(html_path)
        logger.info(f"HTML dashboard generated -> {html_path}")

    if "json" in formats or "all" in formats:
        json_content = JSONReporter.render(
            summary, risk, trends, ai_summary, source_label,
            futures_summary=futures_summary,
            predictive_report=predictive_report,
        )
        json_path = out_path / f"{prefix}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_content)
        generated_files["json"] = str(json_path)
        logger.info(f"JSON data payload generated -> {json_path}")

    # Optional: Draft portfolio tweet if requested
    if draft_tweet:
        draft = TweetDrafter.draft_portfolio_tweet(
            summary,
            ai_summary,
            style=tweet_style,
            llm_api_key=config.llm_api_key,
            llm_model=config.llm_model,
        )
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
    if futures_summary and futures_summary.is_active and (futures_summary.total_margin_balance_usd > 0 or futures_summary.positions):
        print(f" • Futures Derivatives:     ${futures_summary.total_margin_balance_usd:,.2f} Margin ({futures_summary.risk_status})")
    else:
        print(" • Futures Derivatives:     Not in use (Spot-only mode)")
    print(f"\n 💡 Executive Takeaway:\n   \"{ai_summary.headline}\"")
    print("-" * 64)
    print(" 📁 Generated Reports:")
    for fmt, fpath in generated_files.items():
        print(f"   [{fmt.upper()}] {fpath}")
    print("=" * 64 + "\n")

    return generated_files


def generate_market_brief_report(
    mode: str = None,
    output_dir: str = "reports",
    watchlist: List[str] = None,
    draft_tweet: bool = False,
    tweet_style: str = "single",
) -> Dict[str, str]:
    """
    Generates a standalone market intelligence brief + optional tweet draft.
    """
    import json
    active_mode = mode or config.mode
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefix = f"binance_market_brief_{date_str}"

    logger.info(f"Generating Market Intelligence Brief in [{active_mode.upper()}] mode...")
    brief = MarketBriefGenerator.generate(watchlist=watchlist, mode=active_mode)

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
        draft = TweetDrafter.draft_market_tweet(
            brief,
            style=tweet_style,
            llm_api_key=config.llm_api_key,
            llm_model=config.llm_model,
        )
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
        help="Data ingestion mode: 'api' (default, real Binance live data), 'mcp' (Binance Agent OS MCP), 'mock' (test fixtures)",
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
        "--ask",
        type=str,
        default=None,
        help="Ask PortfolioPulse a natural language question (e.g. 'What is my highest risk asset?')",
    )
    parser.add_argument(
        "--orderbook",
        type=str,
        default=None,
        metavar="SYMBOL",
        help="Inspect real-time Binance order book depth, bids/asks, and spread (e.g. --orderbook BTCUSDT)",
    )
    parser.add_argument(
        "--trades",
        type=str,
        default=None,
        metavar="SYMBOL",
        help="Inspect past spot trade fill history, prices, and commissions on any pair (Read-Only) (e.g. --trades BTCUSDT)",
    )
    parser.add_argument(
        "--transfers",
        action="store_true",
        help="Inspect Binance wallet deposit and withdrawal history and net funding",
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

    # If --orderbook is specified, inspect order book and exit
    if args.orderbook:
        from src.analytics.order_book import OrderBookAnalyzer
        sym = args.orderbook.strip().upper()
        if not (sym.endswith("USDT") or sym.endswith("BTC") or sym.endswith("FDUSD") or sym.endswith("USDC")):
            sym = f"{sym}USDT"
        
        mcp = BinanceMCPClient()
        raw_depth = mcp.call_tool("get_order_book", {"symbol": sym, "limit": 20})
        
        print("\n" + "=" * 64)
        print(f" 📊 BINANCE ORDER BOOK DEPTH & SPREAD ANALYTICS ({sym})")
        print("=" * 64)
        print(f" • Best Bid:          ${raw_depth.get('best_bid', 0):,.4f}")
        print(f" • Best Ask:          ${raw_depth.get('best_ask', 0):,.4f}")
        print(f" • Mid Price:         ${raw_depth.get('mid_price', 0):,.4f}")
        print(f" • Bid/Ask Spread:    ${raw_depth.get('spread_usd', 0):.6f} ({raw_depth.get('spread_bps', 0):.2f} bps)")
        print(f" • Total Depth (USD): ${raw_depth.get('total_liquidity_usd', 0):,.2f}")
        print(f"   ├─ Bid Depth:      ${raw_depth.get('bid_depth_usd', 0):,.2f}")
        print(f"   └─ Ask Depth:      ${raw_depth.get('ask_depth_usd', 0):,.2f}")
        print(f" • Imbalance Ratio:   {raw_depth.get('order_imbalance_ratio', 1.0):.3f}")
        print(f" • Market Quality:    {raw_depth.get('market_regime', 'NORMAL')}")
        print("-" * 64)
        print(" Top 5 Asks (Sell Wall):")
        for a in reversed(raw_depth.get("asks_sample", [])):
            print(f"   ${a['price']:,.4f} | Qty: {a['quantity']:>10.4f} | Value: ${a['total_usd']:>12,.2f}")
        print(f"   ─── SPREAD: ${raw_depth.get('spread_usd', 0):.6f} ({raw_depth.get('spread_bps', 0):.2f} bps) ───")
        print(" Top 5 Bids (Buy Wall):")
        for b in raw_depth.get("bids_sample", []):
            print(f"   ${b['price']:,.4f} | Qty: {b['quantity']:>10.4f} | Value: ${b['total_usd']:>12,.2f}")
        print("=" * 64 + "\n")
        return

    # If --trades is specified, inspect past spot trade fills on that pair (read-only)
    if args.trades:
        sym = args.trades.strip().upper()
        if not (sym.endswith("USDT") or sym.endswith("BTC") or sym.endswith("FDUSD") or sym.endswith("USDC")):
            sym = f"{sym}USDT"
        mcp = BinanceMCPClient()
        tr_data = mcp.call_tool("get_my_trades", {"symbol": sym, "limit": 50})
        
        print("\n" + "=" * 64)
        print(f" 📋 BINANCE PAST SPOT TRADE FILL HISTORY (READ-ONLY) ({sym})")
        print("=" * 64)
        print(f" • Total Filled Orders:   {tr_data.get('total_trades', 0)}")
        print(f" • Total Traded Volume:   ${tr_data.get('total_volume_usd', 0):,.2f}")
        print(f"   ├─ Buy Volume:         ${tr_data.get('total_buy_volume_usd', 0):,.2f} ({tr_data.get('total_quantity_bought', 0)} {sym})")
        print(f"   └─ Sell Volume:        ${tr_data.get('total_sell_volume_usd', 0):,.2f} ({tr_data.get('total_quantity_sold', 0)} {sym})")
        print(f" • Average Fill Prices:   Buy: ${tr_data.get('avg_buy_price', 0):,.2f} | Sell: ${tr_data.get('avg_sell_price', 0):,.2f}")
        fees = tr_data.get("total_fees_by_asset", {})
        if fees:
            print(" • Total Commissions:     " + ", ".join(f"{v:.4f} {k}" for k, v in fees.items()))
        print("-" * 64)
        trades_list = tr_data.get("trades", [])
        if trades_list:
            print(" Recent Filled Orders:")
            for t in trades_list[:10]:
                side_color = "🟢 BUY " if t["side"] == "BUY" else "🔴 SELL"
                maker_tag = "Maker" if t["is_maker"] else "Taker"
                print(f"   [{t['datetime_utc']}] {side_color} {t['quantity']:>10.4f} @ ${t['price']:>10,.2f} (${t['quote_quantity']:>10,.2f}) | Fee: {t['commission']} {t['commission_asset']} ({maker_tag})")
        else:
            print(f" No past filled orders recorded on Binance for {sym}.")
        print("=" * 64 + "\n")
        return

    # If --transfers is specified, inspect deposits and withdrawals
    if args.transfers:
        mcp = BinanceMCPClient()
        dep_data = mcp.call_tool("get_deposit_history", {"limit": 50})
        wit_data = mcp.call_tool("get_withdraw_history", {"limit": 50})

        print("\n" + "=" * 64)
        print(" 💳 BINANCE WALLET TRANSFERS (DEPOSITS & WITHDRAWALS)")
        print("=" * 64)
        print(f" • Total Deposits:    {dep_data.get('total_deposits', 0)} transfers")
        print(f" • Total Withdrawals: {wit_data.get('total_withdrawals', 0)} transfers")
        print("-" * 64)
        print(" 📥 Recent Deposits (Incoming Funding):")
        deps = dep_data.get("deposits", [])
        if deps:
            for d in deps[:5]:
                print(f"   • [{d['datetime_utc']}] +{d['amount']:>10.4f} {d['coin']:<6} via {d.get('network') or 'N/A'} [{d['status']}]")
        else:
            print("   (No deposits recorded)")
        print("-" * 64)
        print(" 📤 Recent Withdrawals (Outgoing Transfers):")
        wits = wit_data.get("withdrawals", [])
        if wits:
            for w in wits[:5]:
                fee_txt = f" | Fee: {w['fee']} {w['coin']}" if w.get("fee", 0) > 0 else ""
                print(f"   • [{w['datetime_utc']}] -{w['amount']:>10.4f} {w['coin']:<6} via {w.get('network') or 'N/A'}{fee_txt} [{w['status']}]")
        else:
            print("   (No withdrawals recorded)")
        print("=" * 64 + "\n")
        return

    # If --ask is specified, run the orchestrator and exit
    if args.ask:
        mcp_client = BinanceMCPClient()
        result = mcp_client.ask_portfoliopulse(prompt=args.ask, mode=args.mode)
        print("\n" + "=" * 64)
        print(" 🤖 BINANCE PORTFOLIOPULSE AI - NATURAL LANGUAGE ANSWER")
        print("=" * 64)
        print(f" ❓ Question: {args.ask}")
        print("-" * 64)
        print(f" 💡 Answer:\n{result.get('answer', '')}\n")
        if "actionable_takeaways" in result:
            print(" 📌 Actionable Takeaways:")
            for item in result["actionable_takeaways"]:
                print(f"   • {item}")
        print("=" * 64 + "\n")
        return

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
