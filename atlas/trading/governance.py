from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import RiskPolicy, TradingPermissionLevel


class ControlDomain(StrEnum):
    EXPOSURE = "exposure"
    CONCENTRATION = "concentration"
    ORDER_SANITY = "order_sanity"
    LIQUIDITY = "liquidity"
    CREDIT_CASH = "credit_cash"
    LOSS_CONTROLS = "loss_controls"
    KILL_SWITCH = "kill_switch"
    HUMAN_CONTROL = "human_control"
    RECONCILIATION = "reconciliation"
    LINEAGE = "lineage"
    EXECUTION_ISOLATION = "execution_isolation"
    SECURITY = "security"
    RESILIENCE = "resilience"


@dataclass(frozen=True)
class GovernanceCheck:
    domain: ControlDomain
    name: str
    passed: bool
    detail: str
    required: bool = True


@dataclass(frozen=True)
class GovernanceReport:
    checks: tuple[GovernanceCheck, ...]

    @property
    def ready(self) -> bool:
        return all(check.passed for check in self.checks if check.required)

    @property
    def blocked_count(self) -> int:
        return sum(1 for check in self.checks if check.required and not check.passed)

    def domain_summary(self) -> tuple[tuple[ControlDomain, int, int], ...]:
        domains = []
        for domain in ControlDomain:
            domain_checks = [check for check in self.checks if check.domain == domain]
            if not domain_checks:
                continue
            passed = sum(1 for check in domain_checks if check.passed)
            domains.append((domain, passed, len(domain_checks)))
        return tuple(domains)


def evaluate_governance_controls(
    policy: RiskPolicy,
    *,
    kill_switch_active: bool,
    audit_log_configured: bool = True,
    order_reconciliation_configured: bool = False,
    market_data_recovery_configured: bool = False,
) -> GovernanceReport:
    checks = [
        GovernanceCheck(
            ControlDomain.KILL_SWITCH,
            "kill switch inactive",
            not kill_switch_active,
            "global kill switch must be inactive before broker routing",
        ),
        GovernanceCheck(
            ControlDomain.KILL_SWITCH,
            "emergency kill switch available",
            policy.emergency_kill_switch_available,
            "policy must confirm an emergency kill switch exists",
        ),
        GovernanceCheck(
            ControlDomain.EXECUTION_ISOLATION,
            "live trading enabled",
            policy.live_trading_enabled,
            "live trading flag must be explicitly enabled",
        ),
        GovernanceCheck(
            ControlDomain.EXECUTION_ISOLATION,
            "Live Production Mode active",
            policy.live_production_mode,
            "production mode must be active before live order intents route",
        ),
        GovernanceCheck(
            ControlDomain.EXECUTION_ISOLATION,
            "broker connection configured",
            policy.broker_connection_configured,
            "execution gateway must have an approved broker adapter",
        ),
        GovernanceCheck(
            ControlDomain.EXECUTION_ISOLATION,
            "broker status healthy",
            policy.broker_status_healthy,
            "broker/API status must be healthy before routing",
        ),
        GovernanceCheck(
            ControlDomain.SECURITY,
            "separate paper/live keys confirmed",
            policy.separate_paper_and_live_keys,
            "paper and live credentials must be separate",
        ),
        GovernanceCheck(
            ControlDomain.SECURITY,
            "secure secrets management confirmed",
            policy.secure_secrets_management,
            "credentials must be loaded through approved secret storage",
        ),
        GovernanceCheck(
            ControlDomain.SECURITY,
            "user authenticated",
            policy.user_authenticated,
            "operator identity must be authenticated",
        ),
        GovernanceCheck(
            ControlDomain.SECURITY,
            "role permission granted",
            policy.role_permission_granted,
            "operator role must allow the requested trading level",
        ),
        GovernanceCheck(
            ControlDomain.ORDER_SANITY,
            "duplicate-order check passed",
            policy.duplicate_order_check_passed,
            "duplicate order protection must pass",
        ),
        GovernanceCheck(
            ControlDomain.ORDER_SANITY,
            "compliance checks passed",
            policy.compliance_checks_passed,
            "compliance gate must pass before routing",
        ),
        GovernanceCheck(
            ControlDomain.EXPOSURE,
            "single-asset exposure limit configured",
            0 < policy.max_single_asset_exposure_percent <= 1,
            f"configured value {policy.max_single_asset_exposure_percent}",
        ),
        GovernanceCheck(
            ControlDomain.EXPOSURE,
            "sector exposure limit configured",
            0 < policy.max_sector_exposure_percent <= 1,
            f"configured value {policy.max_sector_exposure_percent}",
        ),
        GovernanceCheck(
            ControlDomain.EXPOSURE,
            "gross exposure limit configured",
            0 < policy.max_gross_exposure_percent <= 2,
            f"configured value {policy.max_gross_exposure_percent}",
        ),
        GovernanceCheck(
            ControlDomain.CONCENTRATION,
            "ADV participation limit configured",
            0 < policy.max_adv_participation_percent <= 0.1,
            f"configured value {policy.max_adv_participation_percent}",
        ),
        GovernanceCheck(
            ControlDomain.LIQUIDITY,
            "minimum dollar volume configured",
            policy.min_average_daily_dollar_volume > 0,
            f"configured value {policy.min_average_daily_dollar_volume}",
        ),
        GovernanceCheck(
            ControlDomain.LIQUIDITY,
            "spread limit configured",
            0 < policy.max_bid_ask_spread_percent <= 0.05,
            f"configured value {policy.max_bid_ask_spread_percent}",
        ),
        GovernanceCheck(
            ControlDomain.LIQUIDITY,
            "market data freshness limit configured",
            0 < policy.max_market_data_age_seconds <= 300,
            f"configured value {policy.max_market_data_age_seconds} seconds",
        ),
        GovernanceCheck(
            ControlDomain.LOSS_CONTROLS,
            "daily loss limit configured",
            0 < policy.max_daily_loss_percent <= 0.2,
            f"configured value {policy.max_daily_loss_percent}",
        ),
        GovernanceCheck(
            ControlDomain.LOSS_CONTROLS,
            "weekly loss limit configured",
            0 < policy.max_weekly_loss_percent <= 0.3,
            f"configured value {policy.max_weekly_loss_percent}",
        ),
        GovernanceCheck(
            ControlDomain.LOSS_CONTROLS,
            "drawdown limit configured",
            0 < policy.max_drawdown_percent <= 0.5,
            f"configured value {policy.max_drawdown_percent}",
        ),
        GovernanceCheck(
            ControlDomain.HUMAN_CONTROL,
            "human approval required",
            policy.require_human_approval,
            "supervised mode requires approval before live routing",
        ),
        GovernanceCheck(
            ControlDomain.HUMAN_CONTROL,
            "approval workflow enabled",
            policy.approval_workflow_enabled,
            "approval service must be active before live routing",
        ),
        GovernanceCheck(
            ControlDomain.CREDIT_CASH,
            "margin gated by permission level",
            not policy.allow_margin
            or policy.permission_level >= TradingPermissionLevel.LIVE_MARGIN_AND_SHORT,
            "margin requires L4 or higher",
        ),
        GovernanceCheck(
            ControlDomain.CREDIT_CASH,
            "short selling gated by permission level",
            not policy.allow_short_selling
            or policy.permission_level >= TradingPermissionLevel.LIVE_MARGIN_AND_SHORT,
            "short selling requires L4 or higher",
        ),
        GovernanceCheck(
            ControlDomain.CREDIT_CASH,
            "leverage capped",
            1.0 <= policy.max_leverage_multiplier <= 2.0,
            f"configured value {policy.max_leverage_multiplier}",
        ),
        GovernanceCheck(
            ControlDomain.LINEAGE,
            "audit log configured",
            audit_log_configured,
            "order intents, approvals, risk checks, and broker results must be auditable",
        ),
        GovernanceCheck(
            ControlDomain.RECONCILIATION,
            "order reconciliation configured",
            order_reconciliation_configured,
            "OMS/broker/custodian reconciliation must exist before live broker routing",
        ),
        GovernanceCheck(
            ControlDomain.RESILIENCE,
            "market data recovery configured",
            market_data_recovery_configured,
            "feed recovery/replay must exist before production broker routing",
        ),
    ]

    return GovernanceReport(tuple(checks))

