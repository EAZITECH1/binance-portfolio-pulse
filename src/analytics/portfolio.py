"""
Portfolio valuation and asset allocation calculator.
Computes USD values, allocation percentages, cost-basis P&L, and 24h estimated returns.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AssetPosition:
    asset: str
    total_amount: float
    free_amount: float
    locked_amount: float
    current_price: float
    usd_value: float
    allocation_pct: float = 0.0
    avg_buy_price: Optional[float] = None
    unrealized_pnl_usd: Optional[float] = None
    unrealized_pnl_pct: Optional[float] = None
    change_24h_pct: float = 0.0
    change_24h_usd: float = 0.0
    is_stablecoin: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset": self.asset,
            "total_amount": round(self.total_amount, 6),
            "free_amount": round(self.free_amount, 6),
            "locked_amount": round(self.locked_amount, 6),
            "current_price": round(self.current_price, 4),
            "usd_value": round(self.usd_value, 2),
            "allocation_pct": round(self.allocation_pct, 2),
            "avg_buy_price": round(self.avg_buy_price, 4) if self.avg_buy_price else None,
            "unrealized_pnl_usd": (
                round(self.unrealized_pnl_usd, 2) if self.unrealized_pnl_usd is not None else None
            ),
            "unrealized_pnl_pct": (
                round(self.unrealized_pnl_pct, 2) if self.unrealized_pnl_pct is not None else None
            ),
            "change_24h_pct": round(self.change_24h_pct, 2),
            "change_24h_usd": round(self.change_24h_usd, 2),
            "is_stablecoin": self.is_stablecoin,
        }


@dataclass
class PortfolioSummary:
    total_value_usd: float
    positions: List[AssetPosition] = field(default_factory=list)
    total_24h_pnl_usd: float = 0.0
    total_24h_pnl_pct: float = 0.0
    total_unrealized_pnl_usd: float = 0.0
    stablecoin_value_usd: float = 0.0
    stablecoin_pct: float = 0.0
    asset_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_value_usd": round(self.total_value_usd, 2),
            "total_24h_pnl_usd": round(self.total_24h_pnl_usd, 2),
            "total_24h_pnl_pct": round(self.total_24h_pnl_pct, 2),
            "total_unrealized_pnl_usd": round(self.total_unrealized_pnl_usd, 2),
            "stablecoin_value_usd": round(self.stablecoin_value_usd, 2),
            "stablecoin_pct": round(self.stablecoin_pct, 2),
            "asset_count": self.asset_count,
            "positions": [p.to_dict() for p in self.positions],
        }


class PortfolioAnalyzer:
    """Calculates comprehensive portfolio metrics across held spot assets."""

    STABLECOINS = {"USDT", "USDC", "FDUSD", "BUSD", "DAI", "TUSD"}

    @classmethod
    def analyze(
        cls,
        raw_balances: List[Dict[str, Any]],
        tickers: Dict[str, Dict[str, Any]],
    ) -> PortfolioSummary:
        """
        Analyzes account balances in conjunction with ticker statistics.
        """
        positions: List[AssetPosition] = []
        total_usd_value = 0.0
        stablecoin_val = 0.0

        for item in raw_balances:
            asset = item.get("asset", "").upper()
            free = float(item.get("free", 0.0))
            locked = float(item.get("locked", 0.0))
            total_amount = free + locked

            if total_amount <= 0:
                continue

            avg_buy = item.get("avg_buy_price")
            avg_buy = float(avg_buy) if avg_buy is not None else None

            # Determine price and 24h change
            is_stable = asset in cls.STABLECOINS
            if is_stable:
                curr_price = 1.0
                change_24h_pct = 0.0
            else:
                symbol = f"{asset}USDT"
                ticker_data = tickers.get(symbol, {})
                curr_price = float(ticker_data.get("lastPrice", 0.0))
                change_24h_pct = float(ticker_data.get("priceChangePercent", 0.0))

            usd_value = total_amount * curr_price
            if usd_value < 1.0:  # Skip dust below $1
                continue

            # Calculate 24h PnL USD
            # previous_value = usd_value / (1 + change_24h_pct / 100)
            # pnl_24h = usd_value - previous_value
            pnl_24h_usd = usd_value * (change_24h_pct / (100.0 + change_24h_pct)) if (100.0 + change_24h_pct) != 0 else 0.0

            # Calculate Unrealized PnL if cost basis known
            unrealized_usd = None
            unrealized_pct = None
            if avg_buy and avg_buy > 0:
                unrealized_usd = (curr_price - avg_buy) * total_amount
                unrealized_pct = ((curr_price / avg_buy) - 1.0) * 100.0

            pos = AssetPosition(
                asset=asset,
                total_amount=total_amount,
                free_amount=free,
                locked_amount=locked,
                current_price=curr_price,
                usd_value=usd_value,
                avg_buy_price=avg_buy,
                unrealized_pnl_usd=unrealized_usd,
                unrealized_pnl_pct=unrealized_pct,
                change_24h_pct=change_24h_pct,
                change_24h_usd=pnl_24h_usd,
                is_stablecoin=is_stable,
            )

            positions.append(pos)
            total_usd_value += usd_value
            if is_stable:
                stablecoin_val += usd_value

        # Calculate allocation percentages and aggregate portfolio totals
        total_24h_pnl_usd = 0.0
        total_unrealized_pnl = 0.0

        for p in positions:
            p.allocation_pct = (p.usd_value / total_usd_value * 100.0) if total_usd_value > 0 else 0.0
            total_24h_pnl_usd += p.change_24h_usd
            if p.unrealized_pnl_usd is not None:
                total_unrealized_pnl += p.unrealized_pnl_usd

        # Sort positions descending by USD value
        positions.sort(key=lambda x: x.usd_value, reverse=True)

        # 24h portfolio overall percentage change
        prev_portfolio_val = total_usd_value - total_24h_pnl_usd
        total_24h_pnl_pct = (
            (total_24h_pnl_usd / prev_portfolio_val * 100.0) if prev_portfolio_val > 0 else 0.0
        )

        stable_pct = (stablecoin_val / total_usd_value * 100.0) if total_usd_value > 0 else 0.0

        return PortfolioSummary(
            total_value_usd=total_usd_value,
            positions=positions,
            total_24h_pnl_usd=total_24h_pnl_usd,
            total_24h_pnl_pct=total_24h_pnl_pct,
            total_unrealized_pnl_usd=total_unrealized_pnl,
            stablecoin_value_usd=stablecoin_val,
            stablecoin_pct=stable_pct,
            asset_count=len(positions),
        )
