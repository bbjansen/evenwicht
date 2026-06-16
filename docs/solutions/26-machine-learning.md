<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 26: Machine Learning Foundations

**Exercise 26.1.** Derive the gradient of the MSE loss $\mathcal{L}(\boldsymbol{\beta}) = \frac{1}{n}\|\mathbf{y} - X\boldsymbol{\beta}\|^2$ in matrix form.

??? success "Solution"

    Write $\mathcal{L} = \frac{1}{n}(\mathbf{y} - X\boldsymbol{\beta})'(\mathbf{y} - X\boldsymbol{\beta}) = \frac{1}{n}(\mathbf{y}'\mathbf{y} - 2\mathbf{y}'X\boldsymbol{\beta} + \boldsymbol{\beta}'X'X\boldsymbol{\beta})$.

    Taking the gradient with respect to $\boldsymbol{\beta}$:

    $$\nabla_{\boldsymbol{\beta}}\mathcal{L} = \frac{1}{n}(-2X'\mathbf{y} + 2X'X\boldsymbol{\beta}) = \frac{2}{n}X'(X\boldsymbol{\beta} - \mathbf{y}) = -\frac{2}{n}X'(\mathbf{y} - X\boldsymbol{\beta}).$$

    Setting $\nabla_{\boldsymbol{\beta}}\mathcal{L} = \mathbf{0}$:

    $$X'X\boldsymbol{\beta} = X'\mathbf{y}.$$

    These are the normal equations. $\square$

---

**Exercise 26.2.** Show that $\sigma'(z) = \sigma(z)(1 - \sigma(z))$.

??? success "Solution"

    Write $\sigma(z) = (1 + e^{-z})^{-1}$. By the chain rule:

    $$\sigma'(z) = -(1 + e^{-z})^{-2} \cdot (-e^{-z}) = \frac{e^{-z}}{(1 + e^{-z})^2}.$$

    Now observe that:

    $$\sigma(z)(1 - \sigma(z)) = \frac{1}{1+e^{-z}} \cdot \frac{e^{-z}}{1+e^{-z}} = \frac{e^{-z}}{(1+e^{-z})^2}.$$

    These expressions are identical, so $\sigma'(z) = \sigma(z)(1 - \sigma(z))$. $\square$

---

**Exercise 26.3.** Dimensions for $p=3$, $n=100$.

??? success "Solution"

    With intercept column, $X$ is $n \times (p+1) = 100 \times 4$.

    - $X'X$: $(4 \times 100)(100 \times 4) = 4 \times 4$.
    - $(X'X)^{-1}$: $4 \times 4$.
    - $X'\mathbf{y}$: $(4 \times 100)(100 \times 1) = 4 \times 1$.
    - $\hat{\boldsymbol{\beta}} = (X'X)^{-1}X'\mathbf{y}$: $(4 \times 4)(4 \times 1) = 4 \times 1$.

    Conformability check: $X\hat{\boldsymbol{\beta}}$ is $(100 \times 4)(4 \times 1) = 100 \times 1$, matching $\mathbf{y}$. All multiplications are conformable. $\square$

---

**Exercise 26.4.** Proportion of variance explained. Eigenvalues: $\lambda_1 = 8.0$, $\lambda_2 = 1.5$, $\lambda_3 = 0.5$.

??? success "Solution"

    Total variance: $\lambda_1 + \lambda_2 + \lambda_3 = 10.0$.

    - First component: $8.0/10.0 = 80.0\%$.
    - First two components: $(8.0 + 1.5)/10.0 = 9.5/10.0 = 95.0\%$.
    - All three: $10.0/10.0 = 100.0\%$.

    $\square$

---

**Exercise 26.5.** Prove the ridge estimator is biased and compute the bias.

??? success "Solution"

    Under the true model $\mathbf{y} = X\boldsymbol{\beta} + \boldsymbol{\varepsilon}$ with $\mathbb{E}[\boldsymbol{\varepsilon}] = \mathbf{0}$:

    $$\hat{\boldsymbol{\beta}}_{\text{ridge}} = (X'X + n\lambda I)^{-1}X'\mathbf{y} = (X'X + n\lambda I)^{-1}X'(X\boldsymbol{\beta} + \boldsymbol{\varepsilon}).$$

    Taking expectation:

    $$\mathbb{E}[\hat{\boldsymbol{\beta}}_{\text{ridge}}] = (X'X + n\lambda I)^{-1}X'X\boldsymbol{\beta}.$$

    The bias is:

    $$\operatorname{Bias} = \mathbb{E}[\hat{\boldsymbol{\beta}}_{\text{ridge}}] - \boldsymbol{\beta} = [(X'X + n\lambda I)^{-1}X'X - I]\boldsymbol{\beta} = -n\lambda(X'X + n\lambda I)^{-1}\boldsymbol{\beta}.$$

    The last step follows because $(X'X + n\lambda I)^{-1}X'X = I - n\lambda(X'X + n\lambda I)^{-1}$.

    The bias is zero if and only if $\boldsymbol{\beta} = \mathbf{0}$ (the true coefficients are all zero) or $\lambda = 0$ (no regularisation). For any $\lambda > 0$ and nonzero $\boldsymbol{\beta}$, the ridge estimator is biased toward zero. $\square$

---

**Exercise 26.6.** Count parameters in a one-hidden-layer ReLU network.

??? success "Solution"

    The network has:

    - Input layer: $p$ features.
    - Hidden layer: $H$ units, each connected to all inputs plus a bias. Weight matrix $W_1$ is $H \times p$, bias $\mathbf{b}_1$ is $H \times 1$. Parameters: $Hp + H = H(p+1)$.
    - Output layer: scalar output, connected to all hidden units plus a bias. Weight vector $\mathbf{w}_2$ is $H \times 1$, bias $b_2$ is $1$. Parameters: $H + 1$.

    Total: $H(p+1) + H + 1 = H(p+2) + 1$.

    For $p = 10$, $H = 64$: $64(10 + 2) + 1 = 64 \times 12 + 1 = 768 + 1 = 769$ parameters.

    $\square$

---

**Exercise 26.7.** One epoch of mini-batch SGD for linear regression.

??? success "Solution"

    **Algorithm.** One epoch of mini-batch SGD proceeds as follows:

    1. Randomly shuffle the indices $\{1, \ldots, n\}$.
    2. Partition the shuffled indices into $\lceil n/B \rceil$ mini-batches of size $B$.
    3. For each mini-batch $\mathcal{B}_k$, compute the mini-batch gradient:

    $$\mathbf{g}_k = \frac{2}{B}\sum_{i \in \mathcal{B}_k} ({\mathbf{x}_i'\boldsymbol{\beta} - y_i})\,\mathbf{x}_i.$$

    4. Update: $\boldsymbol{\beta} \leftarrow \boldsymbol{\beta} - \eta\,\mathbf{g}_k$.

    Each mini-batch gradient is an unbiased estimator of the full gradient $\nabla_{\boldsymbol{\beta}}\mathcal{L} = (2/n)X'(X\boldsymbol{\beta} - \mathbf{y})$, with variance proportional to $1/B$.

    ```typescript
    function sgdEpoch(
      X: number[][], y: number[], batchSize: number, eta: number, beta: number[]
    ): number[] {
      const n = X.length;
      const p = X[0].length;
      const indices = Array.from({length: n}, (_, i) => i);
      // Fisher–Yates shuffle
      for (let i = n - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [indices[i], indices[j]] = [indices[j], indices[i]];
      }

      for (let start = 0; start < n; start += batchSize) {
        const end = Math.min(start + batchSize, n);
        const B = end - start;
        const grad = new Array(p).fill(0);
        for (let b = start; b < end; b++) {
          const i = indices[b];
          let pred = 0;
          for (let j = 0; j < p; j++) pred += X[i][j] * beta[j];
          const residual = pred - y[i];
          for (let j = 0; j < p; j++) grad[j] += (2 / B) * residual * X[i][j];
        }
        for (let j = 0; j < p; j++) beta[j] -= eta * grad[j];
      }
      return beta;
    }
    ```

    With $n = 1000$, $p = 5$, $B = 50$, there are $1000/50 = 20$ mini-batches per epoch. Starting from $\boldsymbol{\beta}^{(0)} = \mathbf{0}$ with $\eta = 0.01$, one epoch moves $\boldsymbol{\beta}$ toward but not to the OLS solution. Different random seeds change the mini-batch ordering, producing different $\boldsymbol{\beta}$ values after one epoch. The variance across seeds decreases as $B$ increases (larger batches reduce gradient noise). After many epochs, all seeds converge to (approximately) the same OLS solution.

    $\square$

---

**Exercise 26.8.** Prove the bias–variance decomposition.

??? success "Solution"

    Let $f = f(\mathbf{x})$ be the true function, $\bar{f} = \mathbb{E}[\hat{f}(\mathbf{x})]$, and $y = f + \varepsilon$ with $\mathbb{E}[\varepsilon] = 0$, $\operatorname{Var}(\varepsilon) = \sigma^2$, and $\varepsilon$ independent of the training set.

    $$\mathbb{E}[(y - \hat{f})^2] = \mathbb{E}[(f + \varepsilon - \hat{f})^2] = \mathbb{E}[((f - \bar{f}) + (\bar{f} - \hat{f}) + \varepsilon)^2].$$

    Expanding the square:

    $$= \mathbb{E}[(f - \bar{f})^2] + \mathbb{E}[(\bar{f} - \hat{f})^2] + \mathbb{E}[\varepsilon^2] + 2(f-\bar{f})\mathbb{E}[\bar{f}-\hat{f}] + 2(f-\bar{f})\mathbb{E}[\varepsilon] + 2\mathbb{E}[(\bar{f}-\hat{f})\varepsilon].$$

    Now: $(f - \bar{f})^2 = \operatorname{Bias}^2$ is a constant; $\mathbb{E}[\bar{f} - \hat{f}] = 0$ by definition of $\bar{f}$; $\mathbb{E}[\varepsilon] = 0$; and $\mathbb{E}[(\bar{f} - \hat{f})\varepsilon] = \mathbb{E}[\bar{f} - \hat{f}] \cdot \mathbb{E}[\varepsilon] = 0$ by independence of $\varepsilon$ from the training set. Therefore:

    $$\mathbb{E}[(y - \hat{f})^2] = \operatorname{Bias}^2 + \operatorname{Var}[\hat{f}] + \sigma^2.$$

    $\square$

    The independence assumption is used in the cross term $\mathbb{E}[(\bar{f}-\hat{f})\varepsilon]$: since $\hat{f}$ depends only on the training set and $\varepsilon$ is the noise on the test point (drawn independently), these are independent random variables, so their product has expectation equal to the product of expectations.

---

**Exercise 26.9.** Ridge MSE and the existence of $\lambda > 0$ with lower MSE than OLS.

??? success "Solution"

    In the eigenbasis of $X'X = V\Lambda V'$, let $\tilde{\boldsymbol{\beta}} = V'\boldsymbol{\beta}$ and $\tilde{\mathbf{d}} = V'X'\mathbf{y}$. The $j$-th component of the ridge estimator is $\tilde{\beta}_j^{\text{ridge}} = d_j/(\lambda_j + n\lambda)$ where $d_j = \mathbf{v}_j'X'\mathbf{y}$.

    The MSE decomposes into variance and bias squared:

    $$\text{MSE} = \sum_{j=1}^{p} \left[\operatorname{Var}(\tilde{\beta}_j^{\text{ridge}}) + \operatorname{Bias}(\tilde{\beta}_j^{\text{ridge}})^2\right].$$

    Since $\tilde{\beta}_j^{\text{ridge}} = \frac{\lambda_j}{\lambda_j + n\lambda}\tilde{\beta}_j^{\text{OLS}}$ and $\operatorname{Var}(\tilde{\beta}_j^{\text{OLS}}) = \sigma^2/\lambda_j$:

    $$\begin{aligned}
    \operatorname{Var}(\tilde{\beta}_j^{\text{ridge}}) &= \left(\frac{\lambda_j}{\lambda_j + n\lambda}\right)^2 \frac{\sigma^2}{\lambda_j} = \frac{\sigma^2\lambda_j}{(\lambda_j + n\lambda)^2}. \\
    \operatorname{Bias}(\tilde{\beta}_j^{\text{ridge}})^2 &= \left(\frac{-n\lambda}{\lambda_j + n\lambda}\right)^2 \tilde{\beta}_j^2 = \frac{n^2\lambda^2\tilde{\beta}_j^2}{(\lambda_j + n\lambda)^2}.
    \end{aligned}$$

    Therefore:

    $$\text{MSE}(\lambda) = \sum_{j=1}^{p}\frac{\sigma^2\lambda_j}{(\lambda_j + n\lambda)^2} + \sum_{j=1}^{p}\frac{n^2\lambda^2\tilde{\beta}_j^2}{(\lambda_j + n\lambda)^2}.$$

    To show there exists $\lambda > 0$ with MSE less than OLS, differentiate with respect to $\lambda$ and evaluate at $\lambda = 0$:

    $$\left.\frac{d}{d\lambda}\text{MSE}\right|_{\lambda=0} = \sum_{j=1}^{p}\left[\frac{-2n\sigma^2}{\lambda_j^2} + \frac{2n\tilde{\beta}_j^2 \cdot 0}{\lambda_j^2}\right] = -2n\sigma^2\sum_{j=1}^{p}\frac{1}{\lambda_j^2} < 0.$$

    Since the derivative is strictly negative at $\lambda = 0$, the MSE decreases as $\lambda$ increases from zero. Therefore there always exists a $\lambda > 0$ for which $\text{MSE}(\boldsymbol{\beta}_{\text{ridge}}) < \text{MSE}(\boldsymbol{\beta}_{\text{OLS}})$. $\square$

---
