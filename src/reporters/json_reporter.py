"""
Structured JSON report generator for Binance PortfolioPulse AI.
Provides clean machine-readable data payloads for downstream pipelines and bots.
"""
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ..analytics.portfolio import PortfolioSummary
from ..analytics.market_trends import MarketTrendHighlight
from ..analytics.risk_analyzer import RiskAssessment
from ..analytics.ai_summary import PlainLanguageSummary
from ..analytics.futures import FuturesAccountSummary
from ..analytics.predictive import PredictiveBalanceReport


class JSONReporter:
    """Serializes portfolio intelligence into structured JSON."""

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
        payload = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_mode": source_mode,
                "agent_name": "Binance PortfolioPulse AI",
                "version": "1.0.0",
            },
            "ai_executive_summary": ai_summary.to_dict(),
            "portfolio": summary.to_dict(),
            "futures": futures_summary.to_dict() if futures_summary else None,
            "predictive_analysis": predictive_report.to_dict() if predictive_report else None,
            "market_trends": {asset: t.to_dict() for asset, t in trends.items()},
            "risk_assessment": risk.to_dict(),
        }
        return json.dumps(payload, indent=2)
