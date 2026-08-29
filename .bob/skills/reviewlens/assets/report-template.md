# ReviewLens Attention Queue Report

> ⚠️ **Template rules (apply EVERY time you render this report):**
> - Section headings are FIXED: use exactly 🔴 REVIEW NOW, 🟠 REVIEW, 🟡 REVIEW IF TIME, 🟢 SAFE TO SKIM, ⚪ INFO.
> - Every finding card MUST include `Confidence: N%`. Missing confidence = malformed card.
> - Do NOT add a "Passing", "✅ LGTM", or positive-findings section.
> - Summary bar uses tier labels (REVIEW NOW / REVIEW / REVIEW IF TIME / SAFE TO SKIM), NOT Critical/Medium/Low/Pass.
> - Finding titles must be hedged: "Potential X (Confidence: N%)" not "X bug" or "X vulnerability".
> - When rendering as `create_html_artifact`, use `id: "reviewlens_report"` and apply the CSS design in the **HTML Design Reference** section below — same classes, same palette, same layout every time.

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

---

## HTML Design Reference

When rendering as `create_html_artifact`, the HTML output MUST use exactly this CSS and structure — no deviations to palette, spacing, or component shapes. The plain-text content above maps to these HTML components:

**CSS (inline in `<style>` block):**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2328;
  background: #ffffff;
  padding: 32px 16px 48px;
}
.wrap { max-width: 760px; margin: 0 auto; }

.header {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #f7f8fa;
  padding: 20px 24px 18px;
  margin-bottom: 24px;
}
.header-label {
  font-size: 11px; font-weight: 600; letter-spacing: .08em;
  color: #57606a; text-transform: uppercase; margin-bottom: 4px;
}
.header-title { font-size: 17px; font-weight: 700; color: #1f2328; margin-bottom: 6px; }
.header-meta  { font-size: 12px; color: #57606a; }

.summary-bar {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 10px; margin-bottom: 24px;
}
.summary-cell { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px 14px; text-align: center; }
.summary-cell .count { font-size: 24px; font-weight: 700; }
.summary-cell .label { font-size: 11px; color: #57606a; margin-top: 2px; letter-spacing: .04em; }
.s-red    { border-left: 4px solid #e53e3e; }
.s-orange { border-left: 4px solid #dd6b20; }
.s-yellow { border-left: 4px solid #d69e2e; }
.s-green  { border-left: 4px solid #38a169; }

.attn-score {
  border: 1px solid #e5e7eb; border-radius: 6px; background: #f7f8fa;
  padding: 14px 24px; margin-bottom: 28px;
  display: flex; align-items: center; gap: 16px;
}
.attn-badge {
  font-size: 12px; font-weight: 700; letter-spacing: .06em;
  color: #fff; padding: 3px 10px; border-radius: 4px;
}
/* Badge color by attention level — pick one: */
/* CRITICAL */ .attn-badge { background: #e53e3e; }
/* HIGH     */ .attn-badge { background: #dd6b20; }
/* MEDIUM   */ .attn-badge { background: #d69e2e; }
/* LOW      */ .attn-badge { background: #38a169; }
.attn-detail { font-size: 12px; color: #57606a; }

.section-heading {
  font-size: 13px; font-weight: 700; letter-spacing: .04em;
  margin: 28px 0 12px; padding-bottom: 6px;
  border-bottom: 2px solid #e5e7eb;
}

.card { border: 1px solid #e5e7eb; border-radius: 6px; margin-bottom: 12px; overflow: hidden; }
.card-header {
  padding: 11px 16px 10px; background: #f7f8fa;
  border-bottom: 1px solid #e5e7eb;
  display: flex; align-items: flex-start; gap: 10px;
}
.card-emoji { font-size: 15px; flex-shrink: 0; margin-top: 1px; }
.card-title { font-size: 13px; font-weight: 600; color: #1f2328; flex: 1; }
.card-file  { font-size: 11px; color: #57606a; font-family: "Consolas","SFMono-Regular",monospace; margin-top: 2px; }
.card-body  { padding: 11px 16px 12px; }
.confidence-line { font-size: 12px; color: #57606a; margin-bottom: 6px; }
.conf-val        { font-weight: 700; color: #1f2328; }
.supported-line  { font-size: 12px; color: #57606a; margin-bottom: 6px; }
.why-label { font-size: 12px; font-weight: 600; color: #1f2328; margin-bottom: 4px; }
.why-list  { list-style: none; padding: 0; margin: 0 0 0 4px; }
.why-list li { font-size: 12px; color: #1f2328; padding: 2px 0 2px 14px; position: relative; }
.why-list li::before { content: "•"; position: absolute; left: 0; color: #57606a; }
.rule-line { font-size: 11px; color: #57606a; margin-top: 6px; font-style: italic; }

.collapsed-card {
  border: 1px solid #e5e7eb; border-radius: 6px;
  padding: 12px 16px; background: #f7f8fa;
  font-size: 12px; color: #57606a;
}
.collapsed-card strong { color: #1f2328; }

.breakdown-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
.breakdown-table td { padding: 5px 0; font-size: 13px; }
.breakdown-table td:first-child  { color: #57606a; width: 100px; }
.breakdown-table td:nth-child(2) { font-weight: 600; width: 50px; }
.breakdown-bar  { height: 8px; background: #e5e7eb; border-radius: 4px; margin-top: 1px; overflow: hidden; }
.breakdown-fill { height: 100%; border-radius: 4px; }

.footer {
  margin-top: 48px; padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  text-align: center; font-size: 12px; color: #57606a;
}
```

**HTML structure map (plain-text section → HTML component):**

| Plain-text element | HTML component |
|---|---|
| Header block (title + meta) | `<div class="header">` with `.header-label`, `.header-title`, `.header-meta` |
| Summary counts (REVIEW NOW / REVIEW / REVIEW IF TIME / SAFE TO SKIM) | `<div class="summary-bar">` with four `.summary-cell` + `.s-red/.s-orange/.s-yellow/.s-green` |
| ATTENTION SCORE line | `<div class="attn-score">` with `.attn-badge` + `.attn-detail` |
| Section headings (🔴 REVIEW NOW etc.) | `<div class="section-heading">` |
| Each finding card | `<div class="card">` with `.card-header` (emoji + title + file) and `.card-body` (confidence, supported-by, why-list, rule-line) |
| SAFE TO SKIM collapsed block | `<div class="collapsed-card">` |
| ANALYSIS BREAKDOWN | `<table class="breakdown-table">` with `.breakdown-bar` / `.breakdown-fill` per row |
| Footer banner (━━━ ReviewLens ━━━) | `<div style="...monospace...">` block + `<div class="footer">Made with IBM Bob</div>` |

**Breakdown bar colors:**
- Style → `background: #38a169`
- Logic → `background: #e53e3e`
- Coverage → `background: #dd6b20`
- Scope → `background: #d69e2e`

**Bar width formula:** scale relative to the largest category count, max 100%.
