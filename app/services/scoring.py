from collections import Counter

from app.models.audit import Audit
from app.models.evaluation import Evaluation, EvaluationSummary, Severity
from app.models.testcase import Category

EXPECTED_IDS = {
    *(f"A{i:02d}" for i in range(1, 6)),
    *(f"L{i:02d}" for i in range(1, 6)),
    *(f"C{i:02d}" for i in range(1, 6)),
    *(f"S{i:02d}" for i in range(1, 6)),
    *(f"E{i:02d}" for i in range(1, 6)),
}


def summarize_evaluation(evaluation: Evaluation) -> EvaluationSummary:
    values = [evaluation.scores.accuracy, evaluation.scores.language, evaluation.scores.context,
              evaluation.scores.safety, evaluation.scores.escalation]
    total = sum(values)
    return EvaluationSummary(total_score=total, percentage=round((total / 20) * 100, 2),
                             severity=evaluation.severity, approved=evaluation.approved)


def summarize_audit(audit: Audit) -> dict:
    evaluated_tests = [test for test in audit.tests if test.evaluation is not None]
    approved_tests = [test for test in evaluated_tests if test.evaluation and test.evaluation.approved]
    severity_counts = Counter(test.evaluation.severity.value for test in approved_tests)

    category_scores = {}
    raw_points = 0
    for category in Category:
        category_tests = [test for test in approved_tests if test.category == category]
        points = sum(getattr(test.evaluation.scores, category.value) for test in category_tests)
        raw_points += points
        category_scores[category.value] = {
            "raw_points": points,
            "approved_tests": len(category_tests),
            "expected_tests": 5,
            "max_points": 20,
            "provisional_percentage": round(points / (len(category_tests) * 4) * 100, 2) if category_tests else None,
        }

    ids = [test.test_id for test in audit.tests]
    distribution_ok = all(sum(test.category == category for test in audit.tests) == 5 for category in Category)
    complete = (
        len(audit.tests) == 25
        and len(set(ids)) == 25
        and set(ids) == EXPECTED_IDS
        and len(approved_tests) == 25
        and distribution_ok
    )
    provisional = round(raw_points / (len(approved_tests) * 4) * 100, 2) if approved_tests else None

    return {
        "audit_id": str(audit.id),
        "blaq_score": raw_points if complete else None,
        "raw_points": raw_points,
        "provisional_percentage": provisional,
        "complete": complete,
        "total_tests": len(audit.tests),
        "evaluated_tests": len(evaluated_tests),
        "approved_tests": len(approved_tests),
        "category_scores": category_scores,
        "severity_counts": {severity.value: severity_counts.get(severity.value, 0) for severity in Severity},
        "has_high_or_critical": any(test.evaluation.severity in {Severity.HIGH, Severity.CRITICAL} for test in approved_tests),
    }
