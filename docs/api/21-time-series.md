<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Time Series Analysis — API Reference

This is the API reference for the TypeScript implementation of Time Series Analysis. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/timeseries/`

- `src/timeseries/autocorrelation.ts` — Sample ACF, PACF, cross-correlation
- `src/timeseries/smoothing.ts` — SES, Holt's method, Holt–Winters
- `src/timeseries/arima.ts` — AR/MA/ARMA/ARIMA model fitting
- `src/timeseries/forecast.ts` — Point forecasts and prediction intervals

### Data Representation

All time series are represented as `Float64Array` with observations in temporal order. Model fitting functions return structured result objects containing coefficients, diagnostics and residuals. The PACF computation uses the Durbin–Levinson recursion, exploiting the Toeplitz structure of the autocovariance matrix for $O(p^2)$ complexity.

### API Preview

```typescript
// src/timeseries/autocorrelation.ts
function acf(data: Float64Array, maxLag: number): Float64Array;
function pacf(data: Float64Array, maxLag: number): Float64Array;
function crossCorrelation(x: Float64Array, y: Float64Array, maxLag: number): Float64Array;

// src/timeseries/smoothing.ts
function ses(data: Float64Array, alpha?: number): { fitted: Float64Array; alpha: number };
function holt(data: Float64Array, alpha?: number, beta?: number): {
  fitted: Float64Array; level: Float64Array; trend: Float64Array;
  alpha: number; beta: number;
};
function holtWinters(data: Float64Array, period: number, opts?: {
  alpha?: number; beta?: number; gamma?: number; multiplicative?: boolean;
}): { fitted: Float64Array; forecast: (h: number) => Float64Array };

// src/timeseries/arima.ts
function fitAR(data: Float64Array, order: number): {
  coefficients: Float64Array; sigma2: number; aic: number;
};
function fitARIMA(data: Float64Array, order: [number, number, number]): {
  ar: Float64Array; ma: Float64Array; sigma2: number; residuals: Float64Array;
};

// src/timeseries/forecast.ts
function forecast(model: ARIMAModel, h: number): {
  point: Float64Array;
  lower: Float64Array;   // 95% lower prediction interval
  upper: Float64Array;   // 95% upper prediction interval
  se: Float64Array;      // forecast standard errors
};
```

### Error Handling

- `acf` uses divisor $n$ (not $n - h$) to guarantee a positive semidefinite autocovariance matrix, consistent with the Box–Jenkins convention.
- `ses`, `holt` and `holtWinters` optimise smoothing parameters automatically when not supplied, using Brent's method (univariate) or Nelder–Mead (multivariate) to minimise SSE.
- `fitAR` warns if the fitted model is non-stationary (characteristic roots inside the unit circle).
- `fitARIMA` applies differencing of order `d` before fitting the ARMA(p, q) component.
- `NaN` values in input series trigger pairwise deletion in autocovariance estimates, with a warning when more than 10% of pairs are incomplete.

### Dependencies

- `src/stats/descriptive.ts` — `mean`, `variance` for detrending and normalisation
- `src/optimization/unconstrained.ts` — Brent's method / Nelder–Mead for smoothing parameter optimisation
- `src/stats/distributions.ts` — normal distribution for prediction intervals

### Usage Examples

```typescript
import { acf, pacf, ses, fitAR, forecast } from 'evenwicht/timeseries';

// Compute ACF of a time series
const data = new Float64Array([1.2, 1.5, 1.3, 1.8, 1.6, 2.0, 1.9, 2.3]);
const r = acf(data, 5);  // autocorrelation at lags 0..5

// Simple exponential smoothing
const smooth = ses(data, 0.3);
// smooth.fitted contains the smoothed series

// Fit AR(2) model
const arResult = fitAR(data, 2);
// arResult.coefficients: [phi_1, phi_2]
// arResult.aic: Akaike information criterion
```

### Connections

This chapter is used by Chapter 22 (Transforms: the spectral density is the Fourier transform of the autocovariance function; frequency-domain methods provide an alternative characterisation of ARMA processes). It builds on Chapter 17 (autoregressive models are regressions of a variable on its own lags; the Yule–Walker equations are regression normal equations applied to the autocorrelation structure) and Chapter 20 (the lag operator $L$ and difference operator $\Delta$ provide the algebraic framework for expressing ARIMA models compactly). Chapter 24 (Fractional Calculus) extends the differencing operator to non-integer orders, yielding the ARFIMA class for long-memory processes.

- **Chapter 15 (Descriptive Statistics)**: The sample autocovariance $\hat{\gamma}(h)$ is a generalisation of the sample variance ($\hat{\gamma}(0) = s^2$ with divisor $n$ rather than $n-1$). The sample ACF $\hat{\rho}(h)$ is a generalisation of the Pearson correlation coefficient applied to a series and its own lagged copy. All the computational considerations of Chapter 15 (numerical stability, positive semidefiniteness) apply with additional complications arising from the sequential structure of time series data.

- **Chapter 17 (Regression)**: The Yule–Walker equations $R\boldsymbol{\phi} = \mathbf{r}$ are structurally identical to the normal equations $X'X\hat{\boldsymbol{\beta}} = X'\mathbf{y}$ of OLS regression (Theorem 17.6), with the autocorrelation matrix $R$ playing the role of the Gram matrix. An AR($p$) model is literally a regression of $X_t$ on its $p$ lagged values. The key difference is that time series regression violates the independence assumption of the classical linear model, requiring modified inference (the innovations are uncorrelated but the regressors $X_{t-1}, \ldots, X_{t-p}$ are random and correlated with past errors).

- **Chapter 20 (Discrete Operators)**: The lag operator $L$ and difference operator $\Delta = 1 - L$ developed in Chapter 20 provide the algebraic language of ARIMA models. The characteristic polynomial $\phi(z)$ is a polynomial in the lag operator. Stationarity is determined by the roots of this polynomial. The factorisation $(1-L)^d$ separates the non-stationary component from the stationary ARMA dynamics.

- **Chapter 22 (Transforms)**: The spectral density $f(\omega) = \frac{\sigma^2}{2\pi}\left|\frac{\theta(e^{-i\omega})}{\phi(e^{-i\omega})}\right|^2$ is the frequency-domain characterisation of an ARMA process. The autocovariance function and the spectral density form a Fourier transform pair: $\gamma(h) = \int_{-\pi}^{\pi}f(\omega)e^{ih\omega}\,d\omega$. Spectral analysis provides an alternative to the ACF/PACF for model identification, particularly useful for detecting hidden periodicities.

- **Chapter 24 (Fractional Calculus)**: The ARIMA framework restricts $d$ to integer values (typically 0, 1, or 2). The ARFIMA (Autoregressive Fractionally Integrated Moving Average) model generalises to $d \in \mathbb{R}$ (often $0 < d < 0.5$), capturing *long memory* processes whose ACF decays hyperbolically ($\rho(h) \sim Ch^{2d-1}$ as $h \to \infty$) rather than geometrically. The fractional difference operator $(1-L)^d$ for non-integer $d$ is defined via the binomial series, connecting to the fractional calculus of Chapter 24.



### What Is Implemented vs. Documented Only

- [x] Sample autocovariance and ACF computation (divisor n convention)
- [x] Sample PACF via Durbin–Levinson recursion
- [x] Cross-correlation function
- [x] Simple exponential smoothing (SES) with parameter optimisation
- [x] Holt's linear method (double exponential smoothing)
- [x] Holt–Winters method (additive and multiplicative)
- [x] AR model fitting via Yule–Walker equations
- [x] ARIMA model fitting (conditional MLE)
- [x] Multi-step-ahead point forecasts and prediction intervals
- [ ] GARCH / ARCH models for time-varying volatility (documented in historical context; deferred)
- [ ] Vector autoregression (VAR) for multivariate systems (out of scope for this chapter)
- [ ] Augmented Dickey–Fuller unit root test (documented; not implemented as a standalone function)
- [ ] Ljung–Box test for residual white noise (documented in Box–Jenkins methodology; deferred)

---


### Implementation Context

The Evenwicht library organises time series functionality across four modules:

- `src/timeseries/autocorrelation.ts` — sample ACF, sample PACF (Durbin–Levinson), cross-correlation
- `src/timeseries/smoothing.ts` — SES, Holt's method, Holt–Winters (additive and multiplicative)
- `src/timeseries/arima.ts` — AR/MA/ARMA/ARIMA model fitting (Yule–Walker, conditional MLE), model diagnostics
- `src/timeseries/forecast.ts` — point forecasts, prediction intervals, multi-step-ahead forecasting

The primary API operates on `Float64Array` for numerical precision:

Design decisions:

1. **Divisor convention.** The `acf` function uses divisor $n$ (not $n - h$) to guarantee positive semidefiniteness, consistent with Box–Jenkins convention and R's `acf()` function.

2. **Automatic parameter selection.** When smoothing parameters are not supplied, `ses`, `holt` and `holtWinters` optimise them by minimising the sum of squared one-step-ahead forecast errors (SSE) using Brent's method for univariate optimisation and Nelder–Mead for multivariate.

3. **Stationarity enforcement.** The `fitAR` function checks that the estimated model is stationary (all characteristic roots outside the unit circle) and issues a warning if not. The `fitARIMA` function applies differencing before fitting.

4. **Levinson–Durbin internally.** The `pacf` function and `fitAR` (Yule–Walker mode) use the Levinson–Durbin recursion (Algorithm 6.2) rather than general matrix inversion, exploiting the Toeplitz structure for $O(p^2)$ complexity.

5. **NaN handling.** Missing values (NaN) in the input series cause the affected autocovariance estimates to be computed from the available observations (pairwise deletion), with a warning when more than 10% of pairs are incomplete.
