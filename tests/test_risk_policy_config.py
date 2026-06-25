from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atlas.trading import (
    RiskPolicyConfigError,
    TradingPermissionLevel,
    list_risk_policy_profiles,
    load_risk_policy_profile,
    risk_policy_to_dict,
)
from atlas.trading.config import risk_policy_from_dict


class RiskPolicyConfigTest(unittest.TestCase):
    def test_development_profile_blocks_live_trading(self) -> None:
        policy = load_risk_policy_profile("development")

        self.assertFalse(policy.live_trading_enabled)
        self.assertFalse(policy.live_production_mode)
        self.assertEqual(TradingPermissionLevel.RESEARCH, policy.permission_level)

    def test_live_template_is_l3_but_not_enabled(self) -> None:
        policy = load_risk_policy_profile("live_cash_equities.template")

        self.assertEqual(
            TradingPermissionLevel.LIVE_CASH_EQUITIES,
            policy.permission_level,
        )
        self.assertFalse(policy.live_trading_enabled)
        self.assertFalse(policy.live_production_mode)

    def test_profiles_are_listed_by_filename(self) -> None:
        profiles = list_risk_policy_profiles()

        self.assertIn("development", profiles)
        self.assertIn("paper", profiles)
        self.assertIn("live_cash_equities.template", profiles)

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaises(RiskPolicyConfigError):
            risk_policy_from_dict({"unknown": True})

    def test_invalid_permission_level_is_rejected(self) -> None:
        with self.assertRaises(RiskPolicyConfigError):
            risk_policy_from_dict({"permission_level": "LIVE_UNKNOWN_MODE"})

    def test_missing_profile_is_rejected(self) -> None:
        with self.assertRaises(RiskPolicyConfigError):
            load_risk_policy_profile("missing-profile")

    def test_profile_can_round_trip_to_plain_dict(self) -> None:
        policy = load_risk_policy_profile("paper")
        plain = risk_policy_to_dict(policy)

        self.assertEqual("PAPER_TRADING", plain["permission_level"])
        self.assertEqual(["EQUITY", "ETF"], plain["allowed_asset_classes"])

    def test_invalid_json_profile_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "broken.json").write_text("{", encoding="utf-8")

            with self.assertRaises(RiskPolicyConfigError):
                load_risk_policy_profile("broken", profile_dir=directory)


if __name__ == "__main__":
    unittest.main()
