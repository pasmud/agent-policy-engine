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
