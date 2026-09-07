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
