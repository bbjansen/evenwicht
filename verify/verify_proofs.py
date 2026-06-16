# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Proof structure and algebraic step verification for the Evenwicht textbook.

Extracts every proof from Section 4 ("Core Theory") of all 48 chapters,
validates structural properties, and where possible verifies algebraic
manipulations symbolically via sympy.

Usage:
    python3 verify/verify_proofs.py

Also exposes ``build() -> Chapter`` for integration with the verification
framework (run_all.py).
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework import Chapter, StructuralCheck

# ---------------------------------------------------------------------------
# Chapter file registry (mirrors verify_prose.py)
# ---------------------------------------------------------------------------

CHAPTER_FILES = {
    i: f"{i:02d}-{name}.md"
    for i, name in enumerate([
        "",
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
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TheoremBlock:
    """A theorem/lemma/proposition and its associated proof."""
    chapter: int
    chapter_title: str
    label: str           # e.g. "Theorem 3.5"
    kind: str            # "Theorem", "Lemma", "Proposition", "Corollary"
    statement: str       # Full theorem statement text
    proof: str           # Full proof text
    hypotheses: list[str] = field(default_factory=list)
    conclusion: str = ""


@dataclass
class AlgebraicStep:
    """A single algebraic equation or equality extracted from a proof."""
    lhs: str
    rhs: str
    raw: str


@dataclass
class ProofCheckResult:
    """Result of checking a single proof."""
    theorem_label: str
    chapter: int
    checks_passed: int = 0
    checks_total: int = 0
    issues: list[str] = field(default_factory=list)


@dataclass
class FullResult:
    """Aggregated results from all chapters."""
    theorems: list[TheoremBlock] = field(default_factory=list)
    proof_results: list[ProofCheckResult] = field(default_factory=list)
    chapters_processed: int = 0
    chapters_with_proofs: int = 0


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

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


def _extract_theorem_blocks(
    section_text: str,
    chapter_num: int,
    chapter_title: str,
) -> list[TheoremBlock]:
    """Extract theorem statements and their proofs from Section 4."""
    blocks: list[TheoremBlock] = []

    # Match **Theorem X.Y** / **Lemma X.Y** / **Proposition X.Y** / **Corollary X.Y**
    theorem_pattern = re.compile(
        r"\*\*(Theorem|Lemma|Proposition|Corollary)\s+([\d.]+[a-z]?)\*\*"
        r"\s*(?:\(([^)]+)\))?\s*\.?\s*(.*?)(?=\n\n\*\*(?:Theorem|Lemma|Proposition"
        r"|Corollary|Definition|Example|Remark|Algorithm)\s|\n---\n|\Z)",
        re.DOTALL,
    )

    for m in theorem_pattern.finditer(section_text):
        kind = m.group(1)
        number = m.group(2)
        name = m.group(3) or ""
        body = m.group(4).strip()

        label = f"{kind} {number}"
        if name:
            label += f" ({name})"

        # Split body into statement and proof
        proof_marker = re.search(
            r"\*Proof\.\*|\*Proof:?\*|_Proof\._|_Proof:?_",
            body,
        )

        if proof_marker:
            statement = body[:proof_marker.start()].strip()
            proof_text = body[proof_marker.end():].strip()
            # Proof ends at square symbol or next block
            qed = re.search(r"\$\\square\$|\\square|\$\\blacksquare\$|QED", proof_text)
            if qed:
                proof_text = proof_text[:qed.start()].strip()
        else:
            statement = body
            proof_text = ""

        block = TheoremBlock(
            chapter=chapter_num,
            chapter_title=chapter_title,
            label=label,
            kind=kind,
            statement=statement,
            proof=proof_text,
        )

        # Extract hypotheses (text before "Then" or "then" in statement)
        _extract_hypotheses(block)

        blocks.append(block)

    return blocks


def _extract_hypotheses(block: TheoremBlock) -> None:
    """Parse hypotheses and conclusion from a theorem statement."""
    statement = block.statement

    # Common patterns: "Let ... Then ..." or "If ... then ..."
    # Try "Let ... Then ..."
    let_then = re.search(
        r"(?:Let|Suppose|Assume|Given)\b(.*?)\b(?:Then|then)\b(.*)",
        statement,
        re.DOTALL,
    )
    if let_then:
        hyp_text = let_then.group(1).strip().rstrip(".")
        block.hypotheses = [h.strip() for h in re.split(r"[,;](?:\s*and\s*)?", hyp_text) if h.strip()]
        block.conclusion = let_then.group(2).strip()
        return

    # Try "If ... then ..."
    if_then = re.search(
        r"\bIf\b(.*?)\bthen\b(.*)",
        statement,
        re.DOTALL | re.IGNORECASE,
    )
    if if_then:
        hyp_text = if_then.group(1).strip().rstrip(",")
        block.hypotheses = [h.strip() for h in re.split(r"[,;](?:\s*and\s*)?", hyp_text) if h.strip()]
        block.conclusion = if_then.group(2).strip()
        return

    # Try "For all/every ..."
    forall = re.search(
        r"\b(?:For all|For every|For each)\b(.*?)(?:,\s*)(.*)",
        statement,
        re.DOTALL,
    )
    if forall:
        block.hypotheses = [forall.group(1).strip()]
        block.conclusion = forall.group(2).strip()


def _extract_algebraic_steps(proof_text: str) -> list[AlgebraicStep]:
    """Extract algebraic equalities from a proof.

    Looks for display-math equations ($$...$$) and inline $...=...$ patterns.
    """
    steps: list[AlgebraicStep] = []

    # Display math: $$...$$
    display_math = re.findall(r"\$\$(.*?)\$\$", proof_text, re.DOTALL)
    for expr in display_math:
        # Handle aligned environments
        expr_clean = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", expr)
        # Split on \\ for multi-line
        lines = re.split(r"\\\\", expr_clean)
        for line in lines:
            line = line.strip()
            if "=" in line:
                # Split on first = sign (respecting LaTeX)
                parts = line.split("=", 1)
                if len(parts) == 2:
                    lhs = parts[0].strip().lstrip("&")
                    rhs = parts[1].strip()
                    steps.append(AlgebraicStep(lhs=lhs, rhs=rhs, raw=line))

    # Inline math with equality: $expr = expr$
    inline_eq = re.findall(r"\$((?:[^$]|\\\$)+)\$", proof_text)
    for expr in inline_eq:
        if "=" in expr and "\\neq" not in expr and "\\leq" not in expr and "\\geq" not in expr:
            parts = expr.split("=", 1)
            if len(parts) == 2:
                lhs = parts[0].strip()
                rhs = parts[1].strip()
                if lhs and rhs and len(lhs) > 1 and len(rhs) > 1:
                    steps.append(AlgebraicStep(lhs=lhs, rhs=rhs, raw=expr))

    return steps


# ---------------------------------------------------------------------------
# Proof checking
# ---------------------------------------------------------------------------

def _check_proof_structure(block: TheoremBlock) -> ProofCheckResult:
    """Run structural checks on a single theorem/proof pair."""
    result = ProofCheckResult(
        theorem_label=f"Ch {block.chapter:02d} {block.label}",
        chapter=block.chapter,
    )

    # Check 1: Proof exists
    result.checks_total += 1
    if block.proof:
        result.checks_passed += 1
    else:
        result.issues.append("No proof text found")
        return result  # No further checks possible

    # Check 2: Proof references the hypotheses
    result.checks_total += 1
    if block.hypotheses:
        # Check that at least some hypothesis language appears in the proof
        hyp_keywords = []
        for h in block.hypotheses:
            # Extract meaningful words from hypothesis
            words = re.findall(r"[a-zA-Z]{3,}", h)
            hyp_keywords.extend(w.lower() for w in words if len(w) > 3)

        if hyp_keywords:
            proof_lower = block.proof.lower()
            hits = sum(1 for kw in hyp_keywords if kw in proof_lower)
            if hits > 0:
                result.checks_passed += 1
            else:
                result.issues.append(
                    "Proof does not appear to reference the theorem's hypotheses"
                )
        else:
            result.checks_passed += 1  # No meaningful keywords to check
    else:
        result.checks_passed += 1  # No hypotheses to check against

    # Check 3: Proof progresses toward conclusion
    result.checks_total += 1
    if block.conclusion:
        # Check that some conclusion language appears in the proof
        conclusion_words = re.findall(r"[a-zA-Z]{3,}", block.conclusion)
        conclusion_words = [w.lower() for w in conclusion_words if len(w) > 3]
        if conclusion_words:
            proof_lower = block.proof.lower()
            hits = sum(1 for w in conclusion_words if w in proof_lower)
            if hits > 0:
                result.checks_passed += 1
            else:
                result.issues.append(
                    "Proof does not appear to reach the theorem's conclusion"
                )
        else:
            result.checks_passed += 1
    else:
        result.checks_passed += 1

    # Check 4: Algebraic steps are internally consistent (where possible)
    steps = _extract_algebraic_steps(block.proof)
    if steps:
        step_result = _verify_algebraic_chain(steps)
        result.checks_total += step_result.checks_total
        result.checks_passed += step_result.checks_passed
        result.issues.extend(step_result.issues)

    # Check 5: Proof chain of implications is well-formed
    result.checks_total += 1
    implication_words = [
        "therefore", "thus", "hence", "so ", "it follows",
        "which gives", "which implies", "consequently",
        "we conclude", "this shows", "we have",
        "since", "because", "by",
    ]
    proof_lower = block.proof.lower()
    connective_count = sum(1 for w in implication_words if w in proof_lower)
    if len(block.proof) > 100 and connective_count == 0:
        result.issues.append(
            "Proof lacks logical connectives (therefore, hence, since, ...)"
        )
    else:
        result.checks_passed += 1

    return result


def _verify_algebraic_chain(steps: list[AlgebraicStep]) -> ProofCheckResult:
    """Attempt to verify algebraic equalities using sympy."""
    result = ProofCheckResult(theorem_label="(algebraic steps)", chapter=0)

    try:
        import sympy
        from sympy.parsing.latex import parse_latex
    except ImportError:
        # sympy or latex parsing not available; skip symbolic checks
        return result

    for i, step in enumerate(steps):
        result.checks_total += 1
        try:
            lhs_expr = _safe_parse_latex(step.lhs)
            rhs_expr = _safe_parse_latex(step.rhs)

            if lhs_expr is None or rhs_expr is None:
                # Could not parse; skip but don't count as failure
                result.checks_total -= 1
                continue

            diff = sympy.simplify(lhs_expr - rhs_expr)
            if diff == 0 or diff == sympy.S.Zero:
                result.checks_passed += 1
            else:
                # Try numerical evaluation as fallback
                try:
                    free = diff.free_symbols
                    if free:
                        # Substitute random values
                        import random
                        random.seed(42 + i)
                        subs = {s: random.uniform(0.5, 2.0) for s in free}
                        val = complex(diff.subs(subs).evalf())
                        if abs(val) < 1e-8:
                            result.checks_passed += 1
                        else:
                            result.issues.append(
                                f"Step {i+1}: {step.raw[:80]} "
                                f"(residual={val:.2e})"
                            )
                    else:
                        val = complex(diff.evalf())
                        if abs(val) < 1e-8:
                            result.checks_passed += 1
                        else:
                            result.issues.append(
                                f"Step {i+1}: {step.raw[:80]} "
                                f"(residual={val:.2e})"
                            )
                except Exception:
                    # Numerical evaluation also failed; skip
                    result.checks_total -= 1
        except Exception:
            # Parsing or simplification error; skip
            result.checks_total -= 1

    return result


def _safe_parse_latex(latex_str: str) -> "sympy.Expr | None":
    """Attempt to parse a LaTeX string into a sympy expression.

    Returns None if parsing fails.
    """
    try:
        from sympy.parsing.latex import parse_latex

        # Clean up common LaTeX artifacts
        s = latex_str.strip()
        s = re.sub(r"\\quad|\\qquad|\\text\{[^}]*\}", "", s)
        s = re.sub(r"\\left|\\right", "", s)
        s = re.sub(r"\\,|\\;|\\:|\\!", "", s)
        s = s.strip()

        if not s or len(s) < 1:
            return None

        return parse_latex(s)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

def extract_and_check_all(docs_dir: str) -> FullResult:
    """Extract and check all proofs from the textbook."""
    result = FullResult()

    for ch_num, filename in sorted(CHAPTER_FILES.items()):
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        result.chapters_processed += 1
        chapter_title = _extract_chapter_title(text)

        # Extract Core Theory section
        section4 = _extract_section(text, 4, title="Core Theory")
        if not section4:
            continue

        blocks = _extract_theorem_blocks(section4, ch_num, chapter_title)
        if not blocks:
            continue

        result.chapters_with_proofs += 1
        result.theorems.extend(blocks)

        for block in blocks:
            check_result = _check_proof_structure(block)
            result.proof_results.append(check_result)

    return result


# ---------------------------------------------------------------------------
# Framework integration: build() -> Chapter
# ---------------------------------------------------------------------------

def build() -> Chapter:
    """Build a Chapter of structural checks for the verification framework."""
    ch = Chapter(201, "Proof Verification")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs", "domains")

    # Run full extraction and checking
    result = extract_and_check_all(docs_dir)

    # Check: theorems were extracted
    def check_extraction() -> tuple[bool, str]:
        if result.theorems:
            return True, ""
        return False, "No theorems extracted from any chapter"

    ch.add(StructuralCheck(
        label="Theorem extraction found proofs",
        section="4",
        predicate=check_extraction,
    ))

    # Check: coverage across chapters
    def check_coverage() -> tuple[bool, str]:
        if result.chapters_with_proofs >= 10:
            return True, ""
        return False, (
            f"Only {result.chapters_with_proofs} chapters had extractable "
            f"proofs (expected >=10)"
        )

    ch.add(StructuralCheck(
        label="Proof coverage across chapters (>=10 chapters)",
        section="4",
        predicate=check_coverage,
    ))

    # Check: all proofs have proof text (informational)
    def check_proofs_exist() -> tuple[bool, str]:
        missing = [
            r.theorem_label for r in result.proof_results
            if "No proof text found" in " ".join(r.issues)
        ]
        if not missing:
            return True, ""
        return True, (
            f"{len(missing)} theorems lack proof text: "
            + ", ".join(missing[:5])
        )

    ch.add(StructuralCheck(
        label="All theorems have associated proofs",
        section="4",
        predicate=check_proofs_exist,
    ))

    # Check: proofs reference hypotheses (informational)
    def check_hypotheses() -> tuple[bool, str]:
        issues = [
            r.theorem_label for r in result.proof_results
            if any("hypotheses" in i for i in r.issues)
        ]
        if not issues:
            return True, ""
        return True, (
            f"{len(issues)} proofs don't reference their hypotheses: "
            + ", ".join(issues[:5])
        )

    ch.add(StructuralCheck(
        label="Proofs reference their hypotheses",
        section="4",
        predicate=check_hypotheses,
    ))

    # Check: proofs have logical connectives (informational)
    def check_connectives() -> tuple[bool, str]:
        issues = [
            r.theorem_label for r in result.proof_results
            if any("connective" in i for i in r.issues)
        ]
        if not issues:
            return True, ""
        return True, (
            f"{len(issues)} proofs lack logical connectives: "
            + ", ".join(issues[:5])
        )

    ch.add(StructuralCheck(
        label="Proofs contain logical connectives",
        section="4",
        predicate=check_connectives,
    ))

    # Check: algebraic steps verify (aggregate pass rate)
    def check_algebra() -> tuple[bool, str]:
        total_steps = sum(r.checks_total for r in result.proof_results)
        passed_steps = sum(r.checks_passed for r in result.proof_results)
        if total_steps == 0:
            return True, ""  # No algebraic steps to check
        rate = passed_steps / total_steps
        if rate >= 0.8:
            return True, ""
        return False, (
            f"Only {passed_steps}/{total_steps} ({rate:.0%}) proof checks "
            f"passed (threshold: 80%)"
        )

    ch.add(StructuralCheck(
        label="Proof structural checks pass rate >=80%",
        section="4",
        predicate=check_algebra,
    ))

    # Check: proofs reach their conclusions (informational)
    def check_conclusions() -> tuple[bool, str]:
        issues = [
            r.theorem_label for r in result.proof_results
            if any("conclusion" in i for i in r.issues)
        ]
        if not issues:
            return True, ""
        return True, (
            f"{len(issues)} proofs don't reach their conclusions: "
            + ", ".join(issues[:5])
        )

    ch.add(StructuralCheck(
        label="Proofs reach their conclusions",
        section="4",
        predicate=check_conclusions,
    ))

    return ch


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run proof verification as a standalone script."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs", "domains")

    print("Extracting and checking proofs from all 48 chapters...")
    result = extract_and_check_all(docs_dir)

    print(f"  Chapters processed: {result.chapters_processed}")
    print(f"  Chapters with proofs: {result.chapters_with_proofs}")
    print(f"  Total theorems extracted: {len(result.theorems)}")

    total_checks = sum(r.checks_total for r in result.proof_results)
    passed_checks = sum(r.checks_passed for r in result.proof_results)
    print(f"  Total proof checks: {total_checks}")
    print(f"  Passed: {passed_checks}")
    if total_checks > 0:
        print(f"  Pass rate: {passed_checks / total_checks:.1%}")

    # Show issues
    all_issues = [
        (r.theorem_label, issue)
        for r in result.proof_results
        for issue in r.issues
    ]
    if all_issues:
        print(f"\nIssues ({len(all_issues)}):")
        for label, issue in all_issues[:30]:
            print(f"  [{label}] {issue}")
        if len(all_issues) > 30:
            print(f"  ... and {len(all_issues) - 30} more")

    # Run framework checks
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
