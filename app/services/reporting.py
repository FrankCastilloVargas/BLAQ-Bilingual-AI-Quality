from app.models.audit import Audit
from app.models.evaluation import Severity
from app.models.report import AuditReport, CategoryReport, ReportFinding
from app.services.scoring import summarize_audit


SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.NONE: 4,
}


def build_audit_report(audit: Audit) -> AuditReport:
    summary = summarize_audit(audit)
    approved = [test for test in audit.tests if test.evaluation and test.evaluation.approved]

    findings = [
        ReportFinding(
            test_id=test.test_id,
            category=test.category.value,
            severity=test.evaluation.severity.value,
            finding=test.evaluation.finding,
            business_impact=test.evaluation.business_impact,
            recommendation=test.evaluation.recommendation,
        )
        for test in sorted(approved, key=lambda item: (SEVERITY_ORDER[item.evaluation.severity], item.test_id))
        if test.evaluation.severity != Severity.NONE
    ]

    category_scores = {
        name: CategoryReport(
            raw_points=data["raw_points"],
            approved_tests=data["approved_tests"],
            expected_tests=data["expected_tests"],
            max_points=data["max_points"],
            percentage=(round(data["raw_points"] / data["max_points"] * 100, 2)
                        if data["approved_tests"] == data["expected_tests"] else data["provisional_percentage"]),
        )
        for name, data in summary["category_scores"].items()
    }

    if summary["complete"]:
        status = "FINAL"
        executive_summary = (
            f"BLAQ-25 completed with a score of {summary['blaq_score']}/100. "
            f"{summary['severity_counts']['CRITICAL']} critical and "
            f"{summary['severity_counts']['HIGH']} high-severity findings were confirmed by human review."
        )
    else:
        status = "PROVISIONAL"
        executive_summary = (
            f"Audit in progress: {summary['approved_tests']} of 25 required tests are human-approved. "
            "A final BLAQ Score is not issued until all 25 official tests are approved."
        )

    return AuditReport(
        audit_id=str(audit.id), client=audit.client, product_name=audit.product_name,
        model_version=audit.model_version, reviewer=audit.reviewer, audit_date=audit.audit_date.isoformat(),
        status=status, executive_summary=executive_summary, blaq_score=summary["blaq_score"],
        provisional_percentage=summary["provisional_percentage"], approved_tests=summary["approved_tests"],
        total_tests=summary["total_tests"], category_scores=category_scores,
        severity_counts=summary["severity_counts"], priority_findings=findings,
    )
