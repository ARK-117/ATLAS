from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from atlas.trading import (
    Approval,
    AssetClass,
    JsonlAuditLogger,
    MarketSnapshot,
    OrderIntent,
    OrderSide,
    OrderType,
    PortfolioState,
    RiskEngine,
    RiskPolicy,
    SimulatedBrokerAdapter,
    TradingGateway,
    TradingPermissionLevel,
)


class RiskEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now(timezone.utc)
        self.intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=5,
            expected_max_loss=50.0,
            stop_loss_price=90.0,
            reason="unit test cash equity trade",
            data_sources_used=("unit-test-market-data",),
            created_by="operator",
            strategy_id="manual-test",
        )
        self.market = MarketSnapshot(
            symbol="AAPL",
            price=100.0,
            timestamp=self.now,
            sector="technology",
            bid_ask_spread_percent=0.001,
            average_daily_dollar_volume=100_000_000.0,
            volatility_percent=0.02,
            source="unit-test",
        )
        self.portfolio = PortfolioState(
            account_id="acct-test",
            equity=100_000.0,
            cash=50_000.0,
            peak_equity=100_000.0,
        )

    def live_policy(self, **overrides: object) -> RiskPolicy:
        values = {
            "live_trading_enabled": True,
            "live_production_mode": True,
            "permission_level": TradingPermissionLevel.LIVE_CASH_EQUITIES,
            "broker_connection_configured": True,
            "separate_paper_and_live_keys": True,
            "secure_secrets_management": True,
            "user_authenticated": True,
            "role_permission_granted": True,
            "approval_workflow_enabled": True,
            "emergency_kill_switch_available": True,
            "broker_status_healthy": True,
            "compliance_checks_passed": True,
        }
        values.update(overrides)
        return RiskPolicy(**values)

    def approval_for(self, intent: OrderIntent, acknowledged: bool = True) -> Approval:
        return Approval(
            order_intent_id=intent.id,
            approved_by="human-operator",
            approved_at=self.now,
            expires_at=self.now + timedelta(minutes=2),
            production_acknowledged=acknowledged,
        )

    def test_live_order_is_blocked_by_default(self) -> None:
        result = RiskEngine().evaluate(
            intent=self.intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=RiskPolicy(),
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("live trading is not enabled in risk policy", result.reasons)
        self.assertIn("live production mode is not active", result.reasons)
        self.assertIn("permission level is below live cash equities", result.reasons)
        self.assertIn("human approval is required", result.reasons)

    def test_live_order_requires_production_acknowledged_approval(self) -> None:
        policy = self.live_policy()
        approval = self.approval_for(self.intent, acknowledged=False)

        result = RiskEngine().evaluate(
            intent=self.intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=policy,
            approval=approval,
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("production approval acknowledgement is required", result.reasons)

    def test_valid_live_order_can_pass_pre_trade_checks(self) -> None:
        policy = self.live_policy()
        approval = self.approval_for(self.intent)

        result = RiskEngine().evaluate(
            intent=self.intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=policy,
            approval=approval,
            now=self.now,
        )

        self.assertTrue(result.approved)
        self.assertEqual(500.0, result.order_notional)

    def test_risk_limits_block_large_order(self) -> None:
        large_intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=2_000,
            expected_max_loss=5_000.0,
            stop_loss_price=95.0,
            reason="unit test large trade",
            data_sources_used=("unit-test-market-data",),
            created_by="operator",
        )
        policy = self.live_policy(max_order_notional=10_000.0)
        approval = self.approval_for(large_intent)

        result = RiskEngine().evaluate(
            intent=large_intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=policy,
            approval=approval,
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("order notional exceeds max order limit", result.reasons)
        self.assertIn("single-asset exposure would exceed limit", result.reasons)

    def test_missing_live_order_fields_are_blocked(self) -> None:
        incomplete_intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=5,
            created_by="operator",
        )

        result = RiskEngine().evaluate(
            intent=incomplete_intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=self.live_policy(),
            approval=self.approval_for(incomplete_intent),
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("expected maximum loss is required", result.reasons)
        self.assertIn("stop-loss or invalidation condition is required", result.reasons)
        self.assertIn("reason for trade is required", result.reasons)
        self.assertIn("data sources used are required", result.reasons)

    def test_options_require_options_permission_level_and_module(self) -> None:
        option_intent = OrderIntent(
            symbol="AAPL260116C00100000",
            side=OrderSide.BUY,
            quantity=1,
            asset_class=AssetClass.OPTION,
            expected_max_loss=250.0,
            invalidation_condition="option thesis invalidated",
            reason="unit test option trade",
            data_sources_used=("unit-test-options-chain",),
        )
        option_market = MarketSnapshot(
            symbol=option_intent.symbol,
            price=2.50,
            timestamp=self.now,
            sector="technology",
            asset_class=AssetClass.OPTION,
            bid_ask_spread_percent=0.001,
            average_daily_dollar_volume=100_000_000.0,
            volatility_percent=0.02,
            source="unit-test",
        )
        policy = self.live_policy(
            allowed_asset_classes=(AssetClass.EQUITY, AssetClass.ETF, AssetClass.OPTION)
        )

        result = RiskEngine().evaluate(
            intent=option_intent,
            portfolio=self.portfolio,
            market=option_market,
            policy=policy,
            approval=self.approval_for(option_intent),
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("options trading is not enabled", result.reasons)
        self.assertIn("permission level is below required live_options", result.reasons)

    def test_short_sale_requires_margin_and_short_permission_level(self) -> None:
        short_intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=5,
            expected_max_loss=100.0,
            stop_loss_price=110.0,
            reason="unit test short sale",
            data_sources_used=("unit-test-market-data",),
        )
        policy = self.live_policy(allow_short_selling=True)

        result = RiskEngine().evaluate(
            intent=short_intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=policy,
            approval=self.approval_for(short_intent),
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("permission level is below live margin and short selling", result.reasons)

    def test_complex_orders_require_complex_order_permission_level(self) -> None:
        bracket_intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=5,
            order_type=OrderType.BRACKET,
            expected_max_loss=50.0,
            stop_loss_price=90.0,
            reason="unit test bracket order",
            data_sources_used=("unit-test-market-data",),
        )
        policy = self.live_policy()

        result = RiskEngine().evaluate(
            intent=bracket_intent,
            portfolio=self.portfolio,
            market=self.market,
            policy=policy,
            approval=self.approval_for(bracket_intent),
            now=self.now,
        )

        self.assertFalse(result.approved)
        self.assertIn("complex order types are not enabled", result.reasons)
        self.assertIn("permission level is below complex orders", result.reasons)

    def test_gateway_audits_before_broker_submission(self) -> None:
        policy = self.live_policy()
        approval = self.approval_for(self.intent)

        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            gateway = TradingGateway(
                risk_engine=RiskEngine(),
                broker=SimulatedBrokerAdapter(),
                audit_logger=JsonlAuditLogger(audit_path),
            )

            result = gateway.submit_intent(
                intent=self.intent,
                portfolio=self.portfolio,
                market=self.market,
                policy=policy,
                approval=approval,
                now=self.now,
            )

            self.assertTrue(result.accepted)
            audit_lines = audit_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(audit_lines))
            self.assertIn("order_intent_risk_checked", audit_lines[0])
            self.assertIn("broker_submission_result", audit_lines[1])


if __name__ == "__main__":
    unittest.main()
