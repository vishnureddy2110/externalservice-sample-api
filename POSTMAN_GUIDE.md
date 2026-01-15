# Postman Testing Guide

This guide provides detailed instructions for testing the Transaction Enrichment API using Postman.

## Quick Start

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** (top left)
3. Select **Upload Files**
4. Import these files:
   - `postman_collection.json`
   - `postman_environment.json`
5. Select the **Transaction Enrichment API - Local** environment from the environment dropdown (top right)

### 2. Start the API Service

```bash
conda activate fastapi-env
uvicorn app.main:app --reload --port 8080
```

### 3. Run Tests

**Option A: Run Individual Tests**
- Click on any request in the collection
- Click **Send**
- View response and test results in the **Test Results** tab

**Option B: Run All Tests**
- Click on the collection name
- Click **Run** button
- Click **Run Transaction Enrichment API**
- View test results summary

---

## Test Cases Overview

### 1. Health Check

**Purpose:** Verify the API service is running and healthy

**Request:**
```
GET /health
```

**Expected Response (200 OK):**
```json
{
  "status": "ok",
  "dataset_path": "data/sample_transactions.json",
  "dataset_count": 1,
  "utc_now": "2026-01-14T12:00:00+00:00"
}
```

**Automated Tests:**
- Status code is 200
- Response has required fields
- Status is "ok"
- Dataset count is a valid number

---

### 2. Enrich Transaction - Dataset Hit

**Purpose:** Test successful enrichment using a transaction ID that exists in the dataset

**Request:**
```
POST /v1/enrich
```

**Key Field:** `transaction_id: "tx_1001"` (exists in dataset)

**Expected Behavior:**
- `dataset_hit: true`
- Returns actual data from `data/sample_transactions.json`
- External services data from dataset

**Automated Tests:**
- Status code is 200
- Dataset hit is true
- All required payload fields present
- External services (emailage, threatmetrix, ekata) exist
- Risk score is calculated and valid

---

### 3. Enrich Transaction - Mock Data (No Dataset Hit)

**Purpose:** Test deterministic mock data generation when transaction doesn't exist in dataset

**Request:**
```
POST /v1/enrich
```

**Key Field:** `transaction_id: "tx_9999"` (does NOT exist in dataset)

**Expected Behavior:**
- `dataset_hit: false`
- Generates deterministic mock data using SHA-256 hashing
- Mock data is consistent across requests with same inputs

**Automated Tests:**
- Status code is 200
- Dataset hit is false
- Mock external services are generated
- Scores are valid numbers

**Try This:** Send the same request multiple times - you should get identical mock data every time (deterministic)

---

### 4. Enrich Transaction - Email Fallback Lookup

**Purpose:** Test secondary lookup mechanism using email when transaction_id doesn't match

**Request:**
```
POST /v1/enrich
```

**Key Fields:**
- `transaction_id: "tx_9998"` (doesn't exist)
- `email: "vik@example.com"` (exists in dataset)

**Expected Behavior:**
- `dataset_hit: true` (found via email lookup)
- Returns most recent transaction for that email
- Customer email matches the request

**Automated Tests:**
- Status code is 200
- Dataset hit is true via email
- Email matches request

---

### 5. Enrich Transaction - Minimal Required Fields

**Purpose:** Test API with only required fields (no optional data)

**Request:**
```
POST /v1/enrich
```

**Fields Included:**
- `request_id`
- `transaction_id`
- `transaction_time`
- `data.first_name`
- `data.last_name`
- `data.email`

**Expected Behavior:**
- Request succeeds with minimal data
- Mock data fills in missing external service info
- Optional fields are null/empty

**Automated Tests:**
- Status code is 200
- Response structure is valid

---

### 6. Enrich Transaction - With Full Address & Device

**Purpose:** Test API with all optional fields populated

**Request:**
```
POST /v1/enrich
```

**Fields Included:**
- Full billing and shipping addresses
- Complete device information
- Payment card details
- Customer ID, merchant ID, channel

**Expected Behavior:**
- All provided data is reflected in response
- Billing address properly mapped
- Device info included in customer payload

**Automated Tests:**
- Status code is 200
- Billing address present and has line1
- Device info present and has user_agent

---

### 7. Enrich Transaction - Invalid Email (Validation Error)

**Purpose:** Test Pydantic email validation

**Request:**
```
POST /v1/enrich
```

**Key Field:** `email: "not-an-email"` (invalid format)

**Expected Behavior:**
- Request fails validation
- Returns 422 Unprocessable Entity
- Error details explain validation issue

**Automated Tests:**
- Status code is 422
- Response has detail field with error info

**Expected Error Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "data", "email"],
      "msg": "value is not a valid email address",
      "input": "not-an-email"
    }
  ]
}
```

---

### 8. Enrich Transaction - Missing Required Fields

**Purpose:** Test validation when required fields are missing

**Request:**
```
POST /v1/enrich
```

**Missing:** `transaction_time` and `data` fields

**Expected Behavior:**
- Request fails validation
- Returns 422 Unprocessable Entity
- Lists all missing required fields

**Automated Tests:**
- Status code is 422
- Validation error details present

---

### 9. Enrich Transaction - High Risk Score

**Purpose:** Test risk scoring logic with potentially suspicious transaction data

**Request:**
```
POST /v1/enrich
```

**Key Fields:**
- Suspicious email domain
- High transaction amount
- Unknown card BIN

**Expected Behavior:**
- Risk assessment is calculated
- `blended_score` reflects risk level
- `recommended_action` is either ALLOW or REVIEW
- May include `reason_codes` if risk factors detected

**Automated Tests:**
- Status code is 200
- Risk fields present (blended_score, recommended_action, reason_codes)
- Recommended action is valid (ALLOW or REVIEW)

**Risk Calculation:**
```
blended_score = (0.55 × threatmetrix_score) + (0.45 × emailage_score)

If blended_score >= 60: recommended_action = "REVIEW"
If blended_score < 60: recommended_action = "ALLOW"
```

---

## Understanding Test Results

### Test Results Tab

After sending a request, click the **Test Results** tab to see:

- ✅ **PASS** - Test passed successfully
- ❌ **FAIL** - Test failed (see assertion details)
- Test execution time
- Response time

### Console Output

View detailed logs:
1. Open Postman Console (bottom left icon)
2. See all requests, responses, and test logs
3. Useful for debugging failures

---

## Running Collection Tests

### Using Collection Runner

1. Click on collection name: **Transaction Enrichment API**
2. Click **Run** button
3. Configure run:
   - Select/deselect specific tests
   - Set delay between requests (optional)
   - Set iterations (run multiple times)
4. Click **Run Transaction Enrichment API**
5. View results summary:
   - Total tests passed/failed
   - Response times
   - Individual test assertions

### Expected Results

When all tests pass, you should see:
- **9 requests** executed
- **30+ tests** passed
- All assertions green checkmarks

---

## Customizing Tests

### Modifying Environment Variables

1. Click environment dropdown (top right)
2. Select **Transaction Enrichment API - Local**
3. Click edit icon
4. Modify `base_url` if running on different port

Example for different port:
```
base_url = http://localhost:3000
```

### Adding New Tests

Edit a request's **Tests** tab to add custom assertions:

```javascript
// Example: Check specific risk score
pm.test("Risk score is below 50", function () {
    var jsonData = pm.response.json();
    var score = jsonData.transaction_payload.risk.blended_score;
    pm.expect(score).to.be.below(50);
});

// Example: Validate email domain
pm.test("Email is from example.com", function () {
    var jsonData = pm.response.json();
    var email = jsonData.data.email;
    pm.expect(email).to.include("@example.com");
});
```

---

## Troubleshooting

### Issue: All requests fail with "Could not get any response"

**Solution:**
1. Verify the API service is running: `curl http://localhost:8080/health`
2. Check the port matches environment variable
3. Ensure no firewall blocking localhost:8080

### Issue: Tests fail with "Cannot read property of undefined"

**Solution:**
1. Check response body structure
2. Verify API is returning expected format
3. Review test assertions in Tests tab

### Issue: Dataset hit is always false

**Solution:**
1. Check dataset file exists: `data/sample_transactions.json`
2. Verify service loaded dataset (check `/health` endpoint `dataset_count`)
3. Ensure `transaction_id` or `email` matches dataset entry

### Issue: 422 Validation errors on valid data

**Solution:**
1. Check email format is valid
2. Ensure all required fields present
3. Verify date format is ISO 8601 with timezone
4. Check card BIN is 6-8 characters, last4 is 4 characters

---

## Advanced Usage

### Chaining Requests

Use test scripts to save data for subsequent requests:

```javascript
// In Test tab of first request
pm.test("Save transaction ID", function () {
    var jsonData = pm.response.json();
    pm.environment.set("saved_transaction_id", jsonData.transaction_id);
});

// In subsequent request, use:
// {{saved_transaction_id}}
```

### Data-Driven Testing

1. Create CSV file with test data
2. Use Collection Runner
3. Select **Data** file
4. Use `{{column_name}}` in requests
5. Tests run for each row in CSV

### Newman (CLI Runner)

Run tests from command line:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run postman_collection.json -e postman_environment.json

# Generate HTML report
newman run postman_collection.json -e postman_environment.json -r html
```

---

## Best Practices

1. **Always select the correct environment** before running tests
2. **Check test results** after each request - don't just look at response
3. **Use Collection Runner** for regression testing before deployments
4. **Keep collection updated** when API changes
5. **Add descriptive test names** for clarity
6. **Use environment variables** for flexibility across environments

---

## Next Steps

- Add more test cases for edge cases
- Create additional environments (dev, staging, prod)
- Integrate with CI/CD pipeline using Newman
- Add pre-request scripts for dynamic data generation
- Create monitors for continuous testing

---

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review API documentation at http://localhost:8080/docs
- Check service logs for errors
