<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 17: Regression

**Exercise 17.1.** Prove that the regression line passes through $(\bar{x}, \bar{y})$.

??? success "Solution"

    The OLS estimators for simple regression are:

    $$\hat{\beta}_1 = \frac{S_{xy}}{S_{xx}} = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}, \qquad \hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}.$$

    The second equation is derived from the first normal equation $\sum_{i=1}^n (y_i - \hat{\beta}_0 - \hat{\beta}_1 x_i) = 0$, which gives $n\bar{y} - n\hat{\beta}_0 - n\hat{\beta}_1 \bar{x} = 0$, hence $\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}$.

    Evaluating the fitted line at $x = \bar{x}$:

    $$\hat{y}\big|_{x=\bar{x}} = \hat{\beta}_0 + \hat{\beta}_1 \bar{x} = (\bar{y} - \hat{\beta}_1 \bar{x}) + \hat{\beta}_1 \bar{x} = \bar{y}.$$

    Therefore the regression line passes through the point $(\bar{x}, \bar{y})$.

    $\square$

---

**Exercise 17.2.** Show that in simple regression, $R^2 = r_{xy}^2$.

??? success "Solution"

    We have $R^2 = \text{SSR}/\text{SST} = 1 - \text{SSE}/\text{SST}$, where:

    $$\text{SST} = \sum (y_i - \bar{y})^2 = S_{yy}, \quad \text{SSR} = \sum (\hat{y}_i - \bar{y})^2, \quad \text{SSE} = \sum (y_i - \hat{y}_i)^2.$$

    Since $\hat{y}_i = \hat{\beta}_0 + \hat{\beta}_1 x_i = \bar{y} + \hat{\beta}_1(x_i - \bar{x})$:

    $$\text{SSR} = \sum [\hat{\beta}_1(x_i - \bar{x})]^2 = \hat{\beta}_1^2 S_{xx} = \frac{S_{xy}^2}{S_{xx}^2} \cdot S_{xx} = \frac{S_{xy}^2}{S_{xx}}.$$

    Therefore:

    $$R^2 = \frac{\text{SSR}}{\text{SST}} = \frac{S_{xy}^2/S_{xx}}{S_{yy}} = \frac{S_{xy}^2}{S_{xx} S_{yy}} = \left(\frac{S_{xy}}{\sqrt{S_{xx} S_{yy}}}\right)^2 = r_{xy}^2.$$

    $\square$

---

**Exercise 17.3.** Given a dataset with $p = 5$ predictors and VIF values $\{1.2, 2.1, 3.8, 11.4, 14.7\}$, identify which variables are problematic and propose two distinct strategies to address the multicollinearity.

??? success "Solution"

    A VIF exceeding 10 indicates severe multicollinearity. Variables 4 (VIF $= 11.4$) and 5 (VIF $= 14.7$) are **problematic**.

    Recall $\text{VIF}_j = 1/(1 - R_j^2)$, where $R_j^2$ is the $R^2$ from regressing $x_j$ on all other predictors. VIF $= 14.7$ implies $R_j^2 = 1 - 1/14.7 = 0.932$, meaning 93.2% of the variance of that predictor is explained by the others.

    **Strategy 1: Remove one of the collinear variables.** If variables 4 and 5 are highly correlated with each other (likely, given both have high VIFs), drop the one with lower theoretical importance. This directly eliminates the collinearity. After removal, recompute VIFs to confirm the problem is resolved.

    **Strategy 2: Ridge regression (or other regularisation).** Add a penalty $\lambda \sum \beta_j^2$ to the objective function. Ridge regression shrinks the coefficients of collinear variables toward each other and toward zero, stabilising the estimates. The bias introduced is offset by a substantial reduction in variance, often yielding better predictions. The ridge estimator is $\hat{\beta}_{\text{ridge}} = (X^TX + \lambda I)^{-1}X^Ty$.

    $\square$

---

**Exercise 17.4.** Consider the model $y = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \varepsilon$ with $n = 50$ observations. The OLS results are $\hat{\beta}_1 = 2.3$, $\operatorname{SE}(\hat{\beta}_1) = 0.8$, $\hat{\beta}_2 = -1.1$, $\operatorname{SE}(\hat{\beta}_2) = 0.5$ and $s^2 = 4.2$. (a) Test $H_0: \beta_1 = 0$ at the 5% level. (b) Test $H_0: \beta_2 = 0$ at the 5% level. (c) Construct a 95% confidence interval for $\beta_1$.

??? success "Solution"

    Degrees of freedom: $\nu = n - p - 1 = 50 - 2 - 1 = 47$. For $\nu = 47$, $t_{0.025, 47} \approx 2.012$.

    (a) $t_1 = \hat{\beta}_1 / \operatorname{SE}(\hat{\beta}_1) = 2.3 / 0.8 = 2.875$. Since $|t_1| = 2.875 > 2.012$, **reject $H_0: \beta_1 = 0$** at the 5% level. The predictor $x_1$ is statistically significant.

    (b) $t_2 = \hat{\beta}_2 / \operatorname{SE}(\hat{\beta}_2) = -1.1 / 0.5 = -2.200$. Since $|t_2| = 2.200 > 2.012$, **reject $H_0: \beta_2 = 0$** at the 5% level. The predictor $x_2$ is statistically significant.

    (c) 95% CI for $\beta_1$:

    $$\hat{\beta}_1 \pm t_{0.025, 47} \cdot \operatorname{SE}(\hat{\beta}_1) = 2.3 \pm 2.012 \times 0.8 = 2.3 \pm 1.610 = (0.690,\; 3.910).$$

    The CI does not contain 0, consistent with the rejection of $H_0$ in part (a).

    $\square$

---

**Exercise 17.5.** Derive the Gauss–Markov theorem for the simple regression case directly.

??? success "Solution"

    Let $\tilde{\beta}_1 = \sum_{i=1}^n c_i y_i$ be a linear estimator of $\beta_1$, where $y_i = \beta_0 + \beta_1 x_i + \varepsilon_i$.

    **Unbiasedness constraints:**

    $$\mathbb{E}[\tilde{\beta}_1] = \sum c_i \mathbb{E}[y_i] = \sum c_i (\beta_0 + \beta_1 x_i) = \beta_0 \sum c_i + \beta_1 \sum c_i x_i.$$

    For $\mathbb{E}[\tilde{\beta}_1] = \beta_1$ for all $\beta_0, \beta_1$, the following conditions are required:

    $$\sum_{i=1}^n c_i = 0 \quad \text{and} \quad \sum_{i=1}^n c_i x_i = 1.$$

    **Minimisation.** The goal is to minimise $\operatorname{Var}(\tilde{\beta}_1) = \sigma^2 \sum c_i^2$ subject to the two constraints. Using Lagrange multipliers $\mu$ and $\lambda$:

    $$\begin{aligned}
    \mathcal{L} &= \sum c_i^2 - 2\lambda\!\left(\sum c_i x_i - 1\right) - 2\mu\!\left(\sum c_i\right). \\
    \frac{\partial \mathcal{L}}{\partial c_i} &= 2c_i - 2\lambda x_i - 2\mu = 0 \implies c_i = \lambda x_i + \mu.
    \end{aligned}$$

    Apply constraints:

    $\sum c_i = 0$: $\lambda \sum x_i + n\mu = 0 \implies \mu = -\lambda \bar{x}$.

    So $c_i = \lambda(x_i - \bar{x})$.

    $\sum c_i x_i = 1$: $\lambda \sum (x_i - \bar{x}) x_i = 1 \implies \lambda \sum (x_i - \bar{x})(x_i - \bar{x} + \bar{x}) = 1 \implies \lambda S_{xx} = 1$.

    (Using $\sum (x_i - \bar{x}) = 0$, so $\sum (x_i - \bar{x})x_i = \sum (x_i - \bar{x})^2 = S_{xx}$.)

    Therefore $\lambda = 1/S_{xx}$ and:

    $$c_i = \frac{x_i - \bar{x}}{S_{xx}}.$$

    This gives the OLS estimator $\hat{\beta}_1 = \sum \frac{(x_i - \bar{x})}{S_{xx}} y_i$. Since this is the unique solution to the constrained minimisation, the OLS estimator has the smallest variance among all linear unbiased estimators.

    $\square$

---

**Exercise 17.6.** A researcher estimates $\log(\text{wage}) = 0.5 + 0.08 \cdot \text{education} + 0.02 \cdot \text{experience} + e$ using $n = 1000$ observations. (a) Interpret the coefficient on education. (b) If the researcher suspects that ability (unobserved) is positively correlated with both education and wages, determine the sign of the omitted variable bias on the education coefficient. (c) Would the bias cause the estimated return to education to be too high or too low?

??? success "Solution"

    (a) The coefficient $0.08$ on education means: **each additional year of education is associated with an approximately 8% increase in wages**, holding experience constant. (In a log-linear model, $\partial \ln(\text{wage})/\partial(\text{education}) = 0.08$, so a one-unit change in education leads to a $100 \times 0.08 = 8\%$ change in wages.)

    (b) If ability is positively correlated with both education ($\operatorname{Cov}(\text{ability}, \text{education}) > 0$, since more able people tend to get more education) and wages ($\beta_{\text{ability}} > 0$, since higher ability leads to higher wages), then the omitted variable bias formula gives:

    $$\operatorname{Bias} = \beta_{\text{ability}} \cdot \frac{\operatorname{Cov}(\text{ability}, \text{education})}{\operatorname{Var}(\text{education})} > 0.$$

    The bias on the education coefficient is **positive**.

    (c) Since the bias is positive, the estimated return to education of $8\%$ is **too high**. Part of what appears to be the "return to education" is actually the effect of unobserved ability. The true causal effect of education on wages is smaller than $8\%$.

    $\square$

---

**Exercise 17.7.** Prove that adding a variable to a regression can never decrease $R^2$ (even if the variable is pure noise). Then show that $\bar{R}^2$ can decrease. For the first part, the unrestricted model nests the restricted one. For the second, express $\bar{R}^2$ in terms of $s^2$ and show that $s^2$ can increase when a useless variable is added.

??? success "Solution"

    **Part 1: $R^2$ cannot decrease.**

    Consider the restricted model with $p$ predictors and the unrestricted model with $p+1$ predictors. The unrestricted model nests the restricted model (by setting the coefficient of the new variable to zero). Since OLS minimises SSE, the unrestricted model achieves $\text{SSE}_{p+1} \leq \text{SSE}_p$ (it can always do at least as well by setting the extra coefficient to zero). Since $\text{SST}$ is constant:

    $$R^2_{p+1} = 1 - \frac{\text{SSE}_{p+1}}{\text{SST}} \geq 1 - \frac{\text{SSE}_p}{\text{SST}} = R^2_p.$$

    **Part 2: $\bar{R}^2$ can decrease.**

    The adjusted $R^2$ is:

    $$\bar{R}^2 = 1 - \frac{\text{SSE}/(n - p - 1)}{\text{SST}/(n - 1)} = 1 - \frac{s^2}{\text{SST}/(n-1)},$$

    where $s^2 = \text{SSE}/(n - p - 1)$ is the residual mean square.

    When a useless variable is added, SSE decreases only negligibly (by approximately zero), but the denominator $n - p - 1$ decreases by 1. This can cause $s^2 = \text{SSE}/(n - p - 1)$ to increase if the reduction in SSE is not sufficient to compensate for the lost degree of freedom. Specifically, $s^2$ increases when the partial $F$-statistic for the new variable is less than 1:

    $$F_{\text{partial}} = \frac{\text{SSE}_p - \text{SSE}_{p+1}}{s^2_{p+1}} < 1.$$

    When $s^2$ increases, $\bar{R}^2$ decreases. This penalises the inclusion of variables that do not sufficiently improve the fit.

    $\square$

---

**Exercise 17.8.** A time-series regression of quarterly GDP growth on lagged inflation and lagged unemployment produces residuals with a Durbin–Watson statistic of $DW = 0.87$. (a) Estimate the first-order autocorrelation $\hat{\rho}$. (b) Interpret this value. (c) What are the consequences for the reported standard errors, and what remedy is appropriate?

??? success "Solution"

    (a) The Durbin–Watson statistic and the first-order autocorrelation are related by:

    $$DW \approx 2(1 - \hat{\rho}).$$

    Solving: $\hat{\rho} \approx 1 - DW/2 = 1 - 0.87/2 = 1 - 0.435 = 0.565$.

    (b) $\hat{\rho} = 0.565$ indicates **strong positive autocorrelation** in the residuals. Consecutive residuals tend to have the same sign, suggesting the regression misses a persistent pattern in the data. This is common in time-series regressions where important dynamics are omitted.

    (c) **Consequences:** Positive autocorrelation causes the OLS standard errors to be **underestimated** (too small), because OLS assumes independent errors. This leads to inflated $t$-statistics, $p$-values that are too small and confidence intervals that are too narrow. The coefficient estimates themselves remain unbiased (by Gauss–Markov), but inference is invalid.

    **Remedy:** Use Newey–West (HAC) standard errors, which are consistent in the presence of both heteroscedasticity and autocorrelation. Alternatively, use the Cochrane–Orcutt or Prais–Winsten procedure, which transforms the model by quasi-differencing: regress $(y_t - \hat{\rho} y_{t-1})$ on $(x_t - \hat{\rho} x_{t-1})$. This removes the first-order autocorrelation. Another approach is to include lagged dependent variables or an AR(1) error structure in the model specification.

    $\square$

---
