from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from .audit import JsonlAuditLogger
from .brokers import BrokerAdapter, BrokerExecutionResult
from .models import Approval, MarketSnapshot, OrderIntent, PortfolioState, RiskPolicy
from .risk import RiskEngine


class TradingGateway:
    """Coordinates order-intent evaluation, audit logging, and broker submission."""

    def __init__(
        self,
        risk_engine: RiskEngine,
        broker: BrokerAdapter,
        audit_logger: JsonlAuditLogger,
    ) -> None:
        self.risk_engine = risk_engine
        self.broker = broker
        self.audit_logger = audit_logger

    def submit_intent(
        self,
        intent: OrderIntent,
        portfolio: PortfolioState,
        market: MarketSnapshot,
        policy: RiskPolicy,
        approval: Approval | None = None,
        now: datetime | None = None,
    ) -> BrokerExecutionResult:
        risk_result = self.risk_engine.evaluate(
            intent=intent,
            portfolio=portfolio,
            market=market,
            policy=policy,
            approval=approval,
            now=now,
        )

        self.audit_logger.append(
            "order_intent_risk_checked",
            {
                "intent": asdict(intent),
                "portfolio_account_id": portfolio.account_id,
                "market": asdict(market),
                "policy": asdict(policy),
                "approval": asdict(approval) if approval else None,
                "risk_result": asdict(risk_result),
            },
        )

        if not risk_result.approved:
            return BrokerExecutionResult(
                broker_order_id="",
                accepted=False,
                status="blocked",
                message="; ".join(risk_result.reasons),
            )

        execution_result = self.broker.submit_order(intent, market, risk_result)
        self.audit_logger.append(
            "broker_submission_result",
            {
                "intent_id": intent.id,
                "broker": self.broker.name,
                "result": asdict(execution_result),
            },
        )
        return execution_result

