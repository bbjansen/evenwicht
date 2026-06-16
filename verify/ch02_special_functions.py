# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Chapter 2: Special Functions — Verification.

Covers the Gamma function, Beta function, error function, normal CDF,
binomial coefficients, Stirling's approximation, and the binomial theorem.
"""

import math
import scipy.special
import scipy.stats

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(2, "Special Functions")

    # ------------------------------------------------------------------
    # Symbolic checks
    # ------------------------------------------------------------------

    # Gamma(z+1) = z * Gamma(z) — verified numerically at z = 3.5
    ch.add(NumericCheck(
        label="Gamma(z+1) = z*Gamma(z) at z=3.5",
        section="2.1",
        stated=0.0,
        computed=lambda: scipy.special.gamma(4.5) - 3.5 * scipy.special.gamma(3.5),
        tolerance=1e-10,
        note="recurrence relation",
    ))

    # Gamma(1/2) = sqrt(pi) — symbolic
    def _gamma_half():
        import sympy
        return sympy.Eq(sympy.gamma(sympy.Rational(1, 2)), sympy.sqrt(sympy.pi))

    ch.add(SymbolicCheck(
        label="Gamma(1/2) = sqrt(pi)",
        section="2.1",
        identity=_gamma_half,
    ))

    # Euler reflection formula: Gamma(z)*Gamma(1-z) = pi/sin(pi*z) at z=0.3
    ch.add(NumericCheck(
        label="Euler reflection: Gamma(z)*Gamma(1-z) = pi/sin(pi*z) at z=0.3",
        section="2.1",
        stated=0.0,
        computed=lambda: (
            scipy.special.gamma(0.3) * scipy.special.gamma(0.7)
            - math.pi / math.sin(math.pi * 0.3)
        ),
        tolerance=1e-10,
        note="reflection formula residual",
    ))

    # Beta-Gamma relation: B(a,b) = Gamma(a)*Gamma(b)/Gamma(a+b) at a=2, b=3
    ch.add(NumericCheck(
        label="B(a,b) = Gamma(a)*Gamma(b)/Gamma(a+b) at a=2, b=3",
        section="2.2",
        stated=0.0,
        computed=lambda: (
            scipy.special.beta(2, 3)
            - scipy.special.gamma(2) * scipy.special.gamma(3) / scipy.special.gamma(5)
        ),
        tolerance=1e-10,
        note="Beta-Gamma relation residual",
    ))

    # Beta symmetry: B(a,b) = B(b,a) — verified numerically at several points
    def _beta_symmetry():
        pairs = [(2, 3), (0.5, 1.5), (0.7, 2.3), (4, 1), (1.1, 5.5)]
        for a, b in pairs:
            diff = abs(scipy.special.beta(a, b) - scipy.special.beta(b, a))
            if diff > 1e-15:
                return False, f"B({a},{b}) != B({b},{a}), diff={diff}"
        return True, ""

    ch.add(StructuralCheck(
        label="B(a,b) = B(b,a) (verified at 5 sample points)",
        section="2.2",
        predicate=_beta_symmetry,
    ))

    # erf odd symmetry: erf(-x) = -erf(x) — symbolic
    def _erf_odd():
        import sympy
        x = sympy.Symbol("x")
        return sympy.Eq(sympy.erf(-x), -sympy.erf(x))

    ch.add(SymbolicCheck(
        label="erf(-x) = -erf(x)",
        section="2.3",
        identity=_erf_odd,
    ))

    # Pascal's rule: C(n,k) = C(n-1,k-1) + C(n-1,k) at n=10, k=4
    ch.add(NumericCheck(
        label="Pascal's rule: C(10,4) = C(9,3) + C(9,4)",
        section="2.4",
        stated=0.0,
        computed=lambda: (
            scipy.special.comb(10, 4, exact=True)
            - scipy.special.comb(9, 3, exact=True)
            - scipy.special.comb(9, 4, exact=True)
        ),
        tolerance=1e-15,
        note="Pascal's rule residual",
    ))

    # ------------------------------------------------------------------
    # Numeric checks — Worked examples
    # ------------------------------------------------------------------

    ch.add(NumericCheck(
        label="Gamma(5) = 24",
        section="2.1",
        stated=24.0,
        computed=lambda: scipy.special.gamma(5),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Gamma(0.5) ~ 1.7724538509",
        section="2.1",
        stated=1.7724538509,
        computed=lambda: scipy.special.gamma(0.5),
        tolerance=1e-8,
    ))

    ch.add(NumericCheck(
        label="Gamma(0.7) ~ 1.29806",
        section="2.1",
        stated=1.29806,
        computed=lambda: scipy.special.gamma(0.7),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Gamma(3.7) ~ 4.1707",
        section="2.1",
        stated=4.1707,
        computed=lambda: scipy.special.gamma(3.7),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Beta(2,3) = 1/12 ~ 0.08333",
        section="2.2",
        stated=1.0 / 12.0,
        computed=lambda: scipy.special.beta(2, 3),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="erf(1.3859) ~ 0.95000",
        section="2.3",
        stated=0.95000,
        computed=lambda: scipy.special.erf(1.3859),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Phi(1.96) ~ 0.975",
        section="2.3",
        stated=0.975,
        computed=lambda: scipy.stats.norm.cdf(1.96),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="C(100,50) ~ 1.00891e29",
        section="2.4",
        stated=1.00891e29,
        computed=lambda: float(scipy.special.comb(100, 50, exact=True)),
        tolerance=1e-4,
    ))

    def _gen_binom(n, k):
        """Generalized binomial coefficient for real n, integer k >= 0."""
        result = 1.0
        for i in range(int(k)):
            result *= (n - i) / (i + 1)
        return result

    ch.add(NumericCheck(
        label="C(0.5, 3) = 0.0625",
        section="2.4",
        stated=0.0625,
        computed=lambda: _gen_binom(0.5, 3),
        tolerance=1e-6,
    ))

    # Stirling's approximation: n! ~ sqrt(2*pi*n)*(n/e)^n, relative error < 1% for n=10
    def _stirling_check():
        n = 10
        exact = math.factorial(n)
        approx = math.sqrt(2 * math.pi * n) * (n / math.e) ** n
        rel_err = abs(approx - exact) / exact
        ok = rel_err < 0.01
        msg = f"relative error = {rel_err:.6f} (threshold 0.01)"
        return ok, msg

    ch.add(StructuralCheck(
        label="Stirling approx for 10! has relative error < 1%",
        section="2.5",
        predicate=_stirling_check,
    ))

    # ------------------------------------------------------------------
    # Structural check — Binomial theorem
    # ------------------------------------------------------------------

    def _binomial_theorem():
        n = 10
        lhs = 2 ** n
        rhs = sum(scipy.special.comb(n, k, exact=True) for k in range(n + 1))
        ok = lhs == rhs
        msg = f"(1+1)^{n} = {lhs}, sum C({n},k) = {rhs}"
        return ok, msg

    ch.add(StructuralCheck(
        label="Binomial theorem: (1+1)^10 = sum C(10,k) for k=0..10",
        section="2.4",
        predicate=_binomial_theorem,
    ))

    # ==================================================================
    # Table verification — Lanczos coefficients (Section 6, line 819)
    # ==================================================================

    # The Lanczos coefficient table is a set of reference constants.
    # We verify that using these coefficients in the Lanczos approximation
    # produces Gamma function values accurate to near machine precision.

    _lanczos_coeffs = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7,
    ]

    def _lanczos_gamma(z, coeffs=_lanczos_coeffs):
        """Lanczos approximation with g=7, using the tabulated coefficients."""
        import math as _m
        if z < 0.5:
            return _m.pi / (_m.sin(_m.pi * z) * _lanczos_gamma(1 - z, coeffs))
        z -= 1
        x = coeffs[0]
        for i in range(1, 9):
            x += coeffs[i] / (z + i)
        t = z + 7.5
        return _m.sqrt(2 * _m.pi) * t ** (z + 0.5) * _m.exp(-t) * x

    for z_val, z_label in [(0.5, "0.5"), (1.5, "1.5"), (3.5, "3.5"),
                            (5.0, "5"), (10.0, "10"), (0.25, "0.25")]:
        ch.add(NumericCheck(
            label=f"Lanczos table: Gamma({z_label}) via tabulated coefficients",
            section="6",
            stated=scipy.special.gamma(z_val),
            computed=lambda z=z_val: _lanczos_gamma(z),
            tolerance=1e-12,
            note="Verifies Lanczos coefficient table (Section 6)",
        ))

    # ==================================================================
    # Exercise checks (Section 11)
    # ==================================================================

    # --- Exercise 11.1: Gamma(7) = 6! = 720 ---
    ch.add(NumericCheck(
        label="Ex 11.1: Gamma(7) = 720",
        section="11",
        stated=720.0,
        computed=lambda: scipy.special.gamma(7),
        tolerance=1e-10,
    ))

    # --- Exercise 11.2: B(3,4) = 2!*3!/6! = 1/60 ---
    ch.add(NumericCheck(
        label="Ex 11.2: B(3,4) = 1/60",
        section="11",
        stated=1.0 / 60.0,
        computed=lambda: scipy.special.beta(3, 4),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.2: B(3,4) via Gamma = Gamma(3)*Gamma(4)/Gamma(7)",
        section="11",
        stated=1.0 / 60.0,
        computed=lambda: scipy.special.gamma(3) * scipy.special.gamma(4) / scipy.special.gamma(7),
        tolerance=1e-10,
    ))

    # --- Exercise 11.3: C(10,3) = 120 ---
    ch.add(NumericCheck(
        label="Ex 11.3: C(10,3) = 120",
        section="11",
        stated=120.0,
        computed=lambda: float(scipy.special.comb(10, 3, exact=True)),
        tolerance=1e-15,
    ))

    ch.add(NumericCheck(
        label="Ex 11.3: C(10,3) via factorials = 10!/(3!*7!)",
        section="11",
        stated=120.0,
        computed=lambda: math.factorial(10) / (math.factorial(3) * math.factorial(7)),
        tolerance=1e-15,
    ))

    # --- Exercise 11.4: Gamma(1/2) = sqrt(pi) (symbolic) ---
    def _ex4_gamma_half():
        import sympy
        return sympy.Eq(sympy.gamma(sympy.Rational(1, 2)), sympy.sqrt(sympy.pi))

    ch.add(SymbolicCheck(
        label="Ex 11.4: Gamma(1/2) = sqrt(pi)",
        section="11",
        identity=_ex4_gamma_half,
    ))

    # Numeric cross-check
    ch.add(NumericCheck(
        label="Ex 11.4: Gamma(0.5) ~ sqrt(pi) ~ 1.7724539",
        section="11",
        stated=math.sqrt(math.pi),
        computed=lambda: scipy.special.gamma(0.5),
        tolerance=1e-10,
    ))

    # --- Exercise 11.5: Duplication formula at z=3 ---
    # Duplication formula: Gamma(z)*Gamma(z+1/2) = sqrt(pi)/(2^{2z-1}) * Gamma(2z)
    # At z=3: Gamma(3)*Gamma(3.5) = sqrt(pi)/32 * Gamma(6) = sqrt(pi)/32 * 120
    ch.add(NumericCheck(
        label="Ex 11.5: Gamma(3)*Gamma(3.5) via duplication formula",
        section="11",
        stated=0.0,
        computed=lambda: (
            scipy.special.gamma(3) * scipy.special.gamma(3.5)
            - math.sqrt(math.pi) / (2**(2*3 - 1)) * scipy.special.gamma(6)
        ),
        tolerance=1e-10,
        note="residual of duplication formula at z=3",
    ))

    ch.add(NumericCheck(
        label="Ex 11.5: Gamma(3) = 2! = 2",
        section="11",
        stated=2.0,
        computed=lambda: scipy.special.gamma(3),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.5: Gamma(3.5) = (5/2)*(3/2)*(1/2)*sqrt(pi) ~ 3.3234",
        section="11",
        stated=3.3234,
        computed=lambda: scipy.special.gamma(3.5),
        tolerance=1e-3,
    ))

    # --- Exercise 11.6: erf(x) ~ 2x/sqrt(pi) for small x ---
    def _ex6_erf_linear():
        # For small x, erf(x) ~ 2*x/sqrt(pi)
        # Check at x = 0.01: relative error should be very small
        x = 0.01
        erf_exact = float(scipy.special.erf(x))
        erf_linear = 2 * x / math.sqrt(math.pi)
        rel_err = abs(erf_exact - erf_linear) / abs(erf_exact)
        ok = rel_err < 1e-4  # linear approximation within 0.01% at x=0.01
        return ok, f"erf(0.01) = {erf_exact:.10f}, 2*0.01/sqrt(pi) = {erf_linear:.10f}, rel_err = {rel_err:.2e}"

    ch.add(StructuralCheck(
        label="Ex 11.6: erf(x) ~ 2x/sqrt(pi) for small x (at x=0.01)",
        section="11",
        predicate=_ex6_erf_linear,
    ))

    # Next correction term: erf(x) ~ 2/sqrt(pi)*(x - x^3/3)
    def _ex6_erf_cubic():
        x = 0.1
        erf_exact = float(scipy.special.erf(x))
        erf_cubic = 2 / math.sqrt(math.pi) * (x - x**3 / 3)
        rel_err = abs(erf_exact - erf_cubic) / abs(erf_exact)
        ok = rel_err < 1e-4  # cubic correction within 0.01% at x=0.1
        return ok, f"erf(0.1) = {erf_exact:.10f}, cubic approx = {erf_cubic:.10f}, rel_err = {rel_err:.2e}"

    ch.add(StructuralCheck(
        label="Ex 11.6: erf(x) ~ 2/sqrt(pi)*(x - x^3/3) correction term (at x=0.1)",
        section="11",
        predicate=_ex6_erf_cubic,
    ))

    # --- Exercise 11.7: Stirling's approximation from Laplace's method ---
    # Verify Stirling for several n values with increasing accuracy
    def _ex7_stirling():
        for n in [10, 50, 100, 500]:
            exact = math.lgamma(n + 1)  # log(n!)
            stirling = 0.5 * math.log(2 * math.pi * n) + n * math.log(n) - n
            rel_err = abs(stirling - exact) / abs(exact)
            if rel_err > 1.0 / (12 * n) * 1.5:  # Stirling error ~ 1/(12n), allow 50% margin
                return False, f"Stirling rel error at n={n}: {rel_err:.6e}, expected < {1.5/(12*n):.6e}"
        return True, ""

    ch.add(StructuralCheck(
        label="Ex 11.7: Stirling approximation error ~ 1/(12n) for n=10,50,100,500",
        section="11",
        predicate=_ex7_stirling,
    ))

    # --- Exercise 11.8: Beta-Gamma relation proof verification ---
    # B(a,b) = Gamma(a)*Gamma(b)/Gamma(a+b), verify at multiple non-integer points
    def _ex8_beta_gamma():
        test_pairs = [(1.5, 2.5), (0.3, 0.7), (2.7, 3.1), (0.1, 4.9), (5.5, 0.5)]
        for a, b in test_pairs:
            beta_val = float(scipy.special.beta(a, b))
            gamma_val = float(
                scipy.special.gamma(a) * scipy.special.gamma(b) / scipy.special.gamma(a + b)
            )
            rel_err = abs(beta_val - gamma_val) / abs(beta_val)
            if rel_err > 1e-12:
                return False, f"B({a},{b}) = {beta_val}, Gamma form = {gamma_val}, rel_err = {rel_err:.2e}"
        return True, ""

    ch.add(StructuralCheck(
        label="Ex 11.8: Beta-Gamma relation at 5 non-integer sample points",
        section="11",
        predicate=_ex8_beta_gamma,
    ))

    # ------------------------------------------------------------------
    # Remark 3.7: Gamma log-convexity and basic properties
    # ------------------------------------------------------------------

    # Gamma(1) = 1
    ch.add(NumericCheck(
        label="Remark 3.7: Gamma(1) = 1",
        section="3",
        stated=1.0,
        computed=lambda: scipy.special.gamma(1.0),
        tolerance=1e-15,
        note="Remark 3.7: Bohr-Mollerup condition",
    ))

    # Log-convexity: ln Gamma is convex on (0, inf)
    # Verify second derivative of ln Gamma (trigamma) > 0 at several points
    def _remark_3_7_log_convexity():
        test_points = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]
        for z in test_points:
            # trigamma = d^2/dz^2 ln Gamma(z) = polygamma(1, z)
            trigamma = float(scipy.special.polygamma(1, z))
            if trigamma <= 0:
                return (False, f"trigamma({z}) = {trigamma} <= 0, violates log-convexity")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.7: ln Gamma is convex (trigamma > 0 on (0,inf))",
        section="3",
        predicate=_remark_3_7_log_convexity,
        note="Remark 3.7: Bohr-Mollerup log-convexity",
    ))

    # Gamma overflows at z ~ 171.6
    ch.add(StructuralCheck(
        label="Remark 3.7/Def 3.8: Gamma overflows near z=171.6",
        section="3",
        predicate=lambda: (
            math.isinf(scipy.special.gamma(172.0)) and not math.isinf(scipy.special.gamma(170.0)),
            f"Gamma(172)={scipy.special.gamma(172.0)}, Gamma(170)={scipy.special.gamma(170.0)}"
        ),
        note="Remark 3.7 / Definition 3.8: log-Gamma needed for large z",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Lanczos Approximation for Gamma(z) ---
    def _algo_lanczos_gamma():
        """Implement Algorithm 5.1 (Lanczos) and verify against scipy."""
        coefficients = [
            0.99999999999980993,
            676.5203681218851,
            -1259.1392167224028,
            771.32342877765313,
            -176.61502916214059,
            12.507343278686905,
            -0.13857109526572012,
            9.9843695780195716e-6,
            1.5056327351493116e-7,
        ]

        def lanczos_gamma(z):
            if z < 0.5:
                return math.pi / (math.sin(math.pi * z) * lanczos_gamma(1 - z))
            z = z - 1
            ag = coefficients[0]
            for i in range(1, 9):
                ag += coefficients[i] / (z + i)
            t = z + 7.5
            return math.sqrt(2 * math.pi) * t ** (z + 0.5) * math.exp(-t) * ag

        test_values = [0.5, 1.0, 1.5, 2.0, 3.5, 5.0, 10.0, 0.3, 0.7, 100.0]
        for z in test_values:
            lanczos_val = lanczos_gamma(z)
            scipy_val = float(scipy.special.gamma(z))
            rel_err = abs(lanczos_val - scipy_val) / abs(scipy_val)
            if rel_err > 1e-10:
                return (False, f"Lanczos Gamma({z}) = {lanczos_val}, scipy = {scipy_val}, rel_err = {rel_err:.2e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Lanczos Gamma matches scipy at 10 test points",
        section="6",
        predicate=_algo_lanczos_gamma,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Log-Gamma via Lanczos ---
    def _algo_log_gamma():
        """Implement Algorithm 5.2 (Log-Gamma) and verify against scipy."""
        coefficients = [
            0.99999999999980993,
            676.5203681218851,
            -1259.1392167224028,
            771.32342877765313,
            -176.61502916214059,
            12.507343278686905,
            -0.13857109526572012,
            9.9843695780195716e-6,
            1.5056327351493116e-7,
        ]

        def log_gamma(z):
            if z < 0.5:
                return math.log(math.pi / math.sin(math.pi * z)) - log_gamma(1 - z)
            z = z - 1
            ag = coefficients[0]
            for i in range(1, 9):
                ag += coefficients[i] / (z + i)
            t = z + 7.5
            return 0.5 * math.log(2 * math.pi) + (z + 0.5) * math.log(t) - t + math.log(ag)

        test_values = [0.5, 1.0, 5.0, 50.0, 150.0, 200.0]
        for z in test_values:
            our_val = log_gamma(z)
            scipy_val = float(scipy.special.gammaln(z))
            abs_err = abs(our_val - scipy_val)
            if abs_err > 1e-8:
                return (False, f"logGamma({z}) = {our_val}, scipy = {scipy_val}, abs_err = {abs_err:.2e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Log-Gamma via Lanczos matches scipy (no overflow for large z)",
        section="6",
        predicate=_algo_log_gamma,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Beta Function via Log-Gamma ---
    def _algo_beta_log_gamma():
        """Implement Algorithm 5.3 and verify."""
        def log_gamma_scipy(z):
            return float(scipy.special.gammaln(z))

        def beta_via_loggamma(a, b):
            return math.exp(log_gamma_scipy(a) + log_gamma_scipy(b) - log_gamma_scipy(a + b))

        test_pairs = [(2, 3), (0.5, 0.5), (10, 10), (100, 100), (1, 1)]
        for a, b in test_pairs:
            our_val = beta_via_loggamma(a, b)
            scipy_val = float(scipy.special.beta(a, b))
            rel_err = abs(our_val - scipy_val) / abs(scipy_val)
            if rel_err > 1e-10:
                return (False, f"Beta({a},{b}) = {our_val}, scipy = {scipy_val}, rel_err = {rel_err:.2e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Beta via Log-Gamma matches scipy (handles large params)",
        section="6",
        predicate=_algo_beta_log_gamma,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.4: Error Function Approximation (Abramowitz & Stegun) ---
    def _algo_erf_approx():
        """Implement Algorithm 5.4 and verify against scipy."""
        def erf_approx(x):
            if x < 0:
                return -erf_approx(-x)
            p = 0.3275911
            a1 = 0.254829592
            a2 = -0.284496736
            a3 = 1.421413741
            a4 = -1.453152027
            a5 = 1.061405429
            t = 1 / (1 + p * x)
            t2 = t * t
            t3 = t2 * t
            t4 = t3 * t
            t5 = t4 * t
            return 1 - (a1 * t + a2 * t2 + a3 * t3 + a4 * t4 + a5 * t5) * math.exp(-x * x)

        test_values = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, -0.5, -1.0]
        for x in test_values:
            our_val = erf_approx(x)
            scipy_val = float(scipy.special.erf(x))
            abs_err = abs(our_val - scipy_val)
            if abs_err > 1.5e-7:  # stated max error
                return (False, f"erf({x}) = {our_val}, scipy = {scipy_val}, abs_err = {abs_err:.2e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: erf approximation (A&S) within 1.5e-7 of scipy",
        section="6",
        predicate=_algo_erf_approx,
        note="Algorithm 5.4 verified",
    ))

    # --- Algorithm 5.5: Binomial Coefficient (multiplicative formula) ---
    def _algo_binomial_coeff():
        """Implement Algorithm 5.5 and verify."""
        def binomial(n, k):
            if k < 0 or k > n:
                return 0
            if k == 0 or k == n:
                return 1
            k = min(k, n - k)
            result = 1
            for i in range(k):
                result = result * (n - i) // (i + 1)
            return result

        test_cases = [(10, 3, 120), (20, 10, 184756), (100, 50, int(scipy.special.comb(100, 50, exact=True))),
                      (5, 0, 1), (5, 5, 1), (7, 2, 21)]
        for n, k, expected in test_cases:
            val = binomial(n, k)
            if val != expected:
                return (False, f"C({n},{k}) = {val}, expected {expected}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: Binomial coefficient (multiplicative) correct for C(100,50)",
        section="6",
        predicate=_algo_binomial_coeff,
        note="Algorithm 5.5 verified",
    ))

    # --- Algorithm 5.6: Factorial via lookup ---
    def _algo_factorial():
        """Verify factorial correctness and overflow behavior."""
        for n in range(21):
            if math.factorial(n) != scipy.special.factorial(n, exact=True):
                return (False, f"{n}! mismatch")
        # Verify 170! is representable, 171! overflows
        val_170 = float(scipy.special.gamma(171))
        val_171 = float(scipy.special.gamma(172))
        if math.isinf(val_170):
            return (False, f"170! should be representable, got inf")
        if not math.isinf(val_171):
            return (False, f"171! should overflow, got {val_171}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.6: Factorial correct for n=0..20, overflow at n=171",
        section="6",
        predicate=_algo_factorial,
        note="Algorithm 5.6 verified",
    ))

    # --- Remark 3.13: Beta function in probability distributions ---
    # Beta PDF integrates to 1 when normalised by B(a,b)
    def _remark_3_13_beta_pdf():
        """Verify Beta(a,b) normalises the Beta distribution PDF to 1."""
        from scipy.integrate import quad
        for a, b in [(2, 5), (0.5, 0.5), (1, 1), (3, 3)]:
            B_ab = scipy.special.beta(a, b)
            integrand = lambda x, a=a, b=b: x**(a-1) * (1-x)**(b-1)
            result, _ = quad(integrand, 0, 1)
            rel_err = abs(result - B_ab) / B_ab
            if rel_err > 1e-10:
                return (False, f"B({a},{b}): integral={result}, B={B_ab}, rel_err={rel_err}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.13: Beta(a,b) normalises Beta distribution PDF",
        section="3.13",
        predicate=_remark_3_13_beta_pdf,
        note="Remark 3.13: Beta function in probability",
    ))

    return ch


if __name__ == "__main__":
    from framework import Report

    chapter = build()
    chapter.run()
    report = Report()
    report.add_chapter(chapter)
    report.print_console()
    raise SystemExit(report.exit_code)
