<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 6: Series & Approximation

**Exercise 6.1.** Determine convergence or divergence.

??? success "Solution"

    **(a)** $\sum_{n=1}^{\infty} \frac{1}{n^3}$

    This is a $p$-series with $p = 3 > 1$. **Converges** (by the $p$-series test).

    **(b)** $\sum_{n=1}^{\infty} \frac{n}{n+1}$

    $\lim_{n \to \infty} \frac{n}{n+1} = 1 \neq 0$. The terms do not tend to zero, so the series **diverges** (by the divergence test / $n$-th term test).

    **(c)** $\sum_{n=0}^{\infty} \frac{3^n}{4^n} = \sum_{n=0}^{\infty} (3/4)^n$

    This is a geometric series with ratio $r = 3/4$. Since $|r| < 1$, it **converges** to $\frac{1}{1 - 3/4} = 4$.

    **(d)** $\sum_{n=1}^{\infty} \frac{(-1)^n}{n^2}$

    The series $\sum \frac{1}{n^2}$ converges (p-series, $p = 2 > 1$), so $\sum \frac{(-1)^n}{n^2}$ **converges absolutely** (and hence converges). Its sum is $-\pi^2/12$.

---

**Exercise 6.2.** Maclaurin polynomial $T_4(x)$ for $f(x) = e^{-x^2}$.

??? success "Solution"

    The Maclaurin series for $e^u$ is $1 + u + \frac{u^2}{2} + \cdots$. Setting $u = -x^2$:

    $$e^{-x^2} = 1 + (-x^2) + \frac{(-x^2)^2}{2} + \cdots = 1 - x^2 + \frac{x^4}{2} - \cdots$$

    So $T_4(x) = 1 - x^2 + \frac{x^4}{2}$.

    **At $x = 0.5$:** $T_4(0.5) = 1 - 0.25 + \frac{0.0625}{2} = 1 - 0.25 + 0.03125 = 0.78125$.

    **True value:** $e^{-0.25} \approx 0.77880$. Error $\approx 0.00245$.

---

**Exercise 6.3.** Present value of a perpetuity.

??? success "Solution"

    The present value is:

    $$PV = \sum_{n=1}^{\infty} \frac{C}{(1+r)^n} = C \sum_{n=1}^{\infty} \left(\frac{1}{1+r}\right)^n = C \cdot \frac{1/(1+r)}{1 - 1/(1+r)} = \frac{C}{r}.$$

    With $C = 500$ and $r = 0.04$:

    $$PV = \frac{500}{0.04} = 12{,}500.$$

---

**Exercise 6.4.** Use the ratio test to show $\sum_{n=0}^{\infty} x^n / n!$ converges for all $x$.

??? success "Solution"

    Let $a_n = x^n / n!$. The ratio test gives:

    $$\begin{aligned}
    \left|\frac{a_{n+1}}{a_n}\right| &= \left|\frac{x^{n+1}}{(n+1)!} \cdot \frac{n!}{x^n}\right| = \frac{|x|}{n+1}. \\
    L &= \lim_{n \to \infty} \frac{|x|}{n+1} = 0 < 1 \quad \text{for every fixed } x \in \mathbb{R}.
    \end{aligned}$$

    Since $L = 0 < 1$, the series converges absolutely for all $x$. The radius of convergence is $R = \infty$.

---

**Exercise 6.5.** Prove $\sum_{n=1}^{\infty} \frac{1}{n \cdot 2^n}$ converges and find its sum.

??? success "Solution"

    **Convergence:** By the ratio test, $\left|\frac{a_{n+1}}{a_n}\right| = \frac{n}{n+1} \cdot \frac{1}{2} \to \frac{1}{2} < 1$. So the series converges.

    **Finding the sum:** Start with the geometric series $\sum_{n=0}^{\infty} x^n = \frac{1}{1-x}$ for $|x| < 1$.

    Integrate both sides from $0$ to $t$ (where $|t| < 1$):

    $$\sum_{n=0}^{\infty} \frac{t^{n+1}}{n+1} = -\ln(1-t).$$

    Reindexing ($m = n+1$):

    $$\sum_{m=1}^{\infty} \frac{t^m}{m} = -\ln(1-t).$$

    Set $t = 1/2$:

    $$\sum_{n=1}^{\infty} \frac{1}{n \cdot 2^n} = -\ln(1 - 1/2) = -\ln(1/2) = \ln 2 \approx 0.6931.$$

---

**Exercise 6.6.** Leibniz formula: how many terms for error $< 10^{-3}$ and $< 10^{-6}$?

??? success "Solution"

    The series $\sum_{n=0}^{\infty} \frac{(-1)^n}{2n+1}$ is an alternating series with decreasing terms. By the alternating series estimation theorem, the error after $N$ terms is bounded by the absolute value of the first omitted term:

    $$|R_N| \leq \frac{1}{2(N) + 1} = \frac{1}{2N+1}.$$

    (Here the partial sum uses terms $n = 0, 1, \ldots, N-1$, so the first omitted term is $n = N$.)

    **For error $< 10^{-3}$:** Need $\frac{1}{2N+1} < 10^{-3}$, i.e., $2N + 1 > 1000$, so $N \geq 500$. We need at least **500 terms**.

    **For error $< 10^{-6}$:** Need $\frac{1}{2N+1} < 10^{-6}$, so $N \geq 500{,}000$. We need at least **500,000 terms**.

    The Leibniz series converges very slowly.

---

**Exercise 6.7.** Outline the Riemann rearrangement algorithm.

??? success "Solution"

    Given the alternating harmonic series $\sum (-1)^{n+1}/n = 1 - 1/2 + 1/3 - 1/4 + \cdots$ (conditionally convergent) and a target $T$:

    **Algorithm:**

    1. Separate the series into positive terms $p_k = 1, 1/3, 1/5, 1/7, \ldots$ and negative terms $q_k = -1/2, -1/4, -1/6, \ldots$, each listed in their natural order.
    2. Initialise partial sum $S = 0$. Maintain pointers $i = 1$ (into positive terms) and $j = 1$ (into negative terms).
    3. **While** $S < T$: add positive terms one at a time ($S \leftarrow S + p_i$, $i \leftarrow i + 1$) until $S \geq T$.
    4. **While** $S > T$: add negative terms one at a time ($S \leftarrow S + q_j$, $j \leftarrow j + 1$) until $S \leq T$.
    5. Repeat steps 3-4.

    **Why this works:** The positive terms $\sum 1/(2k-1)$ diverge to $+\infty$ and the negative terms $\sum -1/(2k)$ diverge to $-\infty$, so it is always possible to overshoot $T$ in either direction. However, since the individual terms $\to 0$, the overshoots become arbitrarily small, so the partial sums converge to $T$.

---

**Exercise 6.8.** Two strategies for computing $\ln(3)$ with convergent series.

??? success "Solution"

    **Strategy 1: Splitting.** Write $\ln(3) = \ln(3/2) + \ln(2)$.

    For $\ln(2) = \ln(1 + 1)$: Use $\ln(1 + x) = x - x^2/2 + x^3/3 - \cdots$ with $x = 1$. This is at the boundary of convergence (converges by the alternating series test but slowly).

    Better: $\ln(2) = -\ln(1/2) = -\ln(1 + (-1/2)) = 1/2 + 1/8 + 1/24 + \cdots$ converges quickly.

    For $\ln(3/2) = \ln(1 + 1/2) = 1/2 - 1/8 + 1/24 - \cdots$, which converges since $|x| = 1/2 < 1$.

    So $\ln(3) = \ln(1 + 1/2) + \ln(2)$, and both pieces can be computed from convergent series (though $\ln(2)$ at $x = 1$ is slow; better to use Strategy 2 for both).

    **Strategy 2: The arctanh series.** Use the identity:

    $$\ln\!\left(\frac{1+y}{1-y}\right) = 2\sum_{k=0}^{\infty} \frac{y^{2k+1}}{2k+1} = 2\!\left(y + \frac{y^3}{3} + \frac{y^5}{5} + \cdots\right).$$

    Setting $\frac{1+y}{1-y} = 3$ gives $1 + y = 3 - 3y$, so $y = 1/2$. Then:

    $$\ln(3) = 2\sum_{k=0}^{\infty} \frac{(1/2)^{2k+1}}{2k+1} = 2\!\left(\frac{1}{2} + \frac{1}{24} + \frac{1}{160} + \frac{1}{896} + \cdots\right).$$

    This converges much faster than the standard $\ln(1+x)$ series because $|y| = 1/2$ and the series involves only odd powers, so the effective ratio is $y^2 = 1/4$. Similarly, $\ln(2) = 2 \operatorname{arctanh}(1/3)$, from $\frac{1+y}{1-y} = 2 \implies y = 1/3$, which converges even faster.

---
