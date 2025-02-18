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
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Evaluate tool calls against a policy")
    check.add_argument("--policy", required=True, help="Path to policy JSON file")
    check.add_argument("--input", required=True, help="Path to tool call JSON file")
    check.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    check.add_argument("--audit-out", help="Write audit records as JSONL to this path")
    check.add_argument(
        "--fail-on-deny",
        action="store_true",
        help="Exit with code 2 if any call is denied",
    )

    return parser


def cmd_check(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    calls = _load_calls(args.input)
    audit_log = AuditLog()
    engine = PolicyEngine(policy, audit_log=audit_log)
    decisions = engine.check_many(calls)
    report = decisions_to_report(decisions)
    report["policy"] = {
        "version": policy.version,
        "default_effect": policy.default_effect,
        "rules": len(policy.rules),
        "path": str(Path(args.policy)),
    }
    if args.audit_out:
        audit_log.write_jsonl(args.audit_out)
        report["audit_out"] = str(Path(args.audit_out))
    sys.stdout.write(render_report(report, args.format) + "\n")
    if args.fail_on_deny and report["summary"]["denied"] > 0:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            return cmd_check(args)
        parser.error(f"unknown command: {args.command}")
        return 2  # pragma: no cover
    except (PolicyLoadError, ValueError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
