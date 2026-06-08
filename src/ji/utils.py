"""Shared helpers for path resolution, date parsing, and file I/O."""

import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

ENV_JOURNAL_DIR = "JI_DIR"


def journal_dir() -> Path:
    """Resolve journal root directory.

    Priority: $JI_DIR → .ji/config.json → ~/.ji/journal
    """
    env = os.environ.get(ENV_JOURNAL_DIR)
    if env:
        return Path(env).expanduser().resolve()

    config = Path.home() / ".ji" / "config.json"
    if config.exists():
        try:
            cfg = json.loads(config.read_text())
            if "dir" in cfg:
                return Path(cfg["dir"]).expanduser().resolve()
        except (json.JSONDecodeError, OSError):
            pass

    return Path.home() / ".ji" / "journal"


def entry_path(d: date, base: Optional[Path] = None) -> Path:
    """Return path for a journal entry file on a given date."""
    base = base or journal_dir()
    return base / f"{d.isoformat()}.md"


def parse_date_arg(s: str) -> date:
    """Parse ISO date (2026-06-07) or relative shorthand.

    Supported:
        today         → today
        yesterday     → today - 1d
        2026-06-07    → explicit
    """
    s = s.strip().lower()
    if s == "today":
        return date.today()
    if s == "yesterday":
        return date.today() - timedelta(days=1)
    # try ISO
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass
    # try m-d or m/d
    m = re.match(r"^(\d{1,2})[-/](\d{1,2})$", s)
    if m:
        today = date.today()
        return date(today.year, int(m.group(1)), int(m.group(2)))
    raise ValueError(f"Unrecognised date: {s!r}")


def parse_date_range(
    from_str: Optional[str], to_str: Optional[str]
) -> tuple[date, date]:
    """Parse a date range; defaults to current week (Mon–Sun)."""
    if from_str and to_str:
        return parse_date_arg(from_str), parse_date_arg(to_str)
    if from_str:
        d = parse_date_arg(from_str)
        return d, d
    if to_str:
        d = parse_date_arg(to_str)
        return d, d

    # default: current ISO week (Mon–Sun)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def entries_in_range(
    start: date, end: date, base: Optional[Path] = None
) -> list[tuple[date, str]]:
    """Return sorted list of (date, full_text) for entries in [start, end]."""
    base = base or journal_dir()
    results: list[tuple[date, str]] = []
    current = start
    while current <= end:
        path = entry_path(current, base)
        if path.exists():
            text = path.read_text(encoding="utf-8")
            results.append((current, text))
        current += timedelta(days=1)
    return results


def append_text(d: date, text: str, base: Optional[Path] = None) -> Path:
    """Append a timed entry to the end of a journal file, creating it if needed."""
    p = entry_path(d, base)
    p.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%H:%M")
    block = f"\n**{timestamp}** — {text}\n"
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(block)
    return p


def load_config() -> dict:
    """Load ~/.ji/config.json or return empty defaults."""
    path = Path.home() / ".ji" / "config.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_config(cfg: dict) -> None:
    """Persist ~/.ji/config.json."""
    path = Path.home() / ".ji" / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n")
