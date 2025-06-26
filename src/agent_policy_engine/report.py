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


def render_report(report: dict[str, Any], fmt: str) -> str:
    fmt_norm = fmt.lower()
    if fmt_norm == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if fmt_norm == "text":
        lines = [
            f"total={report['summary']['total']} allowed={report['summary']['allowed']} denied={report['summary']['denied']}"
        ]
        for idx, decision in enumerate(report.get("decisions", []), start=1):
            call = decision.get("call", {})
            tool = call.get("tool", "?")
            agent = call.get("agent", "?")
            effect = decision.get("effect", "?")
            matched = decision.get("matched_rule") or "<default>"
            reason = decision.get("reason", "")
            lines.append(
                f"{idx}. {effect.upper():5} tool={tool} agent={agent} rule={matched} reason={reason}"
            )
        return "\n".join(lines)
    raise ValueError(f"unsupported format: {fmt}")
