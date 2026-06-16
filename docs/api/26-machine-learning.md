<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Machine Learning Foundations — API Reference

This is the API reference for the TypeScript implementation of Machine Learning Foundations. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/ml/`

- `src/ml/linear.ts` — Ridge regression (closed-form via Cholesky)
- `src/ml/logistic.ts` — Logistic regression with numerically stable sigmoid
- `src/ml/regularization.ts` — Regularisation utilities
- `src/ml/optimize.ts` — SGD with momentum
- `src/ml/pca.ts` — Principal component analysis via eigendecomposition
- `src/ml/network.ts` — Two-layer neural network with backpropagation

### Data Representation

Feature matrices are `number[][]` (row-major, each row is an observation). Label vectors are `number[]`. Weight vectors returned by linear models are `number[]`. The PCA module operates on the sample covariance matrix using the eigendecomposition from `evenwicht/linalg` (Chapter 10).

### API Preview

```typescript
// src/ml/linear.ts
/** Ridge regression: (X'X + n*lambda*I)^{-1} X'y. */
function ridge(X: number[][], y: number[], lambda: number): number[];

// src/ml/logistic.ts
/** Numerically stable sigmoid: branches on sign of z to avoid overflow. */
function sigmoid(z: number): number;
/** Logistic regression via gradient descent. */
function logisticRegression(X: number[][], y: number[], opts?: {
  learningRate?: number; maxIterations?: number; tolerance?: number;
}): { weights: number[]; bias: number };

// src/ml/optimize.ts
/** SGD with momentum. Data is shuffled each epoch. */
function sgdMomentum(
  gradient: (params: number[], batchX: number[][], batchY: number[]) => number[],
  initialParams: number[],
  X: number[][], y: number[],
  opts?: { batchSize?: number; learningRate?: number; momentum?: number; epochs?: number },
): number[];

// src/ml/pca.ts
/** PCA: returns eigenvectors sorted by decreasing eigenvalue. */
function pca(data: number[][], k: number): {
  components: number[][];     // k principal component vectors (rows)
  eigenvalues: number[];      // k largest eigenvalues
  projected: number[][];      // data projected onto k components
  explainedVariance: number;  // fraction of total variance explained
};

// src/ml/network.ts
interface NetworkConfig { inputDim: number; hiddenDim: number; outputDim: number; activation?: 'relu' | 'sigmoid' | 'tanh'; }
function createNetwork(config: NetworkConfig): NeuralNetwork;
interface NeuralNetwork {
  forward(x: number[]): { output: number[]; cache: ForwardCache };
  backprop(cache: ForwardCache, target: number[]): Gradients;
  updateWeights(gradients: Gradients, learningRate: number): void;
}
```

### Error Handling

- `ridge` throws if `X` has zero rows or if the regularised Gram matrix is singular (numerically, if the Cholesky factorisation fails).
- `sigmoid` returns values in `(0, 1)` for all finite inputs; for `z >= 0` it computes `1 / (1 + exp(-z))`, for `z < 0` it computes `exp(z) / (1 + exp(z))`, avoiding overflow in both cases.
- `pca` throws if `k` exceeds the number of features or if `k < 1`.
- `sgdMomentum` shuffles data each epoch using a Fisher-Yates shuffle; it does not modify the original arrays.
- The neural network `backprop` function computes gradients via the delta recursion; it does not update weights (that is a separate call).

### Dependencies

- `src/linear/` — matrix operations for ridge regression normal equations
- `src/linear/eigen.ts` — eigendecomposition for PCA
- `src/stats/covariance.ts` — sample covariance matrix for PCA
- `src/optimization/unconstrained.ts` — underlying optimiser concepts

### Usage Examples

```typescript
import { ridge, sigmoid, logisticRegression, pca } from 'evenwicht/ml';

// Ridge regression with lambda = 0.1
const X = [[1, 2], [2, 3], [3, 4], [4, 5]];
const y = [3, 5, 7, 9];
const weights = ridge(X, y, 0.1);
// weights ≈ [1.0, 1.0]  (y ≈ x1 + x2)

// Stable sigmoid
sigmoid(0);     // 0.5
sigmoid(100);   // ≈ 1.0 (no overflow)
sigmoid(-100);  // ≈ 0.0 (no overflow)

// PCA: reduce 4D data to 2 components
const data = [[1,2,3,4], [2,3,4,5], [3,4,5,6], [4,5,6,7]];
const result = pca(data, 2);
// result.explainedVariance ≈ 1.0 (data lies on a 1D subspace)
```

### Connections

This chapter synthesises Chapters 4, 7, 9, 10, 11, 14, 16 and 17 into a unified computational framework. It connects forward to Chapter 27 (Quantitative Trading), Chapter 21 (Time Series) and Chapter 29 (Control Systems).

- **Differential Calculus** (Chapter 4): The chain rule is the mathematical foundation of backpropagation. Its generalisation to Jacobian matrices (Chapter 7) extends backpropagation to multi-output layers.

- **Matrices** (Chapter 9): The OLS and ridge estimators are matrix formulas. Neural network forward passes are sequences of matrix-vector multiplications.

- **Eigenvalues** (Chapter 10): PCA is eigendecomposition of the covariance matrix. The condition number $\kappa(X'X)$ determines numerical stability and motivates ridge regularisation.

- **Unconstrained Optimisation** (Chapter 11): Gradient descent convergence theory ($O(1/T)$ for smooth convex functions, role of condition number) is applied at scale throughout machine learning.

- **Constrained Optimisation** (Chapter 12): Ridge regression as a constrained problem and the KKT conditions for LASSO connect regularisation to the Lagrangian framework.

- **Distributions** (Chapter 14): The Bernoulli distribution underlies logistic regression (cross-entropy loss); the Gaussian underlies squared-error loss.

- **Statistical Inference** (Chapter 16): Maximum likelihood estimation provides the principled derivation of the cross-entropy loss for logistic regression and justifies the Bayesian interpretation of ridge regularisation.

- **Regression** (Chapter 17): Linear regression is the starting point for all supervised learning. The Gauss–Markov theorem and geometric projection interpretation are extended here.



### What Is Implemented vs. Documented Only

- [x] Ridge regression (closed-form via Cholesky factorisation)
- [x] Logistic regression with numerically stable sigmoid and gradient descent
- [x] SGD with momentum (configurable batch size, learning rate, epochs)
- [x] PCA via eigendecomposition of the sample covariance matrix
- [x] Two-layer neural network with forward pass and backpropagation
- [ ] LASSO regression (L1 penalty) (documented; requires coordinate descent, deferred)
- [ ] Elastic net regularisation (documented as a combination of ridge and LASSO; deferred)
- [ ] Deep networks with arbitrary layer count (documented conceptually; only two-layer implemented)
- [ ] Cross-validation and model selection utilities (documented in bias-variance discussion; deferred)
- [ ] Decision trees, random forests, or ensemble methods (out of scope for this chapter)

---


### Implementation Context

The algorithms above map to the Evenwicht library as compositions of existing modules.

**Source files**: `src/ml/linear.ts`, `src/ml/logistic.ts`, `src/ml/regularization.ts`, `src/ml/optimize.ts`, `src/ml/pca.ts`, `src/ml/network.ts`.

**Ridge regression** (`src/ml/linear.ts`) implements the closed-form solution via Cholesky factorisation of $X'X + n\lambda I$ (preferred over explicit inversion for numerical stability). The function accepts a design matrix, response vector and regularisation parameter.

**Logistic regression** (`src/ml/logistic.ts`) implements the numerically stable sigmoid and gradient descent loop. The `sigmoid` function branches on the sign of $z$ to avoid overflow (Section 5).

**SGD with momentum** (`src/ml/optimize.ts`) accepts any gradient function, initial parameters and configuration (batch size, learning rate, momentum coefficient, epochs). Data is shuffled each epoch; velocity accumulates across mini-batches.

**PCA** (`src/ml/pca.ts`) centres the data, computes the sample covariance matrix

$$\Sigma = \frac{1}{n-1}\tilde{X}'\tilde{X}$$

via matrix operations from `evenwicht/linalg`, calls `eigendecompose` from `evenwicht/linalg` (Chapter 10), sorts eigenvectors by decreasing eigenvalue and projects the data onto the leading $K$ directions.

**Neural network** (`src/ml/network.ts`) implements a two-layer network with configurable activation. The `forward` function returns all intermediate quantities

$$\mathbf{z}^{(1)},\quad \mathbf{a}^{(1)},\quad \hat{y}$$

needed by the `backprop` function, which computes gradients via the delta recursion of Theorem 26.20.
