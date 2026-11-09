# BLAQ — Bilingual Language & AI Quality

BLAQ is a human-in-the-loop quality assurance framework for evaluating bilingual AI systems in English and Mexican Spanish.

## MVP v0.1

The first release evaluates AI responses across five dimensions:

- Accuracy
- Language Quality
- Context
- Safety
- Escalation

BLAQ-25 contains 25 test types (5 per dimension). Automated evaluation is advisory: a bilingual human reviewer approves the final finding.

## Core workflow

```
Create Audit -> Add AI Response -> Evaluate -> Human Review -> Approve -> Report
```

## Tech stack

- Python 3.11+
- FastAPI
- Pydantic
- Pytest
- JSON test library

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Testing

```bash
pytest
```

## Status

Early MVP / validation stage. The scoring framework is an operational QA rubric and is not represented as a scientifically validated benchmark.

## License

All rights reserved unless a license is added later.


## Sprint 2 — Audit flow

The MVP now includes:

- 25 concrete bilingual EN/es-MX QA scenarios in `data/blaq25.json`
- JSON persistence for audit records under `data/audits/`
- `POST /audits` to create and persist an audit
- `GET /audits` and `GET /audits/{audit_id}` to retrieve audits
- `POST /evaluations/score` for a single response score
- `POST /evaluations/audit-summary` for an aggregate BLAQ result
- Aggregate scoring based only on human-approved evaluations
- Explicit HIGH/CRITICAL finding visibility independent of the numeric score

The included scenarios describe a fictional customer-service environment. They are templates and must be customized against a real client's documented policies before a paid audit.


## Frozen-consensus evaluator benchmark

The 25-case calibration subset is frozen separately from evaluator predictions. To run a live Hybrid/OpenAI benchmark, configure the evaluator explicitly and keep credentials out of the repository:

```bash
export BLAQ_EVALUATOR=hybrid-openai
export OPENAI_API_KEY=...
python scripts/run_live_benchmark.py
```

On PowerShell:

```powershell
$env:BLAQ_EVALUATOR="hybrid-openai"
$env:OPENAI_API_KEY="..."
python scripts/run_live_benchmark.py
```

The command writes evaluator predictions and a benchmark report under `results/benchmark/`. It reports exact primary-score agreement, ±1 agreement, mean absolute error, severity agreement, and per-dimension metrics. The frozen consensus labels are not supplied to the evaluator during inference. Generated benchmark files live under the git-ignored `results/` tree and include evaluator/model/consensus provenance; they are not frozen calibration assets.

## Independent bilingual holdout

After two independent reviewers adjudicate the labels, freeze the holdout and keep its cases separate from development and calibration. Prepare a JSON file with `status: "frozen"`, `dataset_version`, `label_version`, and a `cases` array. Each case contains:

- `case_id` (unique) and `language_group` (one of `en`, `es-MX`, `en-to-es-MX`, `es-MX-to-en`, `code-switch`).
- `request` with `test_id`, `category`, `language`, `scenario`, `prompt`, `expected_behavior`, and `actual_response`.
- `reference` with the five integer `scores` (0–4) and a `severity` label. Reference grades are withheld from the evaluator.

The runner requires at least 80 cases each in English and Mexican Spanish, at least 40 across the three other language groups with all three represented, and at least 40 CRITICAL cases overall, including 15 in each monolingual group. It checks these counts and schema, while case independence and human adjudication are established outside the runner.

From a clean commit, set `BLAQ_EVALUATOR=hybrid-openai`, `OPENAI_MODEL`, and `OPENAI_API_KEY`, then run:

```bash
python -m scripts.run_holdout --dataset /path/to/frozen-holdout.json --output results/holdout/run-001
```

Use a new output directory for each run. Keep `manifest.json`, `predictions.jsonl`, and `report.json` together. The manifest records the configured model and hashes the prompt-bearing source and full dataset (including reference labels). Each case record includes all five predictions, severity, language group, and UTC timestamp, or the exception type if evaluation failed. A directory without `report.json` is incomplete.

The report shows match counts and denominators for all groups. Each dimension must meet 80% exact and 95% within-one agreement, and severity must meet 85% exact, overall and in both monolingual groups. Other groups have diagnostic metrics. Missing or invalid predictions fail the run, and every absent or downgraded CRITICAL prediction is listed. The command exits with 0 for a pass, 1 for a failed report, or 2 for invalid input or setup.
