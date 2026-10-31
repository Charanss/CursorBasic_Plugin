# my-plugins

Cursor plugin bundle: **Atlassian MCP**, Jira ticket skills, and **Sree-develop** (gates, evidence, Ship flow, hooks).

## Setup

1. Clone or copy this repo, or install from [Charanss/CursorBasic_Plugin](https://github.com/Charanss/CursorBasic_Plugin).
2. For local dev, place at `~/.cursor/plugins/local/my-plugins` and reload Cursor.
3. Open **Customize** and confirm the plugin / Atlassian MCP server appears.
4. Authenticate with Atlassian when prompted (OAuth).
5. In chat: `Fetch PROJ-123` or `/fetch-jira-ticket`.
6. Create tickets: `/create-jira-ticket`.
7. End-to-end work: `/sree-develop PROJ-123 Ship` (product repo + GitHub remote).

## Contents

- `mcp.json` — Atlassian MCP (`https://mcp.atlassian.com/v2/mcp`)
- `skills/fetch-jira-ticket` — summarize existing tickets
- `skills/create-jira-ticket` — create tickets with acceptance criteria
- `skills/sree-develop` — Jira → implement → commit → push with evidence gates
  - **Docs:** `skills/sree-develop/docs/IMPLEMENTATION.md`
- `hooks/` — Cursor hooks (toolchain on prompt, Ship reminder on stop)

### Try Sree-develop gates (product repo root)

```powershell
$env:SREE_SCRIPTS = "C:\path\to\my-plugins\skills\sree-develop\scripts"
cd C:\path\to\your-product-repo
python "$env:SREE_SCRIPTS\resolve_sree_scripts.py" --json
python "$env:SREE_SCRIPTS\sree_session_start.py" --init --text "/sree-develop PROJ-1 Ship" --json
```

## Multiple plugins later

This repo can grow into a **multi-plugin marketplace** (add `.cursor-plugin/marketplace.json` and one folder per plugin). Today everything ships as one plugin: **`my-plugins`**.
