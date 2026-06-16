<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Electromagnetism & Circuit Analysis — API Reference

This is the API reference for the TypeScript implementation of Electromagnetism & Circuit Analysis. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- Delegates to `src/linear/solve.ts` — nodal analysis ($G\mathbf{v} = \mathbf{i}_s$)
- Delegates to `src/linear/eigen.ts` — RLC damping classification via eigenvalues
- Delegates to `src/dynamics/ode.ts` — RK4 for RC, RL, RLC transient simulation
- Delegates to `src/transforms/fft.ts` — frequency response computation

### Data Representation

Circuit state variables (node voltages, capacitor voltages, inductor currents) are stored as `number[]`. The ODE right-hand side function has signature `(t: number, y: number[]) => number[]`, matching the `integrateRK4` interface from `evenwicht/ode`. Matrices (conductance, inductance) use `number[][]` (array of rows), consistent with the linear algebra routines from `evenwicht/linalg`.

Complex impedances are represented as pairs `[re, im]` or as two separate arrays `{ re: number[], im: number[] }` for frequency response vectors, matching the FFT output format from `evenwicht/transforms/fft`.

### API Preview

```typescript
import { integrateRK4 } from 'evenwicht/dynamics/ode';
import { solveLinearSystem, eigenvalues, invertMatrix } from 'evenwicht/linear';
import { fft } from 'evenwicht/transforms/fft';

// Nodal analysis: Gv = i_s
const G = [[0.3, -0.1, -0.2], [-0.1, 0.2, -0.1], [-0.2, -0.1, 0.3]];
const i_s = [1.0, 0.0, -1.0];
const v = solveLinearSystem(G, i_s);  // node voltages

// RC charging curve via ODE
const R = 1000;   // 1 kΩ
const C = 1e-6;   // 1 μF
const tau = R * C; // 1 ms
const rcODE = (t: number, y: number[]): number[] => {
  const Vs = 5.0;  // step input
  return [(Vs - y[0]) / tau];
};
const vcTrace = integrateRK4(rcODE, [0], 0, 5 * tau, tau / 100);

// RLC circuit simulation
const L = 0.1;    // 100 mH
const Cr = 1e-6;  // 1 μF
const Rr = 10;    // 10 Ω
const omega0 = 1 / Math.sqrt(L * Cr);
const zeta = Rr / (2 * omega0 * L);
const rlcODE = (_t: number, y: number[]): number[] => {
  return [y[1], -2 * zeta * omega0 * y[1] - omega0 * omega0 * y[0]];
};
const rlcTrace = integrateRK4(rlcODE, [1, 0], 0, 0.05, 1e-5);

// Eigenvalues for RLC classification
const companion = [[0, 1], [-omega0 * omega0, -2 * zeta * omega0]];
const evals = eigenvalues(companion);

// Frequency response of RC low-pass
const Nf = 1000;
const freqHz = Array.from({ length: Nf }, (_, k) => 10 * Math.pow(10, 4 * k / (Nf - 1)));
const magnitude = freqHz.map(f => {
  const w = 2 * Math.PI * f;
  return 1 / Math.sqrt(1 + (w * tau) ** 2);
});
const phaseRad = freqHz.map(f => {
  const w = 2 * Math.PI * f;
  return -Math.atan(w * tau);
});
```

### Error Handling

- Nodal analysis throws if the conductance matrix $G$ is singular (disconnected network or floating node).
- RLC eigenvalue classification uses the discriminant of the characteristic equation; returns `'underdamped'`, `'critically_damped'`, or `'overdamped'`.
- Time-domain simulations throw if `dt <= 0` or `tEnd <= 0`.

### Dependencies

- `src/linear/solve.ts` — Gaussian elimination for nodal voltage analysis
- `src/linear/eigen.ts` — eigenvalue computation for RLC classification
- `src/dynamics/ode.ts` — RK4 for all transient circuit simulations
- `src/transforms/fft.ts` — FFT for frequency response computation

### Usage Examples

```typescript
import { solveODE } from 'evenwicht/dynamics';
import { solve } from 'evenwicht/linear';

// Nodal analysis of 3-node resistive network
const G = [[0.3, -0.1, -0.2], [-0.1, 0.2, -0.1], [-0.2, -0.1, 0.3]];
const i_s = [1.0, 0.0, -1.0];
// const v = solve(G, i_s);  // node voltages

// RC charging curve: tau = R*C = 1ms
const tau = 0.001;
const rc = solveODE(
  (t, y) => (5.0 - (y as number)) / tau,
  0, 0,
  { method: 'rk4', tEnd: 0.005, stepSize: tau / 100 },
);
// rc.y approaches 5.0 (step input voltage)
```

### Connections

This chapter synthesises Chapter 9 (node voltage analysis is a linear system solve), Chapter 18 (discrete-time filters are the digital realisation of analogue circuit responses), Chapter 19 (RC, RL and RLC circuits are ODEs integrated by RK4) and Chapter 22 (impedance and transfer functions are the Laplace/Fourier-domain representation of circuit equations). It connects backward to Chapter 39 (the RLC circuit IS a damped harmonic oscillator with different physical units) and Chapter 40 (frequency response of analogue filters corresponds to that of digital filters). It connects forward to power electronics, RF engineering and integrated circuit design.

- **Chapter 9 (Matrices & Linear Transformations)**: Kirchhoff's laws at resistive nodes produce the linear system $G\mathbf{v} = \mathbf{i}_s$ (Theorem 9.14). Node voltage analysis IS solving $A\mathbf{x} = \mathbf{b}$. The conductance matrix is symmetric and positive semi-definite, amenable to Cholesky decomposition (Chapter 9, Section 3). The condition number of $G$ determines solution accuracy (Chapter 9, Section 6).

- **Chapter 18 (Difference Equations)**: Discrete-time filters (digital implementations of analogue circuit functions) are linear constant-coefficient difference equations. The first-order IIR low-pass filter $y[n] = (1-\alpha)x[n] + \alpha y[n-1]$ is the discrete-time counterpart of the analogue RC low-pass. The bilinear transform maps continuous-time transfer functions $H(s)$ to discrete-time transfer functions $H(z)$, preserving stability (poles in the left half-plane map to poles inside the unit circle).

- **Chapter 19 (Ordinary Differential Equations)**: RC, RL and RLC circuits are first- and second-order ODEs, solved by the same RK4 integrator used for mechanical systems. The RC circuit $\tau\dot{V} + V = V_s$ is a first-order linear ODE; the RLC circuit is a second-order linear ODE. Coupled circuits produce systems of coupled ODEs.

- **Chapter 22 (Transforms & Spectral Analysis)**: Impedance is the Laplace-domain representation of a circuit element. The transfer function $H(\omega)$ is the Fourier transform of the impulse response. The FFT computes frequency responses and spectral content of circuit signals. The convolution theorem relates time-domain and frequency-domain filtering.

- **Chapter 39 (Classical Mechanics & Waves)**: The series RLC circuit is mathematically identical to the damped harmonic oscillator (Section 3.5). The correspondences are $L \leftrightarrow m$ (inductance is electrical inertia), $R \leftrightarrow b$ (resistance is electrical damping), $1/C \leftrightarrow k$ (elastance is electrical stiffness) and $q \leftrightarrow x$ (charge is electrical displacement). All results on resonance, quality factor and damping classification carry over directly.

- **Chapter 40 (Signal Processing & Digital Filtering)**: The RC low-pass filter's transfer function $H(\omega) = 1/(1 + j\omega\tau)$ has the same functional form as the first-order IIR low-pass. Band-pass filters built from RLC circuits realise the same frequency selectivity achieved digitally. The analogue-to-digital bridge (Section 3.10) connects the continuous-time circuits of this chapter to the discrete-time processing of Chapter 40.



### What Is Implemented vs. Documented Only

- [x] Nodal analysis via `solveLinearSystem()` from `evenwicht/linalg`
- [x] RC and RL transient simulation via `integrateRK4()` from `evenwicht/ode`
- [x] RLC second-order simulation via `integrateRK4()` from `evenwicht/ode`
- [x] Eigenvalue-based damping classification via `eigenvalues()` from `evenwicht/linalg`
- [x] Frequency response computation (composed from impedance algebra)
- [x] Coupled circuit natural frequencies via `eigenvalues()` and `invertMatrix()` from `evenwicht/linalg`
- [x] FFT-based spectral analysis of circuit responses via `fft()` from `evenwicht/transforms/fft`
- [ ] SPICE-like netlist parser (documented only, not implemented)
- [ ] Implicit integration for stiff circuits — documented only, not implemented

---


### Implementation Context

**Nodal analysis as a linear solve.** The conductance matrix $G$ is symmetric positive semi-definite and assembled from branch conductances. The system $G\mathbf{v} = \mathbf{i}_s$ is solved by Gaussian elimination from `evenwicht/linear/solve`. For networks with widely differing resistance values, $\kappa(G) \approx R_{\max}/R_{\min}$ can be large; when $\kappa > 10^{12}$, node voltages lose significant digits. Sparse solvers would reduce cost to $O(n)$ for tree-structured topologies but are not currently used.

**RC/RL as scalar ODEs.** First-order circuits produce scalar ODEs with time constant $\tau = RC$ or $\tau = L/R$. RK4 requires $h \leq \tau/5$ for four-digit accuracy; $h = \tau/100$ provides excellent results across the full transient. The analytical solution $V_C(t) = V_s(1 - e^{-t/\tau})$ is a verification benchmark.

**RLC damping classification.** The companion matrix eigenvalues $\lambda_\pm = -\zeta\omega_0 \pm \omega_0\sqrt{\zeta^2 - 1}$ classify damping directly. The discriminant is computed before integration, avoiding redundant computation. For underdamped circuits ($\zeta < 1$), the step size must resolve both the oscillation ($h \leq \pi/(10\omega_d)$) and the decay envelope ($h \leq 1/(20\zeta\omega_0)$); the smaller constraint governs.

**Stiffness in multi-timescale circuits.** Circuits combining fast parasitic capacitances ($\tau \sim \text{ps}$) with slow RC stages ($\tau \sim \text{ms}$) produce stiffness ratios exceeding $10^9$. RK4 must step at the fast timescale, making explicit integration impractical. Implicit methods (backward Euler, trapezoidal rule) are documented but not implemented.

**Frequency response sampling.** For high-$Q$ resonance ($Q > 100$), the peak bandwidth $\Delta\omega = \omega_0/Q$ is narrow. At least 10 points within the $-3$ dB bandwidth are needed to capture the peak shape. A logarithmic frequency grid is more efficient than a linear one for spanning multiple decades.

**Testing strategy.** Nodal analysis tests verify Kirchhoff's current law at each node. RC transient tests compare numerical output against the exact exponential solution. RLC tests verify resonance frequency $\omega_0 = 1/\sqrt{LC}$ and the $Q$-factor from the decay envelope. Eigenvalue classification is checked against the analytical discriminant $\zeta^2 - 1$.
