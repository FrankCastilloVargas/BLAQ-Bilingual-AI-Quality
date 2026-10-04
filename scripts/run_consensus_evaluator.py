import argparse
import json
from pathlib import Path

from app.models.evaluator import EvaluationRequest
from app.services.evaluator_factory import build_evaluator

DEFAULT_PACKET = Path("validation/review/reviewer_b_blind_subset.json")


def load_requests(packet_path: Path = DEFAULT_PACKET) -> list[tuple[str, EvaluationRequest]]:
    batches = json.loads(packet_path.read_text(encoding="utf-8"))
    rows = []
    for batch in batches:
        for item in batch["items"]:
            rows.append((item["case_id"], EvaluationRequest(**item["request"])))
    if len(rows) != 25 or len({case_id for case_id, _ in rows}) != 25:
        raise ValueError("Benchmark packet must contain exactly 25 unique cases.")
    return rows


def run(packet_path: Path, output_path: Path) -> list[dict]:
    evaluator = build_evaluator()
    predictions = []
    for case_id, request in load_requests(packet_path):
        proposal = evaluator.evaluate(request)
        primary = request.category
        predictions.append({
            "case_id": case_id,
            "primary_dimension": primary,
            "primary_score": getattr(proposal.evaluation.scores, primary),
            "severity": proposal.evaluation.severity.value,
            "evaluator": proposal.evaluator,
        })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(predictions, indent=2), encoding="utf-8")
    return predictions


def main():
    parser = argparse.ArgumentParser(description="Run the configured BLAQ evaluator on the frozen 25-case calibration subset.")
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--output", type=Path, default=Path("results/benchmark/evaluator_predictions.json"))
    args = parser.parse_args()
    predictions = run(args.packet, args.output)
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
