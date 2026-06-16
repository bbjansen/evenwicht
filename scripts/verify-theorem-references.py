#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify cross-chapter theorem/definition citations across all Evenwicht chapters.

Checks that every cross-chapter citation of a theorem, definition, lemma,
corollary, proposition, remark, or example points to an item that actually
exists in the target chapter.

Cross-chapter citation patterns detected:
  P1  "Theorem 3.19 of [Chapter 39](39-...)"
  P2  "[Chapter 4](04-...), Theorem 3.23"
  P3  "in/from/per [Chapter 13](13-...), Theorem 3.38"
  P4  "[Chapter 39](39-...), Theorem 3.7"   (same as P2)
  P5  "Theorem 18.3"  referenced from a different chapter (chapter-number prefix)

Note: Labels in parentheses that appear in the same bullet as a chapter link
but with intervening descriptive text are typically self-references (e.g.,
"[Chapter 10] (Eigenvalues): ... (Theorem 3.9)" where Theorem 3.9 is in the
current chapter).  These are intentionally excluded.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAIN_DIR = PROJECT_ROOT / "docs" / "domains"

# Label kinds we track.
LABEL_KINDS = (
    "Theorem",
    "Definition",
    "Lemma",
    "Corollary",
    "Proposition",
    "Remark",
    "Example",
)
KINDS_PATTERN = "|".join(LABEL_KINDS)

# ── Regex: extract label definitions ────────────────────────────────────
# Matches **Theorem 3.5**, **Definition 3.1**, **Remark 3.5a**, etc.
LABEL_DEF_RE = re.compile(
    rf"\*\*({KINDS_PATTERN})\s+(\d+\.\d+\w*)\*\*"
)

# ── Regex: extract cross-chapter citations ──────────────────────────────
# We look for several patterns that pair a label with a chapter number.
#
# Pattern A: "Theorem 3.19 of [Chapter 39](39-...)"
#   captures (kind, number, chapter_num)
CITE_OF_CHAPTER_RE = re.compile(
    rf"({KINDS_PATTERN})\s+(\d+\.\d+\w*)\s+of\s+\[Chapter\s+(\d+)\]"
)

# Pattern B: "[Chapter N](NN-...), Theorem 3.X" or "[Chapter N](NN-...) Theorem 3.X"
#   Matches the chapter link immediately followed by comma/space then a label.
#   This is the dominant pattern for explicit cross-references.
CITE_CHAPTER_COMMA_RE = re.compile(
    r"\[Chapter\s+(\d+)\]"
    r"\([^\)]*\)"
    r"[,;:\s]*\s*"
    rf"({KINDS_PATTERN})\s+(\d+\.\d+\w*)"
)

# Pattern C: "in/from/per [Chapter N](NN-...), Theorem 3.X"
CITE_IN_CHAPTER_RE = re.compile(
    r"(?:in|from|per)\s+\[Chapter\s+(\d+)\]"
    r"\([^\)]*\)"
    r"[,;:\s]*\s*"
    rf"({KINDS_PATTERN})\s+(\d+\.\d+\w*)"
)

# Pattern D: Chapter-numbered labels referenced from a different chapter.
#   E.g., "Theorem 18.3" appearing in chapter 40 — the prefix 18 != 40
#   (the source chapter) and is not a standard section number, so it must
#   be a reference to chapter 18.
#
#   Standard section numbers (1-13) overlap with chapter numbers, so we
#   cannot distinguish by prefix alone for chapters 1-13.  This pattern
#   only applies to prefixes >= 14 that match a known chapter number.
CITE_CHAPTER_NUMBERED_RE = re.compile(
    rf"(?<!\*\*)({KINDS_PATTERN})\s+(\d+)\.(\d+\w*)"
)

# Section numbers used within chapters — these overlap with chapter numbers
# 1 through 13, so we cannot use them for implicit chapter detection.
SECTION_NUMBERS = set(range(1, 14))


def get_chapter_files() -> list[Path]:
    """Return all chapter markdown files sorted by chapter number."""
    return sorted(DOMAIN_DIR.glob("[0-9]*.md"))


def extract_chapter_number(path: Path) -> int:
    """Extract the leading chapter number from a filename."""
    m = re.match(r"(\d+)", path.name)
    return int(m.group(1)) if m else 0


def build_label_registry(
    files: list[Path],
) -> dict[int, set[tuple[str, str]]]:
    """Build a registry of all defined labels per chapter.

    Returns {chapter_num: {("Theorem", "3.5"), ("Definition", "3.1a"), ...}}.
    """
    registry: dict[int, set[tuple[str, str]]] = {}
    for path in files:
        ch_num = extract_chapter_number(path)
        text = path.read_text(encoding="utf-8")
        labels: set[tuple[str, str]] = set()
        for m in LABEL_DEF_RE.finditer(text):
            kind = m.group(1)
            number = m.group(2)
            labels.add((kind, number))
        registry[ch_num] = labels
    return registry


def extract_cross_citations(
    path: Path,
    source_chapter: int,
    all_chapter_nums: set[int],
) -> list[tuple[int, str, str, int, str]]:
    """Extract cross-chapter citations from a file.

    Returns list of (target_chapter, kind, number, line_number, matched_text).
    Only returns citations that reference a *different* chapter.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    citations: list[tuple[int, str, str, int, str]] = []
    seen: set[tuple[int, str, str, int]] = set()

    for line_idx, line in enumerate(lines, start=1):
        # Pattern A: "Kind N.M of [Chapter X]"
        for m in CITE_OF_CHAPTER_RE.finditer(line):
            kind, number, ch_str = m.group(1), m.group(2), m.group(3)
            target_ch = int(ch_str)
            key = (target_ch, kind, number, line_idx)
            if target_ch != source_chapter and key not in seen:
                seen.add(key)
                citations.append(
                    (target_ch, kind, number, line_idx, m.group(0))
                )

        # Pattern B/C: "[Chapter X](...), Kind N.M" or
        #              "in/from/per [Chapter X](...), Kind N.M"
        for pattern in (
            CITE_CHAPTER_COMMA_RE,
            CITE_IN_CHAPTER_RE,
        ):
            for m in pattern.finditer(line):
                ch_str, kind, number = m.group(1), m.group(2), m.group(3)
                target_ch = int(ch_str)
                key = (target_ch, kind, number, line_idx)
                if target_ch != source_chapter and key not in seen:
                    seen.add(key)
                    citations.append(
                        (target_ch, kind, number, line_idx, m.group(0))
                    )

        # Pattern D: Chapter-numbered labels.
        # A label like "Theorem 18.3" in chapter 40 has prefix 18, which
        # does not match any standard section number (1-13) and is not the
        # source chapter (40).  If 18 is a known chapter number, this is
        # a cross-reference.
        for m in CITE_CHAPTER_NUMBERED_RE.finditer(line):
            kind = m.group(1)
            prefix = int(m.group(2))
            suffix = m.group(3)
            number = f"{prefix}.{suffix}"

            # Skip if prefix matches a standard section number (ambiguous
            # with chapters 1-13), or matches the source chapter, or is
            # not a known chapter number.
            if prefix in SECTION_NUMBERS:
                continue
            if prefix == source_chapter:
                continue
            if prefix not in all_chapter_nums:
                continue

            # Skip bold definitions (**Theorem 18.3**) — those are
            # definitions, not citations.
            start = m.start()
            if start >= 2 and line[start - 2 : start] == "**":
                continue

            target_ch = prefix
            key = (target_ch, kind, number, line_idx)
            if key not in seen:
                seen.add(key)
                citations.append(
                    (target_ch, kind, number, line_idx, m.group(0))
                )

    return citations


def main() -> int:
    files = get_chapter_files()
    if not files:
        print(f"ERROR: No domain files found in {DOMAIN_DIR}")
        return 1

    # ── Phase 1: Build the label registry ───────────────────────────────
    registry = build_label_registry(files)

    # ── Phase 2: Scan for cross-chapter citations ───────────────────────
    all_chapter_nums = set(registry.keys())
    all_citations: list[
        tuple[str, int, int, str, str, int, str]
    ] = []  # (source_file, source_ch, target_ch, kind, number, line, text)

    for path in files:
        source_ch = extract_chapter_number(path)
        cites = extract_cross_citations(path, source_ch, all_chapter_nums)
        for target_ch, kind, number, line_num, matched in cites:
            all_citations.append(
                (path.name, source_ch, target_ch, kind, number, line_num, matched)
            )

    # ── Phase 3: Verify each citation ───────────────────────────────────
    missing: list[tuple[str, int, int, str, str, int, str]] = []
    valid_count = 0

    for entry in all_citations:
        source_file, source_ch, target_ch, kind, number, line_num, matched = entry
        target_labels = registry.get(target_ch, set())

        # Check exact match first.
        if (kind, number) in target_labels:
            valid_count += 1
            continue

        # Some citations use a base number without a letter suffix, while
        # the definition has a suffix (e.g., citing "Theorem 3.6" when the
        # chapter defines "Theorem 3.6a").  Check for any suffix match.
        base_match = any(
            lk == kind and ln.startswith(number)
            for lk, ln in target_labels
        )
        if base_match:
            valid_count += 1
            continue

        # Not found — record as missing.
        missing.append(entry)

    # ── Output ──────────────────────────────────────────────────────────
    print("=" * 78)
    print("CROSS-CHAPTER THEOREM/DEFINITION REFERENCE VERIFICATION — Evenwicht")
    print("=" * 78)
    print()

    # Registry summary
    print(f"{'Chapter':<35} {'Labels defined':>14}")
    print("-" * 51)
    for ch_num in sorted(registry.keys()):
        labels = registry[ch_num]
        ch_file = next(
            (f.name for f in files if extract_chapter_number(f) == ch_num),
            f"Chapter {ch_num}",
        )
        print(f"  {ch_file:<33} {len(labels):>14}")
    print()

    # Citation summary
    print("=" * 78)
    print("CITATION SUMMARY")
    print("=" * 78)
    print(f"  Total cross-chapter citations found:  {len(all_citations)}")
    print(f"  Valid (target exists):                {valid_count}")
    print(f"  Missing (target not found):           {len(missing)}")
    print()

    # Per-source breakdown of citations
    source_counts: dict[str, int] = {}
    for entry in all_citations:
        source_file = entry[0]
        source_counts[source_file] = source_counts.get(source_file, 0) + 1
    if source_counts:
        print(f"{'Source file':<35} {'Citations':>10}")
        print("-" * 47)
        for sf in sorted(source_counts.keys()):
            print(f"  {sf:<33} {source_counts[sf]:>10}")
        print()

    # ── Missing details ─────────────────────────────────────────────────
    if missing:
        print("=" * 78)
        print(f"MISSING REFERENCES ({len(missing)})")
        print("=" * 78)

        # Group by source file
        by_source: dict[str, list[tuple[int, int, str, str, int, str]]] = {}
        for entry in missing:
            source_file = entry[0]
            rest = entry[1:]
            by_source.setdefault(source_file, []).append(rest)

        for source_file in sorted(by_source.keys()):
            print(f"\n  {source_file}:")
            for source_ch, target_ch, kind, number, line_num, matched in by_source[
                source_file
            ]:
                target_labels = registry.get(target_ch, set())
                available = sorted(
                    f"{k} {n}"
                    for k, n in target_labels
                    if k == kind
                )
                avail_str = (
                    f" (available: {', '.join(available[:5])})"
                    if available
                    else " (no such kind in target chapter)"
                )
                ch_exists = target_ch in registry
                if not ch_exists:
                    avail_str = " (target chapter file not found)"
                print(
                    f"    Line {line_num}: {kind} {number} -> "
                    f"Chapter {target_ch}{avail_str}"
                )
        print()

    # ── Final verdict ───────────────────────────────────────────────────
    print("=" * 78)
    print("RESULT")
    print("=" * 78)
    if missing:
        print(
            f"  FAIL: {len(missing)} cross-chapter citation(s) "
            f"reference items not found in their target chapter."
        )
        print()
        return 1
    else:
        print(
            "  PASS: All cross-chapter citations point to items "
            "that exist in their target chapters."
        )
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
