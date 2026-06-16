<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 25: Financial Mathematics

**Exercise 25.1.** Compute the future value of €5,000 invested at 4% annual interest for 10 years under (a) simple interest, (b) annual compounding, (c) monthly compounding, (d) continuous compounding.

??? success "Solution"

    **(a)** Simple interest:

    $$A = P(1 + rt) = 5000(1 + 0.04 \times 10) = 5000(1.40) = \text{€}7{,}000.00.$$

    **(b)** Annual compounding:

    $$A = P(1 + r)^t = 5000(1.04)^{10}.$$

    $(1.04)^{10} = 1.48024$, so $A = 5000 \times 1.48024 = \text{€}7{,}401.22$.

    **(c)** Monthly compounding:

    $$A = P(1 + r/n)^{nt} = 5000(1 + 0.04/12)^{120} = 5000(1.003333)^{120}.$$

    $(1.003333)^{120} = 1.49083$, so $A = 5000 \times 1.49083 = \text{€}7{,}454.16$.

    **(d)** Continuous compounding:

    $$A = Pe^{rt} = 5000 e^{0.04 \times 10} = 5000 e^{0.4}.$$

    Since $e^{0.4} = 1.49182$, $A = 5000 \times 1.49182 = \text{€}7{,}459.12$.

    $\square$

---

**Exercise 25.2.** A zero-coupon bond pays €1,000 at maturity in 7 years. If the market yield is 5.5% annually, what is the bond's price today?

??? success "Solution"

    A zero-coupon bond pays no coupons, so its price is the present value of the face value:

    $$PV = \frac{FV}{(1+y)^T} = \frac{1000}{(1.055)^7}.$$

    $(1.055)^7 = 1.45468$. Therefore:

    $$PV = \frac{1000}{1.45468} = \text{€}687.44.$$

    $\square$

---

**Exercise 25.3.** An ordinary annuity pays €500 per month for 5 years. The monthly discount rate is 0.5%. Compute the present value and future value.

??? success "Solution"

    Parameters: $C = 500$, $r = 0.005$, $T = 60$ months.

    **Present value:**

    $$PV = C \cdot \frac{1 - (1+r)^{-T}}{r} = 500 \cdot \frac{1 - (1.005)^{-60}}{0.005}.$$

    $(1.005)^{60} = 1.34885$, so $(1.005)^{-60} = 0.74137$.

    $$PV = 500 \cdot \frac{1 - 0.74137}{0.005} = 500 \cdot \frac{0.25863}{0.005} = 500 \times 51.7256 = \text{€}25{,}862.78.$$

    **Future value:**

    $$FV = C \cdot \frac{(1+r)^T - 1}{r} = 500 \cdot \frac{1.34885 - 1}{0.005} = 500 \cdot \frac{0.34885}{0.005} = 500 \times 69.7700 = \text{€}34{,}885.02.$$

    Verification: $FV = PV \times (1.005)^{60} = 25862.78 \times 1.34885 = 34885.02$. Confirmed.

    $\square$

---

**Exercise 25.4.** Compute the monthly payment on a €150,000 loan at 4.5% annual interest (compounded monthly) for 15 years. What fraction of the first payment is interest?

??? success "Solution"

    The monthly rate is $r = 0.045/12 = 0.00375$ and $T = 180$ payments.

    $$\text{PMT} = PV \cdot \frac{r}{1 - (1+r)^{-T}} = 150000 \cdot \frac{0.00375}{1 - (1.00375)^{-180}}.$$

    $(1.00375)^{180} = 1.96156$, so $(1.00375)^{-180} = 0.50980$.

    $$\text{PMT} = 150000 \cdot \frac{0.00375}{1 - 0.50980} = 150000 \cdot \frac{0.00375}{0.49020} = 150000 \times 0.007650 = \text{€}1{,}147.49.$$

    The interest portion of the first payment is $I_1 = 150000 \times 0.00375 = \text{€}562.50$.

    Fraction that is interest: $562.50 / 1147.49 = 0.4901 = 49.0\%$.

    $\square$

---

**Exercise 25.5.** A stock is expected to pay a dividend of €3.00 next year, growing at 4% per year indefinitely. If the required return is 9%, compute the stock price using the Gordon growth model. What happens to the price as $g \to r$? Interpret financially.

??? success "Solution"

    By the Gordon growth model (Definition 25.17):

    $$PV = \frac{C}{r - g} = \frac{3.00}{0.09 - 0.04} = \frac{3.00}{0.05} = \text{€}60.00.$$

    As $g \to r$, the denominator $r - g \to 0^+$, so $PV \to \infty$. The financial interpretation is that if dividends grow at a rate approaching the discount rate, the present value of the infinite stream of dividends becomes unbounded. Each future dividend, when discounted, shrinks less and less, so the sum diverges. In practice, a growth rate that equals or exceeds the discount rate indefinitely is unsustainable; the model's assumption of $r > g$ is an economic requirement, not just a mathematical one. A growth rate persistently at or above $r$ would imply the firm eventually commands infinite resources, which is impossible in a finite economy.

    $\square$

---

**Exercise 25.6.** A project has cash flows $[-200000, 80000, 80000, 80000, 80000]$. Compute the NPV at discount rates $r = 0.05, 0.10, 0.15, 0.20, 0.25$. At approximately what rate does NPV cross zero (the IRR)? Verify using Newton's method.

??? success "Solution"

    The NPV is

    $$\text{NPV}(r) = -200000 + 80000 \sum_{t=1}^{4} (1+r)^{-t} = -200000 + 80000 \cdot \frac{1-(1+r)^{-4}}{r}.$$

    | $r$ | PVIFA $= \frac{1-(1+r)^{-4}}{r}$ | NPV |
    |-----|-----------------------------------|-----|
    | 0.05 | 3.5460 | $-200000 + 283680 = +83{,}680$ |
    | 0.10 | 3.1699 | $-200000 + 253590 = +53{,}590$ |
    | 0.15 | 2.8550 | $-200000 + 228396 = +28{,}396$ |
    | 0.20 | 2.5887 | $-200000 + 207099 = +7{,}099$ |
    | 0.25 | 2.3616 | $-200000 + 188928 = -11{,}072$ |

    The NPV crosses zero between $r = 0.20$ and $r = 0.25$.

    **Newton's method** with initial guess $r_0 = 0.20$:

    At $r = 0.20$: $\text{NPV} = 7099$.

    $$\text{NPV}'(r) = \sum_{t=1}^{4} \frac{-t \cdot 80000}{(1+r)^{t+1}}.$$

    At $r = 0.20$:

    - $t=1$: $-80000/(1.20)^2 = -55556$
    - $t=2$: $-160000/(1.20)^3 = -92593$
    - $t=3$: $-240000/(1.20)^4 = -115741$
    - $t=4$: $-320000/(1.20)^5 = -128601$
    - Sum: $-392491$

    $$r_1 = 0.20 - \frac{7099}{-392491} = 0.20 + 0.01809 = 0.2181.$$

    At $r = 0.2181$: $\text{NPV} \approx 206.6$ (nearly zero).

    One more iteration gives $r^* \approx 0.2186$. The IRR is approximately $21.86\%$.

    $\square$

---

**Exercise 25.7.** Derive the formula for the present value of a growing annuity.

??? success "Solution"

    A growing annuity pays $C$ at $t=1$, $C(1+g)$ at $t=2$, ..., $C(1+g)^{T-1}$ at $t=T$. Its present value is:

    $$PV = \sum_{t=1}^{T} \frac{C(1+g)^{t-1}}{(1+r)^t} = \frac{C}{1+r} \sum_{t=0}^{T-1} \left(\frac{1+g}{1+r}\right)^t.$$

    Let $\rho = (1+g)/(1+r)$. Since $r > g$, $\rho < 1$. The sum is a finite geometric series:

    $$\sum_{t=0}^{T-1} \rho^t = \frac{1 - \rho^T}{1 - \rho}.$$

    Substituting $\rho = (1+g)/(1+r)$, the denominator becomes:

    $$1 - \rho = 1 - \frac{1+g}{1+r} = \frac{(1+r)-(1+g)}{1+r} = \frac{r-g}{1+r}.$$

    Therefore:

    $$PV = \frac{C}{1+r} \cdot \frac{1 - \left(\frac{1+g}{1+r}\right)^T}{\frac{r-g}{1+r}} = \frac{C}{r-g}\left[1 - \left(\frac{1+g}{1+r}\right)^T\right].$$

    This is the **growing annuity present value formula**. As $T \to \infty$, the term $\left(\frac{1+g}{1+r}\right)^T \to 0$, recovering the growing perpetuity formula $PV = C/(r-g)$. $\square$

---

**Exercise 25.8.** (a) Show that $[-100, 230, -132]$ has two IRRs. (b) Show that $[-1000, 3600, -4320, 1728]$ has a triple root at $r = 0.20$.

??? success "Solution"

    **(a)** The NPV equation is:

    $$-100 + \frac{230}{1+r} - \frac{132}{(1+r)^2} = 0.$$

    Let $x = 1/(1+r)$. Then:

    $$-100 + 230x - 132x^2 = 0 \quad \Longrightarrow \quad 132x^2 - 230x + 100 = 0.$$

    By the quadratic formula:

    $$x = \frac{230 \pm \sqrt{230^2 - 4(132)(100)}}{2(132)} = \frac{230 \pm \sqrt{52900 - 52800}}{264} = \frac{230 \pm \sqrt{100}}{264} = \frac{230 \pm 10}{264}.$$

    So $x_1 = 240/264 = 10/11$ and $x_2 = 220/264 = 5/6$.

    Since $x = 1/(1+r)$:

    - $x_1 = 10/11 \Rightarrow r_1 = 11/10 - 1 = 0.10 = 10\%$.
    - $x_2 = 5/6 \Rightarrow r_2 = 6/5 - 1 = 0.20 = 20\%$.

    Both are positive real solutions. The IRR criterion is ambiguous because the cash flows change sign twice (negative, positive, negative). The NPV is negative for $r < 10\%$, positive for $10\% < r < 20\%$, and negative again for $r > 20\%$. The correct decision rule is to use NPV at the investor's cost of capital, not the IRR.

    **(b)** The NPV equation with $x = 1/(1+r)$:

    $$-1000 + 3600x - 4320x^2 + 1728x^3 = 0.$$

    Dividing by $-8$:

    $$125 - 450x + 540x^2 - 216x^3 = 0,$$

    equivalently $216x^3 - 540x^2 + 450x - 125 = 0$.

    We check whether this factors as $(6x - 5)^3$:

    $$(6x - 5)^3 = 216x^3 - 3(36)(5)x^2 + 3(6)(25)x - 125 = 216x^3 - 540x^2 + 450x - 125.$$

    This matches exactly. Therefore the equation is $8(6x-5)^3 = 0$. The unique root is $x = 5/6$, giving $r = 1/5 = 0.20$ with algebraic multiplicity three.

    A triple root means the NPV curve touches zero at $r = 0.20$ without crossing it: $\text{NPV}(r) \leq 0$ for all $r$ (it is a cubic in $x$ that is a perfect cube). Both $\text{NPV}'(0.20) = 0$ and $\text{NPV}''(0.20) = 0$. The NPV curve is tangent to the horizontal axis, and Newton's method will exhibit cubic convergence to this root (rather than the usual quadratic).

    $\square$

---
