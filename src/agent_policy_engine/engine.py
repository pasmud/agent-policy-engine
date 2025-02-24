"""Policy evaluation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .audit import AuditLog
from .matcher import rule_matches
