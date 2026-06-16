<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Transforms & Spectral Analysis — API Reference

This is the API reference for the TypeScript implementation of Transforms & Spectral Analysis. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/transforms/`

- `src/transforms/dft.ts` — Naive $O(N^2)$ DFT and inverse DFT
- `src/transforms/fft.ts` — Cooley–Tukey radix-2 FFT
- `src/transforms/spectral.ts` — Periodogram, window functions

### Data Representation

Complex numbers are stored as paired real arrays (`re: number[]`, `im: number[]`) rather than object instances, for cache-friendly access and zero allocation overhead. Real-valued input signals are passed as `number[]`; the DFT output is always complex. The FFT automatically zero-pads to the next power of two when the input length is not a power of two.

### API Preview

```typescript
// src/transforms/dft.ts
/** Naive O(N^2) forward DFT of a real signal. */
function dft(x: number[]): { re: number[]; im: number[] };
/** Naive O(N^2) inverse DFT. */
function idft(re: number[], im: number[]): number[];

// src/transforms/fft.ts
/** Cooley–Tukey radix-2 FFT. Auto-pads to next power of two. */
function fft(x: number[]): { re: number[]; im: number[] };
/** Inverse FFT. */
function ifft(re: number[], im: number[]): number[];

// src/transforms/spectral.ts
/** Periodogram P_k = |X_k|^2 / N. Supports optional windowing. */
function periodogram(x: number[], opts?: { window?: 'hann' | 'hamming' | 'none' }): number[];
/** Hann window coefficients for a signal of length N. */
function hannWindow(N: number): number[];
/** Hamming window coefficients for a signal of length N. */
function hammingWindow(N: number): number[];
```

### Error Handling

- `fft` accepts arbitrary-length input; non-power-of-two lengths are zero-padded internally. The padded length is always the next power of two.
- `idft` and `ifft` throw if `re` and `im` arrays have different lengths.
- `periodogram` returns a one-sided spectrum (bins 0 through N/2) when the input is real-valued, with appropriate doubling of non-DC, non-Nyquist bins.
- Twiddle factors are computed using `Math.cos` and `Math.sin`; accumulated rounding error is bounded by $O(\varepsilon\sqrt{N \log N})$ where $\varepsilon$ is machine epsilon.
- For $N \leq 32$, the naive DFT may be faster than the FFT due to lower overhead.

### Dependencies

- No external module dependencies; the transform implementations are self-contained
- Used by: `src/timeseries/` (spectral analysis), `src/climate/spectral.ts`, `src/geology/` (seismogram analysis)

### Usage Examples

```typescript
import { fft, ifft, periodogram, hannWindow } from 'evenwicht/transforms';

// FFT of a simple signal: 1 Hz sine at 8 Hz sample rate
const N = 64;
const signal = Array.from({ length: N }, (_, k) => Math.sin(2 * Math.PI * k / 8));
const spectrum = fft(signal);
// spectrum.re and spectrum.im contain Fourier coefficients

// Inverse FFT recovers the original signal
const recovered = ifft(spectrum.re, spectrum.im);

// Periodogram with Hann window
const windowed = signal.map((v, n) => v * hannWindow(N)[n]);
const psd = periodogram(windowed);
// Peak at bin corresponding to 1 Hz
```

### Connections

This chapter is used by Chapter 23 (Operators: transforms as operator representations in function spaces; diagonalisation of convolution operators via the DFT). It builds on Chapter 20 (the DFT diagonalises circular convolution, giving the convolution theorem its algebraic meaning) and Chapter 21 (the power spectral density is the Fourier transform of the autocovariance function, linking time-domain and frequency-domain descriptions of stochastic processes). The FFT algorithm exemplifies the divide-and-conquer strategy and connects to the factorisation of the DFT matrix into sparse butterfly stages, a theme that reappears in fast matrix–vector products and structured linear algebra.

- **Discrete Operators** (Chapter 20): The DFT diagonalises the circular convolution operator defined in Chapter 20. The convolution theorem (Theorem 22.3(c)) gives this diagonalisation its algebraic meaning: the DFT matrix simultaneously diagonalises all circulant matrices. The Z-transform introduced in Chapter 20 reduces to the DFT when evaluated at the $N$-th roots of unity.

- **Time Series** (Chapter 21): The power spectral density (Definition 22.7) is the discrete analogue of the Fourier transform of the autocovariance function. For a stationary process with autocovariance $\gamma(h)$, the spectral density $f(\omega) = \sum_{h} \gamma(h) e^{-i\omega h}$ links time-domain and frequency-domain descriptions. The periodogram provides a sample estimate of this spectral density, connecting the statistical framework of Chapter 21 to the transform machinery of this chapter.

- **Operator Algebra** (Chapter 23): The DFT is a change-of-basis operator that diagonalises the shift operator $L$ and, by extension, all operators that are polynomials in $L$. Chapter 23 develops this perspective formally: the DFT matrix factors into sparse butterfly stages, exemplifying the structured factorisation of operators that reappears in fast matrix–vector products.

- **Signal Processing** (Chapter 40): The FFT and spectral analysis tools developed here are the computational foundation for the filtering, modulation and detection algorithms of Chapter 40. The convolution theorem enables fast FIR filtering and the periodogram provides the basic tool for spectrum estimation.



### What Is Implemented vs. Documented Only

- [x] Naive O(N^2) DFT and inverse DFT
- [x] Cooley–Tukey radix-2 FFT with automatic zero-padding
- [x] Periodogram (raw, Hann-windowed, Hamming-windowed)
- [x] Individual window functions (Hann, Hamming) exported for custom pipelines
- [ ] Continuous Fourier transform and inverse (documented theoretically; not implemented as a numerical routine)
- [ ] Laplace transform and Z-transform (documented as contextual theory; not implemented)
- [ ] Non-power-of-two FFT algorithms such as Bluestein or mixed-radix (deferred)
- [ ] Welch's method for spectral density estimation (deferred)
- [ ] Short-time Fourier transform / spectrogram (deferred)

---


### Implementation Context

The Evenwicht implementation spans three files:

- **`src/transforms/dft.ts`** — Naive $O(N^2)$ DFT and inverse DFT. Operates on real-valued input arrays and returns paired `re: number[]` and `im: number[]` output arrays. The inverse DFT conjugates the twiddle factors and scales by $1/N$.

- **`src/transforms/fft.ts`** — Cooley–Tukey radix-2 FFT. Accepts real or complex input (paired arrays). Automatically zero-pads to the next power of two when the input length is not a power of two. Returns paired `re` and `im` arrays.

- **`src/transforms/spectral.ts`** — Periodogram, Hann-windowed periodogram and Hamming-windowed periodogram. Each function accepts a real-valued signal array and returns a power spectral density array. Window functions are also exported individually for use in custom spectral estimation pipelines.
