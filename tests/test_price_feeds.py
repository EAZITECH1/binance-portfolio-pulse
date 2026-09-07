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
        tools = self.mcp_client.list_tools()
        tool_names = [t["name"] for t in tools]
        self.assertNotIn("get_price_feed_snapshot", tool_names)
        self.assertNotIn("get_onchain_snapshot", tool_names)
        self.assertIn("get_market_overview", tool_names)
        self.assertIn("generate_market_brief", tool_names)
        self.assertEqual(len(tools), 7)


if __name__ == "__main__":
    unittest.main()
