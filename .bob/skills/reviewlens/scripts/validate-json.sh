#!/usr/bin/env bash
# ReviewLens — validate-json.sh
# Usage: bash validate-json.sh <findings-file.json>
# Validates that a subagent output conforms to the ReviewLens finding schema.
# Exits 0 if valid, 1 if invalid (prints errors to stderr).

set -e

FILE="${1}"

if [ -z "${FILE}" ]; then
  echo "Usage: validate-json.sh <findings-file.json>" >&2
  exit 1
fi

if [ ! -f "${FILE}" ]; then
  echo "ERROR: File not found: ${FILE}" >&2
  exit 1
fi

python3 - "${FILE}" <<'PYEOF'
import sys, json

VALID_CATEGORIES = {"style", "logic", "coverage", "scope"}
VALID_SEVERITIES = {"critical", "high", "medium", "low", "informational"}

path = sys.argv[1]
errors = []

try:
    with open(path) as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"INVALID JSON: {e}", file=sys.stderr)
    sys.exit(1)

if not isinstance(data, list):
    print("ERROR: Root must be a JSON array", file=sys.stderr)
    sys.exit(1)

for i, finding in enumerate(data):
    prefix = f"Finding[{i}]"

    # Required fields
    for field in ["category", "file", "severity", "confidence", "summary", "human_review_required"]:
        if field not in finding:
            errors.append(f"{prefix}: Missing required field '{field}'")

    # Category validation
    cat = finding.get("category", "")
    if cat not in VALID_CATEGORIES:
        errors.append(f"{prefix}: Invalid category '{cat}'. Must be one of {VALID_CATEGORIES}")

    # Severity validation
    sev = finding.get("severity", "")
    if sev not in VALID_SEVERITIES:
        errors.append(f"{prefix}: Invalid severity '{sev}'. Must be one of {VALID_SEVERITIES}")

    # Confidence validation
    conf = finding.get("confidence", None)
    if conf is not None:
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            errors.append(f"{prefix}: 'confidence' must be a float between 0.0 and 1.0, got {conf}")

    # Evidence required for high/critical
    sev_level = finding.get("severity", "")
    evidence = finding.get("evidence", [])
    if sev_level in ("high", "critical") and (not evidence or len(evidence) == 0):
        errors.append(f"{prefix}: Severity '{sev_level}' requires at least one evidence entry")

    # human_review_required must be bool
    hrr = finding.get("human_review_required")
    if not isinstance(hrr, bool):
        errors.append(f"{prefix}: 'human_review_required' must be true or false")

if errors:
    print(f"\n❌ VALIDATION FAILED for {path}:", file=sys.stderr)
    for e in errors:
        print(f"  • {e}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"✅ VALID: {path} ({len(data)} finding(s))")
    sys.exit(0)
PYEOF
