<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Series & Approximation — API Reference

This is the API reference for the TypeScript implementation of Series & Approximation. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/expr/taylor.ts` — Taylor polynomial computation on `Expr` trees
- `src/expr/higher_order.ts` — $n$th derivative via repeated symbolic differentiation
- `src/numeric/series.ts` — geometric series sum, numerical partial sums, convergence detection

### Data Representation

The series and approximation module touches three areas of the Evenwicht codebase:

- **`src/expr/taylor.ts`** — Taylor polynomial computation. Operates on the `Expr` type from `src/expr/expr.ts`. Takes an expression, a variable name, a centre and an order and returns a new `Expr` representing the Taylor polynomial.
- **`src/expr/higher_order.ts`** — The $n$th derivative. Repeated application of `differentiate` from `src/expr/differentiate.ts`, with simplification after each step.
- **`src/numeric/series.ts`** — Geometric series sum, numerical partial sums and convergence detection. Operates on plain `number` values and `(n: number) => number` term functions.

### API Preview

```typescript
// Taylor polynomial — src/expr/taylor.ts

/**
 * Compute the Taylor polynomial of expr about center, up to the given order.
 * Uses repeated symbolic differentiation internally.
 */
function taylorPolynomial(
  expr: Expr,
  variable: string,
  center: number,
  order: number
): Expr;
```

```typescript
// Higher-order derivatives — src/expr/higher_order.ts

/** Compute the nth derivative of expr with respect to variable. */
function nthDerivative(expr: Expr, variable: string, n: number): Expr;
```

```typescript
// Series utilities — src/numeric/series.ts

/** Closed-form sum of the geometric series a + ar + ar^2 + ... = a/(1-r). */
function geometricSum(a: number, r: number): number;

interface SeriesResult {
  sum: number;
  terms: number;
  converged: boolean;
}

/**
 * Sum the series term(1) + term(2) + ... until successive partial
 * sums differ by less than tolerance, or maxTerms is reached.
 */
function sumSeries(
  term: (n: number) => number,
  tolerance: number,
  maxTerms: number
): SeriesResult;
```

### Error Handling

- **`taylorPolynomial`**: throws if the variable name is not present in the expression, or if the order is negative. Returns an `Expr` that may evaluate to `NaN` if the derivatives at the centre are undefined (e.g., Taylor expansion of $\ln(x)$ at $a = 0$).
- **`geometricSum`**: throws if $|r| \geq 1$, since the series diverges.
- **`sumSeries`**: returns a result object with a `converged` flag. The caller is responsible for checking this flag and deciding whether to trust the result.

### Dependencies

- `src/expr/differentiate.ts` — repeated differentiation for Taylor coefficients
- `src/expr/simplify.ts` — simplification of intermediate derivative expressions
- `src/expr/evaluate.ts` — evaluating derivatives at the expansion centre

### Usage Examples

```typescript
import { variable, exp, sin } from 'evenwicht/expr';
import { taylorPolynomial, nthDerivative } from 'evenwicht/expr';
import { evaluate } from 'evenwicht/expr';
import { geometricSum, sumSeries } from 'evenwicht/numeric';

// Taylor polynomial of e^x around 0, order 5
const x = variable('x');
const T5 = taylorPolynomial(exp(x), 'x', 0, 5);
evaluate(T5, { x: 1 });  // ≈ 2.71667

// Geometric series sum: 1 + 1/2 + 1/4 + ... = 2
geometricSum(1, 0.5);  // 2

// Numerical series: Basel problem 1/1^2 + 1/2^2 + ...
const result = sumSeries((n) => 1 / (n * n), 1e-10, 100000);
// result.sum ≈ 1.6449 (pi^2/6)
```

### Connections

This chapter builds on Chapter 4 (Differentiation) and Chapter 5 (Integration). It is used by Chapter 25 (Financial Mathematics — geometric series for annuity valuation), Chapter 2 (Special Functions — Stirling's approximation as an asymptotic series), Chapter 22 (Transforms & Spectral Analysis — Fourier series as a generalisation of power series) and Chapter 24 (Fractional Calculus — binomial series for fractional powers).

- **Differential Calculus** (Chapter 4): Taylor polynomials are built from repeated differentiation. The Taylor polynomial $T_n(x) = \sum f^{(k)}(a)(x-a)^k / k!$ requires computing $f^{(k)}$ for $k = 0, 1, \ldots, n$. The symbolic differentiation engine of Chapter 4 provides this capability.
- **Integral Calculus** (Chapter 5): The integral test (Theorem 6.16) converts convergence questions about series into convergence questions about improper integrals. The Fundamental Theorem of Calculus, developed in Chapter 5, is the theoretical link.
- **Special Functions** (Chapter 2): Stirling's approximation $n! \approx \sqrt{2\pi n}(n/e)^n$ is an asymptotic series. The Lanczos approximation of $\Gamma(z)$ is a carefully constructed rational approximation related to series expansions. The error function is defined by an integral whose numerical evaluation often uses a truncated series.
- **Transforms & Spectral Analysis** (Chapter 22): Fourier series express periodic functions as sums of sines and cosines, generalising the idea of power series to orthogonal function bases. The convergence theory of Fourier series parallels that of power series but with important differences (Gibbs phenomenon, $L^2$ convergence vs pointwise convergence).
- **Fractional Calculus** (Chapter 24): The binomial series (Example 6.34) for $(1+x)^\alpha$ with non-integer $\alpha$ provides the expansion used in the Grünwald–Letnikov definition of fractional derivatives. The generalised binomial coefficients $\binom{\alpha}{n}$ are the weights in the fractional finite-difference approximation.
- **Financial Mathematics** (Chapter 25): Annuity and perpetuity formulas are direct applications of finite and infinite geometric series. Present value, bond pricing and amortisation schedules all rest on the geometric series formula $\sum ar^k = a/(1-r)$.



### What Is Implemented vs. Documented Only

- [x] Taylor polynomial computation from an `Expr` via repeated symbolic differentiation
- [x] $n$th derivative via iterated `differentiate` + `simplify`
- [x] Geometric series closed-form sum
- [x] Numerical series summation with convergence detection
- [ ] Symbolic power series manipulation (deferred — requires polynomial ring infrastructure)
- [ ] Pade approximants (deferred)
- [ ] Asymptotic expansions (documented, not implemented)
### Numerical Considerations

Series computation is one of the areas where floating-point arithmetic most visibly departs from exact mathematics. The three main pitfalls are overflow in individual terms, catastrophic cancellation in alternating sums, and unreliable convergence detection.

**Overflow in Taylor coefficients.** For the Taylor series of $e^x$ at large $|x|$, individual terms $x^n / n!$ can overflow double precision even though their ratio $x/(n+1)$ is moderate and the partial sums remain representable. For example, $x^{100}/100! \approx 10^{42}$ when $x = 50$, yet $e^{50} \approx 5.2 \times 10^{21}$. The implementation avoids this by computing coefficients incrementally: the $k$-th coefficient is obtained by multiplying the previous one by $x/(k)$, rather than computing $x^k$ and $k!$ separately. The factorial denominator is accumulated via a running product, which stays in the representable range as long as each intermediate coefficient does.

**Catastrophic cancellation in alternating series.** Summing $\cos(x)$ via its Maclaurin series for large $|x|$ involves terms that alternate in sign and grow as large as $|x|^{2k}/(2k)!$. At $x = 20$, the largest term exceeds $10^{14}$, yet $\cos(20) \approx 0.41$. The partial sums swing wildly before settling to a result that has lost most of its significant digits. The standard mitigation is argument reduction: exploit the periodicity $\cos(x) = \cos(x \bmod 2\pi)$ to reduce $|x|$ to $[0, 2\pi)$ before applying the series. The library does not perform this reduction automatically; callers must do it externally.

**Convergence detection limitations.** The `sumSeries` function terminates when $|a_n| < \varepsilon$, which is necessary but not sufficient for convergence of the partial sums. For alternating series satisfying the Leibniz criterion (terms decreasing in absolute value and tending to zero), this gives a rigorous error bound:

$$|S - S_N| \le |a_{N+1}|$$

For general positive-term series (e.g., the harmonic series $\sum 1/n$), individual terms tend to zero while the series diverges. The current implementation does not detect this case. A more robust criterion would compare successive partial sums $|S_n - S_{n-1}|$, but this adds computational cost and still cannot detect slow divergence.

**Geometric series precision.** The closed-form $a/(1-r)$ is $O(1)$ and exact up to floating-point representation error. For $|r|$ very close to 1, the denominator $1 - r$ loses precision: when $r = 1 - 10^{-15}$, the result $a/10^{-15}$ amplifies the rounding error in $r$ by a factor of $10^{15}$. The $|r| \ge 1$ guard prevents silent divergence but does not warn about ill-conditioning when $r$ is near the boundary.

### Implementation Context

The three facilities (Taylor polynomial, numerical series summation and geometric series) address distinct points on the symbolic-vs-numerical spectrum.

**Taylor polynomial construction.** `taylorPolynomial` calls `differentiate` and `simplify` in a loop, evaluating $f^{(k)}(a)$ numerically at each step to form the coefficient $f^{(k)}(a)/k!$. The cost is $O(n \cdot D(f))$ where $D(f)$ is the per-differentiation cost. Because each differentiation can increase expression size (expression swell), the `simplify` call between iterations is necessary; without it, tree size can grow exponentially with the Taylor order. The factorial is accumulated via a running product to avoid overflow from computing $k!$ directly.

**Testing strategy.** Taylor: expand $\sin(x)$ to order 7 and compare against `Math.sin` at several points. Series: sum $1/n^2$ and compare against $\pi^2/6$; sum the alternating harmonic series and compare against $\ln 2$. Geometric: verify $1/(1-0.5) = 2$ and confirm that $|r| \ge 1$ throws.

