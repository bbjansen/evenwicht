#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify glossary completeness across all 48 chapters.

Checks:
  1. Bold terms in Core Theory that are missing from the Glossary.
  2. Glossary entries that never appear in the chapter text (orphaned).

Bold terms that are clearly structural formatting (Definition, Theorem,
Example, Proof, Note, Remark, Prerequisites, Problem, Output, Input,
Corollary, Lemma, Proposition, Algorithm) or numbered labels like
"Definition 3.1" are excluded from the check.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# Bold terms that are clearly formatting / structural labels, not glossary candidates.
SKIP_TERMS: set[str] = {
    "output", "input", "proof", "example", "note", "prerequisites",
    "problem", "remark", "hint", "solution", "step", "case",
    "warning", "important", "tip", "observation", "summary",
    # Mathematical label words used without numbers (e.g., bare "**Definition**")
    "definition", "theorem", "lemma", "corollary", "proposition", "algorithm",
    "axiom", "postulate", "claim", "conjecture", "fact", "result",
    "convention", "notation", "rule", "property",
    # Proof sub-step labels
    "caveat", "conclusion", "part", "base", "inductive", "claim",
    # Subheading starters
    "properties",
}

# Regex for numbered labels like "Definition 3.1", "Theorem 3.5a", etc.
NUMBERED_LABEL_RE = re.compile(
    r"^(Definition|Theorem|Example|Corollary|Lemma|Proposition|Remark|"
    r"Algorithm|Property|Notation|Convention|Rule|Axiom|Postulate|"
    r"Claim|Conjecture|Fact|Result)(\s+\d|\s*$)",
    re.IGNORECASE,
)

# Proof step patterns — bold phrases used to label sub-steps in induction proofs etc.
PROOF_STEP_RE = re.compile(
    r"^(Base cases?|Inductive steps?|Part\s+\(|Step\s+\d|Case\s+\d)",
    re.IGNORECASE,
)

# Bold terms that are diagram titles or section-internal headings (multi-word
# phrases containing colons or clearly not glossary material).
DIAGRAM_TITLE_RE = re.compile(r".*:.*")


def normalize(term: str) -> str:
    """Lowercase, strip trailing punctuation and whitespace."""
    return term.strip().lower().rstrip(".,;:!?")


def singularize(term: str) -> str:
    """Naive singularization: strip trailing 's' if present."""
    if term.endswith("ies"):
        return term[:-3] + "y"
    if term.endswith("ses") or term.endswith("xes") or term.endswith("zes"):
        return term[:-2]
    if term.endswith("s") and not term.endswith("ss"):
        return term[:-1]
    return term


def match_terms(bold: str, glossary_terms: set[str]) -> bool:
    """Check if a bold term matches any glossary term (case-insensitive, plural-aware)."""
    b = normalize(bold)
    if b in glossary_terms:
        return True
    # Try singular/plural variations
    bs = singularize(b)
    if bs in glossary_terms:
        return True
    # Check if any glossary term starts with the bold term (e.g., "PDF" vs "PDF (probability density function)")
    for g in glossary_terms:
        gs = singularize(g)
        if b == gs or bs == g or bs == gs:
            return True
        # Check if bold term is a substring match at word boundary
        if b in g or g in b:
            return True
    return False


def is_skip_term(term: str) -> bool:
    """Return True if this bold term should be skipped."""
    n = normalize(term)
    # Check exact word match (first word) against SKIP_TERMS
    first_word = n.split()[0] if n.split() else n
    if first_word in SKIP_TERMS or n in SKIP_TERMS:
        return True
    if NUMBERED_LABEL_RE.match(term):
        return True
    if PROOF_STEP_RE.match(term):
        return True
    # Skip single-character terms (like bold variable names)
    if len(n) <= 1:
        return True
    # Skip terms that are purely numeric
    if re.match(r"^\d+(\.\d+)?[a-z]?$", n):
        return True
    # Skip terms that are multi-word "Properties of X" headings
    if n.startswith("properties of "):
        return True
    # Skip parenthetical labels like (a), (b), (1), (Weak duality), etc.
    if re.match(r"^\([^)]*\)$", n):
        return True
    # Skip numbered proof steps like "(1) Symmetry...", "(2) Smallest eigenvalue.", etc.
    if re.match(r"^\(\d+\)", n):
        return True
    return False


def extract_section(text: str, section_name: str) -> str:
    """Extract content between a '## N. <section_name>' header and the next '## N.' header."""
    pattern = rf"^## \d+\.\s+{re.escape(section_name)}\s*$"
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(pattern, line):
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^## \d+\.", lines[i]):
            end = i
            break
    return "\n".join(lines[start:end])


def extract_bold_terms(text: str) -> list[str]:
    """Extract all **bold terms** from text."""
    return re.findall(r"\*\*([^*]+)\*\*", text)


def extract_glossary_terms(glossary_text: str) -> dict[str, str]:
    """Extract glossary entries as {normalized_term: original_term}."""
    entries: dict[str, str] = {}
    for line in glossary_text.split("\n"):
        m = re.match(r"^- \*\*([^*]+)\*\*", line)
        if m:
            raw = m.group(1)
            # Strip trailing parenthetical like ($\Omega$) or (AST)
            clean = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
            entries[normalize(clean)] = raw
    return entries


def process_chapter(filepath: Path) -> tuple[list[str], list[str]]:
    """Process a single chapter file.

    Returns:
        (missing_from_glossary, orphaned_glossary)
    """
    text = filepath.read_text(encoding="utf-8")

    core_theory = extract_section(text, "Core Theory")
    glossary_text = extract_section(text, "Glossary")

    if not core_theory:
        return [], []
    if not glossary_text:
        return [], []

    bold_terms = extract_bold_terms(core_theory)
    glossary_entries = extract_glossary_terms(glossary_text)
    glossary_normalized: set[str] = set(glossary_entries.keys())

    # 1. Check bold terms in Core Theory against Glossary
    missing: list[str] = []
    seen: set[str] = set()
    for term in bold_terms:
        if is_skip_term(term):
            continue
        # Skip diagram titles (contain colons and are multi-word)
        if DIAGRAM_TITLE_RE.match(term) and len(term.split()) > 3:
            continue
        n = normalize(term)
        if n in seen:
            continue
        seen.add(n)
        if not match_terms(term, glossary_normalized):
            missing.append(term)

    # 2. Check for orphaned glossary entries (never mentioned in chapter text)
    orphaned: list[str] = []
    for orig_term in glossary_entries.values():
        # Check if the term appears anywhere in the chapter text (outside the glossary itself)
        text_without_glossary = text[:text.find(glossary_text)] if glossary_text in text else text
        text_lower = text_without_glossary.lower()
        # Normalise dashes: treat Unicode en-dash (–) and double-hyphen (--) as equivalent
        text_norm = text_lower.replace("–", "--")
        # Clean the term for searching
        search_term = re.sub(r"\s*\([^)]*\)\s*$", "", orig_term).strip().lower()
        search_term_norm = search_term.replace("–", "--")
        if search_term_norm not in text_norm:
            # Also try singular
            singular = singularize(search_term_norm)
            if singular not in text_norm:
                orphaned.append(orig_term)

    return missing, orphaned


def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}")
        return 1

    print(f"Scanning {len(chapter_files)} chapters for glossary completeness...\n")

    total_missing = 0
    total_orphaned = 0
    chapters_with_issues = 0

    for filepath in chapter_files:
        missing, orphaned = process_chapter(filepath)
        if missing or orphaned:
            chapters_with_issues += 1
            print(f"  {filepath.stem}")
            if missing:
                for term in missing:
                    print(f"    MISSING from glossary: \"{term}\"")
                total_missing += len(missing)
            if orphaned:
                for term in orphaned:
                    print(f"    ORPHANED glossary entry: \"{term}\"")
                total_orphaned += len(orphaned)
            print()

    print("=" * 60)
    print(f"Chapters scanned:        {len(chapter_files)}")
    print(f"Chapters with issues:    {chapters_with_issues}")
    print(f"Missing glossary terms:  {total_missing}")
    print(f"Orphaned glossary terms: {total_orphaned}")
    print("=" * 60)

    if total_missing > 0 or total_orphaned > 0:
        return 1
    print("\nAll glossary checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
