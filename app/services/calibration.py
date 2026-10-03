from pathlib import Path
from app.models.validation import ValidationDataset
from app.models.calibration import BlindReviewBatch, BlindReviewItem

DIMENSIONS = ("accuracy", "language", "context", "safety", "escalation")


def load_validation_dataset(dataset_path: Path) -> ValidationDataset:
    if dataset_path.exists():
        return ValidationDataset.model_validate_json(dataset_path.read_text(encoding="utf-8"))
    if dataset_path == Path("validation/gold_set_v0.1.json"):
        from scripts.build_gold_set import build
        return ValidationDataset.model_validate(build())
    raise FileNotFoundError(dataset_path)


def create_blind_batch(dataset_path: Path, dimension: str, output_path: Path, reviewer_slot: str = "A") -> BlindReviewBatch:
    dataset = load_validation_dataset(dataset_path)
    slot = reviewer_slot.upper()
    if slot not in {"A", "B"}:
        raise ValueError("reviewer_slot must be A or B")
    items = [BlindReviewItem(case_id=c.case_id, source_test_id=c.source_test_id, request=c.request)
             for c in dataset.cases if c.request.category == dimension]
    if not items:
        raise ValueError(f"No cases found for dimension: {dimension}")
    batch = BlindReviewBatch(batch_id=f"{dataset.version}-{dimension}-review-{slot.lower()}",
                             dataset_version=dataset.version, dimension=dimension, items=items)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(batch.model_dump_json(indent=2), encoding="utf-8")
    return batch


def create_reviewer_b_subset(dataset_path: Path, output_path: Path) -> list[BlindReviewBatch]:
    """Create 25 blind cases: five deterministic cases per dimension.

    Selection spans all five source tests in each dimension and mixes response
    variants without reading seed/gold labels.
    """
    dataset = load_validation_dataset(dataset_path)
    batches = []
    variant_index = (0, 1, 2, 1, 2)
    for dimension in DIMENSIONS:
        grouped = {}
        for case in dataset.cases:
            if case.request.category == dimension:
                grouped.setdefault(case.source_test_id, []).append(case)
        selected = []
        for pos, test_id in enumerate(sorted(grouped)):
            cases = sorted(grouped[test_id], key=lambda c: c.case_id)
            selected.append(cases[variant_index[pos] % len(cases)])
        items = [BlindReviewItem(case_id=c.case_id, source_test_id=c.source_test_id, request=c.request)
                 for c in selected]
        batches.append(BlindReviewBatch(
            batch_id=f"{dataset.version}-{dimension}-review-b-subset",
            dataset_version=dataset.version, dimension=dimension, items=items))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "[\n" + ",\n".join(b.model_dump_json(indent=2) for b in batches) + "\n]\n",
        encoding="utf-8")
    return batches


def validate_completed_batch(batch: BlindReviewBatch) -> None:
    if not batch.reviewer.strip():
        raise ValueError("Reviewer identity is required.")
    for item in batch.items:
        if item.reviewer_scores is None or item.reviewer_severity is None:
            raise ValueError(f"Incomplete human label: {item.case_id}")
        if not item.reviewer_finding.strip() or not item.reviewer_recommendation.strip():
            raise ValueError(f"Finding and recommendation are required: {item.case_id}")
