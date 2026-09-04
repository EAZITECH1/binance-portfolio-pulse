"""
Unit tests for Binance PortfolioPulse AI.
Tests portfolio valuation, risk analysis heuristics, and multi-format report generation.
"""
import unittest
from pathlib import Path
import sys

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.connectors.mock_provider import MockDataProvider
from src.analytics.portfolio import PortfolioAnalyzer
from src.analytics.market_trends import MarketTrendAnalyzer
from src.analytics.risk_analyzer import RiskAnalyzer
from src.analytics.ai_summary import AISummaryGenerator
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.html_reporter import HTMLReporter
from src.reporters.json_reporter import JSONReporter


class TestPortfolioPulse(unittest.TestCase):

    def setUp(self):
        self.mock_provider = MockDataProvider()
        self.raw_balances = self.mock_provider.get_account_balances()
        self.tickers = {
            "BTCUSDT": self.mock_provider.get_ticker_24hr("BTCUSDT"),
            "ETHUSDT": self.mock_provider.get_ticker_24hr("ETHUSDT"),
            "SOLUSDT": self.mock_provider.get_ticker_24hr("SOLUSDT"),
            "BNBUSDT": self.mock_provider.get_ticker_24hr("BNBUSDT"),
            "NEARUSDT": self.mock_provider.get_ticker_24hr("NEARUSDT"),
        }
        self.trends = {}
        for asset in ["BTC", "ETH", "SOL", "BNB", "NEAR"]:
            sym = f"{asset}USDT"
            klines = self.mock_provider.get_klines_history(sym, limit=7)
            self.trends[asset] = MarketTrendAnalyzer.analyze_asset_trend(
                asset, self.tickers[sym], klines
            )

    def test_portfolio_valuation(self):
        """Verify total valuation and asset allocation calculations."""
        summary = PortfolioAnalyzer.analyze(self.raw_balances, self.tickers)
        self.assertGreater(summary.total_value_usd, 50000.0)
        self.assertEqual(summary.asset_count, 6)

        # Ensure allocations sum to approximately 100%
        total_alloc = sum(p.allocation_pct for p in summary.positions)
        self.assertAlmostEqual(total_alloc, 100.0, places=1)

        # Check stablecoin buffer detection
        self.assertGreater(summary.stablecoin_value_usd, 0.0)
        self.assertGreater(summary.stablecoin_pct, 0.0)

    def test_concentration_risk_detection(self):
        """Verify concentration flag triggers when a single asset exceeds threshold."""
        summary = PortfolioAnalyzer.analyze(self.raw_balances, self.tickers)
        # BTC is > 50% in mock portfolio
        risk = RiskAnalyzer.evaluate(summary, self.trends, concentration_threshold=0.35)
        
        concentration_flags = [f for f in risk.flags if f.category == "CONCENTRATION"]
        self.assertTrue(len(concentration_flags) > 0)
        self.assertIn("BTC", concentration_flags[0].title)

    def test_volatility_flag_detection(self):
        """Verify volatility flag triggers for large daily price swings."""
        summary = PortfolioAnalyzer.analyze(self.raw_balances, self.tickers)
        risk = RiskAnalyzer.evaluate(summary, self.trends, volatility_threshold=0.08)
        
        volatility_flags = [f for f in risk.flags if f.category == "VOLATILITY"]
        self.assertTrue(len(volatility_flags) > 0)
        self.assertTrue(any("SOL" in f.title for f in volatility_flags))

    def test_ai_summary_generation(self):
        """Verify plain-language AI summary synthesizes headline and key drivers."""
        summary = PortfolioAnalyzer.analyze(self.raw_balances, self.tickers)
        risk = RiskAnalyzer.evaluate(summary, self.trends)
        ai_summary = AISummaryGenerator.generate(summary, risk, self.trends)

        self.assertTrue(len(ai_summary.headline) > 10)
        self.assertTrue(len(ai_summary.overview) > 20)
        self.assertTrue(len(ai_summary.actionable_tips) >= 1)

    def test_reporters_render_valid_content(self):
        """Verify Markdown, HTML, and JSON reports render successfully without errors."""
        summary = PortfolioAnalyzer.analyze(self.raw_balances, self.tickers)
        risk = RiskAnalyzer.evaluate(summary, self.trends)
        ai_summary = AISummaryGenerator.generate(summary, risk, self.trends)

        md = MarkdownReporter.render(summary, risk, self.trends, ai_summary)
        self.assertIn("# 📊 Binance PortfolioPulse", md)
        self.assertIn("Total Portfolio Valuation", md)

        html = HTMLReporter.render(summary, risk, self.trends, ai_summary)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Binance PortfolioPulse AI", html)
        self.assertIn("alloc-bar-wrapper", html)

        json_str = JSONReporter.render(summary, risk, self.trends, ai_summary)
        self.assertIn('"portfolio":', json_str)
        self.assertIn('"risk_assessment":', json_str)


if __name__ == "__main__":
    unittest.main()
