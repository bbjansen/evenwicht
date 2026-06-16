<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 12: Constrained Optimisation

**Exercise 12.1.** Find the maximum and minimum of $f(x,y) = x + 2y$ subject to $x^2 + y^2 = 5$.

??? success "Solution"

    Set up the Lagrangian using the addition convention: $\mathcal{L} = x + 2y + \lambda(x^2 + y^2 - 5)$.

    $$\begin{aligned}
    \frac{\partial \mathcal{L}}{\partial x} &= 1 + 2\lambda x = 0 \implies x = -\frac{1}{2\lambda}. \\
    \frac{\partial \mathcal{L}}{\partial y} &= 2 + 2\lambda y = 0 \implies y = -\frac{1}{\lambda}.
    \end{aligned}$$

    Substitute into the constraint: $\frac{1}{4\lambda^2} + \frac{1}{\lambda^2} = 5 \implies \frac{5}{4\lambda^2} = 5 \implies \lambda^2 = \frac{1}{4} \implies \lambda = \pm \frac{1}{2}$.

    For $\lambda = -1/2$: $x = 1$, $y = 2$. $f(1,2) = 1 + 4 = 5$. **Maximum.**

    For $\lambda = 1/2$: $x = -1$, $y = -2$. $f(-1,-2) = -1 - 4 = -5$. **Minimum.**

---

**Exercise 12.2.** Convert the LP to standard form: minimise $2x_1 - 3x_2$ subject to $x_1 + x_2 \geq 2$, $-x_1 + x_2 \leq 3$, $x_1 \geq 0$, $x_2$ unrestricted.

??? success "Solution"

    **Step 1:** Standard form requires maximisation, $\leq$ constraints and non-negative variables.

    - Convert min to max: maximise $-2x_1 + 3x_2$.
    - Split $x_2$ (unrestricted) into $x_2 = x_2^+ - x_2^-$ with $x_2^+, x_2^- \geq 0$.
    - Convert $x_1 + x_2 \geq 2$ to $-x_1 - x_2 \leq -2$.

    Standard form:

    Maximise $-2x_1 + 3x_2^+ - 3x_2^-$

    subject to:

    $-x_1 - x_2^+ + x_2^- \leq -2$

    $-x_1 + x_2^+ - x_2^- \leq 3$

    $x_1, x_2^+, x_2^- \geq 0.$

    **Step 2** (adding slack variables for equality form): Introduce slacks $s_1, s_2 \geq 0$:

    $-x_1 - x_2^+ + x_2^- + s_1 = -2$

    $-x_1 + x_2^+ - x_2^- + s_2 = 3$

---

**Exercise 12.3.** Apply the simplex method to $\max\; 5x_1 + 4x_2$ subject to $x_1 + x_2 \leq 5$, $2x_1 + x_2 \leq 8$, $x_1, x_2 \geq 0$.

??? success "Solution"

    Add slack variables $s_1, s_2$: $x_1 + x_2 + s_1 = 5$, $2x_1 + x_2 + s_2 = 8$.

    **Tableau 0:**

    | | $x_1$ | $x_2$ | $s_1$ | $s_2$ | RHS |
    |--|-------|-------|-------|-------|-----|
    | $s_1$ | 1 | 1 | 1 | 0 | 5 |
    | $s_2$ | 2 | 1 | 0 | 1 | 8 |
    | $z$ | -5 | -4 | 0 | 0 | 0 |

    Most negative in $z$-row: $x_1$ enters. Ratios: $5/1 = 5$, $8/2 = 4$. Minimum ratio: row 2. Pivot on $(2, 1)$, entry $= 2$.

    Divide row 2 by 2: $(1, 1/2, 0, 1/2, 4)$.

    $R_1 \leftarrow R_1 - R_2'$: $(0, 1/2, 1, -1/2, 1)$.

    $R_z \leftarrow R_z + 5R_2'$: $(0, -3/2, 0, 5/2, 20)$.

    **Tableau 1:**

    | | $x_1$ | $x_2$ | $s_1$ | $s_2$ | RHS |
    |--|-------|-------|-------|-------|-----|
    | $s_1$ | 0 | 1/2 | 1 | -1/2 | 1 |
    | $x_1$ | 1 | 1/2 | 0 | 1/2 | 4 |
    | $z$ | 0 | -3/2 | 0 | 5/2 | 20 |

    Most negative: $x_2$ enters. Ratios: $1/(1/2) = 2$, $4/(1/2) = 8$. Minimum ratio: row 1. Pivot on $(1, 2)$, entry $= 1/2$.

    Multiply row 1 by 2: $(0, 1, 2, -1, 2)$.

    $R_2 \leftarrow R_2 - (1/2)R_1'$: $(1, 0, -1, 1, 3)$.

    $R_z \leftarrow R_z + (3/2)R_1'$: $(0, 0, 3, 1, 23)$.

    **Tableau 2 (final):**

    | | $x_1$ | $x_2$ | $s_1$ | $s_2$ | RHS |
    |--|-------|-------|-------|-------|-----|
    | $x_2$ | 0 | 1 | 2 | -1 | 2 |
    | $x_1$ | 1 | 0 | -1 | 1 | 3 |
    | $z$ | 0 | 0 | 3 | 1 | 23 |

    All $z$-row entries are non-negative. Optimal solution: $x_1 = 3$, $x_2 = 2$, $z = 5(3) + 4(2) = 23$.

---

**Exercise 12.4.** Find the closest point on the plane $2x + y - z = 5$ to the origin.

??? success "Solution"

    Minimise $f(x,y,z) = x^2 + y^2 + z^2$ subject to $g(x,y,z) = 2x + y - z - 5 = 0$.

    Lagrangian: $\nabla f = \lambda \nabla g$: $(2x, 2y, 2z) = \lambda(2, 1, -1)$.

    $$x = \lambda, \quad y = \lambda/2, \quad z = -\lambda/2.$$

    Constraint: $2\lambda + \lambda/2 - (-\lambda/2) = 5 \implies 2\lambda + \lambda/2 + \lambda/2 = 5 \implies 3\lambda = 5 \implies \lambda = 5/3$.

    $$x = 5/3, \quad y = 5/6, \quad z = -5/6.$$

    Distance: $\sqrt{(5/3)^2 + (5/6)^2 + (5/6)^2} = \sqrt{25/9 + 25/36 + 25/36} = \sqrt{25/9 + 50/36} = \sqrt{100/36 + 50/36} = \sqrt{150/36} = \frac{5\sqrt{6}}{6}$.

    **Distance formula verification:** $d = \frac{|2(0) + 1(0) - 1(0) - 5|}{\sqrt{4 + 1 + 1}} = \frac{5}{\sqrt{6}} = \frac{5\sqrt{6}}{6}$. $\checkmark$

---

**Exercise 12.5.** Solve the LP: maximise $5x_1 + 4x_2$ subject to $x_1 + 2x_2 \leq 14$, $3x_1 + 2x_2 \leq 18$, $x_1, x_2 \geq 0$. Write the dual, find the dual solution, and interpret the shadow prices.

??? success "Solution"

    **Primal LP:** Maximise $5x_1 + 4x_2$ subject to $x_1 + 2x_2 \leq 14$, $3x_1 + 2x_2 \leq 18$, $x_1, x_2 \geq 0$.

    (Here column $j$ of $A$ gives the resource requirements for good $j$.)

    **Corner points:**

    - $(0, 0)$: $z = 0$.
    - $(6, 0)$: $z = 30$. (From $3x_1 = 18$.)
    - $(0, 7)$: $z = 28$. (From $2x_2 = 14$.)
    - Intersection of $x_1 + 2x_2 = 14$ and $3x_1 + 2x_2 = 18$: subtract to get $2x_1 = 4$, so $x_1 = 2$, $x_2 = 6$. $z = 10 + 24 = 34$.

    **Optimal:** $x_1^* = 2$, $x_2^* = 6$, $z^* = 34$.

    **Dual LP:** Minimise $14y_1 + 18y_2$ subject to $y_1 + 3y_2 \geq 5$, $2y_1 + 2y_2 \geq 4$, $y_1, y_2 \geq 0$.

    **Dual solution** (from complementary slackness, since both primal constraints are binding):

    $y_1 + 3y_2 = 5$ and $2y_1 + 2y_2 = 4$.

    From the second: $y_1 + y_2 = 2 \implies y_1 = 2 - y_2$. Substituting: $(2 - y_2) + 3y_2 = 5 \implies 2y_2 = 3 \implies y_2 = 3/2$, $y_1 = 1/2$.

    Dual objective: $14(1/2) + 18(3/2) = 7 + 27 = 34 = z^*$. $\checkmark$ (Strong duality.)

    **Shadow prices:** $y_1 = 1/2$ means one additional unit of resource 1 increases profit by $€0.50$. $y_2 = 3/2$ means one additional unit of resource 2 increases profit by $€1.50$.

    **Should the firm buy an extra unit of resource 1 at $€3$?** The shadow price of resource 1 is $€0.50$, which is less than the cost of $€3$. **No**, the firm should not purchase it, as the cost exceeds the benefit.

---

**Exercise 12.6.** Maximise $x_1 - x_2$ subject to $x_1 - x_2 \leq 1$, $-x_1 + x_2 \leq 1$, $x_1, x_2 \geq 0$. Is the feasible region bounded? Does the LP have a finite optimal solution?

??? success "Solution"

    **Feasible region is unbounded.** The constraints $x_1 - x_2 \leq 1$ and $-x_1 + x_2 \leq 1$ together say $|x_1 - x_2| \leq 1$. Combined with $x_1, x_2 \geq 0$, the feasible set is the unbounded strip $\mathcal{F} = \{(x_1, x_2) \geq 0 : |x_1 - x_2| \leq 1\}$. For instance, the ray $(t, t)$ for $t \geq 0$ lies in $\mathcal{F}$ (since $|t - t| = 0 \leq 1$), and $t \to \infty$, confirming the region is unbounded.

    **The LP has a finite optimal solution.** The objective is $z = x_1 - x_2$. The constraint $x_1 - x_2 \leq 1$ directly bounds the objective from above: $z = x_1 - x_2 \leq 1$ for all feasible points. Therefore the optimal value is at most $1$.

    The bound $z = 1$ is achieved: at $(x_1, x_2) = (1, 0)$, we have $z = 1 - 0 = 1$. Checking feasibility: $1 - 0 = 1 \leq 1$ (tight) and $-1 + 0 = -1 \leq 1$ (satisfied), and $x_1, x_2 \geq 0$. So $(1, 0)$ is feasible.

    Therefore the LP has a **finite optimal value** $z^* = 1$, attained at $(x_1^*, x_2^*) = (1, 0)$, despite the feasible region being unbounded. This illustrates that an unbounded feasible region does not imply the objective is unbounded: the objective direction matters.

---

**Exercise 12.7.** Prove the weak duality theorem.

??? success "Solution"

    *Proof.* Consider the primal LP: maximise $\mathbf{c}^T\mathbf{x}$ subject to $A\mathbf{x} \leq \mathbf{b}$, $\mathbf{x} \geq \mathbf{0}$, and the dual LP: minimise $\mathbf{b}^T\mathbf{y}$ subject to $A^T\mathbf{y} \geq \mathbf{c}$, $\mathbf{y} \geq \mathbf{0}$.

    Let $\mathbf{x}$ be primal feasible and $\mathbf{y}$ be dual feasible. Then:

    1. $A\mathbf{x} \leq \mathbf{b}$ and $\mathbf{x} \geq \mathbf{0}$ (primal feasibility).
    2. $A^T\mathbf{y} \geq \mathbf{c}$ and $\mathbf{y} \geq \mathbf{0}$ (dual feasibility).

    From condition 2: $A^T\mathbf{y} \geq \mathbf{c}$. Since $\mathbf{x} \geq \mathbf{0}$, multiplying both sides by $\mathbf{x}^T$ preserves the inequality:

    $$\mathbf{x}^T A^T \mathbf{y} \geq \mathbf{x}^T \mathbf{c} = \mathbf{c}^T\mathbf{x}. \quad (*)$$

    From condition 1: $A\mathbf{x} \leq \mathbf{b}$. Since $\mathbf{y} \geq \mathbf{0}$, multiplying by $\mathbf{y}^T$:

    $$\mathbf{y}^T A \mathbf{x} \leq \mathbf{y}^T \mathbf{b} = \mathbf{b}^T\mathbf{y}. \quad (**)$$

    Note that $\mathbf{x}^T A^T \mathbf{y} = (\mathbf{y}^T A \mathbf{x})^T = \mathbf{y}^T A \mathbf{x}$ (since this is a scalar). Combining $(*)$ and $(**)$:

    $$\mathbf{c}^T\mathbf{x} \leq \mathbf{x}^T A^T \mathbf{y} = \mathbf{y}^T A \mathbf{x} \leq \mathbf{b}^T\mathbf{y}.$$

    Therefore $\mathbf{c}^T\mathbf{x} \leq \mathbf{b}^T\mathbf{y}$.

    $\square$

    The feasibility conditions used were: (i) $\mathbf{x} \geq \mathbf{0}$ (to multiply the dual constraint), (ii) $\mathbf{y} \geq \mathbf{0}$ (to multiply the primal constraint), (iii) $A^T\mathbf{y} \geq \mathbf{c}$ (dual constraint), and (iv) $A\mathbf{x} \leq \mathbf{b}$ (primal constraint).

---

**Exercise 12.8.** Maximise $f(x,y,z) = xyz$ subject to $x + y + z = 12$ and $x + y - z = 0$.

??? success "Solution"

    From the constraints: Adding gives $2(x + y) = 12$, so $x + y = 6$, hence $z = 6$. Subtracting gives $2z = 12$, confirming $z = 6$.

    The problem reduces to: maximise $g(x, y) = 6xy$ subject to $x + y = 6$, $x, y$ free (with $x, y > 0$ required for a positive product).

    **Lagrange multiplier approach:** The Lagrangian is:

    $$\mathcal{L} = xyz + \lambda_1(x + y + z - 12) + \lambda_2(x + y - z).$$

    $$\begin{aligned}
    \frac{\partial \mathcal{L}}{\partial x} &= yz + \lambda_1 + \lambda_2 = 0 \quad (1) \\
    \frac{\partial \mathcal{L}}{\partial y} &= xz + \lambda_1 + \lambda_2 = 0 \quad (2) \\
    \frac{\partial \mathcal{L}}{\partial z} &= xy + \lambda_1 - \lambda_2 = 0 \quad (3)
    \end{aligned}$$

    From (1) and (2): $yz = xz$, so $z(y - x) = 0$. Since $z = 6 \neq 0$, $x = y$.

    From $x + y = 6$ and $x = y$: $x = y = 3$, $z = 6$.

    $f(3, 3, 6) = 3 \cdot 3 \cdot 6 = 54$.

    **Finding multipliers:** From (1): $3 \cdot 6 + \lambda_1 + \lambda_2 = 0$, so $\lambda_1 + \lambda_2 = -18$. From (3): $9 + \lambda_1 - \lambda_2 = 0$, so $\lambda_1 - \lambda_2 = -9$. Solving: $\lambda_1 = -27/2$, $\lambda_2 = -9/2$.

    **Verification via substitution:** With $z = 6$ and $y = 6 - x$: $f = 6x(6-x) = 36x - 6x^2$. Setting $f' = 36 - 12x = 0$: $x = 3$. $f''= -12 < 0$, confirming a maximum. $f(3) = 6 \cdot 3 \cdot 3 = 54$. $\checkmark$

    The maximum value of $xyz$ is $\mathbf{54}$, attained at $(x, y, z) = (3, 3, 6)$.

---
