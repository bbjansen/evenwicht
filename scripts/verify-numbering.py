#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify numbered label consistency across all chapter files.

Checks:
  1. Prefix mismatch  — items in chapter N must carry prefix N (e.g. Definition 4.3, not 3.3)
  2. Duplicate numbers — the same label number used twice in one chapter
  3. Sequence gaps    — numbers jump (e.g. 4.1, 4.2, 4.4 with 4.3 missing)
  4. Cross-references — inline references like "Definition 3.5" or "Theorem 7.12"
                        must resolve to an item that actually exists in the target chapter

Usage:
    python3 scripts/verify-numbering.py [--quick]

  --quick: skip cross-reference resolution (fast mode for CI)
"""

from __future__ import annotations

import glob
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

QUICK_MODE = "--quick" in sys.argv

# Labels that carry a numbered suffix (Chapter N.M style)
LABEL_KINDS = (
    "Definition", "Theorem", "Lemma", "Corollary", "Proposition",
    "Example", "Remark", "Algorithm", "Notation", "Convention", "Axiom",
)

# Pattern: **Definition 4.3** or **Theorem 12.7a**
LABEL_RE = re.compile(
    r"\*\*(" + "|".join(LABEL_KINDS) + r")\s+(\d+)\.(\d+[a-z]?)\*\*"
)

# Pattern: ### Algorithm 6.1: or ### Example 8.2: (subsection headers)
HEADER_RE = re.compile(
    r"^###\s+(Algorithm|Example|Exercise)\s+(\d+)\.(\d+[a-z]?):",
    re.MULTILINE,
)

# Cross-reference pattern: any of the label kinds followed by N.M (outside bold)
# Matches both inline "see Definition 3.5" and parenthetical "(Theorem 4.12)"
XREF_RE = re.compile(
    r"(?<!\*\*)(" + "|".join(LABEL_KINDS) + r")s?\s+(\d+)\.(\d+[a-z]?)"
)


def chapter_number(filepath: str) -> int:
    return int(Path(filepath).stem.split("-")[0])


def extract_labels(text: str) -> list[tuple[str, int, str]]:
    """Return list of (kind, prefix, seq) for every **Kind N.M** found."""
    return [
        (kind, int(prefix), seq)
        for kind, prefix, seq in LABEL_RE.findall(text)
    ]


def extract_xrefs(text: str) -> list[tuple[str, int, str, int]]:
    """Return list of (kind, prefix, seq, line_num) for cross-references."""
    results = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for kind, prefix, seq in XREF_RE.findall(line):
            # Skip if this line is actually the definition itself
            if LABEL_RE.search(line):
                continue
            results.append((kind, int(prefix), seq, lineno))
    return results


def seq_int(seq: str) -> int:
    """Strip trailing letter suffix for numeric comparison: '12a' → 12."""
    return int(re.sub(r"[a-z]$", "", seq))


def analyse_chapter(filepath: str) -> dict:
    ch_num = chapter_number(filepath)
    text = Path(filepath).read_text(encoding="utf-8")
    labels = extract_labels(text)

    # Also extract ### subsection headers (Algorithm, Example, Exercise)
    header_labels = [
        (kind, int(prefix), seq)
        for kind, prefix, seq in HEADER_RE.findall(text)
    ]

    result: dict = {
        "ch": ch_num,
        "path": filepath,
        "prefix_mismatches": [],
        "duplicates": [],
        "gaps": [],
        "header_mismatches": [],
        "xrefs": extract_xrefs(text) if not QUICK_MODE else [],
    }

    # Check ### header prefixes
    for kind, prefix, seq in header_labels:
        if prefix != ch_num:
            result["header_mismatches"].append(f"{kind} {prefix}.{seq}")

    # Group by (prefix, kind) to detect duplicates and gaps per numbering stream
    by_prefix: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for kind, prefix, seq in labels:
        by_prefix[prefix].append((kind, seq))

    for prefix, items in by_prefix.items():
        # 1. Prefix mismatch
        if prefix != ch_num:
            result["prefix_mismatches"].append({
                "prefix": prefix,
                "count": len(items),
                "example": f"{items[0][0]} {prefix}.{items[0][1]}",
            })

        # 2. Duplicates — the same EXACT seq string (including suffix) used more than
        #    once, OR two bare numbers (no suffix) with the same value.
        #    "3.3" + "3.3a" is intentional (sub-item); "3.3" + "3.3" is a real dup.
        exact_seen: dict[str, list[str]] = defaultdict(list)
        for kind, seq in items:
            exact_seen[seq].append(f"{kind} {prefix}.{seq}")
        for seq_str, occurrences in sorted(exact_seen.items()):
            if len(occurrences) > 1:
                result["duplicates"].append({
                    "prefix": prefix,
                    "num": seq_int(seq_str),
                    "labels": occurrences,
                })

        # 3. Gaps — missing integers in the sequence
        nums = sorted({seq_int(seq) for _, seq in items})
        if nums:
            expected = set(range(nums[0], nums[-1] + 1))
            missing = sorted(expected - set(nums))
            if missing:
                result["gaps"].append({
                    "prefix": prefix,
                    "missing": missing,
                })

    return result


def build_global_index(analyses: list[dict]) -> dict[tuple[int, str, int], bool]:
    """Build a set of (prefix, kind, seq_int) for all existing labels."""
    index: dict[tuple[int, str, int], bool] = {}
    for a in analyses:
        filepath = a["path"]
        text = Path(filepath).read_text(encoding="utf-8")
        for kind, prefix, seq in extract_labels(text):
            index[(prefix, kind, seq_int(seq))] = True
            # Also index without kind for "see Definition 3.5" checks
            index[(prefix, "ANY", seq_int(seq))] = True
    return index


def main() -> int:
    files = sorted(glob.glob(str(DOCS_DIR / "[0-9]*.md")))
    if not files:
        print("ERROR: no chapter files found")
        sys.exit(1)

    print("=" * 70)
    print("Evenwicht Numbered Label Verification")
    print("=" * 70)
    print()

    analyses = [analyse_chapter(f) for f in files]

    # Build global label index for cross-reference resolution
    global_index = build_global_index(analyses) if not QUICK_MODE else {}

    errors: list[str] = []
    warnings: list[str] = []

    for a in analyses:
        ch = a["ch"]
        stem = Path(a["path"]).stem

        for pm in a["prefix_mismatches"]:
            errors.append(
                f"Ch {ch:02d} ({stem}): prefix mismatch — "
                f"{pm['count']} item(s) use prefix {pm['prefix']} "
                f"(expected {ch}). E.g. {pm['example']}"
            )

        for dup in a["duplicates"]:
            errors.append(
                f"Ch {ch:02d} ({stem}): duplicate number {dup['prefix']}.{dup['num']} "
                f"— {', '.join(dup['labels'])}"
            )

        if a["header_mismatches"]:
            examples = ", ".join(a["header_mismatches"][:3])
            errors.append(
                f"Ch {ch:02d} ({stem}): ### header prefix mismatch — "
                f"{len(a['header_mismatches'])} header(s) use wrong prefix. "
                f"E.g. {examples}"
            )

        for gap in a["gaps"]:
            missing_str = ", ".join(
                f"{gap['prefix']}.{n}" for n in gap["missing"]
            )
            warnings.append(
                f"Ch {ch:02d} ({stem}): sequence gap in prefix {gap['prefix']} "
                f"— missing {missing_str}"
            )

        if not QUICK_MODE:
            for kind, prefix, seq, lineno in a["xrefs"]:
                key_exact = (prefix, kind, seq_int(seq))
                key_any = (prefix, "ANY", seq_int(seq))
                if key_exact not in global_index and key_any not in global_index:
                    warnings.append(
                        f"Ch {ch:02d} ({stem}:{lineno}): unresolved cross-reference "
                        f"— {kind} {prefix}.{seq} not found in any chapter"
                    )

    # ── Report ─────────────────────────────────────
    print(f"Chapters analysed: {len(files)}")
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print()

    if errors:
        print("--- ERRORS ---")
        for e in errors:
            print(f"  {e}")
        print()

    if warnings:
        print("--- WARNINGS ---")
        for w in warnings:
            print(f"  {w}")
        print()

    if not errors and not warnings:
        print("All numbering checks passed.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
