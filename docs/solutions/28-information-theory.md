<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 28: Information Theory

**Exercise 28.1.** Entropy of a fair six-sided die.

??? success "Solution"

    For $X$ uniform on $\{1,2,3,4,5,6\}$, $p(x) = 1/6$ for all $x$.

    $$H(X) = -\sum_{x=1}^{6} \frac{1}{6}\log_2\frac{1}{6} = -6 \cdot \frac{1}{6}\log_2\frac{1}{6} = -\log_2\frac{1}{6} = \log_2 6 \approx 2.585 \text{ bits}.$$

    $\square$

---

**Exercise 28.2.** Entropy and Huffman code for $P = (0.25, 0.25, 0.25, 0.125, 0.125)$.

??? success "Solution"

    $$\begin{aligned}
    H(X) &= -2(0.25\log_2 0.25) - 0.25\log_2 0.25 - 2(0.125\log_2 0.125) \\
         &= -3(0.25)(-2) - 2(0.125)(-3) = 1.5 + 0.75 = 2.25 \text{ bits.}
    \end{aligned}$$

    **Huffman code construction:**

    1. Merge the two smallest: $0.125 + 0.125 = 0.25$. Symbols: $\{0.25, 0.25, 0.25, 0.25\}$.
    2. Merge two: $0.25 + 0.25 = 0.50$. Symbols: $\{0.50, 0.25, 0.25\}$.
    3. Merge two: $0.25 + 0.25 = 0.50$. Symbols: $\{0.50, 0.50\}$.
    4. Merge: $0.50 + 0.50 = 1.0$.

    One valid code: $a_1 \to 00$, $a_2 \to 01$, $a_3 \to 10$, $a_4 \to 110$, $a_5 \to 111$.

    Expected code length: $L = 0.25(2) + 0.25(2) + 0.25(2) + 0.125(3) + 0.125(3) = 0.5 + 0.5 + 0.5 + 0.375 + 0.375 = 2.25$ bits.

    Check: $H(X) = 2.25 \leq L = 2.25 < H(X) + 1 = 3.25$. Satisfied, and in fact $L = H(X)$ exactly (the Huffman code achieves entropy because all probabilities are dyadic rationals). $\square$

---

**Exercise 28.3.** Joint distribution of two binary RVs.

??? success "Solution"

    Given: $p(0,0) = 0.4$, $p(0,1) = 0.1$, $p(1,0) = 0.2$, $p(1,1) = 0.3$.

    Marginals: $p_X(0) = 0.5$, $p_X(1) = 0.5$; $p_Y(0) = 0.6$, $p_Y(1) = 0.4$.

    $H(X) = -0.5\log_2 0.5 - 0.5\log_2 0.5 = 1.000$ bit.

    $H(Y) = -0.6\log_2 0.6 - 0.4\log_2 0.4 = 0.4422 + 0.5288 = 0.9710$ bits.

    $H(X,Y) = -0.4\log_2 0.4 - 0.1\log_2 0.1 - 0.2\log_2 0.2 - 0.3\log_2 0.3 = 0.5288 + 0.3322 + 0.4644 + 0.5211 = 1.8464$ bits.

    $H(Y \mid X) = H(X,Y) - H(X) = 1.8464 - 1.0000 = 0.8464$ bits.

    $I(X;Y) = H(Y) - H(Y \mid X) = 0.9710 - 0.8464 = 0.1246$ bits.

    **Chain rule verification:** $H(X) + H(Y \mid X) = 1.000 + 0.8464 = 1.8464 = H(X,Y)$. $\checkmark$

    $\square$

---

**Exercise 28.4.** Prove $H(Y \mid X) \leq H(Y)$ with equality iff $X \perp Y$.

??? success "Solution"

    By the definition of mutual information: $I(X;Y) = H(Y) - H(Y \mid X)$.

    By Theorem 28.9, $I(X;Y) \geq 0$. Therefore $H(Y) - H(Y \mid X) \geq 0$, which gives $H(Y \mid X) \leq H(Y)$.

    Equality holds iff $I(X;Y) = 0$, which by Theorem 28.9 holds iff $X$ and $Y$ are independent. $\square$

    Intuitively, conditioning on additional information cannot increase uncertainty on average. Knowing $X$ can only reduce (or maintain) the entropy of $Y$.

---

**Exercise 28.5.** KL divergence asymmetry and Jensen–Shannon divergence.

??? success "Solution"

    $P = (0.4, 0.3, 0.2, 0.1)$, $Q = (0.25, 0.25, 0.25, 0.25)$.

    $$D_{\mathrm{KL}}(P \| Q) = 0.4\log_2\frac{0.4}{0.25} + 0.3\log_2\frac{0.3}{0.25} + 0.2\log_2\frac{0.2}{0.25} + 0.1\log_2\frac{0.1}{0.25}$$

    $$= 0.4\log_2 1.6 + 0.3\log_2 1.2 + 0.2\log_2 0.8 + 0.1\log_2 0.4$$

    $$= 0.4(0.6781) + 0.3(0.2630) + 0.2(-0.3219) + 0.1(-1.3219)$$

    $$= 0.2712 + 0.0789 - 0.0644 - 0.1322 = 0.1536 \text{ bits}.$$

    $$D_{\mathrm{KL}}(Q \| P) = 0.25\log_2\frac{0.25}{0.4} + 0.25\log_2\frac{0.25}{0.3} + 0.25\log_2\frac{0.25}{0.2} + 0.25\log_2\frac{0.25}{0.1}$$

    $$= 0.25(-0.6781) + 0.25(-0.2630) + 0.25(0.3219) + 0.25(1.3219)$$

    $$= -0.1695 - 0.0658 + 0.0805 + 0.3305 = 0.1757 \text{ bits}.$$

    Indeed $D_{\mathrm{KL}}(P\|Q) = 0.1536 \neq 0.1757 = D_{\mathrm{KL}}(Q\|P)$, confirming asymmetry.

    $M = \frac{1}{2}(P+Q) = (0.325, 0.275, 0.225, 0.175)$.

    $$D_{\mathrm{KL}}(P\|M) = 0.4\log_2\frac{0.4}{0.325} + 0.3\log_2\frac{0.3}{0.275} + 0.2\log_2\frac{0.2}{0.225} + 0.1\log_2\frac{0.1}{0.175}$$

    $$= 0.4(0.2994) + 0.3(0.1253) + 0.2(-0.1699) + 0.1(-0.8074)$$

    $$= 0.1198 + 0.0376 - 0.0340 - 0.0807 = 0.0427 \text{ bits}.$$

    $$D_{\mathrm{KL}}(Q\|M) = 0.25\left[\log_2\frac{0.25}{0.325} + \log_2\frac{0.25}{0.275} + \log_2\frac{0.25}{0.225} + \log_2\frac{0.25}{0.175}\right]$$

    $$= 0.25[(-0.3785) + (-0.1375) + (0.1520) + (0.5146)]$$

    $$= 0.25 \times 0.1506 = 0.0377 \text{ bits}.$$

    $$\mathrm{JSD}(P,Q) = 0.5 \times 0.0427 + 0.5 \times 0.0377 = 0.0402 \text{ bits}.$$

    $\square$

---

**Exercise 28.6.** Cross-entropy for a classifier.

??? success "Solution"

    True label: class 1, so $P = (1, 0, 0)$. Model output: $Q = (0.7, 0.2, 0.1)$.

    $$H_Q(P) = -\sum_x p(x)\log_2 q(x) = -1 \cdot \log_2 0.7 - 0 \cdot \log_2 0.2 - 0 \cdot \log_2 0.1 = -\log_2 0.7 = 0.5146 \text{ bits}.$$

    Since $P$ is a one-hot vector with all mass on class 1, only the $q_1 = 0.7$ term survives, giving $H_Q(P) = -\log_2 q_1 = -\log_2 0.7$. $\square$

    Minimising cross-entropy over training examples minimises $\sum_{i=1}^N (-\log_2 q_\theta(y_i^* \mid x_i))$, which equals the negative log-likelihood of the model. Minimising the negative log-likelihood is by definition maximum likelihood estimation. The equivalence follows from Theorem 28.14: since $H(P)$ is constant with respect to $\theta$, $\min_\theta H_Q(P) = \min_\theta [H(P) + D_{\mathrm{KL}}(P\|Q_\theta)] = H(P) + \min_\theta D_{\mathrm{KL}}(P\|Q_\theta)$, so cross-entropy minimisation finds the model distribution closest to the empirical distribution in the KL sense.

---

**Exercise 28.7.** Capacity of the binary erasure channel (BEC).

??? success "Solution"

    The BEC has $p(y=x \mid x) = 1-\varepsilon$ and $p(y=e \mid x) = \varepsilon$ for $x \in \{0,1\}$. Let $p(X=0) = \pi$.

    $H(Y \mid X)$: Given $X=x$, the output is $x$ with probability $1-\varepsilon$ and $e$ with probability $\varepsilon$. $Y \mid X=x$ takes value $x$ with probability $1-\varepsilon$ and $e$ with probability $\varepsilon$, so $H(Y \mid X=x) = -\varepsilon\log_2\varepsilon - (1-\varepsilon)\log_2(1-\varepsilon) = H_b(\varepsilon)$ for both $x=0$ and $x=1$. Thus $H(Y \mid X) = H_b(\varepsilon)$.

    $H(Y)$: $Y$ takes values $\{0, 1, e\}$ with probabilities: $p(Y=0) = \pi(1-\varepsilon)$, $p(Y=1) = (1-\pi)(1-\varepsilon)$, $p(Y=e) = \varepsilon$.

    $$I(X;Y) = H(Y) - H(Y \mid X) = H(Y) - H_b(\varepsilon).$$

    To maximise $I(X;Y)$, $H(Y)$ is maximised. Write:

    $$H(Y) = -\pi(1-\varepsilon)\log_2[\pi(1-\varepsilon)] - (1-\pi)(1-\varepsilon)\log_2[(1-\pi)(1-\varepsilon)] - \varepsilon\log_2\varepsilon.$$

    The first two terms factor as $(1-\varepsilon)[-\pi\log_2\pi - (1-\pi)\log_2(1-\pi)] + (1-\varepsilon)[-\log_2(1-\varepsilon)]$, and the last term is $-\varepsilon\log_2\varepsilon$. Combining:

    $$H(Y) = (1-\varepsilon)H_b(\pi) + H_b(\varepsilon).$$

    Therefore: $I(X;Y) = (1-\varepsilon)H_b(\pi) + H_b(\varepsilon) - H_b(\varepsilon) = (1-\varepsilon)H_b(\pi)$.

    This is maximised when $H_b(\pi)$ is maximised, which occurs at $\pi = 1/2$ where $H_b(1/2) = 1$.

    $$C = (1-\varepsilon) \times 1 = 1 - \varepsilon.$$

    $\square$

---

**Exercise 28.8.** Maximum entropy distribution with known mean on non-negative integers.

??? success "Solution"

    The goal is to maximise $H(X) = -\sum_{k=0}^{\infty} p(k)\log p(k)$ subject to $\sum_{k=0}^{\infty} p(k) = 1$ and $\sum_{k=0}^{\infty} k \cdot p(k) = \mu$.

    Form the Lagrangian: $\mathcal{L} = -\sum_k p(k)\log p(k) - \lambda_0(\sum_k p(k) - 1) - \lambda_1(\sum_k k \cdot p(k) - \mu)$.

    Differentiating with respect to $p(k)$ and setting to zero: $-\log p(k) - 1 - \lambda_0 - \lambda_1 k = 0$.

    So $p(k) = \exp(-1-\lambda_0-\lambda_1 k) = C \cdot \theta^k$ where $C = e^{-1-\lambda_0}$ and $\theta = e^{-\lambda_1}$.

    Normalisation: $\sum_{k=0}^{\infty} C\theta^k = C/(1-\theta) = 1$, so $C = 1 - \theta$.

    Mean constraint: $\sum_{k=0}^{\infty} k(1-\theta)\theta^k = (1-\theta) \cdot \theta/(1-\theta)^2 = \theta/(1-\theta) = \mu$.

    Solving: $\theta = \mu/(1+\mu)$.

    This gives $p(k) = (1-\theta)\theta^k$, the geometric distribution.

    The entropy is:

    $$H(X) = -\sum_{k=0}^{\infty}(1-\theta)\theta^k[\log_2(1-\theta) + k\log_2\theta] = -\log_2(1-\theta) - \frac{\theta}{1-\theta}\log_2\theta.$$

    By the maximum entropy theorem, this exceeds the entropy of any other distribution on $\{0,1,2,\ldots\}$ with the same mean, because for any other such distribution $p$, $D_{\mathrm{KL}}(p\|p^*) \geq 0$ implies $H(p) \leq H(p^*)$. $\square$

---
