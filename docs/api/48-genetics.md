<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Genetics & Bioinformatics — API Reference

This is the API reference for the TypeScript implementation of Genetics & Bioinformatics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/genetics/hardy-weinberg.ts` — Hardy–Weinberg equilibrium chi-square test
- `src/genetics/selection.ts` — selection step, trajectory, overdominance equilibrium
- `src/genetics/wright-fisher.ts` — Wright–Fisher transition matrix, drift simulation
- `src/genetics/substitution.ts` — Jukes–Cantor model, evolutionary distance
- `src/genetics/linkage.ts` — linkage disequilibrium decay

### Data Representation

Allele frequencies are represented as plain `number` values in $[0, 1]$. Genotype counts are `number` arrays or objects. The Wright–Fisher transition matrix is a `Float64Array[]` (array of rows) or a flat `Float64Array` of size $(2N+1)^2$. DNA sequences are `string` values over the alphabet `{A, C, G, T}`. Substitution rate matrices and transition probability matrices are $4 \times 4$ arrays.

### API Preview

```typescript
// src/genetics/hardy-weinberg.ts

import { chiSquareCDF } from 'evenwicht/stats';

interface HWTestResult {
  /** Estimated allele frequency p-hat. */
  pHat: number;
  /** Expected genotype counts [E_AA, E_Aa, E_aa]. */
  expected: [number, number, number];
  /** Chi-square test statistic. */
  chiSquare: number;
  /** p-value from chi-square distribution with 1 df. */
  pValue: number;
  /** Whether the null hypothesis (HW equilibrium) is rejected at the given alpha. */
  rejected: boolean;
}

/**
 * Test whether observed genotype counts are consistent with
 * Hardy–Weinberg equilibrium using the chi-square test.
 *
 * @param observed - Genotype counts [O_AA, O_Aa, O_aa].
 * @param alpha - Significance level (default 0.05).
 * @returns Test result with statistic, p-value and decision.
 */
function hardyWeinbergTest(
  observed: [number, number, number],
  alpha?: number,
): HWTestResult;
```

```typescript
// src/genetics/selection.ts

interface SelectionParams {
  /** Fitness of genotype AA. */
  wAA: number;
  /** Fitness of genotype Aa. */
  wAa: number;
  /** Fitness of genotype aa. */
  waa: number;
}

/**
 * Compute the allele frequency in the next generation under selection.
 */
function selectionStep(p: number, params: SelectionParams): number;

/**
 * Iterate the selection recurrence for a given number of generations.
 *
 * @returns Array of allele frequencies [p_0, p_1, ..., p_T].
 */
function selectionTrajectory(
  p0: number,
  params: SelectionParams,
  generations: number,
): Float64Array;

/**
 * Compute the equilibrium allele frequency under overdominance.
 * Throws if fitnesses do not satisfy overdominance conditions.
 */
function overdominanceEquilibrium(params: SelectionParams): number;
```

```typescript
// src/genetics/wright-fisher.ts

/**
 * Construct the Wright–Fisher transition matrix for population size N.
 *
 * @param N - Diploid population size (matrix is (2N+1) x (2N+1)).
 * @returns The transition matrix as a flat Float64Array.
 */
function wrightFisherMatrix(N: number): Float64Array;

/**
 * Simulate the Wright–Fisher process for T generations.
 *
 * @param N - Diploid population size.
 * @param initialCount - Initial count of allele A (0 to 2N).
 * @param generations - Number of generations to simulate.
 * @returns Array of allele counts per generation.
 */
function simulateWrightFisher(
  N: number,
  initialCount: number,
  generations: number,
): Uint32Array;
```

```typescript
// src/genetics/substitution.ts

/**
 * Compute the Jukes–Cantor rate matrix for a given substitution rate.
 */
function jcRateMatrix(alpha: number): Float64Array;

/**
 * Compute the Jukes–Cantor transition probability matrix at time t.
 */
function jcTransitionMatrix(alpha: number, t: number): Float64Array;

/**
 * Estimate evolutionary distance between two aligned DNA sequences
 * using the Jukes–Cantor correction.
 *
 * @returns Estimated distance d, or NaN if sequences are saturated.
 */
function jukesCantorDistance(seq1: string, seq2: string): number;
```

```typescript
// src/genetics/linkage.ts

/**
 * Compute linkage disequilibrium decay over generations.
 *
 * @param D0 - Initial LD coefficient.
 * @param r - Recombination rate.
 * @param generations - Number of generations.
 * @returns Array of D values [D_0, D_1, ..., D_T].
 */
function ldDecay(D0: number, r: number, generations: number): Float64Array;
```

### Error Handling

- `hardyWeinbergTest` throws if any observed count is negative or if all counts are zero.
- `selectionStep` throws if fitness values are non-positive or if $p \notin [0, 1]$.
- `wrightFisherMatrix` throws if $N < 1$ or $N > 500$ (matrix size limit for memory).
- `jukesCantorDistance` throws if sequences have unequal length or contain characters outside `{A, C, G, T}`. Returns `NaN` for saturated sequences ($\hat{p} \geq 3/4$).
- `overdominanceEquilibrium` throws if $w_{Aa} \leq w_{AA}$ or $w_{Aa} \leq w_{aa}$.

### Dependencies

- `src/stats/distributions.ts` — chi-squared CDF for Hardy–Weinberg test
- `src/core/factorial.ts` — binomial coefficients for Wright–Fisher transition probabilities

### Usage Examples

```typescript
import { hardyWeinbergTest, selectionTrajectory, jukesCantorDistance } from 'evenwicht/genetics';

// Hardy–Weinberg test: observed genotype counts [AA, Aa, aa]
const result = hardyWeinbergTest([50, 40, 10]);
// result.pHat ≈ 0.7, result.pValue: test significance

// Selection trajectory: directional selection favouring A allele
const traj = selectionTrajectory(0.1, { wAA: 1.0, wAa: 0.95, waa: 0.9 }, 100);
// traj: allele frequencies over 100 generations (converges to 1.0)

// Evolutionary distance between aligned DNA sequences
jukesCantorDistance('ATCGATCG', 'ATCGTTCG');  // ≈ 0.137
```

### Connections

This chapter synthesises Chapter 9 (the Wright–Fisher transition matrix, the Jukes–Cantor rate matrix and substitution scoring matrices are all matrix objects), Chapter 13 (allele frequencies are probabilities; genotype frequencies arise from the product rule for independent events; genetic drift is binomial sampling), Chapter 16 (the chi-square test detects departures from Hardy–Weinberg equilibrium), Chapter 18 (allele frequency dynamics under selection and mutation are nonlinear and linear difference equations respectively, with fixed points analysed by the techniques of that chapter) and Chapter 33 (Hardy–Weinberg equilibrium is a fixed point of a discrete map, stable under the conditions of random mating). It connects forward to optimisation (maximum likelihood phylogenetics) and information theory (information content of scoring matrices).

- **Matrices** (Chapter 9): The Wright–Fisher transition matrix is the central object of the neutral drift theory. Its construction involves binomial probabilities (Chapter 13) organised into a stochastic matrix (row sums equal 1). The Jukes–Cantor rate matrix $Q$ and its exponential $P(t) = e^{Qt}$ are $4 \times 4$ matrix objects whose properties (eigenvalues, spectral decomposition) come directly from Chapter 9. Substitution scoring matrices (BLOSUM, PAM) are symmetric matrices of log-odds scores.

- **Probability Theory** (Chapter 13): Hardy–Weinberg is a theorem about independent draws from a probability distribution. Genetic drift is binomial sampling. The chi-square test for HW equilibrium relies on the asymptotic distribution of standardised sums. The log-odds score is a likelihood ratio: the logarithm of the Bayesian odds that a pair of residues is related versus unrelated.

- **Statistical Inference** (Chapter 16): The chi-square goodness-of-fit test (Definition 48.4) is a direct application of Chapter 16. The ANOVA decomposition in quantitative genetics (partitioning phenotypic variance into genetic and environmental components) follows the framework of Chapter 16. GWAS relies on hypothesis testing at millions of variants with Bonferroni or false discovery rate corrections.

- **Difference Equations** (Chapter 18): Allele frequency change under selection (Theorem 48.6) is a first-order nonlinear difference equation. Mutation (Definition 48.9) is a linear recurrence. Linkage disequilibrium decay (Theorem 48.25) is a geometric recurrence. All three have fixed points analysed by the stability criteria of Chapter 18.

- **Equilibrium** (Chapter 33): Hardy–Weinberg equilibrium is a fixed point of a discrete map; perhaps the most important single example in population genetics. The overdominance equilibrium (Theorem 48.8) is a stable fixed point of the selection dynamics. The mutation equilibrium (Theorem 48.10) is a globally attracting fixed point of a linear map. The stationary distribution of the Wright–Fisher chain with mutation is the equilibrium in the sense of an ergodic Markov chain.

- **Eigenvalues** (Chapter 10): The second eigenvalue of the Wright–Fisher matrix determines the rate of heterozygosity loss. The eigenvalues of the Jukes–Cantor rate matrix ($0$ and $-4\alpha$ with multiplicity 3) determine the transition probability matrix via $P(t) = e^{Qt}$. The eigenvalue decomposition is the computational core of phylogenetic distance estimation.



### What Is Implemented vs. Documented Only

- [x] Hardy–Weinberg test (`hardyWeinbergTest`)
- [x] Selection recurrence iteration (`selectionStep`, `selectionTrajectory`)
- [x] Overdominance equilibrium (`overdominanceEquilibrium`)
- [x] Wright–Fisher transition matrix (`wrightFisherMatrix`)
- [x] Wright–Fisher simulation (`simulateWrightFisher`)
- [x] Jukes–Cantor model (`jcRateMatrix`, `jcTransitionMatrix`, `jukesCantorDistance`)
- [x] Linkage disequilibrium decay (`ldDecay`)
- [ ] General substitution models (Kimura, HKY, GTR — deferred, requires parameterised rate matrix framework)
- [ ] Sequence alignment dynamic programming (deferred — algorithmic, not mathematical library scope)
- [ ] BLOSUM/PAM matrix construction (deferred — requires large protein alignment databases)
- [ ] Diffusion approximation for Wright–Fisher (deferred — requires PDE solver)
- [ ] GWAS statistical framework (deferred; requires multiple testing correction framework)

---


### Implementation Context

**Wright–Fisher matrix in log-space.** For population sizes $N > 50$, binomial coefficients $\binom{2N}{j}$ exceed $10^{60}$ and overflow double precision. The transition matrix is constructed in log-space: $\ln T_{ij} = \ln\Gamma(2N+1) - \ln\Gamma(j+1) - \ln\Gamma(2N-j+1) + j\ln p + (2N-j)\ln(1-p)$, then exponentiated. The matrix size limit ($N \leq 500$, yielding a $1001 \times 1001$ matrix) is enforced to prevent excessive memory usage.

**Selection recurrence convergence.** Under directional selection ($w_{AA} > w_{Aa} > w_{aa}$), the allele frequency $p \to 1$ but convergence is slow near fixation (approximately $1/t$ decay of $q = 1-p$). Overdominance converges geometrically to $p^* = (w_{Aa} - w_{aa})/(2w_{Aa} - w_{AA} - w_{aa})$. The `selectionStep` function validates that all fitness values are positive and $p \in [0, 1]$ before each iteration.

**Jukes–Cantor distance singularity.** The correction formula $d = -\frac{3}{4}\ln(1 - 4\hat{p}/3)$ diverges as $\hat{p} \to 3/4$. For $\hat{p} > 0.70$, the variance becomes very large and the estimate is unreliable. The function returns `NaN` for saturated sequences ($\hat{p} \geq 3/4$) rather than throwing, allowing downstream code to handle the case gracefully.

**Chi-square validity.** The Hardy–Weinberg chi-square approximation requires all expected genotype counts $E_k \geq 5$. With small samples ($n < 30$) or extreme allele frequencies ($\hat{p} < 0.05$), this threshold may not be met and the $p$-value becomes unreliable. The function does not currently warn when expected counts are low; users should verify this condition externally.

**Eigenvalue gap in Wright–Fisher matrices.** The second eigenvalue $\lambda_2 \approx 1 - 1/(2N)$ determines the rate of heterozygosity loss. For $N > 100$, the gap from $\lambda_1 = 1$ becomes small, but double precision (15 significant digits) resolves it for all practical matrix sizes ($N \leq 500$).

**Testing strategy.** HW tests use populations in known equilibrium (expected $\chi^2 \approx 0$) and populations with known departures. Selection trajectory tests verify fixation ($p \to 1$) under directional selection and convergence to $p^*$ under overdominance. JC distance tests compare against known distances for sequences differing at a single site. Wright–Fisher simulation tests verify that the mean allele count is preserved (no selection, no mutation).
