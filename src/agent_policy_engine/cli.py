"""Command-line interface for agent-policy-engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .audit import AuditLog
from .engine import PolicyEngine
from .models import ToolCall
from .policy_loader import PolicyLoadError, load_policy
from .report import decisions_to_report, render_report


def _load_json_file(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_calls(path: str | Path) -> list[ToolCall]:
    data = _load_json_file(path)
    if isinstance(data, dict) and "calls" in data:
        data = data["calls"]
    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("input must be a tool call object, a list, or {\"calls\": [...]}")
    return [ToolCall.from_dict(item) for item in items]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-policy-engine",
        description="Evaluate agent tool calls against allow/deny policies with audit output.",
    )
