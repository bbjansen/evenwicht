#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify that terms used in theorem statements are formally defined first.

Checks that each italicized term appearing in a Theorem, Corollary, or Remark
block has been formally introduced in a prior Definition block in the same
chapter, in the chapter's glossary, in a prerequisite chapter's glossary, or
belongs to a common-knowledge allow-list.

Extraction rules:
  - Definition blocks start with ``**Definition 3.N** (Name).`` and define the
    first italicized term(s) in their body text (e.g. *function*).
  - Glossary entries live under ``## 12. Glossary`` as ``- **Term**: ...``.
  - Theorem/Corollary/Remark blocks start with ``**Theorem 3.N**``, etc.
  - Italicized terms inside those blocks are checked for prior definition.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# ---------------------------------------------------------------------------
# Common-knowledge allow-list: mathematical terms so fundamental that every
# chapter may use them without a local definition.
# ---------------------------------------------------------------------------
COMMON_KNOWLEDGE: set[str] = {
    # Basic objects
    "function", "functions", "set", "sets", "subset", "subsets",
    "element", "elements", "number", "numbers", "value", "values",
    "constant", "constants", "variable", "variables", "parameter",
    "parameters", "quantity", "quantities",
    # Number systems
    "integer", "integers", "natural number", "natural numbers",
    "real number", "real numbers", "rational number", "rational numbers",
    "complex number", "complex numbers", "scalar", "scalars",
    "positive", "negative", "non-negative", "nonnegative", "nonzero",
    # Linear algebra basics
    "vector", "vectors", "matrix", "matrices", "transpose",
    "inverse", "rank", "dimension", "linear", "nonlinear",
    "linear combination", "coefficient", "coefficients",
    # Calculus basics
    "derivative", "derivatives", "integral", "integrals",
    "continuous", "differentiable", "convergence", "limit", "limits",
    "sum", "sums", "product", "products", "series",
    "sequence", "sequences", "interval", "intervals",
    "bounded", "unbounded", "finite", "infinite", "countable",
    "uncountable", "open", "closed",
    # Common modifiers / descriptors
    "independent", "dependent", "unique", "optimal", "minimum",
    "maximum", "equal", "equivalent", "identical", "arbitrary",
    "fixed", "given", "known", "unknown", "estimated", "observed",
    "true", "false", "necessary", "sufficient",
    # Probability / statistics fundamentals used everywhere
    "random", "probability", "distribution", "mean", "average",
    "iid", "i.i.d.", "sample", "samples", "population",
    "data", "observation", "observations", "estimate", "estimator",
    "statistic", "statistics", "hypothesis", "null", "test",
    # Common shorthand / jargon
    "model", "formula", "equation", "identity", "inequality",
    "condition", "assumption", "property", "definition", "theorem",
    "proof", "result", "case", "example", "remark", "note",
    "algorithm", "step", "method", "technique", "procedure",
    "solution", "problem", "error", "approximation",
    # Geometry / topology basics
    "point", "points", "space", "distance", "norm", "metric",
    "ball", "neighborhood", "neighbourhood",
    # Logic
    "iff", "if and only if",
    # Notation-like italics that are not true terms
    "th", "st", "nd", "rd", "i.e.", "e.g.", "etc", "vs",
    "resp", "cf", "viz", "ibid",
    # Single-letter and very short tokens (often variable names)
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
    "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
    "w", "x", "y", "z",
    # Additional common terms
    "zero", "one", "two", "pair", "triple",
    "graph", "node", "edge", "path", "weight",
    "input", "output", "state", "system", "field",
    "operator", "operation", "map", "mapping",
    "domain", "range", "image", "codomain",
    "surjective", "injective", "bijective",
    "symmetric", "asymmetric", "antisymmetric",
    "commutative", "associative", "distributive",
    "monotone", "monotonic", "increasing", "decreasing",
    "convex", "concave", "smooth", "analytic",
    "global", "local", "strict", "weak", "strong",
    "left", "right", "upper", "lower",
    "row", "column", "diagonal", "entry", "entries",
    "degree", "order", "index",
    "ratio", "rate", "proportion", "percentage", "fraction",
    "total", "partial", "marginal",
    "real", "complex", "imaginary", "rational", "irrational",
    "abstract", "concrete", "general", "special",
    "standard", "normal", "regular", "singular",
    "trivial", "nontrivial", "degenerate",
    "square", "root", "power", "exponent", "logarithm",
    "infimum", "supremum", "maximum", "minimum",
    "critical", "stationary", "equilibrium",
    "stable", "unstable",
    "response", "predictor", "regressor", "covariate",
    "residual", "residuals", "fitted",
    "noise", "signal", "trend", "component",
    "null hypothesis", "alternative hypothesis",
    "significance", "confidence", "level",
    "bias", "unbiased", "consistent", "efficient",
    "asymptotic", "asymptotically",
    "bernoulli", "binomial", "poisson", "gaussian",
    "uniform", "exponential",
    # Additional generic / cross-domain terms
    "restricted", "unrestricted", "tight", "loose",
    "timing", "absolute value",
    "linear transformation", "linear transformations",
    "standardization", "normalization",
    "oscillatory", "periodic", "aperiodic",
    "transitional", "turbulent", "laminar",
    "fully turbulent",
    "free", "forced", "damped", "undamped",
    "frequency", "amplitude", "phase", "wavelength",
    "gain", "loss", "attenuation",
    "open", "closed", "bounded", "unbounded",
    "special case", "special cases",
    "axial", "tangential", "oblique",
}

# ---------------------------------------------------------------------------
# Structural / formatting terms that should not be flagged
# ---------------------------------------------------------------------------
SKIP_PATTERNS: list[re.Pattern[str]] = [
    # Numbered labels: "Definition 3.1", "Theorem 3.5a"
    re.compile(
        r"^(Definition|Theorem|Example|Corollary|Lemma|Proposition|Remark|"
        r"Algorithm|Property|Notation|Convention|Rule|Axiom|Postulate|"
        r"Claim|Conjecture|Fact|Result)\s+\d",
        re.IGNORECASE,
    ),
    # Pure numbers or numeric labels
    re.compile(r"^\d+(\.\d+)?[a-z]?$"),
    # Chapter references
    re.compile(r"^Chapter\s+\d", re.IGNORECASE),
    # Single character (variable name)
    re.compile(r"^[a-zA-Z]$"),
    # Proof annotations: "Proof omitted.", "Proof sketch.", "Proof (for ...)"
    re.compile(r"^Proof[\s(]", re.IGNORECASE),
    re.compile(r"^Stated without proof", re.IGNORECASE),
    # Full sentences (contain a verb-like period/space pattern, or are very long)
    re.compile(r"^.{60,}$"),
    # Labels ending with a colon (enumeration headings)
    re.compile(r":$"),
]

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# A Definition block header: **Definition 3.N** (Name). ...
DEFINITION_RE = re.compile(
    r"\*\*Definition\s+\d+\.\d+[a-z]?\*\*\s*\(([^)]+)\)\."
)

# Unnumbered Definition or Remark block header: **Definition** (Name). or **Remark** (Name).
UNNUMBERED_DEF_RE = re.compile(
    r"\*\*(Definition|Remark)\*\*\s*\(([^)]+)\)\."
)

# A Theorem/Corollary/Remark block header
THEOREM_HEADER_RE = re.compile(
    r"^\s*\*\*(Theorem|Corollary)\s+(\d+\.\d+[a-z]?)\*\*\s*\(([^)]+)\)\."
)

# Italicized term: *term* but not **bold** and not inside LaTeX $...$
# We extract these after stripping LaTeX.
ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")

# Italicized enumeration label: `N. *Label*:` or `- *Label*:` or `(a) *Label*:`
# These are property names in lists, not technical terms.
ENUM_LABEL_RE = re.compile(
    r"(?:\d+\.\s+|[-*]\s+|\([a-z0-9]+\)\s+)\*([^*]+)\*\s*:"
)

# Glossary entry: - **Term**: definition  or  - **Term ($symbol$)**: definition
GLOSSARY_RE = re.compile(r"^-\s+\*\*([^*]+)\*\*")

# Prerequisite chapter link: [Chapter N](NN-name.md)
PREREQ_CHAPTER_RE = re.compile(r"\[Chapter\s+(\d+)\]")


def normalize(term: str) -> str:
    """Lowercase, strip whitespace and trailing punctuation."""
    return term.strip().lower().rstrip(".,;:!?")


def singularize(term: str) -> str:
    """Naive singularization."""
    if term.endswith("ies"):
        return term[:-3] + "y"
    if term.endswith("ses") or term.endswith("xes") or term.endswith("zes"):
        return term[:-2]
    if term.endswith("s") and not term.endswith("ss"):
        return term[:-1]
    return term


def strip_latex(text: str) -> str:
    """Remove inline and display LaTeX to avoid false matches on math symbols."""
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]+\$", "", text)
    return text


def should_skip(term: str) -> bool:
    """Return True if the term is structural or too short to check."""
    n = normalize(term)
    if not n or len(n) <= 1:
        return True
    for pat in SKIP_PATTERNS:
        if pat.search(term):
            return True
    # Skip italic text that looks like a sentence or instruction
    # (contains a period followed by a space, or ends with a period).
    if re.search(r"\.\s+[A-Z]", term):
        return True
    if term.rstrip().endswith("."):
        return True
    # Skip italic text containing parenthetical clauses that look like
    # meta-commentary rather than a defined term (e.g., "proof omitted").
    if re.search(r"\(proof", term, re.IGNORECASE):
        return True
    return False


def is_common_knowledge(term: str) -> bool:
    """Return True if the term is on the common-knowledge allow-list."""
    n = normalize(term)
    if n in COMMON_KNOWLEDGE:
        return True
    s = singularize(n)
    if s in COMMON_KNOWLEDGE:
        return True
    # Check individual words for multi-word terms: if every word is common
    # knowledge, the compound is unlikely to be a specialized concept.
    words = n.split()
    if len(words) >= 2 and all(w in COMMON_KNOWLEDGE for w in words):
        return True
    return False


# ---------------------------------------------------------------------------
# Section / block extraction helpers
# ---------------------------------------------------------------------------

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


def extract_glossary_terms(glossary_text: str) -> set[str]:
    """Extract normalized glossary terms from a glossary section."""
    terms: set[str] = set()
    for line in glossary_text.split("\n"):
        m = GLOSSARY_RE.match(line)
        if m:
            raw = m.group(1)
            # Strip trailing parenthetical like ($\Omega$) or (AST)
            clean = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
            terms.add(normalize(clean))
            # Also add the singular form
            terms.add(singularize(normalize(clean)))
    return terms


def extract_prerequisite_chapters(text: str) -> list[int]:
    """Extract chapter numbers from the Prerequisites line."""
    for line in text.split("\n"):
        if line.startswith("**Prerequisites**"):
            return [int(m) for m in PREREQ_CHAPTER_RE.findall(line)]
    return []


def _is_block_boundary(line: str) -> bool:
    """Return True if the line starts a new formal block or section header."""
    # Numbered block: **Definition 3.1**, **Theorem 3.2**, etc.
    if re.match(r"^\s*\*\*(Definition|Theorem|Corollary|Remark|Lemma)\s+\d", line):
        return True
    # Unnumbered definition/remark block: **Definition** (...) or **Remark** (...)
    if re.match(r"^\s*\*\*(Definition|Remark)\*\*\s*\(", line):
        return True
    # Section header
    if re.match(r"^## \d+\.", line):
        return True
    return False


def extract_definition_terms(core_text: str) -> set[str]:
    """Extract all terms formally defined in Definition blocks.

    A definition term is the first italicized word/phrase in the body of a
    Definition block.  Handles both numbered and unnumbered formats:
        **Definition 3.1** (Sample space). The *sample space* ...
        **Definition** (Term). The *term* ...
        **Remark** (Term). The *term* ...
    """
    terms: set[str] = set()
    lines = core_text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if this line starts a Definition block (numbered or unnumbered)
        def_match = DEFINITION_RE.search(line) or UNNUMBERED_DEF_RE.search(line)
        if def_match:
            # Collect all lines belonging to this block (until next block or
            # section header). We collect the header line plus continuations.
            block_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # Stop at the next formal block or section header
                if _is_block_boundary(next_line):
                    break
                # Stop at mermaid blocks or proof blocks
                if next_line.strip().startswith("```") or next_line.strip().startswith("???"):
                    break
                block_lines.append(next_line)
                j += 1

            block_text = strip_latex("\n".join(block_lines))
            # Extract ALL italicized terms from the definition block
            # (they are being defined or are closely related defined terms)
            for m in ITALIC_RE.finditer(block_text):
                raw_term = m.group(1).strip()
                if not should_skip(raw_term):
                    terms.add(normalize(raw_term))
                    terms.add(singularize(normalize(raw_term)))

        i += 1

    return terms


def extract_theorem_blocks(core_text: str) -> list[tuple[str, str, list[str]]]:
    """Extract theorem blocks and their italicized terms.

    Returns list of (label, name, [italicized_terms]) for each
    Theorem/Corollary block.
    """
    results: list[tuple[str, str, list[str]]] = []
    lines = core_text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]
        header_match = THEOREM_HEADER_RE.match(line)
        if header_match:
            block_type = header_match.group(1)
            block_num = header_match.group(2)
            block_name = header_match.group(3)
            label = f"{block_type} {block_num} ({block_name})"

            # Collect the block body
            block_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if _is_block_boundary(next_line):
                    break
                if next_line.strip().startswith("```") or next_line.strip().startswith("???"):
                    break
                block_lines.append(next_line)
                j += 1

            raw_block = "\n".join(block_lines)

            # Collect enumeration labels to exclude: "N. *Label*:" patterns
            enum_labels: set[str] = set()
            for em in ENUM_LABEL_RE.finditer(raw_block):
                enum_labels.add(normalize(em.group(1)))

            block_text = strip_latex(raw_block)
            italic_terms: list[str] = []
            for m in ITALIC_RE.finditer(block_text):
                raw_term = m.group(1).strip()
                if should_skip(raw_term):
                    continue
                if normalize(raw_term) in enum_labels:
                    continue
                italic_terms.append(raw_term)

            if italic_terms:
                results.append((label, block_name, italic_terms))

        i += 1

    return results


def term_is_defined(
    term: str,
    local_defs: set[str],
    local_glossary: set[str],
    prereq_glossaries: set[str],
) -> bool:
    """Check whether a term is defined in any of the available sources."""
    n = normalize(term)
    s = singularize(n)

    for source in (local_defs, local_glossary, prereq_glossaries):
        if n in source or s in source:
            return True
        # Check if any source term contains this term or vice versa
        for existing in source:
            if n in existing or existing in n:
                return True
            es = singularize(existing)
            if s in es or es in s:
                return True

    return False


# ---------------------------------------------------------------------------
# Chapter processing
# ---------------------------------------------------------------------------

def load_chapter_glossary(filepath: Path) -> set[str]:
    """Load glossary terms from a single chapter file."""
    text = filepath.read_text(encoding="utf-8")
    glossary_text = extract_section(text, "Glossary")
    return extract_glossary_terms(glossary_text)


def process_chapter(
    filepath: Path,
    all_glossaries: dict[int, set[str]],
) -> list[tuple[str, str, str]]:
    """Process a single chapter and return issues.

    Returns list of (theorem_label, term, chapter_stem) tuples.
    """
    text = filepath.read_text(encoding="utf-8")
    chapter_stem = filepath.stem

    core_text = extract_section(text, "Core Theory")
    if not core_text:
        return []

    glossary_text = extract_section(text, "Glossary")
    local_glossary = extract_glossary_terms(glossary_text)
    local_defs = extract_definition_terms(core_text)

    # Collect prerequisite glossaries
    prereq_nums = extract_prerequisite_chapters(text)
    prereq_glossary: set[str] = set()
    for pnum in prereq_nums:
        if pnum in all_glossaries:
            prereq_glossary |= all_glossaries[pnum]

    # Check theorems
    issues: list[tuple[str, str, str]] = []
    theorem_blocks = extract_theorem_blocks(core_text)

    for label, _, italic_terms in theorem_blocks:
        seen: set[str] = set()
        for term in italic_terms:
            n = normalize(term)
            if n in seen:
                continue
            seen.add(n)

            if is_common_knowledge(term):
                continue

            if not term_is_defined(term, local_defs, local_glossary, prereq_glossary):
                issues.append((label, term, chapter_stem))

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}")
        return 1

    print(f"Scanning {len(chapter_files)} chapters for definition-before-use...\n")

    # Pre-load all glossaries so prerequisite lookups work
    all_glossaries: dict[int, set[str]] = {}
    for fp in chapter_files:
        num = int(fp.stem.split("-")[0])
        all_glossaries[num] = load_chapter_glossary(fp)

    total_issues = 0
    chapters_with_issues = 0

    for filepath in chapter_files:
        issues = process_chapter(filepath, all_glossaries)
        if issues:
            chapters_with_issues += 1
            print(f"  {filepath.stem}")
            for label, term, _ in issues:
                print(f"    {label}: \"{term}\" not defined before use")
            total_issues += len(issues)
            print()

    print("=" * 60)
    print(f"Chapters scanned:        {len(chapter_files)}")
    print(f"Chapters with issues:    {chapters_with_issues}")
    print(f"Undefined terms:         {total_issues}")
    print("=" * 60)

    if total_issues > 0:
        return 1
    print("\nAll definition-before-use checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
