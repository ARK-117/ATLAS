from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import app


class AppTradingCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_data_file = app.DATA_FILE
        app.DATA_FILE = str(Path(self.temp_dir.name) / "atlas_data.json")

    def tearDown(self) -> None:
        app.DATA_FILE = self.original_data_file
        self.temp_dir.cleanup()

    def test_live_policy_summary_shows_default_blocked_state(self) -> None:
        summary = app.live_policy_summary()

        self.assertIn("Active profile: development", summary)
        self.assertIn("Live trading enabled: False", summary)
        self.assertIn("Live Production Mode: False", summary)
        self.assertIn("Permission level: L0 RESEARCH", summary)

    def test_policy_profile_list_marks_active_profile(self) -> None:
        result = app.policy_profile_list()

        self.assertIn("* development", result)
        self.assertIn("- paper", result)

    def test_set_active_risk_policy_profile_persists_choice(self) -> None:
        result = app.set_active_risk_policy_profile("paper")

        self.assertEqual("Active risk policy profile set to: paper", result)
        self.assertEqual("paper", app.active_risk_policy_profile())
        self.assertIn("Active profile: paper", app.live_policy_summary())

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
