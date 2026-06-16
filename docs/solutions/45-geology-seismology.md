<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 45: Geology & Seismology

**Exercise 45.1.** Seismic velocities in granite and water.

??? success "Solution"

    For granite ($K = 50$ GPa, $\mu = 30$ GPa, $\rho = 2700$ kg/m$^3$):

    $$v_P = \sqrt{(K + 4\mu/3)/\rho} = \sqrt{(50 + 40) \times 10^9/2700} = \sqrt{3.333 \times 10^7} = 5774 \text{ m/s}.$$

    $$v_S = \sqrt{\mu/\rho} = \sqrt{30 \times 10^9/2700} = \sqrt{1.111 \times 10^7} = 3333 \text{ m/s}.$$

    $$v_P/v_S = 5774/3333 = 1.732 = \sqrt{3}.$$

    For water ($K = 2.2$ GPa, $\mu = 0$, $\rho = 1000$ kg/m$^3$):

    $$v_P = \sqrt{K/\rho} = \sqrt{2.2 \times 10^9/1000} = \sqrt{2.2 \times 10^6} = 1483 \text{ m/s}.$$

    $v_S = \sqrt{0/1000} = 0$. **No S-waves propagate in water** because fluids have zero shear modulus ($\mu = 0$). S-waves require a medium that resists shearing.

---

**Exercise 45.2.** Moment magnitude and energy.

??? success "Solution"

    $$M_0 = 10^{1.5 M_w + 9.1} = 10^{1.5 \times 7 + 9.1} = 10^{19.6} = 3.981 \times 10^{19} \text{ N}\cdot\text{m}.$$

    $$E = 10^{1.5 M_w + 4.8} = 10^{15.3} = 1.995 \times 10^{15} \text{ J}.$$

    For $M_w = 4.0$:

    $$E_4 = 10^{1.5 \times 4 + 4.8} = 10^{10.8} = 6.310 \times 10^{10} \text{ J}.$$

    Ratio:

    $$E_7/E_4 = 10^{15.3 - 10.8} = 10^{4.5} = 31{,}623.$$

    Approximately **31,623** magnitude-4.0 earthquakes would release the same energy as one magnitude-7.0 event.

---

**Exercise 45.3.** Radiocarbon dating.

??? success "Solution"

    $^{14}$C half-life: $t_{1/2} = 5730$ yr, decay constant $\lambda = \ln 2 / 5730 = 1.210 \times 10^{-4}$ yr$^{-1}$.

    Wooden artefact (62% remaining):

    $$t = -\ln(0.62)/\lambda = 0.4780 / (1.210 \times 10^{-4}) = 3950 \text{ yr}.$$

    Bone sample (12% remaining):

    $$t = -\ln(0.12)/\lambda = 2.120 / (1.210 \times 10^{-4}) = 17{,}520 \text{ yr}.$$

    The bone is older by $17{,}520 - 3950 = 13{,}570$ years.

---

**Exercise 45.4.** Seismic refraction: two-layer model.

??? success "Solution"

    Direct wave travel time: $t_d(x) = x/v_1 = x/5.0$.

    Head wave (refracted): $t_r(x) = 2h_1\cos(i_c)/v_1 + x/v_2$, where $\sin i_c = v_1/v_2 = 5/8 = 0.625$, so $\cos i_c = 0.7806$.

    $$t_r(x) = 2h_1 \times 0.7806/5.0 + x/8.0 = 0.3122\, h_1 + x/8.$$

    The crossover distance (where $t_d = t_r$):

    $$x_c/5 = 0.3122\, h_1 + x_c/8, \qquad x_c(1/5 - 1/8) = 0.3122\, h_1, \qquad x_c = 4.163\, h_1.$$

    From the first-arrival data, fit a line to the refracted arrivals (those beyond the crossover distance) to get slope $1/v_2 = 1/8$ and intercept $0.3122 h_1$. From the intercept, solve for $h_1$.

    For the given distances (50–250 km), refracted arrivals would appear for $x > x_c$ and form a line of slope $1/8 = 0.125$ s/km. The intercept gives $h_1 = \text{intercept}/0.3122$. Typical result: $h_1 \approx 30$–35 km (Moho depth).

---

**Exercise 45.5.** Gutenberg–Richter $b$-value.

??? success "Solution"

    Maximum likelihood estimate:

    $$b = \frac{\log_{10}(e)}{\bar{M} - M_c} = \frac{0.4343}{2.10 - 1.50} = \frac{0.4343}{0.60} = 0.724.$$

    This is below the global average of $b = 1.0$. Volcanic regions sometimes show lower $b$-values due to magmatic pressurisation, indicating a *higher* proportion of larger events relative to small ones.

    Probability of at least one $M \geq 5$ in 10 years: from Gutenberg–Richter,

    $$\log_{10} N(M \geq 5) = a - bM = 4.0 - 0.724 \times 5 = 0.38 \text{ per year},$$

    so $N = 10^{0.38} = 2.4$ events/year. In 10 years, expected number $= 24$.

    $$P(\text{at least one}) = 1 - e^{-24} \approx 1.0.$$

    It is virtually certain.

---

**Exercise 45.6.** Euler pole velocities.

??? success "Solution"

    The velocity at a point on a plate boundary relative to the Euler pole is $v = \omega R \sin\Delta$, where $\Delta$ is the angular distance from the point to the Euler pole and $R = 6371$ km.

    $$\omega = 0.12 \text{ deg/Myr} = 0.12 \times \pi/(180 \times 10^6) = 2.094 \times 10^{-9} \text{ rad/yr}.$$

    Mid-Atlantic ridge ($45^\circ$N, $28^\circ$W): angular distance from pole ($21^\circ$N, $20.6^\circ$W):

    $$\Delta = \arccos(\sin 21^\circ \sin 45^\circ + \cos 21^\circ \cos 45^\circ \cos 7.4^\circ) = \arccos(0.253 + 0.654) = \arccos(0.907) = 25.0^\circ.$$

    $$v = 2.094 \times 10^{-9} \times 6.371 \times 10^6 \times \sin 25^\circ = 13.34 \times 10^{-3} \times 0.4226 = 5.64 \text{ mm/yr}.$$

    **Divergent** (ridge spreading).

    Hellenic trench ($35^\circ$N, $23^\circ$E): $\cos(43.6^\circ) = 0.723$.

    $$\Delta = \arccos(\sin 21^\circ \sin 35^\circ + \cos 21^\circ \cos 35^\circ \cos 43.6^\circ) = \arccos(0.206 + 0.553) = \arccos(0.759) = 40.6^\circ.$$

    $$v = 13.34 \times 10^{-3} \times \sin 40.6^\circ = 13.34 \times 10^{-3} \times 0.651 = 8.68 \text{ mm/yr}.$$

    **Convergent** (subduction).

    The Hellenic trench is faster ($8.68$ vs. $5.64$ mm/yr).

---

**Exercise 45.7.** Four-layer travel times.

??? success "Solution"

    Using the layered travel-time formula for head waves through layer $k$:

    $$T_k(x) = \frac{x}{v_k} + 2\sum_{i=1}^{k-1}\frac{h_i\cos i_{ik}}{v_i},$$

    where $\sin i_{ik} = v_i/v_k$. Compute for each refracted branch and plot $T$ vs. $x$. Crossover distances mark transitions between dominant branches. Linear regression on each branch recovers the layer velocities (from slopes) and thicknesses (from intercepts). The inversion should recover the true values to within the discretisation error.

---

**Exercise 45.8.** Synthetic seismogram and filtering.

??? success "Solution"

    Generate $s(t) = P(t) + S(t) + \eta(t)$ at 50 Hz for 20 s (1000 samples). The PSD shows peaks at 2 Hz (P-wave) and 0.8 Hz (S-wave). A bandpass filter at 0.3–1.5 Hz passes the S-wave while attenuating the P-wave (at 2 Hz) by $> 20$ dB, effectively isolating the S-wave arrival.

---
