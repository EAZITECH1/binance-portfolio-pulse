"""
Quantitative risk analysis engine for crypto portfolios.
Detects concentration risk, excessive volatility, sharp drawdowns, and liquidity buffers.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .portfolio import PortfolioSummary
from .market_trends import MarketTrendHighlight
from .futures import FuturesAccountSummary
from .predictive import PredictiveBalanceReport


@dataclass
class RiskFlag:
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    category: str  # "CONCENTRATION", "VOLATILITY", "DRAWDOWN", "LIQUIDITY", "DIVERSIFICATION", "FUTURES", "VAR"
    title: str
    description: str
    action_item: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "action_item": self.action_item,
        }


@dataclass
class RiskAssessment:
    overall_score: int  # 1 to 10 scale (1 = Minimal Risk, 10 = Severe Risk)
    risk_level: str  # "CONSERVATIVE", "MODERATE", "ELEVATED", "HIGH"
    flags: List[RiskFlag]
    key_vulnerabilities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "flags": [f.to_dict() for f in self.flags],
            "key_vulnerabilities": self.key_vulnerabilities,
        }


class RiskAnalyzer:
    """Evaluates portfolio composition and market fluctuations for critical risk signals."""

    @classmethod
    def evaluate(
        cls,
        summary: PortfolioSummary,
        trends: Dict[str, MarketTrendHighlight],
        concentration_threshold: float = 0.35,
        volatility_threshold: float = 0.08,
        min_stablecoin_buffer: float = 0.10,
        futures_summary: Optional[FuturesAccountSummary] = None,
        predictive_report: Optional[PredictiveBalanceReport] = None,
    ) -> RiskAssessment:
        flags: List[RiskFlag] = []
        score_penalties = 0

        # 0. Zero Holdings Check
        if summary.total_value_usd <= 0 or summary.asset_count == 0:
            return RiskAssessment(
                overall_score=0,
                risk_level="LOW",
                flags=[],
                key_vulnerabilities=["No active token balances in account."],
            )

        # 1. Concentration Risk Checks
        for pos in summary.positions:
            if not pos.is_stablecoin:
                alloc_fraction = pos.allocation_pct / 100.0
                if alloc_fraction >= 0.50:
                    flags.append(
                        RiskFlag(
                            severity="CRITICAL",
                            category="CONCENTRATION",
                            title=f"Severe Concentration in {pos.asset} ({pos.allocation_pct:.1f}%)",
                            description=(
                                f"{pos.asset} constitutes over half ({pos.allocation_pct:.1f}%) of total portfolio value. "
                                f"A sharp downturn in {pos.asset} will disproportionately damage your overall balance."
                            ),
                            action_item=f"Consider rebalancing or taking partial profits in {pos.asset} into stablecoins or major assets.",
                        )
                    )
                    score_penalties += 3
                elif alloc_fraction >= concentration_threshold:
                    flags.append(
                        RiskFlag(
                            severity="HIGH",
                            category="CONCENTRATION",
                            title=f"High Concentration Risk in {pos.asset} ({pos.allocation_pct:.1f}%)",
                            description=(
                                f"{pos.asset} exceeds the prudent single-asset ceiling of {concentration_threshold * 100:.0f}%. "
                                f"Portfolio returns are heavily dependent on this single token's momentum."
                            ),
                            action_item=f"Review your target allocation and consider capping single alt positions below {concentration_threshold * 100:.0f}%.",
                        )
                    )
                    score_penalties += 2

        # 2. Volatility & Rapid Price Move Checks
        for pos in summary.positions:
            if pos.is_stablecoin:
                continue
            abs_change_fraction = abs(pos.change_24h_pct) / 100.0
            if abs_change_fraction >= (volatility_threshold * 1.5):  # e.g. > 12%
                flags.append(
                    RiskFlag(
                        severity="HIGH",
                        category="VOLATILITY",
                        title=f"Extreme Volatility on {pos.asset} ({pos.change_24h_pct:+.1f}% in 24h)",
                        description=(
                            f"{pos.asset} is experiencing massive price swings over the last 24 hours. "
                            f"Such volatility often precedes sharp mean reversions or sudden liquidation cascades."
                        ),
                        action_item="Verify stop-loss orders or evaluate trimming exposure if volatility exceeds your tolerance.",
                    )
                )
                score_penalties += 2
            elif abs_change_fraction >= volatility_threshold:
                flags.append(
                    RiskFlag(
                        severity="MEDIUM",
                        category="VOLATILITY",
                        title=f"Elevated Price Movement on {pos.asset} ({pos.change_24h_pct:+.1f}%)",
                        description=f"{pos.asset} moved more than {volatility_threshold * 100:.0f}% in 24 hours.",
                        action_item="Monitor support/resistance levels closely over the next trading session.",
                    )
                )
                score_penalties += 1

        # 3. Severe Drawdown Checks
        for pos in summary.positions:
            if not pos.is_stablecoin and pos.change_24h_pct <= -6.0:
                flags.append(
                    RiskFlag(
                        severity="HIGH",
                        category="DRAWDOWN",
                        title=f"Sharp Daily Drawdown on {pos.asset} ({pos.change_24h_pct:.1f}%)",
                        description=(
                            f"{pos.asset} dropped {pos.change_24h_pct:.1f}% today, dragging down your portfolio value by "
                            f"${abs(pos.change_24h_usd):,.2f}."
                        ),
                        action_item=f"Inspect broader market sentiment and protocol news regarding {pos.asset}.",
                    )
                )
                score_penalties += 2

        # 4. Liquidity & Defensive Buffer Checks
        stable_fraction = summary.stablecoin_pct / 100.0
        if stable_fraction < (min_stablecoin_buffer / 2):  # e.g. < 5%
            flags.append(
                RiskFlag(
                    severity="HIGH",
                    category="LIQUIDITY",
                    title=f"Depleted Cash/Stablecoin Buffer ({summary.stablecoin_pct:.1f}%)",
                    description=(
                        f"Only {summary.stablecoin_pct:.1f}% of your portfolio is in liquid stablecoins. "
                        f"You have almost no dry powder available to capitalize on market dips without selling depressed assets."
                    ),
                    action_item=f"Aim to maintain at least {min_stablecoin_buffer * 100:.0f}% in USDT/USDC to weather market turbulence.",
                )
            )
            score_penalties += 2
        elif stable_fraction < min_stablecoin_buffer:
            flags.append(
                RiskFlag(
                    severity="MEDIUM",
                    category="LIQUIDITY",
                    title=f"Below Recommended Cash Buffer ({summary.stablecoin_pct:.1f}%)",
                    description=(
                        f"Stablecoins represent {summary.stablecoin_pct:.1f}% of holdings, "
                        f"below the recommended {min_stablecoin_buffer * 100:.0f}% safety cushion."
                    ),
                    action_item="Consider building your reserve to provide flexibility during drawdowns.",
                )
            )
            score_penalties += 1

        # 5. Altcoin Overexposure Check
        major_assets = {"BTC", "ETH", "USDT", "USDC", "FDUSD"}
        alt_usd = sum(p.usd_value for p in summary.positions if p.asset not in major_assets)
        alt_pct = (alt_usd / summary.total_value_usd * 100.0) if summary.total_value_usd > 0 else 0.0
        if alt_pct > 40.0:
            flags.append(
                RiskFlag(
                    severity="MEDIUM",
                    category="DIVERSIFICATION",
                    title=f"Significant Altcoin Exposure ({alt_pct:.1f}%)",
                    description=(
                        f"Secondary altcoins represent {alt_pct:.1f}% of your portfolio. "
                        f"Altcoins typically exhibit higher beta and wider drawdown cycles than BTC or ETH."
                    ),
                    action_item="Ensure you are comfortable with broader market volatility.",
                )
            )
            score_penalties += 1

        # 6. Futures Margin & Liquidation Proximity Checks
        if futures_summary and futures_summary.positions:
            # Margin ratio evaluation
            if futures_summary.margin_ratio_pct >= 80.0:
                flags.append(
                    RiskFlag(
                        severity="CRITICAL",
                        category="FUTURES",
                        title=f"Critical Futures Margin Ratio ({futures_summary.margin_ratio_pct:.1f}%)",
                        description=(
                            f"Your derivatives maintenance margin is at {futures_summary.margin_ratio_pct:.1f}% of total margin balance. "
                            "You are at immediate risk of automated liquidation cascades."
                        ),
                        action_item="Deposit additional collateral or immediately reduce position sizes to protect margin balance.",
                    )
                )
                score_penalties += 4
            elif futures_summary.margin_ratio_pct >= 50.0:
                flags.append(
                    RiskFlag(
                        severity="HIGH",
                        category="FUTURES",
                        title=f"High Futures Margin Usage ({futures_summary.margin_ratio_pct:.1f}%)",
                        description=(
                            f"Derivatives margin ratio is {futures_summary.margin_ratio_pct:.1f}%. "
                            "Adverse market fluctuations may trigger margin calls."
                        ),
                        action_item="Monitor open derivative positions closely and maintain buffer collateral.",
                    )
                )
                score_penalties += 2

            # Liquidation proximity checks for individual positions
            for fp in futures_summary.positions:
                if fp.liquidation_distance_pct < 10.0:
                    flags.append(
                        RiskFlag(
                            severity="CRITICAL",
                            category="FUTURES",
                            title=f"Imminent Liquidation Threat on {fp.symbol} {fp.side} ({fp.liquidation_distance_pct:.1f}% buffer)",
                            description=(
                                f"{fp.symbol} {fp.side} is only {fp.liquidation_distance_pct:.1f}% away from liquidation price (${fp.liquidation_price:,.2f})."
                            ),
                            action_item="Add margin, set a protective stop loss, or de-risk the position immediately.",
                        )
                    )
                    score_penalties += 3
                elif fp.liquidation_distance_pct < 20.0:
                    flags.append(
                        RiskFlag(
                            severity="HIGH",
                            category="FUTURES",
                            title=f"Narrow Liquidation Cushion on {fp.symbol} {fp.side} ({fp.liquidation_distance_pct:.1f}%)",
                            description=(
                                f"{fp.symbol} {fp.side} has a {fp.liquidation_distance_pct:.1f}% buffer before reaching liquidation price (${fp.liquidation_price:,.2f})."
                            ),
                            action_item="Evaluate reducing leverage or setting tighter stop losses.",
                        )
                    )
                    score_penalties += 1

            # High effective leverage check
            if futures_summary.effective_leverage >= 8.0:
                flags.append(
                    RiskFlag(
                        severity="HIGH",
                        category="FUTURES",
                        title=f"High Effective Derivatives Leverage ({futures_summary.effective_leverage:.1f}x)",
                        description=(
                            f"Total notional futures exposure is {futures_summary.effective_leverage:.1f}x your margin balance. "
                            "Small price movements will cause large percentage swings in equity."
                        ),
                        action_item="De-leverage open positions to lower drawdown velocity.",
                    )
                )
                score_penalties += 2

        # 7. Predictive Value-at-Risk (VaR) Check
        if predictive_report and predictive_report.var_95_7d_pct >= 14.0:
            flags.append(
                RiskFlag(
                    severity="HIGH",
                    category="VAR",
                    title=f"Elevated 7-Day Statistical VaR ({predictive_report.var_95_7d_pct:.1f}%)",
                    description=(
                        f"95% 7-Day Value-at-Risk projects potential downside of ${predictive_report.var_95_7d_usd:,.2f} "
                        f"under standard market volatility patterns."
                    ),
                    action_item="Consider rebalancing high-beta assets into stablecoins to dampen portfolio variance.",
                )
            )
            score_penalties += 1

        # Calculate composite risk score (1-10 scale)
        base_score = 3
        composite_score = min(10, max(1, base_score + score_penalties))

        if composite_score <= 3:
            risk_level = "CONSERVATIVE"
        elif composite_score <= 5:
            risk_level = "MODERATE"
        elif composite_score <= 7:
            risk_level = "ELEVATED"
        else:
            risk_level = "HIGH"

        vulnerabilities = [f.title for f in flags if f.severity in ("HIGH", "CRITICAL")]

        return RiskAssessment(
            overall_score=composite_score,
            risk_level=risk_level,
            flags=flags,
            key_vulnerabilities=vulnerabilities,
        )
