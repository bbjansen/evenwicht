<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Robotics & Kinematics — API Reference

This is the API reference for the TypeScript implementation of Robotics & Kinematics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/robotics/rotation.ts` — 2D/3D rotation matrices, homogeneous transformations
- `src/robotics/kinematics.ts` — forward kinematics, Jacobian, inverse kinematics
- `src/robotics/trajectory.ts` — cubic polynomial trajectory planning
- `src/robotics/dynamics.ts` — single-link arm simulation with PID control

### Data Representation

Rotation and homogeneous transformation matrices are stored as flat row-major `Float64Array` values. Joint angles and link lengths are `Float64Array`. End-effector positions are `{ x: number, y: number }` objects. The Jacobian is a flat row-major `Float64Array` of size $2 \times n$ (for planar manipulators).

### API Preview

```typescript
// src/robotics/rotation.ts

/**
 * Construct a 2D rotation matrix as a flat 4-element Float64Array (row-major 2x2).
 *
 * @param theta - Rotation angle in radians.
 * @returns Float64Array [cos(theta), -sin(theta), sin(theta), cos(theta)].
 */
function rotation2D(theta: number): Float64Array;

/**
 * Construct a 3D rotation matrix about the z-axis as a flat 9-element Float64Array (row-major 3x3).
 *
 * @param theta - Rotation angle in radians.
 * @returns Float64Array representing R_z(theta).
 */
function rotationZ(theta: number): Float64Array;

/**
 * Construct a 2D homogeneous transformation matrix (3x3, row-major, 9 elements).
 *
 * @param theta - Rotation angle in radians.
 * @param dx - Translation in x.
 * @param dy - Translation in y.
 * @returns Float64Array representing the 3x3 homogeneous matrix.
 */
function homogeneous2D(theta: number, dx: number, dy: number): Float64Array;
```

```typescript
// src/robotics/kinematics.ts

/**
 * Compute forward kinematics for a planar serial manipulator.
 *
 * @param thetas - Joint angles (n elements), in radians.
 * @param lengths - Link lengths (n elements).
 * @returns Object { x, y } giving end-effector position.
 */
function forwardKinematics2D(
  thetas: Float64Array,
  lengths: Float64Array,
): { x: number; y: number };

/**
 * Compute the Jacobian matrix numerically via central finite differences.
 *
 * @param fk - Forward kinematics function mapping joint angles to [x, y].
 * @param thetas - Current joint angles.
 * @param h - Finite difference step size (default: 1e-7).
 * @returns Float64Array representing the 2 x n Jacobian (row-major).
 */
function numericalJacobian(
  fk: (thetas: Float64Array) => { x: number; y: number },
  thetas: Float64Array,
  h?: number,
): Float64Array;

/**
 * Compute the analytical Jacobian for a 2-link planar arm.
 *
 * @param theta1 - First joint angle.
 * @param theta2 - Second joint angle.
 * @param l1 - First link length.
 * @param l2 - Second link length.
 * @returns Float64Array representing the 2x2 Jacobian (row-major).
 */
function jacobian2Link(
  theta1: number,
  theta2: number,
  l1: number,
  l2: number,
): Float64Array;

/**
 * Solve inverse kinematics via Newton's method.
 *
 * @param fk - Forward kinematics function.
 * @param target - Desired end-effector position { x, y }.
 * @param theta0 - Initial guess for joint angles.
 * @param options - { tolerance?: number, maxIterations?: number, h?: number }.
 * @returns Object { thetas, iterations, error } with solution angles.
 * @throws Error if target is unreachable or iteration does not converge.
 */
function inverseKinematics(
  fk: (thetas: Float64Array) => { x: number; y: number },
  target: { x: number; y: number },
  theta0: Float64Array,
  options?: { tolerance?: number; maxIterations?: number; h?: number },
): { thetas: Float64Array; iterations: number; error: number };
```

```typescript
// src/robotics/trajectory.ts

/** Compute cubic polynomial trajectory coefficients (zero velocity at endpoints). */
function cubicTrajectory(
  thetaStart: number, thetaEnd: number, tf: number,
): { a0: number; a1: number; a2: number; a3: number };

/** Evaluate cubic trajectory at time t, returning position, velocity, acceleration. */
function evaluateCubicTrajectory(
  coeffs: { a0: number; a1: number; a2: number; a3: number }, t: number,
): { position: number; velocity: number; acceleration: number };
```

```typescript
// src/robotics/dynamics.ts

/** Simulate single-link pendulum arm dynamics with PID control using RK4. */
function simulatePendulumArm(
  params: { mass: number; length: number; gravity: number },
  controller: { Kp: number; Kd: number; Ki: number },
  desired: (t: number) => { theta: number; dtheta: number; ddtheta: number },
  initial: { theta0: number; dtheta0: number },
  tEnd: number, dt: number,
): { t: Float64Array; theta: Float64Array; dtheta: Float64Array; torque: Float64Array };
```

### Error Handling

- `forwardKinematics2D` throws if `thetas.length !== lengths.length` or if either array is empty.
- `inverseKinematics` throws if the target is provably outside the workspace ($\|\mathbf{p}^*\| > \sum l_i$ or $\|\mathbf{p}^*\| < |l_1 - l_2 - \cdots|$), or if the iteration exceeds `maxIterations` without convergence.
- `cubicTrajectory` throws if `tf <= 0`.
- `simulatePendulumArm` throws if `dt <= 0` or `tEnd <= 0` or any physical parameter is non-positive.

### Dependencies

- `src/linear/solve.ts` — solving $J\Delta\theta = \mathbf{e}$ in inverse kinematics
- `src/linear/matrix.ts` — matrix multiplication for transformation chains
- `src/numeric/gradient.ts` — central differences for numerical Jacobian
- `src/dynamics/ode.ts` — RK4 for arm dynamics simulation

### Usage Examples

```typescript
import { rotation2D, forwardKinematics2D, inverseKinematics, cubicTrajectory } from 'evenwicht/robotics';

// 2D rotation matrix for 45 degrees
const R = rotation2D(Math.PI / 4);

// Forward kinematics: 2-link arm at 45 and -30 degrees
const pos = forwardKinematics2D(
  new Float64Array([Math.PI / 4, -Math.PI / 6]),
  new Float64Array([1.0, 0.8]),
);
// pos.x, pos.y: end-effector position

// Inverse kinematics to reach target (1.2, 0.5)
const fk = (t: Float64Array) => forwardKinematics2D(t, new Float64Array([1.0, 0.8]));
const ik = inverseKinematics(fk, { x: 1.2, y: 0.5 }, new Float64Array([0, 0]));
// ik.thetas: joint angles that reach the target

// Cubic trajectory from 0 to pi/2 in 2 seconds
const traj = cubicTrajectory(0, Math.PI / 2, 2.0);
```

### Connections

This chapter synthesises Chapter 7 (the Jacobian relates joint velocities to end-effector velocities), Chapter 9 (homogeneous transformation matrices encode rotations and translations), Chapter 11 (inverse kinematics is a nonlinear root-finding problem solved by Newton's method), Chapter 19 (robot dynamics are second-order ODEs integrated by RK4) and Chapter 29 (PID and computed-torque control stabilise the robot along desired trajectories). It connects forward to motion planning, computer vision and autonomous systems.

**Chapter 7 (Multivariate Calculus)**. The manipulator Jacobian is a direct application of the Jacobian matrix of Chapter 7. Singularity analysis (determining where $\det(J) = 0$) is equivalent to finding where the derivative map drops rank.

**Chapter 9 (Matrices)**. Every computation rests on matrix operations: rotation matrices, transformation chain multiplication, solving $J\Delta\boldsymbol{\theta} = \mathbf{e}$, computing determinants for singularity detection and matrix inversion.

**Chapter 10 (Eigenvalues)**. Closed-loop stability depends on eigenvalues of the error dynamics. For computed torque control, the characteristic equation $\lambda^2 + K_d\lambda + K_p = 0$ must have roots with negative real parts.

**Chapter 11 (Optimisation)**. Inverse kinematics is Newton's method applied to $\text{FK}(\boldsymbol{\theta}) - \mathbf{p}^* = \mathbf{0}$. Convergence theory and the pseudoinverse for over/underdetermined systems come from Chapter 11. Redundant robots pose IK as constrained optimisation.

**Chapter 19 (ODEs)**. Robot dynamics produce second-order ODEs converted to first-order systems and integrated by RK4. Step size selection, integrator stability and stiffness considerations apply directly.

**Chapter 29 (Control Systems)**. PID control and stability analysis transfer directly. Computed torque control exploits knowledge of $M$, $C$, $\mathbf{g}$ for exact linearisation; feedback linearisation in nonlinear control.



### What Is Implemented vs. Documented Only

- [x] 2D rotation matrix construction (`rotation2D`)
- [x] 3D rotation about z-axis (`rotationZ`)
- [x] 2D homogeneous transformation (`homogeneous2D`)
- [x] Forward kinematics for planar manipulators (`forwardKinematics2D`)
- [x] Numerical Jacobian via central differences (`numericalJacobian`)
- [x] Analytical 2-link Jacobian (`jacobian2Link`)
- [x] Inverse kinematics via Newton's method (`inverseKinematics`)
- [x] Cubic trajectory planning (`cubicTrajectory`, `evaluateCubicTrajectory`)
- [x] Pendulum arm dynamics with PID (`simulatePendulumArm`)
- [ ] Quintic trajectory (documented; extend polynomial solver from Chapter 9)
- [ ] 3D forward kinematics with DH parameters (documented; uses 4x4 matrix chain)
- [ ] Computed torque control for multi-DOF (documented; requires full $M$, $C$ and $\mathbf{g}$ computation)
- [ ] Workspace boundary computation (documented — use Algorithm 5.6 with `forwardKinematics2D`)

---


### Implementation Context

**Flat row-major storage.** Rotation and homogeneous transformation matrices are stored as flat `Float64Array` values rather than nested arrays. This avoids allocation overhead during the forward kinematics matrix chain, where $n$ matrix multiplications of $3 \times 3$ matrices are performed sequentially.

**Numerical Jacobian step size.** The central-difference Jacobian uses a default perturbation $h = 10^{-7}$, balancing truncation error ($O(h^2)$) against roundoff ($O(\varepsilon_{\text{mach}}/h)$). The optimal step size for double precision is $h \approx \varepsilon_{\text{mach}}^{1/3} \approx 6 \times 10^{-6}$; the default is slightly larger for safety. An analytical Jacobian is provided for the 2-link case and should be preferred when available.

**Singularity handling in inverse kinematics.** When $\det(J) \approx 0$, the Newton step $J^{-1}\mathbf{e}$ amplifies errors catastrophically. The implementation detects unreachable targets ($\|\mathbf{p}^*\| > \sum l_i$) before iterating and throws if the iteration stalls. Damped least-squares (Levenberg-Marquardt) would trade accuracy for stability near singularities but is not currently implemented.

**Multiple IK solutions.** Newton's method converges to a single solution determined by the initial guess. For a 2-link arm, two elbow-up/elbow-down solutions exist generically. To find both, the user must run `inverseKinematics` with different initial guesses spanning the configuration space.

**Cubic trajectory smoothness.** Cubic polynomials ensure continuous position and velocity ($C^1$ at waypoints) but have discontinuous acceleration, producing torque jumps. Quintic polynomials (documented, deferred) would add acceleration continuity. The cubic coefficients are computed in $O(1)$ from boundary conditions with zero velocity at endpoints.

**Testing strategy.** Forward kinematics tests verify known configurations (fully extended arm, right-angle elbow). Jacobian tests compare numerical and analytical Jacobians for the 2-link case. IK tests verify round-trip consistency: `inverseKinematics(forwardKinematics(theta)) == theta`. Trajectory tests check boundary conditions ($\theta(0) = \theta_s$, $\theta(t_f) = \theta_f$, $\dot\theta(0) = \dot\theta(t_f) = 0$).
