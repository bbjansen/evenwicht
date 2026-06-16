#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify domain chapter consistency across all 48 Evenwicht chapters.

Checks:
  1. Required H2 sections present and in correct order.
  2. Non-standard H2 headings flagged.
  3. Required structural elements (mermaid, math, tables, code blocks).
  4. Exercise subsections (Routine, Intermediate, Challenging).
  5. Reference subsections (Textbooks, Historical, Online Resources).
  6. Glossary entries use bold-term bullet format.
  7. Connections section includes a mermaid diagram.
  8. Notation section includes a table.
  9. Definition/Theorem numbering uses consistent prefix (3.x).
  10. Formula labels use consistent prefix (F4.x).
  11. Algorithm labels use consistent prefix (Algorithm 5.x).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAIN_DIR = PROJECT_ROOT / "docs" / "domains"

# Expected H2 sections in order.  Section 8 is intentionally skipped.
# Section 13 (Appendix) is optional.
REQUIRED_SECTIONS: list[tuple[int, str]] = [
    (1, "Historical Context"),
    (2, "Why This Chapter Matters"),
    (3, "Notation & Conventions"),
    (4, "Core Theory"),
    (5, "Formulas & Identities"),
    (6, "Algorithms"),
    (7, "Numerical Considerations"),
    (8, "Worked Examples"),
    (9, "Connections"),
    (10, "Exercises"),
    (11, "References"),
    (12, "Glossary"),
]

OPTIONAL_SECTIONS: list[tuple[int, str]] = [
    (13, "Appendix"),
]

ALL_KNOWN = {title for _, title in REQUIRED_SECTIONS + OPTIONAL_SECTIONS}
TITLE_TO_NUM = {title: num for num, title in REQUIRED_SECTIONS + OPTIONAL_SECTIONS}
NUM_TO_TITLE = {num: title for num, title in REQUIRED_SECTIONS + OPTIONAL_SECTIONS}

EXERCISE_SUBSECTIONS = {"Routine", "Intermediate", "Challenging"}
REFERENCE_SUBSECTIONS = {"Textbooks", "Historical", "Online Resources"}

# Accept both numbered (`## 1. Historical Context`) and bare (`## Historical Context`) H2s.
H2_RE = re.compile(r"^## (?:(\d+)\.\s+)?(.+?)\s*$", re.MULTILINE)
H3_RE = re.compile(r"^### (.+)$", re.MULTILINE)
MERMAID_RE = re.compile(r"^```mermaid\b", re.MULTILINE)
MATH_BLOCK_RE = re.compile(r"^\$\$", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|.+\|$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"^```\w+", re.MULTILINE)
GLOSSARY_ENTRY_RE = re.compile(r"^- \*\*.+?\*\*", re.MULTILINE)
DEFINITION_RE = re.compile(
    r"\*\*(?:Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example)"
    r"\s+(\d+)\.(\d+)",
)
FORMULA_RE = re.compile(r"\*\*F(\d+)\.(\d+)\*\*")
ALGORITHM_RE = re.compile(r"^### Algorithm (\d+)\.(\d+)", re.MULTILINE)


def get_chapter_files() -> list[Path]:
    return sorted(DOMAIN_DIR.glob("[0-9]*.md"))


def extract_chapter_number(path: Path) -> int:
    m = re.match(r"(\d+)", path.name)
    return int(m.group(1)) if m else 0


def section_text(text: str, section_num: int) -> str:
    """Extract the text between a known section heading and the next ## heading."""
    title = NUM_TO_TITLE.get(section_num)
    if not title:
        return ""
    heading = re.search(
        rf"^## (?:{section_num}\.\s+)?{re.escape(title)}\s*$",
        text,
        re.MULTILINE,
    )
    if not heading:
        return ""
    start = heading.end() + 1
    next_h2 = re.search(r"^## ", text[start:], re.MULTILINE)
    return text[start : start + next_h2.start()] if next_h2 else text[start:]


def analyse_chapter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    ch_num = extract_chapter_number(path)

    # H2 sections — accept numbered or bare form; map bare titles to canonical numbers.
    h2_matches: list[tuple[int, str]] = []
    for m in H2_RE.finditer(text):
        num_str = m.group(1)
        title = m.group(2).strip()
        num = int(num_str) if num_str else TITLE_TO_NUM.get(title, 0)
        h2_matches.append((num, title))
    h2_numbers = [n for n, _ in h2_matches]
    h2_map = {n: title for n, title in h2_matches}

    missing_sections = [
        f"{n}. {title}"
        for n, title in REQUIRED_SECTIONS
        if n not in h2_map
    ]

    extra_sections = [
        f"{n}. {title}"
        for n, title in h2_matches
        if title not in ALL_KNOWN
    ]

    # Order check: required section numbers should appear in ascending order
    required_nums = [n for n, _ in REQUIRED_SECTIONS]
    present_required = [n for n in h2_numbers if n in set(required_nums)]
    order_ok = present_required == sorted(present_required)

    # Structural elements (whole chapter)
    mermaid_count = len(MERMAID_RE.findall(text))
    math_count = len(MATH_BLOCK_RE.findall(text))
    table_count = len(TABLE_ROW_RE.findall(text))
    code_count = len(CODE_BLOCK_RE.findall(text))

    # Connections section (## 9) should have a mermaid diagram
    connections_text = section_text(text, 9)
    connections_mermaid = len(MERMAID_RE.findall(connections_text))

    # Notation section (## 3) should have a table
    notation_text = section_text(text, 3)
    notation_tables = len(TABLE_ROW_RE.findall(notation_text))

    # Exercise subsections (## 10)
    exercises_text = section_text(text, 10)
    exercise_h3s = set(H3_RE.findall(exercises_text))
    missing_exercise_subs = EXERCISE_SUBSECTIONS - exercise_h3s

    # Reference subsections (## 11)
    references_text = section_text(text, 11)
    reference_h3s = set(H3_RE.findall(references_text))
    missing_reference_subs = REFERENCE_SUBSECTIONS - reference_h3s

    # Glossary entries (## 12)
    glossary_text = section_text(text, 12)
    glossary_entries = len(GLOSSARY_ENTRY_RE.findall(glossary_text))

    # Definition/Theorem numbering prefix — valid: 3 (section-based) or ch_num
    def_prefixes = {int(m.group(1)) for m in DEFINITION_RE.finditer(text)}
    bad_def_prefix = def_prefixes - {3, ch_num}
    def_convention = (
        "section" if 3 in def_prefixes and ch_num not in def_prefixes
        else "chapter" if ch_num in def_prefixes and 3 not in def_prefixes
        else "mixed" if len(def_prefixes) > 1
        else ""
    )

    # Formula numbering prefix — valid: F4 (section-based) or F<ch_num>
    formula_prefixes = {int(m.group(1)) for m in FORMULA_RE.finditer(text)}
    bad_formula_prefix = formula_prefixes - {4, ch_num}

    # Algorithm numbering prefix — valid: 5 (section-based) or ch_num
    algo_prefixes = {int(m.group(1)) for m in ALGORITHM_RE.finditer(text)}
    bad_algo_prefix = algo_prefixes - {5, ch_num}

    return {
        "file": path.name,
        "chapter": ch_num,
        "missing_sections": missing_sections,
        "extra_sections": extra_sections,
        "order_ok": order_ok,
        "mermaid": mermaid_count,
        "math": math_count,
        "tables": table_count,
        "code_blocks": code_count,
        "connections_mermaid": connections_mermaid,
        "notation_tables": notation_tables,
        "missing_exercise_subs": sorted(missing_exercise_subs),
        "missing_reference_subs": sorted(missing_reference_subs),
        "glossary_entries": glossary_entries,
        "bad_def_prefix": sorted(bad_def_prefix),
        "bad_formula_prefix": sorted(bad_formula_prefix),
        "bad_algo_prefix": sorted(bad_algo_prefix),
        "def_convention": def_convention,
    }


def main() -> int:
    files = get_chapter_files()
    if not files:
        print(f"ERROR: No domain files found in {DOMAIN_DIR}")
        return 1

    data = [analyse_chapter(f) for f in files]
    issues: list[str] = []

    # ── Section coverage matrix ──────────────────────────────────────────
    print("=" * 78)
    print("DOMAIN CHAPTER CONSISTENCY — Evenwicht")
    print("=" * 78)
    print()
    print(f"{'Section':<46} {'Present':>7} {'Missing':>7}")
    print("-" * 62)
    for num, title in REQUIRED_SECTIONS:
        present = sum(
            1 for d in data if f"{num}. {title}" not in d["missing_sections"]
        )
        missing = len(data) - present
        marker = " ***" if missing > 0 else ""
        print(f"  {num}. {title:<42} {present:>7} {missing:>7}{marker}")
    for num, title in OPTIONAL_SECTIONS:
        present = sum(
            1
            for d in data
            if f"{num}. {title}" not in d["missing_sections"]
            and not all(
                f"{num}. {title}" in dd["missing_sections"] for dd in data
            )
        )
        # Count how many actually have it (not in missing AND it exists)
        has_it = sum(
            1 for d in data if f"{num}. {title}" not in d["missing_sections"]
        )
        print(f"  {num}. {title:<42} {has_it:>7} {'(opt)':>7}")
    print()

    # ── Per-document overview ────────────────────────────────────────────
    print("=" * 78)
    print("PER-DOCUMENT OVERVIEW")
    print("=" * 78)
    print()
    print(
        f"{'Document':<30} {'H2 ok':>5} {'Order':>5} "
        f"{'Mermaid':>7} {'Math':>5} {'Tables':>6} {'Code':>5} "
        f"{'Gloss':>5}"
    )
    print("-" * 78)

    for d in data:
        h2_ok = "Y" if not d["missing_sections"] else "N"
        order = "Y" if d["order_ok"] else "N"
        print(
            f"  {d['file']:<28} {h2_ok:>5} {order:>5} "
            f"{d['mermaid']:>7} {d['math']:>5} {d['tables']:>6} "
            f"{d['code_blocks']:>5} {d['glossary_entries']:>5}"
        )

    # ── Missing required sections ────────────────────────────────────────
    docs_missing = [d for d in data if d["missing_sections"]]
    if docs_missing:
        print()
        print("=" * 78)
        print(f"MISSING REQUIRED SECTIONS ({len(docs_missing)} chapters)")
        print("=" * 78)
        for d in docs_missing:
            print(f"\n  {d['file']}:")
            for s in d["missing_sections"]:
                issues.append(f"{d['file']}: missing '{s}'")
                print(f"    - {s}")

    # ── Section order violations ─────────────────────────────────────────
    docs_order = [d for d in data if not d["order_ok"]]
    if docs_order:
        print()
        print("=" * 78)
        print(f"SECTION ORDER VIOLATIONS ({len(docs_order)} chapters)")
        print("=" * 78)
        for d in docs_order:
            issues.append(f"{d['file']}: sections out of order")
            print(f"  - {d['file']}")

    # ── Non-standard H2 headings ─────────────────────────────────────────
    docs_extra = [d for d in data if d["extra_sections"]]
    if docs_extra:
        print()
        print("=" * 78)
        print(f"NON-STANDARD H2 HEADINGS ({len(docs_extra)} chapters)")
        print("=" * 78)
        for d in docs_extra:
            print(f"\n  {d['file']}:")
            for s in d["extra_sections"]:
                print(f"    - {s}")

    # ── Structural element warnings ──────────────────────────────────────
    structural_issues: list[str] = []
    for d in data:
        if d["mermaid"] == 0:
            structural_issues.append(f"{d['file']}: 0 mermaid diagrams")
        if d["math"] == 0:
            structural_issues.append(f"{d['file']}: 0 math blocks")
        if d["tables"] == 0:
            structural_issues.append(f"{d['file']}: 0 tables")
        if d["code_blocks"] == 0:
            structural_issues.append(f"{d['file']}: 0 code blocks")
        if d["connections_mermaid"] == 0:
            structural_issues.append(
                f"{d['file']}: Connections section has no mermaid diagram"
            )
        if d["notation_tables"] == 0:
            structural_issues.append(
                f"{d['file']}: Notation & Conventions section has no table"
            )

    if structural_issues:
        print()
        print("=" * 78)
        print(f"STRUCTURAL ELEMENT WARNINGS ({len(structural_issues)})")
        print("=" * 78)
        for s in structural_issues:
            issues.append(s)
            print(f"  - {s}")

    # ── Exercise subsection issues ───────────────────────────────────────
    docs_ex = [d for d in data if d["missing_exercise_subs"]]
    if docs_ex:
        print()
        print("=" * 78)
        print(f"MISSING EXERCISE SUBSECTIONS ({len(docs_ex)} chapters)")
        print("=" * 78)
        for d in docs_ex:
            print(f"\n  {d['file']}:")
            for s in d["missing_exercise_subs"]:
                issues.append(
                    f"{d['file']}: exercises missing '{s}' subsection"
                )
                print(f"    - {s}")

    # ── Reference subsection issues ──────────────────────────────────────
    docs_ref = [d for d in data if d["missing_reference_subs"]]
    if docs_ref:
        print()
        print("=" * 78)
        print(f"MISSING REFERENCE SUBSECTIONS ({len(docs_ref)} chapters)")
        print("=" * 78)
        for d in docs_ref:
            print(f"\n  {d['file']}:")
            for s in d["missing_reference_subs"]:
                issues.append(
                    f"{d['file']}: references missing '{s}' subsection"
                )
                print(f"    - {s}")

    # ── Glossary warnings ────────────────────────────────────────────────
    docs_gloss = [d for d in data if d["glossary_entries"] == 0]
    if docs_gloss:
        print()
        print("=" * 78)
        print(f"CHAPTERS WITH NO GLOSSARY ENTRIES ({len(docs_gloss)})")
        print("=" * 78)
        for d in docs_gloss:
            issues.append(f"{d['file']}: glossary has 0 entries")
            print(f"  - {d['file']}")

    # ── Numbering convention split ──────────────────────────────────────
    section_conv = [d for d in data if d["def_convention"] == "section"]
    chapter_conv = [d for d in data if d["def_convention"] == "chapter"]
    mixed_conv = [d for d in data if d["def_convention"] == "mixed"]

    print()
    print("=" * 78)
    print("DEFINITION NUMBERING CONVENTIONS")
    print("=" * 78)
    print(f"  Section-based (3.x):   {len(section_conv)} chapters")
    if section_conv:
        names = ", ".join(d["file"].split("-")[0] for d in section_conv)
        print(f"    Ch {names}")
    print(f"  Chapter-based (N.x):   {len(chapter_conv)} chapters")
    if chapter_conv:
        names = ", ".join(d["file"].split("-")[0] for d in chapter_conv)
        print(f"    Ch {names}")
    if mixed_conv:
        print(f"  Mixed (both):          {len(mixed_conv)} chapters")
        for d in mixed_conv:
            issues.append(f"{d['file']}: mixed definition numbering")
            print(f"    - {d['file']}")

    # ── Numbering prefix issues ──────────────────────────────────────────
    numbering_issues: list[str] = []
    for d in data:
        if d["bad_def_prefix"]:
            prefixes = ", ".join(str(p) for p in d["bad_def_prefix"])
            numbering_issues.append(
                f"{d['file']}: Definition/Theorem prefix {prefixes} "
                f"(expected 3 or {d['chapter']})"
            )
        if d["bad_formula_prefix"]:
            prefixes = ", ".join(str(p) for p in d["bad_formula_prefix"])
            numbering_issues.append(
                f"{d['file']}: Formula prefix F{prefixes} "
                f"(expected F4 or F{d['chapter']})"
            )
        if d["bad_algo_prefix"]:
            prefixes = ", ".join(str(p) for p in d["bad_algo_prefix"])
            numbering_issues.append(
                f"{d['file']}: Algorithm prefix {prefixes} "
                f"(expected 5 or {d['chapter']})"
            )

    if numbering_issues:
        print()
        print("=" * 78)
        print(f"NUMBERING PREFIX ERRORS ({len(numbering_issues)})")
        print("=" * 78)
        for s in numbering_issues:
            issues.append(s)
            print(f"  - {s}")

    # ── Summary ──────────────────────────────────────────────────────────
    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Total chapters:                {len(data)}")
    print(
        f"  All required sections present: "
        f"{len(data) - len(docs_missing)}/{len(data)}"
    )
    print(
        f"  Correct section order:         "
        f"{len(data) - len(docs_order)}/{len(data)}"
    )
    print(f"  Non-standard H2 headings:      {len(docs_extra)} chapters")
    print(f"  Structural warnings:           {len(structural_issues)}")
    print(f"  Exercise sub issues:           {len(docs_ex)} chapters")
    print(f"  Reference sub issues:          {len(docs_ref)} chapters")
    print(f"  Numbering issues:              {len(numbering_issues)}")
    print(f"  Total issues:                  {len(issues)}")
    print()

    if issues:
        return 1
    print("All domain chapters pass consistency checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
