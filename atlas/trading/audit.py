from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class AuditLogError(RuntimeError):
    """Raised when an audit event cannot be durably written."""


class JsonlAuditLogger:
    """Append-only JSONL audit log for sensitive trading events."""

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = Path(path)

    def append(self, event_type: str, payload: MappingLike) -> str:
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": _sanitize(_to_plain(payload)),
        }

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(event, sort_keys=True) + "\n")
        except OSError as error:
            raise AuditLogError(f"failed to write audit event: {error}") from error

        return event_id


MappingLike = dict[str, Any] | Any


def _to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _sanitize(value: Any) -> Any:
    secret_keys = {
        "api_key",
        "api_secret",
        "secret",
        "token",
        "password",
        "broker_credentials",
    }

    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if str(key).lower() in secret_keys:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = _sanitize(item)
        return sanitized

    if isinstance(value, list):
        return [_sanitize(item) for item in value]

    return value

