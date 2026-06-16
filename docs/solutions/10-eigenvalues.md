<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 10: Eigenvalues

**Exercise 10.1.** Find the eigenvalues and eigenvectors of $A = \begin{pmatrix} 3 & 0 \\ 0 & 7 \end{pmatrix}$.

??? success "Solution"

    The characteristic polynomial is $\det(A - \lambda I) = (3 - \lambda)(7 - \lambda) = 0$.

    Eigenvalues: $\lambda_1 = 3$, $\lambda_2 = 7$.

    For $\lambda_1 = 3$: $(A - 3I)\mathbf{v} = \begin{pmatrix} 0 & 0 \\ 0 & 4 \end{pmatrix}\mathbf{v} = \mathbf{0}$. Eigenvectors: $\mathbf{v}_1 = (1, 0)^T$ (and scalar multiples).

    For $\lambda_2 = 7$: $(A - 7I)\mathbf{v} = \begin{pmatrix} -4 & 0 \\ 0 & 0 \end{pmatrix}\mathbf{v} = \mathbf{0}$. Eigenvectors: $\mathbf{v}_2 = (0, 1)^T$.

    **General rule:** For a diagonal matrix $D = \operatorname{diag}(d_1, d_2, \ldots, d_n)$, the eigenvalues are the diagonal entries $d_1, \ldots, d_n$ and the eigenvectors are the standard basis vectors $\mathbf{e}_1, \ldots, \mathbf{e}_n$.

---

**Exercise 10.2.** Find the eigenvalues of $B = \begin{pmatrix} 1 & 4 \\ 2 & 3 \end{pmatrix}$.

??? success "Solution"

    $\det(B - \lambda I) = (1-\lambda)(3-\lambda) - 8 = \lambda^2 - 4\lambda + 3 - 8 = \lambda^2 - 4\lambda - 5 = (\lambda - 5)(\lambda + 1) = 0$.

    Eigenvalues: $\lambda_1 = 5$, $\lambda_2 = -1$.

    **Verification:**

    $\operatorname{tr}(B) = 1 + 3 = 4 = 5 + (-1) = \lambda_1 + \lambda_2$. $\checkmark$

    $\det(B) = 3 - 8 = -5 = 5 \cdot (-1) = \lambda_1\lambda_2$. $\checkmark$

---

**Exercise 10.3.** Find the eigenvalues and eigenvectors of $C = \begin{pmatrix} 3 & 1 \\ 0 & 3 \end{pmatrix}$, and determine whether $C$ is diagonalisable.

??? success "Solution"

    Since $C$ is upper triangular, its eigenvalues are the diagonal entries: $\lambda = 3$ (with algebraic multiplicity 2).

    For $\lambda = 3$: $(C - 3I)\mathbf{v} = \begin{pmatrix} 0 & 1 \\ 0 & 0 \end{pmatrix}\mathbf{v} = \mathbf{0}$, which gives $v_2 = 0$. The eigenspace is $\operatorname{span}\{(1, 0)^T\}$, which has dimension 1 (geometric multiplicity = 1).

    Since the geometric multiplicity (1) is strictly less than the algebraic multiplicity (2), $C$ is **not diagonalisable**. This matrix is a Jordan block of size 2 with eigenvalue 3.

---

**Exercise 10.4.** Find the eigenvalues and eigenvectors of $A = \begin{pmatrix} 1 & 2 \\ 2 & 4 \end{pmatrix}$.

??? success "Solution"

    $\det(A - \lambda I) = (1 - \lambda)(4 - \lambda) - 4 = \lambda^2 - 5\lambda + 0 = \lambda(\lambda - 5) = 0$.

    Eigenvalues: $\lambda_1 = 0$, $\lambda_2 = 5$.

    **Implications of $\lambda_1 = 0$:** $\det(A) = 0 \cdot 5 = 0$, so $A$ is singular (not invertible). $\checkmark$ (Indeed $\det(A) = 4 - 4 = 0$.)

    **Eigenvectors:**

    For $\lambda_1 = 0$: $A\mathbf{v} = \mathbf{0}$: $\begin{pmatrix} 1 & 2 \\ 2 & 4 \end{pmatrix}\mathbf{v} = \mathbf{0}$. Row reduction gives $v_1 + 2v_2 = 0$. Eigenvector: $\mathbf{v}_1 = (2, -1)^T$.

    For $\lambda_2 = 5$: $(A - 5I)\mathbf{v} = \begin{pmatrix} -4 & 2 \\ 2 & -1 \end{pmatrix}\mathbf{v} = \mathbf{0}$. Row reduction gives $-4v_1 + 2v_2 = 0$, i.e., $v_2 = 2v_1$. Eigenvector: $\mathbf{v}_2 = (1, 2)^T$.

    **Orthogonality check:** $\mathbf{v}_1 \cdot \mathbf{v}_2 = 2(1) + (-1)(2) = 0$. $\checkmark$ The eigenvectors are orthogonal, as guaranteed by the spectral theorem for symmetric matrices.

---

**Exercise 10.5.** Diagonalise $M = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$ and compute $M^{10}$.

??? success "Solution"

    $\det(M - \lambda I) = -\lambda^2 + 1 = 0$, so $\lambda_1 = 1$, $\lambda_2 = -1$.

    For $\lambda_1 = 1$: $(M - I)\mathbf{v} = \begin{pmatrix} -1 & 1 \\ 1 & -1 \end{pmatrix}\mathbf{v} = \mathbf{0}$. Eigenvector: $\mathbf{v}_1 = (1, 1)^T$.

    For $\lambda_2 = -1$: $(M + I)\mathbf{v} = \begin{pmatrix} 1 & 1 \\ 1 & 1 \end{pmatrix}\mathbf{v} = \mathbf{0}$. Eigenvector: $\mathbf{v}_2 = (1, -1)^T$.

    $$P = \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}, \quad D = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}.$$

    $P^{-1} = \frac{1}{-2}\begin{pmatrix} -1 & -1 \\ -1 & 1 \end{pmatrix} = \frac{1}{2}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$.

    $M = PDP^{-1}$, so $M^{10} = PD^{10}P^{-1}$.

    $D^{10} = \begin{pmatrix} 1^{10} & 0 \\ 0 & (-1)^{10} \end{pmatrix} = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix} = I$.

    Therefore $M^{10} = PIP^{-1} = I = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}$.

---

**Exercise 10.6.** A $3 \times 3$ matrix has eigenvalues $\lambda_1 = 2$, $\lambda_2 = -1$, $\lambda_3 = 3$. Find its trace, determinant and the eigenvalues of $A^2$, $A^{-1}$ and $A + 4I$.

??? success "Solution"

    **(a)** $\operatorname{tr}(A) = \lambda_1 + \lambda_2 + \lambda_3 = 2 + (-1) + 3 = 4$.

    **(b)** $\det(A) = \lambda_1\lambda_2\lambda_3 = 2 \cdot (-1) \cdot 3 = -6$.

    **(c)** Eigenvalues of $A^2$: $\lambda_1^2 = 4$, $\lambda_2^2 = 1$, $\lambda_3^2 = 9$. (If $A\mathbf{v} = \lambda\mathbf{v}$, then $A^2\mathbf{v} = \lambda^2\mathbf{v}$.)

    **(d)** Eigenvalues of $A^{-1}$: $1/\lambda_1 = 1/2$, $1/\lambda_2 = -1$, $1/\lambda_3 = 1/3$. ($A$ is invertible since $\det(A) \neq 0$; from $A\mathbf{v} = \lambda\mathbf{v}$, $\mathbf{v} = \lambda A^{-1}\mathbf{v}$, so $A^{-1}\mathbf{v} = (1/\lambda)\mathbf{v}$.)

    **(e)** Eigenvalues of $A + 4I$: $\lambda_1 + 4 = 6$, $\lambda_2 + 4 = 3$, $\lambda_3 + 4 = 7$. ($(A+4I)\mathbf{v} = A\mathbf{v} + 4\mathbf{v} = (\lambda + 4)\mathbf{v}$.)

---

**Exercise 10.7.** Prove that eigenvectors corresponding to distinct eigenvalues are linearly independent (for the case of three distinct eigenvalues).

??? success "Solution"

    *Proof.* Let $A\mathbf{v}_i = \lambda_i\mathbf{v}_i$ for $i = 1, 2, 3$ with $\lambda_1, \lambda_2, \lambda_3$ distinct and $\mathbf{v}_i \neq \mathbf{0}$. Suppose:

    $$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + c_3\mathbf{v}_3 = \mathbf{0}. \quad (*)$$

    Apply $A$ to both sides:

    $$c_1\lambda_1\mathbf{v}_1 + c_2\lambda_2\mathbf{v}_2 + c_3\lambda_3\mathbf{v}_3 = \mathbf{0}. \quad (**)$$

    Multiply $(*)$ by $\lambda_1$ and subtract from $(**)$:

    $$c_2(\lambda_2 - \lambda_1)\mathbf{v}_2 + c_3(\lambda_3 - \lambda_1)\mathbf{v}_3 = \mathbf{0}. \quad (***)$$

    Apply $A$ to $(***)$:

    $$c_2\lambda_2(\lambda_2 - \lambda_1)\mathbf{v}_2 + c_3\lambda_3(\lambda_3 - \lambda_1)\mathbf{v}_3 = \mathbf{0}.$$

    Multiply $(***)$ by $\lambda_2$ and subtract:

    $$c_3(\lambda_3 - \lambda_1)(\lambda_3 - \lambda_2)\mathbf{v}_3 = \mathbf{0}.$$

    Since $\lambda_3 \neq \lambda_1$, $\lambda_3 \neq \lambda_2$, and $\mathbf{v}_3 \neq \mathbf{0}$, $c_3 = 0$.

    Substituting back into $(***)$: $c_2(\lambda_2 - \lambda_1)\mathbf{v}_2 = \mathbf{0}$. Since $\lambda_2 \neq \lambda_1$ and $\mathbf{v}_2 \neq \mathbf{0}$, $c_2 = 0$.

    Substituting into $(*)$: $c_1\mathbf{v}_1 = \mathbf{0}$. Since $\mathbf{v}_1 \neq \mathbf{0}$, $c_1 = 0$.

    All coefficients are zero, so $\{\mathbf{v}_1, \mathbf{v}_2, \mathbf{v}_3\}$ is linearly independent.

    $\square$

---

**Exercise 10.8.** Prove that the trace equals the sum of eigenvalues and the determinant equals the product of eigenvalues for a $2 \times 2$ matrix.

??? success "Solution"

    *Proof.* The characteristic polynomial of $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$ is:

    $$p(\lambda) = \det(A - \lambda I) = (a - \lambda)(d - \lambda) - bc = \lambda^2 - (a+d)\lambda + (ad - bc) = \lambda^2 - \operatorname{tr}(A)\lambda + \det(A).$$

    If $\lambda_1, \lambda_2$ are the roots of $p(\lambda)$, then by factoring:

    $$p(\lambda) = (\lambda - \lambda_1)(\lambda - \lambda_2) = \lambda^2 - (\lambda_1 + \lambda_2)\lambda + \lambda_1\lambda_2.$$

    Comparing coefficients of $\lambda$ and the constant term:

    $$\operatorname{tr}(A) = \lambda_1 + \lambda_2, \quad \det(A) = \lambda_1\lambda_2.$$

    $\square$

    **Generalisation to $n \times n$:** For an $n \times n$ matrix, the characteristic polynomial is $p(\lambda) = \det(A - \lambda I) = (-1)^n[\lambda^n - (\operatorname{tr}A)\lambda^{n-1} + \cdots + (-1)^n\det(A)]$. By Vieta's formulas applied to the $n$ roots $\lambda_1, \ldots, \lambda_n$: the sum of roots equals the coefficient of $\lambda^{n-1}$ (with sign), giving $\operatorname{tr}(A) = \sum \lambda_i$; the product of roots equals the constant term (with sign), giving $\det(A) = \prod \lambda_i$. The same relations hold: the trace is the sum of eigenvalues and the determinant is the product of eigenvalues.

---
