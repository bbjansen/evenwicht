<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 22: Transforms

**Exercise 22.1.** DFT of the constant signal $x_n = c$.

??? success "Solution"

    $$X_k = \sum_{n=0}^{N-1} x_n \cdot e^{-2\pi i kn/N} = c\sum_{n=0}^{N-1}e^{-2\pi i kn/N}.$$

    For $k = 0$: $X_0 = c\sum_{n=0}^{N-1} 1 = cN$.

    For $k = 1, \ldots, N-1$: Let $\omega = e^{-2\pi i k/N}$. Then $\omega \neq 1$ (since $0 < k < N$), and:

    $$X_k = c \sum_{n=0}^{N-1}\omega^n = c \cdot \frac{1 - \omega^N}{1 - \omega} = c \cdot \frac{1 - e^{-2\pi i k}}{1 - \omega} = c \cdot \frac{1 - 1}{1 - \omega} = 0.$$

    (Since $e^{-2\pi i k} = 1$ for integer $k$.)

    **Interpretation:** All the energy of a constant signal is concentrated at frequency zero (the DC component, $X_0 = cN$). There is no oscillatory content at any nonzero frequency, which matches the intuition that a constant signal has no variation.

    $\square$

---

**Exercise 22.2.** DFT of $x_n = \cos(2\pi k_0 n/N)$.

??? success "Solution"

    Using Euler's formula: $\cos(2\pi k_0 n/N) = \frac{1}{2}(e^{2\pi i k_0 n/N} + e^{-2\pi i k_0 n/N})$.

    $$X_k = \sum_{n=0}^{N-1}\cos\!\left(\frac{2\pi k_0 n}{N}\right) e^{-2\pi i kn/N} = \frac{1}{2}\sum_{n=0}^{N-1}\left(e^{2\pi i(k_0 - k)n/N} + e^{-2\pi i(k_0 + k)n/N}\right).$$

    Each sum is a geometric series that equals $N$ when the exponent is zero (i.e., when $k_0 - k \equiv 0 \pmod{N}$) and $0$ otherwise.

    First sum: $= N$ when $k = k_0$, else $0$.

    Second sum: $= N$ when $k_0 + k \equiv 0 \pmod{N}$, i.e., $k = N - k_0$, else $0$.

    Therefore: $X_{k_0} = N/2$, $X_{N-k_0} = N/2$, and $X_k = 0$ for all other $k$.

    **Comparison with Example 22.13 (sine):** For $x_n = \sin(2\pi k_0 n/N) = \frac{1}{2i}(e^{2\pi i k_0 n/N} - e^{-2\pi i k_0 n/N})$, the DFT gives $X_{k_0} = N/(2i) = -iN/2$ and $X_{N-k_0} = -N/(2i) = iN/2$. The magnitudes are the same ($N/2$), but the **phases differ**: cosine gives purely real coefficients (phase 0), while sine gives purely imaginary coefficients (phase $\pm \pi/2$). This reflects that cosine is an even function (aligned with the real axis in the complex plane) while sine is odd (aligned with the imaginary axis).

    $\square$

---

**Exercise 22.3.** Prove the circular shift property of the DFT.

??? success "Solution"

    The circular shift property states: if $y_n = x_{(n-m) \bmod N}$, then $Y_k = e^{-2\pi i km/N} X_k$.

    **Proof.**

    $$Y_k = \sum_{n=0}^{N-1} y_n e^{-2\pi i kn/N} = \sum_{n=0}^{N-1} x_{(n-m) \bmod N} e^{-2\pi i kn/N}.$$

    Substitute $j = (n - m) \bmod N$, so $n = (j + m) \bmod N$. As $n$ ranges over $\{0, 1, \ldots, N-1\}$, so does $j$ (a bijection modulo $N$).

    $$Y_k = \sum_{j=0}^{N-1} x_j \, e^{-2\pi i k(j+m)/N} = e^{-2\pi i km/N} \sum_{j=0}^{N-1} x_j \, e^{-2\pi i kj/N} = e^{-2\pi i km/N} X_k.$$

    Therefore $Y_k = e^{-2\pi i km/N} X_k$. A circular shift in the time domain corresponds to multiplication by a complex exponential (phase shift) in the frequency domain. The magnitude spectrum is unchanged: $|Y_k| = |X_k|$.

    $\square$

---

**Exercise 22.4.** Circular convolution via DFT.

??? success "Solution"

    $\mathbf{x} = (1, 0, 0, 0)$ and $\mathbf{y} = (1, 1, 1, 1)$, $N = 4$.

    **Step 1: Compute DFTs.**

    $X_k = \sum_{n=0}^{3} x_n e^{-2\pi i kn/4} = x_0 = 1$ for all $k$ (since only $x_0 = 1$ is nonzero).

    So $X_0 = X_1 = X_2 = X_3 = 1$.

    $Y_k = \sum_{n=0}^{3} 1 \cdot e^{-2\pi i kn/4}$. This is $4$ for $k = 0$ and $0$ for $k = 1, 2, 3$ (from Exercise 22.1 with $c = 1$, $N = 4$).

    So $Y_0 = 4$, $Y_1 = Y_2 = Y_3 = 0$.

    **Step 2: Pointwise multiply.** $Z_k = X_k \cdot Y_k$.

    $Z_0 = 1 \cdot 4 = 4$, $Z_1 = Z_2 = Z_3 = 0$.

    **Step 3: Inverse DFT.**

    $z_n = \frac{1}{N}\sum_{k=0}^{N-1} Z_k e^{2\pi i kn/N} = \frac{1}{4}(4 \cdot 1) = 1$ for all $n$.

    So $\mathbf{z} = (1, 1, 1, 1)$.

    **Direct verification.** The circular convolution is:

    $(x \circledast y)_n = \sum_{m=0}^{3} x_m y_{(n-m) \bmod 4}$.

    Since $x_m = 0$ for $m \neq 0$ and $x_0 = 1$:

    $(x \circledast y)_n = x_0 \cdot y_n = y_n = 1$ for all $n$.

    Both methods give $\mathbf{z} = (1, 1, 1, 1)$. $\checkmark$

    $\square$

---

**Exercise 22.5.** Signal parameters: $N = 256$, $f_s = 1000$ Hz, component at 440 Hz.

??? success "Solution"

    **Frequency resolution:** $\Delta f = f_s / N = 1000 / 256 = 3.906$ Hz.

    **Nyquist frequency:** $f_{\text{Nyquist}} = f_s / 2 = 500$ Hz.

    **DFT bin for 440 Hz:** $k = f / \Delta f = 440 / 3.906 = 112.64$. Since this is not an integer, the 440 Hz component does not fall exactly on a bin. It is closest to $k = 113$ (corresponding to $113 \times 3.906 = 441.4$ Hz), and spectral leakage will spread energy to neighboring bins ($k = 112, 113, 114, \ldots$).

    **If $N$ is increased to 512:**

    $\Delta f = 1000 / 512 = 1.953$ Hz (finer resolution).

    $k = 440 / 1.953 = 225.28$. Still not an exact bin, but the leakage is reduced because the frequency resolution is finer.

    $f_{\text{Nyquist}}$ remains $500$ Hz (unchanged, since $f_s$ is the same).

    The key observation is that increasing $N$ (longer observation window) improves frequency resolution, making it easier to distinguish nearby frequency components, but it does not change the maximum resolvable frequency ($f_{\text{Nyquist}}$).

    $\square$

---

**Exercise 22.6.** Implement IDFT using forward DFT.

??? success "Solution"

    **Claim:** $\text{IDFT}(X) = \frac{1}{N}\overline{\text{DFT}(\overline{X})}$.

    **Proof.** The IDFT is defined as:

    $$x_n = \frac{1}{N}\sum_{k=0}^{N-1} X_k \, e^{2\pi i kn/N}.$$

    Now consider the procedure:

    (i) Form $\overline{X}_k$ (complex conjugate of each DFT coefficient).

    (ii) Apply forward DFT: $Y_n = \sum_{k=0}^{N-1} \overline{X}_k \, e^{-2\pi i kn/N}$.

    (iii) Take conjugate: $\overline{Y}_n = \sum_{k=0}^{N-1} X_k \, e^{2\pi i kn/N}$.

    (iv) Divide by $N$: $\frac{\overline{Y}_n}{N} = \frac{1}{N}\sum_{k=0}^{N-1} X_k \, e^{2\pi i kn/N} = x_n$.

    In step (iii), the identity $\overline{\overline{X}_k \, e^{-2\pi i kn/N}} = X_k \, e^{2\pi i kn/N}$ is used (conjugate of a product is the product of conjugates). The result of step (iv) is exactly the IDFT formula.

    ```typescript
    // Assumes Complex has .conjugate() returning the complex conjugate
    // and .scale(c) returning the scalar multiple c * z.
    function idftViaForwardDft(X: Complex[], forwardDft: (x: Complex[]) => Complex[]): Complex[] {
      const N = X.length;
      // (i) Conjugate input
      const Xconj = X.map(z => z.conjugate());
      // (ii) Apply forward DFT
      const Y = forwardDft(Xconj);
      // (iii) Conjugate result, (iv) divide by N
      return Y.map(z => z.conjugate().scale(1 / N));
    }
    ```

    $\square$

---

**Exercise 22.7.** Spectral leakage and windowing for $x_n = \sin(2\pi \cdot 3.5 \cdot n/16)$, $N = 16$.

??? success "Solution"

    The frequency $3.5/16 = 0.21875$ cycles per sample does not correspond to an integer bin (bin $k = 3.5$ is between bins 3 and 4).

    **Without windowing (rectangular window):**

    The periodogram $|X_k|^2$ will show significant power in bins $k = 3$ and $k = 4$ (and their mirror images $k = 12$ and $k = 13$), with nonzero power leaking into all other bins. This is because the rectangular window's spectral representation (a sinc-like function) has large sidelobes.

    ```typescript
    const N = 16;
    const xRect: number[] = [];
    for (let n = 0; n < N; n++) {
      xRect.push(Math.sin(2 * Math.PI * 3.5 * n / N));
    }
    // Compute DFT and periodogram |X_k|^2

    // Hann window: w_n = 0.5 * (1 - cos(2*pi*n/N))
    const xHann: number[] = [];
    for (let n = 0; n < N; n++) {
      const w = 0.5 * (1 - Math.cos(2 * Math.PI * n / N));
      xHann.push(w * Math.sin(2 * Math.PI * 3.5 * n / N));
    }
    // Compute DFT and periodogram |X_k|^2 of windowed signal
    ```

    **With Hann window:** The Hann window $w_n = 0.5(1 - \cos(2\pi n/N))$ has much smaller sidelobes than the rectangular window (first sidelobe at $-31.5$ dB vs. $-13.3$ dB). After applying the Hann window, the periodogram still shows the main peaks near $k = 3$ and $k = 4$, but the leakage into distant bins (e.g., $k = 0, 1, 7, 8, \ldots$) is dramatically reduced. The trade-off is that the main lobe is wider (the peaks at $k = 3$ and $k = 4$ may spread slightly more), but the overall spectral estimate is much cleaner.

    $\square$

---

**Exercise 22.8.** Z-transform of $x_n = a^n u_n$, DTFT and low-pass filter interpretation.

??? success "Solution"

    **Z-transform:**

    $$X(z) = \sum_{n=0}^{\infty} a^n z^{-n} = \sum_{n=0}^{\infty}(az^{-1})^n = \frac{1}{1 - az^{-1}} = \frac{z}{z - a}, \quad |z| > |a|.$$

    **DTFT (evaluate on unit circle $z = e^{i\omega}$):**

    $$X(e^{i\omega}) = \frac{1}{1 - ae^{-i\omega}}.$$

    **Magnitude response:**

    $$\begin{aligned}
    |X(e^{i\omega})|^2 &= \frac{1}{|1 - ae^{-i\omega}|^2} = \frac{1}{(1 - a\cos\omega)^2 + (a\sin\omega)^2} = \frac{1}{1 - 2a\cos\omega + a^2}. \\
    |X(e^{i\omega})| &= \frac{1}{\sqrt{1 - 2a\cos\omega + a^2}}.
    \end{aligned}$$

    **Low-pass filter verification for $0 < a < 1$:**

    At $\omega = 0$ (DC): $|X(e^{i0})| = \frac{1}{\sqrt{1 - 2a + a^2}} = \frac{1}{1 - a}$. For $a = 0.9$: $|X| = 10$.

    At $\omega = \pi$ (Nyquist): $|X(e^{i\pi})| = \frac{1}{\sqrt{1 + 2a + a^2}} = \frac{1}{1 + a}$. For $a = 0.9$: $|X| = 1/1.9 \approx 0.526$.

    The magnitude is maximum at $\omega = 0$ and minimum at $\omega = \pi$. Since the response decreases monotonically from low to high frequencies, this is a **low-pass filter**: it passes low-frequency components (near $\omega = 0$) and attenuates high-frequency components (near $\omega = \pi$). The closer $a$ is to 1, the sharper the roll-off and the stronger the low-pass effect (but also the closer the system is to instability).

    **Sketch for $a = 0.9$:** The magnitude starts at $10$ at $\omega = 0$, decreases smoothly, and reaches $\approx 0.526$ at $\omega = \pi$. The $-3$ dB point (where $|X|$ drops to $10/\sqrt{2} \approx 7.07$) occurs at approximately $\omega = 0.194$ radians.

    $\square$

---
