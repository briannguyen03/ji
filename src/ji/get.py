"""ji get — read entries by date or range."""

import argparse
import json
from .utils import parse_date_arg, parse_date_range, entries_in_range


def cmd_get(args: argparse.Namespace) -> None:
    """Read entries and return structured data."""
    if args.date:
        start = end = parse_date_arg(args.date)
    else:
        start, end = parse_date_range(args.from_date, args.to_date)

    entries = entries_in_range(start, end)

    if args.json_out:
        output = []
        for d, text in entries:
            output.append({"date": d.isoformat(), "text": text})
        print(json.dumps(output))
    else:
        if not entries:
            print(f"No entries found ({start.isoformat()} – {end.isoformat()})")
            return
        for d, text in entries:
            print(f"--- {d.isoformat()} ---")
            print(text.strip())
            print()
