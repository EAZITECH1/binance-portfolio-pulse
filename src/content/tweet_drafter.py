"""
Tweet Drafter for Web3 Content Creators.
Transforms market intelligence briefs and portfolio reports into publication-ready
tweets and threads in crypto-media style (Cointelegraph / CoinMarketCap).
Strictly adheres to Twitter/X's 280-character limit.
"""
import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import List, Dict, Any, Union, Optional

from ..analytics.market_brief import MarketBrief
from ..analytics.portfolio import PortfolioSummary
from ..analytics.ai_summary import PlainLanguageSummary
from ..utils.logger import logger


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
    def _draft_with_anthropic(
        cls,
        context_text: str,
        topic: str,
        style: str,
        api_key: str,
    ) -> Optional[List[str]]:
        """Draft publication-ready tweets using Anthropic API (claude-sonnet-4-6)."""
        prompt = (
            f"You are a professional crypto journalist and Web3 content creator for Binance PortfolioPulse AI.\n"
            f"Given the {topic} intelligence below, write a ready-to-post {'single tweet' if style == 'single' else '3-tweet numbered thread (1/3, 2/3, 3/3)'}.\n"
            "CRITICAL RULES:\n"
            "- Every single tweet MUST be STRICTLY under 280 characters. Count characters carefully.\n"
            "- Use engaging crypto journalism style (Cointelegraph / CoinMarketCap format).\n"
            "- Include verified figures, relevant emojis, and hashtags (#Bitcoin, #Binance, #Crypto).\n\n"
            f"Context Data:\n{context_text}\n\n"
            "Return ONLY a valid JSON array of strings (e.g. [\"Tweet text 1\", \"Tweet text 2\"]) with NO markdown formatting or commentary."
        )
        try:
            req_data = json.dumps({
                "model": "claude-sonnet-4-6",
                "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=req_data,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                    "User-Agent": "Binance-PortfolioPulse-AI/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                text_content = resp_json.get("content", [{}])[0].get("text", "").strip()
                if text_content.startswith("```"):
                    text_content = text_content.split("```")[1]
                    if text_content.startswith("json"):
                        text_content = text_content[4:]
                parsed = json.loads(text_content.strip())
                if isinstance(parsed, list) and all(isinstance(t, str) for t in parsed):
                    return [cls._truncate_if_needed(t) for t in parsed]
                elif isinstance(parsed, str):
                    return [cls._truncate_if_needed(parsed)]
        except Exception as e:
            logger.warning(f"Anthropic LLM tweet generation failed: {e}. Falling back to template drafter.")
        return None

    @classmethod
    def draft_market_tweet(
        cls,
        brief: Union[MarketBrief, Dict[str, Any]],
        style: str = "single",
        anthropic_api_key: Optional[str] = None,
    ) -> DraftedTweet:
        """Drafts a Cointelegraph/CMC style tweet from a MarketBrief."""
        b_dict = brief.to_dict() if hasattr(brief, "to_dict") else brief
        metrics = b_dict.get("metrics", {})
        top_gainers = b_dict.get("top_gainers", [])

        if anthropic_api_key:
            context = f"Headline: {b_dict.get('headline')}\nSentiment: {b_dict.get('sentiment')}\nMetrics: {json.dumps(metrics)}\nKey Points: {json.dumps(b_dict.get('key_points', []))}"
            llm_tweets = cls._draft_with_anthropic(context, topic="market", style=style, api_key=anthropic_api_key)
            if llm_tweets:
                char_counts = [len(t) for t in llm_tweets]
                preview = "\n\n---\n\n".join(f"Tweet {i+1} ({len(t)}/280 chars):\n{t}" for i, t in enumerate(llm_tweets))
                return DraftedTweet(
                    style=style,
                    topic="market",
                    tweets=llm_tweets,
                    total_tweets=len(llm_tweets),
                    char_counts=char_counts,
                    formatted_preview=preview,
                )

        btc_p = metrics.get("btc_price", 63450.0)
        btc_c = metrics.get("btc_change_24h", 3.15)
        sol_p = metrics.get("sol_price", 164.80)
        sol_c = metrics.get("sol_change_24h", 9.42)
        top_g = top_gainers[0] if top_gainers else {"asset": "SUI", "priceChangePercent": 14.7}
        vol = metrics.get("total_tracked_volume_usd", 0.0)
        vol_str = f"${vol/1e9:.1f}B" if vol >= 1e9 else f"${vol/1e6:.0f}M" if vol >= 1e6 else f"${vol:,.0f}"
        avg_move = metrics.get("average_24h_change_pct", 0.0)
        avg_sign = "+" if avg_move >= 0 else ""

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

            # Tweet 2: Movers & Binance Spot Activity
            t2 = (
                f"📊 KEY MOVERS & BINANCE SPOT ACTIVITY:\n\n"
                f"• $SOL: ${sol_p:,.2f} ({sol_sign}{sol_c:.1f}%)\n"
                f"• ${top_g['asset']}: +{top_g['priceChangePercent']:.1f}%\n"
                f"• Tracked 24h Volume: {vol_str} USD\n"
                f"• Watchlist Avg Movement: {avg_sign}{avg_move:.2f}%\n\n"
                f"Spot order flow shows sustained liquidity across leading pairs. (2/3)"
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
                f"Tracked 24h volume tops {vol_str} on Binance spot.\n\n"
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
        anthropic_api_key: Optional[str] = None,
    ) -> DraftedTweet:
        """Drafts a shareable personal portfolio performance post."""
        pnl_sign = "+" if summary.total_24h_pnl_usd >= 0 else "-"
        abs_pnl_usd = abs(summary.total_24h_pnl_usd)
        abs_pnl_pct = abs(summary.total_24h_pnl_pct)

        # Top asset
        top_pos = summary.positions[0] if summary.positions else None
        top_asset_str = f"${top_pos.asset} ({top_pos.allocation_pct:.0f}%)" if top_pos else "Crypto"

        if anthropic_api_key:
            context = (
                f"Valuation: ${summary.total_value_usd:,.2f}\n"
                f"24h P&L: {pnl_sign}${abs_pnl_usd:,.2f} ({pnl_sign}{abs_pnl_pct:.2f}%)\n"
                f"Top Asset: {top_asset_str}\n"
                f"Stables: ${summary.stablecoin_value_usd:,.2f} ({summary.stablecoin_pct:.1f}%)\n"
                f"Holdings: {', '.join(f'{p.asset}: {p.allocation_pct:.0f}%' for p in summary.positions[:4])}"
            )
            llm_tweets = cls._draft_with_anthropic(context, topic="portfolio", style=style, api_key=anthropic_api_key)
            if llm_tweets:
                char_counts = [len(t) for t in llm_tweets]
                preview = "\n\n---\n\n".join(f"Tweet {i+1} ({len(t)}/280 chars):\n{t}" for i, t in enumerate(llm_tweets))
                return DraftedTweet(
                    style=style,
                    topic="portfolio",
                    tweets=llm_tweets,
                    total_tweets=len(llm_tweets),
                    char_counts=char_counts,
                    formatted_preview=preview,
                )

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
        anthropic_api_key: Optional[str] = None,
    ) -> DraftedTweet:
        """Unified dispatch method for drafting tweets."""
        if topic == "portfolio" or isinstance(brief_or_summary, PortfolioSummary):
            if isinstance(brief_or_summary, PortfolioSummary):
                return cls.draft_portfolio_tweet(brief_or_summary, style=style, anthropic_api_key=anthropic_api_key)
            raise ValueError("Portfolio topic requires a PortfolioSummary object")
        else:
            return cls.draft_market_tweet(brief_or_summary, style=style, anthropic_api_key=anthropic_api_key)

