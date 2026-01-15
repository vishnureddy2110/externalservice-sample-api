# Service-Specific Enrichment Endpoints

The API now includes dedicated endpoints for each external service, allowing you to request enrichment from individual services instead of getting all services at once.

## Overview

| Endpoint | Service | Purpose |
|----------|---------|---------|
| `POST /v1/enrich` | All Services | Legacy endpoint - returns all services (backward compatible) |
| `POST /v1/enrich/emailage` | Emailage | Email risk assessment and validation |
| `POST /v1/enrich/threatmetrix` | ThreatMetrix | Device fingerprinting and fraud detection |
| `POST /v1/enrich/ekata` | Ekata | Identity verification |

---

## Endpoint Details

### 1. Emailage Endpoint

**Endpoint:** `POST /v1/enrich/emailage`

**Description:** Returns Emailage email risk assessment data only.

**Request:**
```json
{
  "request_id": "req_email_001",
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
```

**Response:**
```json
{
  "request_id": "req_email_001",
  "transaction_id": "tx_1001",
  "transaction_time": "2026-01-14T05:22:31+00:00",
  "dataset_hit": true,
  "service": "emailage",
  "data": {
    "first_name": "Vishnu",
    "last_name": "Reddy",
    "email": "vik@example.com",
    "ip": "73.14.55.10",
    "phone": "+1-555-9999"
  },
  "enrichment": {
    "score": 21,
    "email_first_seen": "2019-07-10T00:00:00Z",
    "email_last_seen": "2026-01-09T00:00:00Z",
    "domain_exists": true,
    "disposable": false,
    "free_provider": true
  }
}
```

**Enrichment Fields:**
- `score` (0-100): Email risk score (higher = riskier)
- `email_first_seen`: First time email was seen in Emailage database
- `email_last_seen`: Most recent time email was seen
- `domain_exists`: Whether email domain is valid
- `disposable`: Whether email is from disposable email provider
- `free_provider`: Whether email is from free email provider (Gmail, Yahoo, etc.)

---

### 2. ThreatMetrix Endpoint

**Endpoint:** `POST /v1/enrich/threatmetrix`

**Description:** Returns ThreatMetrix device fingerprinting and fraud detection data only.

**Request:**
```json
{
  "request_id": "req_tm_001",
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
```

**Response:**
```json
{
  "request_id": "req_tm_001",
  "transaction_id": "tx_1001",
  "transaction_time": "2026-01-14T05:22:31+00:00",
  "dataset_hit": true,
  "service": "threatmetrix",
  "data": {
    "first_name": "Vishnu",
    "last_name": "Reddy",
    "email": "vik@example.com",
    "ip": "73.14.55.10",
    "phone": "+1-555-9999"
  },
  "enrichment": {
    "risk_score": 18,
    "policy": "ALLOW",
    "device_risk": 12,
    "ip_risk": 9,
    "true_ip": true,
    "bot_detected": false
  }
}
```

**Enrichment Fields:**
- `risk_score` (0-100): Overall ThreatMetrix risk score
- `policy`: Recommended action ("ALLOW", "REVIEW", or "REJECT")
- `device_risk` (0-100): Device fingerprint risk score
- `ip_risk` (0-100): IP address risk score
- `true_ip`: Whether IP matches claimed location
- `bot_detected`: Whether automated bot activity detected

---

### 3. Ekata Endpoint

**Endpoint:** `POST /v1/enrich/ekata`

**Description:** Returns Ekata identity verification data only.

**Request:**
```json
{
  "request_id": "req_ekata_001",
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
```

**Response:**
```json
{
  "request_id": "req_ekata_001",
  "transaction_id": "tx_1001",
  "transaction_time": "2026-01-14T05:22:31+00:00",
  "dataset_hit": true,
  "service": "ekata",
  "data": {
    "first_name": "Vishnu",
    "last_name": "Reddy",
    "email": "vik@example.com",
    "ip": "73.14.55.10",
    "phone": "+1-555-9999"
  },
  "enrichment": {
    "identity_confidence": 78,
    "phone_to_name_match": true,
    "address_to_name_match": true,
    "email_to_name_match": true
  }
}
```

**Enrichment Fields:**
- `identity_confidence` (0-100): Overall identity verification confidence score
- `phone_to_name_match`: Whether phone number matches provided name
- `address_to_name_match`: Whether address matches provided name
- `email_to_name_match`: Whether email matches provided name

---

## Usage Examples

### Using curl

**Emailage:**
```bash
curl -X POST http://localhost:8080/v1/enrich/emailage \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "transaction_id": "tx_1001",
    "transaction_time": "2026-01-14T05:22:31Z",
    "data": {
      "first_name": "Vishnu",
      "last_name": "Reddy",
      "email": "vik@example.com",
      "ip": "73.14.55.10"
    }
  }'
```

**ThreatMetrix:**
```bash
curl -X POST http://localhost:8080/v1/enrich/threatmetrix \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_002",
    "transaction_id": "tx_1001",
    "transaction_time": "2026-01-14T05:22:31Z",
    "data": {
      "first_name": "Vishnu",
      "last_name": "Reddy",
      "email": "vik@example.com",
      "ip": "73.14.55.10"
    }
  }'
```

**Ekata:**
```bash
curl -X POST http://localhost:8080/v1/enrich/ekata \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_003",
    "transaction_id": "tx_1001",
    "transaction_time": "2026-01-14T05:22:31Z",
    "data": {
      "first_name": "Vishnu",
      "last_name": "Reddy",
      "email": "vik@example.com",
      "ip": "73.14.55.10"
    }
  }'
```

---

## Response Structure

All service-specific endpoints follow the same response structure:

```json
{
  "request_id": "string",
  "transaction_id": "string",
  "transaction_time": "ISO 8601 timestamp",
  "dataset_hit": boolean,
  "service": "emailage|threatmetrix|ekata",
  "data": {
    // Echo of input data
  },
  "enrichment": {
    // Service-specific fields
  }
}
```

**Common Fields:**
- `request_id`: Your request identifier (echoed back)
- `transaction_id`: Transaction identifier
- `transaction_time`: Transaction timestamp in UTC
- `dataset_hit`: `true` if data found in dataset, `false` if using mock data
- `service`: Which service provided the enrichment
- `data`: Echo of the input customer data
- `enrichment`: Service-specific enrichment data

---

## Dataset Lookup Behavior

The service-specific endpoints use the same dataset lookup logic as the main `/v1/enrich` endpoint:

1. **Primary Lookup:** Match by `transaction_id`
2. **Fallback Lookup:** Match by `email` (returns most recent transaction)
3. **Mock Generation:** If no match, generate deterministic mock data

**Dataset Hit (`dataset_hit: true`):**
- Returns actual service data from `data/sample_transactions.json`
- Data matches historical transaction

**Mock Data (`dataset_hit: false`):**
- Generates deterministic mock data using SHA-256 hashing
- Same inputs always produce same outputs (for testing consistency)
- Seed: `transaction_id|email|ip|bin`

---

## Comparison: All Services vs. Service-Specific

### All Services Endpoint (`/v1/enrich`)

**Use When:**
- You need data from all three services
- You want risk scoring (blended score from multiple services)
- You need full transaction payload with all enrichment

**Response Includes:**
- Transaction details
- Customer information
- All three external services (emailage, threatmetrix, ekata)
- Risk assessment (blended score, reason codes, recommended action)
- Features and velocity data

---

### Service-Specific Endpoints

**Use When:**
- You only need data from one specific service
- You want to reduce response size
- You're implementing progressive enrichment (call services one at a time)
- You want to test individual services independently

**Response Includes:**
- Request metadata
- Customer data (echo)
- Single service enrichment data only

---

## Testing

### Pytest Tests

Run tests for all endpoints:
```bash
pytest -v tests/test_enrich.py
```

**Test Coverage:**
- ✅ `test_enrich_emailage_endpoint` - Dataset hit for Emailage
- ✅ `test_enrich_threatmetrix_endpoint` - Dataset hit for ThreatMetrix
- ✅ `test_enrich_ekata_endpoint` - Dataset hit for Ekata
- ✅ `test_enrich_emailage_mock_data` - Mock data generation

---

### Postman Tests

The Postman collection now includes **12 test cases** (up from 9):

**New Tests:**
1. **Enrich - Emailage Only** - Test Emailage endpoint with dataset hit
2. **Enrich - ThreatMetrix Only** - Test ThreatMetrix endpoint with dataset hit
3. **Enrich - Ekata Only** - Test Ekata endpoint with dataset hit

**Import Collection:**
1. Open Postman
2. Import `postman_collection.json`
3. Select "Transaction Enrichment API - Local" environment
4. Run collection

**Each test validates:**
- Correct HTTP status code (200)
- Service field matches endpoint
- Enrichment data structure
- Score/confidence ranges (0-100)
- Data type validations

---

## API Documentation

Once the service is running, visit:
- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc

All four endpoints are documented with:
- Request/response schemas
- Example payloads
- Field descriptions
- Try-it-out functionality

---

## Migration Guide

### Existing Code Using `/v1/enrich`

**No changes required!** The `/v1/enrich` endpoint remains unchanged and backward compatible.

```python
# This still works exactly as before
response = requests.post(
    "http://localhost:8080/v1/enrich",
    json=payload
)
```

### Adopting Service-Specific Endpoints

**Option 1: Call services individually**
```python
# Get only Emailage data
emailage_response = requests.post(
    "http://localhost:8080/v1/enrich/emailage",
    json=payload
)

# Get only ThreatMetrix data
tm_response = requests.post(
    "http://localhost:8080/v1/enrich/threatmetrix",
    json=payload
)
```

**Option 2: Progressive enrichment**
```python
# Start with lightweight check
emailage_response = requests.post(
    "http://localhost:8080/v1/enrich/emailage",
    json=payload
)

if emailage_response.json()["enrichment"]["score"] > 50:
    # High risk - get more data
    tm_response = requests.post(
        "http://localhost:8080/v1/enrich/threatmetrix",
        json=payload
    )
```

---

## Performance Considerations

### Response Size Comparison

| Endpoint | Approx. Response Size | Services Included |
|----------|----------------------|-------------------|
| `/v1/enrich` | ~2-3 KB | All 3 services + risk scoring |
| `/v1/enrich/emailage` | ~500 bytes | Emailage only |
| `/v1/enrich/threatmetrix` | ~400 bytes | ThreatMetrix only |
| `/v1/enrich/ekata` | ~350 bytes | Ekata only |

**Benefits:**
- Smaller payloads = faster network transfer
- Only request services you actually need
- Easier to cache individual service responses

---

## Error Handling

All endpoints use the same validation and error handling:

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "data", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

**Common Validation Errors:**
- Invalid email format
- Missing required fields (`request_id`, `transaction_id`, `transaction_time`, `data`)
- Invalid date format
- Invalid data types

---

## Future Enhancements

Potential additions to consider:

- [ ] Batch endpoint for multiple transactions
- [ ] Webhook callbacks for async enrichment
- [ ] Rate limiting per service
- [ ] Service-specific API keys
- [ ] Caching layer per service
- [ ] Service health checks (individual service status)

---

## Support

**Questions or Issues?**
- Check main [README.md](README.md)
- Review [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)
- Visit API docs at http://localhost:8080/docs

**Last Updated:** 2026-01-14
**API Version:** 0.1.0
