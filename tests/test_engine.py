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

    def test_allow_rule(self):
        decision = self.engine.evaluate(ToolCall.from_dict({"tool": "web.search"}))
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.matched_rule, "allow-read")

    def test_priority_overrides(self):
        decision = self.engine.evaluate(ToolCall.from_dict({"tool": "shell.exec", "agent": "admin"}))
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.matched_rule, "allow-shell-for-admin")

    def test_deny_reason(self):
        decision = self.engine.evaluate(ToolCall.from_dict({"tool": "shell.exec", "agent": "dev"}))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "Shell is blocked")
