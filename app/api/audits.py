from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.audit import Audit
from app.models.review import HumanReview
from app.services.review import TestNotFoundError, approve_test
from app.services.storage import AuditNotFoundError, get_audit, list_audits, save_audit

router = APIRouter()


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
