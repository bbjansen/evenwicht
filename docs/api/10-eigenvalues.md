<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Eigenvalues & Eigenvectors — API Reference

This is the API reference for the TypeScript implementation of Eigenvalues & Eigenvectors. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/linear/eigen.ts` — power iteration and characteristic polynomial computation

### Data Representation

The `powerIteration` function takes a `Matrix` (from `src/linear/matrix.ts`) and returns an object containing the dominant eigenvalue as a `number` and the corresponding eigenvector as a `Float64Array`. The `characteristicPolynomial2x2` returns polynomial coefficients as a tuple.

### API Preview

```typescript
// src/linear/eigen.ts

/**
 * Approximate the dominant eigenvalue and eigenvector of A via power iteration.
 *
 * @param A - A square matrix (n x n), represented as a Matrix type.
 * @param opts - Optional configuration:
 *   - tolerance: convergence threshold for eigenvalue (default: 1e-10)
 *   - maxIterations: maximum number of iterations (default: 1000)
 * @returns An object { eigenvalue: number, eigenvector: Float64Array }.
 * @throws Error if A is not square.
 * @throws Error if the algorithm does not converge within maxIterations.
 */
function powerIteration(
    A: Matrix,
    opts?: { tolerance?: number; maxIterations?: number }
): { eigenvalue: number; eigenvector: Float64Array };

/**
 * Compute the characteristic polynomial of a 2x2 matrix.
 *
 * @param A - A 2x2 matrix.
 * @returns A tuple [a, b, c] representing the polynomial a*lambda^2 + b*lambda + c.
 *   For a 2x2 matrix, a = 1, b = -tr(A), c = det(A).
 * @throws Error if A is not 2x2.
 */
function characteristicPolynomial2x2(A: Matrix): [number, number, number];
```

### Error Handling

- `powerIteration` throws an `Error` if the input matrix is not square.
- `powerIteration` throws an `Error` if the algorithm does not converge within the maximum number of iterations.
- `characteristicPolynomial2x2` throws an `Error` if the input matrix is not $2 \times 2$.
- Default tolerance for power iteration is $10^{-10}$; default maximum iterations is 1000.

### Dependencies

- `src/linear/matrix.ts` — `Matrix` type and `matrixVectorProduct`
- `src/linear/vector.ts` — `norm`, `normalize` for eigenvector normalisation
- Used by: `src/dynamics/system.ts` (stability analysis), `src/applications/equilibrium.ts`, `src/graph/spectral.ts`

### Usage Examples

```typescript
import { matrix } from 'evenwicht/linear';
import { powerIteration, characteristicPolynomial2x2 } from 'evenwicht/linear';

// Find dominant eigenvalue of a 2x2 matrix
const A = matrix(2, 2, new Float64Array([2, 1, 1, 3]));
const result = powerIteration(A);
// result.eigenvalue ≈ 3.618 (golden ratio + 1)
// result.eigenvector ≈ [0.526, 0.851]

// Characteristic polynomial of a 2x2 matrix
const [a, b, c] = characteristicPolynomial2x2(A);
// lambda^2 - 5*lambda + 5 = 0
```

### Connections

This chapter is used by Chapter 18 (Difference Equations — stability of a discrete dynamical system $\mathbf{x}_{k+1} = A\mathbf{x}_k$ depends on whether $|\lambda| < 1$ for all eigenvalues), Chapter 19 (Ordinary Differential Equations — stability of $\dot{\mathbf{x}} = A\mathbf{x}$ depends on whether $\operatorname{Re}(\lambda) < 0$), Chapter 11 (Optimisation — a critical point is a local minimum if and only if all Hessian eigenvalues are positive), Chapter 17 (Regression — principal component analysis uses the eigenvectors of the covariance matrix, though PCA itself is out of scope) and Chapter 23 (Operator Algebra — eigenvalues of linear operators on function spaces).

- **Chapter 18 (Difference Equations)**: The discrete dynamical system $\mathbf{x}_{k+1} = A\mathbf{x}_k$ has the solution $\mathbf{x}_k = A^k\mathbf{x}_0$. If $A = PDP^{-1}$, then $\mathbf{x}_k = PD^kP^{-1}\mathbf{x}_0$; the long-term behaviour is determined by the eigenvalues. The system is stable (all solutions decay to $\mathbf{0}$) if and only if $|\lambda_i| < 1$ for every eigenvalue. If any $|\lambda_i| > 1$, solutions grow without bound. The eigenvalue criterion is the fundamental stability test for linear recurrences, including ARMA models in time series and the Solow growth model in economics.

- **Chapter 19 (Ordinary Differential Equations)**: The continuous system $\dot{\mathbf{x}} = A\mathbf{x}$ has the solution $\mathbf{x}(t) = e^{At}\mathbf{x}_0$. When $A = PDP^{-1}$, the solution decomposes as $\mathbf{x}(t) = \sum_i c_i e^{\lambda_i t}\mathbf{v}_i$. The system is asymptotically stable if and only if $\operatorname{Re}(\lambda_i) < 0$ for all eigenvalues. This criterion is the continuous-time analogue of the discrete stability condition and is the basis of Lyapunov's stability theory.

- **Chapter 11 (Optimisation)**: The second-order sufficient conditions for a local minimum of $f$ at a critical point $\mathbf{x}^*$ require the Hessian $H_f(\mathbf{x}^*)$ to be positive definite, which by the spectral theorem means all eigenvalues are positive. The eigenvalues of the Hessian also determine the convergence rate of gradient descent: the condition number $\kappa = \lambda_{\max}/\lambda_{\min}$ governs how many iterations are needed.

- **Chapter 17 (Regression)**: Principal component analysis (PCA) computes the eigenvectors of the covariance matrix $\Sigma = \frac{1}{n}X^TX$. The eigenvector corresponding to the largest eigenvalue is the direction of greatest variance in the data. The eigenvalues give the variance explained by each principal component. While PCA itself is out of scope for this chapter, the eigenvalue computation is the mathematical core.

- **Chapter 23 (Operator Algebra)**: The eigenvalue concept extends to linear operators on infinite-dimensional function spaces. The differential operator $D = d/dx$ has eigenfunction $e^{\lambda x}$ (since $De^{\lambda x} = \lambda e^{\lambda x}$), and the Sturm–Liouville eigenvalue problem is the infinite-dimensional analogue of $A\mathbf{v} = \lambda\mathbf{v}$.



### What Is Implemented vs. Documented Only

- [x] Power iteration (`powerIteration`)
- [x] Characteristic polynomial for 2x2 matrices (`characteristicPolynomial2x2`)
- [ ] Inverse iteration (deferred)
- [ ] Full QR algorithm for all eigenvalues (deferred)
- [ ] Singular value decomposition / SVD (deferred)
- [ ] Matrix exponential (deferred — documented in Definition 10.20)
- [ ] Eigenvalue computation for general $n \times n$ matrices via characteristic polynomial root-finding (deferred — numerically ill-advised for $n > 4$)

### Numerical Considerations

Eigenvalue computation is inherently sensitive to round-off, and the choice of algorithm determines whether this sensitivity is manageable or catastrophic. The two methods provided (direct formula for $2 \times 2$ and power iteration for general $n$) have very different numerical profiles.

**Characteristic polynomial instability.** For $2 \times 2$ matrices, the eigenvalues are the roots of $\lambda^2 - \operatorname{tr}(A)\lambda + \det(A) = 0$, computed via the quadratic formula. This is numerically stable for small matrices. For $n > 4$, computing the characteristic polynomial and finding its roots is numerically ill-advised. The Wilkinson polynomial is the classic cautionary example: a degree-20 polynomial with integer roots $1, 2, \ldots, 20$, where a perturbation of $2^{-23}$ in one coefficient moves a root by approximately $2.8 \times 10^{8}$. The condition number of a polynomial root $r$ with respect to the coefficient $a_k$ is

$$\kappa_k = \frac{|r|^k}{\left|p'(r)\right|}$$

which grows rapidly with degree. The library does not expose a general `characteristicPolynomial` function for this reason.

**Power iteration convergence rate.** Power iteration converges geometrically at a rate determined by the eigenvalue ratio $|\lambda_2 / \lambda_1|$ per step. If $|\lambda_2/\lambda_1| = 0.9$, then $k \approx \log(10^{-10}) / \log(0.9) \approx 219$ iterations are needed for 10-digit accuracy. If $|\lambda_2/\lambda_1| = 0.99$, convergence requires $k \approx 2{,}302$ iterations. When $|\lambda_1| = |\lambda_2|$ (e.g., eigenvalues $+3$ and $-3$, or complex conjugate pairs), the iterates oscillate without converging and the algorithm throws after exhausting `maxIterations`.

**Eigenvector normalisation and sign ambiguity.** The eigenvector is determined only up to a scalar multiple; normalisation to unit length removes the magnitude ambiguity but leaves a sign ambiguity ($\mathbf{v}$ and $-\mathbf{v}$ are both valid). Successive iterates can flip sign, so convergence is detected by comparing eigenvalue estimates (a scalar) rather than eigenvector norms. The eigenvalue estimate uses $\|\mathbf{w}\| = \|A\mathbf{v}_k\|$ which gives $|\lambda_1|$; the Rayleigh quotient $\mathbf{v}^T A \mathbf{v}$ would recover the sign and converge faster (quadratically vs. linearly) but is not used in the current implementation.

**Random initial vector and degenerate starts.** If the initial vector happens to be orthogonal to the dominant eigenvector $\mathbf{u}_1$, power iteration converges to a subdominant eigenvalue. In exact arithmetic this is a genuine failure mode. In floating-point arithmetic, round-off noise introduces a component along $\mathbf{u}_1$ of magnitude $\sim \varepsilon_{\text{mach}} \|\mathbf{v}_0\|$, which is amplified by the factor $|\lambda_1/\lambda_2|$ per step. After $\sim 50$ iterations (for typical eigenvalue ratios), this noise component dominates and convergence to $\lambda_1$ resumes. The algorithm is therefore robust in practice, though convergence may be delayed.

### Implementation Context

The eigenvalue module provides two methods (a direct formula for $2 \times 2$ matrices and power iteration for general $n$), reflecting a deliberate scope limitation for a library that does not yet ship the QR algorithm.

**Complexity.** Each power iteration step costs $O(n^2)$ for the matrix-vector product. Total cost is $O(n^2 k)$ where $k$ is the iteration count, typically well under the 1000-iteration default for well-separated eigenvalues.

**Testing strategy.** For $2 \times 2$: compare `characteristicPolynomial2x2` roots against hand-computed eigenvalues. For power iteration: use a diagonal matrix (eigenvalues known exactly) and verify convergence to the largest. Test non-convergence by constructing a matrix with $|\lambda_1| = |\lambda_2|$ and confirming the error is thrown.

