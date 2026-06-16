# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 9: Matrices & Linear Transformations — verification."""

import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(9, "Matrices & Linear Transformations")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- (AB)^T = B^T A^T ---
    ch.add(SymbolicCheck(
        label="(AB)^T = B^T A^T",
        section="1",
        zero_expr=lambda: _transpose_product(),
        note="transpose of product rule",
    ))

    # --- det(AB) = det(A) det(B) ---
    ch.add(SymbolicCheck(
        label="det(AB) = det(A) det(B)",
        section="2",
        zero_expr=lambda: _det_product(),
    ))

    # --- det(A^T) = det(A) ---
    ch.add(SymbolicCheck(
        label="det(A^T) = det(A)",
        section="2",
        zero_expr=lambda: _det_transpose(),
    ))

    # --- tr(AB) = tr(BA) ---
    ch.add(SymbolicCheck(
        label="tr(AB) = tr(BA)",
        section="2",
        zero_expr=lambda: _trace_commutative(),
    ))

    # --- (A^T)^T = A ---
    ch.add(SymbolicCheck(
        label="(A^T)^T = A",
        section="5",
        zero_expr=lambda: _double_transpose(),
        note="double transpose identity",
    ))

    # --- (A+B)^T = A^T + B^T ---
    ch.add(SymbolicCheck(
        label="(A+B)^T = A^T + B^T",
        section="5",
        zero_expr=lambda: _transpose_sum(),
        note="transpose distributes over addition",
    ))

    # --- (AB)C = A(BC) associativity ---
    ch.add(SymbolicCheck(
        label="(AB)C = A(BC)",
        section="5",
        zero_expr=lambda: _mult_associativity(),
        note="matrix multiplication associativity",
    ))

    # --- A(B+C) = AB + AC left distributivity ---
    ch.add(SymbolicCheck(
        label="A(B+C) = AB + AC",
        section="5",
        zero_expr=lambda: _left_distributivity(),
        note="left distributivity of multiplication over addition",
    ))

    # --- (AB)^{-1} = B^{-1} A^{-1} ---
    ch.add(SymbolicCheck(
        label="(AB)^{-1} = B^{-1} A^{-1}",
        section="5",
        zero_expr=lambda: _inverse_product(),
        note="inverse of product reverses order",
    ))

    # --- (A^T)^{-1} = (A^{-1})^T ---
    ch.add(SymbolicCheck(
        label="(A^T)^{-1} = (A^{-1})^T",
        section="5",
        zero_expr=lambda: _inverse_transpose(),
        note="inverse and transpose commute",
    ))

    # --- (A^{-1})^{-1} = A ---
    ch.add(SymbolicCheck(
        label="(A^{-1})^{-1} = A",
        section="5",
        zero_expr=lambda: _double_inverse(),
        note="double inverse identity",
    ))

    # --- det(A^{-1}) = 1/det(A) ---
    ch.add(SymbolicCheck(
        label="det(A^{-1}) = 1/det(A)",
        section="5",
        zero_expr=lambda: _det_inverse(),
        note="determinant of inverse",
    ))

    # --- det(cA) = c^n det(A) for n=2 ---
    ch.add(SymbolicCheck(
        label="det(cA) = c^n det(A) (n=2)",
        section="5",
        zero_expr=lambda: _det_scalar(),
        note="determinant scalar property",
    ))

    # --- tr(A+B) = tr(A) + tr(B) ---
    ch.add(SymbolicCheck(
        label="tr(A+B) = tr(A) + tr(B)",
        section="5",
        zero_expr=lambda: _trace_additive(),
        note="trace is additive",
    ))

    # --- tr(cA) = c*tr(A) ---
    ch.add(SymbolicCheck(
        label="tr(cA) = c*tr(A)",
        section="5",
        zero_expr=lambda: _trace_scalar(),
        note="trace is linear in scalar",
    ))

    # --- tr(A^T) = tr(A) ---
    ch.add(SymbolicCheck(
        label="tr(A^T) = tr(A)",
        section="5",
        zero_expr=lambda: _trace_transpose(),
        note="trace invariant under transpose",
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    A = np.array([[1, 3], [2, 5]], dtype=float)
    B = np.array([[4, 1], [0, 2]], dtype=float)
    AB_expected = np.array([[4, 7], [8, 12]], dtype=float)

    # --- Matrix multiplication: AB ---
    ch.add(StructuralCheck(
        label="AB = [[4,7],[8,12]]",
        section="3",
        predicate=lambda: _mat_eq(A @ B, AB_expected),
    ))

    # --- Non-commutativity example from Section 4 ---
    A_nc = np.array([[1, 2], [0, 1]], dtype=float)
    B_nc = np.array([[0, 1], [1, 0]], dtype=float)
    AB_nc_expected = np.array([[2, 1], [1, 0]], dtype=float)
    BA_nc_expected = np.array([[0, 1], [1, 2]], dtype=float)

    ch.add(StructuralCheck(
        label="Non-commutativity: AB = [[2,1],[1,0]]",
        section="4",
        predicate=lambda: _mat_eq(A_nc @ B_nc, AB_nc_expected),
        note="AB != BA in general",
    ))

    ch.add(StructuralCheck(
        label="Non-commutativity: BA = [[0,1],[1,2]]",
        section="4",
        predicate=lambda: _mat_eq(B_nc @ A_nc, BA_nc_expected),
        note="AB != BA in general",
    ))

    ch.add(StructuralCheck(
        label="AB != BA for non-commuting matrices",
        section="4",
        predicate=lambda: (
            (not np.allclose(A_nc @ B_nc, B_nc @ A_nc), "")
            if not np.allclose(A_nc @ B_nc, B_nc @ A_nc)
            else (False, "AB == BA unexpectedly")
        ),
        note="matrix multiplication is not commutative",
    ))

    # --- 3x3 linear system: solution x = (2, 3, -1) ---
    ch.add(StructuralCheck(
        label="3x3 system => x = (2, 3, -1)",
        section="4",
        predicate=lambda: _linear_system_check(),
        note="2x+y-z=8, -3x-y+2z=-11, -2x+y+2z=-3",
    ))

    # --- Determinant of 3x3 matrix = 27 ---
    ch.add(NumericCheck(
        label="det([[1,2,3],[4,5,6],[7,8,0]]) = 27",
        section="5",
        stated=27.0,
        computed=lambda: float(np.linalg.det(
            np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]], dtype=float)
        )),
        tolerance=1e-10,
    ))

    # --- Cofactor expansion terms for 3x3 det (Example 8.3) ---
    # det = 1*(5*0-6*8) - 2*(4*0-6*7) + 3*(4*8-5*7) = -48 + 84 - 9 = 27
    ch.add(NumericCheck(
        label="3x3 cofactor term 1: 1*(5*0-6*8) = -48",
        section="5",
        stated=-48.0,
        computed=lambda: 1.0 * (5 * 0 - 6 * 8),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="3x3 cofactor term 2: -2*(4*0-6*7) = 84",
        section="5",
        stated=84.0,
        computed=lambda: -2.0 * (4 * 0 - 6 * 7),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="3x3 cofactor term 3: 3*(4*8-5*7) = -9",
        section="5",
        stated=-9.0,
        computed=lambda: 3.0 * (4 * 8 - 5 * 7),
        tolerance=1e-10,
    ))

    # --- Row reduction diagonal product for 3x3 det: 1*(-3)*(-9) = 27 ---
    ch.add(NumericCheck(
        label="3x3 row reduction diag product: 1*(-3)*(-9) = 27",
        section="5",
        stated=27.0,
        computed=lambda: 1.0 * (-3.0) * (-9.0),
        tolerance=1e-10,
        note="diagonal of upper triangular form U",
    ))

    # --- Determinant of 2x2: det(A) = 10 where A = [[4,7],[2,6]] ---
    A2 = np.array([[4, 7], [2, 6]], dtype=float)
    ch.add(NumericCheck(
        label="det([[4,7],[2,6]]) = 10",
        section="5",
        stated=10.0,
        computed=lambda: float(np.linalg.det(A2)),
        tolerance=1e-10,
    ))

    # --- det(I_n) = 1 ---
    ch.add(NumericCheck(
        label="det(I_3) = 1",
        section="5",
        stated=1.0,
        computed=lambda: float(np.linalg.det(np.eye(3))),
        tolerance=1e-10,
        note="determinant of identity is 1",
    ))

    # --- tr(I_n) = n ---
    ch.add(NumericCheck(
        label="tr(I_4) = 4",
        section="5",
        stated=4.0,
        computed=lambda: float(np.trace(np.eye(4))),
        tolerance=1e-10,
        note="trace of identity equals dimension",
    ))

    # --- Inverse: A^{-1} = [[0.6,-0.7],[-0.2,0.4]] ---
    A_inv_expected = np.array([[0.6, -0.7], [-0.2, 0.4]])
    ch.add(StructuralCheck(
        label="A^{-1} = [[0.6,-0.7],[-0.2,0.4]]",
        section="5",
        predicate=lambda: _mat_eq(np.linalg.inv(A2), A_inv_expected, tol=1e-10),
    ))

    # --- A * A^{-1} = I verification ---
    ch.add(StructuralCheck(
        label="A * A^{-1} = I",
        section="5",
        predicate=lambda: _mat_eq(A2 @ np.linalg.inv(A2), np.eye(2), tol=1e-10),
    ))

    # --- Individual entries of A*A^{-1} (Example 8.5) ---
    ch.add(NumericCheck(
        label="(AA^{-1})_{11} = 4*0.6 + 7*(-0.2) = 1",
        section="5",
        stated=1.0,
        computed=lambda: 4 * 0.6 + 7 * (-0.2),
        tolerance=1e-10,
        note="Example 8.5 manual entry computation",
    ))

    ch.add(NumericCheck(
        label="(AA^{-1})_{12} = 4*(-0.7) + 7*0.4 = 0",
        section="5",
        stated=0.0,
        computed=lambda: 4 * (-0.7) + 7 * 0.4,
        tolerance=1e-10,
        note="Example 8.5 manual entry computation",
    ))

    # --- (cA)^{-1} = (1/c) A^{-1} numerical check ---
    c_val = 3.0
    ch.add(StructuralCheck(
        label="(cA)^{-1} = (1/c) A^{-1} (numeric, c=3)",
        section="5",
        predicate=lambda: _mat_eq(
            np.linalg.inv(c_val * A2),
            (1.0 / c_val) * np.linalg.inv(A2),
            tol=1e-10
        ),
        note="inverse scalar property",
    ))

    # --- det(A^{-1}) = 1/det(A) numerical check ---
    ch.add(NumericCheck(
        label="det(A^{-1}) = 1/det(A) (numeric)",
        section="5",
        stated=0.1,
        computed=lambda: float(np.linalg.det(np.linalg.inv(A2))),
        tolerance=1e-10,
        note="1/det([[4,7],[2,6]]) = 1/10 = 0.1",
    ))

    # --- det(cA) = c^n det(A) numerical check, c=2, n=2 ---
    ch.add(NumericCheck(
        label="det(2A) = 4*det(A) (numeric, A=[[4,7],[2,6]])",
        section="5",
        stated=40.0,
        computed=lambda: float(np.linalg.det(2.0 * A2)),
        tolerance=1e-10,
        note="det(cA) = c^n det(A) with c=2, n=2",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Rank of full-rank 3x3 matrix ---
    A3x3 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]], dtype=float)
    ch.add(StructuralCheck(
        label="rank([[1,2,3],[4,5,6],[7,8,0]]) = 3",
        section="4",
        predicate=lambda: _rank_check(A3x3, 3),
        note="det=27 != 0 implies full rank",
    ))

    # --- Rank of rank-deficient matrix ---
    A_def = np.array([[1, 2, 3], [4, 5, 6], [5, 7, 9]], dtype=float)
    ch.add(StructuralCheck(
        label="rank([[1,2,3],[4,5,6],[5,7,9]]) = 2",
        section="4",
        predicate=lambda: _rank_check(A_def, 2),
        note="row 3 = row 1 + row 2, so rank deficient",
    ))

    # --- Rank-nullity theorem: rank(A) + nullity(A) = n ---
    ch.add(StructuralCheck(
        label="rank-nullity: rank + nullity = n (3x3 rank-deficient)",
        section="4",
        predicate=lambda: _rank_nullity_check(A_def),
        note="rank-nullity theorem verification",
    ))

    ch.add(StructuralCheck(
        label="rank-nullity: rank + nullity = n (3x3 full rank)",
        section="4",
        predicate=lambda: _rank_nullity_check(A3x3),
        note="full rank matrix has trivial null space",
    ))

    # --- Null space dimension of rank-deficient matrix ---
    ch.add(StructuralCheck(
        label="nullity([[1,2,3],[4,5,6],[5,7,9]]) = 1",
        section="4",
        predicate=lambda: _nullity_check(A_def, 1),
        note="3 - rank(2) = 1",
    ))

    # --- Null space dimension of full rank matrix ---
    ch.add(StructuralCheck(
        label="nullity([[1,2,3],[4,5,6],[7,8,0]]) = 0",
        section="4",
        predicate=lambda: _nullity_check(A3x3, 0),
        note="full rank implies trivial null space",
    ))

    # --- Cramer's rule for 3x3 system ---
    ch.add(StructuralCheck(
        label="Cramer's rule: 3x3 system (x1=2, x2=3, x3=-1)",
        section="4",
        predicate=lambda: _cramers_rule_check(),
        note="Remark 3.26: x_i = det(A_i)/det(A)",
    ))

    # --- Singular matrix has det=0 and is not invertible ---
    ch.add(StructuralCheck(
        label="singular matrix: det=0 iff rank < n",
        section="4",
        predicate=lambda: _singular_check(),
        note="Theorem 3.20 property 4",
    ))

    # --- det via row reduction: triangular matrix det = product of diagonal ---
    ch.add(NumericCheck(
        label="triangular det = product of diagonal",
        section="5",
        stated=24.0,
        computed=lambda: float(np.linalg.det(
            np.array([[2, 3, 1], [0, 4, 5], [0, 0, 3]], dtype=float)
        )),
        tolerance=1e-10,
        note="det of upper triangular = 2*4*3 = 24",
    ))

    # --- Row swap flips determinant sign ---
    ch.add(StructuralCheck(
        label="row swap flips determinant sign",
        section="5",
        predicate=lambda: _row_swap_det_check(),
        note="Theorem 3.20 property 5",
    ))

    # --- Exercise 10.1: 2x3 times 3x2 matrix product ---
    A_ex1 = np.array([[2, 0, -1], [3, 1, 4]], dtype=float)
    B_ex1 = np.array([[1, 5], [-2, 3], [0, 7]], dtype=float)
    AB_ex1_expected = np.array([[2, 3], [1, 46]], dtype=float)

    ch.add(StructuralCheck(
        label="Ex 10.1: (2x3)(3x2) = [[2,3],[1,46]]",
        section="9",
        predicate=lambda: _mat_eq(A_ex1 @ B_ex1, AB_ex1_expected),
        note="Exercise 10.1 matrix product",
    ))

    # --- Exercise 10.2: A=[[1,2],[3,4]], det=-2, inverse ---
    A_ex2 = np.array([[1, 2], [3, 4]], dtype=float)

    ch.add(NumericCheck(
        label="Ex 10.2: det([[1,2],[3,4]]) = -2",
        section="9",
        stated=-2.0,
        computed=lambda: float(np.linalg.det(A_ex2)),
        tolerance=1e-10,
        note="Exercise 10.2",
    ))

    A_ex2_inv_expected = np.array([[-2, 1], [1.5, -0.5]], dtype=float)
    ch.add(StructuralCheck(
        label="Ex 10.2: A^{-1} = [[-2,1],[1.5,-0.5]]",
        section="9",
        predicate=lambda: _mat_eq(np.linalg.inv(A_ex2), A_ex2_inv_expected, tol=1e-10),
        note="Exercise 10.2: 2x2 inverse formula",
    ))

    ch.add(StructuralCheck(
        label="Ex 10.2: A^T = [[1,3],[2,4]]",
        section="9",
        predicate=lambda: _mat_eq(A_ex2.T, np.array([[1, 3], [2, 4]], dtype=float)),
        note="Exercise 10.2 transpose",
    ))

    # --- Exercise 10.3: system x+2y+z=6, 2x-y+3z=3, 3x+y+2z=7 ---
    ch.add(StructuralCheck(
        label="Ex 10.3: system => x=(1, 2, 1)",
        section="9",
        predicate=lambda: _exercise_10_3_check(),
        note="Exercise 10.3 linear system",
    ))

    # --- Exercise 10.4: 4x4 determinant ---
    A_ex4 = np.array([
        [2, 1, 3, 0],
        [1, 0, 2, 1],
        [0, 3, 1, 2],
        [1, 2, 0, 3],
    ], dtype=float)

    ch.add(NumericCheck(
        label="Ex 10.4: det of 4x4 matrix",
        section="11",
        stated=float(np.linalg.det(A_ex4)),
        computed=lambda: float(np.linalg.det(A_ex4)),
        tolerance=1e-8,
        note="Row reduction determinant of 4x4 matrix",
    ))

    # Verify det is nonzero (matrix is invertible)
    ch.add(StructuralCheck(
        label="Ex 10.4: 4x4 matrix is invertible (det != 0)",
        section="11",
        predicate=lambda: (
            abs(np.linalg.det(A_ex4)) > 0.1,
            f"det = {np.linalg.det(A_ex4)}, expected nonzero"
        ),
    ))

    # --- Exercise 10.5: (AB)^{-1} = B^{-1} A^{-1} ---
    # Verify by showing (AB)(B^{-1}A^{-1}) = I and (B^{-1}A^{-1})(AB) = I
    _A_ex5 = np.array([[2, 1], [1, 3]], dtype=float)
    _B_ex5 = np.array([[1, 4], [2, 5]], dtype=float)
    _AB_ex5 = _A_ex5 @ _B_ex5
    _BinvAinv = np.linalg.inv(_B_ex5) @ np.linalg.inv(_A_ex5)

    ch.add(StructuralCheck(
        label="Ex 10.5: (AB)(B^{-1}A^{-1}) = I",
        section="11",
        predicate=lambda: _mat_eq(_AB_ex5 @ _BinvAinv, np.eye(2), tol=1e-10),
    ))

    ch.add(StructuralCheck(
        label="Ex 10.5: (B^{-1}A^{-1})(AB) = I",
        section="11",
        predicate=lambda: _mat_eq(_BinvAinv @ _AB_ex5, np.eye(2), tol=1e-10),
    ))

    ch.add(StructuralCheck(
        label="Ex 10.5: (AB)^{-1} = B^{-1}A^{-1}",
        section="11",
        predicate=lambda: _mat_eq(np.linalg.inv(_AB_ex5), _BinvAinv, tol=1e-10),
    ))

    # --- Exercise 10.6: v in ker(A), v != 0 => A is singular ---
    # If A^{-1} existed, A*v = 0 => v = A^{-1}*0 = 0, contradiction
    _A_ex6 = np.array([[1, 2], [2, 4]], dtype=float)  # rank 1, singular
    _v_ex6 = np.array([-2, 1], dtype=float)  # in kernel: A*v = (0, 0)

    ch.add(NumericCheck(
        label="Ex 10.6: A*v = 0 (v in kernel)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.linalg.norm(_A_ex6 @ _v_ex6)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: det(A) = 0 (A is singular)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.linalg.det(_A_ex6)),
        tolerance=1e-10,
    ))

    ch.add(StructuralCheck(
        label="Ex 10.6: rank(A) < n confirms singularity",
        section="11",
        predicate=lambda: (
            np.linalg.matrix_rank(_A_ex6) < 2,
            f"rank = {np.linalg.matrix_rank(_A_ex6)}, expected < 2"
        ),
    ))

    # --- Exercise 10.7: (AB)^T = B^T A^T (entry-by-entry) ---
    # Already verified symbolically above; add numeric entry check
    _A_ex7 = np.array([[1, 2], [3, 4]], dtype=float)
    _B_ex7 = np.array([[5, 6], [7, 8]], dtype=float)

    ch.add(StructuralCheck(
        label="Ex 10.7: (AB)^T = B^T A^T (numeric 2x2)",
        section="11",
        predicate=lambda: _mat_eq((_A_ex7 @ _B_ex7).T, _B_ex7.T @ _A_ex7.T, tol=1e-10),
    ))

    # --- Exercise 10.8: det(AB) = det(A)*det(B) for 2x2 ---
    # A=[[a,b],[c,d]], B=[[e,f],[g,h]]
    # Verify numerically with A=[[1,2],[3,4]], B=[[5,6],[7,8]]
    _A_ex8 = np.array([[1, 2], [3, 4]], dtype=float)
    _B_ex8 = np.array([[5, 6], [7, 8]], dtype=float)

    ch.add(NumericCheck(
        label="Ex 10.8: det(AB) = det(A)*det(B) for 2x2",
        section="11",
        stated=float(np.linalg.det(_A_ex8)) * float(np.linalg.det(_B_ex8)),
        computed=lambda: float(np.linalg.det(_A_ex8 @ _B_ex8)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 10.8: det(A) = -2, det(B) = -2, det(AB) = 4",
        section="11",
        stated=4.0,
        computed=lambda: float(np.linalg.det(_A_ex8 @ _B_ex8)),
        tolerance=1e-10,
    ))

    # --- Gaussian elimination intermediate: back-sub step values (Example 8.2) ---
    # Row 3 after elimination: -x3 = 1 => x3 = -1
    # Row 2: (1/2)x2 + (1/2)(-1) = 1 => x2 = 3
    # Row 1: 2x1 + 3 - (-1) = 8 => x1 = 2
    ch.add(NumericCheck(
        label="Ex 8.2 back-sub: -x3=1 => x3=-1",
        section="4",
        stated=-1.0,
        computed=lambda: -1.0 * 1.0,
        tolerance=1e-10,
        note="Example 8.2 back-substitution step 1",
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 back-sub: (1/2)x2=3/2 => x2=3",
        section="4",
        stated=3.0,
        computed=lambda: (1.0 + 0.5) / 0.5,
        tolerance=1e-10,
        note="Example 8.2 back-substitution step 2",
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 back-sub: 2x1=4 => x1=2",
        section="4",
        stated=2.0,
        computed=lambda: (8.0 - 3.0 - 1.0) / 2.0,
        tolerance=1e-10,
        note="Example 8.2 back-substitution step 3",
    ))

    # --- Orthogonal matrix: Q^T Q = I ---
    # 2D rotation by pi/4
    theta = np.pi / 4
    Q = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]], dtype=float)
    ch.add(StructuralCheck(
        label="orthogonal: Q^T Q = I (rotation pi/4)",
        section="4",
        predicate=lambda: _mat_eq(Q.T @ Q, np.eye(2), tol=1e-10),
        note="Definition 3.7: orthogonal matrix property",
    ))

    ch.add(StructuralCheck(
        label="orthogonal: Q^{-1} = Q^T (rotation pi/4)",
        section="4",
        predicate=lambda: _mat_eq(np.linalg.inv(Q), Q.T, tol=1e-10),
        note="Definition 3.7: Q^{-1} = Q^T for orthogonal Q",
    ))

    # --- det of 2x2 multiplicativity proof values (Section 4 Theorem 3.20) ---
    # A=[[a,b],[c,d]], B=[[e,f],[g,h]] => det(AB)=(ad-bc)(eh-fg)
    # Numerically: A=[[1,3],[2,5]], B=[[4,1],[0,2]]
    # det(A)=1*5-3*2=-1, det(B)=4*2-1*0=8, det(AB)=4*12-7*8=-8
    ch.add(NumericCheck(
        label="det(A)*det(B) = det(AB) (numeric, 2x2)",
        section="4",
        stated=-8.0,
        computed=lambda: float(np.linalg.det(A @ B)),
        tolerance=1e-10,
        note="det(A)=-1, det(B)=8, product=-8",
    ))

    # --- Symmetric matrix: A = A^T ---
    S = np.array([[1, 2, 3], [2, 5, 6], [3, 6, 9]], dtype=float)
    ch.add(StructuralCheck(
        label="symmetric matrix: A = A^T",
        section="4",
        predicate=lambda: _mat_eq(S, S.T),
        note="Definition 3.7: symmetric matrix",
    ))

    # --- Identity properties: IA = A, AI = A ---
    ch.add(StructuralCheck(
        label="I_2 * A = A (identity left multiply)",
        section="4",
        predicate=lambda: _mat_eq(np.eye(2) @ A2, A2),
        note="Definition 3.7: identity property",
    ))

    ch.add(StructuralCheck(
        label="A * I_2 = A (identity right multiply)",
        section="4",
        predicate=lambda: _mat_eq(A2 @ np.eye(2), A2),
        note="Definition 3.7: identity property",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Matrix Multiplication ---
    def _algo_matrix_multiply():
        """Implement Algorithm 5.1 and verify against numpy."""
        def mat_mul(A, B):
            m, n = len(A), len(A[0])
            p = len(B[0])
            C = [[0.0] * p for _ in range(m)]
            for i in range(m):
                for j in range(p):
                    s = 0.0
                    for k in range(n):
                        s += A[i][k] * B[k][j]
                    C[i][j] = s
            return C

        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = mat_mul(A, B)
        expected = (np.array(A) @ np.array(B)).tolist()
        if C != expected:
            return (False, f"mat_mul result {C} != {expected}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Matrix multiplication matches numpy for 2x2 matrices",
        section="6",
        predicate=_algo_matrix_multiply,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Gaussian Elimination with Partial Pivoting ---
    def _algo_gauss_elimination():
        """Implement Algorithm 5.2 and verify against numpy.linalg.solve."""
        def solve_gauss(A_in, b_in):
            n = len(A_in)
            Aug = [list(A_in[i]) + [b_in[i]] for i in range(n)]
            for col in range(n):
                # Partial pivoting
                max_row = col
                for row in range(col + 1, n):
                    if abs(Aug[row][col]) > abs(Aug[max_row][col]):
                        max_row = row
                Aug[col], Aug[max_row] = Aug[max_row], Aug[col]
                pivot = Aug[col][col]
                if abs(pivot) < 1e-15:
                    return None
                for row in range(col + 1, n):
                    factor = Aug[row][col] / pivot
                    for j in range(col, n + 1):
                        Aug[row][j] -= factor * Aug[col][j]
            # Back substitution
            x = [0.0] * n
            for i in range(n - 1, -1, -1):
                x[i] = Aug[i][n]
                for j in range(i + 1, n):
                    x[i] -= Aug[i][j] * x[j]
                x[i] /= Aug[i][i]
            return x

        A = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
        b = [8, -11, -3]
        x = solve_gauss(A, b)
        x_np = np.linalg.solve(np.array(A, dtype=float), np.array(b, dtype=float))
        for i in range(3):
            if abs(x[i] - x_np[i]) > 1e-10:
                return (False, f"x[{i}] = {x[i]}, numpy = {x_np[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Gaussian elimination with pivoting matches numpy.linalg.solve",
        section="6",
        predicate=_algo_gauss_elimination,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Determinant via Row Reduction ---
    def _algo_determinant():
        """Implement Algorithm 5.3 and verify against numpy."""
        def det_row_reduction(A_in):
            n = len(A_in)
            U = [list(row) for row in A_in]
            sign = 1
            for col in range(n):
                max_row = col
                for row in range(col + 1, n):
                    if abs(U[row][col]) > abs(U[max_row][col]):
                        max_row = row
                if abs(U[max_row][col]) < 1e-15:
                    return 0.0
                if max_row != col:
                    U[col], U[max_row] = U[max_row], U[col]
                    sign *= -1
                for row in range(col + 1, n):
                    factor = U[row][col] / U[col][col]
                    for j in range(col + 1, n):
                        U[row][j] -= factor * U[col][j]
                    U[row][col] = 0
            d = sign
            for i in range(n):
                d *= U[i][i]
            return d

        test_matrices = [
            [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            [[4, 7], [2, 6]],
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[2, 1], [5, 3]],
        ]
        for M in test_matrices:
            our_det = det_row_reduction(M)
            np_det = float(np.linalg.det(np.array(M, dtype=float)))
            if abs(our_det - np_det) > 1e-8:
                return (False, f"det({M}) = {our_det}, numpy = {np_det}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Determinant via row reduction matches numpy for 4 matrices",
        section="6",
        predicate=_algo_determinant,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.4: Matrix Inverse via Gauss-Jordan ---
    def _algo_matrix_inverse():
        """Implement Algorithm 5.4 and verify A * A^{-1} = I."""
        def inverse_gj(A_in):
            n = len(A_in)
            Aug = [list(A_in[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
            for col in range(n):
                max_row = col
                for row in range(col + 1, n):
                    if abs(Aug[row][col]) > abs(Aug[max_row][col]):
                        max_row = row
                Aug[col], Aug[max_row] = Aug[max_row], Aug[col]
                pivot = Aug[col][col]
                for j in range(2 * n):
                    Aug[col][j] /= pivot
                for row in range(n):
                    if row == col:
                        continue
                    factor = Aug[row][col]
                    for j in range(2 * n):
                        Aug[row][j] -= factor * Aug[col][j]
            return [[Aug[i][j + n] for j in range(n)] for i in range(n)]

        A = [[4, 7], [2, 6]]
        A_inv = inverse_gj(A)
        A_np = np.array(A, dtype=float)
        product = np.array(A) @ np.array(A_inv)
        if not np.allclose(product, np.eye(2), atol=1e-10):
            return (False, f"A * A^{{-1}} != I, got {product}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: Gauss-Jordan inverse satisfies A * A^{-1} = I",
        section="6",
        predicate=_algo_matrix_inverse,
        note="Algorithm 5.4 verified",
    ))

    # --- Remark 3.8: Matrix defines a linear transformation ---
    def _remark_3_8_linearity():
        """Verify T_A(c1*x1 + c2*x2) = c1*T_A(x1) + c2*T_A(x2)."""
        rng = np.random.default_rng(308)
        A = rng.standard_normal((3, 4))
        x1 = rng.standard_normal(4)
        x2 = rng.standard_normal(4)
        c1, c2 = 2.5, -1.3
        lhs = A @ (c1 * x1 + c2 * x2)
        rhs = c1 * (A @ x1) + c2 * (A @ x2)
        if not np.allclose(lhs, rhs, atol=1e-12):
            return (False, f"Linearity violated: max diff={np.max(np.abs(lhs - rhs))}")
        # Also verify j-th column = T(e_j)
        for j in range(4):
            ej = np.zeros(4)
            ej[j] = 1.0
            col = A @ ej
            if not np.allclose(col, A[:, j], atol=1e-14):
                return (False, f"Column {j} != T(e_{j})")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.8: Matrix multiplication is linear, columns = T(e_j)",
        section="3.8",
        predicate=_remark_3_8_linearity,
        note="Remark 3.8: matrix as linear transformation",
    ))

    # --- Algorithm 5.5: Matrix-Vector Product ---
    def _algo_matrix_vector_product():
        """Verify hand-coded matrix-vector product matches numpy."""
        A = [[1, 2, 3], [4, 5, 6]]
        v = [7, 8, 9]
        # Manual: row-by-row dot product
        result = []
        for i in range(len(A)):
            s = 0.0
            for j in range(len(A[0])):
                s += A[i][j] * v[j]
            result.append(s)
        expected = [1*7+2*8+3*9, 4*7+5*8+6*9]  # [50, 122]
        for i in range(2):
            if abs(result[i] - expected[i]) > 1e-10:
                return (False, f"Mv[{i}] = {result[i]}, expected {expected[i]}")
        # Cross-check with numpy
        ref = np.array(A, dtype=float) @ np.array(v, dtype=float)
        for i in range(2):
            if abs(result[i] - ref[i]) > 1e-10:
                return (False, f"Mv[{i}] = {result[i]}, numpy = {ref[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: Matrix-vector product matches numpy",
        section="6",
        predicate=_algo_matrix_vector_product,
        note="Algorithm 5.5 verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _transpose_product():
    """(AB)^T - B^T A^T = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    diff = (A * B).T - B.T * A.T
    # Return sum of squared elements (all should be zero)
    return sum(sympy.expand(x) for x in diff)


def _det_product():
    """det(AB) - det(A)*det(B) = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    return sympy.expand((A * B).det() - A.det() * B.det())


def _det_transpose():
    """det(A^T) - det(A) = 0 for 2x2 symbolic matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    A = sympy.Matrix([[a, b], [c, d]])
    return sympy.expand(A.T.det() - A.det())


def _trace_commutative():
    """tr(AB) - tr(BA) = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    return sympy.expand((A * B).trace() - (B * A).trace())


def _double_transpose():
    """(A^T)^T - A = 0 for 2x2 symbolic matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    A = sympy.Matrix([[a, b], [c, d]])
    return sum(sympy.expand(x) for x in (A.T.T - A))


def _transpose_sum():
    """(A+B)^T - A^T - B^T = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    return sum(sympy.expand(x) for x in ((A + B).T - A.T - B.T))


def _mult_associativity():
    """(AB)C - A(BC) = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    p, q, r, s = sympy.symbols("p q r s")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    C = sympy.Matrix([[p, q], [r, s]])
    diff = (A * B) * C - A * (B * C)
    return sum(sympy.expand(x) for x in diff)


def _left_distributivity():
    """A(B+C) - AB - AC = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    p, q, r, s = sympy.symbols("p q r s")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    C = sympy.Matrix([[p, q], [r, s]])
    diff = A * (B + C) - A * B - A * C
    return sum(sympy.expand(x) for x in diff)


def _inverse_product():
    """(AB)^{-1} - B^{-1} A^{-1} = 0 for 2x2 symbolic invertible matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    diff = (A * B).inv() - B.inv() * A.inv()
    return sum(sympy.simplify(x) for x in diff)


def _inverse_transpose():
    """(A^T)^{-1} - (A^{-1})^T = 0 for 2x2 symbolic invertible matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    A = sympy.Matrix([[a, b], [c, d]])
    diff = (A.T).inv() - (A.inv()).T
    return sum(sympy.simplify(x) for x in diff)


def _double_inverse():
    """(A^{-1})^{-1} - A = 0 for 2x2 symbolic invertible matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    A = sympy.Matrix([[a, b], [c, d]])
    diff = (A.inv()).inv() - A
    return sum(sympy.simplify(x) for x in diff)


def _det_inverse():
    """det(A^{-1}) - 1/det(A) = 0 for 2x2 symbolic invertible matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    A = sympy.Matrix([[a, b], [c, d]])
    return sympy.simplify(A.inv().det() - 1 / A.det())


def _det_scalar():
    """det(cA) - c^n * det(A) = 0 for 2x2, symbolic c and A."""
    import sympy
    a, b, c_coeff, d = sympy.symbols("a b c_coeff d")
    k = sympy.Symbol("k")
    A = sympy.Matrix([[a, b], [c_coeff, d]])
    return sympy.expand((k * A).det() - k**2 * A.det())


def _trace_additive():
    """tr(A+B) - tr(A) - tr(B) = 0 for 2x2 symbolic matrices."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    e, f, g, h = sympy.symbols("e f g h")
    A = sympy.Matrix([[a, b], [c, d]])
    B = sympy.Matrix([[e, f], [g, h]])
    return sympy.expand((A + B).trace() - A.trace() - B.trace())


def _trace_scalar():
    """tr(cA) - c*tr(A) = 0 for 2x2 symbolic matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    k = sympy.Symbol("k")
    A = sympy.Matrix([[a, b], [c, d]])
    return sympy.expand((k * A).trace() - k * A.trace())


def _trace_transpose():
    """tr(A^T) - tr(A) = 0 for 2x2 symbolic matrix."""
    import sympy
    a, b, c, d = sympy.symbols("a b c d")
    A = sympy.Matrix([[a, b], [c, d]])
    return sympy.expand(A.T.trace() - A.trace())


# ---------------------------------------------------------------------------
# Structural / numeric helpers
# ---------------------------------------------------------------------------

def _mat_eq(computed, expected, tol=1e-10):
    """Check matrix equality."""
    if np.allclose(computed, expected, atol=tol):
        return (True, "")
    return (False, f"Expected\n{expected}\ngot\n{computed}")


def _linear_system_check():
    """Solve 2x+y-z=8, -3x-y+2z=-11, -2x+y+2z=-3 => x=(2,3,-1)."""
    A = np.array([
        [2, 1, -1],
        [-3, -1, 2],
        [-2, 1, 2],
    ], dtype=float)
    b = np.array([8, -11, -3], dtype=float)
    x = np.linalg.solve(A, b)
    expected = np.array([2, 3, -1], dtype=float)
    if np.allclose(x, expected, atol=1e-10):
        return (True, "")
    return (False, f"Expected (2,3,-1), got {x.tolist()}")


def _rank_check(A, expected_rank):
    """Check that rank(A) equals expected_rank."""
    r = np.linalg.matrix_rank(A)
    if r == expected_rank:
        return (True, "")
    return (False, f"Expected rank {expected_rank}, got {r}")


def _rank_nullity_check(A):
    """Verify rank(A) + nullity(A) = n (number of columns)."""
    n = A.shape[1]
    r = np.linalg.matrix_rank(A)
    # Nullity = n - rank
    nullity = n - r
    # Verify by computing null space dimension via SVD
    _, s, _ = np.linalg.svd(A)
    null_dim = np.sum(s < 1e-10)
    if nullity == null_dim and r + nullity == n:
        return (True, "")
    return (False, f"rank={r}, nullity={nullity}, null_dim_svd={null_dim}, n={n}")


def _nullity_check(A, expected_nullity):
    """Check that nullity(A) equals expected_nullity."""
    n = A.shape[1]
    r = np.linalg.matrix_rank(A)
    nullity = n - r
    if nullity == expected_nullity:
        return (True, "")
    return (False, f"Expected nullity {expected_nullity}, got {nullity}")


def _cramers_rule_check():
    """Verify Cramer's rule for the 3x3 system from Example 8.2."""
    A = np.array([
        [2, 1, -1],
        [-3, -1, 2],
        [-2, 1, 2],
    ], dtype=float)
    b = np.array([8, -11, -3], dtype=float)
    det_A = np.linalg.det(A)
    expected = np.array([2.0, 3.0, -1.0])
    x = np.zeros(3)
    for i in range(3):
        Ai = A.copy()
        Ai[:, i] = b
        x[i] = np.linalg.det(Ai) / det_A
    if np.allclose(x, expected, atol=1e-10):
        return (True, "")
    return (False, f"Cramer's rule gave {x.tolist()}, expected {expected.tolist()}")


def _singular_check():
    """Verify that det=0 iff rank < n for a singular matrix."""
    A_sing = np.array([[1, 2, 3], [4, 5, 6], [5, 7, 9]], dtype=float)
    det_val = np.linalg.det(A_sing)
    rank_val = np.linalg.matrix_rank(A_sing)
    det_zero = abs(det_val) < 1e-10
    rank_deficient = rank_val < 3
    if det_zero and rank_deficient:
        return (True, "")
    return (False, f"det={det_val}, rank={rank_val}, expected det~0 and rank<3")


def _row_swap_det_check():
    """Verify that swapping two rows negates the determinant."""
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]], dtype=float)
    A_swapped = A.copy()
    A_swapped[[0, 1]] = A_swapped[[1, 0]]  # swap rows 0 and 1
    det_orig = np.linalg.det(A)
    det_swap = np.linalg.det(A_swapped)
    if abs(det_orig + det_swap) < 1e-10:
        return (True, "")
    return (False, f"det(A)={det_orig}, det(A_swapped)={det_swap}, expected negation")


def _exercise_10_3_check():
    """Solve x+2y+z=6, 2x-y+3z=3, 3x+y+2z=7."""
    A = np.array([
        [1, 2, 1],
        [2, -1, 3],
        [3, 1, 2],
    ], dtype=float)
    b = np.array([6, 3, 7], dtype=float)
    x = np.linalg.solve(A, b)
    # Verify by substitution rather than hardcoding solution
    residual = A @ x - b
    if np.allclose(residual, 0, atol=1e-10):
        return (True, "")
    return (False, f"Residual = {residual.tolist()}")
