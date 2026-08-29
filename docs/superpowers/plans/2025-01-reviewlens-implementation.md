# ReviewLens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build ReviewLens — an AI PR attention triage layer for IBM Bob that separates harmless changes from changes that deserve engineering attention, producing a ranked ATTENTION QUEUE.

**Architecture:** One orchestrator skill spawns four focused subagents (Style, Logic, Coverage, Scope) in parallel. Each returns structured JSON findings. A deterministic merge script deduplicates, scores, and renders the attention queue.

**Tech Stack:** IBM Bob (Agent mode), bash scripts, Python (diff parsing), Node.js CJS (merge + render), Git

---

## File Map

| File | Responsibility |
|------|----------------|
| `.bob/skills/reviewlens/SKILL.md` | Skill entrypoint, all agent instructions, step-by-step execution |
| `.bob/skills/reviewlens/references/severity-rubric.md` | Deterministic priority tiers and score formula |
| `.bob/skills/reviewlens/references/review-principles.md` | Anti-hallucination rules, signal/noise principle |
| `.bob/skills/reviewlens/assets/report-template.md` | Output report template with placeholders |
| `.bob/skills/reviewlens/scripts/collect-diff.sh` | Git diff extraction (bash) |
| `.bob/skills/reviewlens/scripts/split-hunks.sh` | Diff hunk splitting to JSON (bash + python3) |
| `.bob/skills/reviewlens/scripts/validate-json.sh` | Schema validation of subagent outputs (bash + python3) |
| `.bob/skills/reviewlens/scripts/merge-findings.cjs` | Deduplication + priority scoring + report rendering (Node.js CJS) |
| `reviewlens-demo/` | Controlled demo repository |
| `reviewlens-demo/src/auth/session.py` | Demo code — contains deliberate auth bypass bug |
| `reviewlens-demo/src/auth/login.py` | Demo code — formatting noise |
| `reviewlens-demo/src/users/manager.py` | Demo code — naming noise |
| `reviewlens-demo/src/api/routes.py` | Demo code — whitespace/alignment noise |
| `reviewlens-demo/db/migrations/014_add_session_index.sql` | Demo code — scope violation |
| `reviewlens-demo/tests/auth/test_session.py` | Demo tests — intentionally not updated (coverage gap) |
| `reviewlens-demo/CONTRIBUTING.md` | Repository rules — auth changes require regression tests |
| `evaluation/PR01.md–PR05.md` | Ground truth for 5 evaluation scenarios |

---

## Task 1: Verify Bob Skill Activation

**Files:**
- Read: `.bob/skills/reviewlens/SKILL.md`

- [ ] Open Bob in Agent mode from the workspace root `c:\Users\vihaa\IBM-Hackathon-1`
- [ ] Type: `ReviewLens analyze this PR against main`
- [ ] Verify Bob activates the reviewlens skill (not a generic response)
- [ ] If skill does not activate, check frontmatter description keywords match trigger phrases

**Expected:** Bob reads SKILL.md and begins the collection step.

**Checkpoint:** Skill activates reliably from the trigger phrase.

---

## Task 2: Verify Demo Repo Git State

**Files:**
- Read: `reviewlens-demo/` git log

- [ ] `cd reviewlens-demo`
- [ ] Run: `git log --oneline --all`

Expected output:
```
20c37d6 (HEAD -> feature/refactor-auth-ui) PR #184: Refactor authentication UI
88c29bd (main) Initial commit: baseline authentication, payments, users, and API
```

- [ ] Run: `git diff --stat main...feature/refactor-auth-ui`

Expected: 24 changed files (19 constants + 4 modified + 1 db migration)

- [ ] Run: `git checkout main` and verify baseline `session.py` has token validation FIRST
- [ ] Run: `git checkout feature/refactor-auth-ui` and verify buggy `session.py` has user lookup BEFORE token check

**Checkpoint:** Two clean branches with deterministic diff.

---

## Task 3: Test Diff Extraction Script

**Files:**
- Modify if needed: `.bob/skills/reviewlens/scripts/collect-diff.sh`

- [ ] From inside `reviewlens-demo/` on branch `feature/refactor-auth-ui`, run:

```bash
bash ../.bob/skills/reviewlens/scripts/collect-diff.sh main
```

- [ ] Verify `/tmp/reviewlens-diff.txt` created with the full diff
- [ ] Verify `/tmp/reviewlens-files.txt` lists 24 changed files
- [ ] Verify stat summary shows correct insertion/deletion counts

**Note on Windows:** The bash scripts require Git Bash or WSL. On PowerShell, use:
```powershell
git diff main...HEAD > C:\tmp\reviewlens-diff.txt
git diff --name-only main...HEAD > C:\tmp\reviewlens-files.txt
```

**Checkpoint:** Diff extracted deterministically from Git.

---

## Task 4: Test JSON Validation Script

**Files:**
- Modify if needed: `.bob/skills/reviewlens/scripts/validate-json.sh`

- [ ] Create a valid findings file:
```json
[{"category":"logic","file":"src/auth/session.py","line_start":49,"line_end":64,"severity":"critical","confidence":0.94,"summary":"Test finding","evidence":["Evidence line"],"human_review_required":true}]
```

- [ ] Run: `bash .bob/skills/reviewlens/scripts/validate-json.sh /path/to/findings.json`
- [ ] Verify: `✅ VALID: ... (1 finding(s))`

- [ ] Create an invalid file (missing evidence on critical finding):
```json
[{"category":"logic","file":"src/auth/session.py","line_start":0,"line_end":0,"severity":"critical","confidence":0.94,"summary":"Test","evidence":[],"human_review_required":true}]
```

- [ ] Run validation again, verify it exits with error: `Severity 'critical' requires at least one evidence entry`

**Checkpoint:** Validation correctly accepts and rejects inputs.

---

## Task 5: Test Merge-Findings Script End-to-End

**Files:**
- Test: `.bob/skills/reviewlens/scripts/merge-findings.cjs`

- [ ] Create four sample findings files in `C:\tmp\` (style, logic, coverage, scope JSON)
- [ ] Run:
```powershell
node .bob/skills/reviewlens/scripts/merge-findings.cjs C:\tmp\rl-style.json C:\tmp\rl-logic.json C:\tmp\rl-coverage.json C:\tmp\rl-scope.json "--pr-title=PR #184" "--files=24" "--lines=201"
```

- [ ] Verify output structure:
  - `🔴 REVIEW NOW` block shows critical findings
  - `🟠 REVIEW` block shows high findings
  - `🟢 SAFE TO SKIM` block collapses style findings
  - `ANALYSIS BREAKDOWN` shows correct counts
  - `Signal ratio` shown as percentage

- [ ] Verify that two findings on the same file/lines with overlapping keywords get merged into one card with `Supported by:` line

**Checkpoint:** Same inputs always produce same output.

---

## Task 6: Run Full ReviewLens in Agent Mode

**Files:**
- Entry: `.bob/skills/reviewlens/SKILL.md`

- [ ] Open Bob in **Agent mode** (NOT Plan or Ask mode)
- [ ] Navigate to `reviewlens-demo/` directory context
- [ ] Verify you are on branch `feature/refactor-auth-ui`
- [ ] Tell Bob:
  ```
  ReviewLens analyze this PR against main. PR title: "PR #184: Refactor authentication UI". 
  PR description: "Refactored login UI components for cleaner code style. Updated variable 
  naming to match project conventions. This is a UI-focused refactor with no behavior changes."
  ```

- [ ] Watch Bob:
  1. Run `git diff main...HEAD` to extract diff
  2. Read `CONTRIBUTING.md`
  3. Spawn Style subagent
  4. Spawn Logic subagent
  5. Spawn Coverage subagent
  6. Spawn Scope subagent
  7. Validate JSON outputs
  8. Run merge-findings
  9. Render attention queue

- [ ] Verify final output contains:
  - `🔴 REVIEW NOW` with `src/auth/session.py` authentication finding
  - CONTRIBUTING.md citation on coverage finding
  - `🟢 SAFE TO SKIM` with collapsed formatting/naming changes
  - `db/migrations/014_add_session_index.sql` in scope findings

**Checkpoint:** Full pipeline produces coherent ranked queue.

---

## Task 7: Test Approval Behavior (Risk Mitigation)

**Files:**
- Reference: `.bob/skills/reviewlens/SKILL.md` → Demo Mode section

- [ ] Run full ReviewLens and note whether Bob prompts for approval before each subagent spawn
- [ ] If 4 approval prompts appear: test the **Demo Mode fallback**
  - Tell Bob: "Use ReviewLens Demo Mode — run reviewers sequentially"
  - Verify sequential execution produces the same final output
- [ ] Document which mode you'll use for the live demo

**Checkpoint:** Demo can run without repeated approval interruptions.

---

## Task 8: Evaluate Against Ground Truth

**Files:**
- Read: `evaluation/PR01.md`

- [ ] Run ReviewLens on the demo PR (PR-01 scenario)
- [ ] Open `evaluation/PR01.md`
- [ ] Score findings:
  - TP: auth bypass found? coverage gap found? scope violation found?
  - FP: any findings not in ground truth?
  - FN: any ground truth findings missed?
- [ ] Calculate: `precision = TP / (TP + FP)` and `recall = TP / (TP + FN)`
- [ ] Record runtime (start to attention queue rendered)
- [ ] Record manual triage time (human reading diff to identify meaningful areas)

**Checkpoint:** ReviewLens correctly identifies all three PR-01 signals.

---

## Task 9: Run All 5 Evaluation Scenarios

**Files:**
- Read: `evaluation/PR02.md`, `evaluation/PR03.md`, `evaluation/PR04.md`, `evaluation/PR05.md`

For each of PR-02 through PR-05:
- [ ] Set up the scenario (create a branch with the described changes)
- [ ] Run ReviewLens
- [ ] Score against ground truth
- [ ] Note any false positives (especially: does ReviewLens hallucinate bugs where there are none?)
- [ ] Record signal ratio

**Key checks per scenario:**
- PR-02: No false logic bugs (no bug in this PR)
- PR-03: No false coverage gaps (tests were updated)
- PR-04: Zero noise → no collapsed style card
- PR-05: No false critical findings

**Checkpoint:** ReviewLens produces < 2 false positives across all 5 scenarios.

---

## Task 10: Measure and Record Metrics

- [ ] Calculate average runtime across 5 scenarios
- [ ] Calculate manual triage time for PR-01 (time human reviewer to identify meaningful areas)
- [ ] Record: `Time saved = (manual - reviewlens) / manual × 100%`
- [ ] Record signal ratios per PR
- [ ] Write results to `evaluation/results.md`:

```markdown
# ReviewLens Evaluation Results

| PR | TP | FP | FN | Precision | Recall | Runtime | Signal Ratio |
|----|----|----|----| --------- |--------|---------|--------------|
| 01 |    |    |    |           |        |         |              |
| 02 |    |    |    |           |        |         |              |
...

Manual triage time (PR-01): X minutes
ReviewLens time (PR-01):    Y minutes
Time savings:               Z%
```

**Checkpoint:** Quantitative evidence that ReviewLens works.

---

## Task 11: Prepare Demo Reset Script

**Files:**
- Create: `reviewlens-demo/demo-reset.ps1`

- [ ] Write a PowerShell reset script:

```powershell
# demo-reset.ps1 — Run before each demo to get to clean state
Set-Location $PSScriptRoot
git checkout feature/refactor-auth-ui
git status
Write-Host "Demo ready. Branch: $(git branch --show-current)"
Write-Host "Run Bob in Agent mode and say: ReviewLens analyze this PR against main"
```

- [ ] Test the reset script works
- [ ] Add to README.md: "Run `demo-reset.ps1` before each demo"

**Checkpoint:** Clean-room demo reproducible with one command.

---

## Task 12: Final Hardening Checklist

Run through the failure matrix from the build plan:

- [ ] Skill activates reliably (test 3x from cold start)
- [ ] Works in Agent mode (not Plan/Ask)
- [ ] Subagent approval behavior documented
- [ ] Malformed JSON (remove required field) → validate-json.sh catches it
- [ ] Empty diff (no changes) → graceful output
- [ ] Missing CONTRIBUTING.md → skill continues without it
- [ ] Large diff (> 500 lines) → hunk splitting limits context
- [ ] `/review` comparison prepared (Bob's output vs ReviewLens output for PR-01)

**Checkpoint:** All failure modes handled or documented.

---

## Definition of Done

ReviewLens is complete when:

- [ ] Skill activates reliably from trigger phrases
- [ ] Works in Bob Agent mode
- [ ] Four subagents execute (parallel or sequential fallback)
- [ ] Diff extracted deterministically via Git
- [ ] CONTRIBUTING.md / repo docs discovered and cited
- [ ] Agents return structured JSON
- [ ] JSON validated, schema enforced
- [ ] Findings deduplicated
- [ ] Severity consistent with rubric
- [ ] Confidence displayed as percentage
- [ ] Evidence accompanies serious findings
- [ ] Tests searched before coverage claims
- [ ] Scope compared against PR description
- [ ] Formatting noise collapsed into summary
- [ ] Final output is ranked attention queue
- [ ] Demo PR contains known ground truth (PR-01)
- [ ] 5 PR scenarios evaluated
- [ ] Human baseline measured
- [ ] ReviewLens runtime measured
- [ ] Signal ratio measured
- [ ] `/review` comparison prepared
- [ ] Subagent approval behavior tested
- [ ] Fallback (sequential) path tested
- [ ] Clean-room demo tested
