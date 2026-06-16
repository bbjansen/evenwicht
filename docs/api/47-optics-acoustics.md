<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Optics & Acoustics — API Reference

This is the API reference for the TypeScript implementation of Optics & Acoustics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/applications/optics.ts` — ABCD ray transfer matrices, diffraction patterns, Doppler shift
- Delegates to `src/linear/` — matrix multiplication for optical system chains
- Delegates to `src/linear/eigen.ts` — eigenvalue computation for pipe/room resonance frequencies
- Delegates to `src/transforms/fft.ts` — FFT for sound spectral analysis

### Data Representation

Optical ray states are 2-element arrays `[y, theta]` (height and angle). ABCD matrices are `number[][]` of size $2 \times 2$. Sound signals are `number[]` arrays. Stiffness matrices for pipe discretisation are `number[][]`. Noise generators produce `number[]` arrays.

### ABCD Matrix Helpers

```typescript
import { matMul } from 'evenwicht/linear';

function propagationMatrix(d: number): number[][] {
  return [[1, d], [0, 1]];
}

function thinLensMatrix(f: number): number[][] {
  return [[1, 0], [-1 / f, 1]];
}

function systemMatrix(elements: number[][][]): number[][] {
  let M: number[][] = [[1, 0], [0, 1]]; // identity
  for (const elem of elements) {
    M = matMul(elem, M);
  }
  return M;
}

function traceRay(M: number[][], y: number, theta: number): [number, number] {
  const yOut = M[0][0] * y + M[0][1] * theta;
  const thetaOut = M[1][0] * y + M[1][1] * theta;
  return [yOut, thetaOut];
}
```

### Pipe Discretisation

```typescript
function pipeStiffnessMatrix(N: number, vs: number, dx: number): number[][] {
  const c = (vs * vs) / (dx * dx);
  const K: number[][] = Array.from({ length: N }, () => Array(N).fill(0));
  for (let i = 0; i < N; i++) {
    K[i][i] = 2 * c;
    if (i > 0) K[i][i - 1] = -c;
    if (i < N - 1) K[i][i + 1] = -c;
  }
  return K;
}
```

### Noise Generation

```typescript
function whiteNoise(N: number): number[] {
  const x: number[] = [];
  for (let i = 0; i < N; i++) {
    const u1 = Math.random(), u2 = Math.random();
    x.push(Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2));
  }
  return x;
}

function brownianNoise(N: number): number[] {
  const w = whiteNoise(N);
  const b: number[] = [w[0]];
  for (let i = 1; i < N; i++) b.push(b[i - 1] + w[i]);
  return b;
}
```

### API Preview

```typescript
// ODE integration (Chapter 19)
import { integrateRK4 } from 'evenwicht/dynamics/ode';
// integrateRK4(f, y0, t0, tEnd, h) => number[][]

// Eigenvalue computation (Chapter 10)
import { eigenvalues, eigenvectors } from 'evenwicht/linear';
// eigenvalues(A: number[][]) => number[]
// eigenvectors(A: number[][]) => number[][]

// Matrix operations (Chapter 9)
import { matMul } from 'evenwicht/linear';
// matMul(A: number[][], B: number[][]) => number[][]

// FFT (Chapter 22)
import { fft } from 'evenwicht/transforms/fft';
// fft(x: number[]) => { re: number[], im: number[] }

// Vector operations (Chapter 8)
import { dot, norm, scale, add } from 'evenwicht/linear/vector';
```

### Error Handling

- `thinLensMatrix` throws if `f === 0` (focal length cannot be zero).
- `pipeStiffnessMatrix` throws if $N < 1$.
- `traceRay` returns `NaN` values if the ABCD matrix contains `NaN` (e.g., from singular optical systems).
- Noise generators produce normally distributed samples via the Box-Muller transform.

### Dependencies

- `src/linear/` — matrix multiplication for ABCD matrix chains
- `src/linear/eigen.ts` — eigenvalue computation for pipe and room resonance frequencies
- `src/transforms/fft.ts` — FFT for sound frequency analysis

### Usage Examples

```typescript
// ABCD ray tracing: propagation 10cm then thin lens f=5cm
const M_prop = [[1, 0.1], [0, 1]];
const M_lens = [[1, 0], [-1/0.05, 1]];
// System matrix = M_lens * M_prop
const M = [
  [M_lens[0][0] * M_prop[0][0] + M_lens[0][1] * M_prop[1][0],
   M_lens[0][0] * M_prop[0][1] + M_lens[0][1] * M_prop[1][1]],
  [M_lens[1][0] * M_prop[0][0] + M_lens[1][1] * M_prop[1][0],
   M_lens[1][0] * M_prop[0][1] + M_lens[1][1] * M_prop[1][1]],
];

// Trace a ray at height 0.01m, angle 0
const [yOut, thetaOut] = [M[0][0] * 0.01 + M[0][1] * 0, M[1][0] * 0.01 + M[1][1] * 0];
```

### Connections

This chapter synthesises Chapter 10 (eigenvalues determine the resonance frequencies of pipes, strings and rooms), Chapter 22 (the FFT decomposes sound into frequency components; diffraction patterns are Fourier transforms of apertures) and Chapter 39 (wave superposition, standing waves and driven oscillator resonance provide the physical foundation). It connects forward to signal processing (Ch 40, where spectral methods filter acoustic signals) and control systems (Ch 29, where resonance and frequency response are central design tools).

- **Chapter 10 (Eigenvalues)**: Pipe and room resonance frequencies are eigenvalues of the discretised Laplacian (Theorems 47.6, 47.20). The eigenvalue solver converts boundary conditions into frequencies.

- **Chapter 22 (Transforms)**: The FFT decomposes sound into harmonics (Example 47.30) and verifies beats (Example 47.29). The single-slit diffraction pattern is the Fourier transform of the aperture (Theorem 47.12).

- **Chapter 39 (Mechanics & Waves)**: The wave equation, resonance and superposition from Chapter 39 provide the physical foundations. The quality factor (Theorem 47.8) is the same quantity defined in Chapter 39. Pipe standing waves are acoustic analogues of string vibrations.

- **Chapter 9 (Matrices)**: ABCD ray tracing reduces to matrix multiplication (Theorem 47.16). The imaging condition (Theorem 47.17) is an algebraic condition on a matrix element.

- **Chapter 40 (Signal Processing)**: Acoustic spectral analysis uses the FFT methods of Chapter 40. Windowing, spectral leakage and the Nyquist criterion apply identically.



### What Is Implemented vs. Documented Only

- [x] ABCD ray transfer matrices (propagation, thin lens, system composition)
- [x] Ray tracing through optical systems via matrix multiplication
- [x] Pipe discretisation stiffness matrix for acoustic resonance
- [x] Normal mode analysis via eigenvalue computation
- [x] FFT-based frequency analysis of acoustic signals
- [x] White noise and Brownian noise generation utilities
- [ ] Gaussian beam propagation and waist calculations (documented; deferred)
- [ ] Diffraction and interference pattern computation (out of scope; only geometric optics ray tracing is implemented)
- [ ] Acoustic impedance and transmission line models (documented conceptually; deferred)
- [ ] Room acoustics and reverberation modelling (out of scope)

---


### Implementation Context

**ABCD matrix chain multiplication.** Optical systems are modelled by multiplying $2 \times 2$ matrices in encounter order. Each element (propagation, thin lens) has determinant 1, and the product preserves this invariant. The determinant check $|\det(M_{\text{sys}}) - 1| < \varepsilon$ is a numerical integrity diagnostic. `thinLensMatrix` throws if $f = 0$ since a zero focal length is physically meaningless.

**Pipe and room resonance via eigenvalues.** The tridiagonal stiffness matrix for pipe discretisation has analytical eigenvalues $\lambda_k = 4(v_s/\Delta x)^2 \sin^2(k\pi/(2(N+1)))$, providing an $O(N)$ computation. For $N > 100$, the condition number grows as $O(N^2)$, and the highest eigenvalues may lose a few digits if computed numerically. The analytical formula is both the primary computation and a verification benchmark.

**Room modes.** Room mode frequencies $f_{mnp} = (v_s/2)\sqrt{(m/L_x)^2 + (n/L_y)^2 + (p/L_z)^2}$ are enumerated by brute force over mode indices up to $M_{\max}$, then sorted. Complexity is $O(M_{\max}^3 \log M_{\max}^3)$. Below the Schroeder frequency $f_S = 2000\sqrt{T_{60}/V}$, individual modes are resolvable; above it, modes overlap.

**Sinc singularity.** Diffraction patterns involve $\text{sinc}(u) = \sin(\pi u)/(\pi u)$, which has a removable singularity at $u = 0$. Implementations must return 1.0 directly at $u = 0$ to avoid division by zero.

**Noise generation.** White noise uses the Box-Muller transform on pairs of uniform random samples. Brownian noise is the cumulative sum of white noise. Neither generator is cryptographically secure; they are intended for acoustic simulation and spectral analysis demonstrations.

**Testing strategy.** ABCD tests verify that a ray at the focal point of a lens emerges parallel ($\theta_{\text{out}} = 0$). Pipe eigenvalue tests compare numerical and analytical values. FFT spectral tests confirm that a pure tone at frequency $f_0$ produces a peak at the correct bin. Noise spectral slope tests verify white noise ($\beta \approx 0$) and Brownian noise ($\beta \approx -2$) in log-log PSD plots.
