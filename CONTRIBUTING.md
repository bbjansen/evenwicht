<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Contributing to Evenwicht

Thank you for your interest. This document explains how to report errors,
suggest improvements, and submit changes.

## Reporting Errors

Mathematical, typographical, and factual errors are taken seriously. Every
report is investigated and corrections are credited in the errata.

Open an issue using the **Errata** template. Include:

- The chapter number and section
- What is currently written
- What it should be
- How you found the error (e.g. worked the exercise, checked a reference)

## Suggesting Improvements

For suggestions that are not errors (new exercises, better explanations,
additional references), open a standard issue and describe the improvement.

## Submitting Changes

### Setup

1. Fork the repository
2. Clone your fork
3. Install Python dependencies:
   ```bash
   pip install numpy scipy sympy pyspellchecker requests
   ```

### Branch naming

Create a branch from `main` using one of these prefixes:

| Prefix | Purpose |
|--------|---------|
| `fix/` | Errata and corrections |
| `docs/` | Documentation improvements |
| `feature/` | New content or functionality |
| `chore/` | Maintenance and tooling |

Example: `fix/ch13-theorem-3.7-typo`

### Making changes

1. Match the existing prose tone (see Style below)
2. Use British English throughout
3. Number all definitions, theorems, and algorithms
4. Run the verification suite before committing:
   ```bash
   python scripts/verify-domain-consistency.py
   python scripts/verify-math.py
   python scripts/verify-glossary.py
   python scripts/verify-spelling.py
   python verify/run_all.py
   ```

### Pull requests

1. Push your branch to your fork
2. Open a PR against `main`
3. Fill in the PR template
4. All CI checks must pass before merge

### What the CI checks

- **Documentation checks**: domain consistency, math validation, glossary
  sync, cross-references, spelling, API consistency
- **Mathematical verification**: 4,742 automated checks against SciPy,
  SymPy, and NumPy

### Style

All prose in the domain chapters follows these rules:

- Third person, no "you"
- Short sentences; one point each
- British English (-ise, -our, colour, analyse)
- No em dashes; use semicolons
- No forbidden words (see the full list in the guide)
- Active voice preferred

### Copyright headers

All source files carry a copyright header. Use the `scripts/add-license-headers.sh`
script to add headers to new files.

## Code of Conduct

Be respectful. Focus on the mathematics. Corrections are welcome;
criticism of contributors is not.

## License

By contributing, you agree that your contributions will be licensed under
AGPL-3.0-only (source code) or CC-BY-NC-4.0 (documentation), matching the
project's existing licenses.
