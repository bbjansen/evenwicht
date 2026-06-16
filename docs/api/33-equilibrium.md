<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Equilibrium & Steady States — API Reference

This is the API reference for the TypeScript implementation of Equilibrium & Stability Analysis. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/applications/equilibrium.ts`

### Data Representation

Dynamical systems are specified as objects with a `dimension`, a vector field function `f(x)` and a `jacobian(x)` function. Equilibrium results contain the fixed point, eigenvalues (as `[real, imag]` pairs), a stability classification string and a boolean stability flag. The module depends on eigenvalue computation from `evenwicht/linear` and Newton's method from `evenwicht/optimization`.

### API Preview

```typescript
// src/applications/equilibrium.ts

interface DynamicalSystem {
  dimension: number;
  f: (x: number[]) => number[];
  jacobian: (x: number[]) => number[][];
}

interface EquilibriumResult {
  point: number[];
  eigenvalues: [number, number][];
  classification: 'stable_node' | 'stable_spiral' | 'unstable_node'
    | 'unstable_spiral' | 'saddle' | 'center' | 'indeterminate';
  stable: boolean;
}

/**
 * Find equilibrium near initialGuess via Newton's method,
 * then classify stability via Jacobian eigenvalue analysis.
 */
function findEquilibrium(
  system: DynamicalSystem,
  initialGuess: number[],
  tolerance?: number,
  maxIterations?: number,
): EquilibriumResult;

/**
 * Solow growth model steady state for Cobb-Douglas f(k) = k^alpha.
 * Returns k*, y*, and the speed of convergence delta*(1-alpha).
 */
function solowSteadyState(
  alpha: number, savingsRate: number, depreciation: number,
): { kStar: number; yStar: number; convergenceRate: number };

/**
 * Chemical equilibrium solver for A <=> B + C.
 * Solves K = (B0 + xi)(C0 + xi) / (A0 - xi) for the extent of reaction xi.
 */
function chemicalEquilibrium(
  K: number, A0: number, B0: number, C0: number,
): { xi: number; A: number; B: number; C: number };
```

### Error Handling

- `findEquilibrium` uses Newton's method with default tolerance $10^{-12}$ and 50 maximum iterations. It returns the best iterate found even if convergence is not achieved, with the classification based on the Jacobian at that point.
- Eigenvalue classification uses a threshold of $10^{-10}$ for distinguishing zero from nonzero real and imaginary parts.
- `solowSteadyState` throws if `alpha` is outside `(0, 1)` or if `savingsRate` or `depreciation` is non-positive.
- `chemicalEquilibrium` selects the physically admissible root of the quadratic (positive extent of reaction that does not exceed the initial reactant concentration).

### Dependencies

- `src/linear/eigen.ts` — eigenvalue computation for Jacobian stability classification
- `src/optimization/unconstrained.ts` — Newton's method for finding fixed points

### Usage Examples

```typescript
import { findEquilibrium, solowSteadyState, chemicalEquilibrium } from 'evenwicht/applications';

// Solow growth model: alpha=0.3, savings=0.2, depreciation=0.05
const solow = solowSteadyState(0.3, 0.2, 0.05);
// solow.kStar ≈ 7.25, solow.yStar ≈ 1.81

// Chemical equilibrium: A <=> B + C with K=4, A0=1, B0=0, C0=0
const chem = chemicalEquilibrium(4, 1, 0, 0);
// chem.xi ≈ 0.618, chem.A ≈ 0.382

// 2D dynamical system: find equilibrium near (1, 1)
const eq = findEquilibrium({
  dimension: 2,
  f: (x) => [x[0] - x[0] * x[1], -x[1] + x[0] * x[1]],
  jacobian: (x) => [[1 - x[1], -x[0]], [x[1], -1 + x[0]]],
}, [1, 1]);
// eq.point ≈ [1, 1], eq.classification === 'center'
```

### Connections

This chapter synthesises Chapter 10 (eigenvalues of the Jacobian determine local stability), Chapter 11 (thermodynamic equilibrium as energy minimisation; the second-derivative test classifies minima), Chapter 18 (discrete-time fixed points and their stability in the Solow model and market dynamics) and Chapter 19 (equilibria as zeros of the ODE right-hand side; linearisation and phase portraits). It connects forward to Chapter 36 (Nash equilibrium as a fixed-point concept in game theory) and to Chapter 29 (feedback control stabilising an unstable equilibrium).

- **Eigenvalues** (Chapter 10): The entire stability theory of equilibria rests on eigenvalue computation. The Jacobian matrix is the linearisation of the nonlinear system; its eigenvalues determine whether perturbations grow or decay. The QR algorithm (Chapter 10) provides the numerical backbone for Algorithm 33.27.

- **Unconstrained Optimisation** (Chapter 11): Thermodynamic equilibrium is free energy minimisation. Mechanical equilibrium is potential energy minimisation. The second-derivative test from Chapter 11 directly gives the stability classification of Theorem 33.12. Gradient descent on a potential landscape is precisely the damped dynamics that converge to stable equilibria.

- **Difference Equations** (Chapter 18): The discrete-time Solow model $k_{t+1} = (1-\delta)k_t + sf(k_t)$ is a first-order difference equation whose fixed point and stability are analysed using the techniques of Chapter 18. Market tatonnement in discrete time similarly produces a map whose eigenvalues must lie inside the unit disk.

- **Ordinary Differential Equations** (Chapter 19): Equilibria are defined as zeros of the ODE right-hand side. Phase portraits (Chapter 19) visualise the flow near equilibria. The Hartman–Grobman theorem guarantees that the linearised stability classification applies to the full nonlinear system when the equilibrium is hyperbolic.

- **Epidemiology** (Chapter 30): The disease-free equilibrium of the SIR model and its stability (determined by $R_0$) is a direct application of this chapter's framework. Endemic equilibria involve the same Jacobian eigenvalue analysis.

- **Control Systems** (Chapter 29): Feedback control aims to stabilise an otherwise unstable equilibrium by modifying the system's Jacobian eigenvalues. Pole placement and state feedback are eigenvalue assignment problems applied to the framework of Theorem 33.3.



### What Is Implemented vs. Documented Only

- [x] General equilibrium finder via Newton's method with Jacobian evaluation
- [x] Eigenvalue-based stability classification (stable node, stable spiral, unstable node, unstable spiral, saddle, centre)
- [x] Solow model steady-state computation (Cobb–Douglas production function)
- [x] Chemical equilibrium solver for A <==> B + C via quadratic formula
- [x] IS-LM equilibrium computation with Jacobian eigenvalue analysis
- [x] Lotka–Volterra equilibrium analysis
- [ ] Bifurcation analysis and continuation methods (documented conceptually; deferred)
- [ ] Lyapunov function construction for global stability (documented theoretically; not implemented)
- [ ] Discrete-time equilibrium and stability analysis (deferred; only continuous-time systems are implemented)
- [ ] General n-species ecological equilibrium solvers (out of scope; only two-species Lotka–Volterra is implemented)

---


### Implementation Context

The following TypeScript implementations illustrate the core algorithms within the Evenwicht library architecture.
