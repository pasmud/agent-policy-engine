import unittest

from agent_policy_engine.audit import AuditLog
from agent_policy_engine.engine import PolicyEngine
from agent_policy_engine.models import Policy, ToolCall


class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.policy = Policy.from_dict(
            {
                "version": "1",
                "default_effect": "deny",
                "rules": [
                    {
                        "name": "allow-read",
                        "effect": "allow",
                        "tools": ["fs.read", "web.search"],
                    },
                    {
                        "name": "deny-shell",
                        "effect": "deny",
                        "tools": ["shell.*"],
                        "priority": 10,
                        "reason": "Shell is blocked",
                    },
                    {
                        "name": "allow-shell-for-admin",
                        "effect": "allow",
                        "tools": ["shell.exec"],
                        "agents": ["admin"],
                        "priority": 20,
                    },
                ],
            }
        )
        self.engine = PolicyEngine(self.policy, audit_log=AuditLog())

    def test_default_deny(self):
        decision = self.engine.evaluate(ToolCall.from_dict({"tool": "unknown.tool"}))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.effect, "deny")
        self.assertIsNone(decision.matched_rule)
