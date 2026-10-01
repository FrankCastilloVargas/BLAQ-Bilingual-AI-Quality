from app.models.audit import Audit
from app.models.evaluation import Evaluation, Scores, Severity
from app.models.testcase import Category, TestCase as BlaqTestCase
from app.services.reporting import build_audit_report


def make_test(test_id, category, severity=Severity.NONE, approved=True):
    return BlaqTestCase(
        test_id=test_id, category=category, language="es-MX", scenario="Demo", prompt="Demo",
        expected_behavior="Demo", actual_response="Demo",
        evaluation=Evaluation(
            scores=Scores(accuracy=4, language=4, context=4, safety=4, escalation=4),
            severity=severity, finding=f"Finding {test_id}", business_impact="Impact",
            recommendation="Recommendation", approved=approved,
        ),
    )


def test_partial_report_is_provisional_and_has_no_final_score():
    audit = Audit(client="Demo", product_name="Bot", reviewer="Reviewer",
                  tests=[make_test("A01", Category.ACCURACY, Severity.HIGH)])
    report = build_audit_report(audit)
    assert report.status == "PROVISIONAL"
    assert report.blaq_score is None
    assert report.approved_tests == 1
    assert report.priority_findings[0].test_id == "A01"


def test_unapproved_findings_never_enter_client_report():
    audit = Audit(client="Demo", product_name="Bot", reviewer="Reviewer", tests=[
        make_test("A01", Category.ACCURACY, Severity.LOW, True),
        make_test("A02", Category.ACCURACY, Severity.CRITICAL, False),
    ])
    report = build_audit_report(audit)
    assert [item.test_id for item in report.priority_findings] == ["A01"]
    assert report.severity_counts["CRITICAL"] == 0


def test_findings_are_sorted_by_business_severity():
    audit = Audit(client="Demo", product_name="Bot", reviewer="Reviewer", tests=[
        make_test("A01", Category.ACCURACY, Severity.LOW),
        make_test("S01", Category.SAFETY, Severity.CRITICAL),
        make_test("C01", Category.CONTEXT, Severity.HIGH),
    ])
    report = build_audit_report(audit)
    assert [item.severity for item in report.priority_findings] == ["CRITICAL", "HIGH", "LOW"]


def test_complete_report_is_final_and_scores_100():
    groups = [(Category.ACCURACY, "A"), (Category.LANGUAGE, "L"), (Category.CONTEXT, "C"),
              (Category.SAFETY, "S"), (Category.ESCALATION, "E")]
    tests = [make_test(f"{prefix}{i:02d}", category) for category, prefix in groups for i in range(1, 6)]
    report = build_audit_report(Audit(client="Demo", product_name="Bot", reviewer="Reviewer", tests=tests))
    assert report.status == "FINAL"
    assert report.blaq_score == 100
    assert report.approved_tests == 25
