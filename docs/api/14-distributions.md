<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Probability Distributions — API Reference

This is the API reference for the TypeScript implementation of Probability Distributions. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/stats/distributions.ts`

- `evenwicht/stats/distributions/continuous` -- Normal, Student's t, Chi-squared, F, Continuous Uniform
- `evenwicht/stats/distributions/discrete` -- Bernoulli, Binomial, Poisson, Discrete Uniform

### Data Representation

Each distribution is created by a factory function and exposes a uniform interface. Continuous distributions provide `pdf`, `cdf`, `quantile`, `mean` and `variance`. Discrete distributions provide `pmf` in place of `pdf`. All numerical operations use IEEE 754 double precision. The CDF implementations rely on the special functions from `evenwicht/core/special` (erf, incomplete gamma, incomplete beta).

### API Preview

```typescript
// src/stats/distributions.ts

interface Distribution {
  pdf(x: number): number;       // or pmf(x) for discrete
  cdf(x: number): number;
  quantile(p: number): number;
  mean(): number;
  variance(): number;
}

/** Normal distribution N(mu, sigma^2). Takes variance, not std deviation. */
function normal(mu: number, sigma2: number): Distribution;

/** Student's t-distribution with nu degrees of freedom. */
function studentT(df: number): Distribution;

/** Chi-squared distribution with k degrees of freedom. */
function chiSquared(df: number): Distribution;

/** F-distribution with (d1, d2) degrees of freedom. */
function fDistribution(df1: number, df2: number): Distribution;

/** Continuous uniform on [a, b]. */
function uniform(a: number, b: number): Distribution;

/** Bernoulli distribution with success probability p. */
function bernoulli(p: number): Distribution;

/** Binomial(n, p). PMF uses log-space for large n. */
function binomial(n: number, p: number): Distribution;

/** Poisson(lambda). PMF uses stable recurrence. */
function poisson(lambda: number): Distribution;

/** Discrete uniform on {a, a+1, ..., b}. */
function discreteUniform(a: number, b: number): Distribution;
```

### Error Handling

- All factory functions throw at construction time for invalid parameters: negative variance, `p` outside `[0, 1]`, non-positive degrees of freedom, `a >= b` for uniform.
- `quantile(p)` throws if `p` is outside the open interval `(0, 1)`.
- `cdf(x)` returns `0` or `1` for inputs outside the support without throwing.
- Binomial PMF uses log-Gamma arithmetic to avoid overflow for `n > 170`.
- Poisson PMF uses the recurrence `P(k) = P(k-1) * lambda / k` to avoid factorial overflow.
- All PDF/PMF values are accurate to at least 14 significant digits; CDF values to at least 12.

### Dependencies

- `src/core/special.ts` -- `gamma`, `logGamma`, `beta` for PDF/CDF computations
- `src/core/erf.ts` -- `erf`, `erfc` for normal distribution CDF
- Used by: `src/stats/inference.ts` (p-value computations), `src/stats/confidence.ts`

### Usage Examples

```typescript
import { normal, studentT, binomial, poisson } from 'evenwicht/stats/distributions';

// Standard normal distribution
const z = normal(0, 1);
z.pdf(0);       // ≈ 0.3989 (peak of bell curve)
z.cdf(1.96);    // ≈ 0.975
z.quantile(0.975);  // ≈ 1.96

// Binomial: 10 trials, p = 0.3
const b = binomial(10, 0.3);
b.pmf(3);       // ≈ 0.2668
b.mean();       // 3.0

// Poisson with lambda = 5
const p = poisson(5);
p.pmf(5);       // ≈ 0.1755
p.cdf(7);       // ≈ 0.8666
```

### Connections

This chapter is used by Chapter 16 (Inference -- test statistics follow these distributions), Chapter 17 (Regression -- residuals follow normal distributions, F-tests compare nested models) and Chapter 21 (Time Series -- residual distributions and hypothesis tests). It builds on Chapter 2 (Special Functions) and Chapter 13 (Probability Theory).

- **Chapter 2 (Special Functions)**: The Gamma function, Beta function and error function are the computational primitives on which this chapter rests. The chi-squared PDF involves $\Gamma(k/2)$; the t-distribution PDF involves the ratio $\Gamma((\nu+1)/2)/\Gamma(\nu/2)$; the F-distribution PDF involves the Beta function $B(d_1/2, d_2/2)$; the normal CDF is computed via erf. Without the special functions of Chapter 2, none of the distributions in this chapter can be evaluated numerically.

- **Chapter 13 (Probability Theory)**: This chapter provides the definitions (random variable, CDF, expectation, variance) and the key theorems (law of large numbers, central limit theorem) that underpin the material here. The CLT explains why the normal distribution is central; the LLN justifies using sample means as parameter estimates.

- **Chapter 16 (Statistical Inference)**: Test statistics are distributed as t, chi-squared, or F under the null hypothesis. Confidence intervals are constructed by inverting these distributions (using the quantile function). Every hypothesis test in Chapter 16 reduces to a probability calculation in this chapter.

- **Chapter 17 (Regression)**: OLS residuals are assumed $N(0, \sigma^2)$. The t-test on individual coefficients uses the t-distribution. The overall F-test for model significance uses the F-distribution. The $R^2$ statistic is related to the F-statistic through a monotone transformation.

- **Chapter 15 (Descriptive Statistics)**: Sample statistics (sample mean, sample variance) have sampling distributions characterised by the distributions defined here. The sample mean of normal data follows a normal distribution; the sample variance follows a scaled chi-squared.

- **Chapter 21 (Time Series)**: Residual diagnostics test whether innovations are normally distributed. The Ljung–Box test statistic follows a chi-squared distribution. The Dickey–Fuller test uses a non-standard distribution that is tabulated by simulation.



### What Is Implemented vs. Documented Only

- [x] Normal distribution: PDF, CDF (via erf), quantile (via inverse erf / rational approximation)
- [x] Student's t distribution: PDF, CDF (via regularised incomplete beta), quantile (Newton–Raphson)
- [x] Chi-squared distribution: PDF, CDF (via regularised incomplete gamma), quantile
- [x] F-distribution: PDF, CDF (via regularised incomplete beta), quantile
- [x] Bernoulli, Binomial, Poisson, Discrete Uniform: PMF, CDF, quantile
- [x] Continuous Uniform distribution: PDF, CDF, quantile
- [x] Binomial PMF in log-space to avoid overflow for large n
- [x] Poisson PMF via stable recurrence relation
- [x] Mean and variance accessors for all distributions
- [ ] Multivariate distributions such as multivariate normal and Wishart (out of scope for this chapter)
- [ ] Gamma and Exponential as standalone distribution objects (documented as special cases of chi-squared; standalone wrappers deferred)

---


### Implementation Context

The distributions are implemented in two source modules, organised by the discrete/continuous distinction:

- `evenwicht/stats/distributions/continuous` -- Normal, Student's t, Chi-squared, F, Continuous Uniform
- `evenwicht/stats/distributions/discrete` -- Bernoulli, Binomial, Poisson, Discrete Uniform

Each distribution provides a uniform interface:

Design decisions:

1. **Parameterisation**: The normal distribution takes $\sigma^2$ (variance), not $\sigma$ (standard deviation), to match the mathematical convention $N(\mu, \sigma^2)$. The user passes `normal(0, 1)` for the standard normal, `normal(100, 225)` for $N(100, 15^2)$.

2. **Error handling**: Invalid parameters (negative variance, $p \notin [0,1]$, non-positive degrees of freedom) throw immediately at construction time, not at evaluation time. Quantile inputs outside $(0,1)$ throw; CDF inputs outside the support return 0 or 1 as appropriate.

3. **Dependencies**: The implementation depends on `evenwicht/core/special` (providing `gamma`, `logGamma`, `erf`, `erfc`, `erfInv`, `incompleteBeta`, `incompleteGamma`) and `evenwicht/core/factorial` (providing `binomialCoefficient`, `logBinomialCoefficient`).

4. **Accuracy targets**: All PDF/PMF values are accurate to at least 14 significant digits. CDF values are accurate to at least 12 significant digits across the full range. Quantile values satisfy $|F(Q(p)) - p| < 10^{-14}$ for well-conditioned inputs.

5. **Performance**: All operations are $O(1)$ except the Poisson CDF (which sums $O(\lambda)$ terms) and the Binomial CDF (which sums $O(n)$ terms or uses the incomplete beta). Quantile functions use at most 10 Newton–Raphson iterations.
