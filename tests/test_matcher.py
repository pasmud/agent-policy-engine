import unittest

from agent_policy_engine.matcher import rule_matches
from agent_policy_engine.models import Rule, ToolCall


class TestMatcher(unittest.TestCase):
    def test_matches_wildcards(self):
        rule = Rule.from_dict({"name": "r", "effect": "allow", "tools": ["fs.*"]}, 0)
        self.assertTrue(rule_matches(rule, ToolCall.from_dict({"tool": "fs.read"})))
        self.assertFalse(rule_matches(rule, ToolCall.from_dict({"tool": "db.read"})))
