from app.models.audit import Audit
from app.models.evaluation import Evaluation, Scores, Severity
from app.models.testcase import Category, TestCase
from app.services.scoring import summarize_audit


def make_test(test_id: str, severity: Severity, approved: bool) -> TestCase:
    return TestCase(
        test_id=test_id,
        category=Category.ACCURACY,
        language="es-MX",
        scenario="Demo scenario",
        prompt="Demo prompt",
        expected_behavior="Demo expected behavior",
        actual_response="Demo response",
        evaluation=Evaluation(
            scores=Scores(accuracy=4, language=4, context=4, safety=4, escalation=4),
            severity=severity,
            approved=approved,
        ),
    )


def test_audit_score_uses_only_human_approved_results():
    audit = Audit(
        client="Demo", product_name="Bot", reviewer="Reviewer",
        tests=[make_test("A01", Severity.NONE, True), make_test("A02", Severity.CRITICAL, False)],
    )
    result = summarize_audit(audit)
    assert result["blaq_score"] == 100.0
    assert result["approved_tests"] == 1
    assert result["severity_counts"]["CRITICAL"] == 0


def test_high_severity_flag_is_not_hidden_by_perfect_score():
    audit = Audit(
        client="Demo", product_name="Bot", reviewer="Reviewer",
        tests=[make_test("A01", Severity.HIGH, True)],
    )
    result = summarize_audit(audit)
    assert result["blaq_score"] == 100.0
    assert result["has_high_or_critical"] is True
