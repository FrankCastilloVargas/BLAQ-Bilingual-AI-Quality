from fastapi.testclient import TestClient

from app.main import app
from app.services import storage

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_read_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    payload = {
        "client": "Demo Client",
        "product_name": "Demo Bot",
        "reviewer": "Human Reviewer",
        "tests": [],
    }
    created = client.post("/audits", json=payload)
    assert created.status_code == 201
    audit_id = created.json()["id"]

    fetched = client.get(f"/audits/{audit_id}")
    assert fetched.status_code == 200
    assert fetched.json()["client"] == "Demo Client"
