#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Verify that all Mermaid diagram blocks have the correct type keyword.

Detects mismatches between the declared diagram type and the actual
content (e.g., a quadrantChart tagged as timeline).

Usage:
    python3 scripts/verify-diagrams-types.py

Exit code 0 if no issues, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"


def detect_type(text: str) -> str | None:
    """Detect diagram type from content."""
    if "quadrant-1" in text or "quadrant-2" in text:
        return "quadrantChart"

    has_xq = bool(re.search(r'x-axis\s+"', text))
    has_yq = bool(re.search(r'y-axis\s+"', text))
    has_line = bool(re.search(r"^\s*line\s", text, re.MULTILINE))
    has_bar = bool(re.search(r"^\s*bar\s", text, re.MULTILINE))
    if (has_xq or has_yq) and (has_line or has_bar):
        return "xychart-beta"
    if re.search(r"x-axis\s+\S.*-->", text):
        return "quadrantChart"

    if re.search(r"^\s*root\(\(", text, re.MULTILINE):
        return "mindmap"
    if re.search(r"^\s*\d{4}\s*:", text, re.MULTILINE):
        return "timeline"
    if re.search(r'^\s*state\s+"', text, re.MULTILINE):
        return "stateDiagram-v2"
    if re.search(r"^\s*class\s+\w+\s*\{", text, re.MULTILINE):
        return "classDiagram"
    if "pie" in text.split("\n")[0] if text.split("\n") else "":
        return "pie"

    return None


def main() -> int:
    issues = 0

    for f in sorted(DOCS_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(PROJECT_ROOT)

        for i, m in enumerate(
            re.finditer(r"```mermaid\n(.*?)```", text, re.DOTALL)
        ):
            content = m.group(1)
            lines = [
                l.strip()
                for l in content.split("\n")
                if l.strip()
                and not l.strip().startswith("%%{init")
                and l.strip() != "---"
                and not l.strip().startswith("title:")
                and not l.strip().startswith("config:")
                and not l.strip().startswith("xyChart:")
                and not l.strip().startswith("width:")
                and not l.strip().startswith("height:")
                and not l.strip().startswith("backgroundColor:")
            ]
            if not lines:
                print(f"  {rel} block {i}: EMPTY")
                issues += 1
                continue

            current = lines[0]
            detected = detect_type("\n".join(lines))

            if detected and not current.startswith(detected):
                print(
                    f"  {rel} block {i}: tagged as '{current[:30]}' "
                    f"but content is {detected}"
                )
                issues += 1

    if issues == 0:
        print("All diagram types are correct.")
    else:
        print(f"\n{issues} issue(s) found.")

    return 0 if issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
