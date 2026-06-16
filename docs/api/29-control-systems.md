<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Control Systems — API Reference

This is the API reference for the TypeScript implementation of Control Systems. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/control/pid.ts` — PID controller step function and closed-loop simulation
- `src/control/statespace.ts` — poles, controllability, observability checks
- `src/control/lqr.ts` — continuous-time and discrete-time LQR solvers

### Data Representation

State-space matrices ($A$, $B$, $C$, $Q$, $R$) are stored as flat row-major `Float64Array` values with explicit dimension parameters. PID gains are structured as `PIDGains` objects. Poles are returned as `[real, imag]` pairs. The LQR solver returns the feedback gain matrix $K$ and the Riccati solution $P$ as flat `Float64Array` values.

### API Preview

```typescript
// src/control/pid.ts

/**
 * PID controller parameters.
 */
interface PIDGains {
  /** Proportional gain. */
  Kp: number;
  /** Integral gain. */
  Ki: number;
  /** Derivative gain. */
  Kd: number;
}

/**
 * State of a PID controller (for incremental updates).
 */
interface PIDState {
  integral: number;
  previousError: number;
}

/**
 * Compute PID control output for a single time step.
 *
 * @param gains - PID gains (Kp, Ki, Kd).
 * @param error - Current error e = setpoint - measurement.
 * @param state - Mutable PID state (integral accumulator, previous error).
 * @param dt - Time step size.
 * @returns The control signal u.
 */
function pidStep(
  gains: PIDGains,
  error: number,
  state: PIDState,
  dt: number,
): number;

/**
 * Simulate closed-loop PID control of a state-space plant.
 *
 * @param A - State matrix (n x n), as flat row-major Float64Array.
 * @param B - Input matrix (n x 1), as Float64Array.
 * @param C - Output matrix (1 x n), as Float64Array.
 * @param gains - PID gains.
 * @param reference - Reference signal function r(t).
 * @param x0 - Initial state (n x 1), as Float64Array.
 * @param tEnd - Simulation end time.
 * @param dt - Time step.
 * @returns Object with arrays t, y, u, x for time, output, control and state history.
 */
function simulatePID(
  A: Float64Array,
  B: Float64Array,
  C: Float64Array,
  gains: PIDGains,
  reference: (t: number) => number,
  x0: Float64Array,
  tEnd: number,
  dt: number,
): { t: Float64Array; y: Float64Array; u: Float64Array; x: Float64Array[] };
```

```typescript
// src/control/statespace.ts

/**
 * Compute the poles (eigenvalues of A) of a state-space system.
 *
 * @param A - State matrix (n x n), flat row-major Float64Array.
 * @param n - Dimension of the state.
 * @returns Array of complex poles as [real, imag] pairs.
 */
function poles(A: Float64Array, n: number): Array<[number, number]>;

/**
 * Check controllability of the pair (A, B).
 *
 * @param A - State matrix (n x n), flat row-major.
 * @param B - Input matrix (n x m), flat row-major.
 * @param n - State dimension.
 * @param m - Input dimension.
 * @returns true if rank of controllability matrix equals n.
 */
function isControllable(
  A: Float64Array,
  B: Float64Array,
  n: number,
  m: number,
): boolean;

/**
 * Check observability of the pair (A, C).
 *
 * @param A - State matrix (n x n), flat row-major.
 * @param C - Output matrix (p x n), flat row-major.
 * @param n - State dimension.
 * @param p - Output dimension.
 * @returns true if rank of observability matrix equals n.
 */
function isObservable(
  A: Float64Array,
  C: Float64Array,
  n: number,
  p: number,
): boolean;
```

```typescript
// src/control/lqr.ts

/**
 * Options for the LQR solver.
 */
interface LQROptions {
  /** Convergence tolerance for Riccati iteration. Default: 1e-10. */
  tolerance?: number;
  /** Maximum iterations. Default: 1000. */
  maxIterations?: number;
}

/**
 * Solve the continuous-time LQR problem.
 *
 * @param A - State matrix (n x n), flat row-major.
 * @param B - Input matrix (n x m), flat row-major.
 * @param Q - State cost matrix (n x n), flat row-major, positive semi-definite.
 * @param R - Control cost matrix (m x m), flat row-major, positive definite.
 * @param n - State dimension.
 * @param m - Input dimension.
 * @param opts - Solver options.
 * @returns Object { K, P } where K is the feedback gain (m x n) and P solves the CARE.
 * @throws Error if system is not stabilizable or iteration does not converge.
 */
function lqr(
  A: Float64Array,
  B: Float64Array,
  Q: Float64Array,
  R: Float64Array,
  n: number,
  m: number,
  opts?: LQROptions,
): { K: Float64Array; P: Float64Array };

/**
 * Solve the discrete-time LQR problem.
 *
 * @param A - State matrix (n x n), flat row-major.
 * @param B - Input matrix (n x m), flat row-major.
 * @param Q - State cost matrix (n x n), flat row-major.
 * @param R - Control cost matrix (m x m), flat row-major.
 * @param n - State dimension.
 * @param m - Input dimension.
 * @param opts - Solver options.
 * @returns Object { K, P } where K is the feedback gain and P solves the DARE.
 */
function dlqr(
  A: Float64Array,
  B: Float64Array,
  Q: Float64Array,
  R: Float64Array,
  n: number,
  m: number,
  opts?: LQROptions,
): { K: Float64Array; P: Float64Array };
```

### Error Handling

- `pidStep` throws if `dt <= 0`.
- `simulatePID` throws if matrix dimensions are inconsistent or `tEnd <= 0`.
- `isControllable` / `isObservable` throw if matrix dimensions do not match.
- `lqr` / `dlqr` throw if $R$ is not positive definite, or if the iteration fails to converge (the system may not be stabilisable).

### Dependencies

- `src/linear/eigen.ts` — eigenvalue computation for poles and stability analysis
- `src/linear/solve.ts` — linear system solve for Riccati iteration
- `src/linear/inverse.ts` — matrix inversion in LQR gain computation
- `src/dynamics/ode.ts` — RK4 integration for `simulatePID`

### Usage Examples

```typescript
import { pidStep, simulatePID, lqr, isControllable } from 'evenwicht/control';

// PID controller for a simple first-order plant
const gains = { Kp: 2.0, Ki: 0.5, Kd: 0.1 };
const state = { integral: 0, previousError: 0 };
const u = pidStep(gains, 1.0, state, 0.01);  // control signal for error = 1.0

// Check controllability of a 2D system
const A = new Float64Array([0, 1, -2, -3]);
const B = new Float64Array([0, 1]);
isControllable(A, B, 2, 1);  // true

// LQR: optimal gain for double integrator
const Q = new Float64Array([1, 0, 0, 1]);
const R = new Float64Array([1]);
const { K, P } = lqr(A, B, Q, R, 2, 1);
```

### Connections

This chapter synthesises Chapter 10 (eigenvalues determine stability of the closed-loop system), Chapter 11 (LQR is a quadratic optimisation over linear dynamics), Chapter 18 (discrete-time control systems, digital PID), Chapter 19 (continuous dynamics of physical plants, matrix exponential for state transitions) and Chapter 22 (Laplace/z-transforms yield transfer functions and enable frequency-domain design). It connects forward to applications in robotics, aerospace and algorithmic trading execution.

- **Eigenvalues** (Chapter 10): Stability of a control system reduces to the eigenvalue problem. The eigenvalues of $A$ determine open-loop stability; the eigenvalues of $A - BK$ determine closed-loop stability. The QR algorithm from Chapter 10 provides the numerical engine for pole computation.

- **Optimisation** (Chapter 11): The LQR problem is a continuous-time quadratic optimisation with linear constraints. The Riccati equation is the optimality condition. The trade-off between state penalty ($Q$) and control penalty ($R$) is a classic multi-objective optimisation problem parametrised by positive-definite matrices.

- **Difference Equations** (Chapter 18): Discrete-time control systems are precisely the linear recurrences of Chapter 18 with an input term. The z-transform analysis of discrete controllers parallels the algebraic solution of linear recurrences via generating functions.

- **Ordinary Differential Equations** (Chapter 19): The plant dynamics

    $$\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$$

    is a system of linear ODEs. The matrix exponential solution (Definition 19.13) uses the exponential of the state matrix. Numerical simulation of closed-loop systems employs RK4 from Chapter 19.

- **Transforms** (Chapter 22): The Laplace transform converts the ODE description into the algebraic transfer function $G(s)$. The $z$-transform does the same for discrete systems. Frequency-domain design (Bode, Nyquist) operates entirely in the transform domain.



### What Is Implemented vs. Documented Only

- [x] PID step computation (`pidStep`)
- [x] Closed-loop PID simulation (`simulatePID`)
- [x] Pole computation via eigenvalues (`poles`)
- [x] Controllability check (`isControllable`)
- [x] Observability check (`isObservable`)
- [x] LQR via iterative Riccati (`lqr`)
- [x] Discrete LQR (`dlqr`)
- [ ] Routh–Hurwitz criterion (documented, not implemented — use eigenvalue method)
- [ ] Kalman filter (deferred — requires stochastic framework)
- [ ] Pole placement via Ackermann's formula (deferred)
- [ ] Bode plot generation (deferred — requires frequency sweep)
- [ ] Nyquist plot computation (deferred)

---
### Implementation Context

**Design decisions.** State-space matrices use flat row-major `Float64Array` with explicit dimension parameters rather than a matrix class, matching the layout expected by the linear algebra routines and avoiding wrapper overhead in the inner simulation loop. The PID controller uses a mutable `PIDState` object to carry the integral accumulator and previous error across steps, enabling both standalone step computation and full closed-loop simulation.

**Algorithm choices.** Pole computation delegates to the QR eigenvalue algorithm from Chapter 10 via the companion matrix formulation. The controllability and observability checks build the full Cayley-Hamilton matrices

$$[B,\; AB,\; \ldots,\; A^{n-1}B]$$

and determine rank via SVD, using a tolerance of $\epsilon \cdot \sigma_{\max}$ for singular value thresholding. The LQR solver uses iterative Lyapunov-based Riccati iteration (Algorithm 6.4) rather than the Schur-Hamiltonian method, which is more numerically stable but requires additional infrastructure.

**Numerical pitfalls.** The controllability matrix becomes exponentially ill-conditioned as $n$ grows because columns $A^k B$ span increasingly skewed directions; SVD-based rank detection is necessary for $n > 10$. The Riccati iteration can diverge when $(A, B)$ is nearly uncontrollable or when the initial guess $P_0 = Q$ is far from the solution. Plants with widely separated eigenvalues produce stiff closed-loop dynamics under PID; the RK4 step size must resolve the fastest mode. The derivative term in PID amplifies sensor noise; the backward-difference approximation

$$(e - e_{\text{prev}})/dt$$

is first-order and sufficient for smooth reference signals.

**Performance.**

- PID simulation costs $O(Nn^2)$ per step for $n$-dimensional state (matrix-vector product in RK4).
- LQR iteration costs $O(kn^3)$ for $k$ Lyapunov solves.
- Controllability check costs $O(n^4)$ (building $n$ matrix-vector products plus an SVD).

**Testing.** The double integrator

$$A = \begin{bmatrix}0 & 1\\0 & 0\end{bmatrix},\quad B = \begin{bmatrix}0\\1\end{bmatrix}$$

provides an analytically solvable LQR benchmark. PID closed-loop simulation is tested against known step-response characteristics (rise time, overshoot, steady-state error). Controllability and observability are verified on canonical controllable/uncontrollable pairs.

