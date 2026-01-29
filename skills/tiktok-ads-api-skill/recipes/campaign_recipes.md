# TikTok Ads API Campaign Management Recipes

## 1) List all campaigns with pagination

```python
import requests

def list_all_campaigns(access_token: str, advertiser_id: str) -> list:
    """List all campaigns for an advertiser, handling pagination."""
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"
    headers = {"Access-Token": access_token}

    all_campaigns = []
    page = 1
    page_size = 100

    while True:
        params = {
            "advertiser_id": advertiser_id,
            "page": page,
            "page_size": page_size
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data.get("code") != 0:
            raise ValueError(f"Error: {data.get('message')}")

        campaigns = data.get("data", {}).get("list", [])
        all_campaigns.extend(campaigns)

        page_info = data.get("data", {}).get("page_info", {})
        if page >= page_info.get("total_page", 1):
            break

        page += 1

    return all_campaigns
```

## 2) Create a TRAFFIC campaign

```python
def create_traffic_campaign(
    access_token: str,
    advertiser_id: str,
    campaign_name: str,
    daily_budget: float = 50.0
) -> dict:
    """Create a campaign optimized for website traffic."""
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/create/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_name": campaign_name,
        "objective_type": "TRAFFIC",
        "budget": daily_budget,
        "budget_mode": "BUDGET_MODE_DAY"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 3) Create an APP_PROMOTION campaign

```python
def create_app_install_campaign(
    access_token: str,
    advertiser_id: str,
    campaign_name: str,
    daily_budget: float = 100.0
) -> dict:
    """Create a campaign for app installs."""
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/create/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_name": campaign_name,
        "objective_type": "APP_PROMOTION",
        "app_promotion_type": "APP_INSTALL",
        "budget": daily_budget,
        "budget_mode": "BUDGET_MODE_DAY"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 4) Create a CONVERSIONS campaign

```python
def create_conversion_campaign(
    access_token: str,
    advertiser_id: str,
    campaign_name: str,
    total_budget: float = 500.0
) -> dict:
    """Create a campaign for website conversions with lifetime budget."""
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/create/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_name": campaign_name,
        "objective_type": "CONVERSIONS",
        "budget": total_budget,
        "budget_mode": "BUDGET_MODE_TOTAL"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 5) Update campaign budget

```python
def update_campaign_budget(
    access_token: str,
    advertiser_id: str,
    campaign_id: str,
    new_budget: float,
    budget_mode: str = "BUDGET_MODE_DAY"
) -> dict:
    """Update an existing campaign's budget."""
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/update/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_id": campaign_id,
        "budget": new_budget,
        "budget_mode": budget_mode
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 6) Enable/disable campaigns in bulk

```python
def update_campaigns_status(
    access_token: str,
    advertiser_id: str,
    campaign_ids: list,
    enable: bool = True
) -> dict:
    """Enable or disable multiple campaigns."""
    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/update/status/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_ids": campaign_ids,
        "operation_status": "ENABLE" if enable else "DISABLE"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 7) Create ad group with targeting

```python
def create_targeted_adgroup(
    access_token: str,
    advertiser_id: str,
    campaign_id: str,
    adgroup_name: str,
    daily_budget: float = 50.0,
    location_ids: list = None,
    gender: str = None,  # "GENDER_MALE", "GENDER_FEMALE", "GENDER_UNLIMITED"
    age_groups: list = None,  # ["AGE_18_24", "AGE_25_34", etc.]
    languages: list = None
) -> dict:
    """Create an ad group with audience targeting."""
    url = "https://business-api.tiktok.com/open_api/v1.3/adgroup/create/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_id": campaign_id,
        "adgroup_name": adgroup_name,
        "placement_type": "PLACEMENT_TYPE_AUTOMATIC",
        "budget": daily_budget,
        "budget_mode": "BUDGET_MODE_DAY",
        "schedule_type": "SCHEDULE_FROM_NOW",
        "billing_event": "CPC",
        "bid_type": "BID_TYPE_NO_BID"
    }

    # Add targeting if specified
    if location_ids:
        payload["location_ids"] = location_ids
    if gender:
        payload["gender"] = gender
    if age_groups:
        payload["age_groups"] = age_groups
    if languages:
        payload["languages"] = languages

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 8) Create ad with creative

```python
def create_ad_with_video(
    access_token: str,
    advertiser_id: str,
    adgroup_id: str,
    ad_name: str,
    video_id: str,
    ad_text: str,
    landing_page_url: str,
    call_to_action: str = "LEARN_MORE"
) -> dict:
    """Create an ad with video creative."""
    url = "https://business-api.tiktok.com/open_api/v1.3/ad/create/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "adgroup_id": adgroup_id,
        "ad_name": ad_name,
        "ad_format": "SINGLE_VIDEO",
        "video_id": video_id,
        "ad_text": ad_text,
        "landing_page_url": landing_page_url,
        "call_to_action": call_to_action
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 9) Get campaign, ad group, and ad hierarchy

```python
def get_account_structure(access_token: str, advertiser_id: str) -> dict:
    """Get complete account structure: campaigns > ad groups > ads."""
    headers = {"Access-Token": access_token}
    base_url = "https://business-api.tiktok.com/open_api/v1.3"

    structure = {"campaigns": []}

    # Get campaigns
    campaigns_response = requests.get(
        f"{base_url}/campaign/get/",
        headers=headers,
        params={"advertiser_id": advertiser_id, "page_size": 100}
    )
    campaigns = campaigns_response.json().get("data", {}).get("list", [])

    for campaign in campaigns:
        campaign_id = campaign.get("campaign_id")
        campaign_data = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("campaign_name"),
            "status": campaign.get("status"),
            "objective_type": campaign.get("objective_type"),
            "adgroups": []
        }

        # Get ad groups for this campaign
        adgroups_response = requests.get(
            f"{base_url}/adgroup/get/",
            headers=headers,
            params={
                "advertiser_id": advertiser_id,
                "campaign_ids": [campaign_id],
                "page_size": 100
            }
        )
        adgroups = adgroups_response.json().get("data", {}).get("list", [])

        for adgroup in adgroups:
            adgroup_id = adgroup.get("adgroup_id")
            adgroup_data = {
                "adgroup_id": adgroup_id,
                "adgroup_name": adgroup.get("adgroup_name"),
                "status": adgroup.get("status"),
                "ads": []
            }

            # Get ads for this ad group
            ads_response = requests.get(
                f"{base_url}/ad/get/",
                headers=headers,
                params={
                    "advertiser_id": advertiser_id,
                    "adgroup_ids": [adgroup_id],
                    "page_size": 100
                }
            )
            ads = ads_response.json().get("data", {}).get("list", [])

            for ad in ads:
                adgroup_data["ads"].append({
                    "ad_id": ad.get("ad_id"),
                    "ad_name": ad.get("ad_name"),
                    "status": ad.get("status")
                })

            campaign_data["adgroups"].append(adgroup_data)

        structure["campaigns"].append(campaign_data)

    return structure
```

## 10) Delete campaign (with safety check)

```python
def delete_campaign(
    access_token: str,
    advertiser_id: str,
    campaign_id: str,
    confirm: bool = False
) -> dict:
    """Delete a campaign. Requires explicit confirmation."""
    if not confirm:
        raise ValueError("Set confirm=True to delete campaign")

    url = "https://business-api.tiktok.com/open_api/v1.3/campaign/delete/"
    headers = {"Access-Token": access_token}

    payload = {
        "advertiser_id": advertiser_id,
        "campaign_ids": [campaign_id]
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## Objective types quick reference

| Objective | Use Case | Budget Min |
|-----------|----------|------------|
| `REACH` | Brand awareness | Varies |
| `TRAFFIC` | Website visits | $20/day |
| `VIDEO_VIEWS` | Video engagement | $20/day |
| `LEAD_GENERATION` | Lead forms | $20/day |
| `ENGAGEMENT` | Community growth | $20/day |
| `APP_PROMOTION` | App installs | $50/day |
| `CONVERSIONS` | Website sales | $50/day |
| `CATALOG_SALES` | Product catalog | $50/day |

## Budget mode reference

| Mode | Description |
|------|-------------|
| `BUDGET_MODE_DAY` | Daily budget cap |
| `BUDGET_MODE_TOTAL` | Lifetime budget for campaign duration |
| `BUDGET_MODE_INFINITE` | No budget limit (use with caution) |

## Status values reference

| Status | Description |
|--------|-------------|
| `CAMPAIGN_STATUS_ENABLE` | Campaign is active |
| `CAMPAIGN_STATUS_DISABLE` | Campaign is paused |
| `CAMPAIGN_STATUS_DELETE` | Campaign is deleted |
| `CAMPAIGN_STATUS_BUDGET_EXCEED` | Budget exhausted |
