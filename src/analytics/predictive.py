"""
Predictive future balance engine and quantitative scenario stress-testing.
Calculates real historical volatility and asset betas from Binance 30-day klines,
and models forward-looking portfolio balances across Bull, Bear, and Black Swan scenarios.
"""
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .portfolio import PortfolioSummary
from .futures import FuturesAccountSummary


@dataclass
class ScenarioOutcome:
    name: str
    description: str
    btc_benchmark_change_pct: float
    projected_balance_usd: float
    net_pnl_usd: float
    net_pnl_pct: float
    futures_impact_usd: float = 0.0
    liquidation_triggered: bool = False
    warning_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "btc_benchmark_change_pct": round(self.btc_benchmark_change_pct, 2),
            "projected_balance_usd": round(self.projected_balance_usd, 2),
            "net_pnl_usd": round(self.net_pnl_usd, 2),
            "net_pnl_pct": round(self.net_pnl_pct, 2),
            "futures_impact_usd": round(self.futures_impact_usd, 2),
            "liquidation_triggered": self.liquidation_triggered,
            "warning_notes": self.warning_notes,
        }


@dataclass
class PredictiveBalanceReport:
    current_total_balance_usd: float
    spot_valuation_usd: float
    futures_margin_usd: float
    asset_betas: Dict[str, float]
    asset_volatilities_annual_pct: Dict[str, float]
    portfolio_daily_volatility_pct: float
    portfolio_annual_volatility_pct: float
    projected_7d_base_usd: float
    projected_30d_base_usd: float
    var_95_7d_usd: float
    var_95_7d_pct: float
    var_99_7d_usd: float
    var_99_7d_pct: float
    scenarios: List[ScenarioOutcome] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_total_balance_usd": round(self.current_total_balance_usd, 2),
            "spot_valuation_usd": round(self.spot_valuation_usd, 2),
            "futures_margin_usd": round(self.futures_margin_usd, 2),
            "asset_betas": {k: round(v, 2) for k, v in self.asset_betas.items()},
            "asset_volatilities_annual_pct": {
                k: round(v, 2) for k, v in self.asset_volatilities_annual_pct.items()
            },
            "portfolio_daily_volatility_pct": round(self.portfolio_daily_volatility_pct, 2),
            "portfolio_annual_volatility_pct": round(self.portfolio_annual_volatility_pct, 2),
            "projected_7d_base_usd": round(self.projected_7d_base_usd, 2),
            "projected_30d_base_usd": round(self.projected_30d_base_usd, 2),
            "var_95_7d_usd": round(self.var_95_7d_usd, 2),
            "var_95_7d_pct": round(self.var_95_7d_pct, 2),
            "var_99_7d_usd": round(self.var_99_7d_usd, 2),
            "var_99_7d_pct": round(self.var_99_7d_pct, 2),
            "scenarios": [s.to_dict() for s in self.scenarios],
        }


class PredictiveBalanceEngine:
    """Computes empirical asset metrics and forward-looking stress test scenarios."""

    DEFAULT_BETAS = {
        "BTC": 1.00,
        "ETH": 1.15,
        "SOL": 1.45,
        "BNB": 0.85,
        "NEAR": 1.50,
        "AVAX": 1.40,
        "SUI": 1.65,
        "DOGE": 1.70,
        "PEPE": 2.10,
        "LINK": 1.25,
        "USDT": 0.00,
        "USDC": 0.00,
        "FDUSD": 0.00,
    }

    @staticmethod
    def _extract_daily_returns(klines: List[List[Any]]) -> List[float]:
        """Extract percentage daily close-to-close returns from klines."""
        if not klines or len(klines) < 2:
            return []
        closes = []
        for k in klines:
            try:
                closes.append(float(k[4]))  # close price is index 4
            except (IndexError, ValueError, TypeError):
                pass
        returns = []
        for i in range(1, len(closes)):
            prev = closes[i - 1]
            curr = closes[i]
            if prev > 0:
                returns.append((curr - prev) / prev)
        return returns

    @classmethod
    def calculate_betas_and_volatilities(
        cls,
        klines_by_symbol: Dict[str, List[List[Any]]],
        assets: List[str],
    ) -> tuple[Dict[str, float], Dict[str, float]]:
        """
        Calculates real 30-day historical volatilities and Betas relative to BTC.
        """
        returns_by_asset: Dict[str, List[float]] = {}
        volatilities: Dict[str, float] = {}
        betas: Dict[str, float] = {}

        # 1. Extract returns
        for asset in assets:
            a_up = asset.upper()
            if a_up in ("USDT", "USDC", "FDUSD", "DAI"):
                volatilities[a_up] = 0.0
                betas[a_up] = 0.0
                continue

            sym = f"{a_up}USDT"
            klines = klines_by_symbol.get(sym, [])
            rets = cls._extract_daily_returns(klines)
            if rets:
                returns_by_asset[a_up] = rets
                mean_r = sum(rets) / len(rets)
                variance = sum((r - mean_r) ** 2 for r in rets) / (len(rets) - 1) if len(rets) > 1 else 0.0
                daily_std = math.sqrt(variance)
                annual_vol = daily_std * math.sqrt(365) * 100.0
                volatilities[a_up] = annual_vol
            else:
                volatilities[a_up] = 65.0  # sensible crypto baseline

        # 2. Compute Beta relative to BTC
        btc_returns = returns_by_asset.get("BTC", [])
        btc_var = 0.0
        btc_mean = 0.0
        if len(btc_returns) > 1:
            btc_mean = sum(btc_returns) / len(btc_returns)
            btc_var = sum((r - btc_mean) ** 2 for r in btc_returns) / (len(btc_returns) - 1)

        for asset in assets:
            a_up = asset.upper()
            if a_up in ("USDT", "USDC", "FDUSD", "DAI"):
                betas[a_up] = 0.0
                continue
            if a_up == "BTC":
                betas["BTC"] = 1.00
                continue

            a_returns = returns_by_asset.get(a_up, [])
            if btc_var > 0 and a_returns and len(a_returns) == len(btc_returns):
                a_mean = sum(a_returns) / len(a_returns)
                cov = sum(
                    (a_returns[i] - a_mean) * (btc_returns[i] - btc_mean)
                    for i in range(len(btc_returns))
                ) / (len(btc_returns) - 1)
                beta_val = cov / btc_var
                # Clamp within reasonable market bounds
                betas[a_up] = max(0.2, min(3.5, beta_val))
            else:
                betas[a_up] = cls.DEFAULT_BETAS.get(a_up, 1.30)

        return betas, volatilities

    @classmethod
    def forecast(
        cls,
        spot_summary: PortfolioSummary,
        futures_summary: Optional[FuturesAccountSummary] = None,
        klines_by_symbol: Optional[Dict[str, List[List[Any]]]] = None,
    ) -> PredictiveBalanceReport:
        """
        Executes multi-factor scenario forecasting and parametric VaR estimation.
        """
        klines_by_symbol = klines_by_symbol or {}
        held_assets = [p.asset for p in spot_summary.positions]
        if "BTC" not in held_assets:
            held_assets.append("BTC")

        betas, volatilities = cls.calculate_betas_and_volatilities(klines_by_symbol, held_assets)

        spot_val = spot_summary.total_value_usd
        futures_val = futures_summary.total_margin_balance_usd if futures_summary else 0.0
        current_total = spot_val + futures_val

        if current_total <= 0:
            return PredictiveBalanceReport(
                current_total_balance_usd=0.0,
                spot_valuation_usd=0.0,
                futures_margin_usd=0.0,
                asset_betas=betas,
                asset_volatilities_annual_pct=volatilities,
                portfolio_daily_volatility_pct=0.0,
                portfolio_annual_volatility_pct=0.0,
                projected_7d_base_usd=0.0,
                projected_30d_base_usd=0.0,
                var_95_7d_usd=0.0,
                var_95_7d_pct=0.0,
                var_99_7d_usd=0.0,
                var_99_7d_pct=0.0,
                scenarios=[],
            )

        # Weighted portfolio daily volatility
        weighted_annual_vol = 0.0
        for p in spot_summary.positions:
            w = (p.usd_value / current_total) if current_total > 0 else 0.0
            v = volatilities.get(p.asset, 60.0)
            weighted_annual_vol += w * v

        portfolio_daily_vol = (weighted_annual_vol / math.sqrt(365))

        # Base case drift: 30-day drift based on recent 24h trend dampened
        daily_drift = (spot_summary.total_24h_pnl_pct / 100.0) * 0.25
        projected_7d_base = current_total * (1.0 + daily_drift * 7)
        projected_30d_base = current_total * (1.0 + daily_drift * 30)

        # Parametric 7-Day Value-at-Risk (VaR)
        # z=1.645 for 95%, z=2.326 for 99%
        var_factor_7d = math.sqrt(7) * (portfolio_daily_vol / 100.0)
        var_95_7d_usd = current_total * (1.645 * var_factor_7d)
        var_95_7d_pct = 1.645 * var_factor_7d * 100.0

        var_99_7d_usd = current_total * (2.326 * var_factor_7d)
        var_99_7d_pct = 2.326 * var_factor_7d * 100.0

        # Scenario Definitions
        scenarios_cfg = [
            {
                "name": "Bull Surge (+15% BTC)",
                "description": "Market expansion: BTC surges +15%, alts follow based on empirical beta.",
                "btc_change": 15.0,
            },
            {
                "name": "Moderate Pullback (-8% BTC)",
                "description": "Healthy consolidation: BTC retraces -8%, testing near-term support.",
                "btc_change": -8.0,
            },
            {
                "name": "Bear Contraction (-15% BTC)",
                "description": "Risk-off correction: BTC drops -15%, higher-beta altcoins experience steeper selloffs.",
                "btc_change": -15.0,
            },
            {
                "name": "Flash Crash Shock (-30% BTC)",
                "description": "Black swan liquidity shock: BTC plummets -30%, testing derivative liquidation cushions.",
                "btc_change": -30.0,
            },
        ]

        scenario_outcomes: List[ScenarioOutcome] = []

        for sc in scenarios_cfg:
            btc_move = sc["btc_change"]
            spot_projected = 0.0
            notes = []

            # 1. Spot positions projection
            for p in spot_summary.positions:
                if p.is_stablecoin:
                    spot_projected += p.usd_value
                else:
                    b = betas.get(p.asset, 1.20)
                    asset_move_pct = btc_move * b
                    new_val = p.usd_value * (1.0 + (asset_move_pct / 100.0))
                    spot_projected += max(0.0, new_val)

            # 2. Futures positions projection and liquidation testing
            futures_impact = 0.0
            futures_projected_margin = futures_val
            liq_triggered = False

            if futures_summary and futures_summary.positions:
                for fp in futures_summary.positions:
                    sym_base = fp.symbol.replace("USDT", "")
                    b = betas.get(sym_base, 1.0 if sym_base == "BTC" else 1.20)
                    price_change_pct = btc_move * b
                    new_mark = fp.mark_price * (1.0 + (price_change_pct / 100.0))

                    # Position PnL delta
                    if fp.side == "LONG":
                        pos_pnl_delta = fp.amount * (new_mark - fp.mark_price)
                        # Check liquidation
                        if fp.liquidation_price > 0 and new_mark <= fp.liquidation_price:
                            liq_triggered = True
                            notes.append(
                                f"⚠️ LIQUIDATION ALERT: {fp.symbol} LONG would breach liquidation price ${fp.liquidation_price:,.2f} at projected price ${new_mark:,.2f}!"
                            )
                    else:  # SHORT
                        pos_pnl_delta = abs(fp.amount) * (fp.mark_price - new_mark)
                        # Check liquidation
                        if fp.liquidation_price > 0 and new_mark >= fp.liquidation_price:
                            liq_triggered = True
                            notes.append(
                                f"⚠️ LIQUIDATION ALERT: {fp.symbol} SHORT would breach liquidation price ${fp.liquidation_price:,.2f} at projected price ${new_mark:,.2f}!"
                            )

                    futures_impact += pos_pnl_delta

                if liq_triggered:
                    futures_projected_margin = 0.0  # wipeout if liquidated
                else:
                    futures_projected_margin = max(0.0, futures_val + futures_impact)

            projected_total = spot_projected + futures_projected_margin
            net_pnl = projected_total - current_total
            net_pnl_pct = (net_pnl / current_total * 100.0) if current_total > 0 else 0.0

            has_active_futures = bool(futures_summary and futures_summary.is_active and (futures_summary.total_margin_balance_usd > 0 or futures_summary.positions))
            if not notes and btc_move < 0:
                if has_active_futures:
                    notes.append("Derivatives margin buffer holds; no liquidation triggered.")
                else:
                    notes.append("Spot-only holdings absorb market pullback without liquidation risk.")
            elif not notes and btc_move > 0:
                notes.append("High-beta holdings provide leveraged upside capture.")

            scenario_outcomes.append(
                ScenarioOutcome(
                    name=sc["name"],
                    description=sc["description"],
                    btc_benchmark_change_pct=btc_move,
                    projected_balance_usd=projected_total,
                    net_pnl_usd=net_pnl,
                    net_pnl_pct=net_pnl_pct,
                    futures_impact_usd=futures_impact,
                    liquidation_triggered=liq_triggered,
                    warning_notes=notes,
                )
            )

        return PredictiveBalanceReport(
            current_total_balance_usd=current_total,
            spot_valuation_usd=spot_val,
            futures_margin_usd=futures_val,
            asset_betas=betas,
            asset_volatilities_annual_pct=volatilities,
            portfolio_daily_volatility_pct=portfolio_daily_vol,
            portfolio_annual_volatility_pct=weighted_annual_vol,
            projected_7d_base_usd=projected_7d_base,
            projected_30d_base_usd=projected_30d_base,
            var_95_7d_usd=var_95_7d_usd,
            var_95_7d_pct=var_95_7d_pct,
            var_99_7d_usd=var_99_7d_usd,
            var_99_7d_pct=var_99_7d_pct,
            scenarios=scenario_outcomes,
        )
