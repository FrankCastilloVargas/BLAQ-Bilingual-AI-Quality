from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse, Response

from app.models.audit import Audit
from app.models.audit_create import AuditCreateFromCatalog
from app.models.review import HumanReview
from app.models.report import AuditReport
from app.models.test_response import TestResponseUpdate
from app.services.review import TestNotFoundError, approve_test
from app.services.catalog import CatalogValidationError, create_audit_from_catalog
from app.services.reporting import build_audit_report
from app.services.responses import set_test_response
from app.services.html_report import render_audit_report_html
from app.services.pdf_report import render_audit_report_pdf
from app.services.storage import AuditNotFoundError, get_audit, list_audits, save_audit

router = APIRouter()


@router.post("/blaq25", response_model=Audit, status_code=status.HTTP_201_CREATED)
def create_blaq25_audit(request: AuditCreateFromCatalog) -> Audit:
    try:
        return save_audit(create_audit_from_catalog(request))
    except CatalogValidationError as exc:
        raise HTTPException(status_code=500, detail="BLAQ-25 catalog is invalid") from exc


@router.post("", response_model=Audit, status_code=status.HTTP_201_CREATED)
def create_audit(audit: Audit) -> Audit:
    return save_audit(audit)


@router.get("", response_model=list[Audit])
def read_audits() -> list[Audit]:
    return list_audits()


@router.get("/{audit_id}", response_model=Audit)
def read_audit(audit_id: UUID) -> Audit:
    try:
        return get_audit(audit_id)
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc


@router.put("/{audit_id}/tests/{test_id}/response", response_model=Audit)
def update_test_response(audit_id: UUID, test_id: str, request: TestResponseUpdate) -> Audit:
    try:
        audit = get_audit(audit_id)
        set_test_response(audit, test_id, request.actual_response)
        return save_audit(audit)
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc
    except TestNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Test not found") from exc


@router.put("/{audit_id}/tests/{test_id}/review", response_model=Audit)
def review_test(audit_id: UUID, test_id: str, review: HumanReview) -> Audit:
    try:
        audit = get_audit(audit_id)
        approve_test(audit, test_id, review)
        return save_audit(audit)
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc
    except TestNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Test not found") from exc


@router.get("/{audit_id}/report", response_model=AuditReport)
def read_audit_report(audit_id: UUID) -> AuditReport:
    try:
        return build_audit_report(get_audit(audit_id))
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc


@router.get("/{audit_id}/report.html", response_class=HTMLResponse)
def read_audit_report_html(audit_id: UUID) -> HTMLResponse:
    try:
        report = build_audit_report(get_audit(audit_id))
        return HTMLResponse(content=render_audit_report_html(report))
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc


@router.get("/{audit_id}/report.pdf")
def read_audit_report_pdf(audit_id: UUID) -> Response:
    try:
        report = build_audit_report(get_audit(audit_id))
        pdf = render_audit_report_pdf(report)
        filename = f"blaq25-{audit_id}.pdf"
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        })
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc
