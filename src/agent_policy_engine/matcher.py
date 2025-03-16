"""Rule matching logic."""

from __future__ import annotations

import fnmatch
import re
from typing import Any

from .models import Rule, ToolCall
