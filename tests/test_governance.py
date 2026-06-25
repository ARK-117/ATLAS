from __future__ import annotations

import unittest

from atlas.trading import (
    ControlDomain,
    RiskPolicy,
    TradingPermissionLevel,
    evaluate_governance_controls,
)


class GovernanceTest(unittest.TestCase):
    def test_development_policy_is_not_production_ready(self) -> None:
        report = evaluate_governance_controls(
            RiskPolicy(),
            kill_switch_active=False,
        )

        self.assertFalse(report.ready)
        self.assertGreater(report.blocked_count, 0)
        names = {check.name for check in report.checks if not check.passed}
        self.assertIn("live trading enabled", names)
        self.assertIn("Live Production Mode active", names)

    def test_kill_switch_blocks_otherwise_ready_policy(self) -> None:
        report = evaluate_governance_controls(
            self.ready_l3_policy(),
            kill_switch_active=True,
            order_reconciliation_configured=True,
            market_data_recovery_configured=True,
        )

        self.assertFalse(report.ready)
        blocked = [check for check in report.checks if not check.passed]
        self.assertEqual(["kill switch inactive"], [check.name for check in blocked])

    def test_ready_l3_policy_passes_when_required_controls_exist(self) -> None:
        report = evaluate_governance_controls(
            self.ready_l3_policy(),
            kill_switch_active=False,
            order_reconciliation_configured=True,
            market_data_recovery_configured=True,
        )

        self.assertTrue(report.ready)
        self.assertEqual(0, report.blocked_count)

    def test_domain_summary_includes_core_control_domains(self) -> None:
        report = evaluate_governance_controls(
            RiskPolicy(),
            kill_switch_active=False,
        )
        domains = {domain for domain, _, _ in report.domain_summary()}

        self.assertIn(ControlDomain.EXPOSURE, domains)
        self.assertIn(ControlDomain.LIQUIDITY, domains)
        self.assertIn(ControlDomain.HUMAN_CONTROL, domains)
        self.assertIn(ControlDomain.LINEAGE, domains)

    @staticmethod
    def ready_l3_policy() -> RiskPolicy:
        return RiskPolicy(
            live_trading_enabled=True,
            live_production_mode=True,
            permission_level=TradingPermissionLevel.LIVE_CASH_EQUITIES,
            broker_connection_configured=True,
            separate_paper_and_live_keys=True,
            secure_secrets_management=True,
            user_authenticated=True,
            role_permission_granted=True,
            approval_workflow_enabled=True,
            emergency_kill_switch_available=True,
            broker_status_healthy=True,
            compliance_checks_passed=True,
            duplicate_order_check_passed=True,
            require_human_approval=True,
        )


if __name__ == "__main__":
    unittest.main()

