"""
Plain-language AI summary generator.
Translates crypto analytics, P&L, and risk flags into clear, conversational summaries
that any non-trader can immediately understand.
Works 100% offline via a built-in financial reasoning engine, with optional Gemini/OpenAI enhancement.
"""
import json
import urllib.request
import urllib.error
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
    def _generate_with_llm(
        cls,
        summary: PortfolioSummary,
        risk: RiskAssessment,
        trends: Dict[str, MarketTrendHighlight],
        api_key: str,
        model: Optional[str] = None,
    ) -> Optional[PlainLanguageSummary]:
        """Generate high-quality summary via configurable LLM API (model placeholder)."""
        from ..config import config
        target_model = model or config.llm_model
        if not api_key or api_key.strip() in ("", "your_api_key_here", "your_llm_api_key_here") or target_model == "your-model-name-here":
            return None

        prompt = (
            "You are a friendly, expert crypto financial analyst for Binance PortfolioPulse AI.\n"
            "Given the portfolio metrics below, generate a clear, conversational plain-language summary.\n\n"
            f"Portfolio Valuation: ${summary.total_value_usd:,.2f}\n"
            f"24h P&L: ${summary.total_24h_pnl_usd:,.2f} ({summary.total_24h_pnl_pct:+.2f}%)\n"
            f"Stablecoin Reserves: ${summary.stablecoin_value_usd:,.2f} ({summary.stablecoin_pct:.1f}%)\n"
            f"Asset Count: {summary.asset_count}\n"
            f"Risk Level: {risk.risk_level} (Score: {risk.overall_score}/10)\n"
            f"Risk Flags: {', '.join(f.title for f in risk.flags) if risk.flags else 'None'}\n"
            f"Holdings Breakdown: {', '.join(f'{p.asset} ({p.allocation_pct:.1f}%, 24h: {p.change_24h_pct:+.1f}%)' for p in summary.positions[:5])}\n\n"
            "Return ONLY valid JSON matching this exact structure without markdown backticks:\n"
            "{\n"
            '  "headline": "A concise punchy 1-sentence daily headline",\n'
            '  "overview": "A 2-3 sentence conversational overview of account value and allocation",\n'
            '  "market_drivers": "Bullet points with • describing what moved today",\n'
            '  "risk_perspective": "A 2-sentence balanced risk perspective",\n'
            '  "actionable_tips": ["Tip 1", "Tip 2"]\n'
            "}"
        )
        try:
            is_openai = target_model.startswith("gpt-") or target_model.startswith("o1") or target_model.startswith("o3")
            if is_openai:
                url = config.llm_base_url or "https://api.openai.com/v1/chat/completions"
                req_data = json.dumps({
                    "model": target_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                }).encode("utf-8")
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "content-type": "application/json",
                    "User-Agent": "Binance-PortfolioPulse-AI/1.0",
                }
            else:
                url = config.llm_base_url or "https://api.anthropic.com/v1/messages"
                req_data = json.dumps({
                    "model": target_model,
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": prompt}],
                }).encode("utf-8")
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                    "User-Agent": "Binance-PortfolioPulse-AI/1.0",
                }

            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                if is_openai:
                    text_content = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                else:
                    text_content = resp_json.get("content", [{}])[0].get("text", "").strip()

                if text_content.startswith("```"):
                    text_content = text_content.split("```")[1]
                    if text_content.startswith("json"):
                        text_content = text_content[4:]
                parsed = json.loads(text_content.strip())
                return PlainLanguageSummary(
                    headline=parsed.get("headline", ""),
                    overview=parsed.get("overview", ""),
                    market_drivers=parsed.get("market_drivers", ""),
                    risk_perspective=parsed.get("risk_perspective", ""),
                    actionable_tips=parsed.get("actionable_tips", []),
                )
        except Exception as e:
            logger.warning(f"LLM summary generation failed: {e}. Falling back to rule-based synthesis.")
            return None

    # Alias for backward compatibility
    _generate_with_anthropic = _generate_with_llm

    @classmethod
    def generate(
        cls,
        summary: PortfolioSummary,
        risk: RiskAssessment,
        trends: Dict[str, MarketTrendHighlight],
        anthropic_api_key: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ) -> PlainLanguageSummary:
        """
        Synthesizes portfolio data into clear everyday language.
        Uses configured LLM API if key is available; otherwise uses high-fidelity financial rules.
        """
        key = llm_api_key or anthropic_api_key
        if key:
            llm_summary = cls._generate_with_llm(summary, risk, trends, key, model=llm_model)
            if llm_summary:
                return llm_summary

        # Zero holdings check
        if summary.total_value_usd <= 0 or summary.asset_count == 0:
            return PlainLanguageSummary(
                headline="Your Binance Spot account currently has no active token holdings ($0.00).",
                overview="As of today, your total account is valued at $0.00 USD across 0 active positions.",
                market_drivers="• No active portfolio asset movements detected today.",
                risk_perspective="Your account has zero exposure to market volatility with $0.00 deployed in active positions.",
                actionable_tips=[
                    "Deposit or transfer assets into your Binance Spot wallet to begin tracking portfolio analytics.",
                    "Query get_market_overview() to discover live market momentum across major assets.",
                ],
            )

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
