#!/usr/bin/env bash
# ReviewLens — collect-diff.sh
# Usage: bash collect-diff.sh [BASE_BRANCH]
# Extracts the PR diff, changed files, and metadata for ReviewLens.
# Outputs to /tmp/reviewlens-diff.txt and /tmp/reviewlens-files.txt

set -e

BASE_BRANCH="${1:-main}"
HEAD_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
REPO_ROOT="$(git rev-parse --show-toplevel)"

echo "ReviewLens: Collecting diff from ${BASE_BRANCH}...${HEAD_BRANCH}" >&2
echo "Repo root: ${REPO_ROOT}" >&2

# Validate we are in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "ERROR: Not inside a git repository." >&2
  exit 1
fi

# Validate base branch exists
if ! git rev-parse --verify "origin/${BASE_BRANCH}" > /dev/null 2>&1 && \
   ! git rev-parse --verify "${BASE_BRANCH}" > /dev/null 2>&1; then
  echo "ERROR: Base branch '${BASE_BRANCH}' not found locally or in origin." >&2
  exit 1
fi

# Resolve base ref
BASE_REF="${BASE_BRANCH}"
if git rev-parse --verify "origin/${BASE_BRANCH}" > /dev/null 2>&1; then
  BASE_REF="origin/${BASE_BRANCH}"
fi

# Extract full diff
git diff "${BASE_REF}...HEAD" > /tmp/reviewlens-diff.txt
echo "Diff written to /tmp/reviewlens-diff.txt ($(wc -l < /tmp/reviewlens-diff.txt) lines)" >&2

# Extract changed file list
git diff --name-only "${BASE_REF}...HEAD" > /tmp/reviewlens-files.txt
echo "Changed files written to /tmp/reviewlens-files.txt ($(wc -l < /tmp/reviewlens-files.txt) files)" >&2

# Extract stat summary
git diff --stat "${BASE_REF}...HEAD" > /tmp/reviewlens-stat.txt
echo "Stat summary written to /tmp/reviewlens-stat.txt" >&2

# Count changed lines
INSERTIONS=$(git diff --stat "${BASE_REF}...HEAD" | tail -1 | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)
DELETIONS=$(git diff --stat "${BASE_REF}...HEAD" | tail -1 | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
CHANGED_FILES=$(wc -l < /tmp/reviewlens-files.txt)

echo ""
echo "=== ReviewLens Diff Summary ==="
echo "Base:          ${BASE_REF}"
echo "Head:          ${HEAD_BRANCH}"
echo "Changed files: ${CHANGED_FILES}"
echo "Insertions:    ${INSERTIONS}"
echo "Deletions:     ${DELETIONS}"
echo "==============================="
