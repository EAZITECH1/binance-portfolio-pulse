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
            import ssl
            try:
                resp_ctx = urllib.request.urlopen(req, timeout=8, context=self.ssl_context)
            except urllib.error.URLError as ssl_err:
                if "CERTIFICATE_VERIFY_FAILED" in str(ssl_err):
                    resp_ctx = urllib.request.urlopen(req, timeout=8, context=ssl._create_unverified_context())
                else:
                    raise ssl_err

            with resp_ctx as resp:
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
                "description": "Get 24-hour price change and volume statistics for a crypto pair",
                "inputSchema": {
                    "type": "object",
                    "properties": {"symbol": {"type": "string", "description": "e.g. BTCUSDT"}},
                    "required": ["symbol"],
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

        # Decide whether to use real exchange API or mock
        use_live = (mode == "api") or (mode != "mock" and bool(self.api_client.api_key))

        # Ingest balances & tickers
        if use_live:
            try:
                raw = self.api_client.get_account_balances()
            except Exception as e:
                logger.warning(f"Error fetching live balances: {e}")
                raw = []
            tickers = {}
            trends = {}
            for item in raw:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                try:
                    t = self.api_client.get_ticker_24hr(sym)
                    tickers[sym] = t
                    k = self.api_client.get_klines(sym, interval="1d", limit=7)
                    trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, t, k)
                except Exception:
                    tickers[sym] = {"symbol": sym, "lastPrice": "0.00", "priceChangePercent": "0.00"}
        else:
            raw = self.mock_provider.get_account_balances()
            tickers = {}
            trends = {}
            for item in raw:
                asset = item.get("asset", "").upper()
                if asset in ("USDT", "USDC", "FDUSD"):
                    continue
                sym = f"{asset}USDT"
                t = self.mock_provider.get_ticker_24hr(sym)
                tickers[sym] = t
                k = self.mock_provider.get_klines_history(sym, limit=7)
                trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(asset, t, k)

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
        brief = MarketBriefGenerator.generate(watchlist=watchlist, mode=mode or ("api" if use_live else "mock"))

        # Build comprehensive answer
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
            if self.fallback_to_api and self.api_client.api_key:
                try:
                    return self.api_client.get_account_balances()
                except Exception as e:
                    logger.warning(f"Error fetching account balances: {e}")
                    return []
            if config.mode == "mock" and not self.api_client.api_key:
                return self.mock_provider.get_account_balances()
            return []

        elif name == "get_ticker_24hr":
            sym = arguments.get("symbol", "BTCUSDT")
            if self.fallback_to_api:
                try:
                    return self.api_client.get_ticker_24hr(sym)
                except Exception:
                    pass
            return self.mock_provider.get_ticker_24hr(sym)

        elif name == "get_klines":
            sym = arguments.get("symbol", "BTCUSDT")
            limit = arguments.get("limit", 7)
            if self.fallback_to_api:
                try:
                    return self.api_client.get_klines(sym, limit=limit)
                except Exception:
                    pass
            return self.mock_provider.get_klines_history(sym, limit=limit)

        elif name == "get_market_overview":
            watchlist = arguments.get("watchlist")
            if self.fallback_to_api:
                try:
                    return self.api_client.get_market_overview(watchlist)
                except Exception as e:
                    logger.warning(f"Live market overview query failed: {e}")
            from ..config import config
            if config.mode == "mock":
                return self.mock_provider.get_market_overview(watchlist)
            return self.api_client.get_market_overview(watchlist)

        elif name == "generate_market_brief":
            from ..analytics.market_brief import MarketBriefGenerator
            from ..config import config
            watchlist = arguments.get("watchlist")
            mode = "mock" if config.mode == "mock" else "api"
            brief = MarketBriefGenerator.generate(watchlist=watchlist, mode=mode)
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
                if self.fallback_to_api and self.api_client.api_key:
                    try:
                        raw = self.api_client.get_account_balances()
                    except Exception:
                        pass
                if not raw and config.mode == "mock" and not self.api_client.api_key:
                    raw = self.mock_provider.get_account_balances()

                tickers = {}
                for item in raw:
                    sym = f"{item['asset']}USDT"
                    try:
                        tickers[sym] = self.api_client.get_ticker_24hr(sym)
                    except Exception:
                        tickers[sym] = {"symbol": sym, "lastPrice": "0.00", "priceChangePercent": "0.00"}
                summary = PortfolioAnalyzer.analyze(raw, tickers)
                draft = TweetDrafter.draft_portfolio_tweet(
                    summary,
                    style=style,
                    llm_api_key=config.llm_api_key,
                    llm_model=config.llm_model,
                )
            else:
                mode = "mock" if config.mode == "mock" else "api"
                brief = MarketBriefGenerator.generate(mode=mode)
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
