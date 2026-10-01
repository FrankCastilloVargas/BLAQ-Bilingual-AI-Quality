from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.report import AuditReport


def render_audit_report_pdf(report: AuditReport) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=0.65*inch, leftMargin=0.65*inch,
                            topMargin=0.6*inch, bottomMargin=0.6*inch,
                            title=f"BLAQ-25 Report - {report.client}", author="BLAQ")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("BlaqTitle", parent=styles["Title"], fontSize=22, leading=26, alignment=TA_CENTER, spaceAfter=10)
    score_style = ParagraphStyle("Score", parent=styles["Heading1"], fontSize=26, leading=30, alignment=TA_CENTER, spaceAfter=12)
    h2 = ParagraphStyle("BlaqH2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=8)
    body = styles["BodyText"]
    small = ParagraphStyle("Small", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#667085"))

    story = [Paragraph("BLAQ-25 Bilingual AI Quality Audit", title),
             Paragraph(f"<b>{escape(report.status)}</b>", styles["Heading3"]), Spacer(1, 8)]
    meta = [
        ["Client", escape(report.client), "Product", escape(report.product_name)],
        ["Model", escape(report.model_version or "Not specified"), "Audit date", escape(report.audit_date)],
        ["Reviewer", escape(report.reviewer), "Approved tests", f"{report.approved_tests}/25"],
    ]
    table = Table(meta, colWidths=[0.9*inch, 2.2*inch, 1.0*inch, 2.2*inch])
    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#D9DEE8")),
                               ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#F3F5F8")),
                               ("BACKGROUND",(2,0),(2,-1),colors.HexColor("#F3F5F8")),
                               ("VALIGN",(0,0),(-1,-1),"TOP"),("FONTNAME",(0,0),(-1,-1),"Helvetica"),
                               ("FONTSIZE",(0,0),(-1,-1),9),("PADDING",(0,0),(-1,-1),6)]))
    story += [table, Paragraph("Executive Summary", h2)]
    score = f"{report.blaq_score}/100" if report.blaq_score is not None else "Pending"
    story += [Paragraph(score, score_style), Paragraph(escape(report.executive_summary), body)]

    story.append(Paragraph("Category Results", h2))
    rows = [["Category", "Points", "Percentage"]]
    for name, item in report.category_scores.items():
        pct = f"{item.percentage}%" if item.percentage is not None else "Pending"
        rows.append([name.title(), f"{item.raw_points}/{item.max_points}", pct])
    category_table = Table(rows, colWidths=[2.7*inch, 1.6*inch, 1.8*inch], repeatRows=1)
    category_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#172033")),
                                        ("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#D9DEE8")),
                                        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),
                                        ("PADDING",(0,0),(-1,-1),7)]))
    story.append(category_table)

    story.append(Paragraph("Priority Findings", h2))
    if not report.priority_findings:
        story.append(Paragraph("No human-approved findings with severity above NONE.", body))
    for finding in report.priority_findings:
        story += [Paragraph(f"<b>{escape(finding.test_id)} · {escape(finding.severity)}</b>", styles["Heading3"]),
                  Paragraph(f"<b>Finding:</b> {escape(finding.finding)}", body),
                  Paragraph(f"<b>Business impact:</b> {escape(finding.business_impact)}", body),
                  Paragraph(f"<b>Recommendation:</b> {escape(finding.recommendation)}", body), Spacer(1, 8)]

    story += [Spacer(1, 18), Paragraph(f"BLAQ — Bilingual Language &amp; AI Quality · Human-reviewed assessment · Audit ID {escape(report.audit_id)}", small)]
    doc.build(story)
    return buffer.getvalue()
