"""
Markdown report generator for Binance PortfolioPulse AI.
Produces clean, GitHub-flavored Markdown reports with tables, emojis, and risk badges.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ..analytics.portfolio import PortfolioSummary
from ..analytics.market_trends import MarketTrendHighlight
from ..analytics.risk_analyzer import RiskAssessment
from ..analytics.ai_summary import PlainLanguageSummary
from ..analytics.futures import FuturesAccountSummary
from ..analytics.predictive import PredictiveBalanceReport


class MarkdownReporter:
    """Renders comprehensive crypto portfolio and risk reports in Markdown format."""

    @classmethod
    def render(
        cls,
        summary: PortfolioSummary,
        risk: RiskAssessment,
        trends: Dict[str, MarketTrendHighlight],
        ai_summary: PlainLanguageSummary,
        source_mode: str = "Binance Agent OS (MCP)",
        futures_summary: Optional[FuturesAccountSummary] = None,
        predictive_report: Optional[PredictiveBalanceReport] = None,
    ) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        pnl_symbol = "+" if summary.total_24h_pnl_usd >= 0 else "-"
        abs_pnl_usd = abs(summary.total_24h_pnl_usd)
        abs_pnl_pct = abs(summary.total_24h_pnl_pct)

        # Risk badge
        risk_color_map = {
            "CONSERVATIVE": "🟢 **CONSERVATIVE**",
            "MODERATE": "🟡 **MODERATE**",
            "ELEVATED": "🟠 **ELEVATED**",
            "HIGH": "🔴 **HIGH RISK**",
        }
        risk_badge = risk_color_map.get(risk.risk_level, f"**{risk.risk_level}**")

        unrealized_sign = "+" if summary.total_unrealized_pnl_usd >= 0 else "-"
        abs_unrealized_usd = abs(summary.total_unrealized_pnl_usd)

        lines = [
            f"# 📊 Binance PortfolioPulse Daily Report",
            f"**Generated:** `{now_str}` | **Data Source:** `{source_mode}` | **Risk Level:** {risk_badge} (Score: `{risk.overall_score}/10`)",
            "",
            "---",
            "",
            "## 💡 Plain-Language Summary (At a Glance)",
            f"### {ai_summary.headline}",
            "",
            f"{ai_summary.overview}",
            "",
            "**Key Market Drivers:**",
            f"{ai_summary.market_drivers}",
            "",
            f"> **Risk Perspective:** {ai_summary.risk_perspective}",
            "",
            "---",
            "",
            "## 💰 Portfolio Overview & Asset Allocation",
            "",
            "| Metric | Value |",
            "| :--- | :--- |",
            f"| **Total Portfolio Valuation** | **${summary.total_value_usd:,.2f}** |",
            f"| **24-Hour Net Change** | **{pnl_symbol}${abs_pnl_usd:,.2f} ({pnl_symbol}{abs_pnl_pct:.2f}%)** |",
            f"| **Total Unrealized P&L** | **{unrealized_sign}${abs_unrealized_usd:,.2f}** |",
            f"| **Liquid Stablecoin Buffer** | **${summary.stablecoin_value_usd:,.2f} ({summary.stablecoin_pct:.1f}%)** |",
            f"| **Active Assets Held** | **{summary.asset_count}** |",
            "",
            "### Detailed Holdings Breakdown",
            "",
            "| Asset | Balance | Price (USD) | Value (USD) | Alloc (%) | 24h Change | Unrealized P&L |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for p in summary.positions:
            chg_icon = "🟢" if p.change_24h_pct >= 0 else "🔴"
            chg_str = f"{chg_icon} {p.change_24h_pct:+.2f}%" if not p.is_stablecoin else "⚪ 0.00%"
            
            pnl_str = "-"
            if p.unrealized_pnl_usd is not None:
                pnl_icon = "📈" if p.unrealized_pnl_usd >= 0 else "📉"
                pnl_str = f"{pnl_icon} ${p.unrealized_pnl_usd:+,.2f} ({p.unrealized_pnl_pct:+.1f}%)"

            lines.append(
                f"| **{p.asset}** | {p.total_amount:,.4f} | ${p.current_price:,.2f} | ${p.usd_value:,.2f} | {p.allocation_pct:.1f}% | {chg_str} | {pnl_str} |"
            )

        if futures_summary and (futures_summary.total_margin_balance_usd > 0 or futures_summary.positions):
            f_status_map = {
                "SAFE": "🟢 SAFE",
                "MODERATE": "🟡 MODERATE",
                "WARNING": "🟠 WARNING",
                "CRITICAL_LIQUIDATION_RISK": "🔴 CRITICAL LIQUIDATION RISK",
            }
            f_badge = f_status_map.get(futures_summary.risk_status, futures_summary.risk_status)
            lines.extend([
                "",
                "---",
                "",
                "## ⚡ Binance Futures Derivatives & Margin Intelligence",
                "",
                f"**Margin Health Status:** {f_badge} | **Margin Ratio:** `{futures_summary.margin_ratio_pct:.1f}%` | **Effective Leverage:** `{futures_summary.effective_leverage:.1f}x`",
                "",
                "| Futures Metric | Value |",
                "| :--- | :--- |",
                f"| **Total Margin Balance** | **${futures_summary.total_margin_balance_usd:,.2f}** |",
                f"| **Available Margin Cushion** | **${futures_summary.available_balance_usd:,.2f}** |",
                f"| **Total Maintenance Margin** | **${futures_summary.total_maint_margin_usd:,.2f}** |",
                f"| **Unrealized Derivatives P&L** | **${futures_summary.total_unrealized_pnl_usd:+,.2f}** |",
                f"| **Net Directional Delta** | **${futures_summary.net_delta_usd:+,.2f}** |",
                "",
            ])
            if futures_summary.positions:
                lines.extend([
                    "### Open Derivatives Positions",
                    "",
                    "| Contract | Side | Size | Mark Price | Liq. Price | Cushion | Unrealized P&L |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
                ])
                for fp in futures_summary.positions:
                    pnl_sign = "+" if fp.unrealized_pnl_usd >= 0 else ""
                    pnl_icon = "📈" if fp.unrealized_pnl_usd >= 0 else "📉"
                    cushion_icon = "🟢" if fp.liquidation_distance_pct > 20 else ("🟡" if fp.liquidation_distance_pct > 10 else "🔴")
                    lines.append(
                        f"| **{fp.symbol}** | `{fp.side} {fp.leverage}x` | {abs(fp.amount):.4f} (${fp.notional_usd:,.2f}) | ${fp.mark_price:,.2f} | ${fp.liquidation_price:,.2f} | {cushion_icon} {fp.liquidation_distance_pct:.1f}% | {pnl_icon} {pnl_sign}${fp.unrealized_pnl_usd:,.2f} ({pnl_sign}{fp.unrealized_pnl_pct:.1f}%) |"
                    )
                lines.append("")

        if predictive_report and predictive_report.scenarios:
            lines.extend([
                "",
                "---",
                "",
                "## 🔮 Predictive Balance & Scenario Stress-Testing",
                f"**Current Balance:** `${predictive_report.current_total_balance_usd:,.2f}` | **7-Day Expected:** `${predictive_report.projected_7d_base_usd:,.2f}` | **7D 95% Value-at-Risk (VaR):** `${predictive_report.var_95_7d_usd:,.2f}` (`{predictive_report.var_95_7d_pct:.1f}%`)",
                "",
                "### Stress-Test Scenarios (Empirical Beta & Volatility)",
                "",
                "| Scenario | Benchmark Move | Projected Balance | Net Impact ($ / %) | Safety & Liquidation Notes |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ])
            for sc in predictive_report.scenarios:
                sc_sign = "+" if sc.net_pnl_usd >= 0 else ""
                sc_icon = "🚀" if sc.btc_benchmark_change_pct > 10 else ("🟢" if sc.net_pnl_usd >= 0 else ("🔴" if sc.btc_benchmark_change_pct < -20 else "↘️"))
                status_note = sc.warning_notes[0] if sc.warning_notes else "Normal market fluctuations absorbed."
                lines.append(
                    f"| {sc_icon} **{sc.name}** | `{sc.btc_benchmark_change_pct:+.1f}%` | **${sc.projected_balance_usd:,.2f}** | {sc_sign}${sc.net_pnl_usd:,.2f} ({sc_sign}{sc.net_pnl_pct:.1f}%) | {status_note} |"
                )
            lines.append("")

        lines.extend([
            "",
            "---",
            "",
            "## 📈 Market Trend Highlights for Held Assets",
            "",
            "| Asset | 24h High | 24h Low | 7d Volatility | Trend Sentiment |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])

        for asset, trend in trends.items():
            vol_str = f"{trend.volatility_7d_pct:.1f}%" if trend.volatility_7d_pct is not None else "N/A"
            sentiment_badges = {
                "BULLISH_SURGE": "🚀 Bullish Surge",
                "MODERATE_UP": "↗️ Moderate Gain",
                "CONSOLIDATION": "➡️ Consolidating",
                "MODERATE_DOWN": "↘️ Moderate Pullback",
                "BEARISH_DROP": "📉 Sharp Drop",
            }
            sent_str = sentiment_badges.get(trend.trend_sentiment, trend.trend_sentiment)
            lines.append(
                f"| **{asset}** | ${trend.high_24h:,.2f} | ${trend.low_24h:,.2f} | {vol_str} | {sent_str} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## ⚠️ Risk Flags & Safety Analysis",
        ])

        if not risk.flags:
            lines.extend([
                "✅ *No high or critical risk flags detected. Portfolio shows balanced risk management.*",
                "",
            ])
        else:
            lines.extend([
                "| Severity | Category | Issue | Actionable Recommendation |",
                "| :--- | :--- | :--- | :--- |",
            ])
            for f in risk.flags:
                sev_icon = {
                    "CRITICAL": "🛑 **CRITICAL**",
                    "HIGH": "⚠️ **HIGH**",
                    "MEDIUM": "⚡ **MEDIUM**",
                    "LOW": "ℹ️ **LOW**",
                }.get(f.severity, f.severity)
                lines.append(
                    f"| {sev_icon} | {f.category} | **{f.title}**<br>{f.description} | {f.action_item} |"
                )
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 🎯 Actionable Takeaways for Today",
        ])
        for idx, tip in enumerate(ai_summary.actionable_tips, 1):
            lines.append(f"{idx}. {tip}")

        lines.extend([
            "",
            "---",
            "*Disclaimer: This report is generated automatically by Binance PortfolioPulse AI using Binance Agent OS. Not financial advice.*",
        ])

        return "\n".join(lines)
