# Testing Architecture

## Overview

The Transaction Enrichment API uses a multi-layered testing approach to ensure quality and reliability.

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Layers                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │         API/E2E Tests (Postman)                     │   │
│  │  • 9 test cases                                      │   │
│  │  • End-to-end workflows                             │   │
│  │  • Manual & automated execution                     │   │
│  │  • 30+ assertions                                   │   │
│  └────────────────────────────────────────────────────┘   │
│                          ▲                                  │
│                          │                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │    Integration Tests (pytest + TestClient)          │   │
│  │  • 2 test cases                                      │   │
│  │  • FastAPI TestClient                               │   │
│  │  • Dataset integration                              │   │
│  └────────────────────────────────────────────────────┘   │
│                          ▲                                  │
│                          │                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Application Layer                            │   │
│  │  • FastAPI endpoints                                │   │
│  │  • Pydantic validation                              │   │
│  │  • Business logic                                   │   │
│  └────────────────────────────────────────────────────┘   │
│                          ▲                                  │
│                          │                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Data Layer                                   │   │
│  │  • Dataset store                                    │   │
│  │  • Mock data generation                             │   │
│  │  • Enrichment logic                                 │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Test Types

### 1. Unit Tests (pytest)

**Purpose:** Test individual functions and modules in isolation

**Location:** `tests/test_enrich.py`

**Coverage:**
- ✓ Health endpoint
- ✓ Dataset lookup logic
- ✓ Request validation

**Execution:**
```bash
pytest -v
```

**Benefits:**
- Fast execution (< 1 second)
- Early bug detection
- Easy debugging
- CI/CD friendly

---

### 2. Integration Tests (pytest + FastAPI TestClient)

**Purpose:** Test component interactions and data flow

**Location:** `tests/test_enrich.py`

**Coverage:**
- ✓ FastAPI routing
- ✓ Pydantic validation
- ✓ Dataset store integration
- ✓ Response formatting

**Execution:**
```bash
pytest -v
```

**Benefits:**
- Tests actual FastAPI behavior
- Validates request/response flow
- No external dependencies needed

---

### 3. API Tests (Postman)

**Purpose:** Test complete workflows and user scenarios

**Location:** `postman_collection.json`

**Coverage:**
- ✓ Happy paths
- ✓ Error scenarios
- ✓ Edge cases
- ✓ Business logic
- ✓ Validation rules

**Execution:**
- Postman GUI: Import and run
- CLI: `newman run postman_collection.json`

**Benefits:**
- Manual exploration
- Non-developer friendly
- Documentation via examples
- Share with stakeholders

---

## Test Flow Diagram

```
┌──────────────┐
│   Developer  │
└──────┬───────┘
       │
       │ Makes code changes
       │
       ▼
┌──────────────────────────────────────────┐
│   Local Development                       │
│                                           │
│   1. Run pytest                           │
│      $ pytest -v                          │
│      ✓ 2 tests passed                    │
│                                           │
│   2. Start service                        │
│      $ uvicorn app.main:app --reload     │
│                                           │
│   3. Run Postman tests                    │
│      • Import collection                  │
│      • Run Collection Runner              │
│      ✓ 9 requests, 30+ tests passed     │
│                                           │
└──────────────────────────────────────────┘
       │
       │ Commit & Push
       │
       ▼
┌──────────────────────────────────────────┐
│   CI/CD Pipeline (Optional)               │
│                                           │
│   1. Install dependencies                 │
│   2. Run pytest with coverage            │
│   3. Start service                        │
│   4. Run Newman (Postman CLI)            │
│   5. Generate reports                     │
│                                           │
└──────────────────────────────────────────┘
       │
       │ All tests pass
       │
       ▼
┌──────────────────────────────────────────┐
│   Deployment                              │
└──────────────────────────────────────────┘
```

---

## Test Coverage Map

### Endpoint Coverage

| Endpoint | pytest | Postman | Coverage % |
|----------|--------|---------|------------|
| GET /health | ✓ | ✓ | 100% |
| POST /v1/enrich | ✓ | ✓ (9 scenarios) | 100% |

### Feature Coverage

| Feature | pytest | Postman | Notes |
|---------|--------|---------|-------|
| Dataset lookup (by ID) | ✓ | ✓ | tx_1001 |
| Dataset lookup (by email) | Partial | ✓ | vik@example.com |
| Mock data generation | Partial | ✓ | Deterministic |
| Email validation | ✗ | ✓ | 422 error |
| Required field validation | ✗ | ✓ | 422 error |
| Risk scoring | Partial | ✓ | Blended score |
| Full address handling | ✗ | ✓ | Optional fields |
| Device info handling | ✗ | ✓ | Optional fields |

### Edge Case Coverage

| Edge Case | pytest | Postman | Status |
|-----------|--------|---------|--------|
| Minimal required fields | ✗ | ✓ | Covered |
| All optional fields | ✗ | ✓ | Covered |
| Invalid email format | ✗ | ✓ | Covered |
| Missing required fields | ✗ | ✓ | Covered |
| Non-existent transaction | Implicit | ✓ | Covered |
| High risk transaction | ✗ | ✓ | Covered |

**Legend:**
- ✓ = Covered
- ✗ = Not covered
- Partial = Partially covered

---

## Test Data Strategy

### Dataset Records

```
┌─────────────────────────────────────┐
│  data/sample_transactions.json      │
│                                     │
│  • tx_1001 (vik@example.com)       │
│  • Complete external services       │
│  • Known risk scores               │
│  • Reference for "dataset hit"      │
└─────────────────────────────────────┘
```

### Mock Data Generation

```
┌─────────────────────────────────────────────┐
│  Deterministic Mock Generation               │
│                                              │
│  Input: transaction_id + email + ip + bin   │
│         │                                    │
│         ▼                                    │
│  SHA-256 Hash                               │
│         │                                    │
│         ▼                                    │
│  Scores, dates, flags                       │
│  (same input → same output)                 │
└─────────────────────────────────────────────┘
```

**Benefits:**
- No external API dependencies
- Predictable test results
- Fast execution
- Offline testing

---

## Test Execution Matrix

### Local Development

| Scenario | Command | Expected Time | When to Run |
|----------|---------|---------------|-------------|
| Quick sanity check | `pytest -v` | < 1s | After every code change |
| Full API validation | Postman Collection Runner | < 5s | Before commit |
| Manual exploration | Postman individual requests | Varies | Feature development |
| Coverage report | `pytest --cov=app` | < 2s | Before PR |

### CI/CD Pipeline

| Stage | Tool | Command | Success Criteria |
|-------|------|---------|------------------|
| Unit tests | pytest | `pytest -v` | All pass |
| Integration tests | pytest | `pytest -v` | All pass |
| API tests | Newman | `newman run ...` | All pass, < 5s |
| Coverage check | pytest-cov | `pytest --cov=app --cov-report=html` | > 80% |

---

## Test Automation Flow

```
┌───────────────────────────────────────────────────────┐
│                  Git Push                              │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────┐
│  GitHub Actions / CI Tool                              │
│                                                        │
│  1. Checkout code                                     │
│  2. Setup Python 3.11                                 │
│  3. Install dependencies                              │
│     $ pip install -r requirements.txt                │
│                                                        │
│  4. Run pytest                                        │
│     $ pytest -v --cov=app                            │
│     ├─ If FAIL → ❌ Build fails                      │
│     └─ If PASS → ✓ Continue                         │
│                                                        │
│  5. Start service (background)                        │
│     $ uvicorn app.main:app --port 8080 &             │
│                                                        │
│  6. Wait for service ready                            │
│     $ curl http://localhost:8080/health              │
│                                                        │
│  7. Install Newman                                    │
│     $ npm install -g newman                          │
│                                                        │
│  8. Run Postman tests                                 │
│     $ newman run postman_collection.json             │
│     ├─ If FAIL → ❌ Build fails                      │
│     └─ If PASS → ✓ Continue                         │
│                                                        │
│  9. Generate reports                                  │
│     - Coverage report (HTML)                          │
│     - Newman test results                             │
│                                                        │
│  10. Upload artifacts                                 │
│      - Test reports                                   │
│      - Coverage reports                               │
│                                                        │
└───────────────────────────────────────────────────────┘
                     │
                     ▼
            ✅ All tests passed
                     │
                     ▼
            Ready for deployment
```

---

## Test Reporting

### Pytest Output

```
======================== test session starts ========================
platform darwin -- Python 3.11.13, pytest-8.3.4
collected 2 items

tests/test_enrich.py::test_health PASSED                     [ 50%]
tests/test_enrich.py::test_enrich_dataset_hit PASSED         [100%]

========================= 2 passed in 0.25s =========================
```

### Postman Collection Runner

```
┌─────────────────────────┬──────────┬──────────┐
│                         │ executed │   failed │
├─────────────────────────┼──────────┼──────────┤
│              iterations │        1 │        0 │
├─────────────────────────┼──────────┼──────────┤
│                requests │        9 │        0 │
├─────────────────────────┼──────────┼──────────┤
│            test-scripts │       18 │        0 │
├─────────────────────────┼──────────┼──────────┤
│      prerequest-scripts │        0 │        0 │
├─────────────────────────┼──────────┼──────────┤
│              assertions │       32 │        0 │
└─────────────────────────┴──────────┴──────────┘
```

### Coverage Report

```
Name                Stmts   Miss  Cover
---------------------------------------
app/__init__.py         0      0   100%
app/dataset.py         45      2    96%
app/enrich.py         120      5    96%
app/main.py            18      0   100%
app/models.py          35      0   100%
---------------------------------------
TOTAL                 218      7    97%
```

---

## Quality Gates

### Required for Merge

- ✅ All pytest tests pass
- ✅ All Postman tests pass (if running manually)
- ✅ Code coverage > 80%
- ✅ No linting errors
- ✅ Service starts successfully

### Recommended

- 📊 Performance benchmarks (response time < 500ms)
- 📝 Test coverage report reviewed
- 🔍 No security vulnerabilities (e.g., Bandit scan)
- 📋 API documentation updated

---

## Extending Test Coverage

### Adding New pytest Tests

**Location:** `tests/test_enrich.py`

**Example:**
```python
def test_enrich_invalid_email():
    payload = {
        "request_id": "req_1",
        "transaction_id": "tx_1",
        "transaction_time": "2026-01-14T05:22:31Z",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "invalid-email"
        }
    }
    r = client.post("/v1/enrich", json=payload)
    assert r.status_code == 422
```

### Adding New Postman Tests

1. Duplicate existing request
2. Modify request body/parameters
3. Update test name
4. Add/modify test assertions in **Tests** tab
5. Export updated collection

---

## Best Practices

### Test Organization

✅ **DO:**
- Keep tests independent (no shared state)
- Use descriptive test names
- Test one thing per test case
- Mock external dependencies
- Use fixtures for common setup

❌ **DON'T:**
- Share mutable state between tests
- Test multiple scenarios in one test
- Rely on test execution order
- Use sleep() for timing (use proper waits)

### Test Data Management

✅ **DO:**
- Use realistic test data
- Keep dataset small (1-10 records)
- Document test data purpose
- Use deterministic generation for mocks

❌ **DON'T:**
- Use production data
- Hardcode sensitive information
- Create large datasets (slows tests)
- Use random data (non-reproducible)

---

## Troubleshooting

### Common Issues

**Problem:** Tests pass locally but fail in CI

**Solutions:**
- Check environment variables
- Verify dataset file is committed
- Ensure service startup time is adequate
- Check port availability

---

**Problem:** Postman tests intermittently fail

**Solutions:**
- Increase delay between requests
- Check for race conditions
- Verify service is fully started
- Use proper wait conditions

---

**Problem:** Coverage dropped after changes

**Solutions:**
- Add tests for new code
- Check for untested branches
- Review coverage report details
- Refactor complex functions

---

## Resources

- **Pytest Docs:** https://docs.pytest.org/
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/
- **Postman Learning:** https://learning.postman.com/
- **Newman CLI:** https://learning.postman.com/docs/running-collections/using-newman-cli/

---

**Maintained by:** Development Team
**Last Updated:** 2026-01-14
**Next Review:** As needed with major changes
