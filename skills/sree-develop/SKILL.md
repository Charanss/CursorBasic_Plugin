---
name: sree-develop
description: >-
  End-to-end Sree develop flow: fetch a Jira ticket via Atlassian MCP,
  implement the work against acceptance criteria, then commit and push
  to GitHub. Use when the user says Sree-develop, /sree-develop, Sree-develop
  TICKET-123 Ship, or asks to implement a Jira ticket and push the changes.
---

# Sree-develop

Implement a Jira ticket in the current repo. When the user includes **`Ship`** in the prompt (e.g. `Sree-develop AOS-5342 Ship`), you **must** commit and push to GitHub after implementation and record both in evidence gates.

Full flow: `docs/IMPLEMENTATION.md`.

## Ship keyword

| Prompt | `ship_profile` | Commit / push |
|--------|----------------|---------------|
| `Sree-develop AOS-5342` | `implement_only` | Only if user asks |
| `Sree-develop AOS-5342 Ship` | `full` | **Required** + evidence gates |

## Mandatory gates (product repo root)

Before Jira fetch or edits:

```powershell
python skills/sree-develop/scripts/resolve_sree_scripts.py --json
python skills/sree-develop/scripts/sree_session_start.py --init --text "<full user prompt>" --json
python skills/sree-develop/scripts/validate_evidence.py --json
```

If `resolve_sree_scripts` returns `"blocked": "toolchain"`, stop (read-only only). See `references/toolchain-layer1.md` and `docs/IMPLEMENTATION.md`.

## Required input

- Jira issue key (e.g. `SCRUM-5`). Ask if missing.

Optional: target branch name (default: current branch, or create `feature/<issue-key-lowercase>` if user asks for a new branch).

## Workflow

### 0. Session evidence

Evidence file: `.cursor/sree-develop-evidence.json` (local only, never commit). Status stays **`partial`** until a future closeout layer sets **`complete`**.

### 1. Fetch the ticket

1. Ensure Atlassian MCP is authenticated; if not, prompt for OAuth then continue.
2. Resolve `cloudId` via `getAccessibleAtlassianResources` (once per session).
3. Load the issue with `getJiraIssue` (`view: evidence` or `full`).
4. Summarize for the user:

```markdown
## <KEY> — <summary>
**Type:** … | **Status:** … | **Priority:** …

### Goal
…

### Acceptance criteria
- [ ] …
```

5. Pause briefly only if AC is empty or ambiguous — ask one clarifying question, then proceed.

### 2. Implement

1. Explore the codebase; match existing patterns and scope.
2. Implement the smallest change set that satisfies the acceptance criteria.
3. Prefer editing existing files over new files; no drive-by refactors.
4. Run relevant tests/linters when available; fix failures you caused.
5. Do **not** edit, transition, or comment on the Jira issue unless the user asks.

### 3. Commit

When implementation is ready (or user says commit):

1. Run in parallel: `git status`, `git diff`, `git log -5 --oneline`.
2. Stage only files related to this ticket (never `.env`, credentials, secrets).
3. Commit with a message tied to the ticket:

```text
<type>(scope): <short why>

<KEY>: <one line linking to the ticket goal>
```

Example: `feat(auth): add login rate limit`

`SCRUM-5: enforce 5 attempts per minute on /login`

4. Use a HEREDOC (or PowerShell here-string) for the message. Do not use `--no-verify` or amend unless the user explicitly asks and amend rules allow it.
5. Run `git status` after commit to verify.
6. **Gate (always after commit):**

```powershell
python skills/sree-develop/scripts/record_git_ship.py record-commit --message "<first line>" --json
```

### 4. Push to GitHub

When **`Ship`** was in the prompt (or user asked to push):

1. Confirm remote is GitHub (`git remote -v`). If no remote / not GitHub, stop and tell the user.
2. Push the current branch: `git push -u origin HEAD` (first push) or `git push`.
3. Never force-push to `main`/`master`. Never `push --force` unless the user explicitly requests it.
4. **Gate (after successful push):**

```powershell
python skills/sree-develop/scripts/record_git_ship.py record-push --json
```

5. If **`Ship`** intent: validate delivery:

```powershell
python skills/sree-develop/scripts/validate_evidence.py --require-ship --json
python skills/sree-develop/scripts/record_git_ship.py check-ship --json
```

6. Reply with: issue key, branch name, commit SHA, and PR URL if `gh pr create` was requested (do not open a PR unless asked).

## Done checklist

Reply with:

- Jira key + one-line summary of what shipped
- Files touched (brief)
- Commit SHA + branch
- Push result (success / blocked reason)
- Remaining AC items, if any

## Do not

- Invent ticket requirements when Jira is unreachable — stop and report auth/API errors.
- Commit unrelated dirty files from the working tree.
- Push if commit failed or hooks rejected the commit (fix, then new commit).
- Claim **Ship** complete without `validate_evidence.py --require-ship` passing.
