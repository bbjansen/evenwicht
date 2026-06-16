#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Extract subject-index terms from all 48 chapter markdown files and produce
an alphabetically organized subject index.

Terms are extracted from three sources in each chapter:
  1. Bold terms in glossary sections (## 13. Glossary / ## Glossary)
  2. Section headings (## and ### headings containing key concepts)
  3. Bold terms in prose (**term** patterns marking first use of a concept)

Source: docs/domains/[0-9]*.md
Output: dist/subject-index.md
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"
OUTPUT_FILE = PROJECT_ROOT / "dist" / "subject-index.md"

# ---------------------------------------------------------------------------
# Heading noise patterns -- headings that are structural, not conceptual
# ---------------------------------------------------------------------------
STRUCTURAL_HEADINGS = {
    "historical context",
    "why this chapter matters",
    "notation & conventions",
    "notation and conventions",
    "core theory",
    "formulas & identities",
    "formulas and identities",
    "algorithms",
    "numerical considerations",
    "implementation notes",
    "worked examples",
    "connections",
    "exercises",
    "references",
    "glossary",
    "module structure",
    "data representation",
    "api signatures",
    "error handling",
    "what is implemented vs. documented only",
    "what is implemented vs documented only",
    "browser vs node",
    "browser vs. node",
}

# Bold-term patterns to exclude -- these are structural labels, not concepts
BOLD_NOISE_PATTERNS = [
    r"^Part\s+[IVXLCDM]+$",            # Part I, Part II, ...
    r"^Prerequisites?$",
    r"^Learning Objectives?$",
    r"^Connections?$",
    r"^Definition\s+\d",                # Definition 3.1
    r"^Theorem\s+\d",                   # Theorem 3.5
    r"^Lemma\s+\d",
    r"^Corollary\s+\d",
    r"^Proposition\s+\d",
    r"^Example\s+\d",                   # Example 3.3a
    r"^Remark\s+\d",
    r"^Proof",
    r"^Algorithm\s+\d",                 # Algorithm 5.1
    r"^F\d+\.\d+",                      # Formula references F4.1
    r"^Step\s+\d",
    r"^Case\s+\d",
    r"^Note$",
    r"^Warning$",
    r"^Hint$",
    r"^Solution$",
    r"^Summary$",
    r"^Overview$",
    r"^Discrete case$",
    r"^Continuous case$",
    r"^Discrete$",
    r"^Continuous$",
    r"^Input$",
    r"^Output$",
    r"^Return$",
    r"^Returns$",
    r"^Parameters?$",
    r"^Complexity$",
    r"^Time complexity$",
    r"^Space complexity$",
    r"^A\d",                            # Appendix labels: A14.1, A3, etc.
    r"^B\.\s",                          # Appendix B. labels
    r"^C\.\s",                          # Appendix C. labels
    r"^[A-Z]\d+\.\d+\s",               # Appendix table labels
    r"^Formula\s+\d",                   # Formula N.M labels
    r"^Foundational$",                  # Difficulty label
    r"^Chapter\s+\d",                   # Chapter references
    r"^Section\s+\d",                   # Section references
    r"^Table\s+\d",                     # Table references
    r"^Figure\s+\d",                    # Figure references
]

# Overly generic terms that should not appear in a subject index
GENERIC_TERMS = {
    "algorithm", "algorithms", "api", "api design principles", "api preview",
    "appendix", "application", "applications", "basic rules", "chapter",
    "conclusion", "context", "description", "discussion", "exercise",
    "formula", "formulas", "function", "functions", "implementation",
    "introduction", "method", "methods", "model", "models", "notation",
    "overview", "problem", "problems", "proof", "proofs", "property",
    "properties", "result", "results", "section", "solution", "solutions",
    "summary", "table", "tables", "theory", "value", "values",
    "accuracy", "module structure", "key insight",
    "algorithm updates", "accuracy targets",
    # Difficulty labels used in exercises
    "beginner", "intermediate", "advanced", "challenge",
    # Iteration step labels
    "iteration 1", "iteration 2", "iteration 3", "iteration 4", "iteration 5",
    # Incomplete/truncated terms
    "adjusted", "inverse", "interpretation",
    # Generic organizational terms
    "internal dependencies", "distributions",
    "activity", "dispatch on `expr.kind`",
}

BOLD_NOISE_RE = [re.compile(p, re.IGNORECASE) for p in BOLD_NOISE_PATTERNS]

# Minimum term length to include
MIN_TERM_LENGTH = 3

# Maximum term length (words) -- very long bold phrases are usually sentences
MAX_TERM_WORDS = 8


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def chapter_number(filepath: Path) -> int:
    """Return the chapter number from a filename like '03-limits-continuity.md'."""
    match = re.match(r"(\d+)", filepath.name)
    return int(match.group(1)) if match else 0


def is_structural_heading(text: str) -> bool:
    """Return True if the heading is a structural/boilerplate section title."""
    normalized = text.strip().lower()
    # Remove leading number prefix like "1. " or "13. "
    normalized = re.sub(r"^\d+\.\s*", "", normalized)
    return normalized in STRUCTURAL_HEADINGS


def is_noise_bold(text: str) -> bool:
    """Return True if the bold term is a structural label, not a concept."""
    stripped = text.strip()
    for pat in BOLD_NOISE_RE:
        if pat.match(stripped):
            return True
    if stripped.lower() in GENERIC_TERMS:
        return True
    return False


def clean_heading_term(heading: str) -> str | None:
    """Extract a clean concept term from a heading line.

    Input:  '### Gaussian Elimination with Partial Pivoting'
    Output: 'Gaussian elimination with partial pivoting'

    Returns None if the heading is structural or an algorithm/example label.
    """
    # Remove markdown heading markers
    text = re.sub(r"^#{2,4}\s+", "", heading.strip())
    # Remove leading section numbers like "4. " or "13. "
    text = re.sub(r"^\d+\.\s*", "", text)

    # Skip appendix headings (A., B., C., A14.1, etc.)
    if re.match(r"^[A-C]\.\s", text) or re.match(r"^[A-C]\d+\.\d+\s", text):
        return None

    # Remove "Algorithm N.M: " prefix and extract the concept after the colon
    alg_match = re.match(r"Algorithm\s+\d+\.\d+:\s*(.+)", text)
    if alg_match:
        text = alg_match.group(1)
    # Also catch "Algorithm N: " without sub-number
    alg_match2 = re.match(r"Algorithm\s+\d+:\s*(.+)", text)
    if alg_match2:
        text = alg_match2.group(1)
    # Remove "Example N.M: " prefix
    ex_match = re.match(r"Example\s+\d+\.\d+[a-z]?:\s*(.+)", text)
    if ex_match:
        text = ex_match.group(1)
        # Example titles are often too specific (e.g. "2x2 Matrix Multiplication")
        # Skip them unless they name a general concept
        if re.search(r"\d\s*[x\u00d7]\s*\d", text):
            return None
    # Also catch "Example N: " without sub-number
    ex_match2 = re.match(r"Example\s+\d+:\s*(.+)", text)
    if ex_match2:
        text = ex_match2.group(1)

    # Remove inline LaTeX
    text = re.sub(r"\$[^$]+\$", "", text).strip()

    if not text or len(text) < MIN_TERM_LENGTH:
        return None

    if is_structural_heading(text):
        return None

    # Skip if the cleaned term is generic
    if text.strip().lower() in GENERIC_TERMS:
        return None

    # Skip numbered exercise/example headings like "5 Galaxy Rotation Curves"
    # These are "### N Title" from worked example sections
    if re.match(r"^\d+\.?\d*\s", text):
        return None

    # Skip backtick-wrapped code identifiers
    if text.startswith("`") or text.endswith("`"):
        return None

    return text


def extract_glossary_terms(text: str) -> list[str]:
    """Extract bold terms from the glossary section."""
    # Find glossary section
    pattern = r"^##\s+(?:\d+\.\s+)?Glossary\s*$"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return []

    start = match.end()
    # Find the next ## heading or end of file
    next_heading = re.search(r"^##\s", text[start:], re.MULTILINE)
    section = text[start:start + next_heading.start()] if next_heading else text[start:]

    terms = []
    # Match glossary entries: "- **Term**: definition" or "- **Term (notation)**: definition"
    for m in re.finditer(r"^-\s+\*\*([^*]+)\*\*", section, re.MULTILINE):
        raw = m.group(1).strip()
        # Remove parenthesized LaTeX notation like "($\Omega$)" or "($P$)"
        clean = re.sub(r"\s*\(\s*\$[^)]*\$\s*\)", "", raw)
        # Remove any remaining inline LaTeX
        clean = re.sub(r"\$[^$]+\$", "", clean).strip()
        # Remove empty parentheses left after LaTeX removal
        clean = re.sub(r"\s*\(\s*\)", "", clean).strip()
        # Remove trailing punctuation
        clean = clean.rstrip(":").strip()
        if clean and len(clean) >= MIN_TERM_LENGTH:
            terms.append(clean)
    return terms


def extract_heading_terms(text: str) -> list[str]:
    """Extract concept terms from ## and ### headings."""
    terms = []
    for m in re.finditer(r"^(#{2,3})\s+(.+)$", text, re.MULTILINE):
        heading_text = m.group(2).strip()
        term = clean_heading_term(f"{m.group(1)} {heading_text}")
        if term:
            terms.append(term)
    return terms


def extract_prose_bold_terms(text: str) -> list[str]:
    """Extract bold terms from prose paragraphs (first-use markers).

    Targets **term** patterns but filters out structural labels
    (definitions, theorems, examples) and very long phrases.
    """
    terms = []
    for m in re.finditer(r"\*\*([^*]+)\*\*", text):
        raw = m.group(1).strip()

        if is_noise_bold(raw):
            continue

        # Skip if it contains line breaks
        if "\n" in raw:
            continue

        # Skip very long phrases (likely not a term)
        if len(raw.split()) > MAX_TERM_WORDS:
            continue

        # Skip single characters or very short
        if len(raw) < MIN_TERM_LENGTH:
            continue

        # Skip if it looks like a formula (all LaTeX)
        if raw.startswith("$") and raw.endswith("$"):
            continue

        # Skip entries that are just numbers or identifiers
        if re.match(r"^[\d.]+$", raw):
            continue

        # Clean up: remove parenthesized LaTeX notation, inline LaTeX, trailing colons
        clean = re.sub(r"\s*\(\s*\$[^)]*\$\s*\)", "", raw)
        clean = re.sub(r"\$[^$]+\$", "", clean).strip()
        clean = re.sub(r"\s*\(\s*\)", "", clean).strip()
        clean = clean.rstrip(":.").strip()

        # Skip if cleaning left nothing useful
        if not clean or len(clean) < MIN_TERM_LENGTH:
            continue

        # Skip if it looks like a sentence (starts with common verbs)
        if re.match(r"^(The|A|An|If|When|For|This|That|It|Note|In|On|At|By|To)\s",
                     clean) and len(clean.split()) > 3:
            continue

        # Skip code identifiers (backtick-wrapped or camelCase function names)
        if clean.startswith("`") or clean.endswith("`"):
            continue
        if "/" in clean and clean.startswith("src/"):
            continue

        terms.append(clean)

    return terms


def normalize_term(term: str) -> str:
    """Normalize a term for deduplication and grouping.

    Lowercases, strips whitespace, and applies minor normalization.
    """
    t = term.strip().lower()
    # Collapse multiple spaces
    t = re.sub(r"\s+", " ", t)
    return t


def merge_singular_plural(index: dict[str, dict]) -> dict[str, dict]:
    """Merge singular and plural forms of terms.

    If both 'eigenvalue' and 'eigenvalues' exist, merge into the singular form.
    """
    # Build a list of normalized keys
    keys = sorted(index.keys())
    merged: set[str] = set()

    for key in keys:
        if key in merged:
            continue

        # Check common plural forms
        plural_forms = []
        if not key.endswith("s"):
            plural_forms.append(key + "s")
            plural_forms.append(key + "es")
        if key.endswith("y") and not key.endswith("ey"):
            plural_forms.append(key[:-1] + "ies")
        if key.endswith("ix"):
            plural_forms.append(key[:-2] + "ices")
        if key.endswith("is"):
            plural_forms.append(key[:-2] + "es")

        for plural in plural_forms:
            if plural in index and plural != key and plural not in merged:
                # Merge plural into singular
                for ch in index[plural]["chapters"]:
                    if ch not in index[key]["chapters"]:
                        index[key]["chapters"].append(ch)
                merged.add(plural)

        # Also check if current key IS a plural and its singular exists
        singular_candidates = []
        if key.endswith("ies") and len(key) > 3:
            singular_candidates.append(key[:-3] + "y")
        elif key.endswith("ices"):
            singular_candidates.append(key[:-4] + "ix")
        elif key.endswith("es") and len(key) > 2:
            singular_candidates.append(key[:-2])
            singular_candidates.append(key[:-1])
        elif key.endswith("s") and not key.endswith("ss") and len(key) > 1:
            singular_candidates.append(key[:-1])

        for singular in singular_candidates:
            if singular in index and singular not in merged and key not in merged:
                # Merge this plural into the singular
                for ch in index[key]["chapters"]:
                    if ch not in index[singular]["chapters"]:
                        index[singular]["chapters"].append(ch)
                merged.add(key)
                break

    # Remove merged entries
    for key in merged:
        del index[key]

    return index


def pick_display_form(term: str) -> str:
    """Choose the display form for a term.

    Capitalizes the first letter, keeps the rest as-is.
    """
    if not term:
        return term
    return term[0].upper() + term[1:]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    source_files = sorted(
        DOCS_DIR.glob("[0-9]*.md"),
        key=lambda p: chapter_number(p),
    )

    if not source_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}", file=sys.stderr)
        sys.exit(1)

    # normalized_term -> { "display": str, "chapters": set[int], "sources": set[str] }
    index: dict[str, dict] = {}

    def add_term(term: str, chapter: int, source: str) -> None:
        """Add a term occurrence to the index."""
        norm = normalize_term(term)
        if not norm:
            return
        if norm not in index:
            index[norm] = {
                "display": term.strip(),
                "chapters": [],
                "sources": set(),
            }
        if chapter not in index[norm]["chapters"]:
            index[norm]["chapters"].append(chapter)
        index[norm]["sources"].add(source)
        # Prefer the display form that looks most like a proper term
        # (glossary > heading > prose; longer > shorter for same source)
        existing = index[norm]["display"]
        if source == "glossary" and "glossary" not in index[norm]["sources"]:
            pass  # sources already updated above
        # Keep the longest non-all-caps display form
        if len(term.strip()) > len(existing) and not term.isupper():
            index[norm]["display"] = term.strip()

    chapters_processed = 0
    glossary_terms_total = 0
    heading_terms_total = 0
    prose_terms_total = 0

    for filepath in source_files:
        chap_num = chapter_number(filepath)
        text = filepath.read_text(encoding="utf-8")
        chapters_processed += 1

        # 1. Glossary terms
        glossary_terms = extract_glossary_terms(text)
        for term in glossary_terms:
            add_term(term, chap_num, "glossary")
        glossary_terms_total += len(glossary_terms)

        # 2. Section headings
        heading_terms = extract_heading_terms(text)
        for term in heading_terms:
            add_term(term, chap_num, "heading")
        heading_terms_total += len(heading_terms)

        # 3. Bold terms in prose
        prose_terms = extract_prose_bold_terms(text)
        for term in prose_terms:
            add_term(term, chap_num, "prose")
        prose_terms_total += len(prose_terms)

    # Merge singular/plural forms
    index = merge_singular_plural(index)

    # Post-processing: clean display forms and remove noise entries
    for norm_key, data in index.items():
        display = data["display"]
        # Clean trailing dashes, em-dashes, colons
        display = re.sub(r"\s*[—–\-:]+\s*$", "", display).strip()
        # Clean trailing "with" or "for" (truncated headings)
        display = re.sub(r"\s+(with|for|of|and|or|the|in|to|from|by|at|on)\s*$",
                         "", display, flags=re.IGNORECASE).strip()
        data["display"] = display

    to_remove = []
    for norm_key, data in index.items():
        display = data["display"]
        # Remove entries with empty parentheses artifact from LaTeX stripping
        if re.search(r"\(\s*\)", display):
            to_remove.append(norm_key)
            continue
        # Remove entries that are generic
        if norm_key in GENERIC_TERMS:
            to_remove.append(norm_key)
            continue
        # Remove entries starting with appendix labels
        if re.match(r"^[a-c]\.\s", norm_key) or re.match(r"^[a-c]\d+\.\d+\s", norm_key):
            to_remove.append(norm_key)
            continue
        # Remove very short generic words (3 chars or less, all alpha)
        if len(norm_key) <= 3 and norm_key.isalpha():
            to_remove.append(norm_key)
            continue
        # Remove entries appearing in too many chapters (>40 = ubiquitous, not useful)
        if len(data["chapters"]) > 40:
            to_remove.append(norm_key)
            continue
        # Remove if display form is empty after cleaning
        if not data["display"] or len(data["display"]) < MIN_TERM_LENGTH:
            to_remove.append(norm_key)
            continue
        # Remove backtick-wrapped code terms and file paths
        if display.startswith("`") or display.endswith("`"):
            to_remove.append(norm_key)
            continue
        if norm_key.startswith("`") or norm_key.endswith("`"):
            to_remove.append(norm_key)
            continue
        # Remove terms that start with a digit (numbered headings that slipped through)
        if norm_key and norm_key[0].isdigit():
            to_remove.append(norm_key)
            continue
        # Remove file path entries
        if "src/" in norm_key or ".ts" in norm_key or ".md" in norm_key:
            to_remove.append(norm_key)
            continue
        # Remove terms starting with dash or em-dash (LaTeX artifacts)
        if display.startswith("-") or display.startswith("\u2014") or display.startswith("\u2013"):
            to_remove.append(norm_key)
            continue
        # Remove terms that are purely non-alphabetic (LaTeX residue)
        if not any(c.isalpha() for c in display):
            to_remove.append(norm_key)
            continue
    for key in to_remove:
        del index[key]

    # Group alphabetically A-Z
    alpha_groups: dict[str, list[tuple[str, list[int]]]] = defaultdict(list)
    for norm_key, data in index.items():
        display = pick_display_form(data["display"])
        chapters = sorted(data["chapters"])
        first_char = display[0].upper() if display else "?"
        if not first_char.isalpha():
            first_char = "#"
        alpha_groups[first_char].append((display, chapters))

    # Sort entries within each letter group
    for letter in alpha_groups:
        alpha_groups[letter].sort(key=lambda x: x[0].lower())

    # Build output
    lines: list[str] = []
    lines.append("# Subject Index")
    lines.append("")

    total_terms = sum(len(entries) for entries in alpha_groups.values())

    # Emit groups A-Z, then # for non-alpha
    for letter in sorted(alpha_groups.keys(), key=lambda c: (c == "#", c)):
        entries = alpha_groups[letter]
        lines.append(f"## {letter}")
        lines.append("")
        for display, chapters in entries:
            ch_str = ", ".join(str(c) for c in chapters)
            lines.append(f"{display}, {ch_str}")
        lines.append("")

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")

    # Summary
    print(f"Processed {chapters_processed} chapters")
    print(f"  Glossary terms extracted: {glossary_terms_total}")
    print(f"  Heading terms extracted:  {heading_terms_total}")
    print(f"  Prose bold terms extracted: {prose_terms_total}")
    print(f"Total unique terms (after dedup/merge): {total_terms}")
    print(f"Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
