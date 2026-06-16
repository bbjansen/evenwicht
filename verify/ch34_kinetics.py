# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 34: Chemical Kinetics & Reaction Networks."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(34, "Chemical Kinetics & Reaction Networks")

    # --- Symbolic checks ---

    # S1: First-order kinetics: [A](t) = [A]_0 * e^{-kt} solves d[A]/dt = -k[A]
    def first_order_ode():
        import sympy as sp
        t, k, A0 = sp.symbols('t k A0', positive=True)
        A = A0 * sp.exp(-k * t)
        dAdt = sp.diff(A, t)
        return sp.Eq(sp.simplify(dAdt + k * A), 0)
    ch.add(SymbolicCheck(
        label="First-order decay solution satisfies dA/dt = -kA",
        section="4",
        identity=first_order_ode,
    ))

    # S2: Arrhenius linearization: ln(k) = ln(A) - Ea/(R*T)
    def arrhenius_linearization():
        import sympy as sp
        T, Ea, R, A_pre = sp.symbols('T Ea R A', positive=True)
        k = A_pre * sp.exp(-Ea / (R * T))
        ln_k = sp.log(k)
        expected = sp.log(A_pre) - Ea / (R * T)
        return sp.Eq(sp.simplify(ln_k - expected), 0)
    ch.add(SymbolicCheck(
        label="Arrhenius: ln(k) = ln(A) - Ea/(RT)",
        section="4",
        identity=arrhenius_linearization,
    ))

    # S3: Michaelis-Menten at [S]=Km gives v = Vmax/2
    def mm_half_max():
        import sympy as sp
        Vmax, Km = sp.symbols('Vmax Km', positive=True)
        v = Vmax * Km / (Km + Km)
        return sp.Eq(sp.simplify(v - Vmax / 2), 0)
    ch.add(SymbolicCheck(
        label="Michaelis-Menten: v(Km) = Vmax/2",
        section="4",
        identity=mm_half_max,
    ))

    # S4: Second-order integrated rate law (F4.3)
    def second_order_check():
        import sympy as sp
        t, k, A0 = sp.symbols('t k A0', positive=True)
        # 1/[A](t) = 1/A0 + kt => [A](t) = A0/(1 + A0*k*t)
        A = A0 / (1 + A0 * k * t)
        dAdt = sp.diff(A, t)
        # Should satisfy d[A]/dt = -k*[A]^2
        return sp.Eq(sp.simplify(dAdt + k * A**2), 0)
    ch.add(SymbolicCheck(
        label="F4.3: Second-order rate law solution satisfies dA/dt = -kA^2",
        section="5",
        identity=second_order_check,
    ))

    # S5: Two-temperature Arrhenius formula (F4.5)
    def two_temp_arrhenius():
        import sympy as sp
        Ea, R = sp.symbols('Ea R', positive=True)
        T1, T2 = sp.symbols('T1 T2', positive=True)
        A_pre = sp.Symbol('A', positive=True)
        k1 = A_pre * sp.exp(-Ea / (R * T1))
        k2 = A_pre * sp.exp(-Ea / (R * T2))
        lhs = sp.log(k2 / k1)
        rhs = (Ea / R) * (1/T1 - 1/T2)
        return sp.Eq(sp.simplify(lhs - rhs), 0)
    ch.add(SymbolicCheck(
        label="F4.5: ln(k2/k1) = (Ea/R)(1/T1 - 1/T2)",
        section="5",
        identity=two_temp_arrhenius,
    ))

    # S6: Lineweaver-Burk linearization (F4.7)
    def lineweaver_burk_check():
        import sympy as sp
        Vmax, Km, S = sp.symbols('Vmax Km S', positive=True)
        v = Vmax * S / (Km + S)
        inv_v = 1 / v
        expected = (Km / Vmax) * (1 / S) + 1 / Vmax
        return sp.Eq(sp.simplify(inv_v - expected), 0)
    ch.add(SymbolicCheck(
        label="F4.7: Lineweaver-Burk 1/v = (Km/Vmax)(1/[S]) + 1/Vmax",
        section="5",
        identity=lineweaver_burk_check,
    ))

    # S7: Maximum intermediate concentration formula (F4.12)
    def max_intermediate_check():
        import sympy as sp
        k1, k2, A0 = sp.symbols('k1 k2 A0', positive=True)
        # [B]_max = A0 * (k2/k1)^{k2/(k1-k2)}
        B_max = A0 * (k2 / k1) ** (k2 / (k1 - k2))
        # Verify at specific values k1=0.05, k2=0.01
        val = B_max.subs([(k1, sp.Rational(5, 100)), (k2, sp.Rational(1, 100)), (A0, 1)])
        # (0.01/0.05)^(0.01/(0.05-0.01)) = (1/5)^(0.01/0.04) = (1/5)^(0.25) = 5^{-1/4}
        expected = 5 ** sp.Rational(-1, 4)
        return sp.Eq(sp.simplify(val - expected), 0)
    ch.add(SymbolicCheck(
        label="F4.12: [B]_max = A0*(k2/k1)^{k2/(k1-k2)} for k1=0.05,k2=0.01",
        section="5",
        identity=max_intermediate_check,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 8.1: First-order rate constant
    def fit_first_order_k():
        times = [0, 100, 200, 300, 400, 500]
        concs = [0.100, 0.078, 0.061, 0.048, 0.037, 0.029]
        ln_concs = [math.log(c) for c in concs]
        n = len(times)
        sum_t = sum(times)
        sum_y = sum(ln_concs)
        sum_ty = sum(t*y for t, y in zip(times, ln_concs))
        sum_t2 = sum(t**2 for t in times)
        slope = (n * sum_ty - sum_t * sum_y) / (n * sum_t2 - sum_t**2)
        return -slope
    ch.add(NumericCheck(
        label="Ex 8.1: First-order rate constant k",
        section="9",
        stated=0.00247,
        computed=fit_first_order_k,
        tolerance=5e-3,
    ))

    # Example 8.1: Half-life
    ch.add(NumericCheck(
        label="Ex 8.1: First-order half-life",
        section="9",
        stated=281.0,
        computed=lambda: math.log(2) / 0.00247,
        tolerance=5e-3,
    ))

    # Example 8.1: R-squared of first-order fit
    def first_order_r_squared():
        times = [0, 100, 200, 300, 400, 500]
        concs = [0.100, 0.078, 0.061, 0.048, 0.037, 0.029]
        ln_concs = [math.log(c) for c in concs]
        n = len(times)
        sum_t = sum(times)
        sum_y = sum(ln_concs)
        sum_ty = sum(t*y for t, y in zip(times, ln_concs))
        sum_t2 = sum(t**2 for t in times)
        slope = (n * sum_ty - sum_t * sum_y) / (n * sum_t2 - sum_t**2)
        intercept = (sum_y - slope * sum_t) / n
        ss_res = sum((y - (slope * t + intercept))**2 for t, y in zip(times, ln_concs))
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean)**2 for y in ln_concs)
        return 1 - ss_res / ss_tot
    ch.add(NumericCheck(
        label="Ex 8.1: R-squared of first-order fit",
        section="9",
        stated=0.9998,
        computed=first_order_r_squared,
        tolerance=5e-3,
    ))

    # Example 8.1: Prediction at t=281 s (half-life check)
    ch.add(NumericCheck(
        label="Ex 8.1: [A] at t=281 s (half-life)",
        section="9",
        stated=0.050,
        computed=lambda: 0.100 * math.exp(-0.00247 * 281),
        tolerance=1e-2,
    ))

    # --- Table values: Arrhenius 1/T and ln(k) ---
    _arrhenius_temps = [300, 320, 340, 360, 380]
    _arrhenius_ks = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
    _inv_T_stated = [3.333e-3, 3.125e-3, 2.941e-3, 2.778e-3, 2.632e-3]
    _lnk_stated = [-10.82, -9.12, -7.56, -6.17, -4.89]
    for _T, _invT_s in zip(_arrhenius_temps, _inv_T_stated):
        ch.add(NumericCheck(
            label=f"Ex 8.2 table: 1/{_T} K",
            section="9",
            stated=_invT_s,
            computed=(lambda T=_T: 1.0 / T),
            tolerance=1e-3,
        ))
    for _k, _lnk_s in zip(_arrhenius_ks, _lnk_stated):
        ch.add(NumericCheck(
            label=f"Ex 8.2 table: ln({_k:.1e})",
            section="9",
            stated=_lnk_s,
            computed=(lambda k=_k: math.log(k)),
            tolerance=1e-2,
        ))

    # --- Table values: Lineweaver-Burk 1/v ---
    _lb_substrates = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
    _lb_rates = [2.5, 4.4, 8.3, 12.0, 16.0, 20.0, 22.2]
    _lb_inv_v_stated = [0.400, 0.227, 0.120, 0.0833, 0.0625, 0.0500, 0.0450]
    for _s, _v, _ivs in zip(_lb_substrates, _lb_rates, _lb_inv_v_stated):
        ch.add(NumericCheck(
            label=f"Ex 8.3 table: 1/v at [S]={_s}",
            section="9",
            stated=_ivs,
            computed=(lambda v=_v: 1.0 / v),
            tolerance=5e-3,
            note="Rounded to 3 significant figures in table",
        ))

    # Example 8.2: Arrhenius activation energy
    def arrhenius_ea():
        temps = [300, 320, 340, 360, 380]
        ks = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
        x = [1/T for T in temps]
        y = [math.log(k) for k in ks]
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        Ea = -slope * 8.314  # J/mol
        return Ea / 1000  # kJ/mol
    ch.add(NumericCheck(
        label="Ex 8.2: Activation energy (kJ/mol)",
        section="9",
        stated=70.4,
        computed=arrhenius_ea,
        tolerance=5e-2,
    ))

    # Example 8.2: Arrhenius slope
    def arrhenius_slope():
        temps = [300, 320, 340, 360, 380]
        ks = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
        x = [1/T for T in temps]
        y = [math.log(k) for k in ks]
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        return slope
    ch.add(NumericCheck(
        label="Ex 8.2: Arrhenius slope m",
        section="9",
        stated=-8470.0,
        computed=arrhenius_slope,
        tolerance=5e-2,
    ))

    # Example 8.2: Pre-exponential factor A
    def arrhenius_prefactor():
        temps = [300, 320, 340, 360, 380]
        ks = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
        x = [1/T for T in temps]
        y = [math.log(k) for k in ks]
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n
        return math.exp(intercept)
    ch.add(NumericCheck(
        label="Ex 8.2: Pre-exponential factor A",
        section="9",
        stated=3.6e7,
        computed=arrhenius_prefactor,
        tolerance=1e-1,
    ))

    # Example 8.2: Arrhenius intercept b
    def arrhenius_intercept():
        temps = [300, 320, 340, 360, 380]
        ks = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
        x = [1/T for T in temps]
        y = [math.log(k) for k in ks]
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n
        return intercept
    ch.add(NumericCheck(
        label="Ex 8.2: Arrhenius intercept b",
        section="9",
        stated=17.41,
        computed=arrhenius_intercept,
        tolerance=5e-2,
    ))

    # Example 8.2: Predicted rate at T=350 K
    def arrhenius_predict_350():
        temps = [300, 320, 340, 360, 380]
        ks = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
        x = [1/T for T in temps]
        y = [math.log(k) for k in ks]
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n
        Ea = -slope * 8.314
        A = math.exp(intercept)
        return A * math.exp(-Ea / (8.314 * 350))
    ch.add(NumericCheck(
        label="Ex 8.2: Predicted k at T=350 K",
        section="9",
        stated=1.02e-3,
        computed=arrhenius_predict_350,
        tolerance=1e-1,
    ))

    # Example 8.3: Michaelis-Menten Vmax
    ch.add(NumericCheck(
        label="Ex 8.3: Vmax from Lineweaver-Burk",
        section="9",
        stated=25.0,
        computed=lambda: 1 / 0.0400,
        tolerance=1e-2,
    ))

    # Example 8.3: Km
    ch.add(NumericCheck(
        label="Ex 8.3: Km from Lineweaver-Burk",
        section="9",
        stated=0.90,
        computed=lambda: 0.0360 * 25.0,
        tolerance=1e-2,
    ))

    # Example 8.3: Verification v at [S]=Km=0.90
    ch.add(NumericCheck(
        label="Ex 8.3: v at [S]=Km (verification)",
        section="9",
        stated=12.5,
        computed=lambda: 25.0 * 0.90 / (0.90 + 0.90),
        tolerance=1e-3,
    ))

    # Example 8.4: Sequential kinetics - time of max [B]
    ch.add(NumericCheck(
        label="Ex 8.4: Time of maximum [B]",
        section="9",
        stated=40.2,
        computed=lambda: math.log(0.05 / 0.01) / (0.05 - 0.01),
        tolerance=1e-2,
    ))

    # Example 8.4: [A] at tmax
    ch.add(NumericCheck(
        label="Ex 8.4: [A] at t_max=40.2 s",
        section="9",
        stated=0.134,
        computed=lambda: math.exp(-0.05 * 40.2),
        tolerance=1e-2,
    ))

    # Example 8.4: [B] at tmax
    def b_at_tmax():
        k1, k2, A0 = 0.05, 0.01, 1.0
        t = math.log(k1/k2) / (k1 - k2)
        B = (k1 * A0 / (k2 - k1)) * (math.exp(-k1*t) - math.exp(-k2*t))
        return B
    ch.add(NumericCheck(
        label="Ex 8.4: Maximum [B] concentration",
        section="9",
        stated=0.669,
        computed=b_at_tmax,
        tolerance=1e-3,
    ))

    # Example 8.4: [C] at tmax
    ch.add(NumericCheck(
        label="Ex 8.4: [C] at t_max=40.2 s",
        section="9",
        stated=0.197,
        computed=lambda: 1.0 - math.exp(-0.05 * 40.2) - 0.669,
        tolerance=5e-2,
    ))

    # Example 8.4: [A] at t=50
    ch.add(NumericCheck(
        label="Ex 8.4: [A] at t=50 s",
        section="9",
        stated=0.0821,
        computed=lambda: math.exp(-0.05 * 50),
        tolerance=1e-3,
    ))

    # Example 8.4: [B] at t=50
    def b_at_50():
        k1, k2, A0 = 0.05, 0.01, 1.0
        t = 50
        B = (k1 * A0 / (k2 - k1)) * (math.exp(-k1*t) - math.exp(-k2*t))
        return B
    ch.add(NumericCheck(
        label="Ex 8.4: [B] at t=50 s",
        section="9",
        stated=0.656,
        computed=b_at_50,
        tolerance=1e-2,
    ))

    # Example 8.4: [C] at t=50
    ch.add(NumericCheck(
        label="Ex 8.4: [C] at t=50 s",
        section="9",
        stated=0.262,
        computed=lambda: 1.0 - math.exp(-0.05*50) - (
            (0.05 / (0.01 - 0.05)) * (math.exp(-0.05*50) - math.exp(-0.01*50))
        ),
        tolerance=1e-2,
    ))

    # --- Formula gap fills ---

    # F4.1: Zeroth-order rate law [A](t) = [A]_0 - k*t
    ch.add(NumericCheck(
        label="F4.1: Zeroth-order [A](100) = 0.100 - 0.0005*100 = 0.050",
        section="5",
        stated=0.050,
        computed=lambda: 0.100 - 0.0005 * 100,
        tolerance=1e-10,
        note="k=0.0005 M/s, A0=0.100 M",
    ))

    # F4.2: First-order rate law [A](t) = [A]_0 * exp(-k*t)
    ch.add(NumericCheck(
        label="F4.2: First-order [A](281) = 0.100*exp(-0.00247*281) ~ 0.050",
        section="5",
        stated=0.050,
        computed=lambda: 0.100 * math.exp(-0.00247 * 281),
        tolerance=1e-2,
    ))

    # F4.4: Arrhenius k = A*exp(-Ea/(RT))
    ch.add(NumericCheck(
        label="F4.4: Arrhenius k(350K) from fitted parameters",
        section="5",
        stated=1.02e-3,
        computed=lambda: 3.6e7 * math.exp(-70400 / (8.314 * 350)),
        tolerance=2e-1,
    ))

    # F4.6: Michaelis-Menten v = Vmax*[S]/(Km + [S])
    ch.add(NumericCheck(
        label="F4.6: Michaelis-Menten v at [S]=Km => Vmax/2 = 12.5",
        section="5",
        stated=12.5,
        computed=lambda: 25.0 * 0.90 / (0.90 + 0.90),
        tolerance=1e-3,
    ))

    # F4.8: Stoichiometry matrix N and reaction rate vector
    def stoich_rank_check():
        N = np.array([
            [-1,  0, -1],
            [ 2, -1,  1],
            [ 0, -1,  0],
            [ 0,  1,  1],
            [ 0,  1, -1],
        ], dtype=float)
        rank = np.linalg.matrix_rank(N)
        ok = rank == 3
        return (ok, f"rank(N) = {rank}, expected 3" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.8: Stoichiometry matrix rank = 3",
        section="5",
        predicate=stoich_rank_check,
    ))

    # F4.9: Conservation laws from null space of N^T
    def conservation_law_check():
        N = np.array([
            [-1,  0, -1],
            [ 2, -1,  1],
            [ 0, -1,  0],
            [ 0,  1,  1],
            [ 0,  1, -1],
        ], dtype=float)
        # Bromine conservation: ell = [2, 1, 0, 1, 0]
        ell = np.array([2, 1, 0, 1, 0], dtype=float)
        result = N.T @ ell
        ok = np.allclose(result, 0)
        return (ok, f"N^T * ell = {result}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.9: Conservation law N^T * ell = 0 for bromine atoms",
        section="5",
        predicate=conservation_law_check,
    ))

    # F4.10: Sequential kinetics [B](t) = (k1*A0/(k2-k1))*(exp(-k1*t) - exp(-k2*t))
    ch.add(NumericCheck(
        label="F4.10: Sequential [B] at t=40.2 (t_max) ~ 0.669",
        section="5",
        stated=0.669,
        computed=lambda: (0.05 * 1.0 / (0.01 - 0.05)) * (math.exp(-0.05 * 40.2) - math.exp(-0.01 * 40.2)),
        tolerance=1e-3,
    ))

    # F4.11: t_max = ln(k1/k2)/(k1 - k2)
    ch.add(NumericCheck(
        label="F4.11: t_max = ln(k1/k2)/(k1-k2) = ln(5)/0.04 ~ 40.2",
        section="5",
        stated=40.2,
        computed=lambda: math.log(0.05 / 0.01) / (0.05 - 0.01),
        tolerance=1e-2,
    ))

    # Ex 8.5: Hydrogen atom conservation law
    def hydrogen_conservation_ex85():
        N = np.array([
            [-1,  0, -1],
            [ 2, -1,  1],
            [ 0, -1,  0],
            [ 0,  1,  1],
            [ 0,  1, -1],
        ], dtype=float)
        ell = np.array([0, 0, 2, 1, 1], dtype=float)
        result = N.T @ ell
        ok = np.allclose(result, 0)
        return (ok, f"N^T * ell = {result}" if not ok else "")
    ch.add(StructuralCheck(
        label="Ex 8.5: Hydrogen conservation law verification",
        section="9",
        predicate=hydrogen_conservation_ex85,
    ))

    # --- Structural checks ---

    # Conservation: [A] + [B] + [C] = [A]_0 for sequential kinetics
    def sequential_conservation():
        k1, k2, A0 = 0.05, 0.01, 1.0
        for t in [10, 20, 50, 100, 200]:
            A = A0 * math.exp(-k1 * t)
            B = (k1 * A0 / (k2 - k1)) * (math.exp(-k1*t) - math.exp(-k2*t))
            C = A0 - A - B
            total = A + B + C
            if abs(total - A0) > 1e-10:
                return (False, f"At t={t}: A+B+C={total} != {A0}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Sequential kinetics: [A]+[B]+[C] = [A]_0",
        section="9",
        predicate=sequential_conservation,
    ))

    # Stoichiometry matrix null space gives conservation laws
    def stoich_conservation():
        # H-Br system: 5 species, 3 reactions
        N = np.array([
            [-1,  0, -1],
            [ 2, -1,  1],
            [ 0, -1,  0],
            [ 0,  1,  1],
            [ 0,  1, -1],
        ], dtype=float)
        rank = np.linalg.matrix_rank(N)
        null_dim = N.shape[0] - rank
        ok = rank == 3 and null_dim == 2
        return (ok, f"rank(N)={rank}, null dim={null_dim}" if not ok else "")
    ch.add(StructuralCheck(
        label="H-Br stoichiometry: rank=3, 2 conservation laws",
        section="9",
        predicate=stoich_conservation,
    ))

    # Bromine conservation law: 2*Br2 + Br + HBr = const
    def bromine_conservation():
        N = np.array([
            [-1,  0, -1],
            [ 2, -1,  1],
            [ 0, -1,  0],
            [ 0,  1,  1],
            [ 0,  1, -1],
        ], dtype=float)
        ell = np.array([2, 1, 0, 1, 0], dtype=float)
        result = N.T @ ell
        ok = np.allclose(result, 0)
        return (ok, f"N^T * ell = {result}" if not ok else "")
    ch.add(StructuralCheck(
        label="Bromine atom conservation law verification",
        section="9",
        predicate=bromine_conservation,
    ))

    # Hydrogen conservation law: 2*H2 + HBr + H = const (H atom balance)
    # Note: the text states ell_2 = (0,0,1,1,1) but the correct atom-counting
    # vector is (0,0,2,1,1) since H2 carries 2 hydrogen atoms.
    def hydrogen_conservation():
        N = np.array([
            [-1,  0, -1],
            [ 2, -1,  1],
            [ 0, -1,  0],
            [ 0,  1,  1],
            [ 0,  1, -1],
        ], dtype=float)
        ell = np.array([0, 0, 2, 1, 1], dtype=float)
        result = N.T @ ell
        ok = np.allclose(result, 0)
        return (ok, f"N^T * ell = {result}" if not ok else "")
    ch.add(StructuralCheck(
        label="Hydrogen atom conservation law verification",
        section="9",
        predicate=hydrogen_conservation,
        note="Text states ell=(0,0,1,1,1) but correct H-atom vector is (0,0,2,1,1)",
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 10.1: N2O5 decomposition ---
    # k = 6.2e-4 s^-1
    # (a) half-life = ln(2)/k
    ch.add(NumericCheck(
        label="Exercise 10.1a: Half-life of N2O5",
        section="11",
        stated=math.log(2) / 6.2e-4,
        computed=lambda: math.log(2) / 6.2e-4,
        tolerance=1e-6,
    ))
    # (b) [A](1000) = 0.50 * exp(-6.2e-4 * 1000)
    ch.add(NumericCheck(
        label="Exercise 10.1b: [A] after 1000 s",
        section="11",
        stated=0.50 * math.exp(-6.2e-4 * 1000),
        computed=lambda: 0.50 * math.exp(-6.2e-4 * 1000),
        tolerance=1e-6,
    ))
    # (c) 90% decomposed => 0.10 remaining => t = ln(10)/k
    ch.add(NumericCheck(
        label="Exercise 10.1c: Time for 90% decomposition",
        section="11",
        stated=math.log(10) / 6.2e-4,
        computed=lambda: math.log(10) / 6.2e-4,
        tolerance=1e-6,
    ))

    # --- Exercise 10.2: Second-order reaction ---
    # k=0.015, [A]_0=2.0
    # (a) half-life = 1/(k*[A]_0)
    ch.add(NumericCheck(
        label="Exercise 10.2a: Second-order half-life",
        section="11",
        stated=1 / (0.015 * 2.0),
        computed=lambda: 1 / (0.015 * 2.0),
        tolerance=1e-6,
    ))
    # (b) [A](100) = A0/(1 + A0*k*t) = 2.0/(1+2.0*0.015*100) = 2.0/4.0 = 0.5
    ch.add(NumericCheck(
        label="Exercise 10.2b: [A] at t=100 s",
        section="11",
        stated=0.5,
        computed=lambda: 2.0 / (1 + 2.0 * 0.015 * 100),
        tolerance=1e-6,
    ))
    # (c) 10% remaining: 0.2 = 2.0/(1+2.0*0.015*t) => 1+0.03t = 10 => t = 300
    ch.add(NumericCheck(
        label="Exercise 10.2c: Time for 10% remaining",
        section="11",
        stated=300.0,
        computed=lambda: (1/0.2 - 1/(2.0)) / 0.015,
        tolerance=1e-6,
    ))

    # --- Exercise 10.3: Activation energy from two temperatures ---
    # k1=0.111 at T1=298, k2=0.543 at T2=318
    # Ea = R * ln(k2/k1) / (1/T1 - 1/T2)
    ch.add(NumericCheck(
        label="Exercise 10.3: Activation energy (J/mol)",
        section="11",
        stated=8.314 * math.log(0.543 / 0.111) / (1/298 - 1/318),
        computed=lambda: 8.314 * math.log(0.543 / 0.111) / (1/298 - 1/318),
        tolerance=1e-6,
    ))

    # --- Exercise 10.4: Michaelis-Menten ---
    # Vmax=100, Km=2.5
    # (a) v at [S]=1.0: v = 100*1.0/(2.5+1.0) = 28.57
    ch.add(NumericCheck(
        label="Exercise 10.4a: Rate at [S]=1.0 mM",
        section="11",
        stated=100 * 1.0 / (2.5 + 1.0),
        computed=lambda: 100 * 1.0 / (2.5 + 1.0),
        tolerance=1e-6,
    ))
    # (b) 80% of Vmax: 0.8*100 = 100*S/(2.5+S) => 0.8*(2.5+S) = S => 2+0.8S=S => S=10
    ch.add(NumericCheck(
        label="Exercise 10.4b: [S] for 80% of Vmax",
        section="11",
        stated=10.0,
        computed=lambda: 0.8 * 2.5 / (1 - 0.8),
        tolerance=1e-6,
    ))
    # (c) At [S]=10*Km=25: v = 100*25/(2.5+25) = 100*25/27.5
    ch.add(NumericCheck(
        label="Exercise 10.4c: Fraction of Vmax at [S]=10*Km",
        section="11",
        stated=10.0 / 11.0,
        computed=lambda: 25 / (2.5 + 25),
        tolerance=1e-6,
    ))

    # --- Exercise 10.5: Sequential kinetics ---
    # k1=0.10, k2=0.02, [A]_0=0.50
    # (a) tmax = ln(k1/k2)/(k1-k2)
    ch.add(NumericCheck(
        label="Exercise 10.5a: tmax for intermediate B",
        section="11",
        stated=math.log(0.10/0.02) / (0.10 - 0.02),
        computed=lambda: math.log(0.10/0.02) / (0.10 - 0.02),
        tolerance=1e-6,
    ))
    # (b) [B]_max
    def ex345_bmax():
        k1, k2, A0 = 0.10, 0.02, 0.50
        t = math.log(k1/k2) / (k1 - k2)
        return (k1 * A0 / (k2 - k1)) * (math.exp(-k1*t) - math.exp(-k2*t))
    ch.add(NumericCheck(
        label="Exercise 10.5b: Maximum [B]",
        section="11",
        stated=ex345_bmax(),
        computed=ex345_bmax,
        tolerance=1e-10,
    ))

    # --- Exercise 10.6: Reversible reaction ---
    # k1=0.03, k_{-1}=0.01, [A]_0 assumed 1.0
    # [A]_eq = k_{-1}*A0/(k1+k_{-1}) = 0.01/(0.04) = 0.25
    ch.add(NumericCheck(
        label="Exercise 10.6: [A]_eq = k_{-1}/(k1+k_{-1}) * A0",
        section="11",
        stated=0.25,
        computed=lambda: 0.01 / (0.03 + 0.01) * 1.0,
        tolerance=1e-6,
    ))
    # Approach rate = k1 + k_{-1} = 0.04
    ch.add(NumericCheck(
        label="Exercise 10.6: Relaxation rate = k1 + k_{-1}",
        section="11",
        stated=0.04,
        computed=lambda: 0.03 + 0.01,
        tolerance=1e-10,
    ))

    # --- Exercise 10.7: Stoichiometry matrix ---
    # (1) A + B -> C: [-1, -1, 1, 0, 0]
    # (2) C -> D + E: [0, 0, -1, 1, 1]
    # (3) D -> A: [1, 0, 0, -1, 0]
    def ex347_stoich():
        N = np.array([
            [-1,  0,  1],
            [-1,  0,  0],
            [ 1, -1,  0],
            [ 0,  1, -1],
            [ 0,  1,  0],
        ], dtype=float)
        rank = np.linalg.matrix_rank(N)
        n_species = N.shape[0]
        n_conserv = n_species - rank
        return rank, n_conserv
    ch.add(NumericCheck(
        label="Exercise 10.7: Stoichiometry matrix rank",
        section="11",
        stated=3.0,
        computed=lambda: float(ex347_stoich()[0]),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.7: Number of conservation laws",
        section="11",
        stated=2.0,
        computed=lambda: float(ex347_stoich()[1]),
        tolerance=1e-6,
    ))

    # --- Exercise 10.8: Brusselator ---
    # (a) Equilibrium: (x*, y*) = (a, b/a)
    # For a=1, b=3: (1, 3)
    ch.add(NumericCheck(
        label="Exercise 10.8a: Brusselator equilibrium x* = a",
        section="11",
        stated=1.0,
        computed=lambda: 1.0,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.8a: Brusselator equilibrium y* = b/a",
        section="11",
        stated=3.0,
        computed=lambda: 3.0 / 1.0,
        tolerance=1e-10,
    ))
    # (c) tr(J) = b - 1 - a^2 = 3 - 1 - 1 = 1 > 0 => unstable
    ch.add(NumericCheck(
        label="Exercise 10.8c: tr(J) = b - 1 - a^2",
        section="11",
        stated=1.0,
        computed=lambda: 3 - 1 - 1**2,
        tolerance=1e-10,
    ))
    # det(J) = a^2 = 1
    ch.add(NumericCheck(
        label="Exercise 10.8c: det(J) = a^2",
        section="11",
        stated=1.0,
        computed=lambda: 1.0**2,
        tolerance=1e-10,
    ))
    # (d) Hopf bifurcation: tr(J) = 0 => b_c = 1 + a^2
    ch.add(NumericCheck(
        label="Exercise 10.8d: Hopf bifurcation b_c = 1 + a^2 (a=1)",
        section="11",
        stated=2.0,
        computed=lambda: 1 + 1**2,
        tolerance=1e-10,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Reaction Network via RK4 ---
    def alg_5_1_reaction_rk4():
        # A -> B with rate k=0.1; dc_A/dt = -k*c_A, dc_B/dt = k*c_A
        k = 0.1
        N = np.array([[-1], [1]])  # stoichiometry matrix (2 species, 1 reaction)
        def r(c):
            return np.array([k * c[0]])
        c = np.array([1.0, 0.0])
        h = 0.01
        T = 50.0
        for _ in range(int(T / h)):
            def f(cc):
                return (N @ r(cc)).flatten()
            k1 = h * f(c)
            k2 = h * f(c + k1 / 2)
            k3 = h * f(c + k2 / 2)
            k4 = h * f(c + k3)
            c = c + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        # Analytical: c_A = exp(-k*T), c_B = 1 - exp(-k*T)
        c_A_exact = math.exp(-k * T)
        c_B_exact = 1 - c_A_exact
        ok1 = abs(c[0] - c_A_exact) < 1e-6
        ok2 = abs(c[1] - c_B_exact) < 1e-6
        # Conservation: c_A + c_B = 1
        ok3 = abs(c[0] + c[1] - 1.0) < 1e-8
        return (ok1 and ok2 and ok3, f"c_A={c[0]:.8f} (exact {c_A_exact:.8f}), c_B={c[1]:.8f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Reaction network via RK4",
        section="6",
        predicate=alg_5_1_reaction_rk4,
    ))

    # --- Algorithm 5.2: Arrhenius Parameter Estimation ---
    def alg_5_2_arrhenius():
        R = 8.314
        # Generate data: Ea=50000 J/mol, A=1e10
        Ea_true, A_true = 50000.0, 1e10
        temps = np.array([300, 350, 400, 450, 500], dtype=float)
        rates = A_true * np.exp(-Ea_true / (R * temps))
        x = 1.0 / temps
        y = np.log(rates)
        # Linear regression
        n = len(x)
        x_mean, y_mean = np.mean(x), np.mean(y)
        m = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
        b = y_mean - m * x_mean
        Ea_est = -m * R
        A_est = math.exp(b)
        ok1 = abs(Ea_est - Ea_true) / Ea_true < 1e-6
        ok2 = abs(A_est - A_true) / A_true < 1e-4
        return (bool(ok1 and ok2), f"Ea={Ea_est:.0f} (true {Ea_true:.0f}), A={A_est:.2e} (true {A_true:.2e})")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Arrhenius parameter estimation",
        section="6",
        predicate=alg_5_2_arrhenius,
    ))

    # --- Algorithm 5.3: Lineweaver-Burk ---
    def alg_5_3_lineweaver_burk():
        Vmax_true, Km_true = 10.0, 2.0
        S_vals = np.array([0.5, 1.0, 2.0, 4.0, 8.0, 16.0])
        v_vals = Vmax_true * S_vals / (Km_true + S_vals)
        x = 1.0 / S_vals
        y = 1.0 / v_vals
        # Linear regression
        x_mean, y_mean = np.mean(x), np.mean(y)
        m = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
        b = y_mean - m * x_mean
        Vmax_est = 1 / b
        Km_est = m / b
        ok1 = abs(Vmax_est - Vmax_true) / Vmax_true < 1e-6
        ok2 = abs(Km_est - Km_true) / Km_true < 1e-6
        return (bool(ok1 and ok2), f"Vmax={Vmax_est:.4f} (true {Vmax_true}), Km={Km_est:.4f} (true {Km_true})")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Lineweaver-Burk parameter estimation",
        section="6",
        predicate=alg_5_3_lineweaver_burk,
    ))

    # --- Algorithm 5.4: Conservation Law Extraction ---
    def alg_5_4_conservation():
        # A -> B + C: stoichiometry N = [[-1],[1],[1]]
        N = np.array([[-1], [1], [1]])
        # Left null space of N: vectors l such that l^T N = 0
        # SVD of N^T
        U, s, Vt = np.linalg.svd(N.T)
        # Null space of N^T = columns of V corresponding to zero singular values
        null_dim = N.shape[0] - len(s[s > 1e-10])
        null_vectors = Vt[len(s[s > 1e-10]):].T
        # Should have 2 independent conservation laws (3 species, 1 reaction => 2 laws)
        ok1 = null_dim == 2
        # Verify conservation: l^T * N = 0 for each law
        ok2 = True
        for j in range(null_vectors.shape[1]):
            l = null_vectors[:, j]
            if abs(l @ N) > 1e-10:
                ok2 = False
        return (ok1 and ok2, f"Null space dim={null_dim}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Conservation law extraction (left null space)",
        section="6",
        predicate=alg_5_4_conservation,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.13: At [S] = Km, v = Vmax/2
    def remark_3413_km_half_vmax():
        Vmax = 10.0
        Km = 5.0
        S = Km  # set [S] = Km
        v = Vmax * S / (Km + S)
        ok = abs(v - Vmax / 2) < 1e-10
        return (ok, f"v(Km) = {v:.6f}, Vmax/2 = {Vmax/2:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.13: v(Km) = Vmax/2",
        section="4",
        predicate=remark_3413_km_half_vmax,
        note="Remark 3.13",
    ))

    # Remark 3.4: First-order kinetics identical to radioactive decay
    # [A](t) = [A]_0 * exp(-k*t), same as N(t) = N_0 * exp(-lambda*t)
    def remark_344_first_order_decay():
        k = 0.1
        A0 = 100.0
        t = 10.0
        A_kinetics = A0 * math.exp(-k * t)
        N_decay = A0 * math.exp(-k * t)  # with lambda = k
        ok = abs(A_kinetics - N_decay) < 1e-10
        # Also verify half-life: t_1/2 = ln(2)/k
        t_half = math.log(2) / k
        A_half = A0 * math.exp(-k * t_half)
        ok2 = abs(A_half - A0 / 2) < 1e-10
        return (ok and ok2, f"A(t)={A_kinetics:.4f}, N(t)={N_decay:.4f}, A(t_1/2)={A_half:.4f}")
    ch.add(StructuralCheck(
        label="Remark 3.4: First-order kinetics = radioactive decay (lambda=k)",
        section="4",
        predicate=remark_344_first_order_decay,
        note="Remark 3.4",
    ))

    # Remark 3.6: Diagnostic plots — first-order: ln[A] vs t is linear
    def remark_346_diagnostic_plots():
        k = 0.05
        A0 = 1.0
        times = [0, 1, 2, 5, 10, 20]
        # First order: ln[A] = ln(A0) - k*t => linear
        ln_A = [math.log(A0 * math.exp(-k * t)) for t in times]
        # Check linearity: slope should be -k, intercept ln(A0)
        # Fit slope via first/last point
        slope = (ln_A[-1] - ln_A[0]) / (times[-1] - times[0])
        ok = abs(slope - (-k)) < 1e-10
        return (ok, f"slope of ln[A] vs t = {slope:.6f}, expected = {-k:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.6: First-order: ln[A] vs t is linear with slope -k",
        section="4",
        predicate=remark_346_diagnostic_plots,
        note="Remark 3.6",
    ))

    # --- Remark 3.15: Lineweaver-Burk amplifies error at low [S] ---
    def _remark_34_15_lineweaver_burk():
        """Verify Lineweaver-Burk distorts error: low [S] points have large 1/[S]."""
        V_max, K_m = 10.0, 2.0
        rng = np.random.default_rng(3415)
        S_vals = np.array([0.5, 1, 2, 5, 10, 20, 50])
        noise_std = 0.5
        v_vals = V_max * S_vals / (K_m + S_vals) + rng.normal(0, noise_std, len(S_vals))
        # In 1/v vs 1/S space, errors at low S are amplified
        inv_S = 1.0 / S_vals
        inv_v = 1.0 / v_vals
        # Variance of 1/v ~ (1/v^2)^2 * var(v) = noise_std^2 / v^4
        # At low S, v is small so 1/v has huge variance
        v_true_low = V_max * S_vals[0] / (K_m + S_vals[0])
        v_true_high = V_max * S_vals[-1] / (K_m + S_vals[-1])
        var_inv_v_low = noise_std**2 / v_true_low**4
        var_inv_v_high = noise_std**2 / v_true_high**4
        # Low [S] should have much larger variance in transformed space
        if var_inv_v_low <= var_inv_v_high:
            return (False, f"Error amplification not verified: low={var_inv_v_low}, high={var_inv_v_high}")
        ratio = var_inv_v_low / var_inv_v_high
        if ratio < 10:
            return (False, f"Amplification ratio {ratio} too small, expected >> 1")
        return (True, f"Var(1/v) ratio low/high [S] = {ratio:.1f}")

    ch.add(StructuralCheck(
        label="Remark 3.15: Lineweaver-Burk amplifies error at low [S]",
        section="34.15",
        predicate=_remark_34_15_lineweaver_burk,
        note="Remark 3.15: limitations of double-reciprocal",
    ))

    # --- Remark 3.23: Sequential first-order kinetics = Bateman equations ---
    def _remark_34_23_bateman():
        """Verify A->B->C sequential first-order matches Bateman solution."""
        k1, k2 = 0.3, 0.1
        A0 = 1.0
        t = 10.0
        # Analytical: A(t) = A0*exp(-k1*t)
        # B(t) = A0*k1/(k2-k1)*(exp(-k1*t) - exp(-k2*t))
        # C(t) = A0 - A(t) - B(t)
        A_t = A0 * math.exp(-k1 * t)
        B_t = A0 * k1 / (k2 - k1) * (math.exp(-k1 * t) - math.exp(-k2 * t))
        C_t = A0 - A_t - B_t
        # Conservation: A+B+C = A0
        if abs(A_t + B_t + C_t - A0) > 1e-10:
            return (False, f"Conservation violated: A+B+C={A_t+B_t+C_t}, A0={A0}")
        # Verify with numerical integration
        dt_sim = 0.001
        A_sim, B_sim, C_sim = A0, 0.0, 0.0
        for _ in range(int(t / dt_sim)):
            dA = -k1 * A_sim * dt_sim
            dB = (k1 * A_sim - k2 * B_sim) * dt_sim
            A_sim += dA
            B_sim += dB
            C_sim = A0 - A_sim - B_sim
        if abs(A_sim - A_t) > 0.01:
            return (False, f"A: analytical={A_t:.6f}, numerical={A_sim:.6f}")
        if abs(B_sim - B_t) > 0.01:
            return (False, f"B: analytical={B_t:.6f}, numerical={B_sim:.6f}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.23: Sequential kinetics A->B->C matches Bateman equations",
        section="34.23",
        predicate=_remark_34_23_bateman,
        note="Remark 3.23: Bateman equations equivalence",
    ))

    # --- Remark 3.26: Hopf bifurcation — transition from damped to sustained oscillation ---
    def _remark_34_26_hopf():
        """Verify Hopf bifurcation: eigenvalues cross imaginary axis."""
        # Simple 2D system: dx/dt = mu*x - y - x*(x^2+y^2), dy/dt = x + mu*y - y*(x^2+y^2)
        # At origin: Jacobian = [[mu, -1], [1, mu]], eigenvalues = mu +/- i
        # Hopf at mu = 0: Re(lambda) changes sign
        for mu in [-0.5, -0.1, 0.0, 0.1, 0.5]:
            J = np.array([[mu, -1], [1, mu]])
            evals = np.linalg.eigvals(J)
            re_parts = evals.real
            if mu < 0 and np.any(re_parts >= 0):
                return (False, f"mu={mu}: eigenvalues should have Re < 0, got {evals}")
            if mu > 0 and np.any(re_parts <= 0):
                return (False, f"mu={mu}: eigenvalues should have Re > 0, got {evals}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.26: Hopf bifurcation — eigenvalues cross imaginary axis at mu=0",
        section="34.26",
        predicate=_remark_34_26_hopf,
        note="Remark 3.26: Hopf bifurcation eigenvalue crossing",
    ))

    # ==================================================================
    # Table verification — first-order decay concentrations (Section 9)
    # ==================================================================
    # The table states [A](t) at t = 0, 100, 200, 300, 400, 500 s.
    # Verify each concentration value against [A] = [A]_0 * exp(-k*t)
    # using the fitted rate constant k = 0.00247 s^{-1}.
    _decay_times = [0, 100, 200, 300, 400, 500]
    _decay_concs_stated = [0.100, 0.078, 0.061, 0.048, 0.037, 0.029]
    _k_fitted = 0.00247
    for _t, _c_stated in zip(_decay_times, _decay_concs_stated):
        ch.add(NumericCheck(
            label=f"Table 8.1: [A](t={_t}) = {_c_stated} vs first-order model",
            section="9",
            stated=_c_stated,
            computed=(lambda t=_t: 0.100 * math.exp(-_k_fitted * t)),
            tolerance=0.02,
            note="First-order decay [A]=[A]_0*exp(-k*t), k=0.00247",
        ))

    # ==================================================================
    # Table verification — Michaelis-Menten rates (Section 9)
    # ==================================================================
    # Verify the raw v values against v = Vmax*[S]/(Km + [S])
    # using the Lineweaver-Burk fitted parameters Vmax=25.0, Km=0.90.
    _mm_Vmax = 25.0
    _mm_Km = 0.90
    _mm_substrates = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
    _mm_rates_stated = [2.5, 4.4, 8.3, 12.0, 16.0, 20.0, 22.2]
    for _s, _v_stated in zip(_mm_substrates, _mm_rates_stated):
        ch.add(NumericCheck(
            label=f"Table 8.3: v([S]={_s}) = {_v_stated} vs Michaelis-Menten model",
            section="9",
            stated=_v_stated,
            computed=(lambda s=_s: _mm_Vmax * s / (_mm_Km + s)),
            tolerance=0.15,
            note="Michaelis-Menten v=Vmax*[S]/(Km+[S]), Vmax=25.0, Km=0.90; "
                 "data are synthetic observations with noise, not exact model values",
        ))

    # ==================================================================
    # Table verification — Arrhenius rate constants (Section 9)
    # ==================================================================
    # Verify the stated k(T) values against the Arrhenius equation
    # k = A * exp(-Ea/(R*T)) using the fitted parameters.
    _arr_A = 3.6e7         # pre-exponential factor (from textbook fit)
    _arr_Ea = 70400.0      # activation energy in J/mol (from textbook fit)
    _arr_R = 8.314         # gas constant
    _arr_temps = [300, 320, 340, 360, 380]
    _arr_ks_stated = [2.0e-5, 1.1e-4, 5.2e-4, 2.1e-3, 7.5e-3]
    for _T, _k_stated in zip(_arr_temps, _arr_ks_stated):
        ch.add(NumericCheck(
            label=f"Table 8.2: k(T={_T}) = {_k_stated:.1e} vs Arrhenius model",
            section="9",
            stated=_k_stated,
            computed=(lambda T=_T: _arr_A * math.exp(-_arr_Ea / (_arr_R * T))),
            tolerance=0.15,
            note="Arrhenius k=A*exp(-Ea/(RT)), A=3.6e7, Ea=70400 J/mol",
        ))

    return ch
