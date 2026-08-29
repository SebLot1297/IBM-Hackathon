# ReviewLens Severity Rubric

## Priority Tiers

### 🔴 REVIEW NOW — Critical

**Trigger:** `severity = critical` OR (`severity = high` AND `confidence ≥ 0.85`)

**Meaning:** Potential security issue, data loss, authentication bypass, major correctness
regression, or system availability risk.

**Examples:**
- Session validation order changed (auth bypass risk)
- Payment amount calculation altered
- Permissions check removed or reordered
- SQL injection surface introduced
- Cryptographic primitive replaced with weaker one
- Data written to wrong scope (e.g., public instead of private)

**Required:** Must have `evidence` array populated. Confidence must be explicit.

---

### 🟠 REVIEW — High

**Trigger:** `severity = high` OR (`severity = medium` AND `confidence ≥ 0.80`)

**Meaning:** Likely behavioral defect, meaningful regression, or untested change to
critical path.

**Examples:**
- Logic condition changed in non-trivial way
- Error handling removed or weakened
- State transition altered
- API response shape changed
- Missing regression test for changed authentication path
- Test for security-critical behavior removed

---

### 🟡 REVIEW IF TIME — Medium

**Trigger:** `severity = medium` OR scope concern regardless of confidence

**Meaning:** Human review is useful but not blocking. Scope violations, moderate coverage
gaps, non-obvious behavioral questions.

**Examples:**
- PR modifies files not mentioned in description
- Database migration in a UI-only PR
- Coverage gap for edge case in non-critical path
- Condition change with low blast radius

---

### 🟢 SAFE TO SKIM — Low

**Trigger:** `severity = low`

**Meaning:** Stylistic, cosmetic, or minor improvements. No behavioral risk.

**Examples:**
- Variable renamed for consistency
- Import ordering fixed
- Whitespace/formatting normalized
- Comment updated
- Unused import removed

**Policy:** Collapse all low-severity findings into a single summary card.
Do NOT show individual cards for each formatting change.

---

### ⚪ INFO — Informational

**Trigger:** `severity = informational`

**Meaning:** Context only. Not actionable. Reviewer may find it useful.

**Examples:**
- File touched but no meaningful change
- Dependency version bumped
- Configuration constant updated

---

## Priority Score Formula

Used by the merge script to sort findings within each tier:

```
priority_score = severity_weight × confidence × evidence_quality

severity_weight:
  critical      = 5.0
  high          = 4.0
  medium        = 3.0
  low           = 1.0
  informational = 0.5

evidence_quality:
  has one or more evidence entries = 1.0
  no evidence entries              = 0.6
```

**Rule:** Same inputs always produce the same ordering.
**Rule:** Never override this formula with subjective LLM judgment.

---

## Confidence Display

Always show confidence as a percentage rounded to nearest integer:

```
Confidence: 94%    ✅
Confidence: 0.94   ❌
Confidence: HIGH   ❌
BUG FOUND          ❌ (never use)
```

Confidence thresholds for display language:
- ≥ 90%: "Strong evidence of..."
- 70–89%: "Likely..."
- 50–69%: "Possible..."
- < 50%: "Uncertain — may warrant a second look"

---

## Collapse Rule for Style Findings

When there are 3 or more `low` severity style findings:
- Do NOT show individual cards
- Show one collapsed summary card:

```
🟢 SAFE TO SKIM

N formatting / naming changes
Collapsed into 1 summary.
Files: [list up to 5 files, then "+ N more"]
```
