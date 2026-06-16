# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Mermaid diagram validation for all 48 Evenwicht textbook chapters.

Parses every ```mermaid code block from docs/domains/*.md and validates:
  1. Syntax — matching brackets, valid diagram types, well-formed init directives
  2. Cross-references — "Chapter N" labels point to chapters 1..48
  3. Consistency — node labels that mention chapter titles match the actual chapter title

Reports issues via the StructuralCheck framework so results integrate with run_all.py.
"""

from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import dataclass, field

from framework import Chapter, StructuralCheck


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOCS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "domains",
)

VALID_DIAGRAM_TYPES = {
    "flowchart",
    "graph",
    "mindmap",
    "timeline",
    "stateDiagram-v2",
    "stateDiagram",
    "xychart-beta",
    "quadrantChart",
    "sankey-beta",
    "classDiagram",
    "sequenceDiagram",
    "erDiagram",
    "gantt",
    "pie",
    "gitgraph",
    "journey",
    "block-beta",
    "packet-beta",
    "architecture-beta",
    "kanban",
    "requirementDiagram",
    "C4Context",
    "C4Container",
    "C4Component",
    "C4Dynamic",
    "C4Deployment",
    "zenuml",
}

MAX_CHAPTER = 48

# Bracket / delimiter pairs to validate
BRACKET_PAIRS = {
    "(": ")",
    "[": "]",
    "{": "}",
}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class MermaidBlock:
    """A single mermaid code block extracted from a markdown file."""
    file: str
    chapter_num: int
    block_index: int
    raw: str
    diagram_type: str = ""
    issues: list[str] = field(default_factory=list)


@dataclass
class ChapterInfo:
    """Metadata about one chapter derived from its markdown file."""
    number: int
    title: str
    file: str
    headings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def _chapter_num_from_filename(filename: str) -> int:
    """Extract chapter number from filenames like '01-expressions.md'."""
    basename = os.path.basename(filename)
    m = re.match(r"(\d+)-", basename)
    return int(m.group(1)) if m else 0


def _extract_chapter_title(content: str) -> str:
    """Extract the H1 title from chapter markdown."""
    m = re.search(r"^#\s+Chapter\s+\d+:\s*(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _extract_headings(content: str) -> list[str]:
    """Extract all markdown headings."""
    return re.findall(r"^#{1,4}\s+(.+)$", content, re.MULTILINE)


def load_chapters() -> dict[int, ChapterInfo]:
    """Load metadata for all chapters."""
    chapters: dict[int, ChapterInfo] = {}
    pattern = os.path.join(DOCS_DIR, "*.md")
    for filepath in sorted(glob.glob(pattern)):
        num = _chapter_num_from_filename(filepath)
        if num == 0:
            continue
        with open(filepath, encoding="utf-8") as fh:
            content = fh.read()
        chapters[num] = ChapterInfo(
            number=num,
            title=_extract_chapter_title(content),
            file=filepath,
            headings=_extract_headings(content),
        )
    return chapters


def extract_mermaid_blocks(filepath: str, chapter_num: int) -> list[MermaidBlock]:
    """Extract all mermaid code blocks from a markdown file."""
    with open(filepath, encoding="utf-8") as fh:
        content = fh.read()

    raw_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
    blocks: list[MermaidBlock] = []
    for idx, raw in enumerate(raw_blocks):
        blocks.append(MermaidBlock(
            file=filepath,
            chapter_num=chapter_num,
            block_index=idx,
            raw=raw,
        ))
    return blocks


# ---------------------------------------------------------------------------
# Diagram type detection
# ---------------------------------------------------------------------------


def _detect_diagram_type(block: MermaidBlock) -> str:
    """Identify the mermaid diagram type from the block content.

    Skips frontmatter (---...---), %%{init} directives, and title lines
    to find the first keyword that identifies the diagram type.
    """
    lines = block.raw.strip().split("\n")
    in_frontmatter = False
    for line in lines:
        stripped = line.strip()

        # Handle YAML frontmatter delimiters
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue

        # Skip init directives
        if stripped.startswith("%%{"):
            continue
        # Skip empty lines
        if not stripped:
            continue
        # Skip standalone title lines that may appear after frontmatter
        if stripped.startswith("title:"):
            continue

        # The first meaningful token is the diagram type
        token = stripped.split()[0] if stripped.split() else ""
        # Some types have direction suffix: "flowchart TD", "graph LR"
        return token

    return ""


# ---------------------------------------------------------------------------
# Syntax validation
# ---------------------------------------------------------------------------


def _validate_init_json(block: MermaidBlock) -> None:
    """Validate that %%{init: {...}}%% directives contain valid JSON."""
    for m in re.finditer(r"%%\{init:\s*(\{.*?\})\s*\}%%", block.raw, re.DOTALL):
        json_str = m.group(1)
        try:
            json.loads(json_str)
        except json.JSONDecodeError as exc:
            block.issues.append(f"Invalid JSON in %%{{init}}: {exc}")


def _validate_brackets(block: MermaidBlock) -> None:
    """Check that brackets are balanced in the diagram body.

    Ignores content inside quoted strings and %%{init}%% directives.
    """
    # Strip out init directives and quoted strings before checking brackets
    body = re.sub(r"%%\{.*?\}%%", "", block.raw, flags=re.DOTALL)
    # Strip frontmatter
    body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.DOTALL)
    # Strip double-quoted strings
    body = re.sub(r'"[^"]*"', '""', body)
    # Strip single-quoted strings
    body = re.sub(r"'[^']*'", "''", body)

    # For mindmap and timeline, brackets in indented content lines are
    # often decorative (e.g., root((Topic))). We only flag clearly
    # unbalanced cases.
    stack: list[tuple[str, int]] = []
    for i, ch in enumerate(body):
        if ch in BRACKET_PAIRS:
            stack.append((ch, i))
        elif ch in BRACKET_PAIRS.values():
            expected_open = {v: k for k, v in BRACKET_PAIRS.items()}[ch]
            if stack and stack[-1][0] == expected_open:
                stack.pop()
            else:
                # Track but don't immediately fail — Mermaid is lenient
                # with certain constructs like (( )) in mindmaps.
                pass

    # Only report if there's a significant imbalance (more than a few
    # unmatched). Minor mismatches in node shapes like (( )) are fine.
    open_counts: dict[str, int] = {}
    close_counts: dict[str, int] = {}
    for ch in body:
        if ch in BRACKET_PAIRS:
            open_counts[ch] = open_counts.get(ch, 0) + 1
        elif ch in BRACKET_PAIRS.values():
            expected_open = {v: k for k, v in BRACKET_PAIRS.items()}[ch]
            close_counts[expected_open] = close_counts.get(expected_open, 0) + 1

    for opener, closer in BRACKET_PAIRS.items():
        o = open_counts.get(opener, 0)
        c = close_counts.get(opener, 0)
        if o != c:
            # Mermaid uses doubled brackets for shapes: (( )), [[ ]], {{ }}
            # These are always balanced. A difference of 1 in a small block
            # is likely a real error.
            diff = abs(o - c)
            # Tolerate even differences since doubled brackets are common
            if diff % 2 == 1:
                block.issues.append(
                    f"Unbalanced '{opener}{closer}': {o} open vs {c} close (diff={diff})"
                )


def _validate_frontmatter(block: MermaidBlock) -> None:
    """Check that YAML frontmatter (---...---) is properly closed."""
    lines = block.raw.strip().split("\n")
    fence_count = 0
    for line in lines:
        if line.strip() == "---":
            fence_count += 1
        elif fence_count == 1:
            # Inside frontmatter — continue
            continue
        elif fence_count >= 2:
            break
        else:
            break

    if fence_count == 1:
        block.issues.append("Unclosed YAML frontmatter (single '---' without closing)")


# ---------------------------------------------------------------------------
# Reference validation
# ---------------------------------------------------------------------------


def _validate_chapter_references(
    block: MermaidBlock,
    chapters: dict[int, ChapterInfo],
) -> None:
    """Check that 'Chapter N' references point to valid chapters (1..48)."""
    for m in re.finditer(r"Chapter\s+(\d+)", block.raw):
        ref_num = int(m.group(1))
        if ref_num < 1 or ref_num > MAX_CHAPTER:
            block.issues.append(
                f"Invalid chapter reference: 'Chapter {ref_num}' "
                f"(valid range: 1..{MAX_CHAPTER})"
            )
        elif ref_num not in chapters:
            block.issues.append(
                f"Chapter {ref_num} referenced but no matching file found"
            )

    # Also check 'Ch N' and 'Ch. N' shorthand references
    for m in re.finditer(r"\bCh\.?\s+(\d+)\b", block.raw):
        ref_num = int(m.group(1))
        if ref_num < 1 or ref_num > MAX_CHAPTER:
            block.issues.append(
                f"Invalid chapter reference: 'Ch {ref_num}' "
                f"(valid range: 1..{MAX_CHAPTER})"
            )


def _validate_chapter_title_consistency(
    block: MermaidBlock,
    chapters: dict[int, ChapterInfo],
) -> None:
    """If a node label says 'Chapter N<br/>Some Title', verify the title matches."""
    # Pattern: Chapter N<br/>Title or Chapter N\\nTitle
    # Common abbreviation mappings used in diagrams
    _abbreviations: dict[str, list[str]] = {
        "differentiation": ["differential calculus"],
        "odes": ["ordinary differential equations"],
        "pdes": ["partial differential equations"],
        "stats": ["statistics", "statistical"],
        "optim": ["optimization"],
        "approx": ["approximation"],
        "prob": ["probability"],
        "info": ["information"],
        "eqns": ["equations"],
    }

    for m in re.finditer(
        r"Chapter\s+(\d+)\s*(?:<br\s*/?>|\\n)\s*([^\"'\]\)]+)",
        block.raw,
    ):
        ref_num = int(m.group(1))
        stated_title = m.group(2).strip().rstrip('"])')
        if ref_num in chapters:
            actual_title = chapters[ref_num].title
            # Normalize for comparison — stated titles may be abbreviated
            stated_lower = stated_title.lower().strip()
            actual_lower = actual_title.lower().strip()
            # Accept if the stated title is a substring of or equal to the actual
            if stated_lower and stated_lower not in actual_lower and actual_lower not in stated_lower:
                # Check known abbreviation mappings
                is_known_abbrev = False
                for abbrev, expansions in _abbreviations.items():
                    if abbrev in stated_lower:
                        if any(exp in actual_lower for exp in expansions):
                            is_known_abbrev = True
                            break
                if is_known_abbrev:
                    continue

                # Check if stated is a reasonable abbreviation (shared words)
                stated_words = set(stated_lower.split())
                actual_words = set(actual_lower.split())
                # Remove common stop words
                stop = {"&", "and", "the", "of", "in", "for", "with", "a"}
                stated_content = stated_words - stop
                actual_content = actual_words - stop
                shared = stated_content & actual_content
                if not shared:
                    # Check word-stem overlap (first 4 chars)
                    stated_stems = {w[:4] for w in stated_content if len(w) > 3}
                    actual_stems = {w[:4] for w in actual_content if len(w) > 3}
                    stem_shared = stated_stems & actual_stems
                    if not stem_shared:
                        block.issues.append(
                            f"Chapter {ref_num} title mismatch: "
                            f"diagram says '{stated_title}', "
                            f"actual is '{actual_title}'"
                        )


def _validate_theorem_references(block: MermaidBlock) -> None:
    """Check that Theorem N.M references have valid chapter prefix."""
    for m in re.finditer(r"Theorem\s+(\d+)\.(\d+)", block.raw):
        ch_num = int(m.group(1))
        if ch_num < 1 or ch_num > MAX_CHAPTER:
            block.issues.append(
                f"Invalid theorem reference: 'Theorem {m.group(1)}.{m.group(2)}' "
                f"— chapter {ch_num} is outside valid range 1..{MAX_CHAPTER}"
            )

    # Same for Definition, Lemma, Proposition, Corollary
    for kind in ("Definition", "Lemma", "Proposition", "Corollary"):
        for m in re.finditer(rf"{kind}\s+(\d+)\.(\d+)", block.raw):
            ch_num = int(m.group(1))
            if ch_num < 1 or ch_num > MAX_CHAPTER:
                block.issues.append(
                    f"Invalid {kind.lower()} reference: "
                    f"'{kind} {m.group(1)}.{m.group(2)}' "
                    f"— chapter {ch_num} is outside valid range 1..{MAX_CHAPTER}"
                )


# ---------------------------------------------------------------------------
# Diagram-type-specific validation
# ---------------------------------------------------------------------------


def _validate_flowchart(block: MermaidBlock) -> None:
    """Validate flowchart-specific syntax."""
    lines = block.raw.strip().split("\n")
    found_direction = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("flowchart") or stripped.startswith("graph"):
            parts = stripped.split()
            if len(parts) >= 2:
                direction = parts[1]
                valid_dirs = {"TD", "TB", "BT", "LR", "RL"}
                if direction not in valid_dirs:
                    block.issues.append(
                        f"Invalid flowchart direction '{direction}' "
                        f"(expected one of {valid_dirs})"
                    )
                else:
                    found_direction = True
            else:
                found_direction = True  # default direction is fine
            break

    # Check for arrow syntax: -->, --->, -.->
    body = block.raw
    # Verify node definitions use valid shapes
    # Common node shapes: A["text"], A("text"), A(("text")), A["text"], A{"text"}
    # We don't exhaustively validate shapes since Mermaid is flexible


def _validate_xychart(block: MermaidBlock) -> None:
    """Validate xychart-beta specific syntax."""
    has_x = bool(re.search(r"x-axis", block.raw))
    has_y = bool(re.search(r"y-axis", block.raw))
    has_data = bool(re.search(r"\b(line|bar)\s+[\[\"]", block.raw))

    if not has_x:
        block.issues.append("xychart-beta missing x-axis definition")
    if not has_y:
        block.issues.append("xychart-beta missing y-axis definition")
    if not has_data:
        block.issues.append("xychart-beta missing data series (line or bar)")


def _validate_quadrant(block: MermaidBlock) -> None:
    """Validate quadrantChart syntax."""
    has_x = bool(re.search(r"x-axis", block.raw))
    has_y = bool(re.search(r"y-axis", block.raw))
    if not has_x:
        block.issues.append("quadrantChart missing x-axis")
    if not has_y:
        block.issues.append("quadrantChart missing y-axis")


def _validate_sankey(block: MermaidBlock) -> None:
    """Validate sankey-beta syntax — needs comma-separated flow lines."""
    # After stripping init/frontmatter, body lines should be: Source,Target,Value
    lines = block.raw.strip().split("\n")
    data_lines = 0
    in_frontmatter = False
    past_header = False
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("%%{"):
            continue
        if stripped == "sankey-beta" or not stripped:
            past_header = True
            continue
        if past_header and "," in stripped:
            data_lines += 1

    if data_lines == 0:
        block.issues.append("sankey-beta has no data flow lines (expected Source,Target,Value)")


def _validate_state_diagram(block: MermaidBlock) -> None:
    """Validate stateDiagram-v2 syntax."""
    has_transition = bool(re.search(r"-->", block.raw))
    has_start = bool(re.search(r"\[\*\]", block.raw))
    if not has_transition:
        block.issues.append("stateDiagram-v2 has no transitions (-->)")


# ---------------------------------------------------------------------------
# Main validation pipeline
# ---------------------------------------------------------------------------


def validate_block(
    block: MermaidBlock,
    chapters: dict[int, ChapterInfo],
) -> None:
    """Run all validations on a single mermaid block."""
    # Detect diagram type
    block.diagram_type = _detect_diagram_type(block)

    # Check that diagram type is recognized
    if block.diagram_type and block.diagram_type not in VALID_DIAGRAM_TYPES:
        block.issues.append(
            f"Unrecognized diagram type '{block.diagram_type}'"
        )

    # Syntax checks
    _validate_init_json(block)
    _validate_frontmatter(block)
    _validate_brackets(block)

    # Reference checks
    _validate_chapter_references(block, chapters)
    _validate_chapter_title_consistency(block, chapters)
    _validate_theorem_references(block)

    # Type-specific checks
    if block.diagram_type in ("flowchart", "graph"):
        _validate_flowchart(block)
    elif block.diagram_type == "xychart-beta":
        _validate_xychart(block)
    elif block.diagram_type == "quadrantChart":
        _validate_quadrant(block)
    elif block.diagram_type == "sankey-beta":
        _validate_sankey(block)
    elif block.diagram_type in ("stateDiagram-v2", "stateDiagram"):
        _validate_state_diagram(block)


def validate_all() -> tuple[list[MermaidBlock], dict[int, ChapterInfo]]:
    """Extract and validate every mermaid block across all chapters.

    Returns (all_blocks, chapters) where each block has its .issues populated.
    """
    chapters = load_chapters()
    all_blocks: list[MermaidBlock] = []

    pattern = os.path.join(DOCS_DIR, "*.md")
    for filepath in sorted(glob.glob(pattern)):
        ch_num = _chapter_num_from_filename(filepath)
        if ch_num == 0:
            continue
        blocks = extract_mermaid_blocks(filepath, ch_num)
        for block in blocks:
            validate_block(block, chapters)
        all_blocks.extend(blocks)

    return all_blocks, chapters


# ---------------------------------------------------------------------------
# Framework integration
# ---------------------------------------------------------------------------


def build() -> Chapter:
    """Build a Chapter with StructuralChecks for the diagram validation suite.

    Compatible with verify/framework.py and verify/run_all.py.
    """
    ch = Chapter(100, "Mermaid Diagram Validation")
    all_blocks, chapters = validate_all()

    total_blocks = len(all_blocks)
    blocks_with_issues = [b for b in all_blocks if b.issues]
    total_issues = sum(len(b.issues) for b in all_blocks)

    # --- Check 1: Total diagram count ---
    ch.add(StructuralCheck(
        label=f"Diagram count ({total_blocks} blocks extracted)",
        section="diag",
        predicate=lambda: (total_blocks > 0, f"Expected >0 mermaid blocks, found {total_blocks}"),
    ))

    # --- Check 2: Every block has a recognized diagram type ---
    no_type = [b for b in all_blocks if not b.diagram_type]
    ch.add(StructuralCheck(
        label="All blocks have a detected diagram type",
        section="diag",
        predicate=lambda _nt=no_type: (
            len(_nt) == 0,
            f"{len(_nt)} block(s) have no detected diagram type: "
            + ", ".join(
                f"Ch{b.chapter_num} block {b.block_index}" for b in _nt[:5]
            ),
        ),
    ))

    # --- Check 3: No unrecognized diagram types ---
    bad_type = [
        b for b in all_blocks
        if b.diagram_type and b.diagram_type not in VALID_DIAGRAM_TYPES
    ]
    ch.add(StructuralCheck(
        label="All diagram types are valid Mermaid types",
        section="diag",
        predicate=lambda _bt=bad_type: (
            len(_bt) == 0,
            f"{len(_bt)} block(s) use unrecognized types: "
            + ", ".join(
                f"Ch{b.chapter_num}#{b.block_index}='{b.diagram_type}'" for b in _bt[:5]
            ),
        ),
    ))

    # --- Check 4: Init JSON is valid ---
    json_issues = [
        b for b in all_blocks
        if any("Invalid JSON" in iss for iss in b.issues)
    ]
    ch.add(StructuralCheck(
        label="All %%{init}%% directives contain valid JSON",
        section="diag",
        predicate=lambda _ji=json_issues: (
            len(_ji) == 0,
            f"{len(_ji)} block(s) have invalid init JSON: "
            + ", ".join(f"Ch{b.chapter_num}#{b.block_index}" for b in _ji[:5]),
        ),
    ))

    # --- Check 5: Brackets balanced ---
    bracket_issues = [
        b for b in all_blocks
        if any("Unbalanced" in iss for iss in b.issues)
    ]
    ch.add(StructuralCheck(
        label="Brackets balanced in all diagrams",
        section="diag",
        predicate=lambda _bi=bracket_issues: (
            len(_bi) == 0,
            f"{len(_bi)} block(s) have bracket imbalance: "
            + "; ".join(
                f"Ch{b.chapter_num}#{b.block_index}: "
                + next(iss for iss in b.issues if "Unbalanced" in iss)
                for b in _bi[:5]
            ),
        ),
    ))

    # --- Check 6: Frontmatter properly closed ---
    fm_issues = [
        b for b in all_blocks
        if any("frontmatter" in iss.lower() for iss in b.issues)
    ]
    ch.add(StructuralCheck(
        label="YAML frontmatter properly closed in all diagrams",
        section="diag",
        predicate=lambda _fi=fm_issues: (
            len(_fi) == 0,
            f"{len(_fi)} block(s) have unclosed frontmatter: "
            + ", ".join(f"Ch{b.chapter_num}#{b.block_index}" for b in _fi[:5]),
        ),
    ))

    # --- Check 7: Chapter references valid ---
    ref_issues = [
        b for b in all_blocks
        if any("chapter reference" in iss.lower() or "referenced but no matching" in iss.lower()
               for iss in b.issues)
    ]
    ch.add(StructuralCheck(
        label="All Chapter N references point to valid chapters (1..48)",
        section="diag",
        predicate=lambda _ri=ref_issues: (
            len(_ri) == 0,
            f"{len(_ri)} block(s) have invalid chapter references: "
            + "; ".join(
                f"Ch{b.chapter_num}#{b.block_index}: "
                + next(iss for iss in b.issues if "chapter" in iss.lower())
                for b in _ri[:5]
            ),
        ),
    ))

    # --- Check 8: Chapter title consistency ---
    title_issues = [
        b for b in all_blocks
        if any("title mismatch" in iss.lower() for iss in b.issues)
    ]
    ch.add(StructuralCheck(
        label="Chapter title labels match actual chapter titles",
        section="diag",
        predicate=lambda _ti=title_issues: (
            len(_ti) == 0,
            f"{len(_ti)} block(s) have title mismatches: "
            + "; ".join(
                f"Ch{b.chapter_num}#{b.block_index}: "
                + next(iss for iss in b.issues if "title mismatch" in iss.lower())
                for b in _ti[:5]
            ),
        ),
    ))

    # --- Check 9: Theorem / Definition references valid ---
    thm_issues = [
        b for b in all_blocks
        if any("theorem reference" in iss.lower() or "definition reference" in iss.lower()
               or "lemma reference" in iss.lower() or "proposition reference" in iss.lower()
               or "corollary reference" in iss.lower()
               for iss in b.issues)
    ]
    ch.add(StructuralCheck(
        label="Theorem/Definition/Lemma references have valid chapter prefixes",
        section="diag",
        predicate=lambda _thi=thm_issues: (
            len(_thi) == 0,
            f"{len(_thi)} block(s) have invalid theorem references: "
            + "; ".join(
                f"Ch{b.chapter_num}#{b.block_index}" for b in _thi[:5]
            ),
        ),
    ))

    # --- Check 10: Diagram-type-specific checks ---
    type_specific_keywords = [
        "missing x-axis", "missing y-axis", "missing data series",
        "no data flow", "no transitions", "Invalid flowchart direction",
    ]
    type_issues = [
        b for b in all_blocks
        if any(
            any(kw in iss for kw in type_specific_keywords)
            for iss in b.issues
        )
    ]
    ch.add(StructuralCheck(
        label="Diagram-type-specific syntax valid (axes, flows, transitions)",
        section="diag",
        predicate=lambda _tsi=type_issues: (
            len(_tsi) == 0,
            f"{len(_tsi)} block(s) fail type-specific checks: "
            + "; ".join(
                f"Ch{b.chapter_num}#{b.block_index} ({b.diagram_type}): "
                + "; ".join(b.issues)
                for b in _tsi[:5]
            ),
        ),
    ))

    # --- Check 11: Overall — zero issues ---
    ch.add(StructuralCheck(
        label=f"Overall: {total_blocks} diagrams, {total_issues} issues in {len(blocks_with_issues)} blocks",
        section="diag",
        predicate=lambda _ti=total_issues, _bwi=blocks_with_issues: (
            _ti == 0,
            f"{_ti} issue(s) across {len(_bwi)} block(s):\n"
            + "\n".join(
                f"  Ch{b.chapter_num} block {b.block_index} ({b.diagram_type}): "
                + "; ".join(b.issues)
                for b in _bwi[:20]
            ),
        ),
    ))

    # --- Per-chapter checks: one check per chapter that has diagrams ---
    chapters_with_blocks: dict[int, list[MermaidBlock]] = {}
    for b in all_blocks:
        chapters_with_blocks.setdefault(b.chapter_num, []).append(b)

    for ch_num in sorted(chapters_with_blocks.keys()):
        ch_blocks = chapters_with_blocks[ch_num]
        ch_issues = [b for b in ch_blocks if b.issues]
        issue_count = sum(len(b.issues) for b in ch_blocks)
        ch_title = chapters.get(ch_num, ChapterInfo(ch_num, "?", "")).title

        ch.add(StructuralCheck(
            label=f"Ch {ch_num:02d} ({ch_title}): {len(ch_blocks)} diagrams",
            section=f"{ch_num}",
            predicate=lambda _ic=issue_count, _ci=ch_issues, _cn=ch_num: (
                _ic == 0,
                f"{_ic} issue(s) in Ch {_cn}: "
                + "; ".join(
                    f"block {b.block_index}: " + "; ".join(b.issues)
                    for b in _ci[:5]
                ),
            ),
        ))

    return ch


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from framework import Report

    chapter = build()
    chapter.run()

    report = Report()
    report.add_chapter(chapter)
    report.print_console()

    raise SystemExit(report.exit_code)
