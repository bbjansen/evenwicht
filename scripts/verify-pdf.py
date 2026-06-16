#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify the generated PDF for rendering errors.

Extracts text from each page and scans for:
  1. Raw markdown that wasn't rendered (**, ***, ???, ```)
  2. Raw LaTeX commands visible as text (\\frac, \\text, \\begin)
  3. Unrendered math delimiters ($...$, $$...$$)
  4. Unrendered markdown links [text](url)
  5. Mermaid diagram source code leaked into text
  6. Raw HTML comments
  7. Unrendered admonitions (??? note, !!! warning)

Usage:
  pip install pymupdf
  python3 scripts/verify-pdf.py [path/to/pdf]

Defaults to book/evenwicht-latest.pdf or dist/evenwicht.pdf.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF required. pip install pymupdf")
    sys.exit(2)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Patterns that indicate rendering failures
PATTERNS = [
    # Raw markdown
    (r"\*\*\w+.*?\*\*", "Raw bold markdown (**text**)"),
    (r"^\?\?\?[\s+]*note", "Unrendered admonition (??? note)"),
    (r"^```(?:mermaid|python|typescript|bash)", "Raw code fence (```)"),
    (r"^!\[.*?\]\(.*?\.png\)", "Unrendered image reference"),

    # Raw LaTeX visible as text
    (r"\\frac\{", "Raw \\frac command"),
    (r"\\text\{", "Raw \\text command"),
    (r"\\begin\{(?:aligned|equation|cases)", "Raw \\begin command"),
    (r"\\end\{(?:aligned|equation|cases)", "Raw \\end command"),
    (r"\\(?:alpha|beta|gamma|sigma|lambda|mu|nu|pi)\b", "Raw Greek letter command"),
    (r"\\\$", "Raw escaped dollar sign"),

    # Unrendered math
    (r"(?<!\w)\$[^$\n`{]{3,80}\$(?!\w)", "Possible unrendered inline math"),
    (r"^\$\$", "Possible unrendered display math"),

    # Markdown links
    (r"\[(?:Chapter|Definition|Theorem|Algorithm)\s+\d+", "Possible unrendered markdown link"),

    # Mermaid source
    (r"^flowchart\s+(?:LR|TD|TB|RL|BT)", "Mermaid flowchart source"),
    (r"^graph\s+(?:LR|TD|TB)", "Mermaid graph source"),
    (r"^timeline\b", "Mermaid timeline source"),
    (r"^stateDiagram", "Mermaid stateDiagram source"),
    (r"^mindmap\b", "Mermaid mindmap source"),
    (r"^xychart-beta", "Mermaid xychart source"),
    (r"^sequenceDiagram", "Mermaid sequence source"),
    (r"-->(?:\|)", "Mermaid arrow syntax"),

    # HTML
    (r"<!--.*?-->", "Raw HTML comment"),
    (r"</?(?:div|span|br|img)\b", "Raw HTML tag"),
]

# Lines to skip (false positives from legitimate content)
SKIP_PATTERNS = [
    r"^\d+$",                    # Page numbers
    r"^v\d+\.\d+",              # Version string in footer
    r"^EVENWICHT$",             # Header
    r"^CHAPTER\s+\d+",         # Chapter header
    r"Contents$",              # TOC
    r"List of Figures$",       # LoF
    r"^\.\s*\.\s*\.\s*",       # TOC dots
]


def find_pdf(argv: list[str]) -> Path:
    if argv:
        p = Path(argv[0])
        if p.exists():
            return p
    for candidate in [
        PROJECT_ROOT / "book" / "evenwicht-latest.pdf",
        PROJECT_ROOT / "dist" / "evenwicht.pdf",
    ]:
        if candidate.exists():
            return candidate
    print("ERROR: No PDF found. Build first or pass path as argument.")
    sys.exit(1)


def main() -> int:
    pdf_path = find_pdf(sys.argv[1:])
    print(f"Scanning: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    print(f"Pages: {total_pages}")
    print()

    compiled = [(re.compile(p, re.MULTILINE), desc) for p, desc in PATTERNS]
    skip_compiled = [re.compile(p) for p in SKIP_PATTERNS]

    issues: list[tuple[int, str, str]] = []

    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()

        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Skip known false positives
            if any(sp.search(line) for sp in skip_compiled):
                continue

            for pattern, desc in compiled:
                if pattern.search(line):
                    # Extra filter: skip bold in TOC and headings
                    if "bold markdown" in desc:
                        # Only flag if it looks like raw markdown, not bold text
                        if line.startswith("**") and line.endswith("**"):
                            issues.append((page_num + 1, desc, line[:80]))
                    else:
                        issues.append((page_num + 1, desc, line[:80]))
                    break  # One issue per line

    doc.close()

    # Group by type
    by_type: dict[str, list[tuple[int, str]]] = {}
    for page, desc, fragment in issues:
        by_type.setdefault(desc, []).append((page, fragment))

    if not issues:
        print("No rendering errors found.")
        return 0

    print("=" * 78)
    print(f"FOUND {len(issues)} POTENTIAL ISSUES")
    print("=" * 78)

    for desc, occurrences in sorted(by_type.items(), key=lambda x: -len(x[1])):
        print(f"\n{desc} ({len(occurrences)} occurrences):")
        for page, fragment in occurrences[:5]:
            print(f"  p.{page}: {fragment}")
        if len(occurrences) > 5:
            print(f"  ... and {len(occurrences) - 5} more")

    print()
    print(f"Total: {len(issues)} issues across {len(by_type)} categories")
    return 1


if __name__ == "__main__":
    sys.exit(main())
