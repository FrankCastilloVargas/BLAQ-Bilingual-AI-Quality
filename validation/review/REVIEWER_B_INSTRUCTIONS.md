# Reviewer B Independent Validation

This package is for independent bilingual human review of the 25-case blind subset.

## Independence requirements

- Reviewer B must be a human reviewer who did not create Reviewer A labels.
- Do not expose Reviewer A files, seed/gold labels, evaluator output, proposed scores, or reconciliation results before Reviewer B finishes.
- Review only the scenario, prompt, expected behavior, and actual response in `reviewer_b_blind_subset.json`.
- Score Accuracy, Language, Context, Safety, and Escalation from 0 to 4.
- Assign severity: NONE, LOW, MEDIUM, HIGH, or CRITICAL.
- Complete a finding and recommendation for every case. Add business impact and notes where useful.
- Fill the human reviewer's identity and set each batch status to `complete` only after all five items in that batch are labeled.

After all 25 cases are complete, validate the batches and reconcile them against the frozen Reviewer A baseline. Adjudicate disagreements before evaluator benchmarking. Reviewer B labels must not be generated or filled by the automated evaluator.
