from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import app
from atlas.trading import BrokerExecutionResult, MarketSnapshot, OrderIntent, OrderSide


class AppTradingCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.original_data_file = app.DATA_FILE
        self.original_audit_file = app.ORDER_INTENT_AUDIT_FILE
        app.DATA_FILE = str(self.temp_path / "atlas_data.json")
        app.ORDER_INTENT_AUDIT_FILE = str(self.temp_path / "order_intents.jsonl")

    def tearDown(self) -> None:
        app.DATA_FILE = self.original_data_file
        app.ORDER_INTENT_AUDIT_FILE = self.original_audit_file
        self.temp_dir.cleanup()

    def test_live_policy_summary_shows_default_blocked_state(self) -> None:
        summary = app.live_policy_summary()

        self.assertIn("Active profile: development", summary)
        self.assertIn("Kill switch active: False", summary)
        self.assertIn("Live trading enabled: False", summary)
        self.assertIn("Live Production Mode: False", summary)
        self.assertIn("Permission level: L0 RESEARCH", summary)

    def test_system_controls_default_to_inactive_kill_switch(self) -> None:
        summary = app.system_control_summary()

        self.assertIn("Kill switch: inactive", summary)
        self.assertIn("Reason: none", summary)

    def test_kill_switch_can_be_activated_and_cleared_with_confirmation(self) -> None:
        activation = app.activate_kill_switch("unit test stop")

        self.assertIn("Kill switch activated", activation)
        self.assertTrue(app.system_controls()["kill_switch_active"])
        self.assertIn("unit test stop", app.system_control_summary())
        self.assertTrue(Path(app.ORDER_INTENT_AUDIT_FILE).exists())

        blocked_clear = app.clear_kill_switch("YES")
        self.assertIn("Kill switch clear blocked", blocked_clear)
        self.assertTrue(app.system_controls()["kill_switch_active"])

        cleared = app.clear_kill_switch(app.KILL_SWITCH_CLEAR_CONFIRMATION)
        self.assertIn("Kill switch cleared", cleared)
        self.assertFalse(app.system_controls()["kill_switch_active"])

    def test_readiness_report_blocks_when_kill_switch_active(self) -> None:
        app.activate_kill_switch("unit test stop")

        report = app.production_readiness_report()

        self.assertIn("BLOCKED: kill switch inactive", report)
        self.assertIn("Result: production broker execution must remain blocked.", report)

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

    def test_create_order_intent_persists_record_after_risk_check(self) -> None:
        original_get_market_snapshot = app.get_market_snapshot
        app.get_market_snapshot = lambda ticker: MarketSnapshot(
            symbol=ticker,
            price=100.0,
            timestamp=datetime.now(timezone.utc),
            sector="technology",
            average_daily_dollar_volume=100_000_000.0,
            source="unit-test",
        )

        try:
            result = app.create_order_intent(
                side_text="buy",
                ticker="AAPL",
                quantity_text="1",
                stop_loss_text="90",
                max_loss_text="10",
                reason="unit test",
            )
        finally:
            app.get_market_snapshot = original_get_market_snapshot

        self.assertIn("ATLAS real-trading order intent risk check", result)
        self.assertIn("No live broker order was placed.", result)
        self.assertIn("AAPL", app.list_order_intents())

    def test_order_intent_can_be_stored_listed_shown_and_approved(self) -> None:
        intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=1,
            expected_max_loss=10.0,
            stop_loss_price=90.0,
            reason="unit test",
            data_sources_used=("unit-test",),
            created_by="test",
        )
        market = MarketSnapshot(
            symbol="AAPL",
            price=100.0,
            timestamp=datetime.now(timezone.utc),
            sector="technology",
            average_daily_dollar_volume=100_000_000.0,
            source="unit-test",
        )
        result = BrokerExecutionResult(
            broker_order_id="",
            accepted=False,
            status="blocked",
            message="human approval is required",
        )

        app.store_order_intent_record(intent, market, result)

        self.assertIn(intent.id, app.list_order_intents())
        shown = app.show_order_intent(intent.id)
        self.assertIn("Approval: none", shown)
        self.assertIn("human approval is required", shown)

        blocked = app.approve_order_intent(intent.id, "YES")
        self.assertIn("Approval blocked", blocked)

        approved = app.approve_order_intent(intent.id, app.APPROVAL_CONFIRMATION)
        self.assertIn("Approval recorded", approved)
        self.assertIn("Approval: recorded by local-cli", app.show_order_intent(intent.id))
        self.assertTrue(Path(app.ORDER_INTENT_AUDIT_FILE).exists())

    def test_recheck_order_intent_uses_stored_market_when_fresh_lookup_unavailable(self) -> None:
        intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=1,
            expected_max_loss=10.0,
            stop_loss_price=90.0,
            reason="unit test",
            data_sources_used=("unit-test",),
            created_by="test",
        )
        market = MarketSnapshot(
            symbol="AAPL",
            price=100.0,
            timestamp=datetime.now(timezone.utc),
            sector="technology",
            average_daily_dollar_volume=100_000_000.0,
            source="unit-test",
        )
        app.store_order_intent_record(
            intent,
            market,
            BrokerExecutionResult(
                broker_order_id="",
                accepted=False,
                status="blocked",
                message="human approval is required",
            ),
        )
        original_get_market_snapshot = app.get_market_snapshot
        app.get_market_snapshot = lambda ticker: None

        try:
            result = app.recheck_order_intent(intent.id)
        finally:
            app.get_market_snapshot = original_get_market_snapshot

        self.assertIn("ATLAS order intent recheck", result)
        self.assertIn("No live broker order was placed.", result)

    def test_kill_switch_blocks_order_intent_recheck(self) -> None:
        intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=1,
            expected_max_loss=10.0,
            stop_loss_price=90.0,
            reason="unit test",
            data_sources_used=("unit-test",),
            created_by="test",
        )
        market = MarketSnapshot(
            symbol="AAPL",
            price=100.0,
            timestamp=datetime.now(timezone.utc),
            sector="technology",
            average_daily_dollar_volume=100_000_000.0,
            source="unit-test",
        )
        app.store_order_intent_record(
            intent,
            market,
            BrokerExecutionResult(
                broker_order_id="",
                accepted=False,
                status="blocked",
                message="human approval is required",
            ),
        )
        app.activate_kill_switch("unit test stop")

        result = app.recheck_order_intent(intent.id)

        self.assertIn("kill switch is active", result)


if __name__ == "__main__":
    unittest.main()
