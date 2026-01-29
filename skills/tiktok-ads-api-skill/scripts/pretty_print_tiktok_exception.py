#!/usr/bin/env python3
"""
Pretty-print TikTok Ads API error responses.

This is a library-style helper you can import, and also a CLI that can be used
to format error responses for debugging.

Recommended usage in code:
  from scripts.pretty_print_tiktok_exception import format_tiktok_error
  ...
  response = requests.post(url, headers=headers, json=payload)
  data = response.json()
  if data.get("code") != 0:
      print(format_tiktok_error(response, data))
"""

from __future__ import annotations

import json
from typing import Optional

import requests


def format_tiktok_error(
    response: Optional[requests.Response] = None,
    data: Optional[dict] = None
) -> str:
    """
    Format a TikTok API error response for debugging.

    Args:
        response: The requests.Response object (optional)
        data: The parsed JSON response body (optional)

    Returns:
        Formatted error string
    """
    lines: list[str] = []

    lines.append("=" * 50)
    lines.append("TikTok API Error")
    lines.append("=" * 50)

    # HTTP status from response
    if response is not None:
        lines.append(f"HTTP Status: {response.status_code}")

        # Extract request_id from headers if present
        request_id = response.headers.get("x-tt-logid") or response.headers.get("X-Tt-Logid")
        if request_id:
            lines.append(f"Request ID: {request_id}")

    # Parse error details from data
    if data:
        code = data.get("code")
        message = data.get("message", "No message")

        lines.append(f"\nError Code: {code}")
        lines.append(f"Message: {message}")

        # Check for nested error data
        error_data = data.get("data")
        if error_data and isinstance(error_data, dict):
            lines.append("\nError Details:")
            for key, value in error_data.items():
                lines.append(f"  {key}: {value}")

    lines.append("=" * 50)

    return "\n".join(lines)


def format_error_response(response_dict: dict) -> str:
    """
    Format a TikTok API error from a dictionary.

    Args:
        response_dict: The parsed JSON response

    Returns:
        Formatted error string
    """
    return format_tiktok_error(data=response_dict)


# Error code reference
ERROR_CODES = {
    0: ("Success", "Request completed successfully"),
    40001: ("Invalid Access Token", "The access token is invalid or malformed"),
    40002: ("Token Expired", "The access token has expired, refresh required"),
    40003: ("No Permission", "The app lacks required permissions/scopes"),
    40004: ("Advertiser Access Denied", "User cannot access this advertiser account"),
    40100: ("Invalid Parameter", "A request parameter is invalid or rate limit exceeded"),
    40101: ("Missing Required Parameter", "A required parameter is missing"),
    40102: ("Invalid Parameter Value", "A parameter value is invalid for its type"),
    40200: ("Campaign Operation Failed", "Campaign create/update/delete failed"),
    40300: ("Ad Group Operation Failed", "Ad group operation failed"),
    40400: ("Reporting Error", "Report request failed"),
    50001: ("Internal Server Error", "TikTok server error, retry later"),
}


def explain_error_code(code: int) -> tuple[str, str]:
    """
    Get explanation for an error code.

    Args:
        code: TikTok API error code

    Returns:
        Tuple of (error_name, description)
    """
    return ERROR_CODES.get(code, ("Unknown Error", "Error code not documented"))


def print_error_reference() -> None:
    """Print all known error codes and their meanings."""
    print("\nTikTok Ads API Error Code Reference")
    print("=" * 60)
    print(f"{'Code':<8} {'Name':<30} Description")
    print("-" * 60)
    for code, (name, desc) in sorted(ERROR_CODES.items()):
        print(f"{code:<8} {name:<30} {desc}")
    print("=" * 60)


def main() -> int:
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reference":
        print_error_reference()
        return 0

    print(
        "This module is intended to be imported.\n"
        "\nUsage examples:\n"
        "  from scripts.pretty_print_tiktok_exception import format_tiktok_error, explain_error_code\n"
        "\n"
        "  # Format an error response\n"
        "  response = requests.post(url, headers=headers, json=payload)\n"
        "  data = response.json()\n"
        "  if data.get('code') != 0:\n"
        "      print(format_tiktok_error(response, data))\n"
        "\n"
        "  # Explain an error code\n"
        "  name, desc = explain_error_code(40001)\n"
        "  print(f'{name}: {desc}')\n"
        "\n"
        "Run with --reference to see all error codes.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
