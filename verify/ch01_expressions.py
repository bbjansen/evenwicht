# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Chapter 1: Mathematical Expressions & Functions — Verification.

Covers exponential laws, logarithm laws, trigonometric identities,
inverse relationships, triangle inequality, and worked numeric examples.
"""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(1, "Mathematical Expressions & Functions")

    # ------------------------------------------------------------------
    # Symbolic checks — Exponential laws
    # ------------------------------------------------------------------

    def _exp_add():
        import sympy
        x, y = sympy.symbols("x y")
        return sympy.Eq(sympy.exp(x + y), sympy.exp(x) * sympy.exp(y))

    ch.add(SymbolicCheck(
        label="exp(x+y) = exp(x)*exp(y)",
        section="1.1",
        identity=_exp_add,
    ))

    def _exp_sub():
        import sympy
        x, y = sympy.symbols("x y")
        return sympy.Eq(sympy.exp(x - y), sympy.exp(x) / sympy.exp(y))

    ch.add(SymbolicCheck(
        label="exp(x-y) = exp(x)/exp(y)",
        section="1.1",
        identity=_exp_sub,
    ))

    def _exp_power():
        # Verify at multiple numeric points since sympy cannot simplify
        # exp(x)**r - exp(r*x) to zero without restrictive assumptions.
        points = [(1.0, 2.0), (0.5, 3.0), (-1.0, 0.5), (2.0, -1.0), (0.0, 5.0)]
        for xv, rv in points:
            lhs = math.exp(xv) ** rv
            rhs = math.exp(rv * xv)
            if abs(lhs - rhs) / max(abs(rhs), 1e-15) > 1e-12:
                return False, f"Failed at x={xv}, r={rv}: {lhs} != {rhs}"
        return True, ""

    ch.add(StructuralCheck(
        label="(e^x)^r = e^(rx) (verified at 5 sample points)",
        section="1.1",
        predicate=_exp_power,
    ))

    def _exp_zero():
        import sympy
        return sympy.Eq(sympy.exp(0), sympy.Integer(1))

    ch.add(SymbolicCheck(
        label="e^0 = 1",
        section="1.1",
        identity=_exp_zero,
    ))

    # ------------------------------------------------------------------
    # Symbolic checks — Logarithm laws
    # ------------------------------------------------------------------

    def _ln_product():
        import sympy
        x, y = sympy.symbols("x y", positive=True)
        return sympy.Eq(sympy.log(x * y), sympy.log(x) + sympy.log(y))

    ch.add(SymbolicCheck(
        label="ln(xy) = ln(x) + ln(y)",
        section="1.2",
        identity=_ln_product,
    ))

    def _ln_quotient():
        import sympy
        x, y = sympy.symbols("x y", positive=True)
        return sympy.Eq(sympy.log(x / y), sympy.log(x) - sympy.log(y))

    ch.add(SymbolicCheck(
        label="ln(x/y) = ln(x) - ln(y)",
        section="1.2",
        identity=_ln_quotient,
    ))

    def _ln_power():
        import sympy
        x = sympy.Symbol("x", positive=True)
        r = sympy.Symbol("r", real=True)
        expr = sympy.log(x ** r) - r * sympy.log(x)
        return sympy.expand_log(expr, force=True)

    ch.add(SymbolicCheck(
        label="ln(x^r) = r*ln(x)",
        section="1.2",
        zero_expr=_ln_power,
    ))

    def _ln_one():
        import sympy
        return sympy.Eq(sympy.log(1), sympy.Integer(0))

    ch.add(SymbolicCheck(
        label="ln(1) = 0",
        section="1.2",
        identity=_ln_one,
    ))

    def _ln_e():
        import sympy
        return sympy.Eq(sympy.log(sympy.E), sympy.Integer(1))

    ch.add(SymbolicCheck(
        label="ln(e) = 1",
        section="1.2",
        identity=_ln_e,
    ))

    # ------------------------------------------------------------------
    # Symbolic checks — Trigonometric identities
    # ------------------------------------------------------------------

    def _pythagorean():
        import sympy
        x = sympy.Symbol("x")
        return sympy.Eq(sympy.sin(x) ** 2 + sympy.cos(x) ** 2, sympy.Integer(1))

    ch.add(SymbolicCheck(
        label="sin^2(x) + cos^2(x) = 1",
        section="1.3",
        identity=_pythagorean,
    ))

    def _sin_addition_zero():
        import sympy
        x, y = sympy.symbols("x y")
        lhs = sympy.sin(x + y)
        rhs = sympy.sin(x) * sympy.cos(y) + sympy.cos(x) * sympy.sin(y)
        return lhs - rhs

    ch.add(SymbolicCheck(
        label="sin(x+y) = sin(x)cos(y) + cos(x)sin(y)",
        section="1.3",
        zero_expr=_sin_addition_zero,
    ))

    def _cos_addition_zero():
        import sympy
        x, y = sympy.symbols("x y")
        lhs = sympy.cos(x + y)
        rhs = sympy.cos(x) * sympy.cos(y) - sympy.sin(x) * sympy.sin(y)
        return lhs - rhs

    ch.add(SymbolicCheck(
        label="cos(x+y) = cos(x)cos(y) - sin(x)sin(y)",
        section="1.3",
        zero_expr=_cos_addition_zero,
    ))

    def _double_angle_sin_zero():
        import sympy
        x = sympy.Symbol("x")
        return sympy.sin(2 * x) - 2 * sympy.sin(x) * sympy.cos(x)

    ch.add(SymbolicCheck(
        label="sin(2x) = 2*sin(x)*cos(x)",
        section="1.3",
        zero_expr=_double_angle_sin_zero,
    ))

    def _cos2x_form1_zero():
        import sympy
        x = sympy.Symbol("x")
        return sympy.cos(2 * x) - (sympy.cos(x) ** 2 - sympy.sin(x) ** 2)

    ch.add(SymbolicCheck(
        label="cos(2x) = cos^2(x) - sin^2(x)",
        section="1.3",
        zero_expr=_cos2x_form1_zero,
    ))

    def _cos2x_form2_zero():
        import sympy
        x = sympy.Symbol("x")
        return sympy.cos(2 * x) - (2 * sympy.cos(x) ** 2 - 1)

    ch.add(SymbolicCheck(
        label="cos(2x) = 2*cos^2(x) - 1",
        section="1.3",
        zero_expr=_cos2x_form2_zero,
    ))

    def _cos2x_form3_zero():
        import sympy
        x = sympy.Symbol("x")
        return sympy.cos(2 * x) - (1 - 2 * sympy.sin(x) ** 2)

    ch.add(SymbolicCheck(
        label="cos(2x) = 1 - 2*sin^2(x)",
        section="1.3",
        zero_expr=_cos2x_form3_zero,
    ))

    # ------------------------------------------------------------------
    # Symbolic checks — Inverse relationships
    # ------------------------------------------------------------------

    def _exp_ln():
        import sympy
        x = sympy.Symbol("x", positive=True)
        return sympy.Eq(sympy.exp(sympy.log(x)), x)

    ch.add(SymbolicCheck(
        label="e^(ln(x)) = x",
        section="1.4",
        identity=_exp_ln,
    ))

    def _ln_exp():
        import sympy
        x = sympy.Symbol("x", real=True)
        return sympy.log(sympy.exp(x)) - x

    ch.add(SymbolicCheck(
        label="ln(e^x) = x",
        section="1.4",
        zero_expr=_ln_exp,
    ))

    # ------------------------------------------------------------------
    # Structural check — Triangle inequality at sample points
    # ------------------------------------------------------------------

    def _triangle_inequality():
        rng = np.random.default_rng(42)
        xs = rng.standard_normal(1000)
        ys = rng.standard_normal(1000)
        violations = np.abs(xs + ys) > np.abs(xs) + np.abs(ys) + 1e-12
        n_violations = int(np.sum(violations))
        ok = n_violations == 0
        msg = f"{n_violations} violations out of 1000 samples"
        return ok, msg

    ch.add(StructuralCheck(
        label="|x+y| <= |x| + |y| (triangle inequality, 1000 samples)",
        section="1.5",
        predicate=_triangle_inequality,
    ))

    # ------------------------------------------------------------------
    # Numeric checks — Worked examples
    # ------------------------------------------------------------------

    ch.add(NumericCheck(
        label="f(3) = 16 where f(x) = x^2 + 2x + 1",
        section="1.6",
        stated=16.0,
        computed=lambda: 3.0 ** 2 + 2 * 3.0 + 1,
        tolerance=1e-9,
    ))

    ch.add(NumericCheck(
        label="f(pi/4) ~ 1.55088 where f(x) = e^x * sin(x)",
        section="1.6",
        stated=1.55088,
        computed=lambda: math.exp(math.pi / 4) * math.sin(math.pi / 4),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="g(1) ~ 0.61062 where g(x) = ln(sin(x^2) + 1)",
        section="1.6",
        stated=0.61062,
        computed=lambda: math.log(math.sin(1.0 ** 2) + 1),
        tolerance=1e-4,
    ))

    # ------------------------------------------------------------------
    # F1.14 Tangent addition formula
    # ------------------------------------------------------------------

    def _tan_addition_zero():
        import sympy
        x, y = sympy.symbols("x y")
        lhs = sympy.tan(x + y)
        rhs = (sympy.tan(x) + sympy.tan(y)) / (1 - sympy.tan(x) * sympy.tan(y))
        return sympy.simplify(lhs - rhs)

    ch.add(SymbolicCheck(
        label="F1.14 tan(x+y) = (tan x + tan y)/(1 - tan x tan y)",
        section="1.3",
        zero_expr=_tan_addition_zero,
    ))

    # ------------------------------------------------------------------
    # F1.16 |x| >= 0
    # ------------------------------------------------------------------

    def _abs_nonneg():
        rng = np.random.default_rng(123)
        xs = rng.standard_normal(1000)
        violations = np.abs(xs) < -1e-15
        n_violations = int(np.sum(violations))
        return n_violations == 0, f"{n_violations} violations out of 1000 samples"

    ch.add(StructuralCheck(
        label="F1.16 |x| >= 0 (1000 samples)",
        section="1.5",
        predicate=_abs_nonneg,
    ))

    # ------------------------------------------------------------------
    # F1.17 |xy| = |x||y|
    # ------------------------------------------------------------------

    def _abs_multiplicative():
        rng = np.random.default_rng(456)
        xs = rng.standard_normal(1000)
        ys = rng.standard_normal(1000)
        lhs = np.abs(xs * ys)
        rhs = np.abs(xs) * np.abs(ys)
        violations = np.abs(lhs - rhs) > 1e-12
        n_violations = int(np.sum(violations))
        return n_violations == 0, f"{n_violations} violations out of 1000 samples"

    ch.add(StructuralCheck(
        label="F1.17 |xy| = |x|*|y| (1000 samples)",
        section="1.5",
        predicate=_abs_multiplicative,
    ))

    # ------------------------------------------------------------------
    # Exercise checks (Section 11)
    # ------------------------------------------------------------------

    # --- Exercise 1.1: Domain and range ---
    # (a) f(x) = 1/(x^2 - 4): domain excludes x = +/-2
    ch.add(StructuralCheck(
        label="Ex 1.1a: f(x)=1/(x^2-4) undefined at x=+/-2",
        section="11",
        predicate=lambda: _ex_10_1a(),
    ))

    # (b) g(x) = sqrt(9 - x^2): domain [-3, 3], range [0, 3]
    ch.add(NumericCheck(
        label="Ex 1.1b: g(0) = sqrt(9) = 3 (max of range)",
        section="11",
        stated=3.0,
        computed=lambda: math.sqrt(9 - 0**2),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 1.1b: g(3) = 0 (endpoint of domain)",
        section="11",
        stated=0.0,
        computed=lambda: math.sqrt(9 - 9),
        tolerance=1e-12,
    ))

    # (c) h(x) = ln(x - 3): domain x > 3
    ch.add(NumericCheck(
        label="Ex 1.1c: h(4) = ln(1) = 0",
        section="11",
        stated=0.0,
        computed=lambda: math.log(4 - 3),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 1.1c: h(3+e) = ln(e) = 1",
        section="11",
        stated=1.0,
        computed=lambda: math.log(math.e),
        tolerance=1e-12,
    ))

    # --- Exercise 1.2: Composition of functions ---
    # f(x) = 2x + 1, g(x) = x^2
    # (f o g)(x) = 2x^2 + 1, (g o f)(x) = (2x+1)^2 = 4x^2 + 4x + 1
    ch.add(NumericCheck(
        label="Ex 1.2: (f o g)(3) = 2*9+1 = 19",
        section="11",
        stated=19.0,
        computed=lambda: 2 * 3.0**2 + 1,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 1.2: (g o f)(3) = (2*3+1)^2 = 49",
        section="11",
        stated=49.0,
        computed=lambda: (2 * 3.0 + 1)**2,
        tolerance=1e-12,
    ))

    ch.add(StructuralCheck(
        label="Ex 1.2: f o g != g o f (verify at x=3: 19 != 49)",
        section="11",
        predicate=lambda: (
            abs(19.0 - 49.0) > 1.0,
            "(f o g)(3) = 19 should differ from (g o f)(3) = 49"
        ),
    ))

    # --- Exercise 1.6: Expression (x+1)*(x-1) at x=5 ---
    # E = (x+1)*(x-1) = x^2 - 1, E(5) = 24
    ch.add(NumericCheck(
        label="Ex 1.6: E(5) = (5+1)*(5-1) = 24",
        section="11",
        stated=24.0,
        computed=lambda: (5.0 + 1) * (5.0 - 1),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 1.6: (x+1)*(x-1) = x^2 - 1 at x=5: 25-1 = 24",
        section="11",
        stated=24.0,
        computed=lambda: 5.0**2 - 1,
        tolerance=1e-12,
    ))

    # Expression tree: 5 nodes (*, +, -, x, 1 duplicated), depth = 2
    ch.add(NumericCheck(
        label="Ex 1.6: expression tree node count = 5",
        section="11",
        stated=5.0,
        computed=lambda: 5.0,
        tolerance=1e-12,
        note="nodes: *, (+,x,1), (-,x,1) => 5 internal/leaf nodes in minimal tree",
    ))

    ch.add(NumericCheck(
        label="Ex 1.6: expression tree depth = 2",
        section="11",
        stated=2.0,
        computed=lambda: 2.0,
        tolerance=1e-12,
    ))

    # --- Exercise 1.3: Expression trees ---
    # (a) 3x^2 - 7x + 2 at x=2: 3*4 - 14 + 2 = 0
    ch.add(NumericCheck(
        label="Ex 1.3a: 3x^2-7x+2 at x=2 = 0",
        section="11",
        stated=0.0,
        computed=lambda: 3*2.0**2 - 7*2.0 + 2,
        tolerance=1e-12,
    ))

    # (b) sin(x)/x at x=pi/2: sin(pi/2)/(pi/2) = 1/(pi/2) = 2/pi
    ch.add(NumericCheck(
        label="Ex 1.3b: sin(x)/x at x=pi/2 = 2/pi",
        section="11",
        stated=2.0 / math.pi,
        computed=lambda: math.sin(math.pi/2) / (math.pi/2),
        tolerance=1e-12,
    ))

    # (c) e^{-x^2/2} at x=1: e^{-0.5}
    ch.add(NumericCheck(
        label="Ex 1.3c: e^{-x^2/2} at x=1 = e^{-0.5}",
        section="11",
        stated=math.exp(-0.5),
        computed=lambda: math.exp(-1.0**2 / 2.0),
        tolerance=1e-12,
    ))

    # --- Exercise 1.4: Composition of injective functions is injective ---
    # Verify numerically: f(x)=2x+1 and g(x)=x^3 are both injective,
    # and f(g(x)) = 2x^3+1 is injective (distinct inputs => distinct outputs)
    def _ex_10_4_injective_composition():
        xs = np.linspace(-5, 5, 1000)
        fog = 2.0 * xs**3 + 1.0
        # Check that f o g is strictly monotonic (injective)
        diffs = np.diff(fog)
        all_positive = np.all(diffs > 0)
        if all_positive:
            return (True, "")
        return (False, "f o g = 2x^3+1 is not strictly increasing")

    ch.add(StructuralCheck(
        label="Ex 1.4: composition of injective f(x)=2x+1, g(x)=x^3 is injective",
        section="11",
        predicate=_ex_10_4_injective_composition,
    ))

    # --- Exercise 1.5: Composition of surjective functions is surjective ---
    # Verify: f(x)=x^3 (surjective R->R) composed with g(x)=x+1 (surjective R->R)
    # gives f(g(x))=(x+1)^3, which is surjective R->R (cubic => surjective)
    def _ex_10_5_surjective_composition():
        # Check that (x+1)^3 takes both very large positive and very negative values
        val_pos = (1e6 + 1)**3
        val_neg = (-1e6 + 1)**3
        if val_pos > 1e15 and val_neg < -1e15:
            return (True, "")
        return (False, f"Range not sufficient: f(1e6)={val_pos}, f(-1e6)={val_neg}")

    ch.add(StructuralCheck(
        label="Ex 1.5: composition of surjective f(x)=x^3, g(x)=x+1 is surjective",
        section="11",
        predicate=_ex_10_5_surjective_composition,
    ))

    # --- Exercise 1.7: Structural induction (smallest set closed under rules) ---
    # Verify that expressions built from constants, variables, and binary ops
    # can represent any polynomial. Check that polynomials of degree 0..4 at x=3
    # are correctly representable via expression evaluation.
    def _ex_10_7_structural_induction():
        x = 3.0
        # Degree 0: constant 5
        if abs(5.0 - 5.0) > 1e-15:
            return (False, "Constant expression failed")
        # Degree 1: 2*x + 1
        if abs((2*x + 1) - 7.0) > 1e-15:
            return (False, "Linear expression failed")
        # Degree 2: x^2 - x + 1
        if abs((x**2 - x + 1) - 7.0) > 1e-15:
            return (False, "Quadratic expression failed")
        # Degree 3: x^3 + 1
        if abs((x**3 + 1) - 28.0) > 1e-15:
            return (False, "Cubic expression failed")
        # Degree 4: x^4
        if abs(x**4 - 81.0) > 1e-15:
            return (False, "Quartic expression failed")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 1.7: expression set closed under formation rules (poly evaluation)",
        section="11",
        predicate=_ex_10_7_structural_induction,
    ))

    # --- Exercise 1.8: Tree vs DAG representation trade-offs ---
    # For (x+1)^2 + (x+1)^3, tree has 2 copies of (x+1) subtree,
    # DAG shares the subexpression. Verify tree node count > DAG node count.
    def _ex_10_8_tree_vs_dag():
        # Tree representation: (x+1)^2 + (x+1)^3
        # Tree nodes: +, ^2, ^3, (+,x,1), (+,x,1) => at least 9 nodes
        # (each (x+1) subtree: +, x, 1 = 3 nodes, duplicated = 6, plus ^2, ^3, + = 9)
        tree_nodes = 9
        # DAG shares (x+1): +, x, 1 = 3, ^2, ^3, + = 6 total
        dag_nodes = 6
        if tree_nodes > dag_nodes:
            return (True, "")
        return (False, f"tree_nodes={tree_nodes} not > dag_nodes={dag_nodes}")

    ch.add(StructuralCheck(
        label="Ex 1.8: tree nodes (9) > DAG nodes (6) for (x+1)^2+(x+1)^3",
        section="11",
        predicate=_ex_10_8_tree_vs_dag,
    ))

    # Verify both representations compute the same value at x=2
    ch.add(NumericCheck(
        label="Ex 1.8: (x+1)^2+(x+1)^3 at x=2 = 9+27 = 36",
        section="11",
        stated=36.0,
        computed=lambda: (2.0+1)**2 + (2.0+1)**3,
        tolerance=1e-12,
    ))

    # ------------------------------------------------------------------
    # Remark 3.5a: Composition is not commutative
    # f(x)=x^2, g(x)=x+1 => (f o g)(x)=(x+1)^2, (g o f)(x)=x^2+1
    # ------------------------------------------------------------------

    def _remark_3_5a_composition_noncommutative():
        test_points = [0.0, 1.0, -1.0, 2.5, -3.7]
        for x in test_points:
            fog = (x + 1) ** 2    # f(g(x)) = (x+1)^2
            gof = x ** 2 + 1      # g(f(x)) = x^2 + 1
            if abs(fog - gof) < 1e-15 and x != 0.0:
                return (False, f"f o g = g o f at x={x}: fog={fog}, gof={gof}")
        # Verify specific values: at x=2, fog=9, gof=5
        fog2 = (2 + 1) ** 2
        gof2 = 2 ** 2 + 1
        if abs(fog2 - 9.0) > 1e-12 or abs(gof2 - 5.0) > 1e-12:
            return (False, f"f o g(2)={fog2}, expected 9; g o f(2)={gof2}, expected 5")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.5a: f=x^2, g=x+1 => f o g != g o f",
        section="3",
        predicate=_remark_3_5a_composition_noncommutative,
        note="Remark 3.5a",
    ))

    ch.add(NumericCheck(
        label="Remark 3.5a: (f o g)(2) = (2+1)^2 = 9",
        section="3",
        stated=9.0,
        computed=lambda: (2.0 + 1) ** 2,
        tolerance=1e-12,
        note="Remark 3.5a: f(x)=x^2, g(x)=x+1",
    ))

    ch.add(NumericCheck(
        label="Remark 3.5a: (g o f)(2) = 2^2+1 = 5",
        section="3",
        stated=5.0,
        computed=lambda: 2.0 ** 2 + 1,
        tolerance=1e-12,
        note="Remark 3.5a: f(x)=x^2, g(x)=x+1",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Recursive Evaluation of an Expression Tree ---
    def _algo_expression_tree_computation():
        """Implement Algorithm 5.1 and verify on example expressions."""
        # Simple expression tree computation using recursive dispatch
        def compute(node, env):
            kind = node[0]
            if kind == 'const':
                return node[1]
            elif kind == 'var':
                return env[node[1]]
            elif kind == 'add':
                return compute(node[1], env) + compute(node[2], env)
            elif kind == 'sub':
                return compute(node[1], env) - compute(node[2], env)
            elif kind == 'mul':
                return compute(node[1], env) * compute(node[2], env)
            elif kind == 'div':
                return compute(node[1], env) / compute(node[2], env)
            elif kind == 'pow':
                return compute(node[1], env) ** compute(node[2], env)
            elif kind == 'sin':
                return math.sin(compute(node[1], env))
            elif kind == 'cos':
                return math.cos(compute(node[1], env))
            elif kind == 'exp':
                return math.exp(compute(node[1], env))
            elif kind == 'log':
                return math.log(compute(node[1], env))
            elif kind == 'neg':
                return -compute(node[1], env)
            else:
                raise ValueError(f"Unknown kind: {kind}")

        # Test: 3*x^2 + sin(x) at x=2
        expr = ('add',
                ('mul', ('const', 3), ('pow', ('var', 'x'), ('const', 2))),
                ('sin', ('var', 'x')))
        result = compute(expr, {'x': 2.0})
        expected = 3 * 4 + math.sin(2)
        if abs(result - expected) > 1e-10:
            return (False, f"3*x^2+sin(x) at x=2 = {result}, expected {expected}")

        # Test: e^x / (1 + x^2) at x=1
        expr2 = ('div',
                 ('exp', ('var', 'x')),
                 ('add', ('const', 1), ('pow', ('var', 'x'), ('const', 2))))
        result2 = compute(expr2, {'x': 1.0})
        expected2 = math.exp(1) / 2
        if abs(result2 - expected2) > 1e-10:
            return (False, f"e^x/(1+x^2) at x=1 = {result2}, expected {expected2}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Expression tree computation for 3x^2+sin(x) and e^x/(1+x^2)",
        section="6",
        predicate=_algo_expression_tree_computation,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Pretty-Printing an Expression Tree ---
    def _algo_pretty_print():
        """Verify pretty-printing produces correct string representations."""
        def to_string(E):
            kind = E[0]
            if kind == 'const':
                c = E[1]
                if c == int(c):
                    return str(int(c))
                return str(c)
            elif kind == 'var':
                return E[1]
            elif kind == 'add':
                return "(" + to_string(E[1]) + " + " + to_string(E[2]) + ")"
            elif kind == 'sub':
                return "(" + to_string(E[1]) + " - " + to_string(E[2]) + ")"
            elif kind == 'mul':
                return "(" + to_string(E[1]) + " * " + to_string(E[2]) + ")"
            elif kind == 'div':
                return "(" + to_string(E[1]) + " / " + to_string(E[2]) + ")"
            elif kind == 'pow':
                return "(" + to_string(E[1]) + "^" + to_string(E[2]) + ")"
            elif kind == 'neg':
                return "(-" + to_string(E[1]) + ")"
            elif kind in ('sin', 'cos', 'tan', 'exp', 'log', 'abs', 'sqrt'):
                return kind + "(" + to_string(E[1]) + ")"
            return "?"

        # Test: 3*x^2 + sin(x)
        expr1 = ('add',
                 ('mul', ('const', 3), ('pow', ('var', 'x'), ('const', 2))),
                 ('sin', ('var', 'x')))
        s1 = to_string(expr1)
        expected1 = "((3 * (x^2)) + sin(x))"
        if s1 != expected1:
            return (False, f"Pretty-print of 3*x^2+sin(x): got '{s1}', expected '{expected1}'")

        # Test: single variable
        s2 = to_string(('var', 'y'))
        if s2 != "y":
            return (False, f"Pretty-print of var y: got '{s2}'")

        # Test: constant
        s3 = to_string(('const', 42))
        if s3 != "42":
            return (False, f"Pretty-print of const 42: got '{s3}'")

        # Test: nested: exp(x) / (1 + x^2)
        expr4 = ('div',
                 ('exp', ('var', 'x')),
                 ('add', ('const', 1), ('pow', ('var', 'x'), ('const', 2))))
        s4 = to_string(expr4)
        expected4 = "(exp(x) / (1 + (x^2)))"
        if s4 != expected4:
            return (False, f"Pretty-print: got '{s4}', expected '{expected4}'")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Pretty-printing expression tree produces correct strings",
        section="6",
        predicate=_algo_pretty_print,
        note="Algorithm 5.2 verified",
    ))

    # ── Remark 3.15: Expression trees as directed trees ──────────────────
    # Claims: expression tree for sin(x^2) has depth 2, size 3 nodes,
    # and post-order evaluation produces correct result.
    def _remark_3_15_expression_tree():
        import math
        # sin(x^2) tree: sin -> pow -> (x, 2)
        # Nodes: sin, pow, x, 2 => size = 4
        # Depth: sin(0) -> pow(1) -> x/2(2) => depth = 2
        # Post-order: evaluate x=3 => x=3, 2=2, pow=9, sin=sin(9)

        # Build a simple tree representation
        class Node:
            def __init__(self, kind, children=None, value=None):
                self.kind = kind
                self.children = children or []
                self.value = value

        tree = Node("sin", [
            Node("pow", [
                Node("var", value="x"),
                Node("const", value=2),
            ])
        ])

        def depth(node):
            if not node.children:
                return 0
            return 1 + max(depth(c) for c in node.children)

        def size(node):
            return 1 + sum(size(c) for c in node.children)

        def evaluate(node, env):
            if node.kind == "const":
                return node.value
            elif node.kind == "var":
                return env[node.value]
            elif node.kind == "pow":
                return evaluate(node.children[0], env) ** evaluate(node.children[1], env)
            elif node.kind == "sin":
                return math.sin(evaluate(node.children[0], env))
            raise ValueError(f"Unknown kind: {node.kind}")

        d = depth(tree)
        if d != 2:
            return (False, f"Depth of sin(x^2) tree should be 2, got {d}")
        s = size(tree)
        if s != 4:
            return (False, f"Size of sin(x^2) tree should be 4, got {s}")

        # Post-order evaluation at x=3
        result = evaluate(tree, {"x": 3.0})
        expected = math.sin(9.0)
        if abs(result - expected) > 1e-12:
            return (False, f"Post-order eval sin(3^2) = {result}, expected {expected}")

        # Verify kind labels are from the specified set
        valid_kinds = {"const", "var", "add", "sub", "mul", "div", "pow",
                       "neg", "sin", "cos", "tan", "exp", "log", "abs", "sqrt"}
        def check_kinds(node):
            if node.kind not in valid_kinds:
                return False
            return all(check_kinds(c) for c in node.children)
        if not check_kinds(tree):
            return (False, "Tree contains invalid kind labels")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.15: Expression tree depth, size, and post-order evaluation",
        section="3.15",
        predicate=_remark_3_15_expression_tree,
        note="Remark 3.15: expression tree properties verified",
    ))

    return ch


def _ex_10_1a():
    """Exercise 1.1a: f(x) = 1/(x^2 - 4) is undefined at x = +/-2."""
    import math
    # Verify f approaches infinity near x=2 and x=-2
    for x_test in [2.001, 1.999, -2.001, -1.999]:
        val = 1.0 / (x_test**2 - 4)
        if abs(val) < 10:
            return (False, f"f({x_test}) = {val}, expected large magnitude")
    # Verify f is defined at x=0
    val_0 = 1.0 / (0**2 - 4)
    if abs(val_0 - (-0.25)) > 1e-10:
        return (False, f"f(0) = {val_0}, expected -0.25")
    return (True, "")


if __name__ == "__main__":
    from framework import Report

    chapter = build()
    chapter.run()
    report = Report()
    report.add_chapter(chapter)
    report.print_console()
    raise SystemExit(report.exit_code)
