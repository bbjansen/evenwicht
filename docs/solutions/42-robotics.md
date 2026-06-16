<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 42: Robotics & Kinematics

**Exercise 42.1.** 3-link planar arm at $\boldsymbol{\theta} = (\pi/6, \pi/4, \pi/3)$.

??? success "Solution"

    $x = l_1\cos\theta_1 + l_2\cos(\theta_1 + \theta_2) + l_3\cos(\theta_1 + \theta_2 + \theta_3)$.

    $\theta_1 = \pi/6$, $\theta_1 + \theta_2 = \pi/6 + \pi/4 = 5\pi/12$, $\theta_1 + \theta_2 + \theta_3 = 5\pi/12 + \pi/3 = 3\pi/4$.

    $$\begin{aligned}
    x &= 1.0\cos(\pi/6) + 0.7\cos(5\pi/12) + 0.4\cos(3\pi/4) \\
      &= 1.0 \times 0.8660 + 0.7 \times 0.2588 + 0.4 \times (-0.7071) \\
      &= 0.8660 + 0.1812 - 0.2828 = 0.7644.
    \end{aligned}$$

    $$\begin{aligned}
    y &= 1.0\sin(\pi/6) + 0.7\sin(5\pi/12) + 0.4\sin(3\pi/4) \\
      &= 1.0 \times 0.5000 + 0.7 \times 0.9659 + 0.4 \times 0.7071 \\
      &= 0.5000 + 0.6761 + 0.2828 = 1.4590.
    \end{aligned}$$

    End-effector position: $(0.764, 1.459)$.

---

**Exercise 42.2.** Numerical vs. analytical Jacobian at $\theta_1 = \pi/3$, $\theta_2 = \pi/6$.

??? success "Solution"

    Analytical (Theorem 42.10) with $l_1 = 1.0$, $l_2 = 0.8$:

    $\theta_1 + \theta_2 = \pi/2$.

    $J_{11} = -l_1\sin\theta_1 - l_2\sin(\pi/2) = -0.8660 - 0.8 = -1.6660$

    $J_{12} = -l_2\sin(\pi/2) = -0.8$

    $J_{21} = l_1\cos\theta_1 + l_2\cos(\pi/2) = 0.5 + 0 = 0.5$

    $J_{22} = l_2\cos(\pi/2) = 0$

    $$J = \begin{pmatrix} -1.6660 & -0.8000 \\ 0.5000 & 0.0000 \end{pmatrix}.$$

    Numerical with $h = 10^{-7}$: central differences on FK yield the same values to at least 8 significant digits, e.g., $J_{11} \approx -1.6660254$ (analytical) vs. $-1.6660254$ (numerical). The agreement is limited by the $O(h^2) \sim 10^{-14}$ truncation error plus $O(\varepsilon/h) \sim 10^{-9}$ roundoff, giving about 9 digits of accuracy.

---

**Exercise 42.3.** Workspace boundary for $l_1 = 1.5$, $l_2 = 1.0$.

??? success "Solution"

    Inner radius: $r_{\min} = l_1 - l_2 = 0.5$. Outer radius: $r_{\max} = l_1 + l_2 = 2.5$.

    The workspace is the annulus $\{(x,y) : 0.5 \leq \sqrt{x^2 + y^2} \leq 2.5\}$.

    Area: $\pi(R^2 - r^2) = \pi(6.25 - 0.25) = 6\pi \approx 18.85$ square units.

---

**Exercise 42.4.** Two IK solutions for $\mathbf{p}^* = (1.0, 0.5)$ with $l_1 = l_2 = 1.0$.

??? success "Solution"

    $\|\mathbf{p}^*\| = \sqrt{1.25} = 1.118$. Since $0 \leq 1.118 \leq 2$, the target is reachable.

    Analytically: $\cos\theta_2 = (x^2 + y^2 - l_1^2 - l_2^2)/(2l_1 l_2) = (1.25 - 2)/2 = -0.375$.

    $\theta_2 = \pm\arccos(-0.375) = \pm 1.955$ rad.

    For $\theta_2 = +1.955$ (elbow-up): $\theta_1 = \operatorname{atan2}(y, x) - \operatorname{atan2}(l_2\sin\theta_2, l_1 + l_2\cos\theta_2) = \operatorname{atan2}(0.5, 1.0) - \operatorname{atan2}(0.9270, 0.625) = 0.4636 - 0.9769 = -0.5133$ rad.

    For $\theta_2 = -1.955$ (elbow-down): $\theta_1 = 0.4636 + 0.9769 = 1.4405$ rad.

    Newton's method from $(0.5, 1.0)$ converges to $(\theta_1, \theta_2) \approx (-0.513, 1.955)$. From $(0.5, -1.0)$ it converges to $(\theta_1, \theta_2) \approx (1.441, -1.955)$.

    Both verify: FK$(\boldsymbol{\theta}) = (1.0, 0.5)$.

---

**Exercise 42.5.** Damped least-squares through singularity.

??? success "Solution"

    Tracing from $(1.0, 0.0)$ to $(1.8, 0.0)$ passes through the singular extended configuration at $r = l_1 + l_2 = 1.8$ where $\theta_2 = 0$ and $\det(J) = l_1 l_2 \sin\theta_2 = 0$.

    Without damping, $J^{-1}$ diverges as $\theta_2 \to 0$, causing large erratic joint angle updates.

    With damping ($\lambda = 0.05$): $\Delta\boldsymbol{\theta} = J^T(JJ^T + 0.0025 I)^{-1}\mathbf{e}$. Near the singularity, the damping term dominates, producing a smooth, bounded joint trajectory that passes through the singular configuration without divergence. The trade-off is that the end-effector may not reach exactly $(1.8, 0.0)$; the path deviates slightly because the damped solution sacrifices accuracy for stability.

---

**Exercise 42.6.** Quintic trajectory.

??? success "Solution"

    $\theta(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5$ with six conditions at $t = 0$ and $t = 2$:

    $\theta(0) = 0$: $a_0 = 0$.
    $\dot{\theta}(0) = 0$: $a_1 = 0$.
    $\ddot{\theta}(0) = 0$: $a_2 = 0$.
    $\theta(2) = \pi/2$: $8a_3 + 16a_4 + 32a_5 = \pi/2$.
    $\dot{\theta}(2) = 0$: $12a_3 + 32a_4 + 80a_5 = 0$.
    $\ddot{\theta}(2) = 0$: $12a_3 + 48a_4 + 160a_5 = 0$.

    From the last two: subtracting gives $16a_4 + 80a_5 = 0$, so $a_4 = -5a_5$.

    Substituting into $\dot{\theta}(2) = 0$: $12a_3 + 32(-5a_5) + 80a_5 = 12a_3 - 80a_5 = 0$, so $a_3 = 20a_5/3$.

    Into $\theta(2)$: $8(20a_5/3) + 16(-5a_5) + 32a_5 = 160a_5/3 - 80a_5 + 32a_5 = 160a_5/3 - 48a_5 = (160 - 144)a_5/3 = 16a_5/3 = \pi/2$.

    $a_5 = 3\pi/32$, $a_4 = -15\pi/32$, $a_3 = 20\pi/32 = 5\pi/8$.

    $$\theta(t) = \frac{5\pi}{8}t^3 - \frac{15\pi}{32}t^4 + \frac{3\pi}{32}t^5.$$

    At $t = 1$: $\theta(1) = 5\pi/8 - 15\pi/32 + 3\pi/32 = 20\pi/32 - 15\pi/32 + 3\pi/32 = 8\pi/32 = \pi/4$. The quintic has continuous acceleration at the endpoints (zero jerk), producing smoother actuator commands than the cubic.

---

**Exercise 42.7.** Energy analysis of the PID-controlled pendulum.

??? success "Solution"

    Total energy: $E(t) = \frac{1}{2}ml^2\dot{\theta}^2 + mgl\sin\theta$ (where $V = mgl\sin\theta$ follows from $g(\theta) = \partial V/\partial\theta = mgl\cos\theta$).

    At $t = 0$: $\theta = 0$ (horizontal), $\dot{\theta} = 0$. $E(0) = 0 + mgl\sin(0) = 0$ J.

    At equilibrium $\theta = \pi/4$: $E_{\text{eq}} = 0 + mgl\sin(\pi/4) = 9.81 \times 0.7071 = 6.937$ J.

    The PID controller does work on the arm. Initially, the controller accelerates the arm upward (adding kinetic energy). At the target angle, the arm overshoots and oscillates, with the derivative term dissipating energy through a braking torque (proportional to $-K_d\dot{\theta}$) that dissipates kinetic energy. The controller adds approximately $6.94$ J of potential energy to raise the arm from horizontal to $\pi/4$. The integral term of the PID supplies the steady-state torque $\tau_{\text{ss}} = mgl\cos(\pi/4) \approx 6.94$ N$\cdot$m needed to hold the arm against gravity. The energy plot shows an initial transient (overshoot/oscillation) settling to the final potential energy level.

---

**Exercise 42.8.** 3-DOF planar arm Jacobian rank.

??? success "Solution"

    The $2 \times 3$ Jacobian for a 3-link planar arm is:

    $$J = \begin{pmatrix} -l_1 s_1 - l_2 s_{12} - l_3 s_{123} & -l_2 s_{12} - l_3 s_{123} & -l_3 s_{123} \\ l_1 c_1 + l_2 c_{12} + l_3 c_{123} & l_2 c_{12} + l_3 c_{123} & l_3 c_{123} \end{pmatrix}$$

    where $s_1 = \sin\theta_1$, $s_{12} = \sin(\theta_1 + \theta_2)$, etc.

    At a generic configuration, $\operatorname{rank}(J) = 2$: the arm can move the end-effector in both $x$ and $y$ directions.

    When all links are collinear ($\theta_2 = \theta_3 = 0$): every column of $J$ is proportional to $(-\sin\theta_1, \cos\theta_1)^T$, so $\operatorname{rank}(J) = 1$. The end-effector can only move tangentially, not radially.

    The pseudoinverse solution $\Delta\boldsymbol{\theta} = J^T(JJ^T)^{-1}\mathbf{e}$ distributes the motion across all three joints, choosing the minimum-norm joint displacement. The extra degree of freedom (the null space of $J$, one-dimensional) allows reconfiguration of the arm without moving the end-effector. This is used in practice to avoid obstacles or singularities.

---
