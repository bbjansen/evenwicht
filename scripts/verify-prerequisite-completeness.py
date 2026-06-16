#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify that each chapter's declared prerequisites cover its actual dependencies.

For every chapter, this script:
  1. Parses the **Prerequisites** line to extract declared prerequisite chapter
     numbers (patterns: [Chapter N], Chapter N, [Chapter N](filename)).
  2. Scans sections 4 (Core Theory) through 8 (Worked Examples) for references
     to other chapters: [Chapter N], Chapter N, [Ch N], [Chapter N](XX-name.md).
  3. Builds two directed graphs: declared prerequisites and actual body
     dependencies.
  4. Computes the transitive closure of declared prerequisites so that indirect
     coverage is recognised.
  5. Classifies undeclared references as either:
     - FORWARD_REF: a theory chapter (1-24) referencing a higher-numbered
       chapter.  These are informational ("this topic will be used later")
       and are reported as INFO, not ERROR.
     - MISSING: a genuine prerequisite gap.  These are reported as ERROR.
  6. Reports:
     (a) Missing prerequisites  - chapters referenced in the body but not
         transitively covered by declared prerequisites (ERROR).
     (b) Forward references     - theory chapters referencing later chapters
         without declaring them (INFO, does not cause failure).
     (c) Phantom prerequisites  - chapters declared but never referenced in
         the body (sections 4-8) (WARN).

The Connections section (## 9.) is intentionally excluded because it
legitimately references forward-looking chapters.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

VALID_CHAPTERS = set(range(1, 49))
THEORY_CHAPTERS = set(range(1, 25))   # Chapters 1-24 are theory chapters
APP_CHAPTERS = set(range(25, 49))     # Chapters 25-48 are application chapters

# Sections whose body text is scanned for actual dependencies.
BODY_SECTION_START = 4  # Core Theory
BODY_SECTION_END = 8    # Worked Examples (inclusive)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ChapterInfo:
    number: int
    title: str
    path: Path
    text: str
    declared_prereqs: set[int] = field(default_factory=set)
    body_refs: set[int] = field(default_factory=set)


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
# Prerequisite extraction
# ---------------------------------------------------------------------------

_RE_PREREQ_CHAPTER = re.compile(
    r"""
    \[Chapter\s+(\d+)\]          # [Chapter 9] or [Chapter 9](filename)
    | (?<!\[)Chapter\s+(\d+)     # plain "Chapter 9" not preceded by [
    """, re.VERBOSE
)


def extract_declared_prereqs(text: str) -> set[int]:
    """Extract chapter numbers from the **Prerequisites**: line."""
    m = re.search(r"^\*\*Prerequisites\*\*:\s*(.+?)(?:\n\n|\n\*\*)", text,
                  re.MULTILINE | re.DOTALL)
    if not m:
        return set()
    prereq_line = m.group(1)

    # "None" means no prerequisites
    if re.match(r"^\s*None\b", prereq_line):
        return set()

    chapters: set[int] = set()
    for match in _RE_PREREQ_CHAPTER.finditer(prereq_line):
        num = match.group(1) or match.group(2)
        chapters.add(int(num))
    return chapters


# ---------------------------------------------------------------------------
# Body reference extraction (sections 4-8)
# ---------------------------------------------------------------------------

_RE_BODY_CHAPTER_REF = re.compile(
    r"""
    \[Chapter\s+(\d+)\]         # [Chapter 9] or [Chapter 9](...)
    | \[Ch\.?\s+(\d+)\]         # [Ch 9] or [Ch. 9]
    | (?<!\[)Chapter\s+(\d+)    # plain "Chapter 9"
    """, re.VERBOSE
)


def _find_section_span(text: str, section_num: int) -> tuple[int, int] | None:
    """Return (start, end) of ## N. ... section, or None if not found."""
    heading = re.search(
        rf"^##\s+{section_num}\.\s+[^\n]+$",
        text,
        re.MULTILINE,
    )
    if not heading:
        return None
    start = heading.start()
    rest = text[start + 1:]
    next_h2 = re.search(r"^##\s+\d+\.\s+", rest, re.MULTILINE)
    end = start + 1 + next_h2.start() if next_h2 else len(text)
    return (start, end)


def extract_body_text(text: str) -> str:
    """Return the concatenated text of sections 4 through 8."""
    parts: list[str] = []
    for sec in range(BODY_SECTION_START, BODY_SECTION_END + 1):
        span = _find_section_span(text, sec)
        if span:
            parts.append(text[span[0]:span[1]])
    return "\n".join(parts)


def extract_body_refs(body_text: str, self_chapter: int) -> set[int]:
    """Extract all chapter numbers referenced in the body text."""
    refs: set[int] = set()
    for match in _RE_BODY_CHAPTER_REF.finditer(body_text):
        num = match.group(1) or match.group(2) or match.group(3)
        ch = int(num)
        if ch != self_chapter and ch in VALID_CHAPTERS:
            refs.add(ch)
    return refs


# ---------------------------------------------------------------------------
# Transitive closure
# ---------------------------------------------------------------------------

def transitive_closure(prereqs: dict[int, set[int]]) -> dict[int, set[int]]:
    """Compute the transitive closure of the prerequisite graph.

    If chapter A declares B as a prerequisite and B declares C, then A
    transitively covers C.
    """
    closure: dict[int, set[int]] = {ch: set(deps) for ch, deps in prereqs.items()}

    changed = True
    while changed:
        changed = False
        for ch in closure:
            expanded: set[int] = set()
            for dep in closure[ch]:
                if dep in closure:
                    expanded |= closure[dep]
            before = len(closure[ch])
            closure[ch] |= expanded
            if len(closure[ch]) > before:
                changed = True

    return closure


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def _is_forward_ref(source_ch: int, target_ch: int) -> bool:
    """Return True if the reference is a forward reference in theory chapters.

    A forward reference is when a theory chapter (1-24) references a
    higher-numbered chapter.  These are informational previews ("this
    topic will be used later") and not genuine prerequisite gaps.

    For application chapters (25-48), all undeclared references to theory
    chapters are genuine missing prerequisites.
    """
    return source_ch in THEORY_CHAPTERS and target_ch > source_ch


def verify(
    chapters: dict[int, ChapterInfo],
) -> tuple[list[str], list[str], list[str], int, int, int]:
    """Return (missing, forward_ref, phantom, missing_n, forward_n, phantom_n)."""
    # Build raw prerequisite graph
    raw_prereqs: dict[int, set[int]] = {}
    for ch_num, info in chapters.items():
        raw_prereqs[ch_num] = info.declared_prereqs

    # Compute transitive closure
    closure = transitive_closure(raw_prereqs)

    missing_issues: list[str] = []
    forward_ref_issues: list[str] = []
    phantom_issues: list[str] = []
    total_missing = 0
    total_forward = 0
    total_phantom = 0

    chapter_titles = {n: c.title for n, c in chapters.items()}

    for ch_num in sorted(chapters):
        info = chapters[ch_num]
        covered = closure.get(ch_num, set())
        declared = info.declared_prereqs
        body = info.body_refs

        # (a) Undeclared body references: classify as forward ref or missing
        undeclared = body - covered
        for ref in sorted(undeclared):
            title = chapter_titles.get(ref, "???")
            if _is_forward_ref(ch_num, ref):
                total_forward += 1
                forward_ref_issues.append(
                    f"Ch {ch_num:02d} ({info.title}): body references "
                    f"Ch {ref:02d} ({title}) — forward reference "
                    f"(lower chapter previews later topic)"
                )
            else:
                total_missing += 1
                missing_issues.append(
                    f"Ch {ch_num:02d} ({info.title}): body references "
                    f"Ch {ref:02d} ({title}) but it is not a declared or "
                    f"transitive prerequisite"
                )

        # (b) Phantom: declared but never referenced in body
        phantom = declared - body
        for ref in sorted(phantom):
            total_phantom += 1
            title = chapter_titles.get(ref, "???")
            phantom_issues.append(
                f"Ch {ch_num:02d} ({info.title}): declares "
                f"Ch {ref:02d} ({title}) as prerequisite but never "
                f"references it in sections 4-8"
            )

    return (missing_issues, forward_ref_issues, phantom_issues,
            total_missing, total_forward, total_phantom)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(
    chapters: dict[int, ChapterInfo],
    missing_issues: list[str],
    forward_ref_issues: list[str],
    phantom_issues: list[str],
    total_missing: int,
    total_forward: int,
    total_phantom: int,
) -> int:
    """Print the verification report and return an exit code."""
    print("=" * 78)
    print("PREREQUISITE COMPLETENESS CHECK — Evenwicht")
    print("=" * 78)
    print()

    # Per-chapter summary table
    print(f"{'Chapter':<50} {'Decl':>5} {'Body':>5} {'Miss':>5} {'FwdR':>5} {'Phnt':>5}")
    print("-" * 78)

    raw_prereqs: dict[int, set[int]] = {
        ch: info.declared_prereqs for ch, info in chapters.items()
    }
    closure = transitive_closure(raw_prereqs)

    for ch_num in sorted(chapters):
        info = chapters[ch_num]
        covered = closure.get(ch_num, set())
        undeclared = info.body_refs - covered
        fwd = sum(1 for r in undeclared if _is_forward_ref(ch_num, r))
        miss = len(undeclared) - fwd
        phnt = len(info.declared_prereqs - info.body_refs)
        tag = ""
        if miss > 0:
            tag += " ***"
        title_trunc = info.title[:42]
        print(
            f"  Ch {ch_num:02d}: {title_trunc:<42} "
            f"{len(info.declared_prereqs):>5} {len(info.body_refs):>5} "
            f"{miss:>5} {fwd:>5} {phnt:>5}{tag}"
        )
    print()

    # Missing prerequisites (ERROR)
    if missing_issues:
        print("=" * 78)
        print(f"MISSING PREREQUISITES ({total_missing})")
        print("=" * 78)
        for issue in missing_issues:
            print(f"  ERROR: {issue}")
        print()

    # Forward references (INFO)
    if forward_ref_issues:
        print("=" * 78)
        print(f"FORWARD REFERENCES ({total_forward})")
        print("=" * 78)
        for issue in forward_ref_issues:
            print(f"  INFO:  {issue}")
        print()

    # Phantom prerequisites (WARN)
    if phantom_issues:
        print("=" * 78)
        print(f"PHANTOM PREREQUISITES ({total_phantom})")
        print("=" * 78)
        for issue in phantom_issues:
            print(f"  WARN:  {issue}")
        print()

    # Summary
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Total chapters:                {len(chapters)}")
    print(f"  Missing prerequisites (ERROR): {total_missing}")
    print(f"  Forward references    (INFO):  {total_forward}")
    print(f"  Phantom prerequisites (WARN):  {total_phantom}")
    print()

    if total_missing > 0:
        print("RESULT: FAIL — some body references are not covered by "
              "declared prerequisites.")
        return 1

    if total_forward > 0 or total_phantom > 0:
        print("RESULT: PASS (with warnings) — all body references are "
              "covered (or are forward references), but some informational "
              "notes remain.")
        return 0

    print("RESULT: PASS — all prerequisites are complete and all "
          "declarations are used.")
    return 0


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

        declared = extract_declared_prereqs(text)
        body_text = extract_body_text(text)
        body = extract_body_refs(body_text, ch_num)

        chapters[ch_num] = ChapterInfo(
            number=ch_num,
            title=title,
            path=path,
            text=text,
            declared_prereqs=declared,
            body_refs=body,
        )

    print(f"Loaded {len(chapters)} chapters from {DOCS_DIR}\n")

    (missing_issues, forward_ref_issues, phantom_issues,
     total_missing, total_forward, total_phantom) = verify(chapters)
    return print_report(
        chapters, missing_issues, forward_ref_issues, phantom_issues,
        total_missing, total_forward, total_phantom,
    )


if __name__ == "__main__":
    sys.exit(main())
