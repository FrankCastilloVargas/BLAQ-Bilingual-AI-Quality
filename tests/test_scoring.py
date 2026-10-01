from app.models.evaluation import Evaluation, Scores, Severity
from app.services.scoring import summarize_evaluation


def test_perfect_score_is_100_percent():
    evaluation = Evaluation(
        scores=Scores(accuracy=4, language=4, context=4, safety=4, escalation=4)
    )
    result = summarize_evaluation(evaluation)
    assert result.total_score == 20
    assert result.percentage == 100.0


def test_high_severity_is_preserved_independent_of_score():
    evaluation = Evaluation(
        scores=Scores(accuracy=4, language=4, context=4, safety=4, escalation=4),
        severity=Severity.HIGH,
    )
    result = summarize_evaluation(evaluation)
    assert result.percentage == 100.0
    assert result.severity == Severity.HIGH
