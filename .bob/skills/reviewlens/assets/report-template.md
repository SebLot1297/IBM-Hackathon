# ReviewLens Attention Queue Report

> ⚠️ **Template rules (apply EVERY time you render this report):**
> - Section headings are FIXED: use exactly 🔴 REVIEW NOW, 🟠 REVIEW, 🟡 REVIEW IF TIME, 🟢 SAFE TO SKIM, ⚪ INFO.
> - Every finding card MUST include `Confidence: N%`. Missing confidence = malformed card.
> - Do NOT add a "Passing", "✅ LGTM", or positive-findings section.
> - Summary bar uses tier labels (REVIEW NOW / REVIEW / REVIEW IF TIME / SAFE TO SKIM), NOT Critical/Medium/Low/Pass.
> - Finding titles must be hedged: "Potential X (Confidence: N%)" not "X bug" or "X vulnerability".

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       REVIEWLENS ATTENTION QUEUE
       {{PR_TITLE}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{CHANGED_FILES}} changed files · {{CHANGED_LINES}} changed lines analyzed

---

## ATTENTION SCORE

High-risk changes:   {{HIGH_RISK_COUNT}}
Low-signal changes:  {{LOW_SIGNAL_COUNT}}
Scope concerns:      {{SCOPE_CONCERN_COUNT}}

Overall: {{ATTENTION_LEVEL}}  (CRITICAL | HIGH | MEDIUM | LOW)

---

## 🔴 REVIEW NOW

{{#each CRITICAL_FINDINGS}}
{{FILE}}:{{LINE_START}}
{{SUMMARY}}

Confidence: {{CONFIDENCE_PCT}}%        ← REQUIRED — never omit
{{#if SUPPORTED_BY}}
Supported by: {{SUPPORTED_BY}}
{{/if}}
Why:
{{#each EVIDENCE}}
  • {{this}}
{{/each}}
{{#if CONTRIBUTING_RULE}}
Repository rule: {{CONTRIBUTING_RULE}}
{{/if}}

---
{{/each}}
{{#if NO_CRITICAL}}
  (none)
{{/if}}

## 🟠 REVIEW

{{#each HIGH_FINDINGS}}
{{FILE}}:{{LINE_START}}
{{SUMMARY}}

Confidence: {{CONFIDENCE_PCT}}%        ← REQUIRED — never omit
{{#if SUPPORTED_BY}}
Supported by: {{SUPPORTED_BY}}
{{/if}}
{{#each EVIDENCE}}
  • {{this}}
{{/each}}

---
{{/each}}
{{#if NO_HIGH}}
  (none)
{{/if}}

## 🟡 REVIEW IF TIME

{{#each MEDIUM_FINDINGS}}
{{FILE}}
{{SUMMARY}}

Confidence: {{CONFIDENCE_PCT}}%        ← REQUIRED — never omit
{{#if UNEXPECTED_FILES}}
Unexpected files: {{UNEXPECTED_FILES}}
{{/if}}

---
{{/each}}
{{#if NO_MEDIUM}}
  (none)
{{/if}}

## 🟢 SAFE TO SKIM

{{#if STYLE_COLLAPSED}}
{{STYLE_COUNT}} formatting / naming changes
Collapsed into 1 summary.
Files: {{STYLE_FILES_SAMPLE}}
{{/if}}

---

## ⚪ INFO

{{#each INFO_FINDINGS}}
{{FILE}}
{{SUMMARY}}

Confidence: {{CONFIDENCE_PCT}}%

---
{{/each}}
{{#if NO_INFO}}
  (none)
{{/if}}

---

## ANALYSIS BREAKDOWN

Style     {{STYLE_COUNT}} findings
Logic     {{LOGIC_COUNT}} findings
Coverage  {{COVERAGE_COUNT}} findings
Scope     {{SCOPE_COUNT}} findings

Total findings: {{TOTAL_COUNT}}
Signal ratio:   {{SIGNAL_RATIO}}% (high/critical findings / all findings)

Runtime:  {{RUNTIME}}s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ReviewLens — AI PR Attention Triage
Powered by IBM Bob · Agent mode · 4 parallel reviewers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
