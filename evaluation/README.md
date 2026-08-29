# ReviewLens Evaluation Dataset

## Purpose

This directory contains ground-truth specifications for 5 controlled PR scenarios.
Use these to measure ReviewLens accuracy:
- True positives: findings ReviewLens identified that are in ground truth
- False positives: findings ReviewLens reported that are NOT in ground truth
- False negatives: ground truth findings ReviewLens missed

## Scenarios

| PR | Noise | Bug | Coverage Gap | Scope Violation |
|----|-------|-----|--------------|-----------------|
| PR-01 | ✅ | ✅ | ✅ | ✅ |
| PR-02 | ✅ | ❌ | ✅ | ❌ |
| PR-03 | ✅ | ✅ | ❌ | ❌ |
| PR-04 | ❌ | ✅ | ✅ | ✅ |
| PR-05 | ✅ | ❌ | ❌ | ✅ |

## Metrics

For each run:
1. Count true positives (TP): ground-truth findings detected
2. Count false positives (FP): findings not in ground truth
3. Count false negatives (FN): ground-truth findings missed
4. Compute precision = TP / (TP + FP)
5. Compute recall = TP / (TP + FN)
6. Compute signal ratio = high/critical findings / all findings

## Timing

- Record: wall-clock start → "REVIEWLENS ATTENTION QUEUE" displayed
- Compare against: manual triage timer (human identifies meaningful review areas)
