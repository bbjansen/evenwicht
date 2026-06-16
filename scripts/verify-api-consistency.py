#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify API documentation consistency across Evenwicht API docs.

Checks:
  1. Each API doc contains all required H3 sections.
  2. Reports any non-standard H3 headings.
  3. Counts TypeScript code blocks per doc — flags any with 0.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_DIR = PROJECT_ROOT / "docs" / "api"

REQUIRED_SECTIONS = {
    "Module Structure",
    "Data Representation",
    "API Preview",
    "Error Handling",
    "Implementation Context",
    "Dependencies",
    "Usage Examples",
    "What Is Implemented vs. Documented Only",
    "Connections",
}

H3_RE = re.compile(r"^### (.+)$", re.MULTILINE)
TS_CODE_BLOCK_RE = re.compile(r"^```typescript\b", re.MULTILINE)


def get_api_files() -> list[Path]:
    """Return sorted list of API markdown files matching [0-9]*.md."""
    return sorted(API_DIR.glob("[0-9]*.md"))


def main() -> int:
    files = get_api_files()
    if not files:
        print(f"ERROR: No API files found in {API_DIR}")
        return 1

    issues: list[str] = []
    doc_data: list[dict] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        headings = [m.strip() for m in H3_RE.findall(text)]
        ts_count = len(TS_CODE_BLOCK_RE.findall(text))
        heading_set = set(headings)

        missing = REQUIRED_SECTIONS - heading_set
        extra = heading_set - REQUIRED_SECTIONS

        doc_data.append(
            {
                "file": path.name,
                "headings": headings,
                "missing": sorted(missing),
                "extra": sorted(extra),
                "ts_blocks": ts_count,
            }
        )

    # Print section presence table
    print("=" * 78)
    print("API DOC CONSISTENCY — Evenwicht API Reference")
    print("=" * 78)
    print()

    # Section coverage matrix
    print(f"{'Section':<46} {'Present':>7} {'Missing':>7}")
    print("-" * 62)
    for section in sorted(REQUIRED_SECTIONS):
        present = sum(
            1 for d in doc_data if section in set(d["headings"])
        )
        missing = len(doc_data) - present
        marker = " ***" if missing > 0 else ""
        print(f"  {section:<44} {present:>7} {missing:>7}{marker}")
    print()

    # Per-doc details
    print("=" * 78)
    print("PER-DOCUMENT DETAILS")
    print("=" * 78)
    print()
    print(
        f"{'Document':<36} {'H3s':>5} {'TS blocks':>10} {'Missing':>8} "
        f"{'Extra':>6}"
    )
    print("-" * 78)

    for d in doc_data:
        print(
            f"  {d['file']:<34} {len(d['headings']):>5} "
            f"{d['ts_blocks']:>10} {len(d['missing']):>8} "
            f"{len(d['extra']):>6}"
        )

    # Missing sections detail
    docs_with_missing = [d for d in doc_data if d["missing"]]
    if docs_with_missing:
        print()
        print("=" * 78)
        print(f"MISSING REQUIRED SECTIONS ({len(docs_with_missing)} docs)")
        print("=" * 78)
        for d in docs_with_missing:
            print(f"\n  {d['file']}:")
            for section in d["missing"]:
                issues.append(f"{d['file']}: missing '{section}'")
                print(f"    - {section}")

    # Non-standard headings detail
    docs_with_extra = [d for d in doc_data if d["extra"]]
    if docs_with_extra:
        print()
        print("=" * 78)
        print(f"NON-STANDARD H3 HEADINGS ({len(docs_with_extra)} docs)")
        print("=" * 78)
        for d in docs_with_extra:
            print(f"\n  {d['file']}:")
            for heading in d["extra"]:
                print(f"    - {heading}")

    # TypeScript code block check
    docs_no_ts = [d for d in doc_data if d["ts_blocks"] == 0]
    if docs_no_ts:
        print()
        print("=" * 78)
        print(f"DOCS WITH 0 TYPESCRIPT CODE BLOCKS ({len(docs_no_ts)})")
        print("=" * 78)
        for d in docs_no_ts:
            issues.append(f"{d['file']}: 0 TypeScript code blocks")
            print(f"  - {d['file']}")

    # Summary
    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Total API docs: {len(doc_data)}")
    print(f"  Docs with all required sections: "
          f"{len(doc_data) - len(docs_with_missing)}/{len(doc_data)}")
    print(f"  Docs with non-standard headings: {len(docs_with_extra)}")
    print(f"  Docs with TypeScript code blocks: "
          f"{len(doc_data) - len(docs_no_ts)}/{len(doc_data)}")
    print(f"  Total issues: {len(issues)}")
    print()

    if issues:
        return 1
    print("All API docs pass consistency checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
