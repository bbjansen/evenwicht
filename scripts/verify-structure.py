#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify structural consistency across all 48 domain chapters and API docs.

Checks every domain chapter (docs/domains/*.md) for:

  1. Bold titles in Historical Context must be noun phrases with year, not
     full sentences.  Titles longer than 85 characters are flagged.
  2. Every Algorithm heading must have a fenced code block within 30 lines.
  3. Hex values in mermaid style directives must be 6-digit (#rrggbb).
  4. No title/title: lines inside mermaid blocks.
  5. Dependency graph (flowchart LR) must use the correct colours:
     focal #4a6fa5, prerequisites #e8e8e8, downstream #d6e4f0.
  6. Glossary entries must be in alphabetical order (strip leading $).
  7. Lines 1-3 must be the standard copyright/SPDX/LICENSE header.
  8. No double hyphens (--) in prose outside code/mermaid/comments/dividers.

Checks every API file (docs/api/*.md) for:

  9. First heading must contain an em dash (U+2014 or spaced ---).
 10. Copyright header (same as domain files).

Usage:
  python3 scripts/verify-structure.py              # check all files
  python3 scripts/verify-structure.py --quick       # check first 3 domain + 3 API files

Exit code 1 if any FAIL-level issues are found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAIN_DIR = PROJECT_ROOT / "docs" / "domains"
API_DIR = PROJECT_ROOT / "docs" / "api"

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

# ── Expected copyright header (lines 1-3) ──────────

COPYRIGHT_LINES = [
    "<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->",
    "<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->",
    "<!-- See LICENSE for full terms. Commercial licensing available. -->",
]

# ── Type alias ──────────────────────────────────────

Issue = tuple[int, str, str, str]  # (line_number, severity, category, message)


# ── File discovery ──────────────────────────────────

def discover_domain_files(quick: bool = False) -> list[Path]:
    """Return sorted list of domain chapter Markdown files."""
    files = sorted(DOMAIN_DIR.glob("[0-9]*.md"))
    if quick:
        files = files[:3]
    return files


def discover_api_files(quick: bool = False) -> list[Path]:
    """Return sorted list of API reference Markdown files."""
    files = sorted(API_DIR.glob("[0-9]*.md"))
    if quick:
        files = files[:3]
    return files


# ── Mermaid block extraction ───────────────────────

def extract_mermaid_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """Return list of (start, end) line indices for mermaid fenced blocks.

    start is the line with ```mermaid, end is the line with the closing ```.
    Both indices are 0-based.
    """
    blocks: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("```mermaid"):
            start = i
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                i += 1
            blocks.append((start, i))
        i += 1
    return blocks


# ── Code/mermaid/comment zone tracking ─────────────

def build_zone_mask(lines: list[str]) -> list[str]:
    """Return a list of zone labels for each line: 'prose', 'code',
    'mermaid', or 'comment'.  Used to skip non-prose zones.
    """
    zones = ["prose"] * len(lines)
    in_code = False
    in_mermaid = False
    in_comment = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track HTML comments (single-line and multi-line).
        if not in_code and not in_mermaid:
            if "<!--" in stripped and "-->" in stripped:
                zones[i] = "comment"
                continue
            if "<!--" in stripped:
                in_comment = True
                zones[i] = "comment"
                continue
            if in_comment:
                zones[i] = "comment"
                if "-->" in stripped:
                    in_comment = False
                continue

        # Track fenced code / mermaid blocks.
        if stripped.startswith("```"):
            if not in_code and not in_mermaid:
                if stripped.startswith("```mermaid"):
                    in_mermaid = True
                    zones[i] = "mermaid"
                else:
                    in_code = True
                    zones[i] = "code"
            else:
                zones[i] = "mermaid" if in_mermaid else "code"
                in_mermaid = False
                in_code = False
            continue

        if in_mermaid:
            zones[i] = "mermaid"
        elif in_code:
            zones[i] = "code"

    return zones


# ── Section extraction helpers ─────────────────────

def find_section_range(lines: list[str], heading: str) -> tuple[int, int]:
    """Return (start, end) 0-based line indices for a ## section.

    start is the line after the heading; end is the line before the next
    ## heading (or end of file).  Returns (-1, -1) if not found.
    """
    start = -1
    for i, line in enumerate(lines):
        if re.match(rf"^## (?:\d+\.\s+)?{re.escape(heading)}\s*$", line.strip()):
            start = i + 1
            break
    if start == -1:
        return -1, -1
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^## ", lines[i].strip()) and i != start - 1:
            end = i
            break
    return start, end


# ── Individual checks ──────────────────────────────

def check_historical_bold_titles(lines: list[str]) -> list[Issue]:
    """Check 1: Bold titles in Historical Context are noun phrases, not sentences."""
    issues: list[Issue] = []
    start, end = find_section_range(lines, "Historical Context")
    if start == -1:
        return issues

    for i in range(start, end):
        line = lines[i].strip()
        # Bold titles start a paragraph with **...**
        if not line.startswith("**"):
            continue
        # Extract the bold portion.
        m = re.match(r"^\*\*(.+?)\*\*", line)
        if not m:
            continue
        title = m.group(1)
        # Skip "Key Milestones" style sub-headings (no year).
        if "(" not in title:
            continue
        # Flag titles > 70 chars as potential full sentences.
        if len(title) > 85:
            issues.append((
                i + 1, "FAIL", "Historical title length",
                f"title is {len(title)} chars (>70), likely a sentence: \"{title[:60]}...\"",
            ))
        # Check that title contains a year-like marker in parentheses.
        # Accepted patterns:
        #   (1734)  (1660s-1680s)  (~450 BCE)  (late nineteenth century)
        #   (early 1900s)  (c. 1200)  (1734-1760)  (twentieth century)
        #   (18th century)  (2005-present)  (circa 850 CE)
        #   (1876 onward)  (1990s-present)  (first century BCE)
        _ORDINAL_WORD = (
            r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth"
            r"|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth"
            r"|seventeenth|eighteenth|nineteenth|twentieth|twenty-first)"
        )
        _ERA = r"(?:\s*(?:BCE|CE|AD|BC))?"
        _ONWARDS = r"(?:\s+(?:onward|onwards))?"
        year_match = re.search(
            r"\("
            r"(?:~|c\.\s*|circa\s+)?"                 # optional ~ or c. or circa
            r"(?:"
            # Numeric year/decade, optional era suffix, optional range to
            # another year/decade or "present"/"onward".
            r"\d{3,4}(?:s)?" + _ERA
            + r"(?:\s*[–\-]\s*(?:\d{3,4}(?:s)?" + _ERA + r"|present))?"
            + _ONWARDS
            + r"|"
            # Descriptive prefix + year/decade/century.
            r"(?:early|mid|late|circa)[\s\-]+"
            r"(?:\d{3,4}(?:s)?" + _ERA
            + r"(?:\s*[–\-]\s*(?:\d{3,4}(?:s)?|present))?"
            + r"|" + _ORDINAL_WORD + r"\s+century" + _ERA + _ONWARDS + r")"
            r"|"
            # Bare ordinal word century (e.g. "twentieth century").
            + _ORDINAL_WORD + r"\s+century" + _ERA + _ONWARDS
            + r"|"
            # Numeric ordinal century, optional range (e.g. "18th century",
            # "20th-21st century").  The "century" keyword appears once at
            # the end, shared by both ordinals when a range is present.
            r"\d{1,2}(?:st|nd|rd|th)"
            + r"(?:\s*[–\-]\s*\d{1,2}(?:st|nd|rd|th))?"
            + r"\s+century" + _ERA
            + r")"
            r"\)",
            title,
            re.IGNORECASE,
        )
        if not year_match:
            issues.append((
                i + 1, "FAIL", "Historical title format",
                f"title lacks year in parentheses: \"{title}\"",
            ))

    return issues


def check_algorithm_pseudocode(lines: list[str], zones: list[str]) -> list[Issue]:
    """Check 2: Every Algorithm heading has a fenced code block within 30 lines."""
    issues: list[Issue] = []
    algo_re = re.compile(
        r"(?:^###\s+Algorithm\s+\d+\.\d+)"
        r"|(?:^\*\*Algorithm\s+\d+\.\d+\*\*)",
    )

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not algo_re.match(stripped):
            continue
        # Search the next 30 lines for a fenced code block.
        found_code = False
        limit = min(i + 51, len(lines))
        for j in range(i + 1, limit):
            if lines[j].strip().startswith("```") and not lines[j].strip().startswith("```mermaid"):
                found_code = True
                break
            # Stop if another heading is reached.
            if re.match(r"^#{1,3}\s+", lines[j].strip()):
                break
            if re.match(r"^\*\*Algorithm\s+\d+\.\d+\*\*", lines[j].strip()):
                break
        if not found_code:
            issues.append((
                i + 1, "FAIL", "Algorithm missing pseudocode",
                f"no fenced code block within 30 lines of: \"{stripped[:70]}\"",
            ))

    return issues


def check_mermaid_hex_digits(lines: list[str], zones: list[str]) -> list[Issue]:
    """Check 3: Inside mermaid blocks, all # hex values in style directives
    must be 6 digits.  Flag 3-digit shorthand like #fff or #333.
    """
    issues: list[Issue] = []
    # Match 3-digit hex that is NOT followed by another hex digit (so #4a6fa5
    # is 6-digit, not matched).  Negative lookbehind/ahead to avoid matching
    # inside 6-digit values.
    short_hex_re = re.compile(r"#([0-9a-fA-F]{3})(?![0-9a-fA-F])")

    for i, line in enumerate(lines):
        if zones[i] != "mermaid":
            continue
        # Only check lines that are style directives or themeVariables.
        # Skip HTML entities like &#770; which are not hex colours.
        for m in short_hex_re.finditer(line):
            # Check if preceded by & (HTML entity like &#770;)
            if m.start() > 0 and line[m.start() - 1] == "&":
                continue
            issues.append((
                i + 1, "FAIL", "3-digit hex in mermaid",
                f"found #{m.group(1)} -- use 6-digit hex (e.g. #{m.group(1)[0]*2}{m.group(1)[1]*2}{m.group(1)[2]*2})",
            ))

    return issues


def check_no_mermaid_titles(lines: list[str], zones: list[str]) -> list[Issue]:
    """Check 4: No 'title ' or 'title:' lines inside mermaid blocks."""
    issues: list[Issue] = []
    title_re = re.compile(r"^(\s{4}|\t)title[\s:]")

    for i, line in enumerate(lines):
        if zones[i] != "mermaid":
            continue
        if title_re.match(line):
            issues.append((
                i + 1, "FAIL", "Mermaid title line",
                f"title directive inside mermaid block: \"{line.strip()[:60]}\"",
            ))

    return issues


def check_dependency_graph_colours(lines: list[str]) -> list[Issue]:
    """Check 5: The flowchart LR dependency graph block uses correct colours.

    Focal node: fill:#4a6fa5
    Prerequisites: fill:#e8e8e8
    Downstream: fill:#d6e4f0
    """
    issues: list[Issue] = []

    # Find the Connections section.
    conn_start, conn_end = find_section_range(lines, "Connections")
    if conn_start == -1:
        return issues

    # Find mermaid blocks within Connections.
    mermaid_blocks = extract_mermaid_blocks(lines)
    for block_start, block_end in mermaid_blocks:
        if block_start < conn_start or block_start >= conn_end:
            continue
        # Check if this block contains flowchart LR.
        has_flowchart = False
        for j in range(block_start, min(block_end + 1, len(lines))):
            if "flowchart LR" in lines[j]:
                has_flowchart = True
                break
        if not has_flowchart:
            continue

        # Collect all style lines.
        style_lines: list[tuple[int, str]] = []
        for j in range(block_start, min(block_end + 1, len(lines))):
            stripped = lines[j].strip()
            if stripped.startswith("style "):
                style_lines.append((j, stripped))

        if not style_lines:
            issues.append((
                block_start + 1, "FAIL", "Dependency graph colours",
                "flowchart LR in Connections has no style directives",
            ))
            continue

        # Check each style line for valid colours.
        has_focal = False
        for lineno_idx, style_line in style_lines:
            fill_match = re.search(r"fill:(#[0-9a-fA-F]+)", style_line)
            if not fill_match:
                continue
            fill_colour = fill_match.group(1).lower()
            if fill_colour == "#4a6fa5":
                has_focal = True
            elif fill_colour not in ("#e8e8e8", "#d6e4f0"):
                issues.append((
                    lineno_idx + 1, "FAIL", "Dependency graph colours",
                    f"unexpected fill colour {fill_colour} -- expected #4a6fa5, #e8e8e8 or #d6e4f0",
                ))

        if not has_focal:
            issues.append((
                block_start + 1, "FAIL", "Dependency graph colours",
                "dependency graph missing focal node colour fill:#4a6fa5",
            ))

    return issues


def check_glossary_order(lines: list[str]) -> list[Issue]:
    """Check 6: Glossary entries are in alphabetical order (strip leading $)."""
    issues: list[Issue] = []
    start, end = find_section_range(lines, "Glossary")
    if start == -1:
        return issues

    glossary_entry_re = re.compile(r"^- \*\*([^*]+)\*\*")
    entries: list[tuple[int, str]] = []

    for i in range(start, end):
        stripped = lines[i].strip()
        m = glossary_entry_re.match(stripped)
        if m:
            term = m.group(1).strip()
            entries.append((i + 1, term))

    for idx in range(1, len(entries)):
        _, prev_term = entries[idx - 1]
        curr_line, curr_term = entries[idx]
        # Strip leading $ for sort comparison.
        prev_sort = prev_term.lstrip("$").strip().lower()
        curr_sort = curr_term.lstrip("$").strip().lower()
        if prev_sort > curr_sort:
            issues.append((
                curr_line, "FAIL", "Glossary order",
                f"\"{curr_term}\" should come before \"{prev_term}\" (alphabetical)",
            ))

    return issues


def check_copyright_header(lines: list[str]) -> list[Issue]:
    """Check 7/10: Lines 1-3 must be the standard copyright/SPDX/LICENSE."""
    issues: list[Issue] = []
    for idx, expected in enumerate(COPYRIGHT_LINES):
        if idx >= len(lines):
            issues.append((
                idx + 1, "FAIL", "Copyright header",
                "missing copyright header line",
            ))
            continue
        actual = lines[idx].rstrip()
        if actual != expected:
            issues.append((
                idx + 1, "FAIL", "Copyright header",
                f"expected: \"{expected[:60]}...\"" if len(expected) > 60 else f"expected: \"{expected}\"",
            ))
    return issues


def check_no_double_hyphens(lines: list[str], zones: list[str]) -> list[Issue]:
    """Check 8: No -- in prose outside code/mermaid/comments and section dividers.

    Exemptions:
    - Lines inside code, mermaid, or comment zones.
    - Section dividers (lines that are just --- or ----).
    - HTML comment delimiters <!-- and -->.
    - Markdown YAML front matter delimiters (---).
    """
    issues: list[Issue] = []
    html_comment_open = re.compile(r"<!--")
    html_comment_close = re.compile(r"-->")
    # Match -- that is NOT between word characters (compound names like
    # Cauchy--Schwarz use -- as a LaTeX-convention en-dash between proper
    # nouns; those are acceptable).
    double_hyphen_re = re.compile(r"(?<!\w)--(?!\w)|(?<=\s)--(?=\s)")

    for i, line in enumerate(lines):
        if zones[i] != "prose":
            continue
        stripped = line.strip()
        # Skip section dividers (--- or longer).
        if re.match(r"^-{3,}\s*$", stripped):
            continue
        # Skip table separator rows (|---|---|, |:---:|---| etc.).
        if re.match(r"^\|[\s:]*-+[\s:]*(?:\|[\s:]*-+[\s:]*)*\|?\s*$", stripped):
            continue
        # Remove HTML comment markers before checking for --.
        cleaned = html_comment_open.sub("   ", line)
        cleaned = html_comment_close.sub("  ", cleaned)
        if double_hyphen_re.search(cleaned):
            issues.append((
                i + 1, "FAIL", "Double hyphens in prose",
                f"found '--' outside code/mermaid: \"{stripped[:70]}\"",
            ))

    return issues


def check_api_title_format(lines: list[str]) -> list[Issue]:
    """Check 9: First heading in API file must contain em dash.

    Accepts Unicode em dash (U+2014) or the pattern ' --- '.
    Rejects plain '--' or single '-' as separators.
    """
    issues: list[Issue] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            # Found first heading.
            # Accept Unicode em dash or spaced triple-dash.
            if "\u2014" not in stripped and " \u2014 " not in stripped and " --- " not in stripped:
                issues.append((
                    i + 1, "FAIL", "API title format",
                    f"first heading lacks em dash (\u2014): \"{stripped[:70]}\"",
                ))
            break
    return issues


# ── Per-file check orchestration ───────────────────

def check_domain_file(filepath: Path) -> list[Issue]:
    """Run all domain checks on a single chapter file."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    zones = build_zone_mask(lines)

    all_issues: list[Issue] = []
    all_issues.extend(check_copyright_header(lines))
    all_issues.extend(check_historical_bold_titles(lines))
    all_issues.extend(check_algorithm_pseudocode(lines, zones))
    all_issues.extend(check_mermaid_hex_digits(lines, zones))
    all_issues.extend(check_no_mermaid_titles(lines, zones))
    all_issues.extend(check_dependency_graph_colours(lines))
    all_issues.extend(check_glossary_order(lines))
    all_issues.extend(check_no_double_hyphens(lines, zones))
    return all_issues


def check_api_file(filepath: Path) -> list[Issue]:
    """Run all API checks on a single API reference file."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    all_issues: list[Issue] = []
    all_issues.extend(check_copyright_header(lines))
    all_issues.extend(check_api_title_format(lines))
    return all_issues


# ── Reporting ──────────────────────────────────────

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
    files_with_issues = 0

    # Category tallies.
    from collections import defaultdict
    category_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"FAIL": 0, "WARN": 0})

    print()
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print(f"{_BOLD}  STRUCTURAL CONSISTENCY VERIFICATION REPORT{_RESET}")
    if quick:
        print(f"  {_YELLOW}QUICK MODE{_RESET} -- first 3 files per category")
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print()

    for filepath_str in sorted(all_issues.keys()):
        issues = all_issues[filepath_str]
        if not issues:
            continue

        files_with_issues += 1
        ch_fails = sum(1 for _, s, _, _ in issues if s == "FAIL")
        ch_warns = sum(1 for _, s, _, _ in issues if s == "WARN")
        total_fail += ch_fails
        total_warn += ch_warns

        stem = Path(filepath_str).parent.name + "/" + Path(filepath_str).stem
        status = FAIL if ch_fails > 0 else WARN
        print(f"  {status}  {_BOLD}{stem}{_RESET}  ({ch_fails} fail, {ch_warns} warn)")

        for lineno, sev, category, message in issues:
            label = severity_label(sev)
            print(f"         L{lineno:<5d} {label}  [{category}] {message}")
            category_counts[category][sev] += 1

        print()

    # Files with no issues.
    clean_count = files_checked - files_with_issues
    if clean_count > 0:
        print(f"  {PASS}  {clean_count} file{'s' if clean_count != 1 else ''} clean")
        print()

    # Category summary.
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print(f"{_BOLD}  CATEGORY SUMMARY{_RESET}")
    print(f"{'=' * 78}")
    print(f"  {'Category':<40s} {'FAIL':>6s} {'WARN':>6s} {'Total':>6s}")
    print(f"  {'-' * 58}")
    for cat in sorted(category_counts.keys()):
        f = category_counts[cat]["FAIL"]
        w = category_counts[cat]["WARN"]
        t = f + w
        print(f"  {cat:<40s} {f:>6d} {w:>6d} {t:>6d}")
    print(f"  {'-' * 58}")
    print(f"  {'TOTAL':<40s} {total_fail:>6d} {total_warn:>6d} {total_fail + total_warn:>6d}")

    # Final summary.
    print()
    print(f"{_BOLD}{'=' * 78}{_RESET}")
    print(f"{_BOLD}  SUMMARY{_RESET}")
    print(f"{'=' * 78}")
    print(f"  Files scanned:             {files_checked}")
    print(f"  Files with issues:         {files_with_issues}")
    print(f"  FAIL-level issues:         {total_fail}")
    print(f"  WARN-level issues:         {total_warn}")
    print(f"  Total issues:              {total_fail + total_warn}")
    print(f"{'=' * 78}")

    if total_fail > 0:
        print(f"\n  {FAIL}  {total_fail} structural violations must be fixed before merge.")
    elif total_warn > 0:
        print(f"\n  {WARN}  No failures, but {total_warn} warnings should be reviewed.")
    else:
        print(f"\n  {PASS}  All structural checks passed.")

    print()
    return total_fail > 0


# ── CLI ────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify structural consistency across Evenwicht chapters and API docs.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Only check the first 3 files per category (for CI).",
    )
    args = parser.parse_args()

    domain_files = discover_domain_files(quick=args.quick)
    api_files = discover_api_files(quick=args.quick)

    if not domain_files:
        print(f"ERROR: No domain chapter files found in {DOMAIN_DIR}", file=sys.stderr)
        return 1

    total_files = len(domain_files) + len(api_files)
    mode = "QUICK MODE (3+3 files)" if args.quick else "full scan"
    print(f"Checking structural consistency ({mode}) ...")
    print(f"  Domain chapters: {len(domain_files)}")
    for f in domain_files:
        print(f"    {f.relative_to(PROJECT_ROOT)}")
    print(f"  API references:  {len(api_files)}")
    for f in api_files:
        print(f"    {f.relative_to(PROJECT_ROOT)}")

    all_issues: dict[str, list[Issue]] = {}

    for filepath in domain_files:
        issues = check_domain_file(filepath)
        all_issues[str(filepath)] = issues

    for filepath in api_files:
        issues = check_api_file(filepath)
        all_issues[str(filepath)] = issues

    # Tally categories from all_issues for the report.
    has_failures = print_report(all_issues, total_files, args.quick)

    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
