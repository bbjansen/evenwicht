<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 35: Pharmacokinetics

**Exercise 35.1.** IV bolus basics.

??? success "Solution"

    $k_e = 0.1$ h$^{-1}$, $V_d = 50$ L, dose $D = 400$ mg.

    **(a)** $t_{1/2} = \ln 2/k_e = 0.6931/0.1 = 6.93$ h.

    **(b)** $C_0 = D/V_d = 400/50 = 8.0$ mg/L.

    **(c)** $CL = k_e \times V_d = 0.1 \times 50 = 5.0$ L/h.

    **(d)** $C(8) = C_0 e^{-k_e \times 8} = 8.0 \times e^{-0.8} = 8.0 \times 0.4493 = 3.59$ mg/L.

    **(e)** $\text{AUC}_0^\infty = C_0/k_e = 8.0/0.1 = 80.0$ mg$\cdot$h/L.

---

**Exercise 35.2.** Oral formulation.

??? success "Solution"

    $k_a = 2.0$ h$^{-1}$, $k_e = 0.3$ h$^{-1}$, $V_d = 25$ L, $F = 0.65$, $D = 100$ mg.

    $t_{\max} = \frac{\ln(k_a/k_e)}{k_a - k_e} = \frac{\ln(2.0/0.3)}{2.0 - 0.3} = \frac{\ln(6.667)}{1.7} = \frac{1.897}{1.7} = 1.116$ h.

    Substituting $t_{\max}$ into the Bateman equation directly (equivalently, applying Theorem 35.14):

    $C_{\max} = \frac{FD}{V_d} \cdot \frac{k_a}{k_a - k_e}\left(e^{-k_e t_{\max}} - e^{-k_a t_{\max}}\right)$.

    $= \frac{0.65 \times 100}{25} \cdot \frac{2.0}{1.7}(e^{-0.3 \times 1.116} - e^{-2.0 \times 1.116})$

    $= 2.6 \times 1.1765 \times (e^{-0.335} - e^{-2.232}) = 3.059 \times (0.7153 - 0.1068) = 3.059 \times 0.6085 = 1.86$ mg/L.

    *Alternatively, using the closed-form expression of Theorem 35.14:* $C_{\max} = \frac{FD}{V_d}\left(\frac{k_e}{k_a}\right)^{k_e/(k_a-k_e)} = \frac{0.65 \times 100}{25}\left(\frac{0.3}{2.0}\right)^{0.3/1.7} = 2.6 \times (0.15)^{0.1765} = 2.6 \times 0.716 = 1.86$ mg/L. $\checkmark$

---

**Exercise 35.3.** Multiple IV dosing.

??? success "Solution"

    $D = 300$ mg, $\tau = 8$ h, $k_e = 0.25$ h$^{-1}$, $V_d = 35$ L.

    $r = e^{-k_e\tau} = e^{-2.0} = 0.1353$.

    Accumulation factor: $R = 1/(1-r) = 1/(1-0.1353) = 1/0.8647 = 1.156$.

    $C_0 = D/V_d = 300/35 = 8.571$ mg/L.

    $C_{\max,ss} = C_0 \times R = 8.571 \times 1.156 = 9.91$ mg/L.

    $C_{\min,ss} = C_0 \times R \times r = 9.91 \times 0.1353 = 1.34$ mg/L.

---

**Exercise 35.4.** Approach to steady state.

??? success "Solution"

    $k_e = 0.05$ h$^{-1}$, $t_{1/2} = 13.86$ h, $\tau = 12$ h.

    $r = e^{-k_e\tau} = e^{-0.6} = 0.5488$.

    Fraction of steady state after $n$ doses: $f_n = (1-r^n)/(1-r)$ divided by $1/(1-r)$ gives $f_n = 1 - r^n$.

    | $n$ | $r^n$ | $f_n$ |
    |-----|--------|-------|
    | 1 | 0.5488 | 0.451 |
    | 2 | 0.3012 | 0.699 |
    | 3 | 0.1653 | 0.835 |
    | 5 | 0.0498 | 0.950 |
    | 10 | 0.0025 | 0.998 |

    For 90% of steady state: $1 - r^n \geq 0.90$, so $r^n \leq 0.10$. $n \geq \ln(10)/\ln(1/r) = 2.3026/\ln(1/0.5488) = 2.3026/0.6 = 3.84$, so $n \geq 4$ doses. $\checkmark$

---

**Exercise 35.5.** Dosing regimen design.

??? success "Solution"

    MEC $= 5$ mg/L, MTC $= 40$ mg/L, $k_e = 0.08$ h$^{-1}$, $V_d = 60$ L.

    **(a)** Maximum dosing interval: $C_{\max}$ must not exceed MTC and $C_{\min}$ must stay above MEC. $\tau_{\max} = \ln(\text{MTC}/\text{MEC})/k_e = \ln(40/5)/0.08 = \ln(8)/0.08 = 2.0794/0.08 = 26.0$ h.

    **(b)** Target $\bar{C}_{ss} = 15$ mg/L, $\tau = 12$ h. $\bar{C}_{ss} = \frac{D}{CL \times \tau} = \frac{D}{k_e V_d \tau}$. $D = \bar{C}_{ss} \times k_e \times V_d \times \tau = 15 \times 0.08 \times 60 \times 12 = 864$ mg.

    **(c)** Loading dose: $D_L = D/(1-e^{-k_e\tau}) = 864/(1-e^{-0.96}) = 864/(1-0.3829) = 864/0.6171 = 1400$ mg.

    **(d)** $C_{\max,ss} = D_L/V_d = 1400/60 = 23.3$ mg/L. $C_{\min,ss} = C_{\max,ss} \times e^{-k_e\tau} = 23.3 \times 0.3829 = 8.93$ mg/L.

    Check: $5 \leq 8.93$ and $23.3 \leq 40$. Both within the therapeutic window. $\checkmark$

---

**Exercise 35.6.** Bioavailability.

??? success "Solution"

    **(a)** $F = \text{AUC}_{\text{oral}}/\text{AUC}_{\text{IV}} = 52/80 = 0.65$.

    **(b)** From the Bateman equation: $t_{\max} = \ln(k_a/k_e)/(k_a - k_e) = 2.1$ h. And $k_e = 0.15$ h$^{-1}$.

    $2.1 = \ln(k_a/0.15)/(k_a - 0.15)$. Let $x = k_a$. $2.1(x-0.15) = \ln(x/0.15)$.

    Trying $x = 1.0$: LHS = $2.1 \times 0.85 = 1.785$, RHS = $\ln(6.667) = 1.897$. Close.

    Trying $x = 1.1$: LHS = $2.1 \times 0.95 = 1.995$, RHS = $\ln(7.333) = 1.993$. Match.

    $k_a \approx 1.10$ h$^{-1}$.

    **(c)** $\text{AUC}_{\text{oral}} = \frac{FD}{V_d k_e} = \frac{0.65 \times 500}{42 \times 0.15} = \frac{325}{6.3} = 51.6$ mg$\cdot$h/L. This is close to the observed 52, confirming consistency. $\checkmark$

---

**Exercise 35.7.** Two-compartment model.

??? success "Solution"

    $C(t) = 30e^{-2.5t} + 10e^{-0.15t}$, dose $= 600$ mg.

    **(a)** $A = 30$ mg/L, $B = 10$ mg/L, $\alpha = 2.5$ h$^{-1}$, $\beta = 0.15$ h$^{-1}$.

    **(b)** $V_c = D/(A+B) = 600/40 = 15$ L.

    Micro-constants: $k_{21} = (A\beta + B\alpha)/(A+B) = (30 \times 0.15 + 10 \times 2.5)/40 = (4.5+25)/40 = 0.7375$ h$^{-1}$.

    $k_{10} = \alpha\beta/k_{21} = (2.5 \times 0.15)/0.7375 = 0.375/0.7375 = 0.5085$ h$^{-1}$.

    $k_{12} = \alpha + \beta - k_{21} - k_{10} = 2.5 + 0.15 - 0.7375 - 0.5085 = 1.404$ h$^{-1}$.

    **(c)** $\text{AUC} = A/\alpha + B/\beta = 30/2.5 + 10/0.15 = 12 + 66.67 = 78.67$ mg$\cdot$h/L.

    $CL = D/\text{AUC} = 600/78.67 = 7.63$ L/h.

    **(d)** $V_{ss} = V_c(1 + k_{12}/k_{21}) = 15(1 + 1.404/0.7375) = 15(1 + 1.904) = 15 \times 2.904 = 43.6$ L.

---

**Exercise 35.8.** Steady-state oral dosing derivation.

??? success "Solution"

    After the $n$-th dose (at time $t$ within the interval, $0 \leq t \leq \tau$), the contribution from the $j$-th previous dose (given $j$ intervals ago) is:

    $$C_j(t) = \frac{k_a FD}{V_d(k_a - k_e)}\left[e^{-k_e(t + j\tau)} - e^{-k_a(t+j\tau)}\right].$$

    Summing over all previous doses ($j = 0, 1, 2, \ldots$) at steady state:

    $$C_{ss}(t) = \frac{k_a FD}{V_d(k_a-k_e)}\left[e^{-k_e t}\sum_{j=0}^{\infty}e^{-k_e j\tau} - e^{-k_a t}\sum_{j=0}^{\infty}e^{-k_a j\tau}\right].$$

    Each sum is a geometric series: $\sum_{j=0}^{\infty}e^{-k j\tau} = 1/(1-e^{-k\tau})$.

    $$C_{ss}(t) = \frac{k_a FD}{V_d(k_a-k_e)}\left[\frac{e^{-k_e t}}{1-e^{-k_e\tau}} - \frac{e^{-k_a t}}{1-e^{-k_a\tau}}\right].$$

    For $t_{\max,ss}$, set $dC_{ss}/dt = 0$:

    $$-k_e \cdot \frac{e^{-k_e t}}{1-e^{-k_e\tau}} + k_a \cdot \frac{e^{-k_a t}}{1-e^{-k_a\tau}} = 0,$$

    giving $k_a \frac{e^{-k_a t_{\max,ss}}}{1-e^{-k_a\tau}} = k_e \frac{e^{-k_e t_{\max,ss}}}{1-e^{-k_e\tau}}$.

    As $\tau \to \infty$: $e^{-k\tau} \to 0$, so $1/(1-e^{-k\tau}) \to 1$. The condition reduces to $k_a e^{-k_a t_{\max}} = k_e e^{-k_e t_{\max}}$, giving $t_{\max} = \ln(k_a/k_e)/(k_a - k_e)$, which is the single-dose formula.

    $\square$

---
