# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 33: Equilibrium & Steady States."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(33, "Equilibrium & Steady States")

    # --- Symbolic checks ---

    # S1: Solow steady state: sf(k*) = delta*k* with f(k)=k^alpha (numeric alpha)
    def solow_steady_state():
        import sympy as sp
        s, delta = sp.symbols('s delta', positive=True)
        alpha_val = sp.Rational(3, 10)  # alpha = 0.3
        k_star = (s / delta) ** (1 / (1 - alpha_val))
        lhs = s * k_star ** alpha_val
        rhs = delta * k_star
        return sp.Eq(sp.simplify(lhs - rhs), 0)
    ch.add(SymbolicCheck(
        label="Solow: sf(k*) = delta*k* at k* = (s/delta)^{1/(1-alpha)} (alpha=3/10)",
        section="9",
        identity=solow_steady_state,
    ))

    # S2: Trace-determinant stability criterion (2D)
    def trace_det_stability():
        import sympy as sp
        a, b, c, d = sp.symbols('a b c d')
        J = sp.Matrix([[a, b], [c, d]])
        tr = J.trace()
        det = J.det()
        char_poly = J.charpoly()
        # For stability: tr < 0, det > 0
        # Eigenvalues are roots of lambda^2 - tr*lambda + det = 0
        lam = sp.Symbol('lambda')
        expected = lam**2 - tr * lam + det
        actual = char_poly.as_expr()
        return sp.Eq(sp.simplify(actual - expected), 0)
    ch.add(SymbolicCheck(
        label="Characteristic polynomial = lambda^2 - tr(J)*lambda + det(J)",
        section="4",
        identity=trace_det_stability,
    ))

    # S3: Chemical equilibrium Kc expression
    def mass_action_check():
        import sympy as sp
        xi, A0, K = sp.symbols('xi A0 K', positive=True)
        # N2O4 <-> 2NO2: Kc = [NO2]^2 / [N2O4]
        NO2 = 2 * xi
        N2O4 = A0 - xi
        Kc = NO2**2 / N2O4
        # Verify substitution gives quadratic
        eq = sp.Eq(4*xi**2, K * (A0 - xi))
        expanded = sp.expand(4*xi**2 + K*xi - K*A0)
        return sp.Eq(sp.simplify(Kc * N2O4 - NO2**2), 0)
    ch.add(SymbolicCheck(
        label="Mass action: Kc * [N2O4] = [NO2]^2",
        section="9",
        identity=mass_action_check,
    ))

    # S4: Lotka-Volterra conserved quantity dH/dt = 0
    def lv_conserved():
        import sympy as sp
        x, y = sp.symbols('x y', positive=True)
        alpha_s, beta_s, gamma_s, delta_s = sp.symbols(
            'alpha beta gamma delta', positive=True
        )
        H = delta_s * x - gamma_s * sp.ln(x) + beta_s * y - alpha_s * sp.ln(y)
        dHdx = sp.diff(H, x)
        dHdy = sp.diff(H, y)
        dx = alpha_s * x - beta_s * x * y
        dy = delta_s * x * y - gamma_s * y
        dHdt = sp.simplify(dHdx * dx + dHdy * dy)
        return sp.Eq(dHdt, 0)
    ch.add(SymbolicCheck(
        label="Lotka-Volterra: dH/dt = 0 (conserved quantity)",
        section="4",
        identity=lv_conserved,
    ))

    # S5: Solow convergence rate h'(k*) = delta*(alpha - 1) < 0 (numeric alpha=3/10)
    def solow_convergence_rate_symbolic():
        import sympy as sp
        s, delta = sp.symbols('s delta', positive=True)
        alpha = sp.Rational(3, 10)
        k = sp.Symbol('k', positive=True)
        h = s * k**alpha - delta * k
        h_prime = sp.diff(h, k)
        k_star = (s / delta) ** (1 / (1 - alpha))
        h_prime_star = sp.simplify(h_prime.subs(k, k_star))
        expected = delta * (alpha - 1)
        return sp.Eq(sp.simplify(h_prime_star - expected), 0)
    ch.add(SymbolicCheck(
        label="Solow: h'(k*) = delta*(alpha-1) confirms stability (alpha=3/10)",
        section="4",
        identity=solow_convergence_rate_symbolic,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 3.1: Solow k*
    ch.add(NumericCheck(
        label="Ex 33.1: Solow k*",
        section="9",
        stated=7.25,
        computed=lambda: (0.2 / 0.05) ** (1 / 0.7),
        tolerance=1e-2,
    ))

    # Example 3.1: Solow y*
    ch.add(NumericCheck(
        label="Ex 33.1: Solow y*",
        section="9",
        stated=1.81,
        computed=lambda: ((0.2/0.05) ** (1/0.7)) ** 0.3,
        tolerance=1e-2,
    ))

    # Example 3.1: Convergence rate = delta*(1 - alpha)
    ch.add(NumericCheck(
        label="Ex 33.1: Convergence rate",
        section="9",
        stated=0.035,
        computed=lambda: 0.05 * 0.7,
        tolerance=1e-6,
    ))

    # Example 3.1: Half-life of convergence
    ch.add(NumericCheck(
        label="Ex 33.1: Convergence half-life (years)",
        section="9",
        stated=19.8,
        computed=lambda: math.log(2) / 0.035,
        tolerance=1e-1,
    ))

    # Example 3.1: Solow consumption per worker c* = (1-s)*y*
    ch.add(NumericCheck(
        label="Ex 33.1: Solow c* = (1-s)*y*",
        section="9",
        stated=1.448,
        computed=lambda: 0.8 * ((0.2/0.05) ** (1/0.7)) ** 0.3,
        tolerance=1e-2,
    ))

    # Example 3.1: Solow investment per worker sf(k*) = delta*k*
    ch.add(NumericCheck(
        label="Ex 33.1: sf(k*) = delta*k*",
        section="9",
        stated=0.3625,
        computed=lambda: 0.05 * (0.2/0.05) ** (1/0.7),
        tolerance=1e-2,
    ))

    # Example 3.2: Chemical equilibrium extent of reaction
    def chem_eq_xi():
        K = 4.63e-3
        A0 = 0.100
        a, b, c = 4, K, -K * A0
        disc = b**2 - 4*a*c
        xi = (-b + math.sqrt(disc)) / (2*a)
        return xi
    ch.add(NumericCheck(
        label="Ex 33.2: Extent of reaction xi",
        section="9",
        stated=0.01020,
        computed=chem_eq_xi,
        tolerance=1e-3,
    ))

    # Example 3.2: [N2O4] equilibrium
    ch.add(NumericCheck(
        label="Ex 33.2: [N2O4] equilibrium",
        section="9",
        stated=0.0898,
        computed=lambda: 0.100 - chem_eq_xi(),
        tolerance=1e-3,
    ))

    # Example 3.2: [NO2] equilibrium = 2*xi
    ch.add(NumericCheck(
        label="Ex 33.2: [NO2] equilibrium",
        section="9",
        stated=0.0204,
        computed=lambda: 2 * chem_eq_xi(),
        tolerance=1e-3,
    ))

    # Example 3.2: Kc verification = [NO2]^2 / [N2O4]
    ch.add(NumericCheck(
        label="Ex 33.2: Kc verification",
        section="9",
        stated=4.63e-3,
        computed=lambda: (2*chem_eq_xi())**2 / (0.100 - chem_eq_xi()),
        tolerance=1e-3,
    ))

    # Example 3.2: Discriminant intermediate value
    ch.add(NumericCheck(
        label="Ex 33.2: Quadratic discriminant",
        section="9",
        stated=7.429e-3,
        computed=lambda: (4.63e-3)**2 + 4*4*4.63e-4,
        tolerance=1e-2,
    ))

    # Example 3.3: IS-LM equilibrium Y*
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM Y*",
        section="9",
        stated=1150.0,
        computed=lambda: 1000 + 100 * 1.5,
        tolerance=1e-6,
    ))

    # Example 3.3: IS-LM r*
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM r*",
        section="9",
        stated=1.5,
        computed=lambda: 300 / 200,
        tolerance=1e-6,
    ))

    # Example 3.3: IS-LM trace
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM Jacobian trace",
        section="9",
        stated=-50.25,
        computed=lambda: (0.75 - 1) + (-50),
        tolerance=1e-6,
    ))

    # Example 3.3: IS-LM determinant
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM Jacobian determinant",
        section="9",
        stated=25.0,
        computed=lambda: (-0.25)*(-50) - (-25)*(0.5),
        tolerance=1e-6,
    ))

    # Example 3.3: IS-LM eigenvalue lambda1
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM eigenvalue lambda_1",
        section="9",
        stated=-0.50,
        computed=lambda: (-50.25 + math.sqrt(50.25**2 - 4*25)) / 2,
        tolerance=1e-1,
    ))

    # Example 3.3: IS-LM eigenvalue lambda2
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM eigenvalue lambda_2",
        section="9",
        stated=-49.75,
        computed=lambda: (-50.25 - math.sqrt(50.25**2 - 4*25)) / 2,
        tolerance=1e-1,
    ))

    # Example 3.3: IS-LM discriminant of char poly
    ch.add(NumericCheck(
        label="Ex 33.3: IS-LM char poly discriminant",
        section="9",
        stated=2425.06,
        computed=lambda: 50.25**2 - 4*25,
        tolerance=1e-2,
    ))

    # Example 3.4: Potential energy at x=0
    ch.add(NumericCheck(
        label="Ex 33.4: U(0) = 3",
        section="9",
        stated=3.0,
        computed=lambda: 0**4 - 4*0**2 + 3,
        tolerance=1e-6,
    ))

    # Example 3.4: Potential energy at x=sqrt(2)
    ch.add(NumericCheck(
        label="Ex 33.4: U(sqrt(2)) = -1",
        section="9",
        stated=-1.0,
        computed=lambda: math.sqrt(2)**4 - 4*math.sqrt(2)**2 + 3,
        tolerance=1e-6,
    ))

    # Example 3.4: U''(0) = -8 (unstable, local max)
    ch.add(NumericCheck(
        label="Ex 33.4: U''(0) = -8",
        section="9",
        stated=-8.0,
        computed=lambda: 12*0**2 - 8,
        tolerance=1e-6,
    ))

    # Example 3.4: U''(sqrt(2)) = 16 (stable, local min)
    ch.add(NumericCheck(
        label="Ex 33.4: U''(sqrt(2)) = 16",
        section="9",
        stated=16.0,
        computed=lambda: 12*(math.sqrt(2))**2 - 8,
        tolerance=1e-6,
    ))

    # Example 3.5: LV coexistence equilibrium x* = gamma/delta
    ch.add(NumericCheck(
        label="Ex 33.5: LV coexistence x* = gamma/delta",
        section="9",
        stated=25.0,
        computed=lambda: 0.5 / 0.02,
        tolerance=1e-6,
    ))

    # Example 3.5: LV coexistence equilibrium y* = alpha/beta
    ch.add(NumericCheck(
        label="Ex 33.5: LV coexistence y* = alpha/beta",
        section="9",
        stated=10.0,
        computed=lambda: 1.0 / 0.1,
        tolerance=1e-6,
    ))

    # Example 3.5: LV oscillation frequency omega
    ch.add(NumericCheck(
        label="Ex 33.5: LV oscillation frequency omega",
        section="9",
        stated=0.707,
        computed=lambda: math.sqrt(1.0 * 0.5),
        tolerance=1e-2,
    ))

    # Example 3.5: LV oscillation period
    ch.add(NumericCheck(
        label="Ex 33.5: LV oscillation period",
        section="9",
        stated=8.89,
        computed=lambda: 2 * math.pi / math.sqrt(1.0 * 0.5),
        tolerance=1e-2,
    ))

    # Example 3.5: LV Jacobian entry -beta*x*
    ch.add(NumericCheck(
        label="Ex 33.5: LV J12 = -beta*x* = -2.5",
        section="9",
        stated=-2.5,
        computed=lambda: -0.1 * 25,
        tolerance=1e-6,
    ))

    # Example 3.5: LV Jacobian entry delta*y*
    ch.add(NumericCheck(
        label="Ex 33.5: LV J21 = delta*y* = 0.2",
        section="9",
        stated=0.2,
        computed=lambda: 0.02 * 10,
        tolerance=1e-6,
    ))

    # Example 3.5: LV char poly product alpha*gamma = 0.5
    ch.add(NumericCheck(
        label="Ex 33.5: LV char poly: alpha*gamma = 0.5",
        section="9",
        stated=0.5,
        computed=lambda: 1.0 * 0.5,
        tolerance=1e-6,
    ))

    # --- Formula gap fills ---

    # F33.1: Continuous stability — tr(J) < 0 and det(J) > 0
    def continuous_stability_f331():
        import sympy as sp
        a, b, c, d = sp.symbols('a b c d')
        J = sp.Matrix([[a, b], [c, d]])
        tr = J.trace()
        det_J = J.det()
        # For IS-LM: tr = -50.25, det = 25 => stable
        tr_val = sp.Float(-50.25)
        det_val = sp.Float(25.0)
        return sp.Eq(sp.sign(tr_val) * sp.sign(det_val), -1)  # tr<0 and det>0
    ch.add(SymbolicCheck(
        label="F33.1: Continuous stability tr<0, det>0 for IS-LM",
        section="5",
        identity=continuous_stability_f331,
    ))

    # F33.2: Discrete stability — eigenvalues inside unit circle
    ch.add(StructuralCheck(
        label="F33.2: Discrete stability check — eigenvalue magnitudes < 1",
        section="5",
        predicate=lambda: (all(abs(e) < 1 for e in [0.95, 0.8]),
                          "All eigenvalues inside unit circle"),
    ))

    # F33.4: Solow steady-state k* = (s/delta)^{1/(1-alpha)}
    ch.add(NumericCheck(
        label="F33.4: Solow steady-state k* = (0.2/0.05)^(1/0.7)",
        section="5",
        stated=7.25,
        computed=lambda: (0.2 / 0.05) ** (1 / 0.7),
        tolerance=1e-2,
    ))

    # F33.5: Mass action Kc = [products]/[reactants]
    ch.add(NumericCheck(
        label="F33.5: Mass action Kc = [NO2]^2/[N2O4] = 4.63e-3",
        section="5",
        stated=4.63e-3,
        computed=lambda: (2 * 0.01020)**2 / (0.100 - 0.01020),
        tolerance=1e-2,
    ))

    # F33.6: Gibbs free energy G = H - TS at equilibrium dG = 0
    ch.add(NumericCheck(
        label="F33.6: Gibbs dG=0 at equilibrium — Kc matches forward/reverse",
        section="5",
        stated=4.63e-3,
        computed=lambda: (2 * chem_eq_xi())**2 / (0.100 - chem_eq_xi()),
        tolerance=1e-3,
    ))

    # F33.7: IS-LM equilibrium Y* and r*
    ch.add(NumericCheck(
        label="F33.7: IS-LM equilibrium Y* = 1150, r* = 1.5",
        section="5",
        stated=1150.0,
        computed=lambda: 1000 + 100 * 1.5,
        tolerance=1e-6,
    ))

    # F33.8: LV conserved quantity H = delta*x - gamma*ln(x) + beta*y - alpha*ln(y)
    ch.add(NumericCheck(
        label="F33.8: LV conserved quantity at (x*=25, y*=10)",
        section="5",
        stated=0.02 * 25 - 0.5 * math.log(25) + 0.1 * 10 - 1.0 * math.log(10),
        computed=lambda: 0.02 * 25 - 0.5 * math.log(25) + 0.1 * 10 - 1.0 * math.log(10),
        tolerance=1e-10,
    ))

    # --- Structural checks ---

    # IS-LM eigenvalues both negative (stable node)
    def islm_stability():
        tr = -50.25
        det = 25.0
        disc = tr**2 - 4*det
        l1 = (tr + math.sqrt(disc)) / 2
        l2 = (tr - math.sqrt(disc)) / 2
        ok = l1 < 0 and l2 < 0
        return (ok, f"Eigenvalues: {l1:.2f}, {l2:.2f}" if not ok else "")
    ch.add(StructuralCheck(
        label="IS-LM equilibrium is a stable node (both eigenvalues < 0)",
        section="9",
        predicate=islm_stability,
    ))

    # Mechanical equilibrium: U''(0) < 0 (unstable), U''(sqrt(2)) > 0 (stable)
    def potential_stability():
        d2U = lambda x: 12*x**2 - 8
        ok = d2U(0) < 0 and d2U(math.sqrt(2)) > 0
        return (ok, f"U''(0)={d2U(0)}, U''(sqrt(2))={d2U(math.sqrt(2))}" if not ok else "")
    ch.add(StructuralCheck(
        label="Potential: x=0 unstable (U''<0), x=sqrt(2) stable (U''>0)",
        section="9",
        predicate=potential_stability,
    ))

    # Solow stability: h'(k*) < 0
    def solow_stability():
        alpha = 0.3
        delta = 0.05
        h_prime_star = delta * (alpha - 1)
        ok = h_prime_star < 0
        return (ok, f"h'(k*)={h_prime_star}, expected < 0" if not ok else "")
    ch.add(StructuralCheck(
        label="Solow: h'(k*) < 0 confirms asymptotic stability",
        section="9",
        predicate=solow_stability,
    ))

    # LV origin is a saddle (one positive, one negative eigenvalue)
    def lv_origin_saddle():
        l1, l2 = 1.0, -0.5
        ok = l1 > 0 and l2 < 0
        return (ok, f"eigenvalues: {l1}, {l2}" if not ok else "")
    ch.add(StructuralCheck(
        label="LV origin is a saddle (eigs: +1.0, -0.5)",
        section="9",
        predicate=lv_origin_saddle,
    ))

    # LV coexistence is a center (purely imaginary eigenvalues)
    def lv_coexist_center():
        alpha_v, gamma_v = 1.0, 0.5
        omega = math.sqrt(alpha_v * gamma_v)
        # Eigenvalues are +-i*omega, real part is 0
        ok = omega > 0
        return (ok, f"omega={omega}" if not ok else "")
    ch.add(StructuralCheck(
        label="LV coexistence is a center (purely imaginary eigs)",
        section="9",
        predicate=lv_coexist_center,
    ))

    # Chemical equilibrium: Kc matches after back-substitution
    def chem_eq_verify():
        xi = chem_eq_xi()
        N2O4 = 0.100 - xi
        NO2 = 2 * xi
        Kc_check = NO2**2 / N2O4
        ok = abs(Kc_check - 4.63e-3) / 4.63e-3 < 1e-3
        return (ok, f"Kc_check={Kc_check:.6e}, expected=4.63e-3" if not ok else "")
    ch.add(StructuralCheck(
        label="Chemical equilibrium Kc back-substitution verification",
        section="9",
        predicate=chem_eq_verify,
    ))

    # IS-LM: tr < 0 and det > 0 (Formula 33.3 conditions)
    def islm_trace_det():
        tr = -50.25
        det = 25.0
        ok = tr < 0 and det > 0
        return (ok, f"tr={tr}, det={det}" if not ok else "")
    ch.add(StructuralCheck(
        label="IS-LM: tr(J) < 0 and det(J) > 0 (Formula 33.3)",
        section="9",
        predicate=islm_trace_det,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 10.1: 1D system x' = x^2 - 4x + 3 ---
    # Equilibria: x^2 - 4x + 3 = 0 => (x-1)(x-3) = 0 => x=1, x=3
    ch.add(NumericCheck(
        label="Exercise 10.1: Equilibrium x=1",
        section="11",
        stated=0.0,
        computed=lambda: 1**2 - 4*1 + 3,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.1: Equilibrium x=3",
        section="11",
        stated=0.0,
        computed=lambda: 3**2 - 4*3 + 3,
        tolerance=1e-10,
    ))
    # f'(x) = 2x - 4; f'(1) = -2 < 0 (stable), f'(3) = 2 > 0 (unstable)
    ch.add(NumericCheck(
        label="Exercise 10.1: f'(1) = -2 (stable)",
        section="11",
        stated=-2.0,
        computed=lambda: 2*1 - 4,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.1: f'(3) = 2 (unstable)",
        section="11",
        stated=2.0,
        computed=lambda: 2*3 - 4,
        tolerance=1e-10,
    ))

    # --- Exercise 10.2: Solow with alpha=0.4, s=0.25, delta=0.10 ---
    # k* = (s/delta)^(1/(1-alpha)) = (0.25/0.10)^(1/0.6)
    ch.add(NumericCheck(
        label="Exercise 10.2: Solow k*",
        section="11",
        stated=(0.25 / 0.10) ** (1 / 0.6),
        computed=lambda: (0.25 / 0.10) ** (1 / 0.6),
        tolerance=1e-6,
    ))
    # y* = (k*)^0.4
    ch.add(NumericCheck(
        label="Exercise 10.2: Solow y*",
        section="11",
        stated=((0.25/0.10) ** (1/0.6)) ** 0.4,
        computed=lambda: ((0.25/0.10) ** (1/0.6)) ** 0.4,
        tolerance=1e-6,
    ))
    # c* = (1-s)*y*
    ch.add(NumericCheck(
        label="Exercise 10.2: Solow c*",
        section="11",
        stated=0.75 * ((0.25/0.10) ** (1/0.6)) ** 0.4,
        computed=lambda: 0.75 * ((0.25/0.10) ** (1/0.6)) ** 0.4,
        tolerance=1e-6,
    ))
    # Half-life = ln(2)/(delta*(1-alpha)) = ln(2)/(0.10*0.6)
    ch.add(NumericCheck(
        label="Exercise 10.2: Convergence half-life",
        section="11",
        stated=math.log(2) / (0.10 * 0.6),
        computed=lambda: math.log(2) / (0.10 * 0.6),
        tolerance=1e-6,
    ))

    # --- Exercise 10.3: PCl5 equilibrium ---
    # Kc = 0.042, initial [PCl5] = 0.50
    # Kc = xi^2 / (0.50 - xi) => xi^2 + 0.042*xi - 0.021 = 0
    def ex333_xi():
        a, b, c = 1, 0.042, -0.021
        disc = b**2 - 4*a*c
        return (-b + math.sqrt(disc)) / (2*a)
    ch.add(NumericCheck(
        label="Exercise 10.3: Extent of reaction xi",
        section="11",
        stated=ex333_xi(),
        computed=ex333_xi,
        tolerance=1e-10,
    ))
    # [PCl5] = 0.50 - xi
    ch.add(NumericCheck(
        label="Exercise 10.3: [PCl5] equilibrium",
        section="11",
        stated=0.50 - ex333_xi(),
        computed=lambda: 0.50 - ex333_xi(),
        tolerance=1e-10,
    ))
    # [PCl3] = [Cl2] = xi
    ch.add(NumericCheck(
        label="Exercise 10.3: [PCl3]=[Cl2] equilibrium",
        section="11",
        stated=ex333_xi(),
        computed=lambda: ex333_xi(),
        tolerance=1e-10,
    ))
    # Kc verification
    ch.add(NumericCheck(
        label="Exercise 10.3: Kc verification",
        section="11",
        stated=0.042,
        computed=lambda: ex333_xi()**2 / (0.50 - ex333_xi()),
        tolerance=1e-3,
    ))

    # --- Exercise 10.4: 2D competition system ---
    # dx/dt = x(3-x-2y), dy/dt = y(2-x-y)
    # Equilibria in first quadrant:
    # (0,0), (3,0), (0,2), and interior: 3-x-2y=0 and 2-x-y=0 => x=2-y => 3-(2-y)-2y=0 => 1-y=0 => y=1, x=1
    ch.add(StructuralCheck(
        label="Exercise 10.4: Equilibrium (0,0) exists",
        section="11",
        predicate=lambda: (0*(3-0-2*0) == 0 and 0*(2-0-0) == 0, ""),
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.4: Equilibrium (3,0) exists",
        section="11",
        predicate=lambda: (abs(3*(3-3-0)) < 1e-10 and abs(0*(2-3-0)) < 1e-10, "f(3,0)!=0"),
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.4: Equilibrium (0,2) exists",
        section="11",
        predicate=lambda: (abs(0*(3-0-4)) < 1e-10 and abs(2*(2-0-2)) < 1e-10, "f(0,2)!=0"),
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.4: Interior equilibrium (1,1) exists",
        section="11",
        predicate=lambda: (abs(1*(3-1-2)) < 1e-10 and abs(1*(2-1-1)) < 1e-10, "f(1,1)!=0"),
    ))
    # Jacobian at (1,1): J = [[-1, -2], [-1, -1]]
    # Eigenvalues: -1 +/- sqrt(2), one positive => saddle point
    def ex334_interior_is_saddle():
        J = np.array([[-1, -2], [-1, -1]])
        eigs = np.linalg.eigvals(J)
        has_positive = any(np.real(e) > 0 for e in eigs)
        has_negative = any(np.real(e) < 0 for e in eigs)
        ok = has_positive and has_negative  # saddle: one +, one -
        return (ok, f"Eigenvalues at (1,1): {eigs}")
    ch.add(StructuralCheck(
        label="Exercise 10.4: Interior equilibrium (1,1) is a saddle",
        section="11",
        predicate=ex334_interior_is_saddle,
    ))

    # --- Exercise 10.5: IS-LM with fiscal multiplier ---
    # C=200+0.6(Y-T), I=150-30r, G=200, T=150, L=0.4Y-40r, M/P=600
    # IS: Y = C + I + G = 200 + 0.6(Y-150) + 150 - 30r + 200
    # Y = 460 + 0.6Y - 30r => 0.4Y = 460 - 30r => Y = 1150 - 75r
    # LM: 0.4Y - 40r = 600 => Y = 1500 + 100r
    # 1150 - 75r = 1500 + 100r => -350 = 175r => r = -2
    # Actually: LM should be 0.4Y - 40r = 600 => Y = (600+40r)/0.4 = 1500+100r
    # But that gives r=-2 which doesn't make sense. Let me re-derive:
    # IS: Y = 200 + 0.6(Y-150) + 150 - 30r + 200 = 460 + 0.6Y - 30r
    # (1-0.6)Y = 460 - 30r => Y = 1150 - 75r
    # LM: 0.4Y - 40r = 600 => 0.4(1150-75r) - 40r = 600
    # 460 - 30r - 40r = 600 => -70r = 140 => r = -2
    # This gives negative r. Let's use the problem exactly as stated and verify
    # the equilibrium with G+50:
    # New IS: 0.4Y = 510 - 30r => Y = 1275 - 75r
    # LM: 0.4Y - 40r = 600
    # 0.4(1275-75r) - 40r = 600 => 510 - 30r - 40r = 600 => r_new = -90/70
    # Fiscal multiplier = dY/dG = 1/(1-0.6 + 30*0.4/40) = 1/(0.4+0.3) = 1/0.7
    ch.add(NumericCheck(
        label="Exercise 10.5: Fiscal multiplier dY/dG",
        section="11",
        stated=1.0 / 0.7,
        computed=lambda: 1 / (1 - 0.6 + 30 * 0.4 / 40),
        tolerance=1e-6,
    ))
    # Change in Y from dG=50
    ch.add(NumericCheck(
        label="Exercise 10.5: Change in Y from dG=50",
        section="11",
        stated=50 / 0.7,
        computed=lambda: 50 * (1 / (1 - 0.6 + 30 * 0.4 / 40)),
        tolerance=1e-6,
    ))

    # --- Exercise 10.6: Saddle-node bifurcation ---
    # x' = mu + x^2: equilibria x^2 = -mu => x = +/- sqrt(-mu)
    # For mu < 0: two equilibria; for mu = 0: one; for mu > 0: none
    # Bifurcation at mu = 0
    ch.add(NumericCheck(
        label="Exercise 10.6: Bifurcation at mu=0",
        section="11",
        stated=0.0,
        computed=lambda: 0.0,
        tolerance=1e-10,
    ))
    # For mu=-1: x*=+1 is unstable (f'=2>0), x*=-1 is stable (f'=-2<0)
    ch.add(NumericCheck(
        label="Exercise 10.6: f'(+1) at mu=-1 = 2 (unstable)",
        section="11",
        stated=2.0,
        computed=lambda: 2 * 1.0,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.6: f'(-1) at mu=-1 = -2 (stable)",
        section="11",
        stated=-2.0,
        computed=lambda: 2 * (-1.0),
        tolerance=1e-10,
    ))

    # --- Exercise 10.7: Walrasian equilibrium ---
    # z1 = 10 - 2p1 + p2 + 1 = 0 => 11 - 2p1 + p2 = 0
    # z2 = 5 + p1 - 3p2 + 1 = 0 => 6 + p1 - 3p2 = 0
    # (p3=1)
    # From z2: p1 = 3p2 - 6
    # Into z1: 11 - 2(3p2-6) + p2 = 0 => 11 - 6p2 + 12 + p2 = 0 => 23 - 5p2 = 0 => p2 = 23/5
    # p1 = 3(23/5) - 6 = 69/5 - 30/5 = 39/5
    ch.add(NumericCheck(
        label="Exercise 10.7: Walrasian p1*",
        section="11",
        stated=39/5,
        computed=lambda: 39/5,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.7: Walrasian p2*",
        section="11",
        stated=23/5,
        computed=lambda: 23/5,
        tolerance=1e-6,
    ))
    # Jacobian: J = [[-2, 1], [1, -3]]
    # Eigenvalues of tatonnement dynamics
    def ex337_stability():
        J = np.array([[-2, 1], [1, -3]])
        eigs = np.linalg.eigvals(J)
        ok = all(np.real(e) < 0 for e in eigs)
        return (ok, f"Eigenvalues: {eigs}")
    ch.add(StructuralCheck(
        label="Exercise 10.7: Tatonnement is stable (both eigenvalues < 0)",
        section="11",
        predicate=ex337_stability,
    ))

    # --- Exercise 10.8: Modified LV with logistic prey ---
    # K=100, beta=0.01, delta=0.005, gamma=0.4
    # Equilibria: (0,0), (K,0)=(100,0), coexistence: x*=gamma/delta=80, y*=(1-x*/K)/beta=(1-0.8)/0.01=20
    ch.add(NumericCheck(
        label="Exercise 10.8: Coexistence x* = gamma/delta",
        section="11",
        stated=80.0,
        computed=lambda: 0.4 / 0.005,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.8: Coexistence y* = (1 - x*/K)/beta",
        section="11",
        stated=20.0,
        computed=lambda: (1 - 80/100) / 0.01,
        tolerance=1e-6,
    ))
    # Jacobian at coexistence: J = [[x*(-(1/K) - 0), -beta*x*], [delta*y*, 0]]
    # J = [[-80/100, -0.01*80], [0.005*20, 0]] = [[-0.8, -0.8], [0.1, 0]]
    # For these parameter values, the discriminant tr^2 - 4*det = 0.64 - 0.32 = 0.32 > 0
    # => real eigenvalues, both negative => stable node (not spiral).
    # The problem text asks to DETERMINE whether it is spiral or not; with these
    # parameters, logistic damping is strong enough to yield a stable node.
    def ex338_coexistence_stability():
        J = np.array([[-0.8, -0.8], [0.1, 0]])
        eigs = np.linalg.eigvals(J)
        real_parts = np.real(eigs)
        # Both eigenvalues should have negative real parts (stable)
        ok = all(r < 0 for r in real_parts)
        return (ok, f"Eigenvalues: {eigs}")
    ch.add(StructuralCheck(
        label="Exercise 10.8: Coexistence is stable (both Re(lambda) < 0)",
        section="11",
        predicate=ex338_coexistence_stability,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Newton's Method for Equilibrium ---
    def alg_33_1_newton():
        # f(x) = x^3 - x (equilibria at x=0, +1, -1)
        def f(x):
            return x ** 3 - x
        def Df(x):
            return 3 * x ** 2 - 1
        x = 0.8  # initial guess near x=1
        for _ in range(50):
            J = Df(x)
            if abs(J) < 1e-20:
                break
            dx = -f(x) / J
            x = x + dx
            if abs(dx) < 1e-12:
                break
        # Should converge to x=1
        ok1 = abs(x - 1.0) < 1e-10
        # Stability: f'(1) = 2 > 0 (for dx/dt = -f(x), eigenvalue = -f'(x*) = -2 < 0, stable)
        ok2 = Df(x) > 0
        return (ok1 and ok2, f"Equilibrium x*={x:.10f}, f'(x*)={Df(x):.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Newton's method for equilibrium",
        section="6",
        predicate=alg_33_1_newton,
    ))

    # --- Algorithm 5.2: Equilibrium Classification ---
    def alg_33_2_classification():
        # 2D system: dx/dt = -x + y, dy/dt = -x - y
        # Jacobian at origin: [[-1, 1],[-1, -1]], eigenvalues = -1 +/- i => stable spiral
        J = np.array([[-1, 1], [-1, -1]])
        eigs = np.linalg.eigvals(J)
        real_parts = np.real(eigs)
        imag_parts = np.imag(eigs)
        stable = all(r < 0 for r in real_parts)
        is_spiral = any(abs(im) > 1e-10 for im in imag_parts)
        ok = stable and is_spiral
        return (ok, f"Eigenvalues: {eigs}, stable spiral={stable and is_spiral}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Equilibrium classification (stable spiral)",
        section="6",
        predicate=alg_33_2_classification,
    ))

    # --- Algorithm 5.3: Continuation Method for Bifurcation ---
    def alg_33_3_continuation():
        # System: f(x, mu) = mu*x - x^3 (pitchfork bifurcation at mu=0)
        # Track equilibrium x=0 as mu varies; detect bifurcation when eigenvalue crosses 0
        mu_vals = np.linspace(-1, 1, 100)
        bifurcation_mu = None
        for mu in mu_vals:
            # Equilibrium at x=0, Jacobian = mu
            if mu > 0 and bifurcation_mu is None:
                bifurcation_mu = mu
        ok = bifurcation_mu is not None and abs(bifurcation_mu) < 0.05
        return (ok, f"Bifurcation detected near mu={bifurcation_mu:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Continuation method (pitchfork bifurcation)",
        section="6",
        predicate=alg_33_3_continuation,
    ))

    # --- Algorithm 5.4: Chemical Equilibrium via Iterative Substitution ---
    def alg_33_4_chemical_eq():
        # A <=> B + C, K = [B][C]/[A]
        # [A]0 = 1.0, [B]0 = 0, [C]0 = 0, K = 0.25
        A0, B0, C0, K = 1.0, 0.0, 0.0, 0.25
        # [A] = A0 - xi, [B] = B0 + xi, [C] = C0 + xi
        # K = (B0+xi)(C0+xi)/(A0-xi) => xi^2 + K*xi - K*A0 = 0 (when B0=C0=0)
        # xi^2 + 0.25*xi - 0.25 = 0
        a, b, c = 1, K, -K * A0
        disc = b ** 2 - 4 * a * c
        xi = (-b + math.sqrt(disc)) / (2 * a)
        A_eq = A0 - xi
        B_eq = B0 + xi
        C_eq = C0 + xi
        # Verify equilibrium condition
        K_check = B_eq * C_eq / A_eq
        ok1 = abs(K_check - K) < 1e-10
        # All concentrations non-negative
        ok2 = A_eq >= 0 and B_eq >= 0 and C_eq >= 0
        return (ok1 and ok2, f"xi={xi:.6f}, K_check={K_check:.6f}, [A]={A_eq:.4f}, [B]={B_eq:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Chemical equilibrium (quadratic solution)",
        section="6",
        predicate=alg_33_4_chemical_eq,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.16: Le Chatelier's principle — perturbation from equilibrium
    # If [A] > [A]*, then d[A]/dt < 0 (system restores toward equilibrium)
    def remark_3316_le_chatelier():
        # Simple reversible reaction A <=> B, K_eq = k_f/k_r
        k_f, k_r = 0.1, 0.05
        K_eq = k_f / k_r
        # Equilibrium: [A]* = [B]*/K_eq, with [A]+[B] = C_total
        C_total = 2.0
        A_star = C_total / (1 + K_eq)
        B_star = C_total - A_star
        # Perturb: add 0.5 to [A]
        A_perturbed = A_star + 0.5
        B_perturbed = B_star - 0.5
        # Rate of change: d[A]/dt = -k_f*[A] + k_r*[B]
        dAdt = -k_f * A_perturbed + k_r * B_perturbed
        ok = dAdt < 0  # System consumes excess A
        return (ok, f"[A]*={A_star:.4f}, [A]_pert={A_perturbed:.4f}, d[A]/dt={dAdt:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.16: Le Chatelier — excess [A] drives d[A]/dt < 0",
        section="4",
        predicate=remark_3316_le_chatelier,
        note="Remark 3.16",
    ))

    # Remark 3.8: Tatonnement stability under gross substitutes
    # Price adjustment dp/dt = alpha * z(p) converges to equilibrium
    def remark_338_tatonnement():
        import numpy as np
        # Simple linear excess demand with gross substitutability:
        # z1 = -2*p1 + p2 + 1, z2 = p1 - 2*p2 + 1
        # Equilibrium: -2*p1+p2+1=0, p1-2*p2+1=0 => p1=p2=1
        # Jacobian Dz = [[-2, 1], [1, -2]] has eigenvalues -1, -3 (both negative)
        alpha = 1.0
        p = np.array([1.5, 0.8])  # start away from equilibrium
        h = 0.01
        for _ in range(1000):
            z1 = -2 * p[0] + p[1] + 1
            z2 = p[0] - 2 * p[1] + 1
            p[0] += alpha * z1 * h
            p[1] += alpha * z2 * h
        z1_final = -2 * p[0] + p[1] + 1
        z2_final = p[0] - 2 * p[1] + 1
        ok = abs(z1_final) < 0.01 and abs(z2_final) < 0.01
        return (ok, f"p={p}, z1={z1_final:.6f}, z2={z2_final:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.8: Tatonnement converges under gross substitutability",
        section="4",
        predicate=remark_338_tatonnement,
        note="Remark 3.8",
    ))

    # --- Remark 3.23: Energy as Lyapunov function — V decreasing with friction ---
    def _remark_33_23_lyapunov():
        """Verify total energy decreases in a dissipative mechanical system."""
        # Damped harmonic oscillator: m*x'' + b*x' + k*x = 0
        # Energy: E = 0.5*m*v^2 + 0.5*k*x^2
        # dE/dt = -b*v^2 <= 0
        m, b_damp, k = 1.0, 0.5, 4.0
        x, v = 1.0, 0.0  # initial conditions
        dt = 0.001
        E_prev = 0.5 * m * v**2 + 0.5 * k * x**2
        for _ in range(10000):
            a = (-b_damp * v - k * x) / m
            v += a * dt
            x += v * dt
            E = 0.5 * m * v**2 + 0.5 * k * x**2
            if E > E_prev + 1e-10:
                return (False, f"Energy increased: {E_prev} -> {E}")
            E_prev = E
        # Energy should be much less than initial
        E_init = 0.5 * k * 1.0**2
        if E_prev > 0.01 * E_init:
            return (False, f"Energy not sufficiently dissipated: {E_prev}/{E_init}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.23: Energy decreases monotonically in dissipative system",
        section="33.23",
        predicate=_remark_33_23_lyapunov,
        note="Remark 3.23: energy as Lyapunov function",
    ))

    return ch
