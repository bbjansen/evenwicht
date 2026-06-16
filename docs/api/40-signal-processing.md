<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Signal Processing & Digital Filtering — API Reference

This is the API reference for the TypeScript implementation of Signal Processing & Digital Filtering. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- Delegates to `src/discrete/convolution.ts` — FIR filtering via direct convolution
- Delegates to `src/dynamics/difference.ts` — IIR filtering via difference equations
- Delegates to `src/transforms/fft.ts` — FFT for frequency response, fast convolution, spectral analysis
- Delegates to `src/transforms/spectral.ts` — periodogram and windowing

### Data Representation

Signals are represented as `number[]` arrays. Filter coefficients (FIR taps, IIR feedback/feedforward) are also `number[]`. Complex DFT output uses the paired-array representation from `src/transforms/fft.ts`: an object with `re: number[]` and `im: number[]` fields.

### API Preview

```typescript
import { convolve } from 'evenwicht/discrete/convolution';
import { fft, ifft } from 'evenwicht/transforms/fft';
import { periodogram, hannWindow } from 'evenwicht/transforms/spectral';

// FIR filtering via direct convolution (Ch 20)
const b = [1/5, 1/5, 1/5, 1/5, 1/5];  // 5-point moving average
const y = convolve(b, x);               // returns number[]

// IIR filtering via difference equation (Ch 18)
import { solveDifferenceEquation } from 'evenwicht/dynamics/difference';

const bCoeffs = [0.1];                   // feedforward
const aCoeffs = [1, -0.9];              // feedback: y[n] - 0.9*y[n-1] = 0.1*x[n]
const yIIR = solveDifferenceEquation(aCoeffs, bCoeffs, x);

// Frequency response via FFT (Ch 22)
const Nfft = 512;
const hPadded = [...b, ...new Array(Nfft - b.length).fill(0)];
const H = fft(hPadded);
const magnitude = H.re.map((re, k) =>
  Math.sqrt(re * re + H.im[k] * H.im[k])
);

// Fast convolution via FFT
const L = nextPowerOfTwo(x.length + b.length - 1);
const X = fft(zeroPad(x, L));
const Hf = fft(zeroPad(b, L));
const Yre = X.re.map((xr, k) => xr * Hf.re[k] - X.im[k] * Hf.im[k]);
const Yim = X.re.map((xr, k) => xr * Hf.im[k] + X.im[k] * Hf.re[k]);
const yFast = ifft({ re: Yre, im: Yim }).re.slice(0, x.length + b.length - 1);

// Spectral analysis with Hann window
const w = hannWindow(x.length);
const xWindowed = x.map((v, n) => v * w[n]);
const P = periodogram(xWindowed);

// Noise removal
const Xnoisy = fft(noisySignal);
const threshold = 50;
const Xclean = {
  re: Xnoisy.re.map((r, k) =>
    Math.sqrt(r * r + Xnoisy.im[k] * Xnoisy.im[k]) > threshold ? r : 0
  ),
  im: Xnoisy.im.map((im, k) =>
    Math.sqrt(Xnoisy.re[k] * Xnoisy.re[k] + im * im) > threshold ? im : 0
  ),
};
const cleaned = ifft(Xclean).re;
```


```typescript
import { convolve } from 'evenwicht/discrete/convolution';
import { fft, ifft, periodogram, hannWindow } from 'evenwicht/transforms';

/** FIR filter: output = convolve(coefficients, signal). */
function firFilter(b: number[], x: number[]): number[];

/** Frequency response magnitude: |H(e^{j*omega})| via zero-padded FFT of h. */
function frequencyResponse(h: number[], N: number): number[];
```

### Error Handling

- FIR and IIR filtering inherit error behaviour from `convolve` and `solveDifferenceEquation` respectively.
- Fast convolution via FFT requires matching lengths; inputs are zero-padded to the next power of two internally.
- Spectral thresholding for noise removal is heuristic; no error is thrown for poor threshold choices.

### Dependencies

- `src/discrete/convolution.ts` — direct convolution for FIR filtering
- `src/dynamics/difference.ts` — difference equation solver for IIR filtering
- `src/transforms/fft.ts` — FFT/IFFT for fast convolution and frequency response
- `src/transforms/spectral.ts` — periodogram and windowing functions

### Usage Examples

```typescript
import { convolve } from 'evenwicht/discrete';
import { fft, ifft, hannWindow, periodogram } from 'evenwicht/transforms';

// 5-point moving average FIR filter
const b = [0.2, 0.2, 0.2, 0.2, 0.2];
const signal = [1, 0, 0, 0, 0, 0, 0, 0];
const smoothed = convolve(b, signal);

// Spectral analysis with Hann windowing
const N = 128;
const tone = Array.from({ length: N }, (_, k) => Math.sin(2 * Math.PI * 10 * k / N));
const w = hannWindow(N);
const windowed = tone.map((v, n) => v * w[n]);
const psd = periodogram(windowed);
```

### Connections

This chapter synthesises Chapter 18 (IIR filters ARE difference equations; stability requires poles inside the unit circle), Chapter 20 (FIR filters ARE discrete convolution; the shift operator defines filter delays) and Chapter 22 (the FFT computes frequency responses and enables fast convolution). It connects forward to Chapter 29 (Control Systems — transfer functions and frequency-domain design) and Chapter 38 (Climate Modelling — spectral analysis of oscillations). It builds on the operator perspective of Chapter 23 (a filter is a polynomial or rational function of the shift operator $L$).

- **Chapter 18 (Difference Equations)**: IIR filters are linear constant-coefficient difference equations. The stability criterion (poles inside the unit circle) is Theorem 18.3 applied to the filter's feedback polynomial. Every result on homogeneous and particular solutions from Chapter 18 applies directly to IIR filter analysis.

- **Chapter 20 (Discrete Operators)**: FIR filtering IS convolution (Theorem 20.17). The shift operator $L$ from Chapter 20 is the one-sample delay in signal processing. The difference operator $\Delta = 1 - L$ is the first-difference high-pass filter. Every FIR filter is a polynomial in $L$: $H(L) = b_0 + b_1 L + \cdots + b_M L^M$.

- **Chapter 22 (Transforms)**: The FFT provides efficient frequency response computation (Theorem 22.5), fast convolution (Theorem 22.3(c)), spectral analysis (Definition 22.7) and noise removal (Definition 22.8). The convolution theorem (Chapter 22, Theorem 22.3(c)) is the mathematical basis of fast filtering.

- **Chapter 23 (Operator Algebra)**: A filter is a polynomial (FIR) or rational function (IIR) of the shift operator, living in the operator ring developed in Chapter 23. Filter cascading is operator composition; parallel filters sum.

- **Chapter 21 (Time Series)**: ARMA models are IIR filters driven by white noise. The MA part is FIR, the AR part introduces feedback. Spectral analysis of time series (periodogram, power spectral density) uses identical tools.



### What Is Implemented vs. Documented Only

- [x] FIR filtering via `convolve()` from `src/discrete/convolution.ts`
- [x] IIR filtering via `solveDifferenceEquation()` from `src/dynamics/difference.ts`
- [x] FFT and IFFT from `src/transforms/fft.ts`
- [x] Periodogram and windowed periodogram from `src/transforms/spectral.ts`
- [x] Hann and Hamming window functions from `src/transforms/spectral.ts`
- [x] Fast convolution via FFT (composed from existing FFT primitives)
- [x] Frequency response computation (composed from FFT and zero-padding)
- [ ] Optimal FIR design (Parks–McClellan) — documented only, not implemented

---


### Implementation Context

**FIR filtering via direct convolution.** FIR filtering delegates to `convolve()` with $O(N_x \cdot M)$ complexity for signal length $N_x$ and filter length $M$. For large $M$, floating-point accumulation error is bounded by $(M+1)\varepsilon \cdot \max|b_k x_{n-k}|$, which remains well below observable error for typical filter lengths ($M \leq 1000$). Kahan compensated summation is available for very long filters.

**IIR filtering via difference equations.** IIR filters delegate to `solveDifferenceEquation()` from Chapter 18. Stability requires all poles of the feedback polynomial to lie inside the unit circle. When poles approach the unit circle (narrow-band filters), coefficient quantisation can shift poles outside, causing instability. The standard mitigation is to factor into cascaded second-order sections (biquads).

**Fast convolution via FFT.** For $M > \sim 64$, FFT-based convolution ($O(L \log L)$ with $L$ the zero-padded length) is faster than direct convolution. Both signal and filter are zero-padded to the next power of two to match lengths. The FFT introduces $O(\varepsilon\sqrt{N\log N})$ relative error, which is approximately $10^{-13}$ for $N = 10^6$ in double precision.

**Edge effects.** Filtering a finite signal produces transient artefacts in the first $M$ output samples. The implementation uses zero-extension by default (assuming $x[n] = 0$ for $n < 0$), appropriate for causal real-time filtering. Periodic and symmetric extensions are alternative conventions not currently exposed.

**Spectral analysis.** The periodogram computes $P_k = 2\Delta t |X_k|^2/N$ from the FFT output. The Hann window reduces spectral leakage at the cost of slightly broadened peaks and halved amplitude. Frequency resolution is $\Delta f = 1/(N\Delta t)$; zero-padding interpolates the spectrum but does not improve true resolution.

**Testing strategy.** FIR tests verify the impulse response and compare direct convolution against FFT-based convolution for consistency. IIR tests check known RC low-pass step responses ($y[n] \to 1$ exponentially). Frequency response tests verify magnitude at DC and Nyquist against analytical formulas. Spectral tests confirm that a pure tone produces a single peak at the correct frequency bin.
