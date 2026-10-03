import json
from pathlib import Path
import pytest
from app.models.calibration import BlindReviewBatch
from app.services.calibration import create_blind_batch, validate_completed_batch


def test_accuracy_batch_is_blind_and_has_15_cases(tmp_path):
    out=tmp_path/"accuracy.json"
    batch=create_blind_batch(Path("validation/gold_set_v0.1.json"),"accuracy",out)
    assert len(batch.items)==15
    assert {x.source_test_id for x in batch.items}=={"A01","A02","A03","A04","A05"}
    assert all(x.reviewer_scores is None and x.reviewer_severity is None for x in batch.items)
    raw=out.read_text(encoding="utf-8")
    assert '"gold"' not in raw and '"proposal"' not in raw and '"evaluator"' not in raw


def test_incomplete_batch_cannot_be_promoted(tmp_path):
    batch=create_blind_batch(Path("validation/gold_set_v0.1.json"),"accuracy",tmp_path/"a.json")
    batch.reviewer="Reviewer A"
    with pytest.raises(ValueError, match="Incomplete human label"):
        validate_completed_batch(batch)


def test_default_dataset_is_built_when_generated_file_is_missing(tmp_path, monkeypatch):
    import scripts.build_gold_set as builder
    original_catalog = builder.CATALOG.resolve()
    monkeypatch.setattr(builder, "CATALOG", original_catalog)
    monkeypatch.setattr(builder, "OUTPUT", tmp_path / "generated" / "gold.json")
    missing = Path("validation/gold_set_v0.1.json")
    monkeypatch.chdir(tmp_path)
    batch=create_blind_batch(missing,"accuracy",tmp_path/"review.json")
    assert len(batch.items)==15
    assert {x.source_test_id for x in batch.items}=={"A01","A02","A03","A04","A05"}
    raw=(tmp_path/"review.json").read_text(encoding="utf-8")
    assert '"gold"' not in raw and '"proposal"' not in raw and '"evaluator"' not in raw


def test_completed_accuracy_reviewer_a_batch_is_valid():
    from app.models.calibration import BlindReviewBatch
    batch = BlindReviewBatch.model_validate_json(
        Path("validation/review/accuracy_review_a.json").read_text(encoding="utf-8")
    )
    assert batch.reviewer == "Francisco Castillo"
    assert batch.status == "complete"
    assert batch.dimension == "accuracy"
    assert len(batch.items) == 15
    validate_completed_batch(batch)
    counts = {}
    for item in batch.items:
        counts[item.source_test_id] = counts.get(item.source_test_id, 0) + 1
    assert counts == {"A01": 3, "A02": 3, "A03": 3, "A04": 3, "A05": 3}


def test_completed_language_reviewer_a_batch_is_valid():
    from app.models.calibration import BlindReviewBatch
    batch = BlindReviewBatch.model_validate_json(
        Path("validation/review/language_review_a.json").read_text(encoding="utf-8")
    )
    assert batch.reviewer == "Francisco Castillo"
    assert batch.status == "complete"
    assert batch.dimension == "language"
    assert len(batch.items) == 15
    validate_completed_batch(batch)
    counts = {}
    for item in batch.items:
        counts[item.source_test_id] = counts.get(item.source_test_id, 0) + 1
    assert counts == {"L01": 3, "L02": 3, "L03": 3, "L04": 3, "L05": 3}


def test_completed_context_reviewer_a_batch_is_valid():
    from app.models.calibration import BlindReviewBatch
    batch = BlindReviewBatch.model_validate_json(
        Path("validation/review/context_review_a.json").read_text(encoding="utf-8")
    )
    assert batch.reviewer == "Francisco Castillo"
    assert batch.status == "complete"
    assert batch.dimension == "context"
    assert len(batch.items) == 15
    validate_completed_batch(batch)
    counts = {}
    for item in batch.items:
        counts[item.source_test_id] = counts.get(item.source_test_id, 0) + 1
    assert counts == {"C01": 3, "C02": 3, "C03": 3, "C04": 3, "C05": 3}


def test_completed_safety_reviewer_a_batch_is_valid():
    from app.models.calibration import BlindReviewBatch
    batch = BlindReviewBatch.model_validate_json(
        Path("validation/review/safety_review_a.json").read_text(encoding="utf-8")
    )
    assert batch.reviewer == "Francisco Castillo"
    assert batch.status == "complete"
    assert batch.dimension == "safety"
    assert len(batch.items) == 15
    validate_completed_batch(batch)
    counts = {}
    for item in batch.items:
        counts[item.source_test_id] = counts.get(item.source_test_id, 0) + 1
    assert counts == {"S01": 3, "S02": 3, "S03": 3, "S04": 3, "S05": 3}


def test_completed_escalation_reviewer_a_batch_is_valid():
    from app.models.calibration import BlindReviewBatch
    batch = BlindReviewBatch.model_validate_json(
        Path("validation/review/escalation_review_a.json").read_text(encoding="utf-8")
    )
    assert batch.reviewer == "Francisco Castillo"
    assert batch.status == "complete"
    assert batch.dimension == "escalation"
    assert len(batch.items) == 15
    validate_completed_batch(batch)
    counts = {}
    for item in batch.items:
        counts[item.source_test_id] = counts.get(item.source_test_id, 0) + 1
    assert counts == {"E01": 3, "E02": 3, "E03": 3, "E04": 3, "E05": 3}


def test_safety_escalation_freeze_anchors_are_orthogonal():
    import json
    data = json.loads(Path("validation/review/safety_review_a.json").read_text(encoding="utf-8"))
    items = {item["case_id"]: item for item in data["items"]}
    expected = {
        "S03-fail-002": (0, 4, "CRITICAL"),
        "S03-edge-003": (0, 4, "CRITICAL"),
        "S04-fail-002": (0, 1, "CRITICAL"),
        "S04-edge-003": (0, 1, "CRITICAL"),
    }
    for case_id, (safety, escalation, severity) in expected.items():
        item = items[case_id]
        assert item["reviewer_scores"]["safety"] == safety
        assert item["reviewer_scores"]["escalation"] == escalation
        assert item["reviewer_severity"] == severity


def test_reviewer_b_subset_is_blind_balanced_and_deterministic(tmp_path):
    import json
    from app.services.calibration import create_reviewer_b_subset
    out = tmp_path / "reviewer_b.json"
    batches = create_reviewer_b_subset(Path("validation/gold_set_v0.1.json"), out)
    assert len(batches) == 5
    assert sum(len(batch.items) for batch in batches) == 25
    assert {batch.dimension for batch in batches} == {"accuracy", "language", "context", "safety", "escalation"}
    for batch in batches:
        assert len(batch.items) == 5
        assert len({item.source_test_id for item in batch.items}) == 5
        for item in batch.items:
            assert item.reviewer_scores is None
            assert item.reviewer_severity is None
            assert item.reviewer_finding == ""
            assert item.reviewer_business_impact == ""
            assert item.reviewer_recommendation == ""
    first = out.read_text(encoding="utf-8")
    create_reviewer_b_subset(Path("validation/gold_set_v0.1.json"), out)
    assert out.read_text(encoding="utf-8") == first
    raw = json.loads(first)
    assert len(raw) == 5


def test_blind_batch_supports_reviewer_b_slot(tmp_path):
    from app.services.calibration import create_blind_batch
    batch = create_blind_batch(
        Path("validation/gold_set_v0.1.json"), "accuracy",
        tmp_path / "accuracy_review_b.json", "B")
    assert batch.batch_id.endswith("-accuracy-review-b")
    assert all(item.reviewer_scores is None for item in batch.items)


def test_reconciliation_reports_agreement_and_deltas():
    from app.models.calibration import BlindReviewBatch, BlindReviewItem
    from app.models.evaluation import Scores
    from app.models.evaluator import EvaluationRequest
    from app.services.calibration import reconcile_batches
    req = EvaluationRequest(
        test_id="A01", category="accuracy", language="es-MX",
        scenario="s", prompt="p", expected_behavior="e", actual_response="r")
    def batch(reviewer, accuracy, severity):
        return BlindReviewBatch(
            batch_id=reviewer, dataset_version="x", dimension="accuracy",
            reviewer=reviewer, status="complete",
            items=[BlindReviewItem(
                case_id="A01-good-001", source_test_id="A01", request=req,
                reviewer_scores=Scores(accuracy=accuracy, language=4, context=4, safety=4, escalation=4),
                reviewer_severity=severity, reviewer_finding="finding",
                reviewer_recommendation="recommendation")])
    result = reconcile_batches(batch("A", 4, "NONE"), batch("B", 3, "LOW"))
    assert result["overlap_cases"] == 1
    assert result["exact_label_agreement"] == 0
    assert result["severity_agreement"] == 0
    assert result["mean_absolute_score_delta"]["accuracy"] == 1
    assert result["disagreement_case_ids"] == ["A01-good-001"]


def test_reviewer_a_freeze_has_complete_unique_cross_dimension_coverage():
    dimensions = {
        "accuracy": "A",
        "language": "L",
        "context": "C",
        "safety": "S",
        "escalation": "E",
    }
    all_case_ids = []
    for dimension, prefix in dimensions.items():
        raw = json.loads(
            Path(f"validation/review/{dimension}_review_a.json").read_text(encoding="utf-8")
        )
        assert raw["dimension"] == dimension
        assert raw["reviewer"] == "Francisco Castillo"
        assert raw["status"] == "complete"
        assert len(raw["items"]) == 15
        counts = {}
        for item in raw["items"]:
            all_case_ids.append(item["case_id"])
            assert item["source_test_id"].startswith(prefix)
            assert item["request"]["category"] == dimension
            assert item["reviewer_severity"] in {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
            assert all(isinstance(score, int) and 0 <= score <= 4 for score in item["reviewer_scores"].values())
            counts[item["source_test_id"]] = counts.get(item["source_test_id"], 0) + 1
        assert counts == {f"{prefix}{n:02d}": 3 for n in range(1, 6)}
    assert len(all_case_ids) == 75
    assert len(set(all_case_ids)) == 75


def test_committed_reviewer_b_packet_is_blind_and_complete():
    import json
    raw = json.loads(Path("validation/review/reviewer_b_blind_subset.json").read_text(encoding="utf-8"))
    assert len(raw) == 5
    assert sum(len(batch["items"]) for batch in raw) == 25
    assert {batch["dimension"] for batch in raw} == {"accuracy", "language", "context", "safety", "escalation"}
    seen = set()
    for batch in raw:
        assert batch["reviewer"] == ""
        assert batch["status"] == "pending"
        assert len(batch["items"]) == 5
        assert len({item["source_test_id"] for item in batch["items"]}) == 5
        for item in batch["items"]:
            assert item["case_id"] not in seen
            seen.add(item["case_id"])
            assert item["reviewer_scores"] is None
            assert item["reviewer_severity"] is None
            assert item["reviewer_finding"] == ""
            assert item["reviewer_business_impact"] == ""
            assert item["reviewer_recommendation"] == ""
            assert item["reviewer_notes"] == ""
