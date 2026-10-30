---
name: create-jira-ticket
description: >-
  Create a Jira issue via Atlassian MCP with description and acceptance
  criteria. Use when the user asks to create, file, or open a Jira ticket,
  story, bug, or task that should include acceptance criteria.
---

# Create Jira ticket

## When to use

Use when the user wants a **new** Jira issue that includes acceptance criteria.

## Required inputs

Collect before creating (ask only for what is missing):

| Field | Required | Notes |
|-------|----------|-------|
| `projectKey` | Yes | e.g. `PROJ` |
| `summary` | Yes | Short title |
| `issueType` | Yes | e.g. Story, Task, Bug |
| Description | Yes | Problem / context |
| Acceptance criteria | Yes | Testable checklist |
| `priority` / `assignee` / `labels` / `parent` | No | Only if user provides |

## Description template

Build the issue `description` in markdown:

```markdown
## Summary
<1–3 sentences: what and why>

## Acceptance criteria
- [ ] <criterion 1 — observable / testable>
- [ ] <criterion 2>
- [ ] <criterion 3>
```

Rules for acceptance criteria:

- Each item must be verifiable (pass/fail).
- Prefer user-visible or API-observable outcomes over implementation details.
- If the user gives prose AC, rewrite into checklist items; do not drop meaning.
- If a dedicated Acceptance Criteria custom field exists and the user names it, put AC there via `additional_fields` **and** keep a short AC section in the description.

## Steps

1. Resolve `cloudId` once via `getAccessibleAtlassianResources` (reuse for the rest of the session).
2. Draft the full ticket (summary, type, description with AC). Show the draft to the user.
3. **Create only after the user confirms** the draft (unless they already said “create it now” with enough detail).
4. Call `createJiraIssue` with markdown description (`contentFormat` markdown).
5. Reply with the new issue key and link if returned. Offer to fetch or refine the ticket next.

## Do not

- Create, edit, transition, or comment unless the user wants that action.
- Invent project keys, issue types, or assignees — ask or look up via MCP.
- Duplicate-create after a partial failure that already returned an issue key.

## Notes

- Respect the user’s Jira permissions.
- If MCP auth is missing, send them to Cursor MCP settings to complete Atlassian OAuth, then retry.
