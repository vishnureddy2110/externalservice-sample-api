# Transaction Enrichment API

A FastAPI service that enriches transaction data with external service information (mock data for local development).

**🚀 New here? Start with the [Quick Start Guide](QUICKSTART.md) to get running in 5 minutes!**

## Features

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

## API Endpoints

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

### Enrich Transaction

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

**9 comprehensive test cases included** covering:
- Health checks
- Dataset lookups
- Mock data generation
- Validation errors
- Risk scoring

See [TEST_CASES_SUMMARY.md](TEST_CASES_SUMMARY.md) for complete test coverage matrix.

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