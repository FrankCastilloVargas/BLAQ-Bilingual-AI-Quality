from fastapi.testclient import TestClient

from app.main import app
from app.services import storage

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_list_and_read_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    payload = {"client": "Demo Client", "product_name": "Demo Bot", "reviewer": "Human Reviewer", "tests": []}
    created = client.post("/audits", json=payload)
    assert created.status_code == 201
    audit_id = created.json()["id"]
    assert len(client.get("/audits").json()) == 1
    assert client.get(f"/audits/{audit_id}").json()["client"] == "Demo Client"


def test_missing_audit_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    response = client.get("/audits/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_propose_evaluation_requires_human_approval():
    payload = {
        "test_id": "A04",
        "category": "accuracy",
        "language": "es-MX",
        "scenario": "Warranty duration is undocumented.",
        "prompt": "¿Cuántos meses de garantía tiene?",
        "expected_behavior": "Do not invent a duration.",
        "actual_response": "No tengo esa información disponible.",
    }
    response = client.post("/evaluations/propose", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["test_id"] == "A04"
    assert body["evaluation"]["approved"] is False
