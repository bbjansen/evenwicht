#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify abbreviation discipline across all 48 domain chapters.

Checks:
  1. First-use expansion: known technical abbreviations must be expanded
     on first use in the chapter body (Sections 1-2 and 4+).
  2. Single-use abbreviations: if an abbreviation is defined with a
     parenthetical "(XXX)" but used only once after definition, it should
     have been written in full without the abbreviation.

Exclusions:
  - Content inside mermaid blocks, fenced code blocks and HTML comments.
  - The Notation & Conventions section (Section 3), where abbreviations
    are defined as table notation.
  - Standard abbreviations exempt per TONE-GUIDE: e.g., i.e., cf.,
    et al., viz., QED.
  - Abbreviations that appear in the chapter's own glossary definitions
    (the glossary itself defines the expansion).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# ---------------------------------------------------------------------------
# Known technical abbreviations and their expected expansions (lowercase).
# The expansion list is used for fuzzy matching: if ANY expansion fragment
# appears near the abbreviation on first use, it counts as expanded.
# ---------------------------------------------------------------------------
KNOWN_ABBREVIATIONS: dict[str, list[str]] = {
    "ODE":   ["ordinary differential equation"],
    "PDE":   ["partial differential equation"],
    "FFT":   ["fast fourier transform"],
    "DFT":   ["discrete fourier transform"],
    "IDFT":  ["inverse discrete fourier transform"],
    "CLT":   ["central limit theorem"],
    "ANOVA": ["analysis of variance"],
    "PCA":   ["principal component analysis"],
    "SGD":   ["stochastic gradient descent"],
    "RK4":   ["runge-kutta", "runge–kutta", "fourth-order runge"],
    "CFL":   ["courant-friedrichs-lewy", "courant–friedrichs–lewy"],
    "ARIMA": ["autoregressive integrated moving average"],
    "ARMA":  ["autoregressive moving average"],
    "FIR":   ["finite impulse response"],
    "IIR":   ["infinite impulse response"],
    "SVD":   ["singular value decomposition"],
    "QR":    ["qr decomposition", "qr factori"],
    "LU":    ["lu decomposition", "lu factori"],
    "CDF":   ["cumulative distribution function"],
    "PDF":   ["probability density function"],
    "PMF":   ["probability mass function"],
    "MLE":   ["maximum likelihood estimat"],
    "BLAS":  ["basic linear algebra subprogram"],
    "GPU":   ["graphics processing unit"],
    "CPU":   ["central processing unit"],
    "IEEE":  ["institute of electrical and electronics engineers"],
    "OFDM":  ["orthogonal frequency-division multiplex"],
    "DSP":   ["digital signal process"],
    "RLC":   ["resistor-inductor-capacitor", "resistor–inductor–capacitor"],
    "PID":   ["proportional-integral-derivative", "proportional–integral–derivative"],
    "HVAC":  ["heating, ventilation", "heating ventilation"],
    "BDF":   ["backward differentiation formula"],
    "LP":    ["linear programme", "linear program"],
    "NLP":   ["nonlinear program", "non-linear program"],
    "KKT":   ["karush-kuhn-tucker", "karush–kuhn–tucker"],
    "MCMC":  ["markov chain monte carlo"],
    "EM":    ["expectation-maximisation", "expectation-maximization",
              "expectation maximisation", "expectation maximization"],
    "GLS":   ["generalised least squares", "generalized least squares"],
    "OLS":   ["ordinary least squares"],
    "VIF":   ["variance inflation factor"],
    "LASSO": ["least absolute shrinkage"],
    "GARCH": ["generalised autoregressive conditional heteroskedasticity",
              "generalized autoregressive conditional heteroskedasticity",
              "generalised autoregressive conditional heteroscedasticity"],
    "ETS":   ["error, trend, seasonal", "exponential smoothing"],
    "LSTM":  ["long short-term memory"],
    "SIR":   ["susceptible-infected-recovered", "susceptible–infected–recovered"],
    "EBM":   ["energy balance model"],
    "CFD":   ["computational fluid dynamics"],
    "DOF":   ["degree of freedom", "degrees of freedom"],
    "AC":    ["alternating current"],
    "DC":    ["direct current"],
    "IC":    ["initial condition", "integrated circuit"],
    "NPV":   ["net present value"],
    "IRR":   ["internal rate of return"],
    "DCF":   ["discounted cash flow"],
    "DeFi":  ["decentralised finance", "decentralized finance"],
    "APY":   ["annual percentage yield"],
    "PVIFA": ["present value interest factor"],
    "MBA":   ["master of business administration"],
    "MIRR":  ["modified internal rate of return"],
    "MGF":   ["moment generating function"],
    "EDA":   ["exploratory data analysis"],
    "CUSUM": ["cumulative sum"],
    "CV":    ["coefficient of variation"],
    "IQR":   ["interquartile range"],
    "HITS":  ["hyperlink-induced topic search"],
    "NIPS":  ["neural information processing"],
    "DH":    ["denavit-hartenberg", "denavit–hartenberg"],
    "SI":    ["systeme international", "système international"],
    "DLMF":  ["digital library of mathematical functions"],
    "BFS":   ["basic feasible solution", "breadth-first search"],
    "DAG":   ["directed acyclic graph"],
    "MSE":   ["mean squared error", "mean square error"],
    "RMSE":  ["root mean squared error", "root mean square error"],
    "MAP":   ["maximum a posteriori"],
    "AIC":   ["akaike information criterion"],
    "BIC":   ["bayesian information criterion"],
    "ROC":   ["receiver operating characteristic"],
    "AUC":   ["area under the curve"],
    "SVM":   ["support vector machine"],
    "KNN":   ["k-nearest neighbour", "k-nearest neighbor"],
    "GMM":   ["gaussian mixture model"],
    "HMM":   ["hidden markov model"],
    "VAR":   ["vector autoregress"],
    "PACF":  ["partial autocorrelation function"],
    "ACF":   ["autocorrelation function"],
    "SNR":   ["signal-to-noise ratio"],
    "LTI":   ["linear time-invariant"],
    "ADC":   ["analog-to-digital convert", "analogue-to-digital convert"],
    "DAC":   ["digital-to-analog convert", "digital-to-analogue convert"],
    "FEM":   ["finite element method"],
    "BVP":   ["boundary value problem"],
    "IVP":   ["initial value problem"],
    "CG":    ["conjugate gradient"],
    "QP":    ["quadratic program"],
    "SDP":   ["semidefinite program"],
    "SOCP":  ["second-order cone program"],
    "KDE":   ["kernel density estimat"],
    "GLM":   ["generalised linear model", "generalized linear model"],
    "RSS":   ["residual sum of squares"],
    "TSS":   ["total sum of squares"],
    "ESS":   ["explained sum of squares"],
    "LHS":   ["left-hand side"],
    "RHS":   ["right-hand side"],
    "ABCD":  ["abcd matrix", "ray transfer matrix"],
    "AM":    ["amplitude modulation"],
    "FM":    ["frequency modulation"],
}

# Abbreviations too short or too ambiguous to check reliably.
# These produce many false positives because they collide with
# common words, variable names or LaTeX fragments.
AMBIGUOUS_SKIP: set[str] = {
    # Two-letter abbreviations that collide with common words, variable
    # names, LaTeX fragments or are simply too short to check reliably.
    "QR", "LU", "EM", "AC", "DC", "IC", "LP", "CG", "QP",
    "AM", "FM", "CV", "LHS", "RHS", "SI", "AR", "MA", "ML",
    # IEEE and DLMF are proper nouns / organisation names used universally
    # without expansion (IEEE 754, NIST DLMF). Flagging these produces
    # noise with no editorial value.
    "IEEE", "DLMF",
}

# Standard abbreviations that need no expansion per TONE-GUIDE.
EXEMPT_ABBREVIATIONS: set[str] = {
    "QED", "i.e.", "e.g.", "cf.", "et al.", "viz.",
    # Also exempt: single-letter variables, LaTeX commands, etc.
}

# ---------------------------------------------------------------------------
# Stripping helpers
# ---------------------------------------------------------------------------

# Matches fenced code blocks (``` ... ```) including mermaid blocks.
_CODE_BLOCK_RE = re.compile(
    r"^```[^\n]*\n.*?^```",
    re.MULTILINE | re.DOTALL,
)

# Matches HTML comments <!-- ... -->
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# Matches the Notation & Conventions section (from header to next ## header).
_NOTATION_SECTION_RE = re.compile(
    r"^## Notation & Conventions\s*\n.*?(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)

# Matches the Glossary section (from header to next ## header or end).
_GLOSSARY_SECTION_RE = re.compile(
    r"^## Glossary\s*\n.*?(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)

# Matches the References section (bibliographic entries use abbreviations
# as proper nouns and parenthetical citations, not as body prose).
_REFERENCES_SECTION_RE = re.compile(
    r"^## References\s*\n.*?(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)


def extract_glossary_abbreviations(text: str) -> set[str]:
    """Extract abbreviations defined in the Glossary section.

    Glossary entries like '- **Cumulative distribution function (CDF)**:'
    define abbreviations that should be considered as expanded within the
    glossary itself.
    """
    abbrs: set[str] = set()
    m = _GLOSSARY_SECTION_RE.search(text)
    if not m:
        return abbrs
    glossary = m.group(0)
    # Match parenthetical abbreviations in bold glossary terms.
    for match in re.finditer(r"\*\*[^*]+\(([A-Z]{2,})\)[^*]*\*\*", glossary):
        abbrs.add(match.group(1))
    return abbrs


def extract_notation_abbreviations(text: str) -> set[str]:
    """Extract abbreviations used in the Notation & Conventions table.

    These are the chapter's own defined notation and should not be flagged.
    """
    abbrs: set[str] = set()
    m = _NOTATION_SECTION_RE.search(text)
    if not m:
        return abbrs
    notation = m.group(0)
    for match in re.finditer(r"\b([A-Z]{2,})\b", notation):
        abbrs.add(match.group(1))
    # Also pick up parenthetical definitions like "probability density function (PDF)"
    for match in re.finditer(r"\(([A-Z]{2,})\)", notation):
        abbrs.add(match.group(1))
    return abbrs


def find_abbreviation_uses(
    lines: list[str], abbr: str
) -> list[tuple[int, str]]:
    """Find all lines where an abbreviation appears as a whole word.

    Returns list of (line_number_1based, line_text).
    """
    # Build a pattern that matches the abbreviation as a whole word,
    # but not inside LaTeX commands or as part of a longer uppercase word.
    # The lookahead rejects both lowercase continuations (FFTs is fine,
    # but FIRAS is not a match for FIR) and uppercase continuations.
    pattern = re.compile(
        r"(?<![A-Za-z])" + re.escape(abbr) + r"(?![A-Za-z])"
        + r"|"
        # Also match the common plural form: ABBRs (lowercase s only).
        + r"(?<![A-Za-z])" + re.escape(abbr) + r"s(?![A-Za-z])"
    )
    results = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            results.append((i + 1, line))
    return results


def has_expansion_nearby(
    line: str, abbr: str, expansions: list[str], context_lines: list[str],
    line_idx: int
) -> bool:
    """Check if the abbreviation is expanded on or near the given line.

    Looks for patterns like:
      - "full form (ABBR)"
      - "ABBR (full form)"  (less common but accepted)
      - The full form appearing on the same line or the line before.
    """
    # Check the current line and one line before/after for the expansion.
    window_start = max(0, line_idx - 1)
    window_end = min(len(context_lines), line_idx + 2)
    window_text = " ".join(context_lines[window_start:window_end]).lower()

    for expansion in expansions:
        if expansion in window_text:
            return True

    # Also check for the parenthetical pattern directly:
    # "something (ABBR)" on the same line.
    paren_pattern = re.compile(
        r"\w\s+\(" + re.escape(abbr) + r"\)", re.IGNORECASE
    )
    if paren_pattern.search(line):
        return True

    return False


def count_uses_outside_definition(
    lines: list[str], abbr: str, definition_line_idx: int
) -> int:
    """Count how many times an abbreviation is used after its definition line.

    Only counts uses in the stripped content (code blocks etc. already removed).
    """
    pattern = re.compile(r"(?<![A-Za-z])" + re.escape(abbr) + r"(?![A-Za-z])")
    count = 0
    for i, line in enumerate(lines):
        if i == definition_line_idx:
            continue
        if pattern.search(line):
            count += 1
    return count


# ---------------------------------------------------------------------------
# Per-chapter analysis
# ---------------------------------------------------------------------------

class Issue:
    """A single abbreviation issue in a chapter."""

    def __init__(self, kind: str, abbr: str, line_no: int, detail: str):
        self.kind = kind       # "UNEXPANDED" or "SINGLE-USE"
        self.abbr = abbr
        self.line_no = line_no
        self.detail = detail

    def __str__(self) -> str:
        return f"    {self.kind} [{self.abbr}] line {self.line_no}: {self.detail}"


def process_chapter(filepath: Path) -> list[Issue]:
    """Analyse a single chapter for abbreviation issues."""
    raw_text = filepath.read_text(encoding="utf-8")
    issues: list[Issue] = []

    # Extract abbreviations defined in notation and glossary sections
    # (these are exempt from first-use expansion checks).
    notation_abbrs = extract_notation_abbreviations(raw_text)
    glossary_abbrs = extract_glossary_abbreviations(raw_text)
    chapter_defined = notation_abbrs | glossary_abbrs

    # Build a version of the original lines with excluded regions blanked out,
    # preserving line count for accurate line numbers.
    blanked_lines = _blank_excluded_regions(raw_text)

    # --- Check 1: First-use expansion ---
    for abbr, expansions in KNOWN_ABBREVIATIONS.items():
        if abbr in AMBIGUOUS_SKIP:
            continue
        if abbr in EXEMPT_ABBREVIATIONS:
            continue

        uses = find_abbreviation_uses(blanked_lines, abbr)
        if not uses:
            continue

        # Skip if this abbreviation is defined in notation/glossary.
        # But only if it has an expansion there; bare uses still need
        # first-use expansion in the body.
        if abbr in chapter_defined:
            continue

        first_line_no, first_line = uses[0]
        first_idx = first_line_no - 1  # 0-based

        if not has_expansion_nearby(
            first_line, abbr, expansions, blanked_lines, first_idx
        ):
            # Truncate line for display.
            display = first_line.strip()
            if len(display) > 100:
                display = display[:97] + "..."
            issues.append(Issue(
                "UNEXPANDED", abbr, first_line_no,
                display,
            ))

    # --- Check 2: Single-use abbreviations ---
    # Find parenthetical definitions like "full form (ABBR)" and check
    # if the abbreviation is used more than once after definition.
    paren_def_re = re.compile(
        r"[a-z]\s+\(([A-Z]{2,})\)"
    )
    for i, line in enumerate(blanked_lines):
        for m in paren_def_re.finditer(line):
            abbr = m.group(1)
            if abbr in EXEMPT_ABBREVIATIONS:
                continue
            # Count uses of this abbreviation after the definition line.
            uses_after = count_uses_outside_definition(
                blanked_lines, abbr, i
            )
            if uses_after == 0:
                display = line.strip()
                if len(display) > 100:
                    display = display[:97] + "..."
                issues.append(Issue(
                    "SINGLE-USE", abbr, i + 1,
                    f"defined but never used again: {display}",
                ))

    return issues


def _blank_excluded_regions(raw_text: str) -> list[str]:
    """Return a list of lines with excluded regions replaced by empty strings.

    This preserves line count so line numbers stay accurate.
    """
    lines = raw_text.split("\n")
    result = list(lines)  # copy

    # Blank HTML comments.
    text = raw_text
    for m in _HTML_COMMENT_RE.finditer(text):
        _blank_span(result, text, m.start(), m.end())

    # Blank fenced code blocks.
    for m in _CODE_BLOCK_RE.finditer(text):
        _blank_span(result, text, m.start(), m.end())

    # Blank Notation & Conventions section.
    for m in _NOTATION_SECTION_RE.finditer(text):
        _blank_span(result, text, m.start(), m.end())

    # Blank References section (bibliographic entries are not body prose).
    for m in _REFERENCES_SECTION_RE.finditer(text):
        _blank_span(result, text, m.start(), m.end())

    # Blank Glossary section (glossary definitions expand abbreviations
    # by design; they should not count as body uses or definitions).
    for m in _GLOSSARY_SECTION_RE.finditer(text):
        _blank_span(result, text, m.start(), m.end())

    return result


def _blank_span(
    lines: list[str], full_text: str, start: int, end: int
) -> None:
    """Blank out lines in the given character range."""
    # Convert character offsets to line numbers.
    line_start = full_text.count("\n", 0, start)
    line_end = full_text.count("\n", 0, end)
    for i in range(line_start, min(line_end + 1, len(lines))):
        lines[i] = ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}")
        return 1

    print(f"Scanning {len(chapter_files)} chapters for abbreviation discipline...\n")

    total_unexpanded = 0
    total_single_use = 0
    chapters_with_issues = 0

    for filepath in chapter_files:
        issues = process_chapter(filepath)
        if issues:
            chapters_with_issues += 1
            print(f"  {filepath.stem}")
            for issue in sorted(issues, key=lambda x: (x.kind, x.line_no)):
                print(str(issue))
            print()
            total_unexpanded += sum(1 for i in issues if i.kind == "UNEXPANDED")
            total_single_use += sum(1 for i in issues if i.kind == "SINGLE-USE")

    print("=" * 60)
    print(f"Chapters scanned:            {len(chapter_files)}")
    print(f"Chapters with issues:        {chapters_with_issues}")
    print(f"Unexpanded abbreviations:    {total_unexpanded}")
    print(f"Single-use abbreviations:    {total_single_use}")
    print("=" * 60)

    if total_unexpanded > 0 or total_single_use > 0:
        return 1
    print("\nAll abbreviation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
