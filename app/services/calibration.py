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


def reconcile_batches(reviewer_a: BlindReviewBatch, reviewer_b: BlindReviewBatch) -> dict:
    """Compare completed overlapping labels without modifying either review."""
    validate_completed_batch(reviewer_a)
    validate_completed_batch(reviewer_b)
    a_items = {item.case_id: item for item in reviewer_a.items}
    b_items = {item.case_id: item for item in reviewer_b.items}
    overlap = sorted(set(a_items) & set(b_items))
    if not overlap:
        raise ValueError("Reviewer batches have no overlapping cases")
    dimensions = DIMENSIONS
    exact = 0
    severity_matches = 0
    abs_delta = {dimension: 0 for dimension in dimensions}
    disagreements = []
    for case_id in overlap:
        a, b = a_items[case_id], b_items[case_id]
        score_pairs = [(getattr(a.reviewer_scores, d), getattr(b.reviewer_scores, d)) for d in dimensions]
        same_scores = all(x == y for x, y in score_pairs)
        same_severity = a.reviewer_severity == b.reviewer_severity
        exact += int(same_scores and same_severity)
        severity_matches += int(same_severity)
        for d, (x, y) in zip(dimensions, score_pairs):
            abs_delta[d] += abs(x - y)
        if not (same_scores and same_severity):
            disagreements.append(case_id)
    n = len(overlap)
    return {
        "overlap_cases": n,
        "exact_label_agreement": exact / n,
        "severity_agreement": severity_matches / n,
        "mean_absolute_score_delta": {d: abs_delta[d] / n for d in dimensions},
        "disagreement_case_ids": disagreements,
    }
