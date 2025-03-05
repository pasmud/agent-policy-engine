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

    def evaluate(self, call: ToolCall) -> Decision:
        matched: list[Rule] = [rule for rule in self.policy.rules if rule_matches(rule, call)]
        matched_names = tuple(rule.name for rule in matched)

        if matched:
            # Highest priority wins; tie preserves document order by using stable sort.
            winner = sorted(matched, key=lambda r: r.priority, reverse=True)[0]
            allowed = winner.effect == "allow"
            reason = winner.reason or f"Matched rule '{winner.name}' ({winner.effect})"
            return Decision(
                allowed=allowed,
                effect=winner.effect,
                reason=reason,
                matched_rule=winner.name,
                matched_rules=matched_names,
                call=call,
            )

        allowed = self.policy.default_effect == "allow"
        reason = f"No rule matched; default effect is '{self.policy.default_effect}'"
        return Decision(
            allowed=allowed,
            effect=self.policy.default_effect,
            reason=reason,
            matched_rule=None,
            matched_rules=matched_names,
            call=call,
        )

    def check(self, call: ToolCall) -> Decision:
        """Evaluate and append to audit log."""
        decision = self.evaluate(call)
        self.audit_log.append(decision)
        return decision

    def evaluate_many(self, calls: Iterable[ToolCall]) -> list[Decision]:
        return [self.evaluate(call) for call in calls]
