<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Game Theory — API Reference

This is the API reference for the TypeScript implementation of Game Theory. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

The game theory operations in Evenwicht are located in:

- `src/game-theory/normal-form.ts` — representation of normal-form games, pure strategy Nash finding
- `src/game-theory/mixed-nash.ts` — mixed Nash equilibrium computation for two-player games
- `src/game-theory/zero-sum.ts` — zero-sum game solver via LP (delegates to `src/optimization/linprog.ts`)
- `src/game-theory/replicator.ts` — replicator dynamics integration (delegates to `src/ode/rk4.ts`)

### Data Representation

Payoff matrices are `number[][]` (row-major). Mixed strategies are `number[]` probability vectors summing to 1. Pure strategy Nash equilibria are returned as arrays of `{ row, col, payoff1, payoff2 }` objects. The replicator dynamics returns population state trajectories as `number[][]`.

### API Preview

```typescript
// src/game-theory/normal-form.ts

/**
 * Represent a two-player normal-form game and find pure-strategy Nash equilibria
 * using the best-response method.
 *
 * @param A - Payoff matrix for player 1 (m x k, as number[][]).
 * @param B - Payoff matrix for player 2 (m x k, as number[][]).
 * @returns Array of pure Nash equilibria, each as { row: number, col: number,
 *   payoff1: number, payoff2: number }.
 */
function findPureNash(
    A: number[][],
    B: number[][]
): { row: number; col: number; payoff1: number; payoff2: number }[];
```

```typescript
// src/game-theory/mixed-nash.ts

/**
 * Compute all mixed-strategy Nash equilibria of a 2x2 bimatrix game
 * via the indifference principle.
 *
 * @param A - Player 1 payoff matrix (2x2).
 * @param B - Player 2 payoff matrix (2x2).
 * @returns Object { p: number, q: number, payoff1: number, payoff2: number }
 *   where p = P(player 1 plays row 1) and q = P(player 2 plays column 1).
 *   Returns null if no interior mixed equilibrium exists.
 */
function mixedNash2x2(
    A: [[number, number], [number, number]],
    B: [[number, number], [number, number]]
): { p: number; q: number; payoff1: number; payoff2: number } | null;
```

```typescript
// src/game-theory/zero-sum.ts

/**
 * Solve a two-player zero-sum game by formulating and solving the
 * equivalent linear program (Chapter 12).
 *
 * @param A - Payoff matrix for the row player (m x k).
 * @param opts - Optional: { tolerance?: number } for LP solver precision.
 * @returns Object { p: number[], q: number[], value: number } where
 *   p is the row player's optimal mixed strategy, q is the column
 *   player's optimal mixed strategy, and value is the game value v.
 */
function solveZeroSum(
    A: number[][],
    opts?: { tolerance?: number }
): { p: number[]; q: number[]; value: number };
```

```typescript
// src/game-theory/replicator.ts

/**
 * Integrate the replicator dynamics for a symmetric game using the
 * fourth-order Runge–Kutta method (Chapter 19).
 *
 * @param A - Payoff matrix of the symmetric game (m x m).
 * @param x0 - Initial population state (length m, sums to 1, all nonneg).
 * @param T - Total integration time.
 * @param dt - Step size.
 * @returns Array of population states at each time step, each of length m.
 */
function replicator(
    A: number[][],
    x0: number[],
    T: number,
    dt: number
): number[][];
```

### Error Handling

- `findPureNash` validates that $A$ and $B$ have identical dimensions. Throws if matrices are empty or dimensions mismatch.
- `mixedNash2x2` returns `null` (rather than throwing) when the denominator in F36.2 is zero or the solution lies outside $[0,1]$. This signals that no interior mixed equilibrium exists; the game has only pure or boundary equilibria.
- `solveZeroSum` delegates to the LP solver and propagates its `status` field. If the LP is infeasible (which should not occur for valid zero-sum games), the function throws with a diagnostic message.
- `replicator` validates that `x0` sums to 1 (within tolerance $10^{-10}$) and has all nonnegative entries. Throws if the initial state is not in the simplex.

### Dependencies

- `src/optimization/linprog.ts` — simplex method for zero-sum game solver
- `src/dynamics/ode.ts` — RK4 for replicator dynamics integration

### Usage Examples

```typescript
import { findPureNash, mixedNash2x2, solveZeroSum } from 'evenwicht/game-theory';

// Prisoner's dilemma: find pure Nash (both defect)
const A = [[3, 0], [5, 1]];  // row player payoffs
const B = [[3, 5], [0, 1]];  // column player payoffs
const nash = findPureNash(A, B);
// nash = [{ row: 1, col: 1, payoff1: 1, payoff2: 1 }]

// Matching pennies: mixed Nash
const mp = mixedNash2x2([[1, -1], [-1, 1]], [[-1, 1], [1, -1]]);
// mp.p = 0.5, mp.q = 0.5, mp.payoff1 = 0, mp.payoff2 = 0

// Zero-sum game via LP
const zs = solveZeroSum([[3, -1], [-2, 1]]);
// zs.value: game value; zs.p, zs.q: optimal mixed strategies
```

### Connections

This chapter draws on the equilibrium analysis of Chapter 33 (Nash equilibrium is a fixed-point concept; evolutionarily stable strategies are stable equilibria of a dynamical system). The LP formulation of zero-sum games is a direct application of Chapter 12. Mixed strategies require the expected value machinery of Chapter 13. The replicator dynamics constitute an autonomous ODE system analysed with the tools of Chapter 19. The concept of mechanism design connects forward to optimisation under incentive constraints, extending the Lagrangian framework of Chapter 12 to settings with private information.

- **Chapter 9 (Matrices)**: Payoff matrices are the data structure of game theory. The bilinear form $\mathbf{p}^T A \mathbf{q}$ for expected payoff computation is matrix multiplication. The indifference conditions that determine mixed equilibria reduce to solving linear systems $A\mathbf{q} = c\mathbf{1}$. The replicator dynamics involve the matrix-vector product $A\mathbf{x}$.

- **Chapter 12 (Constrained Optimisation & LP)**: The minimax theorem (Theorem 36.15) is equivalent to LP strong duality. Every finite zero-sum game reduces to a linear programme, solvable by the simplex method. Mechanism design constraints (incentive compatibility, individual rationality) are linear inequalities that define a feasible polyhedron for the designer's optimisation.

- **Chapter 13 (Probability Theory)**: Mixed strategies are probability distributions over actions (Definition 36.7). Expected payoff is computed via the expectation operator (Definition 36.8). The Nash existence theorem relies on properties of probability simplices (compact, convex subsets of $\mathbb{R}^n$). Bayesian games involve conditional probabilities and expectation over type distributions.

- **Chapter 19 (ODEs)**: The replicator dynamics (Definition 36.21) constitute an autonomous ODE system on the probability simplex. Stability of evolutionary equilibria (Theorem 36.23) is analysed via the eigenvalues of the Jacobian. Numerical integration uses the Runge–Kutta methods developed in Chapter 19.

- **Chapter 33 (Equilibrium & Steady States)**: Nash equilibrium is a fixed-point concept: the profile $(s_1^*, \ldots, s_n^*)$ is a fixed point of the best-response correspondence. The ESS is a stable equilibrium of the replicator dynamics in the sense of Chapter 33. The folk theorem describes equilibria of repeated dynamic systems.



### What Is Implemented vs. Documented Only

- [x] Pure-strategy Nash equilibrium finder for bimatrix games (`findPureNash`)
- [x] Mixed Nash for $2 \times 2$ games via indifference conditions (`mixedNash2x2`)
- [x] Zero-sum game solver via LP reduction (`solveZeroSum`)
- [x] Replicator dynamics integrator (`replicator`)
- [ ] Support enumeration for general $m \times k$ bimatrix games (deferred)
- [ ] Lemke–Howson algorithm (deferred)
- [ ] Extensive-form game representation and backward induction (deferred)
- [ ] Auction simulator (deferred)

---


### Implementation Context

**Best-response enumeration.** `findPureNash` iterates over all $m \times k$ cells to identify mutual best responses, running in $O(mk)$ time. Payoff matrices are plain `number[][]`; no matrix library is needed since only element-wise comparisons are performed.

**Indifference principle for 2x2 games.** `mixedNash2x2` computes mixing probabilities via the closed-form formula with denominator $a_{11} - a_{12} - a_{21} + a_{22}$. When this quantity is near zero, the equilibrium is structurally unstable and the result is highly sensitive to payoff perturbations. The function returns `null` rather than throwing to signal the absence of an interior mixed equilibrium.

**LP reduction for zero-sum games.** `solveZeroSum` reformulates the minimax problem as a linear programme and delegates to the simplex method from Chapter 12. LP solver tolerance (default $10^{-10}$) governs feasibility checks. For games with more than roughly 100 strategies per player, interior-point methods would be preferable, though the current implementation uses simplex.

**Simplex projection in replicator dynamics.** The replicator ODE $\dot{x}_i = x_i[(A\mathbf{x})_i - \mathbf{x}^T A \mathbf{x}]$ is integrated by RK4 with a simplex projection after each step: negative components are clipped to zero and the vector is renormalised. This prevents floating-point drift from producing negative population shares but introduces a small projection error. Near the simplex boundary, population shares approach zero and timescales diverge, requiring smaller step sizes.

**Testing strategy.** Pure Nash tests use classic textbook games (Prisoner's Dilemma, Battle of the Sexes) with known equilibria. Mixed Nash tests verify the Matching Pennies equilibrium at $p = q = 0.5$. Zero-sum tests compare LP output against analytically known minimax values. Replicator tests check that the population state remains in the simplex and that known ESS attract nearby trajectories.
