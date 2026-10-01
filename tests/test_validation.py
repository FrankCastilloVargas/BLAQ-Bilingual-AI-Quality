from app.models.evaluation import Evaluation, Scores, Severity
from app.models.evaluator import EvaluationProposal, EvaluationRequest
from app.models.validation import GoldLabel, ValidationCase
from app.services.validation import calculate_metrics


def case(case_id, language, severity, scores):
    return ValidationCase(case_id=case_id, source_test_id="A01", language=language, case_type="typical",
        request=EvaluationRequest(test_id="A01", category="accuracy", language=language, scenario="s", prompt="p", expected_behavior="e", actual_response="a"),
        gold=GoldLabel(scores=Scores(**scores), severity=severity, finding="f", business_impact="b", recommendation="r", reviewer="human"))

def proposal(scores, severity):
    return EvaluationProposal(test_id="A01", evaluation=Evaluation(scores=Scores(**scores), severity=severity), evaluator="test", rationale="r")

def test_perfect_agreement():
    s={k:4 for k in ("accuracy","language","context","safety","escalation")}
    m=calculate_metrics([case("c1","es-MX",Severity.HIGH,s)],[proposal(s,Severity.HIGH)])
    assert m.exact_dimension_agreement == 1
    assert m.within_one_dimension_agreement == 1
    assert m.mean_absolute_error == 0
    assert m.severity_exact_agreement == 1
    assert m.high_critical_recall == 1

def test_error_and_serious_miss_are_measured():
    gold={k:0 for k in ("accuracy","language","context","safety","escalation")}
    pred={k:2 for k in gold}
    m=calculate_metrics([case("c1","en",Severity.CRITICAL,gold)],[proposal(pred,Severity.MEDIUM)])
    assert m.exact_dimension_agreement == 0
    assert m.within_one_dimension_agreement == 0
    assert m.mean_absolute_error == 2
    assert m.high_critical_recall == 0
    assert m.by_language["en"]["cases"] == 1
