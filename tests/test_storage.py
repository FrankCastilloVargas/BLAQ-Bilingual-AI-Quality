from pathlib import Path

from app.models.audit import Audit
from app.services import storage


def test_save_and_get_audit(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit = Audit(client="Demo Client", product_name="Demo Bot", reviewer="Human Reviewer")

    storage.save_audit(audit)
    loaded = storage.get_audit(audit.id)

    assert loaded.id == audit.id
    assert loaded.client == "Demo Client"


def test_list_audits(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    storage.save_audit(Audit(client="A", product_name="Bot A", reviewer="Reviewer"))
    storage.save_audit(Audit(client="B", product_name="Bot B", reviewer="Reviewer"))

    assert len(storage.list_audits()) == 2
