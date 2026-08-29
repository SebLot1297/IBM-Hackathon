# ReviewLens Live Demo Script — Demo 2

> **Audience:** IBM Hackathon video / live demo
> **Duration:** ~3–4 minutes of active AI time
> **Repo:** `reviewlens-demo2/` (this directory)

---

## What you will see

A realistic PR has been prepared on branch `feat/task-completion`.
It claims to add a task completion endpoint and a task summary view. It actually contains:

| Finding | Type | Severity |
|---------|------|----------|
| `require_auth()` moved **after** request body parsing in `POST /api/tasks` | Logic — auth bypass window | 🔴 CRITICAL |
| Off-by-one in `db.get_tasks` pagination: `page * page_size` instead of `(page-1) * page_size` — page 1 always returns empty | Logic — data visibility | 🔴 HIGH |
| No tests for `/api/tasks/<id>/complete` (new endpoint, zero test coverage) | Coverage — missing tests | 🟠 HIGH |
| `db/migrations/002_labels.sql` — unrelated to the stated PR scope | Scope creep | 🟡 MEDIUM |
| ~5 variable/parameter renames in `tasks.py` and `tasks.js` | Style noise | 🟢 LOW |

ReviewLens will find all of them.

---

## Pre-flight checklist

1. Make sure you are in **Agent mode** in IBM Bob.
2. Open this repository in Bob.
3. The PR branch `feat/task-completion` must exist.

```powershell
# Confirm the branch exists
cd reviewlens-demo2
git branch
# expected: feat/task-completion, main
```

---

## Demo Steps

### Step 1 — Open IBM Bob in Agent mode

Switch to Agent mode if not already there.

---

### Step 2 — Trigger ReviewLens

Type exactly this into Bob:

```
ReviewLens analyze this PR

PR title: feat: add /api/tasks/<id>/complete endpoint and task summary view
Base branch: main
PR branch: feat/task-completion

PR Description:
Adds a new POST /api/tasks/<id>/complete endpoint that lets the authenticated
owner mark a task as done. Also adds GET /api/tasks/summary to return pending
vs completed counts. Refactors the frontend tasks.js to use the new summary
endpoint instead of computing counts client-side.
```

---

### Step 3 — Watch the four subagents spawn

Bob will:
1. Run `git diff main...feat/task-completion` to collect the diff
2. Read `CONTRIBUTING.md` for repository rules
3. Spawn **Style**, **Logic**, **Coverage**, and **Scope** agents in parallel
4. Validate their JSON output
5. Merge and deduplicate with the scoring script
6. Render the ranked ATTENTION QUEUE

---

### Step 4 — Expected output (what ReviewLens should produce)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       REVIEWLENS ATTENTION QUEUE
       feat: add /api/tasks/<id>/complete endpoint
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5 changed files · ~120 changed lines analyzed

PR ATTENTION SCORE
High-risk changes:  2–3
Low-signal changes: 5
Scope concerns:     1

🔴 REVIEW NOW
───────────────────────────────────────────────────────
taskflow-api/app.py:47
Authentication check moved after request body parsing
— an attacker can trigger body parsing logic before auth
validation completes. Violates CONTRIBUTING.md rule #1.

Confidence: ~90%

taskflow-api/db.py:58
Pagination off-by-one: page 1 always returns empty
— start = page * page_size evaluates to 20 for page=1,
skipping the first page entirely.

Confidence: ~95%

🟠 REVIEW
───────────────────────────────────────────────────────
taskflow-api/app.py (new /api/tasks/<id>/complete endpoint)
No tests added for new complete endpoint.
CONTRIBUTING.md requires auth test, 401 test, and 400 test.

🟡 REVIEW IF TIME
───────────────────────────────────────────────────────
db/migrations/002_labels.sql
Migration file included — not mentioned in PR description
and unrelated to task completion feature.

🟢 SAFE TO SKIM
───────────────────────────────────────────────────────
5 formatting / variable rename changes
Files: taskflow-api/tasks.py, frontend/tasks.js
```

---

## Talking points for the video

- **"Same pattern as Demo 1, entirely different codebase — ReviewLens generalises."**
- **"The auth bypass is identical in shape to the FinPay bug: `require_auth()` is still called, just three lines too late."**
- **"Pagination off-by-one: `page * page_size` instead of `(page-1) * page_size` — requesting page 1 returns nothing."**
- **"The labels migration is pure scope creep — bundled silently with a task completion feature."**
- **"Style noise collapses five renames into one 🟢 line so reviewers don't drown in trivial diffs."**

---

## Resetting the demo

```powershell
# Nothing destructive was done — the branches are static.
# Just re-run ReviewLens with the same prompt to replay.
```
