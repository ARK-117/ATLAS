from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping
from uuid import uuid4


class EventFamily(StrEnum):
    MARKET = "market"
    REFERENCE = "reference"
    FUNDAMENTAL = "fundamental"
    NEWS = "news"
    RESEARCH = "research"
    PORTFOLIO_EXECUTION = "portfolio_execution"
    RISK = "risk"
    GOVERNANCE = "governance"
    SYSTEM = "system"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CanonicalEvent:
    """Point-in-time event record shared by every ATLAS subsystem."""

    family: EventFamily
    event_type: str
    source: str
    subject: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)
    event_time: datetime = field(default_factory=utc_now)
    ingestion_time: datetime = field(default_factory=utc_now)
    source_event_id: str = ""
    lineage: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "atlas.canonical_event.v1"
    event_id: str = field(default_factory=lambda: str(uuid4()))
