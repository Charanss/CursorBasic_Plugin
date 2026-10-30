# Evidence bundle (layer 1)

## Path

In the **product repo** you are implementing (not the plugin repo):

`.cursor/sree-develop-evidence.json`

## Rules

- **Never commit** this file. `sree_session_start.py` adds it to `.git/info/exclude` when possible.
- **`status: partial`** — session in progress; do not claim end-to-end done in chat.
- **`status: complete`** — reserved for a later layer (PR/CI closeout gate).

## Validate

From the product repo root:

```powershell
python path\to\skills\sree-develop\scripts\validate_evidence.py --json
```

Schema: `schemas/sree-develop-evidence.schema.json`
