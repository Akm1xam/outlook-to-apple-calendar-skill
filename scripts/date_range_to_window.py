#!/usr/bin/env python3
"""Resolve explicit date inputs into a calendar query window."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert explicit start/end dates into an inclusive-start/exclusive-end "
            "window for Outlook calendar queries."
        )
    )
    parser.add_argument("--start", required=True, help="Start date or datetime, ISO 8601")
    parser.add_argument("--end", help="Inclusive end date/datetime, ISO 8601")
    parser.add_argument(
        "--exclusive-end",
        help="Exclusive end date/datetime, ISO 8601. Use instead of --end when already known.",
    )
    parser.add_argument(
        "--timezone",
        required=True,
        help="IANA timezone used for date-only values, for example Europe/Moscow.",
    )
    parser.add_argument(
        "--single-day",
        action="store_true",
        help="Treat --start as a one-day date range. Cannot be combined with --end.",
    )
    return parser.parse_args()


def parse_iso(value: str, timezone: ZoneInfo) -> tuple[datetime, bool]:
    text = value.strip()
    if not text:
        raise ValueError("date value cannot be empty")
    if len(text) == 10:
        parsed_date = date.fromisoformat(text)
        return datetime.combine(parsed_date, time.min, tzinfo=timezone), True
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone), False


def main() -> None:
    args = parse_args()
    if args.end and args.exclusive_end:
        raise SystemExit("Use either --end or --exclusive-end, not both.")
    if args.single_day and (args.end or args.exclusive_end):
        raise SystemExit("--single-day cannot be combined with --end or --exclusive-end.")
    if not args.single_day and not args.end and not args.exclusive_end:
        raise SystemExit("Provide --end, --exclusive-end, or --single-day.")

    timezone = ZoneInfo(args.timezone)
    start, start_is_date_only = parse_iso(args.start, timezone)

    if args.single_day:
        end_exclusive = datetime.combine(start.date() + timedelta(days=1), time.min, tzinfo=timezone)
        end_mode = "single_day"
    elif args.exclusive_end:
        end_exclusive, _ = parse_iso(args.exclusive_end, timezone)
        end_mode = "already_exclusive"
    else:
        end_value, end_is_date_only = parse_iso(args.end, timezone)
        if end_is_date_only:
            end_exclusive = datetime.combine(
                end_value.date() + timedelta(days=1), time.min, tzinfo=timezone
            )
            end_mode = "inclusive_date_end"
        else:
            end_exclusive = end_value
            end_mode = "explicit_datetime_end"

    if end_exclusive <= start:
        raise SystemExit("The exclusive end must be after the start.")

    result = {
        "start_inclusive": start.isoformat(),
        "end_exclusive": end_exclusive.isoformat(),
        "timezone": args.timezone,
        "start_was_date_only": start_is_date_only,
        "end_mode": end_mode,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
