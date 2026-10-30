---
name: fetch-jira-ticket
description: >-
  Fetch and summarize a Jira ticket via Atlassian MCP. Use when the user
  provides a ticket key (e.g. PROJ-123), asks for Jira details, acceptance
  criteria, or wants to implement work from a ticket.
---

# Fetch Jira ticket

## When to use

Use this skill whenever the user mentions a Jira issue key or asks to pull ticket details.

## Steps

1. Use the Atlassian MCP tools to read the issue by key (e.g. `PROJ-123`).
2. If search is needed, use JQL such as `key = PROJ-123` or `text ~ "..."`.
3. Summarize for the user in this format:

```markdown
## PROJ-123 — <summary>
**Type:** … | **Status:** … | **Assignee:** … | **Priority:** …

### Description
…

### Acceptance criteria
… (extract from description/AC fields if present)

### Comments / recent updates
… (only if relevant)
```

4. Ask whether they want help implementing the ticket next.
5. Do not create, edit, transition, or comment on issues unless the user explicitly asks.

## Notes

- Act only within the user's existing Jira permissions.
- If MCP is not authenticated, tell them to complete Atlassian OAuth from Cursor MCP settings, then retry.
