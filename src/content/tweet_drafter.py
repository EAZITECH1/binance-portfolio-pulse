"""
Tweet Drafter for Web3 Content Creators.
Transforms market intelligence briefs and portfolio reports into publication-ready
tweets and threads in crypto-media style (Cointelegraph / CoinMarketCap).
Strictly adheres to Twitter/X's 280-character limit.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Union, Optional

from ..analytics.market_brief import MarketBrief
from ..analytics.portfolio import PortfolioSummary
from ..analytics.ai_summary import PlainLanguageSummary


@dataclass
class DraftedTweet:
    style: str  # "single" or "thread"
    topic: str  # "market" or "portfolio"
    tweets: List[str]
    total_tweets: int
    char_counts: List[int]
    formatted_preview: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style,
            "topic": self.topic,
            "total_tweets": self.total_tweets,
            "tweets": self.tweets,
            "char_counts": self.char_counts,
            "formatted_preview": self.formatted_preview,
        }


class TweetDrafter:
    """Drafts crisp, high-engagement tweets and threads within 280 character limits."""

    MAX_TWEET_LEN = 280

    @classmethod
    def _truncate_if_needed(cls, text: str, max_len: int = 280) -> str:
        """Ensure text never breaches Twitter/X character limits."""
        if len(text) <= max_len:
            return text
        return text[:max_len - 3].rstrip() + "..."

    @classmethod
    def draft_market_tweet(
        cls,
        brief: Union[MarketBrief, Dict[str, Any]],
        style: str = "single",
    ) -> DraftedTweet:
        """Drafts a Cointelegraph/CMC style tweet from a MarketBrief."""
        b_dict = brief.to_dict() if hasattr(brief, "to_dict") else brief
        metrics = b_dict.get("metrics", {})
        top_gainers = b_dict.get("top_gainers", [])

        btc_p = metrics.get("btc_price", 63450.0)
        btc_c = metrics.get("btc_change_24h", 3.15)
        sol_p = metrics.get("sol_price", 164.80)
        sol_c = metrics.get("sol_change_24h", 9.42)
        top_g = top_gainers[0] if top_gainers else {"asset": "SUI", "priceChangePercent": 14.7}
        tvl = metrics.get("tvl_usd", "94.5B")
        whale = metrics.get("whale_signal", "NET OUTFLOW ($320M)")

        btc_sign = "+" if btc_c >= 0 else ""
        sol_sign = "+" if sol_c >= 0 else ""

        if style == "thread":
            # Tweet 1: Hook + Lead stats
            t1 = (
                f"🚨 MARKET PULSE: Crypto pushes higher as Bitcoin holds steady "
                f"above ${btc_p:,.0f} ({btc_sign}{btc_c:.1f}%).\n\n"
                f"Selective altcoins are leading the charge today, with {top_g['asset']} "
                f"and $SOL seeing heavy spot inflows.\n\n"
                f"Here's what you need to know today 🧵👇 (1/3)"
            )
            t1 = cls._truncate_if_needed(t1)

            # Tweet 2: Movers & Market Data pulse
            t2 = (
                f"📊 KEY MOVERS & MARKET DATA:\n\n"
                f"• $SOL: ${sol_p:,.2f} ({sol_sign}{sol_c:.1f}%)\n"
                f"• ${top_g['asset']}: +{top_g['priceChangePercent']:.1f}%\n"
                f"• Total DeFi TVL: ${tvl}\n"
                f"• Whale flow: {whale}\n\n"
                f"Institutional accumulation signals remain active across major exchanges. (2/3)"
            )
            t2 = cls._truncate_if_needed(t2)

            # Tweet 3: Outlook & Takeaway
            t3 = (
                f"💡 TAKEAWAY: Capital is rotating into high-beta layer-1s while BTC "
                f"builds liquidity above support.\n\n"
                f"Are you taking profits into stables or riding the momentum?\n\n"
                f"#Bitcoin #Solana #Crypto #Binance (3/3)"
            )
            t3 = cls._truncate_if_needed(t3)

            tweets = [t1, t2, t3]
        else:
            # Single punchy tweet (Cointelegraph / CoinMarketCap format)
            single = (
                f"⚡ MARKET UPDATE: Bitcoin trades at ${btc_p:,.0f} ({btc_sign}{btc_c:.1f}%) "
                f"as altcoin momentum accelerates.\n\n"
                f"Top runners: ${top_g['asset']} (+{top_g['priceChangePercent']:.1f}%) & "
                f"$SOL ${sol_p:,.2f} ({sol_sign}{sol_c:.1f}%).\n"
                f"DeFi TVL holds at ${tvl} with exchange outflows pointing to accumulation.\n\n"
                f"#Bitcoin #Crypto #Binance"
            )
            tweets = [cls._truncate_if_needed(single)]

        char_counts = [len(t) for t in tweets]
        preview = "\n\n---\n\n".join(
            f"Tweet {i+1} ({len(t)}/280 chars):\n{t}" for i, t in enumerate(tweets)
        )

        return DraftedTweet(
            style=style,
            topic="market",
            tweets=tweets,
            total_tweets=len(tweets),
            char_counts=char_counts,
            formatted_preview=preview,
        )

    @classmethod
    def draft_portfolio_tweet(
        cls,
        summary: PortfolioSummary,
        ai_summary: Optional[PlainLanguageSummary] = None,
        style: str = "single",
    ) -> DraftedTweet:
        """Drafts a shareable personal portfolio performance post."""
        pnl_sign = "+" if summary.total_24h_pnl_usd >= 0 else "-"
        abs_pnl_usd = abs(summary.total_24h_pnl_usd)
        abs_pnl_pct = abs(summary.total_24h_pnl_pct)

        # Top asset
        top_pos = summary.positions[0] if summary.positions else None
        top_asset_str = f"${top_pos.asset} ({top_pos.allocation_pct:.0f}%)" if top_pos else "Crypto"

        if style == "thread":
            t1 = (
                f"📈 PORTFOLIO PULSE: 24-hour recap.\n\n"
                f"Net movement: {pnl_sign}${abs_pnl_usd:,.2f} ({pnl_sign}{abs_pnl_pct:.2f}%).\n"
                f"Total valuation: ${summary.total_value_usd:,.2f} across {summary.asset_count} assets.\n\n"
                f"Quick breakdown of allocation & risk flags 🧵👇 (1/3)"
            )
            t1 = cls._truncate_if_needed(t1)

            # Asset breakdown
            assets_brief = " | ".join(f"${p.asset}: {p.allocation_pct:.0f}%" for p in summary.positions[:4])
            t2 = (
                f"💼 ALLOCATION & STABLES:\n\n"
                f"• Core positions: {assets_brief}\n"
                f"• Stablecoin cushion: ${summary.stablecoin_value_usd:,.2f} ({summary.stablecoin_pct:.1f}%)\n\n"
                f"Maintaining cash buffers to deploy on dips without forced liquidations. (2/3)"
            )
            t2 = cls._truncate_if_needed(t2)

            t3 = (
                f"🎯 TAKEAWAY: {top_asset_str} drove today's P&L. Rebalancing "
                f"thresholds monitored via @Binance Agent OS.\n\n"
                f"Daily risk check completed. Ready for tomorrow's session.\n\n"
                f"#DeFi #CryptoPortfolio #BinanceAgentOS (3/3)"
            )
            t3 = cls._truncate_if_needed(t3)
            tweets = [t1, t2, t3]
        else:
            single = (
                f"📊 PORTFOLIO UPDATE: Balance moved {pnl_sign}${abs_pnl_usd:,.2f} "
                f"({pnl_sign}{abs_pnl_pct:.2f}%) over the last 24h to ${summary.total_value_usd:,.2f}.\n\n"
                f"Lead holding: {top_asset_str}. Stable reserve holds at {summary.stablecoin_pct:.1f}%.\n"
                f"Tracked autonomously with Binance Agent OS.\n\n"
                f"#Crypto #Binance #DeFi"
            )
            tweets = [cls._truncate_if_needed(single)]

        char_counts = [len(t) for t in tweets]
        preview = "\n\n---\n\n".join(
            f"Tweet {i+1} ({len(t)}/280 chars):\n{t}" for i, t in enumerate(tweets)
        )

        return DraftedTweet(
            style=style,
            topic="portfolio",
            tweets=tweets,
            total_tweets=len(tweets),
            char_counts=char_counts,
            formatted_preview=preview,
        )

    @classmethod
    def draft(
        cls,
        brief_or_summary: Any,
        style: str = "single",
        topic: str = "market",
    ) -> DraftedTweet:
        """Unified dispatch method for drafting tweets."""
        if topic == "portfolio" or isinstance(brief_or_summary, PortfolioSummary):
            if isinstance(brief_or_summary, PortfolioSummary):
                return cls.draft_portfolio_tweet(brief_or_summary, style=style)
            raise ValueError("Portfolio topic requires a PortfolioSummary object")
        else:
            return cls.draft_market_tweet(brief_or_summary, style=style)
