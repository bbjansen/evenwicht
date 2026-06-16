<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Orbital Mechanics — API Reference

This is the API reference for the TypeScript implementation of Orbital Mechanics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/applications/orbital.ts`

### Data Representation

The 2D orbital state vector is a 4-element `Float64Array`: `[x, y, vx, vy]`. The gravitational parameter $\mu$ (in m$^3$/s$^2$) is passed explicitly. ODE integration uses the `solveODE` function from `evenwicht/dynamics/ode`. Conservation quantities (specific energy and angular momentum) are computed at each time step for validation.

### API Preview

```typescript
// src/applications/orbital.ts

/**
 * Gravitational two-body vector field for 2D orbital integration.
 * Returns a derivative function (t, y) => dydt for use with ODE solvers.
 *
 * @param mu - Gravitational parameter (G * M) in m^3/s^2.
 */
function gravitational2D(mu: number): (t: number, y: Float64Array) => Float64Array;

/** Specific orbital energy: E = v^2/2 - mu/r. */
function specificEnergy(mu: number, y: Float64Array): number;

/** Angular momentum (z-component): h = x*vy - y*vx. */
function angularMomentum(y: Float64Array): number;

/**
 * Hohmann transfer orbit between two circular orbits.
 *
 * @param mu - Gravitational parameter.
 * @param r1 - Radius of inner circular orbit.
 * @param r2 - Radius of outer circular orbit.
 * @returns Delta-v for each burn, total delta-v and transfer time.
 */
function hohmannTransfer(mu: number, r1: number, r2: number): {
  dv1: number; dv2: number; totalDv: number; transferTime: number;
};

/**
 * Eigenvalue-based stability analysis of a Lagrange point.
 * Accepts the 4x4 Jacobian of the linearised equations of motion.
 */
function analyzeStability(jacobian: number[][]): {
  stable: boolean;
  eigenvals: { real: number; imag: number }[];
};
```

### Error Handling

- `gravitational2D` produces a vector field that becomes singular at `r = 0` (collision). The ODE solver should use adaptive step sizing to avoid passing through the singularity.
- `hohmannTransfer` throws if `r1 <= 0` or `r2 <= 0`, or if `r1 === r2` (no transfer needed).
- `specificEnergy` and `angularMomentum` are diagnostic functions; significant drift (relative error exceeding $10^{-6}$ per orbit) in either quantity indicates insufficient integrator accuracy.
- `analyzeStability` classifies a Lagrange point as stable if all eigenvalues of the Jacobian have non-positive real parts; Lagrange points L4 and L5 are linearly stable for mass ratios below the Routh critical value.

### Dependencies

- `src/dynamics/ode.ts` — RK4 for orbital integration
- `src/linear/eigen.ts` — eigenvalue computation for Lagrange point stability
- `src/linear/vector.ts` — vector operations for energy and angular momentum computation

### Usage Examples

```typescript
import { solveODE } from 'evenwicht/dynamics';
import { specificEnergy, angularMomentum, hohmannTransfer } from 'evenwicht/applications/orbital';

// Circular orbit: mu = 1, r = 1, v = 1
const y0 = new Float64Array([1.0, 0.0, 0.0, 1.0]);  // [x, y, vx, vy]
const E = specificEnergy(1.0, y0);  // -0.5 (bound orbit)
const h = angularMomentum(y0);  // 1.0

// Hohmann transfer from LEO to GEO
const transfer = hohmannTransfer(3.986e14, 6.678e6, 4.2164e7);
// transfer.totalDv: total delta-v required
// transfer.transferTime: half the transfer orbit period
```

### Connections

This chapter synthesises Chapter 5 (energy conservation provides the vis-viva equation and classifies orbit types), Chapter 8 (vector cross products define angular momentum, whose constancy confines orbits to a plane), Chapter 10 (eigenvalues of the linearised three-body problem determine Lagrange point stability), Chapter 11 (Hohmann transfer optimisation minimises total delta-v) and Chapter 19 (RK4 integrates the equations of motion). It extends Chapter 39 (Classical Physics; Newton's second law as an ODE, the Kepler problem introduced qualitatively) to a full computational treatment. It connects forward to control systems (Ch 29, orbit station-keeping) and energy systems (Ch 32, satellite power budgets).

- **Integration (Ch. 5)**: The vis-viva equation derives from energy conservation, itself proven by integrating the work done by gravity along the orbit. The transfer time integral (for eccentric anomaly) uses the trapezoidal rule or Gaussian quadrature from Chapter 5.
- **Vectors (Ch. 8)**: Angular momentum $\mathbf{L} = \mathbf{r} \times \mathbf{v}$ is a cross product. Radial velocity $\dot{r} = (\mathbf{r} \cdot \mathbf{v})/r$ is a dot product divided by magnitude. All orbital computations are fundamentally vector operations.
- **Eigenvalues (Ch. 10)**: Stability of Lagrange points is determined by the eigenvalues of the $4 \times 4$ Jacobian of the linearised equations of motion. The tidal tensor's eigenvalues give principal stretch directions. Normal mode frequencies of satellite oscillations about equilibrium are eigenvalues of the restoring force matrix.
- **Optimisation (Ch. 11)**: The Hohmann transfer minimises total $\Delta v$ among two-impulse coplanar transfers; a constrained optimisation problem. More general trajectory optimisation (gravity assists, low-thrust spirals) uses gradient descent on the delta-v objective function with initial condition parameters.
- **ODEs (Ch. 19)**: The entire chapter rests on solving $\ddot{\mathbf{r}} = -\mu\mathbf{r}/r^3$ numerically. The RK4 method from Chapter 19 is the primary computational tool. Drag perturbations add a non-conservative term to the ODE.
- **Matrices (Ch. 9)**: The state transition matrix of a linearised orbit propagation is a $6 \times 6$ matrix. Coordinate transformations between orbital elements and Cartesian state use rotation matrices.
- **Difference Equations (Ch. 18)**: Discrete orbit propagation (Kepler's equation solved iteratively, mean-to-true anomaly conversion) involves fixed-point iteration, the discrete analogue of continuous dynamics.



### What Is Implemented vs. Documented Only

- [x] Gravitational two-body ODE vector field for 2D orbital integration
- [x] Specific energy and angular momentum conservation checking
- [x] Hohmann transfer orbit computation (delta-v, transfer time)
- [x] Lagrange point stability analysis via Jacobian eigenvalues
- [ ] Three-body problem integration (documented; the user constructs the combined vector field manually)
- [ ] Orbital element conversion (Keplerian elements to/from Cartesian state vectors) (deferred)
- [ ] Lambert's problem solver for trajectory design (documented in connections; deferred)
- [ ] Perturbation methods (J2 oblateness, atmospheric drag) (out of scope)
- [ ] Interplanetary trajectory optimisation (out of scope)

---


### Implementation Context

**State vector convention.** For 2D orbital problems, the state vector is a 4-element array $[x, y, v_x, v_y]$. The derivative function takes $(t, \mathbf{y})$ and returns the time derivative of the state vector.

**Conservation law checking.** After integration, energy and angular momentum should be computed at each saved time step. Significant drift (relative error exceeding $10^{-6}$ per orbit) indicates that the step size is too large.

**Hohmann transfer utility.** Both burns and the transfer time are computed from the semi-major axis of the transfer ellipse and the vis-viva equation.

**Eigenvalue analysis for stability.** The linearised equations at a Lagrange point yield a $4 \times 4$ matrix. Eigenvalues with positive real parts indicate instability; purely imaginary eigenvalues indicate marginal stability.
