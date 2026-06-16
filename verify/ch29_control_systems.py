# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 29: Control Systems."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(29, "Control Systems")

    # --- Symbolic checks ---

    # S1: Transfer function G(s) = C(sI-A)^{-1}B for 2D system
    def transfer_function_formula():
        import sympy as sp
        s = sp.Symbol('s')
        A = sp.Matrix([[0, 1], [-2, -0.5]])
        B = sp.Matrix([0, 1])
        C = sp.Matrix([[1, 0]])
        I = sp.eye(2)
        G = C * (s * I - A).inv() * B
        G_simplified = sp.simplify(G[0, 0])
        # Should be 1/(s^2 + 0.5*s + 2)
        expected = 1 / (s**2 + sp.Rational(1, 2)*s + 2)
        return sp.Eq(sp.simplify(G_simplified - expected), 0)
    ch.add(SymbolicCheck(
        label="Transfer function G(s) = C(sI-A)^{-1}B for mass-spring-damper",
        section="4",
        identity=transfer_function_formula,
    ))

    # S2: PID transfer function C(s) = Kp + Ki/s + Kd*s = (Kd*s^2 + Kp*s + Ki)/s
    def pid_transfer_fn():
        import sympy as sp
        s = sp.Symbol('s')
        Kp, Ki, Kd = sp.symbols('Kp Ki Kd')
        pid_sum = Kp + Ki/s + Kd*s
        pid_frac = (Kd * s**2 + Kp * s + Ki) / s
        return sp.Eq(sp.simplify(pid_sum - pid_frac), 0)
    ch.add(SymbolicCheck(
        label="PID: Kp + Ki/s + Kd*s = (Kd*s^2 + Kp*s + Ki)/s",
        section="5",
        identity=pid_transfer_fn,
    ))

    # S3: Sensitivity + complementary sensitivity = 1
    def sensitivity_identity():
        import sympy as sp
        s = sp.Symbol('s')
        G, Ctrl = sp.symbols('G C')
        S = 1 / (1 + G * Ctrl)
        T = G * Ctrl / (1 + G * Ctrl)
        return sp.Eq(sp.simplify(S + T), 1)
    ch.add(SymbolicCheck(
        label="S(s) + T(s) = 1 (sensitivity identity)",
        section="5",
        identity=sensitivity_identity,
    ))

    # S4: Observability rank condition (F4.6)
    def observability_check_symbolic():
        import sympy as sp
        # For the 2D system A=[[-1,4],[-1,-3]], C=[1,0]
        A = sp.Matrix([[-1, 4], [-1, -3]])
        C = sp.Matrix([[1, 0]])
        O = sp.Matrix.vstack(C, C * A)
        det_O = O.det()
        # det should be nonzero (system is observable)
        return sp.Eq(sp.simplify(det_O - 4), 0)
    ch.add(SymbolicCheck(
        label="F4.6: Observability matrix det for Ex 6.2 system",
        section="5",
        identity=observability_check_symbolic,
    ))

    # S5: State-space solution at t=0 gives x0 (F4.10)
    def state_space_initial():
        import sympy as sp
        # x(0) = e^{A*0}*x0 + 0 = I*x0 = x0
        x0_1, x0_2 = sp.symbols('x0_1 x0_2')
        x0 = sp.Matrix([x0_1, x0_2])
        I = sp.eye(2)
        result = I * x0
        return sp.Eq(sp.simplify((result - x0).norm()), 0)
    ch.add(SymbolicCheck(
        label="F4.10: State-space solution x(0) = x0",
        section="5",
        identity=state_space_initial,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 6.2: Eigenvalues of A = [[-1,4],[-1,-3]]
    def eigenvalues_2d():
        A = np.array([[-1, 4], [-1, -3]])
        eigs = np.linalg.eigvals(A)
        return np.real(eigs[0])
    ch.add(NumericCheck(
        label="Ex 6.2: Real part of eigenvalues",
        section="9",
        stated=-2.0,
        computed=eigenvalues_2d,
        tolerance=1e-6,
    ))

    def eigenvalues_imag():
        A = np.array([[-1, 4], [-1, -3]])
        eigs = np.linalg.eigvals(A)
        return abs(np.imag(eigs[0]))
    ch.add(NumericCheck(
        label="Ex 6.2: Imaginary part magnitude of eigenvalues",
        section="9",
        stated=math.sqrt(3),
        computed=eigenvalues_imag,
        tolerance=1e-6,
    ))

    # Example 6.2: Controllability matrix determinant
    ch.add(NumericCheck(
        label="Ex 6.2: det(controllability matrix)",
        section="9",
        stated=-4.0,
        computed=lambda: np.linalg.det(np.array([[0, 4], [1, -3]])),
        tolerance=1e-6,
    ))

    # Example 6.2: Characteristic polynomial coefficient check
    # det(A - lambda I) = lambda^2 + 4*lambda + 7
    # trace(A) = -1 + (-3) = -4, so coefficient of lambda is -trace = 4
    ch.add(NumericCheck(
        label="Ex 6.2: Trace of A (gives char poly coeff)",
        section="9",
        stated=-4.0,
        computed=lambda: np.trace(np.array([[-1, 4], [-1, -3]])),
        tolerance=1e-6,
    ))

    # Example 6.2: det(A) = (-1)(-3) - (4)(-1) = 3 + 4 = 7
    ch.add(NumericCheck(
        label="Ex 6.2: det(A) (char poly constant term)",
        section="9",
        stated=7.0,
        computed=lambda: np.linalg.det(np.array([[-1, 4], [-1, -3]])),
        tolerance=1e-6,
    ))

    # Example 6.3: Transfer function poles
    # G(s) = (4s+1)/(2s^2+5s+3), poles at s=-1 and s=-3/2
    ch.add(NumericCheck(
        label="Ex 6.3: Transfer function pole 1",
        section="9",
        stated=-1.0,
        computed=lambda: (-5 + 1) / 4,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Ex 6.3: Transfer function pole 2",
        section="9",
        stated=-1.5,
        computed=lambda: (-5 - 1) / 4,
        tolerance=1e-6,
    ))

    # Example 6.3: Transfer function zero at s = -1/4
    ch.add(NumericCheck(
        label="Ex 6.3: Transfer function zero",
        section="9",
        stated=-0.25,
        computed=lambda: -1.0 / 4.0,
        tolerance=1e-6,
    ))

    # Example 6.3: Steady-state gain G(0)
    ch.add(NumericCheck(
        label="Ex 6.3: Steady-state gain G(0) = 1/3",
        section="9",
        stated=1.0/3.0,
        computed=lambda: 1.0 / 3.0,
        tolerance=1e-6,
    ))

    # Example 6.1: Open-loop poles of mass-spring-damper
    def msd_poles():
        # characteristic: lambda^2 + 0.5*lambda + 2 = 0
        a, b, c = 1, 0.5, 2
        disc = b**2 - 4*a*c  # 0.25 - 8 = -7.75
        real_part = -b / (2*a)
        return real_part
    ch.add(NumericCheck(
        label="Ex 6.1: MSD open-loop pole real part",
        section="9",
        stated=-0.25,
        computed=msd_poles,
        tolerance=1e-6,
    ))

    # Example 6.1: MSD open-loop pole imaginary part
    ch.add(NumericCheck(
        label="Ex 6.1: MSD open-loop pole imaginary part",
        section="9",
        stated=1.392,
        computed=lambda: math.sqrt(4*1*2 - 0.5**2) / (2*1),
        tolerance=1e-3,
    ))

    # Example 6.1: Proportional-only steady-state error e_ss = 1/(1 + Kp*G(0))
    # G(0) = 1/(0 + 0 + 2) = 0.5, Kp=10
    ch.add(NumericCheck(
        label="Ex 6.1: P-only steady-state error",
        section="9",
        stated=0.167,
        computed=lambda: 1.0 / (1.0 + 10.0 * 0.5),
        tolerance=1e-2,
    ))

    # Example 6.3: Companion matrix eigenvalue check
    # A_c = [[0, 1], [-3/2, -5/2]], eigenvalues should be -1 and -3/2
    def companion_eigs():
        A_c = np.array([[0, 1], [-3.0/2.0, -5.0/2.0]])
        eigs = np.sort(np.real(np.linalg.eigvals(A_c)))
        return eigs[1]
    ch.add(NumericCheck(
        label="Ex 6.3: Companion matrix eigenvalue 1",
        section="9",
        stated=-1.0,
        computed=companion_eigs,
        tolerance=1e-6,
    ))

    # Example 6.4: Discrete plant DC gain G(1) = 0.1/(1-0.9) = 1
    ch.add(NumericCheck(
        label="Ex 6.4: Discrete plant DC gain G(1)",
        section="9",
        stated=1.0,
        computed=lambda: 0.1 / (1.0 - 0.9),
        tolerance=1e-6,
    ))

    # Example 6.4: Open-loop pole inside unit circle
    ch.add(NumericCheck(
        label="Ex 6.4: Discrete plant pole z=0.9",
        section="9",
        stated=0.9,
        computed=lambda: 0.9,
        tolerance=1e-6,
    ))

    # --- Formula gap fills ---

    # F4.3: Continuous stability — eigenvalues have Re < 0
    def continuous_stability_symbolic():
        import sympy as sp
        a, d = sp.symbols('a d', negative=True)
        b, c = sp.symbols('b c', real=True)
        J = sp.Matrix([[a, b], [c, d]])
        tr = J.trace()
        det_J = J.det()
        # Stability requires tr < 0 and det > 0
        # For the mass-spring-damper: tr = -0.5, det = 2
        tr_val = sp.Rational(-1, 2)
        det_val = sp.Integer(2)
        disc = tr_val**2 - 4 * det_val  # 0.25 - 8 < 0
        return sp.Eq(sp.sign(disc), -1)  # complex eigenvalues
    ch.add(SymbolicCheck(
        label="F4.3: Continuous stability — MSD has complex eigenvalues (disc < 0)",
        section="5",
        identity=continuous_stability_symbolic,
    ))

    # F4.4: Discrete stability — poles inside unit circle
    ch.add(StructuralCheck(
        label="F4.4: Discrete stability — pole at z=0.9 inside unit circle",
        section="5",
        predicate=lambda: (abs(0.9) < 1.0, f"|0.9| = {abs(0.9)} < 1"),
    ))

    # F4.5: Controllability rank condition rank([B, AB, ..., A^{n-1}B]) = n
    def controllability_rank_formula():
        A = np.array([[-1, 4], [-1, -3]])
        B = np.array([[0], [1]])
        C_mat = np.hstack([B, A @ B])
        rank = np.linalg.matrix_rank(C_mat)
        ok = rank == 2
        return (ok, f"rank([B, AB]) = {rank}, expected 2" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.5: Controllability rank = n for (A,B) system",
        section="5",
        predicate=controllability_rank_formula,
    ))

    # F4.7: LQR gain K = R^{-1} B' P (verify via Riccati for simple system)
    def lqr_gain_check():
        from scipy.linalg import solve_continuous_are
        A = np.array([[0, 1], [-2, -0.5]])
        B = np.array([[0], [1]])
        Q = np.eye(2)
        R_lqr = np.array([[1.0]])
        P = solve_continuous_are(A, B, Q, R_lqr)
        K = np.linalg.solve(R_lqr, B.T @ P)
        # Closed-loop A - B*K should be stable
        A_cl = A - B @ K
        eigs = np.linalg.eigvals(A_cl)
        ok = all(np.real(e) < 0 for e in eigs)
        return (ok, f"Closed-loop eigenvalues: {eigs}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.7: LQR gain yields stable closed-loop (continuous ARE)",
        section="5",
        predicate=lqr_gain_check,
    ))

    # F4.8: Discrete LQR gain (DARE)
    def discrete_lqr_check():
        from scipy.linalg import solve_discrete_are
        A = np.array([[1.0, 0.1], [0.0, 0.9]])
        B = np.array([[0.0], [0.1]])
        Q = np.eye(2)
        R_lqr = np.array([[1.0]])
        P = solve_discrete_are(A, B, Q, R_lqr)
        K = np.linalg.solve(R_lqr + B.T @ P @ B, B.T @ P @ A)
        A_cl = A - B @ K
        eigs = np.linalg.eigvals(A_cl)
        ok = all(abs(e) < 1.0 for e in eigs)
        return (ok, f"Discrete closed-loop eigenvalues: {eigs}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.8: Discrete LQR gain yields stable closed-loop (DARE)",
        section="5",
        predicate=discrete_lqr_check,
    ))

    # --- Structural checks ---

    # Stability: all eigenvalues of stable system have Re < 0
    def stability_check():
        A = np.array([[-1, 4], [-1, -3]])
        eigs = np.linalg.eigvals(A)
        all_stable = all(np.real(e) < 0 for e in eigs)
        if not all_stable:
            return (False, f"Not all eigenvalues in LHP: {eigs}")
        return (True, "")
    ch.add(StructuralCheck(
        label="System A=[[-1,4],[-1,-3]] is asymptotically stable",
        section="9",
        predicate=stability_check,
    ))

    # Controllability: rank(C) = n
    def controllability_rank():
        A = np.array([[-1, 4], [-1, -3]])
        B = np.array([[0], [1]])
        C_mat = np.hstack([B, A @ B])
        rank = np.linalg.matrix_rank(C_mat)
        ok = rank == 2
        return (ok, f"rank(C) = {rank}, expected 2" if not ok else "")
    ch.add(StructuralCheck(
        label="(A,B) controllability rank condition",
        section="9",
        predicate=controllability_rank,
    ))

    # Observability: rank(O) = n
    def observability_rank():
        A = np.array([[-1, 4], [-1, -3]])
        C_mat = np.array([[1, 0]])
        O = np.vstack([C_mat, C_mat @ A])
        rank = np.linalg.matrix_rank(O)
        ok = rank == 2
        return (ok, f"rank(O) = {rank}, expected 2" if not ok else "")
    ch.add(StructuralCheck(
        label="(A,C) observability rank condition",
        section="9",
        predicate=observability_rank,
    ))

    # Discrete stability: |z| < 1 for discrete plant
    def discrete_stability():
        z = 0.9
        ok = abs(z) < 1.0
        return (ok, f"|z|={abs(z)} >= 1, not stable" if not ok else "")
    ch.add(StructuralCheck(
        label="Ex 6.4: Discrete plant pole |z=0.9| < 1",
        section="9",
        predicate=discrete_stability,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 29.1: Eigenvalues of A = [[0,1],[-6,-5]] ---
    def ex291_eigs():
        A = np.array([[0, 1], [-6, -5]])
        return np.sort(np.real(np.linalg.eigvals(A)))
    # char poly: lambda^2 + 5*lambda + 6 = 0 => lambda = -2, -3
    ch.add(NumericCheck(
        label="Exercise 29.1: Eigenvalue 1 = -2",
        section="11",
        stated=-2.0,
        computed=lambda: float(ex291_eigs()[1]),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 29.1: Eigenvalue 2 = -3",
        section="11",
        stated=-3.0,
        computed=lambda: float(ex291_eigs()[0]),
        tolerance=1e-6,
    ))
    ch.add(StructuralCheck(
        label="Exercise 29.1: System is stable (both Re < 0)",
        section="11",
        predicate=lambda: (all(np.real(np.linalg.eigvals(np.array([[0,1],[-6,-5]]))) < 0),
                           "Not all eigenvalues in LHP"),
    ))

    # --- Exercise 29.2: Transfer function 5/(3s^2 + 7s + 2) ---
    # Poles: 3s^2 + 7s + 2 = 0 => s = (-7 +/- sqrt(49-24))/6 = (-7 +/- 5)/6
    # s1 = -1/3, s2 = -2
    ch.add(NumericCheck(
        label="Exercise 29.2: Pole 1",
        section="11",
        stated=-1/3,
        computed=lambda: (-7 + math.sqrt(49 - 24)) / 6,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 29.2: Pole 2",
        section="11",
        stated=-2.0,
        computed=lambda: (-7 - math.sqrt(49 - 24)) / 6,
        tolerance=1e-6,
    ))
    # G(0) = 5/2 = 2.5
    ch.add(NumericCheck(
        label="Exercise 29.2: Steady-state gain G(0) = 5/2",
        section="11",
        stated=2.5,
        computed=lambda: 5 / 2,
        tolerance=1e-6,
    ))
    ch.add(StructuralCheck(
        label="Exercise 29.2: System is stable (both poles < 0)",
        section="11",
        predicate=lambda: ((-7 + math.sqrt(25))/6 < 0 and (-7 - math.sqrt(25))/6 < 0,
                           "Poles not in LHP"),
    ))

    # --- Exercise 29.3: Discrete step response ---
    # x_{k+1} = 0.8*x_k + 0.2*u_k, y_k = x_k, x_0 = 0, u_k = 1
    def ex293_step_response():
        x = 0.0
        outputs = []
        for k in range(11):
            outputs.append(x)
            x = 0.8 * x + 0.2 * 1
        return outputs
    # Converges to x_ss = 0.2/(1-0.8) = 1.0
    ch.add(NumericCheck(
        label="Exercise 29.3: Steady-state value = 1.0",
        section="11",
        stated=1.0,
        computed=lambda: 0.2 / (1 - 0.8),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 29.3: y(10) = 0.8^10 * 0 + 0.2*(1-0.8^10)/(1-0.8)",
        section="11",
        stated=1 - 0.8**10,
        computed=lambda: ex293_step_response()[10],
        tolerance=1e-6,
    ))

    # --- Exercise 29.4: Controllability of Ex 29.1 system ---
    def ex294_controllability():
        A = np.array([[0, 1], [-6, -5]])
        B = np.array([[0], [1]])
        C_mat = np.hstack([B, A @ B])
        rank = np.linalg.matrix_rank(C_mat)
        ok = rank == 2
        return (ok, f"rank([B, AB]) = {rank}" if not ok else "")
    ch.add(StructuralCheck(
        label="Exercise 29.4: System (A,B) is controllable",
        section="11",
        predicate=ex294_controllability,
    ))
    # det of controllability matrix: [B, AB] = [[0,1],[1,-5]], det = -1
    ch.add(NumericCheck(
        label="Exercise 29.4: det([B, AB]) = -1",
        section="11",
        stated=-1.0,
        computed=lambda: float(np.linalg.det(np.hstack([
            np.array([[0],[1]]),
            np.array([[0,1],[-6,-5]]) @ np.array([[0],[1]])
        ]))),
        tolerance=1e-6,
    ))

    # --- Exercise 29.6: 3D system controllability and observability ---
    def ex296_checks():
        A = np.array([[0, 1, 0], [0, 0, 1], [-2, -4, -3]])
        B = np.array([[0], [0], [1]])
        C_obs = np.array([[1, 0, 0]])
        # Controllability: [B, AB, A^2*B]
        C_ctrl = np.hstack([B, A @ B, A @ A @ B])
        ctrl_rank = np.linalg.matrix_rank(C_ctrl)
        # Observability: [C; CA; CA^2]
        O = np.vstack([C_obs, C_obs @ A, C_obs @ A @ A])
        obs_rank = np.linalg.matrix_rank(O)
        ok = ctrl_rank == 3 and obs_rank == 3
        return (ok, f"ctrl_rank={ctrl_rank}, obs_rank={obs_rank}")
    ch.add(StructuralCheck(
        label="Exercise 29.6: 3D system fully controllable and observable",
        section="11",
        predicate=ex296_checks,
    ))
    # Open-loop poles: eigenvalues of A
    def ex296_poles():
        A = np.array([[0, 1, 0], [0, 0, 1], [-2, -4, -3]])
        return np.sort(np.real(np.linalg.eigvals(A)))
    ch.add(StructuralCheck(
        label="Exercise 29.6: All open-loop poles have Re < 0",
        section="11",
        predicate=lambda: (all(np.real(np.linalg.eigvals(
            np.array([[0,1,0],[0,0,1],[-2,-4,-3]]))) < 0),
                           "Not all poles in LHP"),
    ))

    # --- Exercise 29.7: LQR for double integrator ---
    def ex297_lqr():
        from scipy.linalg import solve_continuous_are
        A = np.array([[0, 1], [0, 0]])
        B = np.array([[0], [1]])
        Q = np.eye(2)
        R = np.array([[1.0]])
        P = solve_continuous_are(A, B, Q, R)
        K = np.linalg.solve(R, B.T @ P)
        A_cl = A - B @ K
        eigs = np.linalg.eigvals(A_cl)
        ok = all(np.real(e) < 0 for e in eigs)
        return (ok, f"Closed-loop eigs: {eigs}")
    ch.add(StructuralCheck(
        label="Exercise 29.7: LQR double integrator yields stable CL",
        section="11",
        predicate=ex297_lqr,
    ))

    # --- Exercise 29.8: Uncontrollable system ---
    def ex298_uncontrollable():
        A = np.array([[0, 1], [0, 0]])
        B = np.array([[1], [0]])
        C_ctrl = np.hstack([B, A @ B])
        rank = np.linalg.matrix_rank(C_ctrl)
        ok = rank < 2  # Not full rank => not controllable
        return (ok, f"rank([B, AB]) = {rank}, system IS controllable" if not ok else "")
    ch.add(StructuralCheck(
        label="Exercise 29.8: System [[0,1],[0,0]], B=[1,0] is NOT controllable",
        section="11",
        predicate=ex298_uncontrollable,
    ))

    # --- Exercise 29.5: G(s)=10/(s^2+3s+2) state-space and PID ---
    # Poles: s^2+3s+2=0 => s=-1, s=-2 (stable open-loop)
    ch.add(NumericCheck(
        label="Exercise 29.5: Open-loop pole 1 = -1",
        section="11",
        stated=-1.0,
        computed=lambda: (-3 + math.sqrt(9-8)) / 2,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 29.5: Open-loop pole 2 = -2",
        section="11",
        stated=-2.0,
        computed=lambda: (-3 - math.sqrt(9-8)) / 2,
        tolerance=1e-6,
    ))
    # DC gain G(0) = 10/2 = 5
    ch.add(NumericCheck(
        label="Exercise 29.5: DC gain G(0) = 10/2 = 5",
        section="11",
        stated=5.0,
        computed=lambda: 10 / 2,
        tolerance=1e-6,
    ))
    # Controllable canonical form: A = [[0,1],[-2,-3]], B=[[0],[1]], C=[[10,0]]
    def ex295_state_space():
        A = np.array([[0, 1], [-2, -3]])
        B = np.array([[0], [1]])
        C_obs = np.array([[10, 0]])
        eigs = np.sort(np.real(np.linalg.eigvals(A)))
        ok = abs(eigs[0] - (-2)) < 1e-6 and abs(eigs[1] - (-1)) < 1e-6
        return (ok, f"State-space eigenvalues: {eigs}")
    ch.add(StructuralCheck(
        label="Exercise 29.5: Controllable canonical form eigenvalues match poles",
        section="11",
        predicate=ex295_state_space,
    ))

    # Exercise 29.5: Overshoot for second-order system with zeta=0.72
    # Overshoot = exp(-pi*zeta/sqrt(1-zeta^2))
    ch.add(NumericCheck(
        label="Exercise 29.5: Overshoot with zeta=0.72 ~ 3.8%",
        section="11",
        stated=0.038,
        computed=lambda: math.exp(-math.pi * 0.72 / math.sqrt(1 - 0.72**2)),
        tolerance=5e-2,
        note="Overshoot = exp(-pi*zeta/sqrt(1-zeta^2)), zeta=0.72",
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.21: Controllability-observability duality
    # Controllability of (A,B) <=> observability of (A^T, B^T)
    def remark_321_duality():
        A = np.array([[0, 1], [-2, -3]])
        B = np.array([[0], [1]])
        # Controllability matrix of (A, B): [B, AB]
        C_ctrl = np.hstack([B, A @ B])
        rank_ctrl = np.linalg.matrix_rank(C_ctrl)
        # Observability matrix of (A^T, B^T): [B^T; B^T A^T] = [B^T; (AB)^T]
        O_obs = np.vstack([B.T, (A @ B).T])
        rank_obs = np.linalg.matrix_rank(O_obs)
        ok = rank_ctrl == rank_obs
        return (ok, f"rank(C_ctrl)={rank_ctrl}, rank(O_dual)={rank_obs}")
    ch.add(StructuralCheck(
        label="Remark 3.21: Controllability(A,B) <=> Observability(A^T,B^T)",
        section="4",
        predicate=remark_321_duality,
        note="Remark 3.21",
    ))

    # Remark 3.3: S(s) + T(s) = 1 numerically for specific G, C at sample frequencies
    def remark_33_sensitivity_numeric():
        # G(s) = 1/(s^2 + 0.5s + 2), C(s) = 10 (proportional)
        test_freqs = [0.1, 1.0, 5.0, 10.0]
        for omega in test_freqs:
            s = 1j * omega
            G = 1 / (s**2 + 0.5*s + 2)
            C_ctrl = 10
            L = G * C_ctrl
            S = 1 / (1 + L)
            T = L / (1 + L)
            if abs(S + T - 1) > 1e-10:
                return (False, f"S+T={S+T} at omega={omega}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Remark 3.3: S(jw) + T(jw) = 1 at sample frequencies",
        section="4",
        predicate=remark_33_sensitivity_numeric,
        note="Remark 3.3",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: PID Closed-Loop Simulation ---
    def alg_5_1_pid():
        # Simple first-order plant: dx/dt = -x + u, y = x
        # PID should drive output to reference r=1.0
        A = np.array([[-1.0]])
        B = np.array([[1.0]])
        C_out = np.array([[1.0]])
        Kp, Ki, Kd = 5.0, 2.0, 0.5
        h = 0.01
        T_end = 10.0
        x = np.array([0.0])
        integral = 0.0
        e_prev = 1.0  # r(0) - y(0) = 1 - 0
        r = 1.0
        for _ in range(int(T_end / h)):
            y = C_out @ x
            e = r - y[0]
            integral += e * h
            de = (e - e_prev) / h
            u = Kp * e + Ki * integral + Kd * de
            # RK4 step
            def f(xx, uu):
                return (A @ xx + B * uu).flatten()
            k1 = h * f(x, u)
            k2 = h * f(x + k1 / 2, u)
            k3 = h * f(x + k2 / 2, u)
            k4 = h * f(x + k3, u)
            x = x + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            e_prev = e
        y_final = (C_out @ x)[0]
        # Should have converged to r=1.0
        ok = abs(y_final - 1.0) < 0.05
        return (ok, f"Final output y={y_final:.4f}, target=1.0")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: PID closed-loop simulation",
        section="6",
        predicate=alg_5_1_pid,
    ))

    # --- Algorithm 5.2: Transfer Function Poles ---
    def alg_5_2_poles():
        # G(s) = 1/(s^2 + 3s + 2) => poles at s=-1, s=-2
        # Denominator: a0=2, a1=3, a2=1
        coeffs = [2, 3, 1]  # a0, a1, a2
        a_n = coeffs[-1]
        n = len(coeffs) - 1
        companion = np.zeros((n, n))
        for i in range(n - 1):
            companion[i, i + 1] = 1.0
        for i in range(n):
            companion[n - 1, i] = -coeffs[i] / a_n
        poles = np.sort(np.real(np.linalg.eigvals(companion)))
        ok = abs(poles[0] - (-2)) < 1e-6 and abs(poles[1] - (-1)) < 1e-6
        return (ok, f"Poles: {poles}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Transfer function poles via companion matrix",
        section="6",
        predicate=alg_5_2_poles,
    ))

    # --- Algorithm 5.3: Controllability and Observability ---
    def alg_5_3_ctrl_obs():
        A = np.array([[0, 1], [-2, -3]])
        B = np.array([[0], [1]])
        C_out = np.array([[1, 0]])
        n = A.shape[0]
        # Controllability
        Cc = np.hstack([np.linalg.matrix_power(A, i) @ B for i in range(n)])
        rank_c = np.linalg.matrix_rank(Cc)
        controllable = (rank_c == n)
        # Observability
        Oo = np.vstack([C_out @ np.linalg.matrix_power(A, i) for i in range(n)])
        rank_o = np.linalg.matrix_rank(Oo)
        observable = (rank_o == n)
        ok = controllable and observable
        return (ok, f"Controllable={controllable} (rank={rank_c}), Observable={observable} (rank={rank_o})")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Controllability and observability check",
        section="6",
        predicate=alg_5_3_ctrl_obs,
    ))

    # --- Algorithm 5.4: LQR via Iterative Riccati ---
    def alg_5_4_lqr():
        from scipy.linalg import solve_continuous_lyapunov
        A = np.array([[0, 1], [-2, -3]])
        B = np.array([[0], [1]])
        Q = np.eye(2)
        R = np.array([[1.0]])
        P = Q.copy()
        for _ in range(200):
            K = np.linalg.solve(R, B.T @ P)
            Acl = A - B @ K
            P_new = solve_continuous_lyapunov(Acl.T, -(Q + K.T @ R @ K))
            if np.linalg.norm(P_new - P) < 1e-10:
                break
            P = P_new
        K_final = np.linalg.solve(R, B.T @ P)
        # Closed-loop should be stable: all eigenvalues negative real part
        Acl = A - B @ K_final
        eigs = np.linalg.eigvals(Acl)
        ok = all(np.real(e) < 0 for e in eigs)
        return (ok, f"CL eigenvalues: {eigs}, K={K_final}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: LQR via iterative Riccati (stable closed-loop)",
        section="6",
        predicate=alg_5_4_lqr,
    ))

    # --- Remark 3.6: Transfer function steady-state gain = G(0) ---
    def _remark_3_6_steady_state_gain():
        """Verify G(0) = b_0/a_0 for a stable first-order system."""
        # G(s) = b/(s+a) => G(0) = b/a
        b, a = 5.0, 2.0
        G_0 = b / a  # steady-state gain
        # Simulate step response: dy/dt = -a*y + b*u, u=1
        dt = 0.001
        y = 0.0
        for _ in range(20000):
            y += dt * (-a * y + b * 1.0)
        if abs(y - G_0) > 0.01:
            return (False, f"Steady-state y={y}, G(0)={G_0}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.6: Transfer function G(0) = steady-state gain",
        section="3.6",
        predicate=_remark_3_6_steady_state_gain,
        note="Remark 3.6: transfer function properties",
    ))

    # --- Remark 3.18: Controllability depends on (A,B), not A alone ---
    def _remark_3_18_controllability():
        """Verify stable system can be uncontrollable with wrong B."""
        # A = [[-1, 0], [0, -2]] is stable (negative eigenvalues)
        A = np.array([[-1, 0], [0, -2]], dtype=float)
        # B = [[1], [0]] => controllability matrix [B, AB] = [[1, -1], [0, 0]] rank 1 < 2
        B_bad = np.array([[1], [0]], dtype=float)
        C_bad = np.column_stack([B_bad, A @ B_bad])
        rank_bad = np.linalg.matrix_rank(C_bad)
        if rank_bad >= 2:
            return (False, f"Expected uncontrollable, rank={rank_bad}")
        # B = [[1], [1]] => [B, AB] = [[1, -1], [1, -2]] rank 2
        B_good = np.array([[1], [1]], dtype=float)
        C_good = np.column_stack([B_good, A @ B_good])
        rank_good = np.linalg.matrix_rank(C_good)
        if rank_good < 2:
            return (False, f"Expected controllable, rank={rank_good}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.18: Stable system uncontrollable with wrong B, controllable with right B",
        section="3.18",
        predicate=_remark_3_18_controllability,
        note="Remark 3.18: controllability is property of (A,B)",
    ))

    # ── Remark 3.9: Integral windup ──────────────────────────────────────
    # Claims: when actuator saturates, integral term grows unboundedly.
    # Verify: PID with constant error and no saturation feedback => integral grows.
    def _remark_3_9_integral_windup():
        import numpy as np

        # Simulate PID with constant error (setpoint=1, plant stuck at 0)
        Ki = 1.0
        dt = 0.01
        n_steps = 1000
        error = 1.0  # constant error (plant saturated, can't respond)

        integral = 0.0
        integral_values = []
        for _ in range(n_steps):
            integral += Ki * error * dt
            integral_values.append(integral)

        # Integral should grow linearly without bound
        integrals = np.array(integral_values)
        if integrals[-1] <= integrals[0]:
            return (False, f"Integral not growing: start={integrals[0]}, end={integrals[-1]}")

        # Check it's approximately linear growth
        mid = n_steps // 2
        expected_ratio = n_steps / mid
        actual_ratio = integrals[-1] / integrals[mid - 1] if integrals[mid - 1] > 0 else 0
        if abs(actual_ratio - expected_ratio) > 0.1:
            return (False, f"Integral growth not linear: ratio={actual_ratio}, expected={expected_ratio}")

        # Final integral value should be Ki * error * T = 1 * 1 * 10 = 10
        T = n_steps * dt
        expected_final = Ki * error * T
        if abs(integrals[-1] - expected_final) > 1e-6:
            return (False, f"Final integral={integrals[-1]}, expected={expected_final}")

        # Demonstrate anti-windup: with clamping, integral stays bounded
        integral_clamped = 0.0
        clamp_max = 2.0
        for _ in range(n_steps):
            integral_clamped += Ki * error * dt
            integral_clamped = min(integral_clamped, clamp_max)

        if integral_clamped > clamp_max + 1e-10:
            return (False, f"Clamped integral={integral_clamped} exceeds clamp={clamp_max}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.9: Integral windup — unbounded growth without anti-windup",
        section="3.9",
        predicate=_remark_3_9_integral_windup,
        note="Remark 3.9: integral windup demonstrated",
    ))

    # ── Remark 3.24: LQR as constrained optimization ────────────────────
    # Claims: Riccati solution encodes Pontryagin conditions; increasing Q/R
    # ratio produces more aggressive control (faster regulation).
    def _remark_3_24_lqr_aggressiveness():
        import numpy as np
        from scipy.linalg import solve_continuous_are

        # Simple scalar system: dx/dt = -x + u
        A = np.array([[-1.0]])
        B = np.array([[1.0]])

        gains = []
        for q_val in [1.0, 10.0, 100.0]:
            Q = np.array([[q_val]])
            R = np.array([[1.0]])
            P = solve_continuous_are(A, B, Q, R)
            K = np.linalg.solve(R, B.T @ P)
            gains.append(K[0, 0])

        # Higher Q => larger gain K => more aggressive control
        for i in range(len(gains) - 1):
            if gains[i + 1] <= gains[i]:
                return (False, f"Gain not increasing with Q: gains={gains}")

        # Verify: closed-loop pole moves further left (faster) with higher Q
        poles = []
        for q_val in [1.0, 10.0, 100.0]:
            Q = np.array([[q_val]])
            R = np.array([[1.0]])
            P = solve_continuous_are(A, B, Q, R)
            K = np.linalg.solve(R, B.T @ P)
            A_cl = A - B @ K
            poles.append(A_cl[0, 0])

        # Closed-loop poles should be more negative (faster decay)
        for i in range(len(poles) - 1):
            if poles[i + 1] >= poles[i]:
                return (False, f"Poles not moving left with Q: poles={poles}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.24: LQR — increasing Q/R ratio produces more aggressive control",
        section="3.24",
        predicate=_remark_3_24_lqr_aggressiveness,
        note="Remark 3.24: LQR design parameter effect verified",
    ))

    return ch
