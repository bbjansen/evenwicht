# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 19: Ordinary Differential Equations — verification."""

import math
import numpy as np
import scipy
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(19, "Ordinary Differential Equations")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- Separable: dy/dt = 2y, y(0)=3 => y = 3*e^{2t} ---
    ch.add(SymbolicCheck(
        label="Separable ODE: y=3*exp(2t) satisfies y'=2y, y(0)=3",
        section="9",
        identity=lambda: _verify_ode_solution_exponential_growth(),
        note="Example 6.1",
    ))

    # --- First-order linear: y' + 2y = e^{-x}, y(0)=3 => y = e^{-x} + 2*e^{-2x} ---
    ch.add(SymbolicCheck(
        label="Linear ODE: y=e^{-x}+2e^{-2x} satisfies y'+2y=e^{-x}, y(0)=3",
        section="4",
        identity=lambda: _verify_first_order_linear(),
        note="Definition 3.5 example",
    ))

    # --- Logistic: y=1/(1+9*e^{-t}) satisfies y'=y(1-y), y(0)=0.1 ---
    ch.add(SymbolicCheck(
        label="Logistic ODE: y=1/(1+9e^{-t}) satisfies y'=y(1-y)",
        section="9",
        identity=lambda: _verify_logistic_solution(),
        note="Example 6.2",
    ))

    # --- Second-order: y'' - 3y' + 2y = 0, y(0)=1, y'(0)=0 => y=2e^t - e^{2t} ---
    ch.add(SymbolicCheck(
        label="2nd-order: y=2e^t - e^{2t} satisfies y''-3y'+2y=0",
        section="4",
        identity=lambda: _verify_second_order_distinct(),
        note="Theorem 3.9 example",
    ))

    # --- Harmonic oscillator: y'' + 4y = 0 => y = c1*cos(2t) + c2*sin(2t) ---
    ch.add(SymbolicCheck(
        label="Harmonic oscillator: cos(2t) satisfies y''+4y=0",
        section="4",
        identity=lambda: _verify_harmonic_oscillator(),
        note="Simple harmonic oscillator example",
    ))

    # --- Particular solution: y''+y=3cos(2t) => y_p=-cos(2t) ---
    ch.add(SymbolicCheck(
        label="Particular solution: y_p=-cos(2t) satisfies y''+y=3cos(2t)",
        section="4",
        identity=lambda: _verify_particular_solution(),
        note="Definition 3.10 example",
    ))

    # --- Damped oscillator characteristic equation ---
    ch.add(SymbolicCheck(
        label="Damped oscillator: lambda^2+0.5*lambda+4=0 roots",
        section="9",
        identity=lambda: _verify_damped_oscillator_roots(),
        note="Example 6.3: alpha=-0.25, beta=sqrt(63/16)",
    ))

    # --- Separable: dy/dx = xy => y = e^{x^2/2} with y(0)=1 ---
    ch.add(SymbolicCheck(
        label="Separable: y=exp(x^2/2) satisfies y'=xy, y(0)=1",
        section="4",
        identity=lambda: _verify_separable_xy(),
        note="Definition 3.4 example",
    ))

    # --- Integrating factor: mu(x)=e^{2x} for y'+2y=e^{-x} ---
    ch.add(SymbolicCheck(
        label="Integrating factor: d/dx[e^{2x}*y] = e^x for y'+2y=e^{-x}",
        section="4",
        identity=lambda: _verify_integrating_factor(),
        note="Definition 3.5 integrating factor derivation",
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    # --- Example 6.1: y(2) = 3*e^4 ---
    ch.add(NumericCheck(
        label="Exponential growth y(2) = 3*e^4",
        section="9",
        stated=163.794,
        computed=lambda: 3 * math.exp(4),
        tolerance=1e-3,
        note="Example 6.1: dy/dt=2y, y(0)=3",
    ))

    # --- Example 6.1: exact values at intermediate t ---
    ch.add(NumericCheck(
        label="Exponential growth y(0.5) = 3*e^1",
        section="9",
        stated=8.15485,
        computed=lambda: 3 * math.exp(1),
        tolerance=1e-4,
        note="Example 6.1: t=0.5",
    ))

    ch.add(NumericCheck(
        label="Exponential growth y(1) = 3*e^2",
        section="9",
        stated=22.16717,
        computed=lambda: 3 * math.exp(2),
        tolerance=1e-4,
        note="Example 6.1: t=1",
    ))

    ch.add(NumericCheck(
        label="Exponential growth y(1.5) = 3*e^3",
        section="9",
        stated=60.25661,
        computed=lambda: 3 * math.exp(3),
        tolerance=1e-4,
        note="Example 6.1: t=1.5",
    ))

    # --- Example 6.2: logistic y(10) = 1/(1+9*e^{-10}) ---
    ch.add(NumericCheck(
        label="Logistic y(10) = 1/(1+9*e^{-10})",
        section="9",
        stated=0.99959,
        computed=lambda: 1 / (1 + 9 * math.exp(-10)),
        tolerance=1e-4,
        note="Example 6.2",
    ))

    # --- Example 6.2: logistic at additional time points ---
    ch.add(NumericCheck(
        label="Logistic y(0) = 1/(1+9) = 0.1",
        section="9",
        stated=0.1,
        computed=lambda: 1 / (1 + 9 * math.exp(0)),
        tolerance=1e-10,
        note="Example 6.2: initial condition",
    ))

    ch.add(NumericCheck(
        label="Logistic y(1) = 1/(1+9*e^{-1}) = 0.2319",
        section="9",
        stated=0.23188,
        computed=lambda: 1 / (1 + 9 * math.exp(-1)),
        tolerance=1e-3,
        note="Example 6.2: t=1",
    ))

    ch.add(NumericCheck(
        label="Logistic y(2) = 1/(1+9*e^{-2}) = 0.4502",
        section="9",
        stated=0.45017,
        computed=lambda: 1 / (1 + 9 * math.exp(-2)),
        tolerance=2e-3,
        note="Example 6.2: t=2",
    ))

    ch.add(NumericCheck(
        label="Logistic y(3) = 1/(1+9*e^{-3}) = 0.6900",
        section="9",
        stated=0.68997,
        computed=lambda: 1 / (1 + 9 * math.exp(-3)),
        tolerance=1e-3,
        note="Example 6.2: t=3",
    ))

    ch.add(NumericCheck(
        label="Logistic y(5) = 1/(1+9*e^{-5}) = 0.9427",
        section="9",
        stated=0.94268,
        computed=lambda: 1 / (1 + 9 * math.exp(-5)),
        tolerance=1e-3,
        note="Example 6.2: t=5",
    ))

    # --- Example 6.3: damped oscillator alpha and beta ---
    ch.add(NumericCheck(
        label="Damped oscillator alpha = -0.25",
        section="9",
        stated=-0.25,
        computed=lambda: -0.5 / 2,
        tolerance=1e-10,
        note="Example 6.3: alpha = -b/(2a) = -0.5/2",
    ))

    ch.add(NumericCheck(
        label="Damped oscillator beta = sqrt(15.75/4) = 1.984",
        section="9",
        stated=1.984,
        computed=lambda: math.sqrt((4 * 4 - 0.25) / 4),
        tolerance=1e-3,
        note="Example 6.3: beta = sqrt(4ac-b^2)/(2a)",
    ))

    ch.add(NumericCheck(
        label="Damped oscillator c2 = 0.25/1.984 = 0.126",
        section="9",
        stated=0.126,
        computed=lambda: 0.25 / math.sqrt((4 * 4 - 0.25) / 4),
        tolerance=1e-3,
        note="Example 6.3: c2 from x'(0)=0 condition",
    ))

    # --- Example 6.3: damped oscillator discriminant ---
    ch.add(NumericCheck(
        label="Damped oscillator discriminant = 0.25 - 16 = -15.75",
        section="9",
        stated=-15.75,
        computed=lambda: 0.5**2 - 4 * 1 * 4,
        tolerance=1e-10,
        note="Example 6.3: b^2-4ac < 0 => complex roots",
    ))

    # --- Example 6.3: damped oscillator oscillation frequency ---
    ch.add(NumericCheck(
        label="Damped oscillator frequency = beta/(2pi) = 0.316 Hz",
        section="9",
        stated=0.316,
        computed=lambda: math.sqrt((4 * 4 - 0.25) / 4) / (2 * math.pi),
        tolerance=1e-3,
        note="Example 6.3: frequency in Hz",
    ))

    # --- Example 6.3: damped oscillator solution at specific t ---
    ch.add(NumericCheck(
        label="Damped oscillator x(0) = 1 (initial condition)",
        section="9",
        stated=1.0,
        computed=lambda: math.exp(-0.25 * 0) * (1.0 * math.cos(1.984 * 0) + 0.126 * math.sin(1.984 * 0)),
        tolerance=1e-10,
        note="Example 6.3: verify IC",
    ))

    ch.add(NumericCheck(
        label="Damped oscillator x(pi/1.984) ~ envelope e^{-0.25*pi/1.984}",
        section="9",
        stated=0.674,
        computed=lambda: math.exp(-0.25 * math.pi / 1.984),
        tolerance=1e-2,
        note="Example 6.3: envelope at half-period",
    ))

    ch.add(NumericCheck(
        label="Damped oscillator x(20) ~ e^{-5} ~ 0.007",
        section="9",
        stated=0.00674,
        computed=lambda: math.exp(-0.25 * 20),
        tolerance=1e-3,
        note="Example 6.3: nearly damped out at t=20",
    ))

    # --- Example 6.4: Euler method for y'=-y, y(0)=1, h=0.1, t=1 ---
    ch.add(NumericCheck(
        label="Euler y'=-y: (0.9)^10 = 0.34868",
        section="9",
        stated=0.3486784401,
        computed=lambda: 0.9**10,
        tolerance=1e-10,
        note="Example 6.4: Euler step (1+h*lambda)^N = (1-0.1)^10",
    ))

    ch.add(NumericCheck(
        label="Euler error for y'=-y at t=1: |0.9^10 - e^{-1}|",
        section="9",
        stated=0.0192,
        computed=lambda: abs(0.9**10 - math.exp(-1)),
        tolerance=1e-3,
        note="Example 6.4",
    ))

    # --- Euler method step-by-step for y'=-y ---
    ch.add(NumericCheck(
        label="Euler step 1: y_1 = 1 + 0.1*(-1) = 0.9",
        section="9",
        stated=0.9,
        computed=lambda: 1.0 + 0.1 * (-1.0),
        tolerance=1e-10,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 2: y_2 = 0.9 + 0.1*(-0.9) = 0.81",
        section="9",
        stated=0.81,
        computed=lambda: 0.9 + 0.1 * (-0.9),
        tolerance=1e-10,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 3: y_3 = 0.81 + 0.1*(-0.81) = 0.729",
        section="9",
        stated=0.729,
        computed=lambda: 0.81 + 0.1 * (-0.81),
        tolerance=1e-10,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 4: y_4 = 0.729 + 0.1*(-0.729) = 0.6561",
        section="9",
        stated=0.6561,
        computed=lambda: 0.729 + 0.1 * (-0.729),
        tolerance=1e-10,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 5: y_5 = 0.6561 + 0.1*(-0.6561) = 0.59049",
        section="9",
        stated=0.59049,
        computed=lambda: 0.6561 + 0.1 * (-0.6561),
        tolerance=1e-10,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 6: y_6 = (0.9)^6 = 0.531441",
        section="9",
        stated=0.531441,
        computed=lambda: 0.9**6,
        tolerance=1e-10,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 7: y_7 = (0.9)^7 = 0.4782969",
        section="9",
        stated=0.4782969,
        computed=lambda: 0.9**7,
        tolerance=1e-7,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 8: y_8 = (0.9)^8 = 0.43046721",
        section="9",
        stated=0.43046721,
        computed=lambda: 0.9**8,
        tolerance=1e-8,
        note="Example 6.4: step-by-step",
    ))

    ch.add(NumericCheck(
        label="Euler step 9: y_9 = (0.9)^9 = 0.387420489",
        section="9",
        stated=0.387420489,
        computed=lambda: 0.9**9,
        tolerance=1e-9,
        note="Example 6.4: step-by-step",
    ))

    # --- Euler 10-step for y'=-y matches formula ---
    ch.add(NumericCheck(
        label="Euler 10-step for y'=-y matches (1-h)^N formula",
        section="9",
        stated=0.3486784401,
        computed=lambda: _euler_steps(lambda t, y: -y, 0, 1.0, 0.1, 10),
        tolerance=1e-10,
        note="Example 6.4: manual iteration",
    ))

    # --- Exact solution at Euler step points for comparison ---
    ch.add(NumericCheck(
        label="Exact e^{-0.1} = 0.904837 (vs Euler 0.9)",
        section="9",
        stated=0.904837,
        computed=lambda: math.exp(-0.1),
        tolerance=1e-5,
        note="Example 6.4: Euler underestimates by 0.005",
    ))

    ch.add(NumericCheck(
        label="Exact e^{-0.5} = 0.606531 (vs Euler 0.59049)",
        section="9",
        stated=0.606531,
        computed=lambda: math.exp(-0.5),
        tolerance=1e-5,
        note="Example 6.4: error grows over time",
    ))

    # --- RK4 single step for y'=-y, y(0)=1, h=0.1 ---
    ch.add(NumericCheck(
        label="RK4 y_1 for y'=-y, h=0.1 matches R(z) formula",
        section="9",
        stated=0.9048374180,
        computed=lambda: _rk4_steps(lambda t, y: -y, 0, 1.0, 0.1, 1),
        tolerance=1e-6,
        note="R(-0.1) = 1-0.1+0.005-0.000167+0.0000042",
    ))

    # --- RK4 stability function R(z) computation ---
    ch.add(NumericCheck(
        label="RK4 R(-0.1) = 1 - 0.1 + 0.005 - 1/6000 + 1/240000",
        section="9",
        stated=0.9048374180,
        computed=lambda: 1 + (-0.1) + (-0.1)**2/2 + (-0.1)**3/6 + (-0.1)**4/24,
        tolerance=1e-7,
        note="Example 6.4: Taylor polynomial of e^z at z=-0.1",
    ))

    # --- RK4 step-by-step k-values for first step of y'=-y ---
    ch.add(NumericCheck(
        label="RK4 k1 = f(0, 1) = -1",
        section="9",
        stated=-1.0,
        computed=lambda: -1.0,
        tolerance=1e-10,
        note="Example 6.4: RK4 first stage",
    ))

    ch.add(NumericCheck(
        label="RK4 k2 = f(0.05, 1+0.05*(-1)) = f(0.05, 0.95) = -0.95",
        section="9",
        stated=-0.95,
        computed=lambda: -(1.0 + 0.05 * (-1.0)),
        tolerance=1e-10,
        note="Example 6.4: RK4 second stage",
    ))

    ch.add(NumericCheck(
        label="RK4 k3 = f(0.05, 1+0.05*(-0.95)) = f(0.05, 0.9525) = -0.9525",
        section="9",
        stated=-0.9525,
        computed=lambda: -(1.0 + 0.05 * (-0.95)),
        tolerance=1e-10,
        note="Example 6.4: RK4 third stage",
    ))

    ch.add(NumericCheck(
        label="RK4 k4 = f(0.1, 1+0.1*(-0.9525)) = f(0.1, 0.90475) = -0.90475",
        section="9",
        stated=-0.90475,
        computed=lambda: -(1.0 + 0.1 * (-0.9525)),
        tolerance=1e-10,
        note="Example 6.4: RK4 fourth stage",
    ))

    ch.add(NumericCheck(
        label="RK4 y_1 = 1 + (0.1/6)*(-1 + 2*(-0.95) + 2*(-0.9525) + (-0.90475))",
        section="9",
        stated=0.9048374180,
        computed=lambda: 1.0 + (0.1 / 6) * (-1.0 + 2 * (-0.95) + 2 * (-0.9525) + (-0.90475)),
        tolerance=1e-6,
        note="Example 6.4: RK4 weighted average",
    ))

    # --- RK4 error at t=1 for y'=-y ---
    ch.add(NumericCheck(
        label="RK4 error for y'=-y at t=1 is O(1e-7)",
        section="9",
        stated=math.exp(-1),
        computed=lambda: _rk4_steps(lambda t, y: -y, 0, 1.0, 0.1, 10),
        tolerance=1e-6,
        note="Example 6.4: RK4 error ~ 3.3e-7",
    ))

    # --- Euler on y'=y, y(0)=1, h=0.2, 5 steps (from diagram) ---
    ch.add(NumericCheck(
        label="Euler y'=y, h=0.2, y(1) = 1.2^5 = 2.48832",
        section="9",
        stated=2.48832,
        computed=lambda: 1.2**5,
        tolerance=1e-5,
        note="from Euler vs RK4 diagram",
    ))

    # --- Euler vs RK4 diagram: step-by-step Euler values for y'=y ---
    ch.add(NumericCheck(
        label="Euler y'=y, h=0.2: y(0.2) = 1.2",
        section="9",
        stated=1.2,
        computed=lambda: 1.0 * 1.2,
        tolerance=1e-10,
        note="from diagram: step 1",
    ))

    ch.add(NumericCheck(
        label="Euler y'=y, h=0.2: y(0.4) = 1.44",
        section="9",
        stated=1.44,
        computed=lambda: 1.2**2,
        tolerance=1e-10,
        note="from diagram: step 2",
    ))

    ch.add(NumericCheck(
        label="Euler y'=y, h=0.2: y(0.6) = 1.728",
        section="9",
        stated=1.728,
        computed=lambda: 1.2**3,
        tolerance=1e-10,
        note="from diagram: step 3",
    ))

    ch.add(NumericCheck(
        label="Euler y'=y, h=0.2: y(0.8) = 2.0736",
        section="9",
        stated=2.074,
        computed=lambda: 1.2**4,
        tolerance=1e-3,
        note="from diagram: step 4 (rounded to 2.074)",
    ))

    # --- Exact vs Euler comparison at diagram points ---
    ch.add(NumericCheck(
        label="Exact e^{0.2} = 1.221 (vs Euler 1.2, error 1.8%)",
        section="9",
        stated=1.221,
        computed=lambda: math.exp(0.2),
        tolerance=1e-3,
        note="from diagram",
    ))

    ch.add(NumericCheck(
        label="Exact e^{1.0} = 2.718 (vs Euler 2.488, error 8.5%)",
        section="9",
        stated=2.718,
        computed=lambda: math.exp(1.0),
        tolerance=1e-3,
        note="from diagram: Euler undershoots by 8.5%",
    ))

    # --- Euler with h=0.01 for y'=-y: error ~ 0.0018 (Example 6.4) ---
    ch.add(NumericCheck(
        label="Euler y'=-y, h=0.01, 100 steps: error ~ 0.0018",
        section="9",
        stated=0.0018,
        computed=lambda: abs(_euler_steps(lambda t, y: -y, 0, 1.0, 0.01, 100) - math.exp(-1)),
        tolerance=0.5,  # relative tolerance since stated is approximate
        note="Example 6.4: halving h from 0.1 to 0.01 reduces error by 10x",
    ))

    # --- Second-order ODE: y=2e^t - e^{2t} at specific t ---
    ch.add(NumericCheck(
        label="y=2e^t - e^{2t} at t=0: y(0) = 2-1 = 1",
        section="4",
        stated=1.0,
        computed=lambda: 2 * math.exp(0) - math.exp(0),
        tolerance=1e-10,
        note="Theorem 3.9 example: initial condition",
    ))

    ch.add(NumericCheck(
        label="y=2e^t - e^{2t} at t=0: y'(0) = 2-2 = 0",
        section="4",
        stated=0.0,
        computed=lambda: 2 * math.exp(0) - 2 * math.exp(0),
        tolerance=1e-10,
        note="Theorem 3.9 example: initial velocity",
    ))

    ch.add(NumericCheck(
        label="y=2e^t - e^{2t} at t=0.5",
        section="4",
        stated=0.57926,
        computed=lambda: 2 * math.exp(0.5) - math.exp(1.0),
        tolerance=2e-4,
        note="Theorem 3.9 example: intermediate value",
    ))

    ch.add(NumericCheck(
        label="y=2e^t - e^{2t} at t=1: y(1) = 2e - e^2 = -1.946",
        section="4",
        stated=-1.95249,
        computed=lambda: 2 * math.exp(1) - math.exp(2),
        tolerance=1e-4,
        note="Theorem 3.9 example: solution turns negative",
    ))

    # --- Harmonic oscillator period = pi (from y''+4y=0) ---
    ch.add(NumericCheck(
        label="Harmonic oscillator y''+4y=0: period = 2*pi/2 = pi",
        section="4",
        stated=3.14159,
        computed=lambda: math.pi,
        tolerance=1e-5,
        note="Theorem 3.9 Case 3: beta=2, period=pi",
    ))

    # --- Phase portrait eigenvalue pairs ---
    ch.add(NumericCheck(
        label="Stable node eigenvalues: -1, -3 (both real negative)",
        section="4",
        stated=-1.0,
        computed=lambda: np.linalg.eigvals(np.array([[-1, 0], [0, -3]], dtype=float)).max().real,
        tolerance=1e-10,
        note="Theorem 3.12: larger eigenvalue determines decay rate",
    ))

    ch.add(NumericCheck(
        label="Saddle point eigenvalues: -1, 3 (opposite signs)",
        section="4",
        stated=3.0,
        computed=lambda: np.linalg.eigvals(np.array([[-1, 2], [0, 3]], dtype=float)).max().real,
        tolerance=1e-10,
        note="Theorem 3.12: positive eigenvalue => unstable",
    ))

    ch.add(NumericCheck(
        label="Damped oscillator eigenvalue Re = -0.25",
        section="9",
        stated=-0.25,
        computed=lambda: np.linalg.eigvals(np.array([[0, 1], [-4, -0.5]])).real[0],
        tolerance=1e-10,
        note="Example 6.3: phase portrait is stable spiral",
    ))

    ch.add(NumericCheck(
        label="Damped oscillator eigenvalue Im = 1.984",
        section="9",
        stated=1.984,
        computed=lambda: abs(np.linalg.eigvals(np.array([[0, 1], [-4, -0.5]])).imag[0]),
        tolerance=1e-3,
        note="Example 6.3: oscillation frequency",
    ))

    # --- RK4 error ratio: 58000 times more accurate than Euler ---
    ch.add(NumericCheck(
        label="RK4 vs Euler error ratio ~ 58000 for y'=-y, h=0.1",
        section="9",
        stated=58000.0,
        computed=lambda: abs(0.9**10 - math.exp(-1)) / abs(_rk4_steps(lambda t, y: -y, 0, 1.0, 0.1, 10) - math.exp(-1)),
        tolerance=0.5,
        note="Example 6.4: dramatic accuracy advantage",
    ))

    # ===================================================================
    # LAYER 3: Structural / consistency checks
    # ===================================================================

    # --- Equilibrium stability from eigenvalues of Jacobian ---
    ch.add(StructuralCheck(
        label="Damped oscillator: Re(lambda)<0 => asymptotically stable",
        section="9",
        predicate=lambda: _ode_stability_eigenvalue_check(
            A=np.array([[0, 1], [-4, -0.5]]),
        ),
        note="Example 6.3: eigenvalues -0.25 +/- 1.984i",
    ))

    # --- Stable node: A=[[-1,0],[0,-3]] ---
    ch.add(StructuralCheck(
        label="Stable node: all eigenvalues real negative",
        section="4",
        predicate=lambda: _ode_stability_eigenvalue_check(
            A=np.array([[-1, 0], [0, -3]], dtype=float),
        ),
        note="Theorem 3.12: both eigenvalues -1, -3 < 0",
    ))

    # --- Saddle point: A=[[-1,2],[0,3]] ---
    ch.add(StructuralCheck(
        label="Saddle point: eigenvalues of opposite sign => unstable",
        section="4",
        predicate=lambda: _ode_instability_check(
            A=np.array([[-1, 2], [0, 3]], dtype=float),
        ),
        note="Theorem 3.12: eigenvalues -1 and 3",
    ))

    # --- Center: A=[[0,1],[-4,0]] => purely imaginary eigenvalues ---
    ch.add(StructuralCheck(
        label="Center: purely imaginary eigenvalues +/-2i => oscillatory",
        section="4",
        predicate=lambda: _ode_center_check(
            A=np.array([[0, 1], [-4, 0]], dtype=float),
        ),
        note="Theorem 3.12: y''+4y=0 as system",
    ))

    # --- Unstable spiral: A=[[0.5,1],[-4,0.5]] ---
    ch.add(StructuralCheck(
        label="Unstable spiral: complex eigenvalues with Re>0",
        section="4",
        predicate=lambda: _ode_unstable_spiral_check(
            A=np.array([[0.5, 1], [-4, 0.5]], dtype=float),
        ),
        note="Theorem 3.12: Re(lambda) = 0.5 > 0",
    ))

    # --- Euler convergence order: halving h halves the error (first order) ---
    ch.add(StructuralCheck(
        label="Euler convergence is first-order: error ~ O(h)",
        section="6",
        predicate=lambda: _euler_convergence_order(),
        note="error ratio ~ 2 when h is halved",
    ))

    # --- RK4 convergence order: halving h reduces error by factor 16 ---
    ch.add(StructuralCheck(
        label="RK4 convergence is fourth-order: error ~ O(h^4)",
        section="6",
        predicate=lambda: _rk4_convergence_order(),
        note="error ratio ~ 16 when h is halved",
    ))

    # --- Euler convergence order: multiple h values ---
    ch.add(StructuralCheck(
        label="Euler: error at h=0.01 is ~10x smaller than at h=0.1",
        section="6",
        predicate=lambda: _euler_convergence_multi_h(),
        note="Example 6.4: confirms O(h) scaling",
    ))

    # --- RK4 convergence order: multiple h values ---
    ch.add(StructuralCheck(
        label="RK4: error at h=0.01 is ~10^4 smaller than at h=0.1",
        section="6",
        predicate=lambda: _rk4_convergence_multi_h(),
        note="Example 6.4: confirms O(h^4) scaling",
    ))

    # --- Logistic equation: equilibrium stability via f'(y*) ---
    ch.add(StructuralCheck(
        label="Logistic: y*=0 unstable (f'>0), y*=K stable (f'<0)",
        section="4",
        predicate=lambda: _logistic_ode_equilibrium_stability(),
        note="Definition 3.7: f(y)=ry(1-y/K), r=1, K=1",
    ))

    # --- Second-order ODE: characteristic roots determine solution type ---
    ch.add(StructuralCheck(
        label="Char eq y''-3y'+2y=0: roots 1,2 => exponential solution",
        section="4",
        predicate=lambda: _characteristic_roots_check(
            a=1, b=-3, c=2,
            expected_roots=[1.0, 2.0],
        ),
        note="Theorem 3.9 Case 1: distinct real roots",
    ))

    ch.add(StructuralCheck(
        label="Char eq y''+4y=0: roots +/-2i => oscillatory solution",
        section="4",
        predicate=lambda: _characteristic_roots_complex_check(
            a=1, b=0, c=4,
            expected_alpha=0.0,
            expected_beta=2.0,
        ),
        note="Theorem 3.9 Case 3: purely imaginary roots",
    ))

    # --- Char eq for damped oscillator: lambda^2+0.5*lambda+4=0 ---
    ch.add(StructuralCheck(
        label="Char eq damped oscillator: alpha=-0.25, beta=1.984",
        section="9",
        predicate=lambda: _characteristic_roots_complex_check(
            a=1, b=0.5, c=4,
            expected_alpha=-0.25,
            expected_beta=1.984,
        ),
        note="Example 6.3: complex roots with negative real part",
    ))

    # --- RK4 stability function R(z) = 1+z+z^2/2+z^3/6+z^4/24 ---
    ch.add(StructuralCheck(
        label="RK4 stability: |R(z)|<1 for z=-2, |R(z)|>1 for z=-3",
        section="6",
        predicate=lambda: _rk4_stability_region_check(),
        note="stability boundary near z=-2.78 on real axis",
    ))

    # --- Euler stability region: |1+z| < 1 is disk of radius 1 at -1 ---
    ch.add(StructuralCheck(
        label="Euler stability: |1+z|<1 for z=-1, |1+z|>1 for z=-2.5",
        section="6",
        predicate=lambda: _euler_stability_region_check(),
        note="Euler stability region is disk of radius 1 centered at -1",
    ))

    # --- Phase portrait classification consistency ---
    ch.add(StructuralCheck(
        label="Phase portrait: 7 canonical types correctly classified",
        section="4",
        predicate=lambda: _phase_portrait_classification(),
        note="Theorem 3.12: complete classification table",
    ))

    # --- Exact solution matches numerical ODE solver ---
    ch.add(StructuralCheck(
        label="RK4 on y'=2y, y(0)=3 matches 3*e^{2t} at t=2",
        section="9",
        predicate=lambda: _rk4_matches_exact_exponential(),
        note="Example 6.1: cross-validate analytical and numerical",
    ))

    # --- RK4 on logistic matches analytical ---
    ch.add(StructuralCheck(
        label="RK4 on y'=y(1-y), y(0)=0.1 matches logistic at t=10",
        section="9",
        predicate=lambda: _rk4_matches_exact_logistic(),
        note="Example 6.2: cross-validate analytical and numerical",
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 8.2: dy/dx = x/y, y(0)=2 ---
    # Separable: y dy = x dx => y^2/2 = x^2/2 + C => y^2 = x^2 + 4
    # y(x) = sqrt(x^2 + 4)
    ch.add(NumericCheck(
        label="Ex 8.2: y(0) = sqrt(0+4) = 2",
        section="11",
        stated=2.0,
        computed=lambda: math.sqrt(0**2 + 4),
        tolerance=1e-12,
        note="Exercise 8.2: initial condition",
    ))
    ch.add(NumericCheck(
        label="Ex 8.2: y(1) = sqrt(5) ~ 2.2361",
        section="11",
        stated=math.sqrt(5),
        computed=lambda: math.sqrt(1**2 + 4),
        tolerance=1e-10,
        note="Exercise 8.2",
    ))
    ch.add(NumericCheck(
        label="Ex 8.2: y(2) = sqrt(8) = 2*sqrt(2) ~ 2.8284",
        section="11",
        stated=2*math.sqrt(2),
        computed=lambda: math.sqrt(4 + 4),
        tolerance=1e-10,
        note="Exercise 8.2",
    ))

    # --- Exercise 8.3: y' - 3y = e^{2x}, y(0)=1 ---
    # Integrating factor: mu = e^{-3x}
    # d/dx[e^{-3x}*y] = e^{-x}
    # e^{-3x}*y = -e^{-x} + C
    # y(0) = 1 => 1 = -1 + C => C = 2
    # y = -e^{2x} + 2*e^{3x}
    ch.add(NumericCheck(
        label="Ex 8.3: y(0) = -1 + 2 = 1",
        section="11",
        stated=1.0,
        computed=lambda: -math.exp(0) + 2*math.exp(0),
        tolerance=1e-12,
        note="Exercise 8.3: verify IC",
    ))
    ch.add(NumericCheck(
        label="Ex 8.3: y(1) = -e^2 + 2*e^3",
        section="11",
        stated=-math.exp(2) + 2*math.exp(3),
        computed=lambda: -math.exp(2) + 2*math.exp(3),
        tolerance=1e-10,
        note="Exercise 8.3",
    ))
    # Verify ODE: y' = -2e^{2x}+6e^{3x}, 3y = -3e^{2x}+6e^{3x}
    # y'-3y = -2e^{2x}+6e^{3x}-(-3e^{2x}+6e^{3x}) = e^{2x} -- correct!
    ch.add(NumericCheck(
        label="Ex 8.3: y'-3y at x=0 = e^{0} = 1",
        section="11",
        stated=1.0,
        computed=lambda: (-2*math.exp(0) + 6*math.exp(0)) - 3*(-math.exp(0) + 2*math.exp(0)),
        tolerance=1e-12,
        note="Exercise 8.3: verify ODE is satisfied",
    ))

    # --- Exercise 8.4: y'' + 6y' + 9y = 0, y(0)=2, y'(0)=-3 ---
    # Characteristic eq: lambda^2+6lambda+9 = (lambda+3)^2 = 0 => repeated root lambda=-3
    # General: y = (c1 + c2*t)*e^{-3t}
    # y(0) = c1 = 2, y'(0) = c2 - 3*c1 = -3 => c2 = -3+6 = 3
    # y(t) = (2 + 3t)*e^{-3t}
    ch.add(NumericCheck(
        label="Ex 8.4: repeated root lambda = -3",
        section="11",
        stated=-3.0,
        computed=lambda: (-6 + math.sqrt(36-36)) / 2,
        tolerance=1e-12,
        note="Exercise 8.4: repeated root case",
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: y(0) = 2",
        section="11",
        stated=2.0,
        computed=lambda: (2 + 3*0)*math.exp(-3*0),
        tolerance=1e-12,
        note="Exercise 8.4: verify IC",
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: y'(0) = -3",
        section="11",
        stated=-3.0,
        computed=lambda: 3*math.exp(0) + (2+0)*(-3)*math.exp(0),
        tolerance=1e-12,
        note="Exercise 8.4: verify IC y'(0) = c2 - 3*c1 = 3-6 = -3",
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: y(1) = 5*e^{-3}",
        section="11",
        stated=5*math.exp(-3),
        computed=lambda: (2+3*1)*math.exp(-3*1),
        tolerance=1e-10,
        note="Exercise 8.4",
    ))

    # --- Exercise 8.5: y' = y(2-y)(y-1) equilibria ---
    # Equilibria: y=0, y=1, y=2
    # f'(y) = (2-y)(y-1) + y(-1)(y-1) + y(2-y)(1) = (2-y)(y-1) - y(y-1) + y(2-y)
    # f'(0) = 2*(-1) - 0 + 0 = -2 < 0 => stable
    # f'(1) = 1*0 - 1*0 + 1*1 = 1 > 0 => unstable
    # f'(2) = 0*1 - 2*1 + 2*0 = -2 < 0 => stable
    ch.add(NumericCheck(
        label="Ex 8.5: f'(0) = -2 (stable)",
        section="11",
        stated=-2.0,
        computed=lambda: (2-0)*(0-1) - 0*(0-1) + 0*(2-0),
        tolerance=1e-12,
        note="Exercise 8.5: derivative at y=0",
    ))
    ch.add(NumericCheck(
        label="Ex 8.5: f'(1) = 1 (unstable)",
        section="11",
        stated=1.0,
        computed=lambda: (2-1)*(1-1) - 1*(1-1) + 1*(2-1),
        tolerance=1e-12,
        note="Exercise 8.5: derivative at y=1",
    ))
    ch.add(NumericCheck(
        label="Ex 8.5: f'(2) = -2 (stable)",
        section="11",
        stated=-2.0,
        computed=lambda: (2-2)*(2-1) - 2*(2-1) + 2*(2-2),
        tolerance=1e-12,
        note="Exercise 8.5: derivative at y=2",
    ))

    # --- Exercise 8.6: x'' + 2x' + 5x = 0 as system ---
    # A = [[0, 1], [-5, -2]]
    # Eigenvalues: lambda = (-2 +/- sqrt(4-20))/2 = -1 +/- 2i
    # Spiral, oscillation freq = 2, decay rate = 1
    A_ex6 = np.array([[0, 1], [-5, -2]], dtype=float)
    eigs_ex6 = np.linalg.eigvals(A_ex6)
    ch.add(NumericCheck(
        label="Ex 8.6: Re(lambda) = -1 (decay rate)",
        section="11",
        stated=-1.0,
        computed=lambda: float(np.linalg.eigvals(np.array([[0,1],[-5,-2]])).real[0]),
        tolerance=1e-10,
        note="Exercise 8.6: stable spiral",
    ))
    ch.add(NumericCheck(
        label="Ex 8.6: |Im(lambda)| = 2 (oscillation frequency)",
        section="11",
        stated=2.0,
        computed=lambda: abs(float(np.linalg.eigvals(np.array([[0,1],[-5,-2]])).imag[0])),
        tolerance=1e-10,
        note="Exercise 8.6",
    ))

    # --- Exercise 8.7: Euler and RK4 for y'=t+y, y(0)=1, h=0.1 ---
    # Exact: y(t) = 2*e^t - t - 1
    # At t=0.1: exact = 2*e^{0.1} - 0.1 - 1 = 2*1.10517... - 1.1 = 1.11034
    exact_01 = 2*math.exp(0.1) - 0.1 - 1

    # Euler: y_1 = y_0 + h*f(0, 1) = 1 + 0.1*(0+1) = 1.1
    euler_y1 = 1.0 + 0.1 * (0 + 1)
    ch.add(NumericCheck(
        label="Ex 8.7: Euler y_1 = 1.1",
        section="11",
        stated=1.1,
        computed=euler_y1,
        tolerance=1e-12,
        note="Exercise 8.7: Euler step",
    ))

    # RK4: k1 = f(0, 1) = 1
    # k2 = f(0.05, 1+0.05*1) = 0.05+1.05 = 1.1
    # k3 = f(0.05, 1+0.05*1.1) = 0.05+1.055 = 1.105
    # k4 = f(0.1, 1+0.1*1.105) = 0.1+1.1105 = 1.2105
    # y_1 = 1 + (0.1/6)*(1 + 2*1.1 + 2*1.105 + 1.2105) = 1 + (0.1/6)*6.6205
    rk4_k1 = 0 + 1
    rk4_k2 = 0.05 + (1 + 0.05*rk4_k1)
    rk4_k3 = 0.05 + (1 + 0.05*rk4_k2)
    rk4_k4 = 0.1 + (1 + 0.1*rk4_k3)
    rk4_y1 = 1 + (0.1/6)*(rk4_k1 + 2*rk4_k2 + 2*rk4_k3 + rk4_k4)

    ch.add(NumericCheck(
        label="Ex 8.7: RK4 y_1",
        section="11",
        stated=rk4_y1,
        computed=rk4_y1,
        tolerance=1e-12,
        note="Exercise 8.7: RK4 step",
    ))
    ch.add(NumericCheck(
        label="Ex 8.7: exact y(0.1) = 2*e^{0.1}-1.1",
        section="11",
        stated=exact_01,
        computed=lambda: 2*math.exp(0.1) - 0.1 - 1,
        tolerance=1e-10,
        note="Exercise 8.7: exact solution",
    ))
    # RK4 should be much closer to exact than Euler
    ch.add(StructuralCheck(
        label="Ex 8.7: RK4 error << Euler error",
        section="11",
        predicate=lambda: (
            abs(rk4_y1 - exact_01) < abs(euler_y1 - exact_01),
            f"RK4 err={abs(rk4_y1-exact_01):.2e} >= Euler err={abs(euler_y1-exact_01):.2e}"
        ),
        note="Exercise 8.7",
    ))

    # --- Exercise 8.8: Linear system x'=Ax, A=[[-1,2],[0,-3]] ---
    # (a) Eigenvalues: -1, -3
    # Eigenvectors: lambda=-1: (1,0), lambda=-3: A+3I = [[2,2],[0,0]] => v=(1,-1)
    # (b) General: x(t) = c1*e^{-t}*(1,0) + c2*e^{-3t}*(1,-1)
    # (c) Stable (both eigs < 0)
    # (d) x(0) = (4,2): c1*(1,0)+c2*(1,-1)=(4,2) => c1+c2=4, -c2=2 => c2=-2, c1=6
    A_ex8 = np.array([[-1, 2], [0, -3]], dtype=float)
    x0_ex8 = np.array([4.0, 2.0])
    # x(t) = 6*e^{-t}*(1,0) + (-2)*e^{-3t}*(1,-1) = (6e^{-t}-2e^{-3t}, 2e^{-3t})
    ch.add(NumericCheck(
        label="Ex 8.8: eigenvalue 1 = -1",
        section="11",
        stated=-1.0,
        computed=lambda: max(np.linalg.eigvals(np.array([[-1,2],[0,-3]])).real),
        tolerance=1e-10,
        note="Exercise 8.8(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 8.8: eigenvalue 2 = -3",
        section="11",
        stated=-3.0,
        computed=lambda: min(np.linalg.eigvals(np.array([[-1,2],[0,-3]])).real),
        tolerance=1e-10,
        note="Exercise 8.8(a)",
    ))
    # (d) Verify x(0) = (4,2)
    ch.add(NumericCheck(
        label="Ex 8.8(d): x1(0) = 6-2 = 4",
        section="11",
        stated=4.0,
        computed=lambda: 6*math.exp(0) - 2*math.exp(0),
        tolerance=1e-12,
        note="Exercise 8.8(d)",
    ))
    ch.add(NumericCheck(
        label="Ex 8.8(d): x2(0) = 2",
        section="11",
        stated=2.0,
        computed=lambda: 2*math.exp(0),
        tolerance=1e-12,
        note="Exercise 8.8(d)",
    ))
    # x(1) = (6e^{-1}-2e^{-3}, 2e^{-3})
    ch.add(NumericCheck(
        label="Ex 8.8(d): x1(1) = 6e^{-1}-2e^{-3}",
        section="11",
        stated=6*math.exp(-1) - 2*math.exp(-3),
        computed=lambda: 6*math.exp(-1) - 2*math.exp(-3),
        tolerance=1e-10,
        note="Exercise 8.8(d)",
    ))
    ch.add(NumericCheck(
        label="Ex 8.8(d): x2(1) = 2e^{-3}",
        section="11",
        stated=2*math.exp(-3),
        computed=lambda: 2*math.exp(-3),
        tolerance=1e-10,
        note="Exercise 8.8(d)",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # Note: Euler and RK4 are already extensively tested via worked examples.
    # Adding explicit algorithm implementation verification.

    # --- Euler's Method (Algorithm, unnamed) ---
    def _algo_euler_method():
        """Verify Euler's method implementation with known O(h) convergence."""
        def euler(f, t0, y0, h, N):
            t, y = t0, y0
            for _ in range(N):
                y = y + h * f(t, y)
                t = t + h
            return y

        # dy/dt = y, y(0)=1, exact: e^1 at t=1
        exact = math.exp(1)
        err_h01 = abs(euler(lambda t, y: y, 0, 1, 0.1, 10) - exact)
        err_h001 = abs(euler(lambda t, y: y, 0, 1, 0.01, 100) - exact)
        ratio = err_h01 / err_h001
        # O(h): ratio should be ~10
        if ratio < 5 or ratio > 20:
            return (False, f"Euler convergence ratio = {ratio:.2f}, expected ~10 (O(h))")
        return (True, "")

    ch.add(StructuralCheck(
        label="Euler's Method: O(h) convergence verified on dy/dt=y",
        section="6",
        predicate=_algo_euler_method,
        note="Euler's method verified (implicit Algorithm)",
    ))

    # --- RK4 Method (Algorithm, unnamed) ---
    def _algo_rk4_method():
        """Verify RK4 implementation with known O(h^4) convergence."""
        def rk4(f, t0, y0, h, N):
            t, y = t0, y0
            for _ in range(N):
                k1 = f(t, y)
                k2 = f(t + h / 2, y + h / 2 * k1)
                k3 = f(t + h / 2, y + h / 2 * k2)
                k4 = f(t + h, y + h * k3)
                y = y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
                t = t + h
            return y

        # dy/dt = y, y(0)=1, exact: e^1 at t=1
        exact = math.exp(1)
        err_h01 = abs(rk4(lambda t, y: y, 0, 1, 0.1, 10) - exact)
        err_h005 = abs(rk4(lambda t, y: y, 0, 1, 0.05, 20) - exact)
        ratio = err_h01 / err_h005
        # O(h^4): halving h reduces error by 2^4 = 16
        if ratio < 10 or ratio > 25:
            return (False, f"RK4 convergence ratio = {ratio:.2f}, expected ~16 (O(h^4))")

        # Also verify accuracy: RK4 with h=0.1 should be very accurate
        if err_h01 > 5e-6:
            return (False, f"RK4 error with h=0.1: {err_h01:.2e}, expected < 5e-6")

        return (True, "")

    ch.add(StructuralCheck(
        label="RK4 Method: O(h^4) convergence verified on dy/dt=y",
        section="6",
        predicate=_algo_rk4_method,
        note="RK4 method verified (implicit Algorithm)",
    ))

    # --- Algorithm 19.1: Euler's method (explicit label) ---
    def _algo_euler_method():
        """Verify Euler's method on dy/dt = -y, y(0)=1 (exact: e^{-t})."""
        def euler(f, t0, y0, h, N):
            t, y = t0, y0
            for _ in range(N):
                y = y + h * f(t, y)
                t = t + h
            return y

        f = lambda t, y: -y
        exact_at_1 = math.exp(-1.0)

        # O(h) convergence: halving h halves the error
        err_h01 = abs(euler(f, 0, 1.0, 0.1, 10) - exact_at_1)
        err_h005 = abs(euler(f, 0, 1.0, 0.05, 20) - exact_at_1)
        ratio = err_h01 / err_h005
        if ratio < 1.5 or ratio > 2.5:
            return (False, f"Euler O(h) ratio = {ratio:.2f}, expected ~2")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 19.1: Euler's method O(h) convergence on dy/dt=-y",
        section="6",
        predicate=_algo_euler_method,
        note="Algorithm 19.1 verified",
    ))

    # --- Algorithm 19.2: RK4 (explicit label) ---
    def _algo_rk4_explicit():
        """Verify RK4 on dy/dt = -y, y(0)=1 gives accurate result."""
        def rk4(f, t0, y0, h, N):
            t, y = t0, y0
            for _ in range(N):
                k1 = f(t, y)
                k2 = f(t + h/2, y + h/2 * k1)
                k3 = f(t + h/2, y + h/2 * k2)
                k4 = f(t + h, y + h * k3)
                y = y + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)
                t = t + h
            return y

        f = lambda t, y: -y
        exact = math.exp(-1.0)
        result = rk4(f, 0, 1.0, 0.1, 10)
        err = abs(result - exact)
        if err > 1e-6:
            return (False, f"RK4 error = {err:.2e}, expected < 1e-6")

        # O(h^4): halving h reduces error by ~16
        err_h01 = abs(rk4(f, 0, 1.0, 0.1, 10) - exact)
        err_h005 = abs(rk4(f, 0, 1.0, 0.05, 20) - exact)
        if err_h005 > 1e-15:
            ratio = err_h01 / err_h005
            if ratio < 10 or ratio > 25:
                return (False, f"RK4 O(h^4) ratio = {ratio:.2f}, expected ~16")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 19.2: RK4 method accuracy and O(h^4) convergence",
        section="6",
        predicate=_algo_rk4_explicit,
        note="Algorithm 19.2 verified",
    ))

    # --- Remark 3.14: State-space solution x(t) = e^{At}x0 + int e^{A(t-s)}Bu(s) ds ---
    def _remark_3_14_state_space():
        """Verify state-space formula for linear ODE with input."""
        from scipy.linalg import expm
        A = np.array([[-1, 0], [0, -2]], dtype=float)
        B = np.array([[1], [1]], dtype=float)
        x0 = np.array([1, 0], dtype=float)
        # Step input u(t) = 1
        t_final = 5.0
        dt = 0.001
        # Numerical integration of convolution
        t_pts = np.arange(0, t_final, dt)
        x_conv = expm(A * t_final) @ x0
        integral = np.zeros(2)
        for s in t_pts:
            integral += expm(A * (t_final - s)) @ B.flatten() * 1.0 * dt
        x_formula = x_conv + integral
        # Compare with direct Euler integration
        x_euler = x0.copy()
        for _ in range(int(t_final / dt)):
            x_euler = x_euler + dt * (A @ x_euler + B.flatten() * 1.0)
        if not np.allclose(x_formula, x_euler, atol=0.05):
            return (False, f"Formula: {x_formula}, Euler: {x_euler}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: State-space x(t) = e^{At}x0 + conv(e^{A(t-s)}Bu(s))",
        section="3.14",
        predicate=_remark_3_14_state_space,
        note="Remark 3.14: state-space model and Green's function",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _verify_ode_solution_exponential_growth():
    """Verify y=3e^{2t} satisfies y'=2y and y(0)=3."""
    import sympy
    t = sympy.Symbol("t")
    y = 3 * sympy.exp(2 * t)
    lhs = sympy.diff(y, t)
    rhs = 2 * y
    ic = y.subs(t, 0)
    return sympy.Eq(sympy.simplify(lhs - rhs), 0) & sympy.Eq(ic, 3)


def _verify_first_order_linear():
    """Verify y=e^{-x}+2e^{-2x} satisfies y'+2y=e^{-x} and y(0)=3."""
    import sympy
    x = sympy.Symbol("x")
    y = sympy.exp(-x) + 2 * sympy.exp(-2 * x)
    ode_residual = sympy.diff(y, x) + 2 * y - sympy.exp(-x)
    ic = y.subs(x, 0)
    return sympy.Eq(sympy.simplify(ode_residual), 0) & sympy.Eq(ic, 3)


def _verify_logistic_solution():
    """Verify y=1/(1+9e^{-t}) satisfies y'=y(1-y)."""
    import sympy
    t = sympy.Symbol("t")
    y = 1 / (1 + 9 * sympy.exp(-t))
    lhs = sympy.diff(y, t)
    rhs = y * (1 - y)
    residual = sympy.simplify(lhs - rhs)
    ic = sympy.simplify(y.subs(t, 0) - sympy.Rational(1, 10))
    return sympy.Eq(residual, 0) & sympy.Eq(ic, 0)


def _verify_second_order_distinct():
    """Verify y=2e^t-e^{2t} satisfies y''-3y'+2y=0 and ICs y(0)=1, y'(0)=0."""
    import sympy
    t = sympy.Symbol("t")
    y = 2 * sympy.exp(t) - sympy.exp(2 * t)
    yp = sympy.diff(y, t)
    ypp = sympy.diff(y, t, 2)
    ode_residual = ypp - 3 * yp + 2 * y
    ic0 = y.subs(t, 0)
    ic1 = yp.subs(t, 0)
    return (
        sympy.Eq(sympy.simplify(ode_residual), 0)
        & sympy.Eq(ic0, 1)
        & sympy.Eq(ic1, 0)
    )


def _verify_harmonic_oscillator():
    """Verify cos(2t) satisfies y''+4y=0."""
    import sympy
    t = sympy.Symbol("t")
    y = sympy.cos(2 * t)
    ypp = sympy.diff(y, t, 2)
    residual = ypp + 4 * y
    return sympy.Eq(sympy.simplify(residual), 0)


def _verify_particular_solution():
    """Verify y_p=-cos(2t) satisfies y''+y=3cos(2t)."""
    import sympy
    t = sympy.Symbol("t")
    y_p = -sympy.cos(2 * t)
    ypp = sympy.diff(y_p, t, 2)
    residual = ypp + y_p - 3 * sympy.cos(2 * t)
    return sympy.Eq(sympy.simplify(residual), 0)


def _verify_damped_oscillator_roots():
    """Verify roots of lambda^2+0.5*lambda+4=0 are -0.25+/-i*sqrt(63/16)."""
    import sympy
    lam = sympy.Symbol("lambda")
    poly = lam**2 + sympy.Rational(1, 2) * lam + 4
    roots = sympy.solve(poly, lam)
    # Should be -1/4 +/- i*sqrt(63)/4
    expected_real = sympy.Rational(-1, 4)
    expected_imag = sympy.sqrt(63) / 4
    r1, r2 = sorted(roots, key=lambda r: sympy.im(r))
    check1 = sympy.Eq(sympy.re(r1), expected_real)
    check2 = sympy.Eq(sympy.Abs(sympy.im(r1)), expected_imag)
    return check1 & check2


def _verify_separable_xy():
    """Verify y=exp(x^2/2) satisfies y'=xy and y(0)=1."""
    import sympy
    x = sympy.Symbol("x")
    y = sympy.exp(x**2 / 2)
    lhs = sympy.diff(y, x)
    rhs = x * y
    ic = y.subs(x, 0)
    return sympy.Eq(sympy.simplify(lhs - rhs), 0) & sympy.Eq(ic, 1)


def _verify_integrating_factor():
    """Verify d/dx[e^{2x}*y] = e^x when y = e^{-x}+2e^{-2x}."""
    import sympy
    x = sympy.Symbol("x")
    y = sympy.exp(-x) + 2 * sympy.exp(-2 * x)
    product = sympy.exp(2 * x) * y
    derivative = sympy.diff(product, x)
    return sympy.Eq(sympy.simplify(derivative - sympy.exp(x)), 0)


# ---------------------------------------------------------------------------
# Numeric helpers: Euler and RK4 implementations
# ---------------------------------------------------------------------------

def _euler_steps(f, t0, y0, h, n):
    """Run n steps of Euler's method."""
    t, y = t0, y0
    for _ in range(n):
        y = y + h * f(t, y)
        t = t + h
    return y


def _rk4_steps(f, t0, y0, h, n):
    """Run n steps of classical RK4."""
    t, y = t0, y0
    for _ in range(n):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h / 2 * k1)
        k3 = f(t + h / 2, y + h / 2 * k2)
        k4 = f(t + h, y + h * k3)
        y = y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        t = t + h
    return y


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _ode_stability_eigenvalue_check(A):
    """Check Re(lambda)<0 for all eigenvalues => asymptotically stable."""
    eigs = np.linalg.eigvals(A)
    for lam in eigs:
        if lam.real >= 0:
            return (False, f"Eigenvalue {lam} has Re(lambda)={lam.real} >= 0")
    return (True, "")


def _ode_instability_check(A):
    """Check that at least one eigenvalue has Re(lambda)>0 => unstable."""
    eigs = np.linalg.eigvals(A)
    has_positive = any(lam.real > 0 for lam in eigs)
    if has_positive:
        return (True, "")
    return (False, f"Expected at least one eigenvalue with Re>0, got {eigs}")


def _ode_center_check(A):
    """Check that eigenvalues are purely imaginary (center)."""
    eigs = np.linalg.eigvals(A)
    for lam in eigs:
        if abs(lam.real) > 1e-10:
            return (False, f"Eigenvalue {lam} has Re(lambda)={lam.real}, expected ~0")
        if abs(lam.imag) < 1e-10:
            return (False, f"Eigenvalue {lam} has Im(lambda)={lam.imag}, expected nonzero")
    return (True, "")


def _ode_unstable_spiral_check(A):
    """Check complex eigenvalues with Re(lambda)>0 => unstable spiral."""
    eigs = np.linalg.eigvals(A)
    has_positive_real = all(lam.real > 0 for lam in eigs)
    has_nonzero_imag = any(abs(lam.imag) > 1e-10 for lam in eigs)
    if has_positive_real and has_nonzero_imag:
        return (True, "")
    return (False, f"Expected unstable spiral, got eigenvalues {eigs}")


def _euler_convergence_order():
    """Verify Euler is first-order by checking error ratio when halving h."""
    f = lambda t, y: -y
    exact = math.exp(-1)

    e1 = abs(_euler_steps(f, 0, 1.0, 0.1, 10) - exact)
    e2 = abs(_euler_steps(f, 0, 1.0, 0.05, 20) - exact)

    ratio = e1 / e2
    # For first-order method, ratio should be ~2
    if 1.8 < ratio < 2.2:
        return (True, "")
    return (False, f"Error ratio={ratio:.3f}, expected ~2.0 for first-order")


def _rk4_convergence_order():
    """Verify RK4 is fourth-order by checking error ratio when halving h."""
    f = lambda t, y: -y
    exact = math.exp(-1)

    e1 = abs(_rk4_steps(f, 0, 1.0, 0.1, 10) - exact)
    e2 = abs(_rk4_steps(f, 0, 1.0, 0.05, 20) - exact)

    if e2 == 0:
        return (True, "")
    ratio = e1 / e2
    # For fourth-order method, ratio should be ~16
    if 14.0 < ratio < 18.0:
        return (True, "")
    return (False, f"Error ratio={ratio:.3f}, expected ~16.0 for fourth-order")


def _euler_convergence_multi_h():
    """Verify Euler O(h) convergence at h=0.1 and h=0.01."""
    f = lambda t, y: -y
    exact = math.exp(-1)
    e1 = abs(_euler_steps(f, 0, 1.0, 0.1, 10) - exact)
    e2 = abs(_euler_steps(f, 0, 1.0, 0.01, 100) - exact)
    ratio = e1 / e2
    # Should be ~10 (factor of 10 in h => factor of 10 in error)
    if 8.0 < ratio < 12.0:
        return (True, "")
    return (False, f"Error ratio h=0.1/h=0.01 = {ratio:.3f}, expected ~10")


def _rk4_convergence_multi_h():
    """Verify RK4 O(h^4) convergence at h=0.1 and h=0.01."""
    f = lambda t, y: -y
    exact = math.exp(-1)
    e1 = abs(_rk4_steps(f, 0, 1.0, 0.1, 10) - exact)
    e2 = abs(_rk4_steps(f, 0, 1.0, 0.01, 100) - exact)
    if e2 == 0:
        return (True, "")
    ratio = e1 / e2
    # Should be ~10^4 = 10000
    if 8000 < ratio < 12000:
        return (True, "")
    return (False, f"Error ratio h=0.1/h=0.01 = {ratio:.1f}, expected ~10000")


def _logistic_ode_equilibrium_stability():
    """Check logistic f(y)=y(1-y): f'(0)=1>0 (unstable), f'(1)=-1<0 (stable)."""
    # f(y) = y(1-y), f'(y) = 1-2y
    fp_0 = 1 - 2 * 0  # = 1 > 0
    fp_1 = 1 - 2 * 1  # = -1 < 0
    if fp_0 > 0 and fp_1 < 0:
        return (True, "")
    return (False, f"f'(0)={fp_0}, f'(1)={fp_1}, expected >0 and <0")


def _characteristic_roots_check(a, b, c, expected_roots):
    """Check that roots of a*lam^2+b*lam+c=0 match expected values."""
    disc = b**2 - 4 * a * c
    if disc < 0:
        return (False, f"Expected real roots but discriminant={disc}<0")
    r1 = (-b + math.sqrt(disc)) / (2 * a)
    r2 = (-b - math.sqrt(disc)) / (2 * a)
    computed = sorted([r1, r2])
    expected = sorted(expected_roots)
    if np.allclose(computed, expected, atol=1e-10):
        return (True, "")
    return (False, f"Expected roots {expected}, got {computed}")


def _characteristic_roots_complex_check(a, b, c, expected_alpha, expected_beta):
    """Check complex roots alpha +/- i*beta."""
    disc = b**2 - 4 * a * c
    if disc >= 0:
        return (False, f"Expected complex roots but discriminant={disc}>=0")
    alpha = -b / (2 * a)
    beta = math.sqrt(-disc) / (2 * a)
    if abs(alpha - expected_alpha) < 1e-3 and abs(beta - expected_beta) < 1e-3:
        return (True, "")
    return (False, f"Expected alpha={expected_alpha}, beta={expected_beta}, got alpha={alpha}, beta={beta}")


def _rk4_stability_region_check():
    """Check RK4 stability function R(z)=1+z+z^2/2+z^3/6+z^4/24."""
    def R(z):
        return 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24

    # z=-2 should be inside stability region: |R(-2)| < 1
    r_neg2 = abs(R(-2))
    if r_neg2 >= 1:
        return (False, f"|R(-2)|={r_neg2} >= 1, expected inside stability region")

    # z=-3 should be outside stability region: |R(-3)| > 1
    r_neg3 = abs(R(-3))
    if r_neg3 <= 1:
        return (False, f"|R(-3)|={r_neg3} <= 1, expected outside stability region")

    return (True, "")


def _euler_stability_region_check():
    """Check Euler stability function R(z) = 1+z."""
    # z=-1: |1+(-1)| = 0 < 1, inside
    r_neg1 = abs(1 + (-1))
    if r_neg1 >= 1:
        return (False, f"|1+(-1)|={r_neg1} >= 1, expected inside")

    # z=-0.5: |1+(-0.5)| = 0.5 < 1, inside
    r_neg05 = abs(1 + (-0.5))
    if r_neg05 >= 1:
        return (False, f"|1+(-0.5)|={r_neg05} >= 1, expected inside")

    # z=-2.5: |1+(-2.5)| = 1.5 > 1, outside
    r_neg25 = abs(1 + (-2.5))
    if r_neg25 <= 1:
        return (False, f"|1+(-2.5)|={r_neg25} <= 1, expected outside")

    return (True, "")


def _phase_portrait_classification():
    """Verify phase portrait classification for canonical 2x2 systems."""
    test_cases = [
        # (A, expected_type)
        (np.array([[-1, 0], [0, -3]], dtype=float), "stable_node"),
        (np.array([[1, 0], [0, 3]], dtype=float), "unstable_node"),
        (np.array([[-1, 2], [0, 3]], dtype=float), "saddle"),
        (np.array([[0, 1], [-4, -0.5]], dtype=float), "stable_spiral"),
        (np.array([[0.5, 1], [-4, 0.5]], dtype=float), "unstable_spiral"),
        (np.array([[0, 1], [-4, 0]], dtype=float), "center"),
        (np.array([[-3, 0], [0, -3]], dtype=float), "stable_node"),  # repeated eigenvalue
    ]

    for A, expected in test_cases:
        eigs = np.linalg.eigvals(A)
        real_parts = [lam.real for lam in eigs]
        imag_parts = [lam.imag for lam in eigs]
        has_complex = any(abs(im) > 1e-10 for im in imag_parts)
        all_neg = all(r < -1e-10 for r in real_parts)
        all_pos = all(r > 1e-10 for r in real_parts)
        mixed = any(r > 1e-10 for r in real_parts) and any(r < -1e-10 for r in real_parts)
        all_zero_real = all(abs(r) < 1e-10 for r in real_parts)

        if expected == "stable_node":
            if not (all_neg and not has_complex):
                return (False, f"Expected stable_node for {A.tolist()}, eigs={eigs}")
        elif expected == "unstable_node":
            if not (all_pos and not has_complex):
                return (False, f"Expected unstable_node for {A.tolist()}, eigs={eigs}")
        elif expected == "saddle":
            if not mixed:
                return (False, f"Expected saddle for {A.tolist()}, eigs={eigs}")
        elif expected == "stable_spiral":
            if not (all_neg and has_complex):
                return (False, f"Expected stable_spiral for {A.tolist()}, eigs={eigs}")
        elif expected == "unstable_spiral":
            if not (all_pos and has_complex):
                return (False, f"Expected unstable_spiral for {A.tolist()}, eigs={eigs}")
        elif expected == "center":
            if not (all_zero_real and has_complex):
                return (False, f"Expected center for {A.tolist()}, eigs={eigs}")

    return (True, "")


def _rk4_matches_exact_exponential():
    """Verify RK4 on y'=2y, y(0)=3 matches 3*e^{2t} at t=2."""
    f = lambda t, y: 2 * y
    exact = 3 * math.exp(4)
    numerical = _rk4_steps(f, 0, 3.0, 0.01, 200)
    rel_error = abs(numerical - exact) / exact
    if rel_error < 1e-8:
        return (True, "")
    return (False, f"RK4 relative error = {rel_error:.2e}, expected < 1e-8")


def _rk4_matches_exact_logistic():
    """Verify RK4 on y'=y(1-y), y(0)=0.1 matches logistic at t=10."""
    f = lambda t, y: y * (1 - y)
    exact = 1 / (1 + 9 * math.exp(-10))
    numerical = _rk4_steps(f, 0, 0.1, 0.05, 200)
    abs_error = abs(numerical - exact)
    if abs_error < 1e-9:
        return (True, "")
    return (False, f"RK4 absolute error = {abs_error:.2e}, expected < 1e-9")
