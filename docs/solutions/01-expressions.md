<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 1: Mathematical Expressions & Functions

**Exercise 1.1.** Determine the domain and range of the following functions:

??? success "Solution"

    **(a)** $f(x) = \frac{1}{x^2 - 4}$

    The denominator $x^2 - 4 = (x-2)(x+2)$ is zero when $x = \pm 2$. Therefore the domain is $\mathbb{R} \setminus \{-2, 2\}$.

    For the range: as $x \to \pm 2$, $f(x) \to \pm \infty$. At $x = 0$, $f(0) = -1/4$. As $x \to \pm\infty$, $f(x) \to 0^+$. The maximum value on $(-2, 2)$ occurs at $x = 0$ where $f(0) = -1/4$; as $x \to 2^-$ or $x \to -2^+$, $f(x) \to -\infty$. On $(2,\infty)$ and $(-\infty,-2)$, $f(x) > 0$ and approaches $0^+$ and $+\infty$. Thus the range is $(-\infty, -1/4] \cup (0, \infty)$.

    **(b)** $g(x) = \sqrt{9 - x^2}$

    We need $9 - x^2 \geq 0$, i.e., $x^2 \leq 9$, so the domain is $[-3, 3]$.

    At $x = 0$, $g(0) = 3$ (the maximum). At $x = \pm 3$, $g(\pm 3) = 0$. Since $g$ is continuous and takes all intermediate values, the range is $[0, 3]$.

    **(c)** $h(x) = \ln(x - 3)$

    We need $x - 3 > 0$, so the domain is $(3, \infty)$.

    As $x \to 3^+$, $h(x) \to -\infty$. As $x \to \infty$, $h(x) \to \infty$. The range is $(-\infty, \infty)$.

---

**Exercise 1.2.** Let $f(x) = 2x + 1$ and $g(x) = x^2$. Compute $(f \circ g)(x)$ and $(g \circ f)(x)$.

??? success "Solution"

    $(f \circ g)(x) = f(g(x)) = f(x^2) = 2x^2 + 1$.

    $(g \circ f)(x) = g(f(x)) = g(2x+1) = (2x+1)^2 = 4x^2 + 4x + 1$.

    Since $2x^2 + 1 \neq 4x^2 + 4x + 1$ in general (e.g., at $x = 1$: $f \circ g(1) = 3$ but $g \circ f(1) = 9$), this confirms $f \circ g \neq g \circ f$. Function composition is not commutative.

---

**Exercise 1.3.** Write the expression tree (as nested constructor calls) for each expression.

??? success "Solution"

    **(a)** $3x^2 - 7x + 2$

    ```
    add(
      sub(
        mul(constant(3), pow(variable('x'), constant(2))),
        mul(constant(7), variable('x'))
      ),
      constant(2)
    )
    ```

    **(b)** $\frac{\sin(x)}{x}$

    ```
    div(
      sin(variable('x')),
      variable('x')
    )
    ```

    **(c)** $e^{-x^2/2}$

    ```
    exp(
      neg(
        div(
          pow(variable('x'), constant(2)),
          constant(2)
        )
      )
    )
    ```

    (Equivalently, `exp(mul(constant(-1/2), pow(variable('x'), constant(2))))` if one prefers multiplication by $-1/2$ over negation and division.)

---

**Exercise 1.4.** Prove that the composition of two injective functions is injective.

??? success "Solution"

    *Proof.* Let $f: B \to C$ and $g: A \to B$ be injective. We must show $f \circ g: A \to C$ is injective.

    Suppose $(f \circ g)(a_1) = (f \circ g)(a_2)$ for some $a_1, a_2 \in A$. Then $f(g(a_1)) = f(g(a_2))$. Since $f$ is injective, this implies $g(a_1) = g(a_2)$. Since $g$ is injective, this implies $a_1 = a_2$. Therefore $f \circ g$ is injective.

    $\square$

---

**Exercise 1.5.** Prove that the composition of two surjective functions is surjective.

??? success "Solution"

    *Proof.* Let $f: B \to C$ and $g: A \to B$ be surjective. We must show $f \circ g: A \to C$ is surjective.

    Let $c \in C$ be arbitrary. Since $f$ is surjective, there exists $b \in B$ such that $f(b) = c$. Since $g$ is surjective, there exists $a \in A$ such that $g(a) = b$. Then $(f \circ g)(a) = f(g(a)) = f(b) = c$. Since $c$ was arbitrary, $f \circ g$ is surjective.

    $\square$

---

**Exercise 1.6.** Consider $E = (x + 1) \cdot (x - 1)$.

??? success "Solution"

    The expression tree is:

    ```
            mul
           /   \
         add   sub
        / \    / \
       x   1  x   1
    ```

    **Node count**: 7 nodes total (1 `mul`, 1 `add`, 1 `sub`, 2 `variable('x')`, 2 `constant(1)`).

    **Depth**: 2 (two edges from root to the deepest leaf, matching the definition in Remark 1.19 where depth is the number of edges on the longest root-to-leaf path).

    **Evaluation at $x = 5$**, tracing bottom-up:

    - Left-`x` leaf: $5$
    - Left-`1` leaf: $1$
    - `add` node: $5 + 1 = 6$
    - Right-`x` leaf: $5$
    - Right-`1` leaf: $1$
    - `sub` node: $5 - 1 = 4$
    - `mul` node (root): $6 \times 4 = 24$

    Result: $E(5) = 24$. (Verification: $(5+1)(5-1) = 6 \cdot 4 = 24$.)

---

**Exercise 1.7.** Prove that the set of expressions is the smallest set closed under the formation rules.

??? success "Solution"

    *Proof.* Let $\mathcal{E}$ be the set of expressions defined by Definition 1.18 (constants, variables, binary operations and unary operations). Let $S$ be any set satisfying all four closure rules. We prove $\mathcal{E} \subseteq S$ by structural induction.

    **Base cases:** Every constant $c$ belongs to $S$ by closure rule 1. Every variable $x$ belongs to $S$ by closure rule 2. These are the atomic expressions in $\mathcal{E}$.

    **Inductive step (binary):** If $e_1, e_2 \in \mathcal{E}$ and $e_1, e_2 \in S$ (by the inductive hypothesis), then $\text{op}(e_1, e_2) \in \mathcal{E}$ by formation rule 3, and $\text{op}(e_1, e_2) \in S$ by closure rule 3 applied to $S$.

    **Inductive step (unary):** If $e \in \mathcal{E}$ and $e \in S$ (by the inductive hypothesis), then for any unary operator $\text{op}$, the expression $\text{op}(e)$ belongs to $\mathcal{E}$ by formation rule 4, and $\text{op}(e) \in S$ by closure rule 4.

    By structural induction, every expression in $\mathcal{E}$ belongs to $S$. Since $S$ was an arbitrary set closed under the formation rules, $\mathcal{E}$ is contained in every such set, making it the smallest.

    $\square$

---

**Exercise 1.8.** Tree vs. DAG representations for expressions.

??? success "Solution"

    Consider $(x+1)^2 + (x+1)^3$. In the tree representation, the subexpression $x+1$ appears as two distinct subtrees. In a DAG representation, a single node for $x+1$ is shared, with two parent edges leading to the `pow` nodes.

    **Operations easier with DAG (sharing):**
    - *Evaluation*: the shared subexpression $x+1$ is computed once rather than twice. For deeply nested shared subexpressions, this can reduce evaluation from exponential to polynomial time.
    - *Common subexpression elimination*: already done by construction.
    - *Memory*: the DAG uses fewer nodes, reducing memory consumption when subexpressions repeat heavily.

    **Operations harder with DAG:**
    - *Differentiation*: in a tree, each node has exactly one parent, so the derivative at each node depends only on the path from root to that node. In a DAG, a shared node has multiple parents, so the chain rule must sum contributions from all paths. This requires either a topological sort with accumulation (reverse-mode AD) or careful bookkeeping to avoid double-counting.
    - *Mutation/simplification*: modifying a shared node affects all expressions that reference it. In a tree, one can freely transform a subtree without side effects.
    - *Structural equality*: in a tree, structural equality is a simple recursive check. In a DAG, one must distinguish structural equality from pointer equality.

    DAGs trade simpler local reasoning (which trees provide) for globally efficient computation and memory. This is exactly the trade-off exploited by automatic differentiation: forward-mode AD works naturally on trees, while reverse-mode AD (backpropagation) is the algorithm designed to handle the DAG structure efficiently.

---
