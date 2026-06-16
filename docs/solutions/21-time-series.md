<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 21: Time Series

**Exercise 21.1.** AR(1) process: $X_t = 0.6X_{t-1} + \varepsilon_t$, $\varepsilon_t \sim \operatorname{WN}(0, 4)$.

??? success "Solution"

    (a) **Stationarity:** The characteristic polynomial is $\phi(z) = 1 - 0.6z$. The root is $z = 1/0.6 = 5/3 \approx 1.667$. Since $|z| > 1$ (equivalently $|\phi| = |0.6| < 1$), the process is **stationary**. $\checkmark$

    (b) **Autocovariance function.** For AR(1), $\gamma(h) = \phi^h \gamma(0)$.

    $\gamma(0) = \frac{\sigma^2}{1 - \phi^2} = \frac{4}{1 - 0.36} = \frac{4}{0.64} = 6.25$.

    $\gamma(1) = \phi \cdot \gamma(0) = 0.6 \times 6.25 = 3.75$.

    $\gamma(2) = \phi^2 \cdot \gamma(0) = 0.36 \times 6.25 = 2.25$.

    $\gamma(3) = \phi^3 \cdot \gamma(0) = 0.216 \times 6.25 = 1.35$.

    (c) **ACF:** $\rho(h) = \phi^h$.

    $\rho(1) = 0.6$, $\rho(2) = 0.36$, $\rho(3) = 0.216$.

    (d) **PACF:** For an AR(1) process, the PACF is nonzero only at lag 1:

    $\hat{\phi}_{11} = 0.6$, $\hat{\phi}_{22} = 0$, $\hat{\phi}_{33} = 0$.

    This is the signature of AR(1): exponentially decaying ACF and PACF that cuts off after lag 1.

    $\square$

---

**Exercise 21.2.** MA(2) process: $X_t = \varepsilon_t + 0.5\varepsilon_{t-1} - 0.3\varepsilon_{t-2}$, $\sigma^2 = 1$.

??? success "Solution"

    (a) **Stationarity:** Any MA($q$) process is stationary because the mean, variance and autocovariance depend only on the parameters $\theta_j$ and $\sigma^2$, not on $t$. $\mathbb{E}[X_t] = 0$, $\operatorname{Var}(X_t)$ is constant, and $\operatorname{Cov}(X_t, X_{t+h})$ depends only on $h$. $\checkmark$

    (b) **Autocovariances:** For MA(2) with $\theta_0 = 1$, $\theta_1 = 0.5$, $\theta_2 = -0.3$:

    $\gamma(0) = \sigma^2(\theta_0^2 + \theta_1^2 + \theta_2^2) = 1(1 + 0.25 + 0.09) = 1.34$.

    $\gamma(1) = \sigma^2(\theta_0\theta_1 + \theta_1\theta_2) = 1(0.5 + (0.5)(-0.3)) = 0.5 - 0.15 = 0.35$.

    $\gamma(2) = \sigma^2(\theta_0\theta_2) = 1(-0.3) = -0.3$.

    $\gamma(3) = 0$ (no overlap between $X_t$ and $X_{t-3}$ since MA(2) has memory of only 2 lags).

    (c) **Verify $\rho(h) = 0$ for $h > 2$:** For an MA($q$) process, $\gamma(h) = 0$ for $|h| > q$, because $X_t$ and $X_{t+h}$ depend on non-overlapping sets of innovations when $h > q$. Thus $\rho(h) = \gamma(h)/\gamma(0) = 0$ for $h > 2$. $\checkmark$

    (d) **Invertibility:** The MA polynomial is $\theta(z) = 1 + 0.5z - 0.3z^2$. For invertibility, all roots of $\theta(z) = 0$ must lie outside the unit circle.

    $-0.3z^2 + 0.5z + 1 = 0 \implies z = \frac{-0.5 \pm \sqrt{0.25 + 1.2}}{-0.6} = \frac{-0.5 \pm \sqrt{1.45}}{-0.6} = \frac{-0.5 \pm 1.204}{-0.6}$.

    $z_1 = \frac{-0.5 + 1.204}{-0.6} = \frac{0.704}{-0.6} = -1.173$.

    $z_2 = \frac{-0.5 - 1.204}{-0.6} = \frac{-1.704}{-0.6} = 2.840$.

    Both $|z_1| = 1.173 > 1$ and $|z_2| = 2.840 > 1$, so the process is **invertible**.

    $\square$

---

**Exercise 21.3.** Simple exponential smoothing.

??? success "Solution"

    Data: $y = (120, 125, 130, 128, 135, 140, 138, 145, 150, 148, 155, 160)$.
    $\alpha = 0.3$, $\hat{y}_{1|0} = y_1 = 120$.

    The recursion is $\hat{y}_{t+1|t} = \alpha y_t + (1 - \alpha)\hat{y}_{t|t-1}$.

    | $t$ | $y_t$ | $\hat{y}_{t|t-1}$ | $e_t = y_t - \hat{y}_{t|t-1}$ | $e_t^2$ |
    |-----|--------|--------------------|------|---------|
    | 1   | 120    | 120.00             | 0.00   | 0.00    |
    | 2   | 125    | 120.00             | 5.00   | 25.00   |
    | 3   | 130    | 121.50             | 8.50   | 72.25   |
    | 4   | 128    | 124.05             | 3.95   | 15.60   |
    | 5   | 135    | 125.24             | 9.77   | 95.36   |
    | 6   | 140    | 128.16             | 11.84  | 140.08  |
    | 7   | 138    | 131.72             | 6.29   | 39.52   |
    | 8   | 145    | 133.60             | 11.40  | 129.92  |
    | 9   | 150    | 137.02             | 12.98  | 168.51  |
    | 10  | 148    | 140.91             | 7.09   | 50.22   |
    | 11  | 155    | 143.04             | 11.96  | 143.11  |
    | 12  | 160    | 146.63             | 13.37  | 178.83  |

    Detailed computation of forecasts:

    $\hat{y}_{2|1} = 0.3(120) + 0.7(120) = 120.00$

    $\hat{y}_{3|2} = 0.3(125) + 0.7(120.00) = 37.5 + 84.0 = 121.50$

    $\hat{y}_{4|3} = 0.3(130) + 0.7(121.50) = 39.0 + 85.05 = 124.05$

    $\hat{y}_{5|4} = 0.3(128) + 0.7(124.05) = 38.4 + 86.84 = 125.24$

    $\hat{y}_{6|5} = 0.3(135) + 0.7(125.24) = 40.5 + 87.67 = 128.16$

    $\hat{y}_{7|6} = 0.3(140) + 0.7(128.16) = 42.0 + 89.71 = 131.72$

    $\hat{y}_{8|7} = 0.3(138) + 0.7(131.72) = 41.4 + 92.20 = 133.60$

    $\hat{y}_{9|8} = 0.3(145) + 0.7(133.60) = 43.5 + 93.52 = 137.02$

    $\hat{y}_{10|9} = 0.3(150) + 0.7(137.02) = 45.0 + 95.91 = 140.91$

    $\hat{y}_{11|10} = 0.3(148) + 0.7(140.91) = 44.4 + 98.64 = 143.04$

    $\hat{y}_{12|11} = 0.3(155) + 0.7(143.04) = 46.5 + 100.13 = 146.63$

    **Forecast for month 13:**

    $\hat{y}_{13|12} = 0.3(160) + 0.7(146.63) = 48.0 + 102.64 = 150.64$.

    **MSE:** Sum of $e_t^2$ for $t = 2, \ldots, 12$ (11 one-step-ahead forecasts):

    $\text{MSE} = \frac{25.00 + 72.25 + 15.60 + 95.36 + 140.08 + 39.52 + 129.92 + 168.51 + 50.22 + 143.11 + 178.83}{11} = \frac{1058.40}{11} \approx 96.22$.

    $\square$

---

**Exercise 21.4.** AR(2) process: $X_t = 1.2X_{t-1} - 0.5X_{t-2} + \varepsilon_t$.

??? success "Solution"

    (a) **Characteristic polynomial:** $\phi(z) = 1 - 1.2z + 0.5z^2$.

    (b) **Roots:** Set $0.5z^2 - 1.2z + 1 = 0$, so $z = \frac{1.2 \pm \sqrt{1.44 - 2.0}}{1.0} = \frac{1.2 \pm \sqrt{-0.56}}{1.0}$.

    The roots are complex: $z = 1.2 \pm 0.7483i$.

    $|z| = \sqrt{1.44 + 0.56} = \sqrt{2.0} = \sqrt{2} \approx 1.414$.

    (c) **Stationarity:** Since $|z_1| = |z_2| = \sqrt{2} > 1$ (all roots are outside the unit circle), the process is **stationary**. Equivalently, the spectral radius of the companion matrix is $1/\sqrt{2} \approx 0.707 < 1$.

    (d) **Yule–Walker equations for AR(2):**

    $\rho(1) = \phi_1 + \phi_2 \rho(1) \implies \rho(1) = 1.2 + (-0.5)\rho(1) \implies 1.5\rho(1) = 1.2 \implies \rho(1) = 0.8$.

    $\rho(2) = \phi_1 \rho(1) + \phi_2 = 1.2(0.8) + (-0.5) = 0.96 - 0.5 = 0.46$.

    $\square$

---

**Exercise 21.5.** Model identification from ACF/PACF patterns.

??? success "Solution"

    (a) The ACF decays gradually ($0.82, 0.71, 0.59, 0.50$) and the PACF has a significant value at lag 1 ($\hat{\phi}_{11} = 0.82$) with values near zero at higher lags ($0.08, -0.04, 0.02$). This is the classic signature of an **AR(1)** model: slowly decaying ACF and PACF that cuts off after lag 1.

    (b) **Yule–Walker estimation for AR(1):** $\hat{\phi} = \hat{\rho}(1) = 0.82$.

    The estimated model is $X_t = 0.82 X_{t-1} + \varepsilon_t$.

    (c) **95% confidence band for ACF:** Under the null hypothesis of white noise, $\hat{\rho}(h) \approx N(0, 1/n)$ for large $n$. The approximate 95% band is:

    $$\pm \frac{1.96}{\sqrt{n}} = \pm \frac{1.96}{\sqrt{200}} = \pm \frac{1.96}{14.14} = \pm 0.1386.$$

    All sample ACF values ($0.82, 0.71, 0.59, 0.50$) are well outside this band, confirming significant autocorrelation.

    (d) **PACF significance:** The critical value is $\pm 0.1386$. The PACF values at lags 2, 3, 4 are $0.08, -0.04, 0.02$, all within the $\pm 0.1386$ band. Therefore, **none of the PACF values at lags 2, 3, 4 are significant**, confirming the AR(1) identification.

    $\square$

---

**Exercise 21.6.** ARIMA(0,1,1) forecasting: $\theta_1 = 0.4$, $\sigma^2 = 2.5$, $X_n = 50$, $\hat{\varepsilon}_n = 1.2$.

??? success "Solution"

    ARIMA(0,1,1) means $(1 - L)X_t = (1 + \theta_1 L)\varepsilon_t$, or equivalently $X_t = X_{t-1} + \varepsilon_t + \theta_1 \varepsilon_{t-1}$.

    (a) **One-step-ahead forecast:**

    $$\hat{X}_{n+1|n} = X_n + \theta_1 \hat{\varepsilon}_n = 50 + 0.4(1.2) = 50 + 0.48 = 50.48.$$

    (b) **Two-step-ahead forecast:**

    $$\hat{X}_{n+2|n} = \hat{X}_{n+1|n} + \theta_1 \mathbb{E}[\varepsilon_{n+1}] = 50.48 + 0.4(0) = 50.48.$$

    (Since $\mathbb{E}[\varepsilon_{n+1}] = 0$ at forecast time, the two-step forecast equals the one-step forecast for ARIMA(0,1,1).)

    (c) **Prediction intervals:**

    For ARIMA(0,1,1), the forecast error variances are:

    One-step: $\operatorname{Var}(e_{n+1|n}) = \sigma^2 = 2.5$, so $\text{SE}_1 = \sqrt{2.5} = 1.581$.

    Two-step: $\operatorname{Var}(e_{n+2|n}) = \sigma^2(1 + (1 + \theta_1)^2) = 2.5(1 + 1.96) = 2.5 \times 2.96 = 7.4$, so $\text{SE}_2 = \sqrt{7.4} = 2.720$.

    (The two-step error comes from: $e_{n+2|n} = \varepsilon_{n+2} + (1 + \theta_1)\varepsilon_{n+1}$.)

    95% prediction intervals:

    One-step: $50.48 \pm 1.96 \times 1.581 = 50.48 \pm 3.10 = (47.38, 53.58)$.

    Two-step: $50.48 \pm 1.96 \times 2.720 = 50.48 \pm 5.33 = (45.15, 55.81)$.

    $\square$

---

**Exercise 21.7.** Prove any MA($q$) process is stationary.

??? success "Solution"

    Let $X_t = \sum_{j=0}^{q}\theta_j \varepsilon_{t-j}$ where $\theta_0 = 1$ and $\varepsilon_t \sim \operatorname{WN}(0, \sigma^2)$.

    **Mean:** $\mathbb{E}[X_t] = \sum_{j=0}^q \theta_j \mathbb{E}[\varepsilon_{t-j}] = 0$ for all $t$.

    **Variance:**

    $$\operatorname{Var}(X_t) = \mathbb{E}[X_t^2] = \mathbb{E}\!\left[\left(\sum_{j=0}^q \theta_j \varepsilon_{t-j}\right)^2\right] = \sum_{j=0}^q \theta_j^2 \sigma^2 = \sigma^2 \sum_{j=0}^q \theta_j^2,$$

    using $\mathbb{E}[\varepsilon_s \varepsilon_r] = \sigma^2 \mathbf{1}_{s=r}$. This does not depend on $t$.

    **Autocovariance:** For $h \geq 0$:

    $$\gamma(h) = \operatorname{Cov}(X_t, X_{t+h}) = \mathbb{E}\!\left[\left(\sum_{j=0}^q \theta_j\varepsilon_{t-j}\right)\left(\sum_{k=0}^q \theta_k\varepsilon_{t+h-k}\right)\right] = \sigma^2 \sum_{j=0}^{q-h} \theta_j \theta_{j+h},$$

    for $0 \leq h \leq q$, and $\gamma(h) = 0$ for $h > q$.

    This expression depends only on $h$, not on $t$. Since the mean, variance and autocovariance are all independent of $t$, the process is (weakly) **stationary**. No conditions on $\theta_1, \ldots, \theta_q$ are needed.

    $\square$

---

**Exercise 21.8.** Prove stationarity conditions for AR(1).

??? success "Solution"

    Consider $X_t = \phi X_{t-1} + \varepsilon_t$ where $\varepsilon_t \sim \operatorname{WN}(0, \sigma^2)$.

    **Case $|\phi| \geq 1$: No stationary solution.**

    Suppose for contradiction that a stationary solution exists with finite variance $\gamma(0) = \operatorname{Var}(X_t)$. From $X_t = \phi X_{t-1} + \varepsilon_t$:

    $$\gamma(0) = \operatorname{Var}(X_t) = \phi^2 \operatorname{Var}(X_{t-1}) + \sigma^2 = \phi^2 \gamma(0) + \sigma^2$$

    (using independence of $X_{t-1}$ and $\varepsilon_t$ for a stationary solution). Then $\gamma(0)(1 - \phi^2) = \sigma^2$. If $|\phi| \geq 1$, then $1 - \phi^2 \leq 0$, so either $\gamma(0) \leq 0$ (impossible for a nondegenerate process) or $\gamma(0) = \infty$. Contradiction.

    $\square$

    **Case $|\phi| < 1$: Unique stationary solution $X_t = \sum_{j=0}^{\infty}\phi^j\varepsilon_{t-j}$.**

    By back-substitution: $X_t = \varepsilon_t + \phi X_{t-1} = \varepsilon_t + \phi\varepsilon_{t-1} + \phi^2 X_{t-2} = \cdots = \sum_{j=0}^{N}\phi^j\varepsilon_{t-j} + \phi^{N+1}X_{t-N-1}$.

    As $N \to \infty$, $\phi^{N+1}X_{t-N-1} \to 0$ in mean square (since $\mathbb{E}[|\phi^{N+1}X_{t-N-1}|^2] = \phi^{2(N+1)}\gamma(0) \to 0$). So formally $X_t = \sum_{j=0}^{\infty}\phi^j\varepsilon_{t-j}$.

    **Convergence in mean square:**

    $$\mathbb{E}\!\left[\left(\sum_{j=0}^{\infty}\phi^j\varepsilon_{t-j}\right)^2\right] = \sum_{j=0}^{\infty}\phi^{2j}\sigma^2 = \frac{\sigma^2}{1 - \phi^2} < \infty.$$

    The partial sums $S_N = \sum_{j=0}^N \phi^j \varepsilon_{t-j}$ form a Cauchy sequence in $L^2$: for $M > N$,

    $$\mathbb{E}[(S_M - S_N)^2] = \sigma^2\sum_{j=N+1}^{M}\phi^{2j} \to 0 \text{ as } N, M \to \infty.$$

    So the series converges in mean square. $\checkmark$

    **Constant mean:** $\mathbb{E}[X_t] = \sum_{j=0}^{\infty}\phi^j \mathbb{E}[\varepsilon_{t-j}] = 0$ for all $t$. $\checkmark$

    **Autocovariance depends only on lag:**

    $$\gamma(h) = \operatorname{Cov}(X_t, X_{t+h}) = \mathbb{E}\!\left[\sum_{j=0}^{\infty}\phi^j\varepsilon_{t-j}\sum_{k=0}^{\infty}\phi^k\varepsilon_{t+h-k}\right] = \sigma^2\sum_{j=0}^{\infty}\phi^j\phi^{j+h} = \sigma^2\phi^h\sum_{j=0}^{\infty}\phi^{2j} = \frac{\sigma^2\phi^h}{1-\phi^2}.$$

    This depends only on $h$, not on $t$. $\checkmark$

    **Uniqueness:** If $Y_t$ is another stationary solution, then $Z_t = X_t - Y_t$ satisfies $Z_t = \phi Z_{t-1}$ with $\operatorname{Var}(Z_t) = \phi^2 \operatorname{Var}(Z_{t-1})$. By stationarity, $\operatorname{Var}(Z_t) = \phi^2 \operatorname{Var}(Z_t)$, so $(1 - \phi^2)\operatorname{Var}(Z_t) = 0$, hence $\operatorname{Var}(Z_t) = 0$ and $Z_t = 0$ a.s.

    $\square$

---
