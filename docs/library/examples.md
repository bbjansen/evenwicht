<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Examples

Short, self-contained examples that show how the library modules work
together. Each example links to the theory chapter that explains the
mathematics behind it.

## Symbolic Differentiation

Build an expression tree, differentiate it symbolically, then evaluate the
result at a point. See [Chapter 1](../domains/01-expressions.md) for
expression trees and [Chapter 4](../domains/04-differential-calculus.md)
for differentiation rules.

```typescript
import { expr, diff, evaluate } from "evenwicht";

const f = expr.add(
  expr.pow(expr.var("x"), expr.const(2)),
  expr.mul(expr.const(3), expr.var("x")),
);

const df = diff(f, "x");
evaluate(df, { x: 2.0 }); // 7.0
```

## Eigenvalue Decomposition

Compute the eigenvalues and eigenvectors of a symmetric matrix. See
[Chapter 10](../domains/10-eigenvalues.md) for the theory and
[Chapter 9](../domains/09-matrices.md) for matrix representation.

```typescript
import { matrix, eigen } from "evenwicht";

const A = matrix.from([
  [4, 1],
  [1, 3],
]);

const { values, vectors } = eigen.decompose(A);
// values: [3.618, 2.382] (to 3 d.p.)
```

## Hypothesis Testing

Run a two-sample t-test to compare two group means. See
[Chapter 16](../domains/16-statistical-inference.md) for the statistical
theory and [Chapter 14](../domains/14-distributions.md) for the
t-distribution.

```typescript
import { stats } from "evenwicht";

const control = [5.1, 4.8, 5.3, 5.0, 4.9];
const treatment = [5.5, 5.7, 5.4, 5.8, 5.6];

const result = stats.tTest(control, treatment);
// { t: -3.87, df: 8, pValue: 0.0048 }
```

## ODE Integration

Solve a first-order ODE using the RK4 method. See
[Chapter 19](../domains/19-odes.md) for the Runge–Kutta algorithm and
error analysis.

```typescript
import { dynamics } from "evenwicht";

// dy/dt = -2y, y(0) = 1  →  exact solution: y = e^{-2t}
const solution = dynamics.solveODE(
  (t, y) => -2 * y,
  { t0: 0, y0: 1, tEnd: 3, stepSize: 0.01 },
);

solution.at(1.0); // 0.1353 (≈ e^{-2})
```

## Portfolio Optimisation

Compute the minimum-variance portfolio for a set of assets. See
[Chapter 11](../domains/11-unconstrained-optimization.md) for
optimisation and [Chapter 15](../domains/15-descriptive-statistics.md)
for the covariance matrix.

```typescript
import { optimize, stats } from "evenwicht";

const returns = [
  [0.02, 0.01, 0.03],  // asset A
  [0.01, 0.04, 0.02],  // asset B
  [0.03, 0.02, 0.01],  // asset C
];

const cov = stats.covarianceMatrix(returns);
const weights = optimize.minVariancePortfolio(cov);
// weights: [0.40, 0.33, 0.27] (subject to sum = 1)
```
