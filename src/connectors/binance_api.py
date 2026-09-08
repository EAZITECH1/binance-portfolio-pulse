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
from typing import Dict, Any, List, Optional, Set

from ..utils.logger import logger


import ssl


def get_ssl_context() -> ssl.SSLContext:
    """Returns a secure SSL context validating against CA certificates."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    try:
        return ssl.create_default_context()
    except Exception as e:
        raise ssl.SSLError(
            f"Unable to create secure SSL context: {e}. "
            "Please install certifi ('pip install certifi') or run macOS 'Install Certificates.command'."
        )


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
                with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body)
            except urllib.error.URLError as e:
                if "CERTIFICATE_VERIFY_FAILED" in str(e):
                    logger.error(
                        f"SSL certificate verification failed connecting to {base}: {e}. "
                        "To protect your credentials, unverified connections are disallowed. "
                        "Please run 'pip install certifi' or install macOS root certificates."
                    )
                    raise
                last_error = e
                logger.debug(f"Request to {base}{path} failed: {e}. Trying next Binance endpoint...")
                continue
            except (urllib.error.HTTPError, Exception) as e:
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

    def get_tickers_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch 24-hour price change statistics for multiple symbols in a single HTTP request.
        Uses Binance GET /api/v3/ticker/24hr?symbols=[...] with fallback to full exchange tickers.
        """
        if not symbols:
            return []
        sym_set = {s.upper() for s in symbols}
        try:
            symbols_param = json.dumps(list(sym_set), separators=(",", ":"))
            data = self._request("GET", "/api/v3/ticker/24hr", {"symbols": symbols_param})
            if isinstance(data, list):
                return data
        except Exception:
            # If an unlisted/invalid token caused 400, fetch full tickers in 1 fast request
            try:
                all_tickers = self.get_all_tickers_24hr()
                return [t for t in all_tickers if t.get("symbol") in sym_set]
            except Exception as e:
                logger.warning(f"Batch ticker query failed: {e}")
        return []

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

    _active_symbols_cache: Optional[Set[str]] = None
    _active_symbols_cache_time: float = 0.0

    def get_active_spot_symbols(self) -> Set[str]:
        """
        Fetch all symbols currently active for spot trading (status == TRADING).
        Caches result for 15 minutes to avoid redundant exchangeInfo network calls.
        """
        now = time.time()
        if self._active_symbols_cache is not None and (now - self._active_symbols_cache_time) < 900:
            return self._active_symbols_cache
        try:
            info = self._request("GET", "/api/v3/exchangeInfo", {"permissions": "SPOT"})
            active = {
                s["symbol"] for s in info.get("symbols", [])
                if s.get("status") == "TRADING" and s.get("isSpotTradingAllowed", False)
            }
            self._active_symbols_cache = active
            self._active_symbols_cache_time = now
            return active
        except Exception as e:
            logger.warning(f"Failed to fetch active spot symbols from exchangeInfo: {e}")
            if self._active_symbols_cache:
                return self._active_symbols_cache
            return set()

    def get_market_overview(self, watchlist: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch real-time market overview across Binance spot markets.
        If watchlist is specified, evaluates those specific assets.
        If watchlist is None, evaluates exchange-wide liquid USDT spot pairs
        to identify the TRUE top gainers, top losers, total volume, and sentiment.
        Strictly filters to actively trading pairs (excluding halted, break, or delisted tokens).
        """
        raw_tickers = []
        is_exchange_wide = not watchlist

        if watchlist:
            symbols = [f"{asset.upper()}USDT" for asset in watchlist]
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
        else:
            # Exchange-wide discovery: scan all liquid USDT spot pairs that are ACTIVELY TRADING
            try:
                active_symbols = self.get_active_spot_symbols()
                all_tickers = self.get_all_tickers_24hr()
                now_ms = time.time() * 1000

                for t in all_tickers:
                    sym = t.get("symbol", "")
                    if not sym.endswith("USDT"):
                        continue
                    # Exclude leveraged/synthetic tokens (UP/DOWN/BEAR/BULL)
                    if any(sym.endswith(x) for x in ["UPUSDT", "DOWNUSDT", "BEARUSDT", "BULLUSDT"]):
                        continue
                    # Exclude halted, break, suspended, or delisted pairs
                    if active_symbols and sym not in active_symbols:
                        continue
                    # Ensure ticker was active recently (last trade closeTime within past 60 minutes)
                    close_time = float(t.get("closeTime", 0))
                    if close_time > 0 and (now_ms - close_time) > 3600 * 1000:
                        continue

                    try:
                        price = float(t.get("lastPrice", 0.0))
                        q_vol = float(t.get("quoteVolume", 0.0))
                        trade_count = int(t.get("count", 0))
                        if price <= 0 or trade_count <= 0:
                            continue
                        # Require at least $1,000,000 in 24h quote volume to filter out illiquid dust
                        if q_vol >= 1_000_000:
                            raw_tickers.append(t)
                    except (ValueError, TypeError):
                        continue

                # Fallback if volume filter was overly restrictive
                if len(raw_tickers) < 10:
                    raw_tickers = [
                        t for t in all_tickers
                        if t.get("symbol", "").endswith("USDT")
                        and (not active_symbols or t.get("symbol") in active_symbols)
                        and not any(t.get("symbol", "").endswith(x) for x in ["UPUSDT", "DOWNUSDT"])
                    ]
            except Exception as e:
                logger.error(f"Exchange-wide ticker fetch failed: {e}")
                raise ConnectionError(f"Failed to fetch live Binance exchange tickers: {e}")

        items = []
        total_vol_usd = 0.0
        for t in raw_tickers:
            sym = t.get("symbol", "")
            asset = sym[:-4] if sym.endswith("USDT") else sym
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
        top_gainers = sorted_by_change[:5] if sorted_by_change else []
        top_losers = sorted_by_change[-5:][::-1] if len(sorted_by_change) >= 5 else (sorted_by_change[-2:][::-1] if len(sorted_by_change) >= 2 else [])

        # For market sentiment: compute average change of tracked liquid assets
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

    _mcap_cache: Optional[List[Dict[str, Any]]] = None
    _mcap_cache_time: float = 0.0

    def get_top_by_market_cap(
        self, limit: int = 10, include_stables: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch real-time top cryptocurrencies ranked by market capitalization.
        Queries Binance's official marketing composite market cap dataset.
        Excludes wrapped tokens and optionally stablecoins.
        """
        now = time.time()
        if self._mcap_cache is not None and (now - self._mcap_cache_time) < 300:
            cached = self._mcap_cache
            filtered = [
                c for c in cached
                if include_stables or not c.get("is_stablecoin", False)
            ]
            for i, c in enumerate(filtered[:limit]):
                c["rank"] = i + 1
            return filtered[:limit]

        stables = {"USDT", "USDC", "USDS", "FDUSD", "DAI", "TUSD", "BUSD", "EUR", "TRY"}
        wrapped = {"WBTC", "WBETH", "WETH", "WBNB", "WEETH"}
        results = []
        seen = set()

        # Binance official composite marketing market cap endpoint
        try:
            req = urllib.request.Request(
                "https://www.binance.com/bapi/composite/v1/public/marketing/symbol/list",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            ctx = get_ssl_context()
            with urllib.request.urlopen(req, context=ctx, timeout=7) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            items = data.get("data", [])
            for x in items:
                asset = str(x.get("baseAsset") or "").upper()
                quote = str(x.get("quoteAsset") or "").upper()
                mcap = float(x.get("marketCap") or 0)
                price = float(x.get("price") or 0)
                chg = float(x.get("dayChange") or 0)
                vol = float(x.get("volume") or 0)
                if quote != "USDT" or mcap <= 0 or price <= 0:
                    continue
                if asset in wrapped or asset in seen:
                    continue
                seen.add(asset)
                fmt_mcap = f"${mcap/1e12:.2f}T" if mcap >= 1e12 else f"${mcap/1e9:.2f}B" if mcap >= 1e9 else f"${mcap/1e6:.1f}M"
                results.append({
                    "asset": asset,
                    "name": x.get("name") or asset,
                    "price": price,
                    "market_cap_usd": mcap,
                    "market_cap_formatted": fmt_mcap,
                    "change_24h_pct": round(chg, 2),
                    "volume_24h_usd": vol,
                    "cmc_rank": x.get("rank"),
                    "is_stablecoin": asset in stables,
                })
        except Exception as e:
            logger.error(f"Binance market cap API query failed: {e}")

        results.sort(key=lambda x: x["market_cap_usd"], reverse=True)
        self._mcap_cache = results
        self._mcap_cache_time = now

        filtered = [
            c for c in results
            if include_stables or not c.get("is_stablecoin", False)
        ]
        final_list = filtered[:limit]
        for i, c in enumerate(final_list):
            c["rank"] = i + 1
        return final_list
