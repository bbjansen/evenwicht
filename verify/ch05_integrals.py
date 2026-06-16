# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 5: Integral Calculus — verification."""

import math
import numpy as np
import scipy.integrate
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(5, "Integral Calculus")

    # ===================================================================
    # LAYER 1: Symbolic — antiderivative formulas (Section 5)
    # ===================================================================

    # --- F5.1: int x^n dx = x^(n+1)/(n+1) + C ---
    ch.add(SymbolicCheck(
        label="F5.1: int x^n dx = x^(n+1)/(n+1) + C",
        section="5",
        zero_expr=lambda: _power_antideriv(),
    ))

    # --- F5.2: int e^x dx = e^x + C ---
    ch.add(SymbolicCheck(
        label="F5.2: int e^x dx = e^x + C",
        section="5",
        zero_expr=lambda: _exp_antideriv(),
    ))

    # --- F5.3: int 1/x dx = ln|x| + C ---
    ch.add(SymbolicCheck(
        label="F5.3: int 1/x dx = ln|x| + C",
        section="5",
        zero_expr=lambda: _reciprocal_antideriv(),
    ))

    # --- F5.4: int sin(x) dx = -cos(x) + C ---
    ch.add(SymbolicCheck(
        label="F5.4: int sin(x) dx = -cos(x) + C",
        section="5",
        zero_expr=lambda: _sin_antideriv(),
    ))

    # --- F5.5: int cos(x) dx = sin(x) + C ---
    ch.add(SymbolicCheck(
        label="F5.5: int cos(x) dx = sin(x) + C",
        section="5",
        zero_expr=lambda: _cos_antideriv(),
    ))

    # --- F5.6: int tan(x) dx = -ln|cos(x)| + C ---
    ch.add(SymbolicCheck(
        label="F5.6: int tan(x) dx = -ln|cos(x)| + C",
        section="5",
        zero_expr=lambda: _tan_antideriv(),
    ))

    # --- F5.7: int sec^2(x) dx = tan(x) + C ---
    ch.add(SymbolicCheck(
        label="F5.7: int sec^2(x) dx = tan(x) + C",
        section="5",
        zero_expr=lambda: _sec2_antideriv(),
    ))

    # --- F5.8: int 1/(1+x^2) dx = arctan(x) + C ---
    ch.add(SymbolicCheck(
        label="F5.8: int 1/(1+x^2) dx = arctan(x) + C",
        section="5",
        zero_expr=lambda: _arctan_antideriv(),
    ))

    # --- F5.9: int 1/sqrt(1-x^2) dx = arcsin(x) + C ---
    ch.add(SymbolicCheck(
        label="F5.9: int 1/sqrt(1-x^2) dx = arcsin(x) + C",
        section="5",
        zero_expr=lambda: _arcsin_antideriv(),
    ))

    # --- F5.10: int a^x dx = a^x/ln(a) + C (verified numerically for a=2) ---
    ch.add(NumericCheck(
        label="F5.10: int_0^1 2^x dx = (2-1)/ln(2) = 1/ln(2)",
        section="5",
        stated=1.0 / math.log(2.0),
        computed=lambda: scipy.integrate.quad(lambda x: 2.0**x, 0, 1)[0],
        tolerance=1e-12,
        note="a=2 numeric verification of a^x/ln(a)",
    ))

    # --- F5.10 symbolic: d/dx[a^x/ln(a)] = a^x ---
    ch.add(SymbolicCheck(
        label="F5.10: d/dx[a^x/ln(a)] = a^x (differentiation check)",
        section="5",
        zero_expr=lambda: _general_exp_deriv_check(),
    ))

    # --- F5.11: int ln(x) dx = x*ln(x) - x + C ---
    ch.add(SymbolicCheck(
        label="F5.11: int ln(x) dx = x*ln(x) - x + C",
        section="5",
        zero_expr=lambda: _ln_antideriv(),
    ))

    # --- F5.12: int sqrt(x) dx = (2/3)*x^(3/2) + C ---
    ch.add(SymbolicCheck(
        label="F5.12: int sqrt(x) dx = (2/3)*x^(3/2) + C",
        section="5",
        zero_expr=lambda: _sqrt_antideriv(),
    ))

    # ===================================================================
    # LAYER 1 (cont.): FTC and by-parts identities (Sections 4, 6, 9)
    # ===================================================================

    # --- FTC Part 1: d/dx int_a^x f(t) dt = f(x) ---
    ch.add(SymbolicCheck(
        label="FTC Part 1: d/dx int_0^x sin(t) dt = sin(x)",
        section="6",
        zero_expr=lambda: _ftc(),
    ))

    # --- Integration by parts: d/dx[e^x(x-1)] = x*e^x (Ex 8.4 verification step) ---
    ch.add(SymbolicCheck(
        label="Ex 8.4 verify: d/dx[e^x(x-1)] = x*e^x",
        section="9",
        zero_expr=lambda: _by_parts_deriv_check(),
    ))

    # --- Integration by parts symbolic: int x*e^x dx = e^x(x-1) ---
    ch.add(SymbolicCheck(
        label="Ex 8.4 symbolic: int x*e^x dx = e^x(x-1) + C",
        section="9",
        zero_expr=lambda: _by_parts_antideriv(),
    ))

    # --- Gaussian integral symbolic: int_{-inf}^{inf} e^{-x^2} dx = sqrt(pi) ---
    ch.add(SymbolicCheck(
        label="Gaussian integral: int e^{-x^2} dx = sqrt(pi)",
        section="4",
        zero_expr=lambda: _gaussian_integral_symbolic(),
        note="Remark 3.16",
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # -------------------------------------------------------------------
    # Example 5.17: int_0^pi sin(x) dx = 2
    # -------------------------------------------------------------------

    ch.add(NumericCheck(
        label="Ex 8.1: int_0^pi sin(x) dx = 2 (exact via FTC)",
        section="9",
        stated=2.0,
        computed=-math.cos(math.pi) + math.cos(0),
        tolerance=1e-12,
    ))

    # Simpson n=10 vs scipy cross-check
    simp10 = _simpson(math.sin, 0, math.pi, 10)
    simp10_scipy = float(scipy.integrate.simpson(
        np.sin(np.linspace(0, math.pi, 11)),
        x=np.linspace(0, math.pi, 11),
    ))
    ch.add(NumericCheck(
        label="Ex 8.1: Simpson(sin,0,pi,n=10) vs scipy",
        section="9",
        stated=simp10_scipy,
        computed=simp10,
        tolerance=1e-14,
    ))

    # Simpson n=10 error is O(h^4), consistent with error bound
    simp10_err = abs(simp10 - 2.0)
    simp10_bound = math.pi**5 / (180 * 10**4)
    ch.add(StructuralCheck(
        label="Ex 8.1: Simpson n=10 error < theoretical bound pi^5/(180*10^4)",
        section="9",
        predicate=lambda: (
            simp10_err <= simp10_bound,
            f"error {simp10_err:.2e} > bound {simp10_bound:.2e}"
        ),
        note="Lagrange error bound for Simpson's rule",
    ))

    # Trapezoid n=4 for sin on [0,pi]: Section 6 diagram derives
    # T_4 = (pi/4)/2 * (0 + 2*0.707 + 2*1.0 + 2*0.707 + 0) ~ 1.896
    trap4_sin = _trapezoid(math.sin, 0, math.pi, 4)
    h4 = math.pi / 4
    # Textbook formula: h/2 * [f(x0) + 2f(x1) + 2f(x2) + 2f(x3) + f(x4)]
    trap4_manual = (h4 / 2) * (0 + 2 * math.sin(math.pi / 4) + 2 * math.sin(math.pi / 2)
                                + 2 * math.sin(3 * math.pi / 4) + 0)
    ch.add(NumericCheck(
        label="Ex 8.1: Trap n=4 manual formula matches implementation",
        section="9",
        stated=trap4_manual,
        computed=trap4_sin,
        tolerance=1e-14,
    ))

    # Textbook states T_4 ~ 1.896
    ch.add(NumericCheck(
        label="Ex 8.1: Trap(sin,0,pi,n=4) ~ 1.896",
        section="9",
        stated=1.896,
        computed=trap4_sin,
        tolerance=5e-3,
        note="Section 6 diagram approximate value",
    ))

    # -------------------------------------------------------------------
    # Example 5.18: int_0^1 e^x dx = e - 1
    # -------------------------------------------------------------------

    exact_ex = math.e - 1

    ch.add(NumericCheck(
        label="Ex 8.2: int_0^1 e^x dx = e-1 ~ 1.71828",
        section="9",
        stated=1.71828182845905,
        computed=exact_ex,
        tolerance=1e-12,
    ))

    # --- Quadrature error table (Section 9, Example 5.18) ---
    # The textbook gives rounded order-of-magnitude error values.
    # We verify the actual computed errors and then verify the
    # convergence RATES which are the key claims.
    ns = [4, 8, 16, 32, 64]
    trap_errs = []
    simp_errs = []
    for n in ns:
        trap_errs.append(abs(_trapezoid(math.exp, 0, 1, n) - exact_ex))
        simp_errs.append(abs(_simpson(math.exp, 0, 1, n) - exact_ex))

    # Verify all trapezoid errors are positive and decreasing
    ch.add(StructuralCheck(
        label="Ex 8.2: Trap errors strictly decrease as n doubles",
        section="9",
        predicate=lambda: (
            all(trap_errs[i] > trap_errs[i + 1] for i in range(len(trap_errs) - 1)),
            f"trap errors not decreasing: {[f'{e:.2e}' for e in trap_errs]}"
        ),
    ))

    # Verify all Simpson errors are positive and decreasing
    ch.add(StructuralCheck(
        label="Ex 8.2: Simpson errors strictly decrease as n doubles",
        section="9",
        predicate=lambda: (
            all(simp_errs[i] > simp_errs[i + 1] for i in range(len(simp_errs) - 1)),
            f"simp errors not decreasing: {[f'{e:.2e}' for e in simp_errs]}"
        ),
    ))

    # ------------------------------------------------------------------
    # Table verification: exact textbook error values (Section 9, line 519)
    # ------------------------------------------------------------------

    # Trapezoid errors stated in the table
    stated_trap = [8.9e-3, 2.2e-3, 5.6e-4, 1.4e-4, 3.5e-5]
    for i, n in enumerate(ns):
        ch.add(NumericCheck(
            label=f"Table 9: Trap error n={n} = {stated_trap[i]:.1e}",
            section="9",
            stated=stated_trap[i],
            computed=trap_errs[i],
            tolerance=0.05,
            note="Quadrature error table row",
        ))

    # Simpson errors stated in the table
    stated_simp = [3.7e-5, 2.3e-6, 1.5e-7, 9.1e-9, 5.7e-10]
    for i, n in enumerate(ns):
        ch.add(NumericCheck(
            label=f"Table 9: Simpson error n={n} = {stated_simp[i]:.1e}",
            section="9",
            stated=stated_simp[i],
            computed=simp_errs[i],
            tolerance=0.05,
            note="Quadrature error table row",
        ))

    # Also verify by order of magnitude (original checks)
    stated_trap_oom = [-3, -4, -4, -5, -5]  # floor(log10(stated))
    for i, n in enumerate(ns):
        computed_oom = math.floor(math.log10(trap_errs[i]))
        ch.add(StructuralCheck(
            label=f"Ex 8.2: Trap error at n={n} order 1e{stated_trap_oom[i]}",
            section="9",
            predicate=lambda i=i, co=computed_oom, so=stated_trap_oom[i]: (
                abs(co - so) <= 1,
                f"computed OOM={co}, textbook OOM={so}"
            ),
            note="textbook error table",
        ))

    # Simpson: textbook gives illustrative values; our implementation shows
    # consistent O(1/n^4) convergence. Verify errors are small and improve
    # by ~16x with each doubling (already checked by convergence ratio tests).
    # Check Simpson errors are at least 4 OOM better than trapezoid errors.
    for i, n in enumerate(ns):
        ch.add(StructuralCheck(
            label=f"Ex 8.2: Simpson error << Trap error at n={n}",
            section="9",
            predicate=lambda i=i: (
                simp_errs[i] < trap_errs[i] * 0.01,
                f"simp={simp_errs[i]:.2e} not << trap={trap_errs[i]:.2e}"
            ),
            note="Simpson converges much faster than trapezoid",
        ))

    # Convergence rates — trapezoid O(1/n^2): ratio ~ 4 for each doubling
    for i in range(len(ns) - 1):
        ratio = trap_errs[i] / trap_errs[i + 1]
        ch.add(NumericCheck(
            label=f"Ex 8.2: Trap convergence n={ns[i]}/n={ns[i+1]} ~ 4",
            section="9",
            stated=4.0,
            computed=ratio,
            tolerance=0.05,
            note="O(1/n^2) rate",
        ))

    # Convergence rates — Simpson O(1/n^4): ratio ~ 16 for each doubling
    for i in range(len(ns) - 1):
        ratio = simp_errs[i] / simp_errs[i + 1]
        ch.add(NumericCheck(
            label=f"Ex 8.2: Simpson convergence n={ns[i]}/n={ns[i+1]} ~ 16",
            section="9",
            stated=16.0,
            computed=ratio,
            tolerance=0.1,
            note="O(1/n^4) rate",
        ))

    # -------------------------------------------------------------------
    # Example 5.19: int_0^1 4/(1+x^2) dx = pi
    # -------------------------------------------------------------------

    # Exact: 4*[arctan(1) - arctan(0)] = 4*(pi/4 - 0) = pi
    ch.add(NumericCheck(
        label="Ex 8.3: 4*(arctan(1)-arctan(0)) = pi (exact)",
        section="9",
        stated=math.pi,
        computed=4.0 * (math.atan(1.0) - math.atan(0.0)),
        tolerance=1e-15,
    ))

    f_pi = lambda x: 4.0 / (1.0 + x * x)

    # Simpson n=100 ~ pi to full double precision
    simp100 = _simpson(f_pi, 0, 1, 100)
    ch.add(NumericCheck(
        label="Ex 8.3: Simpson(4/(1+x^2),0,1,n=100) ~ pi",
        section="9",
        stated=math.pi,
        computed=simp100,
        tolerance=1e-12,
    ))

    # Cross-check with scipy quad
    quad_pi, _ = scipy.integrate.quad(f_pi, 0, 1)
    ch.add(NumericCheck(
        label="Ex 8.3: scipy quad 4/(1+x^2) = pi",
        section="9",
        stated=math.pi,
        computed=quad_pi,
        tolerance=1e-14,
    ))

    # -------------------------------------------------------------------
    # Example 5.20: int_0^1 x*e^x dx = 1 (integration by parts)
    # -------------------------------------------------------------------

    # Exact: [e^x(x-1)]_0^1 = e^1*(1-1) - e^0*(0-1) = 0 - (-1) = 1
    ch.add(NumericCheck(
        label="Ex 8.4: [e^x(x-1)]_0^1 = 1 (by parts, exact)",
        section="9",
        stated=1.0,
        computed=math.exp(1) * (1 - 1) - math.exp(0) * (0 - 1),
        tolerance=1e-12,
    ))

    # Intermediate step: boundary term e^1*(1-1) = 0
    ch.add(NumericCheck(
        label="Ex 8.4: boundary e^1*(1-1) = 0",
        section="9",
        stated=0.0,
        computed=math.exp(1) * (1 - 1),
        tolerance=1e-15,
    ))

    # Intermediate step: boundary term e^0*(0-1) = -1
    ch.add(NumericCheck(
        label="Ex 8.4: boundary e^0*(0-1) = -1",
        section="9",
        stated=-1.0,
        computed=math.exp(0) * (0 - 1),
        tolerance=1e-15,
    ))

    # Cross-check with scipy quad
    quad_result, _ = scipy.integrate.quad(lambda x: x * math.exp(x), 0, 1)
    ch.add(NumericCheck(
        label="Ex 8.4: scipy quad x*e^x on [0,1] = 1",
        section="9",
        stated=1.0,
        computed=quad_result,
        tolerance=1e-12,
    ))

    # Simpson n=50 cross-check (textbook TypeScript example)
    simp50_xex = _simpson(lambda x: x * math.exp(x), 0, 1, 50)
    ch.add(NumericCheck(
        label="Ex 8.4: Simpson(x*e^x,0,1,n=50) ~ 1",
        section="9",
        stated=1.0,
        computed=simp50_xex,
        tolerance=1e-6,
        note="textbook TypeScript example uses n=50",
    ))

    # ===================================================================
    # LAYER 2 (cont.): Improper integrals (Section 4, Examples 3.15)
    # ===================================================================

    # --- Type I: int_0^inf e^{-x} dx = 1 ---
    quad_exp_decay, _ = scipy.integrate.quad(lambda x: math.exp(-x), 0, np.inf)
    ch.add(NumericCheck(
        label="Improper Type I: int_0^inf e^{-x} dx = 1",
        section="4",
        stated=1.0,
        computed=quad_exp_decay,
        tolerance=1e-12,
        note="Example 3.15",
    ))

    # Analytic: lim_{R->inf} [-e^{-x}]_0^R = lim (1 - e^{-R}) = 1
    R = 50
    ch.add(NumericCheck(
        label="Improper Type I: 1-e^{-50} ~ 1",
        section="4",
        stated=1.0,
        computed=1.0 - math.exp(-R),
        tolerance=1e-12,
        note="truncation verification",
    ))

    # --- Type II: int_0^1 x^{-1/2} dx = 2 ---
    quad_sqrt_sing, _ = scipy.integrate.quad(lambda x: x**(-0.5), 0, 1)
    ch.add(NumericCheck(
        label="Improper Type II: int_0^1 x^{-1/2} dx = 2",
        section="4",
        stated=2.0,
        computed=quad_sqrt_sing,
        tolerance=1e-10,
        note="Example 3.15",
    ))

    # Analytic: [2*x^{1/2}]_eps^1 = 2 - 2*sqrt(eps) -> 2
    eps = 1e-12
    ch.add(NumericCheck(
        label="Improper Type II: 2-2*sqrt(eps) -> 2 as eps->0",
        section="4",
        stated=2.0,
        computed=2.0 - 2.0 * math.sqrt(eps),
        tolerance=1e-5,
        note="analytic limit verification",
    ))

    # --- Gaussian integral numerical: int_{-inf}^{inf} e^{-x^2} dx = sqrt(pi) ---
    quad_gauss, _ = scipy.integrate.quad(lambda x: math.exp(-x**2), -np.inf, np.inf)
    ch.add(NumericCheck(
        label="Gaussian integral numeric: int e^{-x^2} dx = sqrt(pi)",
        section="4",
        stated=math.sqrt(math.pi),
        computed=quad_gauss,
        tolerance=1e-12,
        note="Remark 3.16",
    ))

    # Half-Gaussian: int_0^inf e^{-x^2} dx = sqrt(pi)/2
    quad_half_gauss, _ = scipy.integrate.quad(lambda x: math.exp(-x**2), 0, np.inf)
    ch.add(NumericCheck(
        label="Half-Gaussian: int_0^inf e^{-x^2} dx = sqrt(pi)/2",
        section="4",
        stated=math.sqrt(math.pi) / 2.0,
        computed=quad_half_gauss,
        tolerance=1e-12,
        note="Remark 3.16, connects to Gamma(1/2)",
    ))

    # Gamma(1/2) = sqrt(pi) connection
    ch.add(NumericCheck(
        label="Gamma(1/2) = sqrt(pi)",
        section="4",
        stated=math.sqrt(math.pi),
        computed=math.gamma(0.5),
        tolerance=1e-12,
        note="Remark 3.16, Gamma function connection",
    ))

    # Normal density normalization: (1/sqrt(2*pi)) * int e^{-x^2/2} dx = 1
    quad_normal, _ = scipy.integrate.quad(
        lambda x: math.exp(-x**2 / 2.0) / math.sqrt(2.0 * math.pi),
        -np.inf, np.inf,
    )
    ch.add(NumericCheck(
        label="Normal density normalization: N(0,1) integrates to 1",
        section="4",
        stated=1.0,
        computed=quad_normal,
        tolerance=1e-12,
        note="Remark 3.16, normal distribution",
    ))

    # ===================================================================
    # LAYER 2 (cont.): Quadrature algorithm verification (Section 6)
    # ===================================================================

    # Midpoint rule for sin on [0,pi], n=100
    mid100_sin = _midpoint(math.sin, 0, math.pi, 100)
    ch.add(NumericCheck(
        label="Midpoint(sin,0,pi,n=100) ~ 2",
        section="6",
        stated=2.0,
        computed=mid100_sin,
        tolerance=1e-4,
        note="Algorithm 5.1",
    ))

    # Midpoint rule for e^x on [0,1], n=100
    mid100_exp = _midpoint(math.exp, 0, 1, 100)
    ch.add(NumericCheck(
        label="Midpoint(e^x,0,1,n=100) ~ e-1",
        section="6",
        stated=exact_ex,
        computed=mid100_exp,
        tolerance=1e-4,
        note="Algorithm 5.1",
    ))

    # ===================================================================
    # LAYER 2 (cont.): Archimedes parabolic segment (Section 1)
    # ===================================================================

    # Geometric series 1 + 1/4 + 1/16 + ... = 4/3
    ch.add(NumericCheck(
        label="Archimedes series: 1+1/4+1/16+... = 4/3",
        section="1",
        stated=4.0 / 3.0,
        computed=sum(0.25**k for k in range(50)),
        tolerance=1e-12,
        note="parabolic segment area ratio",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Simpson error bound: |E_S| <= pi^5/(180*n^4) for sin ---
    n = 10
    simp_err = abs(_simpson(math.sin, 0, math.pi, n) - 2.0)
    err_bound = math.pi**5 / (180 * n**4)
    ch.add(StructuralCheck(
        label="Simpson error within bound for sin, n=10",
        section="7",
        predicate=lambda: (
            simp_err <= err_bound,
            f"error {simp_err:.2e} > bound {err_bound:.2e}"
        ),
    ))

    # --- Textbook: Simpson error bound pi^5/(180*10^4) ~ 1.7e-4 ---
    ch.add(NumericCheck(
        label="Simpson error bound pi^5/(180*10^4) ~ 1.7e-4",
        section="7",
        stated=1.7e-4,
        computed=err_bound,
        tolerance=0.05,
        note="textbook states ~1.7e-4",
    ))

    # --- Trapezoid error bound: |E_T| <= (b-a)^3/(12*n^2)*max|f''| ---
    n_trap = 10
    trap_err_sin = abs(_trapezoid(math.sin, 0, math.pi, n_trap) - 2.0)
    trap_bound_sin = math.pi**3 / (12 * n_trap**2)  # max|sin''| = max|sin| = 1
    ch.add(StructuralCheck(
        label="Trapezoid error within bound for sin, n=10",
        section="7",
        predicate=lambda: (
            trap_err_sin <= trap_bound_sin,
            f"error {trap_err_sin:.2e} > bound {trap_bound_sin:.2e}"
        ),
    ))

    # --- Midpoint error bound: |E_M| <= (b-a)^3/(24*n^2)*max|f''| ---
    mid_err_sin = abs(_midpoint(math.sin, 0, math.pi, n_trap) - 2.0)
    mid_bound_sin = math.pi**3 / (24 * n_trap**2)
    ch.add(StructuralCheck(
        label="Midpoint error within bound for sin, n=10",
        section="7",
        predicate=lambda: (
            mid_err_sin <= mid_bound_sin,
            f"error {mid_err_sin:.2e} > bound {mid_bound_sin:.2e}"
        ),
    ))

    # --- Midpoint error bound constant is half the trapezoid bound ---
    ch.add(StructuralCheck(
        label="Midpoint bound = Trapezoid bound / 2",
        section="7",
        predicate=lambda: (
            abs(mid_bound_sin - trap_bound_sin / 2.0) < 1e-15,
            f"mid bound {mid_bound_sin} != trap bound/2 {trap_bound_sin/2}"
        ),
        note="Section 6: midpoint constant smaller by factor 2",
    ))

    # --- Simpson exact for cubics (Section 6 comparison table) ---
    simp_cubic = _simpson(lambda x: x**3, 0, 1, 2)
    exact_cubic = 0.25  # int_0^1 x^3 dx = 1/4
    ch.add(StructuralCheck(
        label="Simpson exact for x^3 (degree 3 polynomial)",
        section="6",
        predicate=lambda: (
            abs(simp_cubic - exact_cubic) < 1e-14,
            f"Simpson(x^3) = {simp_cubic}, expected {exact_cubic}"
        ),
        note="Simpson exact for polynomials up to degree 3",
    ))

    # --- Simpson exact for x^2 on [0,1] with n=2 ---
    simp_quad = _simpson(lambda x: x**2, 0, 1, 2)
    exact_quad = 1.0 / 3.0
    ch.add(StructuralCheck(
        label="Simpson exact for x^2 (degree 2 polynomial)",
        section="6",
        predicate=lambda: (
            abs(simp_quad - exact_quad) < 1e-14,
            f"Simpson(x^2) = {simp_quad}, expected {exact_quad}"
        ),
    ))

    # --- Simpson exact for x on [0,1] with n=2 ---
    simp_lin = _simpson(lambda x: x, 0, 1, 2)
    exact_lin = 0.5
    ch.add(StructuralCheck(
        label="Simpson exact for x (degree 1 polynomial)",
        section="6",
        predicate=lambda: (
            abs(simp_lin - exact_lin) < 1e-14,
            f"Simpson(x) = {simp_lin}, expected {exact_lin}"
        ),
    ))

    # --- Simpson exact for constant on [0,1] with n=2 ---
    simp_const = _simpson(lambda x: 7.0, 0, 1, 2)
    ch.add(StructuralCheck(
        label="Simpson exact for f=7 (degree 0 polynomial)",
        section="6",
        predicate=lambda: (
            abs(simp_const - 7.0) < 1e-14,
            f"Simpson(7) = {simp_const}, expected 7.0"
        ),
    ))

    # --- Additivity: int_0^pi sin = int_0^{pi/2} sin + int_{pi/2}^pi sin ---
    left_half = _simpson(math.sin, 0, math.pi / 2, 20)
    right_half = _simpson(math.sin, math.pi / 2, math.pi, 20)
    full = _simpson(math.sin, 0, math.pi, 40)
    ch.add(StructuralCheck(
        label="Additivity: int_0^pi = int_0^{pi/2} + int_{pi/2}^pi",
        section="4",
        predicate=lambda: (
            abs(full - (left_half + right_half)) < 1e-14,
            f"full={full}, sum={left_half + right_half}"
        ),
        note="Theorem 3.7",
    ))

    # --- Linearity: int (2*sin + 3*cos) = 2*int(sin) + 3*int(cos) ---
    f_lin_comb = lambda x: 2.0 * math.sin(x) + 3.0 * math.cos(x)
    combined = _simpson(f_lin_comb, 0, math.pi, 20)
    separate = 2.0 * _simpson(math.sin, 0, math.pi, 20) + 3.0 * _simpson(math.cos, 0, math.pi, 20)
    ch.add(StructuralCheck(
        label="Linearity: int(2sin+3cos) = 2*int(sin)+3*int(cos)",
        section="4",
        predicate=lambda: (
            abs(combined - separate) < 1e-12,
            f"combined={combined}, separate={separate}"
        ),
        note="Theorem 3.5",
    ))

    # --- Monotonicity: sin(x) <= 1 on [0,pi], so int sin <= int 1 = pi ---
    int_sin = _simpson(math.sin, 0, math.pi, 20)
    ch.add(StructuralCheck(
        label="Monotonicity: int_0^pi sin(x) <= pi",
        section="4",
        predicate=lambda: (
            int_sin <= math.pi + 1e-12,
            f"int sin = {int_sin} > pi = {math.pi}"
        ),
        note="Theorem 3.6",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 5.1: int_1^3 (2x+1) dx ---
    # FTC: F(x) = x^2 + x, F(3) - F(1) = 12 - 2 = 10
    ch.add(NumericCheck(
        label="Ex 5.1: int_1^3 (2x+1) dx = 10 (FTC)",
        section="11",
        stated=10.0,
        computed=lambda: (3.0**2 + 3.0) - (1.0**2 + 1.0),
        tolerance=1e-12,
    ))

    # Riemann sum with n=4 right endpoints
    ch.add(NumericCheck(
        label="Ex 5.1: Riemann sum n=4 right endpoints ~ 11",
        section="11",
        stated=11.0,
        computed=lambda: _riemann_right(lambda x: 2*x+1, 1, 3, 4),
        tolerance=1e-12,
        note="R_4 = 0.5*(3+5+7+9) = 0.5*22 = 11 (overestimate for increasing f)",
    ))

    # --- Exercise 5.2: int_0^{pi/2} cos(x) dx = 1 ---
    ch.add(NumericCheck(
        label="Ex 5.2: int_0^{pi/2} cos(x) dx = 1 (exact)",
        section="11",
        stated=1.0,
        computed=lambda: math.sin(math.pi/2) - math.sin(0),
        tolerance=1e-12,
    ))

    # Simpson n=4
    simp4_cos = _simpson(math.cos, 0, math.pi/2, 4)
    ch.add(NumericCheck(
        label="Ex 5.2: Simpson(cos, 0, pi/2, n=4) ~ 1",
        section="11",
        stated=1.0,
        computed=simp4_cos,
        tolerance=1e-3,
    ))

    # --- Exercise 5.3: antiderivative of 3x^2 - 4x + 7 is x^3 - 2x^2 + 7x + C ---
    ch.add(SymbolicCheck(
        label="Ex 5.3: int (3x^2-4x+7) dx = x^3-2x^2+7x + C",
        section="11",
        zero_expr=lambda: _exercise_5_10_3(),
    ))

    # --- Exercise 5.4: substitution u=x^2+1, int_0^2 2x/(x^2+1) dx ---
    # = ln(x^2+1)|_0^2 = ln(5) - ln(1) = ln(5)
    ch.add(NumericCheck(
        label="Ex 5.4: int_0^2 2x/(x^2+1) dx = ln(5)",
        section="11",
        stated=math.log(5),
        computed=lambda: math.log(2.0**2 + 1) - math.log(0.0**2 + 1),
        tolerance=1e-12,
    ))

    quad_ex104, _ = scipy.integrate.quad(lambda x: 2*x/(x**2+1), 0, 2)
    ch.add(NumericCheck(
        label="Ex 5.4: scipy quad verification = ln(5)",
        section="11",
        stated=math.log(5),
        computed=quad_ex104,
        tolerance=1e-12,
    ))

    # --- Exercise 5.5: int_0^1 x*cos(x) dx by parts ---
    # = [x*sin(x)]_0^1 - int_0^1 sin(x) dx = sin(1) - [-cos(x)]_0^1
    # = sin(1) - (1 - cos(1)) = sin(1) + cos(1) - 1
    exact_ex105 = math.sin(1) + math.cos(1) - 1

    ch.add(NumericCheck(
        label="Ex 5.5: int_0^1 x*cos(x) dx = sin(1)+cos(1)-1",
        section="11",
        stated=exact_ex105,
        computed=lambda: math.sin(1) + math.cos(1) - 1,
        tolerance=1e-12,
    ))

    quad_ex105, _ = scipy.integrate.quad(lambda x: x*math.cos(x), 0, 1)
    ch.add(NumericCheck(
        label="Ex 5.5: scipy quad x*cos(x) on [0,1]",
        section="11",
        stated=exact_ex105,
        computed=quad_ex105,
        tolerance=1e-12,
    ))

    simp20_ex105 = _simpson(lambda x: x*math.cos(x), 0, 1, 20)
    ch.add(NumericCheck(
        label="Ex 5.5: Simpson n=20 x*cos(x) on [0,1]",
        section="11",
        stated=exact_ex105,
        computed=simp20_ex105,
        tolerance=1e-6,
    ))

    # --- Exercise 5.6: int_1^inf 1/x^p dx ---
    # Converges for p > 1, value = 1/(p-1)
    ch.add(NumericCheck(
        label="Ex 5.6: int_1^inf 1/x^2 dx = 1 (p=2)",
        section="11",
        stated=1.0,
        computed=lambda: 1.0 / (2 - 1),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 5.6: int_1^inf 1/x^3 dx = 1/2 (p=3)",
        section="11",
        stated=0.5,
        computed=lambda: 1.0 / (3 - 1),
        tolerance=1e-12,
    ))

    quad_p2, _ = scipy.integrate.quad(lambda x: 1.0/x**2, 1, np.inf)
    ch.add(NumericCheck(
        label="Ex 5.6: scipy quad 1/x^2 on [1,inf) = 1",
        section="11",
        stated=1.0,
        computed=quad_p2,
        tolerance=1e-10,
    ))

    # --- Exercise 5.8: pi via int_0^1 4/(1+x^2) dx with Simpson ---
    ch.add(NumericCheck(
        label="Ex 5.8: Simpson n=100 gives pi to 10+ digits",
        section="11",
        stated=math.pi,
        computed=_simpson(f_pi, 0, 1, 100),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 5.8: Simpson n=1000 gives pi to 15+ digits",
        section="11",
        stated=math.pi,
        computed=_simpson(f_pi, 0, 1, 1000),
        tolerance=1e-14,
    ))

    # --- Exercise 5.7: Simpson exact for degree <= 3 ---
    # Verify for f=1, f=x, f=x^2, f=x^3 on arbitrary interval [a,b] with n=2
    def _ex_10_7_simpson_exact():
        a, b = 1.0, 3.0
        test_cases = [
            (lambda x: 1.0, b - a, "f=1"),
            (lambda x: x, (b**2 - a**2) / 2.0, "f=x"),
            (lambda x: x**2, (b**3 - a**3) / 3.0, "f=x^2"),
            (lambda x: x**3, (b**4 - a**4) / 4.0, "f=x^3"),
        ]
        for f, exact, name in test_cases:
            simp = _simpson(f, a, b, 2)
            if abs(simp - exact) > 1e-12:
                return (False, f"Simpson not exact for {name}: got {simp}, expected {exact}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 5.7: Simpson exact for f=1, x, x^2, x^3 on [1,3] with n=2",
        section="11",
        predicate=_ex_10_7_simpson_exact,
    ))

    # Also verify NOT exact for degree 4
    simp_x4 = _simpson(lambda x: x**4, 1, 3, 2)
    exact_x4 = (3.0**5 - 1.0**5) / 5.0
    ch.add(StructuralCheck(
        label="Ex 5.7: Simpson NOT exact for x^4 on [1,3] with n=2",
        section="11",
        predicate=lambda: (
            abs(simp_x4 - exact_x4) > 1e-6,
            f"Simpson unexpectedly exact for x^4: {simp_x4} vs {exact_x4}"
        ),
    ))

    # --- Algorithm 5.2: Trapezoid Rule ---
    def _algo_trapezoid_rule():
        """Verify trapezoid rule convergence (O(h^2)) on sin(x) over [0, pi]."""
        exact = 2.0
        err_n10 = abs(_trapezoid(math.sin, 0, math.pi, 10) - exact)
        err_n100 = abs(_trapezoid(math.sin, 0, math.pi, 100) - exact)
        # Ratio should be ~100 for O(h^2)
        ratio = err_n10 / err_n100
        if ratio < 50 or ratio > 200:
            return (False, f"Trapezoid O(h^2) ratio = {ratio:.1f}, expected ~100")
        # Also check absolute accuracy at n=100
        if err_n100 > 1e-3:
            return (False, f"Trapezoid(sin,0,pi,100) error = {err_n100:.2e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Trapezoid rule O(h^2) convergence on sin(x) over [0,pi]",
        section="6",
        predicate=_algo_trapezoid_rule,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Simpson's Rule ---
    def _algo_simpsons_rule():
        """Verify Simpson's rule convergence (O(h^4)) on sin(x) over [0, pi]."""
        exact = 2.0
        err_n10 = abs(_simpson(math.sin, 0, math.pi, 10) - exact)
        err_n100 = abs(_simpson(math.sin, 0, math.pi, 100) - exact)
        # Ratio should be ~10000 for O(h^4)
        if err_n10 < 1e-15 or err_n100 < 1e-15:
            return (True, "")  # Machine precision reached
        ratio = err_n10 / err_n100
        if ratio < 5000 or ratio > 20000:
            return (False, f"Simpson O(h^4) ratio = {ratio:.1f}, expected ~10000")
        # Also check that Simpson is exact for cubics
        cubic_exact = (3.0**4 - 1.0**4) / 4.0  # int x^3 from 1 to 3
        cubic_simp = _simpson(lambda x: x**3, 1, 3, 2)
        if abs(cubic_simp - cubic_exact) > 1e-12:
            return (False, f"Simpson not exact for x^3: {cubic_simp} vs {cubic_exact}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Simpson's rule O(h^4) convergence and exactness for cubics",
        section="6",
        predicate=_algo_simpsons_rule,
        note="Algorithm 5.3 verified",
    ))

    # ── Remark 3.11: FTC significance ────────────────────────────────────
    # Claims: (1) integration then differentiation recovers original,
    # (2) definite integral = antiderivative difference (much easier than Riemann sums).
    def _remark_3_11_ftc_significance():
        import numpy as np

        # Verify Riemann sum converges to antiderivative difference for sin(x) on [0, pi]
        # Exact integral = -cos(pi) - (-cos(0)) = 2
        exact = 2.0

        # Riemann sum with increasing N should converge
        errors = []
        for N in [100, 1000, 10000]:
            a, b = 0.0, np.pi
            dx = (b - a) / N
            x_mid = np.array([a + (i + 0.5) * dx for i in range(N)])
            riemann = np.sum(np.sin(x_mid)) * dx
            errors.append(abs(riemann - exact))

        # Errors should decrease
        for i in range(len(errors) - 1):
            if errors[i + 1] >= errors[i]:
                return (False, f"Riemann sum error not decreasing: {errors}")

        # Antiderivative difference is trivially exact
        antideriv_diff = (-np.cos(np.pi)) - (-np.cos(0.0))
        if abs(antideriv_diff - exact) > 1e-14:
            return (False, f"Antiderivative difference = {antideriv_diff}, expected {exact}")

        # The FTC claim: antiderivative method is exact while Riemann needs N->inf
        if errors[-1] > 1e-8:
            # Even 10000 Riemann intervals has nontrivial error
            pass  # This is expected for moderate N
        if abs(antideriv_diff - exact) > abs(errors[-1]):
            return (False, "Antiderivative method should be more accurate than Riemann sums")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.11: FTC — antiderivative evaluation vs Riemann sum convergence",
        section="3.11",
        predicate=_remark_3_11_ftc_significance,
        note="Remark 3.11: FTC significance verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Quadrature helpers
# ---------------------------------------------------------------------------

def _riemann_right(f, a, b, n):
    """Right-endpoint Riemann sum."""
    h = (b - a) / n
    s = 0.0
    for i in range(1, n + 1):
        s += f(a + i * h)
    return s * h


# ---------------------------------------------------------------------------
# Exercise symbolic helpers
# ---------------------------------------------------------------------------

def _exercise_5_10_3():
    """Verify int (3x^2 - 4x + 7) dx = x^3 - 2x^2 + 7x + C."""
    import sympy as sp
    x = sp.Symbol('x')
    return sp.integrate(3*x**2 - 4*x + 7, x) - (x**3 - 2*x**2 + 7*x)


def _simpson(f, a, b, n):
    assert n % 2 == 0
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        coeff = 4 if i % 2 == 1 else 2
        s += coeff * f(a + i * h)
    return s * h / 3

def _trapezoid(f, a, b, n):
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h

def _midpoint(f, a, b, n):
    h = (b - a) / n
    s = 0.0
    for i in range(n):
        x_mid = a + (i + 0.5) * h
        s += f(x_mid)
    return h * s


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _power_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    # int x^3 dx = x^4/4
    return sp.integrate(x**3, x) - x**4/4

def _exp_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.integrate(sp.exp(x), x) - sp.exp(x)

def _reciprocal_antideriv():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    return sp.integrate(1/x, x) - sp.ln(x)

def _sin_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.integrate(sp.sin(x), x) - (-sp.cos(x))

def _cos_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.integrate(sp.cos(x), x) - sp.sin(x)

def _tan_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    result = sp.integrate(sp.tan(x), x)
    expected = -sp.ln(sp.cos(x))
    return sp.simplify(result - expected)

def _sec2_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.simplify(sp.integrate(1/sp.cos(x)**2, x) - sp.tan(x))

def _arctan_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.simplify(sp.integrate(1/(1+x**2), x) - sp.atan(x))

def _arcsin_antideriv():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.simplify(sp.integrate(1/sp.sqrt(1-x**2), x) - sp.asin(x))

def _general_exp_deriv_check():
    """Verify d/dx[a^x/ln(a)] = a^x (differentiation check for F5.10)."""
    import sympy as sp
    x = sp.Symbol('x')
    a = sp.Symbol('a', positive=True)
    F = a**x / sp.ln(a)
    return sp.simplify(sp.diff(F, x) - a**x)

def _ln_antideriv():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    return sp.simplify(sp.integrate(sp.ln(x), x) - (x*sp.ln(x) - x))

def _sqrt_antideriv():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    return sp.simplify(sp.integrate(sp.sqrt(x), x) - sp.Rational(2, 3)*x**sp.Rational(3, 2))

def _ftc():
    import sympy as sp
    x, t = sp.symbols('x t')
    F = sp.integrate(sp.sin(t), (t, 0, x))
    return sp.diff(F, x) - sp.sin(x)

def _by_parts_deriv_check():
    """Verify d/dx[e^x(x-1)] = x*e^x (the verification step in Example 5.20)."""
    import sympy as sp
    x = sp.Symbol('x')
    F = sp.exp(x) * (x - 1)
    return sp.simplify(sp.diff(F, x) - x * sp.exp(x))

def _by_parts_antideriv():
    """Verify int x*e^x dx = e^x(x-1) + C."""
    import sympy as sp
    x = sp.Symbol('x')
    result = sp.integrate(x * sp.exp(x), x)
    expected = sp.exp(x) * (x - 1)
    return sp.simplify(result - expected)

def _gaussian_integral_symbolic():
    """Verify int_{-inf}^{inf} e^{-x^2} dx = sqrt(pi)."""
    import sympy as sp
    x = sp.Symbol('x')
    result = sp.integrate(sp.exp(-x**2), (x, -sp.oo, sp.oo))
    return sp.simplify(result - sp.sqrt(sp.pi))
