#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify notation consistency across all 48 Evenwicht chapters.

Checks:
  1. Parse the notation table in Section 3 (## 3. Notation & Conventions)
     of every chapter, extracting each row's LaTeX symbol and meaning text.
  2. Build a global registry mapping each symbol to the chapters and
     meanings in which it appears.
  3. For symbols appearing in 3 or more chapters, detect conflicting
     meanings via keyword overlap analysis.
  4. Report symbols with conflicting meanings, grouped by symbol.
  5. Exclude universal symbols from conflict detection.  Single Latin
     letters (a-z, A-Z), common Greek letters, and bold/variant forms
     are all standard mathematical practice — every textbook reuses
     these across chapters.  Only compound symbols (e.g. $R_0$,
     $\\Delta t$, $\\hat{\\beta}$) are checked for genuine conflicts.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAIN_DIR = PROJECT_ROOT / "docs" / "domains"

# Universal symbols excluded from conflict detection — these are expected
# to have context-dependent meanings across chapters.  Single Latin
# letters and common Greek letters naturally carry different meanings in
# different mathematical domains (e.g. λ for eigenvalue vs wavelength vs
# rate parameter).  Only compound symbols are worth checking.
#
# Values are stored in *normalised* form (as produced by normalise_symbol).
UNIVERSAL_SYMBOLS: set[str] = {
    # All single lowercase Latin letters (a-z)
    *"abcdefghijklmnopqrstuvwxyz",
    # All single uppercase Latin letters (A-Z)
    *"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    # Common Greek letters (normalised form keeps the backslash command)
    r"\alpha", r"\beta", r"\gamma", r"\delta", r"\epsilon",
    r"\varepsilon", r"\lambda", r"\mu", r"\sigma", r"\tau",
    r"\theta", r"\omega", r"\rho", r"\phi", r"\pi", r"\nu",
    r"\eta", r"\xi",
    # Bold / mathbf / boldsymbol single-letter variants (normalised:
    # braces are stripped so \mathbf{x} -> \mathbfx, etc.)
    r"\boldsymbolx", r"\mathbfx", r"\mathbfy", r"\mathbfv",
}

# Minimum number of chapters in which a symbol must appear before we
# check for meaning consistency.
MIN_CHAPTERS = 3

# Two meanings are considered compatible when the fraction of shared
# keywords meets or exceeds this threshold.
SIMILARITY_THRESHOLD = 0.30

# ── Regexes ─────────────────────────────────────────────────────────────

# Match | $...$ | meaning text |  (a single notation table row)
TABLE_ROW_RE = re.compile(
    r"^\|\s*(\$[^$]+\$)\s*\|\s*(.+?)\s*\|$",
    re.MULTILINE,
)

# Separator row:  |---|---|
TABLE_SEP_RE = re.compile(r"^\|[-\s|:]+\|$", re.MULTILINE)

# Strip LaTeX command noise for canonical comparison.
LATEX_CMD_RE = re.compile(r"\\(?:text|mathrm|operatorname|mathbb|mathcal)\b\s*")


def get_chapter_files() -> list[Path]:
    """Return all numbered domain chapter files, sorted."""
    return sorted(DOMAIN_DIR.glob("[0-9]*.md"))


def extract_chapter_number(path: Path) -> int:
    """Extract the leading chapter number from a filename."""
    m = re.match(r"(\d+)", path.name)
    return int(m.group(1)) if m else 0


def section_text(text: str, section_num: int) -> str:
    """Extract the text between ## N. ... and the next ## heading."""
    heading = re.search(
        rf"^## {section_num}\.\s+[^\n]+$",
        text,
        re.MULTILINE,
    )
    if not heading:
        return ""
    start = heading.end() + 1
    next_h2 = re.search(r"^## \d+\.\s", text[start:], re.MULTILINE)
    return text[start : start + next_h2.start()] if next_h2 else text[start:]


def normalise_symbol(raw: str) -> str:
    """Produce a canonical form of a LaTeX symbol for grouping.

    Strips outer $...$ delimiters, removes whitespace, and drops
    decorative LaTeX commands (\\text, \\mathrm, etc.) so that
    superficial formatting differences do not prevent matching.
    """
    s = raw.strip()
    if s.startswith("$") and s.endswith("$"):
        s = s[1:-1]
    s = LATEX_CMD_RE.sub("", s)
    s = re.sub(r"[{}\s]", "", s)
    return s


# Regex matching any \mathbf or \boldsymbol wrapping a single letter
# after normalisation (braces stripped, so \mathbf{x} -> \mathbfx).
_BOLD_SINGLE_RE = re.compile(r"^\\(?:mathbf|boldsymbol)([A-Za-z])$")


def is_universal(symbol: str) -> bool:
    """Return True if *symbol* is a universal/context-dependent symbol.

    A symbol is universal if it is:
    - A single Latin letter (a-z, A-Z),
    - A common Greek letter (\\alpha, \\lambda, etc.),
    - A bold/variant wrapping of a single letter (\\mathbf{x}, etc.), or
    - A comma-separated list where every part is universal.
    """
    canon = normalise_symbol(symbol)
    # Match bare single-letter symbols possibly with comma-separated
    # variants like "f, g, h" or "x, y, z".
    parts = [p.strip().rstrip(",") for p in canon.split(",")]
    return all(_is_universal_part(p) for p in parts if p)


def _is_universal_part(canon: str) -> bool:
    """Check a single normalised symbol against the allow-list."""
    if canon in UNIVERSAL_SYMBOLS:
        return True
    # Catch any \mathbf / \boldsymbol wrapping a single letter, even if
    # not explicitly listed (e.g. \mathbfz).
    if _BOLD_SINGLE_RE.match(canon):
        return True
    return False


def extract_notation_rows(text: str) -> list[tuple[str, str]]:
    """Parse the notation table from Section 3 text.

    Returns a list of (symbol_latex, meaning_text) tuples.
    """
    rows: list[tuple[str, str]] = []
    for m in TABLE_ROW_RE.finditer(text):
        symbol = m.group(1).strip()
        meaning = m.group(2).strip()
        # Skip header/separator rows that slip through.
        if meaning.lower() in ("meaning", "------", "-------"):
            continue
        if TABLE_SEP_RE.match(m.group(0)):
            continue
        rows.append((symbol, meaning))
    return rows


def meaning_keywords(meaning: str) -> set[str]:
    """Extract meaningful keywords from a meaning string.

    Lowercases, strips LaTeX fragments, punctuation, and common stop
    words to produce a set suitable for overlap comparison.
    """
    stop_words = {
        "a", "an", "the", "of", "in", "for", "and", "or", "on", "at",
        "to", "is", "by", "as", "with", "from", "that", "this", "its",
        "are", "be", "it", "all", "per", "when", "if", "any", "each",
        "e.g.", "i.e.", "where", "such",
    }
    # Remove inline LaTeX.
    cleaned = re.sub(r"\$[^$]*\$", " ", meaning)
    # Remove markdown formatting.
    cleaned = re.sub(r"[*_`|\\]", " ", cleaned)
    # Remove punctuation except hyphens within words.
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", " ", cleaned)
    tokens = cleaned.lower().split()
    return {w for w in tokens if w not in stop_words and len(w) > 1}


def meanings_compatible(meaning_a: str, meaning_b: str) -> bool:
    """Return True if two meaning strings are semantically compatible.

    Uses keyword overlap: if the intersection of keywords relative to
    the smaller set meets or exceeds SIMILARITY_THRESHOLD, the meanings
    are considered compatible.
    """
    kw_a = meaning_keywords(meaning_a)
    kw_b = meaning_keywords(meaning_b)
    if not kw_a or not kw_b:
        return True  # Cannot compare — treat as compatible.
    overlap = len(kw_a & kw_b)
    min_size = min(len(kw_a), len(kw_b))
    return (overlap / min_size) >= SIMILARITY_THRESHOLD


def cluster_meanings(
    entries: list[tuple[int, str]],
) -> list[list[tuple[int, str]]]:
    """Group chapter/meaning pairs into compatibility clusters.

    Each cluster contains meanings that are mutually compatible.  If
    only one cluster results, all meanings are consistent.
    """
    clusters: list[list[tuple[int, str]]] = []
    for ch, meaning in entries:
        placed = False
        for cluster in clusters:
            # Compatible with the first entry in the cluster is enough;
            # transitivity within a cluster is assumed.
            if meanings_compatible(cluster[0][1], meaning):
                cluster.append((ch, meaning))
                placed = True
                break
        if not placed:
            clusters.append([(ch, meaning)])
    return clusters


def main() -> int:
    files = get_chapter_files()
    if not files:
        print(f"ERROR: No domain files found in {DOMAIN_DIR}")
        return 1

    # ── Phase 1: Parse notation tables ──────────────────────────────────
    registry: dict[str, list[tuple[int, str]]] = defaultdict(list)
    chapters_parsed = 0
    total_symbols = 0
    chapters_without_table: list[str] = []

    for path in files:
        ch_num = extract_chapter_number(path)
        text = path.read_text(encoding="utf-8")
        notation = section_text(text, 3)
        rows = extract_notation_rows(notation)
        if not rows:
            chapters_without_table.append(path.name)
            continue
        chapters_parsed += 1
        for symbol, meaning in rows:
            canon = normalise_symbol(symbol)
            registry[canon].append((ch_num, meaning))
            total_symbols += 1

    # ── Phase 2: Detect conflicts ───────────────────────────────────────
    conflicts: dict[str, list[list[tuple[int, str]]]] = {}
    symbols_checked = 0

    for symbol, entries in sorted(registry.items()):
        if len(entries) < MIN_CHAPTERS:
            continue
        if is_universal(symbol):
            continue
        symbols_checked += 1
        clusters = cluster_meanings(entries)
        if len(clusters) > 1:
            conflicts[symbol] = clusters

    # ── Output ──────────────────────────────────────────────────────────
    print("=" * 78)
    print("NOTATION CONSISTENCY — Evenwicht")
    print("=" * 78)
    print()

    # Statistics
    unique_symbols = len(registry)
    multi_chapter = sum(
        1 for entries in registry.values() if len(entries) >= MIN_CHAPTERS
    )
    universal_skipped = sum(
        1 for sym, entries in registry.items()
        if len(entries) >= MIN_CHAPTERS and is_universal(sym)
    )

    print(f"  Chapters parsed:                    {chapters_parsed}/{len(files)}")
    print(f"  Total notation rows:                {total_symbols}")
    print(f"  Unique symbols:                     {unique_symbols}")
    print(f"  Symbols in {MIN_CHAPTERS}+ chapters:              {multi_chapter}")
    print(f"  Universal (skipped):                {universal_skipped}")
    print(f"  Symbols checked for conflicts:      {symbols_checked}")
    print()

    # Chapters without a notation table
    if chapters_without_table:
        print("=" * 78)
        print(f"CHAPTERS WITHOUT NOTATION TABLE ({len(chapters_without_table)})")
        print("=" * 78)
        for name in chapters_without_table:
            print(f"  - {name}")
        print()

    # Most widely shared symbols
    print("=" * 78)
    print("MOST WIDELY SHARED SYMBOLS (5+ chapters)")
    print("=" * 78)
    print()
    print(f"  {'Symbol':<30} {'Chapters':>8}")
    print("  " + "-" * 40)
    for symbol, entries in sorted(
        registry.items(),
        key=lambda kv: (-len(kv[1]), kv[0]),
    ):
        if len(entries) >= 5:
            ch_list = ", ".join(str(ch) for ch, _ in entries)
            display = f"${symbol}$"
            print(f"  {display:<30} {len(entries):>4}  [{ch_list}]")
    print()

    # Conflicts
    issues: list[str] = []

    if conflicts:
        print("=" * 78)
        print(f"CONFLICTING MEANINGS DETECTED ({len(conflicts)} symbols)")
        print("=" * 78)
        for symbol, clusters in sorted(conflicts.items()):
            display = f"${symbol}$"
            print(f"\n  {display}")
            for idx, cluster in enumerate(clusters, 1):
                sample_meaning = cluster[0][1]
                ch_nums = [str(ch) for ch, _ in cluster]
                # Truncate long meanings for readability.
                if len(sample_meaning) > 70:
                    sample_meaning = sample_meaning[:67] + "..."
                print(f"    Group {idx} (ch {', '.join(ch_nums)}):")
                print(f"      {sample_meaning}")
            issues.append(
                f"${symbol}$: {len(clusters)} conflicting meaning groups "
                f"across {sum(len(c) for c in clusters)} chapters"
            )
        print()
    else:
        print("No conflicting meanings detected among shared symbols.")
        print()

    # ── Summary ─────────────────────────────────────────────────────────
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Chapters parsed:               {chapters_parsed}/{len(files)}")
    print(f"  Symbols checked:               {symbols_checked}")
    print(f"  Conflicts found:               {len(conflicts)}")
    print(f"  Total issues:                  {len(issues)}")
    print()

    if issues:
        for issue in issues:
            print(f"  ISSUE: {issue}")
        print()
        return 1

    print("All shared notation symbols are consistent across chapters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
