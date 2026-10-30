#!/usr/bin/env python3
"""Validate .cursor/sree-develop-evidence.json (layer 1 rules)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import process_compliance as pc  # noqa: E402

REQUIRED_TOP = ("schema_version", "product", "status", "process", "workflow_stage")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Sree-develop evidence file.")
    parser.add_argument(
        "--path",
        default=".cursor/sree-develop-evidence.json",
        help="Evidence JSON path relative to repo or absolute",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    parser.add_argument(
        "--require-ship",
        action="store_true",
        help="When intent.ship is true, require git commit + push recorded",
    )
    args = parser.parse_args()

    scripts_dir = pc.resolve_scripts_dir()
    ok_manifest, _ = pc.verify_manifest(scripts_dir)
    if not ok_manifest:
        pc.fail_blocked("manifest_stale_or_tampered")

    path = Path(args.path)
    if not path.is_file():
        pc.emit_json({"status": "error", "reason": "evidence_missing", "path": str(path)}, exit_code=1)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        pc.emit_json({"status": "error", "reason": "evidence_invalid_json", "detail": str(exc)}, exit_code=1)

    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing:{key}")

    if data.get("product") != "sree-develop":
        errors.append("product_must_be_sree-develop")

    if data.get("status") not in ("partial", "complete"):
        errors.append("invalid:status")

    process = data.get("process")
    if not isinstance(process, dict) or not process.get("session_started"):
        errors.append("missing:process.session_started")

    if data.get("status") == "complete":
        errors.append("layer1_cannot_be_complete_yet")

    intent = data.get("intent") if isinstance(data.get("intent"), dict) else {}
    git_info = data.get("git") if isinstance(data.get("git"), dict) else {}
    if args.require_ship and intent.get("ship"):
        if not git_info.get("commit_sha"):
            errors.append("ship_requires:git.commit_sha")
        if not git_info.get("pushed"):
            errors.append("ship_requires:git.pushed")

    payload = {
        "status": "ok" if not errors else "invalid",
        "path": str(path.resolve()),
        "errors": errors,
        "session_started": process.get("session_started") if isinstance(process, dict) else None,
    }
    if args.json:
        pc.emit_json(payload, exit_code=0 if not errors else 1)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        raise SystemExit(1)
    print(f"evidence ok: {path}")


if __name__ == "__main__":
    main()
