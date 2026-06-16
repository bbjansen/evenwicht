<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Ordinary Differential Equations — API Reference

This is the API reference for the TypeScript implementation of Ordinary Differential Equations. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

The ODE solver in Evenwicht is located in:

- `src/dynamics/ode.ts` — Euler's method, RK4 and the `solveODE` interface

### Data Representation

Scalar ODEs use `number` for the state variable. Systems of ODEs use `Float64Array` for state vectors. The right-hand side function signature is `(t: number, y: number | Float64Array) => number | Float64Array`. Time values are stored in `Float64Array`; solution values are stored as `number[]` (scalar) or `Float64Array[]` (systems).

### API Preview

```typescript
// src/dynamics/ode.ts

/**
 * The right-hand side of an ODE y' = f(t, y).
 * For scalar ODEs, y is a number. For systems, y is a Float64Array.
 */
type ODEFunction = (t: number, y: number | Float64Array) => number | Float64Array;

/**
 * Options for the ODE solver.
 */
interface SolveODEOptions {
    /** The numerical method to use. Default: 'rk4'. */
    method?: 'euler' | 'rk4';
    /** Step size h. Default: 0.01. */
    stepSize?: number;
    /** Number of steps. Either numSteps or tEnd must be provided. */
    numSteps?: number;
    /** End time. Either numSteps or tEnd must be provided. */
    tEnd?: number;
}

/**
 * Result of an ODE solve: arrays of time values and corresponding y values.
 */
interface ODESolution {
    /** Time values t_0, t_1, ..., t_N. */
    t: Float64Array;
    /** Solution values y(t_0), y(t_1), ..., y(t_N). For systems, each entry is a Float64Array. */
    y: number[] | Float64Array[];
}

/**
 * Solve the initial-value problem y' = f(t, y), y(t0) = y0.
 *
 * @param f - The right-hand side function.
 * @param t0 - Initial time.
 * @param y0 - Initial value (number for scalar ODE, Float64Array for system).
 * @param opts - Solver options (method, stepSize, numSteps or tEnd).
 * @returns An ODESolution containing time and solution arrays.
 * @throws Error if neither numSteps nor tEnd is provided.
 * @throws Error if stepSize is not positive.
 */
function solveODE(
    f: ODEFunction,
    t0: number,
    y0: number | Float64Array,
    opts?: SolveODEOptions
): ODESolution;
```

### Error Handling

- `solveODE` throws an `Error` if neither `numSteps` nor `tEnd` is provided.
- `solveODE` throws an `Error` if `stepSize` is zero or negative.
- Default method is `'rk4'`; default step size is $0.01$.
- For systems, the initial value `y0` and the return value of `f` must be `Float64Array` instances of matching length.

### Dependencies

- No external module dependencies; the ODE solver is self-contained
- Used by: `src/epidemiology/`, `src/pharmacokinetics/`, `src/applications/orbital.ts` and other simulation modules

### Usage Examples

```typescript
import { solveODE } from 'evenwicht/dynamics';

// Scalar ODE: exponential decay dy/dt = -0.5*y
const decay = solveODE(
  (t, y) => -0.5 * (y as number),
  0, 1.0,
  { method: 'rk4', tEnd: 10, stepSize: 0.01 },
);
// decay.y[decay.y.length - 1] ≈ exp(-5) ≈ 0.00674

// System: simple harmonic oscillator [x', v'] = [v, -x]
const sho = solveODE(
  (t, y) => {
    const state = y as Float64Array;
    return new Float64Array([state[1], -state[0]]);
  },
  0, new Float64Array([1.0, 0.0]),
  { method: 'rk4', tEnd: 6.2832, stepSize: 0.01 },
);
```

### Connections

This chapter extends Chapter 18 (Difference Equations; the discrete analogue, where $x_{k+1} = f(x_k)$ replaces $\dot{x} = f(x)$, and stability requires $|\lambda| < 1$ rather than $\operatorname{Re}(\lambda) < 0$). Chapter 23 (Operator Algebra) generalises the differential operator $D = d/dt$ to abstract linear operators on function spaces, and the characteristic polynomial of a linear ODE becomes the minimal polynomial of an operator. Chapter 10 (Eigenvalues) provides the eigenvalue criteria used in the stability analysis of Section 4.

- **Chapter 4 (Differential Calculus)**: Every ODE is fundamentally a statement about derivatives. The chain rule, product rule and other differentiation techniques are used both in deriving solutions (e.g. the integrating factor method uses the product rule) and in analysing error (Taylor expansion of the exact solution).

- **Chapter 5 (Integral Calculus)**: Solving an ODE analytically reduces, in many cases, to evaluating integrals; whether by separating variables or integrating both sides of the multiplied equation. The fundamental theorem of calculus connects the integral $\int f\,dx$ to the antiderivative, which is itself the solution of $y' = f(x)$.

- **Chapter 9 (Matrices)**: Systems of ODEs $\dot{\mathbf{x}} = A\mathbf{x}$ require matrix operations. The coefficient matrix $A$ encodes the coupling between state variables, and the solution involves matrix-vector multiplication, the eigendecomposition and the matrix exponential.

- **Chapter 10 (Eigenvalues)**: The stability of $\dot{\mathbf{x}} = A\mathbf{x}$ is determined entirely by the eigenvalues of $A$. Asymptotic stability requires all eigenvalues to have negative real parts; this is the continuous-time analogue of the discrete condition $|\lambda| < 1$ for $\mathbf{x}_{k+1} = A\mathbf{x}_k$ (Chapter 18).

- **Chapter 18 (Difference Equations)**: Difference equations are the discrete analogue of ODEs: the recurrence $x_{n+1} = f(x_n)$ replaces $\dot{x} = f(x)$, Euler's method is precisely the bridge between them ($x_{n+1} = x_n + hf(x_n)$), and the stability criterion $|\lambda| < 1$ is the discrete counterpart of $\operatorname{Re}(\lambda) < 0$.

- **Chapter 23 (Operator Algebra)**: The differential operator $D = d/dt$ is a linear operator on function spaces, and the linear ODE $a_n D^n y + \cdots + a_1 Dy + a_0 y = 0$ factors as $p(D)y = 0$ where $p$ is the characteristic polynomial. The eigenvalue equation $Dy = \lambda y$ has eigenfunctions $e^{\lambda t}$; these are the exponential solutions of Section 4.



### What Is Implemented vs. Documented Only

- [x] Euler's method (`method: 'euler'`)
- [x] Fourth-order Runge–Kutta (`method: 'rk4'`)
- [x] Scalar ODEs ($y$ is a number)
- [x] Systems of ODEs ($\mathbf{y}$ is a `Float64Array`)
- [ ] Adaptive step-size control (deferred)
- [ ] Implicit methods for stiff problems (deferred)
- [ ] Matrix exponential computation (deferred; documented in Definition 19.13)
- [ ] Event detection / zero-crossing (deferred)

---
### Implementation Context

**Algorithm choice.** Two methods are provided: Euler ($O(h)$ global error) for pedagogical use and prototyping, and RK4 ($O(h^4)$ global error) for production accuracy. RK4 requires four evaluations of $f$ per step versus one for Euler, but its dramatically better convergence rate makes it superior for any tolerance below about 1%. The default step size $h = 0.01$ yields roughly 8 digits of accuracy for well-behaved problems.

**Scalar vs. system dispatch.** The `solveODE` function accepts both `number` and `Float64Array` for the initial value, using a runtime type check to dispatch between scalar and vector code paths. The vector path allocates intermediate `Float64Array` buffers for the four RK4 stages ($k_1$ through $k_4$), reusing them across steps to avoid per-step allocation pressure.

**Numerical pitfalls.** Euler's method is unstable for the test equation $y' = \lambda y$ unless $|1 + h\lambda| < 1$; for stiff problems this forces impractically small $h$. RK4's stability region extends to $h\lambda \approx -2.78$ on the negative real axis. Neither method handles stiff systems well; users should monitor for step-size-dependent oscillations as a stiffness indicator. Exponentially growing solutions amplify local truncation errors; decreasing $h$ or switching to adaptive control is necessary for long integrations of unstable systems.

**Performance.** Each RK4 step costs $O(4n)$ for an $n$-dimensional system (four function evaluations of $O(n)$ each, plus vector additions). Total cost is $O(Nn)$ where $N = T/h$. The fixed step-size design avoids the overhead of error estimation and step rejection present in adaptive solvers.

**Testing.** Exponential decay ($y' = -\lambda y$) and the harmonic oscillator ($x'' + x = 0$) serve as primary test problems with known exact solutions. Convergence order is verified by halving $h$ and checking that the error ratio approaches $2$ (Euler) or $16$ (RK4). Conservation of energy in the harmonic oscillator detects systematic drift.

