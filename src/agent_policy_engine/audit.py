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
