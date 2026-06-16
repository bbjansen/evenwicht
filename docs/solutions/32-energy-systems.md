<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 32: Energy Systems & Nuclear Engineering

**Exercise 32.1.** Iodine-131 decay.

??? success "Solution"

    $t_{1/2} = 8.02$ days.

    **(a)** $\lambda = \ln 2/t_{1/2} = 0.6931/8.02 = 0.08643$ day$^{-1}$.

    **(b)** After 24 days: $A(24) = 550 \times e^{-0.08643 \times 24} = 550 \times e^{-2.0743} = 550 \times 0.1256 = 69.1$ MBq.

    **(c)** Activity falls to 1%: $0.01 = e^{-\lambda t}$, so $t = -\ln(0.01)/\lambda = \ln(100)/0.08643 = 4.6052/0.08643 = 53.3$ days.

    $\square$

---

**Exercise 32.2.** Decay of isotope A to stable B.

??? success "Solution"

    $t_{1/2} = 30$ yr, so $\lambda = \ln 2/30 = 0.02310$ yr$^{-1}$.

    $N_A(100) = 10^{24} e^{-0.02310 \times 100} = 10^{24} e^{-2.310} = 10^{24} \times 0.09888 = 9.888 \times 10^{22}$.

    $N_B(100) = 10^{24} - N_A(100) = 10^{24} - 9.888 \times 10^{22} = 9.011 \times 10^{23}$.

    Fraction transmuted: $(10^{24} - 9.888 \times 10^{22})/10^{24} = 1 - 0.09888 = 0.9011 = 90.1\%$.

    $\square$

---

**Exercise 32.3.** Newton's cooling.

??? success "Solution"

    $T(t) = T_{\text{env}} + (T_0 - T_{\text{env}})e^{-h't} = 30 + 270 e^{-0.05t}$.

    Set $T(t^*) = 80$: $80 = 30 + 270 e^{-0.05t^*}$, so $e^{-0.05t^*} = 50/270 = 0.18519$.

    $t^* = -\ln(0.18519)/0.05 = 1.6864/0.05 = 33.7$ hours.

    $\square$

---

**Exercise 32.4.** Economic dispatch.

??? success "Solution"

    Cost for generator $i$: $C_i(P_i) = b_i P_i + c_i P_i^2$ (per-unit formulation). Marginal cost: $MC_i = b_i + 2c_i P_i$.

    Equal incremental cost: set $MC_i = \lambda^*$ for all active generators.

    $P_i = (\lambda^* - b_i)/(2c_i)$:

    - $P_1 = (\lambda^* - 18)/0.016$
    - $P_2 = (\lambda^* - 22)/0.024$
    - $P_3 = (\lambda^* - 28)/0.036$
    - $P_4 = (\lambda^* - 35)/0.050$

    Demand balance: $P_1 + P_2 + P_3 + P_4 = 1100$.

    $$\frac{\lambda^*-18}{0.016} + \frac{\lambda^*-22}{0.024} + \frac{\lambda^*-28}{0.036} + \frac{\lambda^*-35}{0.050} = 1100.$$

    $62.5(\lambda^*-18) + 41.667(\lambda^*-22) + 27.778(\lambda^*-28) + 20(\lambda^*-35) = 1100$.

    $151.944\lambda^* - (1125 + 916.67 + 777.78 + 700) = 1100$.

    $151.944\lambda^* - 3519.44 = 1100$.

    $\lambda^* = 4619.44/151.944 = 30.40$ €/MWh.

    Individual outputs:

    - $P_1 = (30.40 - 18)/0.016 = 775$ MW. Exceeds $P_1^{\max} = 600$, so set $P_1 = 600$.

    With $P_1$ capped at 600: remaining demand = $1100 - 600 = 500$ MW from generators 2–4.

    Re-solve: $41.667(\lambda^*-22) + 27.778(\lambda^*-28) + 20(\lambda^*-35) = 500$.

    $89.444\lambda^* - 916.67 - 777.78 - 700 = 500$. $89.444\lambda^* = 2894.44$. $\lambda^* = 32.36$ €/MWh.

    - $P_2 = (32.36-22)/0.024 = 431.7$ MW. Exceeds $P_2^{\max}=400$, so set $P_2 = 400$.

    Re-solve with $P_1=600$, $P_2=400$: remaining = $1100 - 600 - 400 = 100$ MW.

    $27.778(\lambda^*-28) + 20(\lambda^*-35) = 100$. $47.778\lambda^* = 100 + 777.78 + 700 = 1577.78$. $\lambda^* = 33.02$.

    - $P_3 = (33.02-28)/0.036 = 139.4$ MW. Within [50, 300]. $\checkmark$
    - $P_4 = (33.02-35)/0.050 = -39.6$. Negative, so $P_4 = P_4^{\min} = 20$.

    Re-solve with $P_1=600$, $P_2=400$, $P_4=20$: $P_3 = 1100-600-400-20=80$ MW. $MC_3 = 28 + 0.036 \times 80 = 30.88$ €/MWh.

    System marginal cost: $\lambda^* = MC_3 = 30.88$ €/MWh (the marginal cost of the last dispatched unit). Generator 4 is at its minimum with $MC_4 = 35 + 2(0.025)(20) = 36.0$ €/MWh $> \lambda^* = 30.88$ €/MWh, consistent with the KKT conditions.

    Total optimised cost: $C_1(600) + C_2(400) + C_3(80) + C_4(20) = (18\times600+0.008\times360000)+(22\times400+0.012\times160000)+(28\times80+0.018\times6400)+(35\times20+0.025\times400) = (10800+2880)+(8800+1920)+(2240+115.2)+(700+10) = 13680+10720+2355.2+710 = €27{,}465$.

    Equal output at $P_i = 275$ each (where feasible; $P_4^{\max}=200$, so not all can produce 275). This constraint violation already shows the equal-output plan is infeasible, but forcing $P_1=P_2=P_3=275$, $P_4=200$ (total=1025, insufficient) or other adjustments, the cost would be higher due to operating expensive generators at high output. The optimisation exploits the merit order.

    $\square$

---

**Exercise 32.5.** Battery arbitrage.

??? success "Solution"

    Prices: [25, 22, 20, 18, 55, 70, 65, 40]. Charge during cheap hours (1–4), discharge during expensive hours (5–8).

    Round-trip efficiency: $\eta = \eta_c \times \eta_d = 0.90 \times 0.90 = 0.81$.

    Minimum profitable spread: buy at price $p_{\text{low}}$, sell at $p_{\text{high}}$. Profit per MWh: $p_{\text{high}} \times \eta_d - p_{\text{low}}/\eta_c > 0$, i.e., $p_{\text{high}}/p_{\text{low}} > 1/(\eta_c\eta_d) = 1/0.81 = 1.235$. Minimum spread ratio is $23.5\%$.

    **Optimal strategy:** Charge at hour 4 (€18) and hour 3 (€20): energy stored = $100 \times 0.90 = 90$ MWh per hour. After 2 hours charging: SOC = $100 + 90 + 90 = 280$ MW. But $\text{SOC}^{\max} = 200$, so can only charge $200 - 100 = 100$ MWh total, taking $100/0.90 = 111.1$ MWh from grid. Charge 1 hour at €18 (store 90 MWh, SOC = 190) and partial at €20 (store 10 MWh, grid draws $10/0.9 = 11.1$ MWh, SOC = 200).

    Charge fully during cheapest hours, discharge fully during most expensive. Charge: 100 MW at €18 (SOC: $100 + 90 = 190$), 100 MW at €20 (SOC: $190 + \min(90, 10) = 200$, grid cost = $11.1 \times 20 = €222$, total charge cost = $€1800 + €222 = €2{,}022$).

    Discharge: 100 MW at €70 for 1 hour (SOC $\to 100$, revenue = $100 \times 70 = €7{,}000$), then 80 MW at €65 for 1 hour (SOC $\to 20$, revenue = $80 \times 65 = €5{,}200$).

    Maximum revenue: $€7{,}000 + €5{,}200 - €2{,}022 = €10{,}178$.

    $\square$

---

**Exercise 32.6.** ARIMA model identification for electricity demand.

??? success "Solution"

    For hourly demand data over two weeks (336 hours):

    **Expected ACF structure:** Significant autocorrelation at lags 1, 2, ... (consecutive hours are correlated), with a strong spike at lag 24 (daily cycle: demand at 2pm today is correlated with demand at 2pm yesterday). Also significant at lag 168 (weekly cycle). The ACF decays slowly, indicating non-stationarity.

    **PACF structure:** After differencing, the PACF helps identify the AR order. Significant PACF at lags 1 and possibly 2, with a spike at lag 24.

    **Seasonal differencing with $s=24$:** Applying $(1-L^{24})$ removes the daily seasonal pattern. The differenced series $y_t - y_{t-24}$ represents the deviation of today's demand from the same hour yesterday. This series should be approximately stationary, with ACF showing short-range dependence. A SARIMA model $\text{ARIMA}(p,d,q)(P,D,Q)_{24}$ with $D=1$ (one seasonal difference) is appropriate. Typically $d=0$ or $d=1$ for the non-seasonal part, with $p,q \leq 2$ and $P,Q \leq 1$.

    $\square$

---

**Exercise 32.7.** Reactor buckling derivation.

??? success "Solution"

    In spherical coordinates with azimuthal symmetry, the Helmholtz equation $\nabla^2\phi + B^2\phi = 0$ becomes:

    $$\frac{1}{r^2}\frac{d}{dr}\left(r^2\frac{d\phi}{dr}\right) + B^2\phi = 0.$$

    Substituting $\phi(r) = u(r)/r$: $\frac{d^2u}{dr^2} + B^2 u = 0$.

    General solution: $u(r) = A\sin(Br) + C\cos(Br)$. Since $\phi(0)$ must be finite and $\phi = u/r$, $u(0) = 0$ is required, so $C = 0$. Thus $\phi(r) = A\sin(Br)/r$.

    Boundary condition $\phi(R) = 0$: $\sin(BR) = 0$, so $BR = n\pi$ for positive integer $n$. The fundamental mode ($n=1$) gives $B = \pi/R$, so:

    $$B_g^2 = \left(\frac{\pi}{R}\right)^2.$$

    $\square$

    For criticality, the material buckling equals the geometric buckling: $B_m^2 = B_g^2$ where $B_m^2 = (\nu\Sigma_f - \Sigma_a)/D$. Setting equal:

    $$\frac{\nu\Sigma_f - \Sigma_a}{D} = \frac{\pi^2}{R_c^2} \quad \Rightarrow \quad R_c = \frac{\pi}{\sqrt{(\nu\Sigma_f - \Sigma_a)/D}}.$$

---

**Exercise 32.8.** Multi-period dispatch LP with storage.

??? success "Solution"

    **Decision variables:** $P_{g,t}$ (output of generator $g$ at hour $t$), $c_t$ (charge power at hour $t$), $d_t$ (discharge power at hour $t$), $\text{SOC}_t$ (state of charge at end of hour $t$). For $g = 1,2$ and $t = 1,\ldots,24$: total = $2 \times 24 + 24 + 24 + 24 = 120$ decision variables.

    **Objective:** Minimise total generation cost:

    $$\min \sum_{t=1}^{24}\sum_{g=1}^{2}(b_g P_{g,t} + c_g P_{g,t}^2).$$

    (For an LP, approximate as linear: $\min \sum_{t,g} b_g P_{g,t}$.)

    **Constraints:**

    1. Demand balance: $P_{1,t} + P_{2,t} + d_t - c_t = D_t$ for each $t$ (24 constraints).
    2. Generator limits: $P_g^{\min} \leq P_{g,t} \leq P_g^{\max}$ (48 constraints).
    3. SOC dynamics: $\text{SOC}_t = \text{SOC}_{t-1} + \eta_c c_t - d_t/\eta_d$ (24 constraints).
    4. SOC limits: $\text{SOC}^{\min} \leq \text{SOC}_t \leq \text{SOC}^{\max}$ (48 constraints).
    5. Charge/discharge limits: $0 \leq c_t \leq c^{\max}$, $0 \leq d_t \leq d^{\max}$ (48 constraints).
    6. Non-negativity: $P_{g,t}, c_t, d_t \geq 0$.

    Total constraints: $24 + 48 + 24 + 48 + 48 = 192$ (plus non-negativity).

    The dual variable on the demand balance constraint at hour $t$ is the **locational marginal price (LMP)** at hour $t$: the marginal cost of serving one additional unit of demand at that hour. It reflects both generation costs and the opportunity cost of storage.

    $\square$

---
