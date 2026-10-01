from html import escape

from app.models.report import AuditReport


def render_audit_report_html(report: AuditReport) -> str:
    score = f"{report.blaq_score}/100" if report.blaq_score is not None else "Pending"
    categories = "".join(
        f"<tr><td>{escape(name.title())}</td><td>{item.raw_points}/{item.max_points}</td>"
        f"<td>{item.percentage if item.percentage is not None else 'Pending'}%</td></tr>"
        for name, item in report.category_scores.items()
    )
    findings = "".join(
        "<article class='finding'>"
        f"<h3>{escape(item.test_id)} · {escape(item.severity)}</h3>"
        f"<p><strong>Finding:</strong> {escape(item.finding)}</p>"
        f"<p><strong>Business impact:</strong> {escape(item.business_impact)}</p>"
        f"<p><strong>Recommendation:</strong> {escape(item.recommendation)}</p>"
        "</article>"
        for item in report.priority_findings
    ) or "<p>No human-approved findings with severity above NONE.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BLAQ-25 Report — {escape(report.client)}</title>
<style>
:root {{ font-family: Inter, Arial, sans-serif; color: #172033; background: #f5f7fa; }}
body {{ margin: 0; }} main {{ max-width: 920px; margin: 0 auto; padding: 48px; background: white; }}
header {{ border-bottom: 3px solid #172033; padding-bottom: 24px; margin-bottom: 32px; }}
h1 {{ margin: 0 0 8px; font-size: 34px; }} h2 {{ margin-top: 36px; }}
.meta {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 24px; }}
.score {{ font-size: 44px; font-weight: 700; margin: 12px 0; }}
.badge {{ display: inline-block; padding: 5px 10px; border: 1px solid currentColor; border-radius: 999px; font-weight: 700; }}
table {{ width: 100%; border-collapse: collapse; }} th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #d9dee8; }}
.finding {{ break-inside: avoid; padding: 16px 0; border-bottom: 1px solid #d9dee8; }}
footer {{ margin-top: 48px; font-size: 12px; color: #667085; }}
@media print {{ :root {{ background: white; }} main {{ padding: 20mm; max-width: none; }} }}
</style>
</head>
<body><main>
<header><h1>BLAQ-25 Bilingual AI Quality Audit</h1><span class="badge">{escape(report.status)}</span></header>
<section class="meta">
<div><strong>Client:</strong> {escape(report.client)}</div><div><strong>Product:</strong> {escape(report.product_name)}</div>
<div><strong>Model:</strong> {escape(report.model_version or "Not specified")}</div><div><strong>Audit date:</strong> {escape(report.audit_date)}</div>
<div><strong>Reviewer:</strong> {escape(report.reviewer)}</div><div><strong>Approved tests:</strong> {report.approved_tests}/25</div>
</section>
<h2>Executive Summary</h2><div class="score">{score}</div><p>{escape(report.executive_summary)}</p>
<h2>Category Results</h2><table><thead><tr><th>Category</th><th>Points</th><th>Percentage</th></tr></thead><tbody>{categories}</tbody></table>
<h2>Priority Findings</h2>{findings}
<footer>BLAQ — Bilingual Language & AI Quality · Human-reviewed assessment · Audit ID {escape(report.audit_id)}</footer>
</main></body></html>"""
