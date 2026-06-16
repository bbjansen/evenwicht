# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 39: Classical Mechanics & Waves — verification."""

import math
import numpy as np
import scipy
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(39, "Classical Mechanics & Waves")

    g = 9.81

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Projectile range formula: R = v0^2*sin(2*theta)/g",
        section="5",
        identity=lambda: _projectile_range_identity(),
    ))

    ch.add(SymbolicCheck(
        label="SHO frequency: omega = sqrt(k/m), T = 2*pi/omega",
        section="5",
        identity=lambda: _sho_period_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Damped eigenvalues: lambda = -gamma +/- sqrt(gamma^2 - omega^2)",
        section="5",
        zero_expr=lambda: _damped_eigenvalue_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Driven oscillator amplitude formula: A(Omega) = (F0/m)/sqrt((w^2-O^2)^2+4g^2*O^2)",
        section="5",
        identity=lambda: _driven_amplitude_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Harmonic oscillator energy: E = (1/2)*m*omega^2*A^2 is constant",
        section="5",
        identity=lambda: _harmonic_energy_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Standing wave decomposition: sin(kx)cos(wt) = (1/2)[sin(kx-wt)+sin(kx+wt)]",
        section="5",
        zero_expr=lambda: _standing_wave_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Resonance frequency: Omega_res = sqrt(omega^2 - 2*gamma^2)",
        section="5",
        zero_expr=lambda: _resonance_frequency_identity(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # --- Example 8.1: Projectile ---
    v0, theta_deg = 25, 50
    theta = math.radians(theta_deg)

    ch.add(NumericCheck(
        label="Projectile: sin(100 deg) = 0.9848",
        section="9.1",
        stated=0.9848,
        computed=lambda: math.sin(2 * theta),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Projectile: v0^2 = 625",
        section="9.1",
        stated=625.0,
        computed=lambda: v0**2,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Projectile range: v0=25 m/s, theta=50 deg => R ~ 62.76 m",
        section="9.1",
        stated=62.76,
        computed=lambda: v0**2 * math.sin(2 * theta) / g,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Projectile: v_x = v0*cos(theta) = 25*cos(50 deg) ~ 16.070 m/s",
        section="9.1",
        stated=16.070,
        computed=lambda: v0 * math.cos(theta),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Projectile: v_y = v0*sin(theta) = 25*sin(50 deg) ~ 19.151 m/s",
        section="9.1",
        stated=19.151,
        computed=lambda: v0 * math.sin(theta),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Projectile: sin(50 deg) ~ 0.7660",
        section="9.1",
        stated=0.7660,
        computed=lambda: math.sin(theta),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Projectile time of flight: ~3.906 s",
        section="9.1",
        stated=3.906,
        computed=lambda: 2 * v0 * math.sin(theta) / g,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Projectile max height: v_y^2/(2*g) ~ 18.70 m",
        section="9.1",
        stated=18.70,
        computed=lambda: (v0 * math.sin(theta))**2 / (2 * g),
        tolerance=2e-3,
    ))

    # --- Example 8.2: Damped oscillator ---
    omega, gamma = 10.0, 2.0
    m_osc = 1.0
    k_osc = 100.0
    b_damp = 4.0

    ch.add(NumericCheck(
        label="Damped oscillator: omega = sqrt(k/m) = sqrt(100) = 10 rad/s",
        section="9.2",
        stated=10.0,
        computed=lambda: math.sqrt(k_osc / m_osc),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Damped oscillator: gamma = b/(2m) = 4/2 = 2 rad/s",
        section="9.2",
        stated=2.0,
        computed=lambda: b_damp / (2 * m_osc),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Damped freq: omega_d = sqrt(100-4) ~ 9.798 rad/s",
        section="9.2",
        stated=9.798,
        computed=lambda: math.sqrt(omega**2 - gamma**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Damped discriminant: gamma^2 - omega^2 = 4 - 100 = -96",
        section="9.2",
        stated=-96.0,
        computed=lambda: gamma**2 - omega**2,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Damped eigenvalue imaginary part: sqrt(96) ~ 9.798",
        section="9.2",
        stated=9.798,
        computed=lambda: math.sqrt(96),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Damped eigenvalue real part: -gamma = -2",
        section="9.2",
        stated=-2.0,
        computed=lambda: -gamma,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Damping ratio: zeta = gamma/omega = 0.2 (underdamped < 1)",
        section="9.2",
        stated=0.2,
        computed=lambda: gamma / omega,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Quality factor: Q = omega/(2*gamma) = 10/4 = 2.5",
        section="9.2",
        stated=2.5,
        computed=lambda: omega / (2 * gamma),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Damped envelope at t=1: 0.1*exp(-2) ~ 0.01353",
        section="9.2",
        stated=0.01353,
        computed=lambda: 0.1 * math.exp(-2 * 1),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Damped envelope at t=5: 0.1*exp(-10) ~ 4.540e-6",
        section="9.2",
        stated=4.540e-6,
        computed=lambda: 0.1 * math.exp(-gamma * 5),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Initial energy E0 = 0.5*k*x0^2 = 0.5*100*0.01 = 0.5 J",
        section="9.2",
        stated=0.5,
        computed=lambda: 0.5 * k_osc * 0.1**2,
        tolerance=1e-10,
    ))

    # --- Driven oscillator (Formulas F4.6-F4.8, Theorem 3.7) ---
    # Using omega=10, gamma=2, F0/m = 1 (unit forcing)
    F0_over_m = 1.0

    ch.add(NumericCheck(
        label="Driven oscillator resonance freq: Omega_res = sqrt(100-8) ~ 9.592 rad/s",
        section="5",
        stated=9.592,
        computed=lambda: math.sqrt(omega**2 - 2 * gamma**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Driven oscillator: resonance exists since gamma=2 < omega/sqrt(2) ~ 7.071",
        section="5",
        stated=7.071,
        computed=lambda: omega / math.sqrt(2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Driven oscillator amplitude at resonance: A_max = (F0/m)/(2*gamma*omega_d) ~ 0.02552",
        section="5",
        stated=0.02552,
        computed=lambda: F0_over_m / (2 * gamma * math.sqrt(omega**2 - gamma**2)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Driven oscillator amplitude at Omega=omega: A(omega) = (F0/m)/(2*gamma*omega) ~ 0.025",
        section="5",
        stated=0.025,
        computed=lambda: F0_over_m / math.sqrt((omega**2 - omega**2)**2 + 4 * gamma**2 * omega**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Driven oscillator amplitude at Omega=0 (static): A(0) = (F0/m)/omega^2 = 0.01",
        section="5",
        stated=0.01,
        computed=lambda: F0_over_m / math.sqrt((omega**2)**2),
        tolerance=1e-10,
    ))

    # --- Example 8.3: Coupled spring normal modes ---
    ch.add(NumericCheck(
        label="Coupled spring stiffness matrix K[0,0] = k1+kc = 6+2 = 8",
        section="9.3",
        stated=8.0,
        computed=lambda: 6.0 + 2.0,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Coupled spring stiffness matrix K[1,1] = k2+kc = 4+2 = 6",
        section="9.3",
        stated=6.0,
        computed=lambda: 4.0 + 2.0,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Coupled spring: char poly discriminant = 121-88 = 33",
        section="9.3",
        stated=33.0,
        computed=lambda: 11.0**2 - 4 * 22.0,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Coupled spring: lambda_1 ~ 2.628",
        section="9.3",
        stated=2.628,
        computed=lambda: (11 - math.sqrt(33)) / 2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Coupled spring: lambda_2 ~ 8.372",
        section="9.3",
        stated=8.372,
        computed=lambda: (11 + math.sqrt(33)) / 2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Normal mode omega_1 ~ 1.621 rad/s",
        section="9.3",
        stated=1.621,
        computed=lambda: math.sqrt((11 - math.sqrt(33)) / 2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Normal mode omega_2 ~ 2.894 rad/s",
        section="9.3",
        stated=2.894,
        computed=lambda: math.sqrt((11 + math.sqrt(33)) / 2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Mode 1 shape ratio u2/u1 = (8-lambda_1)/2 ~ 2.686",
        section="9.3",
        stated=2.686,
        computed=lambda: (8 - (11 - math.sqrt(33)) / 2) / 2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Mode 2 shape ratio u2/u1 = (8-lambda_2)/2 ~ -0.186",
        section="9.3",
        stated=-0.186,
        computed=lambda: (8 - (11 + math.sqrt(33)) / 2) / 2,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Mode 1 period T1 = 2*pi/omega_1 ~ 3.876 s",
        section="9.3",
        stated=3.876,
        computed=lambda: 2 * math.pi / math.sqrt((11 - math.sqrt(33)) / 2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Mode 2 period T2 = 2*pi/omega_2 ~ 2.171 s",
        section="9.3",
        stated=2.171,
        computed=lambda: 2 * math.pi / math.sqrt((11 + math.sqrt(33)) / 2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Coupled spring: product of eigenvalues = det(D) = 8*3-(-2)*(-1) = 22",
        section="9.3",
        stated=22.0,
        computed=lambda: 8.0 * 3.0 - (-2.0) * (-1.0),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Coupled spring: sum of eigenvalues = trace(D) = 8+3 = 11",
        section="9.3",
        stated=11.0,
        computed=lambda: 8.0 + 3.0,
        tolerance=1e-10,
    ))

    # --- Example 8.4: Nonlinear pendulum ---
    l_pend = 1.0
    theta0_pend = math.radians(120)

    ch.add(NumericCheck(
        label="Small-angle pendulum period: T0 = 2*pi*sqrt(1/9.81) ~ 2.006 s",
        section="9.4",
        stated=2.006,
        computed=lambda: 2 * math.pi * math.sqrt(l_pend / g),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Pendulum omega_0 = sqrt(g/l) = sqrt(9.81) ~ 3.132 rad/s",
        section="9.4",
        stated=3.132,
        computed=lambda: math.sqrt(g / l_pend),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Pendulum: sin(theta0/2) = sin(60 deg) = sqrt(3)/2 ~ 0.8660",
        section="9.4",
        stated=0.8660,
        computed=lambda: math.sin(theta0_pend / 2),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Pendulum: K(sin(60 deg)) = K(sqrt(3)/2) ~ 2.157",
        section="9.4",
        stated=2.157,
        computed=lambda: float(scipy.special.ellipk(math.sin(theta0_pend / 2)**2)),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="Pendulum period correction factor: 2*K/pi ~ 1.373",
        section="9.4",
        stated=1.373,
        computed=lambda: 2 * float(scipy.special.ellipk(math.sin(theta0_pend / 2)**2)) / math.pi,
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="Nonlinear pendulum period (theta0=120 deg): ~2.754 s",
        section="9.4",
        stated=2.754,
        computed=lambda: _nonlinear_pendulum_period(theta0_pend),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Pendulum period deviation from linear: ~37.3%",
        section="9.4",
        stated=37.3,
        computed=lambda: (_nonlinear_pendulum_period(theta0_pend) - 2 * math.pi * math.sqrt(l_pend / g)) / (2 * math.pi * math.sqrt(l_pend / g)) * 100,
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Pendulum initial energy: E0 = mgl*(1-cos(120 deg)) = 9.81*1.5 = 14.715 J",
        section="9.4",
        stated=14.715,
        computed=lambda: 1.0 * g * l_pend * (1 - math.cos(theta0_pend)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Pendulum cos(120 deg) = -0.5",
        section="9.4",
        stated=-0.5,
        computed=lambda: math.cos(theta0_pend),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Pendulum 1 - cos(120 deg) = 1.5",
        section="9.4",
        stated=1.5,
        computed=lambda: 1 - math.cos(theta0_pend),
        tolerance=1e-10,
    ))

    # Pendulum period at smaller angles (series correction)
    theta0_30 = math.radians(30)
    ch.add(NumericCheck(
        label="Pendulum period at theta0=30 deg via elliptic integral ~ 2.040 s",
        section="9.4",
        stated=2.040,
        computed=lambda: _nonlinear_pendulum_period(theta0_30),
        tolerance=2e-3,
    ))

    theta0_60 = math.radians(60)
    ch.add(NumericCheck(
        label="Pendulum period at theta0=60 deg via elliptic integral ~ 2.153 s",
        section="9.4",
        stated=2.153,
        computed=lambda: _nonlinear_pendulum_period(theta0_60),
        tolerance=2e-3,
    ))

    theta0_90 = math.radians(90)
    ch.add(NumericCheck(
        label="Pendulum period at theta0=90 deg via elliptic integral ~ 2.368 s",
        section="9.4",
        stated=2.368,
        computed=lambda: _nonlinear_pendulum_period(theta0_90),
        tolerance=2e-3,
    ))

    # --- Example 8.5: Vibrating string ---
    N_str = 8
    tau_str = 10.0
    m_str = 0.01
    L_str = 1.0
    dx_str = L_str / (N_str + 1)  # 1/9
    c_str = tau_str / dx_str       # 90
    sqrt_c_over_m = math.sqrt(c_str / m_str)  # sqrt(9000) ~ 94.87

    ch.add(NumericCheck(
        label="String: dx = L/(N+1) = 1/9 ~ 0.1111 m",
        section="9.5",
        stated=1.0 / 9.0,
        computed=lambda: dx_str,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="String: c = tau/dx = 10/(1/9) = 90 N/m",
        section="9.5",
        stated=90.0,
        computed=lambda: c_str,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="String: sqrt(c/m) = sqrt(9000) ~ 94.87 rad/s",
        section="9.5",
        stated=94.87,
        computed=lambda: sqrt_c_over_m,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="String: 2*sqrt(c/m) ~ 189.7 rad/s",
        section="9.5",
        stated=189.7,
        computed=lambda: 2 * sqrt_c_over_m,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="String: diagonal of D = 2c/m = 18000 s^-2",
        section="9.5",
        stated=18000.0,
        computed=lambda: 2 * c_str / m_str,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="String: off-diagonal of D = -c/m = -9000 s^-2",
        section="9.5",
        stated=-9000.0,
        computed=lambda: -c_str / m_str,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="String mode k=1 freq: omega_1 ~ 33.0 rad/s",
        section="9.5",
        stated=33.0,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(math.pi / 18),
        tolerance=2e-2,
    ))

    ch.add(NumericCheck(
        label="String mode k=2 freq: omega_2 ~ 64.9 rad/s",
        section="9.5",
        stated=64.9,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(2 * math.pi / 18),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=3 freq: omega_3 ~ 94.9 rad/s",
        section="9.5",
        stated=94.9,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(3 * math.pi / 18),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=4 freq: omega_4 ~ 122.0 rad/s",
        section="9.5",
        stated=122.0,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(4 * math.pi / 18),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=5 freq: omega_5 ~ 145.5 rad/s",
        section="9.5",
        stated=145.5,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(5 * math.pi / 18),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=6 freq: omega_6 ~ 164.3 rad/s",
        section="9.5",
        stated=164.3,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(6 * math.pi / 18),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=7 freq: omega_7 ~ 178.3 rad/s",
        section="9.5",
        stated=178.3,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(7 * math.pi / 18),
        tolerance=2e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=8 freq: omega_8 ~ 186.9 rad/s",
        section="9.5",
        stated=186.9,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(8 * math.pi / 18),
        tolerance=2e-3,
    ))

    # Frequencies in Hz (from table in text)
    ch.add(NumericCheck(
        label="String mode k=1 freq in Hz: f_1 ~ 5.25 Hz",
        section="9.5",
        stated=5.25,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(math.pi / 18) / (2 * math.pi),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=2 freq in Hz: f_2 ~ 10.3 Hz",
        section="9.5",
        stated=10.3,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(2 * math.pi / 18) / (2 * math.pi),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=3 freq in Hz: f_3 ~ 15.1 Hz",
        section="9.5",
        stated=15.1,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(3 * math.pi / 18) / (2 * math.pi),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=4 freq in Hz: f_4 ~ 19.4 Hz",
        section="9.5",
        stated=19.4,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(4 * math.pi / 18) / (2 * math.pi),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="String mode k=5 freq in Hz: f_5 ~ 23.2 Hz",
        section="9.5",
        stated=23.2,
        computed=lambda: 2 * sqrt_c_over_m * math.sin(5 * math.pi / 18) / (2 * math.pi),
        tolerance=5e-3,
    ))

    # Continuum limit wave speed (mu = m/dx for this discrete model)
    mu_str = m_str / dx_str  # linear mass density = 0.09 kg/m
    c_wave = math.sqrt(tau_str / mu_str)  # wave speed
    ch.add(NumericCheck(
        label="Continuum string wave speed: c = sqrt(tau/mu) = sqrt(10/0.09) ~ 10.541 m/s",
        section="5",
        stated=10.541,
        computed=lambda: c_wave,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Continuum fundamental freq: omega_1 = pi*c/L ~ 33.12 rad/s",
        section="5",
        stated=33.12,
        computed=lambda: math.pi * c_wave / L_str,
        tolerance=2e-3,
    ))

    # Discrete string analytical eigenvalues (lambda_k = 4*c/m * sin^2(k*pi/(2*(N+1))))
    ch.add(NumericCheck(
        label="String eigenvalue lambda_1 = 4*c/m*sin^2(pi/18) ~ 1085.5",
        section="9.5",
        stated=1085.5,
        computed=lambda: 4 * c_str / m_str * math.sin(math.pi / 18)**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="String eigenvalue lambda_4 = 4*c/m*sin^2(4*pi/18) ~ 14874.3",
        section="9.5",
        stated=14874.3,
        computed=lambda: 4 * c_str / m_str * math.sin(4 * math.pi / 18)**2,
        tolerance=1e-3,
    ))

    # Step-size recommendation verification (Section 7)
    ch.add(NumericCheck(
        label="RK4 step size for omega=10: h <= 0.3/omega = 0.03 s",
        section="7",
        stated=0.03,
        computed=lambda: 0.3 / 10.0,
        tolerance=1e-10,
    ))

    # --- Formula gap fills ---

    # F4.9: Normal modes omega_k = 2*sqrt(c/m)*sin(k*pi/(2*(N+1)))
    ch.add(NumericCheck(
        label="F4.9: Normal mode omega_1 for coupled spring ~ 1.621 rad/s",
        section="5",
        stated=1.621,
        computed=lambda: math.sqrt((11 - math.sqrt(33)) / 2),
        tolerance=1e-3,
    ))

    # F4.13: Pendulum energy E = mgl*(1 - cos(theta)) + (1/2)*m*l^2*omega^2
    ch.add(NumericCheck(
        label="F4.13: Pendulum initial energy E0 = mgl*(1-cos(120deg)) = 14.715 J",
        section="5",
        stated=14.715,
        computed=lambda: 1.0 * 9.81 * 1.0 * (1 - math.cos(math.radians(120))),
        tolerance=1e-3,
    ))

    # F4.16: Fourier sine coefficient b_n = (2/L)*integral_0^L f(x)*sin(n*pi*x/L) dx
    def fourier_sine_coeff_check():
        # For center-plucked string: b_n = 0 for even n, nonzero for odd n
        N = 8
        dx = 1.0 / (N + 1)
        u0 = []
        for j in range(1, N + 1):
            if j <= N // 2:
                u0.append(j * dx)
            else:
                u0.append((N + 1 - j) * dx)
        u0 = np.array(u0)
        # Compute b_1
        mode1 = np.array([math.sin(j * math.pi / (N + 1)) for j in range(1, N + 1)])
        b1 = np.dot(u0, mode1) / np.dot(mode1, mode1)
        ok = abs(b1) > 0.01
        return (ok, f"b_1 = {b1:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.16: Fourier sine coefficient b_1 > 0 for center pluck",
        section="5",
        predicate=fourier_sine_coeff_check,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Coupled spring eigenvalues: dynamical matrix D has correct spectrum",
        section="9.3",
        predicate=lambda: _coupled_spring_eigenvalue_check(),
    ))

    ch.add(StructuralCheck(
        label="String modes: eigenvalues of tridiagonal match formula",
        section="9.5",
        predicate=lambda: _string_eigenvalue_check(),
    ))

    ch.add(StructuralCheck(
        label="String eigenvectors: components u_j^(k) = sin(j*k*pi/(N+1))",
        section="9.5",
        predicate=lambda: _string_eigenvector_check(),
    ))

    ch.add(StructuralCheck(
        label="Driven oscillator: amplitude maximized at Omega_res",
        section="5",
        predicate=lambda: _driven_resonance_peak_check(),
    ))

    ch.add(StructuralCheck(
        label="Nonlinear pendulum: period increases monotonically with theta0",
        section="9.4",
        predicate=lambda: _pendulum_period_monotone_check(),
    ))

    ch.add(StructuralCheck(
        label="Damped oscillator: companion matrix eigenvalues have negative real part",
        section="9.2",
        predicate=lambda: _damped_stability_check(),
    ))

    ch.add(StructuralCheck(
        label="String modes: odd-mode-only excitation by symmetric pluck",
        section="9.5",
        predicate=lambda: _symmetric_pluck_odd_modes_check(),
    ))

    ch.add(StructuralCheck(
        label="Harmonic oscillator energy conservation over one period",
        section="5",
        predicate=lambda: _energy_conservation_check(),
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 11.1: Free fall from 45 m ---
    h_drop = 45.0
    # t = sqrt(2*h/g), v_impact = g*t = sqrt(2*g*h)
    t_fall = math.sqrt(2 * h_drop / g)
    v_impact = g * t_fall

    ch.add(NumericCheck(
        label="Ex 11.1: Free fall time from 45 m: t = sqrt(2*45/9.81) ~ 3.029 s",
        section="11",
        stated=3.029,
        computed=lambda: math.sqrt(2 * 45.0 / 9.81),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 11.1: Impact velocity from 45 m: v = g*t ~ 29.71 m/s",
        section="11",
        stated=29.71,
        computed=lambda: 9.81 * math.sqrt(2 * 45.0 / 9.81),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 11.1: Impact velocity alt: v = sqrt(2*g*h) ~ 29.71 m/s",
        section="11",
        stated=math.sqrt(2 * g * h_drop),
        computed=lambda: g * math.sqrt(2 * h_drop / g),
        tolerance=1e-10,
        note="two forms must agree",
    ))

    # RK4 simulation check for free fall
    def _ex1_freefall_rk4():
        h_step = 0.01
        state = np.array([45.0, 0.0])  # [height, velocity] (height decreasing)
        def rhs(s):
            return np.array([s[1], -9.81])  # dy/dt = v, dv/dt = -g (taking down as negative)
        t = 0.0
        while state[0] > 0 and t < 10:
            k1 = rhs(state)
            k2 = rhs(state + h_step/2 * k1)
            k3 = rhs(state + h_step/2 * k2)
            k4 = rhs(state + h_step * k3)
            state = state + h_step/6 * (k1 + 2*k2 + 2*k3 + k4)
            t += h_step
        # t should be close to analytical value
        t_analytical = math.sqrt(2 * 45.0 / 9.81)
        ok = abs(t - t_analytical) < 0.02  # within 20ms (step is 10ms)
        return ok, f"RK4 time = {t:.4f}, analytical = {t_analytical:.4f}"

    ch.add(StructuralCheck(
        label="Ex 11.1: RK4 free fall time matches analytical within 20 ms",
        section="11",
        predicate=_ex1_freefall_rk4,
    ))

    # --- Exercise 11.2: Spring-mass k=50 N/m, m=2 kg ---
    k_ex2, m_ex2, x0_ex2 = 50.0, 2.0, 0.08
    omega_ex2 = math.sqrt(k_ex2 / m_ex2)
    T_ex2 = 2 * math.pi / omega_ex2
    vmax_ex2 = omega_ex2 * x0_ex2  # max velocity = omega * A

    ch.add(NumericCheck(
        label="Ex 11.2: omega = sqrt(50/2) = 5 rad/s",
        section="11",
        stated=5.0,
        computed=lambda: math.sqrt(50.0 / 2.0),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.2: T = 2*pi/5 ~ 1.2566 s",
        section="11",
        stated=2 * math.pi / 5,
        computed=lambda: 2 * math.pi / math.sqrt(50.0 / 2.0),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.2: v_max = omega * x0 = 5 * 0.08 = 0.4 m/s",
        section="11",
        stated=0.4,
        computed=lambda: math.sqrt(50.0 / 2.0) * 0.08,
        tolerance=1e-10,
    ))

    # --- Exercise 11.3: Critically damped oscillator omega=8, gamma=8 ---
    omega_ex3, gamma_ex3 = 8.0, 8.0

    ch.add(NumericCheck(
        label="Ex 11.3: Critically damped eigenvalue: -gamma = -8 (repeated)",
        section="11",
        stated=-8.0,
        computed=lambda: -gamma_ex3,
        tolerance=1e-10,
    ))

    # Companion matrix eigenvalue check
    def _ex3_critical_damp():
        A_comp = np.array([[0, 1], [-omega_ex3**2, -2 * gamma_ex3]], dtype=float)
        evals = np.linalg.eigvals(A_comp)
        # Both eigenvalues should be -8 (repeated root; tiny imaginary part is numerical artifact)
        ok = all(abs(e.real - (-8.0)) < 1e-6 and abs(e.imag) < 1e-4 for e in evals)
        return ok, f"Eigenvalues: {evals.tolist()}, expected [-8, -8]"

    ch.add(StructuralCheck(
        label="Ex 11.3: Companion matrix eigenvalues = [-8, -8] (critically damped)",
        section="11",
        predicate=_ex3_critical_damp,
    ))

    # x(t) = (1 + gamma*t)*exp(-gamma*t) for x(0)=1, x'(0)=0
    # x(0.5) = (1 + 8*0.5)*exp(-8*0.5) = 5*exp(-4)
    ch.add(NumericCheck(
        label="Ex 11.3: x(0.5) = 5*exp(-4) ~ 0.09158",
        section="11",
        stated=5 * math.exp(-4),
        computed=lambda: (1 + 8 * 0.5) * math.exp(-8 * 0.5),
        tolerance=1e-10,
    ))

    # --- Exercise 11.4: 3 masses, 4 springs, k=10 N/m ---
    def _ex4_three_mass():
        k_s = 10.0
        K = np.array([
            [2 * k_s, -k_s, 0],
            [-k_s, 2 * k_s, -k_s],
            [0, -k_s, 2 * k_s],
        ], dtype=float)
        D_mat = K / 1.0  # m = 1 kg
        evals = np.sort(np.linalg.eigvals(D_mat))
        # Analytical eigenvalues for tridiagonal: 2k - 2k*cos(j*pi/(N+1))
        # = 2k*(1 - cos(j*pi/4)) for j=1,2,3
        expected = sorted([
            2 * k_s * (1 - math.cos(j * math.pi / 4))
            for j in range(1, 4)
        ])
        ok = all(abs(evals[i] - expected[i]) / expected[i] < 1e-10 for i in range(3))
        return ok, f"Eigenvalues: {evals.tolist()}, expected: {expected}"

    ch.add(StructuralCheck(
        label="Ex 11.4: 3-mass stiffness matrix eigenvalues match formula",
        section="11",
        predicate=_ex4_three_mass,
    ))

    # Normal mode frequencies
    k_ex4 = 10.0
    ch.add(NumericCheck(
        label="Ex 11.4: omega_1 = sqrt(2k*(1-cos(pi/4))) ~ 2.42 rad/s",
        section="11",
        stated=math.sqrt(2 * k_ex4 * (1 - math.cos(math.pi / 4))),
        computed=lambda: math.sqrt(2 * 10.0 * (1 - math.cos(math.pi / 4))),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.4: omega_2 = sqrt(2k) ~ 4.47 rad/s",
        section="11",
        stated=math.sqrt(2 * k_ex4),
        computed=lambda: math.sqrt(2 * 10.0 * (1 - math.cos(2 * math.pi / 4))),
        tolerance=1e-10,
        note="cos(pi/2) = 0, so eigenvalue = 2k",
    ))

    ch.add(NumericCheck(
        label="Ex 11.4: omega_3 = sqrt(2k*(1+cos(pi/4))) ~ 5.85 rad/s",
        section="11",
        stated=math.sqrt(2 * k_ex4 * (1 + math.cos(math.pi / 4))),
        computed=lambda: math.sqrt(2 * 10.0 * (1 - math.cos(3 * math.pi / 4))),
        tolerance=1e-10,
    ))

    # --- Exercise 11.5: Nonlinear pendulum l=0.5 m, theta0=pi/2 ---
    def _ex5_pendulum():
        l_pend = 0.5
        theta0 = math.pi / 2
        g_local = 9.81
        omega0 = math.sqrt(g_local / l_pend)
        h_step = 0.001
        T_sim = 20.0
        n_steps = int(T_sim / h_step)
        # State: [theta, omega]
        state = np.array([theta0, 0.0])
        def rhs(s):
            return np.array([s[1], -(g_local / l_pend) * math.sin(s[0])])
        E0 = 1.0 * g_local * l_pend * (1 - math.cos(theta0)) + 0.5 * 1.0 * l_pend**2 * 0.0**2
        max_energy_err = 0.0
        zero_crossings = []
        prev_theta = theta0
        for i in range(n_steps):
            k1 = rhs(state)
            k2 = rhs(state + h_step/2 * k1)
            k3 = rhs(state + h_step/2 * k2)
            k4 = rhs(state + h_step * k3)
            state = state + h_step/6 * (k1 + 2*k2 + 2*k3 + k4)
            # Energy check
            E = 1.0 * g_local * l_pend * (1 - math.cos(state[0])) + 0.5 * 1.0 * l_pend**2 * state[1]**2
            rel_err = abs(E - E0) / abs(E0) if E0 != 0 else abs(E)
            max_energy_err = max(max_energy_err, rel_err)
            # Detect downward zero crossings for period
            if prev_theta > 0 and state[0] <= 0 and state[1] < 0:
                zero_crossings.append((i + 1) * h_step)
            prev_theta = state[0]
        # Period from zero-crossing intervals (full period = 2 * half-period)
        if len(zero_crossings) >= 2:
            periods = [zero_crossings[i+1] - zero_crossings[i] for i in range(len(zero_crossings)-1)]
            avg_period = np.mean(periods)
        else:
            return False, "Not enough zero crossings detected"
        # Compare with elliptic integral formula
        T_exact = _nonlinear_pendulum_period_general(theta0, l_pend)
        period_err = abs(avg_period - T_exact) / T_exact
        ok = period_err < 0.01 and max_energy_err < 1e-8
        return ok, f"Period: RK4={avg_period:.4f}s, exact={T_exact:.4f}s, err={period_err:.4e}; energy_err={max_energy_err:.2e}"

    ch.add(StructuralCheck(
        label="Ex 11.5: Pendulum l=0.5m, theta0=pi/2: period and energy check",
        section="11",
        predicate=_ex5_pendulum,
    ))

    # --- Exercise 11.6: Driven oscillator omega=5, gamma=0.5, F0/m=10 ---
    omega_ex6 = 5.0
    gamma_ex6 = 0.5
    F0m_ex6 = 10.0

    ch.add(NumericCheck(
        label="Ex 11.6: Omega_res = sqrt(25 - 0.5) ~ 4.950 rad/s",
        section="11",
        stated=math.sqrt(omega_ex6**2 - 2 * gamma_ex6**2),
        computed=lambda: math.sqrt(25 - 0.5),
        tolerance=1e-10,
    ))

    # A_max = (F0/m)/(2*gamma*omega_d) where omega_d = sqrt(omega^2 - gamma^2)
    omega_d_ex6 = math.sqrt(omega_ex6**2 - gamma_ex6**2)
    ch.add(NumericCheck(
        label="Ex 11.6: A_max = F0m/(2*gamma*omega_d) ~ 2.010",
        section="11",
        stated=F0m_ex6 / (2 * gamma_ex6 * omega_d_ex6),
        computed=lambda: 10.0 / (2 * 0.5 * math.sqrt(25 - 0.25)),
        tolerance=1e-10,
    ))

    # Q-factor
    ch.add(NumericCheck(
        label="Ex 11.6: Q = omega/(2*gamma) = 5/(2*0.5) = 5",
        section="11",
        stated=5.0,
        computed=lambda: 5.0 / (2 * 0.5),
        tolerance=1e-10,
    ))

    # Half-power bandwidth: Delta_Omega ~ omega/Q = 1 rad/s
    ch.add(NumericCheck(
        label="Ex 11.6: Half-power bandwidth Delta_Omega = omega/Q = 1 rad/s",
        section="11",
        stated=1.0,
        computed=lambda: 5.0 / 5.0,
        tolerance=1e-10,
    ))

    # Verify amplitude formula at several driving frequencies
    def _ex6_driven_amplitude():
        omega_0, gam, F0m = 5.0, 0.5, 10.0
        def A_formula(Omega):
            return F0m / math.sqrt((omega_0**2 - Omega**2)**2 + 4 * gam**2 * Omega**2)
        # At resonance
        Om_res = math.sqrt(omega_0**2 - 2 * gam**2)
        A_res = A_formula(Om_res)
        omega_d = math.sqrt(omega_0**2 - gam**2)
        A_max_expected = F0m / (2 * gam * omega_d)
        if abs(A_res - A_max_expected) / A_max_expected > 1e-10:
            return False, f"A(Omega_res)={A_res:.6f} != A_max={A_max_expected:.6f}"
        # Verify amplitude decreases away from resonance
        for Om in [1.0, 3.0, 7.0]:
            if A_formula(Om) > A_res * 1.001:
                return False, f"A({Om})={A_formula(Om):.6f} > A_res={A_res:.6f}"
        return True, ""

    ch.add(StructuralCheck(
        label="Ex 11.6: Driven oscillator amplitude peaks at Omega_res",
        section="11",
        predicate=_ex6_driven_amplitude,
    ))

    # --- Exercise 11.7: String N=16, m=0.005, tau=5, L=0.5 ---
    N_ex7 = 16
    m_ex7 = 0.005
    tau_ex7 = 5.0
    L_ex7 = 0.5
    dx_ex7 = L_ex7 / (N_ex7 + 1)
    c_ex7 = tau_ex7 / dx_ex7

    def _ex7_string_eigenvalues():
        N = 16
        c = tau_ex7 / dx_ex7
        m = m_ex7
        # Build tridiagonal dynamical matrix
        D_mat = np.zeros((N, N))
        for i in range(N):
            D_mat[i, i] = 2 * c / m
            if i > 0:
                D_mat[i, i-1] = -c / m
            if i < N - 1:
                D_mat[i, i+1] = -c / m
        eigs_num = np.sort(np.linalg.eigvals(D_mat))
        # Analytical eigenvalues
        eigs_anal = sorted([
            4 * c / m * math.sin(k * math.pi / (2 * (N + 1)))**2
            for k in range(1, N + 1)
        ])
        max_err = max(abs(eigs_num[i] - eigs_anal[i]) / eigs_anal[i] for i in range(N))
        ok = max_err < 1e-10
        return ok, f"Max relative eigenvalue error: {max_err:.2e}"

    ch.add(StructuralCheck(
        label="Ex 11.7: N=16 string eigenvalues match analytical formula",
        section="11",
        predicate=_ex7_string_eigenvalues,
    ))

    # Third mode frequency
    ch.add(NumericCheck(
        label="Ex 11.7: omega_3 for N=16 string",
        section="11",
        stated=2 * math.sqrt(c_ex7 / m_ex7) * math.sin(3 * math.pi / (2 * (N_ex7 + 1))),
        computed=lambda: 2 * math.sqrt(tau_ex7 / dx_ex7 / m_ex7) * math.sin(3 * math.pi / 34),
        tolerance=1e-10,
    ))

    # --- Exercise 11.8: Coupled pendulums with weak spring ---
    l_ex8 = 1.0
    k_ex8 = 2.0
    d_ex8 = 0.5
    m_ex8 = 1.0
    g_local = 9.81
    kappa = k_ex8 * d_ex8**2 / (m_ex8 * l_ex8**2)  # coupling parameter

    omega1_ex8 = math.sqrt(g_local / l_ex8)
    omega2_ex8 = math.sqrt(g_local / l_ex8 + 2 * kappa)

    ch.add(NumericCheck(
        label="Ex 11.8: omega_1 (symmetric) = sqrt(g/l) ~ 3.132 rad/s",
        section="11",
        stated=3.132,
        computed=lambda: math.sqrt(9.81 / 1.0),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 11.8: omega_2 (antisymmetric) = sqrt(g/l + 2*kd^2/(ml^2)) ~ 3.290 rad/s",
        section="11",
        stated=3.290,
        computed=lambda: math.sqrt(9.81 / 1.0 + 2 * 2.0 * 0.5**2 / (1.0 * 1.0**2)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 11.8: Beat frequency Delta_omega = omega_2 - omega_1 ~ 0.158 rad/s",
        section="11",
        stated=0.158,
        computed=lambda: (
            math.sqrt(9.81 / 1.0 + 2 * 2.0 * 0.25 / 1.0)
            - math.sqrt(9.81 / 1.0)
        ),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 11.8: Beat period T_beat = 2*pi/Delta_omega ~ 39.8 s",
        section="11",
        stated=39.8,
        computed=lambda: 2 * math.pi / (
            math.sqrt(9.81 + 1.0) - math.sqrt(9.81)
        ),
        tolerance=5e-2,
    ))

    # Dynamical matrix eigenvalue check
    def _ex8_coupled_pendulums():
        D_mat = np.array([
            [g_local / l_ex8 + kappa, -kappa],
            [-kappa, g_local / l_ex8 + kappa],
        ], dtype=float)
        evals = np.sort(np.linalg.eigvals(D_mat))
        expected = sorted([g_local / l_ex8, g_local / l_ex8 + 2 * kappa])
        ok = all(abs(evals[i] - expected[i]) < 1e-10 for i in range(2))
        return ok, f"Eigenvalues: {evals.tolist()}, expected: {expected}"

    ch.add(StructuralCheck(
        label="Ex 11.8: Coupled pendulum dynamical matrix eigenvalues",
        section="11",
        predicate=_ex8_coupled_pendulums,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Projectile via RK4 ---
    def alg_5_1_projectile():
        v0, theta = 25.0, math.radians(50)
        g = 9.81
        h = 0.001
        y_state = np.array([0.0, 0.0, v0 * math.cos(theta), v0 * math.sin(theta)])
        def f(y):
            return np.array([y[2], y[3], 0.0, -g])
        t = 0
        while y_state[1] >= 0 or t < 0.1:
            k1 = h * f(y_state)
            k2 = h * f(y_state + k1 / 2)
            k3 = h * f(y_state + k2 / 2)
            k4 = h * f(y_state + k3)
            y_state = y_state + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t += h
            if y_state[1] < 0:
                break
        R_analytical = v0 ** 2 * math.sin(2 * theta) / g
        ok = abs(y_state[0] - R_analytical) < 0.1
        return (ok, f"Range={y_state[0]:.2f}m, analytical={R_analytical:.2f}m")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Projectile trajectory via RK4",
        section="6",
        predicate=alg_5_1_projectile,
    ))

    # --- Algorithm 5.2: Damped Oscillator Classification ---
    def alg_5_2_damped_osc():
        omega, gamma = 10.0, 2.0
        lam_plus = -gamma + np.sqrt(gamma ** 2 - omega ** 2 + 0j)
        lam_minus = -gamma - np.sqrt(gamma ** 2 - omega ** 2 + 0j)
        is_underdamped = np.iscomplex(lam_plus) or abs(np.imag(lam_plus)) > 1e-10
        ok1 = is_underdamped  # gamma=2 < omega=10
        # Simulate
        x, v = 0.1, 0.0
        h_sim = 0.001
        for _ in range(int(5 / h_sim)):
            def f_osc(state):
                return np.array([state[1], -2 * gamma * state[1] - omega ** 2 * state[0]])
            st = np.array([x, v])
            k1 = h_sim * f_osc(st)
            k2 = h_sim * f_osc(st + k1 / 2)
            k3 = h_sim * f_osc(st + k2 / 2)
            k4 = h_sim * f_osc(st + k3)
            st = st + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            x, v = st
        # After 5 seconds with gamma=2, amplitude ~ 0.1*e^{-10} ~ 0
        ok2 = abs(x) < 1e-3
        return (ok1 and ok2, f"Underdamped={is_underdamped}, x(5)={x:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Damped oscillator (underdamped classification and decay)",
        section="6",
        predicate=alg_5_2_damped_osc,
    ))

    # --- Algorithm 5.3: Normal Mode Computation ---
    def alg_5_3_normal_modes():
        # Example 8.3: K = [[8,-2],[-2,6]], M = diag(1,2)
        K = np.array([[8, -2], [-2, 6]], dtype=float)
        M = np.diag([1.0, 2.0])
        D = np.linalg.inv(M) @ K
        eigvals_D = np.sort(np.linalg.eigvals(D))
        omega = np.sqrt(eigvals_D)
        # Expected: lambda1 ~ 2.628, lambda2 ~ 8.372
        disc = math.sqrt(33)
        lam1 = (11 - disc) / 2
        lam2 = (11 + disc) / 2
        ok1 = abs(eigvals_D[0] - lam1) < 1e-6
        ok2 = abs(eigvals_D[1] - lam2) < 1e-6
        return (ok1 and ok2, f"omega={omega}, eigenvalues={eigvals_D}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Normal mode computation (coupled springs)",
        section="6",
        predicate=alg_5_3_normal_modes,
    ))

    # --- Algorithm 5.4: Nonlinear Pendulum with Energy Check ---
    def alg_5_4_pendulum():
        g_val, l = 9.81, 1.0
        theta0 = 2 * math.pi / 3  # 120 degrees
        dtheta0 = 0.0
        h_p = 0.001
        T_end = 10.0
        m_val = 1.0
        E0 = 0.5 * m_val * l ** 2 * dtheta0 ** 2 + m_val * g_val * l * (1 - math.cos(theta0))
        th, dth = theta0, dtheta0
        max_energy_err = 0.0
        for _ in range(int(T_end / h_p)):
            def f_pend(state):
                return np.array([state[1], -(g_val / l) * math.sin(state[0])])
            st = np.array([th, dth])
            k1 = h_p * f_pend(st)
            k2 = h_p * f_pend(st + k1 / 2)
            k3 = h_p * f_pend(st + k2 / 2)
            k4 = h_p * f_pend(st + k3)
            st = st + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            th, dth = st
            E = 0.5 * m_val * l ** 2 * dth ** 2 + m_val * g_val * l * (1 - math.cos(th))
            err = abs(E - E0) / E0
            max_energy_err = max(max_energy_err, err)
        ok = max_energy_err < 1e-6
        return (ok, f"Max energy error: {max_energy_err:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Nonlinear pendulum (energy conservation check)",
        section="6",
        predicate=alg_5_4_pendulum,
    ))

    # --- Algorithm 5.5: Vibrating String with FFT ---
    def alg_5_5_string_fft():
        N = 8
        tau_s = 10.0
        m_s = 0.01
        dx = 1.0 / (N + 1)
        c = tau_s / dx
        # Tridiagonal stiffness matrix
        K = np.zeros((N, N))
        for i in range(N):
            K[i, i] = 2 * c
            if i > 0:
                K[i, i - 1] = -c
            if i < N - 1:
                K[i, i + 1] = -c
        D = K / m_s
        eigvals_K = np.sort(np.linalg.eigvals(D))
        omega_eigen = np.sqrt(np.real(eigvals_K))
        # Analytical: omega_k = 2*sqrt(c/m)*sin(k*pi/(2*(N+1)))
        omega_analytical = [2 * math.sqrt(c / m_s) * math.sin(k * math.pi / (2 * (N + 1)))
                            for k in range(1, N + 1)]
        ok = all(abs(omega_eigen[i] - omega_analytical[i]) < 0.1 for i in range(N))
        return (ok, f"omega_1={omega_eigen[0]:.2f} (analytical {omega_analytical[0]:.2f})")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Vibrating string eigenfrequencies match analytical",
        section="6",
        predicate=alg_5_5_string_fft,
    ))

    # --- Remark 3.4: RK4 free-fall matches analytical solution ---
    def _remark_3_4_freefall_rk4():
        """Verify RK4 on free fall matches y = y0 + v0*t - g*t^2/2."""
        g = 9.81
        y0, v0 = 100.0, 0.0
        dt = 0.01
        t_final = 4.0
        # RK4
        y, v = y0, v0
        t = 0.0
        def dydt(t, y, v): return v
        def dvdt(t, y, v): return -g
        while t < t_final - dt/2:
            k1y = dt * dydt(t, y, v)
            k1v = dt * dvdt(t, y, v)
            k2y = dt * dydt(t + dt/2, y + k1y/2, v + k1v/2)
            k2v = dt * dvdt(t + dt/2, y + k1y/2, v + k1v/2)
            k3y = dt * dydt(t + dt/2, y + k2y/2, v + k2v/2)
            k3v = dt * dvdt(t + dt/2, y + k2y/2, v + k2v/2)
            k4y = dt * dydt(t + dt, y + k3y, v + k3v)
            k4v = dt * dvdt(t + dt, y + k3y, v + k3v)
            y += (k1y + 2*k2y + 2*k3y + k4y) / 6
            v += (k1v + 2*k2v + 2*k3v + k4v) / 6
            t += dt
        y_exact = y0 + v0 * t_final - 0.5 * g * t_final**2
        if abs(y - y_exact) > 1e-6:
            return (False, f"RK4 y={y:.8f}, exact={y_exact:.8f}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: RK4 free-fall matches analytical y = y0 - gt^2/2",
        section="3.4",
        predicate=_remark_3_4_freefall_rk4,
        note="Remark 3.4: RK4 validation on free fall",
    ))

    # --- Remark 3.14: Nonlinear pendulum — RK4 handles near-separatrix ---
    def _remark_3_14_pendulum():
        """Verify nonlinear pendulum: period increases as theta0 -> pi."""
        g_over_L = 9.81
        dt = 0.0001
        periods = []
        for theta0 in [0.1, 0.5, 1.0, 2.0, 3.0]:
            theta, omega = theta0, 0.0
            t = 0.0
            prev_omega = omega
            first_crossing = None
            while t < 200:
                # RK4
                def f_theta(th, om): return om
                def f_omega(th, om): return -g_over_L * math.sin(th)
                k1t = dt * f_theta(theta, omega)
                k1o = dt * f_omega(theta, omega)
                k2t = dt * f_theta(theta + k1t/2, omega + k1o/2)
                k2o = dt * f_omega(theta + k1t/2, omega + k1o/2)
                k3t = dt * f_theta(theta + k2t/2, omega + k2o/2)
                k3o = dt * f_omega(theta + k2t/2, omega + k2o/2)
                k4t = dt * f_theta(theta + k3t, omega + k3o)
                k4o = dt * f_omega(theta + k3t, omega + k3o)
                theta += (k1t + 2*k2t + 2*k3t + k4t) / 6
                omega += (k1o + 2*k2o + 2*k3o + k4o) / 6
                t += dt
                # Detect upward zero-crossings of omega; interval = one period
                if prev_omega < 0 and omega >= 0 and t > 0.1:
                    if first_crossing is None:
                        first_crossing = t
                    else:
                        periods.append(t - first_crossing)
                        break
                prev_omega = omega
            else:
                periods.append(float('inf'))
        # Period should increase with theta0
        for i in range(len(periods) - 1):
            if periods[i+1] <= periods[i] - 0.01:
                return (False, f"Period not increasing: {periods}")
        # Small angle period ~ 2*pi/sqrt(g/L)
        T_linear = 2 * math.pi / math.sqrt(g_over_L)
        if abs(periods[0] - T_linear) / T_linear > 0.01:
            return (False, f"Small angle period {periods[0]:.4f} vs linear {T_linear:.4f}")
        return (True, f"Periods: {[f'{p:.4f}' for p in periods]}")

    ch.add(StructuralCheck(
        label="Remark 3.14: Nonlinear pendulum period increases with amplitude",
        section="3.14",
        predicate=_remark_3_14_pendulum,
        note="Remark 3.14: RK4 replaces elliptic function theory",
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _projectile_range_identity():
    import sympy
    v0, theta, g = sympy.symbols('v0 theta g', positive=True)
    R = v0**2 * sympy.sin(2 * theta) / g
    # At theta=pi/4, range is maximized: R = v0^2/g
    R_max = R.subs(theta, sympy.pi / 4)
    return sympy.Eq(sympy.simplify(R_max), v0**2 / g)


def _sho_period_identity():
    import sympy
    k, m = sympy.symbols('k m', positive=True)
    omega = sympy.sqrt(k / m)
    T = 2 * sympy.pi / omega
    return sympy.Eq(T, 2 * sympy.pi * sympy.sqrt(m / k))


def _damped_eigenvalue_identity():
    import sympy
    gamma, omega, lam = sympy.symbols('gamma omega lambda')
    # Characteristic eq: lam^2 + 2*gamma*lam + omega^2 = 0
    # Root: lam = -gamma +/- sqrt(gamma^2 - omega^2)
    lam_plus = -gamma + sympy.sqrt(gamma**2 - omega**2)
    char_poly = lam_plus**2 + 2 * gamma * lam_plus + omega**2
    return sympy.simplify(char_poly)


def _driven_amplitude_identity():
    """Verify that A(Omega_res) = (F0/m)/(2*gamma*omega_d)."""
    import sympy
    omega, gamma, F0m = sympy.symbols('omega gamma F0m', positive=True)
    omega_d = sympy.sqrt(omega**2 - gamma**2)
    Omega_res = sympy.sqrt(omega**2 - 2 * gamma**2)
    # Amplitude at resonance
    denom_sq = (omega**2 - Omega_res**2)**2 + 4 * gamma**2 * Omega_res**2
    A_res = F0m / sympy.sqrt(denom_sq)
    A_max = F0m / (2 * gamma * omega_d)
    diff = sympy.simplify(A_res - A_max)
    return sympy.Eq(diff, 0)


def _harmonic_energy_identity():
    """Verify E = (1/2)*m*omega^2*A^2 from T+V for x = A*cos(omega*t+phi)."""
    import sympy
    m, A_amp, omega, t, phi = sympy.symbols('m A omega t phi', real=True)
    x = A_amp * sympy.cos(omega * t + phi)
    v = sympy.diff(x, t)
    T_kin = sympy.Rational(1, 2) * m * v**2
    V_pot = sympy.Rational(1, 2) * m * omega**2 * x**2
    E = sympy.simplify(T_kin + V_pot)
    expected = sympy.Rational(1, 2) * m * omega**2 * A_amp**2
    return sympy.Eq(sympy.trigsimp(E), expected)


def _standing_wave_identity():
    """Verify sin(kx)cos(wt) = (1/2)[sin(kx-wt) + sin(kx+wt)]."""
    import sympy
    k, x, omega, t = sympy.symbols('k x omega t', real=True)
    lhs = sympy.sin(k * x) * sympy.cos(omega * t)
    rhs = (sympy.sin(k * x - omega * t) + sympy.sin(k * x + omega * t)) / 2
    return sympy.simplify(lhs - rhs)


def _resonance_frequency_identity():
    """Verify dA/dOmega = 0 at Omega_res = sqrt(omega^2 - 2*gamma^2)."""
    import sympy
    omega, gamma, Omega = sympy.symbols('omega gamma Omega', positive=True)
    # Denominator squared of A(Omega)
    D_sq = (omega**2 - Omega**2)**2 + 4 * gamma**2 * Omega**2
    # d(D_sq)/dOmega = 0 at the maximum of A (minimum of D_sq)
    dD = sympy.diff(D_sq, Omega)
    # Evaluate at Omega_res
    Omega_res = sympy.sqrt(omega**2 - 2 * gamma**2)
    return sympy.simplify(dD.subs(Omega, Omega_res))


def _nonlinear_pendulum_period(theta0):
    from scipy.special import ellipk
    g = 9.81
    l = 1.0
    T0 = 2 * math.pi * math.sqrt(l / g)
    k_param = math.sin(theta0 / 2)
    K = ellipk(k_param**2)
    return 2 * T0 / math.pi * K


def _nonlinear_pendulum_period_general(theta0, l):
    """Nonlinear pendulum period via complete elliptic integral for arbitrary length."""
    from scipy.special import ellipk
    g = 9.81
    T0 = 2 * math.pi * math.sqrt(l / g)
    k_param = math.sin(theta0 / 2)
    K = ellipk(k_param**2)
    return 2 * T0 / math.pi * K


def _coupled_spring_eigenvalue_check():
    D = np.array([[8, -2], [-1, 3]], dtype=float)
    eigs = np.sort(np.linalg.eigvals(D))
    expected = sorted([(11 - math.sqrt(33)) / 2, (11 + math.sqrt(33)) / 2])
    ok = all(abs(eigs[i] - expected[i]) < 1e-10 for i in range(2))
    return ok, f"Computed: {eigs.tolist()}, Expected: {expected}"


def _string_eigenvalue_check():
    N = 8
    tau = 10
    m_mass = 0.01
    dx = 1.0 / 9
    c = tau / dx
    # Build tridiagonal
    K = np.zeros((N, N))
    for i in range(N):
        K[i, i] = 2 * c
        if i > 0:
            K[i, i-1] = -c
        if i < N - 1:
            K[i, i+1] = -c
    D = K / m_mass
    eigs_num = np.sort(np.linalg.eigvals(D))
    # Analytical
    eigs_anal = [4 * c / m_mass * math.sin(k * math.pi / (2 * (N + 1)))**2
                 for k in range(1, N + 1)]
    eigs_anal.sort()
    max_err = max(abs(eigs_num[i] - eigs_anal[i]) / eigs_anal[i] for i in range(N))
    ok = max_err < 1e-10
    return ok, f"Max relative eigenvalue error: {max_err:.2e}"


def _string_eigenvector_check():
    """Verify eigenvector components u_j^(k) = sin(j*k*pi/(N+1)) for the tridiagonal."""
    N = 8
    tau = 10
    m_mass = 0.01
    dx = 1.0 / 9
    c = tau / dx
    # Build tridiagonal dynamical matrix
    D = np.zeros((N, N))
    for i in range(N):
        D[i, i] = 2 * c / m_mass
        if i > 0:
            D[i, i-1] = -c / m_mass
        if i < N - 1:
            D[i, i+1] = -c / m_mass
    # Check each analytical eigenvector
    max_residual = 0.0
    for k in range(1, N + 1):
        lam_k = 4 * c / m_mass * math.sin(k * math.pi / (2 * (N + 1)))**2
        u_k = np.array([math.sin(j * k * math.pi / (N + 1)) for j in range(1, N + 1)])
        # Residual: D*u - lambda*u should be zero
        residual = np.linalg.norm(D @ u_k - lam_k * u_k) / np.linalg.norm(u_k)
        max_residual = max(max_residual, residual)
    ok = max_residual < 1e-10
    return ok, f"Max relative eigenvector residual: {max_residual:.2e}"


def _driven_resonance_peak_check():
    """Verify that A(Omega) is maximal at Omega_res for omega=10, gamma=2."""
    omega, gamma = 10.0, 2.0
    Omega_res = math.sqrt(omega**2 - 2 * gamma**2)

    def amplitude(Om):
        return 1.0 / math.sqrt((omega**2 - Om**2)**2 + 4 * gamma**2 * Om**2)

    A_res = amplitude(Omega_res)
    # Sample around the resonance
    omegas = np.linspace(0.1, 15, 1000)
    A_vals = [amplitude(Om) for Om in omegas]
    A_max_sampled = max(A_vals)
    # The amplitude at Omega_res should be >= any sampled value (within tolerance)
    ok = A_res >= A_max_sampled * 0.9999
    return ok, f"A(Omega_res)={A_res:.6f}, max sampled={A_max_sampled:.6f}"


def _pendulum_period_monotone_check():
    """Verify T(theta0) is strictly increasing for theta0 in (0, pi)."""
    from scipy.special import ellipk
    g = 9.81
    l = 1.0
    T0 = 2 * math.pi * math.sqrt(l / g)
    angles = [math.radians(a) for a in range(5, 176, 5)]
    periods = []
    for th0 in angles:
        k_param = math.sin(th0 / 2)
        K_val = ellipk(k_param**2)
        T = 2 * T0 / math.pi * K_val
        periods.append(T)
    monotone = all(periods[i] < periods[i + 1] for i in range(len(periods) - 1))
    return monotone, f"Periods not strictly increasing; first violation in sequence"


def _damped_stability_check():
    """Verify companion matrix eigenvalues have Re < 0 for various omega, gamma > 0."""
    cases = [(10, 2), (10, 10), (10, 15), (5, 1), (20, 0.5)]
    for omega, gamma in cases:
        A = np.array([[0, 1], [-omega**2, -2 * gamma]], dtype=float)
        evals = np.linalg.eigvals(A)
        if any(e.real >= 0 for e in evals):
            return False, f"Non-negative real part for omega={omega}, gamma={gamma}: {evals}"
    return True, "All eigenvalues have negative real parts"


def _symmetric_pluck_odd_modes_check():
    """Verify symmetric (triangular center-plucked) initial shape has zero projection on even modes."""
    N = 8
    dx = 1.0 / (N + 1)
    # Triangular pluck at center
    u0 = []
    for j in range(1, N + 1):
        if j <= N // 2:
            u0.append(j * dx)
        else:
            u0.append((N + 1 - j) * dx)
    u0 = np.array(u0)
    # Project onto each mode
    max_even_coeff = 0.0
    min_odd_coeff = float('inf')
    for k in range(1, N + 1):
        mode = np.array([math.sin(j * k * math.pi / (N + 1)) for j in range(1, N + 1)])
        coeff = abs(np.dot(u0, mode))
        if k % 2 == 0:
            max_even_coeff = max(max_even_coeff, coeff)
        else:
            min_odd_coeff = min(min_odd_coeff, coeff)
    ok = max_even_coeff < 1e-14 and min_odd_coeff > 1e-4
    return ok, f"Max even mode coeff: {max_even_coeff:.2e}, min odd mode coeff: {min_odd_coeff:.2e}"


def _energy_conservation_check():
    """Verify harmonic oscillator energy is exactly constant: E = (1/2)*k*A^2."""
    omega = 10.0
    A = 0.1
    m = 1.0
    k = m * omega**2
    # Sample at many time points
    times = np.linspace(0, 10, 10000)
    E_expected = 0.5 * k * A**2
    max_err = 0.0
    for t in times:
        x = A * math.cos(omega * t)
        v = -A * omega * math.sin(omega * t)
        E = 0.5 * m * v**2 + 0.5 * k * x**2
        err = abs(E - E_expected) / E_expected
        max_err = max(max_err, err)
    ok = max_err < 1e-12
    return ok, f"Max relative energy error: {max_err:.2e}"
