<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Information Theory — API Reference

This is the API reference for the TypeScript implementation of Information Theory. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/information/`

- `src/information/entropy.ts` — Shannon entropy, joint entropy, conditional entropy, mutual information
- `src/information/divergence.ts` — KL divergence, cross-entropy
- `src/information/channel.ts` — Channel capacity utilities

### Data Representation

Discrete probability distributions are `number[]` arrays summing to 1. Joint distributions are `number[][]` matrices where `pxy[i][j] = P(X = i, Y = j)`. All information-theoretic quantities are computed in bits (log base 2) by default, with `*Nats` variants using the natural logarithm.

### API Preview

```typescript
// src/information/entropy.ts

/** Shannon entropy H(X) in bits. Skips zero-probability entries. */
function entropy(p: number[]): number;
/** Shannon entropy in nats (natural log). */
function entropyNats(p: number[]): number;
/** Binary entropy H_b(p) = -p log p - (1-p) log(1-p). */
function binaryEntropy(p: number): number;
/** Joint entropy H(X, Y) from a joint probability matrix. */
function jointEntropy(pxy: number[][]): number;
/** Conditional entropy H(Y|X) = H(X,Y) - H(X). */
function conditionalEntropy(pxy: number[][]): number;
/** Mutual information I(X;Y) = H(X) + H(Y) - H(X,Y). */
function mutualInformation(pxy: number[][]): number;

// src/information/divergence.ts

/** KL divergence D_KL(P || Q) in bits. Returns Infinity if Q(i) = 0 where P(i) > 0. */
function klDivergence(p: number[], q: number[]): number;
/** KL divergence in nats. */
function klDivergenceNats(p: number[], q: number[]): number;
/** Cross-entropy H(P, Q) = H(P) + D_KL(P || Q). */
function crossEntropy(p: number[], q: number[]): number;
```

### Error Handling

- `entropy` returns 0 for a degenerate distribution (single element with probability 1), consistent with the convention $0 \log 0 = 0$.
- `klDivergence` returns `Infinity` when any `q[i] === 0` where `p[i] > 0` (the KL divergence is undefined when the support of P is not contained in the support of Q).
- `klDivergence` and `crossEntropy` throw if `p` and `q` have different lengths.
- `binaryEntropy` returns 0 for `p <= 0` or `p >= 1` (boundary cases).
- `jointEntropy` and `conditionalEntropy` compute marginals internally from the joint matrix; they throw if any row has a different length (ragged matrix).

### Dependencies

- No external module dependencies; all computations use `Math.log2` and basic arithmetic
- Used by: `src/ml/` (cross-entropy loss), feature selection algorithms

### Usage Examples

```typescript
import { entropy, klDivergence, mutualInformation, binaryEntropy } from 'evenwicht/information';

// Entropy of a fair coin: 1 bit
entropy([0.5, 0.5]);  // 1.0

// Entropy of a biased coin
binaryEntropy(0.9);  // ≈ 0.469 bits

// KL divergence between two distributions
klDivergence([0.5, 0.5], [0.9, 0.1]);  // ≈ 0.737 bits

// Mutual information from a joint distribution
const pxy = [[0.3, 0.1], [0.1, 0.5]];
mutualInformation(pxy);  // > 0 (X and Y are dependent)
```

### Connections

This chapter draws on Chapter 13 (probability measures, expectation, Jensen's inequality) and Chapter 14 (Gaussian, exponential and uniform distributions as maximum entropy solutions). It applies Chapter 11 (Lagrangian optimisation for maximum entropy and channel capacity). It connects forward to machine learning applications (cross-entropy loss, variational inference, feature selection via mutual information), coding theory and statistical model selection (AIC as an information-theoretic criterion).

- **Probability Theory** (Chapter 13): Shannon entropy is defined as an expectation $H(X) = \mathbb{E}[-\log p(X)]$ and all information-theoretic inequalities reduce to properties of expectation and convexity. Jensen's inequality (Chapter 13) is the fundamental tool for proving non-negativity of KL divergence. The conditional probability formalism provides the language for conditional entropy and channel transition probabilities.

- **Distributions** (Chapter 14): The maximum entropy principle produces specific distributions as solutions to constrained optimisation: the uniform (no constraints beyond normalisation), the exponential (fixed mean on $[0,\infty)$), the Gaussian (fixed mean and variance on $\mathbb{R}$) and the Poisson (fixed mean on non-negative integers, approximately). Computing entropy and divergence for named distributions provides closed-form benchmarks.

- **Integration** (Chapter 5): Differential entropy requires computing $-\int f(x) \log f(x) \, dx$ for continuous distributions. The proof that the Gaussian maximises entropy under a variance constraint (Theorem 28.19) uses integral calculus. Mutual information for continuous variables involves double integrals of joint densities.

- **Series & Approximation** (Chapter 6): Entropy computations for infinite alphabets involve convergent series. The Taylor expansion $\log(1+x) \approx x - x^2/2 + \cdots$ is useful for approximating KL divergence between nearby distributions, yielding the second-order approximation $D_{\mathrm{KL}}(p \| q) \approx \frac{1}{2\ln 2}\sum_x (p(x) - q(x))^2/q(x)$ (related to chi-squared divergence).

- **Optimisation** (Chapter 11): The maximum entropy principle is a constrained optimisation problem solved via Lagrange multipliers. Channel capacity computation (Blahut–Arimoto) is an alternating optimisation algorithm. The connection between KL divergence minimisation and maximum likelihood provides the theoretical foundation for loss function design in machine learning.



### What Is Implemented vs. Documented Only

- [x] Shannon entropy (bits and nats) for discrete distributions
- [x] Binary entropy function
- [x] Joint entropy from a joint probability matrix
- [x] Conditional entropy H(Y|X)
- [x] Mutual information I(X;Y)
- [x] KL divergence (bits and nats)
- [x] Cross-entropy H_Q(P)
- [x] Jensen–Shannon divergence
- [x] Channel capacity via Blahut–Arimoto algorithm
- [ ] Differential entropy for continuous distributions (documented theoretically; not implemented)
- [ ] Rate-distortion computation (documented in theory; deferred)
- [ ] Source coding (Huffman, arithmetic coding) algorithms (out of scope; only theoretical bounds are covered)
- [ ] Error-correcting code construction (out of scope; Shannon's channel coding theorem is stated but codes are not implemented)


---


### Implementation Context

The algorithms above map to the Evenwicht library as follows.

**Source files**: `src/information/entropy.ts`, `src/information/divergence.ts`, `src/information/channel.ts`.
