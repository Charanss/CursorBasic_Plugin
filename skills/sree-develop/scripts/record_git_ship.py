#!/usr/bin/env python3
"""Record git commit/push in evidence after agent runs git (Ship flow gate)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import evidence_io as ev  # noqa: E402
from lib import process_compliance as pc  # noqa: E402

SKILL_VERSION = "0.3.0-ship"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_output(args: list[str], repo: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pc.emit_json(
            {
                "status": "error",
                "reason": "git_command_failed",
                "command": args,
                "stderr": (result.stderr or "").strip()[:500],
            },
            exit_code=1,
        )
    return (result.stdout or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Record commit or push in Ship evidence.")
    parser.add_argument("--repo", default=".", help="Product repo root")
    sub = parser.add_subparsers(dest="action", required=True)

    commit_p = sub.add_parser("record-commit", help="After successful git commit")
    commit_p.add_argument("--json", action="store_true", help="Print JSON result")
    commit_p.add_argument("--sha", default="", help="Commit SHA (default: HEAD)")
    commit_p.add_argument("--branch", default="", help="Branch name (default: current)")
    commit_p.add_argument("--message", default="", help="First line of commit message")

    push_p = sub.add_parser("record-push", help="After successful git push")
    push_p.add_argument("--json", action="store_true", help="Print JSON result")
    push_p.add_argument("--remote", default="origin", help="Remote name")
    push_p.add_argument("--sha", default="", help="Commit SHA pushed (default: HEAD)")

    check_p = sub.add_parser("check-ship", help="Gate: Ship intent must show commit + push recorded")
    check_p.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    scripts_dir = pc.resolve_scripts_dir()
    ok_manifest, errors = pc.verify_manifest(scripts_dir)
    if not ok_manifest:
        pc.fail_blocked("manifest_stale_or_tampered", ";".join(errors))

    repo_root = Path(args.repo).expanduser().resolve()
    try:
        data = ev.load(repo_root)
    except FileNotFoundError:
        pc.emit_json({"status": "error", "reason": "evidence_missing"}, exit_code=1)

    intent = data.get("intent") or {}
    git_info = data.setdefault("git", {})

    if args.action == "record-commit":
        sha = args.sha or git_output(["rev-parse", "HEAD"], repo_root)
        branch = args.branch or git_output(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
        git_info.update(
            {
                "commit_sha": sha,
                "feature_branch": branch,
                "commit_message_excerpt": (args.message or "")[:200],
                "commit_recorded_at": now_iso(),
            }
        )
        data["workflow_stage"] = max(int(data.get("workflow_stage") or 0), 3)
        data.setdefault("process", {})["skill_version"] = SKILL_VERSION
        path = ev.save(repo_root, data)
        payload = {"status": "ok", "gate": "commit_recorded", "commit_sha": sha, "branch": branch}
        if args.json:
            pc.emit_json(payload)
        print(json.dumps(payload, indent=2))
        return

    if args.action == "record-push":
        if not intent.get("ship"):
            pc.emit_json(
                {"status": "ok", "gate": "push_skipped", "reason": "ship_intent_false"},
            )
        sha = args.sha or git_output(["rev-parse", "HEAD"], repo_root)
        git_info.update(
            {
                "pushed": True,
                "push_remote": args.remote,
                "push_sha": sha,
                "push_recorded_at": now_iso(),
            }
        )
        data["workflow_stage"] = max(int(data.get("workflow_stage") or 0), 4)
        data.setdefault("process", {})["skill_version"] = SKILL_VERSION
        path = ev.save(repo_root, data)
        payload = {"status": "ok", "gate": "push_recorded", "push_sha": sha, "remote": args.remote}
        if args.json:
            pc.emit_json(payload)
        print(json.dumps(payload, indent=2))
        return

    if args.action == "check-ship":
        errors_list: list[str] = []
        if not intent.get("ship"):
            payload = {"status": "ok", "gate": "check_ship", "required": False}
            if args.json:
                pc.emit_json(payload)
            print(json.dumps(payload, indent=2))
            return
        if not git_info.get("commit_sha"):
            errors_list.append("missing:git.commit_sha")
        if not git_info.get("pushed"):
            errors_list.append("missing:git.pushed")
        payload = {
            "status": "ok" if not errors_list else "blocked",
            "gate": "check_ship",
            "required": True,
            "errors": errors_list,
        }
        if args.json:
            pc.emit_json(payload, exit_code=0 if not errors_list else 1)
        if errors_list:
            for err in errors_list:
                print(err, file=sys.stderr)
            raise SystemExit(1)
        print(json.dumps(payload, indent=2))
        return


if __name__ == "__main__":
    main()
