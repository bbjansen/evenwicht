#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify exercise difficulty categorisation across all Evenwicht chapters.

Checks whether exercises are correctly ordered by difficulty tier
(Routine < Intermediate < Challenging) using a proxy difficulty score.

Scoring heuristics:
  - Word count (longer exercises tend to be harder)
  - Number of sub-parts (a), (b), (c) etc.
  - Presence of rigour keywords: "prove", "show that", "derive", "establish"
  - Presence of computational keywords: "compute", "calculate", "find", "evaluate"
  - Cross-chapter references (referencing other chapters = harder)
  - Presence of "Hint:" (author felt a hint was needed = harder)

Flags:
  1. Chapters where Routine median >= Intermediate median or
     Intermediate median >= Challenging median.
  2. Individual exercises that appear miscategorised (e.g. a Routine exercise
     scoring above the chapter's Challenging median).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# ── Scoring constants ──────────────────────────────────────────────────────

# Weight applied to each word in the exercise body.
W_WORD = 1.0

# Bonus per sub-part: (a), (b), ...
W_SUBPART = 8.0

# Rigour keywords push the score up.
RIGOUR_KEYWORDS = [
    r"\bprove\b", r"\bshow\s+that\b", r"\bderive\b", r"\bestablish\b",
    r"\bdemonstrate\b", r"\bjustify\b", r"\bstructural\s+induction\b",
]
W_RIGOUR = 15.0

# Computational keywords are neutral (no bonus or penalty).
COMPUTE_KEYWORDS = [
    r"\bcompute\b", r"\bcalculate\b", r"\bfind\b", r"\bevaluate\b",
    r"\bdetermine\b", r"\bsimplify\b",
]
W_COMPUTE = -3.0

# Cross-chapter references imply broader knowledge.
CROSS_REF_RE = re.compile(
    r"(?:Chapter|Ch\.?)\s+\d+|"
    r"(?:Theorem|Definition|Lemma|Proposition|Algorithm|Example|Exercise)\s+\d+\.\d+",
)
W_CROSS_REF = 10.0

# Hints indicate the author considered the problem non-trivial.
HINT_RE = re.compile(r"\bHint\b\s*:", re.IGNORECASE)
W_HINT = 6.0

# ── Regex patterns ─────────────────────────────────────────────────────────

# Matches the start of an exercise: **Exercise N.M** or **Exercise N.M.**
EXERCISE_RE = re.compile(r"\*\*Exercise\s+(\d+)\.(\d+)\*?\*?\.?")

# Matches sub-part labels that appear as list items or sentence starters.
# Excludes f(x), g(x) etc. by requiring start-of-line or bullet prefix.
SUBPART_RE = re.compile(r"(?:^|\n)\s*[-*]?\s*\([a-h]\)")

# Section 10 heading.
SECTION_10_RE = re.compile(r"^## 10\.\s+Exercises", re.MULTILINE)

# Tier headings within the exercises section.
TIER_RE = re.compile(r"^###\s+(Routine|Intermediate|Challenging)\s*$", re.MULTILINE)


# ── Data structures ────────────────────────────────────────────────────────

TIERS = ("Routine", "Intermediate", "Challenging")


@dataclass
class Exercise:
    label: str          # e.g. "Exercise 10.3"
    tier: str           # Routine | Intermediate | Challenging
    text: str           # full body text of the exercise
    score: float = 0.0


@dataclass
class ChapterResult:
    file: str
    chapter: int
    exercises: list[Exercise] = field(default_factory=list)
    tier_medians: dict[str, float] = field(default_factory=dict)
    tier_issues: list[str] = field(default_factory=list)
    miscat_issues: list[str] = field(default_factory=list)


# ── Scoring ────────────────────────────────────────────────────────────────

def score_exercise(text: str) -> float:
    """Compute a difficulty proxy score for a single exercise."""
    score = 0.0

    # Word count (strip math and markdown markup for cleaner count).
    words = re.sub(r"\$[^$]+\$", " MATH ", text)
    words = re.sub(r"[*_`#|>]", " ", words)
    word_count = len(words.split())
    score += word_count * W_WORD

    # Sub-parts.
    subparts = len(SUBPART_RE.findall(text))
    score += subparts * W_SUBPART

    # Rigour keywords.
    for pat in RIGOUR_KEYWORDS:
        score += len(re.findall(pat, text, re.IGNORECASE)) * W_RIGOUR

    # Computational keywords (mild negative offset).
    for pat in COMPUTE_KEYWORDS:
        score += len(re.findall(pat, text, re.IGNORECASE)) * W_COMPUTE

    # Cross-chapter references.
    score += len(CROSS_REF_RE.findall(text)) * W_CROSS_REF

    # Hints.
    score += len(HINT_RE.findall(text)) * W_HINT

    return score


# ── Parsing ────────────────────────────────────────────────────────────────

def extract_exercises(text: str) -> list[Exercise]:
    """Extract exercises grouped by tier from Section 10."""
    sec_match = SECTION_10_RE.search(text)
    if not sec_match:
        return []

    sec_start = sec_match.start()
    next_h2 = re.search(r"^## \d+\.", text[sec_match.end():], re.MULTILINE)
    sec_end = sec_match.end() + next_h2.start() if next_h2 else len(text)
    section = text[sec_start:sec_end]

    # Find tier boundaries.
    tier_matches = list(TIER_RE.finditer(section))
    if not tier_matches:
        return []

    # Build tier spans: (tier_name, start_offset, end_offset).
    tier_spans: list[tuple[str, int, int]] = []
    for i, m in enumerate(tier_matches):
        start = m.end()
        end = tier_matches[i + 1].start() if i + 1 < len(tier_matches) else len(section)
        tier_spans.append((m.group(1), start, end))

    exercises: list[Exercise] = []

    for tier_name, span_start, span_end in tier_spans:
        tier_text = section[span_start:span_end]

        # Split on exercise headings.
        ex_starts = list(EXERCISE_RE.finditer(tier_text))
        for i, ex_match in enumerate(ex_starts):
            prefix = ex_match.group(1)
            number = ex_match.group(2)
            label = f"Exercise {prefix}.{number}"

            body_start = ex_match.start()
            body_end = ex_starts[i + 1].start() if i + 1 < len(ex_starts) else len(tier_text)
            body = tier_text[body_start:body_end].strip()

            ex = Exercise(label=label, tier=tier_name, text=body)
            ex.score = score_exercise(body)
            exercises.append(ex)

    return exercises


def get_chapter_files() -> list[Path]:
    return sorted(DOCS_DIR.glob("[0-9]*.md"))


def extract_chapter_number(path: Path) -> int:
    m = re.match(r"(\d+)", path.name)
    return int(m.group(1)) if m else 0


# ── Analysis ───────────────────────────────────────────────────────────────

def analyse_chapter(path: Path) -> ChapterResult:
    text = path.read_text(encoding="utf-8")
    ch_num = extract_chapter_number(path)
    exercises = extract_exercises(text)

    result = ChapterResult(file=path.name, chapter=ch_num, exercises=exercises)

    # Compute per-tier medians.
    for tier in TIERS:
        scores = [e.score for e in exercises if e.tier == tier]
        if scores:
            result.tier_medians[tier] = median(scores)

    # Check tier ordering: Routine < Intermediate < Challenging.
    for lo, hi in [("Routine", "Intermediate"), ("Intermediate", "Challenging")]:
        if lo in result.tier_medians and hi in result.tier_medians:
            if result.tier_medians[lo] >= result.tier_medians[hi]:
                result.tier_issues.append(
                    f"{lo} median ({result.tier_medians[lo]:.1f}) "
                    f">= {hi} median ({result.tier_medians[hi]:.1f})"
                )

    # Flag individual miscategorised exercises.
    challenging_med = result.tier_medians.get("Challenging")
    routine_med = result.tier_medians.get("Routine")

    for ex in exercises:
        if ex.tier == "Routine" and challenging_med is not None:
            if ex.score >= challenging_med:
                result.miscat_issues.append(
                    f"{ex.label} ({ex.tier}, score={ex.score:.1f}) "
                    f">= Challenging median ({challenging_med:.1f})"
                )
        if ex.tier == "Challenging" and routine_med is not None:
            if ex.score <= routine_med:
                result.miscat_issues.append(
                    f"{ex.label} ({ex.tier}, score={ex.score:.1f}) "
                    f"<= Routine median ({routine_med:.1f})"
                )

    return result


# ── Output ─────────────────────────────────────────────────────────────────

def main() -> int:
    files = get_chapter_files()
    if not files:
        print(f"ERROR: No domain files found in {DOCS_DIR}")
        return 1

    results = [analyse_chapter(f) for f in files]

    total_tier_issues = 0
    total_miscat_issues = 0
    chapters_with_problems = 0

    # ── Header ──────────────────────────────────────────────────────────
    print("=" * 78)
    print("EXERCISE DIFFICULTY VERIFICATION — Evenwicht")
    print("=" * 78)
    print()

    # ── Per-chapter score overview ──────────────────────────────────────
    print(
        f"{'Chapter':<35} {'Routine':>8} {'Interm.':>8} "
        f"{'Chall.':>8}  {'Status'}"
    )
    print("-" * 78)

    for r in results:
        if not r.exercises:
            print(f"  {r.file:<33} {'—':>8} {'—':>8} {'—':>8}  SKIP (no exercises)")
            continue

        rout = f"{r.tier_medians['Routine']:.0f}" if "Routine" in r.tier_medians else "—"
        intr = f"{r.tier_medians['Intermediate']:.0f}" if "Intermediate" in r.tier_medians else "—"
        chal = f"{r.tier_medians['Challenging']:.0f}" if "Challenging" in r.tier_medians else "—"

        has_issues = bool(r.tier_issues or r.miscat_issues)
        status = "FAIL" if has_issues else "OK"
        if has_issues:
            chapters_with_problems += 1

        total_tier_issues += len(r.tier_issues)
        total_miscat_issues += len(r.miscat_issues)

        print(f"  {r.file:<33} {rout:>8} {intr:>8} {chal:>8}  {status}")

    # ── Tier ordering violations ────────────────────────────────────────
    tier_violators = [r for r in results if r.tier_issues]
    if tier_violators:
        print()
        print("=" * 78)
        print(f"TIER ORDERING VIOLATIONS ({len(tier_violators)} chapters)")
        print("=" * 78)
        for r in tier_violators:
            for issue in r.tier_issues:
                print(f"  {r.file}: {issue}")

    # ── Miscategorised exercises ────────────────────────────────────────
    miscat_chapters = [r for r in results if r.miscat_issues]
    if miscat_chapters:
        print()
        print("=" * 78)
        print(f"POTENTIALLY MISCATEGORISED EXERCISES ({total_miscat_issues} total)")
        print("=" * 78)
        for r in miscat_chapters:
            for issue in r.miscat_issues:
                print(f"  {r.file}: {issue}")

    # ── Detailed per-exercise scores (only for chapters with issues) ───
    problem_chapters = [r for r in results if r.tier_issues or r.miscat_issues]
    if problem_chapters:
        print()
        print("=" * 78)
        print("EXERCISE SCORE DETAIL (flagged chapters only)")
        print("=" * 78)
        for r in problem_chapters:
            print(f"\n  {r.file} (Ch. {r.chapter}):")
            for tier in TIERS:
                tier_exs = [e for e in r.exercises if e.tier == tier]
                if tier_exs:
                    scores_str = ", ".join(
                        f"{e.label.split('.')[-1]}={e.score:.0f}" for e in tier_exs
                    )
                    med = r.tier_medians.get(tier, 0)
                    print(f"    {tier:<14} median={med:>6.1f}  [{scores_str}]")

    # ── Summary ─────────────────────────────────────────────────────────
    total_chapters = len(results)
    chapters_with_exercises = sum(1 for r in results if r.exercises)
    total_exercises = sum(len(r.exercises) for r in results)

    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Total chapters scanned:        {total_chapters}")
    print(f"  Chapters with exercises:       {chapters_with_exercises}")
    print(f"  Total exercises scored:        {total_exercises}")
    print(f"  Tier ordering violations:      {total_tier_issues}")
    print(f"  Potentially miscategorised:    {total_miscat_issues}")
    print(f"  Chapters with problems:        {chapters_with_problems}/{chapters_with_exercises}")
    print()

    if total_tier_issues > 0 or total_miscat_issues > 0:
        return 1

    print("All exercise difficulty tiers are correctly ordered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
