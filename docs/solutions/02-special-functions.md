<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 2: Special Functions

**Exercise 2.1.** Evaluate $\Gamma(7)$ and verify that it equals $6! = 720$.

??? success "Solution"

    By the recursive property $\Gamma(n) = (n-1)!$ for positive integers:

    $\Gamma(7) = 6! = 720$.

    Alternatively, applying the recurrence $\Gamma(z+1) = z\,\Gamma(z)$ repeatedly:

    $\Gamma(7) = 6 \cdot \Gamma(6) = 6 \cdot 5 \cdot \Gamma(5) = 6 \cdot 5 \cdot 4 \cdot \Gamma(4) = 6 \cdot 5 \cdot 4 \cdot 3 \cdot \Gamma(3) = 6 \cdot 5 \cdot 4 \cdot 3 \cdot 2 \cdot \Gamma(2) = 6 \cdot 5 \cdot 4 \cdot 3 \cdot 2 \cdot 1 = 720$.

---

**Exercise 2.2.** Compute $B(3,4)$ using the Beta-Gamma relation.

??? success "Solution"

    $B(3,4) = \frac{\Gamma(3)\,\Gamma(4)}{\Gamma(7)} = \frac{2! \cdot 3!}{6!} = \frac{2 \cdot 6}{720} = \frac{12}{720} = \frac{1}{60}$.

---

**Exercise 2.3.** Compute $\binom{10}{3}$ using the multiplicative formula.

??? success "Solution"

    $\binom{10}{3} = \frac{10 \cdot 9 \cdot 8}{1 \cdot 2 \cdot 3} = \frac{720}{6} = 120$.

    Verification: $\frac{10!}{3! \cdot 7!} = \frac{10 \cdot 9 \cdot 8}{3 \cdot 2 \cdot 1} = \frac{720}{6} = 120$. $\checkmark$

---

**Exercise 2.4.** Prove that $\Gamma(1/2) = \sqrt{\pi}$.

??? success "Solution"

    *Proof.* By definition,

    $$\Gamma(1/2) = \int_0^\infty t^{-1/2} e^{-t}\,dt.$$

    Substitute $t = u^2$, so $dt = 2u\,du$. When $t = 0$, $u = 0$; when $t \to \infty$, $u \to \infty$. Then:

    $$\Gamma(1/2) = \int_0^\infty (u^2)^{-1/2} e^{-u^2} \cdot 2u\,du = \int_0^\infty \frac{1}{u} \cdot e^{-u^2} \cdot 2u\,du = 2\int_0^\infty e^{-u^2}\,du.$$

    The Gaussian integral gives $\int_0^\infty e^{-u^2}\,du = \frac{\sqrt{\pi}}{2}$. Therefore:

    $$\Gamma(1/2) = 2 \cdot \frac{\sqrt{\pi}}{2} = \sqrt{\pi}.$$

    $\square$

---

**Exercise 2.5.** Use the duplication formula with $z = 3$ to compute $\Gamma(3)\,\Gamma(3.5)$.

??? success "Solution"

    The Legendre duplication formula states:

    $$\Gamma(z)\,\Gamma\!\left(z + \tfrac{1}{2}\right) = \frac{\sqrt{\pi}}{2^{2z-1}}\,\Gamma(2z).$$

    With $z = 3$:

    $$\Gamma(3)\,\Gamma(3.5) = \frac{\sqrt{\pi}}{2^{5}}\,\Gamma(6) = \frac{\sqrt{\pi}}{32} \cdot 120 = \frac{120\sqrt{\pi}}{32} = \frac{15\sqrt{\pi}}{4}.$$

    Verification: $\Gamma(3) = 2! = 2$. For $\Gamma(3.5)$: $\Gamma(3.5) = 2.5 \cdot 1.5 \cdot 0.5 \cdot \Gamma(0.5) = 2.5 \cdot 1.5 \cdot 0.5 \cdot \sqrt{\pi} = \frac{15\sqrt{\pi}}{8}$.

    So $\Gamma(3) \cdot \Gamma(3.5) = 2 \cdot \frac{15\sqrt{\pi}}{8} = \frac{15\sqrt{\pi}}{4}$.

    $\square$

---

**Exercise 2.6.** Show that $\operatorname{erf}(x) \approx \frac{2x}{\sqrt{\pi}}$ for small $x$ and compute the next correction term.

??? success "Solution"

    By definition, $\operatorname{erf}(x) = \frac{2}{\sqrt{\pi}}\int_0^x e^{-t^2}\,dt$.

    Expand $e^{-t^2}$ in a Taylor series: $e^{-t^2} = 1 - t^2 + \frac{t^4}{2} - \cdots$

    Integrating term by term:

    $$\operatorname{erf}(x) = \frac{2}{\sqrt{\pi}}\left[t - \frac{t^3}{3} + \frac{t^5}{10} - \cdots\right]_0^x = \frac{2}{\sqrt{\pi}}\left(x - \frac{x^3}{3} + \frac{x^5}{10} - \cdots\right).$$

    The zeroth-order approximation (replacing $e^{-t^2} \approx 1$) gives:

    $$\operatorname{erf}(x) \approx \frac{2x}{\sqrt{\pi}}.$$

    The next correction term is:

    $$-\frac{2x^3}{3\sqrt{\pi}}.$$

    So to second order: $\operatorname{erf}(x) \approx \frac{2}{\sqrt{\pi}}\left(x - \frac{x^3}{3}\right) = \frac{2x}{\sqrt{\pi}} - \frac{2x^3}{3\sqrt{\pi}}$.

---

**Exercise 2.7.** Derive Stirling's approximation via Laplace's method.

??? success "Solution"

    Starting from $\Gamma(n+1) = \int_0^\infty t^n e^{-t}\,dt$, write the integrand as $e^{n \ln t - t}$. The function $h(t) = n \ln t - t$ has its maximum where $h'(t) = n/t - 1 = 0$, i.e., at $t = n$.

    Substitute $t = n + \sqrt{n}\,s$ (centring at the maximum), so $dt = \sqrt{n}\,ds$:

    $$\Gamma(n+1) = \sqrt{n}\int_{-\sqrt{n}}^{\infty} \exp\!\big[n\ln(n + \sqrt{n}\,s) - (n + \sqrt{n}\,s)\big]\,ds.$$

    Expand the log about $s = 0$:

    $$n\ln(n + \sqrt{n}\,s) = n\ln n + n\ln\!\left(1 + \frac{s}{\sqrt{n}}\right) = n\ln n + \sqrt{n}\,s - \frac{s^2}{2} + O(s^3/\sqrt{n}).$$

    So the exponent becomes:

    $$n\ln n + \sqrt{n}\,s - \frac{s^2}{2} - n - \sqrt{n}\,s + O(s^3/\sqrt{n}) = n\ln n - n - \frac{s^2}{2} + O(s^3/\sqrt{n}).$$

    Therefore:

    $$\Gamma(n+1) \approx \sqrt{n}\,e^{n\ln n - n}\int_{-\infty}^{\infty} e^{-s^2/2}\,ds = \sqrt{n}\,n^n e^{-n} \cdot \sqrt{2\pi} = \sqrt{2\pi n}\,n^n e^{-n}.$$

    This is Stirling's formula: $n! \sim \sqrt{2\pi n}\left(\frac{n}{e}\right)^n$.

    $\square$

---

**Exercise 2.8.** Prove the Beta-Gamma relation in full detail.

??? success "Solution"

    *Proof.* Write $\Gamma(a)\Gamma(b)$ as a double integral:

    $$\Gamma(a)\Gamma(b) = \int_0^\infty s^{a-1}e^{-s}\,ds \cdot \int_0^\infty t^{b-1}e^{-t}\,dt = \int_0^\infty\!\!\int_0^\infty s^{a-1}t^{b-1}e^{-(s+t)}\,ds\,dt.$$

    Apply the substitution $s = ru$, $t = r(1-u)$, where $r \in (0,\infty)$ and $u \in (0,1)$. Note $s + t = r$.

    The Jacobian is:

    $$\frac{\partial(s,t)}{\partial(r,u)} = \begin{vmatrix} u & r \\ 1-u & -r \end{vmatrix} = -ru - r(1-u) = -r.$$

    Taking the absolute value: $|J| = r$. So $ds\,dt = r\,dr\,du$.

    Substituting:

    $$\begin{aligned}
    \Gamma(a)\Gamma(b) &= \int_0^1\!\!\int_0^\infty (ru)^{a-1}(r(1-u))^{b-1}e^{-r}\cdot r\,dr\,du \\
    &= \int_0^1 u^{a-1}(1-u)^{b-1}\,du \cdot \int_0^\infty r^{a+b-1}e^{-r}\,dr \\
    &= B(a,b) \cdot \Gamma(a+b).
    \end{aligned}$$

    Therefore $B(a,b) = \frac{\Gamma(a)\Gamma(b)}{\Gamma(a+b)}$.

    $\square$

---
