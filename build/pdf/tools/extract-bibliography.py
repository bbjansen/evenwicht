#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Extract all references from the 48 chapter markdown files and produce a
consolidated, deduplicated bibliography sorted alphabetically by author within
each category.

Source: docs/domains/[0-9]*.md  (each has ## 12. References ... ## 13. Glossary)
Output: dist/bibliography.md
"""

from __future__ import annotations

import glob
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"
OUTPUT_FILE = PROJECT_ROOT / "dist" / "bibliography.md"

CATEGORIES = ["Textbooks", "Historical", "Online Resources"]

# Map the subsection headings found in the source files to the output headings.
CATEGORY_OUTPUT = {
    "Textbooks": "Textbooks",
    "Historical": "Historical Sources",
    "Online Resources": "Online Resources",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def chapter_number(filepath: str) -> int:
    """Return the chapter number from a filename like '03-limits-continuity.md'."""
    basename = os.path.basename(filepath)
    match = re.match(r"(\d+)", basename)
    if match:
        return int(match.group(1))
    return 0


def extract_references_section(text: str) -> str | None:
    """Return the text between '## 12. References' and '## 13. Glossary'."""
    # Match the references heading (with or without section number).
    start = re.search(r"^## (?:\d+\.\s*)?References\s*$", text, re.MULTILINE)
    if not start:
        return None
    # Match the glossary heading (with or without section number).
    end = re.search(r"^## (?:\d+\.\s*)?Glossary\s*$", text[start.end():], re.MULTILINE)
    if end:
        return text[start.end(): start.end() + end.start()]
    # If no glossary, take everything after references.
    return text[start.end():]


def parse_references(section: str) -> dict[str, list[str]]:
    """Parse a references section into {category: [ref_text, ...]}."""
    result: dict[str, list[str]] = {cat: [] for cat in CATEGORIES}
    current_category: str | None = None

    for line in section.splitlines():
        # Detect subsection heading.
        heading_match = re.match(r"^###\s+(.+)$", line)
        if heading_match:
            heading = heading_match.group(1).strip()
            if heading in CATEGORIES:
                current_category = heading
            continue

        # Detect a reference item (with or without bullet prefix).
        ref_match = re.match(r"^(?:- )?\[(\d+)\]\s+(.+)$", line)
        if ref_match and current_category:
            ref_body = ref_match.group(2).strip()
            result[current_category].append(ref_body)

    return result


def normalise_for_dedup(ref_body: str) -> str:
    """Produce a normalised key for deduplication.

    Strip trailing punctuation differences, collapse whitespace, lower-case.
    """
    key = ref_body.strip().rstrip(".")
    key = re.sub(r"\s+", " ", key)
    return key.lower()


def sort_key(ref_body: str) -> str:
    """Return a sort key based on the author's last name (lowercase)."""
    return ref_body.lower()


def format_chapters(chapters: list[int]) -> str:
    """Format a list of chapter numbers as '(Chapter 3)' or '(Chapters 1, 5, 12)'."""
    chapters = sorted(set(chapters))
    if len(chapters) == 1:
        return f"(Chapter {chapters[0]})"
    return "(Chapters " + ", ".join(str(c) for c in chapters) + ")"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    source_files = sorted(glob.glob(str(DOCS_DIR / "[0-9]*.md")))
    if not source_files:
        print("Error: no source files found in", DOCS_DIR, file=sys.stderr)
        sys.exit(1)

    # {category: {normalised_key: (canonical_text, [chapter_numbers])}}
    bibliography: dict[str, dict[str, tuple[str, list[int]]]] = {
        cat: {} for cat in CATEGORIES
    }

    total_raw = 0
    files_processed = 0

    for filepath in source_files:
        chap = chapter_number(filepath)
        text = Path(filepath).read_text(encoding="utf-8")
        section = extract_references_section(text)
        if section is None:
            print(f"Warning: no references section found in {filepath}", file=sys.stderr)
            continue

        files_processed += 1
        refs = parse_references(section)

        for category in CATEGORIES:
            for ref_body in refs[category]:
                total_raw += 1
                key = normalise_for_dedup(ref_body)
                if key in bibliography[category]:
                    # Duplicate -- add the chapter number.
                    existing_text, chapters = bibliography[category][key]
                    chapters.append(chap)
                else:
                    bibliography[category][key] = (ref_body, [chap])

    # Build output.
    lines: list[str] = ["# Bibliography", ""]

    total_unique = 0
    for category in CATEGORIES:
        entries = bibliography[category]
        if not entries:
            continue

        output_heading = CATEGORY_OUTPUT[category]
        lines.append(f"## {output_heading}")
        lines.append("")

        # Sort alphabetically by canonical text.
        sorted_entries = sorted(entries.values(), key=lambda e: sort_key(e[0]))

        ref_num = 0
        for ref_text, chapters in sorted_entries:
            total_unique += 1
            ref_num += 1
            chap_str = format_chapters(chapters)
            lines.append(f"[{ref_num}] {ref_text} {chap_str}")
            lines.append("")

    # Write output.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")

    # Report.
    duplicates = total_raw - total_unique
    print(f"Processed {files_processed} chapter files")
    print(f"Total raw references:    {total_raw}")
    print(f"Total unique references: {total_unique}")
    print(f"Duplicates removed:      {duplicates}")
    print(f"Output written to:       {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
