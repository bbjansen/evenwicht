<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 23: Operator Algebra

**Exercise 23.1.** Let $T = 2D + I$. Compute $T(e^x)$ and $T(\sin x)$.

??? success "Solution"

    $T(e^x) = 2D(e^x) + I(e^x) = 2e^x + e^x = 3e^x$.

    $T(\sin x) = 2D(\sin x) + I(\sin x) = 2\cos x + \sin x$.

    $\square$

---

**Exercise 23.2.** Verify that $(D + I)(D + 2I) = D^2 + 3D + 2I$ by expanding and applying to $f(x) = x^2$.

??? success "Solution"

    **Algebraic expansion:**

    $(D + I)(D + 2I) = D(D + 2I) + I(D + 2I) = D^2 + 2D + D + 2I = D^2 + 3D + 2I$. $\checkmark$

    **Verification on $f(x) = x^2$:**

    Left-hand side: First compute $(D + 2I)(x^2) = D(x^2) + 2x^2 = 2x + 2x^2$. Then $(D + I)(2x + 2x^2) = D(2x + 2x^2) + (2x + 2x^2) = (2 + 4x) + (2x + 2x^2) = 2x^2 + 6x + 2$.

    Right-hand side: $D^2(x^2) + 3D(x^2) + 2I(x^2) = 2 + 3(2x) + 2x^2 = 2x^2 + 6x + 2$.

    Both sides equal $2x^2 + 6x + 2$. $\checkmark$

    $\square$

---

**Exercise 23.3.** Compute $(I - 0.6L)(x_t)$ for $x_t = t^2$ at $t = 3$.

??? success "Solution"

    $(I - 0.6L)(x_t) = x_t - 0.6 x_{t-1}$.

    At $t = 3$: $x_3 - 0.6 x_2 = 9 - 0.6(4) = 9 - 2.4 = 6.6$.

    $\square$

---

**Exercise 23.4.** Compute the commutator $[D, M_{x^2}]$ and apply to $f(x) = e^x$.

??? success "Solution"

    $[D, M_{x^2}] = DM_{x^2} - M_{x^2}D$.

    Apply to a generic $f$:

    $DM_{x^2}(f) = D(x^2 f) = 2xf + x^2 f'$ (by the product rule).

    $M_{x^2}D(f) = x^2 f'$.

    $[D, M_{x^2}](f) = (2xf + x^2 f') - x^2 f' = 2xf = M_{2x}(f)$.

    So $[D, M_{x^2}] = M_{2x}$ (the "multiply by $2x$" operator).

    **Apply to $f(x) = e^x$:** $[D, M_{x^2}](e^x) = 2xe^x$.

    **Direct verification:** $D(x^2 e^x) = 2xe^x + x^2 e^x$ and $x^2 D(e^x) = x^2 e^x$. Difference: $2xe^x$. $\checkmark$

    $\square$

---

**Exercise 23.5.** Factor $D^2 + \omega^2 I$ over $\mathbb{C}$ and solve $(D^2 + \omega^2 I)y = 0$.

??? success "Solution"

    $D^2 + \omega^2 I = (D - i\omega I)(D + i\omega I)$.

    The factored equation $(D - i\omega)(D + i\omega)y = 0$ has solutions from each factor:

    $(D + i\omega)y = 0 \implies y' = -i\omega y \implies y = c_1 e^{-i\omega x}$.

    $(D - i\omega)y = 0 \implies y' = i\omega y \implies y = c_2 e^{i\omega x}$.

    General complex solution: $y = c_1 e^{i\omega x} + c_2 e^{-i\omega x}$.

    Using Euler's formula to write the general real solution:

    $$y(x) = A\cos(\omega x) + B\sin(\omega x),$$

    where $A = c_1 + c_2$ and $B = i(c_1 - c_2)$ are real constants. This is the familiar harmonic oscillator solution with angular frequency $\omega$.

    $\square$

---

**Exercise 23.6.** Prove the exponential shift theorem: $p(D)(e^{\lambda x}) = p(\lambda) e^{\lambda x}$.

??? success "Solution"

    First observe that $D^n(e^{\lambda x}) = \lambda^n e^{\lambda x}$ for all $n \geq 0$. This follows by induction: $D(e^{\lambda x}) = \lambda e^{\lambda x}$, and if $D^k(e^{\lambda x}) = \lambda^k e^{\lambda x}$, then $D^{k+1}(e^{\lambda x}) = D(\lambda^k e^{\lambda x}) = \lambda^{k+1}e^{\lambda x}$.

    Now let $p(D) = \sum_{k=0}^n a_k D^k$ be a polynomial operator. Then:

    $$p(D)(e^{\lambda x}) = \sum_{k=0}^n a_k D^k(e^{\lambda x}) = \sum_{k=0}^n a_k \lambda^k e^{\lambda x} = e^{\lambda x}\sum_{k=0}^n a_k \lambda^k = p(\lambda) e^{\lambda x}.$$

    This shows that $e^{\lambda x}$ is an eigenfunction of any polynomial operator $p(D)$, with eigenvalue $p(\lambda)$. In particular, $e^{\lambda x}$ is a solution of $p(D)y = 0$ if and only if $\lambda$ is a root of the characteristic polynomial $p(\lambda) = 0$.

    $\square$

---

**Exercise 23.7.** Prove that an involution $T$ ($T^2 = I$) has eigenvalues $\pm 1$ only.

??? success "Solution"

    Suppose $T\mathbf{v} = \lambda \mathbf{v}$ for some eigenvector $\mathbf{v} \neq 0$ and eigenvalue $\lambda$.

    Apply $T$ again: $T^2 \mathbf{v} = T(\lambda \mathbf{v}) = \lambda T\mathbf{v} = \lambda^2 \mathbf{v}$.

    But $T^2 = I$, so $T^2 \mathbf{v} = I\mathbf{v} = \mathbf{v}$.

    Therefore $\lambda^2 \mathbf{v} = \mathbf{v}$, and since $\mathbf{v} \neq 0$, it follows that $\lambda^2 = 1$, hence $\lambda = +1$ or $\lambda = -1$.

    Equivalently: $T^2 = I$ means $T$ satisfies the polynomial $p(\lambda) = \lambda^2 - 1 = (\lambda - 1)(\lambda + 1)$. The minimal polynomial of $T$ divides $p$, so all eigenvalues are roots of $p$, namely $\pm 1$.

    $\square$

---

**Exercise 23.8.** Verify the operator exponential $e^{aD}(x^3) = (x + a)^3$ by expanding to third order.

??? success "Solution"

    $e^{aD} = \sum_{k=0}^{\infty} \frac{(aD)^k}{k!} = I + aD + \frac{a^2 D^2}{2} + \frac{a^3 D^3}{6} + \cdots$

    Apply to $x^3$:

    $I(x^3) = x^3$.

    $aD(x^3) = a \cdot 3x^2 = 3ax^2$.

    $\frac{a^2}{2}D^2(x^3) = \frac{a^2}{2} \cdot 6x = 3a^2 x$.

    $\frac{a^3}{6}D^3(x^3) = \frac{a^3}{6} \cdot 6 = a^3$.

    $\frac{a^4}{24}D^4(x^3) = 0$ (and all higher terms vanish since $D^k(x^3) = 0$ for $k \geq 4$).

    Sum: $x^3 + 3ax^2 + 3a^2 x + a^3 = (x + a)^3$. $\checkmark$

    **Connection to the binomial theorem:**

    $(x + a)^3 = \sum_{k=0}^{3}\binom{3}{k}x^{3-k}a^k = x^3 + 3x^2 a + 3xa^2 + a^3$.

    The operator expansion $e^{aD}(x^n) = \sum_{k=0}^n \frac{a^k}{k!}D^k(x^n) = \sum_{k=0}^n \frac{a^k}{k!} \cdot \frac{n!}{(n-k)!}x^{n-k} = \sum_{k=0}^n \binom{n}{k}a^k x^{n-k} = (x+a)^n$.

    This is precisely the binomial theorem. The operator identity $e^{aD}f(x) = f(x + a)$ (Taylor's theorem in operator form, Theorem 23.26) applied to $f(x) = x^n$ yields the binomial expansion. In this sense, the binomial theorem is a special case of the operator exponential applied to monomials.

    $\square$

---

**Exercise 23.9.** Verify the Jacobi identity for $A = D$, $B = M_x$, $C = M_{x^2}$.

??? success "Solution"

    First compute the inner commutators using the product rule.

    $[B, C] = [M_x, M_{x^2}] = M_x M_{x^2} - M_{x^2} M_x$. Both sides produce $M_{x^3}$, so $[B, C] = O$.

    $[C, A] = [M_{x^2}, D]$. From Exercise 23.4, $[D, M_{x^2}] = M_{2x}$, so $[M_{x^2}, D] = -M_{2x}$.

    $[A, B] = [D, M_x] = I$ (canonical commutation relation, Example 23.17).

    Now compute the outer commutators:

    $[A, [B, C]] = [D, O] = O$.

    $[B, [C, A]] = [M_x, -M_{2x}] = -[M_x, M_{2x}] = O$ (multiplication operators commute).

    $[C, [A, B]] = [M_{x^2}, I] = O$ (every operator commutes with $I$).

    Sum: $O + O + O = O$. The Jacobi identity is verified.

    $\square$

---

**Exercise 23.10.** Verify the semigroup property $e^{(s+t)A} = e^{sA}e^{tA}$ for $A = \begin{pmatrix} 0 & 1 \\ -1 & 0 \end{pmatrix}$, $s = 1$, $t = 2$.

??? success "Solution"

    First observe that $A^2 = \begin{pmatrix} 0 & 1 \\ -1 & 0 \end{pmatrix}\begin{pmatrix} 0 & 1 \\ -1 & 0 \end{pmatrix} = \begin{pmatrix} -1 & 0 \\ 0 & -1 \end{pmatrix} = -I$.

    Therefore $A^3 = A^2 \cdot A = -A$, $A^4 = I$, and the pattern repeats with period 4. The matrix exponential series becomes:

    $$e^{tA} = I + tA + \frac{t^2 A^2}{2!} + \frac{t^3 A^3}{3!} + \cdots = \left(1 - \frac{t^2}{2!} + \frac{t^4}{4!} - \cdots\right)I + \left(t - \frac{t^3}{3!} + \frac{t^5}{5!} - \cdots\right)A = \cos(t)\,I + \sin(t)\,A.$$

    **Left-hand side:** $e^{3A} = \cos(3)\,I + \sin(3)\,A = \begin{pmatrix} \cos 3 & \sin 3 \\ -\sin 3 & \cos 3 \end{pmatrix}$.

    **Right-hand side:** $e^{A}e^{2A} = (\cos 1\,I + \sin 1\,A)(\cos 2\,I + \sin 2\,A)$.

    Expand: $\cos 1 \cos 2\,I + \cos 1 \sin 2\,A + \sin 1 \cos 2\,A + \sin 1 \sin 2\,A^2$.

    Since $A^2 = -I$: $= (\cos 1 \cos 2 - \sin 1 \sin 2)\,I + (\cos 1 \sin 2 + \sin 1 \cos 2)\,A = \cos 3\,I + \sin 3\,A$.

    Both sides equal $\cos 3\,I + \sin 3\,A$. $\checkmark$

    $\square$

---
