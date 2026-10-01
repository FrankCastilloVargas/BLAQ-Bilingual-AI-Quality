from collections import Counter
from app.models.validation import ValidationDataset
from scripts.build_gold_set import build

def test_gold_set_v01_is_balanced_and_parseable(tmp_path, monkeypatch):
    import scripts.build_gold_set as builder
    monkeypatch.setattr(builder, "OUTPUT", tmp_path / "gold.json")
    payload = build()
    dataset = ValidationDataset.model_validate(payload)
    assert dataset.status == "seed"
    assert len(dataset.cases) == 75
    ids = Counter(case.source_test_id for case in dataset.cases)
    assert len(ids) == 25 and set(ids.values()) == {3}
    categories = Counter(case.request.category for case in dataset.cases)
    assert set(categories.values()) == {15}
    kinds = Counter(case.case_type for case in dataset.cases)
    assert kinds == {"typical": 25, "edge": 25, "adversarial": 25}
    assert all(case.gold.review_status == "seed" for case in dataset.cases)
