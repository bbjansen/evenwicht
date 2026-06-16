<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Vectors & Vector Spaces — API Reference

This is the API reference for the TypeScript implementation of Vectors & Vector Spaces. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

The vector operations in Evenwicht are located in:

- `src/linear/vector.ts` — core vector arithmetic, dot product, norm, projection, normalisation

### Data Representation

Vectors are stored as `Float64Array`. The length of the array determines the dimension. There is no wrapper class or object; a vector is simply a `Float64Array`, keeping the representation minimal and interoperable.

### Immutability

All operations return new `Float64Array` instances. Input arrays are never mutated. This design follows the library's preference for pure functions (see README) and avoids subtle aliasing bugs.

### API Preview

```typescript
// src/linear/vector.ts

/**
 * Component-wise addition of two vectors.
 * Throws if the vectors have different lengths.
 */
function vectorAdd(u: Float64Array, v: Float64Array): Float64Array;

/**
 * Multiply every component of v by the scalar c.
 */
function vectorScale(c: number, v: Float64Array): Float64Array;

/**
 * Dot product (inner product) of u and v.
 * Throws if the vectors have different lengths.
 */
function dot(u: Float64Array, v: Float64Array): number;

/**
 * Euclidean norm of v: sqrt(v . v).
 * Uses scaled computation to avoid overflow/underflow.
 */
function norm(v: Float64Array): number;

/**
 * Orthogonal projection of u onto v: ((u . v) / (v . v)) * v.
 * Throws if v is the zero vector or if lengths differ.
 */
function projection(u: Float64Array, v: Float64Array): Float64Array;

/**
 * Return the unit vector in the direction of v: v / ||v||.
 * Throws if v is the zero vector.
 */
function normalize(v: Float64Array): Float64Array;
```

### Error Handling

- **Dimension mismatch**: `vectorAdd`, `dot` and `projection` throw an `Error` if the input vectors have different lengths. The error message includes the actual lengths to aid debugging.
- **Zero vector**: `projection` and `normalize` throw an `Error` when the direction vector is the zero vector (division by zero in the scalar coefficient).
- **Empty vectors**: Operations on zero-length `Float64Array` instances return zero-length results (for `vectorAdd`, `vectorScale`) or return 0 (for `dot`, `norm`). These edge cases follow the mathematical convention that a sum over an empty index set is zero.

### Dependencies

- No external module dependencies; vector operations are self-contained primitives
- Used by: `src/linear/matrix.ts`, `src/optimization/`, `src/linear/eigen.ts`

### Usage Examples

```typescript
import { vectorAdd, vectorScale, dot, norm, normalize, projection } from 'evenwicht/linear';

const u = new Float64Array([1, 2, 3]);
const v = new Float64Array([4, 5, 6]);

vectorAdd(u, v);      // Float64Array [5, 7, 9]
vectorScale(2, u);    // Float64Array [2, 4, 6]
dot(u, v);            // 32
norm(u);              // sqrt(14) ≈ 3.7417
normalize(u);         // [0.2673, 0.5345, 0.8018]
projection(u, v);     // projects u onto v
```

### Connections

This chapter is used by Chapter 9 (Matrices — a matrix is a linear map between vector spaces), Chapter 10 (Eigenvalues — eigenvectors are special vectors left invariant in direction by a linear map), Chapter 11 (Optimisation — the gradient is a vector, gradient descent moves along vectors), Chapter 15 (Descriptive Statistics — covariance as an inner product on the space of random variables) and Chapter 17 (Regression — data columns as vectors, the normal equations as a projection). The dot product and norm defined here already appeared informally in Chapter 7 (Multivariate Calculus), where the gradient $\nabla f$ and directional derivative $D_\mathbf{u}f = \nabla f \cdot \mathbf{u}$ rely on vector operations; this chapter provides the formal foundations.

- **Chapter 9 (Matrices)**: A matrix is a linear map between vector spaces. Matrix-vector multiplication $A\mathbf{v}$ transforms a vector $\mathbf{v} \in \mathbb{R}^n$ into a vector $A\mathbf{v} \in \mathbb{R}^m$. The columns of $A$ determine the image of the standard basis vectors, and the column space of $A$ is a subspace of $\mathbb{R}^m$. The concepts of span, linear independence, basis and dimension defined in this chapter are the language used to analyse matrices.

- **Chapter 10 (Eigenvalues)**: An eigenvector $\mathbf{v}$ of a matrix $A$ satisfies $A\mathbf{v} = \lambda\mathbf{v}$; it is a vector whose direction is unchanged by the linear map. Finding eigenvectors reduces to solving a system of linear equations in the vector space framework. Eigenvectors corresponding to distinct eigenvalues of a symmetric matrix are orthogonal (using the inner product from this chapter).

- **Chapter 7 (Multivariate Calculus)**: The gradient $\nabla f(\mathbf{a})$ is a vector in $\mathbb{R}^n$. The directional derivative $D_\mathbf{u}f = \nabla f \cdot \mathbf{u}$ is a dot product. The Cauchy–Schwarz inequality proves that $|D_\mathbf{u}f| \leq \|\nabla f\|$, with equality when $\mathbf{u}$ is the unit vector in the gradient direction. This is the theoretical basis of gradient descent.

- **Chapter 15 (Descriptive Statistics)**: A data set with $n$ observations of a variable can be viewed as a vector in $\mathbb{R}^n$. The sample covariance between two variables is the dot product of their centred data vectors (divided by $n-1$). The correlation coefficient is the cosine of the angle between centred data vectors; a direct application of Definition 8.9.

- **Chapter 17 (Regression)**: Ordinary least squares fits a linear model by projecting the response vector $\mathbf{y}$ onto the column space of the design matrix $X$. The residual vector $\mathbf{e} = \mathbf{y} - X\hat{\boldsymbol{\beta}}$ is orthogonal to the column space. This is the projection and orthogonality framework from this chapter, applied in $\mathbb{R}^n$ where $n$ is the number of observations.



### What Is Implemented vs. Documented Only

- [x] Vector addition (`vectorAdd`)
- [x] Scalar multiplication (`vectorScale`)
- [x] Dot product (`dot`)
- [x] Euclidean norm (`norm`)
- [x] Projection (`projection`)
- [x] Normalisation (`normalize`)
- [ ] Cross product in $\mathbb{R}^3$ (deferred — specialised to 3 dimensions, not part of general linear algebra)
- [ ] Gram–Schmidt orthogonalisation (documented in this chapter, implementation deferred to Chapter 9)
- [ ] $p$-norms for $p \neq 2$ (deferred)
### Numerical Considerations

Vector operations are the numerical foundation for all linear algebra in the library. Although the individual operations are simple, they interact with floating-point arithmetic in ways that become significant at scale.

**Norm overflow and underflow.** The naive computation $\|\mathbf{v}\| = \sqrt{\sum v_i^2}$ overflows when any $|v_i| > 10^{154}$ (since $(10^{154})^2 = 10^{308}$ is near the double-precision maximum) and underflows when all $|v_i| < 10^{-162}$ (since $(10^{-162})^2 = 10^{-324}$ rounds to zero). In both cases the true norm may be perfectly representable. The implementation uses scaled computation: it divides every component by $\max_i |v_i|$ before squaring, then multiplies the result by the scale factor:

$$\|\mathbf{v}\| = \max_i |v_i| \cdot \sqrt{\sum_i \left(\frac{v_i}{\max_i |v_i|}\right)^2}$$

This two-pass algorithm costs $O(n)$ extra but prevents silent overflow and underflow. The built-in `Math.hypot` uses a similar technique internally.

**Dot product rounding error.** The naive summation loop $\sum_{i=1}^n u_i v_i$ has worst-case rounding error bounded by $n \varepsilon_{\text{mach}} \sum |u_i v_i|$. For $n = 1000$ and terms of comparable magnitude, this means up to $\sim 10^{-13}$ relative error, which is adequate for most applications. Kahan compensated summation would reduce the error bound to $O(\varepsilon_{\text{mach}})$ independent of $n$, at roughly $4\times$ the arithmetic cost per element; it is not used in the current implementation. When high-precision dot products are critical (e.g., in iterative refinement for ill-conditioned linear systems), callers should consider external compensated summation.

**Projection numerical stability.** The projection formula $\operatorname{proj}_{\mathbf{v}} \mathbf{u} = \frac{\mathbf{u} \cdot \mathbf{v}}{\mathbf{v} \cdot \mathbf{v}} \mathbf{v}$ involves dividing by $\|\mathbf{v}\|^2$. When $\mathbf{v}$ is nearly the zero vector (all components near machine epsilon), the denominator is tiny and the result is dominated by round-off. The function throws an `Error` for the exact zero vector but does not warn for near-zero vectors. In the Gram–Schmidt orthogonalisation context (Chapter 9), repeated projections can accumulate rounding errors that destroy orthogonality; the modified Gram–Schmidt algorithm or Householder reflections are more stable alternatives.

### Implementation Context

Vector operations are low-level building blocks consumed by the matrix, eigenvalue and optimisation modules, so their design prioritises correctness and cache efficiency over flexibility.

**`Float64Array` over `number[]`.** All vectors are stored as `Float64Array` rather than plain `number[]`. Both use IEEE 754 double-precision (64-bit) floats, so the arithmetic is identical. The advantages of `Float64Array` are:

- *Memory layout*: A `Float64Array` is backed by a contiguous `ArrayBuffer`. This improves cache locality for sequential access patterns, which vector operations invariably have.
- *Type guarantee*: Every element is a double. A `number[]` can accidentally contain `undefined`, strings or objects; a `Float64Array` silently coerces anything to a float, preventing type-related bugs.
- *Interoperability*: `Float64Array` can be passed directly to WebAssembly, WebGL or other typed-array-aware APIs without conversion.

For small vectors ($n \le 10$) the allocation overhead is comparable to the benefit; for large vectors ($n \ge 100$) the cache advantage is measurable.

**Immutability.** Every operation allocates and returns a new `Float64Array`. Input arrays are never mutated. This avoids aliasing bugs (e.g., `vectorAdd(v, v)` working correctly) and aligns with the library's pure-function convention.

**Testing strategy.** Verify `dot` and `norm` against hand-computed values for small vectors. Test overflow resistance of `norm` with components at $10^{200}$. Test dimension-mismatch throws. Confirm `projection(u, v)` satisfies $u - \text{proj}_v(u) \perp v$ within tolerance.

