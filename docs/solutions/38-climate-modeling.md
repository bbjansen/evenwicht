<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 38: Climate & Environmental Modelling

**Exercise 38.1.** Venus: $S = 2601$ $\text{W m}^{-2}$, $\alpha = 0.77$. Compute equilibrium temperature for $\varepsilon = 1$ and find effective emissivity for $T = 737$ K.

??? success "Solution"

    With $\varepsilon = 1$ (no greenhouse):

    $$T^* = \left[\frac{S(1-\alpha)}{4\sigma}\right]^{1/4} = \left[\frac{2601 \times 0.23}{4 \times 5.67 \times 10^{-8}}\right]^{1/4} = \left[\frac{598.23}{2.268 \times 10^{-7}}\right]^{1/4} = [2.638 \times 10^9]^{1/4}.$$

    $\sqrt{2.638 \times 10^9} = 51380$, $\sqrt{51380} = 226.7$ K. So the bare equilibrium temperature of Venus is approximately $227$ K ($-46^\circ$C).

    For the observed $T = 737$ K, the effective emissivity is:

    $$\varepsilon = \frac{S(1-\alpha)}{4\sigma T^4} = \frac{598.23}{4 \times 5.67 \times 10^{-8} \times 737^4}.$$

    $737^4 = (737^2)^2 = (543169)^2 = 2.950 \times 10^{11}$.

    $$\varepsilon = \frac{598.23}{4 \times 5.67 \times 10^{-8} \times 2.950 \times 10^{11}} = \frac{598.23}{66896} \approx 0.00894.$$

    **Interpretation:** Venus has $\varepsilon \approx 0.009$, meaning its atmosphere traps over 99% of the thermal radiation the surface would emit. This extreme greenhouse effect (compared to Earth's $\varepsilon \approx 0.61$) is caused by a dense $\text{CO}_2$ atmosphere (${\sim}96.5\%$ $\text{CO}_2$ at 92 bar surface pressure) with sulfuric acid clouds. The 510 K difference between the bare and observed temperatures illustrates runaway greenhouse warming.

    $\square$

---

**Exercise 38.2.** Relaxation timescale and volcanic cooling recovery.

??? success "Solution"

    The relaxation timescale is:

    $$\tau = \frac{C}{4\varepsilon\sigma(T^*)^3} = \frac{4.2 \times 10^8}{4 \times 0.61 \times 5.67 \times 10^{-8} \times 288^3}.$$

    $288^3 = 2.389 \times 10^7$. The denominator is $4 \times 0.61 \times 5.67 \times 10^{-8} \times 2.389 \times 10^7 = 3.306$ $\text{W m}^{-2}\text{K}^{-1}$.

    $$\tau = \frac{4.2 \times 10^8}{3.306} = 1.270 \times 10^8 \text{ s} \approx 4.03 \text{ years}.$$

    For a 0.5 K cooling, the temperature deficit decays as $\delta T(t) = -0.5 \, e^{-t/\tau}$. Recovery of 90% means $\lvert\delta T(t)\rvert = 0.05$ K, so:

    $$e^{-t/\tau} = 0.1 \implies t = \tau \ln 10 = 4.03 \times 2.303 \approx 9.28 \text{ years}.$$

    It takes approximately 9.3 years to recover 90% of a volcanic cooling perturbation of 0.5 K.

    $\square$

---

**Exercise 38.3.** Radiative forcing and equilibrium warming.

??? success "Solution"

    Using $F = 5.35\ln(C/C_0)$ and equilibrium sensitivity $\Delta T_{2\times} = 3^\circ$C (so $\lambda_{\text{eff}} = 3/F_{2\times} = 3/3.71 = 0.808$ $^\circ$C/(W m$^{-2}$)):

    (a) 50% increase: $C/C_0 = 1.5$. $F = 5.35 \ln 1.5 = 5.35 \times 0.4055 = 2.17$ $\text{W m}^{-2}$. $\Delta T = 0.808 \times 2.17 = 1.75^\circ$C.

    (b) Tripling: $C/C_0 = 3$. $F = 5.35 \ln 3 = 5.35 \times 1.0986 = 5.88$ $\text{W m}^{-2}$. $\Delta T = 0.808 \times 5.88 = 4.75^\circ$C.

    (c) 280 ppm to 420 ppm: $C/C_0 = 420/280 = 1.5$. Same as (a): $F = 2.17$ $\text{W m}^{-2}$, $\Delta T = 1.75^\circ$C.

    Note: the current forcing from pre-industrial to 420 ppm is 2.17 W/m$^2$, implying an equilibrium warming of 1.75$^\circ$C. Since the observed warming is about 1.3$^\circ$C (as of 2024), the climate system has not yet equilibrated due to the ocean's thermal inertia.

    $\square$

---

**Exercise 38.4.** Two-box carbon cycle.

??? success "Solution"

    The transfer matrix is:

    $$A = \begin{pmatrix} -k_{ao} & k_{oa} \\ k_{ao} & -k_{oa} \end{pmatrix} = \begin{pmatrix} -0.02 & 0.002 \\ 0.02 & -0.002 \end{pmatrix}.$$

    The eigenvalues satisfy $\det(A - \lambda I) = 0$:

    $$\begin{aligned}
    (-0.02 - \lambda)(-0.002 - \lambda) - (0.002)(0.02) &= 0, \\
    \lambda^2 + 0.022\lambda + 0.00004 - 0.00004 &= 0, \\
    \lambda^2 + 0.022\lambda &= 0, \\
    \lambda(\lambda + 0.022) &= 0.
    \end{aligned}$$

    The eigenvalues are $\lambda_1 = 0$ (conservation of total carbon) and $\lambda_2 = -0.022$ yr$^{-1}$.

    The adjustment timescale is $\tau = 1/0.022 \approx 45.5$ years.

    If 100 GtC is added instantaneously to the atmosphere, the perturbation decays exponentially toward the new equilibrium partition. In the two-box model, the atmosphere eventually retains a fraction $k_{oa}/(k_{ao} + k_{oa}) = 0.002/0.022 = 9.09\%$ of the pulse.

    The atmospheric fraction at time $t$ is:

    $$\frac{C_a(t) - C_a^*}{100} = \frac{k_{ao}}{k_{ao}+k_{oa}}e^{-0.022t} + \frac{k_{oa}}{k_{ao}+k_{oa}}.$$

    This gives $C_a(t)/100 = 0.9091 \, e^{-0.022t} + 0.0909$.

    After 100 years: $0.9091 \, e^{-2.2} + 0.0909 = 0.9091 \times 0.1108 + 0.0909 = 0.1007 + 0.0909 = 0.192$. About $19.2\%$ of the 100 GtC remains in the atmosphere (19.2 GtC).

    After 500 years: $0.9091 \, e^{-11} + 0.0909 = 0.9091 \times 1.67 \times 10^{-5} + 0.0909 \approx 0.0909$. About $9.1\%$ remains (9.1 GtC), the equilibrium partition.

    $\square$

---

**Exercise 38.5.** EBM with ice-albedo feedback, graphical analysis.

??? success "Solution"

    The equilibria are the intersections of $g(T) = S(1 - \alpha(T))/4$ and $h(T) = \varepsilon\sigma T^4$.

    For $S = 1361$ W/m$^2$, using $\alpha_i = 0.65$, $\alpha_w = 0.30$, $T_i = 260$ K, $T_w = 290$ K, $\varepsilon = 0.61$:

    - For $T \leq 260$ K: $g(T) = 1361 \times 0.35/4 = 119.1$ W/m$^2$ (constant).
    - For $T \geq 290$ K: $g(T) = 1361 \times 0.70/4 = 238.2$ W/m$^2$ (constant).
    - For $260 < T < 290$ K: $g(T)$ increases linearly from 119.1 to 238.2.

    Meanwhile $h(T) = 0.61 \times 5.67 \times 10^{-8} \times T^4$:
    - $h(260) = 0.61 \times 5.67 \times 10^{-8} \times 260^4 = 0.61 \times 5.67 \times 10^{-8} \times 4.570 \times 10^9 = 158.0$ W/m$^2$.
    - $h(290) = 0.61 \times 5.67 \times 10^{-8} \times 290^4 = 244.9$ W/m$^2$.

    At $S = 1361$: The curves $g$ and $h$ intersect three times: once in the cold region (near $T \approx 232$ K, the "Snowball Earth" state), once in the transition zone (unstable) and once in the warm region (near $T \approx 288$ K, the current climate).

    At $S = 1300$: $g(T)$ shifts down. In the warm region: $g = 1300 \times 0.70/4 = 227.5$, while $h(290) = 244.9 > 227.5$. No warm equilibrium exists. The cold-region value $g = 1300 \times 0.35/4 = 113.75$, and $h(232) \approx 100$; these still intersect. Only the Snowball Earth equilibrium remains, confirming that a reduction in $S$ can trigger irreversible glaciation.

    $\square$

---

**Exercise 38.6.** Mann–Kendall trend test with autocorrelation correction.

??? success "Solution"

    With $n = 600$ months and $S = 45000$:

    $\operatorname{Var}(S) = n(n-1)(2n+5)/18 = 600 \times 599 \times 1205/18 = 433{,}077{,}000/18 = 24{,}059{,}833$.

    $Z = (S-1)/\sqrt{\operatorname{Var}(S)} = 44999/4905.08 \approx 9.17$.

    The two-sided $p$-value for $Z = 9.17$ is $p < 10^{-19}$. The trend is overwhelmingly significant without correction.

    **With Hamed–Rao correction** for $\rho = 0.3$:

    Effective sample size: $n^* \approx n(1-\rho)/(1+\rho) = 600 \times 0.7/1.3 = 323.1$.

    Corrected variance: $\operatorname{Var}^*(S) = \operatorname{Var}(S) \times n/n^* = 24{,}059{,}833 \times 600/323.1 = 44{,}679{,}356$.

    $Z^* = 44999/\sqrt{44{,}679{,}356} = 44999/6684.3 \approx 6.73$.

    The corrected $p$-value for $Z^* = 6.73$ is still $p < 10^{-10}$. The trend remains highly significant even after accounting for positive autocorrelation, though the $Z$-score decreased from 9.17 to 6.73, illustrating the inflation of apparent significance when autocorrelation is ignored.

    $\square$

---

**Exercise 38.7.** Coupled EBM-carbon cycle simulation.

??? success "Solution"

    The four-variable ODE system is:

    $$\begin{aligned}
    C\frac{dT}{dt} &= \frac{S(1-\alpha)}{4} + F(t) - \varepsilon\sigma T^4, \quad F(t) = 5.35\ln\!\left(\frac{C_a(t)}{C_{a,0}}\right), \\
    \frac{dC_a}{dt} &= E(t) - k_{ao}C_a + k_{oa}C_o - k_{al}C_a + k_{la}C_l, \\
    \frac{dC_o}{dt} &= k_{ao}C_a - k_{oa}C_o, \\
    \frac{dC_l}{dt} &= k_{al}C_a - k_{la}C_l.
    \end{aligned}$$

    With $E(t) = 10$ GtC/yr for $0 \leq t \leq 100$ yr and $E(t) = 0$ for $t > 100$ yr, initial conditions $T(0) = 288$ K, $C_a(0) = 590$ GtC, $C_o(0) = 38000$ GtC, $C_l(0) = 2000$ GtC, using the standard parameter values from the chapter.

    RK4 integration with $h = 0.1$ yr for 600 years yields:

    - After 100 years (when emissions stop): $C_a \approx 590 + \sim 550 = \sim 1140$ GtC (approximately doubled), $F \approx 5.35 \ln(1140/590) \approx 3.5$ W/m$^2$, $\Delta T \approx 2.0$--$2.5^\circ$C.
    - Peak warming occurs 10–30 years after emissions cease (due to ocean thermal inertia), at approximately $\Delta T \approx 2.5$--$3.0^\circ$C.
    - At $t = 600$ yr: atmospheric $\text{CO}_2$ has partially equilibrated with the ocean ($\tau \approx 100$--300 yr), $C_a$ has declined substantially but remains above pre-industrial. Residual warming at 500 years after emission cessation is approximately $0.5$--$1.0^\circ$C, reflecting the long ocean carbon uptake timescale.

    $\square$

---

**Exercise 38.8.** Synthetic temperature record analysis.

??? success "Solution"

    Generate $T(t) = 0.01t + 0.2\sin(2\pi t/65) + \eta(t)$ for $t = 1, \ldots, 200$ with $\eta \sim N(0, 0.01)$.

    (a) The PSD shows a peak at $f = 1/65 \approx 0.0154$ yr$^{-1}$ (the AMO-like oscillation) and elevated power at $f \to 0$ (the linear trend manifests as low-frequency power). The frequency resolution $\Delta f = 1/200 = 0.005$ yr$^{-1}$ can resolve $f = 1/65$.

    (b) Linear regression gives $\hat{\beta}_1 \approx 0.01$ $^\circ$C/yr. The 95% confidence interval width depends on the residual variance and autocorrelation. For $\sigma = 0.1$ and $n = 200$, the standard error of the slope is approximately $\sigma/(n\sqrt{1/12}) \approx 0.1/(200 \times 0.289) = 0.00173$, giving a 95% CI of approximately $0.01 \pm 0.0034$ $^\circ$C/yr.

    (c) The Mann–Kendall test detects a significant monotonic trend. For a 200-year record with a clear positive drift of 2$^\circ$C total, $S$ is strongly positive and $\lvert Z\rvert \gg 2$.

    (d) The AMO-like oscillation biases the trend estimate depending on record length. If the record covers a rising phase of the 65-year cycle (say 30 years), the estimated trend is inflated: $0.01 + 0.2 \times 2\pi/(65) \times \cos(\cdot) \approx 0.01 + 0.006 = 0.016$ $^\circ$C/yr. Conversely, a falling phase yields an underestimate. Only records spanning at least two full cycles (130 years) reliably separate the trend from the oscillation. This is precisely the challenge in attributing observed warming: natural multidecadal variability can temporarily amplify or mask the anthropogenic trend.

    $\square$

---
