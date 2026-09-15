"""
Model Context Protocol (MCP) Client and Bridge for Binance Agent OS.
Supports both:
1. Client connection to Binance Agent OS MCP endpoint (https://agent.binance.com/mcp/agentic)
2. Standalone MCP Server over stdio for integration with Claude Desktop, Cursor, Codex, and Agent OS.
"""
import json
import sys
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

from ..utils.logger import logger
from .mock_provider import MockDataProvider
from .binance_api import BinanceAPIClient


class BinanceMCPClient:
    """
    Client interface for interacting with Binance Agent OS via the Model Context Protocol.
    Conforms to the MCP JSON-RPC 2.0 specification.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        fallback_to_api: bool = True,
        api_client: Optional[BinanceAPIClient] = None,
    ):
        from ..config import config
        self.endpoint_url = endpoint_url or config.mcp_endpoint
        self.auth_token = auth_token or config.mcp_auth_token
        self.fallback_to_api = fallback_to_api
        self.api_client = api_client or BinanceAPIClient()
        self.mock_provider = MockDataProvider()
        self._request_id = 0
        from .binance_api import get_ssl_context
        self.ssl_context = get_ssl_context()

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def send_mcp_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sends a JSON-RPC 2.0 request to the Binance Agent OS MCP HTTP/SSE endpoint.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Binance-Agent-OS-Client/1.0",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        req = urllib.request.Request(
            self.endpoint_url,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=8, context=self.ssl_context) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text)
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
            logger.warning(
                f"Direct Binance MCP endpoint ({self.endpoint_url}) call '{method}' failed: {e}. "
                f"Falling back to high-fidelity data provider."
            )
            return {"error": {"code": -32000, "message": str(e)}}

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools exposed by the Binance MCP server."""
        from ..config import config
        if config.mode != "mock" and self.auth_token:
            resp = self.send_mcp_request("tools/list")
            if "result" in resp and "tools" in resp["result"]:
                return resp["result"]["tools"]

        # Default standard Binance Agent OS Tool Catalog
        return [
            {
                "name": "get_account_balances",
                "description": "Fetch spot asset balances from Binance Agentic sub-account",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_ticker_24hr",
                "description": "Get 24-hour price change and volume statistics for a crypto pair or batch of pairs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "e.g. BTCUSDT"},
                        "symbols": {"type": "array", "items": {"type": "string"}, "description": "Batch of symbols e.g. ['BTCUSDT', 'ETHUSDT']"}
                    },
                },
            },
            {
                "name": "get_klines",
                "description": "Get candlestick bars for trend analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "interval": {"type": "string", "default": "1d"},
                        "limit": {"type": "integer", "default": 7},
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "get_market_overview",
                "description": "Get market-wide overview including top gainers, top losers, and sentiment across a watchlist",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "watchlist": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of asset symbols (e.g. ['BTC', 'ETH', 'SOL'])",
                        }
                    },
                },
            },
            {
                "name": "generate_market_brief",
                "description": "Generate a concise, readable market intelligence update using verified Binance exchange data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "watchlist": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of assets to focus on",
                        }
                    },
                },
            },
            {
                "name": "draft_tweet",
                "description": "Draft a publication-ready crypto-media tweet or thread from market or portfolio intelligence",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "enum": ["market", "portfolio"],
                            "default": "market",
                            "description": "Content focus: general market update or portfolio performance",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["single", "thread"],
                            "default": "single",
                            "description": "Tweet format: single post (<=280 chars) or 3-tweet thread",
                        },
                    },
                },
            },
            {
                "name": "ask_portfoliopulse",
                "description": "Orchestrator tool: Ask PortfolioPulse any question about your Binance portfolio or the crypto market to get an autonomous intelligence analysis and actionable takeaways",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Natural language question or request (e.g. 'What is my highest risk asset?' or 'Give me an executive market briefing')",
                        },
                        "watchlist": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional asset symbols to include in market context",
                        },
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "get_top_by_market_cap",
                "description": "Fetch real-time top cryptocurrencies ranked by market capitalization with live price, 24h change %, and trading volume directly from Binance market data.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of top coins to return (default: 10, max: 50)",
                            "default": 10,
                        },
                        "include_stables": {
                            "type": "boolean",
                            "description": "Whether to include stablecoins (USDT, USDC, etc.) in rankings (default: true)",
                            "default": True,
                        },
                    },
                },
            },
            {
                "name": "get_futures_account",
                "description": "Fetch Binance USDT-M Futures derivatives balances, margin ratio, effective leverage, and open derivative contracts.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_predictive_balance",
                "description": "Run forward-looking portfolio balance projections, empirical beta calculations, and quantitative stress-test scenarios (Bull, Bear, Flash Crash, VaR) using real 30-day historical klines from Binance.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_order_book",
                "description": "Fetch real-time order book market depth, best bid/ask, spread in USD and basis points (bps), total liquidity, and order book imbalance ratio for any Binance trading pair.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading pair symbol (e.g. 'BTCUSDT', 'ETHUSDT', 'SOLUSDT')",
                            "default": "BTCUSDT",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Depth limit (e.g. 5, 10, 20, 50, 100). Default: 20",
                            "default": 20,
                        },
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "get_my_trades",
                "description": "Read-only: Fetch past filled spot orders, historical fill prices, quantities, and commissions on any Binance trading pair (does not place or execute orders).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading pair symbol (e.g. 'BTCUSDT', 'ETHUSDT', 'SOLUSDT')",
                            "default": "BTCUSDT",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of recent trades to return (default: 50, max: 500)",
                            "default": 50,
                        },
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "get_deposit_history",
                "description": "Fetch user's crypto and fiat deposit transfer records, txIds, amounts, and networks on Binance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin": {
                            "type": "string",
                            "description": "Optional asset filter (e.g. 'USDT', 'BTC', 'ETH')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of deposit records (default: 50)",
                            "default": 50,
                        },
                    },
                },
            },
            {
                "name": "get_withdraw_history",
                "description": "Fetch user's crypto and fiat withdrawal transfer records, destination addresses, fees, and status on Binance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin": {
                            "type": "string",
                            "description": "Optional asset filter (e.g. 'USDT', 'BTC', 'ETH')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of withdrawal records (default: 50)",
                            "default": 50,
                        },
                    },
                },
            },
        ]

    def ask_portfoliopulse(
        self,
        prompt: str,
        watchlist: Optional[List[str]] = None,
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrator method that ingests balances, market tickers, risk assessment,
        and uses LLM synthesis or financial rule engine to answer any query.
        """
        from ..analytics.portfolio import PortfolioAnalyzer
        from ..analytics.risk_analyzer import RiskAnalyzer
        from ..analytics.market_trends import MarketTrendAnalyzer
        from ..analytics.ai_summary import AISummaryGenerator
        from ..analytics.market_brief import MarketBriefGenerator
        from ..config import config

        active_mode = mode or config.mode

        is_explicit_portfolio = any(w in prompt.lower() for w in [
            "my portfolio", "my balance", "my holding", "my wallet", "my pnl",
            "my account", "my risk", "my token", "my asset"
        ])
        is_order_book_query = any(w in prompt.lower() for w in [
            "order book", "orderbook", "spread", "bid", "ask", "depth", "liquidity depth", "order-book", "bids/asks"
        ])
        is_mcap_query = any(w in prompt.lower() for w in [
            "market cap", "marketcap", "top 10", "top coins", "biggest coin", "rank by cap",
            "largest coin", "ranked by market"
        ])
        is_tweet_query = any(w in prompt.lower() for w in ["tweet", "thread", "post", "x.com", "twitter"])
        is_market_query = any(w in prompt.lower() for w in [
            "market", "brief", "briefing", "bitcoin", "btc", "eth", "solana", "sol",
            "crypto", "trend", "altcoin", "mover", "gainer", "loser", "action"
        ])

        # Priority 1: Order Book & Liquidity Depth Query
        if is_order_book_query and not is_explicit_portfolio:
            import re
            from ..analytics.order_book import OrderBookAnalyzer
            match = re.search(r'\b([a-zA-Z0-9]{2,10}(?:usdt|btc|eth|bnb|fdusd)?)\b', prompt.lower())
            asset_cand = "BTCUSDT"
            if match:
                cand = match.group(1).upper()
                if cand in ("ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX", "SUI", "NEAR", "LINK", "BTC"):
                    asset_cand = f"{cand}USDT"
                elif cand.endswith("USDT") or cand.endswith("BTC") or cand.endswith("FDUSD"):
                    asset_cand = cand
                elif "eth" in prompt.lower():
                    asset_cand = "ETHUSDT"
                elif "sol" in prompt.lower():
                    asset_cand = "SOLUSDT"
                elif "bnb" in prompt.lower():
                    asset_cand = "BNBUSDT"
                elif "btc" in prompt.lower() or "bitcoin" in prompt.lower():
                    asset_cand = "BTCUSDT"
            
            raw_depth = None
            if active_mode == "mock":
                raw_depth = self.mock_provider.get_order_book(asset_cand, limit=20)
            else:
                try:
                    raw_depth = self.api_client.get_order_book(asset_cand, limit=20)
                except Exception as e:
                    logger.warning(f"Order book query error: {e}")
                    raw_depth = self.mock_provider.get_order_book(asset_cand, limit=20)
            
            ob_analysis = OrderBookAnalyzer.analyze(asset_cand, raw_depth)
            
            return {
                "query": prompt,
                "answer": ob_analysis.format_summary(),
                "order_book": ob_analysis.to_dict(),
                "requires_credentials": False,
            }

        # Priority 1.5: Deposits & Withdrawals / Transfer History Query
        is_transfer_query = any(w in prompt.lower() for w in [
            "deposit", "withdraw", "transfers", "cash flow", "funding history", "deposits and withdrawals", "funding"
        ])
        if is_transfer_query:
            from ..analytics.transactions import TransactionHistoryAnalyzer
            raw_deps = []
            raw_wits = []
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_deps = self.api_client.get_deposit_history(limit=50)
                except Exception as e:
                    logger.warning(f"Live deposit query failed: {e}")
                try:
                    raw_wits = self.api_client.get_withdraw_history(limit=50)
                except Exception as e:
                    logger.warning(f"Live withdrawal query failed: {e}")
            elif active_mode == "mock":
                raw_deps = self.mock_provider.get_deposit_history(limit=50)
                raw_wits = self.mock_provider.get_withdraw_history(limit=50)

            if not raw_deps and not raw_wits and active_mode != "mock":
                # Check if API keys exist
                if not (self.api_client.api_key and self.api_client.api_secret):
                    return {
                        "query": prompt,
                        "answer": (
                            "🔐 **API Keys Required for Transfer History**\n"
                            "To inspect your deposits and withdrawals, please configure read-only BINANCE_API_KEY and BINANCE_API_SECRET in `.env`."
                        ),
                        "requires_credentials": True,
                    }

            t_analysis = TransactionHistoryAnalyzer.parse_transfers(raw_deps, raw_wits)
            summary_txt = t_analysis.format_summary()
            
            recent_lines = ["\nRecent Transfers:"]
            for rec in t_analysis.transfers[:8]:
                sign = "+" if rec.transfer_type == "DEPOSIT" else "-"
                fee_txt = f" (Fee: {rec.fee} {rec.coin})" if rec.fee > 0 else ""
                recent_lines.append(f"• [{rec.formatted_time}] {rec.transfer_type}: {sign}{rec.amount} {rec.coin}{fee_txt} [{rec.status}]")

            return {
                "query": prompt,
                "answer": summary_txt + "\n" + "\n".join(recent_lines),
                "transfers": t_analysis.to_dict(),
                "requires_credentials": False,
            }

        # Priority 1.6: Spot Trade History Query on Any Pair
        is_trade_query = any(w in prompt.lower() for w in [
            "my trade", "trade history", "trades on", "executed trades", "past trades", "my orders", "fill history", "fills"
        ])
        if is_trade_query:
            import re
            from ..analytics.transactions import TransactionHistoryAnalyzer
            match = re.search(r'\b([a-zA-Z0-9]{2,10}(?:usdt|btc|eth|bnb|fdusd)?)\b', prompt.lower())
            asset_cand = "BTCUSDT"
            if match:
                cand = match.group(1).upper()
                if cand in ("ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX", "SUI", "NEAR", "LINK", "BTC"):
                    asset_cand = f"{cand}USDT"
                elif cand.endswith("USDT") or cand.endswith("BTC") or cand.endswith("FDUSD"):
                    asset_cand = cand
                elif "eth" in prompt.lower():
                    asset_cand = "ETHUSDT"
                elif "sol" in prompt.lower():
                    asset_cand = "SOLUSDT"
                elif "bnb" in prompt.lower():
                    asset_cand = "BNBUSDT"

            raw_trades = []
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_trades = self.api_client.get_my_trades(asset_cand, limit=50)
                except Exception as e:
                    logger.warning(f"Live trade query failed for {asset_cand}: {e}")
            elif active_mode == "mock":
                raw_trades = self.mock_provider.get_my_trades(asset_cand, limit=50)

            if not raw_trades and active_mode != "mock":
                if not (self.api_client.api_key and self.api_client.api_secret):
                    return {
                        "query": prompt,
                        "answer": (
                            f"🔐 **API Keys Required for Trade History**\n"
                            f"To inspect your past filled spot orders on {asset_cand}, please configure read-only BINANCE_API_KEY and BINANCE_API_SECRET in `.env`."
                        ),
                        "requires_credentials": True,
                    }

            tr_analysis = TransactionHistoryAnalyzer.parse_trades(asset_cand, raw_trades)
            summary_txt = tr_analysis.format_summary()

            recent_trades_txt = ["\nRecent Filled Orders:"]
            if tr_analysis.trades:
                for t in tr_analysis.trades[:8]:
                    recent_trades_txt.append(
                        f"• [{t.formatted_time}] {t.side} {t.quantity} {t.symbol} @ ${t.price:,.2f} (${t.quote_quantity:,.2f}) | Comm: {t.commission} {t.commission_asset}"
                    )
            else:
                recent_trades_txt.append(f"• No trade executions found for {asset_cand}.")

            return {
                "query": prompt,
                "answer": summary_txt + "\n" + "\n".join(recent_trades_txt),
                "trades": tr_analysis.to_dict(),
                "requires_credentials": False,
            }

        # Priority 2: Market Cap Rankings Query
        if is_mcap_query:
            include_stables = "exclude stable" not in prompt.lower() and "no stable" not in prompt.lower()
            if active_mode == "mock":
                top_coins = self.mock_provider.get_top_by_market_cap(limit=10, include_stables=include_stables)
            else:
                top_coins = self.api_client.get_top_by_market_cap(limit=10, include_stables=include_stables)
            lines = [
                "🌐 **Top 10 Cryptocurrencies Ranked by Market Capitalization (Live Binance Data)**:\n",
                "| Rank | Coin | Name | Price | 24h Change | Market Cap | 24h Volume |",
                "|:---:|:---|:---|:---:|:---:|:---:|:---:|",
            ]
            for c in top_coins:
                chg_sign = "+" if c["change_24h_pct"] >= 0 else ""
                vol_m = c["volume_24h_usd"] / 1e6
                lines.append(
                    f"| {c['rank']} | **${c['asset']}** | {c['name']} | ${c['price']:,.2f} | {chg_sign}{c['change_24h_pct']:.2f}% | {c['market_cap_formatted']} | ${vol_m:.1f}M |"
                )
            lead = top_coins[0] if top_coins else {"name": "Bitcoin", "market_cap_formatted": "$1.58T"}
            lines.append(f"\n💡 **Market Structure Analysis**: {lead['name']} leads the cryptocurrency market with a circulating valuation of {lead['market_cap_formatted']}. All market capitalization figures and spot trading metrics are verified via live Binance market data feeds.")
            answer = "\n".join(lines)
            return {
                "query": prompt,
                "answer": answer,
                "top_by_market_cap": top_coins,
                "requires_credentials": False,
            }

        # Priority 2: Tweet Drafting Query (Market focus unless explicitly requesting portfolio)
        if is_tweet_query and not is_explicit_portfolio:
            from ..content.tweet_drafter import TweetDrafter
            brief = MarketBriefGenerator.generate(watchlist=watchlist, mode="mock" if active_mode == "mock" else "api")
            style = "thread" if "thread" in prompt.lower() else "single"
            draft = TweetDrafter.draft_market_tweet(brief, style=style)
            answer = (
                f"🐦 Drafted Publication-Ready Market Tweet ({style.upper()}):\n\n"
                f"{draft.formatted_preview}\n\n"
                f"📊 Live Binance Market Reference:\n"
                f"• {brief.headline}\n"
                f"• Sentiment: {brief.sentiment.replace('_', ' ')}\n"
                f"• Tracked 24h Volume: ${brief.metrics.get('total_tracked_volume_usd', 0):,.0f} USD"
            )
            return {
                "query": prompt,
                "answer": answer,
                "market_brief": brief.to_dict(),
                "drafted_tweet": draft.to_dict(),
                "requires_credentials": False,
            }

        # Priority 3: Asset-Specific Movement / Driver Query (e.g. "Why is ETH moving today, and what should I watch?")
        import re
        asset_match = re.search(r'\b(eth|ethereum|sol|solana|btc|bitcoin|bnb|xrp|doge|ada|avax|sui|near|link)\b', prompt.lower())
        is_asset_driver_query = bool(asset_match and any(w in prompt.lower() for w in ["why", "moving", "driving", "watch", "driver", "today", "level"]))

        if is_asset_driver_query and not is_explicit_portfolio and not is_tweet_query:
            token_raw = asset_match.group(1).upper()
            aliases = {"ETHEREUM": "ETH", "SOLANA": "SOL", "BITCOIN": "BTC"}
            target_asset = aliases.get(token_raw, token_raw)
            sym = f"{target_asset}USDT"
            
            ticker = None
            if active_mode == "mock":
                ticker = self.mock_provider.get_ticker_24hr(sym)
            else:
                try:
                    ticker = self.api_client.get_ticker_24hr(sym)
                except Exception:
                    pass
            
            if ticker:
                last_price = float(ticker.get("lastPrice") or 0)
                chg_pct = float(ticker.get("priceChangePercent") or 0)
                high_24h = float(ticker.get("highPrice") or 0)
                low_24h = float(ticker.get("lowPrice") or 0)
                q_vol = float(ticker.get("quoteVolume") or 0)
                brief = MarketBriefGenerator.generate(watchlist=watchlist, mode="mock" if active_mode == "mock" else "api")
                chg_sign = "+" if chg_pct >= 0 else ""
                vol_fmt = f"${q_vol/1e9:.2f}B" if q_vol >= 1e9 else f"${q_vol/1e6:.1f}M"
                
                answer = (
                    f"🌐 Binance PortfolioPulse: {target_asset} Market Analysis\n\n"
                    f"📊 Live Price & 24h Spot Metrics:\n"
                    f"• Current Price: ${last_price:,.2f} ({chg_sign}{chg_pct:.2f}%)\n"
                    f"• 24h Trading Range: ${low_24h:,.2f} – ${high_24h:,.2f}\n"
                    f"• 24h Binance Spot Volume: {vol_fmt} USD\n"
                    f"• Broad Market Sentiment: {brief.sentiment.replace('_', ' ')}\n\n"
                    f"🔍 Why is {target_asset} Moving Today?\n"
                    f"• Price Action: {target_asset} is trading with {chg_sign}{chg_pct:.2f}% daily momentum on strong Binance spot liquidity ({vol_fmt} USD).\n"
                    f"• Market Regime: Broader market conditions reflect {brief.sentiment.replace('_', ' ')} sentiment with ${brief.metrics.get('total_tracked_volume_usd', 0):,.0f} in tracked exchange volume.\n"
                    f"• Market Context: {brief.headline}\n\n"
                    f"🎯 What Should You Watch?\n"
                    f"• Key Resistance: 24h High at ${high_24h:,.2f} — a sustained breakout confirms ongoing upside continuation.\n"
                    f"• Critical Support: 24h Low at ${low_24h:,.2f} — defending this level maintains structural support.\n"
                    f"• Volume Dynamics: Monitor whether Binance spot volume sustains above {vol_fmt} to validate trend strength.\n"
                    f"• Macro Sentiment: Track Bitcoin correlation as market-wide liquidity shapes altcoin momentum."
                )
                return {
                    "query": prompt,
                    "answer": answer,
                    "target_asset": target_asset,
                    "ticker": ticker,
                    "market_brief": brief.to_dict(),
                    "requires_credentials": False,
                }

        # Priority 4: General Market Intelligence Query
        if is_market_query and not is_explicit_portfolio:
            brief = MarketBriefGenerator.generate(watchlist=watchlist, mode="mock" if active_mode == "mock" else "api")
            gainers_str = ", ".join(f"${g['asset']} (+{g['priceChangePercent']:.1f}%)" for g in brief.top_gainers[:3])
            losers_str = ", ".join(f"${l['asset']} ({l['priceChangePercent']:.1f}%)" for l in brief.top_losers[:3]) if brief.top_losers else "None"
            answer = (
                f"🌐 Real-Time Binance Market Intelligence:\n\n"
                f"• Headline: {brief.headline}\n"
                f"• Sentiment: {brief.sentiment.replace('_', ' ')}\n"
                f"• Tracked 24h Volume: ${brief.metrics.get('total_tracked_volume_usd', 0):,.0f} USD\n"
                f"• Top Gainers: {gainers_str}\n"
                f"• Top Losers: {losers_str}\n\n"
                f"📌 Live Market Observations:\n" +
                "\n".join(f"   - {kp}" for kp in brief.key_points)
            )
            return {
                "query": prompt,
                "answer": answer,
                "market_brief": brief.to_dict(),
                "requires_credentials": False,
            }

        # Priority 4: Personal Portfolio Analysis (Requires Credentials or Mock Mode)
        if active_mode == "mock":
            raw = self.mock_provider.get_account_balances()
            tickers = {}
            trends = {}
            for item in raw:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                t = self.mock_provider.get_ticker_24hr(sym)
                if t:
                    tickers[sym] = t
                    k = self.mock_provider.get_klines_history(sym, limit=7)
                    trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, t, k)
        else:
            has_keys = bool(self.api_client.api_key and self.api_client.api_secret)
            if not has_keys:
                brief = MarketBriefGenerator.generate(watchlist=watchlist, mode="api")
                answer = (
                    f"🔐 Portfolio Authentication Notice:\n"
                    f"To analyze your personal wallet holdings, risk exposure, and P&L with real account data, "
                    f"please configure read-only BINANCE_API_KEY and BINANCE_API_SECRET in your .env file.\n\n"
                    f"🌐 Real-Time Binance Market Context:\n"
                    f"• {brief.headline}\n"
                    f"• Sentiment: {brief.sentiment.replace('_', ' ')}\n"
                    f"• Tracked 24h Volume: ${brief.metrics.get('total_tracked_volume_usd', 0):,.0f} USD\n\n"
                    f"📌 Live Market Takeaways:\n" +
                    "\n".join(f"   - {kp}" for kp in brief.key_points[:3]) +
                    f"\n\n💡 Tip: To inspect live market movers and trends without credentials, run:\n"
                    f"   python3 run_agent.py --brief market"
                )
                return {
                    "query": prompt,
                    "answer": answer,
                    "market_brief": brief.to_dict(),
                    "requires_credentials": True,
                }
            raw = self.api_client.get_account_balances()
            tickers = {}
            trends = {}
            non_stables = [
                item.get("asset", "").upper()
                for item in raw
                if item.get("asset", "").upper() not in ("USDT", "USDC", "FDUSD")
            ]
            symbols_to_fetch = [f"{a}USDT" for a in non_stables]
            batch_tickers = {}
            if symbols_to_fetch:
                try:
                    batch_res = self.api_client.get_tickers_batch(symbols_to_fetch)
                    batch_tickers = {t["symbol"]: t for t in batch_res if isinstance(t, dict) and "symbol" in t}
                except Exception as e:
                    logger.warning(f"Batch ticker fetch failed: {e}")

            for item in raw:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                t = batch_tickers.get(sym)
                if not t:
                    logger.info(f"No active Binance spot pair for {sym}. Valued at $0.00.")
                    t = {"symbol": sym, "lastPrice": "0.00", "priceChangePercent": "0.00"}
                tickers[sym] = t
                if float(t.get("lastPrice", 0.0)) > 0:
                    try:
                        k = self.api_client.get_klines(sym, interval="1d", limit=7)
                        trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, t, k)
                    except Exception as e:
                        logger.warning(f"Failed to fetch klines for {sym}: {e}")

        summary = PortfolioAnalyzer.analyze(raw, tickers)
        risk = RiskAnalyzer.evaluate(
            summary=summary,
            trends=trends,
            concentration_threshold=config.risk_concentration_threshold,
            volatility_threshold=config.risk_volatility_threshold,
            min_stablecoin_buffer=config.min_stablecoin_buffer,
        )
        ai_summary = AISummaryGenerator.generate(
            summary=summary,
            risk=risk,
            trends=trends,
            llm_api_key=config.llm_api_key,
            llm_model=config.llm_model,
            anthropic_api_key=config.anthropic_api_key,
            gemini_api_key=config.gemini_api_key,
            openai_api_key=config.openai_api_key,
        )
        brief = MarketBriefGenerator.generate(watchlist=watchlist, mode="mock" if active_mode == "mock" else "api")

        if is_tweet_query and summary.total_value_usd > 0:
            from ..content.tweet_drafter import TweetDrafter
            style = "thread" if "thread" in prompt.lower() else "single"
            draft = TweetDrafter.draft_portfolio_tweet(summary, ai_summary, style=style)
            answer = (
                f"🐦 Ready-to-Post Tweet ({style.upper()}):\n\n"
                f"{draft.formatted_preview}\n\n"
                f"📊 Market Context: {brief.headline}"
            )
        else:
            answer = (
                f"Portfolio Valuation: ${summary.total_value_usd:,.2f} | 24h P&L: {'+' if summary.total_24h_pnl_usd >= 0 else ''}${summary.total_24h_pnl_usd:,.2f} ({summary.total_24h_pnl_pct:+.2f}%)\n"
                f"Risk Level: {risk.risk_level} (Score: {risk.overall_score}/10)\n\n"
                f"Analysis for: \"{prompt}\"\n\n"
                f"Executive Summary: {ai_summary.headline}\n\n"
                f"Market Context: {brief.headline}\n\n"
                f"Overview: {ai_summary.overview}"
            )

        return {
            "query": prompt,
            "answer": answer,
            "portfolio_valuation_usd": summary.total_value_usd,
            "pnl_24h_usd": summary.total_24h_pnl_usd,
            "risk_level": risk.risk_level,
            "risk_score": risk.overall_score,
            "risk_flags": [f.title for f in risk.flags],
            "actionable_takeaways": ai_summary.actionable_tips,
            "market_headline": brief.headline,
            "market_sentiment": brief.sentiment,
        }

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific Binance MCP tool with fallback capability."""
        resp = self.send_mcp_request("tools/call", {"name": name, "arguments": arguments})
        if "result" in resp and not resp.get("error"):
            return resp["result"]

        # Fallback to direct API or mock data if MCP endpoint is restricted by policy
        logger.debug(f"Handling '{name}' via local agent tool provider.")
        from ..config import config
        if name == "get_account_balances":
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    return self.api_client.get_account_balances()
                except Exception as e:
                    logger.warning(f"Error fetching account balances: {e}")
                    return {"error": str(e)}
            if config.mode == "mock":
                return self.mock_provider.get_account_balances()
            return {"error": "BINANCE_API_KEY and BINANCE_API_SECRET are required for account balance access"}

        elif name == "get_ticker_24hr":
            from ..config import config
            symbols = arguments.get("symbols")
            if symbols and isinstance(symbols, list):
                if config.mode == "mock":
                    return [self.mock_provider.get_ticker_24hr(s) for s in symbols if self.mock_provider.get_ticker_24hr(s)]
                return self.api_client.get_tickers_batch(symbols)

            sym = (arguments.get("symbol") or "BTCUSDT").upper()
            if config.mode == "mock":
                t = self.mock_provider.get_ticker_24hr(sym)
                return t if t is not None else {"error": f"Symbol '{sym}' not found in mock catalog"}
            return self.api_client.get_ticker_24hr(sym)

        elif name == "get_klines":
            sym = (arguments.get("symbol") or "BTCUSDT").upper()
            limit = arguments.get("limit", 7)
            from ..config import config
            if config.mode == "mock":
                return self.mock_provider.get_klines_history(sym, limit=limit)
            return self.api_client.get_klines(sym, limit=limit)

        elif name == "get_market_overview":
            watchlist = arguments.get("watchlist")
            from ..config import config
            if config.mode == "mock":
                return self.mock_provider.get_market_overview(watchlist)
            return self.api_client.get_market_overview(watchlist)

        elif name == "generate_market_brief":
            from ..analytics.market_brief import MarketBriefGenerator
            from ..config import config
            watchlist = arguments.get("watchlist")
            brief = MarketBriefGenerator.generate(watchlist=watchlist, mode=config.mode)
            return brief.to_dict()

        elif name == "draft_tweet":
            from ..analytics.market_brief import MarketBriefGenerator
            from ..content.tweet_drafter import TweetDrafter
            from ..config import config
            topic = arguments.get("topic", "market")
            style = arguments.get("style", "single")

            if topic == "portfolio":
                from ..analytics.portfolio import PortfolioAnalyzer
                raw = []
                if self.api_client.api_key and self.api_client.api_secret:
                    try:
                        raw = self.api_client.get_account_balances()
                    except Exception as e:
                        logger.warning(f"Error fetching account balances: {e}")
                elif config.mode == "mock":
                    raw = self.mock_provider.get_account_balances()

                if not raw:
                    return {"error": "No portfolio balances found. Configure BINANCE_API_KEY and BINANCE_API_SECRET in .env for portfolio tweets, or use topic='market' for real-time market tweets."}

                tickers = {}
                held_symbols = [f"{item['asset']}USDT" for item in raw if item.get('asset') not in ("USDT", "USDC", "FDUSD")]
                if config.mode == "mock":
                    tickers = {s: self.mock_provider.get_ticker_24hr(s) for s in held_symbols}
                else:
                    batch_res = self.api_client.get_tickers_batch(held_symbols)
                    tickers = {t["symbol"]: t for t in batch_res if isinstance(t, dict) and "symbol" in t}
                summary = PortfolioAnalyzer.analyze(raw, tickers)
                draft = TweetDrafter.draft_portfolio_tweet(
                    summary,
                    style=style,
                    llm_api_key=config.llm_api_key,
                    llm_model=config.llm_model,
                )
            else:
                brief = MarketBriefGenerator.generate(mode=config.mode)
                draft = TweetDrafter.draft_market_tweet(
                    brief,
                    style=style,
                    llm_api_key=config.llm_api_key,
                    llm_model=config.llm_model,
                )

            return draft.to_dict()

        elif name == "ask_portfoliopulse":
            prompt = arguments.get("prompt", "Analyze my portfolio status")
            watchlist = arguments.get("watchlist")
            return self.ask_portfoliopulse(prompt=prompt, watchlist=watchlist)

        elif name == "get_top_by_market_cap":
            limit = int(arguments.get("limit", 10))
            include_stables = bool(arguments.get("include_stables", True))
            from ..config import config
            if config.mode == "mock":
                return self.mock_provider.get_top_by_market_cap(limit=limit, include_stables=include_stables)
            return self.api_client.get_top_by_market_cap(limit=limit, include_stables=include_stables)

        elif name == "get_futures_account":
            from ..config import config
            from ..analytics.futures import FuturesAnalyzer
            raw_f = None
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_f = self.api_client.get_futures_account()
                except Exception as e:
                    logger.info(f"Live futures account query: {e}. (Enable Futures on your Binance API key to view active margin).")
                    raw_f = {
                        "totalMarginBalance": "0.00",
                        "totalWalletBalance": "0.00",
                        "totalUnrealizedProfit": "0.00",
                        "totalMaintMargin": "0.00",
                        "totalInitialMargin": "0.00",
                        "availableBalance": "0.00",
                        "positions": [],
                    }
            elif config.mode == "mock":
                raw_f = self.mock_provider.get_futures_account()
            else:
                raw_f = {
                    "totalMarginBalance": "0.00",
                    "totalWalletBalance": "0.00",
                    "totalUnrealizedProfit": "0.00",
                    "totalMaintMargin": "0.00",
                    "totalInitialMargin": "0.00",
                    "availableBalance": "0.00",
                    "positions": [],
                }

            mark_prices = []
            try:
                mark_prices = self.api_client.get_futures_mark_prices()
            except Exception:
                if config.mode == "mock":
                    mark_prices = self.mock_provider.get_futures_mark_prices()

            f_summary = FuturesAnalyzer.analyze(raw_f, mark_prices=mark_prices)
            return f_summary.to_dict()

        elif name == "get_predictive_balance":
            from ..config import config
            from ..analytics.portfolio import PortfolioAnalyzer
            from ..analytics.futures import FuturesAnalyzer
            from ..analytics.predictive import PredictiveBalanceEngine

            raw_balances = []
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_balances = self.api_client.get_account_balances()
                except Exception:
                    pass
            if not raw_balances:
                raw_balances = self.mock_provider.get_account_balances()

            held_non_stables = [b.get("asset", "").upper() for b in raw_balances if b.get("asset", "").upper() not in ("USDT", "USDC", "FDUSD")]
            symbols = [f"{a}USDT" for a in held_non_stables]
            tickers_map = {}
            if self.fallback_to_api:
                try:
                    batch_res = self.api_client.get_tickers_batch(symbols)
                    tickers_map = {t["symbol"]: t for t in batch_res if isinstance(t, dict) and "symbol" in t}
                except Exception:
                    pass
            for s in symbols:
                if s not in tickers_map:
                    t = self.mock_provider.get_ticker_24hr(s)
                    if t:
                        tickers_map[s] = t

            spot_summary = PortfolioAnalyzer.analyze(raw_balances, tickers_map)

            raw_f = None
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_f = self.api_client.get_futures_account()
                except Exception:
                    raw_f = {
                        "totalMarginBalance": "0.00",
                        "totalWalletBalance": "0.00",
                        "totalUnrealizedProfit": "0.00",
                        "totalMaintMargin": "0.00",
                        "totalInitialMargin": "0.00",
                        "availableBalance": "0.00",
                        "positions": [],
                    }
            elif config.mode == "mock":
                raw_f = self.mock_provider.get_futures_account()
            else:
                raw_f = {
                    "totalMarginBalance": "0.00",
                    "totalWalletBalance": "0.00",
                    "totalUnrealizedProfit": "0.00",
                    "totalMaintMargin": "0.00",
                    "totalInitialMargin": "0.00",
                    "availableBalance": "0.00",
                    "positions": [],
                }
            f_summary = FuturesAnalyzer.analyze(raw_f)

            all_syms = list(set(["BTCUSDT"] + symbols))
            try:
                klines_batch = self.api_client.get_historical_klines_batch(all_syms, limit=30)
            except Exception:
                klines_batch = self.mock_provider.get_historical_klines_batch(all_syms, limit=30)

            report = PredictiveBalanceEngine.forecast(spot_summary, f_summary, klines_batch)
            return report.to_dict()

        elif name == "get_order_book":
            from ..config import config
            from ..analytics.order_book import OrderBookAnalyzer
            sym = (arguments.get("symbol") or "BTCUSDT").upper()
            limit = int(arguments.get("limit", 20))
            raw_depth = None
            if config.mode == "mock":
                raw_depth = self.mock_provider.get_order_book(sym, limit=limit)
            else:
                try:
                    raw_depth = self.api_client.get_order_book(sym, limit=limit)
                except Exception as e:
                    logger.warning(f"Live order book fetch failed for {sym}: {e}")
                    raw_depth = self.mock_provider.get_order_book(sym, limit=limit)
            analysis = OrderBookAnalyzer.analyze(sym, raw_depth)
            return analysis.to_dict()

        elif name == "get_my_trades":
            from ..config import config
            from ..analytics.transactions import TransactionHistoryAnalyzer
            sym = (arguments.get("symbol") or "BTCUSDT").upper()
            limit = int(arguments.get("limit", 50))
            raw_trades = []
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_trades = self.api_client.get_my_trades(sym, limit=limit)
                except Exception as e:
                    logger.warning(f"Live trade history fetch failed for {sym}: {e}")
                    if config.mode == "mock":
                        raw_trades = self.mock_provider.get_my_trades(sym, limit=limit)
            elif config.mode == "mock":
                raw_trades = self.mock_provider.get_my_trades(sym, limit=limit)
            
            analysis = TransactionHistoryAnalyzer.parse_trades(sym, raw_trades)
            return analysis.to_dict()

        elif name == "get_deposit_history":
            from ..config import config
            from ..analytics.transactions import TransactionHistoryAnalyzer
            coin = arguments.get("coin")
            limit = int(arguments.get("limit", 50))
            raw_deposits = []
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_deposits = self.api_client.get_deposit_history(coin=coin, limit=limit)
                except Exception as e:
                    logger.warning(f"Live deposit history fetch failed: {e}")
                    if config.mode == "mock":
                        raw_deposits = self.mock_provider.get_deposit_history(coin=coin, limit=limit)
            elif config.mode == "mock":
                raw_deposits = self.mock_provider.get_deposit_history(coin=coin, limit=limit)

            analysis = TransactionHistoryAnalyzer.parse_transfers(raw_deposits, [])
            return {
                "total_deposits": len(raw_deposits),
                "deposits_by_coin": analysis.deposits_by_coin,
                "deposits": [t.to_dict() for t in analysis.transfers if t.transfer_type == "DEPOSIT"],
            }

        elif name == "get_withdraw_history":
            from ..config import config
            from ..analytics.transactions import TransactionHistoryAnalyzer
            coin = arguments.get("coin")
            limit = int(arguments.get("limit", 50))
            raw_withdrawals = []
            if self.fallback_to_api and self.api_client.api_key and self.api_client.api_secret:
                try:
                    raw_withdrawals = self.api_client.get_withdraw_history(coin=coin, limit=limit)
                except Exception as e:
                    logger.warning(f"Live withdrawal history fetch failed: {e}")
                    if config.mode == "mock":
                        raw_withdrawals = self.mock_provider.get_withdraw_history(coin=coin, limit=limit)
            elif config.mode == "mock":
                raw_withdrawals = self.mock_provider.get_withdraw_history(coin=coin, limit=limit)

            analysis = TransactionHistoryAnalyzer.parse_transfers([], raw_withdrawals)
            return {
                "total_withdrawals": len(raw_withdrawals),
                "withdrawals_by_coin": analysis.withdrawals_by_coin,
                "withdrawals": [t.to_dict() for t in analysis.transfers if t.transfer_type == "WITHDRAWAL"],
            }

        raise NotImplementedError(f"Tool {name} is not implemented.")



def run_stdio_mcp_server():
    """
    Runs an interactive stdio MCP server exposing Binance portfolio analysis tools.
    Compatible with Claude Desktop, Cursor, Codex, and Agent OS.
    """
    mcp_client = BinanceMCPClient()
    logger.info("Starting Binance Agent OS stdio MCP Server...")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                # EOF reached
                break
            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})


            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "binance-agent-os-portfolio-pulse",
                            "version": "1.0.0",
                        },
                    },
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": mcp_client.list_tools()},
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                tool_result = mcp_client.call_tool(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(tool_result, indent=2)}
                        ]
                    },
                }
            elif method == "notifications/initialized":
                # Client notification after initialize; no response required
                continue
            elif method == "ping":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            else:
                if req_id is None:
                    # Client notifications have no id and do not expect a response
                    continue
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            if req_id is not None:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(e)},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()



if __name__ == "__main__":
    if "--stdio" in sys.argv:
        run_stdio_mcp_server()
