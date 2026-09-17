"""
Binance Read-Only Transaction, Past Trade Fill, and Transfer (Deposit/Withdrawal) Analytics.
Parses historical spot trade fills (myTrades) on any pair, deposit records, and withdrawal records.
Strictly read-only; does not place or execute orders.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


@dataclass
class TradeExecution:
    symbol: str
    order_id: int
    trade_id: int
    price: float
    quantity: float
    quote_quantity: float
    commission: float
    commission_asset: str
    is_buyer: bool
    is_maker: bool
    timestamp_ms: int

    @property
    def side(self) -> str:
        return "BUY" if self.is_buyer else "SELL"

    @property
    def formatted_time(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp_ms / 1000.0, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "order_id": self.order_id,
            "trade_id": self.trade_id,
            "side": self.side,
            "price": round(self.price, 8),
            "quantity": round(self.quantity, 6),
            "quote_quantity": round(self.quote_quantity, 2),
            "commission": round(self.commission, 6),
            "commission_asset": self.commission_asset,
            "is_maker": self.is_maker,
            "timestamp_ms": self.timestamp_ms,
            "datetime_utc": self.formatted_time,
        }


@dataclass
class TransferRecord:
    transfer_type: str  # "DEPOSIT" or "WITHDRAWAL"
    coin: str
    amount: float
    status: str  # "COMPLETED", "PENDING", "FAILED"
    network: Optional[str] = None
    address: Optional[str] = None
    tx_id: Optional[str] = None
    fee: float = 0.0
    timestamp_ms: Optional[int] = None
    timestamp_str: Optional[str] = None

    @property
    def formatted_time(self) -> str:
        if self.timestamp_ms:
            dt = datetime.fromtimestamp(self.timestamp_ms / 1000.0, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        return self.timestamp_str or "N/A"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.transfer_type,
            "coin": self.coin,
            "amount": round(self.amount, 6),
            "fee": round(self.fee, 6),
            "status": self.status,
            "network": self.network,
            "address": self.address,
            "tx_id": self.tx_id,
            "datetime_utc": self.formatted_time,
        }


@dataclass
class TradeHistoryAnalysis:
    symbol: str
    total_trades: int
    total_buy_volume_usd: float
    total_sell_volume_usd: float
    total_volume_usd: float
    total_quantity_bought: float
    total_quantity_sold: float
    avg_buy_price: float
    avg_sell_price: float
    total_fees_by_asset: Dict[str, float] = field(default_factory=dict)
    trades: List[TradeExecution] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "total_trades": self.total_trades,
            "total_buy_volume_usd": round(self.total_buy_volume_usd, 2),
            "total_sell_volume_usd": round(self.total_sell_volume_usd, 2),
            "total_volume_usd": round(self.total_volume_usd, 2),
            "total_quantity_bought": round(self.total_quantity_bought, 6),
            "total_quantity_sold": round(self.total_quantity_sold, 6),
            "avg_buy_price": round(self.avg_buy_price, 4),
            "avg_sell_price": round(self.avg_sell_price, 4),
            "total_fees_by_asset": {k: round(v, 6) for k, v in self.total_fees_by_asset.items()},
            "trades": [t.to_dict() for t in self.trades],
        }

    def format_summary(self) -> str:
        lines = [
            f"📋 **Binance Trade History: {self.symbol} (Read-Only)**",
            f"• **Past Filled Orders:** {self.total_trades}",
            f"• **Total Volume:** ${self.total_volume_usd:,.2f} (Buys: ${self.total_buy_volume_usd:,.2f} | Sells: ${self.total_sell_volume_usd:,.2f})",
            f"• **Avg Fill Price:** Buy: ${self.avg_buy_price:,.2f} | Sell: ${self.avg_sell_price:,.2f}",
        ]
        if self.total_fees_by_asset:
            fees_str = ", ".join(f"{v:.4f} {k}" for k, v in self.total_fees_by_asset.items())
            lines.append(f"• **Commissions Paid:** {fees_str}")
        return "\n".join(lines)


@dataclass
class TransferHistoryAnalysis:
    total_deposits: int
    total_withdrawals: int
    deposits_by_coin: Dict[str, float] = field(default_factory=dict)
    withdrawals_by_coin: Dict[str, float] = field(default_factory=dict)
    net_funding_by_coin: Dict[str, float] = field(default_factory=dict)
    transfers: List[TransferRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_deposits": self.total_deposits,
            "total_withdrawals": self.total_withdrawals,
            "deposits_by_coin": {k: round(v, 4) for k, v in self.deposits_by_coin.items()},
            "withdrawals_by_coin": {k: round(v, 4) for k, v in self.withdrawals_by_coin.items()},
            "net_funding_by_coin": {k: round(v, 4) for k, v in self.net_funding_by_coin.items()},
            "transfers": [t.to_dict() for t in self.transfers],
        }

    def format_summary(self) -> str:
        lines = [
            "💳 **Binance Transfers & Cash Flow History**",
            f"• **Deposits:** {self.total_deposits} records | **Withdrawals:** {self.total_withdrawals} records",
        ]
        all_coins = set(list(self.deposits_by_coin.keys()) + list(self.withdrawals_by_coin.keys()))
        if all_coins:
            lines.append("• **Net Funding by Asset:**")
            for c in sorted(all_coins):
                dep = self.deposits_by_coin.get(c, 0.0)
                wit = self.withdrawals_by_coin.get(c, 0.0)
                net = dep - wit
                sign = "+" if net >= 0 else ""
                lines.append(f"   - **{c}**: {sign}{net:,.4f} (In: {dep:,.4f} | Out: {wit:,.4f})")
        return "\n".join(lines)


class TransactionHistoryAnalyzer:
    """Quantitative transaction, trade execution, and wallet transfer parser."""

    @classmethod
    def parse_trades(cls, symbol: str, raw_trades: List[Dict[str, Any]]) -> TradeHistoryAnalysis:
        parsed_trades: List[TradeExecution] = []
        total_buy_usd = 0.0
        total_sell_usd = 0.0
        total_buy_qty = 0.0
        total_sell_qty = 0.0
        fees_map: Dict[str, float] = {}

        for item in raw_trades:
            try:
                p = float(item.get("price") or 0.0)
                q = float(item.get("qty") or 0.0)
                quote_q = float(item.get("quoteQty") or (p * q))
                comm = float(item.get("commission") or 0.0)
                comm_asset = str(item.get("commissionAsset") or "USDT").upper()
                is_buyer = bool(item.get("isBuyer", False))
                is_maker = bool(item.get("isMaker", False))
                t_ms = int(item.get("time") or 0)
                t_id = int(item.get("id") or 0)
                o_id = int(item.get("orderId") or 0)

                exec_record = TradeExecution(
                    symbol=symbol.upper(),
                    order_id=o_id,
                    trade_id=t_id,
                    price=p,
                    quantity=q,
                    quote_quantity=quote_q,
                    commission=comm,
                    commission_asset=comm_asset,
                    is_buyer=is_buyer,
                    is_maker=is_maker,
                    timestamp_ms=t_ms,
                )
                parsed_trades.append(exec_record)

                if is_buyer:
                    total_buy_usd += quote_q
                    total_buy_qty += q
                else:
                    total_sell_usd += quote_q
                    total_sell_qty += q

                if comm > 0 and comm_asset:
                    fees_map[comm_asset] = fees_map.get(comm_asset, 0.0) + comm
            except Exception:
                continue

        avg_buy_p = (total_buy_usd / total_buy_qty) if total_buy_qty > 0 else 0.0
        avg_sell_p = (total_sell_usd / total_sell_qty) if total_sell_qty > 0 else 0.0

        return TradeHistoryAnalysis(
            symbol=symbol.upper(),
            total_trades=len(parsed_trades),
            total_buy_volume_usd=total_buy_usd,
            total_sell_volume_usd=total_sell_usd,
            total_volume_usd=total_buy_usd + total_sell_usd,
            total_quantity_bought=total_buy_qty,
            total_quantity_sold=total_sell_qty,
            avg_buy_price=avg_buy_p,
            avg_sell_price=avg_sell_p,
            total_fees_by_asset=fees_map,
            trades=parsed_trades,
        )

    @classmethod
    def parse_transfers(
        cls,
        raw_deposits: List[Dict[str, Any]],
        raw_withdrawals: List[Dict[str, Any]],
    ) -> TransferHistoryAnalysis:
        records: List[TransferRecord] = []
        dep_map: Dict[str, float] = {}
        wit_map: Dict[str, float] = {}

        # Deposit status codes: 0: pending, 6: credited but cannot withdraw, 1: success
        for d in raw_deposits:
            try:
                coin = str(d.get("coin") or "").upper()
                amt = float(d.get("amount") or 0.0)
                status_code = d.get("status")
                status = "COMPLETED" if status_code == 1 else ("PENDING" if status_code == 0 else "PROCESSING")
                t_ms = int(d.get("insertTime") or 0)
                records.append(
                    TransferRecord(
                        transfer_type="DEPOSIT",
                        coin=coin,
                        amount=amt,
                        status=status,
                        network=d.get("network"),
                        address=d.get("address"),
                        tx_id=d.get("txId"),
                        fee=0.0,
                        timestamp_ms=t_ms,
                    )
                )
                if status == "COMPLETED":
                    dep_map[coin] = dep_map.get(coin, 0.0) + amt
            except Exception:
                continue

        # Withdrawal status codes: 0: Email Sent, 1: Cancelled, 2: Awaiting Approval, 3: Rejected, 4: Processing, 5: Failure, 6: Completed
        for w in raw_withdrawals:
            try:
                coin = str(w.get("coin") or "").upper()
                amt = float(w.get("amount") or 0.0)
                fee = float(w.get("transactionFee") or 0.0)
                status_code = w.get("status")
                status = "COMPLETED" if status_code == 6 else ("PROCESSING" if status_code in (2, 4) else "PENDING")
                records.append(
                    TransferRecord(
                        transfer_type="WITHDRAWAL",
                        coin=coin,
                        amount=amt,
                        status=status,
                        network=w.get("network"),
                        address=w.get("address"),
                        tx_id=w.get("txId"),
                        fee=fee,
                        timestamp_str=w.get("completeTime") or w.get("applyTime"),
                    )
                )
                if status == "COMPLETED":
                    wit_map[coin] = wit_map.get(coin, 0.0) + amt
            except Exception:
                continue

        all_coins = set(list(dep_map.keys()) + list(wit_map.keys()))
        net_map = {c: dep_map.get(c, 0.0) - wit_map.get(c, 0.0) for c in all_coins}

        return TransferHistoryAnalysis(
            total_deposits=len(raw_deposits),
            total_withdrawals=len(raw_withdrawals),
            deposits_by_coin=dep_map,
            withdrawals_by_coin=wit_map,
            net_funding_by_coin=net_map,
            transfers=records,
        )
