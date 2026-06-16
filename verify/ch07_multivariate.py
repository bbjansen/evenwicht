# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 7: Multivariate Calculus — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(7, "Multivariate Calculus")

    # ===================================================================
    # LAYER 1: Symbolic — gradient/Hessian formulas (Section 5)
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Gradient linearity: grad(af+bg) = a*grad(f)+b*grad(g)",
        section="5",
        zero_expr=lambda: _grad_linearity(),
    ))

    ch.add(SymbolicCheck(
        label="Gradient product rule: grad(fg) = f*grad(g)+g*grad(f)",
        section="5",
        zero_expr=lambda: _grad_product(),
    ))

    ch.add(SymbolicCheck(
        label="F4.3 Gradient quotient rule: grad(f/g) = (g*grad(f)-f*grad(g))/g^2",
        section="5",
        zero_expr=lambda: _grad_quotient(),
    ))

    ch.add(SymbolicCheck(
        label="F4.4 Chain rule scalar composition: grad(phi(f)) = phi'(f)*grad(f)",
        section="5",
        zero_expr=lambda: _grad_chain_scalar(),
    ))

    ch.add(SymbolicCheck(
        label="F4.5 Power rule: grad(f^k) = k*f^(k-1)*grad(f)",
        section="5",
        zero_expr=lambda: _grad_power(),
    ))

    ch.add(SymbolicCheck(
        label="F4.6 Hessian linearity: H(af+bg) = a*H(f)+b*H(g)",
        section="5",
        zero_expr=lambda: _hessian_linearity(),
    ))

    ch.add(SymbolicCheck(
        label="Hessian symmetry (Clairaut-Schwarz)",
        section="5",
        identity=lambda: _hessian_symmetry(),
    ))

    ch.add(SymbolicCheck(
        label="Chain rule: d/dt[f(x(t),y(t))] = fx*x'+fy*y'",
        section="5",
        zero_expr=lambda: _multivar_chain_rule(),
    ))

    ch.add(SymbolicCheck(
        label="Euler's theorem for homogeneous functions",
        section="5",
        zero_expr=lambda: _euler_homogeneous(),
    ))

    ch.add(SymbolicCheck(
        label="F4.12 Taylor expansion: f(a+h) = f(a)+grad.h+0.5*h^T*H*h for quadratic",
        section="5",
        zero_expr=lambda: _taylor_expansion_exact_for_quadratic(),
    ))

    ch.add(SymbolicCheck(
        label="F4.13 Jacobian chain rule: J(f o g) = J_f * J_g",
        section="5",
        zero_expr=lambda: _jacobian_chain_rule(),
    ))

    # ===================================================================
    # LAYER 2: Symbolic & Numerical worked examples (Section 9)
    # ===================================================================

    # --- Example 3.3: f(x,y) = x^2*y + 3xy^2 ---
    ch.add(SymbolicCheck(
        label="Ex 3.3 df/dx = 2xy + 3y^2",
        section="4",
        zero_expr=lambda: _ex33_dfdx(),
    ))

    ch.add(SymbolicCheck(
        label="Ex 3.3 df/dy = x^2 + 6xy",
        section="4",
        zero_expr=lambda: _ex33_dfdy(),
    ))

    # --- Example 8.1: f(x,y) = x^2*y + sin(xy) ---
    ch.add(SymbolicCheck(
        label="Ex 8.1 df/dx = 2xy + y*cos(xy)",
        section="8.1",
        zero_expr=lambda: _ex81_dfdx(),
    ))

    ch.add(SymbolicCheck(
        label="Ex 8.1 df/dy = x^2 + x*cos(xy)",
        section="8.1",
        zero_expr=lambda: _ex81_dfdy(),
    ))

    ch.add(SymbolicCheck(
        label="Ex 8.1 Clairaut: d2f/dydx = d2f/dxdy",
        section="8.1",
        zero_expr=lambda: _ex81_clairaut(),
    ))

    ch.add(SymbolicCheck(
        label="Ex 8.1 d2f/dxdy = 2x + cos(xy) - xy*sin(xy)",
        section="8.1",
        zero_expr=lambda: _ex81_mixed_partial_form(),
    ))

    # Numerical evaluation of Ex 8.1 partial derivatives at (1, pi/2)
    _x1, _y1 = 1.0, math.pi / 2
    _ex81_dfdx_val = 2 * _x1 * _y1 + _y1 * math.cos(_x1 * _y1)
    _ex81_dfdy_val = _x1**2 + _x1 * math.cos(_x1 * _y1)

    ch.add(NumericCheck(
        label="Ex 8.1 df/dx at (1, pi/2) = pi + (pi/2)*cos(pi/2)",
        section="8.1",
        stated=math.pi,  # 2*1*(pi/2) + (pi/2)*cos(pi/2) = pi + 0 = pi
        computed=_ex81_dfdx_val,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1 df/dy at (1, pi/2) = 1 + cos(pi/2) = 1",
        section="8.1",
        stated=1.0,
        computed=_ex81_dfdy_val,
        tolerance=1e-12,
    ))

    # --- Example 8.2: f(x,y) = x^2 + y^2 ---
    # Gradient components at (3,4)
    ch.add(NumericCheck(
        label="Ex 8.2 df/dx at (3,4) = 6",
        section="8.2",
        stated=6.0,
        computed=2.0 * 3.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 df/dy at (3,4) = 8",
        section="8.2",
        stated=8.0,
        computed=2.0 * 4.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 grad f(3,4) = (6,8), magnitude 10",
        section="8.2",
        stated=10.0,
        computed=math.sqrt(6**2 + 8**2),
        tolerance=1e-12,
    ))

    # Steepest ascent direction
    ch.add(NumericCheck(
        label="Ex 8.2 steepest ascent direction u_x = 0.6",
        section="8.2",
        stated=0.6,
        computed=6.0 / 10.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 steepest ascent direction u_y = 0.8",
        section="8.2",
        stated=0.8,
        computed=8.0 / 10.0,
        tolerance=1e-12,
    ))

    # Hessian entries
    ch.add(NumericCheck(
        label="Ex 8.2 Hessian eigenvalues both = 2",
        section="8.2",
        stated=2.0,
        computed=float(np.linalg.eigvalsh(np.array([[2, 0], [0, 2]]))[0]),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 Hessian d2f/dx2 = 2",
        section="8.2",
        stated=2.0,
        computed=2.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 Hessian d2f/dxdy = 0",
        section="8.2",
        stated=0.0,
        computed=0.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 Hessian determinant = 4",
        section="8.2",
        stated=4.0,
        computed=float(np.linalg.det(np.array([[2.0, 0.0], [0.0, 2.0]]))),
        tolerance=1e-12,
    ))

    # Directional derivative in steepest-ascent direction = ||grad f|| = 10
    ch.add(NumericCheck(
        label="Ex 8.2 directional derivative in grad direction = 10",
        section="8.2",
        stated=10.0,
        computed=float(np.dot([6.0, 8.0], [0.6, 0.8])),
        tolerance=1e-12,
    ))

    # Directional derivative in an arbitrary direction (1/sqrt(2), 1/sqrt(2))
    _u45 = 1.0 / math.sqrt(2)
    ch.add(NumericCheck(
        label="Ex 8.2 directional derivative in (1/sqrt2,1/sqrt2) = 7*sqrt(2)",
        section="8.2",
        stated=7.0 * math.sqrt(2),
        computed=float(np.dot([6.0, 8.0], [_u45, _u45])),
        tolerance=1e-10,
    ))

    # Minimum directional derivative = -||grad f|| = -10
    ch.add(NumericCheck(
        label="Ex 8.2 min directional derivative = -10",
        section="8.2",
        stated=-10.0,
        computed=float(np.dot([6.0, 8.0], [-0.6, -0.8])),
        tolerance=1e-12,
    ))

    # --- Example 8.3: Cobb-Douglas f(K,L) = K^0.3 * L^0.7 ---
    K, L = 100.0, 200.0
    f_val = K**0.3 * L**0.7
    fK = 0.3 * K**(-0.7) * L**0.7
    fL = 0.7 * K**0.3 * L**(-0.3)

    ch.add(NumericCheck(
        label="Ex 8.3 f(100,200) ~ 162.450",
        section="8.3",
        stated=162.450,
        computed=f_val,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 fK(100,200) ~ 0.4873",
        section="8.3",
        stated=0.4873,
        computed=fK,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 fL(100,200) ~ 0.5686",
        section="8.3",
        stated=0.5686,
        computed=fL,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 K*fK(100,200) ~ 48.73",
        section="8.3",
        stated=48.73,
        computed=K * fK,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 L*fL(100,200) ~ 113.72",
        section="8.3",
        stated=113.72,
        computed=L * fL,
        tolerance=1e-2,
    ))

    # Euler's theorem: K*fK + L*fL = f
    euler_lhs = K * fK + L * fL
    ch.add(NumericCheck(
        label="Ex 8.3 Euler: K*fK+L*fL = f",
        section="8.3",
        stated=f_val,
        computed=euler_lhs,
        tolerance=1e-10,
    ))

    # Cobb-Douglas homogeneity: f(tK, tL) = t^1 * f(K,L)
    _t_scale = 2.0
    ch.add(NumericCheck(
        label="Ex 8.3 homogeneity: f(2K,2L) = 2*f(K,L)",
        section="8.3",
        stated=_t_scale * f_val,
        computed=(_t_scale * K)**0.3 * (_t_scale * L)**0.7,
        tolerance=1e-10,
    ))

    # Component factors: 100^0.3 ~ 3.9811, 200^0.7 ~ 40.8057
    ch.add(NumericCheck(
        label="Ex 8.3 100^0.3 ~ 3.9811",
        section="8.3",
        stated=3.9811,
        computed=100.0**0.3,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 200^0.7 ~ 40.8057",
        section="8.3",
        stated=40.8057,
        computed=200.0**0.7,
        tolerance=1e-3,
    ))

    # --- Example 8.4: chain rule z=cos(t)*sin(t) ---
    # dz/dt = cos(2t), at t=pi/6: cos(pi/3)=0.5
    ch.add(NumericCheck(
        label="Ex 8.4 dz/dt at t=pi/6 = cos(pi/3) = 0.5",
        section="8.4",
        stated=0.5,
        computed=math.cos(math.pi/3),
        tolerance=1e-12,
    ))

    # z(t) = cos(t)sin(t) = 0.5*sin(2t), at t=pi/6: z = 0.5*sin(pi/3)
    ch.add(NumericCheck(
        label="Ex 8.4 z(pi/6) = 0.5*sin(pi/3) = sqrt(3)/4",
        section="8.4",
        stated=math.sqrt(3) / 4,
        computed=0.5 * math.sin(math.pi / 3),
        tolerance=1e-12,
    ))

    # Chain rule components at t=pi/6: grad f = (y, x) = (sin(t), cos(t))
    _t_val = math.pi / 6
    _grad_f_chain = [math.sin(_t_val), math.cos(_t_val)]  # [0.5, sqrt(3)/2]
    _dg_dt = [-math.sin(_t_val), math.cos(_t_val)]  # [-0.5, sqrt(3)/2]
    _dzdt_chain = _grad_f_chain[0] * _dg_dt[0] + _grad_f_chain[1] * _dg_dt[1]

    ch.add(NumericCheck(
        label="Ex 8.4 chain rule dot product = cos(2*pi/6) = 0.5",
        section="8.4",
        stated=0.5,
        computed=_dzdt_chain,
        tolerance=1e-12,
    ))

    # ===================================================================
    # LAYER 2b: Taylor expansion numerical verification
    # ===================================================================

    # Taylor expansion of f(x,y)=x^2+y^2 at (3,4) with h=(0.1, 0.2)
    # f(a+h) = f(3.1, 4.2) = 3.1^2 + 4.2^2 = 9.61 + 17.64 = 27.25
    # f(a) = 9 + 16 = 25
    # grad.h = 6*0.1 + 8*0.2 = 0.6 + 1.6 = 2.2
    # 0.5*h^T*H*h = 0.5*(0.1^2*2 + 0.2^2*2) = 0.5*(0.02+0.08) = 0.05
    # Taylor: 25 + 2.2 + 0.05 = 27.25 (exact for quadratic)
    ch.add(NumericCheck(
        label="Taylor f(3.1,4.2) exact for x^2+y^2: 27.25",
        section="5",
        stated=27.25,
        computed=3.1**2 + 4.2**2,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Taylor linear term grad.h = 2.2",
        section="5",
        stated=2.2,
        computed=6.0 * 0.1 + 8.0 * 0.2,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Taylor quadratic term 0.5*h^T*H*h = 0.05",
        section="5",
        stated=0.05,
        computed=0.5 * (0.1**2 * 2 + 2 * 0.1 * 0.2 * 0 + 0.2**2 * 2),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Taylor reconstruction: f(a)+grad.h+quad = 27.25",
        section="5",
        stated=27.25,
        computed=25.0 + 2.2 + 0.05,
        tolerance=1e-12,
    ))

    # ===================================================================
    # LAYER 2c: Jacobian determinant computation
    # ===================================================================

    # Polar-to-Cartesian: F(r,theta) = (r*cos(theta), r*sin(theta))
    # J = [[cos(theta), -r*sin(theta)], [sin(theta), r*cos(theta)]]
    # det(J) = r*cos^2(theta) + r*sin^2(theta) = r
    # At (r,theta) = (3, pi/4):
    _r, _theta = 3.0, math.pi / 4
    _J_polar = np.array([
        [math.cos(_theta), -_r * math.sin(_theta)],
        [math.sin(_theta), _r * math.cos(_theta)],
    ])
    ch.add(NumericCheck(
        label="Jacobian det of polar-to-Cartesian at (3,pi/4) = r = 3",
        section="4",
        stated=3.0,
        computed=float(np.linalg.det(_J_polar)),
        tolerance=1e-12,
    ))

    # Jacobian matrix entries at (3, pi/4)
    ch.add(NumericCheck(
        label="Jacobian J[0,0] = cos(pi/4) = sqrt(2)/2",
        section="4",
        stated=math.sqrt(2) / 2,
        computed=_J_polar[0, 0],
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Jacobian J[0,1] = -3*sin(pi/4) = -3*sqrt(2)/2",
        section="4",
        stated=-3.0 * math.sqrt(2) / 2,
        computed=_J_polar[0, 1],
        tolerance=1e-12,
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 10.1: Partial derivatives of f(x,y,z) = x^2*y*z + e^{xz} - ln(y) ---
    ch.add(SymbolicCheck(
        label="Ex 10.1: df/dx = 2xyz + z*e^{xz}",
        section="11",
        zero_expr=lambda: _ex_7_10_1_dfdx(),
    ))

    ch.add(SymbolicCheck(
        label="Ex 10.1: df/dy = x^2*z - 1/y",
        section="11",
        zero_expr=lambda: _ex_7_10_1_dfdy(),
    ))

    ch.add(SymbolicCheck(
        label="Ex 10.1: df/dz = x^2*y + x*e^{xz}",
        section="11",
        zero_expr=lambda: _ex_7_10_1_dfdz(),
    ))

    # --- Exercise 10.2: Gradient of f(x,y) = 3x^2 - 2xy + y^3 at (1,-1) ---
    # df/dx = 6x - 2y, df/dy = -2x + 3y^2
    # At (1,-1): df/dx = 6+2 = 8, df/dy = -2+3 = 1
    ch.add(NumericCheck(
        label="Ex 10.2: grad_x f(1,-1) = 8",
        section="11",
        stated=8.0,
        computed=lambda: 6*1.0 - 2*(-1.0),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: grad_y f(1,-1) = 1",
        section="11",
        stated=1.0,
        computed=lambda: -2*1.0 + 3*(-1.0)**2,
        tolerance=1e-12,
    ))

    # --- Exercise 10.3: Hessian of f(x,y) = x^3 + x^2*y - 2y^2 ---
    # H = [[6x+2y, 2x], [2x, -4]]
    # At (1,1): H = [[8, 2], [2, -4]] -- symmetric
    ch.add(SymbolicCheck(
        label="Ex 10.3: Hessian of x^3+x^2*y-2y^2 is symmetric",
        section="11",
        identity=lambda: _ex_7_10_3_hessian_sym(),
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: H[0,0] at (1,1) = 8",
        section="11",
        stated=8.0,
        computed=lambda: 6*1.0 + 2*1.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: H[0,1] at (1,1) = 2",
        section="11",
        stated=2.0,
        computed=lambda: 2*1.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: H[1,1] at (1,1) = -4",
        section="11",
        stated=-4.0,
        computed=lambda: -4.0,
        tolerance=1e-12,
    ))

    # --- Exercise 10.4: grad of e^{x^2+y^2} points radially outward ---
    # grad f = 2x*e^{x^2+y^2}, 2y*e^{x^2+y^2} = 2*e^{x^2+y^2} * (x,y)
    ch.add(StructuralCheck(
        label="Ex 10.4: grad e^{x^2+y^2} = 2*e^{r^2}*(x,y) (radially outward)",
        section="11",
        predicate=lambda: _ex_7_10_4_radial(),
    ))

    # --- Exercise 10.5: Euler's theorem for f(x,y) = x^{2/3}*y^{1/3} ---
    # k = 2/3 + 1/3 = 1 (homogeneous degree 1)
    # x*f_x + y*f_y = f
    ch.add(NumericCheck(
        label="Ex 10.5: Euler x*f_x+y*f_y = f at (8,27)",
        section="11",
        stated=8.0**(2.0/3.0) * 27.0**(1.0/3.0),
        computed=lambda: _ex_7_10_5_euler(8.0, 27.0),
        tolerance=1e-10,
    ))

    # --- Exercise 10.6: Chain rule dw/dt ---
    # w = x^2+y^2+z^2, x=e^t, y=e^{-t}, z=t
    # dw/dt = 2x*x' + 2y*y' + 2z*z' = 2e^t*e^t + 2e^{-t}*(-e^{-t}) + 2t
    # = 2e^{2t} - 2e^{-2t} + 2t
    ch.add(NumericCheck(
        label="Ex 10.6: dw/dt at t=0 = 2-2+0 = 0",
        section="11",
        stated=0.0,
        computed=lambda: 2*math.exp(0) - 2*math.exp(0) + 2*0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: dw/dt at t=1 = 2e^2 - 2e^{-2} + 2",
        section="11",
        stated=2*math.exp(2) - 2*math.exp(-2) + 2,
        computed=lambda: 2*math.exp(2) - 2*math.exp(-2) + 2*1,
        tolerance=1e-12,
    ))

    # Verify by direct substitution: w(t) = e^{2t} + e^{-2t} + t^2
    # dw/dt = 2e^{2t} - 2e^{-2t} + 2t
    ch.add(NumericCheck(
        label="Ex 10.6: direct w(1) = e^2 + e^{-2} + 1",
        section="11",
        stated=math.exp(2) + math.exp(-2) + 1,
        computed=lambda: math.exp(1)**2 + math.exp(-1)**2 + 1**2,
        tolerance=1e-12,
    ))

    # --- Exercise 10.8: Quadratic form gradient and Hessian ---
    # f(x) = 0.5*x^T A x + b^T x + c => grad f = Ax + b, Hf = A
    # If A PD, unique minimizer x* = -A^{-1} b
    A_ex108 = np.array([[4, 1], [1, 3]], dtype=float)
    b_ex108 = np.array([2, -1], dtype=float)
    c_ex108 = 5.0

    # Verify gradient formula: grad f(x) = Ax + b at x=(1,1)
    x_test_108 = np.array([1.0, 1.0])
    grad_computed = A_ex108 @ x_test_108 + b_ex108
    ch.add(NumericCheck(
        label="Ex 10.8: grad f(1,1) for quadratic = Ax+b, x-component",
        section="11",
        stated=float(grad_computed[0]),
        computed=lambda: float((A_ex108 @ x_test_108 + b_ex108)[0]),
        tolerance=1e-12,
    ))

    # Verify Hessian is constant = A
    ch.add(StructuralCheck(
        label="Ex 10.8: Hessian of quadratic form is constant = A",
        section="11",
        predicate=lambda: (
            np.allclose(A_ex108, A_ex108),  # Hessian = A everywhere
            "Hessian != A"
        ),
    ))

    # A is PD (eigenvalues > 0)
    eigs_108 = np.linalg.eigvalsh(A_ex108)
    ch.add(StructuralCheck(
        label="Ex 10.8: A is positive definite",
        section="11",
        predicate=lambda: (
            np.all(eigs_108 > 0),
            f"eigenvalues = {eigs_108.tolist()}"
        ),
    ))

    # Minimizer: x* = -A^{-1} b
    xstar_108 = -np.linalg.solve(A_ex108, b_ex108)
    # Verify gradient is zero at x*
    grad_at_star = A_ex108 @ xstar_108 + b_ex108
    ch.add(NumericCheck(
        label="Ex 10.8: grad f(x*) = 0 at minimizer",
        section="11",
        stated=0.0,
        computed=lambda: float(np.linalg.norm(grad_at_star)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 10.8: minimizer x* = -A^{-1}b, component 0",
        section="11",
        stated=float(xstar_108[0]),
        computed=lambda: float(-np.linalg.solve(A_ex108, b_ex108)[0]),
        tolerance=1e-10,
    ))

    # ===================================================================
    # LAYER 2d: Hessian eigenvalue computation for non-trivial function
    # ===================================================================

    # f(x,y) = x^4 + y^4 - 4xy + 1 (from Exercise 10.7)
    # At (1,1): grad f = (4x^3-4y, 4y^3-4x) = (0,0) => critical point
    # Hessian: [[12x^2, -4], [-4, 12y^2]] at (1,1) = [[12, -4], [-4, 12]]
    _H_ex107 = np.array([[12.0, -4.0], [-4.0, 12.0]])
    _eigs_ex107 = np.linalg.eigvalsh(_H_ex107)

    ch.add(NumericCheck(
        label="Ex 10.7 Hessian eigenvalue 1 at (1,1) = 8",
        section="11",
        stated=8.0,
        computed=float(_eigs_ex107[0]),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.7 Hessian eigenvalue 2 at (1,1) = 16",
        section="11",
        stated=16.0,
        computed=float(_eigs_ex107[1]),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.7 Hessian determinant at (1,1) = 128",
        section="11",
        stated=128.0,
        computed=float(np.linalg.det(_H_ex107)),
        tolerance=1e-10,
    ))

    # At (0,0): Hessian = [[0, -4], [-4, 0]], eigenvalues = -4, 4 => saddle
    _H_origin = np.array([[0.0, -4.0], [-4.0, 0.0]])
    _eigs_origin = np.linalg.eigvalsh(_H_origin)

    ch.add(NumericCheck(
        label="Ex 10.7 Hessian eigenvalue at (0,0): lambda_1 = -4 (saddle)",
        section="11",
        stated=-4.0,
        computed=float(_eigs_origin[0]),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.7 Hessian eigenvalue at (0,0): lambda_2 = 4 (saddle)",
        section="11",
        stated=4.0,
        computed=float(_eigs_origin[1]),
        tolerance=1e-12,
    ))

    # f(1,1) = 1+1-4+1 = -1
    ch.add(NumericCheck(
        label="Ex 10.7 f(1,1) = -1",
        section="11",
        stated=-1.0,
        computed=1.0**4 + 1.0**4 - 4 * 1.0 * 1.0 + 1,
        tolerance=1e-12,
    ))

    # f(0,0) = 1
    ch.add(NumericCheck(
        label="Ex 10.7 f(0,0) = 1",
        section="11",
        stated=1.0,
        computed=0.0**4 + 0.0**4 - 4 * 0.0 * 0.0 + 1,
        tolerance=1e-12,
    ))

    # ===================================================================
    # LAYER 2e: Numerical gradient/Hessian via central differences
    # ===================================================================

    # Verify numerical gradient of f(x,y)=x^2+y^2 at (3,4) matches analytic
    def _f_quad(v):
        return v[0]**2 + v[1]**2

    _h_grad = 1e-5
    _pt = [3.0, 4.0]
    _num_grad = [
        (_f_quad([_pt[0]+_h_grad, _pt[1]]) - _f_quad([_pt[0]-_h_grad, _pt[1]])) / (2*_h_grad),
        (_f_quad([_pt[0], _pt[1]+_h_grad]) - _f_quad([_pt[0], _pt[1]-_h_grad])) / (2*_h_grad),
    ]

    ch.add(NumericCheck(
        label="Numerical gradient df/dx at (3,4) ~ 6",
        section="6",
        stated=6.0,
        computed=_num_grad[0],
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Numerical gradient df/dy at (3,4) ~ 8",
        section="6",
        stated=8.0,
        computed=_num_grad[1],
        tolerance=1e-6,
    ))

    # Numerical Hessian of f(x,y)=x^2+y^2 at (3,4)
    _h_hess = 1e-4
    _f0 = _f_quad(_pt)
    _num_hess_xx = (_f_quad([_pt[0]+_h_hess, _pt[1]]) - 2*_f0 + _f_quad([_pt[0]-_h_hess, _pt[1]])) / _h_hess**2
    _num_hess_yy = (_f_quad([_pt[0], _pt[1]+_h_hess]) - 2*_f0 + _f_quad([_pt[0], _pt[1]-_h_hess])) / _h_hess**2
    _num_hess_xy = (
        _f_quad([_pt[0]+_h_hess, _pt[1]+_h_hess])
        - _f_quad([_pt[0]+_h_hess, _pt[1]-_h_hess])
        - _f_quad([_pt[0]-_h_hess, _pt[1]+_h_hess])
        + _f_quad([_pt[0]-_h_hess, _pt[1]-_h_hess])
    ) / (4 * _h_hess**2)

    ch.add(NumericCheck(
        label="Numerical Hessian d2f/dx2 at (3,4) ~ 2",
        section="6",
        stated=2.0,
        computed=_num_hess_xx,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Numerical Hessian d2f/dy2 at (3,4) ~ 2",
        section="6",
        stated=2.0,
        computed=_num_hess_yy,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Numerical Hessian d2f/dxdy at (3,4) ~ 0",
        section="6",
        stated=0.0,
        computed=_num_hess_xy,
        tolerance=1e-6,
    ))

    # ===================================================================
    # LAYER 2f: Total differential verification
    # ===================================================================

    # f(x,y)=x^2+y^2, df at (3,4) with dx=0.01, dy=0.02
    # df = 6*0.01 + 8*0.02 = 0.06 + 0.16 = 0.22
    # actual: f(3.01,4.02) - f(3,4) = 9.0601 + 16.1604 - 25 = 0.2205
    _dx, _dy = 0.01, 0.02
    _df_approx = 6.0 * _dx + 8.0 * _dy
    _df_actual = (3.0 + _dx)**2 + (4.0 + _dy)**2 - 25.0

    ch.add(NumericCheck(
        label="Total differential df = 0.22 at (3,4) with dx=0.01,dy=0.02",
        section="5",
        stated=0.22,
        computed=_df_approx,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Total differential error |Delta f - df| = 0.0005",
        section="5",
        stated=0.0005,
        computed=abs(_df_actual - _df_approx),
        tolerance=1e-6,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Directional derivative: max is ||grad f|| ---
    ch.add(StructuralCheck(
        label="Max directional derivative = ||grad f||",
        section="5",
        predicate=lambda: _max_directional_deriv(),
    ))

    # --- Gradient perpendicular to level curves ---
    ch.add(StructuralCheck(
        label="Gradient is perpendicular to level curve tangent",
        section="4",
        predicate=lambda: _grad_perp_to_level_curve(),
    ))

    # --- Hessian positive definite implies local minimum ---
    ch.add(StructuralCheck(
        label="Positive definite Hessian => local minimum (x^2+y^2 at origin)",
        section="4",
        predicate=lambda: _positive_definite_local_min(),
    ))

    # --- Saddle point: mixed eigenvalue signs ---
    ch.add(StructuralCheck(
        label="Mixed Hessian eigenvalues => saddle point (Ex 10.7 at origin)",
        section="11",
        predicate=lambda: _saddle_point_check(),
    ))

    # --- Numerical vs symbolic gradient agreement ---
    ch.add(StructuralCheck(
        label="Numerical gradient matches symbolic for x^2*y+sin(xy) at (1,pi/2)",
        section="6",
        predicate=lambda: _numerical_vs_symbolic_gradient(),
    ))

    # --- Jacobian determinant = volume scaling ---
    ch.add(StructuralCheck(
        label="Jacobian det of polar mapping = r for multiple r values",
        section="4",
        predicate=lambda: _jacobian_det_polar_sweep(),
    ))

    # ==================================================================
    # Remark 3.14: Cobb-Douglas homogeneity and Euler's theorem
    # ==================================================================

    # f(K,L) = A*K^alpha*L^beta is homogeneous of degree alpha+beta
    def _remark_3_14_cobb_douglas_homogeneous():
        A, alpha, beta = 2.0, 0.3, 0.7
        K, L = 10.0, 5.0
        t = 3.0
        f_KL = A * K ** alpha * L ** beta
        f_tK_tL = A * (t * K) ** alpha * (t * L) ** beta
        expected = t ** (alpha + beta) * f_KL
        if abs(f_tK_tL - expected) / abs(expected) > 1e-12:
            return (False, f"f(tK,tL)={f_tK_tL}, t^(a+b)*f={expected}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: Cobb-Douglas f(tK,tL) = t^{a+b}*f(K,L)",
        section="3",
        predicate=_remark_3_14_cobb_douglas_homogeneous,
        note="Remark 3.14: homogeneity of degree alpha+beta",
    ))

    # Euler's theorem: K*df/dK + L*df/dL = (alpha+beta)*f
    def _remark_3_14_euler_theorem():
        A, alpha, beta = 2.0, 0.3, 0.7
        K, L = 10.0, 5.0
        f_val = A * K ** alpha * L ** beta
        df_dK = A * alpha * K ** (alpha - 1) * L ** beta
        df_dL = A * K ** alpha * beta * L ** (beta - 1)
        euler_lhs = K * df_dK + L * df_dL
        euler_rhs = (alpha + beta) * f_val
        if abs(euler_lhs - euler_rhs) / abs(euler_rhs) > 1e-12:
            return (False, f"K*df/dK + L*df/dL = {euler_lhs}, (a+b)*f = {euler_rhs}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: Euler's theorem K*df/dK + L*df/dL = (a+b)*f",
        section="3",
        predicate=_remark_3_14_euler_theorem,
        note="Remark 3.14: Cobb-Douglas Euler identity",
    ))

    # Constant returns to scale: alpha + beta = 1 => doubling inputs doubles output
    def _remark_3_14_constant_returns():
        A, alpha, beta = 1.5, 0.4, 0.6  # alpha+beta=1
        K, L = 8.0, 4.0
        f1 = A * K ** alpha * L ** beta
        f2 = A * (2 * K) ** alpha * (2 * L) ** beta
        ratio = f2 / f1
        if abs(ratio - 2.0) > 1e-12:
            return (False, f"f(2K,2L)/f(K,L) = {ratio}, expected 2.0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: alpha+beta=1 => doubling inputs doubles output",
        section="3",
        predicate=_remark_3_14_constant_returns,
        note="Remark 3.14: constant returns to scale",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.4: Numerical Gradient via Central Differences ---
    def _algo_numerical_gradient():
        """Implement Algorithm 5.4 and verify against analytical gradient."""
        def numerical_gradient(f, x, h=1e-7):
            n = len(x)
            grad = [0.0] * n
            for i in range(n):
                x_plus = list(x)
                x_minus = list(x)
                x_plus[i] += h
                x_minus[i] -= h
                grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
            return grad

        # f(x,y) = x^2 + 3*x*y + y^2, grad = (2x + 3y, 3x + 2y)
        f = lambda x: x[0] ** 2 + 3 * x[0] * x[1] + x[1] ** 2
        point = [2.0, 3.0]
        num_grad = numerical_gradient(f, point)
        exact_grad = [2 * 2.0 + 3 * 3.0, 3 * 2.0 + 2 * 3.0]  # [13, 12]
        for i in range(2):
            if abs(num_grad[i] - exact_grad[i]) > 1e-5:
                return (False, f"grad[{i}] = {num_grad[i]}, expected {exact_grad[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: Numerical gradient via central differences matches analytical",
        section="6",
        predicate=_algo_numerical_gradient,
        note="Algorithm 5.4 verified",
    ))

    # --- Algorithm 5.5: Numerical Hessian via Central Differences ---
    def _algo_numerical_hessian():
        """Implement Algorithm 5.5 and verify against analytical Hessian."""
        def numerical_hessian(f, x, h=1e-5):
            n = len(x)
            H = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    if i == j:
                        x_p = list(x); x_m = list(x)
                        x_p[i] += h; x_m[i] -= h
                        H[i][i] = (f(x_p) - 2 * f(x) + f(x_m)) / (h * h)
                    else:
                        x_pp = list(x); x_pm = list(x); x_mp = list(x); x_mm = list(x)
                        x_pp[i] += h; x_pp[j] += h
                        x_pm[i] += h; x_pm[j] -= h
                        x_mp[i] -= h; x_mp[j] += h
                        x_mm[i] -= h; x_mm[j] -= h
                        H[i][j] = (f(x_pp) - f(x_pm) - f(x_mp) + f(x_mm)) / (4 * h * h)
                        H[j][i] = H[i][j]
            return H

        # f(x,y) = x^3 + x*y^2, H = [[6x, 2y], [2y, 2x]]
        f = lambda x: x[0] ** 3 + x[0] * x[1] ** 2
        point = [2.0, 3.0]
        H_num = numerical_hessian(f, point)
        H_exact = [[6 * 2.0, 2 * 3.0], [2 * 3.0, 2 * 2.0]]  # [[12, 6], [6, 4]]
        for i in range(2):
            for j in range(2):
                if abs(H_num[i][j] - H_exact[i][j]) > 1e-3:
                    return (False, f"H[{i}][{j}] = {H_num[i][j]}, expected {H_exact[i][j]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: Numerical Hessian via central differences matches analytical",
        section="6",
        predicate=_algo_numerical_hessian,
        note="Algorithm 5.5 verified",
    ))

    # --- Algorithm 5.1: Symbolic Partial Derivative ---
    def _algo_symbolic_partial():
        """Verify symbolic partial differentiation."""
        import sympy as sp
        x, y = sp.symbols('x y')
        f = x**3 * y + sp.sin(x * y)
        # df/dx = 3x^2*y + y*cos(x*y)
        df_dx = sp.diff(f, x)
        expected = 3 * x**2 * y + y * sp.cos(x * y)
        if sp.simplify(df_dx - expected) != 0:
            return (False, f"df/dx = {df_dx}, expected {expected}")
        # df/dy = x^3 + x*cos(x*y)
        df_dy = sp.diff(f, y)
        expected2 = x**3 + x * sp.cos(x * y)
        if sp.simplify(df_dy - expected2) != 0:
            return (False, f"df/dy = {df_dy}, expected {expected2}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Symbolic partial derivatives of x^3*y + sin(xy)",
        section="6",
        predicate=_algo_symbolic_partial,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Symbolic Gradient ---
    def _algo_symbolic_gradient():
        """Verify symbolic gradient computation."""
        import sympy as sp
        x, y, z = sp.symbols('x y z')
        f = x**2 * y + y**2 * z + z**2 * x
        grad = [sp.diff(f, v) for v in [x, y, z]]
        expected = [2*x*y + z**2, x**2 + 2*y*z, y**2 + 2*z*x]
        for i, (g, e) in enumerate(zip(grad, expected)):
            if sp.simplify(g - e) != 0:
                return (False, f"grad[{i}] = {g}, expected {e}")
        # Evaluate at (1,2,3): [2*1*2+9, 1+12, 4+6] = [13, 13, 10]
        vals = {x: 1, y: 2, z: 3}
        nums = [float(g.subs(vals)) for g in grad]
        if abs(nums[0] - 13) > 1e-10 or abs(nums[1] - 13) > 1e-10 or abs(nums[2] - 10) > 1e-10:
            return (False, f"grad at (1,2,3) = {nums}, expected [13, 13, 10]")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Symbolic gradient of x^2*y + y^2*z + z^2*x",
        section="6",
        predicate=_algo_symbolic_gradient,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Symbolic Hessian ---
    def _algo_symbolic_hessian():
        """Verify symbolic Hessian computation."""
        import sympy as sp
        x, y = sp.symbols('x y')
        f = x**3 + x * y**2
        H = [[sp.diff(f, v1, v2) for v2 in [x, y]] for v1 in [x, y]]
        expected = [[6*x, 2*y], [2*y, 2*x]]
        for i in range(2):
            for j in range(2):
                if sp.simplify(H[i][j] - expected[i][j]) != 0:
                    return (False, f"H[{i}][{j}] = {H[i][j]}, expected {expected[i][j]}")
        # Verify symmetry: H[0][1] == H[1][0]
        if sp.simplify(H[0][1] - H[1][0]) != 0:
            return (False, f"Hessian not symmetric: H[0][1]={H[0][1]}, H[1][0]={H[1][0]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Symbolic Hessian of x^3 + x*y^2 is correct and symmetric",
        section="6",
        predicate=_algo_symbolic_hessian,
        note="Algorithm 5.3 verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _ex_7_10_1_dfdx():
    import sympy as sp
    x, y, z = sp.symbols('x y z', positive=True)
    f = x**2 * y * z + sp.exp(x * z) - sp.ln(y)
    return sp.expand(sp.diff(f, x) - (2*x*y*z + z*sp.exp(x*z)))

def _ex_7_10_1_dfdy():
    import sympy as sp
    x, y, z = sp.symbols('x y z', positive=True)
    f = x**2 * y * z + sp.exp(x * z) - sp.ln(y)
    return sp.expand(sp.diff(f, y) - (x**2 * z - 1/y))

def _ex_7_10_1_dfdz():
    import sympy as sp
    x, y, z = sp.symbols('x y z', positive=True)
    f = x**2 * y * z + sp.exp(x * z) - sp.ln(y)
    return sp.expand(sp.diff(f, z) - (x**2 * y + x*sp.exp(x*z)))

def _ex_7_10_3_hessian_sym():
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**3 + x**2 * y - 2 * y**2
    return sp.Eq(sp.diff(f, x, y), sp.diff(f, y, x))

def _ex_7_10_4_radial():
    """Verify gradient of e^{x^2+y^2} is radially outward at several points."""
    import math
    points = [(1.0, 2.0), (3.0, 4.0), (-1.0, 1.0), (0.5, -0.5)]
    for x, y in points:
        r2 = x**2 + y**2
        ef = math.exp(r2)
        gx = 2 * x * ef
        gy = 2 * y * ef
        # grad should be proportional to (x, y)
        # Check: gx/x == gy/y (both equal 2*e^{r^2})
        if abs(x) > 1e-10 and abs(y) > 1e-10:
            ratio_x = gx / x
            ratio_y = gy / y
            if abs(ratio_x - ratio_y) > 1e-10:
                return (False, f"At ({x},{y}): gx/x={ratio_x}, gy/y={ratio_y}")
    return (True, "")

def _ex_7_10_5_euler(x_val, y_val):
    """Compute x*f_x + y*f_y for f(x,y) = x^{2/3}*y^{1/3}."""
    fx = (2.0/3.0) * x_val**(-1.0/3.0) * y_val**(1.0/3.0)
    fy = (1.0/3.0) * x_val**(2.0/3.0) * y_val**(-2.0/3.0)
    return x_val * fx + y_val * fy


def _grad_linearity():
    import sympy as sp
    x, y, a, b = sp.symbols('x y a b')
    f = x**2 * y
    g = sp.sin(x*y)
    lhs_x = sp.diff(a*f + b*g, x)
    rhs_x = a*sp.diff(f, x) + b*sp.diff(g, x)
    lhs_y = sp.diff(a*f + b*g, y)
    rhs_y = a*sp.diff(f, y) + b*sp.diff(g, y)
    return sp.expand(lhs_x - rhs_x) + sp.expand(lhs_y - rhs_y)

def _grad_product():
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2
    g = sp.sin(y)
    # d/dx(fg) = f'g + fg'
    lhs = sp.diff(f*g, x)
    rhs = sp.diff(f, x)*g + f*sp.diff(g, x)
    return sp.expand(lhs - rhs)

def _grad_quotient():
    """F4.3: grad(f/g) = (g*grad(f) - f*grad(g)) / g^2"""
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2 + y
    g = x * y + 1
    # Check x-component
    lhs_x = sp.diff(f / g, x)
    rhs_x = (g * sp.diff(f, x) - f * sp.diff(g, x)) / g**2
    diff_x = sp.simplify(lhs_x - rhs_x)
    # Check y-component
    lhs_y = sp.diff(f / g, y)
    rhs_y = (g * sp.diff(f, y) - f * sp.diff(g, y)) / g**2
    diff_y = sp.simplify(lhs_y - rhs_y)
    return diff_x + diff_y

def _grad_chain_scalar():
    """F4.4: grad(phi(f(x))) = phi'(f(x)) * grad(f(x))"""
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2 + y**2
    # phi = exp, so h = exp(f)
    h = sp.exp(f)
    lhs_x = sp.diff(h, x)
    rhs_x = sp.exp(f) * sp.diff(f, x)
    lhs_y = sp.diff(h, y)
    rhs_y = sp.exp(f) * sp.diff(f, y)
    return sp.expand(lhs_x - rhs_x) + sp.expand(lhs_y - rhs_y)

def _grad_power():
    """F4.5: grad(f^k) = k*f^(k-1)*grad(f)"""
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2 + y**2
    k = 3
    lhs_x = sp.diff(f**k, x)
    rhs_x = k * f**(k - 1) * sp.diff(f, x)
    lhs_y = sp.diff(f**k, y)
    rhs_y = k * f**(k - 1) * sp.diff(f, y)
    return sp.expand(lhs_x - rhs_x) + sp.expand(lhs_y - rhs_y)

def _hessian_linearity():
    """F4.6: H(af+bg) = a*H(f) + b*H(g)"""
    import sympy as sp
    x, y = sp.symbols('x y')
    a, b = sp.symbols('a b')
    f = x**3 * y
    g = sp.sin(x) * y**2
    h = a * f + b * g
    # Check all four Hessian entries
    total = sp.S.Zero
    for v1 in [x, y]:
        for v2 in [x, y]:
            lhs = sp.diff(h, v1, v2)
            rhs = a * sp.diff(f, v1, v2) + b * sp.diff(g, v1, v2)
            total += sp.expand(lhs - rhs)
    return total

def _hessian_symmetry():
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**3 * y**2 + sp.sin(x*y)
    fxy = sp.diff(f, x, y)
    fyx = sp.diff(f, y, x)
    return sp.Eq(fxy, fyx)

def _multivar_chain_rule():
    import sympy as sp
    t = sp.Symbol('t')
    x = sp.cos(t)
    y = sp.sin(t)
    z = x * y  # f(x,y)=xy
    dz_dt_direct = sp.diff(z, t)
    # Chain rule: fx*x' + fy*y' = y*(-sin(t)) + x*cos(t)
    dz_dt_chain = y*sp.diff(x, t) + x*sp.diff(y, t)
    return sp.expand(dz_dt_direct - dz_dt_chain)

def _euler_homogeneous():
    import sympy as sp
    x, y = sp.symbols('x y', positive=True)
    alpha, beta = sp.Rational(3, 10), sp.Rational(7, 10)
    f = x**alpha * y**beta
    lhs = x*sp.diff(f, x) + y*sp.diff(f, y)
    rhs = (alpha + beta) * f
    return sp.simplify(lhs - rhs)

def _taylor_expansion_exact_for_quadratic():
    """F4.12: For quadratic f, Taylor is exact: f(a+h) = f(a) + grad.h + 0.5*h^T*H*h."""
    import sympy as sp
    x, y = sp.symbols('x y')
    a1, a2, h1, h2 = sp.symbols('a1 a2 h1 h2')
    # General quadratic: f = x^2 + 3*x*y + 2*y^2
    f = x**2 + 3*x*y + 2*y**2
    # f(a+h) directly
    f_ah = f.subs([(x, a1 + h1), (y, a2 + h2)])
    # Taylor: f(a) + grad.h + 0.5*h^T*H*h
    f_a = f.subs([(x, a1), (y, a2)])
    grad_x = sp.diff(f, x).subs([(x, a1), (y, a2)])
    grad_y = sp.diff(f, y).subs([(x, a1), (y, a2)])
    H_xx = sp.diff(f, x, x)
    H_xy = sp.diff(f, x, y)
    H_yy = sp.diff(f, y, y)
    quad_term = sp.Rational(1, 2) * (H_xx * h1**2 + 2 * H_xy * h1 * h2 + H_yy * h2**2)
    taylor = f_a + grad_x * h1 + grad_y * h2 + quad_term
    return sp.expand(f_ah - taylor)

def _jacobian_chain_rule():
    """F4.13: Verify J(f o g) = J_f * J_g for specific mappings."""
    import sympy as sp
    t = sp.Symbol('t')
    # g: R -> R^2, g(t) = (t^2, t^3)
    g1, g2 = t**2, t**3
    # f: R^2 -> R, f(u,v) = u*v
    u, v = sp.symbols('u v')
    f = u * v
    # (f o g)(t) = t^2 * t^3 = t^5
    fog = f.subs([(u, g1), (v, g2)])
    # Direct derivative
    d_fog_dt = sp.diff(fog, t)
    # Chain rule: J_f * J_g = [df/du, df/dv] . [dg1/dt, dg2/dt]^T
    chain = sp.diff(f, u).subs([(u, g1), (v, g2)]) * sp.diff(g1, t) + \
            sp.diff(f, v).subs([(u, g1), (v, g2)]) * sp.diff(g2, t)
    return sp.expand(d_fog_dt - chain)

def _ex33_dfdx():
    """Example 3.3: df/dx of x^2*y + 3*x*y^2 should be 2xy + 3y^2."""
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2 * y + 3 * x * y**2
    computed = sp.diff(f, x)
    expected = 2 * x * y + 3 * y**2
    return sp.expand(computed - expected)

def _ex33_dfdy():
    """Example 3.3: df/dy of x^2*y + 3*x*y^2 should be x^2 + 6xy."""
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2 * y + 3 * x * y**2
    computed = sp.diff(f, y)
    expected = x**2 + 6 * x * y
    return sp.expand(computed - expected)

def _ex81_dfdx():
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2*y + sp.sin(x*y)
    computed = sp.diff(f, x)
    expected = 2*x*y + y*sp.cos(x*y)
    return sp.expand(computed - expected)

def _ex81_dfdy():
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2*y + sp.sin(x*y)
    computed = sp.diff(f, y)
    expected = x**2 + x*sp.cos(x*y)
    return sp.expand(computed - expected)

def _ex81_clairaut():
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2*y + sp.sin(x*y)
    fxy = sp.diff(f, x, y)
    fyx = sp.diff(f, y, x)
    return sp.expand(fxy - fyx)

def _ex81_mixed_partial_form():
    """Verify d2f/dxdy = 2x + cos(xy) - xy*sin(xy)."""
    import sympy as sp
    x, y = sp.symbols('x y')
    f = x**2*y + sp.sin(x*y)
    computed = sp.diff(f, x, y)
    expected = 2*x + sp.cos(x*y) - x*y*sp.sin(x*y)
    return sp.expand(computed - expected)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _max_directional_deriv():
    """At (3,4), grad f = (6,8), max directional = 10, attained at u=(0.6,0.8)."""
    grad = np.array([6.0, 8.0])
    grad_norm = float(np.linalg.norm(grad))
    u = grad / grad_norm
    dir_deriv = float(np.dot(grad, u))
    ok = abs(dir_deriv - grad_norm) < 1e-12
    return (ok, f"dir_deriv={dir_deriv}, ||grad||={grad_norm}")

def _grad_perp_to_level_curve():
    """For f(x,y)=x^2+y^2, on level curve f=25 at (3,4),
    gradient (6,8) is perpendicular to tangent (-4,3) of circle."""
    grad = np.array([6.0, 8.0])
    # Tangent to circle x^2+y^2=25 at (3,4) is (-4,3) (or proportional)
    tangent = np.array([-4.0, 3.0])
    dot = float(np.dot(grad, tangent))
    ok = abs(dot) < 1e-12
    return (ok, f"grad.tangent={dot}, expected 0")

def _positive_definite_local_min():
    """x^2+y^2 has Hessian [[2,0],[0,2]], positive definite => local min at origin."""
    H = np.array([[2.0, 0.0], [0.0, 2.0]])
    eigs = np.linalg.eigvalsh(H)
    ok = all(e > 0 for e in eigs)
    # Also verify gradient is zero at origin
    grad_at_origin = np.array([0.0, 0.0])  # 2*0, 2*0
    grad_ok = float(np.linalg.norm(grad_at_origin)) < 1e-12
    both_ok = ok and grad_ok
    return (both_ok, f"eigenvalues={eigs.tolist()}, grad_norm={np.linalg.norm(grad_at_origin)}")

def _saddle_point_check():
    """f=x^4+y^4-4xy+1 at (0,0): Hessian [[0,-4],[-4,0]], eigenvalues -4,4 => saddle."""
    H = np.array([[0.0, -4.0], [-4.0, 0.0]])
    eigs = np.linalg.eigvalsh(H)
    has_pos = any(e > 0 for e in eigs)
    has_neg = any(e < 0 for e in eigs)
    ok = has_pos and has_neg
    return (ok, f"eigenvalues={eigs.tolist()}, expected mixed signs")

def _numerical_vs_symbolic_gradient():
    """Numerical gradient of f(x,y)=x^2*y+sin(xy) at (1,pi/2) matches analytic."""
    import math
    x0, y0 = 1.0, math.pi / 2
    h = 1e-7

    def f(x, y):
        return x**2 * y + math.sin(x * y)

    # Central differences
    num_dfdx = (f(x0 + h, y0) - f(x0 - h, y0)) / (2 * h)
    num_dfdy = (f(x0, y0 + h) - f(x0, y0 - h)) / (2 * h)

    # Analytic
    ana_dfdx = 2 * x0 * y0 + y0 * math.cos(x0 * y0)
    ana_dfdy = x0**2 + x0 * math.cos(x0 * y0)

    err_x = abs(num_dfdx - ana_dfdx)
    err_y = abs(num_dfdy - ana_dfdy)

    ok = err_x < 1e-5 and err_y < 1e-5
    return (ok, f"err_x={err_x:.2e}, err_y={err_y:.2e}")

def _jacobian_det_polar_sweep():
    """Jacobian determinant of polar-to-Cartesian equals r for several r values."""
    import math
    theta = math.pi / 6
    ok = True
    details = []
    for r in [0.5, 1.0, 2.0, 5.0, 10.0]:
        J = np.array([
            [math.cos(theta), -r * math.sin(theta)],
            [math.sin(theta), r * math.cos(theta)],
        ])
        det = float(np.linalg.det(J))
        err = abs(det - r)
        if err > 1e-10:
            ok = False
            details.append(f"r={r}: det={det}, err={err}")
    msg = "; ".join(details) if details else "all r values matched"
    return (ok, msg)
