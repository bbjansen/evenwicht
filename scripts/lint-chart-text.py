#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Lint Mermaid chart text for plain-text math that should use Unicode.

Scans all domain chapter files for xychart-beta and other Mermaid diagrams,
extracts titles, axis labels, and line/bar labels, then flags plain-text
math notation that should be replaced with proper Unicode symbols.

Checks for:
  1. Caret (^) used as superscript  →  Unicode superscripts (², ³, ˣ, ⁿ, …)
  2. Underscore (_) used as subscript  →  Unicode subscripts (₀, ₙ, ₜ, …)
  3. Spelled-out Greek letters  →  Unicode Greek (theta → θ, phi → φ, …)
  4. ASCII math operators  →  proper symbols (sqrt → √, * → ·, etc.)
  5. Common notation patterns  →  Unicode (CO2 → CO₂, log10 → log₁₀, …)
  6. Typographic issues  →  proper characters (- as minus → −, ' as prime → ′)

Usage:
    python3 scripts/lint-chart-text.py           # lint all domain files
    python3 scripts/lint-chart-text.py --fix     # show suggested replacements
    python3 scripts/lint-chart-text.py FILE ...  # lint specific files

Exit code 0 if no issues found, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ── Project layout ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# ── Issue reporting ───────────────────────────────────────────────────────────


@dataclass
class Issue:
    """A single lint finding."""

    file: str
    line: int
    text: str
    message: str
    suggestion: str

    def __str__(self) -> str:
        short = self.text
        if len(short) > 80:
            short = short[:77] + "..."
        return f"  {self.file}:{self.line}: {self.message}\n    | {short}"

    def verbose(self) -> str:
        short = self.text
        if len(short) > 80:
            short = short[:77] + "..."
        return (
            f"  {self.file}:{self.line}: {self.message}\n"
            f"    | {short}\n"
            f"    → {self.suggestion}"
        )


# ── Greek letter mapping ─────────────────────────────────────────────────────

GREEK_MAP: dict[str, str] = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "zeta": "ζ",
    "eta": "η",
    "theta": "θ",
    "iota": "ι",
    "kappa": "κ",
    "lambda": "λ",
    "mu": "μ",
    "nu": "ν",
    "xi": "ξ",
    "pi": "π",
    "rho": "ρ",
    "sigma": "σ",
    "tau": "τ",
    "upsilon": "υ",
    "phi": "φ",
    "chi": "χ",
    "psi": "ψ",
    "omega": "ω",
    "Gamma": "Γ",
    "Delta": "Δ",
    "Theta": "Θ",
    "Lambda": "Λ",
    "Pi": "Π",
    "Sigma": "Σ",
    "Phi": "Φ",
    "Psi": "Ψ",
    "Omega": "Ω",
}

# Words/phrases that happen to contain Greek letter names but aren't Greek.
# Also includes cases where the Greek name is used as a proper noun
# (e.g. "Gamma Function" is the function's name, not the symbol Γ).
GREEK_FALSE_POSITIVES: set[str] = {
    "piecewise", "pipeline", "multiple", "simple", "example",
    "compute", "complete", "template", "update", "capture",
    "approximate", "etail", "detail", "beta-",  # compound words
}

# Patterns where a Greek letter name is used as a proper noun / title word,
# not as a math symbol.  E.g. "Gamma Function", "Delta Force".
_GREEK_PROPER_RE = re.compile(
    r"\b(Gamma|Delta|Theta|Lambda|Sigma|Omega|Pi|Chi)\s+[A-Z]"
)

# ── Superscript / subscript maps ─────────────────────────────────────────────

SUPERSCRIPT_DIGITS: dict[str, str] = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
}

SUPERSCRIPT_LETTERS: dict[str, str] = {
    "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ",
    "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ",
    "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ",
    "p": "ᵖ", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ",
    "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ",
    "D": "ᴰ",
}

SUBSCRIPT_DIGITS: dict[str, str] = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
}

SUBSCRIPT_LETTERS: dict[str, str] = {
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ",
    "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ",
    "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ",
    "v": "ᵥ", "x": "ₓ",
}

# ── Compound patterns ─────────────────────────────────────────────────────────

# Patterns that should be flagged with specific suggestions.
# Each entry: (compiled regex, message template, suggestion template).
# Templates may use \1, \2 etc. for captured groups.

COMPOUND_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    # CO2 without subscript (but not already CO₂)
    (
        re.compile(r"\bCO2\b"),
        "plain 'CO2' should use subscript",
        "CO₂",
    ),
    # log10 without subscript
    (
        re.compile(r"\blog10\b"),
        "plain 'log10' should use subscript",
        "log₁₀",
    ),
    # N0, A0, I0, V0, t0 etc. as subscript-zero patterns
    (
        re.compile(r"\b([A-Z])0\b(?!\.)"),
        "'\\1₀' — use subscript zero",
        "\\1₀",
    ),
    # Vmax / vmax without subscript
    (
        re.compile(r"\b([Vv])max\b"),
        "'\\1max' should use subscript",
        "\\1ₘₐₓ",
    ),
    # v_max, x_max etc. underscore subscript
    (
        re.compile(r"\b([a-zA-Z])_max\b"),
        "'\\1_max' should use subscript",
        "\\1ₘₐₓ",
    ),
    # sqrt() instead of √
    (
        re.compile(r"\bsqrt\("),
        "'sqrt(' should use √",
        "√(",
    ),
    # ||...|| for norms instead of ‖...‖
    (
        re.compile(r"\|\|"),
        "'||' should use ‖ (double vertical bar)",
        "‖",
    ),
    # grad (as in "grad f") instead of ∇
    (
        re.compile(r"\bgrad\b"),
        "'grad' should use ∇",
        "∇",
    ),
    # Gamma(x) function notation
    (
        re.compile(r"\bGamma\("),
        "'Gamma(' should use Γ(",
        "Γ(",
    ),
    # Chi-Squared / Chi-Square
    (
        re.compile(r"\bChi-Squared?\b"),
        "'Chi-Squared' should use χ²",
        "χ²",
    ),
    # "std dev" should be σ
    (
        re.compile(r"\bstd dev\b"),
        "'std dev' should use σ",
        "σ",
    ),
]

# ── Chart element extraction ──────────────────────────────────────────────────

# Matches Mermaid chart text elements:
#   title: "..."  or  title "..."
#   x-axis "..."  or  y-axis "..."
#   line "..."    or  bar "..."
_CHART_ELEMENT_RE = re.compile(
    r"""
    (?:
        ^title:\s*"([^"]*)"               # title: "text"
      | ^\s*title\s+"([^"]*)"             # title "text" (inline)
      | ^\s*(?:x-axis|y-axis)\s+"([^"]*)" # axis "label"
      | ^\s*(?:line|bar)\s+"([^"]*)"       # series "label"
    )
    """,
    re.VERBOSE,
)


def extract_chart_texts(
    lines: list[str],
) -> list[tuple[int, str, str]]:
    """Extract (line_number, element_type, text) from Mermaid chart elements.

    Only extracts from within ```mermaid ... ``` blocks.
    """
    results: list[tuple[int, str, str]] = []
    in_mermaid = False

    for i, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        if stripped.startswith("```mermaid"):
            in_mermaid = True
            continue
        if stripped.startswith("```") and in_mermaid:
            in_mermaid = False
            continue
        if not in_mermaid:
            continue

        m = _CHART_ELEMENT_RE.match(stripped)
        if not m:
            continue

        # Determine which group matched
        for g_idx, group in enumerate(m.groups(), start=1):
            if group is not None:
                elem_type = ["title-front", "title-inline",
                             "axis", "series"][g_idx - 1]
                results.append((i, elem_type, group))
                break

    return results


# ── Lint checks ───────────────────────────────────────────────────────────────


def check_caret(text: str) -> list[tuple[str, str]]:
    """Flag ^ used as superscript."""
    findings: list[tuple[str, str]] = []
    if "^" in text:
        # Extract the superscript expression
        for m in re.finditer(r"(\w)\^(\(?)([a-zA-Z0-9+\-*/]+)\)?", text):
            base, exp = m.group(1), m.group(3)
            # Try to build Unicode superscript
            all_maps = {**SUPERSCRIPT_DIGITS, **SUPERSCRIPT_LETTERS, "+": "⁺", "-": "⁻"}
            sup = ""
            convertible = True
            for ch in exp:
                if ch in all_maps:
                    sup += all_maps[ch]
                else:
                    convertible = False
                    break
            if convertible and sup:
                findings.append(
                    (f"'^{exp}' should use superscript", f"{base}{sup}")
                )
            else:
                findings.append(
                    (f"'^' notation — consider Unicode superscript", text)
                )
    return findings


def check_underscore(text: str) -> list[tuple[str, str]]:
    """Flag _ used as subscript in variable names."""
    findings: list[tuple[str, str]] = []
    for m in re.finditer(r"(\w)_([a-zA-Z0-9]+)", text):
        base, sub_text = m.group(1), m.group(2)
        # Try to build Unicode subscript
        all_maps = {**SUBSCRIPT_DIGITS, **SUBSCRIPT_LETTERS}
        sub = ""
        convertible = True
        for ch in sub_text:
            if ch in all_maps:
                sub += all_maps[ch]
            else:
                convertible = False
                break
        if convertible and sub:
            findings.append(
                (f"'_{sub_text}' should use subscript", f"{base}{sub}")
            )
        else:
            findings.append(
                (f"'_{sub_text}' — not all chars have Unicode subscript forms",
                 f"consider rewriting '{m.group(0)}'")
            )
    return findings


def check_greek(text: str) -> list[tuple[str, str]]:
    """Flag spelled-out Greek letters used as math symbols."""
    findings: list[tuple[str, str]] = []
    for name, symbol in GREEK_MAP.items():
        pattern = re.compile(rf"\b{re.escape(name)}\b")
        if not pattern.search(text):
            continue
        for m in pattern.finditer(text):
            start, end = m.start(), m.end()
            # Check surrounding context for false positives
            ctx_start = max(0, start - 10)
            ctx_end = min(len(text), end + 10)
            context = text[ctx_start:ctx_end].lower()
            if any(fp in context for fp in GREEK_FALSE_POSITIVES):
                continue
            # Skip proper-noun usage like "Gamma Function"
            if _GREEK_PROPER_RE.match(text, start):
                continue
            findings.append(
                (f"'{name}' should use {symbol}", symbol)
            )
            break  # one finding per Greek letter per text
    return findings


def check_asterisk_multiply(text: str) -> list[tuple[str, str]]:
    """Flag * used as multiplication between terms."""
    findings: list[tuple[str, str]] = []
    # Match patterns like "A0 * e^(-kt)" or "delta*k"
    if re.search(r"\w\s*\*\s*\w", text):
        findings.append(
            ("'*' as multiplication should use · (middle dot)", "·")
        )
    return findings


def check_hyphen_minus(text: str) -> list[tuple[str, str]]:
    """Flag hyphen-minus used as math minus sign (with spaces around it)."""
    findings: list[tuple[str, str]] = []
    # Pattern: <alnum> - <alnum> where it looks like subtraction
    # Exclude compound words like "Bias-Variance"
    for m in re.finditer(r"(?<=[0-9a-z]) - (?=[0-9a-z])", text):
        # Check it's not a compound word (both sides alpha)
        start, end = m.start(), m.end()
        ctx = text[max(0, start - 5):min(len(text), end + 5)]
        if re.search(r"[0-9=+]", ctx):
            findings.append(
                ("hyphen '-' used as minus — use '−' (U+2212)", "−")
            )
            break
    return findings


def check_apostrophe_prime(text: str) -> list[tuple[str, str]]:
    """Flag apostrophe used as prime in math notation like f'(x)."""
    findings: list[tuple[str, str]] = []
    # Match f'(x) or f''(x) patterns but not possessives like Newton's
    if re.search(r"[a-z]'(?:\(|[²³])", text):
        findings.append(
            ("apostrophe as prime — use ′ (U+2032)", "′")
        )
    return findings


# ── Main lint runner ──────────────────────────────────────────────────────────


def lint_file(filepath: Path) -> list[Issue]:
    """Run all checks on a single file and return issues found."""
    issues: list[Issue] = []
    try:
        rel_path = filepath.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_path = filepath
    lines = filepath.read_text(encoding="utf-8").splitlines()
    chart_texts = extract_chart_texts(lines)

    for line_no, _elem_type, text in chart_texts:
        findings: list[tuple[str, str]] = []

        # Run compound pattern checks first (more specific)
        compound_matched: set[str] = set()
        for pattern, msg_template, sug_template in COMPOUND_PATTERNS:
            m = pattern.search(text)
            if m:
                msg = pattern.sub(msg_template, m.group(0))
                sug = pattern.sub(sug_template, m.group(0))
                findings.append((msg, sug))
                compound_matched.add(m.group(0))

        # Run generic checks, skipping underscore findings already
        # covered by compound patterns
        findings.extend(check_caret(text))
        for msg, sug in check_underscore(text):
            # Skip if the match was already caught by a compound pattern
            if any(cm in text for cm in compound_matched
                   if "_" in cm):
                continue
            findings.append((msg, sug))
        findings.extend(check_greek(text))
        findings.extend(check_asterisk_multiply(text))
        findings.extend(check_hyphen_minus(text))
        findings.extend(check_apostrophe_prime(text))

        for message, suggestion in findings:
            issues.append(Issue(
                file=str(rel_path),
                line=line_no,
                text=text,
                message=message,
                suggestion=suggestion,
            ))

    return issues


def discover_files(paths: list[str] | None = None) -> list[Path]:
    """Find files to lint."""
    if paths:
        return [Path(p).resolve() for p in paths]
    return sorted(DOCS_DIR.glob("*.md"))


# ── CLI entry point ───────────────────────────────────────────────────────────


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Lint Mermaid chart text for plain-text math notation.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to lint (default: all domain chapters).",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show suggested replacements for each issue.",
    )
    args = parser.parse_args()

    files = discover_files(args.files if args.files else None)
    all_issues: list[Issue] = []

    for filepath in files:
        all_issues.extend(lint_file(filepath))

    if not all_issues:
        print("✓ No plain-text math found in chart elements.")
        return 0

    # Group by file
    by_file: dict[str, list[Issue]] = {}
    for issue in all_issues:
        by_file.setdefault(issue.file, []).append(issue)

    print(f"Found {len(all_issues)} issue(s) in {len(by_file)} file(s):\n")

    for filename, issues in sorted(by_file.items()):
        print(f"── {filename} ──")
        for issue in issues:
            if args.fix:
                print(issue.verbose())
            else:
                print(issue)
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
