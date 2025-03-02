"""Policy evaluation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .audit import AuditLog
from .matcher import rule_matches
from .models import Decision, Policy, Rule, ToolCall


@dataclass(frozen=True)
class EvaluationResult:
    decision: Decision
    record: dict


class PolicyEngine:
    """Evaluate tool calls against a policy and record audit events."""

    def __init__(self, policy: Policy, audit_log: AuditLog | None = None) -> None:
        self.policy = policy
        self.audit_log = audit_log or AuditLog()
