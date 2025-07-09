import json
import tempfile
import unittest
from pathlib import Path

from agent_policy_engine.audit import AuditLog
from agent_policy_engine.models import Decision, ToolCall


class TestAuditLog(unittest.TestCase):
    def _decision(self, allowed=True):
        call = ToolCall.from_dict({"tool": "t", "agent": "a"})
        return Decision(
            allowed=allowed,
            effect="allow" if allowed else "deny",
            reason="r",
            matched_rule="rule1" if allowed else None,
            matched_rules=("rule1",) if allowed else (),
            call=call,
        )
