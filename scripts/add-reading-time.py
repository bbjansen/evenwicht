#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Add estimated reading time to chapter markdown files.

Counts words (excluding code blocks, mermaid blocks, HTML comments, and
front matter) and inserts a reading time line after the chapter title.
Uses 200 words per minute for academic/technical content.

Usage:
    python3 scripts/add-reading-time.py                    # dry run (show stats)
    python3 scripts/add-reading-time.py --apply            # apply changes
    python3 scripts/add-reading-time.py --apply FILE ...   # apply to specific files
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

WORDS_PER_MINUTE = 200

READING_TIME_RE = re.compile(r"^\*Estimated reading time: \d+ minutes?\*$")


def count_words(text: str) -> int:
    """Count words in markdown text, excluding code blocks, mermaid blocks,
    HTML comments, and YAML front matter."""

    # Remove YAML front matter
    content = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)

    # Remove HTML comments
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

    # Remove fenced code blocks (``` and ~~~) and mermaid blocks
    content = re.sub(r"^(`{3,}|~{3,}).*?\n\1\s*$", "", content, flags=re.DOTALL | re.MULTILINE)

    # Remove inline code
    content = re.sub(r"`[^`]+`", "", content)

    # Count remaining words
    words = content.split()
    return len(words)


def reading_time(word_count: int) -> int:
    """Calculate reading time in minutes, rounded up."""
    return max(1, math.ceil(word_count / WORDS_PER_MINUTE))


def add_reading_time(text: str) -> tuple[str, int, int]:
    """Insert or update reading time after the chapter title.

    Returns (new_text, word_count, minutes).
    """
    wc = count_words(text)
    minutes = reading_time(wc)
    reading_line = f"*Estimated reading time: {minutes} minutes*"

    lines = text.split("\n")
    result: list[str] = []
    inserted = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if not inserted and line.startswith("# Chapter "):
            result.append(line)
            i += 1

            # Check if the next non-blank line is already a reading time line
            # First, consume any blank line between title and potential reading time
            blanks: list[str] = []
            while i < len(lines) and lines[i].strip() == "":
                blanks.append(lines[i])
                i += 1

            if i < len(lines) and READING_TIME_RE.match(lines[i].strip()):
                # Replace existing reading time line
                result.append("")
                result.append(reading_line)
                i += 1  # skip old reading time line

                # Consume blank line after old reading time if present
                if i < len(lines) and lines[i].strip() == "":
                    result.append("")
                    i += 1
            else:
                # Insert new reading time line
                result.append("")
                result.append(reading_line)
                result.append("")
                # Re-add any blank lines we consumed, but we already add one above
                # so skip one blank if blanks were present
                if blanks:
                    # We already added a blank line after reading_line,
                    # the original had blank(s) before the next content line,
                    # so we don't need to re-add them (the one blank we added suffices)
                    pass
                else:
                    # No blank line was between title and next line originally;
                    # we still want one blank after reading time
                    pass

            inserted = True
            continue

        result.append(line)
        i += 1

    return "\n".join(result), wc, minutes


def process_file(filepath: Path, apply: bool) -> tuple[int, int]:
    """Process a single file. Returns (word_count, minutes)."""
    text = filepath.read_text(encoding="utf-8")
    new_text, wc, minutes = add_reading_time(text)

    rel = filepath.relative_to(PROJECT_ROOT)
    if apply:
        if new_text != text:
            filepath.write_text(new_text, encoding="utf-8")
            print(f"  {rel}: {wc} words, {minutes} min (updated)")
        else:
            print(f"  {rel}: {wc} words, {minutes} min (no change)")
    else:
        print(f"  {rel}: {wc} words, {minutes} min")

    return wc, minutes


def main() -> int:
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]

    if args:
        files = [Path(a).resolve() for a in args]
    else:
        files = sorted(DOCS_DIR.glob("*.md"))

    total_words = 0
    total_files = 0
    for f in files:
        wc, _ = process_file(f, apply)
        total_words += wc
        total_files += 1

    total_minutes = reading_time(total_words)
    mode = "Applied" if apply else "Dry run"
    print(f"\n{mode}: {total_files} file(s), {total_words} total words, ~{total_minutes} min total reading time")

    return 0


if __name__ == "__main__":
    sys.exit(main())
