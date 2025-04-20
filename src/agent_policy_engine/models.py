"""Core data models for policy evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return a deterministic-friendly UTC timestamp helper for runtime use."""
