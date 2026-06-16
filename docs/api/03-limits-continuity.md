<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Limits & Continuity — API Reference

This is the API reference for the TypeScript implementation of Limits & Continuity. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/numeric/limit.ts` — numerical limit evaluation via successive approximation
- `src/numeric/bisect.ts` — bisection root-finder (IVT-based)

### Data Representation

Both functions operate on plain JavaScript functions `(x: number) => number`. Results are returned as structured objects (`LimitResult`, `BisectResult`) containing the computed value, convergence status and diagnostic information.

### Scope

Evenwicht does not include a symbolic limit engine. Symbolic limit computation requires pattern-matching, algebraic simplification and series expansion capabilities outside the current scope. A partial symbolic engine that handles some cases but fails unpredictably on others would be worse than none at all.

What the library provides:

1. **Numerical limit evaluation**: a utility that evaluates $f$ at points approaching $a$ and reports whether the sequence of values converges.
2. **Bisection root-finder**: an implementation of the IVT-based bisection algorithm.

These are pure numerical tools: they operate on JavaScript functions `(x: number) => number`, not on `Expr` trees.

### Browser vs Node

Both `evaluateLimit` and `bisect` are pure functions with no platform dependencies. They use only `Math` built-ins and basic arithmetic, running identically in Node.js and browsers.

### API Preview

```typescript
// Numerical limit evaluation — src/numeric/limit.ts
interface LimitResult {
  converged: boolean;
  value?: number;
  reason?: string;
}

/** Evaluate a limit numerically by successive approximation toward a. */
function evaluateLimit(
  f: (x: number) => number,
  a: number,
  options?: {
    direction?: 'left' | 'right' | 'both';
    steps?: number;
  }
): LimitResult;
```

```typescript
// Bisection root-finder — src/numeric/bisect.ts
interface BisectResult {
  root: number;
  iterations: number;
  bracketSize: number;
}

/**
 * Find a root of f on [a, b] using the bisection method.
 * Requires f(a) and f(b) to have opposite signs (IVT guarantee).
 */
function bisect(
  f: (x: number) => number,
  a: number,
  b: number,
  options?: {
    tolerance?: number;
    maxIterations?: number;
  }
): BisectResult;
```

### Error Handling

- `evaluateLimit` does not throw. Non-finite samples result in `converged: false`.
- `bisect` throws if $f(a) \cdot f(b) \ge 0$ or $a \ge b$. It returns the best bracket found even if `maxIterations` is reached.

### Dependencies

- No external module dependencies; both are self-contained numerical utilities
- Used by: `src/optimization/` (root-finding in Newton's method), `src/financial/` (IRR solver uses bisection as fallback)

### Usage Examples

```typescript
import { evaluateLimit } from 'evenwicht/numeric';
import { bisect } from 'evenwicht/numeric';

// Evaluate limit of sin(x)/x as x -> 0
const lim = evaluateLimit((x) => Math.sin(x) / x, 0);
// lim.converged === true, lim.value ≈ 1.0

// One-sided limit: limit of 1/x as x -> 0 from the right
const rightLim = evaluateLimit((x) => 1 / x, 0, { direction: 'right' });
// rightLim.converged === false (diverges to Infinity)

// Find root of x^3 - 2 on [1, 2]
const root = bisect((x) => x ** 3 - 2, 1, 2);
// root.root ≈ 1.2599 (cube root of 2)
```

### Connections

This chapter is used by Chapter 4 (Differential Calculus), where the derivative is defined as a limit and Chapter 5 (Integral Calculus), where the Riemann integral is defined as a limit of sums. It builds on Chapter 1 (Expressions & Functions). The IVT motivates the bisection root-finding algorithm, which appears in numerical methods throughout the library. Series convergence (Chapter 6) relies on limits of sequences.

- **Differential Calculus** (Chapter 4): The derivative is *defined* as a limit: $f'(a) = \lim_{h \to 0} \frac{f(a+h) - f(a)}{h}$. Every theorem about derivatives ultimately rests on the limit laws from this chapter. The proof that differentiability implies continuity is a direct application of the limit definition. L'Hôpital's rule, stated here as Theorem 3.17, is proved in Chapter 4 using the Mean Value Theorem.

- **Integral Calculus** (Chapter 5): The Riemann integral is defined as the limit of Riemann sums: $\int_a^b f(x)\,dx = \lim_{\|P\| \to 0} \sum f(x_i^*) \Delta x_i$. The Fundamental Theorem of Calculus connects this limit to antidifferentiation, creating the bridge between Chapters 4 and 5.

- **Series & Approximation** (Chapter 6): An infinite series $\sum_{n=1}^\infty a_n$ converges if and only if its sequence of partial sums $S_N = \sum_{n=1}^N a_n$ has a limit as $N \to \infty$. Every convergence test (ratio, root, comparison) is a criterion for the existence of this limit.

- **Unconstrained Optimisation** (Chapter 11): The IVT motivates root-finding algorithms (bisection, Newton's method). The EVT guarantees that a continuous function on a closed bounded set has a maximum and minimum, which is the theoretical foundation for optimisation on compact domains.



### What Is Implemented vs. Documented Only

- [x] Numerical limit evaluation by successive approximation (`evaluateLimit`)
- [x] Bisection root-finder (`bisect`)
- [ ] Symbolic limit computation (out of scope — requires CAS capabilities)
- [ ] Newton's method for root-finding (documented in Chapter 11, Unconstrained Optimisation)
- [ ] Brent's method for root-finding (deferred — faster than bisection, same reliability)
### Numerical Considerations

Limit evaluation and bisection are thin numerical routines whose primary challenge is floating-point behaviour near the target point, not algorithmic complexity. Both algorithms operate at the boundary of representable precision, where the gap between adjacent floating-point numbers becomes the limiting factor.

**Cancellation near the limit point.** The successive approximation algorithm samples $f$ at $a \pm 10^{-i}$ for $i = 1, \ldots, k$ (default $k = 12$). As $h = 10^{-i}$ shrinks below roughly $10^{-8}$, two problems arise: first, $a + h$ may round to $a$ in double precision when $|a| \gg h$ (since the spacing between adjacent doubles near $a$ is $|a| \cdot \varepsilon_{\text{mach}} \approx |a| \cdot 2.2 \times 10^{-16}$); second, the subtraction $f(a+h) - f(a-h)$ loses significant digits to cancellation. The algorithm therefore caps the number of steps rather than driving $h$ to zero and reports non-convergence when the last two samples still disagree. For oscillatory functions such as $\sin(1/x)$ near $x = 0$, the method correctly reports non-convergence because successive samples do not stabilise.

**Bisection convergence and midpoint computation.** Bisection converges linearly, gaining one bit of accuracy per iteration. The number of iterations required for tolerance $\tau$ is

$$k = \left\lceil \log_2\!\left(\frac{b - a}{\tau}\right) \right\rceil$$

For the default tolerance $\tau = 10^{-10}$ on a unit interval, this gives $k = 34$ iterations. The midpoint is computed as $a + (b-a)/2$ rather than $(a+b)/2$ to avoid overflow when $a$ and $b$ are large numbers of the same sign (e.g., $a = 10^{200}$, $b = 10^{200} + 1$ would overflow in the sum). Bisection is unconditionally stable: it cannot diverge, skip over roots, or produce iterates outside the bracket. This makes it the safest root-finder when derivative information is unavailable, at the cost of slower convergence compared to Newton's method (Chapter 11) or Brent's method.

**When limit evaluation fails.** The successive approximation method is a heuristic, not a guaranteed algorithm. It fails for functions with essential singularities (e.g., $e^{1/x}$ near $x = 0$), oscillatory limits ($\sin(1/x)$), and targets at infinity. It also cannot distinguish a true limit of zero from a function that happens to pass through zero at the sampled points. For rigorous limit computation, symbolic methods (not implemented in this library) are required.

### Implementation Context

Limit evaluation and bisection are thin numerical routines whose main challenge is floating-point behaviour near the target point, not algorithmic complexity.

**Successive approximation for limits.** The evaluator samples $f$ at $a \pm 10^{-i}$ for $i = 1 \ldots k$ (default $k = 12$). This geometric spacing is deliberate: it covers twelve orders of magnitude while keeping the number of evaluations constant. Convergence is declared when successive values agree to machine-epsilon scale. The method fails for oscillatory functions ($\sin(1/x)$ near 0) and for targets at infinity, where the sampling direction must be reversed.

**Bisection guarantees.** Bisection is chosen over Newton/secant methods because it requires only a sign-change bracket and no derivative information. It converges linearly at one bit per iteration, needing $\lceil\log_2((b - a)/\tau)\rceil$ steps for tolerance $\tau$. The midpoint is computed as $a + (b - a)/2$ rather than $(a + b)/2$ to avoid overflow when $a$ and $b$ are large and of the same sign.

**Testing strategy.** Limits: verify $\lim_{x \to 0} \sin(x)/x = 1$, one-sided limits of $1/x$ and non-convergent cases ($\sin(1/x)$). Bisection: check $\cos$ root at $\pi/2$, verify iteration count matches $\lceil\log_2(\text{interval}/\text{tol})\rceil$ and confirm the sign-change precondition throws when violated.

