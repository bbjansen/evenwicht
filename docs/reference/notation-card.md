<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Notation Quick-Reference Card

This page collects the notation used throughout Evenwicht in a single compact reference. Each symbol is listed with its meaning and the chapter in which it first appears. Chapter-local notation tables may add context-specific uses; this card covers the global conventions.

---

## Sets and Number Systems

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $\mathbb{R}$ | The set of real numbers | [Ch 1](../domains/01-expressions.md) |
| $\mathbb{R}^n$ | The set of $n$-tuples of real numbers | [Ch 7](../domains/07-multivariate-calculus.md) |
| $\mathbb{R}^{m \times n}$ | The set of $m \times n$ real matrices | [Ch 9](../domains/09-matrices.md) |
| $\mathbb{R}_+$ or $[0, \infty)$ | Non-negative reals | [Ch 1](../domains/01-expressions.md) |
| $\mathbb{C}$ | The set of complex numbers | [Ch 10](../domains/10-eigenvalues.md) |
| $\mathbb{Z}$ | The set of integers | [Ch 1](../domains/01-expressions.md) |
| $\mathbb{N}$ | The set of natural numbers (including 0) | [Ch 1](../domains/01-expressions.md) |
| $\mathbb{N}_0$ | Synonym for $\mathbb{N}$: $\{0, 1, 2, \ldots\}$ | [Ch 20](../domains/20-discrete-operators.md) |
| $\mathbb{Q}$ | The set of rational numbers | [Ch 1](../domains/01-expressions.md) |
| $\emptyset$ | The empty set | [Ch 13](../domains/13-probability-theory.md) |
| $A \times B$ | Cartesian product of sets $A$ and $B$ | [Ch 1](../domains/01-expressions.md) |
| $A \setminus B$ | Set difference: elements in $A$ not in $B$ | [Ch 13](../domains/13-probability-theory.md) |
| $A^c$ | Complement of $A$ | [Ch 13](../domains/13-probability-theory.md) |

---

## Vectors and Matrices

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $\mathbf{v}, \mathbf{u}, \mathbf{w}$ | Vectors (boldface lowercase) | [Ch 8](../domains/08-vectors.md) |
| $v_i$ | The $i$-th component of $\mathbf{v}$ | [Ch 8](../domains/08-vectors.md) |
| $\mathbf{e}_i$ | The $i$-th standard basis vector | [Ch 8](../domains/08-vectors.md) |
| $\mathbf{0}$ | The zero vector | [Ch 8](../domains/08-vectors.md) |
| $A, B, M$ | Matrices (uppercase roman) | [Ch 9](../domains/09-matrices.md) |
| $a_{ij}$ | Entry in row $i$, column $j$ of $A$ | [Ch 9](../domains/09-matrices.md) |
| $A^T$ | Transpose of $A$: $(A^T)_{ij} = a_{ji}$ | [Ch 9](../domains/09-matrices.md) |
| $A^{-1}$ | Inverse of $A$ (when it exists) | [Ch 9](../domains/09-matrices.md) |
| $\det(A)$ or $\lvert A \rvert$ | Determinant of $A$ | [Ch 9](../domains/09-matrices.md) |
| $\operatorname{tr}(A)$ | Trace of $A$: $\sum_i a_{ii}$ | [Ch 9](../domains/09-matrices.md) |
| $\operatorname{rank}(A)$ | Rank of $A$ | [Ch 9](../domains/09-matrices.md) |
| $I_n$ | The $n \times n$ identity matrix | [Ch 9](../domains/09-matrices.md) |
| $O$ | The zero matrix | [Ch 9](../domains/09-matrices.md) |
| $\operatorname{diag}(d_1, \ldots, d_n)$ | Diagonal matrix with entries $d_1, \ldots, d_n$ | [Ch 9](../domains/09-matrices.md) |
| $\kappa(A)$ | Condition number: $\lVert A \rVert \cdot \lVert A^{-1} \rVert$ | [Ch 9](../domains/09-matrices.md) |
| $e^{At}$ | Matrix exponential | [Ch 19](../domains/19-odes.md) |

---

## Calculus

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $f'(x)$ | Derivative of $f$ at $x$ (Lagrange notation) | [Ch 4](../domains/04-differential-calculus.md) |
| $\frac{df}{dx}$, $\frac{dy}{dx}$ | Derivative (Leibniz notation) | [Ch 4](../domains/04-differential-calculus.md) |
| $Df$ | Derivative operator applied to $f$ | [Ch 4](../domains/04-differential-calculus.md) |
| $f^{(n)}(x)$ | The $n$-th derivative of $f$ | [Ch 4](../domains/04-differential-calculus.md) |
| $\frac{\partial f}{\partial x_i}$, $f_{x_i}$ | Partial derivative of $f$ with respect to $x_i$ | [Ch 7](../domains/07-multivariate-calculus.md) |
| $\nabla f$ | Gradient: vector of all partial derivatives | [Ch 7](../domains/07-multivariate-calculus.md) |
| $H_f$ or $\nabla^2 f$ | Hessian matrix of second partial derivatives | [Ch 7](../domains/07-multivariate-calculus.md) |
| $J_F$ | Jacobian matrix of a vector-valued function $\mathbf{F}$ | [Ch 7](../domains/07-multivariate-calculus.md) |
| $D_\mathbf{u} f$ | Directional derivative in the direction $\mathbf{u}$ | [Ch 7](../domains/07-multivariate-calculus.md) |
| $df$ | Total differential of $f$ | [Ch 7](../domains/07-multivariate-calculus.md) |
| $\int_a^b f(x)\,dx$ | Definite integral of $f$ from $a$ to $b$ | [Ch 5](../domains/05-integral-calculus.md) |
| $\int f(x)\,dx$ | Indefinite integral (antiderivative family) | [Ch 5](../domains/05-integral-calculus.md) |
| $[F(x)]_a^b$ | Evaluation notation: $F(b) - F(a)$ | [Ch 5](../domains/05-integral-calculus.md) |

---

## Probability and Statistics

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $\Omega$ | Sample space | [Ch 13](../domains/13-probability-theory.md) |
| $\mathcal{F}$ | Sigma-algebra (collection of events) | [Ch 13](../domains/13-probability-theory.md) |
| $P(A)$ | Probability of event $A$ | [Ch 13](../domains/13-probability-theory.md) |
| $P(A \mid B)$ | Conditional probability of $A$ given $B$ | [Ch 13](../domains/13-probability-theory.md) |
| $X, Y, Z$ | Random variables | [Ch 13](../domains/13-probability-theory.md) |
| $\mathbb{E}[X]$ | Expected value of $X$ | [Ch 13](../domains/13-probability-theory.md) |
| $\operatorname{Var}(X)$ or $\sigma^2$ | Variance of $X$ | [Ch 13](../domains/13-probability-theory.md) |
| $\operatorname{Cov}(X,Y)$ | Covariance of $X$ and $Y$ | [Ch 13](../domains/13-probability-theory.md) |
| $\rho(X,Y)$ | Correlation coefficient | [Ch 13](../domains/13-probability-theory.md) |
| $M_X(t)$ | Moment generating function: $\mathbb{E}[e^{tX}]$ | [Ch 13](../domains/13-probability-theory.md) |
| $p(x)$ or $p_X(x)$ | Probability mass function (PMF) | [Ch 13](../domains/13-probability-theory.md) |
| $f(x)$ or $f_X(x)$ | Probability density function (PDF) | [Ch 13](../domains/13-probability-theory.md) |
| $F(x)$ or $F_X(x)$ | Cumulative distribution function (CDF) | [Ch 13](../domains/13-probability-theory.md) |
| $\bar{x}$ | Sample mean | [Ch 15](../domains/15-descriptive-statistics.md) |
| $s^2$ | Sample variance (Bessel-corrected) | [Ch 15](../domains/15-descriptive-statistics.md) |
| $\hat{\theta}$ | Estimator of parameter $\theta$ | [Ch 16](../domains/16-statistical-inference.md) |
| $L(\theta \mid x)$ | Likelihood function | [Ch 16](../domains/16-statistical-inference.md) |
| $\ell(\theta)$ | Log-likelihood | [Ch 16](../domains/16-statistical-inference.md) |
| $H_0$, $H_1$ | Null and alternative hypotheses | [Ch 16](../domains/16-statistical-inference.md) |

---

## Operators

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $D$ | Derivative operator: $Df = f'$ | [Ch 4](../domains/04-differential-calculus.md) |
| $D^n$ | The $n$-th derivative operator | [Ch 4](../domains/04-differential-calculus.md) |
| $L$ | Lag (backshift) operator: $Lx_t = x_{t-1}$ | [Ch 20](../domains/20-discrete-operators.md) |
| $L^k$ | The $k$-th power of the lag operator: $L^k x_t = x_{t-k}$ | [Ch 20](../domains/20-discrete-operators.md) |
| $L^{-1}$ | Forward shift operator: $L^{-1} x_t = x_{t+1}$ | [Ch 20](../domains/20-discrete-operators.md) |
| $E$ | Shift operator: $Ex_t = x_{t+1}$ | [Ch 18](../domains/18-difference-equations.md) |
| $\Delta$ | Difference operator: $\Delta x_t = x_{t+1} - x_t$ or $\Delta = 1 - L$ | [Ch 18](../domains/18-difference-equations.md) |
| $\Delta^n$ | The $n$-th order difference operator: $(1 - L)^n$ | [Ch 20](../domains/20-discrete-operators.md) |
| $\Sigma$ | Summation operator (discrete indefinite integral) | [Ch 20](../domains/20-discrete-operators.md) |

---

## Norms and Inner Products

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $\lVert\mathbf{v}\rVert$ | Euclidean norm: $\sqrt{v_1^2 + \cdots + v_n^2}$ | [Ch 8](../domains/08-vectors.md) |
| $\lVert\cdot\rVert$ | Euclidean norm (default) unless stated otherwise | [Ch 8](../domains/08-vectors.md) |
| $\langle \mathbf{u}, \mathbf{v} \rangle$ or $\mathbf{u} \cdot \mathbf{v}$ | Inner product (dot product) | [Ch 8](../domains/08-vectors.md) |
| $\mathbf{u} \perp \mathbf{v}$ | Orthogonality: $\mathbf{u} \cdot \mathbf{v} = 0$ | [Ch 8](../domains/08-vectors.md) |
| $\lvert x \rvert$ | Absolute value of $x$ | [Ch 1](../domains/01-expressions.md) |
| $\lvert z \rvert$ | Modulus of a complex number $z$ | [Ch 22](../domains/22-transforms.md) |

---

## Common Conventions

| Symbol | Typical Use | First Appears |
|--------|-------------|---------------|
| $f, g, h$ | Functions $\mathbb{R} \to \mathbb{R}$ | [Ch 1](../domains/01-expressions.md) |
| $x, y, z$ | Real-valued variables | [Ch 1](../domains/01-expressions.md) |
| $t$ | Time (continuous or discrete) | [Ch 5](../domains/05-integral-calculus.md) |
| $n, m$ | Positive integers (dimensions, indices, sizes) | [Ch 1](../domains/01-expressions.md) |
| $k$ | Summation or iteration index | [Ch 1](../domains/01-expressions.md) |
| $\alpha, \beta$ | Parameters (context-dependent) | [Ch 8](../domains/08-vectors.md) |
| $\lambda$ | Eigenvalue; Lagrange multiplier; parameter | [Ch 10](../domains/10-eigenvalues.md) |
| $\varepsilon$ | Tolerance or machine epsilon | [Ch 3](../domains/03-limits-continuity.md) |
| $h$ | Step size (numerical methods) or increment | [Ch 4](../domains/04-differential-calculus.md) |
| $C$ | Constant of integration | [Ch 5](../domains/05-integral-calculus.md) |
| $\theta$ | Angle (radians); population parameter | [Ch 1](../domains/01-expressions.md) |
| $\mu$ | Population mean; integrating factor | [Ch 13](../domains/13-probability-theory.md) |
| $\sigma$ | Standard deviation | [Ch 13](../domains/13-probability-theory.md) |
| $:=$ | "is defined as" | [Ch 1](../domains/01-expressions.md) |
| $\approx$ | Approximately equal (numerical) | [Ch 1](../domains/01-expressions.md) |
| $\square$ | End of proof | [Ch 1](../domains/01-expressions.md) |
| $O(\cdot)$ | Big-O asymptotic notation | [Ch 4](../domains/04-differential-calculus.md) |
| $o(\cdot)$ | Little-o asymptotic notation | [Ch 7](../domains/07-multivariate-calculus.md) |
| $C^k$ | Class of functions with $k$ continuous derivatives | [Ch 4](../domains/04-differential-calculus.md) |

---

## Transforms

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $F(\omega)$ | Continuous Fourier transform of $f(t)$ | [Ch 22](../domains/22-transforms.md) |
| $F(s)$ | Laplace transform of $f(t)$ | [Ch 22](../domains/22-transforms.md) |
| $X(z)$ | Z-transform of $\{x_n\}$ | [Ch 20](../domains/20-discrete-operators.md) |
| $X_k$ | The $k$-th DFT coefficient | [Ch 22](../domains/22-transforms.md) |
| $s$ | Complex frequency variable ($s = \sigma + i\omega$) | [Ch 22](../domains/22-transforms.md) |
| $\omega_N$ | Primitive $N$-th root of unity: $e^{-2\pi i / N}$ | [Ch 22](../domains/22-transforms.md) |
| $\ast$ | Circular convolution | [Ch 22](../domains/22-transforms.md) |
| $(f * g)_t$ | Discrete convolution: $\sum_k f_k \, g_{t-k}$ | [Ch 20](../domains/20-discrete-operators.md) |

---

## Optimisation

| Symbol | Meaning | First Appears |
|--------|---------|---------------|
| $\mathbf{x}^*$ | Optimal point (minimiser or maximiser) | [Ch 11](../domains/11-unconstrained-optimization.md) |
| $f^*$ | Optimal value: $f(\mathbf{x}^*)$ | [Ch 11](../domains/11-unconstrained-optimization.md) |
| $\mathcal{L}(\mathbf{x}, \boldsymbol{\lambda})$ | Lagrangian function | [Ch 12](../domains/12-constrained-optimization.md) |
| $\lambda_i$ | Lagrange multiplier for constraint $i$ | [Ch 12](../domains/12-constrained-optimization.md) |
| $g_i(\mathbf{x})$ | The $i$-th constraint function | [Ch 12](../domains/12-constrained-optimization.md) |
| $\alpha$, $\eta$ | Step size (learning rate) | [Ch 11](../domains/11-unconstrained-optimization.md) |
| $\succeq 0$, $\succ 0$ | Positive semidefinite, positive definite | [Ch 11](../domains/11-unconstrained-optimization.md) |
