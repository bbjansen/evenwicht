#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify that every person+year claim in Historical Context has a matching Reference.

Checks:
  1. Extracts (person, year) pairs from Section 1 (Historical Context) prose
  2. Extracts (person, year) pairs from mermaid timeline diagrams
  3. Extracts author surnames and years from Section 11 (References)
  4. Cross-matches: every historical claim should have a reference entry
     containing the same surname and year (+-2)

Usage: python3 scripts/verify-historical-coverage.py [--quick]
  --quick: identical behaviour (no network calls in this script), accepted
           for consistency with other verify-* scripts
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

QUICK_MODE = "--quick" in sys.argv

# Year tolerance: a reference within +-YEAR_TOLERANCE of the claimed year counts
# as a match. Covers cases like "published in 1823" vs. reference dated 1821.
YEAR_TOLERANCE = 2


# ── Non-person filter ─────────────────────────
# Words that look like capitalised names but are not people. Checked in
# lowercase. This list is intentionally broad to minimise false positives.

NOT_PERSON_NAMES: set[str] = {
    # English words capitalised at sentence starts / after bold markers
    "the", "this", "that", "these", "those", "his", "her", "its",
    "but", "and", "for", "with", "from", "into", "under", "over",
    "each", "every", "only", "first", "second", "third", "when",
    "where", "while", "after", "before", "between", "during",
    "although", "however", "many", "most", "some", "such", "both",
    "more", "other", "what", "how", "why", "who", "which", "all",
    "not", "nor", "yet", "still", "also", "just", "than", "then",
    # Document structure
    "chapter", "section", "figure", "table", "part", "volume",
    "definition", "theorem", "lemma", "proof", "example", "remark",
    "algorithm", "equation", "formula", "note", "property",
    "corollary", "proposition", "axiom", "notation", "convention",
    # Generic adjectives / adverbs capitalised at sentence starts
    "modern", "applied", "classical", "today", "early", "late",
    "new", "old", "general", "special", "standard", "original",
    "mathematical", "numerical", "computational", "theoretical",
    "practical", "systematic", "formal", "fundamental", "basic",
    # Domain nouns that appear capitalised near years
    "theory", "method", "analysis", "system", "systems", "science",
    "sciences", "functions", "function", "area", "areas", "algebra",
    "calculus", "geometry", "mechanics", "physics", "chemistry",
    "biology", "engineering", "mathematics", "statistics", "model",
    "models", "problem", "problems", "equation", "equations",
    "formula", "formulas", "distribution", "distributions",
    "probability", "variable", "variables", "process", "processes",
    "signal", "signals", "circuit", "circuits", "network", "networks",
    "graph", "graphs", "matrix", "matrices", "vector", "vectors",
    "energy", "power", "force", "field", "fields", "wave", "waves",
    "frequency", "amplitude", "space", "time", "measure", "measures",
    "value", "values", "number", "numbers", "set", "sets",
    "order", "degree", "dimension", "class", "type", "kind",
    "computing", "computation", "programme", "program", "code",
    "data", "information", "knowledge", "logic", "language",
    "structure", "structures", "operation", "operations",
    "optimisation", "optimization", "approximation", "convergence",
    "stability", "equilibrium", "dynamics", "kinetics", "evolution",
    "control", "design", "construction", "development",
    "measurement", "observation", "experiment", "test", "trial",
    "processing", "regression", "inference", "estimation",
    "sampling", "interpolation", "extrapolation",
    # Place names / institutions
    "london", "paris", "berlin", "cambridge", "oxford", "princeton",
    "harvard", "yale", "mit", "stanford", "moscow", "petersburg",
    "vienna", "zurich", "edinburgh", "dublin", "rome", "tokyo",
    "hanover", "woolsthorpe", "brno", "florence",
    "geneva", "columbia", "cornell", "chicago", "manchester",
    "heidelberg", "copenhagen", "continental", "continent", "england",
    "france", "germany", "italy", "japan", "india", "china", "soviet",
    "union", "europe", "america", "britain", "west", "east",
    "rothamsted", "guinness",
    # Organisations / institutions
    "university", "college", "institute", "academy", "society",
    "laboratory", "laboratories", "observatory", "museum",
    "commission", "committee", "council", "bureau", "department",
    # Publication / journal words
    "acta", "annals", "journal", "proceedings", "transactions",
    "bulletin", "letters", "review", "reviews", "reports",
    "memoirs", "notices", "communications", "monthly", "magazine",
    # Latin / non-English title words commonly appearing before years
    "nova", "methodus", "introductio", "analysin", "infinitorum",
    "principia", "mathematica", "mechanica", "theoria", "theoriae",
    "dissertatio", "analytica", "algebraica", "geometria",
    "hydrodynamica", "ausdehnungslehre", "grundlagen", "vorlesungen",
    "lehrbuch", "abhandlungen", "annalen", "zeitschrift",
    "sitzungsberichte", "philosophiae", "naturalis", "celestium",
    "coelestium", "mundi",
    # French title words
    "cours", "analyse", "résumé", "recherches", "essai",
    "théorie", "mémoire", "éléments", "traité",
    # Proper nouns that are not people
    "internet", "wikipedia", "bitcoin", "ethereum", "sputnik",
    "apollo", "mars", "jupiter", "ceres", "earth", "mercury",
    "venus", "saturn", "neptune", "pluto",
    "ieee", "nist", "nasa", "arpa", "darpa", "cern",
    "matlab", "macsyma", "mathematica", "sympy", "wolfram",
    "fortran", "lisp", "python", "java",
    "explorer", "voyager", "pioneer", "viking",
    "motorola", "instruments", "unimate", "unimation", "keccak",
    "boston", "digital",
    # Other false-positive triggers seen in testing
    "introduction", "coordinate", "hessian", "eigenwert",
    "instantaneous", "necessary", "connecting", "introduces",
    "published", "invented", "discovered", "derived", "proposed",
    "developed", "formulated", "defined", "established", "founded",
    "created", "proved", "showed", "demonstrated", "presented",
    "extended", "generalised", "generalized", "refined", "improved",
    "completed", "eliminates", "connects", "systematic",
    "dot", "extension", "rank", "delta", "arm", "change",
    "prize", "bang", "human", "project", "cryptography",
    "geology", "cosmology", "robotics", "acoustics",
    "expressions", "gamma", "chance", "chances", "analyst",
    "minimam", "summa", "basel", "kette", "conjectandi", "aleae",
    "timeline", "milestone", "milestones", "key", "historical",
    "context", "title", "description", "accelerating",
    "fluxions", "fluxionum", "summary",
    # Bold-heading topic words that appear in "**Topic (YYYY).**" patterns
    "government", "twentieth", "least", "backpropagation", "regularisation",
    "regularization", "coding", "state", "predator", "random", "small",
    "heat", "radioactivity", "nuclear", "elliptic", "harmonic",
    "unit", "squares", "advances", "foundations", "revival",
    # Organisations / brands / places appearing in timelines
    "bank", "technologies", "renaissance", "labs", "sorbonne",
    "economics", "erd", "pinocchio", "atlas", "genome", "age",
    "sound", "surgical", "curve", "exploratory", "convex",
    "loa", "mauna", "vinci",
}


# ── Regex building blocks ─────────────────────

# A capitalised word of 3+ chars that might be a surname.
# Uses Unicode categories to handle accented chars like ő (Erdős), ş, ą, etc.
_NAME_TOKEN = r"[A-ZÀ-Ý\u0100-\u017E][a-zà-ÿ\u0100-\u017E]{2,}(?:['']\w+)?"

# Optional compound prefix: von, de, van, etc.
_OPT_PREFIX = r"(?:(?:von|de|van|du|al|la|di|le|el|ibn)[- ])?"

# Optional first name(s) / initial(s) before the surname
_FIRST_NAMES = r"(?:(?:[A-Z][a-zà-ÿ]+|[A-Z]\.)\s+)*"

# A full personal name: first names + compound surname
_FULL_NAME = _FIRST_NAMES + _OPT_PREFIX + r"(" + _NAME_TOKEN + r")"


# ── Section extraction ─────────────────────────

def extract_between_headings(text: str, start_heading: str) -> str:
    """Extract text between a ## heading matching start_heading and the next ## or EOF."""
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^##\s+(?:\d+\.\s*)?{re.escape(start_heading)}\s*$", line):
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^## ", lines[i]):
            end = i
            break
    return "\n".join(lines[start:end])


# ── Name helpers ───────────────────────────────

def _clean_surname(full_match: str, surname_group: str) -> str:
    """Extract the clean surname from a regex match, handling compound prefixes."""
    surname = re.sub(r"[''']s$", "", surname_group)  # strip possessive
    prefix_m = re.match(
        r"(?:.*\s)?((?:von|de|van|du|al|la|di|le|el|ibn)[- ])",
        full_match, re.IGNORECASE,
    )
    if prefix_m:
        surname = prefix_m.group(1) + surname
    return surname


def _is_person_name(word: str) -> bool:
    """Conservative check: is this word plausibly a person's surname?"""
    w = word.lower()
    # Strip compound prefix for the NOT_PERSON_NAMES check
    for pfx in ("von ", "de ", "van ", "du ", "al-", "la ", "di ", "le ", "el ", "ibn "):
        if w.startswith(pfx):
            w = w[len(pfx):]
            break
    return w not in NOT_PERSON_NAMES and len(w) >= 3


# ── Prose extraction ──────────────────────────

def extract_person_year_pairs(text: str) -> list[tuple[str, int]]:
    """Extract (surname, year) pairs from Historical Context prose.

    Uses targeted patterns anchored on name+year co-occurrence rather than
    a generic "find nearest capitalised word to any year" strategy.  This
    approach is conservative: it may miss some claims, but it has a low
    false-positive rate.

    Patterns (applied independently; results are deduplicated):
      P1  Name (YYYY)            — Euler (1734)
      P1b Name (YYYY-YYYY)       — Newton (1665-1666)
      P2  Name's *Title* (YYYY)  — Cauchy's *Cours d'analyse* (1821)
      P3  Name in YYYY           — Euler in 1748
      P4  Name VERB ... in YYYY  — Gauss published in 1809 (up to 120 chars)
      P5  Name's *Title* ... YYYY — possessive + title then year in same clause
      P6  **Name ... (YYYY).**   — bold heading pattern
    """
    pairs: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()

    def _add(full_match_str: str, surname_group: str, year_str: str) -> None:
        surname = _clean_surname(full_match_str, surname_group)
        year = int(year_str)
        if _is_person_name(surname):
            key = (surname.lower(), year)
            if key not in seen:
                seen.add(key)
                pairs.append((surname, year))

    yr = r"(1[4-9]\d{2}|20[0-2]\d)"

    # P1: "Name (YYYY)" — with optional possessive / italic title in between
    for m in re.finditer(
        rf"({_FULL_NAME})[''']?s?\s*(?:\*[^*]*\*\s*)?\({yr}\)",
        text,
    ):
        _add(m.group(1), m.group(2), m.group(3))

    # P1b: "Name (YYYY-YYYY)" — year ranges in parentheses
    for m in re.finditer(
        rf"({_FULL_NAME})[''']?s?\s*(?:\*[^*]*\*\s*)?\({yr}[–\-]+{yr}\)",
        text,
    ):
        _add(m.group(1), m.group(2), m.group(3))
        _add(m.group(1), m.group(2), m.group(4))

    # P2: "Name's *Title* (YYYY)"
    for m in re.finditer(
        rf"({_FULL_NAME})[''']s\s+\*[^*]+\*\s*\({yr}\)",
        text,
    ):
        _add(m.group(1), m.group(2), m.group(3))

    # P3: "Name in YYYY" / "Name, in YYYY"
    for m in re.finditer(
        rf"({_FULL_NAME})[''']?s?,?\s+in\s+{yr}\b",
        text,
    ):
        _add(m.group(1), m.group(2), m.group(3))

    # P4: "Name VERB ... in/of YYYY" within ~120 chars
    _VERBS = (
        r"(?:published|introduced|derived|proposed|developed|formulated|"
        r"defined|established|founded|created|proved|showed|demonstrated|"
        r"presented|extended|generali[sz]ed|refined|improved|completed|"
        r"discovered|invented|popularised|popularized|devised|conceived|"
        r"applied|circulated|constructed|computed|investigated|"
        r"hypothesi[sz]ed|postulated|supplied|obtained|described|treated|"
        r"assumed|wrote|used|named|formalised|formalized|initiated|"
        r"adopted|coined|worked|sought|built|noted|observed|began|"
        r"measured|patented|tabulated|classified|recorded|solved|"
        r"calculated|predicted|collected|documented|reported|verified)"
    )
    for m in re.finditer(
        rf"({_FULL_NAME})\s+{_VERBS}.{{0,120}}?\bin\s+{yr}\b",
        text, re.DOTALL,
    ):
        _add(m.group(1), m.group(2), m.group(3))

    # P5: "Name's *Title* ... YYYY" in same clause (no sentence break)
    for m in re.finditer(
        rf"({_FULL_NAME})[''']s\s+\*[^*]+\*[^.{{}}]*?{yr}",
        text,
    ):
        _add(m.group(1), m.group(2), m.group(3))

    # P6: Bold heading "**Name ... (YYYY).**"
    for m in re.finditer(
        rf"\*\*({_FULL_NAME}).{{0,80}}?\({yr}(?:[–\-]\d{{4}})?\)",
        text,
    ):
        _add(m.group(1), m.group(2), m.group(3))

    return pairs


# ── Timeline extraction ───────────────────────

def extract_timeline_claims(text: str) -> list[tuple[str, int]]:
    """Extract (person, year) pairs from mermaid timeline blocks.

    Only extracts entries where the description starts with a recognisable
    person name (passing the _is_person_name filter).
    """
    pairs: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()

    for block_match in re.finditer(r"```mermaid\s*\n(.*?)```", text, re.DOTALL):
        block = block_match.group(1)
        if "timeline" not in block.lower():
            continue

        for line_match in re.finditer(r"^\s+(\d{4})\s*:\s*(.+)$", block, re.MULTILINE):
            year = int(line_match.group(1))
            description = line_match.group(2).strip()

            # Timeline entries use two formats:
            #   a) "Name–Name – Description" (separator present)
            #   b) "Name introduces/publishes/discovers ..." (no separator)
            # For (a), extract all names before the separator.
            # For (b), extract only leading names before the first verb/preposition.
            separator_idx = description.find(" – ")
            if separator_idx < 0:
                separator_idx = description.find(" — ")

            if separator_idx > 0:
                name_part = description[:separator_idx]
            else:
                # No separator: take text up to the first lowercase word
                # that is not a compound prefix. This stops before verbs
                # like "introduces", "publishes", "discovers", etc.
                stop_m = re.search(
                    r"\s+(?!(?:von|de|van|du|al|la|di|le|el|ibn)\b)[a-z]",
                    description,
                )
                name_part = description[:stop_m.start()] if stop_m else description[:40]

            # Extract all name tokens from the name part
            name_pat = re.compile(
                rf"(?:(?:von|de|van|du|al|la|di|le|el|ibn)[- ])?({_NAME_TOKEN})"
            )
            for name_m in name_pat.finditer(name_part):
                surname = name_m.group(1)
                # Strip possessive
                surname = re.sub(r"[''']s$", "", surname)
                full = name_m.group(0).strip()
                prefix_m = re.match(
                    r"((?:von|de|van|du|al|la|di|le|el|ibn)[- ])",
                    full, re.IGNORECASE,
                )
                if prefix_m:
                    surname = prefix_m.group(1) + surname

                if not _is_person_name(surname):
                    continue

                key = (surname.lower(), year)
                if key not in seen:
                    seen.add(key)
                    pairs.append((surname, year))

    return pairs


# ── Reference extraction ──────────────────────

def extract_reference_entries(text: str) -> list[tuple[set[str], set[int]]]:
    """Extract (surnames, years) from each reference entry in the References section.

    Returns a list of (surname_set, year_set) tuples, one per reference entry.
    """
    refs_text = extract_between_headings(text, "References")
    if not refs_text:
        return []

    entries: list[tuple[set[str], set[int]]] = []

    for line in refs_text.splitlines():
        ref_match = re.match(r"^(?:- )?\[(\d+)\]\s+(.+)$", line)
        if not ref_match:
            continue

        ref_text = ref_match.group(2)

        # Extract years
        years: set[int] = set()
        for ym in re.finditer(r"\b(1[4-9]\d{2}|20[0-2]\d)\b", ref_text):
            years.add(int(ym.group(1)))

        # Extract author surnames from the author portion (before the title)
        surnames: set[str] = set()

        author_end = re.search(r"\*[^*]+\*|\"[^\"]+\"", ref_text)
        author_portion = ref_text[:author_end.start()] if author_end else ref_text[:80]

        surname_pat = re.compile(
            r"(?:(?:von|de|van|du|al|la|di|le|el|ibn)[- ])?"
            r"([A-ZÀ-Ý][a-zà-ÿ]+(?:['']\w+)?)"
        )

        for sm in surname_pat.finditer(author_portion):
            name = sm.group(1)
            if len(name) <= 2:
                continue
            full = sm.group(0).strip()
            prefix_m = re.match(
                r"((?:von|de|van|du|al|la|di|le|el|ibn)[- ])",
                full, re.IGNORECASE,
            )
            if prefix_m:
                name = prefix_m.group(1) + name
            surnames.add(name.lower())

        # Also index the raw first comma-delimited token
        first_word = ref_text.split(",")[0].strip() if "," in ref_text else ""
        if first_word and first_word[0:1].isupper():
            surnames.add(first_word.lower())

        entries.append((surnames, years))

    return entries


# ── Matching ──────────────────────────────────

def find_reference_match(
    surname: str,
    year: int,
    ref_entries: list[tuple[set[str], set[int]]],
) -> bool:
    """Check if any reference entry contains a matching surname and year (+-tolerance)."""
    surname_lower = surname.lower()

    for ref_surnames, ref_years in ref_entries:
        surname_matched = False
        for rs in ref_surnames:
            if surname_lower == rs:
                surname_matched = True
                break
            if surname_lower in rs or rs in surname_lower:
                surname_matched = True
                break
        if not surname_matched:
            continue

        for ry in ref_years:
            if abs(year - ry) <= YEAR_TOLERANCE:
                return True

    return False


# ── Per-chapter processing ────────────────────

def process_chapter(filepath: Path) -> tuple[list[tuple[str, int, str]], int]:
    """Process a single chapter.

    Returns (gaps, total_claims) where gaps is a list of (surname, year, source).
    """
    text = filepath.read_text(encoding="utf-8")

    hist_text = extract_between_headings(text, "Historical Context")
    if not hist_text:
        return [], 0

    ref_entries = extract_reference_entries(text)

    prose_claims = extract_person_year_pairs(hist_text)
    timeline_claims = extract_timeline_claims(hist_text)

    # Deduplicate across sources
    all_claims: dict[tuple[str, int], str] = {}
    for surname, year in prose_claims:
        key = (surname.lower(), year)
        if key not in all_claims:
            all_claims[key] = "prose"

    for surname, year in timeline_claims:
        key = (surname.lower(), year)
        if key not in all_claims:
            all_claims[key] = "timeline"
        elif all_claims[key] == "prose":
            all_claims[key] = "prose+timeline"

    total_claims = len(all_claims)

    # Cross-match
    gaps: list[tuple[str, int, str]] = []
    for (surname_lower, year), source in sorted(
        all_claims.items(), key=lambda x: (x[0][1], x[0][0])
    ):
        # Reconstruct display name with original capitalisation
        display_name = surname_lower
        for s, _ in prose_claims + timeline_claims:
            if s.lower() == surname_lower:
                display_name = s
                break

        if not find_reference_match(display_name, year, ref_entries):
            gaps.append((display_name, year, source))

    return gaps, total_claims


# ── Main ──────────────────────────────────────

def main() -> int:
    chapter_files = sorted(DOCS_DIR.glob("[0-9]*.md"))
    if not chapter_files:
        print(f"ERROR: No chapter files found in {DOCS_DIR}")
        return 1

    print("=" * 72)
    print("Evenwicht Historical Coverage Verification")
    print("=" * 72)
    print()
    print(f"Scanning {len(chapter_files)} chapters...")
    print(f"Year tolerance: +-{YEAR_TOLERANCE}")
    if QUICK_MODE:
        print("Mode: --quick (no network calls; same behaviour for this script)")
    print()

    total_gaps = 0
    total_claims = 0
    chapters_with_gaps = 0

    for filepath in chapter_files:
        ch_name = filepath.stem
        ch_num_match = re.match(r"(\d+)", ch_name)
        ch_num = int(ch_num_match.group(1)) if ch_num_match else 0

        gaps, ch_claims = process_chapter(filepath)
        total_claims += ch_claims

        if gaps:
            chapters_with_gaps += 1
            print(f"  Ch {ch_num:02d} ({ch_name})")
            for surname, year, source in gaps:
                print(f"    GAP: {surname} ({year}) [{source}]")
            total_gaps += len(gaps)
            print()

    # Summary
    print("=" * 72)
    print(f"Chapters scanned:          {len(chapter_files)}")
    print(f"Total person+year claims:  {total_claims}")
    print(f"Unmatched gaps:            {total_gaps}")
    print(f"Chapters with gaps:        {chapters_with_gaps}")
    print("=" * 72)

    if total_gaps > 0:
        print(f"\nFAILED: {total_gaps} historical claims lack reference coverage.")
        return 1

    print("\nAll historical claims have matching references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
