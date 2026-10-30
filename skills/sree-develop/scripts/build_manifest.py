#!/usr/bin/env python3
"""Regenerate manifest.json SHA256 entries for tracked scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.process_compliance import sha256_file  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent
SKIP = {"build_manifest.py", "manifest.json"}


def main() -> None:
    scripts: dict[str, str] = {}
    for path in sorted(SCRIPTS_DIR.rglob("*.py")):
        rel = path.relative_to(SCRIPTS_DIR).as_posix()
        if path.name in SKIP:
            continue
        scripts[rel] = sha256_file(path)

    manifest = {
        "product": "sree-develop",
        "version": 1,
        "scripts": scripts,
    }
    out = SCRIPTS_DIR / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(scripts)} scripts)")


if __name__ == "__main__":
    main()
