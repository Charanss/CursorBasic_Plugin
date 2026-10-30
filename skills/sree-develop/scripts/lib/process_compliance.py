"""Shared helpers for Sree-develop gate scripts (stdlib only)."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

MANIFEST_NAME = "manifest.json"
TRACKED_SUFFIXES = {".py"}


def emit_json(payload: dict[str, Any], exit_code: int = 0) -> None:
    print(json.dumps(payload, indent=2))
    raise SystemExit(exit_code)


def fail_blocked(reason: str, detail: str | None = None) -> None:
    body: dict[str, Any] = {"status": "blocked", "blocked": "toolchain", "reason": reason}
    if detail:
        body["detail"] = detail
    emit_json(body, exit_code=2)


def script_root() -> Path:
    return Path(__file__).resolve().parent.parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(scripts_dir: Path) -> dict[str, Any]:
    manifest_path = scripts_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        fail_blocked("manifest_missing", str(manifest_path))
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail_blocked("manifest_invalid", str(exc))


def verify_manifest(scripts_dir: Path) -> tuple[bool, list[str]]:
    manifest = load_manifest(scripts_dir)
    entries = manifest.get("scripts")
    if not isinstance(entries, dict):
        fail_blocked("manifest_invalid", "missing scripts map")
    errors: list[str] = []
    for rel, expected in entries.items():
        path = scripts_dir / rel
        if not path.is_file():
            errors.append(f"missing:{rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"hash_mismatch:{rel}")
    return (len(errors) == 0, errors)


def resolve_scripts_dir() -> Path:
    for env_name in ("SREE_SCRIPTS", "_SCRIPTS"):
        override = os.environ.get(env_name, "").strip()
        if override:
            return Path(override).expanduser().resolve()

    root = script_root()
    if (root / MANIFEST_NAME).is_file():
        return root

    user_copy = Path.home() / ".cursor" / "skills" / "sree-develop" / "scripts"
    if (user_copy / MANIFEST_NAME).is_file():
        return user_copy

    fail_blocked("scripts_not_found", "Set SREE_SCRIPTS or install plugin scripts")


def ensure_git_excludes_evidence(repo_root: Path, evidence_rel: str) -> None:
    git_dir = repo_root / ".git"
    if not git_dir.is_dir():
        return
    exclude_file = git_dir / "info" / "exclude"
    exclude_file.parent.mkdir(parents=True, exist_ok=True)
    line = evidence_rel.replace("\\", "/")
    existing = exclude_file.read_text(encoding="utf-8") if exclude_file.is_file() else ""
    if line not in existing.splitlines():
        with exclude_file.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(f"{line}\n")


def parse_ticket_key(text: str) -> str | None:
    import re

    match = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", text)
    return match.group(1) if match else None
