"""
Realistic mock data provider for Binance PortfolioPulse AI.
Enables judges and reviewers to test the entire agent pipeline without requiring live API keys.
"""
from typing import Dict, Any, List
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
        # Generic fallback
        return {
            "symbol": sym,
            "lastPrice": "10.00",
            "priceChangePercent": "0.00",
            "highPrice": "10.50",
            "lowPrice": "9.50",
            "volume": "1000.00",
            "quoteVolume": "10000.00",
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
