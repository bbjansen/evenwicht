<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 11: Unconstrained Optimisation

**Exercise 11.1.** Find and classify the critical points of $f(x) = x^3 - 12x + 1$.

??? success "Solution"

    $f'(x) = 3x^2 - 12 = 3(x^2 - 4) = 0 \implies x = \pm 2$.

    $f''(x) = 6x$.

    At $x = 2$: $f''(2) = 12 > 0$. **Local minimum.** $f(2) = 8 - 24 + 1 = -15$.

    At $x = -2$: $f''(-2) = -12 < 0$. **Local maximum.** $f(-2) = -8 + 24 + 1 = 17$.

---

**Exercise 11.2.** Classify the critical point of $f(x,y) = 3x^2 + 2y^2 + 2xy - 4x - 6y + 10$.

??? success "Solution"

    **Finding the critical point:** $\nabla f = \mathbf{0}$:

    $$\begin{aligned}
    f_x &= 6x + 2y - 4 = 0 \\
    f_y &= 4y + 2x - 6 = 0
    \end{aligned}$$

    From the second equation: $x = 3 - 2y$. Substituting: $6(3 - 2y) + 2y - 4 = 0 \implies 18 - 12y + 2y - 4 = 0 \implies -10y = -14 \implies y = 7/5$.

    $x = 3 - 14/5 = 1/5$.

    Critical point: $(1/5, 7/5)$.

    **Hessian:**

    $$H = \begin{pmatrix} 6 & 2 \\ 2 & 4 \end{pmatrix}.$$

    **Discriminant test:** $\det(H) = 24 - 4 = 20 > 0$ and $H_{11} = 6 > 0$. This is a **local minimum**.

    **Eigenvalue test:** $\det(H - \lambda I) = (6-\lambda)(4-\lambda) - 4 = \lambda^2 - 10\lambda + 20 = 0$. $\lambda = \frac{10 \pm \sqrt{20}}{2} = 5 \pm \sqrt{5}$, i.e., $\lambda_1 \approx 2.76$ and $\lambda_2 \approx 7.24$. Both positive, confirming **positive definiteness** and hence a local minimum.

---

**Exercise 11.3.** Show $f(x) = e^x - x$ is strictly convex and find its global minimum.

??? success "Solution"

    $f'(x) = e^x - 1$, $f''(x) = e^x > 0$ for all $x \in \mathbb{R}$. Since $f''(x) > 0$ everywhere, $f$ is **strictly convex**.

    Setting $f'(x) = 0$: $e^x = 1 \implies x = 0$.

    Since $f$ is strictly convex, this is the unique global minimum. $f(0) = 1 - 0 = 1$.

---

**Exercise 11.4.** Apply gradient descent to $f(x,y) = 4x^2 + y^2$ starting from $(10, 10)$ with step size $\alpha = 0.1$. Perform five iterations and comment on convergence.

??? success "Solution"

    $\nabla f = (8x, 2y)$.

    The Hessian is $H = \begin{pmatrix} 8 & 0 \\ 0 & 2 \end{pmatrix}$. Eigenvalues: $\lambda_1 = 2$, $\lambda_2 = 8$. Condition number: $\kappa = 8/2 = 4$.

    Gradient descent update: $(x_{k+1}, y_{k+1}) = (x_k, y_k) - \alpha \nabla f(x_k, y_k) = (x_k - 0.8x_k, y_k - 0.2y_k) = (0.2x_k, 0.8y_k)$.

    | Iteration | $x_k$ | $y_k$ | $f(x_k, y_k)$ |
    |-----------|--------|--------|----------------|
    | 0 | 10 | 10 | 500 |
    | 1 | 2 | 8 | 80 |
    | 2 | 0.4 | 6.4 | 41.6 |
    | 3 | 0.08 | 5.12 | 26.24 |
    | 4 | 0.016 | 4.096 | 16.78 |
    | 5 | 0.0032 | 3.2768 | 10.74 |

    The $x$-component converges rapidly (multiplied by $0.2$ each step), while the $y$-component converges slowly (multiplied by $0.8$). This shows the effect of $\kappa = 4$: with the optimal step size $\alpha = 2/(\lambda_1 + \lambda_2) = 0.2$, the convergence factor would be $\rho = (\kappa-1)/(\kappa+1) = 3/5 = 0.6$. With $\alpha = 0.1$, the effective convergence factor in the $y$-direction is $|1 - 0.1 \times 2| = 0.8$, which is slower than optimal.

---

**Exercise 11.5.** Apply Newton's method to $f(x) = \ln(1 + e^x) + \frac{1}{2}(x-3)^2$ starting from $x_0 = 0$.

??? success "Solution"

    $f'(x) = \frac{e^x}{1 + e^x} + (x - 3) = \sigma(x) + x - 3$, where $\sigma(x) = \frac{e^x}{1+e^x}$ is the sigmoid function.

    $f''(x) = \sigma(x)(1 - \sigma(x)) + 1 > 0$ for all $x$ (since $\sigma(x)(1-\sigma(x)) \geq 0$ and $1 > 0$). So $f$ is **strictly convex**. $\checkmark$

    Newton's update: $x_{k+1} = x_k - \frac{f'(x_k)}{f''(x_k)}$.

    **Iteration 0:** $x_0 = 0$. $\sigma(0) = 0.5$. $f'(0) = 0.5 + 0 - 3 = -2.5$. $f''(0) = 0.5 \times 0.5 + 1 = 1.25$.

    $x_1 = 0 - (-2.5/1.25) = 2.0$.

    **Iteration 1:** $x_1 = 2$. $\sigma(2) = e^2/(1+e^2) \approx 0.8808$. $f'(2) = 0.8808 + 2 - 3 = -0.1192$. $f''(2) = 0.8808 \times 0.1192 + 1 \approx 1.1050$.

    $x_2 = 2 - (-0.1192/1.1050) \approx 2.1079$.

    **Iteration 2:** $x_2 \approx 2.1079$. $\sigma(2.1079) \approx 0.8916$. $f'(2.1079) \approx 0.8916 + 2.1079 - 3 = -0.0005$. $f''(2.1079) \approx 0.8916 \times 0.1084 + 1 \approx 1.0967$.

    $x_3 \approx 2.1079 - (-0.0005/1.0967) \approx 2.1084$.

    The method converges rapidly (quadratic convergence near the minimum). The minimum is at $x^* \approx 2.1084$.

---

**Exercise 11.6.** For the Rosenbrock function $f(x,y) = (1-x)^2 + 100(y - x^2)^2$, verify that $(1,1)$ is the unique global minimum.

??? success "Solution"

    **Gradient:**

    $$\begin{aligned}
    f_x &= -2(1-x) + 100 \cdot 2(y - x^2)(-2x) = -2(1-x) - 400x(y - x^2). \\
    f_y &= 200(y - x^2).
    \end{aligned}$$

    **At $(1,1)$:** $f_x = 0 - 0 = 0$, $f_y = 200(1-1) = 0$. So $(1,1)$ is a critical point. $\checkmark$

    **Uniqueness:** From $f_y = 0$: $y = x^2$. Substituting into $f_x = 0$: $-2(1-x) - 400x(x^2 - x^2) = -2(1-x) = 0$, so $x = 1$ and $y = 1$. The critical point is unique.

    **Hessian:**

    $$\begin{aligned}
    f_{xx} &= 2 - 400(y - x^2) + 800x^2 = 2 - 400y + 400x^2 + 800x^2 = 2 + 1200x^2 - 400y. \\
    f_{xy} &= -400x. \\
    f_{yy} &= 200.
    \end{aligned}$$

    At $(1,1)$:

    $$H = \begin{pmatrix} 2 + 1200 - 400 & -400 \\ -400 & 200 \end{pmatrix} = \begin{pmatrix} 802 & -400 \\ -400 & 200 \end{pmatrix}.$$

    $\det(H) = 802 \times 200 - 160000 = 160400 - 160000 = 400 > 0$ and $H_{11} = 802 > 0$. So $H$ is **positive definite**, confirming a local (and global) minimum.

    **Eigenvalues of $H$:** $\lambda^2 - 1002\lambda + 400 = 0$. $\lambda = \frac{1002 \pm \sqrt{1002^2 - 1600}}{2} = \frac{1002 \pm \sqrt{1002404}}{2} \approx \frac{1002 \pm 1001.2}{2}$.

    $\lambda_1 \approx 0.4$, $\lambda_2 \approx 1001.6$.

    **Condition number:** $\kappa \approx 1001.6/0.4 \approx 2504$. This very large condition number predicts that gradient descent will converge extremely slowly, oscillating in a narrow curved valley. The convergence factor is approximately $\rho \approx (\kappa - 1)/(\kappa + 1) \approx 0.9992$, meaning thousands of iterations to reduce the error by a factor of $e$.

---

**Exercise 11.7.** Prove the first-order characterisation of convexity: a differentiable function $f$ is convex if and only if $f(\mathbf{y}) \geq f(\mathbf{x}) + \nabla f(\mathbf{x})^T(\mathbf{y} - \mathbf{x})$ for all $\mathbf{x}, \mathbf{y}$. Deduce that any critical point of a convex function is a global minimum.

??? success "Solution"

    *Proof.* Let $f$ be convex and differentiable. By the definition of convexity, for any $\mathbf{x}, \mathbf{y}$ and $t \in [0, 1]$:

    $$f((1-t)\mathbf{x} + t\mathbf{y}) \leq (1-t)f(\mathbf{x}) + tf(\mathbf{y}).$$

    Rearranging:

    $$f(\mathbf{x} + t(\mathbf{y} - \mathbf{x})) - f(\mathbf{x}) \leq t[f(\mathbf{y}) - f(\mathbf{x})].$$

    Dividing by $t > 0$:

    $$\frac{f(\mathbf{x} + t(\mathbf{y} - \mathbf{x})) - f(\mathbf{x})}{t} \leq f(\mathbf{y}) - f(\mathbf{x}).$$

    Taking $t \to 0^+$, the left side is the directional derivative of $f$ at $\mathbf{x}$ in the direction $\mathbf{y} - \mathbf{x}$, which equals $\nabla f(\mathbf{x})^T(\mathbf{y} - \mathbf{x})$. Therefore:

    $$\nabla f(\mathbf{x})^T(\mathbf{y} - \mathbf{x}) \leq f(\mathbf{y}) - f(\mathbf{x}),$$

    which gives $f(\mathbf{y}) \geq f(\mathbf{x}) + \nabla f(\mathbf{x})^T(\mathbf{y} - \mathbf{x})$.

    $\square$

    **Critical points of convex functions are global minima:** Suppose $\nabla f(\mathbf{x}^*) = \mathbf{0}$. By the inequality just proved, for any $\mathbf{y}$:

    $$f(\mathbf{y}) \geq f(\mathbf{x}^*) + \nabla f(\mathbf{x}^*)^T(\mathbf{y} - \mathbf{x}^*) = f(\mathbf{x}^*) + \mathbf{0}^T(\mathbf{y} - \mathbf{x}^*) = f(\mathbf{x}^*).$$

    So $f(\mathbf{y}) \geq f(\mathbf{x}^*)$ for all $\mathbf{y}$, meaning $\mathbf{x}^*$ is a global minimum.

    $\square$

---

**Exercise 11.8.** Derive the optimal step size and convergence factor for gradient descent on $f(\mathbf{x}) = \frac{1}{2}\mathbf{x}^TA\mathbf{x}$ where $A$ is $2 \times 2$ symmetric positive definite.

??? success "Solution"

    Let $A$ be $2 \times 2$ symmetric positive definite with eigenvalues $0 < \lambda_1 < \lambda_2$ and orthonormal eigenvectors $\mathbf{q}_1, \mathbf{q}_2$. Write $\mathbf{x}_k = a_k\mathbf{q}_1 + b_k\mathbf{q}_2$.

    The gradient is $\nabla f(\mathbf{x}) = A\mathbf{x}$, so the gradient descent update is:

    $$\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha A\mathbf{x}_k = (I - \alpha A)\mathbf{x}_k.$$

    In the eigenbasis:

    $$a_{k+1} = (1 - \alpha\lambda_1)a_k, \quad b_{k+1} = (1 - \alpha\lambda_2)b_k.$$

    So $a_k = (1 - \alpha\lambda_1)^k a_0$ and $b_k = (1 - \alpha\lambda_2)^k b_0$.

    The convergence factor is $\rho = \max(|1 - \alpha\lambda_1|, |1 - \alpha\lambda_2|)$.

    To minimise $\rho$, the requirement is $|1 - \alpha\lambda_1| = |1 - \alpha\lambda_2|$. Since $\lambda_1 < \lambda_2$, $1 - \alpha\lambda_1 > 1 - \alpha\lambda_2$. The optimal $\alpha$ makes $1 - \alpha\lambda_1 = -(1 - \alpha\lambda_2)$, i.e.:

    $$1 - \alpha\lambda_1 = \alpha\lambda_2 - 1 \implies 2 = \alpha(\lambda_1 + \lambda_2) \implies \alpha = \frac{2}{\lambda_1 + \lambda_2}.$$

    The corresponding convergence factor is:

    $$\rho = 1 - \alpha\lambda_1 = 1 - \frac{2\lambda_1}{\lambda_1 + \lambda_2} = \frac{\lambda_2 - \lambda_1}{\lambda_1 + \lambda_2} = \frac{\kappa - 1}{\kappa + 1},$$

    where $\kappa = \lambda_2/\lambda_1$.

    **When $\kappa = 1$:** $A = \lambda_1 I$, $\alpha = 2/(2\lambda_1) = 1/\lambda_1$, and $\rho = 0$. The update becomes $\mathbf{x}_1 = \mathbf{x}_0 - (1/\lambda_1)(\lambda_1\mathbf{x}_0) = \mathbf{0}$. Gradient descent converges in **one step**.

    **As $\kappa \to \infty$:** $\rho \to 1$, so convergence becomes arbitrarily slow. Each iteration reduces the error by a factor close to $1$. This explains why ill-conditioned problems (large $\kappa$) are difficult for gradient descent.

    $\square$

---
