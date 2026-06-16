# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 3: Limits & Continuity — verification."""

import math
import numpy as np
import scipy.optimize
from scipy.optimize import brentq
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(3, "Limits & Continuity")

    # ===================================================================
    # LAYER 1: Symbolic — fundamental limit identities
    # ===================================================================

    # --- lim sin(x)/x = 1 as x->0 ---
    ch.add(SymbolicCheck(
        label="lim sin(x)/x = 1 (symbolic)",
        section="5",
        identity=lambda: _sinx_over_x_limit(),
    ))

    # --- lim (1+1/n)^n = e ---
    ch.add(SymbolicCheck(
        label="lim (1+1/n)^n = e (symbolic)",
        section="5",
        identity=lambda: _compound_interest_limit(),
    ))

    # --- lim (e^x-1)/x = 1 ---
    ch.add(SymbolicCheck(
        label="lim (e^x-1)/x = 1 (symbolic)",
        section="5",
        identity=lambda: _exp_minus_1_limit(),
    ))

    # --- lim ln(1+x)/x = 1 ---
    ch.add(SymbolicCheck(
        label="lim ln(1+x)/x = 1 (symbolic)",
        section="5",
        identity=lambda: _ln_1_plus_x_limit(),
    ))

    # ===================================================================
    # LAYER 2: Numerical worked examples
    # ===================================================================

    # --- Example 3.18: sin(h)/h table ---
    for h, stated in [(0.1, 0.99833416646828), (1e-2, 0.99998333341667),
                       (1e-4, 0.99999999833333), (1e-8, 1.0)]:
        ch.add(NumericCheck(
            label=f"sin({h})/({h})",
            section="8.1",
            stated=stated,
            computed=math.sin(h) / h,
            tolerance=1e-10,
        ))

    # --- Example 3.19: root of x^3 - x - 1 on [1,2] ---
    root = brentq(lambda x: x**3 - x - 1, 1, 2, xtol=1e-14)
    ch.add(NumericCheck(
        label="Root of x^3-x-1 ~ 1.3247179572",
        section="8.2",
        stated=1.3247179572,
        computed=root,
        tolerance=1e-9,
    ))

    # Verify root satisfies equation
    ch.add(NumericCheck(
        label="f(root) ~ 0",
        section="8.2",
        stated=0.0,
        computed=root**3 - root - 1,
        tolerance=1e-10,
    ))

    # --- Example 3.20: removable discontinuity (x^2-1)/(x-1) -> 2 ---
    eps = 1e-10
    val = ((1 + eps)**2 - 1) / ((1 + eps) - 1)
    ch.add(NumericCheck(
        label="lim (x^2-1)/(x-1) at x=1 = 2",
        section="8.3",
        stated=2.0,
        computed=val,
        tolerance=1e-6,
    ))

    # --- F3.2: (1+1/n)^n convergence table ---
    table = [(1, 2.0), (2, 2.25), (5, 2.488), (10, 2.594),
             (50, 2.691), (100, 2.705), (1000, 2.717)]
    for n, stated in table:
        ch.add(NumericCheck(
            label=f"(1+1/{n})^{n} ~ {stated}",
            section="5",
            stated=stated,
            computed=(1 + 1/n)**n,
            tolerance=1e-3,
        ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- F3.5: x^n / e^x -> 0 as x -> inf (use log to avoid overflow) ---
    ch.add(StructuralCheck(
        label="x^10/e^x -> 0 as x->inf",
        section="5",
        predicate=lambda: (
            10 * math.log(1000) - 1000 < -900,  # log(1000^10/e^1000) ~ -930
            f"log(1000^10/e^1000) = {10*math.log(1000)-1000:.1f} not << 0"
        ),
    ))

    # --- F3.6: ln(x)/x^p -> 0 for p=1 ---
    ch.add(StructuralCheck(
        label="ln(x)/x -> 0 as x->inf",
        section="5",
        predicate=lambda: (
            math.log(1e6) / 1e6 < 1e-4,
            f"ln(1e6)/1e6 = {math.log(1e6)/1e6}"
        ),
    ))

    # --- Ex 8.4: Floor function jump discontinuity ---
    ch.add(StructuralCheck(
        label="Ex 8.4: floor(x) has jump discontinuity at integers",
        section="8.4",
        predicate=lambda: _floor_jump_discontinuity(),
        note="left limit != right limit at every integer",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 3.2: Limit evaluations ---
    # (a) lim x->2 (x^2 + 3x - 1) = 4 + 6 - 1 = 9
    ch.add(NumericCheck(
        label="Ex 3.2a: lim x->2 (x^2+3x-1) = 9",
        section="11",
        stated=9.0,
        computed=lambda: 2.0**2 + 3*2.0 - 1,
        tolerance=1e-12,
    ))

    # (b) lim x->1 (x^2+x)/(x+1) = (1+1)/(1+1) = 1
    ch.add(NumericCheck(
        label="Ex 3.2b: lim x->1 (x^2+x)/(x+1) = 1",
        section="11",
        stated=1.0,
        computed=lambda: (1.0**2 + 1.0) / (1.0 + 1.0),
        tolerance=1e-12,
    ))

    # (c) lim x->0 sin(3x)/x = 3
    ch.add(NumericCheck(
        label="Ex 3.2c: lim x->0 sin(3x)/x = 3",
        section="11",
        stated=3.0,
        computed=lambda: math.sin(3 * 1e-10) / 1e-10,
        tolerance=1e-4,
    ))

    ch.add(SymbolicCheck(
        label="Ex 3.2c: lim x->0 sin(3x)/x = 3 (symbolic)",
        section="11",
        identity=lambda: _ex_10_2c_symbolic(),
    ))

    # --- Exercise 3.3: Continuity classification ---
    # (a) f(x) = (x^2-4)/(x-2): removable discontinuity at x=2, limit = 4
    ch.add(NumericCheck(
        label="Ex 3.3a: lim x->2 (x^2-4)/(x-2) = 4 (removable)",
        section="11",
        stated=4.0,
        computed=lambda: ((2.0 + 1e-10)**2 - 4) / ((2.0 + 1e-10) - 2),
        tolerance=1e-4,
    ))

    # (b) g(x): jump discontinuity at x=2 (left limit=3, function value=5)
    ch.add(NumericCheck(
        label="Ex 3.3b: g(2) = 5, but lim x->2 (x+1) = 3 (removable)",
        section="11",
        stated=3.0,
        computed=lambda: 2.0 + 1.0,
        tolerance=1e-12,
        note="g(2)=5 but limit from both sides is 3, so removable discontinuity",
    ))

    # (c) h(x): jump discontinuity at x=2 (left limit=3, right limit=4)
    ch.add(NumericCheck(
        label="Ex 3.3c: h(2-) = 2+1 = 3, h(2+) = 4 (jump)",
        section="11",
        stated=3.0,
        computed=lambda: 2.0 + 1.0,
        tolerance=1e-12,
        note="Left limit: x+1 at x=2 gives 3",
    ))

    ch.add(NumericCheck(
        label="Ex 3.3c: h(2+) = 2^2 = 4 (jump discontinuity)",
        section="11",
        stated=4.0,
        computed=lambda: 2.0**2,
        tolerance=1e-12,
        note="Right limit: x^2 at x=2 gives 4",
    ))

    # --- Exercise 3.4: Squeeze theorem ---
    # lim x->0 x^2*sin(1/x) = 0
    ch.add(NumericCheck(
        label="Ex 3.4: lim x->0 x^2*sin(1/x) = 0 (squeeze theorem)",
        section="11",
        stated=0.0,
        computed=lambda: (1e-8)**2 * math.sin(1.0 / 1e-8),
        tolerance=1e-10,
    ))

    ch.add(StructuralCheck(
        label="Ex 3.4: |x^2*sin(1/x)| <= x^2 for all x != 0",
        section="11",
        predicate=lambda: _ex_10_4_squeeze(),
    ))

    # --- Exercise 3.6: Bisection method on e^x - 3x on [0,1] ---
    ch.add(NumericCheck(
        label="Ex 3.6: f(0) = e^0 - 0 = 1 > 0",
        section="11",
        stated=1.0,
        computed=lambda: math.exp(0) - 3*0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 3.6: f(1) = e - 3 ~ -0.2817 < 0",
        section="11",
        stated=math.e - 3,
        computed=lambda: math.exp(1) - 3*1,
        tolerance=1e-10,
    ))

    # Bisection steps
    ch.add(NumericCheck(
        label="Ex 3.6: bisection step 1 midpoint = 0.5",
        section="11",
        stated=0.5,
        computed=lambda: (0.0 + 1.0) / 2.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 3.6: f(0.5) = e^0.5 - 1.5 ~ 0.1487",
        section="11",
        stated=math.exp(0.5) - 1.5,
        computed=lambda: math.exp(0.5) - 3*0.5,
        tolerance=1e-10,
    ))

    # After 4 bisection steps, root ~ brentq result
    _root_ex106 = brentq(lambda x: math.exp(x) - 3*x, 0, 1, xtol=1e-14)
    ch.add(NumericCheck(
        label="Ex 3.6: root of e^x - 3x ~ 0.6191",
        section="11",
        stated=0.6191,
        computed=_root_ex106,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 3.6: f(root) ~ 0",
        section="11",
        stated=0.0,
        computed=math.exp(_root_ex106) - 3*_root_ex106,
        tolerance=1e-10,
    ))

    # --- Exercise 3.1: epsilon-delta proof lim_{x->3} (2x+1) = 7 ---
    # For any eps, delta = eps/2 works: |x-3| < eps/2 => |(2x+1)-7| = 2|x-3| < eps
    def _ex_10_1_epsilon_delta():
        for eps in [1.0, 0.1, 0.01, 0.001, 1e-6]:
            delta = eps / 2.0
            # Test several x near 3 within delta
            for x_test in [3 + delta * 0.5, 3 - delta * 0.5, 3 + delta * 0.99]:
                if abs(x_test - 3) < delta:
                    if abs((2*x_test + 1) - 7) >= eps:
                        return (False, f"eps={eps}, x={x_test}: |(2x+1)-7| = {abs((2*x_test+1)-7)} >= {eps}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 3.1: eps-delta for lim_{x->3}(2x+1)=7, delta=eps/2",
        section="11",
        predicate=_ex_10_1_epsilon_delta,
    ))

    # --- Exercise 3.5: sign preservation of continuous functions ---
    # If f is continuous at a and f(a)>0, then f(x)>0 near a.
    # Verify for f(x) = 1+sin(x) at a=0: f(0)=1>0, f(x)>0 on (-pi/2, pi/2)
    def _ex_10_5_sign_preservation():
        a = 0.0
        f_a = 1 + math.sin(a)
        if f_a <= 0:
            return (False, f"f(0) = {f_a} not > 0")
        # Check f(x) > 0 on a neighborhood
        delta = 1.0  # within (-1, 1)
        for x_test in np.linspace(a - delta, a + delta, 100):
            f_x = 1 + math.sin(x_test)
            if f_x <= 0:
                return (False, f"f({x_test}) = {f_x} <= 0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 3.5: sign preservation for f(x)=1+sin(x) at a=0",
        section="11",
        predicate=_ex_10_5_sign_preservation,
    ))

    # --- Exercise 3.7: uniform continuity on [0,1] vs not on R ---
    # f(x) = x^2 on [0,1]: for eps>0, delta=eps/2 works (since |x+y|<=2)
    # f(x) = x^2 on R: for eps=1, no single delta works for all pairs
    def _ex_10_7_uniform_continuity():
        # Part 1: f(x)=x^2 is uniformly continuous on [0,1]
        eps = 0.1
        delta = eps / 2.0  # works because |x+y| <= 2 on [0,1]
        for x_val in np.linspace(0, 1, 50):
            for y_val in np.linspace(0, 1, 50):
                if abs(x_val - y_val) < delta:
                    if abs(x_val**2 - y_val**2) >= eps:
                        return (False, f"Uniform cont failed on [0,1]: x={x_val}, y={y_val}")

        # Part 2: f(x)=x^2 is NOT uniformly continuous on R
        # For eps=1, show that for any delta, we can find x, y with |x-y|<delta but |x^2-y^2|>=1
        for delta_test in [0.1, 0.01, 0.001]:
            n = 1.0 / delta_test  # large n
            x_test = n
            y_test = n + delta_test / 2
            diff = abs(x_test**2 - y_test**2)
            if diff < 1.0:
                return (False, f"Expected |x^2-y^2| >= 1 at x={x_test}, got {diff}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 3.7: x^2 uniformly continuous on [0,1], not on R",
        section="11",
        predicate=_ex_10_7_uniform_continuity,
    ))

    # --- Exercise 3.8: sin(1/x) has essential discontinuity at 0 ---
    # sin(1/x) takes every value in [-1,1] in every neighborhood of 0
    def _ex_10_8_essential_discontinuity():
        # Show that in (0, delta) for any delta, sin(1/x) attains both +1 and -1
        for delta in [0.1, 0.01, 0.001]:
            # sin(1/x) = 1 when 1/x = pi/2 + 2k*pi, i.e., x = 1/(pi/2 + 2k*pi)
            # Find k such that x < delta
            found_plus1 = False
            found_minus1 = False
            for k in range(1, 10000):
                x_plus = 1.0 / (math.pi/2 + 2*k*math.pi)
                x_minus = 1.0 / (3*math.pi/2 + 2*k*math.pi)
                if 0 < x_plus < delta:
                    if abs(math.sin(1.0/x_plus) - 1.0) < 1e-10:
                        found_plus1 = True
                if 0 < x_minus < delta:
                    if abs(math.sin(1.0/x_minus) - (-1.0)) < 1e-10:
                        found_minus1 = True
                if found_plus1 and found_minus1:
                    break
            if not (found_plus1 and found_minus1):
                return (False, f"delta={delta}: +1 found={found_plus1}, -1 found={found_minus1}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 3.8: sin(1/x) attains +1 and -1 in every neighborhood of 0",
        section="11",
        predicate=_ex_10_8_essential_discontinuity,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Numerical Limit Evaluation by Successive Approximation ---
    def _algo_numerical_limit():
        """Implement Algorithm 5.1 and verify on known limits."""
        def evaluate_limit(f, a, direction='both', k=8):
            values = []
            for i in range(1, k + 1):
                h = 10.0 ** (-i)
                if direction in ('right', 'both'):
                    val_right = f(a + h)
                if direction in ('left', 'both'):
                    val_left = f(a - h)
                if direction == 'both':
                    values.append((val_right + val_left) / 2)
                elif direction == 'right':
                    values.append(val_right)
                else:
                    values.append(val_left)
            return values[-1]

        # lim x->0 sin(x)/x = 1
        val = evaluate_limit(lambda x: math.sin(x) / x, 0)
        if abs(val - 1.0) > 1e-8:
            return (False, f"lim sin(x)/x = {val}, expected 1.0")

        # lim x->0 (e^x - 1)/x = 1
        val = evaluate_limit(lambda x: (math.exp(x) - 1) / x, 0)
        if abs(val - 1.0) > 1e-8:
            return (False, f"lim (e^x-1)/x = {val}, expected 1.0")

        # lim x->1 (x^2-1)/(x-1) = 2
        val = evaluate_limit(lambda x: (x ** 2 - 1) / (x - 1), 1)
        if abs(val - 2.0) > 1e-6:
            return (False, f"lim (x^2-1)/(x-1) = {val}, expected 2.0")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Numerical limit evaluation converges for sin(x)/x, (e^x-1)/x, (x^2-1)/(x-1)",
        section="6",
        predicate=_algo_numerical_limit,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Bisection Method for Root-Finding ---
    def _algo_bisection():
        """Implement Algorithm 5.2 and verify against scipy.optimize.brentq."""
        def bisect(f, a, b, tolerance=1e-12):
            if f(a) * f(b) >= 0:
                return None
            max_iter = math.ceil(math.log2((b - a) / tolerance))
            for _ in range(max_iter):
                m = (a + b) / 2
                if f(m) == 0:
                    return m
                if f(a) * f(m) < 0:
                    b = m
                else:
                    a = m
            return (a + b) / 2

        # Root of x^3 - x - 1 on [1, 2]
        f1 = lambda x: x ** 3 - x - 1
        root1 = bisect(f1, 1, 2)
        ref1 = scipy.optimize.brentq(f1, 1, 2)
        if abs(root1 - ref1) > 1e-10:
            return (False, f"x^3-x-1 root: bisect={root1}, scipy={ref1}")

        # Root of e^x - 3x on [0, 1]
        f2 = lambda x: math.exp(x) - 3 * x
        root2 = bisect(f2, 0, 1)
        ref2 = scipy.optimize.brentq(f2, 0, 1)
        if abs(root2 - ref2) > 1e-10:
            return (False, f"e^x-3x root: bisect={root2}, scipy={ref2}")

        # Root of cos(x) - x on [0, pi/2]
        f3 = lambda x: math.cos(x) - x
        root3 = bisect(f3, 0, math.pi / 2)
        ref3 = scipy.optimize.brentq(f3, 0, math.pi / 2)
        if abs(root3 - ref3) > 1e-10:
            return (False, f"cos(x)-x root: bisect={root3}, scipy={ref3}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Bisection root-finding matches scipy.brentq on 3 test functions",
        section="6",
        predicate=_algo_bisection,
        note="Algorithm 5.2 verified",
    ))

    # ==================================================================
    # Theorem 3.17: L'Hopital's rule examples
    # ==================================================================

    import math as _math

    # sin(x)/x -> 1 as x -> 0 (0/0 form)
    ch.add(NumericCheck(
        label="Theorem 3.17: lim x->0 sin(x)/x = 1 (L'Hopital: cos(0)/1 = 1)",
        section="3",
        stated=1.0,
        computed=lambda: _math.cos(0.0) / 1.0,
        tolerance=1e-15,
        note="Theorem 3.17: 0/0 form, f'/g' = cos(x)/1 at x=0",
    ))

    # x^x -> 1 as x -> 0+ (0^0 form)
    def _theorem_3_17_zero_to_zero():
        # x^x = exp(x*ln(x)); x*ln(x) -> 0 as x -> 0+
        # Verify numerically
        vals = [0.1, 0.01, 0.001, 0.0001]
        for x in vals:
            pass
        # At x=0.0001: x^x should be close to 1
        val = 0.0001 ** 0.0001
        if abs(val - 1.0) > 0.01:
            return (False, f"0.0001^0.0001 = {val}, expected ~1.0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Theorem 3.17: lim x->0+ x^x = 1 (0^0 form)",
        section="3",
        predicate=_theorem_3_17_zero_to_zero,
        note="Theorem 3.17: 0^0 indeterminate form",
    ))

    # (1+1/x)^x -> e as x -> inf (1^inf form)
    def _theorem_3_17_one_to_inf():
        vals = [10, 100, 1000, 10000, 100000]
        for x in vals:
            pass
        val = (1 + 1.0 / 100000) ** 100000
        if abs(val - _math.e) > 0.001:
            return (False, f"(1+1/100000)^100000 = {val}, expected {_math.e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Theorem 3.17: lim x->inf (1+1/x)^x = e (1^inf form)",
        section="3",
        predicate=_theorem_3_17_one_to_inf,
        note="Theorem 3.17: 1^inf indeterminate form",
    ))

    return ch


# ---------------------------------------------------------------------------
# Exercise helpers
# ---------------------------------------------------------------------------

def _ex_10_2c_symbolic():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.Eq(sp.limit(sp.sin(3*x)/x, x, 0), 3)


def _ex_10_4_squeeze():
    """Verify |x^2*sin(1/x)| <= x^2 for sample x values."""
    import math
    for x_val in [0.1, 0.01, 0.001, 0.0001, -0.1, -0.01]:
        if x_val == 0:
            continue
        lhs = abs(x_val**2 * math.sin(1.0/x_val))
        rhs = x_val**2
        if lhs > rhs + 1e-15:
            return (False, f"|x^2*sin(1/x)| = {lhs} > x^2 = {rhs} at x={x_val}")
    return (True, "")


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _sinx_over_x_limit():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.Eq(sp.limit(sp.sin(x)/x, x, 0), 1)


def _compound_interest_limit():
    import sympy as sp
    n = sp.Symbol('n', positive=True)
    return sp.Eq(sp.limit((1 + 1/n)**n, n, sp.oo), sp.E)


def _exp_minus_1_limit():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.Eq(sp.limit((sp.exp(x) - 1)/x, x, 0), 1)


def _ln_1_plus_x_limit():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.Eq(sp.limit(sp.ln(1 + x)/x, x, 0), 1)


def _floor_jump_discontinuity():
    """Verify floor(x) has a jump discontinuity at each integer n in [1..5].
    Left limit: floor(n - eps) = n - 1, right limit: floor(n + eps) = n.
    """
    eps = 1e-10
    for n in range(1, 6):
        left_val = math.floor(n - eps)
        right_val = math.floor(n + eps)
        if left_val != n - 1:
            return (False, f"floor({n} - eps) = {left_val}, expected {n - 1}")
        if right_val != n:
            return (False, f"floor({n} + eps) = {right_val}, expected {n}")
        if left_val == right_val:
            return (False, f"No jump at n={n}: left={left_val}, right={right_val}")
    return (True, "")
