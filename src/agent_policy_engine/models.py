"""Core data models for policy evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return a deterministic-friendly UTC timestamp helper for runtime use."""
    return datetime.now(timezone.utc).isoformat()


def _normalize_str_list(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        raise ValueError(f"{field_name} must be a string or list of strings")
    normalized: list[str] = []
    for item in items:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        normalized.append(item.strip())
    return tuple(normalized)


@dataclass(frozen=True)
class ToolCall:
    """A tool invocation request made by an agent."""
