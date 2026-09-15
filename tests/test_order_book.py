"""
Unit tests for Binance Order Book Depth, Spreads, and Liquidity Imbalance.
"""
import unittest
from src.analytics.order_book import OrderBookAnalyzer, OrderBookAnalysis
from src.connectors.mock_provider import MockDataProvider
from src.connectors.mcp_client import BinanceMCPClient


class TestOrderBookAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_provider = MockDataProvider()
        self.mcp_client = BinanceMCPClient()

    def test_order_book_analyzer_calculations(self):
        sample_depth = {
            "lastUpdateId": 12345,
            "bids": [
                ["75000.00", "2.0"],
                ["74990.00", "1.0"],
            ],
            "asks": [
                ["75010.00", "1.5"],
                ["75020.00", "3.0"],
            ],
        }
        res: OrderBookAnalysis = OrderBookAnalyzer.analyze("BTCUSDT", sample_depth)

        self.assertEqual(res.symbol, "BTCUSDT")
        self.assertEqual(res.best_bid, 75000.0)
        self.assertEqual(res.best_ask, 75010.0)
        self.assertEqual(res.mid_price, 75005.0)
        self.assertAlmostEqual(res.spread_usd, 10.0, places=2)
        expected_bps = (10.0 / 75005.0) * 10000.0
        self.assertAlmostEqual(res.spread_bps, expected_bps, places=2)

        # Depth USD
        expected_bid_usd = (75000.0 * 2.0) + (74990.0 * 1.0)
        expected_ask_usd = (75010.0 * 1.5) + (75020.0 * 3.0)
        self.assertEqual(res.bid_depth_usd, expected_bid_usd)
        self.assertEqual(res.ask_depth_usd, expected_ask_usd)
        self.assertEqual(res.total_liquidity_usd, expected_bid_usd + expected_ask_usd)
        self.assertAlmostEqual(res.order_imbalance_ratio, expected_bid_usd / expected_ask_usd, places=3)
        self.assertEqual(res.market_regime, "TIGHT_SPREAD_LIQUID")

    def test_mock_provider_order_book(self):
        depth = self.mock_provider.get_order_book("ETHUSDT", limit=10)
        self.assertIn("bids", depth)
        self.assertIn("asks", depth)
        self.assertTrue(len(depth["bids"]) <= 10)
        self.assertTrue(len(depth["asks"]) <= 10)
        self.assertTrue(float(depth["bids"][0][0]) < float(depth["asks"][0][0]))

    def test_mcp_call_tool_get_order_book(self):
        result = self.mcp_client.call_tool("get_order_book", {"symbol": "BTCUSDT", "limit": 20})
        self.assertEqual(result["symbol"], "BTCUSDT")
        self.assertIn("best_bid", result)
        self.assertIn("best_ask", result)
        self.assertIn("spread_usd", result)
        self.assertIn("spread_bps", result)
        self.assertIn("order_imbalance_ratio", result)
        self.assertIn("market_regime", result)

    def test_ask_portfoliopulse_order_book_intent(self):
        res = self.mcp_client.ask_portfoliopulse("What is the current order book spread for SOL?")
        self.assertIn("SOLUSDT", res["answer"])
        self.assertIn("Best Bid", res["answer"])
        self.assertIn("Best Ask", res["answer"])
        self.assertIn("Bid/Ask Spread", res["answer"])


if __name__ == "__main__":
    unittest.main()
