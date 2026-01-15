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


def test_ekata_service():
    """Test the simplified /v1/ekata endpoint"""
    payload = {
        "request_id": "req_ekata_simple",
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "ip": "192.168.1.100",
            "phone": "+1-555-1234",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101"
        }
    }
    r = client.post("/v1/ekata", json=payload)
    assert r.status_code == 200
    body = r.json()

    # Verify response structure
    assert body["request_id"] == "req_ekata_simple"
    assert "data" in body
    assert "ekata_payload" in body

    # Verify data fields
    assert body["data"]["fname"] == "John"
    assert body["data"]["l_name"] == "Doe"
    assert body["data"]["email"] == "john.doe@example.com"
    assert body["data"]["ip"] == "192.168.1.100"
    assert body["data"]["homephone"] == "+1-555-1234"
    assert body["data"]["city"] == "Seattle"
    assert body["data"]["state"] == "WA"
    assert body["data"]["zip"] == "98101"

    # Verify ekata_payload fields
    assert "risk_score" in body["ekata_payload"]
    assert "first_name_match" in body["ekata_payload"]
    assert "last_name_match" in body["ekata_payload"]
    assert "email_risk" in body["ekata_payload"]
    assert "ip_risk" in body["ekata_payload"]
    assert "phone_risk" in body["ekata_payload"]

    # Verify risk scores are in valid range
    assert 0 <= body["ekata_payload"]["risk_score"] <= 100
    assert 0 <= body["ekata_payload"]["email_risk"] <= 100
    assert 0 <= body["ekata_payload"]["ip_risk"] <= 100
    assert 0 <= body["ekata_payload"]["phone_risk"] <= 100

    # Verify match fields are boolean
    assert isinstance(body["ekata_payload"]["first_name_match"], bool)
    assert isinstance(body["ekata_payload"]["last_name_match"], bool)


def test_emailage_service():
    """Test the simplified /v1/emailage endpoint"""
    payload = {
        "request_id": "req_emailage_simple",
        "data": {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "ip": "10.0.0.1",
            "phone": "+1-555-5678"
        }
    }
    r = client.post("/v1/emailage", json=payload)
    assert r.status_code == 200
    body = r.json()

    # Verify response structure
    assert body["request_id"] == "req_emailage_simple"
    assert "data" in body
    assert "emailage_payload" in body

    # Verify data fields
    assert body["data"]["first_name"] == "Jane"
    assert body["data"]["last_name"] == "Smith"
    assert body["data"]["email"] == "jane.smith@example.com"
    assert body["data"]["ip"] == "10.0.0.1"
    assert body["data"]["phone"] == "+1-555-5678"

    # Verify emailage_payload fields
    assert "score" in body["emailage_payload"]
    assert "email_first_seen" in body["emailage_payload"]
    assert "email_last_seen" in body["emailage_payload"]
    assert "domain_exists" in body["emailage_payload"]
    assert "disposable" in body["emailage_payload"]
    assert "free_provider" in body["emailage_payload"]

    # Verify score is in valid range
    assert 0 <= body["emailage_payload"]["score"] <= 100

    # Verify boolean fields
    assert isinstance(body["emailage_payload"]["domain_exists"], bool)
    assert isinstance(body["emailage_payload"]["disposable"], bool)
    assert isinstance(body["emailage_payload"]["free_provider"], bool)


def test_ekata_service_minimal():
    """Test /v1/ekata with only required fields"""
    payload = {
        "request_id": "req_ekata_min",
        "data": {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@test.com"
        }
    }
    r = client.post("/v1/ekata", json=payload)
    assert r.status_code == 200
    body = r.json()

    assert body["request_id"] == "req_ekata_min"
    assert body["data"]["fname"] == "Bob"
    assert body["data"]["l_name"] == "Jones"
    assert "ekata_payload" in body


def test_emailage_service_minimal():
    """Test /v1/emailage with only required fields"""
    payload = {
        "request_id": "req_emailage_min",
        "data": {
            "first_name": "Alice",
            "last_name": "Williams",
            "email": "alice@test.com"
        }
    }
    r = client.post("/v1/emailage", json=payload)
    assert r.status_code == 200
    body = r.json()

    assert body["request_id"] == "req_emailage_min"
    assert body["data"]["first_name"] == "Alice"
    assert body["data"]["last_name"] == "Williams"
    assert "emailage_payload" in body


def test_ekata_service_invalid_email():
    """Test /v1/ekata with invalid email"""
    payload = {
        "request_id": "req_ekata_invalid",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "not-an-email"
        }
    }
    r = client.post("/v1/ekata", json=payload)
    assert r.status_code == 422


def test_emailage_service_invalid_email():
    """Test /v1/emailage with invalid email"""
    payload = {
        "request_id": "req_emailage_invalid",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "invalid-email"
        }
    }
    r = client.post("/v1/emailage", json=payload)
    assert r.status_code == 422
