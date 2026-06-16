<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 4: Differential Calculus

**Exercise 4.1.** Compute $\frac{d}{dx}[5x^3 - 2x + 7]$.

??? success "Solution"

    By the power rule and sum rule:

    $$\begin{aligned}
    \frac{d}{dx}[5x^3] &= 15x^2, \quad \frac{d}{dx}[-2x] = -2, \quad \frac{d}{dx}[7] = 0. \\
    \frac{d}{dx}[5x^3 - 2x + 7] &= 15x^2 - 2.
    \end{aligned}$$

---

**Exercise 4.2.** Compute $\frac{d}{dx}[x^2 e^x]$ using the product rule.

??? success "Solution"

    Let $u = x^2$ and $v = e^x$. Then $u' = 2x$ and $v' = e^x$.

    $$\frac{d}{dx}[x^2 e^x] = u'v + uv' = 2x e^x + x^2 e^x = e^x(x^2 + 2x).$$

    **Verification at $x = 1$:** The original function gives $f(1) = 1 \cdot e = e \approx 2.718$. The derivative gives $f'(1) = e(1 + 2) = 3e \approx 8.155$.

---

**Exercise 4.3.** Compute $\frac{d}{dx}[\cos(3x)]$ using the chain rule.

??? success "Solution"

    Let $u = 3x$, so $\frac{du}{dx} = 3$. Then:

    $$\frac{d}{dx}[\cos(3x)] = -\sin(3x) \cdot 3 = -3\sin(3x).$$

    **Expression tree before differentiation:**

    ```
      cos
       |
      mul
     /   \
    3     x
    ```

    **After differentiation (applying chain rule):**

    ```
           mul
          /   \
       neg     3
        |
       sin
        |
       mul
      /   \
     3     x
    ```

    Which simplifies to $-3\sin(3x)$.

---

**Exercise 4.4.** Derive $\frac{d}{dx}\!\left[\frac{e^x}{x^2 + 1}\right]$.

??? success "Solution"

    By the quotient rule with $u = e^x$, $v = x^2 + 1$, $u' = e^x$, $v' = 2x$:

    $$\frac{d}{dx}\!\left[\frac{e^x}{x^2 + 1}\right] = \frac{e^x(x^2 + 1) - e^x \cdot 2x}{(x^2 + 1)^2} = \frac{e^x(x^2 - 2x + 1)}{(x^2 + 1)^2} = \frac{e^x(x-1)^2}{(x^2 + 1)^2}.$$

    **At $x = 0$:** $\frac{e^0(0-1)^2}{(0+1)^2} = \frac{1 \cdot 1}{1} = 1$.

---

**Exercise 4.5.** Implicit differentiation for $\frac{x^2}{4} + \frac{y^2}{9} = 1$.

??? success "Solution"

    Differentiate both sides with respect to $x$:

    $$\frac{2x}{4} + \frac{2y}{9}\frac{dy}{dx} = 0 \implies \frac{x}{2} + \frac{2y}{9}\frac{dy}{dx} = 0.$$

    Solving: $\frac{dy}{dx} = -\frac{9x}{4y}$.

    **At $(1, \frac{3\sqrt{3}}{2})$:** First verify the point lies on the ellipse: $\frac{1}{4} + \frac{27/4}{9} = \frac{1}{4} + \frac{3}{4} = 1$. $\checkmark$

    $$\frac{dy}{dx}\bigg|_{(1, \frac{3\sqrt{3}}{2})} = -\frac{9 \cdot 1}{4 \cdot \frac{3\sqrt{3}}{2}} = -\frac{9}{6\sqrt{3}} = -\frac{3}{2\sqrt{3}} = -\frac{3\sqrt{3}}{6} = -\frac{\sqrt{3}}{2}.$$

---

**Exercise 4.6.** Prove by induction that $\frac{d^n}{dx^n}[e^{ax}] = a^n e^{ax}$.

??? success "Solution"

    *Proof.* **Base case** ($n = 1$): $\frac{d}{dx}[e^{ax}] = ae^{ax}$ by the chain rule. This equals $a^1 e^{ax}$. $\checkmark$

    **Inductive step:** Assume $\frac{d^k}{dx^k}[e^{ax}] = a^k e^{ax}$ for some $k \geq 1$. Then:

    $$\frac{d^{k+1}}{dx^{k+1}}[e^{ax}] = \frac{d}{dx}\!\left[a^k e^{ax}\right] = a^k \cdot ae^{ax} = a^{k+1}e^{ax}.$$

    By induction, $\frac{d^n}{dx^n}[e^{ax}] = a^n e^{ax}$ for all $n \geq 1$.

    $\square$

---

**Exercise 4.7.** Numerical estimation of $\frac{d}{dx}[\sin x]$ at $x = 1$.

??? success "Solution"

    The true derivative is $\cos(1) \approx 0.5403023058681398$.

    The forward difference approximation is $\frac{\sin(1 + h) - \sin(1)}{h}$.

    | $h$ | Approx. $f'$ | Absolute error |
    |-----|-------------|----------------|
    | $10^{-1}$ | $0.4972$ | $4.31 \times 10^{-2}$ |
    | $10^{-3}$ | $0.5402$ | $5.40 \times 10^{-5}$ |
    | $10^{-5}$ | $0.5403018$ | $5.40 \times 10^{-7}$ |
    | $10^{-8}$ | $0.5403023$ | $\approx 6 \times 10^{-9}$ |
    | $10^{-12}$ | $0.5403$ | $\approx 3 \times 10^{-5}$ |
    | $10^{-15}$ | $0.555$ | $\approx 1.5 \times 10^{-2}$ |

    The optimal $h$ is around $10^{-8}$. The error initially decreases as $O(h)$ (truncation error from the Taylor expansion $f'(x) \approx \frac{f(x+h) - f(x)}{h} - \frac{h}{2}f''(x) + \cdots$). For very small $h$, the error increases due to **catastrophic cancellation**: $\sin(1+h)$ and $\sin(1)$ agree to many digits, so their difference loses significant figures. The floating-point rounding error is approximately $\varepsilon_{\text{mach}}/h$ where $\varepsilon_{\text{mach}} \approx 2.22 \times 10^{-16}$. The total error is minimised when truncation error $\sim h/2$ equals rounding error $\sim \varepsilon_{\text{mach}}/h$, giving $h_{\text{opt}} \sim \sqrt{\varepsilon_{\text{mach}}} \approx 1.5 \times 10^{-8}$.

---

**Exercise 4.8.** Logarithmic differentiation of $f(x) = x^x$.

??? success "Solution"

    Take the natural log: $\ln f(x) = x \ln x$.

    Differentiate both sides: $\frac{f'(x)}{f(x)} = \ln x + x \cdot \frac{1}{x} = \ln x + 1$.

    Therefore: $f'(x) = f(x)(\ln x + 1) = x^x(\ln x + 1)$.

    **Verification via Algorithm 4.29 (symbolic differentiation):**

    Write $x^x = e^{x \ln x}$. This is the `pow` case with both base and exponent being `variable('x')`. The algorithm uses the identity $u^v = e^{v \ln u}$, so:

    $$\frac{d}{dx}[e^{x \ln x}] = e^{x \ln x} \cdot \frac{d}{dx}[x \ln x] = x^x \cdot (\ln x + 1),$$

    where $\frac{d}{dx}[x \ln x] = 1 \cdot \ln x + x \cdot \frac{1}{x} = \ln x + 1$ by the product rule. This matches. $\checkmark$

---
