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

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = "https://api.binance.com",
        timeout: int = 10,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.ssl_context = get_ssl_context()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Any:
        """Internal helper for executing signed or public Binance HTTP requests."""
        params = params or {}
        headers = {
            "User-Agent": "Binance-Agent-OS-Reporter/1.0",
            "Accept": "application/json",
        }

        if signed:
            if not self.api_key or not self.api_secret:
                raise ValueError(
                    "Signed requests require BINANCE_API_KEY and BINANCE_API_SECRET"
                )
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 5000
            query_str = urllib.parse.urlencode(params)
            signature = hmac.new(
                self.api_secret.encode("utf-8"),
                query_str.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            query_str += f"&signature={signature}"
            headers["X-MBX-APIKEY"] = self.api_key
        else:
            query_str = urllib.parse.urlencode(params)

        url = f"{self.base_url}{path}"
        if query_str:
            url += f"?{query_str}"

        req = urllib.request.Request(url, headers=headers, method=method)

        try:
            try:
                resp_context = urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context)
            except urllib.error.URLError as ssl_err:
                if "CERTIFICATE_VERIFY_FAILED" in str(ssl_err):
                    # macOS system python certs fallback
                    fallback_ctx = ssl._create_unverified_context()
                    resp_context = urllib.request.urlopen(req, timeout=self.timeout, context=fallback_ctx)
                else:
                    raise ssl_err

            with resp_context as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            if e.code == 429:
                logger.error(f"Binance API Rate Limit exceeded (HTTP 429): {err_msg}")
            elif e.code in (401, 403):
                logger.error(
                    f"Binance API Auth/Permission error (HTTP {e.code}): Check API key, IP whitelist, or sub-account scopes: {err_msg}"
                )
            else:
                logger.error(f"Binance API HTTP {e.code} error on {path}: {err_msg}")
            raise
        except urllib.error.URLError as e:
            logger.error(f"Binance API connection failed for {path}: {e.reason}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Binance API request to {path}: {e}")
            raise

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
