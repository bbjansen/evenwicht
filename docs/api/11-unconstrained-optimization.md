<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Unconstrained Optimisation — API Reference

This is the API reference for the TypeScript implementation of Unconstrained Optimisation. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/optimization/unconstrained.ts` — gradient descent and Newton's method

### Data Representation

Input points and gradients are `Float64Array` vectors. The Hessian is a `Matrix` object from `src/linear/matrix.ts`. Results are returned as `OptimizationResult` objects containing the minimiser, iteration count and convergence flag.

### Internal Dependencies

- `newtonsMethod` calls `solve()` from `src/linear/solve.ts` to solve the linear system $H_f(\mathbf{x}_k)\mathbf{d} = -\nabla f(\mathbf{x}_k)$ at each iteration, rather than computing an explicit matrix inverse.

### API Preview

```typescript
// src/optimization/unconstrained.ts

/**
 * Minimize a differentiable function using gradient descent.
 *
 * @param gradient - A function that computes the gradient of the objective
 *   at a given point. Accepts a Float64Array of length n and returns a
 *   Float64Array of length n.
 * @param x0 - Initial point (Float64Array of length n).
 * @param opts - Optional configuration:
 *   - stepSize: the step size alpha (default: 0.01)
 *   - tolerance: convergence threshold for gradient norm (default: 1e-8)
 *   - maxIterations: maximum number of iterations (default: 10000)
 * @returns An object { x: Float64Array, iterations: number, converged: boolean }.
 *   x is the approximate minimizer, iterations is the number of steps taken,
 *   and converged indicates whether the gradient norm fell below tolerance.
 * @throws Error if x0 has length 0.
 */
function gradientDescent(
    gradient: (x: Float64Array) => Float64Array,
    x0: Float64Array,
    opts?: { stepSize?: number; tolerance?: number; maxIterations?: number }
): { x: Float64Array; iterations: number; converged: boolean };

/**
 * Minimize a twice-differentiable function using Newton's method.
 *
 * @param gradient - A function that computes the gradient of the objective
 *   at a given point. Accepts a Float64Array of length n and returns a
 *   Float64Array of length n.
 * @param hessian - A function that computes the Hessian matrix of the
 *   objective at a given point. Accepts a Float64Array of length n and
 *   returns a Matrix (n x n).
 * @param x0 - Initial point (Float64Array of length n).
 * @param opts - Optional configuration:
 *   - tolerance: convergence threshold for gradient norm (default: 1e-10)
 *   - maxIterations: maximum number of iterations (default: 100)
 * @returns An object { x: Float64Array, iterations: number, converged: boolean }.
 *   x is the approximate minimizer, iterations is the number of steps taken,
 *   and converged indicates whether the gradient norm fell below tolerance.
 * @throws Error if x0 has length 0.
 * @throws Error if the Hessian is singular at any iteration (the linear
 *   system H * d = -g has no solution).
 */
function newtonsMethod(
    gradient: (x: Float64Array) => Float64Array,
    hessian: (x: Float64Array) => Matrix,
    x0: Float64Array,
    opts?: { tolerance?: number; maxIterations?: number }
): { x: Float64Array; iterations: number; converged: boolean };
```

### Error Handling

- Both functions throw an `Error` if `x0` has length 0.
- `newtonsMethod` throws if the Hessian is singular at any iteration (i.e., the linear system cannot be solved).
- If the maximum number of iterations is reached without convergence, the functions return with `converged: false` rather than throwing. This allows the caller to inspect the best iterate found so far.
- Default tolerances: $10^{-8}$ for gradient descent, $10^{-10}$ for Newton's method (reflecting Newton's faster convergence).
- Default maximum iterations: 10000 for gradient descent, 100 for Newton's method.

### Dependencies

- `src/linear/solve.ts` — `solve()` for the Newton step linear system $H\mathbf{d} = -\nabla f$
- `src/linear/vector.ts` — `norm` for convergence checking

### Usage Examples

```typescript
import { gradientDescent, newtonsMethod } from 'evenwicht/optimization';
import { matrix } from 'evenwicht/linear';

// Minimize f(x,y) = x^2 + y^2 via gradient descent
const grad = (x: Float64Array) => new Float64Array([2 * x[0], 2 * x[1]]);
const result = gradientDescent(grad, new Float64Array([5, 3]), { stepSize: 0.1 });
// result.x ≈ [0, 0], result.converged === true

// Minimize Rosenbrock via Newton's method
const rosenbrock_grad = (x: Float64Array) => new Float64Array([
  -400 * x[0] * (x[1] - x[0] * x[0]) + 2 * (x[0] - 1),
  200 * (x[1] - x[0] * x[0]),
]);
const rosenbrock_hess = (x: Float64Array) => matrix(2, 2, new Float64Array([
  1200 * x[0] * x[0] - 400 * x[1] + 2, -400 * x[0],
  -400 * x[0], 200,
]));
const nr = newtonsMethod(rosenbrock_grad, rosenbrock_hess, new Float64Array([0, 0]));
// nr.x ≈ [1, 1]
```

### Connections

This chapter is used by Chapter 12 (Constrained Optimisation — Lagrange multipliers extend the unconstrained first-order conditions by incorporating constraints), Chapter 17 (Regression — ordinary least squares minimises the sum of squared errors, a convex unconstrained problem whose normal equations arise from setting $\nabla f = \mathbf{0}$) and Chapter 19 (Ordinary Differential Equations — gradient flow $\dot{\mathbf{x}} = -\nabla f(\mathbf{x})$ is the continuous-time limit of gradient descent). It builds on Chapter 4 (single-variable derivatives), Chapter 7 (gradient, Hessian), Chapter 8 (vectors), Chapter 9 (matrices, linear systems) and Chapter 10 (eigenvalues for definiteness tests).

- **Chapter 4 (Differential Calculus)**: The first-order necessary condition $f'(x^*) = 0$ is the starting point of optimisation theory. Every tool in this chapter (the second derivative test, gradient descent, Newton's method) rests on the ability to compute derivatives. Newton's method for optimisation is Newton's root-finding method (Chapter 4, Algorithm 5.2) applied to the equation $f'(x) = 0$.

- **Chapter 7 (Multivariate Calculus)**: The gradient $\nabla f$ and Hessian $H_f$ are the multivariate generalisations of $f'$ and $f''$ that power multivariate optimisation. The directional derivative $D_\mathbf{u}f = \nabla f \cdot \mathbf{u}$ explains why the negative gradient is the direction of steepest descent. The multivariate Taylor expansion $f(\mathbf{x}^* + \mathbf{h}) \approx f(\mathbf{x}^*) + \frac{1}{2}\mathbf{h}^TH\mathbf{h}$ is the foundation of the second-order sufficient conditions and the derivation of Newton's method.

- **Chapter 10 (Eigenvalues)**: Positive definiteness of the Hessian, the key condition for a local minimum, is equivalent to all eigenvalues being positive (Theorem 11.7). The eigenvalues of the Hessian determine the curvature of $f$ along the principal directions and the condition number $\kappa = \lambda_{\max}/\lambda_{\min}$ governs the convergence rate of gradient descent. Ill-conditioned Hessians (large $\kappa$) produce elongated, narrow level curves that cause gradient descent to zigzag, converging slowly.

- **Chapter 12 (Constrained Optimisation)**: When the domain of optimisation is restricted by equality or inequality constraints, the unconstrained first-order condition $\nabla f = \mathbf{0}$ is replaced by the Lagrangian conditions. The theory of constrained optimisation builds directly on the unconstrained theory: the Lagrangian function $L(\mathbf{x}, \boldsymbol{\lambda}) = f(\mathbf{x}) + \boldsymbol{\lambda}^T\mathbf{g}(\mathbf{x})$ is optimised without constraints in the enlarged $(\mathbf{x}, \boldsymbol{\lambda})$ space.

- **Chapter 17 (Regression)**: Ordinary least squares regression minimises the sum of squared errors $\text{SSE}(\boldsymbol{\beta}) = \|\mathbf{y} - X\boldsymbol{\beta}\|^2$, a convex quadratic function. Setting $\nabla \text{SSE} = \mathbf{0}$ yields the normal equations $X^TX\boldsymbol{\beta} = X^T\mathbf{y}$, which is an application of Theorem 11.5. The Hessian is $2X^TX \succeq 0$, confirming convexity and guaranteeing that the least squares solution is a global minimum.



### What Is Implemented vs. Documented Only

- [x] Gradient descent with fixed step size (`gradientDescent`)
- [x] Newton's method for optimisation (`newtonsMethod`)
- [ ] Line search (Armijo / Wolfe conditions) — documented in Remark 3.20, not implemented
- [ ] Modified Newton's method (Hessian regularisation) — documented in Section 6, not implemented
- [ ] Quasi-Newton methods (BFGS, L-BFGS) — documented in Remark 3.19, not implemented
- [ ] Stochastic gradient descent (SGD) — mentioned in Section 1, not implemented

### Implementation Context

The two optimisers, gradient descent and Newton's method, represent opposite ends of the cost-vs-convergence trade-off. They are often used together in practice: gradient descent for an approximate solution, Newton to polish it.

**Gradient descent step size.** The fixed step size $\alpha$ controls stability: for a quadratic $f(x) = \frac{1}{2}Lx^2$, the iteration diverges when $\alpha > 2/L$. Since the Lipschitz constant $L$ is rarely known, the caller must choose $\alpha$ conservatively. The library does not implement line search or adaptive step sizes (Barzilai–Borwein, Armijo backtracking); these are deferred to a future version. Convergence is linear with rate $\rho = (\kappa - 1)/(\kappa + 1)$, where $\kappa$ is the condition number of the Hessian at the minimum.

**Newton's method and the Hessian.** Each Newton step solves $H \mathbf{d} = -\nabla f$ via Gaussian elimination ($O(n^3)$), producing quadratic convergence near a minimum. The Hessian must be positive definite for the Newton direction to be a descent direction; if $H$ is indefinite (which happens far from the minimum), the step may ascend. A modified Newton approach ($H + \mu I$ with Tikhonov regularisation) would fix this but is not yet implemented.

**Convergence detection.** Both methods use $\|\nabla f\| < \varepsilon$ as the stopping criterion, directly testing the first-order necessary condition. Tolerances below $\sqrt{\varepsilon_{\text{mach}}} \approx 10^{-8}$ risk false non-convergence because finite-difference or floating-point noise in the gradient exceeds the threshold. Default tolerances are $10^{-8}$ (gradient descent) and $10^{-10}$ (Newton), reflecting Newton's higher per-step accuracy.

**Starting point sensitivity.** For nonconvex $f$, different initial points converge to different local minima. Multi-start strategies (not built in) are the standard workaround. For convex $f$, any starting point reaches the unique global minimum.

**Testing strategy.** Minimise $f(x) = x^2 - 4x + 5$ (minimum at $x = 2$) and the Rosenbrock function $(1-x)^2 + 100(y - x^2)^2$ (minimum at $(1, 1)$). Verify Newton converges in fewer than 10 iterations on quadratics. Confirm gradient descent diverges when $\alpha$ exceeds $2/L$ on a known quadratic.

