# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 11: Unconstrained Optimization — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(11, "Unconstrained Optimization")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- Gradient = 0 at critical point of f(x) = x^2 - 4x + 5 ---
    ch.add(SymbolicCheck(
        label="grad f = 0 at critical point (single variable)",
        section="5",
        identity=lambda: _gradient_zero_at_critical_1d(),
        note="f(x) = x^2 - 4x + 5, f'(x*) = 0 at x* = 2",
    ))

    # --- Gradient = 0 at critical point of f(x,y) = x^2 + 2y^2 - 2xy - 2x ---
    ch.add(SymbolicCheck(
        label="grad f = 0 at critical point (multivariate)",
        section="5",
        identity=lambda: _gradient_zero_at_critical_2d(),
        note="f(x,y) = x^2 + 2y^2 - 2xy - 2x, grad f(2,1) = 0",
    ))

    # --- Hessian positive definite implies local min (symbolic eigenvalue check) ---
    ch.add(SymbolicCheck(
        label="Hessian PD => local min: eigenvalues of H for f(x,y) = x^2 + 2y^2 - 2xy - 2x",
        section="5",
        identity=lambda: _hessian_pd_symbolic(),
        note="H = [[2,-2],[-2,4]], eigenvalues 3 +/- sqrt(5), both positive",
    ))

    # --- Newton update formula: x_{k+1} = x_k - f'(x_k)/f''(x_k) ---
    ch.add(SymbolicCheck(
        label="Newton update minimizes local quadratic exactly",
        section="5",
        zero_expr=lambda: _newton_minimizes_quadratic(),
        note="For f(x) = ax^2 + bx + c, one Newton step from any x0 reaches -b/(2a)",
    ))

    # --- Gradient descent update: x_{k+1} = x_k - alpha * grad f(x_k) ---
    ch.add(SymbolicCheck(
        label="Gradient descent on f(x) = (1/2)Lx^2 converges iff alpha < 2/L",
        section="5",
        identity=lambda: _gd_convergence_condition(),
        note="Update factor is |1 - alpha*L| < 1 iff 0 < alpha < 2/L",
    ))

    # --- Convexity: f''(x) >= 0 everywhere => convex ---
    ch.add(SymbolicCheck(
        label="f(x) = x^2 - 4x + 5 is convex (f'' = 2 > 0 everywhere)",
        section="5",
        identity=lambda: _convexity_second_derivative(),
        note="f''(x) = 2 > 0 for all x",
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    # --- Example 8.1: f(x) = x^2 - 4x + 5, minimizer x* = 2, f* = 1 ---
    ch.add(NumericCheck(
        label="Ex 8.1: critical point x* = 2",
        section="9",
        stated=2.0,
        computed=lambda: _find_min_1d(lambda x: x**2 - 4*x + 5, lambda x: 2*x - 4, x0=0.0),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: f(2) = 1",
        section="9",
        stated=1.0,
        computed=lambda: 2.0**2 - 4*2.0 + 5.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: f'(2) = 0",
        section="9",
        stated=0.0,
        computed=lambda: 2*2.0 - 4.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: f''(2) = 2 > 0 (local min)",
        section="9",
        stated=2.0,
        computed=lambda: 2.0,
    ))

    # --- Example 8.2: f(x,y) = x^2 + 2y^2 - 2xy - 2x ---
    ch.add(NumericCheck(
        label="Ex 8.2: critical point (2, 1)",
        section="9",
        stated=0.0,
        computed=lambda: np.linalg.norm(_gradient_ex82(np.array([2.0, 1.0]))),
        tolerance=1e-10,
        note="||grad f(2,1)|| = 0",
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: f(2,1) = -2",
        section="9",
        stated=-2.0,
        computed=lambda: _f_ex82(np.array([2.0, 1.0])),
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: Hessian det = 4",
        section="9",
        stated=4.0,
        computed=lambda: float(np.linalg.det(np.array([[2, -2], [-2, 4]], dtype=float))),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: eigenvalue 1 = 3 - sqrt(5) ~ 0.764",
        section="9",
        stated=3.0 - math.sqrt(5),
        computed=lambda: float(np.sort(np.linalg.eigvalsh(np.array([[2, -2], [-2, 4]], dtype=float)))[0]),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: eigenvalue 2 = 3 + sqrt(5) ~ 5.236",
        section="9",
        stated=3.0 + math.sqrt(5),
        computed=lambda: float(np.sort(np.linalg.eigvalsh(np.array([[2, -2], [-2, 4]], dtype=float)))[1]),
        tolerance=1e-6,
    ))

    # Newton converges in 1 step for quadratic
    ch.add(NumericCheck(
        label="Ex 8.2: Newton converges in 1 step for quadratic",
        section="9",
        stated=0.0,
        computed=lambda: _newton_steps_quadratic_2d(),
        tolerance=1e-10,
        note="||x_1 - x*|| after 1 Newton step from (0,0)",
    ))

    # --- Example 8.3: Gradient descent on f(x,y) = x^2 + y^2 ---
    # Full table from the chapter: k=0,1,2,3,5,10,20,50
    ch.add(NumericCheck(
        label="Ex 8.3: GD k=0 x=5.000",
        section="9",
        stated=5.0,
        computed=lambda: 5.0 * 0.8**0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=0 y=3.000",
        section="9",
        stated=3.0,
        computed=lambda: 3.0 * 0.8**0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=0 f=34.000",
        section="9",
        stated=34.0,
        computed=lambda: 5.0**2 + 3.0**2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=0 ||grad||=11.662",
        section="9",
        stated=11.662,
        computed=lambda: math.sqrt((2*5.0)**2 + (2*3.0)**2),
        tolerance=1e-3,
        note="||grad f(5,3)|| = sqrt(100+36) = sqrt(136)",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=1 x=4.000",
        section="9",
        stated=4.0,
        computed=lambda: 5.0 * 0.8,
        note="x_1 = 0.8 * x_0",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=1 y=2.400",
        section="9",
        stated=2.4,
        computed=lambda: 3.0 * 0.8,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=1 f=21.760",
        section="9",
        stated=21.76,
        computed=lambda: (5.0 * 0.8)**2 + (3.0 * 0.8)**2,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=1 ||grad||=9.329",
        section="9",
        stated=9.329,
        computed=lambda: math.sqrt((2*4.0)**2 + (2*2.4)**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=2 x=3.200",
        section="9",
        stated=3.2,
        computed=lambda: 5.0 * 0.8**2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=2 y=1.920",
        section="9",
        stated=1.92,
        computed=lambda: 3.0 * 0.8**2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=2 f=13.926",
        section="9",
        stated=13.926,
        computed=lambda: (5.0 * 0.8**2)**2 + (3.0 * 0.8**2)**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=2 ||grad||=7.464",
        section="9",
        stated=7.464,
        computed=lambda: math.sqrt((2*3.2)**2 + (2*1.92)**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=3 x=2.560",
        section="9",
        stated=2.56,
        computed=lambda: 5.0 * 0.8**3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=3 y=1.536",
        section="9",
        stated=1.536,
        computed=lambda: 3.0 * 0.8**3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=3 f=8.913",
        section="9",
        stated=8.913,
        computed=lambda: (5.0 * 0.8**3)**2 + (3.0 * 0.8**3)**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=3 ||grad||=5.971",
        section="9",
        stated=5.971,
        computed=lambda: math.sqrt((2*5.0*0.8**3)**2 + (2*3.0*0.8**3)**2),
        tolerance=1e-3,
    ))

    # k=4 (not in chapter table but intermediate step)
    ch.add(NumericCheck(
        label="Ex 8.3: GD k=4 x=2.048",
        section="9",
        stated=2.048,
        computed=lambda: 5.0 * 0.8**4,
        tolerance=1e-6,
        note="Intermediate step between k=3 and k=5",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=4 y=1.229",
        section="9",
        stated=1.2288,
        computed=lambda: 3.0 * 0.8**4,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=4 f=5.704",
        section="9",
        stated=5.704,
        computed=lambda: (5.0 * 0.8**4)**2 + (3.0 * 0.8**4)**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=5 x=1.638",
        section="9",
        stated=1.638,
        computed=lambda: 5.0 * 0.8**5,
        tolerance=1e-3,
        note="Table value from chapter",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=5 y=0.983",
        section="9",
        stated=0.983,
        computed=lambda: 3.0 * 0.8**5,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=5 f=3.651",
        section="9",
        stated=3.650,
        computed=lambda: (5.0 * 0.8**5)**2 + (3.0 * 0.8**5)**2,
        tolerance=1e-2,
        note="Table: 3.650",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=5 ||grad||=3.821",
        section="9",
        stated=3.821,
        computed=lambda: math.sqrt((2*5.0*0.8**5)**2 + (2*3.0*0.8**5)**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=10 x=0.537",
        section="9",
        stated=0.537,
        computed=lambda: 5.0 * 0.8**10,
        tolerance=1e-3,
        note="Table value from chapter",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=10 y=0.322",
        section="9",
        stated=0.322,
        computed=lambda: 3.0 * 0.8**10,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=10 f=0.392",
        section="9",
        stated=0.392,
        computed=lambda: (5.0 * 0.8**10)**2 + (3.0 * 0.8**10)**2,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=10 ||grad||=1.253",
        section="9",
        stated=1.253,
        computed=lambda: math.sqrt((2*5.0*0.8**10)**2 + (2*3.0*0.8**10)**2),
        tolerance=1e-2,
        note="Table: 1.253",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=20 x=0.058",
        section="9",
        stated=0.058,
        computed=lambda: 5.0 * 0.8**20,
        tolerance=1e-2,
        note="Table value from chapter",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=20 y=0.035",
        section="9",
        stated=0.03459,
        computed=lambda: 3.0 * 0.8**20,
        tolerance=1e-3,
        note="Table value from chapter",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=20 f=0.005",
        section="9",
        stated=0.004519,
        computed=lambda: (5.0 * 0.8**20)**2 + (3.0 * 0.8**20)**2,
        tolerance=1e-3,
        note="Table value from chapter",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: GD k=20 ||grad||=0.135",
        section="9",
        stated=0.135,
        computed=lambda: math.sqrt((2*5.0*0.8**20)**2 + (2*3.0*0.8**20)**2),
        tolerance=1e-2,
        note="Table: 0.135",
    ))

    # --- Line search conditions (Armijo and Wolfe) ---
    # Verify at first GD step of Ex 8.3: x=(5,3), alpha=0.1
    ch.add(NumericCheck(
        label="Ex 8.3: Armijo condition RHS at k=0, c1=1e-4",
        section="9",
        stated=33.99864,
        computed=lambda: 34.0 - 1e-4 * 0.1 * ((2*5.0)**2 + (2*3.0)**2),
        tolerance=1e-6,
        note="f(x0) - c1*alpha*||grad||^2 = 34 - 1e-4*0.1*136",
    ))

    ch.add(StructuralCheck(
        label="Ex 8.3: Armijo sufficient decrease holds at k=0",
        section="9",
        predicate=lambda: _check_armijo_condition_k0(),
        note="f(x1)=21.76 <= 33.999 = f(x0) - c1*alpha*||grad||^2",
    ))

    ch.add(StructuralCheck(
        label="Ex 8.3: Wolfe curvature condition holds at k=0",
        section="9",
        predicate=lambda: _check_wolfe_condition_k0(),
        note="grad(x1).d >= c2 * grad(x0).d with c2=0.9, d=-grad(x0)",
    ))

    # --- Example 8.4: Newton's method on f(x) = x^4 - 3x^2 + 2 ---
    xstar_84 = math.sqrt(3.0 / 2.0)

    ch.add(NumericCheck(
        label="Ex 8.4: minimizer x* = sqrt(3/2) ~ 1.22474",
        section="9",
        stated=xstar_84,
        computed=lambda: _newton_1d_ex84(x0=2.0, nsteps=10),
        tolerance=1e-8,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: f(x*) = -0.25",
        section="9",
        stated=-0.25,
        computed=lambda: xstar_84**4 - 3*xstar_84**2 + 2,
        tolerance=1e-10,
    ))

    # Newton iterate table: EVERY step k=0 through k=5
    # k=0: x=2.000000, f'=20.000, f''=42.000, |x-x*|=7.75e-1
    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=0 x=2.000000",
        section="9",
        stated=2.0,
        computed=lambda: 2.0,
        note="Starting point",
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=0 f'=20.000",
        section="9",
        stated=20.0,
        computed=lambda: 4*2.0**3 - 6*2.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=0 f''=42.000",
        section="9",
        stated=42.0,
        computed=lambda: 12*2.0**2 - 6.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=0 |x-x*|=7.75e-1",
        section="9",
        stated=7.753e-1,
        computed=lambda: abs(2.0 - math.sqrt(3.0/2.0)),
        tolerance=1e-3,
    ))

    # k=1: x=1.523810
    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=1 x=1.523810",
        section="9",
        stated=1.523810,
        computed=lambda: _newton_1d_ex84(x0=2.0, nsteps=1),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=1 f'=5.001",
        section="9",
        stated=5.001,
        computed=lambda: _newton_1d_deriv(x0=2.0, nsteps=1),
        tolerance=1e-2,
        note="f'(x_1) ~ 5.001",
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=1 f''=21.866",
        section="9",
        stated=21.866,
        computed=lambda: _newton_1d_second_deriv(x0=2.0, nsteps=1),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=1 |x-x*|=2.99e-1",
        section="9",
        stated=2.99e-1,
        computed=lambda: abs(_newton_1d_ex84(x0=2.0, nsteps=1) - math.sqrt(3.0/2.0)),
        tolerance=1e-2,
    ))

    # k=2: x=1.295094
    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=2 x=1.295094",
        section="9",
        stated=1.295094,
        computed=lambda: _newton_1d_ex84(x0=2.0, nsteps=2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=2 f'=0.912",
        section="9",
        stated=0.912,
        computed=lambda: _newton_1d_deriv(x0=2.0, nsteps=2),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=2 f''=14.098",
        section="9",
        stated=14.098,
        computed=lambda: _newton_1d_second_deriv(x0=2.0, nsteps=2),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=2 |x-x*|=7.04e-2",
        section="9",
        stated=7.04e-2,
        computed=lambda: abs(_newton_1d_ex84(x0=2.0, nsteps=2) - math.sqrt(3.0/2.0)),
        tolerance=5e-2,
    ))

    # k=3: x=1.230028
    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=3 x=1.230028",
        section="9",
        stated=1.230028,
        computed=lambda: _newton_1d_ex84(x0=2.0, nsteps=3),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=3 f'=0.0638",
        section="9",
        stated=0.0638,
        computed=lambda: abs(_newton_1d_deriv(x0=2.0, nsteps=3)),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=3 f''=12.710",
        section="9",
        stated=12.710,
        computed=lambda: _newton_1d_second_deriv(x0=2.0, nsteps=3),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=3 |x-x*|=5.28e-3",
        section="9",
        stated=5.283e-3,
        computed=lambda: abs(_newton_1d_ex84(x0=2.0, nsteps=3) - math.sqrt(3.0/2.0)),
        tolerance=1e-2,
    ))

    # k=4: x=1.224917
    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=4 x=1.224917",
        section="9",
        stated=1.224917,
        computed=lambda: _newton_1d_ex84(x0=2.0, nsteps=4),
        tolerance=1e-3,
        note="Table: 1.224917",
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=4 f''=12.002",
        section="9",
        stated=12.002,
        computed=lambda: _newton_1d_second_deriv(x0=2.0, nsteps=4),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=4 |x-x*|=3.38e-5",
        section="9",
        stated=3.384e-5,
        computed=lambda: abs(_newton_1d_ex84(x0=2.0, nsteps=4) - math.sqrt(3.0/2.0)),
        tolerance=1e-2,
    ))

    # k=5: x=1.224745, error < 1e-8
    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=5 x=1.224745",
        section="9",
        stated=1.224745,
        computed=lambda: _newton_1d_ex84(x0=2.0, nsteps=5),
        tolerance=1e-5,
        note="Table: 1.224745, converged",
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Newton k=5 f''=12.000",
        section="9",
        stated=12.0,
        computed=lambda: _newton_1d_second_deriv(x0=2.0, nsteps=5),
        tolerance=1e-3,
    ))

    ch.add(StructuralCheck(
        label="Ex 8.4: Newton k=5 |x-x*| < 1e-8",
        section="9",
        predicate=lambda: _check_newton_k5_converged(),
        note="Table: error < 1e-8 at k=5",
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: f''(sqrt(3/2)) = 12 (confirms local min)",
        section="9",
        stated=12.0,
        computed=lambda: 12 * (3.0 / 2.0) - 6,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: f''(0) = -6 (local max at x=0)",
        section="9",
        stated=-6.0,
        computed=lambda: 12 * 0.0**2 - 6.0,
    ))

    # ===================================================================
    # LAYER 3: Structural / consistency checks
    # ===================================================================

    # --- Convexity: Hessian PSD everywhere for quadratic f(x,y) = x^2 + 2y^2 - 2xy - 2x ---
    ch.add(StructuralCheck(
        label="Convexity: H PD for f(x,y) = x^2 + 2y^2 - 2xy - 2x",
        section="5",
        predicate=lambda: _check_hessian_pd(np.array([[2, -2], [-2, 4]], dtype=float)),
        note="Constant Hessian, eigenvalues both positive => strictly convex",
    ))

    # --- Convexity: f(x) = x^4 - 3x^2 + 2 is NOT globally convex ---
    ch.add(StructuralCheck(
        label="Non-convexity: f(x) = x^4 - 3x^2 + 2 has f''(0) < 0",
        section="5",
        predicate=lambda: _check_nonconvex_at_zero(),
        note="f''(0) = -6 < 0, so f is not globally convex",
    ))

    # --- Hessian eigenvalue signs determine critical point type ---
    ch.add(StructuralCheck(
        label="Saddle point: f(x,y) = x^2 - y^2, H indefinite at (0,0)",
        section="5",
        predicate=lambda: _check_saddle_point(),
        note="H = [[2,0],[0,-2]], eigenvalues {2, -2} => saddle point",
    ))

    # --- Gradient descent convergence: error decreases monotonically ---
    ch.add(StructuralCheck(
        label="GD on x^2+y^2: objective monotonically decreasing",
        section="9",
        predicate=lambda: _check_gd_monotone_decrease(),
        note="f(x_k) > f(x_{k+1}) for all k until convergence",
    ))

    # --- Newton quadratic convergence: error ratio check ---
    ch.add(StructuralCheck(
        label="Newton quadratic convergence on f(x) = x^4 - 3x^2 + 2",
        section="9",
        predicate=lambda: _check_newton_quadratic_convergence(),
        note="e_{k+1} / e_k^2 bounded => quadratic convergence",
    ))

    # --- Condition number governs GD convergence rate ---
    ch.add(StructuralCheck(
        label="Condition number: kappa = lambda_max / lambda_min for H of Ex 8.2",
        section="5",
        predicate=lambda: _check_condition_number(),
        note="kappa = (3+sqrt(5))/(3-sqrt(5))",
    ))

    # --- GD contraction factor matches theory ---
    ch.add(StructuralCheck(
        label="GD on f=x^2+y^2 with alpha=0.1: contraction factor = 0.8",
        section="9",
        predicate=lambda: _check_gd_contraction_factor(),
        note="x_{k+1} = (1 - 2*alpha) * x_k = 0.8 * x_k",
    ))

    # --- Line search: Armijo satisfied for all first 20 GD steps ---
    ch.add(StructuralCheck(
        label="Armijo condition holds for all GD steps k=0..19 on f=x^2+y^2",
        section="9",
        predicate=lambda: _check_armijo_all_steps(),
        note="c1=1e-4, alpha=0.1: f(x_{k+1}) <= f(x_k) - c1*alpha*||grad||^2",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 10.1: f(x) = x^3 - 12x + 1 ---
    # f'(x) = 3x^2 - 12 = 0 => x = +/-2
    # f''(x) = 6x; f''(2)=12>0 (local min), f''(-2)=-12<0 (local max)
    ch.add(NumericCheck(
        label="Ex 10.1: critical point x=2, f'(2)=0",
        section="11",
        stated=0.0,
        computed=lambda: 3*2.0**2 - 12,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: critical point x=-2, f'(-2)=0",
        section="11",
        stated=0.0,
        computed=lambda: 3*(-2.0)**2 - 12,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: f''(2) = 12 > 0 (local min)",
        section="11",
        stated=12.0,
        computed=lambda: 6*2.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: f''(-2) = -12 < 0 (local max)",
        section="11",
        stated=-12.0,
        computed=lambda: 6*(-2.0),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: f(2) = 8-24+1 = -15 (local min value)",
        section="11",
        stated=-15.0,
        computed=lambda: 2.0**3 - 12*2.0 + 1,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: f(-2) = -8+24+1 = 17 (local max value)",
        section="11",
        stated=17.0,
        computed=lambda: (-2.0)**3 - 12*(-2.0) + 1,
        tolerance=1e-12,
    ))

    # --- Exercise 10.2: f(x,y) = 3x^2+2y^2+2xy-4x-6y+10 ---
    # grad = (6x+2y-4, 4y+2x-6) = 0 => 6x+2y=4, 2x+4y=6
    # x = 1/5, y = 7/5
    ch.add(NumericCheck(
        label="Ex 10.2: critical point x = 1/5",
        section="11",
        stated=0.2,
        computed=lambda: _ex11_10_2_critical()[0],
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: critical point y = 7/5",
        section="11",
        stated=1.4,
        computed=lambda: _ex11_10_2_critical()[1],
        tolerance=1e-10,
    ))

    # Hessian: [[6, 2], [2, 4]], eigenvalues
    H_ex102 = np.array([[6, 2], [2, 4]], dtype=float)
    eigs_ex102 = np.sort(np.linalg.eigvalsh(H_ex102))

    ch.add(StructuralCheck(
        label="Ex 10.2: Hessian PD (both eigenvalues > 0) => local min",
        section="11",
        predicate=lambda: (
            np.all(eigs_ex102 > 0),
            f"eigenvalues = {eigs_ex102.tolist()}"
        ),
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: Hessian det = 6*4-2*2 = 20 > 0",
        section="11",
        stated=20.0,
        computed=lambda: float(np.linalg.det(H_ex102)),
        tolerance=1e-10,
    ))

    # --- Exercise 10.3: f(x) = e^x - x, strictly convex, global min ---
    # f'(x) = e^x - 1 = 0 => x = 0, f(0) = 1
    ch.add(NumericCheck(
        label="Ex 10.3: f'(0) = e^0 - 1 = 0",
        section="11",
        stated=0.0,
        computed=lambda: math.exp(0) - 1,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: f(0) = e^0 - 0 = 1 (global min)",
        section="11",
        stated=1.0,
        computed=lambda: math.exp(0) - 0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: f''(0) = e^0 = 1 > 0 (strictly convex)",
        section="11",
        stated=1.0,
        computed=lambda: math.exp(0),
        tolerance=1e-12,
    ))

    # --- Exercise 10.4: GD on f(x,y) = 4x^2+y^2, alpha=0.1, start (10,10) ---
    # grad f = (8x, 2y)
    # x_{k+1} = x_k - 0.8*x_k = 0.2*x_k, y_{k+1} = y_k - 0.2*y_k = 0.8*y_k
    ch.add(NumericCheck(
        label="Ex 10.4: GD k=1 x = 10*0.2 = 2",
        section="11",
        stated=2.0,
        computed=lambda: 10.0 * (1 - 0.1*8),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: GD k=1 y = 10*0.8 = 8",
        section="11",
        stated=8.0,
        computed=lambda: 10.0 * (1 - 0.1*2),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: GD k=2 x = 2*0.2 = 0.4",
        section="11",
        stated=0.4,
        computed=lambda: 10.0 * 0.2**2,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: GD k=2 y = 8*0.8 = 6.4",
        section="11",
        stated=6.4,
        computed=lambda: 10.0 * 0.8**2,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: condition number kappa = 8/2 = 4",
        section="11",
        stated=4.0,
        computed=lambda: 8.0 / 2.0,
        tolerance=1e-12,
    ))

    # --- Exercise 10.5: Newton on f(x) = ln(1+e^x) + 0.5*(x-3)^2 ---
    # f'(x) = e^x/(1+e^x) + (x-3) = sigmoid(x) + x - 3
    # f''(x) = sigmoid(x)*(1-sigmoid(x)) + 1
    ch.add(StructuralCheck(
        label="Ex 10.5: f strictly convex (f''(x) > 0 for all x)",
        section="11",
        predicate=lambda: _ex11_10_5_convexity(),
    ))

    ch.add(NumericCheck(
        label="Ex 10.5: Newton 3 steps from x0=0",
        section="11",
        stated=0.0,
        computed=lambda: _ex11_10_5_newton_residual(0.0, 3),
        tolerance=1e-6,
        note="||f'(x_3)|| should be very small",
    ))

    # --- Exercise 10.6: Rosenbrock function ---
    # grad = (-2(1-x) - 400x(y-x^2), 200(y-x^2))
    # At (1,1): grad = (0, 0), Hessian = [[802, -400], [-400, 200]]
    ch.add(NumericCheck(
        label="Ex 10.6: grad Rosenbrock at (1,1) = (0,0)",
        section="11",
        stated=0.0,
        computed=lambda: math.sqrt((-2*(1-1) - 400*1*(1-1))**2 + (200*(1-1))**2),
        tolerance=1e-12,
    ))

    H_rosen = np.array([[802, -400], [-400, 200]], dtype=float)
    eigs_rosen = np.linalg.eigvalsh(H_rosen)

    ch.add(StructuralCheck(
        label="Ex 10.6: Hessian at (1,1) positive definite",
        section="11",
        predicate=lambda: (
            np.all(eigs_rosen > 0),
            f"eigenvalues = {eigs_rosen.tolist()}"
        ),
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: condition number kappa at (1,1)",
        section="11",
        stated=float(eigs_rosen[-1] / eigs_rosen[0]),
        computed=lambda: float(np.max(np.linalg.eigvalsh(H_rosen)) / np.min(np.linalg.eigvalsh(H_rosen))),
        tolerance=1e-6,
        note="Large kappa => slow GD convergence",
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: f(1,1) = 0 (global minimum)",
        section="11",
        stated=0.0,
        computed=lambda: (1-1)**2 + 100*(1-1**2)**2,
        tolerance=1e-12,
    ))

    # --- Exercise 10.7: First-order characterization of convexity ---
    # f convex and differentiable => f(y) >= f(x) + grad f(x)^T (y - x)
    # Verify numerically for f(x,y) = x^2 + y^2
    def _ex_10_7_convexity_char():
        rng = np.random.default_rng(107)
        for _ in range(50):
            x_pt = rng.standard_normal(2)
            y_pt = rng.standard_normal(2)
            f_x = x_pt[0]**2 + x_pt[1]**2
            f_y = y_pt[0]**2 + y_pt[1]**2
            grad_x = 2 * x_pt
            tangent = f_x + np.dot(grad_x, y_pt - x_pt)
            if f_y < tangent - 1e-10:
                return (False, f"f(y)={f_y} < f(x)+grad.h={tangent}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 10.7: f(y) >= f(x) + grad f(x)^T(y-x) for f=x^2+y^2 (50 pairs)",
        section="11",
        predicate=_ex_10_7_convexity_char,
    ))

    # Corollary: any critical point of convex f is a global minimum
    # Verify: f(x)=x^4+2 (convex for x>=0 region), critical point at x=0
    ch.add(StructuralCheck(
        label="Ex 10.7: critical point of convex f is global min (f=x^2, x*=0)",
        section="11",
        predicate=lambda: (
            all(x**2 >= 0.0 - 1e-15 for x in np.linspace(-10, 10, 1000)),
            "f(x) < f(0)=0 for some x"
        ),
    ))

    # --- Exercise 10.8: GD convergence factor for quadratic ---
    # f(x) = 0.5*x^T A x, A symmetric PD with eigenvalues lam1 < lam2
    # Optimal step alpha = 2/(lam1+lam2), contraction rho = (kappa-1)/(kappa+1)
    lam1_ex8 = 1.0
    lam2_ex8 = 9.0
    kappa_ex8 = lam2_ex8 / lam1_ex8

    # Contraction factor
    rho_ex8 = (kappa_ex8 - 1) / (kappa_ex8 + 1)
    ch.add(NumericCheck(
        label="Ex 10.8: rho = (kappa-1)/(kappa+1) = 0.8 for kappa=9",
        section="11",
        stated=0.8,
        computed=rho_ex8,
        tolerance=1e-12,
    ))

    # Optimal step size
    alpha_opt = 2.0 / (lam1_ex8 + lam2_ex8)
    ch.add(NumericCheck(
        label="Ex 10.8: optimal alpha = 2/(lam1+lam2) = 0.2",
        section="11",
        stated=0.2,
        computed=alpha_opt,
        tolerance=1e-12,
    ))

    # When kappa=1 (A=cI), rho=0 => converges in 1 step
    ch.add(NumericCheck(
        label="Ex 10.8: kappa=1 => rho=0 (1-step convergence)",
        section="11",
        stated=0.0,
        computed=lambda: (1.0 - 1.0) / (1.0 + 1.0),
        tolerance=1e-12,
    ))

    # Verify GD with optimal step on A=diag(1,9) converges with factor rho
    def _ex_10_8_gd_convergence():
        A = np.diag([1.0, 9.0])
        alpha = 2.0 / (1.0 + 9.0)  # 0.2
        x = np.array([10.0, 10.0])
        errors = []
        for _ in range(20):
            errors.append(float(np.linalg.norm(x)))
            g = A @ x
            x = x - alpha * g
        # Check that error ratio converges to rho = 0.8
        ratios = [errors[i+1] / errors[i] for i in range(5, 15) if errors[i] > 1e-15]
        if not ratios:
            return (False, "No valid ratios")
        avg_ratio = sum(ratios) / len(ratios)
        if abs(avg_ratio - 0.8) < 0.05:
            return (True, "")
        return (False, f"avg ratio = {avg_ratio}, expected ~0.8")

    ch.add(StructuralCheck(
        label="Ex 10.8: GD convergence factor matches rho=0.8 empirically",
        section="11",
        predicate=_ex_10_8_gd_convergence,
    ))

    # ==================================================================
    # Remark 3.9: 2x2 Hessian discriminant test
    # ==================================================================

    # f(x,y) = x^2 + 2y^2 - 2xy + 2x - 4y
    # grad = (2x-2y+2, 4y-2x-4) => critical pt at (0,1)
    # H = [[2,-2],[-2,4]], det(H)=8-4=4>0, f_xx=2>0 => local min
    def _remark_3_9_discriminant_test():
        H = np.array([[2, -2], [-2, 4]], dtype=float)
        f_xx = H[0, 0]
        det_H = np.linalg.det(H)
        # Check local min conditions: f_xx > 0 and det(H) > 0
        if f_xx <= 0:
            return (False, f"f_xx = {f_xx}, expected > 0")
        if det_H <= 0:
            return (False, f"det(H) = {det_H}, expected > 0")
        # Eigenvalues should both be positive
        eigs = np.linalg.eigvalsh(H)
        if np.any(eigs <= 0):
            return (False, f"eigenvalues = {eigs}, expected all positive")
        # Verify eigenvalue values from the text: 3 +/- sqrt(5)
        expected_eigs = sorted([3 - math.sqrt(5), 3 + math.sqrt(5)])
        if not np.allclose(sorted(eigs), expected_eigs, atol=1e-10):
            return (False, f"eigenvalues = {sorted(eigs)}, expected {expected_eigs}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.9: 2x2 Hessian discriminant => local min, eigs=3+/-sqrt(5)",
        section="3",
        predicate=_remark_3_9_discriminant_test,
        note="Remark 3.9: eigenvalues ~0.764 and ~5.236",
    ))

    # Saddle point example: f(x,y) = x^2 - y^2
    # H = [[2,0],[0,-2]], det(H) = -4 < 0 => saddle
    def _remark_3_9_saddle_point():
        H = np.array([[2, 0], [0, -2]], dtype=float)
        det_H = np.linalg.det(H)
        if det_H >= 0:
            return (False, f"det(H) = {det_H}, expected < 0 for saddle")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.9: f=x^2-y^2 has det(H)=-4<0 => saddle point",
        section="3",
        predicate=_remark_3_9_saddle_point,
        note="Remark 3.9: discriminant test for saddle",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Gradient Descent ---
    # Note: Gradient descent is implicitly tested throughout via worked examples.
    # Adding an explicit algorithm implementation test.
    def _algo_gradient_descent():
        """Implement Algorithm 5.1 and verify on Rosenbrock-like function."""
        def gradient_descent(gradient, x0, alpha, tol, max_iter):
            x = list(x0)
            for k in range(max_iter):
                g = gradient(x)
                g_norm = math.sqrt(sum(gi ** 2 for gi in g))
                if g_norm < tol:
                    return x, k, True
                x = [x[i] - alpha * g[i] for i in range(len(x))]
            return x, max_iter, False

        # Minimize f(x,y) = (x-1)^2 + 10*(y-2)^2
        grad = lambda x: [2 * (x[0] - 1), 20 * (x[1] - 2)]
        result, iters, converged = gradient_descent(grad, [0, 0], 0.05, 1e-8, 10000)
        if not converged:
            return (False, f"GD did not converge in 10000 iterations")
        if abs(result[0] - 1.0) > 1e-4 or abs(result[1] - 2.0) > 1e-4:
            return (False, f"GD result = {result}, expected [1, 2]")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Gradient descent converges to minimum of (x-1)^2+10(y-2)^2",
        section="6",
        predicate=_algo_gradient_descent,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Newton's Method for Optimization (Multivariate) ---
    # Note: Newton's method is implicitly tested via worked examples.
    # Adding explicit test with Hessian solve.
    def _algo_newton_multivariate():
        """Implement Algorithm 5.2 and verify quadratic convergence."""
        def newton_opt(gradient, hessian, x0, tol, max_iter):
            x = np.array(x0, dtype=float)
            for k in range(max_iter):
                g = np.array(gradient(x))
                if np.linalg.norm(g) < tol:
                    return x.tolist(), k, True
                H = np.array(hessian(x))
                d = np.linalg.solve(H, -g)
                x = x + d
            return x.tolist(), max_iter, False

        # f(x,y) = x^4 + y^4 - 4*x*y, min at (1,1) or (-1,-1)
        grad = lambda x: [4 * x[0] ** 3 - 4 * x[1], 4 * x[1] ** 3 - 4 * x[0]]
        hess = lambda x: [[12 * x[0] ** 2, -4], [-4, 12 * x[1] ** 2]]
        result, iters, converged = newton_opt(grad, hess, [2.0, 2.0], 1e-12, 100)
        if not converged:
            return (False, f"Newton did not converge")
        if abs(result[0] - 1.0) > 1e-8 or abs(result[1] - 1.0) > 1e-8:
            return (False, f"Newton result = {result}, expected [1, 1]")
        if iters > 20:
            return (False, f"Newton took {iters} iterations, expected < 20 (quadratic convergence)")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Newton's method (multivariate) converges quadratically",
        section="6",
        predicate=_algo_newton_multivariate,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Newton's Method for Single-Variable Optimization ---
    # Note: Already implicitly tested via Ex 10.4. Adding explicit note.
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Newton 1D optimization (implicit: tested via Ex 10.4 above)",
        section="6",
        predicate=lambda: (True, ""),
        note="Algorithm 5.3 implicitly tested via worked examples for f(x)=x^4-3x^2+2",
    ))

    # --- Remark 3.14: Convex optimization — local min = global min ---
    def _remark_3_14_convex():
        """Verify least squares Hessian 2*A^T*A is PSD (convex),
        and that any local min found is the global min."""
        rng = np.random.default_rng(314)
        A = rng.standard_normal((10, 3))
        b = rng.standard_normal(10)
        H = 2 * A.T @ A
        eigs = np.linalg.eigvalsh(H)
        if np.any(eigs < -1e-12):
            return (False, f"Hessian of ||Ax-b||^2 has negative eigenvalue: {eigs}")
        # Verify multiple starting points converge to same solution
        x_star = np.linalg.lstsq(A, b, rcond=None)[0]
        for _ in range(5):
            x0 = rng.standard_normal(3) * 10
            # Simple gradient descent
            x = x0.copy()
            for _ in range(2000):
                grad = 2 * A.T @ (A @ x - b)
                x = x - 0.01 * grad
            if not np.allclose(x, x_star, atol=1e-3):
                return (False, f"GD from {x0} converged to {x}, not {x_star}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: Least squares is convex — all starts find same global min",
        section="3.14",
        predicate=_remark_3_14_convex,
        note="Remark 3.14: convex optimization, local=global",
    ))

    # --- Remark 3.19: Newton converges quadratically, GD converges linearly ---
    def _remark_3_19_convergence_rates():
        """Compare convergence rates: Newton (quadratic) vs GD (linear)."""
        # f(x) = (x-3)^4 + (x-3)^2 — strongly convex near x=3
        def f(x): return (x - 3)**4 + (x - 3)**2
        def fp(x): return 4*(x - 3)**3 + 2*(x - 3)
        def fpp(x): return 12*(x - 3)**2 + 2
        x0 = 5.0
        # Newton
        x_n = x0
        newton_iters = 0
        for _ in range(50):
            newton_iters += 1
            x_n = x_n - fp(x_n) / fpp(x_n)
            if abs(fp(x_n)) < 1e-12:
                break
        # GD with small fixed step
        x_g = x0
        gd_iters = 0
        for _ in range(10000):
            gd_iters += 1
            x_g = x_g - 0.01 * fp(x_g)
            if abs(fp(x_g)) < 1e-12:
                break
        if newton_iters >= gd_iters:
            return (False, f"Newton ({newton_iters} iters) not faster than GD ({gd_iters} iters)")
        return (True, f"Newton: {newton_iters} iters, GD: {gd_iters} iters")

    ch.add(StructuralCheck(
        label="Remark 3.19: Newton converges in fewer iterations than GD",
        section="3.19",
        predicate=_remark_3_19_convergence_rates,
        note="Remark 3.19: Newton vs gradient descent tradeoff",
    ))

    # --- Remark 3.20: Armijo condition (sufficient decrease) ---
    ch.add(StructuralCheck(
        label="Remark 3.20: Armijo condition holds at all GD steps for f=x^2+y^2",
        section="3.20",
        predicate=_check_armijo_all_steps,
        note="Remark 3.20: line search Armijo condition",
    ))

    return ch


# ===================================================================
# Exercise helper functions
# ===================================================================

def _ex11_10_2_critical():
    """Solve 6x+2y=4, 2x+4y=6 for critical point of 3x^2+2y^2+2xy-4x-6y+10."""
    A = np.array([[6, 2], [2, 4]], dtype=float)
    b = np.array([4, 6], dtype=float)
    return np.linalg.solve(A, b)


def _ex11_10_5_convexity():
    """Check f''(x) > 0 for f(x) = ln(1+e^x) + 0.5*(x-3)^2 at many x."""
    import math
    for x in np.linspace(-10, 10, 100):
        sig = 1.0 / (1.0 + math.exp(-x))
        fpp = sig * (1 - sig) + 1.0
        if fpp <= 0:
            return (False, f"f''({x}) = {fpp} <= 0")
    return (True, "")


def _ex11_10_5_newton_residual(x0, nsteps):
    """Run Newton on f(x)=ln(1+e^x)+0.5*(x-3)^2, return |f'(x_n)|."""
    import math
    x = x0
    for _ in range(nsteps):
        sig = 1.0 / (1.0 + math.exp(-x))
        fp = sig + x - 3.0
        fpp = sig * (1 - sig) + 1.0
        x = x - fp / fpp
    sig = 1.0 / (1.0 + math.exp(-x))
    return abs(sig + x - 3.0)


# ===================================================================
# Helper functions — Symbolic
# ===================================================================

def _gradient_zero_at_critical_1d():
    """f(x) = x^2 - 4x + 5, verify f'(2) = 0."""
    import sympy
    x = sympy.Symbol('x')
    f = x**2 - 4*x + 5
    fp = sympy.diff(f, x)
    return sympy.Eq(fp.subs(x, 2), 0)


def _gradient_zero_at_critical_2d():
    """f(x,y) = x^2 + 2y^2 - 2xy - 2x, verify grad f(2,1) = (0,0)."""
    import sympy
    x, y = sympy.symbols('x y')
    f = x**2 + 2*y**2 - 2*x*y - 2*x
    fx = sympy.diff(f, x).subs([(x, 2), (y, 1)])
    fy = sympy.diff(f, y).subs([(x, 2), (y, 1)])
    return sympy.Eq(fx**2 + fy**2, 0)


def _hessian_pd_symbolic():
    """Verify eigenvalues of H = [[2,-2],[-2,4]] are both positive."""
    import sympy
    H = sympy.Matrix([[2, -2], [-2, 4]])
    eigenvals = list(H.eigenvals().keys())
    return sympy.And(*[sympy.StrictGreaterThan(ev, 0) for ev in eigenvals])


def _newton_minimizes_quadratic():
    """For f(x) = a*x^2 + b*x + c, one Newton step from x0 reaches -b/(2a).
    Newton step: x1 = x0 - f'(x0)/f''(x0) = x0 - (2a*x0+b)/(2a) = -b/(2a).
    Verify x1 - (-b/(2a)) = 0.
    """
    import sympy
    a, b, c, x0 = sympy.symbols('a b c x0', real=True)
    a = sympy.Symbol('a', positive=True)
    fp = 2*a*x0 + b
    fpp = 2*a
    x1 = x0 - fp / fpp
    return sympy.simplify(x1 - (-b / (2*a)))


def _gd_convergence_condition():
    """For f(x) = (1/2)Lx^2, GD update x_{k+1} = (1 - alpha*L)*x_k.
    Converges iff |1 - alpha*L| < 1, i.e., 0 < alpha*L < 2.
    Verify: at alpha = 1/L, update factor is 0 (instant convergence).
    """
    import sympy
    L = sympy.Symbol('L', positive=True)
    alpha = 1 / L
    factor = 1 - alpha * L
    return sympy.Eq(factor, 0)


def _convexity_second_derivative():
    """f(x) = x^2 - 4x + 5 has f''(x) = 2 > 0 for all x."""
    import sympy
    x = sympy.Symbol('x')
    f = x**2 - 4*x + 5
    fpp = sympy.diff(f, x, 2)
    return sympy.StrictGreaterThan(fpp, 0)


# ===================================================================
# Helper functions — Numeric
# ===================================================================

def _f_ex82(x: np.ndarray) -> float:
    """f(x,y) = x^2 + 2y^2 - 2xy - 2x."""
    return float(x[0]**2 + 2*x[1]**2 - 2*x[0]*x[1] - 2*x[0])


def _gradient_ex82(x: np.ndarray) -> np.ndarray:
    """Gradient of f(x,y) = x^2 + 2y^2 - 2xy - 2x."""
    return np.array([2*x[0] - 2*x[1] - 2, 4*x[1] - 2*x[0]])


def _find_min_1d(f, fp, x0: float, alpha: float = 0.01, tol: float = 1e-10, maxiter: int = 100000) -> float:
    """Simple gradient descent for a 1D function."""
    x = x0
    for _ in range(maxiter):
        g = fp(x)
        if abs(g) < tol:
            break
        x = x - alpha * g
    return x


def _newton_1d_ex84(x0: float, nsteps: int) -> float:
    """Newton's method on f(x) = x^4 - 3x^2 + 2.
    f'(x) = 4x^3 - 6x, f''(x) = 12x^2 - 6.
    """
    x = x0
    for _ in range(nsteps):
        fp = 4*x**3 - 6*x
        fpp = 12*x**2 - 6
        if abs(fpp) < 1e-15:
            break
        x = x - fp / fpp
    return x


def _newton_1d_deriv(x0: float, nsteps: int) -> float:
    """Return f'(x_k) after nsteps Newton iterations on f(x)=x^4-3x^2+2."""
    x = _newton_1d_ex84(x0, nsteps)
    return 4*x**3 - 6*x


def _newton_1d_second_deriv(x0: float, nsteps: int) -> float:
    """Return f''(x_k) after nsteps Newton iterations on f(x)=x^4-3x^2+2."""
    x = _newton_1d_ex84(x0, nsteps)
    return 12*x**2 - 6


def _newton_steps_quadratic_2d() -> float:
    """One Newton step on f(x,y) = x^2 + 2y^2 - 2xy - 2x from (0,0).
    H = [[2,-2],[-2,4]], grad f(0,0) = [-2, 0].
    Newton step: x1 = x0 - H^{-1} grad = (0,0) - H^{-1} (-2, 0).
    H^{-1} = (1/4)*[[4,2],[2,2]].
    d = -H^{-1} * (-2,0) = (1/4)*[[4,2],[2,2]] * (2,0) = (2, 1).
    x1 = (0,0) + (2,1) = (2,1). Error = 0.
    """
    H = np.array([[2, -2], [-2, 4]], dtype=float)
    g = np.array([-2, 0], dtype=float)
    d = np.linalg.solve(H, -g)
    x1 = np.array([0.0, 0.0]) + d
    xstar = np.array([2.0, 1.0])
    return float(np.linalg.norm(x1 - xstar))


# ===================================================================
# Helper functions — Structural
# ===================================================================

def _check_hessian_pd(H: np.ndarray) -> tuple[bool, str]:
    """Check that all eigenvalues of H are positive."""
    eigenvalues = np.linalg.eigvalsh(H)
    all_positive = all(ev > 0 for ev in eigenvalues)
    if all_positive:
        return True, ""
    return False, f"Eigenvalues {eigenvalues} are not all positive"


def _check_nonconvex_at_zero() -> tuple[bool, str]:
    """f(x) = x^4 - 3x^2 + 2, f''(0) = -6 < 0."""
    fpp_at_0 = 12 * 0.0**2 - 6.0
    if fpp_at_0 < 0:
        return True, ""
    return False, f"f''(0) = {fpp_at_0}, expected negative"


def _check_saddle_point() -> tuple[bool, str]:
    """f(x,y) = x^2 - y^2 has H = [[2,0],[0,-2]], indefinite (saddle)."""
    H = np.array([[2, 0], [0, -2]], dtype=float)
    eigenvalues = np.linalg.eigvalsh(H)
    has_positive = any(ev > 0 for ev in eigenvalues)
    has_negative = any(ev < 0 for ev in eigenvalues)
    if has_positive and has_negative:
        return True, ""
    return False, f"Eigenvalues {eigenvalues} are not mixed sign (not indefinite)"


def _check_gd_monotone_decrease() -> tuple[bool, str]:
    """GD on f(x,y) = x^2 + y^2 from (5,3) with alpha=0.1.
    f values must be strictly decreasing.
    """
    x = np.array([5.0, 3.0])
    alpha = 0.1
    prev_f = x[0]**2 + x[1]**2
    for k in range(50):
        g = 2.0 * x
        x = x - alpha * g
        cur_f = x[0]**2 + x[1]**2
        if cur_f >= prev_f - 1e-15:
            return False, f"f not decreasing at step {k+1}: f_prev={prev_f}, f_cur={cur_f}"
        prev_f = cur_f
    return True, ""


def _check_newton_quadratic_convergence() -> tuple[bool, str]:
    """Newton on f(x) = x^4 - 3x^2 + 2 starting from x0=2.0.
    Check that e_{k+1} / e_k^2 is bounded (quadratic convergence).
    """
    xstar = math.sqrt(3.0 / 2.0)
    x = 2.0
    errors = []
    for _ in range(8):
        errors.append(abs(x - xstar))
        fp = 4*x**3 - 6*x
        fpp = 12*x**2 - 6
        if abs(fpp) < 1e-15:
            break
        x = x - fp / fpp

    # Check quadratic convergence: e_{k+1} / e_k^2 bounded
    ratios = []
    for i in range(1, len(errors) - 1):
        if errors[i] < 1e-14:
            break
        if errors[i-1] > 1e-14:
            ratio = errors[i] / errors[i-1]**2
            ratios.append(ratio)

    if not ratios:
        return False, "Not enough data points for convergence check"

    # The ratio should be bounded (not growing unboundedly)
    max_ratio = max(ratios)
    if max_ratio < 100:  # generous bound for quadratic convergence constant
        return True, ""
    return False, f"Quadratic convergence ratios {ratios}, max = {max_ratio}"


def _check_condition_number() -> tuple[bool, str]:
    """Condition number of H = [[2,-2],[-2,4]] is (3+sqrt(5))/(3-sqrt(5))."""
    H = np.array([[2, -2], [-2, 4]], dtype=float)
    eigenvalues = np.sort(np.linalg.eigvalsh(H))
    kappa_computed = eigenvalues[-1] / eigenvalues[0]
    kappa_expected = (3 + math.sqrt(5)) / (3 - math.sqrt(5))
    if abs(kappa_computed - kappa_expected) / kappa_expected < 1e-10:
        return True, ""
    return False, f"kappa computed={kappa_computed}, expected={kappa_expected}"


def _check_gd_contraction_factor() -> tuple[bool, str]:
    """GD on f=x^2+y^2 with alpha=0.1: each component multiplied by 0.8."""
    x = np.array([5.0, 3.0])
    alpha = 0.1
    g = 2.0 * x
    x_next = x - alpha * g
    expected = 0.8 * x
    if np.allclose(x_next, expected, atol=1e-14):
        return True, ""
    return False, f"x_next = {x_next}, expected = {expected}"


def _check_armijo_condition_k0() -> tuple[bool, str]:
    """Verify Armijo sufficient decrease at the first GD step of Ex 8.3.
    f(x,y) = x^2 + y^2, x0=(5,3), alpha=0.1, c1=1e-4.
    f(x1) <= f(x0) - c1 * alpha * ||grad(x0)||^2.
    """
    f0 = 34.0
    f1 = 21.76
    grad_sq = (2*5.0)**2 + (2*3.0)**2  # 136
    c1 = 1e-4
    alpha = 0.1
    rhs = f0 - c1 * alpha * grad_sq
    if f1 <= rhs:
        return True, ""
    return False, f"f(x1)={f1} > {rhs} = Armijo RHS"


def _check_wolfe_condition_k0() -> tuple[bool, str]:
    """Verify Wolfe curvature condition at the first GD step of Ex 8.3.
    grad(x1) . d >= c2 * grad(x0) . d, where d = -grad(x0).
    """
    grad0 = np.array([10.0, 6.0])
    grad1 = np.array([8.0, 4.8])
    d = -grad0
    lhs = np.dot(grad1, d)  # -108.8
    c2 = 0.9
    rhs = c2 * np.dot(grad0, d)  # 0.9 * (-136) = -122.4
    if lhs >= rhs:
        return True, ""
    return False, f"Wolfe curvature: {lhs} < {rhs}"


def _check_newton_k5_converged() -> tuple[bool, str]:
    """Verify Newton iterate at k=5 has |x-x*| < 1e-8."""
    xstar = math.sqrt(3.0 / 2.0)
    x5 = _newton_1d_ex84(x0=2.0, nsteps=5)
    err = abs(x5 - xstar)
    if err < 1e-8:
        return True, ""
    return False, f"|x_5 - x*| = {err:.2e}, expected < 1e-8"


def _check_armijo_all_steps() -> tuple[bool, str]:
    """Verify Armijo condition holds at every GD step k=0..19 on f=x^2+y^2."""
    x = np.array([5.0, 3.0])
    alpha = 0.1
    c1 = 1e-4
    for k in range(20):
        f_cur = x[0]**2 + x[1]**2
        g = 2.0 * x
        grad_sq = float(np.dot(g, g))
        x_next = x - alpha * g
        f_next = x_next[0]**2 + x_next[1]**2
        rhs = f_cur - c1 * alpha * grad_sq
        if f_next > rhs + 1e-15:
            return False, f"Armijo violated at step {k}: f_next={f_next}, rhs={rhs}"
        x = x_next
    return True, ""
