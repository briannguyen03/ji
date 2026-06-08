"""ji search — grep-based full-text search across journal entries.

Phase 1: plain grep (zero deps).
Phase 2 (future): vector search with fallback to grep.
"""

import argparse
import json
import re
from pathlib import Path
from .utils import journal_dir


def cmd_search(args: argparse.Namespace) -> None:
    """Search journal entries for a query string."""
    query = " ".join(args.query)
    jdir = journal_dir()
    if not jdir.exists():
        print("[]" if args.json_out else "No journal directory found.")
        return

    results: list[dict] = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for fpath in sorted(jdir.glob("*.md")):
        if fpath.name in ("INDEX.md", "TEMPLATE.md", "README.md"):
            continue
        date_str = fpath.stem
        try:
            text = fpath.read_text(encoding="utf-8")
        except OSError:
            continue

        matches: list[dict] = []
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                matches.append({"line": i, "text": line.strip()})

        if matches:
            results.append({"date": date_str, "file": str(fpath), "matches": matches})

    if args.json_out:
        print(json.dumps(results))
    else:
        if not results:
            print(f"No matches for {query!r}")
            return
        for r in results:
            print(f"📄 {r['date']} ({r['file']})")
            for m in r["matches"]:
                print(f"  L{m['line']}: {m['text']}")
            print()
