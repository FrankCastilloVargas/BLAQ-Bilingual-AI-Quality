import json

import pytest

from app.services.benchmark import benchmark_predictions, load_consensus


CONSENSUS = "validation/consensus/consensus_v0.1.json"


def predictions_from_consensus():
    data = json.loads(open(CONSENSUS, encoding="utf-8").read())
    return [
        {
            "case_id": case["case_id"],
            "primary_dimension": case["primary_dimension"],
            "primary_score": case["primary_score"],
            "severity": case["severity"],
        }
        for case in data["cases"]
    ]


def test_benchmark_perfect_predictions():
    consensus = load_consensus(CONSENSUS)
    result = benchmark_predictions(consensus, predictions_from_consensus())
    assert result["cases"] == 25
    assert result["exact_agreement"] == 1.0
    assert result["within_one_agreement"] == 1.0
    assert result["mean_absolute_error"] == 0.0
    assert result["severity_agreement"] == 1.0
    assert all(metrics["cases"] == 5 for metrics in result["by_dimension"].values())


def test_benchmark_reports_controlled_errors():
    consensus = load_consensus(CONSENSUS)
    predictions = predictions_from_consensus()
    predictions[0]["primary_score"] = 3
    predictions[1]["primary_score"] = 2
    predictions[1]["severity"] = "MEDIUM"
    result = benchmark_predictions(consensus, predictions)
    assert result["exact_agreement"] == 23 / 25
    assert result["within_one_agreement"] == 24 / 25
    assert result["mean_absolute_error"] == 3 / 25
    assert result["severity_agreement"] == 24 / 25


def test_benchmark_rejects_incomplete_predictions():
    consensus = load_consensus(CONSENSUS)
    with pytest.raises(ValueError, match="coverage mismatch"):
        benchmark_predictions(consensus, predictions_from_consensus()[:-1])


def test_runner_loads_exact_blind_subset_requests():
    from scripts.run_consensus_evaluator import load_requests
    rows = load_requests()
    assert len(rows) == 25
    assert len({case_id for case_id, _ in rows}) == 25
    assert {request.category for _, request in rows} == {"accuracy", "language", "context", "safety", "escalation"}
    assert all(request.actual_response for _, request in rows)


def test_live_benchmark_requires_explicit_hybrid_configuration(monkeypatch):
    from scripts.run_live_benchmark import require_live_semantic_config
    monkeypatch.delenv("BLAQ_EVALUATOR", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="BLAQ_EVALUATOR"):
        require_live_semantic_config()
    monkeypatch.setenv("BLAQ_EVALUATOR", "hybrid-openai")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        require_live_semantic_config()
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    require_live_semantic_config()
