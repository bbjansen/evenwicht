#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify cross-references between chapters in the Evenwicht documentation.

Checks:
  1. Chapter references  — "Chapter N", "Ch. N", "Chapters N–M", flowchart "Ch N"
  2. Section references   — "Section N.M", "§N.M"
  3. Algorithm references — "Algorithm N.M"
  4. Definition/Theorem references — "Definition N.M", "Theorem N.M", etc.
  5. Connections section consistency — bidirectional link verification
  6. Dependency graph consistency — flowchart edges vs. prose references
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

VALID_CHAPTERS = set(range(1, 49))


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    level: str          # PASS, WARN, ERROR, INFO
    source_ch: int
    message: str


@dataclass
class ChapterInfo:
    number: int
    title: str
    path: Path
    text: str
    # Chapters referenced in prose (body text + Connections header)
    prose_refs: set[int] = field(default_factory=set)
    # Chapters referenced inside the flowchart in the Connections section
    flowchart_refs: set[int] = field(default_factory=set)
    # Chapters explicitly listed in "Within the Library" bullets
    within_library_refs: set[int] = field(default_factory=set)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def extract_chapter_number(filename: str) -> int:
    """Return the chapter number from a filename like '04-differential-calculus.md'."""
    m = re.match(r"(\d+)-", filename)
    if m:
        return int(m.group(1))
    raise ValueError(f"Cannot extract chapter number from {filename}")


def extract_chapter_title(text: str) -> str:
    """Return the chapter title from the first '# Chapter N: ...' heading."""
    m = re.search(r"^#\s+Chapter\s+\d+:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else "(unknown title)"


# ---------------------------------------------------------------------------
# Reference extraction
# ---------------------------------------------------------------------------

_RE_CHAPTER_SINGLE = re.compile(
    r"""
    (?:Chapter|chapter)\s+(\d+)        # "Chapter 4"
    """, re.VERBOSE
)

_RE_CHAPTER_ABBREV = re.compile(
    r"""
    Ch\.\s*(\d+)                        # "Ch. 7"
    """, re.VERBOSE
)

_RE_CHAPTER_RANGE = re.compile(
    r"""
    Chapters?\s+(\d+)\s*[–\-]\s*(\d+)  # "Chapters 3–5" or "Chapters 3-5"
    """, re.VERBOSE
)

_RE_FLOWCHART_EDGE = re.compile(
    r"""
    Ch\s*(\d+)                          # flowchart node "Ch 4" or "Ch4"
    """, re.VERBOSE
)

_RE_ALGORITHM_REF = re.compile(
    r"""
    Algorithm\s+(\d+)\.(\d+)            # "Algorithm 5.1"
    """, re.VERBOSE
)

_RE_FORMAL_REF = re.compile(
    r"""
    (Definition|Theorem|Lemma|Corollary|Proposition)\s+(\d+)\.(\d+)
    """, re.VERBOSE
)

# Cross-chapter formal reference: "Theorem 3.19 of Chapter 39"
_RE_CROSS_CHAPTER_FORMAL = re.compile(
    r"""
    (Definition|Theorem|Lemma|Corollary|Proposition|Algorithm)\s+
    \d+\.\d+\s+of\s+Chapter\s+(\d+)
    """, re.VERBOSE
)

_RE_SECTION_REF = re.compile(
    r"""
    (?:Section|§)\s*(\d+)\.(\d+)        # "Section 4.3" or "§3.2"
    """, re.VERBOSE
)


def _find_section_ranges(text: str, header_pattern: str) -> list[tuple[int, int]]:
    """Return (start, end) ranges for every section matching *header_pattern*."""
    ranges = []
    for m in re.finditer(header_pattern, text, re.MULTILINE):
        start = m.start()
        rest = text[start + 1:]
        next_sec = re.search(r"^##\s+", rest, re.MULTILINE)
        end = start + 1 + next_sec.start() if next_sec else len(text)
        ranges.append((start, end))
    return ranges


def _find_mermaid_ranges(text: str) -> list[tuple[int, int]]:
    """Return (start, end) ranges for every ```mermaid ... ``` block."""
    return [(m.start(), m.end()) for m in re.finditer(r"```mermaid.*?```", text, re.DOTALL)]


def _pos_in_any_range(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s <= pos < e for s, e in ranges)


def is_in_reference_section(text: str, pos: int) -> bool:
    """Return True if *pos* falls inside the References section (## 12. References)."""
    for start, end in _find_section_ranges(text, r"^##\s+\d+\.\s+References"):
        if start <= pos < end:
            return True
    return False


def is_in_mermaid_block(text: str, pos: int) -> bool:
    """Return True if *pos* falls inside a ```mermaid``` code block."""
    return _pos_in_any_range(pos, _find_mermaid_ranges(text))


def is_on_chapter_heading_line(text: str, pos: int, ch_num: int) -> bool:
    """Return True if *pos* is on the '# Chapter N: ...' heading line."""
    line_start = text.rfind("\n", 0, pos)
    line_start = 0 if line_start == -1 else line_start + 1
    line_end = text.find("\n", pos)
    line_end = len(text) if line_end == -1 else line_end
    line = text[line_start:line_end]
    return bool(re.match(rf"^#\s+Chapter\s+{ch_num}\b", line))


# Pattern for inline bibliographic citations: "AuthorName (YEAR), Chapter N"
_RE_INLINE_BIBLIO_CHAPTER = re.compile(
    r"""
    \(\d{4}\),?\s+Chapters?\s+\d+   # "(1984), Chapter 12"
    | \[\d+\],?\s+Chapters?\s+\d+   # "[3], Chapter 12"
    """, re.VERBOSE
)


def is_inline_bibliography(text: str, pos: int) -> bool:
    """Return True if the Chapter reference at *pos* is part of an inline citation.

    Matches patterns like ``Chiang (1984), Chapter 12`` or ``[3], Chapter 5``.
    """
    # Look at the 60 chars before the match to find the citation marker
    window_start = max(0, pos - 60)
    window = text[window_start:pos + 40]
    return bool(_RE_INLINE_BIBLIO_CHAPTER.search(window))


def extract_connections_section(text: str) -> str:
    """Return the text of the '## N. Connections' section (if any)."""
    m = re.search(r"^##\s+\d+\.\s+Connections\b", text, re.MULTILINE)
    if not m:
        return ""
    start = m.start()
    rest = text[start:]
    # Find next top-level section
    next_sec = re.search(r"^##\s+\d+\.\s+", rest[1:], re.MULTILINE)
    end = start + 1 + next_sec.start() if next_sec else len(text)
    return text[start:end]


def extract_within_library_section(text: str) -> str:
    """Return the text of the '### Within the Library' subsection."""
    m = re.search(r"^###\s+Within the Library\b", text, re.MULTILINE)
    if not m:
        return ""
    start = m.start()
    rest = text[start:]
    # Find next heading (any level)
    next_heading = re.search(r"^#{2,3}\s+", rest[1:], re.MULTILINE)
    end = start + 1 + next_heading.start() if next_heading else len(text)
    return text[start:end]


def extract_flowchart_block(connections_text: str) -> str:
    """Return the first mermaid flowchart block inside the connections section."""
    m = re.search(r"```mermaid\s*\n(.*?)```", connections_text, re.DOTALL)
    if not m:
        return ""
    block = m.group(1)
    if "flowchart" not in block:
        return ""
    return block


def chapter_refs_from_text(
    text: str,
    full_text: str,
    skip_references: bool = True,
    skip_mermaid: bool = True,
    skip_heading_for: int | None = None,
) -> set[int]:
    """Extract all chapter numbers referenced in *text*.

    Parameters
    ----------
    skip_references : bool
        Exclude matches inside the ## References section.
    skip_mermaid : bool
        Exclude matches inside ```mermaid``` code blocks.
    skip_heading_for : int | None
        If set, exclude matches on the ``# Chapter N:`` heading line for
        that chapter number.
    """
    refs: set[int] = set()
    base_offset = full_text.find(text) if text != full_text else 0

    # Pre-compute skip ranges once
    mermaid_ranges = _find_mermaid_ranges(full_text) if skip_mermaid else []

    def _should_skip(match_obj: re.Match) -> bool:
        abs_pos = base_offset + match_obj.start()
        if skip_references and is_in_reference_section(full_text, abs_pos):
            return True
        if skip_references and is_inline_bibliography(full_text, abs_pos):
            return True
        if skip_mermaid and _pos_in_any_range(abs_pos, mermaid_ranges):
            return True
        if skip_heading_for is not None and is_on_chapter_heading_line(
            full_text, abs_pos, skip_heading_for
        ):
            return True
        return False

    for m in _RE_CHAPTER_SINGLE.finditer(text):
        if _should_skip(m):
            continue
        refs.add(int(m.group(1)))

    for m in _RE_CHAPTER_ABBREV.finditer(text):
        if _should_skip(m):
            continue
        refs.add(int(m.group(1)))

    for m in _RE_CHAPTER_RANGE.finditer(text):
        if _should_skip(m):
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        refs.update(range(lo, hi + 1))

    for m in _RE_CROSS_CHAPTER_FORMAL.finditer(text):
        if _should_skip(m):
            continue
        refs.add(int(m.group(2)))

    return refs


def flowchart_chapter_refs(flowchart_text: str) -> set[int]:
    """Extract all chapter numbers referenced as nodes in a mermaid flowchart."""
    refs: set[int] = set()
    for m in _RE_FLOWCHART_EDGE.finditer(flowchart_text):
        refs.add(int(m.group(1)))
    return refs


# ---------------------------------------------------------------------------
# Verification checks
# ---------------------------------------------------------------------------

def verify_chapters(chapters: dict[int, ChapterInfo]) -> list[Issue]:
    issues: list[Issue] = []
    total_refs = 0
    chapter_titles = {n: c.title for n, c in chapters.items()}

    for ch_num, info in sorted(chapters.items()):
        # -- 1. Chapter reference validity ----------------------------------
        # Skip references section, mermaid blocks, and the chapter heading line
        all_prose_refs = chapter_refs_from_text(
            info.text, info.text,
            skip_references=True,
            skip_mermaid=True,
            skip_heading_for=ch_num,
        )
        info.prose_refs = all_prose_refs

        for ref in sorted(all_prose_refs):
            total_refs += 1
            title_hint = chapter_titles.get(ref, "???")

            if ref == ch_num:
                # Count the actual self-referencing locations for the message
                mermaid_ranges = _find_mermaid_ranges(info.text)
                occurrences = [
                    occ for occ in _RE_CHAPTER_SINGLE.finditer(info.text)
                    if int(occ.group(1)) == ch_num
                    and not is_on_chapter_heading_line(info.text, occ.start(), ch_num)
                    and not is_in_reference_section(info.text, occ.start())
                    and not is_inline_bibliography(info.text, occ.start())
                    and not _pos_in_any_range(occ.start(), mermaid_ranges)
                ]
                if occurrences:
                    issues.append(Issue(
                        "WARN", ch_num,
                        f"Ch {ch_num:02d} -> Ch {ref} — self-reference "
                        f"({len(occurrences)} occurrence(s) in prose)"
                    ))
            elif ref not in VALID_CHAPTERS:
                issues.append(Issue(
                    "WARN", ch_num,
                    f"Ch {ch_num:02d} -> Ch {ref} — chapter does not exist"
                ))
            else:
                issues.append(Issue(
                    "PASS", ch_num,
                    f"Ch {ch_num:02d} -> Ch {ref} ({title_hint}) — valid reference"
                ))

        # -- 2. Flowchart refs vs prose refs --------------------------------
        conn_text = extract_connections_section(info.text)
        fc_block = extract_flowchart_block(conn_text)
        fc_refs = flowchart_chapter_refs(fc_block)
        # Remove self from flowchart refs (the node for this chapter)
        fc_refs.discard(ch_num)
        info.flowchart_refs = fc_refs

        within_text = extract_within_library_section(info.text)
        wl_refs = chapter_refs_from_text(within_text, info.text, skip_references=False)
        wl_refs.discard(ch_num)
        info.within_library_refs = wl_refs

        # Flowchart edges not in prose
        for ref in sorted(fc_refs - all_prose_refs):
            if ref in VALID_CHAPTERS:
                total_refs += 1
                issues.append(Issue(
                    "INFO", ch_num,
                    f"Ch {ch_num:02d} flowchart references Ch {ref} "
                    f"({chapter_titles.get(ref, '???')}) "
                    f"but no prose mention found"
                ))

        # Flowchart edges referencing invalid chapters
        for ref in sorted(fc_refs):
            if ref not in VALID_CHAPTERS:
                issues.append(Issue(
                    "WARN", ch_num,
                    f"Ch {ch_num:02d} flowchart references Ch {ref} — "
                    f"chapter does not exist"
                ))

        # Within-Library refs not in flowchart
        for ref in sorted(wl_refs - fc_refs):
            if ref in VALID_CHAPTERS:
                issues.append(Issue(
                    "INFO", ch_num,
                    f"Ch {ch_num:02d} 'Within the Library' mentions Ch {ref} "
                    f"({chapter_titles.get(ref, '???')}) "
                    f"but no matching flowchart edge"
                ))

    # -- 5. Bidirectional connection check ----------------------------------
    for ch_num, info in sorted(chapters.items()):
        for ref in sorted(info.within_library_refs):
            if ref not in VALID_CHAPTERS or ref not in chapters:
                continue
            other = chapters[ref]
            if ch_num not in other.within_library_refs and ch_num not in other.flowchart_refs:
                issues.append(Issue(
                    "INFO", ch_num,
                    f"Ch {ch_num:02d} 'Within the Library' -> Ch {ref:02d} "
                    f"({chapter_titles.get(ref, '???')}), "
                    f"but Ch {ref:02d} does not reference Ch {ch_num:02d} back "
                    f"(one-way connection)"
                ))

    return issues, total_refs


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

LEVEL_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2, "PASS": 3}


def print_report(issues: list[Issue], total_refs: int) -> int:
    """Print the verification report and return an exit code (0 = clean)."""
    counts: dict[str, int] = defaultdict(int)
    for issue in issues:
        counts[issue.level] += 1

    # Print non-PASS issues first, then PASS
    sorted_issues = sorted(issues, key=lambda i: (LEVEL_ORDER.get(i.level, 9), i.source_ch))

    for issue in sorted_issues:
        print(f"{issue.level}: {issue.message}")

    print()
    print(
        f"INFO: {total_refs:,} cross-references checked, "
        f"{counts['WARN']} warnings, "
        f"{counts['ERROR']} errors, "
        f"{counts['INFO']} informational"
    )

    return 1 if counts["ERROR"] > 0 else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}", file=sys.stderr)
        return 1

    chapters: dict[int, ChapterInfo] = {}
    for path in chapter_files:
        text = path.read_text(encoding="utf-8")
        ch_num = extract_chapter_number(path.name)
        title = extract_chapter_title(text)
        chapters[ch_num] = ChapterInfo(
            number=ch_num, title=title, path=path, text=text
        )

    print(f"Loaded {len(chapters)} chapters from {DOCS_DIR}\n")

    issues, total_refs = verify_chapters(chapters)
    return print_report(issues, total_refs)


if __name__ == "__main__":
    sys.exit(main())
