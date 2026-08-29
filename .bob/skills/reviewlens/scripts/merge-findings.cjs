#!/usr/bin/env node
// ReviewLens — merge-findings.js
// Usage: node merge-findings.js style.json logic.json coverage.json scope.json
// Reads four finding files, deduplicates, scores, and renders the attention queue.

const fs = require('fs');
const path = require('path');

// ─── Config ─────────────────────────────────────────────────────────────────

const SEVERITY_WEIGHT = {
  critical: 5.0,
  high: 4.0,
  medium: 3.0,
  low: 1.0,
  informational: 0.5
};

const TIER = {
  CRITICAL: '🔴 REVIEW NOW',
  HIGH:     '🟠 REVIEW',
  MEDIUM:   '🟡 REVIEW IF TIME',
  LOW:      '🟢 SAFE TO SKIM',
  INFO:     '⚪ INFO'
};

// ─── Load findings ───────────────────────────────────────────────────────────

function loadFindings(filePath) {
  if (!fs.existsSync(filePath)) {
    console.error(`⚠️  File not found: ${filePath} — skipping`);
    return [];
  }
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) throw new Error('Not an array');
    return data;
  } catch (e) {
    console.error(`⚠️  Failed to parse ${filePath}: ${e.message} — skipping`);
    return [];
  }
}

// ─── Priority Score ──────────────────────────────────────────────────────────

function priorityScore(finding) {
  const sw = SEVERITY_WEIGHT[finding.severity] || 0.5;
  const conf = typeof finding.confidence === 'number' ? finding.confidence : 0.5;
  const eq = (finding.evidence && finding.evidence.length > 0) ? 1.0 : 0.6;
  return sw * conf * eq;
}

// ─── Assign Tier ─────────────────────────────────────────────────────────────

function assignTier(finding) {
  const sev = finding.severity;
  const conf = finding.confidence || 0;
  if (sev === 'critical') return 'CRITICAL';
  if (sev === 'high' && conf >= 0.85) return 'CRITICAL';
  if (sev === 'high') return 'HIGH';
  if (sev === 'medium' && conf >= 0.80) return 'HIGH';
  if (sev === 'medium') return 'MEDIUM';
  if (sev === 'scope' || finding.category === 'scope') return 'MEDIUM';
  if (sev === 'low') return 'LOW';
  return 'INFO';
}

// ─── Deduplication ───────────────────────────────────────────────────────────

function overlaps(a, b) {
  // Same file
  if (a.file !== b.file && a.file !== '*' && b.file !== '*') return false;
  // Nearby lines (within 10 lines)
  const aStart = a.line_start || 0;
  const aEnd = a.line_end || aStart;
  const bStart = b.line_start || 0;
  const bEnd = b.line_end || bStart;
  if (aStart > 0 && bStart > 0) {
    const distance = Math.max(aStart, bStart) - Math.min(aEnd, bEnd);
    if (distance > 10) return false;
  }
  return true;
}

function conceptuallySimilar(a, b) {
  // Simple keyword overlap heuristic
  const keywords = (s) => (s || '').toLowerCase()
    .split(/\W+/)
    .filter(w => w.length > 4);
  const akw = new Set(keywords(a.summary));
  const bkw = new Set(keywords(b.summary));
  let overlap = 0;
  for (const w of akw) { if (bkw.has(w)) overlap++; }
  return overlap >= 2;
}

function deduplicateFindings(findings) {
  const groups = [];

  for (const finding of findings) {
    let merged = false;
    for (const group of groups) {
      const rep = group.findings[0];
      if (overlaps(rep, finding) && conceptuallySimilar(rep, finding)) {
        group.findings.push(finding);
        merged = true;
        break;
      }
    }
    if (!merged) {
      groups.push({ findings: [finding] });
    }
  }

  // Collapse each group into one merged finding
  return groups.map(group => {
    if (group.findings.length === 1) return group.findings[0];

    const best = group.findings.sort((a, b) =>
      (SEVERITY_WEIGHT[b.severity] || 0) - (SEVERITY_WEIGHT[a.severity] || 0)
    )[0];

    const supportedBy = [...new Set(group.findings.map(f => f.category))];
    const allEvidence = group.findings.flatMap(f => f.evidence || []);
    const maxConf = Math.max(...group.findings.map(f => f.confidence || 0));

    return {
      ...best,
      confidence: maxConf,
      evidence: [...new Set(allEvidence)],
      supported_by: supportedBy,
      merged_count: group.findings.length
    };
  });
}

// ─── Render Report ───────────────────────────────────────────────────────────

function renderReport(allFindings, meta) {
  const tiered = {
    CRITICAL: [],
    HIGH: [],
    MEDIUM: [],
    LOW: [],
    INFO: []
  };

  for (const f of allFindings) {
    const tier = assignTier(f);
    tiered[tier].push(f);
  }

  // Sort each tier by priority score (descending)
  for (const tier of Object.keys(tiered)) {
    tiered[tier].sort((a, b) => priorityScore(b) - priorityScore(a));
  }

  const styleLow = allFindings.filter(f => f.category === 'style' && f.severity === 'low');
  const nonStyleFindings = allFindings.filter(f => !(f.category === 'style' && f.severity === 'low'));
  const highRiskCount = tiered.CRITICAL.length + tiered.HIGH.length;
  const signalRatio = allFindings.length > 0
    ? Math.round((highRiskCount / allFindings.length) * 100)
    : 0;

  const lines = [];
  const sep = '━'.repeat(54);

  lines.push(sep);
  lines.push('       REVIEWLENS ATTENTION QUEUE');
  if (meta.prTitle) lines.push(`       ${meta.prTitle}`);
  lines.push(sep);
  lines.push('');
  lines.push(`${meta.changedFiles || '?'} changed files · ${meta.changedLines || '?'} changed lines analyzed`);
  lines.push('');

  // Attention score
  lines.push('PR ATTENTION SCORE');
  lines.push(`High-risk changes:  ${highRiskCount}`);
  lines.push(`Low-signal changes: ${styleLow.length}`);
  lines.push(`Scope concerns:     ${allFindings.filter(f => f.category === 'scope').length}`);
  lines.push('');
  lines.push(sep);

  // Tier blocks
  function renderFinding(f) {
    const loc = f.line_start > 0 ? `:${f.line_start}` : '';
    lines.push('');
    lines.push(`${f.file}${loc}`);
    lines.push(f.summary);
    lines.push('');
    lines.push(`Confidence: ${Math.round((f.confidence || 0) * 100)}%`);
    if (f.supported_by && f.supported_by.length > 1) {
      lines.push(`Supported by: ${f.supported_by.map(c => `• ${c} analysis`).join('  ')}`);
    }
    if (f.evidence && f.evidence.length > 0) {
      lines.push('Why:');
      f.evidence.forEach(e => lines.push(`  ${e}`));
    }
    if (f.unexpected_files && f.unexpected_files.length > 0) {
      lines.push(`Unexpected files: ${f.unexpected_files.join(', ')}`);
    }
    lines.push('');
    lines.push(sep);
  }

  lines.push('');
  lines.push(TIER.CRITICAL);
  lines.push('');
  if (tiered.CRITICAL.length === 0) {
    lines.push('  (none)');
    lines.push('');
    lines.push(sep);
  } else {
    tiered.CRITICAL.forEach(renderFinding);
  }

  lines.push('');
  lines.push(TIER.HIGH);
  lines.push('');
  if (tiered.HIGH.length === 0) {
    lines.push('  (none)');
    lines.push('');
    lines.push(sep);
  } else {
    tiered.HIGH.forEach(renderFinding);
  }

  lines.push('');
  lines.push(TIER.MEDIUM);
  lines.push('');
  if (tiered.MEDIUM.length === 0) {
    lines.push('  (none)');
    lines.push('');
    lines.push(sep);
  } else {
    tiered.MEDIUM.forEach(renderFinding);
  }

  lines.push('');
  lines.push(TIER.LOW);
  lines.push('');
  if (styleLow.length === 0) {
    lines.push('  (none)');
  } else {
    const sampleFiles = [...new Set(styleLow.map(f => f.file))].slice(0, 5);
    const extra = Math.max(0, [...new Set(styleLow.map(f => f.file))].length - 5);
    lines.push(`${styleLow.length} formatting / naming changes`);
    lines.push('Collapsed into 1 summary.');
    lines.push(`Files: ${sampleFiles.join(', ')}${extra > 0 ? ` +${extra} more` : ''}`);
  }
  lines.push('');
  lines.push(sep);

  // Summary breakdown
  lines.push('');
  lines.push('ANALYSIS BREAKDOWN');
  lines.push('');
  const byCategory = {};
  for (const f of allFindings) {
    byCategory[f.category] = (byCategory[f.category] || 0) + 1;
  }
  const cats = ['style', 'logic', 'coverage', 'scope'];
  cats.forEach(c => {
    const count = byCategory[c] || 0;
    lines.push(`  ${c.padEnd(12)} ${String(count).padStart(2)} finding${count !== 1 ? 's' : ''}`);
  });
  lines.push('');
  lines.push(`  Total findings: ${allFindings.length}`);
  lines.push(`  Signal ratio:   ${signalRatio}%`);
  lines.push('');
  lines.push(sep);
  lines.push('ReviewLens — AI PR Attention Triage');
  lines.push('Powered by IBM Bob · Agent mode · 4 parallel reviewers');
  lines.push(sep);

  return lines.join('\n');
}

// ─── Main ────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node merge-findings.js style.json logic.json coverage.json scope.json [--pr-title="..."] [--files=N] [--lines=N]');
  process.exit(1);
}

// Parse flags
const jsonFiles = args.filter(a => !a.startsWith('--'));
const flags = Object.fromEntries(
  args.filter(a => a.startsWith('--')).map(a => {
    const [k, v] = a.replace('--', '').split('=');
    return [k, v || true];
  })
);

const meta = {
  prTitle: flags['pr-title'] || '',
  changedFiles: flags['files'] || '?',
  changedLines: flags['lines'] || '?'
};

// Load all findings
let allFindings = [];
for (const f of jsonFiles) {
  allFindings = allFindings.concat(loadFindings(f));
}

// Deduplicate
const deduped = deduplicateFindings(allFindings);

// Render
const report = renderReport(deduped, meta);
console.log(report);

// Also write JSON for downstream use
const reportData = {
  meta,
  total_findings: deduped.length,
  findings: deduped
};
fs.writeFileSync('/tmp/reviewlens-merged.json', JSON.stringify(reportData, null, 2));
