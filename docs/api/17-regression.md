<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Regression & Econometrics — API Reference

This is the API reference for the TypeScript implementation of Regression & Econometrics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/stats/regression.ts`

- `src/stats/regression.ts` — OLS estimation (simple and multiple), R-squared, F-test
- `src/stats/diagnostics.ts` — VIF, Durbin-Watson, residual analysis
- `src/stats/restrictions.ts` — F-test for general linear restrictions (Wald form)

### Data Representation

The design matrix `X` is a `Matrix` object (from the Evenwicht linear algebra module) that must include the intercept column (column of ones). The response vector `y` is a `Float64Array`. Coefficient vectors, standard errors, residuals and fitted values are all `Float64Array`.

### API Preview

```typescript
// src/stats/regression.ts

interface RegressionResult {
  coefficients: Float64Array;      // beta_hat: (p+1) x 1
  standardErrors: Float64Array;    // SE(beta_hat_j)
  tStats: Float64Array;            // T_j = beta_hat_j / SE_j
  pValues: Float64Array;           // two-sided p-values from t(n-p-1)
  rSquared: number;
  adjustedRSquared: number;
  fStat: number;                   // overall F-statistic
  fPValue: number;
  residuals: Float64Array;         // e = y - X * beta_hat
  fitted: Float64Array;            // y_hat = X * beta_hat
}

/** OLS estimation via normal equations with Cholesky decomposition. */
function ols(X: Matrix, y: Float64Array): RegressionResult;

// src/stats/diagnostics.ts

/** Variance Inflation Factors for each non-intercept variable. */
function vif(X: Matrix): Float64Array;

/** Durbin-Watson statistic for first-order residual autocorrelation. */
function durbinWatson(residuals: Float64Array): number;

// src/stats/restrictions.ts

/** F-test for H0: R * beta = r (Wald form). */
function fTestRestriction(
  betaHat: Float64Array,
  s2: number,
  XtXInv: Matrix,
  R: Matrix,
  r: Float64Array,
  n: number,
  p: number,
): { fStat: number; pValue: number; df: [number, number] };
```

### Error Handling

- `ols` throws if `X` does not have full column rank (singular `X'X`), or if the number of rows in `X` does not match the length of `y`.
- `vif` throws if `X` has fewer than 3 columns (intercept plus at least 2 predictors required for meaningful VIF).
- `durbinWatson` throws if the residual vector has fewer than 3 elements.
- `fTestRestriction` throws if the restriction matrix `R` dimensions are incompatible with the coefficient vector.
- p-values are computed using the library's own t and F distribution CDFs (Chapter 14).

### Dependencies

- `src/linear/solve.ts` — normal equations via Cholesky decomposition
- `src/linear/matrix.ts` — `Matrix` type, `transpose`, `matrixMultiply`
- `src/stats/distributions.ts` — t and F distribution CDFs for p-values

### Usage Examples

```typescript
import { ols, vif, durbinWatson } from 'evenwicht/stats';
import { matrix } from 'evenwicht/linear';

// Simple linear regression: y = 2 + 3x (with noise)
const X = matrix(5, 2, new Float64Array([
  1, 1,  1, 2,  1, 3,  1, 4,  1, 5,
]));  // intercept column + x
const y = new Float64Array([5.1, 7.9, 11.2, 13.8, 17.1]);
const result = ols(X, y);
// result.coefficients ≈ [1.98, 3.04]
// result.rSquared ≈ 0.998

// Check for autocorrelation
durbinWatson(result.residuals);  // ≈ 2.0 (no autocorrelation)
```

### Connections

This chapter is used by Chapter 21 (Time Series; regression on lagged variables, autoregressive models, cointegration). It builds on Chapter 9 (the OLS estimator is a matrix formula requiring the inverse of the Gram matrix $X'X$), Chapter 11 (OLS minimises a convex unconstrained objective; the normal equations are the first-order condition $\nabla f = \mathbf{0}$) and Chapter 16 ($t$-tests and $F$-tests are the inferential machinery). The geometric interpretation of OLS as orthogonal projection connects directly to the linear algebra of Chapter 8 (inner products, orthogonality) and Chapter 9 (column spaces, projections). In applied work, regression underpins demand estimation, production function estimation, returns to education and treatment effect analysis.

- **Chapter 9 (Matrices)**: The OLS estimator $\hat{\boldsymbol{\beta}} = (X'X)^{-1}X'\mathbf{y}$ requires matrix multiplication, transposition and inversion. The hat matrix $H = X(X'X)^{-1}X'$ is an orthogonal projection matrix. The entire theory rests on the linear algebra of column spaces and projections.

- **Chapter 10 (Eigenvalues)**: The eigenvalues of $X'X$ determine the condition number and hence the numerical stability of OLS. When eigenvalues span many orders of magnitude, the problem is ill-conditioned (multicollinearity). Principal component analysis (PCA), which performs eigendecomposition of the correlation matrix of the predictors, is one remedy for multicollinearity: one can regress on the principal components instead of the original variables.

- **Chapter 11 (Unconstrained Optimisation)**: OLS minimises the convex function $\text{SSE}(\boldsymbol{\beta}) = (\mathbf{y} - X\boldsymbol{\beta})'(\mathbf{y} - X\boldsymbol{\beta})$. The normal equations $X'X\hat{\boldsymbol{\beta}} = X'\mathbf{y}$ are the first-order condition $\nabla \text{SSE} = \mathbf{0}$. Convexity guarantees the unique stationary point is the global minimum.

- **Chapter 12 (Constrained Optimisation)**: Testing linear restrictions $R\boldsymbol{\beta} = \mathbf{r}$ is equivalent to comparing the unrestricted OLS solution to the solution of a constrained optimisation problem. The restricted estimator can be obtained via Lagrange multipliers applied to the least squares objective with linear equality constraints.

- **Chapter 16 (Inference)**: The $t$-tests and $F$-tests of regression are special cases of the general hypothesis-testing framework: formulate null and alternative, compute a test statistic with a known distribution under the null and reject if the statistic falls in the critical region.

- **Chapter 21 (Time Series)**: Regression on lagged dependent variables ($y_t$ on $y_{t-1}, y_{t-2}, \ldots$) gives the autoregressive model. The Durbin–Watson statistic tests for serial correlation in regression residuals. Cointegration analysis (Engle–Granger) uses regression residuals to test for long-run equilibrium relationships.



### What Is Implemented vs. Documented Only

- [x] OLS estimation via the normal equations (simple and multiple regression)
- [x] Standard errors, t-statistics and p-values for individual coefficients
- [x] R-squared and adjusted R-squared
- [x] F-test for overall significance
- [x] F-test for general linear restrictions (Wald form)
- [x] Variance Inflation Factor (VIF) computation
- [x] Durbin–Watson statistic for residual autocorrelation
- [ ] QR decomposition or SVD-based OLS solver for ill-conditioned problems (documented in Section 7; deferred to a future release)
- [ ] Heteroscedasticity-robust standard errors (White, 1980) (documented but not implemented)
- [ ] Breusch–Pagan test for heteroscedasticity (documented but not implemented as a standalone function)
- [ ] Weighted least squares (WLS) and generalised least squares (GLS) (deferred)
- [ ] Instrumental variables / two-stage least squares (out of scope)

---


### Implementation Context

The Evenwicht library implements regression and diagnostics across the following source files:

- `src/stats/regression.ts` — simple linear regression and multiple OLS via the normal equations.
- `src/stats/diagnostics.ts` — VIF computation, Durbin–Watson statistic, residual analysis utilities.
- `src/stats/restrictions.ts` — $F$-test for general linear restrictions, Wald test.

The primary API surface:

**Import paths:**

Design decisions:

- `ols` expects the design matrix $X$ to already include the intercept column (column of ones). This gives the user full control over specification.
- `Float64Array` is used for all numeric vectors to ensure double-precision arithmetic throughout.
- The `Matrix` type is the library's standard matrix class from Chapter 9, supporting transpose, multiplication and solve operations.
- $p$-values are computed using the library's own $t$ and $F$ distribution CDFs (Chapter 14), avoiding external dependencies.
- The `vif` function runs $p$ auxiliary regressions internally, reusing the `ols` function.
- The `durbinWatson` function operates on a pre-computed residual vector and assumes the observations are in temporal order.
