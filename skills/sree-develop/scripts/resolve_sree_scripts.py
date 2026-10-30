#!/usr/bin/env python3
"""Locate Sree-develop scripts and verify manifest integrity."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import process_compliance as pc  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve Sree-develop script directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    scripts_dir = pc.resolve_scripts_dir()
    ok, errors = pc.verify_manifest(scripts_dir)
    payload = {
        "status": "ok" if ok else "blocked",
        "blocked": None if ok else "toolchain",
        "scripts_dir": str(scripts_dir),
        "manifest_ok": ok,
        "manifest_errors": errors,
    }
    if args.json:
        pc.emit_json(payload, exit_code=0 if ok else 2)
    print(f"scripts_dir={scripts_dir} manifest_ok={ok}")
    if not ok:
        for err in errors:
            print(err, file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
