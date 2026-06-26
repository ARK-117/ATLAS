from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from atlas.events import CanonicalEvent, EventFamily, JsonlEventStore


class JsonlEventStoreTest(unittest.TestCase):
    def test_empty_store_has_no_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonlEventStore(Path(temp_dir) / "events.jsonl")

            self.assertEqual(0, store.count())
            self.assertEqual([], store.read_all())
            self.assertEqual([], store.latest())

    def test_append_read_count_and_latest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonlEventStore(Path(temp_dir) / "events.jsonl")
            first = CanonicalEvent(
                family=EventFamily.RISK,
                event_type="risk_checked",
                source="unit-test",
                subject="intent-1",
                payload={"status": "blocked"},
                event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            )
            second = CanonicalEvent(
                family=EventFamily.GOVERNANCE,
                event_type="approval_recorded",
                source="unit-test",
                subject="intent-1",
                payload={"approved": True},
                event_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
            )

            self.assertEqual(first.event_id, store.append(first))
            self.assertEqual(second.event_id, store.append(second))

            events = store.read_all()
            self.assertEqual(2, store.count())
            self.assertEqual([first.event_id, second.event_id], [event.event_id for event in events])
            self.assertEqual(EventFamily.RISK, events[0].family)
            self.assertEqual("blocked", events[0].payload["status"])
            self.assertEqual([second.event_id], [event.event_id for event in store.latest(1)])

    def test_secret_like_payload_keys_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonlEventStore(Path(temp_dir) / "events.jsonl")
            event = CanonicalEvent(
                family=EventFamily.SYSTEM,
                event_type="secret_test",
                source="unit-test",
                payload={
                    "api_key": "do-not-store",
                    "nested": {"token": "do-not-store"},
                },
            )

            store.append(event)

            loaded = store.read_all()[0]
            self.assertEqual("[REDACTED]", loaded.payload["api_key"])
            self.assertEqual("[REDACTED]", loaded.payload["nested"]["token"])


if __name__ == "__main__":
    unittest.main()
