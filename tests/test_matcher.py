import unittest

from agent_policy_engine.matcher import rule_matches
from agent_policy_engine.models import Rule, ToolCall


class TestMatcher(unittest.TestCase):
    def test_matches_wildcards(self):
        rule = Rule.from_dict({"name": "r", "effect": "allow", "tools": ["fs.*"]}, 0)
        self.assertTrue(rule_matches(rule, ToolCall.from_dict({"tool": "fs.read"})))
        self.assertFalse(rule_matches(rule, ToolCall.from_dict({"tool": "db.read"})))

    def test_matches_agent_and_action(self):
        rule = Rule.from_dict(
            {
                "name": "r",
                "effect": "allow",
                "agents": ["support-*"],
                "actions": ["call", "simulate"],
            },
            0,
        )
        call = ToolCall.from_dict({"tool": "x", "agent": "support-1", "action": "call"})
        self.assertTrue(rule_matches(rule, call))
        self.assertFalse(
            rule_matches(rule, ToolCall.from_dict({"tool": "x", "agent": "ops", "action": "call"}))
        )
