import json
import tempfile
import unittest
from pathlib import Path

from agent_policy_engine.policy_loader import PolicyLoadError, load_policy


class TestPolicyLoader(unittest.TestCase):
    def test_load_valid_policy(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "policy.json"
            path.write_text(
                json.dumps(
                    {
                        "version": "1",
                        "default_effect": "deny",
                        "rules": [{"name": "r", "effect": "allow", "tools": ["*"]}],
                    }
                ),
                encoding="utf-8",
            )
            policy = load_policy(path)
            self.assertEqual(policy.default_effect, "deny")
            self.assertEqual(len(policy.rules), 1)

    def test_missing_file(self):
        with self.assertRaises(PolicyLoadError):
            load_policy("/tmp/does-not-exist-policy.json")

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "policy.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(PolicyLoadError):
                load_policy(path)

    def test_invalid_schema(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "policy.json"
            path.write_text(json.dumps({"rules": [{"name": "r"}]}), encoding="utf-8")
            with self.assertRaises(PolicyLoadError):
                load_policy(path)


if __name__ == "__main__":
    unittest.main()
