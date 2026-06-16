#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Wrap proof blocks in collapsible admonitions.

Finds blocks starting with '*Proof.*' and ending with '$\\square$',
wraps them in '??? note "Proof"' collapsible blocks.

Usage:
    python3 scripts/wrap-proofs.py                    # dry run (show changes)
    python3 scripts/wrap-proofs.py --apply            # apply changes
    python3 scripts/wrap-proofs.py --apply FILE ...   # apply to specific files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"


def wrap_proofs(text: str) -> tuple[str, int]:
    """Wrap *Proof.* ... $\\square$ blocks in collapsible admonitions.

    Returns (new_text, count_of_wraps).
    """
    lines = text.split("\n")
    result: list[str] = []
    count = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect proof start: line begins with *Proof...* variants
        if (line.startswith("*Proof.*")
            or line.startswith("*Proof*")
            or line.startswith("*Proof sketch.*")
            or line.startswith("*Proof sketch*")
            or line.startswith("*Proof sketch (")
            or line.startswith("*Proof that ")
            or line.startswith("*Proof of ")):
            # Collect all lines of this proof until we find $\square$
            proof_lines: list[str] = [line]
            found_end = False

            # Check if the proof ends on the same line it starts
            if "\\square$" in line or "□" in line:
                found_end = True
                j = i
            else:
                j = i + 1
                while j < len(lines):
                    proof_lines.append(lines[j])
                    if "\\square$" in lines[j] or "□" in lines[j]:
                        found_end = True
                        break
                    j += 1

            if found_end:
                # Check if previous line is blank (needed for admonition)
                # Remove trailing blank lines before the proof if they exist
                # (we'll add our own spacing)

                # Build the collapsible block
                result.append('??? note "Proof"')
                result.append("")

                for pl in proof_lines:
                    # Indent each proof line by 4 spaces
                    if pl.strip() == "":
                        result.append("")
                    else:
                        result.append("    " + pl)

                count += 1
                i = j + 1
                continue
            else:
                # No $\square$ found — leave as-is
                result.append(line)
                i += 1
                continue
        else:
            result.append(line)
            i += 1

    return "\n".join(result), count


def process_file(filepath: Path, apply: bool) -> int:
    """Process a single file. Returns number of proofs wrapped."""
    text = filepath.read_text(encoding="utf-8")
    new_text, count = wrap_proofs(text)

    if count == 0:
        return 0

    rel = filepath.relative_to(PROJECT_ROOT)
    if apply:
        filepath.write_text(new_text, encoding="utf-8")
        print(f"  {rel}: wrapped {count} proof(s)")
    else:
        print(f"  {rel}: would wrap {count} proof(s)")

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
    print(f"\n{mode}: {total} proof(s) across {len(files)} file(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
