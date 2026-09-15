"""
Unit tests for Binance Futures derivatives and margin risk analytics.
"""
import unittest

from src.analytics.futures import FuturesAnalyzer, FuturesAccountSummary, FuturesPosition
from src.connectors.mock_provider import MockDataProvider


class TestFuturesAnalytics(unittest.TestCase):

    def setUp(self):
        self.mock = MockDataProvider()
        self.raw_futures = self.mock.get_futures_account()
        self.mark_prices = self.mock.get_futures_mark_prices()

    def test_futures_analyzer_parses_account_and_positions(self):
        summary = FuturesAnalyzer.analyze(self.raw_futures, self.mark_prices)
        self.assertIsInstance(summary, FuturesAccountSummary)
        self.assertEqual(summary.total_margin_balance_usd, 5250.0)
        self.assertEqual(summary.total_maint_margin_usd, 420.0)
        self.assertEqual(summary.available_balance_usd, 3700.0)
        self.assertEqual(len(summary.positions), 2)

    def test_futures_positions_long_short_details(self):
        summary = FuturesAnalyzer.analyze(self.raw_futures, self.mark_prices)
        btc_pos = next(p for p in summary.positions if p.symbol == "BTCUSDT")
        eth_pos = next(p for p in summary.positions if p.symbol == "ETHUSDT")

        self.assertEqual(btc_pos.side, "LONG")
        self.assertEqual(btc_pos.leverage, 5)
        self.assertGreater(btc_pos.notional_usd, 0)
        self.assertGreater(btc_pos.liquidation_distance_pct, 0)

        self.assertEqual(eth_pos.side, "SHORT")
        self.assertEqual(eth_pos.leverage, 3)
        self.assertGreater(eth_pos.liquidation_distance_pct, 0)

    def test_margin_ratio_and_effective_leverage(self):
        summary = FuturesAnalyzer.analyze(self.raw_futures, self.mark_prices)
        expected_ratio = (420.0 / 5250.0) * 100.0
        self.assertAlmostEqual(summary.margin_ratio_pct, expected_ratio, places=1)
        self.assertGreater(summary.effective_leverage, 1.0)

    def test_critical_liquidation_detection(self):
        # Position with dangerously close liquidation price
        critical_data = {
            "totalMarginBalance": "1000.00",
            "totalMaintMargin": "850.00",  # 85% margin ratio
            "positions": [
                {
                    "symbol": "BTCUSDT",
                    "positionAmt": "1.0",
                    "entryPrice": "63000.00",
                    "markPrice": "63100.00",
                    "liquidationPrice": "62500.00",  # less than 1% away
                    "leverage": "20",
                }
            ],
        }
        summary = FuturesAnalyzer.analyze(critical_data)
        self.assertEqual(summary.risk_status, "CRITICAL_LIQUIDATION_RISK")

    def test_empty_futures_data_handled_gracefully(self):
        summary = FuturesAnalyzer.analyze({})
        self.assertEqual(summary.total_margin_balance_usd, 0.0)
        self.assertEqual(len(summary.positions), 0)
        self.assertEqual(summary.risk_status, "SAFE")


if __name__ == "__main__":
    unittest.main()
