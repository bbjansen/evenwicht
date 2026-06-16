#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Split Implementation Notes from domain chapters into separate API docs.

For each chapter:
1. Extract the Implementation Notes section
2. Keep "What Is Implemented vs. Documented Only" in the domain file
3. Move everything else to docs/api/XX-name.md
4. Replace the extracted content with a brief paragraph + cross-reference

Usage: python3 scripts/split-api-docs.py
"""

import glob
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = PROJECT_ROOT / "docs" / "domains"
API_DIR = PROJECT_ROOT / "docs" / "api"

# H3 headings that should STAY in the domain file (not moved to API)
KEEP_IN_DOMAIN = {
    "What Is Implemented vs. Documented Only",
}

# H3 headings to move to API docs
MOVE_TO_API = {
    "Module Structure", "Data Representation", "API Preview", "API Signatures",
    "API", "API Patterns", "Error Handling", "Constructor Functions",
    "Evaluation", "String Conversion", "Browser vs Node", "Scope",
    "Module Dependencies", "The Operator View",
}


def extract_chapter_title(content: str) -> str:
    """Get the chapter title from the H1 heading."""
    match = re.search(r"^# (?:Chapter \d+: )?(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else "Unknown"


def split_implementation_notes(content: str) -> tuple[str, str, str]:
    """Split content into: before impl notes, kept impl notes, moved API content."""

    # Find Implementation Notes section
    impl_start = re.search(
        r"^(## (?:\d+\.\s*)?Implementation Notes)\s*$", content, re.MULTILINE
    )
    if not impl_start:
        return content, "", ""

    # Find the next H2 section after Implementation Notes
    rest = content[impl_start.end():]
    next_h2 = re.search(r"^## ", rest, re.MULTILINE)
    if next_h2:
        impl_section = rest[:next_h2.start()]
        after_impl = rest[next_h2.start():]
    else:
        impl_section = rest
        after_impl = ""

    before_impl = content[:impl_start.start()]
    impl_heading = impl_start.group(1)

    # Split impl_section into H3 blocks
    blocks = []
    current_heading = None
    current_lines = []

    # Content before any H3 is "intro prose"
    intro_lines = []

    for line in impl_section.split("\n"):
        h3_match = re.match(r"^### (.+)$", line)
        if h3_match:
            if current_heading:
                blocks.append((current_heading, "\n".join(current_lines)))
            elif current_lines:
                intro_lines = current_lines[:]
            current_heading = h3_match.group(1).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_heading:
        blocks.append((current_heading, "\n".join(current_lines)))
    elif current_lines and not intro_lines:
        intro_lines = current_lines

    # Separate into keep vs move
    keep_blocks = []
    move_blocks = []

    for heading, block_content in blocks:
        # Check if heading matches any pattern to keep
        keep = False
        for pattern in KEEP_IN_DOMAIN:
            if pattern.lower() in heading.lower():
                keep = True
                break

        if keep:
            keep_blocks.append((heading, block_content))
        else:
            move_blocks.append((heading, block_content))

    # Build kept implementation notes
    kept = f"\n{impl_heading}\n\n"
    if intro_lines:
        kept += "\n".join(intro_lines).strip() + "\n\n"

    for heading, block_content in keep_blocks:
        kept += block_content.strip() + "\n\n"

    # Build moved API content
    moved = ""
    if move_blocks:
        for heading, block_content in move_blocks:
            moved += block_content.strip() + "\n\n"

    # Reconstruct domain content
    domain_content = before_impl.rstrip() + "\n\n" + kept.rstrip() + "\n\n" + after_impl.lstrip()

    return domain_content, kept, moved


def main():
    API_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(str(DOMAINS_DIR / "[0-9]*.md")))
    total_moved = 0
    total_api_files = 0

    for filepath in files:
        path = Path(filepath)
        basename = path.stem  # e.g., "01-expressions"
        content = path.read_text(encoding="utf-8")

        chapter_title = extract_chapter_title(content)
        domain_content, kept, api_content = split_implementation_notes(content)

        if not api_content.strip():
            print(f"  {basename}: no API content to extract")
            continue

        # Write API doc
        api_lines = api_content.count("\n")
        api_doc = f"# {chapter_title} — API Reference\n\n"
        api_doc += f"This is the API reference for the TypeScript implementation of {chapter_title}. "
        api_doc += f"For the mathematical theory, see the corresponding chapter in the main text.\n\n"
        api_doc += api_content

        api_path = API_DIR / f"{basename}.md"
        api_path.write_text(api_doc, encoding="utf-8")

        # Add cross-reference to domain file's Implementation Notes
        ref_line = f"\nFor the full TypeScript API reference — module structure, type signatures, and error handling — see the [API Reference](../api/{basename}.md).\n"

        # Insert cross-reference after the Implementation Notes heading
        domain_content = re.sub(
            r"(## (?:\d+\.\s*)?Implementation Notes\n)",
            r"\1" + ref_line + "\n",
            domain_content,
            count=1,
        )

        # Write updated domain file
        path.write_text(domain_content, encoding="utf-8")

        total_moved += api_lines
        total_api_files += 1
        print(f"  {basename}: extracted {api_lines} lines to api/")

    print(f"\nDone: {total_api_files} API docs created, {total_moved} total lines moved")


if __name__ == "__main__":
    main()
