<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Fluid Dynamics — API Reference

This is the API reference for the TypeScript implementation of Fluid Dynamics (Simplified). For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/fluids/bernoulli.ts` — Bernoulli equation utilities
- `src/fluids/poiseuille.ts` — Hagen–Poiseuille pipe flow
- `src/fluids/stokes.ts` — Stokes drag, terminal velocity, falling sphere simulation
- `src/fluids/diffusion.ts` — 1D diffusion equation (matrix, eigenvalues, simulation)
- `src/fluids/turbulence.ts` — spectral slope estimation
- `src/fluids/reynolds.ts` — Reynolds number, flow regime classification

### Data Representation

Physical quantities use SI units (Pa, m, kg/m^3, Pa*s, m/s). Diffusion simulations use `Float64Array` for concentration profiles and return arrays of snapshots. Matrices are flat row-major `Float64Array`. Flow regime is classified as a string literal type.

### API Preview

```typescript
// src/fluids/bernoulli.ts

/**
 * Compute the Bernoulli constant along a streamline.
 *
 * @param P - Static pressure (Pa).
 * @param v - Flow velocity (m/s).
 * @param h - Height above reference (m).
 * @param rho - Fluid density (kg/m^3).
 * @param g - Gravitational acceleration (default: 9.81 m/s^2).
 * @returns The Bernoulli constant P + 0.5*rho*v^2 + rho*g*h.
 */
function bernoulliConstant(
  P: number, v: number, h: number, rho: number, g?: number,
): number;

/**
 * Compute velocity at a point given Bernoulli constant and other quantities.
 *
 * @param B - Bernoulli constant from another point on the streamline.
 * @param P - Static pressure at the target point (Pa).
 * @param h - Height at the target point (m).
 * @param rho - Fluid density (kg/m^3).
 * @param g - Gravitational acceleration (default: 9.81 m/s^2).
 * @returns Velocity at the target point (m/s).
 * @throws Error if the computed velocity squared is negative (physically impossible).
 */
function bernoulliVelocity(
  B: number, P: number, h: number, rho: number, g?: number,
): number;

/**
 * Compute pressure at a point given Bernoulli constant and other quantities.
 */
function bernoulliPressure(
  B: number, v: number, h: number, rho: number, g?: number,
): number;
```

```typescript
// src/fluids/poiseuille.ts

/**
 * Compute the Poiseuille velocity at radial position r.
 *
 * @param r - Radial distance from pipe centre (m).
 * @param R - Pipe inner radius (m).
 * @param deltaP - Pressure difference along pipe (Pa).
 * @param mu - Dynamic viscosity (Pa*s).
 * @param L - Pipe length (m).
 * @returns Velocity at radius r (m/s).
 * @throws Error if r > R or any parameter is non-positive.
 */
function poiseuilleVelocity(
  r: number, R: number, deltaP: number, mu: number, L: number,
): number;

/**
 * Compute volumetric flow rate via Hagen–Poiseuille law.
 */
function poiseuilleFlowRate(
  R: number, deltaP: number, mu: number, L: number,
): number;
```

```typescript
// src/fluids/stokes.ts

/**
 * Compute Stokes drag force on a sphere.
 *
 * @param mu - Dynamic viscosity (Pa*s).
 * @param r - Sphere radius (m).
 * @param v - Velocity (m/s).
 * @returns Drag force (N).
 */
function stokesDrag(mu: number, r: number, v: number): number;

/**
 * Compute terminal velocity for a sphere under Stokes drag.
 */
function terminalVelocity(m: number, mu: number, r: number, g?: number): number;

/**
 * Simulate falling sphere ODE: dv/dt = g - (6*pi*mu*r/m)*v.
 *
 * @param params - { mass, radius, viscosity, gravity? }.
 * @param v0 - Initial velocity (m/s).
 * @param tEnd - End time (s).
 * @param dt - Time step (s).
 * @returns Object { t: Float64Array, v: Float64Array }.
 */
function simulateFallingSphere(
  params: { mass: number; radius: number; viscosity: number; gravity?: number },
  v0: number,
  tEnd: number,
  dt: number,
): { t: Float64Array; v: Float64Array };
```

```typescript
// src/fluids/diffusion.ts

/**
 * Construct the N x N tridiagonal diffusion matrix (row-major Float64Array).
 *
 * @param N - Number of interior grid points.
 * @returns Float64Array of length N*N representing the tridiagonal matrix.
 */
function diffusionMatrix(N: number): Float64Array;

/**
 * Compute analytical eigenvalues of the diffusion matrix.
 *
 * @param N - Number of interior grid points.
 * @returns Float64Array of N eigenvalues, sorted by magnitude (slowest first).
 */
function diffusionEigenvalues(N: number): Float64Array;

/**
 * Compute physical decay rates for the discretised diffusion equation.
 *
 * @param N - Number of interior grid points.
 * @param D - Diffusion coefficient (m^2/s).
 * @param L - Domain length (m).
 * @returns Float64Array of N decay rates (1/s), slowest first.
 */
function diffusionDecayRates(N: number, D: number, L: number): Float64Array;

/**
 * Simulate the 1D diffusion equation using method of lines + RK4.
 *
 * @param N - Number of interior grid points.
 * @param D - Diffusion coefficient.
 * @param L - Domain length.
 * @param cLeft - Left boundary value.
 * @param cRight - Right boundary value.
 * @param c0 - Initial concentration at interior points (Float64Array of length N).
 * @param tEnd - End time.
 * @param dt - Time step.
 * @returns Object { t: Float64Array, c: Float64Array[] } where c[k] is concentration at time t[k].
 */
function simulateDiffusion(
  N: number, D: number, L: number,
  cLeft: number, cRight: number,
  c0: Float64Array,
  tEnd: number, dt: number,
): { t: Float64Array; c: Float64Array[] };
```

```typescript
// src/fluids/turbulence.ts

/**
 * Estimate the spectral slope from velocity fluctuation data.
 *
 * @param velocities - Velocity fluctuation time series.
 * @param fs - Sampling frequency (Hz).
 * @param fMin - Lower bound of inertial subrange (Hz).
 * @param fMax - Upper bound of inertial subrange (Hz).
 * @returns Object { slope, intercept, rSquared }.
 */
function spectralSlope(
  velocities: number[],
  fs: number,
  fMin: number,
  fMax: number,
): { slope: number; intercept: number; rSquared: number };
```

```typescript
// src/fluids/reynolds.ts

/**
 * Compute the Reynolds number.
 *
 * @param rho - Fluid density (kg/m^3).
 * @param v - Characteristic velocity (m/s).
 * @param L - Characteristic length (m).
 * @param mu - Dynamic viscosity (Pa*s).
 * @returns Dimensionless Reynolds number.
 */
function reynoldsNumber(rho: number, v: number, L: number, mu: number): number;

/**
 * Classify flow regime based on Reynolds number for pipe flow.
 *
 * @returns 'laminar' | 'transitional' | 'turbulent'.
 */
function flowRegime(Re: number): 'laminar' | 'transitional' | 'turbulent';
```

### Error Handling

- `bernoulliVelocity` throws if the computed $v^2$ is negative (pressure and height at the target exceed the Bernoulli constant).
- `poiseuilleVelocity` throws if $r > R$ (outside the pipe).
- `simulateFallingSphere` and `simulateDiffusion` throw if the time step, end time, or physical parameters are non-positive.
- `spectralSlope` throws if fewer than 3 frequency bins fall in the specified inertial subrange.
- `diffusionMatrix` throws if $N < 1$.

### Dependencies

- `src/dynamics/ode.ts` — RK4 for falling sphere and diffusion simulations
- `src/linear/eigen.ts` — eigenvalue computation for diffusion decay rates
- `src/transforms/fft.ts` — FFT for turbulence spectral analysis
- `src/stats/regression.ts` — linear regression for spectral slope fitting

### Usage Examples

```typescript
import { bernoulliConstant, reynoldsNumber, flowRegime, poiseuilleFlowRate } from 'evenwicht/fluids';

// Bernoulli constant at a point: P=101325 Pa, v=10 m/s, h=0m, rho=1.225 kg/m^3
bernoulliConstant(101325, 10, 0, 1.225);  // ≈ 101386 Pa

// Reynolds number for pipe flow
const Re = reynoldsNumber(1000, 2.0, 0.05, 0.001);  // 100000
flowRegime(Re);  // 'turbulent'

// Poiseuille flow rate
poiseuilleFlowRate(0.01, 1000, 0.001, 1.0);  // volumetric flow in m^3/s
```

### Connections

This chapter synthesises Chapter 5 (integration determines flow rates from velocity profiles and total energy from pressure distributions), Chapter 10 (eigenvalues of the diffusion operator determine modal decay rates; eigenvalues of the wave operator give water hammer frequencies), Chapter 19 (Stokes drag produces a first-order ODE; Poiseuille flow is a second-order ODE; all systems are integrated numerically by RK4) and Chapter 22 (FFT extracts turbulence spectra from velocity time series). It connects forward to heat transfer (the diffusion equation with a source term), acoustics (pressure wave propagation) and computational fluid dynamics.

**Chapter 5 (Integral Calculus)**. The Hagen–Poiseuille flow rate is computed by integrating the parabolic velocity profile over the pipe cross-section. The energy interpretation of Bernoulli's equation relates to the work-energy theorem established through integration. Simpson's rule from Chapter 5 provides the numerical quadrature for flow rate computation.

**Chapter 10 (Eigenvalues)**. The diffusion matrix and the water hammer matrix share the same tridiagonal structure. Their eigenvalues determine, respectively, the decay rates of concentration modes and the natural frequencies of pressure oscillations. The analytical eigenvalue formula for the discrete Laplacian is a special case of the general tridiagonal eigenvalue theory. Power iteration from Chapter 10 verifies the dominant eigenvalue numerically.

**Chapter 19 (ODEs)**. The terminal velocity ODE is the simplest fluid dynamics problem solvable as an initial-value problem. The method-of-lines discretisation converts the diffusion PDE to a system of ODEs integrated by RK4. The convection-diffusion boundary-value problem is a second-order ODE with constant coefficients, solvable by the methods of Chapter 19.

**Chapter 22 (Transforms)**. The FFT from Chapter 22 is the computational tool for extracting turbulence spectra from velocity time series. The periodogram provides the power spectral density, and log-log regression in the inertial subrange yields the Kolmogorov exponent. Spectral leakage and windowing considerations from Chapter 22 apply directly.



### What Is Implemented vs. Documented Only

- [x] Bernoulli constant and solvers (`bernoulliConstant`, `bernoulliVelocity`, `bernoulliPressure`)
- [x] Poiseuille velocity profile and flow rate (`poiseuilleVelocity`, `poiseuilleFlowRate`)
- [x] Stokes drag and terminal velocity (`stokesDrag`, `terminalVelocity`, `simulateFallingSphere`)
- [x] Diffusion matrix construction and eigenvalues (`diffusionMatrix`, `diffusionEigenvalues`, `diffusionDecayRates`)
- [x] Diffusion simulation via method of lines + RK4 (`simulateDiffusion`)
- [x] Spectral slope estimation (`spectralSlope`)
- [x] Reynolds number and flow regime (`reynoldsNumber`, `flowRegime`)
- [ ] Water hammer simulation (documented; extends `diffusionMatrix` to second-order wave system)
- [ ] Convection–diffusion ODE solver (documented; uses `solveODE` from Chapter 19 with BVP boundary conditions)
- [ ] Venturi meter calculator (documented — direct application of `bernoulliVelocity`)

---


### Implementation Context

**Algebraic solvers for Bernoulli and Poiseuille.** The Bernoulli and Poiseuille functions are direct algebraic evaluations ($O(1)$ per call) with no iterative computation. `bernoulliVelocity` checks that the computed $v^2$ is non-negative before taking the square root, throwing if the input parameters are physically impossible.

**Terminal velocity ODE.** The Stokes drag ODE $dv/dt = g - \alpha v$ is linear with eigenvalue $-\alpha$ and time constant $\tau = m/(6\pi\mu r)$. RK4 stability requires $h < 2.785\tau$; in practice $h \leq 0.1\tau$ provides four-digit accuracy. For small spheres in viscous fluids ($\tau \sim 10^{-4}$ s), very small step sizes are needed.

**Diffusion via method of lines.** The 1D diffusion equation is discretised into $N$ interior grid points, producing an $N$-dimensional ODE system with a tridiagonal matrix. Eigenvalues are computed analytically via $\lambda_k = -4\sin^2(k\pi/(2(N+1)))$, avoiding the $O(N^3)$ cost of numerical eigenvalue decomposition. The stiffness ratio grows as $O(N^2)$; for $N > 50$, the CFL condition $h < 2.785\Delta x^2/(4D)$ becomes restrictive, and implicit methods would be preferable.

**Spectral slope estimation.** The Kolmogorov $-5/3$ law is verified by computing the periodogram via FFT and fitting a log-log regression over a user-specified inertial subrange $[f_{\min}, f_{\max}]$. Windowing reduces spectral leakage but does not add information. At least 3 frequency bins must fall within the specified range, otherwise the function throws.

**Reynolds number classification.** Flow regime classification uses standard thresholds for pipe flow: laminar ($\text{Re} < 2300$), transitional ($2300 \leq \text{Re} < 4000$), turbulent ($\text{Re} \geq 4000$). These thresholds are empirical and geometry-dependent; the function returns a string literal type for type safety.

**Testing strategy.** Poiseuille flow rate is verified against the exact formula $Q = \pi R^4 \Delta P/(8\mu L)$. Terminal velocity is checked by comparing the numerical steady state against $v_{\infty} = mg/(6\pi\mu r)$. Diffusion eigenvalues are compared against the analytical formula. Spectral slope tests use synthetic $-5/3$ power-law signals to verify the regression output.
