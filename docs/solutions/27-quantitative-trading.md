<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 27: Quantitative Trading Strategies

**Exercise 27.1.** Compute the global minimum-variance portfolio for three assets.

??? success "Solution"

    Given $\boldsymbol{\mu} = (0.08, 0.12, 0.06)'$ and

    $$\Sigma = \begin{pmatrix} 0.04 & 0.01 & 0.005 \\ 0.01 & 0.09 & 0.02 \\ 0.005 & 0.02 & 0.0225 \end{pmatrix}.$$

    The global minimum-variance portfolio weights are $\mathbf{w}_{\text{gmv}} = \Sigma^{-1}\mathbf{1}/(\mathbf{1}'\Sigma^{-1}\mathbf{1})$.

    First compute $\Sigma^{-1}$. The determinant of $\Sigma$ is $\det(\Sigma) = 0.04(0.09 \times 0.0225 - 0.02^2) - 0.01(0.01 \times 0.0225 - 0.02 \times 0.005) + 0.005(0.01 \times 0.02 - 0.09 \times 0.005) = 0.04(0.002025 - 0.0004) - 0.01(0.000225 - 0.0001) + 0.005(0.0002 - 0.00045) = 0.04(0.001625) - 0.01(0.000125) + 0.005(-0.00025) = 0.0000650 - 0.00000125 - 0.00000125 = 0.0000625$.

    Computing the inverse (using cofactors):

    $$\Sigma^{-1} \approx \begin{pmatrix} 30.0 & -2.0 & -4.0 \\ -2.0 & 13.0 & -10.0 \\ -4.0 & -10.0 & 56.0 \end{pmatrix}.$$

    Then:

    $$\Sigma^{-1}\mathbf{1} = (24.0,\ 1.0,\ 42.0)', \quad \mathbf{1}'\Sigma^{-1}\mathbf{1} = 24.0 + 1.0 + 42.0 = 67.0.$$

    $$\mathbf{w}_{\text{gmv}} = \frac{1}{67.0}(24.0,\ 1.0,\ 42.0)' = (0.358,\ 0.015,\ 0.627)'.$$

    Verification: $0.358 + 0.015 + 0.627 = 1.000$. The weights sum to one.

    Note: the inverse is rounded to integer entries; exact computation gives weights $(0.358, 0.015, 0.627)$ to three decimal places. $\square$

    The minimum-variance portfolio heavily weights asset 3 (lowest volatility, $\sigma_3 = 0.15$) and asset 1 (moderate volatility, low covariance with asset 3), while nearly excluding asset 2 (highest volatility, $\sigma_2 = 0.30$).

---

**Exercise 27.2.** CAPM expected return and Jensen's alpha.

??? success "Solution"

    With $\beta_i = 1.3$, $R_f = 0.03$, $\mathbb{E}[R_m] = 0.10$:

    $$\mathbb{E}[R_i] = R_f + \beta_i(\mathbb{E}[R_m] - R_f) = 0.03 + 1.3(0.10 - 0.03) = 0.03 + 1.3 \times 0.07 = 0.03 + 0.091 = 0.121 = 12.1\%.$$

    If the actual expected return is $12\%$, Jensen's alpha is:

    $$\alpha_i = \mathbb{E}[R_i]_{\text{actual}} - \mathbb{E}[R_i]_{\text{CAPM}} = 0.12 - 0.121 = -0.001 = -0.1\%.$$

    The stock underperforms its CAPM prediction by 10 basis points.

    $\square$

---

**Exercise 27.3.** Kelly criterion for a strategy with 60% win rate.

??? success "Solution"

    Win probability $p = 0.60$, loss probability $q = 0.40$. Average profit per winner = €150, average loss per loser = €100. The win/loss ratio is $b = 150/100 = 1.5$.

    $$f^* = \frac{bp - q}{b} = \frac{1.5 \times 0.60 - 0.40}{1.5} = \frac{0.90 - 0.40}{1.5} = \frac{0.50}{1.5} = 0.333.$$

    Quarter-Kelly: $f_{1/4} = 0.333/4 = 0.083$.

    The full Kelly fraction advises risking 33.3% of capital per trade; the quarter-Kelly fraction of 8.3% provides much more conservative sizing with approximately $1 - (1-1/4)^2 = 7/16 \approx 43.75\%$ of the full Kelly growth rate (approximately, under the quadratic approximation $G(f) \approx \mu f - \frac{1}{2}\sigma^2 f^2$), but substantially lower drawdown risk.

    $\square$

---

**Exercise 27.4.** Tangency portfolio for two assets.

??? success "Solution"

    The exercise states that $(0.05, 0.03)'$ are already excess returns, so the tangency formula $\mathbf{w}^* = \Sigma^{-1}\boldsymbol{\mu}_{\text{excess}}/(\mathbf{1}'\Sigma^{-1}\boldsymbol{\mu}_{\text{excess}})$ uses them directly without subtracting $R_f$ again.

    $$\Sigma = \begin{pmatrix} 0.04 & 0.01 \\ 0.01 & 0.02 \end{pmatrix}.$$

    $\det(\Sigma) = 0.04 \times 0.02 - 0.01^2 = 0.0008 - 0.0001 = 0.0007$.

    $$\Sigma^{-1} = \frac{1}{0.0007}\begin{pmatrix} 0.02 & -0.01 \\ -0.01 & 0.04 \end{pmatrix} = \begin{pmatrix} 28.571 & -14.286 \\ -14.286 & 57.143 \end{pmatrix}.$$

    Unnormalised weights:

    $$\Sigma^{-1}\boldsymbol{\mu}_{\text{excess}} = \begin{pmatrix} 28.571 \times 0.05 + (-14.286) \times 0.03 \\ -14.286 \times 0.05 + 57.143 \times 0.03 \end{pmatrix} = \begin{pmatrix} 1.42855 - 0.42858 \\ -0.71430 + 1.71429 \end{pmatrix} = \begin{pmatrix} 1.0 \\ 1.0 \end{pmatrix}.$$

    Sum: $1.0 + 1.0 = 2.0$.

    Tangency weights: $\mathbf{w}^* = (1.0/2.0,\ 1.0/2.0)' = (0.5,\ 0.5)'$.

    Expected return (raw returns are $\boldsymbol{\mu} = \boldsymbol{\mu}_{\text{excess}} + R_f\mathbf{1} = (0.07, 0.05)'$): $\mathbb{E}[R_p] = 0.5 \times 0.07 + 0.5 \times 0.05 = 0.035 + 0.025 = 0.06$.

    Portfolio variance: $\sigma_p^2 = 0.5^2 \times 0.04 + 2 \times 0.5 \times 0.5 \times 0.01 + 0.5^2 \times 0.02 = 0.01 + 0.005 + 0.005 = 0.02$.

    $\sigma_p = \sqrt{0.02} = 0.1414$.

    Sharpe ratio: $\text{SR} = (0.06 - 0.02)/0.1414 = 0.04/0.1414 = 0.2828$.

    $\square$

---

**Exercise 27.5.** Significance of autocorrelation estimates.

??? success "Solution"

    With $T = 500$ observations, Bartlett standard error $= 1/\sqrt{500} = 0.0447$. At the 5% level, the critical value is $\pm 1.96 \times 0.0447 = \pm 0.0876$.

    - $\hat{\rho}(1) = 0.08$: $|0.08| < 0.0876$. Not significant.
    - $\hat{\rho}(2) = 0.05$: $|0.05| < 0.0876$. Not significant.
    - $\hat{\rho}(3) = 0.02$: Not significant.
    - $\hat{\rho}(4) = -0.01$: Not significant.

    None of the autocorrelations are individually significant at the 5% level. The value $\hat{\rho}(1) = 0.08$ is close to the boundary, but does not cross it. All positive lags show small positive autocorrelations (rather than random signs) is weakly suggestive of momentum, but the evidence is not statistically significant for any single lag. A Ljung–Box test combining all lags might provide stronger evidence. The lack of significant negative autocorrelations rules out a pure mean-reversion strategy. A cautious approach would be to continue monitoring or test on out-of-sample data before deploying a momentum strategy.

    $\square$

---

**Exercise 27.6.** Engle–Granger pairs trading procedure.

??? success "Solution"

    **(i) Test for cointegration:** Run the Augmented Dickey–Fuller (ADF) test on each individual price series $P_A$ and $P_B$ to confirm both are $I(1)$ (non-stationary). Then regress $P_{A,t} = \gamma_0 + \gamma_1 P_{B,t} + u_t$ by OLS. Apply the ADF test to the estimated residuals $\hat{u}_t$. If the null of a unit root is rejected (using Engle–Granger critical values, which are more conservative than standard ADF tables because the residuals are estimated), the pair is cointegrated.

    **(ii) Estimate hedge ratio:** The OLS slope $\hat{\gamma}_1$ is the hedge ratio. For every euro long in asset $A$, sell $\hat{\gamma}_1$ euros of asset $B$.

    **(iii) Construct z-score:** Compute the spread $u_t = P_{A,t} - \hat{\gamma}_1 P_{B,t} - \hat{\gamma}_0$. Over a rolling lookback window of length $L$, compute the rolling mean $\bar{u}$ and rolling standard deviation $\hat{\sigma}_u$. The z-score is $z_t = (u_t - \bar{u})/\hat{\sigma}_u$.

    **(iv) Entry/exit rules:** Open a long spread position when $z_t < -z_{\text{entry}}$ (typically $-2$); open a short spread position when $z_t > z_{\text{entry}}$. Close the position when $|z_t| < z_{\text{exit}}$ (typically $0.5$), indicating the spread has reverted to its mean.

    **Failure conditions:** The strategy fails when (a) the cointegration relationship breaks down (structural break), causing the spread to diverge rather than revert; (b) the hedge ratio changes over time and the rolling window is too slow to adapt; (c) transaction costs exceed the expected profit from mean reversion; (d) the spread takes longer to revert than the trader's capital or risk limits allow.

    $\square$

---

**Exercise 27.7.** The efficient frontier is a hyperbola.

??? success "Solution"

    Starting from $\sigma_p^2 = (C\mu_p^2 - 2B\mu_p + A)/D$, complete the square in $\mu_p$:

    $$D\sigma_p^2 = C\left(\mu_p^2 - \frac{2B}{C}\mu_p\right) + A = C\left(\mu_p - \frac{B}{C}\right)^2 - \frac{B^2}{C} + A = C\left(\mu_p - \frac{B}{C}\right)^2 + \frac{AC - B^2}{C} = C\left(\mu_p - \frac{B}{C}\right)^2 + \frac{D}{C}.$$

    Rearranging:

    $$\frac{\left(\mu_p - B/C\right)^2}{D/C^2} - \frac{\sigma_p^2}{1/C} = -1.$$

    Or equivalently:

    $$\frac{\sigma_p^2}{1/C} - \frac{(\mu_p - B/C)^2}{D/C^2} = 1.$$

    This is the standard form of a hyperbola $\frac{x^2}{a^2} - \frac{y^2}{b^2} = 1$ in $(\sigma_p, \mu_p)$ space with centre $(0, B/C)$, $a^2 = 1/C$ and $b^2 = D/C^2$.

    The asymptotes are $\mu_p - B/C = \pm (b/a)\sigma_p = \pm \sqrt{D/C} \cdot \sigma_p$. The upper branch (efficient frontier) has positive slope asymptote. $\square$

---

**Exercise 27.8.** Multiple-testing correction.

??? success "Solution"

    With $N = 200$ parameter combinations and $T = 1260$ daily observations:

    $$\text{SR}_{\text{threshold}} \approx \sqrt{2\ln N} = \sqrt{2\ln 200} = \sqrt{2 \times 5.2983} = \sqrt{10.5966} = 3.255.$$

    The observed SR of $2.1$ is well below the threshold of $3.255$. The strategy does not show statistically significant skill after correction for multiple testing.

    The minimum SR required for significance at the $N=200$ testing level is approximately $3.26$. This is a much higher bar than the naive $\text{SR} > 0$ or even $\text{SR} > 2$ thresholds often cited informally. The correction reflects that testing 200 combinations virtually guarantees finding an impressive-looking backtest result even when no strategy has genuine skill.

    $\square$

---
