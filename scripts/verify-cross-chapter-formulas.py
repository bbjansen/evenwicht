#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify that formulas restated across chapters are mathematically identical.

When a chapter restates a formula from another chapter (e.g., "This is
Theorem 3.6 of Chapter 17"), this script checks that the LaTeX expressions
match after normalization.

Strategy:
  1. For each chapter, index all labeled formulas in Section 5
     (## 5. Formulas & Identities).  Labels are like **F4.1** followed by
     inline ($...$) or display ($$...$$) math.
  2. Index all theorem/definition display-math: for **Theorem 3.N** blocks,
     capture the first $$...$$ display equation that follows.
  3. Scan all chapters for cross-references citing formulas/theorems from
     other chapters.
  4. When a formula is restated locally AND cites another chapter, compare
     after normalization.
  5. Report mismatches.

Normalization:
  - Strip whitespace
  - Normalize transpose: X' == X^T == X^\\top == X^{\\top}
  - Normalize bold: \\mathbf{x} == \\boldsymbol{x} == \\bm{x}
  - Normalize text: \\text{X} == \\operatorname{X} == \\mathrm{X}

Exit code 0 if no mismatches, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

VALID_CHAPTERS = set(range(1, 49))


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FormulaEntry:
    """A labeled formula or theorem equation from a chapter."""
    chapter: int
    label: str          # e.g. "F4.1", "Theorem 3.6", "Definition 3.12"
    latex: str           # the raw LaTeX expression
    line: int            # line number in the source file


@dataclass
class CrossRef:
    """A cross-reference to a formula/theorem in another chapter."""
    source_chapter: int
    target_chapter: int
    target_label: str    # e.g. "Theorem 3.6", "F4.1"
    local_latex: str     # the locally restated LaTeX (if any)
    line: int
    confidence: str      # "high" = explicit restatement, "low" = nearby formula


@dataclass
class Issue:
    level: str          # MATCH, MISMATCH, INFO
    source_ch: int
    message: str


# ---------------------------------------------------------------------------
# LaTeX normalization
# ---------------------------------------------------------------------------

def normalize_latex(s: str) -> str:
    """Normalize a LaTeX string for comparison.

    This is deliberately conservative: exact match after normalization,
    not symbolic equivalence.
    """
    # Strip leading/trailing $$ or $ delimiters if present.
    # Use [$] character class because \$ in regex is ambiguous.
    s = re.sub(r"^[$][$]", "", s)
    s = re.sub(r"[$][$]$", "", s)
    s = re.sub(r"^[$]", "", s)
    s = re.sub(r"[$]$", "", s)

    # Strip all whitespace
    s = re.sub(r"\s+", "", s)

    # Normalize explicit transpose commands: ^{\top}, ^\top, ^T, ^{T}
    # all become ^{\top}.  We do NOT convert prime (') because it is
    # ambiguous between transpose and derivative across chapters.
    s = re.sub(r"\^\{\\top\}", "^{\\\\top}", s)
    s = re.sub(r"\^\\top(?![a-zA-Z])", "^{\\\\top}", s)
    s = re.sub(r"\^\{T\}", "^{\\\\top}", s)
    # Bare ^T only when followed by a non-letter (to avoid clobbering
    # things like ^{Tx} or ^{T_n})
    s = re.sub(r"\^T(?![a-zA-Z_{])", "^{\\\\top}", s)

    # Normalize bold commands: \boldsymbol{x}, \bm{x} -> \mathbf{x}
    s = re.sub(r"\\boldsymbol\{([^}]*)\}", r"\\mathbf{\1}", s)
    s = re.sub(r"\\bm\{([^}]*)\}", r"\\mathbf{\1}", s)

    # Normalize text/operator commands: \text{X}, \mathrm{X} -> \operatorname{X}
    s = re.sub(r"\\text\{([^}]*)\}", r"\\operatorname{\1}", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\\operatorname{\1}", s)

    # Normalize trailing comma or period (some formulas end with a period)
    s = re.sub(r"[.,;]+$", "", s)

    return s


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_chapter_number(filename: str) -> int:
    """Return the chapter number from a filename like '04-differential-calculus.md'."""
    m = re.match(r"(\d+)-", filename)
    if m:
        return int(m.group(1))
    raise ValueError(f"Cannot extract chapter number from {filename}")


def find_section5_range(text: str) -> tuple[int, int] | None:
    """Return (start, end) character offsets of Section 5 (Formulas & Identities)."""
    m = re.search(r"^##\s+5\.\s+Formulas\s*[&]\s*Identities", text, re.MULTILINE)
    if not m:
        return None
    start = m.start()
    # Find the next ## heading
    rest = text[start + 1:]
    next_sec = re.search(r"^##\s+\d+\.", rest, re.MULTILINE)
    end = start + 1 + next_sec.start() if next_sec else len(text)
    return (start, end)


def extract_formula_labels(section_text: str, ch_num: int,
                           base_line: int) -> list[FormulaEntry]:
    """Extract **F4.N** labeled formulas from Section 5 text.

    Each label is followed by either inline math ($...$) or display math
    ($$...$$) on the same or next line.
    """
    entries: list[FormulaEntry] = []
    lines = section_text.split("\n")

    for i, line in enumerate(lines):
        # Look for **F4.N** pattern
        label_match = re.search(r"\*\*(F\d+\.\d+)\*\*", line)
        if not label_match:
            continue
        label = label_match.group(1)
        lineno = base_line + i

        # Try to extract display math on the same or following lines
        latex = _extract_following_math(lines, i)
        if latex:
            entries.append(FormulaEntry(
                chapter=ch_num, label=label, latex=latex, line=lineno
            ))

    return entries


def extract_theorem_formulas(text: str, ch_num: int) -> list[FormulaEntry]:
    """Extract display equations following each **Theorem 3.N** or
    **Definition 3.N** block in the chapter.

    Collects ALL display equations within the theorem block (up to the next
    labeled block or section heading), so that any of them can be matched
    against cross-references.
    """
    entries: list[FormulaEntry] = []
    lines = text.split("\n")

    # Find the line indices of all labeled blocks and section headings
    # to determine boundary of each theorem block.
    block_starts: list[int] = []
    for i, line in enumerate(lines):
        if re.search(
            r"\*\*(Theorem|Definition|Lemma|Corollary|Proposition|Remark|Algorithm)\s+"
            r"\d+\.\d+\*\*",
            line,
        ):
            block_starts.append(i)
        elif re.match(r"^##\s+\d+\.", line):
            block_starts.append(i)

    for i, line in enumerate(lines):
        # Match **Theorem 3.N**, **Definition 3.N**, **Lemma 3.N**, etc.
        label_match = re.search(
            r"\*\*(Theorem|Definition|Lemma|Corollary|Proposition)\s+"
            r"(\d+\.\d+)\*\*",
            line,
        )
        if not label_match:
            continue
        kind = label_match.group(1)
        number = label_match.group(2)
        label = f"{kind} {number}"

        # Determine the end of this block: next labeled block or 30 lines,
        # whichever is smaller.
        end_line = min(i + 30, len(lines))
        for bs in block_starts:
            if bs > i:
                end_line = min(end_line, bs)
                break

        # Collect all display math in this range
        block_text = "\n".join(lines[i:end_line])
        all_display = re.findall(r"[$][$](.*?)[$][$]", block_text, re.DOTALL)

        for latex_str in all_display:
            latex_str = latex_str.strip()
            if latex_str:
                entries.append(FormulaEntry(
                    chapter=ch_num, label=label, latex=latex_str, line=i + 1
                ))

    return entries


def _extract_following_math(lines: list[str], start_idx: int) -> str | None:
    """Extract the first math expression after a label on or near line start_idx.

    Tries display math ($$...$$) first, then inline ($...$).
    """
    # Check the current line and next ~5 lines for math
    search_window = "\n".join(lines[start_idx:start_idx + 6])

    # Display math (possibly multiline)
    dm = re.search(r"[$][$](.*?)[$][$]", search_window, re.DOTALL)
    if dm:
        return dm.group(1).strip()

    # Inline math on the label line
    line = lines[start_idx]
    # Find inline math after the label
    label_end = line.find("**", line.find("**") + 2) + 2
    rest = line[label_end:]
    im = re.search(r"[$]([^$]+)[$]", rest)
    if im:
        return im.group(1).strip()

    return None


# ---------------------------------------------------------------------------
# Cross-reference detection
# ---------------------------------------------------------------------------

# Patterns for cross-chapter formula/theorem references:
#   "Theorem 3.6 of [Chapter 17]"
#   "Theorem 3.6 of Chapter 17"
#   "Definition 3.12 of [Chapter 17]"
#   "[Chapter 17], Theorem 3.6"
#   "[Chapter 17](17-regression.md), Theorem 3.6"
#   "(Theorem 3.19 of [Chapter 39](...))"
#   "F4.1 of Chapter N" (less common but possible)

_RE_XREF_FORWARD = re.compile(
    r"(?P<kind>Theorem|Definition|Lemma|Corollary|Proposition|Algorithm)\s+"
    r"(?P<number>\d+\.\d+)\s+of\s+\[?Chapter\s+(?P<chapter>\d+)\]?"
    r"(?:\([^)]*\))?",
    re.IGNORECASE,
)

_RE_XREF_BACKWARD = re.compile(
    r"\[Chapter\s+(?P<chapter>\d+)\](?:\([^)]*\))?,?\s+"
    r"(?P<kind>Theorem|Definition|Lemma|Corollary|Proposition|Algorithm)\s+"
    r"(?P<number>\d+\.\d+)",
    re.IGNORECASE,
)

# "This is Theorem 3.6 of [Chapter 17](...)"
_RE_XREF_THIS_IS = re.compile(
    r"[Tt]his\s+is\s+"
    r"(?P<kind>Theorem|Definition|Lemma|Corollary|Proposition)\s+"
    r"(?P<number>\d+\.\d+)\s+of\s+\[Chapter\s+(?P<chapter>\d+)\]"
    r"(?:\([^)]*\))?",
)

# "F4.1 of Chapter N" (formula label cross-ref)
_RE_XREF_FORMULA = re.compile(
    r"(?P<label>F\d+\.\d+)\s+of\s+\[?Chapter\s+(?P<chapter>\d+)\]?"
    r"(?:\([^)]*\))?",
    re.IGNORECASE,
)


def find_cross_references(text: str, ch_num: int) -> list[CrossRef]:
    """Find all cross-references to formulas/theorems from other chapters.

    Deduplicates references that match multiple regex patterns on the same
    line with the same target.
    """
    refs: list[CrossRef] = []
    seen: set[tuple[int, int, str]] = set()  # (lineno, target_ch, label)
    lines = text.split("\n")

    for lineno, line in enumerate(lines, start=1):
        for pattern in [_RE_XREF_THIS_IS, _RE_XREF_FORWARD, _RE_XREF_BACKWARD]:
            for m in pattern.finditer(line):
                target_ch = int(m.group("chapter"))
                if target_ch == ch_num:
                    continue  # Skip self-references
                kind = m.group("kind")
                number = m.group("number")
                label = f"{kind} {number}"

                key = (lineno, target_ch, label)
                if key in seen:
                    continue
                seen.add(key)

                is_explicit = bool(_RE_XREF_THIS_IS.search(line))
                local_latex, confidence = _find_nearby_formula(
                    lines, lineno - 1, is_explicit
                )

                refs.append(CrossRef(
                    source_chapter=ch_num,
                    target_chapter=target_ch,
                    target_label=label,
                    local_latex=local_latex or "",
                    line=lineno,
                    confidence=confidence,
                ))

        # Formula label cross-refs
        for m in _RE_XREF_FORMULA.finditer(line):
            target_ch = int(m.group("chapter"))
            if target_ch == ch_num:
                continue
            label = m.group("label")
            key = (lineno, target_ch, label)
            if key in seen:
                continue
            seen.add(key)

            local_latex, confidence = _find_nearby_formula(
                lines, lineno - 1, False
            )
            refs.append(CrossRef(
                source_chapter=ch_num,
                target_chapter=target_ch,
                target_label=label,
                local_latex=local_latex or "",
                line=lineno,
                confidence=confidence,
            ))

    return refs


def _find_nearby_formula(
    lines: list[str], line_idx: int, is_explicit_restatement: bool
) -> tuple[str | None, str]:
    """Try to find a restated formula near a cross-reference line.

    Returns (latex_or_None, confidence) where confidence is "high" or "low".

    We use tight heuristics to avoid picking up unrelated formulas:
      1. If the reference is an explicit restatement ("This is Theorem X.Y"),
         look for a display equation in the immediately preceding lines
         (the typical pattern is: display equation, then proof text citing it).
      2. If the reference line is on a theorem/definition label line that
         cites another chapter, look at display math immediately following.
      3. Inline math containing '=' on the reference line (low confidence).
    """
    ref_line = lines[line_idx]

    # Strategy 1: "This is Theorem X.Y of Chapter N" -- look ABOVE for
    # the restated display equation (the typical pattern is: state the
    # result as a theorem, give the display equation, then in the proof
    # note "This is Theorem X.Y of Chapter N").
    if is_explicit_restatement:
        for offset in range(1, 8):
            check_idx = line_idx - offset
            if check_idx < 0:
                break
            window = "\n".join(lines[max(0, check_idx - 2):line_idx])
            dm = re.search(r"[$][$](.*?)[$][$]", window, re.DOTALL)
            if dm:
                return dm.group(1).strip(), "high"

    # Strategy 2: Reference is on a theorem/definition label line that
    # cites another chapter -- look at display math immediately following.
    if re.search(
        r"\*\*(Theorem|Definition|Lemma|Corollary|Proposition)\s+\d+\.\d+\*\*",
        ref_line,
    ):
        window = "\n".join(lines[line_idx:line_idx + 8])
        dm = re.search(r"[$][$](.*?)[$][$]", window, re.DOTALL)
        if dm:
            return dm.group(1).strip(), "high"

    # Strategy 3: Inline math on the reference line containing '=' and
    # of sufficient length (likely a formula restatement).
    im = re.findall(r"[$]([^$]+)[$]", ref_line)
    formula_candidates = [m for m in im if "=" in m and len(m) > 10]
    if formula_candidates:
        return max(formula_candidates, key=len).strip(), "low"

    return None, "low"


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_formulas(
    chapter_formulas: dict[int, dict[str, list[FormulaEntry]]],
    cross_refs: list[CrossRef],
) -> list[Issue]:
    """Compare cross-referenced formulas after normalization.

    For each cross-reference, the local formula is compared against ALL
    indexed formulas for the target label.  A match against any one of
    them counts as a match.
    """
    issues: list[Issue] = []

    for xref in cross_refs:
        target_ch = xref.target_chapter
        target_label = xref.target_label

        # Look up the target formula
        if target_ch not in chapter_formulas:
            issues.append(Issue(
                "INFO", xref.source_chapter,
                f"Ch {xref.source_chapter:02d}:{xref.line} references "
                f"{target_label} of Ch {target_ch:02d}, but chapter not loaded"
            ))
            continue

        ch_index = chapter_formulas[target_ch]
        if target_label not in ch_index:
            issues.append(Issue(
                "INFO", xref.source_chapter,
                f"Ch {xref.source_chapter:02d}:{xref.line} references "
                f"{target_label} of Ch {target_ch:02d}, "
                f"but formula not found in target index"
            ))
            continue

        if not xref.local_latex:
            issues.append(Issue(
                "INFO", xref.source_chapter,
                f"Ch {xref.source_chapter:02d}:{xref.line} references "
                f"{target_label} of Ch {target_ch:02d}, "
                f"no locally restated formula found to compare"
            ))
            continue

        target_entries = ch_index[target_label]
        norm_local = normalize_latex(xref.local_latex)

        # Try to match against any of the target formulas
        exact_match = False
        partial_match = False
        best_target_raw = target_entries[0].latex

        for tentry in target_entries:
            norm_target = normalize_latex(tentry.latex)
            if norm_local == norm_target:
                exact_match = True
                best_target_raw = tentry.latex
                break
            if norm_local in norm_target or norm_target in norm_local:
                partial_match = True
                best_target_raw = tentry.latex

        if exact_match:
            issues.append(Issue(
                "MATCH", xref.source_chapter,
                f"Ch {xref.source_chapter:02d}:{xref.line} -> "
                f"{target_label} of Ch {target_ch:02d} -- "
                f"formulas match after normalization"
            ))
        elif partial_match:
            issues.append(Issue(
                "INFO", xref.source_chapter,
                f"Ch {xref.source_chapter:02d}:{xref.line} -> "
                f"{target_label} of Ch {target_ch:02d} -- "
                f"partial match (one formula contains the other)\n"
                f"    local:  {_truncate(xref.local_latex, 100)}\n"
                f"    target: {_truncate(best_target_raw, 100)}"
            ))
        else:
            # Low-confidence matches (nearby formula may be unrelated to the
            # cross-reference) are reported as INFO rather than MISMATCH.
            first_target = target_entries[0]
            norm_first = normalize_latex(first_target.latex)
            level = "MISMATCH" if xref.confidence == "high" else "INFO"
            qualifier = (
                "formulas DIFFER after normalization"
                if level == "MISMATCH"
                else "nearby formula differs (may not be a restatement)"
            )
            issues.append(Issue(
                level, xref.source_chapter,
                f"Ch {xref.source_chapter:02d}:{xref.line} -> "
                f"{target_label} of Ch {target_ch:02d} -- "
                f"{qualifier} "
                f"({len(target_entries)} target formula(s) checked)\n"
                f"    local:  {_truncate(xref.local_latex, 120)}\n"
                f"    target: {_truncate(first_target.latex, 120)}\n"
                f"    norm-local:  {_truncate(norm_local, 120)}\n"
                f"    norm-target: {_truncate(norm_first, 120)}"
            ))

    return issues


def _truncate(s: str, n: int) -> str:
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n - 3] + "..."


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

LEVEL_ORDER = {"MISMATCH": 0, "INFO": 1, "MATCH": 2}


def print_report(issues: list[Issue], total_refs: int, total_indexed: int) -> int:
    """Print the verification report and return an exit code (0 = clean)."""
    counts: dict[str, int] = defaultdict(int)
    for issue in issues:
        counts[issue.level] += 1

    sorted_issues = sorted(
        issues, key=lambda i: (LEVEL_ORDER.get(i.level, 9), i.source_ch)
    )

    for issue in sorted_issues:
        print(f"{issue.level}: {issue.message}")

    print()
    print(
        f"Indexed {total_indexed} formulas/theorems across all chapters."
    )
    print(
        f"Found {total_refs} cross-chapter formula references, "
        f"{counts['MATCH']} matches, "
        f"{counts['MISMATCH']} mismatches, "
        f"{counts['INFO']} informational."
    )

    return 1 if counts["MISMATCH"] > 0 else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}", file=sys.stderr)
        return 1

    # Phase 1: Build formula index for all chapters
    # Maps chapter_num -> {label -> [FormulaEntry, ...]}
    # A theorem may have multiple display equations; we store all of them.
    chapter_formulas: dict[int, dict[str, list[FormulaEntry]]] = {}
    total_indexed = 0

    for path in chapter_files:
        text = path.read_text(encoding="utf-8")
        ch_num = extract_chapter_number(path.name)
        index: dict[str, list[FormulaEntry]] = {}

        # Index Section 5 formula labels
        sec5 = find_section5_range(text)
        if sec5:
            sec5_text = text[sec5[0]:sec5[1]]
            # Compute the line number where Section 5 starts
            base_line = text[:sec5[0]].count("\n") + 1
            for entry in extract_formula_labels(sec5_text, ch_num, base_line):
                index.setdefault(entry.label, []).append(entry)

        # Index theorem/definition display equations
        for entry in extract_theorem_formulas(text, ch_num):
            index.setdefault(entry.label, []).append(entry)

        chapter_formulas[ch_num] = index
        total_indexed += sum(len(v) for v in index.values())

    # Phase 2: Find all cross-references
    all_xrefs: list[CrossRef] = []
    for path in chapter_files:
        text = path.read_text(encoding="utf-8")
        ch_num = extract_chapter_number(path.name)
        xrefs = find_cross_references(text, ch_num)
        all_xrefs.extend(xrefs)

    # Phase 3: Compare
    issues = compare_formulas(chapter_formulas, all_xrefs)

    # Phase 4: Report
    print(f"Loaded {len(chapter_files)} chapters from {DOCS_DIR}\n")
    return print_report(issues, len(all_xrefs), total_indexed)


if __name__ == "__main__":
    sys.exit(main())
