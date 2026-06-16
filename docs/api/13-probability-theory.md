<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
# Probability Theory — API Reference

This is the API reference for the TypeScript implementation of Probability Theory. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/stats/probability.ts`

### Data Representation

Discrete probability distributions are represented as paired `number[]` arrays for values and probabilities. All probability vectors must be non-negative and sum to 1 (within floating-point tolerance). Computations use compensated summation internally to minimise rounding drift.

### API Preview

```typescript
// src/stats/probability.ts

/**
 * Compute posterior probabilities via Bayes' theorem.
 *
 * @param priors - Prior probabilities P(B_i), must sum to 1.
 * @param likelihoods - Likelihoods P(A | B_i), one per hypothesis.
 * @returns Posterior probabilities P(B_i | A).
 */
function bayesPosterior(priors: number[], likelihoods: number[]): number[];

/**
 * Compute expected value of a discrete random variable.
 *
 * @param values - Possible values x_i.
 * @param probs - Corresponding probabilities p(x_i).
 * @returns E[X] = sum of x_i * p(x_i).
 */
function expectedValue(values: number[], probs: number[]): number;

/**
 * Compute variance using the numerically stable two-pass algorithm.
 *
 * @param values - Possible values x_i.
 * @param probs - Corresponding probabilities p(x_i).
 * @returns Var(X) = E[(X - mu)^2].
 */
function varianceTwoPass(values: number[], probs: number[]): number;

/**
 * Compute the n-th moment E[X^n] of a discrete distribution.
 *
 * @param values - Possible values x_i.
 * @param probs - Corresponding probabilities p(x_i).
 * @param n - Moment order (positive integer).
 * @returns E[X^n].
 */
function moment(values: number[], probs: number[], n: number): number;

/**
 * Compute the n-th central moment E[(X - mu)^n].
 *
 * @param values - Possible values x_i.
 * @param probs - Corresponding probabilities p(x_i).
 * @param n - Moment order (positive integer).
 * @returns E[(X - mu)^n].
 */
function centralMoment(values: number[], probs: number[], n: number): number;
```

### Error Handling

- `bayesPosterior` throws if `priors` and `likelihoods` have different lengths, if any prior is negative, or if the evidence (sum of joint probabilities) is zero (no hypothesis assigns positive probability to the observed data).
- `expectedValue` and `varianceTwoPass` throw if `values` and `probs` have different lengths or if the arrays are empty.
- `moment` and `centralMoment` throw if the moment order `n` is not a positive integer.
- All functions silently handle the case where individual `probs[i] === 0` by skipping those terms.

### Dependencies

- No external module dependencies; probability computations are self-contained
- Used by: `src/stats/distributions.ts`, `src/information/entropy.ts`

### Usage Examples

```typescript
import { bayesPosterior, expectedValue, varianceTwoPass } from 'evenwicht/stats';

// Bayes' theorem: medical test with 1% prevalence, 99% sensitivity, 95% specificity
const posteriors = bayesPosterior([0.01, 0.99], [0.99, 0.05]);
// posteriors ≈ [0.167, 0.833]  (positive predictive value ~17%)

// Expected value of a fair die
const values = [1, 2, 3, 4, 5, 6];
const probs = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6];
expectedValue(values, probs);  // 3.5

// Variance of a fair die
varianceTwoPass(values, probs);  // ≈ 2.9167
```

### Connections

This chapter provides the theoretical foundation for the remainder of Part V. Chapter 14 (Distributions) catalogues specific probability distributions and their properties. Chapter 15 (Descriptive Statistics) applies the expectation and variance formulas developed here to empirical data. Chapter 16 (Statistical Inference) uses conditional probability and Bayes' theorem to construct estimators and hypothesis tests. Chapter 17 (Regression) models the conditional expectation $E[Y \mid X]$ and requires distributional assumptions on error terms.

- **Chapter 14 (Distributions)**: This chapter defines what a distribution *is* (PMF, PDF, CDF) and what quantities characterise it (mean, variance, MGF). Chapter 14 catalogues the specific named distributions (Bernoulli, binomial, Poisson, uniform, exponential, normal, gamma), giving their explicit PMFs/PDFs and deriving their moments using the tools established here.

- **Chapter 15 (Descriptive Statistics)**: The sample mean $\bar{X}_n$ and sample variance $S^2$ are empirical counterparts of $E[X]$ and $\operatorname{Var}(X)$. The law of large numbers (Theorem 13.28) guarantees that these sample quantities converge to their population targets as $n$ grows, providing the theoretical justification for descriptive statistics as estimators.

- **Chapter 16 (Statistical Inference)**: Bayes' theorem (Theorem 13.8) is the engine of Bayesian inference: prior distributions are updated to posterior distributions via the likelihood. The law of large numbers (Theorem 13.28) justifies the use of sample means as estimators. The CLT (Theorem 13.29) underpins confidence intervals and hypothesis tests: the sampling distribution of $\bar{X}_n$ is approximately normal for large $n$, enabling the construction of $z$-intervals and $z$-tests without assuming normality of the population.

- **Chapter 17 (Regression)**: Linear regression models $Y = \beta_0 + \beta_1 X + \varepsilon$, where $\varepsilon$ is a random variable with $E[\varepsilon] = 0$. The conditional expectation $E[Y \mid X = x] = \beta_0 + \beta_1 x$ is a special case of Definition 13.24. Assumptions about $\operatorname{Var}(\varepsilon)$ (homoscedasticity) and the distribution of $\varepsilon$ (normality for exact inference) draw directly on this chapter's framework.



### What Is Implemented vs. Documented Only

- [x] Bayes' theorem computation for discrete priors and likelihoods
- [x] Expected value of a discrete random variable
- [x] Two-pass numerically stable variance computation
- [x] General moment and central moment computation for discrete distributions
- [ ] Pseudo-random number generation and Monte Carlo simulation (planned for a future release)
- [ ] Continuous expectation and variance via numerical integration (deferred to distribution-specific implementations in Chapter 14)
- [ ] Moment generating function evaluation (documented theoretically; not implemented as a standalone routine)

---


### Implementation Context

Probability theory, as developed in this chapter, is primarily the *theoretical foundation* for the statistical modules that follow. The Evenwicht library implements the concrete numerical tools in later chapters, but several components from this chapter appear directly:

- **Bayes' theorem utility**: A function implementing Algorithm 13.30 is provided for computing posterior distributions given discrete priors and likelihoods. This supports the Bayesian inference routines of Chapter 16.

- **Expected value and variance computation**: The formulas of Definitions 13.14 and 13.16 are implemented using the numerically stable algorithms of Section 6. These underpin the descriptive statistics module planned for Chapter 15 and the distribution objects of Chapter 14.

- **Moment computation**: General moment computation $E[X^n]$ and central moment computation $E[(X - \mu)^n]$ are provided for arbitrary discrete distributions, supporting the skewness and kurtosis measures of Definition 13.18.

- **CDF evaluation and inversion**: The CDF (Definition 13.13) and its inverse (the quantile function) are implemented for each specific distribution in Chapter 14.

- **No simulation or random number generation**: The current version (v0.x) of the library does not include pseudo-random number generation or Monte Carlo simulation. These capabilities are planned for a future release. The library focuses on exact symbolic and numerical computation of distributional quantities.

The primary source paths relevant to this chapter's formulas are:

- `evenwicht/stats/probability` -- Bayes' theorem, expected value, variance (Algorithms 13.30–13.32).
- `evenwicht/stats/descriptive` -- mean, variance, moments (Chapter 15).
- `evenwicht/stats/distributions/` -- PMF, PDF, CDF evaluation per distribution (Chapter 14).
