<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 19: Ordinary Differential Equations

**Exercise 19.1.** Classify each equation by order, linearity and autonomy: (a) $y' = 3y + 1$, (b) $y'' + ty = 0$, (c) $y' = y^2 - y$, (d) $y''' + y' = \sin t$.

??? success "Solution"

    (a) $y' = 3y + 1$: **First-order**, **linear** ($y$ and $y'$ appear to the first power with constant coefficients), **autonomous** (no explicit dependence on $t$).

    (b) $y'' + ty = 0$: **Second-order**, **linear** (all terms in $y$ and its derivatives are first-degree), **non-autonomous** (the coefficient $t$ depends explicitly on the independent variable).

    (c) $y' = y^2 - y$: **First-order**, **nonlinear** (the $y^2$ term), **autonomous** (no explicit $t$ dependence).

    (d) $y''' + y' = \sin t$: **Third-order**, **linear** (all terms in $y$, $y'$, $y'''$ are first-degree with constant coefficients), **non-autonomous** (the forcing term $\sin t$ depends on $t$).

    $\square$

---

**Exercise 19.2.** Solve by separation of variables: $dy/dx = x/y$ with $y(0) = 2$. Verify the answer by differentiation.

??? success "Solution"

    Separate variables: $y\,dy = x\,dx$.

    Integrate both sides: $\int y\,dy = \int x\,dx \implies \frac{y^2}{2} = \frac{x^2}{2} + C$.

    Apply IC $y(0) = 2$: $\frac{4}{2} = 0 + C \implies C = 2$.

    Solution: $\frac{y^2}{2} = \frac{x^2}{2} + 2 \implies y^2 = x^2 + 4 \implies y = \sqrt{x^2 + 4}$ (taking the positive root since $y(0) = 2 > 0$).

    **Verification:** $\frac{dy}{dx} = \frac{2x}{2\sqrt{x^2 + 4}} = \frac{x}{\sqrt{x^2+4}} = \frac{x}{y}$. $\checkmark$

    $\square$

---

**Exercise 19.3.** Solve the first-order linear ODE $y' - 3y = e^{2x}$ with $y(0) = 1$ using an integrating factor.

??? success "Solution"

    This is a first-order linear ODE. The integrating factor is $\mu(x) = e^{\int -3\,dx} = e^{-3x}$.

    Multiply through: $e^{-3x}y' - 3e^{-3x}y = e^{-3x} \cdot e^{2x} = e^{-x}$.

    The left side is $\frac{d}{dx}[e^{-3x}y]$. So:

    $$\frac{d}{dx}[e^{-3x}y] = e^{-x}.$$

    Integrate: $e^{-3x}y = \int e^{-x}\,dx = -e^{-x} + C$.

    $$y = -e^{-x} \cdot e^{3x} + Ce^{3x} = -e^{2x} + Ce^{3x}.$$

    Apply IC $y(0) = 1$: $1 = -1 + C \implies C = 2$.

    **Solution:** $y(x) = -e^{2x} + 2e^{3x}$.

    **Verification:** $y' = -2e^{2x} + 6e^{3x}$. Then $y' - 3y = (-2e^{2x} + 6e^{3x}) - 3(-e^{2x} + 2e^{3x}) = -2e^{2x} + 6e^{3x} + 3e^{2x} - 6e^{3x} = e^{2x}$. $\checkmark$

    $\square$

---

**Exercise 19.4.** Solve $y'' + 6y' + 9y = 0$ with $y(0) = 2$, $y'(0) = -3$. Identify the case (distinct real roots, repeated root, or complex roots) and state the general form of the solution before applying initial conditions.

??? success "Solution"

    **Characteristic equation:** $r^2 + 6r + 9 = 0 \implies (r + 3)^2 = 0 \implies r = -3$ (repeated root).

    This is the **repeated root case**. The general solution is:

    $$y(x) = (c_1 + c_2 x)e^{-3x}.$$

    **Apply initial conditions:**

    $y(0) = 2$: $c_1 = 2$.

    $y'(x) = c_2 e^{-3x} - 3(c_1 + c_2 x)e^{-3x} = (c_2 - 3c_1 - 3c_2 x)e^{-3x}$.

    $y'(0) = -3$: $c_2 - 3c_1 = -3 \implies c_2 - 6 = -3 \implies c_2 = 3$.

    **Solution:** $y(x) = (2 + 3x)e^{-3x}$.

    $\square$

---

**Exercise 19.5.** For the autonomous equation $y' = y(2 - y)(y - 1)$, find all equilibria. Determine the stability of each equilibrium using the derivative criterion. Sketch the phase line.

??? success "Solution"

    **Equilibria:** Set $y(2 - y)(y - 1) = 0$. Solutions: $y^* = 0$, $y^* = 1$, $y^* = 2$.

    **Stability via derivative criterion.** Let $f(y) = y(2 - y)(y - 1)$. Expanding: $f(y) = -y^3 + 3y^2 - 2y$.

    $f'(y) = -3y^2 + 6y - 2$.

    At $y^* = 0$: $f'(0) = -2 < 0$. **Stable.**

    At $y^* = 1$: $f'(1) = -3 + 6 - 2 = 1 > 0$. **Unstable.**

    At $y^* = 2$: $f'(2) = -12 + 12 - 2 = -2 < 0$. **Stable.**

    **Phase line sketch:**

    - For $y < 0$: $f(y) > 0$. Arrow points up (toward $y = 0$).
    - For $0 < y < 1$: $f(y) < 0$. Arrow points down (toward $y = 0$).
    - For $1 < y < 2$: $f(y) > 0$. Arrow points up (toward $y = 2$).
    - For $y > 2$: $f(y) < 0$. Arrow points down (toward $y = 2$).

    ```
    ... ----> [0] <---- [1] ----> [2] <---- ...
             stable   unstable   stable
    ```

    Solutions approach $y = 0$ from below and from $(0,1)$, flee from $y = 1$ and approach $y = 2$ from $(1,2)$ and from above.

    $\square$

---

**Exercise 19.6.** Write the second-order equation $\ddot{x} + 2\dot{x} + 5x = 0$ as a first-order system $\dot{\mathbf{x}} = A\mathbf{x}$. Find the eigenvalues of $A$ and classify the equilibrium at the origin. Determine the oscillation frequency and decay rate.

??? success "Solution"

    Let $x_1 = x$ and $x_2 = \dot{x}$. Then:

    $$\dot{x}_1 = x_2, \qquad \dot{x}_2 = -5x_1 - 2x_2.$$

    In matrix form: $\dot{\mathbf{x}} = A\mathbf{x}$ with $A = \begin{pmatrix} 0 & 1 \\ -5 & -2 \end{pmatrix}$.

    **Eigenvalues:** $\det(A - \lambda I) = (0 - \lambda)(-2 - \lambda) - (1)(-5) = \lambda^2 + 2\lambda + 5 = 0$.

    $$\lambda = \frac{-2 \pm \sqrt{4 - 20}}{2} = \frac{-2 \pm \sqrt{-16}}{2} = -1 \pm 2i.$$

    **Classification:** Complex eigenvalues with negative real part $\implies$ **stable spiral** (spiral sink).

    **Oscillation frequency:** The imaginary part gives the angular frequency $\omega = 2$ (radians per unit time). The period of oscillation is $T = 2\pi / \omega = \pi$.

    **Decay rate:** The real part gives the decay rate $\sigma = 1$. The amplitude decays as $e^{-t}$. The solution is $x(t) = e^{-t}(c_1 \cos 2t + c_2 \sin 2t)$: oscillations with exponentially decaying envelope.

    $\square$

---

**Exercise 19.7.** Implement one step of Euler's method and one step of RK4 by hand for the problem $y' = t + y$, $y(0) = 1$, with $h = 0.1$. Compare with the exact solution $y(t) = 2e^t - t - 1$ evaluated at $t = 0.1$.

??? success "Solution"

    **Euler's method:** $y_1 = y_0 + h f(t_0, y_0) = 1 + 0.1 \cdot (0 + 1) = 1 + 0.1 = 1.1$.

    **RK4:** Let $f(t, y) = t + y$.

    $k_1 = f(0, 1) = 1$.

    $k_2 = f(0 + 0.05, 1 + 0.05 \cdot 1) = f(0.05, 1.05) = 0.05 + 1.05 = 1.1$.

    $k_3 = f(0 + 0.05, 1 + 0.05 \cdot 1.1) = f(0.05, 1.055) = 0.05 + 1.055 = 1.105$.

    $k_4 = f(0 + 0.1, 1 + 0.1 \cdot 1.105) = f(0.1, 1.1105) = 0.1 + 1.1105 = 1.2105$.

    $$y_1^{\text{RK4}} = 1 + \frac{0.1}{6}(k_1 + 2k_2 + 2k_3 + k_4) = 1 + \frac{0.1}{6}(1 + 2.2 + 2.21 + 1.2105) = 1 + \frac{0.1}{6}(6.6205) = 1.11034.$$

    **Exact solution:** $y(t) = 2e^t - t - 1$. At $t = 0.1$: $y(0.1) = 2e^{0.1} - 0.1 - 1 = 2(1.10517) - 1.1 = 1.11034$.

    **Comparison:**

    | Method | $y_1$ | Error |
    |--------|-------|-------|
    | Euler  | 1.10000 | $1.03 \times 10^{-2}$ |
    | RK4    | 1.11034 | $\approx 3 \times 10^{-7}$ |
    | Exact  | 1.11034 |  |

    RK4 is roughly $10^4$ times more accurate than Euler for this step size, consistent with their respective orders ($O(h^4)$ vs. $O(h)$).

    $\square$

---

**Exercise 19.8.** Consider the linear system $\dot{\mathbf{x}} = A\mathbf{x}$ with $A = \begin{pmatrix} -1 & 2 \\ 0 & -3 \end{pmatrix}$. (a) Find the eigenvalues and eigenvectors of $A$. (b) Write the general solution $\mathbf{x}(t)$. (c) Determine the stability of the origin. (d) Find the specific solution with $\mathbf{x}(0) = (4, 2)^T$.

??? success "Solution"

    (a) **Eigenvalues:** $A$ is upper triangular, so the eigenvalues are the diagonal entries: $\lambda_1 = -1$, $\lambda_2 = -3$.

    **Eigenvectors:**

    For $\lambda_1 = -1$: $(A + I)\mathbf{v} = 0 \implies \begin{pmatrix} 0 & 2 \\ 0 & -2 \end{pmatrix}\mathbf{v} = 0 \implies v_2 = 0$. So $\mathbf{v}_1 = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$.

    For $\lambda_2 = -3$: $(A + 3I)\mathbf{v} = 0 \implies \begin{pmatrix} 2 & 2 \\ 0 & 0 \end{pmatrix}\mathbf{v} = 0 \implies v_1 = -v_2$. So $\mathbf{v}_2 = \begin{pmatrix} -1 \\ 1 \end{pmatrix}$.

    (b) **General solution:**

    $$\mathbf{x}(t) = c_1 e^{-t}\begin{pmatrix} 1 \\ 0 \end{pmatrix} + c_2 e^{-3t}\begin{pmatrix} -1 \\ 1 \end{pmatrix}.$$

    In component form: $x_1(t) = c_1 e^{-t} - c_2 e^{-3t}$, $x_2(t) = c_2 e^{-3t}$.

    (c) **Stability:** Both eigenvalues have negative real parts ($\lambda_1 = -1$, $\lambda_2 = -3$), so the origin is **asymptotically stable** (a stable node, since both eigenvalues are real and negative).

    (d) **Specific solution with $\mathbf{x}(0) = (4, 2)^T$:**

    $x_2(0) = c_2 = 2$.

    $x_1(0) = c_1 - c_2 = 4 \implies c_1 = 4 + 2 = 6$.

    $$\mathbf{x}(t) = 6e^{-t}\begin{pmatrix} 1 \\ 0 \end{pmatrix} + 2e^{-3t}\begin{pmatrix} -1 \\ 1 \end{pmatrix} = \begin{pmatrix} 6e^{-t} - 2e^{-3t} \\ 2e^{-3t} \end{pmatrix}.$$

    $\square$

---
