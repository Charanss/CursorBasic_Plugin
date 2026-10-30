"""Read/write sree-develop evidence bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVIDENCE_REL = ".cursor/sree-develop-evidence.json"


def evidence_path(repo_root: Path) -> Path:
    return repo_root / EVIDENCE_REL


def load(repo_root: Path) -> dict[str, Any]:
    path = evidence_path(repo_root)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def save(repo_root: Path, data: dict[str, Any]) -> Path:
    path = evidence_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
