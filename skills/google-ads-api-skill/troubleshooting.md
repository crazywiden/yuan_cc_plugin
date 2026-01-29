# Troubleshooting guide (Python + Google Ads API)

## 1) Authentication / configuration failures
Symptoms:
- PERMISSION_DENIED
- AUTHENTICATION_ERROR
- "developer_token" issues

Checklist:
- Is `developer_token` present and approved for production?
- Are OAuth credentials (client_id/client_secret/refresh_token) correct?
- Are you pointing to the intended `google-ads.yaml` (HOME vs env var path)?

Action:
- Run `scripts/diagnose_google_ads_setup.py --debug-logging`.

## 2) MCC context errors (login_customer_id)
Symptoms:
- USER_PERMISSION_DENIED
- CUSTOMER_NOT_ENABLED
- Not authorized for customer

Checklist:
- If using an MCC, set login_customer_id to the MCC, and customer_id to the child account.
- Confirm the authenticated user has access to BOTH accounts.

## 3) GAQL INVALID_ARGUMENT
Common causes:
- Field name typos or fields not selectable from a resource
- Incompatible combinations (metrics/segments/resource fields)

Action:
- Use `scripts/gaql_field_probe.py` and official GAQL field compatibility docs.
- Reduce query to minimal SELECT, then add fields incrementally.

## 4) Update does nothing (field masks)
Cause:
- update_mask missing mutated fields.

Action:
- Use protobuf_helpers.field_mask and copy to operation.update_mask.

## 5) Rate limits / RESOURCE_EXHAUSTED
Action:
- Implement exponential backoff + jitter.
- Reduce concurrency.
- Prefer fewer, larger SearchStream calls over many tiny queries.

## 6) Partial failure
If partial_failure enabled:
- You may get successful results plus partial errors.
Action:
- Parse partial failure error details and fix only failed operations.
