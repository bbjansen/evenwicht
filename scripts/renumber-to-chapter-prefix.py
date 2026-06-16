#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Renumber all section-based labels to chapter-based labels.

Every numbered element (Definition, Theorem, Algorithm, Example, Exercise,
Formula, Remark, Lemma, Corollary, Notation, Convention) gets the chapter
number as its prefix instead of the section number.

Usage:
    python3 scripts/renumber-to-chapter-prefix.py [--dry-run] [--chapters 1 2 3]

  --dry-run   : report what would change without writing files
  --chapters  : only process the listed chapter numbers (default: all 1-48)
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = PROJECT_ROOT / "docs" / "domains"
SOLUTIONS_DIR = PROJECT_ROOT / "docs" / "solutions"
VERIFY_DIR = PROJECT_ROOT / "verify"

# ── Label kinds that carry a chapter.number suffix ──────────────────────

LABEL_KINDS = (
    "Definition", "Theorem", "Lemma", "Corollary", "Proposition",
    "Example", "Remark", "Algorithm", "Notation", "Convention", "Axiom",
    "Exercise",
)

# Section numbers in the standard chapter layout
SECTION_MAP = {
    "Definition":  4,  "Theorem":     4,  "Lemma":       4,
    "Corollary":   4,  "Proposition": 4,  "Remark":      4,
    "Notation":    3,  "Convention":  3,  "Axiom":       4,
    "Algorithm":   6,  "Example":     8,  "Exercise":   10,
}


def chapter_number(filepath: str | Path) -> int:
    """Extract chapter number from filename like 01-expressions.md."""
    return int(Path(filepath).stem.split("-")[0])


def build_label_map(content: str, ch: int) -> dict[str, str]:
    """Scan content for all numbered labels and build old→new map.

    Returns a dict mapping e.g. "Definition 3.5" → "Definition 4.5"
    (only entries where old != new).
    """
    renames: dict[str, str] = {}

    # Bold labels: **Definition 3.5** or **Theorem 12.7a**
    for m in re.finditer(
        r"\*\*(" + "|".join(LABEL_KINDS) + r")\s+(\d+)\.(\d+[a-z]?)\*\*",
        content,
    ):
        kind, prefix, num = m.group(1), int(m.group(2)), m.group(3)
        expected_section = SECTION_MAP.get(kind)
        if prefix != ch and (expected_section is None or prefix == expected_section):
            old = f"{kind} {prefix}.{num}"
            new = f"{kind} {ch}.{num}"
            renames[old] = new

    # Heading labels: ### Algorithm 6.1: Title  or  ### Exercise 10.3:
    for m in re.finditer(
        r"^###\s+(" + "|".join(LABEL_KINDS) + r")\s+(\d+)\.(\d+[a-z]?):",
        content,
        re.MULTILINE,
    ):
        kind, prefix, num = m.group(1), int(m.group(2)), m.group(3)
        expected_section = SECTION_MAP.get(kind)
        if prefix != ch and (expected_section is None or prefix == expected_section):
            old = f"{kind} {prefix}.{num}"
            new = f"{kind} {ch}.{num}"
            renames[old] = new

    return renames


def apply_renames(content: str, ch: int) -> tuple[str, int]:
    """Apply all section→chapter renumbering to content. Returns (new_content, count)."""
    total = 0

    # 1. Labels: Definition X.n → Definition {ch}.n  (all label kinds)
    for kind in LABEL_KINDS:
        expected_section = SECTION_MAP.get(kind)
        if expected_section is None:
            continue

        # Bold labels:  **Definition 3.5**
        pattern = rf"(\*\*{kind}\s+){expected_section}\.(\d+[a-z]?)(\*\*)"
        replacement = rf"\g<1>{ch}.\2\3"
        content, n = re.subn(pattern, replacement, content)
        total += n

        # Heading labels:  ### Algorithm 6.1: Title
        pattern = rf"(^###\s+{kind}\s+){expected_section}\.(\d+[a-z]?)(:\s*)"
        replacement = rf"\g<1>{ch}.\2\3"
        content, n = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        total += n

        # Inline references:  Definition 3.5  or  Theorem 4.12  (not bold)
        pattern = rf"(?<!\*\*)({kind}s?\s+){expected_section}\.(\d+[a-z]?)"
        replacement = rf"\g<1>{ch}.\2"
        content, n = re.subn(pattern, replacement, content)
        total += n

        # Short references:  Ex 10.3  or  Ex. 10.3  (for Exercise only)
        if kind == "Exercise":
            for short in [r"\bEx ", r"\bEx\. "]:
                pattern = rf"({short}){expected_section}\.(\d+[a-z]?)"
                replacement = rf"\g<1>{ch}.\2"
                content, n = re.subn(pattern, replacement, content)
                total += n

    # 2. Formulas: F5.x → F{ch}.x  (or F4.x → F{ch}.x for early chapters)
    for sec in (4, 5):
        pattern = rf"\bF{sec}\.(\d+[a-z]?)"
        replacement = rf"F{ch}.\1"
        content, n = re.subn(pattern, replacement, content)
        total += n

    # 3. Subsection headers inside Core Theory: ### 3.1 Title → ### Title
    #    (only inside section 4)
    lines = content.split("\n")
    new_lines = []
    in_core_theory = False
    for line in lines:
        if re.match(r"^## 4\.\s", line):
            in_core_theory = True
        elif re.match(r"^## \d+\.\s", line):
            in_core_theory = False

        if in_core_theory:
            m = re.match(r"^(###\s+)\d+\.\d+\s+(.*)", line)
            if m:
                line = f"{m.group(1)}{m.group(2)}"
                total += 1

        new_lines.append(line)
    content = "\n".join(new_lines)

    # 4. Part A/B/C headings → plain descriptive
    content, n = re.subn(
        r"^(###\s+)Part [A-Z]:\s*",
        r"\1",
        content,
        flags=re.MULTILINE,
    )
    total += n

    return content, total


def process_file(filepath: Path, ch: int, dry_run: bool) -> int:
    """Process a single file. Returns number of changes."""
    with open(filepath) as f:
        content = f.read()

    new_content, count = apply_renames(content, ch)

    if count > 0 and not dry_run:
        with open(filepath, "w") as f:
            f.write(new_content)

    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Renumber labels to chapter prefix")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't write")
    parser.add_argument("--chapters", nargs="+", type=int, default=list(range(1, 49)),
                        help="Chapter numbers to process (default: 1-48)")
    args = parser.parse_args()

    total_files = 0
    total_changes = 0

    for ch in sorted(args.chapters):
        ch_changes = 0

        # Domain file
        for fpath in sorted(DOMAINS_DIR.glob(f"{ch:02d}-*.md")):
            n = process_file(fpath, ch, args.dry_run)
            if n > 0:
                print(f"  Ch{ch:02d} {fpath.name}: {n} changes")
                ch_changes += n
                total_files += 1

        # Solutions file
        for fpath in sorted(SOLUTIONS_DIR.glob(f"{ch:02d}-*.md")):
            n = process_file(fpath, ch, args.dry_run)
            if n > 0:
                print(f"  Ch{ch:02d} solutions/{fpath.name}: {n} changes")
                ch_changes += n
                total_files += 1

        # Verify scripts
        for fpath in sorted(VERIFY_DIR.glob(f"ch{ch:02d}_*.py")):
            n = process_file(fpath, ch, args.dry_run)
            if n > 0:
                print(f"  Ch{ch:02d} verify/{fpath.name}: {n} changes")
                ch_changes += n
                total_files += 1

        total_changes += ch_changes

    action = "Would change" if args.dry_run else "Changed"
    print(f"\n{action} {total_changes} references across {total_files} files")

    if args.dry_run and total_changes > 0:
        print("Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
