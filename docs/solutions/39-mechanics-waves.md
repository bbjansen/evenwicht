<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 39: Classical Mechanics & Waves

**Exercise 39.1.** Free-fall from 45 m.

??? success "Solution"

    Using $x(t) = x_0 - \frac{1}{2}gt^2$ with $x_0 = 45$ m and $g = 9.81$ m/s$^2$:

    At ground: $0 = 45 - \frac{1}{2}(9.81)t^2$, so $t = \sqrt{90/9.81} = \sqrt{9.174} = 3.029$ s.

    Impact velocity: $v = gt = 9.81 \times 3.029 = 29.71$ m/s.

    RK4 simulation with $h = 0.01$ s of $\ddot{x} = -g$ (converted to first-order: $\dot{x} = v$, $\dot{v} = -9.81$) should agree to within $O(h^4) \approx 10^{-8}$ m, confirming exact agreement.

    $\square$

---

**Exercise 39.2.** Spring-mass: $k = 50$ N/m, $m = 2$ kg, $x_0 = 0.08$ m.

??? success "Solution"

    $\omega = \sqrt{k/m} = \sqrt{25} = 5$ rad/s.

    $T = 2\pi/\omega = 2\pi/5 \approx 1.257$ s.

    Maximum velocity: At the equilibrium position, all energy is kinetic. $\frac{1}{2}mv_{\max}^2 = \frac{1}{2}kx_0^2$, so $v_{\max} = x_0\sqrt{k/m} = 0.08 \times 5 = 0.4$ m/s.

    $\square$

---

**Exercise 39.3.** Critically damped oscillator: $\omega = 8$, $\gamma = 8$.

??? success "Solution"

    The companion matrix is:

    $$A = \begin{pmatrix} 0 & 1 \\ -\omega^2 & -2\gamma \end{pmatrix} = \begin{pmatrix} 0 & 1 \\ -64 & -16 \end{pmatrix}.$$

    Eigenvalues: $\lambda^2 + 16\lambda + 64 = 0 \implies (\lambda + 8)^2 = 0 \implies \lambda = -8$ (repeated).

    This confirms critical damping ($\gamma = \omega$).

    General solution: $x(t) = (c_1 + c_2 t)e^{-8t}$.

    From $x(0) = 1$: $c_1 = 1$. From $\dot{x}(0) = 0$: $\dot{x} = (c_2 - 8c_1 - 8c_2 t)e^{-8t}$, so $c_2 - 8 = 0$ gives $c_2 = 8$.

    $$x(t) = (1 + 8t)e^{-8t}.$$

    At $t = 0.5$: $x(0.5) = (1 + 4)e^{-4} = 5 \times 0.01832 = 0.09158$.

    $\square$

---

**Exercise 39.4.** Three coupled masses.

??? success "Solution"

    With wall springs included, the stiffness matrix is:

    $$K = k\begin{pmatrix} 2 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 2 \end{pmatrix}, \quad D = K/m = 10\begin{pmatrix} 2 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 2 \end{pmatrix}.$$

    The eigenvalues of the tridiagonal matrix $\begin{pmatrix} 2 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 2\end{pmatrix}$ are $\lambda_k = 2 - 2\cos(k\pi/4)$ for $k = 1, 2, 3$:

    $\lambda_1 = 2 - 2\cos(\pi/4) = 2 - \sqrt{2} \approx 0.5858$,
    $\lambda_2 = 2 - 2\cos(\pi/2) = 2$,
    $\lambda_3 = 2 - 2\cos(3\pi/4) = 2 + \sqrt{2} \approx 3.4142$.

    Normal mode frequencies: $\omega_k = \sqrt{10\lambda_k}$:

    $\omega_1 = \sqrt{5.858} = 2.420$ rad/s (all masses in phase),
    $\omega_2 = \sqrt{20} = 4.472$ rad/s (middle mass stationary, outer masses in antiphase),
    $\omega_3 = \sqrt{34.14} = 5.843$ rad/s (adjacent masses in antiphase).

    $\square$

---

**Exercise 39.5.** Nonlinear pendulum at $\theta_0 = \pi/2$.

??? success "Solution"

    Equation: $\ddot{\theta} = -(g/l)\sin\theta$ with $g/l = 9.81/0.5 = 19.62$ s$^{-2}$.

    (a) The linear period is $T_{\text{lin}} = 2\pi/\sqrt{g/l} = 2\pi/4.429 = 1.419$ s. For $\theta_0 = \pi/2$, the exact period involves the complete elliptic integral: $T = 4\sqrt{l/g} \cdot K(\sin(\theta_0/2)) = 4 \times 0.2259 \times K(\sin(\pi/4)) = 0.9035 \times K(0.7071)$. $K(0.7071) = 1.8541$, so $T = 0.9035 \times 1.8541 = 1.675$ s, about 18% longer than the linear approximation.

    From zero-crossings in the RK4 simulation, the period should be approximately $1.675$ s.

    (b) With $h = 0.001$ s over 20 s (20000 steps, approximately 12 periods), the relative energy error should be $O(h^4 \times N_{\text{steps}}) \approx 10^{-12} \times 20000 \approx 10^{-8}$.

    (c) With $h = 0.01$ s (a factor-10 increase), the global error per step is $O(h^4) \sim 10^{-8}$ and accumulates over $N = 2000$ steps, giving relative energy error $\sim 10^{-5}$. The ratio $10^{-5}/10^{-8} = 10^3$, consistent with the $O(h^4)$ error scaling: $(0.01/0.001)^4 = 10^4$ per step but $\times 1/10$ fewer steps, giving a net factor of $10^3$.

    $\square$

---

**Exercise 39.6.** Driven oscillator, resonance analysis.

??? success "Solution"

    With $\omega = 5$ rad/s, $\gamma = 0.5$ rad/s, $F_0/m = 10$:

    (a) $\Omega_{\text{res}} = \sqrt{\omega^2 - 2\gamma^2} = \sqrt{25 - 0.5} = \sqrt{24.5} = 4.950$ rad/s.

    $A_{\max} = \frac{F_0/m}{2\gamma\sqrt{\omega^2 - \gamma^2}} = \frac{10}{2 \times 0.5 \times \sqrt{25 - 0.25}} = \frac{10}{1.0 \times 4.975} = 2.010$ m.

    $Q = \omega/(2\gamma) = 5/1 = 5$, half-power bandwidth $\Delta\Omega = \omega/Q = 1$ rad/s.

    (b) The analytical steady-state amplitude is $A(\Omega) = \frac{F_0/m}{\sqrt{(\omega^2 - \Omega^2)^2 + 4\gamma^2\Omega^2}}$:

    - $\Omega = 1$: $A = 10/\sqrt{(24)^2 + 1} = 10/\sqrt{577} = 0.416$ m.
    - $\Omega = 3$: $A = 10/\sqrt{(16)^2 + 9} = 10/\sqrt{265} = 0.614$ m.
    - $\Omega = 4.9$: $A = 10/\sqrt{(0.99)^2 + 24.01} = 10/\sqrt{25} = 2.0$ m.
    - $\Omega = 5$: $A = 10/\sqrt{0 + 25} = 10/5 = 2.0$ m.
    - $\Omega = 7$: $A = 10/\sqrt{(24)^2 + 49} = 10/\sqrt{625} = 0.4$ m.

    The RK4 simulation (after waiting $\sim 20/\gamma = 40$ s for transients to decay) should produce amplitudes matching these to within numerical precision.

    $\square$

---

**Exercise 39.7.** 16-mass string simulation.

??? success "Solution"

    (a) The $16 \times 16$ stiffness matrix is tridiagonal with $K_{ii} = 2\tau/\Delta x$ and $K_{i,i\pm 1} = -\tau/\Delta x$, where $\Delta x = L/(N+1) = 0.5/17$. The eigenvalues of the normalised matrix are $\lambda_k = 2(1 - \cos(k\pi/17))$ for $k = 1, \ldots, 16$. The normal mode frequencies are $\omega_k = 2\sqrt{\tau/(m\Delta x)}\sin(k\pi/(2 \times 17))$.

    With $\tau = 5$ N, $m = 0.005$ kg, $\Delta x = 0.5/17 = 0.02941$ m: $\sqrt{\tau/(m\Delta x)} = \sqrt{5/(0.005 \times 0.02941)} = \sqrt{34000} = 184.4$ rad/s.

    $\omega_k = 2 \times 184.4 \times \sin(k\pi/34)$.

    (b)-(c) Initialising with the third mode and simulating, the FFT of the midpoint time series shows a single peak at $\omega_3$. Adding a 10% second-mode perturbation produces two FFT peaks at $\omega_2$ and $\omega_3$ with approximately 10:1 power ratio (100:1 in power, 10:1 in amplitude).

    $\square$

---

**Exercise 39.8.** Coupled pendulums.

??? success "Solution"

    (a) The dynamical matrix is:

    $$D = \begin{pmatrix} g/l + kd^2/(ml^2) & -kd^2/(ml^2) \\ -kd^2/(ml^2) & g/l + kd^2/(ml^2) \end{pmatrix}.$$

    With $g/l = 9.81$, $kd^2/(ml^2) = 2 \times 0.25/(1 \times 1) = 0.5$:

    $\omega_1^2 = g/l = 9.81$, $\omega_1 = 3.132$ rad/s (symmetric mode).
    $\omega_2^2 = g/l + 2kd^2/(ml^2) = 9.81 + 1.0 = 10.81$, $\omega_2 = 3.290$ rad/s (antisymmetric mode).

    (b) Initial condition $\theta_1(0) = 0.3$, $\theta_2(0) = 0$ excites both modes equally: $\theta_1 = 0.15(\cos\omega_1 t + \cos\omega_2 t)$, $\theta_2 = 0.15(\cos\omega_1 t - \cos\omega_2 t)$.

    Beat frequency: $\Delta\omega = 3.290 - 3.132 = 0.158$ rad/s. Beat period: $T_{\text{beat}} = 2\pi/0.158 = 39.8$ s.

    (c) The FFT of $\theta_1(t)$ shows two peaks of equal amplitude at $\omega_1 = 3.13$ and $\omega_2 = 3.29$ rad/s.

    $\square$

---
