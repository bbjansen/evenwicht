<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 14: Probability Distributions

**Exercise 14.1.** Let $X \sim \mathrm{Binomial}(20, 0.3)$. Compute $\mathbb{E}[X]$, $\operatorname{Var}(X)$ and $P(X = 6)$ (the latter in log-space).

??? success "Solution"

    $\mathbb{E}[X] = np = 20 \times 0.3 = 6$.

    $\operatorname{Var}(X) = np(1-p) = 20 \times 0.3 \times 0.7 = 4.2$.

    For $P(X = 6)$, the computation is performed in log-space to avoid overflow in the binomial coefficient:

    $$\ln P(X = 6) = \ln\binom{20}{6} + 6\ln(0.3) + 14\ln(0.7).$$

    $\ln\binom{20}{6} = \ln(20!) - \ln(6!) - \ln(14!) = \ln(38760) \approx 10.5652$.

    $6\ln(0.3) = 6 \times (-1.2040) = -7.2240$.

    $14\ln(0.7) = 14 \times (-0.3567) = -4.9937$.

    $\ln P(X = 6) \approx 10.5652 - 7.2240 - 4.9937 = -1.6525$.

    $P(X = 6) = e^{-1.6525} \approx 0.1916$.

    Verification: using the exact formula, $P(X=6) = \binom{20}{6}(0.3)^6(0.7)^{14} = 38760 \times 0.000729 \times 0.006782 \approx 0.1916$. $\checkmark$

    $\square$

---

**Exercise 14.2.** Let $X \sim N(50, 100)$. Compute $P(30 < X < 70)$ using the erf function.

??? success "Solution"

    Here $\mu = 50$, $\sigma^2 = 100$, so $\sigma = 10$.

    Standardise: $P(30 < X < 70) = P\!\left(\frac{30 - 50}{10} < Z < \frac{70 - 50}{10}\right) = P(-2 < Z < 2)$.

    Using the relationship $\Phi(z) = \frac{1}{2}\left[1 + \operatorname{erf}\!\left(\frac{z}{\sqrt{2}}\right)\right]$:

    $$P(-2 < Z < 2) = \Phi(2) - \Phi(-2) = 2\Phi(2) - 1 = \operatorname{erf}\!\left(\frac{2}{\sqrt{2}}\right) = \operatorname{erf}(\sqrt{2}).$$

    Numerically, $\operatorname{erf}(\sqrt{2}) = \operatorname{erf}(1.4142) \approx 0.9545$.

    Therefore $P(30 < X < 70) \approx 0.9545$.

    $\square$

---

**Exercise 14.3.** Verify that the Poisson PMF sums to 1: show that $\sum_{k=0}^{\infty} e^{-\lambda}\lambda^k/k! = 1$ by recognising the Taylor series of $e^\lambda$.

??? success "Solution"

    $$\sum_{k=0}^{\infty} \frac{e^{-\lambda}\lambda^k}{k!} = e^{-\lambda} \sum_{k=0}^{\infty} \frac{\lambda^k}{k!} = e^{-\lambda} \cdot e^{\lambda} = 1.$$

    The second equality uses the Maclaurin series $e^x = \sum_{k=0}^{\infty} x^k / k!$, which converges absolutely for all $x \in \mathbb{R}$. Since $\lambda > 0$, the series $\sum \lambda^k/k! = e^\lambda$ is valid and the result follows.

    $\square$

---

**Exercise 14.4.** Prove that if $X \sim \mathrm{Poisson}(\lambda_1)$ and $Y \sim \mathrm{Poisson}(\lambda_2)$ are independent, then $X + Y \sim \mathrm{Poisson}(\lambda_1 + \lambda_2)$.

??? success "Solution"

    We use moment generating functions (MGFs). For a Poisson random variable $X \sim \mathrm{Poisson}(\lambda)$:

    $$M_X(t) = \mathbb{E}[e^{tX}] = \sum_{k=0}^{\infty} e^{tk} \frac{e^{-\lambda}\lambda^k}{k!} = e^{-\lambda}\sum_{k=0}^{\infty}\frac{(\lambda e^t)^k}{k!} = e^{-\lambda} \cdot e^{\lambda e^t} = e^{\lambda(e^t - 1)}.$$

    By independence, $M_{X+Y}(t) = M_X(t) \cdot M_Y(t)$:

    $$M_{X+Y}(t) = e^{\lambda_1(e^t - 1)} \cdot e^{\lambda_2(e^t - 1)} = e^{(\lambda_1 + \lambda_2)(e^t - 1)}.$$

    This is the MGF of a $\mathrm{Poisson}(\lambda_1 + \lambda_2)$ distribution. Since the MGF uniquely determines the distribution (when it exists in a neighbourhood of $t = 0$, which it does here for all $t$), it follows that $X + Y \sim \mathrm{Poisson}(\lambda_1 + \lambda_2)$.

    $\square$

---

**Exercise 14.5.** Let $X_1, \ldots, X_{25}$ be i.i.d. $N(0, 1)$. What is the distribution of $S = \sum X_i^2$? Compute $P(S > 37.65)$ and identify this as the chi-squared critical value at the 5% level with 25 degrees of freedom.

??? success "Solution"

    By definition, if $X_1, \ldots, X_k$ are i.i.d. standard normal, then $S = \sum_{i=1}^k X_i^2 \sim \chi^2(k)$. Here $k = 25$, so $S \sim \chi^2(25)$.

    The chi-squared critical value $\chi^2_{0.05, 25}$ is the value $c$ such that $P(\chi^2(25) > c) = 0.05$. From standard chi-squared tables, $\chi^2_{0.05, 25} = 37.652$.

    Therefore $P(S > 37.65) \approx 0.05$.

    This means 37.65 is (approximately) the 95th percentile of the $\chi^2(25)$ distribution. In hypothesis testing, if a chi-squared test statistic with 25 degrees of freedom exceeds 37.65, $H_0$ is rejected at the 5% significance level.

    $\square$

---

**Exercise 14.6.** Derive the variance formula $\operatorname{Var}(T) = \nu/(\nu-2)$ for $T \sim t(\nu)$ with $\nu > 2$, starting from $T = Z/\sqrt{V/\nu}$ and using independence.

??? success "Solution"

    Let $T = Z/\sqrt{V/\nu}$ where $Z \sim N(0,1)$ and $V \sim \chi^2(\nu)$ are independent.

    Since $\mathbb{E}[Z] = 0$ and $Z$ is independent of $V$, $\mathbb{E}[T] = \mathbb{E}[Z] \cdot \mathbb{E}[1/\sqrt{V/\nu}] = 0$ (for $\nu > 1$). Thus $\operatorname{Var}(T) = \mathbb{E}[T^2]$.

    $$\mathbb{E}[T^2] = \mathbb{E}\!\left[\frac{Z^2}{V/\nu}\right] = \mathbb{E}[Z^2] \cdot \mathbb{E}\!\left[\frac{\nu}{V}\right] = 1 \cdot \nu \cdot \mathbb{E}\!\left[\frac{1}{V}\right],$$

    using independence. The next step requires $\mathbb{E}[1/V]$ where $V \sim \chi^2(\nu)$.

    The PDF of $V$ is $f(v) = \frac{1}{2^{\nu/2}\Gamma(\nu/2)} v^{\nu/2 - 1} e^{-v/2}$ for $v > 0$.

    $$\mathbb{E}\!\left[\frac{1}{V}\right] = \int_0^{\infty} \frac{1}{v} \cdot \frac{v^{\nu/2 - 1} e^{-v/2}}{2^{\nu/2}\Gamma(\nu/2)}\,dv = \frac{1}{2^{\nu/2}\Gamma(\nu/2)}\int_0^{\infty} v^{\nu/2 - 2} e^{-v/2}\,dv.$$

    Substituting $u = v/2$, $dv = 2\,du$:

    $$= \frac{1}{2^{\nu/2}\Gamma(\nu/2)} \cdot 2^{\nu/2 - 1} \int_0^{\infty} u^{\nu/2 - 2} e^{-u}\,du = \frac{2^{\nu/2 - 1}}{2^{\nu/2}} \cdot \frac{\Gamma(\nu/2 - 1)}{\Gamma(\nu/2)}.$$

    Using $\Gamma(\nu/2) = (\nu/2 - 1)\Gamma(\nu/2 - 1)$:

    $$\mathbb{E}\!\left[\frac{1}{V}\right] = \frac{1}{2} \cdot \frac{1}{\nu/2 - 1} = \frac{1}{\nu - 2}.$$

    This requires $\nu/2 - 2 > -1$, i.e., $\nu > 2$.

    Therefore $\operatorname{Var}(T) = \mathbb{E}[T^2] = \nu \cdot \frac{1}{\nu - 2} = \frac{\nu}{\nu - 2}$.

    $\square$

---

**Exercise 14.7.** Prove the de Moivre–Laplace theorem (outline using Stirling's approximation).

??? success "Solution"

    Let $X \sim \mathrm{Binomial}(n, p)$ and $q = 1-p$. We show that for fixed $x$, the standardised PMF converges to the standard normal PDF:

    $$\sqrt{npq} \cdot P(X = k) \to \frac{1}{\sqrt{2\pi}} e^{-x^2/2}, \quad \text{where } k = np + x\sqrt{npq}.$$

    **Step 1.** Write the PMF:

    $$P(X = k) = \binom{n}{k} p^k q^{n-k} = \frac{n!}{k!(n-k)!} p^k q^{n-k}.$$

    **Step 2.** Apply Stirling's approximation $m! \approx \sqrt{2\pi m}\,(m/e)^m$:

    $$\begin{aligned}
    \frac{n!}{k!(n-k)!} &\approx \frac{\sqrt{2\pi n}\,(n/e)^n}{\sqrt{2\pi k}\,(k/e)^k \cdot \sqrt{2\pi(n-k)}\,((n-k)/e)^{n-k}} \\
    &= \frac{1}{\sqrt{2\pi}} \cdot \sqrt{\frac{n}{k(n-k)}} \cdot \frac{n^n}{k^k (n-k)^{n-k}}.
    \end{aligned}$$

    **Step 3.** Substitute $k = np + x\sqrt{npq}$ and $n - k = nq - x\sqrt{npq}$. Take logarithms:

    $$\ln\left(\frac{n^n p^k q^{n-k}}{k^k(n-k)^{n-k}}\right) = k\ln\frac{np}{k} + (n-k)\ln\frac{nq}{n-k}.$$

    Setting $k = np(1 + x\sqrt{q/(np)}\,)$ and expanding $\ln(1 + u)$ to second order around $u = 0$:

    $$k \ln\frac{np}{k} = -k \ln\!\left(1 + \frac{x\sqrt{q}}{\sqrt{np}}\right) \approx -x\sqrt{npq} - \frac{x^2 q}{2} + O(n^{-1/2}),$$

    and similarly for the $(n-k)$ term:

    $$(n-k)\ln\frac{nq}{n-k} \approx x\sqrt{npq} - \frac{x^2 p}{2} + O(n^{-1/2}).$$

    Adding: $-\frac{x^2 q}{2} - \frac{x^2 p}{2} = -\frac{x^2}{2}$.

    **Step 4.** Combining all factors:

    $$\sqrt{npq} \cdot P(X = k) \approx \sqrt{npq} \cdot \frac{1}{\sqrt{2\pi npq}} \cdot e^{-x^2/2} = \frac{1}{\sqrt{2\pi}} e^{-x^2/2}.$$

    This establishes pointwise convergence of the standardised PMF to the standard normal PDF. By a tightness argument (or Scheffé's lemma), this implies convergence in distribution: $(X - np)/\sqrt{npq} \to N(0,1)$.

    $\square$

---

**Exercise 14.8.** Show that $F(d_1, d_2)^{-1} \sim F(d_2, d_1)$.

??? success "Solution"

    By definition, if $W \sim F(d_1, d_2)$, then $W = \frac{U/d_1}{V/d_2}$ where $U \sim \chi^2(d_1)$ and $V \sim \chi^2(d_2)$ are independent.

    Then:

    $$\frac{1}{W} = \frac{V/d_2}{U/d_1},$$

    which is the ratio of $V/d_2$ to $U/d_1$, where $V \sim \chi^2(d_2)$ and $U \sim \chi^2(d_1)$ are independent. By the definition of the $F$-distribution, this is $F(d_2, d_1)$.

    Therefore $1/W \sim F(d_2, d_1)$.

    $\square$

---
