#!/usr/bin/env python3
"""
Validate TikTok Ads API request payloads before sending.

This script helps validate common request structures:
- Campaign creation payloads
- Ad group creation payloads
- Report request parameters

Usage:
  python scripts/validate_request.py --type campaign --file payload.json
  python scripts/validate_request.py --type adgroup --file payload.json
  python scripts/validate_request.py --type report --file payload.json
  echo '{"advertiser_id": "123", "campaign_name": "Test"}' | python scripts/validate_request.py --type campaign
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


# Required fields for each request type
REQUIRED_FIELDS = {
    "campaign": {
        "required": ["advertiser_id", "campaign_name", "objective_type"],
        "optional": ["budget", "budget_mode", "app_promotion_type", "special_industries"],
    },
    "adgroup": {
        "required": ["advertiser_id", "campaign_id", "adgroup_name"],
        "optional": [
            "placement_type", "budget", "budget_mode", "schedule_type",
            "schedule_start_time", "schedule_end_time", "billing_event",
            "bid_type", "bid_price", "location_ids", "gender", "age_groups",
            "languages", "interest_category_ids", "operating_systems"
        ],
    },
    "ad": {
        "required": ["advertiser_id", "adgroup_id", "ad_name"],
        "optional": [
            "ad_format", "video_id", "image_ids", "ad_text",
            "landing_page_url", "call_to_action", "app_id"
        ],
    },
    "report": {
        "required": ["advertiser_id", "report_type", "data_level"],
        "optional": [
            "dimensions", "metrics", "start_date", "end_date",
            "filtering", "page", "page_size", "order_field", "order_type"
        ],
    },
}

# Valid enum values
VALID_ENUMS = {
    "objective_type": [
        "REACH", "TRAFFIC", "VIDEO_VIEWS", "LEAD_GENERATION",
        "ENGAGEMENT", "APP_PROMOTION", "CONVERSIONS", "CATALOG_SALES"
    ],
    "budget_mode": ["BUDGET_MODE_DAY", "BUDGET_MODE_TOTAL", "BUDGET_MODE_INFINITE"],
    "app_promotion_type": ["APP_INSTALL", "APP_RETARGETING"],
    "placement_type": ["PLACEMENT_TYPE_AUTOMATIC", "PLACEMENT_TYPE_NORMAL"],
    "schedule_type": ["SCHEDULE_START_END", "SCHEDULE_FROM_NOW"],
    "billing_event": ["CPC", "CPM", "CPV", "OCPM"],
    "bid_type": ["BID_TYPE_NO_BID", "BID_TYPE_CUSTOM"],
    "gender": ["GENDER_MALE", "GENDER_FEMALE", "GENDER_UNLIMITED"],
    "ad_format": ["SINGLE_VIDEO", "SINGLE_IMAGE", "CAROUSEL"],
    "report_type": ["BASIC", "AUDIENCE", "PLAYABLE_MATERIAL", "CATALOG", "BC"],
    "data_level": [
        "AUCTION_ADVERTISER", "AUCTION_CAMPAIGN", "AUCTION_ADGROUP", "AUCTION_AD"
    ],
}


def validate_required_fields(payload: dict, request_type: str) -> list[str]:
    """Check for missing required fields."""
    errors = []
    config = REQUIRED_FIELDS.get(request_type, {})
    required = config.get("required", [])

    for field in required:
        if field not in payload:
            errors.append(f"Missing required field: {field}")

    return errors


def validate_enum_values(payload: dict) -> list[str]:
    """Validate enum field values."""
    errors = []

    for field, valid_values in VALID_ENUMS.items():
        if field in payload:
            value = payload[field]
            if value not in valid_values:
                errors.append(
                    f"Invalid value for {field}: '{value}'. "
                    f"Valid values: {', '.join(valid_values)}"
                )

    return errors


def validate_types(payload: dict) -> list[str]:
    """Validate field types."""
    errors = []

    # String fields
    string_fields = ["advertiser_id", "campaign_id", "adgroup_id", "ad_id",
                     "campaign_name", "adgroup_name", "ad_name", "ad_text",
                     "landing_page_url", "start_date", "end_date"]
    for field in string_fields:
        if field in payload and not isinstance(payload[field], str):
            errors.append(f"{field} should be a string, got {type(payload[field]).__name__}")

    # Numeric fields
    numeric_fields = ["budget", "bid_price", "page", "page_size"]
    for field in numeric_fields:
        if field in payload:
            if not isinstance(payload[field], (int, float)):
                errors.append(f"{field} should be a number, got {type(payload[field]).__name__}")

    # List fields
    list_fields = ["dimensions", "metrics", "location_ids", "age_groups",
                   "languages", "interest_category_ids", "campaign_ids",
                   "adgroup_ids", "ad_ids"]
    for field in list_fields:
        if field in payload and not isinstance(payload[field], list):
            errors.append(f"{field} should be a list, got {type(payload[field]).__name__}")

    return errors


def validate_date_format(payload: dict) -> list[str]:
    """Validate date field formats."""
    import re
    errors = []
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    datetime_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"

    date_fields = ["start_date", "end_date"]
    for field in date_fields:
        if field in payload:
            if not re.match(date_pattern, str(payload[field])):
                errors.append(f"{field} should be in YYYY-MM-DD format")

    datetime_fields = ["schedule_start_time", "schedule_end_time"]
    for field in datetime_fields:
        if field in payload:
            if not re.match(datetime_pattern, str(payload[field])):
                errors.append(f"{field} should be in 'YYYY-MM-DD HH:MM:SS' format")

    return errors


def validate_payload(payload: dict, request_type: str) -> dict:
    """
    Validate a TikTok Ads API request payload.

    Args:
        payload: The request payload dictionary
        request_type: Type of request (campaign, adgroup, ad, report)

    Returns:
        Dictionary with validation results
    """
    all_errors = []
    warnings = []

    # Required fields
    all_errors.extend(validate_required_fields(payload, request_type))

    # Enum values
    all_errors.extend(validate_enum_values(payload))

    # Type checking
    all_errors.extend(validate_types(payload))

    # Date formats
    all_errors.extend(validate_date_format(payload))

    # Request-specific validations
    if request_type == "campaign":
        if payload.get("objective_type") == "APP_PROMOTION":
            if "app_promotion_type" not in payload:
                warnings.append("APP_PROMOTION objective usually requires app_promotion_type")

        if "budget" not in payload:
            warnings.append("No budget specified - will use account default")

    if request_type == "report":
        if "dimensions" not in payload:
            warnings.append("No dimensions specified - report may be aggregated")
        if "metrics" not in payload:
            all_errors.append("At least one metric should be specified for reports")

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": warnings,
        "fields_found": list(payload.keys()),
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate TikTok Ads API request payloads")
    p.add_argument("--type", required=True,
                   choices=["campaign", "adgroup", "ad", "report"],
                   help="Type of request to validate")
    p.add_argument("--file", default=None,
                   help="Path to JSON file containing payload")
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    # Load payload from file or stdin
    if args.file:
        with open(args.file, "r") as f:
            payload = json.load(f)
    else:
        payload = json.load(sys.stdin)

    # Validate
    result = validate_payload(payload, args.type)

    # Output results
    print("\n" + "=" * 50)
    print(f"Validation Results: {args.type.upper()} request")
    print("=" * 50)

    if result["valid"]:
        print("\n[PASS] Payload structure is valid\n")
    else:
        print("\n[FAIL] Validation errors found\n")

    if result["errors"]:
        print("ERRORS:")
        for err in result["errors"]:
            print(f"  - {err}")
        print()

    if result["warnings"]:
        print("WARNINGS:")
        for warn in result["warnings"]:
            print(f"  - {warn}")
        print()

    print(f"Fields present: {', '.join(result['fields_found'])}")
    print("=" * 50 + "\n")

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
