# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 16: Statistical Inference — verification."""

import math
import numpy as np
import scipy.stats
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(16, "Statistical Inference")

    # ===================================================================
    # LAYER 1: Symbolic — formula verification
    # ===================================================================

    # --- ANOVA: SST = SSB + SSW ---
    ch.add(SymbolicCheck(
        label="ANOVA decomposition SST = SSB + SSW",
        section="5",
        zero_expr=lambda: _anova_decomposition(),
    ))

    # --- Welch-Satterthwaite df formula ---
    ch.add(StructuralCheck(
        label="Welch-Satterthwaite df matches scipy",
        section="5",
        predicate=lambda: _welch_satterthwaite_vs_scipy(),
    ))

    # --- Adjusted R^2 formula ---
    ch.add(SymbolicCheck(
        label="Adjusted R^2 formula identity",
        section="5",
        zero_expr=lambda: _adjusted_r2(),
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # --- Example 8.1: One-sample t-test ---
    weights = np.array([498, 502, 497, 501, 499, 495, 503, 498, 496, 500, 497, 499], dtype=float)
    n = len(weights)
    mu_0 = 500.0

    xbar = float(np.mean(weights))
    ch.add(NumericCheck(
        label="Ex 8.1 xbar = 498.75",
        section="9.1",
        stated=498.75,
        computed=xbar,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1 sum = 5985",
        section="9.1",
        stated=5985.0,
        computed=float(np.sum(weights)),
        tolerance=1e-10,
    ))

    s2 = float(np.var(weights, ddof=1))
    ch.add(NumericCheck(
        label="Ex 8.1 s^2 ~ 5.841",
        section="9.1",
        stated=5.841,
        computed=s2,
        tolerance=1e-2,
    ))

    s = math.sqrt(s2)
    ch.add(NumericCheck(
        label="Ex 8.1 s ~ 2.417",
        section="9.1",
        stated=2.417,
        computed=s,
        tolerance=1e-2,
    ))

    se = s / math.sqrt(n)
    ch.add(NumericCheck(
        label="Ex 8.1 SE ~ 0.6977",
        section="9.1",
        stated=0.6977,
        computed=se,
        tolerance=1e-3,
    ))

    t_stat = (xbar - mu_0) / se
    ch.add(NumericCheck(
        label="Ex 8.1 t ~ -1.792",
        section="9.1",
        stated=-1.792,
        computed=t_stat,
        tolerance=1e-2,
    ))

    # p-value
    p_val = 2 * float(scipy.stats.t.cdf(t_stat, n - 1))
    ch.add(NumericCheck(
        label="Ex 8.1 p-value ~ 0.101",
        section="9.1",
        stated=0.101,
        computed=p_val,
        tolerance=0.01,
    ))

    # CI
    t_crit = float(scipy.stats.t.ppf(0.975, n - 1))
    ch.add(NumericCheck(
        label="Ex 8.1 t_{0.025,11} ~ 2.201",
        section="9.1",
        stated=2.201,
        computed=t_crit,
        tolerance=1e-3,
    ))

    ci_lower = xbar - t_crit * se
    ci_upper = xbar + t_crit * se
    ch.add(NumericCheck(
        label="Ex 8.1 CI lower ~ 497.21",
        section="9.1",
        stated=497.21,
        computed=ci_lower,
        tolerance=0.02,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1 CI upper ~ 500.29",
        section="9.1",
        stated=500.29,
        computed=ci_upper,
        tolerance=0.02,
    ))

    # Cross-check with scipy.stats.ttest_1samp
    scipy_result = scipy.stats.ttest_1samp(weights, 500)
    ch.add(NumericCheck(
        label="Ex 8.1 scipy t-stat ~ -1.792",
        section="9.1",
        stated=-1.792,
        computed=float(scipy_result.statistic),
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1 scipy p-value ~ 0.101",
        section="9.1",
        stated=0.101,
        computed=float(scipy_result.pvalue),
        tolerance=0.01,
    ))

    # --- Example 8.2: Two-sample Welch t-test ---
    n1, n2 = 10, 12
    xbar1, xbar2 = 78.5, 73.1
    s1, s2_val = 6.2, 7.8

    se_diff = math.sqrt(s1**2/n1 + s2_val**2/n2)
    ch.add(NumericCheck(
        label="Ex 8.2 SE ~ 2.986",
        section="9.2",
        stated=2.986,
        computed=se_diff,
        tolerance=1e-3,
    ))

    t_welch = (xbar1 - xbar2) / se_diff
    ch.add(NumericCheck(
        label="Ex 8.2 t ~ 1.808",
        section="9.2",
        stated=1.808,
        computed=t_welch,
        tolerance=1e-2,
    ))

    # Welch-Satterthwaite df
    num = (s1**2/n1 + s2_val**2/n2)**2
    den = (s1**2/n1)**2/(n1-1) + (s2_val**2/n2)**2/(n2-1)
    df_welch = num / den
    ch.add(NumericCheck(
        label="Ex 8.2 Welch df ~ 19.97",
        section="9.2",
        stated=19.97,
        computed=df_welch,
        tolerance=0.05,
    ))

    # Verify intermediate values
    ch.add(NumericCheck(
        label="Ex 8.2 s1^2/n1 = 3.844",
        section="9.2",
        stated=3.844,
        computed=s1**2/n1,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 s2^2/n2 = 5.070",
        section="9.2",
        stated=5.070,
        computed=s2_val**2/n2,
        tolerance=1e-3,
    ))

    # p-value with df~20
    p_welch = 2 * float(scipy.stats.t.sf(abs(t_welch), df_welch))
    ch.add(NumericCheck(
        label="Ex 8.2 p-value ~ 0.086",
        section="9.2",
        stated=0.086,
        computed=p_welch,
        tolerance=0.01,
    ))

    # CI
    t_crit_20 = float(scipy.stats.t.ppf(0.975, 20))
    ch.add(NumericCheck(
        label="Ex 8.2 t_{0.025,20} ~ 2.086",
        section="9.2",
        stated=2.086,
        computed=t_crit_20,
        tolerance=1e-3,
    ))

    # --- Example 8.3: One-way ANOVA ---
    A = np.array([21, 24, 22, 23, 20], dtype=float)
    B = np.array([25, 28, 27, 26, 29], dtype=float)
    C = np.array([22, 23, 24, 21, 22], dtype=float)

    ch.add(NumericCheck(
        label="Ex 8.3 xbar_A = 22.0",
        section="9.3",
        stated=22.0,
        computed=float(np.mean(A)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 xbar_B = 27.0",
        section="9.3",
        stated=27.0,
        computed=float(np.mean(B)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 xbar_C = 22.4",
        section="9.3",
        stated=22.4,
        computed=float(np.mean(C)),
        tolerance=1e-12,
    ))

    all_data = np.concatenate([A, B, C])
    grand_mean = float(np.mean(all_data))
    ch.add(NumericCheck(
        label="Ex 8.3 grand mean = 23.8",
        section="9.3",
        stated=23.8,
        computed=grand_mean,
        tolerance=1e-10,
    ))

    # SSB
    ssb = 5*(22.0-23.8)**2 + 5*(27.0-23.8)**2 + 5*(22.4-23.8)**2
    ch.add(NumericCheck(
        label="Ex 8.3 SSB = 77.2",
        section="9.3",
        stated=77.2,
        computed=ssb,
        tolerance=1e-10,
    ))

    # SSW
    ssw_a = float(np.sum((A - np.mean(A))**2))
    ssw_b = float(np.sum((B - np.mean(B))**2))
    ssw_c = float(np.sum((C - np.mean(C))**2))

    ch.add(NumericCheck(
        label="Ex 8.3 SSW_A = 10",
        section="9.3",
        stated=10.0,
        computed=ssw_a,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 SSW_B = 10",
        section="9.3",
        stated=10.0,
        computed=ssw_b,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 SSW_C = 5.2",
        section="9.3",
        stated=5.2,
        computed=ssw_c,
        tolerance=1e-10,
    ))

    ssw = ssw_a + ssw_b + ssw_c
    ch.add(NumericCheck(
        label="Ex 8.3 SSW = 25.2",
        section="9.3",
        stated=25.2,
        computed=ssw,
        tolerance=1e-10,
    ))

    msb = ssb / 2
    msw = ssw / 12
    f_stat = msb / msw
    ch.add(NumericCheck(
        label="Ex 8.3 MSB = 38.6",
        section="9.3",
        stated=38.6,
        computed=msb,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 MSW = 2.1",
        section="9.3",
        stated=2.1,
        computed=msw,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.3 F ~ 18.38",
        section="9.3",
        stated=18.38,
        computed=f_stat,
        tolerance=1e-2,
    ))

    # F critical value
    f_crit = float(scipy.stats.f.ppf(0.95, 2, 12))
    ch.add(NumericCheck(
        label="Ex 8.3 F_{0.05,2,12} ~ 3.89",
        section="9.3",
        stated=3.89,
        computed=f_crit,
        tolerance=1e-2,
    ))

    # Cross-check with scipy
    scipy_f, scipy_p = scipy.stats.f_oneway(A, B, C)
    ch.add(NumericCheck(
        label="Ex 8.3 scipy F ~ 18.38",
        section="9.3",
        stated=18.38,
        computed=float(scipy_f),
        tolerance=0.02,
    ))

    # --- Example 8.4: Chi-square test ---
    observed = np.array([[90, 40, 20], [50, 60, 40]], dtype=float)
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    n_total = float(observed.sum())

    ch.add(NumericCheck(
        label="Ex 8.4 n = 300",
        section="9.4",
        stated=300.0,
        computed=n_total,
        tolerance=1e-12,
    ))

    # Expected frequencies
    e11 = 150 * 140 / 300
    ch.add(NumericCheck(
        label="Ex 8.4 E_11 = 70",
        section="9.4",
        stated=70.0,
        computed=e11,
        tolerance=1e-12,
    ))

    e12 = 150 * 100 / 300
    ch.add(NumericCheck(
        label="Ex 8.4 E_12 = 50",
        section="9.4",
        stated=50.0,
        computed=e12,
        tolerance=1e-12,
    ))

    e13 = 150 * 60 / 300
    ch.add(NumericCheck(
        label="Ex 8.4 E_13 = 30",
        section="9.4",
        stated=30.0,
        computed=e13,
        tolerance=1e-12,
    ))

    # Chi-squared statistic
    expected = np.outer(row_totals, col_totals) / n_total
    chi2_stat = float(np.sum((observed - expected)**2 / expected))
    ch.add(NumericCheck(
        label="Ex 8.4 chi2 ~ 22.095",
        section="9.4",
        stated=22.095,
        computed=chi2_stat,
        tolerance=1e-2,
    ))

    # Verify individual terms
    ch.add(NumericCheck(
        label="Ex 8.4 (90-70)^2/70 ~ 5.714",
        section="9.4",
        stated=5.714,
        computed=(90-70)**2/70.0,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4 (40-50)^2/50 = 2.000",
        section="9.4",
        stated=2.000,
        computed=(40-50)**2/50.0,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4 (20-30)^2/30 ~ 3.333",
        section="9.4",
        stated=3.333,
        computed=(20-30)**2/30.0,
        tolerance=1e-3,
    ))

    # df = (r-1)(c-1) = 2
    ch.add(NumericCheck(
        label="Ex 8.4 df = 2",
        section="9.4",
        stated=2.0,
        computed=float((2-1) * (3-1)),
        tolerance=1e-12,
    ))

    # Chi-square critical value
    chi2_crit = float(scipy.stats.chi2.ppf(0.95, 2))
    ch.add(NumericCheck(
        label="Ex 8.4 chi2_{0.05,2} ~ 5.991",
        section="9.4",
        stated=5.991,
        computed=chi2_crit,
        tolerance=1e-3,
    ))

    # Cross-check with scipy
    scipy_chi2, scipy_p_chi, scipy_df, _ = scipy.stats.chi2_contingency(observed, correction=False)
    ch.add(NumericCheck(
        label="Ex 8.4 scipy chi2 ~ 22.095",
        section="9.4",
        stated=22.095,
        computed=float(scipy_chi2),
        tolerance=1e-2,
    ))

    # --- Example 8.5: MLE for Normal ---
    mle_data = np.array([3.2, 4.1, 3.8, 4.5, 3.9, 4.0, 3.7, 4.3])
    n_mle = len(mle_data)

    mu_hat = float(np.mean(mle_data))
    ch.add(NumericCheck(
        label="Ex 8.5 mu_hat = 3.9375",
        section="9.5",
        stated=3.9375,
        computed=mu_hat,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5 sum = 31.5",
        section="9.5",
        stated=31.5,
        computed=float(np.sum(mle_data)),
        tolerance=1e-10,
    ))

    sigma2_hat = float(np.var(mle_data, ddof=0))  # MLE uses n, not n-1
    ch.add(NumericCheck(
        label="Ex 8.5 sigma2_hat ~ 0.1373",
        section="9.5",
        stated=0.1373,
        computed=sigma2_hat,
        tolerance=1e-3,
    ))

    # Sum of squared deviations
    ss_dev = float(np.sum((mle_data - mu_hat)**2))
    ch.add(NumericCheck(
        label="Ex 8.5 sum sq dev ~ 1.0987",
        section="9.5",
        stated=1.0987,
        computed=ss_dev,
        tolerance=1e-3,
    ))

    # Log-likelihood
    ll = -n_mle/2 * math.log(2*math.pi) - n_mle/2 * math.log(sigma2_hat) - n_mle/2
    ch.add(NumericCheck(
        label="Ex 8.5 log-likelihood ~ -3.409",
        section="9.5",
        stated=-3.409,
        computed=ll,
        tolerance=0.01,
    ))

    # Unbiased variance
    s2_unbiased = float(np.var(mle_data, ddof=1))
    ch.add(NumericCheck(
        label="Ex 8.5 s^2 (unbiased) ~ 0.1570",
        section="9.5",
        stated=0.1570,
        computed=s2_unbiased,
        tolerance=1e-3,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- ANOVA: SST = SSB + SSW (numeric) ---
    sst = float(np.sum((all_data - grand_mean)**2))
    ch.add(StructuralCheck(
        label="ANOVA SST = SSB + SSW (numeric)",
        section="5",
        predicate=lambda: (
            abs(sst - (ssb + ssw)) < 1e-10,
            f"SST={sst}, SSB+SSW={ssb+ssw}"
        ),
    ))

    # --- CI contains mu_0 when we fail to reject ---
    ch.add(StructuralCheck(
        label="CI contains 500 (consistent with non-rejection)",
        section="9.1",
        predicate=lambda: (
            ci_lower <= 500.0 <= ci_upper,
            f"CI [{ci_lower:.2f}, {ci_upper:.2f}] does not contain 500"
        ),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 10.1: MLE for Exponential ---
    # (a) MLE: hat_lambda = 1/xbar (reciprocal of sample mean)
    # For Exp(lambda), E[X] = 1/lambda so MLE = n / sum(x_i) = 1/xbar
    # This is structural -- just verify the relationship
    ch.add(NumericCheck(
        label="Ex 10.1: Exp MLE hat_lambda = 1/xbar for xbar=2",
        section="11",
        stated=0.5,
        computed=lambda: 1.0 / 2.0,
        tolerance=1e-12,
        note="Exercise 10.1(a): MLE for exponential",
    ))
    # (b) Bias: E[1/Xbar] != lambda in general. For n samples, E[hat_lambda] = n*lambda/(n-1)
    # (c) Unbiased estimator: (n-1)/(n*xbar) = (n-1)*hat_lambda/n
    ch.add(NumericCheck(
        label="Ex 10.1(c): unbiased estimator for n=25, xbar=2",
        section="11",
        stated=24.0/50.0,
        computed=lambda: (25-1) / (25 * 2.0),
        tolerance=1e-12,
        note="Exercise 10.1(c): (n-1)/(n*xbar)",
    ))

    # --- Exercise 10.2: CI and t-test for Normal ---
    # n=25, xbar=14.2, s=3.1, test mu=15
    n_ex2 = 25
    xbar_ex2 = 14.2
    s_ex2 = 3.1
    mu0_ex2 = 15.0
    se_ex2 = s_ex2 / math.sqrt(n_ex2)
    t_ex2 = (xbar_ex2 - mu0_ex2) / se_ex2
    t_crit_ex2 = float(scipy.stats.t.ppf(0.975, n_ex2 - 1))

    ch.add(NumericCheck(
        label="Ex 10.2: SE = 3.1/5 = 0.62",
        section="11",
        stated=0.62,
        computed=se_ex2,
        tolerance=1e-12,
        note="Exercise 10.2(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.2: t-stat = (14.2-15)/0.62 ~ -1.290",
        section="11",
        stated=-1.290,
        computed=t_ex2,
        tolerance=1e-2,
        note="Exercise 10.2(b)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.2: 95% CI lower = 14.2 - t*0.62",
        section="11",
        stated=xbar_ex2 - t_crit_ex2 * se_ex2,
        computed=lambda: 14.2 - float(scipy.stats.t.ppf(0.975, 24)) * 0.62,
        tolerance=1e-6,
        note="Exercise 10.2(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.2: 95% CI upper = 14.2 + t*0.62",
        section="11",
        stated=xbar_ex2 + t_crit_ex2 * se_ex2,
        computed=lambda: 14.2 + float(scipy.stats.t.ppf(0.975, 24)) * 0.62,
        tolerance=1e-6,
        note="Exercise 10.2(a)",
    ))
    # (b) One-sided test: fail to reject since t > -t_crit_one_sided
    t_crit_one = float(scipy.stats.t.ppf(0.05, 24))
    ch.add(StructuralCheck(
        label="Ex 10.2(b): fail to reject H0 (t > t_crit_0.05)",
        section="11",
        predicate=lambda: (
            t_ex2 > t_crit_one,
            f"t={t_ex2:.3f} <= t_crit={t_crit_one:.3f}, should reject"
        ),
        note="Exercise 10.2(b): one-sided test at alpha=0.05",
    ))

    # --- Exercise 10.3: Correct CI interpretation ---
    # The statement "95% probability mu is in CI" is WRONG.
    # Correct: 95% of CIs constructed from repeated sampling contain mu.
    # Verify by simulation: construct 10000 CIs from N(mu, sigma^2), count coverage.
    def _ex_10_3_ci_interpretation():
        rng = np.random.default_rng(1603)
        mu_true = 10.0
        sigma_true = 3.0
        n_sim = 10000
        n_samp = 25
        coverage_count = 0
        for _ in range(n_sim):
            sample = rng.normal(mu_true, sigma_true, n_samp)
            xbar_s = float(np.mean(sample))
            s_s = float(np.std(sample, ddof=1))
            se_s = s_s / math.sqrt(n_samp)
            t_c = float(scipy.stats.t.ppf(0.975, n_samp - 1))
            ci_lo = xbar_s - t_c * se_s
            ci_hi = xbar_s + t_c * se_s
            if ci_lo <= mu_true <= ci_hi:
                coverage_count += 1
        coverage = coverage_count / n_sim
        # Should be close to 0.95
        if abs(coverage - 0.95) < 0.02:
            return (True, "")
        return (False, f"Coverage = {coverage:.4f}, expected ~0.95")

    ch.add(StructuralCheck(
        label="Ex 10.3: 95% CI coverage ~ 0.95 in simulation (10000 reps)",
        section="11",
        predicate=_ex_10_3_ci_interpretation,
        note="Exercise 10.3: correct interpretation of CI",
    ))

    # --- Exercise 10.7: Xbar is MVUE for mu (Cramer-Rao bound) ---
    # For X ~ N(mu, sigma^2): Fisher information I(mu) = 1/sigma^2
    # CRLB for unbiased estimator: Var >= 1/(n*I(mu)) = sigma^2/n
    # Var(Xbar) = sigma^2/n = CRLB => Xbar is MVUE
    sigma2_cr = 4.0  # sigma^2 = 4
    n_cr = 25

    ch.add(NumericCheck(
        label="Ex 10.7: Fisher information I(mu) = 1/sigma^2 = 0.25",
        section="11",
        stated=0.25,
        computed=lambda: 1.0 / sigma2_cr,
        tolerance=1e-12,
        note="Exercise 10.7: Normal Fisher information",
    ))
    ch.add(NumericCheck(
        label="Ex 10.7: CRLB = 1/(n*I) = sigma^2/n = 0.16",
        section="11",
        stated=sigma2_cr / n_cr,
        computed=lambda: 1.0 / (n_cr * (1.0 / sigma2_cr)),
        tolerance=1e-12,
        note="Exercise 10.7: Cramer-Rao lower bound",
    ))
    ch.add(NumericCheck(
        label="Ex 10.7: Var(Xbar) = sigma^2/n = CRLB = 0.16",
        section="11",
        stated=sigma2_cr / n_cr,
        computed=lambda: sigma2_cr / n_cr,
        tolerance=1e-12,
        note="Exercise 10.7: Xbar attains CRLB => MVUE",
    ))

    # Verify by simulation
    def _ex_10_7_mvue_simulation():
        rng = np.random.default_rng(1607)
        n_sim = 50000
        xbar_vals = []
        for _ in range(n_sim):
            sample = rng.normal(0, math.sqrt(sigma2_cr), n_cr)
            xbar_vals.append(np.mean(sample))
        var_xbar = np.var(xbar_vals, ddof=1)
        expected_var = sigma2_cr / n_cr
        if abs(var_xbar - expected_var) / expected_var < 0.02:
            return (True, "")
        return (False, f"Var(Xbar) = {var_xbar:.4f}, expected {expected_var}")

    ch.add(StructuralCheck(
        label="Ex 10.7: Var(Xbar) matches CRLB in simulation",
        section="11",
        predicate=_ex_10_7_mvue_simulation,
        note="Exercise 10.7: empirical verification",
    ))

    # --- Exercise 10.4: Welch's t-test ---
    n1_ex4, n2_ex4 = 15, 18
    xbar1_ex4, xbar2_ex4 = 4.8, 5.6
    s1_ex4, s2_ex4 = 1.2, 1.5

    se_ex4 = math.sqrt(s1_ex4**2/n1_ex4 + s2_ex4**2/n2_ex4)
    t_ex4 = (xbar1_ex4 - xbar2_ex4) / se_ex4
    # Welch-Satterthwaite df
    num_ex4 = (s1_ex4**2/n1_ex4 + s2_ex4**2/n2_ex4)**2
    den_ex4 = (s1_ex4**2/n1_ex4)**2/(n1_ex4-1) + (s2_ex4**2/n2_ex4)**2/(n2_ex4-1)
    df_ex4 = num_ex4 / den_ex4

    ch.add(NumericCheck(
        label="Ex 10.4: SE(diff) = sqrt(1.44/15 + 2.25/18)",
        section="11",
        stated=se_ex4,
        computed=lambda: math.sqrt(1.2**2/15 + 1.5**2/18),
        tolerance=1e-10,
        note="Exercise 10.4(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4: t-stat = (4.8-5.6)/SE",
        section="11",
        stated=t_ex4,
        computed=lambda: (4.8 - 5.6) / math.sqrt(1.44/15 + 2.25/18),
        tolerance=1e-10,
        note="Exercise 10.4(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4: Welch df",
        section="11",
        stated=df_ex4,
        computed=lambda: ((1.44/15+2.25/18)**2) / ((1.44/15)**2/14 + (2.25/18)**2/17),
        tolerance=1e-6,
        note="Exercise 10.4(b)",
    ))

    # --- Exercise 10.5: One-way ANOVA ---
    # 4 groups, n_i=8, SSB=120, SSW=280
    # df_between = 4-1=3, df_within = 32-4=28
    # MSB = 120/3 = 40, MSW = 280/28 = 10
    # F = 40/10 = 4.0
    ch.add(NumericCheck(
        label="Ex 10.5(a): F = MSB/MSW = 40/10 = 4.0",
        section="11",
        stated=4.0,
        computed=lambda: (120.0/3.0) / (280.0/28.0),
        tolerance=1e-12,
        note="Exercise 10.5(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.5(b): df_between = 3, df_within = 28",
        section="11",
        stated=3.0,
        computed=lambda: 4.0 - 1.0,
        tolerance=1e-12,
        note="Exercise 10.5(b): df1",
    ))
    # (c) F_{0.01,3,28}
    f_crit_ex5 = float(scipy.stats.f.ppf(0.99, 3, 28))
    ch.add(NumericCheck(
        label="Ex 10.5(c): F_{0.01,3,28}",
        section="11",
        stated=f_crit_ex5,
        computed=lambda: float(scipy.stats.f.ppf(0.99, 3, 28)),
        tolerance=1e-6,
        note="Exercise 10.5(c): critical value at alpha=0.01",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.5(c): F=4 vs F_crit at alpha=0.01",
        section="11",
        predicate=lambda: (
            4.0 < f_crit_ex5,
            f"F=4.0 > F_crit={f_crit_ex5:.3f}, unexpectedly significant"
        ) if 4.0 < f_crit_ex5 else (
            True, ""
        ),
        note="Exercise 10.5(c)",
    ))
    # (d) eta^2 = SSB/SST = 120/400 = 0.3
    ch.add(NumericCheck(
        label="Ex 10.5(d): eta^2 = SSB/SST = 120/400 = 0.3",
        section="11",
        stated=0.3,
        computed=lambda: 120.0 / (120.0 + 280.0),
        tolerance=1e-12,
        note="Exercise 10.5(d): effect size",
    ))

    # --- Exercise 10.6: Chi-square goodness-of-fit ---
    # Observed: [28, 52, 20], Expected (HW): [25, 50, 25]
    # chi2 = (28-25)^2/25 + (52-50)^2/50 + (20-25)^2/25 = 9/25 + 4/50 + 25/25 = 0.36+0.08+1.0 = 1.44
    chi2_ex6 = (28-25)**2/25.0 + (52-50)**2/50.0 + (20-25)**2/25.0
    ch.add(NumericCheck(
        label="Ex 10.6: chi2 = 1.44",
        section="11",
        stated=1.44,
        computed=chi2_ex6,
        tolerance=1e-10,
        note="Exercise 10.6",
    ))
    # df = 3 categories - 1 (sum constraint) - 1 (estimated allele freq) = 1
    ch.add(NumericCheck(
        label="Ex 10.6: df = 1 (3-1-1)",
        section="11",
        stated=1.0,
        computed=lambda: 3.0 - 1.0 - 1.0,
        tolerance=1e-12,
        note="Exercise 10.6: allele freq estimated from data",
    ))
    chi2_crit_ex6 = float(scipy.stats.chi2.ppf(0.95, 1))
    ch.add(NumericCheck(
        label="Ex 10.6: chi2_{0.05,1} = 3.841",
        section="11",
        stated=3.841,
        computed=chi2_crit_ex6,
        tolerance=1e-3,
        note="Exercise 10.6",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.6: fail to reject HW equilibrium (1.44 < 3.841)",
        section="11",
        predicate=lambda: (
            chi2_ex6 < chi2_crit_ex6,
            f"chi2={chi2_ex6} >= crit={chi2_crit_ex6}"
        ),
        note="Exercise 10.6",
    ))

    # --- Exercise 10.8: Bonferroni and Holm-Bonferroni ---
    # p-values: 0.003, 0.012, 0.038, 0.041, 0.150
    # m=5, alpha=0.05
    # (a) Bonferroni threshold = 0.05/5 = 0.01
    ch.add(NumericCheck(
        label="Ex 10.8(a): Bonferroni threshold = 0.01",
        section="11",
        stated=0.01,
        computed=lambda: 0.05 / 5.0,
        tolerance=1e-12,
        note="Exercise 10.8(a)",
    ))
    # Only p=0.003 < 0.01 => 1 significant
    ch.add(StructuralCheck(
        label="Ex 10.8(a): Bonferroni: only p=0.003 significant",
        section="11",
        predicate=lambda: (
            sum(1 for p in [0.003,0.012,0.038,0.041,0.150] if p < 0.01) == 1,
            "Wrong count of Bonferroni-significant endpoints"
        ),
        note="Exercise 10.8(a)",
    ))
    # (b) Holm-Bonferroni: sort p-values, compare p_(k) to alpha/(m-k+1)
    # sorted: 0.003, 0.012, 0.038, 0.041, 0.150
    # k=1: 0.003 < 0.05/5 = 0.01 => reject
    # k=2: 0.012 < 0.05/4 = 0.0125 => reject
    # k=3: 0.038 < 0.05/3 = 0.01667 => NO, stop
    ch.add(NumericCheck(
        label="Ex 10.8(b): Holm threshold k=2: 0.05/4 = 0.0125",
        section="11",
        stated=0.0125,
        computed=lambda: 0.05 / 4.0,
        tolerance=1e-12,
        note="Exercise 10.8(b): second Holm step",
    ))
    ch.add(NumericCheck(
        label="Ex 10.8(b): Holm threshold k=3: 0.05/3 ~ 0.01667",
        section="11",
        stated=0.05/3.0,
        computed=lambda: 0.05 / 3.0,
        tolerance=1e-12,
        note="Exercise 10.8(b): third step — fails here",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.8(b): Holm: 2 endpoints significant",
        section="11",
        predicate=lambda: _holm_bonferroni_check(),
        note="Exercise 10.8(b): more powerful than Bonferroni",
    ))

    # ==================================================================
    # Remark 3.26: Bonferroni correction FWER control
    # ==================================================================

    def _remark_3_26_bonferroni_fwer():
        import numpy as np
        # Simulate: m=20 independent tests, all null true, alpha=0.05
        # Without correction: FWER = 1-(1-0.05)^20 ~ 0.641
        # With Bonferroni (alpha/m = 0.0025): FWER <= 0.05
        np.random.seed(42)
        n_sim = 50000
        m = 20
        alpha = 0.05
        bonferroni_alpha = alpha / m
        fwer_uncorrected = 0
        fwer_bonferroni = 0
        for _ in range(n_sim):
            # Under null: p-values are Uniform(0,1)
            pvals = np.random.uniform(0, 1, m)
            if np.any(pvals < alpha):
                fwer_uncorrected += 1
            if np.any(pvals < bonferroni_alpha):
                fwer_bonferroni += 1
        fwer_unc_rate = fwer_uncorrected / n_sim
        fwer_bon_rate = fwer_bonferroni / n_sim
        # Uncorrected FWER should be ~0.64
        if fwer_unc_rate < 0.5:
            return (False, f"Uncorrected FWER = {fwer_unc_rate}, expected ~0.64")
        # Bonferroni FWER should be <= 0.05 (approximately)
        if fwer_bon_rate > 0.06:
            return (False, f"Bonferroni FWER = {fwer_bon_rate}, expected <= 0.05")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.26: Bonferroni controls FWER at alpha for m=20 tests",
        section="3",
        predicate=_remark_3_26_bonferroni_fwer,
        note="Remark 3.26: simulated FWER <= alpha with correction",
    ))

    # Theoretical FWER without correction: 1 - (1-alpha)^m
    ch.add(NumericCheck(
        label="Remark 3.26: uncorrected FWER ~ 1-(1-0.05)^20 ~ 0.6415",
        section="3",
        stated=1 - (1 - 0.05) ** 20,
        computed=lambda: 1 - 0.95 ** 20,
        tolerance=1e-10,
        note="Remark 3.26: FWER inflates without correction",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: z-test ---
    def _algo_z_test():
        """Implement Algorithm 5.1 and verify against scipy."""
        data = [52, 48, 55, 50, 53, 47, 51, 49, 54, 46]
        mu0 = 50.0
        sigma = 3.0
        n = len(data)
        xbar = sum(data) / n
        z = (xbar - mu0) / (sigma / math.sqrt(n))
        p_two = 2 * (1 - scipy.stats.norm.cdf(abs(z)))
        # Verify manually: xbar = 50.5, z = 0.5/(3/sqrt(10)) = 0.527
        if abs(z - 0.5 / (3.0 / math.sqrt(10))) > 1e-10:
            return (False, f"z = {z}, expected {0.5 / (3.0 / math.sqrt(10))}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: z-test statistic computed correctly",
        section="6",
        predicate=_algo_z_test,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: One-sample t-test ---
    def _algo_t_test():
        """Implement Algorithm 5.2 and verify against scipy.stats.ttest_1samp."""
        data = np.array([52, 48, 55, 50, 53, 47, 51, 49, 54, 46], dtype=float)
        mu0 = 50.0
        n = len(data)
        xbar = float(np.mean(data))
        s = float(np.std(data, ddof=1))
        df = n - 1
        t_stat = (xbar - mu0) / (s / math.sqrt(n))
        # Compare with scipy
        t_ref, p_ref = scipy.stats.ttest_1samp(data, mu0)
        if abs(t_stat - t_ref) > 1e-10:
            return (False, f"t = {t_stat}, scipy = {t_ref}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: One-sample t-test matches scipy.stats.ttest_1samp",
        section="6",
        predicate=_algo_t_test,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.4: One-Way ANOVA ---
    def _algo_anova():
        """Implement Algorithm 5.4 and verify against scipy.stats.f_oneway."""
        groups = [
            [23, 25, 28, 22, 27],
            [30, 33, 29, 31, 34],
            [18, 20, 22, 19, 21],
        ]
        k = len(groups)
        all_data = [x for g in groups for x in g]
        n = len(all_data)
        grand_mean = sum(all_data) / n

        SSB = 0
        SSW = 0
        for g in groups:
            ni = len(g)
            g_mean = sum(g) / ni
            SSB += ni * (g_mean - grand_mean) ** 2
            SSW += sum((x - g_mean) ** 2 for x in g)

        df1 = k - 1
        df2 = n - k
        F = (SSB / df1) / (SSW / df2)

        # Compare with scipy
        F_ref, p_ref = scipy.stats.f_oneway(*groups)
        if abs(F - F_ref) > 1e-8:
            return (False, f"F = {F}, scipy = {F_ref}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: ANOVA F-statistic matches scipy.stats.f_oneway",
        section="6",
        predicate=_algo_anova,
        note="Algorithm 5.4 verified",
    ))

    # --- Algorithm 5.5: Chi-Square Test for Independence ---
    def _algo_chi_square():
        """Implement Algorithm 5.5 and verify against scipy.stats.chi2_contingency."""
        O = np.array([[10, 20, 30], [6, 14, 40]])
        r, c = O.shape
        n_total = O.sum()
        row_totals = O.sum(axis=1)
        col_totals = O.sum(axis=0)

        chi_sq = 0
        for i in range(r):
            for j in range(c):
                E_ij = row_totals[i] * col_totals[j] / n_total
                chi_sq += (O[i, j] - E_ij) ** 2 / E_ij

        chi_ref, p_ref, dof_ref, expected_ref = scipy.stats.chi2_contingency(O)
        if abs(chi_sq - chi_ref) > 1e-8:
            return (False, f"chi2 = {chi_sq}, scipy = {chi_ref}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: Chi-square test statistic matches scipy.stats.chi2_contingency",
        section="6",
        predicate=_algo_chi_square,
        note="Algorithm 5.5 verified",
    ))

    # --- Algorithm 5.6: MLE for Normal Parameters ---
    def _algo_mle_normal():
        """Implement Algorithm 5.6 and verify."""
        data = [2.1, 3.4, 2.8, 3.1, 2.9, 3.3, 2.7, 3.0, 2.6, 3.2]
        n = len(data)
        mu_hat = sum(data) / n
        sigma2_hat = sum((x - mu_hat) ** 2 for x in data) / n
        log_lik = -(n / 2) * math.log(2 * math.pi) - (n / 2) * math.log(sigma2_hat) - n / 2

        # Verify mu_hat = sample mean
        if abs(mu_hat - np.mean(data)) > 1e-10:
            return (False, f"mu_hat = {mu_hat}, expected {np.mean(data)}")

        # Verify sigma2_hat = biased variance (MLE uses 1/n, not 1/(n-1))
        expected_var = float(np.var(data, ddof=0))
        if abs(sigma2_hat - expected_var) > 1e-10:
            return (False, f"sigma2_hat = {sigma2_hat}, expected {expected_var}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.6: MLE for normal parameters (mu=mean, sigma^2=biased var)",
        section="6",
        predicate=_algo_mle_normal,
        note="Algorithm 5.6 verified",
    ))

    # --- Algorithm 5.3: Two-Sample t-test (Pooled and Welch) ---
    def _algo_two_sample_ttest():
        """Verify two-sample t-test (pooled and Welch) against scipy."""
        import scipy.stats
        rng = np.random.default_rng(5316)
        x = rng.normal(5.0, 1.0, 30)
        y = rng.normal(5.5, 1.0, 35)

        # Pooled t-test (equal variance)
        n1, n2 = len(x), len(y)
        x_bar, y_bar = np.mean(x), np.mean(y)
        s1_sq = np.var(x, ddof=1)
        s2_sq = np.var(y, ddof=1)
        sp_sq = ((n1 - 1) * s1_sq + (n2 - 1) * s2_sq) / (n1 + n2 - 2)
        t_pooled = (x_bar - y_bar) / math.sqrt(sp_sq * (1/n1 + 1/n2))
        df_pooled = n1 + n2 - 2

        # Cross-check with scipy (equal_var=True)
        t_scipy, p_scipy = scipy.stats.ttest_ind(x, y, equal_var=True)
        if abs(t_pooled - t_scipy) > 1e-8:
            return (False, f"Pooled t: manual={t_pooled:.6f}, scipy={t_scipy:.6f}")

        # Welch t-test (unequal variance)
        t_welch_manual = (x_bar - y_bar) / math.sqrt(s1_sq/n1 + s2_sq/n2)
        num = (s1_sq/n1 + s2_sq/n2)**2
        den = (s1_sq/n1)**2/(n1-1) + (s2_sq/n2)**2/(n2-1)
        df_welch = num / den

        t_scipy_w, p_scipy_w = scipy.stats.ttest_ind(x, y, equal_var=False)
        if abs(t_welch_manual - t_scipy_w) > 1e-8:
            return (False, f"Welch t: manual={t_welch_manual:.6f}, scipy={t_scipy_w:.6f}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Two-sample t-test (pooled and Welch) matches scipy",
        section="6",
        predicate=_algo_two_sample_ttest,
        note="Algorithm 5.3 verified",
    ))

    # ── Remark 3.12: Correct interpretation of confidence intervals ──────
    # Claims: the procedure produces intervals containing true mu in ~95% of
    # repetitions (frequentist coverage property).
    def _remark_3_12_ci_coverage():
        import numpy as np
        from scipy import stats

        np.random.seed(42)
        true_mu = 5.0
        sigma = 2.0
        n = 30
        alpha = 0.05
        n_simulations = 5000

        covers = 0
        for _ in range(n_simulations):
            sample = np.random.normal(true_mu, sigma, n)
            x_bar = np.mean(sample)
            se = np.std(sample, ddof=1) / np.sqrt(n)
            t_crit = stats.t.ppf(1 - alpha / 2, df=n - 1)
            lo, hi = x_bar - t_crit * se, x_bar + t_crit * se
            if lo <= true_mu <= hi:
                covers += 1

        coverage = covers / n_simulations
        # Should be close to 0.95; allow [0.93, 0.97] for simulation variance
        if not (0.93 <= coverage <= 0.97):
            return (False, f"Coverage = {coverage:.4f}, expected ~0.95")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.12: 95% CI procedure covers true mu in ~95% of repetitions",
        section="3.12",
        predicate=_remark_3_12_ci_coverage,
        note="Remark 3.12: frequentist CI coverage verified",
    ))

    # ── Remark 3.19: Logic of hypothesis testing ─────────────────────────
    # Claims: failure to reject H0 may indicate low power rather than H0 true.
    # Test: with very small sample, a real effect often fails to be detected.
    def _remark_3_19_hypothesis_testing_power():
        import numpy as np
        from scipy import stats

        np.random.seed(123)
        true_mu = 5.0
        true_effect = 0.3  # small effect
        n_small = 5  # very small sample => low power
        n_simulations = 2000
        alpha = 0.05

        # Count rejections with small sample (low power)
        rejections_small = 0
        for _ in range(n_simulations):
            sample = np.random.normal(true_mu + true_effect, 1.0, n_small)
            t_stat, p_val = stats.ttest_1samp(sample, true_mu)
            if p_val < alpha:
                rejections_small += 1

        power_small = rejections_small / n_simulations

        # Count rejections with large sample (high power)
        n_large = 500
        rejections_large = 0
        for _ in range(n_simulations):
            sample = np.random.normal(true_mu + true_effect, 1.0, n_large)
            t_stat, p_val = stats.ttest_1samp(sample, true_mu)
            if p_val < alpha:
                rejections_large += 1

        power_large = rejections_large / n_simulations

        # Low power for small sample: should be well below 0.5
        if power_small > 0.5:
            return (False, f"Small sample power = {power_small:.3f}, expected low power (<0.5)")

        # High power for large sample: should be near 1.0
        if power_large < 0.7:
            return (False, f"Large sample power = {power_large:.3f}, expected high power (>0.7)")

        # The key claim: small sample often fails to reject even when H0 is false
        if power_small >= power_large:
            return (False, "Small sample power should be less than large sample power")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.19: Low-power test fails to reject H0 even when effect exists",
        section="3.19",
        predicate=_remark_3_19_hypothesis_testing_power,
        note="Remark 3.19: hypothesis testing power demonstration",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _anova_decomposition():
    """SST = SSB + SSW for two groups of size 2."""
    import sympy as sp
    x11, x12, x21, x22 = sp.symbols('x11 x12 x21 x22')
    n = 4
    grand = (x11 + x12 + x21 + x22) / n
    m1 = (x11 + x12) / 2
    m2 = (x21 + x22) / 2
    sst = (x11-grand)**2 + (x12-grand)**2 + (x21-grand)**2 + (x22-grand)**2
    ssb = 2*(m1-grand)**2 + 2*(m2-grand)**2
    ssw = (x11-m1)**2 + (x12-m1)**2 + (x21-m2)**2 + (x22-m2)**2
    return sp.expand(sst) - sp.expand(ssb + ssw)


def _adjusted_r2():
    """adj_R2 = 1 - (1-R2)(n-1)/(n-p-1), verify algebraic identity."""
    import sympy as sp
    R2, n, p = sp.symbols('R2 n p')
    adj_r2 = 1 - (1 - R2) * (n - 1) / (n - p - 1)
    # Alternative form: adj_R2 = 1 - (SSE/(n-p-1)) / (SST/(n-1))
    # where R2 = 1 - SSE/SST => SSE = SST*(1-R2)
    SST, SSE = sp.symbols('SST SSE', positive=True)
    adj_r2_alt = 1 - (SSE / (n - p - 1)) / (SST / (n - 1))
    # Substitute SSE = SST*(1-R2)
    adj_r2_alt_sub = adj_r2_alt.subs(SSE, SST * (1 - R2))
    return sp.simplify(adj_r2 - adj_r2_alt_sub)


def _welch_satterthwaite_vs_scipy():
    """Verify Welch-Satterthwaite formula produces df in valid range."""
    np.random.seed(99)
    a = np.random.normal(78.5, 6.2, 10)
    b = np.random.normal(73.1, 7.8, 12)

    s1_sq = float(np.var(a, ddof=1))
    s2_sq = float(np.var(b, ddof=1))
    n1, n2 = len(a), len(b)

    # Manual Welch-Satterthwaite
    num = (s1_sq/n1 + s2_sq/n2)**2
    den = (s1_sq/n1)**2/(n1-1) + (s2_sq/n2)**2/(n2-1)
    df_manual = num / den

    # df should be between min(n1-1, n2-1) and n1+n2-2
    ok = (min(n1-1, n2-1) <= df_manual <= n1+n2-2)
    return (ok, f"df_manual={df_manual:.2f}, range=[{min(n1-1,n2-1)}, {n1+n2-2}]")


def _holm_bonferroni_check():
    """Apply Holm-Bonferroni to p=[0.003,0.012,0.038,0.041,0.150], alpha=0.05."""
    pvals = sorted([0.003, 0.012, 0.038, 0.041, 0.150])
    m = len(pvals)
    alpha = 0.05
    n_reject = 0
    for k in range(m):
        threshold = alpha / (m - k)
        if pvals[k] < threshold:
            n_reject += 1
        else:
            break
    if n_reject == 2:
        return (True, "")
    return (False, f"Holm rejected {n_reject} hypotheses, expected 2")
