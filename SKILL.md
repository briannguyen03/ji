---
name: ji
description: Journal Interface — CLI for AI-assisted journaling using the ji tool. For journal prompts, reading past entries, stats, and search. Add entries on behalf of the user, read back history, and generate journal prompts using ji commands.
---

# ji — Journal Interface CLI

A zero-dependency CLI journaling tool. Journal entries are plain markdown files stored on disk. All commands support `--json` for agent consumption.

## Location

The project lives at `~/.openclaw/workspace/ji/`. The launcher is at `~/.openclaw/workspace/ji/bin/ji`. The journal directory default is `~/.ji/journal/`.

## Commands

### `ji init [dir]`

Scaffold a journal directory. Creates `INDEX.md`, `TEMPLATE.md`, and today's first entry. Saves the path to `~/.ji/config.json` so subsequent commands find it automatically.

```bash
ji init                    # uses default ~/.ji/journal
ji init /custom/path       # specify a path
ji init /custom/path --force  # overwrite existing index/template
```

### `ji add <text> [--date DATE | -d DATE] [--json]`

Append a timestamped entry to a date's markdown file. Auto-creates the file if it doesn't exist.

```bash
ji add "Had an amazing sushi dinner"
ji add -d yesterday "Finished the wiring diagram"
ji add --date 2026-06-07 "Project milestone reached"
ji add "JSON output for agents" --json
```

**Date formats accepted:** `today`, `yesterday`, ISO (`2026-06-07`), or `m-d`/`m/d` (`6/7`, `06-07`).

The entry is appended with a timestamp line formatted as:
```
**HH:MM** — Your entry text here
```

### `ji get [--date DATE | -d DATE] [--from DATE --to DATE] [--json]`

Read journal entries — single day or range. No args defaults to the current ISO week (Monday–Sunday).

```bash
ji get -d today
ji get -d 2026-06-07
ji get --from 2026-06-01 --to 2026-06-07
ji get --json          # structured output for agents
```

**`--json` output format:**
```json
[{"date": "2026-06-07", "text": "# 2026-06-07\n\n**15:59** — Entry text"}]
```

### `ji search <query> [--json]`

Case-insensitive grep across all entry files. Returns matching lines with line numbers. Skips INDEX.md, TEMPLATE.md automatically.

```bash
ji search "sushi"
ji search "deploy" --json
```

**`--json` output format:**
```json
[{"date": "2026-06-07", "file": "/path/2026-06-07.md", "matches": [{"line": 12, "text": "**20:30** — Had amazing sushi"}]}]
```

### `ji stats [--week] [--from DATE --to DATE] [--json]`

Journal statistics — entry count, word count, streaks, date coverage.

```bash
ji stats
ji stats --week
ji stats --from 2026-01-01 --to 2026-06-01 --json
```

**Stats include:**
- Total entries and words
- Average words per entry
- Current streak (consecutive days ending today)
- Longest streak ever
- First and last entry dates
- Week-specific counts (with `--week`)

**`--json` output format:**
```json
{"total_entries": 42, "total_words": 5600, "current_streak": 5, "longest_streak": 12, "first_date": "2026-01-15", "last_date": "2026-06-08"}
```

## Workflows

### Morning Journal Prompt

Use `ji stats --json` to check if there are recent entries, then prompt for a new entry based on yesterday or today:

```bash
ji get -d yesterday
# → read yesterday's entry
ji add "What I'm doing today"
```

### Evening Reflection

When prompting for a daily journal entry:

```bash
ji stats       # check streak
ji get -d today  # see if already entered
ji add "..."   # add the entry
```

### Context Retrieval

When the user asks "what did I do last week?" or similar:

```bash
ji get --from <date> --to <date>
```

To search for specific topics:

```bash
ji search "<topic>"
```

### Review & Insights

Pull stats and recent entries when the user wants to reflect on progress:

```bash
ji stats           # overview
ji search "<project name>"  # find project references
```

## File Format

Each journal entry is a markdown file named `YYYY-MM-DD.md`:

```markdown
# YYYY-MM-DD

## Entry

**HH:MM** — Entry text

**HH:MM** — Another entry
```

Files are human-readable and hand-editable. No magic format.

## Config

Config file: `~/.ji/config.json`

```json
{"dir": "/home/user/.ji/journal"}
```

Config can be set by:
- `ji init /path` (writes to config)
- `$JI_DIR` environment variable (overrides everything)

The `journal_dir()` function checks in this order:
1. `$JI_DIR` env var
2. `~/.ji/config.json`
3. `~/.ji/journal` (default fallback)

## Agent Usage Notes

- Always use `--json` when you need structured data to parse
- Use `ji stats` before prompting to know if the user has journaled recently
- Default date range (no args on `get` or `stats`) is the current ISO week
- `ji search` is grep-based (Phase 1) — good for keyword lookup, less good for fuzzy/semantic
- The user's current journal path is stored in `~/.ji/config.json`
