from __future__ import annotations

import json
from dataclasses import asdict, fields
from enum import Enum
from pathlib import Path
from typing import Any

from .models import AssetClass, RiskPolicy, TradingPermissionLevel


class RiskPolicyConfigError(ValueError):
    """Raised when a risk policy profile cannot be loaded safely."""


def default_policy_profiles_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "risk_profiles"


def list_risk_policy_profiles(profile_dir: str | Path | None = None) -> tuple[str, ...]:
    directory = Path(profile_dir) if profile_dir is not None else default_policy_profiles_dir()
    if not directory.exists():
        return ()

    return tuple(sorted(path.stem for path in directory.glob("*.json")))


def load_risk_policy_profile(
    profile_name: str,
    profile_dir: str | Path | None = None,
) -> RiskPolicy:
    directory = Path(profile_dir) if profile_dir is not None else default_policy_profiles_dir()
    profile_path = directory / f"{profile_name}.json"

    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise RiskPolicyConfigError(f"risk policy profile not found: {profile_name}") from error
    except json.JSONDecodeError as error:
        raise RiskPolicyConfigError(f"invalid JSON in risk policy profile: {profile_name}") from error

    if not isinstance(raw, dict):
        raise RiskPolicyConfigError("risk policy profile must be a JSON object")

    return risk_policy_from_dict(raw)


def risk_policy_from_dict(raw: dict[str, Any]) -> RiskPolicy:
    allowed_fields = {field.name for field in fields(RiskPolicy)}
    unknown_fields = sorted(set(raw) - allowed_fields - {"profile_name", "description"})
    if unknown_fields:
        raise RiskPolicyConfigError(
            "unknown risk policy fields: " + ", ".join(unknown_fields)
        )

    values = {key: value for key, value in raw.items() if key in allowed_fields}

    try:
        if "permission_level" in values:
            values["permission_level"] = _parse_permission_level(values["permission_level"])

        if "allowed_asset_classes" in values:
            values["allowed_asset_classes"] = tuple(
                _parse_asset_class(value) for value in values["allowed_asset_classes"]
            )
    except (KeyError, ValueError) as error:
        raise RiskPolicyConfigError(f"invalid risk policy value: {error}") from error

    return RiskPolicy(**values)


def risk_policy_to_dict(policy: RiskPolicy) -> dict[str, Any]:
    return _plain(asdict(policy))


def _parse_permission_level(value: Any) -> TradingPermissionLevel:
    if isinstance(value, int):
        return TradingPermissionLevel(value)

    if isinstance(value, str):
        cleaned = value.upper()
        if cleaned.startswith("L") and cleaned[1:].isdigit():
            return TradingPermissionLevel(int(cleaned[1:]))
        if cleaned.isdigit():
            return TradingPermissionLevel(int(cleaned))
        return TradingPermissionLevel[cleaned]

    raise RiskPolicyConfigError("permission_level must be an integer or string")


def _parse_asset_class(value: Any) -> AssetClass:
    if isinstance(value, AssetClass):
        return value
    if isinstance(value, str):
        return AssetClass(value.lower())
    raise RiskPolicyConfigError("asset class values must be strings")


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value
