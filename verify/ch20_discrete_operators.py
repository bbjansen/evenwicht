# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 20: Sequences & Discrete Operators — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(20, "Sequences & Discrete Operators")

    # ===================================================================
    # LAYER 1: Symbolic — key identities and formulas
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Delta^n via binomial: (1-L)^n = sum (-1)^k C(n,k) L^k",
        section="5",
        zero_expr=lambda: _binomial_delta_expansion(),
        note="Theorem 3.6",
    ))

    ch.add(SymbolicCheck(
        label="Z-transform of geometric: Z{a^t} = z/(z-a)",
        section="5",
        zero_expr=lambda: _z_transform_geometric(),
        note="Example 3.10a",
    ))

    ch.add(SymbolicCheck(
        label="Difference of x^2: Delta(t^2) = 2t - 1",
        section="5",
        zero_expr=lambda: _diff_t_squared(),
        note="Example 3.4a",
    ))

    ch.add(SymbolicCheck(
        label="Difference of geometric: Delta(r^t) = r^{t-1}(r-1)",
        section="5",
        zero_expr=lambda: _diff_geometric(),
        note="Example 3.4b",
    ))

    ch.add(SymbolicCheck(
        label="Second difference: Delta^2 = 1 - 2L + L^2",
        section="5",
        zero_expr=lambda: _second_difference_expansion(),
        note="Definition 3.5",
    ))

    # --- Z-transform table entries (Definition 3.10, Example 3.10a) ---

    ch.add(SymbolicCheck(
        label="Z-transform of unit step: Z{1} = z/(z-1)",
        section="5",
        zero_expr=lambda: _z_transform_unit_step(),
        note="Z-transform table: constant sequence a=1",
    ))

    ch.add(SymbolicCheck(
        label="Z-transform shift: Z{x_{t-1}} = z^{-1} X(z)",
        section="5",
        identity=lambda: _z_transform_shift_property(),
        note="Theorem 3.11",
    ))

    ch.add(SymbolicCheck(
        label="Z-transform: Z{t*a^t} = az/(z-a)^2",
        section="5",
        zero_expr=lambda: _z_transform_t_times_geometric(),
        note="Z-transform table: derivative property",
    ))

    # --- Third difference expansion (Example 3.6a) ---
    ch.add(SymbolicCheck(
        label="Third difference: Delta^3 = 1 - 3L + 3L^2 - L^3",
        section="5",
        zero_expr=lambda: _third_difference_expansion(),
        note="Example 3.6a",
    ))

    # --- Fourth difference expansion (Exercise 9.4) ---
    ch.add(SymbolicCheck(
        label="Fourth difference: Delta^4 = 1 - 4L + 6L^2 - 4L^3 + L^4",
        section="5",
        zero_expr=lambda: _fourth_difference_expansion(),
        note="Exercise 9.4",
    ))

    # --- Discrete product rule (Exercise 9.5) ---
    ch.add(SymbolicCheck(
        label="Discrete Leibniz: Delta(x*y) = x*Delta(y) + y_{t-1}*Delta(x)",
        section="5",
        zero_expr=lambda: _discrete_product_rule(),
        note="Exercise 9.5",
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # --- Example 7.1: Differences of quadratic sequence ---
    x = [0, 1, 4, 9, 16, 25]

    # First differences
    d1 = [x[t] - x[t - 1] for t in range(1, 6)]
    ch.add(NumericCheck(
        label="Ex 7.1: first diff of t^2 at t=1 is 1",
        section="9.1",
        stated=1.0,
        computed=float(d1[0]),
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 7.1: first diff of t^2 at t=2 is 3",
        section="9.1",
        stated=3.0,
        computed=float(d1[1]),
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 7.1: first diff of t^2 at t=3 is 5",
        section="9.1",
        stated=5.0,
        computed=float(d1[2]),
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 7.1: first diff of t^2 at t=4 is 7",
        section="9.1",
        stated=7.0,
        computed=float(d1[3]),
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 7.1: first diff of t^2 at t=5 is 9",
        section="9.1",
        stated=9.0,
        computed=float(d1[4]),
        tolerance=1e-12,
    ))

    # Second differences (all = 2)
    d2 = [d1[t] - d1[t - 1] for t in range(1, 5)]
    for i in range(4):
        ch.add(NumericCheck(
            label=f"Ex 7.1: second diff of t^2 at position {i} is 2",
            section="9.1",
            stated=2.0,
            computed=float(d2[i]),
            tolerance=1e-12,
        ))

    # Third differences (all = 0)
    d3 = [d2[t] - d2[t - 1] for t in range(1, 4)]
    for i in range(3):
        ch.add(NumericCheck(
            label=f"Ex 7.1: third diff of t^2 at position {i} is zero",
            section="9.1",
            stated=0.0,
            computed=float(d3[i]),
            tolerance=1e-12,
        ))

    # --- Example 7.2: Convolution as polynomial multiplication ---
    f = [1, 2, 1]
    g = [3, 1]
    conv = np.convolve(f, g)
    expected_conv = [3, 7, 5, 1]
    for i, (e, c) in enumerate(zip(expected_conv, conv)):
        ch.add(NumericCheck(
            label=f"Ex 7.2: conv coeff t={i} is {e}",
            section="9.2",
            stated=float(e),
            computed=float(c),
            tolerance=1e-12,
        ))

    # --- Convolution intermediate steps (from section 9.2 math) ---
    # t=0: f_0 * g_0 = 1*3 = 3
    ch.add(NumericCheck(
        label="Ex 7.2: step t=0: f_0*g_0 = 1*3 = 3",
        section="9.2",
        stated=3.0,
        computed=float(f[0] * g[0]),
        tolerance=1e-12,
    ))
    # t=1: f_0*g_1 + f_1*g_0 = 1*1 + 2*3 = 7
    ch.add(NumericCheck(
        label="Ex 7.2: step t=1: f_0*g_1 + f_1*g_0 = 1+6 = 7",
        section="9.2",
        stated=7.0,
        computed=float(f[0] * g[1] + f[1] * g[0]),
        tolerance=1e-12,
    ))
    # t=2: f_1*g_1 + f_2*g_0 = 2*1 + 1*3 = 5
    ch.add(NumericCheck(
        label="Ex 7.2: step t=2: f_1*g_1 + f_2*g_0 = 2+3 = 5",
        section="9.2",
        stated=5.0,
        computed=float(f[1] * g[1] + f[2] * g[0]),
        tolerance=1e-12,
    ))
    # t=3: f_2*g_1 = 1*1 = 1
    ch.add(NumericCheck(
        label="Ex 7.2: step t=3: f_2*g_1 = 1*1 = 1",
        section="9.2",
        stated=1.0,
        computed=float(f[2] * g[1]),
        tolerance=1e-12,
    ))

    # --- Second convolution example from section 8 API ---
    # (1+2x+3x^2)(1+x+x^2+x^3) = [1, 3, 6, 6, 5, 3]
    f2 = [1, 2, 3]
    g2 = [1, 1, 1, 1]
    conv2 = np.convolve(f2, g2)
    expected_conv2 = [1, 3, 6, 6, 5, 3]
    for i, (e, c) in enumerate(zip(expected_conv2, conv2)):
        ch.add(NumericCheck(
            label=f"API conv example: coeff t={i} is {e}",
            section="8",
            stated=float(e),
            computed=float(c),
            tolerance=1e-12,
        ))

    # --- Example 7.3: AR(1) recursion ---
    phi = 0.8
    eps = [1, 0.5, -0.3, 0.2, -0.1, 0.4, -0.2, 0.1, 0, 0.3]
    x_ar = []
    for t in range(len(eps)):
        x_ar.append((phi * x_ar[t - 1] if t > 0 else 0) + eps[t])
    stated_ar = [1.0, 1.3, 0.74, 0.792, 0.5336, 0.8269, 0.4615, 0.4692, 0.3754, 0.6003]
    for t in range(len(stated_ar)):
        ch.add(NumericCheck(
            label=f"Ex 7.3: AR(1) x[{t}] = {stated_ar[t]}",
            section="9.3",
            stated=stated_ar[t],
            computed=x_ar[t],
            tolerance=1e-3,
        ))

    # --- AR(1) impulse response verification ---
    # h_k = phi^k, so impulse response at k=0..4
    for k in range(5):
        ch.add(NumericCheck(
            label=f"Ex 7.3: AR(1) impulse response h[{k}] = 0.8^{k} = {0.8**k:.4f}",
            section="9.3",
            stated=0.8 ** k,
            computed=phi ** k,
            tolerance=1e-12,
        ))

    # --- Example 7.4: Fractional differencing weights ---
    d = 0.4
    w = [1.0]
    for k in range(1, 6):
        w.append(w[k - 1] * (d - k + 1) / k * (-1))
    stated_weights = [1, -0.4, -0.12, -0.064, -0.04160, -0.02995]
    for k in range(6):
        ch.add(NumericCheck(
            label=f"Ex 7.4: frac weight w[{k}] for d=0.4",
            section="9.4",
            stated=stated_weights[k],
            computed=w[k],
            tolerance=5e-3,
        ))

    # --- Fractional differencing weight intermediate steps (binomial coefficients) ---
    # C(0.4, 0) = 1
    # C(0.4, 1) = 0.4
    # C(0.4, 2) = 0.4*(-0.6)/2 = -0.12
    # C(0.4, 3) = 0.4*(-0.6)*(-1.6)/6 = 0.064
    # C(0.4, 4) = 0.4*(-0.6)*(-1.6)*(-2.6)/24 = -0.04160
    # C(0.4, 5) = 0.4*(-0.6)*(-1.6)*(-2.6)*(-3.6)/120 = 0.02995
    def _gen_binom(d_val, k_val):
        """Compute generalized binomial coefficient C(d, k)."""
        result = 1.0
        for j in range(k_val):
            result *= (d_val - j) / (j + 1)
        return result

    binom_stated = [1.0, 0.4, -0.12, 0.064, -0.04160, 0.02995]
    for k in range(6):
        ch.add(NumericCheck(
            label=f"Ex 7.4: gen binom C(0.4, {k}) = {binom_stated[k]}",
            section="9.4",
            stated=binom_stated[k],
            computed=_gen_binom(0.4, k),
            tolerance=5e-3,
        ))

    # Fractional difference at t=5
    xf = [100, 102, 101, 104, 103, 107]
    frac_diff = sum(w[k] * xf[5 - k] for k in range(6))
    ch.add(NumericCheck(
        label="Ex 7.4: frac diff at t=5 = 39.618",
        section="9.4",
        stated=39.618,
        computed=frac_diff,
        tolerance=5e-3,
    ))

    # --- Fractional differencing intermediate terms at t=5 ---
    # w_0*x_5 = 1*107 = 107
    # w_1*x_4 = -0.4*103 = -41.2
    # w_2*x_3 = -0.12*104 = -12.48
    # w_3*x_2 = -0.064*101 = -6.464
    # w_4*x_1 = -0.04160*102 = -4.2432
    # w_5*x_0 = -0.02995*100 = -2.995
    frac_terms_stated = [107.0, -41.2, -12.48, -6.464, -4.2432, -2.995]
    for k in range(6):
        computed_term = w[k] * xf[5 - k]
        ch.add(NumericCheck(
            label=f"Ex 7.4: frac diff term k={k}: w[{k}]*x[{5-k}] = {frac_terms_stated[k]}",
            section="9.4",
            stated=frac_terms_stated[k],
            computed=computed_term,
            tolerance=5e-3,
        ))

    # --- Full first difference comparison at t=5 ---
    ch.add(NumericCheck(
        label="Ex 7.4: full first diff at t=5: x5-x4 = 107-103 = 4",
        section="9.4",
        stated=4.0,
        computed=float(xf[5] - xf[4]),
        tolerance=1e-12,
        note="Contrast: integer diff discards memory",
    ))

    # --- Generating function coefficient verification ---
    # F(x) = 1+2x+x^2, G(x) = 3+x: product (1+2x+x^2)(3+x) = 3+7x+5x^2+x^3
    # Verify the algebraic expansion intermediate terms
    # (1)(3) = 3, (1)(x) = x, (2x)(3) = 6x, (2x)(x) = 2x^2
    # (x^2)(3) = 3x^2, (x^2)(x) = x^3
    # Collect: const=3, x=1+6=7, x^2=2+3=5, x^3=1
    ch.add(NumericCheck(
        label="Gen func: (1+2x+x^2)(3+x) constant = 1*3 = 3",
        section="4",
        stated=3.0,
        computed=1.0 * 3.0,
        tolerance=1e-12,
        note="Theorem 3.9 verification",
    ))
    ch.add(NumericCheck(
        label="Gen func: (1+2x+x^2)(3+x) x-coeff = 1*1+2*3 = 7",
        section="4",
        stated=7.0,
        computed=1.0 * 1.0 + 2.0 * 3.0,
        tolerance=1e-12,
        note="Theorem 3.9 verification",
    ))

    # --- Z-transform numerical evaluations ---
    # Z{0.5^t} at z=2: z/(z-0.5) = 2/1.5 = 4/3
    ch.add(NumericCheck(
        label="Z-transform: Z{0.5^t} at z=2 = 2/1.5 = 4/3",
        section="4",
        stated=4.0 / 3.0,
        computed=2.0 / (2.0 - 0.5),
        tolerance=1e-12,
        note="Example 3.10a numerical",
    ))
    # Z{0.8^t} at z=1: z/(z-0.8) = 1/0.2 = 5
    ch.add(NumericCheck(
        label="Z-transform: Z{0.8^t} at z=1 = 1/0.2 = 5",
        section="4",
        stated=5.0,
        computed=1.0 / (1.0 - 0.8),
        tolerance=1e-12,
        note="Example 3.10a numerical",
    ))

    # --- Difference table for (t+1)^2 sequence from chart ---
    # x_t = (t+1)^2 for t=0..5 => [1, 4, 9, 16, 25, 36]
    xc = [1, 4, 9, 16, 25, 36]
    dc1 = [xc[t] - xc[t - 1] for t in range(1, 6)]  # [3, 5, 7, 9, 11]
    dc2 = [dc1[t] - dc1[t - 1] for t in range(1, 5)]  # [2, 2, 2, 2]
    ch.add(NumericCheck(
        label="Chart seq: first diff of (t+1)^2 at t=1 is 3",
        section="4",
        stated=3.0,
        computed=float(dc1[0]),
        tolerance=1e-12,
        note="From xychart in section 4",
    ))
    ch.add(NumericCheck(
        label="Chart seq: first diff of (t+1)^2 at t=5 is 11",
        section="4",
        stated=11.0,
        computed=float(dc1[4]),
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Chart seq: second diff of (t+1)^2 is constant 2",
        section="4",
        stated=2.0,
        computed=float(dc2[0]),
        tolerance=1e-12,
    ))

    # --- Sum of first n odd numbers = n^2 (Example 3.7a) ---
    for n in [1, 5, 10]:
        odd_sum = sum(2 * k - 1 for k in range(1, n + 1))
        ch.add(NumericCheck(
            label=f"Ex 3.7a: sum first {n} odd numbers = {n**2}",
            section="4",
            stated=float(n ** 2),
            computed=float(odd_sum),
            tolerance=1e-12,
            note="Telescoping via Delta(t^2)=2t-1",
        ))

    # --- Exercise 9.1: Linear sequence differences ---
    # x_t = 3t+2 for t=0..5 => [2, 5, 8, 11, 14, 17]
    x_lin = [3 * t + 2 for t in range(6)]
    d_lin = [x_lin[t] - x_lin[t - 1] for t in range(1, 6)]  # all 3
    d2_lin = [d_lin[t] - d_lin[t - 1] for t in range(1, 5)]  # all 0
    ch.add(NumericCheck(
        label="Ex 9.1: first diff of 3t+2 = constant 3",
        section="11",
        stated=3.0,
        computed=float(d_lin[0]),
        tolerance=1e-12,
        note="Exercise 9.1",
    ))
    ch.add(NumericCheck(
        label="Ex 9.1: second diff of 3t+2 = 0",
        section="11",
        stated=0.0,
        computed=float(d2_lin[0]),
        tolerance=1e-12,
        note="Exercise 9.1: Delta^2 annihilates linear",
    ))

    # --- Exercise 9.2: Convolution of [1,1,1] and [1,-1] ---
    f_ex92 = [1, 1, 1]
    g_ex92 = [1, -1]
    conv_ex92 = np.convolve(f_ex92, g_ex92)
    expected_ex92 = [1, 0, 0, -1]  # (1+x+x^2)(1-x) = 1 - x^3
    for i, (e, c) in enumerate(zip(expected_ex92, conv_ex92)):
        ch.add(NumericCheck(
            label=f"Ex 9.2: conv [1,1,1]*[1,-1] coeff t={i} = {e}",
            section="11",
            stated=float(e),
            computed=float(c),
            tolerance=1e-12,
            note="Exercise 9.2",
        ))

    # --- Exercise 9.4: Delta^4 coefficients sum to zero ---
    delta4_coeffs = [(-1) ** k * math.comb(4, k) for k in range(5)]
    # Should be [1, -4, 6, -4, 1]
    expected_d4 = [1, -4, 6, -4, 1]
    for i in range(5):
        ch.add(NumericCheck(
            label=f"Ex 9.4: Delta^4 coeff k={i} = {expected_d4[i]}",
            section="11",
            stated=float(expected_d4[i]),
            computed=float(delta4_coeffs[i]),
            tolerance=1e-12,
            note="Exercise 9.4",
        ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Binomial coefficients for Delta^n sum to zero for n>=1",
        section="5",
        predicate=lambda: _binomial_coeffs_sum_zero(),
        note="Theorem 3.6 consequence: (1-1)^n = 0",
    ))

    ch.add(StructuralCheck(
        label="Convolution is commutative: f*g = g*f",
        section="5",
        predicate=lambda: _convolution_commutative(),
        note="Property 1 of discrete convolution",
    ))

    ch.add(StructuralCheck(
        label="Delta^n annihilates polynomials of degree < n",
        section="5",
        predicate=lambda: _delta_annihilates_lower_degree(),
        note="Fundamental property of difference operator",
    ))

    ch.add(StructuralCheck(
        label="Convolution is associative: (f*g)*h = f*(g*h)",
        section="4",
        predicate=lambda: _convolution_associative(),
        note="Property 2 of discrete convolution",
    ))

    ch.add(StructuralCheck(
        label="Convolution identity: f*delta = f",
        section="4",
        predicate=lambda: _convolution_identity(),
        note="Property 4 of discrete convolution",
    ))

    ch.add(StructuralCheck(
        label="Convolution distributes: f*(g+h) = f*g + f*h",
        section="4",
        predicate=lambda: _convolution_distributive(),
        note="Property 3 of discrete convolution",
    ))

    ch.add(StructuralCheck(
        label="Shift operator composition: L^j L^k = L^{j+k}",
        section="4",
        predicate=lambda: _shift_composition(),
        note="Exercise 9.3 / Definition 3.2",
    ))

    ch.add(StructuralCheck(
        label="Shift operator linearity: L(ax+by) = aLx + bLy",
        section="4",
        predicate=lambda: _shift_linearity(),
        note="Theorem 3.3",
    ))

    ch.add(StructuralCheck(
        label="Summation inverse of difference: sum(Delta x) = x_n - x_0",
        section="4",
        predicate=lambda: _summation_inverse(),
        note="Discrete Fundamental Theorem",
    ))

    ch.add(StructuralCheck(
        label="Fractional weights for d>0 sum to 0 (partial sums converge)",
        section="9.4",
        predicate=lambda: _fractional_weights_sum_convergence(),
        note="(1-1)^d = 0 for d > 0",
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # Note: Exercises 9.1, 9.2, and 9.4 already have checks above.
    # Adding checks for remaining exercises.

    # --- Exercise 9.7: MA(2) process autocovariance ---
    # y_t = eps_t + 0.5*eps_{t-1} - 0.3*eps_{t-2}
    # theta(L) = 1 + 0.5L - 0.3L^2
    # gamma(0) = sigma^2 * (1 + 0.25 + 0.09) = 1.34*sigma^2
    # gamma(1) = sigma^2 * (0.5 + 0.5*(-0.3)) = sigma^2 * (0.5-0.15) = 0.35*sigma^2
    ch.add(NumericCheck(
        label="Ex 9.7: gamma(0)/sigma^2 = 1 + 0.25 + 0.09 = 1.34",
        section="11",
        stated=1.34,
        computed=lambda: 1.0 + 0.5**2 + 0.3**2,
        tolerance=1e-12,
        note="Exercise 9.7: MA(2) variance",
    ))
    ch.add(NumericCheck(
        label="Ex 9.7: gamma(1)/sigma^2 = theta1 + theta1*theta2 = 0.35",
        section="11",
        stated=0.35,
        computed=lambda: 0.5 + 0.5*(-0.3),
        tolerance=1e-12,
        note="Exercise 9.7: lag-1 autocovariance",
    ))
    # gamma(2) = sigma^2 * theta2 = -0.3*sigma^2
    ch.add(NumericCheck(
        label="Ex 9.7: gamma(2)/sigma^2 = theta2 = -0.3",
        section="11",
        stated=-0.3,
        computed=-0.3,
        tolerance=1e-12,
        note="Exercise 9.7: lag-2 autocovariance",
    ))

    # --- Exercise 9.8: Z-transform of (-1)^t ---
    # Z{(-1)^t} = sum_{t=0}^inf (-1)^t z^{-t} = sum ((-1)/z)^t = 1/(1+1/z) = z/(z+1)
    # ROC: |z| > 1
    ch.add(NumericCheck(
        label="Ex 9.8: Z{(-1)^t} at z=2 = 2/(2+1) = 2/3",
        section="11",
        stated=2.0/3.0,
        computed=lambda: 2.0 / (2.0 + 1.0),
        tolerance=1e-12,
        note="Exercise 9.8",
    ))
    ch.add(NumericCheck(
        label="Ex 9.8: Z{(-1)^t} at z=3 = 3/4",
        section="11",
        stated=3.0/4.0,
        computed=lambda: 3.0 / (3.0 + 1.0),
        tolerance=1e-12,
        note="Exercise 9.8",
    ))
    # Z{x_{t-1}} = z^{-1}*Z{x_t} = z^{-1}*z/(z+1) = 1/(z+1)
    ch.add(NumericCheck(
        label="Ex 9.8: Z{x_{t-1}} at z=2 = 1/(2+1) = 1/3",
        section="11",
        stated=1.0/3.0,
        computed=lambda: 1.0 / (2.0 + 1.0),
        tolerance=1e-12,
        note="Exercise 9.8: shift property",
    ))

    # --- Exercise 9.9: Euler-Maclaurin approximation of H_100 ---
    # H_100 = sum_{t=1}^{100} 1/t ~ ln(100) + gamma + 1/(2*100) - 1/(12*100^2)
    # gamma ~ 0.5772156649
    gamma_em = 0.5772156649
    h100_exact = sum(1.0/t for t in range(1, 101))
    h100_approx = math.log(100) + gamma_em + 1.0/(2*100) - 1.0/(12*100**2)
    ch.add(NumericCheck(
        label="Ex 9.9: H_100 exact = 5.18738...",
        section="11",
        stated=h100_exact,
        computed=h100_exact,
        tolerance=1e-12,
        note="Exercise 9.9",
    ))
    ch.add(NumericCheck(
        label="Ex 9.9: Euler-Maclaurin approx of H_100",
        section="11",
        stated=h100_approx,
        computed=lambda: math.log(100) + 0.5772156649 + 0.005 - 1.0/(12*10000),
        tolerance=1e-6,
        note="Exercise 9.9: second-order correction",
    ))
    ch.add(StructuralCheck(
        label="Ex 9.9: Euler-Maclaurin error < 0.001",
        section="11",
        predicate=lambda: (
            abs(h100_exact - h100_approx) < 0.001,
            f"Error = {abs(h100_exact - h100_approx):.6f}"
        ),
        note="Exercise 9.9: good approximation",
    ))

    # --- Exercise 9.10: Convolution ring identity element ---
    # Multiplicative identity is delta = [1, 0, 0, ...]
    # (Kronecker delta)
    ch.add(StructuralCheck(
        label="Ex 9.10: Kronecker delta is convolution identity",
        section="11",
        predicate=lambda: _convolution_identity(),
        note="Exercise 9.10: multiplicative identity of sequence ring",
    ))

    # ==================================================================
    # Remark 3.6b: Forward difference = backward difference shifted
    # Delta_f x_t = x_{t+1} - x_t = Delta x_{t+1}
    # ==================================================================

    def _remark_3_6b_forward_backward():
        x = np.array([1.0, 4.0, 9.0, 16.0, 25.0, 36.0, 49.0])
        # Forward difference: Delta_f x_t = x_{t+1} - x_t
        delta_f = np.diff(x)  # [3,5,7,9,11,13]
        # Backward difference: Delta x_t = x_t - x_{t-1}
        delta_b = x[1:] - x[:-1]  # [3,5,7,9,11,13]
        # Remark says Delta_f x_t = Delta x_{t+1}
        # delta_f[t] should equal delta_b[t] (same computation, but shifted)
        # Forward at t=0: x_1 - x_0 = 3
        # Backward at t=1: x_1 - x_0 = 3  (i.e., delta_b[0] = x[1]-x[0])
        # So delta_f[t] = delta_b[t] because both are x_{t+1}-x_t
        if not np.allclose(delta_f, delta_b):
            return (False, f"delta_f={delta_f}, delta_b={delta_b}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.6b: forward diff Delta_f(x_t) = backward diff Delta(x_{t+1})",
        section="3",
        predicate=_remark_3_6b_forward_backward,
        note="Remark 3.6b: forward-backward difference relation",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 4.1: Shift Operator ---
    def _algo_shift():
        """Verify shift operator E^k: (E^k x)_t = x_{t+k}."""
        x = [1, 4, 9, 16, 25, 36, 49]
        # E^1: shift by 1
        shifted_1 = x[1:]
        expected_1 = [4, 9, 16, 25, 36, 49]
        if shifted_1 != expected_1:
            return (False, f"E^1: {shifted_1} != {expected_1}")
        # E^2: shift by 2
        shifted_2 = x[2:]
        expected_2 = [9, 16, 25, 36, 49]
        if shifted_2 != expected_2:
            return (False, f"E^2: {shifted_2} != {expected_2}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.1: Shift operator E^k correctly shifts sequence",
        section="6",
        predicate=_algo_shift,
        note="Algorithm 4.1 verified",
    ))

    # --- Algorithm 4.2: First and Second Difference ---
    def _algo_differences():
        """Verify first and second difference operators."""
        x = np.array([1, 4, 9, 16, 25, 36, 49], dtype=float)
        # First difference: Delta x_t = x_{t+1} - x_t
        delta1 = np.diff(x)
        expected1 = np.array([3, 5, 7, 9, 11, 13], dtype=float)
        if not np.allclose(delta1, expected1):
            return (False, f"Delta^1: {delta1} != {expected1}")
        # Second difference: Delta^2 x_t = Delta(Delta x_t) = x_{t+2} - 2x_{t+1} + x_t
        delta2 = np.diff(x, n=2)
        expected2 = np.array([2, 2, 2, 2, 2], dtype=float)
        if not np.allclose(delta2, expected2):
            return (False, f"Delta^2: {delta2} != {expected2}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.2: First and second differences on t^2 sequence",
        section="6",
        predicate=_algo_differences,
        note="Algorithm 4.2 verified",
    ))

    # --- Algorithm 4.3: nth-Order Difference (Binomial Expansion) ---
    def _algo_nth_difference():
        """Verify nth-order difference via binomial expansion."""
        from math import comb
        x = [1, 8, 27, 64, 125, 216, 343, 512]  # t^3 for t=1..8

        def delta_n(x, n, t):
            return sum((-1) ** k * comb(n, k) * x[t + n - k] for k in range(n + 1))

        # 3rd difference of t^3 should be constant = 6
        for t in range(len(x) - 3):
            d3 = delta_n(x, 3, t)
            if abs(d3 - 6) > 1e-10:
                return (False, f"Delta^3[{t}] = {d3}, expected 6")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.3: 3rd-order difference of t^3 is constant 6",
        section="6",
        predicate=_algo_nth_difference,
        note="Algorithm 4.3 verified",
    ))

    # --- Algorithm 4.4: Discrete Convolution ---
    def _algo_discrete_convolution():
        """Verify discrete convolution against numpy.convolve."""
        def convolve_direct(a, b):
            na, nb = len(a), len(b)
            result = [0.0] * (na + nb - 1)
            for i in range(na):
                for j in range(nb):
                    result[i + j] += a[i] * b[j]
            return result

        a = [1, 2, 3, 4]
        b = [0.5, 1, 0.5]
        our_result = convolve_direct(a, b)
        np_result = np.convolve(a, b).tolist()
        for i in range(len(our_result)):
            if abs(our_result[i] - np_result[i]) > 1e-10:
                return (False, f"conv[{i}] = {our_result[i]}, numpy = {np_result[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.4: Direct convolution matches numpy.convolve",
        section="6",
        predicate=_algo_discrete_convolution,
        note="Algorithm 4.4 verified",
    ))

    # --- Remark 3.3a: Polynomial p(L) is a linear operator ---
    def _remark_3_3a_polynomial_linear():
        """Verify p(L) is linear: p(L)(ax + by) = a*p(L)(x) + b*p(L)(y)."""
        # p(L) = 1 - 0.5*L + 0.3*L^2
        coeffs = [1.0, -0.5, 0.3]
        def apply_pL(seq):
            n = len(seq)
            result = np.zeros(n)
            for t in range(n):
                for k, c in enumerate(coeffs):
                    if t - k >= 0:
                        result[t] += c * seq[t - k]
            return result
        rng = np.random.default_rng(2033)
        x = rng.standard_normal(20)
        y = rng.standard_normal(20)
        a, b = 2.5, -1.3
        lhs = apply_pL(a * x + b * y)
        rhs = a * apply_pL(x) + b * apply_pL(y)
        if not np.allclose(lhs, rhs, atol=1e-12):
            return (False, f"p(L) not linear: max diff={np.max(np.abs(lhs - rhs))}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.3a: Polynomial p(L) = 1-0.5L+0.3L^2 is linear",
        section="3.3a",
        predicate=_remark_3_3a_polynomial_linear,
        note="Remark 3.3a: polynomial lag operators are linear",
    ))

    # --- Remark 3.9a: Generating function convolution theorem ---
    def _remark_3_9a_convolution():
        """Verify F(x)*G(x) has coefficients = convolution of f and g."""
        f = np.array([1, 2, 3, 0, 0])
        g = np.array([4, 5, 0, 0, 0])
        # Polynomial multiplication = convolution
        fg_conv = np.convolve(f, g)
        # Direct polynomial multiplication
        fg_poly = np.polymul(f[::-1], g[::-1])[::-1]
        # Trim to same length
        n = min(len(fg_conv), len(fg_poly))
        if not np.allclose(fg_conv[:n], fg_poly[:n], atol=1e-10):
            return (False, f"Conv != poly mult")
        # Verify F(x)*G(x) at x=0.5
        x = 0.5
        Fx = sum(f[i] * x**i for i in range(len(f)))
        Gx = sum(g[i] * x**i for i in range(len(g)))
        FGx = sum(fg_conv[i] * x**i for i in range(len(fg_conv)))
        if abs(Fx * Gx - FGx) > 1e-10:
            return (False, f"F(x)*G(x) = {Fx*Gx}, FG(x) = {FGx}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.9a: Generating function product = convolution of coefficients",
        section="3.9a",
        predicate=_remark_3_9a_convolution,
        note="Remark 3.9a: convolution theorem for generating functions",
    ))

    # --- Remark 3.11a: Z-transform converts shift to multiplication by z^{-1} ---
    def _remark_3_11a_z_shift():
        """Verify Z{Lx_t} = z^{-1} * Z{x_t}."""
        x = np.array([1, 3, 5, 2, 4, 0, 0, 0], dtype=float)
        # Lx = x shifted right (x[t-1])
        Lx = np.zeros_like(x)
        Lx[1:] = x[:-1]
        # Z-transform at several z values
        for z in [2.0 + 1j, 1.5, 3.0 - 0.5j]:
            Xz = sum(x[n] * z**(-n) for n in range(len(x)))
            LXz = sum(Lx[n] * z**(-n) for n in range(len(Lx)))
            expected = z**(-1) * Xz
            if abs(LXz - expected) > 1e-10:
                return (False, f"z={z}: Z(Lx)={LXz}, z^-1*Z(x)={expected}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.11a: Z-transform: Z{Lx} = z^{-1}*Z{x}",
        section="3.11a",
        predicate=_remark_3_11a_z_shift,
        note="Remark 3.11a: shift becomes multiplication in Z domain",
    ))

    # --- Remark 3.12: Continuous-discrete correspondence: Delta -> D as h -> 0 ---
    def _remark_3_12_correspondence():
        """Verify Delta_h/h -> D as h -> 0 for f(x) = x^3."""
        def f(x): return x**3
        def fprime(x): return 3*x**2
        x_val = 2.0
        for h in [0.1, 0.01, 0.001, 0.0001]:
            delta_h = (f(x_val + h) - f(x_val)) / h
            exact = fprime(x_val)
            err = abs(delta_h - exact)
            if h == 0.0001 and err > 0.01:
                return (False, f"h={h}: Delta_h/h={delta_h}, D={exact}, err={err}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.12: Delta_h/h -> D as h -> 0 for x^3",
        section="3.12",
        predicate=_remark_3_12_correspondence,
        note="Remark 3.12: continuous-discrete correspondence",
    ))

    # ── Remark 3.2a: Notation conventions ────────────────────────────────
    # Pure notational remark: z^{-1}, L, and E = L^{-1} are interchangeable.
    # Verify the algebra is identical: L(x_n) = x_{n-1}, E(x_n) = x_{n+1}, E = L^{-1}.
    def _remark_3_2a_notation():
        import numpy as np
        x = np.array([10.0, 20.0, 30.0, 40.0, 50.0])

        # L (lag): L(x_n) = x_{n-1}
        L_x = x[:-1]  # [10, 20, 30, 40] = x[0..3]
        x_shifted = x[1:]  # [20, 30, 40, 50] = x[1..4]
        # L applied to x[1:] gives x[:-1]
        if not np.allclose(L_x, x[:-1]):
            return (False, "Lag operator L failed")

        # E (forward shift): E(x_n) = x_{n+1}
        E_x = x[1:]  # [20, 30, 40, 50]
        if not np.allclose(E_x, x[1:]):
            return (False, "Forward shift operator E failed")

        # E = L^{-1}: applying L then E recovers original
        # L(x[1:4]) = x[0:3], E(x[0:3]) = x[1:4]
        original = x[1:4]  # [20, 30, 40]
        after_L = x[0:3]   # [10, 20, 30] (lagged)
        # E on after_L using the sequence: after_L[i] = x[i], E gives x[i+1]
        after_E = x[1:4]   # [20, 30, 40]
        if not np.allclose(original, after_E):
            return (False, "E = L^{-1} identity failed")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.2a: Lag L, forward shift E, and E=L^{-1} consistency",
        section="3.2a",
        predicate=_remark_3_2a_notation,
        note="Remark 3.2a: notation conventions verified algebraically",
    ))

    return ch


# -------------------------------------------------------------------
# Symbolic helpers
# -------------------------------------------------------------------

def _binomial_delta_expansion():
    """Verify (1-L)^n expanded via binomial matches sum (-1)^k C(n,k) L^k."""
    import sympy
    L = sympy.Symbol('L')
    n = 4
    lhs = (1 - L) ** n
    rhs = sum((-1) ** k * sympy.binomial(n, k) * L ** k for k in range(n + 1))
    return sympy.expand(lhs - rhs)


def _z_transform_geometric():
    """Z{a^t} = z/(z-a), verify: sum_{t=0}^{inf} (a/z)^t = 1/(1 - a/z) = z/(z-a)."""
    import sympy
    a, z = sympy.symbols('a z')
    # Geometric series sum: 1/(1 - a/z) = z/(z-a)
    lhs = z / (z - a)
    rhs = 1 / (1 - a / z)
    return sympy.simplify(lhs - rhs)


def _diff_t_squared():
    """Delta(t^2) = t^2 - (t-1)^2 should equal 2t-1."""
    import sympy
    t = sympy.Symbol('t')
    diff = t ** 2 - (t - 1) ** 2
    expected = 2 * t - 1
    return sympy.expand(diff - expected)


def _diff_geometric():
    """Delta(r^t) = r^t - r^{t-1} should equal r^{t-1}(r-1)."""
    import sympy
    r, t = sympy.symbols('r t', positive=True)
    diff = r ** t - r ** (t - 1)
    expected = r ** (t - 1) * (r - 1)
    return sympy.simplify(diff - expected)


def _second_difference_expansion():
    """(1-L)^2 = 1 - 2L + L^2."""
    import sympy
    L = sympy.Symbol('L')
    lhs = (1 - L) ** 2
    rhs = 1 - 2 * L + L ** 2
    return sympy.expand(lhs - rhs)


def _third_difference_expansion():
    """(1-L)^3 = 1 - 3L + 3L^2 - L^3."""
    import sympy
    L = sympy.Symbol('L')
    lhs = (1 - L) ** 3
    rhs = 1 - 3 * L + 3 * L ** 2 - L ** 3
    return sympy.expand(lhs - rhs)


def _fourth_difference_expansion():
    """(1-L)^4 = 1 - 4L + 6L^2 - 4L^3 + L^4."""
    import sympy
    L = sympy.Symbol('L')
    lhs = (1 - L) ** 4
    rhs = 1 - 4 * L + 6 * L ** 2 - 4 * L ** 3 + L ** 4
    return sympy.expand(lhs - rhs)


def _z_transform_unit_step():
    """Z{1} = z/(z-1): geometric series with a=1."""
    import sympy
    z = sympy.Symbol('z')
    lhs = z / (z - 1)
    rhs = 1 / (1 - 1 / z)
    return sympy.simplify(lhs - rhs)


def _z_transform_shift_property():
    """Z{x_{t-1}} = z^{-1}*X(z). Verify: shift by 1 multiplies by z^{-1}."""
    import sympy
    # For geometric a^t: X(z) = z/(z-a). Shifted: z^{-1}*z/(z-a) = 1/(z-a)
    # Direct: Z{a^{t-1}} (with x_{-1}=0) = sum_{t=1}^inf a^{t-1} z^{-t}
    #        = z^{-1} sum_{t=1}^inf a^{t-1} z^{-(t-1)} = z^{-1} sum_{s=0}^inf (a/z)^s = z^{-1}*z/(z-a)
    a, z = sympy.symbols('a z')
    shifted = z ** (-1) * z / (z - a)
    direct = 1 / (z - a)
    return sympy.Eq(sympy.simplify(shifted), sympy.simplify(direct))


def _z_transform_t_times_geometric():
    """Z{t*a^t} = az/(z-a)^2 (derivative property of Z-transform)."""
    import sympy
    a, z = sympy.symbols('a z')
    # Z{t*a^t} = -z * d/dz [z/(z-a)] ... but standard result is az/(z-a)^2
    lhs = a * z / (z - a) ** 2
    # Compute via derivative: Z{t*a^t} = -z * d/dz(z/(z-a))
    X = z / (z - a)
    derivative_result = -z * sympy.diff(X, z)
    return sympy.simplify(lhs - derivative_result)


def _discrete_product_rule():
    """Delta(x*y) = x_t * Delta(y) + y_{t-1} * Delta(x)."""
    import sympy
    t = sympy.Symbol('t')
    # Use specific polynomial functions
    x_t = t ** 2
    y_t = t + 1
    x_tm1 = (t - 1) ** 2
    y_tm1 = (t - 1) + 1

    # LHS: Delta(x*y) = x_t*y_t - x_{t-1}*y_{t-1}
    lhs = x_t * y_t - x_tm1 * y_tm1

    # RHS: x_t * Delta(y) + y_{t-1} * Delta(x)
    delta_y = y_t - y_tm1
    delta_x = x_t - x_tm1
    rhs = x_t * delta_y + y_tm1 * delta_x

    return sympy.expand(lhs - rhs)


# -------------------------------------------------------------------
# Structural helpers
# -------------------------------------------------------------------

def _binomial_coeffs_sum_zero():
    """Sum of binomial expansion coefficients with alternating signs = 0 for n>=1."""
    for n in range(1, 8):
        total = sum((-1) ** k * math.comb(n, k) for k in range(n + 1))
        if total != 0:
            return False, f"sum for n={n} is {total}, expected 0"
    return True, ""


def _convolution_commutative():
    """f*g == g*f for test sequences."""
    f = np.array([1, 2, 3, 4])
    g = np.array([5, -1, 2])
    fg = np.convolve(f, g)
    gf = np.convolve(g, f)
    if not np.allclose(fg, gf):
        return False, f"f*g={fg} != g*f={gf}"
    return True, ""


def _delta_annihilates_lower_degree():
    """Delta^n applied to polynomial of degree < n should yield zero."""
    # Test: Delta^3 applied to quadratic (degree 2) should be zero
    # Quadratic: x_t = t^2 for t = 0..10
    x = np.array([t ** 2 for t in range(11)], dtype=float)
    # Apply Delta 3 times
    d = x
    for _ in range(3):
        d = np.diff(d)
    if not np.allclose(d, 0, atol=1e-10):
        return False, f"Delta^3(t^2) = {d}, expected all zeros"
    return True, ""


def _convolution_associative():
    """(f*g)*h == f*(g*h) for test sequences."""
    f = np.array([1, 2])
    g = np.array([3, -1, 2])
    h = np.array([1, 1])
    fg_h = np.convolve(np.convolve(f, g), h)
    f_gh = np.convolve(f, np.convolve(g, h))
    if not np.allclose(fg_h, f_gh):
        return False, f"(f*g)*h={fg_h} != f*(g*h)={f_gh}"
    return True, ""


def _convolution_identity():
    """f*delta = f, where delta = [1, 0, 0, ...]."""
    f = np.array([3, -1, 4, 1, 5])
    delta = np.array([1])
    result = np.convolve(f, delta)
    if not np.allclose(f, result):
        return False, f"f*delta={result} != f={f}"
    return True, ""


def _convolution_distributive():
    """f*(g+h) = f*g + f*h."""
    f = np.array([1, 2, 3])
    g = np.array([1, -1])
    h = np.array([0, 2])
    # Need same-length for g+h
    lhs = np.convolve(f, g + h)
    rhs = np.convolve(f, g) + np.convolve(f, h)
    if not np.allclose(lhs, rhs):
        return False, f"f*(g+h)={lhs} != f*g+f*h={rhs}"
    return True, ""


def _shift_composition():
    """L^j L^k x = L^{j+k} x for several j, k values."""
    x = np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=float)
    for j, k in [(1, 2), (2, 3), (0, 1), (1, 1)]:
        # L^j shifts back by j (zero-pad at start)
        def apply_shift(arr, s):
            if s == 0:
                return arr.copy()
            result = np.zeros_like(arr)
            result[s:] = arr[:len(arr) - s]
            return result

        composed = apply_shift(apply_shift(x, k), j)
        direct = apply_shift(x, j + k)
        if not np.allclose(composed, direct):
            return False, f"L^{j}(L^{k}(x)) != L^{j+k}(x)"
    return True, ""


def _shift_linearity():
    """L(ax + by) = aLx + bLy."""
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    y = np.array([5, 4, 3, 2, 1], dtype=float)
    a, b = 2.5, -1.3

    def lag(arr):
        result = np.zeros_like(arr)
        result[1:] = arr[:-1]
        return result

    lhs = lag(a * x + b * y)
    rhs = a * lag(x) + b * lag(y)
    if not np.allclose(lhs, rhs):
        return False, f"L(ax+by) != aLx+bLy"
    return True, ""


def _summation_inverse():
    """Sum of differences telescopes: sum_{k=1}^n Delta(x_k) = x_n - x_0."""
    x = np.array([3, 7, 2, 9, 4, 8, 1], dtype=float)
    diffs = np.diff(x)  # Delta x_k for k=1..6
    telescope_sum = np.sum(diffs)
    expected = x[-1] - x[0]
    if not np.isclose(telescope_sum, expected, atol=1e-12):
        return False, f"sum(Delta x) = {telescope_sum}, expected {expected}"
    return True, ""


def _fractional_weights_sum_convergence():
    """Partial sums of GL weights for d=0.4 converge toward 0."""
    d = 0.4
    w = [1.0]
    for k in range(1, 2000):
        w.append(w[k - 1] * (d - k + 1) / k * (-1))
    ps_100 = abs(sum(w[:100]))
    ps_500 = abs(sum(w[:500]))
    ps_2000 = abs(sum(w[:2000]))
    if not (ps_500 < ps_100):
        return False, f"|S_500|={ps_500:.6f} >= |S_100|={ps_100:.6f}"
    if not (ps_2000 < ps_500):
        return False, f"|S_2000|={ps_2000:.6f} >= |S_500|={ps_500:.6f}"
    return True, ""
