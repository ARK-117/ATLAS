from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from atlas.trading import (
    Approval,
    JsonlAuditLogger,
    MarketSnapshot,
    OrderIntent,
    OrderSide,
    PortfolioState,
    RiskEngine,
    RiskPolicy,
    SimulatedBrokerAdapter,
    TradingGateway,
)


class RiskEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now(timezone.utc)
        self.intent = OrderIntent(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=5,
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
        self.assertIn("human approval is required", result.reasons)

    def test_live_order_requires_production_acknowledged_approval(self) -> None:
        policy = RiskPolicy(live_trading_enabled=True)
        approval = Approval(
            order_intent_id=self.intent.id,
            approved_by="human-operator",
            approved_at=self.now,
            expires_at=self.now + timedelta(minutes=2),
            production_acknowledged=False,
        )

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
        policy = RiskPolicy(live_trading_enabled=True)
        approval = Approval(
            order_intent_id=self.intent.id,
            approved_by="human-operator",
            approved_at=self.now,
            expires_at=self.now + timedelta(minutes=2),
            production_acknowledged=True,
        )

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
            created_by="operator",
        )
        policy = RiskPolicy(live_trading_enabled=True, max_order_notional=10_000.0)
        approval = Approval(
            order_intent_id=large_intent.id,
            approved_by="human-operator",
            approved_at=self.now,
            expires_at=self.now + timedelta(minutes=2),
            production_acknowledged=True,
        )

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

    def test_gateway_audits_before_broker_submission(self) -> None:
        policy = RiskPolicy(live_trading_enabled=True)
        approval = Approval(
            order_intent_id=self.intent.id,
            approved_by="human-operator",
            approved_at=self.now,
            expires_at=self.now + timedelta(minutes=2),
            production_acknowledged=True,
        )

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

