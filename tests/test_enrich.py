import pytest
from fastapi.testclient import TestClient
from app.main import app, store

# Manually load the dataset for tests
store.load()

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    json_response = r.json()
    assert json_response["status"] == "ok"
    assert json_response["dataset_count"] >= 0

def test_enrich_dataset_hit():
    payload = {
        "request_id": "req_1",
        "transaction_id": "tx_1001",
        "transaction_time": "2026-01-14T05:22:31Z",
        "data": {
            "first_name": "Vishnu",
            "last_name": "Reddy",
            "email": "vik@example.com",
            "ip": "73.14.55.10",
            "phone": "+1-555-9999",
            "city": "hyd",
            "state": "in",
            "zip": "50044"
        }
    }
    r = client.post("/v1/enrich", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["dataset_hit"] is True
    assert "external_services" in body["transaction_payload"]

def test_enrich_emailage_endpoint():
    payload = {
        "request_id": "req_emailage",
        "transaction_id": "tx_1001",
        "transaction_time": "2026-01-14T05:22:31Z",
        "data": {
            "first_name": "Vishnu",
            "last_name": "Reddy",
            "email": "vik@example.com",
            "ip": "73.14.55.10",
            "phone": "+1-555-9999"
        }
    }
    r = client.post("/v1/enrich/emailage", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "emailage"
    assert body["dataset_hit"] is True
    assert "enrichment" in body
    assert "score" in body["enrichment"]

def test_enrich_threatmetrix_endpoint():
    payload = {
        "request_id": "req_tm",
        "transaction_id": "tx_1001",
        "transaction_time": "2026-01-14T05:22:31Z",
        "data": {
            "first_name": "Vishnu",
            "last_name": "Reddy",
            "email": "vik@example.com",
            "ip": "73.14.55.10",
            "phone": "+1-555-9999"
        }
    }
    r = client.post("/v1/enrich/threatmetrix", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "threatmetrix"
    assert body["dataset_hit"] is True
    assert "enrichment" in body
    assert "risk_score" in body["enrichment"]

def test_enrich_ekata_endpoint():
    payload = {
        "request_id": "req_ekata",
        "transaction_id": "tx_1001",
        "transaction_time": "2026-01-14T05:22:31Z",
        "data": {
            "first_name": "Vishnu",
            "last_name": "Reddy",
            "email": "vik@example.com",
            "ip": "73.14.55.10",
            "phone": "+1-555-9999"
        }
    }
    r = client.post("/v1/enrich/ekata", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "ekata"
    assert body["dataset_hit"] is True
    assert "enrichment" in body
    assert "identity_confidence" in body["enrichment"]

def test_enrich_emailage_mock_data():
    payload = {
        "request_id": "req_mock",
        "transaction_id": "tx_9999",
        "transaction_time": "2026-01-14T05:22:31Z",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "ip": "192.168.1.1"
        }
    }
    r = client.post("/v1/enrich/emailage", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "emailage"
    assert body["dataset_hit"] is False
    assert "enrichment" in body
    assert "score" in body["enrichment"]
