# Test Cases Summary

## Overview

The Transaction Enrichment API includes comprehensive test coverage through both **pytest** (unit/integration tests) and **Postman** (API/E2E tests).

---

## Pytest Test Suite

**Location:** `tests/test_enrich.py`

**Run Command:**
```bash
pytest -v
```

### Test Cases

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_health` | Verify service health endpoint | Status 200, dataset count >= 0 |
| `test_enrich_dataset_hit` | Test dataset lookup by transaction_id | Status 200, dataset_hit = true |

**Coverage:**
- Health endpoint functionality
- Dataset loading and lookup
- Request/response validation
- External services data structure

---

## Postman Test Suite

**Location:** `postman_collection.json`

**Import to Postman:** Drag & drop the JSON file into Postman

### Test Cases Matrix

| # | Test Name | Method | Endpoint | Purpose | Expected Status | Key Validation |
|---|-----------|--------|----------|---------|----------------|----------------|
| 1 | Health Check | GET | `/health` | Service status | 200 | Status = "ok", dataset_count exists |
| 2 | Enrich - Dataset Hit | POST | `/v1/enrich` | Lookup by transaction_id | 200 | dataset_hit = true, external services present |
| 3 | Enrich - Mock Data | POST | `/v1/enrich` | Fallback to mocks | 200 | dataset_hit = false, deterministic mocks |
| 4 | Enrich - Email Lookup | POST | `/v1/enrich` | Secondary lookup by email | 200 | dataset_hit = true via email |
| 5 | Enrich - Minimal Fields | POST | `/v1/enrich` | Required fields only | 200 | Response structure valid |
| 6 | Enrich - Full Data | POST | `/v1/enrich` | All optional fields | 200 | Addresses & device present |
| 7 | Invalid Email | POST | `/v1/enrich` | Email validation | 422 | Validation error returned |
| 8 | Missing Fields | POST | `/v1/enrich` | Required field validation | 422 | Missing field errors |
| 9 | High Risk Score | POST | `/v1/enrich` | Risk scoring logic | 200 | Risk fields calculated |

---

## Test Coverage Breakdown

### Functional Coverage

✅ **Core Features**
- [x] Health check endpoint
- [x] Dataset lookup (primary: transaction_id)
- [x] Dataset lookup (fallback: email)
- [x] Deterministic mock data generation
- [x] Risk score calculation
- [x] External services enrichment

✅ **Data Validation**
- [x] Email format validation
- [x] Required field validation
- [x] Optional field handling
- [x] Nested object validation (address, device, card)

✅ **Edge Cases**
- [x] Minimal required fields
- [x] Full data with all optional fields
- [x] Invalid email format
- [x] Missing required fields
- [x] Non-existent transaction_id
- [x] Non-existent email

✅ **Business Logic**
- [x] Dataset hit detection
- [x] Risk score blending (threatmetrix + emailage)
- [x] Recommended action logic (ALLOW vs REVIEW)
- [x] Reason codes generation

---

## Automated Test Assertions

### Postman Automated Checks

Each Postman test includes multiple assertions:

**Example: "Enrich Transaction - Dataset Hit"**
- ✓ Status code is 200
- ✓ Response has correct structure
- ✓ Dataset hit is true
- ✓ Transaction payload has required fields
- ✓ External services are present (emailage, threatmetrix, ekata)
- ✓ Risk score is calculated and in valid range (0-100)

**Total Automated Assertions:** 30+ across all tests

---

## Test Data Summary

### Dataset Records

**File:** `data/sample_transactions.json`

**Records:** 1 transaction

| Field | Value |
|-------|-------|
| transaction_id | `tx_1001` |
| customer.email | `vik@example.com` |
| customer.name | Vik Reddy |
| transaction_time | 2026-01-10T18:22:31Z |
| amount | $42.19 USD |
| status | Completed |
| decision | APPROVE |

### Mock Test Data

Tests use various synthetic data:

**Valid Transactions:**
- tx_9999, tx_full_001, tx_risk_001 (non-existent, trigger mocks)

**Valid Emails:**
- john.doe@example.com
- alice.j@example.com
- risky@suspicious-domain.com

**Invalid Data:**
- Email: "not-an-email" (triggers 422)
- Missing fields (triggers 422)

---

## Test Execution Guide

### Quick Test Run

**Option 1: Pytest (Fast)**
```bash
pytest -v
# Expected: 2 passed in ~0.3s
```

**Option 2: Postman Collection Runner**
1. Import collection & environment
2. Click **Run Collection**
3. View results
4. Expected: 9 requests, 30+ tests passed

**Option 3: Manual Postman Tests**
- Test each endpoint individually
- Review response and test results tab

---

## Test Results Interpretation

### Success Indicators

✅ **All Green**
- All pytest tests pass
- All Postman tests pass (green checkmarks)
- No 5xx server errors
- Response times < 500ms

### Common Failures

❌ **Dataset Not Loaded**
- Symptom: dataset_count = 0 in /health
- Fix: Check dataset file path, restart service

❌ **Email Validation Fails**
- Symptom: 422 error on valid-looking email
- Fix: Ensure email format is correct (user@domain.com)

❌ **Connection Refused**
- Symptom: "Could not get any response" in Postman
- Fix: Ensure service is running on localhost:8080

---

## Continuous Testing

### Local Development

**Run tests before committing:**
```bash
# Unit tests
pytest -v

# Manual API tests
# Open Postman → Run Collection
```

### CI/CD Integration

**Using Newman (Postman CLI):**
```bash
npm install -g newman
newman run postman_collection.json -e postman_environment.json
```

**GitHub Actions Example:**
```yaml
- name: Run API Tests
  run: |
    uvicorn app.main:app --host 0.0.0.0 --port 8080 &
    sleep 5
    newman run postman_collection.json -e postman_environment.json
```

---

## Test Maintenance

### When to Update Tests

- ✏️ API endpoint changes (URL, method)
- ✏️ Request/response schema changes
- ✏️ New required fields added
- ✏️ Business logic changes (risk scoring)
- ✏️ New features added

### Best Practices

1. **Keep tests in sync** with API changes
2. **Add tests for new features** immediately
3. **Test edge cases** not just happy paths
4. **Use descriptive test names** for clarity
5. **Document expected behavior** in test descriptions

---

## Coverage Gaps & Future Tests

### Potential Additional Tests

**Performance Testing:**
- [ ] Load test with 100+ concurrent requests
- [ ] Large dataset (1000+ records) performance
- [ ] Response time benchmarks

**Security Testing:**
- [ ] SQL injection attempts (if using database)
- [ ] XSS in input fields
- [ ] Rate limiting tests
- [ ] Authentication/authorization (if added)

**Data Validation:**
- [ ] Invalid date formats
- [ ] Negative amounts
- [ ] Invalid card BIN/last4 formats
- [ ] Special characters in names
- [ ] Unicode email addresses

**Business Logic:**
- [ ] Multiple transactions same email (most recent)
- [ ] Dataset reload functionality
- [ ] Risk score edge cases (score = 0, 100)
- [ ] All reason codes triggered

---

## Quick Reference

### File Locations

```
tests/test_enrich.py          - Pytest unit tests
postman_collection.json       - Postman API tests
postman_environment.json      - Postman environment
POSTMAN_GUIDE.md             - Detailed Postman guide
TEST_CASES_SUMMARY.md        - This file
```

### Commands

```bash
# Run pytest
pytest -v

# Run pytest with coverage
pytest -v --cov=app

# Run Postman via Newman
newman run postman_collection.json -e postman_environment.json

# Start service
uvicorn app.main:app --reload --port 8080
```

---

## Support & Documentation

- **API Docs:** http://localhost:8080/docs
- **Postman Guide:** [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)
- **Main README:** [README.md](README.md)
- **Test Files:** `tests/` directory

---

**Last Updated:** 2026-01-14
**Test Coverage:** 30+ automated assertions
**Test Execution Time:** < 5 seconds for full suite
