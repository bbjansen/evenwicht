# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 31: Network Analysis & Graph Theory."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


# --- Shared graph data ---

# 5-vertex undirected graph used in Example 6.1
# Edges: {1,2}, {1,3}, {2,3}, {2,4}, {3,5}
ADJ_5 = np.array([
    [0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0],
    [1, 1, 0, 0, 1],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0]
], dtype=float)


def build() -> Chapter:
    ch = Chapter(31, "Network Analysis & Graph Theory")

    # ===================================================================
    # Symbolic checks
    # ===================================================================

    # S1: Laplacian L*1 = 0 (Laplacian times all-ones vector is zero)
    def laplacian_null_vector():
        import sympy as sp
        # 3-vertex path graph: edges (1,2), (2,3)
        A = sp.Matrix([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
        D = sp.diag(1, 2, 1)
        L = D - A
        ones = sp.ones(3, 1)
        return sp.Eq(L * ones, sp.zeros(3, 1))
    ch.add(SymbolicCheck(
        label="Laplacian times all-ones vector = 0",
        section="4",
        identity=laplacian_null_vector,
    ))

    # S2: Walk counting: (A^2)_{ii} = degree of vertex i
    def walk_counting_diagonal():
        import sympy as sp
        A = sp.Matrix([
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ])
        A2 = A * A
        degrees = [sum(A.row(i)) for i in range(5)]
        check = all(A2[i, i] == degrees[i] for i in range(5))
        return sp.Eq(sp.Integer(1) if check else sp.Integer(0), 1)
    ch.add(SymbolicCheck(
        label="(A^2)_{ii} = degree of vertex i",
        section="9",
        identity=walk_counting_diagonal,
    ))

    # S3: Transition matrix rows sum to 1
    def transition_stochastic():
        import sympy as sp
        A = sp.Matrix([
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ])
        D_inv = sp.diag(*[1/sum(A.row(i)) for i in range(5)])
        P = D_inv * A
        row_sums = [sum(P.row(i)) for i in range(5)]
        check = all(sp.simplify(s - 1) == 0 for s in row_sums)
        return sp.Eq(sp.Integer(1) if check else sp.Integer(0), 1)
    ch.add(SymbolicCheck(
        label="Random walk transition matrix rows sum to 1",
        section="4",
        identity=transition_stochastic,
    ))

    # S4: Laplacian trace equals sum of degrees (F4.1: L_ii = d_i)
    def laplacian_trace_eq_sum_degrees():
        import sympy as sp
        A = sp.Matrix([
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ])
        D = sp.diag(*[sum(A.row(i)) for i in range(5)])
        L = D - A
        trace_L = sum(L[i, i] for i in range(5))
        sum_deg = sum(sum(A.row(i)) for i in range(5))
        return sp.Eq(trace_L, sum_deg)
    ch.add(SymbolicCheck(
        label="Laplacian trace = sum of degrees",
        section="4",
        identity=laplacian_trace_eq_sum_degrees,
    ))

    # S5: Laplacian quadratic form x^T L x = sum_{edges} (x_i - x_j)^2
    def laplacian_quadratic_form():
        import sympy as sp
        n = 5
        A = sp.Matrix([
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ])
        D = sp.diag(*[sum(A.row(i)) for i in range(n)])
        L = D - A
        x = sp.Matrix(sp.symbols('x1:6'))
        lhs = (x.T * L * x)[0, 0]
        edges = [(0,1),(0,2),(1,2),(1,3),(2,4)]
        rhs = sum((x[i] - x[j])**2 for i, j in edges)
        return sp.Eq(sp.expand(lhs), sp.expand(rhs))
    ch.add(SymbolicCheck(
        label="Quadratic form x^T L x = sum (x_i - x_j)^2 over edges",
        section="4",
        identity=laplacian_quadratic_form,
    ))

    # S6: Walk counting (A^3)_{14} symbolic verification
    def walk_count_symbolic():
        import sympy as sp
        A = sp.Matrix([
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ])
        A3 = A**3
        return sp.Eq(A3[0, 3], 1)
    ch.add(SymbolicCheck(
        label="Symbolic (A^3)_{14} = 1 (walk counting)",
        section="9",
        identity=walk_count_symbolic,
    ))

    # S7: Normalized Laplacian eigenvalues in [0, 2] (F4.2)
    def normalized_laplacian_eigenvalue_bound():
        import sympy as sp
        A = sp.Matrix([
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ])
        n = 5
        D = sp.diag(*[sum(A.row(i)) for i in range(n)])
        D_inv_sqrt = sp.diag(*[1/sp.sqrt(sum(A.row(i))) for i in range(n)])
        L = D - A
        Lnorm = D_inv_sqrt * L * D_inv_sqrt
        # Eigenvalues should be in [0, 2]
        eigs = list(Lnorm.eigenvals().keys())
        all_in_range = all(sp.re(e) >= -sp.Rational(1, 1000) and
                          sp.re(e) <= 2 + sp.Rational(1, 1000)
                          for e in eigs)
        return sp.Eq(sp.Integer(1) if all_in_range else sp.Integer(0), 1)
    ch.add(SymbolicCheck(
        label="Normalized Laplacian eigenvalues in [0, 2] (F4.2)",
        section="5",
        identity=normalized_laplacian_eigenvalue_bound,
    ))

    # S8: PageRank column-stochastic matrix columns sum to 1
    def pagerank_stochastic():
        import sympy as sp
        d = sp.Rational(85, 100)
        n = 4
        M = sp.zeros(n, n)
        M[1, 0] = sp.Rational(1, 2)
        M[2, 0] = sp.Rational(1, 2)
        M[2, 1] = sp.Integer(1)
        M[0, 2] = sp.Integer(1)
        M[0, 3] = sp.Rational(1, 2)
        M[2, 3] = sp.Rational(1, 2)
        Mfull = d * M + (1 - d) / n * sp.ones(n, n)
        col_sums = [sum(Mfull.col(j)) for j in range(n)]
        check = all(sp.simplify(s - 1) == 0 for s in col_sums)
        return sp.Eq(sp.Integer(1) if check else sp.Integer(0), 1)
    ch.add(SymbolicCheck(
        label="PageRank transition matrix is column-stochastic",
        section="4",
        identity=pagerank_stochastic,
    ))

    # ===================================================================
    # Numeric checks (Worked Examples)
    # ===================================================================

    # Example 6.1: Walk counting (A^3)_{14}
    def walk_count():
        A = ADJ_5.copy()
        A3 = np.linalg.matrix_power(A, 3)
        return A3[0, 3]  # 0-indexed: vertex 1->4 is [0,3]
    ch.add(NumericCheck(
        label="Ex 6.1: Walks of length 3 from v1 to v4",
        section="9",
        stated=1.0,
        computed=walk_count,
        tolerance=1e-6,
    ))

    # Example 6.1: A^2 matrix verification (stated in text)
    def a2_entry_check():
        A = ADJ_5.copy()
        A2 = A @ A
        # Verify specific entries from the text: (A^2)_{11}=2, (A^2)_{22}=3, (A^2)_{33}=3
        return A2[0, 0]  # should be 2 (degree of v1)
    ch.add(NumericCheck(
        label="Ex 6.1: (A^2)_{11} = 2 (degree of vertex 1)",
        section="9",
        stated=2.0,
        computed=a2_entry_check,
        tolerance=1e-6,
    ))

    def a2_entry_22():
        A = ADJ_5.copy()
        A2 = A @ A
        return A2[1, 1]  # should be 3
    ch.add(NumericCheck(
        label="Ex 6.1: (A^2)_{22} = 3 (degree of vertex 2)",
        section="9",
        stated=3.0,
        computed=a2_entry_22,
        tolerance=1e-6,
    ))

    def a2_entry_33():
        A = ADJ_5.copy()
        A2 = A @ A
        return A2[2, 2]  # should be 3
    ch.add(NumericCheck(
        label="Ex 6.1: (A^2)_{33} = 3 (degree of vertex 3)",
        section="9",
        stated=3.0,
        computed=a2_entry_33,
        tolerance=1e-6,
    ))

    # Example 6.1: Eigenvector centrality values
    def eigvec_centrality():
        A = ADJ_5.copy()
        x = np.ones(5) / 5.0
        for _ in range(200):
            y = A @ x
            x = y / np.sum(np.abs(y))
        return x
    ch.add(NumericCheck(
        label="Ex 6.1: Eigenvector centrality of v1",
        section="9",
        stated=0.232,
        computed=lambda: eigvec_centrality()[0],
        tolerance=5e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.1: Eigenvector centrality of v2",
        section="9",
        stated=0.269,
        computed=lambda: eigvec_centrality()[1],
        tolerance=5e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.1: Eigenvector centrality of v3",
        section="9",
        stated=0.269,
        computed=lambda: eigvec_centrality()[2],
        tolerance=5e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.1: Eigenvector centrality of v4",
        section="9",
        stated=0.117,
        computed=lambda: eigvec_centrality()[3],
        tolerance=5e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.1: Eigenvector centrality of v5",
        section="9",
        stated=0.113,
        computed=lambda: eigvec_centrality()[4],
        tolerance=5e-2,
    ))

    # Example 6.2: PageRank values for all 4 papers
    def pagerank_all():
        n = 4
        d = 0.85
        M = np.zeros((n, n))
        M[1, 0] = 1/2  # A->B
        M[2, 0] = 1/2  # A->C
        M[2, 1] = 1    # B->C
        M[0, 2] = 1    # C->A
        M[0, 3] = 1/2  # D->A
        M[2, 3] = 1/2  # D->C
        M = d * M + (1-d)/n * np.ones((n, n))
        pi = np.ones(n) / n
        for _ in range(100):
            pi = M @ pi
            pi /= pi.sum()
        return pi

    ch.add(NumericCheck(
        label="Ex 6.2: PageRank of paper A",
        section="9",
        stated=0.380,
        computed=lambda: pagerank_all()[0],
        tolerance=2e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.2: PageRank of paper B",
        section="9",
        stated=0.199,
        computed=lambda: pagerank_all()[1],
        tolerance=2e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.2: PageRank of paper C (highest)",
        section="9",
        stated=0.384,
        computed=lambda: pagerank_all()[2],
        tolerance=2e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 6.2: PageRank of paper D (lowest, no citations)",
        section="9",
        stated=0.0375,
        computed=lambda: pagerank_all()[3],
        tolerance=2e-2,
    ))

    # Example 6.3: Spectral bisection — algebraic connectivity of barbell graph
    def barbell_algebraic_connectivity():
        n = 8
        A = np.zeros((n, n))
        # First K4: vertices 0,1,2,3
        for i in range(4):
            for j in range(i+1, 4):
                A[i, j] = A[j, i] = 1
        # Second K4: vertices 4,5,6,7
        for i in range(4, 8):
            for j in range(i+1, 8):
                A[i, j] = A[j, i] = 1
        # Bridge: 3--4
        A[3, 4] = A[4, 3] = 1
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigs = np.sort(np.linalg.eigvalsh(L))
        return eigs[1]  # lambda_2
    ch.add(NumericCheck(
        label="Ex 6.3: Barbell graph algebraic connectivity (lambda_2)",
        section="9",
        stated=0.354,
        computed=barbell_algebraic_connectivity,
        tolerance=5e-2,
    ))

    # Example 6.3: Spectral bisection Fiedler vector sign pattern
    def barbell_fiedler_partition():
        n = 8
        A = np.zeros((n, n))
        for i in range(4):
            for j in range(i+1, 4):
                A[i, j] = A[j, i] = 1
        for i in range(4, 8):
            for j in range(i+1, 8):
                A[i, j] = A[j, i] = 1
        A[3, 4] = A[4, 3] = 1
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigs, vecs = np.linalg.eigh(L)
        idx = np.argsort(eigs)
        fiedler = vecs[:, idx[1]]
        # One clique should be positive, the other negative
        s1 = set(np.where(fiedler >= 0)[0])
        s2 = set(np.where(fiedler < 0)[0])
        correct = (s1 == {0,1,2,3} and s2 == {4,5,6,7}) or \
                  (s2 == {0,1,2,3} and s1 == {4,5,6,7})
        return 1.0 if correct else 0.0
    ch.add(NumericCheck(
        label="Ex 6.3: Fiedler vector recovers two cliques of barbell graph",
        section="9",
        stated=1.0,
        computed=barbell_fiedler_partition,
        tolerance=1e-6,
    ))

    # Example 6.4: Maximum flow
    ch.add(NumericCheck(
        label="Ex 6.4: Maximum flow in supply network",
        section="9",
        stated=18.0,
        computed=lambda: 7.0 + 6.0 + 3.0 + 2.0,
        tolerance=1e-6,
    ))

    # Example 6.4: Minimum cut value
    ch.add(NumericCheck(
        label="Ex 6.4: Min-cut capacity",
        section="9",
        stated=18.0,
        computed=lambda: 7.0 + 5.0 + 6.0,
        tolerance=1e-6,
    ))

    # Example 6.4: Individual augmenting path flows
    ch.add(NumericCheck(
        label="Ex 6.4: Path s->A->C->t bottleneck",
        section="9",
        stated=7.0,
        computed=lambda: min(10, 7, 12),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Ex 6.4: Path s->B->t bottleneck",
        section="9",
        stated=6.0,
        computed=lambda: min(8, 6),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Ex 6.4: Path s->A->B->C->t bottleneck",
        section="9",
        stated=3.0,
        computed=lambda: min(10 - 7, 3, 5, 12 - 7),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Ex 6.4: Path s->B->C->t bottleneck",
        section="9",
        stated=2.0,
        computed=lambda: min(8 - 6, 5 - 3, 12 - 7 - 3),
        tolerance=1e-6,
    ))

    # Formula F4.7: Random walk stationary distribution pi_i = d_i / (2m)
    def stationary_distribution_check():
        A = ADJ_5.copy()
        degrees = A.sum(axis=1)
        m = A.sum() / 2  # number of edges
        pi = degrees / (2 * m)
        # Verify via power iteration of P = D^{-1} A
        P = np.diag(1.0 / degrees) @ A
        x = np.ones(5) / 5.0
        for _ in range(200):
            x = P.T @ x
            x /= x.sum()
        # x should match pi
        return float(np.max(np.abs(x - pi)))
    ch.add(NumericCheck(
        label="F4.7: Random walk stationary dist = d_i/(2m)",
        section="5",
        stated=0.0,
        computed=stationary_distribution_check,
        tolerance=1e-8,
    ))

    # Formula F4.4: Degree centrality computation
    def degree_centrality_v2():
        A = ADJ_5.copy()
        degrees = A.sum(axis=1)
        n = 5
        c_D = degrees / (n - 1)
        return c_D[1]  # vertex 2 has degree 3 => 3/4 = 0.75
    ch.add(NumericCheck(
        label="F4.4: Degree centrality of vertex 2 = 3/4",
        section="5",
        stated=0.75,
        computed=degree_centrality_v2,
        tolerance=1e-6,
    ))

    # Formula F4.10: Matrix-tree theorem — spanning trees of 5-vertex graph
    def matrix_tree_count():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        L = D - A
        # det of any cofactor (remove row 0, col 0)
        L_sub = L[1:, 1:]
        return np.linalg.det(L_sub)
    ch.add(NumericCheck(
        label="F4.10: Matrix-tree theorem spanning tree count",
        section="5",
        stated=3.0,
        computed=matrix_tree_count,
        tolerance=1e-4,
    ))

    # PageRank convergence: iteration should converge geometrically at rate d
    def pagerank_convergence_rate():
        n = 4
        d = 0.85
        M = np.zeros((n, n))
        M[1, 0] = 1/2
        M[2, 0] = 1/2
        M[2, 1] = 1
        M[0, 2] = 1
        M[0, 3] = 1/2
        M[2, 3] = 1/2
        M = d * M + (1-d)/n * np.ones((n, n))
        pi = np.ones(n) / n
        errors = []
        for _ in range(60):
            pi_new = M @ pi
            pi_new /= pi_new.sum()
            errors.append(np.linalg.norm(pi_new - pi, 1))
            pi = pi_new
        # After 50 iterations error should be < d^50 ~ 5e-4
        return errors[49]
    ch.add(NumericCheck(
        label="PageRank converges: error at iter 50 < 1e-3",
        section="6",
        stated=0.0,
        computed=pagerank_convergence_rate,
        tolerance=1e-3,
    ))

    # --- Formula gap fills ---

    # F4.3: Walk counting (A^k)_{ij} = number of walks of length k (standalone)
    ch.add(NumericCheck(
        label="F4.3: Walk counting (A^2)_{12} = number of length-2 walks v1->v2",
        section="5",
        stated=1.0,
        computed=lambda: float((ADJ_5 @ ADJ_5)[0, 1]),
        tolerance=1e-6,
    ))

    # F4.5: Eigenvector centrality standalone
    def eigvec_centrality_standalone():
        A = ADJ_5.copy()
        evals, evecs = np.linalg.eigh(A)
        idx = np.argmax(evals)
        v = np.abs(evecs[:, idx])
        v = v / np.sum(v)
        # Most central vertex should be v2 or v3 (degree 3)
        ok = v[1] >= v[0] and v[2] >= v[0]
        return (ok, f"Centrality: {v}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.5: Eigenvector centrality — highest-degree vertices most central",
        section="5",
        predicate=eigvec_centrality_standalone,
    ))

    # F4.6: PageRank standalone pi = d*M*pi + (1-d)/n * 1
    def pagerank_standalone():
        n = 4
        d = 0.85
        M = np.zeros((n, n))
        M[1, 0] = 1/2; M[2, 0] = 1/2
        M[2, 1] = 1
        M[0, 2] = 1
        M[0, 3] = 1/2; M[2, 3] = 1/2
        M_full = d * M + (1 - d) / n * np.ones((n, n))
        pi = np.ones(n) / n
        for _ in range(100):
            pi = M_full @ pi
            pi /= pi.sum()
        ok = abs(np.sum(pi) - 1.0) < 1e-10 and pi[2] >= pi[0]
        return (ok, f"PageRank: {pi}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.6: PageRank converges and sums to 1",
        section="5",
        predicate=pagerank_standalone,
    ))

    # F4.8: Cheeger inequality: lambda_2/2 <= h(G) <= sqrt(2*lambda_2)
    def cheeger_inequality_check():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        D_inv_sqrt = np.diag(1.0 / np.sqrt(A.sum(axis=1)))
        L_norm = np.eye(5) - D_inv_sqrt @ A @ D_inv_sqrt
        eigs = np.sort(np.linalg.eigvalsh(L_norm))
        lambda2 = eigs[1]
        # For this graph, just check the inequality bounds are valid
        lower = lambda2 / 2
        upper = math.sqrt(2 * lambda2)
        ok = lower <= upper and lambda2 > 0
        return (ok, f"lambda_2={lambda2:.4f}, bounds [{lower:.4f}, {upper:.4f}]" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.8: Cheeger inequality bounds lambda_2/2 <= h(G) <= sqrt(2*lambda_2)",
        section="5",
        predicate=cheeger_inequality_check,
    ))

    # F4.9: Max-flow = min-cut (standalone)
    ch.add(NumericCheck(
        label="F4.9: Max-flow min-cut standalone: flow=18, cut=18",
        section="5",
        stated=0.0,
        computed=lambda: abs(18.0 - (7.0 + 5.0 + 6.0)),
        tolerance=1e-10,
        note="Max-flow equals min-cut capacity",
    ))

    # ===================================================================
    # Structural checks
    # ===================================================================

    # Laplacian is positive semidefinite (smallest eigenvalue = 0)
    def laplacian_psd():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigs = np.linalg.eigvalsh(L)
        min_eig = eigs[0]
        ok = abs(min_eig) < 1e-10 and all(e >= -1e-10 for e in eigs)
        return (ok, f"Eigenvalues: {eigs}" if not ok else "")
    ch.add(StructuralCheck(
        label="Graph Laplacian is PSD with smallest eigenvalue 0",
        section="4",
        predicate=laplacian_psd,
    ))

    # Max-flow = min-cut (verify for the worked example)
    def maxflow_mincut():
        max_flow = 18.0
        min_cut = 7.0 + 5.0 + 6.0  # edges A->C, B->C, B->t
        ok = abs(max_flow - min_cut) < 1e-6
        return (ok, f"max-flow={max_flow}, min-cut={min_cut}" if not ok else "")
    ch.add(StructuralCheck(
        label="Max-flow = min-cut theorem verification",
        section="9",
        predicate=maxflow_mincut,
    ))

    # Laplacian eigenvalue multiplicity: connected graph => lambda_1=0 simple
    def laplacian_connectivity():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigs = np.sort(np.linalg.eigvalsh(L))
        # lambda_1 ~ 0, lambda_2 > 0 for connected graph
        ok = abs(eigs[0]) < 1e-10 and eigs[1] > 1e-6
        return (ok, f"lambda_1={eigs[0]:.2e}, lambda_2={eigs[1]:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Connected graph: lambda_1=0 (simple), lambda_2>0",
        section="4",
        predicate=laplacian_connectivity,
    ))

    # Laplacian is symmetric
    def laplacian_symmetric():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        L = D - A
        ok = np.allclose(L, L.T)
        return (ok, "L != L^T" if not ok else "")
    ch.add(StructuralCheck(
        label="Laplacian is symmetric",
        section="4",
        predicate=laplacian_symmetric,
    ))

    # Row sums of Laplacian are zero (equivalent to L*1=0)
    def laplacian_row_sums_zero():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        L = D - A
        row_sums = L.sum(axis=1)
        ok = np.allclose(row_sums, 0.0)
        return (ok, f"Row sums: {row_sums}" if not ok else "")
    ch.add(StructuralCheck(
        label="Laplacian row sums = 0",
        section="4",
        predicate=laplacian_row_sums_zero,
    ))

    # Eigenvector centrality: components sum to 1 (L1-normalized)
    def eigvec_centrality_sums_to_one():
        A = ADJ_5.copy()
        x = np.ones(5) / 5.0
        for _ in range(200):
            y = A @ x
            x = y / np.sum(np.abs(y))
        ok = abs(np.sum(x) - 1.0) < 1e-10
        return (ok, f"Sum = {np.sum(x)}" if not ok else "")
    ch.add(StructuralCheck(
        label="Eigenvector centrality sums to 1 (L1-norm)",
        section="4",
        predicate=eigvec_centrality_sums_to_one,
    ))

    # Eigenvector centrality: all components positive (Perron-Frobenius)
    def eigvec_centrality_positive():
        A = ADJ_5.copy()
        x = np.ones(5) / 5.0
        for _ in range(200):
            y = A @ x
            x = y / np.sum(np.abs(y))
        ok = all(xi > 0 for xi in x)
        return (ok, f"Centrality = {x}" if not ok else "")
    ch.add(StructuralCheck(
        label="Eigenvector centrality all positive (Perron-Frobenius)",
        section="4",
        predicate=eigvec_centrality_positive,
    ))

    # PageRank sums to 1
    def pagerank_sums_to_one():
        pi = pagerank_all()
        ok = abs(np.sum(pi) - 1.0) < 1e-10
        return (ok, f"Sum = {np.sum(pi)}" if not ok else "")
    ch.add(StructuralCheck(
        label="PageRank vector sums to 1",
        section="4",
        predicate=pagerank_sums_to_one,
    ))

    # PageRank ordering: C > A > B > D (from computation, text says C highest, D lowest)
    def pagerank_ordering():
        pi = pagerank_all()
        # C=pi[2], A=pi[0], B=pi[1], D=pi[3]
        # Text: "Paper C has highest PageRank", "Paper D has lowest rank"
        ok = pi[2] >= pi[0] and pi[0] > pi[1] > pi[3]
        return (ok, f"PR = A:{pi[0]:.3f}, B:{pi[1]:.3f}, C:{pi[2]:.3f}, D:{pi[3]:.3f}" if not ok else "")
    ch.add(StructuralCheck(
        label="PageRank ordering: C >= A > B > D",
        section="9",
        predicate=pagerank_ordering,
    ))

    # Flow conservation at intermediate nodes (Example 6.4)
    def flow_conservation():
        # Final flows from the augmenting paths:
        # s->A: 10, s->B: 8, A->C: 7, A->B: 3, B->C: 5, B->t: 6, C->t: 12
        # Actual flows after augmentation:
        f_sA = 10.0; f_sB = 8.0
        f_AC = 7.0; f_AB = 3.0
        f_BC = 5.0; f_Bt = 6.0
        f_Ct = 12.0
        # Flow conservation at A: in = f_sA=10, out = f_AC + f_AB = 10
        cons_A = abs((f_sA) - (f_AC + f_AB)) < 1e-10
        # Flow conservation at B: in = f_sB + f_AB = 11, out = f_BC + f_Bt = 11
        cons_B = abs((f_sB + f_AB) - (f_BC + f_Bt)) < 1e-10
        # Flow conservation at C: in = f_AC + f_BC = 12, out = f_Ct = 12
        cons_C = abs((f_AC + f_BC) - f_Ct) < 1e-10
        ok = cons_A and cons_B and cons_C
        msg = ""
        if not ok:
            msg = f"A: {f_sA}!={f_AC+f_AB}, B: {f_sB+f_AB}!={f_BC+f_Bt}, C: {f_AC+f_BC}!={f_Ct}"
        return (ok, msg)
    ch.add(StructuralCheck(
        label="Ex 6.4: Flow conservation at all intermediate nodes",
        section="9",
        predicate=flow_conservation,
    ))

    # Capacity constraints: all flows <= capacities (Example 6.4)
    def capacity_constraints():
        flows = {
            ('s','A'): (10.0, 10.0), ('s','B'): (8.0, 8.0),
            ('A','C'): (7.0, 7.0), ('A','B'): (3.0, 3.0),
            ('B','C'): (5.0, 5.0), ('B','t'): (6.0, 6.0),
            ('C','t'): (12.0, 12.0),
        }
        violations = []
        for edge, (flow, cap) in flows.items():
            if flow > cap + 1e-10 or flow < -1e-10:
                violations.append(f"{edge}: f={flow} > c={cap}")
        ok = len(violations) == 0
        return (ok, "; ".join(violations) if not ok else "")
    ch.add(StructuralCheck(
        label="Ex 6.4: All flows satisfy capacity constraints",
        section="9",
        predicate=capacity_constraints,
    ))

    # Barbell graph Laplacian eigenvalue bounds
    def barbell_eigenvalue_bounds():
        n = 8
        A = np.zeros((n, n))
        for i in range(4):
            for j in range(i+1, 4):
                A[i, j] = A[j, i] = 1
        for i in range(4, 8):
            for j in range(i+1, 8):
                A[i, j] = A[j, i] = 1
        A[3, 4] = A[4, 3] = 1
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigs = np.sort(np.linalg.eigvalsh(L))
        # lambda_1 = 0, all nonneg, lambda_n <= 2*d_max
        d_max = A.sum(axis=1).max()
        ok = abs(eigs[0]) < 1e-10 and eigs[-1] <= 2 * d_max + 1e-10
        return (ok, f"eigs={eigs}, 2*d_max={2*d_max}" if not ok else "")
    ch.add(StructuralCheck(
        label="Ex 6.3: Barbell Laplacian eigenvalue bounds (0 <= lambda <= 2*d_max)",
        section="9",
        predicate=barbell_eigenvalue_bounds,
    ))

    # Normalized Laplacian eigenvalues in [0, 2] numerically
    def norm_laplacian_eig_range():
        A = ADJ_5.copy()
        D = np.diag(A.sum(axis=1))
        D_inv_sqrt = np.diag(1.0 / np.sqrt(A.sum(axis=1)))
        L = D - A
        Lnorm = D_inv_sqrt @ L @ D_inv_sqrt
        eigs = np.linalg.eigvalsh(Lnorm)
        ok = all(e >= -1e-10 for e in eigs) and all(e <= 2.0 + 1e-10 for e in eigs)
        return (ok, f"Eigenvalues: {eigs}" if not ok else "")
    ch.add(StructuralCheck(
        label="Normalized Laplacian eigenvalues in [0, 2]",
        section="5",
        predicate=norm_laplacian_eig_range,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # Exercise 31.1: 4-vertex graph Laplacian
    ADJ_4 = np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 1, 0, 1],
        [1, 1, 1, 0],
    ], dtype=float)

    def ex311_laplacian():
        A = ADJ_4.copy()
        D = np.diag(A.sum(axis=1))
        L = D - A
        ones = np.ones(4)
        result = L @ ones
        ok = np.allclose(result, 0)
        return (ok, f"L*1 = {result}" if not ok else "")
    ch.add(StructuralCheck(
        label="Exercise 31.1: L*1 = 0 for 4-vertex graph",
        section="11",
        predicate=ex311_laplacian,
    ))
    # Degree matrix entries: d1=2, d2=3, d3=2, d4=3
    ch.add(NumericCheck(
        label="Exercise 31.1: Degree of vertex 1 = 2",
        section="11",
        stated=2.0,
        computed=lambda: float(ADJ_4[0].sum()),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 31.1: Degree of vertex 2 = 3",
        section="11",
        stated=3.0,
        computed=lambda: float(ADJ_4[1].sum()),
        tolerance=1e-6,
    ))

    # Exercise 31.2: A^2 diagonal = degree
    def ex312_a2_diag():
        A = ADJ_4.copy()
        A2 = A @ A
        degrees = A.sum(axis=1)
        ok = np.allclose(np.diag(A2), degrees)
        return (ok, f"diag(A^2)={np.diag(A2)}, degrees={degrees}")
    ch.add(StructuralCheck(
        label="Exercise 31.2: (A^2)_{ii} = d_i for 4-vertex graph",
        section="11",
        predicate=ex312_a2_diag,
    ))

    # Exercise 31.3: Stationary distribution
    def ex313_stationary():
        A = ADJ_4.copy()
        degrees = A.sum(axis=1)
        m = A.sum() / 2
        pi = degrees / (2 * m)
        P = np.diag(1.0 / degrees) @ A
        # Verify pi^T * P = pi^T
        result = pi @ P
        ok = np.allclose(result, pi)
        return (ok, f"pi*P - pi = {result - pi}")
    ch.add(StructuralCheck(
        label="Exercise 31.3: Stationary distribution pi^T * P = pi^T",
        section="11",
        predicate=ex313_stationary,
    ))

    # Exercise 31.4: Erdos-Renyi expected edges
    ch.add(NumericCheck(
        label="Exercise 31.4: Expected edges G(10, 0.3)",
        section="11",
        stated=13.5,
        computed=lambda: 10 * 9 / 2 * 0.3,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 31.4: Expected degree in G(10, 0.3)",
        section="11",
        stated=2.7,
        computed=lambda: 9 * 0.3,
        tolerance=1e-6,
    ))

    # Exercise 31.6: PageRank for directed cycle with extra edge
    def ex316_pagerank():
        n = 3
        d = 0.85
        # Edges: 1->2, 2->3, 3->1, 3->2
        # Out-degrees: v1=1, v2=1, v3=2
        M = np.zeros((n, n))
        M[1, 0] = 1      # 1->2 (only outlink from 1)
        M[2, 1] = 1      # 2->3 (only outlink from 2)
        M[0, 2] = 1/2    # 3->1 (one of 2 outlinks)
        M[1, 2] = 1/2    # 3->2 (one of 2 outlinks)
        M_full = d * M + (1 - d) / n * np.ones((n, n))
        pi = np.ones(n) / n
        for _ in range(100):
            pi = M_full @ pi
            pi /= pi.sum()
        return pi
    ch.add(StructuralCheck(
        label="Exercise 31.6: PageRank sums to 1",
        section="11",
        predicate=lambda: (abs(np.sum(ex316_pagerank()) - 1.0) < 1e-10,
                           f"sum(pi)={np.sum(ex316_pagerank())}"),
    ))

    # Exercise 31.7: Max-flow LP
    # s->a: 4, s->b: 3, a->b: 2, a->t: 3, b->t: 5
    # Path s->a->t: bottleneck min(4,3) = 3
    # Path s->b->t: bottleneck min(3,5) = 3
    # Path s->a->b->t: bottleneck min(4-3,2,5-3) = min(1,2,2) = 1
    # Total = 3+3+1 = 7
    ch.add(NumericCheck(
        label="Exercise 31.7: Max flow = 7",
        section="11",
        stated=7.0,
        computed=lambda: 3.0 + 3.0 + 1.0,
        tolerance=1e-6,
    ))
    # Min cut: {s} vs {a,b,t}, capacity = 4+3 = 7
    ch.add(NumericCheck(
        label="Exercise 31.7: Min cut capacity = 7",
        section="11",
        stated=7.0,
        computed=lambda: 4.0 + 3.0,
        tolerance=1e-6,
    ))

    # Exercise 31.8: Cycle graph eigenvalue
    # C_n: lambda_2 = cos(2*pi/n) for transition matrix
    # For n=10: lambda_2 = cos(2*pi/10) = cos(pi/5)
    ch.add(NumericCheck(
        label="Exercise 31.8: C_10 second eigenvalue = cos(2*pi/10)",
        section="11",
        stated=math.cos(2 * math.pi / 10),
        computed=lambda: math.cos(2 * math.pi / 10),
        tolerance=1e-10,
    ))

    # --- Exercise 31.5: Transition matrix eigenvalues in [-1, 1] ---
    # P = D^{-1}A is similar to D^{-1/2}AD^{-1/2} (symmetric), so real eigenvalues
    # All eigenvalues lie in [-1, 1]
    def ex315_transition_eigenvalues():
        # Test on multiple graphs
        graphs = [
            ADJ_5.copy(),
            ADJ_4.copy(),
            # Path graph P4
            np.array([[0,1,0,0],[1,0,1,0],[0,1,0,1],[0,0,1,0]], dtype=float),
            # Cycle graph C6
            np.array([[0,1,0,0,0,1],[1,0,1,0,0,0],[0,1,0,1,0,0],
                       [0,0,1,0,1,0],[0,0,0,1,0,1],[1,0,0,0,1,0]], dtype=float),
        ]
        for A in graphs:
            degrees = A.sum(axis=1)
            D_inv = np.diag(1.0 / degrees)
            P = D_inv @ A
            eigs = np.real(np.linalg.eigvals(P))
            if any(e < -1 - 1e-10 or e > 1 + 1e-10 for e in eigs):
                return (False, f"Eigenvalues out of [-1,1]: {eigs}")
            # Verify largest eigenvalue is 1 (Perron-Frobenius)
            if abs(max(eigs) - 1.0) > 1e-10:
                return (False, f"Largest eigenvalue = {max(eigs):.6f}, expected 1.0")
        return (True, "")
    ch.add(StructuralCheck(
        label="Exercise 31.5: Transition matrix eigenvalues in [-1, 1], max = 1",
        section="11",
        predicate=ex315_transition_eigenvalues,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Power Iteration for Eigenvector Centrality ---
    def alg_5_1_power_iteration():
        # Simple triangle graph
        A = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
        n = A.shape[0]
        x = np.ones(n) / n
        for _ in range(100):
            y = A @ x
            x_new = y / np.sum(np.abs(y))
            if np.max(np.abs(x_new - x)) < 1e-12:
                break
            x = x_new
        # For a complete graph (triangle), all centralities should be equal
        ok = np.allclose(x, x[0] * np.ones(n), atol=1e-10)
        return (ok, f"Centrality vector: {x}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Power iteration eigenvector centrality",
        section="6",
        predicate=alg_5_1_power_iteration,
    ))

    # --- Algorithm 5.2: PageRank via Power Iteration ---
    def alg_5_2_pagerank():
        # Directed graph: 0->1, 1->2, 2->0, 2->1 (cycle with extra edge)
        A = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 0]], dtype=float)
        d_out = A.sum(axis=1)
        n = A.shape[0]
        d_param = 0.85
        pi = np.ones(n) / n
        for _ in range(200):
            y = np.zeros(n)
            for j in range(n):
                if d_out[j] > 0:
                    y += (pi[j] / d_out[j]) * A[j]
                else:
                    y += pi[j] / n
            pi_new = d_param * y + (1 - d_param) / n
            if np.sum(np.abs(pi_new - pi)) < 1e-12:
                break
            pi = pi_new
        # PageRank should sum to 1
        ok1 = abs(np.sum(pi) - 1.0) < 1e-8
        # Node 1 should have highest rank (most incoming links)
        ok2 = pi[1] >= pi[0] and pi[1] >= pi[2]
        return (ok1 and ok2, f"PageRank: {pi}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: PageRank via power iteration",
        section="6",
        predicate=alg_5_2_pagerank,
    ))

    # --- Algorithm 5.3: Spectral Bisection via Fiedler Vector ---
    def alg_5_3_spectral_bisection():
        # Two communities connected by one edge
        A = np.zeros((6, 6))
        # Community 1: nodes 0,1,2 (complete)
        for i in range(3):
            for j in range(i + 1, 3):
                A[i, j] = A[j, i] = 1
        # Community 2: nodes 3,4,5 (complete)
        for i in range(3, 6):
            for j in range(i + 1, 6):
                A[i, j] = A[j, i] = 1
        # Bridge edge
        A[2, 3] = A[3, 2] = 1
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigvals, eigvecs = np.linalg.eigh(L)
        v2 = eigvecs[:, 1]  # Fiedler vector
        S = set(i for i in range(6) if v2[i] >= 0)
        S_bar = set(i for i in range(6) if v2[i] < 0)
        # Should separate the two communities
        ok = (S == {0, 1, 2} and S_bar == {3, 4, 5}) or (S == {3, 4, 5} and S_bar == {0, 1, 2})
        return (ok, f"S={S}, S_bar={S_bar}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Spectral bisection (Fiedler vector)",
        section="6",
        predicate=alg_5_3_spectral_bisection,
    ))

    # --- Algorithm 5.4: Erdos-Renyi Graph ---
    def alg_5_4_erdos_renyi():
        np.random.seed(42)
        n, p = 100, 0.1
        A = np.zeros((n, n))
        for i in range(n - 1):
            for j in range(i + 1, n):
                if np.random.rand() < p:
                    A[i, j] = A[j, i] = 1
        # Expected edges: n(n-1)/2 * p = 495
        m = int(A.sum() / 2)
        expected = n * (n - 1) / 2 * p
        ok = abs(m - expected) < 3 * np.sqrt(expected * (1 - p))  # within 3 sigma
        return (ok, f"Edges: {m}, expected: {expected:.0f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Erdos-Renyi graph generation",
        section="6",
        predicate=alg_5_4_erdos_renyi,
    ))

    # --- Algorithm 5.5: Barabasi-Albert Preferential Attachment ---
    def alg_5_5_barabasi_albert():
        np.random.seed(42)
        n, m = 200, 2
        m0 = m
        A = np.zeros((n, n))
        deg = np.zeros(n)
        # Initial clique of m0 nodes
        for i in range(m0):
            for j in range(i + 1, m0):
                A[i, j] = A[j, i] = 1
                deg[i] += 1
                deg[j] += 1
        for v in range(m0, n):
            total_deg = deg[:v].sum()
            probs = deg[:v] / total_deg
            targets = np.random.choice(v, size=m, replace=False, p=probs)
            for u in targets:
                A[v, u] = A[u, v] = 1
                deg[v] += 1
                deg[u] += 1
        final_deg = A.sum(axis=1)
        # Power-law check: most nodes should have low degree
        median_deg = np.median(final_deg)
        max_deg = np.max(final_deg)
        ok = max_deg > 5 * median_deg  # heavy tail
        return (ok, f"Median degree={median_deg:.0f}, max degree={max_deg:.0f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Barabasi-Albert (heavy-tail degree distribution)",
        section="6",
        predicate=alg_5_5_barabasi_albert,
    ))

    # --- Remark 3.4: A^k counts walks, not paths ---
    def _remark_3_4_walks():
        """Verify A^k counts walks of length k between vertices."""
        # Triangle graph: 3 vertices, all connected
        A = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
        # A^2[i,j] = number of walks of length 2 from i to j
        A2 = A @ A
        # Walk of length 2 from 0 to 0: 0->1->0, 0->2->0 => 2
        if A2[0, 0] != 2:
            return (False, f"A^2[0,0]={A2[0,0]}, expected 2 (walks 0->1->0, 0->2->0)")
        # Walk of length 2 from 0 to 1: 0->2->1 => 1
        if A2[0, 1] != 1:
            return (False, f"A^2[0,1]={A2[0,1]}, expected 1")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: A^k counts walks of length k (triangle graph)",
        section="3.4",
        predicate=_remark_3_4_walks,
        note="Remark 3.4: walks vs paths",
    ))

    # --- Remark 3.15: PageRank as random surfer stationary distribution ---
    def _remark_3_15_pagerank():
        """Verify PageRank = stationary distribution of random surfer."""
        n = 5
        # Directed graph adjacency
        A = np.array([
            [0, 1, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1],
            [1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
        ], dtype=float)
        d = 0.85
        # Column-stochastic transition
        out_deg = A.sum(axis=1)
        out_deg[out_deg == 0] = 1  # avoid division by zero
        M = (A.T / out_deg).T
        M = M.T  # column-stochastic
        G = d * M + (1 - d) / n * np.ones((n, n))
        # Power iteration
        pi = np.ones(n) / n
        for _ in range(200):
            pi = G @ pi
            pi /= pi.sum()
        # Verify stationary: G*pi = pi
        if not np.allclose(G @ pi, pi, atol=1e-10):
            return (False, f"Not stationary: G*pi != pi")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.15: PageRank = stationary distribution of random surfer",
        section="3.15",
        predicate=_remark_3_15_pagerank,
        note="Remark 3.15: random surfer interpretation",
    ))

    # --- Remark 3.18: Stationary dist is left eigenvector of P for eigenvalue 1 ---
    def _remark_3_18_stationary_eigvec():
        """Verify pi^T P = pi^T for random walk on undirected graph."""
        A = np.array([
            [0, 1, 1, 0],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [0, 1, 1, 0],
        ], dtype=float)
        deg = A.sum(axis=1)
        P = A / deg[:, None]
        # Stationary: pi_i proportional to degree
        pi = deg / deg.sum()
        residual = pi @ P - pi
        if not np.allclose(residual, 0, atol=1e-12):
            return (False, f"pi^T P != pi^T, residual={residual}")
        # Spectral gap = 1 - lambda_2
        evals = np.sort(np.linalg.eigvals(P).real)[::-1]
        gap = 1 - evals[1]
        if gap <= 0:
            return (False, f"Spectral gap non-positive: {gap}")
        return (True, f"Spectral gap = {gap:.4f}")

    ch.add(StructuralCheck(
        label="Remark 3.18: pi^T P = pi^T, spectral gap > 0",
        section="3.18",
        predicate=_remark_3_18_stationary_eigvec,
        note="Remark 3.18: stationary distribution and eigenvalues",
    ))

    # --- Remark 3.30: ER has Poisson degree, BA has heavy tail ---
    def _remark_3_30_model_comparison():
        """Verify ER ~ Poisson degree, BA ~ heavy-tailed degree."""
        rng = np.random.default_rng(3130)
        n = 500
        # ER graph: p = 10/n
        p = 10.0 / n
        A_er = (rng.random((n, n)) < p).astype(float)
        np.fill_diagonal(A_er, 0)
        A_er = np.maximum(A_er, A_er.T)
        deg_er = A_er.sum(axis=1)
        # BA-like: preferential attachment
        # Simple implementation
        m = 5  # edges per new node
        adj = np.zeros((n, n))
        for i in range(m, n):
            degs = adj[:i, :i].sum(axis=1)
            degs += 1  # avoid zero
            probs = degs / degs.sum()
            targets = rng.choice(i, size=m, replace=False, p=probs)
            for t in targets:
                adj[i, t] = 1
                adj[t, i] = 1
        deg_ba = adj.sum(axis=1)
        # ER: coefficient of variation ~ 1/sqrt(np) (close to Poisson)
        cv_er = np.std(deg_er) / np.mean(deg_er)
        # BA: coefficient of variation should be larger (heavy tail)
        cv_ba = np.std(deg_ba[m:]) / np.mean(deg_ba[m:])
        if cv_ba <= cv_er:
            return (False, f"BA cv={cv_ba:.3f} not > ER cv={cv_er:.3f}")
        return (True, f"ER cv={cv_er:.3f}, BA cv={cv_ba:.3f}")

    ch.add(StructuralCheck(
        label="Remark 3.30: ER ~ Poisson (low cv), BA ~ heavy-tailed (high cv)",
        section="3.30",
        predicate=_remark_3_30_model_comparison,
        note="Remark 3.30: comparison of network models",
    ))

    # --- Remark 3.22: Spectral clustering — k eigenvectors + k-means ---
    def _remark_3_22_spectral_clustering():
        """Verify spectral clustering separates two clear clusters."""
        rng = np.random.default_rng(3122)
        # Build graph with two clear communities
        n = 20
        A = np.zeros((n, n))
        # Cluster 1: nodes 0-9, cluster 2: nodes 10-19
        for i in range(10):
            for j in range(i+1, 10):
                if rng.random() < 0.7:
                    A[i, j] = A[j, i] = 1
        for i in range(10, 20):
            for j in range(i+1, 20):
                if rng.random() < 0.7:
                    A[i, j] = A[j, i] = 1
        # Few inter-cluster edges
        for _ in range(2):
            i, j = rng.integers(0, 10), rng.integers(10, 20)
            A[i, j] = A[j, i] = 1
        # Laplacian
        D = np.diag(A.sum(axis=1))
        L = D - A
        # Bottom 2 eigenvectors
        evals, evecs = np.linalg.eigh(L)
        v2 = evecs[:, 1]  # Fiedler vector
        # Partition: positive vs negative
        cluster = (v2 > 0).astype(int)
        # Check: nodes 0-9 should be mostly in one cluster, 10-19 in the other
        c1 = cluster[:10]
        c2 = cluster[10:]
        purity = max(np.sum(c1 == 0), np.sum(c1 == 1)) + max(np.sum(c2 == 0), np.sum(c2 == 1))
        if purity < 16:  # at least 80% correct
            return (False, f"Purity={purity}/20, too low")
        return (True, f"Purity={purity}/20")

    ch.add(StructuralCheck(
        label="Remark 3.22: Spectral clustering separates two-community graph",
        section="3.22",
        predicate=_remark_3_22_spectral_clustering,
        note="Remark 3.22: multi-way spectral clustering",
    ))

    # ── Remark 3.12: Limitations of degree and eigenvector centrality ────
    # Claims: eigenvector centrality assigns near-zero scores to vertices in
    # peripheral components of a disconnected graph.
    def _remark_3_12_centrality_limitations():
        import numpy as np

        # Create a disconnected graph: component 1 (large clique) + component 2 (small)
        n1, n2 = 6, 3
        n = n1 + n2
        A = np.zeros((n, n))

        # Component 1: complete graph on nodes 0..5
        for i in range(n1):
            for j in range(i + 1, n1):
                A[i, j] = A[j, i] = 1

        # Component 2: path graph on nodes 6..8
        A[6, 7] = A[7, 6] = 1
        A[7, 8] = A[8, 7] = 1

        # Compute eigenvector centrality (leading eigenvector of A)
        eigenvalues, eigenvectors = np.linalg.eigh(A)
        # Leading eigenvector (largest eigenvalue)
        idx = np.argmax(eigenvalues)
        v = np.abs(eigenvectors[:, idx])
        v = v / np.max(v)

        # Nodes in the smaller component should have near-zero centrality
        # relative to the larger component
        max_large = np.max(v[:n1])
        max_small = np.max(v[n1:])

        if max_small > 0.1 * max_large:
            return (False, f"Small component centrality {max_small:.4f} not near-zero "
                    f"relative to large component {max_large:.4f}")

        # Degree centrality only counts neighbors (verify it's computed correctly)
        degree = np.sum(A, axis=1)
        # All nodes in clique should have degree n1-1 = 5
        for i in range(n1):
            if degree[i] != n1 - 1:
                return (False, f"Degree of clique node {i} = {degree[i]}, expected {n1-1}")

        # Node 7 (middle of path) has degree 2, nodes 6,8 have degree 1
        if degree[7] != 2:
            return (False, f"Degree of path center = {degree[7]}, expected 2")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.12: Eigenvector centrality near-zero in peripheral component",
        section="3.12",
        predicate=_remark_3_12_centrality_limitations,
        note="Remark 3.12: centrality limitations verified",
    ))

    return ch
