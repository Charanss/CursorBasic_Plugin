#!/usr/bin/env python3
"""Start a Sree-develop session and write local evidence (layer 1 gate)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import process_compliance as pc  # noqa: E402

EVIDENCE_REL = ".cursor/sree-develop-evidence.json"
SKILL_VERSION = "0.2.0-layer1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize Sree-develop session evidence.")
    parser.add_argument("--text", required=True, help="User prompt / slash command text")
    parser.add_argument("--init", action="store_true", help="Create or refresh session evidence")
    parser.add_argument("--repo", default=".", help="Product repo root (default: cwd)")
    parser.add_argument("--ticket", default="", help="Jira key override")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    if not args.init:
        pc.emit_json({"status": "error", "reason": "pass --init to start session"}, exit_code=1)

    scripts_dir = pc.resolve_scripts_dir()
    manifest_ok, manifest_errors = pc.verify_manifest(scripts_dir)
    if not manifest_ok:
        pc.fail_blocked("manifest_stale_or_tampered", ";".join(manifest_errors))

    repo_root = Path(args.repo).expanduser().resolve()
    ticket = (args.ticket or pc.parse_ticket_key(args.text) or "").upper()

    evidence_path = repo_root / EVIDENCE_REL
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    pc.ensure_git_excludes_evidence(repo_root, EVIDENCE_REL)

    evidence = {
        "schema_version": "1.0",
        "product": "sree-develop",
        "status": "partial",
        "ship_profile": "full",
        "execution_mode": "guided",
        "ticket": {"key": ticket or None, "summary": None},
        "process": {
            "session_started": now_iso(),
            "skill_version": SKILL_VERSION,
            "script_manifest_ok": True,
            "scripts_dir": str(scripts_dir),
            "prompt_excerpt": args.text[:500],
        },
        "workflow_stage": 0,
    }

    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    payload = {
        "status": "ok",
        "gate": "session_started",
        "evidence_path": str(evidence_path),
        "ticket_key": ticket or None,
        "manifest_ok": manifest_ok,
    }
    if args.json:
        pc.emit_json(payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
