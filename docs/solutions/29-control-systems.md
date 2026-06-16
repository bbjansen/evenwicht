<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 29: Control Systems

**Exercise 29.1.** Eigenvalues and stability of $A = \begin{bmatrix} 0 & 1 \\ -6 & -5 \end{bmatrix}$.

??? success "Solution"

    Characteristic polynomial: $\det(A - \lambda I) = \lambda^2 + 5\lambda + 6 = (\lambda + 2)(\lambda + 3) = 0$.

    Eigenvalues: $\lambda_1 = -2$, $\lambda_2 = -3$.

    Both eigenvalues are real and negative, so the system $\dot{\mathbf{x}} = A\mathbf{x}$ is *asymptotically stable*. Since both eigenvalues are real and distinct (no imaginary part), the equilibrium is a *stable node* (not a spiral). Trajectories decay exponentially without oscillation; the dominant mode decays as $e^{-2t}$ and the faster mode as $e^{-3t}$.

    $\square$

---

**Exercise 29.2.** Transfer function of $3\ddot{y} + 7\dot{y} + 2y = 5u$.

??? success "Solution"

    Taking the Laplace transform (zero initial conditions): $3s^2 Y(s) + 7sY(s) + 2Y(s) = 5U(s)$.

    $$G(s) = \frac{Y(s)}{U(s)} = \frac{5}{3s^2 + 7s + 2}.$$

    **Poles:** $3s^2 + 7s + 2 = 0 \Rightarrow s = \frac{-7 \pm \sqrt{49 - 24}}{6} = \frac{-7 \pm 5}{6}$. So $s_1 = -1/3$ and $s_2 = -2$.

    Both poles are negative real, so the system is **stable**.

    **Steady-state gain:** $G(0) = 5/2 = 2.5$.

    $\square$

---

**Exercise 29.3.** Discrete-time step response.

??? success "Solution"

    $x_{k+1} = 0.8 x_k + 0.2 u_k$, $y_k = x_k$, with $u_k = 1$ for all $k \geq 0$ and $x_0 = 0$.

    The state evolves as $x_{k+1} = 0.8 x_k + 0.2$. At steady state, $x_{ss} = 0.8 x_{ss} + 0.2$, giving $x_{ss} = 0.2/0.2 = 1.0$.

    | $k$ | $x_k$ |
    |------|---------|
    | 0 | 0.0000 |
    | 1 | 0.2000 |
    | 2 | 0.3600 |
    | 3 | 0.4880 |
    | 4 | 0.5904 |
    | 5 | 0.6723 |
    | 6 | 0.7379 |
    | 7 | 0.7903 |
    | 8 | 0.8322 |
    | 9 | 0.8658 |
    | 10 | 0.8926 |

    The output converges to $y_{ss} = 1.0$.

    $\square$

---

**Exercise 29.4.** Controllability check.

??? success "Solution"

    $A = \begin{bmatrix} 0 & 1 \\ -6 & -5 \end{bmatrix}$, $B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$.

    $AB = \begin{bmatrix} 0 & 1 \\ -6 & -5 \end{bmatrix}\begin{bmatrix} 0 \\ 1 \end{bmatrix} = \begin{bmatrix} 1 \\ -5 \end{bmatrix}$.

    $\mathcal{C} = [B \quad AB] = \begin{bmatrix} 0 & 1 \\ 1 & -5 \end{bmatrix}$.

    $\det(\mathcal{C}) = 0 \times (-5) - 1 \times 1 = -1 \neq 0$.

    The rank is 2 (full rank for a $2 \times 2$ matrix), so the system is **controllable**. $\square$

---

**Exercise 29.5.** PID design for $G(s) = 10/(s^2+3s+2) = 10/((s+1)(s+2))$.

??? success "Solution"

    **State-space (controllable canonical form):** $\dot{x}_1 = x_2$, $\dot{x}_2 = -2x_1 - 3x_2 + 10u$, $y = x_1$. In matrix form: $A = \begin{bmatrix} 0 & 1 \\ -2 & -3 \end{bmatrix}$, $B = \begin{bmatrix} 0 \\ 10 \end{bmatrix}$, $C = [1\ 0]$.

    **PID controller:** $C(s) = K_p + K_i/s + K_d s$. The closed-loop transfer function is $T(s) = C(s)G(s)/(1+C(s)G(s))$.

    For the Ziegler–Nichols method, the first step is to find the ultimate gain $K_u$ and ultimate period $T_u$. With $C(s) = K_p$ only, the closed-loop characteristic equation is $s^2 + 3s + 2 + 10K_p = 0$. For marginal stability (imaginary roots): $s = j\omega$ gives $-\omega^2 + 3j\omega + 2 + 10K_p = 0$. Real part: $-\omega^2 + 2 + 10K_p = 0$; Imaginary part: $3\omega = 0$, so $\omega = 0$, which implies there is no sustained oscillation for any finite $K_p$ (the system is always stable under proportional control since the root locus stays in the left half-plane). Ziegler–Nichols oscillation method does not directly apply.

    Instead, use analytical tuning. The plant has DC gain $G(0) = 10/2 = 5$. Choose $K_p = 0.6$, $K_i = 0.3$, $K_d = 0.1$, giving $C(s) = (0.1s^2 + 0.6s + 0.3)/s$. The closed-loop characteristic polynomial is $s(s^2 + 3s + 2) + 10(0.1s^2 + 0.6s + 0.3) = s^3 + 4s^2 + 8s + 3$. By the Routh–Hurwitz criterion, all coefficients are positive and $4 \times 8 = 32 > 1 \times 3$, so the closed-loop is stable. Numerical root-finding gives poles at approximately $s \approx -0.44$ and $s \approx -1.78 \pm 1.72j$. From the dominant complex pair: $\omega_n \approx 2.48$, $\zeta \approx 0.72$, giving overshoot $\approx e^{-\pi\zeta/\sqrt{1-\zeta^2}} \approx 3.8\%$ (< 20%) and settling time $\approx 4/(\zeta\omega_n) \approx 2.2$ s.

    $\square$

---

**Exercise 29.6.** Controllability, observability and open-loop poles of a 3rd-order system.

??? success "Solution"

    $A = \begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & 1 \\ -2 & -4 & -3 \end{bmatrix}$, $B = \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix}$, $C = [1\ 0\ 0]$.

    **Controllability:** $\mathcal{C} = [B\ \ AB\ \ A^2B]$.
    $AB = \begin{bmatrix} 0 \\ 1 \\ -3 \end{bmatrix}$, $A^2B = A(AB) = \begin{bmatrix} 1 \\ -3 \\ 7 \end{bmatrix}$.

    $\mathcal{C} = \begin{bmatrix} 0 & 0 & 1 \\ 0 & 1 & -3 \\ 1 & -3 & 7 \end{bmatrix}$. $\det(\mathcal{C}) = 0(7-9) - 0(0+3) + 1(0-1) = -1 \neq 0$. Rank 3: **controllable**. $\checkmark$

    **Observability:** $\mathcal{O} = [C'\ \ (CA)'\ \ (CA^2)']'$.
    $CA = [0\ 1\ 0]$, $CA^2 = [0\ 0\ 1]$.

    $\mathcal{O} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix} = I_3$. Rank 3: **observable**. $\checkmark$

    **Open-loop poles:** $\det(sI - A) = s^3 + 3s^2 + 4s + 2 = 0$. Testing $s = -1$: $-1+3-4+2 = 0$. So $(s+1)$ is a factor: $s^3+3s^2+4s+2 = (s+1)(s^2+2s+2) = 0$. The remaining roots: $s = (-2 \pm \sqrt{4-8})/2 = -1 \pm j$.

    Poles: $s = -1$, $s = -1+j$, $s = -1-j$. All have negative real parts; the open-loop system is stable.

    $\square$

---

**Exercise 29.7.** LQR for the double integrator.

??? success "Solution"

    $A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$, $B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$, $Q = I_2$, $R = 1$.

    The CARE is $A'P + PA - PBR^{-1}B'P + Q = 0$, i.e.,

    $$A'P + PA - PBB'P + I = 0.$$

    Let $P = \begin{bmatrix} p_{11} & p_{12} \\ p_{12} & p_{22} \end{bmatrix}$. Then $BB' = \begin{bmatrix} 0 & 0 \\ 0 & 1 \end{bmatrix}$ and $PBB'P = \begin{bmatrix} p_{12}^2 & p_{12}p_{22} \\ p_{12}p_{22} & p_{22}^2 \end{bmatrix}$.

    $A'P = \begin{bmatrix} 0 & 0 \\ p_{11} & p_{12} \end{bmatrix}$, $PA = \begin{bmatrix} 0 & p_{11} \\ 0 & p_{12} \end{bmatrix}$.

    The CARE becomes:

    $(1,1)$: $-p_{12}^2 + 1 = 0 \Rightarrow p_{12} = 1$ (taking positive root).

    $(1,2)$: $p_{11} - p_{12}p_{22} = 0 \Rightarrow p_{11} = p_{22}$.

    $(2,2)$: $2p_{12} - p_{22}^2 + 1 = 0 \Rightarrow p_{22}^2 = 3 \Rightarrow p_{22} = \sqrt{3}$.

    So $p_{11} = \sqrt{3}$, $p_{12} = 1$, $p_{22} = \sqrt{3}$.

    $$P = \begin{bmatrix} \sqrt{3} & 1 \\ 1 & \sqrt{3} \end{bmatrix}.$$

    Optimal gain: $K = R^{-1}B'P = [0\ 1]\begin{bmatrix}\sqrt{3} & 1 \\ 1 & \sqrt{3}\end{bmatrix} = [1,\ \sqrt{3}] \approx [1.000,\ 1.732]$.

    The optimal control law is $u = -Kx = -(x_1 + \sqrt{3}\,x_2)$.

    $\square$

---

**Exercise 29.8.** Uncontrollable system.

??? success "Solution"

    $A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$, $B = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$.

    $AB = \begin{bmatrix} 0 \\ 0 \end{bmatrix}$. $\mathcal{C} = [B\ \ AB] = \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix}$.

    $\operatorname{rank}(\mathcal{C}) = 1 < 2$. The system is **not controllable**.

    **Physical interpretation:** The state equation is $\dot{x}_1 = x_2 + u$ and $\dot{x}_2 = 0$. The input $u$ directly affects $x_1$ but has no influence on $x_2$ whatsoever. The second state $x_2$ is completely autonomous ($x_2(t) = x_2(0)$ for all $t$). If $x_2(0) \neq 0$, no control input can drive $x_2$ to zero.

    **Controllable/uncontrollable decomposition:** The controllable subspace is $\operatorname{span}\{B\} = \operatorname{span}\{(1,0)'\}$, i.e., the $x_1$-axis. The uncontrollable subspace is $\operatorname{span}\{(0,1)'\}$, the $x_2$-axis. The coordinates $x_1$ and $x_2$ already reveal this decomposition: $x_1$ is the controllable state, $x_2$ is uncontrollable. No change of coordinates is needed.

    $\square$

---
