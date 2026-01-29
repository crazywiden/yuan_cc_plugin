# Troubleshooting guide (Python + TikTok Ads API)

## 1) Authentication / Token failures

### Symptoms:
- HTTP 401 Unauthorized
- Error code `40001` (Invalid access token)
- Error code `40002` (Access token expired)
- "authentication failed" message

### Checklist:
- Is `access_token` present in the `Access-Token` header?
- Has the token expired? (Tokens typically expire after a set period)
- Was the OAuth2 flow completed correctly?
- Are `app_id` and `app_secret` correct?
- Is the `auth_code` still valid? (One-time use only)

### Action:
- Run `scripts/diagnose_tiktok_ads_setup.py --debug-logging`.
- Re-authenticate using the OAuth2 flow to get a fresh access_token.
- Check token expiration and implement refresh logic if needed.

---

## 2) Permission / Authorization errors

### Symptoms:
- Error code `40003` (No permission)
- Error code `40004` (Permission denied for advertiser)
- "User does not have access to this advertiser"

### Checklist:
- Does the authenticated user have access to the specified advertiser_id?
- Is the app authorized for the required scopes (Ads Management, Reporting)?
- Is the advertiser account in the correct Business Center?

### Action:
- List authorized advertisers using `/oauth2/advertiser/get/`.
- Verify app scopes in the TikTok Developer Portal.
- Re-authorize the app if scopes were recently changed.

---

## 3) Invalid request / Field validation errors

### Symptoms:
- HTTP 400 Bad Request
- Error code `40100` (Invalid parameter)
- Error code `40101` (Missing required parameter)
- Error code `40102` (Invalid parameter value)

### Common causes:
- Missing required fields (advertiser_id, campaign_id, etc.)
- Invalid enum values (objective_type, budget_mode)
- Invalid date formats (should be "YYYY-MM-DD")
- Budget below minimum threshold
- Invalid JSON in request body

### Action:
- Check the exact field names in official docs.
- Verify enum values are uppercase and match API spec.
- Ensure dates are in correct format.
- Use `scripts/validate_request.py` to check payload structure.

---

## 4) Campaign creation failures

### Symptoms:
- Error code `40200` (Campaign creation failed)
- "Budget is less than minimum"
- "Invalid objective_type"

### Common causes:
- Budget below platform minimum (varies by region/objective)
- Incompatible objective_type with account type
- Missing required fields for specific objective types
- Account not eligible for certain objectives

### Action:
- Check minimum budget requirements for your region.
- Verify objective_type is supported for your account.
- For `APP_PROMOTION`, ensure `app_promotion_type` is set.

---

## 5) Ad group creation failures

### Symptoms:
- Error code `40300` (Ad group creation failed)
- "Invalid placement"
- "Invalid targeting"

### Common causes:
- Campaign does not exist or is not in valid state
- Invalid placement_type for the objective
- Targeting criteria too narrow or invalid
- Schedule dates in the past

### Action:
- Verify campaign_id exists and is enabled.
- Check placement compatibility with objective.
- Review targeting options in official docs.
- Ensure schedule_start_time is in the future.

---

## 6) Reporting errors

### Symptoms:
- Error code `40400` (Report request failed)
- "Invalid dimensions"
- "Invalid metrics"
- Empty report results

### Common causes:
- Incompatible metrics/dimensions combination
- Date range exceeds maximum (typically 365 days)
- data_level doesn't match requested dimensions
- No data available for the specified period

### Action:
- Check metrics/dimensions compatibility matrix in docs.
- Reduce date range to valid bounds.
- Verify data_level matches dimensions (e.g., AUCTION_AD for ad-level).
- Confirm campaigns ran during the specified period.

---

## 7) Rate limits / RESOURCE_EXHAUSTED

### Symptoms:
- HTTP 429 Too Many Requests
- Error code `40100` with "rate limit exceeded"
- X-RateLimit-Remaining header shows 0

### Rate limit tiers:
| Endpoint Type | Typical Limit |
|---------------|---------------|
| Read (GET) | 600 req/min |
| Write (POST) | 300 req/min |
| Reporting | 60 req/min |

### Action:
- Implement exponential backoff with jitter.
- Check `Retry-After` header for wait time.
- Batch operations where possible.
- Use async reporting for large data pulls.
- Cache responses when appropriate.

### Retry pattern:
```python
import time
import random

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        response = func()
        if response.get("code") != 40100:  # Not rate limited
            return response
        delay = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(delay)
    raise Exception("Max retries exceeded")
```

---

## 8) Async report task failures

### Symptoms:
- Task status "FAILED"
- Task never completes
- Download returns empty data

### Common causes:
- Report task timed out (too much data)
- Invalid parameters in task creation
- Backend processing error

### Action:
- Reduce date range or narrow dimensions.
- Check task error message in status response.
- Retry task creation with simpler parameters.
- Contact TikTok support with task_id if persistent.

---

## 9) Creative upload failures

### Symptoms:
- Error code `50001` (Upload failed)
- "File size exceeds limit"
- "Invalid file format"

### File requirements:
| Type | Max Size | Formats |
|------|----------|---------|
| Image | 20MB | JPG, PNG |
| Video | 500MB | MP4, MOV, MPEG, AVI |

### Action:
- Verify file size and format.
- Check image dimensions meet requirements.
- For videos, verify codec compatibility.
- Use chunked upload for large files.

---

## 10) Sandbox vs Production issues

### Symptoms:
- Works in sandbox but fails in production
- "Account not found" in production

### Checklist:
- Are you using the correct base URL?
  - Sandbox: `https://sandbox-ads.tiktok.com/open_api/`
  - Production: `https://business-api.tiktok.com/open_api/`
- Is the advertiser_id valid for the environment?
- Is the access_token from the correct environment?

### Action:
- Verify base URL matches environment.
- Use sandbox for testing, production for live data.
- Re-authenticate if switching environments.

---

## 11) Common error codes reference

| Code | HTTP Status | Description | Action |
|------|-------------|-------------|--------|
| 0 | 200 | Success | N/A |
| 40001 | 401 | Invalid access token | Re-authenticate |
| 40002 | 401 | Token expired | Refresh token |
| 40003 | 403 | No permission | Check scopes |
| 40004 | 403 | Advertiser access denied | Verify advertiser access |
| 40100 | 400/429 | Invalid parameter / Rate limited | Fix param or retry |
| 40101 | 400 | Missing required parameter | Add required fields |
| 40102 | 400 | Invalid parameter value | Fix enum/format |
| 40200 | 400 | Campaign operation failed | Check campaign requirements |
| 40300 | 400 | Ad group operation failed | Check ad group requirements |
| 40400 | 400 | Reporting error | Fix report parameters |
| 50001 | 500 | Internal server error | Retry or contact support |

---

## 12) Debugging checklist

When reporting issues, always collect:
1. Full HTTP request (method, URL, headers minus token, body)
2. Full HTTP response (status, headers, body)
3. `request_id` from response headers
4. Timestamp of the request
5. advertiser_id used
6. API version (v1.2, v1.3, etc.)

Use `scripts/diagnose_tiktok_ads_setup.py` for initial setup validation.
Use `scripts/pretty_print_tiktok_exception.py` to format error responses.
