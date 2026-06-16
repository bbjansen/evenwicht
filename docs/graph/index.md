<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Knowledge Graph

The 48 chapters form a directed dependency graph with **234 edges**.
Each arrow means one chapter builds on another; either as a direct
prerequisite or through shared concepts.

Hover a node for details. Click to highlight its connections. Drag to
rearrange. Scroll to zoom.

<div id="knowledge-graph-container" style="width: 100%; height: 700px; position: relative;"></div>

---

## Reading the Graph

Nodes are coloured by part. An arrow from A to B means B depends on A.
Tightly connected clusters share a mathematical foundation. The most
connected chapters unlock the widest range of downstream material.

## Hub Chapters

Nine chapters serve as major junctions in the dependency graph.

| Chapter | Connections | Why it matters |
|---------|-------------|----------------|
| 10. Eigenvalues | 23 | Stability, PCA, spectral methods, Markov chains |
| 19. ODEs | 21 | Every dynamical model in the application chapters |
| 17. Regression | 21 | Statistical modelling across all applied fields |
| 9. Matrices | 17 | Linear systems, transformations, graph adjacency |
| 11. Optimisation | 16 | Gradient descent, MLE, Lagrangians, portfolio theory |
| 4. Differential Calculus | 15 | Rates of change, chain rule, optimisation |
| 23. Operator Algebra | 15 | Unifying calculus and discrete analysis |
| 5. Integral Calculus | 14 | Accumulation, area, probability, special functions |
| 13. Probability | 14 | Distributions, inference, stochastic models |
| 22. Transforms | 14 | Frequency domain, spectral analysis, filtering |

## Edge Types

The graph contains two kinds of edge:

- **Reference** (229): chapter A is a prerequisite or is cited by chapter B.
- **Shared API** (5): chapters share functions or data structures in the
  TypeScript library.
