#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify alignment between prerequisites, dependency graphs and prose connections.

For every chapter this script cross-validates three sources of truth that
describe how chapters relate to one another:

  1. **Prerequisites** -- the ``**Prerequisites**:`` line in the frontmatter.
  2. **Dependency graph** -- the Mermaid flowchart inside the Connections section.
  3. **"Within This Book"** -- the prose bullet points under that heading.

Checks performed:

  (a) Every prerequisite chapter appears as an incoming edge in the graph.
  (b) Every "Within This Book" chapter appears as an edge in the graph.
  (c) Every graph edge involving the focal chapter has prose support
      (prerequisite *or* "Within This Book").
  (d) Phantom edges: graph connections with no corresponding prose.
  (e) Missing graph nodes: prose references with no graph edge.
  (f) Bidirectional: if Chapter A mentions Chapter B in its connections,
      Chapter B should mention Chapter A back.

Usage:
  python3 scripts/verify-connections.py [--quick]

  --quick: skip the bidirectional cross-chapter check (fast mode for CI)
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

QUICK_MODE = "--quick" in sys.argv


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    level: str          # ERROR, WARN, INFO
    source_ch: int
    message: str


@dataclass
class ChapterInfo:
    number: int
    title: str
    path: Path
    text: str
    prerequisite_chapters: set[int] = field(default_factory=set)
    graph_incoming: set[int] = field(default_factory=set)
    graph_outgoing: set[int] = field(default_factory=set)
    within_book_chapters: set[int] = field(default_factory=set)


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
# Section extraction
# ---------------------------------------------------------------------------

def extract_connections_section(text: str) -> str:
    """Return the text of the '## Connections' section."""
    m = re.search(r"^##\s+Connections\b", text, re.MULTILINE)
    if not m:
        return ""
    start = m.start()
    rest = text[m.end():]
    next_sec = re.search(r"^##\s+", rest, re.MULTILINE)
    end = m.end() + next_sec.start() if next_sec else len(text)
    return text[start:end]


def extract_within_book_section(text: str) -> str:
    """Return the text of the '### Within This Book' subsection."""
    m = re.search(r"^###\s+Within This Book\b", text, re.MULTILINE)
    if not m:
        return ""
    start = m.start()
    rest = text[m.end():]
    next_heading = re.search(r"^#{2,3}\s+", rest, re.MULTILINE)
    end = m.end() + next_heading.start() if next_heading else len(text)
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


# ---------------------------------------------------------------------------
# Prerequisite extraction
# ---------------------------------------------------------------------------

_RE_PREREQ_CHAPTER = re.compile(
    r"""
    \[Chapter\s+(\d+)\]          # [Chapter 9] or [Chapter 9](filename)
    | (?<!\[)Chapter\s+(\d+)     # plain "Chapter 9" not preceded by [
    """, re.VERBOSE
)


def extract_prerequisites(text: str) -> set[int]:
    """Extract chapter numbers from the **Prerequisites**: line."""
    m = re.search(
        r"^\*\*Prerequisites\*\*:\s*(.+?)(?:\n\n|\n\*\*)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return set()
    prereq_line = m.group(1)
    if re.match(r"^\s*None\b", prereq_line):
        return set()
    chapters: set[int] = set()
    for match in _RE_PREREQ_CHAPTER.finditer(prereq_line):
        num = match.group(1) or match.group(2)
        chapters.add(int(num))
    return chapters


# ---------------------------------------------------------------------------
# Dependency graph extraction
# ---------------------------------------------------------------------------

# Matches edge lines like:
#   Ch7["Ch 7: Multivariate Calculus"] --> Ch12["Ch 12: Constrained Optimisation"]
#   Ch9 --> Ch10["Chapter 10: Eigenvalues"]
#   Ch8 --> Ch9
_RE_GRAPH_EDGE = re.compile(
    r"Ch(\d+)(?:\[.*?\])?\s*-->\s*Ch(\d+)(?:\[.*?\])?"
)

# Matches focal node styling: style ChN fill:#4a6fa5 or fill:#555555
_RE_FOCAL_STYLE = re.compile(
    r"style\s+Ch(\d+)\s+fill:#(?:4a6fa5|555555)"
)


def parse_graph(flowchart_text: str, ch_num: int) -> tuple[int, set[int], set[int]]:
    """Parse the Mermaid flowchart and return (focal, incoming, outgoing).

    The focal node is identified by its distinctive fill colour.  Incoming
    edges point *to* the focal node; outgoing edges point *from* it.

    Parameters
    ----------
    flowchart_text : str
        The raw text inside the ```mermaid``` block.
    ch_num : int
        The chapter number (used as fallback focal identification).

    Returns
    -------
    focal : int
        The focal chapter number.
    incoming : set[int]
        Chapter numbers with edges pointing to the focal node.
    outgoing : set[int]
        Chapter numbers the focal node points to.
    """
    # Identify the focal node
    focal_match = _RE_FOCAL_STYLE.search(flowchart_text)
    focal = int(focal_match.group(1)) if focal_match else ch_num

    edges: list[tuple[int, int]] = []
    for m in _RE_GRAPH_EDGE.finditer(flowchart_text):
        src, dst = int(m.group(1)), int(m.group(2))
        edges.append((src, dst))

    incoming: set[int] = set()
    outgoing: set[int] = set()
    for src, dst in edges:
        if dst == focal and src != focal:
            incoming.add(src)
        elif src == focal and dst != focal:
            outgoing.add(dst)

    return focal, incoming, outgoing


# ---------------------------------------------------------------------------
# Within This Book extraction
# ---------------------------------------------------------------------------

_RE_WITHIN_CHAPTER = re.compile(
    r"""
    \[Chapter\s+(\d+)\]          # [Chapter 9] or [Chapter 9](filename)
    | (?<!\[)Chapter\s+(\d+)     # plain "Chapter 9" not preceded by [
    """, re.VERBOSE
)


def extract_within_book_refs(within_text: str) -> set[int]:
    """Extract all chapter numbers referenced in the Within This Book section."""
    chapters: set[int] = set()
    for m in _RE_WITHIN_CHAPTER.finditer(within_text):
        num = m.group(1) or m.group(2)
        chapters.add(int(num))
    return chapters


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_chapters(chapters: dict[int, ChapterInfo]) -> list[Issue]:
    """Run all alignment checks and return a list of issues."""
    issues: list[Issue] = []
    chapter_titles = {n: c.title for n, c in chapters.items()}

    def title_of(n: int) -> str:
        return chapter_titles.get(n, "???")

    for ch_num, info in sorted(chapters.items()):
        # Extract the three data sources
        prereqs = info.prerequisite_chapters
        conn_text = extract_connections_section(info.text)
        fc_block = extract_flowchart_block(conn_text)
        within_text = extract_within_book_section(info.text)
        within_refs = extract_within_book_refs(within_text)
        within_refs.discard(ch_num)

        if not fc_block:
            issues.append(Issue(
                "WARN", ch_num,
                f"Ch {ch_num:02d}: no Mermaid dependency graph found "
                f"in Connections section",
            ))
            info.within_book_chapters = within_refs
            continue

        focal, incoming, outgoing = parse_graph(fc_block, ch_num)
        graph_all = incoming | outgoing
        prose_all = prereqs | within_refs

        info.graph_incoming = incoming
        info.graph_outgoing = outgoing
        info.within_book_chapters = within_refs

        # Verify focal node matches the chapter number
        if focal != ch_num:
            issues.append(Issue(
                "ERROR", ch_num,
                f"Ch {ch_num:02d}: dependency graph focal node is Ch {focal} "
                f"(expected Ch {ch_num})",
            ))

        # (a) Prerequisites not in graph incoming edges
        for ref in sorted(prereqs - incoming):
            if ref in VALID_CHAPTERS:
                issues.append(Issue(
                    "ERROR", ch_num,
                    f"Ch {ch_num:02d}: prerequisite Ch {ref:02d} "
                    f"({title_of(ref)}) has no incoming edge in the "
                    f"dependency graph",
                ))

        # (b) Within This Book refs not in graph edges
        for ref in sorted(within_refs - graph_all):
            if ref in VALID_CHAPTERS:
                issues.append(Issue(
                    "ERROR", ch_num,
                    f"Ch {ch_num:02d}: 'Within This Book' mentions "
                    f"Ch {ref:02d} ({title_of(ref)}) but no matching "
                    f"edge in the dependency graph",
                ))

        # (c,d) Graph edges with no prose support (phantom edges)
        for ref in sorted(graph_all - prose_all):
            if ref in VALID_CHAPTERS:
                direction = "incoming" if ref in incoming else "outgoing"
                issues.append(Issue(
                    "ERROR", ch_num,
                    f"Ch {ch_num:02d}: graph has {direction} edge "
                    f"to Ch {ref:02d} ({title_of(ref)}) but no "
                    f"corresponding prerequisite or 'Within This Book' "
                    f"entry (phantom edge)",
                ))

        # Phantom edges already reported above; exclude them from WARN checks
        phantom = graph_all - prose_all

        # (e) Graph incoming edges not in prerequisites (skip phantoms)
        for ref in sorted(incoming - prereqs - phantom):
            if ref in VALID_CHAPTERS:
                # Check if it appears in Within This Book instead (some
                # chapters list prerequisite chapters in Within This Book
                # prose rather than only in the Prerequisites line).
                if ref not in within_refs:
                    issues.append(Issue(
                        "WARN", ch_num,
                        f"Ch {ch_num:02d}: graph has incoming edge from "
                        f"Ch {ref:02d} ({title_of(ref)}) which is not "
                        f"listed as a prerequisite",
                    ))

        # Graph outgoing edges not in Within This Book (skip phantoms)
        for ref in sorted(outgoing - within_refs - phantom):
            if ref in VALID_CHAPTERS:
                issues.append(Issue(
                    "WARN", ch_num,
                    f"Ch {ch_num:02d}: graph has outgoing edge to "
                    f"Ch {ref:02d} ({title_of(ref)}) with no "
                    f"'Within This Book' entry",
                ))

    # (f) Bidirectional cross-chapter check
    if not QUICK_MODE:
        for ch_num, info in sorted(chapters.items()):
            mentioned = info.within_book_chapters | info.prerequisite_chapters
            for ref in sorted(mentioned):
                if ref not in VALID_CHAPTERS or ref not in chapters:
                    continue
                other = chapters[ref]
                other_mentioned = (
                    other.within_book_chapters | other.prerequisite_chapters
                )
                if ch_num not in other_mentioned:
                    # Determine the relationship direction
                    if ref in info.prerequisite_chapters:
                        rel = "prerequisite"
                    else:
                        rel = "'Within This Book'"
                    issues.append(Issue(
                        "INFO", ch_num,
                        f"Ch {ch_num:02d} lists Ch {ref:02d} "
                        f"({chapter_titles.get(ref, '???')}) as {rel}, "
                        f"but Ch {ref:02d} does not reference "
                        f"Ch {ch_num:02d} back (one-way connection)",
                    ))

    return issues


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

LEVEL_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


def print_report(issues: list[Issue], num_chapters: int) -> int:
    """Print the verification report and return an exit code (0 = clean)."""
    counts: dict[str, int] = defaultdict(int)
    for issue in issues:
        counts[issue.level] += 1

    sorted_issues = sorted(
        issues,
        key=lambda i: (LEVEL_ORDER.get(i.level, 9), i.source_ch),
    )

    print("=" * 78)
    print("CONNECTION ALIGNMENT CHECK")
    print("=" * 78)
    print()

    if not sorted_issues:
        print("  No issues found.")
    else:
        current_level = None
        for issue in sorted_issues:
            if issue.level != current_level:
                if current_level is not None:
                    print()
                current_level = issue.level
            print(f"  {issue.level}: {issue.message}")

    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Chapters scanned:  {num_chapters}")
    print(f"  Errors:            {counts['ERROR']}")
    print(f"  Warnings:          {counts['WARN']}")
    print(f"  Informational:     {counts['INFO']}")
    if QUICK_MODE:
        print(f"  Mode:              --quick (bidirectional check skipped)")
    print()

    if counts["ERROR"] > 0:
        print("RESULT: FAIL")
        return 1

    if counts["WARN"] > 0 or counts["INFO"] > 0:
        print("RESULT: PASS (with warnings)")
        return 0

    print("RESULT: PASS")
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
        prereqs = extract_prerequisites(text)

        chapters[ch_num] = ChapterInfo(
            number=ch_num,
            title=title,
            path=path,
            text=text,
            prerequisite_chapters=prereqs,
        )

    print(f"Loaded {len(chapters)} chapters from {DOCS_DIR}\n")

    issues = verify_chapters(chapters)
    return print_report(issues, len(chapters))


if __name__ == "__main__":
    sys.exit(main())
