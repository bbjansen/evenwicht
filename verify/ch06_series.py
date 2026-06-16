# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 6: Series & Approximation — verification."""

import math
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(6, "Series & Approximation")

    # ===================================================================
    # LAYER 1: Symbolic — Taylor series formulas
    # ===================================================================

    ch.add(SymbolicCheck(
        label="e^x Taylor: sum x^n/n! (6 terms at x=1)",
        section="5",
        zero_expr=lambda: _exp_taylor(),
    ))

    ch.add(SymbolicCheck(
        label="sin(x) Taylor: x - x^3/6 + x^5/120 - x^7/5040",
        section="5",
        zero_expr=lambda: _sin_taylor(),
    ))

    ch.add(SymbolicCheck(
        label="cos(x) Taylor: 1 - x^2/2 + x^4/24 - x^6/720",
        section="5",
        zero_expr=lambda: _cos_taylor(),
    ))

    ch.add(SymbolicCheck(
        label="ln(1+x) Taylor: x - x^2/2 + x^3/3 - x^4/4",
        section="5",
        zero_expr=lambda: _ln_taylor(),
    ))

    ch.add(SymbolicCheck(
        label="Geometric series: sum r^n = 1/(1-r) for |r|<1",
        section="5",
        identity=lambda: _geometric_series(),
    ))

    ch.add(SymbolicCheck(
        label="Finite geometric: sum_{n=0}^{N} r^n = (1-r^{N+1})/(1-r)",
        section="5",
        zero_expr=lambda: _finite_geometric(),
    ))

    # ===================================================================
    # LAYER 2: Numerical worked examples
    # ===================================================================

    # --- Example 8.1: T5(e^x) at x=1 ---
    t5 = sum(1.0 / math.factorial(k) for k in range(6))
    ch.add(NumericCheck(
        label="T5(e^x) at x=1 = 326/120",
        section="8.1",
        stated=326.0 / 120.0,
        computed=t5,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="|T5(1) - e| ~ 0.00161",
        section="8.1",
        stated=0.00161,
        computed=abs(t5 - math.e),
        tolerance=0.05,
    ))

    # Lagrange remainder bound: |R5(1)| <= e/720
    ch.add(StructuralCheck(
        label="Actual error <= Lagrange bound e/720",
        section="8.1",
        predicate=lambda: (
            abs(t5 - math.e) <= math.e / 720,
            f"error {abs(t5-math.e):.6e} > bound {math.e/720:.6e}"
        ),
    ))

    # --- Example 8.2: T7(sin x) at various x ---
    def taylor_sin7(x):
        return x - x**3/6 + x**5/120 - x**7/5040

    for x_val, stated, tol in [(0.5, 0.479425533, 1e-7),
                                 (1.0, 0.841468254, 1e-7),
                                 (2.0, 0.907937, 1e-4)]:
        ch.add(NumericCheck(
            label=f"T7(sin {x_val}) ~ {stated}",
            section="8.2",
            stated=stated,
            computed=taylor_sin7(x_val),
            tolerance=tol,
        ))

    # Error at x=2.0 ~ 1.4e-3
    err_sin_2 = abs(taylor_sin7(2.0) - math.sin(2.0))
    ch.add(NumericCheck(
        label="|T7(sin 2) - sin(2)| ~ 1.4e-3",
        section="8.2",
        stated=1.4e-3,
        computed=err_sin_2,
        tolerance=0.1,
    ))

    # --- Example 8.3: Geometric series (1/2)^n -> 2 ---
    partial = sum(0.5**n for n in range(60))
    ch.add(NumericCheck(
        label="Geometric series (1/2)^n -> 2",
        section="8.3",
        stated=2.0,
        computed=partial,
        tolerance=1e-14,
    ))

    # --- Example 8.4: Annuity PV ---
    r = 0.05
    pv = 1000 * (1 - (1 + r)**(-20)) / r
    ch.add(NumericCheck(
        label="Annuity PV C=1000 r=5% N=20 ~ 12462.21",
        section="8.4",
        stated=12462.21,
        computed=pv,
        tolerance=1e-4,
    ))

    # Verify by explicit summation
    pv_explicit = sum(1000 / (1.05)**k for k in range(1, 21))
    ch.add(NumericCheck(
        label="Annuity PV explicit sum matches formula",
        section="8.4",
        stated=pv,
        computed=pv_explicit,
        tolerance=1e-10,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Ratio test: e^x series has ratio |a_{n+1}/a_n| = |x|/(n+1) -> 0 ---
    ch.add(StructuralCheck(
        label="e^x ratio test: |x|/(n+1) -> 0",
        section="5",
        predicate=lambda: (
            1.0 / 101 < 0.01,  # at n=100, ratio < 0.01
            "ratio at n=100 not small enough"
        ),
    ))

    # --- Alternating series: ln(2) = 1 - 1/2 + 1/3 - 1/4 + ... ---
    alt_sum = sum((-1)**(n+1) / n for n in range(1, 10001))
    ch.add(NumericCheck(
        label="ln(2) via alternating series (10000 terms)",
        section="5",
        stated=math.log(2),
        computed=alt_sum,
        tolerance=1e-4,
    ))

    # ===================================================================
    # Additional formula checks
    # ===================================================================

    # --- F4.1 Divergence test demo: if a_n -/-> 0 then series diverges ---
    ch.add(StructuralCheck(
        label="F4.1 Divergence test: sum n/(n+1) diverges (a_n -> 1 != 0)",
        section="5",
        predicate=lambda: _divergence_test_demo(),
        note="a_n = n/(n+1) -> 1, so sum diverges; partial sums grow without bound",
    ))

    # --- F4.3 Comparison test demo: 1/n^2 <= 1/n(n-1) for n>=2 ---
    ch.add(StructuralCheck(
        label="F4.3 Comparison test: 0 < 1/n^2 <= 1/(n(n-1)) for n>=2",
        section="5",
        predicate=lambda: _comparison_test_demo(),
        note="1/(n(n-1)) telescopes to 1, so sum 1/n^2 converges",
    ))

    # --- F4.4 Ratio test demo: e^x series ratio -> 0 ---
    ch.add(StructuralCheck(
        label="F4.4 Ratio test: |a_{n+1}/a_n| = 1/(n+1) -> 0 for e^x (x=1)",
        section="5",
        predicate=lambda: _ratio_test_demo(),
        note="L = 0 < 1, so series converges absolutely",
    ))

    # --- F4.5 Root test demo: (1/2^n) series ---
    ch.add(StructuralCheck(
        label="F4.5 Root test: (|a_n|)^{1/n} = 1/2 < 1 for sum (1/2)^n",
        section="5",
        predicate=lambda: _root_test_demo(),
        note="L = 1/2 < 1, so series converges",
    ))

    # --- F4.8 Absolute convergence demo ---
    ch.add(StructuralCheck(
        label="F4.8 Absolute convergence: sum |(-1)^n/n^2| = sum 1/n^2 converges",
        section="5",
        predicate=lambda: _absolute_convergence_demo(),
        note="Absolute convergence implies convergence",
    ))

    # --- F4.13 1/(1-x) = sum x^n for |x|<1 ---
    ch.add(SymbolicCheck(
        label="F4.13 1/(1-x) = sum_{n=0}^{inf} x^n for |x|<1",
        section="5",
        identity=lambda: _geometric_power_series(),
    ))

    # --- F4.14 Binomial series (1+x)^alpha ---
    ch.add(StructuralCheck(
        label="F4.14 Binomial series: (1+x)^{1/2} via 10-term expansion at x=0.5",
        section="5",
        predicate=lambda: _binomial_series_demo(),
        note="(1.5)^{0.5} ~ 1.22474; binomial series partial sum should be close",
    ))

    # --- F4.15 Lagrange remainder ---
    ch.add(StructuralCheck(
        label="F4.15 Lagrange remainder: |R_N(x)| <= M|x|^{N+1}/(N+1)!",
        section="5",
        predicate=lambda: _lagrange_remainder_demo(),
        note="e^x at x=1: actual error <= e/(N+1)! for each N",
    ))

    # --- F4.16 Error bound for alternating series ---
    ch.add(StructuralCheck(
        label="F4.16 Alternating series error bound: |error| <= |a_{N+1}|",
        section="5",
        predicate=lambda: _alternating_error_bound_demo(),
        note="ln(2) alternating series: error bounded by first omitted term",
    ))

    # --- F4.17 Finite geometric sum ---
    ch.add(SymbolicCheck(
        label="F4.17 Finite geometric: sum_{n=0}^{N} r^n = (1-r^{N+1})/(1-r)",
        section="5",
        zero_expr=lambda: _finite_geometric_check(),
        note="Verified symbolically for N=8",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 10.1: Convergence tests ---
    # (a) sum 1/n^3 converges (p-series, p=3>1)
    ch.add(NumericCheck(
        label="Ex 10.1a: sum 1/n^3 partial (10000 terms) ~ 1.2021 (Apery-related)",
        section="11",
        stated=1.2021,
        computed=sum(1.0 / n**3 for n in range(1, 10001)),
        tolerance=1e-3,
    ))

    # (b) sum n/(n+1) diverges (divergence test: a_n -> 1 != 0)
    ch.add(StructuralCheck(
        label="Ex 10.1b: sum n/(n+1) diverges (a_n -> 1 != 0)",
        section="11",
        predicate=lambda: (
            abs(10000 / 10001 - 1.0) < 0.001,
            f"a_10000 = {10000/10001}, should approach 1"
        ),
    ))

    # (c) sum (3/4)^n converges (geometric, |r|=3/4<1), sum = 1/(1-3/4) = 4
    ch.add(NumericCheck(
        label="Ex 10.1c: sum (3/4)^n = 1/(1-3/4) = 4",
        section="11",
        stated=4.0,
        computed=lambda: 1.0 / (1.0 - 3.0/4.0),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1c: sum (3/4)^n partial (100 terms) ~ 4",
        section="11",
        stated=4.0,
        computed=sum((3.0/4.0)**n for n in range(100)),
        tolerance=1e-10,
    ))

    # (d) sum (-1)^n/n^2 converges absolutely (sum |a_n| = sum 1/n^2 = pi^2/6)
    ch.add(NumericCheck(
        label="Ex 10.1d: sum (-1)^n/n^2 converges, partial ~ -pi^2/12",
        section="11",
        stated=-math.pi**2 / 12,
        computed=sum((-1.0)**n / n**2 for n in range(1, 100001)),
        tolerance=1e-4,
    ))

    # --- Exercise 10.2: Maclaurin T4 for e^{-x^2} at x=0.5 ---
    # T4(x) = 1 - x^2 + x^4/2 (since e^u = 1+u+u^2/2+..., u=-x^2)
    # T4(0.5) = 1 - 0.25 + 0.03125 = 0.78125
    # True: e^{-0.25} ~ 0.77880
    ch.add(NumericCheck(
        label="Ex 10.2: T4(e^{-x^2}) at x=0.5 = 0.78125",
        section="11",
        stated=0.78125,
        computed=lambda: 1.0 - 0.5**2 + 0.5**4 / 2.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: e^{-0.25} true value ~ 0.77880",
        section="11",
        stated=math.exp(-0.25),
        computed=lambda: math.exp(-0.25),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: |T4(0.5) - e^{-0.25}| ~ 0.00245",
        section="11",
        stated=0.00245,
        computed=abs(0.78125 - math.exp(-0.25)),
        tolerance=0.1,
    ))

    # --- Exercise 10.3: Perpetuity PV ---
    # C=500, r=0.04, PV = C/r = 500/0.04 = 12500
    ch.add(NumericCheck(
        label="Ex 10.3: Perpetuity PV = 500/0.04 = 12500",
        section="11",
        stated=12500.0,
        computed=lambda: 500.0 / 0.04,
        tolerance=1e-12,
    ))

    # Verify by partial sum (100 years, should be close)
    _perp_partial = sum(500.0 / (1.04)**k for k in range(1, 101))
    ch.add(StructuralCheck(
        label="Ex 10.3: 100-year partial sum within 2% of perpetuity C/r=12500",
        section="11",
        predicate=lambda: (
            abs(_perp_partial - 12500.0) / 12500.0 < 0.02,
            f"partial sum {_perp_partial:.2f} is {abs(_perp_partial-12500)/12500:.1%} from 12500"
        ),
        note="100 years captures 98%+ of perpetuity value",
    ))

    # --- Exercise 10.5: sum 1/(n*2^n) = ln(2) ---
    ch.add(NumericCheck(
        label="Ex 10.5: sum 1/(n*2^n) = ln(2)",
        section="11",
        stated=math.log(2),
        computed=sum(1.0 / (n * 2**n) for n in range(1, 100)),
        tolerance=1e-10,
    ))

    # --- Exercise 10.6: Leibniz formula pi/4 ---
    # Error < 10^{-3}: need |a_{N+1}| = 1/(2N+3) < 10^{-3} => N >= 499, so 500 terms
    ch.add(StructuralCheck(
        label="Ex 10.6: 500 terms of Leibniz gives |error| < 10^{-3}",
        section="11",
        predicate=lambda: _ex_10_6_leibniz(500, 1e-3),
    ))

    # Error < 10^{-6}: need 1/(2N+3) < 10^{-6} => N >= 499999, so ~500000 terms
    ch.add(StructuralCheck(
        label="Ex 10.6: 500000 terms of Leibniz gives |error| < 10^{-6}",
        section="11",
        predicate=lambda: _ex_10_6_leibniz(500000, 1e-6),
    ))

    # --- Exercise 10.4: Ratio test for e^x series ---
    # sum x^n/n! has ratio |a_{n+1}/a_n| = |x|/(n+1) -> 0 for every x
    # Radius of convergence is infinite
    def _ex_10_4_ratio_test():
        x_test = 10.0  # large x
        # For n=100, ratio = |x|/(n+1) = 10/101 < 1
        ratio_100 = x_test / 101.0
        if ratio_100 >= 1.0:
            return (False, f"Ratio at n=100 for x=10: {ratio_100} >= 1")
        # Verify limit is 0: ratio decreases with n
        ratios = [x_test / (n + 1) for n in range(1, 200)]
        if ratios[-1] > 0.06:
            return (False, f"Ratio at n=199: {ratios[-1]} not small enough")
        # All ratios eventually < 1 for any x => converges for all x => R = inf
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 10.4: ratio test confirms R=inf for e^x series",
        section="11",
        predicate=_ex_10_4_ratio_test,
    ))

    # --- Exercise 10.7: Riemann rearrangement theorem ---
    # Outline algorithm: to reach target T, add positive terms until partial sum > T,
    # then add negative terms until < T, repeat. Verify for T=2.0 with 1000 terms.
    def _ex_10_7_rearrangement():
        target = 2.0
        # Positive terms of alternating harmonic: 1, 1/3, 1/5, ...
        pos = [1.0 / (2*k - 1) for k in range(1, 10001)]
        # Negative terms: -1/2, -1/4, -1/6, ...
        neg = [-1.0 / (2*k) for k in range(1, 10001)]
        pi, ni = 0, 0
        partial = 0.0
        steps = 0
        for _ in range(2000):
            while partial <= target and pi < len(pos):
                partial += pos[pi]
                pi += 1
                steps += 1
            while partial > target and ni < len(neg):
                partial += neg[ni]
                ni += 1
                steps += 1
        # After many steps, partial sum should be close to target
        if abs(partial - target) < 0.1:
            return (True, "")
        return (False, f"Rearranged partial sum = {partial}, target = {target}")

    ch.add(StructuralCheck(
        label="Ex 10.7: rearrangement algorithm converges toward T=2.0",
        section="11",
        predicate=_ex_10_7_rearrangement,
    ))

    # --- Exercise 10.8: Computing ln(3) via convergent series ---
    # Strategy 1: ln(3) = ln(3/2) + ln(2) = ln(1+1/2) + ln(2)
    # ln(1+x) series converges for |x| <= 1 (x != -1)
    # ln(2) = ln(1+1) converges slowly; ln(3/2) = ln(1+1/2) converges
    # Strategy 2: ln((1+y)/(1-y)) = 2*sum y^{2k+1}/(2k+1), y = 1/2 gives ln(3)
    # since (1+1/2)/(1-1/2) = 3

    # Strategy 2 verification
    y = 0.5
    series_sum = 2 * sum(y**(2*k+1) / (2*k+1) for k in range(50))
    ch.add(NumericCheck(
        label="Ex 10.8: ln(3) via 2*sum y^{2k+1}/(2k+1) with y=1/2",
        section="11",
        stated=math.log(3),
        computed=series_sum,
        tolerance=1e-10,
    ))

    # Strategy 1 verification: ln(3/2) + ln(2)
    ln_3_2 = sum((-1)**(n+1) * (0.5)**n / n for n in range(1, 100))
    ln_2 = sum((-1)**(n+1) / n for n in range(1, 100000))
    ch.add(NumericCheck(
        label="Ex 10.8: ln(3) = ln(3/2) + ln(2) via separate series",
        section="11",
        stated=math.log(3),
        computed=ln_3_2 + ln_2,
        tolerance=1e-3,
    ))

    # ==================================================================
    # Remark checks
    # ==================================================================

    # --- Remark 3.5a: Harmonic series diverges despite a_n -> 0 ---
    def _remark_3_5a_harmonic_diverges():
        # Partial sums of harmonic series grow without bound
        # H_n ~ ln(n) + gamma, so H_{10000} ~ 9.79
        H_100 = sum(1.0 / n for n in range(1, 101))
        H_10000 = sum(1.0 / n for n in range(1, 10001))
        H_1000000 = sum(1.0 / n for n in range(1, 1000001))
        # Verify partial sums keep growing
        if not (H_1000000 > H_10000 > H_100 > 4.0):
            return (False, f"H_100={H_100:.4f}, H_10000={H_10000:.4f}, H_1000000={H_1000000:.4f}")
        # Verify a_n -> 0 even though series diverges
        a_n = 1.0 / 1000000
        if a_n >= 0.001:
            return (False, f"a_1000000 = {a_n}, not small enough")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.5a: harmonic series diverges (a_n->0 not sufficient)",
        section="3",
        predicate=_remark_3_5a_harmonic_diverges,
        note="Remark 3.5a",
    ))

    # --- Remark 3.8a: Ratio test for x^n/n! gives L = |x|/(n+1) -> 0 ---
    def _remark_3_8a_ratio_test_exp():
        for x_val in [1.0, 5.0, 100.0]:
            # a_n = x^n / n!, ratio = |x|/(n+1)
            ratios = [abs(x_val) / (n + 1) for n in range(1, 101)]
            if ratios[-1] >= 1.0:
                return (False, f"x={x_val}: ratio at n=100 = {ratios[-1]}")
            # Verify ratio -> 0
            if ratios[-1] > 0.01 * abs(x_val):
                return (False, f"x={x_val}: ratio at n=100 = {ratios[-1]}, not converging to 0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.8a: ratio |a_{n+1}/a_n| = |x|/(n+1) -> 0 for x^n/n!",
        section="3",
        predicate=_remark_3_8a_ratio_test_exp,
        note="Remark 3.8a: ratio test effective for factorials",
    ))

    # --- Remark 3.12b: Alternating harmonic converges to ln(2) ---
    ch.add(NumericCheck(
        label="Remark 3.12b: sum (-1)^{n+1}/n = ln(2)",
        section="3",
        stated=math.log(2),
        computed=lambda: sum((-1) ** (n + 1) / n for n in range(1, 100001)),
        tolerance=1e-4,
        note="Remark 3.12b: conditional convergence",
    ))

    # --- Remark 3.16a: Lagrange remainder bound for e^x Taylor at x=1 ---
    def _remark_3_16a_lagrange_remainder():
        # For e^x around a=0: |R_n(x)| <= M|x-a|^{n+1}/(n+1)!
        # where M = max |f^{(n+1)}(t)| for t in [0,1] = e
        for N in [3, 5, 8, 12]:
            partial = sum(1.0 / math.factorial(k) for k in range(N + 1))
            actual_error = abs(partial - math.e)
            bound = math.e / math.factorial(N + 1)
            if actual_error > bound + 1e-15:
                return (False, f"N={N}: actual={actual_error:.6e} > bound={bound:.6e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.16a: Lagrange remainder |R_n| <= e/(n+1)! for e^x at x=1",
        section="3",
        predicate=_remark_3_16a_lagrange_remainder,
        note="Remark 3.16a",
    ))

    # --- Remark 3.23a: Binomial series sqrt(1+x) coefficients ---
    # sqrt(1+x) = 1 + x/2 - x^2/8 + x^3/16 - ...
    ch.add(NumericCheck(
        label="Remark 3.23a: sqrt(1+0.5) via binomial series (4 terms)",
        section="3",
        stated=math.sqrt(1.5),
        computed=lambda: 1 + 0.5/2 - 0.5**2/8 + 0.5**3/16,
        tolerance=1e-2,
        note="Remark 3.23a: binomial series alpha=1/2",
    ))

    # Also verify alpha=-1 recovers geometric series: 1/(1+x) = 1 - x + x^2 - x^3 + ...
    ch.add(NumericCheck(
        label="Remark 3.23a: 1/(1+0.3) via geometric series (20 terms)",
        section="3",
        stated=1.0 / 1.3,
        computed=lambda: sum((-0.3) ** n for n in range(20)),
        tolerance=1e-6,
        note="Remark 3.23a: alpha=-1 gives geometric series",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Taylor Polynomial via Symbolic Differentiation ---
    def _algo_taylor_polynomial():
        """Verify Taylor polynomial computation for e^x, sin(x) at center 0."""
        import sympy as sp
        x = sp.Symbol('x')

        # e^x Taylor polynomial of degree 5 at a=0
        f_exp = sp.exp(x)
        taylor_exp = sp.series(f_exp, x, 0, 6).removeO()
        expected_exp = 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120
        diff_exp = sp.simplify(taylor_exp - expected_exp)
        if diff_exp != 0:
            return (False, f"Taylor(e^x, 5) = {taylor_exp}, expected {expected_exp}")

        # sin(x) Taylor polynomial of degree 5 at a=0
        f_sin = sp.sin(x)
        taylor_sin = sp.series(f_sin, x, 0, 6).removeO()
        expected_sin = x - x**3/6 + x**5/120
        diff_sin = sp.simplify(taylor_sin - expected_sin)
        if diff_sin != 0:
            return (False, f"Taylor(sin(x), 5) = {taylor_sin}, expected {expected_sin}")

        # Verify numerical accuracy: T_5(e^x) at x=0.5
        taylor_val = float(taylor_exp.subs(x, 0.5))
        exact_val = math.exp(0.5)
        if abs(taylor_val - exact_val) > 1e-4:
            return (False, f"T_5(e^0.5) = {taylor_val}, exact = {exact_val}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Taylor polynomial matches symbolic series for e^x, sin(x)",
        section="6",
        predicate=_algo_taylor_polynomial,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Numerical Series Summation with Convergence Detection ---
    def _algo_series_summation():
        """Implement Algorithm 5.2 and verify on known series."""
        def sum_series(term, epsilon=1e-12, max_terms=10000):
            s = 0.0
            for n in range(1, max_terms + 1):
                t = term(n)
                s += t
                if abs(t) < epsilon:
                    return s, n, True
            return s, max_terms, False

        # sum 1/n^2 = pi^2/6
        s, n, conv = sum_series(lambda n: 1.0 / n ** 2, epsilon=1e-8)
        if abs(s - math.pi ** 2 / 6) > 0.01:
            return (False, f"sum 1/n^2 = {s}, expected {math.pi**2/6:.6f}")

        # sum 1/2^n = 1 (geometric, starting from n=1)
        s, n, conv = sum_series(lambda n: 1.0 / 2 ** n)
        if abs(s - 1.0) > 1e-10:
            return (False, f"sum 1/2^n = {s}, expected 1.0")

        # Alternating series: sum (-1)^(n+1)/n = ln(2)
        s, n, conv = sum_series(lambda n: (-1.0) ** (n + 1) / n, epsilon=1e-8)
        if abs(s - math.log(2)) > 0.01:
            return (False, f"alt harmonic = {s}, expected {math.log(2):.6f}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Series summation converges for 1/n^2, 1/2^n, alternating harmonic",
        section="6",
        predicate=_algo_series_summation,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Geometric Series Sum (Closed Form) ---
    def _algo_geometric_sum():
        """Implement Algorithm 5.3 and verify."""
        def geometric_sum(a, r):
            if abs(r) >= 1:
                return None  # diverges
            return a / (1 - r)

        test_cases = [
            (1, 0.5, 2.0),       # 1/(1-0.5) = 2
            (3, 0.1, 10.0 / 3),  # 3/(1-0.1) = 10/3
            (1, -0.5, 2.0 / 3),  # 1/(1+0.5) = 2/3
            (2, 0.9, 20.0),      # 2/(1-0.9) = 20
        ]
        for a, r, expected in test_cases:
            val = geometric_sum(a, r)
            if abs(val - expected) > 1e-10:
                return (False, f"geometric_sum({a},{r}) = {val}, expected {expected}")

        # Verify divergence detection
        if geometric_sum(1, 1.0) is not None:
            return (False, "geometric_sum(1, 1.0) should return None (diverges)")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Geometric series closed form correct, detects divergence",
        section="6",
        predicate=_algo_geometric_sum,
        note="Algorithm 5.3 verified",
    ))

    # ── Remark 3.3a: Monotone convergence theorem strategy ───────────────
    # Claims: for a recursive sequence, (i) show monotone, (ii) show bounded,
    # (iii) conclude converges, (iv) find limit by passing to limit in recurrence.
    # Test with a_{n+1} = (a_n + 2/a_n)/2 converging to sqrt(2).
    def _remark_3_3a_monotone_convergence():
        import math
        # Sequence: a_{n+1} = (a_n + 2/a_n) / 2, a_0 = 2
        # This is Newton's method for sqrt(2)
        a = [2.0]
        for _ in range(20):
            a_next = (a[-1] + 2.0 / a[-1]) / 2.0
            a.append(a_next)

        # (i) Verify monotone decreasing (after first term, a_n >= sqrt(2))
        for i in range(1, len(a) - 1):
            if a[i + 1] > a[i] + 1e-15:
                return (False, f"Not monotone: a[{i+1}]={a[i+1]} > a[{i}]={a[i]}")

        # (ii) Verify bounded below by sqrt(2)
        sqrt2 = math.sqrt(2)
        for i in range(1, len(a)):
            if a[i] < sqrt2 - 1e-15:
                return (False, f"Not bounded below: a[{i}]={a[i]} < sqrt(2)={sqrt2}")

        # (iii) Verify convergence (last terms very close together)
        if abs(a[-1] - a[-2]) > 1e-15:
            return (False, f"Not converged: |a[-1] - a[-2]| = {abs(a[-1] - a[-2])}")

        # (iv) Find limit: if L = lim a_n, then L = (L + 2/L)/2 => L^2 = 2 => L = sqrt(2)
        L = a[-1]
        if abs(L - sqrt2) > 1e-14:
            return (False, f"Limit = {L}, expected sqrt(2) = {sqrt2}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.3a: Monotone convergence strategy — recursive sequence converges to sqrt(2)",
        section="3.3a",
        predicate=_remark_3_3a_monotone_convergence,
        note="Remark 3.3a: monotone convergence theorem verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Exercise helpers
# ---------------------------------------------------------------------------

def _ex_10_6_leibniz(n_terms, target_error):
    """Check that n_terms of the Leibniz series gives error < target_error."""
    partial = sum((-1.0)**n / (2*n + 1) for n in range(n_terms))
    actual_error = abs(partial - math.pi/4)
    if actual_error < target_error:
        return (True, "")
    return (False, f"{n_terms} terms: error = {actual_error:.2e}, target = {target_error:.0e}")


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _exp_taylor():
    import sympy as sp
    x = sp.Symbol('x')
    taylor = sp.series(sp.exp(x), x, 0, 7).removeO()
    manual = 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + x**6/720
    return sp.expand(taylor - manual)

def _sin_taylor():
    import sympy as sp
    x = sp.Symbol('x')
    taylor = sp.series(sp.sin(x), x, 0, 8).removeO()
    manual = x - x**3/6 + x**5/120 - x**7/5040
    return sp.expand(taylor - manual)

def _cos_taylor():
    import sympy as sp
    x = sp.Symbol('x')
    taylor = sp.series(sp.cos(x), x, 0, 7).removeO()
    manual = 1 - x**2/2 + x**4/24 - x**6/720
    return sp.expand(taylor - manual)

def _ln_taylor():
    import sympy as sp
    x = sp.Symbol('x')
    taylor = sp.series(sp.ln(1+x), x, 0, 5).removeO()
    manual = x - x**2/2 + x**3/3 - x**4/4
    return sp.expand(taylor - manual)

def _geometric_series():
    import sympy as sp
    r = sp.Symbol('r', positive=True)
    # Assume 0 < r < 1 so Piecewise resolves
    result = sp.Sum(r**sp.Symbol('n'), (sp.Symbol('n'), 0, sp.oo)).doit()
    # Extract the convergent case value
    if hasattr(result, 'args') and isinstance(result, sp.Piecewise):
        result = result.args[0][0]  # first case value
    return sp.Eq(sp.simplify(result), sp.simplify(1/(1-r)))

def _finite_geometric():
    import sympy as sp
    r = sp.Symbol('r')
    N = 5  # verify for N=5
    lhs = sum(r**n for n in range(N+1))
    rhs = (1 - r**(N+1)) / (1 - r)
    return sp.simplify(sp.expand(lhs) - sp.expand(rhs))


# ---------------------------------------------------------------------------
# Additional formula helpers
# ---------------------------------------------------------------------------

def _divergence_test_demo():
    """F4.1: If a_n does not tend to 0, the series diverges.
    a_n = n/(n+1) -> 1 != 0, so partial sums grow unboundedly."""
    # Verify a_n -> 1
    a_1000 = 1000 / 1001
    if abs(a_1000 - 1.0) > 0.002:
        return (False, f"a_1000 = {a_1000}, expected ~1.0")
    # Partial sum of first 100 terms should be large (~ 100)
    partial = sum(n / (n + 1) for n in range(1, 101))
    if partial < 90:
        return (False, f"Partial sum of 100 terms = {partial}, expected > 90")
    return (True, "")


def _comparison_test_demo():
    """F4.3: 0 < 1/n^2 <= 1/(n(n-1)) for n >= 2.
    Since sum 1/(n(n-1)) = 1 (telescoping), sum 1/n^2 converges."""
    for n in range(2, 1001):
        a_n = 1.0 / n**2
        b_n = 1.0 / (n * (n - 1))
        if a_n > b_n + 1e-15:
            return (False, f"1/{n}^2 = {a_n} > 1/({n}*{n-1}) = {b_n}")
    # Verify telescoping sum is 1
    tele = sum(1.0 / (n * (n - 1)) for n in range(2, 10001))
    if abs(tele - 1.0) > 1e-3:
        return (False, f"Telescoping sum = {tele}, expected ~1.0")
    return (True, "")


def _ratio_test_demo():
    """F4.4: For e^x at x=1, a_n = 1/n!. Ratio |a_{n+1}/a_n| = 1/(n+1) -> 0."""
    ratios = []
    for n in range(1, 51):
        ratio = 1.0 / (n + 1)
        ratios.append(ratio)
    # Check ratio at n=50 is small
    if ratios[-1] > 0.02:
        return (False, f"Ratio at n=50 is {ratios[-1]}, expected < 0.02")
    # Check ratios are monotonically decreasing
    for i in range(1, len(ratios)):
        if ratios[i] > ratios[i-1] + 1e-15:
            return (False, f"Ratios not decreasing at n={i+1}")
    return (True, "")


def _root_test_demo():
    """F4.5: For sum (1/2)^n, |a_n|^{1/n} = 1/2 for all n."""
    for n in range(1, 51):
        a_n = (0.5)**n
        root_n = a_n ** (1.0 / n)
        if abs(root_n - 0.5) > 1e-10:
            return (False, f"|a_{n}|^{{1/{n}}} = {root_n}, expected 0.5")
    return (True, "")


def _absolute_convergence_demo():
    """F4.8: sum |(-1)^n / n^2| = sum 1/n^2 converges (to pi^2/6).
    Absolute convergence implies convergence."""
    abs_sum = sum(1.0 / n**2 for n in range(1, 100001))
    expected = math.pi**2 / 6.0
    if abs(abs_sum - expected) > 0.01:
        return (False, f"sum 1/n^2 (100000 terms) = {abs_sum}, expected ~{expected}")
    # Also verify the alternating version converges
    alt_sum = sum((-1.0)**(n+1) / n**2 for n in range(1, 100001))
    expected_alt = math.pi**2 / 12.0
    if abs(alt_sum - expected_alt) > 0.01:
        return (False, f"Alternating sum = {alt_sum}, expected ~{expected_alt}")
    return (True, "")


def _geometric_power_series():
    """F4.13: 1/(1-x) = sum_{n=0}^{inf} x^n for |x| < 1.
    Use sympy Sum with positive x assumption."""
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    n = sp.Symbol('n')
    result = sp.Sum(x**n, (n, 0, sp.oo)).doit()
    # Extract the convergent case value if Piecewise
    if hasattr(result, 'args') and isinstance(result, sp.Piecewise):
        result = result.args[0][0]
    return sp.Eq(sp.simplify(result), sp.simplify(1 / (1 - x)))


def _binomial_series_demo():
    """F4.14: (1+x)^alpha = sum_{n=0}^{inf} C(alpha,n) x^n.
    Test alpha=1/2, x=0.5: (1.5)^{0.5} ~ 1.22474."""
    alpha = 0.5
    x = 0.5
    exact = (1 + x) ** alpha

    # Compute 10-term binomial series partial sum
    partial = 0.0
    binom_coeff = 1.0  # C(alpha, 0) = 1
    for n in range(10):
        partial += binom_coeff * x**n
        binom_coeff *= (alpha - n) / (n + 1)

    error = abs(partial - exact)
    if error > 1e-4:
        return (False, f"Binomial series (10 terms) = {partial}, exact = {exact}, error = {error}")
    return (True, "")


def _lagrange_remainder_demo():
    """F4.15: |R_N(x)| <= M * |x|^{N+1} / (N+1)! where M = max |f^{(N+1)}(c)|.
    For e^x at x=1: M = e (since e^c <= e for c in [0,1]), bound = e/(N+1)!."""
    for N in range(1, 11):
        t_N = sum(1.0 / math.factorial(k) for k in range(N + 1))
        actual_error = abs(t_N - math.e)
        bound = math.e / math.factorial(N + 1)
        if actual_error > bound + 1e-15:
            return (False, f"N={N}: actual error {actual_error:.6e} > bound {bound:.6e}")
    return (True, "")


def _alternating_error_bound_demo():
    """F4.16: For alternating series ln(2) = sum (-1)^{n+1}/n,
    error after N terms is bounded by |a_{N+1}| = 1/(N+1)."""
    exact = math.log(2)
    for N in [10, 50, 100, 500, 1000]:
        partial = sum((-1)**(n + 1) / n for n in range(1, N + 1))
        actual_error = abs(partial - exact)
        bound = 1.0 / (N + 1)
        if actual_error > bound + 1e-15:
            return (False, f"N={N}: actual error {actual_error:.6e} > bound {bound:.6e}")
    return (True, "")


def _finite_geometric_check():
    """F4.17: sum_{n=0}^{N} r^n = (1 - r^{N+1})/(1-r), verified for N=8."""
    import sympy as sp
    r = sp.Symbol('r')
    N = 8
    lhs = sum(r**n for n in range(N + 1))
    rhs = (1 - r**(N + 1)) / (1 - r)
    return sp.simplify(sp.expand(lhs) - sp.expand(rhs))
