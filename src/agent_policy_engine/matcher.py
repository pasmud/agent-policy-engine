"""Rule matching logic."""

from __future__ import annotations

import fnmatch
import re
from typing import Any

from .models import Rule, ToolCall


def _matches_pattern(pattern: str, value: str) -> bool:
    return fnmatch.fnmatchcase(value, pattern)


def _matches_any(patterns: tuple[str, ...], value: str) -> bool:
    return any(_matches_pattern(pattern, value) for pattern in patterns)


def _get_path(data: dict[str, Any], path: str) -> Any:
    """Resolve a dotted path, supporting dict keys and integer list indexes."""
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return _MISSING
            current = current[part]
        elif isinstance(current, list):
            if not part.isdigit():
                return _MISSING
            idx = int(part)
            if idx < 0 or idx >= len(current):
                return _MISSING
            current = current[idx]
        else:
            return _MISSING
    return current
