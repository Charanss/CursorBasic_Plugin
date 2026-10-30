#!/usr/bin/env python3
"""stop: if user asked Ship but evidence has no push, nudge agent to finish gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_common import emit, read_hook_input, workspace_root  # noqa: E402

EVIDENCE = ".cursor/sree-develop-evidence.json"


def main() -> None:
    payload = read_hook_input()
    status = payload.get("status")
    loop_count = int(payload.get("loop_count") or 0)

    if status != "completed" or loop_count >= 2:
        emit({})

    root = workspace_root(payload)
    if not root:
        emit({})

    path = root / EVIDENCE
    if not path.is_file():
        emit({})

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        emit({})

    intent = data.get("intent") or {}
    git_info = data.get("git") or {}
    if not intent.get("ship"):
        emit({})

    if git_info.get("pushed"):
        emit({})

    ticket = (data.get("ticket") or {}).get("key") or "ticket"
    followup = (
        f"Sree-develop Ship is not complete for {ticket}: git push and evidence gates are missing. "
        "Run git push, then: "
        "python skills/sree-develop/scripts/record_git_ship.py record-push --json "
        "and validate_evidence.py --require-ship --json "
        "(set SREE_SCRIPTS to plugin scripts path if needed)."
    )
    emit({"followup_message": followup})


if __name__ == "__main__":
    main()
