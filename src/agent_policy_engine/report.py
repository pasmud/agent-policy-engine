"""Report rendering helpers for CLI output."""

from __future__ import annotations

import json
from typing import Any

from .models import Decision


def decisions_to_report(decisions: list[Decision]) -> dict[str, Any]:
    allowed = sum(1 for d in decisions if d.allowed)
    denied = len(decisions) - allowed
    return {
        "summary": {
            "total": len(decisions),
            "allowed": allowed,
            "denied": denied,
        },
        "decisions": [d.to_dict() for d in decisions],
    }
