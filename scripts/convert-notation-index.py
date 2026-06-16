#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Convert the print-format notation index (markdown tables) into a
web-friendly version with clickable chapter links and list-based layout.

Usage:
    python3 scripts/convert-notation-index.py
    python3 scripts/convert-notation-index.py --dry-run
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "docs" / "reference" / "notation-index.md"

# Chapter number → slug
CHAPTERS: dict[int, str] = {
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


def chapter_num_link(num: int) -> str:
    """Return a linked chapter number like [4](../domains/04-...)."""
    slug = CHAPTERS.get(num)
    if slug is None:
        return str(num)
    return f"[{num}](../domains/{slug}.md)"


def parse_chapters(chapters_str: str) -> list[int]:
    """Parse a string like '16, 24, 32, 38, 48' into a list of ints."""
    nums = []
    for part in chapters_str.split(","):
        part = part.strip()
        if part.isdigit():
            nums.append(int(part))
    return nums


def parse_table_row(line: str) -> tuple[str, str, list[int]] | None:
    """Parse a table row '| Symbol | Meaning | Chapters |' into components.

    Returns (symbol, meaning, chapter_numbers) or None if not a data row.
    """
    line = line.strip()
    if not line.startswith("|"):
        return None

    # Split on pipes and strip
    parts = [p.strip() for p in line.split("|")]
    # Leading/trailing empty strings from split
    parts = [p for p in parts if p != ""]

    if len(parts) < 3:
        return None

    symbol = parts[0]
    meaning = parts[1]
    chapters_str = parts[2]

    # Skip header rows and separator rows
    if symbol.startswith(":") or symbol.startswith("-"):
        return None
    if meaning.startswith(":") or meaning.startswith("-"):
        return None
    if chapters_str.startswith(":") or chapters_str.startswith("-"):
        return None
    if symbol == "Symbol":
        return None

    nums = parse_chapters(chapters_str)
    if not nums:
        return None

    return symbol, meaning, nums


def convert_index(text: str) -> str:
    """Convert the full notation index from table format to list format."""
    lines = text.split("\n")
    output: list[str] = []

    # Header
    output.append(
        "<!-- Copyright (c) 2025-2026 Bob Jansen "
        "<bobjansen@pm.me> -->"
    )
    output.append("<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->")
    output.append(
        "<!-- See LICENSE for full terms. Commercial licensing available. -->"
    )
    output.append("")
    output.append("# Notation Index")
    output.append("")
    output.append('<div class="notation-index" markdown>')
    output.append("")

    in_table = False
    skip_intro = True

    for line in lines:
        stripped = line.strip()

        # Skip copyright, title, and intro paragraph
        if stripped.startswith("<!--"):
            continue
        if stripped == "# Notation Index":
            continue
        if skip_intro and not stripped.startswith("##"):
            # Skip any intro text before the first section heading
            if stripped and not stripped.startswith("|"):
                continue

        # Section heading (## Greek Letters, ## Operators, etc.)
        m = re.match(r"^## (.+)$", stripped)
        if m:
            skip_intro = False
            section_title = m.group(1)
            output.append(f"## {section_title}")
            output.append("")
            in_table = False
            continue

        # Table separator or header row — skip
        if stripped.startswith("|") and re.match(r"^\|[\s:|-]+\|$", stripped):
            in_table = True
            continue

        # Table data row
        if stripped.startswith("|"):
            parsed = parse_table_row(stripped)
            if parsed is None:
                in_table = True
                continue

            symbol, meaning, nums = parsed
            links = ", ".join(chapter_num_link(n) for n in nums)
            output.append(f"- **{symbol}**: {meaning} — {links}")
            in_table = True
            continue

        # Empty line between sections
        if not stripped and not in_table:
            continue

        # End of table block
        if not stripped and in_table:
            in_table = False
            output.append("")
            continue

    output.append("")
    output.append("</div>")
    output.append("")

    # Clean up multiple blank lines
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(output))
    return result


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    text = INDEX_FILE.read_text(encoding="utf-8")
    new_text = convert_index(text)

    if dry_run:
        print(new_text[:5000])
        print(f"\n... ({len(new_text)} chars total)")
    else:
        INDEX_FILE.write_text(new_text, encoding="utf-8")
        print(f"Converted {INDEX_FILE.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
