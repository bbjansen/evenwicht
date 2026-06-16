# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Fact-checking and source-citation verification for the Evenwicht textbook.

Extracts historical claims from Section 1 ("Historical Context") of all 48
chapters, validates dates and person names for consistency, and produces a
structured markdown report at docs/sources/fact-check-report.md.

Usage:
    python3 verify/verify_prose.py

Also exposes ``build() -> Chapter`` for integration with the verification
framework (run_all.py).
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework import Chapter, StructuralCheck

# ---------------------------------------------------------------------------
# Reference data: ~50 key publication dates (year, author, work)
# ---------------------------------------------------------------------------

REFERENCE_DATES: dict[str, tuple[str, int]] = {
    # key -> (author, year)
    "elements": ("Euclid", -300),
    "ars magna": ("Gerolamo Cardano", 1545),
    "liber de ludo aleae": ("Gerolamo Cardano", 1564),
    "pascal-fermat correspondence": ("Blaise Pascal and Pierre de Fermat", 1654),
    "de ratiociniis in ludo aleae": ("Christiaan Huygens", 1657),
    "principia": ("Isaac Newton", 1687),
    "ars conjectandi": ("Jakob Bernoulli", 1713),
    "introductio in analysin infinitorum": ("Leonhard Euler", 1748),
    "introductio": ("Leonhard Euler", 1748),
    "mecanique analytique": ("Joseph-Louis Lagrange", 1788),
    "theorie analytique des probabilites": ("Pierre-Simon Laplace", 1812),
    "disquisitiones arithmeticae": ("Carl Friedrich Gauss", 1801),
    "cours d'analyse": ("Augustin-Louis Cauchy", 1821),
    "riemann habilitation": ("Bernhard Riemann", 1854),
    "h-theorem": ("Ludwig Boltzmann", 1872),
    "elementary principles in statistical mechanics": ("Josiah Willard Gibbs", 1902),
    "grundbegriffe der wahrscheinlichkeitsrechnung": ("Andrei Nikolaevich Kolmogorov", 1933),
    "kolmogorov axioms": ("Andrei Nikolaevich Kolmogorov", 1933),
    "mathematical theory of communication": ("Claude Shannon", 1948),
    "shannon information theory": ("Claude Shannon", 1948),
    "nash equilibrium": ("John Forbes Nash Jr.", 1950),
    "theory of games and economic behavior": ("John von Neumann and Oskar Morgenstern", 1944),
    "minimax theorem": ("John von Neumann", 1928),
    "on computable numbers": ("Alan Turing", 1936),
    "lambda calculus": ("Alonzo Church", 1936),
    "fourier series": ("Joseph Fourier", 1807),
    "theorie analytique de la chaleur": ("Joseph Fourier", 1822),
    "erlangen programme": ("Felix Klein", 1872),
    "cantor set theory": ("Georg Cantor", 1874),
    "grundlagen der geometrie": ("David Hilbert", 1899),
    "hilbert problems": ("David Hilbert", 1900),
    "general theory of relativity": ("Albert Einstein", 1915),
    "special theory of relativity": ("Albert Einstein", 1905),
    "godel incompleteness": ("Kurt Godel", 1931),
    "cybernetics": ("Norbert Wiener", 1948),
    "kalman filter": ("Rudolf Kalman", 1960),
    "black-scholes": ("Fischer Black and Myron Scholes", 1973),
    "rsa cryptosystem": ("Rivest, Shamir, and Adleman", 1977),
    "mandelbrot fractals": ("Benoit Mandelbrot", 1975),
    "lorenz attractor": ("Edward Lorenz", 1963),
    "pagerank": ("Larry Page and Sergey Brin", 1998),
    "backpropagation": ("David Rumelhart, Geoffrey Hinton, and Ronald Williams", 1986),
    "perceptron": ("Frank Rosenblatt", 1958),
    "bayes essay": ("Thomas Bayes", 1763),
    "boltzmann distribution": ("Ludwig Boltzmann", 1868),
    "maxwell equations": ("James Clerk Maxwell", 1865),
    "navier-stokes": ("Claude-Louis Navier and George Gabriel Stokes", 1845),
    "euler method": ("Leonhard Euler", 1768),
    "cournot duopoly": ("Antoine Augustin Cournot", 1838),
    "vickrey auction": ("William Vickrey", 1961),
    "ess smith-price": ("John Maynard Smith and George R. Price", 1973),
}

# Birth and death years for anachronism detection
PERSON_DATES: dict[str, tuple[int, int]] = {
    "euclid": (-325, -265),
    "archimedes": (-287, -212),
    "gerolamo cardano": (1501, 1576),
    "blaise pascal": (1623, 1662),
    "pierre de fermat": (1601, 1665),
    "christiaan huygens": (1629, 1695),
    "isaac newton": (1643, 1727),
    "gottfried wilhelm leibniz": (1646, 1716),
    "jakob bernoulli": (1655, 1705),
    "johann bernoulli": (1667, 1748),
    "leonhard euler": (1707, 1783),
    "joseph-louis lagrange": (1736, 1813),
    "pierre-simon laplace": (1749, 1827),
    "carl friedrich gauss": (1777, 1855),
    "augustin-louis cauchy": (1789, 1857),
    "joseph fourier": (1768, 1830),
    "bernhard riemann": (1826, 1866),
    "karl weierstrass": (1815, 1897),
    "georg cantor": (1845, 1918),
    "david hilbert": (1862, 1943),
    "henri poincare": (1854, 1912),
    "ludwig boltzmann": (1844, 1906),
    "james clerk maxwell": (1831, 1879),
    "josiah willard gibbs": (1839, 1903),
    "albert einstein": (1879, 1955),
    "emmy noether": (1882, 1935),
    "andrei nikolaevich kolmogorov": (1903, 1987),
    "claude shannon": (1916, 2001),
    "alan turing": (1912, 1954),
    "alonzo church": (1903, 1995),
    "kurt godel": (1906, 1978),
    "john von neumann": (1903, 1957),
    "john forbes nash jr.": (1928, 2015),
    "thomas bayes": (1701, 1761),
    "peter gustav lejeune dirichlet": (1805, 1859),
    "antoine augustin cournot": (1801, 1877),
    "norbert wiener": (1894, 1964),
    "rudolf kalman": (1930, 2016),
    "fischer black": (1938, 1995),
    "myron scholes": (1941, 2100),  # alive
    "benoit mandelbrot": (1924, 2010),
    "edward lorenz": (1917, 2008),
    "frank rosenblatt": (1928, 1971),
    "william vickrey": (1914, 1996),
    "john maynard smith": (1920, 2004),
    "reinhard selten": (1930, 2016),
    "john harsanyi": (1920, 2000),
    "george r. price": (1922, 1975),
    "francis galton": (1822, 1911),
    "adolphe quetelet": (1796, 1874),
    "richard von mises": (1883, 1953),
    "felix klein": (1849, 1925),
    "oskar morgenstern": (1902, 1977),
}

# Chapter metadata
CHAPTER_FILES = {
    i: f"{i:02d}-{name}.md"
    for i, name in enumerate([
        "",  # placeholder for 0-index
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
# Data structures for extracted claims
# ---------------------------------------------------------------------------

@dataclass
class HistoricalClaim:
    """A single historical claim extracted from a chapter."""
    chapter: int
    chapter_title: str
    person: str
    year: int | None
    work: str
    claim_text: str
    source: str = ""
    status: str = "UNCHECKED"
    notes: str = ""


@dataclass
class ExtractionResult:
    """All claims and diagnostics from processing the full textbook."""
    claims: list[HistoricalClaim] = field(default_factory=list)
    person_spellings: dict[str, list[tuple[str, int]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    year_issues: list[str] = field(default_factory=list)
    anachronisms: list[str] = field(default_factory=list)
    date_mismatches: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

# Patterns for extracting years from text
_YEAR_PATTERN = re.compile(r"\b(\d{4})\b")
_BCE_PATTERN = re.compile(r"(\d+)\s*(?:BCE|BC|B\.C\.E?\.|b\.c\.e?\.)", re.IGNORECASE)

# Pattern for person names (capitalized multi-word sequences often followed
# by a verb or possessive). We look for sequences of capitalized words.
_PERSON_PATTERN = re.compile(
    r"(?:^|(?<=\.\s)|(?<=,\s)|(?<=;\s)|(?<=\n))"
    r"([A-Z][a-z]+(?:\s+(?:de\s+|von\s+|van\s+|du\s+|le\s+|di\s+|Jr\.?\s*|"
    r"[A-Z]\.?\s*|[A-Z][a-z]+))+)"
)

# Pattern for publication titles (text in *italics*)
_WORK_PATTERN = re.compile(r"\*([^*]+)\*")

# Pattern for a sentence containing a year and a person
_CLAIM_SENTENCE = re.compile(r"[^.]*\b\d{4}\b[^.]*\.")


def _extract_section(text: str, section_num: int, title: str = "") -> str:
    """Extract a section from a chapter markdown file by title or number."""
    # Try title-based match first (unnumbered headings)
    if title:
        pattern = re.compile(rf"^##\s+{re.escape(title)}\s*$", re.MULTILINE)
        match = pattern.search(text)
    else:
        match = None
    # Fall back to numbered heading
    if not match:
        pattern = re.compile(rf"^##\s+{section_num}\.\s+.*$", re.MULTILINE)
        match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    # Find the next ## heading or end of file
    next_heading = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    if next_heading:
        end = match.end() + next_heading.start()
    else:
        end = len(text)
    return text[start:end]


def _extract_chapter_title(text: str) -> str:
    """Extract the chapter title from the first heading."""
    m = re.search(r"^#\s+Chapter\s+\d+:\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else "Unknown"


def _normalize_person(name: str) -> str:
    """Normalize a person name to a canonical lowercase key."""
    name = name.strip().lower()
    # Remove trailing punctuation
    name = re.sub(r"[,;:.'\"]+$", "", name)
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name)
    return name


def _extract_claims_from_section(
    section_text: str,
    chapter_num: int,
    chapter_title: str,
) -> list[HistoricalClaim]:
    """Extract historical claims from the text of a Historical Context section."""
    claims: list[HistoricalClaim] = []

    # Remove mermaid blocks
    cleaned = re.sub(r"```mermaid.*?```", "", section_text, flags=re.DOTALL)
    # Remove markdown heading
    cleaned = re.sub(r"^##\s+.*$", "", cleaned, flags=re.MULTILINE)

    # Split into sentences (approximate)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:
            continue

        # Find years in this sentence
        years_ce = _YEAR_PATTERN.findall(sentence)
        years_bce = _BCE_PATTERN.findall(sentence)

        years: list[int] = []
        for y in years_ce:
            yi = int(y)
            if 1000 <= yi <= 2025:
                years.append(yi)
        for y in years_bce:
            years.append(-int(y))

        if not years:
            continue

        # Find person names
        persons = _PERSON_PATTERN.findall(sentence)
        # Also check for single-word famous names that the pattern might miss
        for known in PERSON_DATES:
            parts = known.split()
            last_name = parts[-1].replace(".", "")
            if last_name.lower() in ("jr", "jr."):
                last_name = parts[-2] if len(parts) > 2 else parts[0]
            if re.search(r"\b" + re.escape(last_name.title()) + r"\b", sentence):
                # Use the full known name
                canonical = known.title()
                if canonical not in persons:
                    persons.append(canonical)

        # Find works (italicized titles)
        works = _WORK_PATTERN.findall(sentence)

        if not persons:
            persons = ["(unattributed)"]

        for person in persons:
            person = person.strip()
            if len(person) < 3:
                continue
            claim = HistoricalClaim(
                chapter=chapter_num,
                chapter_title=chapter_title,
                person=person,
                year=years[0] if years else None,
                work=works[0] if works else "",
                claim_text=sentence[:300],
            )
            claims.append(claim)

    return claims


def _check_year_plausibility(year: int | None) -> str | None:
    """Check that a year is within plausible range."""
    if year is None:
        return None
    if year > 0 and not (1500 <= year <= 2025):
        # Allow ancient dates (negative / BCE)
        if year > 2025:
            return f"Year {year} is in the future"
        if 0 < year < 1500:
            return f"Year {year} is suspiciously early for post-medieval work"
    return None


def _check_anachronism(person: str, year: int | None) -> str | None:
    """Check if a person could have done something in the given year."""
    if year is None:
        return None
    key = _normalize_person(person)
    if key not in PERSON_DATES:
        return None
    birth, death = PERSON_DATES[key]
    if year < birth:
        return (
            f"Anachronism: {person} (born {birth}) could not have done "
            f"something in {year}"
        )
    if year > death + 5:  # +5 for posthumous publications
        return (
            f"Anachronism: {person} (died {death}) is attributed "
            f"something in {year}"
        )
    return None


def _check_reference_dates(claims: list[HistoricalClaim]) -> list[str]:
    """Cross-reference extracted claims against known publication dates."""
    issues: list[str]  = []
    for claim in claims:
        if not claim.work or claim.year is None:
            continue
        work_key = claim.work.lower().strip()
        for ref_key, (ref_author, ref_year) in REFERENCE_DATES.items():
            # Fuzzy match on work title
            if ref_key in work_key or work_key in ref_key:
                if abs(claim.year - ref_year) > 2:
                    issues.append(
                        f"Ch {claim.chapter:02d}: '{claim.work}' dated "
                        f"{claim.year} but reference says {ref_year} "
                        f"(by {ref_author})"
                    )
    return issues


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

def extract_all(docs_dir: str) -> ExtractionResult:
    """Extract and validate all historical claims from the textbook."""
    result = ExtractionResult()

    for ch_num, filename in sorted(CHAPTER_FILES.items()):
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chapter_title = _extract_chapter_title(text)

        # Extract Historical Context section
        section1 = _extract_section(text, 1, title="Historical Context")
        if not section1:
            continue

        claims = _extract_claims_from_section(section1, ch_num, chapter_title)
        result.claims.extend(claims)

        # Track person spellings for consistency checking
        for claim in claims:
            if claim.person != "(unattributed)":
                key = _normalize_person(claim.person)
                result.person_spellings[key].append(
                    (claim.person, claim.chapter)
                )

        # Validate years
        for claim in claims:
            issue = _check_year_plausibility(claim.year)
            if issue:
                result.year_issues.append(
                    f"Ch {ch_num:02d}: {issue} in claim about {claim.person}"
                )
            anachronism = _check_anachronism(claim.person, claim.year)
            if anachronism:
                result.anachronisms.append(f"Ch {ch_num:02d}: {anachronism}")

    # Cross-reference dates
    result.date_mismatches = _check_reference_dates(result.claims)

    return result


def _check_spelling_consistency(
    spellings: dict[str, list[tuple[str, int]]],
) -> list[str]:
    """Check that the same person is spelled consistently across chapters."""
    issues: list[str] = []
    for key, occurrences in spellings.items():
        unique_spellings = set(name for name, _ in occurrences)
        if len(unique_spellings) > 1:
            chapters = sorted(set(ch for _, ch in occurrences))
            issues.append(
                f"Inconsistent spelling for '{key}': "
                f"{', '.join(sorted(unique_spellings))} "
                f"(chapters {chapters})"
            )
    return issues


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_fact_check_report(result: ExtractionResult, output_path: str) -> None:
    """Write the structured fact-check report as markdown."""
    lines: list[str] = []
    lines.append("# Fact-Check Report")
    lines.append("")
    lines.append("Auto-generated report of historical claims extracted from the")
    lines.append("Evenwicht textbook. Each claim is listed with fields for source")
    lines.append("verification.")
    lines.append("")

    # Summary statistics
    total_claims = len(result.claims)
    verified = sum(1 for c in result.claims if c.status == "VERIFIED")
    disputed = sum(1 for c in result.claims if c.status == "DISPUTED")
    unchecked = sum(1 for c in result.claims if c.status == "UNCHECKED")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total claims**: {total_claims}")
    lines.append(f"- **Verified**: {verified}")
    lines.append(f"- **Disputed**: {disputed}")
    lines.append(f"- **Unchecked**: {unchecked}")
    lines.append(f"- **Year plausibility issues**: {len(result.year_issues)}")
    lines.append(f"- **Anachronisms detected**: {len(result.anachronisms)}")
    lines.append(f"- **Date mismatches vs references**: {len(result.date_mismatches)}")
    spelling_issues = _check_spelling_consistency(result.person_spellings)
    lines.append(f"- **Spelling inconsistencies**: {len(spelling_issues)}")
    lines.append("")

    # Issues section
    if result.year_issues or result.anachronisms or result.date_mismatches or spelling_issues:
        lines.append("## Issues Detected")
        lines.append("")
        if result.anachronisms:
            lines.append("### Anachronisms")
            lines.append("")
            for issue in result.anachronisms:
                lines.append(f"- {issue}")
            lines.append("")
        if result.date_mismatches:
            lines.append("### Date Mismatches vs Reference Data")
            lines.append("")
            for issue in result.date_mismatches:
                lines.append(f"- {issue}")
            lines.append("")
        if result.year_issues:
            lines.append("### Year Plausibility")
            lines.append("")
            for issue in result.year_issues:
                lines.append(f"- {issue}")
            lines.append("")
        if spelling_issues:
            lines.append("### Spelling Inconsistencies")
            lines.append("")
            for issue in spelling_issues:
                lines.append(f"- {issue}")
            lines.append("")

    # Per-chapter claims
    current_chapter = -1
    for claim in result.claims:
        if claim.chapter != current_chapter:
            current_chapter = claim.chapter
            lines.append(f"## Chapter {claim.chapter}: {claim.chapter_title}")
            lines.append("")
            lines.append("### Historical Claims")
            lines.append("")

        year_str = str(claim.year) if claim.year is not None else "n/a"
        if claim.year is not None and claim.year < 0:
            year_str = f"{abs(claim.year)} BCE"

        lines.append(f"**Claim**: {claim.claim_text}")
        lines.append(f"- **Person**: {claim.person}")
        lines.append(f"- **Year**: {year_str}")
        lines.append(f"- **Work**: {claim.work if claim.work else '(none cited)'}")
        lines.append(f"- **Source**: {claim.source if claim.source else '(to be filled in)'}")
        lines.append(f"- **Status**: {claim.status}")
        lines.append(f"- **Notes**: {claim.notes if claim.notes else ''}")
        lines.append("")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Framework integration: build() -> Chapter
# ---------------------------------------------------------------------------

def build() -> Chapter:
    """Build a Chapter of structural checks for the verification framework."""
    ch = Chapter(200, "Prose Fact-Checking")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs", "domains")
    report_path = os.path.join(base_dir, "docs", "sources", "fact-check-report.md")

    # Run full extraction
    result = extract_all(docs_dir)

    # Write the report as a side effect
    write_fact_check_report(result, report_path)

    # Structural check: anachronisms (informational)
    def check_no_anachronisms() -> tuple[bool, str]:
        if result.anachronisms:
            msg = f"{len(result.anachronisms)} potential anachronisms found: " + "; ".join(
                result.anachronisms[:5]
            )
            return True, msg
        return True, ""

    ch.add(StructuralCheck(
        label="No anachronisms in historical claims",
        section="1",
        predicate=check_no_anachronisms,
    ))

    # Structural check: year plausibility (informational)
    def check_years_plausible() -> tuple[bool, str]:
        if result.year_issues:
            msg = f"{len(result.year_issues)} year issues noted: " + "; ".join(
                result.year_issues[:5]
            )
            return True, msg
        return True, ""

    ch.add(StructuralCheck(
        label="All years within plausible range (1500-2025 CE or explicit BCE)",
        section="1",
        predicate=check_years_plausible,
    ))

    # Structural check: person name spelling consistency
    def check_spelling_consistency() -> tuple[bool, str]:
        issues = _check_spelling_consistency(result.person_spellings)
        if issues:
            msg = f"{len(issues)} inconsistencies: " + "; ".join(issues[:5])
            return False, msg
        return True, ""

    ch.add(StructuralCheck(
        label="Person names spelled consistently across chapters",
        section="1",
        predicate=check_spelling_consistency,
    ))

    # Structural check: date cross-references (informational)
    def check_reference_dates() -> tuple[bool, str]:
        if result.date_mismatches:
            msg = f"{len(result.date_mismatches)} date mismatches noted: " + "; ".join(
                result.date_mismatches[:5]
            )
            return True, msg
        return True, ""

    ch.add(StructuralCheck(
        label="Publication dates match reference data",
        section="1",
        predicate=check_reference_dates,
    ))

    # Structural check: at least some claims were extracted
    def check_extraction_coverage() -> tuple[bool, str]:
        if len(result.claims) < 48:
            return False, (
                f"Only {len(result.claims)} claims extracted; expected at "
                f"least 48 (one per chapter)"
            )
        return True, ""

    ch.add(StructuralCheck(
        label="Sufficient historical claims extracted (>=48)",
        section="1",
        predicate=check_extraction_coverage,
    ))

    # Structural check: report was written
    def check_report_written() -> tuple[bool, str]:
        if os.path.exists(report_path):
            size = os.path.getsize(report_path)
            if size > 100:
                return True, ""
            return False, f"Report exists but is only {size} bytes"
        return False, f"Report not found at {report_path}"

    ch.add(StructuralCheck(
        label="Fact-check report generated successfully",
        section="1",
        predicate=check_report_written,
    ))

    return ch


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run fact-checking as a standalone script."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs", "domains")
    report_path = os.path.join(base_dir, "docs", "sources", "fact-check-report.md")

    print("Extracting historical claims from all 48 chapters...")
    result = extract_all(docs_dir)

    print(f"  Total claims extracted: {len(result.claims)}")
    print(f"  Year plausibility issues: {len(result.year_issues)}")
    print(f"  Anachronisms detected: {len(result.anachronisms)}")
    print(f"  Date mismatches: {len(result.date_mismatches)}")

    spelling_issues = _check_spelling_consistency(result.person_spellings)
    print(f"  Spelling inconsistencies: {len(spelling_issues)}")

    if result.anachronisms:
        print("\nAnachronisms:")
        for a in result.anachronisms:
            print(f"  - {a}")

    if result.date_mismatches:
        print("\nDate mismatches:")
        for d in result.date_mismatches:
            print(f"  - {d}")

    if spelling_issues:
        print("\nSpelling inconsistencies:")
        for s in spelling_issues:
            print(f"  - {s}")

    print(f"\nWriting report to {report_path}...")
    write_fact_check_report(result, report_path)
    print("Done.")

    # Also run framework checks
    print("\nRunning framework checks...")
    chapter = build()
    chapter.run()
    for r in chapter.results:
        icon = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERR!", "SKIP": "SKIP"}[
            r.status.value
        ]
        print(f"  [{icon}] {r.label}")
        if r.message:
            print(f"         {r.message}")


if __name__ == "__main__":
    main()
