<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 43: Fluid Dynamics (Simplified)

**Exercise 43.1.** Reservoir efflux via Bernoulli's equation.

??? success "Solution"

    Bernoulli's equation between the free surface (point 1: $v_1 \approx 0$, $h_1 = 12$ m) and the discharge (point 2: $h_2 = 0$, atmospheric pressure at both):

    $$\frac{1}{2}\rho v_1^2 + \rho g h_1 + p_1 = \frac{1}{2}\rho v_2^2 + \rho g h_2 + p_2.$$

    With $v_1 \approx 0$, $p_1 = p_2$, $h_2 = 0$:

    $$v_2 = \sqrt{2gh} = \sqrt{2 \times 9.81 \times 12} = \sqrt{235.4} = 15.35 \text{ m/s}.$$

    This is Torricelli's law: $v = \sqrt{2gh}$.

    Volumetric flow rate: $Q = Av = 0.005 \times 15.35 = 0.0768$ m$^3$/s $= 76.8$ L/s.

---

**Exercise 43.2.** Reynolds number.

??? success "Solution"

    $\text{Re} = \rho v D / \mu$.

    Water: $\text{Re} = 1000 \times 2 \times 0.05 / 10^{-3} = 100{,}000$. **Turbulent** ($\text{Re} \gg 2300$).

    Glycerin: $\text{Re} = 1260 \times 2 \times 0.05 / 1.5 = 84.0$. **Laminar** ($\text{Re} \ll 2300$).

---

**Exercise 43.3.** Poiseuille flow.

??? success "Solution"

    $R = D/2 = 0.05$ m, $L = 50$ m, $\Delta P = 500$ Pa, $\mu = 10^{-3}$ Pa$\cdot$s.

    (a) $Q = \pi R^4 \Delta P / (8\mu L) = \pi (0.05)^4 \times 500 / (8 \times 10^{-3} \times 50) = \pi \times 6.25 \times 10^{-6} \times 500 / 0.4 = \pi \times 7.813 \times 10^{-3} = 0.02454$ m$^3$/s.

    (b) $v_{\max} = 2Q/(\pi R^2) = 2 \times 0.02454 / (\pi \times 0.0025) = 0.04908 / 0.007854 = 6.25$ m/s.

    (c) $v_{\text{mean}} = Q/(\pi R^2) = 0.02454 / 0.007854 = 3.125$ m/s.

    (d) $\text{Re} = \rho v_{\text{mean}} D / \mu = 1000 \times 3.125 \times 0.1 / 10^{-3} = 312{,}500$.

    (e) Since $\text{Re} = 312{,}500 \gg 2300$, the Poiseuille solution is **not valid** for this flow. The flow would be turbulent, and the Hagen–Poiseuille formula underestimates the actual pressure drop required (or overestimates the flow rate for the given pressure drop).

---

**Exercise 43.4.** Stokes drag: steel ball in motor oil.

??? success "Solution"

    $r = 2 \times 10^{-3}$ m. Volume: $V = (4/3)\pi r^3 = 3.351 \times 10^{-8}$ m$^3$.

    Buoyancy-corrected mass: $m' = V(\rho_s - \rho_f) = 3.351 \times 10^{-8} \times (7800 - 880) = 3.351 \times 10^{-8} \times 6920 = 2.319 \times 10^{-4}$ kg.

    Stokes drag coefficient: $b = 6\pi\mu r = 6\pi \times 0.3 \times 0.002 = 0.01131$ kg/s.

    Terminal velocity: $v_t = m'g/b = 2.319 \times 10^{-4} \times 9.81 / 0.01131 = 0.2011$ m/s.

    Time constant: $\tau = m'/b = 2.319 \times 10^{-4} / 0.01131 = 0.02051$ s.

    The velocity approaches $v_t$ as $v(t) = v_t(1 - e^{-t/\tau})$. At $t = \ln(100)\tau = 4.605\tau = 0.0944$ s, the velocity first exceeds $99\%$ of $v_t$.

---

**Exercise 43.5.** 1D diffusion eigenmode decay.

??? success "Solution"

    The exact decay rate for the mode $c(x,t) = \sin(\pi x)e^{-D\pi^2 t}$ is $\sigma_1 = D\pi^2 = 10^{-4} \times 9.8696 = 9.870 \times 10^{-4}$ s$^{-1}$ (matching the notation of Corollary 43.18).

    The discrete Laplacian's first eigenvalue on $N$ interior points with spacing $h = 1/(N+1)$ gives the discrete decay rate $\sigma_1^{(N)} = (2D/h^2)(1 - \cos(\pi h)) \approx D\pi^2(1 - \pi^2 h^2/12)$.

    Relative error: $|\sigma_1^{(N)} - \sigma_1|/\sigma_1 \approx \pi^2/(12(N+1)^2)$.

    $N = 10$: $h = 1/11$, error $\approx \pi^2/(12 \times 121) = 0.0068$ (0.68%).
    $N = 50$: $h = 1/51$, error $\approx \pi^2/(12 \times 2601) = 0.000316$ (0.032%).
    $N = 200$: $h = 1/201$, error $\approx \pi^2/(12 \times 40401) = 2.03 \times 10^{-5}$ (0.002%).

    The error decreases as $O(1/N^2)$, confirming the second-order accuracy of the central difference scheme.

---

**Exercise 43.6.** Water hammer frequencies.

??? success "Solution"

    Exact continuum frequencies: $\omega_k = k\pi a/L = k\pi \times 1400/100 = 14k\pi$ rad/s. In Hz: $f_k = 7k$ Hz.

    $f_1 = 7$ Hz, $f_2 = 14$ Hz, $f_3 = 21$ Hz.

    Discrete: with $N = 50$ interior points, $\Delta x = 100/51 = 1.9608$ m. Discrete eigenvalues: $\omega_k^{(N)} = (2a/\Delta x)\sin(k\pi/(2(N+1)))$. For $k = 1$: $\omega_1^{(N)} = (2 \times 1400/1.9608)\sin(\pi/102) = 1428.0 \times 0.03081 = 43.98$ rad/s, $f_1^{(N)} = 7.00$ Hz. Agreement is excellent for low modes.

---

**Exercise 43.7.** Convection-diffusion.

??? success "Solution"

    Analytical solution with boundary conditions $c(0) = 1$, $c(1) = 0$:

    $$c(x) = \frac{e^{\text{Pe}\,x} - e^{\text{Pe}}}{1 - e^{\text{Pe}}}.$$

    For Pe $= 1$: gradual exponential profile from 1 to 0. Pe $= 10$: concentration stays near 1 until a thin boundary layer near $x = 1$. Pe $= 100$: extremely thin boundary layer of width $\sim 1/\text{Pe} = 0.01$.

    **Note on numerical behaviour.** Numerical solutions with central differences develop spurious oscillations at high Pe unless upwind differencing or sufficient grid refinement is used.

---

**Exercise 43.8.** Turbulence spectrum slope estimation.

??? success "Solution"

    Generate $N$ samples with PSD $\propto f^{-5/3}$ in the inertial subrange (10–500 Hz). Estimate the slope from the regression of $\log P(f)$ vs. $\log f$ over the inertial subrange.

    For $N = 8192$: the frequency resolution is $\Delta f = 2000/8192 \approx 0.244$ Hz, giving $\sim 2000$ points in the inertial subrange. Over 100 realisations, the mean slope should be approximately $-1.667$ with standard deviation decreasing as $O(1/\sqrt{N_f})$ where $N_f$ is the number of frequency bins.

    Expected results:
    - $N = 512$: slope $\approx -1.67 \pm 0.15$
    - $N = 1024$: slope $\approx -1.67 \pm 0.10$
    - $N = 8192$: slope $\approx -1.667 \pm 0.03$

    Varying the inertial subrange bounds (e.g., 5–600 vs. 20–400 Hz) affects the estimate by $\sim 5\%$ due to contamination from white noise outside the true inertial range.

---
