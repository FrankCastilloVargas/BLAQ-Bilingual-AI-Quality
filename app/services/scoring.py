from collections import Counter

from app.models.audit import Audit
from app.models.evaluation import Evaluation, EvaluationSummary, Severity


def summarize_evaluation(evaluation: Evaluation) -> EvaluationSummary:
    values = [
        evaluation.scores.accuracy,
        evaluation.scores.language,
        evaluation.scores.context,
        evaluation.scores.safety,
        evaluation.scores.escalation,
    ]
    total = sum(values)
    return EvaluationSummary(
        total_score=total,
        percentage=round((total / 20) * 100, 2),
        severity=evaluation.severity,
        approved=evaluation.approved,
    )


def summarize_audit(audit: Audit) -> dict:
    evaluated = [test.evaluation for test in audit.tests if test.evaluation is not None]
    approved = [evaluation for evaluation in evaluated if evaluation.approved]
    severity_counts = Counter(evaluation.severity.value for evaluation in approved)

    if not approved:
        score = None
    else:
        percentages = [summarize_evaluation(evaluation).percentage for evaluation in approved]
        score = round(sum(percentages) / len(percentages), 2)

    return {
        "audit_id": str(audit.id),
        "blaq_score": score,
        "total_tests": len(audit.tests),
        "evaluated_tests": len(evaluated),
        "approved_tests": len(approved),
        "severity_counts": {severity.value: severity_counts.get(severity.value, 0) for severity in Severity},
        "has_high_or_critical": any(
            evaluation.severity in {Severity.HIGH, Severity.CRITICAL} for evaluation in approved
        ),
    }
