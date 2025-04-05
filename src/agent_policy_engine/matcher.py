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


class _MissingSentinel:
    pass


_MISSING = _MissingSentinel()


def _condition_matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if not expected:
            return actual == expected
        for op, operand in expected.items():
            if op == "eq":
                if actual != operand:
                    return False
            elif op == "neq":
                if actual == operand:
                    return False
            elif op == "in":
                if not isinstance(operand, list):
                    return False
                if actual not in operand:
                    return False
            elif op == "not_in":
                if not isinstance(operand, list):
                    return False
                if actual in operand:
                    return False
            elif op == "contains":
                if not isinstance(actual, (str, list, tuple, dict)):
                    return False
                if operand not in actual:
                    return False
            elif op == "startswith":
                if not isinstance(actual, str) or not isinstance(operand, str):
                    return False
                if not actual.startswith(operand):
                    return False
            elif op == "endswith":
                if not isinstance(actual, str) or not isinstance(operand, str):
                    return False
                if not actual.endswith(operand):
                    return False
            elif op == "regex":
                if not isinstance(actual, str) or not isinstance(operand, str):
                    return False
                if re.search(operand, actual) is None:
                    return False
            elif op == "gt":
                try:
                    if not actual > operand:
                        return False
                except Exception:
                    return False
            elif op == "gte":
                try:
                    if not actual >= operand:
                        return False
                except Exception:
                    return False
            elif op == "lt":
                try:
                    if not actual < operand:
                        return False
                except Exception:
                    return False
            elif op == "lte":
                try:
                    if not actual <= operand:
                        return False
                except Exception:
                    return False
            elif op == "exists":
                if not isinstance(operand, bool):
                    return False
                exists = actual is not _MISSING
                if exists != operand:
                    return False
            else:
                return False
        return True
    return actual == expected


def rule_matches(rule: Rule, call: ToolCall) -> bool:
    """Return True when the rule applies to the given tool call."""
    if not _matches_any(rule.tools, call.tool):
        return False
