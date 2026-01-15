# Transaction Enrichment API Guide

## Overview

This API provides transaction enrichment services with multiple integration options:

1. **Full Enrichment** - All external services in one call
2. **Individual Services** - Simplified APIs for specific services (Ekata, Emailage)
3. **Legacy Service Endpoints** - Backward compatible endpoints with transaction context

## API Endpoints Summary

| Endpoint | Type | Description |
|----------|------|-------------|
| `GET /health` | Health | Service health check |
| `POST /v1/enrich` | Full | Complete transaction enrichment with all services |
| `POST /v1/ekata` | **NEW** Simple | Ekata identity verification only |
| `POST /v1/emailage` | **NEW** Simple | Emailage email risk assessment only |
| `POST /v1/enrich/ekata` | Legacy | Ekata with transaction context |
| `POST /v1/enrich/emailage` | Legacy | Emailage with transaction context |
| `POST /v1/enrich/threatmetrix` | Legacy | ThreatMetrix with transaction context |

---

## Simplified Service APIs

### Why Use Simplified APIs?

The new simplified APIs (`/v1/ekata` and `/v1/emailage`) are designed for:

- **Lightweight integration** - Minimal request payload
- **Focused response** - Only service-specific data
- **Independent verification** - No transaction context required
- **Microservice architecture** - Easy to integrate with event-driven systems

### POST /v1/ekata

Identity verification service that validates and assesses risk for customer identity data.

#### Request Model

```json
{
  "request_id": "string (required)",
  "data": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required, valid email)",
    "ip": "string (optional)",
    "phone": "string (optional)",
    "city": "string (optional)",
    "state": "string (optional)",
    "zip": "string (optional)"
  }
}
```

#### Response Model

```json
{
  "request_id": "string",
  "data": {
    "fname": "string",
    "l_name": "string",
    "email": "string",
    "ip": "string or null",
    "homephone": "string or null",
    "workphone": "string or null",
    "city": "string or null",
    "state": "string or null",
    "zip": "string or null"
  },
  "ekata_payload": {
    "risk_score": "integer (0-100)",
    "first_name_match": "boolean",
    "last_name_match": "boolean",
    "email_risk": "integer (0-100)",
    "ip_risk": "integer (0-100)",
    "phone_risk": "integer (0-100)"
  }
}
```

#### Example Request

```bash
curl -X POST http://localhost:8080/v1/ekata \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_ekata_001",
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
  }'
```

#### Example Response

```json
{
  "request_id": "req_ekata_001",
  "data": {
    "fname": "John",
    "l_name": "Doe",
    "email": "john.doe@example.com",
    "ip": "192.168.1.100",
    "homephone": "+1-555-1234",
    "workphone": null,
    "city": "Seattle",
    "state": "WA",
    "zip": "98101"
  },
  "ekata_payload": {
    "risk_score": 45,
    "first_name_match": true,
    "last_name_match": true,
    "email_risk": 23,
    "ip_risk": 12,
    "phone_risk": 8
  }
}
```

#### Field Descriptions

**ekata_payload Fields:**

- `risk_score`: Overall identity confidence score (0-100, lower is better)
- `first_name_match`: Whether the first name matches identity records
- `last_name_match`: Whether the last name matches identity records
- `email_risk`: Email address risk score (0-100)
- `ip_risk`: IP address risk score (0-100)
- `phone_risk`: Phone number risk score (0-100)

---

### POST /v1/emailage

Email risk assessment service that evaluates email reputation and history.

#### Request Model

```json
{
  "request_id": "string (required)",
  "data": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required, valid email)",
    "ip": "string (optional)",
    "phone": "string (optional)",
    "city": "string (optional)",
    "state": "string (optional)",
    "zip": "string (optional)"
  }
}
```

#### Response Model

```json
{
  "request_id": "string",
  "data": {
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "ip": "string or null",
    "phone": "string or null",
    "city": "string or null",
    "state": "string or null",
    "zip": "string or null"
  },
  "emailage_payload": {
    "score": "integer (0-100)",
    "email_first_seen": "ISO 8601 datetime",
    "email_last_seen": "ISO 8601 datetime",
    "domain_exists": "boolean",
    "disposable": "boolean",
    "free_provider": "boolean"
  }
}
```

#### Example Request

```bash
curl -X POST http://localhost:8080/v1/emailage \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_emailage_001",
    "data": {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@example.com",
      "ip": "10.0.0.1",
      "phone": "+1-555-5678"
    }
  }'
```

#### Example Response

```json
{
  "request_id": "req_emailage_001",
  "data": {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "ip": "10.0.0.1",
    "phone": "+1-555-5678",
    "city": null,
    "state": null,
    "zip": null
  },
  "emailage_payload": {
    "score": 34,
    "email_first_seen": "2021-03-15T10:30:00+00:00",
    "email_last_seen": "2026-01-10T14:22:00+00:00",
    "domain_exists": true,
    "disposable": false,
    "free_provider": true
  }
}
```

#### Field Descriptions

**emailage_payload Fields:**

- `score`: Email risk score (0-100, higher is riskier)
- `email_first_seen`: First time this email was seen in the system
- `email_last_seen`: Most recent activity for this email
- `domain_exists`: Whether the email domain exists and is valid
- `disposable`: Whether this is a disposable/temporary email address
- `free_provider`: Whether this email is from a free provider (Gmail, Yahoo, etc.)

---

## Full Enrichment API

### POST /v1/enrich

Complete transaction enrichment with all external services (Emailage, ThreatMetrix, Ekata).

#### Request Model

```json
{
  "request_id": "string (required)",
  "transaction_id": "string (required)",
  "transaction_time": "ISO 8601 datetime (required)",
  "data": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required)",
    "ip": "string (optional)",
    "phone": "string (optional)",
    "city": "string (optional)",
    "state": "string (optional)",
    "zip": "string (optional)",
    "billing_address": { ... },
    "shipping_address": { ... },
    "device": { ... }
  },
  "payment": {
    "amount": "float (optional)",
    "currency": "string (optional)",
    "card": { ... }
  },
  "customer_id": "integer (optional)",
  "merchant_id": "string (optional)",
  "channel": "string (optional)"
}
```

#### Response Structure

The response includes:
- Request metadata
- Dataset hit status
- Customer data
- Complete transaction payload with:
  - Transaction details
  - Customer information
  - External services data (Emailage, ThreatMetrix, Ekata)
  - Blended risk assessment

See [README.md](README.md) for full example.

---

## Legacy Service Endpoints

These endpoints maintain backward compatibility with the original API design.

### POST /v1/enrich/ekata

Returns Ekata data with transaction context.

### POST /v1/enrich/emailage

Returns Emailage data with transaction context.

### POST /v1/enrich/threatmetrix

Returns ThreatMetrix data with transaction context.

**Note:** These endpoints require the full `EnrichRequest` model (same as `/v1/enrich`).

---

## Data Generation Strategy

### Dataset Lookup

1. **Primary**: Match by `transaction_id`
2. **Fallback**: Match by `email` (returns most recent transaction)
3. **Mock**: Generate deterministic mock data if no match

### Deterministic Mock Data

When no dataset match is found, the service generates deterministic mock data using:

- **SHA-256 hashing** for consistent results
- **Seed composition**: `request_id|email|ip`
- Generates realistic scores, dates, and boolean flags
- Same input always produces the same output

This ensures:
- Reproducible testing
- Consistent behavior across environments
- Predictable responses for development

---

## Error Handling

### Validation Errors (422)

The API validates all input data. Common validation errors:

**Invalid Email Format:**
```json
{
  "detail": [
    {
      "loc": ["body", "data", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Missing Required Fields:**
```json
{
  "detail": [
    {
      "loc": ["body", "data", "first_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Integration Patterns

### Pattern 1: Individual Services

Use simplified APIs for microservice architectures:

```python
# Verify identity with Ekata
ekata_response = requests.post(
    "http://localhost:8080/v1/ekata",
    json={
        "request_id": "req_001",
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }
    }
)

# Check email reputation with Emailage
emailage_response = requests.post(
    "http://localhost:8080/v1/emailage",
    json={
        "request_id": "req_002",
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }
    }
)
```

### Pattern 2: Full Enrichment

Use full enrichment for comprehensive risk assessment:

```python
response = requests.post(
    "http://localhost:8080/v1/enrich",
    json={
        "request_id": "req_001",
        "transaction_id": "tx_001",
        "transaction_time": "2026-01-14T10:00:00Z",
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "ip": "192.168.1.1"
        },
        "payment": {
            "amount": 100.00,
            "currency": "USD"
        }
    }
)

risk_score = response.json()["transaction_payload"]["risk"]["blended_score"]
```

---

## Testing

### Postman Collection

Import the Postman collection for comprehensive API testing:

- **File**: `postman_collection.json`
- **Environment**: `postman_environment.json`

The collection includes:
- 9 Full enrichment tests
- 6+ Simplified API tests (Ekata, Emailage)
- Validation error tests
- Dataset hit/miss scenarios

### Pytest

Run automated tests:

```bash
pytest -v
pytest -v --cov=app  # With coverage
```

---

## Rate Limiting & Performance

This is a **local development/mock service**. For production use:

- Implement rate limiting
- Add caching layer
- Configure connection pooling
- Monitor service health
- Implement circuit breakers for external service calls

---

## Next Steps

1. **Start the service**: `uvicorn app.main:app --reload --port 8080`
2. **Test health endpoint**: `curl http://localhost:8080/health`
3. **Try simplified APIs**: Use the examples above
4. **Import Postman collection**: Test all endpoints interactively
5. **Review test suite**: See `tests/test_enrich.py` for integration examples

For more details, see:
- [README.md](README.md) - Quick start and setup
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) - Postman testing guide
