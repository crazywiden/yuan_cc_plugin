#!/usr/bin/env python3
"""
Diagnostics for TikTok Ads API Python setup.

What it does:
- Loads credentials from environment or config file
- Exchanges auth_code for access_token (if needed)
- Lists accessible advertisers
- Runs a minimal campaign list query

Usage examples:
  python scripts/diagnose_tiktok_ads_setup.py --access_token YOUR_TOKEN --advertiser_id 1234567890
  python scripts/diagnose_tiktok_ads_setup.py --app_id APP_ID --app_secret SECRET --auth_code CODE
  python scripts/diagnose_tiktok_ads_setup.py --config /path/to/config.json --debug_logging
  python scripts/diagnose_tiktok_ads_setup.py --sandbox  # Use sandbox environment
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Optional

import requests


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose TikTok Ads API setup")
    p.add_argument("--config", default=None, help="Path to JSON config file with credentials.")
    p.add_argument("--access_token", default=None, help="Access token for API calls.")
    p.add_argument("--advertiser_id", default=None, help="Advertiser ID to test.")
    p.add_argument("--app_id", default=None, help="App ID for OAuth2 flow.")
    p.add_argument("--app_secret", default=None, help="App secret for OAuth2 flow.")
    p.add_argument("--auth_code", default=None, help="Auth code to exchange for access token.")
    p.add_argument("--sandbox", action="store_true", help="Use sandbox environment.")
    p.add_argument("--debug_logging", action="store_true", help="Enable verbose logging.")
    return p.parse_args()


def _configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s - %(levelname)s] %(name)s: %(message)s"
    )


def _get_base_url(sandbox: bool) -> str:
    if sandbox:
        return "https://sandbox-ads.tiktok.com/open_api/v1.3"
    return "https://business-api.tiktok.com/open_api/v1.3"


def _load_config(config_path: Optional[str]) -> dict:
    """Load configuration from JSON file."""
    if not config_path:
        return {}

    if not os.path.exists(config_path):
        logging.warning(f"Config file not found: {config_path}")
        return {}

    with open(config_path, "r") as f:
        return json.load(f)


def _get_access_token(
    base_url: str,
    app_id: str,
    app_secret: str,
    auth_code: str
) -> Optional[str]:
    """Exchange auth_code for access_token."""
    url = f"{base_url}/oauth2/access_token/"
    payload = {
        "app_id": app_id,
        "secret": app_secret,
        "auth_code": auth_code
    }

    logging.info(f"Exchanging auth_code for access_token...")
    response = requests.post(url, json=payload)
    data = response.json()

    if data.get("code") != 0:
        logging.error(f"Failed to get access token: {data}")
        return None

    token = data.get("data", {}).get("access_token")
    logging.info(f"Successfully obtained access token")
    return token


def _list_advertisers(base_url: str, access_token: str) -> list:
    """List accessible advertiser accounts."""
    url = f"{base_url}/oauth2/advertiser/get/"
    headers = {"Access-Token": access_token}

    logging.info("Fetching authorized advertisers...")
    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get("code") != 0:
        logging.error(f"Failed to list advertisers: {data}")
        return []

    advertisers = data.get("data", {}).get("list", [])
    return advertisers


def _test_campaign_list(
    base_url: str,
    access_token: str,
    advertiser_id: str
) -> bool:
    """Run a minimal campaign list query as smoke test."""
    url = f"{base_url}/campaign/get/"
    headers = {"Access-Token": access_token}
    params = {
        "advertiser_id": advertiser_id,
        "page_size": 5
    }

    logging.info(f"Running smoke test: listing campaigns for advertiser {advertiser_id}...")
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data.get("code") != 0:
        logging.error(f"Campaign list failed: {data}")
        return False

    campaigns = data.get("data", {}).get("list", [])
    logging.info(f"Found {len(campaigns)} campaigns")

    for c in campaigns[:5]:
        print(f"  - {c.get('campaign_name')} (ID: {c.get('campaign_id')}, Status: {c.get('status')})")

    return True


def main() -> int:
    args = _parse_args()
    _configure_logging(args.debug_logging)

    # Determine environment
    base_url = _get_base_url(args.sandbox)
    env_name = "SANDBOX" if args.sandbox else "PRODUCTION"
    logging.info(f"Using {env_name} environment: {base_url}")

    # Load config file if specified
    config = _load_config(args.config)

    # Resolve credentials
    access_token = args.access_token or config.get("access_token") or os.environ.get("TIKTOK_ACCESS_TOKEN")
    advertiser_id = args.advertiser_id or config.get("advertiser_id") or os.environ.get("TIKTOK_ADVERTISER_ID")
    app_id = args.app_id or config.get("app_id") or os.environ.get("TIKTOK_APP_ID")
    app_secret = args.app_secret or config.get("app_secret") or os.environ.get("TIKTOK_APP_SECRET")
    auth_code = args.auth_code or config.get("auth_code")

    # If we need to exchange auth_code for access_token
    if not access_token and auth_code and app_id and app_secret:
        access_token = _get_access_token(base_url, app_id, app_secret, auth_code)
        if not access_token:
            print("\nERROR: Failed to obtain access token.\n")
            return 1

    if not access_token:
        print("\nERROR: No access_token provided.")
        print("Provide via --access_token, --config, or TIKTOK_ACCESS_TOKEN env var.\n")
        print("Or provide --app_id, --app_secret, and --auth_code to exchange for token.\n")
        return 2

    # List accessible advertisers
    print("\n--- Accessible Advertisers ---")
    advertisers = _list_advertisers(base_url, access_token)

    if not advertisers:
        print("No advertisers found or access denied.")
    else:
        for adv in advertisers:
            print(f"  Advertiser ID: {adv.get('advertiser_id')}, Name: {adv.get('advertiser_name')}")

        # Auto-select first advertiser if not specified
        if not advertiser_id and advertisers:
            advertiser_id = str(advertisers[0].get("advertiser_id"))
            logging.info(f"Auto-selected advertiser: {advertiser_id}")

    if not advertiser_id:
        print("\nERROR: No advertiser_id provided or available.\n")
        return 2

    # Run smoke test
    print(f"\n--- Smoke Test (advertiser: {advertiser_id}) ---")
    success = _test_campaign_list(base_url, access_token, advertiser_id)

    if success:
        print("\n" + "=" * 40)
        print("DIAGNOSTICS OK")
        print("=" * 40 + "\n")
        return 0
    else:
        print("\n" + "=" * 40)
        print("DIAGNOSTICS FAILED")
        print("=" * 40 + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
