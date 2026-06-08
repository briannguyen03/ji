"""ji add — append a timed entry to a journal file."""

import argparse
import json
from datetime import date
from .utils import append_text, parse_date_arg


def cmd_add(args: argparse.Namespace) -> None:
    """Append an entry to the journal."""
    d: date = parse_date_arg(args.date) if args.date else date.today()
    text = " ".join(args.text)

    path = append_text(d, text)

    result = {"date": d.isoformat(), "file": str(path), "added": True}

    if args.json_out:
        print(json.dumps(result))
    else:
        print(f"✓ Wrote entry for {d.isoformat()} → {path}")
