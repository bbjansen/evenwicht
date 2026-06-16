<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Special Functions — API Reference

This is the API reference for the TypeScript implementation of Special Functions. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

The special functions are organised across three source files, reflecting their logical grouping:

- `src/core/special.ts` — Gamma, logGamma, Beta, logBeta
- `src/core/erf.ts` — erf, erfc
- `src/core/factorial.ts` — factorial, binomial, generalizedBinomial, fallingFactorial

### Data Representation

All special functions operate on IEEE 754 double-precision `number` values and return `number`. The Gamma function uses the Lanczos approximation with 15-term coefficients. The error function uses the Abramowitz & Stegun rational approximation. Factorial values for $n \leq 170$ are served from a precomputed lookup table.

### API Preview

```typescript
// Gamma and Beta — src/core/special.ts
/** Gamma function via the Lanczos approximation. */
function gamma(z: number): number;

/** Log-Gamma, computed directly to avoid overflow for large z. */
function logGamma(z: number): number;

/** Beta function via the log-Gamma relation B(a,b) = exp(lnΓ(a)+lnΓ(b)-lnΓ(a+b)). */
function beta(a: number, b: number): number;

/** Log-Beta for stable computation with extreme parameters. */
function logBeta(a: number, b: number): number;
```

```typescript
// Error function — src/core/erf.ts
/** Error function erf(x) using Abramowitz & Stegun rational approximation. */
function erf(x: number): number;

/** Complementary error function erfc(x) = 1 - erf(x). */
function erfc(x: number): number;
```

```typescript
// Combinatorics — src/core/factorial.ts
/** Factorial via lookup table for n <= 170; returns Infinity for n > 170. */
function factorial(n: number): number;

/** Binomial coefficient using the multiplicative formula to avoid overflow. */
function binomial(n: number, k: number): number;

/** Generalized binomial coefficient for real alpha, via falling factorial product. */
function generalizedBinomial(alpha: number, k: number): number;

/** Falling factorial (Pochhammer symbol): x(x-1)...(x-n+1). */
function fallingFactorial(x: number, n: number): number;
```

### Error Handling

The following conventions align with the library's error handling strategy (throw at system boundaries, return NaN/Infinity for mathematical edge cases):

- `gamma(0)`, `gamma(-1)`, `gamma(-2)`, ... return `Infinity` (poles of the Gamma function).
- `gamma(NaN)` returns `NaN`. All functions propagate NaN.
- `gamma(172)` returns `Infinity` (overflow).
- `logGamma(z)` for $z \le 0$ returns `NaN` (undefined in real arithmetic).
- `factorial(n)` throws `Error` if $n$ is negative or not an integer.
- `factorial(171)` returns `Infinity` (overflow).
- `binomial(n, k)` returns `0` when $k < 0$ or $k > n$ (standard combinatorial convention).
- `erf(Infinity)` returns `1`; `erf(-Infinity)` returns `-1`.
- `beta(a, b)` throws `Error` if $a \le 0$ or $b \le 0$.

### Dependencies

- No external module dependencies; the special functions are self-contained primitives
- Used by: `src/stats/distributions.ts` (CDF computations), `src/fractional/` (Gamma in GL weights), `src/genetics/` (binomial coefficients)

### Usage Examples

```typescript
import { gamma, logGamma, beta, erf, factorial, binomial } from 'evenwicht/core';

// Gamma function: Gamma(5) = 4! = 24
gamma(5);         // 24
gamma(0.5);       // sqrt(pi) ≈ 1.7724538509

// Log-Gamma avoids overflow
logGamma(200);    // ≈ 857.934 (gamma(200) would overflow)

// Beta function
beta(2, 3);       // 1/12 ≈ 0.08333

// Error function
erf(1.0);         // ≈ 0.8427

// Combinatorics
factorial(10);    // 3628800
binomial(10, 3);  // 120
```

### Connections

This chapter is used by Chapters 14 (Probability Distributions), 24 (Fractional Calculus) and 6 (Series & Approximation). It builds on Chapter 1 (Expressions & Functions).

- **Chapter 14 (Probability Distributions)**: The normal distribution CDF is computed via erf (Theorem 2.16). The PDFs of the $t$-distribution, $F$-distribution and chi-squared distribution involve the Beta and Gamma functions. The binomial distribution PMF uses binomial coefficients. Every distribution in Chapter 14 depends on the functions defined here.

- **Chapter 24 (Fractional Calculus)**: The Grünwald–Letnikov fractional derivative uses generalised binomial coefficients (Definition 2.21) as its weights. The Riemann–Liouville fractional integral involves $\Gamma(\alpha)$ in its kernel. The fractional derivative of a power function $x^n$ is expressed as $\Gamma(n+1)/\Gamma(n+1-\alpha) \cdot x^{n-\alpha}$, directly linking the Gamma function to the meaning of "fractional differentiation."

- **Chapter 6 (Series & Approximation)**: The generalised binomial series $(1+x)^\alpha = \sum_{k=0}^{\infty}\binom{\alpha}{k}x^k$ uses generalised binomial coefficients. Stirling's approximation connects to asymptotic series.

- **Chapter 13 (Probability Theory)**: Binomial coefficients are the combinatorial foundation of discrete probability. The binomial distribution, multinomial coefficients and counting arguments throughout Chapter 13 rely on the factorial and binomial coefficient defined here.



### What Is Implemented vs. Documented Only

- [x] Gamma function (Lanczos approximation)
- [x] Log-Gamma
- [x] Beta function (via log-Gamma)
- [x] Log-Beta
- [x] Error function (rational approximation)
- [x] Complementary error function
- [x] Factorial (lookup table)
- [x] Binomial coefficient (multiplicative formula + log-Gamma fallback)
- [x] Generalised binomial coefficient (product formula)
- [x] Falling factorial
- [ ] Digamma / trigamma functions (deferred)
- [ ] Incomplete Gamma / incomplete Beta (deferred — needed for distribution CDFs, may be added in Phase 5)
- [ ] Regularised incomplete Beta (deferred)
### Numerical Considerations

Special functions are the numerical primitives consumed by almost every statistical and scientific module, so accuracy and overflow resistance are paramount. The central challenge is that these functions are evaluated at extreme parameter values in practice (e.g., $\Gamma(170)$, $\operatorname{erf}(5)$, $\binom{1000}{500}$), where naive implementations overflow, underflow, or lose all significant digits.

**Gamma function overflow and the log-Gamma path.** The Gamma function grows super-exponentially: $\Gamma(z)$ overflows double precision at $z \approx 171.6$ (since $170! \approx 7.3 \times 10^{306}$). For any computation involving $\Gamma$ at moderate-to-large arguments, the `logGamma` function must be used instead, working entirely in log-space. The Beta function is computed as

$$B(a, b) = \exp\bigl(\ln\Gamma(a) + \ln\Gamma(b) - \ln\Gamma(a+b)\bigr)$$

to avoid intermediate overflow even when $B(a,b)$ itself is representable. The Lanczos approximation with $g = 7$ and 9 coefficients delivers full double-precision accuracy (relative error below $2 \times 10^{-15}$) in $O(1)$ time. For $z < 0.5$, the reflection formula $\Gamma(z)\Gamma(1-z) = \pi / \sin(\pi z)$ is applied first, avoiding the poles at non-positive integers.

**Catastrophic cancellation in erfc.** The error function satisfies $\operatorname{erf}(x) \to 1$ rapidly as $x$ grows: $\operatorname{erf}(4) \approx 0.99999998$. Computing $\operatorname{erfc}(x) = 1 - \operatorname{erf}(x)$ for large $x$ loses all significant digits to cancellation. The complementary error function must therefore be computed via a dedicated approximation (the Abramowitz and Stegun rational approximation, formula 7.1.26, with maximum absolute error below $1.5 \times 10^{-7}$) rather than by subtraction from 1.

**Binomial coefficient precision.** For integer arguments, the multiplicative recurrence $\binom{n}{k} = \prod_{i=0}^{k-1} \frac{n-i}{i+1}$ avoids computing large intermediate factorials but accumulates floating-point drift over $k$ multiplications. A final `Math.round` corrects this drift, since the true result is always an integer. For large $n$ and $k$ near $n/2$ (where $\binom{n}{k}$ is largest), the product form may itself overflow; the fallback route

$$\binom{n}{k} = \exp\bigl(\ln\Gamma(n+1) - \ln\Gamma(k+1) - \ln\Gamma(n-k+1)\bigr)$$

stays in log-space until the final exponentiation. The factorial lookup table precomputes all 171 representable values ($0!$ through $170!$) at module load; $171!$ overflows to `Infinity`.

### Implementation Context

Special functions are numerical primitives consumed by almost every statistical and scientific module, so accuracy and overflow resistance are paramount.

**Gamma via Lanczos.** The Lanczos approximation with g=7 and 9 coefficients delivers full double-precision accuracy (15 significant digits) in O(1) time. For z < 0.5, the reflection formula is applied first. The coefficients are hard-coded constants; do not recompute them at runtime.

**Log-Gamma to avoid overflow.** Direct Gamma computation overflows for arguments above approximately 171.6. Always provide a `logGamma` path that works in log-space: `0.5*ln(2*pi) + (z+0.5)*ln(t) - t + ln(Ag)`. The Beta function should be computed via `exp(logGamma(a) + logGamma(b) - logGamma(a+b))` to avoid intermediate overflow even when B(a,b) itself is representable.

**Error function.** The Abramowitz and Stegun rational approximation (formula 7.1.26) gives maximum absolute error below 1.5e-7. For `erfc(x)` with large x, compute the approximation directly rather than `1 - erf(x)` to avoid catastrophic cancellation when erf(x) is near 1.

**Factorial lookup table.** Precompute all 171 values (0! through 170!) into a `Float64Array` at module load. 171! overflows to Infinity. For log-factorial with large n, delegate to `logGamma(n + 1)`.

**Binomial coefficient.** For integer arguments use the multiplicative recurrence `result *= (n-i)/(i+1)` with a final `Math.round` to correct floating-point drift. This avoids computing large intermediate factorials. For real alpha (generalised binomial), use the same product form when k is small, or fall back to the log-Gamma route.

**Testing strategy.** Verify Gamma against known exact values: Gamma(1)=1, Gamma(0.5)=sqrt(pi), Gamma(n)=(n-1)!. Test log-Gamma at large arguments (z=1000) where direct Gamma overflows. Compare erf against scipy/MATLAB reference values at x = 0, 0.5, 1, 2, 5.

