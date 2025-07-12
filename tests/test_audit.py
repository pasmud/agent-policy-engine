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

    def test_append_and_to_dicts(self):
        log = AuditLog()
        rec = log.append(self._decision(True), timestamp="2025-01-01T00:00:00+00:00")
        self.assertEqual(rec.timestamp, "2025-01-01T00:00:00+00:00")
        self.assertEqual(len(log.to_dicts()), 1)
        self.assertTrue(log.to_dicts()[0]["decision"]["allowed"])

    def test_write_and_read_jsonl(self):
        log = AuditLog()
        log.append(self._decision(True), timestamp="2025-01-01T00:00:00+00:00")
        log.append(self._decision(False), timestamp="2025-01-01T00:00:01+00:00")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "audit.jsonl"
            log.write_jsonl(path)
            loaded = AuditLog.from_jsonl(path)
            self.assertEqual(len(loaded.records), 2)
            self.assertFalse(loaded.records[1].decision["allowed"])

    def test_clear(self):
        log = AuditLog()
        log.append(self._decision())
        log.clear()
        self.assertEqual(log.records, [])


if __name__ == "__main__":
    unittest.main()
