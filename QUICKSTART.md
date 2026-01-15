# Quick Start Guide

Get the Transaction Enrichment API running in 5 minutes!

---

## Prerequisites

- Python 3.11+
- Conda (or pip with venv)
- Postman (optional, for API testing)

---

## Step 1: Setup Environment (2 minutes)

```bash
# Navigate to project directory
cd externalservice-sample-api

# Create conda environment
conda create -n fastapi-env python=3.11 pip -y

# Activate environment
conda activate fastapi-env

# Install dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.115.8 uvicorn-0.34.0 pydantic-2.10.6 ...
```

---

## Step 2: Start the Service (30 seconds)

```bash
# Start the API service
uvicorn app.main:app --reload --port 8080
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Service is now running!**

---

## Step 3: Verify Health (10 seconds)

Open a new terminal and run:

```bash
curl http://localhost:8080/health
```

**Expected response:**
```json
{
  "status": "ok",
  "dataset_path": "data/sample_transactions.json",
  "dataset_count": 1,
  "utc_now": "2026-01-14T12:00:00+00:00"
}
```

✅ **API is healthy!**

---

## Step 4: Test API Call (30 seconds)

### Using curl

```bash
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_test",
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

**Expected response (abbreviated):**
```json
{
  "request_id": "req_test",
  "transaction_id": "tx_1001",
  "dataset_hit": true,
  "transaction_payload": {
    "external_services": {
      "emailage": { "score": 21, ... },
      "threatmetrix": { "risk_score": 18, ... },
      "ekata": { "identity_confidence": 78, ... }
    },
    "risk": {
      "blended_score": 19,
      "recommended_action": "ALLOW"
    }
  }
}
```

✅ **API is working!**

---

## Step 5: Explore API Docs (1 minute)

Open your browser and visit:

**Swagger UI (Interactive):**
```
http://localhost:8080/docs
```

**ReDoc (Documentation):**
```
http://localhost:8080/redoc
```

✅ **You can now test the API interactively!**

---

## Step 6: Run Tests (1 minute)

### Pytest Tests

```bash
# In a new terminal (keep service running)
pytest -v
```

**Expected output:**
```
======================== test session starts ========================
collected 2 items

tests/test_enrich.py::test_health PASSED                     [ 50%]
tests/test_enrich.py::test_enrich_dataset_hit PASSED         [100%]

========================= 2 passed in 0.25s =========================
```

✅ **All tests passed!**

---

## Step 7: Import Postman Collection (Optional, 2 minutes)

1. Open Postman
2. Click **Import**
3. Drag these files:
   - `postman_collection.json`
   - `postman_environment.json`
4. Select "Transaction Enrichment API - Local" environment
5. Click on any request and hit **Send**

✅ **You can now test with Postman!**

---

## What's Next?

### Explore Features

**1. Test Dataset Hit:**
```bash
# This transaction exists in the dataset
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{"request_id":"r1","transaction_id":"tx_1001","transaction_time":"2026-01-14T05:22:31Z","data":{"first_name":"Vishnu","last_name":"Reddy","email":"vik@example.com"}}'
```
→ Returns: `dataset_hit: true`

**2. Test Mock Data Generation:**
```bash
# This transaction does NOT exist - will generate mocks
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{"request_id":"r2","transaction_id":"tx_9999","transaction_time":"2026-01-14T05:22:31Z","data":{"first_name":"John","last_name":"Doe","email":"john@example.com"}}'
```
→ Returns: `dataset_hit: false` with deterministic mock data

**3. Test Email Fallback:**
```bash
# Different transaction ID but same email from dataset
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{"request_id":"r3","transaction_id":"tx_new","transaction_time":"2026-01-14T05:22:31Z","data":{"first_name":"Test","last_name":"User","email":"vik@example.com"}}'
```
→ Returns: `dataset_hit: true` (found via email)

---

### Development Workflow

**VSCode Debugging:**
1. Open project in VSCode
2. Press **F5**
3. Service starts with debugger attached
4. Set breakpoints in code
5. Send requests to trigger breakpoints

**Live Reload:**
- Edit any file in `app/` directory
- Service automatically reloads
- No need to restart manually

---

### Modify Dataset

Edit `data/sample_transactions.json` to add more records:

```json
[
  {
    "transaction": {
      "transaction_id": "tx_1001",
      ...
    },
    "customer": {
      "email": "vik@example.com",
      ...
    },
    "external_services": { ... }
  },
  {
    "transaction": {
      "transaction_id": "tx_1002",
      ...
    },
    "customer": {
      "email": "another@example.com",
      ...
    },
    "external_services": { ... }
  }
]
```

**Restart service** to reload dataset:
```bash
# Press CTRL+C to stop
# Then restart
uvicorn app.main:app --reload --port 8080
```

---

## Common Commands Reference

```bash
# Start service
uvicorn app.main:app --reload --port 8080

# Run tests
pytest -v

# Run tests with coverage
pytest -v --cov=app

# Check health
curl http://localhost:8080/health

# Test enrich endpoint
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Run Postman tests via CLI (if Newman installed)
newman run postman_collection.json -e postman_environment.json
```

---

## Project Structure Quick Reference

```
externalservice-sample-api/
├── app/
│   ├── main.py          ← FastAPI app (start here)
│   ├── models.py        ← Request/response models
│   ├── dataset.py       ← Dataset loader
│   └── enrich.py        ← Enrichment logic
├── data/
│   └── sample_transactions.json  ← Dataset file (edit this)
├── tests/
│   └── test_enrich.py   ← Pytest tests
├── postman_collection.json       ← API test cases
├── postman_environment.json      ← Environment config
└── README.md            ← Full documentation
```

---

## Troubleshooting

### Port already in use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8081

# Or kill the process using port 8080
lsof -ti:8080 | xargs kill -9
```

---

### Module not found

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure environment is activated
conda activate fastapi-env

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Dataset count is 0

**Error:**
```json
{ "dataset_count": 0 }
```

**Solution:**
```bash
# Verify dataset file exists
ls data/sample_transactions.json

# Check file contents
cat data/sample_transactions.json

# Restart service to reload
# (Press CTRL+C, then restart)
```

---

### Tests fail with "Could not get any response"

**Solution:**
```bash
# Ensure service is running
curl http://localhost:8080/health

# Check correct port in Postman environment
# (should be http://localhost:8080)
```

---

## Documentation Links

- **Full Documentation:** [README.md](README.md)
- **Postman Guide:** [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)
- **Test Coverage:** [TEST_CASES_SUMMARY.md](TEST_CASES_SUMMARY.md)
- **Architecture:** [TESTING_ARCHITECTURE.md](TESTING_ARCHITECTURE.md)
- **API Docs (live):** http://localhost:8080/docs

---

## Support

**Having issues?**
1. Check this guide first
2. Review [README.md](README.md) for detailed info
3. Check service logs in terminal
4. Verify all prerequisites installed
5. Try restarting service

---

## Success Checklist

After completing this guide, you should have:

- ✅ Service running on http://localhost:8080
- ✅ Health endpoint returning `"status": "ok"`
- ✅ Successfully called `/v1/enrich` endpoint
- ✅ Viewed API docs at http://localhost:8080/docs
- ✅ All pytest tests passing (2 tests)
- ✅ (Optional) Postman collection imported and working

**Congratulations! You're ready to develop!** 🎉

---

**Quick Start Time:** ~5 minutes
**Last Updated:** 2026-01-14
