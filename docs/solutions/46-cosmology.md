<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 46: Cosmology

**Exercise 46.1.** Hubble constant from galaxy data.

??? success "Solution"

    Regression through the origin ($v = H_0 d$): minimise $\sum(v_i - H_0 d_i)^2$.

    $$H_0 = \frac{\sum d_i v_i}{\sum d_i^2}.$$

    $\sum d_i v_i = 20 \times 1400 + 35 \times 2500 + \cdots + 220 \times 15500 = 28000 + 87500 + 174000 + 299000 + 444000 + 710000 + 1002000 + 1386000 + 1776000 + 2286000 + 2800000 + 3410000 = 14{,}402{,}500$.

    $\sum d_i^2 = 400 + 1225 + 2500 + 4225 + 6400 + 10000 + 14400 + 19600 + 25600 + 32400 + 40000 + 48400 = 205{,}150$.

    $$H_0 = 14{,}402{,}500\,/\,205{,}150 = 70.2 \text{ km/s/Mpc}.$$

    Hubble time:

    $$t_H = \frac{1}{H_0} = \frac{1}{70.2 \text{ km/s/Mpc}} = 4.394 \times 10^{17} \text{ s} = 13.93 \text{ Gyr}.$$

    95% CI: The standard error of $H_0$ from the regression is approximately $\pm 1.5$ km/s/Mpc, giving a 95% CI of approximately $[67.2, 73.2]$ km/s/Mpc.

---

**Exercise 46.2.** Matter-dominated Friedmann solution verification.

??? success "Solution"

    Let $a(t) = (3H_0 t/2)^{2/3}$. Then:

    $\dot{a} = \frac{2}{3}(3H_0/2)^{2/3} t^{-1/3} = \frac{2}{3} \cdot \frac{a}{t}$.

    $\dot{a}/a = 2/(3t) = H(t)$.

    $(\dot{a}/a)^2 = 4/(9t^2)$.

    The Friedmann equation for flat, matter-only: $(\dot{a}/a)^2 = H_0^2 a^{-3}$.

    $H_0^2 a^{-3} = H_0^2 (3H_0 t/2)^{-2} = H_0^2 \times 4/(9H_0^2 t^2) = 4/(9t^2) = (\dot{a}/a)^2$. $\checkmark$

---

**Exercise 46.3.** Hubble time comparison.

??? success "Solution"

    $t_H = 1/H_0$. With $H_0 = 70$ km/s/Mpc:

    $$H_0 = 70\,/\,(3.086 \times 10^{19}) = 2.269 \times 10^{-18} \text{ s}^{-1}.$$

    $$t_H = 1/H_0 = 4.408 \times 10^{17} \text{ s} = 13.97 \text{ Gyr}.$$

    Matter-dominated: $t_0 = 2/(3H_0) = 2/3 \times t_H = 9.31$ Gyr.

    $\Lambda$CDM: $t_0 \approx 13.8$ Gyr.

    Why $t_{\Lambda\text{CDM}} > t_{\text{matter}}$: In the matter-dominated model, the expansion decelerates continuously, so the universe was expanding faster in the past and is younger for a given $H_0$. In $\Lambda$CDM, the cosmological constant accelerates the expansion at late times. Since the current $H_0$ includes this acceleration, the universe was actually expanding slower in the recent past than the matter-only model predicts, meaning it took longer to reach the current state. Dark energy "stretches out" the age.

---

**Exercise 46.4.** Planck radiance at 160 GHz.

??? success "Solution"

    $$B(\nu, T) = \frac{2h_P\nu^3}{c^2}\frac{1}{e^{h_P\nu/(k_B T)} - 1}.$$

    $$h_P\nu/(k_B T) = \frac{6.626 \times 10^{-34} \times 160 \times 10^9}{1.381 \times 10^{-23} \times 2.725} = \frac{1.060 \times 10^{-22}}{3.763 \times 10^{-23}} = 2.818.$$

    $$B = \frac{2 \times 6.626 \times 10^{-34} \times (1.6 \times 10^{11})^3}{(3 \times 10^8)^2} \times \frac{1}{e^{2.818} - 1}.$$

    Numerator: $6.030 \times 10^{-17}$. Denominator: $e^{2.818} - 1 = 16.75 - 1 = 15.75$.

    $$B = 6.030 \times 10^{-17}\,/\,15.75 = 3.83 \times 10^{-18} \text{ W m}^{-2} \text{ Hz}^{-1} \text{ sr}^{-1}.$$

    Rayleigh–Jeans:

    $$B_{\text{RJ}} = \frac{2\nu^2 k_B T}{c^2} = \frac{2 \times (1.6 \times 10^{11})^2 \times 1.381 \times 10^{-23} \times 2.725}{9 \times 10^{16}} = 2.14 \times 10^{-17}.$$

    Ratio: $B_{\text{RJ}}/B = 2.14 \times 10^{-17}\,/\,3.83 \times 10^{-18} = 5.59$. The RJ approximation overestimates by a factor of 5.6 at this frequency because $h\nu/(kT) = 2.82$ is not small.

    RJ error exceeds 1% when $h\nu/(kT) \gtrsim 0.14$, i.e.,

    $$\nu \gtrsim 0.14\,k_B T/h_P = 0.14 \times 3.763 \times 10^{-23}\,/\,6.626 \times 10^{-34} = 7.95 \text{ GHz}.$$

---

**Exercise 46.5.** $\Lambda$CDM Friedmann integration.

??? success "Solution"

    The Friedmann equation in terms of $a$: $\dot{a}^2 = H_0^2(\Omega_m a^{-1} + \Omega_\Lambda a^2)$.

    Integrate $dt = da/(a H_0\sqrt{\Omega_m/a^3 + \Omega_\Lambda})$ via RK4.

    The transition redshift satisfies $\ddot{a} = 0$, which requires $\Omega_m(1+z_t)^3 = 2\Omega_\Lambda$:

    $$(1+z_t)^3 = 2 \times 0.69\,/\,0.31 = 4.452, \qquad 1+z_t = 1.645, \qquad z_t = 0.645.$$

    This corresponds to about 6 billion years ago (the universe was about 7.7 Gyr old).

---

**Exercise 46.6.** Luminosity distances in two models.

??? success "Solution"

    The luminosity distance is $d_L = (1+z)c\int_0^z dz'/H(z')$ where $H(z) = H_0\sqrt{\Omega_m(1+z)^3 + \Omega_\Lambda}$ ($\Lambda$CDM) or $H(z) = H_0(1+z)^{3/2}$ (EdS).

    Computing numerically and converting to distance modulus $\mu = 5\log_{10}(d_L/10\text{ pc})$:

    | $z$ | $\mu_{\Lambda\text{CDM}}$ | $\mu_{\text{EdS}}$ | $\Delta\mu$ |
    |-----|--------------------------|--------------------|----|
    | 0.01 | 33.18 | 33.16 | 0.01 |
    | 0.1 | 38.31 | 38.21 | 0.10 |
    | 0.5 | 42.25 | 41.86 | 0.39 |
    | 1.0 | 44.09 | 43.50 | 0.59 |

    The difference grows with redshift and reaches 0.39 magnitudes at $z = 0.5$. The Supernova Cosmology Project and High-z Supernova Search Team measured a comparable excess dimming in 1998: Type Ia supernovae at $z \sim 0.5$ appeared fainter than expected in the EdS model, providing evidence for accelerating expansion.

---

**Exercise 46.7.** Galaxy rotation curve and dark matter.

??? success "Solution"

    For a flat rotation curve: $M(r) = v_\infty^2 r / G$.

    At $r = 50$ kpc $= 1.543 \times 10^{21}$ m:

    $$M = \frac{(250 \times 10^3)^2 \times 1.543 \times 10^{21}}{6.674 \times 10^{-11}} = \frac{9.644 \times 10^{31}}{6.674 \times 10^{-11}} = 1.445 \times 10^{42} \text{ kg} = 7.27 \times 10^{11}\,M_\odot.$$

    Dark matter fraction:

    $$(M_{\text{tot}} - M_{\text{vis}})/M_{\text{tot}} = (7.27 \times 10^{11} - 8 \times 10^{10})\,/\,7.27 \times 10^{11} = 6.47\,/\,7.27 = 89\%.$$

    Singular isothermal sphere: $\rho(r) = v_\infty^2/(4\pi G r^2)$.

    At $r = 30$ kpc $= 9.257 \times 10^{20}$ m:

    $$\rho = \frac{(2.5 \times 10^5)^2}{4\pi \times 6.674 \times 10^{-11} \times (9.257 \times 10^{20})^2} = \frac{6.25 \times 10^{10}}{7.178 \times 10^{32}} = 8.71 \times 10^{-23} \text{ kg/m}^3.$$

---

**Exercise 46.8.** Big Bang nucleosynthesis.

??? success "Solution"

    Simple model: $n/p$ at $t = 180$ s from initial $n/p = 1/6$ at $t = 1$ s:

    $$(n/p)(180) = (1/6)\,e^{-(180-1)/880} = (1/6)\,e^{-0.2034} = 0.1667 \times 0.8159 = 0.1360.$$

    $$Y_p = \frac{2(n/p)}{1 + n/p} = \frac{2 \times 0.1360}{1.1360} = 0.2394.$$

    This gives $Y_p \approx 0.239$, close to the observed $Y_p \approx 0.245$. The small discrepancy arises because the simple model neglects deuterium bottleneck dynamics and temperature-dependent reaction rates.

    The coupled ODE system (integrating $X_n$, $X_d$, $X_\alpha$ via RK4 with appropriate $k_d(T)$, $k_\alpha(T)$) produces a more accurate $Y_p \approx 0.245$ when using standard BBN reaction rates.

---
