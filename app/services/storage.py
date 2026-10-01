import json
from pathlib import Path
from uuid import UUID

from app.models.audit import Audit

DATA_DIR = Path("data/audits")


class AuditNotFoundError(KeyError):
    pass


def _path(audit_id: UUID) -> Path:
    return DATA_DIR / f"{audit_id}.json"


def save_audit(audit: Audit) -> Audit:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _path(audit.id).write_text(
        json.dumps(audit.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return audit


def get_audit(audit_id: UUID) -> Audit:
    path = _path(audit_id)
    if not path.exists():
        raise AuditNotFoundError(str(audit_id))
    return Audit.model_validate_json(path.read_text(encoding="utf-8"))


def list_audits() -> list[Audit]:
    if not DATA_DIR.exists():
        return []
    return [
        Audit.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(DATA_DIR.glob("*.json"))
    ]
