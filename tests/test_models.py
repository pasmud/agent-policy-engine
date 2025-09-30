import unittest

from agent_policy_engine.models import Decision, Policy, Rule, ToolCall


class TestToolCall(unittest.TestCase):
    def test_from_dict_minimal(self):
        call = ToolCall.from_dict({"tool": "filesystem.read"})
        self.assertEqual(call.tool, "filesystem.read")
        self.assertEqual(call.agent, "default")
        self.assertEqual(call.action, "call")
        self.assertEqual(call.arguments, {})
        self.assertEqual(call.context, {})

    def test_from_dict_full(self):
        call = ToolCall.from_dict(
            {
                "tool": "db.query",
                "agent": "analyst",
                "action": "invoke",
                "arguments": {"sql": "select 1"},
                "context": {"env": "dev"},
                "call_id": "abc",
            }
        )
        self.assertEqual(call.agent, "analyst")
        self.assertEqual(call.action, "invoke")
        self.assertEqual(call.call_id, "abc")
        self.assertEqual(call.arguments["sql"], "select 1")

    def test_from_dict_rejects_missing_tool(self):
        with self.assertRaises(ValueError):
            ToolCall.from_dict({"agent": "a"})

    def test_from_dict_rejects_bad_arguments(self):
        with self.assertRaises(ValueError):
            ToolCall.from_dict({"tool": "x", "arguments": []})


class TestRule(unittest.TestCase):
    def test_from_dict_defaults(self):
        rule = Rule.from_dict({"name": "r1", "effect": "allow"}, 0)
        self.assertEqual(rule.tools, ("*",))
        self.assertEqual(rule.agents, ("*",))
        self.assertEqual(rule.actions, ("*",))
        self.assertEqual(rule.priority, 0)
