<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Energy Systems & Nuclear Engineering — API Reference

This is the API reference for the TypeScript implementation of Energy Systems & Thermodynamics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/applications/energy.ts`

- `src/energy/radioactive-decay.ts` — Exponential decay, half-life, Bateman chain
- `src/energy/heat-transfer.ts` — Newton's cooling, Fourier's law, slab conduction
- `src/energy/economic-dispatch.ts` — Optimal generator dispatch

### Data Representation

Physical quantities use plain `number` types with SI units (seconds, meters, Kelvin, Watts, Becquerels). The economic dispatch module uses a `Generator` interface for per-unit cost parameters and constraints.

### API Preview

```typescript
// src/energy/radioactive-decay.ts
function decayRemaining(N0: number, lambda: number, t: number): number;
function halfLife(lambda: number): number;
function decayConstant(tHalf: number): number;
function activity(N0: number, lambda: number, t: number): number;
/** Bateman three-member chain N1 -> N2 -> N3 (stable). Requires lambda1 !== lambda2. */
function batemanThreeChain(N10: number, lambda1: number, lambda2: number, t: number): [number, number, number];

// src/energy/heat-transfer.ts
/** Newton's cooling: T(t) = T_env + (T0 - T_env) * exp(-hPrime * t). */
function newtonCooling(T0: number, Tenv: number, hPrime: number, t: number): number;
/** Steady-state slab temperature (linear interpolation). */
function slabTemperature(T1: number, T2: number, L: number, x: number): number;
/** Heat flux q = k * (T1 - T2) / L in W/m^2. */
function slabHeatFlux(k: number, T1: number, T2: number, L: number): number;

// src/energy/economic-dispatch.ts
interface Generator { b: number; c: number; pMin: number; pMax: number; }
interface DispatchResult { outputs: number[]; systemMarginalCost: number; totalCost: number; }
/**
 * Economic dispatch with quadratic cost C_i = b_i*P_i + c_i*P_i^2.
 * Uses equal incremental cost criterion with iterative constraint handling.
 */
function economicDispatch(generators: Generator[], demand: number): DispatchResult;
```

### Error Handling

- `halfLife` and `decayConstant` throw if the input is non-positive.
- `batemanThreeChain` throws if `lambda1` and `lambda2` are equal (within relative tolerance $10^{-15}$); the degenerate case requires a separate formula.
- `slabTemperature` throws if the position `x` is outside `[0, L]`.
- `economicDispatch` throws if total generator capacity (sum of `pMax`) is less than demand, or if the iterative constraint resolution does not converge within `n + 1` iterations.
- `activity` returns values in Becquerels (disintegrations per second).

### Dependencies

- `src/dynamics/ode.ts` — RK4 for heat transfer simulations (Newton's cooling with time-varying environment)
- `src/optimization/` — constraint handling in economic dispatch

### Usage Examples

```typescript
import { decayRemaining, halfLife, newtonCooling, economicDispatch } from 'evenwicht/energy';

// Radioactive decay: 1000 atoms, lambda = 0.01/s, after 100s
decayRemaining(1000, 0.01, 100);  // ≈ 368

// Half-life from decay constant
halfLife(0.01);  // ≈ 69.3 seconds

// Newton's cooling: coffee at 90C in 20C room, h' = 0.1
newtonCooling(90, 20, 0.1, 10);  // ≈ 45.8C

// Economic dispatch for 3 generators
const generators = [
  { b: 20, c: 0.01, pMin: 50, pMax: 200 },
  { b: 25, c: 0.015, pMin: 40, pMax: 150 },
  { b: 30, c: 0.02, pMin: 30, pMax: 100 },
];
const result = economicDispatch(generators, 350);
// result.outputs: optimal MW allocation per generator
```

### Connections

This chapter synthesises Chapter 19 (radioactive decay is a separable first-order ODE; Bateman equations are linear ODE systems solved by eigenvalue methods or successive integration), Chapter 12 (economic dispatch is a constrained optimisation; LP duality yields electricity shadow prices), Chapter 18 (battery state-of-charge evolution is a first-order difference equation), Chapter 21 (demand forecasting uses ARIMA with exogenous regressors) and Chapter 22 (spectral analysis of renewable intermittency uses the DFT and power spectral density). It connects to Chapter 10 (eigenvalues of the neutron diffusion operator determine reactor criticality), Chapter 11 (unconstrained minimisation of generator cost functions) and Chapter 25 (net present value of energy infrastructure investments).

- **Ordinary Differential Equations** (Chapter 19): Radioactive decay is a canonical separable first-order ODE. The Bateman equations for decay chains are systems of first-order linear ODEs solvable by the integrating factor method. Newton's cooling law is formally identical to the decay equation with $\lambda$ replaced by the cooling rate $h'$. The eigenvalue structure of the Bateman system matrix (a lower-triangular matrix with diagonal entries $-\lambda_i$) makes the decay constants themselves the eigenvalues, connecting to Chapter 10.

- **Constrained Optimisation & Linear Programming** (Chapter 12): The economic dispatch problem is a constrained optimisation with quadratic or linear objectives and linear constraints. The equal incremental cost criterion is a direct application of the Lagrange multiplier method. The LP formulation of dispatch yields dual variables that are locational marginal prices; the most consequential application of LP duality in any industry. Battery storage scheduling is an LP whose temporal coupling constraints resemble the multi-period portfolio problems of Chapter 27.

- **Difference Equations** (Chapter 18): The battery state-of-charge evolution $\text{SOC}_{t+1} = \text{SOC}_t + \eta_c c_t \Delta t - d_t \Delta t / \eta_d$ is a first-order difference equation driven by the charge and discharge decisions. The recursive structure of the SOC constraint in the LP creates a banded constraint matrix that can be exploited for computational efficiency.

- **Time Series** (Chapter 21): Electricity demand forecasting uses ARIMA models with temperature as an exogenous regressor. The autocorrelation function of hourly demand reveals strong periodicities at lags 24 (daily cycle) and 168 (weekly cycle). Seasonal differencing ($(1 - L^{24})$ or $(1 - L^{168})$) removes these periodicities, yielding a stationary series amenable to ARMA modelling.

- **Transforms & Spectral Analysis** (Chapter 22): The FFT-based periodogram characterises the frequency content of wind and solar generation, distinguishing predictable periodic components from random variability. The Kolmogorov–Wiener theory (Chapter 21) implies that forecast accuracy depends on the spectral density: a series with most power at low frequencies (slowly varying) is more predictable than one with a flat spectrum (white noise-like).



### What Is Implemented vs. Documented Only

- [x] Exponential radioactive decay (remaining atoms, activity)
- [x] Half-life and decay constant conversions
- [x] Bateman solution for three-member decay chains
- [x] Newton's law of cooling
- [x] Steady-state slab temperature profile (Fourier's law)
- [x] Slab heat flux computation
- [x] Economic dispatch via equal incremental cost with generator limits


---
### Implementation Context

**Design decisions.** Radioactive decay and Newton's cooling use closed-form exponential solutions evaluated via `Math.exp`, avoiding numerical integration entirely. The Bateman three-chain solution uses the analytical formula with coefficients $\lambda_1 N_0 / (\lambda_2 - \lambda_1)$, which is $O(1)$ per time point. The economic dispatch solver uses the equal incremental cost criterion with iterative constraint handling (Algorithm 5.2), converging in at most $n + 1$ iterations for $n$ generators.

**Numerical pitfalls.** The Bateman solution involves differences of exponentials ($e^{-\lambda_1 t} - e^{-\lambda_2 t}$) that suffer catastrophic cancellation when $\lambda_1 \approx \lambda_2$. The implementation enforces a relative tolerance of $10^{-15}$ between $\lambda_1$ and $\lambda_2$ and throws for the degenerate case, which requires a separate $t e^{-\lambda t}$ formula. For very long times ($\lambda t > 709$), $e^{-\lambda t}$ underflows to zero in IEEE 754 doubles; this is physically correct for long-lived isotopes but must be handled in the Bateman coefficient computation. The log-sum-exp trick can be applied when intermediate terms overflow but the final result does not.

**Economic dispatch.** The equal incremental cost method solves a system of $n$ linear equations per iteration. Generators that hit their min/max limits are fixed and removed from the unconstrained set, yielding at most $n$ re-solves. The system marginal cost $\lambda^*$ is the Lagrange multiplier for the demand constraint. The algorithm assumes convex quadratic cost functions ($c_i > 0$); non-convex costs (e.g., startup costs) would require integer programming.

**Performance.** All decay/cooling computations are $O(1)$ per evaluation. Economic dispatch is $O(n^2)$ worst case. Heat flux and slab temperature are trivial $O(1)$ formulas.

**Testing.** Decay functions are tested against half-life identities ($N(t_{1/2}) = N_0/2$) and the activity formula $A = \lambda N$. The Bateman chain is verified by checking that $N_1 + N_2 + N_3 = N_0$ (mass conservation). Economic dispatch is tested against hand-solved two-generator examples and verified that all generator outputs satisfy their min/max constraints.

