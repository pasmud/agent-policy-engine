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

    def test_when_eq_and_in(self):
        rule = Rule.from_dict(
            {
                "name": "r",
                "effect": "allow",
                "when": {
                    "arguments.priority": {"in": ["low", "medium"]},
                    "context.env": {"eq": "dev"},
                },
            },
            0,
        )
        ok = ToolCall.from_dict(
            {"tool": "t", "arguments": {"priority": "low"}, "context": {"env": "dev"}}
        )
        bad = ToolCall.from_dict(
            {"tool": "t", "arguments": {"priority": "high"}, "context": {"env": "dev"}}
        )
        self.assertTrue(rule_matches(rule, ok))
        self.assertFalse(rule_matches(rule, bad))

    def test_when_missing_path_fails(self):
        rule = Rule.from_dict(
            {"name": "r", "effect": "deny", "when": {"arguments.secret": {"eq": "x"}}},
            0,
        )
        self.assertFalse(rule_matches(rule, ToolCall.from_dict({"tool": "t"})))

    def test_when_exists(self):
        rule = Rule.from_dict(
            {"name": "r", "effect": "deny", "when": {"arguments.cmd": {"exists": True}}},
            0,
        )
        self.assertTrue(rule_matches(rule, ToolCall.from_dict({"tool": "t", "arguments": {"cmd": "ls"}})))
        self.assertFalse(rule_matches(rule, ToolCall.from_dict({"tool": "t", "arguments": {}})))

    def test_regex_and_contains(self):
        rule = Rule.from_dict(
            {
                "name": "r",
                "effect": "deny",
                "when": {
                    "arguments.cmd": {"regex": "rm\\s+-rf"},
                    "arguments.flags": {"contains": "--force"},
                },
            },
            0,
        )
        call = ToolCall.from_dict(
            {"tool": "shell", "arguments": {"cmd": "rm -rf /tmp/x", "flags": ["-v", "--force"]}}
        )
        self.assertTrue(rule_matches(rule, call))
