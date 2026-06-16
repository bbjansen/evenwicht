<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Descriptive Statistics — API Reference

This is the API reference for the TypeScript implementation of Descriptive Statistics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/stats/descriptive.ts`, `src/stats/covariance.ts`, `src/stats/rank.ts`

### Data Representation

All functions operate on `Float64Array` for numerical precision and cache performance. The covariance and correlation matrix functions return a `Matrix` object from the Evenwicht linear algebra module. Weighted variants accept a parallel `Float64Array` of weights.

### API Preview

```typescript
// src/stats/descriptive.ts -- location, spread, shape
function mean(data: Float64Array): number;
function median(data: Float64Array): number;
function variance(data: Float64Array): number;       // Bessel-corrected (n-1)
function populationVariance(data: Float64Array): number; // denominator n
function std(data: Float64Array): number;
function skewness(data: Float64Array): number;
function kurtosis(data: Float64Array): number;        // excess kurtosis
function weightedMean(data: Float64Array, weights: Float64Array): number;
function weightedVariance(data: Float64Array, weights: Float64Array): number;

// src/stats/rank.ts -- quantiles and order statistics
function quantile(data: Float64Array, p: number): number;
function iqr(data: Float64Array): number;
function fiveNumberSummary(data: Float64Array): [number, number, number, number, number];

// src/stats/covariance.ts -- association measures
function covariance(x: Float64Array, y: Float64Array): number;
function correlation(x: Float64Array, y: Float64Array): number;
function covarianceMatrix(data: Float64Array[]): Matrix;
function correlationMatrix(data: Float64Array[]): Matrix;
```

### Error Handling

- `variance` and `std` return `NaN` for single-element arrays (degrees of freedom = 0).
- `correlation` returns `NaN` when either variable has near-zero variance (below `1e-15`), rather than overflowing.
- `quantile` throws if `p` is outside `(0, 1)`.
- `median` and `quantile` create an internal sorted copy; the input array is not modified.
- Functions propagate `NaN` if any input element is `NaN`.
- `variance` and `std` use Welford's online algorithm internally for numerical stability, avoiding catastrophic cancellation with large-mean data.

### Dependencies

- `src/linear/matrix.ts` -- `Matrix` type for covariance and correlation matrices
- Used by: `src/stats/regression.ts`, `src/ml/pca.ts`, `src/timeseries/`

### Usage Examples

```typescript
import { mean, variance, std, median, correlation, fiveNumberSummary } from 'evenwicht/stats';

const data = new Float64Array([2, 4, 4, 4, 5, 5, 7, 9]);

mean(data);        // 5.0
variance(data);    // ≈ 4.571 (Bessel-corrected)
std(data);         // ≈ 2.138
median(data);      // 4.5

fiveNumberSummary(data);  // [2, 4, 4.5, 5, 9]

// Correlation between two variables
const x = new Float64Array([1, 2, 3, 4, 5]);
const y = new Float64Array([2, 4, 5, 4, 5]);
correlation(x, y);  // ≈ 0.7746
```

### Connections

This chapter is used by Chapter 16 (Inference -- test statistics are functions of descriptive statistics; confidence intervals are built from the sample mean and sample variance), Chapter 17 (Regression -- the regression coefficients are ratios of covariances to variances; the $R^2$ statistic is the square of the sample correlation) and Chapter 21 (Time Series -- the autocorrelation function is a sequence of sample correlations at successive lags). The Cauchy–Schwarz inequality from Chapter 8 provides the proof that the correlation coefficient is bounded between $-1$ and $1$. The expectation and variance developed in Chapter 13 are the population quantities that the sample mean and sample variance estimate.

- **Chapter 13 (Probability)**: The sample mean $\bar{x}$ estimates the population mean $\mu = E[X]$. The sample variance $s^2$ estimates the population variance $\sigma^2 = \text{Var}(X)$. The sample correlation $r_{xy}$ estimates the population correlation $\rho_{XY} = \text{Cov}(X,Y)/(\sigma_X \sigma_Y)$. Every formula in this chapter has a population-level counterpart defined in Chapter 13; the descriptive statistics developed here are the empirical counterparts that make population-level concepts operational on finite data.

- **Chapter 16 (Inference)**: Test statistics are constructed from descriptive statistics. The one-sample $t$-statistic $t = (\bar{x} - \mu_0)/(s/\sqrt{n})$ is built from the sample mean and sample standard deviation. The $F$-statistic for comparing two variances is the ratio $s_1^2/s_2^2$. Confidence intervals for the mean take the form $\bar{x} \pm t_{\alpha/2} \cdot s/\sqrt{n}$. Without the descriptive statistics of this chapter, inference has no raw material to work with.

- **Chapter 17 (Regression)**: The ordinary least squares regression coefficient is $\hat{\beta} = s_{xy}/s_x^2$ -- the ratio of the sample covariance to the sample variance of the predictor. The coefficient of determination $R^2 = r_{xy}^2$ is the square of the sample correlation. The multiple regression coefficient vector is $\hat{\boldsymbol{\beta}} = S_{XX}^{-1}\mathbf{s}_{Xy}$, where $S_{XX}$ is the predictor covariance matrix and $\mathbf{s}_{Xy}$ is the vector of covariances between predictors and response. Regression is, in a precise sense, applied descriptive statistics.

- **Chapter 21 (Time Series)**: The autocorrelation function (ACF) at lag $k$ is the sample correlation between a time series and its own $k$-step lagged version: $r_k = \hat{\gamma}(k)/\hat{\gamma}(0)$, where $\hat{\gamma}(k)$ is the sample autocovariance at lag $k$. The partial autocorrelation function (PACF) is defined via a sequence of regressions. Time series analysis is built on the foundation of correlation and covariance.



### What Is Implemented vs. Documented Only

- [x] Sample mean, variance and standard deviation (Welford's algorithm internally)
- [x] Sample skewness and kurtosis (excess kurtosis)
- [x] Median, quantile, IQR and five-number summary via sorting
- [x] Pearson sample covariance and correlation (pairwise)
- [x] Covariance matrix and correlation matrix computation
- [x] Weighted mean and weighted variance
- [x] Population variance variant (denominator n)
- [ ] Mode computation for continuous data via kernel density estimation (deferred; mode is defined only for discrete/histogram contexts)
- [ ] Rank-based statistics such as Spearman correlation or Kendall's tau (deferred to a future release)
- [ ] Box plot rendering or graphical output (out of scope; the library computes the five-number summary only)

---


### Implementation Context

The Evenwicht library organises descriptive statistics across three modules:

- `src/stats/descriptive.ts` -- mean, variance, standard deviation, skewness, kurtosis
- `src/stats/covariance.ts` -- covariance matrix, correlation matrix, pairwise covariance and correlation
- `src/stats/rank.ts` -- quantiles, percentiles, median, IQR, five-number summary

Import paths follow the Evenwicht module convention:

The primary API operates on `Float64Array` for numerical precision and performance:

Design decisions:
1. **Bessel's correction by default.** The `variance` function uses the $n-1$ denominator (sample variance). A `populationVariance` variant with denominator $n$ is available for cases where the data represents the entire population.
2. **Welford internally.** The `variance` and `std` functions use Welford's algorithm (Algorithm 15.23) for numerical stability, even though the data is available in memory (the cost of two passes is minimal for in-memory data, but Welford avoids subtle bugs in edge cases).
3. **Non-destructive quantiles.** The `quantile` and `median` functions do not sort the input array in place; they create an internal copy before sorting.
4. **Matrix type.** The `covarianceMatrix` and `correlationMatrix` functions return a `Matrix` object (from the Evenwicht linear algebra module) that supports the standard matrix operations (transpose, multiplication, eigendecomposition).
5. **NaN propagation.** If the input contains NaN values or if computation is undefined (e.g., variance of a single observation, correlation with zero-variance variable), the functions return `NaN` rather than throwing.
