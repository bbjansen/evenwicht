#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Convert the print-format subject index into a web-friendly version
with clickable chapter links and proper layout.

Usage:
    python3 scripts/convert-subject-index.py
    python3 scripts/convert-subject-index.py --dry-run
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "docs" / "reference" / "subject-index.md"

# Chapter number → (slug, short title)
CHAPTERS: dict[int, tuple[str, str]] = {
    1: ("01-expressions", "Expressions"),
    2: ("02-special-functions", "Special Functions"),
    3: ("03-limits-continuity", "Limits"),
    4: ("04-differential-calculus", "Differentiation"),
    5: ("05-integral-calculus", "Integration"),
    6: ("06-series-approximation", "Series"),
    7: ("07-multivariate-calculus", "Multivariate"),
    8: ("08-vectors", "Vectors"),
    9: ("09-matrices", "Matrices"),
    10: ("10-eigenvalues", "Eigenvalues"),
    11: ("11-unconstrained-optimization", "Unconstrained Opt."),
    12: ("12-constrained-optimization", "Constrained Opt."),
    13: ("13-probability-theory", "Probability"),
    14: ("14-distributions", "Distributions"),
    15: ("15-descriptive-statistics", "Descriptive Stats"),
    16: ("16-statistical-inference", "Inference"),
    17: ("17-regression", "Regression"),
    18: ("18-difference-equations", "Difference Eq."),
    19: ("19-odes", "ODEs"),
    20: ("20-discrete-operators", "Discrete Ops"),
    21: ("21-time-series", "Time Series"),
    22: ("22-transforms", "Transforms"),
    23: ("23-operator-algebra", "Operator Algebra"),
    24: ("24-fractional-calculus", "Fractional Calc."),
    25: ("25-financial-mathematics", "Finance"),
    26: ("26-machine-learning", "Machine Learning"),
    27: ("27-quantitative-trading", "Trading"),
    28: ("28-information-theory", "Info Theory"),
    29: ("29-control-systems", "Control Systems"),
    30: ("30-epidemiology", "Epidemiology"),
    31: ("31-network-analysis", "Networks"),
    32: ("32-energy-systems", "Energy"),
    33: ("33-equilibrium", "Equilibrium"),
    34: ("34-chemical-kinetics", "Chem. Kinetics"),
    35: ("35-pharmacokinetics", "Pharmacokinetics"),
    36: ("36-game-theory", "Game Theory"),
    37: ("37-cryptography", "Cryptography"),
    38: ("38-climate-modeling", "Climate"),
    39: ("39-mechanics-waves", "Mechanics"),
    40: ("40-signal-processing", "Signal Proc."),
    41: ("41-orbital-mechanics", "Orbital Mech."),
    42: ("42-robotics", "Robotics"),
    43: ("43-fluid-dynamics", "Fluids"),
    44: ("44-circuits", "Circuits"),
    45: ("45-geology-seismology", "Geology"),
    46: ("46-cosmology", "Cosmology"),
    47: ("47-optics-acoustics", "Optics"),
    48: ("48-genetics", "Genetics"),
}


def chapter_link(num: int) -> str:
    """Return a markdown link to a chapter."""
    if num not in CHAPTERS:
        return str(num)
    slug, short = CHAPTERS[num]
    return f"[Ch.{num}](../domains/{slug}.md)"


def chapter_num_link(num: int) -> str:
    """Return a linked chapter number like [4](../domains/04-...)."""
    if num not in CHAPTERS:
        return str(num)
    slug, _short = CHAPTERS[num]
    return f"[{num}](../domains/{slug}.md)"


def parse_entry(line: str) -> tuple[str, list[int]] | None:
    """Parse 'Term, 4' or 'Term, 4, 7' into (term, [4, 7])."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("<!--"):
        return None

    # Match: term text, then one or more chapter numbers at the end
    # Pattern: everything up to the last comma-separated numbers
    m = re.match(r"^(.+?),\s*([\d]+(?:\s*,\s*\d+)*)$", line)
    if not m:
        return None

    term = m.group(1).strip().rstrip(",")
    nums_str = m.group(2)
    nums = [int(n.strip()) for n in nums_str.split(",") if n.strip().isdigit()]

    if not nums:
        return None

    return term, nums


def convert_index(text: str) -> str:
    """Convert the full index from print format to web format."""
    lines = text.split("\n")
    output: list[str] = []

    # Header
    output.append("<!-- Copyright (c) 2025-2026 Bob Jansen "
                   "<bobjansen@pm.me> -->")
    output.append("<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->")
    output.append("<!-- See LICENSE for full terms. Commercial licensing "
                   "available. -->")
    output.append("")
    output.append("# Subject Index")
    output.append("")
    output.append('<div class="subject-index" markdown>')
    output.append("")

    current_letter = None

    for line in lines:
        stripped = line.strip()

        # Skip old header and copyright
        if stripped.startswith("# Subject Index"):
            continue
        if stripped.startswith("<!--"):
            continue

        # Letter heading
        m = re.match(r"^## ([A-Z#])\s*$", stripped)
        if m:
            current_letter = m.group(1)
            if current_letter == "#":
                continue
            output.append(f"## {current_letter}")
            output.append("")
            continue

        # Skip the misc # section
        if current_letter == "#":
            continue

        # Empty line
        if not stripped:
            continue

        # Parse entry
        parsed = parse_entry(stripped)
        if parsed is None:
            continue

        term, nums = parsed
        links = ", ".join(chapter_num_link(n) for n in nums)
        output.append(f"- **{term}**: {links}")

    output.append("")
    output.append("</div>")
    output.append("")

    return "\n".join(output)


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    text = INDEX_FILE.read_text(encoding="utf-8")
    new_text = convert_index(text)

    if dry_run:
        print(new_text[:3000])
        print(f"\n... ({len(new_text)} chars total)")
    else:
        INDEX_FILE.write_text(new_text, encoding="utf-8")
        print(f"Converted {INDEX_FILE.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
