"""
Binance REST API connector for live market data and authenticated portfolio balances.
Uses Python standard library (urllib) for zero external dependencies.
"""
import hashlib
import hmac
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

from ..utils.logger import logger


import ssl


def get_ssl_context() -> ssl.SSLContext:
    """Returns a valid SSL context, with graceful fallback on macOS system Python."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    try:
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        return ssl._create_unverified_context()


class BinanceAPIClient:
    """Client for Binance Spot and Market Data REST endpoints."""

    DEFAULT_BASE_URLS = [
        "https://data-api.binance.vision",
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api3.binance.com",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 10,
    ):
        from ..config import config
        self.api_key = api_key if api_key is not None else config.api_key
        self.api_secret = api_secret if api_secret is not None else config.api_secret
        self.base_url = (base_url or config.base_url or "https://api.binance.com").rstrip("/")
        self.timeout = timeout
        self.ssl_context = get_ssl_context()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Any:
        """Internal helper for executing signed or public Binance HTTP requests with multi-endpoint fallback."""
        params = params or {}
        headers = {
            "User-Agent": "Binance-Agent-OS-Reporter/1.0",
            "Accept": "application/json",
        }

        # Candidate endpoints to try if primary fails due to network/DNS
        candidate_urls = [self.base_url] + [u for u in self.DEFAULT_BASE_URLS if u != self.base_url]

        last_error = None
        for base in candidate_urls:
            req_params = dict(params)
            if signed:
                if not self.api_key or not self.api_secret:
                    raise ValueError("Signed requests require BINANCE_API_KEY and BINANCE_API_SECRET")
                req_params["timestamp"] = int(time.time() * 1000)
                req_params["recvWindow"] = 5000
                query_str = urllib.parse.urlencode(req_params)
                signature = hmac.new(
                    self.api_secret.encode("utf-8"),
                    query_str.encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest()
                query_str += f"&signature={signature}"
                headers["X-MBX-APIKEY"] = self.api_key
            else:
                query_str = urllib.parse.urlencode(req_params)

            url = f"{base}{path}"
            if query_str:
                url += f"?{query_str}"

            req = urllib.request.Request(url, headers=headers, method=method)

            try:
                import ssl
                try:
                    resp_context = urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context)
                except urllib.error.URLError as ssl_err:
                    if "CERTIFICATE_VERIFY_FAILED" in str(ssl_err):
                        fallback_ctx = ssl._create_unverified_context()
                        resp_context = urllib.request.urlopen(req, timeout=self.timeout, context=fallback_ctx)
                    else:
                        raise ssl_err

                with resp_context as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body)
            except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
                last_error = e
                logger.debug(f"Request to {base}{path} failed: {e}. Trying next Binance endpoint...")
                continue

        # If all candidates failed
        if isinstance(last_error, urllib.error.HTTPError):
            err_msg = last_error.read().decode("utf-8") if hasattr(last_error, "read") else str(last_error)
            if last_error.code == 429:
                logger.error(f"Binance API Rate Limit exceeded (HTTP 429): {err_msg}")
            elif last_error.code in (401, 403):
                logger.error(f"Binance API Auth/Permission error (HTTP {last_error.code}): Check API keys or scopes: {err_msg}")
            else:
                logger.error(f"Binance API HTTP {last_error.code} error on {path}: {err_msg}")
        else:
            logger.error(f"All Binance endpoints failed for {path}: {last_error}")
        raise last_error

    def ping(self) -> bool:
        """Test general connectivity to Binance API."""
        try:
            self._request("GET", "/api/v3/ping")
            return True
        except Exception:
            return False

    def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """Fetch 24-hour rolling window price change statistics for a symbol."""
        symbol = symbol.upper()
        return self._request("GET", "/api/v3/ticker/24hr", {"symbol": symbol})

    def get_all_tickers_24hr(self) -> List[Dict[str, Any]]:
        """Fetch 24-hour price change statistics for all trading pairs."""
        return self._request("GET", "/api/v3/ticker/24hr")

    def get_klines(
        self, symbol: str, interval: str = "1d", limit: int = 7
    ) -> List[List[Any]]:
        """Fetch historical candlestick bars for trend and volatility analysis."""
        return self._request(
            "GET",
            "/api/v3/klines",
            {"symbol": symbol.upper(), "interval": interval, "limit": limit},
        )

    def get_account_balances(self) -> List[Dict[str, Any]]:
        """
        Fetch user spot account balances (requires signed API key/secret).
        Filters to assets with non-zero balances.
        """
        data = self._request("GET", "/api/v3/account", signed=True)
        balances = data.get("balances", [])
        active_balances = []
        for b in balances:
            free = float(b.get("free", "0"))
            locked = float(b.get("locked", "0"))
            if free > 0 or locked > 0:
                active_balances.append({
                    "asset": b["asset"],
                    "free": str(free),
                    "locked": str(locked),
                })
        return active_balances

    def get_market_overview(self, watchlist: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch real-time market overview across a watchlist of assets using live Binance 24h tickers.
        Ranks top gainers, top losers, total quote volume, and computes live market sentiment.
        """
        if not watchlist:
            watchlist = ["BTC", "ETH", "SOL", "BNB", "SUI", "NEAR", "AVAX", "DOGE", "LINK", "ARB", "PEPE"]

        symbols = [f"{asset.upper()}USDT" for asset in watchlist]
        raw_tickers = []
        try:
            symbols_param = json.dumps(symbols, separators=(",", ":"))
            data = self._request("GET", "/api/v3/ticker/24hr", {"symbols": symbols_param})
            if isinstance(data, list):
                raw_tickers = data
        except Exception:
            for sym in symbols:
                try:
                    t = self.get_ticker_24hr(sym)
                    raw_tickers.append(t)
                except Exception:
                    pass

        items = []
        total_vol_usd = 0.0
        for t in raw_tickers:
            sym = t.get("symbol", "")
            asset = sym.replace("USDT", "")
            price = float(t.get("lastPrice", 0.0))
            change_pct = float(t.get("priceChangePercent", 0.0))
            quote_vol = float(t.get("quoteVolume", 0.0))
            total_vol_usd += quote_vol

            items.append({
                "asset": asset,
                "symbol": sym,
                "price": price,
                "priceChangePercent": change_pct,
                "high24h": float(t.get("highPrice", price)),
                "low24h": float(t.get("lowPrice", price)),
                "volume24hUsd": quote_vol,
            })

        sorted_by_change = sorted(items, key=lambda x: x["priceChangePercent"], reverse=True)
        top_gainers = sorted_by_change[:3] if sorted_by_change else []
        top_losers = sorted_by_change[-2:] if len(sorted_by_change) >= 2 else []

        avg_change = sum(x["priceChangePercent"] for x in items) / len(items) if items else 0.0
        if avg_change > 3.0:
            sentiment = "BULLISH_EXPANSION"
        elif avg_change > 0.5:
            sentiment = "MODERATE_RISK_ON"
        elif avg_change < -3.0:
            sentiment = "BEARISH_RETREAT"
        elif avg_change < -0.5:
            sentiment = "MILD_PULLBACK"
        else:
            sentiment = "NEUTRAL_CONSOLIDATION"

        return {
            "timestamp": int(time.time()),
            "sentiment": sentiment,
            "average_24h_change_pct": round(avg_change, 2),
            "total_tracked_volume_usd": round(total_vol_usd, 2),
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "assets": items,
        }
