"""
Unit tests for Binance market overview and ticker intelligence features.
Verifies watchlist filtering, top movers calculation, volume aggregation, and sentiment classification.
"""
import unittest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.connectors.mock_provider import MockDataProvider
from src.connectors.mcp_client import BinanceMCPClient


class TestMarketOverview(unittest.TestCase):

    def setUp(self):
        self.mock_provider = MockDataProvider()
        self.mcp_client = BinanceMCPClient()

    def test_market_overview_watchlist(self):
        """Verify get_market_overview respects watchlist and identifies top movers."""
        watchlist = ["BTC", "ETH", "SOL", "SUI", "BNB"]
        overview = self.mock_provider.get_market_overview(watchlist)

        self.assertEqual(len(overview["assets"]), 5)
        self.assertTrue(len(overview["top_gainers"]) >= 1)
        self.assertTrue(len(overview["top_losers"]) >= 1)
        self.assertGreater(overview["total_tracked_volume_usd"], 0)
        self.assertIn("sentiment", overview)

    def test_mcp_client_tools_list_has_no_non_binance_tools(self):
        """Verify get_price_feed_snapshot is not present in MCP tool definitions."""
        from unittest.mock import patch
        with patch.object(self.mcp_client, "send_mcp_request", return_value={}):
            tools = self.mcp_client.list_tools()
        tool_names = [t["name"] for t in tools]
        self.assertNotIn("get_price_feed_snapshot", tool_names)
        self.assertNotIn("get_onchain_snapshot", tool_names)
        self.assertIn("get_market_overview", tool_names)
        self.assertIn("generate_market_brief", tool_names)
        self.assertIn("get_top_by_market_cap", tool_names)
        self.assertEqual(len(tools), 8)

    def test_market_overview_drops_unknown_symbols(self):
        """Verify unknown or unlisted tokens like FAKECOIN are dropped and not fabricated as top gainers."""
        watchlist = ["BTC", "FAKECOIN", "ETH"]
        overview = self.mock_provider.get_market_overview(watchlist)
        asset_names = [a["asset"] for a in overview["assets"]]
        self.assertIn("BTC", asset_names)
        self.assertIn("ETH", asset_names)
        self.assertNotIn("FAKECOIN", asset_names)
        gainer_assets = [g["asset"] for g in overview["top_gainers"]]
        self.assertNotIn("FAKECOIN", gainer_assets)

    def test_get_top_by_market_cap(self):
        """Verify get_top_by_market_cap returns ranked coins with market cap data including stablecoins."""
        top = self.mock_provider.get_top_by_market_cap(limit=5)
        self.assertEqual(len(top), 5)
        self.assertEqual(top[0]["rank"], 1)
        self.assertEqual(top[0]["asset"], "BTC")
        self.assertIn("USDT", [c["asset"] for c in top])
        self.assertIn("market_cap_formatted", top[0])
        self.assertGreater(top[0]["market_cap_usd"], 0)


if __name__ == "__main__":
    unittest.main()
