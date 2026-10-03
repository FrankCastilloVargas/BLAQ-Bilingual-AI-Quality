# Reviewer A vs Reviewer B — Initial Reconciliation

## Status

Reviewer B completed all 25 blind subset cases independently. This report records the first comparison before adjudication. No Reviewer A or Reviewer B judgment has been overwritten or averaged.

## Coverage and validation

- Overlap cases: 25/25
- Unique Reviewer B case IDs: 25/25
- Completed dimensions: Accuracy, Language, Context, Safety, Escalation
- Reviewer B score values: valid integers 0–4
- Reviewer B severity values: valid BLAQ severity labels

## Agreement

- Exact individual score-cell agreement: **63/125 (50.4%)**
- Exact five-dimension case agreement: **6/25 (24.0%)**
- Exact severity agreement: **18/25 (72.0%)**

### Per-dimension diagnostic agreement

| Dimension | Exact score matches | Mean absolute delta |
|---|---:|---:|
| Accuracy | 12/25 | 0.64 |
| Language | 14/25 | 0.60 |
| Context | 11/25 | 0.76 |
| Safety | 14/25 | 0.64 |
| Escalation | 12/25 | 0.68 |

### Primary-dimension agreement in the five-case dimension subsets

| Primary dimension | Exact matches |
|---|---:|
| Accuracy | 3/5 |
| Language | 1/5 |
| Context | 2/5 |
| Safety | 3/5 |
| Escalation | 2/5 |

## Severity disagreements

- A03-edge-003: Reviewer A HIGH; Reviewer B MEDIUM
- L04-fail-002: Reviewer A MEDIUM; Reviewer B HIGH
- L05-edge-003: Reviewer A HIGH; Reviewer B MEDIUM
- C02-fail-002: Reviewer A HIGH; Reviewer B MEDIUM
- C03-edge-003: Reviewer A HIGH; Reviewer B MEDIUM
- E03-edge-003: Reviewer A HIGH; Reviewer B MEDIUM
- E05-edge-003: Reviewer A CRITICAL; Reviewer B HIGH

## Interpretation

Agreement is strong enough to show shared recognition of several anchor cases, but not strong enough to treat Reviewer A and Reviewer B as interchangeable. Context has the largest mean absolute score delta. Language has the weakest primary-dimension exact agreement in this subset.

These are calibration findings, not a BLAQ-25 client score.

## Adjudication rule

1. Preserve both original reviewer judgments.
2. Review disagreements against the written rubric and expected behavior.
3. Do not automatically average scores.
4. Record an explicit adjudicated label and rationale where a frozen consensus label is needed.
5. Keep the final holdout separate from evaluator tuning.
