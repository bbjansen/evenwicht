#!/usr/bin/env python3

"""Re-format the already-converted subject index:
   - Remove letter nav bar
   - Change — to :
   - Change [ChapterName](path) to [N](path) where N is chapter number
   - Make each entry a list item for proper column flow
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "docs" / "reference" / "subject-index.md"


def extract_chapter_num(path: str) -> str:
    """Extract chapter number from a path like ../domains/03-limits-continuity.md"""
    m = re.search(r"/(\d{2})-", path)
    if m:
        return str(int(m.group(1)))
    return "?"


def reformat(text: str) -> str:
    lines = text.split("\n")
    output: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Remove the nav bar line (A · B · C ...)
        if stripped.startswith("[A](#a)"):
            continue
        # Remove blank line after nav bar removal
        if not stripped and output and output[-1] == "":
            continue

        # Convert entry lines: **Term** — [Name](path) to - **Term**: [N](path)
        if stripped.startswith("**") and "—" in stripped:
            # Extract term
            term_match = re.match(r"\*\*(.+?)\*\*", stripped)
            if not term_match:
                output.append(line)
                continue

            term = term_match.group(1)

            # Find all links and convert to chapter numbers
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", stripped)
            num_links = []
            for _name, path in links:
                num = extract_chapter_num(path)
                num_links.append(f"[{num}]({path})")

            if num_links:
                output.append(f"- **{term}**: {', '.join(num_links)}")
            else:
                output.append(f"- **{term}**")
            continue

        output.append(line)

    return "\n".join(output)


def main() -> int:
    text = INDEX_FILE.read_text(encoding="utf-8")
    new_text = reformat(text)

    if "--dry-run" in sys.argv:
        print(new_text[:2000])
        print(f"\n... ({len(new_text)} chars)")
    else:
        INDEX_FILE.write_text(new_text, encoding="utf-8")
        print("Reformatted subject index")

    return 0


if __name__ == "__main__":
    sys.exit(main())
