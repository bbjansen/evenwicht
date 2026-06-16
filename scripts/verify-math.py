#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Validate LaTeX math expressions in the Evenwicht textbook.

Extracts inline ($...$) and display ($$...$$) math blocks from all chapter
files and checks for:
  1. Balanced delimiters: braces, brackets, parentheses, \\left/\\right,
     \\begin/\\end pairs.
  2. Common errors: unmatched $ signs, missing \\end{X}, \\left without
     \\right, empty math, nested inline $, \\\\ at end of non-aligned
     display math.
  3. Undefined/unusual LaTeX commands not in the standard amsmath/amssymb/
     mathtools whitelist (~300 commands).

Interval notation like $[0, \\infty)$ is recognized and excluded from the
bracket/parenthesis balance check.

Usage:
    python3 scripts/verify-math.py

Exit code 0 if no issues found, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root: two levels up from this script
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

# ---------------------------------------------------------------------------
# Issue reporting
# ---------------------------------------------------------------------------


@dataclass
class Issue:
    """A single validation issue."""

    chapter: str
    line: int
    fragment: str
    message: str

    def __str__(self) -> str:
        short = self.fragment
        if len(short) > 80:
            short = short[:77] + "..."
        return f"  {self.chapter}:{self.line}: {self.message}\n    | {short}"


# ---------------------------------------------------------------------------
# LaTeX command whitelist (~300 standard commands)
# amsmath, amssymb, mathtools, core LaTeX math
# ---------------------------------------------------------------------------

WHITELIST: set[str] = {
    # --- Greek letters (lower) ---
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta",
    "eta", "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu",
    "xi", "pi", "varpi", "rho", "varrho", "sigma", "varsigma", "tau",
    "upsilon", "phi", "varphi", "chi", "psi", "omega",
    # --- Greek letters (upper) ---
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon",
    "Phi", "Psi", "Omega",
    # --- Binary operators ---
    "pm", "mp", "times", "div", "cdot", "ast", "star", "circ", "bullet",
    "oplus", "ominus", "otimes", "odot", "oslash", "cap", "cup",
    "sqcap", "sqcup", "vee", "wedge", "setminus", "wr",
    "diamond", "bigtriangleup", "bigtriangledown", "triangleleft",
    "triangleright", "dagger", "ddagger", "amalg",
    # --- Relations ---
    "leq", "le", "geq", "ge", "ll", "gg", "prec", "succ",
    "preceq", "succeq", "sim", "simeq", "asymp", "approx", "cong",
    "equiv", "neq", "ne", "propto", "perp", "mid", "nmid", "parallel",
    "bowtie", "vdash", "dashv", "in", "ni", "notin", "subset",
    "supset", "subseteq", "supseteq", "sqsubseteq", "sqsupseteq",
    "not", "lesssim", "gtrsim",
    # --- Arrows ---
    "leftarrow", "rightarrow", "Leftarrow", "Rightarrow",
    "leftrightarrow", "Leftrightarrow", "longleftarrow",
    "longrightarrow", "Longleftarrow", "Longrightarrow",
    "longleftrightarrow", "Longleftrightarrow",
    "mapsto", "to", "gets", "implies", "iff",
    "uparrow", "downarrow", "Uparrow", "Downarrow",
    "updownarrow", "Updownarrow", "nearrow", "searrow",
    "swarrow", "nwarrow", "leadsto",
    "xleftarrow", "xrightarrow", "rightleftharpoons",
    # --- Delimiters ---
    "lbrace", "rbrace", "langle", "rangle", "lfloor", "rfloor",
    "lceil", "rceil", "lvert", "rvert", "lVert", "rVert",
    "Vert", "vert",
    # --- Big delimiters / sizing ---
    "left", "right", "bigl", "bigr", "Bigl", "Bigr",
    "biggl", "biggr", "Biggl", "Biggr",
    "big", "Big", "bigg", "Bigg",
    # --- Punctuation / spacing ---
    "quad", "qquad", "ldots", "cdots", "vdots", "ddots",
    "colon", "dotsc", "dotsb", "dotsm", "dotsi", "dotso",
    # --- Accents / decorations ---
    "hat", "check", "tilde", "acute", "grave", "dot", "ddot",
    "breve", "bar", "vec", "widehat", "widetilde", "overline",
    "underline", "overbrace", "underbrace", "overset", "underset",
    "stackrel",
    # --- Functions (standard operator names) ---
    "sin", "cos", "tan", "sec", "csc", "cot",
    "arcsin", "arccos", "arctan",
    "sinh", "cosh", "tanh", "coth",
    "exp", "log", "ln", "lg",
    "lim", "limsup", "liminf",
    "sup", "inf", "max", "min",
    "arg", "deg", "det", "dim", "gcd", "hom", "ker",
    "Pr", "mod", "bmod", "pmod",
    "operatorname",
    # --- Sums / products / integrals ---
    "sum", "prod", "coprod", "int", "oint", "iint", "iiint",
    "bigcup", "bigcap", "bigoplus", "bigotimes", "bigsqcup",
    "bigvee", "bigwedge",
    # --- Fractions / binomials ---
    "frac", "dfrac", "tfrac", "cfrac", "binom", "dbinom", "tbinom",
    # --- Roots ---
    "sqrt",
    # --- Font commands ---
    "mathrm", "mathbf", "mathit", "mathsf", "mathtt", "mathcal",
    "mathbb", "mathfrak", "mathscr", "boldsymbol",
    "text", "texttt", "textbf", "textit", "textrm", "textsf",
    "rm", "bf", "it", "sf", "tt",
    # --- Miscellaneous symbols ---
    "infty", "nabla", "partial", "forall", "exists", "nexists",
    "emptyset", "varnothing", "neg", "lnot",
    "aleph", "hbar", "ell", "wp", "Re", "Im",
    "angle", "measuredangle", "sphericalangle",
    "triangle", "square", "blacksquare", "checkmark",
    "dag", "ddag", "flat", "natural", "sharp",
    "clubsuit", "diamondsuit", "heartsuit", "spadesuit",
    # --- Layout / environments ---
    "begin", "end",
    "displaystyle", "textstyle", "scriptstyle", "scriptscriptstyle",
    "substack", "cases",
    "tag", "notag", "label", "ref", "eqref",
    # --- Arrays / matrices ---
    "hline", "multicolumn",
    # --- Miscellaneous ---
    "phantom", "hphantom", "vphantom", "smash",
    "mathrlap", "mathllap", "mathclap",
    "boxed", "cancel", "bcancel", "xcancel",
    "color", "textcolor", "colorbox",
    "space", "enspace", "thinspace", "medspace", "thickspace",
    "negmedspace", "negthickspace",
    "mbox", "hbox",
    "smallmatrix",
    "mathrel", "mathbin", "mathop", "mathmakebox",
    # --- Additional symbols found in the textbook ---
    "nRe", "nimaginary", "ndC",  # custom operators via \operatorname in text
}

# Known environment names (for \begin{X} / \end{X} matching)
KNOWN_ENVIRONMENTS: set[str] = {
    "aligned", "align", "align*", "alignat", "alignat*",
    "cases", "dcases", "rcases",
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "smallmatrix",
    "array", "tabular",
    "equation", "equation*",
    "gather", "gather*",
    "multline", "multline*",
    "split", "subarray",
}

# Aligned-style environments where \\ is valid
ALIGNED_ENVIRONMENTS: set[str] = {
    "aligned", "align", "align*", "alignat", "alignat*",
    "cases", "dcases", "rcases",
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "smallmatrix",
    "array", "tabular",
    "gather", "gather*",
    "multline", "multline*",
    "split", "subarray",
}

# Interval notation patterns -- these produce intentionally mismatched
# brackets/parentheses and must be excluded from the balance check.
# Matches things like: [0, \infty), (0, 1], [-1, 1), etc.
_INTERVAL_RE = re.compile(
    r"[\[\(]"            # opening [ or (
    r"[^)\]]*?"          # content (non-greedy)
    r"[\]\)]"            # closing ] or )
)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def _strip_non_math_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """Return (original_line_number, text) pairs, blanking code blocks,
    mermaid blocks, and HTML comments so they don't interfere with
    math extraction."""
    result: list[tuple[int, str]] = []
    in_code_block = False
    in_html_comment = False

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line

        # Handle HTML comments (may span multiple lines)
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
            result.append((i, ""))
            continue

        if "<!--" in line:
            if "-->" in line and line.index("-->") > line.index("<!--"):
                # Single-line comment: blank just the comment portion
                cleaned = re.sub(r"<!--.*?-->", "", line)
                result.append((i, cleaned))
                continue
            else:
                in_html_comment = True
                result.append((i, ""))
                continue

        # Handle code blocks (``` ... ```)
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            result.append((i, ""))
            continue

        if in_code_block:
            result.append((i, ""))
            continue

        result.append((i, line))

    return result


@dataclass
class MathBlock:
    """A single math expression extracted from source."""

    content: str
    line_start: int
    line_end: int
    is_display: bool  # True for $$..$$, False for $...$
    raw_text: str  # The full original text including delimiters


def _extract_math_blocks(
    cleaned_lines: list[tuple[int, str]],
) -> list[MathBlock]:
    """Extract all inline and display math blocks from pre-cleaned lines.

    Display math ($$...$$) may span multiple lines.
    Inline math ($...$) must not span lines and must not contain \\$.
    """
    blocks: list[MathBlock] = []

    # Rebuild full text preserving line numbers
    full_text = ""
    line_map: list[int] = []  # char index -> line number
    for lineno, text in cleaned_lines:
        for _ in text:
            line_map.append(lineno)
        line_map.append(lineno)  # for the newline
        full_text += text + "\n"

    def _lineno_at(pos: int) -> int:
        if pos < len(line_map):
            return line_map[pos]
        return line_map[-1] if line_map else 1

    # Track which character ranges are already consumed by display math
    used_ranges: list[tuple[int, int]] = []

    # Display math: $$ ... $$ (may span lines)
    for m in re.finditer(r"\$\$(.*?)\$\$", full_text, re.DOTALL):
        start, end = m.start(), m.end()
        content = m.group(1)
        # Skip false pairs: when lazy matching pairs the closing $$ of
        # one block with the opening $$ of the next, the "content" is
        # only whitespace.  These are regex artifacts, not real blocks.
        if content.strip() == "":
            continue
        blocks.append(MathBlock(
            content=content,
            line_start=_lineno_at(start),
            line_end=_lineno_at(end - 1),
            is_display=True,
            raw_text=m.group(0),
        ))
        used_ranges.append((start, end))

    # Inline math: $...$ on a single line, not starting with $$
    # Process line by line to avoid cross-line matching
    for lineno, text in cleaned_lines:
        if not text.strip():
            continue

        # Neutralize escaped dollars (\$) before scanning
        neutralized = text.replace("\\$", "\x00\x00")

        # Find the start offset of this line in full_text
        # (We use a simple scan -- correct because cleaned_lines preserves
        # original line ordering and full_text was built from them.)
        pos = 0
        for m in re.finditer(r"(?<!\$)\$(?!\$)", neutralized):
            if pos > m.start():
                continue
            # Find closing $ on the same line
            close = neutralized.find("$", m.start() + 1)
            if close == -1:
                continue
            # Make sure the closing $ is not $$
            if close + 1 < len(neutralized) and neutralized[close + 1] == "$":
                continue
            if close > 0 and neutralized[close - 1] == "$":
                continue

            raw = text[m.start():close + 1]
            content = text[m.start() + 1:close]

            # Compute absolute position in full_text to check overlap
            # with display math ranges. We need to find where this line
            # sits in full_text.
            # Skip if the content is empty or whitespace-only (will be
            # caught by the empty-math check later)

            # Check if this inline block overlaps any display-math range
            # by searching for the raw text near the expected line
            overlap = False
            for rstart, rend in used_ranges:
                rline_start = _lineno_at(rstart)
                rline_end = _lineno_at(rend - 1)
                if rline_start <= lineno <= rline_end:
                    overlap = True
                    break
            if overlap:
                pos = close + 1
                continue

            blocks.append(MathBlock(
                content=content,
                line_start=lineno,
                line_end=lineno,
                is_display=False,
                raw_text=raw,
            ))
            pos = close + 1

    return blocks


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def _has_interval_notation(content: str) -> bool:
    """Detect whether content contains mathematical interval notation like
    [0, infty), (0, 1], [-1, 1), etc., which intentionally uses mismatched
    bracket/paren delimiters."""
    # Patterns for half-open/half-closed intervals:
    #   [a, b)  or  (a, b]
    # where a, b can be numbers, \infty, variables, expressions, etc.
    if re.search(r"\[[^\[\]()]*\)", content):
        return True
    if re.search(r"\([^\[\]()]*\]", content):
        return True
    return False


def check_balanced_braces(block: MathBlock) -> list[str]:
    """Check that {}, [], () are balanced.

    Skips bracket/paren checks for expressions containing interval notation,
    since [a, b) and (a, b] intentionally mismatch.
    """
    issues = []
    content = block.content

    has_intervals = _has_interval_notation(content)

    pairs = [("{", "}")]
    if not has_intervals:
        pairs.extend([("[", "]"), ("(", ")")])

    for open_ch, close_ch in pairs:
        depth = 0
        for ch in content:
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
            if depth < 0:
                issues.append(f"Unmatched closing '{close_ch}'")
                break
        if depth > 0:
            issues.append(
                f"Unmatched opening '{open_ch}' ({depth} unclosed)"
            )
    return issues


def check_left_right_pairs(block: MathBlock) -> list[str]:
    """Check \\left / \\right pairing."""
    issues = []
    lefts = len(re.findall(r"\\left(?![a-zA-Z])", block.content))
    rights = len(re.findall(r"\\right(?![a-zA-Z])", block.content))
    if lefts != rights:
        issues.append(
            f"\\left/\\right mismatch: {lefts} \\left vs {rights} \\right"
        )
    return issues


def check_begin_end_pairs(block: MathBlock) -> list[str]:
    """Check \\begin{{X}} / \\end{{X}} pairing."""
    issues = []
    begins = re.findall(r"\\begin\{([^}]+)\}", block.content)
    ends = re.findall(r"\\end\{([^}]+)\}", block.content)

    begin_counts: dict[str, int] = {}
    for env in begins:
        begin_counts[env] = begin_counts.get(env, 0) + 1

    end_counts: dict[str, int] = {}
    for env in ends:
        end_counts[env] = end_counts.get(env, 0) + 1

    all_envs = set(begin_counts) | set(end_counts)
    for env in sorted(all_envs):
        b = begin_counts.get(env, 0)
        e = end_counts.get(env, 0)
        if b != e:
            if b > e:
                issues.append(
                    f"\\begin{{{env}}} without matching \\end{{{env}}} "
                    f"({b} begins, {e} ends)"
                )
            else:
                issues.append(
                    f"\\end{{{env}}} without matching \\begin{{{env}}} "
                    f"({e} ends, {b} begins)"
                )
    return issues


def check_empty_math(block: MathBlock) -> list[str]:
    """Check for empty math blocks: $$$$ or $ $."""
    issues = []
    stripped = block.content.strip()
    if stripped == "" or stripped.isspace():
        kind = "display" if block.is_display else "inline"
        issues.append(f"Empty {kind} math block")
    return issues


def check_nested_inline_dollar(block: MathBlock) -> list[str]:
    """Check for nested $ inside inline math (common mistake).

    Escaped \\$ (literal dollar sign in LaTeX) is excluded.
    """
    if block.is_display:
        return []
    issues = []
    # Remove escaped \$ before checking
    cleaned = block.content.replace("\\$", "")
    if "$" in cleaned:
        issues.append("Nested $ sign inside inline math")
    return issues


def check_backslash_backslash_in_non_aligned(block: MathBlock) -> list[str]:
    """Check for \\\\ at end of display math that is not in an aligned env."""
    if not block.is_display:
        return []
    issues = []
    content = block.content

    # If the block contains any aligned-style environment, skip this check
    envs_in_block = re.findall(r"\\begin\{([^}]+)\}", content)
    if any(env in ALIGNED_ENVIRONMENTS for env in envs_in_block):
        return []

    # Check if the display block ends with \\ (possibly followed by whitespace)
    if re.search(r"\\\\[ \t]*$", content.rstrip()):
        issues.append(
            "\\\\\\\\ at end of non-aligned display math (likely error)"
        )
    return issues


def check_undefined_commands(block: MathBlock) -> list[str]:
    """Flag LaTeX commands not in the whitelist.

    Skips \\$ (escaped dollar sign) which is not a command name.
    """
    issues = []
    # Find all \commandname sequences (letters only, not \$ or \, etc.)
    commands = re.findall(r"\\([a-zA-Z]+)", block.content)
    seen: set[str] = set()
    for cmd in commands:
        if cmd not in WHITELIST and cmd not in seen:
            seen.add(cmd)
            issues.append(f"Unknown command \\{cmd}")
    return issues


def check_unmatched_dollars(
    cleaned_lines: list[tuple[int, str]],
) -> list[Issue]:
    """Check for lines with an odd number of $ signs (outside code blocks).

    Handles escaped \\$ (literal dollar sign) by removing them first.
    Tracks display-math state across lines for multi-line $$ blocks.
    """
    issues: list[Issue] = []

    in_display = False
    for lineno, line in cleaned_lines:
        if not line.strip():
            continue

        # Remove escaped \$ before counting
        clean = line.replace("\\$", "")

        # Toggle display-math state on $$
        dd_count = clean.count("$$")
        if dd_count % 2 == 1:
            in_display = not in_display

        if in_display:
            continue

        # After removing $$, count remaining single $
        remaining = clean.replace("$$", "")
        dollar_count = remaining.count("$")
        if dollar_count % 2 == 1:
            issues.append(Issue(
                chapter="",
                line=lineno,
                fragment=line.rstrip(),
                message="Odd number of $ signs on this line (unmatched inline math)",
            ))

    return issues


# ---------------------------------------------------------------------------
# Main validation pipeline
# ---------------------------------------------------------------------------


def validate_file(filepath: Path) -> tuple[int, list[Issue]]:
    """Validate all math in a single markdown file.

    Returns (block_count, issues).
    """
    issues: list[Issue] = []
    chapter_name = filepath.name

    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Step 1: Clean non-math blocks
    cleaned = _strip_non_math_blocks(lines)

    # Step 2: Line-level dollar-sign check
    dollar_issues = check_unmatched_dollars(cleaned)
    for iss in dollar_issues:
        iss.chapter = chapter_name
        issues.append(iss)

    # Step 3: Extract math blocks
    blocks = _extract_math_blocks(cleaned)

    # Step 4: Run checks on each block
    checks = [
        check_balanced_braces,
        check_left_right_pairs,
        check_begin_end_pairs,
        check_empty_math,
        check_nested_inline_dollar,
        check_backslash_backslash_in_non_aligned,
        check_undefined_commands,
    ]

    for block in blocks:
        for check_fn in checks:
            msgs = check_fn(block)
            for msg in msgs:
                issues.append(Issue(
                    chapter=chapter_name,
                    line=block.line_start,
                    fragment=block.raw_text.strip().replace("\n", " "),
                    message=msg,
                ))

    return len(blocks), issues


def discover_files() -> list[Path]:
    """Find all chapter markdown files."""
    pattern = re.compile(r"^[0-9].*\.md$")
    files = sorted(
        f for f in DOCS_DIR.iterdir()
        if f.is_file() and pattern.match(f.name)
    )
    return files


def main() -> int:
    if not DOCS_DIR.is_dir():
        print(f"ERROR: docs directory not found: {DOCS_DIR}", file=sys.stderr)
        return 1

    files = discover_files()
    if not files:
        print(f"WARNING: No chapter files found in {DOCS_DIR}", file=sys.stderr)
        return 0

    all_issues: list[Issue] = []
    file_count = 0
    block_count = 0

    for filepath in files:
        file_count += 1
        n_blocks, file_issues = validate_file(filepath)
        block_count += n_blocks
        all_issues.extend(file_issues)

    # --- Report ---
    print(f"Scanned {file_count} files, {block_count} math blocks\n")

    if not all_issues:
        print("No issues found.")
        return 0

    # Group by chapter
    by_chapter: dict[str, list[Issue]] = {}
    for iss in all_issues:
        by_chapter.setdefault(iss.chapter, []).append(iss)

    total = len(all_issues)
    for chapter in sorted(by_chapter):
        chapter_issues = by_chapter[chapter]
        print(f"--- {chapter} ({len(chapter_issues)} issue(s)) ---")
        for iss in sorted(chapter_issues, key=lambda i: i.line):
            print(iss)
        print()

    print(f"Total: {total} issue(s) in {len(by_chapter)} file(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
