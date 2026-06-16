#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Word count report for Evenwicht domain chapters.

Counts words per chapter and per H2 section, excluding code blocks,
mermaid blocks, math blocks, and HTML comments. Flags chapters that
are significantly shorter or longer than the average.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = PROJECT_ROOT / "docs" / "domains"

# Patterns for blocks to exclude
CODE_BLOCK_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MATH_BLOCK_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
INLINE_MATH_RE = re.compile(r"\$[^$\n]+?\$")
H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def strip_excluded(text: str) -> str:
    """Remove code blocks, mermaid blocks, math blocks, and HTML comments."""
    text = HTML_COMMENT_RE.sub("", text)
    text = CODE_BLOCK_RE.sub("", text)
    text = MATH_BLOCK_RE.sub("", text)
    text = INLINE_MATH_RE.sub("", text)
    return text


def count_words(text: str) -> int:
    """Count whitespace-delimited words in cleaned text."""
    cleaned = strip_excluded(text)
    return len(cleaned.split())


def split_h2_sections(text: str) -> list[tuple[str, str]]:
    """Split text into (section_title, section_body) pairs by H2 headings.

    Content before the first H2 is assigned to a "Preamble" section.
    """
    splits = H2_RE.split(text)
    sections: list[tuple[str, str]] = []
    if splits[0].strip():
        sections.append(("Preamble", splits[0]))
    for i in range(1, len(splits), 2):
        title = splits[i]
        body = splits[i + 1] if i + 1 < len(splits) else ""
        sections.append((title, body))
    return sections


def get_chapter_files() -> list[Path]:
    """Return sorted list of chapter markdown files matching [0-9]*.md."""
    return sorted(DOMAINS_DIR.glob("[0-9]*.md"))


def main() -> int:
    files = get_chapter_files()
    if not files:
        print(f"ERROR: No chapter files found in {DOMAINS_DIR}")
        return 1

    chapter_data: list[dict] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        total_words = count_words(text)
        sections = split_h2_sections(text)
        section_counts = [
            (title, count_words(body)) for title, body in sections
        ]
        chapter_data.append(
            {
                "file": path.name,
                "total": total_words,
                "sections": section_counts,
            }
        )

    # Compute statistics
    totals = [c["total"] for c in chapter_data]
    grand_total = sum(totals)
    avg_words = grand_total / len(totals) if totals else 0

    # Print per-chapter table
    print("=" * 78)
    print("WORD COUNT REPORT — Evenwicht Domain Chapters")
    print("=" * 78)
    print()
    print(f"{'Chapter':<42} {'Words':>8}  {'Status':<12}")
    print("-" * 78)

    flagged: list[tuple[str, int, str]] = []
    for ch in chapter_data:
        status = ""
        if avg_words > 0:
            ratio = ch["total"] / avg_words
            if ratio > 1.5:
                status = "LONG (>{:.0f}x)".format(ratio)
                flagged.append((ch["file"], ch["total"], status))
            elif ratio < 0.5:
                status = "SHORT (<{:.1f}x)".format(ratio)
                flagged.append((ch["file"], ch["total"], status))
        print(f"  {ch['file']:<40} {ch['total']:>8}  {status}")

    print("-" * 78)
    print(f"  {'Grand Total':<40} {grand_total:>8}")
    print(f"  {'Average per chapter':<40} {avg_words:>8.0f}")
    print()

    # Per-section detail
    print("=" * 78)
    print("PER-SECTION BREAKDOWN")
    print("=" * 78)
    for ch in chapter_data:
        print()
        print(f"  {ch['file']}")
        for title, wc in ch["sections"]:
            print(f"    {title:<38} {wc:>6}")

    # Section average across chapters
    all_section_counts: list[int] = []
    for ch in chapter_data:
        all_section_counts.extend(wc for _, wc in ch["sections"])
    if all_section_counts:
        section_avg = sum(all_section_counts) / len(all_section_counts)
        print()
        print(f"  Average words per section: {section_avg:.0f}")

    # Flagged chapters summary
    if flagged:
        print()
        print("=" * 78)
        print("FLAGGED CHAPTERS (outside 0.5x-1.5x of average)")
        print("=" * 78)
        for name, words, status in flagged:
            print(f"  {name:<40} {words:>8}  {status}")
    else:
        print()
        print("No chapters flagged — all within 0.5x-1.5x of average.")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
