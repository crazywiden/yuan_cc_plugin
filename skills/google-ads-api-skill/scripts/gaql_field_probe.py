#!/usr/bin/env python3
"""
Probe GAQL fields using GoogleAdsFieldService (metadata lookup).

This is the fastest way to:
- Confirm field names (typos)
- Check selectable/filterable/sortable
- Inspect selectable_with (compatibility hints)

Usage:
  python scripts/gaql_field_probe.py --name_prefix campaign.
  python scripts/gaql_field_probe.py --name_prefix metrics.
  python scripts/gaql_field_probe.py --name_contains "search_term"
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=None, help="Path to google-ads.yaml (optional).")
    p.add_argument("--version", default="v22", help="API version, e.g., v22.")
    p.add_argument("--name_prefix", default=None, help="Prefix match, e.g., 'campaign.'")
    p.add_argument("--name_contains", default=None, help="Contains match (substring), e.g., 'conversion'")
    p.add_argument("--limit", type=int, default=50, help="Max results to print.")
    return p.parse_args()


def _build_query(prefix: Optional[str], contains: Optional[str]) -> str:
    where = []
    if prefix:
        where.append(f"name LIKE '{prefix}%'")
    if contains:
        where.append(f"name LIKE '%{contains}%'")
    where_clause = " AND ".join(where) if where else "name LIKE '%'"
    return f"""
        SELECT
          name,
          category,
          selectable,
          filterable,
          sortable,
          selectable_with,
          data_type,
          is_repeated
        WHERE {where_clause}
    """.strip()


def main() -> int:
    args = _parse_args()
    client = GoogleAdsClient.load_from_storage(path=args.config, version=args.version)

    gaf_service = client.get_service("GoogleAdsFieldService")
    query = _build_query(args.name_prefix, args.name_contains)

    request = client.get_type("SearchGoogleAdsFieldsRequest")
    request.query = query

    try:
        response = gaf_service.search_google_ads_fields(request=request)

        printed = 0
        for field in response:
            print(field.name)
            print(f"  category: {field.category.name}")
            print(f"  data_type: {field.data_type.name}")
            print(f"  selectable: {field.selectable}  filterable: {field.filterable}  sortable: {field.sortable}")
            print(f"  repeated: {field.is_repeated}")
            if field.selectable_with:
                sample = list(field.selectable_with)[:15]
                print(f"  selectable_with (sample): {sample}")
            print()

            printed += 1
            if printed >= args.limit:
                break

        if printed == 0:
            print("No fields matched your criteria.")
            return 0

        return 0

    except GoogleAdsException as ex:
        print(f"GoogleAdsException. Request ID: {ex.request_id}")
        for i, err in enumerate(ex.failure.errors):
            print(f"  [{i}] {err.error_code} - {err.message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
