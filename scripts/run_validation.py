import argparse, json
from pathlib import Path
from app.models.validation import ValidationDataset
from app.services.evaluator_factory import build_evaluator
from app.services.validation import calculate_metrics


def run(dataset_path: Path, output_path: Path) -> dict:
    dataset = ValidationDataset.model_validate_json(dataset_path.read_text(encoding="utf-8"))
    evaluator = build_evaluator()
    proposals = [evaluator.evaluate(case.request) for case in dataset.cases]
    metrics = calculate_metrics(dataset.cases, proposals)
    result = {"dataset": dataset.name, "version": dataset.version, "dataset_status": dataset.status,
              "evaluator": proposals[0].evaluator if proposals else "none", "metrics": metrics.model_dump(mode="json"),
              "cases": [{"case_id": c.case_id, "gold": c.gold.model_dump(mode="json"),
                         "proposal": p.model_dump(mode="json")} for c,p in zip(dataset.cases, proposals, strict=True)]}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run BLAQ evaluator against a frozen human-labeled dataset.")
    parser.add_argument("--dataset", default="validation/gold_set.json")
    parser.add_argument("--output", default="results/validation_latest.json")
    args = parser.parse_args()
    result = run(Path(args.dataset), Path(args.output))
    print(json.dumps(result["metrics"], indent=2))
