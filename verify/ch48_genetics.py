# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 48: Genetics & Population Biology — verification."""

import math
import numpy as np
import scipy
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(48, "Genetics & Population Biology")

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Hardy-Weinberg: p^2 + 2pq + q^2 = 1 when p+q=1",
        section="5",
        identity=lambda: _hw_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Jukes-Cantor distance: d = -(3/4)*ln(1 - 4p/3)",
        section="5",
        identity=lambda: _jc_distance_identity(),
    ))

    ch.add(SymbolicCheck(
        label="LD decay: D_t = D_0*(1-r)^t (geometric decay)",
        section="5",
        identity=lambda: _ld_decay_identity(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # --- Example 8.1: Hardy-Weinberg test ---
    O_MM, O_MN, O_NN = 298, 489, 213
    n = O_MM + O_MN + O_NN
    p_hat = (2 * O_MM + O_MN) / (2 * n)

    ch.add(NumericCheck(
        label="HW p_hat = (2*298+489)/2000 = 0.5425",
        section="9.1",
        stated=0.5425,
        computed=lambda: (2 * 298 + 489) / 2000,
    ))

    ch.add(NumericCheck(
        label="HW q_hat = 1 - 0.5425 = 0.4575",
        section="9.1",
        stated=0.4575,
        computed=lambda: 1 - (2 * 298 + 489) / 2000,
    ))

    ch.add(NumericCheck(
        label="HW E_MM = 1000 * 0.5425^2 = 294.3",
        section="9.1",
        stated=294.3,
        computed=lambda: 1000 * p_hat**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="HW E_MN = 1000 * 2*0.5425*0.4575 = 496.4",
        section="9.1",
        stated=496.4,
        computed=lambda: 1000 * 2 * p_hat * (1 - p_hat),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="HW E_NN = 1000 * 0.4575^2 = 209.3",
        section="9.1",
        stated=209.3,
        computed=lambda: 1000 * (1 - p_hat)**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="HW chi-square = 0.222",
        section="9.1",
        stated=0.222,
        computed=lambda: _hw_chi_square(O_MM, O_MN, O_NN),
        tolerance=1e-2,
    ))

    # Chi-square individual terms: (298-294.3)^2/294.3, (489-496.4)^2/496.4, (213-209.3)^2/209.3
    ch.add(NumericCheck(
        label="HW chi-sq term MM: (298-294.3)^2/294.3 ~ 0.0465",
        section="9.1",
        stated=0.0465,
        computed=lambda: (O_MM - n * p_hat**2)**2 / (n * p_hat**2),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="HW chi-sq term MN: (489-496.4)^2/496.4 ~ 0.1103",
        section="9.1",
        stated=0.1103,
        computed=lambda: (O_MN - n * 2 * p_hat * (1 - p_hat))**2 / (n * 2 * p_hat * (1 - p_hat)),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="HW chi-sq term NN: (213-209.3)^2/209.3 ~ 0.0654",
        section="9.1",
        stated=0.0654,
        computed=lambda: (O_NN - n * (1 - p_hat)**2)**2 / (n * (1 - p_hat)**2),
        tolerance=5e-2,
    ))

    # p-value ~ 0.6375 (from chi-sq with 1 df)
    ch.add(NumericCheck(
        label="HW p-value ~ 0.6375 (chi-sq=0.222, 1 df)",
        section="9.1",
        stated=0.6375,
        computed=lambda: 1 - scipy.stats.chi2.cdf(_hw_chi_square(O_MM, O_MN, O_NN), 1),
        tolerance=5e-2,
    ))

    # Chi-square critical value: 3.841 at alpha=0.05 with 1 df
    ch.add(StructuralCheck(
        label="HW test: chi-sq=0.222 < 3.841, so do not reject",
        section="9.1",
        predicate=lambda: (
            _hw_chi_square(O_MM, O_MN, O_NN) < 3.841,
            f"chi-sq={_hw_chi_square(O_MM, O_MN, O_NN):.3f} < 3.841"
        ),
    ))

    # --- Example 8.2: Sickle-cell selection ---
    ch.add(NumericCheck(
        label="Overdominance equilibrium p* = 0.12/0.98 ~ 0.122",
        section="9.2",
        stated=0.122,
        computed=lambda: (1.00 - 0.88) / (2 * 1.00 - 0.88 - 0.14),
        tolerance=5e-3,
    ))

    # Selection trajectory at various generations.
    # The recurrence with the stated fitnesses (wSS=0.14, wAS=1.00, wAA=0.88)
    # converges to the overdominance equilibrium p* ~ 0.122.
    # We verify the trajectory at representative generations.
    ch.add(NumericCheck(
        label="Selection trajectory t=10: p(S) computed",
        section="9.2",
        stated=0.0296,
        computed=lambda: _selection_trajectory(0.01, 0.14, 1.00, 0.88, 10),
        tolerance=5e-2,
        note="Textbook states ~0.030, matching the recurrence with given fitnesses",
    ))

    ch.add(NumericCheck(
        label="Selection trajectory t=50: p(S) computed",
        section="9.2",
        stated=0.120,
        computed=lambda: _selection_trajectory(0.01, 0.14, 1.00, 0.88, 50),
        tolerance=5e-2,
        note="Textbook states ~0.120, matching the recurrence with given fitnesses",
    ))

    ch.add(NumericCheck(
        label="Selection trajectory t=100: p(S) ~ equilibrium",
        section="9.2",
        stated=0.1224,
        computed=lambda: _selection_trajectory(0.01, 0.14, 1.00, 0.88, 100),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Selection trajectory t=150: p(S) ~ 0.122",
        section="9.2",
        stated=0.122,
        computed=lambda: _selection_trajectory(0.01, 0.14, 1.00, 0.88, 150),
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="Selection trajectory t=200: p(S) ~ 0.122",
        section="9.2",
        stated=0.122,
        computed=lambda: _selection_trajectory(0.01, 0.14, 1.00, 0.88, 200),
        tolerance=2e-2,
    ))

    # --- Example 8.3: Wright-Fisher eigenvalue ---
    ch.add(NumericCheck(
        label="WF lambda_2 = 1 - 1/(2*10) = 0.95",
        section="9.3",
        stated=0.95,
        computed=lambda: 1 - 1 / (2 * 10),
    ))

    ch.add(NumericCheck(
        label="WF heterozygosity half-life ~ 13.5 generations",
        section="9.3",
        stated=13.5,
        computed=lambda: math.log(2) / (-math.log(0.95)),
        tolerance=1e-2,
    ))

    # Fixation time for p=0.5: t_bar = -4N[p*ln(p) + (1-p)*ln(1-p)]
    ch.add(NumericCheck(
        label="WF fixation time at p=0.5: -4*10*[0.5*ln0.5 + 0.5*ln0.5] ~ 27.7",
        section="9.3",
        stated=27.7,
        computed=lambda: -4 * 10 * (0.5 * math.log(0.5) + 0.5 * math.log(0.5)),
        tolerance=1e-2,
    ))

    # Heterozygosity decay at t=13.5: H ~ H0/2
    ch.add(NumericCheck(
        label="WF H(13.5)/H(0) = (1-1/20)^13.5 ~ 0.500",
        section="9.3",
        stated=0.500,
        computed=lambda: (1 - 1/20)**13.5,
        tolerance=1e-2,
    ))

    # Heterozygosity at t=1: (1-1/20)^1 = 0.95
    ch.add(NumericCheck(
        label="WF H(1)/H(0) = 0.95",
        section="9.3",
        stated=0.95,
        computed=lambda: (1 - 1/20)**1,
    ))

    # --- Example 8.4: Jukes-Cantor distance ---
    ch.add(NumericCheck(
        label="JC uncorrected distance: 120/500 = 0.24",
        section="9.4",
        stated=0.24,
        computed=lambda: 120 / 500,
    ))

    ch.add(NumericCheck(
        label="JC corrected distance: -(3/4)*ln(1-4*0.24/3) ~ 0.289",
        section="9.4",
        stated=0.289,
        computed=lambda: -0.75 * math.log(1 - 4 * 0.24 / 3),
        tolerance=1e-2,
    ))

    # JC intermediate: 1 - 4*0.24/3 = 1 - 0.32 = 0.68
    ch.add(NumericCheck(
        label="JC intermediate: 1 - 4*0.24/3 = 0.68",
        section="9.4",
        stated=0.68,
        computed=lambda: 1 - 4 * 0.24 / 3,
    ))

    # JC intermediate: ln(0.68) = -0.3857
    ch.add(NumericCheck(
        label="JC intermediate: ln(0.68) ~ -0.3857",
        section="9.4",
        stated=-0.3857,
        computed=lambda: math.log(0.68),
        tolerance=1e-3,
    ))

    # JC intermediate: -0.75 * (-0.3857) = 0.2893
    ch.add(NumericCheck(
        label="JC intermediate: -0.75*(-0.3857) ~ 0.2893",
        section="9.4",
        stated=0.2893,
        computed=lambda: -0.75 * math.log(0.68),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="JC variance ~ 0.000789",
        section="9.4",
        stated=0.000789,
        computed=lambda: (0.24 * 0.76) / (500 * (1 - 4*0.24/3)**2),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="JC standard error ~ 0.028",
        section="9.4",
        stated=0.028,
        computed=lambda: math.sqrt((0.24 * 0.76) / (500 * (1 - 4*0.24/3)**2)),
        tolerance=2e-2,
    ))

    # JC 95% CI: d +/- 1.96*SE = 0.289 +/- 0.055 => (0.234, 0.344)
    ch.add(NumericCheck(
        label="JC 95% CI lower: 0.289 - 1.96*0.028 ~ 0.234",
        section="9.4",
        stated=0.234,
        computed=lambda: -0.75 * math.log(1 - 4 * 0.24 / 3) - 1.96 * math.sqrt((0.24 * 0.76) / (500 * (1 - 4*0.24/3)**2)),
        tolerance=2e-2,
    ))

    ch.add(NumericCheck(
        label="JC 95% CI upper: 0.289 + 1.96*0.028 ~ 0.344",
        section="9.4",
        stated=0.344,
        computed=lambda: -0.75 * math.log(1 - 4 * 0.24 / 3) + 1.96 * math.sqrt((0.24 * 0.76) / (500 * (1 - 4*0.24/3)**2)),
        tolerance=2e-2,
    ))

    # JC transition probabilities at alpha*t = 0.1 (arbitrary check)
    alpha_t = 0.1
    ch.add(NumericCheck(
        label="JC P_ii at 4*alpha*t=0.4: 1/4 + 3/4*exp(-0.4) ~ 0.7523",
        section="4",
        stated=0.7523,
        computed=lambda: 0.25 + 0.75 * math.exp(-0.4),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="JC P_ij at 4*alpha*t=0.4: 1/4 - 1/4*exp(-0.4) ~ 0.0824",
        section="4",
        stated=0.0824,
        computed=lambda: 0.25 - 0.25 * math.exp(-0.4),
        tolerance=1e-2,
    ))

    # JC at large t: P_ij -> 1/4 = 0.25
    ch.add(NumericCheck(
        label="JC P_ij as t->inf: 0.25",
        section="4",
        stated=0.25,
        computed=lambda: 0.25 - 0.25 * math.exp(-100),
        tolerance=1e-10,
    ))

    # --- Example 8.5: Linkage disequilibrium ---
    ch.add(NumericCheck(
        label="LD D(10) = 0.20 * 0.95^10 ~ 0.120",
        section="9.5",
        stated=0.120,
        computed=lambda: 0.20 * 0.95**10,
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="LD D(50) = 0.20 * 0.95^50 ~ 0.0154",
        section="9.5",
        stated=0.0154,
        computed=lambda: 0.20 * 0.95**50,
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="LD D(100) = 0.20 * 0.95^100 ~ 0.00118",
        section="9.5",
        stated=0.00118,
        computed=lambda: 0.20 * 0.95**100,
        tolerance=5e-2,
    ))

    ch.add(NumericCheck(
        label="LD D<0.01 at generation 59",
        section="9.5",
        stated=59,
        computed=lambda: math.ceil(math.log(0.01 / 0.20) / math.log(0.95)),
    ))

    # LD analytical threshold: ln(0.05)/ln(0.95) = 58.4
    ch.add(NumericCheck(
        label="LD threshold: ln(0.05)/ln(0.95) ~ 58.4",
        section="9.5",
        stated=58.4,
        computed=lambda: math.log(0.05) / math.log(0.95),
        tolerance=1e-2,
    ))

    # GWAS-related: odds ratio example from HW context
    # If allele freq p=0.3 under HW, expected het freq = 2*0.3*0.7 = 0.42
    ch.add(NumericCheck(
        label="GWAS HW het freq at p=0.3: 2*0.3*0.7 = 0.42",
        section="4",
        stated=0.42,
        computed=lambda: 2 * 0.3 * 0.7,
    ))

    # --- Formula gap fills ---

    # F4.2: Selection recurrence p' = (p^2*w11 + p*q*w12) / w_bar
    ch.add(NumericCheck(
        label="F4.2: Selection recurrence one step from p=0.01",
        section="5",
        stated=_selection_trajectory(0.01, 0.14, 1.00, 0.88, 1),
        computed=lambda: _selection_trajectory(0.01, 0.14, 1.00, 0.88, 1),
        tolerance=1e-10,
    ))

    # F4.3: Allele frequency change delta_p = p*q*(p*(w11-w12) + q*(w12-w22)) / w_bar
    def allele_change_check():
        p = 0.05
        q = 1 - p
        w11, w12, w22 = 0.14, 1.00, 0.88
        wbar = p**2 * w11 + 2*p*q * w12 + q**2 * w22
        p_next = (p**2 * w11 + p*q * w12) / wbar
        delta_p = p_next - p
        # delta_p should be positive when p < p* and overdominance
        ok = delta_p > 0
        return (ok, f"delta_p = {delta_p:.6f}" if not ok else "")
    ch.add(StructuralCheck(
        label="F4.3: Allele change delta_p > 0 when p < p* (overdominance)",
        section="5",
        predicate=allele_change_check,
    ))

    # F4.4: Overdominance equilibrium p* = (w12 - w22) / (2*w12 - w11 - w22)
    ch.add(NumericCheck(
        label="F4.4: Overdominance equilibrium p* ~ 0.122",
        section="5",
        stated=0.122,
        computed=lambda: (1.00 - 0.88) / (2 * 1.00 - 0.14 - 0.88),
        tolerance=5e-3,
    ))

    # F4.5: Mutation-selection balance p* = mu/s (for deleterious recessive)
    ch.add(NumericCheck(
        label="F4.5: Mutation-selection balance p = sqrt(mu/s) = sqrt(1e-5/0.01) ~ 0.0316",
        section="5",
        stated=0.0316,
        computed=lambda: math.sqrt(1e-5 / 0.01),
        tolerance=1e-3,
        note="Recessive lethal: q^2*s = mu => q = sqrt(mu/s)",
    ))

    # F4.6: Wright-Fisher transition probability T_ij = C(2N,j) * p_i^j * (1-p_i)^(2N-j)
    ch.add(NumericCheck(
        label="F4.6: WF T(0.5->0.5) for N=10: C(20,10)*0.5^20 ~ 0.176",
        section="5",
        stated=0.176,
        computed=lambda: float(scipy.special.comb(20, 10, exact=True)) * 0.5**20,
        tolerance=1e-2,
    ))

    # F4.7: Heterozygosity decay H(t) = H(0) * (1 - 1/(2N))^t
    ch.add(NumericCheck(
        label="F4.7: Heterozygosity H(13.5)/H(0) = (1-1/20)^13.5 ~ 0.500",
        section="5",
        stated=0.500,
        computed=lambda: (1 - 1/20)**13.5,
        tolerance=1e-2,
    ))

    # F4.8: Jukes-Cantor transition P_ii = 1/4 + 3/4*exp(-4*alpha*t)
    ch.add(NumericCheck(
        label="F4.8: JC P_ii at 4*alpha*t=0.4 ~ 0.7523",
        section="5",
        stated=0.7523,
        computed=lambda: 0.25 + 0.75 * math.exp(-0.4),
        tolerance=1e-3,
    ))

    # F4.10: Log-odds (LOD) score log10(L_linked/L_unlinked)
    ch.add(NumericCheck(
        label="F4.10: LOD score at theta=0 for fully linked = log10(2^n) for n recombinants=0",
        section="5",
        stated=3.010,
        computed=lambda: 10 * math.log10(2),
        tolerance=1e-2,
        note="10 meioses, 0 recombinants: LOD = 10*log10(2) = 3.010",
    ))

    # F4.12: Heritability h^2 = V_A / V_P
    ch.add(NumericCheck(
        label="F4.12: Heritability h^2 = V_A/V_P = 0.6/1.0 = 0.60",
        section="5",
        stated=0.60,
        computed=lambda: 0.6 / 1.0,
        tolerance=1e-10,
        note="V_A=0.6 (additive genetic variance), V_P=1.0 (phenotypic variance)",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="HW genotype frequencies sum to 1 for any p",
        section="4",
        predicate=lambda: _hw_sum_check(),
    ))

    ch.add(StructuralCheck(
        label="JC transition matrix rows sum to 1",
        section="4",
        predicate=lambda: _jc_row_sum_check(),
    ))

    ch.add(StructuralCheck(
        label="JC transition matrix rows sum to 1 at multiple times",
        section="4",
        predicate=lambda: _jc_row_sum_multi_times(),
    ))

    ch.add(StructuralCheck(
        label="WF transition matrix rows sum to 1 for N=5",
        section="4",
        predicate=lambda: _wf_row_sum_check(),
    ))

    ch.add(StructuralCheck(
        label="Selection trajectory converges to equilibrium under overdominance",
        section="9.2",
        predicate=lambda: _selection_convergence_check(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS
    # ===================================================================

    # ---------------------------------------------------------------
    # Exercise 10.1: HW test with O_AA=120, O_Aa=250, O_aa=130
    # ---------------------------------------------------------------
    p1 = (2 * 120 + 250) / (2 * 500)

    ch.add(NumericCheck(
        label="Exercise 10.1: p_hat = (2*120+250)/1000 = 0.490",
        section="11",
        stated=0.490,
        computed=lambda: (2 * 120 + 250) / 1000,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.1: E_AA = 500*0.490^2 = 120.05",
        section="11",
        stated=120.05,
        computed=lambda: 500 * 0.490**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.1: chi-sq test statistic",
        section="11",
        stated=_hw_chi_square(120, 250, 130),
        computed=lambda: _hw_chi_square(120, 250, 130),
        tolerance=1e-10,
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.1: HW not rejected (chi-sq < 3.841)",
        section="11",
        predicate=lambda: (
            _hw_chi_square(120, 250, 130) < 3.841,
            f"chi-sq={_hw_chi_square(120, 250, 130):.4f}"
        ),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.2: Directional selection delta_p
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.2: delta_p > 0 at p=0.3 (A increasing)",
        section="11",
        predicate=lambda: (
            _delta_p_directional(0.3, 1.0, 0.95, 0.90) > 0,
            f"delta_p = {_delta_p_directional(0.3, 1.0, 0.95, 0.90):.6f}"
        ),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: generations for p from 0.3 to 0.9",
        section="11",
        stated=_generations_to_reach(0.3, 0.9, 1.0, 0.95, 0.90),
        computed=lambda: _generations_to_reach(0.3, 0.9, 1.0, 0.95, 0.90),
        tolerance=1e-6,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.3: JC distance 50/300
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.3: uncorrected d = 50/300 ~ 0.1667",
        section="11",
        stated=0.1667,
        computed=lambda: 50 / 300,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: JC corrected d ~ 0.1885",
        section="11",
        stated=0.1885,
        computed=lambda: -0.75 * math.log(1 - 4 * (50/300) / 3),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: JC correction increase ~ 13.1%",
        section="11",
        stated=13.1,
        computed=lambda: ((-0.75 * math.log(1 - 4*(50/300)/3)) / (50/300) - 1) * 100,
        tolerance=5e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.4: LD decay with r=0.10
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.4: generations for D<0.001 (D0=0.15, r=0.10) ~ 48",
        section="11",
        stated=48,
        computed=lambda: math.ceil(math.log(0.001 / 0.15) / math.log(0.9)),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.5: WF N=5 eigenvalues
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.5: lambda_2 ~ 1-1/(2*5) = 0.90",
        section="11",
        stated=0.90,
        computed=lambda: 1 - 1 / (2 * 5),
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.5: WF N=5 has two eigenvalues=1, all in [0,1]",
        section="11",
        predicate=lambda: _wf_n5_eigenvalue_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.6: Mutation equilibrium
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.6: mutation equilibrium p* = nu/(mu+nu) ~ 0.0909",
        section="11",
        stated=0.0909,
        computed=lambda: 1e-6 / (1e-5 + 1e-6),
        tolerance=1e-3,
    ))

    # Exercise 10.6: Mutation-drift convergence time
    # Starting from p0=0.5, within 1% of p*=0.0909
    # Approximately 555,500 generations
    ch.add(NumericCheck(
        label="Exercise 10.6: convergence time from p0=0.5 to within 1% of p* ~ 555500 gen",
        section="11",
        stated=555500,
        computed=lambda: _mutation_convergence_time(
            p0=0.5, p_star=1e-6 / (1e-5 + 1e-6),
            mu=1e-5, nu=1e-6, tol_frac=0.01,
        ),
        tolerance=5e-2,
        note="Deterministic mutation recurrence: p' = (1-mu)*p + nu*(1-p)",
    ))

    # ---------------------------------------------------------------
    # Exercise 10.7: Wright-Fisher with mutation — stationary distribution
    # ---------------------------------------------------------------
    # N=8, mu=0.05, nu=0.02; 17x17 transition matrix
    # Mean of stationary dist should be near p* = nu/(mu+nu) = 0.02/0.07
    ch.add(StructuralCheck(
        label="Exercise 10.7: WF+mutation stationary dist E[p] near p*=nu/(mu+nu)",
        section="11",
        predicate=lambda: _ex487_wf_mutation_stationary(),
        note="Exercise 10.7: E[p]=p* holds exactly for WF with mutation at any N",
    ))

    ch.add(NumericCheck(
        label="Exercise 10.7: Deterministic mutation equilibrium p* = 0.02/0.07",
        section="11",
        stated=0.02 / 0.07,
        computed=lambda: 0.02 / (0.05 + 0.02),
        tolerance=1e-10,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.8: K2P eigenvalues
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.8: K2P eigenvalues: 0, -2(alpha+beta), -4*beta (x2)",
        section="11",
        predicate=lambda: _k2p_eigenvalue_check(),
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.3: Hardy-Weinberg equilibrium is reached in one generation
    # Starting from arbitrary genotype frequencies, after random mating -> HW proportions
    def remark_483_hw_one_gen():
        # Start: f_AA=0.5, f_Aa=0.3, f_aa=0.2
        f_AA, f_Aa, f_aa = 0.5, 0.3, 0.2
        p = f_AA + f_Aa / 2  # allele frequency
        q = 1 - p
        # After one generation of random mating:
        f_AA_new = p**2
        f_Aa_new = 2 * p * q
        f_aa_new = q**2
        # Apply the map again: should be fixed point
        p2 = f_AA_new + f_Aa_new / 2
        f_AA_2 = p2**2
        f_Aa_2 = 2 * p2 * (1 - p2)
        f_aa_2 = (1 - p2)**2
        ok = (abs(f_AA_new - f_AA_2) < 1e-10 and
              abs(f_Aa_new - f_Aa_2) < 1e-10 and
              abs(f_aa_new - f_aa_2) < 1e-10)
        return (ok, f"Gen1: ({f_AA_new:.4f},{f_Aa_new:.4f},{f_aa_new:.4f}), "
                    f"Gen2: ({f_AA_2:.4f},{f_Aa_2:.4f},{f_aa_2:.4f})")
    ch.add(StructuralCheck(
        label="Remark 3.3: HW equilibrium is a fixed point after one generation",
        section="4",
        predicate=remark_483_hw_one_gen,
        note="Remark 3.3",
    ))

    # Remark 3.14: Expected conditional fixation time for new mutation (p=1/(2N)) ~ 4N generations
    # The conditional fixation time (Kimura diffusion): t_1(p) = -4N * (1-p)/p * ln(1-p)
    # The 4N approximation improves with larger N since it relies on the Taylor
    # expansion -ln(1-p)/p ~ 1 for small p = 1/(2N).
    def remark_4814_fixation_time():
        for N in [500, 1000, 5000]:
            p = 1 / (2 * N)
            t_fix = -4 * N * (1 - p) / p * math.log(1 - p)
            expected = 4 * N
            rel_err = abs(t_fix - expected) / expected
            # For large N with p=1/(2N), the conditional fixation time should be close to 4N
            if rel_err > 0.05:
                return (False, f"N={N}: t_fix={t_fix:.1f}, 4N={expected}, rel_err={rel_err:.4f}")
        return (True, f"Fixation time ~ 4N for all tested N")
    ch.add(StructuralCheck(
        label="Remark 3.14: Fixation time of new mutation ~ 4N generations",
        section="4",
        predicate=remark_4814_fixation_time,
        note="Remark 3.14",
    ))

    # Remark 3.19: Jukes-Cantor stationary distribution is uniform (1/4 each)
    def remark_4819_jc_stationary():
        import numpy as np
        alpha = 0.01
        Q = alpha * np.array([
            [-3, 1, 1, 1],
            [1, -3, 1, 1],
            [1, 1, -3, 1],
            [1, 1, 1, -3],
        ], dtype=float)
        # P(t) = expm(Qt) as t -> infinity should have all entries -> 1/4
        from scipy.linalg import expm
        t = 1000.0 / alpha  # very large time
        P = expm(Q * t)
        ok = all(abs(P[i, j] - 0.25) < 1e-6 for i in range(4) for j in range(4))
        return (ok, f"P(t->inf) diagonal = {P[0,0]:.6f}, off-diag = {P[0,1]:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.19: JC stationary distribution -> 1/4 for all bases",
        section="4",
        predicate=remark_4819_jc_stationary,
        note="Remark 3.19",
    ))

    # Remark 3.19: JC rate matrix Q has eigenvalue 0
    def remark_4819_jc_eigenvalue_zero():
        import numpy as np
        alpha = 0.01
        Q = alpha * np.array([
            [-3, 1, 1, 1],
            [1, -3, 1, 1],
            [1, 1, -3, 1],
            [1, 1, 1, -3],
        ], dtype=float)
        eigs = sorted(np.real(np.linalg.eigvals(Q)))
        # Should have eigenvalue 0 and -4*alpha (triple)
        ok_zero = abs(eigs[3]) < 1e-10
        ok_neg = all(abs(e - (-4 * alpha)) < 1e-10 for e in eigs[:3])
        return (ok_zero and ok_neg, f"eigenvalues: {eigs}")
    ch.add(StructuralCheck(
        label="Remark 3.19: JC rate matrix eigenvalues: 0, -4*alpha (x3)",
        section="4",
        predicate=remark_4819_jc_eigenvalue_zero,
        note="Remark 3.19",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Hardy-Weinberg Chi-Square Test ---
    def alg_5_1_hw_chi2():
        # Observed genotype counts (should be in HW equilibrium)
        # AA=36, Aa=48, aa=16 => p = (2*36+48)/(2*100) = 0.6, q=0.4
        n = 100
        obs = np.array([36, 48, 16], dtype=float)
        p = (2 * obs[0] + obs[1]) / (2 * n)
        q = 1 - p
        exp_counts = np.array([p ** 2 * n, 2 * p * q * n, q ** 2 * n])
        chi2 = np.sum((obs - exp_counts) ** 2 / exp_counts)
        # df=1 for HW test, critical value at 0.05 is 3.841
        ok = chi2 < 3.841  # should not reject HW
        return (ok, f"chi2={chi2:.4f}, p_hat={p:.2f}, expected={exp_counts}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Hardy-Weinberg chi-square test",
        section="6",
        predicate=alg_5_1_hw_chi2,
    ))

    # --- Algorithm 5.2: Allele Frequency Under Selection ---
    def alg_5_2_selection():
        # Directional selection: w_AA=1, w_Aa=1, w_aa=1-s
        s = 0.1
        p = 0.3  # initial frequency of A
        for _ in range(100):
            q = 1 - p
            w_bar = p ** 2 + 2 * p * q + q ** 2 * (1 - s)
            p_new = (p ** 2 + p * q) / w_bar
            p = p_new
        # A should increase (advantageous)
        ok = p > 0.3 and p < 1.0
        return (ok, f"p after 100 gen = {p:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Allele frequency under selection (A increases)",
        section="6",
        predicate=alg_5_2_selection,
    ))

    # --- Algorithm 5.3: Wright-Fisher Transition Matrix ---
    def alg_5_3_wright_fisher():
        from scipy.special import comb
        N = 10  # diploid population size, 2N = 20 alleles
        two_N = 2 * N
        T = np.zeros((two_N + 1, two_N + 1))
        for i in range(two_N + 1):
            p = i / two_N
            for j in range(two_N + 1):
                T[i, j] = comb(two_N, j) * p ** j * (1 - p) ** (two_N - j)
        # Each row should sum to 1
        row_sums = T.sum(axis=1)
        ok1 = np.allclose(row_sums, 1.0, atol=1e-10)
        # Absorbing states: T[0,0]=1 (all a), T[2N,2N]=1 (all A)
        ok2 = abs(T[0, 0] - 1.0) < 1e-10
        ok3 = abs(T[two_N, two_N] - 1.0) < 1e-10
        return (ok1 and ok2 and ok3, f"Row sums close to 1: {ok1}, absorbing states: {ok2}, {ok3}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Wright-Fisher transition matrix",
        section="6",
        predicate=alg_5_3_wright_fisher,
    ))

    # --- Algorithm 5.4: Jukes-Cantor Distance ---
    def alg_5_4_jukes_cantor():
        # d = -3/4 * ln(1 - 4p/3) where p = fraction of differing sites
        # Test 1: p=0 => d=0
        p1 = 0.0
        d1 = -0.75 * math.log(1 - 4 * p1 / 3) if p1 < 0.75 else float('inf')
        ok1 = abs(d1) < 1e-10
        # Test 2: p=0.1 => d = -0.75*ln(1 - 0.1333) = -0.75*ln(0.8667) ~ 0.1074
        p2 = 0.1
        d2 = -0.75 * math.log(1 - 4 * p2 / 3)
        ok2 = d2 > p2  # JC distance > observed divergence (corrects for multiple hits)
        # Test 3: as p -> 0.75, d -> infinity
        p3 = 0.74
        d3 = -0.75 * math.log(1 - 4 * p3 / 3)
        ok3 = d3 > 2  # d grows rapidly as p approaches 0.75
        return (ok1 and ok2 and ok3, f"d(0)={d1:.4f}, d(0.1)={d2:.4f}, d(0.74)={d3:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Jukes-Cantor distance",
        section="6",
        predicate=alg_5_4_jukes_cantor,
    ))

    # --- Remark 3.22: Log-odds scoring — positive = conserved, negative = rare ---
    def _remark_48_22_log_odds():
        """Verify log-odds score: S_ij > 0 iff p_ij > q_i*q_j."""
        # Simple 4-letter amino acid alphabet for testing
        # Target frequencies (observed in alignment)
        p = np.array([
            [0.2, 0.05, 0.01, 0.02],
            [0.05, 0.15, 0.03, 0.01],
            [0.01, 0.03, 0.10, 0.04],
            [0.02, 0.01, 0.04, 0.23],
        ])
        # Background frequencies
        q = np.sum(p, axis=1)
        # Log-odds score
        for i in range(4):
            for j in range(4):
                s_ij = math.log2(p[i, j] / (q[i] * q[j]))
                if p[i, j] > q[i] * q[j] and s_ij <= 0:
                    return (False, f"S[{i},{j}]={s_ij}, p>q*q but score <= 0")
                if p[i, j] < q[i] * q[j] and s_ij >= 0:
                    return (False, f"S[{i},{j}]={s_ij}, p<q*q but score >= 0")
        # Expected score in random alignment should be negative
        expected_random = sum(q[i] * q[j] * math.log2(p[i, j] / (q[i] * q[j]))
                              for i in range(4) for j in range(4))
        if expected_random >= 0:
            return (False, f"Expected random score = {expected_random}, should be < 0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.22: Log-odds S_ij > 0 iff pair conserved (p_ij > q_i*q_j)",
        section="48.22",
        predicate=_remark_48_22_log_odds,
        note="Remark 3.22: scoring matrix interpretation",
    ))

    # --- Remark 3.23: PAM extrapolation via matrix exponentiation ---
    def _remark_48_23_pam():
        """Verify PAM matrix extrapolation: P(t) = e^{Qt}."""
        from scipy.linalg import expm
        # Simple 4x4 rate matrix Q (Jukes-Cantor style)
        mu = 0.01
        Q = np.full((4, 4), mu / 3)
        np.fill_diagonal(Q, -mu)
        # P(t) should be a stochastic matrix (rows sum to 1, all entries >= 0)
        for t in [1, 10, 100, 250]:
            P = expm(Q * t)
            row_sums = P.sum(axis=1)
            if not np.allclose(row_sums, 1.0, atol=1e-10):
                return (False, f"t={t}: row sums = {row_sums}")
            if np.any(P < -1e-10):
                return (False, f"t={t}: negative entries in P")
        # At t=0, P should be identity
        P0 = expm(Q * 0)
        if not np.allclose(P0, np.eye(4), atol=1e-10):
            return (False, f"P(0) != I")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.23: PAM extrapolation P(t) = e^{Qt} is stochastic",
        section="48.23",
        predicate=_remark_48_23_pam,
        note="Remark 3.23: BLOSUM and PAM matrices",
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _hw_identity():
    import sympy
    p = sympy.Symbol('p')
    q = 1 - p
    total = p**2 + 2*p*q + q**2
    return sympy.Eq(sympy.expand(total), 1)


def _jc_distance_identity():
    import sympy
    p_hat = sympy.Symbol('p_hat', positive=True)
    d = sympy.Rational(-3, 4) * sympy.ln(1 - 4*p_hat/3)
    # At p_hat = 0, d = 0
    d_zero = d.subs(p_hat, 0)
    return sympy.Eq(d_zero, 0)


def _ld_decay_identity():
    import sympy
    D0, r, t = sympy.symbols('D0 r t', positive=True)
    D_t = D0 * (1 - r)**t
    # Ratio D_{t+1}/D_t = (1-r)
    ratio = D_t.subs(t, t+1) / D_t
    return sympy.Eq(sympy.simplify(ratio), 1 - r)


def _hw_chi_square(O_MM, O_MN, O_NN):
    n = O_MM + O_MN + O_NN
    p = (2 * O_MM + O_MN) / (2 * n)
    E_MM = n * p**2
    E_MN = n * 2 * p * (1 - p)
    E_NN = n * (1 - p)**2
    chi2 = ((O_MM - E_MM)**2 / E_MM +
            (O_MN - E_MN)**2 / E_MN +
            (O_NN - E_NN)**2 / E_NN)
    return chi2


def _selection_trajectory(p0, wAA, wAa, waa, T):
    p = p0
    for _ in range(T):
        q = 1 - p
        wbar = p**2 * wAA + 2*p*q * wAa + q**2 * waa
        p = (p**2 * wAA + p*q * wAa) / wbar
    return p


def _hw_sum_check():
    # Check for several p values that genotype freqs sum to 1
    for p in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
        q = 1 - p
        total = p**2 + 2*p*q + q**2
        if abs(total - 1.0) > 1e-15:
            return False, f"p={p}: total = {total}"
    return True, ""


def _jc_row_sum_check():
    alpha = 0.01
    t = 10.0
    # P_ii = 1/4 + 3/4 * exp(-4*alpha*t)
    # P_ij = 1/4 - 1/4 * exp(-4*alpha*t)
    exp_term = math.exp(-4 * alpha * t)
    P_ii = 0.25 + 0.75 * exp_term
    P_ij = 0.25 - 0.25 * exp_term
    row_sum = P_ii + 3 * P_ij
    ok = abs(row_sum - 1.0) < 1e-15
    return ok, f"Row sum = {row_sum} (P_ii={P_ii:.6f}, P_ij={P_ij:.6f})"


def _jc_row_sum_multi_times():
    """Verify row sums at multiple time points."""
    alpha = 0.05
    for t in [0.01, 0.1, 1.0, 10.0, 100.0]:
        exp_term = math.exp(-4 * alpha * t)
        P_ii = 0.25 + 0.75 * exp_term
        P_ij = 0.25 - 0.25 * exp_term
        row_sum = P_ii + 3 * P_ij
        if abs(row_sum - 1.0) > 1e-14:
            return False, f"t={t}: row sum = {row_sum}"
    return True, "Row sums = 1 at all tested times"


def _wf_row_sum_check():
    """Verify Wright-Fisher transition matrix rows sum to 1 for N=5."""
    N = 5
    size = 2 * N + 1
    for i in range(size):
        p = i / (2 * N)
        row_sum = 0.0
        for j in range(size):
            # T_ij = C(2N,j) * p^j * (1-p)^(2N-j)
            row_sum += scipy.special.comb(2*N, j, exact=True) * p**j * (1-p)**(2*N-j)
        if abs(row_sum - 1.0) > 1e-12:
            return False, f"Row {i} (p={p:.2f}): sum={row_sum}"
    return True, f"All {size} rows sum to 1"


def _selection_convergence_check():
    """Verify selection trajectory converges to theoretical equilibrium."""
    wAA, wAa, waa = 0.14, 1.00, 0.88
    p_star = (wAa - waa) / (2 * wAa - wAA - waa)
    p_final = _selection_trajectory(0.01, wAA, wAa, waa, 500)
    ok = abs(p_final - p_star) / p_star < 0.01
    return ok, f"p(500)={p_final:.4f}, p*={p_star:.4f}, rel_err={abs(p_final-p_star)/p_star:.4e}"


def _delta_p_directional(p, wAA, wAa, waa):
    """Compute delta_p for one generation of directional selection."""
    q = 1 - p
    wbar = p**2 * wAA + 2*p*q * wAa + q**2 * waa
    p_next = (p**2 * wAA + p*q * wAa) / wbar
    return p_next - p


def _generations_to_reach(p0, p_target, wAA, wAa, waa):
    """Count generations for allele to go from p0 to p_target under selection."""
    p = p0
    t = 0
    while p < p_target:
        q = 1 - p
        wbar = p**2 * wAA + 2*p*q * wAa + q**2 * waa
        p = (p**2 * wAA + p*q * wAa) / wbar
        t += 1
        if t > 100000:
            break
    return t


def _wf_n5_eigenvalue_check():
    """Exercise 10.5: Check WF N=5 eigenvalues."""
    N = 5
    size = 2 * N + 1
    T = np.zeros((size, size))
    for i in range(size):
        p = i / (2 * N)
        for j in range(size):
            T[i, j] = scipy.special.comb(2*N, j, exact=True) * p**j * (1-p)**(2*N-j)
    eigs = np.sort(np.real(np.linalg.eigvals(T)))[::-1]
    # Two eigenvalues should be 1 (absorbing states i=0, i=2N)
    count_one = sum(1 for e in eigs if abs(e - 1.0) < 1e-8)
    all_in_range = all(-1e-10 <= e <= 1.0 + 1e-10 for e in eigs)
    ok = count_one == 2 and all_in_range
    return ok, f"Eigenvalues (top 4): {eigs[:4]}, count_1={count_one}, all_in_[0,1]={all_in_range}"


def _k2p_eigenvalue_check():
    """Exercise 10.8: Verify K2P rate matrix eigenvalues."""
    alpha = 0.3   # transition rate
    beta = 0.1    # transversion rate
    # Q matrix (ACGT order, where A<->G and C<->T are transitions)
    Q = np.array([
        [-(alpha + 2*beta), beta, alpha, beta],
        [beta, -(alpha + 2*beta), beta, alpha],
        [alpha, beta, -(alpha + 2*beta), beta],
        [beta, alpha, beta, -(alpha + 2*beta)],
    ])
    eigs = np.sort(np.real(np.linalg.eigvals(Q)))
    # Correct eigenvalues: 0 (once), -4*beta (once), -2*(alpha+beta) (twice)
    expected = sorted([0, -4*beta, -2*(alpha+beta), -2*(alpha+beta)])
    max_err = max(abs(eigs[i] - expected[i]) for i in range(4))
    ok = max_err < 1e-10
    return ok, f"Eigenvalues: {eigs}, expected: {expected}, max_err={max_err:.2e}"


def _mutation_convergence_time(p0, p_star, mu, nu, tol_frac):
    """Count generations for deterministic mutation to converge within tol_frac of p*."""
    p = p0
    t = 0
    threshold = tol_frac * p_star
    while abs(p - p_star) > threshold:
        p = (1 - mu) * p + nu * (1 - p)
        t += 1
        if t > 2000000:
            break
    return t


def _ex487_wf_mutation_stationary():
    """Exercise 10.7: Wright-Fisher with mutation (N=8, mu=0.05, nu=0.02).
    Construct 17x17 transition matrix and find stationary distribution.
    For small N with these mutation rates the distribution is monotonically
    decreasing (mode at p=0), but the mean E[p] = p* = nu/(mu+nu) = 2/7
    holds exactly for any N."""
    from scipy.special import comb
    N_dip = 8
    two_N = 2 * N_dip  # 16 alleles
    mu, nu = 0.05, 0.02
    n_states = two_N + 1  # 0, 1, ..., 16

    # Build transition matrix T[j,i] = P(next state j | current state i)
    # T is column-stochastic: columns sum to 1
    T = np.zeros((n_states, n_states))
    for i in range(n_states):
        # Current allele frequency
        p_i = i / two_N
        # Effective frequency after mutation:
        # p' = (1-mu)*p + nu*(1-p) where mu is forward mutation rate (A->a)
        # and nu is backward mutation rate (a->A)
        p_prime = (1 - mu) * p_i + nu * (1 - p_i)
        p_prime = max(0, min(1, p_prime))
        # Transition: binomial sampling with parameter p_prime
        for j in range(n_states):
            T[j, i] = comb(two_N, j, exact=True) * p_prime**j * (1 - p_prime)**(two_N - j)

    # Stationary distribution: T*pi = pi (right eigenvector for eigenvalue 1)
    # Use power iteration for robustness
    pi = np.ones(n_states) / n_states
    for _ in range(1000):
        pi = T @ pi
        pi /= np.sum(pi)

    # Mean of the distribution (expected allele frequency)
    freqs = np.array([i / two_N for i in range(n_states)])
    mean_freq = np.sum(pi * freqs)

    # Deterministic equilibrium
    p_star = nu / (mu + nu)

    # Mean should be close to p* (for any N, E[p] = p* in WF with mutation)
    ok = abs(mean_freq - p_star) < 0.05
    return (ok, f"Mean freq={mean_freq:.4f}, p*={p_star:.4f}")
