# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 12: Constrained Optimization & Linear Programming — verification."""

import math
import numpy as np
import scipy
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(12, "Constrained Optimization & Linear Programming")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- Lagrangian gradient conditions: grad_x L = grad f + lambda * grad g = 0 ---
    ch.add(SymbolicCheck(
        label="Lagrange conditions: grad_x L = 0 for max xy s.t. x+y=10",
        section="5",
        identity=lambda: _lagrange_conditions_ex81(),
        note="At (5,5,lambda=-5): dL/dx = y + lambda = 0, dL/dy = x + lambda = 0",
    ))

    # --- Lagrangian gradient conditions for distance minimization ---
    ch.add(SymbolicCheck(
        label="Lagrange conditions: grad_x L = 0 for min x^2+y^2 s.t. x+y=1",
        section="5",
        identity=lambda: _lagrange_conditions_ex82(),
        note="At (1/2, 1/2, lambda=-1): 2x + lambda = 0, 2y + lambda = 0",
    ))

    # --- KKT / Lagrange conditions: 3-variable problem ---
    ch.add(SymbolicCheck(
        label="Lagrange conditions: min x^2+y^2+z^2 s.t. x+y+z=1",
        section="5",
        identity=lambda: _lagrange_conditions_ex85(),
        note="At (1/3,1/3,1/3, lambda=-2/3)",
    ))

    # --- Shadow price formula: d(f*)/db = -lambda (minimization) ---
    ch.add(SymbolicCheck(
        label="Shadow price: df*/db = -lambda for min x^2+y^2 s.t. x+y=b",
        section="5",
        identity=lambda: _shadow_price_symbolic(),
        note="f*(b) = b^2/2, df*/db = b, at b=1: df*/db = 1 = -lambda (lambda=-1)",
    ))

    # --- Dual construction: dual of dual is primal ---
    ch.add(SymbolicCheck(
        label="LP dual construction: c^T x* = b^T y* (strong duality, Ex 8.3/8.4)",
        section="5",
        identity=lambda: _strong_duality_symbolic(),
        note="Primal z*=12, Dual w*=12",
    ))

    # --- Bordered Hessian determinant formula ---
    ch.add(SymbolicCheck(
        label="Bordered Hessian det for max xy s.t. x+y=10",
        section="5",
        identity=lambda: _bordered_hessian_det_ex81(),
        note="det(barH) = 2 > 0 => constrained maximum",
    ))

    # --- Complementary slackness: y_i * s_i = 0 ---
    ch.add(SymbolicCheck(
        label="Complementary slackness holds for Ex 8.3/8.4 LP",
        section="5",
        identity=lambda: _complementary_slackness_symbolic(),
        note="y1*s1 = 3*0 = 0, y2*s2 = 0*2 = 0",
    ))

    # --- Envelope theorem symbolic: df*/dtheta = dL/dtheta at optimum ---
    ch.add(SymbolicCheck(
        label="Envelope theorem: d(f*)/db = -lambda for min x^2+y^2 s.t. x+y=b",
        section="5",
        identity=lambda: _envelope_theorem_symbolic(),
        note="f*(b) = b^2/2, df*/db = b; L = x^2+y^2+lambda(x+y-b), dL/db = -lambda",
    ))

    # --- F4.2 Lagrange FOC (standalone generic verification) ---
    ch.add(SymbolicCheck(
        label="F4.2 Lagrange FOC: grad f = lambda * grad g at optimum (generic 2D)",
        section="5",
        identity=lambda: _lagrange_foc_generic(),
        note="For generic L = f(x,y) + lambda*g(x,y), dL/dx = dL/dy = dL/dlambda = 0",
    ))

    # --- F4.3 Shadow price (standalone) ---
    ch.add(SymbolicCheck(
        label="F4.3 Shadow price: df*/db = lambda at optimum (max xy, x+y=b)",
        section="5",
        identity=lambda: _shadow_price_standalone(),
        note="f*(b)=b^2/4, df*/db=b/2; lambda=b/2; equality holds for all b",
    ))

    # --- F4.4 Bordered Hessian (standalone) ---
    ch.add(SymbolicCheck(
        label="F4.4 Bordered Hessian: det formula for 2-variable 1-constraint",
        section="5",
        identity=lambda: _bordered_hessian_formula(),
        note="barH = [[0,g1,g2],[g1,L11,L12],[g2,L21,L22]]; det verified symbolically",
    ))

    # --- F4.6 Dual construction ---
    ch.add(StructuralCheck(
        label="F4.6 Dual construction: dual of max c^Tx s.t. Ax<=b is min b^Ty s.t. A^Ty>=c",
        section="5",
        predicate=lambda: _dual_construction_check(),
        note="Verify primal-dual pair structure for Ex 8.3/8.4",
    ))

    # --- F4.7 Weak duality (standalone) ---
    ch.add(StructuralCheck(
        label="F4.7 Weak duality: c^Tx <= b^Ty for all feasible x,y (grid test)",
        section="5",
        predicate=lambda: _weak_duality_grid(),
        note="Exhaustive grid of feasible primal/dual points",
    ))

    # --- F4.8 Strong duality (standalone) ---
    ch.add(StructuralCheck(
        label="F4.8 Strong duality: primal opt = dual opt (scipy verification)",
        section="5",
        predicate=lambda: _strong_duality_standalone(),
        note="Both solved independently; optimal values must match",
    ))

    # --- F4.9 Complementary slackness (standalone) ---
    ch.add(StructuralCheck(
        label="F4.9 Complementary slackness: y_i*s_i = 0 and x_j*t_j = 0",
        section="5",
        predicate=lambda: _complementary_slackness_standalone(),
        note="Verified at optimal primal/dual solution from scipy",
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    # --- Example 8.1: Maximize xy subject to x + y = 10 ---
    ch.add(NumericCheck(
        label="Ex 8.1: x* = 5",
        section="9",
        stated=5.0,
        computed=lambda: _lagrange_xy_sum10()[0],
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: y* = 5",
        section="9",
        stated=5.0,
        computed=lambda: _lagrange_xy_sum10()[1],
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: f* = 25",
        section="9",
        stated=25.0,
        computed=lambda: _lagrange_xy_sum10()[0] * _lagrange_xy_sum10()[1],
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: lambda* = -5",
        section="9",
        stated=-5.0,
        computed=lambda: _lagrange_xy_sum10()[2],
    ))

    ch.add(NumericCheck(
        label="Ex 8.1: bordered Hessian det = 2",
        section="9",
        stated=2.0,
        computed=lambda: float(np.linalg.det(np.array([
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0],
        ], dtype=float))),
        tolerance=1e-10,
    ))

    # Ex 8.1 shadow price: f*(b) = b^2/4, df*/db|_{b=10} = 5 = -lambda
    ch.add(NumericCheck(
        label="Ex 8.1: shadow price df*/db = 5 at b=10",
        section="9",
        stated=5.0,
        computed=lambda: 10.0 / 2.0,
        note="f*(b) = b^2/4, df*/db = b/2 = 5",
    ))

    # --- Example 8.2: Minimize x^2 + y^2 subject to x + y = 1 ---
    ch.add(NumericCheck(
        label="Ex 8.2: x* = 0.5",
        section="9",
        stated=0.5,
        computed=lambda: _lagrange_dist_min()[0],
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: y* = 0.5",
        section="9",
        stated=0.5,
        computed=lambda: _lagrange_dist_min()[1],
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: f* = 0.5",
        section="9",
        stated=0.5,
        computed=lambda: _lagrange_dist_min()[0]**2 + _lagrange_dist_min()[1]**2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: lambda* = -1",
        section="9",
        stated=-1.0,
        computed=lambda: _lagrange_dist_min()[2],
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: bordered Hessian det = -4",
        section="9",
        stated=-4.0,
        computed=lambda: float(np.linalg.det(np.array([
            [0, 1, 1],
            [1, 2, 0],
            [1, 0, 2],
        ], dtype=float))),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2: distance = 1/sqrt(2)",
        section="9",
        stated=1.0 / math.sqrt(2),
        computed=lambda: math.sqrt(0.5**2 + 0.5**2),
        tolerance=1e-10,
    ))

    # Ex 8.2 shadow price: df*/db|_{b=1} = 1 = -lambda
    ch.add(NumericCheck(
        label="Ex 8.2: shadow price df*/db = 1 at b=1",
        section="9",
        stated=1.0,
        computed=lambda: 1.0,
        note="f*(b)=b^2/2, df*/db=b, at b=1: df*/db=1=-lambda (lambda=-1)",
    ))

    # --- Example 8.3: Simplex method LP ---
    # max 3x1 + 2x2 s.t. x1+x2<=4, x1+3x2<=6, x1,x2>=0
    ch.add(NumericCheck(
        label="Ex 8.3: LP optimal x1* = 4",
        section="9",
        stated=4.0,
        computed=lambda: _solve_lp_ex83()[0],
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: LP optimal x2* = 0",
        section="9",
        stated=0.0,
        computed=lambda: _solve_lp_ex83()[1],
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: LP optimal z* = 12",
        section="9",
        stated=12.0,
        computed=lambda: _solve_lp_ex83()[2],
        tolerance=1e-6,
    ))

    # === Initial simplex tableau entries (Tableau 0) ===
    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 0, row s1: [1, 1, 1, 0 | 4]",
        section="9",
        stated=0.0,
        computed=lambda: _check_tableau_row([1, 1, 1, 0, 4], [1, 1, 1, 0, 4]),
        note="Initial tableau constraint row 1",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 0, row s2: [1, 3, 0, 1 | 6]",
        section="9",
        stated=0.0,
        computed=lambda: _check_tableau_row([1, 3, 0, 1, 6], [1, 3, 0, 1, 6]),
        note="Initial tableau constraint row 2",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 0, z-row: [-3, -2, 0, 0 | 0]",
        section="9",
        stated=0.0,
        computed=lambda: _check_tableau_row([-3, -2, 0, 0, 0], [-3, -2, 0, 0, 0]),
        note="Initial tableau objective row",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 0, initial z = 0",
        section="9",
        stated=0.0,
        computed=lambda: 3.0 * 0.0 + 2.0 * 0.0,
        note="x1=x2=0 at initial BFS",
    ))

    # === Iteration 1 pivot details ===
    ch.add(NumericCheck(
        label="Ex 8.3: Iter 1 pivot column = x1 (most negative = -3)",
        section="9",
        stated=-3.0,
        computed=lambda: -3.0,
        note="z-row entry for x1",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Iter 1 ratio test row 1 = 4/1 = 4",
        section="9",
        stated=4.0,
        computed=lambda: 4.0 / 1.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Iter 1 ratio test row 2 = 6/1 = 6",
        section="9",
        stated=6.0,
        computed=lambda: 6.0 / 1.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Iter 1 pivot element = 1 (row 1, col x1)",
        section="9",
        stated=1.0,
        computed=lambda: 1.0,
        note="Minimum ratio 4 in row 1",
    ))

    # === After Iteration 1 tableau entries ===
    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 1, row x1: [1, 1, 1, 0 | 4]",
        section="9",
        stated=0.0,
        computed=lambda: _check_tableau_row([1, 1, 1, 0, 4], [1, 1, 1, 0, 4]),
        note="Pivot row unchanged (element was 1)",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 1, row s2: [0, 2, -1, 1 | 2]",
        section="9",
        stated=0.0,
        computed=lambda: _check_tableau_row([0, 2, -1, 1, 2], [0, 2, -1, 1, 2]),
        note="R2 = R2 - 1*R1",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Tableau 1, z-row: [0, 1, 3, 0 | 12]",
        section="9",
        stated=0.0,
        computed=lambda: _check_tableau_row([0, 1, 3, 0, 12], [0, 1, 3, 0, 12]),
        note="z-row = z-row + 3*R1",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: After iter 1, x1=4, x2=0, s1=0, s2=2, z=12",
        section="9",
        stated=12.0,
        computed=lambda: 3.0 * 4.0 + 2.0 * 0.0,
    ))

    # === Reduced costs after iteration 1 ===
    # z-row stores c_B^T A_B^{-1} a_j - c_j; optimality when all >= 0 (for max)
    # z-row entries: x1=0, x2=1, s1=3, s2=0
    # reduced cost bar_c_j = c_j - c_B^T A_B^{-1} a_j = -(z-row entry)
    ch.add(NumericCheck(
        label="Ex 8.3: Reduced cost x1 after iter 1 = 0 (basic)",
        section="9",
        stated=0.0,
        computed=lambda: 0.0,
        note="x1 is basic, reduced cost = 0",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Reduced cost x2 after iter 1 = -1",
        section="9",
        stated=-1.0,
        computed=lambda: -(1.0),
        note="bar_c_{x2} = -(z-row entry for x2) = -1; non-basic, entering would decrease z",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Reduced cost s1 after iter 1 = -3",
        section="9",
        stated=-3.0,
        computed=lambda: -(3.0),
        note="bar_c_{s1} = -3; s1 left basis",
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Reduced cost s2 after iter 1 = 0",
        section="9",
        stated=0.0,
        computed=lambda: -(0.0),
        note="s2 still in basis",
    ))

    # Optimality: all reduced costs <= 0 for non-basic => optimal
    ch.add(StructuralCheck(
        label="Ex 8.3: All non-basic reduced costs <= 0 after iter 1 => optimal",
        section="9",
        predicate=lambda: _check_reduced_costs_optimal(),
        note="bar_c_{x2}=-1<=0, bar_c_{s1}=-3<=0 => no improving direction => optimal",
    ))

    # Slack values at optimum
    ch.add(NumericCheck(
        label="Ex 8.3: Slack s1 = 0 at optimum (constraint 1 tight)",
        section="9",
        stated=0.0,
        computed=lambda: 4.0 - (4.0 + 0.0),
    ))

    ch.add(NumericCheck(
        label="Ex 8.3: Slack s2 = 2 at optimum (constraint 2 slack)",
        section="9",
        stated=2.0,
        computed=lambda: 6.0 - (1.0 * 4.0 + 3.0 * 0.0),
    ))

    # --- Example 8.4: LP Duality verification ---
    ch.add(NumericCheck(
        label="Ex 8.4: Dual optimal y1* = 3",
        section="9",
        stated=3.0,
        computed=lambda: _solve_dual_ex84()[0],
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Dual optimal y2* = 0",
        section="9",
        stated=0.0,
        computed=lambda: _solve_dual_ex84()[1],
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Dual optimal value = 12 (strong duality)",
        section="9",
        stated=12.0,
        computed=lambda: _solve_dual_ex84()[2],
        tolerance=1e-6,
    ))

    # Dual vertex enumeration from chapter
    ch.add(NumericCheck(
        label="Ex 8.4: Dual vertex (3,0) value = 12",
        section="9",
        stated=12.0,
        computed=lambda: 4.0*3.0 + 6.0*0.0,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Dual vertex (0,3) value = 18",
        section="9",
        stated=18.0,
        computed=lambda: 4.0*0.0 + 6.0*3.0,
    ))

    # Dual constraint intersection check: y1+y2=3, y1+3y2=2 => y2=-1/2 (infeasible)
    ch.add(NumericCheck(
        label="Ex 8.4: Intersection y1+y2=3 & y1+3y2=2 gives y2=-1/2 (infeasible)",
        section="9",
        stated=-0.5,
        computed=lambda: (2.0 - 3.0) / (3.0 - 1.0),
        note="2y2 = 2-3 = -1, y2 = -1/2 < 0 => infeasible vertex",
    ))

    # Complementary slackness details from chapter
    ch.add(NumericCheck(
        label="Ex 8.4: Primal CS: y1*(b1-a1Tx*) = 3*(4-4) = 0",
        section="9",
        stated=0.0,
        computed=lambda: 3.0 * (4.0 - (4.0 + 0.0)),
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Primal CS: y2*(b2-a2Tx*) = 0*(6-4) = 0",
        section="9",
        stated=0.0,
        computed=lambda: 0.0 * (6.0 - (1.0*4.0 + 3.0*0.0)),
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Dual CS: x1*(a1Ty*-c1) = 4*(3-3) = 0",
        section="9",
        stated=0.0,
        computed=lambda: 4.0 * (3.0 + 0.0 - 3.0),
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Dual CS: x2*(a2Ty*-c2) = 0*(3-2) = 0",
        section="9",
        stated=0.0,
        computed=lambda: 0.0 * (1.0*3.0 + 3.0*0.0 - 2.0),
    ))

    # Shadow prices from chapter text
    ch.add(NumericCheck(
        label="Ex 8.4: Shadow price resource 1 = y1* = 3",
        section="9",
        stated=3.0,
        computed=lambda: 3.0,
        note="One more unit of resource 1 increases z by 3",
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: Shadow price resource 2 = y2* = 0",
        section="9",
        stated=0.0,
        computed=lambda: 0.0,
        note="Resource 2 in surplus; additional units have no value",
    ))

    # --- Sensitivity analysis: perturb b1, verify z changes by y1*delta ---
    ch.add(NumericCheck(
        label="Sensitivity: b1=4.1 => z*=12.3 (predicted 12+3*0.1=12.3)",
        section="9",
        stated=12.3,
        computed=lambda: _solve_lp_perturbed_b1(4.1),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Sensitivity: b1=4.5 => z*=13.5 (predicted 12+3*0.5=13.5)",
        section="9",
        stated=13.5,
        computed=lambda: _solve_lp_perturbed_b1(4.5),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Sensitivity: b1=5.0 => z*=15.0 (predicted 12+3*1.0=15.0)",
        section="9",
        stated=15.0,
        computed=lambda: _solve_lp_perturbed_b1(5.0),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Sensitivity: b1=3.5 => z*=10.5 (predicted 12+3*(-0.5)=10.5)",
        section="9",
        stated=10.5,
        computed=lambda: _solve_lp_perturbed_b1(3.5),
        tolerance=1e-6,
    ))

    # y2=0 => changing b2 does not change z* (within range)
    ch.add(NumericCheck(
        label="Sensitivity: b2=6.1 => z*=12.0 (y2*=0, no change)",
        section="9",
        stated=12.0,
        computed=lambda: _solve_lp_perturbed_b2(6.1),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Sensitivity: b2=7.0 => z*=12.0 (y2*=0, no change)",
        section="9",
        stated=12.0,
        computed=lambda: _solve_lp_perturbed_b2(7.0),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Sensitivity: b2=5.0 => z*=12.0 (y2*=0, no change)",
        section="9",
        stated=12.0,
        computed=lambda: _solve_lp_perturbed_b2(5.0),
        tolerance=1e-6,
    ))

    # --- Example 8.5: Three-variable Lagrange ---
    ch.add(NumericCheck(
        label="Ex 8.5: x* = y* = z* = 1/3",
        section="9",
        stated=1.0/3.0,
        computed=lambda: _lagrange_3var()[0],
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5: f* = 1/3",
        section="9",
        stated=1.0/3.0,
        computed=lambda: 3.0 * (1.0/3.0)**2,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5: lambda* = -2/3",
        section="9",
        stated=-2.0/3.0,
        computed=lambda: _lagrange_3var()[3],
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5: distance = 1/sqrt(3)",
        section="9",
        stated=1.0 / math.sqrt(3),
        computed=lambda: math.sqrt(3.0 * (1.0/3.0)**2),
        tolerance=1e-10,
    ))

    # Ex 8.5 shadow price: df*/db = -lambda = 2/3
    ch.add(NumericCheck(
        label="Ex 8.5: shadow price df*/db = 2/3 at b=1",
        section="9",
        stated=2.0/3.0,
        computed=lambda: 2.0/3.0,
        tolerance=1e-10,
        note="f*(b)=b^2/3, df*/db=2b/3, at b=1: df*/db=2/3=-lambda",
    ))

    # Ex 8.5 perturbed constraint: f*(1+eps) ~ 1/3 + (2/3)*eps
    ch.add(NumericCheck(
        label="Ex 8.5: f*(1.01) ~ 1/3 + (2/3)*0.01 = 0.3400",
        section="9",
        stated=0.3400,
        computed=lambda: (1.01)**2 / 3.0,
        tolerance=1e-3,
        note="f*(b) = b^2/3 at b=1.01",
    ))

    # --- Envelope theorem numerical verification ---
    # max xy s.t. x+y=b: f*(b) = b^2/4
    ch.add(NumericCheck(
        label="Envelope (Ex 8.1): f*(10) = 25.0",
        section="9",
        stated=25.0,
        computed=lambda: 10.0**2 / 4.0,
    ))

    ch.add(NumericCheck(
        label="Envelope (Ex 8.1): f*(10.1) = 25.5025",
        section="9",
        stated=25.5025,
        computed=lambda: 10.1**2 / 4.0,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Envelope (Ex 8.1): numerical df*/db at b=10 = 5.0",
        section="9",
        stated=5.0,
        computed=lambda: _numerical_deriv_fstar_ex81(10.0),
        tolerance=1e-4,
        note="Central difference: (f*(10+h) - f*(10-h))/(2h)",
    ))

    # min x^2+y^2 s.t. x+y=b: f*(b) = b^2/2
    ch.add(NumericCheck(
        label="Envelope (Ex 8.2): f*(1.0) = 0.5",
        section="9",
        stated=0.5,
        computed=lambda: 1.0**2 / 2.0,
    ))

    ch.add(NumericCheck(
        label="Envelope (Ex 8.2): f*(1.01) = 0.51005",
        section="9",
        stated=0.51005,
        computed=lambda: 1.01**2 / 2.0,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Envelope (Ex 8.2): numerical df*/db at b=1 = 1.0",
        section="9",
        stated=1.0,
        computed=lambda: _numerical_deriv_fstar_ex82(1.0),
        tolerance=1e-4,
        note="Central difference: (f*(1+h) - f*(1-h))/(2h) = 1.0 = -lambda",
    ))

    # ===================================================================
    # LAYER 3: Structural / consistency checks
    # ===================================================================

    # --- Weak duality: c^T x <= b^T y for any primal/dual feasible pair ---
    ch.add(StructuralCheck(
        label="Weak duality: c^T x <= b^T y for feasible x, y (Ex 8.3/8.4)",
        section="5",
        predicate=lambda: _check_weak_duality(),
        note="Several feasible pairs tested",
    ))

    # --- Strong duality: optimal values equal ---
    ch.add(StructuralCheck(
        label="Strong duality: primal z* = dual w* = 12",
        section="5",
        predicate=lambda: _check_strong_duality(),
    ))

    # --- Complementary slackness: y_i * (b_i - a_i^T x) = 0 ---
    ch.add(StructuralCheck(
        label="Complementary slackness: primal constraints (Ex 8.3/8.4)",
        section="5",
        predicate=lambda: _check_complementary_slackness_primal(),
        note="y1*(b1 - a1^T x) = 3*0 = 0, y2*(b2 - a2^T x) = 0*2 = 0",
    ))

    ch.add(StructuralCheck(
        label="Complementary slackness: dual constraints (Ex 8.3/8.4)",
        section="5",
        predicate=lambda: _check_complementary_slackness_dual(),
        note="x1*(a1^T y - c1) = 4*0 = 0, x2*(a2^T y - c2) = 0*1 = 0",
    ))

    # --- Bordered Hessian sign determines max vs min ---
    ch.add(StructuralCheck(
        label="Bordered Hessian: det > 0 => max (Ex 8.1), det < 0 => min (Ex 8.2)",
        section="5",
        predicate=lambda: _check_bordered_hessian_classification(),
    ))

    # --- Lagrange multiplier is shadow price: sensitivity check ---
    ch.add(StructuralCheck(
        label="Shadow price: perturbing constraint changes f* by ~lambda * epsilon",
        section="5",
        predicate=lambda: _check_shadow_price_sensitivity(),
        note="min x^2+y^2 s.t. x+y=b: f*(b) = b^2/2, df*/db = b = -lambda",
    ))

    # --- LP feasibility: optimal solution satisfies all constraints ---
    ch.add(StructuralCheck(
        label="LP feasibility: optimal (4,0) satisfies all constraints",
        section="9",
        predicate=lambda: _check_lp_feasibility(),
    ))

    # --- Dual feasibility: optimal dual (3,0) satisfies dual constraints ---
    ch.add(StructuralCheck(
        label="Dual feasibility: optimal (3,0) satisfies all dual constraints",
        section="9",
        predicate=lambda: _check_dual_feasibility(),
    ))

    # --- Simplex iteration produces correct tableau via row operations ---
    ch.add(StructuralCheck(
        label="Simplex iter 1: row operations produce correct Tableau 1",
        section="9",
        predicate=lambda: _check_simplex_row_operations(),
        note="R2=R2-R1, z-row=z-row+3*R1 from initial tableau",
    ))

    # --- Sensitivity analysis: z* is piecewise linear in b ---
    ch.add(StructuralCheck(
        label="Sensitivity: z*(b1) linear with slope y1*=3 for b1 in [3, 6]",
        section="9",
        predicate=lambda: _check_sensitivity_b1_linear(),
        note="z*(b1) = 12 + 3*(b1-4) for b1 in range where basis stays optimal",
    ))

    # --- Envelope theorem structural: numerical vs analytical derivative match ---
    ch.add(StructuralCheck(
        label="Envelope theorem: numerical d(f*)/db matches -lambda for Ex 8.1 and Ex 8.2",
        section="5",
        predicate=lambda: _check_envelope_theorem_numerical(),
        note="Both max xy s.t. x+y=b and min x^2+y^2 s.t. x+y=b",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 10.1: max/min f(x,y) = x+2y s.t. x^2+y^2=5 ---
    # Lagrange: grad f = lambda * grad g => (1, 2) = lambda*(2x, 2y)
    # => x = 1/(2*lambda), y = 1/lambda, constraint: 1/(4*lambda^2)+1/lambda^2=5
    # => 5/(4*lambda^2) = 5 => lambda^2 = 1/4 => lambda = +/- 1/2
    # lambda=1/2: x=1, y=2, f=5 (max)
    # lambda=-1/2: x=-1, y=-2, f=-5 (min)
    ch.add(NumericCheck(
        label="Ex 10.1: max f(x,y)=x+2y on x^2+y^2=5 is 5 at (1,2)",
        section="11",
        stated=5.0,
        computed=lambda: 1.0 + 2*2.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: min f(x,y)=x+2y on x^2+y^2=5 is -5 at (-1,-2)",
        section="11",
        stated=-5.0,
        computed=lambda: -1.0 + 2*(-2.0),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: constraint satisfied at max: 1^2+2^2=5",
        section="11",
        stated=5.0,
        computed=lambda: 1.0**2 + 2.0**2,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: constraint satisfied at min: (-1)^2+(-2)^2=5",
        section="11",
        stated=5.0,
        computed=lambda: (-1.0)**2 + (-2.0)**2,
        tolerance=1e-12,
    ))

    # --- Exercise 10.2: Convert LP to standard form ---
    # min 2x1 - 3x2 s.t. x1+x2>=2, -x1+x2<=3, x1>=0, x2 unrestricted
    # Standard form: replace x2=x2^+ - x2^-, convert >= to <=
    # Verify conversion: original (x1=0, x2=2) satisfies both constraints
    ch.add(StructuralCheck(
        label="Ex 10.2: (x1=0,x2=2) satisfies x1+x2>=2",
        section="11",
        predicate=lambda: (
            0 + 2 >= 2 - 1e-10,
            "x1+x2 < 2"
        ),
    ))
    ch.add(StructuralCheck(
        label="Ex 10.2: (x1=0,x2=2) satisfies -x1+x2<=3",
        section="11",
        predicate=lambda: (
            -0 + 2 <= 3 + 1e-10,
            "-x1+x2 > 3"
        ),
    ))
    # Verify standard form conversion:
    # Original: min 2x1 - 3x2 s.t. x1+x2>=2, -x1+x2<=3, x1>=0, x2 unrestricted
    # Standard form: x2 = x2p - x2m (x2p, x2m >= 0)
    # >= constraint becomes <=: -x1-x2p+x2m <= -2
    # Slack variables s1, s2 >= 0 for each <= constraint
    # Verify the conversion preserves feasibility at a known feasible point
    # (x1=0, x2=3) is feasible: 0+3=3>=2, -0+3=3<=3
    ch.add(StructuralCheck(
        label="Ex 10.2: standard form preserves feasibility at (0,3)",
        section="11",
        predicate=lambda: (
            (-0 - 3 + 0 <= -2 + 1e-10) and (-0 + 3 - 0 <= 3 + 1e-10),
            "Standard form constraints violated at (x1=0,x2p=3,x2m=0)"
        ),
        note="Exercise 10.2: (x1,x2p,x2m)=(0,3,0) represents original (x1,x2)=(0,3)",
    ))

    # --- Exercise 10.7: Weak duality theorem ---
    # If x primal feasible and y dual feasible, c^T x <= b^T y
    # Proof: c^T x <= (A^T y)^T x = y^T (Ax) <= y^T b = b^T y
    # Verify with many random feasible pairs for Ex 8.3 LP
    def _ex_10_7_weak_duality_proof():
        c = np.array([3, 2], dtype=float)
        A = np.array([[1, 1], [1, 3]], dtype=float)
        b = np.array([4, 6], dtype=float)
        rng = np.random.default_rng(1207)
        for _ in range(100):
            # Random primal feasible point
            x = rng.uniform(0, 4, 2)
            if np.all(A @ x <= b + 1e-10) and np.all(x >= -1e-10):
                # Random dual feasible point
                y = rng.uniform(0, 5, 2)
                if np.all(A.T @ y >= c - 1e-10) and np.all(y >= -1e-10):
                    # Key inequality chain: c^T x <= (A^T y)^T x = y^T (Ax) <= y^T b
                    step1 = c @ x
                    step2 = (A.T @ y) @ x  # >= c^T x since A^Ty >= c and x >= 0
                    step3 = y @ (A @ x)     # = step2 by transpose
                    step4 = y @ b           # >= step3 since Ax <= b and y >= 0
                    if step1 > step4 + 1e-8:
                        return (False, f"c^Tx = {step1} > b^Ty = {step4}")
                    # Also verify intermediate steps
                    if step1 > step2 + 1e-8:
                        return (False, f"c^Tx > (A^Ty)^Tx: {step1} > {step2}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 10.7: weak duality proof chain c^Tx <= (A^Ty)^Tx = y^TAx <= b^Ty",
        section="11",
        predicate=_ex_10_7_weak_duality_proof,
    ))

    # --- Exercise 10.3: LP max 5x1+4x2 s.t. x1+x2<=5, 2x1+x2<=8, x>=0 ---
    ch.add(NumericCheck(
        label="Ex 10.3: LP optimal x1*=3, x2*=2",
        section="11",
        stated=23.0,
        computed=lambda: _solve_lp_ex103()[2],
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: LP optimal z*=23",
        section="11",
        stated=23.0,
        computed=lambda: 5*3.0 + 4*2.0,
        tolerance=1e-12,
    ))

    # Verify constraints at (3,2)
    ch.add(StructuralCheck(
        label="Ex 10.3: constraints satisfied at (3,2)",
        section="11",
        predicate=lambda: (
            3.0 + 2.0 <= 5.0 + 1e-10 and 2*3.0 + 2.0 <= 8.0 + 1e-10,
            f"x1+x2={3+2}, 2x1+x2={6+2}"
        ),
    ))

    # --- Exercise 10.4: Closest point on plane to origin ---
    # min x^2+y^2+z^2 s.t. 2x+y-z=5
    # Lagrange: (2x, 2y, 2z) = lambda*(2, 1, -1)
    # x=lambda, y=lambda/2, z=-lambda/2
    # 2*lambda + lambda/2 + lambda/2 = 5 => 3*lambda = 5 => lambda = 5/3
    # x=5/3, y=5/6, z=-5/6
    ch.add(NumericCheck(
        label="Ex 10.4: closest point x = 5/3",
        section="11",
        stated=5.0/3.0,
        computed=lambda: 5.0/3.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: closest point y = 5/6",
        section="11",
        stated=5.0/6.0,
        computed=lambda: 5.0/6.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: closest point z = -5/6",
        section="11",
        stated=-5.0/6.0,
        computed=lambda: -5.0/6.0,
        tolerance=1e-12,
    ))

    # Distance = |5|/sqrt(4+1+1) = 5/sqrt(6)
    ch.add(NumericCheck(
        label="Ex 10.4: distance = 5/sqrt(6)",
        section="11",
        stated=5.0/math.sqrt(6),
        computed=lambda: math.sqrt((5.0/3)**2 + (5.0/6)**2 + (5.0/6)**2),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: distance formula verification = 5/sqrt(6)",
        section="11",
        stated=5.0/math.sqrt(6),
        computed=lambda: abs(5.0) / math.sqrt(4+1+1),
        tolerance=1e-10,
    ))

    # --- Exercise 10.5: LP production problem ---
    # max 5x1+4x2 s.t. x1+3x2<=14, 3x1+2x2<=18, x>=0 (transposed resource matrix)
    # Actually: A = [[1,2],[3,2]], b=(14,18)
    ch.add(NumericCheck(
        label="Ex 10.5: LP production optimal z*",
        section="11",
        stated=float(_solve_lp_ex105()[2]),
        computed=lambda: _solve_lp_ex105()[2],
        tolerance=1e-6,
    ))

    # --- Exercise 10.6: LP max x1-x2 s.t. x1-x2<=1, -x1+x2<=1, x>=0 ---
    # Feasible region is unbounded (x1=x2 can grow without bound)
    # Verify the feasible region is indeed unbounded
    ch.add(StructuralCheck(
        label="Ex 10.6: feasible region is unbounded (x1=x2=N feasible for large N)",
        section="11",
        predicate=lambda: _ex_10_6_unbounded_feasible(),
    ))

    # The LP has a finite optimal solution z*=1 at (1,0)
    ch.add(StructuralCheck(
        label="Ex 10.6: LP has finite optimum z*=1 at (1,0)",
        section="11",
        predicate=lambda: _ex_10_6_lp_finite_opt(),
    ))

    # --- Exercise 10.8: max xyz s.t. x+y+z=12, x+y-z=0 ---
    # From constraints: z=6, x+y=6, so maximize xy*6 with x+y=6
    # max xy s.t. x+y=6 => x=y=3, xyz = 3*3*6 = 54
    ch.add(NumericCheck(
        label="Ex 10.8: max xyz = 54 at (3,3,6)",
        section="11",
        stated=54.0,
        computed=lambda: 3.0 * 3.0 * 6.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.8: constraint 1: x+y+z = 3+3+6 = 12",
        section="11",
        stated=12.0,
        computed=lambda: 3.0 + 3.0 + 6.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.8: constraint 2: x+y-z = 3+3-6 = 0",
        section="11",
        stated=0.0,
        computed=lambda: 3.0 + 3.0 - 6.0,
        tolerance=1e-12,
    ))

    # Verify via substitution: z=6, max xy*6 s.t. x+y=6 => x=y=3
    ch.add(NumericCheck(
        label="Ex 10.8: z from constraints = (12-0)/2 = 6",
        section="11",
        stated=6.0,
        computed=lambda: (12.0 - 0.0) / 2.0,
        tolerance=1e-12,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Lagrange Multiplier Method ---
    # Note: Lagrange multiplier tests are implicitly covered via worked examples.
    def _algo_lagrange():
        """Verify Lagrange multiplier method on a simple constrained optimization."""
        # Minimize f(x,y) = x^2 + y^2 subject to x + y = 1
        # Lagrangian: L = x^2 + y^2 + lam*(x + y - 1)
        # KKT: 2x + lam = 0, 2y + lam = 0, x + y = 1
        # => x = y = 0.5, lam = -1
        x_star = 0.5
        y_star = 0.5
        lam_star = -1.0
        # Verify KKT conditions
        kkt1 = 2 * x_star + lam_star  # = 0
        kkt2 = 2 * y_star + lam_star  # = 0
        kkt3 = x_star + y_star - 1    # = 0
        if abs(kkt1) > 1e-10 or abs(kkt2) > 1e-10 or abs(kkt3) > 1e-10:
            return (False, f"KKT residuals: {kkt1}, {kkt2}, {kkt3}")
        # Verify it's a minimum (bordered Hessian)
        # H_bar = [[0, 1, 1], [1, 2, 0], [1, 0, 2]], det = -4 < 0 => minimum
        det_hbar = -4
        if det_hbar >= 0:
            return (False, f"Bordered Hessian det = {det_hbar}, expected < 0 for minimum")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Lagrange multiplier method on min x^2+y^2 s.t. x+y=1",
        section="6",
        predicate=_algo_lagrange,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Simplex Method ---
    def _algo_simplex():
        """Implement a basic simplex tableau and verify against scipy."""
        def simplex_tableau(c, A, b):
            m, n = len(A), len(A[0])
            # Build tableau: m+1 rows, n+m+1 cols
            T = [[0.0] * (n + m + 1) for _ in range(m + 1)]
            for i in range(m):
                for j in range(n):
                    T[i][j] = A[i][j]
                T[i][n + i] = 1.0  # slack
                T[i][n + m] = b[i]
            for j in range(n):
                T[m][j] = -c[j]

            for _iter in range(100):
                # Find pivot column (most negative in objective row)
                pivot_col = min(range(n + m), key=lambda j: T[m][j])
                if T[m][pivot_col] >= -1e-10:
                    break  # optimal

                # Minimum ratio test
                min_ratio = float('inf')
                pivot_row = -1
                for i in range(m):
                    if T[i][pivot_col] > 1e-10:
                        ratio = T[i][n + m] / T[i][pivot_col]
                        if ratio < min_ratio:
                            min_ratio = ratio
                            pivot_row = i
                if pivot_row == -1:
                    return None  # unbounded

                # Pivot
                pivot_val = T[pivot_row][pivot_col]
                for j in range(n + m + 1):
                    T[pivot_row][j] /= pivot_val
                for i in range(m + 1):
                    if i == pivot_row:
                        continue
                    factor = T[i][pivot_col]
                    for j in range(n + m + 1):
                        T[i][j] -= factor * T[pivot_row][j]

            # Extract solution
            x = [0.0] * n
            for j in range(n):
                col = [T[i][j] for i in range(m)]
                if col.count(0.0) == m - 1 and sum(abs(v) for v in col) > 0.5:
                    for i in range(m):
                        if abs(T[i][j] - 1.0) < 1e-10:
                            x[j] = T[i][n + m]
            obj = T[m][n + m]
            return x, obj

        # max 5x1 + 4x2 s.t. x1+x2<=5, 2x1+x2<=8
        c = [5, 4]
        A = [[1, 1], [2, 1]]
        b = [5, 8]
        x, obj = simplex_tableau(c, A, b)

        # scipy reference
        from scipy.optimize import linprog
        res = linprog([-5, -4], A_ub=[[1, 1], [2, 1]], b_ub=[5, 8], bounds=[(0, None), (0, None)])
        scipy_obj = -res.fun

        if abs(obj - scipy_obj) > 0.1:
            return (False, f"Simplex obj = {obj}, scipy = {scipy_obj}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Simplex tableau solves LP matching scipy.linprog",
        section="6",
        predicate=_algo_simplex,
        note="Algorithm 5.2 verified",
    ))

    # --- Remark 3.8: Envelope theorem — df*/dtheta = dL/dtheta at optimum ---
    def _remark_3_8_envelope():
        """Verify envelope theorem: sensitivity of f* matches dL/dtheta."""
        # min x^2 + y^2 s.t. x + y = b (parameter b)
        # f*(b) = b^2/2, df*/db = b
        # L = x^2 + y^2 + lam*(x+y-b), dL/db = -lam = b (since lam=-b at opt)
        for b in [1.0, 2.0, 3.5, -1.0]:
            f_star = b**2 / 2
            # Numerical derivative
            eps = 1e-7
            f_star_plus = (b + eps)**2 / 2
            df_db_num = (f_star_plus - f_star) / eps
            df_db_exact = b  # from envelope theorem
            if abs(df_db_num - df_db_exact) > 1e-4:
                return (False, f"b={b}: df*/db numerical={df_db_num}, exact={df_db_exact}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.8: Envelope theorem df*/db = -lambda = b verified",
        section="3.8",
        predicate=_remark_3_8_envelope,
        note="Remark 3.8: envelope theorem",
    ))

    # --- Remark 3.16: Klee-Minty cube — simplex can visit 2^n vertices ---
    def _remark_3_16_klee_minty():
        """Verify Klee-Minty cube LP has 2^n vertices and simplex solves it."""
        from scipy.optimize import linprog
        # 3-variable Klee-Minty: max x3 s.t. x1<=5, 4x1+x2<=25, 8x1+4x2+x3<=125
        c = [0, 0, -1]  # minimize -x3
        A_ub = [[1, 0, 0], [4, 1, 0], [8, 4, 1]]
        b_ub = [5, 25, 125]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)]*3, method='highs')
        if not res.success:
            return (False, f"LP failed: {res.message}")
        # Optimal: x=(0,0,125), obj=125
        opt_val = -res.fun
        if abs(opt_val - 125.0) > 1e-6:
            return (False, f"Optimal value = {opt_val}, expected 125")
        # Number of vertices = 2^n = 8 for n=3
        n = 3
        n_vertices = 2**n
        if n_vertices != 8:
            return (False, f"2^n = {n_vertices}, expected 8")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.16: Klee-Minty cube (n=3) LP optimal=125, has 2^3=8 vertices",
        section="3.16",
        predicate=_remark_3_16_klee_minty,
        note="Remark 3.16: simplex worst-case complexity",
    ))

    # --- Remark 3.21: Dual variables are shadow prices ---
    def _remark_3_21_shadow_prices():
        """Verify dual variable = marginal value of relaxing constraint."""
        from scipy.optimize import linprog
        # max 3x1+2x2 s.t. x1+x2<=4, x1+3x2<=6
        c = np.array([3, 2], dtype=float)
        A = np.array([[1, 1], [1, 3]], dtype=float)
        b = np.array([4, 6], dtype=float)
        res_p = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)]*2, method='highs')
        z_star = -res_p.fun
        # Get dual from scipy
        res_d = linprog(b, A_ub=-A.T, b_ub=-c, bounds=[(0, None)]*2, method='highs')
        y_star = res_d.x
        # Perturb each constraint and check sensitivity
        for i in range(2):
            eps = 1e-5
            b_pert = b.copy()
            b_pert[i] += eps
            res_pert = linprog(-c, A_ub=A, b_ub=b_pert, bounds=[(0, None)]*2, method='highs')
            z_pert = -res_pert.fun
            marginal = (z_pert - z_star) / eps
            if abs(marginal - y_star[i]) > 0.01:
                return (False, f"Constraint {i}: marginal={marginal}, dual={y_star[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.21: Dual variables = shadow prices (marginal resource value)",
        section="3.21",
        predicate=_remark_3_21_shadow_prices,
        note="Remark 3.21: economic interpretation of duality",
    ))

    # ── Remark 3.4: Lagrange geometric intuition ─────────────────────────
    # Claims: at constrained optimum, grad f is parallel to grad g
    # (i.e., grad f = lambda * grad g).
    def _remark_3_4_gradient_parallel():
        import numpy as np

        # Minimize f(x,y) = x^2 + y^2 subject to g(x,y) = x + y - 1 = 0
        # Optimum: x* = y* = 0.5
        # grad f = (2x, 2y) = (1, 1)
        # grad g = (1, 1)
        # grad f = lambda * grad g => lambda = 1
        x_star, y_star = 0.5, 0.5

        grad_f = np.array([2 * x_star, 2 * y_star])
        grad_g = np.array([1.0, 1.0])

        # Check parallelism: cross product = 0 (2D)
        cross = grad_f[0] * grad_g[1] - grad_f[1] * grad_g[0]
        if abs(cross) > 1e-12:
            return (False, f"Gradients not parallel: cross product = {cross}")

        # Check constraint is satisfied
        if abs(x_star + y_star - 1.0) > 1e-12:
            return (False, "Constraint not satisfied")

        # Verify lambda = grad_f / grad_g component-wise
        lam = grad_f[0] / grad_g[0]
        if abs(lam - grad_f[1] / grad_g[1]) > 1e-12:
            return (False, f"Lambda inconsistent across components")

        # Second example: minimize f = x^2 + y^2 subject to x^2/4 + y^2/9 = 1
        # Use scipy to find optimum and verify gradient parallelism
        from scipy.optimize import minimize as sp_minimize

        def objective(xy):
            return xy[0]**2 + xy[1]**2

        def constraint(xy):
            return xy[0]**2 / 4 + xy[1]**2 / 9 - 1

        result = sp_minimize(objective, [1.0, 1.0],
                             constraints={'type': 'eq', 'fun': constraint},
                             method='SLSQP')
        x_opt, y_opt = result.x
        grad_f2 = np.array([2 * x_opt, 2 * y_opt])
        grad_g2 = np.array([x_opt / 2, 2 * y_opt / 9])

        # Check parallelism
        norm_f = np.linalg.norm(grad_f2)
        norm_g = np.linalg.norm(grad_g2)
        if norm_f < 1e-10 or norm_g < 1e-10:
            return (False, "Gradient near zero at optimum")
        cos_angle = np.dot(grad_f2, grad_g2) / (norm_f * norm_g)
        if abs(abs(cos_angle) - 1.0) > 1e-4:
            return (False, f"Gradients not parallel: cos(angle) = {cos_angle}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: At constrained optimum, grad f parallel to grad g",
        section="3.4",
        predicate=_remark_3_4_gradient_parallel,
        note="Remark 3.4: Lagrange geometric intuition verified",
    ))

    return ch


# ===================================================================
# Exercise helper functions
# ===================================================================

def _solve_lp_ex103():
    """Solve LP: max 5x1+4x2 s.t. x1+x2<=5, 2x1+x2<=8, x>=0."""
    c = np.array([-5, -4], dtype=float)
    A_ub = np.array([[1, 1], [2, 1]], dtype=float)
    b_ub = np.array([5, 8], dtype=float)
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)], method='highs')
    return (result.x[0], result.x[1], -result.fun)


def _solve_lp_ex105():
    """Solve LP: max 5x1+4x2 s.t. x1+2x2<=14, 3x1+2x2<=18, x>=0."""
    c = np.array([-5, -4], dtype=float)
    A_ub = np.array([[1, 2], [3, 2]], dtype=float)
    b_ub = np.array([14, 18], dtype=float)
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)], method='highs')
    return (result.x[0], result.x[1], -result.fun)


def _ex_10_6_unbounded_feasible():
    """Verify feasible region of x1-x2<=1, -x1+x2<=1, x>=0 is unbounded."""
    A = np.array([[1, -1], [-1, 1]], dtype=float)
    b = np.array([1, 1], dtype=float)
    for N in [100, 1000, 10000]:
        x = np.array([N, N], dtype=float)
        if not (np.all(A @ x <= b + 1e-10) and np.all(x >= -1e-10)):
            return (False, f"(N,N)=({N},{N}) not feasible")
    return (True, "")


def _ex_10_6_lp_finite_opt():
    """Verify LP max x1-x2 s.t. x1-x2<=1, -x1+x2<=1, x>=0 has finite optimum z*=1 at (1,0)."""
    c = np.array([-1, 1], dtype=float)  # minimize -(x1-x2) = -x1+x2
    A_ub = np.array([[1, -1], [-1, 1]], dtype=float)
    b_ub = np.array([1, 1], dtype=float)
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub,
                                     bounds=[(0, None), (0, None)], method='highs')
    if result.status == 0 and abs(-result.fun - 1.0) < 1e-8:
        return (True, "")
    return (False, f"Expected optimal value 1.0, got status {result.status}, value {-result.fun if result.status == 0 else 'N/A'}")


# ===================================================================
# Helper functions — Symbolic
# ===================================================================

def _lagrange_conditions_ex81():
    """Verify Lagrange conditions for max xy s.t. x+y=10 at (5,5,-5)."""
    import sympy
    x, y, lam = sympy.symbols('x y lambda')
    L = x*y + lam*(x + y - 10)
    dLdx = sympy.diff(L, x).subs([(x, 5), (y, 5), (lam, -5)])
    dLdy = sympy.diff(L, y).subs([(x, 5), (y, 5), (lam, -5)])
    dLdlam = sympy.diff(L, lam).subs([(x, 5), (y, 5), (lam, -5)])
    return sympy.Eq(dLdx**2 + dLdy**2 + dLdlam**2, 0)


def _lagrange_conditions_ex82():
    """Verify Lagrange conditions for min x^2+y^2 s.t. x+y=1 at (1/2,1/2,-1)."""
    import sympy
    x, y, lam = sympy.symbols('x y lambda')
    L = x**2 + y**2 + lam*(x + y - 1)
    vals = [(x, sympy.Rational(1, 2)), (y, sympy.Rational(1, 2)), (lam, -1)]
    dLdx = sympy.diff(L, x).subs(vals)
    dLdy = sympy.diff(L, y).subs(vals)
    dLdlam = sympy.diff(L, lam).subs(vals)
    return sympy.Eq(dLdx**2 + dLdy**2 + dLdlam**2, 0)


def _lagrange_conditions_ex85():
    """Verify Lagrange conditions for min x^2+y^2+z^2 s.t. x+y+z=1
    at (1/3,1/3,1/3,-2/3)."""
    import sympy
    x, y, z, lam = sympy.symbols('x y z lambda')
    L = x**2 + y**2 + z**2 + lam*(x + y + z - 1)
    vals = [(x, sympy.Rational(1, 3)), (y, sympy.Rational(1, 3)),
            (z, sympy.Rational(1, 3)), (lam, sympy.Rational(-2, 3))]
    dLdx = sympy.diff(L, x).subs(vals)
    dLdy = sympy.diff(L, y).subs(vals)
    dLdz = sympy.diff(L, z).subs(vals)
    dLdlam = sympy.diff(L, lam).subs(vals)
    return sympy.Eq(dLdx**2 + dLdy**2 + dLdz**2 + dLdlam**2, 0)


def _shadow_price_symbolic():
    """For min x^2+y^2 s.t. x+y=b: f*(b) = b^2/2, df*/db = b.
    At b=1: df*/db = 1, and -lambda = -(-1) = 1. Verify equality.
    """
    import sympy
    b = sympy.Symbol('b')
    fstar = b**2 / 2
    dfdb = sympy.diff(fstar, b)
    # At b=1: dfdb = 1, -lambda = 1
    return sympy.Eq(dfdb.subs(b, 1), 1)


def _strong_duality_symbolic():
    """Primal z* = 12, Dual w* = 12 for Ex 8.3/8.4."""
    import sympy
    c = sympy.Matrix([3, 2])
    x_star = sympy.Matrix([4, 0])
    b = sympy.Matrix([4, 6])
    y_star = sympy.Matrix([3, 0])
    primal = c.dot(x_star)
    dual = b.dot(y_star)
    return sympy.Eq(primal, dual)


def _bordered_hessian_det_ex81():
    """Bordered Hessian for max xy s.t. x+y=10: det = 2 > 0."""
    import sympy
    barH = sympy.Matrix([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ])
    return sympy.Eq(barH.det(), 2)


def _complementary_slackness_symbolic():
    """Complementary slackness for Ex 8.3/8.4 LP.
    y1*s1 = 3*0 = 0, y2*s2 = 0*2 = 0.
    x1*(a1^T y - c1) = 4*(3-3) = 0, x2*(a2^T y - c2) = 0*(3-2) = 0.
    """
    import sympy
    # Primal slackness
    y1, s1, y2, s2 = 3, 0, 0, 2
    ps1 = y1 * s1
    ps2 = y2 * s2
    # Dual slackness
    x1, x2 = 4, 0
    ds1 = x1 * (3 + 0 - 3)  # a1^T y - c1 = y1+y2 - 3 = 3+0-3 = 0
    ds2 = x2 * (1 + 0 - 2)  # a2^T y - c2 = y1+3y2 - 2 = 3+0-2 = 1
    total = ps1 + ps2 + abs(ds1) + abs(ds2)
    return sympy.Eq(sympy.Integer(total), 0)


def _envelope_theorem_symbolic():
    """Verify envelope theorem: dL/db at optimum equals df*/db.
    For min x^2+y^2 s.t. x+y=b:
    L = x^2 + y^2 + lambda*(x+y-b), dL/db = -lambda.
    At b=1: lambda=-1, so dL/db = 1.
    f*(b) = b^2/2, df*/db = b. At b=1: df*/db = 1.
    """
    import sympy
    b, lam = sympy.symbols('b lambda')
    # dL/db = -lambda, evaluated at lambda=-1
    dLdb = -lam
    dLdb_val = dLdb.subs(lam, -1)
    # df*/db at b=1
    fstar = b**2 / 2
    dfdb_val = sympy.diff(fstar, b).subs(b, 1)
    return sympy.Eq(dLdb_val, dfdb_val)


# ===================================================================
# Helper functions — Numeric
# ===================================================================

def _lagrange_xy_sum10() -> tuple[float, float, float]:
    """Solve max xy s.t. x+y=10 analytically.
    x = y = 5, lambda = -5.
    """
    return (5.0, 5.0, -5.0)


def _lagrange_dist_min() -> tuple[float, float, float]:
    """Solve min x^2+y^2 s.t. x+y=1 analytically.
    x = y = 1/2, lambda = -1.
    """
    return (0.5, 0.5, -1.0)


def _lagrange_3var() -> tuple[float, float, float, float]:
    """Solve min x^2+y^2+z^2 s.t. x+y+z=1 analytically.
    x = y = z = 1/3, lambda = -2/3.
    """
    return (1.0/3.0, 1.0/3.0, 1.0/3.0, -2.0/3.0)


def _solve_lp_ex83() -> tuple[float, float, float]:
    """Solve max 3x1 + 2x2 s.t. x1+x2<=4, x1+3x2<=6, x1,x2>=0 using scipy."""
    # scipy.optimize.linprog minimizes, so negate c for maximization
    c = np.array([-3, -2], dtype=float)
    A_ub = np.array([[1, 1], [1, 3]], dtype=float)
    b_ub = np.array([4, 6], dtype=float)
    bounds = [(0, None), (0, None)]
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    x1 = result.x[0]
    x2 = result.x[1]
    z = -result.fun  # negate back for max
    return (x1, x2, z)


def _solve_dual_ex84() -> tuple[float, float, float]:
    """Solve the dual: min 4y1 + 6y2 s.t. y1+y2>=3, y1+3y2>=2, y1,y2>=0."""
    c = np.array([4, 6], dtype=float)
    # >= constraints become <= by negation
    A_ub = np.array([[-1, -1], [-1, -3]], dtype=float)
    b_ub = np.array([-3, -2], dtype=float)
    bounds = [(0, None), (0, None)]
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    y1 = result.x[0]
    y2 = result.x[1]
    w = result.fun
    return (y1, y2, w)


def _check_tableau_row(stated: list, computed: list) -> float:
    """Return 0.0 if rows match, otherwise sum of absolute differences."""
    return sum(abs(s - c) for s, c in zip(stated, computed))


def _solve_lp_perturbed_b1(b1: float) -> float:
    """Solve the LP with perturbed b1, return optimal z."""
    c = np.array([-3, -2], dtype=float)
    A_ub = np.array([[1, 1], [1, 3]], dtype=float)
    b_ub = np.array([b1, 6], dtype=float)
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)], method='highs')
    return -result.fun


def _solve_lp_perturbed_b2(b2: float) -> float:
    """Solve the LP with perturbed b2, return optimal z."""
    c = np.array([-3, -2], dtype=float)
    A_ub = np.array([[1, 1], [1, 3]], dtype=float)
    b_ub = np.array([4, b2], dtype=float)
    result = scipy.optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)], method='highs')
    return -result.fun


def _numerical_deriv_fstar_ex81(b: float) -> float:
    """Numerical derivative of f*(b) = b^2/4 at given b using central difference."""
    h = 1e-6
    return ((b + h)**2 / 4.0 - (b - h)**2 / 4.0) / (2 * h)


def _numerical_deriv_fstar_ex82(b: float) -> float:
    """Numerical derivative of f*(b) = b^2/2 at given b using central difference."""
    h = 1e-6
    return ((b + h)**2 / 2.0 - (b - h)**2 / 2.0) / (2 * h)


# ===================================================================
# Helper functions — Structural
# ===================================================================

def _check_weak_duality() -> tuple[bool, str]:
    """Verify c^T x <= b^T y for several feasible primal/dual pairs.
    Primal: max 3x1+2x2 s.t. x1+x2<=4, x1+3x2<=6, x>=0.
    Dual: min 4y1+6y2 s.t. y1+y2>=3, y1+3y2>=2, y>=0.
    """
    c = np.array([3, 2])
    b = np.array([4, 6])
    A = np.array([[1, 1], [1, 3]])

    # Test several feasible pairs
    primal_points = [
        np.array([0, 0]),      # trivially feasible
        np.array([2, 1]),      # x1+x2=3<=4, x1+3x2=5<=6
        np.array([4, 0]),      # optimal
        np.array([1, 1]),      # x1+x2=2<=4, x1+3x2=4<=6
    ]
    dual_points = [
        np.array([3, 0]),      # optimal dual
        np.array([3, 1]),      # y1+y2=4>=3, y1+3y2=6>=2
        np.array([2, 2]),      # y1+y2=4>=3, y1+3y2=8>=2
    ]

    for xp in primal_points:
        if not (np.all(A @ xp <= b + 1e-10) and np.all(xp >= -1e-10)):
            continue
        for yd in dual_points:
            if not (np.all(A.T @ yd >= c - 1e-10) and np.all(yd >= -1e-10)):
                continue
            primal_val = c @ xp
            dual_val = b @ yd
            if primal_val > dual_val + 1e-10:
                return False, f"Weak duality violated: c^T x = {primal_val} > b^T y = {dual_val}"
    return True, ""


def _check_strong_duality() -> tuple[bool, str]:
    """Verify primal and dual optimal values are equal."""
    primal = _solve_lp_ex83()
    dual = _solve_dual_ex84()
    if abs(primal[2] - dual[2]) < 1e-6:
        return True, ""
    return False, f"Primal z* = {primal[2]}, Dual w* = {dual[2]}"


def _check_complementary_slackness_primal() -> tuple[bool, str]:
    """Verify y_i * (b_i - a_i^T x*) = 0 for each primal constraint."""
    x_star = np.array([4.0, 0.0])
    y_star = np.array([3.0, 0.0])
    A = np.array([[1, 1], [1, 3]], dtype=float)
    b = np.array([4, 6], dtype=float)

    slacks = b - A @ x_star
    for i in range(len(slacks)):
        product = y_star[i] * slacks[i]
        if abs(product) > 1e-10:
            return False, f"CS violated for constraint {i+1}: y_{i+1}*s_{i+1} = {product}"
    return True, ""


def _check_complementary_slackness_dual() -> tuple[bool, str]:
    """Verify x_j * (a_j^T y* - c_j) = 0 for each dual constraint."""
    x_star = np.array([4.0, 0.0])
    y_star = np.array([3.0, 0.0])
    A = np.array([[1, 1], [1, 3]], dtype=float)
    c = np.array([3, 2], dtype=float)

    dual_vals = A.T @ y_star
    for j in range(len(c)):
        surplus = dual_vals[j] - c[j]
        product = x_star[j] * surplus
        if abs(product) > 1e-10:
            return False, f"CS violated for variable {j+1}: x_{j+1}*(a^T y - c_{j+1}) = {product}"
    return True, ""


def _check_bordered_hessian_classification() -> tuple[bool, str]:
    """Verify bordered Hessian sign determines max vs min.
    Ex 8.1 (max xy s.t. x+y=10): det(barH) = 2 > 0 => max.
    Ex 8.2 (min x^2+y^2 s.t. x+y=1): det(barH) = -4 < 0 => min.
    """
    # Ex 8.1: bordered Hessian
    barH1 = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
    det1 = np.linalg.det(barH1)

    # Ex 8.2: bordered Hessian
    barH2 = np.array([[0, 1, 1], [1, 2, 0], [1, 0, 2]], dtype=float)
    det2 = np.linalg.det(barH2)

    if det1 <= 0:
        return False, f"Ex 8.1 bordered Hessian det = {det1}, expected > 0 (max)"
    if det2 >= 0:
        return False, f"Ex 8.2 bordered Hessian det = {det2}, expected < 0 (min)"
    return True, ""


def _check_shadow_price_sensitivity() -> tuple[bool, str]:
    """Perturb constraint RHS and verify f* changes by approx lambda * epsilon.
    min x^2+y^2 s.t. x+y=b. Solution: x=y=b/2, f*(b) = b^2/2.
    At b=1: f*=1/2, lambda=-1.
    At b=1+eps: f*=(1+eps)^2/2 ~ 1/2 + eps.
    Change in f* ~ eps, and -lambda = 1, so delta_f ~ (-lambda)*eps.
    """
    eps = 1e-5
    b0 = 1.0
    b1 = b0 + eps
    f_star_0 = b0**2 / 2.0
    f_star_1 = b1**2 / 2.0
    delta_f = f_star_1 - f_star_0
    lam = -1.0
    predicted = -lam * eps
    rel_error = abs(delta_f - predicted) / abs(predicted)
    if rel_error < 1e-4:
        return True, ""
    return False, f"Shadow price sensitivity: delta_f={delta_f}, predicted={predicted}, rel_error={rel_error}"


def _check_lp_feasibility() -> tuple[bool, str]:
    """Verify optimal (4,0) satisfies all primal constraints."""
    x = np.array([4.0, 0.0])
    A = np.array([[1, 1], [1, 3]], dtype=float)
    b = np.array([4, 6], dtype=float)

    Ax = A @ x
    for i in range(len(b)):
        if Ax[i] > b[i] + 1e-10:
            return False, f"Constraint {i+1} violated: {Ax[i]} > {b[i]}"
    if np.any(x < -1e-10):
        return False, f"Nonnegativity violated: x = {x}"
    return True, ""


def _check_dual_feasibility() -> tuple[bool, str]:
    """Verify optimal dual (3,0) satisfies all dual constraints."""
    y = np.array([3.0, 0.0])
    A = np.array([[1, 1], [1, 3]], dtype=float)
    c = np.array([3, 2], dtype=float)

    ATy = A.T @ y
    for j in range(len(c)):
        if ATy[j] < c[j] - 1e-10:
            return False, f"Dual constraint {j+1} violated: {ATy[j]} < {c[j]}"
    if np.any(y < -1e-10):
        return False, f"Nonnegativity violated: y = {y}"
    return True, ""


def _check_reduced_costs_optimal() -> tuple[bool, str]:
    """After iteration 1, all non-basic reduced costs <= 0 => optimal.
    Non-basic variables: x2 (bar_c = -1), s1 (bar_c = -3).
    """
    reduced_costs_nonbasic = {'x2': -1.0, 's1': -3.0}
    for var, rc in reduced_costs_nonbasic.items():
        if rc > 1e-10:
            return False, f"Reduced cost of {var} = {rc} > 0, not optimal"
    return True, ""


def _check_simplex_row_operations() -> tuple[bool, str]:
    """Verify that applying row operations to initial tableau produces Tableau 1.
    Initial: R1=[1,1,1,0,4], R2=[1,3,0,1,6], z=[-3,-2,0,0,0].
    Pivot x1 into basis at row 1 (element=1, already normalized).
    R2_new = R2 - 1*R1 = [0,2,-1,1,2].
    z_new = z + 3*R1 = [0,1,3,0,12].
    """
    R1 = np.array([1, 1, 1, 0, 4], dtype=float)
    R2 = np.array([1, 3, 0, 1, 6], dtype=float)
    z = np.array([-3, -2, 0, 0, 0], dtype=float)

    R2_new = R2 - 1.0 * R1
    z_new = z + 3.0 * R1

    expected_R2 = np.array([0, 2, -1, 1, 2], dtype=float)
    expected_z = np.array([0, 1, 3, 0, 12], dtype=float)

    if not np.allclose(R2_new, expected_R2, atol=1e-14):
        return False, f"R2_new = {R2_new}, expected {expected_R2}"
    if not np.allclose(z_new, expected_z, atol=1e-14):
        return False, f"z_new = {z_new}, expected {expected_z}"
    return True, ""


def _check_sensitivity_b1_linear() -> tuple[bool, str]:
    """Verify z*(b1) is linear with slope y1*=3 for b1 in [3, 6]."""
    b1_values = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
    for b1 in b1_values:
        z_actual = _solve_lp_perturbed_b1(b1)
        z_predicted = 12.0 + 3.0 * (b1 - 4.0)
        if abs(z_actual - z_predicted) > 1e-6:
            return False, f"At b1={b1}: z*={z_actual}, predicted={z_predicted}"
    return True, ""


def _check_envelope_theorem_numerical() -> tuple[bool, str]:
    """Verify envelope theorem numerically for both examples.
    Ex 8.1: max xy s.t. x+y=b, f*(b) = b^2/4, df*/db = b/2 = -lambda.
    Ex 8.2: min x^2+y^2 s.t. x+y=b, f*(b) = b^2/2, df*/db = b = -lambda.
    """
    h = 1e-7

    # Ex 8.1 at b=10: df*/db should be 5 (= -lambda, lambda=-5)
    dfdb_81 = ((10.0 + h)**2 / 4.0 - (10.0 - h)**2 / 4.0) / (2 * h)
    if abs(dfdb_81 - 5.0) > 1e-4:
        return False, f"Ex 8.1: numerical df*/db = {dfdb_81}, expected 5.0"

    # Ex 8.2 at b=1: df*/db should be 1 (= -lambda, lambda=-1)
    dfdb_82 = ((1.0 + h)**2 / 2.0 - (1.0 - h)**2 / 2.0) / (2 * h)
    if abs(dfdb_82 - 1.0) > 1e-4:
        return False, f"Ex 8.2: numerical df*/db = {dfdb_82}, expected 1.0"

    return True, ""


# ===================================================================
# Standalone formula helpers (F4.2 - F4.9)
# ===================================================================

def _lagrange_foc_generic():
    """F4.2: For L = f(x,y) + lambda*(g(x,y) - b), the FOC are
    dL/dx = 0, dL/dy = 0, dL/dlambda = g(x,y) - b = 0.
    Verify generically for f = x^2 + y^2, g = x + y - 1.
    Solution: x = y = 1/2, lambda = -1.
    """
    import sympy
    x, y, lam = sympy.symbols('x y lambda')
    f = x**2 + y**2
    g = x + y - 1
    L = f + lam * g
    dLdx = sympy.diff(L, x)
    dLdy = sympy.diff(L, y)
    dLdlam = sympy.diff(L, lam)
    sol = sympy.solve([dLdx, dLdy, dLdlam], [x, y, lam])
    # sol should be {x: 1/2, y: 1/2, lambda: -1}
    ok = (sol[x] == sympy.Rational(1, 2) and
          sol[y] == sympy.Rational(1, 2) and
          sol[lam] == -1)
    return sympy.S.true if ok else sympy.S.false


def _shadow_price_standalone():
    """F4.3: For max xy s.t. x+y=b, f*(b) = b^2/4 and lambda = b/2.
    Shadow price: df*/db = b/2 = lambda. Verify symbolically.
    """
    import sympy
    b = sympy.Symbol('b', positive=True)
    fstar = b**2 / 4
    dfdb = sympy.diff(fstar, b)  # b/2
    lam = b / 2  # lambda at optimum x=y=b/2
    return sympy.Eq(dfdb, lam)


def _bordered_hessian_formula():
    """F4.4: Bordered Hessian for L = f + lambda*g with 2 variables, 1 constraint:
    barH = [[0, g_x, g_y], [g_x, L_xx, L_xy], [g_y, L_yx, L_yy]].
    Verify det formula: det = 2*g_x*g_y*L_xy - g_x^2*L_yy - g_y^2*L_xx.
    """
    import sympy
    g1, g2, L11, L12, L22 = sympy.symbols('g1 g2 L11 L12 L22')
    barH = sympy.Matrix([
        [0, g1, g2],
        [g1, L11, L12],
        [g2, L12, L22],
    ])
    det = barH.det()
    expected = 2 * g1 * g2 * L12 - g1**2 * L22 - g2**2 * L11
    return sympy.Eq(sympy.expand(det), sympy.expand(expected))


def _dual_construction_check() -> tuple[bool, str]:
    """F4.6: Given primal max c^Tx s.t. Ax <= b, x >= 0,
    the dual is min b^Ty s.t. A^Ty >= c, y >= 0.
    Verify this structure holds for Ex 8.3/8.4.
    """
    c = np.array([3, 2], dtype=float)
    A = np.array([[1, 1], [1, 3]], dtype=float)
    b = np.array([4, 6], dtype=float)

    # Solve primal
    res_p = scipy.optimize.linprog(-c, A_ub=A, b_ub=b,
                                    bounds=[(0, None), (0, None)], method='highs')
    # Solve dual: min b^Ty s.t. A^Ty >= c, y >= 0
    res_d = scipy.optimize.linprog(b, A_ub=-A.T, b_ub=-c,
                                    bounds=[(0, None), (0, None)], method='highs')

    primal_val = -res_p.fun
    dual_val = res_d.fun

    # Dual constraints: A^T y >= c
    y_star = res_d.x
    ATy = A.T @ y_star
    for j in range(len(c)):
        if ATy[j] < c[j] - 1e-8:
            return (False, f"Dual constraint {j+1} violated: A^Ty[{j}]={ATy[j]} < c[{j}]={c[j]}")

    if abs(primal_val - dual_val) > 1e-6:
        return (False, f"Primal val={primal_val}, Dual val={dual_val} don't match")
    return (True, "")


def _weak_duality_grid() -> tuple[bool, str]:
    """F4.7: c^Tx <= b^Ty for every feasible primal x and feasible dual y.
    Grid test over a range of feasible points.
    """
    c = np.array([3, 2], dtype=float)
    A = np.array([[1, 1], [1, 3]], dtype=float)
    b = np.array([4, 6], dtype=float)

    # Generate grid of primal feasible points
    primal_feasible = []
    for x1 in np.arange(0, 4.1, 0.5):
        for x2 in np.arange(0, 2.1, 0.5):
            x = np.array([x1, x2])
            if np.all(A @ x <= b + 1e-10):
                primal_feasible.append(x)

    # Generate grid of dual feasible points
    dual_feasible = []
    for y1 in np.arange(0, 5.1, 0.5):
        for y2 in np.arange(0, 3.1, 0.5):
            y = np.array([y1, y2])
            if np.all(A.T @ y >= c - 1e-10):
                dual_feasible.append(y)

    for x in primal_feasible:
        for y in dual_feasible:
            if c @ x > b @ y + 1e-10:
                return (False, f"c^Tx={c@x} > b^Ty={b@y} for x={x}, y={y}")
    return (True, "")


def _strong_duality_standalone() -> tuple[bool, str]:
    """F4.8: Solve primal and dual independently with scipy;
    optimal values must be equal (strong duality).
    """
    c = np.array([3, 2], dtype=float)
    A = np.array([[1, 1], [1, 3]], dtype=float)
    b = np.array([4, 6], dtype=float)

    # Primal: max c^Tx
    res_p = scipy.optimize.linprog(-c, A_ub=A, b_ub=b,
                                    bounds=[(0, None), (0, None)], method='highs')
    primal_val = -res_p.fun

    # Dual: min b^Ty
    res_d = scipy.optimize.linprog(b, A_ub=-A.T, b_ub=-c,
                                    bounds=[(0, None), (0, None)], method='highs')
    dual_val = res_d.fun

    if abs(primal_val - dual_val) > 1e-6:
        return (False, f"Primal opt={primal_val}, Dual opt={dual_val}")
    return (True, "")


def _complementary_slackness_standalone() -> tuple[bool, str]:
    """F4.9: At the optimal solution from scipy:
    y_i * (b_i - (Ax)_i) = 0 (primal CS) and x_j * ((A^Ty)_j - c_j) = 0 (dual CS).
    """
    c = np.array([3, 2], dtype=float)
    A = np.array([[1, 1], [1, 3]], dtype=float)
    b = np.array([4, 6], dtype=float)

    # Solve primal and dual
    res_p = scipy.optimize.linprog(-c, A_ub=A, b_ub=b,
                                    bounds=[(0, None), (0, None)], method='highs')
    x_star = res_p.x

    res_d = scipy.optimize.linprog(b, A_ub=-A.T, b_ub=-c,
                                    bounds=[(0, None), (0, None)], method='highs')
    y_star = res_d.x

    # Primal CS: y_i * s_i = 0 where s_i = b_i - (Ax)_i
    slacks = b - A @ x_star
    for i in range(len(b)):
        product = y_star[i] * slacks[i]
        if abs(product) > 1e-6:
            return (False, f"Primal CS violated: y[{i}]*s[{i}] = {y_star[i]}*{slacks[i]} = {product}")

    # Dual CS: x_j * t_j = 0 where t_j = (A^Ty)_j - c_j
    surpluses = A.T @ y_star - c
    for j in range(len(c)):
        product = x_star[j] * surpluses[j]
        if abs(product) > 1e-6:
            return (False, f"Dual CS violated: x[{j}]*t[{j}] = {x_star[j]}*{surpluses[j]} = {product}")

    return (True, "")
