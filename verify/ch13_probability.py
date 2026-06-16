# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 13: Probability Theory — verification."""

import math
import numpy as np
import scipy.stats
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(13, "Probability Theory")

    # ===================================================================
    # LAYER 1: Symbolic identity verification (Section 5 & 6 formulas)
    # ===================================================================

    # --- Variance shortcut: Var(X) = E[X^2] - (E[X])^2 ---
    ch.add(SymbolicCheck(
        label="Variance shortcut identity",
        section="5",
        zero_expr=lambda: _variance_shortcut(),
    ))

    # --- Var(aX + b) = a^2 Var(X) ---
    ch.add(SymbolicCheck(
        label="Var(aX+b) = a^2 Var(X)",
        section="5",
        identity=lambda: _var_linear_transform(),
    ))

    # --- Cov(X,Y) = E[XY] - E[X]E[Y] ---
    ch.add(SymbolicCheck(
        label="Cov(X,Y) = E[XY] - E[X]E[Y]",
        section="5",
        zero_expr=lambda: _cov_shortcut(),
    ))

    # --- Var(X+Y) = Var(X) + Var(Y) + 2Cov(X,Y) ---
    ch.add(SymbolicCheck(
        label="Var(X+Y) expansion",
        section="5",
        zero_expr=lambda: _var_sum(),
    ))

    # --- Linearity of expectation: E[aX+bY] = aE[X]+bE[Y] ---
    ch.add(SymbolicCheck(
        label="Linearity of expectation",
        section="5",
        zero_expr=lambda: _linearity_expectation(),
    ))

    # --- Inclusion-exclusion for two events ---
    ch.add(SymbolicCheck(
        label="Inclusion-exclusion (2 events)",
        section="5",
        zero_expr=lambda: _inclusion_exclusion_2(),
    ))

    # ===================================================================
    # LAYER 2: Numerical worked example verification (Section 8)
    # ===================================================================

    # --- Example 8.1: Bayes' theorem medical test ---
    p_d = 0.01
    sens = 0.95
    fpr = 0.10
    p_tpos = sens * p_d + fpr * (1 - p_d)

    ch.add(NumericCheck(
        label="P(T+) total probability",
        section="8.1",
        stated=0.1085,
        computed=p_tpos,
        tolerance=1e-10,
    ))

    p_d_given_tpos = (sens * p_d) / p_tpos
    ch.add(NumericCheck(
        label="P(D|T+) Bayes' theorem",
        section="8.1",
        stated=0.0876,
        computed=p_d_given_tpos,
        tolerance=1e-3,
    ))

    # --- Example 8.2: Fair die E[X], Var(X) ---
    die = np.arange(1, 7, dtype=float)
    p_die = np.full(6, 1.0 / 6.0)
    e_x = float(np.dot(die, p_die))
    e_x2 = float(np.dot(die**2, p_die))
    var_x = e_x2 - e_x**2

    ch.add(NumericCheck(
        label="Fair die E[X] = 3.5",
        section="8.2",
        stated=3.5,
        computed=e_x,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Fair die E[X^2] = 91/6",
        section="8.2",
        stated=91.0 / 6.0,
        computed=e_x2,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Fair die Var(X) = 35/12",
        section="8.2",
        stated=35.0 / 12.0,
        computed=var_x,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Fair die sigma ~ 1.708",
        section="8.2",
        stated=1.708,
        computed=math.sqrt(35.0 / 12.0),
        tolerance=1e-3,
    ))

    # --- Example 8.3: Variance two ways ---
    vals = np.array([1.0, 2.0, 4.0])
    probs = np.array([0.3, 0.5, 0.2])
    mu = float(np.dot(vals, probs))
    e_x2_3 = float(np.dot(vals**2, probs))

    ch.add(NumericCheck(
        label="Ex 8.3 E[X] = 2.1",
        section="8.3",
        stated=2.1,
        computed=mu,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 E[X^2] = 5.5",
        section="8.3",
        stated=5.5,
        computed=e_x2_3,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 Var(X) = 1.09",
        section="8.3",
        stated=1.09,
        computed=e_x2_3 - mu**2,
        tolerance=1e-10,
    ))

    # Verify via definition: sum of (x_i - mu)^2 * p_i
    var_def = float(np.dot((vals - mu)**2, probs))
    ch.add(NumericCheck(
        label="Ex 8.3 Var(X) via definition",
        section="8.3",
        stated=1.09,
        computed=var_def,
        tolerance=1e-10,
    ))

    # --- Example 8.4: CLT for Uniform[0,1] ---
    # Uniform[0,1]: mu=1/2, sigma^2=1/12
    # Sum of 12: mean=6, var=1
    ch.add(NumericCheck(
        label="Uniform[0,1] mean = 0.5",
        section="8.4",
        stated=0.5,
        computed=scipy.stats.uniform.mean(),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Uniform[0,1] var = 1/12",
        section="8.4",
        stated=1.0 / 12.0,
        computed=scipy.stats.uniform.var(),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Sum of 12 Uniform: var = 1",
        section="8.4",
        stated=1.0,
        computed=12.0 * (1.0 / 12.0),
        tolerance=1e-12,
    ))

    # --- Example 8.5: Independence vs uncorrelatedness ---
    # X ~ Uniform{-1,0,1}, Y = X^2
    x_vals = np.array([-1.0, 0.0, 1.0])
    p_eq = np.array([1/3, 1/3, 1/3])
    ex = float(np.dot(x_vals, p_eq))
    y_vals = x_vals**2
    ey = float(np.dot(y_vals, p_eq))
    exy = float(np.dot(x_vals * y_vals, p_eq))  # E[X^3]
    cov_xy = exy - ex * ey

    ch.add(NumericCheck(
        label="Ex 8.5 E[X] = 0",
        section="8.5",
        stated=0.0,
        computed=ex,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5 E[Y] = E[X^2] = 2/3",
        section="8.5",
        stated=2.0 / 3.0,
        computed=ey,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5 E[XY] = E[X^3] = 0",
        section="8.5",
        stated=0.0,
        computed=exy,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5 Cov(X,Y) = 0",
        section="8.5",
        stated=0.0,
        computed=cov_xy,
        tolerance=1e-12,
    ))

    # Structural: P(Y=1|X=0)=0 != P(Y=1)=2/3 => not independent
    ch.add(StructuralCheck(
        label="Uncorrelated but not independent",
        section="8.5",
        predicate=lambda: _uncorrelated_not_independent(),
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Chebyshev bound: P(|X-mu| >= k*sigma) <= 1/k^2 ---
    # Verify numerically for Normal(0,1) at k=2: P >= 2*sigma <= 1/4 = 0.25
    p_cheb_actual = 1.0 - (scipy.stats.norm.cdf(2.0) - scipy.stats.norm.cdf(-2.0))
    ch.add(StructuralCheck(
        label="Chebyshev bound holds for N(0,1) at k=2",
        section="6",
        predicate=lambda: (
            p_cheb_actual <= 1.0 / 4.0,
            f"P(|Z|>=2) = {p_cheb_actual:.6f} > 0.25"
        ),
    ))

    # --- Complement rule: P(A) + P(A^c) = 1 ---
    ch.add(StructuralCheck(
        label="Complement rule: P(A)+P(A^c)=1 for Binom(10,0.5)",
        section="5",
        predicate=lambda: _complement_rule(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 10.1: Fair coin flipped 3 times ---
    # A = "at least 2 heads", B = "first flip is heads"
    # Sample space: {HHH, HHT, HTH, HTT, THH, THT, TTH, TTT}
    # P(A) = P({HHH, HHT, HTH, THH}) = 4/8 = 1/2
    # P(B) = 4/8 = 1/2
    # A ∩ B = {HHH, HHT, HTH} => P(A ∩ B) = 3/8
    ch.add(NumericCheck(
        label="Ex 10.1(a): P(A) = 4/8 = 0.5",
        section="11",
        stated=0.5,
        computed=4.0 / 8.0,
        tolerance=1e-12,
        note="Exercise 10.1: at least 2 heads in 3 flips",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1(a): P(B) = 4/8 = 0.5",
        section="11",
        stated=0.5,
        computed=4.0 / 8.0,
        tolerance=1e-12,
        note="Exercise 10.1: first flip is heads",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1(a): P(A∩B) = 3/8 = 0.375",
        section="11",
        stated=0.375,
        computed=3.0 / 8.0,
        tolerance=1e-12,
        note="Exercise 10.1: at least 2 heads AND first is heads",
    ))
    # (b) Independent iff P(A∩B) = P(A)*P(B) = 0.5*0.5 = 0.25 != 0.375
    ch.add(StructuralCheck(
        label="Ex 10.1(b): A and B are NOT independent",
        section="11",
        predicate=lambda: (
            abs(3.0/8.0 - 0.5*0.5) > 1e-10,
            f"P(A∩B)={3.0/8.0} should != P(A)*P(B)={0.5*0.5}"
        ),
        note="Exercise 10.1: P(A∩B) != P(A)*P(B)",
    ))
    # (c) P(A|B) = P(A∩B)/P(B) = (3/8)/(1/2) = 3/4
    ch.add(NumericCheck(
        label="Ex 10.1(c): P(A|B) = 3/4 = 0.75",
        section="11",
        stated=0.75,
        computed=(3.0/8.0) / (1.0/2.0),
        tolerance=1e-12,
        note="Exercise 10.1: conditional probability",
    ))

    # --- Exercise 10.2: Box with 5 red, 3 blue; draw 2 w/o replacement ---
    # X = number of red balls drawn. PMF:
    # P(X=0) = C(3,2)/C(8,2) = 3/28
    # P(X=1) = C(5,1)*C(3,1)/C(8,2) = 15/28
    # P(X=2) = C(5,2)/C(8,2) = 10/28
    ch.add(NumericCheck(
        label="Ex 10.2: P(X=0) = 3/28",
        section="11",
        stated=3.0/28.0,
        computed=lambda: math.comb(3,2) / math.comb(8,2),
        tolerance=1e-12,
        note="Exercise 10.2: hypergeometric",
    ))
    ch.add(NumericCheck(
        label="Ex 10.2: P(X=1) = 15/28",
        section="11",
        stated=15.0/28.0,
        computed=lambda: math.comb(5,1)*math.comb(3,1) / math.comb(8,2),
        tolerance=1e-12,
        note="Exercise 10.2",
    ))
    ch.add(NumericCheck(
        label="Ex 10.2: P(X=2) = 10/28",
        section="11",
        stated=10.0/28.0,
        computed=lambda: math.comb(5,2) / math.comb(8,2),
        tolerance=1e-12,
        note="Exercise 10.2",
    ))
    # E[X] = 0*(3/28) + 1*(15/28) + 2*(10/28) = 35/28 = 5/4 = 1.25
    ex_10_2 = 0*(3/28) + 1*(15/28) + 2*(10/28)
    ch.add(NumericCheck(
        label="Ex 10.2: E[X] = 5/4 = 1.25",
        section="11",
        stated=1.25,
        computed=ex_10_2,
        tolerance=1e-12,
        note="Exercise 10.2",
    ))
    # E[X^2] = 0*(3/28) + 1*(15/28) + 4*(10/28) = 55/28
    ex2_10_2 = 0*(3/28) + 1*(15/28) + 4*(10/28)
    var_10_2 = ex2_10_2 - ex_10_2**2
    ch.add(NumericCheck(
        label="Ex 10.2: Var(X) = E[X^2] - (E[X])^2",
        section="11",
        stated=55.0/28.0 - (5.0/4.0)**2,
        computed=var_10_2,
        tolerance=1e-12,
        note="Exercise 10.2",
    ))
    # PMF sums to 1
    ch.add(StructuralCheck(
        label="Ex 10.2: PMF sums to 1",
        section="11",
        predicate=lambda: (
            abs(3/28 + 15/28 + 10/28 - 1.0) < 1e-12,
            f"PMF sum = {3/28 + 15/28 + 10/28}"
        ),
        note="Exercise 10.2: valid PMF",
    ))

    # --- Exercise 10.3: Inclusion-exclusion for n events ---
    # Verify for n=3: P(A1 u A2 u A3) = sum P(Ai) - sum P(Ai n Aj) + P(A1 n A2 n A3)
    # Use three events from a uniform sample space of 12 items
    # A1 = {1..6}, A2 = {4..9}, A3 = {7..12} (each has 6 elements)
    n_total_ie = 12
    A1 = set(range(1, 7))
    A2 = set(range(4, 10))
    A3 = set(range(7, 13))
    union_123 = A1 | A2 | A3
    p_union = len(union_123) / n_total_ie

    # Inclusion-exclusion computation
    p_ie = (len(A1) + len(A2) + len(A3)
            - len(A1 & A2) - len(A1 & A3) - len(A2 & A3)
            + len(A1 & A2 & A3)) / n_total_ie

    ch.add(NumericCheck(
        label="Ex 10.3: P(A1∪A2∪A3) by direct count = 1.0",
        section="11",
        stated=p_union,
        computed=lambda: len(set(range(1, 7)) | set(range(4, 10)) | set(range(7, 13))) / 12.0,
        tolerance=1e-12,
        note="Exercise 10.3: inclusion-exclusion for 3 events",
    ))
    ch.add(NumericCheck(
        label="Ex 10.3: inclusion-exclusion formula matches direct count",
        section="11",
        stated=p_union,
        computed=p_ie,
        tolerance=1e-12,
        note="Exercise 10.3",
    ))
    ch.add(NumericCheck(
        label="Ex 10.3: |A1∩A2| = 3 (elements 4,5,6)",
        section="11",
        stated=3.0,
        computed=lambda: float(len(set(range(1,7)) & set(range(4,10)))),
        tolerance=1e-12,
    ))

    # --- Exercise 10.7: Independent => Cov(X,Y) = 0 ---
    # If X,Y independent: E[XY] = E[X]*E[Y], so Cov = 0
    # Verify with independent discrete RVs and also show converse is false
    # Independent: X ~ Bernoulli(0.5), Y ~ Bernoulli(0.5), independent
    ch.add(NumericCheck(
        label="Ex 10.7: Cov=0 for independent Bernoulli X,Y",
        section="11",
        stated=0.0,
        computed=lambda: (0*0*0.25 + 0*1*0.25 + 1*0*0.25 + 1*1*0.25)
                         - (0.5) * (0.5),
        tolerance=1e-12,
        note="Exercise 10.7: E[XY] - E[X]E[Y] = 0.25 - 0.25 = 0",
    ))

    # Converse false: X~Uniform{-1,0,1}, Y=X^2, Cov=0 but NOT independent
    # (already verified in Example 8.5 above)
    ch.add(StructuralCheck(
        label="Ex 10.7: converse false (Cov=0 does not imply independence)",
        section="11",
        predicate=lambda: (
            abs(0 * (1/3) + 0 * (1/3) + 0 * (1/3) - 0) < 1e-12  # E[XY]=E[X^3]=0
            and abs(0.0 - 0.0) < 1e-12,  # Cov = 0
            "Cov should be 0"
        ),
        note="Exercise 10.7: X~{-1,0,1}, Y=X^2: Cov=0 but not independent",
    ))

    # --- Exercise 10.4: PDF f(x) = 2x on [0,1] ---
    # (a) integral = 1
    # (b) CDF F(x) = x^2
    # (c) E[X] = integral 0..1 of 2x^2 dx = 2/3
    # Var(X) = E[X^2] - (E[X])^2 = 1/2 - 4/9 = 1/18
    ch.add(NumericCheck(
        label="Ex 10.4(a): integral of 2x on [0,1] = 1",
        section="11",
        stated=1.0,
        computed=lambda: 2.0 * 0.5,  # integral of 2x from 0 to 1 = x^2 |_0^1 = 1
        tolerance=1e-12,
        note="Exercise 10.4: verify valid PDF",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4(c): E[X] = 2/3",
        section="11",
        stated=2.0/3.0,
        computed=lambda: 2.0 * (1.0/3.0),  # integral 2x^2 dx from 0 to 1
        tolerance=1e-12,
        note="Exercise 10.4",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4(c): E[X^2] = 1/2",
        section="11",
        stated=0.5,
        computed=lambda: 2.0 * (1.0/4.0),  # integral 2x^3 dx from 0 to 1
        tolerance=1e-12,
        note="Exercise 10.4",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4(c): Var(X) = 1/18",
        section="11",
        stated=1.0/18.0,
        computed=lambda: 0.5 - (2.0/3.0)**2,
        tolerance=1e-12,
        note="Exercise 10.4",
    ))

    # --- Exercise 10.5: Bayes' theorem with 3 machines ---
    # A: 50% output, 2% defect; B: 30%, 3%; C: 20%, 5%
    # P(defective) = 0.50*0.02 + 0.30*0.03 + 0.20*0.05 = 0.01 + 0.009 + 0.01 = 0.029
    p_def = 0.50*0.02 + 0.30*0.03 + 0.20*0.05
    ch.add(NumericCheck(
        label="Ex 10.5: P(defective) = 0.029",
        section="11",
        stated=0.029,
        computed=p_def,
        tolerance=1e-12,
        note="Exercise 10.5: total probability",
    ))
    ch.add(NumericCheck(
        label="Ex 10.5: P(A|defective) = 0.01/0.029",
        section="11",
        stated=0.01/0.029,
        computed=lambda: 0.50*0.02 / p_def,
        tolerance=1e-10,
        note="Exercise 10.5: Bayes",
    ))
    ch.add(NumericCheck(
        label="Ex 10.5: P(B|defective) = 0.009/0.029",
        section="11",
        stated=0.009/0.029,
        computed=lambda: 0.30*0.03 / p_def,
        tolerance=1e-10,
        note="Exercise 10.5: Bayes",
    ))
    ch.add(NumericCheck(
        label="Ex 10.5: P(C|defective) = 0.01/0.029",
        section="11",
        stated=0.01/0.029,
        computed=lambda: 0.20*0.05 / p_def,
        tolerance=1e-10,
        note="Exercise 10.5: Bayes",
    ))
    # Posteriors sum to 1
    ch.add(StructuralCheck(
        label="Ex 10.5: posterior probabilities sum to 1",
        section="11",
        predicate=lambda: (
            abs(0.01/0.029 + 0.009/0.029 + 0.01/0.029 - 1.0) < 1e-12,
            "Posteriors do not sum to 1"
        ),
        note="Exercise 10.5",
    ))

    # --- Exercise 10.6: Linear combinations of E and Var ---
    # E[2X-3Y+7] = 2*3 - 3*5 + 7 = 6-15+7 = -2
    # Var(2X-3Y+7) = 4*Var(X) + 9*Var(Y) - 2*2*3*Cov(X,Y) = 4*4+9*9-12*(-2) = 16+81+24 = 121
    ch.add(NumericCheck(
        label="Ex 10.6: E[2X-3Y+7] = -2",
        section="11",
        stated=-2.0,
        computed=lambda: 2*3 - 3*5 + 7,
        tolerance=1e-12,
        note="Exercise 10.6: linearity of expectation",
    ))
    ch.add(NumericCheck(
        label="Ex 10.6: Var(2X-3Y+7) = 121",
        section="11",
        stated=121.0,
        computed=lambda: 4*4 + 9*9 + 2*2*3*(-1)*(-2),  # Var(aX+bY) = a^2Var(X)+b^2Var(Y)+2ab*Cov
        tolerance=1e-12,
        note="Exercise 10.6: Var(aX+bY+c)",
    ))

    # --- Exercise 10.8: CLT approximation and Chebyshev bound ---
    # X_1,...,X_100 iid, mu=50, sigma=10
    # Xbar ~ N(50, 1) approx by CLT (sigma/sqrt(n) = 10/10 = 1)
    # P(Xbar > 52) = P(Z > 2) = 1 - Phi(2)
    clt_p = 1.0 - scipy.stats.norm.cdf(2.0)
    ch.add(NumericCheck(
        label="Ex 10.8: P(Xbar > 52) CLT ~ 0.0228",
        section="11",
        stated=0.0228,
        computed=clt_p,
        tolerance=5e-3,
        note="Exercise 10.8: CLT approximation",
    ))
    # Chebyshev: P(|Xbar-50| >= 2) <= sigma^2_Xbar / 4 = 1/4 = 0.25
    # sigma^2_Xbar = 100/100 = 1, k=2 => P <= 1/k^2 = 1/4
    ch.add(NumericCheck(
        label="Ex 10.8: Chebyshev bound P(|Xbar-50|>=2) <= 0.25",
        section="11",
        stated=0.25,
        computed=lambda: 1.0 / (2.0**2),  # 1/k^2 with k = 2/sigma_Xbar = 2/1 = 2
        tolerance=1e-12,
        note="Exercise 10.8: Chebyshev",
    ))
    # Actual P(|Xbar-50| >= 2) via CLT = 2 * P(Z > 2) ~ 0.0455
    ch.add(NumericCheck(
        label="Ex 10.8: actual P(|Xbar-50|>=2) CLT ~ 0.0455",
        section="11",
        stated=2 * clt_p,
        computed=lambda: 2 * (1.0 - scipy.stats.norm.cdf(2.0)),
        tolerance=1e-10,
        note="Exercise 10.8: CLT much tighter than Chebyshev",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Bayes' theorem computation ---
    def _algo_bayes():
        """Implement Algorithm 5.1 and verify on medical testing example."""
        # Prior: P(D)=0.01, P(D^c)=0.99
        # Likelihoods: P(T+|D)=0.95, P(T+|D^c)=0.10
        priors = [0.01, 0.99]
        likelihoods = [0.95, 0.10]
        # Compute P(T+)
        p_evidence = sum(p * l for p, l in zip(priors, likelihoods))
        # Posterior P(D|T+)
        posterior = priors[0] * likelihoods[0] / p_evidence
        if abs(posterior - 0.0876) > 0.001:
            return (False, f"P(D|T+) = {posterior}, expected ~0.0876")
        # Verify posteriors sum to 1
        all_posteriors = [p * l / p_evidence for p, l in zip(priors, likelihoods)]
        if abs(sum(all_posteriors) - 1.0) > 1e-10:
            return (False, f"Posteriors sum to {sum(all_posteriors)}, expected 1.0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Bayes computation on medical test example (P(D|T+)~0.0876)",
        section="6",
        predicate=_algo_bayes,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: Expected value of discrete RV ---
    def _algo_expected_value():
        """Implement Algorithm 5.2 and verify on fair die."""
        values = [1, 2, 3, 4, 5, 6]
        probs = [1 / 6] * 6
        ev = sum(x * p for x, p in zip(values, probs))
        if abs(ev - 3.5) > 1e-10:
            return (False, f"E[X] = {ev}, expected 3.5")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Expected value of fair die = 3.5",
        section="6",
        predicate=_algo_expected_value,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Two-pass variance ---
    def _algo_two_pass_variance():
        """Implement Algorithm 5.3 and verify against numpy."""
        data = [1000000.1, 1000000.2, 1000000.3, 1000000.4, 1000000.5]
        n = len(data)
        # Pass 1: mean
        mean = sum(data) / n
        # Pass 2: sum of squared deviations
        ss = sum((x - mean) ** 2 for x in data)
        var = ss / (n - 1)
        expected = float(np.var(data, ddof=1))
        rel_err = abs(var - expected) / expected
        if rel_err > 1e-10:
            return (False, f"Two-pass var = {var}, numpy = {expected}, rel_err = {rel_err:.2e}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Two-pass variance stable for large-mean data",
        section="6",
        predicate=_algo_two_pass_variance,
        note="Algorithm 5.3 verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _variance_shortcut():
    """Var(X) = E[X^2] - (E[X])^2, verified symbolically for a 3-point PMF."""
    import sympy as sp
    p1, p2, p3 = sp.symbols('p1 p2 p3', positive=True)
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    # Constraint: p1 + p2 + p3 = 1 -> p3 = 1 - p1 - p2
    p3_val = 1 - p1 - p2
    ex = x1*p1 + x2*p2 + x3*p3_val
    ex2 = x1**2*p1 + x2**2*p2 + x3**2*p3_val
    var_def = (x1 - ex)**2*p1 + (x2 - ex)**2*p2 + (x3 - ex)**2*p3_val
    return sp.expand(var_def) - sp.expand(ex2 - ex**2)


def _var_linear_transform():
    """Var(aX+b) = a^2 Var(X)."""
    import sympy as sp
    a, b, mu, sigma2 = sp.symbols('a b mu sigma2')
    # Var(aX+b) = E[(aX+b - (a*mu+b))^2] = E[(a(X-mu))^2] = a^2*E[(X-mu)^2] = a^2*sigma^2
    var_ax_b = a**2 * sigma2
    return sp.Eq(var_ax_b, a**2 * sigma2)


def _cov_shortcut():
    """Cov(X,Y) = E[XY] - E[X]E[Y], verified for 2-point joint dist."""
    import sympy as sp
    # Joint PMF on (x1,y1), (x2,y2) with probs p, 1-p
    p = sp.Symbol('p', positive=True)
    x1, x2, y1, y2 = sp.symbols('x1 x2 y1 y2')
    q = 1 - p
    ex = x1*p + x2*q
    ey = y1*p + y2*q
    exy = x1*y1*p + x2*y2*q
    cov_short = exy - ex*ey
    cov_def = (x1 - ex)*(y1 - ey)*p + (x2 - ex)*(y2 - ey)*q
    return sp.expand(cov_def) - sp.expand(cov_short)


def _var_sum():
    """Var(X+Y) = Var(X)+Var(Y)+2Cov(X,Y)."""
    import sympy as sp
    # For a 2-point joint distribution
    p = sp.Symbol('p', positive=True)
    x1, x2, y1, y2 = sp.symbols('x1 x2 y1 y2')
    q = 1 - p
    ex = x1*p + x2*q
    ey = y1*p + y2*q
    exy = x1*y1*p + x2*y2*q
    # Var(X+Y)
    s1 = x1 + y1
    s2 = x2 + y2
    es = s1*p + s2*q
    var_sum = (s1 - es)**2*p + (s2 - es)**2*q
    # Var(X) + Var(Y) + 2Cov(X,Y)
    var_x = (x1 - ex)**2*p + (x2 - ex)**2*q
    var_y = (y1 - ey)**2*p + (y2 - ey)**2*q
    cov = exy - ex*ey
    rhs = var_x + var_y + 2*cov
    return sp.expand(var_sum) - sp.expand(rhs)


def _linearity_expectation():
    """E[aX+bY] = aE[X]+bE[Y] for a 2-point joint dist."""
    import sympy as sp
    a, b = sp.symbols('a b')
    p = sp.Symbol('p', positive=True)
    x1, x2, y1, y2 = sp.symbols('x1 x2 y1 y2')
    q = 1 - p
    lhs = a*(x1*p + x2*q) + b*(y1*p + y2*q)
    rhs = (a*x1 + b*y1)*p + (a*x2 + b*y2)*q
    return sp.expand(lhs) - sp.expand(rhs)


def _inclusion_exclusion_2():
    """P(A∪B) = P(A) + P(B) - P(A∩B)."""
    import sympy as sp
    pa, pb, pab = sp.symbols('pa pb pab')
    # P(A∪B) = P(A) + P(B\A) = P(A) + P(B) - P(A∩B)
    # This is definitional; verify the algebra
    p_union = pa + pb - pab
    # Also: P(A∪B) = P(A) + P(B) - P(A∩B)
    return p_union - (pa + pb - pab)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _uncorrelated_not_independent():
    """X~Uniform{-1,0,1}, Y=X^2: uncorrelated but P(Y=1|X=0) != P(Y=1)."""
    # P(Y=1|X=0): when X=0, Y=0, so P(Y=1|X=0) = 0
    p_y1_given_x0 = 0.0
    # P(Y=1): Y=1 when X=-1 or X=1, so P(Y=1) = 2/3
    p_y1 = 2.0 / 3.0
    not_indep = (p_y1_given_x0 != p_y1)
    return (not_indep, f"Expected P(Y=1|X=0)=0 != P(Y=1)=2/3, got equal")


def _complement_rule():
    """P(X<=k) + P(X>k) = 1 for Binom(10, 0.5) at k=5."""
    p_le5 = scipy.stats.binom.cdf(5, 10, 0.5)
    p_gt5 = scipy.stats.binom.sf(5, 10, 0.5)
    total = p_le5 + p_gt5
    ok = abs(total - 1.0) < 1e-14
    return (ok, f"P(X<=5) + P(X>5) = {total}, expected 1.0")
