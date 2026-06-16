# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 43: Fluid Dynamics — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(43, "Fluid Dynamics")

    g = 9.81

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Torricelli's law: v = sqrt(2*g*h) from Bernoulli",
        section="5",
        identity=lambda: _torricelli_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Hagen-Poiseuille: Q = pi*R^4*dP/(8*mu*L)",
        section="5",
        identity=lambda: _poiseuille_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Terminal velocity approach: v(t) = vt*(1 - exp(-t/tau))",
        section="5",
        identity=lambda: _terminal_velocity_identity(),
    ))

    # S4: Continuity equation (F4.2)
    ch.add(SymbolicCheck(
        label="F4.2: Continuity A1*v1 = A2*v2",
        section="5",
        identity=lambda: _continuity_identity(),
    ))

    # S5: Stokes drag formula (F4.6)
    ch.add(SymbolicCheck(
        label="F4.6: Stokes drag F = 6*pi*mu*r*v",
        section="5",
        identity=lambda: _stokes_drag_identity(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # --- Example 8.1: Torricelli ---
    ch.add(NumericCheck(
        label="Torricelli efflux v = sqrt(2*9.81*5) ~ 9.905 m/s",
        section="9.1",
        stated=9.905,
        computed=lambda: math.sqrt(2 * g * 5),
        tolerance=1e-3,
    ))

    # Example 8.1: Venturi v2 from continuity
    ch.add(NumericCheck(
        label="Venturi v2 = v1*A1/A2 ~ 24.76 m/s",
        section="9.1",
        stated=24.76,
        computed=lambda: math.sqrt(2 * g * 5) * 0.01 / 0.004,
        tolerance=1e-2,
    ))

    # Example 8.1: Venturi pressure P2
    # Exact: -156187.5 Pa; chapter rounds intermediates to -156175 Pa
    ch.add(NumericCheck(
        label="Venturi P2 ~ -156175 Pa (cavitation)",
        section="9.1",
        stated=-156175,
        computed=lambda: 101325 + 0.5 * 1000 * (2 * g * 5 - (math.sqrt(2 * g * 5) * 0.01 / 0.004)**2),
        tolerance=1e-2,
    ))

    # --- Example 8.2: Poiseuille flow ---
    R = 5e-4
    L = 0.02
    mu = 3.5e-3
    dP = 4000
    rho = 1060

    ch.add(NumericCheck(
        label="Poiseuille v_max = dP*R^2/(4*mu*L) ~ 3.571 m/s",
        section="9.2",
        stated=3.571,
        computed=lambda: dP * R**2 / (4 * mu * L),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Poiseuille Q = pi*R^4*dP/(8*mu*L) ~ 1.40e-6 m^3/s",
        section="9.2",
        stated=1.40e-6,
        computed=lambda: math.pi * R**4 * dP / (8 * mu * L),
        tolerance=2e-2,
    ))

    # Mean velocity = v_max / 2 = 1.786 m/s
    ch.add(NumericCheck(
        label="Poiseuille v_mean = v_max/2 ~ 1.786 m/s",
        section="9.2",
        stated=1.786,
        computed=lambda: dP * R**2 / (4 * mu * L) / 2,
        tolerance=1e-3,
    ))

    # Reynolds number
    ch.add(NumericCheck(
        label="Blood flow Re ~ 541",
        section="9.2",
        stated=541,
        computed=lambda: _blood_flow_reynolds(R, dP, mu, L, rho),
        tolerance=5e-3,
    ))

    # Flow regime classification: Re=541 < 2300 => laminar
    ch.add(StructuralCheck(
        label="Blood flow regime: Re=541 is laminar (< 2300)",
        section="9.2",
        predicate=lambda: (
            _blood_flow_reynolds(R, dP, mu, L, rho) < 2300,
            f"Re={_blood_flow_reynolds(R, dP, mu, L, rho):.0f}, laminar threshold=2300"
        ),
    ))

    # Poiseuille velocity at wall: v(R) = 0
    ch.add(NumericCheck(
        label="Poiseuille v(r=R) = 0 (no-slip)",
        section="9.2",
        stated=0.0,
        computed=lambda: dP / (4 * mu * L) * (R**2 - R**2),
        tolerance=1e-15,
    ))

    # --- Example 8.3: Terminal velocity ---
    rs = 5e-4
    rho_s = 2500
    rho_f = 1260
    mu_glyc = 1.5

    m_eff = (4/3) * math.pi * rs**3 * (rho_s - rho_f)

    ch.add(NumericCheck(
        label="Stokes effective mass m_eff ~ 6.492e-7 kg",
        section="9.3",
        stated=6.492e-7,
        computed=lambda: (4/3) * math.pi * rs**3 * (rho_s - rho_f),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Stokes terminal velocity ~ 4.506e-4 m/s",
        section="9.3",
        stated=4.506e-4,
        computed=lambda: m_eff * g / (6 * math.pi * mu_glyc * rs),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Stokes time constant ~ 4.592e-5 s",
        section="9.3",
        stated=4.592e-5,
        computed=lambda: m_eff / (6 * math.pi * mu_glyc * rs),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Stokes Re ~ 3.78e-4",
        section="9.3",
        stated=3.78e-4,
        computed=lambda: rho_f * (m_eff * g / (6 * math.pi * mu_glyc * rs)) * (2 * rs) / mu_glyc,
        tolerance=2e-2,
    ))

    # Verify Re << 1 for Stokes regime
    ch.add(StructuralCheck(
        label="Stokes regime: Re << 1",
        section="9.3",
        predicate=lambda: _stokes_regime_check(rs, rho_s, rho_f, mu_glyc, g),
    ))

    # --- Example 8.4: Diffusion eigenvalues ---
    ch.add(NumericCheck(
        label="Continuum diffusion sigma_1 = D*pi^2/L^2 ~ 9.870e-5",
        section="9.4",
        stated=9.870e-5,
        computed=lambda: 1e-5 * math.pi**2 / 1.0**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Continuum diffusion sigma_2 = D*4*pi^2/L^2 ~ 3.948e-4",
        section="9.4",
        stated=3.948e-4,
        computed=lambda: 1e-5 * 4 * math.pi**2 / 1.0**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Continuum diffusion sigma_3 = D*9*pi^2/L^2 ~ 8.883e-4",
        section="9.4",
        stated=8.883e-4,
        computed=lambda: 1e-5 * 9 * math.pi**2 / 1.0**2,
        tolerance=1e-3,
    ))

    # Discrete sigma_1 for N=20: from text ~ 9.842e-5
    ch.add(NumericCheck(
        label="Discrete sigma_1 (N=20) ~ 9.842e-5 (0.28% from exact)",
        section="9.4",
        stated=9.842e-5,
        computed=lambda: _discrete_decay_rate(1, 20, 1e-5, 1.0),
        tolerance=1e-2,
    ))

    # Grid spacing
    ch.add(NumericCheck(
        label="Grid spacing dx = 1/21 ~ 0.04762 m",
        section="9.4",
        stated=0.04762,
        computed=lambda: 1.0 / 21.0,
        tolerance=1e-3,
    ))

    # --- Example 8.5: Kolmogorov spectrum ---
    ch.add(NumericCheck(
        label="Kolmogorov spectral slope -5/3 ~ -1.667",
        section="9.5",
        stated=-1.667,
        computed=lambda: -5.0 / 3.0,
        tolerance=1e-3,
    ))

    # Amplitude exponent: |A(f)| ~ f^{-5/6}
    ch.add(NumericCheck(
        label="Kolmogorov amplitude exponent -5/6 ~ -0.833",
        section="9.5",
        stated=-0.833,
        computed=lambda: -5.0 / 6.0,
        tolerance=1e-3,
    ))

    # --- Formula gap fills ---

    # F4.1: Bernoulli P + (1/2)*rho*v^2 + rho*g*h = const
    ch.add(NumericCheck(
        label="F4.1: Bernoulli efflux v = sqrt(2*g*h) for h=5m ~ 9.905 m/s",
        section="5",
        stated=9.905,
        computed=lambda: math.sqrt(2 * g * 5),
        tolerance=1e-3,
    ))

    # F4.4: Poiseuille velocity profile v(r) = (dP/(4*mu*L))*(R^2 - r^2)
    ch.add(NumericCheck(
        label="F4.4: Poiseuille v_max = dP*R^2/(4*mu*L) ~ 3.571 m/s",
        section="5",
        stated=3.571,
        computed=lambda: 4000 * (5e-4)**2 / (4 * 3.5e-3 * 0.02),
        tolerance=1e-3,
    ))

    # F4.9: Reynolds number Re = rho*v*D/mu
    ch.add(NumericCheck(
        label="F4.9: Reynolds number for blood flow ~ 541",
        section="5",
        stated=541,
        computed=lambda: _blood_flow_reynolds(5e-4, 4000, 3.5e-3, 0.02, 1060),
        tolerance=5e-3,
    ))

    # F4.12: Peclet number Pe = v*L/D (advection vs diffusion)
    ch.add(NumericCheck(
        label="F4.12: Peclet number Pe = v*L/D for v=1, L=1, D=1e-5 = 1e5",
        section="5",
        stated=1e5,
        computed=lambda: 1.0 * 1.0 / 1e-5,
        tolerance=1e-6,
    ))

    # F4.13: Water hammer pressure rise dP = rho*c*dv
    ch.add(NumericCheck(
        label="F4.13: Water hammer dP = rho*c*dv = 1000*1483*2 = 2.966e6 Pa",
        section="5",
        stated=2.966e6,
        computed=lambda: 1000 * 1483 * 2.0,
        tolerance=1e-3,
        note="rho=1000 kg/m^3, c=1483 m/s, dv=2 m/s",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Diffusion eigenvalues: numerical match analytical formula",
        section="4",
        predicate=lambda: _diffusion_eigenvalue_check(),
    ))

    ch.add(StructuralCheck(
        label="Poiseuille integral: Simpson matches exact Q",
        section="6",
        predicate=lambda: _poiseuille_integral_check(),
    ))

    ch.add(StructuralCheck(
        label="Discrete decay rates converge to continuum as N increases",
        section="9.4",
        predicate=lambda: _decay_rate_convergence(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS
    # ===================================================================

    # ---------------------------------------------------------------
    # Exercise 10.1: Reservoir h=12m
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.1: Torricelli v = sqrt(2*9.81*12) ~ 15.34 m/s",
        section="11",
        stated=15.34,
        computed=lambda: math.sqrt(2 * g * 12),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.1: flow rate Q = 0.005 * v ~ 0.0767 m^3/s",
        section="11",
        stated=0.0767,
        computed=lambda: 0.005 * math.sqrt(2 * g * 12),
        tolerance=1e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.2: Reynolds numbers
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.2: Re water = 1000*2*0.05/0.001 = 100000",
        section="11",
        stated=100000,
        computed=lambda: 1000 * 2 * 0.05 / 1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: Re glycerin = 1260*2*0.05/1.5 ~ 84.0",
        section="11",
        stated=84.0,
        computed=lambda: 1260 * 2 * 0.05 / 1.5,
        tolerance=1e-2,
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.2: water flow is turbulent (Re=100000 > 4000)",
        section="11",
        predicate=lambda: (1000*2*0.05/1e-3 > 4000, f"Re={1000*2*0.05/1e-3}"),
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.2: glycerin flow is laminar (Re=84.0 < 2300)",
        section="11",
        predicate=lambda: (1260*2*0.05/1.5 < 2300, f"Re={1260*2*0.05/1.5:.1f}"),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.3: Horizontal pipe Poiseuille
    # ---------------------------------------------------------------
    R3 = 0.05  # diameter 0.1 m => radius 0.05 m
    L3 = 50
    mu3 = 1e-3
    dP3 = 500

    ch.add(NumericCheck(
        label="Exercise 10.3: Q = pi*R^4*dP/(8*mu*L) ~ 0.0245 m^3/s",
        section="11",
        stated=0.0245,
        computed=lambda: math.pi * R3**4 * dP3 / (8 * mu3 * L3),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: v_max = dP*R^2/(4*mu*L) ~ 6.25 m/s",
        section="11",
        stated=6.25,
        computed=lambda: dP3 * R3**2 / (4 * mu3 * L3),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: v_mean = v_max/2 ~ 3.125 m/s",
        section="11",
        stated=3.125,
        computed=lambda: dP3 * R3**2 / (4 * mu3 * L3) / 2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: Re = rho*v_mean*D/mu = 1000*3.125*0.1/0.001 = 312500",
        section="11",
        stated=312500,
        computed=lambda: 1000 * (dP3 * R3**2 / (4 * mu3 * L3) / 2) * (2 * R3) / mu3,
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.3: Poiseuille NOT valid (Re >> 2300)",
        section="11",
        predicate=lambda: (
            1000 * (dP3 * R3**2 / (4 * mu3 * L3) / 2) * (2 * R3) / mu3 > 2300,
            "Re >> 2300, Poiseuille solution invalid"
        ),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.4: Steel ball in motor oil
    # ---------------------------------------------------------------
    rs4 = 2e-3
    rho_s4 = 7800
    rho_f4 = 880
    mu4 = 0.3
    m_eff4 = (4/3) * math.pi * rs4**3 * (rho_s4 - rho_f4)

    ch.add(NumericCheck(
        label="Exercise 10.4: buoyancy-corrected mass ~ 2.317e-4 kg",
        section="11",
        stated=2.317e-4,
        computed=lambda: (4/3) * math.pi * rs4**3 * (rho_s4 - rho_f4),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.4: terminal velocity ~ 0.2009 m/s",
        section="11",
        stated=0.2009,
        computed=lambda: m_eff4 * g / (6 * math.pi * mu4 * rs4),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.4: time constant tau ~ 0.02050 s",
        section="11",
        stated=0.02050,
        computed=lambda: m_eff4 / (6 * math.pi * mu4 * rs4),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.4: 99% of v_t at t = -tau*ln(0.01) ~ 0.0944 s",
        section="11",
        stated=0.0944,
        computed=lambda: -(m_eff4 / (6 * math.pi * mu4 * rs4)) * math.log(0.01),
        tolerance=1e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.5: Diffusion with D=1e-4
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.5: exact decay rate for D=1e-4: D*pi^2 ~ 9.870e-4",
        section="11",
        stated=9.870e-4,
        computed=lambda: 1e-4 * math.pi**2,
        tolerance=1e-3,
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.5: relative error is O(1/N^2) for discrete decay",
        section="11",
        predicate=lambda: _diffusion_order_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.6: Water hammer frequencies
    # ---------------------------------------------------------------
    a_wh = 1400  # wave speed m/s
    L_wh = 100   # pipe length m

    ch.add(NumericCheck(
        label="Exercise 10.6: first natural freq f1 = a/(2*L) = 7.0 Hz",
        section="11",
        stated=7.0,
        computed=lambda: a_wh / (2 * L_wh),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.6: second natural freq f2 = a/L = 14.0 Hz",
        section="11",
        stated=14.0,
        computed=lambda: a_wh / L_wh,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.6: third natural freq f3 = 3*a/(2*L) = 21.0 Hz",
        section="11",
        stated=21.0,
        computed=lambda: 3 * a_wh / (2 * L_wh),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.7: Convection-diffusion steady-state solution
    # ---------------------------------------------------------------
    # U*dc/dx = D*d^2c/dx^2, c(0)=1, c(1)=0
    # Solution: c(x) = (exp(Pe*x) - exp(Pe)) / (1 - exp(Pe))
    for Pe_val in [1.0, 10.0, 100.0]:
        ch.add(StructuralCheck(
            label=f"Exercise 10.7: Convection-diffusion Pe={Pe_val} BC verification",
            section="11",
            predicate=(lambda pv=Pe_val: _ex437_conv_diff(pv)),
            note=f"Exercise 10.7: Pe={Pe_val}",
        ))

    # ---------------------------------------------------------------
    # Exercise 10.8: Turbulence -5/3 spectrum slope estimation
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.8: Synthetic turbulence spectrum slope ~ -5/3",
        section="11",
        predicate=lambda: _ex438_turbulence_slope(),
        note="Exercise 10.8: Kolmogorov -5/3 law",
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.8: R^4 dependence — doubling pipe radius increases flow by 16x
    ch.add(NumericCheck(
        label="Remark 3.8: Doubling pipe radius -> 16x flow rate",
        section="4",
        stated=16.0,
        computed=lambda: (2.0)**4,
        tolerance=1e-10,
        note="Remark 3.8: Q ~ R^4 (Hagen-Poiseuille)",
    ))

    # Remark 3.12: At t=3*tau, velocity reaches 95% of terminal velocity
    # v(t) = vt*(1 - exp(-t/tau)), at t=3*tau: 1 - exp(-3) ~ 0.9502
    ch.add(NumericCheck(
        label="Remark 3.12: At t=3*tau, v/vt ~ 0.950",
        section="4",
        stated=0.95,
        computed=lambda: 1 - math.exp(-3),
        tolerance=1e-2,
        note="Remark 3.12",
    ))

    # Remark 3.12: At t=5*tau, velocity within 0.7% of terminal velocity
    # 1 - exp(-5) ~ 0.99326, so within 0.674% ~ 0.7%
    ch.add(NumericCheck(
        label="Remark 3.12: At t=5*tau, v/vt ~ 0.993 (within 0.7%)",
        section="4",
        stated=1 - math.exp(-5),
        computed=lambda: 1 - math.exp(-5),
        tolerance=1e-10,
        note="Remark 3.12",
    ))

    def remark_4312_07pct():
        pct_remaining = math.exp(-5) * 100
        ok = abs(pct_remaining - 0.7) < 0.1
        return (ok, f"Remaining = {pct_remaining:.3f}%, claimed ~0.7%")
    ch.add(StructuralCheck(
        label="Remark 3.12: exp(-5)*100 ~ 0.7%",
        section="4",
        predicate=remark_4312_07pct,
        note="Remark 3.12",
    ))

    # Remark 3.21: Kolmogorov spectral slope -5/3 ~ -1.667
    ch.add(NumericCheck(
        label="Remark 3.21: -5/3 ~ -1.667",
        section="4",
        stated=-1.667,
        computed=lambda: -5/3,
        tolerance=1e-3,
        note="Remark 3.21",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Bernoulli's Equation Solver ---
    def alg_5_1_bernoulli():
        # P1 + 0.5*rho*v1^2 + rho*g*h1 = P2 + 0.5*rho*v2^2 + rho*g*h2
        rho, g = 1000.0, 9.81
        P1 = 101325.0  # Pa
        v1 = 2.0  # m/s
        h1 = 10.0  # m
        h2 = 0.0
        v2 = 5.0  # m/s
        P2 = P1 + 0.5 * rho * (v1 ** 2 - v2 ** 2) + rho * g * (h1 - h2)
        # Conservation check
        E1 = P1 + 0.5 * rho * v1 ** 2 + rho * g * h1
        E2 = P2 + 0.5 * rho * v2 ** 2 + rho * g * h2
        ok = abs(E1 - E2) < 1e-6
        return (ok, f"E1={E1:.0f}, E2={E2:.0f}, P2={P2:.0f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Bernoulli's equation (energy conservation)",
        section="6",
        predicate=alg_5_1_bernoulli,
    ))

    # --- Algorithm 5.2: Poiseuille Flow Rate ---
    def alg_5_2_poiseuille():
        # Q = pi*R^4*dP/(8*mu*L) (Hagen-Poiseuille)
        R = 0.01  # m
        dP = 1000.0  # Pa
        mu = 1e-3  # Pa.s (water)
        L = 1.0  # m
        Q = math.pi * R ** 4 * dP / (8 * mu * L)
        # Numerical integration: v(r) = dP/(4*mu*L)*(R^2 - r^2)
        Nr = 1000
        dr = R / Nr
        Q_num = 0.0
        for i in range(Nr):
            r = (i + 0.5) * dr
            v = dP / (4 * mu * L) * (R ** 2 - r ** 2)
            Q_num += v * 2 * math.pi * r * dr
        ok = abs(Q - Q_num) / Q < 1e-3
        return (ok, f"Q_analytical={Q:.6e}, Q_numerical={Q_num:.6e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Poiseuille flow rate (analytical vs numerical)",
        section="6",
        predicate=alg_5_2_poiseuille,
    ))

    # --- Algorithm 5.3: Terminal Velocity via RK4 ---
    def alg_5_3_terminal_velocity():
        m, g_tv = 1.0, 9.81
        b_drag = 0.5  # drag coefficient
        v_terminal = m * g_tv / b_drag
        v = 0.0
        h_tv = 0.01
        for _ in range(int(20 / h_tv)):
            def f_v(vv):
                return g_tv - b_drag * vv / m
            k1 = h_tv * f_v(v)
            k2 = h_tv * f_v(v + k1 / 2)
            k3 = h_tv * f_v(v + k2 / 2)
            k4 = h_tv * f_v(v + k3)
            v = v + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        ok = abs(v - v_terminal) / v_terminal < 0.01
        return (ok, f"v_final={v:.4f}, v_terminal={v_terminal:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Terminal velocity via RK4",
        section="6",
        predicate=alg_5_3_terminal_velocity,
    ))

    # --- Algorithm 5.4: Diffusion Eigenvalue Computation ---
    def alg_5_4_diffusion_eigenvalues():
        # 1D diffusion: d^2u/dx^2 with Dirichlet BCs
        # Eigenvalues: lambda_k = -(k*pi/L)^2 * D
        D = 1.0
        L = 1.0
        N = 20
        dx = L / (N + 1)
        # Tridiagonal matrix
        A = np.zeros((N, N))
        for i in range(N):
            A[i, i] = -2 * D / dx ** 2
            if i > 0:
                A[i, i - 1] = D / dx ** 2
            if i < N - 1:
                A[i, i + 1] = D / dx ** 2
        eigs = np.sort(np.linalg.eigvals(A))
        # First eigenvalue should be ~ -(pi/L)^2 * D
        lam1_analytical = -(math.pi / L) ** 2 * D
        ok = abs(eigs[-1] - lam1_analytical) / abs(lam1_analytical) < 0.05
        return (ok, f"lambda_1={eigs[-1]:.4f}, analytical={lam1_analytical:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Diffusion eigenvalue computation",
        section="6",
        predicate=alg_5_4_diffusion_eigenvalues,
    ))

    # --- Algorithm 5.5: Kolmogorov Spectral Slope ---
    def alg_5_5_kolmogorov_slope():
        # Generate synthetic turbulent velocity with -5/3 spectrum
        np.random.seed(42)
        N_k = 1024
        freqs = np.arange(1, N_k // 2 + 1)
        # Power law spectrum: P(k) ~ k^{-5/3}
        amplitudes = freqs.astype(float) ** (-5 / 6)  # amplitude ~ k^{-5/6}, PSD ~ k^{-5/3}
        phases = np.random.uniform(0, 2 * math.pi, len(freqs))
        # Create signal
        t = np.arange(N_k) / N_k
        signal = np.zeros(N_k)
        for i, (a, phi, f) in enumerate(zip(amplitudes, phases, freqs)):
            signal += a * np.sin(2 * math.pi * f * t + phi)
        # Compute PSD
        X = np.fft.fft(signal)
        PSD = np.abs(X[:N_k // 2]) ** 2
        # Fit log-log slope in inertial range (f=10..100)
        f_range = slice(10, 100)
        log_f = np.log(np.arange(10, 100))
        log_P = np.log(PSD[10:100])
        slope = np.polyfit(log_f, log_P, 1)[0]
        ok = abs(slope - (-5 / 3)) < 0.3
        return (ok, f"Spectral slope={slope:.3f}, expected=-1.667")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Kolmogorov spectral slope estimation",
        section="6",
        predicate=alg_5_5_kolmogorov_slope,
    ))

    # --- Remark 3.4: Continuity equation A1*v1 = A2*v2 ---
    def _remark_43_4_continuity():
        """Verify continuity equation: volumetric flow rate Q = Av is constant."""
        # Pipe narrows from A1 to A2: v2 = v1 * A1/A2
        A1, v1 = 0.1, 2.0   # m^2, m/s
        A2 = 0.02            # narrower section
        Q = A1 * v1          # volumetric flow rate
        v2 = Q / A2
        v2_expected = v1 * A1 / A2
        if abs(v2 - v2_expected) > 1e-10:
            return (False, f"v2={v2}, expected={v2_expected}")
        # Q should be conserved
        Q2 = A2 * v2
        if abs(Q - Q2) > 1e-10:
            return (False, f"Q1={Q}, Q2={Q2}")
        # Multiple sections
        for A in [0.05, 0.01, 0.2]:
            v = Q / A
            if abs(A * v - Q) > 1e-10:
                return (False, f"A={A}: Av={A*v}, Q={Q}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: Continuity equation A1*v1 = A2*v2 (Q conserved)",
        section="43.4",
        predicate=_remark_43_4_continuity,
        note="Remark 3.4: continuity equation for incompressible flow",
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _ex437_conv_diff(Pe):
    """Exercise 10.7: Verify convection-diffusion analytical solution."""
    # c(x) = (exp(Pe*x) - exp(Pe)) / (1 - exp(Pe))
    # BCs: c(0) = (1-exp(Pe))/(1-exp(Pe)) = 1, c(1) = (exp(Pe)-exp(Pe))/(1-exp(Pe)) = 0
    c0 = (math.exp(Pe * 0) - math.exp(Pe)) / (1 - math.exp(Pe))
    c1 = (math.exp(Pe * 1) - math.exp(Pe)) / (1 - math.exp(Pe))
    bc_ok = abs(c0 - 1.0) < 1e-10 and abs(c1) < 1e-10
    if not bc_ok:
        return (False, f"BCs fail: c(0)={c0:.6f}, c(1)={c1:.6f}")
    # Verify ODE: U*dc/dx = D*d^2c/dx^2 where Pe = U*L/D = U/D (L=1)
    # dc/dx = Pe*exp(Pe*x) / (1-exp(Pe))
    # d^2c/dx^2 = Pe^2*exp(Pe*x) / (1-exp(Pe))
    # U*dc/dx = U * Pe*exp(Pe*x)/(1-exp(Pe)) = Pe^2*D*exp(Pe*x)/(1-exp(Pe)) = D*d^2c/dx^2 ✓
    # (since U = Pe*D) — verify numerically at x=0.5
    x_test = 0.5
    dc = Pe * math.exp(Pe * x_test) / (1 - math.exp(Pe))
    d2c = Pe**2 * math.exp(Pe * x_test) / (1 - math.exp(Pe))
    # ODE: Pe * dc = d2c (since U/D = Pe, U*dc/dx = Pe*D*dc/dx, D*d2c/dx^2)
    # Actually: U*dc/dx = D*d^2c/dx^2 => (Pe*D)*dc/dx = D*d^2c/dx^2 => Pe*dc/dx = d^2c/dx^2
    ode_residual = abs(Pe * dc - d2c)
    ode_ok = ode_residual < 1e-8
    return (ode_ok, f"Pe={Pe}: ODE residual={ode_residual:.2e}")


def _ex438_turbulence_slope():
    """Exercise 10.8: Generate -5/3 spectrum and estimate slope."""
    rng = np.random.default_rng(42)
    N = 8192
    fs = 2000
    freqs = np.fft.rfftfreq(N, d=1/fs)
    # Generate spectrum with -5/3 slope in inertial subrange (10-500 Hz)
    spectrum = np.ones(len(freqs))
    for i, f in enumerate(freqs):
        if 10 <= f <= 500:
            spectrum[i] = f**(-5/3)
        elif f > 500:
            spectrum[i] = 500**(-5/3) * 0.01  # noise floor
    # Generate random phases
    phases = rng.uniform(0, 2*np.pi, len(freqs))
    X = np.sqrt(spectrum * N) * np.exp(1j * phases)
    X[0] = 0  # zero mean
    x = np.fft.irfft(X, n=N)
    # Compute PSD
    P = np.abs(np.fft.rfft(x))**2 / N
    # Estimate slope in inertial subrange
    mask = (freqs >= 10) & (freqs <= 500)
    log_f = np.log10(freqs[mask])
    log_P = np.log10(P[mask] + 1e-30)
    slope = np.polyfit(log_f, log_P, 1)[0]
    expected = -5/3
    ok = abs(slope - expected) < 0.3
    return (ok, f"Estimated slope={slope:.3f}, expected={expected:.3f}")


def _torricelli_identity():
    import sympy
    g, h = sympy.symbols('g h', positive=True)
    v = sympy.sqrt(2 * g * h)
    return sympy.Eq(v**2, 2 * g * h)


def _poiseuille_identity():
    import sympy
    R, dP, mu, L = sympy.symbols('R dP mu L', positive=True)
    r = sympy.Symbol('r', positive=True)
    v_r = (dP / (4 * mu * L)) * (R**2 - r**2)
    Q = sympy.integrate(2 * sympy.pi * r * v_r, (r, 0, R))
    Q_expected = sympy.pi * R**4 * dP / (8 * mu * L)
    return sympy.Eq(sympy.simplify(Q - Q_expected), 0)


def _terminal_velocity_identity():
    import sympy
    m, mu, rs, g_s, t = sympy.symbols('m mu rs g t', positive=True)
    alpha = 6 * sympy.pi * mu * rs / m
    vt = m * g_s / (6 * sympy.pi * mu * rs)
    v_t_fn = vt * (1 - sympy.exp(-alpha * t))
    dvdt = sympy.diff(v_t_fn, t)
    residual = dvdt + alpha * v_t_fn - g_s
    return sympy.Eq(sympy.simplify(residual), 0)


def _continuity_identity():
    import sympy
    A1, A2, v1 = sympy.symbols('A1 A2 v1', positive=True)
    v2 = v1 * A1 / A2
    return sympy.Eq(sympy.simplify(A1 * v1 - A2 * v2), 0)


def _stokes_drag_identity():
    import sympy
    mu, rs, v = sympy.symbols('mu rs v', positive=True)
    F_d = 6 * sympy.pi * mu * rs * v
    m, g_s = sympy.symbols('m g', positive=True)
    v_t = m * g_s / (6 * sympy.pi * mu * rs)
    F_at_terminal = F_d.subs(v, v_t)
    return sympy.Eq(sympy.simplify(F_at_terminal - m * g_s), 0)


def _blood_flow_reynolds(R, dP, mu, L, rho):
    Q = math.pi * R**4 * dP / (8 * mu * L)
    v_mean = Q / (math.pi * R**2)
    d = 2 * R
    return rho * v_mean * d / mu


def _stokes_regime_check(rs, rho_s, rho_f, mu_glyc, g):
    m_eff = (4/3) * math.pi * rs**3 * (rho_s - rho_f)
    vt = m_eff * g / (6 * math.pi * mu_glyc * rs)
    Re = rho_f * vt * (2 * rs) / mu_glyc
    ok = Re < 0.1
    return ok, f"Re = {Re:.2e}, Stokes regime requires Re << 1 (< 0.1)"


def _discrete_decay_rate(k, N, D, L_domain):
    dx = L_domain / (N + 1)
    lam = 4 * math.sin(k * math.pi / (2 * (N + 1)))**2
    return D / dx**2 * lam


def _diffusion_eigenvalue_check():
    N = 20
    D_coeff = 1e-5
    L_domain = 1.0
    dx = L_domain / (N + 1)
    # Build tridiagonal
    A = np.zeros((N, N))
    for i in range(N):
        A[i, i] = -2
        if i > 0:
            A[i, i-1] = 1
        if i < N - 1:
            A[i, i+1] = 1
    eigs_num = np.sort(np.linalg.eigvals(A))
    # Analytical eigenvalues
    eigs_anal = np.array([-4 * math.sin(k * math.pi / (2 * (N + 1)))**2
                          for k in range(1, N + 1)])
    eigs_anal.sort()
    max_err = np.max(np.abs(eigs_num - eigs_anal))
    ok = max_err < 1e-10
    return ok, f"Max eigenvalue error: {max_err:.2e}"


def _poiseuille_integral_check():
    """Simpson's rule on Poiseuille integrand should match exact Q."""
    R_val = 5e-4
    dP_val = 4000
    mu_val = 3.5e-3
    L_val = 0.02
    Q_exact = math.pi * R_val**4 * dP_val / (8 * mu_val * L_val)
    n = 2
    dr = R_val / n
    r_pts = [i * dr for i in range(n + 1)]
    def integrand(r):
        return 2 * math.pi * r * (dP_val / (4 * mu_val * L_val)) * (R_val**2 - r**2)
    Q_simp = (dr / 3) * (integrand(r_pts[0]) + 4 * integrand(r_pts[1]) + integrand(r_pts[2]))
    rel_err = abs(Q_simp - Q_exact) / Q_exact
    ok = rel_err < 1e-12
    return ok, f"Simpson Q = {Q_simp:.6e}, exact = {Q_exact:.6e}, rel err = {rel_err:.2e}"


def _decay_rate_convergence():
    """Verify that discrete sigma_1 converges to continuum as N increases."""
    D = 1e-5
    L_domain = 1.0
    sigma_exact = D * math.pi**2 / L_domain**2
    errors = []
    for N in [10, 20, 50, 100]:
        sigma_disc = _discrete_decay_rate(1, N, D, L_domain)
        rel_err = abs(sigma_disc - sigma_exact) / sigma_exact
        errors.append((N, rel_err))
    decreasing = all(errors[i][1] > errors[i+1][1] for i in range(len(errors)-1))
    ok = decreasing and errors[-1][1] < 0.001
    msg = ", ".join(f"N={N}: {e:.4e}" for N, e in errors)
    return ok, f"Rel errors: {msg}"


def _diffusion_order_check():
    """Exercise 10.5: Verify O(1/N^2) convergence for discrete decay rate."""
    D = 1e-4
    L_domain = 1.0
    sigma_exact = D * math.pi**2 / L_domain**2
    errors = []
    for N in [10, 50, 200]:
        sigma_disc = _discrete_decay_rate(1, N, D, L_domain)
        rel_err = abs(sigma_disc - sigma_exact) / sigma_exact
        errors.append((N, rel_err))
    # Check that error * N^2 is approximately constant (O(1/N^2))
    scaled = [e * N**2 for N, e in errors]
    # The ratio of successive scaled errors should be roughly 1
    ratio1 = scaled[1] / scaled[0]
    ratio2 = scaled[2] / scaled[1]
    ok = abs(ratio1 - 1.0) < 0.2 and abs(ratio2 - 1.0) < 0.2
    return ok, f"Scaled errors (err*N^2): {[f'{s:.4f}' for s in scaled]}, ratios: {ratio1:.3f}, {ratio2:.3f}"
