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
