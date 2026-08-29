---
name: reviewlens
description: >
  ReviewLens — AI PR Attention Triage. Use when you want to analyze a pull request and
  produce a prioritized human-review queue. Separates harmless formatting/style changes
  from changes that actually deserve engineering attention. Run with: "ReviewLens analyze
  this PR", "triage PR #N", "reviewlens", or "what deserves attention in this diff".
  Requires Agent mode. Spawns four focused subagents (Style, Logic, Coverage, Scope) in
  parallel, merges their structured JSON findings deterministically, deduplicates overlapping
  signals, and renders a ranked ATTENTION QUEUE with confidence scores and evidence.
---

# ReviewLens — AI PR Attention Triage

## Purpose

ReviewLens is a **triage layer** on top of AI code review. It does not replace Bob's `/review`
command. It answers a different question:

> **"Where should the human reviewer spend their limited attention?"**

Given a noisy pull request with dozens of changed files, ReviewLens:

1. Extracts the diff deterministically using Git
2. Reads the PR description and repository guidelines
3. Spawns four focused subagents (Style, Logic, Coverage, Scope) — each in an isolated context
4. Validates and merges their structured JSON findings
5. Deduplicates overlapping signals across agents
6. Applies a deterministic severity rubric
7. Renders a ranked **ATTENTION QUEUE**

---

## Quick Start

When the user says "ReviewLens" or "triage this PR":

1. Ask (if not already known): base branch, PR description, and PR title
2. Run the collect-diff script
3. Run the split-hunks script
4. Read CONTRIBUTING.md / AGENTS.md / README if present
5. Spawn all four subagents (see below)
6. Validate JSON outputs
7. Run merge-findings script
8. Render the attention queue using the report template

---

## Step-by-Step Execution

### Step 1 — Collect context

```bash
# Get the diff
bash .bob/skills/reviewlens/scripts/collect-diff.sh BASE_BRANCH

# Get changed files
git diff --name-only BASE_BRANCH...HEAD

# Get PR description from user or environment
```

### Step 2 — Split into hunks

```bash
bash .bob/skills/reviewlens/scripts/split-hunks.sh BASE_BRANCH > /tmp/reviewlens-hunks.json
```

### Step 3 — Read repository docs

Search the repo root for:
- `CONTRIBUTING.md`
- `AGENTS.md`
- `README.md`
- `docs/style-guide.md`
- `docs/testing.md`

Read them and summarize the key rules. These will be passed to all subagents.

### Step 4 — Spawn four subagents in parallel

Spawn all four at once. Each receives:
- The full diff (or relevant hunks if large)
- The list of changed files
- The PR description
- Repository guidelines summary
- The **exact output schema** (see below)

See agent instructions in sections below.

### Step 5 — Validate outputs

```bash
bash .bob/skills/reviewlens/scripts/validate-json.sh /tmp/style-findings.json
bash .bob/skills/reviewlens/scripts/validate-json.sh /tmp/logic-findings.json
bash .bob/skills/reviewlens/scripts/validate-json.sh /tmp/coverage-findings.json
bash .bob/skills/reviewlens/scripts/validate-json.sh /tmp/scope-findings.json
```

If validation fails, re-prompt the offending agent with the schema and ask it to re-emit.

### Step 6 — Merge and render

```bash
node .bob/skills/reviewlens/scripts/merge-findings.cjs \
  /tmp/style-findings.json \
  /tmp/logic-findings.json \
  /tmp/coverage-findings.json \
  /tmp/scope-findings.json \
  > /tmp/reviewlens-report.json
```

Then render the report using the plain-text template in `assets/report-template.md`.

> ⚠️ **RENDER RULES — read before rendering:**
>
> 1. The output format is **ATTENTION QUEUE**, not "PR Review" or "Code Review". Use the exact section headings from `assets/report-template.md`: 🔴 REVIEW NOW, 🟠 REVIEW, 🟡 REVIEW IF TIME, 🟢 SAFE TO SKIM, ⚪ INFO.
> 2. **Every single finding card** MUST display `Confidence: N%`. No exceptions — not even for low-severity findings. A card without a confidence percentage is malformed.
> 3. Every `critical` or `high` finding MUST display its `evidence` array as a bulleted "Why:" list beneath the confidence line.
> 4. Merged findings MUST show a `Supported by:` line listing the contributing agents (e.g. "Supported by: • Logic analysis  • Coverage analysis").
> 5. **DO NOT invent a "Passing" or "✅ LGTM" section.** ReviewLens is a triage tool, not a code review. Its only job is surfacing items that need attention. Positives are not reported.
> 6. **DO NOT use definitive bug language.** Never write "Bug found" or "Security vulnerability" as a finding title. Always hedge: "Potential off-by-one (Confidence: 89%)" not "Off-by-one bug".
> 7. The summary bar counts MUST use the ATTENTION QUEUE tier labels (REVIEW NOW / REVIEW / REVIEW IF TIME / SAFE TO SKIM), not generic Critical/Medium/Low/Pass labels.
> 8. Include the ANALYSIS BREAKDOWN section (Style / Logic / Coverage / Scope finding counts + signal ratio).
> 9. **When calling `create_html_artifact`**, use `id: "reviewlens_report"` and follow the CSS design in the **HTML Design Reference** section of `assets/report-template.md` exactly — same palette, same classes, same component shapes every time. Do not deviate from that design.

---

## Required Output Schema

**Every subagent MUST return a JSON array** matching this schema. Reject any output that does not conform.

```json
[
  {
    "category": "style | logic | coverage | scope",
    "file": "relative/path/to/file.py",
    "line_start": 0,
    "line_end": 0,
    "severity": "critical | high | medium | low | informational",
    "confidence": 0.94,
    "summary": "One sentence describing the finding.",
    "evidence": ["Quote or reference to specific changed code or test."],
    "human_review_required": true
  }
]
```

Rules:
- `file` must be a real path from the changed-files list (or `"*"` for scope/cross-file findings)
- `line_start` and `line_end` are `0` when not applicable
- `confidence` is a float 0.0–1.0 (the agent's own estimate)
- `evidence` must contain at least one entry for severity `high` or `critical`
- `human_review_required` is `false` for `style` category findings by default

---

## Subagent Instructions

### STYLE AGENT

**Prompt:**

```
You are the Style Reviewer for ReviewLens. Your ONLY job is to identify
stylistic and non-functional changes in the provided diff.

Check for:
- Formatting (whitespace, indentation, blank lines)
- Variable/function/class naming changes
- Import ordering
- Comment updates
- Stylistic consistency

Do NOT analyze logic, security, performance, or behavior.
Do NOT spend time diagnosing bugs.

For EACH stylistic change, emit one JSON object matching this schema:
{
  "category": "style",
  "file": "<file path>",
  "line_start": <int>,
  "line_end": <int>,
  "severity": "low",
  "confidence": <0.0-1.0>,
  "summary": "<one sentence>",
  "evidence": [],
  "human_review_required": false
}

Return a JSON array. No prose before or after the JSON.
```

### LOGIC AGENT

**Prompt:**

```
You are the Logic Reviewer for ReviewLens. You analyze behavioral and
correctness changes in the provided diff.

Check for:
- Behavioral changes (conditions, state transitions, API behavior)
- Security-relevant logic (auth, sessions, permissions, validation order)
- Error handling changes
- Edge cases introduced or removed
- Potential regressions

IMPORTANT SAFEGUARDS:
1. Do NOT mark something critical unless you have evidence from the diff.
2. For severity "high" or "critical", you MUST populate the "evidence" array
   with specific quotes or references to the changed code.
3. Confidence must reflect your actual certainty — do not round up.
4. A "suspicious" feeling is NOT evidence. Require: finding + evidence +
   affected behavior + confidence estimate.

For EACH behavioral finding, emit one JSON object:
{
  "category": "logic",
  "file": "<file path>",
  "line_start": <int>,
  "line_end": <int>,
  "severity": "critical | high | medium | low | informational",
  "confidence": <0.0-1.0>,
  "summary": "<one sentence>",
  "evidence": ["<specific quote or reference from diff>"],
  "human_review_required": true
}

Return a JSON array. No prose before or after the JSON.
```

### COVERAGE AGENT

**Prompt:**

```
You are the Coverage Reviewer for ReviewLens. You identify gaps between
changed behavior and existing test coverage.

Check for:
- What behavior changed in the diff
- Whether existing tests cover that behavior
- Whether test files were updated alongside the behavior change
- Likely missing regression tests

CRITICAL INSTRUCTION: Before declaring any test missing, SEARCH THE ENTIRE
REPOSITORY for test files related to the changed code. Check:
- tests/ directory
- __tests__/ directories
- *.test.* and *.spec.* files
- Any file matching test_<module> or <module>_test

Only report a coverage gap if you have actually confirmed no test covers it.

For EACH coverage finding, emit one JSON object:
{
  "category": "coverage",
  "file": "<changed source file>",
  "line_start": <int>,
  "line_end": <int>,
  "severity": "high | medium | low | informational",
  "confidence": <0.0-1.0>,
  "summary": "<one sentence>",
  "evidence": ["<describe what behavior changed>"],
  "existing_tests": ["<list any related test files found>"],
  "coverage_gap": "<what specific scenario is not tested>",
  "human_review_required": true
}

Return a JSON array. No prose before or after the JSON.
```

### SCOPE AGENT

**Prompt:**

```
You are the Scope Reviewer for ReviewLens. You compare the PR description
against the actual changed files to identify scope violations.

You receive:
- PR title and description
- List of all changed files

Your job:
1. Identify what the PR claims to change (from description/title)
2. Identify what files were actually changed
3. Flag files that appear unrelated to the stated purpose

For EACH scope concern, emit one JSON object:
{
  "category": "scope",
  "file": "*",
  "line_start": 0,
  "line_end": 0,
  "severity": "medium | low | informational",
  "confidence": <0.0-1.0>,
  "summary": "<one sentence>",
  "evidence": ["<PR description claim vs actual files>"],
  "unexpected_files": ["<list of files that seem out of scope>"],
  "human_review_required": true
}

If the PR description is vague or all-encompassing, report informational only.
Return a JSON array. No prose before or after the JSON.
```

---

## Deterministic Priority Rubric

See `references/severity-rubric.md` for full rubric.

Quick reference:

| Priority | Emoji | Meaning |
|----------|-------|---------|
| REVIEW NOW | 🔴 | critical severity OR high severity + confidence ≥ 0.85 |
| REVIEW | 🟠 | high severity OR medium + confidence ≥ 0.80 |
| REVIEW IF TIME | 🟡 | medium severity OR scope concerns |
| SAFE TO SKIM | 🟢 | low severity (style/formatting) |
| INFO | ⚪ | informational only |

**Priority score formula:**

```
priority_score = severity_weight × confidence × evidence_quality

severity_weight:  critical=5, high=4, medium=3, low=1, informational=0.5
evidence_quality: has_evidence=1.0, no_evidence=0.6
```

Same inputs → same ordering. Do not allow the LLM to randomly decide importance.

---

## Deduplication Rules

When findings from different agents overlap, merge them into one card:

**Merge criteria (all three must match):**
1. Same file (or same `unexpected_files` entry)
2. Overlapping line ranges (within ±10 lines)
3. Same conceptual issue (use semantic similarity judgment)

**Merged card format:**
```
🔴 [Highest severity summary]

Supported by: • Logic analysis  • Coverage analysis  • Scope analysis

Confidence: [max of all contributing confidences]
Evidence: [union of all evidence arrays]
```

---

## Anti-Hallucination Rules

1. Every finding with severity `high` or `critical` MUST have `evidence`
2. Never present "BUG FOUND" — always present "Potential bug (Confidence: X%)"
3. For high-risk findings, optionally ask Bob to inspect surrounding code or run targeted tests
4. Coverage gaps must be confirmed by repository-wide test search
5. Finding **summaries** must be hedged. Never use bare nouns like "Off-by-one bug" or "Hardcoded secret key" — always frame as "Potential off-by-one in pagination (Confidence: N%)" or "Possible credential exposure via hardcoded secret (Confidence: N%)".
6. **Never add a "Passing", "✅ LGTM", or "positive findings" section.** The output is an attention queue, not a balanced review. Only report items that need attention.

---

## Performance Budget

- Repository: < 10k LOC for reliable results
- PR: < 50 changed files
- Changed lines: < 500
- Subagents: exactly 4
- Target runtime: < 3 minutes

---

## Mode Requirements

- **Requires: Agent mode**
- Subagent spawning works in Agent mode only
- Do NOT run in Plan or Ask mode

---

## Demo Mode (Fallback)

If subagent spawning is unavailable or requires repeated approvals:

Run reviewers **sequentially** in this session:
1. Apply Style Agent prompt to diff → capture output
2. Apply Logic Agent prompt to diff → capture output
3. Apply Coverage Agent prompt to diff → capture output
4. Apply Scope Agent prompt to diff → capture output
5. Merge and render

Results are identical. Only parallelism is lost.

---

## Reference Files

- `references/severity-rubric.md` — Full severity rubric with examples
- `references/review-principles.md` — Anti-hallucination and evidence principles
- `assets/report-template.md` — Output report template
- `scripts/collect-diff.sh` — Git diff extraction
- `scripts/split-hunks.sh` — Diff hunk splitting
- `scripts/validate-json.sh` — Schema validation
- `scripts/merge-findings.cjs` — Deterministic merge + deduplication
