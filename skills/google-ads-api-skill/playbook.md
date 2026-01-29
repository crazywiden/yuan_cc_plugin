# Google Ads API Python Playbook (v22)

## 0) Baseline assumptions
- You are using `google-ads` Python client library.
- Default API version: v22.
- Configuration is via `google-ads.yaml` in $HOME, or GOOGLE_ADS_CONFIGURATION_FILE_PATH.

## 1) First successful call (smoke test)
1. Confirm Python runtime supported (3.12+).
2. Install: `python -m pip install google-ads`
3. Configure credentials (developer_token + OAuth refresh token OR other supported auth mode).
4. Run `scripts/diagnose_google_ads_setup.py` to:
   - load config
   - list accessible customers
   - run a minimal GAQL query

## 2) GAQL workflow
- Start with a small query (LIMIT 10).
- Use `GoogleAdsFieldService` to confirm field names + compatibility when you see INVALID_ARGUMENT.
- Prefer `SearchStream` for large datasets.

## 3) Mutate workflow
- Prefer `validate_only=True` first for dangerous changes.
- For updates, always create a correct `update_mask` (field masks guide).
- Consider `partial_failure=True` for bulk ops; parse partial failure errors.

## 4) MCC / manager-account workflow
- If calling under an MCC:
  - set `login_customer_id` to the manager account ID
  - set `customer_id` to the client account being queried/mutated
- If you see authorization errors, confirm correct login_customer_id and account access.

## 5) Debugging workflow
Always capture:
- request_id
- full GoogleAdsException details
- the exact request payload shape (service + method + operations)
- customer_id/login_customer_id/linked_customer_id used
- retry behavior / rate errors if relevant

Use `scripts/pretty_print_googleads_exception.py` to improve readability.

## 6) Version upgrade workflow
1. Check release notes for the newest version and breaking changes.
2. Pin `version="vXX"` in your client initialization during transition.
3. Update GAQL fields and mutate messages as needed.
4. Run smoke tests again (list customers + simple campaign query + one no-op validate_only mutate).
