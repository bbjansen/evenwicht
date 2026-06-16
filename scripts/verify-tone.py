#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify tone and diction across all 48 domain chapters.

Checks every domain chapter against the rules in docs/TONE-GUIDE.md:

  1. Forbidden words and phrases (overused, imprecise or AI-characteristic).
  2. Hagiographic language in body text and reference annotations.
  3. Forbidden metaphors (dead metaphors, filler imagery).
  4. First/second person pronouns in body text.
  5. Oxford commas (", and " / ", or " patterns).
  6. Sentence-initial connectives (Therefore, Hence, Thus, etc.).
  7. Em dashes (prohibited; use semicolons or full stops).
  8. Informal language (basically, just, simply, etc.).
  9. Hagiographic reference annotations (editorial superlatives in
     the References section specifically).

Markup (LaTeX math, mermaid blocks, code blocks, HTML comments) is
stripped before checking so that false positives from formulae, code
or diagram syntax are avoided.

Usage:
  python3 scripts/verify-tone.py              # check all 48 chapters
  python3 scripts/verify-tone.py --quick      # check first 3 chapters (CI)

Exit code 1 if any FAIL-level issues are found.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# ── ANSI colours ────────────────────────────────────

_BOLD = "\033[1m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_GREEN = "\033[92m"
_CYAN = "\033[96m"
_RESET = "\033[0m"

FAIL = f"{_RED}FAIL{_RESET}"
WARN = f"{_YELLOW}WARN{_RESET}"
PASS = f"{_GREEN}PASS{_RESET}"
INFO = f"{_CYAN}INFO{_RESET}"


# ── File discovery ──────────────────────────────────

def discover_files(quick: bool = False) -> list[Path]:
    """Return sorted list of domain chapter Markdown files."""
    files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if quick:
        files = files[:3]
    return files


# ── Markup stripping ────────────────────────────────
#
# We replace stripped content with the same number of newlines so that
# line numbers remain valid for reporting.

_RE_MERMAID = re.compile(r"^```mermaid.*?^```", re.MULTILINE | re.DOTALL)
_RE_FENCED_CODE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_RE_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_RE_DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_RE_INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)(?!\s)(.+?)(?<!\s)\$(?!\$)")
_RE_INLINE_CODE = re.compile(r"`[^`]+`")
_RE_YAML_FRONT = re.compile(r"^---\n.*?\n---", re.DOTALL)


def _replace_keep_newlines(match: re.Match) -> str:
    """Replace match content with whitespace, preserving line count."""
    return "\n" * match.group().count("\n")


def strip_markup(text: str) -> str:
    """Remove LaTeX math, code blocks, mermaid, HTML comments from text.

    Preserves line numbering by replacing removed content with newlines.
    """
    for pattern in [
        _RE_YAML_FRONT,
        _RE_MERMAID,
        _RE_FENCED_CODE,
        _RE_HTML_COMMENT,
        _RE_DISPLAY_MATH,
    ]:
        text = pattern.sub(_replace_keep_newlines, text)

    # Per-line stripping for inline constructs
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line = _RE_INLINE_MATH.sub(" ", line)
        line = _RE_INLINE_CODE.sub(" ", line)
        lines[i] = line
    return "\n".join(lines)


# ── Section extraction ──────────────────────────────

def extract_references_section(text: str) -> tuple[int, int]:
    """Return (start_line, end_line) of the ## References section (1-indexed).

    Returns (0, 0) if not found.
    """
    lines = text.split("\n")
    start = 0
    for i, line in enumerate(lines):
        if re.match(r"^## (?:\d+\.\s*)?References\s*$", line):
            start = i + 1
            break
    if not start:
        return 0, 0
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^## \d+\.", lines[i]):
            end = i
            break
    return start, end


# ── Pattern definitions ─────────────────────────────
#
# Each check returns a list of (line_number, severity, category, message).
# Severity is "FAIL" or "WARN".

Issue = tuple[int, str, str, str]


# 1. Forbidden words/phrases (TONE-GUIDE.md table)
#    Whole-word matching, case-insensitive.
#    Multi-word phrases are matched as literal substrings.

FORBIDDEN_PHRASES: list[tuple[str, str, str]] = [
    # (pattern_text, replacement_hint, severity)
    # -- Single words / short phrases from the table --
    ("utilize", "use", "FAIL"),
    ("utilise", "use", "FAIL"),
    ("leverage", "use; exploit", "FAIL"),
    ("facilitate", "enable; allow", "FAIL"),
    ("comprehensive", "thorough; complete", "FAIL"),
    ("robust", "stable; reliable", "FAIL"),
    ("notable", "omit or rewrite", "FAIL"),
    ("noteworthy", "omit or rewrite", "FAIL"),
    ("crucial", "necessary; important", "FAIL"),
    ("critical", "necessary; important", "FAIL"),
    ("vital", "necessary; important", "FAIL"),
    ("essential", "necessary; important", "FAIL"),
    ("importantly", "omit", "FAIL"),
    ("arguably", "omit", "FAIL"),
    ("essentially", "omit", "FAIL"),
    ("basically", "omit", "FAIL"),
    ("furthermore", "omit or use 'and'", "FAIL"),
    ("moreover", "omit or use 'and'", "FAIL"),
    ("interestingly", "omit", "FAIL"),
    ("remarkably", "omit", "FAIL"),
    ("delve", "examine; study", "FAIL"),
    ("paradigm", "model; framework", "FAIL"),
    ("holistic", "complete; unified", "FAIL"),
    ("synergy", "omit", "FAIL"),
    # -- Multi-word forbidden phrases --
    ("in order to", "to", "FAIL"),
    ("it is worth noting", "omit", "FAIL"),
    ("it should be noted", "omit", "FAIL"),
    ("a wide range of", "many; various", "FAIL"),
    ("plays a key role", "matters; is central", "FAIL"),
    ("serves as", "is", "FAIL"),
    ("in the context of", "in; for; during", "FAIL"),
    ("with respect to", "for; of; about", "FAIL"),
    ("it is important to", "omit", "FAIL"),
    ("it turns out that", "omit", "FAIL"),
    ("the fact that", "that", "FAIL"),
    ("due to the fact that", "because", "FAIL"),
    ("in light of", "given; because of", "FAIL"),
    ("a number of", "several; some", "FAIL"),
    ("at the end of the day", "omit", "FAIL"),
    ("needless to say", "omit", "FAIL"),
    ("cutting-edge", "current; modern; recent", "FAIL"),
    ("cutting edge", "current; modern; recent", "FAIL"),
    ("state-of-the-art", "current; modern; recent", "FAIL"),
    ("state of the art", "current; modern; recent", "FAIL"),
    ("real-world", "practical; applied", "FAIL"),
    ("real world", "practical; applied", "FAIL"),
    ("as mentioned above", "omit", "FAIL"),
    ("as we have seen", "omit", "FAIL"),
]

# Compile word-boundary patterns for single/multi-word forbidden items
_FORBIDDEN_COMPILED: list[tuple[re.Pattern, str, str, str]] = []
for _phrase, _repl, _sev in FORBIDDEN_PHRASES:
    _pat = re.compile(r"\b" + re.escape(_phrase) + r"\b", re.IGNORECASE)
    _FORBIDDEN_COMPILED.append((_pat, _phrase, _repl, _sev))

# "significant" -- only forbidden outside statistics context
_RE_SIGNIFICANT = re.compile(r"\bsignificant(?:ly)?\b", re.IGNORECASE)
_STAT_CONTEXT = re.compile(
    r"(?:statistic|p-value|confidence|hypothesis|test|sample|regression"
    r"|variance|correlation|significance level|chi-square|t-test|z-test"
    r"|ANOVA|F-test|Mann.Whitney|Wilcoxon|Kruskal|Kolmogorov)",
    re.IGNORECASE,
)

# ── Mathematical term exemptions ────────────────────
#
# Certain forbidden words are standard mathematical terms in specific
# phrases.  These are exempted when they appear in their technical sense.
#
# "essential" -- exempt in "essential discontinuity", "essential singularity",
#                "essential supremum/infimum", "essentially bounded"
_ESSENTIAL_MATH_CONTEXT = re.compile(
    r"\bessential(?:ly)?\s+(?:discontinuit|singularit|supremum|infimum|bounded"
    r"|self-adjoint|spectrum|range|support|unique)",
    re.IGNORECASE,
)
# Also exempt when the line contains "discontinuity/singularity" nearby
# (e.g. figure captions, glossary entries referencing the term)
_ESSENTIAL_NEARBY_MATH = re.compile(
    r"(?:discontinuit|singularit)", re.IGNORECASE,
)
# Also exempt when preceded by a word indicating it is a formal term name
_ESSENTIAL_TERM_NAME = re.compile(
    r"(?:called|termed|known\s+as|type|an)\s+\"?(?:essential|Essential)",
    re.IGNORECASE,
)

# "critical" -- exempt in "critical point", "critical value", "critical exponent",
#               "critical temperature", "critical damping", "critical path"
_CRITICAL_MATH_CONTEXT = re.compile(
    r"\bcritical\s+(?:point|value|exponent|temperature|damping|path|number"
    r"|pressure|load|frequency|angle|speed|region|line|mass|radius|density"
    r"|threshold|state|phenomena|behaviour|behavior|section|assembly"
    r"|concentration|buckling|Reynolds|flux|current|heat|size|volume)"
    r"|\bcritical\b\s*(?:if|when|\*)",
    re.IGNORECASE,
)

# "vital" -- exempt in epidemiology/demography domain usage:
#            "vital dynamics", "vital rates", "vital statistics"
_VITAL_DOMAIN_CONTEXT = re.compile(
    r"\bvital\s+(?:dynamic|rate|statistic|registration|event|record)",
    re.IGNORECASE,
)

# "with respect to" -- exempt in mathematical usage (differentiation,
#   integration, convergence, orthogonality, etc.)
_WRT_MATH_CONTEXT = re.compile(
    r"(?:differentiat|integrat|deriv|partial|convergence|converge|orthogonal"
    r"|independent|measur|invariant|symmetric|monoton|continuous|limit"
    r"|gradient|loss|cost|objective|entropy|likelihood|expectation|variance"
    r"|covariance|moment|pdf|density|distribution|function|yield|price"
    r"|rate|sensitivity|elasticity|Jacobian|Hessian|Taylor"
    r"|with\s+respect\s+to\s+(?:the\s+)?(?:variable|parameter|measure"
    r"|norm|metric|inner\s+product|basis|coordinate|component|time"
    r"|weight|input|output|each|all|any|both|every|this|that|its|$))",
    re.IGNORECASE,
)

# "robust" -- exempt in "robust statistics", "robust estimation",
#             "robust control", "robust optimisation/optimization"
_ROBUST_MATH_CONTEXT = re.compile(
    r"(?:\brobust\s+(?:statistic|estimat|control|optimi|regression|standard"
    r"|inference|filter|test|method|rank|PCA|covariance|measure|scale"
    r"|median|trimmed|Winsoris|M-estimat|breakdown|resistant|Huber)"
    r"|\brobust\s+to\b|\bmore\s+robust\b|\bis\s+robust\b)",
    re.IGNORECASE,
)

# "landscape" / "ecosystem" -- only forbidden in figurative use
_RE_LANDSCAPE_FIG = re.compile(r"\blandscape\b", re.IGNORECASE)
_RE_ECOSYSTEM_FIG = re.compile(r"\becosystem\b", re.IGNORECASE)
_LITERAL_LANDSCAPE_CONTEXT = re.compile(
    r"(?:geolog|terrain|topograph|erosion|sediment|mountain|valley|coast"
    r"|seismic|tectonic|geomorphol|watershed|floodplain|elevation|satellite)",
    re.IGNORECASE,
)
_LITERAL_ECOSYSTEM_CONTEXT = re.compile(
    r"(?:biolog|ecolog|species|habitat|biodivers|organism|food.?chain"
    r"|predator|prey|population dynamics|carrying capacity|trophic"
    r"|conservation|wildlife)",
    re.IGNORECASE,
)


# 2. Hagiographic language
HAGIOGRAPHIC_WORDS: list[tuple[str, str]] = [
    ("groundbreaking", "FAIL"),
    ("brilliant", "FAIL"),
    ("genius", "FAIL"),
    ("visionary", "FAIL"),
    ("pioneer", "FAIL"),
    ("pioneering", "FAIL"),
    ("revolutionary", "FAIL"),
    ("seminal", "FAIL"),
    ("landmark", "FAIL"),
    ("masterwork", "FAIL"),
    ("masterpiece", "FAIL"),
    ("definitive", "WARN"),
    ("elegant", "WARN"),
    ("exceptional", "WARN"),
    ("outstanding", "WARN"),
    ("classic", "WARN"),
    ("founding", "WARN"),
    ("foundational", "WARN"),
]

_HAGIOGRAPHIC_COMPILED: list[tuple[re.Pattern, str, str]] = []
for _word, _sev in HAGIOGRAPHIC_WORDS:
    _pat = re.compile(r"\b" + re.escape(_word) + r"\b", re.IGNORECASE)
    _HAGIOGRAPHIC_COMPILED.append((_pat, _word, _sev))


# 3. Forbidden metaphors
FORBIDDEN_METAPHORS: list[str] = [
    "toolbox", "toolkit", "building blocks", "building block",
    "backbone", "cornerstone", "pillar", "bedrock",
    "roadmap", "journey",
]

_FORBIDDEN_METAPHOR_COMPILED: list[tuple[re.Pattern, str]] = []
for _m in FORBIDDEN_METAPHORS:
    _pat = re.compile(r"\b" + re.escape(_m) + r"\b", re.IGNORECASE)
    _FORBIDDEN_METAPHOR_COMPILED.append((_pat, _m))

# "bridge" -- only forbidden in figurative use ("bridge between fields")
_RE_BRIDGE_FIG = re.compile(
    r"\bbridge\b(?:\s+(?:between|connecting|across|from\b.*?\bto))",
    re.IGNORECASE,
)

# "power" -- forbidden as "power of X method/technique/approach"
_RE_POWER_FIG = re.compile(
    r"\bpower\s+of\s+(?:the\s+|this\s+|a\s+)?(?:method|technique|approach|tool|framework|concept)",
    re.IGNORECASE,
)

# "beauty" / "elegance" -- forbidden as metaphors
_RE_BEAUTY = re.compile(
    r"\b(?:beauty|elegance)\s+of\b", re.IGNORECASE,
)

# "lens" -- only forbidden in figurative use ("lens through which to view")
# Exempt in optics/photography/physics context
_RE_LENS_FIG = re.compile(r"\blens\b", re.IGNORECASE)
_LITERAL_LENS_CONTEXT = re.compile(
    r"(?:optic|focal|convex|concave|converging|diverging|refract|ABCD"
    r"|magnif|aperture|camera|microscop|telescop|photo|image|object"
    r"|dioptre|diopter|curvature|spherical|thin\s+lens|thick\s+lens"
    r"|lensmaker|chromatic|aberration|biconvex|biconcave|plano"
    r"|meniscus|achromat|eyepiece|objective|beam|ray|glass"
    r"|crystalline|cornea|retina|pupil|iris|mm\b|\bmm\b|system"
    r"|two-lens|single-lens|multi-lens|compound\s+lens|eye|Fresnel"
    r"|f_|f\s*=|corrective|contact|spectacle)",
    re.IGNORECASE,
)


# 4. First/second person
_RE_FIRST_PERSON = re.compile(
    r"\b(?:we\s+(?:compute|have|see|show|obtain|define|write|note|assume|"
    r"consider|derive|denote|observe|introduce|prove|use|recall|"
    r"proceed|apply|begin|conclude|construct|examine|present|"
    r"establish|find|get|know|need|set|take|want|wish|shall|can|"
    r"may|must|will|now|first|then|next|also|thus|hence|therefore|"
    r"further|start|turn|let|require|restrict|look|treat|study|"
    r"review|discuss|state|describe|explore|investigate|adopt|arrive|"
    r"collect|combine|compare|continue|deduce|develop|distinguish|"
    r"encounter|evaluate|express|formulate|identify|illustrate|"
    r"invoke|mention|model|motivate|notice|offer|outline|point|"
    r"refer|replace|represent|return|select|solve|summarise|"
    r"summarize|suppose|verify|work|remark|check|aim|seek))\b",
    re.IGNORECASE,
)
_RE_SECOND_PERSON = re.compile(
    r"\b(?:you\s+(?:can|may|will|should|must|might|would|could|need|want|"
    r"see|note|have|get|find|know|compute|recall|observe|verify|"
    r"check|notice))\b",
    re.IGNORECASE,
)
_RE_I_PRONOUN = re.compile(
    r"\bI\s+(?:note|show|prove|compute|define|assume|shall|will|have|am)\b"
)
# Heading / list / admonition line detection
_RE_HEADING = re.compile(r"^\s*#{1,6}\s+")
_RE_FIGURE_CAPTION = re.compile(r"^\*Figure\s+\d+")
_RE_TABLE_ROW = re.compile(r"^\s*\|")
_RE_PREREQ_LINE = re.compile(r"^\*\*Prerequisites\*\*")
_RE_LEARNING_OBJ = re.compile(r"^\*\*Learning Objectives\*\*")
_RE_CONNECTIONS = re.compile(r"^\*\*Connections\*\*")


# 5. Oxford comma
_RE_OXFORD_AND = re.compile(r",\s+and\s+", re.IGNORECASE)
_RE_OXFORD_OR = re.compile(r",\s+or\s+", re.IGNORECASE)


# 6. Sentence-initial connectives
SENTENCE_INITIAL_CONNECTIVES: list[str] = [
    "Therefore", "Hence", "Thus", "Consequently",
    "Furthermore", "Moreover", "However",
    "Additionally", "Alternatively", "Conversely",
    "Accordingly", "Subsequently", "Correspondingly",
    "Similarly", "Likewise", "Notwithstanding",
]

_CONNECTIVE_PATTERNS: list[tuple[re.Pattern, str]] = []
for _c in SENTENCE_INITIAL_CONNECTIVES:
    # Match at the start of a sentence: after ". ", start of line, or after "? "
    # The word must be followed by a space or comma (not mid-word).
    _pat = re.compile(
        r"(?:^|(?<=\.\s)|(?<=\?\s)|(?<=!\s))" + re.escape(_c) + r"(?=[\s,])",
        re.MULTILINE,
    )
    _CONNECTIVE_PATTERNS.append((_pat, _c))


# 7. Em dashes
_RE_EM_DASH_SPACED = re.compile(r"\s+---?\s+")
_RE_EM_DASH_UNICODE = re.compile(r"\u2014")
# En dashes for compound names (Cauchy-Schwarz) are fine; only flag em dashes


# 8. Informal language
INFORMAL_WORDS: list[tuple[str, str]] = [
    ("basically", "omit"),
    ("just", "omit or rewrite"),
    ("simply", "omit or rewrite"),
    ("stuff", "items; material"),
    ("pretty much", "approximately; nearly"),
    ("a lot of", "many; much"),
    ("kind of", "somewhat; partially"),
    ("sort of", "somewhat; partially"),
]

_INFORMAL_COMPILED: list[tuple[re.Pattern, str, str]] = []
for _phrase, _repl in INFORMAL_WORDS:
    _pat = re.compile(r"\b" + re.escape(_phrase) + r"\b", re.IGNORECASE)
    _INFORMAL_COMPILED.append((_pat, _phrase, _repl))


# 9. Hagiographic reference annotations -- additional editorial superlatives
#    that commonly appear in reference descriptions
REFERENCE_SUPERLATIVES: list[str] = [
    "groundbreaking", "brilliant", "genius", "visionary",
    "pioneer", "pioneering", "revolutionary", "seminal",
    "landmark", "masterwork", "masterpiece",
    "definitive", "elegant", "exceptional", "outstanding",
    "classic", "monumental", "influential", "authoritative",
    "indispensable", "unrivalled", "unparalleled", "preeminent",
    "pre-eminent", "magisterial", "celebrated", "acclaimed",
    "renowned", "legendary", "towering", "profound",
    "comprehensive",
]

_REF_SUPERLATIVE_COMPILED: list[tuple[re.Pattern, str]] = []
for _w in REFERENCE_SUPERLATIVES:
    _pat = re.compile(r"\b" + re.escape(_w) + r"\b", re.IGNORECASE)
    _REF_SUPERLATIVE_COMPILED.append((_pat, _w))


# ── Checking logic ──────────────────────────────────

def is_reference_line(line: str) -> bool:
    """True if the line looks like a numbered reference entry."""
    return bool(re.match(r"^\s*(?:- )?\[\d+\]", line))


def check_chapter(filepath: Path) -> list[Issue]:
    """Run all tone checks on a single chapter file.

    Returns a list of (line_number, severity, category, message) tuples.
    """
    raw_text = filepath.read_text(encoding="utf-8")
    stripped_text = strip_markup(raw_text)
    lines = stripped_text.split("\n")

    # Identify reference section boundaries (on raw text)
    ref_start, ref_end = extract_references_section(raw_text)

    issues: list[Issue] = []

    for lineno_idx, line in enumerate(lines):
        lineno = lineno_idx + 1
        stripped_line = line.strip()

        # Skip empty lines, heading markers only, table separators
        if not stripped_line:
            continue
        if re.match(r"^-+$|^[|:\s-]+$|^\*{3,}$|^={3,}$", stripped_line):
            continue
        # Skip figure captions, blockquotes, table rows for most checks
        is_figure = bool(_RE_FIGURE_CAPTION.match(stripped_line))
        is_table = bool(_RE_TABLE_ROW.match(stripped_line))
        is_heading = bool(_RE_HEADING.match(line))
        is_prereq = bool(_RE_PREREQ_LINE.match(stripped_line))
        is_learning = bool(_RE_LEARNING_OBJ.match(stripped_line))
        is_connections = bool(_RE_CONNECTIONS.match(stripped_line))

        in_references = ref_start > 0 and ref_start <= lineno <= ref_end

        # ── 1. Forbidden words/phrases ─────────────────
        for pat, phrase, repl, sev in _FORBIDDEN_COMPILED:
            for m in pat.finditer(line):
                matched = m.group().lower()

                # Context-aware exemptions for mathematical terminology
                if matched in ("essential", "essentially"):
                    if (_ESSENTIAL_MATH_CONTEXT.search(line)
                            or _ESSENTIAL_TERM_NAME.search(line)
                            or _ESSENTIAL_NEARBY_MATH.search(line)):
                        continue

                if matched == "critical":
                    if _CRITICAL_MATH_CONTEXT.search(line):
                        continue

                if phrase == "with respect to":
                    if _WRT_MATH_CONTEXT.search(line):
                        continue

                if matched == "robust":
                    if _ROBUST_MATH_CONTEXT.search(line):
                        continue

                if matched == "vital":
                    if _VITAL_DOMAIN_CONTEXT.search(line):
                        continue

                issues.append((
                    lineno, sev, "Forbidden phrase",
                    f"'{m.group()}' -> {repl}",
                ))

        # "significant" -- context-dependent
        for m in _RE_SIGNIFICANT.finditer(line):
            # Check if the surrounding context is statistical
            window_start = max(0, m.start() - 80)
            window_end = min(len(line), m.end() + 80)
            context = line[window_start:window_end]
            if not _STAT_CONTEXT.search(context):
                issues.append((
                    lineno, "WARN", "Forbidden phrase",
                    f"'{m.group()}' outside statistics context -> large; important; material",
                ))

        # "landscape" -- only figurative
        for m in _RE_LANDSCAPE_FIG.finditer(line):
            if not _LITERAL_LANDSCAPE_CONTEXT.search(line):
                issues.append((
                    lineno, "FAIL", "Forbidden metaphor",
                    "'landscape' (figurative) -> field; area; domain",
                ))

        # "ecosystem" -- only figurative
        for m in _RE_ECOSYSTEM_FIG.finditer(line):
            if not _LITERAL_ECOSYSTEM_CONTEXT.search(line):
                issues.append((
                    lineno, "FAIL", "Forbidden metaphor",
                    "'ecosystem' (figurative) -> system; community",
                ))

        # ── 2. Hagiographic language ───────────────────
        for pat, _hagio_word, sev in _HAGIOGRAPHIC_COMPILED:
            for m in pat.finditer(line):
                matched_lower = m.group().lower()

                # "outstanding" -- exempt in financial context
                # (outstanding balance, debt, loan, shares, principal, amount)
                if matched_lower == "outstanding":
                    if re.search(
                        r"\boutstanding\s+(?:balance|debt|loan|share|principal"
                        r"|amount|obligation|bond|note|liability|payment|issue"
                        r"|stock|warrant|option|contract)",
                        line, re.IGNORECASE,
                    ) or re.search(
                        r"(?:balance|debt|loan|share|principal|amount)\s+outstanding",
                        line, re.IGNORECASE,
                    ):
                        continue

                # "classic" -- exempt in "classical" (mathematical usage)
                if matched_lower == "classic":
                    # Only flag bare "classic" not "classical"
                    if re.search(r"\bclassical\b", line, re.IGNORECASE):
                        continue

                # "landmark" -- exempt in geographical/geological context
                if matched_lower == "landmark":
                    if re.search(
                        r"(?:geolog|geograph|terrain|navigation|survey|GPS"
                        r"|triangulat|cartograph|map|coord)",
                        line, re.IGNORECASE,
                    ):
                        continue

                # "founding" / "foundational" -- exempt in factual usage
                # like "founding member", "founding date", "founding year"
                if matched_lower in ("founding", "foundational"):
                    if matched_lower == "founding" and re.search(
                        r"\bfounding\s+(?:of|member|date|year|in\s+\d)",
                        line, re.IGNORECASE,
                    ):
                        continue

                issues.append((
                    lineno, sev, "Hagiographic language",
                    f"'{m.group()}' -- state facts instead",
                ))

        # ── 3. Forbidden metaphors ─────────────────────
        for pat, _metaphor in _FORBIDDEN_METAPHOR_COMPILED:
            for m in pat.finditer(line):
                issues.append((
                    lineno, "FAIL", "Forbidden metaphor",
                    f"'{m.group()}'",
                ))

        if _RE_BRIDGE_FIG.search(line):
            issues.append((
                lineno, "FAIL", "Forbidden metaphor",
                "'bridge' (figurative between fields)",
            ))

        if _RE_POWER_FIG.search(line):
            issues.append((
                lineno, "FAIL", "Forbidden metaphor",
                "'power of [method]'",
            ))

        if _RE_BEAUTY.search(line):
            issues.append((
                lineno, "FAIL", "Forbidden metaphor",
                "'beauty/elegance of'",
            ))

        # "lens" -- only figurative uses
        for m in _RE_LENS_FIG.finditer(line):
            if not _LITERAL_LENS_CONTEXT.search(line):
                issues.append((
                    lineno, "FAIL", "Forbidden metaphor",
                    "'lens' (figurative) -> perspective; view; framework",
                ))

        # ── 4. First/second person ─────────────────────
        # Skip headings, figure captions, blockquotes, tables, learning objectives
        if not (is_figure or is_table or is_heading or is_prereq
                or is_learning or is_connections):
            for m in _RE_FIRST_PERSON.finditer(line):
                issues.append((
                    lineno, "FAIL", "First person",
                    f"'{m.group()}'",
                ))
            for m in _RE_SECOND_PERSON.finditer(line):
                issues.append((
                    lineno, "FAIL", "Second person",
                    f"'{m.group()}'",
                ))
            for m in _RE_I_PRONOUN.finditer(line):
                issues.append((
                    lineno, "FAIL", "First person",
                    f"'{m.group()}'",
                ))

        # ── 5. Oxford comma ────────────────────────────
        # Skip high-false-positive zones: references section (bibliographic
        # author lists use Oxford commas by convention), table rows (notation
        # tables), frontmatter lines (Prerequisites, Connections, Learning
        # Objectives), blockquotes, and admonition title lines.
        skip_oxford = (
            in_references
            or _RE_TABLE_ROW.match(stripped_line)
            or _RE_PREREQ_LINE.match(stripped_line)
            or _RE_LEARNING_OBJ.match(stripped_line)
            or _RE_CONNECTIONS.match(stripped_line)
            or stripped_line.startswith(">")
            or stripped_line.startswith("!!! ")
            or stripped_line.startswith("??? ")
        )
        if not skip_oxford:
            for m in _RE_OXFORD_AND.finditer(line):
                context_before = line[:m.start()]
                # Need 2+ prior commas for a genuine 3-item serial list.
                # With exactly 1 prior comma, ", and" is almost always a
                # two-clause join ("A is X, and B is Y") not an Oxford comma.
                if context_before.count(",") >= 2:
                    issues.append((
                        lineno, "WARN", "Oxford comma",
                        "', and ' -- omit the comma before 'and'",
                    ))
                elif context_before.count(",") == 1:
                    # Heuristic: if the segment before the first comma is
                    # short (under 6 words) it is more likely a list item
                    # than an independent clause. Flag only those.
                    first_seg = context_before.split(",")[0].strip()
                    if len(first_seg.split()) <= 5:
                        issues.append((
                            lineno, "WARN", "Oxford comma",
                            "', and ' -- possible Oxford comma (short list items)",
                        ))

            for m in _RE_OXFORD_OR.finditer(line):
                context_before = line[:m.start()]
                if context_before.count(",") >= 2:
                    issues.append((
                        lineno, "WARN", "Oxford comma",
                        "', or ' -- omit the comma before 'or'",
                    ))
                elif context_before.count(",") == 1:
                    first_seg = context_before.split(",")[0].strip()
                    if len(first_seg.split()) <= 5:
                        issues.append((
                            lineno, "WARN", "Oxford comma",
                            "', or ' -- possible Oxford comma (short list items)",
                        ))

        # ── 6. Sentence-initial connectives ────────────
        for pat, connective in _CONNECTIVE_PATTERNS:
            for m in pat.finditer(line):
                sev = "FAIL" if connective in (
                    "Furthermore", "Moreover", "However",
                    "Additionally", "Alternatively", "Conversely",
                ) else "WARN"
                issues.append((
                    lineno, sev, "Sentence-initial connective",
                    f"'{connective}' at sentence start -- place mid-sentence or restructure",
                ))

        # ── 7. Em dashes ──────────────────────────────
        # Skip references section (conference names like "CRYPTO '85"
        # use double hyphens that are not prose em dashes).
        if not in_references:
            if _RE_EM_DASH_SPACED.search(line):
                issues.append((
                    lineno, "FAIL", "Em dash",
                    "em dash found -- use semicolons or full stops",
                ))
            if _RE_EM_DASH_UNICODE.search(line):
                issues.append((
                    lineno, "FAIL", "Em dash",
                    "Unicode em dash (U+2014) found -- use semicolons or full stops",
                ))

        # ── 8. Informal language ───────────────────────
        for pat, phrase, repl in _INFORMAL_COMPILED:
            # "just" is extremely common in legitimate mathematical use
            # (e.g. "just one root", "just as in the previous case")
            # so we only flag it when followed by a verb-like pattern
            if phrase == "just":
                for m in pat.finditer(line):
                    after = line[m.end():m.end() + 20].strip().lower()
                    # Flag "just" when used informally: "just use", "just do",
                    # "just compute", "just apply", "just note", "just set"
                    if re.match(
                        r"(?:use|do|compute|apply|note|set|take|put|write|plug"
                        r"|add|run|check|look|try|ignore|think|remember|need"
                        r"|want|say|imagine|consider|pick|substitute|assume"
                        r"|define|observe|read|skip|drop|move|follow|call)",
                        after,
                    ):
                        issues.append((
                            lineno, "WARN", "Informal language",
                            f"'{m.group()}' -> {repl}",
                        ))
            elif phrase == "simply":
                for m in pat.finditer(line):
                    # Exclude "simply connected" (mathematical term)
                    after = line[m.end():m.end() + 15].strip().lower()
                    if not after.startswith("connected"):
                        issues.append((
                            lineno, "WARN", "Informal language",
                            f"'{m.group()}' -> {repl}",
                        ))
            else:
                for m in pat.finditer(line):
                    issues.append((
                        lineno, "WARN", "Informal language",
                        f"'{m.group()}' -> {repl}",
                    ))

        # ── 9. Hagiographic reference annotations ──────
        if in_references and is_reference_line(stripped_line):
            for pat, _word in _REF_SUPERLATIVE_COMPILED:
                for m in pat.finditer(line):
                    issues.append((
                        lineno, "FAIL", "Hagiographic reference",
                        f"'{m.group()}' in reference annotation -- state facts only",
                    ))

    return issues


# ── Reporting ───────────────────────────────────────

def severity_label(sev: str) -> str:
    """Return coloured severity label."""
    if sev == "FAIL":
        return FAIL
    if sev == "WARN":
        return WARN
    return INFO


def print_report(
    all_issues: dict[str, list[Issue]],
    files_checked: int,
    quick: bool,
) -> bool:
    """Print the full report. Returns True if any FAIL-level issues exist."""
    total_fail = 0
    total_warn = 0
    chapters_with_issues = 0

    # Category tallies for the summary
    category_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"FAIL": 0, "WARN": 0})

    print()
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print(f"{_BOLD}  TONE & DICTION VERIFICATION REPORT{_RESET}")
    if quick:
        print(f"  {_YELLOW}QUICK MODE{_RESET} -- first 3 chapters only")
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print()

    for filepath_str in sorted(all_issues.keys()):
        issues = all_issues[filepath_str]
        if not issues:
            continue

        chapters_with_issues += 1
        ch_fails = sum(1 for _, s, _, _ in issues if s == "FAIL")
        ch_warns = sum(1 for _, s, _, _ in issues if s == "WARN")
        total_fail += ch_fails
        total_warn += ch_warns

        stem = Path(filepath_str).stem
        status = FAIL if ch_fails > 0 else WARN
        print(f"  {status}  {_BOLD}{stem}{_RESET}  ({ch_fails} fail, {ch_warns} warn)")

        for lineno, sev, category, message in issues:
            label = severity_label(sev)
            print(f"         L{lineno:<5d} {label}  [{category}] {message}")
            category_counts[category][sev] += 1

        print()

    # Chapters with no issues
    clean_count = files_checked - chapters_with_issues
    if clean_count > 0:
        print(f"  {PASS}  {clean_count} chapter{'s' if clean_count != 1 else ''} clean")
        print()

    # ── Category summary ───────────────────────────
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print(f"{_BOLD}  CATEGORY SUMMARY{_RESET}")
    print(f"{'=' * 78}")
    print(f"  {'Category':<35s} {'FAIL':>6s} {'WARN':>6s} {'Total':>6s}")
    print(f"  {'-' * 55}")
    for cat in sorted(category_counts.keys()):
        f = category_counts[cat]["FAIL"]
        w = category_counts[cat]["WARN"]
        t = f + w
        print(f"  {cat:<35s} {f:>6d} {w:>6d} {t:>6d}")
    print(f"  {'-' * 55}")
    print(f"  {'TOTAL':<35s} {total_fail:>6d} {total_warn:>6d} {total_fail + total_warn:>6d}")

    # ── Final summary ──────────────────────────────
    print()
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print(f"{_BOLD}  SUMMARY{_RESET}")
    print(f"{'=' * 78}")
    print(f"  Chapters scanned:          {files_checked}")
    print(f"  Chapters with issues:      {chapters_with_issues}")
    print(f"  FAIL-level issues:         {total_fail}")
    print(f"  WARN-level issues:         {total_warn}")
    print(f"  Total issues:              {total_fail + total_warn}")
    print(f"{'=' * 78}")

    if total_fail > 0:
        print(f"\n  {FAIL}  {total_fail} tone violations must be fixed before merge.")
    elif total_warn > 0:
        print(f"\n  {WARN}  No failures, but {total_warn} warnings should be reviewed.")
    else:
        print(f"\n  {PASS}  All tone checks passed.")

    print()
    return total_fail > 0


# ── CLI ─────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify tone and diction across Evenwicht domain chapters.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Only check the first 3 chapter files (for CI).",
    )
    args = parser.parse_args()

    files = discover_files(quick=args.quick)
    if not files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}", file=sys.stderr)
        return 1

    mode = "QUICK MODE (3 files)" if args.quick else "full scan"
    print(f"Checking tone and diction ({mode}) ...")
    for f in files:
        print(f"  {f.relative_to(PROJECT_ROOT)}")

    all_issues: dict[str, list[Issue]] = {}
    for filepath in files:
        issues = check_chapter(filepath)
        all_issues[str(filepath)] = issues

    has_failures = print_report(all_issues, len(files), args.quick)

    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
