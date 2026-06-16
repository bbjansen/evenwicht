#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Strip hardcoded theme init lines from xychart-beta mermaid blocks.

Removes %%{init:...}%% lines that appear inside mermaid code blocks
immediately before an ``xychart-beta`` directive.  Init lines for other
diagram types (timelines, mindmaps, flowcharts, etc.) are left untouched.

Usage:
    python3 scripts/strip-xychart-themes.py                    # dry run (show changes)
    python3 scripts/strip-xychart-themes.py --apply            # apply changes
    python3 scripts/strip-xychart-themes.py --apply FILE ...   # apply to specific files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

INIT_RE = re.compile(r"^\s*%%\{init:.*\}%%\s*$")


def strip_xychart_themes(text: str) -> tuple[str, int]:
    """Remove init lines that precede xychart-beta in mermaid blocks.

    Returns (new_text, count_of_removals).
    """
    lines = text.split("\n")
    result: list[str] = []
    count = 0
    in_mermaid = False
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```mermaid"):
            in_mermaid = True
            result.append(line)
            i += 1
            continue

        if in_mermaid and line.strip().startswith("```"):
            in_mermaid = False
            result.append(line)
            i += 1
            continue

        if in_mermaid and INIT_RE.match(line):
            # Peek ahead to see if the next non-blank line is xychart-beta
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j < len(lines) and lines[j].strip().startswith("xychart-beta"):
                # Skip this init line
                count += 1
                i += 1
                continue

        result.append(line)
        i += 1

    return "\n".join(result), count


def process_file(filepath: Path, apply: bool) -> int:
    """Process a single file. Returns number of init lines removed."""
    text = filepath.read_text(encoding="utf-8")
    new_text, count = strip_xychart_themes(text)

    if count == 0:
        return 0

    rel = filepath.relative_to(PROJECT_ROOT)
    if apply:
        filepath.write_text(new_text, encoding="utf-8")
        print(f"  {rel}: removed {count} init line(s)")
    else:
        print(f"  {rel}: would remove {count} init line(s)")

    return count


def main() -> int:
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]

    if args:
        files = [Path(a).resolve() for a in args]
    else:
        files = sorted(DOCS_DIR.glob("*.md"))

    total = 0
    for f in files:
        total += process_file(f, apply)

    mode = "Applied" if apply else "Dry run"
    print(f"\n{mode}: {total} init line(s) across {len(files)} file(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
