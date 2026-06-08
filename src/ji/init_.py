"""ji init — scaffold a journal directory."""

import argparse
from pathlib import Path
from .utils import journal_dir, save_config, load_config

TEMPLATE = """# Journal — {date}

## Entry

*What happened today? What are you thinking about?*

## Gratitude

- One thing you're grateful for today.
"""

INDEX_HEADER = """# Journal Index

A chronological record. Each file is named `YYYY-MM-DD.md`.

| Date | Summary |
|------|---------|
"""


def cmd_init(args: argparse.Namespace) -> None:
    """Scaffold journal directory structure."""
    if args.dir:
        jdir = Path(args.dir).expanduser().resolve()
    else:
        jdir = journal_dir()

    if jdir.exists() and any(jdir.iterdir()) and not args.force:
        print(f"⚠  {jdir} already exists and is non-empty. Use --force to overwrite index.")
        # still ensure the dir exists
        jdir.mkdir(parents=True, exist_ok=True)
        return

    jdir.mkdir(parents=True, exist_ok=True)

    # Save path to config
    config = load_config()
    config["dir"] = str(jdir)
    save_config(config)

    # Template
    tmpl = jdir / "TEMPLATE.md"
    if not tmpl.exists() or args.force:
        tmpl.write_text(TEMPLATE.format(date="YYYY-MM-DD"))

    # Index
    idx = jdir / "INDEX.md"
    if not idx.exists() or args.force:
        idx.write_text(INDEX_HEADER)

    # First entry
    from datetime import date
    today = date.today()
    first = jdir / f"{today.isoformat()}.md"
    if not first.exists():
        first.write_text(f"# {today.isoformat()}\n\n## Entry\n\nJournal started.\n")

    print(f"✓ Journal directory: {jdir}")
    print(f"  Templates: TEMPLATE.md, INDEX.md")
    print(f"  First entry: {first.name}")
