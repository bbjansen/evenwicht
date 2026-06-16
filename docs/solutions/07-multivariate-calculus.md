<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 7: Multivariate Calculus

**Exercise 7.1.** Compute all first-order partial derivatives of $f(x,y,z) = x^2yz + e^{xz} - \ln(y)$.

??? success "Solution"

    $$\begin{aligned}
    f_x &= \frac{\partial f}{\partial x} = 2xyz + ze^{xz}. \\
    f_y &= \frac{\partial f}{\partial y} = x^2z - \frac{1}{y}. \\
    f_z &= \frac{\partial f}{\partial z} = x^2y + xe^{xz}.
    \end{aligned}$$

---

**Exercise 7.2.** Gradient of $f(x,y) = 3x^2 - 2xy + y^3$ at $(1, -1)$.

??? success "Solution"

    $$\begin{aligned}
    f_x &= 6x - 2y, \quad f_y = -2x + 3y^2. \\
    \nabla f &= (6x - 2y,\; -2x + 3y^2).
    \end{aligned}$$

    At $(1, -1)$:

    $$\nabla f(1, -1) = (6(1) - 2(-1),\; -2(1) + 3(1)) = (8, 1).$$

---

**Exercise 7.3.** Hessian of $f(x,y) = x^3 + x^2y - 2y^2$.

??? success "Solution"

    First partials: $f_x = 3x^2 + 2xy$, $f_y = x^2 - 4y$.

    Second partials:

    $$\begin{aligned}
    f_{xx} &= 6x + 2y, \quad f_{xy} = 2x, \quad f_{yx} = 2x, \quad f_{yy} = -4. \\
    H_f &= \begin{pmatrix} 6x + 2y & 2x \\ 2x & -4 \end{pmatrix}.
    \end{aligned}$$

    Since $f_{xy} = f_{yx} = 2x$, the Hessian is symmetric (as guaranteed by Schwarz's theorem, since all second partials are continuous). $\checkmark$

---

**Exercise 7.4.** Gradient of $f(x,y) = e^{x^2 + y^2}$ points radially outward.

??? success "Solution"

    $$\begin{aligned}
    f_x &= 2x\,e^{x^2 + y^2}, \quad f_y = 2y\,e^{x^2 + y^2}. \\
    \nabla f &= 2e^{x^2 + y^2}(x, y).
    \end{aligned}$$

    Since $e^{x^2 + y^2} > 0$ for all $(x,y)$, the gradient is $\nabla f = c(x, y)$ where $c = 2e^{x^2 + y^2} > 0$. This is a positive scalar multiple of the position vector $(x,y)$, confirming that $\nabla f$ points radially outward from the origin (at every point except the origin, where $\nabla f = \mathbf{0}$).

    **Implication for level curves:** Since the gradient is always perpendicular to level curves and always points radially, the level curves $e^{x^2 + y^2} = c$ must be circles centred at the origin (i.e., $x^2 + y^2 = \ln c$).

---

**Exercise 7.5.** Verify Euler's theorem for $f(x,y) = x^{2/3}y^{1/3}$.

??? success "Solution"

    This function is homogeneous of degree $k = 2/3 + 1/3 = 1$.

    Euler's theorem states $x f_x + y f_y = kf = f$.

    Compute the partial derivatives:

    $$f_x = \frac{2}{3}x^{-1/3}y^{1/3}, \quad f_y = \frac{1}{3}x^{2/3}y^{-2/3}.$$

    Left side:

    $$xf_x + yf_y = x \cdot \frac{2}{3}x^{-1/3}y^{1/3} + y \cdot \frac{1}{3}x^{2/3}y^{-2/3} = \frac{2}{3}x^{2/3}y^{1/3} + \frac{1}{3}x^{2/3}y^{1/3} = x^{2/3}y^{1/3} = f(x,y).$$

    Both sides equal $f(x,y)$. $\checkmark$

---

**Exercise 7.6.** Multivariate chain rule: $w = x^2 + y^2 + z^2$, $x = e^t$, $y = e^{-t}$, $z = t$.

??? success "Solution"

    **Via chain rule:**

    $$\frac{dw}{dt} = \frac{\partial w}{\partial x}\frac{dx}{dt} + \frac{\partial w}{\partial y}\frac{dy}{dt} + \frac{\partial w}{\partial z}\frac{dz}{dt} = 2x \cdot e^t + 2y \cdot (-e^{-t}) + 2z \cdot 1.$$

    Substituting $x = e^t$, $y = e^{-t}$, $z = t$:

    $$\frac{dw}{dt} = 2e^t \cdot e^t + 2e^{-t}(-e^{-t}) + 2t = 2e^{2t} - 2e^{-2t} + 2t.$$

    **Direct verification:** $w(t) = e^{2t} + e^{-2t} + t^2$.

    $$\frac{dw}{dt} = 2e^{2t} - 2e^{-2t} + 2t. \quad \checkmark$$

---

**Exercise 7.7.** Critical points of $f(x,y) = x^4 + y^4 - 4xy + 1$.

??? success "Solution"

    **Finding critical points:** Set $\nabla f = \mathbf{0}$:

    $$\begin{aligned}
    f_x &= 4x^3 - 4y = 0 \implies y = x^3. \\
    f_y &= 4y^3 - 4x = 0 \implies x = y^3.
    \end{aligned}$$

    Substituting $y = x^3$ into $x = y^3$: $x = (x^3)^3 = x^9$, so $x^9 - x = 0$, i.e., $x(x^8 - 1) = 0$. Real solutions: $x = 0$, $x = 1$, $x = -1$.

    Critical points: $(0, 0)$, $(1, 1)$, $(-1, -1)$.

    **Hessian:**

    $$H_f = \begin{pmatrix} 12x^2 & -4 \\ -4 & 12y^2 \end{pmatrix}.$$

    **At $(0,0)$:** $H = \begin{pmatrix} 0 & -4 \\ -4 & 0 \end{pmatrix}$. $\det(H) = 0 - 16 = -16 < 0$. **Saddle point.**

    **At $(1,1)$:** $H = \begin{pmatrix} 12 & -4 \\ -4 & 12 \end{pmatrix}$. $\det(H) = 144 - 16 = 128 > 0$ and $H_{11} = 12 > 0$. **Local minimum.** $f(1,1) = 1 + 1 - 4 + 1 = -1$.

    **At $(-1,-1)$:** $H = \begin{pmatrix} 12 & -4 \\ -4 & 12 \end{pmatrix}$. Same Hessian as $(1,1)$. $\det(H) = 128 > 0$ and $H_{11} = 12 > 0$. **Local minimum.** $f(-1,-1) = 1 + 1 - 4 + 1 = -1$.

---

**Exercise 7.8.** Gradient and Hessian of the quadratic form $f(\mathbf{x}) = \frac{1}{2}\mathbf{x}^TA\mathbf{x} + \mathbf{b}^T\mathbf{x} + c$.

??? success "Solution"

    *Proof.* Write $f$ in component form:

    $$f(\mathbf{x}) = \frac{1}{2}\sum_{i,j} A_{ij}x_i x_j + \sum_i b_i x_i + c.$$

    **Gradient:** Differentiating with respect to $x_k$:

    $$\frac{\partial f}{\partial x_k} = \frac{1}{2}\sum_j A_{kj}x_j + \frac{1}{2}\sum_i A_{ik}x_i + b_k.$$

    Since $A$ is symmetric ($A_{ik} = A_{ki}$), both sums equal $\sum_j A_{kj}x_j = (A\mathbf{x})_k$. Therefore:

    $$\frac{\partial f}{\partial x_k} = (A\mathbf{x})_k + b_k, \quad \text{so} \quad \nabla f(\mathbf{x}) = A\mathbf{x} + \mathbf{b}.$$

    **Hessian:** Differentiating again:

    $$\frac{\partial^2 f}{\partial x_k \partial x_l} = A_{kl}.$$

    Therefore $H_f = A$, a constant matrix.

    **Minimiser:** Setting $\nabla f = \mathbf{0}$: $A\mathbf{x} + \mathbf{b} = \mathbf{0}$, so $\mathbf{x}^* = -A^{-1}\mathbf{b}$ (which exists since $A$ is positive definite and hence invertible).

    Since $H_f = A$ is positive definite, the second-order sufficient condition for a local minimum is satisfied. Moreover, for a quadratic with positive definite Hessian, any local minimum is the unique global minimum.

    $\square$

---
