"""
Binance USDT-M Futures analytics and derivatives intelligence.
Computes margin ratio, liquidation distances, effective leverage, and net delta exposure.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class FuturesPosition:
    symbol: str
    side: str  # "LONG" or "SHORT"
    amount: float
    notional_usd: float
    entry_price: float
    mark_price: float
    liquidation_price: float
    leverage: int
    margin_type: str  # "cross" or "isolated"
    unrealized_pnl_usd: float
    unrealized_pnl_pct: float
    liquidation_distance_pct: float  # % change to trigger liquidation
    funding_rate: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "amount": round(self.amount, 4),
            "notional_usd": round(self.notional_usd, 2),
            "entry_price": round(self.entry_price, 4),
            "mark_price": round(self.mark_price, 4),
            "liquidation_price": round(self.liquidation_price, 4),
            "leverage": self.leverage,
            "margin_type": self.margin_type,
            "unrealized_pnl_usd": round(self.unrealized_pnl_usd, 2),
            "unrealized_pnl_pct": round(self.unrealized_pnl_pct, 2),
            "liquidation_distance_pct": round(self.liquidation_distance_pct, 2),
            "funding_rate": round(self.funding_rate, 6) if self.funding_rate is not None else None,
        }


@dataclass
class FuturesAccountSummary:
    total_margin_balance_usd: float
    total_wallet_balance_usd: float
    total_unrealized_pnl_usd: float
    total_maint_margin_usd: float
    total_initial_margin_usd: float
    available_balance_usd: float
    margin_ratio_pct: float
    effective_leverage: float
    positions: List[FuturesPosition] = field(default_factory=list)
    net_delta_usd: float = 0.0
    risk_status: str = "SAFE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_margin_balance_usd": round(self.total_margin_balance_usd, 2),
            "total_wallet_balance_usd": round(self.total_wallet_balance_usd, 2),
            "total_unrealized_pnl_usd": round(self.total_unrealized_pnl_usd, 2),
            "total_maint_margin_usd": round(self.total_maint_margin_usd, 2),
            "total_initial_margin_usd": round(self.total_initial_margin_usd, 2),
            "available_balance_usd": round(self.available_balance_usd, 2),
            "margin_ratio_pct": round(self.margin_ratio_pct, 2),
            "effective_leverage": round(self.effective_leverage, 2),
            "net_delta_usd": round(self.net_delta_usd, 2),
            "risk_status": self.risk_status,
            "position_count": len(self.positions),
            "positions": [p.to_dict() for p in self.positions],
        }


class FuturesAnalyzer:
    """Evaluates Binance Futures derivative positions, margin ratio, and liquidation cushions."""

    @classmethod
    def analyze(
        cls,
        raw_futures_data: Dict[str, Any],
        mark_prices: Optional[List[Dict[str, Any]]] = None,
    ) -> FuturesAccountSummary:
        if not raw_futures_data:
            return FuturesAccountSummary(
                total_margin_balance_usd=0.0,
                total_wallet_balance_usd=0.0,
                total_unrealized_pnl_usd=0.0,
                total_maint_margin_usd=0.0,
                total_initial_margin_usd=0.0,
                available_balance_usd=0.0,
                margin_ratio_pct=0.0,
                effective_leverage=0.0,
                positions=[],
                net_delta_usd=0.0,
                risk_status="SAFE",
            )

        margin_balance = float(raw_futures_data.get("totalMarginBalance", 0.0))
        wallet_balance = float(raw_futures_data.get("totalWalletBalance", 0.0))
        unrealized_pnl = float(raw_futures_data.get("totalUnrealizedProfit", 0.0))
        maint_margin = float(raw_futures_data.get("totalMaintMargin", 0.0))
        initial_margin = float(raw_futures_data.get("totalInitialMargin", 0.0))
        avail_balance = float(raw_futures_data.get("availableBalance", 0.0))

        # Funding rate mapping if available
        funding_map = {}
        if mark_prices:
            for item in mark_prices:
                sym = item.get("symbol", "").upper()
                rate = item.get("lastFundingRate")
                if rate is not None:
                    try:
                        funding_map[sym] = float(rate)
                    except (ValueError, TypeError):
                        pass

        positions: List[FuturesPosition] = []
        raw_positions = raw_futures_data.get("positions", [])
        total_notional = 0.0
        net_delta = 0.0

        for p in raw_positions:
            amt = float(p.get("positionAmt", 0.0))
            if amt == 0.0:
                continue

            sym = p.get("symbol", "").upper()
            side = "LONG" if amt > 0 else "SHORT"
            entry_price = float(p.get("entryPrice", 0.0))
            mark_price = float(p.get("markPrice", entry_price))
            liq_price = float(p.get("liquidationPrice", 0.0))
            leverage = int(float(p.get("leverage", 1)))
            isolated = bool(p.get("isolated", False))
            margin_type = "isolated" if isolated else "cross"
            pnl_usd = float(p.get("unrealizedProfit", 0.0))

            notional = abs(amt) * mark_price
            total_notional += notional

            # Delta direction (+ for Long, - for Short)
            if side == "LONG":
                net_delta += notional
            else:
                net_delta -= notional

            # PnL % relative to initial margin required
            initial_req = notional / leverage if leverage > 0 else notional
            pnl_pct = (pnl_usd / initial_req * 100.0) if initial_req > 0 else 0.0

            # Liquidation distance calculation
            if liq_price > 0 and mark_price > 0:
                if side == "LONG":
                    liq_dist_pct = ((mark_price - liq_price) / mark_price) * 100.0
                else:
                    liq_dist_pct = ((liq_price - mark_price) / mark_price) * 100.0
            else:
                liq_dist_pct = 999.0  # negligible liquidation risk

            funding_rate = funding_map.get(sym)

            positions.append(
                FuturesPosition(
                    symbol=sym,
                    side=side,
                    amount=amt,
                    notional_usd=notional,
                    entry_price=entry_price,
                    mark_price=mark_price,
                    liquidation_price=liq_price,
                    leverage=leverage,
                    margin_type=margin_type,
                    unrealized_pnl_usd=pnl_usd,
                    unrealized_pnl_pct=pnl_pct,
                    liquidation_distance_pct=liq_dist_pct,
                    funding_rate=funding_rate,
                )
            )

        # Margin ratio: maintenance margin / total margin balance
        margin_ratio = (maint_margin / margin_balance * 100.0) if margin_balance > 0 else 0.0
        effective_leverage = (total_notional / margin_balance) if margin_balance > 0 else 0.0

        # Assess risk status
        min_liq_dist = min((p.liquidation_distance_pct for p in positions), default=100.0)

        if margin_ratio >= 80.0 or min_liq_dist < 8.0:
            risk_status = "CRITICAL_LIQUIDATION_RISK"
        elif margin_ratio >= 50.0 or min_liq_dist < 15.0 or effective_leverage >= 10.0:
            risk_status = "WARNING"
        elif margin_ratio >= 25.0 or effective_leverage >= 4.0:
            risk_status = "MODERATE"
        else:
            risk_status = "SAFE"

        # Sort positions by notional USD descending
        positions.sort(key=lambda x: x.notional_usd, reverse=True)

        return FuturesAccountSummary(
            total_margin_balance_usd=margin_balance,
            total_wallet_balance_usd=wallet_balance,
            total_unrealized_pnl_usd=unrealized_pnl,
            total_maint_margin_usd=maint_margin,
            total_initial_margin_usd=initial_margin,
            available_balance_usd=avail_balance,
            margin_ratio_pct=margin_ratio,
            effective_leverage=effective_leverage,
            positions=positions,
            net_delta_usd=net_delta,
            risk_status=risk_status,
        )
