#!/usr/bin/env python3
"""Add search boost front matter to domain chapter files.

Boost tiers:
  - Chapters  1-12  (core theory):        boost 2.0
  - Chapters 13-24  (intermediate theory): boost 1.5
  - Chapters 25-48  (applications):        boost 1.0 (default, no front matter needed)

Usage:
  python scripts/add-search-boost.py              # dry-run (default)
  python scripts/add-search-boost.py --apply       # apply changes
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOMAINS_DIR = Path(__file__).resolve().parent.parent / "docs" / "domains"

BOOST_TIERS = [
    (range(1, 13), 2.0),    # core theory
    (range(13, 25), 1.5),   # intermediate theory
]

# Chapters 25-48 stay at the directory-level default (1.0) via .meta.yml,
# so no front matter is needed for them.

FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL | re.MULTILINE)
CHAPTER_NUM_PATTERN = re.compile(r"^(\d+)-")


def get_boost(chapter_num: int) -> float | None:
    """Return the boost value for a chapter number, or None if default."""
    for chapter_range, boost in BOOST_TIERS:
        if chapter_num in chapter_range:
            return boost
    return None


def build_front_matter(boost: float) -> str:
    """Build YAML front matter block with search boost."""
    # Use integer formatting when the value is a whole number
    boost_str = str(int(boost)) if boost == int(boost) else str(boost)
    return f"---\nsearch:\n  boost: {boost_str}\n---\n"


def process_file(path: Path, boost: float, dry_run: bool) -> bool:
    """Add or update search boost front matter in a markdown file.

    Returns True if the file was (or would be) modified.
    """
    content = path.read_text(encoding="utf-8")

    new_front_matter = build_front_matter(boost)

    match = FRONT_MATTER_PATTERN.search(content)
    if match:
        existing_fm = match.group(0)
        boost_str = str(int(boost)) if boost == int(boost) else str(boost)
        if f"boost: {boost_str}" in existing_fm:
            return False  # already correct
        new_content = content[:match.start()] + new_front_matter + content[match.end():]
    else:
        # Insert front matter after the HTML comment block (copyright header)
        # Find the end of consecutive HTML comments at the top of the file
        lines = content.split("\n")
        insert_after = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("<!--") and stripped.endswith("-->"):
                insert_after = i + 1
            elif stripped == "":
                if insert_after > 0:
                    insert_after = i + 1
                    break
                continue
            else:
                break

        before = "\n".join(lines[:insert_after])
        after = "\n".join(lines[insert_after:])

        if before and not before.endswith("\n"):
            before += "\n"

        new_content = before + new_front_matter + "\n" + after

    if dry_run:
        return True

    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true",
                        help="Apply changes (default is dry-run)")
    args = parser.parse_args()
    dry_run = not args.apply

    if dry_run:
        print("DRY RUN -- no files will be modified (use --apply to write changes)\n")

    if not DOMAINS_DIR.is_dir():
        print(f"Error: domains directory not found: {DOMAINS_DIR}", file=sys.stderr)
        sys.exit(1)

    modified = 0
    skipped = 0
    unchanged = 0

    for md_file in sorted(DOMAINS_DIR.glob("*.md")):
        match = CHAPTER_NUM_PATTERN.match(md_file.name)
        if not match:
            skipped += 1
            continue

        chapter_num = int(match.group(1))
        boost = get_boost(chapter_num)

        if boost is None:
            print(f"  SKIP  {md_file.name:40s}  (default boost via .meta.yml)")
            unchanged += 1
            continue

        changed = process_file(md_file, boost, dry_run)
        if changed:
            action = "WOULD UPDATE" if dry_run else "UPDATED"
            print(f"  {action}  {md_file.name:40s}  boost={boost}")
            modified += 1
        else:
            print(f"  OK    {md_file.name:40s}  boost={boost} (already set)")
            unchanged += 1

    print(f"\nSummary: {modified} modified, {unchanged} unchanged, {skipped} skipped")
    if dry_run and modified > 0:
        print("Run with --apply to write changes.")


if __name__ == "__main__":
    main()
