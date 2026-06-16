# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Worked-example arithmetic verification for the Evenwicht textbook.

Extracts every Worked Example from Section 8 of all 48 chapters, finds
explicit arithmetic claims (simple chains of additions, divisions,
multiplications, percentages, and square roots), evaluates them in Python,
and compares the computed result to the stated result.

This is a *conservative* checker: it only verifies patterns it can
reliably parse.  It is better to check 50% of claims correctly than
100% with false positives.

Strategy: only match patterns where the full arithmetic is visible and
unambiguous.  Reject matches that appear to be fragments of larger
expressions (preceding operators, trailing operators, matrix entries,
modular arithmetic, etc.).

Usage:
    python3 verify/verify_worked_examples.py

Also exposes ``build() -> Chapter`` for integration with the verification
framework (run_all.py).
"""

from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework import Chapter, NumericCheck, StructuralCheck

# ---------------------------------------------------------------------------
# Chapter file registry (mirrors verify_proofs.py)
# ---------------------------------------------------------------------------

CHAPTER_FILES = {
    i: f"{i:02d}-{name}.md"
    for i, name in enumerate([
        "",
        "expressions", "special-functions", "limits-continuity",
        "differential-calculus", "integral-calculus", "series-approximation",
        "multivariate-calculus", "vectors", "matrices", "eigenvalues",
        "unconstrained-optimization", "constrained-optimization",
        "probability-theory", "distributions", "descriptive-statistics",
        "statistical-inference", "regression", "difference-equations",
        "odes", "discrete-operators", "time-series", "transforms",
        "operator-algebra", "fractional-calculus", "financial-mathematics",
        "machine-learning", "quantitative-trading", "information-theory",
        "control-systems", "epidemiology", "network-analysis",
        "energy-systems", "equilibrium", "chemical-kinetics",
        "pharmacokinetics", "game-theory", "cryptography",
        "climate-modeling", "mechanics-waves", "signal-processing",
        "orbital-mechanics", "robotics", "fluid-dynamics", "circuits",
        "geology-seismology", "cosmology", "optics-acoustics", "genetics",
    ], start=0)
    if i > 0
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ArithmeticClaim:
    """A single arithmetic claim extracted from a worked example."""
    chapter: int
    example: str          # e.g. "Example 9.1"
    expression: str       # the LHS expression text
    stated_result: float  # the number the text claims
    computed_result: float  # what Python computes
    approximate: bool     # True when the text uses approx
    raw: str              # full matched text for debugging
    ok: bool = False


@dataclass
class ExtractionResult:
    """Aggregated results from all chapters."""
    claims: list[ArithmeticClaim] = field(default_factory=list)
    chapters_processed: int = 0
    chapters_with_examples: int = 0


# ---------------------------------------------------------------------------
# Section / example extraction
# ---------------------------------------------------------------------------

def _extract_section(text: str, section_num: int) -> str:
    """Extract a numbered section from a chapter markdown file."""
    pattern = re.compile(
        rf"^##\s+{section_num}\.\s+.*$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    next_heading = re.search(r"^##\s+\d+\.\s+", text[match.end():], re.MULTILINE)
    if next_heading:
        end = match.end() + next_heading.start()
    else:
        end = len(text)
    return text[start:end]


def _extract_examples(section_text: str) -> list[tuple[str, str]]:
    """Split Section 8 into (example_label, example_body) pairs."""
    examples: list[tuple[str, str]] = []
    parts = re.split(r"(?=^### Example\s+)", section_text, flags=re.MULTILINE)
    for part in parts:
        m = re.match(r"^### (Example\s+[\d.]+)[:\s]", part)
        if m:
            examples.append((m.group(1), part))
    return examples


# ---------------------------------------------------------------------------
# Number parsing helpers
# ---------------------------------------------------------------------------

def _parse_number(s: str) -> float | None:
    """Parse a number string, handling commas and LaTeX thinspaces."""
    s = s.strip()
    if not s:
        return None
    s = s.replace("{,}", "").replace("\\,", "").replace("\u2009", "")
    # Remove digit-grouping commas (e.g. 70,400 -> 70400)
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)
    s = s.replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


def _is_fragment(text: str, match: re.Match) -> bool:
    """Check if a match is part of a larger expression (false positive guard).

    Returns True if the match should be *rejected* because it looks like a
    fragment of a bigger formula.  This is the primary weapon against false
    positives and is deliberately aggressive: rejecting a valid claim is
    much less costly than reporting a bogus mismatch.
    """
    start = match.start()
    end = match.end()

    # --- Context windows ---
    before_wide = text[max(0, start - 30):start]
    before_narrow = text[max(0, start - 5):start]
    after_narrow = text[end:min(len(text), end + 5)]
    after_wide = text[end:min(len(text), end + 30)]

    # --- BEFORE the match ---
    # Reject if immediately preceded by an operator, open paren, comma, &
    if re.search(r"[+\-*/^(,&]$", before_narrow.rstrip()):
        return True
    # Reject if preceded by \cdot, \times, ±, digit (part of bigger expr)
    before_stripped = before_narrow.rstrip()
    if before_stripped.endswith(("\\cdot", "\\times", "\\pm", "\\mp")):
        return True
    # Reject if a digit or closing paren immediately precedes (like 5.35\ln)
    if re.search(r"[\d)]$", before_stripped):
        return True

    # --- AFTER the match ---
    after_stripped = after_narrow.lstrip()
    # Reject if followed by arithmetic operators or open paren
    if re.search(r"^[+\-*/^(]", after_stripped):
        return True
    # Reject if followed by \cdot, \times, \text (units), \pm
    if re.search(r"^\\(?:cdot|times|text|pm|mp)", after_stripped):
        return True
    # Reject if result is followed by / (e.g. 1/15 = 14/15)
    if after_stripped.startswith("/"):
        return True
    # Reject if result is followed by × 10 (scientific notation fragment)
    if re.search(r"^\s*[×x]\s*10", after_wide):
        return True
    if re.search(r"^\s*\\times\s*10", after_wide):
        return True
    # Reject if followed by a % sign (percentage -- would need *100)
    if re.search(r"^\\?%", after_stripped):
        return True
    # Reject if followed by ° (degree symbol -- units attached to result)
    if after_stripped.startswith(("°", "^\\circ")):
        return True
    # Reject if followed by {,} (LaTeX digit grouping -- truncated number)
    if after_stripped.startswith("{,}"):
        return True
    # Reject if followed by a comma and digits (e.g. ",820" in "239,820")
    if re.search(r"^,\d{3}", after_stripped):
        return True

    # --- Modular arithmetic ---
    if "\\pmod" in before_wide or "mod" in after_wide[:10].lower():
        return True
    if "\\bmod" in before_wide or "\\bmod" in after_wide[:10]:
        return True

    # --- Matrix / alignment environments ---
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    if "&" in line:
        return True

    # --- Inside a bigger LaTeX command preceding the match ---
    # Reject if within 30 chars there is a preceding \cdot or \times
    # that is not captured by the narrow window (e.g. "P(0) \cdot 2.5/1")
    if re.search(r"\\(?:cdot|times)\s*$", before_wide):
        return True

    # Reject if preceded by a LaTeX function like \ln, \log, \sin, etc.
    # (e.g. "\ln 2 / 0.035 ≈ 19.8" -- we are matching "2 / 0.035")
    if re.search(r"\\(?:ln|log|sin|cos|tan|exp|sqrt)\s*$", before_wide):
        return True

    # Reject if preceded by \frac{...}{...} (a multiplying fraction)
    if re.search(r"\\frac\{[^}]*\}\{[^}]*\}\s*$", before_wide):
        return True

    # Reject if preceded by \pi (e.g. "2\pi\sqrt{...}")
    if re.search(r"\\pi\s*$", before_wide):
        return True

    return False


# ---------------------------------------------------------------------------
# Pattern matchers -- each returns a list of ArithmeticClaim
#
# IMPORTANT: every matcher calls _is_fragment() to reject partial matches.
# ---------------------------------------------------------------------------

def _find_simple_division(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    """Match patterns like  0.693/0.00247 = 281  in plain text."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"(?<![a-zA-Z_\\(])"                           # not part of word/LaTeX
        r"(\d+(?:\.\d+)?)"                              # numerator
        r"\s*/\s*"
        r"(\d+(?:\.\d+)?)"                              # denominator
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"                            # result
        r"(?!\s*[/(])"                                  # not followed by / or (
        r"(?!\s*\^\{)"                                  # not followed by ^{ (exponent)
        r"(?!\d)"                                       # not a longer number
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        numer_str, denom_str = m.group(1), m.group(2)
        numer = _parse_number(numer_str)
        denom = _parse_number(denom_str)
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if numer is None or denom is None or result is None or denom == 0:
            continue
        # Require at least one decimal operand to reduce false positives
        # from integer expressions like "5/100 = 50 ms"
        if "." not in numer_str and "." not in denom_str:
            continue
        computed = numer / denom
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"{numer}/{denom}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_latex_frac(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    r"""Match \frac{num}{den} = result  or  \frac{num}{den} \approx result."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"\\frac\{(-?\d+(?:\.\d+)?)\}\{(-?\d+(?:\.\d+)?)\}"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/^(])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        numer = _parse_number(m.group(1))
        denom = _parse_number(m.group(2))
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if numer is None or denom is None or result is None or denom == 0:
            continue
        computed = numer / denom
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"\\frac{{{numer}}}{{{denom}}}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_simple_product(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    r"""Match  a \times b = c  or  a \cdot b = c  with decimal operands."""
    claims: list[ArithmeticClaim] = []

    # Only match when at least one operand has a decimal point -- this
    # eliminates most matrix/vector integer products that are partial.
    pat = re.compile(
        r"(?<![a-zA-Z_\\(])"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*(?:\\times|\\cdot|[×])\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/(])"
        r"(?!\s*\^\{)"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        a_str, b_str = m.group(1), m.group(2)
        # Require at least one decimal operand to avoid matching integer
        # fragments like "3 \cdot 2 = 7" from matrix expressions.
        if "." not in a_str and "." not in b_str:
            continue
        a = _parse_number(a_str)
        b = _parse_number(b_str)
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if a is None or b is None or result is None:
            continue
        computed = a * b
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"{a} * {b}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_addition_chain(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    """Match chains like  a + b + c = d  (3+ decimal terms)."""
    claims: list[ArithmeticClaim] = []

    # Require at least 3 terms (2 + operators) and at least one decimal.
    # This avoids matching "2 - 1 = 5" style fragments.
    pat = re.compile(
        r"(?<![a-zA-Z_\\(/*^])"
        r"(-?\d+\.\d+)"                           # first term must have decimal
        r"((?:\s*[+-]\s*\d+(?:\.\d+)?){2,10})"    # 2+ more terms
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/^(])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        chain_str = m.group(1) + m.group(2)
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if result is None:
            continue

        terms = re.findall(r"[+-]?\s*\d+(?:\.\d+)?", chain_str)
        if len(terms) < 3:
            continue
        try:
            values = [float(t.replace(" ", "")) for t in terms]
        except ValueError:
            continue

        computed = sum(values)
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=chain_str.strip(),
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_two_decimal_addition(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    """Match  a + b = c  where both a and b have decimal points."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"(?<![a-zA-Z_\\(/*^])"
        r"(-?\d+\.\d+)"
        r"\s*\+\s*"
        r"(-?\d+\.\d+)"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/^(+\-])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        a = _parse_number(m.group(1))
        b = _parse_number(m.group(2))
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if a is None or b is None or result is None:
            continue
        computed = a + b
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"{a} + {b}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_two_decimal_subtraction(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    """Match  a - b = c  where both a and b have decimal points."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"(?<![a-zA-Z_\\(/*^])"
        r"(\d+\.\d+)"
        r"\s*-\s*"
        r"(\d+\.\d+)"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/^(+\-])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        a = _parse_number(m.group(1))
        b = _parse_number(m.group(2))
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if a is None or b is None or result is None:
            continue
        computed = a - b
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"{a} - {b}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_power_equals(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    """Match  (a.b)^n = c  where the base has a decimal point."""
    claims: list[ArithmeticClaim] = []

    # Only match when base is decimal, e.g. (1.08)^5 = 1.46933
    pat = re.compile(
        r"\((\d+\.\d+)\)\^\{?(\-?\d+(?:\.\d+)?)\}?"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/^(])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        base = _parse_number(m.group(1))
        exp = _parse_number(m.group(2))
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if base is None or exp is None or result is None:
            continue
        try:
            computed = base ** exp
        except (OverflowError, ValueError, ZeroDivisionError):
            continue
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"({base})^{exp}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_sqrt_equals(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    r"""Match \sqrt{number} = b  or \sqrt{a/b} \approx c."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"\\sqrt\{(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?)\}"
        r"\s*(=|≈|\\approx)\s*"
        r"(\d+\.\d+)"                # result must have decimal (avoids \sqrt{2}=1 style)
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        radicand_str = m.group(1)
        approx = m.group(2) in ("≈", "\\approx")
        result = _parse_number(m.group(3))
        if result is None:
            continue
        if "/" in radicand_str:
            parts = radicand_str.split("/")
            numer = _parse_number(parts[0])
            denom = _parse_number(parts[1])
            if numer is None or denom is None or denom == 0:
                continue
            radicand = numer / denom
        else:
            radicand = _parse_number(radicand_str)
        if radicand is None or radicand < 0:
            continue
        computed = math.sqrt(radicand)
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"sqrt({radicand_str})",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_exp_equals(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    r"""Match e^{-2.01} = 0.1340 (exponent and result both with decimals)."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"e\^\{(-?\d+\.\d+)\}"       # exponent must have decimal
        r"\s*(=|≈|\\approx)\s*"
        r"(\d+\.\d+)"                 # result must have decimal
        r"(?!\s*[/^(])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        exponent = _parse_number(m.group(1))
        approx = m.group(2) in ("≈", "\\approx")
        result = _parse_number(m.group(3))
        if exponent is None or result is None:
            continue
        try:
            computed = math.exp(exponent)
        except OverflowError:
            continue
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"e^{{{exponent}}}",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_ln_equals(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    r"""Match \ln(a.b) = c  or  \ln a = c  where result has a decimal."""
    claims: list[ArithmeticClaim] = []

    # \ln followed by a number in parens or braces or standalone
    pat = re.compile(
        r"\\ln\s*"
        r"(?:\(|\\left\()?"
        r"(\d+(?:\.\d+)?)"          # argument
        r"(?:\)|\\right\))?"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+\.\d+)"             # result must have decimal
        r"(?!\s*[/^(])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        arg = _parse_number(m.group(1))
        approx = m.group(2) in ("≈", "\\approx")
        result = _parse_number(m.group(3))
        if arg is None or result is None or arg <= 0:
            continue
        computed = math.log(arg)
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"ln({arg})",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


def _find_parenthesized_product(text: str, chapter: int, example: str) -> list[ArithmeticClaim]:
    """Match (a.b)(c.d) = e  where both factors have decimals."""
    claims: list[ArithmeticClaim] = []

    pat = re.compile(
        r"\((-?\d+\.\d+)\)"
        r"\s*"
        r"\((-?\d+\.\d+)\)"
        r"\s*(=|≈|\\approx)\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"(?!\s*[/^(+\-])"
        r"(?!\d)"
    )

    for m in pat.finditer(text):
        if _is_fragment(text, m):
            continue
        a = _parse_number(m.group(1))
        b = _parse_number(m.group(2))
        approx = m.group(3) in ("≈", "\\approx")
        result = _parse_number(m.group(4))
        if a is None or b is None or result is None:
            continue
        computed = a * b
        rtol = 0.02 if approx else 0.01
        ok = _approx_eq(result, computed, rtol)
        claims.append(ArithmeticClaim(
            chapter=chapter, example=example,
            expression=f"({a})({b})",
            stated_result=result, computed_result=computed,
            approximate=approx, raw=m.group(0), ok=ok,
        ))

    return claims


# ---------------------------------------------------------------------------
# Approximate equality
# ---------------------------------------------------------------------------

def _approx_eq(stated: float, computed: float, rtol: float) -> bool:
    """Check relative approximate equality, with fallback to absolute."""
    if stated == 0.0 and computed == 0.0:
        return True
    if stated == 0.0:
        return abs(computed) < rtol
    return abs(computed - stated) / abs(stated) < rtol


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

ALL_FINDERS = [
    _find_simple_division,
    _find_latex_frac,
    _find_simple_product,
    _find_addition_chain,
    _find_two_decimal_addition,
    _find_two_decimal_subtraction,
    _find_parenthesized_product,
    _find_power_equals,
    _find_sqrt_equals,
    _find_exp_equals,
    _find_ln_equals,
]


def _extract_claims_from_example(
    text: str, chapter: int, example: str,
) -> list[ArithmeticClaim]:
    """Run all pattern matchers on a single example body."""
    claims: list[ArithmeticClaim] = []
    for finder in ALL_FINDERS:
        claims.extend(finder(text, chapter, example))
    return claims


def extract_and_check_all(docs_dir: str) -> ExtractionResult:
    """Extract and check all arithmetic claims from worked examples."""
    result = ExtractionResult()

    for ch_num, filename in sorted(CHAPTER_FILES.items()):
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        result.chapters_processed += 1

        section8 = _extract_section(text, 8)
        if not section8:
            continue

        examples = _extract_examples(section8)
        if not examples:
            continue

        result.chapters_with_examples += 1
        chapter_claims: list[ArithmeticClaim] = []

        for ex_label, ex_body in examples:
            claims = _extract_claims_from_example(ex_body, ch_num, ex_label)
            chapter_claims.extend(claims)

        # Deduplicate claims that share the same raw match text
        seen_raw: set[str] = set()
        for claim in chapter_claims:
            key = f"{claim.chapter}:{claim.example}:{claim.raw}"
            if key not in seen_raw:
                seen_raw.add(key)
                result.claims.append(claim)

    return result


# ---------------------------------------------------------------------------
# Framework integration: build() -> Chapter
# ---------------------------------------------------------------------------

def build() -> Chapter:
    """Build a Chapter of checks for the verification framework."""
    ch = Chapter(202, "Worked-Example Arithmetic Verification")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs", "domains")

    result = extract_and_check_all(docs_dir)

    # Structural check: examples were extracted from chapters
    def check_extraction() -> tuple[bool, str]:
        if result.chapters_with_examples >= 10:
            return True, ""
        return False, (
            f"Only {result.chapters_with_examples} chapters had extractable "
            f"worked examples (expected >= 10)"
        )

    ch.add(StructuralCheck(
        label="Worked examples found in >= 10 chapters",
        section="8",
        predicate=check_extraction,
    ))

    # Structural check: claims were extracted
    def check_claims_found() -> tuple[bool, str]:
        if len(result.claims) >= 20:
            return True, ""
        return False, (
            f"Only {len(result.claims)} arithmetic claims extracted "
            f"(expected >= 20)"
        )

    ch.add(StructuralCheck(
        label="At least 20 arithmetic claims extracted",
        section="8",
        predicate=check_claims_found,
    ))

    # Structural check: overall pass rate
    def check_pass_rate() -> tuple[bool, str]:
        if not result.claims:
            return True, ""
        passed = sum(1 for c in result.claims if c.ok)
        total = len(result.claims)
        rate = passed / total
        if rate >= 0.90:
            return True, ""
        return False, (
            f"Only {passed}/{total} ({rate:.0%}) arithmetic claims passed "
            f"(threshold: 90%)"
        )

    ch.add(StructuralCheck(
        label="Arithmetic claim pass rate >= 90%",
        section="8",
        predicate=check_pass_rate,
    ))

    # Add individual NumericChecks for each claim
    for claim in result.claims:
        tol = 0.02 if claim.approximate else 0.01
        ch.add(NumericCheck(
            label=(
                f"Ch {claim.chapter:02d} {claim.example}: "
                f"{claim.expression}"
            ),
            section="8",
            stated=claim.stated_result,
            computed=claim.computed_result,
            tolerance=tol,
            note="approx" if claim.approximate else "",
        ))

    return ch


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run worked-example arithmetic verification as a standalone script."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs", "domains")

    print("Extracting arithmetic claims from worked examples (Section 8)...")
    result = extract_and_check_all(docs_dir)

    print(f"  Chapters processed: {result.chapters_processed}")
    print(f"  Chapters with worked examples: {result.chapters_with_examples}")
    print(f"  Total arithmetic claims extracted: {len(result.claims)}")

    passed = sum(1 for c in result.claims if c.ok)
    failed = [c for c in result.claims if not c.ok]
    print(f"  Passed: {passed}")
    print(f"  Failed: {len(failed)}")
    if result.claims:
        print(f"  Pass rate: {passed / len(result.claims):.1%}")

    # Show failures
    if failed:
        print(f"\nMismatches ({len(failed)}):")
        for c in failed:
            approx_tag = " (approx)" if c.approximate else ""
            print(
                f"  Ch {c.chapter:02d} | {c.example} | "
                f"{c.expression} => stated {c.stated_result}, "
                f"computed {c.computed_result:.6g}{approx_tag}"
            )
            print(f"    raw: {c.raw[:120]}")

    # Show summary by chapter
    print("\nPer-chapter summary:")
    from collections import Counter
    ch_total: Counter[int] = Counter()
    ch_pass: Counter[int] = Counter()
    for c in result.claims:
        ch_total[c.chapter] += 1
        if c.ok:
            ch_pass[c.chapter] += 1
    for ch_num in sorted(ch_total):
        t = ch_total[ch_num]
        p = ch_pass[ch_num]
        status = "OK" if p == t else "ISSUES"
        print(f"  Ch {ch_num:02d}: {p}/{t} [{status}]")

    # Run framework checks
    print("\nRunning framework checks...")
    chapter = build()
    chapter.run()
    structural_results = [r for r in chapter.results if r.layer.value == "STRUCTURAL"]
    for r in structural_results:
        icon = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERR!", "SKIP": "SKIP"}[
            r.status.value
        ]
        print(f"  [{icon}] {r.label}")
        if r.message:
            print(f"         {r.message}")

    # Final summary from framework
    print(f"\nFramework: {chapter.passed}/{chapter.total} passed, "
          f"{chapter.failed} failed, {chapter.errors} errors")


if __name__ == "__main__":
    main()
