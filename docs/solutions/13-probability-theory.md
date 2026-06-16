<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 13: Probability Theory

**Exercise 13.1.** A fair coin is flipped three times. Let $A$ = "at least two heads" and $B$ = "the first flip is heads." (a) Compute $P(A)$, $P(B)$, and $P(A \cap B)$. (b) Are $A$ and $B$ independent? (c) Compute $P(A \mid B)$.

??? success "Solution"

    The sample space is $\Omega = \{HHH, HHT, HTH, HTT, THH, THT, TTH, TTT\}$, each with probability $1/8$.

    (a) $A = \{HHH, HHT, HTH, THH\}$, so $P(A) = 4/8 = 1/2$.

    $B = \{HHH, HHT, HTH, HTT\}$, so $P(B) = 4/8 = 1/2$.

    $A \cap B = \{HHH, HHT, HTH\}$, so $P(A \cap B) = 3/8$.

    (b) Independence requires $P(A \cap B) = P(A) \cdot P(B)$. Here $P(A) \cdot P(B) = (1/2)(1/2) = 1/4$, but $P(A \cap B) = 3/8 \neq 1/4$. Therefore $A$ and $B$ are **not independent**.

    (c) $P(A \mid B) = \frac{P(A \cap B)}{P(B)} = \frac{3/8}{1/2} = \frac{3}{4}$.

    This accords with probabilistic intuition: knowing the first flip is heads makes it easier to reach "at least two heads," so the conditional probability exceeds the unconditional $P(A) = 1/2$.

    $\square$

---

**Exercise 13.2.** A box contains 5 red balls and 3 blue balls. Two balls are drawn without replacement. Let $X$ be the number of red balls drawn. Find the PMF of $X$, compute $\mathbb{E}[X]$ and $\operatorname{Var}(X)$.

??? success "Solution"

    $X$ follows a hypergeometric distribution with population size $N = 8$, number of success states $K = 5$ and draws $n = 2$. The PMF is:

    $$P(X = k) = \frac{\binom{5}{k}\binom{3}{2-k}}{\binom{8}{2}}, \quad k = 0, 1, 2.$$

    We have $\binom{8}{2} = 28$.

    $P(X = 0) = \frac{\binom{5}{0}\binom{3}{2}}{\binom{8}{2}} = \frac{1 \cdot 3}{28} = \frac{3}{28}$

    $P(X = 1) = \frac{\binom{5}{1}\binom{3}{1}}{\binom{8}{2}} = \frac{5 \cdot 3}{28} = \frac{15}{28}$

    $P(X = 2) = \frac{\binom{5}{2}\binom{3}{0}}{\binom{8}{2}} = \frac{10 \cdot 1}{28} = \frac{10}{28} = \frac{5}{14}$

    Verification: $3/28 + 15/28 + 10/28 = 28/28 = 1$. $\checkmark$

    $\mathbb{E}[X] = 0 \cdot \frac{3}{28} + 1 \cdot \frac{15}{28} + 2 \cdot \frac{10}{28} = \frac{0 + 15 + 20}{28} = \frac{35}{28} = \frac{5}{4}$.

    (This agrees with the hypergeometric mean formula $\mathbb{E}[X] = nK/N = 2 \cdot 5/8 = 5/4$.)

    $\mathbb{E}[X^2] = 0 \cdot \frac{3}{28} + 1 \cdot \frac{15}{28} + 4 \cdot \frac{10}{28} = \frac{55}{28}$.

    $\operatorname{Var}(X) = \mathbb{E}[X^2] - (\mathbb{E}[X])^2 = \frac{55}{28} - \frac{25}{16} = \frac{220 - 175}{112} = \frac{45}{112}$.

    (Using the hypergeometric variance formula: $\operatorname{Var}(X) = n \frac{K}{N}\frac{N-K}{N}\frac{N-n}{N-1} = 2 \cdot \frac{5}{8} \cdot \frac{3}{8} \cdot \frac{6}{7} = \frac{180}{448} = \frac{45}{112}$.) $\checkmark$

    $\square$

---

**Exercise 13.3.** Let $X_1, \ldots, X_{100}$ be iid with $\mu = 50$ and $\sigma = 10$. Using the CLT, approximate $P(\bar{X}_{100} > 52)$. Using Chebyshev's inequality, find an upper bound for $P(|\bar{X}_{100} - 50| \geq 2)$ and compare.

??? success "Solution"

    We have $\mathbb{E}[\bar{X}_{100}] = \mu = 50$ and $\operatorname{Var}(\bar{X}_{100}) = \sigma^2/n = 100/100 = 1$, so $\text{SD}(\bar{X}_{100}) = 1$.

    **CLT approximation:** By the CLT, $\bar{X}_{100} \approx N(50, 1)$. Thus:

    $$P(\bar{X}_{100} > 52) = P\!\left(\frac{\bar{X}_{100} - 50}{1} > 2\right) \approx P(Z > 2) = 1 - \Phi(2) \approx 1 - 0.9772 = 0.0228.$$

    **Chebyshev's inequality:** For any random variable with finite mean and variance:

    $$P(|\bar{X}_{100} - 50| \geq 2) \leq \frac{\operatorname{Var}(\bar{X}_{100})}{2^2} = \frac{1}{4} = 0.25.$$

    **Comparison:** The CLT gives $P(|\bar{X}_{100} - 50| \geq 2) \approx 2 \times 0.0228 = 0.0456$. Chebyshev's bound of $0.25$ is valid but much looser (roughly 5.5 times larger). This illustrates that Chebyshev's inequality is distribution-free but conservative, while the CLT gives a much tighter approximation by exploiting the near-normality of the sample mean for large $n$.

    $\square$

---

**Exercise 13.4.** Let $X$ be a continuous random variable with PDF $f(x) = 2x$ for $0 \leq x \leq 1$ and $f(x) = 0$ otherwise. (a) Verify that $\int f(x)\,dx = 1$. (b) Compute the CDF $F(x)$. (c) Compute $\mathbb{E}[X]$ and $\operatorname{Var}(X)$.

??? success "Solution"

    (a) $\int_{-\infty}^{\infty} f(x)\,dx = \int_0^1 2x\,dx = [x^2]_0^1 = 1$. $\checkmark$

    (b) For $x < 0$: $F(x) = 0$. For $0 \leq x \leq 1$: $F(x) = \int_0^x 2t\,dt = [t^2]_0^x = x^2$. For $x > 1$: $F(x) = 1$.

    $$F(x) = \begin{cases} 0 & x < 0 \\ x^2 & 0 \leq x \leq 1 \\ 1 & x > 1 \end{cases}$$

    (c) $\mathbb{E}[X] = \int_0^1 x \cdot 2x\,dx = \int_0^1 2x^2\,dx = \left[\frac{2x^3}{3}\right]_0^1 = \frac{2}{3}$.

    $\mathbb{E}[X^2] = \int_0^1 x^2 \cdot 2x\,dx = \int_0^1 2x^3\,dx = \left[\frac{x^4}{2}\right]_0^1 = \frac{1}{2}$.

    $\operatorname{Var}(X) = \mathbb{E}[X^2] - (\mathbb{E}[X])^2 = \frac{1}{2} - \frac{4}{9} = \frac{9 - 8}{18} = \frac{1}{18}$.

    $\square$

---

**Exercise 13.5.** (Bayes' theorem application.) Three machines produce items. Machine A produces 50% of output with 2% defect rate; Machine B produces 30% with 3% defect rate; Machine C produces 20% with 5% defect rate. An item is selected at random and found to be defective. What is the probability it was produced by each machine?

??? success "Solution"

    Let $D$ = "item is defective." The prior probabilities and likelihoods are:

    | Machine | $P(M)$ | $P(D \mid M)$ | $P(M) \cdot P(D \mid M)$ |
    |---------|---------|----------------|---------------------------|
    | A       | 0.50    | 0.02           | 0.010                     |
    | B       | 0.30    | 0.03           | 0.009                     |
    | C       | 0.20    | 0.05           | 0.010                     |

    Total probability of a defect: $P(D) = 0.010 + 0.009 + 0.010 = 0.029$.

    By Bayes' theorem:

    $P(A \mid D) = \frac{0.010}{0.029} = \frac{10}{29} \approx 0.3448$

    $P(B \mid D) = \frac{0.009}{0.029} = \frac{9}{29} \approx 0.3103$

    $P(C \mid D) = \frac{0.010}{0.029} = \frac{10}{29} \approx 0.3448$

    Verification: $10/29 + 9/29 + 10/29 = 29/29 = 1$. $\checkmark$

    Despite Machine A producing the most items, its low defect rate means it is equally likely as Machine C (which produces fewer items but with a higher defect rate) to have produced a defective item.

    $\square$

---

**Exercise 13.6.** Let $X$ and $Y$ be jointly distributed with $\mathbb{E}[X] = 3$, $\mathbb{E}[Y] = 5$, $\operatorname{Var}(X) = 4$, $\operatorname{Var}(Y) = 9$, and $\operatorname{Cov}(X, Y) = -2$. Compute $\mathbb{E}[2X - 3Y + 7]$ and $\operatorname{Var}(2X - 3Y + 7)$.

??? success "Solution"

    By linearity of expectation:

    $\mathbb{E}[2X - 3Y + 7] = 2\mathbb{E}[X] - 3\mathbb{E}[Y] + 7 = 2(3) - 3(5) + 7 = 6 - 15 + 7 = -2$.

    For the variance, constants do not contribute, and:

    $$\begin{aligned}
    \operatorname{Var}(2X - 3Y + 7) &= \operatorname{Var}(2X - 3Y) = 4\operatorname{Var}(X) + 9\operatorname{Var}(Y) + 2(2)(-3)\operatorname{Cov}(X, Y) \\
    &= 4(4) + 9(9) + (-12)(-2) = 16 + 81 + 24 = 121.
    \end{aligned}$$

    Using the general formula $\operatorname{Var}(aX + bY) = a^2\operatorname{Var}(X) + b^2\operatorname{Var}(Y) + 2ab\operatorname{Cov}(X,Y)$ with $a = 2$ and $b = -3$.

    $\square$

---

**Exercise 13.7.** Prove that if $X$ and $Y$ are independent random variables with finite variances, then $\operatorname{Cov}(X, Y) = 0$. Give an example showing that the converse is false.

??? success "Solution"

    **Proof.** By definition, $\operatorname{Cov}(X, Y) = \mathbb{E}[XY] - \mathbb{E}[X]\mathbb{E}[Y]$. If $X$ and $Y$ are independent, then $\mathbb{E}[XY] = \mathbb{E}[X]\mathbb{E}[Y]$ (this follows from the factorisation of the joint density/PMF into the product of marginals). Therefore $\operatorname{Cov}(X, Y) = \mathbb{E}[X]\mathbb{E}[Y] - \mathbb{E}[X]\mathbb{E}[Y] = 0$.

    $\square$

    **Counterexample (converse is false).** Let $X \sim \mathrm{Uniform}(-1, 1)$ and $Y = X^2$. Then $Y$ is completely determined by $X$, so $X$ and $Y$ are clearly not independent. However:

    $\mathbb{E}[X] = 0$ (by symmetry).

    $\mathbb{E}[XY] = \mathbb{E}[X \cdot X^2] = \mathbb{E}[X^3] = \int_{-1}^{1} \frac{x^3}{2}\,dx = 0$ (odd function on symmetric interval).

    Therefore $\operatorname{Cov}(X, Y) = \mathbb{E}[XY] - \mathbb{E}[X]\mathbb{E}[Y] = 0 - 0 \cdot \mathbb{E}[Y] = 0$.

    So $\operatorname{Cov}(X, Y) = 0$ but $X$ and $Y$ are dependent. (This is Example 13.37 in the domain chapter.)

    $\square$

---

**Exercise 13.8.** Prove the general inclusion-exclusion formula.

??? success "Solution"

    We prove by induction on $n$ that for events $A_1, \ldots, A_n$:

    $$P\!\left(\bigcup_{i=1}^{n} A_i\right) = \sum_{k=1}^{n} (-1)^{k+1} \sum_{1 \le i_1 < \cdots < i_k \le n} P(A_{i_1} \cap \cdots \cap A_{i_k}).$$

    **Base case ($n = 1$):** $P(A_1) = P(A_1)$. $\checkmark$

    **Base case ($n = 2$):** This is the standard identity $P(A_1 \cup A_2) = P(A_1) + P(A_2) - P(A_1 \cap A_2)$, which follows from the additivity axiom applied to the disjoint decomposition $A_1 \cup A_2 = A_1 \cup (A_2 \setminus A_1)$. $\checkmark$

    **Inductive step:** Assume the formula holds for $n-1$ events. Write $\bigcup_{i=1}^{n} A_i = \left(\bigcup_{i=1}^{n-1} A_i\right) \cup A_n$. By the $n = 2$ case:

    $$P\!\left(\bigcup_{i=1}^{n} A_i\right) = P\!\left(\bigcup_{i=1}^{n-1} A_i\right) + P(A_n) - P\!\left(\left(\bigcup_{i=1}^{n-1} A_i\right) \cap A_n\right).$$

    Now $\left(\bigcup_{i=1}^{n-1} A_i\right) \cap A_n = \bigcup_{i=1}^{n-1} (A_i \cap A_n)$. Apply the induction hypothesis to both $\bigcup_{i=1}^{n-1} A_i$ (a union of $n-1$ events) and $\bigcup_{i=1}^{n-1}(A_i \cap A_n)$ (also a union of $n-1$ events). Substituting:

    $$\begin{aligned}
    P\!\left(\bigcup_{i=1}^{n-1} A_i\right) &= \sum_{k=1}^{n-1}(-1)^{k+1}\sum_{\substack{I \subseteq \{1,\ldots,n-1\} \\ |I|=k}} P\!\left(\bigcap_{i \in I} A_i\right), \\
    P\!\left(\bigcup_{i=1}^{n-1}(A_i \cap A_n)\right) &= \sum_{k=1}^{n-1}(-1)^{k+1}\sum_{\substack{I \subseteq \{1,\ldots,n-1\} \\ |I|=k}} P\!\left(\bigcap_{i \in I} A_i \cap A_n\right).
    \end{aligned}$$

    Combining: the first sum gives all terms not involving $A_n$; $P(A_n)$ is the singleton term involving $A_n$; and the subtracted sum, after the sign change, gives all terms involving $A_n$ and at least one other event. Each subset $J \subseteq \{1, \ldots, n\}$ with $|J| = k$ either does not contain $n$ (contributing from the first sum with sign $(-1)^{k+1}$) or does contain $n$ (contributing from $P(A_n)$ if $|J|=1$, or from the third term if $|J| \geq 2$, in each case with sign $(-1)^{k+1}$). This yields the inclusion-exclusion formula for $n$ events.

    $\square$

---
