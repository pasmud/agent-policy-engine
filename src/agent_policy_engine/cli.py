"""Command-line interface for agent-policy-engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .audit import AuditLog
from .engine import PolicyEngine
from .models import ToolCall
from .policy_loader import PolicyLoadError, load_policy
from .report import decisions_to_report, render_report
