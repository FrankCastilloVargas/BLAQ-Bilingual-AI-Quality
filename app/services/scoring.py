from app.models.evaluation import Evaluation, EvaluationSummary


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
