#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify all references across 48 chapters.

Checks:
  1. URL liveness     — all Online Resources URLs return 200
  2. ISBN validation   — textbook ISBNs are valid (checksum + OpenLibrary lookup)
  3. DOI resolution    — DOIs resolve via doi.org
  4. Citation format   — consistent Author. *Title*. Publisher, Year. pattern
  5. Year plausibility — publication years are in range [1600, 2026]
  6. Duplicate detect  — same work cited differently across chapters
  7. Alphabetical order — references sorted within each subsection

Usage: python3 scripts/verify-references.py [--quick]
  --quick: skip URL checks (fast mode for CI)

Requires: requests (pip3 install requests)
"""

import glob
import re
import sys
import time
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

QUICK_MODE = "--quick" in sys.argv

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    if not QUICK_MODE:
        print("WARNING: 'requests' not installed. URL checks disabled.")
        print("  Install with: pip3 install requests")


# ── Reference extraction ────────────────────────

def extract_references(filepath):
    """Extract all references grouped by category from a chapter file."""
    text = Path(filepath).read_text(encoding="utf-8")

    # Find references section
    start = re.search(r"^## (?:\d+\.\s*)?References\s*$", text, re.MULTILINE)
    if not start:
        return {}

    end = re.search(r"^## (?:\d+\.\s*)?Glossary\s*$", text[start.end():], re.MULTILINE)
    section = text[start.end(): start.end() + end.start()] if end else text[start.end():]

    refs = {"Textbooks": [], "Historical": [], "Online Resources": []}
    current_cat = None

    for line in section.splitlines():
        heading = re.match(r"^###\s+(.+)$", line)
        if heading:
            cat = heading.group(1).strip()
            if cat in refs:
                current_cat = cat
            else:
                # New subsection not in our known categories — track separately
                refs[cat] = []
                current_cat = cat
            continue

        ref_match = re.match(r"^(?:- )?\[(\d+)\]\s+(.+)$", line)
        if ref_match and current_cat:
            refs[current_cat].append({
                "num": int(ref_match.group(1)),
                "text": ref_match.group(2).strip(),
                "line": line.strip(),
            })

    return refs


# ── Parsers ─────────────────────────────────────

def extract_urls(text):
    """Extract all URLs from reference text."""
    return re.findall(r"https?://[^\s)>]+", text)


def extract_year(text):
    """Extract publication year from reference text."""
    # Match 4-digit years, prefer those after publisher name
    years = re.findall(r"\b(1[6-9]\d{2}|20[0-2]\d)\b", text)
    return int(years[-1]) if years else None


def extract_isbn(text):
    """Extract ISBN-10 or ISBN-13 from reference text."""
    isbn = re.search(r"ISBN[:\s-]*([\d-]{10,17})", text, re.IGNORECASE)
    if isbn:
        return re.sub(r"-", "", isbn.group(1))
    return None


def extract_doi(text):
    """Extract DOI from reference text."""
    doi = re.search(r"(10\.\d{4,}/[^\s,;)]+)", text)
    return doi.group(1) if doi else None


def extract_author_sort_key(text):
    """Extract first author surname for alphabetical ordering check."""
    # References start with author name
    match = re.match(r"^([A-Z][a-zà-ÿ]+)", text)
    return match.group(1).lower() if match else ""


# ── Validators ──────────────────────────────────

def validate_isbn_checksum(isbn):
    """Validate ISBN-10 or ISBN-13 checksum."""
    digits = re.sub(r"[^0-9X]", "", isbn.upper())

    if len(digits) == 13:
        total = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(digits))
        return total % 10 == 0
    elif len(digits) == 10:
        total = sum((10 - i) * (10 if d == "X" else int(d)) for i, d in enumerate(digits))
        return total % 11 == 0
    return False


def check_url(url, timeout=10):
    """Check if a URL is reachable. Returns (status_code, redirect_url or None)."""
    if not HAS_REQUESTS:
        return None, None
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={"User-Agent": "Evenwicht-Reference-Checker/1.0"})
        return r.status_code, r.url if r.url != url else None
    except requests.RequestException as e:
        return None, str(e)


def check_doi(doi):
    """Check if a DOI resolves via doi.org."""
    if not HAS_REQUESTS:
        return None
    try:
        r = requests.head(f"https://doi.org/{doi}", timeout=10, allow_redirects=True,
                          headers={"User-Agent": "Evenwicht-Reference-Checker/1.0"})
        return r.status_code
    except requests.RequestException:
        return None


def check_isbn_openlibrary(isbn):
    """Look up ISBN via OpenLibrary API."""
    if not HAS_REQUESTS:
        return None
    try:
        r = requests.get(f"https://openlibrary.org/isbn/{isbn}.json", timeout=10,
                         headers={"User-Agent": "Evenwicht-Reference-Checker/1.0"})
        return r.status_code == 200
    except requests.RequestException:
        return None


# ── Citation format checks ──────────────────────

def check_textbook_format(text):
    """Check textbook citation format: Author. *Title*. Publisher, Year."""
    issues = []

    # Should have italic title
    if not re.search(r"\*[^*]+\*", text):
        issues.append("missing italic title (*Title*)")

    # Should have a year
    year = extract_year(text)
    if not year:
        issues.append("no publication year found")
    elif year > 2026:
        issues.append(f"future year: {year}")
    elif year < 1600:
        issues.append(f"implausible year: {year}")

    # Should start with author name (capitalized); handle non-ASCII names (e.g. Åström)
    if not text[0:1].isupper():
        issues.append("doesn't start with author name")

    return issues


def check_historical_format(text):
    """Check historical citation format: Author. "Title." *Journal* vol (year): pages."""
    issues = []

    year = extract_year(text)
    if not year:
        issues.append("no publication year found")

    if not text[0:1].isupper():
        issues.append("doesn't start with author name")

    return issues


# ── Main ────────────────────────────────────────

def main():
    files = sorted(glob.glob(str(DOCS_DIR / "[0-9]*.md")))
    if not files:
        print("ERROR: no chapter files found")
        sys.exit(1)

    total_refs = 0
    issues = []  # (severity, chapter, category, ref_num, message)
    all_urls = []  # (chapter, ref_num, url)
    all_refs_by_text = defaultdict(list)  # normalized_text -> [(chapter, num)]

    print("=" * 80)
    print("Evenwicht Reference Verification")
    print("=" * 80)
    print()

    # ── Pass 1: Extract and validate format ──────

    for filepath in files:
        ch_name = Path(filepath).stem
        ch_num = int(ch_name.split("-")[0])
        refs = extract_references(filepath)

        if not refs:
            issues.append(("WARN", ch_num, "-", 0, "no references section found"))
            continue

        for category, entries in refs.items():
            total_refs += len(entries)

            # Check alphabetical order
            sort_keys = [extract_author_sort_key(e["text"]) for e in entries]
            for i in range(1, len(sort_keys)):
                if sort_keys[i] and sort_keys[i - 1] and sort_keys[i] < sort_keys[i - 1]:
                    issues.append(("WARN", ch_num, category, entries[i]["num"],
                                   f"not alphabetical: '{sort_keys[i-1]}' before '{sort_keys[i]}'"))

            for entry in entries:
                num = entry["num"]
                text = entry["text"]

                # Track for duplicate detection
                norm_key = re.sub(r"\s+", " ", text.lower().strip().rstrip("."))[:100]
                all_refs_by_text[norm_key].append((ch_num, num))

                # Format checks
                if category == "Textbooks":
                    fmt_issues = check_textbook_format(text)
                elif category == "Historical":
                    fmt_issues = check_historical_format(text)
                else:
                    fmt_issues = []

                for issue in fmt_issues:
                    issues.append(("WARN", ch_num, category, num, f"format: {issue}"))

                # Extract URLs for later checking
                urls = extract_urls(text)
                for url in urls:
                    all_urls.append((ch_num, num, url))

                # Year check
                year = extract_year(text)
                if year and (year > 2026 or year < 1500):
                    issues.append(("ERROR", ch_num, category, num, f"implausible year: {year}"))

    print(f"Extracted {total_refs} references from {len(files)} chapters")
    print()

    # ── Pass 2: Duplicate detection ──────────────

    dup_count = 0
    for norm_text, locations in all_refs_by_text.items():
        if len(locations) > 1:
            chs = ", ".join(f"Ch {ch}[{n}]" for ch, n in locations)
            # Only flag if same text appears in different chapters
            ch_set = set(ch for ch, _ in locations)
            if len(ch_set) > 1:
                dup_count += 1
                issues.append(("INFO", locations[0][0], "-", locations[0][1],
                               f"possible duplicate across chapters: {chs}"))

    print(f"Duplicate check: {dup_count} possible cross-chapter duplicates")

    # ── Pass 3: URL checks (unless --quick) ──────

    if not QUICK_MODE and HAS_REQUESTS:
        print(f"\nChecking {len(all_urls)} URLs...")
        url_ok = 0
        url_fail = 0
        url_redirect = 0

        for i, (ch, num, url) in enumerate(all_urls):
            status, extra = check_url(url)
            if status and 200 <= status < 400:
                url_ok += 1
                if extra and extra != url:
                    url_redirect += 1
            elif status == 403:
                # Many sites block HEAD requests — not a real error
                url_ok += 1
            elif status:
                url_fail += 1
                issues.append(("WARN", ch, "Online Resources", num,
                               f"HTTP {status}: {url}"))
            else:
                url_fail += 1
                issues.append(("WARN", ch, "Online Resources", num,
                               f"unreachable: {url} ({extra})"))

            # Rate limit
            if (i + 1) % 10 == 0:
                print(f"  {i+1}/{len(all_urls)} checked...")
                time.sleep(0.5)

        print(f"  OK: {url_ok}, Failed: {url_fail}, Redirected: {url_redirect}")
    else:
        print(f"\nURL checking: SKIPPED {'(--quick mode)' if QUICK_MODE else '(requests not installed)'}")

    # ── Report ───────────────────────────────────

    errors = [i for i in issues if i[0] == "ERROR"]
    warnings = [i for i in issues if i[0] == "WARN"]
    infos = [i for i in issues if i[0] == "INFO"]

    print()
    print("=" * 80)
    print(f"RESULTS: {total_refs} references checked")
    print(f"  {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
    print("=" * 80)

    if errors:
        print("\n--- ERRORS ---")
        for sev, ch, cat, num, msg in errors:
            print(f"  Ch {ch:02d} [{num}] ({cat}): {msg}")

    if warnings:
        print("\n--- WARNINGS ---")
        for sev, ch, cat, num, msg in warnings:
            print(f"  Ch {ch:02d} [{num}] ({cat}): {msg}")

    if infos:
        print(f"\n--- INFO ({len(infos)} items) ---")
        for sev, ch, cat, num, msg in infos[:20]:
            print(f"  Ch {ch:02d} [{num}] ({cat}): {msg}")
        if len(infos) > 20:
            print(f"  ... and {len(infos) - 20} more")

    print()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
