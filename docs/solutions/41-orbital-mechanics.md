<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 41: Orbital Mechanics & Celestial Dynamics

**Exercise 41.1.** ISS orbital period at $h = 420$ km.

??? success "Solution"

    $r = R_{\oplus} + h = 6.371 \times 10^6 + 420 \times 10^3 = 6.791 \times 10^6$ m.

    $$T = 2\pi\sqrt{\frac{r^3}{\mu}} = 2\pi\sqrt{\frac{(6.791 \times 10^6)^3}{3.986 \times 10^{14}}}.$$

    $r^3 = (6.791)^3 \times 10^{18} = 313.4 \times 10^{18} = 3.134 \times 10^{20}$.

    $r^3/\mu = 3.134 \times 10^{20} / 3.986 \times 10^{14} = 7.862 \times 10^5$.

    $T = 2\pi\sqrt{7.862 \times 10^5} = 2\pi \times 886.7 = 5570$ s $= 92.8$ minutes.

    This agrees well with the observed ISS period of approximately 92.5 minutes. (The slight discrepancy reflects the varying ISS altitude and atmospheric drag.)

---

**Exercise 41.2.** Circular orbit at $r = 7000$ km.

??? success "Solution"

    $r = 7.0 \times 10^6$ m.

    $v = \sqrt{\mu/r} = \sqrt{3.986 \times 10^{14} / 7.0 \times 10^6} = \sqrt{5.694 \times 10^7} = 7546$ m/s $= 7.546$ km/s.

    $E = -\mu/(2r) = -3.986 \times 10^{14}/(2 \times 7.0 \times 10^6) = -2.847 \times 10^7$ J/kg.

    Verification: $E = v^2/2 - \mu/r = (7546)^2/2 - 3.986 \times 10^{14}/7.0 \times 10^6 = 2.847 \times 10^7 - 5.694 \times 10^7 = -2.847 \times 10^7$ J/kg. $\checkmark$

    $L = rv = 7.0 \times 10^6 \times 7546 = 5.282 \times 10^{10}$ m$^2$/s.

---

**Exercise 41.3.** Vis-viva at apsides.

??? success "Solution"

    $a = 10{,}000$ km $= 10^7$ m, $e = 0.3$.

    $r_p = a(1-e) = 7 \times 10^6$ m, $r_a = a(1+e) = 1.3 \times 10^7$ m.

    $v_p = \sqrt{\mu(2/r_p - 1/a)} = \sqrt{3.986 \times 10^{14}(2/(7 \times 10^6) - 1/10^7)} = \sqrt{3.986 \times 10^{14} \times 1.857 \times 10^{-7}} = \sqrt{7.402 \times 10^7} = 8604$ m/s.

    $v_a = \sqrt{\mu(2/r_a - 1/a)} = \sqrt{3.986 \times 10^{14}(2/(1.3 \times 10^7) - 10^{-7})} = \sqrt{3.986 \times 10^{14} \times 5.385 \times 10^{-8}} = \sqrt{2.146 \times 10^7} = 4633$ m/s.

    Verify angular momentum conservation: $v_p r_p = 8604 \times 7 \times 10^6 = 6.023 \times 10^{10}$. $v_a r_a = 4633 \times 1.3 \times 10^7 = 6.023 \times 10^{10}$. $\checkmark$

---

**Exercise 41.4.** Hohmann transfer: 300 km to GEO (35,786 km).

??? success "Solution"

    $r_1 = 6371 + 300 = 6671$ km $= 6.671 \times 10^6$ m. $r_2 = 6371 + 35786 = 42157$ km $= 4.216 \times 10^7$ m.

    $a_t = (r_1 + r_2)/2 = 2.441 \times 10^7$ m.

    $v_{c1} = \sqrt{3.986 \times 10^{14}/6.671 \times 10^6} = 7730$ m/s.

    $v_{t1} = \sqrt{3.986 \times 10^{14}(2/(6.671 \times 10^6) - 1/(2.441 \times 10^7))} = \sqrt{3.986 \times 10^{14} \times 2.588 \times 10^{-7}} = \sqrt{1.031 \times 10^8} = 10{,}155$ m/s.

    $\Delta v_1 = 10155 - 7730 = 2425$ m/s.

    $v_{c2} = \sqrt{3.986 \times 10^{14}/4.216 \times 10^7} = 3075$ m/s.

    $v_{t2} = \sqrt{3.986 \times 10^{14}(2/(4.216 \times 10^7) - 1/(2.441 \times 10^7))} = \sqrt{3.986 \times 10^{14} \times 6.364 \times 10^{-9}} = \sqrt{2.537 \times 10^6} \approx 1593$ m/s.

    $\Delta v_2 = 3075 - 1593 = 1482$ m/s.

    Total $\Delta v = 2425 + 1482 = 3907$ m/s. First burn fraction: $2425/3907 = 62.1\%$.

    Transfer time:

    $$\begin{aligned}
    t &= \pi\sqrt{a_t^3/\mu} \\
      &= \pi\sqrt{(2.441 \times 10^7)^3/3.986 \times 10^{14}} \\
      &= \pi\sqrt{3.648 \times 10^7} \\
      &= \pi \times 6040 = 18{,}974 \text{ s} \approx 5.27 \text{ hours.}
    \end{aligned}$$

---

**Exercise 41.5.** Three orbits with $\mu = 1$, $\mathbf{r}_0 = (1, 0)$.

??? success "Solution"

    For $\mathbf{v}_0 = (0, v_0)$:

    $E = v_0^2/2 - 1/r = v_0^2/2 - 1$.

    $v_0 = 0.8$: $E = 0.32 - 1 = -0.68 < 0$. **Bound (ellipse)**. $a = -\mu/(2E) = 1/1.36 = 0.735$. $T = 2\pi\sqrt{a^3} = 2\pi \times 0.631 = 3.963$.

    $v_0 = 1.0$: $E = 0.5 - 1 = -0.5 < 0$. **Bound (circle)**. $a = 1.0$, $T = 2\pi$.

    $v_0 = 1.5$: $E = 1.125 - 1 = 0.125 > 0$. **Unbound (hyperbola)**.

    For $v_0 = 0.8$: simulation over one period $T \approx 3.96$ should return the particle near $\mathbf{r}_0$.

---

**Exercise 41.6.** Sun–Jupiter Lagrange points ($\nu \approx 9.54 \times 10^{-4}$).

??? success "Solution"

    The five Lagrange points in normalised coordinates (Sun at $(-\nu, 0)$, Jupiter at $(1-\nu, 0)$):

    $L_1$: between Sun and Jupiter. Using Hill sphere: $\xi \approx (\nu/3)^{1/3} = (3.18 \times 10^{-4})^{1/3} = 0.0682$. $L_1$ is at $x \approx 1 - \nu - 0.0682 \approx 0.931$. **Unstable** (saddle-point eigenvalues).

    $L_2$: beyond Jupiter. $L_2$ at $x \approx 1 - \nu + 0.0687 \approx 1.068$. **Unstable**.

    $L_3$: opposite side of Sun. $L_3$ at $x \approx -(1 + 5\nu/12) \approx -1.0004$. **Unstable**.

    $L_4$: leading equilateral point at $(0.5 - \nu, \sqrt{3}/2) \approx (0.499, 0.866)$. Since $\nu = 9.54 \times 10^{-4} < 0.0385$, $L_4$ is **stable**. (Trojan asteroids orbit here.)

    $L_5$: trailing equilateral point at $(0.499, -0.866)$. **Stable** (same criterion as $L_4$).

---

**Exercise 41.7.** ISS orbital decay simulation.

??? success "Solution"

    At 420 km, $v_{\text{circ}} = 7660$ m/s and $T \approx 5550$ s. With $B = 0.003$ m$^2$/kg and exponential atmosphere ($H = 58$ km, $\rho_0 \approx 4 \times 10^{-12}$ kg/m$^3$ at 420 km):

    The energy loss per orbit is $\Delta E \approx -\pi \rho B v^2 a$, giving altitude loss per orbit $\Delta h \approx -\pi \rho B v^2 a^2 / \mu \approx -\pi \times 4 \times 10^{-12} \times 0.003 \times (7660)^2 \times (6.791 \times 10^6) / (3.986 \times 10^{14})$. This gives $\Delta h \approx 60$–130 m per orbit initially, accelerating as the ISS descends into denser atmosphere.

    At approximately 200–250 km altitude (where $\rho$ is $\sim 100\times$ larger), the orbit decays rapidly. Without reboost, the ISS would reach 100 km in roughly 1–2 years, depending on solar activity (which affects atmospheric density at these altitudes).

---

**Exercise 41.8.** Sensitive dependence near escape velocity.

??? success "Solution"

    Launching at $0.99 v_{\text{esc}}$ gives $E < 0$ (bound; the spacecraft follows an elliptical orbit and returns). At $1.01 v_{\text{esc}}$: $E > 0$ (unbound; hyperbolic escape). The trajectories in the rotating Sun–Earth frame diverge dramatically despite a 2% difference in initial speed.

    The Lyapunov exponent $\lambda_L$ is estimated from $\lvert\delta\mathbf{r}(t)\rvert \sim \lvert\delta\mathbf{r}(0)\rvert e^{\lambda_L t}$. For nearby trajectories with $\delta v_0 = 0.001 v_{\text{esc}}$, tracking the divergence over time gives $\lambda_L \sim 1/T_{\text{orbit}}$ in the chaotic region near the separatrix. This illustrates the chaotic three-body dynamics that make trajectory design near the Earth-Sun boundary computationally challenging.

---
