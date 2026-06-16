<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Quantitative Trading Strategies — API Reference

This is the API reference for the TypeScript implementation of Quantitative Trading Strategies. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/quant/`

- `src/quant/portfolio.ts` — Mean-variance optimisation, tangency portfolio, efficient frontier
- `src/quant/factor-model.ts` — CAPM estimation, Fama–French three-factor model
- `src/quant/pairs-trading.ts` — Pairs trading signal generation
- `src/quant/kelly.ts` — Kelly criterion (discrete, continuous, fractional)
- `src/quant/momentum.ts` — Regime detection, time-series momentum signals

### Data Representation

Portfolio optimisation operates on the `number[]` type for weight and return vectors and `number[][]` for covariance matrices. The library uses row-major dense arrays. For production use with large universes ($n > 100$), `Float64Array` provides better cache locality and performance.

### API Preview

```typescript
// src/quant/portfolio.ts

/** Compute minimum-variance portfolio weights for a target return. */
function meanVarianceOptimal(
  expectedReturns: number[], covMatrix: number[][], targetReturn: number,
): { weights: number[]; risk: number; return_: number };

/** Compute the tangency (max Sharpe ratio) portfolio. */
function tangencyPortfolio(
  expectedReturns: number[], covMatrix: number[][], riskFreeRate: number,
): { weights: number[]; sharpe: number };

/** Compute points on the efficient frontier. */
function efficientFrontier(
  expectedReturns: number[], covMatrix: number[][], nPoints?: number,
): { returns: number[]; risks: number[]; weights: number[][] };

// src/quant/factor-model.ts

/** Estimate CAPM parameters (alpha, beta) via OLS regression. */
function estimateCAPM(
  assetReturns: number[], marketReturns: number[], riskFreeRate: number,
): { alpha: number; beta: number; rSquared: number };

// src/quant/kelly.ts

/** Kelly criterion for a discrete bet with win probability p and odds b. */
function kellyDiscrete(p: number, b: number): number;

/** Kelly criterion for log-normal returns. */
function kellyContinuous(mu: number, sigma2: number): number;

/** Fractional Kelly: fraction * full Kelly for risk reduction. */
function kellyFractional(p: number, b: number, fraction: number): number;
```

### Error Handling

- `meanVarianceOptimal` throws if $\Sigma$ is singular (determinant below $10^{-12}$) or if the target return is unreachable.
- `tangencyPortfolio` throws if all excess returns are zero (undefined tangency).
- `kellyDiscrete` returns zero (no bet) when the edge $bp - q$ is non-positive.
- Autocorrelation functions return `NaN` for lags exceeding $T/4$ (insufficient data).

### Dependencies

- `src/linear/` — matrix inversion and solve for portfolio optimisation
- `src/stats/regression.ts` — OLS for CAPM and factor model estimation
- `src/stats/covariance.ts` — covariance and correlation matrix computation

### Usage Examples

```typescript
import { meanVarianceOptimal, tangencyPortfolio } from 'evenwicht/quant/portfolio';
import { kellyDiscrete } from 'evenwicht/quant/kelly';

// Two-asset portfolio optimisation
const mu = [0.08, 0.12];
const cov = [[0.04, 0.006], [0.006, 0.09]];
const optimal = meanVarianceOptimal(mu, cov, 0.10);
// optimal.weights ≈ [0.4, 0.6], optimal.risk ≈ 0.21

// Kelly criterion: 60% win probability, 1:1 odds
const fraction = kellyDiscrete(0.6, 1.0);
// fraction = 0.2 (bet 20% of bankroll)
```

### Connections

This chapter synthesises nearly all preceding applied mathematics chapters into a single domain. It uses Chapter 12 (the mean-variance portfolio problem is a constrained quadratic programme), Chapter 15 (the sample covariance matrix is the fundamental input to portfolio optimisation), Chapter 17 (CAPM and Fama–French estimation are linear regressions; pairs trading spreads are regression residuals), Chapter 21 (momentum detection via autocorrelation; stationarity testing for spread trading), Chapter 22 (spectral analysis of return cycles via the Fourier transform), Chapter 24 (fractional differencing to achieve stationarity while preserving predictive signal) and Chapter 25 (all cash flows are discounted, all performance is risk-adjusted).

- **Constrained Optimisation** (Chapter 12): The mean-variance portfolio problem is the canonical application of Lagrange multipliers to a quadratic objective with linear equality constraints. The shadow price $\lambda_1$ measures the marginal variance cost of demanding additional expected return. Adding inequality constraints ($w_i \geq 0$) transforms the problem into a quadratic programme requiring KKT conditions.

- **Descriptive Statistics** (Chapter 15): The sample covariance matrix $\hat{\Sigma}$ is the primary input to portfolio optimisation. Estimation error in $\hat{\Sigma}$ propagates to weight instability. The correlation coefficient determines diversification benefit.

- **Regression** (Chapter 17): CAPM and Fama–French models are linear regressions. Alpha is the intercept, beta is the slope. Pairs trading hedge ratios are regression coefficients. Standard diagnostics (heteroscedasticity, residual autocorrelation) apply.

- **Time Series** (Chapter 21): Momentum detection relies on the ACF. Mean-reversion strategies exploit negative autocorrelation. The Dickey–Fuller test determines whether a spread is suitable for pairs trading. ARIMA forecasts generate expected-return signals.

- **Transforms** (Chapter 22): The periodogram detects cycles in returns. Spectral peaks correspond to calendar effects exploitable by systematic strategies.

- **Fractional Calculus** (Chapter 24): Fractional differencing provides intermediate transformation between raw prices and returns, preserving predictive memory while achieving stationarity.

- **Financial Mathematics** (Chapter 25): All performance measurement uses risk-adjusted returns. Compounding, present value and annualisation conventions underpin strategy evaluation.



### What Is Implemented vs. Documented Only

- [x] Mean-variance optimisation (analytical Lagrange multiplier solution)
- [x] Tangency portfolio computation
- [x] Efficient frontier tracing
- [x] CAPM and Fama–French regression wrappers
- [x] Pairs trading signal generation with rolling z-score
- [x] Kelly criterion (discrete and continuous)
- [x] Momentum regime detection from ACF
- [ ] Shrinkage covariance estimation (deferred)
- [ ] Transaction cost modelling (deferred)
- [ ] Black–Litterman model (deferred)

---
### Implementation Context

**Design decisions.** Portfolio optimisation uses the analytical Lagrange multiplier solution (Algorithm 6.1) rather than a general-purpose QP solver, yielding exact weights in $O(n^3)$ dominated by matrix inversion. The covariance matrix inverse $\Sigma^{-1}$ is precomputed once and reused across multiple target returns when tracing the efficient frontier. Weight vectors use `number[]` for small universes; `Float64Array` is recommended for $n > 100$.

**Numerical pitfalls.** The sample covariance matrix is ill-conditioned when the number of assets approaches or exceeds the number of observations ($n \geq T$); condition numbers above $10^4$ amplify estimation error in $\Sigma^{-1}\boldsymbol{\mu}$ by a factor of $10^4$. The singularity check (determinant below $10^{-12}$) catches degenerate cases but does not address near-singularity. Shrinkage estimation (Ledoit-Wolf) is documented but deferred. Portfolio weights are renormalised after computation to enforce $\mathbf{w}'\mathbf{1} = 1$ at machine precision.

**Kelly sensitivity.** The continuous Kelly fraction $f^* = \mu/\sigma^2$ is extremely sensitive to estimation error in $\mu$: a 50% overestimate of $\mu$ produces a 50% overestimate of position size. Fractional Kelly ($\kappa f^*$ with $\kappa \in [0.25, 0.5]$) sacrifices roughly 25% of growth rate for substantially reduced drawdown risk.

**Performance.** Mean-variance optimisation is $O(n^3)$. Efficient frontier tracing is $O(n^3 + kn^2)$ for $k$ target returns. Pairs trading signal generation is $O(TL)$ for lookback $L$, reducible to $O(T)$ with online variance updates. Autocorrelation for momentum detection is $O(TH)$ for maximum lag $H$.

**Testing.** Two-asset portfolios are tested against hand-computed weights. The tangency portfolio is verified to maximise the Sharpe ratio compared to a grid of alternative weights. Kelly fractions are tested at boundary conditions: zero edge ($bp = q$) returns zero; certainty ($p = 1$) returns $1/b$. CAPM beta is cross-checked against the correlation-based formula $\beta = \rho \sigma_a / \sigma_m$.

