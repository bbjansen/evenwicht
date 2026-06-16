<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chemical Kinetics & Reaction Networks — API Reference

This is the API reference for the TypeScript implementation of Chemical Kinetics & Reaction Networks. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/kinetics/rate-laws.ts` — zeroth, first, second-order kinetics, half-life
- `src/kinetics/arrhenius.ts` — Arrhenius equation, parameter fitting
- `src/kinetics/michaelis-menten.ts` — Michaelis-Menten kinetics, Lineweaver-Burk regression
- `src/kinetics/network.ts` — reaction network simulation, conservation laws, sequential kinetics

### Data Representation

Concentration vectors are represented as `Float64Array` for efficient numerical computation. The stoichiometry matrix is stored as a dense 2D array (`number[][]` or a matrix type from `evenwicht/matrix`). Rate functions are closures of type `(c: Float64Array) => Float64Array` that compute the rate vector given a concentration vector.

### API Preview

```typescript
// src/kinetics/rate-laws.ts

/**
 * Compute concentration at time t for zeroth-order kinetics.
 *
 * @param A0 - Initial concentration.
 * @param k - Rate constant (mol/L/s).
 * @param t - Time (s).
 * @returns Concentration at time t (clamped to 0).
 */
function zerothOrder(A0: number, k: number, t: number): number;

/**
 * Compute concentration at time t for first-order kinetics.
 *
 * @param A0 - Initial concentration.
 * @param k - Rate constant (1/s).
 * @param t - Time (s).
 * @returns Concentration at time t.
 */
function firstOrder(A0: number, k: number, t: number): number;

/**
 * Compute concentration at time t for second-order kinetics.
 *
 * @param A0 - Initial concentration.
 * @param k - Rate constant (L/mol/s).
 * @param t - Time (s).
 * @returns Concentration at time t.
 */
function secondOrder(A0: number, k: number, t: number): number;

/**
 * Compute half-life for a given order and parameters.
 *
 * @param order - Reaction order (0, 1, or 2).
 * @param k - Rate constant.
 * @param A0 - Initial concentration (required for orders 0 and 2).
 * @returns Half-life in the same time units as k.
 */
function halfLife(order: 0 | 1 | 2, k: number, A0?: number): number;
```

```typescript
// src/kinetics/arrhenius.ts

/**
 * Arrhenius equation parameters.
 */
interface ArrheniusParams {
  /** Pre-exponential factor. */
  A: number;
  /** Activation energy (J/mol). */
  Ea: number;
}

/**
 * Compute rate constant at temperature T.
 *
 * @param params - Arrhenius parameters.
 * @param T - Temperature (K).
 * @returns Rate constant k.
 */
function arrheniusRate(params: ArrheniusParams, T: number): number;

/**
 * Estimate Arrhenius parameters from temperature-rate data.
 *
 * @param temperatures - Array of temperatures (K).
 * @param rateConstants - Array of measured rate constants.
 * @returns Estimated ArrheniusParams with R-squared.
 */
function fitArrhenius(
  temperatures: number[],
  rateConstants: number[],
): { params: ArrheniusParams; rSquared: number };
```

```typescript
// src/kinetics/michaelis-menten.ts

/**
 * Michaelis–Menten parameters.
 */
interface MichaelisMentenParams {
  /** Maximum rate (mol/L/s). */
  Vmax: number;
  /** Michaelis constant (mol/L). */
  Km: number;
}

/**
 * Compute reaction rate from Michaelis–Menten kinetics.
 *
 * @param params - Michaelis–Menten parameters.
 * @param S - Substrate concentration (mol/L).
 * @returns Reaction rate v.
 */
function michaelisMentenRate(params: MichaelisMentenParams, S: number): number;

/**
 * Estimate Michaelis–Menten parameters via Lineweaver–Burk regression.
 *
 * @param substrates - Array of substrate concentrations.
 * @param rates - Array of measured initial rates.
 * @returns Estimated parameters with R-squared.
 */
function fitLineweaverBurk(
  substrates: number[],
  rates: number[],
): { params: MichaelisMentenParams; rSquared: number };
```

```typescript
// src/kinetics/network.ts

/**
 * Define a reaction network and simulate its dynamics.
 *
 * @param stoichiometry - m x r stoichiometry matrix.
 * @param rateFunction - Function computing rate vector from concentrations.
 * @param c0 - Initial concentration vector.
 * @param tEnd - Simulation end time.
 * @param dt - Time step.
 * @returns Object with time array and concentration matrix.
 */
function simulateNetwork(
  stoichiometry: number[][],
  rateFunction: (c: Float64Array) => Float64Array,
  c0: Float64Array,
  tEnd: number,
  dt: number,
): { t: Float64Array; concentrations: Float64Array[] };

/**
 * Extract conservation laws from a stoichiometry matrix.
 *
 * @param stoichiometry - m x r stoichiometry matrix.
 * @returns Array of conservation law vectors (basis of left null space of N).
 */
function conservationLaws(stoichiometry: number[][]): number[][];

/**
 * Simulate sequential first-order kinetics A -> B -> C.
 *
 * @param k1 - Rate constant for A -> B.
 * @param k2 - Rate constant for B -> C.
 * @param A0 - Initial concentration of A.
 * @param tEnd - Simulation end time.
 * @param dt - Time step.
 * @returns Object with time array and concentrations of A, B, C.
 */
function sequentialFirstOrder(
  k1: number,
  k2: number,
  A0: number,
  tEnd: number,
  dt: number,
): { t: Float64Array; A: Float64Array; B: Float64Array; C: Float64Array };
```

### Error Handling

- `zerothOrder`, `firstOrder`, `secondOrder` throw if $k \leq 0$ or $[A]_0 < 0$.
- `halfLife` throws if order is 0 or 2 and $[A]_0$ is not provided (or is non-positive).
- `arrheniusRate` throws if $T \leq 0$.
- `fitArrhenius` throws if fewer than 2 data points are provided, or if any temperature or rate constant is non-positive.
- `fitLineweaverBurk` throws if fewer than 2 data points are provided, or if any substrate concentration or rate is non-positive.
- `simulateNetwork` throws if the dimensions of the stoichiometry matrix, rate function output and initial concentration vector are inconsistent.
- `conservationLaws` throws if the stoichiometry matrix has zero rows or columns.

### Dependencies

- `src/dynamics/ode.ts` — RK4 for network simulation and sequential kinetics
- `src/stats/regression.ts` — linear regression for Arrhenius and Lineweaver–Burk fitting
- `src/linear/solve.ts` — null space computation for conservation laws

### Usage Examples

```typescript
import { firstOrder, halfLife, arrheniusRate, michaelisMentenRate } from 'evenwicht/kinetics';

// First-order decay: [A]_0 = 1.0 mol/L, k = 0.05/s, after 10s
firstOrder(1.0, 0.05, 10);  // ≈ 0.607 mol/L

// Half-life of first-order reaction
halfLife(1, 0.05);  // ≈ 13.86 s

// Arrhenius rate at 300K
arrheniusRate({ A: 1e10, Ea: 50000 }, 300);  // k at 300K

// Michaelis-Menten at substrate = 2*Km
michaelisMentenRate({ Vmax: 10, Km: 1 }, 2);  // ≈ 6.67
```

### Connections

This chapter synthesises Chapter 9 (the stoichiometry matrix is the structural backbone of reaction networks; null-space computation yields conservation laws), Chapter 17 (Arrhenius linearisation and Lineweaver–Burk plots are linear regression problems) and Chapter 19 (rate laws are separable or linear ODEs; coupled networks are ODE systems integrated numerically via RK4). It connects to Chapter 10 (eigenvalue analysis determines stability of steady states and predicts oscillatory behaviour), Chapter 32 (first-order decay is mathematically identical to radioactive decay) and Chapter 35 (pharmacokinetics applies the same compartmental ODE framework to drug metabolism).

- **Matrices** (Chapter 9): The stoichiometry matrix $N$ is the central algebraic object of reaction network theory. Its rank determines the dimension of the stoichiometric subspace (the set of concentration changes accessible from a given initial condition). Its null space characterises steady-state flux distributions; the null space of $N^T$ yields conservation laws. Matrix-vector multiplication $N\mathbf{r}$ computes the rate of change of all species simultaneously.

- **Regression** (Chapter 17): The Arrhenius linearisation $\ln k$ vs $1/T$ is a textbook application of simple linear regression. The Lineweaver–Burk double-reciprocal plot $1/v$ vs $1/[S]$ is another. Order determination (plotting $\ln[A]$ or $1/[A]$ vs $t$ and checking linearity) also relies on regression diagnostics ($R^2$, residual patterns). Parameter estimation pervades experimental kinetics.

- **Ordinary Differential Equations** (Chapter 19): Every rate law is an ODE. Zeroth-order is trivially integrable; first-order is separable with exponential solutions; second-order is separable with reciprocal solutions. Coupled reactions yield ODE systems solved by the methods of Chapter 19 (integrating factors for sequential kinetics, Runge–Kutta for numerical integration of arbitrary networks). The steady-state approximation (setting $d[ES]/dt = 0$ in enzyme kinetics) is the algebraic reduction of a fast ODE subsystem.

- **Eigenvalues** (Chapter 10): Stability analysis of reaction network steady states requires computing eigenvalues of the Jacobian matrix. The Hopf bifurcation in the Oregonator model is detected by eigenvalues crossing the imaginary axis. For linear reaction networks (all first-order), the eigenvalues of the rate matrix directly determine the time constants of the system.

- **Energy Systems** (Chapter 32): First-order chemical decay and radioactive decay are mathematically identical ODEs. The Bateman equations for decay chains (Chapter 32, Theorem 32.7) have the same structure as sequential first-order kinetics (Theorem 34.21). The mathematical tools transfer directly between nuclear physics and chemistry.



### What Is Implemented vs. Documented Only

- [x] Zeroth-, first-, second-order analytical solutions (`zerothOrder`, `firstOrder`, `secondOrder`)
- [x] Half-life computation (`halfLife`)
- [x] Arrhenius rate computation (`arrheniusRate`)
- [x] Arrhenius parameter fitting (`fitArrhenius`)
- [x] Michaelis–Menten rate computation (`michaelisMentenRate`)
- [x] Lineweaver–Burk regression (`fitLineweaverBurk`)
- [x] Reaction network simulation via RK4 (`simulateNetwork`)
- [x] Conservation law extraction (`conservationLaws`)
- [x] Sequential first-order kinetics (`sequentialFirstOrder`)
- [ ] Nonlinear Michaelis–Menten fitting (deferred — requires nonlinear least-squares framework)
- [ ] Stiff ODE integrators (deferred — requires implicit solver infrastructure)
- [ ] Oregonator simulation and bifurcation analysis (documented — requires continuation methods)
- [ ] Sensitivity analysis of rate parameters (deferred — requires automatic differentiation)

---
### Implementation Context

**Design decisions.** Analytical solutions (zeroth, first, second order) are preferred over numerical integration where available, providing $O(1)$ evaluation without step-size concerns. Reaction network simulation delegates to RK4 via the standard `(t, y) => dydt` interface from `evenwicht/ode`, with the vector field $\mathbf{f}(\mathbf{c}) = N \cdot \mathbf{r}(\mathbf{c})$ computed as a stoichiometry-matrix-times-rate-vector product. Conservation laws are extracted by computing the left null space of the stoichiometry matrix $N$ via SVD.

**Numerical pitfalls.** Chemical kinetics frequently exhibit stiffness: rate constants spanning orders of magnitude ($k_1 \sim 10^6$, $k_2 \sim 10^0$) force RK4 to use impractically small step sizes. The implementation uses a conservative initial $h = 0.01 / \max_j r_j(\mathbf{c}_0)$ to prevent any reaction from depleting more than 1% of its reactant per step. Explicit integrators can produce small negative concentrations near species depletion; concentrations are clamped to zero after each step. The Lineweaver-Burk double-reciprocal regression amplifies errors at low substrate concentrations where $1/[S]$ is large; restricting data to $[S] \geq K_m/5$ mitigates this distortion.

**Arrhenius regression.** The linearised fit ($\ln k$ vs $1/T$) can be ill-conditioned when the temperature range is narrow. A span of at least 30-50 K is recommended for reliable activation energy estimates. The condition number of the regression matrix should be below $10^3$.

**Performance.** Analytical rate laws: $O(1)$. Network simulation: $O(N_{\text{steps}} \cdot mr)$ for $m$ species and $r$ reactions. Arrhenius and Lineweaver–Burk fitting: $O(n)$ for $n$ data points. Conservation law extraction: $O(m^2 r)$ for the SVD of the $r \times m$ transposed stoichiometry matrix.

**Testing.** Analytical solutions are cross-validated against RK4 simulation of the same rate law. Half-life formulas are tested against the definition $[A](t_{1/2}) = [A]_0/2$. Conservation laws are verified by confirming that $\boldsymbol{\ell}^T \mathbf{c}(t) = \boldsymbol{\ell}^T \mathbf{c}(0)$ along simulated trajectories. The sequential kinetics $A \to B \to C$ is tested against the Bateman analytical solution.

