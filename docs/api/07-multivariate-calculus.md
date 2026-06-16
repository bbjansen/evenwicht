<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Multivariate Calculus — API Reference

This is the API reference for the TypeScript implementation of Multivariate Calculus. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

The multivariate calculus operations in Evenwicht are organised as follows:

- `src/expr/partial.ts` — symbolic `partialDerivative`, `gradient`, `hessian`
- `src/numeric/gradient.ts` — numerical `numericalGradient`, `numericalHessian`

The symbolic functions reuse `differentiate()` from Chapter 4, which already returns 0 for any variable node whose name does not match the target; precisely the "treat other variables as constants" rule.

### Data Representation

Symbolic multivariate operations use the `Expr` type and produce `Expr[]` (gradient) or `Expr[][]` (Hessian). Numerical operations use `number[]` for points and `number[][]` for Hessian matrices. The numerical gradient and Hessian use central finite differences.

### API Preview

```typescript
// src/expr/partial.ts

/**
 * Compute the partial derivative of expr with respect to variable.
 * Equivalent to differentiate(expr, variable).
 */
function partialDerivative(expr: Expr, variable: string): Expr;

/**
 * Compute the gradient: an array of partial derivatives,
 * one per variable in the given list.
 */
function gradient(expr: Expr, variables: string[]): Expr[];

/**
 * Compute the Hessian: a 2D array of second partial derivatives.
 * hessian(expr, vars)[i][j] = d^2 expr / (d vars[i] d vars[j]).
 * The result is symmetric for C^2 expressions.
 */
function hessian(expr: Expr, variables: string[]): Expr[][];
```

```typescript
// src/numeric/gradient.ts

/**
 * Approximate the gradient of f at point a using central differences.
 * @param f - A function from number[] to number.
 * @param a - The point at which to evaluate the gradient.
 * @param h - Step size (default: 1e-5).
 */
function numericalGradient(
    f: (x: number[]) => number,
    a: number[],
    h?: number
): number[];

/**
 * Approximate the Hessian of f at point a using central differences.
 * @param f - A function from number[] to number.
 * @param a - The point at which to evaluate the Hessian.
 * @param h - Step size (default: 1e-4).
 */
function numericalHessian(
    f: (x: number[]) => number,
    a: number[],
    h?: number
): number[][];
```

### Error Handling

- `partialDerivative` with a variable that does not appear in the expression returns the constant expression 0 (the derivative of a constant is zero).
- `gradient` with an empty variable list returns an empty array.
- `hessian` with an empty variable list returns an empty 2D array.
- `numericalGradient` and `numericalHessian` propagate `NaN` if the function returns `NaN` at any evaluation point.
- Step sizes of zero or negative values throw an `Error`.

### Dependencies

- `src/expr/differentiate.ts` — underlying symbolic differentiation engine
- `src/expr/simplify.ts` — simplification of derivative expressions

### Usage Examples

```typescript
import { variable, add, mul, pow, constant } from 'evenwicht/expr';
import { gradient, hessian } from 'evenwicht/expr';
import { numericalGradient } from 'evenwicht/numeric';
import { evaluate } from 'evenwicht/expr';

// Symbolic gradient of f(x,y) = x^2 + x*y
const x = variable('x'), y = variable('y');
const f = add(pow(x, constant(2)), mul(x, y));
const grad = gradient(f, ['x', 'y']);
// grad[0] = 2x + y, grad[1] = x
evaluate(grad[0], { x: 1, y: 2 });  // 4
evaluate(grad[1], { x: 1, y: 2 });  // 1

// Numerical gradient of g(x,y) = x^2 + y^2 at (1,1)
const g = (pt: number[]) => pt[0] ** 2 + pt[1] ** 2;
numericalGradient(g, [1, 1]);  // ≈ [2, 2]
```

### Connections

This chapter is used by Chapter 11 (Optimisation — gradient descent, Newton's method, second-order conditions via the Hessian), Chapter 12 (Lagrange Multipliers — constrained optimisation using gradient conditions) and Chapter 17 (Regression — the normal equations arise from setting the gradient of the sum of squared errors to zero). The Jacobian matrix introduced here reappears in Chapter 23 (Operator Algebra) and in change-of-variable formulas throughout probability theory (Chapter 13).

- **Chapter 11 (Optimisation)**: The first-order necessary condition for a local minimum of $f$ is $\nabla f(\mathbf{x}^*) = \mathbf{0}$ (the critical point condition). The second-order sufficient condition checks the Hessian: if $H_f(\mathbf{x}^*)$ is positive definite, $\mathbf{x}^*$ is a local minimum. Gradient descent uses $\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha\,\nabla f(\mathbf{x}_k)$; Newton's method uses $\mathbf{x}_{k+1} = \mathbf{x}_k - H_f(\mathbf{x}_k)^{-1}\nabla f(\mathbf{x}_k)$. Both algorithms are direct applications of the gradient and Hessian.

- **Chapter 12 (Lagrange Multipliers)**: To minimise $f(\mathbf{x})$ subject to a constraint $g(\mathbf{x}) = 0$, the Lagrange condition requires $\nabla f = \lambda \nabla g$ for some scalar $\lambda$. This is a system of equations involving the gradients of $f$ and $g$. The geometric interpretation (Definition 7.11) explains why: at a constrained optimum, the gradient of $f$ must be perpendicular to the constraint surface and $\nabla g$ is already perpendicular to it.

- **Chapter 17 (Regression)**: Ordinary least squares minimises the sum of squared errors $S(\beta) = \sum_{i=1}^{N}(y_i - \mathbf{x}_i^T\beta)^2$. Setting $\nabla_\beta S = \mathbf{0}$ yields the normal equations $X^T X \beta = X^T \mathbf{y}$. The Hessian of $S$ with respect to $\beta$ is $2X^T X$, which is positive semidefinite, confirming that the normal equations give a minimum (not a maximum or saddle point).



### What Is Implemented vs. Documented Only

- [x] Symbolic partial derivative (via `differentiate`)
- [x] Symbolic gradient
- [x] Symbolic Hessian
- [x] Numerical gradient (central differences)
- [x] Numerical Hessian (central differences)
- [ ] Symbolic Jacobian for vector-valued functions (deferred)
- [ ] Automatic differentiation / reverse-mode AD (deferred — would enable efficient gradients for large expression graphs)
### Numerical Considerations

Multivariate numerical differentiation extends the step-size dilemma from Chapter 4 to higher dimensions, with the added complication that the optimal step size differs between first and second derivatives, and the computational cost scales quadratically with dimension.

**Optimal step sizes for gradient and Hessian.** The numerical gradient uses central differences in each coordinate direction. The optimal step size for first derivatives is

$$h_{\text{grad}} \approx \varepsilon_{\text{mach}}^{1/3} \approx 6 \times 10^{-6}$$

as in the univariate case (Chapter 4). The numerical Hessian uses second-order central differences, where the round-off error is amplified by an additional factor of $1/h$ relative to first derivatives. The optimal step for second derivatives is therefore larger:

$$h_{\text{Hess}} \approx \varepsilon_{\text{mach}}^{1/4} \approx 1.2 \times 10^{-4}$$

Using the smaller gradient step for Hessian entries introduces severe round-off noise. The library defaults reflect this distinction: $h = 10^{-5}$ for `numericalGradient` and $h = 10^{-4}$ for `numericalHessian`. At these step sizes, the gradient achieves roughly 10 correct digits and the Hessian achieves roughly 8.

**Computational cost scaling.** The numerical gradient requires $2n$ function evaluations ($n$ coordinate directions, two evaluations each for central differences). The numerical Hessian requires $O(n^2)$ evaluations: one base evaluation, $2n$ for the diagonal, and 4 per off-diagonal pair, giving $2n^2 + 2n + 1$ total. For $n = 100$ variables, this is roughly $20{,}000$ evaluations for the gradient and $20{,}000$ for the Hessian. When $n$ reaches hundreds or thousands, the Hessian computation becomes prohibitively expensive, motivating Hessian-free optimisation methods (L-BFGS, conjugate gradient) that require only $O(n)$ gradient evaluations per iteration (Chapter 11).

**Symbolic vs. numerical accuracy trade-off.** The symbolic gradient and Hessian are exact up to evaluation-time rounding, but their cost depends on expression tree size, which can grow through expression swell. The symbolic Hessian exploits Clairaut–Schwarz symmetry ($\partial^2 f / \partial x_i \partial x_j = \partial^2 f / \partial x_j \partial x_i$) to compute only $n(n+1)/2$ entries, halving both computation and simplification calls. The numerical path is $O(n)$ or $O(n^2)$ regardless of expression complexity, making it the pragmatic choice for black-box functions. When both paths are available, comparing symbolic and numerical gradients provides a robust correctness check: agreement to $\sim 10$ digits confirms both implementations.

### Implementation Context

The module offers parallel symbolic and numerical paths for gradient and Hessian computation, each with different accuracy/cost trade-offs.

**Symbolic partial derivative reuse.** `partialDerivative` delegates directly to the single-variable `differentiate` from Chapter 4; variables other than the target are constants whose derivative is zero. This means expression swell and the need for post-differentiation `simplify` carry over identically. The symbolic gradient costs $O(n \cdot s)$ and the Hessian $O(n^2 \cdot s')$ where $s, s'$ are the expression tree sizes before and after one differentiation pass.

**Testing strategy.** Symbolic gradient of $x^2 + xy + y^2$ should yield $[2x + y, x + 2y]$; evaluate both at $(1, 1)$ and compare. Numerical gradient of the same function: verify agreement with symbolic values to $\approx 10$ digits. Hessian: check symmetry numerically and compare diagonal entries against the known constant second derivatives.

