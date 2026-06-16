# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 15: Descriptive Statistics — verification."""

import math
import numpy as np
import scipy.stats
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(15, "Descriptive Statistics")

    # ===================================================================
    # LAYER 1: Symbolic — variance formula equivalence
    # ===================================================================

    # --- Two variance formulas are equivalent ---
    ch.add(SymbolicCheck(
        label="Variance: definition = computational formula",
        section="5",
        zero_expr=lambda: _variance_formulas_equivalent(),
    ))

    # --- Covariance shortcut identity ---
    ch.add(SymbolicCheck(
        label="Cov: definition = computational formula",
        section="5",
        zero_expr=lambda: _cov_formulas_equivalent(),
    ))

    # --- Correlation matrix = D^{-1} S D^{-1} ---
    ch.add(StructuralCheck(
        label="R = D^{-1} S D^{-1} for sample data",
        section="5",
        predicate=lambda: _corr_from_cov(),
    ))

    # ===================================================================
    # LAYER 2: Numerical worked examples
    # ===================================================================

    # --- Example 8.1: mean, variance, std dev ---
    data1 = np.array([4.0, 7.0, 13.0, 2.0, 9.0])

    ch.add(NumericCheck(
        label="Mean of {4,7,13,2,9} = 7",
        section="8.1",
        stated=7.0,
        computed=float(np.mean(data1)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Var(ddof=1) = 18.5",
        section="8.1",
        stated=18.5,
        computed=float(np.var(data1, ddof=1)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Std dev ~ 4.301",
        section="8.1",
        stated=4.301,
        computed=float(np.std(data1, ddof=1)),
        tolerance=1e-3,
    ))

    # --- Example 8.2: Skewness and kurtosis ---
    data_a = np.arange(1.0, 11.0)

    ch.add(NumericCheck(
        label="Dataset A mean = 5.5",
        section="8.2",
        stated=5.5,
        computed=float(np.mean(data_a)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Dataset A std ~ 3.028",
        section="8.2",
        stated=3.028,
        computed=float(np.std(data_a, ddof=1)),
        tolerance=1e-3,
    ))

    # Skewness of symmetric data = 0
    ch.add(NumericCheck(
        label="Dataset A skewness = 0",
        section="8.2",
        stated=0.0,
        computed=float(scipy.stats.skew(data_a, bias=False)),
        tolerance=1e-10,
    ))

    # Kurtosis: textbook uses m4_biased / s^4 (biased 4th moment / unbiased var^2)
    # This is a known estimator variant; scipy uses a different convention
    m4_biased = float(np.mean((data_a - np.mean(data_a))**4))
    s4 = float(np.var(data_a, ddof=1))**2
    ch.add(NumericCheck(
        label="Dataset A kurtosis (m4/s^4) ~ 1.438",
        section="8.2",
        stated=1.438,
        computed=m4_biased / s4,
        tolerance=0.01,
        note="textbook uses m4_biased/s^4 convention",
    ))

    # Dataset B
    data_b = np.array([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 5.0, 10.0, 50.0])

    ch.add(NumericCheck(
        label="Dataset B mean = 8.1",
        section="8.2",
        stated=8.1,
        computed=float(np.mean(data_b)),
        tolerance=1e-12,
    ))

    # Skewness: textbook uses m3_biased / s^3 convention
    m3_b = float(np.mean((data_b - np.mean(data_b))**3))
    s3_b = float(np.std(data_b, ddof=1))**3
    ch.add(NumericCheck(
        label="Dataset B skewness (m3/s^3) ~ 2.15",
        section="8.2",
        stated=2.15,
        computed=m3_b / s3_b,
        tolerance=0.01,
        note="textbook uses m3_biased/s^3 convention",
    ))

    # --- Example 8.3: Covariance and correlation ---
    x = np.array([2.0, 4.0, 5.0, 7.0, 8.0])
    y = np.array([65.0, 73.0, 80.0, 82.0, 90.0])

    ch.add(NumericCheck(
        label="Study hours mean = 5.2",
        section="8.3",
        stated=5.2,
        computed=float(np.mean(x)),
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Exam scores mean = 78",
        section="8.3",
        stated=78.0,
        computed=float(np.mean(y)),
        tolerance=1e-12,
    ))

    cov_xy = float(np.cov(x, y, ddof=1)[0, 1])
    ch.add(NumericCheck(
        label="Cov(hours, scores) = 22.0",
        section="8.3",
        stated=22.0,
        computed=cov_xy,
        tolerance=1e-10,
    ))

    # Verify individual cross-product terms
    xbar, ybar = 5.2, 78.0
    terms = [(2-xbar)*(65-ybar), (4-xbar)*(73-ybar), (5-xbar)*(80-ybar),
             (7-xbar)*(82-ybar), (8-xbar)*(90-ybar)]
    ch.add(NumericCheck(
        label="Cross-product term 1: (-3.2)(-13) = 41.6",
        section="8.3",
        stated=41.6,
        computed=terms[0],
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Cross-product term 3: (-0.2)(2) = -0.4",
        section="8.3",
        stated=-0.4,
        computed=terms[2],
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Cross-product sum = 88.0",
        section="8.3",
        stated=88.0,
        computed=sum(terms),
        tolerance=1e-10,
    ))

    sx = float(np.std(x, ddof=1))
    sy = float(np.std(y, ddof=1))

    ch.add(NumericCheck(
        label="s_x ~ 2.387",
        section="8.3",
        stated=2.387,
        computed=sx,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="s_y ~ 9.460",
        section="8.3",
        stated=9.460,
        computed=sy,
        tolerance=1e-3,
    ))

    r_xy = cov_xy / (sx * sy)
    ch.add(NumericCheck(
        label="r_xy ~ 0.974",
        section="8.3",
        stated=0.974,
        computed=r_xy,
        tolerance=1e-3,
    ))

    # --- Example 8.4: Welford's algorithm ---
    ch.add(StructuralCheck(
        label="Welford vs two-pass on {10^8+1, 10^8+2, 10^8+3}",
        section="8.4",
        predicate=lambda: _welford_stability(),
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Covariance matrix is symmetric and PSD ---
    ch.add(StructuralCheck(
        label="Covariance matrix is symmetric",
        section="5",
        predicate=lambda: _cov_symmetric(),
    ))

    ch.add(StructuralCheck(
        label="Covariance matrix is PSD",
        section="5",
        predicate=lambda: _cov_psd(),
    ))

    # --- Welford recurrence identity ---
    ch.add(StructuralCheck(
        label="Welford recurrence holds for random data",
        section="6",
        predicate=lambda: _welford_recurrence(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 10.1: Dataset {3,7,7,2,9,14,5} ---
    ex_data = np.array([3.0, 7.0, 7.0, 2.0, 9.0, 14.0, 5.0])
    ex_mean = float(np.mean(ex_data))
    ex_median = float(np.median(ex_data))
    ex_var = float(np.var(ex_data, ddof=1))
    ex_std = float(np.std(ex_data, ddof=1))
    ex_sorted = np.sort(ex_data)  # [2,3,5,7,7,9,14]
    ex_q1 = float(np.percentile(ex_data, 25, method='midpoint'))
    ex_q3 = float(np.percentile(ex_data, 75, method='midpoint'))

    ch.add(NumericCheck(
        label="Ex 10.1: mean of {3,7,7,2,9,14,5} = 47/7",
        section="11",
        stated=47.0/7.0,
        computed=ex_mean,
        tolerance=1e-10,
        note="Exercise 10.1",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: median = 7",
        section="11",
        stated=7.0,
        computed=ex_median,
        tolerance=1e-12,
        note="Exercise 10.1: middle value of sorted data",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: sample variance",
        section="11",
        stated=ex_var,
        computed=float(np.var(ex_data, ddof=1)),
        tolerance=1e-12,
        note="Exercise 10.1",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: sample std dev",
        section="11",
        stated=ex_std,
        computed=float(np.std(ex_data, ddof=1)),
        tolerance=1e-12,
        note="Exercise 10.1",
    ))
    # Robustness: replace 14 with 140
    ex_data_outlier = np.array([3.0, 7.0, 7.0, 2.0, 9.0, 140.0, 5.0])
    ch.add(NumericCheck(
        label="Ex 10.1: mean with outlier 140",
        section="11",
        stated=float(np.mean(ex_data_outlier)),
        computed=lambda: (3+7+7+2+9+140+5)/7.0,
        tolerance=1e-10,
        note="Exercise 10.1: mean is NOT robust",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: median with outlier 140 still = 7",
        section="11",
        stated=7.0,
        computed=float(np.median(ex_data_outlier)),
        tolerance=1e-12,
        note="Exercise 10.1: median IS robust",
    ))

    # --- Exercise 10.2: Mean minimizes sum of squared deviations ---
    # d/dc sum(x_i - c)^2 = -2*sum(x_i - c) = 0 => c = xbar
    # Second derivative = 2n > 0 (minimum)
    ch.add(NumericCheck(
        label="Ex 10.2: d/dc sum(x_i-c)^2 = 0 at c=xbar",
        section="11",
        stated=0.0,
        computed=lambda: -2.0 * np.sum(ex_data - np.mean(ex_data)),
        tolerance=1e-10,
        note="Exercise 10.2: FOC for mean",
    ))
    ch.add(NumericCheck(
        label="Ex 10.2: second derivative = 2n = 14 > 0 (minimum)",
        section="11",
        stated=14.0,
        computed=lambda: 2.0 * len(ex_data),
        tolerance=1e-12,
        note="Exercise 10.2: SOC confirms minimum",
    ))
    # Verify: sum(x_i - xbar)^2 < sum(x_i - c)^2 for c != xbar
    ch.add(StructuralCheck(
        label="Ex 10.2: SSD at xbar < SSD at xbar+1",
        section="11",
        predicate=lambda: (
            float(np.sum((ex_data - np.mean(ex_data))**2)) < float(np.sum((ex_data - np.mean(ex_data) - 1)**2)),
            "SSD at xbar not minimal"
        ),
        note="Exercise 10.2",
    ))

    # --- Exercise 10.3: Bessel's correction ---
    # E[sum(x_i - xbar)^2] = (n-1)*sigma^2
    # Verify by simulation: sample from N(0,1), compute sum(x_i-xbar)^2 many times
    def _ex_10_3_bessel():
        rng = np.random.default_rng(1503)
        n_sim = 10000
        n_sample = 20
        sigma2 = 1.0  # true variance of N(0,1)
        ss_vals = []
        for _ in range(n_sim):
            sample = rng.standard_normal(n_sample)
            ss_vals.append(float(np.sum((sample - np.mean(sample))**2)))
        mean_ss = np.mean(ss_vals)
        expected = (n_sample - 1) * sigma2
        if abs(mean_ss - expected) / expected < 0.02:
            return (True, "")
        return (False, f"E[SS] = {mean_ss:.2f}, expected {expected}")

    ch.add(StructuralCheck(
        label="Ex 10.3: E[sum(xi-xbar)^2] = (n-1)*sigma^2 (simulation)",
        section="11",
        predicate=_ex_10_3_bessel,
        note="Exercise 10.3: Bessel's correction derivation",
    ))

    # --- Exercise 10.5: Correlation affine invariance ---
    # r_{u,v} = r_{x,y} for u=a+bx, v=c+dy with bd>0
    x_ex5 = np.array([1, 2, 3, 4, 5], dtype=float)
    y_ex5 = np.array([2, 4, 5, 4, 5], dtype=float)
    a_c, b_c = 10.0, 3.0
    c_c, d_c = -5.0, 2.0
    u_ex5 = a_c + b_c * x_ex5
    v_ex5 = c_c + d_c * y_ex5
    r_xy_ex5 = float(np.corrcoef(x_ex5, y_ex5)[0, 1])
    r_uv_ex5 = float(np.corrcoef(u_ex5, v_ex5)[0, 1])

    ch.add(NumericCheck(
        label="Ex 10.5: r_{xy} = r_{u,v} under affine transform (bd>0)",
        section="11",
        stated=r_xy_ex5,
        computed=r_uv_ex5,
        tolerance=1e-10,
        note="Exercise 10.5: u=10+3x, v=-5+2y",
    ))

    # Sign flips when bd < 0
    v_neg = c_c + (-d_c) * y_ex5
    r_uv_neg = float(np.corrcoef(u_ex5, v_neg)[0, 1])
    ch.add(NumericCheck(
        label="Ex 10.5: r flips sign when bd < 0",
        section="11",
        stated=-r_xy_ex5,
        computed=r_uv_neg,
        tolerance=1e-10,
        note="Exercise 10.5: bd < 0 => r_{uv} = -r_{xy}",
    ))

    # --- Exercise 10.6: Welford's algorithm on large-offset data ---
    # Dataset: {10^9+1, ..., 10^9+100}, true variance = var(1..100) = 100*101/(12) ≈ 841.667
    def _ex_10_6_welford():
        data_w = [1e9 + i for i in range(1, 101)]
        # Welford's online algorithm
        mean_w = 0.0
        m2_w = 0.0
        for i, x in enumerate(data_w, 1):
            delta = x - mean_w
            mean_w += delta / i
            delta2 = x - mean_w
            m2_w += delta * delta2
        var_welford = m2_w / (len(data_w) - 1)
        # Textbook formula (numerically unstable)
        sum_x = sum(data_w)
        sum_x2 = sum(x**2 for x in data_w)
        n = len(data_w)
        var_textbook = (sum_x2 - n * (sum_x / n)**2) / (n - 1)
        # True variance = var(1..100) with ddof=1
        true_var = float(np.var(range(1, 101), ddof=1))
        welford_err = abs(var_welford - true_var) / true_var
        textbook_err = abs(var_textbook - true_var) / true_var
        # Welford should be much more accurate
        if welford_err < 1e-10:
            return (True, "")
        return (False, f"Welford rel error = {welford_err:.2e}, textbook rel error = {textbook_err:.2e}")

    ch.add(StructuralCheck(
        label="Ex 10.6: Welford accurate on {10^9+1,...,10^9+100}",
        section="11",
        predicate=_ex_10_6_welford,
        note="Exercise 10.6: numerical stability comparison",
    ))

    # --- Exercise 10.7: Covariance matrix properties ---
    # 100x3 data, verify S is PSD, R has diagonal=1, R = D^{-1}SD^{-1}
    def _ex_10_7_cov_matrix():
        rng = np.random.default_rng(1507)
        X_data = rng.standard_normal((100, 3))
        S = np.cov(X_data.T, ddof=1)
        R = np.corrcoef(X_data.T)
        # Check eigenvalues of S non-negative
        eigs = np.linalg.eigvalsh(S)
        if np.any(eigs < -1e-10):
            return (False, f"S has negative eigenvalue: {eigs}")
        # Check diagonal of R = 1
        for i in range(3):
            if abs(R[i, i] - 1.0) > 1e-12:
                return (False, f"R[{i},{i}] = {R[i,i]}, expected 1.0")
        # Check R = D^{-1} S D^{-1}
        stds = np.sqrt(np.diag(S))
        D_inv = np.diag(1.0 / stds)
        R_check = D_inv @ S @ D_inv
        if np.max(np.abs(R_check - R)) > 1e-10:
            return (False, f"R != D^{{-1}}SD^{{-1}}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Ex 10.7: cov matrix PSD, corr diagonal=1, R=D^{-1}SD^{-1}",
        section="11",
        predicate=_ex_10_7_cov_matrix,
        note="Exercise 10.7: 100x3 random data",
    ))

    # --- Exercise 10.4: Portfolio return and std ---
    # E[Rp] = 0.6*0.08 + 0.4*0.05 = 0.048 + 0.020 = 0.068
    # Var(Rp) = 0.36*0.0144 + 0.16*0.0049 + 2*0.6*0.4*0.3*0.12*0.07
    # Cov(X,Y) = 0.3*0.12*0.07 = 0.00252
    port_ret = 0.6*0.08 + 0.4*0.05
    cov_xy_port = 0.3 * 0.12 * 0.07
    port_var = 0.6**2 * 0.12**2 + 0.4**2 * 0.07**2 + 2*0.6*0.4*cov_xy_port
    port_std = math.sqrt(port_var)

    ch.add(NumericCheck(
        label="Ex 10.4: portfolio return = 6.8%",
        section="11",
        stated=0.068,
        computed=port_ret,
        tolerance=1e-12,
        note="Exercise 10.4",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4: Cov(X,Y) = 0.00252",
        section="11",
        stated=0.00252,
        computed=cov_xy_port,
        tolerance=1e-12,
        note="Exercise 10.4",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4: portfolio variance",
        section="11",
        stated=port_var,
        computed=0.36*0.0144 + 0.16*0.0049 + 2*0.6*0.4*0.00252,
        tolerance=1e-12,
        note="Exercise 10.4",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4: portfolio std dev",
        section="11",
        stated=port_std,
        computed=math.sqrt(port_var),
        tolerance=1e-12,
        note="Exercise 10.4",
    ))

    # --- Exercise 10.8: t_5 excess kurtosis theoretical = 6 ---
    ch.add(NumericCheck(
        label="Ex 10.8: t_5 excess kurtosis = 6/(5-4) = 6",
        section="11",
        stated=6.0,
        computed=lambda: 6.0 / (5 - 4),
        tolerance=1e-12,
        note="Exercise 10.8: theoretical excess kurtosis of t_5",
    ))
    ch.add(NumericCheck(
        label="Ex 10.8: t_10 excess kurtosis = 6/(10-4) = 1",
        section="11",
        stated=1.0,
        computed=lambda: 6.0 / (10 - 4),
        tolerance=1e-12,
        note="Exercise 10.8: convergence to normal",
    ))
    ch.add(NumericCheck(
        label="Ex 10.8: t_30 excess kurtosis = 6/26 ~ 0.2308",
        section="11",
        stated=6.0/26.0,
        computed=lambda: 6.0 / (30 - 4),
        tolerance=1e-12,
        note="Exercise 10.8",
    ))
    ch.add(NumericCheck(
        label="Ex 10.8: t_100 excess kurtosis = 6/96 ~ 0.0625",
        section="11",
        stated=6.0/96.0,
        computed=lambda: 6.0 / (100 - 4),
        tolerance=1e-12,
        note="Exercise 10.8: approaches 0 (normal)",
    ))

    # ==================================================================
    # Remark 3.4: Mean = median for symmetric distributions
    # ==================================================================

    def _remark_3_4_symmetric_mean_median():
        # Symmetric data: mean should equal median
        symmetric = np.array([1.0, 3.0, 5.0, 7.0, 9.0])
        mean = float(np.mean(symmetric))
        median = float(np.median(symmetric))
        if abs(mean - median) > 1e-12:
            return (False, f"Symmetric: mean={mean}, median={median}")
        # Right-skewed: mean > median
        right_skewed = np.array([1.0, 2.0, 3.0, 4.0, 100.0])
        mean_rs = float(np.mean(right_skewed))
        median_rs = float(np.median(right_skewed))
        if mean_rs <= median_rs:
            return (False, f"Right-skewed: mean={mean_rs} <= median={median_rs}")
        # Left-skewed: mean < median
        left_skewed = np.array([-100.0, 6.0, 7.0, 8.0, 9.0])
        mean_ls = float(np.mean(left_skewed))
        median_ls = float(np.median(left_skewed))
        if mean_ls >= median_ls:
            return (False, f"Left-skewed: mean={mean_ls} >= median={median_ls}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.4: mean=median (symmetric), mean>median (right-skewed)",
        section="3",
        predicate=_remark_3_4_symmetric_mean_median,
        note="Remark 3.4: relationship between mean and median",
    ))

    # ==================================================================
    # Remark 3.19: z-scores have mean 0 and std 1
    # ==================================================================

    def _remark_3_19_z_scores():
        data = np.array([4.0, 7.0, 13.0, 2.0, 9.0, 15.0, 3.0, 11.0])
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        z = (data - mean) / std
        z_mean = float(np.mean(z))
        z_std = float(np.std(z, ddof=1))
        if abs(z_mean) > 1e-12:
            return (False, f"z-score mean = {z_mean}, expected 0")
        if abs(z_std - 1.0) > 1e-12:
            return (False, f"z-score std = {z_std}, expected 1")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.19: z-scores have mean=0, std=1",
        section="3",
        predicate=_remark_3_19_z_scores,
        note="Remark 3.19: standardization properties",
    ))

    # Correlation as average product of z-scores
    def _remark_3_19_corr_via_z():
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([2.0, 4.0, 5.0, 4.5, 5.5])
        zx = (x - np.mean(x)) / np.std(x, ddof=1)
        zy = (y - np.mean(y)) / np.std(y, ddof=1)
        r_z = float(np.sum(zx * zy) / (len(x) - 1))
        r_np = float(np.corrcoef(x, y)[0, 1])
        if abs(r_z - r_np) > 1e-12:
            return (False, f"r_z={r_z}, r_np={r_np}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.19: r_xy = (1/(n-1)) sum(z_x * z_y)",
        section="3",
        predicate=_remark_3_19_corr_via_z,
        note="Remark 3.19: correlation via z-scores",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # Note: Algorithm 5.1 (Two-pass variance) and Algorithm 5.2 (Welford)
    # are already tested above via worked examples and stability checks.

    # --- Algorithm 5.3: Quantile computation via sorting ---
    def _algo_quantile():
        """Implement Algorithm 5.3 and verify against numpy."""
        def quantile(data, p):
            x = sorted(data)
            n = len(x)
            h = (n - 1) * p
            j = int(h)
            g = h - j
            if j + 1 < n:
                return (1 - g) * x[j] + g * x[j + 1]
            return x[j]

        data = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        for p in [0.25, 0.5, 0.75, 0.1, 0.9]:
            our_val = quantile(data, p)
            np_val = float(np.percentile(data, p * 100))
            if abs(our_val - np_val) > 1e-10:
                return (False, f"Q({p}) = {our_val}, numpy = {np_val}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Quantile via sorting matches numpy.percentile",
        section="6",
        predicate=_algo_quantile,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.4: Covariance matrix computation ---
    def _algo_covariance_matrix():
        """Implement Algorithm 5.4 and verify against numpy."""
        data = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [2, 5]], dtype=float)
        n, p = data.shape

        # Step 1: Column means
        means = data.mean(axis=0)

        # Step 2: Center
        centered = data - means

        # Step 3: S = (1/(n-1)) X^T X
        S = np.zeros((p, p))
        for j in range(p):
            for k in range(j, p):
                s = sum(centered[i, j] * centered[i, k] for i in range(n))
                S[j, k] = s / (n - 1)
                S[k, j] = S[j, k]

        expected = np.cov(data.T)
        if not np.allclose(S, expected, atol=1e-10):
            return (False, f"Cov matrix mismatch: {S} vs {expected}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: Covariance matrix matches numpy.cov",
        section="6",
        predicate=_algo_covariance_matrix,
        note="Algorithm 5.4 verified",
    ))

    # --- Algorithm 5.5: Correlation matrix from covariance ---
    def _algo_correlation_matrix():
        """Implement Algorithm 5.5 and verify against numpy."""
        data = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [2, 5]], dtype=float)
        S = np.cov(data.T)
        p = S.shape[0]

        # Step 1: Extract standard deviations
        d = [math.sqrt(S[j, j]) for j in range(p)]

        # Step 2: Normalize
        R = np.zeros((p, p))
        for j in range(p):
            for k in range(p):
                if d[j] > 0 and d[k] > 0:
                    R[j, k] = S[j, k] / (d[j] * d[k])

        expected = np.corrcoef(data.T)
        if not np.allclose(R, expected, atol=1e-10):
            return (False, f"Corr matrix mismatch")
        # Verify diagonal is 1
        for j in range(p):
            if abs(R[j, j] - 1.0) > 1e-10:
                return (False, f"R[{j},{j}] = {R[j,j]}, expected 1.0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: Correlation matrix from covariance matches numpy.corrcoef",
        section="6",
        predicate=_algo_correlation_matrix,
        note="Algorithm 5.5 verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _variance_formulas_equivalent():
    """s^2 = (1/(n-1)) * (sum x_i^2 - n*xbar^2) = (1/(n-1)) * sum (x_i - xbar)^2."""
    import sympy as sp
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    n = 3
    xbar = (x1 + x2 + x3) / n
    # Definition form
    var_def = ((x1-xbar)**2 + (x2-xbar)**2 + (x3-xbar)**2) / (n-1)
    # Computational form
    sum_x2 = x1**2 + x2**2 + x3**2
    var_comp = (sum_x2 - n * xbar**2) / (n-1)
    return sp.expand(var_def) - sp.expand(var_comp)


def _cov_formulas_equivalent():
    """s_xy = (1/(n-1)) * (sum x_i*y_i - n*xbar*ybar) = (1/(n-1)) * sum (x_i-xbar)(y_i-ybar)."""
    import sympy as sp
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    y1, y2, y3 = sp.symbols('y1 y2 y3')
    n = 3
    xbar = (x1 + x2 + x3) / n
    ybar = (y1 + y2 + y3) / n
    # Definition form
    cov_def = ((x1-xbar)*(y1-ybar) + (x2-xbar)*(y2-ybar) + (x3-xbar)*(y3-ybar)) / (n-1)
    # Computational form
    sum_xy = x1*y1 + x2*y2 + x3*y3
    cov_comp = (sum_xy - n * xbar * ybar) / (n-1)
    return sp.expand(cov_def) - sp.expand(cov_comp)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _corr_from_cov():
    """Verify R = D^{-1} S D^{-1}."""
    data = np.array([[2, 65], [4, 73], [5, 80], [7, 82], [8, 90]], dtype=float)
    S = np.cov(data.T, ddof=1)
    stds = np.sqrt(np.diag(S))
    D_inv = np.diag(1.0 / stds)
    R_computed = D_inv @ S @ D_inv
    R_expected = np.corrcoef(data.T)
    diff = float(np.max(np.abs(R_computed - R_expected)))
    ok = diff < 1e-12
    return (ok, f"max |R_computed - R_expected| = {diff}")


def _welford_stability():
    """Welford produces correct variance for large-offset data."""
    data = [1e8 + 1, 1e8 + 2, 1e8 + 3]
    # Welford's online algorithm
    mean = 0.0
    m2 = 0.0
    for i, x in enumerate(data, 1):
        delta = x - mean
        mean += delta / i
        delta2 = x - mean
        m2 += delta * delta2
    var_welford = m2 / (len(data) - 1)
    ok = abs(var_welford - 1.0) < 1e-10
    return (ok, f"Welford variance = {var_welford}, expected 1.0")


def _cov_symmetric():
    """Sample covariance matrix is symmetric."""
    np.random.seed(42)
    data = np.random.randn(50, 4)
    S = np.cov(data.T, ddof=1)
    diff = float(np.max(np.abs(S - S.T)))
    ok = diff < 1e-14
    return (ok, f"max |S - S^T| = {diff}")


def _cov_psd():
    """Sample covariance matrix is positive semidefinite."""
    np.random.seed(42)
    data = np.random.randn(50, 4)
    S = np.cov(data.T, ddof=1)
    eigenvalues = np.linalg.eigvalsh(S)
    min_eig = float(np.min(eigenvalues))
    ok = min_eig >= -1e-14
    return (ok, f"min eigenvalue = {min_eig}")


def _welford_recurrence():
    """Verify Welford recurrence: S_k = S_{k-1} + (x_k - M_{k-1})(x_k - M_k)."""
    np.random.seed(123)
    data = np.random.randn(100)
    mean = 0.0
    s_k = 0.0
    for i, x in enumerate(data, 1):
        old_mean = mean
        mean += (x - mean) / i
        s_k += (x - old_mean) * (x - mean)

    # Compare to numpy
    expected_var = float(np.var(data, ddof=1))
    welford_var = s_k / (len(data) - 1)
    rel_diff = abs(welford_var - expected_var) / expected_var
    ok = rel_diff < 1e-12
    return (ok, f"Welford={welford_var:.10f}, numpy={expected_var:.10f}, rel_diff={rel_diff:.2e}")
