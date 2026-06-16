<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Operator Algebra — API Reference

This is the API reference for the TypeScript implementation of Operator Algebra. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/operators/operator.ts` — `Operator<T>` and `LinearOperator<T>` interfaces, identity, zero
- `src/operators/compose.ts` — generic composition, addition, scalar multiplication
- `src/operators/polynomial.ts` — `polynomialOperator` construction
- `src/operators/derivative_operator.ts` — wraps `differentiate()` from `src/expr/`
- `src/operators/shift_operator.ts` — wraps shift logic from `src/discrete/`
- `src/operators/matrix_operator.ts` — wraps matrix-vector multiply from `src/linear/`

### Data Representation

The operator abstraction in Evenwicht operates at Layer C of the architecture (see `docs/plan.md`). An operator is a generic interface parameterised by the type of object it transforms. Concrete operators wrap the existing domain-specific computations from Layers B and D.

- **Symbolic operators** transform `Expr` values (the expression tree from `src/expr/expr.ts`).
- **Sequence operators** transform `Float64Array` or `number[]` values (sequences from `src/discrete/sequence.ts`).
- **Matrix operators** transform `Float64Array` vectors (using the matrix infrastructure from `src/linear/matrix.ts`).

### File Structure

| File | Responsibility |
|------|---------------|
| `src/operators/operator.ts` | `Operator<T>` and `LinearOperator<T>` interfaces, identity, zero |
| `src/operators/compose.ts` | Generic composition, addition, scalar multiplication |
| `src/operators/polynomial.ts` | `polynomialOperator` construction |
| `src/operators/derivative_operator.ts` | Wraps `differentiate()` from `src/expr/differentiate.ts` |
| `src/operators/integral_operator.ts` | Wraps symbolic integration (limited scope) |
| `src/operators/shift_operator.ts` | Wraps shift logic from `src/discrete/shift.ts` |
| `src/operators/matrix_operator.ts` | Wraps matrix-vector multiply from `src/linear/matrix.ts` |

### Design Decisions

- The operator interface is generic over the element type `T`. This allows the same algebraic operations (compose, add, scale) to work regardless of whether the underlying objects are expressions, sequences, or vectors.
- Composition creates a new operator object that stores references to its operands. Application triggers a chain of `apply` calls (lazy evaluation of the composition).
- No attempt is made to simplify composed operators symbolically. The operator `compose(D, D)` does not produce a "second derivative" operator object; it produces a composed operator that applies $D$ twice when `apply` is called.
- The polynomial operator eagerly computes intermediate results during `apply` (Algorithm 6.2), avoiding exponential blowup of expression trees.

### API Preview

```typescript
// Core interface — src/operators/operator.ts
interface Operator<T> {
  apply(x: T): T;
}

interface LinearOperator<T> extends Operator<T> {
  add(other: LinearOperator<T>): LinearOperator<T>;
  scale(c: number): LinearOperator<T>;
  compose(other: LinearOperator<T>): LinearOperator<T>;
}

// Identity and zero — src/operators/operator.ts
function identityOperator<T>(): LinearOperator<T>;
function zeroOperator<T>(zero: T): LinearOperator<T>;
```

```typescript
// Concrete operators — domain-specific wrappers

// Derivative operator on symbolic expressions
// src/operators/derivative_operator.ts
function derivativeOperator(variable: string): LinearOperator<Expr>;

// Integration operator on symbolic expressions
// src/operators/integral_operator.ts
function integralOperator(variable: string): LinearOperator<Expr>;

// Shift (lag) operator on sequences
// src/operators/shift_operator.ts
function shiftOperator(k: number): LinearOperator<Float64Array>;

// Matrix operator on vectors
// src/operators/matrix_operator.ts
function matrixOperator(A: Matrix): LinearOperator<Float64Array>;
```

```typescript
// Composition and polynomial operators
// src/operators/compose.ts
function compose<T>(
  first: LinearOperator<T>,
  second: LinearOperator<T>
): LinearOperator<T>;

function polynomialOperator<T>(
  base: LinearOperator<T>,
  coefficients: number[],
  identity: LinearOperator<T>
): LinearOperator<T>;
```

```typescript
// Usage examples
import { derivativeOperator, identityOperator, compose, polynomialOperator } from 'evenwicht/operators';
import { Expr, variable, sin, evaluate } from 'evenwicht/expr';

const D = derivativeOperator('x');
const I = identityOperator<Expr>();
const D2 = compose(D, D);                          // Second derivative
const p = polynomialOperator(D, [2, 3, 1], I);    // D² + 3D + 2I

const f = sin(variable('x'));
const result = p.apply(f);  // f'' + 3f' + 2f = -sin(x) + 3cos(x) + 2sin(x)
```

### Error Handling

- `compose` throws if the operators have incompatible types (TypeScript enforces this at compile time).
- `polynomialOperator` with an empty coefficient array returns the zero operator.
- `matrixOperator` throws if the matrix is not square (only square matrices define endomorphisms on a fixed-dimension vector space).
- `shiftOperator` with `k = 0` returns the identity operator.

### Dependencies

- `src/expr/differentiate.ts` — underlying engine for `derivativeOperator`
- `src/discrete/shift.ts` — underlying engine for `shiftOperator`
- `src/linear/matrix.ts` — `matrixVectorProduct` for `matrixOperator`

### Usage Examples

```typescript
import { derivativeOperator, identityOperator, compose, polynomialOperator } from 'evenwicht/operators';
import { variable, sin, evaluate } from 'evenwicht/expr';

// Second derivative operator
const D = derivativeOperator('x');
const D2 = compose(D, D);

// Polynomial operator: D^2 + 3D + 2I (constant-coefficient ODE operator)
const I = identityOperator();
const L = polynomialOperator(D, [2, 3, 1], I);

// Apply to sin(x): should give -sin(x) + 3cos(x) + 2sin(x) = sin(x) + 3cos(x)
const f = sin(variable('x'));
const result = L.apply(f);
```

### Connections

This chapter unifies concepts from Chapter 4 (the derivative as a linear operator), Chapter 5 (integration as the inverse of differentiation), Chapter 9 (matrices as operators on $\mathbb{R}^n$), Chapter 10 (eigenvalues as the spectral theory of operators), Chapter 18 (difference equations as polynomial operators in $L$), Chapter 19 (ODEs as polynomial operators in $D$) and Chapter 20 (discrete operators $L$, $\Delta$). It prepares Chapter 24 (Fractional Calculus), where the operator $D^\alpha$ for non-integer $\alpha$ extends the framework developed here. This chapter draws on every preceding part of the library.

- **Differential Calculus** (Ch. 4): The derivative $D$ is the prototypical linear operator. Every differentiation rule from Chapter 4 is a statement about how $D$ interacts with other operations: the product rule says $D(fg) = (Df)g + f(Dg)$, which is the Leibniz rule for the commutator $[D, M_f]$.

- **Integral Calculus** (Ch. 5): Integration is the inverse operator $D^{-1}$. The Fundamental Theorem of Calculus states $D \circ D^{-1} = I$ (on continuous functions) and $D^{-1} \circ D = I + C$ (up to a constant of integration).

- **Matrices** (Ch. 9) and **Eigenvalues** (Ch. 10): A matrix is the finite-dimensional representation of a linear operator. The eigenvalue equation $A\mathbf{v} = \lambda \mathbf{v}$ is the operator eigenvalue problem in $\mathbb{R}^n$. Diagonalisation $A = PDP^{-1}$ decomposes the operator into independent scalar multiplications along eigenvector directions.

- **Difference Equations** (Ch. 18) and **ODEs** (Ch. 19): Both are polynomial operator equations: $p(L)x = f$ and $p(D)y = g$ respectively. The solution theory in both cases reduces to finding roots of the characteristic polynomial.

- **Discrete Operators** (Ch. 20): The shift $L$, difference $\Delta$ and summation $\Sigma$ operators are discrete analogues of $e^{-D}$, $D$ and $D^{-1}$ respectively. This chapter provides the algebraic framework that makes the analogy precise.

- **Fractional Calculus** (Ch. 24): The operators $D^\alpha$ for non-integer $\alpha$ extend the polynomial operator framework to arbitrary real powers. The semigroup property $D^\alpha D^\beta = D^{\alpha + \beta}$ is the composition law for fractional operators.



### What Is Implemented vs. Documented Only

- [x] Generic `Operator<T>` and `LinearOperator<T>` interfaces
- [x] Operator composition, addition, scalar multiplication
- [x] Identity operator and zero operator
- [x] Polynomial operator construction
- [x] Derivative operator wrapper (symbolic)
- [x] Shift operator wrapper (sequences)
- [x] Matrix operator wrapper (vectors)
- [ ] Operator norm computation (deferred; requires norm on the underlying space)
- [ ] Spectral radius computation (deferred; requires eigenvalue machinery on infinite-dimensional spaces)
- [ ] Operator exponential (documented; matrix exponential deferred to future release)
### Implementation Context

**Design decisions.** The `Operator<T>` interface is generic over the element type, allowing the same algebraic combinators (compose, add, scale) to work on expressions, sequences and vectors without code duplication. Composition is lazy: `compose(T1, T2)` stores references and chains `apply` calls at evaluation time rather than eagerly computing a "composed" representation. This avoids exponential blowup of expression trees when building high-degree polynomial operators.

**Polynomial evaluation.** The `polynomialOperator` uses Algorithm 6.2 (iterative accumulation), computing $p(D)f = a_0 f + a_1 Df + \cdots + a_n D^n f$ by maintaining a running derivative and summing weighted terms. This is $O(n)$ applications of the base operator. The alternative Horner-form evaluation could improve numerical stability when coefficients span many orders of magnitude, but is not currently implemented because the symbolic differentiation path produces exact results.

**Numerical pitfalls.** For matrix operators, deep composition $A^n \mathbf{v}$ via repeated multiplication accumulates $O(n)$ round-off; eigendecomposition-based computation is preferred for large $n$. Polynomial operators on sequences (FIR filters) are backward-stable for well-conditioned coefficients, but the inverse operator $\phi(L)^{-1}$ (IIR filter) can be numerically unstable when AR roots lie near the unit circle. The matrix exponential $e^{At}$ is notoriously difficult to compute accurately and is deferred.

**Performance.** Generic composition costs $O(c_1 + c_2)$ where $c_i$ is the cost of each operand's `apply`. Polynomial operator application on sequences is $O(Nn)$ for sequence length $N$ and polynomial degree $n$. Symbolic polynomial operators cost $O(ns)$ where $s$ is expression tree size.

**Testing.** Operator algebra axioms (associativity, distributivity, identity) are verified by applying composed operators to known inputs. The exponential shift property $p(D)(e^{\lambda x}) = p(\lambda)e^{\lambda x}$ provides exact reference values. Sequence operators are tested against direct loop computation.

