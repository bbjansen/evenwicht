<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Sequences & Discrete Operators — API Reference

This is the API reference for the TypeScript implementation of Sequences & Discrete Operators. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/discrete/sequence.ts` — `Sequence` type, factory functions (geometric, arithmetic, impulse, step)
- `src/discrete/shift.ts` — shift/lag operator with configurable boundary treatment
- `src/discrete/difference.ts` — first, second and $n$th-order difference operators
- `src/discrete/convolution.ts` — direct (quadratic) convolution

### Data Representation

The discrete operators module uses the following structure:

- **`src/discrete/sequence.ts`** — The `Sequence` type representing a finite discrete sequence as an array of numbers with an optional start index. Factory functions for common sequences: geometric, arithmetic, impulse, step.
- **`src/discrete/shift.ts`** — Implementation of the shift/lag operator $L^k$. Handles both forward and backward shifts with configurable boundary treatment (zero-padding, periodic, or truncation).
- **`src/discrete/difference.ts`** — First difference, second difference and general $n$th-order difference via the binomial expansion. Returns a new sequence of appropriate length.
- **`src/discrete/convolution.ts`** — Direct (quadratic) convolution. The FFT-based $O(n \log n)$ variant is documented but deferred until the Fourier module (Chapter 22) is available.

### API Preview

```typescript
// src/discrete/sequence.ts
function sequence(data: number[]): number[];
function geometric(ratio: number, length: number): number[];
function impulse(length: number): number[];

// src/discrete/shift.ts
function shift(x: number[], k: number): number[];

// src/discrete/difference.ts
function difference(x: number[]): number[];
function nthDifference(x: number[], n: number): number[];

// src/discrete/convolution.ts
function convolve(f: number[], g: number[]): number[];
```

### Error Handling

- **`shift`**: throws if the input sequence is empty. Returns a zero-padded sequence of the same length.
- **`difference`**: throws if the sequence has fewer than 2 elements (first difference) or fewer than $n+1$ elements ($n$th difference).
- **`convolve`**: throws if either input is empty. Returns a sequence of length $M + N - 1$.

### Dependencies

- No external module dependencies; operates on plain `number[]` arrays
- Used by: `src/timeseries/` (ACF computation), `src/operators/shift_operator.ts`, `src/transforms/` (time-domain convolution)

### Usage Examples

```typescript
import { sequence, geometric, shift, difference, convolve } from 'evenwicht/discrete';

// Create and shift a sequence
const x = sequence([10, 20, 30, 40, 50]);
shift(x, 1);   // [0, 10, 20, 30, 40]  (lag by 1)

// Differences of a quadratic sequence
const quad = sequence([1, 4, 9, 16, 25]);
difference(quad);           // [3, 5, 7, 9]
difference(difference(quad)); // [2, 2, 2]

// Polynomial multiplication via convolution
convolve([1, 2, 3], [1, 1, 1, 1]);  // [1, 3, 6, 6, 5, 3]
```

### Connections

This chapter builds on Chapter 6 (the geometric series and power series provide the generating-function viewpoint) and Chapter 18 (difference equations are the primary application of the operators developed here). It is used by Chapter 21 (Time Series; the lag operator $L$ is the central algebraic tool for ARMA models), Chapter 23 (Operator Algebra; the shift and difference operators become elements of an operator ring, and their formal power series are the bridge between discrete and continuous) and Chapter 24 (Fractional Calculus; the binomial expansion of $(1-L)^d$ for non-integer $d$ defines fractional differencing, the basis of ARFIMA models).

- **Series & Approximation** (Chapter 6): The generating function $F(x) = \sum f_t x^t$ is a power series whose convergence theory (radius of convergence, absolute convergence) is covered in Chapter 6. The $Z$-transform is a Laurent series whose convergence analysis uses the same tools. The geometric series formula $1/(1-r) = \sum r^k$ for $|r| < 1$ is the prototype for all operator inversions $(1 - \phi L)^{-1} = \sum \phi^k L^k$.

- **Difference Equations** (Chapter 18): Every linear constant-coefficient difference equation is a polynomial in $L$ applied to the unknown sequence. The operators of this chapter provide the algebraic language; Chapter 18 provides the solution theory. The characteristic equation of a difference equation is literally the operator polynomial evaluated as a function of $z$ (the $Z$-transform variable).

- **Time Series** (Chapter 21): ARMA models are rational functions of $L$: $\phi(L) y_t = \theta(L) \varepsilon_t$, where $\phi(L) = 1 - \phi_1 L - \cdots - \phi_p L^p$ and $\theta(L) = 1 + \theta_1 L + \cdots + \theta_q L^q$. The lag operator notation compresses the specification and enables algebraic manipulation (invertibility conditions, stationarity conditions, spectral density computation).

- **Operator Algebra** (Chapter 23): The shift operator $L$, the difference operator $\Delta = 1 - L$ and the derivative $D$ are all elements of an operator algebra. The formal identity $L^{-1} = e^D$ (in the continuous limit) connects the discrete and continuous frameworks. Chapter 23 develops this into a rigorous algebraic theory.

- **Fractional Calculus** (Chapter 24): The fractional difference $(1 - L)^d$ for non-integer $d \in (0, 1)$ is defined by the binomial series expansion of Theorem 20.11, extended to non-integer $n$ via generalised binomial coefficients (Definition 2.21). This is the foundation of ARFIMA (AutoRegressive Fractionally Integrated Moving Average) models for long-memory processes.



### What Is Implemented vs. Documented Only

- [x] Sequence representation with start index and array storage
- [x] Shift operator (forward and backward, arbitrary $k$)
- [x] First difference and second difference (optimised single-pass)
- [x] $n$th-order difference via binomial coefficients
- [x] Direct discrete convolution $O(MN)$
- [ ] FFT-based convolution $O(n \log n)$ (deferred to Chapter 22 infrastructure)
- [ ] $Z$-transform evaluation at specific $z$ (documented, not needed for core operations)
- [ ] Summation operator (formal inverse of $\Delta$, implemented as cumulative sum)

---
### Implementation Context

**Data structures.** Sequences are plain `number[]` arrays rather than a wrapper class, keeping interop with the rest of the library simple. The shift operator returns a new array of the same length with zero-padding at boundaries, avoiding index gymnastics for the caller.

**Algorithm choices.** First and second differences use dedicated single-pass implementations rather than composing generic `nthDifference`, saving one intermediate allocation and halving the number of passes over the data. The $n$th-order difference uses the binomial expansion (Algorithm 6.3) with precomputed coefficients via the stable recurrence $\binom{n}{k+1} = \binom{n}{k}(n-k)/(k+1)$, avoiding factorial overflow for $n > 20$. Direct convolution is $O(MN)$; the FFT-based $O(n \log n)$ variant is deferred until the Fourier module (Chapter 22) is available.

**Numerical pitfalls.** Higher-order differences amplify noise by a factor of $2^n$ in the binomial coefficients' absolute sum. Differences above order 3 on empirical data should be used with caution. For large $n$ (above 66), binomial coefficients overflow 64-bit integers; the floating-point recurrence introduces small rounding errors in the coefficients. Convolution of long sequences with mixed-sign values is susceptible to catastrophic cancellation in the inner-product accumulation; Kahan summation can be applied at minimal cost.

**Performance.** Shift is $O(N)$. First/second difference is $O(N)$. The $n$th difference is $O(Nn)$. Direct convolution is $O(MN)$; for $M + N > 64$, the deferred FFT path would reduce this to $O((M+N)\log(M+N))$.

**Testing.** Differences of polynomial sequences verify that $\Delta^{n+1}$ of a degree-$n$ polynomial is zero. Convolution is tested as polynomial multiplication against direct algebraic expansion. Shift round-trips ($\text{shift}(x, k)$ followed by $\text{shift}(\cdot, -k)$) verify that the interior elements are preserved.

