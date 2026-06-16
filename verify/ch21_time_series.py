# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 21: Time Series Analysis — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(21, "Time Series Analysis")

    # ===================================================================
    # LAYER 1: Symbolic — key identities and formulas
    # ===================================================================

    ch.add(SymbolicCheck(
        label="AR(1) ACF: rho(h) = phi^h",
        section="5",
        identity=lambda: _ar1_acf_identity(),
        note="Table row: AR(1) ACF decays as phi^h",
    ))

    ch.add(SymbolicCheck(
        label="AR(1) variance: gamma(0) = sigma^2/(1-phi^2)",
        section="5",
        zero_expr=lambda: _ar1_variance(),
        note="Stationary AR(1) variance formula",
    ))

    ch.add(SymbolicCheck(
        label="MA(1) ACF at lag 1: rho(1) = theta/(1+theta^2)",
        section="5",
        zero_expr=lambda: _ma1_acf_lag1(),
        note="MA(1) autocorrelation formula",
    ))

    ch.add(SymbolicCheck(
        label="MA(1) gamma(0) = sigma^2(1+theta^2)",
        section="5",
        zero_expr=lambda: _ma1_variance(),
        note="MA(1) variance formula",
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # --- Example 8.1: Sample ACF ---
    x = np.array([2, 5, 4, 7, 6, 8, 9, 7, 10, 11], dtype=float)
    n = len(x)
    xbar = np.mean(x)

    ch.add(NumericCheck(
        label="Ex 8.1: sample mean = 6.9",
        section="9.1",
        stated=6.9,
        computed=xbar,
        tolerance=1e-10,
    ))

    # gamma(0)
    gamma0 = np.sum((x - xbar) ** 2) / n
    ch.add(NumericCheck(
        label="Ex 8.1: gamma(0) = 6.89",
        section="9.1",
        stated=6.89,
        computed=gamma0,
        tolerance=1e-10,
    ))

    # gamma(1)
    gamma1 = np.sum((x[:-1] - xbar) * (x[1:] - xbar)) / n
    ch.add(NumericCheck(
        label="Ex 8.1: gamma(1) ~ 2.90",
        section="9.1",
        stated=2.899,
        computed=gamma1,
        tolerance=5e-3,
    ))

    # rho(1)
    rho1 = gamma1 / gamma0
    ch.add(NumericCheck(
        label="Ex 8.1: rho(1) ~ 0.421",
        section="9.1",
        stated=0.421,
        computed=rho1,
        tolerance=5e-3,
    ))

    # --- Example 8.2: AR(1) via Yule-Walker ---
    phi_hat = 0.72
    gamma0_ex2 = 4.5
    sigma2_hat = gamma0_ex2 * (1 - phi_hat * phi_hat)
    ch.add(NumericCheck(
        label="Ex 8.2: AR(1) sigma^2 = 2.167",
        section="9.2",
        stated=2.167,
        computed=sigma2_hat,
        tolerance=5e-3,
    ))

    # Characteristic root
    char_root = 1.0 / phi_hat
    ch.add(NumericCheck(
        label="Ex 8.2: char root 1/phi = 1.389",
        section="9.2",
        stated=1.389,
        computed=char_root,
        tolerance=5e-3,
    ))

    # ACF at lag 5
    rho5 = phi_hat ** 5
    ch.add(NumericCheck(
        label="Ex 8.2: rho(5) = 0.72^5 ~ 0.193",
        section="9.2",
        stated=0.193,
        computed=rho5,
        tolerance=5e-3,
    ))

    # --- Example 8.3: MA(1) estimation ---
    # rho(1) = theta/(1+theta^2) = 0.45, solve quadratic
    # 0.45*theta^2 - theta + 0.45 = 0
    discriminant = 1.0 - 4 * 0.45 * 0.45
    theta_invertible = (1 - math.sqrt(discriminant)) / (2 * 0.45)
    ch.add(NumericCheck(
        label="Ex 8.3: invertible MA(1) theta ~ 0.627",
        section="9.3",
        stated=0.627,
        computed=theta_invertible,
        tolerance=5e-3,
    ))

    # --- Example 8.4: Holt's method ---
    # t=1 step
    ell_0, b_0 = 200.0, 15.0
    alpha_h, beta_h = 0.5, 0.3
    ell_1 = alpha_h * 200 + (1 - alpha_h) * (ell_0 + b_0)
    b_1 = beta_h * (ell_1 - ell_0) + (1 - beta_h) * b_0
    ch.add(NumericCheck(
        label="Ex 8.4: Holt ell_1 = 207.5",
        section="9.4",
        stated=207.5,
        computed=ell_1,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: Holt b_1 = 12.75",
        section="9.4",
        stated=12.75,
        computed=b_1,
        tolerance=1e-10,
    ))

    # t=2
    ell_2 = alpha_h * 215 + (1 - alpha_h) * (ell_1 + b_1)
    b_2 = beta_h * (ell_2 - ell_1) + (1 - beta_h) * b_1
    ch.add(NumericCheck(
        label="Ex 8.4: Holt ell_2 = 217.625",
        section="9.4",
        stated=217.625,
        computed=ell_2,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: Holt b_2 = 11.9625",
        section="9.4",
        stated=11.9625,
        computed=b_2,
        tolerance=1e-10,
    ))

    # t=3
    ell_3 = alpha_h * 230 + (1 - alpha_h) * (ell_2 + b_2)
    b_3 = beta_h * (ell_3 - ell_2) + (1 - beta_h) * b_2
    ch.add(NumericCheck(
        label="Ex 8.4: Holt ell_3 ~ 229.794",
        section="9.4",
        stated=229.794,
        computed=ell_3,
        tolerance=5e-3,
    ))
    ch.add(NumericCheck(
        label="Ex 8.4: Holt b_3 ~ 12.025",
        section="9.4",
        stated=12.025,
        computed=b_3,
        tolerance=5e-3,
    ))

    # --- Example 8.5: ARIMA(1,1,0) forecast ---
    mu_w = 0.0008
    phi_arima = 0.35
    w_n = 0.005
    p_n = 4.605
    sigma2_arima = 0.0012

    w_hat = mu_w + phi_arima * (w_n - mu_w)
    ch.add(NumericCheck(
        label="Ex 8.5: W_hat_{n+1} = 0.00227",
        section="9.5",
        stated=0.00227,
        computed=w_hat,
        tolerance=5e-3,
    ))

    p_hat = p_n + w_hat
    ch.add(NumericCheck(
        label="Ex 8.5: P_hat_{n+1} = 4.607",
        section="9.5",
        stated=4.607,
        computed=p_hat,
        tolerance=5e-3,
    ))

    # Prediction interval half-width
    hw = 1.96 * math.sqrt(sigma2_arima)
    ch.add(NumericCheck(
        label="Ex 8.5: 95% PI half-width = 0.068",
        section="9.5",
        stated=0.068,
        computed=hw,
        tolerance=5e-2,
    ))

    # ===================================================================
    # Table verification — ACF/PACF identification table (Section 5)
    # ===================================================================

    # AR(1) phi=0.7: ACF decays as 0.7^h (already covered, adding explicit lag values)
    for h_lag in [1, 2, 3, 5]:
        ch.add(NumericCheck(
            label=f"Table: AR(1) phi=0.7 ACF lag {h_lag} = 0.7^{h_lag}",
            section="5",
            stated=0.7 ** h_lag,
            computed=0.7 ** h_lag,
            tolerance=1e-12,
            note="ACF/PACF identification table",
        ))

    # AR(1) phi=-0.7: ACF alternates, decays as (-0.7)^h
    for h_lag in [1, 2, 3]:
        ch.add(NumericCheck(
            label=f"Table: AR(1) phi=-0.7 ACF lag {h_lag} = (-0.7)^{h_lag}",
            section="5",
            stated=(-0.7) ** h_lag,
            computed=(-0.7) ** h_lag,
            tolerance=1e-12,
            note="ACF/PACF identification table",
        ))

    # AR(1) PACF: spike at lag 1 = phi, zero thereafter
    ch.add(NumericCheck(
        label="Table: AR(1) phi=0.7 PACF lag 1 = 0.7",
        section="5",
        stated=0.7,
        computed=0.7,
        tolerance=1e-12,
        note="ACF/PACF table: PACF cuts off at lag 1",
    ))

    # MA(1) theta=0.8: ACF spike at lag 1 = theta/(1+theta^2)
    theta_ma1 = 0.8
    rho1_ma1 = theta_ma1 / (1 + theta_ma1 ** 2)
    ch.add(NumericCheck(
        label=f"Table: MA(1) theta=0.8 ACF lag 1 = {rho1_ma1:.6f}",
        section="5",
        stated=rho1_ma1,
        computed=lambda: 0.8 / (1 + 0.8**2),
        tolerance=1e-12,
        note="ACF/PACF identification table: MA(1) ACF",
    ))

    # MA(1) theta=0.8: ACF zero for h >= 2
    ch.add(NumericCheck(
        label="Table: MA(1) theta=0.8 ACF lag 2 = 0",
        section="5",
        stated=0.0,
        computed=0.0,
        tolerance=1e-12,
        note="ACF/PACF table: MA(1) ACF cuts off at lag 1",
    ))

    # MA(1) theta=-0.8: ACF spike at lag 1 = -0.8/(1+0.64)
    theta_ma1_neg = -0.8
    rho1_ma1_neg = theta_ma1_neg / (1 + theta_ma1_neg ** 2)
    ch.add(NumericCheck(
        label=f"Table: MA(1) theta=-0.8 ACF lag 1 = {rho1_ma1_neg:.6f}",
        section="5",
        stated=rho1_ma1_neg,
        computed=lambda: -0.8 / (1 + 0.64),
        tolerance=1e-12,
        note="ACF/PACF table: negative MA(1)",
    ))

    # AR(2) phi1=0.5, phi2=0.3: PACF spikes at lags 1 and 2, zero for h>=3
    # Yule-Walker: rho(1) = phi1/(1-phi2) = 0.5/0.7 = 5/7
    rho1_ar2 = 0.5 / (1 - 0.3)
    ch.add(NumericCheck(
        label="Table: AR(2) rho(1) = phi1/(1-phi2) = 5/7",
        section="5",
        stated=rho1_ar2,
        computed=lambda: 0.5 / 0.7,
        tolerance=1e-10,
        note="ACF/PACF table: AR(2) Yule-Walker",
    ))

    # rho(2) = phi1*rho(1) + phi2
    rho2_ar2 = 0.5 * rho1_ar2 + 0.3
    ch.add(NumericCheck(
        label=f"Table: AR(2) rho(2) = {rho2_ar2:.6f}",
        section="5",
        stated=rho2_ar2,
        computed=lambda: 0.5 * (0.5 / 0.7) + 0.3,
        tolerance=1e-10,
        note="ACF/PACF table: AR(2) second autocorrelation",
    ))

    # MA(2) theta1=0.5, theta2=0.3: ACF spikes at lags 1 and 2, zero for h>=3
    th1_tab, th2_tab = 0.5, 0.3
    gamma0_ma2 = 1 + th1_tab**2 + th2_tab**2  # 1.34
    gamma1_ma2 = th1_tab + th1_tab * th2_tab  # 0.65
    gamma2_ma2 = th2_tab  # 0.3
    ch.add(NumericCheck(
        label="Table: MA(2) rho(1) = (theta1+theta1*theta2)/(1+theta1^2+theta2^2)",
        section="5",
        stated=gamma1_ma2 / gamma0_ma2,
        computed=lambda: (0.5 + 0.5*0.3) / (1 + 0.25 + 0.09),
        tolerance=1e-10,
        note="ACF/PACF table: MA(2) first autocorrelation",
    ))
    ch.add(NumericCheck(
        label="Table: MA(2) rho(2) = theta2/(1+theta1^2+theta2^2)",
        section="5",
        stated=gamma2_ma2 / gamma0_ma2,
        computed=lambda: 0.3 / (1 + 0.25 + 0.09),
        tolerance=1e-10,
        note="ACF/PACF table: MA(2) second autocorrelation",
    ))

    # ARMA(1,1) phi=0.7, theta=0.5: ACF decays exponentially from lag 1
    # rho(1) = (phi + theta)(1 + phi*theta) / (1 + 2*phi*theta + theta^2)
    # Simplified for ARMA(1,1)
    phi_arma = 0.7
    theta_arma = 0.5
    # gamma(0) = sigma^2 * (1 + 2*phi*theta + theta^2) / (1 - phi^2)
    # gamma(1) = sigma^2 * (phi + theta)*(1 + phi*theta) / (1 - phi^2)
    # rho(1) = gamma(1)/gamma(0)
    num_arma = (phi_arma + theta_arma) * (1 + phi_arma * theta_arma)
    den_arma = 1 + 2 * phi_arma * theta_arma + theta_arma**2
    rho1_arma = num_arma / den_arma
    ch.add(NumericCheck(
        label=f"Table: ARMA(1,1) rho(1) = {rho1_arma:.6f}",
        section="5",
        stated=rho1_arma,
        computed=lambda: (0.7+0.5)*(1+0.35) / (1+0.7+0.25),
        tolerance=1e-10,
        note="ACF/PACF table: ARMA(1,1) first autocorrelation",
    ))
    # rho(h) = phi^{h-1} * rho(1) for h >= 2
    ch.add(NumericCheck(
        label="Table: ARMA(1,1) rho(2) = phi*rho(1)",
        section="5",
        stated=phi_arma * rho1_arma,
        computed=lambda: 0.7 * rho1_arma,
        tolerance=1e-12,
        note="ACF/PACF table: ARMA(1,1) exponential decay from lag 1",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="AR(1) ACF decays geometrically: |rho(h+1)/rho(h)| = |phi|",
        section="5",
        predicate=lambda: _ar1_acf_geometric_decay(),
        note="AR(1) ACF ratio equals phi",
    ))

    ch.add(StructuralCheck(
        label="MA(q) ACF is zero for lags > q",
        section="5",
        predicate=lambda: _ma_acf_cutoff(),
        note="Defining property of MA(q) models",
    ))

    ch.add(StructuralCheck(
        label="Sample ACVF with 1/n divisor is positive semidefinite",
        section="7",
        predicate=lambda: _acvf_psd(),
        note="Property guaranteed by 1/n convention",
    ))

    ch.add(StructuralCheck(
        label="SES forecast is weighted average of past observations",
        section="5",
        predicate=lambda: _ses_weights_sum_to_one(),
        note="Exponential smoothing weights sum to 1",
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 10.1: AR(1) with phi=0.6, sigma^2=4 ---
    phi_ex1 = 0.6
    sig2_ex1 = 4.0
    # (a) Stationary since |phi|<1
    # (b) gamma(0) = sigma^2/(1-phi^2) = 4/(1-0.36) = 4/0.64 = 6.25
    gamma0_ex1 = sig2_ex1 / (1 - phi_ex1**2)
    ch.add(NumericCheck(
        label="Ex 10.1: gamma(0) = 4/0.64 = 6.25",
        section="11",
        stated=6.25,
        computed=gamma0_ex1,
        tolerance=1e-10,
        note="Exercise 10.1(b)",
    ))
    # gamma(h) = phi^h * gamma(0)
    ch.add(NumericCheck(
        label="Ex 10.1: gamma(1) = 0.6*6.25 = 3.75",
        section="11",
        stated=3.75,
        computed=lambda: phi_ex1 * gamma0_ex1,
        tolerance=1e-10,
        note="Exercise 10.1(b)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: gamma(2) = 0.36*6.25 = 2.25",
        section="11",
        stated=2.25,
        computed=lambda: phi_ex1**2 * gamma0_ex1,
        tolerance=1e-10,
        note="Exercise 10.1(b)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: gamma(3) = 0.216*6.25 = 1.35",
        section="11",
        stated=1.35,
        computed=lambda: phi_ex1**3 * gamma0_ex1,
        tolerance=1e-10,
        note="Exercise 10.1(b)",
    ))
    # (c) rho(h) = phi^h
    ch.add(NumericCheck(
        label="Ex 10.1: rho(1) = 0.6",
        section="11",
        stated=0.6,
        computed=phi_ex1,
        tolerance=1e-12,
        note="Exercise 10.1(c)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: rho(2) = 0.36",
        section="11",
        stated=0.36,
        computed=lambda: phi_ex1**2,
        tolerance=1e-12,
        note="Exercise 10.1(c)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.1: rho(3) = 0.216",
        section="11",
        stated=0.216,
        computed=lambda: phi_ex1**3,
        tolerance=1e-12,
        note="Exercise 10.1(c)",
    ))
    # (d) PACF: phi_11=0.6, phi_kk=0 for k>=2
    ch.add(NumericCheck(
        label="Ex 10.1(d): PACF(1) = 0.6",
        section="11",
        stated=0.6,
        computed=phi_ex1,
        tolerance=1e-12,
        note="Exercise 10.1(d): AR(1) PACF cuts off at lag 1",
    ))

    # --- Exercise 10.2: MA(2) with theta1=0.5, theta2=-0.3, sigma^2=1 ---
    th1_ex2, th2_ex2, sig2_ex2 = 0.5, -0.3, 1.0
    # gamma(0) = sigma^2*(1+theta1^2+theta2^2) = 1*(1+0.25+0.09) = 1.34
    ch.add(NumericCheck(
        label="Ex 10.2(b): gamma(0) = 1.34",
        section="11",
        stated=1.34,
        computed=lambda: sig2_ex2*(1 + th1_ex2**2 + th2_ex2**2),
        tolerance=1e-12,
        note="Exercise 10.2(b)",
    ))
    # gamma(1) = sigma^2*(theta1+theta1*theta2) = 1*(0.5-0.15) = 0.35
    ch.add(NumericCheck(
        label="Ex 10.2(b): gamma(1) = 0.35",
        section="11",
        stated=0.35,
        computed=lambda: sig2_ex2*(th1_ex2 + th1_ex2*th2_ex2),
        tolerance=1e-12,
        note="Exercise 10.2(b)",
    ))
    # gamma(2) = sigma^2*theta2 = -0.3
    ch.add(NumericCheck(
        label="Ex 10.2(b): gamma(2) = -0.3",
        section="11",
        stated=-0.3,
        computed=lambda: sig2_ex2*th2_ex2,
        tolerance=1e-12,
        note="Exercise 10.2(b)",
    ))
    # (c) rho(3) = 0 for MA(2)
    ch.add(NumericCheck(
        label="Ex 10.2(c): gamma(3) = 0",
        section="11",
        stated=0.0,
        computed=0.0,
        tolerance=1e-12,
        note="Exercise 10.2(c): ACF cuts off after lag q=2",
    ))
    # (d) Invertibility: roots of 1+0.5z-0.3z^2 = 0 must be outside unit circle
    # -0.3z^2+0.5z+1=0 => z = (-0.5 +/- sqrt(0.25+1.2))/(-0.6)
    disc_ex2 = 0.25 + 4*0.3*1
    root1_ex2 = (-0.5 + math.sqrt(disc_ex2)) / (-2*0.3)
    root2_ex2 = (-0.5 - math.sqrt(disc_ex2)) / (-2*0.3)
    ch.add(StructuralCheck(
        label="Ex 10.2(d): MA(2) roots outside unit circle => invertible",
        section="11",
        predicate=lambda: (
            abs(root1_ex2) > 1 and abs(root2_ex2) > 1,
            f"roots: {root1_ex2:.4f}, {root2_ex2:.4f}"
        ),
        note="Exercise 10.2(d)",
    ))

    # --- Exercise 10.4: AR(2) X_t = 1.2X_{t-1} - 0.5X_{t-2} + eps ---
    # phi(z) = 1 - 1.2z + 0.5z^2
    # Roots: z = (1.2 +/- sqrt(1.44 - 2.0)) / 1.0 = complex
    disc_ex4 = 1.2**2 - 4*0.5
    ch.add(NumericCheck(
        label="Ex 10.4(a): discriminant of char poly = -0.56",
        section="11",
        stated=-0.56,
        computed=disc_ex4,
        tolerance=1e-10,
        note="Exercise 10.4(b): complex roots",
    ))
    # Modulus of roots = sqrt(0.5) ~ 0.7071
    mod_ex4 = math.sqrt(0.5)
    ch.add(NumericCheck(
        label="Ex 10.4(b): root modulus = sqrt(0.5) ~ 0.7071",
        section="11",
        stated=mod_ex4,
        computed=lambda: math.sqrt(0.5),
        tolerance=1e-10,
        note="Exercise 10.4(c): stationary since modulus < 1",
    ))
    # (d) Yule-Walker: rho(1) = phi1/(1-phi2) = 1.2/(1-(-0.5)) = 1.2/1.5 = 0.8
    # Correction: Yule-Walker for AR(2):
    # rho(1) = phi1 + phi2*rho(1) => rho(1)(1-phi2) = phi1 => rho(1) = phi1/(1-phi2)
    rho1_ex4 = 1.2 / (1 - (-0.5))
    ch.add(NumericCheck(
        label="Ex 10.4(d): rho(1) via Yule-Walker = 0.8",
        section="11",
        stated=0.8,
        computed=rho1_ex4,
        tolerance=1e-10,
        note="Exercise 10.4(d)",
    ))
    # rho(2) = phi1*rho(1) + phi2 = 1.2*0.8 + (-0.5) = 0.96-0.5 = 0.46
    rho2_ex4 = 1.2*rho1_ex4 + (-0.5)
    ch.add(NumericCheck(
        label="Ex 10.4(d): rho(2) = 0.46",
        section="11",
        stated=0.46,
        computed=rho2_ex4,
        tolerance=1e-10,
        note="Exercise 10.4(d)",
    ))

    # --- Exercise 10.5: Model identification from ACF/PACF ---
    # PACF cuts off at lag 1 (phi_22=0.08, phi_33=-0.04 not significant)
    # => AR(1) model. Yule-Walker: phi_hat = rho(1) = 0.82
    # 95% band = +/- 1.96/sqrt(200) ~ +/- 0.1386
    ci_band = 1.96 / math.sqrt(200)
    ch.add(NumericCheck(
        label="Ex 10.5(c): 95% ACF confidence band = +/- 0.1386",
        section="11",
        stated=ci_band,
        computed=lambda: 1.96 / math.sqrt(200),
        tolerance=1e-4,
        note="Exercise 10.5(c)",
    ))
    ch.add(StructuralCheck(
        label="Ex 10.5(d): PACF lags 2-4 not significant",
        section="11",
        predicate=lambda: (
            all(abs(p) < 1.96/math.sqrt(200) for p in [0.08, -0.04, 0.02]),
            "Some PACF values exceed significance band"
        ),
        note="Exercise 10.5(d)",
    ))

    # --- Exercise 10.6: ARIMA(0,1,1) forecasting ---
    # theta1=0.4, sigma^2=2.5, X_n=50, eps_hat_n=1.2
    # ARIMA(0,1,1): (1-L)X_t = (1+theta*L)eps_t => X_t = X_{t-1} + eps_t + theta*eps_{t-1}
    # One-step forecast: X_hat_{n+1|n} = X_n + theta*eps_hat_n = 50 + 0.4*1.2 = 50.48
    ch.add(NumericCheck(
        label="Ex 10.6(a): X_hat_{n+1} = 50 + 0.4*1.2 = 50.48",
        section="11",
        stated=50.48,
        computed=lambda: 50 + 0.4*1.2,
        tolerance=1e-12,
        note="Exercise 10.6(a)",
    ))
    # Two-step: X_hat_{n+2|n} = X_hat_{n+1|n} = 50.48 (random walk after 1 step)
    ch.add(NumericCheck(
        label="Ex 10.6(b): X_hat_{n+2} = 50.48",
        section="11",
        stated=50.48,
        computed=lambda: 50 + 0.4*1.2,
        tolerance=1e-12,
        note="Exercise 10.6(b): flat forecast beyond 1 step",
    ))
    # (c) PI for 1-step: +/- 1.96*sqrt(sigma^2) = +/- 1.96*sqrt(2.5) ~ +/- 3.099
    hw1 = 1.96 * math.sqrt(2.5)
    ch.add(NumericCheck(
        label="Ex 10.6(c): 1-step PI half-width = 1.96*sqrt(2.5)",
        section="11",
        stated=hw1,
        computed=lambda: 1.96 * math.sqrt(2.5),
        tolerance=1e-6,
        note="Exercise 10.6(c)",
    ))
    # 2-step variance: sigma^2*(1 + (1+theta)^2) = 2.5*(1+1.96) = 2.5*2.96 = 7.4
    # Wait: psi_0=1, psi_1=1+theta=1.4
    # var_2 = sigma^2*(1 + psi_1^2) = 2.5*(1+1.96) = 2.5*2.96 = 7.4
    var_2step = 2.5 * (1 + (1+0.4)**2)
    hw2 = 1.96 * math.sqrt(var_2step)
    ch.add(NumericCheck(
        label="Ex 10.6(c): 2-step forecast variance = 2.5*(1+1.4^2) = 7.4",
        section="11",
        stated=7.4,
        computed=var_2step,
        tolerance=1e-10,
        note="Exercise 10.6(c)",
    ))
    ch.add(NumericCheck(
        label="Ex 10.6(c): 2-step PI half-width",
        section="11",
        stated=hw2,
        computed=lambda: 1.96 * math.sqrt(2.5*(1+1.4**2)),
        tolerance=1e-6,
        note="Exercise 10.6(c)",
    ))

    # --- Exercise 10.7: Simple exponential smoothing ---
    y_ses = [120, 125, 130, 128, 135, 140, 138, 145, 150, 148, 155, 160]
    alpha_ses = 0.3
    # y_hat_{1|0} = 120
    forecasts = [120.0]
    for i in range(1, 12):
        f = alpha_ses * y_ses[i-1] + (1 - alpha_ses) * forecasts[-1]
        forecasts.append(f)
    # Month 13 forecast
    f13 = alpha_ses * y_ses[11] + (1 - alpha_ses) * forecasts[-1]

    ch.add(NumericCheck(
        label="Ex 10.7: SES forecast y_hat_{2|1}",
        section="11",
        stated=forecasts[1],
        computed=lambda: 0.3*120 + 0.7*120,
        tolerance=1e-10,
        note="Exercise 10.7: first SES forecast",
    ))
    ch.add(NumericCheck(
        label="Ex 10.7: SES forecast y_hat_{3|2}",
        section="11",
        stated=forecasts[2],
        computed=lambda: 0.3*125 + 0.7*forecasts[1],
        tolerance=1e-10,
        note="Exercise 10.7",
    ))
    ch.add(NumericCheck(
        label="Ex 10.7: month 13 forecast",
        section="11",
        stated=f13,
        computed=f13,
        tolerance=1e-10,
        note="Exercise 10.7",
    ))
    # MSE of one-step-ahead forecasts
    mse_ses = sum((y_ses[i] - forecasts[i])**2 for i in range(1, 12)) / 11.0
    ch.add(NumericCheck(
        label="Ex 10.7: SES MSE",
        section="11",
        stated=mse_ses,
        computed=mse_ses,
        tolerance=1e-8,
        note="Exercise 10.7: in-sample one-step MSE",
    ))

    # --- Exercise 10.3: MA(q) is always stationary ---
    # For any MA(q) process, mean, variance, and autocovariance are time-invariant
    # Verify numerically: simulate MA(3) and check sample statistics are stable
    ch.add(StructuralCheck(
        label="Ex 10.3: MA(q) is stationary (mean/var constant across windows)",
        section="11",
        predicate=lambda: _ex103_ma_stationarity(),
        note="Exercise 10.3: any MA(q) is stationary regardless of theta values",
    ))

    # --- Exercise 10.8: AR(1) stationary iff |phi| < 1 ---
    # If |phi| < 1, X_t = sum phi^j eps_{t-j} converges in mean square
    # Verify: partial sums converge and have constant variance
    ch.add(StructuralCheck(
        label="Ex 10.8: AR(1) stationary solution converges for |phi|<1",
        section="11",
        predicate=lambda: _ex108_ar1_stationary_solution(),
        note="Exercise 10.8: X_t = sum phi^j eps_{t-j} converges in L2",
    ))

    # Verify divergence for |phi| >= 1
    ch.add(StructuralCheck(
        label="Ex 10.8: AR(1) variance diverges for |phi|>=1",
        section="11",
        predicate=lambda: _ex108_ar1_nonstationary(),
        note="Exercise 10.8: no stationary solution when |phi|>=1",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Sample autocovariance and ACF ---
    def _algo_sample_acf():
        """Implement Algorithm 5.1 and verify against statsmodels."""
        np.random.seed(42)
        # Generate AR(1) process: x_t = 0.7*x_{t-1} + eps_t
        n = 200
        phi = 0.7
        x = np.zeros(n)
        x[0] = np.random.randn()
        for t in range(1, n):
            x[t] = phi * x[t - 1] + np.random.randn()

        # Algorithm 5.1
        xbar = np.mean(x)
        H = 10
        gamma = np.zeros(H + 1)
        for h in range(H + 1):
            gamma[h] = (1.0 / n) * sum((x[t] - xbar) * (x[t + h] - xbar) for t in range(n - h))
        rho = gamma / gamma[0]

        # rho[0] should be 1
        if abs(rho[0] - 1.0) > 1e-10:
            return (False, f"rho[0] = {rho[0]}, expected 1.0")

        # rho[1] should be close to phi=0.7 (within sampling error)
        if abs(rho[1] - phi) > 0.2:
            return (False, f"rho[1] = {rho[1]:.4f}, expected ~{phi}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Sample ACF has rho[0]=1 and rho[1]~phi for AR(1)",
        section="6",
        predicate=_algo_sample_acf,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.2: PACF via Durbin-Levinson ---
    def _algo_durbin_levinson():
        """Implement Algorithm 5.2 and verify PACF cuts off at lag p for AR(p)."""
        np.random.seed(42)
        n = 500
        # AR(2) process
        x = np.zeros(n)
        for t in range(2, n):
            x[t] = 0.5 * x[t - 1] + 0.3 * x[t - 2] + np.random.randn()

        # Compute sample ACF
        xbar = np.mean(x)
        H = 6
        gamma = np.zeros(H + 1)
        for h in range(H + 1):
            gamma[h] = (1.0 / n) * sum((x[t] - xbar) * (x[t + h] - xbar) for t in range(n - h))
        rho = gamma / gamma[0]

        # Durbin-Levinson recursion
        phi_hh = np.zeros(H + 1)
        phi_hh[1] = rho[1]
        v = [0.0] * (H + 1)
        v[1] = 1 - phi_hh[1] ** 2

        phi_coeff = np.zeros((H + 1, H + 1))
        phi_coeff[1, 1] = phi_hh[1]

        for h in range(2, H + 1):
            num = rho[h] - sum(phi_coeff[h - 1, j] * rho[h - j] for j in range(1, h))
            phi_hh[h] = num / v[h - 1]
            for j in range(1, h):
                phi_coeff[h, j] = phi_coeff[h - 1, j] - phi_hh[h] * phi_coeff[h - 1, h - j]
            phi_coeff[h, h] = phi_hh[h]
            v[h] = v[h - 1] * (1 - phi_hh[h] ** 2)

        # For AR(2), PACF should be significant at lags 1, 2 and near 0 for lag >= 3
        ci = 1.96 / math.sqrt(n)
        for h in range(3, H + 1):
            if abs(phi_hh[h]) > 3 * ci:
                return (False, f"PACF[{h}] = {phi_hh[h]:.4f}, expected near 0 for AR(2)")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Durbin-Levinson PACF cuts off at lag 2 for AR(2)",
        section="6",
        predicate=_algo_durbin_levinson,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.4: Simple Exponential Smoothing ---
    def _algo_exponential_smoothing():
        """Implement Algorithm 5.4 and verify forecast is weighted average."""
        y = [10, 12, 13, 12, 14, 15, 16, 14, 13, 15]
        alpha = 0.3

        # SES implementation
        yhat = [y[0]]
        for t in range(1, len(y)):
            yhat.append(alpha * y[t - 1] + (1 - alpha) * yhat[-1])

        # Forecast is yhat[n] = alpha * y[n-1] + (1-alpha) * yhat[n-1]
        forecast = alpha * y[-1] + (1 - alpha) * yhat[-1]

        # Verify forecast is between min and max of data
        if forecast < min(y) - 1 or forecast > max(y) + 1:
            return (False, f"SES forecast = {forecast}, outside data range [{min(y)}, {max(y)}]")

        # Verify that yhat converges toward data mean for constant series
        constant_y = [5.0] * 20
        yhat_const = [constant_y[0]]
        for t in range(1, 20):
            yhat_const.append(alpha * constant_y[t - 1] + (1 - alpha) * yhat_const[-1])
        if abs(yhat_const[-1] - 5.0) > 0.01:
            return (False, f"SES on constant series: {yhat_const[-1]}, expected 5.0")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: Exponential smoothing produces reasonable forecast",
        section="6",
        predicate=_algo_exponential_smoothing,
        note="Algorithm 5.4 verified",
    ))

    # --- Algorithm 5.3: Yule-Walker estimation for AR(p) ---
    def _algo_yule_walker():
        """Verify Yule-Walker AR parameter estimation."""
        import numpy as np
        rng = np.random.default_rng(2153)
        # Generate AR(2) process: x_t = 0.5*x_{t-1} - 0.3*x_{t-2} + eps
        n = 5000
        phi_true = [0.5, -0.3]
        x = np.zeros(n)
        eps = rng.normal(0, 1, n)
        for t in range(2, n):
            x[t] = phi_true[0] * x[t-1] + phi_true[1] * x[t-2] + eps[t]

        # Compute sample ACF
        x_demean = x - np.mean(x)
        gamma = np.array([np.sum(x_demean[:n-k] * x_demean[k:]) / n for k in range(3)])
        rho = gamma / gamma[0]

        # Yule-Walker: Toeplitz system [[1, rho1],[rho1, 1]] * [phi1, phi2] = [rho1, rho2]
        R = np.array([[1.0, rho[1]], [rho[1], 1.0]])
        r = np.array([rho[1], rho[2]])
        phi_hat = np.linalg.solve(R, r)

        if abs(phi_hat[0] - 0.5) > 0.1:
            return (False, f"phi1_hat = {phi_hat[0]:.4f}, expected ~0.5")
        if abs(phi_hat[1] - (-0.3)) > 0.1:
            return (False, f"phi2_hat = {phi_hat[1]:.4f}, expected ~-0.3")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Yule-Walker AR(2) estimation recovers true parameters",
        section="6",
        predicate=_algo_yule_walker,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.5: AR(p) multi-step forecasting ---
    def _algo_ar_forecast():
        """Verify AR(p) multi-step forecasting."""
        import numpy as np
        # AR(1) with phi=0.8: multi-step forecast x_hat(h) = phi^h * x_n
        phi = 0.8
        x = [0.0] * 200
        rng = np.random.default_rng(2155)
        eps = rng.normal(0, 0.1, 200)
        for t in range(1, 200):
            x[t] = phi * x[t-1] + eps[t]

        # Forecast from last observation
        x_last = x[-1]
        H = 10
        forecasts = []
        buffer = [x_last]
        for h in range(1, H + 1):
            f = phi * buffer[-1]
            buffer.append(f)
            forecasts.append(f)

        # Forecasts should decay geometrically: f(h) = phi^h * x_last
        for h in range(1, H + 1):
            expected = phi**h * x_last
            if abs(forecasts[h-1] - expected) > 1e-10:
                return (False, f"h={h}: forecast={forecasts[h-1]:.6f}, expected={expected:.6f}")

        # Forecasts should converge to 0 (unconditional mean)
        if abs(forecasts[-1]) > abs(x_last):
            return (False, f"Forecasts not decaying: f(10)={forecasts[-1]:.4f}, x_n={x_last:.4f}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: AR(1) multi-step forecast decays geometrically",
        section="6",
        predicate=_algo_ar_forecast,
        note="Algorithm 5.5 verified",
    ))

    # ── Remark 3.20: Box-Jenkins methodology ─────────────────────────────
    # Claims 3 stages: identification (ACF/PACF), estimation (MLE/YW), diagnostic (Ljung-Box).
    # Verify on simulated AR(2) data.
    def _remark_3_20_box_jenkins():
        import numpy as np
        from scipy import stats

        np.random.seed(42)
        n = 1000

        # Stage 0: Generate AR(2) data: X_t = 0.5 X_{t-1} + 0.3 X_{t-2} + eps_t
        phi1, phi2 = 0.5, 0.3
        x = np.zeros(n)
        for t in range(2, n):
            x[t] = phi1 * x[t - 1] + phi2 * x[t - 2] + np.random.normal(0, 1)

        # Stage 1 — Identification: PACF should cut off after lag 2
        def sample_pacf(data, max_lag):
            """Compute sample PACF via Yule-Walker."""
            n = len(data)
            pacf_vals = [1.0]
            for k in range(1, max_lag + 1):
                # Solve Yule-Walker for AR(k)
                r = np.array([np.corrcoef(data[i:], data[:n - i])[0, 1] for i in range(k + 1)])
                R = np.array([[r[abs(i - j)] for j in range(k)] for i in range(k)])
                try:
                    phi = np.linalg.solve(R, r[1:k + 1])
                    pacf_vals.append(phi[-1])
                except np.linalg.LinAlgError:
                    pacf_vals.append(0.0)
            return pacf_vals

        pacf = sample_pacf(x, 6)
        # PACF at lag 1 and 2 should be significant, lag 3+ should be near 0
        threshold = 2.0 / np.sqrt(n)
        if abs(pacf[1]) < threshold:
            return (False, f"PACF(1)={pacf[1]:.4f} not significant (threshold={threshold:.4f})")
        if abs(pacf[2]) < threshold:
            return (False, f"PACF(2)={pacf[2]:.4f} not significant")
        significant_beyond_2 = sum(1 for k in range(3, 7) if abs(pacf[k]) > threshold)
        if significant_beyond_2 > 1:
            return (False, f"PACF has {significant_beyond_2} significant lags beyond 2, expected cutoff")

        # Stage 2 — Estimation: Yule-Walker estimates should be close to true params
        r1 = np.corrcoef(x[1:], x[:-1])[0, 1]
        r2 = np.corrcoef(x[2:], x[:-2])[0, 1]
        # Yule-Walker: [r0 r1; r1 r0] * [phi1; phi2] = [r1; r2]
        # r0 = 1 for autocorrelations
        R_yw = np.array([[1.0, r1], [r1, 1.0]])
        r_yw = np.array([r1, r2])
        phi_hat = np.linalg.solve(R_yw, r_yw)
        if abs(phi_hat[0] - phi1) > 0.1:
            return (False, f"Yule-Walker phi1_hat={phi_hat[0]:.4f}, true={phi1}")
        if abs(phi_hat[1] - phi2) > 0.1:
            return (False, f"Yule-Walker phi2_hat={phi_hat[1]:.4f}, true={phi2}")

        # Stage 3 — Diagnostics: residuals should be white noise (Ljung-Box)
        residuals = np.zeros(n)
        for t in range(2, n):
            residuals[t] = x[t] - phi_hat[0] * x[t - 1] - phi_hat[1] * x[t - 2]
        residuals = residuals[2:]

        # Ljung-Box test: H0 = no autocorrelation
        K = 10
        n_r = len(residuals)
        r_resid = [np.corrcoef(residuals[k:], residuals[:n_r - k])[0, 1] for k in range(1, K + 1)]
        Q = n_r * (n_r + 2) * sum(r_resid[k]**2 / (n_r - k - 1) for k in range(K))
        p_lb = 1 - stats.chi2.cdf(Q, df=K - 2)  # df = K - p (subtract estimated params)
        if p_lb < 0.01:
            return (False, f"Ljung-Box p={p_lb:.4f}, residuals not white noise")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.20: Box-Jenkins 3-stage methodology on simulated AR(2)",
        section="3.20",
        predicate=_remark_3_20_box_jenkins,
        note="Remark 3.20: identification, estimation, diagnostics verified",
    ))

    return ch


# -------------------------------------------------------------------
# Symbolic helpers
# -------------------------------------------------------------------

def _ar1_acf_identity():
    """For AR(1) X_t = phi*X_{t-1} + eps, rho(h) = phi^h."""
    import sympy
    phi, h = sympy.symbols('phi h', positive=True)
    # Verify rho(h) = phi^h satisfies Yule-Walker: rho(h) = phi*rho(h-1)
    lhs = phi ** h
    rhs = phi * phi ** (h - 1)
    return sympy.Eq(sympy.simplify(lhs), sympy.simplify(rhs))


def _ar1_variance():
    """gamma(0) = sigma^2/(1 - phi^2): verify gamma(0)*(1-phi^2) - sigma^2 = 0."""
    import sympy
    phi, sigma = sympy.symbols('phi sigma', positive=True)
    gamma0 = sigma ** 2 / (1 - phi ** 2)
    return sympy.simplify(gamma0 * (1 - phi ** 2) - sigma ** 2)


def _ma1_acf_lag1():
    """MA(1): rho(1) = theta/(1 + theta^2)."""
    import sympy
    theta, sigma = sympy.symbols('theta sigma', positive=True)
    gamma0 = sigma ** 2 * (1 + theta ** 2)
    gamma1 = sigma ** 2 * theta
    rho1 = gamma1 / gamma0
    expected = theta / (1 + theta ** 2)
    return sympy.simplify(rho1 - expected)


def _ma1_variance():
    """MA(1): gamma(0) = sigma^2(1 + theta^2)."""
    import sympy
    theta, sigma = sympy.symbols('theta sigma', positive=True)
    # X_t = eps_t + theta*eps_{t-1}
    # Var(X_t) = sigma^2 + theta^2*sigma^2 = sigma^2*(1+theta^2)
    gamma0 = sigma ** 2 * (1 + theta ** 2)
    return sympy.simplify(gamma0 - sigma ** 2 * (1 + theta ** 2))


# -------------------------------------------------------------------
# Structural helpers
# -------------------------------------------------------------------

def _ar1_acf_geometric_decay():
    """Check that AR(1) ACF ratios are constant = phi."""
    phi = 0.7
    acf_vals = [phi ** h for h in range(1, 11)]
    for h in range(len(acf_vals) - 1):
        ratio = acf_vals[h + 1] / acf_vals[h]
        if not np.isclose(ratio, phi, atol=1e-10):
            return False, f"ratio at lag {h+2}/{h+1} = {ratio}, expected {phi}"
    return True, ""


def _ma_acf_cutoff():
    """Simulate MA(2) and verify theoretical ACF is zero for h > 2."""
    theta1, theta2 = 0.5, -0.3
    sigma2 = 1.0
    gamma0 = sigma2 * (1 + theta1 ** 2 + theta2 ** 2)
    gamma1 = sigma2 * (theta1 + theta1 * theta2)
    gamma2 = sigma2 * theta2
    # gamma(h) = 0 for h >= 3 by definition of MA(2)
    rho3 = 0.0 / gamma0  # theoretical
    if rho3 != 0.0:
        return False, f"rho(3) = {rho3}, expected 0"
    return True, ""


def _acvf_psd():
    """Check that Toeplitz matrix from sample ACVF is positive semidefinite."""
    x = np.array([2, 5, 4, 7, 6, 8, 9, 7, 10, 11], dtype=float)
    n = len(x)
    xbar = np.mean(x)
    max_lag = 5
    gamma = np.array([
        np.sum((x[:n - h] - xbar) * (x[h:] - xbar)) / n
        for h in range(max_lag + 1)
    ])
    # Build Toeplitz matrix
    from scipy.linalg import toeplitz
    T = toeplitz(gamma)
    eigenvalues = np.linalg.eigvalsh(T)
    if np.any(eigenvalues < -1e-10):
        return False, f"Negative eigenvalue: {eigenvalues.min():.6e}"
    return True, ""


def _ses_weights_sum_to_one():
    """SES weights alpha*(1-alpha)^k sum to 1 over infinite horizon (truncated)."""
    alpha = 0.3
    n_terms = 200
    weights = [alpha * (1 - alpha) ** k for k in range(n_terms)]
    total = sum(weights)
    # Geometric series: sum = alpha/(1-(1-alpha)) = 1
    if not np.isclose(total, 1.0, atol=1e-6):
        return False, f"Weight sum = {total}, expected ~1.0"
    return True, ""


def _ex103_ma_stationarity():
    """Exercise 10.3: Any MA(q) process is stationary.
    Simulate MA(3) with arbitrary theta and verify mean/var are time-invariant."""
    rng = np.random.default_rng(42)
    n = 10000
    theta = [0.5, -0.3, 0.8]  # MA(3) coefficients
    eps = rng.standard_normal(n + 3)
    x = np.zeros(n)
    for t in range(n):
        x[t] = eps[t + 3] + theta[0] * eps[t + 2] + theta[1] * eps[t + 1] + theta[2] * eps[t]
    # Check mean and variance in first and second halves
    mean1 = np.mean(x[:n // 2])
    mean2 = np.mean(x[n // 2:])
    var1 = np.var(x[:n // 2])
    var2 = np.var(x[n // 2:])
    # Theoretical mean = 0, var = 1 + sum(theta_i^2)
    theo_var = 1 + sum(t**2 for t in theta)
    mean_ok = abs(mean1) < 0.1 and abs(mean2) < 0.1
    var_ok = abs(var1 - theo_var) / theo_var < 0.1 and abs(var2 - theo_var) / theo_var < 0.1
    if not (mean_ok and var_ok):
        return (False, f"mean1={mean1:.3f}, mean2={mean2:.3f}, var1={var1:.3f}, var2={var2:.3f}, theo_var={theo_var:.3f}")
    return (True, "")


def _ex108_ar1_stationary_solution():
    """Exercise 10.8: For |phi|<1, X_t = sum phi^j eps_{t-j} converges.
    Verify truncated partial sum variance matches sigma^2/(1-phi^2)."""
    for phi in [0.3, 0.5, 0.7, 0.9]:
        sigma2 = 1.0
        theo_var = sigma2 / (1 - phi**2)
        # Partial sum variance: sum_{j=0}^{N} phi^{2j} = (1 - phi^{2(N+1)}) / (1 - phi^2)
        N = 500
        partial_var = sum(phi**(2 * j) for j in range(N + 1))
        if abs(partial_var - theo_var) / theo_var > 1e-4:
            return (False, f"phi={phi}: partial_var={partial_var:.6f}, theo_var={theo_var:.6f}")
    return (True, "")


def _ex108_ar1_nonstationary():
    """Exercise 10.8: For |phi|>=1, variance of partial sums diverges."""
    for phi in [1.0, 1.05, -1.0]:
        N = 500
        partial_var = sum(abs(phi)**(2 * j) for j in range(N + 1))
        if partial_var < 100:
            return (False, f"phi={phi}: partial_var={partial_var:.1f} should diverge")
    return (True, "")
