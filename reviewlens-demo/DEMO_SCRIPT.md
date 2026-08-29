# ReviewLens Live Demo Script

> **Audience:** IBM Hackathon video / live demo
> **Duration:** ~3–4 minutes of active AI time
> **Repo:** `reviewlens-demo/` (this directory)

---

## What you will see

A realistic PR has been prepared on branch `feat/user-dashboard`.
It claims to add a user dashboard endpoint. It actually contains:

| Finding | Type | Severity |
|---------|------|----------|
| `require_auth()` moved **after** request body parsing in `/api/transfer` | Logic — auth bypass window | 🔴 CRITICAL |
| Off-by-one in `db.get_transactions` pagination: `page * page_size` instead of `(page-1) * page_size` — page 1 always returns empty | Logic — data visibility | 🔴 HIGH |
| No tests for `/api/dashboard` (new endpoint, zero test coverage) | Coverage — missing tests | 🟠 HIGH |
| `db/migrations/002_user_preferences.sql` — unrelated to the stated PR scope | Scope creep | 🟡 MEDIUM |
| ~6 variable/parameter renames in `payments.py` and `dashboard.js` | Style noise | 🟢 LOW |

ReviewLens will find all of them.

---

## Pre-flight checklist

1. Make sure you are in **Agent mode** in IBM Bob.
2. Open this repository in Bob.
3. The PR branch `feat/user-dashboard` must exist (it does — it was committed by the setup script).

```powershell
# Confirm the branch exists
cd reviewlens-demo
git branch
# expected: feat/user-dashboard, main
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

PR title: feat: add /api/dashboard endpoint with balance + transaction summary
Base branch: main
PR branch: feat/user-dashboard

PR Description:
Adds a new GET /api/dashboard endpoint that returns the authenticated user's
balance, recent transactions, and a sent/received summary in a single call.
Also refactors the frontend dashboard.js to use the new combined endpoint
instead of two separate API calls.
```

---

### Step 3 — Watch the four subagents spawn

Bob will:
1. Run `git diff main...feat/user-dashboard` to collect the diff
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
       feat: add /api/dashboard endpoint
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5 changed files · ~130 changed lines analyzed

PR ATTENTION SCORE
High-risk changes:  2–3
Low-signal changes: 5–6
Scope concerns:     1

🔴 REVIEW NOW
───────────────────────────────────────────────────────
finpay-api/app.py:44
Authentication check moved after request body parsing
— an attacker can trigger body parsing logic before auth
validation completes. Violates CONTRIBUTING.md rule #1.

Confidence: ~88%

finpay-api/db.py:51
Pagination off-by-one: page 1 always returns empty
— start = page * page_size evaluates to 20 for page=1,
skipping the first page entirely.

Confidence: ~95%

🟠 REVIEW
───────────────────────────────────────────────────────
finpay-api/app.py (new /api/dashboard endpoint)
No tests added for new dashboard endpoint.
CONTRIBUTING.md requires auth test, 401 test, and 400 test.

🟡 REVIEW IF TIME
───────────────────────────────────────────────────────
db/migrations/002_user_preferences.sql
Migration file included — not mentioned in PR description
and unrelated to dashboard feature.

🟢 SAFE TO SKIM
───────────────────────────────────────────────────────
5–6 formatting / variable rename changes
Files: finpay-api/payments.py, frontend/dashboard.js
```

---

## Talking points for the video

- **"ReviewLens doesn't just say 'looks good' — it ranks what actually matters."**
- **"The auth bypass is subtle. The `require_auth()` call is still there — it's just been moved three lines down, after the body has already been parsed. A human reviewer skimming this could easily miss it."**
- **"The pagination bug means that requesting page 1 always returns zero results. It's a one-character off-by-one that breaks the feature entirely."**
- **"Style noise — six renames — gets collapsed into one line so reviewers don't waste time on it."**
- **"This whole triage ran in under 3 minutes and used four parallel AI reviewers with deterministic scoring."**

---

## Resetting the demo

```powershell
# Nothing destructive was done — the branches are static.
# Just re-run ReviewLens with the same prompt to replay.
```
