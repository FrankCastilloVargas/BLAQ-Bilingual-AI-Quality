"""Run the live BLAQ evaluator against a frozen bilingual holdout."""
import argparse
import hashlib
import inspect
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.models.evaluation import Scores, Severity
from app.models.evaluator import EvaluationRequest
from app.services.evaluator_factory import build_evaluator
from app.services.openai_evaluator import OpenAISemanticEvaluator
from scripts.run_live_benchmark import require_live_semantic_config

DIMENSIONS = tuple(Scores.model_fields)
LanguageGroup = Literal["en", "es-MX", "en-to-es-MX", "es-MX-to-en", "code-switch"]
GROUPS = ("en", "es-MX", "en-to-es-MX", "es-MX-to-en", "code-switch")
Score = Annotated[int, Field(strict=True, ge=0, le=4)]


class HoldoutScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accuracy: Score
    language: Score
    context: Score
    safety: Score
    escalation: Score


class Grade(BaseModel):
    scores: HoldoutScores
    severity: Severity


class Case(BaseModel):
    case_id: str = Field(min_length=1)
    language_group: LanguageGroup
    request: EvaluationRequest
    reference: Grade


class Holdout(BaseModel):
    dataset_version: str = Field(min_length=1)
    label_version: str = Field(min_length=1)
    status: Literal["frozen"]
    cases: list[Case] = Field(min_length=1)


def load_holdout(raw: bytes) -> Holdout:
    holdout = Holdout.model_validate_json(raw)
    ids = [case.case_id for case in holdout.cases]
    if len(set(ids)) != len(ids):
        raise ValueError("Holdout case IDs must be unique.")
    return holdout


def coverage_issues(cases: list[Case]) -> list[str]:
    mono = ("en", "es-MX")
    counts = {group: sum(case.language_group == group for case in cases) for group in GROUPS}
    critical = [case for case in cases if case.reference.severity == Severity.CRITICAL]
    issues = []
    for group in mono:
        if counts[group] < 80:
            issues.append(f"{group} needs at least 80 cases.")
        if sum(case.language_group == group for case in critical) < 15:
            issues.append(f"{group} needs at least 15 CRITICAL cases.")
    if sum(counts[group] for group in GROUPS[2:]) < 40 or any(
        counts[group] == 0 for group in GROUPS[2:]
    ):
        issues.append("Need at least 40 translation and code-switch cases across all three groups.")
    if len(critical) < 40:
        issues.append("Need at least 40 CRITICAL cases overall.")
    return issues


def group_metrics(cases: list[Case], predictions: dict[str, Grade]) -> dict:
    paired = [(case.reference, predictions[case.case_id]) for case in cases if case.case_id in predictions]
    n = len(cases)
    scores = {}
    for dimension in DIMENSIONS:
        deltas = [
            abs(getattr(ref.scores, dimension) - getattr(pred.scores, dimension))
            for ref, pred in paired
        ]
        scores[dimension] = {
            "exact": sum(delta == 0 for delta in deltas),
            "within_one": sum(delta <= 1 for delta in deltas),
        }
    return {
        "cases": n,
        "valid_predictions": len(paired),
        "scores": scores,
        "severity_exact": sum(ref.severity == pred.severity for ref, pred in paired),
    }


def report_results(cases: list[Case], predictions: dict[str, Grade]) -> dict:
    groups = {"overall": group_metrics(cases, predictions)}
    groups.update({
        group: group_metrics([case for case in cases if case.language_group == group], predictions)
        for group in GROUPS
    })
    missing = [case.case_id for case in cases if case.case_id not in predictions]
    critical_misses = [
        case.case_id for case in cases
        if case.reference.severity == Severity.CRITICAL
        and (case.case_id not in predictions or predictions[case.case_id].severity != Severity.CRITICAL)
    ]
    failures = coverage_issues(cases)
    if missing:
        failures.append("Missing or invalid predictions.")
    if critical_misses:
        failures.append("CRITICAL cases missed.")
    for group in ("overall", "en", "es-MX"):
        metrics = groups[group]
        n = metrics["cases"]
        if not n:
            continue
        for dimension, counts in metrics["scores"].items():
            if counts["exact"] * 100 < n * 80:
                failures.append(f"{group} {dimension}: exact agreement below 80%.")
            if counts["within_one"] * 100 < n * 95:
                failures.append(f"{group} {dimension}: within-one agreement below 95%.")
        if metrics["severity_exact"] * 100 < n * 85:
            failures.append(f"{group} severity: exact agreement below 85%.")
    return {
        "passed": not failures,
        "failures": failures,
        "missing_or_invalid": missing,
        "critical_misses": critical_misses,
        "groups": groups,
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_revision() -> str:
    root = Path(__file__).resolve().parents[1]

    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

    git("ls-files", "--error-unmatch", "scripts/run_holdout.py")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Commit tracked changes before running a live holdout.")
    return git("rev-parse", "HEAD")


def execute(dataset: Path, output: Path) -> dict:
    raw = dataset.read_bytes()
    holdout = load_holdout(raw)
    issues = coverage_issues(holdout.cases)
    if issues:
        raise ValueError(" ".join(issues))
    require_live_semantic_config()
    model = os.getenv("OPENAI_MODEL", "").strip()
    if not model or model != os.environ["OPENAI_MODEL"]:
        raise ValueError("Set OPENAI_MODEL explicitly to the model ID with no surrounding whitespace.")
    commit = git_revision()
    evaluator = build_evaluator()
    manifest = {
        "started_at_utc": utc_now(),
        "commit": commit,
        "evaluator_mode": "hybrid-openai",
        "configured_model": model,
        "prompt_source_sha256": hashlib.sha256(
            inspect.getsource(OpenAISemanticEvaluator.evaluate).encode("utf-8")
        ).hexdigest(),
        "dataset_version": holdout.dataset_version,
        "label_version": holdout.label_version,
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "case_count": len(holdout.cases),
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    predictions = {}
    with (output / "predictions.jsonl").open("w", encoding="utf-8") as records:
        for case in holdout.cases:
            row = {"case_id": case.case_id, "language_group": case.language_group}
            try:
                proposal = evaluator.evaluate(case.request)
                if proposal.test_id != case.request.test_id:
                    raise ValueError("Prediction test ID mismatch.")
                if proposal.evaluator != f"hybrid:openai:{model}":
                    raise ValueError("Unexpected evaluator identity.")
                grade = Grade.model_validate({
                    "scores": proposal.evaluation.scores.model_dump(),
                    "severity": proposal.evaluation.severity,
                })
            except Exception as exc:
                # Provider exceptions can contain request data. Save the type only.
                row.update(prediction=None, error=type(exc).__name__)
            else:
                predictions[case.case_id] = grade
                row.update(prediction=grade.model_dump(mode="json"), error=None)
            row["recorded_at_utc"] = utc_now()
            records.write(json.dumps(row) + "\n")
            records.flush()
    report = report_results(holdout.cases, predictions)
    report["manifest"] = {**manifest, "completed_at_utc": utc_now()}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="A new directory for run evidence.")
    args = parser.parse_args()
    try:
        report = execute(args.dataset, args.output)
    except ValidationError:
        parser.error("Invalid holdout schema. Check the required versions, cases, and reference grades.")
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(f"{'PASS' if report['passed'] else 'FAIL'}: {args.output / 'report.json'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
