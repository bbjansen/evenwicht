<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Statistical Inference — API Reference

This is the API reference for the TypeScript implementation of Statistical Inference. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/stats/inference.ts`

- `src/stats/estimation.ts` -- Maximum likelihood estimation
- `src/stats/confidence.ts` -- Confidence interval construction
- `src/stats/hypothesis.ts` -- z-tests, t-tests, paired t-tests
- `src/stats/anova.ts` -- One-way analysis of variance
- `src/stats/chi_square.ts` -- Chi-square tests for independence and goodness of fit

### Data Representation

All test functions return a structured result object containing at minimum `{ statistic, pValue, df, reject }`. Confidence intervals are returned as `{ lower, upper, level }`. All p-value computations call the CDF functions from the distributions module (Chapter 14).

### API Preview

```typescript
// src/stats/hypothesis.ts

interface TestResult {
  statistic: number;
  pValue: number;
  df: number;
  reject: boolean;
  ci?: { lower: number; upper: number };
}

interface TestOptions {
  alpha?: number;            // default 0.05
  alternative?: 'two-sided' | 'less' | 'greater';
}

function zTest(data: Float64Array, mu0: number, sigma: number, opts?: TestOptions): TestResult;
function tTest(data: Float64Array, mu0: number, opts?: TestOptions): TestResult;
function tTestTwoSample(x: Float64Array, y: Float64Array, opts?: TestOptions & { equalVariance?: boolean }): TestResult;
function pairedTTest(x: Float64Array, y: Float64Array, opts?: TestOptions): TestResult;

// src/stats/anova.ts
interface AnovaResult {
  ssb: number; ssw: number; sst: number;
  fStatistic: number; df: [number, number];
  pValue: number; reject: boolean;
}
function oneWayAnova(groups: Float64Array[], opts?: { alpha?: number }): AnovaResult;

// src/stats/chi_square.ts
interface ChiSquareResult {
  statistic: number; expected: number[][];
  df: number; pValue: number; reject: boolean;
}
function chiSquareIndependence(table: number[][], opts?: { alpha?: number }): ChiSquareResult;
function chiSquareGoodnessOfFit(observed: number[], expected: number[], opts?: { alpha?: number }): ChiSquareResult;

// src/stats/estimation.ts
function mleNormal(data: Float64Array): { mu: number; sigma2: number; logLikelihood: number };

// src/stats/confidence.ts
function confidenceInterval(data: Float64Array, opts: {
  parameter: 'mean' | 'proportion' | 'difference';
  level?: number; knownVariance?: number;
}): { lower: number; upper: number; level: number };
```

### Error Handling

- `tTest` throws if the data array has fewer than 2 observations.
- `tTestTwoSample` with `equalVariance: true` uses the pooled variance; with `false` (default) uses the Welch approximation for degrees of freedom.
- `pairedTTest` throws if `x` and `y` have different lengths.
- `chiSquareIndependence` throws if any expected cell count is below 1 (warns if below 5).
- `chiSquareGoodnessOfFit` throws if `observed` and `expected` have different lengths or if any expected frequency is zero.
- `oneWayAnova` throws if fewer than 2 groups are provided or if any group has fewer than 2 observations.

### Dependencies

- `src/stats/distributions.ts` -- normal, t, chi-squared and F distribution CDFs for p-value computation
- `src/stats/descriptive.ts` -- `mean`, `variance` for test statistic computation

### Usage Examples

```typescript
import { tTest, chiSquareGoodnessOfFit, confidenceInterval } from 'evenwicht/stats';

// One-sample t-test: test if mean differs from 5
const data = new Float64Array([5.1, 4.9, 5.2, 5.0, 4.8, 5.3]);
const result = tTest(data, 5.0);
// result.pValue > 0.05 (fail to reject H0)

// Chi-square goodness of fit for a fair die
const observed = [18, 12, 15, 20, 17, 18];
const expected = [100/6, 100/6, 100/6, 100/6, 100/6, 100/6];
const chi2 = chiSquareGoodnessOfFit(observed, expected);

// 95% confidence interval for the mean
const ci = confidenceInterval(data, { parameter: 'mean', level: 0.95 });
// ci.lower ≈ 4.86, ci.upper ≈ 5.28
```

### Connections

This chapter is used by Chapter 17 (Regression), which employs t-tests for individual coefficients, F-tests for overall model significance and confidence intervals for predictions. The distributions introduced in Chapter 14 serve as the reference distributions for all tests in this chapter. The descriptive statistics of Chapter 15 supply the summary quantities (sample means, variances, counts) that form the inputs to every inferential procedure.

- **Chapter 13 (Probability)**: The law of large numbers (Chapter 13) guarantees that the sample mean converges to the population mean, underpinning the consistency of estimators. The central limit theorem justifies the Normal approximation used in the z-test and the Wald confidence interval for proportions. Bayes' theorem provides the foundation for Bayesian alternatives to the frequentist methods developed here.

- **Chapter 14 (Distributions)**: Every inferential procedure in this chapter relies on the distributional theory of Chapter 14. The z-test uses the Normal CDF; the t-test uses the $t$-distribution; ANOVA uses the $F$-distribution; the chi-square test uses the $\chi^2$-distribution. Without efficient and accurate implementations of these CDFs and quantile functions, no test can produce correct p-values or critical values.

- **Chapter 15 (Descriptive Statistics)**: The sample mean, sample variance and frequency counts computed in Chapter 15 serve as the raw inputs to inference. Every test statistic in this chapter is assembled from these descriptive summaries. The careful numerical algorithms for variance computation (Welford's algorithm, two-pass formulas) discussed in Chapter 15 directly benefit the numerical stability of the procedures here.

- **Chapter 17 (Regression)**: Linear regression is, at its core, an estimation and testing framework. The least-squares estimator $\hat{\beta} = (X^TX)^{-1}X^Ty$ is the MLE under Normal errors. The t-test (Definition 16.22) is used to test whether individual regression coefficients are zero. The F-test is used to test overall model significance (whether all coefficients are jointly zero) and to compare nested models. Confidence intervals for predictions use the $t$-distribution with the appropriate degrees of freedom.



### What Is Implemented vs. Documented Only

- [x] One-sample z-test for population mean (known variance)
- [x] One-sample and two-sample t-tests (pooled and Welch variants)
- [x] Paired t-test
- [x] Confidence interval construction for means and proportions
- [x] One-way ANOVA (F-test for equality of group means)
- [x] Chi-square test for independence (contingency tables)
- [x] Chi-square goodness-of-fit test
- [x] MLE for normal distribution parameters
- [ ] Two-way ANOVA and higher factorial designs (deferred; only one-way is implemented)
- [ ] Nonparametric tests such as Wilcoxon rank-sum or Kruskal–Wallis (deferred to a future release)
- [ ] Bayesian posterior computation for general parametric models (deferred; only discrete Bayes from Chapter 13 is provided)
- [ ] Likelihood ratio tests for general model comparison (documented but deferred)

---


### Implementation Context

The statistical inference module is organised across several source files:

- **`src/stats/estimation.ts`** -- Maximum likelihood estimation for parametric families. Exports `mleNormal(data)` returning `{ mu, sigma2, logLikelihood }`. Method-of-moments estimators for common distributions.

- **`src/stats/confidence.ts`** -- Confidence interval construction. Exports `confidenceInterval(data, options)` with options specifying the parameter of interest (mean, proportion, difference), known or unknown variance and confidence level. Returns `{ lower, upper, level }`.

- **`src/stats/hypothesis.ts`** -- Core hypothesis testing functions:
  - `zTest(data, mu0, sigma, options)` -- z-test for population mean.
  - `tTest(data, mu0, options)` -- one-sample t-test.
  - `tTestTwoSample(x, y, options)` -- two-sample t-test (pooled or Welch, controlled by `equalVariance` flag).
  - `pairedTTest(x, y, options)` -- paired t-test.
  
  Each returns `{ statistic, pValue, ci, df, reject }`.

- **`src/stats/anova.ts`** -- Analysis of variance. Exports `oneWayAnova(groups, options)` returning `{ ssb, ssw, sst, fStatistic, df, pValue, reject }`.

- **`src/stats/chi_square.ts`** -- Chi-square tests. Exports `chiSquareIndependence(table, options)` returning `{ statistic, expected, df, pValue, reject }`. Also exports `chiSquareGoodnessOfFit(observed, expected, options)`.

**API Design Principles.** All test functions accept an `options` object with:
- `alpha` (default 0.05): significance level.
- `alternative` (default "two-sided"): one of "two-sided", "less", "greater".
- Additional test-specific options (e.g., `equalVariance` for two-sample t-test).

All test functions return a result object with at minimum `{ statistic, pValue, df, reject }` and, where applicable, a confidence interval `ci: { lower, upper }`.

**Dependencies on Chapter 14.** The p-value computations call the CDF functions from the distributions module: `normalCdf`, `tCdf`, `fCdf`, `chiSquaredCdf`. Quantile functions (`normalQuantile`, `tQuantile`) are used for confidence interval construction.
