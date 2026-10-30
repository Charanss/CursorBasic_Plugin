#!/usr/bin/env python3
"""beforeSubmitPrompt: block Sree-develop if gate scripts/toolchain are broken."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "sree-develop" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_common import emit, is_sree_prompt, read_hook_input, scripts_dir  # noqa: E402
from lib import process_compliance as pc  # noqa: E402


def main() -> None:
    payload = read_hook_input()
    prompt = str(payload.get("prompt") or "")

    if not is_sree_prompt(prompt):
        emit({"continue": True})

    os.environ["SREE_SCRIPTS"] = str(scripts_dir())
    try:
        directory = pc.resolve_scripts_dir()
        ok, _errors = pc.verify_manifest(directory)
    except SystemExit:
        emit(
            {
                "continue": False,
                "user_message": "Sree-develop toolchain blocked. Reinstall the plugin or fix SREE_SCRIPTS / manifest.",
            }
        )
        return

    if not ok:
        emit(
            {
                "continue": False,
                "user_message": "Sree-develop script manifest check failed. Run build_manifest.py in the plugin repo.",
            }
        )

    emit({"continue": True})


if __name__ == "__main__":
    main()
