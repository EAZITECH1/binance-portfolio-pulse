"""
Plain-language AI summary generator.
Translates crypto analytics, P&L, and risk flags into clear, conversational summaries
that any non-trader can immediately understand.
Works 100% offline via a built-in financial reasoning engine, with optional Gemini/OpenAI enhancement.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .portfolio import PortfolioSummary
from .risk_analyzer import RiskAssessment
from .market_trends import MarketTrendHighlight
from ..utils.logger import logger


@dataclass
class PlainLanguageSummary:
    headline: str
    overview: str
    market_drivers: str
    risk_perspective: str
    actionable_tips: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "headline": self.headline,
            "overview": self.overview,
            "market_drivers": self.market_drivers,
            "risk_perspective": self.risk_perspective,
            "actionable_tips": self.actionable_tips,
        }


class AISummaryGenerator:
    """Generates plain-language insights for non-technical crypto holders."""

    @classmethod
    def generate(
        cls,
        summary: PortfolioSummary,
        risk: RiskAssessment,
        trends: Dict[str, MarketTrendHighlight],
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ) -> PlainLanguageSummary:
        """
        Synthesizes portfolio data into clear everyday language.
        """
        # Top performer and worst performer over 24h
        crypto_positions = [p for p in summary.positions if not p.is_stablecoin]
        crypto_positions_by_change = sorted(crypto_positions, key=lambda x: x.change_24h_pct, reverse=True)

        top_gain = crypto_positions_by_change[0] if crypto_positions_by_change else None
        worst_drop = crypto_positions_by_change[-1] if crypto_positions_by_change else None

        # Determine daily direction
        pnl_sign = "+" if summary.total_24h_pnl_usd >= 0 else "-"
        abs_pnl_usd = abs(summary.total_24h_pnl_usd)
        abs_pnl_pct = abs(summary.total_24h_pnl_pct)

        # 1. Headline
        if summary.total_24h_pnl_usd >= 0:
            if top_gain and top_gain.change_24h_pct > 5.0:
                headline = (
                    f"Your portfolio climbed {abs_pnl_pct:.1f}% (+${abs_pnl_usd:,.2f}) today, "
                    f"powered by a surge in {top_gain.asset} (+{top_gain.change_24h_pct:.1f}%)."
                )
            else:
                headline = (
                    f"Your balance gained {abs_pnl_pct:.1f}% (+${abs_pnl_usd:,.2f}) today, "
                    f"reflecting steady green across your holdings."
                )
        else:
            if worst_drop and worst_drop.change_24h_pct < -5.0:
                headline = (
                    f"Your portfolio retreated {abs_pnl_pct:.1f}% (-${abs_pnl_usd:,.2f}) today, "
                    f"primarily weighed down by a pullback in {worst_drop.asset} ({worst_drop.change_24h_pct:.1f}%)."
                )
            else:
                headline = (
                    f"Your balance dipped slightly by {abs_pnl_pct:.1f}% (-${abs_pnl_usd:,.2f}) today "
                    f"in mild market consolidation."
                )

        # 2. Plain-language overview
        top_holding = summary.positions[0] if summary.positions else None
        top_holding_str = (
            f"Your largest holding is {top_holding.asset}, which makes up {top_holding.allocation_pct:.1f}% "
            f"of your total balance (${top_holding.usd_value:,.2f}). "
            if top_holding
            else ""
        )

        overview = (
            f"As of today, your total account is valued at ${summary.total_value_usd:,.2f}. "
            f"Over the past 24 hours, your net change was {pnl_sign}${abs_pnl_usd:,.2f} ({pnl_sign}{abs_pnl_pct:.1f}%). "
            f"{top_holding_str}You have ${summary.stablecoin_value_usd:,.2f} "
            f"({summary.stablecoin_pct:.1f}%) in liquid cash/stablecoins."
        )

        # 3. Market drivers breakdown
        drivers_parts = []
        if top_gain and top_gain.change_24h_pct > 2.0:
            drivers_parts.append(
                f"• {top_gain.asset} had a strong day, gaining +{top_gain.change_24h_pct:.1f}% "
                f"and contributing +${top_gain.change_24h_usd:,.2f} in value."
            )
        if worst_drop and worst_drop.change_24h_pct < -2.0:
            drivers_parts.append(
                f"• {worst_drop.asset} saw selling pressure, decreasing by {worst_drop.change_24h_pct:.1f}% "
                f"(-${abs(worst_drop.change_24h_usd):,.2f})."
            )
        
        # Check BTC if present
        btc_pos = next((p for p in summary.positions if p.asset == "BTC"), None)
        if btc_pos and btc_pos != top_gain and btc_pos != worst_drop:
            drivers_parts.append(
                f"• Bitcoin (BTC) moved {btc_pos.change_24h_pct:+.1f}% to ${btc_pos.current_price:,.2f}, "
                f"providing a stabilizing anchor for your overall account."
            )

        if not drivers_parts:
            drivers_parts.append("• Market prices remained calm across your portfolio over the last 24 hours.")

        market_drivers = "\n".join(drivers_parts)

        # 4. Risk perspective
        if risk.risk_level in ("ELEVATED", "HIGH"):
            risk_perspective = (
                f"Overall Risk Status: {risk.risk_level} (Score: {risk.overall_score}/10). "
                f"We noticed notable flags: "
                + "; ".join(f.title for f in risk.flags[:2])
                + ". While high upside is exciting, maintaining proper balance protects against sudden swings."
            )
        else:
            risk_perspective = (
                f"Overall Risk Status: {risk.risk_level} (Score: {risk.overall_score}/10). "
                f"Your account shows healthy diversification and no immediate danger signs."
            )

        # 5. Actionable tips
        actionable_tips = []
        for flag in risk.flags:
            if flag.action_item not in actionable_tips:
                actionable_tips.append(flag.action_item)

        if not actionable_tips:
            actionable_tips.append("Continue monitoring your positions periodically to maintain your target allocations.")
            actionable_tips.append("Ensure your Binance 2FA and security settings remain up to date.")

        return PlainLanguageSummary(
            headline=headline,
            overview=overview,
            market_drivers=market_drivers,
            risk_perspective=risk_perspective,
            actionable_tips=actionable_tips[:3],
        )
