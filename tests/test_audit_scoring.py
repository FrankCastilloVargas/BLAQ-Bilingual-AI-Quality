from app.models.audit import Audit
from app.models.evaluation import Evaluation, Scores, Severity
from app.models.testcase import Category, TestCase as BlaqTestCase
from app.services.scoring import summarize_audit


def make_test(test_id: str, category: Category, primary_score: int = 4, approved: bool = True, severity: Severity = Severity.NONE) -> BlaqTestCase:
    values = dict(accuracy=4, language=4, context=4, safety=4, escalation=4)
    values[category.value] = primary_score
    return BlaqTestCase(test_id=test_id, category=category, language="es-MX", scenario="Demo", prompt="Demo",
                        expected_behavior="Demo", actual_response="Demo",
                        evaluation=Evaluation(scores=Scores(**values), severity=severity, approved=approved))


def test_partial_audit_has_no_final_blaq_score():
    audit = Audit(client="Demo", product_name="Bot", reviewer="Reviewer",
                  tests=[make_test("A01", Category.ACCURACY)])
    result = summarize_audit(audit)
    assert result["blaq_score"] is None
    assert result["raw_points"] == 4
    assert result["provisional_percentage"] == 100.0
    assert result["complete"] is False


def test_primary_category_only_drives_points():
    audit = Audit(client="Demo", product_name="Bot", reviewer="Reviewer",
                  tests=[make_test("A01", Category.ACCURACY, primary_score=1)])
    result = summarize_audit(audit)
    assert result["raw_points"] == 1
    assert result["provisional_percentage"] == 25.0


def test_unapproved_critical_is_excluded():
    audit = Audit(client="Demo", product_name="Bot", reviewer="Reviewer", tests=[
        make_test("A01", Category.ACCURACY, approved=True),
        make_test("A02", Category.ACCURACY, approved=False, severity=Severity.CRITICAL),
    ])
    result = summarize_audit(audit)
    assert result["approved_tests"] == 1
    assert result["severity_counts"]["CRITICAL"] == 0


def test_complete_blaq25_scores_100():
    groups = [(Category.ACCURACY, "A"), (Category.LANGUAGE, "L"), (Category.CONTEXT, "C"),
              (Category.SAFETY, "S"), (Category.ESCALATION, "E")]
    tests = [make_test(f"{prefix}{i:02d}", category) for category, prefix in groups for i in range(1, 6)]
    result = summarize_audit(Audit(client="Demo", product_name="Bot", reviewer="Reviewer", tests=tests))
    assert result["complete"] is True
    assert result["raw_points"] == 100
    assert result["blaq_score"] == 100
    assert all(item["raw_points"] == 20 for item in result["category_scores"].values())
