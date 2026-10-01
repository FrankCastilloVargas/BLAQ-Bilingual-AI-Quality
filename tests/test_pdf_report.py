from app.models.report import AuditReport, CategoryReport, ReportFinding
from app.services.pdf_report import render_audit_report_pdf


def sample_report():
    return AuditReport(
        audit_id="audit-1", client="Demo Client", product_name="Demo Bot", model_version="v1",
        reviewer="Reviewer", audit_date="2026-10-01", status="FINAL",
        executive_summary="BLAQ-25 completed and human-reviewed.", blaq_score=88,
        provisional_percentage=88.0, approved_tests=25, total_tests=25,
        category_scores={"accuracy": CategoryReport(raw_points=18, approved_tests=5, percentage=90.0)},
        severity_counts={"NONE": 20, "LOW": 2, "MEDIUM": 2, "HIGH": 1, "CRITICAL": 0},
        priority_findings=[ReportFinding(test_id="A02", category="accuracy", severity="HIGH",
            finding="Invented discount", business_impact="Customer receives an invalid price.",
            recommendation="Use documented pricing only.")],
    )


def test_pdf_renderer_returns_valid_pdf_bytes():
    pdf = render_audit_report_pdf(sample_report())
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 1000


def test_pdf_renderer_handles_special_characters():
    report = sample_report()
    report.client = "ACME & Partners <Mexico>"
    report.priority_findings[0].finding = "Price < expected & unsupported"
    pdf = render_audit_report_pdf(report)
    assert pdf.startswith(b"%PDF-")
