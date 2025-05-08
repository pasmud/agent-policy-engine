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

    tool: str
    agent: str = "default"
    action: str = "call"
    arguments: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    call_id: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "ToolCall":
        if not isinstance(data, dict):
            raise ValueError("tool call must be an object")
        tool = data.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError("tool call 'tool' must be a non-empty string")
        agent = data.get("agent", "default")
        action = data.get("action", "call")
        call_id = data.get("call_id", "")
        if not isinstance(agent, str) or not agent.strip():
            raise ValueError("tool call 'agent' must be a non-empty string")
        if not isinstance(action, str) or not action.strip():
            raise ValueError("tool call 'action' must be a non-empty string")
        if not isinstance(call_id, str):
            raise ValueError("tool call 'call_id' must be a string")
        arguments = data.get("arguments", {})
        context = data.get("context", {})
        if not isinstance(arguments, dict):
            raise ValueError("tool call 'arguments' must be an object")
        if not isinstance(context, dict):
            raise ValueError("tool call 'context' must be an object")
        return cls(
            tool=tool.strip(),
            agent=agent.strip(),
            action=action.strip(),
            arguments=dict(arguments),
            context=dict(context),
            call_id=call_id.strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "agent": self.agent,
            "action": self.action,
            "arguments": dict(self.arguments),
            "context": dict(self.context),
            "call_id": self.call_id,
        }


@dataclass(frozen=True)
class Rule:
    """A single allow/deny rule."""

    name: str
