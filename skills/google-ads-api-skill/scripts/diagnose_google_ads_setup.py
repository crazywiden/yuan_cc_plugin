#!/usr/bin/env python3
"""
Diagnostics for Google Ads API Python setup.

What it does:
- Loads GoogleAdsClient config (google-ads.yaml)
- Optionally sets login_customer_id (MCC context)
- Calls CustomerService.list_accessible_customers()
- Runs a minimal GAQL query via GoogleAdsService.search_stream()

Usage examples:
  python scripts/diagnose_google_ads_setup.py --customer_id 1234567890
  python scripts/diagnose_google_ads_setup.py --auto_customer
  python scripts/diagnose_google_ads_setup.py --auto_customer --login_customer_id 1234567890
  python scripts/diagnose_google_ads_setup.py --config /path/to/google-ads.yaml --version v22 --debug_logging
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from typing import Optional

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=None, help="Path to google-ads.yaml. If omitted, uses default resolution.")
    p.add_argument("--version", default="v22", help="Google Ads API version, e.g., v22.")
    p.add_argument("--customer_id", default=None, help="Customer ID (no hyphens).")
    p.add_argument("--auto_customer", action="store_true", help="Pick the first accessible customer automatically.")
    p.add_argument("--login_customer_id", default=None, help="MCC login customer ID (no hyphens).")
    p.add_argument("--debug_logging", action="store_true", help="Enable verbose logging.")
    return p.parse_args()


def _extract_customer_id(resource_name: str) -> Optional[str]:
    # Usually "customers/1234567890"
    m = re.match(r"^customers/(\d+)$", resource_name.strip())
    return m.group(1) if m else None


def _configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="[%(asctime)s - %(levelname)s] %(name)s: %(message)s")
    # Helpful noise reduction:
    logging.getLogger("grpc").setLevel(logging.INFO if debug else logging.WARNING)


def main() -> int:
    args = _parse_args()
    _configure_logging(args.debug_logging)

    # Surface config resolution hints.
    if args.config:
        logging.info("Using config path: %s", args.config)
    else:
        env_path = os.environ.get("GOOGLE_ADS_CONFIGURATION_FILE_PATH")
        if env_path:
            logging.info("GOOGLE_ADS_CONFIGURATION_FILE_PATH=%s", env_path)
        else:
            logging.info("No --config provided and GOOGLE_ADS_CONFIGURATION_FILE_PATH not set; using default location resolution.")

    client = GoogleAdsClient.load_from_storage(path=args.config, version=args.version)

    if args.login_customer_id:
        client.login_customer_id = str(args.login_customer_id)
        logging.info("Set login_customer_id=%s", client.login_customer_id)

    try:
        customer_service = client.get_service("CustomerService")
        accessible = customer_service.list_accessible_customers()

        print("\nAccessible customers:")
        for rn in accessible.resource_names:
            print(f"  {rn}")

        customer_id = args.customer_id
        if not customer_id and args.auto_customer:
            for rn in accessible.resource_names:
                cid = _extract_customer_id(rn)
                if cid:
                    customer_id = cid
                    break

        if not customer_id:
            print("\nERROR: Provide --customer_id or use --auto_customer.\n")
            return 2

        ga_service = client.get_service("GoogleAdsService")
        query = """
            SELECT customer.id, customer.descriptive_name
            FROM customer
            LIMIT 1
        """.strip()

        print(f"\nRunning smoke GAQL query against customer_id={customer_id} (version={args.version}) ...\n")

        stream = ga_service.search_stream(customer_id=str(customer_id), query=query)
        found = False
        for batch in stream:
            for row in batch.results:
                found = True
                print("Smoke query result row:")
                print(row)

        if not found:
            print("Smoke query returned no rows (unexpected for customer query, but not always fatal).")

        print("\nDiagnostics OK.")
        return 0

    except GoogleAdsException as ex:
        print(f"\nGoogleAdsException. Request ID: {ex.request_id}")
        for i, err in enumerate(ex.failure.errors):
            print(f"  [{i}] {err.error_code} - {err.message}")
            if err.location and err.location.field_path_elements:
                path = " > ".join(e.field_name for e in err.location.field_path_elements)
                print(f"      field_path: {path}")
        return 1

    except Exception as e:
        print("\nUnhandled exception:", repr(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
