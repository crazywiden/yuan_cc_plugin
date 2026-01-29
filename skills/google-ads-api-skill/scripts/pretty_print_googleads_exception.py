#!/usr/bin/env python3
"""
Pretty-print GoogleAdsException details.

This is a library-style helper you can import, and also a CLI that can be used
in small repro scripts if you paste exception text to stdout.

Recommended usage in code:
  from scripts.pretty_print_googleads_exception import format_google_ads_exception
  ...
  except GoogleAdsException as ex:
      print(format_google_ads_exception(ex))
      raise
"""

from __future__ import annotations

from typing import Optional

from google.ads.googleads.errors import GoogleAdsException


def _field_path(err) -> Optional[str]:
    if not err.location or not err.location.field_path_elements:
        return None
    return " > ".join(e.field_name for e in err.location.field_path_elements)


def format_google_ads_exception(ex: GoogleAdsException) -> str:
    lines: list[str] = []
    lines.append(f"GoogleAdsException (request_id={ex.request_id})")
    lines.append(f"GoogleAdsFailure errors={len(ex.failure.errors)}")
    for idx, err in enumerate(ex.failure.errors):
        lines.append(f"  [{idx}] error_code={err.error_code}")
        lines.append(f"       message={err.message}")
        fp = _field_path(err)
        if fp:
            lines.append(f"       field_path={fp}")
        if err.trigger:
            lines.append(f"       trigger={err.trigger.string_value or err.trigger.int64_value or err.trigger.double_value or '...'}")
    return "\n".join(lines)


def main() -> int:
    print(
        "This module is intended to be imported.\n"
        "Example:\n"
        "  from scripts.pretty_print_googleads_exception import format_google_ads_exception\n"
        "  ...\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
