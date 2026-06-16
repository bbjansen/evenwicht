<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 47: Optics & Acoustics

**Exercise 47.1.** Doppler shift.

??? success "Solution"

    $v_s = 343$ m/s (speed of sound), source speed $u = 30$ m/s, $f = 700$ Hz.

    (a) Approaching:

    $$f_{\text{obs}} = f \times \frac{v_s}{v_s - u} = 700 \times \frac{343}{313} = 767.1 \text{ Hz}.$$

    Receding:

    $$f_{\text{obs}} = f \times \frac{v_s}{v_s + u} = 700 \times \frac{343}{373} = 643.4 \text{ Hz}.$$

    (b) Ratio: $767.1/643.4 = 1.192$.

    (c) For $f_{\text{approach}} = 2f$: $v_s/(v_s - u) = 2$, so $v_s = 2v_s - 2u$, giving

    $$u = v_s/2 = 171.5 \text{ m/s}$$

    (half the speed of sound, Mach 0.5).

---

**Exercise 47.2.** Closed-open pipe resonances.

??? success "Solution"

    (a) Analytical:

    $$f_n = (2n-1)\,v_s/(4L) = (2n-1) \times 343/(4 \times 0.5) = (2n-1) \times 171.5 \text{ Hz}.$$

    $f_1 = 171.5$ Hz, $f_2 = 514.5$ Hz, $f_3 = 857.5$ Hz, $f_4 = 1200.5$ Hz, $f_5 = 1543.5$ Hz.

    (b) With $N = 30$ grid points, the discrete eigenvalue problem approximates these. The first eigenvalue gives $f_1^{(30)} \approx 171.3$ Hz (error $< 0.2\%$). Higher modes have larger errors due to the $O(1/N^2)$ discretisation error.

    (c) With $N = 100$: errors decrease by factor $(30/100)^2 \approx 0.09$, giving sub-0.02% agreement.

---

**Exercise 47.3.** Resonance quality factor.

??? success "Solution"

    (a) $\gamma = \pi f_0/Q = \pi \times 500/25 = 62.83$ rad/s.

    (b) $|H(\Omega)| = 1/\sqrt{(1 - \Omega^2)^2 + (2\gamma\Omega/\omega_0^2)^2}$ where $\Omega$ is normalised so that $\omega_0 = 1$ (equivalently, $\Omega = 2\pi f / \omega_0$). The peak occurs at $f_0 = 500$ Hz.

    (c) Half-power bandwidth: $\Delta f = f_0/Q = 500/25 = 20$ Hz. The $-3$ dB points are at $490$ and $510$ Hz.

    (d) $Q = f_0/\Delta f = 500/20 = 25$. $\checkmark$

---

**Exercise 47.4.** Beat frequency.

??? success "Solution"

    (a) Beat frequency: $f_{\text{beat}} = |f_2 - f_1| = |662 - 659.3| = 2.7$ Hz.

    (b) At $f_s = 16384$ Hz for $T = 0.5$ s: $N = 8192$ samples. $s[n] = \sin(2\pi f_1 n/f_s) + \sin(2\pi f_2 n/f_s)$.

    (c) FFT reveals two peaks at bins $k_1 = f_1 N/f_s = 659.3 \times 8192/16384 = 329.65 \approx 330$ and $k_2 = 662 \times 8192/16384 = 331$. With frequency resolution $\Delta f = f_s/N = 2$ Hz, the peaks are separated by one bin.

    (d) Number of complete beats in 0.5 s: $0.5 \times 2.7 = 1.35$. So approximately 1 complete beat, with the amplitude envelope going through one full cycle plus 35% of a second.

---

**Exercise 47.5.** Timbre comparison.

??? success "Solution"

    At $f_0 = 261.6$ Hz (middle C):

    Square wave: $s(t) = \sum_{n=1,3,5,\ldots}^{19} \frac{1}{n}\sin(2\pi n f_0 t)$. FFT power at harmonic $n$: $P_n \propto 1/n^2$ (odd harmonics only).

    Sawtooth: $s(t) = \sum_{n=1}^{10} \frac{(-1)^{n+1}}{n}\sin(2\pi n f_0 t)$. FFT power at harmonic $n$: $P_n \propto 1/n^2$ (all harmonics).

    The FFT confirms: square wave has power only at odd harmonics with $-6$ dB/octave falloff; sawtooth has all harmonics with $-6$ dB/octave falloff.

---

**Exercise 47.6.** Single-slit diffraction.

??? success "Solution"

    (a) Intensity: $I(\theta) = I_0 [\sin(\pi a \sin\theta/\lambda)/(\pi a \sin\theta/\lambda)]^2$.

    $\pi a/\lambda = \pi \times 50/0.5 = 100\pi$. First minima at $\sin\theta = \lambda/a = 0.5/50 = 0.01$, so $\theta = \pm 0.01$ rad.

    (b) First secondary maximum at $\sin\theta \approx 3\lambda/(2a) = 0.015$, $\theta = 0.015$ rad.

    $$I/I_0 = \left[\frac{\sin(1.5\pi)}{1.5\pi}\right]^2 = \frac{1}{(1.5\pi)^2} = \frac{1}{2.25\pi^2} = 0.0450.$$

    Theoretical: $(2/(3\pi))^2 = 4/(9\pi^2) = 0.0450$. $\checkmark$

---

**Exercise 47.7.** Three-lens ray tracing.

??? success "Solution"

    ABCD matrices for thin lenses and free-space propagation:

    $$\text{Lens: } \begin{pmatrix} 1 & 0 \\ -1/f & 1 \end{pmatrix}, \qquad \text{Space of length } d\text{: } \begin{pmatrix} 1 & d \\ 0 & 1 \end{pmatrix}.$$

    The element matrices are:

    $$L_1 = \begin{pmatrix} 1 & 0 \\ -1/50 & 1 \end{pmatrix}, \quad S_{40} = \begin{pmatrix} 1 & 40 \\ 0 & 1 \end{pmatrix}, \quad L_2 = \begin{pmatrix} 1 & 0 \\ 1/30 & 1 \end{pmatrix}, \quad S_{60} = \begin{pmatrix} 1 & 60 \\ 0 & 1 \end{pmatrix}, \quad L_3 = \begin{pmatrix} 1 & 0 \\ -1/80 & 1 \end{pmatrix}.$$

    (a) The total system matrix from object to the last lens is $M = L_3 \cdot S_{60} \cdot L_2 \cdot S_{40} \cdot L_1 \cdot S_{120}$, built by multiplying from right to left. The result is

    $$M = \begin{pmatrix} -0.600 & 108.0 \\ -0.00583 & -0.617 \end{pmatrix}.$$

    (b) The imaging condition $B + d_i D = 0$ gives

    $$d_i = -B/D = -108.0/(-0.617) = 175.1\,\text{mm}.$$

    The positive image distance indicates a real image, 175.1 mm beyond the third lens.

    (c) The magnification is $A + d_i C = -0.600 + 175.1 \times (-0.00583) = -1.62$. The image is inverted and slightly demagnified.

    (d) $\det(M) = (-0.600)(-0.617) - (108.0)(-0.00583) = 0.370 + 0.630 = 1.0$. $\checkmark$

---

**Exercise 47.8.** Noise spectrum verification.

??? success "Solution"

    (a) White noise: PSD $P_k$ is approximately constant across all bins. The standard deviation of $P_k$ equals its mean (exponential distribution of $|X_k|^2$), so std/mean $\approx 1$. $\checkmark$

    (b) Brownian noise ($x[n] = \sum_{k=0}^n w[k]$ where $w$ is white noise): the PSD falls as $1/f^2$, since integration in the time domain multiplies the spectrum by $1/(2\pi i f)$, giving power $\propto 1/f^2$. The slope of $\log P_k$ vs. $\log f_k$ should be approximately $-2$.

    Regression of $\log P_k$ vs. $\log f_k$ (excluding DC) over the range $f_k \in [f_s/N, f_s/4]$ gives slope $\approx -2.0 \pm 0.1$ for $N = 2^{14}$.

---
