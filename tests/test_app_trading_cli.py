from __future__ import annotations

import unittest

import app


class AppTradingCliTest(unittest.TestCase):
    def test_live_policy_summary_shows_default_blocked_state(self) -> None:
        summary = app.live_policy_summary()

        self.assertIn("Live trading enabled: False", summary)
        self.assertIn("Live Production Mode: False", summary)
        self.assertIn("Permission level: L0 RESEARCH", summary)

    def test_create_order_intent_rejects_invalid_side_before_market_lookup(self) -> None:
        result = app.create_order_intent(
            side_text="hold",
            ticker="AAPL",
            quantity_text="1",
            stop_loss_text="90",
            max_loss_text="10",
            reason="unit test",
        )

        self.assertEqual("Invalid side. Use buy or sell.", result)

    def test_create_order_intent_requires_reason_before_market_lookup(self) -> None:
        result = app.create_order_intent(
            side_text="buy",
            ticker="AAPL",
            quantity_text="1",
            stop_loss_text="90",
            max_loss_text="10",
            reason="",
        )

        self.assertEqual("Reason is required for every real-trading order intent.", result)


if __name__ == "__main__":
    unittest.main()

