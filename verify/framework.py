# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Verification framework for the Evenwicht math textbook.

Supports three verification layers:
  1. Symbolic — verify formulas/identities via sympy symbolic computation
  2. Numeric — verify worked-example numbers against scipy/numpy reference values
  3. Structural — verify consistency properties (convergence rates, distributions sum to 1, etc.)

Usage:
    from framework import Check, SymbolicCheck, NumericCheck, StructuralCheck, Chapter, Report

    chapter = Chapter(13, "Probability Theory")
    chapter.add(NumericCheck(
        label="Bayes P(D|T+)",
        section="8.1",
        stated=0.0876,
        computed=lambda: 0.0095 / 0.1085,
        tolerance=1e-3,
    ))
    chapter.run()
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIP = "SKIP"


class Layer(Enum):
    SYMBOLIC = "SYMBOLIC"
    NUMERIC = "NUMERIC"
    STRUCTURAL = "STRUCTURAL"


@dataclass
class Result:
    chapter: int
    label: str
    section: str
    layer: Layer
    status: Status
    stated: str = ""
    computed: str = ""
    message: str = ""
    note: str = ""


# ---------------------------------------------------------------------------
# Check base class
# ---------------------------------------------------------------------------

@dataclass
class Check:
    label: str
    section: str = ""
    note: str = ""

    def run(self, chapter_num: int) -> Result:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Numeric check — compare stated vs computed float values
# ---------------------------------------------------------------------------

@dataclass
class NumericCheck(Check):
    stated: float = 0.0
    computed: Callable[[], float] | float = 0.0
    tolerance: float = 1e-6

    def run(self, chapter_num: int) -> Result:
        try:
            comp = self.computed() if callable(self.computed) else self.computed
            ok = _approx_eq(self.stated, comp, self.tolerance)
            return Result(
                chapter=chapter_num,
                label=self.label,
                section=self.section,
                layer=Layer.NUMERIC,
                status=Status.PASS if ok else Status.FAIL,
                stated=_fmt(self.stated),
                computed=_fmt(comp),
                message="" if ok else f"delta={abs(comp - self.stated):.6e}, tol={self.tolerance:.1e}",
                note=self.note,
            )
        except Exception as exc:
            return Result(
                chapter=chapter_num,
                label=self.label,
                section=self.section,
                layer=Layer.NUMERIC,
                status=Status.ERROR,
                message=f"{type(exc).__name__}: {exc}",
                note=self.note,
            )


# ---------------------------------------------------------------------------
# Symbolic check — verify a sympy identity evaluates to True / simplifies to 0
# ---------------------------------------------------------------------------

@dataclass
class SymbolicCheck(Check):
    """Verify a symbolic identity.

    Provide *one* of:
      - ``identity``: a callable returning a sympy Boolean (e.g., Eq(lhs, rhs))
        that should evaluate to True.
      - ``zero_expr``: a callable returning a sympy expression that should
        simplify to 0.
    """
    identity: Callable | None = None
    zero_expr: Callable | None = None

    def run(self, chapter_num: int) -> Result:
        try:
            import sympy
            if self.identity is not None:
                expr = self.identity()
                simplified = sympy.simplify(expr)
                ok = simplified is sympy.true or simplified == True  # noqa: E712
                return Result(
                    chapter=chapter_num,
                    label=self.label,
                    section=self.section,
                    layer=Layer.SYMBOLIC,
                    status=Status.PASS if ok else Status.FAIL,
                    stated="True",
                    computed=str(simplified),
                    note=self.note,
                )
            elif self.zero_expr is not None:
                expr = self.zero_expr()
                simplified = sympy.simplify(expr)
                ok = simplified == 0 or simplified == sympy.S.Zero
                return Result(
                    chapter=chapter_num,
                    label=self.label,
                    section=self.section,
                    layer=Layer.SYMBOLIC,
                    status=Status.PASS if ok else Status.FAIL,
                    stated="0",
                    computed=str(simplified),
                    note=self.note,
                )
            else:
                return Result(
                    chapter=chapter_num,
                    label=self.label,
                    section=self.section,
                    layer=Layer.SYMBOLIC,
                    status=Status.ERROR,
                    message="No identity or zero_expr provided",
                    note=self.note,
                )
        except Exception as exc:
            return Result(
                chapter=chapter_num,
                label=self.label,
                section=self.section,
                layer=Layer.SYMBOLIC,
                status=Status.ERROR,
                message=f"{type(exc).__name__}: {exc}",
                note=self.note,
            )


# ---------------------------------------------------------------------------
# Structural check — verify a boolean property
# ---------------------------------------------------------------------------

@dataclass
class StructuralCheck(Check):
    """Verify a structural/consistency property.

    ``predicate`` is a callable returning (bool, message_on_failure).
    """
    predicate: Callable[[], tuple[bool, str]] | None = None

    def run(self, chapter_num: int) -> Result:
        try:
            ok, msg = self.predicate()
            return Result(
                chapter=chapter_num,
                label=self.label,
                section=self.section,
                layer=Layer.STRUCTURAL,
                status=Status.PASS if ok else Status.FAIL,
                message="" if ok else msg,
                note=self.note,
            )
        except Exception as exc:
            return Result(
                chapter=chapter_num,
                label=self.label,
                section=self.section,
                layer=Layer.STRUCTURAL,
                status=Status.ERROR,
                message=f"{type(exc).__name__}: {exc}",
                note=self.note,
            )


# ---------------------------------------------------------------------------
# Chapter container
# ---------------------------------------------------------------------------

class Chapter:
    def __init__(self, number: int, title: str):
        self.number = number
        self.title = title
        self.checks: list[Check] = []
        self.results: list[Result] = []

    def add(self, check: Check) -> None:
        self.checks.append(check)

    def run(self) -> list[Result]:
        self.results = [c.run(self.number) for c in self.checks]
        return self.results

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == Status.PASS)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == Status.FAIL)

    @property
    def errors(self) -> int:
        return sum(1 for r in self.results if r.status == Status.ERROR)

    @property
    def total(self) -> int:
        return len(self.results)


# ---------------------------------------------------------------------------
# Report — console + markdown output
# ---------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.chapters: list[Chapter] = []

    def add_chapter(self, chapter: Chapter) -> None:
        self.chapters.append(chapter)

    def print_console(self) -> None:
        sep = "=" * 110
        print(sep)
        print("EVENWICHT TEXTBOOK — MATHEMATICAL VERIFICATION REPORT")
        print(sep)
        print()

        for ch in self.chapters:
            print(f"--- Ch {ch.number:02d}: {ch.title} ({ch.passed}/{ch.total} passed) ---")
            for r in ch.results:
                icon = {"PASS": "\u2713", "FAIL": "\u2717", "ERROR": "!", "SKIP": "-"}[r.status.value]
                line = f"  {icon} {r.status.value:<5s} | {r.layer.value:<10s} | {r.section:<6s} | {r.label}"
                if r.stated and r.computed:
                    line += f"  [stated: {r.stated}, computed: {r.computed}]"
                if r.message:
                    line += f"  — {r.message}"
                if r.note:
                    line += f"  ({r.note})"
                print(line)
            if ch.failed > 0 or ch.errors > 0:
                print(f"  ** {ch.failed} FAILURES, {ch.errors} ERRORS **")
            print()

        # Summary
        total = sum(ch.total for ch in self.chapters)
        passed = sum(ch.passed for ch in self.chapters)
        failed = sum(ch.failed for ch in self.chapters)
        errors = sum(ch.errors for ch in self.chapters)

        print(sep)
        print(f"SUMMARY: {passed}/{total} passed, {failed} failed, {errors} errors")
        if failed == 0 and errors == 0:
            print("All verifications PASSED.")
        print(sep)

    def write_markdown(self, path: str) -> None:
        lines: list[str] = []
        lines.append("# Evenwicht Textbook — Mathematical Verification Report\n")
        lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        total = sum(ch.total for ch in self.chapters)
        passed = sum(ch.passed for ch in self.chapters)
        failed = sum(ch.failed for ch in self.chapters)
        errors = sum(ch.errors for ch in self.chapters)

        lines.append(f"**Overall: {passed}/{total} passed, {failed} failed, {errors} errors**\n")

        for ch in self.chapters:
            lines.append(f"\n## Ch {ch.number:02d}: {ch.title}\n")
            lines.append(f"Result: {ch.passed}/{ch.total} passed\n")
            lines.append("| Status | Layer | Section | Check | Details |")
            lines.append("|--------|-------|---------|-------|---------|")
            for r in ch.results:
                icon = {"PASS": "\u2713", "FAIL": "\u2717", "ERROR": "!", "SKIP": "-"}[r.status.value]
                details = ""
                if r.stated and r.computed:
                    details = f"stated: `{r.stated}`, computed: `{r.computed}`"
                if r.message:
                    details += f" {r.message}" if details else r.message
                if r.note:
                    details += f" *({r.note})*"
                lines.append(f"| {icon} {r.status.value} | {r.layer.value} | {r.section} | {r.label} | {details} |")
            lines.append("")

        # Failures summary
        all_failures = [r for ch in self.chapters for r in ch.results if r.status in (Status.FAIL, Status.ERROR)]
        if all_failures:
            lines.append("\n## Failures & Errors\n")
            for r in all_failures:
                lines.append(f"- **Ch {r.chapter:02d} §{r.section}** — {r.label}: {r.message}")
            lines.append("")

        with open(path, "w") as f:
            f.write("\n".join(lines))

    @property
    def exit_code(self) -> int:
        failed = sum(ch.failed for ch in self.chapters)
        errors = sum(ch.errors for ch in self.chapters)
        return 0 if (failed == 0 and errors == 0) else 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _approx_eq(stated: float, computed: float, tol: float) -> bool:
    if stated == 0.0 and computed == 0.0:
        return True
    if stated == 0.0:
        return abs(computed) < tol
    return abs(computed - stated) / abs(stated) < tol


def _fmt(val: float) -> str:
    if val == 0.0:
        return "0"
    a = abs(val)
    if a >= 1e6 or a < 1e-4:
        return f"{val:.6e}"
    if a >= 100:
        return f"{val:.4f}"
    if a >= 1:
        return f"{val:.6f}"
    return f"{val:.6f}"
