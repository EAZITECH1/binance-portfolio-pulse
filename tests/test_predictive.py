"""
Unit tests for predictive balance forecasting, empirical beta, and scenario stress-testing.
"""
import unittest

from src.analytics.portfolio import PortfolioAnalyzer
from src.analytics.futures import FuturesAnalyzer
from src.analytics.predictive import PredictiveBalanceEngine, PredictiveBalanceReport
from src.connectors.mock_provider import MockDataProvider


class TestPredictiveAnalytics(unittest.TestCase):

    def setUp(self):
        self.mock = MockDataProvider()
        self.raw_balances = self.mock.get_account_balances()
        self.tickers = {
            f"{item['asset']}USDT": self.mock.get_ticker_24hr(f"{item['asset']}USDT")
            for item in self.raw_balances
            if item["asset"] not in ("USDT", "USDC", "FDUSD")
        }
        self.spot_summary = PortfolioAnalyzer.analyze(self.raw_balances, self.tickers)
        self.futures_summary = FuturesAnalyzer.analyze(self.mock.get_futures_account())
        self.symbols = [p.asset for p in self.spot_summary.positions]
        self.klines_batch = self.mock.get_historical_klines_batch(
            [f"{s}USDT" for s in self.symbols] + ["BTCUSDT"], limit=30
        )

    def test_predictive_engine_generates_complete_report(self):
        report = PredictiveBalanceEngine.forecast(
            self.spot_summary, self.futures_summary, self.klines_batch
        )
        self.assertIsInstance(report, PredictiveBalanceReport)
        self.assertGreater(report.current_total_balance_usd, 0)
        self.assertGreater(report.projected_7d_base_usd, 0)
        self.assertGreater(report.var_95_7d_usd, 0)
        self.assertGreater(report.var_99_7d_usd, report.var_95_7d_usd)

    def test_asset_betas_and_stablecoin_properties(self):
        betas, vols = PredictiveBalanceEngine.calculate_betas_and_volatilities(
            self.klines_batch, ["BTC", "ETH", "USDT"]
        )
        self.assertEqual(betas.get("BTC"), 1.0)
        self.assertEqual(betas.get("USDT"), 0.0)
        self.assertEqual(vols.get("USDT"), 0.0)
        self.assertGreater(vols.get("BTC", 0), 0)

    def test_stress_test_scenarios_logic(self):
        report = PredictiveBalanceEngine.forecast(
            self.spot_summary, self.futures_summary, self.klines_batch
        )
        scenario_names = [s.name for s in report.scenarios]
        self.assertTrue(any("Bull" in n for n in scenario_names))
        self.assertTrue(any("Bear" in n for n in scenario_names))
        self.assertTrue(any("Crash" in n for n in scenario_names))

        bull = next(s for s in report.scenarios if "Bull" in s.name)
        bear = next(s for s in report.scenarios if "Bear" in s.name)
        self.assertGreater(bull.projected_balance_usd, report.current_total_balance_usd)
        self.assertLess(bear.projected_balance_usd, report.current_total_balance_usd)

    def test_zero_balance_handled_cleanly(self):
        empty_spot = PortfolioAnalyzer.analyze([], {})
        report = PredictiveBalanceEngine.forecast(empty_spot, None, {})
        self.assertEqual(report.current_total_balance_usd, 0.0)
        self.assertEqual(report.var_95_7d_usd, 0.0)
        self.assertEqual(len(report.scenarios), 0)


if __name__ == "__main__":
    unittest.main()
