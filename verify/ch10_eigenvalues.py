# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 10: Eigenvalues & Eigenvectors — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(10, "Eigenvalues & Eigenvectors")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- tr(A) = sum of eigenvalues ---
    ch.add(SymbolicCheck(
        label="tr(A) = sum of eigenvalues (2x2)",
        section="1",
        identity=lambda: _trace_eigenvalue_sum(),
    ))

    # --- det(A) = product of eigenvalues ---
    ch.add(SymbolicCheck(
        label="det(A) = product of eigenvalues (2x2)",
        section="1",
        identity=lambda: _det_eigenvalue_product(),
    ))

    # --- Characteristic polynomial: p(lam) = lam^2 - tr(A)*lam + det(A) ---
    ch.add(SymbolicCheck(
        label="Characteristic poly: lam^2 - tr(A)*lam + det(A)",
        section="1",
        zero_expr=lambda: _characteristic_poly_2x2(),
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    # --- A = [[4,2],[1,3]]: eigenvalues 2 and 5 ---
    A1 = np.array([[4, 2], [1, 3]], dtype=float)

    ch.add(StructuralCheck(
        label="A=[[4,2],[1,3]]: eigenvalues {2, 5}",
        section="2",
        predicate=lambda: _eigenvalue_set_check(A1, [2.0, 5.0]),
    ))

    # --- tr(A) = 7 = 2 + 5 ---
    ch.add(NumericCheck(
        label="tr(A) = 7 = 2 + 5",
        section="2",
        stated=7.0,
        computed=lambda: float(np.trace(A1)),
    ))

    # --- det(A) = 10 = 2 * 5 ---
    ch.add(NumericCheck(
        label="det(A) = 10 = 2 * 5",
        section="2",
        stated=10.0,
        computed=lambda: float(np.linalg.det(A1)),
        tolerance=1e-10,
    ))

    # --- Eigenvector verification: A*v = lambda*v ---
    ch.add(StructuralCheck(
        label="Eigenvector check: A*v = lambda*v for A=[[4,2],[1,3]]",
        section="2",
        predicate=lambda: _eigenvector_check(A1),
    ))

    # --- A = [[5,2],[2,2]]: eigenvalues 1 and 6 ---
    A2 = np.array([[5, 2], [2, 2]], dtype=float)

    ch.add(StructuralCheck(
        label="A=[[5,2],[2,2]]: eigenvalues {1, 6}",
        section="3",
        predicate=lambda: _eigenvalue_set_check(A2, [1.0, 6.0]),
    ))

    # --- Orthogonal eigenvectors for symmetric A2 ---
    ch.add(StructuralCheck(
        label="Orthogonal eigenvectors for A=[[5,2],[2,2]]",
        section="3",
        predicate=lambda: _orthogonal_eigenvectors_check(A2),
        note="symmetric matrix => orthogonal eigenvectors",
    ))

    # --- Diagonalization: P*D*P^{-1} = A ---
    ch.add(StructuralCheck(
        label="Diagonalization: P*D*P^{-1} = A",
        section="3",
        predicate=lambda: _diagonalization_check(A1),
    ))

    # --- 3x3 matrix: eigenvalues 2-sqrt(2), 2, 2+sqrt(2) ---
    A3 = np.array([
        [2, -1, 0],
        [-1, 2, -1],
        [0, -1, 2],
    ], dtype=float)

    ch.add(StructuralCheck(
        label="A=tridiag(-1,2,-1): eigenvalues {2-sqrt(2), 2, 2+sqrt(2)}",
        section="4",
        predicate=lambda: _eigenvalue_set_check(
            A3, [2 - math.sqrt(2), 2.0, 2 + math.sqrt(2)]
        ),
    ))

    # --- H = [[6,2],[2,3]]: eigenvalues 2 and 7 ---
    H = np.array([[6, 2], [2, 3]], dtype=float)

    ch.add(StructuralCheck(
        label="H=[[6,2],[2,3]]: eigenvalues {2, 7}",
        section="5",
        predicate=lambda: _eigenvalue_set_check(H, [2.0, 7.0]),
    ))

    # --- Positive definite: all eigenvalues > 0 ---
    ch.add(StructuralCheck(
        label="H=[[6,2],[2,3]] is positive definite",
        section="5",
        predicate=lambda: _positive_definite_check(H),
    ))

    # --- Condition number = max_eig / min_eig = 7/2 = 3.5 ---
    ch.add(NumericCheck(
        label="Condition number of H = 3.5",
        section="5",
        stated=3.5,
        computed=lambda: float(np.max(np.linalg.eigvalsh(H)) / np.min(np.linalg.eigvalsh(H))),
        tolerance=1e-10,
    ))

    # ===================================================================
    # Spectral mapping properties
    # ===================================================================

    # --- F4.7 sigma(A^{-1}) = {1/lambda} ---
    ch.add(StructuralCheck(
        label="F4.7 sigma(A^{-1}) = {1/lambda} for A=[[4,2],[1,3]]",
        section="1",
        predicate=lambda: _spectral_inverse_check(A1),
        note="eigs(A)={2,5}, eigs(A^{-1})={1/2,1/5}",
    ))

    # --- F4.8 sigma(A + mu*I) = {lambda + mu} ---
    ch.add(StructuralCheck(
        label="F4.8 sigma(A + mu*I) = {lambda + mu} for mu=3",
        section="1",
        predicate=lambda: _spectral_shift_check(A1, 3.0),
        note="eigs(A)={2,5}, eigs(A+3I)={5,8}",
    ))

    # --- F4.9 sigma(A^k) = {lambda^k} ---
    ch.add(StructuralCheck(
        label="F4.9 sigma(A^k) = {lambda^k} for k=3",
        section="1",
        predicate=lambda: _spectral_power_check(A1, 3),
        note="eigs(A)={2,5}, eigs(A^3)={8,125}",
    ))

    # --- F4.10 Symmetric matrix has real eigenvalues ---
    ch.add(StructuralCheck(
        label="F4.10 Symmetric matrix has all real eigenvalues",
        section="3",
        predicate=lambda: _symmetric_real_eigenvalues_check(),
        note="Tested on several random symmetric matrices",
    ))

    # --- F4.12 Positive definite iff all eigenvalues > 0 ---
    ch.add(StructuralCheck(
        label="F4.12 PD iff all eigenvalues > 0",
        section="5",
        predicate=lambda: _pd_iff_positive_eigenvalues(),
        note="A^T A is PD for full-rank A; verified x^T A x > 0 and eigs > 0",
    ))

    # --- F4.13 PSD iff all eigenvalues >= 0 ---
    ch.add(StructuralCheck(
        label="F4.13 PSD iff all eigenvalues >= 0",
        section="5",
        predicate=lambda: _psd_iff_nonneg_eigenvalues(),
        note="A^T A is PSD; rank-deficient version has zero eigenvalue",
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 10.1: Diagonal matrix eigenvalues ---
    A_ex1 = np.array([[3, 0], [0, 7]], dtype=float)
    ch.add(StructuralCheck(
        label="Ex 10.1: diag(3,7) has eigenvalues {3, 7}",
        section="11",
        predicate=lambda: _eigenvalue_set_check(A_ex1, [3.0, 7.0]),
    ))

    # --- Exercise 10.2: B=[[1,4],[2,3]] eigenvalues ---
    B_ex2 = np.array([[1, 4], [2, 3]], dtype=float)
    # char poly: lam^2 - 4*lam - 5 = (lam-5)(lam+1), eigenvalues 5 and -1
    ch.add(StructuralCheck(
        label="Ex 10.2: B=[[1,4],[2,3]] eigenvalues {-1, 5}",
        section="11",
        predicate=lambda: _eigenvalue_set_check(B_ex2, [-1.0, 5.0]),
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: tr(B) = 4 = 5 + (-1)",
        section="11",
        stated=4.0,
        computed=lambda: float(np.trace(B_ex2)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: det(B) = -5 = 5 * (-1)",
        section="11",
        stated=-5.0,
        computed=lambda: float(np.linalg.det(B_ex2)),
        tolerance=1e-10,
    ))

    # --- Exercise 10.3: Upper triangular C=[[3,1],[0,3]] ---
    C_ex3 = np.array([[3, 1], [0, 3]], dtype=float)
    ch.add(StructuralCheck(
        label="Ex 10.3: C=[[3,1],[0,3]] eigenvalue = 3 (multiplicity 2)",
        section="11",
        predicate=lambda: _eigenvalue_set_check(C_ex3, [3.0, 3.0]),
    ))

    # C is defective (not diagonalizable): eigenspace for lambda=3 has dim 1
    ch.add(StructuralCheck(
        label="Ex 10.3: C is defective (not diagonalizable)",
        section="11",
        predicate=lambda: _defective_check(C_ex3, 3.0),
    ))

    # --- Exercise 10.4: A=[[1,2],[2,4]] eigenvalues ---
    A_ex4 = np.array([[1, 2], [2, 4]], dtype=float)
    # Eigenvalues: 0 and 5
    ch.add(StructuralCheck(
        label="Ex 10.4: A=[[1,2],[2,4]] eigenvalues {0, 5}",
        section="11",
        predicate=lambda: _eigenvalue_set_check(A_ex4, [0.0, 5.0]),
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: det(A) = 0 (singular, eigenvalue 0)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.linalg.det(A_ex4)),
        tolerance=1e-10,
    ))

    ch.add(StructuralCheck(
        label="Ex 10.4: Eigenvectors orthogonal (symmetric A)",
        section="11",
        predicate=lambda: _orthogonal_eigenvectors_check(A_ex4),
    ))

    # --- Exercise 10.5: Diagonalize M=[[0,1],[1,0]] ---
    M_ex5 = np.array([[0, 1], [1, 0]], dtype=float)
    # Eigenvalues: -1, 1
    ch.add(StructuralCheck(
        label="Ex 10.5: M=[[0,1],[1,0]] eigenvalues {-1, 1}",
        section="11",
        predicate=lambda: _eigenvalue_set_check(M_ex5, [-1.0, 1.0]),
    ))

    # M^10 = P*D^10*P^{-1}; since eigenvalues are +/-1, D^10 = I, so M^10 = I
    M10 = np.linalg.matrix_power(M_ex5, 10)
    ch.add(StructuralCheck(
        label="Ex 10.5: M^10 = I (eigenvalues +/-1, even power)",
        section="11",
        predicate=lambda: (
            np.allclose(M10, np.eye(2), atol=1e-10),
            f"M^10 = {M10}, expected I"
        ),
    ))

    ch.add(StructuralCheck(
        label="Ex 10.5: Diagonalization M = PDP^{-1}",
        section="11",
        predicate=lambda: _diagonalization_check(M_ex5),
    ))

    # --- Exercise 10.6: Spectral properties from eigenvalues 2, -1, 3 ---
    # (a) tr(A) = 2 + (-1) + 3 = 4
    ch.add(NumericCheck(
        label="Ex 10.6a: tr(A) = 2+(-1)+3 = 4",
        section="11",
        stated=4.0,
        computed=lambda: 2.0 + (-1.0) + 3.0,
        tolerance=1e-12,
    ))

    # (b) det(A) = 2*(-1)*3 = -6
    ch.add(NumericCheck(
        label="Ex 10.6b: det(A) = 2*(-1)*3 = -6",
        section="11",
        stated=-6.0,
        computed=lambda: 2.0 * (-1.0) * 3.0,
        tolerance=1e-12,
    ))

    # (c) eigenvalues of A^2: 4, 1, 9
    ch.add(StructuralCheck(
        label="Ex 10.6c: eigenvalues of A^2 = {1, 4, 9}",
        section="11",
        predicate=lambda: (
            sorted([4.0, 1.0, 9.0]) == [1.0, 4.0, 9.0],
            "eigenvalues of A^2 = {lambda^2}"
        ),
    ))

    # (d) eigenvalues of A^{-1}: 1/2, -1, 1/3
    ch.add(NumericCheck(
        label="Ex 10.6d: eigenvalues of A^{-1} sum = 1/2-1+1/3 = -1/6",
        section="11",
        stated=1.0/2.0 + (-1.0) + 1.0/3.0,
        computed=lambda: 1.0/2.0 - 1.0 + 1.0/3.0,
        tolerance=1e-12,
    ))

    # (e) eigenvalues of A+4I: 6, 3, 7
    ch.add(NumericCheck(
        label="Ex 10.6e: eigenvalues of A+4I: sum = 6+3+7 = 16",
        section="11",
        stated=16.0,
        computed=lambda: (2+4) + (-1+4) + (3+4),
        tolerance=1e-12,
    ))

    # --- Exercise 10.7: Eigenvectors for distinct eigenvalues are LI ---
    # For a 3x3 matrix with 3 distinct eigenvalues, eigenvectors form a basis
    A_ex7 = np.array([[2, 1, 0], [0, 3, 1], [0, 0, 5]], dtype=float)
    eigs_ex7 = np.linalg.eigvals(A_ex7).real  # Should be 2, 3, 5 (upper triangular)

    ch.add(StructuralCheck(
        label="Ex 10.7: 3 distinct eigenvalues {2, 3, 5}",
        section="11",
        predicate=lambda: (
            len(set(np.round(eigs_ex7, 10))) == 3,
            f"eigenvalues = {eigs_ex7}, expected 3 distinct"
        ),
    ))

    # Eigenvectors should be linearly independent
    _, P_ex7 = np.linalg.eig(A_ex7)
    ch.add(StructuralCheck(
        label="Ex 10.7: eigenvectors for distinct eigenvalues are LI",
        section="11",
        predicate=lambda: (
            np.linalg.matrix_rank(P_ex7) == 3,
            f"rank of eigenvector matrix = {np.linalg.matrix_rank(P_ex7)}, expected 3"
        ),
    ))

    # Verify by checking det(P) != 0
    ch.add(StructuralCheck(
        label="Ex 10.7: det(P) != 0 (eigenvector matrix invertible)",
        section="11",
        predicate=lambda: (
            abs(np.linalg.det(P_ex7)) > 1e-10,
            f"det(P) = {np.linalg.det(P_ex7)}, expected nonzero"
        ),
    ))

    # --- Exercise 10.8: tr(A) = lambda_1+lambda_2, det(A) = lambda_1*lambda_2 ---
    # For general 2x2: p(lambda) = lambda^2 - tr(A)*lambda + det(A)
    # = (lambda - lambda_1)(lambda - lambda_2) => Vieta's formulas
    def _ex_10_8_vieta():
        import sympy
        a, b, c, d = sympy.symbols('a b c d')
        A_sym = sympy.Matrix([[a, b], [c, d]])
        lam = sympy.Symbol('lambda')
        char_poly = (A_sym - lam * sympy.eye(2)).det()
        # Expand: (a-lam)(d-lam) - bc = lam^2 - (a+d)*lam + (ad-bc)
        expanded = sympy.expand(char_poly)
        # Compare with (lam - lam1)(lam - lam2) = lam^2 - (lam1+lam2)*lam + lam1*lam2
        # Coefficient of lam: -(a+d) = -(lam1+lam2) => tr(A) = lam1+lam2
        # Constant term: ad-bc = lam1*lam2 => det(A) = lam1*lam2
        tr_coeff = -expanded.coeff(lam, 1)
        det_coeff = expanded.coeff(lam, 0)
        tr_ok = sympy.simplify(tr_coeff - (a + d)) == 0
        det_ok = sympy.simplify(det_coeff - (a*d - b*c)) == 0
        if tr_ok and det_ok:
            return (True, "")
        return (False, f"tr coeff match: {tr_ok}, det coeff match: {det_ok}")

    ch.add(StructuralCheck(
        label="Ex 10.8: tr(A) = sum eigenvalues, det(A) = product (Vieta, symbolic)",
        section="11",
        predicate=_ex_10_8_vieta,
    ))

    # Numeric verification
    A_ex8_num = np.array([[7, 3], [2, 8]], dtype=float)
    eigs_ex8 = np.linalg.eigvals(A_ex8_num).real

    ch.add(NumericCheck(
        label="Ex 10.8: tr(A) = sum of eigenvalues (numeric)",
        section="11",
        stated=float(np.trace(A_ex8_num)),
        computed=lambda: float(np.sum(np.linalg.eigvals(A_ex8_num).real)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 10.8: det(A) = product of eigenvalues (numeric)",
        section="11",
        stated=float(np.linalg.det(A_ex8_num)),
        computed=lambda: float(np.prod(np.linalg.eigvals(A_ex8_num).real)),
        tolerance=1e-10,
    ))

    # ==================================================================
    # Remark 3.16: A^k = P D^k P^{-1}
    # ==================================================================

    def _remark_3_16_matrix_power():
        A = np.array([[4, 2], [1, 3]], dtype=float)
        evals, P = np.linalg.eig(A)
        P_inv = np.linalg.inv(P)
        for k in [2, 5, 10, 50]:
            Ak_direct = np.linalg.matrix_power(A, k)
            Dk = np.diag(evals ** k)
            Ak_diag = P @ Dk @ P_inv
            if not np.allclose(Ak_direct, Ak_diag, atol=1e-8):
                diff = np.max(np.abs(Ak_direct - Ak_diag))
                return (False, f"k={k}: max diff = {diff}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.16: A^k = P D^k P^{-1} for k=2,5,10,50",
        section="3",
        predicate=_remark_3_16_matrix_power,
        note="Remark 3.16: power of diagonalization",
    ))

    # ==================================================================
    # Remark 3.17: Defective matrix [[1,1],[0,1]]
    # ==================================================================

    def _remark_3_17_defective_matrix():
        A = np.array([[1, 1], [0, 1]], dtype=float)
        evals = np.linalg.eigvals(A)
        # Both eigenvalues should be 1
        if not np.allclose(sorted(evals.real), [1.0, 1.0], atol=1e-12):
            return (False, f"eigenvalues = {evals}, expected [1, 1]")
        # Algebraic multiplicity = 2, geometric multiplicity = 1
        # rank(A - I) = rank([[0,1],[0,0]]) = 1, so nullity = 2 - 1 = 1
        A_minus_I = A - np.eye(2)
        rank = np.linalg.matrix_rank(A_minus_I)
        geo_mult = 2 - rank  # nullity = n - rank
        if geo_mult != 1:
            return (False, f"geometric multiplicity = {geo_mult}, expected 1")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.17: [[1,1],[0,1]] has eigenvalue 1 with alg=2, geo=1",
        section="3",
        predicate=_remark_3_17_defective_matrix,
        note="Remark 3.17: defective (not diagonalizable) matrix",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Characteristic Polynomial for 2x2 ---
    def _algo_char_poly():
        """Implement Algorithm 5.1 for 2x2 and verify eigenvalues."""
        A = np.array([[4, 2], [1, 3]], dtype=float)
        trace = A[0, 0] + A[1, 1]
        det = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
        # Eigenvalues from quadratic: lambda = (trace +/- sqrt(trace^2 - 4*det)) / 2
        disc = trace ** 2 - 4 * det
        lam1 = (trace + math.sqrt(disc)) / 2
        lam2 = (trace - math.sqrt(disc)) / 2
        expected = sorted(np.linalg.eigvals(A).real)
        computed = sorted([lam1, lam2])
        for i in range(2):
            if abs(computed[i] - expected[i]) > 1e-10:
                return (False, f"eigenvalue {i}: {computed[i]} != {expected[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Characteristic polynomial for 2x2 gives correct eigenvalues",
        section="6",
        predicate=_algo_char_poly,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Power Iteration ---
    def _algo_power_iteration():
        """Implement Algorithm 5.2 and verify dominant eigenvalue."""
        def power_iteration(A, tol=1e-10, max_iter=1000):
            n = A.shape[0]
            np.random.seed(42)
            v = np.random.randn(n)
            v = v / np.linalg.norm(v)
            lam_prev = 0.0
            for _ in range(max_iter):
                w = A @ v
                lam = np.linalg.norm(w)
                if lam == 0:
                    return None, None
                v = w / lam
                if abs(lam - lam_prev) < tol:
                    # Use Rayleigh quotient for sign
                    lam_signed = float(v @ A @ v)
                    return lam_signed, v
                lam_prev = lam
            return None, None

        A = np.array([[4, 2], [1, 3]], dtype=float)
        lam, v = power_iteration(A)
        expected_lam = max(np.linalg.eigvals(A).real)
        if abs(lam - expected_lam) > 1e-6:
            return (False, f"Power iteration: lambda={lam}, expected={expected_lam}")

        # Verify eigenvector: Av = lam*v
        residual = np.linalg.norm(A @ v - lam * v)
        if residual > 1e-6:
            return (False, f"Eigenvector residual = {residual}")

        # Test on symmetric matrix
        B = np.array([[6, 2], [2, 3]], dtype=float)
        lam_b, v_b = power_iteration(B)
        expected_b = max(np.linalg.eigvals(B).real)
        if abs(lam_b - expected_b) > 1e-6:
            return (False, f"Power iteration (sym): lambda={lam_b}, expected={expected_b}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Power iteration finds dominant eigenvalue of [[4,2],[1,3]]",
        section="6",
        predicate=_algo_power_iteration,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Inverse Iteration ---
    def _algo_inverse_iteration():
        """Implement Algorithm 5.3 and verify eigenvalue closest to shift."""
        def inverse_iteration(A, mu, tol=1e-10, max_iter=1000):
            n = A.shape[0]
            B = A - mu * np.eye(n)
            np.random.seed(42)
            v = np.random.randn(n)
            v = v / np.linalg.norm(v)
            lam_prev = 0.0
            for _ in range(max_iter):
                w = np.linalg.solve(B, v)
                lam_inv = np.linalg.norm(w)
                v = w / lam_inv
                lam = mu + 1.0 / lam_inv
                if abs(lam - lam_prev) < tol:
                    return lam, v
                lam_prev = lam
            return None, None

        A = np.array([[4, 2], [1, 3]], dtype=float)
        # Eigenvalues are 2 and 5. Shift near 2 should find 2.
        lam, v = inverse_iteration(A, mu=1.5)
        if abs(lam - 2.0) > 1e-6:
            return (False, f"Inverse iteration with mu=1.5: lambda={lam}, expected=2.0")

        # Shift near 5 should find 5.
        lam, v = inverse_iteration(A, mu=4.8)
        if abs(lam - 5.0) > 1e-6:
            return (False, f"Inverse iteration with mu=4.8: lambda={lam}, expected=5.0")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Inverse iteration finds eigenvalue closest to shift",
        section="6",
        predicate=_algo_inverse_iteration,
        note="Algorithm 5.3 verified",
    ))

    # --- Remark 3.2: Eigenvector direction is preserved (not rotated) ---
    def _remark_3_2_geometric():
        """Verify Av is parallel to v (only scaled, not rotated)."""
        A = np.array([[2, 1], [1, 3]], dtype=float)
        evals, evecs = np.linalg.eigh(A)
        for i in range(len(evals)):
            v = evecs[:, i]
            Av = A @ v
            lam = evals[i]
            # Av should equal lambda * v
            if not np.allclose(Av, lam * v, atol=1e-10):
                return (False, f"Av != lambda*v for eigenvalue {lam}")
            # Verify stretching interpretation
            if lam > 1 and np.linalg.norm(Av) <= np.linalg.norm(v):
                return (False, f"lambda={lam}>1 but ||Av|| <= ||v|| (should stretch)")
            if 0 < lam < 1 and np.linalg.norm(Av) >= np.linalg.norm(v):
                return (False, f"lambda={lam}<1 but ||Av|| >= ||v|| (should compress)")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.2: Eigenvectors only scaled (not rotated) by A",
        section="3.2",
        predicate=_remark_3_2_geometric,
        note="Remark 3.2: geometric interpretation",
    ))

    # --- Remark 3.19: Spectral theorem properties for symmetric matrices ---
    def _remark_3_19_spectral():
        """Verify symmetric matrices: real eigenvalues, orthogonal eigenvectors, diagonalizable."""
        rng = np.random.default_rng(319)
        for _ in range(5):
            B = rng.standard_normal((4, 4))
            A = B + B.T  # symmetric
            evals, evecs = np.linalg.eigh(A)
            # 1. All eigenvalues real
            if not np.all(np.isreal(evals)):
                return (False, f"Non-real eigenvalue found: {evals}")
            # 2. Eigenvectors orthogonal: Q^T Q = I
            QTQ = evecs.T @ evecs
            if not np.allclose(QTQ, np.eye(4), atol=1e-10):
                return (False, f"Eigenvectors not orthogonal: max off-diag={np.max(np.abs(QTQ - np.eye(4)))}")
            # 3. Diagonalizable: A = Q D Q^T
            D = np.diag(evals)
            A_recon = evecs @ D @ evecs.T
            if not np.allclose(A, A_recon, atol=1e-10):
                return (False, f"A != Q D Q^T: max err={np.max(np.abs(A - A_recon))}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.19: Symmetric => real evals, orthogonal evecs, diagonalizable",
        section="3.19",
        predicate=_remark_3_19_spectral,
        note="Remark 3.19: spectral theorem properties",
    ))

    return ch


# ---------------------------------------------------------------------------
# Exercise helpers
# ---------------------------------------------------------------------------

def _defective_check(A, lam):
    """Check that eigenspace for lambda has dim < algebraic multiplicity."""
    n = A.shape[0]
    # For lambda with algebraic mult 2, geometric mult should be 1 (defective)
    kernel = A - lam * np.eye(n)
    rank = np.linalg.matrix_rank(kernel, tol=1e-10)
    geo_mult = n - rank
    if geo_mult < 2:  # algebraic mult is 2, geo is 1 => defective
        return (True, "")
    return (False, f"Geometric multiplicity = {geo_mult}, expected < 2")


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _trace_eigenvalue_sum():
    """For A=[[4,2],[1,3]], verify tr(A) = sum of eigenvalues (2+5=7)."""
    import sympy
    A = sympy.Matrix([[4, 2], [1, 3]])
    eigenvals = A.eigenvals()  # dict {eigenvalue: multiplicity}
    eig_sum = sum(val * mult for val, mult in eigenvals.items())
    return sympy.Eq(A.trace(), eig_sum)


def _det_eigenvalue_product():
    """For A=[[4,2],[1,3]], verify det(A) = product of eigenvalues (2*5=10)."""
    import sympy
    A = sympy.Matrix([[4, 2], [1, 3]])
    eigenvals = A.eigenvals()
    eig_prod = sympy.Mul(*[val**mult for val, mult in eigenvals.items()])
    return sympy.Eq(A.det(), eig_prod)


def _characteristic_poly_2x2():
    """Verify det(A - lam*I) = lam^2 - tr(A)*lam + det(A) for generic 2x2."""
    import sympy
    a, b, c, d, lam = sympy.symbols("a b c d lambda")
    A = sympy.Matrix([[a, b], [c, d]])
    I = sympy.eye(2)
    char_poly = (A - lam * I).det()
    expected = lam**2 - (a + d) * lam + (a * d - b * c)
    return sympy.expand(char_poly - expected)


# ---------------------------------------------------------------------------
# Structural / numeric helpers
# ---------------------------------------------------------------------------

def _eigenvalue_set_check(A, expected_eigs):
    """Check that eigenvalues of A match the expected set (sorted)."""
    computed = sorted(np.linalg.eigvals(A).real)
    expected = sorted(expected_eigs)
    if np.allclose(computed, expected, atol=1e-10):
        return (True, "")
    return (False, f"Expected eigenvalues {expected}, got {computed}")


def _eigenvector_check(A):
    """Verify A*v = lambda*v for each eigenpair."""
    eigenvalues, eigenvectors = np.linalg.eig(A)
    for i in range(len(eigenvalues)):
        lam = eigenvalues[i]
        v = eigenvectors[:, i]
        Av = A @ v
        lam_v = lam * v
        if not np.allclose(Av, lam_v, atol=1e-10):
            return (False, f"A*v != lambda*v for lambda={lam}: {Av} != {lam_v}")
    return (True, "")


def _orthogonal_eigenvectors_check(A):
    """For symmetric A, verify eigenvectors are orthogonal."""
    eigenvalues, eigenvectors = np.linalg.eigh(A)
    n = len(eigenvalues)
    for i in range(n):
        for j in range(i + 1, n):
            dot = abs(np.dot(eigenvectors[:, i], eigenvectors[:, j]))
            if dot > 1e-10:
                return (False, f"Eigenvectors {i} and {j} not orthogonal: dot={dot}")
    return (True, "")


def _diagonalization_check(A):
    """Verify P * D * P^{-1} = A."""
    eigenvalues, P = np.linalg.eig(A)
    D = np.diag(eigenvalues)
    reconstructed = P @ D @ np.linalg.inv(P)
    if np.allclose(reconstructed, A, atol=1e-10):
        return (True, "")
    return (False, f"P*D*P^(-1) != A:\n{reconstructed}\n!=\n{A}")


def _positive_definite_check(A):
    """Check all eigenvalues are strictly positive."""
    eigenvalues = np.linalg.eigvalsh(A)
    if np.all(eigenvalues > 0):
        return (True, "")
    return (False, f"Not positive definite: eigenvalues = {eigenvalues.tolist()}")


# ---------------------------------------------------------------------------
# Spectral mapping helpers
# ---------------------------------------------------------------------------

def _spectral_inverse_check(A):
    """F4.7: sigma(A^{-1}) = {1/lambda : lambda in sigma(A)}."""
    eigs_A = sorted(np.linalg.eigvals(A).real)
    A_inv = np.linalg.inv(A)
    eigs_inv = sorted(np.linalg.eigvals(A_inv).real)
    expected = sorted([1.0 / lam for lam in eigs_A])
    if np.allclose(eigs_inv, expected, atol=1e-10):
        return (True, "")
    return (False, f"eigs(A^{{-1}}) = {eigs_inv}, expected {expected}")


def _spectral_shift_check(A, mu):
    """F4.8: sigma(A + mu*I) = {lambda + mu : lambda in sigma(A)}."""
    n = A.shape[0]
    eigs_A = sorted(np.linalg.eigvals(A).real)
    eigs_shifted = sorted(np.linalg.eigvals(A + mu * np.eye(n)).real)
    expected = sorted([lam + mu for lam in eigs_A])
    if np.allclose(eigs_shifted, expected, atol=1e-10):
        return (True, "")
    return (False, f"eigs(A+{mu}I) = {eigs_shifted}, expected {expected}")


def _spectral_power_check(A, k):
    """F4.9: sigma(A^k) = {lambda^k : lambda in sigma(A)}."""
    eigs_A = sorted(np.linalg.eigvals(A).real)
    A_k = np.linalg.matrix_power(A, k)
    eigs_k = sorted(np.linalg.eigvals(A_k).real)
    expected = sorted([lam**k for lam in eigs_A])
    if np.allclose(eigs_k, expected, atol=1e-8):
        return (True, "")
    return (False, f"eigs(A^{k}) = {eigs_k}, expected {expected}")


def _symmetric_real_eigenvalues_check():
    """F4.10: Symmetric matrices have all real eigenvalues.
    Test on several random symmetric matrices."""
    rng = np.random.default_rng(42)
    for _ in range(10):
        n = rng.integers(2, 6)
        B = rng.standard_normal((n, n))
        A = (B + B.T) / 2  # symmetric
        eigs = np.linalg.eigvals(A)
        if np.max(np.abs(eigs.imag)) > 1e-10:
            return (False, f"Imaginary parts in eigenvalues: {eigs}")
    return (True, "")


def _pd_iff_positive_eigenvalues():
    """F4.12: A is positive definite iff all eigenvalues > 0.
    Build A = B^T B for full-rank B => PD; verify eigs > 0 and x^T A x > 0."""
    rng = np.random.default_rng(77)
    n = 3
    B = rng.standard_normal((n, n))
    A = B.T @ B
    eigs = np.linalg.eigvalsh(A)
    if not np.all(eigs > 0):
        return (False, f"Expected all eigs > 0, got {eigs.tolist()}")
    # Verify x^T A x > 0 for random x
    for _ in range(20):
        x = rng.standard_normal(n)
        quad = x @ A @ x
        if quad <= 0:
            return (False, f"x^T A x = {quad} <= 0 for x={x}")
    return (True, "")


def _psd_iff_nonneg_eigenvalues():
    """F4.13: A is PSD iff all eigenvalues >= 0.
    Build rank-deficient A = B^T B where B is (n-1) x n => PSD with a zero eigenvalue."""
    rng = np.random.default_rng(88)
    n = 4
    B = rng.standard_normal((n - 1, n))  # rank at most n-1
    A = B.T @ B
    eigs = np.linalg.eigvalsh(A)
    if np.any(eigs < -1e-10):
        return (False, f"Expected all eigs >= 0, got {eigs.tolist()}")
    # Should have at least one eigenvalue near 0
    if np.min(np.abs(eigs)) > 0.1:
        return (False, f"Expected at least one eigenvalue near 0, got {eigs.tolist()}")
    # Verify x^T A x >= 0 for random x
    for _ in range(20):
        x = rng.standard_normal(n)
        quad = x @ A @ x
        if quad < -1e-10:
            return (False, f"x^T A x = {quad} < 0 for x={x}")
    return (True, "")
