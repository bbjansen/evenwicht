# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Timeline chronological order verification for all 48 Evenwicht chapters.

Extracts every ``timeline`` mermaid block from docs/domains/*.md and verifies
that the year labels appear in non-decreasing order.  Mixed-format years
(e.g. "1920s", "c. 1850") are normalised to integers where possible; entries
that cannot be parsed are skipped without failing the check.

Usage:
    python3 verify/verify_timelines.py

Also exposes ``build() -> Chapter`` for integration with run_all.py.
"""

from __future__ import annotations

import glob
import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework import Chapter, StructuralCheck

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAINS_DIR = os.path.join(BASE_DIR, "docs", "domains")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TimelineViolation:
    file: str
    chapter: int
    earlier_year: int
    later_year: int
    earlier_entry: str
    later_entry: str


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _chapter_num(path: str) -> int:
    m = re.match(r"(\d+)-", os.path.basename(path))
    return int(m.group(1)) if m else 0


def _extract_timeline_blocks(text: str) -> list[str]:
    """Return the raw content of every ``timeline`` mermaid block."""
    blocks = []
    for raw in re.findall(r"```mermaid\n([\s\S]*?)```", text):
        lines = raw.strip().split("\n")
        in_fm = False
        for line in lines:
            s = line.strip()
            if s == "---":
                in_fm = not in_fm
                continue
            if in_fm or s.startswith("%%{") or not s:
                continue
            if s.split()[0] == "timeline":
                blocks.append(raw)
            break
    return blocks


def _parse_year(token: str) -> int | None:
    """Extract an integer year from a token such as '1905', '1920s', 'c.1850'."""
    # Strip prefixes: c., ca., ~, approx., etc.
    token = re.sub(r"^[^0-9]*", "", token)
    # Take the first 4-digit sequence
    m = re.search(r"\b(\d{4})\b", token)
    if m:
        return int(m.group(1))
    # 3-digit century entry like "400 BC" — skip
    return None


def _extract_timeline_entries(block: str) -> list[tuple[int, str]]:
    """Return list of (year, raw_entry_text) from a timeline block.

    Timeline event syntax: ``    YEAR : Description`` or ``    YEAR : Desc -- Detail``
    Also handles section headers: ``    section LABEL``
    """
    entries: list[tuple[int, str]] = []
    for line in block.split("\n"):
        stripped = line.strip()
        # Skip directives, blank lines, title lines
        if not stripped or stripped.startswith("%%{") or stripped.startswith("title"):
            continue
        if stripped.startswith("section"):
            continue
        # Match ``YEAR : ...`` pattern
        m = re.match(r"^(\S+)\s*:", stripped)
        if m:
            year = _parse_year(m.group(1))
            if year is not None:
                entries.append((year, stripped))
    return entries


# ---------------------------------------------------------------------------
# Chronology check
# ---------------------------------------------------------------------------

def check_chronological_order(domain_files: list[str]) -> list[TimelineViolation]:
    """Return all chronological-order violations across all timeline blocks."""
    violations: list[TimelineViolation] = []

    for fp in sorted(domain_files):
        ch = _chapter_num(fp)
        with open(fp, encoding="utf-8") as f:
            text = f.read()

        for block in _extract_timeline_blocks(text):
            entries = _extract_timeline_entries(block)
            if len(entries) < 2:
                continue

            for i in range(1, len(entries)):
                prev_year, prev_text = entries[i - 1]
                curr_year, curr_text = entries[i]
                if curr_year < prev_year:
                    violations.append(TimelineViolation(
                        file=fp,
                        chapter=ch,
                        earlier_year=curr_year,
                        later_year=prev_year,
                        earlier_entry=curr_text[:80],
                        later_entry=prev_text[:80],
                    ))

    return violations


# ---------------------------------------------------------------------------
# Framework integration
# ---------------------------------------------------------------------------

def build() -> Chapter:
    """Build a Chapter of chronological-order checks for run_all.py."""
    ch = Chapter(203, "Timeline Chronological Order")

    domain_files = sorted(glob.glob(os.path.join(DOMAINS_DIR, "*.md")))
    violations = check_chronological_order(domain_files)

    def predicate(_v: list[TimelineViolation] = violations) -> tuple[bool, str]:
        if not _v:
            return True, ""
        msgs = []
        for v in _v[:8]:
            msgs.append(
                f"Ch{v.chapter:02d} {os.path.basename(v.file)}: "
                f"year {v.earlier_year} appears after {v.later_year} "
                f"('{v.earlier_entry[:50]}' after '{v.later_entry[:50]}')"
            )
        suffix = f" (+{len(_v)-8} more)" if len(_v) > 8 else ""
        return False, f"{len(_v)} out-of-order timeline entries:\n" + "\n".join(msgs) + suffix

    ch.add(StructuralCheck(
        label="All timeline entries appear in non-decreasing year order",
        section="timeline",
        predicate=predicate,
    ))

    # Also report total timelines checked
    total_timelines = sum(
        len(_extract_timeline_blocks(open(fp, encoding="utf-8").read()))
        for fp in domain_files
    )
    ch.add(StructuralCheck(
        label=f"Timeline coverage: {total_timelines} timeline blocks across {len(domain_files)} chapters",
        section="timeline",
        predicate=lambda _t=total_timelines: (
            _t >= 48,
            f"Expected >=48 timelines (one per chapter), found {_t}"
        ),
    ))

    return ch


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from framework import Report

    chapter = build()
    chapter.run()

    report = Report()
    report.add_chapter(chapter)
    report.print_console()

    raise SystemExit(report.exit_code)
