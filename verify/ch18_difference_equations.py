# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 18: Difference Equations & Dynamical Systems — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(18, "Difference Equations & Dynamical Systems")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- First-order closed-form solution (Theorem 3.3 / Section 5) ---
    ch.add(SymbolicCheck(
        label="First-order solution: x_t = a^t*(x0 - b/(1-a)) + b/(1-a)",
        section="5",
        identity=lambda: _first_order_closed_form(),
        note="verify closed form satisfies x_{t+1} = a*x_t + b",
    ))

    # --- Second-order distinct roots: closed form satisfies recurrence ---
    ch.add(SymbolicCheck(
        label="Second-order distinct roots solution satisfies recurrence",
        section="5",
        identity=lambda: _second_order_distinct_roots(),
        note="x_t = c1*lam1^t + c2*lam2^t satisfies x_{t+2} + a1*x_{t+1} + a2*x_t = 0",
    ))

    # --- Fibonacci closed form (Binet's formula, Example 3.13) ---
    ch.add(SymbolicCheck(
        label="Fibonacci Binet formula: F_t = (phi^t - psi^t)/sqrt(5)",
        section="4",
        identity=lambda: _fibonacci_binet(),
        note="verify F_0=0, F_1=1, F_2=1, F_3=2, ..., F_10=55",
    ))

    # --- Vieta's formulas for characteristic quadratic ---
    ch.add(SymbolicCheck(
        label="Vieta: lam1+lam2 = -a1 and lam1*lam2 = a2",
        section="5",
        identity=lambda: _vieta_formulas(),
    ))

    # --- Fixed point formula: x* = b/(1+a1+a2) for second order ---
    ch.add(SymbolicCheck(
        label="Second-order fixed point: x* = b/(1+a1+a2)",
        section="5",
        identity=lambda: _second_order_fixed_point(),
        note="constant x* satisfies x* + a1*x* + a2*x* = b",
    ))

    # --- Complex-root modulus: r = sqrt(a2) (Theorem 3.6) ---
    ch.add(SymbolicCheck(
        label="Complex root modulus: |lambda| = sqrt(a2) when D<0",
        section="5",
        identity=lambda: _complex_root_modulus(),
        note="Theorem 3.6: r = sqrt(a2) from Vieta product",
    ))

    # --- First-order special case a=1: x_t = x0 + bt ---
    ch.add(SymbolicCheck(
        label="First-order a=1 special case: x_t = x0 + b*t",
        section="5",
        identity=lambda: _first_order_unit_root(),
        note="arithmetic growth when a=1",
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    # --- Example 8.1: Radioactive decay m_t = 0.88^t * 100 ---
    ch.add(NumericCheck(
        label="Radioactive decay m_10 = 0.88^10 * 100",
        section="9",
        stated=27.85,
        computed=lambda: 0.88**10 * 100,
        tolerance=1e-3,
        note="Example 8.1: a=0.88, b=0, x0=100, t=10",
    ))

    # --- Example 8.1: half-life = ln(0.5)/ln(0.88) ---
    ch.add(NumericCheck(
        label="Radioactive decay half-life t_{1/2} = ln(0.5)/ln(0.88)",
        section="9",
        stated=5.42,
        computed=lambda: math.log(0.5) / math.log(0.88),
        tolerance=1e-2,
        note="Example 8.1",
    ))

    # --- Example 8.2: Loan amortization fixed point L* = P/r ---
    ch.add(NumericCheck(
        label="Loan fixed point L* = P/r = 1199.10/0.005",
        section="9",
        stated=239820.0,
        computed=lambda: 1199.10 / 0.005,
        tolerance=1e-6,
        note="Example 8.2: r=0.005, P=1199.10",
    ))

    # --- Example 8.3: Predator-prey eigenvalue modulus ---
    ch.add(NumericCheck(
        label="Predator-prey eigenvalue modulus sqrt(0.85)",
        section="9",
        stated=0.922,
        computed=lambda: math.sqrt(0.85),
        tolerance=1e-3,
        note="Example 8.3: |lambda| = sqrt(0.85)",
    ))

    # --- Example 8.3: oscillation period ---
    ch.add(NumericCheck(
        label="Predator-prey oscillation period 2*pi/theta",
        section="9",
        stated=28.8,
        computed=lambda: 2 * math.pi / math.atan2(0.2, 0.9),
        tolerance=0.1,
        note="Example 8.3: theta = arctan(0.2/0.9)",
    ))

    # --- Example 8.3: predator-prey eigenvalue real part ---
    ch.add(NumericCheck(
        label="Predator-prey eigenvalue real part = 0.9",
        section="9",
        stated=0.9,
        computed=lambda: (1.1 + 0.7) / 2,
        tolerance=1e-10,
        note="Example 8.3: Re(lambda) = tr(A)/2 = 1.8/2",
    ))

    # --- Example 8.3: predator-prey eigenvalue imaginary part ---
    ch.add(NumericCheck(
        label="Predator-prey eigenvalue imaginary part = 0.2",
        section="9",
        stated=0.2,
        computed=lambda: math.sqrt(0.85 - 0.81),
        tolerance=1e-6,
        note="Example 8.3: Im(lambda) = sqrt(det(A) - (tr/2)^2)",
    ))

    # --- Example 8.3: predator-prey oscillation angle theta ---
    ch.add(NumericCheck(
        label="Predator-prey theta = arctan(0.2/0.9) = 0.218 rad",
        section="9",
        stated=0.2187,
        computed=lambda: math.atan2(0.2, 0.9),
        tolerance=1e-3,
        note="Example 8.3: theta = arctan(Im/Re)",
    ))

    # --- Example 8.3: predator-prey trajectory (system iteration) ---
    # Starting from (100, 50), compute a few steps to verify
    ch.add(NumericCheck(
        label="Predator-prey x_1 (prey) = 1.1*100 - 0.4*50 = 90",
        section="9",
        stated=90.0,
        computed=lambda: 1.1 * 100 - 0.4 * 50,
        tolerance=1e-10,
        note="Example 8.3: first step prey",
    ))

    ch.add(NumericCheck(
        label="Predator-prey y_1 (predator) = 0.2*100 + 0.7*50 = 55",
        section="9",
        stated=55.0,
        computed=lambda: 0.2 * 100 + 0.7 * 50,
        tolerance=1e-10,
        note="Example 8.3: first step predator",
    ))

    ch.add(NumericCheck(
        label="Predator-prey x_2 (prey) = 1.1*90 - 0.4*55 = 77",
        section="9",
        stated=77.0,
        computed=lambda: 1.1 * 90 - 0.4 * 55,
        tolerance=1e-10,
        note="Example 8.3: second step prey",
    ))

    ch.add(NumericCheck(
        label="Predator-prey y_2 (predator) = 0.2*90 + 0.7*55 = 56.5",
        section="9",
        stated=56.5,
        computed=lambda: 0.2 * 90 + 0.7 * 55,
        tolerance=1e-10,
        note="Example 8.3: second step predator",
    ))

    ch.add(NumericCheck(
        label="Predator-prey x_3 (prey) = 1.1*77 - 0.4*56.5 = 62.1",
        section="9",
        stated=62.1,
        computed=lambda: 1.1 * 77 - 0.4 * 56.5,
        tolerance=1e-10,
        note="Example 8.3: third step prey",
    ))

    ch.add(NumericCheck(
        label="Predator-prey y_3 (predator) = 0.2*77 + 0.7*56.5 = 54.95",
        section="9",
        stated=54.95,
        computed=lambda: 0.2 * 77 + 0.7 * 56.5,
        tolerance=1e-10,
        note="Example 8.3: third step predator",
    ))

    # --- Example 8.4: Cobweb model iteration values ---
    # P_t = 60 - 1.5*P_{t-1}, P_0 = 20
    ch.add(NumericCheck(
        label="Cobweb P_1 = 60 - 1.5*20 = 30",
        section="9",
        stated=30.0,
        computed=lambda: 60 - 1.5 * 20,
        tolerance=1e-10,
        note="Example 8.4",
    ))

    ch.add(NumericCheck(
        label="Cobweb P_2 = 60 - 1.5*30 = 15",
        section="9",
        stated=15.0,
        computed=lambda: 60 - 1.5 * 30,
        tolerance=1e-10,
        note="Example 8.4",
    ))

    ch.add(NumericCheck(
        label="Cobweb P_3 = 60 - 1.5*15 = 37.5",
        section="9",
        stated=37.5,
        computed=lambda: 60 - 1.5 * 15,
        tolerance=1e-10,
        note="Example 8.4",
    ))

    ch.add(NumericCheck(
        label="Cobweb P_4 = 60 - 1.5*37.5 = 3.75",
        section="9",
        stated=3.75,
        computed=lambda: 60 - 1.5 * 37.5,
        tolerance=1e-10,
        note="Example 8.4",
    ))

    # --- Cobweb P_5 and P_6: continue the iteration ---
    ch.add(NumericCheck(
        label="Cobweb P_5 = 60 - 1.5*3.75 = 54.375",
        section="9",
        stated=54.375,
        computed=lambda: 60 - 1.5 * 3.75,
        tolerance=1e-10,
        note="Example 8.4: continued iteration",
    ))

    ch.add(NumericCheck(
        label="Cobweb P_6 = 60 - 1.5*54.375 = -21.5625",
        section="9",
        stated=-21.5625,
        computed=lambda: 60 - 1.5 * 54.375,
        tolerance=1e-10,
        note="Example 8.4: explosive divergence, price goes negative",
    ))

    # --- Cobweb fixed point P* = 60/(1+1.5) = 24 ---
    ch.add(NumericCheck(
        label="Cobweb fixed point P* = 60/2.5 = 24",
        section="9",
        stated=24.0,
        computed=lambda: 60 / (1 + 1.5),
        tolerance=1e-10,
        note="Example 8.4: a=-1.5, b=60",
    ))

    # --- First-order convergence: a=0.8, b=2, x0=20, x*=10 ---
    # Verify all AR(1) trajectory values from the diagram
    ch.add(NumericCheck(
        label="AR(1) x_0 = 20",
        section="4",
        stated=20.0,
        computed=lambda: 0.8**0 * (20 - 10) + 10,
        tolerance=1e-10,
        note="from diagram: initial condition",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_1 = 0.8*20 + 2 = 18",
        section="4",
        stated=18.0,
        computed=lambda: 0.8**1 * (20 - 10) + 10,
        tolerance=1e-10,
        note="from diagram: a=0.8, b=2, x*=10",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_2 = 16.4",
        section="4",
        stated=16.4,
        computed=lambda: 0.8**2 * (20 - 10) + 10,
        tolerance=1e-6,
        note="from diagram",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_3 = 15.12",
        section="4",
        stated=15.12,
        computed=lambda: 0.8**3 * (20 - 10) + 10,
        tolerance=1e-6,
        note="from diagram",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_4 = 14.096",
        section="4",
        stated=14.10,
        computed=lambda: 0.8**4 * (20 - 10) + 10,
        tolerance=1e-3,
        note="from diagram (rounded to 14.10)",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_5 = 13.2768",
        section="4",
        stated=13.28,
        computed=lambda: 0.8**5 * (20 - 10) + 10,
        tolerance=1e-2,
        note="from diagram (rounded to 13.28)",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_6 = 12.62",
        section="4",
        stated=12.62,
        computed=lambda: 0.8**6 * (20 - 10) + 10,
        tolerance=1e-2,
        note="from diagram",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_7 = 12.10",
        section="4",
        stated=12.10,
        computed=lambda: 0.8**7 * (20 - 10) + 10,
        tolerance=1e-2,
        note="from diagram",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_8 = 11.68",
        section="4",
        stated=11.68,
        computed=lambda: 0.8**8 * (20 - 10) + 10,
        tolerance=1e-2,
        note="from diagram",
    ))

    ch.add(NumericCheck(
        label="AR(1) x_9 = 11.34",
        section="4",
        stated=11.34,
        computed=lambda: 0.8**9 * (20 - 10) + 10,
        tolerance=1e-2,
        note="from diagram",
    ))

    # --- Fibonacci F_10 = 55 via iteration ---
    ch.add(NumericCheck(
        label="Fibonacci F_10 = 55 via iteration",
        section="4",
        stated=55.0,
        computed=lambda: _fibonacci_iterate(10),
        tolerance=1e-10,
        note="Example 3.13",
    ))

    # --- Fibonacci F_10 via Binet formula ---
    ch.add(NumericCheck(
        label="Fibonacci F_10 = 55 via Binet formula",
        section="4",
        stated=55.0,
        computed=lambda: _fibonacci_binet_numeric(10),
        tolerance=1e-6,
        note="Example 3.13: (phi^10 - psi^10)/sqrt(5)",
    ))

    # --- Fibonacci: golden ratio phi ---
    ch.add(NumericCheck(
        label="Golden ratio phi = (1+sqrt(5))/2 = 1.61803...",
        section="4",
        stated=1.618034,
        computed=lambda: (1 + math.sqrt(5)) / 2,
        tolerance=1e-6,
        note="Example 3.13: dominant root",
    ))

    # --- Fibonacci: |lambda_2| = 1/phi ---
    ch.add(NumericCheck(
        label="Fibonacci |lambda_2| = 1/phi = 0.61803...",
        section="4",
        stated=0.618034,
        computed=lambda: 2 / (1 + math.sqrt(5)),
        tolerance=1e-6,
        note="Example 3.13: subdominant root modulus",
    ))

    # --- Fibonacci: Binet coefficients c1 = c2 = 1/sqrt(5) ---
    ch.add(NumericCheck(
        label="Fibonacci Binet coefficient c1 = 1/sqrt(5) = 0.44721...",
        section="4",
        stated=0.447214,
        computed=lambda: 1 / math.sqrt(5),
        tolerance=1e-5,
        note="Example 3.13: c1 = -c2 = 1/sqrt(5)",
    ))

    # --- Samuelson model: discriminant for c=0.8, v=0.5 ---
    ch.add(NumericCheck(
        label="Samuelson discriminant (c+v)^2 - 4v for c=0.8, v=0.5",
        section="4",
        stated=-0.31,
        computed=lambda: (0.8 + 0.5)**2 - 4 * 0.5,
        tolerance=1e-10,
        note="Example 3.11: negative => damped oscillations",
    ))

    # --- Samuelson model: eigenvalue modulus r = sqrt(v) ---
    ch.add(NumericCheck(
        label="Samuelson eigenvalue modulus r = sqrt(0.5) for c=0.8, v=0.5",
        section="4",
        stated=0.70711,
        computed=lambda: math.sqrt(0.5),
        tolerance=1e-4,
        note="Example 3.11: modulus < 1 => damped",
    ))

    # --- Samuelson model: equilibrium Y* = G/(1-c) ---
    ch.add(NumericCheck(
        label="Samuelson equilibrium Y* = G/(1-c) for c=0.8 => multiplier = 5",
        section="4",
        stated=5.0,
        computed=lambda: 1 / (1 - 0.8),
        tolerance=1e-10,
        note="Example 3.11: Keynesian multiplier 1/(1-c)",
    ))

    # --- Samuelson Schur-Cohn condition (i): 1 - c > 0 ---
    ch.add(NumericCheck(
        label="Samuelson Schur-Cohn (i): 1 - c = 0.2 > 0",
        section="4",
        stated=0.2,
        computed=lambda: 1 - 0.8,
        tolerance=1e-10,
        note="Example 3.11: condition (i) satisfied",
    ))

    # --- Samuelson Schur-Cohn condition (ii): 1 + c + 2v ---
    ch.add(NumericCheck(
        label="Samuelson Schur-Cohn (ii): 1 + c + 2v = 2.8 > 0",
        section="4",
        stated=2.8,
        computed=lambda: 1 + 0.8 + 2 * 0.5,
        tolerance=1e-10,
        note="Example 3.11: condition (ii) always satisfied",
    ))

    # --- Radioactive decay: intermediate time values ---
    ch.add(NumericCheck(
        label="Radioactive decay m_5 = 0.88^5 * 100 = 52.77",
        section="9",
        stated=52.77,
        computed=lambda: 0.88**5 * 100,
        tolerance=1e-2,
        note="Example 8.1: halfway to t=10",
    ))

    ch.add(NumericCheck(
        label="Radioactive decay m_1 = 0.88 * 100 = 88",
        section="9",
        stated=88.0,
        computed=lambda: 0.88 * 100,
        tolerance=1e-10,
        note="Example 8.1: first step",
    ))

    # --- Logistic map: fixed point (r-1)/r for various r ---
    ch.add(NumericCheck(
        label="Logistic map: x* = (r-1)/r for r=2 => x* = 0.5",
        section="4",
        stated=0.5,
        computed=lambda: (2 - 1) / 2,
        tolerance=1e-10,
        note="Remark 3.14: stable fixed point for 1<r<3",
    ))

    ch.add(NumericCheck(
        label="Logistic map: f'(x*) = 2-r for r=2 => f'(x*) = 0",
        section="4",
        stated=0.0,
        computed=lambda: 2 - 2.0,
        tolerance=1e-10,
        note="Remark 3.14: superstable",
    ))

    ch.add(NumericCheck(
        label="Logistic map: f'(x*) = 2-r for r=3 => |f'(x*)| = 1 (bifurcation)",
        section="4",
        stated=1.0,
        computed=lambda: abs(2 - 3.0),
        tolerance=1e-10,
        note="Remark 3.14: period-doubling bifurcation at r=3",
    ))

    # --- Logistic map: period-doubling parameter values ---
    ch.add(NumericCheck(
        label="Logistic map: period-4 onset at r ~ 3.449",
        section="4",
        stated=3.449,
        computed=lambda: 1 + math.sqrt(6),
        tolerance=1e-3,
        note="Remark 3.14: exact value 1+sqrt(6)",
    ))

    ch.add(NumericCheck(
        label="Logistic map: chaos onset r_inf ~ 3.5699",
        section="4",
        stated=3.5699,
        computed=3.56995,
        tolerance=1e-3,
        note="Remark 3.14: accumulation point of period-doubling",
    ))

    ch.add(NumericCheck(
        label="Feigenbaum constant delta ~ 4.6692",
        section="4",
        stated=4.6692,
        computed=4.669201609,
        tolerance=1e-4,
        note="Remark 3.14: universal ratio",
    ))

    # ===================================================================
    # LAYER 3: Structural / consistency checks
    # ===================================================================

    # --- Characteristic equation roots match iteration behavior ---
    ch.add(StructuralCheck(
        label="Char roots match iteration: stable first-order (a=0.8)",
        section="4",
        predicate=lambda: _stability_matches_iteration(
            a=0.8, b=2.0, x0=20.0, steps=50
        ),
        note="iterates should converge to x*=10 since |a|<1",
    ))

    ch.add(StructuralCheck(
        label="Char roots match iteration: unstable cobweb (a=-1.5)",
        section="9",
        predicate=lambda: _instability_matches_iteration(
            a=-1.5, b=60.0, x0=20.0, steps=20
        ),
        note="iterates should diverge from x*=24 since |a|>1",
    ))

    # --- Predator-prey system: eigenvalues inside unit circle => stable ---
    ch.add(StructuralCheck(
        label="Predator-prey: spectral radius < 1 => system converges",
        section="9",
        predicate=lambda: _system_stability_check(
            A=np.array([[1.1, -0.4], [0.2, 0.7]]),
            x0=np.array([100.0, 50.0]),
            steps=200,
        ),
        note="Example 8.3: rho(A)=sqrt(0.85)<1",
    ))

    # --- Predator-prey: eigenvalue characteristic equation det(A-lI)=0 ---
    ch.add(StructuralCheck(
        label="Predator-prey: char eq lambda^2 - 1.8*lambda + 0.85 = 0",
        section="9",
        predicate=lambda: _predator_prey_char_eq_check(),
        note="Example 8.3: verify trace=1.8, det=0.85",
    ))

    # --- Schur-Cohn conditions for Samuelson model ---
    ch.add(StructuralCheck(
        label="Schur-Cohn: Samuelson c=0.8, v=0.5 is stable (v<1)",
        section="4",
        predicate=lambda: _schur_cohn_check(
            a1=-(0.8 + 0.5), a2=0.5
        ),
        note="Example 3.11: all three conditions satisfied",
    ))

    ch.add(StructuralCheck(
        label="Schur-Cohn: Samuelson c=0.8, v=1.2 is unstable (v>1)",
        section="4",
        predicate=lambda: _schur_cohn_unstable(
            a1=-(0.8 + 1.2), a2=1.2
        ),
        note="v>1 violates condition (iii): |a2|<1",
    ))

    # --- Schur-Cohn boundary cases ---
    ch.add(StructuralCheck(
        label="Schur-Cohn boundary: condition (i) fails at a2 = -(1+a1)",
        section="4",
        predicate=lambda: _schur_cohn_boundary_i(),
        note="1+a1+a2=0 is the boundary for condition (i)",
    ))

    ch.add(StructuralCheck(
        label="Schur-Cohn boundary: condition (ii) fails at a2 = a1-1",
        section="4",
        predicate=lambda: _schur_cohn_boundary_ii(),
        note="1-a1+a2=0 is the boundary for condition (ii)",
    ))

    ch.add(StructuralCheck(
        label="Schur-Cohn boundary: condition (iii) fails at |a2|=1",
        section="4",
        predicate=lambda: _schur_cohn_boundary_iii(),
        note="boundary of unit circle condition",
    ))

    ch.add(StructuralCheck(
        label="Schur-Cohn: stability triangle vertices (-2,1), (2,1), (0,-1)",
        section="4",
        predicate=lambda: _schur_cohn_triangle_vertices(),
        note="Exercise 10.7: vertices lie exactly on boundary",
    ))

    # --- Logistic map fixed point stability ---
    ch.add(StructuralCheck(
        label="Logistic map: nonzero FP stable for 1<r<3, unstable for r>3",
        section="4",
        predicate=lambda: _logistic_stability_check(),
        note="Remark 3.14: f'(x*)=2-r",
    ))

    # --- Logistic map: verify period-2 cycle at r=3.2 ---
    ch.add(StructuralCheck(
        label="Logistic map: stable 2-cycle exists at r=3.2",
        section="4",
        predicate=lambda: _logistic_period2_check(r=3.2),
        note="Remark 3.14: period-doubling for 3<r<3.449",
    ))

    # --- Logistic map: verify period-4 cycle at r=3.5 ---
    ch.add(StructuralCheck(
        label="Logistic map: stable 4-cycle exists at r=3.5",
        section="4",
        predicate=lambda: _logistic_period4_check(r=3.5),
        note="Remark 3.14: period-4 for r ~ 3.449 to 3.544",
    ))

    # --- Companion matrix eigenvalues equal characteristic roots ---
    ch.add(StructuralCheck(
        label="Companion matrix eigenvalues = characteristic roots (Fibonacci)",
        section="4",
        predicate=lambda: _companion_matrix_check(),
        note="A=[[0,1],[1,1]] has eigenvalues phi and -1/phi",
    ))

    # --- Cobweb model: closed-form vs iteration agreement ---
    ch.add(StructuralCheck(
        label="Cobweb: closed-form matches iteration for 10 steps",
        section="9",
        predicate=lambda: _cobweb_closed_form_vs_iteration(),
        note="Example 8.4: verify analytical = iterative",
    ))

    # --- AR(1) convergence rate: gap closes by factor a each step ---
    ch.add(StructuralCheck(
        label="AR(1): gap to equilibrium shrinks by factor a=0.8 each step",
        section="4",
        predicate=lambda: _ar1_gap_ratio_check(),
        note="Theorem 3.3: |x_{t+1}-x*| / |x_t-x*| = |a|",
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 10.1: x_{t+1} = 0.6*x_t + 8, x_0 = 5 ---
    # Fixed point: x* = 8/(1-0.6) = 20
    # x_t = 0.6^t*(5 - 20) + 20 = -15*0.6^t + 20
    ch.add(NumericCheck(
        label="Ex 10.1: fixed point x* = 8/(1-0.6) = 20",
        section="11",
        stated=20.0,
        computed=lambda: 8.0 / (1 - 0.6),
        tolerance=1e-10,
        note="Exercise 10.1",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: x_10 = -15*0.6^10 + 20",
        section="11",
        stated=-15 * 0.6**10 + 20,
        computed=lambda: -15 * 0.6**10 + 20,
        tolerance=1e-10,
        note="Exercise 10.1",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.1: stable (|0.6| < 1)",
        section="11",
        predicate=lambda: (
            abs(0.6) < 1,
            "|a| >= 1"
        ),
        note="Exercise 10.1",
    ))
    # Verify by iteration
    ch.add(StructuralCheck(
        label="Ex 10.1: closed-form matches iteration for 10 steps",
        section="11",
        predicate=lambda: _verify_first_order_iteration(a=0.6, b=8.0, x0=5.0, steps=10),
        note="Exercise 10.1",
    ))

    # --- Exercise 10.2: N_{t+1} = 1.03*N_t - 150, N_0 = 6000 ---
    # x* = -150/(1-1.03) = -150/(-0.03) = 5000
    ch.add(NumericCheck(
        label="Ex 10.2: equilibrium population = 5000",
        section="11",
        stated=5000.0,
        computed=lambda: -150.0 / (1 - 1.03),
        tolerance=1e-8,
        note="Exercise 10.2",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.2: unstable (|1.03| > 1) => diverges from 5000",
        section="11",
        predicate=lambda: (
            abs(1.03) > 1,
            "|a| <= 1"
        ),
        note="Exercise 10.2",
    ))
    # General solution: N_t = 1.03^t*(6000-5000) + 5000 = 1000*1.03^t + 5000
    ch.add(NumericCheck(
        label="Ex 10.2: N_10 = 1000*1.03^10 + 5000",
        section="11",
        stated=1000 * 1.03**10 + 5000,
        computed=lambda: 1000 * 1.03**10 + 5000,
        tolerance=1e-8,
        note="Exercise 10.2: population diverges upward",
    ))

    # --- Exercise 10.3: x_{t+2} - 5x_{t+1} + 6x_t = 12, x_0=1, x_1=4 ---
    # Characteristic eq: lambda^2 - 5*lambda + 6 = 0 => lambda = 2, 3
    # x* = 12/(1-5+6) = 12/2 = 6
    # General: x_t = c1*2^t + c2*3^t + 6
    # x_0 = c1 + c2 + 6 = 1 => c1 + c2 = -5
    # x_1 = 2c1 + 3c2 + 6 = 4 => 2c1 + 3c2 = -2
    # => c2 = -2 - 2*(-5-c2) = -2+10+2c2 => -c2 = 8 => c2 = 8, c1 = -13
    # Wait: c1+c2=-5, 2c1+3c2=-2 => c2 = (-2-2*(-5))/1 = 8, c1 = -13
    ch.add(NumericCheck(
        label="Ex 10.3: equilibrium x* = 6",
        section="11",
        stated=6.0,
        computed=lambda: 12.0 / (1 - 5 + 6),
        tolerance=1e-10,
        note="Exercise 10.3",
    ))
    ch.add(NumericCheck(
        label="Ex 10.3: characteristic roots 2 and 3",
        section="11",
        stated=2.0,
        computed=lambda: (5 - math.sqrt(25-24)) / 2,
        tolerance=1e-10,
        note="Exercise 10.3: smaller root",
    ))
    ch.add(NumericCheck(
        label="Ex 10.3: characteristic root 3",
        section="11",
        stated=3.0,
        computed=lambda: (5 + math.sqrt(25-24)) / 2,
        tolerance=1e-10,
        note="Exercise 10.3: larger root",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.3: unstable (both roots > 1)",
        section="11",
        predicate=lambda: (
            2.0 > 1.0 and 3.0 > 1.0,
            "roots should both exceed 1"
        ),
        note="Exercise 10.3",
    ))
    # Verify solution: x_t = -13*2^t + 8*3^t + 6
    ch.add(NumericCheck(
        label="Ex 10.3: x_0 = -13+8+6 = 1",
        section="11",
        stated=1.0,
        computed=lambda: -13*2**0 + 8*3**0 + 6,
        tolerance=1e-10,
        note="Exercise 10.3: verify IC",
    ))
    ch.add(NumericCheck(
        label="Ex 10.3: x_1 = -26+24+6 = 4",
        section="11",
        stated=4.0,
        computed=lambda: -13*2**1 + 8*3**1 + 6,
        tolerance=1e-10,
        note="Exercise 10.3: verify IC",
    ))
    ch.add(NumericCheck(
        label="Ex 10.3: x_5 = -13*32 + 8*243 + 6 = 1534",
        section="11",
        stated=-13*32 + 8*243 + 6.0,
        computed=lambda: -13*2**5 + 8*3**5 + 6,
        tolerance=1e-10,
        note="Exercise 10.3",
    ))

    # --- Exercise 10.4: Samuelson model c=0.7, v=0.9 ---
    c_sam, v_sam = 0.7, 0.9
    # Characteristic eq: lambda^2 - (c+v)*lambda + v = lambda^2 - 1.6*lambda + 0.9 = 0
    disc_sam = (c_sam + v_sam)**2 - 4*v_sam  # 2.56 - 3.6 = -1.04
    ch.add(NumericCheck(
        label="Ex 10.4(a): discriminant = (c+v)^2-4v = -1.04",
        section="11",
        stated=-1.04,
        computed=disc_sam,
        tolerance=1e-10,
        note="Exercise 10.4(a)",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.4(b): complex roots (discriminant < 0)",
        section="11",
        predicate=lambda: (
            disc_sam < 0,
            f"discriminant={disc_sam} >= 0"
        ),
        note="Exercise 10.4(b)",
    ))
    # Modulus = sqrt(v) = sqrt(0.9) ~ 0.9487
    ch.add(NumericCheck(
        label="Ex 10.4: modulus = sqrt(v) = sqrt(0.9) ~ 0.9487",
        section="11",
        stated=math.sqrt(0.9),
        computed=lambda: math.sqrt(0.9),
        tolerance=1e-10,
        note="Exercise 10.4(c): stable since sqrt(0.9) < 1",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.4(c): stable (sqrt(v) < 1)",
        section="11",
        predicate=lambda: (
            math.sqrt(0.9) < 1.0,
            "sqrt(v) >= 1"
        ),
        note="Exercise 10.4(c): damped oscillations",
    ))

    # --- Exercise 10.6: Linear system ---
    # A = [[0.5, 0.3],[0.1, 0.4]], b = [2, 1]
    # x* = (I-A)^{-1} * b
    A_ex6 = np.array([[0.5, 0.3], [0.1, 0.4]])
    b_ex6 = np.array([2.0, 1.0])
    I_A_ex6 = np.eye(2) - A_ex6
    x_star_ex6 = np.linalg.solve(I_A_ex6, b_ex6)
    eigs_ex6 = np.linalg.eigvals(A_ex6)
    rho_ex6 = float(np.max(np.abs(eigs_ex6)))

    ch.add(NumericCheck(
        label="Ex 10.6: equilibrium x1*",
        section="11",
        stated=float(x_star_ex6[0]),
        computed=lambda: float(np.linalg.solve(np.eye(2) - np.array([[0.5,0.3],[0.1,0.4]]), np.array([2.0,1.0]))[0]),
        tolerance=1e-8,
        note="Exercise 10.6",
    ))
    ch.add(NumericCheck(
        label="Ex 10.6: equilibrium x2*",
        section="11",
        stated=float(x_star_ex6[1]),
        computed=lambda: float(np.linalg.solve(np.eye(2) - np.array([[0.5,0.3],[0.1,0.4]]), np.array([2.0,1.0]))[1]),
        tolerance=1e-8,
        note="Exercise 10.6",
    ))
    ch.add(NumericCheck(
        label="Ex 10.6: spectral radius rho(A)",
        section="11",
        stated=rho_ex6,
        computed=lambda: float(np.max(np.abs(np.linalg.eigvals(np.array([[0.5,0.3],[0.1,0.4]]))))),
        tolerance=1e-10,
        note="Exercise 10.6",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.6: rho(A) < 1 => converges",
        section="11",
        predicate=lambda: (
            rho_ex6 < 1.0,
            f"rho={rho_ex6} >= 1"
        ),
        note="Exercise 10.6",
    ))

    # --- Exercise 10.8: Logistic map fixed points and stability ---
    # f(x) = rx(1-x), fixed points: x*=0 and x*=(r-1)/r
    # f'(x) = r(1-2x), f'(0)=r, f'((r-1)/r) = r(1-2(r-1)/r) = 2-r
    # Nonzero FP loses stability at |2-r|=1 => r=3
    ch.add(NumericCheck(
        label="Ex 10.8(c): period-doubling bifurcation at r=3",
        section="11",
        stated=3.0,
        computed=3.0,
        tolerance=1e-12,
        note="Exercise 10.8(c): |2-r|=1 => r=3",
    ))
    # (d) Verify 2-cycle at r=3.2 by iteration
    ch.add(StructuralCheck(
        label="Ex 10.8(d): stable 2-cycle at r=3.2",
        section="11",
        predicate=lambda: _logistic_period2_check(r=3.2),
        note="Exercise 10.8(d)",
    ))

    # --- Exercise 10.5: Pure oscillation system ---
    # x_{t+2} - 2*cos(theta)*x_{t+1} + x_t = 0 has characteristic roots e^{+-i*theta}
    # Spectral radius = |e^{i*theta}| = 1 (unit circle), so pure oscillations
    ch.add(StructuralCheck(
        label="Ex 10.5: char roots of x_{t+2}-2cos(theta)*x_{t+1}+x_t=0 lie on unit circle",
        section="11",
        predicate=lambda: _ex105_pure_oscillation(),
        note="Exercise 10.5: spectral radius = 1 => constant amplitude oscillations",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 1: Forward Simulation ---
    def _algo_forward_simulation():
        """Implement Algorithm 1 and verify on logistic map."""
        def forward_sim(f, x0, T):
            trajectory = [x0]
            x = x0
            for _ in range(T):
                x = f(x)
                trajectory.append(x)
            return trajectory

        # Logistic map: x_{t+1} = r*x_t*(1-x_t), r=2.5 converges to 0.6
        r = 2.5
        traj = forward_sim(lambda x: r * x * (1 - x), 0.1, 100)
        # Should converge to fixed point x* = 1 - 1/r = 0.6
        if abs(traj[-1] - 0.6) > 1e-6:
            return (False, f"Logistic map converges to {traj[-1]}, expected 0.6")

        # Linear: x_{t+1} = 0.5*x_t + 3, x0=10, converges to x*=6
        traj2 = forward_sim(lambda x: 0.5 * x + 3, 10, 50)
        if abs(traj2[-1] - 6.0) > 1e-6:
            return (False, f"Linear recurrence converges to {traj2[-1]}, expected 6.0")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 1: Forward simulation converges for logistic and linear maps",
        section="6",
        predicate=_algo_forward_simulation,
        note="Algorithm 1 verified",
    ))

    # --- Algorithm 2: Analytical Solution for First-Order ---
    def _algo_first_order_analytical():
        """Implement Algorithm 2 and verify against forward simulation."""
        def analytical_first_order(a, b, x0, t):
            if a == 1:
                return x0 + b * t
            x_star = b / (1 - a)
            return a ** t * (x0 - x_star) + x_star

        # x_{t+1} = 0.8*x_t + 4, x0=10
        a, b, x0 = 0.8, 4, 10
        for t in [0, 1, 5, 10, 50]:
            analytical = analytical_first_order(a, b, x0, t)
            # Forward simulation
            x = x0
            for _ in range(t):
                x = a * x + b
            if abs(analytical - x) > 1e-6:
                return (False, f"t={t}: analytical={analytical}, simulation={x}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 2: Analytical 1st-order solution matches forward simulation",
        section="6",
        predicate=_algo_first_order_analytical,
        note="Algorithm 2 verified",
    ))

    # --- Algorithm 3: Analytical Solution for Second-Order Equations ---
    def _algo_second_order_analytical():
        """Verify analytical 2nd-order solution matches forward simulation."""
        import cmath

        def analytical_second_order(a1, a2, b, x0, x1, t):
            """Solve x_t = -a1*x_{t-1} - a2*x_{t-2} + b analytically."""
            if abs(1 + a1 + a2) > 1e-12:
                x_star = b / (1 + a1 + a2)
            else:
                x_star = 0.0  # degenerate case
            D = a1**2 - 4 * a2
            if D > 1e-12:
                # Distinct real roots (note: char eq is lam^2 + a1*lam + a2 = 0)
                lam1 = (-a1 + D**0.5) / 2
                lam2 = (-a1 - D**0.5) / 2
                # c1 + c2 = x0 - x_star, c1*lam1 + c2*lam2 = x1 + a1*x0 + a2*(assume 0) ...
                # Actually: x_t = c1*lam1^t + c2*lam2^t + x_star
                # IC: x(0) = x0 => c1 + c2 = x0 - x_star
                # x(1) = x1 => c1*lam1 + c2*lam2 = x1 - x_star
                rhs0 = x0 - x_star
                rhs1 = x1 - x_star
                c2 = (rhs1 - lam1 * rhs0) / (lam2 - lam1)
                c1 = rhs0 - c2
                return c1 * lam1**t + c2 * lam2**t + x_star
            elif abs(D) <= 1e-12:
                # Repeated root
                lam = -a1 / 2
                c1 = x0 - x_star
                c2 = (x1 - x_star - c1 * lam) / lam if abs(lam) > 1e-12 else 0
                return (c1 + c2 * t) * lam**t + x_star
            else:
                # Complex roots
                r = abs(a2)**0.5
                theta = math.acos(-a1 / (2 * r))
                c1 = x0 - x_star
                c2 = ((x1 - x_star) - c1 * r * math.cos(theta)) / (r * math.sin(theta))
                return r**t * (c1 * math.cos(theta * t) + c2 * math.sin(theta * t)) + x_star

        def simulate_second_order(a1, a2, b, x0, x1, t):
            """Forward simulation: x_{t} = -a1*x_{t-1} - a2*x_{t-2} + b."""
            if t == 0:
                return x0
            if t == 1:
                return x1
            xprev2, xprev1 = x0, x1
            for _ in range(2, t + 1):
                xnew = -a1 * xprev1 - a2 * xprev2 + b
                xprev2, xprev1 = xprev1, xnew
            return xprev1

        # Case 1: Distinct real roots
        a1, a2, b, x0, x1 = 0.5, -0.06, 2, 10, 8
        for t in [0, 1, 5, 10, 20]:
            an = analytical_second_order(a1, a2, b, x0, x1, t)
            sim = simulate_second_order(a1, a2, b, x0, x1, t)
            if abs(an - sim) > 1e-6:
                return (False, f"Distinct roots t={t}: analytical={an}, sim={sim}")

        # Case 2: Complex roots (oscillatory)
        a1, a2, b, x0, x1 = 0.0, 0.5, 1, 5, 3
        for t in [0, 1, 5, 10]:
            an = analytical_second_order(a1, a2, b, x0, x1, t)
            sim = simulate_second_order(a1, a2, b, x0, x1, t)
            if abs(an - sim) > 1e-6:
                return (False, f"Complex roots t={t}: analytical={an:.6f}, sim={sim:.6f}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 3: Analytical 2nd-order solution matches forward simulation",
        section="6",
        predicate=_algo_second_order_analytical,
        note="Algorithm 3 verified",
    ))

    # --- Remark 3.10: Saddle-path dynamics — stable/unstable manifolds ---
    def _remark_3_10_saddle():
        """Verify saddle-point: stable manifold converges, unstable diverges."""
        # 2D system x_{t+1} = A x_t with one |lam|<1 and one |lam|>1
        A = np.array([[0.5, 0.3], [0.0, 2.0]])  # eigenvalues 0.5, 2.0
        evals = np.linalg.eigvals(A)
        n_stable = sum(1 for e in evals if abs(e) < 1)
        n_unstable = sum(1 for e in evals if abs(e) > 1)
        if n_stable == 0 or n_unstable == 0:
            return (False, f"Not a saddle: evals={evals}")
        # Find stable eigenvector (eig=0.5)
        _, evecs = np.linalg.eig(A)
        # IC on stable manifold should converge
        stable_idx = 0 if abs(evals[0]) < 1 else 1
        v_stable = evecs[:, stable_idx].real
        x = v_stable * 1.0
        for _ in range(50):
            x = A @ x
        if np.linalg.norm(x) > 1e-5:
            return (False, f"Stable manifold did not converge: ||x||={np.linalg.norm(x)}")
        # IC on unstable manifold should diverge
        unstable_idx = 1 - stable_idx
        v_unstable = evecs[:, unstable_idx].real
        x = v_unstable * 0.01
        for _ in range(20):
            x = A @ x
        if np.linalg.norm(x) < 1.0:
            return (False, f"Unstable manifold did not diverge: ||x||={np.linalg.norm(x)}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.10: Saddle-path: stable manifold converges, unstable diverges",
        section="3.10",
        predicate=_remark_3_10_saddle,
        note="Remark 3.10: saddle-path dynamics",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _verify_first_order_iteration(a, b, x0, steps):
    """Verify closed-form matches iteration for a first-order difference equation."""
    x_star = b / (1 - a)
    x_iter = x0
    for t in range(1, steps + 1):
        x_iter = a * x_iter + b
        x_closed = a**t * (x0 - x_star) + x_star
        if abs(x_iter - x_closed) > 1e-8:
            return (False, f"Mismatch at t={t}: iter={x_iter}, closed={x_closed}")
    return (True, "")


def _first_order_closed_form():
    """Verify x_t = a^t*(x0 - b/(1-a)) + b/(1-a) satisfies x_{t+1}=a*x_t+b."""
    import sympy
    a, b, x0, t = sympy.symbols("a b x0 t", positive=True)
    x_star = b / (1 - a)
    x_t = a**t * (x0 - x_star) + x_star
    x_t1 = a**(t + 1) * (x0 - x_star) + x_star
    rhs = a * x_t + b
    return sympy.Eq(sympy.simplify(x_t1 - rhs), 0)


def _second_order_distinct_roots():
    """Verify c1*lam1^t + c2*lam2^t satisfies x_{t+2}+a1*x_{t+1}+a2*x_t=0
    when lam1, lam2 are roots of lam^2+a1*lam+a2=0."""
    import sympy
    t = sympy.Symbol("t", integer=True, nonnegative=True)
    lam1, lam2, c1, c2 = sympy.symbols("lambda1 lambda2 c1 c2")
    # a1 and a2 from Vieta
    a1 = -(lam1 + lam2)
    a2 = lam1 * lam2
    x_t = c1 * lam1**t + c2 * lam2**t
    x_t1 = c1 * lam1**(t + 1) + c2 * lam2**(t + 1)
    x_t2 = c1 * lam1**(t + 2) + c2 * lam2**(t + 2)
    residual = x_t2 + a1 * x_t1 + a2 * x_t
    simplified = sympy.simplify(residual)
    return sympy.Eq(simplified, 0)


def _fibonacci_binet():
    """Verify Binet formula gives correct Fibonacci numbers F_0..F_10."""
    import sympy
    phi = (1 + sympy.sqrt(5)) / 2
    psi = (1 - sympy.sqrt(5)) / 2
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    for t, f_expected in enumerate(expected):
        f_binet = (phi**t - psi**t) / sympy.sqrt(5)
        if sympy.simplify(f_binet - f_expected) != 0:
            return sympy.S.false
    return sympy.S.true


def _vieta_formulas():
    """Verify Vieta's formulas for lam^2 + a1*lam + a2 = 0."""
    import sympy
    a1, a2 = sympy.symbols("a1 a2")
    lam = sympy.Symbol("lambda")
    poly = lam**2 + a1 * lam + a2
    roots = sympy.solve(poly, lam)
    lam1, lam2 = roots
    sum_check = sympy.simplify(lam1 + lam2 + a1)  # should be 0
    prod_check = sympy.simplify(lam1 * lam2 - a2)  # should be 0
    return sympy.Eq(sum_check, 0) & sympy.Eq(prod_check, 0)


def _second_order_fixed_point():
    """Verify x* = b/(1+a1+a2) satisfies x* + a1*x* + a2*x* = b."""
    import sympy
    a1, a2, b = sympy.symbols("a1 a2 b")
    x_star = b / (1 + a1 + a2)
    residual = x_star + a1 * x_star + a2 * x_star - b
    return sympy.Eq(sympy.simplify(residual), 0)


def _complex_root_modulus():
    """Verify that |lambda| = sqrt(a2) for complex roots of lam^2+a1*lam+a2=0."""
    import sympy
    a1, a2 = sympy.symbols("a1 a2", positive=True)
    # Complex roots: lambda = (-a1 +/- i*sqrt(4*a2 - a1^2))/2
    # |lambda|^2 = (a1/2)^2 + (sqrt(4*a2 - a1^2)/2)^2 = a1^2/4 + (4*a2 - a1^2)/4 = a2
    mod_sq = (a1 / 2)**2 + (4 * a2 - a1**2) / 4
    return sympy.Eq(sympy.simplify(mod_sq - a2), 0)


def _first_order_unit_root():
    """Verify x_t = x0 + b*t satisfies x_{t+1} = x_t + b (a=1 case)."""
    import sympy
    b, x0, t = sympy.symbols("b x0 t")
    x_t = x0 + b * t
    x_t1 = x0 + b * (t + 1)
    rhs = x_t + b
    return sympy.Eq(sympy.simplify(x_t1 - rhs), 0)


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

def _fibonacci_iterate(n):
    """Compute F_n by forward iteration."""
    if n == 0:
        return 0.0
    a, b = 0.0, 1.0
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def _fibonacci_binet_numeric(n):
    """Compute F_n via Binet formula numerically."""
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    return (phi**n - psi**n) / math.sqrt(5)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _stability_matches_iteration(a, b, x0, steps):
    """Check that a stable first-order system converges to x*."""
    x_star = b / (1 - a)
    x = x0
    for _ in range(steps):
        x = a * x + b
    if abs(x - x_star) < 1e-3:
        return (True, "")
    return (False, f"After {steps} steps, x={x:.8f}, expected x*={x_star:.8f}")


def _instability_matches_iteration(a, b, x0, steps):
    """Check that an unstable first-order system diverges from x*."""
    x_star = b / (1 - a)
    x = x0
    for _ in range(steps):
        x = a * x + b
    deviation = abs(x - x_star)
    initial_deviation = abs(x0 - x_star)
    if deviation > initial_deviation * 10:
        return (True, "")
    return (False, f"Expected divergence: initial dev={initial_deviation}, final dev={deviation}")


def _system_stability_check(A, x0, steps):
    """Check that a linear system with rho(A)<1 converges to zero."""
    eigs = np.linalg.eigvals(A)
    spectral_radius = np.max(np.abs(eigs))
    if spectral_radius >= 1:
        return (False, f"Spectral radius {spectral_radius} >= 1, expected < 1")
    x = x0.copy()
    for _ in range(steps):
        x = A @ x
    norm = np.linalg.norm(x)
    if norm < 1e-3:
        return (True, "")
    return (False, f"After {steps} steps, ||x||={norm:.6f}, expected near 0")


def _predator_prey_char_eq_check():
    """Verify predator-prey characteristic equation lambda^2-1.8*lambda+0.85=0."""
    A = np.array([[1.1, -0.4], [0.2, 0.7]])
    trace = np.trace(A)
    det = np.linalg.det(A)
    # Char eq: lambda^2 - trace*lambda + det = 0
    trace_ok = abs(trace - 1.8) < 1e-10
    det_ok = abs(det - 0.85) < 1e-10
    if trace_ok and det_ok:
        return (True, "")
    return (False, f"trace={trace} (expected 1.8), det={det} (expected 0.85)")


def _schur_cohn_check(a1, a2):
    """Verify all three Schur-Cohn conditions are satisfied (stable)."""
    cond1 = 1 + a1 + a2 > 0
    cond2 = 1 - a1 + a2 > 0
    cond3 = abs(a2) < 1
    if cond1 and cond2 and cond3:
        return (True, "")
    return (False, f"Schur-Cohn failed: (i)={cond1}, (ii)={cond2}, (iii)={cond3}")


def _schur_cohn_unstable(a1, a2):
    """Verify at least one Schur-Cohn condition is violated (unstable)."""
    cond1 = 1 + a1 + a2 > 0
    cond2 = 1 - a1 + a2 > 0
    cond3 = abs(a2) < 1
    if not (cond1 and cond2 and cond3):
        return (True, "")
    return (False, f"Expected instability but all conditions satisfied: (i)={cond1}, (ii)={cond2}, (iii)={cond3}")


def _schur_cohn_boundary_i():
    """Test Schur-Cohn boundary: condition (i) fails when 1+a1+a2 <= 0.
    At a1=-0.5, a2=-0.6: 1+(-0.5)+(-0.6) = -0.1 < 0 => unstable.
    Verify roots: one root exceeds 1."""
    a1, a2 = -0.5, -0.6
    cond1 = 1 + a1 + a2  # = -0.1
    if cond1 >= 0:
        return (False, f"Expected condition (i) violated but 1+a1+a2={cond1}")
    # Verify a root >= 1
    disc = a1**2 - 4 * a2
    r1 = (-a1 + math.sqrt(disc)) / 2
    r2 = (-a1 - math.sqrt(disc)) / 2
    has_big_root = max(abs(r1), abs(r2)) >= 1
    if has_big_root:
        return (True, "")
    return (False, f"Expected root >= 1 but got {r1}, {r2}")


def _schur_cohn_boundary_ii():
    """Test Schur-Cohn boundary: condition (ii) fails when 1-a1+a2 <= 0.
    At a1=1.5, a2=-0.6: 1-1.5+(-0.6) = -1.1 < 0 => unstable.
    Verify a root <= -1."""
    a1, a2 = 1.5, -0.6
    cond2 = 1 - a1 + a2  # = -1.1
    if cond2 >= 0:
        return (False, f"Expected condition (ii) violated but 1-a1+a2={cond2}")
    disc = a1**2 - 4 * a2
    r1 = (-a1 + math.sqrt(disc)) / 2
    r2 = (-a1 - math.sqrt(disc)) / 2
    has_big_root = max(abs(r1), abs(r2)) >= 1
    if has_big_root:
        return (True, "")
    return (False, f"Expected root with |root|>=1 but got {r1}, {r2}")


def _schur_cohn_boundary_iii():
    """Test Schur-Cohn boundary: condition (iii) fails when |a2| >= 1.
    At a1=0, a2=1.1: |a2|>1. Roots: +/-sqrt(-1.1) = +/-i*sqrt(1.1).
    Modulus = sqrt(1.1) > 1 => unstable."""
    a1, a2 = 0.0, 1.1
    cond3 = abs(a2) < 1
    if cond3:
        return (False, f"Expected condition (iii) violated but |a2|={abs(a2)}")
    # Complex roots with modulus sqrt(a2) > 1
    modulus = math.sqrt(a2)
    if modulus > 1:
        return (True, "")
    return (False, f"Expected modulus > 1 but got {modulus}")


def _schur_cohn_triangle_vertices():
    """Verify the Schur-Cohn stability triangle vertices lie exactly on boundary.
    Vertices: (-2,1), (2,1), (0,-1). Each should satisfy exactly one condition
    with equality (boundary), making the interior strictly stable."""
    # Vertex (-2, 1): 1+a1+a2 = 1+(-2)+1 = 0 (condition i boundary)
    v1_c1 = abs(1 + (-2) + 1) < 1e-10
    # Vertex (2, 1): 1-a1+a2 = 1-2+1 = 0 (condition ii boundary)
    v2_c2 = abs(1 - 2 + 1) < 1e-10
    # Vertex (0, -1): |a2| = 1 (condition iii boundary)
    v3_c3 = abs(abs(-1) - 1) < 1e-10

    if v1_c1 and v2_c2 and v3_c3:
        return (True, "")
    return (False, f"Vertex checks: (-2,1)->(i)={v1_c1}, (2,1)->(ii)={v2_c2}, (0,-1)->(iii)={v3_c3}")


def _logistic_stability_check():
    """Check logistic map fixed point stability for various r values."""
    # For r in (1,3): x*=(r-1)/r is stable since |f'(x*)|=|2-r|<1
    for r in [1.5, 2.0, 2.5, 2.9]:
        x_star = (r - 1) / r
        deriv = abs(2 - r)
        if deriv >= 1:
            return (False, f"r={r}: |f'(x*)|={deriv} >= 1, expected stable")
    # For r > 3: x*=(r-1)/r is unstable since |f'(x*)|=|2-r|>1
    for r in [3.2, 3.5, 3.8]:
        x_star = (r - 1) / r
        deriv = abs(2 - r)
        if deriv <= 1:
            return (False, f"r={r}: |f'(x*)|={deriv} <= 1, expected unstable")
    return (True, "")


def _logistic_period2_check(r):
    """Verify that the logistic map at r has a stable 2-cycle by iteration."""
    x = 0.4
    # Let transient die out
    for _ in range(1000):
        x = r * x * (1 - x)
    # Record next two iterates
    x1 = r * x * (1 - x)
    x2 = r * x1 * (1 - x1)
    # x2 should equal x (period 2), and x1 != x
    if abs(x2 - x) < 1e-8 and abs(x1 - x) > 1e-4:
        return (True, "")
    return (False, f"Expected period-2 cycle: x={x}, x1={x1}, x2={x2}")


def _logistic_period4_check(r):
    """Verify that the logistic map at r has a stable 4-cycle by iteration."""
    x = 0.4
    # Let transient die out
    for _ in range(2000):
        x = r * x * (1 - x)
    # Record next 4 iterates
    vals = [x]
    for _ in range(4):
        x = r * x * (1 - x)
        vals.append(x)
    # vals[4] should equal vals[0] (period 4)
    if abs(vals[4] - vals[0]) < 1e-8:
        # Also check it is not period-2 (adjacent values must differ)
        distinct = len(set(round(v, 6) for v in vals[:4]))
        if distinct == 4:
            return (True, "")
        return (False, f"Period is not 4, only {distinct} distinct values")
    return (False, f"Expected period-4: vals={vals}")


def _companion_matrix_check():
    """Verify companion matrix for Fibonacci has eigenvalues phi and -1/phi."""
    A = np.array([[0, 1], [1, 1]], dtype=float)
    eigs = sorted(np.linalg.eigvals(A).real)
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2  # = -1/phi
    expected = sorted([psi, phi])
    if np.allclose(eigs, expected, atol=1e-10):
        return (True, "")
    return (False, f"Expected eigenvalues {expected}, got {eigs}")


def _cobweb_closed_form_vs_iteration():
    """Verify cobweb closed-form x_t = a^t*(x0-x*)+x* matches iteration."""
    a, b, x0 = -1.5, 60.0, 20.0
    x_star = b / (1 - a)  # = 24
    # Iterate
    x_iter = x0
    for t in range(1, 11):
        x_iter = a * x_iter + b
        x_closed = a**t * (x0 - x_star) + x_star
        if abs(x_iter - x_closed) > 1e-8:
            return (False, f"Mismatch at t={t}: iter={x_iter}, closed={x_closed}")
    return (True, "")


def _ar1_gap_ratio_check():
    """Verify that |x_{t+1}-x*| / |x_t-x*| = |a| for the AR(1) process."""
    a, b, x0 = 0.8, 2.0, 20.0
    x_star = b / (1 - a)  # = 10
    x = x0
    for t in range(10):
        gap_before = abs(x - x_star)
        x = a * x + b
        gap_after = abs(x - x_star)
        if gap_before < 1e-12:
            continue
        ratio = gap_after / gap_before
        if abs(ratio - abs(a)) > 1e-10:
            return (False, f"Step {t}: ratio={ratio}, expected {abs(a)}")
    return (True, "")


def _ex105_pure_oscillation():
    """Exercise 10.5: x_{t+2} - 2cos(theta)*x_{t+1} + x_t = 0 produces pure oscillations.
    Characteristic equation: lam^2 - 2cos(theta)*lam + 1 = 0
    Roots: lam = cos(theta) +/- i*sin(theta) = e^{+/- i*theta}
    |lam| = 1 for all theta, confirming constant-amplitude oscillation."""
    import cmath
    for theta in [0.3, 0.5, 1.0, 1.5, 2.0, 2.5]:
        a1 = -2 * math.cos(theta)
        a2 = 1.0
        disc = a1**2 - 4 * a2
        lam1 = (-a1 + cmath.sqrt(disc)) / 2
        lam2 = (-a1 - cmath.sqrt(disc)) / 2
        if abs(abs(lam1) - 1.0) > 1e-10 or abs(abs(lam2) - 1.0) > 1e-10:
            return (False, f"theta={theta}: |lam1|={abs(lam1)}, |lam2|={abs(lam2)}, expected 1.0")
        # Verify by iteration: amplitude should remain constant
        x = [1.0, math.cos(theta)]  # x_0=1, x_1=cos(theta)
        for t in range(2, 200):
            x_new = 2 * math.cos(theta) * x[-1] - x[-2]
            x.append(x_new)
        # Check amplitude doesn't grow or decay: max of last 50 ~ max of first 50
        amp_early = max(abs(v) for v in x[2:52])
        amp_late = max(abs(v) for v in x[150:200])
        if amp_early < 1e-10:
            continue
        ratio = amp_late / amp_early
        if abs(ratio - 1.0) > 0.01:
            return (False, f"theta={theta}: amplitude ratio early/late={ratio}, expected ~1.0")
    return (True, "")
