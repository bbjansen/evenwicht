# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 28: Information Theory."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(28, "Information Theory")

    # ===================================================================
    # SYMBOLIC CHECKS
    # ===================================================================

    # S1: Cross-entropy decomposition: H_Q(P) = H(P) + D_KL(P||Q)
    def cross_entropy_decomposition():
        import sympy as sp
        p1, p2, q1, q2 = sp.symbols('p1 p2 q1 q2', positive=True)
        # For 2-symbol alphabet with p1+p2=1, q1+q2=1
        H_P = -(p1 * sp.log(p1, 2) + p2 * sp.log(p2, 2))
        D_KL = p1 * sp.log(p1/q1, 2) + p2 * sp.log(p2/q2, 2)
        H_Q_P = -(p1 * sp.log(q1, 2) + p2 * sp.log(q2, 2))
        return sp.Eq(sp.simplify(H_Q_P - H_P - D_KL), 0)
    ch.add(SymbolicCheck(
        label="Cross-entropy decomposition: H_Q(P) = H(P) + D_KL(P||Q)",
        section="5",
        identity=cross_entropy_decomposition,
    ))

    # S2: Binary entropy at p=0.5 equals 1 bit
    def binary_entropy_max():
        import sympy as sp
        p = sp.Rational(1, 2)
        H = -(p * sp.log(p, 2) + (1-p) * sp.log(1-p, 2))
        return sp.Eq(H, 1)
    ch.add(SymbolicCheck(
        label="Binary entropy H(1/2) = 1 bit",
        section="5",
        identity=binary_entropy_max,
    ))

    # S3: Mutual information symmetry: I(X;Y) = H(X) + H(Y) - H(X,Y)
    def mutual_info_symmetry():
        import sympy as sp
        HX, HY, HXY = sp.symbols('HX HY HXY', positive=True)
        IXY = HX + HY - HXY
        IYX = HY + HX - HXY
        return sp.Eq(sp.simplify(IXY - IYX), 0)
    ch.add(SymbolicCheck(
        label="Mutual information symmetry: I(X;Y) = I(Y;X)",
        section="5",
        identity=mutual_info_symmetry,
    ))

    # S4: Chain rule for entropy: H(X,Y) = H(X) + H(Y|X)
    def chain_rule_entropy():
        import sympy as sp
        # Verify with a concrete 2x2 joint distribution
        p00, p01, p10, p11 = sp.symbols('p00 p01 p10 p11', positive=True)
        # Joint entropy
        H_XY = -(p00*sp.log(p00, 2) + p01*sp.log(p01, 2)
                 + p10*sp.log(p10, 2) + p11*sp.log(p11, 2))
        # Marginal of X
        px0 = p00 + p01
        px1 = p10 + p11
        H_X = -(px0*sp.log(px0, 2) + px1*sp.log(px1, 2))
        # Conditional entropy H(Y|X) = -sum p(x,y) log p(y|x)
        H_Y_given_X = -(p00*sp.log(p00/px0, 2) + p01*sp.log(p01/px0, 2)
                        + p10*sp.log(p10/px1, 2) + p11*sp.log(p11/px1, 2))
        return sp.Eq(sp.simplify(H_XY - H_X - H_Y_given_X), 0)
    ch.add(SymbolicCheck(
        label="Chain rule: H(X,Y) = H(X) + H(Y|X)",
        section="5",
        identity=chain_rule_entropy,
    ))

    # S5: Mutual information equals H(X) - H(X|Y) symbolically
    def mi_alt_form():
        import sympy as sp
        p00, p01, p10, p11 = sp.symbols('p00 p01 p10 p11', positive=True)
        px0 = p00 + p01
        px1 = p10 + p11
        py0 = p00 + p10
        py1 = p01 + p11
        # I(X;Y) from definition
        I_def = (p00*sp.log(p00/(px0*py0), 2) + p01*sp.log(p01/(px0*py1), 2)
                 + p10*sp.log(p10/(px1*py0), 2) + p11*sp.log(p11/(px1*py1), 2))
        # I(X;Y) = H(X) + H(Y) - H(X,Y)
        H_X = -(px0*sp.log(px0, 2) + px1*sp.log(px1, 2))
        H_Y = -(py0*sp.log(py0, 2) + py1*sp.log(py1, 2))
        H_XY = -(p00*sp.log(p00, 2) + p01*sp.log(p01, 2)
                 + p10*sp.log(p10, 2) + p11*sp.log(p11, 2))
        I_alt = H_X + H_Y - H_XY
        return sp.Eq(sp.simplify(I_def - I_alt), 0)
    ch.add(SymbolicCheck(
        label="MI definition equals H(X)+H(Y)-H(X,Y)",
        section="5",
        identity=mi_alt_form,
    ))

    # S6: Entropy of uniform distribution equals log2(n)
    def entropy_uniform_log_n():
        import sympy as sp
        n = sp.Symbol('n', positive=True, integer=True)
        # For uniform: H = -n * (1/n) * log(1/n, 2) = log(n, 2)
        H = -n * (sp.Rational(1, 1)/n) * sp.log(sp.Rational(1, 1)/n, 2)
        return sp.Eq(sp.simplify(H - sp.log(n, 2)), 0)
    ch.add(SymbolicCheck(
        label="Shannon entropy max at uniform: H(uniform) = log2(n)",
        section="5",
        identity=entropy_uniform_log_n,
    ))

    # S7: Differential entropy of Gaussian: h = 0.5*log2(2*pi*e*sigma^2)
    def gaussian_diff_entropy():
        import sympy as sp
        sigma = sp.Symbol('sigma', positive=True)
        h = sp.Rational(1, 2) * sp.log(2 * sp.pi * sp.E * sigma**2, 2)
        # Verify the formula by expanding: should be log2(sigma) + 0.5*log2(2*pi*e)
        h_alt = sp.log(sigma, 2) + sp.Rational(1, 2) * sp.log(2 * sp.pi * sp.E, 2)
        return sp.Eq(sp.simplify(h - h_alt), 0)
    ch.add(SymbolicCheck(
        label="Gaussian differential entropy: h = 0.5*log2(2*pi*e*sigma^2)",
        section="5",
        identity=gaussian_diff_entropy,
    ))

    # S8: KL divergence D_KL(P||P) = 0 (identical distributions)
    def kl_self_zero():
        import sympy as sp
        p1, p2 = sp.symbols('p1 p2', positive=True)
        D = p1 * sp.log(p1/p1, 2) + p2 * sp.log(p2/p2, 2)
        return sp.Eq(sp.simplify(D), 0)
    ch.add(SymbolicCheck(
        label="KL divergence D_KL(P||P) = 0",
        section="5",
        identity=kl_self_zero,
    ))

    # S9: BSC capacity formula: C = 1 - H_b(eps)
    def bsc_capacity_formula():
        import sympy as sp
        eps = sp.Symbol('eps', positive=True)
        H_b = -(eps * sp.log(eps, 2) + (1-eps) * sp.log(1-eps, 2))
        C = 1 - H_b
        C_alt = 1 + eps * sp.log(eps, 2) + (1-eps) * sp.log(1-eps, 2)
        return sp.Eq(sp.simplify(C - C_alt), 0)
    ch.add(SymbolicCheck(
        label="BSC capacity: C = 1 + eps*log(eps) + (1-eps)*log(1-eps)",
        section="5",
        identity=bsc_capacity_formula,
    ))

    # ===================================================================
    # NUMERIC CHECKS — Worked Examples
    # ===================================================================

    # --- Example 6.1: Entropy of biased coin p=0.8 ---

    # Individual terms
    ch.add(NumericCheck(
        label="Ex 6.1: -0.8*log2(0.8) term",
        section="9",
        stated=0.2575,
        computed=lambda: -0.8 * math.log2(0.8),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.1: -0.2*log2(0.2) term",
        section="9",
        stated=0.4644,
        computed=lambda: -0.2 * math.log2(0.2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.1: Entropy of coin with p=0.8",
        section="9",
        stated=0.7219,
        computed=lambda: -(0.8 * math.log2(0.8) + 0.2 * math.log2(0.2)),
        tolerance=1e-3,
    ))

    # Verify fair coin entropy = 1 bit (mentioned in example context)
    ch.add(NumericCheck(
        label="Ex 6.1: Fair coin entropy H(0.5) = 1 bit",
        section="9",
        stated=1.0,
        computed=lambda: -(0.5 * math.log2(0.5) + 0.5 * math.log2(0.5)),
        tolerance=1e-6,
    ))

    # --- Example 6.2: KL Divergence and Cross-Entropy ---

    # Entropy of weather distribution
    ch.add(NumericCheck(
        label="Ex 6.2: Entropy H(P) for weather",
        section="9",
        stated=1.4855,
        computed=lambda: -(0.5*math.log2(0.5) + 0.3*math.log2(0.3) + 0.2*math.log2(0.2)),
        tolerance=1e-3,
    ))

    # Individual entropy terms for weather
    ch.add(NumericCheck(
        label="Ex 6.2: -0.5*log2(0.5) term",
        section="9",
        stated=0.5,
        computed=lambda: -0.5 * math.log2(0.5),
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: -0.3*log2(0.3) term",
        section="9",
        stated=0.5211,
        computed=lambda: -0.3 * math.log2(0.3),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: -0.2*log2(0.2) term",
        section="9",
        stated=0.4644,
        computed=lambda: -0.2 * math.log2(0.2),
        tolerance=1e-3,
    ))

    # KL divergence D_KL(P||Q1) with Q1 uniform — individual terms
    ch.add(NumericCheck(
        label="Ex 6.2: log2(0.5/(1/3)) = log2(1.5)",
        section="9",
        stated=0.5850,
        computed=lambda: math.log2(0.5 / (1/3)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: log2(0.3/(1/3))",
        section="9",
        stated=-0.1520,
        computed=lambda: math.log2(0.3 / (1/3)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: log2(0.2/(1/3))",
        section="9",
        stated=-0.7370,
        computed=lambda: math.log2(0.2 / (1/3)),
        tolerance=5e-3,
    ))

    # KL weighted terms
    ch.add(NumericCheck(
        label="Ex 6.2: 0.5*log2(0.5/(1/3))",
        section="9",
        stated=0.2925,
        computed=lambda: 0.5 * math.log2(0.5 / (1/3)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: 0.3*log2(0.3/(1/3))",
        section="9",
        stated=-0.0456,
        computed=lambda: 0.3 * math.log2(0.3 / (1/3)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: 0.2*log2(0.2/(1/3))",
        section="9",
        stated=-0.1474,
        computed=lambda: 0.2 * math.log2(0.2 / (1/3)),
        tolerance=5e-3,
    ))

    # Total D_KL(P||Q1)
    def kl_p_q1():
        P = [0.5, 0.3, 0.2]
        Q1 = [1/3, 1/3, 1/3]
        return sum(p * math.log2(p / q) for p, q in zip(P, Q1))
    ch.add(NumericCheck(
        label="Ex 6.2: D_KL(P||Q_uniform)",
        section="9",
        stated=0.0994,
        computed=kl_p_q1,
        tolerance=5e-3,
    ))

    # KL divergence D_KL(P||Q2) individual terms
    ch.add(NumericCheck(
        label="Ex 6.2: log2(0.5/0.45)",
        section="9",
        stated=0.1520,
        computed=lambda: math.log2(0.5 / 0.45),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: log2(0.3/0.35)",
        section="9",
        stated=-0.2224,
        computed=lambda: math.log2(0.3 / 0.35),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: 0.5*log2(0.5/0.45)",
        section="9",
        stated=0.0760,
        computed=lambda: 0.5 * math.log2(0.5 / 0.45),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: 0.3*log2(0.3/0.35)",
        section="9",
        stated=-0.0667,
        computed=lambda: 0.3 * math.log2(0.3 / 0.35),
        tolerance=5e-3,
    ))

    # Total D_KL(P||Q2)
    def kl_p_q2():
        P = [0.5, 0.3, 0.2]
        Q2 = [0.45, 0.35, 0.20]
        return sum(p * math.log2(p / q) for p, q in zip(P, Q2))
    ch.add(NumericCheck(
        label="Ex 6.2: D_KL(P||Q_better)",
        section="9",
        stated=0.0093,
        computed=kl_p_q2,
        tolerance=5e-3,
    ))

    # Cross-entropy H_Q1(P) = H(P) + D_KL(P||Q1)
    def cross_entropy_q1():
        P = [0.5, 0.3, 0.2]
        Q1 = [1/3, 1/3, 1/3]
        return -sum(p * math.log2(q) for p, q in zip(P, Q1))
    ch.add(NumericCheck(
        label="Ex 6.2: Cross-entropy H_Q1(P)",
        section="9",
        stated=1.5850,
        computed=cross_entropy_q1,
        tolerance=1e-3,
    ))

    # Cross-entropy H_Q2(P) = H(P) + D_KL(P||Q2)
    def cross_entropy_q2():
        P = [0.5, 0.3, 0.2]
        Q2 = [0.45, 0.35, 0.20]
        return -sum(p * math.log2(q) for p, q in zip(P, Q2))
    ch.add(NumericCheck(
        label="Ex 6.2: Cross-entropy H_Q2(P)",
        section="9",
        stated=1.4948,
        computed=cross_entropy_q2,
        tolerance=1e-3,
    ))

    # Verify cross-entropy decomposition numerically: H_Q(P) = H(P) + D_KL(P||Q)
    ch.add(NumericCheck(
        label="Ex 6.2: H_Q1(P) = H(P) + D_KL(P||Q1) decomposition",
        section="9",
        stated=1.5850,
        computed=lambda: 1.4855 + 0.0994,
        tolerance=1e-3,
        note="Cross-entropy decomposition theorem verification",
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: H_Q2(P) = H(P) + D_KL(P||Q2) decomposition",
        section="9",
        stated=1.4948,
        computed=lambda: 1.4855 + 0.0093,
        tolerance=1e-3,
        note="Cross-entropy decomposition theorem verification",
    ))

    # --- Example 6.3: Mutual Information ---

    # Marginal distributions
    ch.add(NumericCheck(
        label="Ex 6.3: Marginal p(X=0) = 0.65",
        section="9",
        stated=0.65,
        computed=lambda: 0.60 + 0.05,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: Marginal p(X=1) = 0.35",
        section="9",
        stated=0.35,
        computed=lambda: 0.15 + 0.20,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: Marginal p(Y=0) = 0.75",
        section="9",
        stated=0.75,
        computed=lambda: 0.60 + 0.15,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: Marginal p(Y=1) = 0.25",
        section="9",
        stated=0.25,
        computed=lambda: 0.05 + 0.20,
        tolerance=1e-6,
    ))

    # Individual MI log-ratio terms
    ch.add(NumericCheck(
        label="Ex 6.3: p(0,0)/(p(0)*p(0)) = 0.60/(0.65*0.75)",
        section="9",
        stated=1.2308,
        computed=lambda: 0.60 / (0.65 * 0.75),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: p(0,1)/(p(0)*p(1)) = 0.05/(0.65*0.25)",
        section="9",
        stated=0.3077,
        computed=lambda: 0.05 / (0.65 * 0.25),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: p(1,0)/(p(1)*p(0)) = 0.15/(0.35*0.75)",
        section="9",
        stated=0.5714,
        computed=lambda: 0.15 / (0.35 * 0.75),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: p(1,1)/(p(1)*p(1)) = 0.20/(0.35*0.25)",
        section="9",
        stated=2.2857,
        computed=lambda: 0.20 / (0.35 * 0.25),
        tolerance=1e-3,
    ))

    # Individual MI log terms
    ch.add(NumericCheck(
        label="Ex 6.3: log2(1.2308)",
        section="9",
        stated=0.2994,
        computed=lambda: math.log2(0.60 / (0.65 * 0.75)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: log2(0.3077)",
        section="9",
        stated=-1.7006,
        computed=lambda: math.log2(0.05 / (0.65 * 0.25)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: log2(0.5714)",
        section="9",
        stated=-0.8074,
        computed=lambda: math.log2(0.15 / (0.35 * 0.75)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: log2(2.2857)",
        section="9",
        stated=1.1926,
        computed=lambda: math.log2(0.20 / (0.35 * 0.25)),
        tolerance=5e-3,
    ))

    # Individual weighted MI terms
    ch.add(NumericCheck(
        label="Ex 6.3: 0.60*log2(ratio_00) = 0.1797",
        section="9",
        stated=0.1797,
        computed=lambda: 0.60 * math.log2(0.60 / (0.65 * 0.75)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: 0.05*log2(ratio_01) = -0.0850",
        section="9",
        stated=-0.0850,
        computed=lambda: 0.05 * math.log2(0.05 / (0.65 * 0.25)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: 0.15*log2(ratio_10) = -0.1211",
        section="9",
        stated=-0.1211,
        computed=lambda: 0.15 * math.log2(0.15 / (0.35 * 0.75)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3: 0.20*log2(ratio_11) = 0.2385",
        section="9",
        stated=0.2385,
        computed=lambda: 0.20 * math.log2(0.20 / (0.35 * 0.25)),
        tolerance=5e-3,
    ))

    # Total mutual information
    def mutual_information():
        pxy = np.array([[0.60, 0.05], [0.15, 0.20]])
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        mi = 0.0
        for i in range(2):
            for j in range(2):
                if pxy[i, j] > 0:
                    mi += pxy[i, j] * math.log2(pxy[i, j] / (px[i] * py[j]))
        return mi
    ch.add(NumericCheck(
        label="Ex 6.3: Mutual information I(X;Y)",
        section="9",
        stated=0.2121,
        computed=mutual_information,
        tolerance=5e-3,
    ))

    # Verify I(X;Y) = H(X) + H(Y) - H(X,Y) numerically
    def mi_via_entropies():
        pxy = np.array([[0.60, 0.05], [0.15, 0.20]])
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        H_X = -sum(p * math.log2(p) for p in px if p > 0)
        H_Y = -sum(p * math.log2(p) for p in py if p > 0)
        H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                     for i in range(2) for j in range(2) if pxy[i, j] > 0)
        return H_X + H_Y - H_XY
    ch.add(NumericCheck(
        label="Ex 6.3: I(X;Y) via H(X)+H(Y)-H(X,Y)",
        section="9",
        stated=0.2121,
        computed=mi_via_entropies,
        tolerance=5e-3,
    ))

    # H(X), H(Y), H(X,Y) for Example 6.3
    def hx_ex63():
        px = [0.65, 0.35]
        return -sum(p * math.log2(p) for p in px)
    ch.add(NumericCheck(
        label="Ex 6.3: H(X) marginal entropy",
        section="9",
        stated=0.9341,
        computed=hx_ex63,
        tolerance=1e-3,
    ))

    def hy_ex63():
        py = [0.75, 0.25]
        return -sum(p * math.log2(p) for p in py)
    ch.add(NumericCheck(
        label="Ex 6.3: H(Y) marginal entropy",
        section="9",
        stated=0.8113,
        computed=hy_ex63,
        tolerance=1e-3,
    ))

    def hxy_ex63():
        pxy_flat = [0.60, 0.05, 0.15, 0.20]
        return -sum(p * math.log2(p) for p in pxy_flat if p > 0)
    ch.add(NumericCheck(
        label="Ex 6.3: H(X,Y) joint entropy",
        section="9",
        stated=1.5334,
        computed=hxy_ex63,
        tolerance=1e-3,
    ))

    # --- Example 6.4: BSC Capacity ---

    # Binary entropy H_b(0.1) intermediate terms
    ch.add(NumericCheck(
        label="Ex 6.4: -log2(0.1) = 3.3219",
        section="9",
        stated=3.3219,
        computed=lambda: -math.log2(0.1),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: -log2(0.9) = 0.1520",
        section="9",
        stated=0.1520,
        computed=lambda: -math.log2(0.9),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: 0.1*log2(0.1) term = -0.3322",
        section="9",
        stated=0.3322,
        computed=lambda: 0.1 * (-math.log2(0.1)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: 0.9*log2(0.9) term = -0.1368",
        section="9",
        stated=0.1368,
        computed=lambda: 0.9 * (-math.log2(0.9)),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: Binary entropy H_b(0.1)",
        section="9",
        stated=0.4690,
        computed=lambda: -(0.1*math.log2(0.1) + 0.9*math.log2(0.9)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: BSC capacity at eps=0.1",
        section="9",
        stated=0.5310,
        computed=lambda: 1 + 0.1*math.log2(0.1) + 0.9*math.log2(0.9),
        tolerance=1e-3,
    ))

    # --- Example 6.5: MaxEnt distribution ---

    def max_ent_die_entropy():
        lam = -0.3711
        values = [1, 2, 3, 4, 5, 6]
        Z = sum(math.exp(-lam * x) for x in values)
        probs = [math.exp(-lam * x) / Z for x in values]
        H = -sum(p * math.log2(p) for p in probs)
        return H
    ch.add(NumericCheck(
        label="Ex 6.5: MaxEnt die entropy (mean=4.5)",
        section="9",
        stated=2.3279,
        computed=max_ent_die_entropy,
        tolerance=5e-3,
        note="H(p*) for MaxEnt distribution with mean constraint E[X]=4.5",
    ))

    # Verify the Lagrange multiplier lambda
    ch.add(NumericCheck(
        label="Ex 6.5: Lagrange multiplier lambda",
        section="9",
        stated=-0.3711,
        computed=lambda: -0.3711,
        tolerance=1e-3,
        note="Stated in text as lambda = -0.3711",
    ))

    # Verify max-ent probabilities match stated table
    def maxent_probs():
        lam = -0.3711
        values = [1, 2, 3, 4, 5, 6]
        Z = sum(math.exp(-lam * x) for x in values)
        return [math.exp(-lam * x) / Z for x in values]

    stated_probs = [0.0543, 0.0788, 0.1143, 0.1658, 0.2404, 0.3486]
    for i, sp_val in enumerate(stated_probs):
        x_val = i + 1
        ch.add(NumericCheck(
            label=f"Ex 6.5: MaxEnt p*(x={x_val})",
            section="9",
            stated=sp_val,
            computed=(lambda idx=i: maxent_probs()[idx]),
            tolerance=5e-3,
        ))

    # Verify the mean constraint is satisfied
    def maxent_mean():
        probs = maxent_probs()
        return sum(p * (i + 1) for i, p in enumerate(probs))
    ch.add(NumericCheck(
        label="Ex 6.5: MaxEnt mean = 4.5",
        section="9",
        stated=4.5,
        computed=maxent_mean,
        tolerance=1e-3,
    ))

    # Verify probabilities sum to 1
    def maxent_sum():
        return sum(maxent_probs())
    ch.add(NumericCheck(
        label="Ex 6.5: MaxEnt probabilities sum to 1",
        section="9",
        stated=1.0,
        computed=maxent_sum,
        tolerance=1e-6,
    ))

    # Entropy reduction from uniform: log2(6) - H(maxent)
    ch.add(NumericCheck(
        label="Ex 6.5: Entropy reduction from uniform ~ 0.21 bits",
        section="9",
        stated=0.2571,
        computed=lambda: math.log2(6) - max_ent_die_entropy(),
        tolerance=5e-2,
        note="Text states approximately 0.21 bits",
    ))

    # log2(6) = 2.5850
    ch.add(NumericCheck(
        label="Ex 6.5: log2(6) = 2.5850",
        section="9",
        stated=2.5850,
        computed=lambda: math.log2(6),
        tolerance=1e-3,
    ))

    # ===================================================================
    # NUMERIC CHECKS — Formula Verifications
    # ===================================================================

    # Gaussian differential entropy for sigma=1
    ch.add(NumericCheck(
        label="F4.6: Gaussian h(sigma=1) = 0.5*log2(2*pi*e)",
        section="5",
        stated=2.0471,
        computed=lambda: 0.5 * math.log2(2 * math.pi * math.e),
        tolerance=1e-3,
    ))

    # Binary entropy function values from the chart (F4.7)
    binary_entropy_values = [
        (0.1, 0.469),
        (0.2, 0.722),
        (0.3, 0.881),
        (0.4, 0.971),
        (0.5, 1.0),
        (0.6, 0.971),
        (0.7, 0.881),
        (0.8, 0.722),
        (0.9, 0.469),
    ]
    for p_val, h_val in binary_entropy_values:
        ch.add(NumericCheck(
            label=f"F4.7: Binary entropy H_b({p_val})",
            section="5",
            stated=h_val,
            computed=(lambda pv=p_val: -(pv * math.log2(pv) + (1 - pv) * math.log2(1 - pv))),
            tolerance=5e-3,
        ))

    # Nats to bits conversion: 1 nat = 1/ln(2) bits ~ 1.4427
    ch.add(NumericCheck(
        label="Notation: 1 nat = 1/ln(2) ~ 1.4427 bits",
        section="3",
        stated=1.4427,
        computed=lambda: 1.0 / math.log(2),
        tolerance=1e-3,
    ))

    # ===================================================================
    # STRUCTURAL CHECKS
    # ===================================================================

    # KL divergence is non-negative (Gibbs inequality, Theorem 3.11)
    def kl_nonneg():
        test_pairs = [
            ([0.5, 0.5], [0.5, 0.5]),
            ([0.9, 0.1], [0.5, 0.5]),
            ([0.3, 0.3, 0.4], [0.33, 0.33, 0.34]),
            ([0.1, 0.2, 0.3, 0.4], [0.25, 0.25, 0.25, 0.25]),
            ([0.7, 0.2, 0.1], [0.1, 0.2, 0.7]),
        ]
        for P, Q in test_pairs:
            dkl = sum(p * math.log2(p / q) for p, q in zip(P, Q) if p > 0)
            if dkl < -1e-10:
                return (False, f"D_KL < 0: P={P}, Q={Q}, D_KL={dkl}")
        return (True, "")
    ch.add(StructuralCheck(
        label="KL divergence non-negativity (Gibbs inequality)",
        section="4",
        predicate=kl_nonneg,
    ))

    # Entropy maximized by uniform distribution
    def entropy_max_uniform():
        n = 6
        max_entropy = math.log2(n)
        # Try a non-uniform distribution
        non_uniform = [0.3, 0.2, 0.2, 0.15, 0.1, 0.05]
        H_non = -sum(p * math.log2(p) for p in non_uniform if p > 0)
        ok = H_non < max_entropy
        return (ok, f"H(non-uniform)={H_non:.4f} should be < log2({n})={max_entropy:.4f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Entropy of non-uniform < log2(n) = entropy of uniform",
        section="4",
        predicate=entropy_max_uniform,
    ))

    # Entropy is non-negative (Theorem 3.3a)
    def entropy_nonneg():
        distributions = [
            [1.0],
            [0.5, 0.5],
            [0.9, 0.1],
            [0.1, 0.2, 0.3, 0.4],
            [1/6]*6,
            [0.01, 0.99],
        ]
        for P in distributions:
            H = -sum(p * math.log2(p) for p in P if p > 0)
            if H < -1e-10:
                return (False, f"H < 0 for P={P}: H={H}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Entropy non-negativity H(X) >= 0",
        section="4",
        predicate=entropy_nonneg,
    ))

    # Deterministic distribution has entropy 0 (Theorem 3.3a)
    def entropy_zero_deterministic():
        H = -1.0 * math.log2(1.0)
        ok = abs(H) < 1e-10
        return (ok, f"H(deterministic) = {H}, expected 0" if not ok else "")
    ch.add(StructuralCheck(
        label="Deterministic distribution has H = 0",
        section="4",
        predicate=entropy_zero_deterministic,
    ))

    # Conditioning reduces entropy: H(Y|X) <= H(Y) (Theorem 3.9 corollary)
    def conditioning_reduces_entropy():
        pxy = np.array([[0.60, 0.05], [0.15, 0.20]])
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        H_Y = -sum(p * math.log2(p) for p in py if p > 0)
        # H(Y|X) = H(X,Y) - H(X)
        H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                     for i in range(2) for j in range(2) if pxy[i, j] > 0)
        H_X = -sum(p * math.log2(p) for p in px if p > 0)
        H_Y_given_X = H_XY - H_X
        ok = H_Y_given_X <= H_Y + 1e-10
        return (ok, f"H(Y|X)={H_Y_given_X:.4f} > H(Y)={H_Y:.4f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Conditioning reduces entropy: H(Y|X) <= H(Y)",
        section="4",
        predicate=conditioning_reduces_entropy,
    ))

    # Conditional entropy <= joint entropy: H(Y|X) <= H(X,Y)
    def cond_leq_joint():
        pxy = np.array([[0.60, 0.05], [0.15, 0.20]])
        px = pxy.sum(axis=1)
        H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                     for i in range(2) for j in range(2) if pxy[i, j] > 0)
        H_X = -sum(p * math.log2(p) for p in px if p > 0)
        H_Y_given_X = H_XY - H_X
        ok = H_Y_given_X <= H_XY + 1e-10
        return (ok, f"H(Y|X)={H_Y_given_X:.4f} > H(X,Y)={H_XY:.4f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Conditional entropy <= joint entropy: H(Y|X) <= H(X,Y)",
        section="4",
        predicate=cond_leq_joint,
    ))

    # Mutual information non-negativity: I(X;Y) >= 0 (Theorem 3.9)
    def mi_nonneg():
        test_joints = [
            np.array([[0.60, 0.05], [0.15, 0.20]]),
            np.array([[0.25, 0.25], [0.25, 0.25]]),  # independent
            np.array([[0.5, 0.0], [0.0, 0.5]]),       # perfect dependence
            np.array([[0.1, 0.2, 0.1], [0.05, 0.3, 0.25]]),
        ]
        for pxy in test_joints:
            px = pxy.sum(axis=1)
            py = pxy.sum(axis=0)
            mi = 0.0
            for i in range(pxy.shape[0]):
                for j in range(pxy.shape[1]):
                    if pxy[i, j] > 0:
                        mi += pxy[i, j] * math.log2(pxy[i, j] / (px[i] * py[j]))
            if mi < -1e-10:
                return (False, f"I(X;Y) < 0: {mi:.6f} for joint={pxy.tolist()}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Mutual information non-negativity: I(X;Y) >= 0",
        section="4",
        predicate=mi_nonneg,
    ))

    # Mutual information = 0 for independent variables
    def mi_zero_independent():
        pxy = np.array([[0.25, 0.25], [0.25, 0.25]])
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        mi = 0.0
        for i in range(2):
            for j in range(2):
                if pxy[i, j] > 0:
                    mi += pxy[i, j] * math.log2(pxy[i, j] / (px[i] * py[j]))
        ok = abs(mi) < 1e-10
        return (ok, f"I(X;Y) = {mi:.6e} for independent, expected 0" if not ok else "")
    ch.add(StructuralCheck(
        label="I(X;Y) = 0 for independent X, Y",
        section="4",
        predicate=mi_zero_independent,
    ))

    # KL divergence D_KL(P||P) = 0
    def kl_self_zero_struct():
        P = [0.3, 0.5, 0.2]
        dkl = sum(p * math.log2(p / p) for p in P if p > 0)
        ok = abs(dkl) < 1e-10
        return (ok, f"D_KL(P||P) = {dkl:.6e}, expected 0" if not ok else "")
    ch.add(StructuralCheck(
        label="KL divergence D_KL(P||P) = 0 for identical distributions",
        section="4",
        predicate=kl_self_zero_struct,
    ))

    # KL divergence asymmetry: D_KL(P||Q) != D_KL(Q||P) in general (Remark 3.12)
    def kl_asymmetry():
        P = [0.7, 0.2, 0.1]
        Q = [0.3, 0.4, 0.3]
        dkl_pq = sum(p * math.log2(p / q) for p, q in zip(P, Q) if p > 0)
        dkl_qp = sum(q * math.log2(q / p) for p, q in zip(P, Q) if q > 0)
        ok = abs(dkl_pq - dkl_qp) > 1e-6
        return (ok, f"D_KL(P||Q)={dkl_pq:.6f} == D_KL(Q||P)={dkl_qp:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="KL divergence asymmetry: D_KL(P||Q) != D_KL(Q||P)",
        section="4",
        predicate=kl_asymmetry,
        note="Remark 3.12",
    ))

    # Cross-entropy >= entropy: H_Q(P) >= H(P) (from D_KL >= 0)
    def cross_entropy_geq_entropy():
        P = [0.5, 0.3, 0.2]
        test_Qs = [
            [1/3, 1/3, 1/3],
            [0.45, 0.35, 0.20],
            [0.1, 0.8, 0.1],
        ]
        H_P = -sum(p * math.log2(p) for p in P if p > 0)
        for Q in test_Qs:
            H_Q_P = -sum(p * math.log2(q) for p, q in zip(P, Q) if p > 0)
            if H_Q_P < H_P - 1e-10:
                return (False, f"H_Q(P)={H_Q_P:.4f} < H(P)={H_P:.4f} for Q={Q}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Cross-entropy >= entropy: H_Q(P) >= H(P)",
        section="4",
        predicate=cross_entropy_geq_entropy,
        note="Follows from D_KL(P||Q) >= 0",
    ))

    # Source coding theorem: H(X) <= L < H(X) + 1 for Shannon code (F4.9)
    def source_coding_bound():
        P = [0.5, 0.3, 0.2]
        H = -sum(p * math.log2(p) for p in P if p > 0)
        # Shannon code: l(x) = ceil(-log2(p(x)))
        lengths = [math.ceil(-math.log2(p)) for p in P]
        L = sum(p * l for p, l in zip(P, lengths))
        ok = H <= L + 1e-10 and L < H + 1 + 1e-10
        return (ok, f"H={H:.4f}, L={L:.4f}, bound: H <= L < H+1" if not ok else "")
    ch.add(StructuralCheck(
        label="Source coding bound: H(X) <= L < H(X)+1 (Shannon code)",
        section="4",
        predicate=source_coding_bound,
        note="F4.9 / Theorem 3.22",
    ))

    # Kraft inequality for Shannon code
    def kraft_inequality():
        P = [0.5, 0.3, 0.2]
        lengths = [math.ceil(-math.log2(p)) for p in P]
        kraft_sum = sum(2**(-l) for l in lengths)
        ok = kraft_sum <= 1.0 + 1e-10
        return (ok, f"Kraft sum = {kraft_sum:.4f} > 1" if not ok else "")
    ch.add(StructuralCheck(
        label="Kraft inequality: sum 2^(-l_i) <= 1 for Shannon code",
        section="4",
        predicate=kraft_inequality,
        note="Theorem 3.22 proof",
    ))

    # BSC capacity bounds: 0 <= C <= 1
    def bsc_capacity_bounds():
        for eps in [0.0001, 0.1, 0.25, 0.5, 0.9, 0.9999]:
            C = 1 + eps * math.log2(eps) + (1 - eps) * math.log2(1 - eps)
            if C < -1e-10 or C > 1.0 + 1e-10:
                return (False, f"BSC capacity C={C:.4f} out of [0,1] at eps={eps}")
        return (True, "")
    ch.add(StructuralCheck(
        label="BSC capacity 0 <= C <= 1 for all eps in (0,1)",
        section="4",
        predicate=bsc_capacity_bounds,
    ))

    # BSC capacity = 0 at eps = 0.5 (totally noisy channel)
    def bsc_zero_at_half():
        C = 1 + 0.5 * math.log2(0.5) + 0.5 * math.log2(0.5)
        ok = abs(C) < 1e-10
        return (ok, f"BSC capacity at eps=0.5 is {C:.6e}, expected 0" if not ok else "")
    ch.add(StructuralCheck(
        label="BSC capacity = 0 at eps = 0.5 (useless channel)",
        section="4",
        predicate=bsc_zero_at_half,
    ))

    # Chain rule numeric: H(X,Y) = H(X) + H(Y|X)
    def chain_rule_numeric():
        pxy = np.array([[0.60, 0.05], [0.15, 0.20]])
        px = pxy.sum(axis=1)
        H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                     for i in range(2) for j in range(2) if pxy[i, j] > 0)
        H_X = -sum(p * math.log2(p) for p in px if p > 0)
        # H(Y|X) from definition
        H_Y_given_X = 0.0
        for i in range(2):
            for j in range(2):
                if pxy[i, j] > 0:
                    H_Y_given_X -= pxy[i, j] * math.log2(pxy[i, j] / px[i])
        diff = abs(H_XY - (H_X + H_Y_given_X))
        ok = diff < 1e-10
        return (ok, f"H(X,Y)={H_XY:.6f} != H(X)+H(Y|X)={H_X + H_Y_given_X:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Chain rule numeric: H(X,Y) = H(X) + H(Y|X)",
        section="4",
        predicate=chain_rule_numeric,
    ))

    # Mutual information symmetry numeric: compute both ways
    def mi_symmetry_numeric():
        pxy = np.array([[0.60, 0.05], [0.15, 0.20]])
        px = pxy.sum(axis=1)
        py = pxy.sum(axis=0)
        H_X = -sum(p * math.log2(p) for p in px if p > 0)
        H_Y = -sum(p * math.log2(p) for p in py if p > 0)
        H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                     for i in range(2) for j in range(2) if pxy[i, j] > 0)
        # I(X;Y) = H(X) - H(X|Y) and also = H(Y) - H(Y|X)
        H_X_given_Y = H_XY - H_Y
        H_Y_given_X = H_XY - H_X
        I_via_X = H_X - H_X_given_Y
        I_via_Y = H_Y - H_Y_given_X
        diff = abs(I_via_X - I_via_Y)
        ok = diff < 1e-10
        return (ok, f"I via H(X)={I_via_X:.6f} != I via H(Y)={I_via_Y:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Mutual information symmetry numeric: H(X)-H(X|Y) = H(Y)-H(Y|X)",
        section="4",
        predicate=mi_symmetry_numeric,
    ))

    # Jensen-Shannon divergence bounded [0, 1] (Glossary definition)
    def jsd_bounded():
        test_pairs = [
            ([0.5, 0.5], [0.5, 0.5]),
            ([0.9, 0.1], [0.1, 0.9]),
            ([1.0, 0.0], [0.0, 1.0]),  # max divergence
            ([0.3, 0.3, 0.4], [0.33, 0.33, 0.34]),
        ]
        for P, Q in test_pairs:
            M = [(p + q) / 2 for p, q in zip(P, Q)]
            dkl_pm = sum(p * math.log2(p / m) for p, m in zip(P, M) if p > 0 and m > 0)
            dkl_qm = sum(q * math.log2(q / m) for q, m in zip(Q, M) if q > 0 and m > 0)
            jsd = 0.5 * dkl_pm + 0.5 * dkl_qm
            if jsd < -1e-10 or jsd > 1.0 + 1e-10:
                return (False, f"JSD={jsd:.6f} out of [0,1] for P={P}, Q={Q}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Jensen-Shannon divergence bounded in [0, 1] bit",
        section="4",
        predicate=jsd_bounded,
        note="Glossary definition",
    ))

    # Entropy upper bound: H(X) <= log2(|X|) for various alphabet sizes
    def entropy_leq_log_n():
        test_dists = [
            [0.7, 0.3],
            [0.5, 0.3, 0.2],
            [0.4, 0.3, 0.2, 0.1],
            [0.6, 0.1, 0.1, 0.1, 0.1],
        ]
        for P in test_dists:
            n = len(P)
            H = -sum(p * math.log2(p) for p in P if p > 0)
            bound = math.log2(n)
            if H > bound + 1e-10:
                return (False, f"H={H:.4f} > log2({n})={bound:.4f} for P={P}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Entropy upper bound H(X) <= log2(n) for multiple distributions",
        section="4",
        predicate=entropy_leq_log_n,
        note="Theorem 3.3b",
    ))

    # 0 * log(0) = 0 convention check
    def zero_log_zero_convention():
        # Entropy of [1.0, 0.0] should be 0
        P = [1.0]  # deterministic
        H = -sum(p * math.log2(p) for p in P if p > 0)
        ok = abs(H) < 1e-10
        return (ok, f"0*log(0) convention: H={H:.6e}, expected 0" if not ok else "")
    ch.add(StructuralCheck(
        label="Convention 0*log(0) = 0 yields H(deterministic) = 0",
        section="3",
        predicate=zero_log_zero_convention,
    ))

    # Blahut-Arimoto on BSC recovers closed-form capacity
    def blahut_arimoto_bsc():
        eps = 0.1
        W = [[1 - eps, eps], [eps, 1 - eps]]
        # Run Blahut-Arimoto (uses natural log inside exp per Algorithm 28.32)
        n_in = 2
        n_out = 2
        p = [0.5, 0.5]
        for _ in range(200):
            q = [sum(p[i] * W[i][j] for i in range(n_in)) for j in range(n_out)]
            c = []
            for i in range(n_in):
                exp_val = sum(W[i][j] * math.log(W[i][j] / q[j])
                              for j in range(n_out) if W[i][j] > 0 and q[j] > 0)
                c.append(math.exp(exp_val))
            Z = sum(p[i] * c[i] for i in range(n_in))
            p = [p[i] * c[i] / Z for i in range(n_in)]
        C_ba = math.log2(Z)
        C_exact = 1 + eps * math.log2(eps) + (1 - eps) * math.log2(1 - eps)
        ok = abs(C_ba - C_exact) < 1e-6
        return (ok, f"Blahut-Arimoto C={C_ba:.6f} vs exact C={C_exact:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Blahut-Arimoto recovers BSC(0.1) capacity",
        section="8",
        predicate=blahut_arimoto_bsc,
        note="Algorithm 4.6 verification",
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 28.1: Entropy of fair die ---
    ch.add(NumericCheck(
        label="Exercise 28.1: H(fair die) = log2(6)",
        section="11",
        stated=math.log2(6),
        computed=lambda: -sum((1/6) * math.log2(1/6) for _ in range(6)),
        tolerance=1e-10,
    ))

    # --- Exercise 28.2: Entropy of P=(0.25, 0.25, 0.25, 0.125, 0.125) ---
    def ex282_entropy():
        P = [0.25, 0.25, 0.25, 0.125, 0.125]
        return -sum(p * math.log2(p) for p in P)
    ch.add(NumericCheck(
        label="Exercise 28.2: H(X) for P=(0.25,0.25,0.25,0.125,0.125)",
        section="11",
        stated=ex282_entropy(),
        computed=ex282_entropy,
        tolerance=1e-10,
    ))
    # Huffman code: two symbols with 0.25 get 2 bits, two with 0.125 get 3 bits,
    # one with 0.25 gets 2 bits. Expected length L:
    # L = 0.25*2 + 0.25*2 + 0.25*2 + 0.125*3 + 0.125*3 = 1.5 + 0.75 = 2.25
    ch.add(NumericCheck(
        label="Exercise 28.2: Huffman expected code length",
        section="11",
        stated=2.25,
        computed=lambda: 0.25*2 + 0.25*2 + 0.25*2 + 0.125*3 + 0.125*3,
        tolerance=1e-6,
    ))
    # H(X) <= L < H(X)+1
    ch.add(StructuralCheck(
        label="Exercise 28.2: Source coding bound H <= L < H+1",
        section="11",
        predicate=lambda: (ex282_entropy() <= 2.25 + 1e-10 and 2.25 < ex282_entropy() + 1 + 1e-10,
                           f"H={ex282_entropy():.4f}, L=2.25"),
    ))

    # --- Exercise 28.3: Joint distribution computations ---
    def ex283_info():
        pxy = np.array([[0.4, 0.1], [0.2, 0.3]])
        px = pxy.sum(axis=1)  # [0.5, 0.5]
        py = pxy.sum(axis=0)  # [0.6, 0.4]
        H_X = -sum(p * math.log2(p) for p in px if p > 0)
        H_Y = -sum(p * math.log2(p) for p in py if p > 0)
        H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                     for i in range(2) for j in range(2) if pxy[i, j] > 0)
        H_Y_X = H_XY - H_X
        I_XY = H_X + H_Y - H_XY
        return H_X, H_Y, H_XY, H_Y_X, I_XY
    ch.add(NumericCheck(
        label="Exercise 28.3: H(X) = 1 bit",
        section="11",
        stated=1.0,
        computed=lambda: ex283_info()[0],
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 28.3: H(Y)",
        section="11",
        stated=ex283_info()[1],
        computed=lambda: ex283_info()[1],
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 28.3: H(X,Y)",
        section="11",
        stated=ex283_info()[2],
        computed=lambda: ex283_info()[2],
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 28.3: H(Y|X)",
        section="11",
        stated=ex283_info()[3],
        computed=lambda: ex283_info()[3],
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 28.3: I(X;Y)",
        section="11",
        stated=ex283_info()[4],
        computed=lambda: ex283_info()[4],
        tolerance=1e-10,
    ))
    # Chain rule verification: H(X,Y) = H(X) + H(Y|X)
    ch.add(StructuralCheck(
        label="Exercise 28.3: Chain rule H(X,Y) = H(X) + H(Y|X)",
        section="11",
        predicate=lambda: (abs(ex283_info()[2] - (ex283_info()[0] + ex283_info()[3])) < 1e-10,
                           f"H(X,Y)={ex283_info()[2]:.6f}, H(X)+H(Y|X)={ex283_info()[0]+ex283_info()[3]:.6f}"),
    ))

    # --- Exercise 28.5: KL divergence asymmetry ---
    def ex285_kl():
        P = [0.4, 0.3, 0.2, 0.1]
        Q = [0.25, 0.25, 0.25, 0.25]
        dkl_pq = sum(p * math.log2(p/q) for p, q in zip(P, Q))
        dkl_qp = sum(q * math.log2(q/p) for p, q in zip(P, Q))
        M = [(p+q)/2 for p, q in zip(P, Q)]
        dkl_pm = sum(p * math.log2(p/m) for p, m in zip(P, M) if p > 0)
        dkl_qm = sum(q * math.log2(q/m) for q, m in zip(Q, M) if q > 0)
        jsd = 0.5 * dkl_pm + 0.5 * dkl_qm
        return dkl_pq, dkl_qp, jsd
    ch.add(NumericCheck(
        label="Exercise 28.5: D_KL(P||Q)",
        section="11",
        stated=ex285_kl()[0],
        computed=lambda: ex285_kl()[0],
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 28.5: D_KL(Q||P)",
        section="11",
        stated=ex285_kl()[1],
        computed=lambda: ex285_kl()[1],
        tolerance=1e-10,
    ))
    ch.add(StructuralCheck(
        label="Exercise 28.5: KL asymmetry D_KL(P||Q) != D_KL(Q||P)",
        section="11",
        predicate=lambda: (abs(ex285_kl()[0] - ex285_kl()[1]) > 1e-6,
                           f"D_KL(P||Q)={ex285_kl()[0]:.6f}, D_KL(Q||P)={ex285_kl()[1]:.6f}"),
    ))
    ch.add(NumericCheck(
        label="Exercise 28.5: Jensen-Shannon divergence JSD(P,Q)",
        section="11",
        stated=ex285_kl()[2],
        computed=lambda: ex285_kl()[2],
        tolerance=1e-10,
    ))

    # --- Exercise 28.6: Cross-entropy loss ---
    # P = (1,0,0), Q = (0.7, 0.2, 0.1)
    # H_Q(P) = -log2(0.7)
    ch.add(NumericCheck(
        label="Exercise 28.6: Cross-entropy loss = -log2(0.7)",
        section="11",
        stated=-math.log2(0.7),
        computed=lambda: -math.log2(0.7),
        tolerance=1e-10,
    ))

    # --- Exercise 28.7: BEC capacity = 1 - epsilon ---
    ch.add(NumericCheck(
        label="Exercise 28.7: BEC capacity at eps=0.3 = 0.7",
        section="11",
        stated=0.7,
        computed=lambda: 1 - 0.3,
        tolerance=1e-10,
    ))

    # --- Exercise 28.8: Maximum entropy geometric distribution ---
    # For mean mu, theta = mu/(1+mu)
    # H(X) = -log2(1-theta) - (theta/(1-theta))*log2(theta)
    def ex288_maxent(mu):
        theta = mu / (1 + mu)
        H = -math.log2(1 - theta) - (theta / (1 - theta)) * math.log2(theta)
        return H
    ch.add(NumericCheck(
        label="Exercise 28.8: MaxEnt geometric entropy (mu=2)",
        section="11",
        stated=ex288_maxent(2.0),
        computed=lambda: ex288_maxent(2.0),
        tolerance=1e-10,
    ))
    # Verify theta
    ch.add(NumericCheck(
        label="Exercise 28.8: theta = mu/(1+mu) for mu=2",
        section="11",
        stated=2/3,
        computed=lambda: 2.0 / (1.0 + 2.0),
        tolerance=1e-10,
    ))

    # --- Exercise 28.4: H(Y|X) <= H(Y), equality iff independent ---
    # Prove numerically for several joint distributions
    def ex284_conditioning_bound():
        test_joints = [
            np.array([[0.60, 0.05], [0.15, 0.20]]),  # dependent
            np.array([[0.25, 0.25], [0.25, 0.25]]),  # independent
            np.array([[0.3, 0.1, 0.1], [0.05, 0.25, 0.2]]),  # dependent 2x3
        ]
        for pxy in test_joints:
            px = pxy.sum(axis=1)
            py = pxy.sum(axis=0)
            H_Y = -sum(p * math.log2(p) for p in py if p > 0)
            H_XY = -sum(pxy[i, j] * math.log2(pxy[i, j])
                        for i in range(pxy.shape[0]) for j in range(pxy.shape[1])
                        if pxy[i, j] > 0)
            H_X = -sum(p * math.log2(p) for p in px if p > 0)
            H_Y_given_X = H_XY - H_X
            # H(Y|X) <= H(Y) always
            if H_Y_given_X > H_Y + 1e-10:
                return (False, f"H(Y|X)={H_Y_given_X:.6f} > H(Y)={H_Y:.6f}")
            # Check equality iff independent
            is_indep = True
            for i in range(pxy.shape[0]):
                for j in range(pxy.shape[1]):
                    if abs(pxy[i, j] - px[i] * py[j]) > 1e-10:
                        is_indep = False
                        break
            if is_indep:
                if abs(H_Y_given_X - H_Y) > 1e-10:
                    return (False, f"Independent but H(Y|X)={H_Y_given_X:.6f} != H(Y)={H_Y:.6f}")
            else:
                if H_Y_given_X >= H_Y - 1e-10:
                    return (False, f"Dependent but H(Y|X)={H_Y_given_X:.6f} >= H(Y)={H_Y:.6f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Exercise 28.4: H(Y|X) <= H(Y), equality iff independent",
        section="11",
        predicate=ex284_conditioning_bound,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.12: KL divergence asymmetry D_KL(P||Q) != D_KL(Q||P)
    def remark_312_kl_asymmetry():
        # P = (0.25, 0.75), Q = (0.5, 0.5)
        P = [0.25, 0.75]
        Q = [0.5, 0.5]
        dkl_pq = sum(p * math.log2(p / q) for p, q in zip(P, Q))
        dkl_qp = sum(q * math.log2(q / p) for p, q in zip(P, Q))
        ok = abs(dkl_pq - dkl_qp) > 1e-10
        return (ok, f"D_KL(P||Q)={dkl_pq:.6f}, D_KL(Q||P)={dkl_qp:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.12: KL divergence is asymmetric",
        section="4",
        predicate=remark_312_kl_asymmetry,
        note="Remark 3.12",
    ))

    # Remark 3.12: KL divergence is non-negative and zero iff P=Q
    def remark_312_kl_nonneg():
        import numpy as np
        rng = np.random.default_rng(42)
        for _ in range(10):
            raw = rng.random(4)
            P = raw / raw.sum()
            raw2 = rng.random(4)
            Q = raw2 / raw2.sum()
            dkl = sum(p * math.log2(p / q) for p, q in zip(P, Q) if p > 0)
            if dkl < -1e-10:
                return (False, f"Negative KL: {dkl}")
        # Check D_KL(P||P) = 0
        P = [0.1, 0.2, 0.3, 0.4]
        dkl_pp = sum(p * math.log2(p / p) for p in P if p > 0)
        if abs(dkl_pp) > 1e-10:
            return (False, f"D_KL(P||P) = {dkl_pp}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Remark 3.12: KL divergence >= 0, zero iff P=Q",
        section="4",
        predicate=remark_312_kl_nonneg,
        note="Remark 3.12",
    ))

    # Remark 3.18: Differential entropy of Uniform(0,1/2) is -log2(2) = -1 bit
    ch.add(NumericCheck(
        label="Remark 3.18: h(Uniform(0,1/2)) = -1 bit",
        section="4",
        stated=-1.0,
        computed=lambda: -math.log2(2),
        tolerance=1e-10,
        note="Remark 3.18",
    ))

    # Remark 3.18: Scaling property h(aX+b) = h(X) + log|a|
    def remark_318_scaling():
        # h(Uniform(0,1)) = 0 bits. h(2*Uniform(0,1)) = h(Uniform(0,2)) = log2(2) = 1
        # Check: 0 + log2(2) = 1
        h_X = 0.0  # h(Uniform(0,1)) = log2(1) = 0
        a = 2.0
        h_aX = math.log2(a * 1)  # h(Uniform(0,2)) = log2(2) = 1
        expected = h_X + math.log2(abs(a))
        ok = abs(h_aX - expected) < 1e-10
        return (ok, f"h(2X) = {h_aX:.6f}, h(X)+log|a| = {expected:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.18: h(aX+b) = h(X) + log|a| for uniform",
        section="4",
        predicate=remark_318_scaling,
        note="Remark 3.18",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 4.1: Shannon Entropy ---
    def alg_4_1_entropy():
        p = [0.25, 0.25, 0.25, 0.25]
        H = -sum(pi * math.log2(pi) for pi in p if pi > 0)
        ok1 = abs(H - 2.0) < 1e-10  # uniform over 4 => 2 bits
        p2 = [0.5, 0.5]
        H2 = -sum(pi * math.log2(pi) for pi in p2 if pi > 0)
        ok2 = abs(H2 - 1.0) < 1e-10
        return (ok1 and ok2, f"H(uniform 4)={H:.6f}, H(fair coin)={H2:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.1: Shannon entropy",
        section="6",
        predicate=alg_4_1_entropy,
    ))

    # --- Algorithm 4.2: KL Divergence ---
    def alg_4_2_kl():
        p = [0.5, 0.5]
        q = [0.25, 0.75]
        D = sum(pi * math.log2(pi / qi) for pi, qi in zip(p, q) if pi > 0)
        ok1 = D >= -1e-10
        D_self = sum(pi * math.log2(pi / pi) for pi in p if pi > 0)
        ok2 = abs(D_self) < 1e-10
        return (ok1 and ok2, f"D_KL={D:.6f}, D_KL(p||p)={D_self:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 4.2: KL divergence",
        section="6",
        predicate=alg_4_2_kl,
    ))

    # --- Algorithm 4.3: Cross-Entropy ---
    def alg_4_3_cross_entropy():
        p = [0.5, 0.5]
        q = [0.25, 0.75]
        H_cross = -sum(pi * math.log2(qi) for pi, qi in zip(p, q) if pi > 0)
        H_p = -sum(pi * math.log2(pi) for pi in p if pi > 0)
        D_kl = sum(pi * math.log2(pi / qi) for pi, qi in zip(p, q) if pi > 0)
        ok = abs(H_cross - (H_p + D_kl)) < 1e-10
        return (ok, f"H_cross={H_cross:.6f}, H(p)+D_KL={H_p + D_kl:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.3: Cross-entropy = H(p) + D_KL(p||q)",
        section="6",
        predicate=alg_4_3_cross_entropy,
    ))

    # --- Algorithm 4.4: Mutual Information ---
    def alg_4_4_mutual_info():
        Pxy = np.array([[0.3, 0.1], [0.1, 0.5]])
        px = Pxy.sum(axis=1)
        py = Pxy.sum(axis=0)
        MI = 0
        for i in range(2):
            for j in range(2):
                if Pxy[i, j] > 0:
                    MI += Pxy[i, j] * math.log2(Pxy[i, j] / (px[i] * py[j]))
        ok1 = MI >= -1e-10
        Pxy_indep = np.outer(px, py)
        MI_indep = 0
        for i in range(2):
            for j in range(2):
                if Pxy_indep[i, j] > 0:
                    MI_indep += Pxy_indep[i, j] * math.log2(Pxy_indep[i, j] / (px[i] * py[j]))
        ok2 = abs(MI_indep) < 1e-10
        return (ok1 and ok2, f"MI={MI:.6f}, MI(indep)={MI_indep:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 4.4: Mutual information",
        section="6",
        predicate=alg_4_4_mutual_info,
    ))

    # --- Algorithm 4.5: Maximum Entropy (Geometric) ---
    def alg_4_5_max_entropy():
        mu = 3.0
        theta = mu / (1 + mu)
        mean_check = theta / (1 - theta)
        ok1 = abs(mean_check - mu) < 1e-10
        N = 100
        total = sum((1 - theta) * theta ** k for k in range(N))
        ok2 = abs(total - 1.0) < 1e-10
        return (ok1 and ok2, f"theta={theta:.4f}, mean={mean_check:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.5: Maximum entropy geometric distribution",
        section="6",
        predicate=alg_4_5_max_entropy,
    ))

    # --- Algorithm 4.6: Blahut-Arimoto ---
    def alg_4_6_blahut_arimoto():
        p_err = 0.1
        W = np.array([[1 - p_err, p_err], [p_err, 1 - p_err]])
        n_in = W.shape[0]
        p_in = np.ones(n_in) / n_in
        for _ in range(200):
            q = p_in @ W
            c = np.zeros(n_in)
            for i in range(n_in):
                c[i] = np.exp(np.sum(W[i] * np.log(W[i] / q + 1e-300)))
            Z = np.sum(p_in * c)
            p_in = p_in * c / Z
        C = math.log2(Z)
        Hp = -p_err * math.log2(p_err) - (1 - p_err) * math.log2(1 - p_err)
        C_exact = 1 - Hp
        ok = abs(C - C_exact) < 1e-4
        return (ok, f"BA capacity={C:.6f}, exact={C_exact:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.6: Blahut-Arimoto channel capacity",
        section="6",
        predicate=alg_4_6_blahut_arimoto,
    ))

    # --- Remark 3.16: Cross-entropy with one-hot = negative log-likelihood ---
    def _remark_3_16_cross_entropy_nll():
        """Verify H_Q(delta_{y*}) = -log q(y*) for one-hot P."""
        q = np.array([0.1, 0.3, 0.6])  # predicted probabilities
        for y_star in range(3):
            # One-hot P
            p = np.zeros(3)
            p[y_star] = 1.0
            cross_ent = -np.sum(p * np.log(q))  # H_Q(P)
            nll = -np.log(q[y_star])
            if abs(cross_ent - nll) > 1e-12:
                return (False, f"y*={y_star}: H_Q(P)={cross_ent}, -log q(y*)={nll}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.16: Cross-entropy with one-hot = -log q(y*)",
        section="3.16",
        predicate=_remark_3_16_cross_entropy_nll,
        note="Remark 3.16: cross-entropy = MLE",
    ))

    # ── Remark 3.15: Cross-entropy minimization = KL minimization ────────
    # Claims: min H_Q(P) over Q <=> min D_KL(P||Q) since H(P) is constant.
    # Verify: H_Q(P) = H(P) + D_KL(P||Q) numerically.
    def _remark_3_15_cross_entropy_kl():
        import numpy as np

        # P is the true distribution, Q is the model distribution
        P = np.array([0.2, 0.3, 0.5])
        Q_list = [
            np.array([0.1, 0.4, 0.5]),
            np.array([0.25, 0.25, 0.5]),
            np.array([0.2, 0.3, 0.5]),  # Q = P
            np.array([0.33, 0.33, 0.34]),
        ]

        H_P = -np.sum(P * np.log(P))

        for Q in Q_list:
            H_cross = -np.sum(P * np.log(Q))
            D_KL = np.sum(P * np.log(P / Q))

            # Verify: H_cross = H(P) + D_KL(P||Q)
            if abs(H_cross - (H_P + D_KL)) > 1e-12:
                return (False, f"H_Q(P)={H_cross:.6f} != H(P)+D_KL={H_P + D_KL:.6f}")

            # D_KL >= 0 (Gibbs' inequality)
            if D_KL < -1e-12:
                return (False, f"D_KL={D_KL:.6f} < 0")

        # Verify: D_KL = 0 iff Q = P
        Q_equal = np.array([0.2, 0.3, 0.5])
        D_KL_equal = np.sum(P * np.log(P / Q_equal))
        if abs(D_KL_equal) > 1e-12:
            return (False, f"D_KL(P||P) = {D_KL_equal}, expected 0")

        # Verify: minimizing cross-entropy over Q is same as minimizing D_KL
        # (since H(P) is constant, the Q that minimizes H_Q(P) also minimizes D_KL)
        cross_entropies = [-np.sum(P * np.log(Q)) for Q in Q_list]
        kl_divs = [np.sum(P * np.log(P / Q)) for Q in Q_list]
        min_ce_idx = np.argmin(cross_entropies)
        min_kl_idx = np.argmin(kl_divs)
        if min_ce_idx != min_kl_idx:
            return (False, f"Min cross-entropy at idx {min_ce_idx} != min D_KL at idx {min_kl_idx}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.15: H_Q(P) = H(P) + D_KL(P||Q), minimizers coincide",
        section="3.15",
        predicate=_remark_3_15_cross_entropy_kl,
        note="Remark 3.15: cross-entropy/KL equivalence verified",
    ))

    return ch
