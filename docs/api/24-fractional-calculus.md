<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Fractional Calculus — API Reference

This is the API reference for the TypeScript implementation of Fractional Calculus. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/fractional/gl.ts` — Grünwald–Letnikov weights and fractional derivative approximation
- `src/fractional/difference.ts` — fractional differencing operator $(1-L)^d$ for time series
- `src/fractional/rl.ts` — Riemann–Liouville fractional integral and power-function derivative

### Data Representation

Fractional differencing operates on `number[]` time series. The Grünwald–Letnikov weights are computed via a stable recurrence relation and stored in `number[]`. The Riemann–Liouville fractional integral accepts a callable function `(t: number) => number` and evaluates it on a uniform grid. Gamma function evaluations use the `evenwicht/core/special` module.

### API Preview

```typescript
// src/fractional/

/**
 * Compute Grünwald–Letnikov weights via the recurrence
 * w_0 = 1, w_k = w_{k-1} * (1 - (alpha + 1) / k).
 *
 * @param alpha - Fractional order.
 * @param n - Number of weights to compute.
 * @returns Array of GL weights [w_0, w_1, ..., w_{n-1}].
 */
function glWeights(alpha: number, n: number): number[];

/**
 * Grünwald–Letnikov fractional derivative approximation.
 *
 * @param f - Function to differentiate.
 * @param alpha - Fractional order (alpha > 0).
 * @param x - Evaluation point.
 * @param h - Step size.
 * @param n - Number of terms in the GL sum.
 * @returns Approximation to D^alpha f(x).
 */
function glDerivative(
  f: (t: number) => number, alpha: number,
  x: number, h: number, n: number,
): number;

/**
 * Fractional differencing operator (1-L)^d applied to a time series.
 *
 * @param x - Input time series.
 * @param d - Differencing order (typically 0 < d < 1).
 * @returns Fractionally differenced series.
 */
function fractionalDifference(x: number[], d: number): number[];

/**
 * Truncated fractional difference with finite memory window.
 *
 * @param x - Input time series.
 * @param alpha - Fractional differencing order.
 * @param window - Maximum number of lags (memory cutoff).
 * @returns Fractionally differenced series (truncated).
 */
function fractionalDifferenceTruncated(x: number[], alpha: number, window: number): number[];

/**
 * Riemann–Liouville fractional derivative of x^beta (analytical).
 * Returns Gamma(beta+1) / Gamma(beta-alpha+1) * x^(beta-alpha).
 */
function rlPowerDerivative(alpha: number, beta: number, x: number): number;

/**
 * Numerical Riemann–Liouville fractional integral via product trapezoidal rule.
 */
function rlFractionalIntegral(
  f: (t: number) => number, alpha: number,
  a: number, x: number, n: number,
): number;
```

### Error Handling

- `glWeights` throws if `n < 1` or `alpha` is not finite.
- `fractionalDifference` with `d = 0` returns the original series unchanged; with integer `d` it reduces to standard differencing.
- `rlPowerDerivative` uses log-Gamma arithmetic (`lnGamma`) to avoid overflow for large arguments.
- `rlFractionalIntegral` omits the singular endpoint `t = x` when `0 < alpha < 1` to handle the kernel singularity $(x - t)^{\alpha - 1}$.
- The GL approximation converges at rate $O(h)$ for $C^1$ functions; the truncated variant introduces a controlled bias bounded by the tail sum of the weights.

### Dependencies

- `src/core/special.ts` — `gamma`, `logGamma` for GL weights and RL kernel evaluation
- `src/discrete/shift.ts` — shift operator for the fractional differencing implementation

### Usage Examples

```typescript
import { glWeights, fractionalDifference, rlPowerDerivative } from 'evenwicht/fractional';

// GL weights for order d = 0.5, first 5 terms
const w = glWeights(0.5, 5);
// w ≈ [1, -0.5, -0.125, -0.0625, -0.0391]

// Fractional differencing of a time series (preserves memory, removes trend)
const prices = [100, 102, 101, 105, 107, 110, 108];
const diffed = fractionalDifference(prices, 0.4);

// Analytical: D^0.5 of x^2 = Gamma(3)/Gamma(2.5) * x^1.5
rlPowerDerivative(0.5, 2, 4.0);  // ≈ 2*Gamma(3)/Gamma(2.5) * 4^1.5
```

### Connections

This chapter builds on Chapter 2 (the Gamma function provides the key interpolation), Chapter 4 (extending the derivative operator beyond integers), Chapter 5 (the Riemann–Liouville integral generalises iterated integration), Chapter 20 (the Grünwald–Letnikov definition generalises finite differences) and Chapter 23 (fractional powers of the differentiation operator). It connects forward to Chapter 21 (Time Series) through ARFIMA models and fractional differencing in finance.

- **Special Functions** (Ch. 2): The Gamma function $\Gamma(z)$ is the interpolation mechanism that extends factorial to real arguments, enabling every definition in this chapter. The Beta function appears in the proof of the semigroup property (Theorem 24.9) and the RL derivative of power functions (Theorem 24.8). The Mittag–Leffler function $E_\alpha(z)$ (Exercise 7.8) generalises the exponential and is the eigenfunction of the Caputo derivative.

- **Differential Calculus** (Ch. 4): The ordinary derivative $D^n$ is the integer-order special case of fractional differentiation. The limit-of-difference-quotient definition of $D^1$ generalises directly to the Grünwald–Letnikov definition of $D^\alpha$.

- **Integral Calculus** (Ch. 5): The Cauchy formula for iterated integration is the starting point for the Riemann–Liouville fractional integral (Definition 24.6). The convolution structure of the RL integral connects to the convolution theorem of Chapter 5.

- **Discrete Operators** (Ch. 20): The lag operator $L$ and the difference operator $\Delta = 1 - L$ are the discrete analogues of integration and differentiation. The fractional difference operator $(1-L)^d$ (Definition 24.15) generalises $\Delta^n$ to non-integer $d$, providing the bridge between fractional calculus and time series analysis.

- **Operator Algebra** (Ch. 23): Fractional calculus extends the operator algebra framework by defining $D^\alpha$ for non-integer $\alpha$. The semigroup property $D^\alpha \circ D^\beta = D^{\alpha+\beta}$ (Theorem 24.9 for integrals; extended to derivatives under regularity conditions via Theorem 24.12) is the composition law that makes $\{D^\alpha\}$ a one-parameter family of operators.

- **Time Series** (Ch. 21): ARFIMA models use the fractional difference operator $(1-L)^d$ to capture long memory. The fractional differencing parameter $d$ is estimated from data and determines the rate of autocorrelation decay. The GL weights provide the computational mechanism for fractional differencing.

- **Financial Mathematics** (Ch. 25): Fractional Brownian motion with Hurst exponent $H \neq 1/2$ models long-range dependence in asset returns. The connection $d = H - 1/2$ links the ARFIMA parameter to the self-similarity exponent.



### What Is Implemented vs. Documented Only

- [x] Grünwald–Letnikov fractional difference weights via recurrence
- [x] Grünwald–Letnikov fractional derivative approximation for arbitrary order
- [x] Fractional differencing operator (1-L)^d for time series
- [x] Riemann–Liouville derivative of power functions (analytical formula via Gamma function)
- [ ] Caputo fractional derivative numerical evaluation (documented; deferred to a future release)
- [ ] Mittag–Leffler function evaluation (documented in exercises; not implemented)
- [ ] Fractional ODE solvers (out of scope; the chapter focuses on the differencing operator)
- [ ] ARFIMA model fitting (documented in connections to Chapter 21; fitting deferred to the time series module)

---


### Implementation Context

(Implementation details are integrated into the Algorithms section above, which covers both the mathematical algorithms and their library API.)
