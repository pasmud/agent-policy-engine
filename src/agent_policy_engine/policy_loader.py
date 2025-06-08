"""Policy loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Policy


class PolicyLoadError(ValueError):
    """Raised when a policy file cannot be parsed or validated."""


def _load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise PolicyLoadError(
                f"YAML policy '{path}' requires PyYAML to be installed"
            ) from exc
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise PolicyLoadError(f"invalid JSON in policy '{path}': {exc}") from exc


def load_policy(path: str | Path) -> Policy:
    """Load and validate a policy from a JSON (or YAML, if PyYAML installed) file."""
    policy_path = Path(path)
    if not policy_path.exists():
        raise PolicyLoadError(f"policy file not found: {policy_path}")
    if not policy_path.is_file():
        raise PolicyLoadError(f"policy path is not a file: {policy_path}")
    data = _load_data(policy_path)
