"""
Binance Order Book (Market Depth & Liquidity) Analytics.
Fetches and analyzes bid/ask depth, spread, slippage estimation, and order book imbalance.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class OrderBookEntry:
    price: float
    quantity: float
    total_usd: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "price": round(self.price, 8),
            "quantity": round(self.quantity, 6),
            "total_usd": round(self.total_usd, 2),
        }


@dataclass
class OrderBookAnalysis:
    symbol: str
    best_bid: float
    best_ask: float
    mid_price: float
    spread_usd: float
    spread_bps: float  # Basis points (1 bp = 0.01%)
    bid_depth_usd: float
    ask_depth_usd: float
    total_liquidity_usd: float
    order_imbalance_ratio: float  # bid_depth / ask_depth (>1.0 indicates buy pressure)
    market_regime: str  # "TIGHT_SPREAD_LIQUID", "MODERATE_SPREAD", "WIDE_SPREAD_ILLIQUID"
    bids: List[OrderBookEntry] = field(default_factory=list)
    asks: List[OrderBookEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "best_bid": round(self.best_bid, 8),
            "best_ask": round(self.best_ask, 8),
            "mid_price": round(self.mid_price, 8),
            "spread_usd": round(self.spread_usd, 8),
            "spread_bps": round(self.spread_bps, 2),
            "bid_depth_usd": round(self.bid_depth_usd, 2),
            "ask_depth_usd": round(self.ask_depth_usd, 2),
            "total_liquidity_usd": round(self.total_liquidity_usd, 2),
            "order_imbalance_ratio": round(self.order_imbalance_ratio, 3),
            "market_regime": self.market_regime,
            "bids_sample": [b.to_dict() for b in self.bids[:5]],
            "asks_sample": [a.to_dict() for a in self.asks[:5]],
        }

    def format_summary(self) -> str:
        """Returns a clean plain-text markdown summary of the order book."""
        pressure = (
            "🟢 Strong Buy Pressure" if self.order_imbalance_ratio > 1.2
            else ("🔴 Heavy Sell Pressure" if self.order_imbalance_ratio < 0.8
            else "⚖️ Balanced Liquidity")
        )
        lines = [
            f"📊 **Binance Order Book Intelligence: {self.symbol}**",
            f"• **Best Bid:** ${self.best_bid:,.4f} | **Best Ask:** ${self.best_ask:,.4f}",
            f"• **Mid-Market Price:** ${self.mid_price:,.4f}",
            f"• **Bid/Ask Spread:** ${self.spread_usd:.6f} (`{self.spread_bps:.2f} bps` / `{self.spread_bps/100:.3f}%`)",
            f"• **Order Book Liquidity:** ${self.total_liquidity_usd:,.2f} (Bids: ${self.bid_depth_usd:,.2f} | Asks: ${self.ask_depth_usd:,.2f})",
            f"• **Depth Imbalance:** {pressure} (Bid/Ask Ratio: `{self.order_imbalance_ratio:.2f}`)",
            f"• **Market Quality:** `{self.market_regime}`",
        ]
        return "\n".join(lines)


class OrderBookAnalyzer:
    """Quantitative order book calculator."""

    @classmethod
    def analyze(cls, symbol: str, raw_depth: Dict[str, Any]) -> OrderBookAnalysis:
        raw_bids = raw_depth.get("bids", [])
        raw_asks = raw_depth.get("asks", [])

        parsed_bids: List[OrderBookEntry] = []
        parsed_asks: List[OrderBookEntry] = []

        total_bid_usd = 0.0
        for item in raw_bids:
            try:
                p = float(item[0])
                q = float(item[1])
                val = p * q
                parsed_bids.append(OrderBookEntry(price=p, quantity=q, total_usd=val))
                total_bid_usd += val
            except (IndexError, ValueError, TypeError):
                continue

        total_ask_usd = 0.0
        for item in raw_asks:
            try:
                p = float(item[0])
                q = float(item[1])
                val = p * q
                parsed_asks.append(OrderBookEntry(price=p, quantity=q, total_usd=val))
                total_ask_usd += val
            except (IndexError, ValueError, TypeError):
                continue

        best_bid = parsed_bids[0].price if parsed_bids else 0.0
        best_ask = parsed_asks[0].price if parsed_asks else 0.0

        if best_bid > 0 and best_ask > 0:
            mid = (best_bid + best_ask) / 2.0
            spread_usd = best_ask - best_bid
            spread_bps = (spread_usd / mid) * 10000.0 if mid > 0 else 0.0
        else:
            mid = max(best_bid, best_ask)
            spread_usd = 0.0
            spread_bps = 0.0

        imbalance = (total_bid_usd / total_ask_usd) if total_ask_usd > 0 else 1.0
        total_liq = total_bid_usd + total_ask_usd

        # Market quality classification
        if spread_bps <= 3.0:
            regime = "TIGHT_SPREAD_LIQUID"
        elif spread_bps <= 15.0:
            regime = "MODERATE_SPREAD"
        else:
            regime = "WIDE_SPREAD_ILLIQUID"

        return OrderBookAnalysis(
            symbol=symbol.upper(),
            best_bid=best_bid,
            best_ask=best_ask,
            mid_price=mid,
            spread_usd=spread_usd,
            spread_bps=spread_bps,
            bid_depth_usd=total_bid_usd,
            ask_depth_usd=total_ask_usd,
            total_liquidity_usd=total_liq,
            order_imbalance_ratio=imbalance,
            market_regime=regime,
            bids=parsed_bids,
            asks=parsed_asks,
        )
