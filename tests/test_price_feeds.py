"""
Unit tests for Price Feed Data Provider and expanded market overview features.
"""
import unittest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.connectors.price_feed_data import PriceFeedDataProvider
from src.connectors.mock_provider import MockDataProvider


class TestPriceFeedData(unittest.TestCase):

    def setUp(self):
        self.provider = PriceFeedDataProvider(mode="mock")
        self.mock_provider = MockDataProvider()

    def test_price_feed_snapshot_metrics(self):
        """Verify price feed snapshot contains required market and network metrics."""
        snapshot = self.provider.get_price_feed_snapshot()
        self.assertIn("bnb_chain", snapshot)
        self.assertIn("ethereum", snapshot)
        self.assertIn("solana", snapshot)
        self.assertIn("defi_pulse", snapshot)
        self.assertIn("oracle_network", snapshot)
        self.assertIn("whale_flow", snapshot)

        # Verify BNB Chain gas & txs
        self.assertGreater(snapshot["bnb_chain"]["daily_transactions"], 1000000)
        self.assertGreater(snapshot["bnb_chain"]["gas_gwei"], 0)

        # Verify DeFi TVL
        self.assertGreater(snapshot["defi_pulse"]["total_tvl_usd"], 1e10)

    def test_backward_compatibility_alias(self):
        """Verify get_onchain_snapshot backward compatibility alias works."""
        snapshot = self.provider.get_onchain_snapshot()
        self.assertIn("bnb_chain", snapshot)


    def test_market_overview_watchlist(self):
        """Verify get_market_overview respects watchlist and identifies top movers."""
        watchlist = ["BTC", "ETH", "SOL", "SUI", "BNB"]
        overview = self.mock_provider.get_market_overview(watchlist)

        self.assertEqual(len(overview["assets"]), 5)
        self.assertTrue(len(overview["top_gainers"]) >= 1)
        self.assertTrue(len(overview["top_losers"]) >= 1)
        self.assertGreater(overview["total_tracked_volume_usd"], 0)
        self.assertIn("sentiment", overview)


if __name__ == "__main__":
    unittest.main()
