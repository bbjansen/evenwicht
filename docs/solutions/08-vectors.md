<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 8: Vectors & Vector Spaces

**Exercise 8.1.** Let $\mathbf{u} = (2, -1, 3)^T$ and $\mathbf{v} = (-1, 4, 2)^T$.

??? success "Solution"

    $\mathbf{u} + \mathbf{v} = (2 + (-1),\; -1 + 4,\; 3 + 2)^T = (1, 3, 5)^T$.

    $\mathbf{u} - \mathbf{v} = (2 - (-1),\; -1 - 4,\; 3 - 2)^T = (3, -5, 1)^T$.

    $3\mathbf{u} + 2\mathbf{v} = (6, -3, 9)^T + (-2, 8, 4)^T = (4, 5, 13)^T$.

    $\lVert\mathbf{u}\rVert = \sqrt{2^2 + (-1)^2 + 3^2} = \sqrt{4 + 1 + 9} = \sqrt{14}$.

---

**Exercise 8.2.** Dot product and angle between $\mathbf{u} = (1,1,1,1)^T$ and $\mathbf{v} = (1,-1,1,-1)^T$.

??? success "Solution"

    $\mathbf{u} \cdot \mathbf{v} = 1(1) + 1(-1) + 1(1) + 1(-1) = 1 - 1 + 1 - 1 = 0$.

    Since $\mathbf{u} \cdot \mathbf{v} = 0$, the vectors are **orthogonal**. The angle between them is $\theta = \arccos(0) = \pi/2$ (90 degrees).

---

**Exercise 8.3.** Projection of $\mathbf{u} = (2,3,1)^T$ onto $\mathbf{v} = (1,1,1)^T$.

??? success "Solution"

    $\operatorname{proj}_{\mathbf{v}}(\mathbf{u}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\mathbf{v} \cdot \mathbf{v}}\,\mathbf{v} = \frac{2 + 3 + 1}{1 + 1 + 1}(1,1,1)^T = \frac{6}{3}(1,1,1)^T = 2(1,1,1)^T = (2,2,2)^T$.

    **Residual:** $\mathbf{u} - \operatorname{proj}_{\mathbf{v}}(\mathbf{u}) = (2,3,1)^T - (2,2,2)^T = (0, 1, -1)^T$.

    **Verification:** $(0, 1, -1)^T \cdot (1, 1, 1)^T = 0 + 1 - 1 = 0$. $\checkmark$ The residual is orthogonal to $\mathbf{v}$.

---

**Exercise 8.4.** Verify the parallelogram law for $\mathbf{u} = (1,2,-1)^T$, $\mathbf{v} = (3,0,1)^T$.

??? success "Solution"

    $\mathbf{u} + \mathbf{v} = (4, 2, 0)^T$, so $\lVert\mathbf{u} + \mathbf{v}\rVert^2 = 16 + 4 + 0 = 20$.

    $\mathbf{u} - \mathbf{v} = (-2, 2, -2)^T$, so $\lVert\mathbf{u} - \mathbf{v}\rVert^2 = 4 + 4 + 4 = 12$.

    $\lVert\mathbf{u}\rVert^2 = 1 + 4 + 1 = 6$, $\lVert\mathbf{v}\rVert^2 = 9 + 0 + 1 = 10$.

    LHS: $\lVert\mathbf{u}+\mathbf{v}\rVert^2 + \lVert\mathbf{u}-\mathbf{v}\rVert^2 = 20 + 12 = 32$.

    RHS: $2\lVert\mathbf{u}\rVert^2 + 2\lVert\mathbf{v}\rVert^2 = 12 + 20 = 32$.

    $32 = 32$. $\checkmark$

---

**Exercise 8.5.** Linear independence of $\{(1,0,1)^T, (0,1,1)^T, (1,1,0)^T\}$.

??? success "Solution"

    Form the matrix with these vectors as columns and compute its determinant:

    $$A = \begin{pmatrix} 1 & 0 & 1 \\ 0 & 1 & 1 \\ 1 & 1 & 0 \end{pmatrix}.$$

    $\det(A) = 1(0 - 1) - 0(0 - 1) + 1(0 - 1) = -1 + 0 - 1 = -2 \neq 0$.

    Since the determinant is nonzero, the vectors are **linearly independent**. As there are 3 linearly independent vectors in $\mathbb{R}^3$, they form a **basis** for $\mathbb{R}^3$.

---

**Exercise 8.6.** Gram–Schmidt on $\mathbf{v}_1 = (1,1,0)^T$ and $\mathbf{v}_2 = (1,0,1)^T$.

??? success "Solution"

    **Step 1:** $\mathbf{q}_1 = \frac{\mathbf{v}_1}{\lVert\mathbf{v}_1\rVert} = \frac{1}{\sqrt{2}}(1, 1, 0)^T$.

    **Step 2:** $\mathbf{w}_2 = \mathbf{v}_2 - (\mathbf{v}_2 \cdot \mathbf{q}_1)\mathbf{q}_1$.

    $\mathbf{v}_2 \cdot \mathbf{q}_1 = \frac{1}{\sqrt{2}}(1 \cdot 1 + 0 \cdot 1 + 1 \cdot 0) = \frac{1}{\sqrt{2}}$.

    $\mathbf{w}_2 = (1, 0, 1)^T - \frac{1}{\sqrt{2}} \cdot \frac{1}{\sqrt{2}}(1, 1, 0)^T = (1, 0, 1)^T - \frac{1}{2}(1, 1, 0)^T = (1/2, -1/2, 1)^T$.

    $\lVert\mathbf{w}_2\rVert = \sqrt{1/4 + 1/4 + 1} = \sqrt{3/2} = \frac{\sqrt{6}}{2}$.

    $\mathbf{q}_2 = \frac{\mathbf{w}_2}{\lVert\mathbf{w}_2\rVert} = \frac{2}{\sqrt{6}}(1/2, -1/2, 1)^T = \frac{1}{\sqrt{6}}(1, -1, 2)^T$.

    **Verification:**

    $\mathbf{q}_1 \cdot \mathbf{q}_2 = \frac{1}{\sqrt{2}} \cdot \frac{1}{\sqrt{6}}(1 \cdot 1 + 1 \cdot (-1) + 0 \cdot 2) = \frac{1}{\sqrt{12}}(1 - 1 + 0) = 0$. $\checkmark$

    $\lVert\mathbf{q}_1\rVert = \sqrt{1/2 + 1/2} = 1$. $\checkmark$

    $\lVert\mathbf{q}_2\rVert = \frac{1}{\sqrt{6}}\sqrt{1 + 1 + 4} = \frac{\sqrt{6}}{\sqrt{6}} = 1$. $\checkmark$

---

**Exercise 8.7.** Prove the Cauchy–Schwarz inequality.

??? success "Solution"

    *Proof.* If $\mathbf{v} = \mathbf{0}$, both sides are zero and the inequality holds trivially. Assume $\mathbf{u}, \mathbf{v} \neq \mathbf{0}$.

    Let $\hat{\mathbf{u}} = \mathbf{u}/\lVert\mathbf{u}\rVert$ and $\hat{\mathbf{v}} = \mathbf{v}/\lVert\mathbf{v}\rVert$ be unit vectors. Consider:

    $$\lVert\hat{\mathbf{u}} - (\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})\hat{\mathbf{v}}\rVert^2 \geq 0.$$

    Expanding the left side:

    $$\lVert\hat{\mathbf{u}}\rVert^2 - 2(\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})(\hat{\mathbf{u}} \cdot \hat{\mathbf{v}}) + (\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})^2\lVert\hat{\mathbf{v}}\rVert^2 \geq 0.$$

    Since $\lVert\hat{\mathbf{u}}\rVert = \lVert\hat{\mathbf{v}}\rVert = 1$:

    $$1 - 2(\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})^2 + (\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})^2 \geq 0 \implies 1 - (\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})^2 \geq 0.$$

    Therefore $(\hat{\mathbf{u}} \cdot \hat{\mathbf{v}})^2 \leq 1$, which means $|\hat{\mathbf{u}} \cdot \hat{\mathbf{v}}| \leq 1$.

    Substituting back:

    $$\left|\frac{\mathbf{u}}{\lVert\mathbf{u}\rVert} \cdot \frac{\mathbf{v}}{\lVert\mathbf{v}\rVert}\right| \leq 1 \implies |\mathbf{u} \cdot \mathbf{v}| \leq \lVert\mathbf{u}\rVert\,\lVert\mathbf{v}\rVert.$$

    $\square$

---

**Exercise 8.8.** Prove an orthogonal set of nonzero vectors is linearly independent.

??? success "Solution"

    *Proof.* Let $\{\mathbf{v}_1, \mathbf{v}_2, \ldots, \mathbf{v}_k\}$ be a set of mutually orthogonal nonzero vectors. Suppose:

    $$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + \cdots + c_k\mathbf{v}_k = \mathbf{0}.$$

    Take the dot product of both sides with $\mathbf{v}_j$ for an arbitrary $j \in \{1, \ldots, k\}$:

    $$c_1(\mathbf{v}_1 \cdot \mathbf{v}_j) + c_2(\mathbf{v}_2 \cdot \mathbf{v}_j) + \cdots + c_k(\mathbf{v}_k \cdot \mathbf{v}_j) = \mathbf{0} \cdot \mathbf{v}_j = 0.$$

    By orthogonality, $\mathbf{v}_i \cdot \mathbf{v}_j = 0$ for all $i \neq j$. So all terms vanish except the $j$-th:

    $$c_j(\mathbf{v}_j \cdot \mathbf{v}_j) = c_j\lVert\mathbf{v}_j\rVert^2 = 0.$$

    Since $\mathbf{v}_j \neq \mathbf{0}$, $\lVert\mathbf{v}_j\rVert^2 > 0$, so $c_j = 0$.

    Since $j$ was arbitrary, all coefficients $c_1 = c_2 = \cdots = c_k = 0$. Therefore the vectors are linearly independent.

    $\square$

---
