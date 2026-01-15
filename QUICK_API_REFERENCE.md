# Quick API Reference

## Base URL
```
http://localhost:8080
```

## Endpoints Overview

| Method | Endpoint | Purpose | Request Size |
|--------|----------|---------|--------------|
| GET | `/health` | Health check | N/A |
| POST | `/v1/ekata` | ⭐ Ekata identity check | Minimal |
| POST | `/v1/emailage` | ⭐ Email risk check | Minimal |
| POST | `/v1/enrich` | Full enrichment | Large |
| POST | `/v1/enrich/ekata` | Ekata (legacy) | Large |
| POST | `/v1/enrich/emailage` | Emailage (legacy) | Large |
| POST | `/v1/enrich/threatmetrix` | ThreatMetrix | Large |

---

## Quick Examples

### Ekata - Identity Verification

```bash
curl -X POST http://localhost:8080/v1/ekata \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "data": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "ip": "192.168.1.1",
      "phone": "+1-555-1234"
    }
  }'
```

**Response:**
```json
{
  "request_id": "req_001",
  "data": {
    "fname": "John",
    "l_name": "Doe",
    "email": "john@example.com",
    "ip": "192.168.1.1",
    "homephone": "+1-555-1234",
    "workphone": null,
    "city": null,
    "state": null,
    "zip": null
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

---

### Emailage - Email Risk Assessment

```bash
curl -X POST http://localhost:8080/v1/emailage \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_002",
    "data": {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com"
    }
  }'
```

**Response:**
```json
{
  "request_id": "req_002",
  "data": {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "ip": null,
    "phone": null,
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

---

## Field Requirements

### Ekata & Emailage (Simplified APIs)

**Required:**
- `request_id` (string)
- `data.first_name` (string)
- `data.last_name` (string)
- `data.email` (string, valid email)

**Optional:**
- `data.ip` (string)
- `data.phone` (string)
- `data.city` (string)
- `data.state` (string)
- `data.zip` (string)

---

## Response Field Guide

### Ekata Payload

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `risk_score` | int | 0-100 | Overall identity confidence (lower is better) |
| `first_name_match` | bool | - | First name matches records |
| `last_name_match` | bool | - | Last name matches records |
| `email_risk` | int | 0-100 | Email address risk |
| `ip_risk` | int | 0-100 | IP address risk |
| `phone_risk` | int | 0-100 | Phone number risk |

### Emailage Payload

| Field | Type | Description |
|-------|------|-------------|
| `score` | int (0-100) | Email risk score (higher is riskier) |
| `email_first_seen` | datetime | First time email was seen |
| `email_last_seen` | datetime | Most recent email activity |
| `domain_exists` | bool | Domain is valid and exists |
| `disposable` | bool | Disposable/temporary email |
| `free_provider` | bool | Free provider (Gmail, Yahoo, etc.) |

---

## HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | Success | Valid request, data returned |
| 422 | Validation Error | Invalid email, missing fields |
| 500 | Server Error | Internal error |

---

## Common Validation Errors

### Invalid Email
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

### Missing Required Field
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

## Python Integration Examples

### Using Requests

```python
import requests

# Ekata check
ekata_response = requests.post(
    "http://localhost:8080/v1/ekata",
    json={
        "request_id": "req_001",
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "ip": "192.168.1.1"
        }
    }
)

if ekata_response.status_code == 200:
    result = ekata_response.json()
    risk_score = result["ekata_payload"]["risk_score"]
    print(f"Risk score: {risk_score}")

# Emailage check
emailage_response = requests.post(
    "http://localhost:8080/v1/emailage",
    json={
        "request_id": "req_002",
        "data": {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com"
        }
    }
)

if emailage_response.status_code == 200:
    result = emailage_response.json()
    email_score = result["emailage_payload"]["score"]
    print(f"Email score: {email_score}")
```

### Error Handling

```python
try:
    response = requests.post(
        "http://localhost:8080/v1/ekata",
        json=payload
    )
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 422:
        print("Validation error:", e.response.json())
    else:
        print("HTTP error:", e)
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
```

---

## JavaScript/Node.js Integration

```javascript
const axios = require('axios');

async function checkIdentity(data) {
  try {
    const response = await axios.post(
      'http://localhost:8080/v1/ekata',
      {
        request_id: 'req_001',
        data: data
      }
    );

    const riskScore = response.data.ekata_payload.risk_score;
    console.log(`Risk score: ${riskScore}`);
    return response.data;

  } catch (error) {
    if (error.response && error.response.status === 422) {
      console.error('Validation error:', error.response.data);
    } else {
      console.error('Request failed:', error.message);
    }
  }
}

async function checkEmail(data) {
  try {
    const response = await axios.post(
      'http://localhost:8080/v1/emailage',
      {
        request_id: 'req_002',
        data: data
      }
    );

    const emailScore = response.data.emailage_payload.score;
    console.log(`Email score: ${emailScore}`);
    return response.data;

  } catch (error) {
    console.error('Request failed:', error.message);
  }
}

// Usage
checkIdentity({
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  ip: '192.168.1.1'
});

checkEmail({
  first_name: 'Jane',
  last_name: 'Smith',
  email: 'jane@example.com'
});
```

---

## Testing with Postman

1. **Import Collection**: `postman_collection.json`
2. **Import Environment**: `postman_environment.json`
3. **Select Environment**: "Transaction Enrichment API - Local"
4. **Run Collection**: Test all endpoints at once

### Key Test Cases

- ✅ Ekata Service - Simplified API
- ✅ Emailage Service - Simplified API
- ✅ Minimal Fields Tests
- ✅ Invalid Email Tests
- ✅ Full Enrichment Tests

---

## API Decision Tree

```
Need to verify identity data?
├─ YES → Use /v1/ekata
└─ NO

Need to check email reputation?
├─ YES → Use /v1/emailage
└─ NO

Need full transaction enrichment with all services?
├─ YES → Use /v1/enrich
└─ NO

Need specific service with transaction context?
└─ YES → Use /v1/enrich/{service}
```

---

## Performance Tips

1. **Use simplified APIs** when you don't need full transaction context
2. **Cache responses** based on input data (deterministic mocking)
3. **Parallel requests** - Ekata and Emailage can be called independently
4. **Validate locally** before sending to API
5. **Batch processing** - Consider implementing batch endpoint for high volume

---

## Common Integration Patterns

### Pattern 1: Pre-Transaction Check
```python
# Before processing payment
ekata = check_ekata(customer_data)
emailage = check_emailage(customer_data)

if ekata["risk_score"] > 80 or emailage["score"] > 70:
    flag_for_review()
else:
    process_payment()
```

### Pattern 2: Post-Transaction Enrichment
```python
# After transaction completed
enrichment = full_enrich(transaction_data)
risk_score = enrichment["transaction_payload"]["risk"]["blended_score"]

if risk_score >= 60:
    send_to_manual_review()
```

### Pattern 3: Microservice Architecture
```python
# Service 1: Identity Service
identity_result = call_ekata(data)

# Service 2: Email Service
email_result = call_emailage(data)

# Service 3: Risk Engine
final_decision = risk_engine(identity_result, email_result)
```

---

## See Also

- [README.md](README.md) - Setup and installation
- [API_GUIDE.md](API_GUIDE.md) - Detailed API documentation
- [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) - Postman testing guide
- [CHANGELOG.md](CHANGELOG.md) - What's new
