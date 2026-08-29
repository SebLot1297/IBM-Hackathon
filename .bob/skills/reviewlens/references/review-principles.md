# ReviewLens Review Principles

## Core Principle: Triage, Not Review

ReviewLens is a **triage layer**. Its output answers:

> "Where should the human reviewer spend their limited attention?"

It is NOT a replacement for Bob's `/review` command. It does not fix code.
It does not merge PRs. It is read-only, deterministic, and human-in-the-loop.

---

## Anti-Hallucination Rules

### Rule 1: Evidence Required for High/Critical

Any finding with `severity = high` or `severity = critical` MUST include at least
one entry in the `evidence` array. The evidence must:
- Quote or reference specific lines from the diff
- Describe the before/after behavioral change
- Not be a vague restatement of the summary

**Bad evidence:**
```json
"evidence": ["This looks suspicious."]
```

**Good evidence:**
```json
"evidence": [
  "Old: token validated before user lookup (line 71-75)",
  "New: user lookup occurs before token validation (line 84-91)",
  "Unauthenticated requests now reach database query logic"
]
```

### Rule 2: Never "BUG FOUND"

Never output definitive bug declarations. Always hedge with confidence.

| ❌ Never write | ✅ Always write |
|----------------|----------------|
| BUG FOUND | Potential bug (Confidence: 89%) |
| SECURITY VULNERABILITY | Possible authentication bypass (Confidence: 94%) |
| THIS IS WRONG | Behavioral change may cause regression (Confidence: 72%) |

### Rule 3: Confidence Must Be Honest

Do not round up confidence to appear more authoritative.
- If you are 70% sure, say 70%.
- If you are 50% sure, say 50%.
- If you are less than 40% sure, drop the finding or mark informational.

### Rule 4: Test Search Before Coverage Claims

Before claiming "no test exists for X":
1. Search `tests/` directory
2. Search `__tests__/` directories
3. Search for `*.test.*` and `*.spec.*` files
4. Search for `test_<module>` and `<module>_test` patterns
5. Only report a gap if no relevant test was found

### Rule 5: Scope Findings Need PR Description

The Scope Agent must quote the PR description in its evidence. A scope finding
without the PR description as reference is not a valid scope finding.

---

## Signal vs. Noise Principle

The core product promise of ReviewLens is **signal ratio**:

```
signal ratio = useful findings / all findings
```

A ReviewLens session that returns 50 findings of equal weight has failed.
The goal is:
- Collapse noise (style, formatting) into one summary
- Surface 1–5 genuinely important findings
- Rank them so the engineer knows where to start

---

## What Each Agent Is Responsible For

| Agent | Question | Not responsible for |
|-------|----------|---------------------|
| Style | Is this change non-functional? | Logic, security, tests |
| Logic | Does behavior change in a risky way? | Formatting, tests, scope |
| Coverage | Is changed behavior adequately tested? | Logic correctness, style |
| Scope | Does the diff match the PR description? | Code quality, tests |

Agents must stay in their lane. A Style Agent that starts flagging logic bugs
is wrong — that's the Logic Agent's job, and double-reporting creates noise.

---

## Deduplication Principle

When multiple agents flag the same issue from different angles, merge them.

**Three-agent merge example:**
- Logic: "Authentication validation order changed"
- Coverage: "No test for new authentication path"
- Scope: "Auth code changed in UI-only PR"

These become ONE card:
```
🔴 Potential authentication regression

Supported by: • Logic analysis  • Coverage analysis  • Scope analysis
Confidence: 94%
Evidence: [combined evidence from all three agents]
```

This is stronger than three separate cards. It shows convergent signals.

---

## Repository Guidelines Integration

If the repository has CONTRIBUTING.md, AGENTS.md, or similar docs with rules,
ReviewLens MUST incorporate them:

1. Read the docs during the main agent step
2. Pass relevant rules to subagents as context
3. When a finding relates to a documented rule, cite the rule

**Example:**
```
Finding: Missing regression test for auth change

CONTRIBUTING.md rule: "Authentication changes require regression tests,
security review, and changelog entry."

This finding is supported by repository policy.
```

This turns ReviewLens from a generic linter into a **repository-aware** triage tool.

---

## Human-in-the-Loop Design

ReviewLens never:
- Modifies code
- Creates commits
- Merges PRs
- Applies fixes
- Opens issues automatically

ReviewLens always:
- Produces a prioritized queue
- Explains WHY each item matters
- Provides evidence
- Leaves the decision to the engineer

The workflow is: Analyze → Prioritize → Explain → Human decides.
