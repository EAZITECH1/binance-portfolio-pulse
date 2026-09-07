"""
Unit tests for Web3 content creation and market intelligence modules.
Verifies character count constraints (<=280 chars), thread structuring, and brief synthesis.
"""
import unittest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analytics.market_brief import MarketBriefGenerator, MarketBrief
from src.content.tweet_drafter import TweetDrafter
from src.connectors.mock_provider import MockDataProvider
from src.analytics.portfolio import PortfolioAnalyzer


class TestContentAndMarketBrief(unittest.TestCase):

    def setUp(self):
        self.mock_provider = MockDataProvider()
        self.brief = MarketBriefGenerator.generate(mode="mock")

    def test_market_brief_structure(self):
        """Verify market brief contains headline, sentiment, key points, and metrics."""
        self.assertTrue(len(self.brief.headline) > 10)
        self.assertIn(self.brief.sentiment, [
            "BULLISH_EXPANSION", "MODERATE_RISK_ON", "NEUTRAL_CONSOLIDATION",
            "MILD_PULLBACK", "BEARISH_RETREAT"
        ])
        self.assertTrue(len(self.brief.key_points) >= 3)
        self.assertTrue(len(self.brief.top_gainers) >= 1)
        self.assertTrue(len(self.brief.top_losers) >= 1)
        self.assertIn("btc_price", self.brief.metrics)

        # Verify markdown export
        md = self.brief.to_markdown()
        self.assertIn("# 🌐 Binance Agent OS - Daily Market Brief", md)
        self.assertIn("Top Movers", md)

    def test_market_single_tweet_length(self):
        """Verify single market tweet strictly respects Twitter's 280-char ceiling."""
        draft = TweetDrafter.draft_market_tweet(self.brief, style="single")
        self.assertEqual(draft.total_tweets, 1)
        for t in draft.tweets:
            self.assertLessEqual(len(t), 280, f"Tweet exceeds 280 characters: {len(t)}")
        self.assertIn("#Bitcoin", draft.tweets[0])

    def test_market_thread_tweet_formatting(self):
        """Verify market thread generates numbered tweets, each under 280 characters."""
        draft = TweetDrafter.draft_market_tweet(self.brief, style="thread")
        self.assertEqual(draft.total_tweets, 3)
        for i, t in enumerate(draft.tweets):
            self.assertLessEqual(len(t), 280, f"Thread tweet {i+1} exceeds 280 chars: {len(t)}")
            self.assertIn(f"({i+1}/3)", t)

    def test_portfolio_single_tweet_length(self):
        """Verify single portfolio performance tweet is under 280 characters."""
        raw = self.mock_provider.get_account_balances()
        tickers = {
            f"{item['asset']}USDT": self.mock_provider.get_ticker_24hr(f"{item['asset']}USDT")
            for item in raw
        }
        summary = PortfolioAnalyzer.analyze(raw, tickers)
        draft = TweetDrafter.draft_portfolio_tweet(summary, style="single")

        self.assertEqual(draft.total_tweets, 1)
        for t in draft.tweets:
            self.assertLessEqual(len(t), 280)
            self.assertIn("PORTFOLIO UPDATE", t)

    def test_portfolio_thread_tweet_formatting(self):
        """Verify portfolio performance thread is correctly numbered and under 280 chars."""
        raw = self.mock_provider.get_account_balances()
        tickers = {
            f"{item['asset']}USDT": self.mock_provider.get_ticker_24hr(f"{item['asset']}USDT")
            for item in raw
        }
        summary = PortfolioAnalyzer.analyze(raw, tickers)
        draft = TweetDrafter.draft_portfolio_tweet(summary, style="thread")

        self.assertEqual(draft.total_tweets, 3)
        for i, t in enumerate(draft.tweets):
            self.assertLessEqual(len(t), 280)
            self.assertIn(f"({i+1}/3)", t)


if __name__ == "__main__":
    unittest.main()
