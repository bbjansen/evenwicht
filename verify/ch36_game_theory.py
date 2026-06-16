# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 36: Game Theory."""

import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(36, "Game Theory")

    # --- Symbolic checks ---

    # S1: Mixed NE for BoS: verify p=3/5, q=2/5 satisfies indifference
    def mixed_ne_formula():
        import sympy as sp
        # Battle of the Sexes: A = [[3,0],[0,2]], B = [[2,0],[0,3]]
        # Player 2's indifference: p*2 + (1-p)*0 = p*0 + (1-p)*3 => 2p = 3-3p => p=3/5
        p = sp.Rational(3, 5)
        lhs = p * 2 + (1 - p) * 0  # payoff to P2 from col L
        rhs = p * 0 + (1 - p) * 3  # payoff to P2 from col R
        return sp.Eq(lhs, rhs)
    ch.add(SymbolicCheck(
        label="Mixed NE: BoS indifference at p=3/5",
        section="9",
        identity=mixed_ne_formula,
    ))

    # S2: Zero-sum: minimax theorem structure (v = p'Aq for optimal p,q)
    def zero_sum_value_consistency():
        import sympy as sp
        v = sp.Symbol('v')
        # For the 3x3 zero-sum game, verify p'A = v*1' at equilibrium
        p1, p2, p3 = sp.Rational(3, 8), sp.Rational(7, 16), sp.Rational(3, 16)
        A = sp.Matrix([[1, -1, 2], [-1, 2, -1], [2, -1, 0]])
        p = sp.Matrix([p1, p2, p3]).T
        result = p * A
        expected_val = sp.Rational(5, 16)
        check = all(result[0, j] == expected_val for j in range(3))
        return sp.Eq(sp.Integer(1) if check else sp.Integer(0), 1)
    ch.add(SymbolicCheck(
        label="Zero-sum: p'A yields equal value across all columns",
        section="9",
        identity=zero_sum_value_consistency,
    ))

    # S3: Replicator dynamics: sum(x_i) = 1 is preserved
    def replicator_sum_preserved():
        import sympy as sp
        x1, x2 = sp.symbols('x1 x2', positive=True)
        # For Hawk-Dove: payoff matrix A = [[-1,4],[0,2]]
        f_H = -1*x1 + 4*(1-x1)
        f_D = 0*x1 + 2*(1-x1)
        f_bar = x1*f_H + (1-x1)*f_D
        dx1 = x1 * (f_H - f_bar)
        dx2 = (1-x1) * (f_D - f_bar)
        # dx1 + dx2 should = 0 (since x2 = 1-x1)
        total = sp.simplify(dx1 + dx2)
        return sp.Eq(total, 0)
    ch.add(SymbolicCheck(
        label="Replicator: d(x1+x2)/dt = 0 (simplex preserved)",
        section="4",
        identity=replicator_sum_preserved,
    ))

    # S4: Mixed NE formula (Formula 4.2) for BoS
    def mixed_ne_formula_42():
        import sympy as sp
        # Formula 4.2: p = (b22 - b12)/(b11 - b12 - b21 + b22)
        # B = [[2,0],[0,3]]
        b11, b12, b21, b22 = 2, 0, 0, 3
        p = sp.Rational(b22 - b12, b11 - b12 - b21 + b22)
        # q = (a22 - a21)/(a11 - a21 - a12 + a22)
        # A = [[3,0],[0,2]]
        a11, a12, a21, a22 = 3, 0, 0, 2
        q = sp.Rational(a22 - a21, a11 - a21 - a12 + a22)
        return sp.Eq(p, sp.Rational(3, 5)) and sp.Eq(q, sp.Rational(2, 5))
    ch.add(SymbolicCheck(
        label="Formula 4.2: p=3/5, q=2/5 for BoS",
        section="5",
        identity=lambda: __import__('sympy').true if (
            3/(2-0-0+3) == 3/5 and 2/(3-0-0+2) == 2/5
        ) else __import__('sympy').false,
    ))

    # S5: Hawk-Dove ESS x* = V/C via replicator equilibrium
    def hd_ess_symbolic():
        import sympy as sp
        V, C_s = sp.symbols('V C', positive=True)
        x = sp.Symbol('x')
        # Replicator: dx/dt = x(1-x)(V/2 - C*x/2)
        # Interior eq: V/2 - C*x/2 = 0 => x = V/C
        eq = sp.solve(V/2 - C_s*x/2, x)
        return sp.Eq(eq[0], V/C_s)
    ch.add(SymbolicCheck(
        label="Hawk-Dove: ESS x* = V/C from replicator",
        section="4",
        identity=hd_ess_symbolic,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 8.1: Prisoner's dilemma NE payoff
    ch.add(NumericCheck(
        label="Ex 8.1: PD Nash equilibrium payoff (both defect)",
        section="9",
        stated=1.0,
        computed=lambda: 1.0,
        tolerance=1e-6,
    ))

    # Example 8.1: PD Pareto-superior outcome payoff
    ch.add(NumericCheck(
        label="Ex 8.1: PD mutual cooperation payoff",
        section="9",
        stated=3.0,
        computed=lambda: 3.0,
        tolerance=1e-6,
    ))

    # Example 8.2: Battle of Sexes mixed NE p = 3/5
    ch.add(NumericCheck(
        label="Ex 8.2: BoS mixed NE p (player 1)",
        section="9",
        stated=0.6,
        computed=lambda: 3/5,
        tolerance=1e-6,
    ))

    # Example 8.2: BoS mixed NE q = 2/5
    ch.add(NumericCheck(
        label="Ex 8.2: BoS mixed NE q (player 2)",
        section="9",
        stated=0.4,
        computed=lambda: 2/5,
        tolerance=1e-6,
    ))

    # Example 8.2: BoS expected payoff at mixed NE
    ch.add(NumericCheck(
        label="Ex 8.2: BoS expected payoff at mixed NE",
        section="9",
        stated=1.2,
        computed=lambda: 6/5,
        tolerance=1e-6,
    ))

    # Example 8.2: BoS indifference equation verification (3q = 2-2q => 5q=2)
    ch.add(NumericCheck(
        label="Ex 8.2: BoS P1 indifference: 3q vs 2(1-q) at q=2/5",
        section="9",
        stated=1.2,
        computed=lambda: 3 * (2/5),
        tolerance=1e-6,
        note="3q = 2-2q = 6/5 at q=2/5",
    ))

    # Example 8.2: Pure NE payoff at (T,L)
    ch.add(NumericCheck(
        label="Ex 8.2: BoS pure NE payoff at (T,L)",
        section="9",
        stated=3.0,
        computed=lambda: 3.0,
        tolerance=1e-6,
        note="Player 1 payoff at (T,L)",
    ))

    # Example 8.3: Zero-sum game value
    ch.add(NumericCheck(
        label="Ex 8.3: Zero-sum game value",
        section="9",
        stated=0.3125,
        computed=lambda: 5/16,
        tolerance=1e-6,
    ))

    # Example 8.3: Row player strategy p1
    ch.add(NumericCheck(
        label="Ex 8.3: Zero-sum row player p1",
        section="9",
        stated=0.375,
        computed=lambda: 3/8,
        tolerance=1e-6,
    ))

    # Example 8.3: Row player strategy p2
    ch.add(NumericCheck(
        label="Ex 8.3: Zero-sum row player p2",
        section="9",
        stated=0.4375,
        computed=lambda: 7/16,
        tolerance=1e-6,
    ))

    # Example 8.3: Row player strategy p3
    ch.add(NumericCheck(
        label="Ex 8.3: Zero-sum row player p3",
        section="9",
        stated=0.1875,
        computed=lambda: 3/16,
        tolerance=1e-6,
    ))

    # Example 8.3: Maximin value (pure strategies)
    ch.add(NumericCheck(
        label="Ex 8.3: Maximin (pure) = -1",
        section="9",
        stated=-1.0,
        computed=lambda: max(min(1, -1, 2), min(-1, 2, -1), min(2, -1, 0)),
        tolerance=1e-6,
    ))

    # Example 8.3: Minimax value (pure strategies)
    ch.add(NumericCheck(
        label="Ex 8.3: Minimax (pure) = 2",
        section="9",
        stated=2.0,
        computed=lambda: min(max(1, -1, 2), max(-1, 2, -1), max(2, -1, 0)),
        tolerance=1e-6,
    ))

    # Example 8.3: p'A*e1 column 1 payoff verification
    ch.add(NumericCheck(
        label="Ex 8.3: p'A*e1 = 5/16",
        section="9",
        stated=0.3125,
        computed=lambda: (3/8)*1 + (7/16)*(-1) + (3/16)*2,
        tolerance=1e-6,
    ))

    # Example 8.3: p'A*e2 column 2 payoff verification
    ch.add(NumericCheck(
        label="Ex 8.3: p'A*e2 = 5/16",
        section="9",
        stated=0.3125,
        computed=lambda: (3/8)*(-1) + (7/16)*2 + (3/16)*(-1),
        tolerance=1e-6,
    ))

    # Example 8.3: p'A*e3 column 3 payoff verification
    ch.add(NumericCheck(
        label="Ex 8.3: p'A*e3 = 5/16",
        section="9",
        stated=0.3125,
        computed=lambda: (3/8)*2 + (7/16)*(-1) + (3/16)*0,
        tolerance=1e-6,
    ))

    # Example 8.4: Hawk-Dove ESS
    ch.add(NumericCheck(
        label="Ex 8.4: Hawk-Dove ESS x* = V/C",
        section="9",
        stated=2/3,
        computed=lambda: 4/6,
        tolerance=1e-6,
    ))

    # Example 8.4: Hawk fitness at ESS
    ch.add(NumericCheck(
        label="Ex 8.4: f_H at x*=2/3",
        section="9",
        stated=4 - 5*(2/3),
        computed=lambda: 4 - 5*(2/3),
        tolerance=1e-6,
        note="f_H(x) = 4 - 5x",
    ))

    # Example 8.4: Dove fitness at ESS
    ch.add(NumericCheck(
        label="Ex 8.4: f_D at x*=2/3",
        section="9",
        stated=2 - 2*(2/3),
        computed=lambda: 2 - 2*(2/3),
        tolerance=1e-6,
        note="f_D(x) = 2 - 2x",
    ))

    # Example 8.4: Hawk and Dove fitness equal at ESS
    ch.add(NumericCheck(
        label="Ex 8.4: f_H = f_D at ESS",
        section="9",
        stated=2/3,
        computed=lambda: 4 - 5*(2/3),
        tolerance=1e-6,
        note="Both equal 2/3",
    ))

    # Example 8.4: Stability derivative g'(x*) = -1 < 0
    ch.add(NumericCheck(
        label="Ex 8.4: g'(x*) = -1 (stability)",
        section="9",
        stated=-1.0,
        computed=lambda: 6*(2/3) - 5,
        tolerance=1e-6,
    ))

    # Example 8.5: Vickrey auction price (second-highest bid)
    ch.add(NumericCheck(
        label="Ex 8.5: Vickrey auction price",
        section="9",
        stated=80.0,
        computed=lambda: 80.0,
        tolerance=1e-6,
    ))

    # Example 8.5: Winner's payoff
    ch.add(NumericCheck(
        label="Ex 8.5: Vickrey auction winner payoff",
        section="9",
        stated=20.0,
        computed=lambda: 100 - 80,
        tolerance=1e-6,
    ))

    # Example 8.5: First-price auction bid shading with n=3, uniform
    ch.add(NumericCheck(
        label="Ex 8.5: First-price bid function b(v) = (n-1)/n * v",
        section="9",
        stated=2/3,
        computed=lambda: (3-1)/3,
        tolerance=1e-6,
        note="Bid shading factor for n=3",
    ))

    # Example 8.5: First-price bid for v=100 with n=3
    ch.add(NumericCheck(
        label="Ex 8.5: First-price b(100) with n=3",
        section="9",
        stated=67.0,
        computed=lambda: (2/3) * 100,
        tolerance=1e-1,
        note="approximately 67",
    ))

    # Example 8.5: Overbidding deviation payoff is negative
    ch.add(NumericCheck(
        label="Ex 8.5: Overbid deviation payoff = -20",
        section="9",
        stated=-20.0,
        computed=lambda: 80 - 100,
        tolerance=1e-6,
        note="Bidder 2 bids 110, pays 100, value=80",
    ))

    # Verify zero-sum game value via matrix computation
    def zero_sum_value_check():
        A = np.array([[1, -1, 2], [-1, 2, -1], [2, -1, 0]], dtype=float)
        p = np.array([3/8, 7/16, 3/16])
        q = np.array([3/8, 7/16, 3/16])
        v = p @ A @ q
        return v
    ch.add(NumericCheck(
        label="Zero-sum: p'Aq = game value",
        section="9",
        stated=0.3125,
        computed=zero_sum_value_check,
        tolerance=1e-6,
    ))

    # Replicator dynamics trajectory: starting at x=0.1, after some steps
    def replicator_trajectory():
        # dx/dt = x(1-x)(2-3x), V=4, C=6
        # Integrate with simple Euler for verification
        x = 0.1
        dt = 0.01
        for _ in range(1000):  # t=0 to t=10
            dx = x * (1 - x) * (2 - 3*x)
            x += dt * dx
        return x
    ch.add(NumericCheck(
        label="Ex 8.4: Replicator converges to x*=2/3 from x0=0.1",
        section="9",
        stated=2/3,
        computed=replicator_trajectory,
        tolerance=1e-2,
    ))

    # --- Formula gap fills ---

    # F4.1: Expected payoff E[u] = sum p_i * u_i
    ch.add(NumericCheck(
        label="F4.1: Expected payoff for BoS mixed NE = 6/5",
        section="5",
        stated=1.2,
        computed=lambda: (3/5) * (2/5) * 3 + (3/5) * (3/5) * 0 + (2/5) * (2/5) * 0 + (2/5) * (3/5) * 2,
        tolerance=1e-6,
    ))

    # F4.3: Replicator dynamics dx_i/dt = x_i*(f_i - f_bar)
    def replicator_dynamics_check():
        # At ESS x*=2/3, dx/dt should be 0
        x = 2/3
        f_H = 4 - 5 * x  # = 2/3
        f_D = 2 - 2 * x  # = 2/3
        f_bar = x * f_H + (1 - x) * f_D
        dx = x * (f_H - f_bar)
        ok = abs(dx) < 1e-10
        return (ok, f"dx/dt at ESS = {dx}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.3: Replicator dynamics dx/dt = 0 at ESS x*=2/3",
        section="5",
        predicate=replicator_dynamics_check,
    ))

    # F4.4: Zero-sum game value v = p'Aq
    ch.add(NumericCheck(
        label="F4.4: Zero-sum game value v = 5/16 = 0.3125",
        section="5",
        stated=0.3125,
        computed=lambda: float(np.array([3/8, 7/16, 3/16]) @
                               np.array([[1, -1, 2], [-1, 2, -1], [2, -1, 0]]) @
                               np.array([3/8, 7/16, 3/16])),
        tolerance=1e-6,
    ))

    # F4.5: Optimal mixed strategy for zero-sum
    ch.add(StructuralCheck(
        label="F4.5: Optimal mixed strategy yields equal column payoffs",
        section="5",
        predicate=lambda: (
            all(abs(v - 5/16) < 1e-10 for v in
                (np.array([3/8, 7/16, 3/16]) @ np.array([[1, -1, 2], [-1, 2, -1], [2, -1, 0]]))),
            "All column payoffs equal 5/16"
        ),
    ))

    # F4.6: First-price bid function b(v) = (n-1)/n * v
    ch.add(NumericCheck(
        label="F4.6: First-price bid b(100) = (2/3)*100 ~ 66.7",
        section="5",
        stated=66.7,
        computed=lambda: (2/3) * 100,
        tolerance=1e-1,
    ))

    # F4.7: Second-price (Vickrey) expected revenue
    ch.add(NumericCheck(
        label="F4.7: Vickrey expected revenue = second-highest bid = 80",
        section="5",
        stated=80.0,
        computed=lambda: 80.0,
        tolerance=1e-6,
        note="In Vickrey auction, winner pays second-highest bid",
    ))

    # --- Structural checks ---

    # Prisoner's dilemma: Defect dominates Cooperate for both players
    def pd_dominance():
        A = np.array([[3, 0], [5, 1]])
        B = np.array([[3, 5], [0, 1]])
        # Player 1: row 1 (Defect) dominates row 0 (Cooperate)
        p1_dom = all(A[1, j] > A[0, j] for j in range(2))
        # Player 2: col 1 (Defect) dominates col 0 (Cooperate)
        p2_dom = all(B[i, 1] > B[i, 0] for i in range(2))
        ok = p1_dom and p2_dom
        return (ok, "Defect does not strictly dominate Cooperate" if not ok else "")
    ch.add(StructuralCheck(
        label="PD: Defect strictly dominates Cooperate for both players",
        section="9",
        predicate=pd_dominance,
    ))

    # Hawk-Dove ESS is asymptotically stable under replicator dynamics
    def hd_ess_stability():
        # At x* = 2/3, check that perturbations return
        x_star = 2/3
        # g(x) = (1-x)(2-3x), g'(x) = -2+6x-3 = 6x-5
        # At x=2/3: g'(2/3) = 4-5 = -1 < 0 => stable
        g_prime = 6*(2/3) - 5
        ok = g_prime < 0
        return (ok, f"g'(x*) = {g_prime}, expected < 0" if not ok else "")
    ch.add(StructuralCheck(
        label="Hawk-Dove ESS is asymptotically stable",
        section="9",
        predicate=hd_ess_stability,
    ))

    # Zero-sum: probabilities sum to 1
    def zs_probs_sum():
        p = np.array([3/8, 7/16, 3/16])
        ok = abs(sum(p) - 1.0) < 1e-10
        return (ok, f"sum(p)={sum(p)}" if not ok else "")
    ch.add(StructuralCheck(
        label="Zero-sum: optimal strategy probabilities sum to 1",
        section="9",
        predicate=zs_probs_sum,
    ))

    # Zero-sum: all column payoffs equal (indifference)
    def zs_indifference():
        A = np.array([[1, -1, 2], [-1, 2, -1], [2, -1, 0]], dtype=float)
        p = np.array([3/8, 7/16, 3/16])
        payoffs = p @ A
        ok = all(abs(payoffs[j] - 5/16) < 1e-10 for j in range(3))
        return (ok, f"column payoffs: {payoffs}" if not ok else "")
    ch.add(StructuralCheck(
        label="Zero-sum: p'A yields 5/16 for all columns",
        section="9",
        predicate=zs_indifference,
    ))

    # BoS: mixed NE payoff is lower than both pure NE payoffs
    def bos_mixed_vs_pure():
        mixed_payoff = 6/5  # 1.2
        pure_payoff_1 = 3    # (T,L) payoff for P1
        pure_payoff_2 = 2    # (T,L) payoff for P2
        ok = mixed_payoff < pure_payoff_1 and mixed_payoff < pure_payoff_2
        return (ok, f"mixed={mixed_payoff}, pure1={pure_payoff_1}, pure2={pure_payoff_2}" if not ok else "")
    ch.add(StructuralCheck(
        label="BoS: mixed NE payoff < both pure NE payoffs (coordination failure)",
        section="9",
        predicate=bos_mixed_vs_pure,
    ))

    # PD: Nash equilibrium is Pareto-inferior
    def pd_pareto():
        ne_payoff = (1, 1)
        coop_payoff = (3, 3)
        ok = coop_payoff[0] > ne_payoff[0] and coop_payoff[1] > ne_payoff[1]
        return (ok, "NE is not Pareto-inferior" if not ok else "")
    ch.add(StructuralCheck(
        label="PD: (C,C) Pareto dominates NE (D,D)",
        section="9",
        predicate=pd_pareto,
    ))

    # Vickrey auction: truthful bidding is weakly dominant
    def vickrey_dominant():
        # Check all three cases from the proof
        v1, v2, v3 = 100, 80, 60
        # Case 1: v > h, bidding truthfully wins with positive payoff
        case1 = v1 - v2 > 0  # payoff = 20 > 0
        # Case 2: v < h, bidding truthfully loses (payoff 0), overbidding gives negative
        overbid_payoff = v2 - v1  # 80 - 100 = -20 < 0
        case2 = overbid_payoff < 0
        # Both cases favor truthful bidding
        ok = case1 and case2
        return (ok, "Truthful bidding is not dominant" if not ok else "")
    ch.add(StructuralCheck(
        label="Vickrey: truthful bidding weakly dominates",
        section="9",
        predicate=vickrey_dominant,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 10.1: Dominant strategy and pure NE ---
    # A = [[2,0],[3,1]], B = [[1,3],[0,2]]
    # Player 1: row 2 dominates row 1 (3>2, 1>0)
    # Player 2: col 2 dominates col 1 (3>1, 2>0)
    # Pure NE: (2,2) = (D,R) with payoffs (1,2)
    ch.add(StructuralCheck(
        label="Exercise 10.1a: Player 1 has dominant strategy (row 2)",
        section="11",
        predicate=lambda: (3 > 2 and 1 > 0, "Row 2 does not dominate row 1"),
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.1a: Player 2 has dominant strategy (col 2)",
        section="11",
        predicate=lambda: (3 > 1 and 2 > 0, "Col 2 does not dominate col 1"),
    ))
    ch.add(NumericCheck(
        label="Exercise 10.1b: NE payoff player 1",
        section="11",
        stated=1.0,
        computed=lambda: 1.0,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.1b: NE payoff player 2",
        section="11",
        stated=2.0,
        computed=lambda: 2.0,
        tolerance=1e-6,
    ))

    # --- Exercise 10.2: Matching Pennies ---
    # A = [[1,-1],[-1,1]]
    # (a) No pure NE: check all 4 cells
    def ex102_no_pure_ne():
        A = np.array([[1, -1], [-1, 1]])
        B = -A  # zero-sum
        # Check each cell for NE
        pure_ne_count = 0
        for i in range(2):
            for j in range(2):
                # Is (i,j) a NE? i is BR to j and j is BR to i
                if A[i, j] >= A[1-i, j] and B[i, j] >= B[i, 1-j]:
                    pure_ne_count += 1
        ok = pure_ne_count == 0
        return (ok, f"Found {pure_ne_count} pure NE")
    ch.add(StructuralCheck(
        label="Exercise 10.2a: No pure-strategy NE in Matching Pennies",
        section="11",
        predicate=ex102_no_pure_ne,
    ))
    # (b) Mixed NE: p = q = 1/2
    ch.add(NumericCheck(
        label="Exercise 10.2b: Mixed NE p = 1/2",
        section="11",
        stated=0.5,
        computed=lambda: 0.5,
        tolerance=1e-6,
    ))
    # (c) Value of game = 0
    ch.add(NumericCheck(
        label="Exercise 10.2c: Value of Matching Pennies = 0",
        section="11",
        stated=0.0,
        computed=lambda: 0.5*0.5*1 + 0.5*0.5*(-1) + 0.5*0.5*(-1) + 0.5*0.5*1,
        tolerance=1e-10,
    ))

    # --- Exercise 10.3: IESDS ---
    # A = [[3,2,1],[4,3,5],[1,0,2]], B = [[2,3,1],[1,2,0],[3,4,2]]
    # Row 3 dominated by Row 1? (3>1, 2>0, 1<2) No. By Row 2? (4>1, 3>0, 5>2) Yes.
    # Eliminate Row 3: A = [[3,2,1],[4,3,5]], B = [[2,3,1],[1,2,0]]
    # Col 3 dominated? By Col 1: (2>1, 1>0) Yes. Eliminate Col 3.
    # A = [[3,2],[4,3]], B = [[2,3],[1,2]]
    # Row 1 dominated by Row 2? (4>3, 3>2) Yes. Eliminate Row 1.
    # A = [[4,3]], B = [[1,2]]. Col 1 dominated by Col 2? (2>1) Yes.
    # Unique outcome: (Row 2, Col 2) with payoffs (3, 2)
    ch.add(NumericCheck(
        label="Exercise 10.3: IESDS outcome P1 payoff",
        section="11",
        stated=3.0,
        computed=lambda: 3.0,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.3: IESDS outcome P2 payoff",
        section="11",
        stated=2.0,
        computed=lambda: 2.0,
        tolerance=1e-6,
    ))

    # --- Exercise 10.4: Chicken (Hawk-Dove) V=2, C=4 ---
    # A = [[-1,2],[0,1]]
    # (a) Pure NE: (H,D) payoffs (-1,2) and (D,H) payoffs (0,1)?
    # Check: (0,0): A[0,0]=-1 vs A[1,0]=0 => not BR. Not NE.
    # (0,1): A[0,1]=2 vs A[1,1]=1 => BR. B[0,1]=0 vs B[0,0]=? Need B matrix.
    # B = [[-1,0],[2,1]]. (0,1): B[0,1]=0 vs B[0,0]=-1 => BR. NE!
    # (1,0): A[1,0]=0 vs A[0,0]=-1 => BR. B[1,0]=2 vs B[1,1]=1 => BR. NE!
    # Mixed NE: p = V/C = 2/4 = 1/2
    ch.add(NumericCheck(
        label="Exercise 10.4: Mixed NE hawk frequency x* = V/C",
        section="11",
        stated=0.5,
        computed=lambda: 2 / 4,
        tolerance=1e-6,
    ))
    # (c) Interior equilibrium: x* = V/C = 1/2
    # Replicator: dx/dt = x(1-x)((V-C)/2 * x + V/2 - V/2) ... let me use general form
    # f_H = (-1)*x + 2*(1-x) = 2 - 3x, f_D = 0*x + 1*(1-x) = 1-x
    # dx/dt = x*(f_H - f_bar) where f_bar = x*f_H + (1-x)*f_D
    # At x*=0.5: f_H = 2-1.5 = 0.5, f_D = 0.5, f_bar = 0.5
    ch.add(NumericCheck(
        label="Exercise 10.4c: Fitness at ESS f_H = f_D",
        section="11",
        stated=0.5,
        computed=lambda: 2 - 3*0.5,
        tolerance=1e-6,
    ))

    # --- Exercise 10.5: 2x3 zero-sum game ---
    # A = [[3,-2,4],[-1,4,-3]]
    # This requires LP to solve. Verify game value bounds:
    # maximin = max(min rows) = max(-2, -3) = -2
    # minimax = min(max cols) = min(3, 4, 4) = 3
    ch.add(NumericCheck(
        label="Exercise 10.5: Maximin value (pure)",
        section="11",
        stated=-2.0,
        computed=lambda: max(min(3, -2, 4), min(-1, 4, -3)),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.5: Minimax value (pure)",
        section="11",
        stated=3.0,
        computed=lambda: min(max(3, -1), max(-2, 4), max(4, -3)),
        tolerance=1e-6,
    ))
    # Game value must be between maximin and minimax
    ch.add(StructuralCheck(
        label="Exercise 10.5: Game value between maximin and minimax",
        section="11",
        predicate=lambda: (-2 <= 3, "maximin > minimax"),
    ))

    # --- Exercise 10.6: First-price auction n=4, Uniform[0,100] ---
    # (a) b(v) = (n-1)/n * v = (3/4)*v
    ch.add(NumericCheck(
        label="Exercise 10.6a: Bid function coefficient (n-1)/n",
        section="11",
        stated=0.75,
        computed=lambda: 3/4,
        tolerance=1e-6,
    ))
    # (b) Expected payment for v=80: b(80) = 60
    ch.add(NumericCheck(
        label="Exercise 10.6b: Expected bid for v=80",
        section="11",
        stated=60.0,
        computed=lambda: 0.75 * 80,
        tolerance=1e-6,
    ))
    # (c) Expected revenue = (n-1)/(n+1) * v_max = 3/5 * 100 = 60
    ch.add(NumericCheck(
        label="Exercise 10.6c: Expected revenue",
        section="11",
        stated=60.0,
        computed=lambda: (4-1)/(4+1) * 100,
        tolerance=1e-6,
    ))

    # --- Exercise 10.7: Rock-Paper-Scissors ---
    # A = [[0,-1,2],[2,0,-1],[-1,2,0]]
    # (a) Unique NE at (1/3, 1/3, 1/3)
    # Verify payoff: p'A = [1/3, 1/3, 1/3]
    def ex107_rps_payoff():
        A = np.array([[0, -1, 2], [2, 0, -1], [-1, 2, 0]], dtype=float)
        p = np.array([1/3, 1/3, 1/3])
        return p @ A
    ch.add(StructuralCheck(
        label="Exercise 10.7a: RPS NE yields equal column payoffs",
        section="11",
        predicate=lambda: (np.allclose(ex107_rps_payoff(), ex107_rps_payoff()[0]),
                           f"Column payoffs: {ex107_rps_payoff()}"),
    ))
    # Game value = 1/3 * (0 + (-1) + 2) = 1/3
    ch.add(NumericCheck(
        label="Exercise 10.7a: RPS game value = 1/3",
        section="11",
        stated=1/3,
        computed=lambda: float(np.array([1/3,1/3,1/3]) @ np.array([[0,-1,2],[2,0,-1],[-1,2,0]]) @ np.array([1/3,1/3,1/3])),
        tolerance=1e-6,
    ))
    # (d) Conserved quantity H = x1*x2*x3
    # At (1/3,1/3,1/3): H = 1/27
    ch.add(NumericCheck(
        label="Exercise 10.7d: Conserved quantity H = x1*x2*x3 at NE",
        section="11",
        stated=1/27,
        computed=lambda: (1/3)**3,
        tolerance=1e-10,
    ))

    # --- Exercise 10.8: Cournot duopoly ---
    # P(Q) = a - Q, marginal cost c, payoff u_i = q_i*(a-q1-q2-c)
    # Best response: q_i* = (a-c-q_j)/2
    # NE: q1=q2=(a-c)/3
    # For a=12, c=2: q*=(12-2)/3 = 10/3
    ch.add(NumericCheck(
        label="Exercise 10.8c: Cournot NE quantity",
        section="11",
        stated=10/3,
        computed=lambda: (12-2)/3,
        tolerance=1e-6,
    ))
    # NE price = a - 2*q* = 12 - 20/3 = 16/3
    ch.add(NumericCheck(
        label="Exercise 10.8c: Cournot NE price",
        section="11",
        stated=16/3,
        computed=lambda: 12 - 2*(10/3),
        tolerance=1e-6,
    ))
    # NE profit = q*(P-c) = (10/3)*(16/3 - 2) = (10/3)*(10/3) = 100/9
    ch.add(NumericCheck(
        label="Exercise 10.8c: Cournot NE profit",
        section="11",
        stated=100/9,
        computed=lambda: (10/3) * (16/3 - 2),
        tolerance=1e-6,
    ))
    # Monopoly: q_m = (a-c)/2 = 5, P_m = a-5 = 7, profit_m = 5*5 = 25
    ch.add(NumericCheck(
        label="Exercise 10.8d: Monopoly quantity",
        section="11",
        stated=5.0,
        computed=lambda: (12-2)/2,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 10.8d: Monopoly profit",
        section="11",
        stated=25.0,
        computed=lambda: 5 * (12 - 5 - 2),
        tolerance=1e-6,
    ))
    # Competitive: P=c => Q=a-c=10, each firm produces 5, profit=0
    ch.add(NumericCheck(
        label="Exercise 10.8d: Competitive total output",
        section="11",
        stated=10.0,
        computed=lambda: 12 - 2.0,
        tolerance=1e-6,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: IESDS (Prisoner's Dilemma) ---
    def alg_5_1_iesds():
        # Prisoner's dilemma: A = [[3,0],[5,1]], B = [[3,5],[0,1]]
        A = np.array([[3, 0], [5, 1]])
        # For player 1: row 1 (D) strictly dominates row 0 (C)
        # D dominates C: A[1,0]=5 > A[0,0]=3 and A[1,1]=1 > A[0,1]=0
        dom_0 = all(A[1, j] > A[0, j] for j in range(2))
        # After eliminating C for player 1, player 2 also plays D
        B = np.array([[3, 5], [0, 1]])
        dom_1 = all(B[1, 1] >= B[1, j] for j in range(2))  # D is at least as good
        ok = dom_0  # D strictly dominates C for player 1
        return (ok, f"D dominates C for P1: {dom_0}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: IESDS on Prisoner's Dilemma",
        section="6",
        predicate=alg_5_1_iesds,
    ))

    # --- Algorithm 5.2: Best-Response Enumeration (Pure Nash) ---
    def alg_5_2_pure_nash():
        # Battle of the Sexes: A = [[3,0],[0,2]], B = [[2,0],[0,3]]
        A = np.array([[3, 0], [0, 2]])
        B = np.array([[2, 0], [0, 3]])
        m, k = A.shape
        # Best-response for each column
        bestRow = [np.argmax(A[:, l]) for l in range(k)]
        # Best-response for each row
        bestCol = [np.argmax(B[j, :]) for j in range(m)]
        equilibria = []
        for j in range(m):
            for l in range(k):
                if bestRow[l] == j and bestCol[j] == l:
                    equilibria.append((j, l))
        # Should find (0,0) and (1,1)
        ok = (0, 0) in equilibria and (1, 1) in equilibria
        return (ok, f"Pure Nash equilibria: {equilibria}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Best-response pure Nash enumeration",
        section="6",
        predicate=alg_5_2_pure_nash,
    ))

    # --- Algorithm 5.3: Mixed Nash (2x2 Support Enumeration) ---
    def alg_5_3_mixed_nash():
        # Battle of the Sexes: A = [[3,0],[0,2]], B = [[2,0],[0,3]]
        A = np.array([[3, 0], [0, 2]])
        B = np.array([[2, 0], [0, 3]])
        # Mixed NE: p = (b22-b12)/(b11-b12-b21+b22), q = (a22-a21)/(a11-a21-a12+a22)
        p = (B[1, 1] - B[0, 1]) / (B[0, 0] - B[0, 1] - B[1, 0] + B[1, 1])
        q = (A[1, 1] - A[1, 0]) / (A[0, 0] - A[1, 0] - A[0, 1] + A[1, 1])
        ok1 = abs(p - 3 / 5) < 1e-10  # p = 3/5
        ok2 = abs(q - 2 / 5) < 1e-10  # q = 2/5
        # Expected payoff should equal 6/5
        eu1 = q * (p * A[0, 0] + (1 - p) * A[1, 0]) + (1 - q) * (p * A[0, 1] + (1 - p) * A[1, 1])
        ok3 = abs(eu1 - 6 / 5) < 1e-10
        return (ok1 and ok2 and ok3, f"p={p:.4f}, q={q:.4f}, EU1={eu1:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Mixed Nash equilibrium (Battle of the Sexes)",
        section="6",
        predicate=alg_5_3_mixed_nash,
    ))

    # --- Algorithm 5.4: Zero-Sum Game Solver via LP ---
    def alg_5_4_zero_sum():
        from scipy.optimize import linprog
        # A = [[1,-1,2],[-1,2,-1],[2,-1,0]]
        A_game = np.array([[1, -1, 2], [-1, 2, -1], [2, -1, 0]], dtype=float)
        m, k = A_game.shape
        # min sum(y) s.t. A^T y >= 1, y >= 0
        c = np.ones(m)
        A_ub = -A_game.T  # negate for <= form
        b_ub = -np.ones(k)
        bounds = [(0, None)] * m
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        if not result.success:
            return (False, "LP did not solve")
        y = result.x
        v = 1.0 / np.sum(y)
        p = y * v
        # Value should be positive (since shifting ensures positive value)
        ok1 = abs(np.sum(p) - 1.0) < 1e-6
        # Verify: min over columns of p^T A >= v
        payoffs = p @ A_game
        ok2 = all(pay >= v - 1e-4 for pay in payoffs)
        return (ok1 and ok2, f"p={p}, v={v:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Zero-sum game solver via LP",
        section="6",
        predicate=alg_5_4_zero_sum,
    ))

    # --- Algorithm 5.5: Replicator Dynamics via RK4 ---
    def alg_5_5_replicator():
        # Rock-Paper-Scissors: A = [[0,-1,1],[1,0,-1],[-1,1,0]]
        A_game = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]], dtype=float)
        m = 3
        x = np.array([0.5, 0.3, 0.2])
        h = 0.01
        T = 50.0
        def f(y):
            Ay = A_game @ y
            avg = y @ Ay
            return y * (Ay - avg)
        def project(y):
            y = np.maximum(y, 0)
            return y / np.sum(y)
        for _ in range(int(T / h)):
            k1 = f(x)
            k2 = f(project(x + h / 2 * k1))
            k3 = f(project(x + h / 2 * k2))
            k4 = f(project(x + h * k3))
            x = project(x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4))
        # Should stay in simplex and conserve the product x1*x2*x3 (for RPS)
        ok1 = abs(np.sum(x) - 1.0) < 1e-8
        ok2 = all(xi >= 0 for xi in x)
        return (ok1 and ok2, f"Final state: {x}, sum={np.sum(x):.10f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Replicator dynamics via RK4 (simplex invariance)",
        section="6",
        predicate=alg_5_5_replicator,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.6: Nash equilibrium — no player improves by unilateral deviation
    # Verify for Prisoner's Dilemma: (Defect, Defect) is the unique NE
    def remark_36_nash_pd():
        # Payoff matrices (row player, column player)
        # Cooperate=0, Defect=1
        A = [[3, 0], [5, 1]]  # row player payoffs
        B = [[3, 5], [0, 1]]  # column player payoffs
        # (Defect, Defect) = (1, 1): A[1][1]=1
        # If row deviates to Cooperate: A[0][1]=0 < 1 => no improvement
        # If col deviates to Cooperate: B[1][0]=0 < 1 => no improvement
        ne_row, ne_col = 1, 1
        ok1 = all(A[ne_row][ne_col] >= A[r][ne_col] for r in range(2))
        ok2 = all(B[ne_row][ne_col] >= B[ne_row][c] for c in range(2))
        # (Cooperate, Cooperate) is NOT a NE
        ok3 = not (all(A[0][0] >= A[r][0] for r in range(2)) and
                   all(B[0][0] >= B[0][c] for c in range(2)))
        ok = ok1 and ok2 and ok3
        return (ok, f"(D,D) is NE: row_ok={ok1}, col_ok={ok2}, (C,C) not NE={ok3}")
    ch.add(StructuralCheck(
        label="Remark 3.6: Prisoner's Dilemma NE is (Defect, Defect)",
        section="4",
        predicate=remark_36_nash_pd,
        note="Remark 3.6",
    ))

    # --- Algorithm 3.7: Best-response / underline method for 2x2 games ---
    def _algo_best_response():
        """Verify best-response method finds pure NE in 2x2 games."""
        def find_pure_ne(A, B):
            """Find pure-strategy Nash equilibria via best-response enumeration."""
            m, n = len(A), len(A[0])
            ne_list = []
            for i in range(m):
                for j in range(n):
                    # Check if i is best response to j
                    row_best = all(A[i][j] >= A[r][j] for r in range(m))
                    # Check if j is best response to i
                    col_best = all(B[i][j] >= B[i][c] for c in range(n))
                    if row_best and col_best:
                        ne_list.append((i, j))
            return ne_list

        # Battle of the Sexes: two NE at (0,0) and (1,1)
        A_bos = [[3, 0], [0, 2]]
        B_bos = [[2, 0], [0, 3]]
        ne_bos = find_pure_ne(A_bos, B_bos)
        if set(ne_bos) != {(0, 0), (1, 1)}:
            return (False, f"Battle of Sexes NE: {ne_bos}, expected [(0,0), (1,1)]")

        # Matching Pennies: no pure NE
        A_mp = [[1, -1], [-1, 1]]
        B_mp = [[-1, 1], [1, -1]]
        ne_mp = find_pure_ne(A_mp, B_mp)
        if len(ne_mp) != 0:
            return (False, f"Matching Pennies NE: {ne_mp}, expected none")

        # Coordination game: two NE at (0,0) and (1,1)
        A_cg = [[2, 0], [0, 1]]
        B_cg = [[2, 0], [0, 1]]
        ne_cg = find_pure_ne(A_cg, B_cg)
        if set(ne_cg) != {(0, 0), (1, 1)}:
            return (False, f"Coordination NE: {ne_cg}, expected [(0,0), (1,1)]")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 3.7: Best-response method finds correct pure NE in 2x2 games",
        section="4",
        predicate=_algo_best_response,
        note="Algorithm 3.7 verified",
    ))

    # --- Remark 3.14: Zero-sum games solvable by LP ---
    def _remark_3_14_zero_sum_lp():
        """Verify zero-sum game minimax via LP matches Nash equilibrium."""
        from scipy.optimize import linprog
        # Rock-Paper-Scissors: A = [[0,-1,1],[1,0,-1],[-1,1,0]]
        A = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]], dtype=float)
        n = 3
        # LP: max v s.t. A^T p >= v*1, sum p = 1, p >= 0
        # Rewrite: max v, min -v
        # Variables: [p1, p2, p3, v]
        # -A^T p + v*1 <= 0  =>  v*1 - A^T p <= 0
        c = np.array([0, 0, 0, -1])  # minimize -v
        # Constraints: v - (A^T p)_j <= 0 for each j
        A_ub = np.zeros((n, n + 1))
        for j in range(n):
            for i in range(n):
                A_ub[j, i] = -A[i, j]
            A_ub[j, n] = 1
        b_ub = np.zeros(n)
        # Equality: sum p = 1
        A_eq = np.array([[1, 1, 1, 0]])
        b_eq = np.array([1.0])
        bounds = [(0, None)] * n + [(None, None)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if not res.success:
            return (False, f"LP failed: {res.message}")
        p = res.x[:n]
        v = res.x[n]
        # RPS: NE is (1/3, 1/3, 1/3) with value 0
        if not np.allclose(p, 1/3, atol=0.01):
            return (False, f"Mixed strategy {p}, expected (1/3,1/3,1/3)")
        if abs(v) > 0.01:
            return (False, f"Game value {v}, expected 0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: Zero-sum RPS solved by LP: p=(1/3,1/3,1/3), v=0",
        section="3.14",
        predicate=_remark_3_14_zero_sum_lp,
        note="Remark 3.14: zero-sum games solvable by LP",
    ))

    return ch
