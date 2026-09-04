"""
Quantitative risk analysis engine for crypto portfolios.
Detects concentration risk, excessive volatility, sharp drawdowns, and liquidity buffers.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

from .portfolio import PortfolioSummary
from .market_trends import MarketTrendHighlight


@dataclass
class RiskFlag:
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    category: str  # "CONCENTRATION", "VOLATILITY", "DRAWDOWN", "LIQUIDITY", "DIVERSIFICATION"
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
    ) -> RiskAssessment:
        flags: List[RiskFlag] = []
        score_penalties = 0

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
