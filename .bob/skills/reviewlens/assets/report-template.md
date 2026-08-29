# ReviewLens Attention Queue Report

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

Confidence: {{CONFIDENCE_PCT}}%
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

Confidence: {{CONFIDENCE_PCT}}%
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

Confidence: {{CONFIDENCE_PCT}}%
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
