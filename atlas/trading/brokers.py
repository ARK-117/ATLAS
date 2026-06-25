from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from .models import MarketSnapshot, OrderIntent, RiskCheckResult


@dataclass(frozen=True)
class BrokerExecutionResult:
    broker_order_id: str
    accepted: bool
    status: str
    message: str
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BrokerAdapter(Protocol):
    name: str

    def submit_order(
        self,
        intent: OrderIntent,
        market: MarketSnapshot,
        risk_result: RiskCheckResult,
    ) -> BrokerExecutionResult:
        ...


class SimulatedBrokerAdapter:
    """Internal broker simulator for execution-path testing."""

    name = "simulated"

    def submit_order(
        self,
        intent: OrderIntent,
        market: MarketSnapshot,
        risk_result: RiskCheckResult,
    ) -> BrokerExecutionResult:
        if not risk_result.approved:
            return BrokerExecutionResult(
                broker_order_id="",
                accepted=False,
                status="blocked",
                message="risk engine blocked the order intent",
            )

        return BrokerExecutionResult(
            broker_order_id=f"SIM-{uuid4()}",
            accepted=True,
            status="accepted",
            message=(
                f"simulated {intent.side.value} order accepted for "
                f"{intent.quantity:g} {intent.symbol.upper()} at reference price {market.price:.2f}"
            ),
        )


class LiveBrokerNotConfiguredAdapter:
    """Guard rail used until a real broker integration is explicitly built."""

    name = "live-not-configured"

    def submit_order(
        self,
        intent: OrderIntent,
        market: MarketSnapshot,
        risk_result: RiskCheckResult,
    ) -> BrokerExecutionResult:
        return BrokerExecutionResult(
            broker_order_id="",
            accepted=False,
            status="not_configured",
            message=(
                "live broker execution is not configured; build a broker-specific adapter "
                "with credential isolation, reconciliation, and production approval first"
            ),
        )

