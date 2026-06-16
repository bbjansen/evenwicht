<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 34: Chemical Kinetics & Reaction Networks

**Exercise 34.1.** First-order decomposition of $\text{N}_2\text{O}_5$.

??? success "Solution"

    $k = 6.2 \times 10^{-4}$ s$^{-1}$.

    **(a)** $t_{1/2} = \ln 2/k = 0.6931/(6.2 \times 10^{-4}) = 1118$ s $\approx 18.6$ min.

    **(b)** $[A](1000) = 0.50 \times e^{-6.2 \times 10^{-4} \times 1000} = 0.50 \times e^{-0.62} = 0.50 \times 0.5379 = 0.269$ mol/L.

    **(c)** 90% decomposed means 10% remains: $0.10 = e^{-kt}$, so $t = \ln(10)/k = 2.3026/(6.2\times10^{-4}) = 3714$ s $\approx 61.9$ min.

---

**Exercise 34.2.** Second-order reaction $2A \to$ products.

??? success "Solution"

    $k = 0.015$ L mol$^{-1}$ s$^{-1}$, $[A]_0 = 2.0$ mol/L.

    **(a)** $t_{1/2} = 1/(k[A]_0) = 1/(0.015 \times 2.0) = 33.3$ s.

    **(b)** $1/[A] = 1/[A]_0 + kt$. $1/[A](100) = 1/2.0 + 0.015 \times 100 = 0.5 + 1.5 = 2.0$. $[A](100) = 0.50$ mol/L.

    **(c)** 10% remains: $[A] = 0.20$ mol/L. $1/0.20 = 1/2.0 + 0.015t$. $5.0 = 0.5 + 0.015t$. $t = 4.5/0.015 = 300$ s.

---

**Exercise 34.3.** Arrhenius activation energy.

??? success "Solution"

    Two-temperature form: $\ln(k_2/k_1) = \frac{E_a}{R}\left(\frac{1}{T_1} - \frac{1}{T_2}\right)$.

    $\ln(0.543/0.111) = \ln(4.892) = 1.5873$.

    $1/T_1 - 1/T_2 = 1/298 - 1/318 = (318-298)/(298 \times 318) = 20/94764 = 2.1104 \times 10^{-4}$ K$^{-1}$.

    $E_a = R \times 1.5873/(2.1104 \times 10^{-4}) = 8.314 \times 7522.2 = 62{,}530$ J/mol $= 62.5$ kJ/mol.

---

**Exercise 34.4.** Michaelis–Menten kinetics.

??? success "Solution"

    $V_{\max} = 100$ $\mu$mol/L/min, $K_m = 2.5$ mmol/L.

    **(a)** At $[S] = 1.0$ mmol/L: $v = V_{\max}[S]/(K_m + [S]) = 100 \times 1.0/(2.5+1.0) = 100/3.5 = 28.6$ $\mu$mol/L/min.

    **(b)** $v = 0.80 V_{\max}$: $0.80 = [S]/(K_m + [S])$. $0.80 K_m + 0.80[S] = [S]$. $0.20[S] = 0.80 K_m$. $[S] = 4K_m = 10.0$ mmol/L.

    **(c)** At $[S] = 10K_m = 25$ mmol/L: $v/V_{\max} = 25/(2.5+25) = 25/27.5 = 0.909 = 90.9\%$.

---

**Exercise 34.5.** Sequential reaction $A \to B \to C$.

??? success "Solution"

    $k_1 = 0.10$ s$^{-1}$, $k_2 = 0.02$ s$^{-1}$, $[A]_0 = 0.50$ mol/L.

    **(a)** $t_{\max} = \frac{\ln(k_1/k_2)}{k_1 - k_2} = \frac{\ln(0.10/0.02)}{0.10 - 0.02} = \frac{\ln 5}{0.08} = \frac{1.6094}{0.08} = 20.12$ s.

    **(b)** $[B]_{\max} = [A]_0 \frac{k_1}{k_2}\left(\frac{k_2}{k_1}\right)^{k_1/(k_1-k_2)} = [A]_0 \left(\frac{k_2}{k_1}\right)^{k_2/(k_1-k_2)}$.

    $= 0.50 \times (0.02/0.10)^{0.02/0.08} = 0.50 \times 0.2^{0.25} = 0.50 \times 0.6687 = 0.334$ mol/L.

    **(c)** When $k_1 \gg k_2$: $A$ converts to $B$ almost instantly. $t_{\max} \approx \ln(k_1/k_2)/k_1 \to 0$, but $[B]_{\max} \to [A]_0(k_2/k_1)^{k_2/k_1} \to [A]_0$ as $k_2/k_1 \to 0$. The intermediate accumulates to the full initial concentration.

    **(d)** When $k_2 \gg k_1$: $t_{\max} \to 0$ and $[B]_{\max} \to [A]_0(k_2/k_1)^{-k_2/k_1 \cdot (k_1/k_2)} \to 0$. The intermediate is consumed as fast as it is formed. This is the quasi-steady-state regime where $d[B]/dt \approx 0$ and $[B] \approx k_1[A]/k_2 \ll [A]$.

    $\square$

---

**Exercise 34.6.** Reversible reaction.

??? success "Solution"

    **(a)** $d[A]/dt = -k_1[A] + k_{-1}[B] = -k_1[A] + k_{-1}([A]_0 - [A]) = -(k_1+k_{-1})[A] + k_{-1}[A]_0$.

    **(b)** At equilibrium, $d[A]/dt = 0$: $[A]_{\text{eq}} = k_{-1}[A]_0/(k_1+k_{-1})$.

    With $k_1 = 0.03$, $k_{-1} = 0.01$: $[A]_{\text{eq}} = 0.01 \times [A]_0/0.04 = 0.25[A]_0$.

    **(c)** The ODE is linear first-order: $d[A]/dt = -(k_1+k_{-1})([A] - [A]_{\text{eq}})$.

    Solution: $[A](t) - [A]_{\text{eq}} = ([A]_0 - [A]_{\text{eq}})e^{-(k_1+k_{-1})t}$.

    So $[A](t) = [A]_{\text{eq}} + 0.75[A]_0 e^{-0.04t}$, approaching $[A]_{\text{eq}}$ exponentially with rate constant $k_1 + k_{-1} = 0.04$ s$^{-1}$.

    $\square$

---

**Exercise 34.7.** Stoichiometry matrix.

??? success "Solution"

    Species: $\{A, B, C, D, E\}$. Reactions: (1) $A+B \to C$, (2) $C \to D+E$, (3) $D \to A$.

    $$N = \begin{bmatrix} -1 & 0 & 1 \\ -1 & 0 & 0 \\ 1 & -1 & 0 \\ 0 & 1 & -1 \\ 0 & 1 & 0 \end{bmatrix}.$$

    Rank of $N$: The $3 \times 3$ submatrix from rows $\{A, C, D\}$ has determinant $\begin{vmatrix} -1 & 0 & 1 \\ 1 & -1 & 0 \\ 0 & 1 & -1 \end{vmatrix} = -1(1-0) - 0 + 1(1-0) = -1+1 = 0$. Try another: rows $\{A, B, C\}$: $\begin{vmatrix}-1&0&1\\-1&0&0\\1&-1&0\end{vmatrix} = -1(0)-0+1(1) = 1 \neq 0$. Rank = 3.

    Number of species = 5, rank = 3, so there are $5 - 3 = 2$ conservation laws.

    Conservation law 1: $[A] + [C] + [D] = \text{const}$ (atom of type "A" is recycled through reactions 1, 2, 3).

    Conservation law 2: $[B] + [C] + [E] = \text{const}$ (the "B" atom enters via reaction 1, transfers to $C$, then to $E$).

    Verification: $N^T(1,0,1,1,0)^T = (-1-0+1+0+0,\; 0-0-1+1+1,\; 1+0+0-1+0)^T = (0,0,0)^T$. $\checkmark$

    $N^T(0,1,1,0,1)^T = (0-1+1+0+0,\; 0+0-1+0+1,\; 0+0+0+0+0)^T = (0,0,0)^T$. $\checkmark$

    Physically, conservation law 1 tracks the total pool of species containing the "A-atom," and conservation law 2 tracks the "B-atom" pool.

    $\square$

---

**Exercise 34.8.** Brusselator.

??? success "Solution"

    **(a)** Equilibrium: $a - (b+1)x + x^2y = 0$ and $bx - x^2y = 0$. From the second: $y = b/x$. Substituting: $a - (b+1)x + x^2(b/x) = a - (b+1)x + bx = a - x = 0$. So $x^* = a$, $y^* = b/a$.

    **(b)** $J = \begin{bmatrix} -(b+1) + 2xy & x^2 \\ b - 2xy & -x^2 \end{bmatrix}$. At $(a, b/a)$: $J = \begin{bmatrix} b-1 & a^2 \\ -b & -a^2 \end{bmatrix}$.

    **(c)** $\operatorname{tr}(J) = (b-1) + (-a^2) = b - 1 - a^2$. $\det(J) = (b-1)(-a^2) - a^2(-b) = -a^2(b-1) + a^2 b = a^2$.

    **(d)** Hopf bifurcation: $\operatorname{tr}(J) = 0$ with $\det(J) > 0$. $b - 1 - a^2 = 0 \Rightarrow b_c = 1 + a^2$. Since $\det(J) = a^2 > 0$ for $a > 0$, the eigenvalues at $b = b_c$ are $\lambda = \pm i\sqrt{a^2} = \pm ia$ (purely imaginary).

    **(e)** For $a = 1$, $b = 3$: $b_c = 1 + 1 = 2 < 3$, so the system is above the bifurcation. $\operatorname{tr}(J) = 3 - 1 - 1 = 1 > 0$: the equilibrium is unstable (eigenvalues have positive real part). Numerical simulation from $(1.5, 1.5)$ shows the trajectory spiraling outward from the equilibrium and converging to a stable limit cycle, confirming sustained chemical oscillations.

---
