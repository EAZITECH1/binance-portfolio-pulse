"""
Market trend analysis and technical metrics calculator for held crypto assets.
"""
import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class MarketTrendHighlight:
    symbol: str
    asset: str
    current_price: float
    price_change_24h_pct: float
    high_24h: float
    low_24h: float
    volume_24h: float
    quote_volume_24h: float
    sma_7d: Optional[float] = None
    price_vs_sma_pct: Optional[float] = None
    volatility_7d_pct: Optional[float] = None
    trend_sentiment: str = "NEUTRAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "asset": self.asset,
            "current_price": round(self.current_price, 4),
            "price_change_24h_pct": round(self.price_change_24h_pct, 2),
            "high_24h": round(self.high_24h, 4),
            "low_24h": round(self.low_24h, 4),
            "volume_24h": round(self.volume_24h, 2),
            "quote_volume_24h": round(self.quote_volume_24h, 2),
            "sma_7d": round(self.sma_7d, 4) if self.sma_7d is not None else None,
            "price_vs_sma_pct": (
                round(self.price_vs_sma_pct, 2) if self.price_vs_sma_pct is not None else None
            ),
            "volatility_7d_pct": (
                round(self.volatility_7d_pct, 2) if self.volatility_7d_pct is not None else None
            ),
            "trend_sentiment": self.trend_sentiment,
        }


class MarketTrendAnalyzer:
    """Calculates momentum, moving averages, and historical volatility."""

    @classmethod
    def analyze_asset_trend(
        cls,
        asset: str,
        ticker: Dict[str, Any],
        klines: Optional[List[List[Any]]] = None,
    ) -> MarketTrendHighlight:
        """
        Analyzes 24h ticker data and optional candlestick bars.
        """
        curr_price = float(ticker.get("lastPrice", 0.0))
        pct_change_24h = float(ticker.get("priceChangePercent", 0.0))
        high_24h = float(ticker.get("highPrice", curr_price))
        low_24h = float(ticker.get("lowPrice", curr_price))
        volume = float(ticker.get("volume", 0.0))
        quote_volume = float(ticker.get("quoteVolume", 0.0))

        sma_7d = None
        price_vs_sma = None
        volatility_7d = None

        if klines and len(klines) >= 3:
            # Extract closing prices
            closes = [float(k[4]) for k in klines]
            sma_7d = sum(closes) / len(closes)
            price_vs_sma = ((curr_price - sma_7d) / sma_7d * 100.0) if sma_7d > 0 else 0.0

            # Calculate daily returns standard deviation (daily volatility)
            if len(closes) > 1:
                daily_returns = [
                    (closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))
                ]
                mean_ret = sum(daily_returns) / len(daily_returns)
                variance = sum((r - mean_ret) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
                volatility_7d = math.sqrt(variance) * 100.0

        # Classify trend sentiment
        if pct_change_24h >= 6.0:
            sentiment = "BULLISH_SURGE"
        elif pct_change_24h >= 1.5:
            sentiment = "MODERATE_UP"
        elif pct_change_24h <= -6.0:
            sentiment = "BEARISH_DROP"
        elif pct_change_24h <= -1.5:
            sentiment = "MODERATE_DOWN"
        else:
            sentiment = "CONSOLIDATION"

        return MarketTrendHighlight(
            symbol=f"{asset}USDT",
            asset=asset,
            current_price=curr_price,
            price_change_24h_pct=pct_change_24h,
            high_24h=high_24h,
            low_24h=low_24h,
            volume_24h=volume,
            quote_volume_24h=quote_volume,
            sma_7d=sma_7d,
            price_vs_sma_pct=price_vs_sma,
            volatility_7d_pct=volatility_7d,
            trend_sentiment=sentiment,
        )
