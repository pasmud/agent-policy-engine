import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC) + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, "-m", "agent_policy_engine", *args],
        cwd=str(cwd or REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class TestCLI(unittest.TestCase):
    def test_help(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("agent-policy-engine", result.stdout)
        self.assertIn("check", result.stdout)

    def test_check_json_report(self):
        result = run_cli(
            "check",
            "--policy",
            "examples/policy.json",
            "--input",
            "examples/calls.json",
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["summary"]["total"], 4)
        self.assertEqual(report["summary"]["allowed"], 2)
        self.assertEqual(report["summary"]["denied"], 2)

    def test_check_text_report(self):
        result = run_cli(
            "check",
            "--policy",
            "examples/policy.json",
            "--input",
            "examples/calls.json",
            "--format",
            "text",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("total=4", result.stdout)
        self.assertIn("DENY", result.stdout)
        self.assertIn("ALLOW", result.stdout)

    def test_fail_on_deny(self):
        result = run_cli(
            "check",
            "--policy",
            "examples/policy.json",
            "--input",
            "examples/calls.json",
            "--fail-on-deny",
        )
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertGreater(report["summary"]["denied"], 0)

    def test_audit_out_written(self):
        with tempfile.TemporaryDirectory() as td:
            audit_path = Path(td) / "audit.jsonl"
            result = run_cli(
                "check",
                "--policy",
                "examples/policy.json",
                "--input",
                "examples/calls.json",
                "--audit-out",
                str(audit_path),
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(audit_path.exists())
            lines = [line for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(lines), 4)
            record = json.loads(lines[0])
            self.assertIn("timestamp", record)
            self.assertIn("decision", record)

    def test_invalid_policy_returns_error(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text(
                json.dumps({"version": "1", "default_effect": "maybe", "rules": []}),
                encoding="utf-8",
            )
            result = run_cli("check", "--policy", str(bad), "--input", "examples/calls.json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("error:", result.stderr)
