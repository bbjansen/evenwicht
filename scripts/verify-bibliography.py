#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify textbooks and historical papers exist via external APIs.

Checks:
  - Textbooks: OpenLibrary search by author + title
  - Historical papers: CrossRef search by author + title + year
  - Online Resources: HTTP HEAD for liveness

Usage:
  python3 scripts/verify-bibliography.py              # full check
  python3 scripts/verify-bibliography.py --textbooks   # textbooks only
  python3 scripts/verify-bibliography.py --papers      # papers only
  python3 scripts/verify-bibliography.py --urls        # URLs only
  python3 scripts/verify-bibliography.py --quick       # first 5 per category

Requires: requests (pip3 install requests)
"""

import glob
import re
import sys
import time
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "domains"

try:
    import requests
except ImportError:
    print("ERROR: 'requests' required. pip3 install requests")
    sys.exit(2)

QUICK = "--quick" in sys.argv
CHECK_TEXTBOOKS = "--textbooks" in sys.argv or not any(a.startswith("--t") or a.startswith("--p") or a.startswith("--u") for a in sys.argv[1:])
CHECK_PAPERS = "--papers" in sys.argv or not any(a.startswith("--t") or a.startswith("--p") or a.startswith("--u") for a in sys.argv[1:])
CHECK_URLS = "--urls" in sys.argv or not any(a.startswith("--t") or a.startswith("--p") or a.startswith("--u") for a in sys.argv[1:])

HEADERS = {"User-Agent": "Evenwicht-Bibliography-Checker/1.0 (mailto:bobjansen@pm.me)"}


# ── Extraction ───────────────────────────────────

def extract_all_references():
    """Extract all references from all chapters, grouped by category."""
    textbooks = []
    historical = []
    online = []

    for filepath in sorted(glob.glob(str(DOCS_DIR / "[0-9]*.md"))):
        ch_num = int(Path(filepath).stem.split("-")[0])
        text = Path(filepath).read_text(encoding="utf-8")

        start = re.search(r"^## (?:\d+\.\s*)?References\s*$", text, re.MULTILINE)
        if not start:
            continue
        end = re.search(r"^## (?:\d+\.\s*)?Glossary\s*$", text[start.end():], re.MULTILINE)
        section = text[start.end(): start.end() + end.start()] if end else text[start.end():]

        current_cat = None
        for line in section.splitlines():
            heading = re.match(r"^###\s+(.+)$", line)
            if heading:
                cat = heading.group(1).strip()
                if "Textbook" in cat:
                    current_cat = "textbooks"
                elif "Historical" in cat:
                    current_cat = "historical"
                elif "Online" in cat:
                    current_cat = "online"
                continue

            ref_match = re.match(r"^(?:- )?\[(\d+)\]\s+(.+)$", line)
            if ref_match and current_cat:
                entry = {"ch": ch_num, "num": int(ref_match.group(1)), "text": ref_match.group(2).strip()}
                if current_cat == "textbooks":
                    textbooks.append(entry)
                elif current_cat == "historical":
                    historical.append(entry)
                elif current_cat == "online":
                    online.append(entry)

    return textbooks, historical, online


# ── Parsers ──────────────────────────────────────

def parse_textbook(text):
    """Extract author, title, year from a textbook reference."""
    # Author(s). *Title*, edition. Publisher, Year.
    author_match = re.match(r"^(.+?)\.\s+\*", text)
    title_match = re.search(r"\*([^*]+)\*", text)
    year_match = re.findall(r"\b(1[6-9]\d{2}|20[0-2]\d)\b", text)

    author = author_match.group(1).strip() if author_match else None
    title = title_match.group(1).strip() if title_match else None
    year = int(year_match[-1]) if year_match else None

    return author, title, year


def parse_paper(text):
    """Extract author, title, journal, year from a historical paper reference."""
    author_match = re.match(r"^(.+?)\.\s+[\"']", text)
    if not author_match:
        author_match = re.match(r"^(.+?)\.\s+\*", text)
    title_match = re.search(r'["\u201c]([^"\u201d]+)["\u201d]', text)
    if not title_match:
        title_match = re.search(r"\*([^*]+)\*", text)
    journal_match = re.search(r"\*([^*]+)\*\s+\d", text)
    year_match = re.findall(r"\b(1[6-9]\d{2}|20[0-2]\d)\b", text)

    author = author_match.group(1).strip() if author_match else None
    title = title_match.group(1).strip() if title_match else None
    journal = journal_match.group(1).strip() if journal_match else None
    year = int(year_match[0]) if year_match else None

    return author, title, journal, year


# ── API Lookups ──────────────────────────────────

def check_openlibrary(author, title, year):
    """Search OpenLibrary for a textbook. Returns (found, details)."""
    if not title:
        return None, "no title parsed"

    # Search by title + author
    query = title[:80]
    params = {"q": query, "limit": 3}
    if author:
        # Use first author surname
        surname = author.split(",")[0].split(" ")[-1]
        params["author"] = surname

    try:
        r = requests.get("https://openlibrary.org/search.json", params=params,
                         headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"

        data = r.json()
        if data.get("numFound", 0) > 0:
            top = data["docs"][0]
            found_title = top.get("title", "")
            found_year = top.get("first_publish_year", "?")
            return True, f"found: '{found_title}' ({found_year})"
        else:
            return False, "not found in OpenLibrary"
    except Exception as e:
        return None, str(e)


def check_crossref(author, title, year):
    """Search CrossRef for a paper. Returns (found, details)."""
    if not title:
        return None, "no title parsed"

    query = title[:100]
    params = {"query": query, "rows": 3}

    try:
        r = requests.get("https://api.crossref.org/works", params=params,
                         headers={**HEADERS, "Accept": "application/json"}, timeout=15)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"

        data = r.json()
        items = data.get("message", {}).get("items", [])
        if not items:
            return False, "not found in CrossRef"

        # Check if any result matches reasonably
        for item in items[:3]:
            found_title = " ".join(item.get("title", [""])).lower()
            query_lower = title.lower()[:60]
            # Fuzzy match: check if significant words overlap
            query_words = set(re.findall(r"\w{4,}", query_lower))
            found_words = set(re.findall(r"\w{4,}", found_title))
            overlap = len(query_words & found_words)
            if overlap >= min(3, len(query_words)):
                doi = item.get("DOI", "no DOI")
                found_year = item.get("published-print", {}).get("date-parts", [[None]])[0][0]
                if not found_year:
                    found_year = item.get("created", {}).get("date-parts", [[None]])[0][0]
                return True, f"DOI: {doi} ({found_year})"

        return False, "no matching title in CrossRef results"
    except Exception as e:
        return None, str(e)


def check_url(url):
    """Check URL liveness."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers=HEADERS)
        if 200 <= r.status_code < 400 or r.status_code == 403:
            return True, f"HTTP {r.status_code}"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:50]


# ── Main ─────────────────────────────────────────

def main():
    textbooks, historical, online = extract_all_references()

    print("=" * 80)
    print("Evenwicht Bibliography Verification")
    print("=" * 80)
    print(f"\nExtracted: {len(textbooks)} textbooks, {len(historical)} papers, {len(online)} URLs")
    print()

    results = {"found": 0, "not_found": 0, "error": 0, "skipped": 0}
    issues = []

    # ── Textbooks ────────────────────────────────
    if CHECK_TEXTBOOKS:
        items = textbooks[:5] if QUICK else textbooks
        print(f"--- Checking {len(items)} textbooks via OpenLibrary ---")
        for i, ref in enumerate(items):
            author, title, year = parse_textbook(ref["text"])
            found, detail = check_openlibrary(author, title, year)

            status = "FOUND" if found else ("NOT FOUND" if found is False else "ERROR")
            symbol = "\u2713" if found else ("\u2717" if found is False else "?")
            print(f"  {symbol} Ch {ref['ch']:02d} [{ref['num']}] {(title or 'no title')[:50]}")

            if found:
                results["found"] += 1
            elif found is False:
                results["not_found"] += 1
                issues.append(f"Ch {ref['ch']:02d} [{ref['num']}] TEXTBOOK not found: {(author or '?')}, *{(title or '?')[:40]}* ({year or '?'})")
            else:
                results["error"] += 1

            if (i + 1) % 10 == 0:
                print(f"  ... {i+1}/{len(items)} checked")
                time.sleep(1)  # rate limit

        print()

    # ── Historical papers ────────────────────────
    if CHECK_PAPERS:
        items = historical[:5] if QUICK else historical
        print(f"--- Checking {len(items)} papers via CrossRef ---")
        for i, ref in enumerate(items):
            author, title, journal, year = parse_paper(ref["text"])
            found, detail = check_crossref(author, title, year)

            status = "FOUND" if found else ("NOT FOUND" if found is False else "ERROR")
            symbol = "\u2713" if found else ("\u2717" if found is False else "?")
            print(f"  {symbol} Ch {ref['ch']:02d} [{ref['num']}] {(title or 'no title')[:50]}")

            if found:
                results["found"] += 1
            elif found is False:
                results["not_found"] += 1
                issues.append(f"Ch {ref['ch']:02d} [{ref['num']}] PAPER not found: {(author or '?')}, \"{(title or '?')[:40]}\" ({year or '?'})")
            else:
                results["error"] += 1

            if (i + 1) % 10 == 0:
                print(f"  ... {i+1}/{len(items)} checked")
                time.sleep(1)

        print()

    # ── URLs ─────────────────────────────────────
    if CHECK_URLS:
        items = online[:5] if QUICK else online
        print(f"--- Checking {len(items)} URLs ---")
        for i, ref in enumerate(items):
            urls = re.findall(r"https?://[^\s)>]+", ref["text"])
            for url in urls:
                found, detail = check_url(url)
                symbol = "\u2713" if found else "\u2717"
                if not found:
                    print(f"  {symbol} Ch {ref['ch']:02d} [{ref['num']}] {url[:60]} — {detail}")
                    issues.append(f"Ch {ref['ch']:02d} [{ref['num']}] URL: {url} — {detail}")
                    results["not_found"] += 1
                else:
                    results["found"] += 1

            if (i + 1) % 10 == 0:
                time.sleep(0.5)

        print()

    # ── Report ───────────────────────────────────
    print("=" * 80)
    print(f"RESULTS: {results['found']} found, {results['not_found']} not found, {results['error']} errors")
    print("=" * 80)

    if issues:
        print(f"\n--- {len(issues)} ISSUES ---")
        for issue in issues:
            print(f"  {issue}")

    print()
    return 1 if results["not_found"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
