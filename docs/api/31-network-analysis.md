<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Network Analysis & Graph Theory — API Reference

This is the API reference for the TypeScript implementation of Network Analysis & Graph Theory. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/graph/adjacency.ts` — adjacency matrix construction, degree vector, Laplacian
- `src/graph/centrality.ts` — degree centrality, eigenvector centrality, PageRank
- `src/graph/spectral.ts` — spectral bisection, spectral clustering
- `src/graph/randomwalk.ts` — transition matrix, stationary distribution, random walk simulation
- `src/graph/flow.ts` — maximum flow (Edmonds-Karp), minimum cut
- `src/graph/generators.ts` — random graph generators (Erdos-Renyi, Barabasi-Albert)

### Data Representation

Graphs are represented as adjacency matrices stored in flat row-major `Float64Array` of size $n \times n$. Sparse graphs still use dense matrices (no sparse representation). Centrality vectors and degree vectors are `Float64Array` of length $n$. Partitions and clusters are returned as arrays of vertex index arrays.

### API Preview

```typescript
// src/graph/adjacency.ts

/**
 * Construct adjacency matrix from an edge list.
 *
 * @param n - Number of vertices.
 * @param edges - Array of [source, target, weight?] tuples.
 * @param directed - If true, create directed adjacency matrix (default: false).
 * @returns Adjacency matrix as flat row-major Float64Array (n x n).
 */
function adjacencyMatrix(
  n: number,
  edges: Array<[number, number, number?]>,
  directed?: boolean,
): Float64Array;

/**
 * Compute degree vector of a graph.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Degree vector as Float64Array of length n.
 */
function degreeVector(A: Float64Array, n: number): Float64Array;

/**
 * Construct the graph Laplacian L = D - A.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Laplacian matrix as flat row-major Float64Array (n x n).
 */
function laplacian(A: Float64Array, n: number): Float64Array;

/**
 * Construct the normalized Laplacian D^{-1/2} L D^{-1/2}.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Normalized Laplacian as flat row-major Float64Array (n x n).
 * @throws Error if any vertex has degree 0 (isolated vertex).
 */
function normalizedLaplacian(A: Float64Array, n: number): Float64Array;
```

```typescript
// src/graph/centrality.ts

/**
 * Compute degree centrality for all vertices.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Centrality vector as Float64Array of length n, values in [0, 1].
 */
function degreeCentrality(A: Float64Array, n: number): Float64Array;

/**
 * Compute eigenvector centrality via power iteration.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @param opts - Options: tolerance (default 1e-10), maxIterations (default 1000).
 * @returns Centrality vector (L1-normalized) as Float64Array of length n.
 * @throws Error if graph is disconnected or iteration does not converge.
 */
function eigenvectorCentrality(
  A: Float64Array,
  n: number,
  opts?: { tolerance?: number; maxIterations?: number },
): Float64Array;

/**
 * Compute PageRank for a directed graph.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 *            A[i*n + j] = 1 indicates edge from j to i (column = source).
 * @param n - Number of vertices.
 * @param opts - Options: damping (default 0.85), tolerance (default 1e-10),
 *              maxIterations (default 200).
 * @returns PageRank vector (L1-normalized) as Float64Array of length n.
 */
function pageRank(
  A: Float64Array,
  n: number,
  opts?: { damping?: number; tolerance?: number; maxIterations?: number },
): Float64Array;
```

```typescript
// src/graph/spectral.ts

/**
 * Compute spectral bisection of a graph using the Fiedler vector.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Object { partition: [number[], number[]], fiedlerVector: Float64Array,
 *          algebraicConnectivity: number }.
 */
function spectralBisection(
  A: Float64Array,
  n: number,
): {
  partition: [number[], number[]];
  fiedlerVector: Float64Array;
  algebraicConnectivity: number;
};

/**
 * Spectral clustering into k groups using bottom-k eigenvectors of the Laplacian.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @param k - Number of clusters.
 * @param opts - Options: normalized (default true, use normalized Laplacian),
 *              maxKmeansIterations (default 100).
 * @returns Array of k arrays, each containing vertex indices in that cluster.
 */
function spectralClustering(
  A: Float64Array,
  n: number,
  k: number,
  opts?: { normalized?: boolean; maxKmeansIterations?: number },
): number[][];
```

```typescript
// src/graph/randomwalk.ts

/**
 * Compute the transition matrix P = D^{-1}A for a random walk.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Transition matrix as flat row-major Float64Array (n x n).
 * @throws Error if any vertex has degree 0.
 */
function transitionMatrix(A: Float64Array, n: number): Float64Array;

/**
 * Compute the stationary distribution of a random walk.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @returns Stationary distribution as Float64Array of length n (sums to 1).
 * @throws Error if graph is disconnected.
 */
function stationaryDistribution(A: Float64Array, n: number): Float64Array;

/**
 * Simulate a random walk on a graph.
 *
 * @param A - Adjacency matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @param start - Starting vertex index (0-based).
 * @param steps - Number of steps to simulate.
 * @param rng - Random number generator function returning values in [0, 1).
 * @returns Array of visited vertex indices (length = steps + 1).
 */
function simulateRandomWalk(
  A: Float64Array,
  n: number,
  start: number,
  steps: number,
  rng: () => number,
): number[];
```

```typescript
// src/graph/flow.ts

/**
 * Solve the maximum flow problem using the Ford-Fulkerson method
 * with BFS (Edmonds-Karp algorithm).
 *
 * @param capacity - Capacity matrix (n x n), flat row-major Float64Array.
 *                   capacity[i*n + j] = capacity of edge (i, j).
 * @param n - Number of vertices.
 * @param source - Source vertex index.
 * @param sink - Sink vertex index.
 * @returns Object { maxFlow: number, flow: Float64Array } where flow is the
 *          n x n flow matrix.
 */
function maxFlow(
  capacity: Float64Array,
  n: number,
  source: number,
  sink: number,
): { maxFlow: number; flow: Float64Array };

/**
 * Compute the minimum cut corresponding to the maximum flow.
 *
 * @param capacity - Capacity matrix (n x n), flat row-major Float64Array.
 * @param n - Number of vertices.
 * @param source - Source vertex index.
 * @param sink - Sink vertex index.
 * @returns Object { cutValue: number, sourceSet: number[], sinkSet: number[] }.
 */
function minCut(
  capacity: Float64Array,
  n: number,
  source: number,
  sink: number,
): { cutValue: number; sourceSet: number[]; sinkSet: number[] };
```

```typescript
// src/graph/generators.ts

/**
 * Generate an Erdős–Rényi random graph G(n, p).
 *
 * @param n - Number of vertices.
 * @param p - Edge probability.
 * @param rng - Random number generator function returning values in [0, 1).
 * @returns Adjacency matrix as flat row-major Float64Array (n x n), symmetric.
 */
function erdosRényi(
  n: number,
  p: number,
  rng: () => number,
): Float64Array;

/**
 * Generate a Barabási–Albert preferential attachment graph.
 *
 * @param n - Final number of vertices.
 * @param m - Number of edges each new vertex adds.
 * @param rng - Random number generator function returning values in [0, 1).
 * @returns Adjacency matrix as flat row-major Float64Array (n x n), symmetric.
 * @throws Error if m < 1 or n <= m.
 */
function barabasiAlbert(
  n: number,
  m: number,
  rng: () => number,
): Float64Array;
```

### Error Handling

- `adjacencyMatrix` throws if any vertex index is out of range $[0, n)$.
- `eigenvectorCentrality` throws if the graph is disconnected (Perron–Frobenius requires irreducibility) or if the power iteration fails to converge within `maxIterations`.
- `pageRank` handles dangling nodes (vertices with out-degree 0) by distributing their rank equally to all vertices; it always converges due to the teleportation term.
- `normalizedLaplacian` and `transitionMatrix` throw if any vertex has degree 0 (isolated vertices make $D^{-1}$ undefined).
- `maxFlow` throws if `source === sink` or if vertex indices are out of range.
- `spectralClustering` throws if $k > n$ or $k < 1$.

### Dependencies

- `src/linear/eigen.ts` — eigenvalue/eigenvector computation for spectral methods, PageRank, centrality
- `src/linear/solve.ts` — linear system solve for Laplacian-based computations
- `src/optimization/linprog.ts` — LP solver for max-flow formulation (alternative)

### Usage Examples

```typescript
import { adjacencyMatrix, pageRank, spectralBisection, maxFlow } from 'evenwicht/graph';

// Build a small graph: triangle with 3 vertices
const A = adjacencyMatrix(3, [[0, 1], [1, 2], [0, 2]]);

// PageRank of a directed web graph
const directed = adjacencyMatrix(4, [[0, 1], [1, 2], [2, 0], [2, 3]], true);
const pr = pageRank(directed, 4, { damping: 0.85 });
// pr sums to 1.0, higher values for more-linked nodes

// Spectral bisection
const { partition, algebraicConnectivity } = spectralBisection(A, 3);

// Max-flow: capacity network
const cap = new Float64Array([0, 10, 10, 0, 0, 0, 0, 5, 0, 0, 0, 10, 0, 0, 0, 0]);
const { maxFlow: flow } = maxFlow(cap, 4, 0, 3);
```

### Connections

This chapter synthesises Chapter 9 (the adjacency matrix and its algebra), Chapter 10 (eigenvector centrality and spectral clustering require eigenvalue computation; the power method computes PageRank), Chapter 12 (network flow is a linear programme; max-flow min-cut duality is LP duality applied to networks) and Chapter 13 (random walks on graphs are Markov chains; stationary distributions are eigenvectors of transition matrices). It connects forward to applications in social network analysis, blockchain transaction graphs, supply chain optimisation and recommendation systems.

- **Matrices** (Chapter 9): The adjacency matrix is the fundamental data structure. Matrix multiplication ($A^k$ for walk counting), matrix-vector products (power iteration for centrality) and linear systems (flow conservation constraints) are all operations from Chapter 9. The graph Laplacian inherits all properties of symmetric matrices.

- **Eigenvalues** (Chapter 10): Eigenvector centrality is the dominant eigenvector of $A$. PageRank is the dominant eigenvector of a modified stochastic matrix. Spectral clustering uses the smallest eigenvectors of the Laplacian. The power method from Chapter 10 is the primary computational engine. The spectral theorem guarantees real eigenvalues for the symmetric Laplacian.

- **Constrained Optimisation** (Chapter 12): Network flow is a linear programme. The max-flow min-cut theorem is LP duality applied to the flow LP. The minimum normalised cut problem (before relaxation) is a combinatorial optimisation; its spectral relaxation connects to eigenvalue optimisation.

- **Probability Theory** (Chapter 13): Random walks on graphs are Markov chains. The transition matrix

    $$P = D^{-1}A$$

    defines a stochastic process. Stationary distributions, mixing times and convergence to equilibrium use the theory of Chapter 13. The Erdős–Rényi model applies probability to graph construction.



### What Is Implemented vs. Documented Only

- [x] Adjacency matrix construction (`adjacencyMatrix`)
- [x] Degree vector and Laplacian (`degreeVector`, `laplacian`, `normalizedLaplacian`)
- [x] Degree centrality (`degreeCentrality`)
- [x] Eigenvector centrality via power iteration (`eigenvectorCentrality`)
- [x] PageRank (`pageRank`)
- [x] Transition matrix and stationary distribution (`transitionMatrix`, `stationaryDistribution`)
- [x] Random walk simulation (`simulateRandomWalk`)
- [x] Spectral bisection (`spectralBisection`)
- [x] Spectral clustering (`spectralClustering`)
- [x] Maximum flow / minimum cut (`maxFlow`, `minCut`)
- [x] Erdős–Rényi generation (`erdosRényi`)
- [x] Barabási–Albert generation (`barabasiAlbert`)
- [ ] Betweenness centrality (documented, not implemented — requires all-pairs shortest paths)
- [ ] Community detection via modularity maximisation (documented, not implemented)
- [ ] Watts–Strogatz small-world model (documented, not implemented)

---
### Implementation Context

**Data structures.** Graphs are stored as dense $n \times n$ `Float64Array` adjacency matrices in flat row-major layout. This trades memory $O(n^2)$ for simplicity and compatibility with the linear algebra routines. For large sparse graphs, a CSR representation would reduce memory to $O(n + m)$ and matrix-vector products to $O(m)$, but is not currently implemented.

**Algorithm choices.** Eigenvector centrality and PageRank use power iteration (Algorithms 5.1 and 5.2), which requires only matrix-vector products and converges geometrically at rate

$$|\lambda_2/\lambda_1| \quad\text{(centrality)}\qquad\text{or}\qquad d^k \quad\text{(PageRank with damping } d\text{)}$$

Spectral bisection computes the Fiedler vector (second-smallest eigenvector of the Laplacian) via the full QR eigendecomposition; for large sparse graphs, Lanczos iteration would be more efficient but is deferred. Max-flow uses the Edmonds-Karp variant of Ford-Fulkerson (BFS augmenting paths), guaranteeing $O(VE^2)$ worst-case complexity.

**Numerical pitfalls.** Eigenvector centrality requires an irreducible (connected) graph; disconnected graphs cause the power iteration to converge to a subgraph's eigenvector. PageRank handles dangling nodes (zero out-degree) by distributing their rank uniformly, ensuring convergence. The smallest Laplacian eigenvalues are numerically sensitive for nearly disconnected graphs; $\lambda_2 \approx 0$ can be confused with the zero eigenvalue due to rounding. The normalised Laplacian

$$D^{-1/2}\,L\,D^{-1/2}$$

is undefined for isolated vertices (degree 0).

**Performance.**

- Power iteration: $O(N_{\text{iter}} \cdot n^2)$ per problem (dense matrix-vector product).
- Spectral bisection: $O(n^3)$ for full eigendecomposition.
- Max-flow (Edmonds-Karp): $O(n \cdot m^2)$ where $m$ is the edge count.
- Graph generation: $O(n^2)$ for Erdos-Renyi, $O(nm)$ for Barabasi-Albert.

**Testing.** PageRank is tested on small hand-computed examples and verified to sum to 1. Eigenvector centrality is compared against normalised dominant eigenvectors from the eigenvalue module. The Fiedler vector is tested on barbell graphs (two cliques joined by a bridge) where the optimal bisection is known. Max-flow is verified against the max-flow min-cut theorem: the cut value equals the flow value.

