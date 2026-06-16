<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 36: Game Theory

**Exercise 36.1.** Dominant strategies and pure Nash equilibria.

??? success "Solution"

    $A = \begin{pmatrix} 2 & 0 \\ 3 & 1 \end{pmatrix}$, $B = \begin{pmatrix} 1 & 3 \\ 0 & 2 \end{pmatrix}$.

    **(a)** Player 1 (rows): Row 2 gives $3 > 2$ (col 1) and $1 > 0$ (col 2). Row 2 strictly dominates Row 1. Player 1 has a dominant strategy: Row 2.

    Player 2 (columns): Given player 1 plays Row 2, player 2's payoffs are $B_{21} = 0$ vs $B_{22} = 2$. Col 2 is better. But checking dominance: Col 1 gives $(1, 0)$ vs Col 2 gives $(3, 2)$. Col 2 dominates Col 1 for player 2 ($3 > 1$ and $2 > 0$). Player 2 has a dominant strategy: Col 2.

    **(b)** Best responses: Player 1's BR to Col 1 is Row 2 ($3>2$); BR to Col 2 is Row 2 ($1>0$). Player 2's BR to Row 1 is Col 2 ($3>1$); BR to Row 2 is Col 2 ($2>0$).

    Pure NE: (Row 2, Col 2) with payoffs $(A_{22}, B_{22}) = (1, 2)$. This is the unique Nash equilibrium.

---

**Exercise 36.2.** Matching Pennies.

??? success "Solution"

    $A = \begin{pmatrix} 1 & -1 \\ -1 & 1 \end{pmatrix}$ (player 1's payoff; zero-sum so $B = -A$).

    **(a)** Checking all pure strategy profiles: $(H,H)$: player 2 deviates to $T$. $(H,T)$: player 1 deviates to $T$. $(T,H)$: player 1 deviates to $H$. $(T,T)$: player 2 deviates to $H$. No pure NE exists. $\checkmark$

    **(b)** Let player 1 play $H$ with probability $p$. Player 2's expected payoff from $H$: $-p + (1-p) = 1-2p$. From $T$: $p - (1-p) = 2p-1$. For indifference: $1-2p = 2p-1$, giving $p = 1/2$.

    Similarly, player 2 plays $H$ with probability $q = 1/2$.

    Mixed NE: both players randomise uniformly, $(p,q) = (1/2, 1/2)$.

    **(c)** Value of the game: $V = p(qA_{11} + (1-q)A_{12}) + (1-p)(qA_{21}+(1-q)A_{22}) = 1/2(1/2-1/2)+1/2(-1/2+1/2) = 0$. The value is $0$.

---

**Exercise 36.3.** Iterated elimination of dominated strategies.

??? success "Solution"

    $A = \begin{pmatrix} 3 & 2 & 1 \\ 4 & 3 & 5 \\ 1 & 0 & 2 \end{pmatrix}$, $B = \begin{pmatrix} 2 & 3 & 1 \\ 1 & 2 & 0 \\ 3 & 4 & 2 \end{pmatrix}$.

    **Step 1:** Does Row 3 have a dominated strategy for player 1? Row 3 payoffs: $(1,0,2)$. Row 2 payoffs: $(4,3,5)$. Row 2 dominates Row 3 ($4>1$, $3>0$, $5>2$). Eliminate Row 3.

    Remaining: Rows 1,2. $A' = \begin{pmatrix}3&2&1\\4&3&5\end{pmatrix}$, $B' = \begin{pmatrix}2&3&1\\1&2&0\end{pmatrix}$.

    **Step 2:** For player 2, Col 3 payoffs: $(1,0)$. Col 2 payoffs: $(3,2)$. Col 2 dominates Col 3 ($3>1$, $2>0$). Eliminate Col 3.

    Remaining: $A'' = \begin{pmatrix}3&2\\4&3\end{pmatrix}$, $B'' = \begin{pmatrix}2&3\\1&2\end{pmatrix}$.

    **Step 3:** For player 1: Row 2 dominates Row 1 ($4>3$, $3>2$). Eliminate Row 1.

    Remaining: Row 2. $A''' = (4\ 3)$, $B''' = (1\ 2)$.

    **Step 4:** Player 2 chooses Col 2 ($2 > 1$).

    Surviving profile: **(Row 2, Col 2)** with payoffs $(3, 2)$. The outcome is unique.

    $\square$

---

**Exercise 36.4.** Hawk–Dove game.

??? success "Solution"

    $A = \begin{pmatrix} -1 & 2 \\ 0 & 1 \end{pmatrix}$ with $V=2$, $C=4$.

    **(a) Pure NE:** Best responses: BR$_1$(Hawk) = Dove ($0 > -1$); BR$_1$(Dove) = Hawk ($2 > 1$). BR$_2$(Hawk) = Dove; BR$_2$(Dove) = Hawk (by symmetry of the game).

    Pure NE: (Hawk, Dove) and (Dove, Hawk), with payoffs $(2,0)$ and $(0,2)$ respectively.

    **Mixed NE:** Let $x$ be the probability of Hawk. Indifference: $-x + 2(1-x) = 0 \cdot x + 1 \cdot (1-x)$. $2-3x = 1-x$. $1 = 2x$. $x = 1/2$. Mixed NE: $(1/2, 1/2)$, payoff = $-1/2 + 1 = 1/2$ each.

    **(b)** Replicator equation: $\dot{x} = x(f_H - \bar{f})$ where $f_H = -x + 2(1-x) = 2-3x$, $f_D = 0 \cdot x + (1-x) = 1-x$, $\bar{f} = x f_H + (1-x)f_D = x(2-3x) + (1-x)(1-x) = 2x-3x^2+1-2x+x^2 = 1-2x^2$.

    $\dot{x} = x(f_H - \bar{f}) = x(2-3x - 1 + 2x^2) = x(1-3x+2x^2) = x(1-x)(1-2x)$.

    **(c)** Interior equilibrium: $\dot{x} = 0$ at $x^* = 1/2$ (from $1-2x = 0$). Stability: $d/dx[x(1-x)(1-2x)]|_{x=1/2} = (1/2)(1/2)(-2) = -1/2 < 0$. **Stable.** $\checkmark$

    **(d)** From $x_0 = 0.9$, the trajectory decreases toward $x^* = 0.5$ monotonically (since $\dot{x} < 0$ for $x > 1/2$). The Hawk frequency declines from 90% to the ESS of 50%.

---

**Exercise 36.5.** $2 \times 3$ zero-sum game LP.

??? success "Solution"

    $A = \begin{pmatrix} 3 & -2 & 4 \\ -1 & 4 & -3 \end{pmatrix}$.

    **Player 1's LP:** Maximise $v$ subject to $3p - (1-p) \geq v$ (col 1), $-2p + 4(1-p) \geq v$ (col 2), $4p - 3(1-p) \geq v$ (col 3), $0 \leq p \leq 1$.

    Let $p$ = probability of Row 1. Constraints:
    1. $4p - 1 \geq v$
    2. $4 - 6p \geq v$
    3. $7p - 3 \geq v$

    Set constraint 1 = constraint 2: $4p-1 = 4-6p \Rightarrow 10p = 5 \Rightarrow p = 1/2$. $v = 4(1/2)-1 = 1$.

    Check constraint 3: $7(1/2)-3 = 0.5 < 1 = v$. Constraint 3 is violated — the row player cannot guarantee payoff $v = 1$ when the column player plays column 3 (which yields only $0.5$). This candidate is infeasible.

    So try constraints 1 = 3: $4p-1 = 7p-3 \Rightarrow 2 = 3p \Rightarrow p = 2/3$. $v = 4(2/3)-1 = 5/3$. Check constraint 2: $4-6(2/3) = 0 < 5/3$. Not satisfied.

    Try constraints 2 = 3: $4-6p = 7p-3 \Rightarrow 7 = 13p \Rightarrow p = 7/13$. $v = 4-6(7/13) = 4-42/13 = 10/13 \approx 0.769$. Check constraint 1: $4(7/13)-1 = 28/13-1 = 15/13 > 10/13$. Satisfied. $\checkmark$

    So Player 1 plays $p = 7/13$ (Row 1 with prob 7/13, Row 2 with prob 6/13). Value $= 10/13$.

    **Player 2's strategy:** Columns 2 and 3 are active. Let $q_2, q_3$ be probabilities on columns 2 and 3 ($q_1 = 0$). Player 1's indifference between rows:

    Row 1: $-2q_2 + 4q_3 = 10/13$.
    Row 2: $4q_2 - 3q_3 = 10/13$.
    $q_2 + q_3 = 1$.

    From equations: $-2q_2 + 4(1-q_2) = 10/13$. $4-6q_2 = 10/13$. $q_2 = (4-10/13)/6 = (42/13)/6 = 42/78 = 7/13$. $q_3 = 6/13$.

    Player 2 plays columns $(0, 7/13, 6/13)$. Value of the game: $10/13 \approx 0.769$.

---

**Exercise 36.6.** First-price auction.

??? success "Solution"

    4 bidders, valuations iid $\text{Uniform}[0,100]$.

    **(a)** Equilibrium bid function: $b(v) = \frac{n-1}{n}v = \frac{3}{4}v$. Each bidder shades their bid to 75% of their valuation.

    **(b)** Expected payment of bidder with $v = 80$: The bidder bids $b(80) = 60$. They win when all other 3 bidders have valuations below 80. $\Pr(\text{win}) = (80/100)^3 = 0.512$. Expected payment = $b \times \Pr(\text{win}) = 60 \times 0.512 = 30.72$.

    **(c)** Seller's expected revenue: The expected payment of the highest bidder equals $\mathbb{E}[\text{2nd highest valuation}]$ (by revenue equivalence). For $n = 4$ iid $U[0,100]$: $\mathbb{E}[V_{(3:4)}] = \frac{n-1}{n+1} \times 100 = \frac{3}{5} \times 100 = 60$.

    Alternatively, revenue $= n \times \mathbb{E}[\text{payment per bidder}] = 4 \times \mathbb{E}[b(V)\mathbf{1}\{\text{win}\}] = 4 \times \mathbb{E}[\frac{3}{4}V \cdot (V/100)^3/\ldots]$. By revenue equivalence with the second-price auction: seller revenue $= \mathbb{E}[V_{(n-1:n)}] = \frac{n-1}{n+1} \times 100 = 60$.

---

**Exercise 36.7.** Rock-Paper-Scissors.

??? success "Solution"

    $A = \begin{pmatrix} 0 & -1 & 2 \\ 2 & 0 & -1 \\ -1 & 2 & 0 \end{pmatrix}$.

    **(a)** By symmetry, $(1/3, 1/3, 1/3)$ is a candidate. Player 1's expected payoff from each pure strategy against $(1/3,1/3,1/3)$: Row 1: $(0-1+2)/3 = 1/3$. Row 2: $(2+0-1)/3 = 1/3$. Row 3: $(-1+2+0)/3 = 1/3$. All equal, so player 1 is indifferent. By symmetry, player 2 is also indifferent. The profile $(1/3,1/3,1/3)$ is hence a NE.

    Uniqueness: Any NE must make the opponent indifferent over the support. If any strategy is excluded, the remaining $2 \times 2$ subgame has no equilibrium in which both players are indifferent (can be verified). So the full mixture is the unique NE.

    **(b)** Replicator dynamics: Let $\mathbf{x} = (x_1, x_2, x_3)$ with $x_1+x_2+x_3=1$. Fitness: $f_1 = -x_2+2x_3$, $f_2 = 2x_1-x_3$, $f_3 = -x_1+2x_2$. $\bar{f} = x_1 f_1 + x_2 f_2 + x_3 f_3$.

    $$\dot{x}_i = x_i(f_i - \bar{f}), \quad i=1,2,3.$$

    **(c)** At the interior equilibrium, the Jacobian (restricted to the 2D simplex) has purely imaginary eigenvalues. The equilibrium is a **centre**: trajectories orbit but do not converge or diverge. The system is neutrally stable (Lyapunov stable but not asymptotically stable).

    **(d)** The constraint $x_1 + x_2 + x_3 = 1$ is preserved under the replicator dynamics. Differentiating:

    $$\frac{d}{dt}(x_1+x_2+x_3) = \dot{x}_1 + \dot{x}_2 + \dot{x}_3 = \sum_{i=1}^3 x_i(f_i-\bar{f}) = \sum_i x_i f_i - \bar{f} \sum_i x_i.$$

    Since $\bar{f} = \sum_i x_i f_i$ by definition and $\sum_i x_i = 1$, this equals $\bar{f} - \bar{f} \cdot 1 = 0$.

    Therefore $x_1 + x_2 + x_3$ is conserved: if the initial condition satisfies $\sum_i x_i(0) = 1$, then $\sum_i x_i(t) = 1$ for all $t \geq 0$.

    $\square$

---

**Exercise 36.8.** Cournot duopoly.

??? success "Solution"

    **(a)** $u_i(q_1,q_2) = q_i(P(Q)-c) = q_i(a-q_1-q_2-c)$.

    **(b)** Best response: $\partial u_1/\partial q_1 = a-2q_1-q_2-c = 0 \Rightarrow q_1^*(q_2) = (a-c-q_2)/2$. By symmetry, $q_2^*(q_1) = (a-c-q_1)/2$.

    **(c)** Nash equilibrium: $q_1 = (a-c-q_2)/2$ and $q_2 = (a-c-q_1)/2$. By symmetry $q_1 = q_2 = q^*$. $q^* = (a-c-q^*)/2 \Rightarrow 2q^* = a-c-q^* \Rightarrow q^* = (a-c)/3$.

    Price: $P = a-2q^* = a - 2(a-c)/3 = (a+2c)/3$.

    Profit per firm: $\pi^* = q^*(P-c) = \frac{a-c}{3} \cdot \frac{a-c}{3} = \frac{(a-c)^2}{9}$.

    **(d)** Monopoly: $q_M = (a-c)/2$, $\pi_M = (a-c)^2/4$. Each Cournot firm earns $(a-c)^2/9$; total Cournot profit $= 2(a-c)^2/9 < (a-c)^2/4$ (monopoly profit is higher; duopolists compete it away).

    Competitive outcome: $P = c$, $Q = a-c$, profit $= 0$. Cournot output $2(a-c)/3 < a-c$, so price exceeds marginal cost; Cournot is between monopoly and competition.

    **(e)** With $a=12$, $c=2$: $q^* = (12-2)/3 = 10/3 \approx 3.33$. On the discrete grid $\{0,\ldots,10\}$, the closest is $q = 3$. Both firms choosing $q_1 = q_2 = 3$ gives $P = 6$, $\pi = 3 \times 4 = 12$ each. Checking deviations: $q_1 = 4$ gives $P = 5$, $\pi_1 = 4 \times 3 = 12$ (tie). $q_1 = 2$: $P = 7$, $\pi_1 = 2 \times 5 = 10 < 12$. So $(3,3)$ and $(4,3)$, $(3,4)$ are all candidate equilibria on the grid. The pure NE on the discrete grid includes $(3,3)$, verified by `findPureNash`.
