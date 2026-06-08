"""ji stats — entry counts, word counts, streaks, date coverage."""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from .utils import journal_dir, parse_date_range


def cmd_stats(args: argparse.Namespace) -> None:
    """Compute journal statistics."""
    jdir = journal_dir()
    if not jdir.exists():
        print("{}" if args.json_out else "No journal directory found.")
        return

    # Gather all entry dates
    entry_dates: set[date] = set()
    entry_word_counts: dict[date, int] = {}
    for fpath in jdir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"):
        try:
            d = date.fromisoformat(fpath.stem)
            entry_dates.add(d)
            text = fpath.read_text(encoding="utf-8")
            entry_word_counts[d] = len(text.split())
        except (ValueError, OSError):
            continue

    if not entry_dates:
        print("{}" if args.json_out else "No entries found.")
        return

    total_entries = len(entry_dates)
    total_words = sum(entry_word_counts.values())
    sorted_dates = sorted(entry_dates)
    first_date = sorted_dates[0]
    last_date = sorted_dates[-1]

    # Streak: current consecutive days ending at last_date
    current_streak = 0
    check = last_date
    while check in entry_dates:
        current_streak += 1
        check -= timedelta(days=1)

    # Longest streak
    longest = 0
    run = 0
    if sorted_dates:
        run = 1
        longest = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                run += 1
                longest = max(longest, run)
            else:
                run = 1

    # Word count per entry (average)
    avg_words = total_words / total_entries if total_entries else 0

    # Week stats (if --week or within a range)
    if args.week:
        start, end = parse_date_range(args.from_date, args.to_date)
        week_entries = sum(1 for d in entry_dates if start <= d <= end)
        week_words = sum(
            wc for d, wc in entry_word_counts.items() if start <= d <= end
        )
    else:
        week_entries = total_entries
        week_words = total_words
        start = first_date
        end = last_date

    result = {
        "range": {"from": start.isoformat(), "to": end.isoformat()},
        "total_entries": total_entries,
        "total_words": total_words,
        "avg_words_per_entry": round(avg_words, 1),
        "current_streak": current_streak,
        "longest_streak": longest,
        "first_date": first_date.isoformat(),
        "last_date": last_date.isoformat(),
        "week_entries": week_entries,
        "week_words": week_words,
    }

    if args.json_out:
        print(json.dumps(result))
    else:
        print(f"📊 Journal Stats ({start.isoformat()} – {end.isoformat()})")
        print(f"  Entries: {total_entries} total")
        print(f"  Words:   {total_words} total, {avg_words:.0f} avg/entry")
        print(f"  Streak:  {current_streak} days (longest: {longest})")
        print(f"  Period:  {first_date.isoformat()} → {last_date.isoformat()}")
        if args.week:
            print(f"  Week:    {week_entries} entries, {week_words} words")
