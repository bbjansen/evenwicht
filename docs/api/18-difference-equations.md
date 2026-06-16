<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Difference Equations & Dynamical Systems — API Reference

This is the API reference for the TypeScript implementation of Difference Equations & Dynamical Systems. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/dynamics/`

- `src/dynamics/difference.ts` — first-order and second-order linear difference equations, forward simulation
- `src/dynamics/system.ts` — vector-valued linear systems $\mathbf{x}_{t+1} = A\mathbf{x}_t + \mathbf{b}$
- `src/dynamics/logistic.ts` — logistic map, bifurcation analysis

### Data Representation

Scalar difference equations use plain `number` sequences. Vector-valued systems use `Float64Array` for state vectors and the `Matrix` type from `src/linear/matrix.ts` for transition matrices. Simulation outputs are arrays of state snapshots at each time step.

### API Preview

```typescript
// src/dynamics/difference.ts

interface DifferenceEqResult {
  trajectory: Float64Array;
  equilibrium?: number;
  converged: boolean;
}

/**
 * Solve a first-order linear difference equation x_{t+1} = a*x_t + b.
 *
 * @param a - Coefficient of x_t.
 * @param b - Constant term.
 * @param x0 - Initial condition.
 * @param steps - Number of steps to simulate.
 * @returns Trajectory [x_0, x_1, ..., x_steps].
 */
function solveDifferenceEq(
  a: number, b: number, x0: number, steps: number,
): DifferenceEqResult;

/**
 * Simulate a general scalar difference equation x_{t+1} = f(x_t).
 *
 * @param f - The iteration function.
 * @param x0 - Initial condition.
 * @param steps - Number of steps.
 * @returns Array of values [x_0, x_1, ..., x_steps].
 */
function simulateDifference(
  f: (x: number) => number, x0: number, steps: number,
): Float64Array;

// src/dynamics/system.ts

/**
 * Simulate the linear system x_{t+1} = A*x_t + b.
 *
 * @param A - Transition matrix (n x n).
 * @param b - Constant vector (length n), or zero vector if omitted.
 * @param x0 - Initial state vector (length n).
 * @param steps - Number of time steps.
 * @returns Array of state vectors [x_0, x_1, ..., x_steps].
 */
function simulateLinearSystem(
  A: Matrix, b: Float64Array, x0: Float64Array, steps: number,
): Float64Array[];

// src/dynamics/logistic.ts

/**
 * Simulate the logistic map x_{t+1} = r*x_t*(1 - x_t).
 *
 * @param r - Growth parameter.
 * @param x0 - Initial condition in (0, 1).
 * @param steps - Number of iterations.
 * @returns Trajectory array.
 */
function logisticMap(r: number, x0: number, steps: number): Float64Array;
```

### Error Handling

- `solveDifferenceEq` throws an `Error` if $1 + a_1 + a_2 = 0$ for a second-order equation (no finite equilibrium exists).
- `simulateDifference` throws an `Error` if `steps` is negative.
- `simulateLinearSystem` throws an `Error` if the dimensions of $A$, $\mathbf{b}$ and $\mathbf{x}_0$ are incompatible.
- `logisticMap` throws if `x0` is outside $(0, 1)$ or if `r` is non-positive.

### Dependencies

- `src/linear/matrix.ts` — `Matrix` type and `matrixVectorProduct` for system simulation
- `src/linear/eigen.ts` — eigenvalue computation for stability analysis of transition matrices

### Usage Examples

```typescript
import { solveDifferenceEq, simulateLinearSystem, logisticMap } from 'evenwicht/dynamics';
import { matrix } from 'evenwicht/linear';

// First-order: x_{t+1} = 0.8*x_t + 10  (converges to x* = 50)
const result = solveDifferenceEq(0.8, 10, 0, 50);
// result.trajectory[50] ≈ 50

// Logistic map in chaotic regime
const chaos = logisticMap(3.9, 0.5, 200);

// 2D linear system
const A = matrix(2, 2, new Float64Array([0.5, 0.1, 0.0, 0.8]));
const b = new Float64Array([1, 0]);
const x0 = new Float64Array([0, 0]);
const trajectory = simulateLinearSystem(A, b, x0, 100);
```

### Connections

This chapter is used by Chapter 19 (Ordinary Differential Equations; the continuous analogue, where stability requires $\operatorname{Re}(\lambda) < 0$ rather than $|\lambda| < 1$), Chapter 20 (Discrete Operators; the shift operator $E$ and its algebra formalise difference equations) and Chapter 21 (Time Series; ARMA models are difference equations driven by white noise). It builds on Chapter 9 (matrix systems $\mathbf{x}_{t+1} = A\mathbf{x}_t$) and Chapter 10 (eigenvalues of the transition matrix determine long-run behaviour).

- **Chapter 9 (Matrices)**: The system $\mathbf{x}_{t+1} = A\mathbf{x}_t + \mathbf{b}$ is the primary application of matrix powers $A^t$. Computing the solution trajectory requires matrix-vector multiplication and the closed-form solution requires diagonalisation or Jordan decomposition. The companion matrix representation converts higher-order scalar equations into first-order systems, unifying the theory.

- **Chapter 10 (Eigenvalues)**: The stability criterion $\rho(A) < 1$ is the discrete-time analogue of the continuous-time condition $\operatorname{Re}(\lambda) < 0$. Eigenvalue computation is the computational bottleneck of stability analysis. Complex eigenvalues produce oscillatory dynamics; real eigenvalues produce monotone dynamics. The eigenvectors determine the directions along which the system evolves independently.

- **Chapter 19 (Ordinary Differential Equations)**: Continuous-time systems $\dot{\mathbf{x}} = A\mathbf{x}$ have solutions $\mathbf{x}(t) = e^{At}\mathbf{x}_0$, with stability requiring $\operatorname{Re}(\lambda) < 0$ for all eigenvalues. The passage from discrete to continuous is: $x_{t+1} - x_t = (A - I)x_t$, so the discrete map with matrix $A$ corresponds (heuristically) to the continuous system with matrix $A - I$. The stability condition $|\lambda| < 1$ maps to $\operatorname{Re}(\lambda - 1) < 0$, i.e., $\operatorname{Re}(\lambda) < 0$ for the continuous eigenvalue.

- **Chapter 20 (Discrete Operators)**: The shift operator $E$ defined by $Ex_t = x_{t+1}$ and the difference operator $\Delta = E - I$ provide an algebraic framework for solving difference equations. The characteristic equation $\lambda^2 + a_1\lambda + a_2 = 0$ arises from the operator equation $(E^2 + a_1E + a_2)x_t = 0$, treating $E$ as a formal variable.

- **Chapter 21 (Time Series)**: An ARMA$(p,q)$ model $x_t = \phi_1 x_{t-1} + \cdots + \phi_p x_{t-p} + \varepsilon_t + \theta_1\varepsilon_{t-1} + \cdots + \theta_q\varepsilon_{t-q}$ is a stochastic difference equation. The AR component is a deterministic difference equation driven by noise. Stationarity of the AR process requires all roots of the characteristic polynomial $1 - \phi_1\lambda - \cdots - \phi_p\lambda^p$ to lie outside the unit circle. This is the same spectral radius condition as deterministic stability, expressed in reciprocal form.



### What Is Implemented vs. Documented Only

- [x] First-order analytical solution (`solveDifferenceEq` with `order: 1`)
- [x] Second-order analytical solution (`solveDifferenceEq` with `order: 2`)
- [x] Forward simulation for scalar equations (`simulateDifference`)
- [x] Forward simulation for linear systems (`simulateLinearSystem`)
- [ ] Schur–Cohn stability test as a standalone function (deferred)
- [ ] Bifurcation diagram computation (deferred)
- [ ] Nonlinear system simulation (deferred)

---
### Implementation Context

**Data structures.** Scalar trajectories use `Float64Array` for cache-friendly sequential access. Vector systems reuse the `Matrix` type from `src/linear/matrix.ts` for transition matrices and store each state snapshot as a separate `Float64Array`, avoiding a single large allocation that would be difficult to resize.

**Algorithm choice.** The analytical solution (closed-form via characteristic roots) is preferred over forward simulation when available, because it computes $x_t$ in $O(1)$ per query rather than $O(t)$. Forward simulation is used for general nonlinear maps where no closed form exists. The discriminant-based branching (distinct roots, repeated root, complex roots) follows Algorithm 3 in the domain chapter.

**Numerical pitfalls.** The geometric sum $b(1 - a^t)/(1 - a)$ suffers catastrophic cancellation when $a \approx 1$ and $t$ is moderate; the implementation detects $|1 - a| < 10^{-12}$ and falls back to the arithmetic growth formula $x_0 + bt$. The discriminant threshold $|D| < \epsilon$ triggers the repeated-root path to avoid the ill-conditioned distinct-root formula when roots nearly coincide. Computing $a^t$ via `Math.pow` avoids the $O(t)$ error accumulation of manual multiplication loops.

**Performance.** Scalar simulation is $O(T)$; system simulation is $O(Tn^2)$ per step due to matrix-vector multiplication. For long trajectories of linear systems, diagonalisation-based $O(n^3)$ solutions are faster when $T \gg n$, but only when the eigenvector matrix is well-conditioned.

**Testing.** Analytical solutions are verified against forward simulation for agreement within RK4-level tolerance. Stability classification is tested at the Schur-Cohn boundary ($|a_2| = 1 \pm \epsilon$). The logistic map is tested at known bifurcation points ($r = 3.0$, $r = 3.449$) and in the chaotic regime ($r = 3.9$) against published orbit statistics.

