# TikTok Ads API Python Playbook (v1.3)

## 0) Baseline assumptions
- You are using direct HTTP requests via the `requests` library (no SDK wrappers)
- Default API version: v1.3
- Base URL: `https://business-api.tiktok.com/open_api/v1.3/`
- All requests require `Access-Token` header

## 1) First successful call (smoke test)

1. Confirm Python runtime supported (3.8+).
2. Install dependencies:
   ```bash
   pip install requests
   ```
3. Obtain credentials:
   - `app_id` and `app_secret` from TikTok Developer Portal
   - `auth_code` from OAuth2 authorization flow
4. Run `scripts/diagnose_tiktok_ads_setup.py` to:
   - Exchange auth_code for access_token
   - List authorized advertisers
   - Run a minimal campaign list query

## 2) Authentication workflow

### OAuth2 Authorization Code Flow
```python
import requests

def get_access_token(app_id: str, app_secret: str, auth_code: str) -> dict:
    """Exchange auth_code for access_token."""
    url = "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/"
    payload = {
        "app_id": app_id,
        "secret": app_secret,
        "auth_code": auth_code
    }
    response = requests.post(url, json=payload)
    return response.json()
```

### List authorized advertisers
```python
def list_advertisers(access_token: str, app_id: str, app_secret: str) -> dict:
    """List all advertiser accounts authorized for this app."""
    url = "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/"
    headers = {"Access-Token": access_token}
    params = {
        "app_id": app_id,
        "secret": app_secret
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

## 3) Campaign management workflow

### List campaigns
```python
def list_campaigns(access_token: str, advertiser_id: str) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"
    headers = {"Access-Token": access_token}
    params = {
        "advertiser_id": advertiser_id,
        "page_size": 100
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

### Create campaign
```python
def create_campaign(
    access_token: str,
    advertiser_id: str,
    campaign_name: str,
    objective_type: str,
    budget: float,
    budget_mode: str = "BUDGET_MODE_DAY"
) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/create/"
    headers = {"Access-Token": access_token}
    payload = {
        "advertiser_id": advertiser_id,
        "campaign_name": campaign_name,
        "objective_type": objective_type,
        "budget": budget,
        "budget_mode": budget_mode
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

### Update campaign status
```python
def update_campaign_status(
    access_token: str,
    advertiser_id: str,
    campaign_ids: list,
    operation_status: str  # "ENABLE" or "DISABLE"
) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/update/status/"
    headers = {"Access-Token": access_token}
    payload = {
        "advertiser_id": advertiser_id,
        "campaign_ids": campaign_ids,
        "operation_status": operation_status
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 4) Ad group workflow

### Create ad group
```python
def create_ad_group(
    access_token: str,
    advertiser_id: str,
    campaign_id: str,
    adgroup_name: str,
    placement_type: str = "PLACEMENT_TYPE_AUTOMATIC",
    budget: float = 50.0,
    budget_mode: str = "BUDGET_MODE_DAY",
    schedule_type: str = "SCHEDULE_START_END",
    schedule_start_time: str = None,  # Format: "2024-01-01 00:00:00"
    billing_event: str = "CPC",
    bid_type: str = "BID_TYPE_NO_BID"
) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/adgroup/create/"
    headers = {"Access-Token": access_token}
    payload = {
        "advertiser_id": advertiser_id,
        "campaign_id": campaign_id,
        "adgroup_name": adgroup_name,
        "placement_type": placement_type,
        "budget": budget,
        "budget_mode": budget_mode,
        "schedule_type": schedule_type,
        "billing_event": billing_event,
        "bid_type": bid_type
    }
    if schedule_start_time:
        payload["schedule_start_time"] = schedule_start_time
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 5) Reporting workflow

### Synchronous report (for small datasets)
```python
def get_sync_report(
    access_token: str,
    advertiser_id: str,
    data_level: str = "AUCTION_CAMPAIGN",
    metrics: list = None,
    dimensions: list = None,
    start_date: str = None,
    end_date: str = None
) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    headers = {"Access-Token": access_token}

    if metrics is None:
        metrics = ["spend", "impressions", "clicks", "ctr", "cpc", "conversions"]
    if dimensions is None:
        dimensions = ["campaign_id"]

    params = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "data_level": data_level,
        "dimensions": json.dumps(dimensions),
        "metrics": json.dumps(metrics),
        "start_date": start_date,
        "end_date": end_date,
        "page_size": 1000
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

### Asynchronous report workflow (for large datasets)
```python
import time

def create_async_report_task(
    access_token: str,
    advertiser_id: str,
    data_level: str,
    metrics: list,
    dimensions: list,
    start_date: str,
    end_date: str
) -> str:
    """Create async report task and return task_id."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/task/create/"
    headers = {"Access-Token": access_token}
    payload = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "data_level": data_level,
        "dimensions": dimensions,
        "metrics": metrics,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    return data.get("data", {}).get("task_id")


def check_task_status(access_token: str, advertiser_id: str, task_id: str) -> dict:
    """Check async report task status."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/task/check/"
    headers = {"Access-Token": access_token}
    params = {
        "advertiser_id": advertiser_id,
        "task_id": task_id
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def download_async_report(access_token: str, advertiser_id: str, task_id: str) -> dict:
    """Download completed async report."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/task/download/"
    headers = {"Access-Token": access_token}
    params = {
        "advertiser_id": advertiser_id,
        "task_id": task_id
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def run_async_report(
    access_token: str,
    advertiser_id: str,
    data_level: str,
    metrics: list,
    dimensions: list,
    start_date: str,
    end_date: str,
    poll_interval: int = 10,
    max_polls: int = 60
) -> dict:
    """Create async report, wait for completion, and download results."""
    task_id = create_async_report_task(
        access_token, advertiser_id, data_level,
        metrics, dimensions, start_date, end_date
    )

    for _ in range(max_polls):
        status_response = check_task_status(access_token, advertiser_id, task_id)
        status = status_response.get("data", {}).get("status")

        if status == "COMPLETED":
            return download_async_report(access_token, advertiser_id, task_id)
        elif status == "FAILED":
            raise Exception(f"Report task failed: {status_response}")

        time.sleep(poll_interval)

    raise TimeoutError("Report task did not complete in time")
```

## 6) Creative upload workflow

### Upload image
```python
def upload_image(
    access_token: str,
    advertiser_id: str,
    image_file_path: str
) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/file/image/ad/upload/"
    headers = {"Access-Token": access_token}

    with open(image_file_path, "rb") as f:
        files = {"image_file": f}
        data = {"advertiser_id": advertiser_id}
        response = requests.post(url, headers=headers, files=files, data=data)

    return response.json()
```

### Upload video
```python
def upload_video(
    access_token: str,
    advertiser_id: str,
    video_file_path: str
) -> dict:
    url = "https://business-api.tiktok.com/open_api/v1.3/file/video/ad/upload/"
    headers = {"Access-Token": access_token}

    with open(video_file_path, "rb") as f:
        files = {"video_file": f}
        data = {"advertiser_id": advertiser_id}
        response = requests.post(url, headers=headers, files=files, data=data)

    return response.json()
```

## 7) Debugging workflow

Always capture:
- HTTP status code
- Response body `code` and `message` fields
- `request_id` from response headers (for TikTok support)
- The exact request payload shape
- advertiser_id used
- retry behavior / rate errors if relevant

Use `scripts/pretty_print_tiktok_exception.py` to improve readability.

## 8) Rate limit handling

```python
import time
from functools import wraps

def with_retry(max_retries: int = 5, base_delay: float = 1.0):
    """Decorator for exponential backoff retry on rate limit errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                response = func(*args, **kwargs)

                # Check for rate limit error
                if isinstance(response, dict):
                    code = response.get("code")
                    if code == 40100:  # Rate limit exceeded
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limited. Retrying in {delay}s...")
                        time.sleep(delay)
                        continue

                return response

            raise Exception("Max retries exceeded due to rate limiting")
        return wrapper
    return decorator
```

## 9) Version upgrade workflow

1. Check release notes for the newest API version and breaking changes at TikTok Developer Portal.
2. Update base URL version in your code (e.g., `v1.2` → `v1.3`).
3. Test endpoints: list advertisers, list campaigns, run a basic report.
4. Check for deprecated fields in campaign/ad group/ad payloads.
5. Update any hardcoded enum values that may have changed.
