# Transaction Enrichment API

A FastAPI service that enriches transaction data with external service information (mock data for local development).

**🚀 New here? Start with the [Quick Start Guide](QUICKSTART.md) to get running in 5 minutes!**

## 📚 Documentation

- **[QUICK_API_REFERENCE.md](QUICK_API_REFERENCE.md)** - Quick reference for all API endpoints
- **[API_GUIDE.md](API_GUIDE.md)** - Comprehensive API documentation with examples
- **[POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)** - Postman collection testing guide
- **[CHANGELOG.md](CHANGELOG.md)** - Recent changes and new features

## Features

- **Multiple API modes**: Full enrichment and individual service endpoints
- **Simplified service APIs**: New `/v1/ekata` and `/v1/emailage` endpoints with minimal request/response format
- **Dataset lookup**: Primary lookup by `transaction_id`, fallback by `email` (most recent transaction)
- **Deterministic mocks**: When no dataset match, generates consistent mock data using SHA-256 hashing
- **Health endpoint**: Returns service status and dataset count
- **Full validation**: Pydantic models with email validation
- **VSCode debugging**: Pre-configured debug launch settings

## Project Structure

```
externalservice-sample-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # Pydantic request/response models
│   ├── dataset.py        # JSON dataset loader
│   └── enrich.py         # Enrichment logic
├── data/
│   └── sample_transactions.json
├── tests/
│   ├── __init__.py
│   └── test_enrich.py
├── .vscode/
│   └── launch.json       # VSCode debug config
├── .env                  # Environment configuration
├── .gitignore            # Git ignore rules
├── requirements.txt
├── pytest.ini
├── postman_collection.json     # Postman test collection
├── postman_environment.json    # Postman environment
├── POSTMAN_GUIDE.md           # Detailed Postman testing guide
└── README.md
```

## Setup

### 1. Create and activate conda environment

```bash
conda create -n fastapi-env python=3.11 pip -y
conda activate fastapi-env
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the service

```bash
uvicorn app.main:app --reload --port 8080
```

Or use the VSCode debugger (F5) with the "Run FastAPI (uvicorn)" configuration.

## API Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Transaction Enrichment API                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ⭐ NEW Simplified APIs (Minimal Request/Response)      │
│  ┌────────────────────────────────────────────────┐    │
│  │  POST /v1/ekata        → Ekata identity check  │    │
│  │  POST /v1/emailage     → Email risk check      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Full Enrichment (All Services)                         │
│  ┌────────────────────────────────────────────────┐    │
│  │  POST /v1/enrich       → Complete enrichment   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Legacy Service Endpoints (With Transaction Context)    │
│  ┌────────────────────────────────────────────────┐    │
│  │  POST /v1/enrich/ekata       → Ekata only      │    │
│  │  POST /v1/enrich/emailage    → Emailage only   │    │
│  │  POST /v1/enrich/threatmetrix → ThreatMetrix   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Health & Monitoring                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  GET /health           → Service status        │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

The API provides both **comprehensive enrichment** (all services) and **individual service** endpoints:

1. `/v1/enrich` - Full transaction enrichment with all external services
2. `/v1/ekata` - ⭐ **NEW** Simplified Ekata identity verification only
3. `/v1/emailage` - ⭐ **NEW** Simplified Emailage email risk assessment only
4. `/v1/enrich/emailage` - Legacy Emailage enrichment (with transaction details)
5. `/v1/enrich/threatmetrix` - Legacy ThreatMetrix enrichment (with transaction details)
6. `/v1/enrich/ekata` - Legacy Ekata enrichment (with transaction details)

### Health Check

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "ok",
  "dataset_path": "data/sample_transactions.json",
  "dataset_count": 1,
  "utc_now": "2026-01-14T12:00:00+00:00"
}
```

### Ekata Service (Simplified)

**Endpoint:** `POST /v1/ekata`

Identity verification service that returns risk assessment for provided identity data.

**Request:**
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

**Response:**
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

**Required Fields:**
- `request_id` (string)
- `data.first_name` (string)
- `data.last_name` (string)
- `data.email` (string, valid email format)

**Optional Fields:**
- `data.ip` (string)
- `data.phone` (string)
- `data.city` (string)
- `data.state` (string)
- `data.zip` (string)

### Emailage Service (Simplified)

**Endpoint:** `POST /v1/emailage`

Email risk assessment service that returns email reputation and history.

**Request:**
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

**Response:**
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

**Required Fields:**
- `request_id` (string)
- `data.first_name` (string)
- `data.last_name` (string)
- `data.email` (string, valid email format)

**Optional Fields:**
- `data.ip` (string)
- `data.phone` (string)
- `data.city` (string)
- `data.state` (string)
- `data.zip` (string)

### Enrich Transaction (Full)

```bash
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_abc123",
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
    },
    "payment": {
      "amount": 42.19,
      "currency": "USD",
      "card": {
        "bin": "411111",
        "last4": "1111",
        "network": "VISA"
      }
    },
    "merchant_id": "M12345",
    "channel": "web"
  }'
```

**Response:**
```json
{
  "request_id": "req_abc123",
  "transaction_id": "tx_1001",
  "transaction_time": "2026-01-14T05:22:31+00:00",
  "dataset_hit": true,
  "data": { ... },
  "transaction_payload": {
    "transaction": { ... },
    "customer": { ... },
    "external_services": {
      "emailage": { ... },
      "threatmetrix": { ... },
      "ekata": { ... }
    },
    "risk": {
      "blended_score": 19,
      "reason_codes": [],
      "recommended_action": "ALLOW"
    }
  }
}
```

## Testing

### Pytest (Unit/Integration Tests)

Run all tests:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=app
```

### Postman (API/E2E Tests)

See [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) for detailed instructions.

**Quick Start:**
1. Import `postman_collection.json` and `postman_environment.json` into Postman
2. Select "Transaction Enrichment API - Local" environment
3. Run collection or individual requests

**15+ comprehensive test cases included** covering:
- Health checks
- Full transaction enrichment (dataset hits and mock data)
- Individual service endpoints (Ekata, Emailage, ThreatMetrix)
- **NEW** Simplified service APIs (`/v1/ekata`, `/v1/emailage`)
- Dataset lookups and email fallback
- Mock data generation
- Validation errors
- Risk scoring

## Configuration

Edit `.env` to configure:

```env
DATASET_PATH=data/sample_transactions.json
PORT=8080
```

## How It Works

### Dataset Lookup Strategy

1. **Primary**: Match by `transaction_id`
2. **Fallback**: Match by `email` (returns most recent transaction)
3. **Mock**: Generate deterministic mock data if no match

### Mock Data Generation

When no dataset match is found, the service generates deterministic mock data using:
- SHA-256 hashing for consistent results
- Input seed: `transaction_id|email|ip|bin`
- Generates realistic scores, dates, and flags

### Risk Scoring

Blended risk score calculation:
```
blended_score = (0.55 × threatmetrix_score) + (0.45 × emailage_score)
```

Recommended actions:
- `blended_score >= 60`: REVIEW
- `blended_score < 60`: ALLOW

## Adding More Dataset Records

Edit `data/sample_transactions.json` and add more records:

```json
[
  {
    "transaction": { ... },
    "customer": { ... },
    "external_services": { ... }
  },
  {
    "transaction": { ... },
    "customer": { ... },
    "external_services": { ... }
  }
]
```

**Note**: Restart the service to reload the dataset, or implement a `/reload` endpoint.

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Postman Collection

Import the Postman collection and environment for comprehensive API testing:

**Files:**
- `postman_collection.json` - Full test suite with 9 test cases
- `postman_environment.json` - Environment variables

**How to import:**

1. Open Postman
2. Click **Import** button
3. Drag and drop both JSON files or browse to select them
4. Select the "Transaction Enrichment API - Local" environment
5. Run individual requests or use **Collection Runner** to run all tests

**Test Cases Included:**

1. **Health Check** - Verify service status
2. **Dataset Hit** - Test successful dataset lookup by transaction_id
3. **Mock Data Generation** - Test fallback to deterministic mocks
4. **Email Fallback Lookup** - Test secondary lookup by email
5. **Minimal Required Fields** - Test with bare minimum data
6. **Full Address & Device** - Test with all optional fields
7. **Invalid Email Validation** - Test email validation error (422)
8. **Missing Required Fields** - Test missing field validation (422)
9. **High Risk Scoring** - Test risk assessment logic

Each test includes automated assertions to validate:
- Response status codes
- Response structure
- Field presence and types
- Business logic (dataset hits, risk scores, etc.)

## Development

### VSCode Debugging

Press F5 to start debugging with breakpoints. The launch configuration is pre-configured in `.vscode/launch.json`.

### Adding New Fields

1. Update Pydantic models in `app/models.py`
2. Update enrichment logic in `app/enrich.py`
3. Add tests in `tests/test_enrich.py`

## License

MIT