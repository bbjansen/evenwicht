#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Extract notation tables from all 48 chapter markdown files and produce a
consolidated notation index grouped by category.

Source: docs/domains/[0-9]*.md  (each has ## 3. Notation & Conventions)
Output: dist/notation-index.md
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
OUTPUT_FILE = PROJECT_ROOT / "dist" / "notation-index.md"

# ---------------------------------------------------------------------------
# Category classification
# ---------------------------------------------------------------------------

# Patterns matched against the raw LaTeX symbol column to assign categories.
# Order matters: first match wins.

GREEK_LETTERS = [
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon",
    "zeta", "eta", "theta", "vartheta", "iota", "kappa",
    "lambda", "mu", "nu", "xi", "pi", "varpi",
    "rho", "varrho", "sigma", "varsigma", "tau", "upsilon",
    "phi", "varphi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi",
    "Sigma", "Upsilon", "Phi", "Psi", "Omega",
]

OPERATOR_KEYWORDS = [
    r"\\nabla", r"\\partial", r"\\sum", r"\\prod", r"\\int",
    r"\\circ", r"\\times", r"\\otimes", r"\\oplus", r"\\wedge",
    r"\\cup", r"\\cap", r"\\setminus", r"\\triangle",
    r"\\lim", r"\\sup", r"\\inf", r"\\max", r"\\min",
    r"\\frac\{d", r"\\frac\{\\partial",
    r"\\to", r"\\mapsto", r"\\Rightarrow", r"\\Leftrightarrow",
    r"\\equiv", r"\\approx", r"\\sim", r"\\propto",
    r"\\leq", r"\\geq", r"\\neq", r"\\ll", r"\\gg",
    r"\\perp", r"\\mid", r"\\nmid",
    r"\\stackrel",
    r"\\operatorname",
    r":=",
]

SET_KEYWORDS = [
    r"\\mathbb\{", r"\\mathcal\{F\}", r"\\mathcal\{P\}",
    r"\\in", r"\\subset", r"\\subseteq", r"\\emptyset", r"\\varnothing",
    r"\\text\{span\}", r"\\dim",
    r"\\mathbb\{R\}", r"\\mathbb\{Z\}", r"\\mathbb\{N\}", r"\\mathbb\{Q\}",
    r"\\mathbb\{C\}", r"\\mathbb\{F\}",
]

FUNCTION_KEYWORDS = [
    r"\\log", r"\\ln", r"\\exp", r"\\sin", r"\\cos", r"\\tan",
    r"\\arcsin", r"\\arccos", r"\\arctan",
    r"\\det", r"\\tr", r"\\rank", r"\\diag",
    r"\\gcd", r"\\mathrm\{id\}",
    r"f\(", r"g\(", r"h\(",
    r"\\Gamma\(", r"\\zeta\(",
    r"\\mathcal\{L\}", r"\\mathcal\{Z\}",
]

STATISTICS_KEYWORDS = [
    r"E\[", r"\\operatorname\{Var\}", r"\\operatorname\{Cov\}",
    r"\\bar\{", r"\\hat\{", r"\\tilde\{",
    r"\\rho\(X", r"\\rho_\{",
    r"p\(x\)", r"f_X", r"F_X", r"F\(x\)",
    r"M_X", r"\\chi\^2",
    r"\\sigma\^2", r"\\sigma_",
    r"\\mu_X", r"\\mu\}",
    r"sample mean", r"PMF", r"PDF", r"CDF",
    r"p-value", r"confidence",
]

VECTOR_MATRIX_KEYWORDS_SYMBOL = [
    r"\\mathbf\{",       # boldface vectors
    r"\\boldsymbol\{",   # bold symbols (vectors)
    r"\\lVert",          # norms
    r"\\langle",         # inner products
    r"A\^T", r"A\^{-1}", r"A\^{\\dagger}",  # matrix operations
    r"\\odot",           # Hadamard product
    r"\\binom\{",        # binomial coefficients (matrix-adjacent)
]

VECTOR_MATRIX_KEYWORDS_MEANING = [
    "vector", "matrix", "matric", "transpose", "inverse matrix",
    "eigenvector", "eigenvalue", "determinant", "trace",
    "norm", "inner product", "dot product", "cross product",
    "orthogonal", "projection", "basis", "column",
    "row ", "diagonal", "singular", "rank",
    "adjacency", "jacobian", "hessian",
]

CONSTANT_VARIABLE_KEYWORDS_MEANING = [
    "constant", "variable", "parameter", "coefficient",
    "velocity", "speed", "acceleration", "force", "mass",
    "energy", "power", "temperature", "pressure", "voltage",
    "current", "resistance", "capacitance", "inductance",
    "frequency", "wavelength", "amplitude", "phase",
    "distance", "radius", "position", "displacement",
    "time", "period", "rate", "density", "concentration",
    "population", "number of", "count", "dose", "clearance",
    "flow", "flux", "intensity", "impedance",
    "cost", "price", "value", "return", "yield", "payment",
    "interest", "discount", "present value", "future value",
    "index", "score", "weight", "degree",
    "observation", "iterate", "step", "order statistic",
    "grid spacing", "learning rate", "security parameter",
]


def classify_symbol(symbol: str, meaning: str) -> str:
    """Assign a symbol to one of the predefined categories."""
    combined = symbol + " " + meaning

    # Greek letters: check if the symbol *itself* is primarily a Greek letter
    # (not just using one as a subscript or part of a larger expression).
    # Strip the leading $ and extract the core LaTeX command.
    core = symbol.strip().strip("$").strip()
    # Remove leading \mathbf{}, \boldsymbol{}, etc. wrappers
    core_unwrapped = re.sub(r"^\\(?:mathbf|boldsymbol|mathcal|mathrm)\{(.+)\}$", r"\1", core)
    # Check if the core is a single Greek letter command
    for gl in GREEK_LETTERS:
        if core_unwrapped == f"\\{gl}" or core == f"\\{gl}":
            return "Greek Letters"
        # Also match things like \alpha_0 or \mu_X
        if re.match(rf"^\\{gl}(?:[_^]|$)", core_unwrapped) or re.match(rf"^\\{gl}(?:[_^]|$)", core):
            return "Greek Letters"

    # Statistics (check before operators since E[X] contains brackets)
    for kw in STATISTICS_KEYWORDS:
        if re.search(kw, combined, re.IGNORECASE):
            return "Statistics"

    # Sets & Spaces
    for kw in SET_KEYWORDS:
        if re.search(kw, symbol):
            return "Sets & Spaces"

    # Operators
    for kw in OPERATOR_KEYWORDS:
        if re.search(kw, symbol):
            return "Operators"

    # Functions
    for kw in FUNCTION_KEYWORDS:
        if re.search(kw, combined):
            return "Functions"

    # Vectors & Matrices -- check symbol patterns
    for kw in VECTOR_MATRIX_KEYWORDS_SYMBOL:
        if re.search(kw, symbol):
            return "Vectors & Matrices"

    # Meaning-based classification
    meaning_lower = meaning.lower()

    if any(w in meaning_lower for w in ["operator", "derivative", "gradient", "divergence",
                                         "laplacian", "curl", "composition"]):
        return "Operators"
    if any(w in meaning_lower for w in ["set ", "space", "field", "ring", "group",
                                         "domain", "codomain", "range", "sigma-algebra"]):
        return "Sets & Spaces"
    if any(w in meaning_lower for w in ["function", "map", "transform", "kernel"]):
        return "Functions"
    if any(w in meaning_lower for w in ["mean", "variance", "deviation", "distribution",
                                         "probability", "random", "expectation", "estimator",
                                         "sample", "hypothesis", "confidence", "correlation"]):
        return "Statistics"

    # Vectors & Matrices -- check meaning
    for kw in VECTOR_MATRIX_KEYWORDS_MEANING:
        if kw in meaning_lower:
            return "Vectors & Matrices"

    # Constants & Variables -- catch domain-specific symbols by meaning
    for kw in CONSTANT_VARIABLE_KEYWORDS_MEANING:
        if kw in meaning_lower:
            return "Constants & Variables"

    # Final Greek-letter fallback for symbols containing a Greek letter
    for gl in GREEK_LETTERS:
        if f"\\{gl}" in symbol:
            return "Greek Letters"

    return "Other"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def chapter_number(filepath: str) -> int:
    """Return the chapter number from a filename like '03-limits-continuity.md'."""
    basename = os.path.basename(filepath)
    match = re.match(r"(\d+)", basename)
    if match:
        return int(match.group(1))
    return 0


def extract_notation_section(text: str) -> str | None:
    """Return the text between '## 3. Notation & Conventions' and the next '##' heading."""
    # Match either "## 3. Notation & Conventions" or "## Notation & Conventions"
    pattern = r"^##\s+(?:\d+\.\s+)?Notation\s*&\s*Conventions\s*$"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    start = match.end()
    # Find the next ## heading
    next_heading = re.search(r"^##\s", text[start:], re.MULTILINE)
    if next_heading:
        return text[start:start + next_heading.start()]
    return text[start:]


def parse_table_rows(section: str) -> list[tuple[str, str]]:
    """Parse markdown table rows into (symbol, meaning) tuples.

    Expects rows like:
        | $\\alpha$ | learning rate |
    Skips the header row and separator row.
    """
    rows: list[tuple[str, str]] = []
    lines = section.strip().splitlines()

    in_table = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                # End of table block
                break
            continue

        # Skip separator rows like |--------|---------|
        if re.match(r"^\|[-|\s:]+\|$", stripped):
            in_table = True
            continue

        # Skip header row (Symbol | Meaning)
        if "Symbol" in stripped and "Meaning" in stripped:
            in_table = True
            continue

        if not in_table:
            # We haven't seen the separator yet; this might be the header
            if re.match(r"^\|\s*\S+.*\|\s*\S+.*\|$", stripped):
                in_table = True
                continue
            continue

        # Parse a data row
        parts = stripped.split("|")
        # parts[0] and parts[-1] are empty strings from leading/trailing |
        if len(parts) >= 4:
            symbol = parts[1].strip()
            meaning = parts[2].strip()
            if symbol and meaning:
                rows.append((symbol, meaning))

    return rows


def normalize_symbol(symbol: str) -> str:
    """Produce a normalized key for deduplication.

    Strips surrounding $, collapses whitespace, removes minor formatting
    differences so that '$\\alpha$' and '$ \\alpha $' match.
    """
    s = symbol.strip()
    # Remove surrounding dollar signs
    s = s.strip("$").strip()
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    source_files = sorted(
        DOCS_DIR.glob("[0-9]*.md"),
        key=lambda p: chapter_number(str(p)),
    )

    if not source_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}", file=sys.stderr)
        sys.exit(1)

    # symbol_key -> { "display": str, "meanings": list[str], "chapters": list[int] }
    symbol_data: dict[str, dict] = {}

    chapters_processed = 0
    chapters_with_notation = 0

    for filepath in source_files:
        chap_num = chapter_number(str(filepath))
        text = filepath.read_text(encoding="utf-8")
        section = extract_notation_section(text)

        chapters_processed += 1

        if section is None:
            print(f"  WARNING: No notation section found in {filepath.name}", file=sys.stderr)
            continue

        chapters_with_notation += 1
        rows = parse_table_rows(section)

        for symbol, meaning in rows:
            key = normalize_symbol(symbol)
            if key not in symbol_data:
                symbol_data[key] = {
                    "display": symbol,
                    "meanings": [],
                    "chapters": [],
                }

            # Add chapter reference
            if chap_num not in symbol_data[key]["chapters"]:
                symbol_data[key]["chapters"].append(chap_num)

            # Add meaning if it is genuinely new (not a near-duplicate)
            existing_meanings = symbol_data[key]["meanings"]
            meaning_normalized = meaning.lower().strip().rstrip(".")
            is_duplicate = False
            for existing in existing_meanings:
                if existing.lower().strip().rstrip(".") == meaning_normalized:
                    is_duplicate = True
                    break
            if not is_duplicate:
                symbol_data[key]["meanings"].append(meaning)

    # Classify symbols into categories
    CATEGORY_ORDER = [
        "Greek Letters",
        "Operators",
        "Sets & Spaces",
        "Vectors & Matrices",
        "Functions",
        "Statistics",
        "Constants & Variables",
        "Other",
    ]

    categorized: dict[str, list[tuple[str, dict]]] = {cat: [] for cat in CATEGORY_ORDER}

    for key, data in symbol_data.items():
        combined_meaning = "; ".join(data["meanings"])
        category = classify_symbol(data["display"], combined_meaning)
        categorized[category].append((key, data))

    # Sort each category alphabetically by normalized symbol key
    for cat in categorized:
        categorized[cat].sort(key=lambda item: item[0].lower().replace("\\", ""))

    # Build output
    lines: list[str] = []
    lines.append("# Notation Index")
    lines.append("")
    lines.append(f"This index consolidates notation from all {chapters_with_notation} chapters "
                 f"of the Evenwicht project. Symbols that appear in multiple chapters list all "
                 f"distinct meanings and the chapter numbers where they are used.")
    lines.append("")

    total_unique = len(symbol_data)

    for category in CATEGORY_ORDER:
        entries = categorized[category]
        if not entries:
            continue

        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Symbol | Meaning | Chapters |")
        lines.append("|:--------------|:-------------------------------------------------------|-------:|")

        for _key, data in entries:
            display = data["display"]
            meanings = "; ".join(data["meanings"])
            chapters = ", ".join(str(c) for c in sorted(data["chapters"]))
            lines.append(f"| {display} | {meanings} | {chapters} |")

        lines.append("")

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")

    # Summary
    print(f"Processed {chapters_processed} chapters ({chapters_with_notation} with notation sections)")
    print(f"Total unique symbols: {total_unique}")
    for cat in CATEGORY_ORDER:
        count = len(categorized[cat])
        if count:
            print(f"  {cat}: {count}")
    print(f"Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
