<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 24: Fractional Calculus

**Exercise 24.1.** Compute $D^{1/3} x^2$ using Theorem 24.8.

??? success "Solution"

    Theorem 24.8 (the power rule for fractional derivatives) states:

    $$D^\alpha x^p = \frac{\Gamma(p + 1)}{\Gamma(p + 1 - \alpha)} x^{p - \alpha}, \quad p > -1.$$

    With $\alpha = 1/3$ and $p = 2$:

    $$D^{1/3} x^2 = \frac{\Gamma(3)}{\Gamma(3 - 1/3)} x^{2 - 1/3} = \frac{\Gamma(3)}{\Gamma(8/3)} x^{5/3}.$$

    $\Gamma(3) = 2! = 2$.

    $\Gamma(8/3) = \Gamma(5/3 + 1) = \frac{5}{3}\Gamma(5/3) = \frac{5}{3} \cdot \frac{2}{3}\Gamma(2/3)$.

    $\Gamma(2/3) \approx 1.3541$.

    $\Gamma(8/3) = \frac{10}{9} \times 1.3541 \approx 1.5046$.

    $$D^{1/3}x^2 = \frac{2}{1.5046}\,x^{5/3} \approx 1.3293\,x^{5/3}.$$

    Expressed exactly: $D^{1/3}x^2 = \frac{2}{\Gamma(8/3)}\,x^{5/3} = \frac{2 \cdot \Gamma(2/3) \cdot 9}{10}\,x^{5/3}$... More cleanly:

    $$D^{1/3}x^2 = \frac{\Gamma(3)}{\Gamma(8/3)}\,x^{5/3} = \frac{2}{\Gamma(8/3)}\,x^{5/3} \approx 1.329\,x^{5/3}.$$

    $\square$

---

**Exercise 24.2.** Show GL weights for $\alpha = 1$ and $\alpha = 2$ reduce to standard difference coefficients.

??? success "Solution"

    The Grünwald–Letnikov weights are $w_k^{(\alpha)} = (-1)^k \binom{\alpha}{k} = \frac{(-1)^k \Gamma(\alpha + 1)}{k!\,\Gamma(\alpha - k + 1)}$.

    **Case $\alpha = 1$:**

    $w_0 = (-1)^0 \binom{1}{0} = 1$.

    $w_1 = (-1)^1 \binom{1}{1} = -1$.

    $w_k = (-1)^k \binom{1}{k} = 0$ for $k \geq 2$ (since $\binom{1}{k} = 0$ for $k > 1$).

    This gives $\Delta^1 x_t = x_t - x_{t-1}$, the standard first backward difference. $\checkmark$

    **Case $\alpha = 2$:**

    $w_0 = (-1)^0\binom{2}{0} = 1$.

    $w_1 = (-1)^1\binom{2}{1} = -2$.

    $w_2 = (-1)^2\binom{2}{2} = 1$.

    $w_k = (-1)^k\binom{2}{k} = 0$ for $k \geq 3$.

    This gives $\Delta^2 x_t = x_t - 2x_{t-1} + x_{t-2}$, the standard second difference. $\checkmark$

    In general, for positive integer $\alpha = n$, the GL weights are exactly the binomial coefficients $(-1)^k\binom{n}{k}$, and only finitely many ($n + 1$) are nonzero. For non-integer $\alpha$, infinitely many weights are nonzero, reflecting the non-local nature of fractional derivatives.

    $\square$

---

**Exercise 24.3.** Implement the GL weight recurrence and verify asymptotic decay.

??? success "Solution"

    The GL weights satisfy the recurrence:

    $$w_0 = 1, \qquad w_k = w_{k-1} \cdot \frac{k - 1 - \alpha}{k}, \quad k = 1, 2, \ldots$$

    ```typescript
    function glWeights(alpha: number, n: number): number[] {
      const w: number[] = [1];
      for (let k = 1; k < n; k++) {
        w.push(w[k - 1] * (k - 1 - alpha) / k);
      }
      return w;
    }

    const alpha = 0.4;
    const weights = glWeights(alpha, 20);

    // Display weights
    for (let k = 0; k < 20; k++) {
      console.log(`w[${k}] = ${weights[k].toFixed(8)}, |w[${k}]| = ${Math.abs(weights[k]).toFixed(8)}`);
    }

    // Log-log plot data for asymptotic verification
    // Expected: |w_k| ~ C * k^{-(alpha+1)} = C * k^{-1.4}
    for (let k = 2; k < 20; k++) {
      const logK = Math.log(k);
      const logW = Math.log(Math.abs(weights[k]));
      console.log(`log(k)=${logK.toFixed(3)}, log|w_k|=${logW.toFixed(3)}, slope=${(logW / logK).toFixed(3)}`);
    }
    ```

    **First 20 weights for $\alpha = 0.4$:**

    $w_0 = 1$
    $w_1 = -0.4$
    $w_2 = w_1 \cdot (1 - 0.4)/2 = -0.4 \times 0.3 = -0.12$
    $w_3 = -0.12 \times (2 - 0.4)/3 = -0.12 \times 0.5333 = -0.064$
    $w_4 = -0.064 \times (3 - 0.4)/4 = -0.064 \times 0.65 = -0.0416$

    The weights alternate in sign for the first few terms, then become consistently negative and decay in magnitude. On a log-log plot, $\ln|w_k|$ vs. $\ln k$ approaches a line with slope $-(1 + \alpha) = -1.4$ for large $k$, confirming the asymptotic decay $|w_k| \sim C \cdot k^{-1.4}$. This power-law decay (as opposed to the eventual vanishing of integer-order weights) is the hallmark of the "long memory" property of fractional operators.

    $\square$

---

**Exercise 24.4.** Prove ${}^CD^\alpha_a[c] = 0$ for any constant $c$ directly from the Caputo definition.

??? success "Solution"

    The Caputo fractional derivative of order $\alpha$ ($n - 1 < \alpha < n$) is defined as:

    $${}^C D^\alpha_a f(x) = \frac{1}{\Gamma(n - \alpha)}\int_a^x \frac{f^{(n)}(\tau)}{(x - \tau)^{\alpha - n + 1}}\,d\tau.$$

    For $f(x) = c$ (constant) and $0 < \alpha < 1$ (so $n = 1$):

    $${}^C D^\alpha_a[c] = \frac{1}{\Gamma(1 - \alpha)}\int_a^x \frac{(c)'}{(x - \tau)^{\alpha}}\,d\tau = \frac{1}{\Gamma(1 - \alpha)}\int_a^x \frac{0}{(x - \tau)^{\alpha}}\,d\tau = 0.$$

    For general $n - 1 < \alpha < n$: the $n$-th derivative of a constant is $f^{(n)}(\tau) = 0$ for all $n \geq 1$, so the integrand is identically zero, and ${}^C D^\alpha_a[c] = 0$.

    This is the key advantage of the Caputo definition over the Riemann–Liouville definition: the fractional derivative of a constant is zero, consistent with ordinary calculus and permitting conventional initial conditions.

    $\square$

---

**Exercise 24.5.** Compute ${}^{RL}D^{1/2}_0[1]$ and discuss the result.

??? success "Solution"

    The Riemann–Liouville fractional derivative of order $\alpha$ ($0 < \alpha < 1$) is:

    $${}^{RL}D^\alpha_0 f(x) = \frac{1}{\Gamma(1 - \alpha)}\frac{d}{dx}\int_0^x \frac{f(\tau)}{(x - \tau)^{\alpha}}\,d\tau.$$

    For $f(x) = 1$ and $\alpha = 1/2$:

    $${}^{RL}D^{1/2}_0[1] = \frac{1}{\Gamma(1/2)}\frac{d}{dx}\int_0^x \frac{1}{(x - \tau)^{1/2}}\,d\tau.$$

    Evaluate the integral: $\int_0^x (x - \tau)^{-1/2}\,d\tau = [-2(x-\tau)^{1/2}]_0^x = 0 - (-2x^{1/2}) = 2\sqrt{x}$.

    $${}^{RL}D^{1/2}_0[1] = \frac{1}{\Gamma(1/2)}\frac{d}{dx}(2\sqrt{x}) = \frac{1}{\sqrt{\pi}} \cdot \frac{1}{\sqrt{x}} = \frac{1}{\sqrt{\pi x}}.$$

    (Using $\Gamma(1/2) = \sqrt{\pi}$.)

    **Discussion:** The RL half-derivative of the constant function 1 is $(\sqrt{\pi x})^{-1} \neq 0$. This non-zero result for a constant is mathematically correct within the RL framework (where the fractional derivative acts on the entire history of the function from the lower terminal $a = 0$), but it creates difficulties for initial value problems. When modelling a physical system at rest ($y(0) = c$), the RL framework attributes a nonzero (indeed, singular at $x = 0$) fractional derivative to this constant state. This makes the interpretation of initial conditions unnatural: ${}^{RL}D^{1/2}y(0)$ has no clear physical meaning. The Caputo definition resolves this by differentiating first (integer order) and then fractionally integrating, yielding ${}^C D^{1/2}_0[1] = 0$, which is the expected result.

    $\square$

---

**Exercise 24.6.** Fractional differencing of a random walk.

??? success "Solution"

    ```typescript
    function fractionalDifference(x: number[], d: number, maxLag: number = 100): number[] {
      // Compute GL weights
      const w: number[] = [1];
      for (let k = 1; k <= maxLag; k++) {
        w.push(w[k - 1] * (k - 1 - d) / k);
      }

      // Apply fractional difference
      const n = x.length;
      const y: number[] = [];
      for (let t = 0; t < n; t++) {
        let val = 0;
        for (let k = 0; k <= Math.min(t, maxLag); k++) {
          val += w[k] * x[t - k];
        }
        y.push(val);
      }
      return y;
    }

    // Generate random walk
    const n = 1000;
    const eps: number[] = []; // N(0,1) samples
    // ... (use a PRNG to generate eps)
    const x: number[] = [0];
    for (let t = 1; t < n; t++) {
      x.push(x[t - 1] + eps[t]);
    }

    const y05 = fractionalDifference(x, 0.5);
    const y10 = fractionalDifference(x, 1.0);

    // Compute autocorrelation functions for x, y05, y10
    ```

    **Expected observations:**

    1. **Original series ($d = 0$):** The random walk $x_t$ is non-stationary. Its ACF $\hat{\rho}(h)$ decays very slowly (nearly 1 at all displayed lags), reflecting the unit root.

    2. **$d = 1.0$ (standard differencing):** $y_t = (1-L)^1 x_t = \varepsilon_t$ is white noise. The ACF drops to zero immediately at lag 1 and beyond. The series is stationary (in fact, independent).

    3. **$d = 0.5$ (fractional differencing):** Applying $(1-L)^{0.5}$ to a random walk (which is $I(1)$) yields an $I(0.5)$ process, which is on the boundary between stationarity and non-stationarity. The ACF of this series decays as a power law $\rho(h) \sim C \cdot h^{2(0.5) - 1} = C \cdot h^{0}$, i.e., the ACF does not decay. Full stationarity requires $d_{\text{eff}} < 0.5$, and here $d_{\text{eff}} = 1 - 0.5 = 0.5$ is exactly on the boundary. In practice, the ACF decays much more slowly than for the $d = 1$ case, exhibiting pronounced long-memory behaviour.

    The key insight is that fractional differencing provides a continuum between the non-stationary random walk ($d = 0$, no differencing applied) and the memoryless white noise ($d = 1$, full differencing). For stationarity with preserved memory, one should choose $d \in (0.5, 1)$ so that the effective memory parameter $d_{\text{eff}} = 1 - d$ of the differenced series lies in $(0, 0.5)$. This is the foundation of ARFIMA modelling.

    $\square$

---

**Exercise 24.7.** Verify the semigroup property numerically.

??? success "Solution"

    We want to verify $D^{0.4}(D^{0.6} f)(x) \approx D^{1.0} f(x)$ for $f(x) = x^3$ at $x = 1$.

    **Exact values using the power rule (Theorem 24.8):**

    $D^{1.0}(x^3) = 3x^2$, so $D^{1.0}(x^3)|_{x=1} = 3$.

    $D^{0.6}(x^3) = \frac{\Gamma(4)}{\Gamma(3.4)}x^{2.4} = \frac{6}{\Gamma(3.4)}x^{2.4}$.

    $\Gamma(3.4) = 2.4 \times 1.4 \times \Gamma(1.4) = 2.4 \times 1.4 \times 0.88726 = 2.9809$.

    $D^{0.6}(x^3) = \frac{6}{2.9809}x^{2.4} = 2.0128\,x^{2.4}$.

    $D^{0.4}(2.0128\,x^{2.4}) = 2.0128 \cdot \frac{\Gamma(3.4)}{\Gamma(3.0)}x^{2.0} = 2.0128 \cdot \frac{2.9809}{2}x^2 = 2.0128 \times 1.4905 \times x^2 = 3.0000\,x^2$.

    At $x = 1$: $D^{0.4}(D^{0.6}f)(1) = 3.0000$. $\checkmark$

    **Numerical GL approximation with $h = 0.01$:**

    ```typescript
    function glDerivative(f: (x: number) => number, x: number, alpha: number, h: number): number {
      const N = Math.floor(x / h);
      const w: number[] = [1];
      for (let k = 1; k <= N; k++) {
        w.push(w[k - 1] * (k - 1 - alpha) / k);
      }
      let sum = 0;
      for (let k = 0; k <= N; k++) {
        sum += w[k] * f(x - k * h);
      }
      return sum / Math.pow(h, alpha);
    }

    const f = (x: number) => x ** 3;
    const h = 0.01;

    // Step 1: Compute D^{0.6} f at many points
    const g = (x: number) => glDerivative(f, x, 0.6, h);

    // Step 2: Compute D^{0.4} g at x = 1
    const composed = glDerivative(g, 1.0, 0.4, h);

    // Direct: D^{1.0} f at x = 1
    const direct = glDerivative(f, 1.0, 1.0, h);

    console.log(`D^{0.4}(D^{0.6} f)(1) = ${composed}`);
    console.log(`D^{1.0} f(1) = ${direct}`);
    console.log(`Exact = 3`);
    ```

    With $h = 0.01$, both numerical values should be close to 3 (within a few percent, limited by the $O(h)$ truncation error of the GL scheme). The closeness of the two values confirms the semigroup property $D^{0.4} \circ D^{0.6} = D^{1.0}$.

    $\square$

---

**Exercise 24.8.** Show that the Mittag–Leffler function is an eigenfunction of the Caputo derivative.

??? success "Solution"

    The Mittag–Leffler function is $E_\alpha(z) = \sum_{k=0}^{\infty}\frac{z^k}{\Gamma(\alpha k + 1)}$.

    We need to show ${}^C D^\alpha_0[E_\alpha(\lambda x^\alpha)] = \lambda E_\alpha(\lambda x^\alpha)$.

    **Step 1:** Write $E_\alpha(\lambda x^\alpha) = \sum_{k=0}^{\infty}\frac{\lambda^k x^{\alpha k}}{\Gamma(\alpha k + 1)}$.

    **Step 2:** Apply ${}^C D^\alpha_0$ term-by-term (justified by uniform convergence on compact sets):

    $${}^C D^\alpha_0\!\left[\sum_{k=0}^{\infty}\frac{\lambda^k x^{\alpha k}}{\Gamma(\alpha k + 1)}\right] = \sum_{k=0}^{\infty}\frac{\lambda^k}{\Gamma(\alpha k + 1)}\,{}^C D^\alpha_0[x^{\alpha k}].$$

    **Step 3:** Apply Theorem 24.11 (the fractional power rule for the Caputo derivative):

    For $p = \alpha k$ with $k \geq 1$:

    $${}^C D^\alpha_0[x^{\alpha k}] = \frac{\Gamma(\alpha k + 1)}{\Gamma(\alpha k + 1 - \alpha)}x^{\alpha k - \alpha} = \frac{\Gamma(\alpha k + 1)}{\Gamma(\alpha(k-1) + 1)}x^{\alpha(k-1)}.$$

    For $k = 0$: ${}^C D^\alpha_0[x^0] = {}^C D^\alpha_0[1] = 0$ (from Exercise 24.4).

    **Step 4:** Substitute:

    $${}^C D^\alpha_0[E_\alpha(\lambda x^\alpha)] = \sum_{k=1}^{\infty}\frac{\lambda^k}{\Gamma(\alpha k + 1)} \cdot \frac{\Gamma(\alpha k + 1)}{\Gamma(\alpha(k-1) + 1)}x^{\alpha(k-1)} = \sum_{k=1}^{\infty}\frac{\lambda^k x^{\alpha(k-1)}}{\Gamma(\alpha(k-1) + 1)}.$$

    **Step 5:** Re-index with $j = k - 1$:

    $$= \sum_{j=0}^{\infty}\frac{\lambda^{j+1} x^{\alpha j}}{\Gamma(\alpha j + 1)} = \lambda\sum_{j=0}^{\infty}\frac{(\lambda x^\alpha)^j}{\Gamma(\alpha j + 1)} = \lambda E_\alpha(\lambda x^\alpha).$$

    Therefore ${}^C D^\alpha_0[E_\alpha(\lambda x^\alpha)] = \lambda E_\alpha(\lambda x^\alpha)$, confirming that $E_\alpha(\lambda x^\alpha)$ is an eigenfunction of the Caputo derivative with eigenvalue $\lambda$.

    When $\alpha = 1$, $E_1(z) = e^z$ and the result reduces to $D(e^{\lambda x}) = \lambda e^{\lambda x}$, the classical eigenfunction property of the exponential.

    $\square$
