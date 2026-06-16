<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Classical Mechanics & Waves — API Reference

This is the API reference for the TypeScript implementation of Classical Mechanics & Waves. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/applications/mechanics.ts` — harmonic oscillator, pendulum, projectile motion utilities
- Delegates to `src/dynamics/ode.ts` for RK4 integration
- Delegates to `src/linear/eigen.ts` for normal mode computation
- Delegates to `src/transforms/fft.ts` for frequency analysis

### Data Representation

All mechanical systems are cast as first-order ODE systems $\dot{\mathbf{y}} = \mathbf{f}(t, \mathbf{y})$. The state vector $\mathbf{y}$ is stored as `number[]`. The vector field $\mathbf{f}$ is a function `(t: number, y: number[]) => number[]`. This matches the interface of `integrateRK4` from `evenwicht/ode`.

Matrices (mass, stiffness, dynamical) are stored as `number[][]` (array of rows). The eigenvalue routines from `evenwicht/linalg` accept this format and return eigenvalues as `number[]` and eigenvectors as `number[][]`.

The FFT from `evenwicht/fft` accepts a real-valued array and returns real and imaginary coefficient arrays. The power spectrum is $P_k = \mathrm{re}_k^2 + \mathrm{im}_k^2$.

### Constructing Tridiagonal Matrices

```typescript
function tridiagonalStiffness(N: number, tau: number, dx: number): number[][] {
  const c = tau / dx;
  const K: number[][] = Array.from({ length: N }, () => Array(N).fill(0));
  for (let i = 0; i < N; i++) {
    K[i][i] = 2 * c;
    if (i > 0) K[i][i - 1] = -c;
    if (i < N - 1) K[i][i + 1] = -c;
  }
  return K;
}
```

### Energy Computation Utilities

```typescript
function harmonicEnergy(x: number, v: number, m: number, k: number): number {
  return 0.5 * m * v * v + 0.5 * k * x * x;
}

function pendulumEnergy(
  theta: number, dtheta: number, m: number, l: number, g: number,
): number {
  return 0.5 * m * l * l * dtheta * dtheta + m * g * l * (1 - Math.cos(theta));
}

function relativeEnergyError(Ecurrent: number, E0: number): number {
  return Math.abs(Ecurrent - E0) / Math.abs(E0);
}
```

### Period Detection from Time Series

```typescript
function detectPeriod(timeSeries: number[][], h: number): number {
  // timeSeries[k] = [theta_k, dtheta_k]
  // Find first downward zero-crossing of theta (quarter period from peak)
  // then multiply by 2 for half-period
  let crossings: number[] = [];
  for (let i = 1; i < timeSeries.length; i++) {
    if (timeSeries[i - 1][0] >= 0 && timeSeries[i][0] < 0) {
      // Linear interpolation for sub-step accuracy
      const frac = timeSeries[i - 1][0] /
                   (timeSeries[i - 1][0] - timeSeries[i][0]);
      crossings.push((i - 1 + frac) * h);
    }
  }
  if (crossings.length >= 2) {
    return 2 * (crossings[1] - crossings[0]); // Full period = 2 * half-period
  }
  return NaN;
}
```

### API Preview

```typescript
// ODE integration (Chapter 19)
import { integrateRK4 } from 'evenwicht/dynamics/ode';
// integrateRK4(f, y0, t0, tEnd, h) => number[][]

// Eigenvalue computation (Chapter 10)
import { eigenvalues, eigenvectors, matMul, inverse } from 'evenwicht/linear';
// eigenvalues(A: number[][]) => number[]
// eigenvectors(A: number[][]) => number[][]

// FFT (Chapter 22)
import { fft } from 'evenwicht/transforms/fft';
// fft(x: number[]) => { re: number[], im: number[] }

// Vector operations (Chapter 8)
import { dot, norm, scale, add } from 'evenwicht/linear/vector';
```

### Error Handling

- ODE integration for mechanical systems propagates `NaN` if singular states (zero-length pendulum, division by zero) are reached.
- Tridiagonal matrix construction throws if $N < 1$.
- `detectPeriod` returns `NaN` if fewer than two zero crossings are found (insufficient simulation length).

### Dependencies

- `src/dynamics/ode.ts` — RK4 integration for all equations of motion
- `src/linear/eigen.ts` — eigenvalue computation for normal mode frequencies
- `src/linear/vector.ts` — dot product, norm for energy computation
- `src/transforms/fft.ts` — frequency-domain analysis of vibration signals

### Usage Examples

```typescript
import { solveODE } from 'evenwicht/dynamics';

// Simple harmonic oscillator: x'' + x = 0 => [x', v'] = [v, -x]
const sho = solveODE(
  (t, y) => {
    const s = y as Float64Array;
    return new Float64Array([s[1], -s[0]]);
  },
  0, new Float64Array([1.0, 0.0]),
  { method: 'rk4', tEnd: 6.28, stepSize: 0.01 },
);

// Nonlinear pendulum: theta'' + (g/l)*sin(theta) = 0
const g = 9.81, l = 1.0;
const pendulum = solveODE(
  (t, y) => {
    const s = y as Float64Array;
    return new Float64Array([s[1], -(g / l) * Math.sin(s[0])]);
  },
  0, new Float64Array([0.5, 0.0]),
  { method: 'rk4', tEnd: 20, stepSize: 0.001 },
);
```

### Connections

This chapter synthesises Chapter 4 (velocity is the derivative of position; force is the negative gradient of potential), Chapter 5 (integrating acceleration recovers velocity and position), Chapter 8 (vector operations for multi-dimensional trajectories), Chapter 10 (eigenvalues determine oscillation frequencies and stability), Chapter 19 (RK4 numerically integrates all equations of motion) and Chapter 22 (FFT decomposes vibration signals into frequency components). It connects forward to control systems (Ch 29, where oscillatory plant dynamics require feedback stabilisation) and energy systems (Ch 32, where mechanical vibrations affect turbine design).

- **Differentiation (Ch. 4)**: Velocity is the derivative of position; force is the negative derivative of potential $F = -dV/dx$. Every equation of motion in this chapter involves differentiation.
- **Integration (Ch. 5)**: Integrating acceleration gives velocity; integrating velocity gives position. Free-fall solutions (Theorem 39.2) are obtained by direct antidifferentiation. The work-energy theorem is an integral relation.
- **Vectors (Ch. 8)**: Projectile motion in 2D requires vector state variables. Angular momentum uses the cross product $\mathbf{L} = \mathbf{r} \times m\mathbf{v}$. Kinetic energy is $T = \frac{1}{2}m(\mathbf{v} \cdot \mathbf{v})$.
- **Eigenvalues (Ch. 10)**: Normal mode frequencies are square roots of eigenvalues of $M^{-1}K$ (Theorem 39.9). Damping classification derives from eigenvalues of the companion matrix (Theorem 39.6). String vibration frequencies are eigenvalues of the tridiagonal stiffness matrix (Theorem 39.19). Eigenvalues are THE bridge between linear algebra and oscillatory physics.
- **ODEs (Ch. 19)**: Newton's second law IS an ODE. Every simulation in this chapter uses `integrateRK4`. The reduction to first-order systems follows Chapter 19, Section 3. The characteristic equation of the oscillator uses the eigenvalue theory of linear systems from Chapter 19.
- **Transforms (Ch. 22)**: The FFT extracts frequency content from simulated vibration data (Example 8.5). Mode shapes of the string are the Fourier sine basis (Theorem 39.23). The discrete sine transform decomposes initial conditions into modal amplitudes (Theorem 39.20). Standing waves and superposition connect directly to Fourier analysis.
- **Control Systems (Ch. 29)**: The damped, driven oscillator is the canonical plant model in classical control. Resonance corresponds to the gain peaking that PID tuning must avoid. Transfer function poles are the eigenvalues of the companion matrix.
- **Energy Systems (Ch. 32)**: Turbine blade vibrations, wind-induced structural oscillations and resonance in power grid components are all coupled oscillator problems analysed by the normal mode techniques of this chapter.



### What Is Implemented vs. Documented Only

- [x] Harmonic oscillator and pendulum ODE integration via RK4
- [x] Energy computation utilities (harmonic energy, pendulum energy, relative error)
- [x] Tridiagonal stiffness matrix construction for coupled oscillators / string discretisation
- [x] Normal mode analysis via eigenvalue computation of mass-stiffness systems
- [x] Period estimation from zero-crossing detection
- [x] Power spectrum via FFT for frequency analysis
- [ ] Damped and driven oscillator simulation as standalone functions (documented; the user constructs the ODE directly)
- [ ] Wave equation PDE solvers in 2D or 3D (out of scope; only 1D discrete chain is implemented)
- [ ] Doppler effect and shock wave computation (documented theoretically; not implemented)
- [ ] Nonlinear wave phenomena such as solitons (out of scope)

---


### Implementation Context

**State vector convention.** All mechanical systems are reduced to first-order form $\dot{\mathbf{y}} = \mathbf{f}(t, \mathbf{y})$ with state vectors stored as `number[]`. The harmonic oscillator uses $[x, v]$; the pendulum uses $[\theta, \dot\theta]$; projectile motion uses $[x, y, v_x, v_y]$. This matches the `integrateRK4` interface directly.

**Step size for oscillatory systems.** RK4 requires approximately 20-30 steps per oscillation period for four-digit accuracy: $h \leq 2\pi/(20\,\omega_{\max}) \approx 0.3/\omega_{\max}$. For a vibrating string with $N$ masses, $\omega_{\max}$ grows as $O(N)$, forcing the step size to decrease with refinement.

**Energy drift in non-symplectic integration.** RK4 does not preserve the Hamiltonian. Energy error grows secularly as $|\Delta E| \sim C h^4 \omega^5 T$. Halving $h$ reduces drift by $16\times$. The `relativeEnergyError` utility monitors this drift. For long-time simulations, symplectic integrators (Störmer–Verlet) bound energy error without secular growth but at reduced order ($O(h^2)$).

**Tridiagonal stiffness matrix.** The coupled oscillator and discrete string problems use a tridiagonal $N \times N$ matrix with diagonal $2c$ and off-diagonals $-c$. Eigenvalues are computed by the QR algorithm ($O(N^3)$) or the analytical formula $\lambda_k = 4c\sin^2(k\pi/(2(N+1)))$ ($O(N)$). The frequency ratio $\omega_{\max}/\omega_{\min} \approx (2/\pi)N$ determines the effective stiffness.

**Period detection.** `detectPeriod` uses linear interpolation between zero crossings for sub-step accuracy. It returns `NaN` if fewer than two downward zero crossings are found, indicating insufficient simulation length. Near the separatrix ($\theta_0 \to \pi$), the pendulum period diverges logarithmically and adaptive step sizes become necessary.

**Testing strategy.** Harmonic oscillator tests compare numerical trajectories against the analytical solution $x(t) = A\cos(\omega t + \phi)$. Pendulum tests verify energy conservation and compare the small-angle period $2\pi\sqrt{l/g}$ against the numerically detected period. Normal mode tests check eigenvalue-derived frequencies against FFT peaks from simulated time series.
