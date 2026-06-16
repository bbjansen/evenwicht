<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Differential Calculus — API Reference

This is the API reference for the TypeScript implementation of Differential Calculus. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/expr/differentiate.ts` — symbolic differentiation (Algorithm 4.29)
- `src/expr/simplify.ts` — algebraic simplification, applied after differentiation
- `src/numeric/derivative.ts` — forward, central, backward finite differences

### Data Representation

Symbolic differentiation operates on the `Expr` type from `src/expr/expr.ts` (defined in Chapter 1). The `differentiate` function takes an `Expr` and a variable name string, and returns a new `Expr` representing the derivative. No mutation occurs: the input tree is not modified.

Numerical differentiation operates on plain JavaScript functions `(x: number) => number`. It does not interact with the expression tree system.

### API Preview

```typescript
// Symbolic differentiation — src/expr/differentiate.ts

/** Differentiate an expression tree with respect to a named variable. */
function differentiate(expr: Expr, variable: string): Expr;

// Algebraic simplification — src/expr/simplify.ts

/** Apply algebraic identities to reduce an expression tree (x+0 -> x, x*1 -> x, etc.). */
function simplify(expr: Expr): Expr;

// Numerical differentiation — src/numeric/derivative.ts

/**
 * Approximate f'(x) using finite differences.
 * Central differences (default) achieve O(h^2) truncation error;
 * forward/backward differences achieve O(h).
 */
function differentiateNumeric(
  f: (x: number) => number,
  x: number,
  opts?: {
    method?: 'forward' | 'central' | 'backward';  // default: 'central'
    h?: number;                                     // default: ~6e-6 for central, ~1.5e-8 for forward/backward
  }
): number;
```

### Dispatch on `expr.kind`

The `differentiate` function is implemented as a `switch` statement on `expr.kind`, directly mirroring Algorithm 4.29. Each `case` constructs a new expression tree using the constructor functions from `src/expr/constructors.ts`. The chain rule is embedded in every unary function case: the derivative of `sin(A)` is `mul(cos(A), differentiate(A, v))`, where the recursive call `differentiate(A, v)` handles the chain rule's "inner derivative."

The `pow` case contains a three-way branch:
1. If the exponent is a constant (`expr.exponent.kind === 'const'`): apply the power rule.
2. If the base is a constant (`expr.base.kind === 'const'`): apply the exponential rule.
3. Otherwise: apply the general logarithmic differentiation formula.

### Simplification After Differentiation

Raw differentiation output is verbose. For instance, $\frac{d}{dx}[x^2]$ produces `mul(mul(constant(2), pow(x, constant(1))), constant(1))`, which represents $2 \cdot x^1 \cdot 1$. After simplification, this reduces to `mul(constant(2), variable('x'))`, representing $2x$. The `simplify` function applies the rules documented in plan.md (Week 4): $x \cdot 1 \to x$, $x^1 \to x$, $0 + x \to x$, constant folding and so on.

The recommended workflow is:

```typescript
const df = simplify(differentiate(f, 'x'));
```

### Error Handling

- **Symbolic differentiation**: Never throws. All expression kinds have defined derivative rules. Variables not matching the differentiation variable are treated as constants (their derivative is 0).
- **Numerical differentiation**: May return `NaN` or `Infinity` if the function $f$ produces such values at or near the evaluation point. The step size `h` must be positive; passing `h <= 0` throws an `Error`.

### Dependencies

- `src/expr/types.ts` — `Expr` type (Chapter 1)
- `src/expr/constructors.ts` — tree-building functions used internally by `differentiate`

### Usage Examples

```typescript
import { variable, pow, constant, sin } from 'evenwicht/expr';
import { differentiate, simplify, evaluate } from 'evenwicht/expr';
import { differentiateNumeric } from 'evenwicht/numeric';

// Symbolic: d/dx[x^3] = 3x^2
const x = variable('x');
const f = pow(x, constant(3));
const df = simplify(differentiate(f, 'x'));
evaluate(df, { x: 2 });  // 12

// Numerical: approximate derivative of sin at pi/4
differentiateNumeric(Math.sin, Math.PI / 4);  // ≈ cos(pi/4) ≈ 0.7071

// Numerical with explicit method
differentiateNumeric(Math.sin, Math.PI / 4, { method: 'forward', h: 1e-7 });
```

### Connections

This chapter is used by Chapter 5 (Integral Calculus, via the Fundamental Theorem of Calculus), Chapter 6 (Taylor series require higher-order derivatives), Chapter 7 (partial derivatives extend single-variable differentiation), Chapter 11 (optimisation uses critical points where $f'=0$) and Chapter 23 (the derivative as a linear operator). It builds on Chapter 1 (Expressions) and Chapter 3 (Limits).

- **Integral Calculus** (Chapter 5): The Fundamental Theorem of Calculus establishes that differentiation and integration are inverse operations. If $F'(x) = f(x)$, then $\int_a^b f(x)\,dx = F(b) - F(a)$. The symbolic differentiation algorithm from this chapter is the verification mechanism: to check a proposed antiderivative $F$, differentiate it and confirm that the result matches $f$.

- **Series & Approximation** (Chapter 6): Taylor series require higher-order derivatives: $f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n$. The symbolic differentiation function can be applied repeatedly to compute $f^{(n)}$, and the `simplify` function keeps the intermediate expressions manageable.

- **Multivariate Calculus** (Chapter 7): Partial derivatives extend the single-variable derivative to functions of several variables. The `differentiate` function already supports this: for an expression containing variables $x$ and $y$, calling `differentiate(expr, 'x')` differentiates with respect to $x$ while treating $y$ as a constant (since variables not matching the differentiation variable return 0 in the `var` case). Gradients, Jacobians and Hessians are built from repeated application of `differentiate` with different variable names.

- **Unconstrained Optimisation** (Chapter 11): Finding local minima and maxima requires solving $f'(x) = 0$ (first-order necessary condition) and checking $f''(x)$ (second-order sufficient condition). Gradient descent uses $\nabla f$, the vector of partial derivatives, as the direction of steepest descent.

- **Operator Algebra** (Chapter 23): The derivative $D$ is a linear operator (Theorem 4.6). It composes with itself ($D^2$ gives the second derivative), with the shift operator ($DL$ differentiates a lagged expression) and with matrix operators. Chapter 23 develops this perspective, treating $D$ as an element of an operator algebra alongside shift, integration and matrix multiplication.



### What Is Implemented vs. Documented Only

- [x] Symbolic differentiation for all 15 `Expr` kinds
- [x] Simplification applied after differentiation
- [x] Forward, central and backward numerical differences
- [x] Configurable step size and method for numerical differentiation
- [ ] Automatic differentiation (deferred — requires dual numbers or tape-based approach)
- [ ] Higher-order numerical derivatives (deferred to Chapter 6/Week 9)
### Numerical Considerations

Numerical differentiation is governed by a fundamental tension between truncation error (which decreases with step size $h$) and round-off error (which increases as $h$ shrinks). This tension determines the achievable accuracy and the optimal step size for each difference scheme.

**The step-size dilemma.** The central difference formula has two competing error sources. The truncation error from the Taylor expansion is $O(h^2)$, while the round-off error from subtracting nearly equal values $f(x+h)$ and $f(x-h)$ is $O(\varepsilon_{\text{mach}} / h)$. Balancing these gives the optimal step size and best achievable error:

$$h_{\text{opt}}^{\text{central}} \approx \varepsilon_{\text{mach}}^{1/3} \approx 6 \times 10^{-6}, \quad \text{error} \approx \varepsilon_{\text{mach}}^{2/3} \approx 4 \times 10^{-11}$$

For the forward difference scheme, the truncation error is $O(h)$ and the round-off is $O(\varepsilon_{\text{mach}} / h)$, giving:

$$h_{\text{opt}}^{\text{forward}} \approx \varepsilon_{\text{mach}}^{1/2} \approx 1.5 \times 10^{-8}, \quad \text{error} \approx \varepsilon_{\text{mach}}^{1/2} \approx 1.5 \times 10^{-8}$$

The central scheme therefore yields roughly 10 correct digits at best, versus 8 for forward/backward. The library default of $h = 10^{-5}$ targets a safe middle ground for central differences.

**Symbolic differentiation is exact but can swell.** Symbolic differentiation applies the sum, product, quotient and chain rules recursively on the expression tree. The result is mathematically exact (no truncation or rounding), but the output tree size can grow as $O(n \cdot 2^d)$ where $d$ is the nesting depth, because the product and quotient rules each double the tree width. Without post-differentiation simplification, this expression swell compounds through higher-order derivatives (Chapter 6, Taylor series) and can cause exponential blowup. Always call `simplify` after `differentiate`.

**When numerical differentiation fails.** The central difference formula fails at points where $f$ is not smooth (e.g., $|x|$ at $x = 0$), returning a value that depends on $h$ rather than converging. It also fails for functions with rapid oscillation on scales smaller than $h$, producing aliased derivative estimates. For functions with known singularities, the forward or backward scheme can be used to approach the singularity from one side, but accuracy degrades near the singular point. Symbolic differentiation handles all these cases correctly, producing the exact derivative expression (which may itself be undefined at the singular point).

### Implementation Context

The chapter ships two independent paths (symbolic and numerical differentiation) whose design trade-offs are complementary.

**Symbolic differentiation via tree recursion.** `differentiate` dispatches on the `kind` tag of the `Expr` discriminated union and applies the corresponding rule (sum, product, quotient, chain) recursively. Each node produces a bounded number of output nodes, but the product and quotient rules double the tree width, so the output size is $O(n \cdot 2^d)$ in the worst case where $d$ is the nesting depth. Always call `simplify` after `differentiate` to collapse identity terms ($x + 0$, $x \cdot 1$, $0 \cdot x$) and prevent expression swell from propagating into later computations.

**Forward and backward variants.** These are $O(h)$ accurate and exist for boundary cases: causal signals or one-sided domains where sampling on both sides of $x$ is not possible.

**Performance.** Symbolic differentiation is $O(n)$ in the input tree size (before simplification). Numerical differentiation costs 2 function evaluations regardless of expression complexity, making it the pragmatic choice when $f$ is a black-box callback.

**Testing strategy.** Symbolic: round-trip $d/dx[x^n]$ against $n x^{n-1}$ for several $n$; verify chain rule on $\sin(\exp(x))$. Numerical: compare against symbolic derivatives at random points; confirm error order by halving $h$ and checking the ratio of successive errors ($\approx 4$ for central, $\approx 2$ for forward).

