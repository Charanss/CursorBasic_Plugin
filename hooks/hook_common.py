"""Shared stdin/stdout helpers for Sree-develop Cursor hooks."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def read_hook_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def workspace_root(payload: dict[str, Any]) -> Path | None:
    env_dir = os.environ.get("CURSOR_PROJECT_DIR", "").strip()
    if env_dir:
        return Path(env_dir).resolve()
    roots = payload.get("workspace_roots") or []
    if roots:
        return Path(str(roots[0])).resolve()
    return None


def plugin_root() -> Path:
    env_root = os.environ.get("CURSOR_PLUGIN_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parent.parent


def scripts_dir() -> Path:
    return plugin_root() / "skills" / "sree-develop" / "scripts"


def is_sree_prompt(text: str) -> bool:
    import re

    return bool(re.search(r"(/sree-develop\b|\bsree-develop\b)", text, re.IGNORECASE))


def emit(obj: dict[str, Any]) -> None:
    print(json.dumps(obj))
    raise SystemExit(0)
