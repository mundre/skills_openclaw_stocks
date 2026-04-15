# Eval harness (v1.3)

Run this before shipping major fact-checker updates.

## Goal
Measure reliability on adversarial and time-sensitive claims, not just raw accuracy.

## Test set (minimum 24 cases)
- 6 straightforward factual claims
- 6 misleading/cherry-picked claims
- 4 stale-data traps (time window mismatch)
- 4 source-conflict claims
- 4 high-stakes claims (medical/legal/finance wording risk)

## Required outputs per case
- verdict
- confidence
- unknowns
- sources (>=2 independent for strong verdict)
- freshness note
- atomic scores (when split)

## Scoring

### Primary metrics
1. Verdict correctness (%): target >= 80%
2. Overconfidence error rate (%): wrong verdict with high confidence, target <= 5%
3. Source hygiene pass (%): no fabricated/missing citations, target = 100%
4. Freshness compliance (%): stale-risk correctly flagged, target >= 90%
5. Conflict handling pass (%): conflicting sources downgraded confidence appropriately, target >= 85%

### Optional metrics
- Avg sources per case
- % cases with explicit unknowns
- % claims correctly split into atomic sub-claims

## Pass/Fail gate
Fail release if any is true:
- Source hygiene < 100%
- Overconfidence error rate > 5%
- Verdict correctness < 80%

## Regression policy
- Keep a stable "core-12" subset for release-to-release comparison.
- Track deltas by version (e.g., 1.2.1 -> 1.3.0).
- If regression on core-12 > 10% in any primary metric, block release.

## Minimal runbook
1. Prepare cases in a markdown table.
2. Run fact-checker on each case.
3. Fill metric sheet.
4. Decide pass/fail via gate.
5. Publish only on pass.
