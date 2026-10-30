# Toolchain (layer 1)

Before Jira fetch or code edits on `/sree-develop`, run:

```powershell
python skills/sree-develop/scripts/resolve_sree_scripts.py --json
python skills/sree-develop/scripts/sree_session_start.py --init --text "<user prompt>" --json
```

If resolve returns `"blocked": "toolchain"`, stop: read-only analysis only.

## Script locations (first match wins)

1. `SREE_SCRIPTS` or `_SCRIPTS` env var
2. Plugin skill `scripts/` next to `manifest.json`
3. `~/.cursor/skills/sree-develop/scripts`

## After editing scripts

```powershell
python skills/sree-develop/scripts/build_manifest.py
```

Commit updated `manifest.json` or gates will fail with hash mismatch.
