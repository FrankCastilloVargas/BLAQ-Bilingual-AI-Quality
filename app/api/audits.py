from fastapi import APIRouter

from app.models.audit import Audit

router = APIRouter()


@router.post("", response_model=Audit)
def create_audit(audit: Audit) -> Audit:
    """Validate and echo an audit payload for the MVP."""
    return audit
