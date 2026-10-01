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
