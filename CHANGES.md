# Recent Changes - Service-Specific Endpoints

## What's New

Added three new service-specific enrichment endpoints that allow you to request data from individual external services instead of all at once.

### New Endpoints

1. **`POST /v1/enrich/emailage`** - Email risk assessment only
2. **`POST /v1/enrich/threatmetrix`** - Device fingerprinting and fraud detection only
3. **`POST /v1/enrich/ekata`** - Identity verification only

### Benefits

- **Smaller responses** - Only get the data you need
- **Faster** - Reduced payload size means faster network transfer
- **Flexible** - Implement progressive enrichment strategies
- **Independent testing** - Test each service separately

## Backward Compatibility

The original `/v1/enrich` endpoint remains **100% backward compatible**. All existing code continues to work without changes.

## Quick Example

**Before (all services):**
```bash
curl -X POST http://localhost:8080/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{"request_id":"req_1","transaction_id":"tx_1001",...}'
```

**After (specific service):**
```bash
# Get only Emailage data
curl -X POST http://localhost:8080/v1/enrich/emailage \
  -H "Content-Type: application/json" \
  -d '{"request_id":"req_1","transaction_id":"tx_1001",...}'
```

## Updated Files

### Code Changes
- ✅ `app/main.py` - Added 3 new endpoint handlers
- ✅ `app/enrich.py` - Added service-specific enrichment functions
- ✅ `tests/test_enrich.py` - Added 4 new test cases (10 total)

### Documentation
- ✅ `SERVICE_SPECIFIC_ENDPOINTS.md` - Complete guide for new endpoints
- ✅ `postman_collection.json` - Added 3 new test cases (12 total)
- ✅ `CHANGES.md` - This file

### Test Results

All tests passing:
```
6 passed in 0.28s
- test_health
- test_enrich_dataset_hit (legacy endpoint)
- test_enrich_emailage_endpoint
- test_enrich_threatmetrix_endpoint
- test_enrich_ekata_endpoint
- test_enrich_emailage_mock_data
```

## Documentation

See [SERVICE_SPECIFIC_ENDPOINTS.md](SERVICE_SPECIFIC_ENDPOINTS.md) for:
- Detailed endpoint documentation
- Request/response examples
- Usage patterns
- Migration guide

## API Docs

Visit http://localhost:8080/docs to see interactive documentation for all endpoints.

---

**Date:** 2026-01-14
**API Version:** 0.1.0
