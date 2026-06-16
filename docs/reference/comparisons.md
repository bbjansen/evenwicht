<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Cross-Chapter Comparison Tables

The same mathematical structures recur in different settings throughout this text. A derivative in continuous time has a counterpart in the difference operator; an ODE has a counterpart in a recurrence relation; a population parameter has a counterpart in a sample statistic. The tables below make these parallels explicit so that a reader who has mastered one setting can transfer that understanding to the other.

---

## 1. Continuous vs Discrete

Chapters [4](../domains/04-differential-calculus.md), [5](../domains/05-integral-calculus.md) and [19](../domains/19-odes.md) develop calculus and differential equations in continuous time. Chapters [18](../domains/18-difference-equations.md) and [20](../domains/20-discrete-operators.md) develop the discrete analogues.

| Continuous | Discrete | Notes |
|------------|----------|-------|
| Independent variable $t \in \mathbb{R}$ | Index $t \in \mathbb{Z}$ or $t \in \mathbb{N}_0$ | Continuous time vs discrete time steps |
| Function $f(t)$ | Sequence $\{x_t\}$ | Both map from a domain to $\mathbb{R}$ |
| Derivative $f'(t) = \frac{df}{dt}$ | Forward difference $\Delta x_t = x_{t+1} - x_t$ | Rate of change vs first difference |
| Derivative operator $D$ | Difference operator $\Delta = E - I$ | $D$ is the infinitesimal generator; $\Delta$ is its discrete counterpart |
| Shift by $h$: $f(t + h)$ | Shift operator $E$: $Ex_t = x_{t+1}$ | $E = e^{hD}$ in the formal operator correspondence |
| Taylor expansion: $f(t+h) = \sum \frac{h^k}{k!} f^{(k)}(t)$ | Newton forward difference: $x_{t+k} = \sum \binom{k}{j} \Delta^j x_t$ | Polynomial expansion in $h$ vs binomial expansion in $\Delta$ |
| Integral $\int_a^b f(t)\,dt$ | Summation $\sum_{t=a}^{b-1} x_t$ | Area under a curve vs accumulation of terms |
| Antiderivative $F'(t) = f(t)$ | Antidifference $\Sigma$: $\Delta(\Sigma x_t) = x_t$ | Inverse of differentiation vs inverse of differencing |
| Fundamental Theorem of Calculus: $\int_a^b f(t)\,dt = F(b) - F(a)$ | Telescoping: $\sum_{t=a}^{b-1} \Delta x_t = x_b - x_a$ | Both express the inverse relationship |
| ODE: $y' = f(t, y)$ | Recurrence: $x_{t+1} = g(t, x_t)$ | Continuous vs discrete dynamical systems |
| Linear ODE: $ay'' + by' + cy = 0$ | Linear recurrence: $x_{t+2} + a_1 x_{t+1} + a_2 x_t = 0$ | Characteristic equation governs both |
| Solution $y(t) = c_1 e^{\lambda_1 t} + c_2 e^{\lambda_2 t}$ | Solution $x_t = c_1 \lambda_1^t + c_2 \lambda_2^t$ | Exponentials vs powers of eigenvalues |
| Equilibrium: $f(y^*) = 0$ | Fixed point: $x^* = g(x^*)$ | Stability governed by eigenvalues in both cases |
| Stability: $\operatorname{Re}(\lambda) < 0$ | Stability: $\lvert\lambda\rvert < 1$ | Left half-plane vs interior of the unit disc |
| Exponential function $e^{at}$ | Geometric sequence $r^t$ | Both satisfy their respective "eigenvalue equations" |
| Convolution $\int f(\tau)\,g(t - \tau)\,d\tau$ | Discrete convolution $\sum_k f_k \, g_{t-k}$ | Continuous vs discrete superposition |
| Dirac delta $\delta(t)$ | Kronecker delta $\delta_t$ | Identity elements for their respective convolutions |

---

## 2. Time Domain vs Frequency Domain

Chapters [19](../domains/19-odes.md) and [21](../domains/21-time-series.md) work in the time domain. Chapter [22](../domains/22-transforms.md) introduces transforms that move signals and systems into the frequency domain.

| Time Domain | Frequency Domain | Notes |
|-------------|-----------------|-------|
| Signal $f(t)$ or $\{x_t\}$ | Spectrum $F(\omega)$, $X_k$ or $X(z)$ | The same information in a different representation |
| Convolution $(f * g)(t)$ | Pointwise product $F(\omega) \cdot G(\omega)$ | Convolution theorem: transforms turn convolution into multiplication |
| Pointwise product $f(t) \cdot g(t)$ | Convolution $\frac{1}{2\pi}(F * G)(\omega)$ | The dual of the convolution theorem |
| Derivative $f'(t)$ | Multiplication by $i\omega$ (Fourier) or $s$ (Laplace) | Differentiation becomes an algebraic operation |
| Integration $\int f(\tau)\,d\tau$ | Division by $i\omega$ (Fourier) or $s$ (Laplace) | Integration becomes division |
| Lag $Lx_t = x_{t-1}$ | Multiplication by $z^{-1}$ (Z-transform) | The lag operator is a unit delay in the $z$-plane |
| Difference $\Delta x_t$ | Multiplication by $(1 - z^{-1})$ | $\Delta = 1 - L$ translates directly |
| ODE: $ay'' + by' + cy = g(t)$ | Algebraic equation: $(as^2 + bs + c)Y(s) = G(s)$ | The Laplace transform reduces ODEs to algebra |
| Recurrence: $x_{t+2} + a_1 x_{t+1} + a_2 x_t = b_t$ | $(z^2 + a_1 z + a_2)X(z) = B(z) + \text{ICs}$ | The Z-transform reduces recurrences to algebra |
| AR process $\phi(L)X_t = \varepsilon_t$ | Transfer function $H(z) = 1/\phi(z)$ | Roots of $\phi(z)$ determine stationarity |
| Autocovariance $\gamma(h)$ | Power spectral density $P_k$ | The Wiener--Khinchin theorem relates the two |
| Impulse response $h(t)$ or $\{h_t\}$ | Transfer function $H(s)$ or $H(z)$ | The transform of the impulse response |
| Stability: poles in left half-plane ($\operatorname{Re}(s) < 0$) | Stability: poles inside unit circle ($\lvert z \rvert < 1$) | Continuous vs discrete stability criteria |
| Sampling interval $\Delta t$ | Sampling frequency $f_s = 1/\Delta t$ | The bridge between continuous and discrete frequencies |
| Nyquist limit: $f_{\max} < f_s / 2$ | Aliasing if violated | Constraint on the frequency content that sampling can capture |

---

## 3. Constrained vs Unconstrained Optimisation

Chapter [11](../domains/11-unconstrained-optimization.md) treats optimisation without constraints. Chapter [12](../domains/12-constrained-optimization.md) adds equality and inequality constraints and introduces linear programming.

| Unconstrained (Ch 11) | Constrained (Ch 12) | Notes |
|------------------------|---------------------|-------|
| Objective $f(\mathbf{x})$ | Objective $f(\mathbf{x})$ subject to $g_i(\mathbf{x}) = 0$ | The same objective, but the feasible set is restricted |
| Domain: all of $\mathbb{R}^n$ | Feasible set $\mathcal{F} \subseteq \mathbb{R}^n$ | Constraints carve out a subset of the domain |
| First-order condition: $\nabla f(\mathbf{x}^*) = \mathbf{0}$ | First-order condition: $\nabla f = \sum_i \lambda_i \nabla g_i$ | The gradient of $f$ must lie in the span of constraint gradients |
| Solve $\nabla f = \mathbf{0}$ directly | Solve the Lagrangian system $\nabla_\mathbf{x} \mathcal{L} = \mathbf{0}$ and $g_i = 0$ | The Lagrangian adjoins the constraints to the objective |
| Second-order condition: $H_f \succ 0$ (minimum) | Second-order condition: bordered Hessian $\bar{H}$ test | The Hessian is evaluated on the tangent space of the constraints |
| No multipliers | Lagrange multipliers $\lambda_i$ | Each multiplier measures the sensitivity of $f^*$ to the $i$-th constraint |
| Gradient descent: $\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha \nabla f$ | Simplex method pivots along vertices of $\mathcal{F}$ | Iterative methods differ because the geometry differs |
| Newton's method: uses $H_f^{-1}$ | Interior point methods: barrier functions | Both exploit second-order information |
| Convexity of $f$ guarantees a global minimum | Convexity of $f$ and $\mathcal{F}$ guarantees a global minimum | Strong duality holds for convex problems |
| Convergence rate: linear (GD), quadratic (Newton) | Simplex: finite pivots; interior point: polynomial | Different complexity profiles |
| Sensitivity: $\frac{\partial f^*}{\partial \theta}$ via implicit differentiation | Envelope theorem: $\frac{\partial f^*}{\partial \theta} = \frac{\partial \mathcal{L}}{\partial \theta}$ | The multipliers encode the shadow prices |

---

## 4. Population vs Sample Statistics

Chapter [13](../domains/13-probability-theory.md) defines probability and population-level quantities. Chapters [15](../domains/15-descriptive-statistics.md) and [16](../domains/16-statistical-inference.md) define their sample-based counterparts and the inference machinery that connects the two.

| Population (Ch 13) | Sample (Ch 15, 16) | Notes |
|---------------------|---------------------|-------|
| Population mean $\mu = \mathbb{E}[X]$ | Sample mean $\bar{x} = \frac{1}{n}\sum x_i$ | $\bar{x}$ is an unbiased estimator of $\mu$ |
| Population variance $\sigma^2 = \operatorname{Var}(X)$ | Sample variance $s^2 = \frac{1}{n-1}\sum(x_i - \bar{x})^2$ | Bessel's correction ($n-1$) makes $s^2$ unbiased for $\sigma^2$ |
| Standard deviation $\sigma$ | Sample standard deviation $s$ | $s$ is consistent but slightly biased for $\sigma$ |
| Covariance $\operatorname{Cov}(X,Y)$ | Sample covariance $s_{xy} = \frac{1}{n-1}\sum(x_i - \bar{x})(y_i - \bar{y})$ | Same Bessel correction applies |
| Correlation $\rho(X,Y)$ | Sample correlation $r_{xy} = s_{xy}/(s_x s_y)$ | Pearson correlation coefficient |
| Distribution $F_X(x) = P(X \leq x)$ | Empirical CDF $\hat{F}_n(x) = \frac{1}{n}\sum \mathbf{1}(x_i \leq x)$ | The Glivenko--Cantelli theorem guarantees $\hat{F}_n \to F$ |
| Quantile $Q(p)$: smallest $x$ with $F(x) \geq p$ | Sample quantile: $x_{(\lceil np \rceil)}$ (interpolated) | Multiple interpolation conventions exist |
| Median $Q(0.5)$ | Sample median $\tilde{x}$ | The middle order statistic |
| Parameter $\theta$ | Estimator $\hat{\theta}$ | A function of the sample that targets $\theta$ |
| Likelihood $L(\theta \mid x) = f(x \mid \theta)$ | Maximum likelihood estimator: $\hat{\theta} = \arg\max L(\theta \mid x)$ | MLE is consistent and asymptotically efficient |
| Fisher information $I(\theta)$ | Observed information $-\ell''(\hat{\theta})$ | Governs the precision of $\hat{\theta}$ |
| True value $\theta$ | Confidence interval $[\hat{\theta} - z_{\alpha/2}\,\text{SE},\; \hat{\theta} + z_{\alpha/2}\,\text{SE}]$ | The interval covers $\theta$ with probability $1 - \alpha$ before observing data |
| Moment $\mathbb{E}[X^k]$ | Sample moment $\frac{1}{n}\sum x_i^k$ | Method of moments equates population and sample moments |
| Skewness $\mathbb{E}[(X-\mu)^3]/\sigma^3$ | Sample skewness $g_1$ | Third standardised moment |
| Kurtosis $\mathbb{E}[(X-\mu)^4]/\sigma^4$ | Sample kurtosis $g_2$ | Fourth standardised moment |
| $\mu = \mu_0$ (hypothesis) | Test statistic $T$, p-value $p$ | Hypothesis testing quantifies evidence against $H_0$ |
