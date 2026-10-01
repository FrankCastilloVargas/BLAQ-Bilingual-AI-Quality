# Gold Set v0.1 Protocol

Gold Set v0.1 uses all 25 official BLAQ-25 scenarios with three synthetic response variants per test: compliant, substantive failure, and difficult/edge-adversarial. This yields 75 cases and 15 cases per primary BLAQ dimension.

## Important limitation

All v0.1 labels are **seed labels**. They are authored calibration hypotheses, not independent ground truth and not evidence that BLAQ is validated. The generic score templates intentionally make the dataset easy to generate reproducibly; each case must be reviewed dimension-by-dimension before calibration metrics are used for external claims.

## Promotion process

1. Reviewer A independently scores every case without seeing evaluator output.
2. Reviewer B independently scores a representative subset, prioritizing HIGH/CRITICAL and ambiguous cases.
3. Disagreements are reconciled against the BLAQ rubric and documented expected behavior.
4. Replace generic findings, impacts, and recommendations with case-specific human labels.
5. Mark reconciled cases as consensus; promote the dataset to calibrated only after coverage and review checks pass.
6. Freeze the calibrated dataset before comparing rule-based, LLM-only, and hybrid evaluators.

Never tune an evaluator on the same cases used as the final holdout benchmark. A later dataset version should split development/calibration cases from a frozen holdout set.
