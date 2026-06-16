<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Pharmacokinetics — API Reference

This is the API reference for the TypeScript implementation of Pharmacokinetics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/pharmacokinetics/one-compartment.ts` — IV bolus, half-life, clearance, AUC, multiple dosing
- `src/pharmacokinetics/oral.ts` — oral absorption (Bateman equation), tmax, cmax
- `src/pharmacokinetics/two-compartment.ts` — two-compartment IV model, macro constants
- `src/pharmacokinetics/dosing.ts` — steady state, accumulation, loading dose, regimen design
- `src/pharmacokinetics/auc.ts` — trapezoidal AUC, linear-log AUC, terminal extrapolation

### Data Representation

Pharmacokinetic models operate on concentration–time profiles represented as parallel `Float64Array` instances for time and concentration values. The ODE right-hand side for multicompartment models follows the signature `(t: number, y: Float64Array) => Float64Array`, consistent with the numerical integration routines in `evenwicht/ode`.

### API Preview

```typescript
// src/pharmacokinetics/one-compartment.ts

/**
 * Parameters for the one-compartment IV bolus model.
 */
interface OneCompartmentParams {
  /** Elimination rate constant (1/h). */
  ke: number;
  /** Volume of distribution (L). */
  Vd: number;
}

/**
 * Compute plasma concentration at time t after IV bolus.
 */
function ivBolus(params: OneCompartmentParams, dose: number, t: number): number;

/**
 * Compute the elimination half-life.
 */
function halfLife(ke: number): number;

/**
 * Compute clearance from ke and Vd.
 */
function clearance(ke: number, Vd: number): number;

/**
 * Compute AUC from 0 to infinity for IV bolus.
 */
function aucIVBolus(params: OneCompartmentParams, dose: number): number;

/**
 * Simulate multiple IV bolus doses.
 *
 * @param params - PK parameters.
 * @param dose - Dose per administration.
 * @param tau - Dosing interval (h).
 * @param nDoses - Number of doses.
 * @param dt - Simulation time step.
 * @returns Object with arrays t and C.
 */
function simulateMultipleDose(
  params: OneCompartmentParams,
  dose: number,
  tau: number,
  nDoses: number,
  dt: number,
): { t: Float64Array; C: Float64Array };
```

```typescript
// src/pharmacokinetics/oral.ts

/**
 * Parameters for the one-compartment oral model.
 */
interface OralParams {
  /** Absorption rate constant (1/h). */
  ka: number;
  /** Elimination rate constant (1/h). */
  ke: number;
  /** Volume of distribution (L). */
  Vd: number;
  /** Bioavailability (0 to 1). */
  F: number;
}

/**
 * Compute plasma concentration at time t after oral dose (Bateman equation).
 */
function oralConcentration(params: OralParams, dose: number, t: number): number;

/**
 * Compute time to peak concentration.
 */
function tmax(ka: number, ke: number): number;

/**
 * Compute peak concentration after oral dose.
 */
function cmax(params: OralParams, dose: number): number;

/**
 * Compute AUC from 0 to infinity for oral dose.
 */
function aucOral(params: OralParams, dose: number): number;
```

```typescript
// src/pharmacokinetics/two-compartment.ts

/**
 * Parameters for the two-compartment model.
 */
interface TwoCompartmentParams {
  /** Central compartment volume (L). */
  Vc: number;
  /** Transfer rate central to peripheral (1/h). */
  k12: number;
  /** Transfer rate peripheral to central (1/h). */
  k21: number;
  /** Elimination rate from central (1/h). */
  k10: number;
}

/**
 * Compute macro constants (alpha, beta, A, B) from micro constants.
 */
function macroConstants(
  params: TwoCompartmentParams,
  dose: number,
): { alpha: number; beta: number; A: number; B: number };

/**
 * Simulate two-compartment IV bolus using RK4.
 */
function simulateTwoCompartment(
  params: TwoCompartmentParams,
  dose: number,
  tEnd: number,
  dt: number,
): { t: Float64Array; C1: Float64Array; C2: Float64Array };
```

```typescript
// src/pharmacokinetics/dosing.ts

/**
 * Compute steady-state peak and trough for IV bolus repeated dosing.
 */
function steadyState(
  ke: number,
  Vd: number,
  dose: number,
  tau: number,
): { Cmax_ss: number; Cmin_ss: number; Cavg_ss: number };

/**
 * Compute the accumulation factor.
 */
function accumulationFactor(ke: number, tau: number): number;

/**
 * Compute loading dose to achieve immediate steady state.
 */
function loadingDose(maintenanceDose: number, ke: number, tau: number): number;

/**
 * Compute maximum dosing interval for a given therapeutic window.
 */
function maxDosingInterval(ke: number, MTC: number, MEC: number): number;

/**
 * Design a dosing regimen given PK parameters and therapeutic targets.
 */
function designRegimen(
  CL: number,
  Vd: number,
  F: number,
  MEC: number,
  MTC: number,
  targetCss: number,
): { dose: number; tau: number; loadingDose: number };
```

```typescript
// src/pharmacokinetics/auc.ts

/**
 * Compute AUC by linear trapezoidal rule from concentration-time data.
 */
function aucTrapezoidal(times: number[], concentrations: number[]): number;

/**
 * Compute AUC by linear-log trapezoidal rule.
 */
function aucLinearLog(times: number[], concentrations: number[]): number;

/**
 * Compute AUC with terminal extrapolation to infinity.
 *
 * @param times - Sampling times.
 * @param concentrations - Measured concentrations.
 * @param lambdaZ - Terminal elimination rate constant.
 * @returns Total AUC from 0 to infinity.
 */
function aucExtrapolated(
  times: number[],
  concentrations: number[],
  lambdaZ: number,
): number;

/**
 * Estimate terminal elimination rate constant from log-linear terminal phase.
 *
 * @param times - Sampling times in terminal phase.
 * @param concentrations - Measured concentrations in terminal phase.
 * @returns Estimated lambda_z.
 */
function estimateLambdaZ(times: number[], concentrations: number[]): number;
```

### Error Handling

- All functions throw if rate constants are non-positive or if $V_d \leq 0$.
- `oralConcentration` throws if $k_a = k_e$ (degenerate case requiring a separate formula involving $t \cdot e^{-k_e t}$).
- `aucTrapezoidal` and `aucLinearLog` throw if arrays have different lengths or fewer than 2 points.
- `estimateLambdaZ` throws if fewer than 3 terminal phase points are provided or if any concentration is non-positive.
- `designRegimen` throws if MEC $\geq$ MTC (invalid therapeutic window) or if the computed dose exceeds safety limits.

### Dependencies

- `src/dynamics/ode.ts` — RK4 for two-compartment model simulation
- `src/stats/regression.ts` — linear regression for terminal phase lambda_z estimation

### Usage Examples

```typescript
import { ivBolus, halfLife, steadyState, oralConcentration, tmax } from 'evenwicht/pharmacokinetics';

// IV bolus: 500mg dose, ke=0.1/h, Vd=50L, concentration at 4h
ivBolus({ ke: 0.1, Vd: 50 }, 500, 4);  // ≈ 6.70 mg/L

// Half-life
halfLife(0.1);  // 6.93 hours

// Steady-state from repeated IV doses (500mg every 8h)
const ss = steadyState(0.1, 50, 500, 8);
// ss.Cmax_ss, ss.Cmin_ss, ss.Cavg_ss

// Oral dose: time to peak concentration
tmax(1.5, 0.1);  // ≈ 1.8 hours (ka >> ke)
```

### Connections

This chapter synthesises Chapter 5 (AUC computation via improper integrals), Chapter 6 (geometric series for drug accumulation), Chapter 18 (difference equations governing trough concentrations across doses) and Chapter 19 (ODE formulation and eigenvalue solutions for compartmental models). It connects forward to Chapter 30 (Epidemiology; compartmental models share identical mathematical structure), Chapter 17 (Regression; population PK parameter estimation) and Chapter 10 (Eigenvalues; two-compartment model analysis).

- **Integral Calculus** (Chapter 5): The AUC is the fundamental pharmacokinetic exposure metric, computed as an improper integral for analytic models and by the trapezoidal rule for discrete data. The relationship $\text{AUC} = D/CL$ is a direct consequence of integration of the exponential decay. Bioavailability is defined as a ratio of integrals.

- **Series & Approximation** (Chapter 6): The geometric series $\sum r^j = 1/(1-r)$ is the mathematical engine of repeated dosing pharmacokinetics. Every accumulation formula (peak, trough, average at steady state) derives from the partial or infinite geometric sum. The convergence rate of the geometric series directly determines the time to steady state.

- **Difference Equations** (Chapter 18): The trough concentration sequence $C_{n+1}^- = rC_n^- + rC_0$ is a first-order linear difference equation whose fixed-point analysis provides an alternative derivation of steady-state results. The stability condition $|r| < 1$ (always satisfied for positive $k_e$ and $\tau$) guarantees convergence to steady state from any initial condition.

- **Ordinary Differential Equations** (Chapter 19): The one-compartment model is a first-order linear ODE; the oral model is a first-order linear ODE with exponential forcing; the two-compartment model is a linear system whose solution involves matrix exponentials and eigenvalue decomposition. The classification of the two-compartment system as a stable node (two distinct negative real eigenvalues) follows from the eigenvalue theory of Chapter 19.

- **Eigenvalues** (Chapter 10): The macro rate constants $\alpha$ and $\beta$ of the two-compartment model are the negated eigenvalues of the system matrix. The biexponential solution is the spectral decomposition of the matrix exponential. Curve stripping is equivalent to identifying eigenvalues from the time-domain response; a direct application of the eigenvalue-eigenvector framework.

- **Regression** (Chapter 17): Pharmacokinetic parameter estimation from clinical data uses linear regression (semilogarithmic terminal phase for $k_e$), nonlinear least-squares (fitting compartmental models to full concentration–time profiles) and mixed-effects models (population PK). The regression diagnostics of Chapter 17 (residual analysis, confidence intervals, multicollinearity) apply directly.



### What Is Implemented vs. Documented Only

- [x] One-compartment IV bolus concentration (`ivBolus`)
- [x] Half-life, clearance computations (`halfLife`, `clearance`)
- [x] AUC for IV bolus (`aucIVBolus`)
- [x] Multiple-dose IV bolus simulation (`simulateMultipleDose`)
- [x] Oral concentration via Bateman equation (`oralConcentration`)
- [x] Tmax and Cmax computation (`tmax`, `cmax`)
- [x] Two-compartment simulation via RK4 (`simulateTwoCompartment`)
- [x] Macro constant computation (`macroConstants`)
- [x] Steady-state calculations (`steadyState`, `accumulationFactor`)
- [x] Loading dose and dosing interval (`loadingDose`, `maxDosingInterval`)
- [x] AUC by trapezoidal rule (`aucTrapezoidal`, `aucLinearLog`)
- [x] Terminal phase estimation (`estimateLambdaZ`)
- [ ] Nonlinear (Michaelis–Menten) kinetics (deferred — requires nonlinear ODE solver)
- [ ] Population PK mixed-effects estimation (deferred — requires nonlinear mixed-effects framework)
- [ ] PBPK multi-organ simulation (deferred — requires tissue-specific parametrisation)
- [ ] Bayesian individual parameter estimation (deferred — requires MCMC framework)

---
### Implementation Context

**Design decisions.** One-compartment models use closed-form exponentials evaluated via `Math.exp`, avoiding numerical integration entirely. The two-compartment model uses RK4 because the biexponential analytical solution requires computing macro constants from micro constants (a quadratic eigenvalue problem), which is provided as a separate `macroConstants` function but is numerically sensitive when $\alpha \approx \beta$. Multiple-dose simulation superposes individual dose contributions analytically via $\sum_j C_0 e^{-k_e(t - t_j)}$, which is $O(n_{\text{doses}})$ per time point.

**Numerical pitfalls.** The oral Bateman equation $C(t) \propto (e^{-k_e t} - e^{-k_a t}) / (k_a - k_e)$ has catastrophic cancellation when $k_a \approx k_e$; the implementation throws for the degenerate case, which requires the separate formula $C(t) \propto t e^{-k_e t}$. The two-compartment model becomes stiff when $\alpha/\beta \gg 1$ (fast distribution, slow elimination); RK4 requires $h < 2/\alpha$ for stability while the simulation extends to $5/\beta$. For stiffness ratios below 50 (typical in pharmacokinetics), RK4 with $h = 0.01$ h suffices.

**AUC computation.** The linear trapezoidal rule is the regulatory standard (FDA guidance). The linear-log variant uses $\text{AUC}_i = (C_i - C_{i+1})(t_{i+1} - t_i) / \ln(C_i/C_{i+1})$ during the elimination phase, which is exact for monoexponential decline. Terminal extrapolation adds $C_{\text{last}}/\lambda_z$ to the measured AUC. Estimating $\lambda_z$ requires at least 3 points spanning 2-3 half-lives in the terminal phase.

**Performance.** All one-compartment computations are $O(1)$ per time point. Multiple-dose simulation is $O(N_{\text{steps}} \cdot n_{\text{doses}})$. Two-compartment RK4 is $O(N_{\text{steps}})$ with constant-size (2D) state. AUC by trapezoidal rule is $O(n)$ for $n$ data points.

**Testing.** IV bolus concentrations are tested against the identity $C(t_{1/2}) = C_0/2$. Steady-state peak/trough formulas are verified against explicit simulation over many dosing cycles. The AUC of an IV bolus is cross-checked against the analytical result $D/(k_e \cdot V_d)$. The accumulation factor $1/(1 - r)$ is tested against the geometric series partial sum at $n = 100$ doses.

