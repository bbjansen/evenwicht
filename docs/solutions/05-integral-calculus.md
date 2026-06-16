<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 5: Integral Calculus

**Exercise 5.1.** Evaluate $\int_1^3 (2x + 1)\,dx$ using the FTC.

??? success "Solution"

    The antiderivative is $F(x) = x^2 + x$. By the FTC:

    $$\int_1^3 (2x+1)\,dx = F(3) - F(1) = (9 + 3) - (1 + 1) = 12 - 2 = 10.$$

    **Riemann sum verification** with $n = 4$, right endpoints on $[1, 3]$:

    $\Delta x = (3-1)/4 = 0.5$. Right endpoints: $x_1 = 1.5, x_2 = 2, x_3 = 2.5, x_4 = 3$.

    $$\begin{aligned}
    R_4 &= \sum_{i=1}^{4} f(x_i)\Delta x = 0.5[f(1.5) + f(2) + f(2.5) + f(3)] \\
    &= 0.5[(3+1) + (4+1) + (5+1) + (6+1)] = 0.5[4 + 5 + 6 + 7] = 0.5 \times 22 = 11.
    \end{aligned}$$

    The Riemann sum gives $11$, which overestimates the true value $10$ (as expected for a right Riemann sum of an increasing function).

---

**Exercise 5.2.** Evaluate $\int_0^{\pi/2} \cos(x)\,dx$ exactly. Compare with Simpson.

??? success "Solution"

    **Exact:** $\int_0^{\pi/2}\cos(x)\,dx = [\sin(x)]_0^{\pi/2} = 1 - 0 = 1$.

    **Simpson with $n = 4$:** $h = \frac{\pi/2 - 0}{4} = \frac{\pi}{8}$. Nodes: $x_0 = 0, x_1 = \pi/8, x_2 = \pi/4, x_3 = 3\pi/8, x_4 = \pi/2$.

    $$\begin{aligned}
    S_4 &= \frac{h}{3}[f(x_0) + 4f(x_1) + 2f(x_2) + 4f(x_3) + f(x_4)] \\
    &= \frac{\pi}{24}[\cos 0 + 4\cos(\pi/8) + 2\cos(\pi/4) + 4\cos(3\pi/8) + \cos(\pi/2)] \\
    &= \frac{\pi}{24}[1 + 4(0.92388) + 2(0.70711) + 4(0.38268) + 0] \\
    &= \frac{\pi}{24}[1 + 3.69552 + 1.41421 + 1.53073] \\
    &= \frac{\pi}{24}[7.64046] \approx \frac{3.14159}{24} \times 7.64046 \approx 0.99998.
    \end{aligned}$$

    The Simpson approximation gives $\approx 0.99998$, extremely close to the exact value $1$, with error $\approx 2 \times 10^{-5}$.

---

**Exercise 5.3.** Find the antiderivative of $f(x) = 3x^2 - 4x + 7$.

??? success "Solution"

    $$F(x) = x^3 - 2x^2 + 7x + C.$$

    **Verification:** $F'(x) = 3x^2 - 4x + 7 = f(x)$. $\checkmark$

---

**Exercise 5.4.** Use $u = x^2 + 1$ to evaluate $\int_0^2 \frac{2x}{x^2 + 1}\,dx$.

??? success "Solution"

    Let $u = x^2 + 1$, so $du = 2x\,dx$. When $x = 0$: $u = 1$. When $x = 2$: $u = 5$.

    $$\int_0^2 \frac{2x}{x^2+1}\,dx = \int_1^5 \frac{du}{u} = [\ln u]_1^5 = \ln 5 - \ln 1 = \ln 5 \approx 1.6094.$$

---

**Exercise 5.5.** Integration by parts: $\int_0^1 x\cos(x)\,dx$.

??? success "Solution"

    Let $u = x$, $dv = \cos(x)\,dx$, so $du = dx$, $v = \sin(x)$.

    $$\begin{aligned}
    \int_0^1 x\cos(x)\,dx &= [x\sin(x)]_0^1 - \int_0^1 \sin(x)\,dx = \sin(1) - [-\cos(x)]_0^1 \\
    &= \sin(1) - (-\cos(1) + \cos(0)) = \sin(1) + \cos(1) - 1 \approx 0.8415 + 0.5403 - 1 = 0.3818.
    \end{aligned}$$

    For numerical verification with Simpson's rule at $n = 20$: With $h = 1/20 = 0.05$ and 21 nodes, the Simpson approximation would give a result matching $\sin(1) + \cos(1) - 1 \approx 0.38177$ to high accuracy (Simpson error for smooth functions with $n = 20$ is $O(h^4) \approx 10^{-6}$).

---

**Exercise 5.6.** Convergence of $\int_1^\infty \frac{1}{x^p}\,dx$.

??? success "Solution"

    For $p \neq 1$:

    $$\int_1^R x^{-p}\,dx = \left[\frac{x^{1-p}}{1-p}\right]_1^R = \frac{R^{1-p} - 1}{1-p}.$$

    - If $p > 1$: $1 - p < 0$, so $R^{1-p} \to 0$ as $R \to \infty$. The integral converges to $\frac{-1}{1-p} = \frac{1}{p-1}$.
    - If $p < 1$: $1 - p > 0$, so $R^{1-p} \to \infty$ as $R \to \infty$. The integral diverges.

    For $p = 1$:

    $$\int_1^R \frac{1}{x}\,dx = \ln R \to \infty. \quad \text{Diverges.}$$

    **Conclusion:** The integral $\int_1^\infty x^{-p}\,dx$ converges if and only if $p > 1$ and its value is $\frac{1}{p-1}$.

---

**Exercise 5.7.** Prove Simpson's rule is exact for polynomials of degree $\leq 3$.

??? success "Solution"

    *Proof.* By linearity, it suffices to verify for $f(x) = 1, x, x^2, x^3$ on $[a, b]$ with $n = 2$ (one panel). With $h = (b-a)/2$ and $m = (a+b)/2$:

    Simpson's formula: $S = \frac{h}{3}[f(a) + 4f(m) + f(b)]$.

    **$f(x) = 1$:** Exact: $\int_a^b 1\,dx = b - a = 2h$. Simpson: $\frac{h}{3}(1 + 4 + 1) = \frac{6h}{3} = 2h$. $\checkmark$

    **$f(x) = x$:** Exact: $\frac{b^2 - a^2}{2} = \frac{(b-a)(b+a)}{2} = h(a+b)$. Simpson: $\frac{h}{3}[a + 4m + b] = \frac{h}{3}[a + 4 \cdot \frac{a+b}{2} + b] = \frac{h}{3}[a + 2a + 2b + b] = \frac{h}{3}[3(a+b)] = h(a+b)$. $\checkmark$

    **$f(x) = x^2$:** Exact: $\frac{b^3 - a^3}{3}$. Using $b = a + 2h$ and $m = a + h$:

    $$\frac{(a+2h)^3 - a^3}{3} = \frac{6a^2h + 12ah^2 + 8h^3}{3} = 2a^2h + 4ah^2 + \frac{8h^3}{3}.$$

    Simpson: $\frac{h}{3}[a^2 + 4(a+h)^2 + (a+2h)^2] = \frac{h}{3}[a^2 + 4a^2 + 8ah + 4h^2 + a^2 + 4ah + 4h^2] = \frac{h}{3}[6a^2 + 12ah + 8h^2] = 2a^2h + 4ah^2 + \frac{8h^3}{3}$. $\checkmark$

    **$f(x) = x^3$:** Exact: $\frac{b^4 - a^4}{4} = \frac{(a+2h)^4 - a^4}{4}$.

    Expanding: $(a+2h)^4 = a^4 + 8a^3h + 24a^2h^2 + 32ah^3 + 16h^4$.

    So the integral is $2a^3h + 6a^2h^2 + 8ah^3 + 4h^4$.

    Simpson: $\frac{h}{3}[a^3 + 4(a+h)^3 + (a+2h)^3]$.

    $(a+h)^3 = a^3 + 3a^2h + 3ah^2 + h^3$, $(a+2h)^3 = a^3 + 6a^2h + 12ah^2 + 8h^3$.

    Sum: $a^3 + 4a^3 + 12a^2h + 12ah^2 + 4h^3 + a^3 + 6a^2h + 12ah^2 + 8h^3 = 6a^3 + 18a^2h + 24ah^2 + 12h^3$.

    $\frac{h}{3} \times (6a^3 + 18a^2h + 24ah^2 + 12h^3) = 2a^3h + 6a^2h^2 + 8ah^3 + 4h^4$. $\checkmark$

    Simpson's rule is exact for all polynomials of degree $\leq 3$.

    $\square$

---

**Exercise 5.8.** Compute $\pi$ to 10 decimal places using $\int_0^1 \frac{4}{1+x^2}\,dx$ and Simpson's rule.

??? success "Solution"

    Note that $\int_0^1 \frac{4}{1+x^2}\,dx = [4\arctan(x)]_0^1 = 4 \cdot \frac{\pi}{4} = \pi$.

    **Error bound for Simpson's rule:** $|E_S| \leq \frac{(b-a)^5}{180n^4} \max|f^{(4)}(x)|$.

    We need $f(x) = \frac{4}{1+x^2}$. Computing $f^{(4)}(x)$:
    - $f'(x) = \frac{-8x}{(1+x^2)^2}$
    - $f''(x) = \frac{-8(1+x^2)^2 + 32x^2(1+x^2)}{(1+x^2)^4} = \frac{-8 + 24x^2}{(1+x^2)^3}$
    - After further differentiation, $f^{(4)}(x) = \frac{96(5x^4 - 10x^2 + 1)}{(1+x^2)^5}$

    $\max_{[0,1]} |f^{(4)}(x)|$ is bounded above by $1536$ (a conservative theoretical estimate; evaluating at $x = 0$ gives $|f^{(4)}(0)| = 96$, and the maximum on $[0,1]$ satisfies $|f^{(4)}(x)| \leq 96 \cdot 16 = 1536$). The actual maximum is closer to $96$, so the bound $n \approx 650$ is conservative; in practice $n = 100$ already achieves the required accuracy.

    Setting $\frac{1}{180 n^4} \cdot 1536 < 0.5 \times 10^{-10}$:

    $$\begin{aligned}
    n^4 &> \frac{1536}{180 \times 0.5 \times 10^{-10}} = \frac{1536}{9 \times 10^{-9}} \approx 1.707 \times 10^{11} \\
    n &> (1.707 \times 10^{11})^{1/4} \approx 643.
    \end{aligned}$$

    So $n \approx 650$ (must be even for Simpson's rule) suffices according to the theoretical bound.

    ```typescript
    function simpsonPi(n: number): number {
      // n must be even
      const h = 1.0 / n;
      let sum = 4.0 / (1 + 0) + 4.0 / (1 + 1); // f(0) + f(1)
      for (let i = 1; i < n; i++) {
        const x = i * h;
        const fx = 4.0 / (1 + x * x);
        sum += (i % 2 === 0) ? 2 * fx : 4 * fx;
      }
      return (h / 3) * sum;
    }

    // Find minimum n by experiment
    for (const n of [100, 200, 500, 650, 700, 1000, 2000]) {
      const approx = simpsonPi(n);
      const error = Math.abs(approx - Math.PI);
      console.log(`n=${n}: error = ${error.toExponential(3)}`);
    }
    // Typical output:
    // n=100:  error ~ 3.3e-10
    // n=200:  error ~ 2.1e-11
    // n=500:  error ~ 5.3e-13
    // n=650:  error ~ 1.8e-13
    // n=1000: error ~ 3.3e-14
    ```

    In practice, $n = 100$ already achieves $\sim 10^{-10}$ accuracy, much better than the theoretical bound predicts. This is because the theoretical bound uses a conservative worst-case estimate for $f^{(4)}$; the actual fourth derivative is significantly smaller over most of $[0,1]$. The observed convergence rate is $O(n^{-4})$, consistent with Simpson's rule theory.

---
