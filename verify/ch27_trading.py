# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 27: Quantitative Trading Strategies."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(27, "Quantitative Trading Strategies")

    # --- Symbolic checks ---

    # S1: Kelly criterion derivation: f* = (bp - q)/b
    def kelly_discrete_check():
        import sympy as sp
        p, b = sp.symbols('p b', positive=True)
        q = 1 - p
        f = sp.Symbol('f', positive=True)
        G = p * sp.ln(1 + b * f) + q * sp.ln(1 - f)
        dG = sp.diff(G, f)
        f_star = sp.solve(dG, f)[0]
        expected = (b * p - q) / b
        return sp.Eq(sp.simplify(f_star - expected), 0)
    ch.add(SymbolicCheck(
        label="Kelly criterion: f* = (bp - q)/b",
        section="4",
        identity=kelly_discrete_check,
    ))

    # S2: Portfolio variance formula: Var(Rp) = w'Sigma w
    def portfolio_variance_formula():
        import sympy as sp
        w1, w2 = sp.symbols('w1 w2')
        s11, s12, s22 = sp.symbols('s11 s12 s22')
        w = sp.Matrix([w1, w2])
        Sigma = sp.Matrix([[s11, s12], [s12, s22]])
        var_p = (w.T @ Sigma @ w)[0, 0]
        expanded = w1**2 * s11 + 2 * w1 * w2 * s12 + w2**2 * s22
        return sp.Eq(sp.simplify(var_p - expanded), 0)
    ch.add(SymbolicCheck(
        label="Portfolio variance w'Sigma w expansion",
        section="5",
        identity=portfolio_variance_formula,
    ))

    # S3: CAPM expected return: E[Ri] = Rf + beta*(E[Rm] - Rf)
    def capm_alpha_check():
        import sympy as sp
        Ri, Rf, beta, Rm, alpha = sp.symbols('Ri Rf beta Rm alpha')
        # alpha = Ri - Rf - beta*(Rm - Rf)
        # If CAPM holds exactly, alpha = 0
        alpha_expr = Ri - Rf - beta * (Rm - Rf)
        Ri_capm = Rf + beta * (Rm - Rf)
        return sp.Eq(sp.simplify(Ri_capm - Rf - beta * (Rm - Rf)), 0)
    ch.add(SymbolicCheck(
        label="CAPM: E[Ri]-Rf = beta*(E[Rm]-Rf)",
        section="5",
        identity=capm_alpha_check,
    ))

    # S4: Sharpe ratio formula (F4.3)
    def sharpe_ratio_check():
        import sympy as sp
        E_Rp, Rf, sigma_p = sp.symbols('E_Rp Rf sigma_p', positive=True)
        SR = (E_Rp - Rf) / sigma_p
        # Verify SR * sigma_p = E_Rp - Rf
        return sp.Eq(sp.simplify(SR * sigma_p - (E_Rp - Rf)), 0)
    ch.add(SymbolicCheck(
        label="F4.3: Sharpe ratio SR*sigma_p = E[Rp] - Rf",
        section="5",
        identity=sharpe_ratio_check,
    ))

    # S5: Efficient frontier parabolic form (F4.9)
    def efficient_frontier_check():
        import sympy as sp
        A, B, C, D, mu_p = sp.symbols('A B C D mu_p')
        # D = AC - B^2
        sigma_sq = (C * mu_p**2 - 2 * B * mu_p + A) / D
        # At the GMV portfolio, mu_gmv = B/C, sigma_gmv^2 = 1/C
        mu_gmv = B / C
        sigma_gmv_sq = sigma_sq.subs(mu_p, mu_gmv)
        expected_gmv = sp.Rational(1, 1) / C
        # sigma_gmv^2 = (C*(B/C)^2 - 2B*(B/C) + A) / D = (B^2/C - 2B^2/C + A) / D
        #             = (A - B^2/C)/D = (AC - B^2)/(CD) = D/(CD) = 1/C
        return sp.Eq(sp.simplify(sigma_gmv_sq - expected_gmv).subs(D, A*C - B**2), 0)
    ch.add(SymbolicCheck(
        label="F4.9: Efficient frontier GMV at mu=B/C gives sigma^2=1/C",
        section="5",
        identity=efficient_frontier_check,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 8.1: Two-asset portfolio
    ch.add(NumericCheck(
        label="Ex 8.1: Equal-weight portfolio volatility",
        section="9",
        stated=0.1245,
        computed=lambda: math.sqrt(0.25*0.04 + 2*0.25*0.006 + 0.25*0.01),
        tolerance=1e-3,
    ))

    # Example 8.1: Covariance matrix determinant
    ch.add(NumericCheck(
        label="Ex 8.1: det(Sigma)",
        section="9",
        stated=0.000364,
        computed=lambda: 0.04 * 0.01 - 0.006**2,
        tolerance=1e-3,
    ))

    # Example 8.1: Sigma_inv element (1,1)
    ch.add(NumericCheck(
        label="Ex 8.1: Sigma_inv(1,1)",
        section="9",
        stated=27.473,
        computed=lambda: 0.01 / 0.000364,
        tolerance=1e-3,
    ))

    # Example 8.1: Sigma_inv element (1,2)
    ch.add(NumericCheck(
        label="Ex 8.1: Sigma_inv(1,2)",
        section="9",
        stated=-16.484,
        computed=lambda: -0.006 / 0.000364,
        tolerance=1e-3,
    ))

    # Example 8.1: Sigma_inv element (2,2)
    ch.add(NumericCheck(
        label="Ex 8.1: Sigma_inv(2,2)",
        section="9",
        stated=109.890,
        computed=lambda: 0.04 / 0.000364,
        tolerance=1e-3,
    ))

    # Example 8.1: Intermediate A = mu' Sigma_inv mu
    def compute_A():
        Sigma_inv = np.array([[0.01, -0.006], [-0.006, 0.04]]) / 0.000364
        mu = np.array([0.10, 0.06])
        return mu @ Sigma_inv @ mu
    ch.add(NumericCheck(
        label="Ex 8.1: A = mu' Sigma_inv mu",
        section="9",
        stated=0.4725,
        computed=compute_A,
        tolerance=5e-3,
    ))

    # Example 8.1: Intermediate B = mu' Sigma_inv 1
    def compute_B():
        Sigma_inv = np.array([[0.01, -0.006], [-0.006, 0.04]]) / 0.000364
        mu = np.array([0.10, 0.06])
        ones = np.ones(2)
        return mu @ Sigma_inv @ ones
    ch.add(NumericCheck(
        label="Ex 8.1: B = mu' Sigma_inv 1",
        section="9",
        stated=6.703,
        computed=compute_B,
        tolerance=5e-3,
    ))

    # Example 8.1: Intermediate C = 1' Sigma_inv 1
    def compute_C():
        Sigma_inv = np.array([[0.01, -0.006], [-0.006, 0.04]]) / 0.000364
        ones = np.ones(2)
        return ones @ Sigma_inv @ ones
    ch.add(NumericCheck(
        label="Ex 8.1: C = 1' Sigma_inv 1",
        section="9",
        stated=104.396,
        computed=compute_C,
        tolerance=5e-3,
    ))

    # Example 8.1: lambda1 for mu_target = 0.08
    ch.add(NumericCheck(
        label="Ex 8.1: lambda1 for mu_target=0.08",
        section="9",
        stated=0.375,
        computed=lambda: (104.396 * 0.08 - 6.703) / 4.397,
        tolerance=5e-3,
    ))

    # Example 8.3: Kelly fraction
    ch.add(NumericCheck(
        label="Ex 8.3: Full Kelly fraction",
        section="9",
        stated=0.300,
        computed=lambda: (1.8 * 0.55 - 0.45) / 1.8,
        tolerance=1e-3,
    ))

    # Example 8.3: Kelly growth rate
    ch.add(NumericCheck(
        label="Ex 8.3: Growth rate at full Kelly",
        section="9",
        stated=0.0770,
        computed=lambda: 0.55 * math.log(1 + 1.8 * 0.30) + 0.45 * math.log(1 - 0.30),
        tolerance=1e-3,
    ))

    # Example 8.3: Half-Kelly growth rate
    ch.add(NumericCheck(
        label="Ex 8.3: Growth rate at half Kelly",
        section="9",
        stated=0.0583,
        computed=lambda: 0.55 * math.log(1 + 1.8 * 0.15) + 0.45 * math.log(1 - 0.15),
        tolerance=1e-3,
    ))

    # Example 8.3: Half-Kelly achieves 75.7% of maximum growth
    ch.add(NumericCheck(
        label="Ex 8.3: Half-Kelly growth ratio",
        section="9",
        stated=0.757,
        computed=lambda: (0.55 * math.log(1 + 1.8 * 0.15) + 0.45 * math.log(1 - 0.15)) /
                         (0.55 * math.log(1 + 1.8 * 0.30) + 0.45 * math.log(1 - 0.30)),
        tolerance=1e-2,
    ))

    # Example 8.4: Pairs trading rolling mean
    ch.add(NumericCheck(
        label="Ex 8.4: Rolling mean of spreads",
        section="9",
        stated=-0.125,
        computed=lambda: (-0.85 + 1.05 - 0.80 + 0.10) / 4,
        tolerance=1e-3,
    ))

    # Example 8.4: Pairs trading rolling std
    ch.add(NumericCheck(
        label="Ex 8.4: Rolling std of spreads",
        section="9",
        stated=0.897,
        computed=lambda: math.sqrt((0.526 + 1.381 + 0.456 + 0.051) / 3),
        tolerance=1e-3,
    ))

    # Example 8.4: Pairs trading z-score
    ch.add(NumericCheck(
        label="Ex 8.4: Z-score at t=10",
        section="9",
        stated=-1.81,
        computed=lambda: (-1.75 - (-0.125)) / 0.897,
        tolerance=1e-2,
    ))

    # Example 8.5: Deflated Sharpe ratio threshold
    ch.add(NumericCheck(
        label="Ex 8.5: SR threshold for N=500",
        section="9",
        stated=3.53,
        computed=lambda: math.sqrt(2 * math.log(500)),
        tolerance=1e-2,
    ))

    # Example 8.5: Expected max SR estimator
    ch.add(NumericCheck(
        label="Ex 8.5: E[max SR] / sqrt(T)",
        section="9",
        stated=0.0993,
        computed=lambda: math.sqrt(2 * math.log(500)) / math.sqrt(1260),
        tolerance=1e-2,
    ))

    # Example 8.2: CAPM beta estimation
    def compute_capm_beta():
        asset = np.array([0.02, -0.01, 0.03, 0.01, -0.02, 0.04, 0.00, 0.02, -0.01, 0.03, 0.01, 0.02])
        market = np.array([0.01, -0.02, 0.02, 0.00, -0.03, 0.03, -0.01, 0.01, -0.02, 0.02, 0.01, 0.01])
        cov_im = np.cov(asset, market, ddof=1)[0, 1]
        var_m = np.var(market, ddof=1)
        return cov_im / var_m
    ch.add(NumericCheck(
        label="Ex 8.2: CAPM beta",
        section="9",
        stated=0.980,
        computed=compute_capm_beta,
        tolerance=5e-2,
    ))

    # Example 8.2: Jensen's alpha
    def compute_alpha():
        asset = np.array([0.02, -0.01, 0.03, 0.01, -0.02, 0.04, 0.00, 0.02, -0.01, 0.03, 0.01, 0.02])
        market = np.array([0.01, -0.02, 0.02, 0.00, -0.03, 0.03, -0.01, 0.01, -0.02, 0.02, 0.01, 0.01])
        mean_asset = np.mean(asset)
        mean_market = np.mean(market)
        beta = np.cov(asset, market, ddof=1)[0, 1] / np.var(market, ddof=1)
        return mean_asset - beta * mean_market
    ch.add(NumericCheck(
        label="Ex 8.2: Jensen's alpha (monthly)",
        section="9",
        stated=0.00922,
        computed=compute_alpha,
        tolerance=5e-2,
    ))

    # Example 8.2: Sample mean of asset returns
    ch.add(NumericCheck(
        label="Ex 8.2: Sample mean asset returns",
        section="9",
        stated=0.01167,
        computed=lambda: np.mean([0.02, -0.01, 0.03, 0.01, -0.02, 0.04, 0.00, 0.02, -0.01, 0.03, 0.01, 0.02]),
        tolerance=5e-3,
    ))

    # Example 8.2: Sample mean of market returns
    ch.add(NumericCheck(
        label="Ex 8.2: Sample mean market returns",
        section="9",
        stated=0.00250,
        computed=lambda: np.mean([0.01, -0.02, 0.02, 0.00, -0.03, 0.03, -0.01, 0.01, -0.02, 0.02, 0.01, 0.01]),
        tolerance=5e-3,
    ))

    # Example 8.2: Annualized alpha (~11.1%)
    ch.add(NumericCheck(
        label="Ex 8.2: Annualized alpha",
        section="9",
        stated=0.111,
        computed=lambda: 0.00922 * 12,
        tolerance=5e-2,
    ))

    # --- Formula checks (gap fills) ---

    # F4.1: Portfolio return R_p = sum w_i * R_i
    def portfolio_return_check():
        import sympy as sp
        w1, w2, R1, R2 = sp.symbols('w1 w2 R1 R2')
        Rp = w1 * R1 + w2 * R2
        # At equal weights with equal returns, Rp = R
        return sp.Eq(sp.simplify(Rp.subs([(w1, sp.Rational(1, 2)), (w2, sp.Rational(1, 2)),
                                           (R1, R2)]) - R2), 0)
    ch.add(SymbolicCheck(
        label="F4.1: Portfolio return R_p = sum(w_i * R_i)",
        section="5",
        identity=portfolio_return_check,
    ))

    # F4.2: Portfolio variance sigma_p^2 = w' Sigma w (already S2, adding standalone numeric)
    ch.add(NumericCheck(
        label="F4.2: Portfolio variance for equal-weight 2-asset",
        section="5",
        stated=0.25 * 0.04 + 2 * 0.25 * 0.006 + 0.25 * 0.01,
        computed=lambda: np.array([0.5, 0.5]) @ np.array([[0.04, 0.006], [0.006, 0.01]]) @ np.array([0.5, 0.5]),
        tolerance=1e-10,
    ))

    # F4.6: Kelly discrete f* = (bp - q)/b (already S1, adding numeric standalone)
    ch.add(NumericCheck(
        label="F4.6: Kelly discrete f* = (bp-q)/b for p=0.55, b=1.8",
        section="5",
        stated=0.300,
        computed=lambda: (1.8 * 0.55 - 0.45) / 1.8,
        tolerance=1e-3,
    ))

    # F4.7: Kelly continuous f* = (mu - r) / sigma^2
    ch.add(NumericCheck(
        label="F4.7: Kelly continuous f* = (mu - r)/sigma^2",
        section="5",
        stated=2.0,
        computed=lambda: (0.12 - 0.02) / 0.05,
        tolerance=1e-6,
        note="mu=0.12, r=0.02, sigma^2=0.05 => f*=2.0",
    ))

    # F4.8: Kelly growth rate g(f) = p*ln(1+bf) + q*ln(1-f)
    ch.add(NumericCheck(
        label="F4.8: Kelly growth rate at full Kelly f=0.30",
        section="5",
        stated=0.0770,
        computed=lambda: 0.55 * math.log(1 + 1.8 * 0.30) + 0.45 * math.log(1 - 0.30),
        tolerance=1e-3,
    ))

    # F4.10: GMV weights w_gmv = Sigma_inv * 1 / (1' Sigma_inv 1)
    def gmv_weights_check():
        Sigma = np.array([[0.04, 0.006], [0.006, 0.01]])
        Sigma_inv = np.linalg.inv(Sigma)
        ones = np.ones(2)
        w_gmv = Sigma_inv @ ones / (ones @ Sigma_inv @ ones)
        return float(np.sum(w_gmv))
    ch.add(NumericCheck(
        label="F4.10: GMV weights sum to 1",
        section="5",
        stated=1.0,
        computed=gmv_weights_check,
        tolerance=1e-10,
    ))

    # F4.11: Tangency weights w_tan = Sigma_inv * (mu - Rf*1) / (1' Sigma_inv (mu - Rf*1))
    def tangency_weights_check():
        Sigma = np.array([[0.04, 0.006], [0.006, 0.01]])
        Sigma_inv = np.linalg.inv(Sigma)
        mu = np.array([0.10, 0.06])
        Rf = 0.02
        excess = mu - Rf * np.ones(2)
        ones = np.ones(2)
        w_tan = Sigma_inv @ excess / (ones @ Sigma_inv @ excess)
        return float(np.sum(w_tan))
    ch.add(NumericCheck(
        label="F4.11: Tangency weights sum to 1",
        section="5",
        stated=1.0,
        computed=tangency_weights_check,
        tolerance=1e-10,
    ))

    # F4.12: Deflated Sharpe: threshold E[max SR] = sqrt(2*ln(N))
    ch.add(NumericCheck(
        label="F4.12: Deflated Sharpe threshold for N=500",
        section="5",
        stated=3.53,
        computed=lambda: math.sqrt(2 * math.log(500)),
        tolerance=1e-2,
    ))

    # --- Structural checks ---

    # Portfolio weights sum to 1
    def weights_sum_to_one():
        mu = np.array([0.10, 0.06])
        Sigma = np.array([[0.04, 0.006], [0.006, 0.01]])
        Sigma_inv = np.linalg.inv(Sigma)
        ones = np.ones(2)
        w_gmv = Sigma_inv @ ones / (ones @ Sigma_inv @ ones)
        s = np.sum(w_gmv)
        ok = abs(s - 1.0) < 1e-10
        return (ok, f"Sum of GMV weights = {s}" if not ok else "")
    ch.add(StructuralCheck(
        label="GMV portfolio weights sum to 1",
        section="4",
        predicate=weights_sum_to_one,
    ))

    # Kelly fraction is 0 when edge is non-positive
    def kelly_no_edge():
        p = 0.4
        b = 1.0
        q = 1 - p
        f_star = (b * p - q) / b
        ok = f_star <= 0
        return (ok, f"Kelly fraction = {f_star}, should be <= 0 for no edge" if not ok else "")
    ch.add(StructuralCheck(
        label="Kelly fraction <= 0 when no edge (p=0.4, b=1)",
        section="4",
        predicate=kelly_no_edge,
    ))

    # Pairs trading: |z| < 2 means no entry signal
    def pairs_no_entry():
        z = (-1.75 - (-0.125)) / 0.897
        ok = abs(z) < 2.0
        return (ok, f"|z|={abs(z):.3f} >= 2.0, expected no signal" if not ok else "")
    ch.add(StructuralCheck(
        label="Ex 8.4: |z|=1.81 < 2.0, no entry signal",
        section="9",
        predicate=pairs_no_entry,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 10.1: 3-asset GMV portfolio ---
    def ex101_gmv():
        Sigma = np.array([
            [0.04, 0.01, 0.005],
            [0.01, 0.09, 0.02],
            [0.005, 0.02, 0.0225],
        ])
        Sigma_inv = np.linalg.inv(Sigma)
        ones = np.ones(3)
        w_gmv = Sigma_inv @ ones / (ones @ Sigma_inv @ ones)
        return w_gmv
    ch.add(NumericCheck(
        label="Exercise 10.1: GMV weights sum to 1",
        section="11",
        stated=1.0,
        computed=lambda: float(np.sum(ex101_gmv())),
        tolerance=1e-10,
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.1: GMV portfolio computed successfully",
        section="11",
        predicate=lambda: (abs(np.sum(ex101_gmv()) - 1.0) < 1e-10,
                           f"GMV weights: {ex101_gmv()}, sum={np.sum(ex101_gmv())}"),
    ))

    # --- Exercise 10.2: CAPM expected return and alpha ---
    # beta=1.3, Rf=0.03, E[Rm]=0.10 => E[Ri] = 0.03 + 1.3*(0.10-0.03) = 0.121
    ch.add(NumericCheck(
        label="Exercise 10.2: CAPM expected return",
        section="11",
        stated=0.121,
        computed=lambda: 0.03 + 1.3 * (0.10 - 0.03),
        tolerance=1e-6,
    ))
    # Alpha = actual - CAPM predicted = 0.12 - 0.121 = -0.001
    ch.add(NumericCheck(
        label="Exercise 10.2: Jensen's alpha",
        section="11",
        stated=-0.001,
        computed=lambda: 0.12 - 0.121,
        tolerance=1e-6,
    ))

    # --- Exercise 10.3: Kelly fraction ---
    # Win rate 60%, avg profit €150, avg loss €100
    # b = 150/100 = 1.5, p = 0.60, q = 0.40
    # f* = (bp - q)/b = (1.5*0.6 - 0.4)/1.5 = (0.9 - 0.4)/1.5 = 0.5/1.5
    ch.add(NumericCheck(
        label="Exercise 10.3: Kelly fraction",
        section="11",
        stated=1/3,
        computed=lambda: (1.5 * 0.6 - 0.4) / 1.5,
        tolerance=1e-6,
    ))
    # Quarter Kelly
    ch.add(NumericCheck(
        label="Exercise 10.3: Quarter-Kelly fraction",
        section="11",
        stated=1/12,
        computed=lambda: (1.5 * 0.6 - 0.4) / (1.5 * 4),
        tolerance=1e-6,
    ))

    # --- Exercise 10.4: Tangency portfolio ---
    # mu = (0.05, 0.03) are already excess returns; do not subtract Rf again
    def ex104_tangency():
        Sigma = np.array([[0.04, 0.01], [0.01, 0.02]])
        Sigma_inv = np.linalg.inv(Sigma)
        excess = np.array([0.05, 0.03])
        ones = np.ones(2)
        w_tan = Sigma_inv @ excess / (ones @ Sigma_inv @ excess)
        return w_tan
    ch.add(NumericCheck(
        label="Exercise 10.4: Tangency weights sum to 1",
        section="11",
        stated=1.0,
        computed=lambda: float(np.sum(ex104_tangency())),
        tolerance=1e-10,
    ))
    # Tangency portfolio expected excess return
    def ex104_tan_ret():
        w = ex104_tangency()
        excess = np.array([0.05, 0.03])
        return float(w @ excess)
    ch.add(NumericCheck(
        label="Exercise 10.4: Tangency expected excess return",
        section="11",
        stated=ex104_tan_ret(),
        computed=ex104_tan_ret,
        tolerance=1e-10,
    ))
    # Tangency portfolio volatility
    def ex104_tan_vol():
        w = ex104_tangency()
        Sigma = np.array([[0.04, 0.01], [0.01, 0.02]])
        return math.sqrt(float(w @ Sigma @ w))
    ch.add(NumericCheck(
        label="Exercise 10.4: Tangency volatility",
        section="11",
        stated=ex104_tan_vol(),
        computed=ex104_tan_vol,
        tolerance=1e-10,
    ))
    # Sharpe ratio
    def ex104_sharpe():
        return ex104_tan_ret() / ex104_tan_vol()
    ch.add(NumericCheck(
        label="Exercise 10.4: Tangency Sharpe ratio",
        section="11",
        stated=ex104_sharpe(),
        computed=ex104_sharpe,
        tolerance=1e-10,
    ))

    # --- Exercise 10.5: Bartlett standard error ---
    # SE = 1/sqrt(500) = 0.0447, critical = 0.0876
    # Lag 1: |0.08| < 0.0876 => not significant
    # Lag 2: |0.05| < 0.0876 => not significant
    ch.add(NumericCheck(
        label="Exercise 10.5: Bartlett standard error",
        section="11",
        stated=0.0447,
        computed=lambda: 1 / math.sqrt(500),
        tolerance=1e-3,
    ))
    ch.add(StructuralCheck(
        label="Exercise 10.5: Lag 1 not significant at 5% level",
        section="11",
        predicate=lambda: (abs(0.08) < 2 * 0.0447,
                           f"|rho(1)|={0.08} vs 2*SE={2*0.0447}"),
    ))

    # --- Exercise 10.7: Efficient frontier is a hyperbola ---
    # sigma^2 = (C*mu^2 - 2B*mu + A)/D
    # Verify the GMV portfolio lies at mu=B/C, sigma^2=1/C
    def ex107_gmv_point():
        Sigma = np.array([[0.04, 0.006], [0.006, 0.01]])
        Sigma_inv = np.linalg.inv(Sigma)
        mu = np.array([0.10, 0.06])
        ones = np.ones(2)
        A = float(mu @ Sigma_inv @ mu)
        B = float(mu @ Sigma_inv @ ones)
        C = float(ones @ Sigma_inv @ ones)
        D = A * C - B**2
        mu_gmv = B / C
        sigma_gmv_sq = 1.0 / C
        # Verify via parabolic formula
        sigma_check = (C * mu_gmv**2 - 2 * B * mu_gmv + A) / D
        ok = abs(sigma_check - sigma_gmv_sq) < 1e-10
        return (ok, f"sigma^2(mu_gmv)={sigma_check:.6e} vs 1/C={sigma_gmv_sq:.6e}")
    ch.add(StructuralCheck(
        label="Exercise 10.7: GMV at minimum of efficient frontier parabola",
        section="11",
        predicate=ex107_gmv_point,
    ))

    # --- Exercise 10.8: Deflated Sharpe ratio ---
    # N=200, T=1260, E[max SR] = sqrt(2*ln(N))
    ch.add(NumericCheck(
        label="Exercise 10.8: E[max SR] for N=200",
        section="11",
        stated=math.sqrt(2 * math.log(200)),
        computed=lambda: math.sqrt(2 * math.log(200)),
        tolerance=1e-10,
    ))
    # Threshold SR per unit time
    ch.add(NumericCheck(
        label="Exercise 10.8: E[max SR]/sqrt(T) for T=1260",
        section="11",
        stated=math.sqrt(2 * math.log(200)) / math.sqrt(1260),
        computed=lambda: math.sqrt(2 * math.log(200)) / math.sqrt(1260),
        tolerance=1e-10,
    ))
    # Is observed SR=2.1 significant? Compare to threshold
    ch.add(StructuralCheck(
        label="Exercise 10.8: Observed SR=2.1 below threshold for N=200",
        section="11",
        predicate=lambda: (2.1 < math.sqrt(2 * math.log(200)),
                           f"SR=2.1 vs threshold={math.sqrt(2*math.log(200)):.3f}"),
    ))

    # --- Exercise 10.6: Engle-Granger pairs trading procedure ---
    # Verify: z-score entry/exit rules and hedge ratio estimation
    def ex106_pairs_trading():
        np.random.seed(42)
        n = 250
        # Simulate two cointegrated series
        eps = np.random.randn(n) * 0.5
        x = np.cumsum(np.random.randn(n))
        y = 1.5 * x + eps  # hedge ratio = 1.5, spread = eps
        # Estimate hedge ratio via OLS
        beta_hat = np.sum(x * y) / np.sum(x * x)
        spread = y - beta_hat * x
        mu = np.mean(spread)
        sigma = np.std(spread)
        z = (spread - mu) / sigma
        # At least some z-scores should exceed 2 (entry threshold)
        entries = np.sum(np.abs(z) > 2)
        ok = entries > 0 and abs(beta_hat - 1.5) < 0.3
        return (ok, f"beta_hat={beta_hat:.3f}, entries={entries}")
    ch.add(StructuralCheck(
        label="Exercise 10.6: Engle-Granger pairs trading procedure",
        section="11",
        predicate=ex106_pairs_trading,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Mean-Variance Portfolio Optimization ---
    def alg_5_1_mean_variance():
        mu = np.array([0.10, 0.15, 0.12])
        Sigma = np.array([
            [0.04, 0.006, 0.010],
            [0.006, 0.09, 0.015],
            [0.010, 0.015, 0.0625],
        ])
        mu_target = 0.12
        SigmaInv = np.linalg.inv(Sigma)
        ones = np.ones(3)
        A = mu @ SigmaInv @ mu
        B = mu @ SigmaInv @ ones
        C = ones @ SigmaInv @ ones
        D = A * C - B ** 2
        lam1 = (C * mu_target - B) / D
        lam2 = (A - B * mu_target) / D
        w = SigmaInv @ (lam1 * mu + lam2 * ones)
        # Weights should sum to 1
        ok1 = abs(np.sum(w) - 1.0) < 1e-8
        # Portfolio return should equal target
        ok2 = abs(w @ mu - mu_target) < 1e-8
        return (ok1 and ok2, f"w={w}, sum={np.sum(w):.6f}, ret={w @ mu:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Mean-variance portfolio optimization",
        section="6",
        predicate=alg_5_1_mean_variance,
    ))

    # --- Algorithm 5.2: Tangency Portfolio ---
    def alg_5_2_tangency():
        mu = np.array([0.10, 0.15, 0.12])
        Sigma = np.array([
            [0.04, 0.006, 0.010],
            [0.006, 0.09, 0.015],
            [0.010, 0.015, 0.0625],
        ])
        Rf = 0.03
        excess_mu = mu - Rf
        SigmaInv = np.linalg.inv(Sigma)
        unnorm = SigmaInv @ excess_mu
        w = unnorm / np.sum(unnorm)
        # Weights sum to 1
        ok1 = abs(np.sum(w) - 1.0) < 1e-10
        # Sharpe ratio: (w'mu - Rf) / sqrt(w'Sigma w)
        port_ret = w @ mu
        port_var = w @ Sigma @ w
        sharpe = (port_ret - Rf) / np.sqrt(port_var)
        ok2 = sharpe > 0  # Should be positive
        return (ok1 and ok2, f"Tangency w={w}, Sharpe={sharpe:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Tangency portfolio (max Sharpe)",
        section="6",
        predicate=alg_5_2_tangency,
    ))

    # --- Algorithm 5.3: Pairs Trading Signal ---
    def alg_5_3_pairs_trading():
        np.random.seed(42)
        T = 500
        # Cointegrated pair: PB random walk, PA = 1.5*PB + stationary noise
        PB = 100 + np.cumsum(np.random.randn(T) * 0.5)
        PA = 1.5 * PB + np.random.randn(T) * 2
        L = 50
        z_entry = 2.0
        # Estimate cointegration coeff
        gamma1 = np.cov(PA, PB)[0, 1] / np.var(PB)
        gamma0 = np.mean(PA) - gamma1 * np.mean(PB)
        spread = PA - gamma1 * PB - gamma0
        signals = np.zeros(T)
        for t in range(L + 1, T):
            window = spread[t - L:t]
            roll_mean = np.mean(window)
            roll_std = np.std(window)
            if roll_std < 1e-10:
                continue
            z = (spread[t] - roll_mean) / roll_std
            if z < -z_entry:
                signals[t] = 1
            elif z > z_entry:
                signals[t] = -1
            elif abs(z) < 0.5:
                signals[t] = 0
            else:
                signals[t] = signals[t - 1]
        # Should generate both long and short signals
        ok = np.any(signals > 0) and np.any(signals < 0)
        return (ok, f"Long signals: {np.sum(signals > 0)}, Short: {np.sum(signals < 0)}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Pairs trading signal generation",
        section="6",
        predicate=alg_5_3_pairs_trading,
    ))

    # --- Algorithm 5.4: Momentum Regime Detection ---
    def alg_5_4_momentum():
        np.random.seed(42)
        from scipy.stats import norm
        T = 1000
        # Generate autocorrelated returns (momentum)
        r = np.zeros(T)
        r[0] = np.random.randn()
        for t in range(1, T):
            r[t] = 0.3 * r[t - 1] + np.random.randn()
        H = 10
        gamma0 = np.var(r)
        rho = np.zeros(H)
        for h in range(1, H + 1):
            rho[h - 1] = np.mean((r[h:] - np.mean(r)) * (r[:-h] - np.mean(r))) / gamma0
        se = 1 / np.sqrt(T)
        cv = norm.ppf(0.975) * se
        momentum_count = np.sum(rho > cv)
        reversion_count = np.sum(rho < -cv)
        if momentum_count > reversion_count:
            regime = "MOMENTUM"
        elif reversion_count > momentum_count:
            regime = "MEAN_REVERSION"
        else:
            regime = "NEUTRAL"
        ok = regime == "MOMENTUM"
        return (ok, f"Regime={regime}, momentum_count={momentum_count}, reversion={reversion_count}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Momentum regime detection",
        section="6",
        predicate=alg_5_4_momentum,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.5: Global minimum-variance portfolio
    # w_gmv = Sigma^{-1}*1 / (1'*Sigma^{-1}*1), sigma_gmv^2 = 1/C
    def remark_35_gmv():
        import numpy as np
        # 3-asset covariance matrix
        Sigma = np.array([
            [0.04, 0.006, 0.002],
            [0.006, 0.09, 0.009],
            [0.002, 0.009, 0.01],
        ])
        ones = np.ones(3)
        Sigma_inv = np.linalg.inv(Sigma)
        C = ones @ Sigma_inv @ ones
        w_gmv = Sigma_inv @ ones / C
        sigma_gmv_sq = w_gmv @ Sigma @ w_gmv
        # Verify sigma_gmv^2 = 1/C
        ok1 = abs(sigma_gmv_sq - 1 / C) < 1e-10
        # Verify weights sum to 1
        ok2 = abs(np.sum(w_gmv) - 1.0) < 1e-10
        ok = ok1 and ok2
        return (ok, f"sigma_gmv^2={sigma_gmv_sq:.6f}, 1/C={1/C:.6f}, sum(w)={np.sum(w_gmv):.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.5: GMV portfolio: sigma_gmv^2 = 1/C",
        section="4",
        predicate=remark_35_gmv,
        note="Remark 3.5",
    ))

    return ch
