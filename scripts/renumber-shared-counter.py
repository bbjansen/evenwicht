#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Renumber all theorem-like items to a single shared counter per chapter.

Academic standard: Definition 14.1, Theorem 14.2, Lemma 14.3, Remark 14.4, ...
All theorem-like environments share one sequential counter within each chapter.

Separate counters are kept for:
  - Algorithm  (own counter: Algorithm 14.1, 14.2, ...)
  - Exercise   (own counter: Exercise 14.1, 14.2, ...)
  - Formula    (own counter: F14.1, F14.2, ...)

Uses a two-pass placeholder strategy to avoid collision bugs.

Usage:
    python3 scripts/renumber-shared-counter.py [--dry-run] [--chapters 1 2 3]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = PROJECT_ROOT / "docs" / "domains"
SOLUTIONS_DIR = PROJECT_ROOT / "docs" / "solutions"
VERIFY_DIR = PROJECT_ROOT / "verify"

# Items sharing the main counter
SHARED_KINDS = (
    "Definition", "Theorem", "Lemma", "Corollary", "Proposition",
    "Remark", "Example", "Notation", "Convention", "Axiom",
)

# Items with their own counter
SEPARATE_KINDS = ("Algorithm", "Exercise")

ALL_KINDS = SHARED_KINDS + SEPARATE_KINDS


def chapter_number(filepath: Path) -> int:
    return int(filepath.stem.split("-")[0])


def scan_items(content: str, ch: int, kinds: tuple[str, ...]) -> list[tuple[int, str, str]]:
    """Find all numbered items of given kinds belonging to this chapter, in order."""
    items: list[tuple[int, str, str]] = []
    seen: set[tuple[str, str]] = set()

    # Bold: **Definition 14.3** or **Theorem 6.26**
    bold_re = re.compile(
        r"\*\*(" + "|".join(kinds) + r")\s+(\d+)\.(\d+[a-z]?)\*\*"
    )
    for m in bold_re.finditer(content):
        kind, prefix, num = m.group(1), int(m.group(2)), m.group(3)
        if prefix == ch:
            label = f"{prefix}.{num}"
            key = (kind, label)
            if key not in seen:
                seen.add(key)
                items.append((m.start(), kind, label))

    # Heading: ### Algorithm 6.1: Title
    header_re = re.compile(
        r"^###\s+(" + "|".join(kinds) + r")\s+(\d+)\.(\d+[a-z]?)\s*:",
        re.MULTILINE,
    )
    for m in header_re.finditer(content):
        kind, prefix, num = m.group(1), int(m.group(2)), m.group(3)
        if prefix == ch:
            label = f"{prefix}.{num}"
            key = (kind, label)
            if key not in seen:
                seen.add(key)
                items.append((m.start(), kind, label))

    items.sort(key=lambda x: x[0])
    return items


def build_rename_map(content: str, ch: int) -> dict[str, str]:
    """Build old→new mapping for all items in a chapter."""
    rename_map: dict[str, str] = {}

    # Shared counter
    shared_items = scan_items(content, ch, SHARED_KINDS)
    for seq, (_, kind, old_label) in enumerate(shared_items, 1):
        new_label = f"{ch}.{seq}"
        if old_label != new_label:
            rename_map[f"{kind} {old_label}"] = new_label

    # Algorithm counter
    algo_items = scan_items(content, ch, ("Algorithm",))
    for seq, (_, kind, old_label) in enumerate(algo_items, 1):
        new_label = f"{ch}.{seq}"
        if old_label != new_label:
            rename_map[f"Algorithm {old_label}"] = new_label

    # Exercise counter
    ex_items = scan_items(content, ch, ("Exercise",))
    for seq, (_, kind, old_label) in enumerate(ex_items, 1):
        new_label = f"{ch}.{seq}"
        if old_label != new_label:
            rename_map[f"Exercise {old_label}"] = new_label

    return rename_map


def apply_map(content: str, rename_map: dict[str, str]) -> tuple[str, int]:
    """Apply rename map using two-pass placeholder strategy."""
    if not rename_map:
        return content, 0

    count = 0

    # Build placeholder map
    placeholders: dict[str, str] = {}
    for i, old_key in enumerate(rename_map):
        placeholders[old_key] = f"\x00RENUM{i:04d}\x00"

    # Pass 1: old labels → placeholders (longest first to avoid partial matches)
    for old_key in sorted(placeholders, key=lambda x: -len(x)):
        placeholder = placeholders[old_key]
        parts = old_key.split(" ", 1)
        kind, old_label = parts[0], parts[1]

        # Bold: **Kind N.M**
        pattern = rf"(\*\*{kind}\s+){re.escape(old_label)}(\*\*)"
        content, n = re.subn(pattern, rf"\g<1>{placeholder}\2", content)
        count += n

        # Heading: ### Kind N.M:
        pattern = rf"(^###\s+{kind}\s+){re.escape(old_label)}(\s*:)"
        content, n = re.subn(pattern, rf"\g<1>{placeholder}\2", content, flags=re.MULTILINE)
        count += n

        # Inline ref: Kind N.M (not bold, not followed by more digits)
        pattern = rf"(?<!\*\*)({kind}s?\s+){re.escape(old_label)}(?!\d)"
        content, n = re.subn(pattern, rf"\g<1>{placeholder}", content)
        count += n

        # Short exercise refs: Ex N.M, Ex. N.M
        if kind == "Exercise":
            for short in [r"Ex ", r"Ex\. "]:
                pattern = rf"(\b{short}){re.escape(old_label)}(?!\d)"
                content, n = re.subn(pattern, rf"\g<1>{placeholder}", content)
                count += n

    # Pass 2: placeholders → final labels
    for old_key, placeholder in placeholders.items():
        new_label = rename_map[old_key]
        content = content.replace(placeholder, new_label)

    return content, count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Renumber to single shared counter per chapter"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--chapters", nargs="+", type=int, default=list(range(1, 49))
    )
    args = parser.parse_args()

    # Phase 1: build all rename maps from domain files
    all_maps: dict[int, dict[str, str]] = {}
    for ch in sorted(args.chapters):
        for fpath in sorted(DOMAINS_DIR.glob(f"{ch:02d}-*.md")):
            with open(fpath) as f:
                content = f.read()
            rmap = build_rename_map(content, ch)
            if rmap:
                all_maps[ch] = rmap

    total_renames = sum(len(m) for m in all_maps.values())
    print(f"Chapters with renames: {len(all_maps)}")
    print(f"Total items to renumber: {total_renames}")

    if args.dry_run:
        for ch, rmap in sorted(all_maps.items()):
            print(f"\n  Ch{ch:02d}: {len(rmap)} renames")
            for old, new in sorted(rmap.items()):
                print(f"    {old} -> {old.split()[0]} {new}")
        print(f"\nRun without --dry-run to apply.")
        return

    if total_renames == 0:
        print("Nothing to renumber.")
        return

    # Phase 2: apply to all files
    total_files = 0
    total_changes = 0

    for ch in sorted(args.chapters):
        if ch not in all_maps:
            continue
        rmap = all_maps[ch]

        # Domain, solutions, verify files
        file_patterns = [
            (DOMAINS_DIR, f"{ch:02d}-*.md", ""),
            (SOLUTIONS_DIR, f"{ch:02d}-*.md", "solutions/"),
            (VERIFY_DIR, f"ch{ch:02d}_*.py", "verify/"),
        ]
        for directory, pattern, prefix in file_patterns:
            for fpath in sorted(directory.glob(pattern)):
                with open(fpath) as f:
                    content = f.read()
                new_content, n = apply_map(content, rmap)
                if n > 0:
                    with open(fpath, "w") as f:
                        f.write(new_content)
                    print(f"  Ch{ch:02d} {prefix}{fpath.name}: {n} changes")
                    total_files += 1
                    total_changes += n

    # Phase 3: cross-chapter references
    print(f"\nScanning for cross-chapter references...")
    xref_changes = 0
    for ch_file in sorted(args.chapters):
        for directory, pattern, prefix in [
            (DOMAINS_DIR, f"{ch_file:02d}-*.md", ""),
            (SOLUTIONS_DIR, f"{ch_file:02d}-*.md", "solutions/"),
        ]:
            for fpath in sorted(directory.glob(pattern)):
                with open(fpath) as f:
                    content = f.read()
                changed = False
                for ref_ch, rmap in all_maps.items():
                    if ref_ch == ch_file:
                        continue
                    new_content, n = apply_map(content, rmap)
                    if n > 0:
                        content = new_content
                        changed = True
                        xref_changes += n
                if changed:
                    with open(fpath, "w") as f:
                        f.write(content)
                    print(f"  Ch{ch_file:02d} {prefix}{fpath.name}: cross-refs updated")
                    total_files += 1

    total_changes += xref_changes
    print(f"\nChanged {total_changes} references across {total_files} files")


if __name__ == "__main__":
    main()
