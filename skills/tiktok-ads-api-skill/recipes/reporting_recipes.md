# TikTok Ads API Reporting Recipes

## 1) Campaign-level performance (last 7 days)

```python
import requests
import json
from datetime import datetime, timedelta

def get_campaign_performance_last_7_days(access_token: str, advertiser_id: str) -> dict:
    """Get campaign-level performance for the last 7 days."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    headers = {"Access-Token": access_token}

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    params = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "data_level": "AUCTION_CAMPAIGN",
        "dimensions": json.dumps(["campaign_id"]),
        "metrics": json.dumps([
            "spend", "impressions", "clicks", "ctr", "cpc",
            "conversions", "conversion_rate", "cost_per_conversion"
        ]),
        "start_date": start_date,
        "end_date": end_date,
        "page_size": 1000
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

## 2) Ad-level performance with daily breakdown

```python
def get_ad_performance_daily(
    access_token: str,
    advertiser_id: str,
    start_date: str,
    end_date: str
) -> dict:
    """Get ad-level performance broken down by day."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    headers = {"Access-Token": access_token}

    params = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "data_level": "AUCTION_AD",
        "dimensions": json.dumps(["ad_id", "stat_time_day"]),
        "metrics": json.dumps([
            "spend", "impressions", "clicks", "ctr",
            "video_views_p25", "video_views_p50", "video_views_p75", "video_views_p100"
        ]),
        "start_date": start_date,
        "end_date": end_date,
        "page_size": 1000
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

## 3) Audience demographics report

```python
def get_audience_demographics(
    access_token: str,
    advertiser_id: str,
    campaign_ids: list,
    start_date: str,
    end_date: str
) -> dict:
    """Get audience demographics breakdown."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    headers = {"Access-Token": access_token}

    params = {
        "advertiser_id": advertiser_id,
        "report_type": "AUDIENCE",
        "data_level": "AUCTION_CAMPAIGN",
        "dimensions": json.dumps(["campaign_id", "gender", "age"]),
        "metrics": json.dumps(["spend", "impressions", "clicks", "conversions"]),
        "start_date": start_date,
        "end_date": end_date,
        "filtering": json.dumps({"campaign_ids": campaign_ids}),
        "page_size": 1000
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

## 4) Country/region breakdown

```python
def get_geo_breakdown(
    access_token: str,
    advertiser_id: str,
    start_date: str,
    end_date: str
) -> dict:
    """Get performance breakdown by country/region."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    headers = {"Access-Token": access_token}

    params = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "data_level": "AUCTION_CAMPAIGN",
        "dimensions": json.dumps(["campaign_id", "country_code"]),
        "metrics": json.dumps(["spend", "impressions", "clicks", "ctr", "conversions"]),
        "start_date": start_date,
        "end_date": end_date,
        "page_size": 1000
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

## 5) Convert report to DataFrame

```python
import pandas as pd

def report_to_dataframe(report_response: dict) -> pd.DataFrame:
    """Convert TikTok report response to pandas DataFrame."""
    if report_response.get("code") != 0:
        raise ValueError(f"Report error: {report_response.get('message')}")

    data = report_response.get("data", {})
    rows = data.get("list", [])

    if not rows:
        return pd.DataFrame()

    # Extract metrics and dimensions from rows
    records = []
    for row in rows:
        record = {}
        # Add dimensions
        if "dimensions" in row:
            record.update(row["dimensions"])
        # Add metrics
        if "metrics" in row:
            record.update(row["metrics"])
        records.append(record)

    df = pd.DataFrame(records)

    # Convert numeric columns
    numeric_cols = ["spend", "impressions", "clicks", "conversions", "ctr", "cpc"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
```

## 6) Full async report workflow

```python
import time

def get_large_report_async(
    access_token: str,
    advertiser_id: str,
    start_date: str,
    end_date: str,
    poll_interval: int = 15,
    max_wait: int = 600  # 10 minutes
) -> dict:
    """Create async report, poll until complete, download results."""
    headers = {"Access-Token": access_token}

    # Step 1: Create task
    create_url = "https://business-api.tiktok.com/open_api/v1.3/report/task/create/"
    create_payload = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "data_level": "AUCTION_AD",
        "dimensions": ["ad_id", "stat_time_day"],
        "metrics": [
            "spend", "impressions", "clicks", "ctr", "cpc",
            "conversions", "conversion_rate", "cost_per_conversion",
            "video_views_p25", "video_views_p50", "video_views_p75", "video_views_p100"
        ],
        "start_date": start_date,
        "end_date": end_date
    }
    create_response = requests.post(create_url, headers=headers, json=create_payload)
    task_id = create_response.json().get("data", {}).get("task_id")

    if not task_id:
        raise ValueError(f"Failed to create task: {create_response.json()}")

    print(f"Created task: {task_id}")

    # Step 2: Poll for completion
    check_url = "https://business-api.tiktok.com/open_api/v1.3/report/task/check/"
    elapsed = 0

    while elapsed < max_wait:
        check_params = {"advertiser_id": advertiser_id, "task_id": task_id}
        check_response = requests.get(check_url, headers=headers, params=check_params)
        status_data = check_response.json().get("data", {})
        status = status_data.get("status")

        print(f"Task status: {status} (elapsed: {elapsed}s)")

        if status == "COMPLETED":
            break
        elif status == "FAILED":
            raise ValueError(f"Task failed: {status_data}")

        time.sleep(poll_interval)
        elapsed += poll_interval

    if elapsed >= max_wait:
        raise TimeoutError("Task did not complete in time")

    # Step 3: Download results
    download_url = "https://business-api.tiktok.com/open_api/v1.3/report/task/download/"
    download_params = {"advertiser_id": advertiser_id, "task_id": task_id}
    download_response = requests.get(download_url, headers=headers, params=download_params)

    return download_response.json()
```

## 7) Paginated report fetch

```python
def get_all_pages(
    access_token: str,
    advertiser_id: str,
    data_level: str,
    dimensions: list,
    metrics: list,
    start_date: str,
    end_date: str
) -> list:
    """Fetch all pages of a report."""
    url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    headers = {"Access-Token": access_token}

    all_rows = []
    page = 1
    page_size = 1000

    while True:
        params = {
            "advertiser_id": advertiser_id,
            "report_type": "BASIC",
            "data_level": data_level,
            "dimensions": json.dumps(dimensions),
            "metrics": json.dumps(metrics),
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "page_size": page_size
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data.get("code") != 0:
            raise ValueError(f"Error: {data.get('message')}")

        rows = data.get("data", {}).get("list", [])
        all_rows.extend(rows)

        page_info = data.get("data", {}).get("page_info", {})
        total_pages = page_info.get("total_page", 1)

        if page >= total_pages:
            break

        page += 1

    return all_rows
```

## Common metrics reference

| Metric | Description |
|--------|-------------|
| `spend` | Total spend in account currency |
| `impressions` | Number of ad impressions |
| `clicks` | Number of clicks |
| `ctr` | Click-through rate (clicks/impressions) |
| `cpc` | Cost per click |
| `cpm` | Cost per 1000 impressions |
| `conversions` | Number of conversions |
| `conversion_rate` | Conversions/clicks |
| `cost_per_conversion` | Spend/conversions |
| `video_views_p25` | Video views at 25% |
| `video_views_p50` | Video views at 50% |
| `video_views_p75` | Video views at 75% |
| `video_views_p100` | Video completions |
| `reach` | Unique users reached |
| `frequency` | Average impressions per user |

## Common dimensions reference

| Dimension | Description |
|-----------|-------------|
| `campaign_id` | Campaign identifier |
| `adgroup_id` | Ad group identifier |
| `ad_id` | Ad identifier |
| `stat_time_day` | Day-level date |
| `stat_time_hour` | Hour-level timestamp |
| `country_code` | Country/region code |
| `gender` | User gender |
| `age` | Age group |
| `platform` | Device platform |
| `ac` | Connection type |
