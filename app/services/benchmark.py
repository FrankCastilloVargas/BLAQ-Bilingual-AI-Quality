import json
from pathlib import Path

DIMENSIONS = ("accuracy", "language", "context", "safety", "escalation")


def load_consensus(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {case["case_id"]: case for case in data["cases"]}


def benchmark_predictions(consensus: dict, predictions: list[dict]) -> dict:
    predicted = {item["case_id"]: item for item in predictions}
    missing = sorted(set(consensus) - set(predicted))
    extra = sorted(set(predicted) - set(consensus))
    if missing or extra:
        raise ValueError(f"Prediction coverage mismatch; missing={missing}, extra={extra}")

    rows = []
    for case_id, target in consensus.items():
        pred = predicted[case_id]
        if pred["primary_dimension"] != target["primary_dimension"]:
            raise ValueError(f"Primary dimension mismatch for {case_id}")
        score = pred["primary_score"]
        if not isinstance(score, int) or not 0 <= score <= 4:
            raise ValueError(f"Invalid primary score for {case_id}: {score}")
        delta = abs(score - target["primary_score"])
        rows.append({
            "case_id": case_id,
            "dimension": target["primary_dimension"],
            "target": target["primary_score"],
            "predicted": score,
            "absolute_error": delta,
            "exact": delta == 0,
            "within_one": delta <= 1,
            "severity_match": pred["severity"] == target["severity"],
        })

    n = len(rows)
    summary = {
        "cases": n,
        "exact_agreement": sum(r["exact"] for r in rows) / n,
        "within_one_agreement": sum(r["within_one"] for r in rows) / n,
        "mean_absolute_error": sum(r["absolute_error"] for r in rows) / n,
        "severity_agreement": sum(r["severity_match"] for r in rows) / n,
        "by_dimension": {},
    }
    for dimension in DIMENSIONS:
        group = [r for r in rows if r["dimension"] == dimension]
        summary["by_dimension"][dimension] = {
            "cases": len(group),
            "exact_agreement": sum(r["exact"] for r in group) / len(group),
            "within_one_agreement": sum(r["within_one"] for r in group) / len(group),
            "mean_absolute_error": sum(r["absolute_error"] for r in group) / len(group),
            "severity_agreement": sum(r["severity_match"] for r in group) / len(group),
        }
    summary["rows"] = rows
    return summary


def benchmark_files(consensus_path: str | Path, predictions_path: str | Path) -> dict:
    consensus = load_consensus(consensus_path)
    predictions = json.loads(Path(predictions_path).read_text(encoding="utf-8"))
    return benchmark_predictions(consensus, predictions)
