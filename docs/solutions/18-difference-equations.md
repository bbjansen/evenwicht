<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 18: Difference Equations

**Exercise 18.1.** Solve $x_{t+1} = 0.6x_t + 8$ with $x_0 = 5$. Find the fixed point, determine stability and compute $x_{10}$.

??? success "Solution"

    **Fixed point:** Set $x^* = 0.6x^* + 8$, so $0.4x^* = 8$, hence $x^* = 20$.

    **Stability:** The coefficient $|a| = |0.6| < 1$, so the fixed point is **stable** (attracting).

    **General solution:** The general solution of a first-order linear difference equation $x_{t+1} = ax_t + b$ is:

    $$x_t = (x_0 - x^*) a^t + x^* = (5 - 20)(0.6)^t + 20 = -15 \cdot (0.6)^t + 20.$$

    **Compute $x_{10}$:**

    $$x_{10} = -15 \cdot (0.6)^{10} + 20 = -15 \cdot 0.006047 + 20 = -0.0907 + 20 = 19.909.$$

    The solution converges geometrically to the fixed point $x^* = 20$.

    $\square$

---

**Exercise 18.2.** A population grows according to $N_{t+1} = 1.03N_t - 150$. Find the equilibrium population size and determine whether the population converges to or diverges from it. Starting from $N_0 = 6000$, find $N_t$ for general $t$.

??? success "Solution"

    **Equilibrium:** $N^* = 1.03N^* - 150 \implies -0.03N^* = -150 \implies N^* = 5000$.

    **Stability:** $|a| = |1.03| > 1$, so the equilibrium is **unstable** (divergent).

    **General solution:**

    $$N_t = (N_0 - N^*)(1.03)^t + N^* = (6000 - 5000)(1.03)^t + 5000 = 1000 \cdot (1.03)^t + 5000.$$

    Since $N_0 = 6000 > N^* = 5000$ and $a = 1.03 > 1$, the population **diverges from the equilibrium**, growing without bound. The term $1000 \cdot (1.03)^t$ grows exponentially: after 10 periods, $N_{10} = 1000(1.03)^{10} + 5000 \approx 1344 + 5000 = 6344$.

    $\square$

---

**Exercise 18.3.** Solve $x_{t+2} - 5x_{t+1} + 6x_t = 12$ with $x_0 = 1$, $x_1 = 4$. Classify the stability of the equilibrium.

??? success "Solution"

    **Particular solution (equilibrium):** $x^* - 5x^* + 6x^* = 12 \implies 2x^* = 12 \implies x^* = 6$.

    **Characteristic equation:** $r^2 - 5r + 6 = 0 \implies (r - 2)(r - 3) = 0$, so $r_1 = 2$, $r_2 = 3$.

    **General solution:** $x_t = c_1 \cdot 2^t + c_2 \cdot 3^t + 6$.

    **Apply initial conditions:**

    $x_0 = 1$: $c_1 + c_2 + 6 = 1 \implies c_1 + c_2 = -5$.

    $x_1 = 4$: $2c_1 + 3c_2 + 6 = 4 \implies 2c_1 + 3c_2 = -2$.

    From the first equation: $c_1 = -5 - c_2$. Substituting: $2(-5 - c_2) + 3c_2 = -2 \implies -10 + c_2 = -2 \implies c_2 = 8$.

    Then $c_1 = -5 - 8 = -13$.

    **Solution:** $x_t = -13 \cdot 2^t + 8 \cdot 3^t + 6$.

    **Stability:** Both roots $|r_1| = 2 > 1$ and $|r_2| = 3 > 1$ are outside the unit circle. The equilibrium $x^* = 6$ is **unstable**. The solution diverges, dominated by the $3^t$ term.

    $\square$

---

**Exercise 18.4.** For the Samuelson model with $c = 0.7$ and $v = 0.9$: (a) write the characteristic equation, (b) determine whether the roots are real or complex, (c) classify the equilibrium as stable or unstable, (d) describe the qualitative behaviour (monotone/oscillatory, convergent/divergent).

??? success "Solution"

    The Samuelson multiplier-accelerator model gives the second-order equation:

    $$Y_{t+2} - c(1 + v)Y_{t+1} + cvY_t = \bar{G}$$

    where $c$ is the marginal propensity to consume and $v$ is the accelerator coefficient. Substituting $c = 0.7$, $v = 0.9$:

    $$\begin{aligned}
    Y_{t+2} - 0.7(1.9)Y_{t+1} + 0.63Y_t &= \bar{G} \\
    Y_{t+2} - 1.33Y_{t+1} + 0.63Y_t &= \bar{G}.
    \end{aligned}$$

    (a) **Characteristic equation:** $r^2 - 1.33r + 0.63 = 0$.

    (b) **Discriminant:** $\Delta = 1.33^2 - 4(0.63) = 1.7689 - 2.52 = -0.7511 < 0$.

    The roots are **complex**.

    $$r = \frac{1.33 \pm \sqrt{-0.7511}}{2} = \frac{1.33 \pm 0.8667i}{2} = 0.665 \pm 0.4334i.$$

    (c) **Modulus:** $|r| = \sqrt{0.665^2 + 0.4334^2} = \sqrt{0.4422 + 0.1878} = \sqrt{0.63} \approx 0.7937$.

    Since $|r| = \sqrt{cv} = \sqrt{0.63} < 1$, the equilibrium is **stable**.

    (d) The roots are complex with modulus less than 1, so the behaviour is **oscillatory and convergent** (damped oscillations). The system oscillates around the equilibrium with decreasing amplitude, the amplitude decaying by a factor of $\sqrt{0.63} \approx 0.794$ each period. The period of oscillation is $2\pi / \arg(r) = 2\pi / \arctan(0.4334/0.665) \approx 2\pi / 0.5767 \approx 10.9$ periods.

    $\square$

---

**Exercise 18.5.** Prove that $x_{t+2} - 2\cos(\theta)x_{t+1} + x_t = 0$ produces pure oscillations $x_t = c_1\cos(\theta t) + c_2\sin(\theta t)$ with constant amplitude. What is the spectral radius? Interpret physically.

??? success "Solution"

    **Characteristic equation:** $r^2 - 2\cos(\theta)r + 1 = 0$.

    Using the quadratic formula:

    $$r = \frac{2\cos(\theta) \pm \sqrt{4\cos^2(\theta) - 4}}{2} = \cos(\theta) \pm \sqrt{\cos^2(\theta) - 1} = \cos(\theta) \pm i\sin(\theta).$$

    (For $\theta \neq 0, \pi$, the discriminant is negative since $\cos^2\theta - 1 = -\sin^2\theta < 0$.)

    So $r_1 = e^{i\theta}$ and $r_2 = e^{-i\theta}$.

    The general solution (in complex form) is $x_t = c_1 e^{i\theta t} + c_2 e^{-i\theta t}$. For real initial conditions, $c_2 = \bar{c}_1$, and the solution becomes:

    $$x_t = A\cos(\theta t) + B\sin(\theta t),$$

    where $A, B$ are real constants determined by initial conditions. This can also be written as $x_t = R\cos(\theta t - \phi)$ with $R = \sqrt{A^2 + B^2}$ and $\phi = \arctan(B/A)$.

    **Amplitude:** $|x_t|^2 \leq A^2 + B^2 = R^2$, which is constant. The amplitude $R$ does not decay or grow.

    **Spectral radius:** $\rho = |r_1| = |r_2| = |e^{i\theta}| = 1$. The spectral radius equals exactly 1.

    **Physical interpretation:** The system is a lossless oscillator (no damping, no energy input). It oscillates with constant amplitude and angular frequency $\theta$ per time step, analogous to a frictionless harmonic oscillator. The spectral radius being exactly 1 means the system is marginally stable: it neither converges to equilibrium nor diverges.

    $\square$

---

**Exercise 18.6.** Consider the linear system $\mathbf{x}_{t+1} = \begin{pmatrix} 0.5 & 0.3 \\ 0.1 & 0.4 \end{pmatrix}\mathbf{x}_t + \begin{pmatrix} 2 \\ 1 \end{pmatrix}$. Find the equilibrium $\mathbf{x}^*$, compute the eigenvalues of $A$, verify the spectral radius condition and describe the qualitative convergence.

??? success "Solution"

    **Equilibrium:** $\mathbf{x}^* = A\mathbf{x}^* + \mathbf{b}$, so $(I - A)\mathbf{x}^* = \mathbf{b}$.

    $$I - A = \begin{pmatrix} 0.5 & -0.3 \\ -0.1 & 0.6 \end{pmatrix}.$$

    $\det(I - A) = 0.5 \times 0.6 - (-0.3)(-0.1) = 0.30 - 0.03 = 0.27$.

    $$\begin{aligned}
    (I - A)^{-1} &= \frac{1}{0.27}\begin{pmatrix} 0.6 & 0.3 \\ 0.1 & 0.5 \end{pmatrix} = \begin{pmatrix} 2.222 & 1.111 \\ 0.370 & 1.852 \end{pmatrix}. \\
    \mathbf{x}^* &= (I - A)^{-1}\mathbf{b} = \begin{pmatrix} 2.222 \times 2 + 1.111 \times 1 \\ 0.370 \times 2 + 1.852 \times 1 \end{pmatrix} = \begin{pmatrix} 5.556 \\ 2.593 \end{pmatrix}.
    \end{aligned}$$

    **Eigenvalues of $A$:** $\det(A - \lambda I) = (0.5 - \lambda)(0.4 - \lambda) - 0.03 = \lambda^2 - 0.9\lambda + 0.17 = 0$.

    $$\lambda = \frac{0.9 \pm \sqrt{0.81 - 0.68}}{2} = \frac{0.9 \pm \sqrt{0.13}}{2} = \frac{0.9 \pm 0.3606}{2}.$$

    $\lambda_1 = 0.6303$, $\lambda_2 = 0.2697$.

    **Spectral radius:** $\rho(A) = \max(|\lambda_1|, |\lambda_2|) = 0.6303 < 1$. The spectral radius condition is satisfied.

    **Qualitative convergence:** Both eigenvalues are real and positive with $0 < \lambda_2 < \lambda_1 < 1$, so the system converges **monotonically** (no oscillations) to the equilibrium $\mathbf{x}^* \approx (5.556, 2.593)^T$. The rate of convergence is governed by the dominant eigenvalue $\lambda_1 \approx 0.63$; the error decays approximately as $(0.63)^t$.

    $\square$

---

**Exercise 18.7.** Show that the Schur–Cohn conditions for second-order stability (Theorem 18.8) are equivalent to the geometric requirement that the point $(a_1, a_2)$ lies inside the triangle with vertices $(-2, 1)$, $(2, 1)$ and $(0, -1)$ in the $(a_1, a_2)$-plane. Sketch this stability triangle.

??? success "Solution"

    For the second-order equation $x_{t+2} + a_1 x_{t+1} + a_2 x_t = 0$, the characteristic equation is $r^2 + a_1 r + a_2 = 0$, and stability requires both roots to satisfy $|r| < 1$. The Schur–Cohn conditions are:

    1. $|a_2| < 1$
    2. $1 + a_1 + a_2 > 0$
    3. $1 - a_1 + a_2 > 0$

    **Geometric interpretation.** These three inequalities define a region in the $(a_1, a_2)$-plane:

    - $a_2 < 1$ and $a_2 > -1$: a horizontal strip.
    - $a_2 > -1 - a_1$: a half-plane above the line $a_2 = -1 - a_1$ (passing through $(-2, 1)$ and $(0, -1)$).
    - $a_2 > a_1 - 1$: a half-plane above the line $a_2 = a_1 - 1$ (passing through $(0, -1)$ and $(2, 1)$).

    The intersection of these three constraints is a triangle with vertices:

    - $a_2 = 1$ meets $a_2 = -1 - a_1$: $(1)= -1 - a_1 \implies a_1 = -2$. Vertex: $(-2, 1)$.
    - $a_2 = 1$ meets $a_2 = a_1 - 1$: $1 = a_1 - 1 \implies a_1 = 2$. Vertex: $(2, 1)$.
    - $a_2 = -1 - a_1$ meets $a_2 = a_1 - 1$: $-1 - a_1 = a_1 - 1 \implies a_1 = 0, a_2 = -1$. Vertex: $(0, -1)$.

    **Proof of equivalence.**

    $(\Rightarrow)$: If $|r_1|, |r_2| < 1$, then by Vieta's formulas $a_2 = r_1 r_2$ and $a_1 = -(r_1 + r_2)$. Then $|a_2| = |r_1 r_2| < 1$. Also $1 + a_1 + a_2 = (1 - r_1)(1 - r_2) > 0$ (since $|r_i| < 1$ means $r_i < 1$ if real, and $(1-r_1)(1-r_2) > 0$ for complex conjugate pairs as well). Similarly $1 - a_1 + a_2 = (1 + r_1)(1 + r_2) > 0$.

    $(\Leftarrow)$: Define $p(r) = r^2 + a_1 r + a_2$. Then $p(1) = 1 + a_1 + a_2 > 0$ and $p(-1) = 1 - a_1 + a_2 > 0$ by conditions 2 and 3. Also $|a_2| = |r_1 r_2| < 1$ by condition 1. Since $p(1) > 0$, $p(-1) > 0$, and the product of roots has modulus less than 1, one can show (by case analysis on real vs. complex roots) that both roots lie inside the unit circle.

    $\square$

---

**Exercise 18.8.** For the logistic map $x_{t+1} = rx_t(1-x_t)$: (a) find all fixed points as a function of $r$, (b) determine the stability of each fixed point by computing $|f'(x^*)|$, (c) find the value of $r$ at which the nonzero fixed point loses stability and (d) verify numerically (by simulation) that a stable 2-cycle exists for $r = 3.2$.

??? success "Solution"

    Let $f(x) = rx(1 - x)$.

    (a) **Fixed points:** $x^* = rx^*(1 - x^*)$.

    Either $x^* = 0$ or $1 = r(1 - x^*)$, giving $x^* = 1 - 1/r = (r-1)/r$.

    Fixed points: $x_1^* = 0$ and $x_2^* = (r-1)/r$ (the latter exists in $(0,1)$ for $r > 1$).

    (b) **Stability via $|f'(x^*)|$:** $f'(x) = r(1 - 2x)$.

    At $x_1^* = 0$: $f'(0) = r$. Stable iff $|r| < 1$, i.e., $0 < r < 1$.

    At $x_2^* = (r-1)/r$: $f'((r-1)/r) = r(1 - 2(r-1)/r) = r \cdot (1 - 2 + 2/r) = r(-1 + 2/r) = 2 - r$.

    Stable iff $|2 - r| < 1$, i.e., $-1 < 2 - r < 1$, i.e., $1 < r < 3$.

    (c) The nonzero fixed point loses stability when $|2 - r| = 1$. For $r > 1$, $2 - r$ is decreasing. It reaches $-1$ when $2 - r = -1$, i.e., $r = 3$. At $r = 3$, a **period-doubling bifurcation** occurs.

    (d) **Numerical verification for $r = 3.2$:** Starting from $x_0 = 0.5$, after transient decay the orbit converges to a stable 2-cycle alternating between approximately $x_a \approx 0.5130$ and $x_b \approx 0.7995$. The 2-cycle points satisfy $x^2 - \frac{r+1}{r}x + \frac{r+1}{r^2} = 0$, giving $x = \frac{(r+1) \pm \sqrt{(r+1)(r-3)}}{2r}$. For $r = 3.2$: $x = \frac{4.2 \pm \sqrt{4.2 \times 0.2}}{6.4} = \frac{4.2 \pm \sqrt{0.84}}{6.4} = \frac{4.2 \pm 0.9165}{6.4}$, yielding $x_a \approx 0.5130$ and $x_b \approx 0.7995$.

    $\square$

---
