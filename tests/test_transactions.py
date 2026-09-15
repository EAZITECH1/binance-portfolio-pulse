"""
Unit tests for Binance Trade Execution and Transfer (Deposit/Withdrawal) Analytics.
"""
import unittest
from src.analytics.transactions import TransactionHistoryAnalyzer
from src.connectors.mock_provider import MockDataProvider
from src.connectors.mcp_client import BinanceMCPClient


class TestTransactionHistoryAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_provider = MockDataProvider()
        self.mcp_client = BinanceMCPClient()

    def test_parse_trades_analytics(self):
        sample_trades = [
            {
                "symbol": "BTCUSDT",
                "id": 1,
                "orderId": 101,
                "price": "60000.00",
                "qty": "0.10",
                "quoteQty": "6000.00",
                "commission": "0.001",
                "commissionAsset": "BNB",
                "time": 1700000000000,
                "isBuyer": True,
                "isMaker": False,
            },
            {
                "symbol": "BTCUSDT",
                "id": 2,
                "orderId": 102,
                "price": "65000.00",
                "qty": "0.05",
                "quoteQty": "3250.00",
                "commission": "0.0005",
                "commissionAsset": "BNB",
                "time": 1700001000000,
                "isBuyer": False,
                "isMaker": True,
            },
        ]
        res = TransactionHistoryAnalyzer.parse_trades("BTCUSDT", sample_trades)
        self.assertEqual(res.symbol, "BTCUSDT")
        self.assertEqual(res.total_trades, 2)
        self.assertEqual(res.total_buy_volume_usd, 6000.00)
        self.assertEqual(res.total_sell_volume_usd, 3250.00)
        self.assertEqual(res.total_volume_usd, 9250.00)
        self.assertEqual(res.avg_buy_price, 60000.00)
        self.assertEqual(res.avg_sell_price, 65000.00)
        self.assertAlmostEqual(res.total_fees_by_asset["BNB"], 0.0015, places=5)
        self.assertIn("Binance Trade History: BTCUSDT", res.format_summary())

    def test_parse_transfers_analytics(self):
        deps = [
            {"coin": "USDT", "amount": "1000.0", "status": 1, "network": "TRX", "insertTime": 1700000000000},
            {"coin": "BTC", "amount": "0.1", "status": 1, "network": "BTC", "insertTime": 1700001000000},
        ]
        wits = [
            {"coin": "USDT", "amount": "300.0", "transactionFee": "1.0", "status": 6, "network": "BSC", "applyTime": "2026-09-01"},
        ]
        res = TransactionHistoryAnalyzer.parse_transfers(deps, wits)
        self.assertEqual(res.total_deposits, 2)
        self.assertEqual(res.total_withdrawals, 1)
        self.assertEqual(res.deposits_by_coin["USDT"], 1000.0)
        self.assertEqual(res.withdrawals_by_coin["USDT"], 300.0)
        self.assertEqual(res.net_funding_by_coin["USDT"], 700.0)
        self.assertEqual(res.net_funding_by_coin["BTC"], 0.1)
        self.assertIn("Binance Transfers & Cash Flow History", res.format_summary())

    def test_mcp_call_tool_get_my_trades(self):
        res = self.mcp_client.call_tool("get_my_trades", {"symbol": "ETHUSDT", "limit": 10})
        self.assertEqual(res["symbol"], "ETHUSDT")
        self.assertIn("total_trades", res)
        self.assertIn("total_volume_usd", res)
        self.assertIn("trades", res)

    def test_mcp_call_tool_transfers(self):
        dep_res = self.mcp_client.call_tool("get_deposit_history", {"limit": 10})
        self.assertIn("total_deposits", dep_res)
        self.assertIn("deposits", dep_res)

        wit_res = self.mcp_client.call_tool("get_withdraw_history", {"limit": 10})
        self.assertIn("total_withdrawals", wit_res)
        self.assertIn("withdrawals", wit_res)

    def test_ask_portfoliopulse_transfers_and_trades_intent(self):
        ans_dep = self.mcp_client.ask_portfoliopulse("Show my deposit and withdrawal history")
        self.assertIn("Binance Transfers & Cash Flow History", ans_dep["answer"])

        ans_tr = self.mcp_client.ask_portfoliopulse("Show my trade history for SOL")
        self.assertIn("Binance Trade History: SOLUSDT", ans_tr["answer"])


if __name__ == "__main__":
    unittest.main()
