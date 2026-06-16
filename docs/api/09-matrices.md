<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Matrices & Linear Transformations — API Reference

This is the API reference for the TypeScript implementation of Matrices & Linear Transformations. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

The matrix operations in Evenwicht are organised across the following modules:

- `src/linear/matrix.ts` — the `Matrix` type, matrix construction, addition, scalar multiplication, multiplication, transpose, identity and zero matrices.
- `src/linear/solve.ts` — Gaussian elimination with partial pivoting, back-substitution.
- `src/linear/determinant.ts` — determinant computation via row reduction.
- `src/linear/inverse.ts` — matrix inverse via Gauss–Jordan elimination.

### Data Representation

```typescript
interface Matrix {
    rows: number;
    cols: number;
    data: Float64Array;  // row-major: entry (i,j) at data[i * cols + j]
}
```

Row-major layout with `Float64Array` ensures contiguous storage and efficient cache usage for row-oriented operations.

### API Preview

```typescript
// src/linear/matrix.ts

/** Create a matrix from dimensions and a Float64Array of row-major data. */
function matrix(rows: number, cols: number, data: Float64Array): Matrix;

/** Add two matrices of the same dimensions. */
function matrixAdd(A: Matrix, B: Matrix): Matrix;

/** Multiply every entry of A by the scalar c. */
function matrixScale(c: number, A: Matrix): Matrix;

/** Multiply A (m x n) by B (n x p) to produce an m x p matrix. */
function matrixMultiply(A: Matrix, B: Matrix): Matrix;

/** Transpose A: swap rows and columns. */
function transpose(A: Matrix): Matrix;

/** Return the n x n identity matrix. */
function identity(n: number): Matrix;
```

```typescript
// src/linear/solve.ts

/**
 * Solve the system Ax = b using Gaussian elimination with partial pivoting.
 * Throws if A is singular or the system has no unique solution.
 */
function solve(A: Matrix, b: Float64Array): Float64Array;

/** Compute the matrix-vector product Av. */
function matrixVectorProduct(A: Matrix, v: Float64Array): Float64Array;
```

```typescript
// src/linear/determinant.ts

/** Compute the determinant of a square matrix via row reduction. O(n^3). */
function determinant(A: Matrix): number;
```

```typescript
// src/linear/inverse.ts

/** Compute the inverse of a square matrix via Gauss–Jordan elimination.
 *  Throws if the matrix is singular. */
function inverse(A: Matrix): Matrix;
```

### Error Handling

- `matrixAdd` throws if $A$ and $B$ have different dimensions.
- `matrixMultiply` throws if the number of columns of $A$ does not equal the number of rows of $B$.
- `matrixVectorProduct` throws if the vector length does not equal the number of columns of $A$.
- `determinant` throws if the matrix is not square.
- `inverse` throws if the matrix is not square or is singular ($\det(A) = 0$).
- `solve` throws if $A$ is not square or is singular (no unique solution).

### Dependencies

- `src/linear/vector.ts` — vector operations used in matrix-vector products
- Used by: `src/optimization/`, `src/stats/regression.ts`, `src/linear/eigen.ts`

### Usage Examples

```typescript
import { matrix, matrixMultiply, transpose, identity, solve, determinant, inverse } from 'evenwicht/linear';

// Create a 2x2 matrix
const A = matrix(2, 2, new Float64Array([1, 2, 3, 4]));

// Matrix operations
const At = transpose(A);
const I = identity(2);
const det = determinant(A);  // -2
const Ainv = inverse(A);

// Solve Ax = b
const b = new Float64Array([5, 11]);
const x = solve(A, b);  // x = [1, 2]
```

### Connections

This chapter is used by Chapter 10 (Eigenvalues — the characteristic polynomial $\det(A - \lambda I) = 0$ requires both determinants and matrix arithmetic), Chapter 12 (Constrained Optimisation — the simplex method operates on augmented matrices via row operations), Chapter 17 (Regression — the ordinary least squares estimator is $\hat{\boldsymbol{\beta}} = (X^T X)^{-1} X^T \mathbf{y}$) and Chapter 23 (Operator Algebra — matrices are the canonical representation of linear operators on finite-dimensional spaces). The rank and null space concepts introduced here reappear throughout the linear algebra chapters.

- **Chapter 8 (Vectors)**: Matrices act on vectors via the matrix-vector product $A\mathbf{x}$, which computes a linear combination of the columns of $A$ with the entries of $\mathbf{x}$ as coefficients. The dot product from Chapter 8 appears as the basic operation in matrix multiplication: each entry $(AB)_{ij}$ is a dot product of a row of $A$ and a column of $B$.

- **Chapter 10 (Eigenvalues)**: The eigenvalues of a matrix $A$ are the roots of the characteristic polynomial $\det(A - \lambda I) = 0$. Computing this polynomial requires both matrix subtraction and the determinant. The eigenvectors are the nonzero solutions of $(A - \lambda I)\mathbf{x} = \mathbf{0}$, a homogeneous linear system solved by Gaussian elimination. The null space of $A - \lambda I$ is the eigenspace.

- **Chapter 12 (Constrained Optimisation)**: Linear programming solves optimisation problems of the form $\max\,\mathbf{c}^T\mathbf{x}$ subject to $A\mathbf{x} \leq \mathbf{b}$. The simplex method operates directly on the augmented matrix $[A \mid \mathbf{b}]$ using pivot operations that are row reduction steps. The LP feasibility and optimality conditions are expressed in terms of the rank of constraint matrices.

- **Chapter 17 (Regression)**: The ordinary least squares estimator is $\hat{\boldsymbol{\beta}} = (X^T X)^{-1} X^T \mathbf{y}$. This formula involves matrix transposition, matrix multiplication and matrix inversion. The matrix $X^T X$ is the Gram matrix of the design matrix; its condition number determines the numerical reliability of the regression. When $X^T X$ is nearly singular (multicollinearity), the estimates are unreliable.

- **Chapter 23 (Operator Algebra)**: A matrix $A \in \mathbb{R}^{m \times n}$ is the finite-dimensional representation of a linear operator. The algebra of matrices (addition, multiplication, inversion) is the concrete realisation of the abstract algebra of linear operators. Determinants, traces and eigenvalues are operator invariants; they do not depend on the choice of basis.



### What Is Implemented vs. Documented Only

- [x] Matrix type with `Float64Array` storage
- [x] Matrix addition, scalar multiplication
- [x] Matrix multiplication ($O(n^3)$ triple loop)
- [x] Transpose
- [x] Identity and zero matrix construction
- [x] Gaussian elimination with partial pivoting
- [x] Back-substitution
- [x] Determinant via row reduction
- [x] Matrix inverse via Gauss–Jordan
- [x] Matrix-vector product
- [ ] LU decomposition (deferred — would allow efficient re-use of factorisation for multiple right-hand sides)
- [ ] QR decomposition (deferred — more numerically stable for least-squares problems)
- [ ] Strassen's algorithm (deferred — only advantageous for large matrices)
- [ ] Sparse matrix support (deferred)
### Numerical Considerations

Matrix computations are the most numerically sensitive operations in the library. The condition number of the matrix determines how many digits of accuracy are lost in every operation, and pivoting strategy determines whether the algorithm amplifies or controls round-off.

**Condition number and digit loss.** The condition number $\kappa(A) = \|A\| \cdot \|A^{-1}\|$ measures how sensitive the solution of $Ax = b$ is to perturbations in $A$ or $b$. The key rule of thumb is:

$$\text{digits lost} \approx \log_{10} \kappa(A)$$

For double precision with $\sim 16$ significant digits, a system with $\kappa(A) = 10^{12}$ yields a solution with only $\sim 4$ reliable digits. When $\kappa(A) > 10^{16}$, the solution is numerically meaningless. The library does not currently compute or report condition numbers; callers working with potentially ill-conditioned systems (e.g., multicollinear regression in Chapter 17, nearly parallel constraints in Chapter 12) should estimate $\kappa$ externally and consider regularisation.

**Partial pivoting and growth factors.** Without pivoting, Gaussian elimination can amplify round-off catastrophically. Pivoting on an element of size $10^{-20}$ produces multipliers of $10^{20}$, which magnify any rounding error in subsequent rows by the same factor. Partial pivoting (selecting the largest absolute entry in the current column as the pivot) bounds the multipliers by 1, reducing the growth factor. In theory, the growth factor with partial pivoting can reach $2^{n-1}$, but in practice it almost never exceeds $\sim 10$ for matrices arising in applications. Full pivoting (searching the entire remaining submatrix) has a tighter bound of $n^{1/2}(2 \cdot 3^{1/2} \cdot \ldots \cdot n^{1/(n-1)})^{1/2}$ but costs $O(n^2)$ comparisons per step; partial pivoting is sufficient for all practical cases.

**Never invert to solve.** Computing $A^{-1}$ and then forming $A^{-1}b$ requires $\sim 3$ times the arithmetic of direct LU-based solve and introduces additional round-off from the extra matrix multiplication. The `solve(A, b)` function uses forward elimination plus back-substitution at $O(n^3)$ cost. The `inverse` function exists only when $A^{-1}$ itself is needed (e.g., the covariance matrix $(X^TX)^{-1}$ in regression). The relative residual $\|Ax - b\| / \|b\|$ should be checked after any solve to detect ill-conditioning.

**Determinant computation.** The determinant is computed as a byproduct of row reduction: $\det(A) = (-1)^s \prod_i u_{ii}$, where $s$ is the number of row swaps and $u_{ii}$ are the pivots. For large matrices, the product of pivots can overflow or underflow even when $\det(A)$ is moderate. Working with $\ln|\det(A)| = \sum \ln|u_{ii}|$ and tracking the sign separately avoids this issue, but the current implementation uses the direct product.

### Implementation Context

The matrix module is the numerical backbone of the library. Design decisions here propagate into eigenvalue computation, optimisation and regression.

**Row-major `Float64Array` storage.** Entry $(i, j)$ lives at `data[i * cols + j]`. This makes row traversal (the inner loop of matrix-vector multiplication) access contiguous memory, which is cache-friendly. Column traversal is not contiguous, so algorithms that need column access (e.g., column pivoting) pay a cache penalty, but row-major is the right default because matrix-vector products and forward elimination both iterate along rows.

**Complexity.** Multiplication is $O(mnp)$ ($O(n^3)$ for square). Solve, determinant and inverse are all $O(n^3)$. Strassen's $O(n^{2.8})$ is not implemented because its overhead exceeds naive $O(n^3)$ for the matrix sizes typical in this library ($n < 500$).

**Testing strategy.** Solve $A x = b$ and verify $\|Ax - b\| / \|b\| < \varepsilon$. Confirm $A \cdot A^{-1} = I$ within tolerance. Test determinant sign-change tracking with known row swaps. Verify dimension-mismatch errors for incompatible operands.

