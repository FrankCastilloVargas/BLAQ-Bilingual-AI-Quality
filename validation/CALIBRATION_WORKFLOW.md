# Human Calibration Workflow

BLAQ calibration must keep evaluator output and seed gold labels hidden from Reviewer A during first-pass scoring.

## Reviewer A

Review each response against the scenario, prompt, expected behavior, and BLAQ 0-4 dimensions. Record all five scores, severity, finding, business impact, recommendation, and optional notes. Do not inspect model proposals or the seed label while scoring.

## Reviewer B

Independently review a representative subset, emphasizing ambiguous and HIGH/CRITICAL cases. Reviewer B should also be blind to evaluator output and Reviewer A's labels until their first pass is complete.

## Reconciliation

Only after both passes may disagreements be compared and reconciled. Reconciled labels can be marked consensus. Automated evaluator performance is measured only after labels are frozen.

The assistant may prepare cases, enforce schema, calculate agreement, and identify disagreements, but assistant-authored labels must not be represented as independent human ground truth.
