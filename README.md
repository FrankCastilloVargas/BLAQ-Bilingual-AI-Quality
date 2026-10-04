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
