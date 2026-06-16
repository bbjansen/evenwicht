<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 15: Descriptive Statistics

**Exercise 15.1.** Let $x = \{3, 7, 7, 2, 9, 14, 5\}$. Compute the sample mean, median, variance, standard deviation and IQR. Verify that the median is more robust than the mean by recomputing both after replacing $14$ with $140$.

??? success "Solution"

    **Original data:** $\{3, 7, 7, 2, 9, 14, 5\}$, sorted: $\{2, 3, 5, 7, 7, 9, 14\}$, $n = 7$.

    Mean: $\bar{x} = (3 + 7 + 7 + 2 + 9 + 14 + 5)/7 = 47/7 \approx 6.714$.

    Median: The middle value (4th of 7) is $7$.

    Variance: $s^2 = \frac{1}{n-1}\sum (x_i - \bar{x})^2$.

    | $x_i$ | $x_i - \bar{x}$ | $(x_i - \bar{x})^2$ |
    |--------|:---:|:---:|
    | 2      | $-4.714$ | $22.224$ |
    | 3      | $-3.714$ | $13.796$ |
    | 5      | $-1.714$ | $2.939$ |
    | 7      | $0.286$ | $0.082$ |
    | 7      | $0.286$ | $0.082$ |
    | 9      | $2.286$ | $5.224$ |
    | 14     | $7.286$ | $53.082$ |

    $\sum (x_i - \bar{x})^2 = 97.429$. So $s^2 = 97.429 / 6 \approx 16.238$.

    Standard deviation: $s \approx 4.030$.

    IQR: $Q_1$ = median of $\{2, 3, 5\} = 3$, $Q_3$ = median of $\{7, 9, 14\} = 9$. IQR $= 9 - 3 = 6$.

    **Modified data (14 replaced by 140):** $\{2, 3, 5, 7, 7, 9, 140\}$.

    Mean: $(3 + 7 + 7 + 2 + 9 + 140 + 5)/7 = 173/7 \approx 24.714$.

    Median: still $7$ (the middle value of the sorted data is unchanged).

    The mean changed from $6.71$ to $24.71$ (a shift of $+18$), while the median remained exactly $7$. This shows the median's resistance to outliers: a single extreme value drastically affects the mean but has no effect on the median.

    $\square$

---

**Exercise 15.2.** Covariance and correlation matrix verification.

??? success "Solution"

    ```typescript
    import { Matrix } from 'leibniz';

    // Generate a 100x3 data matrix (using a seeded pseudo-random generator for reproducibility)
    function generateData(n: number, p: number): number[][] {
      // Simple LCG for reproducibility
      let seed = 42;
      const rand = () => { seed = (1103515245 * seed + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
      const data: number[][] = [];
      for (let i = 0; i < n; i++) {
        const row: number[] = [];
        for (let j = 0; j < p; j++) {
          row.push(rand() * 10);  // values in [0, 10)
        }
        data.push(row);
      }
      return data;
    }

    const n = 100, p = 3;
    const X = generateData(n, p);

    // Column means
    const means = Array(p).fill(0);
    for (let i = 0; i < n; i++)
      for (let j = 0; j < p; j++)
        means[j] += X[i][j];
    for (let j = 0; j < p; j++) means[j] /= n;

    // Covariance matrix S (p x p)
    const S: number[][] = Array.from({ length: p }, () => Array(p).fill(0));
    for (let j = 0; j < p; j++) {
      for (let k = 0; k < p; k++) {
        let sum = 0;
        for (let i = 0; i < n; i++) {
          sum += (X[i][j] - means[j]) * (X[i][k] - means[k]);
        }
        S[j][k] = sum / (n - 1);
      }
    }

    // Standard deviations
    const stds = Array(p).fill(0).map((_, j) => Math.sqrt(S[j][j]));

    // Correlation matrix R = D^{-1} S D^{-1}
    const R: number[][] = Array.from({ length: p }, () => Array(p).fill(0));
    for (let j = 0; j < p; j++)
      for (let k = 0; k < p; k++)
        R[j][k] = S[j][k] / (stds[j] * stds[k]);

    // Verify diagonal of R equals 1
    for (let j = 0; j < p; j++) {
      console.assert(Math.abs(R[j][j] - 1) < 1e-12, `R[${j}][${j}] should be 1`);
    }

    // Verify R = D^{-1} S D^{-1} (already how we computed it)

    // Verify eigenvalues of S are non-negative (S is positive semidefinite)
    // Use characteristic polynomial for 3x3 or numerical method
    ```

    **Key verifications:**

    1. **Diagonal entries of $R$ equal 1:** By construction, $R_{jj} = S_{jj}/(s_j \cdot s_j) = s_j^2/s_j^2 = 1$. $\checkmark$

    2. **$R = D^{-1}SD^{-1}$:** This is the definition: $R_{jk} = S_{jk}/(s_j s_k) = (D^{-1}SD^{-1})_{jk}$. $\checkmark$

    3. **Eigenvalues of $S$ are non-negative:** The sample covariance matrix $S = \frac{1}{n-1}(X - \mathbf{1}\bar{x}^T)^T(X - \mathbf{1}\bar{x}^T)$ is a Gram matrix (of the form $B^TB$), hence positive semidefinite. All eigenvalues are $\geq 0$. $\checkmark$

    $\square$

---

**Exercise 15.3.** Derive Bessel's correction from first principles.

??? success "Solution"

    Let $X_1, \ldots, X_n$ be iid with mean $\mu$ and variance $\sigma^2$. We compute $\mathbb{E}\!\left[\sum_{i=1}^n (X_i - \bar{X})^2\right]$.

    Using the identity $X_i - \bar{X} = (X_i - \mu) - (\bar{X} - \mu)$:

    $$(X_i - \bar{X})^2 = (X_i - \mu)^2 - 2(X_i - \mu)(\bar{X} - \mu) + (\bar{X} - \mu)^2.$$

    Summing over $i$:

    $$\sum_{i=1}^n (X_i - \bar{X})^2 = \sum_{i=1}^n (X_i - \mu)^2 - 2(\bar{X} - \mu)\sum_{i=1}^n(X_i - \mu) + n(\bar{X} - \mu)^2.$$

    Note $\sum_{i=1}^n (X_i - \mu) = n(\bar{X} - \mu)$. Substituting:

    $$= \sum_{i=1}^n (X_i - \mu)^2 - 2n(\bar{X} - \mu)^2 + n(\bar{X} - \mu)^2 = \sum_{i=1}^n (X_i - \mu)^2 - n(\bar{X} - \mu)^2.$$

    Taking expectations:

    $$\mathbb{E}\!\left[\sum_{i=1}^n (X_i - \bar{X})^2\right] = \sum_{i=1}^n \mathbb{E}[(X_i - \mu)^2] - n\mathbb{E}[(\bar{X} - \mu)^2] = n\sigma^2 - n \cdot \frac{\sigma^2}{n} = n\sigma^2 - \sigma^2 = (n-1)\sigma^2.$$

    We used $\mathbb{E}[(\bar{X} - \mu)^2] = \operatorname{Var}(\bar{X}) = \sigma^2/n$.

    Therefore:

    $$\mathbb{E}\!\left[\frac{1}{n-1}\sum_{i=1}^n (X_i - \bar{X})^2\right] = \sigma^2.$$

    The denominator $n - 1$ (Bessel's correction) is necessary to produce an unbiased estimator of $\sigma^2$. Dividing by $n$ would yield $\mathbb{E}[S^2] = \frac{n-1}{n}\sigma^2$, which underestimates $\sigma^2$. The "lost" degree of freedom arises because estimating $\mu$ by $\bar{X}$ reduces the effective information by one dimension.

    $\square$

---

**Exercise 15.4.** Prove that the sample mean minimises the sum of squared deviations.

??? success "Solution"

    Define $g(c) = \sum_{i=1}^{n}(x_i - c)^2$. The goal is to find $c$ that minimises $g$.

    **First derivative:** $\frac{dg}{dc} = \sum_{i=1}^{n} 2(x_i - c)(-1) = -2\sum_{i=1}^{n}(x_i - c)$.

    Setting $dg/dc = 0$:

    $$\sum_{i=1}^{n}(x_i - c) = 0 \implies \sum_{i=1}^{n} x_i = nc \implies c = \frac{1}{n}\sum_{i=1}^{n} x_i = \bar{x}.$$

    **Second derivative:** $\frac{d^2g}{dc^2} = 2n > 0$.

    Since the second derivative is strictly positive, $c = \bar{x}$ is a global minimum of $g(c)$.

    $\square$

---

**Exercise 15.5.** A portfolio consists of two assets with returns $x$ (mean 8%, std 12%) and $y$ (mean 5%, std 7%) and correlation $r_{xy} = 0.3$. Compute the portfolio return and standard deviation for weights $(0.6, 0.4)$.

??? success "Solution"

    Let $w_x = 0.6$, $w_y = 0.4$, $\mu_x = 0.08$, $\mu_y = 0.05$, $s_x = 0.12$, $s_y = 0.07$, $r_{xy} = 0.3$.

    **Portfolio return:**

    $$\mu_p = w_x \mu_x + w_y \mu_y = 0.6(0.08) + 0.4(0.05) = 0.048 + 0.020 = 0.068 = 6.8\%.$$

    **Covariance:**

    $$\operatorname{Cov}(X, Y) = r_{xy} \cdot s_x \cdot s_y = 0.3 \times 0.12 \times 0.07 = 0.00252.$$

    **Portfolio variance:**

    $$\begin{aligned}
    \sigma_p^2 &= w_x^2 s_x^2 + w_y^2 s_y^2 + 2 w_x w_y \operatorname{Cov}(X, Y) \\
    &= (0.36)(0.0144) + (0.16)(0.0049) + 2(0.6)(0.4)(0.00252) \\
    &= 0.005184 + 0.000784 + 0.001210 = 0.007178.
    \end{aligned}$$

    **Portfolio standard deviation:**

    $$\sigma_p = \sqrt{0.007178} \approx 0.08472 = 8.47\%.$$

    Note the diversification benefit: the portfolio standard deviation ($8.47\%$) is less than the weighted average of the individual standard deviations ($0.6 \times 12\% + 0.4 \times 7\% = 10.0\%$). This reduction occurs because $r_{xy} < 1$.

    $\square$

---

**Exercise 15.6.** Show that the correlation coefficient is invariant under affine transformations.

??? success "Solution"

    Let $u_i = a + bx_i$ and $v_i = c + dy_i$ with $bd > 0$.

    **Means:** $\bar{u} = a + b\bar{x}$, $\bar{v} = c + d\bar{y}$.

    **Deviations:** $u_i - \bar{u} = b(x_i - \bar{x})$, $v_i - \bar{v} = d(y_i - \bar{y})$.

    **Standard deviations:** $s_u = |b| \cdot s_x$ and $s_v = |d| \cdot s_y$.

    **Covariance:**

    $$S_{uv} = \frac{1}{n-1}\sum_{i=1}^n (u_i - \bar{u})(v_i - \bar{v}) = \frac{1}{n-1}\sum_{i=1}^n b(x_i - \bar{x}) \cdot d(y_i - \bar{y}) = bd \cdot S_{xy}.$$

    **Correlation:**

    $$r_{uv} = \frac{S_{uv}}{s_u \cdot s_v} = \frac{bd \cdot S_{xy}}{|b| s_x \cdot |d| s_y} = \frac{bd}{|bd|} \cdot \frac{S_{xy}}{s_x s_y} = \frac{bd}{|bd|} \cdot r_{xy}.$$

    Since $bd > 0$, $bd/|bd| = 1$, so $r_{uv} = r_{xy}$.

    (If $bd < 0$, $r_{uv} = -r_{xy}$; the sign of the correlation flips when one variable is reflected.)

    $\square$

---

**Exercise 15.7.** Implement Welford's algorithm and verify it on the dataset $\{10^9 + 1, 10^9 + 2, \ldots, 10^9 + 100\}$. Compare the result to the textbook formula.

??? success "Solution"

    ```typescript
    function welfordVariance(data: number[]): { mean: number; variance: number } {
      let n = 0;
      let mean = 0;
      let M2 = 0;

      for (const x of data) {
        n++;
        const delta = x - mean;
        mean += delta / n;
        const delta2 = x - mean;
        M2 += delta * delta2;
      }

      return { mean, variance: M2 / (n - 1) };
    }

    function textbookVariance(data: number[]): { mean: number; variance: number } {
      const n = data.length;
      const mean = data.reduce((s, x) => s + x, 0) / n;
      const sumSq = data.reduce((s, x) => s + x * x, 0);
      const variance = (sumSq - n * mean * mean) / (n - 1);
      return { mean, variance };
    }

    // Generate data: {10^9 + 1, ..., 10^9 + 100}
    const data: number[] = [];
    for (let i = 1; i <= 100; i++) {
      data.push(1e9 + i);
    }

    const welford = welfordVariance(data);
    const textbook = textbookVariance(data);

    // True sample variance of {1,...,100} is n(n^2-1)/(12(n-1)) = 100*9999/(12*99) = 841.6̄
    // Note: (n^2-1)/12 = 833.25 is the population variance; Bessel's correction gives n/(n-1) times that.
    const trueVariance = (100 * (100 * 100 - 1)) / (12 * 99);  // 841.6̄ recurring

    console.log(`Welford: mean=${welford.mean}, variance=${welford.variance}`);
    console.log(`Textbook: mean=${textbook.mean}, variance=${textbook.variance}`);
    console.log(`True variance: ${trueVariance}`);
    console.log(`Welford relative error: ${Math.abs(welford.variance - trueVariance) / trueVariance}`);
    console.log(`Textbook relative error: ${Math.abs(textbook.variance - trueVariance) / trueVariance}`);
    ```

    **Expected results:** The population variance of $\{1, 2, \ldots, 100\}$ is $(n^2 - 1)/12 = 9999/12 = 833.25$. Both algorithms compute the sample variance (dividing by $n - 1$), so the true sample variance (with Bessel's correction) is $\frac{n}{n-1} \cdot \frac{n^2-1}{12} = \frac{100 \times 9999}{12 \times 99} = 841.\overline{6}$. Variance is shift-invariant, so the shifted data has the same value.

    Welford's algorithm maintains numerical stability by computing running differences, so its relative error should be near machine epsilon ($\approx 10^{-15}$).

    The textbook formula $(\sum x_i^2 - n\bar{x}^2)/(n-1)$ computes $\sum x_i^2 \approx 10^{20}$ and $n\bar{x}^2 \approx 10^{20}$, then subtracts to get $\approx 10^5$. This catastrophic cancellation loses roughly 15 digits of significance. In double precision (about 15–16 significant digits), the textbook formula may produce an answer with very few correct digits or even a negative variance, while Welford's algorithm gives the correct result.

    $\square$

---

**Exercise 15.8.** Excess kurtosis of the $t$-distribution.

??? success "Solution"

    The excess kurtosis of $t(\nu)$ is $\kappa_4 = 6/(\nu - 4)$ for $\nu > 4$.

    For $\nu = 5$: $\kappa_4 = 6/(5-4) = 6$.

    For $\nu = 10$: $\kappa_4 = 6/(10-4) = 1$.

    For $\nu = 30$: $\kappa_4 = 6/(30-4) = 6/26 \approx 0.231$.

    For $\nu = 100$: $\kappa_4 = 6/(100-4) = 6/96 = 0.0625$.

    ```typescript
    function simulateKurtosis(nu: number, nSamples: number): number {
      // Generate t-distributed samples using ratio of normal to sqrt(chi-squared/nu)
      // Use Box-Muller for normals and sum of squared normals for chi-squared
      const samples: number[] = [];
      let seed = 12345;
      const rand = () => { seed = (1103515245 * seed + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
      const normalSample = () => {
        const u1 = rand(), u2 = rand();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
      };

      for (let i = 0; i < nSamples; i++) {
        const z = normalSample();
        let chiSq = 0;
        for (let j = 0; j < nu; j++) {
          const w = normalSample();
          chiSq += w * w;
        }
        samples.push(z / Math.sqrt(chiSq / nu));
      }

      const mean = samples.reduce((a, b) => a + b, 0) / nSamples;
      const m2 = samples.reduce((a, x) => a + (x - mean) ** 2, 0) / nSamples;
      const m4 = samples.reduce((a, x) => a + (x - mean) ** 4, 0) / nSamples;

      return m4 / (m2 * m2) - 3;  // excess kurtosis
    }

    const nSamples = 10000;
    for (const nu of [5, 10, 30, 100]) {
      const theoretical = 6 / (nu - 4);
      const simulated = simulateKurtosis(nu, nSamples);
      console.log(`nu=${nu}: theoretical=${theoretical.toFixed(4)}, simulated=${simulated.toFixed(4)}`);
    }
    ```

    **Expected output (approximate):**

    | $\nu$ | Theoretical $\kappa_4$ | Simulated (typical) |
    |--------|:---:|:---:|
    | 5      | 6.0000 | $\sim 5$--$7$ (high variance) |
    | 10     | 1.0000 | $\sim 0.8$--$1.2$ |
    | 30     | 0.2308 | $\sim 0.15$--$0.30$ |
    | 100    | 0.0625 | $\sim 0.0$--$0.12$ |

    As $\nu \to \infty$, $\kappa_4 \to 0$, confirming convergence of the $t$-distribution to the normal distribution (whose excess kurtosis is 0). The convergence is slow for the $t_5$ case because the fourth moment barely exists ($\nu = 5$ is just above the threshold $\nu > 4$), leading to high sampling variability.

    $\square$

---
