"""
Interactive HTML Dashboard Reporter for Binance PortfolioPulse AI.
Renders a sleek, responsive, dark-mode fintech report inspired by Binance Agent OS.
Standalone and zero-dependency: requires no external CDNs or JavaScript frameworks.
"""
from datetime import datetime, timezone
from typing import Dict, Any

from ..analytics.portfolio import PortfolioSummary
from ..analytics.market_trends import MarketTrendHighlight
from ..analytics.risk_analyzer import RiskAssessment
from ..analytics.ai_summary import PlainLanguageSummary


class HTMLReporter:
    """Renders visual HTML dashboard reports."""

    COLORS = [
        "#F0B90B",  # Binance Gold
        "#3861FB",  # CoinMarketCap Blue
        "#00D1B2",  # Solana / Mint
        "#9B51E0",  # Purple
        "#FF9900",  # Orange
        "#25A750",  # Green
        "#82868E",  # Muted Grey
    ]

    @classmethod
    def render(
        cls,
        summary: PortfolioSummary,
        risk: RiskAssessment,
        trends: Dict[str, MarketTrendHighlight],
        ai_summary: PlainLanguageSummary,
        source_mode: str = "Binance Agent OS (MCP)",
    ) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        pnl_symbol = "+" if summary.total_24h_pnl_usd >= 0 else "-"
        pnl_class = "green" if summary.total_24h_pnl_usd >= 0 else "red"
        abs_pnl_usd = abs(summary.total_24h_pnl_usd)
        abs_pnl_pct = abs(summary.total_24h_pnl_pct)

        # Risk badge color
        risk_theme_map = {
            "CONSERVATIVE": ("#0ecb81", "rgba(14, 203, 129, 0.15)"),
            "MODERATE": ("#f0b90b", "rgba(240, 185, 11, 0.15)"),
            "ELEVATED": ("#f6851b", "rgba(246, 133, 27, 0.15)"),
            "HIGH": ("#f6465d", "rgba(246, 70, 93, 0.15)"),
        }
        risk_color, risk_bg = risk_theme_map.get(
            risk.risk_level, ("#f0b90b", "rgba(240, 185, 11, 0.15)")
        )

        # Allocation progress bar HTML
        alloc_bars_html = []
        alloc_legend_html = []
        for i, pos in enumerate(summary.positions):
            color = cls.COLORS[i % len(cls.COLORS)]
            alloc_bars_html.append(
                f'<div style="width: {pos.allocation_pct}%; background-color: {color};" '
                f'title="{pos.asset}: {pos.allocation_pct:.1f}%"></div>'
            )
            alloc_legend_html.append(
                f'<div class="legend-item">'
                f'<span class="legend-dot" style="background-color: {color};"></span>'
                f'<span class="legend-asset">{pos.asset}</span>'
                f'<span class="legend-pct">{pos.allocation_pct:.1f}%</span>'
                f'</div>'
            )

        # Holdings table rows HTML
        holdings_rows = []
        for pos in summary.positions:
            chg_class = "green" if pos.change_24h_pct >= 0 else "red"
            chg_text = f"{pos.change_24h_pct:+.2f}%" if not pos.is_stablecoin else "0.00%"
            
            pnl_cell = '<span class="muted">-</span>'
            if pos.unrealized_pnl_usd is not None:
                pos_pnl_class = "green" if pos.unrealized_pnl_usd >= 0 else "red"
                pnl_cell = f'<span class="{pos_pnl_class}">${pos.unrealized_pnl_usd:+,.2f} ({pos.unrealized_pnl_pct:+.1f}%)</span>'

            holdings_rows.append(
                f'<tr>'
                f'<td><strong class="asset-name">{pos.asset}</strong></td>'
                f'<td>{pos.total_amount:,.4f}</td>'
                f'<td>${pos.current_price:,.2f}</td>'
                f'<td><strong>${pos.usd_value:,.2f}</strong></td>'
                f'<td><span class="pill">{pos.allocation_pct:.1f}%</span></td>'
                f'<td><span class="{chg_class}">{chg_text}</span></td>'
                f'<td>{pnl_cell}</td>'
                f'</tr>'
            )

        # Market trends rows HTML
        trend_rows = []
        for asset, trend in trends.items():
            sentiment_map = {
                "BULLISH_SURGE": ("🚀 Surge", "green"),
                "MODERATE_UP": ("↗️ Gain", "green"),
                "CONSOLIDATION": ("➡️ Neutral", "muted"),
                "MODERATE_DOWN": ("↘️ Pullback", "red"),
                "BEARISH_DROP": ("📉 Drop", "red"),
            }
            sent_label, sent_class = sentiment_map.get(trend.trend_sentiment, (trend.trend_sentiment, "muted"))
            vol_text = f"{trend.volatility_7d_pct:.1f}%" if trend.volatility_7d_pct is not None else "N/A"

            trend_rows.append(
                f'<tr>'
                f'<td><strong>{asset}</strong></td>'
                f'<td>${trend.current_price:,.2f}</td>'
                f'<td>${trend.high_24h:,.2f} / ${trend.low_24h:,.2f}</td>'
                f'<td>{vol_text}</td>'
                f'<td><span class="badge {sent_class}">{sent_label}</span></td>'
                f'</tr>'
            )

        # Risk flag cards HTML
        risk_cards = []
        for f in risk.flags:
            sev_badge_class = "red" if f.severity in ("CRITICAL", "HIGH") else "amber"
            risk_cards.append(
                f'<div class="risk-card {f.severity.lower()}">'
                f'<div class="risk-card-header">'
                f'<span class="badge {sev_badge_class}">{f.severity}</span>'
                f'<span class="risk-cat">{f.category}</span>'
                f'</div>'
                f'<h4 class="risk-title">{f.title}</h4>'
                f'<p class="risk-desc">{f.description}</p>'
                f'<div class="risk-action"><strong>Action:</strong> {f.action_item}</div>'
                f'</div>'
            )

        # Actionable tips
        action_items_html = "".join(f"<li>{tip}</li>" for tip in ai_summary.actionable_tips)

        unrealized_sign = "+" if summary.total_unrealized_pnl_usd >= 0 else "-"
        abs_unrealized_usd = abs(summary.total_unrealized_pnl_usd)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binance PortfolioPulse - Daily Analysis</title>
    <style>
        :root {{
            --bg-base: #0b0e11;
            --bg-surface: #181a20;
            --bg-elevated: #2b313a;
            --text-primary: #eaecef;
            --text-secondary: #848e9c;
            --text-muted: #5e6673;
            --gold: #f0b90b;
            --green: #0ecb81;
            --red: #f6465d;
            --border-color: #2b313a;
            --border-radius: 12px;
            --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-base);
            color: var(--text-primary);
            font-family: var(--font-stack);
            line-height: 1.5;
            padding: 32px 20px;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        /* Header */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .logo-area {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .logo-icon {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #f0b90b, #f8d33a);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #000;
            font-size: 20px;
        }}
        h1 {{ font-size: 24px; font-weight: 700; color: #fff; }}
        .meta-tag {{ font-size: 13px; color: var(--text-secondary); }}
        
        /* Metric Cards Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}
        .metric-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 20px;
            position: relative;
        }}
        .metric-label {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: #fff;
        }}
        .metric-sub {{
            font-size: 14px;
            margin-top: 6px;
            font-weight: 600;
        }}

        /* AI Executive Banner */
        .ai-banner {{
            background: linear-gradient(135deg, rgba(240, 185, 11, 0.08), rgba(24, 26, 32, 0.95));
            border: 1px solid rgba(240, 185, 11, 0.3);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 28px;
        }}
        .ai-banner-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(240, 185, 11, 0.2);
            color: var(--gold);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .ai-banner h2 {{ font-size: 18px; margin-bottom: 10px; color: #fff; }}
        .ai-banner p {{ color: var(--text-primary); font-size: 15px; line-height: 1.6; margin-bottom: 12px; }}
        .ai-banner-drivers {{
            background: var(--bg-elevated);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            color: var(--text-secondary);
            white-space: pre-line;
            line-height: 1.7;
        }}

        /* Section Containers */
        .section-box {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 28px;
        }}
        .section-box h3 {{
            font-size: 18px;
            margin-bottom: 16px;
            color: #fff;
        }}

        /* Allocation Bar */
        .alloc-bar-wrapper {{
            height: 14px;
            display: flex;
            border-radius: 7px;
            overflow: hidden;
            background-color: var(--bg-elevated);
            margin-bottom: 16px;
        }}
        .legend-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }}
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .legend-asset {{ font-weight: 600; color: #fff; }}
        .legend-pct {{ color: var(--text-secondary); }}

        /* Data Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}
        th {{
            color: var(--text-secondary);
            font-weight: 500;
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 14px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
        }}
        tr:last-child td {{ border-bottom: none; }}
        .asset-name {{ font-size: 15px; color: #fff; }}

        /* Risk Cards */
        .risk-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
        }}
        .risk-card {{
            background: var(--bg-elevated);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 18px;
        }}
        .risk-card.critical, .risk-card.high {{
            border-left: 4px solid var(--red);
        }}
        .risk-card.medium {{
            border-left: 4px solid var(--gold);
        }}
        .risk-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .risk-cat {{ font-size: 12px; color: var(--text-secondary); font-weight: 600; }}
        .risk-title {{ font-size: 15px; color: #fff; margin-bottom: 8px; }}
        .risk-desc {{ font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5; }}
        .risk-action {{
            background: rgba(0, 0, 0, 0.25);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            color: var(--text-primary);
        }}

        /* Action Steps */
        .action-list {{
            list-style-type: decimal;
            padding-left: 20px;
            color: var(--text-primary);
            line-height: 1.8;
            font-size: 14px;
        }}

        /* Utility Classes */
        .green {{ color: var(--green); }}
        .red {{ color: var(--red); }}
        .muted {{ color: var(--text-muted); }}
        .pill {{
            background-color: var(--bg-elevated);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge.green {{ background: rgba(14, 203, 129, 0.15); color: var(--green); }}
        .badge.red {{ background: rgba(246, 70, 93, 0.15); color: var(--red); }}
        .badge.amber {{ background: rgba(240, 185, 11, 0.15); color: var(--gold); }}

        footer {{
            text-align: center;
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-area">
                <div class="logo-icon">B</div>
                <div>
                    <h1>Binance PortfolioPulse AI</h1>
                    <div class="meta-tag">Binance Agent OS • Daily Portfolio & Risk Intelligence</div>
                </div>
            </div>
            <div class="meta-tag">
                Generated: <strong>{now_str}</strong><br>
                Source: <strong>{source_mode}</strong>
            </div>
        </header>

        <!-- Top Metrics Cards -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Portfolio Value</div>
                <div class="metric-value">${summary.total_value_usd:,.2f}</div>
                <div class="metric-sub {pnl_class}">
                    24h: {pnl_symbol}${abs_pnl_usd:,.2f} ({pnl_symbol}{abs_pnl_pct:.2f}%)
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Unrealized P&L</div>
                <div class="metric-value">{unrealized_sign}${abs_unrealized_usd:,.2f}</div>
                <div class="metric-sub muted">Calculated from cost basis</div>
            </div>
            <div class="metric-card" style="border-color: {risk_color};">
                <div class="metric-label">Overall Risk Status</div>
                <div class="metric-value" style="color: {risk_color};">{risk.risk_level}</div>
                <div class="metric-sub" style="color: {risk_color};">Score: {risk.overall_score}/10</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cash / Stable Reserve</div>
                <div class="metric-value">${summary.stablecoin_value_usd:,.2f}</div>
                <div class="metric-sub muted">{summary.stablecoin_pct:.1f}% of total portfolio</div>
            </div>
        </div>

        <!-- Plain-Language AI Synthesis -->
        <div class="ai-banner">
            <div class="ai-banner-badge">✨ AI Financial Intelligence</div>
            <h2>{ai_summary.headline}</h2>
            <p>{ai_summary.overview}</p>
            <div class="ai-banner-drivers">
                <strong>Market Drivers:</strong><br>{ai_summary.market_drivers}
            </div>
        </div>

        <!-- Asset Allocation Bar -->
        <div class="section-box">
            <h3>Asset Allocation Breakdown</h3>
            <div class="alloc-bar-wrapper">
                {''.join(alloc_bars_html)}
            </div>
            <div class="legend-grid">
                {''.join(alloc_legend_html)}
            </div>
        </div>

        <!-- Holdings Table -->
        <div class="section-box">
            <h3>Holdings & Performance</h3>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Asset</th>
                            <th>Total Balance</th>
                            <th>Current Price</th>
                            <th>USD Value</th>
                            <th>Allocation</th>
                            <th>24h Change</th>
                            <th>Unrealized P&L</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(holdings_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Market Highlights Table -->
        <div class="section-box">
            <h3>Market Highlights & Volatility</h3>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>24h High / Low</th>
                            <th>7d Volatility</th>
                            <th>Trend Sentiment</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(trend_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Risk Flags -->
        <div class="section-box">
            <h3>⚠️ Risk Flags & Vulnerabilities</h3>
            <div class="risk-grid">
                {''.join(risk_cards) if risk_cards else '<p class="muted">No critical risk flags detected today.</p>'}
            </div>
        </div>

        <!-- Actionable Steps -->
        <div class="section-box">
            <h3>🎯 Practical Next Steps for Non-Traders</h3>
            <ol class="action-list">
                {action_items_html}
            </ol>
        </div>

        <footer>
            Binance Agent OS Mini Hackathon (Track A - Agent Creation) • Generated automatically by Binance PortfolioPulse AI • Not financial advice.
        </footer>
    </div>
</body>
</html>"""
        return html
