# jira-ticket-details

Local Cursor plugin that connects to the Atlassian Rovo MCP server and includes a skill for fetching Jira ticket details.

## Setup

1. This folder lives at `~/.cursor/plugins/local/jira-ticket-details`.
2. Reload the Cursor window (`Developer: Reload Window`).
3. Open **Customize** and confirm the plugin / Atlassian MCP server appears.
4. Authenticate with Atlassian when prompted (OAuth).
5. In chat, ask: `Fetch PROJ-123` or invoke `/fetch-jira-ticket`.
6. To create: `/create-jira-ticket` (or ask to create a ticket with acceptance criteria).
7. End-to-end implement + commit + push: `/sree-develop SCRUM-5` (needs a git repo with GitHub remote).

## Contents

- `mcp.json` — Atlassian MCP (`https://mcp.atlassian.com/v2/mcp`)
- `skills/fetch-jira-ticket` — summarize existing tickets
- `skills/create-jira-ticket` — create tickets with acceptance criteria
- `skills/sree-develop` — fetch ticket → implement → commit → push to GitHub
  - **Layer 1:** evidence file + gate scripts under `skills/sree-develop/scripts/` (see `references/toolchain-layer1.md`)

### Try layer 1 (in any git repo checkout)

```powershell
cd C:\path\to\your-product-repo
python path\to\skills\sree-develop\scripts\resolve_sree_scripts.py --json
python path\to\skills\sree-develop\scripts\sree_session_start.py --init --text "/sree-develop PROJ-1" --json
python path\to\skills\sree-develop\scripts\validate_evidence.py --json
```
