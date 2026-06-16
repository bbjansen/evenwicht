<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Constrained Optimisation & Linear Programming — API Reference

This is the API reference for the TypeScript implementation of Constrained Optimisation & Linear Programming. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/optimization/lagrange.ts` — Lagrange multiplier solver (numerical, using Newton's method on the KKT system)
- `src/optimization/linprog.ts` — simplex method for linear programming

### Data Representation

The `lagrange` solver uses plain `number[]` for decision variables and multipliers. The `simplex` solver uses `Float64Array` for the objective and RHS vectors and a `Matrix` for the constraint matrix. Results include optimal values, multipliers (Lagrange), or status strings (simplex).

### API Preview

```typescript
// src/optimization/lagrange.ts

/**
 * Solve a constrained optimization problem using the method of Lagrange
 * multipliers. The solver forms the KKT system and applies Newton's method.
 *
 * @param objective - The objective function f(x1, x2, ..., xn).
 * @param constraints - Array of constraint functions g_i(x1, ..., xn).
 *   Each constraint is treated as g_i(x) = 0.
 * @param x0 - Initial guess for the decision variables (length n).
 * @param opts - Optional configuration:
 *   - tolerance: convergence threshold for the KKT residual (default: 1e-10)
 *   - maxIterations: maximum Newton iterations (default: 100)
 * @returns An object { x, multipliers, value }:
 *   - x: the optimal point (number[])
 *   - multipliers: the Lagrange multipliers (number[])
 *   - value: the objective value f(x*) (number)
 * @throws Error if Newton's method does not converge within maxIterations.
 */
function lagrange(
    objective: (...args: number[]) => number,
    constraints: ((...args: number[]) => number)[],
    x0: number[],
    opts?: { tolerance?: number; maxIterations?: number }
): { x: number[]; multipliers: number[]; value: number };
```

```typescript
// src/optimization/linprog.ts

/**
 * Solve a linear program in standard form using the simplex method:
 *   maximize c'x subject to Ax <= b, x >= 0.
 *
 * @param c - Objective coefficients (Float64Array of length n).
 * @param A - Constraint matrix (Matrix of size m x n).
 * @param b - Right-hand side of constraints (Float64Array of length m).
 *   All entries of b must be nonnegative; use two-phase method internally otherwise.
 * @param opts - Optional configuration:
 *   - tolerance: numerical tolerance for pivoting and optimality (default: 1e-10)
 * @returns An object { x, value, status }:
 *   - x: the optimal decision variables (Float64Array of length n)
 *   - value: the optimal objective value (number)
 *   - status: 'optimal' | 'unbounded' | 'infeasible'
 */
function simplex(
    c: Float64Array,
    A: Matrix,
    b: Float64Array,
    opts?: { tolerance?: number }
): { x: Float64Array; value: number; status: 'optimal' | 'unbounded' | 'infeasible' };
```

### Error Handling

- `lagrange` throws an `Error` if Newton's method does not converge within the specified maximum iterations. The error message includes the final residual norm.
- `simplex` does *not* throw for unbounded or infeasible problems. Instead, it returns the appropriate `status` string, allowing the caller to handle these cases programmatically. This design follows the convention of established LP solvers (GLPK, HiGHS).
- Both functions validate inputs: `lagrange` checks that `x0` has the correct dimension; `simplex` checks that the dimensions of `c`, `A` and `b` are consistent.
- Default tolerance for both solvers is $10^{-10}$.

### Dependencies

- `src/numeric/gradient.ts` — numerical gradient and Hessian for the KKT system Jacobian
- `src/linear/solve.ts` — linear system solve for Newton steps in Lagrange solver
- `src/linear/matrix.ts` — `Matrix` type for constraint matrices

### Usage Examples

```typescript
import { lagrange } from 'evenwicht/optimization';
import { simplex } from 'evenwicht/optimization';
import { matrix } from 'evenwicht/linear';

// Minimize x^2 + y^2 subject to x + y = 1
const result = lagrange(
  (x, y) => x * x + y * y,
  [(x, y) => x + y - 1],
  [0.5, 0.5],
);
// result.x ≈ [0.5, 0.5], result.value ≈ 0.5

// Linear program: maximize 3x + 2y subject to x + y <= 4, x + 3y <= 6
const lp = simplex(
  new Float64Array([3, 2]),
  matrix(2, 2, new Float64Array([1, 1, 1, 3])),
  new Float64Array([4, 6]),
);
// lp.value = 12, lp.x ≈ [4, 0], lp.status === 'optimal'
```

### Connections

This chapter is used by Chapter 17 (Regression — constrained estimation, restricted least squares, hypothesis testing as constrained optimisation). The Lagrange multiplier method extends the unconstrained theory of Chapter 11 to problems with side conditions. The LP duality theory connects to game theory (minimax theorems via von Neumann) and to the broader framework of convex optimisation. Shadow prices and the envelope theorem are foundational tools in microeconomic analysis, operations research and resource allocation.

- **Chapter 11 (Unconstrained Optimisation)**: The Lagrange multiplier method is the constrained extension of the first-order and second-order conditions from Chapter 11. In unconstrained optimisation, one sets $\nabla f = \mathbf{0}$; in constrained optimisation, the condition becomes $\nabla f = -\sum \lambda_i \nabla g_i$ — the gradient of $f$ need not be zero, but must be a linear combination of the constraint gradients. The bordered Hessian extends the Hessian test to the constrained setting. Newton's method for solving the Lagrange system is the same Newton's method used for unconstrained minimisation (Chapter 11), applied to the augmented KKT system.

- **Chapter 17 (Regression)**: Restricted least squares — minimising $\|\mathbf{y} - X\boldsymbol{\beta}\|^2$ subject to $R\boldsymbol{\beta} = \mathbf{r}$ — is a direct application of the Lagrange multiplier method with a quadratic objective and linear constraints. The resulting estimator is $\hat{\boldsymbol{\beta}}_R = \hat{\boldsymbol{\beta}} - (X^TX)^{-1}R^T[R(X^TX)^{-1}R^T]^{-1}(R\hat{\boldsymbol{\beta}} - \mathbf{r})$, and the Lagrange multiplier is used to construct the $F$-test for the hypothesis $R\boldsymbol{\beta} = \mathbf{r}$.



### What Is Implemented vs. Documented Only

- [x] Lagrange multiplier solver via Newton's method on the KKT system (`lagrange`)
- [x] Simplex method in tableau form (`simplex`)
- [ ] Two-phase simplex for problems with negative $b_i$ entries (deferred)
- [ ] Revised simplex method (deferred; more efficient for large sparse problems)
- [ ] Interior point method (deferred)
- [ ] Inequality-constrained optimisation / KKT conditions (deferred)

### Implementation Context

The two solvers address fundamentally different problem classes: nonlinear equality constraints (Lagrange) and linear programmes (simplex).

**Lagrange multiplier solver via Newton on the KKT system.** The Lagrange conditions form $n + m$ nonlinear equations in $n$ decision variables and $m$ multipliers. The solver applies Newton's method to this combined system, requiring the $(n+m) \times (n+m)$ Jacobian at each step at a cost of $O((n+m)^3)$. Gradients and the Jacobian are computed via numerical finite differences from Chapter 7. Convergence is quadratic near a solution but depends heavily on the initial guess; if constraint gradients are nearly parallel (degenerate LICQ), the Jacobian is ill-conditioned and multiplier estimates become unreliable.

**Multiple stationary points.** The KKT conditions are necessary but not sufficient. The solver finds one stationary point per run; the caller should use multiple initial guesses to explore additional candidates and classify them via the bordered Hessian.

**Simplex method in tableau form.** The tableau representation operates on an $(m+1) \times (n+m+1)$ augmented matrix. Each pivot step costs $O(mn)$ arithmetic. The worst-case pivot count is exponential ($\binom{n+m}{m}$) but the average is $O(m)$, giving typical total cost of $O(m^2 n)$. Status is returned as a string (`'optimal'`, `'unbounded'`, `'infeasible'`) rather than throwing, following the convention of production LP solvers.

**Degeneracy and cycling.** Degenerate basic feasible solutions (basic variables at zero) cause zero-length pivot steps. In rare cases this leads to cycling. Bland's rule (always choosing the lowest-indexed eligible entering/leaving variable) is the simplest anti-cycling guarantee and should be implemented if cycling is observed in practice.

**Numerical stability.** Pivoting on a very small element amplifies round-off. Practical mitigations include pre-scaling the constraint matrix so entries are of comparable magnitude and monitoring pivot magnitudes. Feasibility tolerance (default $10^{-10}$) accommodates accumulated rounding -- a constraint violated by less than this threshold is treated as satisfied.

**Testing strategy.** Lagrange: maximise $xy$ subject to $x + y = 10$ (known optimum at $(5, 5)$). Simplex: solve the classic diet problem and compare against a known optimal. Verify that unbounded and infeasible LPs return the correct status strings rather than throwing.

