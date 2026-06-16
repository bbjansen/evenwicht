#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Convert chapter references to clickable markdown links.

Finds patterns like 'Chapter N', 'Ch N', 'Ch. N' in prose text and
converts them to '[Chapter N](NN-slug.md)' links.  Also handles
multi-chapter references like 'Chapters 3-6', 'Chapters 4 and 5',
and 'Chapters 14, 24, and 6'.

Skips references that are:
- Already inside markdown links [...](...)
- Inside fenced code blocks or mermaid blocks
- Inside HTML comments
- In bibliography lines (starting with [N])

Usage:
    python3 scripts/linkify-chapters.py                    # dry run (show counts)
    python3 scripts/linkify-chapters.py --apply            # apply changes
    python3 scripts/linkify-chapters.py --apply FILE ...   # apply to specific files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

CHAPTER_SLUGS: dict[int, str] = {
    1: "01-expressions",
    2: "02-special-functions",
    3: "03-limits-continuity",
    4: "04-differential-calculus",
    5: "05-integral-calculus",
    6: "06-series-approximation",
    7: "07-multivariate-calculus",
    8: "08-vectors",
    9: "09-matrices",
    10: "10-eigenvalues",
    11: "11-unconstrained-optimization",
    12: "12-constrained-optimization",
    13: "13-probability-theory",
    14: "14-distributions",
    15: "15-descriptive-statistics",
    16: "16-statistical-inference",
    17: "17-regression",
    18: "18-difference-equations",
    19: "19-odes",
    20: "20-discrete-operators",
    21: "21-time-series",
    22: "22-transforms",
    23: "23-operator-algebra",
    24: "24-fractional-calculus",
    25: "25-financial-mathematics",
    26: "26-machine-learning",
    27: "27-quantitative-trading",
    28: "28-information-theory",
    29: "29-control-systems",
    30: "30-epidemiology",
    31: "31-network-analysis",
    32: "32-energy-systems",
    33: "33-equilibrium",
    34: "34-chemical-kinetics",
    35: "35-pharmacokinetics",
    36: "36-game-theory",
    37: "37-cryptography",
    38: "38-climate-modeling",
    39: "39-mechanics-waves",
    40: "40-signal-processing",
    41: "41-orbital-mechanics",
    42: "42-robotics",
    43: "43-fluid-dynamics",
    44: "44-circuits",
    45: "45-geology-seismology",
    46: "46-cosmology",
    47: "47-optics-acoustics",
    48: "48-genetics",
}

# Markdown link pattern: [text](url)
_LINK_RE = re.compile(r"\[(?:[^\[\]]|\[[^\]]*\])*\]\([^)]*\)")


def _chapter_link(num: int, label: str) -> str:
    """Build a markdown link for a chapter reference."""
    slug = CHAPTER_SLUGS.get(num)
    if slug is None:
        return label
    return f"[{label}]({slug}.md)"


def _is_bibliography_line(line: str) -> bool:
    """Check if a line is a bibliography entry like '[1] Author...'."""
    return bool(re.match(r"^\s*\[\d+\]", line))


def _is_heading_line(line: str) -> bool:
    """Check if a line is a markdown heading containing the chapter's own title."""
    return bool(re.match(r"^#{1,6}\s+Chapter\s+\d", line))


def _apply_to_unlinked(line: str, transform) -> tuple[str, int]:
    """Apply a transform function to parts of a line not inside markdown links.

    The transform function takes a string and returns (new_string, count).
    """
    parts: list[str] = []
    total = 0
    last_end = 0

    for m in _LINK_RE.finditer(line):
        before = line[last_end:m.start()]
        new_before, c = transform(before)
        parts.append(new_before)
        total += c
        parts.append(m.group(0))
        last_end = m.end()

    after = line[last_end:]
    new_after, c = transform(after)
    parts.append(new_after)
    total += c

    return "".join(parts), total


# ---------------------------------------------------------------------------
# Phase 1: "Chapters N-M" ranges
# ---------------------------------------------------------------------------
_CHAPTERS_RANGE = re.compile(
    r"Chapters\s+(\d{1,2})"
    r"[\u2013\u2014\-]"
    r"(\d{1,2})"
)


def _phase_range(text: str) -> tuple[str, int]:
    """Replace 'Chapters N-M' with individual linked chapters."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        start, end = int(m.group(1)), int(m.group(2))
        if start < 1 or start > 48 or end < 1 or end > 48:
            return m.group(0)
        valid = [n for n in range(start, end + 1) if n in CHAPTER_SLUGS]
        if not valid:
            return m.group(0)
        links = [_chapter_link(n, f"Chapter {n}") for n in valid]
        count += len(links)
        return ", ".join(links)

    result = _CHAPTERS_RANGE.sub(repl, text)
    return result, count


# ---------------------------------------------------------------------------
# Phase 2: "Chapters N and M"
# ---------------------------------------------------------------------------
_CHAPTERS_AND = re.compile(
    r"Chapters\s+(\d{1,2})\s+and\s+(\d{1,2})"
)


def _phase_and(text: str) -> tuple[str, int]:
    """Replace 'Chapters N and M' with two linked chapters."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        a, b = int(m.group(1)), int(m.group(2))
        if not (1 <= a <= 48 and 1 <= b <= 48):
            return m.group(0)
        if a not in CHAPTER_SLUGS or b not in CHAPTER_SLUGS:
            return m.group(0)
        count += 2
        return f"{_chapter_link(a, f'Chapter {a}')} and {_chapter_link(b, f'Chapter {b}')}"

    result = _CHAPTERS_AND.sub(repl, text)
    return result, count


# ---------------------------------------------------------------------------
# Phase 3: "Chapters N, M, ..., and P" with optional parenthetical descriptions
# ---------------------------------------------------------------------------
_CHAPTERS_LIST = re.compile(
    r"Chapters\s+"
    r"(\d{1,2}(?:\s*\([^)]*\))?)"                          # first: N (desc)?
    r"((?:\s*,\s*\d{1,2}(?:\s*\([^)]*\))?)+)"              # more: , M (desc)?
    r"(\s*,?\s*and\s+\d{1,2}(?:\s*\([^)]*\))?)?"           # optional: and P (desc)?
)


def _phase_list(text: str) -> tuple[str, int]:
    """Replace 'Chapters N, M, ..., and P' with linked chapters."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        full = m.group(0)
        # Extract all (number, description) pairs
        pair_pat = re.compile(r"(\d{1,2})(\s*\([^)]*\))?")
        pairs = pair_pat.findall(full)
        if not pairs:
            return full

        nums = [int(p[0]) for p in pairs]
        descs = [p[1] for p in pairs]

        if not all(1 <= n <= 48 and n in CHAPTER_SLUGS for n in nums):
            return full

        parts = []
        for num, desc in zip(nums, descs):
            parts.append(_chapter_link(num, f"Chapter {num}") + desc)
        count += len(parts)

        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            sep = " and " if " and " in full else ", "
            return sep.join(parts)
        else:
            if ", and " in full or ",and " in full:
                return ", ".join(parts[:-1]) + ", and " + parts[-1]
            elif " and " in full:
                return ", ".join(parts[:-1]) + " and " + parts[-1]
            else:
                return ", ".join(parts)

    result = _CHAPTERS_LIST.sub(repl, text)
    return result, count


# ---------------------------------------------------------------------------
# Phase 4: Individual "Chapter N" / "Ch N" / "Ch. N"
# ---------------------------------------------------------------------------
_SINGLE_REF = re.compile(
    r"((?:Chapter|Ch\.?)\s+(\d{1,2}))"
)


def _phase_single(text: str) -> tuple[str, int]:
    """Replace individual Chapter/Ch references with links."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        num = int(m.group(2))
        if num < 1 or num > 48 or num not in CHAPTER_SLUGS:
            return m.group(1)
        count += 1
        return _chapter_link(num, f"Chapter {num}")

    result = _SINGLE_REF.sub(repl, text)
    return result, count


def linkify_line(line: str) -> tuple[str, int]:
    """Linkify chapter references in a single line.

    Runs four phases, each protecting existing markdown links,
    so that links created by earlier phases are not re-processed.

    Returns (new_line, count_of_replacements).
    """
    if _is_bibliography_line(line) or _is_heading_line(line):
        return line, 0

    total = 0

    for phase in (_phase_range, _phase_and, _phase_list, _phase_single):
        line, c = _apply_to_unlinked(line, phase)
        total += c

    return line, total


def linkify_text(text: str) -> tuple[str, int]:
    """Linkify chapter references in markdown text.

    Skips fenced code blocks, mermaid blocks, and HTML comments.
    Returns (new_text, count_of_replacements).
    """
    lines = text.split("\n")
    result: list[str] = []
    total_count = 0
    in_fenced_block = False
    in_html_comment = False

    for line in lines:
        # Track HTML comment blocks (multi-line)
        if not in_fenced_block:
            if in_html_comment:
                if "-->" in line:
                    in_html_comment = False
                result.append(line)
                continue
            if "<!--" in line and "-->" not in line:
                in_html_comment = True
                result.append(line)
                continue

        # Track fenced code blocks (``` or ~~~)
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fenced_block = not in_fenced_block
            result.append(line)
            continue

        if in_fenced_block or in_html_comment:
            result.append(line)
            continue

        new_line, c = linkify_line(line)
        result.append(new_line)
        total_count += c

    return "\n".join(result), total_count


def process_file(filepath: Path, apply: bool) -> int:
    """Process a single file. Returns number of references linked."""
    text = filepath.read_text(encoding="utf-8")
    new_text, count = linkify_text(text)

    if count == 0:
        return 0

    rel = filepath.relative_to(PROJECT_ROOT)
    if apply:
        filepath.write_text(new_text, encoding="utf-8")
        print(f"  {rel}: linked {count} reference(s)")
    else:
        print(f"  {rel}: would link {count} reference(s)")

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
    print(f"\n{mode}: {total} reference(s) across {len(files)} file(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
