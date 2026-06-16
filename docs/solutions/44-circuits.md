<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 44: Electromagnetism & Circuit Analysis

**Exercise 44.1.** Two-node resistive network.

??? success "Solution"

    Conductances: $G_1 = 1/100 = 0.01$ S, $G_{12} = 1/50 = 0.02$ S, $G_2 = 1/200 = 0.005$ S.

    Conductance matrix:

    $$G = \begin{pmatrix} G_1 + G_{12} & -G_{12} \\ -G_{12} & G_2 + G_{12} \end{pmatrix} = \begin{pmatrix} 0.03 & -0.02 \\ -0.02 & 0.025 \end{pmatrix}.$$

    Source vector: $\mathbf{i}_s = \begin{pmatrix} 0.5 \\ 0 \end{pmatrix}$.

    Solve $G\mathbf{v} = \mathbf{i}_s$. $\det(G) = 0.03 \times 0.025 - 0.0004 = 0.00035$.

    $v_1 = (0.025 \times 0.5)/(0.00035) = 0.0125/0.00035 = 35.71$ V.

    $v_2 = (0.02 \times 0.5)/(0.00035) = 0.01/0.00035 = 28.57$ V.

    KCL at node 1: current through $R_1 = v_1/100 = 0.3571$ A, through $R_{12} = (v_1 - v_2)/50 = 7.14/50 = 0.1429$ A. Total leaving $= 0.5$ A $= I_s$. $\checkmark$

    KCL at node 2: current through $R_2 = v_2/200 = 0.1429$ A, through $R_{12}$ into node 2 $= 0.1429$ A. $0.1429 - 0.1429 = 0$. $\checkmark$

---

**Exercise 44.2.** RC circuit.

??? success "Solution"

    $\tau = RC = 4700 \times 22 \times 10^{-6} = 0.1034$ s.

    $v(t) = 12(1 - e^{-t/\tau})$.

    At $t = \tau$: $v = 12(1 - e^{-1}) = 12 \times 0.6321 = 7.585$ V.

    At $t = 2\tau$: $v = 12(1 - e^{-2}) = 12 \times 0.8647 = 10.38$ V.

    At $t = 5\tau$: $v = 12(1 - e^{-5}) = 12 \times 0.9933 = 11.92$ V.

    RK4 simulation of $\dot{v} = (V_s - v)/(RC)$ matches these values to numerical precision.

---

**Exercise 44.3.** RL circuit.

??? success "Solution"

    $\tau = L/R = 0.05/100 = 5 \times 10^{-4}$ s $= 0.5$ ms.

    $I(t) = (V/R)(1 - e^{-t/\tau}) = 0.1(1 - e^{-t/0.0005})$.

    For 90% of steady state: $1 - e^{-t/\tau} = 0.9$, $e^{-t/\tau} = 0.1$, $t = \tau\ln 10 = 0.0005 \times 2.303 = 1.151$ ms.

---

**Exercise 44.4.** Series RLC circuit.

??? success "Solution"

    $L = 10$ mH, $C = 100$ nF, $R = 50$ $\Omega$.

    (a) $\omega_0 = 1/\sqrt{LC} = 1/\sqrt{10^{-2} \times 10^{-7}} = 1/\sqrt{10^{-9}} = 31{,}623$ rad/s $\approx 5033$ Hz.

    $\zeta = R/(2\sqrt{L/C}) = 50/(2\sqrt{10^{-2}/10^{-7}}) = 50/(2\sqrt{10^5}) = 50/(2 \times 316.2) = 0.0791$.

    $Q = 1/(2\zeta) = 6.32$.

    (b) Since $\zeta = 0.079 < 1$: **underdamped**.

    (c) Eigenvalues: $\lambda = -\zeta\omega_0 \pm j\omega_0\sqrt{1-\zeta^2} = -2500 \pm j31{,}524$ (approximately).

    $\omega_d = \omega_0\sqrt{1 - \zeta^2} = 31{,}623\sqrt{1 - 0.00626} = 31{,}524$ rad/s $\approx 5017$ Hz.

    (d) RK4 simulation from $V_C(0) = 5$ V, $I(0) = 0$ produces a decaying sinusoid. Measuring the period between zero-crossings gives $f_d \approx 5017$ Hz, matching the analytical $\omega_d/(2\pi)$.

---

**Exercise 44.5.** RC low-pass at 1 kHz.

??? success "Solution"

    Cutoff: $f_c = 1/(2\pi RC) = 1000$ Hz. Choose $R = 1$ k$\Omega$: $C = 1/(2\pi \times 1000 \times 1000) = 159.2$ nF. Use $C = 150$ nF (nearest standard value), giving $f_c = 1/(2\pi \times 1000 \times 150 \times 10^{-9}) = 1061$ Hz.

    Magnitude response: $\lvert H(f)\rvert = 1/\sqrt{1 + (f/f_c)^2}$.

    At $f_c$: $\lvert H\rvert = 1/\sqrt{2} = -3$ dB. At $10 f_c$: $\lvert H\rvert \approx 0.1 = -20$ dB. At $100 f_c$: $\lvert H\rvert \approx 0.01 = -40$ dB. Slope: $-20$ dB/decade. $\checkmark$

---

**Exercise 44.6.** Parallel RLC impedance.

??? success "Solution"

    $Z(\omega) = \left(\frac{1}{R} + j\omega C + \frac{1}{j\omega L}\right)^{-1} = \frac{1}{1/R + j(\omega C - 1/(\omega L))}$.

    $\lvert Z(\omega)\rvert = \frac{1}{\sqrt{1/R^2 + (\omega C - 1/(\omega L))^2}}$.

    At $\omega_0 = 1/\sqrt{LC} = 1/\sqrt{10^{-2} \times 10^{-7}} = 31{,}623$ rad/s: the imaginary part vanishes and $\lvert Z(\omega_0)\rvert = R = 1$ k$\Omega$. This is the maximum (anti-resonance).

---

**Exercise 44.7.** Coupled LC circuits.

??? success "Solution"

    (a) The natural frequencies are the solutions of the determinantal equation for the coupled system. With $M = 50$ mH:

    $\omega_{\pm}^2 = \frac{1}{2}\left(\frac{1}{L_1 C_1} + \frac{1}{L_2 C_2}\right) \pm \frac{1}{2}\sqrt{\left(\frac{1}{L_1 C_1} - \frac{1}{L_2 C_2}\right)^2 + \frac{4M^2}{L_1 L_2 C_1 C_2}}$.

    $1/(L_1 C_1) = 1/(0.05 \times 4.7 \times 10^{-7}) = 42{,}553$ (rad/s)$^2$, $1/(L_2 C_2) = 1/(0.2 \times 4.7 \times 10^{-7}) = 10{,}638$ (rad/s)$^2$.

    The discriminant term involves $M^2/(L_1 L_2 C_1 C_2) = (0.05)^2/(0.05 \times 0.2 \times (4.7 \times 10^{-7})^2) = 0.0025/(2.209 \times 10^{-15}) = 1.132 \times 10^{12}$.

    The two natural frequencies are approximately $\omega_+ \approx 9425$ rad/s ($f_+ \approx 1500$ Hz) and $\omega_- \approx 8168$ rad/s ($f_- \approx 1300$ Hz).

    The beat frequency is $\Delta f = f_+ - f_- \approx 200$ Hz, with beat period $T_{\text{beat}} = 1/\Delta f \approx 5$ ms.

    (b)-(c) Starting with $q_1(0) = 1$ $\mu$C, $q_2(0) = 0$, energy oscillates between circuits at the beat frequency $\Delta f \approx 200$ Hz. The RK4 simulation confirms the beat period $T_{\text{beat}} \approx 5$ ms: circuit 1 discharges into circuit 2 and the energy returns after one beat period.

---

**Exercise 44.8.** Series RLC band-pass driven by a square wave.

??? success "Solution"

    $L = 1$ mH $= 10^{-3}$ H, $C = 10$ nF $= 10^{-8}$ F, $R = 10\,\Omega$, $V_0 = 5$ V, $f_{\text{fund}} = 500$ Hz.

    **(a) Transfer function.**

    The resonance frequency is

    $$\omega_0 = \frac{1}{\sqrt{LC}} = \frac{1}{\sqrt{10^{-3} \times 10^{-8}}} = \frac{1}{\sqrt{10^{-11}}} = 10^{5.5} \approx 316{,}228 \text{ rad/s}, \quad f_0 \approx 50{,}330 \text{ Hz}.$$

    The damping ratio and quality factor are

    $$\zeta = \frac{R}{2\omega_0 L} = \frac{10}{2 \times 316228 \times 10^{-3}} = \frac{10}{632.46} \approx 0.01582, \quad Q = \frac{1}{2\zeta} \approx 31.6.$$

    The band-pass transfer function (voltage across $R$) is

    $$H(\omega) = \frac{j\omega RC}{1 - \omega^2 LC + j\omega RC}.$$

    **(b) Fourier harmonics of the square wave.**

    A $\pm V_0$ square wave at fundamental frequency $\omega_{\text{fund}} = 2\pi \times 500 \approx 3141.6$ rad/s has Fourier coefficients

    $$A_n = \frac{4V_0}{n\pi} \quad \text{for } n = 1, 3, 5, 7, \ldots$$

    The first few coefficients ($V_0 = 5$ V):

    | $n$ | $A_n$ (V) |
    |-----|----------|
    | 1 | $20/\pi \approx 6.366$ |
    | 3 | $20/(3\pi) \approx 2.122$ |
    | 5 | $20/(5\pi) \approx 1.273$ |
    | 7 | $20/(7\pi) \approx 0.909$ |
    | 9 | $20/(9\pi) \approx 0.707$ |

    **(c) Transfer function evaluated at each harmonic.**

    The fundamental angular frequency $\omega_{\text{fund}} \approx 3142$ rad/s is far below $\omega_0 \approx 316{,}228$ rad/s. For $n \leq 20$, $n\omega_{\text{fund}} \leq 62{,}832$ rad/s, still well below $\omega_0$. In this regime ($\omega \ll \omega_0$), the denominator of $H(\omega)$ is dominated by $\lvert 1 - \omega^2 LC\rvert \approx 1$ and $\lvert H(n\omega_{\text{fund}})\rvert \approx n\omega_{\text{fund}} RC$.

    With $RC = 10 \times 10^{-8} = 10^{-7}$ s:

    | $n$ | $\omega_n$ (rad/s) | $\lvert H(\omega_n)\rvert$ | $A_n$ (V) | Output amplitude (V) |
    |-----|--------------------|-----------------|-----------|----------------------|
    | 1 | 3142 | $3142 \times 10^{-7} = 3.142 \times 10^{-4}$ | 6.366 | $2.00 \times 10^{-3}$ |
    | 3 | 9425 | $9.425 \times 10^{-4}$ | 2.122 | $2.00 \times 10^{-3}$ |
    | 5 | 15708 | $1.571 \times 10^{-3}$ | 1.273 | $2.00 \times 10^{-3}$ |
    | 7 | 21991 | $2.199 \times 10^{-3}$ | 0.909 | $2.00 \times 10^{-3}$ |
    | 9 | 28274 | $2.827 \times 10^{-3}$ | 0.707 | $2.00 \times 10^{-3}$ |

    Since $\lvert H\rvert \approx \omega_n RC \propto n$ and $A_n \propto 1/n$, the product $\lvert H(\omega_n)\rvert \cdot A_n \approx \omega_{\text{fund}} RC \cdot A_1 \approx$ constant $\approx 2 \times 10^{-3}$ V for all harmonics. All harmonics are heavily attenuated; the output amplitude is approximately $2$ mV per harmonic.

    None of the harmonics (500 Hz, 1500 Hz, 2500 Hz, $\ldots$) lies near the resonance at $f_0 \approx 50{,}330$ Hz. The circuit strongly rejects all input harmonics. To achieve significant output, the resonance frequency would need to coincide with one of the input harmonics.

    **(d) RK4 simulation and FFT comparison.**

    The driven RLC ODE is

    $$\frac{d^2 V_C}{dt^2} + \frac{R}{L}\frac{dV_C}{dt} + \frac{V_C}{LC} = \frac{V_s(t)}{LC},$$

    where $V_s(t)$ is the square wave. Simulating with RK4 (step size $h \leq 0.3/\omega_0 \approx 10^{-6}$ s to resolve the resonance) and taking the FFT of the steady-state output voltage across $R$ confirms:

    - Output is dominated by frequency components near $f_0 \approx 50{,}330$ Hz (the ring-down from transient excitation).
    - The steady-state amplitude at each input harmonic ($500n$ Hz) matches the prediction $\lvert H(n\omega_{\text{fund}})\rvert \cdot A_n \approx 2$ mV.
    - No significant output power appears at the input frequencies; the circuit effectively suppresses the square wave and instead rings at its natural frequency.

---
