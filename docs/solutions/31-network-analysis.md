<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 31: Network Analysis & Graph Theory

**Exercise 31.1.** Laplacian computation.

??? success "Solution"

    $$A = \begin{bmatrix} 0 & 1 & 0 & 1 \\ 1 & 0 & 1 & 1 \\ 0 & 1 & 0 & 1 \\ 1 & 1 & 1 & 0 \end{bmatrix}.$$

    Degrees: $d_1 = 2$, $d_2 = 3$, $d_3 = 2$, $d_4 = 3$.

    $D = \operatorname{diag}(2, 3, 2, 3)$.

    $$L = D - A = \begin{bmatrix} 2 & -1 & 0 & -1 \\ -1 & 3 & -1 & -1 \\ 0 & -1 & 2 & -1 \\ -1 & -1 & -1 & 3 \end{bmatrix}.$$

    $$L\mathbf{1} = \begin{bmatrix} 2-1+0-1 \\ -1+3-1-1 \\ 0-1+2-1 \\ -1-1-1+3 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ 0 \\ 0 \end{bmatrix} = \mathbf{0}. \quad \checkmark$$

    $\square$

---

**Exercise 31.2.** $A^2$ and length-2 walks.

??? success "Solution"

    $$A^2 = \begin{bmatrix} 0&1&0&1\\1&0&1&1\\0&1&0&1\\1&1&1&0\end{bmatrix}\begin{bmatrix}0&1&0&1\\1&0&1&1\\0&1&0&1\\1&1&1&0\end{bmatrix} = \begin{bmatrix}2&1&2&1\\1&3&1&2\\2&1&2&1\\1&2&1&3\end{bmatrix}.$$

    Diagonal: $(A^2)_{11} = 2 = d_1$, $(A^2)_{22} = 3 = d_2$, $(A^2)_{33} = 2 = d_3$, $(A^2)_{44} = 3 = d_4$. $\checkmark$

    $(A^2)_{ij}$ counts the number of length-2 walks from $i$ to $j$. A walk of length 2 from $i$ back to $i$ must go $i \to k \to i$ for some neighbour $k$ of $i$; the number of such walks equals the number of neighbours $d_i$. $\square$

---

**Exercise 31.3.** Stationary distribution.

??? success "Solution"

    Total edges: $m = (2+3+2+3)/2 = 5$ (sum of degrees divided by 2).

    $\pi_i = d_i/(2m)$: $\pi_1 = 2/10 = 0.2$, $\pi_2 = 3/10 = 0.3$, $\pi_3 = 2/10 = 0.2$, $\pi_4 = 3/10 = 0.3$.

    $$P = D^{-1}A = \begin{bmatrix} 0 & 1/2 & 0 & 1/2 \\ 1/3 & 0 & 1/3 & 1/3 \\ 0 & 1/2 & 0 & 1/2 \\ 1/3 & 1/3 & 1/3 & 0 \end{bmatrix}.$$

    $\boldsymbol{\pi}'P$: Row 1: $0.2(0)+0.3(1/3)+0.2(0)+0.3(1/3) = 0.1+0.1 = 0.2 = \pi_1$. $\checkmark$

    Row 2: $0.2(1/2)+0.3(0)+0.2(1/2)+0.3(1/3) = 0.1+0.1+0.1 = 0.3 = \pi_2$. $\checkmark$

    Similarly for rows 3 and 4. Thus $\boldsymbol{\pi}'P = \boldsymbol{\pi}'$. $\square$

---

**Exercise 31.4.** Erdos–Renyi $G(10, 0.3)$.

??? success "Solution"

    Expected edges: $\binom{10}{2} \times 0.3 = 45 \times 0.3 = 13.5$.

    Expected degree: $(n-1)p = 9 \times 0.3 = 2.7$.

    A specific realization (one possible outcome) might produce 12 edges with degree sequence $[3, 2, 3, 4, 1, 3, 2, 3, 3, 2]$, which has mean degree $2.6$ (close to the expected $2.7$). Each realization differs; the degree distribution is approximately binomial $\text{Bin}(9, 0.3)$ for each vertex.

    $\square$

---

**Exercise 31.5.** Eigenvalues of $P = D^{-1}A$ lie in $[-1,1]$.

??? success "Solution"

    Define the symmetric matrix $\tilde{P} = D^{-1/2}AD^{-1/2}$. Then $P = D^{-1}A = D^{-1/2}\tilde{P}D^{1/2}$, so $P$ and $\tilde{P}$ are similar. Similar matrices share eigenvalues.

    Since $\tilde{P}$ is real symmetric, its eigenvalues are real. By the Rayleigh quotient:

    $$\lambda = \frac{\mathbf{x}'\tilde{P}\mathbf{x}}{\mathbf{x}'\mathbf{x}} = \frac{\mathbf{x}'D^{-1/2}AD^{-1/2}\mathbf{x}}{\mathbf{x}'\mathbf{x}}.$$

    Let $\mathbf{y} = D^{-1/2}\mathbf{x}$. Then $\lambda = \frac{\mathbf{y}'A\mathbf{y}}{\mathbf{y}'D\mathbf{y}}$. Since $\lvert A_{ij}\rvert \leq 1$ and using the Cauchy–Schwarz inequality, $\lvert\mathbf{y}'A\mathbf{y}\rvert = \lvert\sum_{i \sim j} y_i y_j\rvert \leq \sum_{i \sim j} \lvert y_i\rvert\lvert y_j\rvert \leq \frac{1}{2}\sum_{i\sim j}(y_i^2 + y_j^2) = \sum_i d_i y_i^2 = \mathbf{y}'D\mathbf{y}$.

    Therefore $\lvert\lambda\rvert \leq 1$. If the graph is connected, the eigenvalue $+1$ is achieved with eigenvector $D^{1/2}\mathbf{1}$. $\square$

---

**Exercise 31.6.** PageRank computation.

??? success "Solution"

    Edges: $1 \to 2$, $2 \to 3$, $3 \to 1$, $3 \to 2$. Hyperlink matrix (column-stochastic):

    $$H = \begin{bmatrix} 0 & 0 & 1/2 \\ 1 & 0 & 1/2 \\ 0 & 1 & 0 \end{bmatrix}.$$

    Google matrix: $M = dH + \frac{1-d}{3}\mathbf{1}\mathbf{1}' = 0.85H + 0.05\mathbf{1}\mathbf{1}'$.

    $$M = \begin{bmatrix} 0.05 & 0.05 & 0.475 \\ 0.9 & 0.05 & 0.475 \\ 0.05 & 0.9 & 0.05 \end{bmatrix}.$$

    Power iteration from $\boldsymbol{\pi}^{(0)} = [1/3, 1/3, 1/3]'$:

    $\boldsymbol{\pi}^{(1)} = M\boldsymbol{\pi}^{(0)} = [(0.05+0.05+0.475)/3, (0.9+0.05+0.475)/3, (0.05+0.9+0.05)/3] = [0.1917, 0.4750, 0.3333]$ (components sum to 1 up to rounding).

    Continuing iterations converges to approximately $\boldsymbol{\pi} \approx [0.244, 0.411, 0.345]$. Vertex 2 has the highest PageRank (it receives links from both 1 and 3), followed by vertex 3, then vertex 1.

    Convergence to $L_1$ error below $10^{-3}$ typically requires approximately 15–20 iterations for this small graph.

    $\square$

---

**Exercise 31.7.** Max-flow problem.

??? success "Solution"

    Network: $s \to a$ (cap 4), $s \to b$ (cap 3), $a \to b$ (cap 2), $a \to t$ (cap 3), $b \to t$ (cap 5).

    **LP formulation:** Variables: $f_{sa}, f_{sb}, f_{ab}, f_{at}, f_{bt} \geq 0$. Maximise $f_{sa} + f_{sb}$ (total flow from source). Subject to: capacity constraints ($f_{sa} \leq 4$, etc.), flow conservation at $a$ ($f_{sa} = f_{ab} + f_{at}$) and $b$ ($f_{sb} + f_{ab} = f_{bt}$).

    **Augmenting path method:**

    1. Path $s \to a \to t$: bottleneck = min(4, 3) = 3. Send 3 units. Remaining: $s\to a$: 1, $a\to t$: 0.
    2. Path $s \to b \to t$: bottleneck = min(3, 5) = 3. Send 3 units. Remaining: $s\to b$: 0, $b\to t$: 2.
    3. Path $s \to a \to b \to t$: bottleneck = min(1, 2, 2) = 1. Send 1 unit.

    Total flow: $3 + 3 + 1 = 7$.

    **Min-cut verification:** Cut $\{s\}$ vs $\{a,b,t\}$: capacity = $4 + 3 = 7$. This equals the max flow, confirming the max-flow min-cut theorem. $\square$

---

**Exercise 31.8.** Mixing time of cycle vs. complete graph.

??? success "Solution"

    For the cycle $C_n$ with transition matrix $P_{ij} = 1/2$ if $\lvert i-j\rvert = 1 \pmod{n}$: the eigenvalues of $P$ are $\lambda_k = \cos(2\pi k/n)$ for $k = 0, 1, \ldots, n-1$. The second largest is $\lambda_1 = \cos(2\pi/n)$.

    For large $n$: $\lambda_1 \approx 1 - 2\pi^2/n^2$, so $1 - \lambda_1 \approx 2\pi^2/n^2$. The mixing time scales as $t_{\text{mix}} \sim 1/(1-\lambda_1) \sim n^2/(2\pi^2) = \Theta(n^2)$.

    For the complete graph $K_n$: the lazy random walk has transition matrix $P = \frac{1}{2}I + \frac{1}{2}\frac{1}{n-1}(J - I) = \frac{n-3}{2(n-1)}I + \frac{1}{2(n-1)}J$. The eigenvalues are $1$ (for the uniform vector) and $\lambda_2 = \frac{n-3}{2(n-1)} + \frac{1}{2(n-1)} \cdot 0 = 1 - \frac{n}{2(n-1)}$ with multiplicity $n-1$. For large $n$, $\lambda_2 \approx 1/2$.

    The spectral gap is $\gamma = 1 - \lambda_2 = \frac{n}{2(n-1)} \to 1/2$ as $n \to \infty$. By the standard mixing time bound $t_{\text{mix}} = \Theta\!\left(\frac{1}{\gamma}\log n\right)$, we have $t_{\text{mix}} = \Theta(\log n)$. To see the lower bound, note that after one step from a deterministic start the distribution places weight $1/2$ on the starting vertex and $1/(2(n-1))$ on each other vertex; the total variation distance from stationary is approximately $1/2 - 1/n$. Reducing this to $\varepsilon$ requires $\Omega(\log n)$ steps because each step contracts total variation by at most $1 - \gamma \approx 1/2$.

    The qualitative difference is connectivity: in $C_n$, information diffuses like a random walk on a line (each step moves $\pm 1$ position), requiring $\Theta(n^2)$ steps to traverse the entire circle. In $K_n$, each step can reach any vertex with nearly equal probability, so the walk mixes in $\Theta(\log n)$ steps. The spectral gap $\gamma$ quantifies this: it is $\Theta(1/n^2)$ for the cycle (bottleneck: narrow connectivity) and $\Theta(1)$ for the complete graph (no bottleneck), but even with a constant spectral gap the $\log n$ factor is needed to eliminate the initial concentration at the starting vertex. $\square$

---
