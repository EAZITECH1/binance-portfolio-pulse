"""
Realistic mock data provider for Binance PortfolioPulse AI.
Enables judges and reviewers to test the entire agent pipeline without requiring live API keys.
"""
from typing import Dict, Any, List, Optional
import time


class MockDataProvider:
    """Provides a realistic, diversified crypto portfolio and live market data simulation."""

    def __init__(self):
        # Realistic spot portfolio holdings
        self.holdings = [
            {"asset": "BTC", "free": "0.625", "locked": "0.000", "avg_buy_price": 59200.00},
            {"asset": "ETH", "free": "4.150", "locked": "0.000", "avg_buy_price": 2850.00},
            {"asset": "SOL", "free": "45.000", "locked": "0.000", "avg_buy_price": 142.50},
            {"asset": "BNB", "free": "12.200", "locked": "0.000", "avg_buy_price": 540.00},
            {"asset": "NEAR", "free": "650.000", "locked": "0.000", "avg_buy_price": 4.80},
            {"asset": "USDT", "free": "3850.000", "locked": "0.000", "avg_buy_price": 1.00},
        ]

        # 24h ticker statistics (Price, Change %, High, Low, Volume)
        self.market_tickers = {
            "BTCUSDT": {
                "symbol": "BTCUSDT",
                "lastPrice": "63450.00",
                "priceChangePercent": "3.15",
                "highPrice": "64100.00",
                "lowPrice": "61200.00",
                "volume": "28450.12",
                "quoteVolume": "1785000000.00",
            },
            "ETHUSDT": {
                "symbol": "ETHUSDT",
                "lastPrice": "2720.00",
                "priceChangePercent": "-2.45",
                "highPrice": "2810.00",
                "lowPrice": "2680.00",
                "volume": "195400.50",
                "quoteVolume": "535000000.00",
            },
            "SOLUSDT": {
                "symbol": "SOLUSDT",
                "lastPrice": "164.80",
                "priceChangePercent": "9.42",
                "highPrice": "168.50",
                "lowPrice": "148.20",
                "volume": "4210500.00",
                "quoteVolume": "670000000.00",
            },
            "BNBUSDT": {
                "symbol": "BNBUSDT",
                "lastPrice": "582.40",
                "priceChangePercent": "1.80",
                "highPrice": "590.00",
                "lowPrice": "570.00",
                "volume": "385000.00",
                "quoteVolume": "224000000.00",
            },
            "NEARUSDT": {
                "symbol": "NEARUSDT",
                "lastPrice": "4.10",
                "priceChangePercent": "-7.85",
                "highPrice": "4.55",
                "lowPrice": "4.02",
                "volume": "18400000.00",
                "quoteVolume": "78000000.00",
            },
            "AVAXUSDT": {
                "symbol": "AVAXUSDT",
                "lastPrice": "28.40",
                "priceChangePercent": "4.12",
                "highPrice": "29.20",
                "lowPrice": "27.10",
                "volume": "1120000.00",
                "quoteVolume": "31800000.00",
            },
            "DOGEUSDT": {
                "symbol": "DOGEUSDT",
                "lastPrice": "0.1140",
                "priceChangePercent": "-1.20",
                "highPrice": "0.1180",
                "lowPrice": "0.1120",
                "volume": "420000000.00",
                "quoteVolume": "47880000.00",
            },
            "SUIUSDT": {
                "symbol": "SUIUSDT",
                "lastPrice": "1.82",
                "priceChangePercent": "14.65",
                "highPrice": "1.88",
                "lowPrice": "1.58",
                "volume": "54000000.00",
                "quoteVolume": "98280000.00",
            },
            "LINKUSDT": {
                "symbol": "LINKUSDT",
                "lastPrice": "12.25",
                "priceChangePercent": "2.80",
                "highPrice": "12.60",
                "lowPrice": "11.90",
                "volume": "2100000.00",
                "quoteVolume": "25725000.00",
            },
            "ARBUSDT": {
                "symbol": "ARBUSDT",
                "lastPrice": "0.585",
                "priceChangePercent": "-3.40",
                "highPrice": "0.612",
                "lowPrice": "0.578",
                "volume": "32000000.00",
                "quoteVolume": "18720000.00",
            },
            "PEPEUSDT": {
                "symbol": "PEPEUSDT",
                "lastPrice": "0.0000095",
                "priceChangePercent": "8.30",
                "highPrice": "0.0000098",
                "lowPrice": "0.0000087",
                "volume": "14500000000000.00",
                "quoteVolume": "137750000.00",
            },
            "USDTUSDT": {
                "symbol": "USDTUSDT",
                "lastPrice": "1.00",
                "priceChangePercent": "0.01",
                "highPrice": "1.0005",
                "lowPrice": "0.9995",
                "volume": "5000000000.00",
                "quoteVolume": "5000000000.00",
            },
        }

    def get_account_balances(self) -> List[Dict[str, Any]]:
        """Return simulated account spot balances."""
        return [
            {
                "asset": item["asset"],
                "free": item["free"],
                "locked": item["locked"],
                "avg_buy_price": item["avg_buy_price"],
            }
            for item in self.holdings
        ]

    def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """Return simulated 24h ticker for a symbol."""
        sym = symbol.upper()
        if sym in self.market_tickers:
            return self.market_tickers[sym]
        # Unknown symbol fallback - never fabricate a nonzero price
        return {
            "symbol": sym,
            "lastPrice": "0.00",
            "priceChangePercent": "0.00",
            "highPrice": "0.00",
            "lowPrice": "0.00",
            "volume": "0.00",
            "quoteVolume": "0.00",
        }

    def get_klines_history(self, symbol: str, limit: int = 7) -> List[List[Any]]:
        """Return simulated 7-day daily candlestick (kline) data."""
        # Standard Binance kline structure:
        # [OpenTime, Open, High, Low, Close, Volume, CloseTime, ...]
        now_ms = int(time.time() * 1000)
        day_ms = 86400 * 1000
        
        last_price = float(self.get_ticker_24hr(symbol).get("lastPrice", 100.0))
        pct_change = float(self.get_ticker_24hr(symbol).get("priceChangePercent", 0.0))
        
        # Build 7-day trend backwards
        klines = []
        base_price = last_price / (1.0 + (pct_change / 100.0))
        for i in range(limit - 1, -1, -1):
            t_open = now_ms - (i * day_ms)
            # Slight synthetic drift
            factor = 1.0 + ((limit - 1 - i) * (pct_change / (limit * 100.0)))
            c = round(base_price * factor, 4)
            o = round(c * 0.995, 4)
            h = round(max(o, c) * 1.015, 4)
            l = round(min(o, c) * 0.985, 4)
            v = 10000.0 + (i * 1500.0)
            klines.append([t_open, str(o), str(h), str(l), str(c), str(v), t_open + day_ms - 1])
            
        return klines

    def get_market_overview(self, watchlist: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Return comprehensive market overview across a watchlist of assets.
        Calculates top gainers, top losers, total volume, and sentiment.
        """
        if not watchlist:
            watchlist = ["BTC", "ETH", "SOL", "BNB", "SUI", "NEAR", "AVAX", "PEPE", "DOGE", "LINK", "ARB"]

        items = []
        total_vol_usd = 0.0

        for asset in watchlist:
            sym = f"{asset.upper()}USDT"
            t = self.get_ticker_24hr(sym)
            price = float(t.get("lastPrice", 0.0))
            change_pct = float(t.get("priceChangePercent", 0.0))
            quote_vol = float(t.get("quoteVolume", 0.0))
            total_vol_usd += quote_vol

            items.append({
                "asset": asset.upper(),
                "symbol": sym,
                "price": price,
                "priceChangePercent": change_pct,
                "high24h": float(t.get("highPrice", price)),
                "low24h": float(t.get("lowPrice", price)),
                "volume24hUsd": quote_vol,
            })

        # Rank by performance
        sorted_by_change = sorted(items, key=lambda x: x["priceChangePercent"], reverse=True)
        top_gainers = sorted_by_change[:3]
        top_losers = sorted_by_change[-2:]

        # Classify market sentiment
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
