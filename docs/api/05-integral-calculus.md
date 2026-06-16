<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Integral Calculus — API Reference

This is the API reference for the TypeScript implementation of Integral Calculus. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Numerical integration is implemented in:

- `src/numeric/integral.ts` — the `integrateNumeric` function

Symbolic (exact, closed-form) integration is not implemented in Evenwicht. While symbolic differentiation is a straightforward recursive tree transformation (each differentiation rule corresponds to a pattern match on expression nodes), symbolic integration is fundamentally harder: there is no simple recursive algorithm that finds antiderivatives for arbitrary expressions. The Risch algorithm (1969) provides a decision procedure for integration in terms of elementary functions, but its implementation is exceedingly complex and lies outside the scope of this library. All integration in Evenwicht is numerical.

### Data Representation

The integrand `f` is a plain JavaScript function `(x: number) => number`. Integration limits are `number` values. The result is a single `number` approximating the definite integral.

### API Preview

```typescript
// Numerical integration — src/numeric/integral.ts

/**
 * Approximate the definite integral of f over [a, b].
 *
 * @param f - The integrand.
 * @param a - Lower limit of integration.
 * @param b - Upper limit of integration.
 * @param opts.method - Quadrature rule: 'trapezoid', 'simpson', or 'midpoint'.
 * @param opts.n - Number of subintervals (default: 100).
 */
function integrateNumeric(
  f: (x: number) => number,
  a: number,
  b: number,
  opts?: {
    method?: 'trapezoid' | 'simpson' | 'midpoint';
    n?: number;
  }
): number;
```

**Parameters**:
- `f` -- the integrand, a function from `number` to `number`.
- `a`, `b` -- the lower and upper limits of integration. The case $a > b$ is handled by the convention $\int_a^b f = -\int_b^a f$.
- `opts.method` -- the quadrature rule to use. Default: `'simpson'`.
- `opts.n` -- the number of subintervals. Default: `100`. For Simpson's rule, `n` is rounded up to the next even number if odd.

**Return value**: a `number` approximating $\int_a^b f(x)\,dx$.

### Error Handling

- If `a === b`, the function returns `0` (the integral over an interval of zero width is zero).
- If `f` returns `NaN` or `Infinity` at any evaluation point, the result is `NaN`. The library does not attempt to handle singularities automatically.
- If `n <= 0`, the function throws an `Error`.

### Dependencies

- No external module dependencies; the numerical integrator is self-contained
- Used by: `src/stats/distributions.ts` (CDF via numerical integration), `src/fractional/` (Riemann–Liouville integral)

### Usage Examples

```typescript
import { integrateNumeric } from 'evenwicht/numeric';

// Integral of x^2 from 0 to 1 = 1/3
integrateNumeric((x) => x * x, 0, 1);  // ≈ 0.33333

// Integral of sin(x) from 0 to pi = 2
integrateNumeric(Math.sin, 0, Math.PI);  // ≈ 2.0

// Using trapezoid rule with 1000 subintervals
integrateNumeric(
  (x) => Math.exp(-x * x), 0, 3,
  { method: 'trapezoid', n: 1000 },
);  // ≈ 0.8862 (close to sqrt(pi)/2)
```

### Connections

This chapter is used by Chapter 6 (Series & Approximation — term-by-term integration of power series), Chapter 13 (Probability Theory — expected value as an integral), Chapter 2 (Special Functions — the Gamma and Beta functions are defined as integrals) and Chapter 24 (Fractional Calculus — the Riemann–Liouville fractional integral generalises the Cauchy formula for iterated integration).

- **Chapter 4 (Differentiation)**: The Fundamental Theorem of Calculus is the link between Chapters 4 and 5. Differentiation and integration are inverse operations: the FTC Part 1 says $\frac{d}{dx}\int_a^x f(t)\,dt = f(x)$, and Part 2 says $\int_a^b F'(x)\,dx = F(b) - F(a)$. The proofs of the substitution rule and integration by parts rely directly on the chain rule and product rule from Chapter 4.

- **Chapter 6 (Series & Approximation)**: Power series can be integrated term by term within their radius of convergence: $\int \sum a_n x^n\,dx = \sum \frac{a_n}{n+1}x^{n+1} + C$. This provides a method for finding antiderivatives of functions defined by series (e.g., $\int e^{-x^2}\,dx$ expressed as a power series) and is the basis for Taylor series derivations of special function values.

- **Chapter 13 (Probability Theory)**: The expected value of a continuous random variable $X$ with density $f$ is $E[X] = \int_{-\infty}^{\infty} x\,f(x)\,dx$, a direct application of the improper integral. Every probability computation involving a continuous distribution (CDF evaluation, moment computation, convolution) reduces to integration. The numerical quadrature methods of this chapter provide the computational basis.

- **Chapter 2 (Special Functions)**: The Gamma function $\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}\,dt$ and the Beta function $B(a,b) = \int_0^1 t^{a-1}(1-t)^{b-1}\,dt$ are both definite (improper) integrals. The proof of the factorial property $\Gamma(z+1) = z\Gamma(z)$ uses integration by parts (Theorem 5.13 of this chapter). The error function $\operatorname{erf}(x) = \frac{2}{\sqrt{\pi}}\int_0^x e^{-t^2}\,dt$ is defined as an integral, and its derivative $\operatorname{erf}'(x) = \frac{2}{\sqrt{\pi}}e^{-x^2}$ follows from FTC Part 1.

- **Chapter 24 (Fractional Calculus)**: The Riemann–Liouville fractional integral of order $\alpha > 0$ is

$$I^\alpha f(x) = \frac{1}{\Gamma(\alpha)}\int_a^x (x - t)^{\alpha - 1}f(t)\,dt,$$

a direct generalisation of Cauchy's formula for $n$-fold iterated integration. When $\alpha$ is a positive integer $n$, this reduces to the ordinary $n$-th iterated integral of $f$. The transition from integer to non-integer $\alpha$, the central idea of fractional calculus, rests on the Riemann integral and the Gamma function.



### What Is Implemented vs. Documented Only

- [x] Midpoint rule
- [x] Trapezoid rule
- [x] Simpson's rule
- [ ] Adaptive quadrature (deferred — would double $n$ until convergence)
- [ ] Gauss–Legendre quadrature (deferred — higher accuracy per evaluation for smooth functions)
- [ ] Symbolic / closed-form integration (out of scope)
### Numerical Considerations

Numerical quadrature approximates a definite integral by evaluating the integrand at finitely many points. The accuracy depends on the smoothness of the integrand, the quadrature rule and the number of subintervals. The three Newton–Cotes rules provided by the library differ substantially in convergence order and have distinct failure modes.

**Convergence order and error bounds.** For a smooth integrand $f$ on $[a, b]$ with step size $h = (b-a)/n$, the error bounds for each rule are:

$$E_{\text{trapezoid}} = -\frac{(b-a)}{12}\,h^2\,f''(\xi), \quad E_{\text{midpoint}} = \frac{(b-a)}{24}\,h^2\,f''(\xi), \quad E_{\text{Simpson}} = -\frac{(b-a)}{180}\,h^4\,f^{(4)}(\xi)$$

for some $\xi \in [a, b]$. Simpson's rule is fourth-order accurate ($O(h^4)$), meaning doubling $n$ reduces the error by a factor of 16, versus a factor of 4 for the trapezoid and midpoint rules. The midpoint rule has half the error constant of the trapezoid rule at equal $n$, making it the better second-order choice when Simpson's even-$n$ requirement cannot be met.

**Singularities and improper integrals.** None of the rules handle endpoint singularities: if $f$ returns `NaN` or `Infinity` at any sample point, the entire result is poisoned. For integrands with integrable singularities (e.g., $\int_0^1 x^{-1/2}\,dx = 2$), the midpoint rule avoids the singular endpoint and may still converge, while the trapezoid rule fails immediately. For Type I improper integrals ($\int_a^\infty f$), the caller must truncate the domain to a finite cutoff $R$ and verify the tail contribution is negligible. A change of variables $t = 1/x$ transforms a slowly decaying tail into a bounded integrand on $[0, 1/a]$.

**Oscillatory integrands and sampling requirements.** For $f(x) = g(x)\sin(\omega x)$ with large angular frequency $\omega$, the uniform grid must satisfy the Nyquist condition $h \ll 2\pi/\omega$ to resolve the oscillations. With $\omega = 10^4$ and a unit interval, this requires $n > 10^4 / (2\pi) \approx 1600$ subintervals at minimum, with practical accuracy demanding $n$ several times larger. When this makes the computation prohibitively expensive, specialised oscillatory quadrature methods (Filon, Levin) are needed; these are outside the library's current scope.

**Round-off accumulation.** Summing $n$ function evaluations accumulates round-off error proportional to $\sqrt{n} \cdot \varepsilon_{\text{mach}}$ in the average case (or $n \cdot \varepsilon_{\text{mach}}$ in the worst case). For $n = 10^6$, the accumulated round-off is at most $\sim 10^{-10}$, which is comparable to Simpson's truncation error at that resolution. Beyond $n \approx 10^8$, round-off dominates and further subdivision degrades rather than improves the result.

### Implementation Context

Three Newton–Cotes quadrature rules are provided. They share $O(n)$ function evaluations but differ substantially in convergence order.

**Algorithm choice.** Simpson's rule achieves $O(h^4)$ error versus $O(h^2)$ for the trapezoid and midpoint rules, using the same evaluation points plus midpoints. It is the default for smooth integrands. The midpoint rule is actually more accurate than the trapezoid rule at equal $n$ (the constant in its $O(h^2)$ bound is half as large), so it is preferred when Simpson's even-$n$ requirement cannot be met. All three are exact for polynomials up to degree 1 (trapezoid/midpoint) or 3 (Simpson).

**Simpson's even-$n$ guard.** Simpson's rule requires an even number of subintervals. If the caller passes an odd $n$, the implementation silently rounds up to $n+1$ rather than throwing, because the cost difference is one extra evaluation and the alternative (an error) would surprise users with no mathematical benefit.

**Testing strategy.** Integrate $\sin(x)$ on $[0, \pi]$ (exact value 2), $x^3$ on $[0, 1]$ (Simpson must be exact) and $e^{-x^2}$ on $[-5, 5]$ ($\approx \sqrt{\pi}$). Verify that doubling $n$ reduces the error by a factor of $\approx 4$ (trapezoid/midpoint) or $\approx 16$ (Simpson).

