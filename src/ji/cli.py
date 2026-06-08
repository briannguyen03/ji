"""ji — Journal Interface CLI entry point."""

import argparse
import sys

from .add import cmd_add
from .get import cmd_get
from .init_ import cmd_init
from .search import cmd_search
from .stats import cmd_stats


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        dest="json_out",
        action="store_true",
        help="Output structured JSON (for agent consumption)",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="ji",
        description="Journal Interface — CLI for AI-assisted journaling.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- add ---
    p_add = sub.add_parser("add", help="Append a journal entry")
    _add_json_flag(p_add)
    p_add.add_argument("text", nargs="+", help="Entry text")
    p_add.add_argument("--date", "-d", help="Date (ISO, 'today', 'yesterday')")
    p_add.set_defaults(func=cmd_add)

    # --- get ---
    p_get = sub.add_parser("get", help="Read journal entries")
    _add_json_flag(p_get)
    p_get.add_argument("--date", help="Single date (ISO, 'today', 'yesterday')")
    p_get.add_argument("--from", dest="from_date", help="Range start")
    p_get.add_argument("--to", dest="to_date", help="Range end")
    p_get.set_defaults(func=cmd_get)

    # --- search ---
    p_search = sub.add_parser("search", help="Search journal entries (grep)")
    _add_json_flag(p_search)
    p_search.add_argument("query", nargs="+", help="Search terms")
    p_search.set_defaults(func=cmd_search)

    # --- stats ---
    p_stats = sub.add_parser("stats", help="Journal statistics")
    _add_json_flag(p_stats)
    p_stats.add_argument("--week", action="store_true", help="Show this week stats")
    p_stats.add_argument("--from", dest="from_date", help="Range start")
    p_stats.add_argument("--to", dest="to_date", help="Range end")
    p_stats.set_defaults(func=cmd_stats)

    # --- init ---
    p_init = sub.add_parser("init", help="Scaffold a journal directory")
    p_init.add_argument("dir", nargs="?", help="Journal directory path")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing")
    p_init.set_defaults(func=cmd_init)

    args = parser.parse_args(argv)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
