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


def test_human_review_approves_and_persists_test(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    payload = {
        "client": "Demo Client", "product_name": "Demo Bot", "reviewer": "Human Reviewer",
        "tests": [{
            "test_id": "A01", "category": "accuracy", "language": "es-MX",
            "scenario": "Demo", "prompt": "Demo", "expected_behavior": "Demo", "actual_response": "Demo",
            "evaluation": {
                "scores": {"accuracy": 2, "language": 3, "context": 3, "safety": 3, "escalation": 3},
                "severity": "MEDIUM", "finding": "AI proposal", "approved": False
            }
        }]
    }
    audit_id = client.post("/audits", json=payload).json()["id"]
    review = {
        "scores": {"accuracy": 1, "language": 4, "context": 4, "safety": 2, "escalation": 3},
        "severity": "HIGH", "finding": "Human-confirmed failure",
        "business_impact": "Customer may receive incorrect information.",
        "recommendation": "Use documented policy only.", "review_notes": "Reviewed manually."
    }
    response = client.put(f"/audits/{audit_id}/tests/A01/review", json=review)
    assert response.status_code == 200
    evaluation = response.json()["tests"][0]["evaluation"]
    assert evaluation["approved"] is True
    assert evaluation["scores"]["accuracy"] == 1
    assert evaluation["severity"] == "HIGH"
    persisted = client.get(f"/audits/{audit_id}").json()["tests"][0]["evaluation"]
    assert persisted["approved"] is True


def test_review_unknown_test_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit_id = client.post("/audits", json={"client": "Demo", "product_name": "Bot", "reviewer": "Reviewer", "tests": []}).json()["id"]
    review = {
        "scores": {"accuracy": 4, "language": 4, "context": 4, "safety": 4, "escalation": 4},
        "severity": "NONE", "finding": "", "business_impact": "", "recommendation": "", "review_notes": ""
    }
    assert client.put(f"/audits/{audit_id}/tests/A99/review", json=review).status_code == 404
