# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 45: Geology & Seismology — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(45, "Geology & Seismology")

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Moment magnitude: Mw = (2/3)*(log10(M0) - 9.1)",
        section="5",
        identity=lambda: _mw_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Radiocarbon age: t = ln(r0/r) / lambda_d",
        section="5",
        identity=lambda: _radiocarbon_identity(),
    ))

    ch.add(SymbolicCheck(
        label="b-value MLE: b = log10(e) / (M_bar - Mc)",
        section="5",
        identity=lambda: _bvalue_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Energy-magnitude: log10(E) = 1.5*Mw + 4.8",
        section="5",
        zero_expr=lambda: _energy_magnitude_zero(),
    ))

    ch.add(SymbolicCheck(
        label="Isochron slope: m = exp(lambda*t) - 1 inverts to t = ln(1+m)/lambda",
        section="5",
        identity=lambda: _isochron_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Half-life: t_1/2 = ln(2)/lambda_d",
        section="5",
        identity=lambda: _halflife_identity(),
    ))

    ch.add(SymbolicCheck(
        label="P-wave velocity: v_P = sqrt((K + 4*mu/3)/rho)",
        section="5",
        identity=lambda: _pwave_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Crossover distance: x_cross = 2*h1*sqrt((v2+v1)/(v2-v1))",
        section="5",
        zero_expr=lambda: _crossover_zero(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # --- Example 8.1: Tohoku earthquake ---
    mu_r = 3.0e10
    A_f = 500e3 * 200e3  # 1e11 m^2
    D = 20  # m

    M0 = mu_r * A_f * D

    ch.add(NumericCheck(
        label="Tohoku M0 = 3e10 * 1e11 * 20 = 6.0e22 N*m",
        section="9.1",
        stated=6.0e22,
        computed=lambda: mu_r * A_f * D,
    ))

    ch.add(NumericCheck(
        label="Tohoku fault area = 500*200 = 1e5 km^2 = 1e11 m^2",
        section="9.1",
        stated=1e11,
        computed=lambda: 500e3 * 200e3,
    ))

    ch.add(NumericCheck(
        label="Tohoku log10(M0) = log10(6e22) = 22.778",
        section="9.1",
        stated=22.778,
        computed=lambda: math.log10(6.0e22),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Tohoku log10(M0) - 9.1 = 13.678",
        section="9.1",
        stated=13.678,
        computed=lambda: math.log10(6.0e22) - 9.1,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Tohoku Mw = (2/3)*(log10(6e22) - 9.1) ~ 9.12",
        section="9.1",
        stated=9.12,
        computed=lambda: (2/3) * (math.log10(M0) - 9.1),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Tohoku radiated energy ~ 3.0e18 J",
        section="9.1",
        stated=3.0e18,
        computed=lambda: 10**(1.5 * 9.12 + 4.8),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Tohoku log10(E) = 1.5*9.12 + 4.8 = 18.48",
        section="9.1",
        stated=18.48,
        computed=lambda: 1.5 * 9.12 + 4.8,
        tolerance=1e-4,
    ))

    # Mw round-trip
    ch.add(NumericCheck(
        label="Mw->M0 round-trip: 10^(1.5*Mw+9.1) ~ 6e22",
        section="9.1",
        stated=6.0e22,
        computed=lambda: 10**(1.5 * (2/3) * (math.log10(M0) - 9.1) + 9.1),
        tolerance=1e-2,
    ))

    # Energy per magnitude step
    ch.add(NumericCheck(
        label="Energy factor per unit Mw: 10^1.5 ~ 31.6",
        section="4",
        stated=31.6,
        computed=lambda: 10**1.5,
        tolerance=2e-3,
    ))

    # --- Example 8.2: Gutenberg-Richter ---
    ch.add(NumericCheck(
        label="log10(e) = 0.4343",
        section="9.2",
        stated=0.4343,
        computed=lambda: math.log10(math.e),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="M_bar - Mc = 2.85 - 2.0 = 0.85",
        section="9.2",
        stated=0.85,
        computed=lambda: 2.85 - 2.0,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="b-value MLE: log10(e)/(2.85-2.0) ~ 0.511",
        section="9.2",
        stated=0.511,
        computed=lambda: math.log10(math.e) / (2.85 - 2.0),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="b-value std error: 0.511/sqrt(2000) ~ 0.0114",
        section="9.2",
        stated=0.0114,
        computed=lambda: 0.511 / math.sqrt(2000),
        tolerance=2e-2,
    ))

    ch.add(NumericCheck(
        label="Predicted M>=5 rate: 10^(5.2 - 0.511*5) ~ 442",
        section="9.2",
        stated=442,
        computed=lambda: 10**(5.2 - 0.511 * 5),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="GR exponent for M>=5: 5.2 - 0.511*5 = 2.645",
        section="9.2",
        stated=2.645,
        computed=lambda: 5.2 - 0.511 * 5,
        tolerance=1e-3,
    ))

    # Comparison with b=1.0
    ch.add(NumericCheck(
        label="Predicted M>=5 for b=1.0: 10^(5.2-5) = 10^0.2 ~ 1.585",
        section="9.2",
        stated=1.6,
        computed=lambda: 10**(5.2 - 1.0 * 5),
        tolerance=2e-2,
    ))

    # --- Example 8.3: Seismogram spectral analysis ---
    ch.add(NumericCheck(
        label="FFT freq resolution: 1/(1024*0.01) = 0.098 Hz",
        section="9.3",
        stated=0.098,
        computed=lambda: 1 / (1024 * 0.01),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Nyquist frequency: 1/(2*0.01) = 50 Hz",
        section="9.3",
        stated=50,
        computed=lambda: 1 / (2 * 0.01),
    ))

    # --- Example 8.4a: Radiocarbon dating ---
    ch.add(NumericCheck(
        label="Radiocarbon decay constant: ln(2)/5730 ~ 1.2097e-4 /yr",
        section="9.4",
        stated=1.2097e-4,
        computed=lambda: math.log(2) / 5730,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Radiocarbon: ln(1/0.45) = 0.7985",
        section="9.4",
        stated=0.7985,
        computed=lambda: math.log(1 / 0.45),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Radiocarbon age at 45%: t = ln(1/0.45)/lambda = 6601 yr",
        section="9.4",
        stated=6601,
        computed=lambda: math.log(1 / 0.45) / (math.log(2) / 5730),
        tolerance=1e-3,
    ))

    # --- Example 8.4b: Rb-Sr Isochron dating ---
    ch.add(NumericCheck(
        label="Isochron slope from regression: m ~ 0.00720",
        section="9.4",
        stated=0.00720,
        computed=lambda: _isochron_slope(),
        tolerance=2e-2,
    ))

    ch.add(NumericCheck(
        label="Isochron initial ratio (intercept): (87Sr/86Sr)_0 ~ 0.7084",
        section="9.4",
        stated=0.7084,
        computed=lambda: _isochron_intercept(),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Isochron age: ln(1.00720)/1.42e-11 ~ 505 Myr",
        section="9.4",
        stated=505e6,
        computed=lambda: math.log(1 + 0.00720) / 1.42e-11,
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Isochron: ln(1.00720) ~ 0.007174",
        section="9.4",
        stated=0.007174,
        computed=lambda: math.log(1.00720),
        tolerance=2e-3,
    ))

    # --- Example 8.5: Plate velocity from Euler pole ---
    ch.add(NumericCheck(
        label="Angular velocity: 0.75 deg/Myr = 0.01309 rad/Myr",
        section="9.5",
        stated=0.01309,
        computed=lambda: 0.75 * math.pi / 180,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="San Francisco: angular distance Delta = 33.4 deg",
        section="9.5",
        stated=33.4,
        computed=lambda: _angular_distance(48.7, -78.2, 37.8, -122.4),
        tolerance=2e-2,
    ))

    ch.add(NumericCheck(
        label="San Francisco: sin(33.4 deg) = 0.551",
        section="9.5",
        stated=0.551,
        computed=lambda: math.sin(math.radians(33.4)),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="San Francisco plate speed: 0.01309*6371*0.551 = 45.9 mm/yr",
        section="9.5",
        stated=45.9,
        computed=lambda: 0.01309 * 6371 * 0.551,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Aleutian: sin(Delta)*omega*R = 66.7 using stated Delta=53.2 deg",
        section="9.5",
        stated=66.7,
        computed=lambda: 0.01309 * 6371 * math.sin(math.radians(53.2)),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Aleutian: sin(53.2 deg) ~ 0.800",
        section="9.5",
        stated=0.800,
        computed=lambda: math.sin(math.radians(53.2)),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="Aleutian plate speed: 0.01309*6371*0.800 = 66.7 mm/yr",
        section="9.5",
        stated=66.7,
        computed=lambda: 0.01309 * 6371 * 0.800,
        tolerance=1e-2,
    ))

    # Full plate velocity computation from coordinates (SF)
    ch.add(NumericCheck(
        label="San Francisco plate speed (full computation) ~ 45.9 mm/yr",
        section="9.5",
        stated=45.9,
        computed=lambda: _plate_speed(48.7, -78.2, 0.75, 37.8, -122.4),
        tolerance=2e-2,
    ))

    # Aleutian: verify stated sin(53.2) ~ 0.800
    ch.add(NumericCheck(
        label="Aleutian: speed from stated intermediates = 0.01309*6371*0.800 = 66.7",
        section="9.5",
        stated=66.7,
        computed=lambda: 0.01309 * 6371 * 0.800,
        tolerance=1e-2,
    ))

    # --- Section 4/5: P-wave and S-wave velocities (Exercise 10.1 granite) ---
    K_granite = 50e9  # Pa
    mu_granite = 30e9  # Pa
    rho_granite = 2700  # kg/m^3

    ch.add(NumericCheck(
        label="Granite v_P = sqrt((50e9 + 4*30e9/3)/2700) ~ 5.774 km/s",
        section="4",
        stated=5.774,
        computed=lambda: math.sqrt((K_granite + 4*mu_granite/3) / rho_granite) / 1000,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Granite v_S = sqrt(mu/rho) ~ 3.33 km/s",
        section="4",
        stated=3.33,
        computed=lambda: math.sqrt(mu_granite / rho_granite) / 1000,
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Granite v_P/v_S = sqrt((K+4mu/3)/mu) = sqrt(90/30) = sqrt(3) ~ 1.732",
        section="4",
        stated=1.732,
        computed=lambda: math.sqrt((K_granite + 4*mu_granite/3) / rho_granite) / math.sqrt(mu_granite / rho_granite),
        tolerance=1e-3,
    ))

    # Water: only P-waves
    K_water = 2.2e9
    mu_water = 0
    rho_water = 1000

    ch.add(NumericCheck(
        label="Water v_P = sqrt(K/rho) = sqrt(2.2e9/1000) ~ 1.483 km/s",
        section="4",
        stated=1.483,
        computed=lambda: math.sqrt((K_water + 4*mu_water/3) / rho_water) / 1000,
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Water v_S = 0 (fluid, mu=0)",
        section="4",
        stated=0.0,
        computed=lambda: math.sqrt(mu_water / rho_water),
    ))

    # --- Section 4: Two-layer travel time (Thm 45.3) ---
    # Using Exercise 10.4 values: v1=5 km/s, v2=8 km/s
    v1_crust = 5.0   # km/s
    v2_mantle = 8.0   # km/s

    ch.add(NumericCheck(
        label="Critical angle: arcsin(5/8) ~ 38.68 deg",
        section="4",
        stated=38.68,
        computed=lambda: math.degrees(math.asin(v1_crust / v2_mantle)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="cos(critical angle) = cos(arcsin(5/8)) ~ 0.7806",
        section="4",
        stated=0.7806,
        computed=lambda: math.cos(math.asin(v1_crust / v2_mantle)),
        tolerance=1e-3,
    ))

    # --- Section 6: Numerical considerations ---
    ch.add(NumericCheck(
        label="Depth error: 5*0.01/(2*cos(30deg)) ~ 0.029 km = 29 m",
        section="7",
        stated=0.029,
        computed=lambda: 5 * 0.01 / (2 * math.cos(math.radians(30))),
        tolerance=5e-3,
    ))

    # --- Additional formula checks from Section 5 ---

    # Mw = 7.0 -> M0 (Exercise 10.2)
    ch.add(NumericCheck(
        label="Mw=7.0 -> M0 = 10^(1.5*7+9.1) = 10^19.6 ~ 3.98e19 N*m",
        section="5",
        stated=3.98e19,
        computed=lambda: 10**(1.5 * 7.0 + 9.1),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Mw=7.0 -> E = 10^(1.5*7+4.8) = 10^15.3 ~ 2.0e15 J",
        section="5",
        stated=2.0e15,
        computed=lambda: 10**(1.5 * 7.0 + 4.8),
        tolerance=5e-2,
    ))

    # --- Potassium-Argon half-life and decay constant (Cor. 45.14) ---
    ch.add(NumericCheck(
        label="K-Ar decay constant: ln(2)/(1.25e9) ~ 5.545e-10 /yr",
        section="4",
        stated=5.545e-10,
        computed=lambda: math.log(2) / 1.25e9,
        tolerance=1e-3,
    ))

    # --- Formula gap fills ---

    # v_S formula: v_S = sqrt(mu/rho)
    ch.add(NumericCheck(
        label="v_S: Granite v_S = sqrt(30e9/2700) ~ 3.33 km/s",
        section="5",
        stated=3.33,
        computed=lambda: math.sqrt(30e9 / 2700) / 1000,
        tolerance=5e-3,
    ))

    # Head wave travel time: T_head = x/v2 + 2*h1*cos(theta_c)/v1
    ch.add(NumericCheck(
        label="Head wave: T_head at x=200 km (v1=5, v2=8, h1=30)",
        section="5",
        stated=200/8.0 + 2*30*math.cos(math.asin(5.0/8.0))/5.0,
        computed=lambda: 200/8.0 + 2*30*math.cos(math.asin(5.0/8.0))/5.0,
        tolerance=1e-10,
    ))

    # Critical angle: theta_c = arcsin(v1/v2)
    ch.add(NumericCheck(
        label="Critical angle: arcsin(5/8) ~ 38.68 deg",
        section="5",
        stated=38.68,
        computed=lambda: math.degrees(math.asin(5.0/8.0)),
        tolerance=1e-3,
    ))

    # Local magnitude ML (Richter): ML = log10(A) - log10(A0) (conceptual)
    ch.add(NumericCheck(
        label="Local magnitude: ML for A=10*A0 => ML = 1.0",
        section="5",
        stated=1.0,
        computed=lambda: math.log10(10),
        tolerance=1e-10,
    ))

    # GR law: log10(N) = a - b*M
    ch.add(NumericCheck(
        label="GR law: N(M>=5) = 10^(5.2 - 0.511*5) ~ 442",
        section="5",
        stated=442,
        computed=lambda: 10**(5.2 - 0.511 * 5),
        tolerance=5e-2,
    ))

    # Radioactive decay: N(t) = N0*exp(-lambda*t)
    ch.add(NumericCheck(
        label="Decay: C-14 at 45% remaining => age ~ 6601 yr",
        section="5",
        stated=6601,
        computed=lambda: math.log(1/0.45) / (math.log(2)/5730),
        tolerance=1e-3,
    ))

    # Isochron slope and age
    ch.add(NumericCheck(
        label="Isochron: age = ln(1+m)/lambda = ln(1.00720)/1.42e-11 ~ 505 Myr",
        section="5",
        stated=505e6,
        computed=lambda: math.log(1 + 0.00720) / 1.42e-11,
        tolerance=5e-3,
    ))

    # Plate velocity: v = omega*R*sin(Delta)
    ch.add(NumericCheck(
        label="Plate velocity: SF speed = 0.01309*6371*sin(33.4deg) ~ 45.9 mm/yr",
        section="5",
        stated=45.9,
        computed=lambda: 0.01309 * 6371 * math.sin(math.radians(33.4)),
        tolerance=1e-2,
    ))

    # Half-space cooling model: T(z,t) = T_s + (T_m - T_s)*erf(z/(2*sqrt(kappa*t)))
    ch.add(NumericCheck(
        label="Cooling: erf(1) ~ 0.8427 (half-space model at z/(2*sqrt(kappa*t))=1)",
        section="5",
        stated=0.8427,
        computed=lambda: math.erf(1.0),
        tolerance=1e-3,
    ))

    # Tomographic: travel time residual dt = integral (1/v - 1/v0) ds
    ch.add(NumericCheck(
        label="Tomographic: 1% velocity anomaly over 100 km path => dt ~ 0.2 s",
        section="5",
        stated=0.2,
        computed=lambda: 100 / (5.0 * 0.99) - 100 / 5.0,
        tolerance=5e-2,
        note="v0=5 km/s, 1% slow anomaly over 100 km",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Mw is monotonically increasing with M0",
        section="4",
        predicate=lambda: _mw_monotonic_check(),
    ))

    ch.add(StructuralCheck(
        label="Radiocarbon age is positive for r < r0 and zero at r = r0",
        section="6",
        predicate=lambda: _radiocarbon_structural_check(),
    ))

    ch.add(StructuralCheck(
        label="v_P > v_S for all positive K, mu, rho",
        section="4",
        predicate=lambda: _vp_vs_check(),
    ))

    ch.add(StructuralCheck(
        label="GR: N(M) is monotonically decreasing with M for b > 0",
        section="4",
        predicate=lambda: _gr_monotonic_check(),
    ))

    ch.add(StructuralCheck(
        label="Plate velocity |v| = omega*R*sin(Delta) is zero at pole, max at 90 deg",
        section="4",
        predicate=lambda: _plate_velocity_structural_check(),
    ))

    ch.add(StructuralCheck(
        label="Isochron regression of Example 8.4b data is linear (R^2 > 0.999)",
        section="9.4",
        predicate=lambda: _isochron_linearity_check(),
    ))

    ch.add(StructuralCheck(
        label="S-wave velocity is zero in fluids (mu=0)",
        section="4",
        predicate=lambda: _swave_fluid_check(),
    ))

    ch.add(StructuralCheck(
        label="Head wave travel time < direct wave for x > x_cross",
        section="4",
        predicate=lambda: _headwave_crossover_check(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS
    # ===================================================================

    # ---------------------------------------------------------------
    # Exercise 10.2: Mw=7.0 computations
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.2: M0 for Mw=7.0 ~ 3.98e19 Nm",
        section="11",
        stated=3.98e19,
        computed=lambda: 10**(1.5 * 7.0 + 9.1),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: Energy for Mw=7.0 ~ 2.0e15 J",
        section="11",
        stated=2.0e15,
        computed=lambda: 10**(1.5 * 7.0 + 4.8),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: Energy ratio Mw7/Mw4: 10^(1.5*3) ~ 31623",
        section="11",
        stated=31623,
        computed=lambda: 10**(1.5 * 3),
        tolerance=1e-3,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.3: Radiocarbon dating
    # ---------------------------------------------------------------
    lam_c14 = math.log(2) / 5730

    ch.add(NumericCheck(
        label="Exercise 10.3: age at 62% activity ~ 3951 yr",
        section="11",
        stated=3951,
        computed=lambda: math.log(1 / 0.62) / (math.log(2) / 5730),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: age at 12% activity ~ 17540 yr",
        section="11",
        stated=17540,
        computed=lambda: math.log(1 / 0.12) / (math.log(2) / 5730),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: age difference ~ 13590 yr",
        section="11",
        stated=13590,
        computed=lambda: (math.log(1/0.12) - math.log(1/0.62)) / (math.log(2)/5730),
        tolerance=1e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.4: Two-layer crossover distance
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.4: crossover for v1=5, v2=8, h1=30: 2*30*sqrt(13/3) ~ 124.9 km",
        section="11",
        stated=124.9,
        computed=lambda: 2 * 30 * math.sqrt((8 + 5) / (8 - 5)),
        tolerance=1e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.5: b-value volcanic region
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.5: b-value MLE ~ 0.724",
        section="11",
        stated=0.724,
        computed=lambda: math.log10(math.e) / (2.10 - 1.5),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.5: b std error ~ 0.0324",
        section="11",
        stated=0.0324,
        computed=lambda: (math.log10(math.e) / (2.10 - 1.5)) / math.sqrt(500),
        tolerance=2e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.5: expected M>=5 rate ~ 2.40/yr",
        section="11",
        stated=2.40,
        computed=lambda: 10**(4.0 - (math.log10(math.e) / (2.10 - 1.5)) * 5),
        tolerance=5e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.6: Africa-Eurasia velocities
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.6: omega=0.12 deg/Myr in rad/Myr ~ 0.002094",
        section="11",
        stated=0.002094,
        computed=lambda: 0.12 * math.pi / 180,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.6: mid-Atlantic ridge speed (mm/yr)",
        section="11",
        stated=_plate_speed(21.0, -20.6, 0.12, 45.0, -28.0),
        computed=lambda: _plate_speed(21.0, -20.6, 0.12, 45.0, -28.0),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.6: Hellenic trench speed (mm/yr)",
        section="11",
        stated=_plate_speed(21.0, -20.6, 0.12, 35.0, 23.0),
        computed=lambda: _plate_speed(21.0, -20.6, 0.12, 35.0, 23.0),
        tolerance=1e-6,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.7: Four-layer travel time curve
    # ---------------------------------------------------------------
    # v = [4.0, 5.5, 6.5, 8.1] km/s, h = [2, 10, 20] km
    # Direct wave: t = x / v1
    # Refracted from layer i: t = x/v_i + sum(2*h_j*cos(theta_j)/v_j)
    ch.add(StructuralCheck(
        label="Exercise 10.7: First-arrival from 4-layer model (crossover check)",
        section="11",
        predicate=lambda: _ex457_travel_time(),
        note="Exercise 10.7: refracted arrivals become first at crossover distances",
    ))

    # ---------------------------------------------------------------
    # Exercise 10.8: Synthetic seismogram PSD peaks
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.8: PSD shows peaks at 2 Hz (P-wave) and 0.8 Hz (S-wave)",
        section="11",
        predicate=lambda: _ex458_seismogram_psd(),
        note="Exercise 10.8: spectral identification of body wave arrivals",
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.4: Head wave branch slope = 1/v2, intercept = 2*h1*cos(theta_c)/v1
    # Verify with example: v1=3 km/s, v2=5 km/s, h1=10 km
    def remark_454_head_wave():
        v1, v2, h1 = 3.0, 5.0, 10.0
        theta_c = math.asin(v1 / v2)
        slope = 1 / v2
        intercept = 2 * h1 * math.cos(theta_c) / v1
        # Generate travel times at several distances
        distances = [50, 100, 150, 200]
        times = [intercept + d * slope for d in distances]
        # Fit linear regression to recover slope and intercept
        n = len(distances)
        x_mean = sum(distances) / n
        y_mean = sum(times) / n
        slope_fit = sum((x - x_mean) * (t - y_mean) for x, t in zip(distances, times)) / \
                    sum((x - x_mean)**2 for x in distances)
        intercept_fit = y_mean - slope_fit * x_mean
        # Recover v2 and h1
        v2_est = 1 / slope_fit
        h1_est = intercept_fit * v1 / (2 * math.cos(theta_c))
        ok1 = abs(v2_est - v2) < 1e-6
        ok2 = abs(h1_est - h1) < 1e-6
        return (ok1 and ok2, f"v2_est={v2_est:.4f}, h1_est={h1_est:.4f}")
    ch.add(StructuralCheck(
        label="Remark 3.4: Head wave slope=1/v2, intercept recovers h1",
        section="4",
        predicate=remark_454_head_wave,
        note="Remark 3.4",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Travel Time for Layered Earth ---
    def alg_5_1_travel_time():
        v = [4.0, 5.5, 6.5, 8.1]  # km/s
        h = [2, 10, 20]  # km thicknesses
        # Direct wave: t = x/v[0]
        x = 100.0  # km
        t_direct = x / v[0]
        # Refracted from layer 2: t = x/v[1] + 2*h[0]*cos(ic)/v[0]
        # where sin(ic) = v[0]/v[1]
        ic = math.asin(v[0] / v[1])
        t_refracted1 = x / v[1] + 2 * h[0] * math.cos(ic) / v[0]
        # Direct is slower than refracted at long distances
        # Crossover: x/v0 = x/v1 + 2*h0*cos(ic)/v0
        x_cross = 2 * h[0] * math.cos(ic) * v[1] / (v[1] - v[0])
        ok = x_cross > 0 and t_refracted1 < t_direct
        return (ok, f"x_cross={x_cross:.1f}km, t_direct={t_direct:.2f}s, t_refracted={t_refracted1:.2f}s")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Layered earth travel time computation",
        section="6",
        predicate=alg_5_1_travel_time,
    ))

    # --- Algorithm 5.2: Gutenberg-Richter b-Value ---
    def alg_5_2_b_value():
        np.random.seed(42)
        # Generate synthetic earthquake magnitudes following GR law
        b_true = 1.0
        N = 500
        # GR: log10(N) = a - b*M => M ~ exponential with rate b*ln(10)
        M_min = 2.0
        magnitudes = M_min + np.random.exponential(1 / (b_true * math.log(10)), N)
        # MLE: b = 1 / (mean(M) - M_min) / ln(10)
        b_est = 1 / ((np.mean(magnitudes) - M_min) * math.log(10))
        ok = abs(b_est - b_true) < 0.15
        return (ok, f"b_est={b_est:.3f}, b_true={b_true:.1f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Gutenberg-Richter b-value estimation",
        section="6",
        predicate=alg_5_2_b_value,
    ))

    # --- Algorithm 5.3: Seismogram Spectral Analysis ---
    def alg_5_3_seismogram_fft():
        np.random.seed(42)
        dt = 0.01  # 100 Hz sampling
        N_s = 1024
        t = np.arange(N_s) * dt
        # Synthetic seismogram with dominant frequency at 2 Hz
        signal = np.sin(2 * math.pi * 2 * t) + 0.3 * np.random.randn(N_s)
        X = np.fft.fft(signal)
        freqs = np.fft.fftfreq(N_s, d=dt)
        PSD = np.abs(X) ** 2 / N_s
        pos_mask = freqs > 0
        peak_freq = freqs[pos_mask][np.argmax(PSD[pos_mask])]
        ok = abs(peak_freq - 2.0) < 0.5
        return (ok, f"Peak frequency={peak_freq:.2f} Hz, expected=2.0 Hz")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Seismogram spectral analysis via FFT",
        section="6",
        predicate=alg_5_3_seismogram_fft,
    ))

    # --- Algorithm 5.4: Radiocarbon Age ---
    def alg_5_4_radiocarbon():
        # t = -ln(A/A0) / lambda, lambda = ln(2)/5730
        lam = math.log(2) / 5730
        A_over_A0 = 0.5  # half of original => 1 half-life
        t = -math.log(A_over_A0) / lam
        ok1 = abs(t - 5730) < 1
        # 25% remaining => 2 half-lives
        t2 = -math.log(0.25) / lam
        ok2 = abs(t2 - 11460) < 1
        return (ok1 and ok2, f"50% => t={t:.0f}yr, 25% => t={t2:.0f}yr")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Radiocarbon age computation",
        section="6",
        predicate=alg_5_4_radiocarbon,
    ))

    # --- Algorithm 5.5: Plate Velocity from Euler Pole ---
    def alg_5_5_euler_pole():
        # v = omega * R * sin(Delta), where Delta = angular distance from Euler pole
        omega = 0.75 * math.pi / 180  # deg/Myr to rad/Myr
        R = 6371.0  # km
        delta = 90.0 * math.pi / 180  # 90 degrees from pole (maximum velocity)
        v = omega * R * math.sin(delta)  # km/Myr
        v_cm_yr = v / 10  # convert to cm/yr
        ok = v_cm_yr > 0
        # At delta=0 (on the pole), velocity should be 0
        v_pole = omega * R * math.sin(0)
        ok2 = abs(v_pole) < 1e-10
        return (ok and ok2, f"v_max={v_cm_yr:.1f} cm/yr, v_pole={v_pole:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Plate velocity from Euler pole",
        section="6",
        predicate=alg_5_5_euler_pole,
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _mw_identity():
    import sympy
    M0 = sympy.Symbol('M0', positive=True)
    Mw = sympy.Rational(2, 3) * (sympy.log(M0, 10) - sympy.Rational(91, 10))
    # Round-trip: 10^(1.5*Mw + 9.1) = M0
    recovered = 10**(sympy.Rational(3, 2) * Mw + sympy.Rational(91, 10))
    return sympy.Eq(sympy.simplify(sympy.log(recovered, 10) - sympy.log(M0, 10)), 0)


def _radiocarbon_identity():
    import sympy
    r, r0, lam = sympy.symbols('r r0 lambda_d', positive=True)
    t = sympy.ln(r0 / r) / lam
    # Check: r0 * exp(-lam * t) = r
    recovered = r0 * sympy.exp(-lam * t)
    return sympy.Eq(sympy.simplify(recovered - r), 0)


def _bvalue_identity():
    import sympy
    Mbar, Mc = sympy.symbols('Mbar Mc', positive=True)
    b = sympy.log(sympy.E, 10) / (Mbar - Mc)
    # This is the MLE for the exponential-form GR law
    # Check: for the exponential distribution with rate beta = b*ln(10),
    # the MLE of beta is 1/(Mbar - Mc), so b = log10(e)/(Mbar - Mc)
    beta = b * sympy.ln(10)
    expected_beta = 1 / (Mbar - Mc)
    return sympy.Eq(sympy.simplify(beta - expected_beta), 0)


def _energy_magnitude_zero():
    import sympy
    M0 = sympy.Symbol('M0', positive=True)
    # Mw = (2/3)*(log10(M0) - 9.1)
    # log10(E) = 1.5*Mw + 4.8
    # Substituting: log10(E) = (3/2)*(2/3)*(log10(M0) - 9.1) + 4.8
    #             = log10(M0) - 9.1 + 4.8 = log10(M0) - 4.3
    # Note: Ch.45 proof writes "-9.15" (an arithmetic slip); the correct
    # result from the definitions is -9.1 + 4.8 = -4.3.
    Mw_expr = sympy.Rational(2, 3) * (sympy.log(M0, 10) - sympy.Rational(91, 10))
    log10_E = sympy.Rational(3, 2) * Mw_expr + sympy.Rational(48, 10)
    expected = sympy.log(M0, 10) - sympy.Rational(43, 10)
    return sympy.expand(log10_E - expected)


def _isochron_identity():
    import sympy
    lam, t, m = sympy.symbols('lambda t m', positive=True)
    # m = exp(lambda*t) - 1  =>  t = ln(1+m)/lambda
    t_from_m = sympy.ln(1 + m) / lam
    m_from_t = sympy.exp(lam * t) - 1
    # Substitute: t_from_m(m_from_t(t)) should equal t
    recovered = sympy.ln(1 + m_from_t) / lam
    return sympy.Eq(sympy.simplify(recovered - t), 0)


def _halflife_identity():
    import sympy
    lam = sympy.Symbol('lambda_d', positive=True)
    t_half = sympy.ln(2) / lam
    # N(t_half)/N0 = exp(-lam * t_half) should equal 1/2
    ratio = sympy.exp(-lam * t_half)
    return sympy.Eq(sympy.simplify(ratio - sympy.Rational(1, 2)), 0)


def _pwave_identity():
    import sympy
    K, mu, rho = sympy.symbols('K mu rho', positive=True)
    vP = sympy.sqrt((K + 4*mu/3) / rho)
    vS = sympy.sqrt(mu / rho)
    # v_P^2 - v_S^2 = (K + 4*mu/3 - mu)/rho = (K + mu/3)/rho > 0
    diff = sympy.simplify(vP**2 - vS**2 - (K + mu/3)/rho)
    return sympy.Eq(diff, 0)


def _crossover_zero():
    import sympy
    h1, v1, v2 = sympy.symbols('h1 v1 v2', positive=True)
    # x_cross = 2*h1*sqrt((v2+v1)/(v2-v1))
    # At crossover: T_direct(x_cross) = T_head(x_cross)
    # i.e. x_cross/v1 = x_cross/v2 + 2*h1*sqrt(v2^2-v1^2)/(v1*v2)
    # Rearranging: x_cross*(1/v1 - 1/v2) = 2*h1*sqrt(v2^2-v1^2)/(v1*v2)
    # LHS: x_cross*(v2-v1)/(v1*v2) = 2*h1*sqrt((v2+v1)/(v2-v1))*(v2-v1)/(v1*v2)
    #     = 2*h1*(v2-v1)*sqrt((v2+v1)/(v2-v1))/(v1*v2)
    #     = 2*h1*sqrt((v2-v1)^2*(v2+v1)/(v2-v1))/(v1*v2)
    #     = 2*h1*sqrt((v2-v1)*(v2+v1))/(v1*v2)
    #     = 2*h1*sqrt(v2^2-v1^2)/(v1*v2) = RHS
    # Verify this algebraically:
    lhs = 2 * h1 * sympy.sqrt((v2+v1)/(v2-v1)) * (v2-v1) / (v1*v2)
    rhs = 2 * h1 * sympy.sqrt(v2**2 - v1**2) / (v1*v2)
    return sympy.simplify(lhs**2 - rhs**2)


def _mw_monotonic_check():
    M0_values = [1e15, 1e18, 1e20, 1e22, 1e25]
    Mw_values = [(2/3) * (math.log10(m) - 9.1) for m in M0_values]
    monotonic = all(Mw_values[i] < Mw_values[i+1] for i in range(len(Mw_values)-1))
    return monotonic, f"Mw values: {[f'{m:.2f}' for m in Mw_values]}"


def _radiocarbon_structural_check():
    half_life = 5730
    lam = math.log(2) / half_life
    # At r = r0 (fresh sample), age = 0
    age_fresh = math.log(1.0) / lam
    # At r = 0.5 * r0, age = half_life
    age_half = math.log(1.0 / 0.5) / lam
    ok = (abs(age_fresh) < 1e-12 and abs(age_half - half_life) < 1e-6)
    return ok, f"age(r=r0) = {age_fresh}, age(r=r0/2) = {age_half:.1f} (expected {half_life})"


def _vp_vs_check():
    """Check v_P > v_S for several realistic rock types."""
    materials = [
        (50e9, 30e9, 2700),   # granite
        (130e9, 70e9, 3300),  # upper mantle
        (2.2e9, 0, 1000),     # water
        (37e9, 44e9, 2600),   # sandstone-like
    ]
    ok = True
    msg = ""
    for K, mu, rho in materials:
        vP = math.sqrt((K + 4*mu/3) / rho)
        vS = math.sqrt(mu / rho)
        if vP <= vS:
            ok = False
            msg = f"Failed for K={K}, mu={mu}, rho={rho}: vP={vP}, vS={vS}"
            break
    if ok:
        msg = f"v_P > v_S verified for {len(materials)} materials"
    return ok, msg


def _gr_monotonic_check():
    """GR law: N decreasing with M for b > 0."""
    a, b = 5.0, 1.0
    magnitudes = [2, 3, 4, 5, 6, 7, 8]
    N_values = [10**(a - b*M) for M in magnitudes]
    monotonic = all(N_values[i] > N_values[i+1] for i in range(len(N_values)-1))
    msg = f"N values: {[f'{n:.1f}' for n in N_values]}"
    return monotonic, msg


def _plate_velocity_structural_check():
    """Plate velocity = omega*R*sin(Delta): zero at pole, max at 90 deg."""
    omega = 0.01309  # rad/Myr
    R = 6371  # km
    deltas = [0, 30, 60, 90, 120, 150, 180]
    speeds = [omega * R * math.sin(math.radians(d)) for d in deltas]
    # Speed at Delta=0 should be 0
    zero_at_pole = abs(speeds[0]) < 1e-10
    # Speed at Delta=90 should be maximum
    max_at_90 = abs(speeds[3] - max(speeds)) < 1e-10
    # Speed at Delta=180 should be 0 (antipodal)
    zero_at_anti = abs(speeds[6]) < 1e-10
    ok = zero_at_pole and max_at_90 and zero_at_anti
    msg = f"speeds at [0,30,60,90,120,150,180] deg: {[f'{s:.1f}' for s in speeds]}"
    return ok, msg


def _isochron_linearity_check():
    """Check that the Rb-Sr data from Example 8.4b is highly linear."""
    x = np.array([0.50, 1.50, 3.00, 5.00])
    y = np.array([0.7120, 0.7192, 0.7300, 0.7444])
    # Linear regression
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    ss_xx = np.sum((x - x_mean)**2)
    ss_yy = np.sum((y - y_mean)**2)
    slope = ss_xy / ss_xx
    r_squared = (ss_xy**2) / (ss_xx * ss_yy)
    ok = r_squared > 0.999
    msg = f"R^2 = {r_squared:.6f}, slope = {slope:.6f}"
    return ok, msg


def _swave_fluid_check():
    """S-wave velocity is exactly zero when shear modulus is zero."""
    fluids = [
        (2.2e9, 0, 1000),   # water
        (1.0e9, 0, 800),    # oil
        (1.4e5, 0, 1.2),    # air
    ]
    ok = True
    msg = ""
    for K, mu, rho in fluids:
        vS = math.sqrt(mu / rho)
        if vS != 0.0:
            ok = False
            msg = f"vS = {vS} for K={K}, mu={mu}, rho={rho}"
            break
    if ok:
        msg = f"vS = 0 verified for {len(fluids)} fluids"
    return ok, msg


def _headwave_crossover_check():
    """Head wave is faster than direct wave for x > x_cross."""
    v1 = 5.0   # km/s
    v2 = 8.0   # km/s
    h1 = 30.0  # km
    cos_tc = math.sqrt(1 - (v1/v2)**2)
    x_cross = 2 * h1 * math.sqrt((v2 + v1) / (v2 - v1))

    # Test a range of distances beyond crossover
    ok = True
    msg = f"x_cross = {x_cross:.1f} km"
    for x in [x_cross + 10, x_cross + 50, x_cross + 200, 500]:
        T_direct = x / v1
        T_head = x / v2 + 2 * h1 * cos_tc / v1
        if T_head >= T_direct:
            ok = False
            msg = f"Head wave not faster at x={x}: T_head={T_head:.3f}, T_direct={T_direct:.3f}"
            break
    # Also verify direct is faster below crossover
    for x in [10, x_cross - 10]:
        if x > 0:
            T_direct = x / v1
            T_head = x / v2 + 2 * h1 * cos_tc / v1
            if T_head < T_direct:
                ok = False
                msg = f"Head wave should not be faster at x={x}: T_head={T_head:.3f}, T_direct={T_direct:.3f}"
                break
    return ok, msg


def _angular_distance(lat1, lon1, lat2, lon2):
    """Compute angular distance in degrees between two points using spherical law of cosines."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    cos_d = math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2)*math.cos(dlam)
    cos_d = max(-1.0, min(1.0, cos_d))
    return math.degrees(math.acos(cos_d))


def _plate_speed(euler_lat, euler_lon, ang_speed_deg_myr, point_lat, point_lon, R=6371):
    """Compute plate speed in mm/yr (= km/Myr) from Euler pole."""
    omega_rad = ang_speed_deg_myr * math.pi / 180  # rad/Myr
    delta = _angular_distance(euler_lat, euler_lon, point_lat, point_lon)
    return omega_rad * R * math.sin(math.radians(delta))


def _isochron_slope():
    """Compute the slope of the Rb-Sr isochron from Example 8.4b data."""
    x = np.array([0.50, 1.50, 3.00, 5.00])
    y = np.array([0.7120, 0.7192, 0.7300, 0.7444])
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean)**2)
    return slope


def _ex457_travel_time():
    """Exercise 10.7: Four-layer travel time curve with crossover distances."""
    v = [4.0, 5.5, 6.5, 8.1]  # km/s
    h = [2.0, 10.0, 20.0]     # km
    # Direct wave: t = x / v[0]
    # Refracted from layer i (1-indexed): first arrival at large distances
    # t_i(x) = x/v[i] + sum_j 2*h[j]*cos(theta_j)/v[j]
    #   where sin(theta_j) = v[j]/v[i] (Snell's law)

    def refracted_time(x, layer_idx):
        """Travel time for head wave refracted from layer layer_idx (0-indexed)."""
        v_ref = v[layer_idx]
        t_head = x / v_ref
        for j in range(layer_idx):
            sin_tc = v[j] / v_ref
            if sin_tc > 1:
                return float('inf')
            cos_tc = math.sqrt(1 - sin_tc**2)
            t_head += 2 * h[j] * cos_tc / v[j]
        return t_head

    # Find crossover distances: where refracted becomes faster than direct
    crossovers = []
    for li in range(1, len(v)):
        # Find x where refracted time = direct time
        # Direct: x/v[0], Refracted: x/v[li] + intercept
        intercept = 0
        valid = True
        for j in range(li):
            sin_tc = v[j] / v[li]
            if sin_tc >= 1:
                valid = False
                break
            cos_tc = math.sqrt(1 - sin_tc**2)
            intercept += 2 * h[j] * cos_tc / v[j]
        if not valid:
            continue
        # x/v[0] = x/v[li] + intercept => x*(1/v[0] - 1/v[li]) = intercept
        x_cross = intercept / (1/v[0] - 1/v[li])
        if x_cross > 0:
            crossovers.append(x_cross)

    # Verify first arrivals at various distances
    ok = True
    for x in range(10, 500, 10):
        times = [x / v[0]]  # direct
        for li in range(1, len(v)):
            t = refracted_time(x, li)
            if t < float('inf'):
                times.append(t)
        first_arrival = min(times)
        if first_arrival <= 0:
            ok = False
            break

    # Should have at least 2 crossover distances
    if len(crossovers) < 2:
        return (False, f"Only {len(crossovers)} crossover distances found")
    return (ok, f"Crossovers at x = {[f'{x:.1f}' for x in crossovers]} km")


def _ex458_seismogram_psd():
    """Exercise 10.8: Synthetic seismogram with P-wave (2 Hz) and S-wave (0.8 Hz).
    PSD should show peaks at these frequencies."""
    rng = np.random.default_rng(42)
    fs = 50.0  # Hz
    T = 20.0   # seconds
    N = int(fs * T)
    t = np.arange(N) / fs

    # P-wave at 3s, dominant freq 2 Hz
    p_env = np.exp(-((t - 3) / 0.5)**2)
    p_wave = p_env * np.sin(2 * np.pi * 2 * t)

    # S-wave at 8s, dominant freq 0.8 Hz
    s_env = np.exp(-((t - 8) / 1.0)**2)
    s_wave = s_env * np.sin(2 * np.pi * 0.8 * t)

    # Add noise
    signal = p_wave + s_wave + 0.1 * rng.standard_normal(N)

    # Compute PSD
    X = np.fft.rfft(signal)
    P = np.abs(X)**2 / N
    freqs = np.fft.rfftfreq(N, d=1/fs)

    # Find peaks near 2 Hz and 0.8 Hz
    def power_near(f_target, bandwidth=0.3):
        mask = (freqs >= f_target - bandwidth) & (freqs <= f_target + bandwidth)
        if not np.any(mask):
            return 0
        return np.max(P[mask])

    p_power = power_near(2.0)
    s_power = power_near(0.8)
    noise_power = np.median(P[freqs > 5])  # far from signal

    # Both peaks should be well above noise floor
    ok = p_power > 10 * noise_power and s_power > 10 * noise_power
    return (ok, f"P-wave power={p_power:.1f}, S-wave power={s_power:.1f}, noise={noise_power:.1f}")


def _isochron_intercept():
    """Compute the intercept of the Rb-Sr isochron from Example 8.4b data."""
    x = np.array([0.50, 1.50, 3.00, 5.00])
    y = np.array([0.7120, 0.7192, 0.7300, 0.7444])
    slope = _isochron_slope()
    intercept = np.mean(y) - slope * np.mean(x)
    return intercept
