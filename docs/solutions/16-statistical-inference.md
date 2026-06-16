<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 16: Statistical Inference

**Exercise 16.1.** A sample of $n = 25$: $\bar{x} = 14.2$, $s = 3.1$. (a) 95% CI for $\mu$. (b) Test $H_0: \mu = 15$ vs. $H_1: \mu < 15$ at $\alpha = 0.05$. (c) Consistency check.

??? success "Solution"

    (a) With unknown variance and $n = 25$, the $t$-distribution with $\nu = 24$ degrees of freedom applies.

    The 95% CI is $\bar{x} \pm t_{0.025, 24} \cdot \frac{s}{\sqrt{n}}$. From $t$-tables, $t_{0.025, 24} \approx 2.064$.

    $$\begin{aligned}
    \operatorname{SE} &= \frac{3.1}{\sqrt{25}} = \frac{3.1}{5} = 0.62. \\
    \text{CI} &= 14.2 \pm 2.064 \times 0.62 = 14.2 \pm 1.280 = (12.920,\; 15.480).
    \end{aligned}$$

    (b) Test statistic: $t = \frac{\bar{x} - \mu_0}{s/\sqrt{n}} = \frac{14.2 - 15}{0.62} = \frac{-0.8}{0.62} = -1.290$.

    For a one-sided test with $H_1: \mu < 15$ at $\alpha = 0.05$, the critical value is $-t_{0.05, 24} \approx -1.711$.

    Since $-1.290 > -1.711$, the test statistic does not fall in the rejection region. **Fail to reject $H_0$.**

    (c) Yes, the results are consistent. The 95% CI $(12.920, 15.480)$ contains $\mu_0 = 15$, which is equivalent to failing to reject $H_0: \mu = 15$ at the $\alpha = 0.05$ level in a two-sided test. The one-sided test also fails to reject, which is consistent since the one-sided test is "easier" to reject (lower critical value in absolute terms) in the direction of interest, yet the evidence is still insufficient.

    $\square$

---

**Exercise 16.2.** Explain why "there is a 95% probability that $\mu$ lies in the CI" is incorrect.

??? success "Solution"

    The statement is incorrect because $\mu$ is a fixed (unknown) constant, not a random variable. It either lies in the computed interval or it does not---there is no probability involved once the interval is computed from observed data. The correct interpretation is: **the procedure used to construct the interval has the property that, in repeated sampling, 95% of the intervals so constructed will contain the true parameter $\mu$.** The randomness is in the interval (which depends on the random sample), not in the parameter. Before the data are observed, there is a 95% probability that the random interval $[\bar{X} - t^* \cdot S/\sqrt{n},\; \bar{X} + t^* \cdot S/\sqrt{n}]$ will contain $\mu$. After the data are observed and a specific numerical interval is computed, the correct language is "the interval is computed with 95% confidence" (referring to the long-run reliability of the method), not "there is a 95% probability."

    $\square$

---

**Exercise 16.3.** Let $X_1, \ldots, X_n \sim \mathrm{Exponential}(\lambda)$. (a) Derive the MLE $\hat{\lambda}_{\text{MLE}}$. (b) Show that $\hat{\lambda}_{\text{MLE}}$ is biased. (c) Find an unbiased estimator.

??? success "Solution"

    (a) The likelihood is:

    $$L(\lambda) = \prod_{i=1}^n \lambda e^{-\lambda x_i} = \lambda^n e^{-\lambda \sum x_i}.$$

    The log-likelihood is:

    $$\ell(\lambda) = n \ln \lambda - \lambda \sum_{i=1}^n x_i.$$

    Setting $\ell'(\lambda) = 0$:

    $$\frac{n}{\lambda} - \sum_{i=1}^n x_i = 0 \implies \hat{\lambda}_{\text{MLE}} = \frac{n}{\sum_{i=1}^n X_i} = \frac{1}{\bar{X}}.$$

    Verify second derivative: $\ell''(\lambda) = -n/\lambda^2 < 0$, confirming maximum. $\checkmark$

    (b) $\hat{\lambda}_{\text{MLE}} = 1/\bar{X}$. The expectation $\mathbb{E}[1/\bar{X}]$ is required. Since $X_i \sim \mathrm{Exp}(\lambda)$, $\sum X_i \sim \mathrm{Gamma}(n, \lambda)$ (with rate parametrisation). Thus $Y = \lambda \sum X_i \sim \mathrm{Gamma}(n, 1)$, and $\bar{X} = Y/(n\lambda)$.

    $$\mathbb{E}\!\left[\frac{1}{\bar{X}}\right] = \mathbb{E}\!\left[\frac{n\lambda}{Y}\right] = n\lambda \cdot \mathbb{E}\!\left[\frac{1}{Y}\right].$$

    For $Y \sim \mathrm{Gamma}(n, 1)$: $\mathbb{E}[Y^{-1}] = \frac{\Gamma(n-1)}{\Gamma(n)} = \frac{1}{n-1}$ (valid for $n > 1$).

    Therefore $\mathbb{E}[\hat{\lambda}_{\text{MLE}}] = n\lambda \cdot \frac{1}{n-1} = \frac{n}{n-1}\lambda \neq \lambda$.

    The MLE is **biased** upward by the factor $n/(n-1)$.

    (c) An unbiased estimator is:

    $$\hat{\lambda}_{\text{unbiased}} = \frac{n-1}{n} \cdot \hat{\lambda}_{\text{MLE}} = \frac{n-1}{\sum_{i=1}^n X_i}.$$

    Then $\mathbb{E}[\hat{\lambda}_{\text{unbiased}}] = \frac{n-1}{n} \cdot \frac{n}{n-1}\lambda = \lambda$.

    $\square$

---

**Exercise 16.4.** Welch's $t$-test. Group 1: $n_1 = 15$, $\bar{x}_1 = 4.8$, $s_1 = 1.2$. Group 2: $n_2 = 18$, $\bar{x}_2 = 5.6$, $s_2 = 1.5$.

??? success "Solution"

    (a) **Welch's $t$-statistic:**

    $$t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}} = \frac{4.8 - 5.6}{\sqrt{\frac{1.44}{15} + \frac{2.25}{18}}} = \frac{-0.8}{\sqrt{0.0960 + 0.1250}} = \frac{-0.8}{\sqrt{0.2210}} = \frac{-0.8}{0.4701} = -1.702.$$

    (b) **Welch–Satterthwaite degrees of freedom:**

    $$\nu = \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{(s_1^2/n_1)^2}{n_1 - 1} + \frac{(s_2^2/n_2)^2}{n_2 - 1}} = \frac{(0.2210)^2}{\frac{(0.0960)^2}{14} + \frac{(0.1250)^2}{17}}.$$

    Numerator: $(0.2210)^2 = 0.04884$.

    Denominator: $\frac{0.009216}{14} + \frac{0.015625}{17} = 0.000658 + 0.000919 = 0.001577$.

    $$\nu = \frac{0.04884}{0.001577} \approx 30.97.$$

    Round down to $\nu \approx 30$.

    (c) For a two-sided test at $\alpha = 0.05$ with $\nu \approx 30$: $t_{0.025, 30} \approx 2.042$. Since $|t| = 1.702 < 2.042$, the test **fails to reject** $H_0: \mu_1 = \mu_2$.

    **95% CI for $\mu_1 - \mu_2$:**

    $$(\bar{x}_1 - \bar{x}_2) \pm t_{0.025, 30} \cdot \operatorname{SE} = -0.8 \pm 2.042 \times 0.4701 = -0.8 \pm 0.960 = (-1.760,\; 0.160).$$

    The CI contains 0, consistent with the failure to reject.

    $\square$

---

**Exercise 16.5.** One-way ANOVA: 4 groups, $n_i = 8$, SSB $= 120$, SSW $= 280$.

??? success "Solution"

    (a) SST $= \text{SSB} + \text{SSW} = 120 + 280 = 400$.

    Degrees of freedom: $df_B = k - 1 = 3$, $df_W = n - k = 32 - 4 = 28$.

    $\text{MSB} = \text{SSB}/df_B = 120/3 = 40$.

    $\text{MSW} = \text{SSW}/df_W = 280/28 = 10$.

    $F = \text{MSB}/\text{MSW} = 40/10 = 4.0$.

    (b) Degrees of freedom: $(df_B, df_W) = (3, 28)$.

    (c) From $F$-tables, $F_{0.01, 3, 28} \approx 4.57$. Since $F = 4.0 < 4.57$, the result is **not significant** at $\alpha = 0.01$.

    (For reference, $F_{0.05, 3, 28} \approx 2.95$, so the result is significant at $\alpha = 0.05$ but not at $\alpha = 0.01$.)

    (d) $\eta^2 = \text{SSB}/\text{SST} = 120/400 = 0.30$. This means 30% of the total variability in the outcome is explained by group membership, which is considered a large effect size (Cohen's guidelines: $\eta^2 \geq 0.14$ is large).

    $\square$

---

**Exercise 16.6.** Chi-square goodness-of-fit test for Hardy–Weinberg equilibrium.

??? success "Solution"

    The observed allele frequency is $\hat{p}_A = (2 \times 28 + 52)/(2 \times 100) = 108/200 = 0.54$ and $\hat{p}_a = 1 - 0.54 = 0.46$.

    Under Hardy–Weinberg equilibrium with these estimated allele frequencies, the expected counts are:

    $$E_{AA} = n\hat{p}_A^2 = 100(0.54)^2 = 29.16, \quad E_{Aa} = 2n\hat{p}_A\hat{p}_a = 100 \times 2(0.54)(0.46) = 49.68, \quad E_{aa} = n\hat{p}_a^2 = 100(0.46)^2 = 21.16.$$

    |          | AA    | Aa    | aa    | Total |
    |----------|-------|-------|-------|-------|
    | Observed | 28    | 52    | 20    | 100   |
    | Expected | 29.16 | 49.68 | 21.16 | 100   |

    The test statistic is:

    $$\chi^2 = \frac{(28 - 29.16)^2}{29.16} + \frac{(52 - 49.68)^2}{49.68} + \frac{(20 - 21.16)^2}{21.16} = \frac{1.3456}{29.16} + \frac{5.3824}{49.68} + \frac{1.3456}{21.16} \approx 0.046 + 0.108 + 0.064 = 0.218.$$

    **Degrees of freedom:** There are 3 categories. One df is lost for the constraint that counts sum to $n = 100$, and a further df is lost because the allele frequency $\hat{p}_A$ was estimated from the data. Therefore $df = 3 - 1 - 1 = 1$.

    **Critical value:** $\chi^2_{0.05, 1} = 3.841$.

    Since $\chi^2 = 0.218 < 3.841$, $H_0$ is **not rejected**. The data are consistent with Hardy–Weinberg equilibrium.

    $\square$

---

**Exercise 16.7.** Prove that $\bar{X}$ is the MVUE for $\mu$ when sampling from $N(\mu, \sigma^2)$.

??? success "Solution"

    We show that $\bar{X}$ attains the Cramér–Rao lower bound.

    **Fisher information for a single observation.** The log-likelihood for one observation is:

    $$\ell(\mu; x) = -\frac{1}{2}\ln(2\pi\sigma^2) - \frac{(x - \mu)^2}{2\sigma^2}.$$

    Score function: $\frac{\partial \ell}{\partial \mu} = \frac{x - \mu}{\sigma^2}$.

    Fisher information:

    $$I(\mu) = \mathbb{E}\!\left[\left(\frac{\partial \ell}{\partial \mu}\right)^2\right] = \mathbb{E}\!\left[\frac{(X - \mu)^2}{\sigma^4}\right] = \frac{\sigma^2}{\sigma^4} = \frac{1}{\sigma^2}.$$

    **Cramér–Rao lower bound for $n$ observations:**

    $$\operatorname{Var}(\hat{\mu}) \geq \frac{1}{n I(\mu)} = \frac{\sigma^2}{n}.$$

    **Variance of $\bar{X}$:**

    $$\operatorname{Var}(\bar{X}) = \frac{\sigma^2}{n}.$$

    Since $\operatorname{Var}(\bar{X}) = \frac{\sigma^2}{n} = \frac{1}{nI(\mu)}$, the sample mean attains the Cramér–Rao lower bound exactly.

    Since $\bar{X}$ is unbiased ($\mathbb{E}[\bar{X}] = \mu$) and achieves the Cramér–Rao lower bound, it is the minimum variance unbiased estimator (MVUE) for $\mu$.

    $\square$

---

**Exercise 16.8.** Multiple testing corrections. P-values: $0.003, 0.012, 0.038, 0.041, 0.150$. Family-wise $\alpha = 0.05$, $m = 5$ tests.

??? success "Solution"

    (a) **Bonferroni correction:** The adjusted significance level is $\alpha/m = 0.05/5 = 0.01$.

    | Endpoint | p-value | $< 0.01$? | Significant? |
    |----------|---------|-----------|:---:|
    | 1        | 0.003   | Yes       | Yes |
    | 2        | 0.012   | No        | No  |
    | 3        | 0.038   | No        | No  |
    | 4        | 0.041   | No        | No  |
    | 5        | 0.150   | No        | No  |

    Only **endpoint 1** is significant under Bonferroni.

    (b) **Holm–Bonferroni step-down procedure:**

    Order the p-values from smallest to largest: $p_{(1)} = 0.003$, $p_{(2)} = 0.012$, $p_{(3)} = 0.038$, $p_{(4)} = 0.041$, $p_{(5)} = 0.150$.

    | Step $j$ | $p_{(j)}$ | Threshold $\alpha/(m - j + 1)$ | Reject? |
    |-----------|-----------|:---:|:---:|
    | 1         | 0.003     | $0.05/5 = 0.010$ | Yes ($0.003 < 0.010$) |
    | 2         | 0.012     | $0.05/4 = 0.0125$ | Yes ($0.012 < 0.0125$) |
    | 3         | 0.038     | $0.05/3 \approx 0.0167$ | No ($0.038 > 0.0167$) |

    Stop at step 3. **Endpoints 1 and 2** are significant under Holm–Bonferroni.

    (c) The Holm procedure is uniformly more powerful than the Bonferroni correction because it uses a step-down approach: once the smallest p-values have been declared significant, the remaining comparisons are tested against progressively less stringent thresholds ($\alpha/(m-1)$, $\alpha/(m-2)$, etc.) rather than the fixed $\alpha/m$. The Bonferroni threshold is $\alpha/m$ for all tests, which is the most conservative threshold in the Holm sequence. Since every p-value rejected by Bonferroni is also rejected by Holm (both start with the same threshold $\alpha/m$), but Holm can additionally reject further hypotheses at the less stringent thresholds, Holm is uniformly at least as powerful. Importantly, Holm still controls the family-wise error rate at level $\alpha$.

    $\square$

---
