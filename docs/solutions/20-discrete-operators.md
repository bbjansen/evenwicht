<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 20: Sequences & Discrete Operators

!!! info "Convention note"

    This chapter defines the **backward difference** $\Delta = 1 - L$, so $\Delta x_t = x_t - x_{t-1}$ (Definition 20.7). Most solutions use this convention. However, Exercises 20.6 (summation by parts) and 20.9 (Euler–Maclaurin) use the **forward difference** $\Delta_f x_t = x_{t+1} - x_t$, which is the standard convention for those classical results. The two are related by a time shift: $\Delta_f x_t = \Delta x_{t+1}$. Each solution states which convention it uses.

---

**Exercise 20.1.** Let $x_t = 3t + 2$ for $t = 0, 1, \ldots, 5$. Compute $\Delta x_t$ and $\Delta^2 x_t$. Explain why $\Delta^2 = 0$ for any linear (affine) sequence.

??? success "Solution"

    Using the backward difference $\Delta x_t = x_t - x_{t-1}$ (Definition 20.7):

    $$\Delta x_t = (3t + 2) - (3(t-1) + 2) = 3t + 2 - 3t + 3 - 2 = 3.$$

    $$\Delta^2 x_t = \Delta(\Delta x_t) = \Delta(3) = 3 - 3 = 0.$$

    **Why $\Delta^2 = 0$ for affine sequences:** If $x_t = at + b$, then $\Delta x_t = x_t - x_{t-1} = a(t) + b - a(t-1) - b = a$, a constant. Then $\Delta^2 x_t = \Delta(a) = a - a = 0$. The difference operator $\Delta$ reduces the degree of a polynomial by 1 (analogous to how differentiation $D$ reduces degree by 1 in the continuous case). A degree-1 polynomial (affine function) becomes a constant after one application of $\Delta$, and a constant becomes 0 after a second application. In general, $\Delta^{n+1}(p) = 0$ for any polynomial $p$ of degree $n$, the discrete analogue of $D^{n+1}(p) = 0$.

    $\square$

---

**Exercise 20.2.** Compute the convolution of $f = [1, 1, 1]$ and $g = [1, -1]$. Interpret the result as polynomial multiplication: what are $f(x)$ and $g(x)$, and what is their product?

??? success "Solution"

    The convolution $(f * g)_k = \sum_j f_j g_{k-j}$.

    $f$ has indices $0, 1, 2$ and $g$ has indices $0, 1$. The result has indices $0, 1, 2, 3$.

    $(f*g)_0 = f_0 g_0 = 1 \cdot 1 = 1$.

    $(f*g)_1 = f_0 g_1 + f_1 g_0 = 1 \cdot (-1) + 1 \cdot 1 = 0$.

    $(f*g)_2 = f_0 g_2 + f_1 g_1 + f_2 g_0 = 0 + 1 \cdot (-1) + 1 \cdot 1 = 0$.

    $(f*g)_3 = f_1 g_2 + f_2 g_1 = 0 + 1 \cdot (-1) = -1$.

    Result: $f * g = [1, 0, 0, -1]$.

    **Polynomial interpretation:** $f(x) = 1 + x + x^2$ and $g(x) = 1 - x$. Their product:

    $$f(x) \cdot g(x) = (1 + x + x^2)(1 - x) = 1 + x + x^2 - x - x^2 - x^3 = 1 - x^3.$$

    The coefficients of $1 - x^3$ are $[1, 0, 0, -1]$, confirming the convolution result. Convolution of coefficient sequences corresponds exactly to polynomial multiplication.

    $\square$

---

**Exercise 20.3.** Show that $L^j L^k = L^{j+k}$ for all integers $j, k$. (This states that the powers of $L$ form a group under composition.)

??? success "Solution"

    The lag operator $L$ acts on sequences by $L(x_t) = x_{t-1}$, so $L^m(x_t) = x_{t-m}$ for any integer $m$.

    $$L^j(L^k(x_t)) = L^j(x_{t-k}) = x_{(t-k)-j} = x_{t-(j+k)} = L^{j+k}(x_t).$$

    Since this holds for all sequences $\{x_t\}$ and all $t$, $L^j L^k = L^{j+k}$ as operators.

    This shows that the powers of $L$ form a group under composition: the operation is associative (composition of functions), the identity is $L^0 = I$, and every $L^j$ has an inverse $L^{-j}$ (the forward shift). The group is isomorphic to $(\mathbb{Z}, +)$.

    $\square$

---

**Exercise 20.4.** Using Theorem 20.11, expand $\Delta^4 x_t$ as a weighted sum of $x_t, x_{t-1}, x_{t-2}, x_{t-3}, x_{t-4}$. Verify the coefficients sum to zero.

??? success "Solution"

    By Theorem 20.11 (the binomial theorem for operators), $\Delta^n = (I - L)^n = \sum_{k=0}^{n} \binom{n}{k}(-1)^k L^k$.

    For $n = 4$:

    $$\Delta^4 = \sum_{k=0}^{4}\binom{4}{k}(-1)^k L^k = L^0 - 4L^1 + 6L^2 - 4L^3 + L^4.$$

    Applying to $x_t$:

    $$\Delta^4 x_t = x_t - 4x_{t-1} + 6x_{t-2} - 4x_{t-3} + x_{t-4}.$$

    **Verification that coefficients sum to zero:**

    $$1 + (-4) + 6 + (-4) + 1 = 0. \checkmark$$

    This must hold because $\Delta^4$ applied to a constant gives zero (a constant is a degree-0 polynomial, and $\Delta$ kills polynomials of degree less than the order of differencing). Setting $x_t = c$ for all $t$: $\Delta^4(c) = c(1 - 4 + 6 - 4 + 1) = 0$.

    $\square$

---

**Exercise 20.5.** Prove that $\Delta(x_t \cdot y_t) = x_t \cdot \Delta y_t + y_{t-1} \cdot \Delta x_t$. This is the *discrete product rule* (Leibniz rule for differences). Compare to the continuous product rule $D(fg) = fDg + gDf$.

??? success "Solution"

    Using the backward difference $\Delta x_t = x_t - x_{t-1}$ (the convention of this chapter):

    $$\Delta(x_t y_t) = x_t y_t - x_{t-1} y_{t-1}.$$

    Add and subtract $x_t y_{t-1}$:

    $$\begin{aligned}
    &= x_t y_t - x_t y_{t-1} + x_t y_{t-1} - x_{t-1} y_{t-1} = x_t(y_t - y_{t-1}) + y_{t-1}(x_t - x_{t-1}) \\
    &= x_t \cdot \Delta y_t + y_{t-1} \cdot \Delta x_t.
    \end{aligned}$$

    **Comparison with the continuous product rule:** The continuous rule $D(fg) = fDg + gDf$ is symmetric in $f$ and $g$. The discrete rule is **not symmetric**: one factor is evaluated at $t$ and the other at $t-1$. This asymmetry arises because the difference quotient is inherently one-sided, unlike the derivative which is a limit.

    $\square$

---

**Exercise 20.6.** The *summation by parts* formula states that $\sum_{t=a}^{b} f_t \Delta g_t = [f_t g_t]_a^{b+1} - \sum_{t=a}^{b} g_{t+1} \Delta f_t$. Derive this from the discrete product rule (Exercise 20.5). (This is the discrete analogue of integration by parts.)

??? success "Solution"

    This exercise uses the forward-difference version of the product rule, which is the standard form for summation by parts. The forward difference is $\Delta_f x_t = x_{t+1} - x_t$, related to the backward difference by $\Delta_f x_t = \Delta x_{t+1}$. For the summation by parts formula as stated, the relevant product rule with forward differences is:

    $$\Delta_f(f_t g_t) = f_{t+1}g_{t+1} - f_t g_t = f_t \Delta_f g_t + g_{t+1} \Delta_f f_t.$$

    Rearranging:

    $$f_t \Delta_f g_t = \Delta_f(f_t g_t) - g_{t+1} \Delta_f f_t.$$

    Sum both sides from $t = a$ to $t = b$:

    $$\sum_{t=a}^{b} f_t \Delta_f g_t = \sum_{t=a}^{b} \Delta_f(f_t g_t) - \sum_{t=a}^{b} g_{t+1} \Delta_f f_t.$$

    The first sum on the right is telescoping:

    $$\sum_{t=a}^{b} \Delta_f(f_t g_t) = \sum_{t=a}^{b}(f_{t+1}g_{t+1} - f_t g_t) = f_{b+1}g_{b+1} - f_a g_a = [f_t g_t]_a^{b+1}.$$

    Therefore:

    $$\sum_{t=a}^{b} f_t \Delta g_t = [f_t g_t]_a^{b+1} - \sum_{t=a}^{b} g_{t+1} \Delta f_t.$$

    This is the **summation by parts** formula, the discrete analogue of integration by parts $\int_a^b f\,dg = [fg]_a^b - \int_a^b g\,df$.

    $\square$

---

**Exercise 20.7.** An MA(2) process is defined by $y_t = \varepsilon_t + 0.5\varepsilon_{t-1} - 0.3\varepsilon_{t-2}$. Express this using the lag operator as $y_t = \theta(L)\varepsilon_t$. Identify $\theta(L)$. Compute the autocovariance $\gamma(1) = \operatorname{Cov}(y_t, y_{t-1})$ assuming $\operatorname{Var}(\varepsilon_t) = \sigma^2$.

??? success "Solution"

    **Lag operator form:** $y_t = (1 + 0.5L - 0.3L^2)\varepsilon_t = \theta(L)\varepsilon_t$, where $\theta(L) = 1 + 0.5L - 0.3L^2$.

    **Autocovariance $\gamma(1) = \operatorname{Cov}(y_t, y_{t-1})$:**

    Write $y_t = \varepsilon_t + \theta_1 \varepsilon_{t-1} + \theta_2 \varepsilon_{t-2}$ with $\theta_1 = 0.5$, $\theta_2 = -0.3$.

    $$\gamma(1) = \operatorname{Cov}(y_t, y_{t-1}) = \mathbb{E}[y_t y_{t-1}] - \mathbb{E}[y_t]\mathbb{E}[y_{t-1}].$$

    Since $\mathbb{E}[y_t] = 0$:

    $$\gamma(1) = \mathbb{E}[(\varepsilon_t + 0.5\varepsilon_{t-1} - 0.3\varepsilon_{t-2})(\varepsilon_{t-1} + 0.5\varepsilon_{t-2} - 0.3\varepsilon_{t-3})].$$

    Using $\mathbb{E}[\varepsilon_s \varepsilon_r] = \sigma^2$ if $s = r$ and $0$ otherwise:

    $$\gamma(1) = 0.5\sigma^2 + (0.5)(-0.3)\sigma^2 + 0 = 0.5\sigma^2 - 0.15\sigma^2 = 0.35\sigma^2.$$

    (The nonzero terms come from: $0.5\varepsilon_{t-1}$ with $\varepsilon_{t-1}$ giving $0.5\sigma^2$, and $-0.3\varepsilon_{t-2}$ with $0.5\varepsilon_{t-2}$ giving $-0.15\sigma^2$.)

    In general, for an MA($q$) process, $\gamma(h) = \sigma^2 \sum_{j=0}^{q-h} \theta_j \theta_{j+h}$ (with $\theta_0 = 1$). Here $\gamma(1) = \sigma^2(\theta_0\theta_1 + \theta_1\theta_2) = \sigma^2(0.5 + (0.5)(-0.3)) = 0.35\sigma^2$.

    $\square$

---

**Exercise 20.8.** Compute the $Z$-transform of the sequence $x_t = (-1)^t$ for $t \geq 0$. What is the region of convergence? Use Theorem 20.21 to find $\mathcal{Z}\{x_{t-1}\}$ (with $x_{-1} = 0$).

??? success "Solution"

    $$X(z) = \sum_{t=0}^{\infty} (-1)^t z^{-t} = \sum_{t=0}^{\infty} (-z^{-1})^t = \frac{1}{1 - (-z^{-1})} = \frac{1}{1 + z^{-1}} = \frac{z}{z + 1}.$$

    This converges when $|-z^{-1}| < 1$, i.e., $|z| > 1$.

    **Region of convergence:** $\{z \in \mathbb{C} : |z| > 1\}$.

    **$\mathcal{Z}\{x_{t-1}\}$ using the time-shift property:** For causal sequences with $x_{-1} = 0$, Theorem 20.21 gives:

    $$\mathcal{Z}\{x_{t-1}\} = z^{-1} X(z) = z^{-1} \cdot \frac{z}{z+1} = \frac{1}{z + 1}.$$

    $\square$

---

**Exercise 20.9.** The *Euler–Maclaurin formula* relates a discrete sum to a continuous integral plus correction terms involving differences. State the formula to second order and use it to improve the estimate $\sum_{t=1}^{100} 1/t \approx \ln(100) + \gamma$ (where $\gamma \approx 0.5772$ is the Euler–Mascheroni constant).

??? success "Solution"

    The Euler–Maclaurin formula to second order is:

    $$\sum_{t=a}^{b} f(t) = \int_a^b f(x)\,dx + \frac{f(a) + f(b)}{2} + \frac{1}{12}(f'(b) - f'(a)) - \cdots$$

    For $f(t) = 1/t$, $a = 1$, $b = 100$:

    $$\int_1^{100} \frac{1}{x}\,dx = \ln(100) \approx 4.60517.$$

    $$\frac{f(1) + f(100)}{2} = \frac{1 + 0.01}{2} = 0.505.$$

    $f'(x) = -1/x^2$, so $\frac{1}{12}(f'(100) - f'(1)) = \frac{1}{12}(-0.0001 - (-1)) = \frac{1}{12}(0.9999) \approx 0.08333$.

    Euler–Maclaurin estimate:

    $$\sum_{t=1}^{100}\frac{1}{t} \approx \ln(100) + 0.505 + 0.08333 \approx 4.60517 + 0.505 + 0.08333 = 5.19350.$$

    The exact value is $H_{100} = \sum_{t=1}^{100} 1/t \approx 5.18738$.

    The well-known asymptotic is $H_n \approx \ln n + \gamma$ where $\gamma \approx 0.57722$ is the Euler–Mascheroni constant ($\gamma \approx 0.5772$). This gives $\ln(100) + 0.57722 \approx 5.18239$, which has error $\approx 0.005$.

    The Euler–Maclaurin formula gives a better approximation by including the correction terms. The estimate $5.194$ overshoots by about $0.006$, which could be improved by including the next correction term $-\frac{1}{720}(f'''(b) - f'''(a))$. The key insight is that the Euler–Maclaurin formula systematically improves the trapezoidal-rule approximation to the integral by adding correction terms involving derivatives at the endpoints.

    $\square$

---

**Exercise 20.10.** Prove that the set of all sequences $\{x_t\}_{t \in \mathbb{Z}}$ forms a commutative ring under pointwise addition and convolution as multiplication. (A *ring* is an algebraic structure satisfying the axioms of addition and multiplication listed in the standard algebra references; here, verify the axioms directly.) What is the multiplicative identity? Which sequences have convolution inverses?

??? success "Solution"

    Let $\mathcal{S} = \{(x_t)_{t \in \mathbb{Z}}\}$ be the set of all doubly-infinite sequences. Define:

    - Addition: $(x + y)_t = x_t + y_t$ (pointwise).
    - Multiplication: $(x * y)_t = \sum_{k} x_k y_{t-k}$ (convolution).

    **1. $(\mathcal{S}, +)$ is an abelian group:** Pointwise addition of sequences is commutative, associative, has identity $\mathbf{0} = (\ldots, 0, 0, 0, \ldots)$, and every element $x$ has additive inverse $-x$ defined by $(-x)_t = -x_t$. $\checkmark$

    **2. Convolution is associative:**

    $$((x*y)*z)_t = \sum_k (x*y)_k z_{t-k} = \sum_k \left(\sum_j x_j y_{k-j}\right) z_{t-k} = \sum_{j,k} x_j y_{k-j} z_{t-k}.$$

    Substituting $m = k - j$: $= \sum_{j,m} x_j y_m z_{t-j-m} = \sum_j x_j (y*z)_{t-j} = (x*(y*z))_t.$ $\checkmark$

    **3. Convolution is commutative:**

    $$(x*y)_t = \sum_k x_k y_{t-k} = \sum_m x_{t-m} y_m = (y*x)_t,$$

    where the substitution $m = t - k$ was used. $\checkmark$

    **4. Distributivity:** $x * (y + z) = x*y + x*z$ follows from linearity of summation. $\checkmark$

    **Multiplicative identity:** The Kronecker delta sequence $\delta$ with $\delta_0 = 1$ and $\delta_t = 0$ for $t \neq 0$. Then $(\delta * x)_t = \sum_k \delta_k x_{t-k} = x_t$. $\checkmark$

    **Convolution inverses:** A sequence $x$ has a convolution inverse $y$ (i.e., $x * y = \delta$) if and only if $x_0 \neq 0$. The inverse can be computed recursively: $y_0 = 1/x_0$, and for $t > 0$: $y_t = -\frac{1}{x_0}\sum_{k=1}^{t} x_k y_{t-k}$. This is analogous to the condition that a formal power series $\sum a_n z^n$ is invertible iff $a_0 \neq 0$.

    $\square$

---
