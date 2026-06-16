# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 23: Operator Algebra — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(23, "Operator Algebra")

    # ===================================================================
    # LAYER 1: Symbolic — key identities and formulas
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Canonical commutator: [D, M_x] = I",
        section="5",
        identity=lambda: _canonical_commutator(),
        note="Example 3.18 / Theorem [D, M_x] = I",
    ))

    ch.add(SymbolicCheck(
        label="[D, M_{x^n}] = n*M_{x^{n-1}} for n=3",
        section="5",
        identity=lambda: _generalized_commutator(),
        note="Section 5 identity",
    ))

    ch.add(SymbolicCheck(
        label="Commutator antisymmetry: [A,B] = -[B,A]",
        section="5",
        identity=lambda: _commutator_antisymmetry(),
        note="Remark 3.20(a)",
    ))

    ch.add(SymbolicCheck(
        label="Exponential shift: e^{aD}f(x) = f(x+a) for f=x^3, a=1",
        section="5",
        zero_expr=lambda: _exponential_shift(),
        note="Theorem 3.25",
    ))

    ch.add(SymbolicCheck(
        label="p(D)(e^{lambda*x}) = p(lambda)*e^{lambda*x}",
        section="5",
        zero_expr=lambda: _polynomial_operator_exponential(),
        note="Polynomial operator identity (Section 5)",
    ))

    ch.add(SymbolicCheck(
        label="Operator polynomial factoring: (D+I)(D+2I) = D^2+3D+2I",
        section="5",
        zero_expr=lambda: _operator_polynomial_factoring(),
        note="Remark 3.16 / Example 8.2",
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # --- Example 8.1: (D + 2I)(e^{3x}) = 5*e^{3x} ---
    # At x = 0: e^{3*0} = 1, so result = 5
    ch.add(NumericCheck(
        label="Ex 8.1: (D+2I)(e^{3x}) at x=0 = 5",
        section="9.1",
        stated=5.0,
        computed=lambda: 3 * math.exp(0) + 2 * math.exp(0),
        tolerance=1e-12,
    ))
    # At x = 1: e^3 ~ 20.0855, 5*e^3 ~ 100.428
    ch.add(NumericCheck(
        label="Ex 8.1: (D+2I)(e^{3x}) at x=1 = 5*e^3",
        section="9.1",
        stated=5 * math.exp(3),
        computed=lambda: 3 * math.exp(3) + 2 * math.exp(3),
        tolerance=1e-10,
    ))

    # --- Example 8.2: p(D)(e^{-x}) = 0 for p(D) = D^2 + 3D + 2I ---
    # D(e^{-x}) = -e^{-x}, D^2(e^{-x}) = e^{-x}
    # p(D)(e^{-x}) = e^{-x} - 3e^{-x} + 2e^{-x} = 0
    ch.add(NumericCheck(
        label="Ex 8.2: p(D)(e^{-x}) = 0 at x=1",
        section="9.2",
        stated=0.0,
        computed=lambda: math.exp(-1) + 3 * (-math.exp(-1)) + 2 * math.exp(-1),
        tolerance=1e-12,
    ))
    # Also for e^{-2x}: D=-2e^{-2x}, D^2=4e^{-2x}
    # p(D)(e^{-2x}) = 4e^{-2x} + 3*(-2e^{-2x}) + 2e^{-2x} = (4-6+2)e^{-2x} = 0
    ch.add(NumericCheck(
        label="Ex 8.2: p(D)(e^{-2x}) = 0 at x=1",
        section="9.2",
        stated=0.0,
        computed=lambda: 4 * math.exp(-2) - 6 * math.exp(-2) + 2 * math.exp(-2),
        tolerance=1e-12,
    ))

    # --- Example 8.3: AR(2) lag polynomial residual ---
    x = [10, 12, 11, 13, 14, 12, 15]
    # phi(L) = I - 0.5L - 0.3L^2
    # At t=2: 1*x[2] + (-0.5)*x[1] + (-0.3)*x[0] = 11 - 6 - 3 = 2
    ch.add(NumericCheck(
        label="Ex 8.3: phi(L)x at t=2 = 2",
        section="9.3",
        stated=2.0,
        computed=lambda: 1 * 11 + (-0.5) * 12 + (-0.3) * 10,
        tolerance=1e-12,
    ))
    # At t=3: 1*x[3] + (-0.5)*x[2] + (-0.3)*x[1] = 13 - 5.5 - 3.6 = 3.9
    ch.add(NumericCheck(
        label="Ex 8.3: phi(L)x at t=3 = 3.9",
        section="9.3",
        stated=3.9,
        computed=lambda: 1 * 13 + (-0.5) * 11 + (-0.3) * 12,
        tolerance=1e-12,
    ))

    # --- Example 8.4: Matrix operator iteration ---
    A = np.array([[0.8, 0.1], [0.2, 0.9]])
    v0 = np.array([100.0, 0.0])
    v1 = A @ v0
    v2 = A @ v1
    v3 = A @ v2

    ch.add(NumericCheck(
        label="Ex 8.4: v1[0] = 80",
        section="9.4",
        stated=80.0,
        computed=float(v1[0]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: v1[1] = 20",
        section="9.4",
        stated=20.0,
        computed=float(v1[1]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: v2[0] = 66",
        section="9.4",
        stated=66.0,
        computed=float(v2[0]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: v2[1] = 34",
        section="9.4",
        stated=34.0,
        computed=float(v2[1]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: v3[0] = 56.2",
        section="9.4",
        stated=56.2,
        computed=float(v3[0]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: v3[1] = 43.8",
        section="9.4",
        stated=43.8,
        computed=float(v3[1]),
        tolerance=1e-10,
    ))

    # --- Example 8.5: Canonical commutator on x^3 ---
    # [D, M_x](x^3) = D(x^4) - x*D(x^3) = 4x^3 - 3x^3 = x^3
    # At x=2: 8
    ch.add(NumericCheck(
        label="Ex 8.5: [D,M_x](x^3) at x=2 = 8",
        section="9.5",
        stated=8.0,
        computed=lambda: 4 * (2.0 ** 3) - 3 * (2.0 ** 3),
        tolerance=1e-12,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Jacobi identity: [A,[B,C]] + [B,[C,A]] + [C,[A,B]] = 0",
        section="5",
        predicate=lambda: _jacobi_identity(),
        note="Remark 3.20(c)",
    ))

    ch.add(StructuralCheck(
        label="Matrix operator: composition A^3 = A*A*A",
        section="5",
        predicate=lambda: _matrix_composition(),
        note="Theorem 3.10 / associativity",
    ))

    ch.add(StructuralCheck(
        label="Stochastic matrix converges to steady state",
        section="9.4",
        predicate=lambda: _stochastic_steady_state(),
        note="Example 8.4: columns sum to 1 => steady state exists",
    ))

    ch.add(StructuralCheck(
        label="Operator exponential semigroup: e^{(s+t)A} = e^{sA}*e^{tA}",
        section="5",
        predicate=lambda: _exponential_semigroup(),
        note="Theorem 3.27(b)",
    ))

    ch.add(StructuralCheck(
        label="Commutator Leibniz rule: [A,BC] = [A,B]C + B[A,C]",
        section="5",
        predicate=lambda: _commutator_leibniz(),
        note="Remark 3.20(d)",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 11.1: T = 2D + I applied to e^x and sin(x) ---
    # T(e^x) = 2*D(e^x) + e^x = 2*e^x + e^x = 3*e^x
    ch.add(NumericCheck(
        label="Ex 11.1: T(e^x) = 3*e^x at x=1",
        section="11",
        stated=3 * math.exp(1),
        computed=lambda: 2 * math.exp(1) + math.exp(1),
        tolerance=1e-12,
    ))

    # T(sin x) = 2*cos(x) + sin(x)
    ch.add(NumericCheck(
        label="Ex 11.1: T(sin x) = 2*cos(x) + sin(x) at x=pi/4",
        section="11",
        stated=2 * math.cos(math.pi / 4) + math.sin(math.pi / 4),
        computed=lambda: 2 * math.cos(math.pi / 4) + math.sin(math.pi / 4),
        tolerance=1e-12,
    ))

    # Verify symbolically
    def _ex1_T_symbolic():
        import sympy
        x = sympy.Symbol('x')
        f1 = sympy.exp(x)
        T_f1 = 2 * sympy.diff(f1, x) + f1
        f2 = sympy.sin(x)
        T_f2 = 2 * sympy.diff(f2, x) + f2
        check1 = sympy.simplify(T_f1 - 3 * sympy.exp(x))
        check2 = sympy.simplify(T_f2 - (2 * sympy.cos(x) + sympy.sin(x)))
        return sympy.Eq(check1 + check2, 0)

    ch.add(SymbolicCheck(
        label="Ex 11.1: T=2D+I on e^x and sin(x) symbolic verification",
        section="11",
        identity=_ex1_T_symbolic,
    ))

    # --- Exercise 11.2: (D+I)(D+2I) = D^2 + 3D + 2I applied to x^2 ---
    def _ex2_operator_product():
        import sympy
        x = sympy.Symbol('x')
        f = x**2
        # LHS: (D+I)(D+2I)(x^2) = (D+I)(2x + 2x^2) = 2 + 4x + 2x^2 + 2x
        inner = sympy.diff(f, x) + 2 * f  # (D+2I)(f) = 2x + 2x^2
        lhs = sympy.diff(inner, x) + inner  # (D+I)(inner) = (2 + 4x) + (2x + 2x^2)
        # RHS: D^2(x^2) + 3*D(x^2) + 2*x^2 = 2 + 6x + 2x^2
        rhs = sympy.diff(f, x, 2) + 3 * sympy.diff(f, x) + 2 * f
        return sympy.Eq(sympy.expand(lhs), sympy.expand(rhs))

    ch.add(SymbolicCheck(
        label="Ex 11.2: (D+I)(D+2I)(x^2) = (D^2+3D+2I)(x^2)",
        section="11",
        identity=_ex2_operator_product,
    ))

    # --- Exercise 11.3: Lag operator (I - 0.6L)(x_t) for x_t = t^2 at t=3 ---
    # x_t = t^2, so x_3 = 9, x_2 = 4
    # (I - 0.6L)(x_3) = x_3 - 0.6*x_2 = 9 - 0.6*4 = 9 - 2.4 = 6.6
    ch.add(NumericCheck(
        label="Ex 11.3: (I - 0.6L)(t^2) at t=3 = 9 - 0.6*4 = 6.6",
        section="11",
        stated=6.6,
        computed=lambda: 3**2 - 0.6 * 2**2,
        tolerance=1e-12,
    ))

    # --- Exercise 11.4: [D, M_{x^2}] = 2*M_x ---
    def _ex4_commutator_x2():
        import sympy
        x = sympy.Symbol('x')
        f = sympy.exp(x)  # test function
        # [D, M_{x^2}](f) = D(x^2 * f) - x^2 * D(f) = 2x*f + x^2*f' - x^2*f' = 2x*f
        dm = sympy.diff(x**2 * f, x)
        md = x**2 * sympy.diff(f, x)
        commutator = sympy.expand(dm - md)
        expected = 2 * x * f
        return sympy.Eq(commutator, expected)

    ch.add(SymbolicCheck(
        label="Ex 11.4: [D, M_{x^2}](e^x) = 2x*e^x",
        section="11",
        identity=_ex4_commutator_x2,
    ))

    # Numeric verification at x=2
    ch.add(NumericCheck(
        label="Ex 11.4: [D, M_{x^2}](e^x) at x=2 = 2*2*e^2 ~ 29.556",
        section="11",
        stated=4 * math.exp(2),
        computed=lambda: (
            (2 * 2 * math.exp(2) + 4 * math.exp(2))  # D(x^2 * e^x) = 2x*e^x + x^2*e^x
            - 4 * math.exp(2)  # x^2 * D(e^x) = x^2*e^x
        ),
        tolerance=1e-12,
    ))

    # --- Exercise 11.5: SHO factoring (D^2 + omega^2)y = 0 ---
    # Factor: (D + i*omega)(D - i*omega) = D^2 + omega^2
    # General solution: y = A*cos(omega*t) + B*sin(omega*t)
    def _ex5_sho_factoring():
        import sympy
        D_op, omega = sympy.symbols('D omega')
        factored = (D_op + sympy.I * omega) * (D_op - sympy.I * omega)
        expanded = sympy.expand(factored)
        expected = D_op**2 + omega**2
        return sympy.Eq(expanded, expected)

    ch.add(SymbolicCheck(
        label="Ex 11.5: (D+i*omega)(D-i*omega) = D^2 + omega^2",
        section="11",
        identity=_ex5_sho_factoring,
    ))

    # Verify general solution satisfies ODE
    def _ex5_sho_solution():
        import sympy
        t = sympy.Symbol('t')
        omega = sympy.Symbol('omega', positive=True)
        A, B = sympy.symbols('A B')
        y = A * sympy.cos(omega * t) + B * sympy.sin(omega * t)
        ode_residual = sympy.diff(y, t, 2) + omega**2 * y
        return sympy.Eq(sympy.simplify(ode_residual), 0)

    ch.add(SymbolicCheck(
        label="Ex 11.5: y = A*cos(wt) + B*sin(wt) satisfies D^2y + w^2*y = 0",
        section="11",
        identity=_ex5_sho_solution,
    ))

    # --- Exercise 11.6: p(D)(e^{lambda*x}) = p(lambda)*e^{lambda*x} ---
    def _ex6_exp_shift():
        import sympy
        x, lam = sympy.symbols('x lambda')
        f = sympy.exp(lam * x)
        # p(D) = D^3 - 2*D + 5*I (a general polynomial)
        d1 = sympy.diff(f, x)
        d2 = sympy.diff(f, x, 2)
        d3 = sympy.diff(f, x, 3)
        pDf = d3 - 2 * d1 + 5 * f
        p_lam = lam**3 - 2 * lam + 5
        return sympy.simplify(pDf - p_lam * f)

    ch.add(SymbolicCheck(
        label="Ex 11.6: p(D)(e^{lam*x}) = p(lam)*e^{lam*x} for p = D^3 - 2D + 5I",
        section="11",
        zero_expr=_ex6_exp_shift,
    ))

    # --- Exercise 11.7: Involution eigenvalues are +/-1 ---
    # If T^2 = I and T*v = lam*v, then T^2*v = lam^2*v = v => lam^2 = 1 => lam = +/-1
    def _ex7_involution():
        # Test with a known involution: reflection matrix [[1,0],[0,-1]]
        T = np.array([[1, 0], [0, -1]], dtype=float)
        # Verify T^2 = I
        T2 = T @ T
        I_mat = np.eye(2)
        if not np.allclose(T2, I_mat, atol=1e-15):
            return False, "T^2 != I"
        evals = np.linalg.eigvals(T)
        evals_sorted = sorted(evals.real)
        if not (abs(evals_sorted[0] - (-1)) < 1e-10 and abs(evals_sorted[1] - 1) < 1e-10):
            return False, f"Eigenvalues {evals_sorted} are not +/-1"
        # Also test with Pauli-X: [[0,1],[1,0]]
        Tx = np.array([[0, 1], [1, 0]], dtype=float)
        Tx2 = Tx @ Tx
        if not np.allclose(Tx2, I_mat, atol=1e-15):
            return False, "Pauli-X^2 != I"
        evals_x = sorted(np.linalg.eigvals(Tx).real)
        if not (abs(evals_x[0] - (-1)) < 1e-10 and abs(evals_x[1] - 1) < 1e-10):
            return False, f"Pauli-X eigenvalues {evals_x} are not +/-1"
        return True, ""

    ch.add(StructuralCheck(
        label="Ex 11.7: Involution eigenvalues are +1 and -1 (two test matrices)",
        section="11",
        predicate=_ex7_involution,
    ))

    # --- Exercise 11.8: e^{aD}(x^3) = (x+a)^3 by series expansion ---
    def _ex8_exp_shift_cubic():
        import sympy
        x, a = sympy.symbols('x a')
        f = x**3
        # e^{aD}(f) = sum_{k=0}^{3} a^k * f^{(k)}(x) / k!
        # f' = 3x^2, f'' = 6x, f''' = 6, f^{(4)} = 0
        taylor_sum = sum(
            a**k * sympy.diff(f, x, k) / sympy.factorial(k)
            for k in range(4)
        )
        shifted = (x + a)**3
        return sympy.expand(taylor_sum - shifted)

    ch.add(SymbolicCheck(
        label="Ex 11.8: e^{aD}(x^3) = (x+a)^3 via power series to 3rd order",
        section="11",
        zero_expr=_ex8_exp_shift_cubic,
    ))

    # Numeric check at x=2, a=3: (2+3)^3 = 125
    ch.add(NumericCheck(
        label="Ex 11.8: e^{3D}(x^3) at x=2 = (2+3)^3 = 125",
        section="11",
        stated=125.0,
        computed=lambda: (
            2**3                           # k=0: x^3
            + 3 * 3 * 2**2                 # k=1: a * 3x^2
            + 3**2 * 6 * 2 / 2            # k=2: a^2 * 6x / 2!
            + 3**3 * 6 / 6                 # k=3: a^3 * 6 / 3!
        ),
        tolerance=1e-12,
    ))

    # ==================================================================
    # Remark 3.4: N(f) = f^2 is nonlinear
    # ==================================================================

    def _remark_3_4_nonlinear_squaring():
        # N(f+g) = (f+g)^2 != f^2 + g^2 = N(f) + N(g)
        # Test with specific functions at sample points
        x_vals = np.linspace(0, 2, 50)
        f = np.sin(x_vals)
        g = np.cos(x_vals)
        N_f_plus_g = (f + g) ** 2
        N_f_plus_N_g = f ** 2 + g ** 2
        # These should NOT be equal (unless f*g = 0 everywhere)
        diff = np.max(np.abs(N_f_plus_g - N_f_plus_N_g))
        if diff < 1e-10:
            return (False, "N(f+g) = N(f)+N(g), but squaring should be nonlinear")
        # The difference is 2*f*g (cross term)
        expected_diff = 2 * f * g
        if not np.allclose(N_f_plus_g - N_f_plus_N_g, expected_diff, atol=1e-12):
            return (False, "N(f+g) - N(f) - N(g) != 2fg")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: N(f)=f^2 is nonlinear: (f+g)^2 != f^2+g^2",
        section="3",
        predicate=_remark_3_4_nonlinear_squaring,
        note="Remark 3.4: nonlinear operator example",
    ))

    # ==================================================================
    # Remark 3.11: Non-commutativity AB != BA for dim >= 2
    # ==================================================================

    def _remark_3_11_noncommutativity():
        A = np.array([[1, 2], [3, 4]], dtype=float)
        B = np.array([[0, 1], [1, 0]], dtype=float)
        AB = A @ B
        BA = B @ A
        if np.allclose(AB, BA):
            return (False, "AB = BA, but expected non-commutativity")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.11: AB != BA for 2x2 matrices",
        section="3",
        predicate=_remark_3_11_noncommutativity,
        note="Remark 3.11: operator algebra is non-commutative",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Generic Operator Composition ---
    def _algo_operator_composition():
        """Verify (T2 o T1)(f)(x) = T2(T1(f))(x)."""
        # T1 = D (differentiation), T2 = D (differentiation)
        # (D o D)(x^3) = D(3x^2) = 6x. At x=2: 12
        import sympy as sp
        x = sp.Symbol('x')
        f = x ** 3
        d1 = sp.diff(f, x)
        d2 = sp.diff(d1, x)
        val = float(d2.subs(x, 2))
        if abs(val - 12.0) > 1e-10:
            return (False, f"D^2(x^3) at x=2 = {val}, expected 12")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Operator composition D^2(x^3) = 6x verified",
        section="6",
        predicate=_algo_operator_composition,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.3: Applying p(L) to a sequence ---
    def _algo_polynomial_lag_operator():
        """Verify p(L) applied to a sequence: (1 - 0.5L)x = y."""
        # AR(1): y_t = x_t - 0.5*x_{t-1}
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # p(L) = 1 - 0.5*L, apply to x
        y = [x[0]]  # first value: x[0] (L has no x_{-1})
        for t in range(1, len(x)):
            y.append(x[t] - 0.5 * x[t - 1])

        # Verify: y[1] = 2 - 0.5*1 = 1.5
        if abs(y[1] - 1.5) > 1e-10:
            return (False, f"y[1] = {y[1]}, expected 1.5")
        # y[5] = 6 - 0.5*5 = 3.5
        if abs(y[5] - 3.5) > 1e-10:
            return (False, f"y[5] = {y[5]}, expected 3.5")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Polynomial lag operator (1-0.5L) applied to sequence",
        section="6",
        predicate=_algo_polynomial_lag_operator,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.2: Applying p(D) to a Symbolic Expression ---
    def _algo_polynomial_diff_operator():
        """Verify polynomial differential operator p(D) applied symbolically."""
        import sympy as sp
        x = sp.Symbol('x')

        # p(D) = D^2 + 3D + 2 applied to e^x
        # D(e^x) = e^x, D^2(e^x) = e^x
        # p(D)[e^x] = e^x + 3*e^x + 2*e^x = 6*e^x
        f = sp.exp(x)
        coeffs = [2, 3, 1]  # a_0=2, a_1=3, a_2=1 => 2I + 3D + D^2
        result = sum(c * sp.diff(f, x, k) for k, c in enumerate(coeffs))
        expected = 6 * sp.exp(x)
        if sp.simplify(result - expected) != 0:
            return (False, f"p(D)[e^x] = {result}, expected {expected}")

        # p(D) = D^2 - 1 applied to sin(x)
        # D(sin(x)) = cos(x), D^2(sin(x)) = -sin(x)
        # p(D)[sin(x)] = -sin(x) - sin(x) = -2*sin(x)
        f2 = sp.sin(x)
        coeffs2 = [-1, 0, 1]  # -I + D^2
        result2 = sum(c * sp.diff(f2, x, k) for k, c in enumerate(coeffs2))
        expected2 = -2 * sp.sin(x)
        if sp.simplify(result2 - expected2) != 0:
            return (False, f"(D^2-1)[sin(x)] = {result2}, expected {expected2}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Polynomial operator p(D) applied to exp(x) and sin(x)",
        section="6",
        predicate=_algo_polynomial_diff_operator,
        note="Algorithm 5.2 verified",
    ))

    # --- Remark 3.19: [D, M_x] = I (commutator of derivative and multiplication) ---
    def _remark_3_19_commutator():
        """Verify [D, M_x]f = f for several test functions."""
        import sympy as sp
        x = sp.Symbol('x')
        test_funcs = [sp.exp(x), sp.sin(x), x**3, sp.log(x + 1)]
        for f in test_funcs:
            D_Mx_f = sp.diff(x * f, x)       # D(x*f)
            Mx_D_f = x * sp.diff(f, x)       # x*D(f)
            commutator = sp.simplify(D_Mx_f - Mx_D_f - f)
            if commutator != 0:
                return (False, f"[D, M_x]({f}) - f = {commutator}, expected 0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.19: [D, M_x] = I verified for exp, sin, x^3, log(x+1)",
        section="3.19",
        predicate=_remark_3_19_commutator,
        note="Remark 3.19: canonical commutation relation",
    ))

    # --- Remark 3.26: Delta = I - e^{-D} expanded as series in D ---
    def _remark_3_26_delta_expansion():
        """Verify Delta = D - D^2/2! + D^3/3! - ... numerically on a sequence."""
        # For f(x) = x^3, Delta f = f(x) - f(x-1) = x^3 - (x-1)^3 = 3x^2 - 3x + 1
        # Series: D*f - D^2*f/2 + D^3*f/6 - D^4*f/24 + ...
        import sympy as sp
        x = sp.Symbol('x')
        f = x**3
        delta_exact = sp.expand(f - f.subs(x, x - 1))
        # Truncated series in D
        series_approx = sp.Integer(0)
        for n in range(1, 10):
            term = (-1)**(n+1) * sp.diff(f, x, n) / sp.factorial(n)
            series_approx += term
        series_approx = sp.expand(series_approx)
        diff = sp.simplify(delta_exact - series_approx)
        if diff != 0:
            return (False, f"Delta expansion mismatch: diff = {diff}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.26: Delta = D - D^2/2! + D^3/3! - ... verified for x^3",
        section="3.26",
        predicate=_remark_3_26_delta_expansion,
        note="Remark 3.26: continuous-discrete connection",
    ))

    return ch


# -------------------------------------------------------------------
# Symbolic helpers
# -------------------------------------------------------------------

def _canonical_commutator():
    """[D, M_x] = I: verify DM_x(f) - M_xD(f) = f for generic polynomial."""
    import sympy
    x = sympy.Symbol('x')
    f = x ** 4 + 3 * x ** 2 - 2 * x + 7
    dm = sympy.diff(x * f, x)  # D(M_x(f)) = D(x*f)
    md = x * sympy.diff(f, x)  # M_x(D(f)) = x*f'
    commutator = sympy.expand(dm - md)
    return sympy.Eq(commutator, f)


def _generalized_commutator():
    """[D, M_{x^n}] = n*M_{x^{n-1}}: verify for n=3."""
    import sympy
    x = sympy.Symbol('x')
    n = 3
    f = x ** 2 + 5 * x - 1
    dm = sympy.diff(x ** n * f, x)
    md = x ** n * sympy.diff(f, x)
    commutator = sympy.expand(dm - md)
    expected = n * x ** (n - 1) * f
    return sympy.Eq(sympy.expand(commutator), sympy.expand(expected))


def _commutator_antisymmetry():
    """[A,B] = -[B,A] for matrix operators."""
    import sympy
    A = sympy.Matrix([[1, 2], [3, 4]])
    B = sympy.Matrix([[0, 1], [1, 0]])
    ab = A * B - B * A
    ba = B * A - A * B
    return sympy.Eq(ab, -ba)


def _exponential_shift():
    """e^{aD}f(x) = f(x+a): verify sum a^k f^{(k)}(x)/k! = f(x+a) for f=x^3, a=1."""
    import sympy
    x, a = sympy.symbols('x a')
    f = x ** 3
    # Taylor expansion of f at x, shift by a=1
    taylor = sum(sympy.diff(f, x, k).subs(x, x) * a ** k / sympy.factorial(k)
                 for k in range(4))  # x^3 is degree 3, so 4 terms suffice
    shifted = (x + a) ** 3
    return sympy.expand(taylor - shifted)


def _polynomial_operator_exponential():
    """p(D)(e^{lam*x}) = p(lam)*e^{lam*x} for p = D^2 + 3D + 2."""
    import sympy
    x, lam = sympy.symbols('x lambda')
    f = sympy.exp(lam * x)
    d1 = sympy.diff(f, x)      # lam * e^{lam*x}
    d2 = sympy.diff(f, x, 2)   # lam^2 * e^{lam*x}
    pDf = d2 + 3 * d1 + 2 * f
    p_lam = lam ** 2 + 3 * lam + 2
    return sympy.simplify(pDf - p_lam * f)


def _operator_polynomial_factoring():
    """(D+I)(D+2I) applied to f should equal (D^2+3D+2I)f."""
    import sympy
    x = sympy.Symbol('x')
    f = sympy.sin(x) + x ** 3
    # (D+2I)f = f' + 2f
    inner = sympy.diff(f, x) + 2 * f
    # (D+I)(result) = D(inner) + inner
    lhs = sympy.diff(inner, x) + inner
    # D^2f + 3Df + 2f
    rhs = sympy.diff(f, x, 2) + 3 * sympy.diff(f, x) + 2 * f
    return sympy.expand(lhs - rhs)


# -------------------------------------------------------------------
# Structural helpers
# -------------------------------------------------------------------

def _jacobi_identity():
    """[A,[B,C]] + [B,[C,A]] + [C,[A,B]] = 0 for 3x3 matrices."""
    rng = np.random.default_rng(123)
    A = rng.standard_normal((3, 3))
    B = rng.standard_normal((3, 3))
    C = rng.standard_normal((3, 3))

    def comm(X, Y):
        return X @ Y - Y @ X

    result = comm(A, comm(B, C)) + comm(B, comm(C, A)) + comm(C, comm(A, B))
    if not np.allclose(result, 0, atol=1e-10):
        return False, f"Max deviation: {np.max(np.abs(result)):.2e}"
    return True, ""


def _matrix_composition():
    """A^3 computed via repeated multiplication matches np.linalg.matrix_power."""
    A = np.array([[0.8, 0.1], [0.2, 0.9]])
    direct = A @ A @ A
    power = np.linalg.matrix_power(A, 3)
    if not np.allclose(direct, power, atol=1e-12):
        return False, f"Max diff: {np.max(np.abs(direct - power)):.2e}"
    return True, ""


def _stochastic_steady_state():
    """Stochastic matrix converges; steady state from eigenvector."""
    A = np.array([[0.8, 0.1], [0.2, 0.9]])
    v = np.array([100.0, 0.0])
    for _ in range(200):
        v = A @ v
    # Steady state: eigenvector for eigenvalue 1
    # Column sums = 1, so A is stochastic. Steady state pi satisfies A*pi = pi.
    # pi = [1/3, 2/3] * 100 = [33.33, 66.67]
    expected = np.array([100.0 / 3, 200.0 / 3])
    if not np.allclose(v, expected, atol=0.1):
        return False, f"Steady state {v} != expected {expected}"
    return True, ""


def _exponential_semigroup():
    """e^{(s+t)A} = e^{sA} e^{tA} for a 2x2 matrix."""
    from scipy.linalg import expm
    A = np.array([[1.0, 0.5], [-0.3, 0.8]])
    s, t = 0.3, 0.7
    lhs = expm((s + t) * A)
    rhs = expm(s * A) @ expm(t * A)
    if not np.allclose(lhs, rhs, atol=1e-10):
        return False, f"Max diff: {np.max(np.abs(lhs - rhs)):.2e}"
    return True, ""


def _commutator_leibniz():
    """[A, BC] = [A,B]C + B[A,C] for matrices."""
    rng = np.random.default_rng(456)
    A = rng.standard_normal((3, 3))
    B = rng.standard_normal((3, 3))
    C = rng.standard_normal((3, 3))

    def comm(X, Y):
        return X @ Y - Y @ X

    lhs = comm(A, B @ C)
    rhs = comm(A, B) @ C + B @ comm(A, C)
    if not np.allclose(lhs, rhs, atol=1e-10):
        return False, f"Max diff: {np.max(np.abs(lhs - rhs)):.2e}"
    return True, ""
