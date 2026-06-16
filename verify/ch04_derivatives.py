# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 4: Differential Calculus — verification."""

import math
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(4, "Differential Calculus")

    # ===================================================================
    # LAYER 1: Symbolic — differentiation rules (Section 5 formulas)
    # ===================================================================

    # --- F4.1: Constant rule ---
    ch.add(SymbolicCheck(
        label="F4.1 Constant rule: d/dx[c] = 0",
        section="5",
        zero_expr=lambda: _constant_rule(),
    ))

    # --- F4.2: Power rule ---
    ch.add(SymbolicCheck(
        label="F4.2 Power rule: d/dx[x^n] = n*x^(n-1)",
        section="5",
        zero_expr=lambda: _power_rule(),
    ))

    # --- F4.2 Power rule for general real exponent ---
    ch.add(SymbolicCheck(
        label="F4.2 Power rule fractional: d/dx[x^(3/2)] = (3/2)*x^(1/2)",
        section="5",
        zero_expr=lambda: _power_rule_fractional(),
    ))

    # --- F4.3: Sum/Difference rule ---
    ch.add(SymbolicCheck(
        label="F4.3 Sum rule: d/dx[f+g] = f'+g'",
        section="5",
        zero_expr=lambda: _sum_rule(),
    ))

    ch.add(SymbolicCheck(
        label="F4.3 Difference rule: d/dx[f-g] = f'-g'",
        section="5",
        zero_expr=lambda: _difference_rule(),
    ))

    # --- F4.4: Product rule ---
    ch.add(SymbolicCheck(
        label="F4.4 Product rule: (fg)' = f'g + fg'",
        section="5",
        zero_expr=lambda: _product_rule(),
    ))

    # --- F4.5: Quotient rule ---
    ch.add(SymbolicCheck(
        label="F4.5 Quotient rule: (f/g)' = (f'g-fg')/g^2",
        section="5",
        zero_expr=lambda: _quotient_rule(),
    ))

    # --- F4.6: Chain rule ---
    ch.add(SymbolicCheck(
        label="F4.6 Chain rule: d/dx[f(g(x))] = f'(g(x))*g'(x)",
        section="5",
        zero_expr=lambda: _chain_rule(),
    ))

    # --- F4.7: Exponential ---
    ch.add(SymbolicCheck(
        label="F4.7 d/dx[e^x] = e^x",
        section="5",
        zero_expr=lambda: _exp_derivative(),
    ))

    # --- F4.8: Natural logarithm ---
    ch.add(SymbolicCheck(
        label="F4.8 d/dx[ln(x)] = 1/x",
        section="5",
        zero_expr=lambda: _ln_derivative(),
    ))

    # --- F4.9: General exponential ---
    ch.add(SymbolicCheck(
        label="F4.9 d/dx[a^x] = a^x * ln(a)",
        section="5",
        zero_expr=lambda: _general_exp_derivative(),
    ))

    # --- F4.10: General logarithm ---
    ch.add(SymbolicCheck(
        label="F4.10 d/dx[log_a(x)] = 1/(x*ln(a))",
        section="5",
        zero_expr=lambda: _general_log_derivative(),
    ))

    # --- F4.11: Sine ---
    ch.add(SymbolicCheck(
        label="F4.11 d/dx[sin(x)] = cos(x)",
        section="5",
        zero_expr=lambda: _sin_derivative(),
    ))

    # --- F4.12: Cosine ---
    ch.add(SymbolicCheck(
        label="F4.12 d/dx[cos(x)] = -sin(x)",
        section="5",
        zero_expr=lambda: _cos_derivative(),
    ))

    # --- F4.13: Tangent ---
    ch.add(SymbolicCheck(
        label="F4.13 d/dx[tan(x)] = 1/cos^2(x)",
        section="5",
        zero_expr=lambda: _tan_derivative(),
    ))

    # --- F4.14: Absolute value ---
    ch.add(SymbolicCheck(
        label="F4.14 d/dx[|x|] = x/|x| (sign function)",
        section="5",
        zero_expr=lambda: _abs_derivative(),
    ))

    # --- F4.15: Square root ---
    ch.add(SymbolicCheck(
        label="F4.15 d/dx[sqrt(x)] = 1/(2*sqrt(x))",
        section="5",
        zero_expr=lambda: _sqrt_derivative(),
    ))

    # --- F4.16: Logarithmic differentiation ---
    ch.add(SymbolicCheck(
        label="F4.16 d/dx[f(x)^g(x)] logarithmic differentiation",
        section="5",
        zero_expr=lambda: _log_diff_rule(),
    ))

    # ===================================================================
    # LAYER 1 continued: Theorems from Section 4
    # ===================================================================

    # --- Theorem 4.6: Linearity of differentiation ---
    ch.add(SymbolicCheck(
        label="Thm 4.6 Linearity: D(af+bg) = a*Df + b*Dg",
        section="4",
        zero_expr=lambda: _linearity_check(),
    ))

    # --- Higher-order derivatives (Definition 4.5) ---
    ch.add(SymbolicCheck(
        label="Def 4.5 Second derivative: d^2/dx^2[x^3] = 6x",
        section="4",
        zero_expr=lambda: _second_derivative(),
    ))

    ch.add(SymbolicCheck(
        label="Def 4.5 Third derivative: d^3/dx^3[x^4] = 24x",
        section="4",
        zero_expr=lambda: _third_derivative(),
    ))

    # --- Theorem 4.20: tan derivative via quotient rule ---
    ch.add(SymbolicCheck(
        label="Thm 4.20 d/dx[sin/cos] = (cos^2+sin^2)/cos^2 = 1/cos^2",
        section="4",
        zero_expr=lambda: _tan_via_quotient(),
    ))

    # --- Remark 4.3: |x| continuous at 0 but not differentiable ---
    # Left limit of difference quotient = -1, right limit = +1
    def _remark_3_3_abs_not_diff():
        h_vals = [1e-4, 1e-6, 1e-8, 1e-10]
        # Right-hand limit: (|0+h| - |0|)/h = h/h = 1
        for h in h_vals:
            right = (abs(h) - abs(0)) / h
            if abs(right - 1.0) > 1e-6:
                return (False, f"Right limit at h={h}: {right}, expected 1.0")
        # Left-hand limit: (|0+h| - |0|)/h = |h|/h = -1 for h < 0
        for h in h_vals:
            left = (abs(-h) - abs(0)) / (-h)
            if abs(left - (-1.0)) > 1e-6:
                return (False, f"Left limit at h={-h}: {left}, expected -1.0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 4.3: |x| at x=0: left deriv=-1, right deriv=+1",
        section="3",
        predicate=_remark_3_3_abs_not_diff,
        note="Remark 4.3: continuous does not imply differentiable",
    ))

    # --- Theorem 4.23: x^x logarithmic differentiation (Exercise 4.8) ---
    ch.add(SymbolicCheck(
        label="Thm 4.23 / Ex 4.8: d/dx[x^x] = x^x*(ln(x)+1)",
        section="4",
        zero_expr=lambda: _x_to_x_derivative(),
    ))

    # --- Implicit differentiation: x^2+y^2=1 => dy/dx = -x/y ---
    ch.add(SymbolicCheck(
        label="Remark 4.27 Implicit diff: x^2+y^2=1 => dy/dx = -x/y",
        section="4",
        zero_expr=lambda: _implicit_circle(),
    ))

    # --- Exercise 4.1: d/dx[5x^3 - 2x + 7] = 15x^2 - 2 ---
    ch.add(SymbolicCheck(
        label="Ex 4.1: d/dx[5x^3-2x+7] = 15x^2-2",
        section="11",
        zero_expr=lambda: _exercise_10_1(),
    ))

    # --- Exercise 4.2: d/dx[x^2*e^x] = e^x*(x^2+2x) ---
    ch.add(SymbolicCheck(
        label="Ex 4.2: d/dx[x^2*e^x] = e^x*(x^2+2x)",
        section="11",
        zero_expr=lambda: _exercise_10_2(),
    ))

    # --- Exercise 4.3: d/dx[cos(3x)] = -3*sin(3x) ---
    ch.add(SymbolicCheck(
        label="Ex 4.3: d/dx[cos(3x)] = -3*sin(3x)",
        section="11",
        zero_expr=lambda: _exercise_10_3(),
    ))

    # --- Exercise 4.4: d/dx[e^x/(x^2+1)] via quotient rule ---
    ch.add(SymbolicCheck(
        label="Ex 4.4: d/dx[e^x/(x^2+1)] quotient rule",
        section="11",
        zero_expr=lambda: _exercise_10_4(),
    ))

    # --- Exercise 4.5: implicit diff of ellipse ---
    ch.add(SymbolicCheck(
        label="Ex 4.5: ellipse x^2/4+y^2/9=1 => dy/dx = -9x/(4y)",
        section="11",
        zero_expr=lambda: _exercise_10_5(),
    ))

    # --- Exercise 4.6: n-th derivative of e^(ax) = a^n * e^(ax) ---
    ch.add(SymbolicCheck(
        label="Ex 4.6: d^4/dx^4[e^(3x)] = 81*e^(3x)",
        section="11",
        zero_expr=lambda: _exercise_10_6(),
    ))

    # ===================================================================
    # LAYER 2: Numerical worked examples (Section 9)
    # ===================================================================

    # --- Example 4.33: d/dx[x^2] at x=3 = 6 ---
    ch.add(NumericCheck(
        label="Ex 4.33: d/dx[x^2] at x=3 = 6",
        section="9",
        stated=6.0,
        computed=2 * 3.0,
        tolerance=1e-12,
    ))

    # --- Example 4.34: d/dx[e^x sin(x)] at x=0 = 1 ---
    ch.add(NumericCheck(
        label="Ex 4.34: d/dx[e^x sin(x)] at x=0 = 1",
        section="9",
        stated=1.0,
        computed=math.exp(0) * (math.sin(0) + math.cos(0)),
        tolerance=1e-12,
    ))

    # --- Example 4.34 intermediate: e^x*(sin x + cos x) decomposition at x=0 ---
    ch.add(NumericCheck(
        label="Ex 4.34 intermediate: e^0*sin(0)=0, e^0*cos(0)=1, sum=1",
        section="9",
        stated=1.0,
        computed=math.exp(0) * math.sin(0) + math.exp(0) * math.cos(0),
        tolerance=1e-12,
    ))

    # --- Example 4.35: d/dx[sin(x^2)] at x=1 = 2*cos(1) ---
    ch.add(NumericCheck(
        label="Ex 4.35: d/dx[sin(x^2)] at x=1 ~ 1.0806",
        section="9",
        stated=1.0806046117362795,
        computed=2.0 * math.cos(1.0),
        tolerance=1e-10,
    ))

    # --- Example 4.35 stated TypeScript output ---
    ch.add(NumericCheck(
        label="Ex 4.35: 2*cos(1) matches stated 1.0806046117362795",
        section="9",
        stated=1.0806046117362795,
        computed=2.0 * math.cos(1.0),
        tolerance=1e-15,
    ))

    # --- Example 4.36: d/dx[ln(x^2+1)] at x=1 = 1 ---
    ch.add(NumericCheck(
        label="Ex 4.36: d/dx[ln(x^2+1)] at x=1 = 1",
        section="9",
        stated=1.0,
        computed=2.0 * 1.0 / (1.0**2 + 1.0),
        tolerance=1e-12,
    ))

    # --- Example 4.36 intermediate: 2x/(x^2+1) at x=1: num=2, denom=2 ---
    ch.add(NumericCheck(
        label="Ex 4.36 intermediate: numerator 2*1=2, denominator 1+1=2, ratio=1",
        section="9",
        stated=1.0,
        computed=2.0 / 2.0,
        tolerance=1e-12,
    ))

    # --- Example 4.36: evaluate at x=2 as additional verification ---
    ch.add(NumericCheck(
        label="Ex 4.36: d/dx[ln(x^2+1)] at x=2 = 4/5 = 0.8",
        section="9",
        stated=0.8,
        computed=2.0 * 2.0 / (2.0**2 + 1.0),
        tolerance=1e-12,
    ))

    # --- Example 4.37: symbolic vs numerical comparison ---
    symbolic = 2.0 * math.cos(1.0)
    h = 1e-5
    f = lambda t: math.sin(t * t)
    central = (f(1.0 + h) - f(1.0 - h)) / (2 * h)
    forward = (f(1.0 + h) - f(1.0)) / h

    ch.add(NumericCheck(
        label="Ex 4.37: Central diff matches symbolic to ~10 digits",
        section="9",
        stated=symbolic,
        computed=central,
        tolerance=1e-8,
    ))

    ch.add(StructuralCheck(
        label="Ex 4.37: Forward diff less accurate than central diff",
        section="9",
        predicate=lambda: (
            abs(forward - symbolic) > abs(central - symbolic),
            f"Forward error {abs(forward-symbolic):.2e} should be > central error {abs(central-symbolic):.2e}"
        ),
    ))

    # --- Example 4.37: stated TypeScript central output ---
    ch.add(NumericCheck(
        label="Ex 4.37: central diff ~ 1.0806046117354583 (stated in TypeScript)",
        section="9",
        stated=symbolic,
        computed=central,
        tolerance=1e-8,
        note="TS output: 1.0806046117354583",
    ))

    # --- Example 4.37: forward diff O(h) error ---
    ch.add(StructuralCheck(
        label="Ex 4.37: forward diff error is O(h) ~ 1e-8 to 1e-7",
        section="9",
        predicate=lambda: (
            1e-9 < abs(forward - symbolic) < 1e-3,
            f"Forward error {abs(forward-symbolic):.2e} not in expected O(h) range"
        ),
    ))

    # --- Example 4.37: central diff error is O(h^2) ~ much smaller ---
    ch.add(StructuralCheck(
        label="Ex 4.37: central diff error is O(h^2), much smaller than forward",
        section="9",
        predicate=lambda: (
            abs(central - symbolic) < abs(forward - symbolic) * 1e-2,
            f"Central error {abs(central-symbolic):.2e} not sufficiently smaller than forward {abs(forward-symbolic):.2e}"
        ),
    ))

    # ===================================================================
    # LAYER 2 continued: Numerical checks for exercises
    # ===================================================================

    # --- Exercise 4.2: verify d/dx[x^2*e^x] at x=1 ---
    ch.add(NumericCheck(
        label="Ex 4.2: d/dx[x^2*e^x] at x=1 = 3e",
        section="11",
        stated=3.0 * math.e,
        computed=math.exp(1.0) * (1.0 + 2.0 * 1.0),
        tolerance=1e-12,
    ))

    # --- Exercise 4.4: d/dx[e^x/(x^2+1)] at x=0 = 1 ---
    ch.add(NumericCheck(
        label="Ex 4.4: d/dx[e^x/(x^2+1)] at x=0 = 1",
        section="11",
        stated=1.0,
        computed=(math.exp(0) * (0**2 + 1) - math.exp(0) * 2 * 0) / (0**2 + 1)**2,
        tolerance=1e-12,
    ))

    # --- Exercise 4.5: slope at (1, 3*sqrt(3)/2) on ellipse ---
    # dy/dx = -9x/(4y) = -9/(4 * 3sqrt(3)/2) = -9/(6sqrt(3)) = -sqrt(3)/2
    ch.add(NumericCheck(
        label="Ex 4.5: slope at (1, 3sqrt(3)/2) = -sqrt(3)/2",
        section="11",
        stated=-math.sqrt(3) / 2.0,
        computed=-9.0 * 1.0 / (4.0 * 3.0 * math.sqrt(3) / 2.0),
        tolerance=1e-12,
        note="dy/dx = -9x/(4y) for ellipse x^2/4+y^2/9=1",
    ))

    # --- Exercise 4.7: forward diff errors for sin(x) at x=1 ---
    _exact_cos1 = math.cos(1.0)

    def _fwd_sin(h_val):
        return (math.sin(1.0 + h_val) - math.sin(1.0)) / h_val

    ch.add(StructuralCheck(
        label="Ex 4.7: forward diff error O(h) for h=1e-1 to 1e-8 decreasing",
        section="11",
        predicate=lambda: _forward_diff_convergence(),
    ))

    ch.add(StructuralCheck(
        label="Ex 4.7: forward diff error increases for very small h (cancellation)",
        section="11",
        predicate=lambda: _forward_diff_cancellation(),
    ))

    # --- Exercise 4.8: d/dx[x^x] at x=2 = 4*(ln(2)+1) ---
    ch.add(NumericCheck(
        label="Ex 4.8: d/dx[x^x] at x=2 = 4*(ln2+1) ~ 6.7726",
        section="11",
        stated=4.0 * (math.log(2.0) + 1.0),
        computed=2.0**2.0 * (math.log(2.0) + 1.0),
        tolerance=1e-12,
    ))

    # ===================================================================
    # LAYER 2 continued: Numerical checks from Section 4 diagrams/text
    # ===================================================================

    # --- Tangent line approximation (Section 4 chart) ---
    # f(x)=x^2 at x=1, tangent y=2x-1
    ch.add(NumericCheck(
        label="Sec 4 tangent line: f(1)=1, tangent(1)=2*1-1=1 (agree at tangent point)",
        section="4",
        stated=1.0,
        computed=2.0 * 1.0 - 1.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Sec 4 tangent: f(0.5)=0.25, tangent(0.5)=0 (discrepancy=0.25)",
        section="4",
        stated=0.25,
        computed=0.5**2 - (2.0 * 0.5 - 1.0),
        tolerance=1e-12,
        note="Discrepancy between curve and tangent at x=0.5",
    ))

    ch.add(NumericCheck(
        label="Sec 4 tangent: f(2)=4, tangent(2)=3, gap=1",
        section="4",
        stated=1.0,
        computed=2.0**2 - (2.0 * 2.0 - 1.0),
        tolerance=1e-12,
        note="Gap between curve and tangent at x=2",
    ))

    # --- sin/cos chart data points (Section 4 diagram) ---
    ch.add(NumericCheck(
        label="Sec 4 chart: sin(0.5) ~ 0.479",
        section="4",
        stated=0.479,
        computed=math.sin(0.5),
        tolerance=2e-3,
        note="Chart label precision",
    ))

    ch.add(NumericCheck(
        label="Sec 4 chart: cos(0.5) ~ 0.878",
        section="4",
        stated=0.878,
        computed=math.cos(0.5),
        tolerance=2e-3,
        note="Chart label precision",
    ))

    # ===================================================================
    # LAYER 2 continued: Section 7 numerical considerations
    # ===================================================================

    # --- Optimal step sizes (Section 7) ---
    eps = 2.22e-16  # machine epsilon

    ch.add(NumericCheck(
        label="Sec 7: optimal h for forward diff ~ sqrt(eps) ~ 1.49e-8",
        section="7",
        stated=1.49e-8,
        computed=math.sqrt(eps),
        tolerance=0.02,
        note="h* ~ sqrt(epsilon)",
    ))

    ch.add(NumericCheck(
        label="Sec 7: optimal h for central diff ~ eps^(1/3) ~ 6.06e-6",
        section="7",
        stated=6.06e-6,
        computed=eps**(1.0/3.0),
        tolerance=0.02,
        note="h* ~ eps^(1/3)",
    ))

    # --- Verify central diff achieves ~10-11 digits (Section 7) ---
    ch.add(StructuralCheck(
        label="Sec 7: central diff for sin(x^2) at x=1 achieves >= 10 digits",
        section="7",
        predicate=lambda: _central_digits_check(),
    ))

    # --- Backward difference (Algorithm 4.32) ---
    backward = (f(1.0) - f(1.0 - h)) / h
    ch.add(NumericCheck(
        label="Alg 4.32: backward diff for sin(x^2) at x=1 matches symbolic",
        section="6",
        stated=symbolic,
        computed=backward,
        tolerance=1e-4,
        note="O(h) accuracy for backward difference",
    ))

    ch.add(StructuralCheck(
        label="Alg 4.32: backward diff same order as forward diff",
        section="6",
        predicate=lambda: (
            abs(backward - symbolic) > abs(central - symbolic),
            f"Backward error {abs(backward-symbolic):.2e} should be > central error {abs(central-symbolic):.2e}"
        ),
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Theorem 4.2: differentiable implies continuous ---
    ch.add(StructuralCheck(
        label="Thm 4.2: |x| not differentiable at 0 (left != right derivative)",
        section="4",
        predicate=lambda: _abs_not_diff_at_zero(),
    ))

    # --- Rolle's theorem (Theorem 4.24) ---
    ch.add(StructuralCheck(
        label="Thm 4.24 Rolle: f=x^2-x on [0,1], f(0)=f(1)=0, f'(c)=0 at c=0.5",
        section="4",
        predicate=lambda: (
            abs(2 * 0.5 - 1.0) < 1e-12,
            f"f'(0.5) = {2*0.5-1.0}, expected 0"
        ),
    ))

    # --- Mean Value Theorem (Theorem 4.25) ---
    ch.add(StructuralCheck(
        label="Thm 4.25 MVT: f=x^2 on [0,2], f'(c)=(4-0)/2=2, c=1",
        section="4",
        predicate=lambda: (
            abs(2 * 1.0 - 2.0) < 1e-12,
            f"f'(1) = {2*1.0}, expected 2 (MVT slope)"
        ),
    ))

    # --- L'Hopital's rule (Theorem 4.26): lim x->0 sin(x)/x = 1 ---
    ch.add(NumericCheck(
        label="Thm 4.26 L'Hopital: lim x->0 sin(x)/x = cos(0)/1 = 1",
        section="4",
        stated=1.0,
        computed=math.cos(0.0) / 1.0,
        tolerance=1e-12,
        note="0/0 form: d/dx[sin x]/d/dx[x] = cos(0)/1",
    ))

    # --- Fundamental limits used in proofs ---
    ch.add(StructuralCheck(
        label="Sec 4: lim h->0 (e^h-1)/h = 1 (used in Thm 4.14 proof)",
        section="4",
        predicate=lambda: _exp_limit_check(),
    ))

    ch.add(StructuralCheck(
        label="Sec 4: lim h->0 sin(h)/h = 1 (used in Thm 4.18 proof)",
        section="4",
        predicate=lambda: _sin_limit_check(),
    ))

    ch.add(StructuralCheck(
        label="Sec 4: lim h->0 (cos(h)-1)/h = 0 (used in Thm 4.18 proof)",
        section="4",
        predicate=lambda: _cos_limit_check(),
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 4.30: Forward Difference ---
    def _algo_forward_difference():
        """Verify forward difference f'(x) ~ (f(x+h)-f(x))/h converges O(h)."""
        f = math.sin
        x = 1.0
        exact = math.cos(1.0)
        h1 = 0.01
        h2 = 0.001
        err1 = abs((f(x + h1) - f(x)) / h1 - exact)
        err2 = abs((f(x + h2) - f(x)) / h2 - exact)
        ratio = err1 / err2
        # O(h) means ratio ~ 10 for h1/h2 = 10
        if ratio < 5 or ratio > 20:
            return (False, f"Forward diff error ratio = {ratio:.2f}, expected ~10")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.30: Forward difference is O(h) for sin'(1)=cos(1)",
        section="6",
        predicate=_algo_forward_difference,
        note="Algorithm 4.30 verified",
    ))

    # --- Algorithm 4.31: Central Difference ---
    def _algo_central_difference():
        """Verify central difference is O(h^2)."""
        f = math.sin
        x = 1.0
        exact = math.cos(1.0)
        h1 = 0.01
        h2 = 0.001
        err1 = abs((f(x + h1) - f(x - h1)) / (2 * h1) - exact)
        err2 = abs((f(x + h2) - f(x - h2)) / (2 * h2) - exact)
        ratio = err1 / err2
        # O(h^2) means ratio ~ 100 for h1/h2 = 10
        if ratio < 50 or ratio > 200:
            return (False, f"Central diff error ratio = {ratio:.2f}, expected ~100")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.31: Central difference is O(h^2) for sin'(1)=cos(1)",
        section="6",
        predicate=_algo_central_difference,
        note="Algorithm 4.31 verified",
    ))

    # --- Algorithm 4.32: Backward Difference ---
    def _algo_backward_difference():
        """Verify backward difference f'(x) ~ (f(x)-f(x-h))/h converges O(h)."""
        f = math.exp
        x = 1.0
        exact = math.exp(1.0)
        h1 = 0.01
        h2 = 0.001
        err1 = abs((f(x) - f(x - h1)) / h1 - exact)
        err2 = abs((f(x) - f(x - h2)) / h2 - exact)
        ratio = err1 / err2
        if ratio < 5 or ratio > 20:
            return (False, f"Backward diff error ratio = {ratio:.2f}, expected ~10")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.32: Backward difference is O(h) for exp'(1)=e",
        section="6",
        predicate=_algo_backward_difference,
        note="Algorithm 4.32 verified",
    ))

    # --- Algorithm 4.29: Symbolic Differentiation ---
    def _algo_symbolic_diff():
        """Verify symbolic differentiation via recursive tree transformation."""
        import sympy as sp
        x = sp.Symbol('x')

        # Power rule: d/dx[x^3] = 3x^2
        expr1 = x**3
        d1 = sp.diff(expr1, x)
        if sp.simplify(d1 - 3*x**2) != 0:
            return (False, f"d/dx[x^3] = {d1}, expected 3x^2")

        # Product rule: d/dx[x*sin(x)] = sin(x) + x*cos(x)
        expr2 = x * sp.sin(x)
        d2 = sp.diff(expr2, x)
        expected2 = sp.sin(x) + x * sp.cos(x)
        if sp.simplify(d2 - expected2) != 0:
            return (False, f"d/dx[x*sin(x)] = {d2}")

        # Chain rule: d/dx[exp(x^2)] = 2x*exp(x^2)
        expr3 = sp.exp(x**2)
        d3 = sp.diff(expr3, x)
        expected3 = 2 * x * sp.exp(x**2)
        if sp.simplify(d3 - expected3) != 0:
            return (False, f"d/dx[exp(x^2)] = {d3}")

        # Quotient rule: d/dx[sin(x)/x] = (x*cos(x) - sin(x))/x^2
        expr4 = sp.sin(x) / x
        d4 = sp.diff(expr4, x)
        expected4 = (x * sp.cos(x) - sp.sin(x)) / x**2
        if sp.simplify(d4 - expected4) != 0:
            return (False, f"d/dx[sin(x)/x] = {d4}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 4.29: Symbolic differentiation (power, product, chain, quotient rules)",
        section="6",
        predicate=_algo_symbolic_diff,
        note="Algorithm 4.29 verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _constant_rule():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(sp.Integer(7), x)  # should be 0


def _power_rule():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(x**5, x) - 5*x**4  # verify for n=5


def _power_rule_fractional():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    return sp.simplify(sp.diff(x**sp.Rational(3, 2), x) - sp.Rational(3, 2)*x**sp.Rational(1, 2))


def _sum_rule():
    import sympy as sp
    x = sp.Symbol('x')
    f = sp.sin(x)
    g = x**3
    lhs = sp.diff(f + g, x)
    rhs = sp.diff(f, x) + sp.diff(g, x)
    return sp.expand(lhs - rhs)


def _difference_rule():
    import sympy as sp
    x = sp.Symbol('x')
    f = sp.exp(x)
    g = x**2
    lhs = sp.diff(f - g, x)
    rhs = sp.diff(f, x) - sp.diff(g, x)
    return sp.expand(lhs - rhs)


def _product_rule():
    import sympy as sp
    x = sp.Symbol('x')
    f = sp.exp(x)
    g = sp.sin(x)
    lhs = sp.diff(f*g, x)
    rhs = sp.diff(f, x)*g + f*sp.diff(g, x)
    return sp.expand(lhs - rhs)


def _quotient_rule():
    import sympy as sp
    x = sp.Symbol('x')
    f = sp.sin(x)
    g = sp.cos(x)
    lhs = sp.diff(f/g, x)
    rhs = (sp.diff(f, x)*g - f*sp.diff(g, x)) / g**2
    return sp.simplify(lhs - rhs)


def _chain_rule():
    import sympy as sp
    x = sp.Symbol('x')
    # d/dx[sin(x^2)] = cos(x^2)*2x
    lhs = sp.diff(sp.sin(x**2), x)
    rhs = sp.cos(x**2) * 2*x
    return sp.expand(lhs - rhs)


def _exp_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(sp.exp(x), x) - sp.exp(x)


def _ln_derivative():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    return sp.diff(sp.ln(x), x) - 1/x


def _general_exp_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    a = sp.Symbol('a', positive=True)
    return sp.simplify(sp.diff(a**x, x) - a**x * sp.ln(a))


def _general_log_derivative():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    a = sp.Symbol('a', positive=True)
    # log_a(x) = ln(x)/ln(a)
    return sp.simplify(sp.diff(sp.log(x, a), x) - 1/(x * sp.ln(a)))


def _sin_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(sp.sin(x), x) - sp.cos(x)


def _cos_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(sp.cos(x), x) - (-sp.sin(x))


def _tan_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.simplify(sp.diff(sp.tan(x), x) - 1/sp.cos(x)**2)


def _abs_derivative():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    # For x > 0: d/dx[|x|] = 1 = x/|x| = x/x = 1
    return sp.simplify(sp.diff(sp.Abs(x), x) - x/sp.Abs(x))


def _sqrt_derivative():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    return sp.diff(sp.sqrt(x), x) - 1/(2*sp.sqrt(x))


def _log_diff_rule():
    """F4.16: d/dx[f(x)^g(x)] = f^g * [g'*ln(f) + g*f'/f]."""
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    # Verify with f(x) = x, g(x) = x  =>  x^x
    fg = x**x
    lhs = sp.diff(fg, x)
    rhs = fg * (1 * sp.ln(x) + x * (1/x))  # g'=1, f'=1, ln(f)=ln(x), g=x, f=x
    return sp.simplify(lhs - rhs)


def _linearity_check():
    import sympy as sp
    x = sp.Symbol('x')
    a, b = sp.Rational(3), sp.Rational(-2)
    f = sp.sin(x)
    g = x**4
    lhs = sp.diff(a*f + b*g, x)
    rhs = a*sp.diff(f, x) + b*sp.diff(g, x)
    return sp.expand(lhs - rhs)


def _second_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(x**3, x, 2) - 6*x


def _third_derivative():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.diff(x**4, x, 3) - 24*x


def _tan_via_quotient():
    """Verify tan derivative via quotient rule: (cos^2+sin^2)/cos^2 = 1/cos^2."""
    import sympy as sp
    x = sp.Symbol('x')
    # d/dx[sin/cos] via quotient rule
    lhs = sp.diff(sp.sin(x)/sp.cos(x), x)
    rhs = 1/sp.cos(x)**2
    return sp.simplify(lhs - rhs)


def _x_to_x_derivative():
    import sympy as sp
    x = sp.Symbol('x', positive=True)
    lhs = sp.diff(x**x, x)
    rhs = x**x * (sp.ln(x) + 1)
    return sp.simplify(lhs - rhs)


def _implicit_circle():
    """Implicit differentiation of x^2 + y^2 = 1 => dy/dx = -x/y."""
    import sympy as sp
    x = sp.Symbol('x')
    y = sp.Function('y')(x)
    # Differentiate x^2 + y^2 - 1 = 0 w.r.t. x
    eq = x**2 + y**2 - 1
    d_eq = sp.diff(eq, x)
    # d_eq = 2x + 2y*y'
    # Solve for y' => y' = -x/y
    dy_dx = sp.solve(d_eq, sp.diff(y, x))[0]
    expected = -x / y
    return sp.simplify(dy_dx - expected)


def _exercise_10_1():
    import sympy as sp
    x = sp.Symbol('x')
    return sp.expand(sp.diff(5*x**3 - 2*x + 7, x) - (15*x**2 - 2))


def _exercise_10_2():
    import sympy as sp
    x = sp.Symbol('x')
    lhs = sp.diff(x**2 * sp.exp(x), x)
    rhs = sp.exp(x) * (x**2 + 2*x)
    return sp.expand(lhs - rhs)


def _exercise_10_3():
    import sympy as sp
    x = sp.Symbol('x')
    lhs = sp.diff(sp.cos(3*x), x)
    rhs = -3*sp.sin(3*x)
    return sp.expand(lhs - rhs)


def _exercise_10_4():
    import sympy as sp
    x = sp.Symbol('x')
    lhs = sp.diff(sp.exp(x) / (x**2 + 1), x)
    rhs = (sp.diff(sp.exp(x), x) * (x**2 + 1) - sp.exp(x) * sp.diff(x**2 + 1, x)) / (x**2 + 1)**2
    return sp.simplify(lhs - rhs)


def _exercise_10_5():
    """Ellipse x^2/4 + y^2/9 = 1 => dy/dx = -9x/(4y)."""
    import sympy as sp
    x = sp.Symbol('x')
    y = sp.Function('y')(x)
    eq = x**2 / 4 + y**2 / 9 - 1
    d_eq = sp.diff(eq, x)
    dy_dx = sp.solve(d_eq, sp.diff(y, x))[0]
    expected = -sp.Rational(9, 4) * x / y
    return sp.simplify(dy_dx - expected)


def _exercise_10_6():
    """d^4/dx^4[e^(3x)] = 3^4 * e^(3x) = 81*e^(3x)."""
    import sympy as sp
    x = sp.Symbol('x')
    return sp.simplify(sp.diff(sp.exp(3*x), x, 4) - 81*sp.exp(3*x))


# ---------------------------------------------------------------------------
# Structural / numerical helpers
# ---------------------------------------------------------------------------

def _forward_diff_convergence():
    """Exercise 4.7: forward diff error decreases as h decreases (until cancellation)."""
    exact = math.cos(1.0)
    h_values = [1e-1, 1e-3, 1e-5, 1e-8]
    errors = [abs((math.sin(1.0 + h) - math.sin(1.0)) / h - exact) for h in h_values]
    # Each error should be smaller than the previous (convergence)
    for i in range(1, len(errors)):
        if errors[i] >= errors[i-1]:
            return (False, f"Error at h={h_values[i]:.0e} ({errors[i]:.2e}) >= error at h={h_values[i-1]:.0e} ({errors[i-1]:.2e})")
    return (True, "")


def _forward_diff_cancellation():
    """Exercise 4.7: for very small h, cancellation increases the error."""
    exact = math.cos(1.0)
    err_1e8 = abs((math.sin(1.0 + 1e-8) - math.sin(1.0)) / 1e-8 - exact)
    err_1e15 = abs((math.sin(1.0 + 1e-15) - math.sin(1.0)) / 1e-15 - exact)
    ok = err_1e15 > err_1e8
    return (ok, f"Error at h=1e-15 ({err_1e15:.2e}) should be > error at h=1e-8 ({err_1e8:.2e})")


def _central_digits_check():
    """Verify central difference achieves >= 10 significant digits for sin(x^2) at x=1."""
    exact = 2.0 * math.cos(1.0)
    h = 1e-5
    f = lambda t: math.sin(t * t)
    central = (f(1.0 + h) - f(1.0 - h)) / (2 * h)
    rel_err = abs(central - exact) / abs(exact)
    digits = -math.log10(rel_err) if rel_err > 0 else 16
    ok = digits >= 9.5
    return (ok, f"Central diff achieved {digits:.1f} digits, expected >= ~10")


def _abs_not_diff_at_zero():
    """Left-hand derivative of |x| at 0 is -1, right-hand is +1."""
    h = 1e-10
    left = (abs(0 - h) - abs(0)) / (-h)
    right = (abs(0 + h) - abs(0)) / h
    ok = abs(left - (-1.0)) < 1e-6 and abs(right - 1.0) < 1e-6 and abs(left - right) > 1.5
    return (ok, f"Left deriv={left:.4f}, right deriv={right:.4f}, should be -1 and +1")


def _exp_limit_check():
    """lim h->0 (e^h - 1)/h = 1."""
    h = 1e-10
    val = (math.exp(h) - 1.0) / h
    ok = abs(val - 1.0) < 1e-5
    return (ok, f"(e^h-1)/h = {val}, expected 1.0")


def _sin_limit_check():
    """lim h->0 sin(h)/h = 1."""
    h = 1e-10
    val = math.sin(h) / h
    ok = abs(val - 1.0) < 1e-5
    return (ok, f"sin(h)/h = {val}, expected 1.0")


def _cos_limit_check():
    """lim h->0 (cos(h)-1)/h = 0."""
    h = 1e-8
    val = (math.cos(h) - 1.0) / h
    ok = abs(val) < 1e-5
    return (ok, f"(cos(h)-1)/h = {val}, expected 0")
