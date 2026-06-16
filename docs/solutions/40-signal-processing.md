<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 40: Signal Processing & Digital Filtering

**Exercise 40.1.** 3-point moving average on $x = [1, 4, 2, 5, 3, 6, 2, 4]$.

??? success "Solution"

    With $b = [1/3, 1/3, 1/3]$ and assuming $x[n] = 0$ for $n < 0$:

    $$\begin{aligned}
    y[0] &= (x[0])/3 = 1/3 \approx 0.333, \\
    y[1] &= (x[1] + x[0])/3 = 5/3 \approx 1.667, \\
    y[2] &= (x[2] + x[1] + x[0])/3 = (2 + 4 + 1)/3 = 7/3 \approx 2.333, \checkmark \\
    y[3] &= (x[3] + x[2] + x[1])/3 = (5 + 2 + 4)/3 = 11/3 \approx 3.667, \\
    y[4] &= (x[4] + x[3] + x[2])/3 = (3 + 5 + 2)/3 = 10/3 \approx 3.333, \\
    y[5] &= (x[5] + x[4] + x[3])/3 = (6 + 3 + 5)/3 = 14/3 \approx 4.667, \\
    y[6] &= (x[6] + x[5] + x[4])/3 = (2 + 6 + 3)/3 = 11/3 \approx 3.667, \\
    y[7] &= (x[7] + x[6] + x[5])/3 = (4 + 2 + 6)/3 = 12/3 = 4.000.
    \end{aligned}$$

    $\square$

---

**Exercise 40.2.** IIR filter $y[n] = 0.5x[n] + 0.8y[n-1]$.

??? success "Solution"

    This is a first-order IIR with $b_0 = 0.5$, $a_1 = -0.8$. With the convention $y[n] + a_1 y[n-1] = b_0 x[n]$, the coefficient is $a_1 = -0.8$; equivalently, $y[n] = b_0 x[n] - a_1 y[n-1]$ with $-a_1 = 0.8$. The feedback polynomial is $A(z) = 1 - 0.8z^{-1}$, with pole at $z = 0.8$.

    Since $\lvert 0.8\rvert < 1$, the filter is **stable**.

    Impulse response ($x[n] = \delta[n]$, $y[-1] = 0$):

    $y[0] = 0.5 \times 1 + 0.8 \times 0 = 0.5$

    $y[1] = 0.5 \times 0 + 0.8 \times 0.5 = 0.4$

    $y[2] = 0 + 0.8 \times 0.4 = 0.32$

    $y[3] = 0 + 0.8 \times 0.32 = 0.256$

    $y[4] = 0 + 0.8 \times 0.256 = 0.2048$

    The impulse response is $h[n] = 0.5 \times 0.8^n$ for $n \geq 0$, decaying geometrically.

    $\square$

---

**Exercise 40.3.** Magnitude response of $h = [1, 2, 1]$.

??? success "Solution"

    $H(\omega) = 1 + 2e^{-i\omega} + e^{-2i\omega} = e^{-i\omega}(e^{i\omega} + 2 + e^{-i\omega}) = e^{-i\omega}(2 + 2\cos\omega)$.

    $\lvert H(\omega) \rvert = 2(1 + \cos\omega) = 4\cos^2(\omega/2)$.

    At $\omega = 0$: $\lvert H(0) \rvert = 4\cos^2(0) = 4$.

    At $\omega = \pi/2$: $\lvert H(\pi/2) \rvert = 4\cos^2(\pi/4) = 4 \times 0.5 = 2$.

    At $\omega = \pi$: $\lvert H(\pi) \rvert = 4\cos^2(\pi/2) = 0$.

    Maximum at DC, zero at Nyquist: this is a **low-pass filter**.

    $\square$

---

**Exercise 40.4.** Cascade of two FIR filters.

??? success "Solution"

    Let $h_1$ and $h_2$ be the impulse responses. Cascading means $y = h_2 * (h_1 * x)$. By associativity of convolution: $y = (h_2 * h_1) * x = h * x$ where $h = h_1 * h_2$.

    The order of $h_1 * h_2$: if $h_1$ has order $M_1$ (support $\{0, \ldots, M_1\}$) and $h_2$ has order $M_2$, then $h_1 * h_2$ has support $\{0, \ldots, M_1 + M_2\}$, so the cascaded filter has order $M_1 + M_2$.

    $\square$

---

**Exercise 40.5.** Isolating a 440 Hz tone from noise.

??? success "Solution"

    With $N = 256$ and $f_s = 8000$ Hz, the frequency resolution is $\Delta f = f_s/N = 31.25$ Hz. The DFT bin for 440 Hz is $k = 440/31.25 = 14.08 \approx 14$.

    The procedure is:

    ```
    k_440 = round(440 * N / f_s)          // = 14
    X = DFT(noisy_signal)
    X_clean = zero array of length N
    X_clean[k_440] = X[k_440]             // retain signal bin
    X_clean[N - k_440] = X[N - k_440]     // retain conjugate bin (symmetry)
    recovered = IDFT(X_clean)
    ```

    Only bins $k = 14$ and $k = N - 14 = 242$ (conjugate symmetry) are retained; all other bins are zeroed. The IDFT recovers a pure 437.5 Hz sinusoid (the nearest bin frequency to 440 Hz).

    $\square$

---

**Exercise 40.6.** First-difference followed by accumulator.

??? success "Solution"

    The first difference is $\Delta x[n] = x[n] - x[n-1]$. The accumulator (running sum) is $S[n] = \sum_{k=-\infty}^{n} \Delta x[k]$. This is a telescoping sum:

    $$S[n] = \sum_{k=-\infty}^{n}(x[k] - x[k-1]) = x[n] - \lim_{k\to-\infty} x[k].$$

    If $x[n] = 0$ for $n < 0$ (causal signal), then $S[n] = x[n]$ for $n \geq 0$, recovering the original. In operator notation: $\Delta = 1 - L$ and the accumulator is $(1 - L)^{-1} = \sum_{k=0}^{\infty} L^k$. The composition $(1-L)^{-1}(1-L) = I$ is thus the identity operator.

    This is the discrete analog of the fundamental theorem of calculus: differentiation followed by integration recovers the original function (up to a constant).

    $\square$

---

**Exercise 40.7.** IIR first-order low-pass frequency response.

??? success "Solution"

    $y[n] = (1-\alpha)x[n] + \alpha y[n-1]$. The transfer function is:

    $$\begin{aligned}
    H(\omega) &= \frac{1-\alpha}{1 - \alpha e^{-i\omega}}. \\
    \lvert H(\omega) \rvert^2 &= \frac{(1-\alpha)^2}{\lvert 1 - \alpha e^{-i\omega} \rvert^2} = \frac{(1-\alpha)^2}{(1-\alpha\cos\omega)^2 + (\alpha\sin\omega)^2} = \frac{(1-\alpha)^2}{1 - 2\alpha\cos\omega + \alpha^2}.
    \end{aligned}$$

    At the $-3$ dB cutoff, $\lvert H(\omega_c) \rvert^2 = 1/2 \times \lvert H(0) \rvert^2 = 1/2$. Since $\lvert H(0) \rvert^2 = (1-\alpha)^2/(1-\alpha)^2 = 1$:

    $$\begin{aligned}
    \frac{(1-\alpha)^2}{1 - 2\alpha\cos\omega_c + \alpha^2} &= \frac{1}{2}. \\
    2(1-\alpha)^2 &= 1 - 2\alpha\cos\omega_c + \alpha^2. \\
    2\alpha\cos\omega_c &= 1 + \alpha^2 - 2(1-\alpha)^2 = -1 + 4\alpha - \alpha^2. \\
    \cos\omega_c &= \frac{-1 + 4\alpha - \alpha^2}{2\alpha} = 2 - \frac{1}{2\alpha} - \frac{\alpha}{2}.
    \end{aligned}$$

    As $\alpha \to 1$: $\cos\omega_c \to 2 - 1/2 - 1/2 = 1$, so $\omega_c \to 0$. This confirms that heavier smoothing (larger $\alpha$) produces a lower cutoff frequency.

    $\square$

---

**Exercise 40.8.** Overlap-add method.

??? success "Solution"

    Partition $x$ into blocks of length $B$: $x_i[n] = x[n]$ for $iB \leq n < (i+1)B$, zero elsewhere. Each block is convolved with $h$ via FFT of length $L = B + M - 1$ (zero-padded to the next power of 2). The convolution of each block has length $B + M - 1$, and the overlapping tails (of length $M - 1$) from adjacent blocks are added together.

    Cost per block: $3 \times O(L\log L)$ (two FFTs + one IFFT) $+ O(L)$ for the pointwise multiply. Number of blocks: $\lceil N/B \rceil$.

    Total cost: $O(N/B \times L\log L) = O(N(B+M)/B \times \log(B+M))$.

    To minimise, take the derivative with respect to $B$. Setting $L = B + M$ and ignoring constants:

    $$C(B) \propto \frac{N(B+M)\log(B+M)}{B}.$$

    For $M \ll B$, $C(B) \approx N\log B$, which decreases monotonically with $B$. The unconstrained optimum is therefore $B = N$ (a single FFT over the entire signal), recovering the $O(N\log N)$ cost of Algorithm 40.31. The overlap-add method becomes useful when $N$ is too large to store in memory. Under the constraint $B \leq B_{\max}$, the optimum is $B = B_{\max}$. In practice, $B \approx 4M$ to $8M$ provides a good balance between FFT efficiency and memory usage. When $B = 4M$: $L = 5M$, cost per block $\propto 5M\log(5M)$, number of blocks $= N/(4M)$, total $\propto 1.25 N\log(5M)$.

    $\square$

---
