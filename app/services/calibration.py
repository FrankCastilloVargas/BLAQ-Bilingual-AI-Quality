from pathlib import Path
from app.models.validation import ValidationDataset
from app.models.calibration import BlindReviewBatch, BlindReviewItem


def load_validation_dataset(dataset_path: Path) -> ValidationDataset:
    if dataset_path.exists():
        return ValidationDataset.model_validate_json(dataset_path.read_text(encoding="utf-8"))
    if dataset_path == Path("validation/gold_set_v0.1.json"):
        from scripts.build_gold_set import build
        return ValidationDataset.model_validate(build())
    raise FileNotFoundError(dataset_path)


def create_blind_batch(dataset_path: Path, dimension: str, output_path: Path) -> BlindReviewBatch:
    dataset = load_validation_dataset(dataset_path)
    items = [BlindReviewItem(case_id=c.case_id, source_test_id=c.source_test_id, request=c.request)
             for c in dataset.cases if c.request.category == dimension]
    if not items:
        raise ValueError(f"No cases found for dimension: {dimension}")
    batch = BlindReviewBatch(batch_id=f"{dataset.version}-{dimension}-review-a", dataset_version=dataset.version,
                             dimension=dimension, items=items)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(batch.model_dump_json(indent=2), encoding="utf-8")
    return batch


def validate_completed_batch(batch: BlindReviewBatch) -> None:
    if not batch.reviewer.strip():
        raise ValueError("Reviewer identity is required.")
    for item in batch.items:
        if item.reviewer_scores is None or item.reviewer_severity is None:
            raise ValueError(f"Incomplete human label: {item.case_id}")
        if not item.reviewer_finding.strip() or not item.reviewer_recommendation.strip():
            raise ValueError(f"Finding and recommendation are required: {item.case_id}")
