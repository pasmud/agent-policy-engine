"""Audit log for policy decisions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Decision


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AuditRecord:
    timestamp: str
    decision: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"timestamp": self.timestamp, "decision": self.decision}


@dataclass
class AuditLog:
    """In-memory audit log with optional JSON serialization."""

    records: list[AuditRecord] = field(default_factory=list)

    def append(self, decision: Decision, timestamp: str | None = None) -> AuditRecord:
        record = AuditRecord(timestamp=timestamp or _timestamp(), decision=decision.to_dict())
        self.records.append(record)
        return record

    def extend(self, decisions: list[Decision], timestamp: str | None = None) -> list[AuditRecord]:
        ts = timestamp or _timestamp()
        return [self.append(decision, timestamp=ts) for decision in decisions]

    def to_dicts(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self.records]

    def clear(self) -> None:
        self.records.clear()

    def write_jsonl(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as fh:
            for record in self.records:
                fh.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "AuditLog":
        target = Path(path)
        records: list[AuditRecord] = []
        for line in target.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError("audit record must be an object")
            ts = payload.get("timestamp")
            decision = payload.get("decision")
            if not isinstance(ts, str) or not isinstance(decision, dict):
                raise ValueError("audit record requires string timestamp and object decision")
            records.append(AuditRecord(timestamp=ts, decision=decision))
        return cls(records=records)
