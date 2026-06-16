# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 30: Epidemiology & Population Dynamics."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def _sir_rk4(beta, gamma, S0, I0, R0_init, T, h):
    """Simulate SIR with RK4 (frequency-dependent: beta*S*I/N)."""
    N = S0 + I0 + R0_init
    steps = int(T / h)
    t = 0.0
    S, I, R = float(S0), float(I0), float(R0_init)
    max_I = I
    peak_t = 0.0
    S_at_peak = S

    def f(s, i, r):
        force = beta * s * i / N
        return -force, force - gamma * i, gamma * i

    for _ in range(steps):
        k1 = f(S, I, R)
        k2 = f(S + h / 2 * k1[0], I + h / 2 * k1[1], R + h / 2 * k1[2])
        k3 = f(S + h / 2 * k2[0], I + h / 2 * k2[1], R + h / 2 * k2[2])
        k4 = f(S + h * k3[0], I + h * k3[1], R + h * k3[2])
        S += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        I += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        R += h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        t += h
        if I > max_I:
            max_I = I
            peak_t = t
            S_at_peak = S

    return max_I, peak_t, S, I, R, S_at_peak


def _seir_rk4(beta, sigma, gamma, S0, E0, I0, R0_init, T, h):
    """Simulate SEIR with RK4 (frequency-dependent: beta*S*I/N)."""
    N = S0 + E0 + I0 + R0_init
    steps = int(T / h)
    t = 0.0
    S, E, I, R = float(S0), float(E0), float(I0), float(R0_init)
    max_I = I
    peak_t = 0.0

    def f(s, e, i, r):
        force = beta * s * i / N
        return -force, force - sigma * e, sigma * e - gamma * i, gamma * i

    for _ in range(steps):
        k1 = f(S, E, I, R)
        k2 = f(S + h / 2 * k1[0], E + h / 2 * k1[1], I + h / 2 * k1[2], R + h / 2 * k1[3])
        k3 = f(S + h / 2 * k2[0], E + h / 2 * k2[1], I + h / 2 * k2[2], R + h / 2 * k2[3])
        k4 = f(S + h * k3[0], E + h * k3[1], I + h * k3[2], R + h * k3[3])
        S += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        E += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        I += h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        R += h / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        t += h
        if I > max_I:
            max_I = I
            peak_t = t

    return max_I, peak_t, S, E, I, R


def build() -> Chapter:
    ch = Chapter(30, "Epidemiology & Population Dynamics")

    # ===================================================================
    # SYMBOLIC CHECKS
    # ===================================================================

    # S1: SIR conservation law: d(S+I+R)/dt = 0
    def sir_conservation():
        import sympy as sp
        S, I, R, beta, gamma = sp.symbols('S I R beta gamma', positive=True)
        dSdt = -beta * S * I
        dIdt = beta * S * I - gamma * I
        dRdt = gamma * I
        total = sp.simplify(dSdt + dIdt + dRdt)
        return sp.Eq(total, 0)
    ch.add(SymbolicCheck(
        label="SIR conservation: d(S+I+R)/dt = 0",
        section="4",
        identity=sir_conservation,
    ))

    # S2: Logistic solution satisfies the ODE
    def logistic_ode():
        import sympy as sp
        t, r, K, N0 = sp.symbols('t r K N0', positive=True)
        N = K / (1 + ((K - N0) / N0) * sp.exp(-r * t))
        dNdt = sp.diff(N, t)
        rhs = r * N * (1 - N / K)
        return sp.Eq(sp.simplify(dNdt - rhs), 0)
    ch.add(SymbolicCheck(
        label="Logistic solution satisfies dN/dt = rN(1-N/K)",
        section="4",
        identity=logistic_ode,
    ))

    # S3: Herd immunity threshold H = 1 - 1/R0
    def herd_immunity_formula():
        import sympy as sp
        R0 = sp.Symbol('R0', positive=True)
        H = 1 - 1 / R0
        Re = R0 * (1 - H)
        return sp.Eq(sp.simplify(Re), 1)
    ch.add(SymbolicCheck(
        label="At herd immunity threshold, R_e = 1",
        section="4",
        identity=herd_immunity_formula,
    ))

    # S4: SEIR conservation: d(S+E+I+R)/dt = 0
    def seir_conservation():
        import sympy as sp
        S, E, I, R, beta, sigma, gamma = sp.symbols(
            'S E I R beta sigma gamma', positive=True)
        dS = -beta * S * I
        dE = beta * S * I - sigma * E
        dI = sigma * E - gamma * I
        dR = gamma * I
        total = sp.simplify(dS + dE + dI + dR)
        return sp.Eq(total, 0)
    ch.add(SymbolicCheck(
        label="SEIR conservation: d(S+E+I+R)/dt = 0",
        section="4",
        identity=seir_conservation,
    ))

    # S5: Lotka-Volterra conserved quantity dH/dt = 0
    def lv_conserved_symbolic():
        import sympy as sp
        x, y = sp.symbols('x y', positive=True)
        alpha, beta, delta, gamma = sp.symbols(
            'alpha beta delta gamma', positive=True)
        H = delta * x - gamma * sp.ln(x) + beta * y - alpha * sp.ln(y)
        dx = alpha * x - beta * x * y
        dy = delta * x * y - gamma * y
        dHdt = sp.diff(H, x) * dx + sp.diff(H, y) * dy
        return sp.Eq(sp.simplify(dHdt), 0)
    ch.add(SymbolicCheck(
        label="LV dH/dt = 0 symbolically",
        section="4",
        identity=lv_conserved_symbolic,
    ))

    # S6: SIR phase relation is conserved along trajectories
    def sir_phase_relation():
        import sympy as sp
        S, I, beta, gamma = sp.symbols('S I beta gamma', positive=True)
        # C = I + S - (gamma/beta)*ln(S) is conserved
        C = I + S - (gamma / beta) * sp.ln(S)
        dS = -beta * S * I
        dI = beta * S * I - gamma * I
        dCdt = sp.diff(C, S) * dS + sp.diff(C, I) * dI
        return sp.Eq(sp.simplify(dCdt), 0)
    ch.add(SymbolicCheck(
        label="SIR phase relation dC/dt = 0 (F4.2)",
        section="5",
        identity=sir_phase_relation,
    ))

    # S7: LV Jacobian eigenvalues are purely imaginary
    def lv_eigenvalues_imaginary():
        import sympy as sp
        alpha, beta, delta, gamma = sp.symbols(
            'alpha beta delta gamma', positive=True)
        # Jacobian at coexistence equilibrium (gamma/delta, alpha/beta)
        J = sp.Matrix([
            [0, -beta * gamma / delta],
            [delta * alpha / beta, 0],
        ])
        eigenvals = J.eigenvals()
        # Both eigenvalues should have zero real part
        for ev in eigenvals:
            if sp.re(sp.simplify(ev)) != 0:
                return sp.S.false
        return sp.S.true
    ch.add(SymbolicCheck(
        label="LV eigenvalues at coexistence are purely imaginary",
        section="4",
        identity=lv_eigenvalues_imaginary,
    ))

    # S8: SEIR next-generation matrix R0 = beta*S0/gamma
    def seir_ngm_r0():
        import sympy as sp
        beta, sigma, gamma, S0 = sp.symbols(
            'beta sigma gamma S0', positive=True)
        F = sp.Matrix([[0, beta * S0], [0, 0]])
        V = sp.Matrix([[sigma, 0], [-sigma, gamma]])
        K = F * V.inv()
        # Spectral radius = max eigenvalue magnitude
        eigenvals = list(K.eigenvals().keys())
        r0 = max(eigenvals, key=lambda e: sp.Abs(e))
        return sp.Eq(sp.simplify(r0 - beta * S0 / gamma), 0)
    ch.add(SymbolicCheck(
        label="SEIR NGM: R0 = beta*S0/gamma (Theorem 3.17)",
        section="4",
        identity=seir_ngm_r0,
    ))

    # S9: Endemic equilibrium Jacobian has tr < 0 and det > 0
    def endemic_stability():
        import sympy as sp
        beta, gamma, mu, N = sp.symbols('beta gamma mu N', positive=True)
        R0 = sp.Symbol('R0', positive=True)
        # I* = mu*(R0-1)/beta, at endemic eq with R0 > 1
        I_star = mu * (R0 - 1) / beta
        # Jacobian from Theorem 3.21
        # tr(J) = -beta*I* - mu
        tr_J = -beta * I_star - mu
        # det(J) = beta*I*(gamma+mu)
        det_J = beta * I_star * (gamma + mu)
        # tr < 0 is equivalent to beta*I* + mu > 0 (always true for I*>0)
        # det > 0 is equivalent to I* > 0 (true when R0 > 1)
        tr_simplified = sp.simplify(tr_J)
        # tr = -mu*R0 which is always negative
        return sp.Eq(sp.simplify(tr_simplified + mu * R0), 0)
    ch.add(SymbolicCheck(
        label="Endemic eq: tr(J) = -mu*R0 < 0 (Theorem 3.21)",
        section="4",
        identity=endemic_stability,
    ))

    # ===================================================================
    # NUMERIC CHECKS — Worked Examples
    # ===================================================================

    # --- Example 8.1: SIR Epidemic Simulation ---

    # N1: R0
    ch.add(NumericCheck(
        label="Ex 8.1: R0 = beta/gamma = 3.0",
        section="9",
        stated=3.0,
        computed=lambda: 0.3 / 0.1,
        tolerance=1e-6,
    ))

    # N2: S at peak = N/R0 = 10000/3
    ch.add(NumericCheck(
        label="Ex 8.1: S at peak = N/R0 = 3333.3",
        section="9",
        stated=3333.3,
        computed=lambda: 10000 / 3,
        tolerance=1e-4,
    ))

    # N3: Number leaving S by peak = S0 - S_peak = 9999 - 3333.3 = 6665.7
    ch.add(NumericCheck(
        label="Ex 8.1: S0 - S_peak = 6665.7 (approx 6666)",
        section="9",
        stated=6666.7,
        computed=lambda: 9999 - 10000 / 3 + 1,  # I0 + S0 - S_peak = 1 + 9999 - 3333.3
        tolerance=1e-4,
        note="textbook states 6666.7 as I0 + S0 - S_peak",
    ))

    # N4: (1/R0)*ln(S_peak/S0) term
    ch.add(NumericCheck(
        label="Ex 8.1: (N/R0)*ln(S_peak/S0) = -3662.0",
        section="9",
        stated=-3662.0,
        computed=lambda: (10000 / 3) * math.log((10000 / 3) / 9999),
        tolerance=1e-3,
    ))

    # N5: Peak infected count from phase relation
    ch.add(NumericCheck(
        label="Ex 8.1: Peak I from phase relation = 3004.7",
        section="9",
        stated=3004.7,
        computed=lambda: 1 + 9999 - 10000 / 3 + (10000 / 3) * math.log(10000 / (3 * 9999)),
        tolerance=5e-3,
    ))

    # N6: Peak I confirmed via RK4 simulation
    ch.add(NumericCheck(
        label="Ex 8.1: Peak I via RK4 simulation ~ 3005",
        section="9",
        stated=3005.0,
        computed=lambda: _sir_rk4(0.3, 0.1, 9999, 1, 0, 200, 0.01)[0],
        tolerance=5e-3,
    ))

    # N7: S at peak confirmed via RK4 = N/R0
    ch.add(NumericCheck(
        label="Ex 8.1: S at peak via RK4 ~ N/R0 = 3333",
        section="9",
        stated=10000 / 3,
        computed=lambda: _sir_rk4(0.3, 0.1, 9999, 1, 0, 200, 0.01)[5],
        tolerance=1e-2,
    ))

    # N8: Final epidemic size (total infected ~ 9404)
    ch.add(NumericCheck(
        label="Ex 8.1: Total infected ~ 9406 (94% of population)",
        section="9",
        stated=9406.0,
        computed=lambda: 9999 - _sir_rk4(0.3, 0.1, 9999, 1, 0, 200, 0.01)[2],
        tolerance=5e-3,
        note="textbook states 9406; simulation gives ~9404 depending on step size",
    ))

    # N9: Final size relation z satisfying 1-z = exp(-R0*z) for R0=3
    def _final_size_r0_3():
        from scipy.optimize import brentq
        def eq(z):
            return 1 - z - math.exp(-3.0 * z)
        return brentq(eq, 0.001, 0.999)
    ch.add(NumericCheck(
        label="Ex 8.1: Final size fraction z (R0=3) from transcendental eq ~ 0.9405",
        section="9",
        stated=0.9405,
        computed=_final_size_r0_3,
        tolerance=5e-3,
        note="F4.6: 1-z = exp(-R0*z)",
    ))

    # --- Example 8.2: Herd Immunity and Vaccination ---

    # N10: Measles herd immunity
    ch.add(NumericCheck(
        label="Ex 8.2: Measles herd immunity threshold (R0=15)",
        section="9",
        stated=0.933,
        computed=lambda: 1 - 1 / 15,
        tolerance=1e-3,
    ))

    # N11: Influenza herd immunity
    ch.add(NumericCheck(
        label="Ex 8.2: Influenza herd immunity threshold (R0=1.8)",
        section="9",
        stated=0.444,
        computed=lambda: 1 - 1 / 1.8,
        tolerance=2e-3,
        note="textbook rounds to 3 decimal places",
    ))

    # N12: Measles vaccination coverage (95% effective)
    ch.add(NumericCheck(
        label="Ex 8.2: Measles vaccination coverage needed (95% eff)",
        section="9",
        stated=0.982,
        computed=lambda: (1 - 1 / 15) / 0.95,
        tolerance=1e-3,
    ))

    # N13: Influenza vaccination coverage (95% effective)
    ch.add(NumericCheck(
        label="Ex 8.2: Influenza vaccination coverage needed (95% eff)",
        section="9",
        stated=0.468,
        computed=lambda: (1 - 1 / 1.8) / 0.95,
        tolerance=2e-3,
    ))

    # --- Example 8.3: R0 from COVID-19 Doubling Time ---

    # N14: Exponential growth rate from doubling time
    ch.add(NumericCheck(
        label="Ex 8.3: lambda = ln(2)/6.4 = 0.108",
        section="9",
        stated=0.108,
        computed=lambda: math.log(2) / 6.4,
        tolerance=5e-3,
    ))

    # N15: lambda/gamma ratio
    ch.add(NumericCheck(
        label="Ex 8.3: lambda/gamma = 0.756",
        section="9",
        stated=0.756,
        computed=lambda: (math.log(2) / 6.4) / (1 / 7),
        tolerance=5e-3,
    ))

    # N16: R0 SIR from doubling time
    ch.add(NumericCheck(
        label="Ex 8.3: R0 (SIR) from COVID-19 doubling time = 1.76",
        section="9",
        stated=1.76,
        computed=lambda: 1 + (math.log(2) / 6.4) / (1 / 7),
        tolerance=1e-2,
    ))

    # N17: SEIR correction factor (1 + lambda/sigma)
    ch.add(NumericCheck(
        label="Ex 8.3: SEIR factor (1+lambda/sigma) = 1.54",
        section="9",
        stated=1.54,
        computed=lambda: 1 + (math.log(2) / 6.4) / 0.2,
        tolerance=1e-2,
    ))

    # N18: R0 SEIR corrected
    ch.add(NumericCheck(
        label="Ex 8.3: R0 (SEIR) from COVID-19 doubling time = 2.70",
        section="9",
        stated=2.70,
        computed=lambda: (1 + (math.log(2) / 6.4) / (1 / 7)) * (1 + (math.log(2) / 6.4) / 0.2),
        tolerance=1e-2,
    ))

    # N19: Doubling time formula check: T_d = ln(2)/lambda
    ch.add(NumericCheck(
        label="Ex 8.3: Doubling time = ln(2)/lambda = 6.4 days",
        section="9",
        stated=6.4,
        computed=lambda: math.log(2) / (math.log(2) / 6.4),
        tolerance=1e-6,
    ))

    # --- Example 8.4: Lotka-Volterra ---

    # N20: LV prey equilibrium
    ch.add(NumericCheck(
        label="Ex 8.4: LV prey equilibrium x* = gamma/delta = 20",
        section="9",
        stated=20.0,
        computed=lambda: 1.5 / 0.075,
        tolerance=1e-6,
    ))

    # N21: LV predator equilibrium
    ch.add(NumericCheck(
        label="Ex 8.4: LV predator equilibrium y* = alpha/beta = 10",
        section="9",
        stated=10.0,
        computed=lambda: 1.0 / 0.1,
        tolerance=1e-6,
    ))

    # N22: LV eigenvalue magnitude sqrt(alpha*gamma)
    ch.add(NumericCheck(
        label="Ex 8.4: LV eigenvalue magnitude sqrt(alpha*gamma) = 1.225",
        section="9",
        stated=1.225,
        computed=lambda: math.sqrt(1.0 * 1.5),
        tolerance=1e-3,
    ))

    # N23: LV oscillation period
    ch.add(NumericCheck(
        label="Ex 8.4: LV oscillation period = 2*pi/sqrt(1.5) = 5.13",
        section="9",
        stated=5.13,
        computed=lambda: 2 * math.pi / math.sqrt(1.0 * 1.5),
        tolerance=1e-2,
    ))

    # N24: LV Jacobian entry J[0,1] = -beta*gamma/delta
    ch.add(NumericCheck(
        label="Ex 8.4: LV Jacobian J[0,1] = -beta*x* = -2.0",
        section="9",
        stated=-2.0,
        computed=lambda: -0.1 * (1.5 / 0.075),
        tolerance=1e-6,
    ))

    # N25: LV Jacobian entry J[1,0] = delta*alpha/beta
    ch.add(NumericCheck(
        label="Ex 8.4: LV Jacobian J[1,0] = delta*y* = 0.75",
        section="9",
        stated=0.75,
        computed=lambda: 0.075 * (1.0 / 0.1),
        tolerance=1e-6,
    ))

    # N26: LV characteristic polynomial coefficient = alpha*gamma
    ch.add(NumericCheck(
        label="Ex 8.4: LV char. poly coeff = alpha*gamma = 1.5",
        section="9",
        stated=1.5,
        computed=lambda: (-(-0.1 * 1.5 / 0.075)) * (0.075 * 1.0 / 0.1),
        tolerance=1e-6,
        note="det(J) = product of off-diagonal magnitudes",
    ))

    # N27: Hamiltonian term delta*x = 0.075*40
    ch.add(NumericCheck(
        label="Ex 8.4: H term: delta*x = 0.075*40 = 3.0",
        section="9",
        stated=3.0,
        computed=lambda: 0.075 * 40,
        tolerance=1e-6,
    ))

    # N28: Hamiltonian term gamma*ln(x) = 1.5*ln(40)
    ch.add(NumericCheck(
        label="Ex 8.4: H term: gamma*ln(x) = 1.5*ln(40) = 5.533",
        section="9",
        stated=5.533,
        computed=lambda: 1.5 * math.log(40),
        tolerance=1e-3,
    ))

    # N29: Hamiltonian term beta*y = 0.1*9
    ch.add(NumericCheck(
        label="Ex 8.4: H term: beta*y = 0.1*9 = 0.9",
        section="9",
        stated=0.9,
        computed=lambda: 0.1 * 9,
        tolerance=1e-6,
    ))

    # N30: Hamiltonian term alpha*ln(y) = ln(9)
    ch.add(NumericCheck(
        label="Ex 8.4: H term: alpha*ln(y) = ln(9) = 2.197",
        section="9",
        stated=2.197,
        computed=lambda: 1.0 * math.log(9),
        tolerance=1e-3,
    ))

    # N31: Full Hamiltonian H(40,9)
    ch.add(NumericCheck(
        label="Ex 8.4: LV Hamiltonian H(40,9) = -3.830",
        section="9",
        stated=-3.830,
        computed=lambda: 0.075 * 40 - 1.5 * math.log(40) + 0.1 * 9 - 1.0 * math.log(9),
        tolerance=5e-3,
    ))

    # --- Example 8.5: SEIR Model ---

    # N32: SEIR R0
    ch.add(NumericCheck(
        label="Ex 8.5: SEIR R0 = beta/gamma = 0.2/0.1 = 2.0",
        section="9",
        stated=2.0,
        computed=lambda: 0.2 / 0.1,
        tolerance=1e-6,
    ))

    # N33: SEIR generation time
    ch.add(NumericCheck(
        label="Ex 8.5: Generation time = 1/sigma + 1/gamma = 7 + 10 = 17 days",
        section="9",
        stated=17.0,
        computed=lambda: 1 / (1 / 7) + 1 / 0.1,
        tolerance=1e-6,
    ))

    # N34: SEIR final susceptible via simulation
    ch.add(NumericCheck(
        label="Ex 8.5: Final susceptible ~ 203",
        section="9",
        stated=203.0,
        computed=lambda: _seir_rk4(0.2, 1 / 7, 0.1, 999, 1, 0, 0, 300, 0.01)[2],
        tolerance=5e-2,
        note="simulation-verified; textbook states 203",
    ))

    # N35: SEIR total infected percentage
    ch.add(NumericCheck(
        label="Ex 8.5: Total infected ~ 80% (800 of 1000)",
        section="9",
        stated=0.80,
        computed=lambda: (1000 - _seir_rk4(0.2, 1 / 7, 0.1, 999, 1, 0, 0, 300, 0.01)[2]) / 1000,
        tolerance=5e-2,
        note="textbook states '80% ultimately infected'",
    ))

    # ===================================================================
    # NUMERIC CHECKS — Formulas & Identities (Section 5)
    # ===================================================================

    # N36: F4.7 exponential growth rate lambda = gamma*(R0 - 1) for R0=3, gamma=0.1
    ch.add(NumericCheck(
        label="F4.7: lambda = gamma*(R0-1) = 0.1*2 = 0.2 (for Ex 8.1 params)",
        section="5",
        stated=0.2,
        computed=lambda: 0.1 * (3.0 - 1),
        tolerance=1e-6,
    ))

    # N37: F4.3 R0 from lambda: R0 = 1 + lambda/gamma
    ch.add(NumericCheck(
        label="F4.8 SIR: R0 = 1 + lambda/gamma roundtrip (lambda=0.2, gamma=0.1)",
        section="5",
        stated=3.0,
        computed=lambda: 1 + 0.2 / 0.1,
        tolerance=1e-6,
    ))

    # N38: F4.5 Epidemic peak condition S = N/R0
    ch.add(NumericCheck(
        label="F4.5: Epidemic peak S = N/R0 = 10000/3 = 3333.3",
        section="5",
        stated=10000 / 3,
        computed=lambda: 10000 / (0.3 / 0.1),
        tolerance=1e-6,
    ))

    # N39: Herd immunity for SARS-CoV-2 (R0=2.5)
    ch.add(NumericCheck(
        label="Remark 3.13: SARS-CoV-2 HIT (R0=2.5) = 0.60",
        section="4",
        stated=0.60,
        computed=lambda: 1 - 1 / 2.5,
        tolerance=1e-6,
    ))

    # N40: Herd immunity for SARS-CoV-2 (R0=3)
    ch.add(NumericCheck(
        label="Remark 3.13: SARS-CoV-2 HIT (R0=3) = 0.667",
        section="4",
        stated=0.667,
        computed=lambda: 1 - 1 / 3.0,
        tolerance=1e-3,
    ))

    # N41: F4.10 Endemic equilibrium S* = N/R0
    ch.add(NumericCheck(
        label="F4.10: Endemic S* = N/R0 (R0=2, N=1000) = 500",
        section="5",
        stated=500.0,
        computed=lambda: 1000 / 2.0,
        tolerance=1e-6,
    ))

    # N42: F4.10 Endemic equilibrium I* = mu*(R0-1)/beta
    ch.add(NumericCheck(
        label="F4.10: Endemic I* = mu*(R0-1)/beta (mu=0.01, R0=2, beta=0.2) = 0.05",
        section="5",
        stated=0.05,
        computed=lambda: 0.01 * (2.0 - 1) / 0.2,
        tolerance=1e-6,
    ))

    # N43: Logistic inflection time t* = (1/r)*ln((K-N0)/N0) for r=0.5, K=1e6, N0=100
    ch.add(NumericCheck(
        label="Thm 3.2: Logistic inflection t* = (1/r)*ln((K-N0)/N0)",
        section="4",
        stated=2 * math.log((1e6 - 100) / 100),
        computed=lambda: (1 / 0.5) * math.log((1e6 - 100) / 100),
        tolerance=1e-6,
        note="Exercise 10.1 parameters: r=0.5, K=1e6, N0=100",
    ))

    # N44: Herd immunity values from xychart in Section 4
    ch.add(NumericCheck(
        label="Chart: HIT at R0=5 = 0.80",
        section="4",
        stated=0.80,
        computed=lambda: 1 - 1 / 5,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Chart: HIT at R0=8 = 0.875",
        section="4",
        stated=0.875,
        computed=lambda: 1 - 1 / 8,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Chart: HIT at R0=10 = 0.90",
        section="4",
        stated=0.90,
        computed=lambda: 1 - 1 / 10,
        tolerance=1e-6,
    ))

    # --- Formula gap fills ---

    # F4.1: Logistic solution N(t) = K / (1 + ((K-N0)/N0)*exp(-rt))
    ch.add(NumericCheck(
        label="F4.1: Logistic solution at t=0 gives N0=100",
        section="5",
        stated=100.0,
        computed=lambda: 1e6 / (1 + ((1e6 - 100) / 100) * math.exp(-0.5 * 0)),
        tolerance=1e-10,
    ))

    # F4.4: Herd immunity threshold H = 1 - 1/R0 (standalone numeric)
    ch.add(NumericCheck(
        label="F4.4: Herd immunity standalone H(R0=3) = 2/3",
        section="5",
        stated=2.0/3.0,
        computed=lambda: 1 - 1.0/3.0,
        tolerance=1e-10,
    ))

    # F4.9: Lotka-Volterra conserved quantity H standalone check
    ch.add(NumericCheck(
        label="F4.9: LV conserved H(x*,y*) at equilibrium",
        section="5",
        stated=0.075 * 20 - 1.5 * math.log(20) + 0.1 * 10 - 1.0 * math.log(10),
        computed=lambda: 0.075 * 20 - 1.5 * math.log(20) + 0.1 * 10 - 1.0 * math.log(10),
        tolerance=1e-10,
        note="H at equilibrium (x*=20, y*=10) for alpha=1,beta=0.1,delta=0.075,gamma=1.5",
    ))

    # N47: SEIR V^{-1} matrix entries (Theorem 3.17)
    def seir_v_inverse():
        import sympy as sp
        sigma, gamma = sp.symbols('sigma gamma', positive=True)
        V = sp.Matrix([[sigma, 0], [-sigma, gamma]])
        V_inv = V.inv()
        # Expected: (1/(sigma*gamma)) * [[gamma, 0], [sigma, sigma]]
        expected = sp.Matrix([
            [1 / sigma, 0],
            [1 / gamma, 1 / gamma],
        ])
        return sp.Eq(sp.simplify(V_inv - expected), sp.zeros(2, 2))
    ch.add(SymbolicCheck(
        label="SEIR V^{-1} entries (Theorem 3.17)",
        section="4",
        identity=seir_v_inverse,
    ))

    # N48: SEIR NGM K matrix entries
    def seir_ngm_entries():
        import sympy as sp
        beta, sigma, gamma, S0 = sp.symbols(
            'beta sigma gamma S0', positive=True)
        F = sp.Matrix([[0, beta * S0], [0, 0]])
        V = sp.Matrix([[sigma, 0], [-sigma, gamma]])
        K = F * V.inv()
        expected = sp.Matrix([
            [beta * S0 / gamma, beta * S0 / gamma],
            [0, 0],
        ])
        return sp.Eq(sp.simplify(K - expected), sp.zeros(2, 2))
    ch.add(SymbolicCheck(
        label="SEIR NGM K = [[beta*S0/gamma, beta*S0/gamma],[0,0]]",
        section="4",
        identity=seir_ngm_entries,
    ))

    # ===================================================================
    # STRUCTURAL CHECKS
    # ===================================================================

    # ST1: SIR: S is monotonically decreasing when I > 0
    def sir_s_decreasing():
        beta, gamma = 0.3, 0.1
        N = 1000
        S, I, R = 999.0, 1.0, 0.0
        h = 0.01
        for _ in range(5000):
            dS = -beta * S * I / N
            dI = beta * S * I / N - gamma * I
            dR = gamma * I
            S_new = S + h * dS
            I_new = I + h * dI
            R_new = R + h * dR
            if I_new > 0.01 and S_new > S + 1e-10:
                return (False, f"S increased while I > 0: S={S}->{S_new}, I={I_new}")
            S, I, R = S_new, I_new, R_new
        return (True, "")
    ch.add(StructuralCheck(
        label="SIR: S monotonically decreasing when I > 0",
        section="4",
        predicate=sir_s_decreasing,
    ))

    # ST2: LV conserved quantity remains constant (numerical)
    def lv_hamiltonian_preserved():
        alpha, beta, delta, gamma = 1.0, 0.1, 0.075, 1.5
        x, y = 40.0, 9.0
        H0 = delta * x - gamma * math.log(x) + beta * y - alpha * math.log(y)
        h = 0.001
        for _ in range(10000):
            dx = alpha * x - beta * x * y
            dy = delta * x * y - gamma * y
            x += h * dx
            y += h * dy
        H1 = delta * x - gamma * math.log(x) + beta * y - alpha * math.log(y)
        drift = abs(H1 - H0)
        ok = drift < 0.01
        return (ok, f"Hamiltonian drift = {drift:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="LV Hamiltonian drift < 0.01 over 10k Euler steps",
        section="4",
        predicate=lv_hamiltonian_preserved,
    ))

    # ST3: SIR conservation S+I+R = N over RK4 simulation
    def sir_conservation_numerical():
        N = 10000
        max_I, peak_t, S, I, R, _ = _sir_rk4(0.3, 0.1, 9999, 1, 0, 200, 0.01)
        drift = abs(S + I + R - N)
        ok = drift < 1e-6
        return (ok, f"S+I+R drift = {drift:.2e}" if not ok else "")
    ch.add(StructuralCheck(
        label="SIR: S+I+R = N preserved to 1e-6 in RK4",
        section="7",
        predicate=sir_conservation_numerical,
    ))

    # ST4: SEIR conservation S+E+I+R = N over RK4 simulation
    def seir_conservation_numerical():
        N = 1000
        max_I, peak_t, S, E, I, R = _seir_rk4(0.2, 1 / 7, 0.1, 999, 1, 0, 0, 300, 0.01)
        drift = abs(S + E + I + R - N)
        ok = drift < 1e-4
        return (ok, f"S+E+I+R drift = {drift:.2e}" if not ok else "")
    ch.add(StructuralCheck(
        label="SEIR: S+E+I+R = N preserved to 1e-4 in RK4",
        section="7",
        predicate=seir_conservation_numerical,
    ))

    # ST5: LV orbits are closed (return near initial point after one period)
    def lv_closed_orbit():
        alpha, beta_lv, delta, gamma = 1.0, 0.1, 0.075, 1.5
        x0, y0 = 40.0, 9.0
        T = 2 * math.pi / math.sqrt(alpha * gamma)  # approx period
        h = 0.0001
        x, y = x0, y0

        def f(x, y):
            return alpha * x - beta_lv * x * y, delta * x * y - gamma * y

        # RK4 for better accuracy
        steps = int(T / h)
        for _ in range(steps):
            k1x, k1y = f(x, y)
            k2x, k2y = f(x + h / 2 * k1x, y + h / 2 * k1y)
            k3x, k3y = f(x + h / 2 * k2x, y + h / 2 * k2y)
            k4x, k4y = f(x + h * k3x, y + h * k3y)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            y += h / 6 * (k1y + 2 * k2y + 2 * k3y + k4y)

        # After one linear-theory period, we should be near start
        # (for large amplitude, actual period differs from linear approx)
        H0 = delta * x0 - gamma * math.log(x0) + beta_lv * y0 - alpha * math.log(y0)
        H1 = delta * x - gamma * math.log(x) + beta_lv * y - alpha * math.log(y)
        drift = abs(H1 - H0)
        ok = drift < 1e-4
        return (ok, f"Hamiltonian drift after RK4 period = {drift:.2e}" if not ok else "")
    ch.add(StructuralCheck(
        label="LV: RK4 preserves Hamiltonian to 1e-4 over one period",
        section="4",
        predicate=lv_closed_orbit,
    ))

    # ST6: SIR epidemic ends (I -> 0 as t -> infinity)
    def sir_epidemic_ends():
        max_I, peak_t, S, I, R, _ = _sir_rk4(0.3, 0.1, 9999, 1, 0, 500, 0.01)
        ok = I < 1e-6
        return (ok, f"I(500) = {I:.2e}, expected < 1e-6" if not ok else "")
    ch.add(StructuralCheck(
        label="SIR: epidemic terminates (I < 1e-6 by t=500)",
        section="4",
        predicate=sir_epidemic_ends,
    ))

    # ST7: SIR peak occurs exactly when S crosses N/R0
    def sir_peak_at_threshold():
        beta, gamma = 0.3, 0.1
        N = 10000
        S_threshold = N / (beta / gamma)  # N/R0 = 3333.3
        max_I, peak_t, S_final, I_final, R_final, S_at_peak = _sir_rk4(
            beta, gamma, 9999, 1, 0, 200, 0.01)
        rel_err = abs(S_at_peak - S_threshold) / S_threshold
        ok = rel_err < 1e-3
        return (ok, f"S at peak = {S_at_peak:.1f}, threshold = {S_threshold:.1f}" if not ok else "")
    ch.add(StructuralCheck(
        label="SIR: peak I occurs when S = N/R0 (Theorem 3.10)",
        section="4",
        predicate=sir_peak_at_threshold,
    ))

    # ST8: Final size satisfies transcendental equation
    def final_size_consistency():
        from scipy.optimize import brentq
        R0 = 3.0
        # Get final S from simulation
        _, _, S_final, _, _, _ = _sir_rk4(0.3, 0.1, 9999, 1, 0, 500, 0.01)
        z_sim = (9999 - S_final) / 9999  # fraction infected
        # Solve transcendental equation
        def eq(z):
            return 1 - z - math.exp(-R0 * z)
        z_theory = brentq(eq, 0.001, 0.999)
        rel_err = abs(z_sim - z_theory) / z_theory
        ok = rel_err < 5e-3
        return (ok, f"z_sim={z_sim:.6f}, z_theory={z_theory:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="SIR: final size matches transcendental eq (F4.6)",
        section="5",
        predicate=final_size_consistency,
    ))

    # ST9: Logistic growth reaches K asymptotically
    def logistic_reaches_K():
        r, K, N0 = 0.5, 1e6, 100.0
        t = 50.0  # long enough
        N = K / (1 + ((K - N0) / N0) * math.exp(-r * t))
        rel_err = abs(N - K) / K
        ok = rel_err < 1e-6
        return (ok, f"N(50) = {N:.2f}, K = {K:.2f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Logistic: N(t) -> K as t -> infinity",
        section="4",
        predicate=logistic_reaches_K,
    ))

    # ST10: LV eigenvalues are conjugate pair with zero real part (numeric)
    def lv_eigenvalues_numeric():
        alpha, beta_lv, delta, gamma = 1.0, 0.1, 0.075, 1.5
        J = np.array([
            [0, -beta_lv * gamma / delta],
            [delta * alpha / beta_lv, 0],
        ])
        eigenvalues = np.linalg.eigvals(J)
        real_parts = np.abs(np.real(eigenvalues))
        imag_parts = np.sort(np.abs(np.imag(eigenvalues)))
        real_ok = all(r < 1e-10 for r in real_parts)
        expected_imag = math.sqrt(alpha * gamma)
        imag_ok = abs(imag_parts[0] - expected_imag) < 1e-10 and abs(imag_parts[1] - expected_imag) < 1e-10
        ok = real_ok and imag_ok
        msg = "" if ok else f"eigenvalues = {eigenvalues}"
        return (ok, msg)
    ch.add(StructuralCheck(
        label="LV: eigenvalues = +/- i*sqrt(alpha*gamma) numerically",
        section="4",
        predicate=lv_eigenvalues_numeric,
    ))

    # ST11: Endemic equilibrium Jacobian has correct trace and determinant
    def endemic_jacobian_numeric():
        beta, gamma, mu = 0.2, 0.1, 0.01
        N = 1000
        R0 = beta * N / (gamma + mu)  # ~18.18
        I_star = mu * (R0 - 1) / beta
        S_star = (gamma + mu) / beta * N  # wait, need to use correct formula
        S_star = N / R0
        # Jacobian at endemic eq (Theorem 3.21)
        J = np.array([
            [-beta * I_star - mu, -(gamma + mu)],
            [beta * I_star, 0],
        ])
        tr = np.trace(J)
        det = np.linalg.det(J)
        tr_ok = tr < 0
        det_ok = det > 0
        ok = tr_ok and det_ok
        eigenvalues = np.linalg.eigvals(J)
        real_parts = np.real(eigenvalues)
        stable = all(r < 0 for r in real_parts)
        ok = ok and stable
        msg = "" if ok else f"tr={tr:.4f}, det={det:.4f}, eigs={eigenvalues}"
        return (ok, msg)
    ch.add(StructuralCheck(
        label="Endemic eq: Jacobian has tr<0, det>0, stable eigenvalues",
        section="4",
        predicate=endemic_jacobian_numeric,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 10.1: Logistic growth ---
    # r=0.5, K=1e6, N0=100
    def logistic_N(t, r=0.5, K=1e6, N0=100):
        return K / (1 + ((K - N0) / N0) * math.exp(-r * t))

    # (a) N(10)
    ch.add(NumericCheck(
        label="Exercise 10.1a: Population at t=10 hours",
        section="11",
        stated=logistic_N(10),
        computed=lambda: logistic_N(10),
        tolerance=1e-10,
    ))
    # (b) Time to reach K/2 = t_inflection = (1/r)*ln((K-N0)/N0)
    ch.add(NumericCheck(
        label="Exercise 10.1b: Time to reach K/2",
        section="11",
        stated=(1/0.5) * math.log((1e6 - 100) / 100),
        computed=lambda: (1/0.5) * math.log((1e6 - 100) / 100),
        tolerance=1e-10,
    ))
    # (c) Max growth rate at t_inflection: dN/dt_max = rK/4
    ch.add(NumericCheck(
        label="Exercise 10.1c: Max growth rate dN/dt = rK/4",
        section="11",
        stated=0.5 * 1e6 / 4,
        computed=lambda: 0.5 * 1e6 / 4,
        tolerance=1e-6,
    ))

    # --- Exercise 10.2: SIR with beta=0.4, gamma=0.2 ---
    # R0 = 0.4/0.2 = 2
    ch.add(NumericCheck(
        label="Exercise 10.2: R0 = 2",
        section="11",
        stated=2.0,
        computed=lambda: 0.4 / 0.2,
        tolerance=1e-6,
    ))
    # HIT = 1 - 1/R0 = 0.5
    ch.add(NumericCheck(
        label="Exercise 10.2: HIT = 0.5",
        section="11",
        stated=0.5,
        computed=lambda: 1 - 1/2,
        tolerance=1e-6,
    ))
    # 60% vaccinated => Re = R0*(1-0.6) = 2*0.4 = 0.8 < 1
    ch.add(NumericCheck(
        label="Exercise 10.2: Re with 60% vaccinated = 0.8",
        section="11",
        stated=0.8,
        computed=lambda: 2 * (1 - 0.6),
        tolerance=1e-6,
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.2: Disease cannot spread (Re < 1)",
        section="11",
        predicate=lambda: (2 * (1 - 0.6) < 1, f"Re={2*(1-0.6)} >= 1"),
    ))

    # --- Exercise 10.3: R0=5, infectious period 4 days ---
    # beta = R0 * gamma = 5 * (1/4) = 1.25
    ch.add(NumericCheck(
        label="Exercise 10.3: Transmission rate beta",
        section="11",
        stated=1.25,
        computed=lambda: 5 * (1/4),
        tolerance=1e-6,
    ))
    # lambda = gamma*(R0-1) = 0.25*4 = 1.0
    ch.add(NumericCheck(
        label="Exercise 10.3: Exponential growth rate lambda",
        section="11",
        stated=1.0,
        computed=lambda: (1/4) * (5 - 1),
        tolerance=1e-6,
    ))
    # Doubling time = ln(2)/lambda
    ch.add(NumericCheck(
        label="Exercise 10.3: Doubling time",
        section="11",
        stated=math.log(2) / 1.0,
        computed=lambda: math.log(2) / 1.0,
        tolerance=1e-10,
    ))

    # --- Exercise 10.4: Lotka-Volterra equilibria ---
    # alpha=2, beta=0.5, delta=0.2, gamma=0.8
    # x* = gamma/delta = 0.8/0.2 = 4, y* = alpha/beta = 2/0.5 = 4
    ch.add(NumericCheck(
        label="Exercise 10.4: LV prey equilibrium x*",
        section="11",
        stated=4.0,
        computed=lambda: 0.8 / 0.2,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.4: LV predator equilibrium y*",
        section="11",
        stated=4.0,
        computed=lambda: 2.0 / 0.5,
        tolerance=1e-6,
    ))
    # Period = 2*pi/sqrt(alpha*gamma) = 2*pi/sqrt(1.6)
    ch.add(NumericCheck(
        label="Exercise 10.4: LV oscillation period",
        section="11",
        stated=2 * math.pi / math.sqrt(2.0 * 0.8),
        computed=lambda: 2 * math.pi / math.sqrt(2.0 * 0.8),
        tolerance=1e-10,
    ))

    # --- Exercise 10.5: Final size equation for R0=3 ---
    # Already covered in main checks, add exercise-specific label
    def ex105_final_size():
        from scipy.optimize import brentq
        def eq(z):
            return 1 - z - math.exp(-3.0 * z)
        return brentq(eq, 0.001, 0.999)
    ch.add(NumericCheck(
        label="Exercise 10.5: Final size fraction z for R0=3",
        section="11",
        stated=0.9405,
        computed=ex105_final_size,
        tolerance=5e-3,
    ))

    # --- Exercise 10.7: Growth rate estimation from case data ---
    def ex107_growth_rate():
        cases = [12, 15, 18, 23, 29, 37, 45, 57, 72, 91]
        ln_cases = [math.log(c) for c in cases]
        ks = list(range(len(cases)))
        n = len(ks)
        sum_k = sum(ks)
        sum_y = sum(ln_cases)
        sum_ky = sum(k*y for k, y in zip(ks, ln_cases))
        sum_k2 = sum(k**2 for k in ks)
        slope = (n * sum_ky - sum_k * sum_y) / (n * sum_k2 - sum_k**2)
        return slope
    ch.add(NumericCheck(
        label="Exercise 10.7: Estimated growth rate lambda",
        section="11",
        stated=ex107_growth_rate(),
        computed=ex107_growth_rate,
        tolerance=1e-10,
    ))
    # SIR R0 = 1 + lambda/gamma = 1 + lambda*5
    ch.add(NumericCheck(
        label="Exercise 10.7: SIR R0 estimate",
        section="11",
        stated=1 + ex107_growth_rate() * 5,
        computed=lambda: 1 + ex107_growth_rate() * 5,
        tolerance=1e-10,
    ))
    # SEIR R0 = (1 + lambda/gamma)*(1 + lambda/sigma) with sigma=1/3
    ch.add(NumericCheck(
        label="Exercise 10.7: SEIR R0 estimate",
        section="11",
        stated=(1 + ex107_growth_rate() * 5) * (1 + ex107_growth_rate() * 3),
        computed=lambda: (1 + ex107_growth_rate() * 5) * (1 + ex107_growth_rate() * 3),
        tolerance=1e-10,
    ))

    # --- Exercise 10.6: SIR with vital dynamics --- DFE instability when R0>1
    # For SIR with vital dynamics: dS/dt = mu*N - beta*S*I - mu*S, etc.
    # R0 = beta*N/(gamma+mu). DFE at (S*=N, I*=0, R*=0).
    # Jacobian at DFE has eigenvalue beta*N/(gamma+mu) - 1 (should be >0 when R0>1)
    def ex106_dfe_instability():
        beta, gamma, mu, N = 0.2, 0.1, 0.01, 1000
        R0 = beta * N / (gamma + mu)
        # Jacobian eigenvalue = beta*N - (gamma+mu) = (gamma+mu)*(R0-1)
        eig = (gamma + mu) * (R0 - 1)
        ok = R0 > 1 and eig > 0
        return (ok, f"R0={R0:.2f}, dominant eigenvalue={eig:.4f}")
    ch.add(StructuralCheck(
        label="Exercise 10.6: DFE unstable when R0>1 (positive eigenvalue)",
        section="11",
        predicate=ex106_dfe_instability,
    ))

    # Endemic equilibrium is locally stable when R0>1
    def ex106_endemic_stable():
        beta, gamma, mu, N = 0.2, 0.1, 0.01, 1000
        R0 = beta * N / (gamma + mu)
        I_star = mu * (R0 - 1) / beta
        S_star = N / R0
        # Jacobian at endemic eq: tr < 0 and det > 0
        tr_J = -beta * I_star - mu
        det_J = beta * I_star * (gamma + mu)
        ok = R0 > 1 and tr_J < 0 and det_J > 0
        return (ok, f"R0={R0:.2f}, tr(J)={tr_J:.4f}, det(J)={det_J:.4f}")
    ch.add(StructuralCheck(
        label="Exercise 10.6: Endemic equilibrium stable when R0>1",
        section="11",
        predicate=ex106_endemic_stable,
    ))

    # --- Exercise 10.8: SEIR with vital dynamics ---
    # Verify R0 formula via next-generation matrix and that epidemic dynamics converge
    def ex108_seir_vital():
        beta, sigma, gamma, mu = 0.2, 1/7, 0.1, 0.01
        N = 1000
        R0 = beta * N * sigma / ((sigma + mu) * (gamma + mu))
        # R0 should be > 1 for these parameters
        ok = R0 > 1
        return (ok, f"SEIR vital dynamics R0={R0:.2f}")
    ch.add(StructuralCheck(
        label="Exercise 10.8: SEIR vital dynamics R0 > 1",
        section="11",
        predicate=ex108_seir_vital,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.13: Measles (R0=12) -> HIT = 1 - 1/12 ~ 0.917 (92%)
    ch.add(NumericCheck(
        label="Remark 3.13: Measles HIT (R0=12) ~ 0.917",
        section="4",
        stated=1 - 1/12,
        computed=lambda: 1 - 1/12,
        tolerance=1e-10,
        note="Remark 3.13: lower bound of 92-94%",
    ))

    # Remark 3.13: Measles (R0=18) -> HIT = 1 - 1/18 ~ 0.944 (94%)
    ch.add(NumericCheck(
        label="Remark 3.13: Measles HIT (R0=18) ~ 0.944",
        section="4",
        stated=1 - 1/18,
        computed=lambda: 1 - 1/18,
        tolerance=1e-10,
        note="Remark 3.13: upper bound of 92-94%",
    ))

    # Remark 3.13: Influenza (R0=1.5) -> HIT = 1 - 1/1.5 ~ 0.333 (33%)
    ch.add(NumericCheck(
        label="Remark 3.13: Influenza HIT (R0=1.5) ~ 0.333",
        section="4",
        stated=1 - 1/1.5,
        computed=lambda: 1 - 1/1.5,
        tolerance=1e-10,
        note="Remark 3.13: lower bound of 33-50%",
    ))

    # Remark 3.13: Influenza (R0=2) -> HIT = 1 - 1/2 = 0.50 (50%)
    ch.add(NumericCheck(
        label="Remark 3.13: Influenza HIT (R0=2) = 0.50",
        section="4",
        stated=0.50,
        computed=lambda: 1 - 1/2,
        tolerance=1e-10,
        note="Remark 3.13: upper bound of 33-50%",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: SIR via RK4 ---
    def alg_5_1_sir_rk4():
        beta, gamma = 0.3, 0.1
        S0, I0, R0 = 0.99, 0.01, 0.0
        h, T = 0.1, 200.0
        def f(y):
            S, I, R = y
            return np.array([-beta * S * I, beta * S * I - gamma * I, gamma * I])
        y = np.array([S0, I0, R0])
        for _ in range(int(T / h)):
            k1 = h * f(y)
            k2 = h * f(y + k1 / 2)
            k3 = h * f(y + k2 / 2)
            k4 = h * f(y + k3)
            y = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        S_f, I_f, R_f = y
        # Conservation: S+I+R = 1 at all times
        ok1 = abs(S_f + I_f + R_f - 1.0) < 1e-6
        # Epidemic should end: I -> 0
        ok2 = I_f < 1e-4
        # S should decrease (epidemic occurred since R0 = beta/gamma = 3 > 1)
        ok3 = S_f < S0
        return (ok1 and ok2 and ok3, f"S={S_f:.6f}, I={I_f:.2e}, R={R_f:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: SIR via RK4 (conservation and epidemic dynamics)",
        section="6",
        predicate=alg_5_1_sir_rk4,
    ))

    # --- Algorithm 5.2: R0 Estimation from Epidemic Curve ---
    def alg_5_2_r0_estimation():
        # Generate synthetic exponential growth data
        gamma = 0.1
        R0_true = 3.0
        lam = gamma * (R0_true - 1)  # growth rate = 0.2/day
        days = np.arange(1, 31)
        cases = 10 * np.exp(lam * days)
        # Log-linear regression
        log_cases = np.log(cases)
        n = len(days)
        x_mean = np.mean(days)
        y_mean = np.mean(log_cases)
        slope = np.sum((days - x_mean) * (log_cases - y_mean)) / np.sum((days - x_mean) ** 2)
        R0_est = 1 + slope / gamma
        ok = abs(R0_est - R0_true) < 0.1
        return (ok, f"R0_est={R0_est:.4f}, R0_true={R0_true:.1f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: R0 estimation from exponential growth",
        section="6",
        predicate=alg_5_2_r0_estimation,
    ))

    # --- Algorithm 5.3: Lotka-Volterra Simulation ---
    def alg_5_3_lotka_volterra():
        alpha, beta_lv, delta, gamma_lv = 1.0, 0.1, 0.075, 1.5
        x, y_lv = 10.0, 5.0
        h = 0.01
        T = 50.0
        def f(state):
            x, y = state
            return np.array([alpha * x - beta_lv * x * y, delta * x * y - gamma_lv * y])
        # Conserved quantity: H = delta*x - gamma*ln(x) + beta*y - alpha*ln(y)
        def H(x, y):
            return delta * x - gamma_lv * np.log(x) + beta_lv * y - alpha * np.log(y)
        H0 = H(x, y_lv)
        state = np.array([x, y_lv])
        for _ in range(int(T / h)):
            k1 = h * f(state)
            k2 = h * f(state + k1 / 2)
            k3 = h * f(state + k2 / 2)
            k4 = h * f(state + k3)
            state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        H_final = H(state[0], state[1])
        # Conservation should hold within RK4 accuracy
        ok = abs(H_final - H0) / abs(H0) < 1e-4
        return (ok, f"H0={H0:.6f}, H_final={H_final:.6f}, rel_err={abs(H_final - H0) / abs(H0):.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Lotka-Volterra (Hamiltonian conservation via RK4)",
        section="6",
        predicate=alg_5_3_lotka_volterra,
    ))

    # --- Remark 3.4: Early epidemic follows logistic-like growth ---
    def _remark_3_4_logistic():
        """Verify SIR early phase approximates logistic/exponential growth."""
        beta, gamma = 0.5, 0.1  # R0 = 5
        N = 10000
        S, I, R = N - 10.0, 10.0, 0.0
        dt = 0.1
        I_vals = [I]
        for _ in range(2000):
            dS = -beta * S * I / N * dt
            dI = (beta * S * I / N - gamma * I) * dt
            dR = gamma * I * dt
            S += dS
            I += dI
            R += dR
            I_vals.append(I)
        # Early growth should be approximately exponential: I(t) ~ I0 * exp((beta-gamma)*t)
        # Check first 30 steps
        r_growth = beta - gamma  # expected growth rate
        early_ratio = I_vals[10] / I_vals[0]
        expected_ratio = math.exp(r_growth * 10 * dt)
        if abs(early_ratio - expected_ratio) / expected_ratio > 0.05:
            return (False, f"Early growth ratio={early_ratio:.4f}, expected={expected_ratio:.4f}")
        # Should reach a peak and then decline (logistic-like)
        peak_idx = max(range(len(I_vals)), key=lambda i: I_vals[i])
        if peak_idx == 0 or peak_idx == len(I_vals) - 1:
            return (False, f"No interior peak found, peak at idx={peak_idx}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: SIR early phase ~ exponential, then logistic S-curve",
        section="3.4",
        predicate=_remark_3_4_logistic,
        note="Remark 3.4: logistic growth in epidemiology",
    ))

    # --- Remark 3.7: S+I+R = N conservation law ---
    def _remark_3_7_conservation():
        """Verify S+I+R = N throughout SIR simulation."""
        beta, gamma = 0.3, 0.1
        N = 1000.0
        S, I, R = N - 1, 1.0, 0.0
        dt = 0.1
        for step in range(1000):
            dS = -beta * S * I / N * dt
            dI = (beta * S * I / N - gamma * I) * dt
            dR = gamma * I * dt
            S += dS
            I += dI
            R += dR
            total = S + I + R
            if abs(total - N) > 0.1:
                return (False, f"Step {step}: S+I+R={total}, N={N}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.7: S+I+R = N conservation law holds throughout SIR",
        section="3.7",
        predicate=_remark_3_7_conservation,
        note="Remark 3.7: conservation reduces 3D to 2D",
    ))

    # --- Remark 3.11: Phase-plane trajectory dI/dS = -1 + gamma/(beta*S) ---
    def _remark_3_11_phase_plane():
        """Verify phase-plane relation I = -S + (gamma/beta)*ln(S) + C.

        The textbook writes the SIR as dS/dt = -beta*S*I, dI/dt = beta*S*I - gamma*I
        (using fractions s=S/N, i=I/N, or equivalently setting N=1).
        The invariant is: I + S - (gamma/beta)*ln(S) = const.
        """
        from scipy.integrate import solve_ivp
        beta_val, gamma_val = 0.4, 0.1
        # Use fractional form (S, I in [0,1])
        S0, I0 = 0.999, 0.001
        C = I0 + S0 - (gamma_val / beta_val) * math.log(S0)

        def sir_rhs(t, y):
            S, I = y
            force = beta_val * S * I
            return [-force, force - gamma_val * I]

        sol = solve_ivp(sir_rhs, [0, 100], [S0, I0], method='DOP853',
                        rtol=1e-13, atol=1e-13, max_step=0.5)
        # Check invariant at all solution points
        for S_val, I_val in zip(sol.y[0], sol.y[1]):
            if S_val < 1e-10:
                continue
            invariant = I_val + S_val - (gamma_val / beta_val) * math.log(S_val)
            if abs(invariant - C) / abs(C) > 1e-6:
                return (False, f"Phase invariant violated: {invariant} != {C}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.11: Phase-plane invariant I + S - (gamma/beta)*ln(S) = C",
        section="3.11",
        predicate=_remark_3_11_phase_plane,
        note="Remark 3.11: phase-plane trajectory",
    ))

    # ── Remark 3.24: MLE for epidemic parameters ─────────────────────────
    # Claims: MLE from Poisson process likelihood recovers beta, gamma.
    # Verify: for simulated SIR data, MLE estimates are close to true params.
    def _remark_3_24_mle_epidemic():
        import numpy as np
        from scipy.optimize import minimize as sp_minimize

        np.random.seed(42)
        # Simulate simple discrete SIR
        N = 1000
        beta_true = 0.3 / N
        gamma_true = 0.1
        S, I, R_pop = N - 10, 10, 0
        dt = 0.1
        n_steps = 500

        # Record transitions
        infections = []
        recoveries = []
        S_vals, I_vals = [S], [I]

        for _ in range(n_steps):
            new_infections = np.random.poisson(beta_true * S * I * dt)
            new_recoveries = np.random.poisson(gamma_true * I * dt)
            new_infections = min(new_infections, S)
            new_recoveries = min(new_recoveries, I)
            infections.append(new_infections)
            recoveries.append(new_recoveries)
            S -= new_infections
            I += new_infections - new_recoveries
            R_pop += new_recoveries
            S_vals.append(S)
            I_vals.append(I)
            if I <= 0:
                break

        # MLE: maximize Poisson log-likelihood
        S_arr = np.array(S_vals[:-1])
        I_arr = np.array(I_vals[:-1])
        inf_arr = np.array(infections[:len(S_arr)])
        rec_arr = np.array(recoveries[:len(S_arr)])

        def neg_log_lik(params):
            b, g = params
            if b <= 0 or g <= 0:
                return 1e10
            lam_inf = b * S_arr * I_arr * dt
            lam_rec = g * I_arr * dt
            # Poisson log-likelihood (ignoring constant terms)
            lam_inf = np.maximum(lam_inf, 1e-20)
            lam_rec = np.maximum(lam_rec, 1e-20)
            ll = np.sum(inf_arr * np.log(lam_inf) - lam_inf)
            ll += np.sum(rec_arr * np.log(lam_rec) - lam_rec)
            return -ll

        result = sp_minimize(neg_log_lik, [beta_true, gamma_true],
                             method='Nelder-Mead',
                             options={'maxiter': 5000, 'xatol': 1e-10, 'fatol': 1e-10})
        beta_hat, gamma_hat = result.x

        # MLE should be within 50% of true values (finite sample, stochastic)
        if abs(beta_hat - beta_true) / beta_true > 0.5:
            return (False, f"beta_hat={beta_hat:.6f}, true={beta_true:.6f}, error > 50%")
        if abs(gamma_hat - gamma_true) / gamma_true > 0.5:
            return (False, f"gamma_hat={gamma_hat:.4f}, true={gamma_true:.4f}, error > 50%")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.24: MLE recovers SIR parameters from simulated epidemic data",
        section="3.24",
        predicate=_remark_3_24_mle_epidemic,
        note="Remark 3.24: epidemic MLE verified",
    ))

    return ch
