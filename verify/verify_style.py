# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Style and notation compliance verification for all Evenwicht chapter and
solutions files.

Checks enforced:
  1.  No \\blacksquare anywhere (must be \\square)
  2.  No $\\square$ or \\square inside a $$....$$ display block
  3.  No \\text{Var}, \\text{Cov}, \\text{Bias} (must be \\operatorname{...})
  4.  No bare E[ in math contexts (must be \\mathbb{E}[)
  5.  Every timeline mermaid block has the correct %%{init}%% theme
  6.  Every mindmap mermaid block has the correct %%{init}%% theme
  7.  No %%{init}%% on xychart-beta blocks
  8.  Every exercise in each solutions file is wrapped in ??? success "Solution"
  9.  No draft fragments (leftover reasoning text)
  10. No bare *Proof.* outside a ??? note "Proof" admonition

Usage:
    python3 verify/verify_style.py

Also exposes ``build() -> Chapter`` for integration with run_all.py.
"""

from __future__ import annotations

import glob
import os
import re
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework import Chapter, StructuralCheck

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAINS_DIR = os.path.join(BASE_DIR, "docs", "domains")
SOLUTIONS_DIR = os.path.join(BASE_DIR, "docs", "solutions")

# ---------------------------------------------------------------------------
# Expected %%{init}%% themes (must match exactly what's in the style guide)
# ---------------------------------------------------------------------------

TIMELINE_INIT_REQUIRED_KEYS = {
    "cScale0": "#d1ecf1",
    "cScale1": "#c8e6c9",
    "cScale2": "#fff3cd",
    "cScale3": "#f8d7da",
    "cScale4": "#e8daef",
    "cScale5": "#d1f2eb",
    "cScale6": "#e8e8e8",
    "cScale7": "#d1ecf1",
    "cScale8": "#c8e6c9",
    "cScale9": "#fff3cd",
    "cScaleLabel0": "#333333",
    "cScaleLabel1": "#333333",
    "cScaleLabel2": "#333333",
    "cScaleLabel3": "#333333",
    "cScaleLabel4": "#333333",
    "cScaleLabel5": "#333333",
    "cScaleLabel6": "#333333",
    "cScaleLabel7": "#333333",
    "cScaleLabel8": "#333333",
    "cScaleLabel9": "#333333",
}

MINDMAP_INIT_REQUIRED_KEYS = {
    "cScale0": "#d1ecf1",
    "cScale1": "#c8e6c9",
    "cScale2": "#fff3cd",
    "cScale3": "#e8daef",
    "cScale4": "#d1f2eb",
    "cScale5": "#f8d7da",
}


# Draft fragment patterns — leftover authoring text
# Patterns are anchored to avoid matching legitimate prose
DRAFT_PATTERNS = [
    r"Wait,\s+let me reconsider",
    r"(?<!\w)(?<!Error )Correction:\s+",  # "Correction:" not preceded by "Error" (excludes "Error Correction:")
    r"^Hmm,\s+",
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\[stub\]",
    r"\[to be completed\]",
    r"\[incomplete\]",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _chapter_num(path: str) -> int:
    m = re.match(r"(\d+)-", os.path.basename(path))
    return int(m.group(1)) if m else 0


def _extract_mermaid_blocks(text: str) -> list[tuple[str, str]]:
    """Return list of (first_diagram_type, full_block_text) for every mermaid block."""
    blocks = []
    for raw in re.findall(r"```mermaid\n([\s\S]*?)```", text):
        # Find first non-init, non-blank, non-frontmatter line
        diag_type = ""
        in_fm = False
        for line in raw.split("\n"):
            s = line.strip()
            if s == "---":
                in_fm = not in_fm
                continue
            if in_fm or s.startswith("%%{") or not s:
                continue
            diag_type = s.split()[0] if s.split() else ""
            break
        blocks.append((diag_type, raw))
    return blocks


def _init_theme_vars(block_text: str) -> dict:
    """Extract themeVariables dict from a %%{init}%% directive, or {} if absent."""
    m = re.search(r"%%\{init:\s*(\{.*?\})\s*\}%%", block_text, re.DOTALL)
    if not m:
        return {}
    import json
    try:
        obj = json.loads(m.group(1))
        return obj.get("themeVariables", {})
    except Exception:
        return {}


def _has_init(block_text: str) -> bool:
    return bool(re.search(r"%%\{init:", block_text))


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    file: str
    line: int
    message: str


def check_blacksquare(files: list[str]) -> list[Violation]:
    """Rule 1: no \\blacksquare anywhere."""
    violations = []
    for fp in files:
        text = _read(fp)
        for i, line in enumerate(text.split("\n"), 1):
            if r"\blacksquare" in line:
                violations.append(Violation(fp, i, r"\blacksquare found (use \square)"))
    return violations


def check_square_in_display(files: list[str]) -> list[Violation]:
    """Rule 2: \\square must not appear inside a $$...$$ display block."""
    violations = []
    # Match $$ ... $$ blocks (multi-line)
    for fp in files:
        text = _read(fp)
        # Find display math blocks: either standalone $$ delimiters or inline $$...$$
        # Strategy: find all $$ ... $$ spans
        for m in re.finditer(r"\$\$([\s\S]*?)\$\$", text):
            inner = m.group(1)
            if r"\square" in inner:
                line_num = text[:m.start()].count("\n") + 1
                violations.append(Violation(
                    fp, line_num,
                    r"$\square$ inside $$....$$ block — move to standalone line after block"
                ))
    return violations


def check_text_operators(files: list[str]) -> list[Violation]:
    """Rule 3: \\text{Var}, \\text{Cov}, \\text{Bias} must be \\operatorname{...}."""
    violations = []
    pattern = re.compile(r"\\text\{(Var|Cov|Bias|diag|proj|sinc|WN|rank|span|dim|tr|det)\}")
    for fp in files:
        text = _read(fp)
        for i, line in enumerate(text.split("\n"), 1):
            for m in pattern.finditer(line):
                violations.append(Violation(
                    fp, i,
                    rf"\text{{{m.group(1)}}} found (use \operatorname{{{m.group(1)}}})"
                ))
    return violations


def check_bare_expectation(files: list[str]) -> list[Violation]:
    """Rule 4: bare E[ in math contexts must be \\mathbb{E}[.

    Ignores:
    - Lines inside fenced code or mermaid blocks
    - E[ immediately followed by a double-quote (Mermaid node IDs)
    - Array/algorithm index patterns: E[i, E[j
    - Text like 'Example', 'Exercise', 'Expected', 'Entropy'
    """
    violations = []
    # Pattern: E[ not preceded by \, {, or a letter (to avoid \mathbb{E[, operatorname{E[, etc.)
    # and not followed by " (Mermaid) or i,j,k digits (array index)
    pattern = re.compile(r"(?<![\\{a-zA-Z])E\[(?![\"0-9ijk,\s])")
    for fp in files:
        text = _read(fp)
        in_fence = False
        for i, line in enumerate(text.split("\n"), 1):
            s = line.strip()
            if s.startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            # Skip Mermaid arrows and node definitions
            if "-->" in line or s.startswith("%%"):
                continue
            for m in pattern.finditer(line):
                # Double-check: not already \mathbb{E}[
                context = line[max(0, m.start()-10):m.start()]
                if "mathbb" in context or "operatorname" in context:
                    continue
                violations.append(Violation(
                    fp, i,
                    f"Bare E[ found (use \\mathbb{{E}}[): ...{line[max(0,m.start()-8):m.start()+8].strip()}..."
                ))
    return violations


def check_timeline_init(domain_files: list[str]) -> list[Violation]:
    """Rule 5: every timeline block must have the correct %%{init}%% theme."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type != "timeline":
                continue
            if not _has_init(block):
                violations.append(Violation(fp, 0, f"Ch{ch:02d} timeline missing %%{{init}}%% theme block"))
                continue
            tv = _init_theme_vars(block)
            for key, expected in TIMELINE_INIT_REQUIRED_KEYS.items():
                actual = tv.get(key, "")
                if actual.lower() != expected.lower():
                    violations.append(Violation(
                        fp, 0,
                        f"Ch{ch:02d} timeline %%{{init}}%% themeVariables.{key}: "
                        f"expected '{expected}', got '{actual or '(missing)'}'"
                    ))
    return violations


def check_mindmap_init(domain_files: list[str]) -> list[Violation]:
    """Rule 6: every mindmap block must have the correct %%{init}%% theme."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type != "mindmap":
                continue
            if not _has_init(block):
                violations.append(Violation(fp, 0, f"Ch{ch:02d} mindmap missing %%{{init}}%% theme block"))
                continue
            tv = _init_theme_vars(block)
            for key, expected in MINDMAP_INIT_REQUIRED_KEYS.items():
                actual = tv.get(key, "")
                if actual.lower() != expected.lower():
                    violations.append(Violation(
                        fp, 0,
                        f"Ch{ch:02d} mindmap %%{{init}}%% themeVariables.{key}: "
                        f"expected '{expected}', got '{actual or '(missing)'}'"
                    ))
    return violations


def check_xychart_no_init(domain_files: list[str]) -> list[Violation]:
    """Rule 7: xychart-beta blocks must NOT have %%{init}%%."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type != "xychart-beta":
                continue
            if _has_init(block):
                violations.append(Violation(
                    fp, 0,
                    f"Ch{ch:02d} xychart-beta has %%{{init}}%% (remove it; use YAML title front-matter instead)"
                ))
    return violations





def check_flowchart_init(domain_files: list[str]) -> list[Violation]:
    """Rule 11: every flowchart/graph block must have %%{init}%% theme."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type not in ("flowchart", "graph"):
                continue
            if not _has_init(block):
                violations.append(Violation(fp, 0, f"Ch{ch:02d} {diag_type} missing %%{{init}}%% theme block"))
    return violations


def check_statediagram_init(domain_files: list[str]) -> list[Violation]:
    """Rule 12: every stateDiagram block must have %%{init}%% theme."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type not in ("stateDiagram-v2", "stateDiagram"):
                continue
            if not _has_init(block):
                violations.append(Violation(fp, 0, f"Ch{ch:02d} stateDiagram missing %%{{init}}%% theme block"))
    return violations


def check_quadrant_init(domain_files: list[str]) -> list[Violation]:
    """Rule 13: every quadrantChart block must have %%{init}%% theme."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type != "quadrantChart":
                continue
            if not _has_init(block):
                violations.append(Violation(fp, 0, f"Ch{ch:02d} quadrantChart missing %%{{init}}%% theme block"))
    return violations


def check_xychart_palette(domain_files: list[str]) -> list[Violation]:
    """Rule 14: every xychart-beta block must have plotColorPalette in YAML config."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type != "xychart-beta":
                continue
            if "plotColorPalette" not in block:
                violations.append(Violation(
                    fp, 0,
                    f"Ch{ch:02d} xychart-beta missing plotColorPalette in YAML config"
                ))
    return violations


def check_pie_init(domain_files: list[str]) -> list[Violation]:
    """Rule 15: every pie block must have %%{init}%% with pie colour theme."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type != "pie":
                continue
            if not _has_init(block):
                violations.append(Violation(fp, 0, f"Ch{ch:02d} pie chart missing %%{{init}}%% theme block"))
    return violations


def check_no_yaml_frontmatter(domain_files: list[str]) -> list[Violation]:
    """Rule 16: no YAML frontmatter in mermaid blocks (except xychart-beta which uses it for config)."""
    violations = []
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type == "xychart-beta":
                continue
            if re.search(r"^---\s*\n.*?\n---\s*\n", block, re.DOTALL):
                violations.append(Violation(
                    fp, 0,
                    f"Ch{ch:02d} {diag_type} has YAML frontmatter (remove it; use %%{{init}}%% for theming)"
                ))
    return violations


def check_flowchart_style_lines(domain_files: list[str]) -> list[Violation]:
    """Rule 17: every flowchart node must have an inline style line."""
    violations = []
    # Node IDs are defined at the start of a line (after indentation) followed
    # by a shape bracket: ID["label"], ID{"label"}, ID("label").
    # We extract IDs from style lines and compare.
    skip_ids = {"flowchart", "graph", "subgraph", "end", "style", "class", "click",
                "classDef", "direction", "LR", "TD", "TB", "RL", "BT"}
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        for diag_type, block in _extract_mermaid_blocks(text):
            if diag_type not in ("flowchart", "graph"):
                continue
            # Collect all node IDs that have style lines
            styled_ids = set(re.findall(r"style\s+(\w+)\s+fill:", block))
            # Collect all node IDs defined in the block — only at line start
            node_ids: set[str] = set()
            for line in block.split("\n"):
                s = line.strip()
                if not s or s.startswith("style ") or s.startswith("%%{") or s.startswith("class "):
                    continue
                # Match: "    ID[" or "    ID{" or "    ID(" at line start
                m = re.match(r"^\s+([A-Za-z][A-Za-z0-9_]+)\s*[\[({]", line)
                if m and m.group(1) not in skip_ids:
                    node_ids.add(m.group(1))
                # Match: "--> ID[" (target node definition)
                for m in re.finditer(r"--[->|.]+\s+([A-Za-z][A-Za-z0-9_]+)\s*[\[({]", s):
                    if m.group(1) not in skip_ids:
                        node_ids.add(m.group(1))
            missing = node_ids - styled_ids
            if missing:
                sample = ", ".join(sorted(missing)[:5])
                violations.append(Violation(
                    fp, 0,
                    f"Ch{ch:02d} flowchart missing style lines for: {sample}"
                ))
    return violations


def check_solution_wrapping(solution_files: list[str]) -> list[Violation]:
    """Rule 8: every exercise in each solutions file must have a ??? success "Solution" block."""
    violations = []
    for fp in solution_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        # Count exercise statements
        exercise_count = len(re.findall(r"^\*\*Exercise\s+\d+\.\d+", text, re.MULTILINE))
        # Count solution admonitions
        solution_count = len(re.findall(r'^\?\?\?\s+success\s+"Solution"', text, re.MULTILINE))
        if exercise_count == 0:
            continue  # no exercises to check
        if solution_count != exercise_count:
            violations.append(Violation(
                fp, 0,
                f"Ch{ch:02d} solutions: {exercise_count} exercises but {solution_count} "
                f"??? success \"Solution\" blocks (expected {exercise_count})"
            ))
    return violations


def check_draft_fragments(files: list[str]) -> list[Violation]:
    """Rule 9: no draft/authoring fragments left in the files."""
    violations = []
    combined = re.compile("|".join(DRAFT_PATTERNS))
    for fp in files:
        text = _read(fp)
        for i, line in enumerate(text.split("\n"), 1):
            if combined.search(line):
                violations.append(Violation(
                    fp, i,
                    f"Draft fragment: {line.strip()[:80]}"
                ))
    return violations


def check_bare_proof_markers(domain_files: list[str]) -> list[Violation]:
    """Rule 10: *Proof.* must only appear inside ??? note \"Proof\" admonitions (indented 4+ spaces)."""
    violations = []
    proof_re = re.compile(r"^\*Proof[\.:]\*|^_Proof[\.:]_")
    for fp in domain_files:
        text = _read(fp)
        ch = _chapter_num(fp)
        in_fence = False
        for i, line in enumerate(text.split("\n"), 1):
            s = line.strip()
            if s.startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            if proof_re.match(s):
                # It's OK if the line is indented >=4 spaces (inside an admonition)
                indent = len(line) - len(line.lstrip())
                if indent < 4:
                    violations.append(Violation(
                        fp, i,
                        f"Ch{ch:02d} bare *Proof.* at line {i} not inside ??? note \"Proof\" admonition"
                    ))
    return violations


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------


@dataclass
class StyleReport:
    blacksquare: list[Violation] = field(default_factory=list)
    square_in_display: list[Violation] = field(default_factory=list)
    text_operators: list[Violation] = field(default_factory=list)
    bare_expectation: list[Violation] = field(default_factory=list)
    timeline_init: list[Violation] = field(default_factory=list)
    mindmap_init: list[Violation] = field(default_factory=list)
    xychart_no_init: list[Violation] = field(default_factory=list)
    flowchart_init: list[Violation] = field(default_factory=list)
    statediagram_init: list[Violation] = field(default_factory=list)
    quadrant_init: list[Violation] = field(default_factory=list)
    xychart_palette: list[Violation] = field(default_factory=list)
    pie_init: list[Violation] = field(default_factory=list)
    yaml_frontmatter: list[Violation] = field(default_factory=list)
    flowchart_styles: list[Violation] = field(default_factory=list)
    solution_wrapping: list[Violation] = field(default_factory=list)
    draft_fragments: list[Violation] = field(default_factory=list)
    bare_proof_markers: list[Violation] = field(default_factory=list)


def run_all_checks() -> StyleReport:
    domain_files = sorted(glob.glob(os.path.join(DOMAINS_DIR, "*.md")))
    solution_files = sorted(glob.glob(os.path.join(SOLUTIONS_DIR, "*.md")))
    all_files = domain_files + solution_files

    report = StyleReport()
    report.blacksquare = check_blacksquare(all_files)
    report.square_in_display = check_square_in_display(all_files)
    report.text_operators = check_text_operators(all_files)
    report.bare_expectation = check_bare_expectation(all_files)
    report.timeline_init = check_timeline_init(domain_files)
    report.mindmap_init = check_mindmap_init(domain_files)
    report.xychart_no_init = check_xychart_no_init(domain_files)
    report.flowchart_init = check_flowchart_init(domain_files)
    report.statediagram_init = check_statediagram_init(domain_files)
    report.quadrant_init = check_quadrant_init(domain_files)
    report.xychart_palette = check_xychart_palette(domain_files)
    report.pie_init = check_pie_init(domain_files)
    report.yaml_frontmatter = check_no_yaml_frontmatter(domain_files)
    report.flowchart_styles = check_flowchart_style_lines(domain_files)
    report.solution_wrapping = check_solution_wrapping(solution_files)
    report.draft_fragments = check_draft_fragments(all_files)
    report.bare_proof_markers = check_bare_proof_markers(domain_files)
    return report


# ---------------------------------------------------------------------------
# Framework integration
# ---------------------------------------------------------------------------


def _make_check(label: str, violations: list[Violation]) -> StructuralCheck:
    def predicate(_v: list[Violation] = violations) -> tuple[bool, str]:
        if not _v:
            return True, ""
        sample = "; ".join(
            f"{os.path.basename(v.file)}:{v.line}: {v.message}"
            for v in _v[:5]
        )
        suffix = f" (+{len(_v)-5} more)" if len(_v) > 5 else ""
        return False, f"{len(_v)} violation(s): {sample}{suffix}"
    return StructuralCheck(label=label, section="style", predicate=predicate)


def build() -> Chapter:
    """Build a Chapter of style/notation compliance checks."""
    ch = Chapter(202, "Style & Notation Compliance")
    report = run_all_checks()

    ch.add(_make_check(
        r"No \blacksquare (use \square)",
        report.blacksquare,
    ))
    ch.add(_make_check(
        r"$\square$ not inside $$...$$ display blocks",
        report.square_in_display,
    ))
    ch.add(_make_check(
        r"No \text{Var/Cov/Bias/...} (use \operatorname{...})",
        report.text_operators,
    ))
    ch.add(_make_check(
        r"No bare E[ in math contexts (use \mathbb{E}[)",
        report.bare_expectation,
    ))
    ch.add(_make_check(
        "Every timeline block has correct %%{init}%% cScale theme",
        report.timeline_init,
    ))
    ch.add(_make_check(
        "Every mindmap block has correct %%{init}%% neutral theme",
        report.mindmap_init,
    ))
    ch.add(_make_check(
        "No %%{init}%% on xychart-beta blocks",
        report.xychart_no_init,
    ))
    ch.add(_make_check(
        "Every flowchart/graph block has %%{init}%% theme",
        report.flowchart_init,
    ))
    ch.add(_make_check(
        "Every stateDiagram block has %%{init}%% theme",
        report.statediagram_init,
    ))
    ch.add(_make_check(
        "Every quadrantChart block has %%{init}%% theme",
        report.quadrant_init,
    ))
    ch.add(_make_check(
        "Every xychart-beta block has plotColorPalette config",
        report.xychart_palette,
    ))
    ch.add(_make_check(
        "Every pie chart block has %%{init}%% colour theme",
        report.pie_init,
    ))
    ch.add(_make_check(
        "No YAML frontmatter in non-xychart mermaid blocks",
        report.yaml_frontmatter,
    ))
    ch.add(_make_check(
        "Every flowchart node has inline style line",
        report.flowchart_styles,
    ))
    ch.add(_make_check(
        "Every exercise in solutions files wrapped in ??? success \"Solution\"",
        report.solution_wrapping,
    ))
    ch.add(_make_check(
        "No draft/authoring fragments in files",
        report.draft_fragments,
    ))
    ch.add(_make_check(
        'No bare *Proof.* outside ??? note "Proof" admonitions',
        report.bare_proof_markers,
    ))
    return ch


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from framework import Report

    chapter = build()
    chapter.run()

    report = Report()
    report.add_chapter(chapter)
    report.print_console()

    raise SystemExit(report.exit_code)
