from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .models import CanonicalEvent, EventFamily


class EventStoreError(RuntimeError):
    """Raised when canonical events cannot be read or written durably."""


class JsonlEventStore:
    """Append-only JSONL storage for canonical ATLAS events."""

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = Path(path)

    def append(self, event: CanonicalEvent) -> str:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(event_to_dict(event), sort_keys=True) + "\n")
        except OSError as error:
            raise EventStoreError(f"failed to write canonical event: {error}") from error

        return event.event_id

    def read_all(self) -> list[CanonicalEvent]:
        if not self.path.exists():
            return []

        events: list[CanonicalEvent] = []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(event_from_dict(json.loads(line)))
                    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                        raise EventStoreError(
                            f"failed to parse canonical event on line {line_number}: {error}"
                        ) from error
        except OSError as error:
            raise EventStoreError(f"failed to read canonical events: {error}") from error

        return events

    def latest(self, limit: int = 10) -> list[CanonicalEvent]:
        if limit <= 0:
            return []
        return list(reversed(self.read_all()[-limit:]))

    def count(self) -> int:
        return len(self.read_all())


def event_to_dict(event: CanonicalEvent) -> dict[str, Any]:
    return _sanitize(_to_plain(event))


def event_from_dict(raw: dict[str, Any]) -> CanonicalEvent:
    return CanonicalEvent(
        family=EventFamily(raw["family"]),
        event_type=raw["event_type"],
        source=raw["source"],
        subject=raw.get("subject", ""),
        payload=raw.get("payload", {}),
        event_time=_parse_datetime(raw["event_time"]),
        ingestion_time=_parse_datetime(raw["ingestion_time"]),
        source_event_id=raw.get("source_event_id", ""),
        lineage=raw.get("lineage", {}),
        schema_version=raw.get("schema_version", "atlas.canonical_event.v1"),
        event_id=raw["event_id"],
    )


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return _to_plain(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain(item) for item in value]
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
