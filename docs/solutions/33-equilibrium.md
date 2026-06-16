<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 33: Equilibrium & Steady States

**Exercise 33.1.** Equilibria of $\dot{x} = x^2 - 4x + 3 = (x-1)(x-3)$.

??? success "Solution"

    Equilibria: $x^* = 1$ and $x^* = 3$.

    Derivative test: $f'(x) = 2x - 4$. $f'(1) = -2 < 0$: **stable**. $f'(3) = 2 > 0$: **unstable**.

    Phase line: For $x < 1$, $f(x) > 0$ (rightward flow); for $1 < x < 3$, $f(x) < 0$ (leftward flow toward 1); for $x > 3$, $f(x) > 0$ (rightward flow away from 3).

---

**Exercise 33.2.** Solow growth model.

??? success "Solution"

    $f(k) = k^{0.4}$, $s = 0.25$, $\delta = 0.10$. Steady state: $sf(k^*) = \delta k^*$, i.e., $0.25(k^*)^{0.4} = 0.10 k^*$.

    $(k^*)^{0.4}/(k^*) = 0.4$, so $(k^*)^{-0.6} = 0.4$, giving $k^* = 0.4^{-1/0.6} = 0.4^{-5/3}$.

    By F33.4: $k^* = (s/\delta)^{1/(1-\alpha)} = (0.25/0.10)^{1/0.6} = 2.5^{5/3}$. $0.4^{-5/3} = (2/5)^{-5/3} = (5/2)^{5/3} = 2.5^{5/3}$. $\ln(2.5) = 0.9163$, so $\ln(k^*) = 5/3 \times 0.9163 = 1.5272$, $k^* = e^{1.5272} = 4.605$.

    $y^* = (4.605)^{0.4} = e^{0.4 \times 1.5272} = e^{0.6109} = 1.842$.

    $c^* = (1-s)y^* = 0.75 \times 1.842 = 1.381$.

    Half-life of convergence: Linearising $\dot{k} = sf(k) - \delta k$ around $k^*$: $\dot{k} \approx [sf'(k^*) - \delta](k - k^*) = [0.25 \times 0.4 \times (k^*)^{-0.6} - 0.10](k-k^*)$. Since $(k^*)^{-0.6} = 0.4$, the coefficient is $0.25 \times 0.4 \times 0.4 - 0.10 = 0.04 - 0.10 = -0.06$.

    The convergence rate is $0.06$ per period. Half-life: $t_{1/2} = \ln 2/0.06 = 11.55$ periods.

---

**Exercise 33.3.** Chemical equilibrium: $\text{PCl}_5 \rightleftharpoons \text{PCl}_3 + \text{Cl}_2$.

??? success "Solution"

    ICE table with $x$ = extent of reaction:

    | | $\text{PCl}_5$ | $\text{PCl}_3$ | $\text{Cl}_2$ |
    |---|---|---|---|
    | Initial | 0.50 | 0 | 0 |
    | Change | $-x$ | $+x$ | $+x$ |
    | Equil. | $0.50-x$ | $x$ | $x$ |

    $K_c = [\text{PCl}_3][\text{Cl}_2]/[\text{PCl}_5] = x^2/(0.50-x) = 0.042$.

    $x^2 + 0.042x - 0.021 = 0$. $x = \frac{-0.042 + \sqrt{0.001764 + 0.084}}{2} = \frac{-0.042 + \sqrt{0.085764}}{2} = \frac{-0.042 + 0.2929}{2} = 0.1254$.

    Equilibrium concentrations: $[\text{PCl}_5] = 0.50 - 0.125 = 0.375$ mol/L, $[\text{PCl}_3] = [\text{Cl}_2] = 0.125$ mol/L.

    Check: $0.125^2/0.375 = 0.01563/0.375 = 0.0417 \approx 0.042$. $\checkmark$

---

**Exercise 33.4.** Two-species competition.

??? success "Solution"

    $\dot{x} = x(3-x-2y)$, $\dot{y} = y(2-x-y)$.

    Equilibria in the first quadrant:
    1. $(0, 0)$: trivial.
    2. $(3, 0)$: species 1 at carrying capacity, species 2 extinct.
    3. $(0, 2)$: species 2 at carrying capacity, species 1 extinct.
    4. Interior: $3-x-2y = 0$ and $2-x-y = 0$. From the second: $x = 2-y$. Substituting: $3-(2-y)-2y = 0 \Rightarrow 1-y = 0 \Rightarrow y = 1$. $x = 1$. So $(1, 1)$.

    Jacobian:

    $$J = \begin{bmatrix} 3-2x-2y & -2x \\ -y & 2-x-2y \end{bmatrix}.$$

    At $(0,0)$: $J = \operatorname{diag}(3, 2)$. Eigenvalues: 3, 2. **Unstable node.**

    At $(3,0)$: $J = \begin{bmatrix} -3 & -6 \\ 0 & -1 \end{bmatrix}$. Eigenvalues: $-3, -1$. **Stable node.**

    At $(0,2)$: $J = \begin{bmatrix} -1 & 0 \\ -2 & -2 \end{bmatrix}$. Eigenvalues: $-1, -2$. **Stable node.**

    At $(1,1)$: $J = \begin{bmatrix} -1 & -2 \\ -1 & -1 \end{bmatrix}$, $\operatorname{tr}(J) = -2$, $\det(J) = 1-2 = -1 < 0$. Eigenvalues: $(-2 \pm \sqrt{4+4})/2 = -1 \pm \sqrt{2}$. One positive, one negative. **Saddle point (unstable).**

    Ecological interpretation: The two species cannot coexist stably. The system is bistable: depending on initial conditions, either species 1 wins (trajectory to $(3,0)$) or species 2 wins (trajectory to $(0,2)$). The saddle at $(1,1)$ defines the separatrix between the basins of attraction.

---

**Exercise 33.5.** IS-LM equilibrium.

??? success "Solution"

    **IS curve** (goods market equilibrium, $C = 200 + 0.6(Y-T)$, $I = 150 - 30r$, $G = 200$, $T = 150$):

    $$Y = 200 + 0.6(Y - 150) + 150 - 30r + 200 = 460 + 0.6Y - 30r.$$

    $$0.4Y = 460 - 30r \implies Y = 1150 - 75r. \quad \text{(IS)}$$

    **LM curve** (money market equilibrium, $L = 0.4Y - 40r$, $M/P = 400$):

    $$0.4Y - 40r = 400 \implies Y = 1000 + 100r. \quad \text{(LM)}$$

    **Equilibrium**: Setting IS $=$ LM:

    $$1150 - 75r = 1000 + 100r \implies 150 = 175r \implies r^* = \frac{6}{7} \approx 0.857\%.$$

    $$Y^* = 1000 + 100 \cdot \frac{6}{7} = 1000 + \frac{600}{7} \approx 1085.7.$$

    **Fiscal multiplier**: With $G' = 250$ ($\Delta G = 50$), the new IS is $0.4Y = 510 - 30r$, so $Y = 1275 - 75r$.

    New equilibrium: $1275 - 75r = 1000 + 100r \implies 275 = 175r \implies r^{**} = \frac{11}{7} \approx 1.571\%$.

    $$Y^{**} = 1000 + 100 \cdot \frac{11}{7} = 1000 + \frac{1100}{7} \approx 1157.1.$$

    $$\Delta Y = Y^{**} - Y^* = \frac{1100 - 600}{7} = \frac{500}{7} \approx 71.4. \quad \frac{\Delta Y}{\Delta G} = \frac{500/7}{50} = \frac{10}{7} \approx 1.43.$$

    The IS-LM fiscal multiplier is smaller than the simple Keynesian multiplier $1/(1-c) = 2.5$ because higher income raises money demand, pushing up the interest rate and crowding out private investment.

    **Stability**: The tatonnement $\dot{Y} = \alpha(AD - Y)$, $\dot{r} = \beta(L - M/P)$ has Jacobian $\operatorname{tr}(J) < 0$ and $\det(J) > 0$, confirming both equilibria are stable nodes.

---

**Exercise 33.6.** Saddle-node bifurcation $\dot{x} = \mu + x^2$.

??? success "Solution"

    Equilibria: $x^2 + \mu = 0 \Rightarrow x = \pm\sqrt{-\mu}$.

    - For $\mu < 0$: two equilibria at $x = \pm\sqrt{-\mu}$. $f'(x) = 2x$: at $x = -\sqrt{-\mu}$, $f' = -2\sqrt{-\mu} < 0$ (**stable**); at $x = +\sqrt{-\mu}$, $f' = 2\sqrt{-\mu} > 0$ (**unstable**).
    - For $\mu = 0$: one equilibrium at $x = 0$ with $f'(0) = 0$ (half-stable).
    - For $\mu > 0$: no real equilibria. $\dot{x} = \mu + x^2 > 0$ for all $x$; trajectories escape to $+\infty$.

    The bifurcation occurs at $\mu = 0$, where the stable and unstable equilibria collide and annihilate. This is the **saddle-node bifurcation**.

---

**Exercise 33.7.** Three-good exchange economy.

??? success "Solution"

    $z_1(p) = 10 - 2p_1 + p_2 + p_3$, $z_2(p) = 5 + p_1 - 3p_2 + p_3$, $p_3 = 1$.

    Walrasian equilibrium: $z_1 = 0$ and $z_2 = 0$.

    $10 - 2p_1 + p_2 + 1 = 0 \Rightarrow -2p_1 + p_2 = -11$.
    $5 + p_1 - 3p_2 + 1 = 0 \Rightarrow p_1 - 3p_2 = -6$.

    From the second: $p_1 = 3p_2 - 6$. Substituting: $-2(3p_2 - 6) + p_2 = -11$. $-6p_2 + 12 + p_2 = -11$. $-5p_2 = -23$. $p_2 = 4.6$. $p_1 = 3(4.6) - 6 = 7.8$.

    Equilibrium prices: $(p_1^*, p_2^*, p_3) = (7.8, 4.6, 1)$.

    By Walras' law, $p_1 z_1 + p_2 z_2 + p_3 z_3 = 0$ holds identically. At equilibrium $z_1 = z_2 = 0$, so $p_3 z_3 = 0$. Since $p_3 = 1 \neq 0$, we have $z_3(p^*) = 0$. $\checkmark$

    Jacobian of tatonnement $\dot{p}_i = z_i(p)$:

    $$J = \begin{bmatrix} \partial z_1/\partial p_1 & \partial z_1/\partial p_2 \\ \partial z_2/\partial p_1 & \partial z_2/\partial p_2 \end{bmatrix} = \begin{bmatrix} -2 & 1 \\ 1 & -3 \end{bmatrix}.$$

    Eigenvalues: $\lambda^2 + 5\lambda + 5 = 0$. $\lambda = (-5 \pm \sqrt{25-20})/2 = (-5 \pm \sqrt{5})/2$. $\lambda_1 = (-5+2.236)/2 = -1.382$, $\lambda_2 = (-5-2.236)/2 = -3.618$.

    Both eigenvalues are negative: the equilibrium is a **stable node**. Tatonnement converges.

    $\square$

---

**Exercise 33.8.** Modified Lotka–Volterra with logistic prey.

??? success "Solution"

    $\dot{x} = x(1-x/K) - \beta xy$, $\dot{y} = \delta xy - \gamma y$.

    With $K=100$, $\beta=0.01$, $\delta=0.005$, $\gamma=0.4$.

    Equilibria: (i) $(0,0)$; (ii) $(K,0) = (100,0)$; (iii) Coexistence: $\delta x - \gamma = 0 \Rightarrow x^* = \gamma/\delta = 0.4/0.005 = 80$. $1 - x^*/K - \beta y^* = 0 \Rightarrow y^* = (1-80/100)/\beta = 0.2/0.01 = 20$.

    Coexistence equilibrium: $(80, 20)$.

    Jacobian:

    $$J = \begin{bmatrix} 1 - 2x/K - \beta y & -\beta x \\ \delta y & \delta x - \gamma \end{bmatrix}.$$

    At $(80, 20)$:

    $$J = \begin{bmatrix} 1 - 160/100 - 0.01 \times 20 & -0.01 \times 80 \\ 0.005 \times 20 & 0 \end{bmatrix} = \begin{bmatrix} 1 - 1.6 - 0.2 & -0.8 \\ 0.1 & 0 \end{bmatrix} = \begin{bmatrix} -0.8 & -0.8 \\ 0.1 & 0 \end{bmatrix}.$$

    $\operatorname{tr}(J) = -0.8 < 0$, $\det(J) = 0 - (-0.08) = 0.08 > 0$.

    Discriminant: $\Delta = (-0.8)^2 - 4(0.08) = 0.64 - 0.32 = 0.32 > 0$. The eigenvalues are real: $\lambda = (-0.8 \pm \sqrt{0.32})/2 = (-0.8 \pm 0.566)/2$. $\lambda_1 = -0.117$, $\lambda_2 = -0.683$. Both negative: **stable node** (not a spiral for these parameters).

    If $K$ were smaller (making the prey growth rate more influential), $\operatorname{tr}(J)$ would be smaller in magnitude and the discriminant could become negative, yielding a stable spiral. The physical reason logistic growth converts the centre into a stable equilibrium is that the density-dependent term $-x^2/K$ provides a restoring force absent in the pure Lotka–Volterra model: when prey are abundant, their growth rate diminishes, damping the oscillations that would otherwise persist forever.

---
