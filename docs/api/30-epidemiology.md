<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Epidemiology & Population Dynamics — API Reference

This is the API reference for the TypeScript implementation of Epidemiology & Population Dynamics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/epidemiology/sir.ts` — SIR model: $R_0$, herd immunity, vector field, simulation
- `src/epidemiology/seir.ts` — SEIR model with exposed compartment
- `src/epidemiology/lotka-volterra.ts` — Lotka-Volterra predator-prey dynamics
- `src/epidemiology/estimation.ts` — $R_0$ estimation from growth-phase data

### Data Representation

Compartmental models operate on state vectors of 3–5 components ($S$, $E$, $I$, $R$, etc.), represented as `Float64Array` for consistency with the numerical integration routines in `evenwicht/ode`. The ODE right-hand side is a function `(t: number, y: Float64Array) => Float64Array`.

### API Preview

```typescript
// src/epidemiology/sir.ts

/**
 * SIR model parameters.
 */
interface SIRParams {
  /** Transmission rate. */
  beta: number;
  /** Recovery rate. */
  gamma: number;
}

/**
 * Compute R0 for the SIR model.
 */
function basicReproductionNumber(params: SIRParams): number;

/**
 * Compute the herd immunity threshold.
 */
function herdImmunityThreshold(R0: number): number;

/**
 * Define the SIR vector field for use with RK4.
 *
 * @param params - SIR parameters.
 * @returns A function (t, y) => dydt suitable for the ODE solver.
 */
function sirVectorField(
  params: SIRParams,
): (t: number, y: Float64Array) => Float64Array;

/**
 * Simulate the SIR model using RK4.
 *
 * @param params - SIR parameters.
 * @param S0 - Initial susceptible count.
 * @param I0 - Initial infected count.
 * @param R0_init - Initial removed count.
 * @param tEnd - Simulation end time.
 * @param dt - Time step.
 * @returns Object with arrays t, S, I, R.
 */
function simulateSIR(
  params: SIRParams,
  S0: number,
  I0: number,
  R0_init: number,
  tEnd: number,
  dt: number,
): { t: Float64Array; S: Float64Array; I: Float64Array; R: Float64Array };
```

```typescript
// src/epidemiology/seir.ts

/**
 * SEIR model parameters.
 */
interface SEIRParams {
  beta: number;
  sigma: number;
  gamma: number;
}

/**
 * Simulate the SEIR model using RK4.
 */
function simulateSEIR(
  params: SEIRParams,
  S0: number,
  E0: number,
  I0: number,
  R0_init: number,
  tEnd: number,
  dt: number,
): { t: Float64Array; S: Float64Array; E: Float64Array; I: Float64Array; R: Float64Array };
```

```typescript
// src/epidemiology/lotka-volterra.ts

/**
 * Lotka–Volterra parameters.
 */
interface LotkaVolterraParams {
  alpha: number;
  beta: number;
  delta: number;
  gamma: number;
}

/**
 * Simulate the Lotka–Volterra predator-prey system.
 */
function simulateLotkaVolterra(
  params: LotkaVolterraParams,
  x0: number,
  y0: number,
  tEnd: number,
  dt: number,
): { t: Float64Array; x: Float64Array; y: Float64Array };

/**
 * Compute the conserved quantity H(x, y).
 */
function lotkaVolterraHamiltonian(
  params: LotkaVolterraParams,
  x: number,
  y: number,
): number;
```

```typescript
// src/epidemiology/estimation.ts

/**
 * Estimate R0 from exponential growth phase data.
 *
 * @param caseCounts - Daily new case counts during growth phase.
 * @param gamma - Recovery rate (1/infectious period).
 * @returns Estimated R0.
 */
function estimateR0FromGrowth(
  caseCounts: number[],
  gamma: number,
): number;
```

### Error Handling

- `simulateSIR` / `simulateSEIR` throw if initial conditions are negative, if $\beta$ or $\gamma$ is non-positive, or if the initial conditions do not satisfy $S_0 + I_0 + R_0 = N$ (with tolerance $10^{-10}$).
- `herdImmunityThreshold` throws if $R_0 \leq 1$ (no meaningful threshold exists).
- `estimateR0FromGrowth` throws if fewer than 3 data points are provided or if the linear regression slope is non-positive (no exponential growth detected).

### Dependencies

- `src/dynamics/ode.ts` — RK4 integration for all compartmental model simulations
- `src/stats/regression.ts` — linear regression for $R_0$ estimation from growth data

### Usage Examples

```typescript
import { simulateSIR, basicReproductionNumber, herdImmunityThreshold } from 'evenwicht/epidemiology';

// SIR model: COVID-like parameters
const params = { beta: 0.3, gamma: 0.1 };
const R0 = basicReproductionNumber(params);  // 3.0
herdImmunityThreshold(R0);  // 0.667 (67% must be immune)

// Simulate epidemic in population of 1000
const sim = simulateSIR(params, 999, 1, 0, 200, 0.1);
// sim.I reaches peak around t ≈ 50

// Lotka-Volterra predator-prey
import { simulateLotkaVolterra } from 'evenwicht/epidemiology';
const lv = simulateLotkaVolterra(
  { alpha: 1.1, beta: 0.4, delta: 0.1, gamma: 0.4 },
  10, 10, 100, 0.01,
);
```

### Connections

This chapter synthesises Chapter 10 (eigenvalues determine stability of disease-free and endemic equilibria), Chapter 13 (stochastic foundations of transmission probabilities), Chapter 17 (fitting models to surveillance data) and Chapter 19 (ODE formulation and RK4 numerical integration). It connects forward to stochastic simulation methods and spatial epidemic models.

- **Eigenvalues** (Chapter 10): The stability of equilibria in all compartmental models reduces to computing eigenvalues of the Jacobian matrix. The next-generation matrix method defines $R_0$ as a spectral radius (dominant eigenvalue). The purely imaginary eigenvalues of the Lotka–Volterra system explain its oscillatory behaviour.

- **Probability Theory** (Chapter 13): The deterministic SIR model is the mean-field limit of a stochastic process. Each transmission event has probability $\beta \cdot dt$ per susceptible-infected pair; the law of large numbers (Chapter 13) ensures that for large populations, the stochastic process concentrates around the deterministic trajectory. For small populations, stochastic effects dominate; extinction can occur even when $R_0 > 1$.

- **Regression** (Chapter 17): Parameter estimation from epidemic data uses linear regression (log-linear growth rate fitting) and nonlinear least squares (fitting the full SIR trajectory to case data). The confidence intervals from regression propagate to uncertainty in $R_0$ and forecasted epidemic trajectories.

- **Ordinary Differential Equations** (Chapter 19): The SIR, SEIR and Lotka–Volterra systems are autonomous systems of nonlinear ODEs. The analysis tools (equilibrium classification, phase portraits, Jacobian linearisation) come directly from Chapter 19. Numerical integration via RK4 provides the computational backbone.

- **Control Systems** (Chapter 29): Epidemic control (lockdowns, vaccination campaigns) can be viewed through the lens of feedback control. The effective reproduction number $R_e$ is the controlled output; interventions reduce $\beta$ (social distancing) or increase removal from the susceptible class (vaccination). Optimal control theory determines the timing and intensity of interventions to minimise total infections subject to economic constraints.



### What Is Implemented vs. Documented Only

- [x] SIR simulation via RK4 (`simulateSIR`)
- [x] SEIR simulation via RK4 (`simulateSEIR`)
- [x] Lotka–Volterra simulation (`simulateLotkaVolterra`)
- [x] $R_0$ computation (`basicReproductionNumber`)
- [x] Herd immunity threshold (`herdImmunityThreshold`)
- [x] $R_0$ estimation from growth data (`estimateR0FromGrowth`)
- [x] Lotka–Volterra Hamiltonian (`lotkaVolterraHamiltonian`)
- [ ] Stochastic SIR (Gillespie algorithm — deferred, requires stochastic framework)
- [ ] Age-structured models (deferred — requires matrix population framework)
- [ ] Spatial models (deferred — requires PDE or network framework)
- [ ] MCMC parameter estimation (deferred — requires sampling framework)

---
### Implementation Context

**Design decisions.** Compartmental state vectors use `Float64Array` of length 3 (SIR) or 4 (SEIR) for direct compatibility with the RK4 solver in `evenwicht/ode`. The vector field functions are closures that capture model parameters, returning a new `Float64Array` per evaluation. The Lotka-Volterra Hamiltonian $H(x,y) = \delta x - \gamma\ln x + \beta y - \alpha\ln y$ is exposed as a standalone function for conservation diagnostics.

**Numerical pitfalls.** RK4 can produce small negative compartment values near $I = 0$ at the tail of an epidemic due to truncation error. The implementation clamps compartments to zero after each step and redistributes the deficit to maintain $S + I + R = N$. Conservation ($S + I + R = N$) is monitored as a numerical diagnostic; drift above $10^{-10}$ signals that $h$ should be reduced. A step size $h \leq 0.01 \cdot \min(1/\beta, 1/\gamma)$ provides four-digit accuracy for typical parameters.

**Lotka-Volterra drift.** The Lotka-Volterra system is Hamiltonian, and RK4 does not exactly preserve the conserved quantity $H$. Over long simulations, $H$ drifts secularly, causing orbits to spiral outward. For short to medium runs, $h \leq 0.01/\max(\alpha, \gamma)$ keeps drift below $10^{-8}$. Symplectic integrators would be needed for long-term fidelity but are not currently implemented.

**$R_0$ estimation.** The growth-rate method fits $\ln(\text{cases})$ vs. time via linear regression, then converts the slope $\lambda$ to $R_0 = 1 + \lambda/\gamma$. The estimate is sensitive to the choice of the exponential growth window; including post-peak data biases $\lambda$ downward. At least 3 data points in the growth phase are required.

**Testing.** SIR simulations are verified against the conservation law $S + I + R = N$ and the peak infection formula $I_{\max} = I_0 + S_0 - S_{\text{peak}} + (1/R_0)\ln(S_{\text{peak}}/S_0)$. The herd immunity threshold is tested against the formula $1 - 1/R_0$. Lotka-Volterra conservation is checked by monitoring $|H_k - H_0|$ over the trajectory.

