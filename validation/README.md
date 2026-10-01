# BLAQ Validation

This directory contains frozen evaluator-validation datasets. Human labels are ground truth for comparison; model output must never rewrite them.

Dataset status meanings:
- **seed**: authored calibration examples; not independent evidence of validity.
- **calibrated**: reviewed independently and reconciled.
- **validated**: reserved for a dataset that meets the project's documented validation protocol.

The initial gold set is intentionally small. It proves the harness, not BLAQ's commercial validity. Expand it with balanced typical, edge, and adversarial cases across all five BLAQ dimensions and EN/es-MX before making performance claims.

Run locally with the default token-free evaluator:

    python scripts/run_validation.py

Run the configured hybrid evaluator by setting BLAQ_EVALUATOR=hybrid-openai and the required runtime credentials. Results are written as JSON and should be compared across evaluator/model/prompt versions.
