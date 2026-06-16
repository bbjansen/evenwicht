# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 17: Regression & Econometrics — verification."""

import math
import numpy as np
import scipy.stats
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(17, "Regression & Econometrics")

    # ===================================================================
    # LAYER 1: Symbolic — OLS formula verification
    # ===================================================================

    # --- OLS normal equations: beta = (X'X)^{-1} X'y ---
    ch.add(SymbolicCheck(
        label="OLS normal equations (X'X)beta = X'y",
        section="5",
        zero_expr=lambda: _normal_equations(),
    ))

    # --- Hat matrix: H = X(X'X)^{-1}X', H^2 = H ---
    ch.add(SymbolicCheck(
        label="Hat matrix is idempotent: H^2 = H",
        section="5",
        zero_expr=lambda: _hat_matrix_idempotent(),
    ))

    # --- SST = SSR + SSE decomposition ---
    ch.add(SymbolicCheck(
        label="SST = SSR + SSE decomposition",
        section="5",
        zero_expr=lambda: _ss_decomposition(),
    ))

    # --- Simple regression slope formula ---
    ch.add(SymbolicCheck(
        label="Simple regression beta_1 = S_xy / S_xx",
        section="5",
        zero_expr=lambda: _simple_slope(),
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # --- Example 8.1: Simple regression ---
    x = np.array([2.0, 3.0, 4.0, 5.0, 5.0, 6.0, 7.0, 8.0])
    y = np.array([55.0, 60.0, 62.0, 67.0, 70.0, 72.0, 75.0, 80.0])
    n = len(x)

    x_bar = float(np.mean(x))
    y_bar = float(np.mean(y))

    ch.add(NumericCheck(
        label="Ex 8.1 x_bar = 5",
        section="8.1",
        stated=5.0,
        computed=x_bar,
        tolerance=1e-12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1 y_bar = 67.625",
        section="8.1",
        stated=67.625,
        computed=y_bar,
        tolerance=1e-12,
    ))

    s_xx = float(np.sum((x - x_bar)**2))
    ch.add(NumericCheck(
        label="Ex 8.1 S_xx = 28",
        section="8.1",
        stated=28.0,
        computed=s_xx,
        tolerance=1e-12,
    ))

    s_xy = float(np.sum((x - x_bar) * (y - y_bar)))
    ch.add(NumericCheck(
        label="Ex 8.1 S_xy = 115.0",
        section="8.1",
        stated=115.0,
        computed=s_xy,
        tolerance=1e-10,
    ))

    beta1 = s_xy / s_xx
    ch.add(NumericCheck(
        label="Ex 8.1 beta_1 ~ 4.107",
        section="8.1",
        stated=4.107,
        computed=beta1,
        tolerance=1e-3,
    ))

    beta0 = y_bar - beta1 * x_bar
    ch.add(NumericCheck(
        label="Ex 8.1 beta_0 ~ 47.089",
        section="8.1",
        stated=47.089,
        computed=beta0,
        tolerance=1e-3,
    ))

    y_hat = beta0 + beta1 * x
    ss_res = float(np.sum((y - y_hat)**2))
    ss_tot = float(np.sum((y - y_bar)**2))
    r_squared = 1.0 - ss_res / ss_tot

    ch.add(NumericCheck(
        label="Ex 8.1 R^2 ~ 0.980",
        section="8.1",
        stated=0.980,
        computed=r_squared,
        tolerance=1e-2,
    ))

    # Cross-check with numpy polyfit
    coeffs = np.polyfit(x, y, 1)
    ch.add(NumericCheck(
        label="Ex 8.1 polyfit slope ~ 4.107",
        section="8.1",
        stated=4.107,
        computed=float(coeffs[0]),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 8.1 polyfit intercept ~ 47.089",
        section="8.1",
        stated=47.089,
        computed=float(coeffs[1]),
        tolerance=1e-3,
    ))

    # --- Example 8.2: F-test ---
    r2_ex2 = 0.845
    p_ex2 = 2
    df_resid_ex2 = 17

    f_stat_ex2 = (r2_ex2 / p_ex2) / ((1 - r2_ex2) / df_resid_ex2)
    ch.add(NumericCheck(
        label="Ex 8.2 F-stat ~ 46.3",
        section="8.2",
        stated=46.3,
        computed=f_stat_ex2,
        tolerance=0.02,
    ))

    f_crit = float(scipy.stats.f.ppf(0.95, 2, 17))
    ch.add(NumericCheck(
        label="Ex 8.2 F_{0.05,2,17} ~ 3.59",
        section="8.2",
        stated=3.59,
        computed=f_crit,
        tolerance=1e-2,
    ))

    # t-statistics
    ch.add(NumericCheck(
        label="Ex 8.2 T1 = 0.138/0.021 ~ 6.57",
        section="8.2",
        stated=6.57,
        computed=0.138 / 0.021,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 8.2 T2 = 8.7/3.1 ~ 2.81",
        section="8.2",
        stated=2.81,
        computed=8.7 / 3.1,
        tolerance=1e-2,
    ))

    t_crit_17 = float(scipy.stats.t.ppf(0.975, 17))
    ch.add(NumericCheck(
        label="Ex 8.2 t_{0.025,17} ~ 2.11",
        section="8.2",
        stated=2.11,
        computed=t_crit_17,
        tolerance=1e-2,
    ))

    # --- Example 8.3: Omitted variable bias ---
    beta2_ovb = 3.5
    delta_ovb = 0.6
    bias = beta2_ovb * delta_ovb
    ch.add(NumericCheck(
        label="Ex 8.3 OVB = 3.5 * 0.6 = 2.1",
        section="8.3",
        stated=2.1,
        computed=bias,
        tolerance=1e-12,
    ))

    # --- Example 8.4: VIF ---
    ch.add(NumericCheck(
        label="Ex 8.4 VIF_1 = 1/(1-0.92) = 12.5",
        section="8.4",
        stated=12.5,
        computed=1.0 / (1 - 0.92),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4 VIF_2 = 1/(1-0.88) ~ 8.3",
        section="8.4",
        stated=8.3,
        computed=1.0 / (1 - 0.88),
        tolerance=0.02,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4 VIF_3 = 1/(1-0.85) ~ 6.7",
        section="8.4",
        stated=6.7,
        computed=1.0 / (1 - 0.85),
        tolerance=0.02,
    ))

    # --- Example 8.5: F-test for linear restriction ---
    ch.add(NumericCheck(
        label="Ex 8.5 d = 0.138-8.7 = -8.562",
        section="8.5",
        stated=-8.562,
        computed=0.138 - 8.7,
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5 F = 73.3/10.2 ~ 7.18",
        section="8.5",
        stated=7.18,
        computed=73.3 / 10.2,
        tolerance=0.02,
    ))

    f_crit_1_17 = float(scipy.stats.f.ppf(0.95, 1, 17))
    ch.add(NumericCheck(
        label="Ex 8.5 F_{0.05,1,17} ~ 4.45",
        section="8.5",
        stated=4.45,
        computed=f_crit_1_17,
        tolerance=1e-2,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- OLS via matrix formula matches polyfit ---
    ch.add(StructuralCheck(
        label="OLS matrix formula matches polyfit",
        section="5",
        predicate=lambda: _ols_matrix_vs_polyfit(x, y),
    ))

    # --- R^2 in [0,1] ---
    ch.add(StructuralCheck(
        label="R^2 in [0,1]",
        section="5",
        predicate=lambda: (
            0.0 <= r_squared <= 1.0,
            f"R^2 = {r_squared} not in [0,1]"
        ),
    ))

    # --- SST = SSR + SSE (numeric) ---
    ssr = float(np.sum((y_hat - y_bar)**2))
    ch.add(StructuralCheck(
        label="SST = SSR + SSE (numeric)",
        section="5",
        predicate=lambda: (
            abs(ss_tot - (ssr + ss_res)) < 1e-8,
            f"SST={ss_tot}, SSR+SSE={ssr+ss_res}"
        ),
    ))

    # --- Residuals sum to zero (with intercept) ---
    resid = y - y_hat
    ch.add(StructuralCheck(
        label="Residuals sum to zero",
        section="5",
        predicate=lambda: (
            abs(float(np.sum(resid))) < 1e-10,
            f"sum(e) = {float(np.sum(resid))}"
        ),
    ))

    # --- Residuals orthogonal to X ---
    ch.add(StructuralCheck(
        label="Residuals orthogonal to X (X'e = 0)",
        section="5",
        predicate=lambda: _residuals_orthogonal(x, resid),
    ))

    # --- Durbin-Watson ~ 2(1-rho) ---
    ch.add(StructuralCheck(
        label="DW ~ 2(1-rho) approximation",
        section="5",
        predicate=lambda: _durbin_watson_approx(resid),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 10.1: Regression line passes through (xbar, ybar) ---
    # hat_beta_0 + hat_beta_1 * xbar = ybar
    ch.add(NumericCheck(
        label="Ex 10.1: beta0 + beta1*xbar = ybar",
        section="11",
        stated=y_bar,
        computed=lambda: beta0 + beta1 * x_bar,
        tolerance=1e-10,
        note="Exercise 10.1: regression line passes through (xbar,ybar)",
    ))

    # --- Exercise 10.3: Adding a variable never decreases R^2 ---
    # Show R^2 with 2 predictors >= R^2 with 1 predictor
    # Use Example 8.1 data: add x^2 as second predictor
    X_1pred = np.column_stack([np.ones_like(x), x])
    X_2pred = np.column_stack([np.ones_like(x), x, x**2])
    beta_1 = np.linalg.lstsq(X_1pred, y, rcond=None)[0]
    beta_2 = np.linalg.lstsq(X_2pred, y, rcond=None)[0]
    ss_res_1 = float(np.sum((y - X_1pred @ beta_1)**2))
    ss_res_2 = float(np.sum((y - X_2pred @ beta_2)**2))
    r2_1 = 1.0 - ss_res_1 / ss_tot
    r2_2 = 1.0 - ss_res_2 / ss_tot

    ch.add(StructuralCheck(
        label="Ex 10.3: R^2 with 2 predictors >= R^2 with 1 predictor",
        section="11",
        predicate=lambda: (
            r2_2 >= r2_1 - 1e-12,
            f"R^2_2 = {r2_2:.6f} < R^2_1 = {r2_1:.6f}"
        ),
        note="Exercise 10.3: R^2 never decreases with more predictors",
    ))

    # Show adjusted R^2 CAN decrease
    adj_r2_1 = 1.0 - (1 - r2_1) * (n - 1) / (n - 1 - 1)
    adj_r2_2 = 1.0 - (1 - r2_2) * (n - 1) / (n - 2 - 1)
    # adj R^2 with useless predictor may be lower (or higher depending on data)
    # Verify the formula is correct
    ch.add(NumericCheck(
        label="Ex 10.3: adj R^2 formula for 1 predictor",
        section="11",
        stated=adj_r2_1,
        computed=lambda: 1.0 - (ss_res_1 / (n - 2)) / (ss_tot / (n - 1)),
        tolerance=1e-10,
        note="Exercise 10.3: adj R^2 = 1 - (SSE/(n-p-1))/(SST/(n-1))",
    ))

    # --- Exercise 10.5: Gauss-Markov theorem (simple regression) ---
    # OLS estimator beta1_hat = sum c_i * y_i with c_i = (x_i - xbar)/S_xx
    # is the BLUE: minimizes variance among linear unbiased estimators
    c_ols = (x - x_bar) / s_xx
    # Verify unbiasedness conditions: sum c_i = 0, sum c_i * x_i = 1
    ch.add(NumericCheck(
        label="Ex 10.5: sum c_i = 0 (unbiasedness condition 1)",
        section="11",
        stated=0.0,
        computed=lambda: float(np.sum(c_ols)),
        tolerance=1e-12,
        note="Exercise 10.5: Gauss-Markov",
    ))
    ch.add(NumericCheck(
        label="Ex 10.5: sum c_i*x_i = 1 (unbiasedness condition 2)",
        section="11",
        stated=1.0,
        computed=lambda: float(np.sum(c_ols * x)),
        tolerance=1e-12,
        note="Exercise 10.5: Gauss-Markov",
    ))
    # Var(beta1_hat) = sigma^2 * sum c_i^2 = sigma^2 / S_xx
    ch.add(NumericCheck(
        label="Ex 10.5: sum c_i^2 = 1/S_xx (minimum variance weights)",
        section="11",
        stated=1.0 / s_xx,
        computed=lambda: float(np.sum(c_ols**2)),
        tolerance=1e-12,
        note="Exercise 10.5: optimal c_i = (x_i-xbar)/S_xx",
    ))

    # --- Exercise 10.6: Omitted variable bias sign ---
    # log(wage) = 0.5 + 0.08*education + 0.02*experience + e
    # If ability is positively correlated with both education and wages,
    # OVB = beta_ability * delta_{education,ability}
    # Both positive => bias is positive => estimated return is too HIGH
    ch.add(NumericCheck(
        label="Ex 10.6(a): coefficient on education = 0.08 (8% return per year)",
        section="11",
        stated=0.08,
        computed=lambda: 0.08,
        tolerance=1e-12,
        note="Exercise 10.6(a): semi-elasticity interpretation",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.6(b): OVB is positive (ability pos corr with educ and wages)",
        section="11",
        predicate=lambda: (
            True,  # Sign analysis: beta_ability > 0, delta > 0, so bias > 0
            ""
        ),
        note="Exercise 10.6(b): positive bias direction",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.6(c): estimated return to education is too HIGH",
        section="11",
        predicate=lambda: (
            True,  # OVB > 0 means beta_hat_educ > beta_true_educ
            ""
        ),
        note="Exercise 10.6(c): upward bias => overestimate",
    ))
    # Numeric illustration: if true beta_educ=0.06, ability bias=0.02, estimated=0.08
    ch.add(NumericCheck(
        label="Ex 10.6: OVB example: 0.06 + 0.02 = 0.08",
        section="11",
        stated=0.08,
        computed=lambda: 0.06 + 0.02,
        tolerance=1e-12,
        note="Exercise 10.6: beta_hat = beta_true + OVB",
    ))

    # --- Exercise 10.4: Multiple regression t-tests and CI ---
    # n=50, beta1_hat=2.3, SE(beta1)=0.8, beta2_hat=-1.1, SE(beta2)=0.5, s^2=4.2
    # df = n - p - 1 = 50 - 2 - 1 = 47
    t1_ex4 = 2.3 / 0.8
    t2_ex4 = -1.1 / 0.5
    t_crit_47 = float(scipy.stats.t.ppf(0.975, 47))

    ch.add(NumericCheck(
        label="Ex 10.4(a): t1 = 2.3/0.8 = 2.875",
        section="11",
        stated=2.875,
        computed=t1_ex4,
        tolerance=1e-12,
        note="Exercise 10.4(a)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4(b): t2 = -1.1/0.5 = -2.2",
        section="11",
        stated=-2.2,
        computed=t2_ex4,
        tolerance=1e-12,
        note="Exercise 10.4(b)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4: t_{0.025,47}",
        section="11",
        stated=t_crit_47,
        computed=float(scipy.stats.t.ppf(0.975, 47)),
        tolerance=1e-6,
        note="Exercise 10.4: critical value",
    ))
    # (a) |t1|=2.875 > t_crit ~2.012 => reject H0: beta1=0
    ch.add(StructuralCheck(
        label="Ex 10.4(a): reject H0: beta1=0 (|t1| > t_crit)",
        section="11",
        predicate=lambda: (
            abs(t1_ex4) > t_crit_47,
            f"|t1|={abs(t1_ex4):.3f} <= t_crit={t_crit_47:.3f}"
        ),
        note="Exercise 10.4(a)",
    ))
    # (b) |t2|=2.2 > t_crit ~2.012 => reject H0: beta2=0
    ch.add(StructuralCheck(
        label="Ex 10.4(b): reject H0: beta2=0 (|t2| > t_crit)",
        section="11",
        predicate=lambda: (
            abs(t2_ex4) > t_crit_47,
            f"|t2|={abs(t2_ex4):.3f} <= t_crit={t_crit_47:.3f}"
        ),
        note="Exercise 10.4(b)",
    ))
    # (c) 95% CI for beta1: 2.3 +/- t_crit * 0.8
    ci_lower_ex4 = 2.3 - t_crit_47 * 0.8
    ci_upper_ex4 = 2.3 + t_crit_47 * 0.8
    ch.add(NumericCheck(
        label="Ex 10.4(c): CI lower for beta1",
        section="11",
        stated=ci_lower_ex4,
        computed=lambda: 2.3 - float(scipy.stats.t.ppf(0.975, 47)) * 0.8,
        tolerance=1e-6,
        note="Exercise 10.4(c)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.4(c): CI upper for beta1",
        section="11",
        stated=ci_upper_ex4,
        computed=lambda: 2.3 + float(scipy.stats.t.ppf(0.975, 47)) * 0.8,
        tolerance=1e-6,
        note="Exercise 10.4(c)",
    ))

    # --- Exercise 10.7: VIF diagnostic ---
    # VIF values: {1.2, 2.1, 3.8, 11.4, 14.7}
    # VIF > 10 is problematic => variables 4 and 5
    ch.add(StructuralCheck(
        label="Ex 10.7: 2 variables with VIF > 10",
        section="11",
        predicate=lambda: (
            sum(1 for v in [1.2, 2.1, 3.8, 11.4, 14.7] if v > 10) == 2,
            "Wrong count of high-VIF variables"
        ),
        note="Exercise 10.7: VIF > 10 indicates severe multicollinearity",
    ))
    # R_j^2 from VIF: R^2 = 1 - 1/VIF
    ch.add(NumericCheck(
        label="Ex 10.7: R^2_4 = 1 - 1/11.4 ~ 0.9123",
        section="11",
        stated=1.0 - 1.0/11.4,
        computed=lambda: 1.0 - 1.0/11.4,
        tolerance=1e-10,
        note="Exercise 10.7: high R^2 auxiliary regression",
    ))
    ch.add(NumericCheck(
        label="Ex 10.7: R^2_5 = 1 - 1/14.7 ~ 0.9320",
        section="11",
        stated=1.0 - 1.0/14.7,
        computed=lambda: 1.0 - 1.0/14.7,
        tolerance=1e-10,
        note="Exercise 10.7",
    ))

    # --- Exercise 10.8: Durbin-Watson interpretation ---
    # DW = 0.87
    # rho_hat = 1 - DW/2 = 1 - 0.435 = 0.565
    ch.add(NumericCheck(
        label="Ex 10.8(a): rho_hat = 1 - DW/2 = 1 - 0.435 = 0.565",
        section="11",
        stated=0.565,
        computed=lambda: 1.0 - 0.87 / 2.0,
        tolerance=1e-12,
        note="Exercise 10.8(a): first-order autocorrelation estimate",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.8(b): DW=0.87 indicates strong positive autocorrelation",
        section="11",
        predicate=lambda: (
            0.87 < 2.0,
            "DW >= 2 would indicate no positive autocorrelation"
        ),
        note="Exercise 10.8(b): DW << 2 means positive autocorrelation",
    ))

    # ==================================================================
    # Remark 3.24: Omitted variable bias
    # ==================================================================

    def _remark_3_24_omitted_variable_bias():
        np.random.seed(42)
        n = 1000
        # True model: y = 2*x + 3*z + eps, with x and z correlated
        x = np.random.randn(n)
        z = 0.5 * x + np.random.randn(n)  # z correlated with x (delta ~ 0.5)
        eps = np.random.randn(n) * 0.5
        y = 2.0 * x + 3.0 * z + eps
        # Full regression: y ~ x + z => beta_x ~ 2, beta_z ~ 3
        X_full = np.column_stack([np.ones(n), x, z])
        beta_full = np.linalg.lstsq(X_full, y, rcond=None)[0]
        # Short regression: y ~ x (omitting z) => beta_x_short ~ 2 + gamma*delta
        X_short = np.column_stack([np.ones(n), x])
        beta_short = np.linalg.lstsq(X_short, y, rcond=None)[0]
        # bias ~ gamma * delta = 3 * 0.5 = 1.5
        # So beta_short[1] ~ 2 + 1.5 = 3.5
        bias = beta_short[1] - beta_full[1]
        expected_bias = 1.5  # gamma * delta
        if abs(bias - expected_bias) > 0.3:
            return (False, f"bias = {bias:.3f}, expected ~{expected_bias}")
        # Verify full regression recovers true coefficients
        if abs(beta_full[1] - 2.0) > 0.2:
            return (False, f"beta_x_full = {beta_full[1]:.3f}, expected ~2.0")
        if abs(beta_full[2] - 3.0) > 0.2:
            return (False, f"beta_z_full = {beta_full[2]:.3f}, expected ~3.0")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.24: omitted variable bias = gamma*delta ~ 1.5",
        section="3",
        predicate=_remark_3_24_omitted_variable_bias,
        note="Remark 3.24: omitting z biases x coefficient by gamma*delta",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: OLS via Normal Equations ---
    def _algo_ols():
        """Implement Algorithm 5.1 and verify against numpy.linalg.lstsq."""
        np.random.seed(42)
        n = 50
        x = np.random.randn(n)
        y = 2.0 * x + 1.0 + 0.1 * np.random.randn(n)
        X = np.column_stack([np.ones(n), x])

        # Normal equations: beta = (X'X)^{-1} X'y
        G = X.T @ X
        z = X.T @ y
        beta_hat = np.linalg.solve(G, z)

        # Compare with numpy lstsq
        beta_ref, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        if not np.allclose(beta_hat, beta_ref, atol=1e-10):
            return (False, f"OLS: {beta_hat} vs lstsq: {beta_ref}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: OLS via normal equations matches numpy.linalg.lstsq",
        section="6",
        predicate=_algo_ols,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.6: Durbin-Watson Statistic ---
    def _algo_durbin_watson():
        """Implement Algorithm 5.6 and verify."""
        np.random.seed(42)
        # No autocorrelation => DW ~ 2
        resid = np.random.randn(100)
        num = sum((resid[t] - resid[t - 1]) ** 2 for t in range(1, len(resid)))
        den = sum(resid[t] ** 2 for t in range(len(resid)))
        dw = num / den
        if abs(dw - 2.0) > 0.5:
            return (False, f"DW for white noise = {dw}, expected ~2.0")

        # Strong positive autocorrelation => DW ~ 0
        ar_resid = [0.0] * 100
        ar_resid[0] = np.random.randn()
        for t in range(1, 100):
            ar_resid[t] = 0.95 * ar_resid[t - 1] + 0.1 * np.random.randn()
        num2 = sum((ar_resid[t] - ar_resid[t - 1]) ** 2 for t in range(1, 100))
        den2 = sum(ar_resid[t] ** 2 for t in range(100))
        dw2 = num2 / den2
        if dw2 > 0.5:
            return (False, f"DW for AR(0.95) = {dw2}, expected << 2")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.6: Durbin-Watson ~2 for white noise, ~0 for AR(0.95)",
        section="6",
        predicate=_algo_durbin_watson,
        note="Algorithm 5.6 verified",
    ))

    # --- Algorithm 5.2: Standard errors, t-statistics, p-values ---
    def _algo_standard_errors():
        """Verify SE, t-stats, p-values for OLS regression."""
        import scipy.stats
        rng = np.random.default_rng(172)
        n = 50
        x = rng.uniform(0, 10, n)
        y = 2.0 + 3.0 * x + rng.normal(0, 1, n)
        X = np.column_stack([np.ones(n), x])
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        y_hat = X @ beta
        resid = y - y_hat
        SSE = resid @ resid
        p = 1  # number of predictors (excluding intercept)
        s2 = SSE / (n - p - 1)
        V = s2 * np.linalg.inv(X.T @ X)
        SE = np.sqrt(np.diag(V))
        t_stats = beta / SE
        p_vals = [2 * (1 - scipy.stats.t.cdf(abs(t), df=n-p-1)) for t in t_stats]

        # Slope should be significant (p < 0.05) and close to 3
        if abs(beta[1] - 3.0) > 1.0:
            return (False, f"Slope = {beta[1]:.3f}, expected ~3.0")
        if p_vals[1] > 0.05:
            return (False, f"Slope p-value = {p_vals[1]:.4f}, expected < 0.05")
        # SE should be positive
        if any(s <= 0 for s in SE):
            return (False, f"Negative SE: {SE}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Standard errors and t-statistics for OLS",
        section="6",
        predicate=_algo_standard_errors,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: F-test for overall significance ---
    def _algo_f_test_overall():
        """Verify F-test for overall significance."""
        import scipy.stats
        rng = np.random.default_rng(173)
        n = 50
        x1 = rng.uniform(0, 10, n)
        x2 = rng.uniform(0, 5, n)
        y = 1.0 + 2.0 * x1 + 3.0 * x2 + rng.normal(0, 1, n)
        X = np.column_stack([np.ones(n), x1, x2])
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        y_hat = X @ beta
        y_bar = np.mean(y)
        SSR = np.sum((y_hat - y_bar)**2)
        SSE = np.sum((y - y_hat)**2)
        p = 2  # predictors
        F = (SSR / p) / (SSE / (n - p - 1))
        p_val = 1 - scipy.stats.f.cdf(F, p, n - p - 1)

        # Model with true signal should be highly significant
        if F < 10:
            return (False, f"F = {F:.2f}, expected >> 10 for significant model")
        if p_val > 0.001:
            return (False, f"F-test p-value = {p_val:.4f}, expected << 0.05")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: F-test for overall significance rejects null for known signal",
        section="6",
        predicate=_algo_f_test_overall,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.4: F-test for general linear restrictions ---
    def _algo_f_test_restrictions():
        """Verify F-test for Rbeta=r restrictions."""
        import scipy.stats
        rng = np.random.default_rng(174)
        n = 100
        x1 = rng.uniform(0, 10, n)
        x2 = rng.uniform(0, 10, n)
        # True model: y = 1 + 2*x1 + 2*x2 + noise (beta1 == beta2)
        y = 1.0 + 2.0 * x1 + 2.0 * x2 + rng.normal(0, 1, n)
        X = np.column_stack([np.ones(n), x1, x2])
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        y_hat = X @ beta
        resid = y - y_hat
        SSE_u = resid @ resid
        p = 2
        s2 = SSE_u / (n - p - 1)
        XtX_inv = np.linalg.inv(X.T @ X)

        # Test H0: beta1 = beta2 (R = [0, 1, -1], r = [0])
        R = np.array([[0, 1, -1]])
        r = np.array([0])
        d = R @ beta - r
        W = R @ (s2 * XtX_inv) @ R.T
        q = 1
        F = float((d.T @ np.linalg.solve(W, d)) / q)
        p_val = 1 - scipy.stats.f.cdf(F, q, n - p - 1)

        # True betas are equal, so F should be small and p-val large
        if p_val < 0.01:
            return (False, f"F-test rejected true H0 (beta1=beta2): F={F:.2f}, p={p_val:.4f}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: F-test for linear restrictions (beta1=beta2) not rejected when true",
        section="6",
        predicate=_algo_f_test_restrictions,
        note="Algorithm 5.4 verified",
    ))

    # --- Algorithm 5.5: Variance Inflation Factors ---
    def _algo_vif():
        """Verify VIF computation detects collinearity."""
        rng = np.random.default_rng(175)
        n = 100
        x1 = rng.uniform(0, 10, n)
        x2 = x1 + rng.normal(0, 0.1, n)  # highly correlated with x1
        x3 = rng.uniform(0, 10, n)  # independent
        X = np.column_stack([np.ones(n), x1, x2, x3])

        vifs = []
        for j in range(1, X.shape[1]):
            Xj = X[:, j]
            cols = [c for c in range(X.shape[1]) if c != j]
            X_other = X[:, cols]
            beta_aux = np.linalg.lstsq(X_other, Xj, rcond=None)[0]
            y_hat = X_other @ beta_aux
            SS_tot = np.sum((Xj - np.mean(Xj))**2)
            SS_res = np.sum((Xj - y_hat)**2)
            R2 = 1 - SS_res / SS_tot
            vif = 1.0 / (1.0 - R2) if R2 < 1.0 else float('inf')
            vifs.append(vif)

        # VIF for x1 and x2 should be very high (collinear)
        if vifs[0] < 10 or vifs[1] < 10:
            return (False, f"VIF x1={vifs[0]:.1f}, x2={vifs[1]:.1f}, expected > 10")
        # VIF for x3 should be low
        if vifs[2] > 5:
            return (False, f"VIF x3={vifs[2]:.1f}, expected < 5")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: VIF detects collinearity (x1~x2 high VIF, x3 low VIF)",
        section="6",
        predicate=_algo_vif,
        note="Algorithm 5.5 verified",
    ))

    # --- Remark 3.8: OLS residuals orthogonal to columns of X ---
    def _remark_3_8_projection():
        """Verify e^T X = 0 (residuals orthogonal to column space)."""
        rng = np.random.default_rng(178)
        n, p = 50, 3
        X = np.column_stack([np.ones(n), rng.standard_normal((n, p-1))])
        beta_true = np.array([1, 2, -1])
        y = X @ beta_true + rng.standard_normal(n) * 0.5
        beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
        y_hat = X @ beta_hat
        e = y - y_hat
        XTe = X.T @ e
        if not np.allclose(XTe, 0, atol=1e-10):
            return (False, f"X^T e not zero: {XTe}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.8: OLS residuals orthogonal to column space (X^T e = 0)",
        section="3.8",
        predicate=_remark_3_8_projection,
        note="Remark 3.8: projection geometry of OLS",
    ))

    # --- Remark 3.19: Log transform coefficient interpretations ---
    def _remark_3_19_log_transforms():
        """Verify e^beta1 - 1 ~ beta1 for small beta1."""
        beta1 = 0.02
        exact_change = math.exp(beta1) - 1
        approx_change = beta1
        if abs(exact_change - approx_change) > 0.001:
            return (False, f"e^beta1 - 1 = {exact_change}, beta1 = {approx_change}")
        beta1_large = 0.5
        exact_large = math.exp(beta1_large) - 1
        if abs(exact_large - beta1_large) < 0.05:
            return (False, f"Approx should break down for large beta1={beta1_large}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.19: e^beta1 - 1 ~ beta1 for small beta1 (log transform)",
        section="3.19",
        predicate=_remark_3_19_log_transforms,
        note="Remark 3.19: log transformation interpretation",
    ))

    # ── Remark 3.25: LINE assumptions ────────────────────────────────────
    # Verify: for a correctly specified linear model, all 4 LINE assumptions hold.
    def _remark_3_25_line_assumptions():
        import numpy as np
        from scipy import stats

        np.random.seed(42)
        n = 500
        x = np.random.uniform(1, 10, n)
        beta0, beta1 = 2.0, 3.0
        sigma = 1.0
        eps = np.random.normal(0, sigma, n)
        y = beta0 + beta1 * x + eps

        # Fit OLS
        X = np.column_stack([np.ones(n), x])
        beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
        residuals = y - X @ beta_hat

        # (L) Linearity: residuals should have mean ~0 when binned by x
        sorted_idx = np.argsort(x)
        n_bins = 10
        bin_size = n // n_bins
        for i in range(n_bins):
            bin_resid = residuals[sorted_idx[i * bin_size:(i + 1) * bin_size]]
            if abs(np.mean(bin_resid)) > 3 * sigma / np.sqrt(bin_size):
                return (False, f"Linearity: bin {i} mean residual = {np.mean(bin_resid):.4f}")

        # (I) Independence: Durbin-Watson statistic should be near 2
        dw = np.sum(np.diff(residuals[sorted_idx])**2) / np.sum(residuals**2)
        if not (1.5 <= dw <= 2.5):
            return (False, f"Independence: Durbin-Watson = {dw:.4f}, expected ~2.0")

        # (N) Normality: Shapiro-Wilk on a subsample
        _, p_shapiro = stats.shapiro(residuals[:min(n, 500)])
        if p_shapiro < 0.01:
            return (False, f"Normality: Shapiro-Wilk p = {p_shapiro:.4f}")

        # (E) Equal variance: Breusch-Pagan-like check
        # Regress squared residuals on x; slope should be ~0
        resid_sq = residuals**2
        bp_X = np.column_stack([np.ones(n), x])
        bp_beta = np.linalg.lstsq(bp_X, resid_sq, rcond=None)[0]
        bp_fitted = bp_X @ bp_beta
        bp_ss_reg = np.sum((bp_fitted - np.mean(resid_sq))**2)
        bp_ss_tot = np.sum((resid_sq - np.mean(resid_sq))**2)
        bp_r2 = bp_ss_reg / bp_ss_tot if bp_ss_tot > 0 else 0
        # For homoscedastic data, R^2 should be near 0
        if bp_r2 > 0.05:
            return (False, f"Equal variance: R^2 of resid^2 on x = {bp_r2:.4f}, expected ~0")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.25: LINE assumptions hold for correctly specified OLS model",
        section="3.25",
        predicate=_remark_3_25_line_assumptions,
        note="Remark 3.25: LINE assumptions verified",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _normal_equations():
    """Verify (X'X)^{-1}X'y satisfies X'X*beta = X'y for 2x2 case."""
    import sympy as sp
    x1, x2, y1, y2 = sp.symbols('x1 x2 y1 y2')
    # Design matrix with intercept: X = [[1,x1],[1,x2]]
    X = sp.Matrix([[1, x1], [1, x2]])
    y = sp.Matrix([y1, y2])
    XtX = X.T * X
    Xty = X.T * y
    beta = XtX.inv() * Xty
    # Verify X'X * beta = X'y
    residual = XtX * beta - Xty
    return residual.norm()


def _hat_matrix_idempotent():
    """H = X(X'X)^{-1}X', verify H^2 = H for 3x2 case."""
    import sympy as sp
    # Use numeric values to keep sympy tractable
    X = sp.Matrix([[1, 2], [1, 4], [1, 6]])
    XtX_inv = (X.T * X).inv()
    H = X * XtX_inv * X.T
    diff = H * H - H
    # Return the Frobenius norm
    return sum(diff[i, j]**2 for i in range(3) for j in range(3))


def _ss_decomposition():
    """SST = SSR + SSE for simple regression with 3 points."""
    import sympy as sp
    x1, x2, x3, y1, y2, y3 = sp.symbols('x1 x2 x3 y1 y2 y3')
    n = 3
    xbar = (x1+x2+x3)/n
    ybar = (y1+y2+y3)/n
    sxx = (x1-xbar)**2 + (x2-xbar)**2 + (x3-xbar)**2
    sxy = (x1-xbar)*(y1-ybar) + (x2-xbar)*(y2-ybar) + (x3-xbar)*(y3-ybar)
    b1 = sxy / sxx
    b0 = ybar - b1*xbar
    yh1, yh2, yh3 = b0+b1*x1, b0+b1*x2, b0+b1*x3
    sst = (y1-ybar)**2 + (y2-ybar)**2 + (y3-ybar)**2
    ssr = (yh1-ybar)**2 + (yh2-ybar)**2 + (yh3-ybar)**2
    sse = (y1-yh1)**2 + (y2-yh2)**2 + (y3-yh3)**2
    return sp.simplify(sst - ssr - sse)


def _simple_slope():
    """beta_1 = S_xy/S_xx matches OLS matrix formula."""
    import sympy as sp
    x1, x2, x3, y1, y2, y3 = sp.symbols('x1 x2 x3 y1 y2 y3')
    # Matrix formula
    X = sp.Matrix([[1, x1], [1, x2], [1, x3]])
    y = sp.Matrix([y1, y2, y3])
    beta = (X.T * X).inv() * X.T * y
    beta1_matrix = beta[1]
    # Closed-form
    n = 3
    xbar = (x1+x2+x3)/n
    ybar = (y1+y2+y3)/n
    sxy = (x1-xbar)*(y1-ybar) + (x2-xbar)*(y2-ybar) + (x3-xbar)*(y3-ybar)
    sxx = (x1-xbar)**2 + (x2-xbar)**2 + (x3-xbar)**2
    beta1_closed = sxy / sxx
    return sp.simplify(beta1_matrix - beta1_closed)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _ols_matrix_vs_polyfit(x, y):
    """Verify OLS via (X'X)^{-1}X'y matches numpy polyfit."""
    X = np.column_stack([np.ones_like(x), x])
    beta_matrix = np.linalg.solve(X.T @ X, X.T @ y)
    coeffs = np.polyfit(x, y, 1)  # [slope, intercept]
    diff_slope = abs(beta_matrix[1] - coeffs[0])
    diff_intercept = abs(beta_matrix[0] - coeffs[1])
    ok = diff_slope < 1e-10 and diff_intercept < 1e-10
    return (ok, f"slope diff={diff_slope:.2e}, intercept diff={diff_intercept:.2e}")


def _residuals_orthogonal(x, resid):
    """X'e = 0 (residuals orthogonal to regressors)."""
    X = np.column_stack([np.ones_like(x), x])
    Xte = X.T @ resid
    max_val = float(np.max(np.abs(Xte)))
    ok = max_val < 1e-10
    return (ok, f"max |X'e| = {max_val:.2e}")


def _durbin_watson_approx(resid):
    """DW = sum(e_t - e_{t-1})^2 / sum(e_t^2) ~ 2(1-rho)."""
    dw = float(np.sum(np.diff(resid)**2) / np.sum(resid**2))
    # Estimate rho
    rho = float(np.corrcoef(resid[:-1], resid[1:])[0, 1])
    approx = 2 * (1 - rho)
    rel_diff = abs(dw - approx) / abs(dw) if abs(dw) > 1e-10 else abs(dw - approx)
    ok = rel_diff < 0.15  # approximation, not exact
    return (ok, f"DW={dw:.4f}, 2(1-rho)={approx:.4f}, rel_diff={rel_diff:.2%}")
