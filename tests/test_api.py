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


def test_report_endpoint_returns_provisional_report(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    payload = {
        "client": "Demo Client", "product_name": "Demo Bot", "reviewer": "Reviewer",
        "tests": [{
            "test_id": "A01", "category": "accuracy", "language": "es-MX", "scenario": "Demo",
            "prompt": "Demo", "expected_behavior": "Demo", "actual_response": "Demo",
            "evaluation": {
                "scores": {"accuracy": 3, "language": 4, "context": 4, "safety": 4, "escalation": 4},
                "severity": "MEDIUM", "finding": "Confirmed issue", "business_impact": "Impact",
                "recommendation": "Recommendation", "approved": True
            }
        }]
    }
    audit_id = client.post("/audits", json=payload).json()["id"]
    response = client.get(f"/audits/{audit_id}/report")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PROVISIONAL"
    assert body["blaq_score"] is None
    assert body["approved_tests"] == 1
    assert body["priority_findings"][0]["test_id"] == "A01"


def test_html_report_endpoint_returns_printable_document(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit_id = client.post("/audits", json={
        "client": "Demo", "product_name": "Bot", "reviewer": "Reviewer", "tests": []
    }).json()["id"]
    response = client.get(f"/audits/{audit_id}/report.html")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "BLAQ-25 Bilingual AI Quality Audit" in response.text
    assert "PROVISIONAL" in response.text


def test_pdf_report_endpoint_returns_downloadable_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit_id = client.post("/audits", json={
        "client": "Demo", "product_name": "Bot", "reviewer": "Reviewer", "tests": []
    }).json()["id"]
    response = client.get(f"/audits/{audit_id}/report.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")


def test_create_blaq25_audit_from_official_catalog(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    response = client.post("/audits/blaq25", json={
        "client": "ACME", "product_name": "Support Bot", "model_version": "v2", "reviewer": "Reviewer"
    })
    assert response.status_code == 201
    body = response.json()
    assert len(body["tests"]) == 25
    assert body["tests"][0]["test_id"] == "A01"
    assert body["tests"][-1]["test_id"] == "E05"
    assert all(item["actual_response"] is None for item in body["tests"])
    assert all(item["evaluation"] is None for item in body["tests"])
    persisted = client.get(f'/audits/{body["id"]}')
    assert persisted.status_code == 200
    assert len(persisted.json()["tests"]) == 25


def test_update_test_response_persists_without_approving(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit = client.post("/audits/blaq25", json={
        "client": "ACME", "product_name": "Bot", "reviewer": "Reviewer"
    }).json()
    audit_id = audit["id"]
    response = client.put(f"/audits/{audit_id}/tests/A02/response", json={
        "actual_response": "Dos servicios cuestan $160 por descuento."
    })
    assert response.status_code == 200
    test = next(item for item in response.json()["tests"] if item["test_id"] == "A02")
    assert test["actual_response"] == "Dos servicios cuestan $160 por descuento."
    assert test["evaluation"] is None
    persisted = client.get(f"/audits/{audit_id}").json()
    saved = next(item for item in persisted["tests"] if item["test_id"] == "A02")
    assert saved["actual_response"] == test["actual_response"]


def test_update_test_response_rejects_unknown_test(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit_id = client.post("/audits/blaq25", json={
        "client": "ACME", "product_name": "Bot", "reviewer": "Reviewer"
    }).json()["id"]
    response = client.put(f"/audits/{audit_id}/tests/A99/response", json={"actual_response": "x"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Test not found"


def test_update_test_response_rejects_empty_response(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit_id = client.post("/audits/blaq25", json={
        "client": "ACME", "product_name": "Bot", "reviewer": "Reviewer"
    }).json()["id"]
    response = client.put(f"/audits/{audit_id}/tests/A01/response", json={"actual_response": ""})
    assert response.status_code == 422


def test_propose_stored_response_and_preserve_human_review_boundary(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path / "audits")
    audit_id = client.post("/audits/blaq25", json={
        "client": "ACME", "product_name": "Bot", "reviewer": "Reviewer"
    }).json()["id"]
    url = f"/audits/{audit_id}/tests/A02"
    assert client.post(f"{url}/propose").status_code == 409
    client.put(f"{url}/response", json={"actual_response": "Definitely $160."})
    proposed = client.post(f"{url}/propose")
    assert proposed.status_code == 200
    assert proposed.json()["test_id"] == "A02"
    assert proposed.json()["evaluation"]["approved"] is False
    saved = client.get(f"/audits/{audit_id}").json()
    a02 = next(t for t in saved["tests"] if t["test_id"] == "A02")
    assert a02["evaluation"]["severity"] == "MEDIUM"
    assert a02["evaluation"]["approved"] is False
    assert client.get(f"/audits/{audit_id}/report").json()["approved_tests"] == 0
    client.put(f"{url}/response", json={"actual_response": "The price is $178."})
    saved = client.get(f"/audits/{audit_id}").json()
    assert next(t for t in saved["tests"] if t["test_id"] == "A02")["evaluation"] is None
    assert client.post(f"/audits/{audit_id}/tests/A99/propose").status_code == 404
