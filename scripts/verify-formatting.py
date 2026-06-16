#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify formatting rules across all 48 domain chapters.

Checks:
  1. Display math spacing     — every $$ block needs blank lines before and after
  2. Admonition formatting    — 4-space indent, blank line after opener, no nesting,
                                proof blocks end with QED marker
  3. Wall-of-text detection   — paragraphs exceeding ~120 words without a break
  4. Glossary alphabetical    — glossary entries in strict alphabetical order
  5. Algorithm completeness   — each Algorithm subsection has Input, Output, Complexity
  6. Copyright header         — lines 1-3 must be the standard copyright/SPDX/LICENSE
  7. Section structure        — all 12 mandatory H2 sections present, unnumbered
  8. Proof QED markers        — every proof block contains a QED square

Usage:
    python3 scripts/verify-formatting.py [--quick]

  --quick: skip wall-of-text detection (fast mode for CI)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

QUICK_MODE = "--quick" in sys.argv

# The 12 mandatory H2 sections every chapter must contain.
MANDATORY_SECTIONS = [
    "Historical Context",
    "Why This Chapter Matters",
    "Notation & Conventions",
    "Core Theory",
    "Formulas & Identities",
    "Algorithms",
    "Numerical Considerations",
    "Worked Examples",
    "Connections",
    "Exercises",
    "References",
    "Glossary",
]

# Expected copyright header (lines 1-3).
COPYRIGHT_LINES = [
    "<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->",
    "<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->",
    "<!-- See LICENSE for full terms. Commercial licensing available. -->",
]

# Maximum words in a paragraph before it is flagged as a wall of text.
WALL_OF_TEXT_THRESHOLD = 120


def check_display_math_spacing(lines: list[str]) -> list[str]:
    """Check that every $$ block is preceded and followed by a blank line.

    Display math comes in two forms:

    1. Single-line: ``$$formula$$`` — the entire block is one line.
       Needs a blank line before AND after.

    2. Multi-line: an opening ``$$`` on its own line, content lines,
       then a closing ``$$`` on its own line.  The opening ``$$`` needs
       a blank line before it; the closing ``$$`` needs a blank line
       after it.

    Lines inside fenced code blocks are excluded.
    """
    issues: list[str] = []
    in_code_block = False
    in_math_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track fenced code blocks (``` or ~~~).
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if not stripped.startswith("$$"):
            continue

        line_num = i + 1  # 1-based

        # Determine whether this is a single-line block or a multi-line
        # opener/closer.  A line that is *just* "$$" (possibly with
        # trailing whitespace) is a multi-line delimiter.  A line like
        # "$$formula$$" is single-line.
        is_solo_delim = stripped.rstrip() == "$$"

        if is_solo_delim and not in_math_block:
            # Opening $$ of a multi-line block — needs blank line before.
            in_math_block = True
            if i > 0 and lines[i - 1].strip():
                issues.append(
                    f"  line {line_num}: display math ($$) not preceded by a blank line"
                )
        elif is_solo_delim and in_math_block:
            # Closing $$ of a multi-line block — needs blank line after.
            in_math_block = False
            if i < len(lines) - 1 and lines[i + 1].strip():
                issues.append(
                    f"  line {line_num}: display math ($$) not followed by a blank line"
                )
        else:
            # Single-line $$...$$  — needs blank before AND after.
            # Also handles $$...$$ that opens or closes inside a block
            # (e.g. "$$\begin{aligned}...$$").
            if stripped.endswith("$$") and len(stripped) > 2:
                # Truly single-line.
                if i > 0 and lines[i - 1].strip():
                    issues.append(
                        f"  line {line_num}: display math ($$) not preceded by a blank line"
                    )
                if i < len(lines) - 1 and lines[i + 1].strip():
                    issues.append(
                        f"  line {line_num}: display math ($$) not followed by a blank line"
                    )
            else:
                # Starts with $$ but does not close on the same line.
                # Treat as opening delimiter of a multi-line block.
                in_math_block = True
                if i > 0 and lines[i - 1].strip():
                    issues.append(
                        f"  line {line_num}: display math ($$) not preceded by a blank line"
                    )

    return issues


def check_admonition_formatting(lines: list[str]) -> list[str]:
    """Check admonition formatting rules.

    Rules:
      - Content inside an admonition must be indented exactly 4 spaces.
      - Proof blocks (??? note "Proof") must have a blank line between the
        opening line and the first content line.
      - No nested admonitions (an admonition opener inside another admonition).
      - Proof blocks must end with $\\square$ on the last content line.
    """
    issues: list[str] = []
    in_code_block = False
    admonition_re = re.compile(r'^(\s*)(!!!|\?\?\?\+?)\s+\w+')
    proof_re = re.compile(r'^(\s*)\?\?\?\+?\s+note\s+"Proof"')

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            i += 1
            continue

        match = admonition_re.match(lines[i])
        if not match:
            i += 1
            continue

        line_num = i + 1  # 1-based
        base_indent = len(match.group(1))
        is_proof = bool(proof_re.match(lines[i]))

        # Check blank line after proof opener.
        if is_proof:
            if i + 1 < len(lines) and lines[i + 1].strip():
                issues.append(
                    f"  line {line_num}: proof block missing blank line after opening"
                )

        # Walk the admonition body: lines indented more than the opener.
        content_indent = base_indent + 4
        j = i + 1
        last_content_line_num = None
        last_content_text = ""

        while j < len(lines):
            raw = lines[j]
            raw_stripped = raw.strip()

            # Empty lines are allowed inside the block.
            if not raw_stripped:
                j += 1
                continue

            # Determine indentation of this line.
            indent = len(raw) - len(raw.lstrip())
            if indent < content_indent:
                # We have left the admonition body.
                break

            # Check exact 4-space indent (relative to the opener).
            # Lines inside nested code blocks are exempt.
            inner_stripped = raw_stripped
            if inner_stripped.startswith("```") or inner_stripped.startswith("~~~"):
                # Skip to matching closer.
                j += 1
                while j < len(lines):
                    if lines[j].strip().startswith("```") or lines[j].strip().startswith("~~~"):
                        j += 1
                        break
                    j += 1
                continue

            # Flag non-4-space indentation (only first-level content lines).
            if indent != content_indent and indent < content_indent + 4:
                # Allow additional indentation for sub-lists, code, etc.
                # Only flag lines that are indented less than 4 spaces beyond opener
                # but still within the block.
                if indent > base_indent and indent < content_indent:
                    issues.append(
                        f"  line {j + 1}: admonition content indented {indent - base_indent} spaces instead of 4"
                    )

            # Check for nested admonitions.
            if admonition_re.match(raw):
                issues.append(
                    f"  line {j + 1}: nested admonition detected inside admonition at line {line_num}"
                )

            last_content_line_num = j + 1
            last_content_text = raw_stripped
            j += 1

        # For proof blocks, verify QED marker on last content line.
        if is_proof and last_content_text:
            if "$\\square$" not in last_content_text:
                issues.append(
                    f"  line {last_content_line_num}: proof block (opened line {line_num}) does not end with $\\square$"
                )

        i = j if j > i + 1 else i + 1

    return issues


def check_wall_of_text(lines: list[str]) -> list[str]:
    """Flag paragraphs exceeding WALL_OF_TEXT_THRESHOLD words.

    A paragraph is a consecutive run of non-blank lines that are not
    headings, list items, display math, code fences, or admonition openers.
    """
    issues: list[str] = []
    in_code_block = False

    para_start = None
    word_count = 0

    def _is_break(line_stripped: str) -> bool:
        """Return True if this line type breaks a paragraph."""
        if not line_stripped:
            return True
        if line_stripped.startswith("#"):
            return True
        if line_stripped.startswith("- ") or line_stripped.startswith("* "):
            return True
        if re.match(r'^\d+\.\s', line_stripped):
            return True
        if line_stripped.startswith("$$"):
            return True
        if line_stripped.startswith("```") or line_stripped.startswith("~~~"):
            return True
        if re.match(r'^(!!!|\?\?\?\+?)\s', line_stripped):
            return True
        if line_stripped.startswith("|"):
            return True
        if line_stripped.startswith("---"):
            return True
        if line_stripped.startswith(">"):
            return True
        return False

    def _flush() -> None:
        nonlocal para_start, word_count
        if para_start is not None and word_count > WALL_OF_TEXT_THRESHOLD:
            issues.append(
                f"  line {para_start}: paragraph has ~{word_count} words (>{WALL_OF_TEXT_THRESHOLD})"
            )
        para_start = None
        word_count = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            _flush()
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if _is_break(stripped):
            _flush()
            continue

        if para_start is None:
            para_start = i + 1  # 1-based
        word_count += len(stripped.split())

    _flush()
    return issues


def check_glossary_order(lines: list[str]) -> list[str]:
    """Check that glossary entries are in strict alphabetical order.

    Glossary entries are lines matching '- **Term** ...'.  We extract all
    such entries inside the ## Glossary section and verify ordering.
    """
    issues: list[str] = []
    glossary_entry_re = re.compile(r'^- \*\*([^*]+)\*\*')

    # Find the ## Glossary section.
    in_glossary = False
    entries: list[tuple[int, str]] = []  # (line_num, term)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^## Glossary\s*$', stripped):
            in_glossary = True
            continue
        if in_glossary and stripped.startswith("## "):
            break
        if not in_glossary:
            continue

        m = glossary_entry_re.match(stripped)
        if m:
            entries.append((i + 1, m.group(1).strip()))

    # Check alphabetical order (case-insensitive).
    for idx in range(1, len(entries)):
        _, prev_term = entries[idx - 1]
        curr_line, curr_term = entries[idx]
        if prev_term.lower() > curr_term.lower():
            issues.append(
                f"  line {curr_line}: glossary entry \"{curr_term}\" should come before \"{prev_term}\" (alphabetical order)"
            )

    return issues


def check_algorithm_completeness(lines: list[str]) -> list[str]:
    """Check that each Algorithm subsection has Input, Output, Complexity.

    Looks for ### Algorithm N.x subsections within ## Algorithms and verifies
    the required bold-label lines are present.
    """
    issues: list[str] = []
    algo_header_re = re.compile(r'^### Algorithm\s+\d+\.\d+')

    # Find the ## Algorithms section boundaries.
    algo_section_start = None
    algo_section_end = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^## Algorithms\s*$', stripped):
            algo_section_start = i
            continue
        if algo_section_start is not None and algo_section_end is None:
            if stripped.startswith("## ") and not stripped.startswith("## Algorithms"):
                algo_section_end = i
                break

    if algo_section_start is None:
        return issues
    if algo_section_end is None:
        algo_section_end = len(lines)

    # Find each Algorithm subsection.
    algo_starts: list[tuple[int, str]] = []
    for i in range(algo_section_start, algo_section_end):
        m = algo_header_re.match(lines[i].strip())
        if m:
            algo_starts.append((i, lines[i].strip()))

    for idx, (start, header) in enumerate(algo_starts):
        # Determine end of this subsection.
        if idx + 1 < len(algo_starts):
            end = algo_starts[idx + 1][0]
        else:
            end = algo_section_end

        block = "\n".join(lines[start:end])
        line_num = start + 1  # 1-based

        has_input = bool(re.search(r'\*\*Input\*\*', block))
        has_output = bool(re.search(r'\*\*Output\*\*', block))
        has_complexity = bool(re.search(r'\*\*Complexity\*\*', block))

        missing = []
        if not has_input:
            missing.append("Input")
        if not has_output:
            missing.append("Output")
        if not has_complexity:
            missing.append("Complexity")
        if missing:
            issues.append(
                f"  line {line_num}: {header} missing: {', '.join(missing)}"
            )

    return issues


def check_copyright_header(lines: list[str]) -> list[str]:
    """Check that lines 1-3 are the standard copyright/SPDX/LICENSE comments."""
    issues: list[str] = []

    for idx, expected in enumerate(COPYRIGHT_LINES):
        if idx >= len(lines):
            issues.append(
                f"  line {idx + 1}: missing copyright header line"
            )
            continue
        actual = lines[idx].rstrip("\n").rstrip()
        if actual != expected:
            issues.append(
                f"  line {idx + 1}: copyright header mismatch"
            )

    return issues


def check_section_structure(lines: list[str]) -> list[str]:
    """Check all 12 mandatory H2 sections are present and unnumbered.

    Also detects numbered headings like '## 1. Historical Context'.
    """
    issues: list[str] = []
    found_sections: set[str] = set()
    numbered_heading_re = re.compile(r'^## \d+\.\s+(.+)$')

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("## "):
            continue
        # Skip H3 and beyond.
        if stripped.startswith("### "):
            continue

        heading_text = stripped[3:].strip()

        # Check for numbered headings.
        m = numbered_heading_re.match(stripped)
        if m:
            issues.append(
                f"  line {i + 1}: numbered heading detected: \"{stripped}\" (should be unnumbered)"
            )
            heading_text = m.group(1).strip()

        found_sections.add(heading_text)

    for section in MANDATORY_SECTIONS:
        if section not in found_sections:
            issues.append(
                f"  missing mandatory section: ## {section}"
            )

    return issues


def check_proof_qed(lines: list[str]) -> list[str]:
    """Check that every proof block contains $\\square$ somewhere.

    This is a simpler/broader check than the admonition formatter:
    it scans the entire body of each proof block for the QED marker.
    """
    issues: list[str] = []
    proof_re = re.compile(r'^(\s*)\?\?\?\+?\s+note\s+"Proof"')
    in_code_block = False

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            i += 1
            continue

        m = proof_re.match(lines[i])
        if not m:
            i += 1
            continue

        line_num = i + 1  # 1-based
        base_indent = len(m.group(1))
        content_indent = base_indent + 4
        found_qed = False

        j = i + 1
        while j < len(lines):
            raw = lines[j]
            raw_stripped = raw.strip()

            if not raw_stripped:
                j += 1
                continue

            indent = len(raw) - len(raw.lstrip())
            if indent < content_indent and raw_stripped:
                break

            if "$\\square$" in raw_stripped:
                found_qed = True

            j += 1

        if not found_qed:
            issues.append(
                f"  line {line_num}: proof block missing $\\square$ QED marker"
            )

        i = j if j > i + 1 else i + 1

    return issues


def process_chapter(filepath: Path) -> list[str]:
    """Run all formatting checks on a single chapter file.

    Returns a list of issue strings (empty if all checks pass).
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    all_issues: list[str] = []

    all_issues.extend(check_display_math_spacing(lines))
    all_issues.extend(check_admonition_formatting(lines))
    all_issues.extend(check_glossary_order(lines))
    all_issues.extend(check_algorithm_completeness(lines))
    all_issues.extend(check_copyright_header(lines))
    all_issues.extend(check_section_structure(lines))
    all_issues.extend(check_proof_qed(lines))

    if not QUICK_MODE:
        all_issues.extend(check_wall_of_text(lines))

    return all_issues


def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}")
        return 1

    checks = "7 of 8 (skipping wall-of-text)" if QUICK_MODE else "all 8"
    print(f"Scanning {len(chapter_files)} chapters for formatting issues ({checks} checks)...\n")

    total_issues = 0
    chapters_with_issues = 0

    for filepath in chapter_files:
        issues = process_chapter(filepath)
        if issues:
            chapters_with_issues += 1
            print(f"  {filepath.stem}")
            for issue in issues:
                print(f"    {issue}")
            total_issues += len(issues)
            print()

    print("=" * 60)
    print(f"Chapters scanned:        {len(chapter_files)}")
    print(f"Chapters with issues:    {chapters_with_issues}")
    print(f"Total issues:            {total_issues}")
    print("=" * 60)

    if total_issues > 0:
        return 1
    print("\nAll formatting checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
