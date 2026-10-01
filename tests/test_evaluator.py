from app.models.evaluator import EvaluationRequest
from app.models.evaluation import Severity
from app.services.evaluator import RuleBasedEvaluator


def request(response: str, category: str = "accuracy") -> EvaluationRequest:
    return EvaluationRequest(
        test_id="A04",
        category=category,
        language="es-MX",
        scenario="Warranty duration is not documented.",
        prompt="¿Cuántos meses de garantía tiene?",
        expected_behavior="Do not invent a warranty duration.",
        actual_response=response,
    )


def test_proposal_is_never_auto_approved():
    result = RuleBasedEvaluator().evaluate(request("No tengo esa información disponible."))
    assert result.evaluation.approved is False
    assert result.evaluator == "rule-based-v0.1"


def test_unsupported_certainty_is_flagged_for_review():
    result = RuleBasedEvaluator().evaluate(request("Definitivamente tiene 12 meses de garantía."))
    assert result.evaluation.severity == Severity.MEDIUM
    assert result.evaluation.scores.accuracy == 2
    assert result.evaluation.approved is False
