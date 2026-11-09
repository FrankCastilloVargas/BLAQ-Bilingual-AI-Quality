import json
from types import SimpleNamespace

import pytest

from scripts import run_holdout


def packet():
    cases = []
    groups = {"en": (80, 15), "es-MX": (80, 15), "en-to-es-MX": (10, 10),
              "es-MX-to-en": (10, 0), "code-switch": (20, 0)}
    for group, (count, critical) in groups.items():
        for i in range(count):
            case_id = f"{group}-{i}"
            cases.append({
                "case_id": case_id,
                "language_group": group,
                "request": {"test_id": case_id, "category": "accuracy", "language": group,
                            "scenario": "Test", "prompt": "Test", "expected_behavior": "Test",
                            "actual_response": "Test"},
                "reference": {"scores": dict.fromkeys(run_holdout.DIMENSIONS, 4),
                              "severity": "CRITICAL" if i < critical else "NONE"},
            })
    return {"dataset_version": "v1", "label_version": "v1", "status": "frozen", "cases": cases}


def test_report_enforces_each_language_threshold():
    cases = run_holdout.Holdout.model_validate(packet()).cases
    predictions = {case.case_id: case.reference for case in cases}
    assert run_holdout.report_results(cases, predictions)["passed"]

    for case in cases[15:32]:
        grade = case.reference.model_copy(deep=True)
        grade.scores.context = 3
        predictions[case.case_id] = grade

    report = run_holdout.report_results(cases, predictions)
    assert report["failures"] == ["en context: exact agreement below 80%."]
    assert report["groups"]["en"]["scores"]["context"] == {"exact": 63, "within_one": 80}


def test_live_execution_records_errors_and_blocks_critical_misses(tmp_path, monkeypatch):
    payload = packet()
    dataset = tmp_path / "holdout.json"
    dataset.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "run"
    references = {case["case_id"]: case["reference"] for case in payload["cases"]}

    class FakeEvaluator:
        def evaluate(self, request):
            assert "reference" not in request.model_dump()
            if request.test_id == "en-0":
                raise TimeoutError("provider detail")
            reference = references[request.test_id]
            grade = run_holdout.Grade.model_validate(reference)
            if request.test_id == "es-MX-0":
                grade.severity = run_holdout.Severity.HIGH
            if request.test_id == "en-to-es-MX-0":
                grade.scores.context = True  # Invalid integer score.
            return SimpleNamespace(test_id=request.test_id, evaluation=grade, evaluator="hybrid:openai:test-model")

    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("BLAQ_EVALUATOR", "hybrid-openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    monkeypatch.setattr(run_holdout, "git_revision", lambda: "a" * 40)
    monkeypatch.setattr(run_holdout, "build_evaluator", FakeEvaluator)

    report = run_holdout.execute(dataset, output)
    assert not report["passed"]
    assert report["critical_misses"] == ["en-0", "es-MX-0", "en-to-es-MX-0"]
    records = [json.loads(line) for line in (output / "predictions.jsonl").read_text().splitlines()]
    assert len(records) == 200
    assert records[0]["error"] == "TimeoutError"
    assert set(records[1]["prediction"]["scores"]) == set(run_holdout.DIMENSIONS)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["commit"] == "a" * 40
    assert manifest["configured_model"] == "test-model"
    assert len(manifest["prompt_source_sha256"]) == 64
    assert json.loads((output / "report.json").read_text()) == report
    with pytest.raises(FileExistsError):
        run_holdout.execute(dataset, output)


def test_duplicate_case_ids_rejected():
    payload = packet()
    payload["cases"][1]["case_id"] = payload["cases"][0]["case_id"]
    with pytest.raises(ValueError, match="unique"):
        run_holdout.load_holdout(json.dumps(payload).encode())
