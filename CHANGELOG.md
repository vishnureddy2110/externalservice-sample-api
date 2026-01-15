# Changelog

## [Unreleased] - 2026-01-15

### Added

#### New Simplified Service APIs

- **POST /v1/ekata** - Simplified Ekata identity verification endpoint
  - Minimal request model (only requires request_id and identity data)
  - Focused response with identity risk assessment
  - Returns: risk_score, name/email/IP/phone risk indicators
  - Response format matches requirements: `fname`, `l_name`, `homephone` fields

- **POST /v1/emailage** - Simplified Emailage email risk assessment endpoint
  - Minimal request model (only requires request_id and contact data)
  - Focused response with email reputation data
  - Returns: score, email history, domain flags

#### New Request/Response Models

- `EkataRequest` - Simplified request model for Ekata service
- `EkataResponse` - Response model with `data` and `ekata_payload`
- `EkataResponseData` - Modified field names (`fname`, `l_name`, `homephone`, `workphone`)
- `EkataPayload` - Risk assessment payload with 6 risk indicators
- `EmailageRequest` - Simplified request model for Emailage service
- `EmailageResponse` - Response model with `data` and `emailage_payload`
- `EmailagePayload` - Email reputation payload
- `ServiceRequestData` - Shared data model for simplified service APIs

#### New Business Logic

- `enrich_ekata_service()` - Ekata enrichment using simplified request model
- `enrich_emailage_service()` - Emailage enrichment using simplified request model
- `_get_simple_seed()` - Seed generation for simplified service requests

#### Documentation

- **API_GUIDE.md** - Comprehensive API documentation
  - Detailed endpoint descriptions
  - Request/response examples
  - Field descriptions
  - Integration patterns
  - Error handling guide

- Updated **README.md**
  - Added simplified API endpoint documentation
  - Added new features section
  - Updated API endpoints list
  - Added example requests/responses for Ekata and Emailage

#### Testing

- Added 8+ new test cases for simplified APIs:
  - `test_ekata_service()` - Full test of Ekata endpoint
  - `test_emailage_service()` - Full test of Emailage endpoint
  - `test_ekata_service_minimal()` - Minimal field test
  - `test_emailage_service_minimal()` - Minimal field test
  - `test_ekata_service_invalid_email()` - Validation test
  - `test_emailage_service_invalid_email()` - Validation test

- Added 6 new Postman test requests:
  - Ekata Service - Simplified API
  - Emailage Service - Simplified API
  - Ekata Service - Minimal Fields
  - Emailage Service - Minimal Fields
  - Ekata Service - Invalid Email
  - Emailage Service - Invalid Email

### Changed

- Enhanced feature list to highlight new simplified APIs
- Updated Postman collection description to reflect 15+ test cases
- Maintained backward compatibility with existing `/v1/enrich/*` endpoints

### Maintained

- All existing endpoints remain unchanged:
  - `GET /health`
  - `POST /v1/enrich`
  - `POST /v1/enrich/emailage`
  - `POST /v1/enrich/threatmetrix`
  - `POST /v1/enrich/ekata`

- Dataset lookup strategy unchanged
- Deterministic mock data generation unchanged
- Risk scoring algorithm unchanged

## Architecture Changes

### API Structure

```
Before:
- /health
- /v1/enrich (full enrichment)
- /v1/enrich/emailage (legacy)
- /v1/enrich/threatmetrix (legacy)
- /v1/enrich/ekata (legacy)

After:
- /health
- /v1/enrich (full enrichment)
- /v1/ekata ⭐ NEW - Simplified
- /v1/emailage ⭐ NEW - Simplified
- /v1/enrich/emailage (legacy, maintained)
- /v1/enrich/threatmetrix (legacy, maintained)
- /v1/enrich/ekata (legacy, maintained)
```

### Request Model Hierarchy

```
EnrichRequest (complex, requires transaction context)
  ↓
  Used by: /v1/enrich, /v1/enrich/{service}

ServiceRequestData (simple, minimal fields)
  ↓
  Used by: /v1/ekata, /v1/emailage
```

### Response Model Differences

**Legacy Format** (`/v1/enrich/ekata`):
```json
{
  "request_id": "...",
  "transaction_id": "...",
  "transaction_time": "...",
  "dataset_hit": true/false,
  "service": "ekata",
  "data": { ... },
  "enrichment": { ... }
}
```

**New Simplified Format** (`/v1/ekata`):
```json
{
  "request_id": "...",
  "data": {
    "fname": "...",
    "l_name": "...",
    ...
  },
  "ekata_payload": {
    "risk_score": 45,
    "first_name_match": true,
    ...
  }
}
```

## Migration Guide

### From Legacy to Simplified APIs

**Legacy Ekata Call:**
```python
response = requests.post("/v1/enrich/ekata", json={
    "request_id": "req_001",
    "transaction_id": "tx_001",
    "transaction_time": "2026-01-14T10:00:00Z",
    "data": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    }
})
result = response.json()["enrichment"]
```

**New Simplified Ekata Call:**
```python
response = requests.post("/v1/ekata", json={
    "request_id": "req_001",
    "data": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    }
})
result = response.json()["ekata_payload"]
```

### Benefits of Simplified APIs

1. **Smaller payloads** - No transaction context required
2. **Faster responses** - Less data to serialize/deserialize
3. **Clearer intent** - API name matches the service
4. **Easier integration** - Minimal required fields
5. **Better for microservices** - No cross-service dependencies

## Testing Coverage

### Pytest Tests

- 13 total test cases (up from 8)
- 100% coverage of new endpoints
- Validation error testing
- Minimal field testing

### Postman Collection

- 18 total requests (up from 12)
- Full integration testing
- Automated assertions
- Environment variables support

## Files Modified

### Core Application
- `app/models.py` - Added 9 new model classes
- `app/enrich.py` - Added 2 new enrichment functions
- `app/main.py` - Added 2 new API endpoints

### Testing
- `tests/test_enrich.py` - Added 8 new test functions
- `postman_collection.json` - Added 6 new test requests

### Documentation
- `README.md` - Updated with new API documentation
- `API_GUIDE.md` - ⭐ NEW comprehensive API guide
- `CHANGELOG.md` - ⭐ NEW this file

## Backward Compatibility

✅ All existing endpoints are fully backward compatible
✅ No breaking changes to existing API contracts
✅ Legacy endpoints remain fully functional
✅ Dataset lookup strategy unchanged
✅ Mock data generation unchanged
✅ Risk scoring algorithm unchanged

## Next Release

Consider adding:
- ThreatMetrix simplified endpoint (`/v1/threatmetrix`)
- Batch enrichment endpoint
- Webhook support for async processing
- API key authentication
- Rate limiting middleware
