#!/usr/bin/env bash
# ReviewLens — split-hunks.sh
# Usage: bash split-hunks.sh [BASE_BRANCH]
# Splits the diff into logical hunks and emits JSON array to stdout.
# Each hunk includes: file, hunk_index, header, lines_added, lines_removed, content.

set -e

BASE_BRANCH="${1:-main}"

BASE_REF="${BASE_BRANCH}"
if git rev-parse --verify "origin/${BASE_BRANCH}" > /dev/null 2>&1; then
  BASE_REF="origin/${BASE_BRANCH}"
fi

# Use git diff with unified context, parse per-file hunks into JSON
python3 - "${BASE_REF}" <<'PYEOF'
import sys, subprocess, json, re

base_ref = sys.argv[1]

result = subprocess.run(
    ["git", "diff", f"{base_ref}...HEAD"],
    capture_output=True, text=True
)
diff_text = result.stdout

hunks = []
current_file = None
current_hunk = None
hunk_index = 0

for line in diff_text.splitlines():
    # New file header
    file_match = re.match(r'^diff --git a/.+ b/(.+)$', line)
    if file_match:
        if current_hunk:
            hunks.append(current_hunk)
            current_hunk = None
        current_file = file_match.group(1)
        hunk_index = 0
        continue

    # Hunk header
    hunk_match = re.match(r'^(@@ .+? @@.*)', line)
    if hunk_match and current_file:
        if current_hunk:
            hunks.append(current_hunk)
        hunk_index += 1
        current_hunk = {
            "file": current_file,
            "hunk_index": hunk_index,
            "header": hunk_match.group(1),
            "lines_added": 0,
            "lines_removed": 0,
            "content": []
        }
        continue

    if current_hunk is not None:
        if line.startswith('+') and not line.startswith('+++'):
            current_hunk["lines_added"] += 1
        elif line.startswith('-') and not line.startswith('---'):
            current_hunk["lines_removed"] += 1
        current_hunk["content"].append(line)

if current_hunk:
    hunks.append(current_hunk)

# Convert content lists to strings
for h in hunks:
    h["content"] = "\n".join(h["content"])

print(json.dumps(hunks, indent=2))
PYEOF
