# Verification Suite

Mathematical verification for all 48 chapters of the Evenwicht textbook. Every formula, worked example, identity, and theorem statement in the book is checked automatically.

> **Note:** This suite validates the **documentation content** (textbook math), not the TypeScript library. Library tests use vitest and live in `src/`. These Python scripts independently confirm the textbook is mathematically correct using NumPy, SciPy, and SymPy as reference implementations.

## Quick Start

```bash
# Run everything (chapters + meta-tests)
python3 verify/run_all.py

# Run specific chapters
python3 verify/run_all.py --chapters 13 14

# Run only meta-tests (theorems, diagrams, prose, proofs)
python3 verify/run_all.py --meta

# Run only chapter tests, skip meta
python3 verify/run_all.py --no-meta

# Combine: specific chapters + meta
python3 verify/run_all.py --chapters 1 2 --meta
```

A markdown report is written to `verify/report/verification-report.md` after every run. Override with `--report path/to/file.md`.

## Dependencies

```
numpy
scipy
sympy
```

## What Gets Verified

The suite uses a 3-layer verification approach, each targeting a different class of errors:

### Layer 1: Symbolic

Verifies formulas and identities via SymPy symbolic computation. A `SymbolicCheck` takes either an `identity` (a SymPy Boolean that must evaluate to `True`) or a `zero_expr` (a SymPy expression that must simplify to `0`).

Example: verifying that `exp(x+y) = exp(x) * exp(y)`.

### Layer 2: Numeric

Verifies worked-example numbers against NumPy/SciPy reference values. A `NumericCheck` compares a `stated` value from the text against a `computed` value with a configurable `tolerance` (default `1e-6`, relative).

Example: verifying that Bayes' theorem P(D|T+) = 0.0876 matches the computation 0.0095/0.1085.

### Layer 3: Structural

Verifies consistency properties that don't fit neatly into symbolic or numeric checks. A `StructuralCheck` runs a `predicate` function returning `(bool, failure_message)`.

Example: verifying that a probability distribution sums to 1, or that a convergence rate matches its stated order.

## Property-Based Theorem Testing

Beyond verifying individual formulas, the suite stress-tests theorem *statements* using five strategies:

1. **Random stress test** -- generate random inputs satisfying the hypotheses, verify the conclusion holds
2. **Counterexample hunt** -- verify the conclusion *fails* when hypotheses are violated (confirms they are necessary)
3. **Monte Carlo convergence** -- simulate limit theorems and verify approach to stated limits
4. **Consequence test** -- if the theorem is true, verify observable consequences
5. **Proof step algebra** -- verify each algebraic manipulation in the proof chain

These live in `theorem_testing.py` (core, chapters 1-24) and `theorem_testing_applied.py` (applied, chapters 25-48).

## File Structure

```
verify/
  run_all.py                     # Orchestrator (this file's entry point)
  framework.py                   # Check/Chapter/Report classes
  ch01_expressions.py            # Chapter 1 checks
  ...                            #   one file per chapter
  ch48_genetics.py               # Chapter 48 checks
  theorem_testing.py             # Property-based theorem tests (core)
  theorem_testing_applied.py     # Property-based theorem tests (applied)
  validate_diagrams.py           # Mermaid diagram syntax/cross-ref validation
  verify_prose.py                # Historical claim fact-checking
  verify_proofs.py               # Proof structure and algebraic step verification
  report/
    verification-report.md       # Generated markdown report
```

Chapter files (`ch01` through `ch48`) contain per-chapter checks. Meta modules run cross-cutting validations.

The registries in `run_all.py` control what runs:

- `CHAPTERS` -- maps chapter numbers (1-48) to module names
- `META_MODULES` -- maps meta-test keys to module names

## Adding New Checks

### Adding checks to an existing chapter

Open the chapter file (e.g., `ch13_probability.py`) and add checks inside the `build()` function:

```python
def build() -> Chapter:
    ch = Chapter(13, "Probability Theory")

    # Numeric: verify a worked example
    ch.add(NumericCheck(
        label="Bayes P(D|T+)",
        section="13.1",
        stated=0.0876,
        computed=lambda: 0.0095 / 0.1085,
        tolerance=1e-3,
    ))

    # Symbolic: verify an identity
    ch.add(SymbolicCheck(
        label="P(A|B) * P(B) = P(B|A) * P(A)",
        section="13.2",
        identity=lambda: sympy.Eq(
            sympy.Symbol("PAB") * sympy.Symbol("PB"),
            sympy.Symbol("PBA") * sympy.Symbol("PA"),
        ),
    ))

    # Structural: verify a property
    ch.add(StructuralCheck(
        label="PMF sums to 1",
        section="13.3",
        predicate=lambda: (abs(sum(pmf_values) - 1.0) < 1e-10, "PMF does not sum to 1"),
    ))

    return ch
```

### Adding a new chapter

1. Create `verify/chNN_name.py` with a `build() -> Chapter` function
2. Add the entry to `CHAPTERS` in `run_all.py`

### Adding a new meta module

1. Create the module with a `build() -> Chapter` function
2. Add the entry to `META_MODULES` in `run_all.py`

## Coverage

- 48 chapter verification modules
- ~3,900+ individual checks across all chapters
  - ~2,600 numeric checks
  - ~400 symbolic checks
  - ~1,000 structural checks
- 5 meta-verification modules (theorem testing, diagrams, prose, proofs)
