<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 3: Limits & Continuity

**Exercise 3.1.** Use the $\varepsilon$-$\delta$ definition to prove $\lim_{x \to 3}(2x+1) = 7$.

??? success "Solution"

    *Proof.* Let $\varepsilon > 0$ be given. We need $\delta > 0$ such that $|x - 3| < \delta$ implies $|(2x+1) - 7| < \varepsilon$.

    Note that $|(2x+1) - 7| = |2x - 6| = 2|x - 3|$.

    Choose $\delta = \varepsilon / 2$. Then if $|x - 3| < \delta$:

    $$\lvert (2x+1) - 7 \rvert = 2\lvert x - 3 \rvert < 2\delta = 2 \cdot \frac{\varepsilon}{2} = \varepsilon.$$

    $\square$

---

**Exercise 3.2.** Evaluate the following limits.

??? success "Solution"

    **(a)** $\lim_{x \to 2}(x^2 + 3x - 1)$

    By the sum and product limit laws, this equals $(2)^2 + 3(2) - 1 = 4 + 6 - 1 = 9$.

    **(b)** $\lim_{x \to 1}\frac{x^2 + x}{x + 1}$

    The denominator is nonzero at $x = 1$ (it equals $2$), so by the quotient rule:

    $$\frac{1^2 + 1}{1 + 1} = \frac{2}{2} = 1.$$

    **(c)** $\lim_{x \to 0}\frac{\sin(3x)}{x}$

    Rewrite as $3 \cdot \frac{\sin(3x)}{3x}$. As $x \to 0$, $3x \to 0$, so $\frac{\sin(3x)}{3x} \to 1$ by the standard limit. Therefore the answer is $3$.

---

**Exercise 3.3.** Determine continuity at $x = 2$.

??? success "Solution"

    **(a)** $f(x) = \frac{x^2 - 4}{x - 2}$

    For $x \neq 2$: $f(x) = \frac{(x-2)(x+2)}{x-2} = x + 2$. So $\lim_{x \to 2} f(x) = 4$. But $f(2)$ is undefined (the function has a division by zero). This is a **removable discontinuity** at $x = 2$.

    **(b)** $g(x) = \begin{cases} x + 1 & x < 2 \\ 5 & x = 2 \\ x + 1 & x > 2 \end{cases}$

    $\lim_{x \to 2} g(x) = \lim_{x \to 2}(x + 1) = 3$, but $g(2) = 5 \neq 3$. This is a **removable discontinuity** (the limit exists but does not equal the function value).

    **(c)** $h(x) = \begin{cases} x + 1 & x \leq 2 \\ x^2 & x > 2 \end{cases}$

    $\lim_{x \to 2^-} h(x) = 2 + 1 = 3$ and $\lim_{x \to 2^+} h(x) = 2^2 = 4$. The one-sided limits differ, so the limit does not exist. This is a **jump discontinuity** at $x = 2$.

---

**Exercise 3.4.** Use the squeeze theorem to evaluate $\lim_{x \to 0} x^2 \sin(1/x)$.

??? success "Solution"

    Since $-1 \leq \sin(1/x) \leq 1$ for all $x \neq 0$, multiplying by $x^2 \geq 0$:

    $$-x^2 \leq x^2 \sin(1/x) \leq x^2.$$

    Since $\lim_{x \to 0}(-x^2) = 0$ and $\lim_{x \to 0} x^2 = 0$, the squeeze theorem gives:

    $$\lim_{x \to 0} x^2 \sin(1/x) = 0.$$

---

**Exercise 3.5.** Prove the sign preservation property.

??? success "Solution"

    *Proof.* Suppose $f$ is continuous at $a$ and $f(a) > 0$. Set $\varepsilon = f(a)/2 > 0$.

    By continuity, there exists $\delta > 0$ such that $|x - a| < \delta$ implies $|f(x) - f(a)| < \varepsilon = f(a)/2$.

    This means $f(a) - f(a)/2 < f(x) < f(a) + f(a)/2$, i.e., $f(a)/2 < f(x)$.

    Since $f(a) > 0$, it follows that $f(x) > f(a)/2 > 0$ for all $x \in (a - \delta, a + \delta)$.

    $\square$

---

**Exercise 3.6.** Bisection method for $e^x - 3x = 0$ on $[0, 1]$.

??? success "Solution"

    Let $f(x) = e^x - 3x$.

    $f(0) = 1 > 0$, $f(1) = e - 3 \approx -0.2817 < 0$. So a root exists in $[0,1]$ by IVT.

    **Step 1:** Midpoint $c_1 = 0.5$. $f(0.5) = e^{0.5} - 1.5 \approx 1.6487 - 1.5 = 0.1487 > 0$. Root in $[0.5, 1]$.

    **Step 2:** Midpoint $c_2 = 0.75$. $f(0.75) = e^{0.75} - 2.25 \approx 2.1170 - 2.25 = -0.1330 < 0$. Root in $[0.5, 0.75]$.

    **Step 3:** Midpoint $c_3 = 0.625$. $f(0.625) = e^{0.625} - 1.875 \approx 1.8682 - 1.875 = -0.0068 < 0$. Root in $[0.5, 0.625]$.

    **Step 4:** Midpoint $c_4 = 0.5625$. $f(0.5625) = e^{0.5625} - 1.6875 \approx 1.7551 - 1.6875 = 0.0676 > 0$. Root in $[0.5625, 0.625]$.

    After four steps, the root is bracketed in $[0.5625, 0.625]$, with midpoint $\approx 0.6191$ as the current best estimate.

---

**Exercise 3.7.** Uniform continuity of $f(x) = x^2$.

??? success "Solution"

    **Part 1: $f(x) = x^2$ is uniformly continuous on $[0, 1]$.**

    Let $\varepsilon > 0$. For $x, y \in [0,1]$:

    $$\lvert x^2 - y^2 \rvert = \lvert x + y \rvert\lvert x - y \rvert \leq (\lvert x \rvert + \lvert y \rvert)\lvert x - y \rvert \leq 2\lvert x - y \rvert.$$

    Choose $\delta = \varepsilon/2$. Then $|x - y| < \delta$ implies $|x^2 - y^2| \leq 2|x - y| < 2\delta = \varepsilon$.

    $\square$

    **Part 2: $f(x) = x^2$ is not uniformly continuous on $\mathbb{R}$.**

    Take $\varepsilon = 1$. For any $\delta > 0$, choose $x = 1/\delta$ and $y = x + \delta/2 = 1/\delta + \delta/2$. Then $|x - y| = \delta/2 < \delta$, but:

    $$\lvert x^2 - y^2 \rvert = \lvert x + y \rvert\lvert x - y \rvert = \left(\frac{2}{\delta} + \frac{\delta}{2}\right)\frac{\delta}{2} = 1 + \frac{\delta^2}{4} > 1 = \varepsilon.$$

    So no single $\delta$ works for all pairs, and $f$ is not uniformly continuous on $\mathbb{R}$.

    $\square$

---

**Exercise 3.8.** Prove $f(x) = \sin(1/x)$ has an essential discontinuity at $x = 0$.

??? success "Solution"

    *Proof.* Let $L$ be any proposed limit. We will show $L$ cannot be the limit.

    **Case 1: $L \neq 1$.** Set $\varepsilon = |1 - L|/2 > 0$. For any $\delta > 0$, choose $x = \frac{1}{2n\pi + \pi/2}$ for sufficiently large $n$ so that $0 < x < \delta$. Then $\sin(1/x) = \sin(2n\pi + \pi/2) = 1$, so $|f(x) - L| = |1 - L| = 2\varepsilon \geq \varepsilon$.

    **Case 2: $L = 1$.** Set $\varepsilon = 1$. For any $\delta > 0$, choose $x = \frac{1}{2n\pi + 3\pi/2}$ for large $n$ so that $0 < x < \delta$. Then $\sin(1/x) = \sin(2n\pi + 3\pi/2) = -1$, so $|f(x) - L| = |-1 - 1| = 2 \geq \varepsilon$.

    In both cases, the $\varepsilon$-$\delta$ definition of a limit is violated. More directly: for any $\delta > 0$, the interval $(0, \delta)$ contains points where $\sin(1/x) = 1$ and points where $\sin(1/x) = -1$. Thus $f(x)$ oscillates between $-1$ and $1$ in every neighbourhood of $0$ and no limit can exist. This is an essential (oscillatory) discontinuity.

    $\square$

---
