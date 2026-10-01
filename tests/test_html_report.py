from app.models.report import AuditReport, CategoryReport, ReportFinding
from app.services.html_report import render_audit_report_html


def sample_report():
    return AuditReport(
        audit_id="audit-1", client="<script>alert(1)</script>", product_name="Demo & Bot",
        model_version="v1", reviewer="Reviewer", audit_date="2026-10-01", status="FINAL",
        executive_summary="Completed & reviewed.", blaq_score=88, provisional_percentage=88.0,
        approved_tests=25, total_tests=25,
        category_scores={"accuracy": CategoryReport(raw_points=18, approved_tests=5, percentage=90.0)},
        severity_counts={"NONE": 20, "LOW": 2, "MEDIUM": 2, "HIGH": 1, "CRITICAL": 0},
        priority_findings=[ReportFinding(test_id="A02", category="accuracy", severity="HIGH",
            finding="<b>Invented discount</b>", business_impact="Wrong price & expectation",
            recommendation="Use documented pricing only.")],
    )


def test_html_renderer_contains_client_report_sections():
    html = render_audit_report_html(sample_report())
    assert "BLAQ-25 Bilingual AI Quality Audit" in html
    assert "88/100" in html
    assert "Category Results" in html
    assert "Priority Findings" in html


def test_html_renderer_escapes_untrusted_text():
    html = render_audit_report_html(sample_report())
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<b>Invented discount</b>" not in html
    assert "&lt;b&gt;Invented discount&lt;/b&gt;" in html
    assert "Demo &amp; Bot" in html
