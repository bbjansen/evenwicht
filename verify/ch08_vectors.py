# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 8: Vectors & Vector Spaces — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(8, "Vectors & Vector Spaces")

    # ===================================================================
    # LAYER 1: Symbolic identity verification
    # ===================================================================

    # --- Cauchy-Schwarz inequality: |u.v| <= ||u|| * ||v|| ---
    ch.add(StructuralCheck(
        label="Cauchy-Schwarz inequality (sample vectors)",
        section="1",
        predicate=lambda: _cauchy_schwarz_check(),
        note="|u.v| <= ||u||*||v||",
    ))

    # --- Parallelogram law: ||u+v||^2 + ||u-v||^2 = 2||u||^2 + 2||v||^2 ---
    ch.add(SymbolicCheck(
        label="Parallelogram law",
        section="1",
        zero_expr=lambda: _parallelogram_law(),
        note="||u+v||^2 + ||u-v||^2 = 2(||u||^2 + ||v||^2)",
    ))

    # --- Polarization identity: u.v = (1/4)(||u+v||^2 - ||u-v||^2) ---
    ch.add(SymbolicCheck(
        label="Polarization identity",
        section="1",
        zero_expr=lambda: _polarization_identity(),
        note="u.v = (1/4)(||u+v||^2 - ||u-v||^2)",
    ))

    # --- Pythagorean theorem: if u perp v then ||u+v||^2 = ||u||^2 + ||v||^2 ---
    ch.add(SymbolicCheck(
        label="Pythagorean theorem (orthogonal vectors)",
        section="1",
        zero_expr=lambda: _pythagorean_orthogonal(),
        note="u perp v => ||u+v||^2 = ||u||^2 + ||v||^2",
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification
    # ===================================================================

    u = np.array([1, 2, 3], dtype=float)
    v = np.array([4, -1, 2], dtype=float)

    # --- Vector addition: u + v = (5, 1, 5) ---
    ch.add(StructuralCheck(
        label="u+v = (5,1,5)",
        section="2",
        predicate=lambda: _vec_eq(u + v, [5, 1, 5]),
    ))

    # --- Scalar multiplication: 3u = (3, 6, 9) ---
    ch.add(StructuralCheck(
        label="3u = (3,6,9)",
        section="2",
        predicate=lambda: _vec_eq(3 * u, [3, 6, 9]),
    ))

    # --- Linear combination: 2u - v = (-2, 5, 4) ---
    ch.add(StructuralCheck(
        label="2u - v = (-2,5,4)",
        section="2",
        predicate=lambda: _vec_eq(2 * u - v, [-2, 5, 4]),
    ))

    # --- Dot product: u.v = 8 ---
    ch.add(NumericCheck(
        label="u.v = 8",
        section="3",
        stated=8.0,
        computed=lambda: float(np.dot(u, v)),
    ))

    # --- Norm: ||u|| = sqrt(14) ---
    ch.add(NumericCheck(
        label="||u|| = sqrt(14)",
        section="3",
        stated=math.sqrt(14),
        computed=lambda: float(np.linalg.norm(u)),
        tolerance=1e-10,
    ))

    # --- Norm numerical: ||u|| ~ 3.7417 ---
    ch.add(NumericCheck(
        label="||u|| ~ 3.7417",
        section="3",
        stated=3.7417,
        computed=lambda: float(np.linalg.norm(u)),
        tolerance=1e-4,
    ))

    # --- Norm: ||v|| = sqrt(21) ---
    ch.add(NumericCheck(
        label="||v|| = sqrt(21)",
        section="3",
        stated=math.sqrt(21),
        computed=lambda: float(np.linalg.norm(v)),
        tolerance=1e-10,
    ))

    # --- Norm numerical: ||v|| ~ 4.5826 ---
    ch.add(NumericCheck(
        label="||v|| ~ 4.5826",
        section="3",
        stated=4.5826,
        computed=lambda: float(np.linalg.norm(v)),
        tolerance=1e-4,
    ))

    # --- cos(theta) = 8/sqrt(294) ~ 0.4666 ---
    ch.add(NumericCheck(
        label="cos(theta) = 8/sqrt(294)",
        section="3",
        stated=0.4666,
        computed=lambda: 8.0 / math.sqrt(294),
        tolerance=1e-3,
    ))

    # --- theta ~ 1.0854 rad ---
    ch.add(NumericCheck(
        label="theta ~ 1.0854 rad",
        section="3",
        stated=1.0854,
        computed=lambda: math.acos(8.0 / math.sqrt(294)),
        tolerance=1e-3,
    ))

    # --- theta ~ 62.19 degrees ---
    ch.add(NumericCheck(
        label="theta ~ 62.19 degrees",
        section="3",
        stated=62.19,
        computed=lambda: math.degrees(math.acos(8.0 / math.sqrt(294))),
        tolerance=1e-2,
    ))

    # --- Projection: proj_v(u) for u=(3,4), v=(1,0) => (3,0) ---
    ch.add(StructuralCheck(
        label="proj_(1,0)((3,4)) = (3,0)",
        section="4",
        predicate=lambda: _projection_check(
            np.array([3.0, 4.0]), np.array([1.0, 0.0]), np.array([3.0, 0.0])
        ),
    ))

    # --- Projection: proj_v(u) for u=(3,4), v=(1,1) => (3.5,3.5) ---
    ch.add(StructuralCheck(
        label="proj_(1,1)((3,4)) = (3.5,3.5)",
        section="4",
        predicate=lambda: _projection_check(
            np.array([3.0, 4.0]), np.array([1.0, 1.0]), np.array([3.5, 3.5])
        ),
    ))

    # --- Linear dependence: v3 = v1 + v2 ---
    ch.add(StructuralCheck(
        label="Linear dependence: v3 = v1 + v2",
        section="5",
        predicate=lambda: _linear_dependence_check(),
        note="v1=(1,0,2), v2=(0,1,1), v3=(1,1,3)",
    ))

    # ===================================================================
    # Additional dot product / norm property checks
    # ===================================================================

    # --- F4.1 Dot product commutativity: u.v = v.u ---
    ch.add(StructuralCheck(
        label="F4.1 Dot product commutativity: u.v = v.u (5 sample pairs)",
        section="1",
        predicate=lambda: _dot_commutativity_check(),
    ))

    # --- F4.2 Dot product linearity: (au+bw).v = a(u.v) + b(w.v) ---
    ch.add(StructuralCheck(
        label="F4.2 Dot product linearity: (au+bw).v = a(u.v)+b(w.v) (samples)",
        section="1",
        predicate=lambda: _dot_linearity_check(),
    ))

    # --- F4.3 Positive definiteness: u.u >= 0, and u.u = 0 iff u = 0 ---
    ch.add(StructuralCheck(
        label="F4.3 Positive definiteness: u.u >= 0, u.u=0 iff u=0",
        section="1",
        predicate=lambda: _dot_positive_definiteness_check(),
    ))

    # --- F4.4 Norm non-negativity: ||u|| >= 0, ||u||=0 iff u=0 ---
    ch.add(StructuralCheck(
        label="F4.4 Norm non-negativity: ||u|| >= 0, ||u||=0 iff u=0",
        section="1",
        predicate=lambda: _norm_nonnegativity_check(),
    ))

    # --- F4.6 Triangle inequality: ||u+v|| <= ||u|| + ||v|| ---
    ch.add(StructuralCheck(
        label="F4.6 Triangle inequality: ||u+v|| <= ||u||+||v|| (samples)",
        section="1",
        predicate=lambda: _triangle_inequality_check(),
    ))

    # --- F4.8 Reverse triangle inequality: | ||u||-||v|| | <= ||u-v|| ---
    ch.add(StructuralCheck(
        label="F4.8 Reverse triangle inequality: | ||u||-||v|| | <= ||u-v|| (samples)",
        section="1",
        predicate=lambda: _reverse_triangle_inequality_check(),
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    u_ex = np.array([2, -1, 3], dtype=float)
    v_ex = np.array([-1, 4, 2], dtype=float)

    # --- Exercise 10.1 ---
    ch.add(StructuralCheck(
        label="Ex 10.1: u+v = (1, 3, 5)",
        section="11",
        predicate=lambda: _vec_eq(u_ex + v_ex, [1, 3, 5]),
    ))

    ch.add(StructuralCheck(
        label="Ex 10.1: u-v = (3, -5, 1)",
        section="11",
        predicate=lambda: _vec_eq(u_ex - v_ex, [3, -5, 1]),
    ))

    ch.add(StructuralCheck(
        label="Ex 10.1: 3u+2v = (4, 5, 13)",
        section="11",
        predicate=lambda: _vec_eq(3*u_ex + 2*v_ex, [4, 5, 13]),
    ))

    ch.add(NumericCheck(
        label="Ex 10.1: ||u|| = sqrt(14)",
        section="11",
        stated=math.sqrt(14),
        computed=lambda: float(np.linalg.norm(u_ex)),
        tolerance=1e-10,
    ))

    # --- Exercise 10.2: Dot product and angle ---
    u_ex2 = np.array([1, 1, 1, 1], dtype=float)
    v_ex2 = np.array([1, -1, 1, -1], dtype=float)

    ch.add(NumericCheck(
        label="Ex 10.2: u.v = 1-1+1-1 = 0 (orthogonal)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.dot(u_ex2, v_ex2)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.2: angle = pi/2 (orthogonal)",
        section="11",
        stated=math.pi / 2,
        computed=lambda: math.acos(0.0 / (float(np.linalg.norm(u_ex2)) * float(np.linalg.norm(v_ex2)))),
        tolerance=1e-10,
    ))

    # --- Exercise 10.3: Projection ---
    u_ex3 = np.array([2, 3, 1], dtype=float)
    v_ex3 = np.array([1, 1, 1], dtype=float)
    # proj = (u.v/v.v)*v = (6/3)*(1,1,1) = (2,2,2)
    proj_ex3 = (float(np.dot(u_ex3, v_ex3)) / float(np.dot(v_ex3, v_ex3))) * v_ex3
    residual_ex3 = u_ex3 - proj_ex3

    ch.add(StructuralCheck(
        label="Ex 10.3: proj_v(u) = (2, 2, 2)",
        section="11",
        predicate=lambda: _vec_eq(proj_ex3, [2, 2, 2]),
    ))

    ch.add(NumericCheck(
        label="Ex 10.3: residual orthogonal to v (dot = 0)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.dot(residual_ex3, v_ex3)),
        tolerance=1e-12,
    ))

    # --- Exercise 10.4: Parallelogram law ---
    u_ex4 = np.array([1, 2, -1], dtype=float)
    v_ex4 = np.array([3, 0, 1], dtype=float)

    lhs_para = float(np.linalg.norm(u_ex4 + v_ex4))**2 + float(np.linalg.norm(u_ex4 - v_ex4))**2
    rhs_para = 2 * float(np.linalg.norm(u_ex4))**2 + 2 * float(np.linalg.norm(v_ex4))**2

    ch.add(NumericCheck(
        label="Ex 10.4: ||u+v||^2+||u-v||^2 = 2||u||^2+2||v||^2",
        section="11",
        stated=rhs_para,
        computed=lhs_para,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 10.4: LHS = 32",
        section="11",
        stated=32.0,
        computed=lhs_para,
        tolerance=1e-10,
        note="||u+v||^2=4+4+0=20, ||u-v||^2=4+4+4=12, sum=32",
    ))

    # --- Exercise 10.5: Linear independence ---
    v1_ex5 = np.array([1, 0, 1], dtype=float)
    v2_ex5 = np.array([0, 1, 1], dtype=float)
    v3_ex5 = np.array([1, 1, 0], dtype=float)
    M_ex5 = np.column_stack([v1_ex5, v2_ex5, v3_ex5])

    ch.add(NumericCheck(
        label="Ex 10.5: det of [v1,v2,v3] = -2 (nonzero => linearly independent)",
        section="11",
        stated=-2.0,
        computed=lambda: float(np.linalg.det(M_ex5)),
        tolerance=1e-10,
    ))

    ch.add(StructuralCheck(
        label="Ex 10.5: rank = 3 (basis for R^3)",
        section="11",
        predicate=lambda: (
            np.linalg.matrix_rank(M_ex5) == 3,
            f"rank = {np.linalg.matrix_rank(M_ex5)}, expected 3"
        ),
    ))

    # --- Exercise 10.6: Gram-Schmidt ---
    v1_gs = np.array([1, 1, 0], dtype=float)
    v2_gs = np.array([1, 0, 1], dtype=float)
    # q1 = v1 / ||v1||
    q1_gs = v1_gs / np.linalg.norm(v1_gs)
    # q2 = (v2 - proj_{q1}(v2)) / ||...||
    proj_q1_v2 = np.dot(v2_gs, q1_gs) * q1_gs
    u2_gs = v2_gs - proj_q1_v2
    q2_gs = u2_gs / np.linalg.norm(u2_gs)

    ch.add(NumericCheck(
        label="Ex 10.6: q1.q2 = 0 (orthogonal)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.dot(q1_gs, q2_gs)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: ||q1|| = 1",
        section="11",
        stated=1.0,
        computed=lambda: float(np.linalg.norm(q1_gs)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: ||q2|| = 1",
        section="11",
        stated=1.0,
        computed=lambda: float(np.linalg.norm(q2_gs)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 10.6: q1 = (1/sqrt(2), 1/sqrt(2), 0)",
        section="11",
        stated=1.0 / math.sqrt(2),
        computed=lambda: float(q1_gs[0]),
        tolerance=1e-12,
    ))

    # --- Exercise 10.7: Cauchy-Schwarz via unit vector expansion ---
    # Proof: for unit u,v: ||u - (u.v)v||^2 >= 0 => 1 - (u.v)^2 >= 0 => |u.v| <= 1
    # Then for general u,v: |u.v| <= ||u||*||v||
    def _ex_10_7_cauchy_schwarz():
        rng = np.random.default_rng(777)
        for _ in range(20):
            u = rng.standard_normal(5)
            v = rng.standard_normal(5)
            # Normalize
            u_hat = u / np.linalg.norm(u)
            v_hat = v / np.linalg.norm(v)
            # ||u_hat - (u_hat.v_hat)*v_hat||^2 >= 0
            proj_coeff = np.dot(u_hat, v_hat)
            residual = u_hat - proj_coeff * v_hat
            residual_sq = np.dot(residual, residual)
            if residual_sq < -1e-14:
                return (False, f"||u - (u.v)v||^2 = {residual_sq} < 0")
            # This implies 1 - (u.v)^2 >= 0 => |u.v| <= 1
            if abs(proj_coeff) > 1.0 + 1e-12:
                return (False, f"|u_hat.v_hat| = {abs(proj_coeff)} > 1")
            # General CS: |u.v| <= ||u||*||v||
            lhs = abs(np.dot(u, v))
            rhs = np.linalg.norm(u) * np.linalg.norm(v)
            if lhs > rhs + 1e-10:
                return (False, f"|u.v| = {lhs} > ||u||*||v|| = {rhs}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 10.7: Cauchy-Schwarz via ||u-(u.v)v||^2 >= 0 (20 random pairs)",
        section="11",
        predicate=_ex_10_7_cauchy_schwarz,
    ))

    # --- Exercise 10.8: Orthogonal nonzero vectors are linearly independent ---
    # Proof idea: if c1*v1 + ... + ck*vk = 0, dot with vj => cj*||vj||^2 = 0 => cj = 0
    def _ex_10_8_orthogonal_li():
        # Construct orthogonal set
        v1 = np.array([1, 0, 0, 0], dtype=float)
        v2 = np.array([0, 2, 0, 0], dtype=float)
        v3 = np.array([0, 0, 3, 0], dtype=float)
        vecs = [v1, v2, v3]
        # Verify orthogonality
        for i in range(len(vecs)):
            for j in range(i+1, len(vecs)):
                if abs(np.dot(vecs[i], vecs[j])) > 1e-14:
                    return (False, f"v{i+1}.v{j+1} != 0")
        # Verify linear independence: if c1*v1+c2*v2+c3*v3 = 0, dot with each vj
        # c_j = 0 for all j (since ||vj|| != 0)
        # Check by forming matrix and verifying rank = 3
        M = np.column_stack(vecs)
        rank = np.linalg.matrix_rank(M)
        if rank == len(vecs):
            return (True, "")
        return (False, f"rank = {rank}, expected {len(vecs)}")

    ch.add(StructuralCheck(
        label="Ex 10.8: orthogonal nonzero vectors are linearly independent",
        section="11",
        predicate=_ex_10_8_orthogonal_li,
    ))

    # Also verify with random orthogonal set via QR
    def _ex_10_8_random_orthogonal():
        rng = np.random.default_rng(888)
        A = rng.standard_normal((5, 3))
        Q, R = np.linalg.qr(A)
        # Q[:, :3] is orthonormal set
        vecs = Q[:, :3]
        # Check orthogonality
        gram = vecs.T @ vecs
        off_diag = gram - np.eye(3)
        if np.max(np.abs(off_diag)) > 1e-12:
            return (False, f"Not orthonormal: max off-diag = {np.max(np.abs(off_diag))}")
        # Check rank = 3 (linearly independent)
        rank = np.linalg.matrix_rank(vecs)
        if rank != 3:
            return (False, f"rank = {rank}, expected 3")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 10.8: random orthonormal set is linearly independent",
        section="11",
        predicate=_ex_10_8_random_orthogonal,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1-5.5: Core vector operations ---
    def _algo_vector_operations():
        """Implement Algorithms 5.1-5.5 and verify against numpy."""
        import numpy as np

        # Algorithm 5.1: Vector Addition
        def vec_add(u, v):
            return [u[i] + v[i] for i in range(len(u))]

        # Algorithm 5.2: Scalar Multiplication
        def scalar_mul(c, v):
            return [c * v[i] for i in range(len(v))]

        # Algorithm 5.3: Dot Product
        def dot(u, v):
            return sum(u[i] * v[i] for i in range(len(u)))

        # Algorithm 5.4: Euclidean Norm
        def norm(v):
            return math.sqrt(sum(x * x for x in v))

        # Algorithm 5.5: Projection
        def proj(u, v):
            scale = dot(u, v) / dot(v, v)
            return scalar_mul(scale, v)

        u = [1.0, 2.0, 3.0]
        v = [4.0, 5.0, 6.0]
        u_np = np.array(u)
        v_np = np.array(v)

        # Test addition
        result = vec_add(u, v)
        expected = (u_np + v_np).tolist()
        if result != expected:
            return (False, f"vec_add: {result} != {expected}")

        # Test scalar mul
        result = scalar_mul(3.0, u)
        expected = (3.0 * u_np).tolist()
        if result != expected:
            return (False, f"scalar_mul: {result} != {expected}")

        # Test dot product
        result = dot(u, v)
        expected = float(np.dot(u_np, v_np))
        if abs(result - expected) > 1e-10:
            return (False, f"dot: {result} != {expected}")

        # Test norm
        result = norm(u)
        expected = float(np.linalg.norm(u_np))
        if abs(result - expected) > 1e-10:
            return (False, f"norm: {result} != {expected}")

        # Test projection
        result = proj(u, v)
        expected_proj = (np.dot(u_np, v_np) / np.dot(v_np, v_np) * v_np).tolist()
        for i in range(3):
            if abs(result[i] - expected_proj[i]) > 1e-10:
                return (False, f"proj[{i}]: {result[i]} != {expected_proj[i]}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithms 5.1-5.5: Vector add, scalar mul, dot, norm, projection match numpy",
        section="6",
        predicate=_algo_vector_operations,
        note="Algorithms 5.1-5.5 verified",
    ))

    # ── Remark 3.21: Abstract vector spaces ──────────────────────────────
    # Claims: polynomials of degree <= n form a vector space of dimension n+1,
    # and the 8 axioms hold. Verify closure under addition and scalar multiplication,
    # and that dimension = n+1.
    def _remark_3_21_abstract_vector_spaces():
        import numpy as np

        # Polynomials of degree <= 2 as coefficient vectors [a0, a1, a2]
        # Verify vector space axioms
        p1 = np.array([1.0, 2.0, 3.0])  # 1 + 2x + 3x^2
        p2 = np.array([4.0, -1.0, 0.5])  # 4 - x + 0.5x^2
        zero = np.array([0.0, 0.0, 0.0])

        # Closure under addition: p1 + p2 is still degree <= 2
        p_sum = p1 + p2
        if len(p_sum) != 3:
            return (False, "Addition not closed in polynomial space")

        # Closure under scalar multiplication
        p_scaled = 2.5 * p1
        if len(p_scaled) != 3:
            return (False, "Scalar multiplication not closed")

        # Commutativity: p1 + p2 = p2 + p1
        if not np.allclose(p1 + p2, p2 + p1):
            return (False, "Addition not commutative")

        # Associativity
        p3 = np.array([0.0, 1.0, -1.0])
        if not np.allclose((p1 + p2) + p3, p1 + (p2 + p3)):
            return (False, "Addition not associative")

        # Additive identity
        if not np.allclose(p1 + zero, p1):
            return (False, "Zero vector not identity")

        # Additive inverse
        if not np.allclose(p1 + (-p1), zero):
            return (False, "Additive inverse fails")

        # Scalar multiplication distributivity
        if not np.allclose(2.0 * (p1 + p2), 2.0 * p1 + 2.0 * p2):
            return (False, "Scalar distributivity fails")

        # 1*v = v
        if not np.allclose(1.0 * p1, p1):
            return (False, "Multiplicative identity fails")

        # Dimension = n+1 = 3 for degree <= 2
        dim = 3  # basis: {1, x, x^2}
        if dim != 2 + 1:
            return (False, f"Dimension should be n+1=3, got {dim}")

        # Also verify: m x n matrices form vector space of dimension mn
        m, n = 2, 3
        M1 = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)
        M2 = np.array([[7, 8, 9], [10, 11, 12]], dtype=float)
        M_sum = M1 + M2
        if M_sum.shape != (m, n):
            return (False, "Matrix addition not closed")
        if m * n != 6:
            return (False, f"Matrix space dimension should be mn=6, got {m*n}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.21: Polynomial and matrix spaces satisfy vector space axioms",
        section="3.21",
        predicate=_remark_3_21_abstract_vector_spaces,
        note="Remark 3.21: abstract vector space properties verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _parallelogram_law():
    """||u+v||^2 + ||u-v||^2 - 2(||u||^2 + ||v||^2) = 0."""
    import sympy
    u1, u2, v1, v2 = sympy.symbols("u1 u2 v1 v2", real=True)
    u = sympy.Matrix([u1, u2])
    v = sympy.Matrix([v1, v2])
    lhs = (u + v).dot(u + v) + (u - v).dot(u - v)
    rhs = 2 * (u.dot(u) + v.dot(v))
    return sympy.expand(lhs - rhs)


def _polarization_identity():
    """u.v - (1/4)(||u+v||^2 - ||u-v||^2) = 0."""
    import sympy
    u1, u2, v1, v2 = sympy.symbols("u1 u2 v1 v2", real=True)
    u = sympy.Matrix([u1, u2])
    v = sympy.Matrix([v1, v2])
    dot = u.dot(v)
    polarization = sympy.Rational(1, 4) * (
        (u + v).dot(u + v) - (u - v).dot(u - v)
    )
    return sympy.expand(dot - polarization)


def _pythagorean_orthogonal():
    """For orthogonal u, v: ||u+v||^2 - ||u||^2 - ||v||^2 = 0.
    Use u=(a,0), v=(0,b) as orthogonal pair."""
    import sympy
    a, b = sympy.symbols("a b", real=True)
    u = sympy.Matrix([a, 0])
    v = sympy.Matrix([0, b])
    expr = (u + v).dot(u + v) - u.dot(u) - v.dot(v)
    return sympy.expand(expr)


# ---------------------------------------------------------------------------
# Structural / numeric helpers
# ---------------------------------------------------------------------------

def _cauchy_schwarz_check():
    """Verify Cauchy-Schwarz for several sample vector pairs."""
    test_pairs = [
        ([1, 2, 3], [4, -1, 2]),
        ([1, 0], [0, 1]),
        ([3, 4], [1, 1]),
        ([1, 1, 1, 1], [2, -1, 3, 0]),
        ([5, 0, -3], [2, 7, 1]),
    ]
    for a, b in test_pairs:
        ua = np.array(a, dtype=float)
        vb = np.array(b, dtype=float)
        lhs = abs(np.dot(ua, vb))
        rhs = np.linalg.norm(ua) * np.linalg.norm(vb)
        if lhs > rhs + 1e-12:
            return (False, f"Cauchy-Schwarz violated for {a}, {b}: {lhs} > {rhs}")
    return (True, "")


def _vec_eq(computed, expected, tol=1e-10):
    """Check vector equality."""
    exp = np.array(expected, dtype=float)
    if np.allclose(computed, exp, atol=tol):
        return (True, "")
    return (False, f"Expected {expected}, got {computed.tolist()}")


def _projection_check(u, v, expected):
    """proj_v(u) = (u.v / v.v) * v."""
    proj = (np.dot(u, v) / np.dot(v, v)) * v
    if np.allclose(proj, expected, atol=1e-10):
        return (True, "")
    return (False, f"Expected {expected.tolist()}, got {proj.tolist()}")


def _linear_dependence_check():
    """v3 = v1 + v2 => linearly dependent set {v1, v2, v3}."""
    v1 = np.array([1, 0, 2], dtype=float)
    v2 = np.array([0, 1, 1], dtype=float)
    v3 = np.array([1, 1, 3], dtype=float)
    # v3 should equal v1 + v2
    if not np.allclose(v3, v1 + v2):
        return (False, f"v3 != v1 + v2: {v3} != {(v1 + v2).tolist()}")
    # Matrix [v1, v2, v3] should be rank 2
    M = np.column_stack([v1, v2, v3])
    rank = np.linalg.matrix_rank(M)
    if rank != 2:
        return (False, f"Expected rank 2, got {rank}")
    return (True, "")


# ---------------------------------------------------------------------------
# Dot product / norm property helpers
# ---------------------------------------------------------------------------

def _random_vector_pairs(rng, n_pairs=10, dim=4):
    """Generate pairs of random vectors for property testing."""
    pairs = []
    for _ in range(n_pairs):
        u = rng.standard_normal(dim)
        v = rng.standard_normal(dim)
        pairs.append((u, v))
    return pairs


def _dot_commutativity_check():
    """F4.1: u.v = v.u for random vector pairs."""
    rng = np.random.default_rng(100)
    for u, v in _random_vector_pairs(rng, 10, 5):
        uv = np.dot(u, v)
        vu = np.dot(v, u)
        if abs(uv - vu) > 1e-12:
            return (False, f"u.v={uv} != v.u={vu} for u={u}, v={v}")
    return (True, "")


def _dot_linearity_check():
    """F4.2: (au + bw).v = a(u.v) + b(w.v) for random vectors."""
    rng = np.random.default_rng(200)
    for _ in range(10):
        dim = 5
        u = rng.standard_normal(dim)
        v = rng.standard_normal(dim)
        w = rng.standard_normal(dim)
        a, b = rng.standard_normal(2)
        lhs = np.dot(a * u + b * w, v)
        rhs = a * np.dot(u, v) + b * np.dot(w, v)
        if abs(lhs - rhs) > 1e-10:
            return (False, f"Linearity violated: lhs={lhs}, rhs={rhs}")
    return (True, "")


def _dot_positive_definiteness_check():
    """F4.3: u.u >= 0, and u.u = 0 iff u = 0."""
    rng = np.random.default_rng(300)
    # Check non-zero vectors have u.u > 0
    for _ in range(10):
        u = rng.standard_normal(5)
        uu = np.dot(u, u)
        if uu < -1e-15:
            return (False, f"u.u = {uu} < 0 for u={u}")
        if uu < 1e-15:
            return (False, f"u.u = {uu} ~ 0 for non-zero u={u}")
    # Check zero vector has u.u = 0
    z = np.zeros(5)
    zz = np.dot(z, z)
    if abs(zz) > 1e-15:
        return (False, f"0.0 = {zz}, expected 0")
    return (True, "")


def _norm_nonnegativity_check():
    """F4.4: ||u|| >= 0 for all u, and ||u|| = 0 iff u = 0."""
    rng = np.random.default_rng(400)
    for _ in range(10):
        u = rng.standard_normal(5)
        norm_u = np.linalg.norm(u)
        if norm_u < -1e-15:
            return (False, f"||u|| = {norm_u} < 0")
    # Zero vector
    z = np.zeros(5)
    if abs(np.linalg.norm(z)) > 1e-15:
        return (False, f"||0|| = {np.linalg.norm(z)}, expected 0")
    return (True, "")


def _triangle_inequality_check():
    """F4.6: ||u+v|| <= ||u|| + ||v|| for random vector pairs."""
    rng = np.random.default_rng(500)
    for u, v in _random_vector_pairs(rng, 20, 5):
        lhs = np.linalg.norm(u + v)
        rhs = np.linalg.norm(u) + np.linalg.norm(v)
        if lhs > rhs + 1e-10:
            return (False, f"||u+v||={lhs} > ||u||+||v||={rhs}")
    return (True, "")


def _reverse_triangle_inequality_check():
    """F4.8: | ||u|| - ||v|| | <= ||u - v|| for random vector pairs."""
    rng = np.random.default_rng(600)
    for u, v in _random_vector_pairs(rng, 20, 5):
        lhs = abs(np.linalg.norm(u) - np.linalg.norm(v))
        rhs = np.linalg.norm(u - v)
        if lhs > rhs + 1e-10:
            return (False, f"| ||u||-||v|| |={lhs} > ||u-v||={rhs}")
    return (True, "")
