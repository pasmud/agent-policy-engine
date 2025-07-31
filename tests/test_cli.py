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
