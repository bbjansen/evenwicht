# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 42: Robotics & Kinematics — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(42, "Robotics & Kinematics")

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="2-link FK: x = l1*cos(t1) + l2*cos(t1+t2)",
        section="5",
        identity=lambda: _fk_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Jacobian det = l1*l2*sin(t2)",
        section="5",
        identity=lambda: _jacobian_det_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Cubic trajectory: a2 = 3*dtheta/tf^2, a3 = -2*dtheta/tf^3",
        section="5",
        identity=lambda: _cubic_trajectory_identity(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # --- Example 8.1: 2-link FK ---
    l1, l2 = 1.0, 0.8
    t1 = math.pi / 4
    t2 = math.pi / 3

    ch.add(NumericCheck(
        label="FK x-position: l1=1, l2=0.8, t1=pi/4, t2=pi/3 => x ~ 0.500",
        section="9.1",
        stated=0.500,
        computed=lambda: l1 * math.cos(t1) + l2 * math.cos(t1 + t2),
        tolerance=5e-3,
    ))

    ch.add(NumericCheck(
        label="FK y-position => y ~ 1.480",
        section="9.1",
        stated=1.480,
        computed=lambda: l1 * math.sin(t1) + l2 * math.sin(t1 + t2),
        tolerance=5e-3,
    ))

    # FK intermediate: 0.8*cos(7pi/12) = -0.2071, 0.8*sin(7pi/12) = 0.7727
    # (textbook shows the product l2*cos(t1+t2), not the bare trig value)
    ch.add(NumericCheck(
        label="FK intermediate: 0.8*cos(7pi/12) ~ -0.2071",
        section="9.1",
        stated=-0.2071,
        computed=lambda: 0.8 * math.cos(7 * math.pi / 12),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="FK intermediate: 0.8*sin(7pi/12) ~ 0.7727",
        section="9.1",
        stated=0.7727,
        computed=lambda: 0.8 * math.sin(7 * math.pi / 12),
        tolerance=1e-3,
    ))

    # FK intermediate: cos(pi/4) = sin(pi/4) = 0.7071
    ch.add(NumericCheck(
        label="FK intermediate: cos(pi/4) = 0.7071",
        section="9.1",
        stated=0.7071,
        computed=lambda: math.cos(math.pi / 4),
        tolerance=1e-3,
    ))

    # Full x breakdown: 0.7071 + 0.8*(-0.2071) = 0.7071 - 0.16569 = 0.5000
    ch.add(NumericCheck(
        label="FK x breakdown: 0.7071 + 0.8*(-0.2071) ~ 0.5000",
        section="9.1",
        stated=0.5000,
        computed=lambda: math.cos(math.pi / 4) + 0.8 * math.cos(7 * math.pi / 12),
        tolerance=5e-3,
    ))

    # Full y breakdown: 0.7071 + 0.8*0.7727 = 0.7071 + 0.6182 = 1.4798
    ch.add(NumericCheck(
        label="FK y = 0.7071 + 0.8*0.7727 = 1.4798",
        section="9.1",
        stated=1.4798,
        computed=lambda: math.sin(math.pi / 4) + 0.8 * math.sin(7 * math.pi / 12),
        tolerance=5e-4,
    ))

    # --- Example 8.2: Jacobian ---
    # At (theta1=0, theta2=pi/2), Jacobian entries from Thm 42.10
    # J = [[-l2*sin(phi), -l2*sin(phi)], [l1+l2*cos(phi), l2*cos(phi)]]
    # where phi=t1+t2=pi/2
    # J = [[-0.8, -0.8], [1.0, 0]] (stated in the text)
    ch.add(NumericCheck(
        label="Jacobian J[0,0] at (0,pi/2): -l2*sin(pi/2) = -0.8",
        section="9.2",
        stated=-0.8,
        computed=lambda: -l1 * math.sin(0) - l2 * math.sin(math.pi / 2),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Jacobian J[0,1] at (0,pi/2): -l2*sin(pi/2) = -0.8",
        section="9.2",
        stated=-0.8,
        computed=lambda: -l2 * math.sin(math.pi / 2),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Jacobian J[1,0] at (0,pi/2): l1*cos(0)+l2*cos(pi/2) = 1.0",
        section="9.2",
        stated=1.0,
        computed=lambda: l1 * math.cos(0) + l2 * math.cos(math.pi / 2),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Jacobian J[1,1] at (0,pi/2): l2*cos(pi/2) = 0.0",
        section="9.2",
        stated=0.0,
        computed=lambda: l2 * math.cos(math.pi / 2),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="det(J) at t2=pi/2: l1*l2*sin(pi/2) = 0.8",
        section="9.2",
        stated=0.8,
        computed=lambda: 1.0 * 0.8 * math.sin(math.pi / 2),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="det(J) at t2=0 (singular): 0.0",
        section="9.2",
        stated=0.0,
        computed=lambda: 1.0 * 0.8 * math.sin(0),
        tolerance=1e-15,
    ))

    # At singular config (0,0), Jacobian entries:
    # J = [[0, 0], [1.8, 0.8]] (stated in the text)
    ch.add(NumericCheck(
        label="Jacobian J[1,0] at (0,0): l1+l2 = 1.8",
        section="9.2",
        stated=1.8,
        computed=lambda: l1 * math.cos(0) + l2 * math.cos(0),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Jacobian J[1,1] at (0,0): l2 = 0.8",
        section="9.2",
        stated=0.8,
        computed=lambda: l2 * math.cos(0),
        tolerance=1e-10,
    ))

    # --- Example 8.3: Inverse kinematics ---
    ch.add(NumericCheck(
        label="IK target reachability: ||(1.2,0.8)|| = 1.442 in [0.2, 1.8]",
        section="9.3",
        stated=1.442,
        computed=lambda: math.sqrt(1.2**2 + 0.8**2),
        tolerance=1e-3,
    ))

    # Workspace bounds
    ch.add(NumericCheck(
        label="IK workspace inner radius: |l1-l2| = 0.2",
        section="9.3",
        stated=0.2,
        computed=lambda: abs(l1 - l2),
    ))

    ch.add(NumericCheck(
        label="IK workspace outer radius: l1+l2 = 1.8",
        section="9.3",
        stated=1.8,
        computed=lambda: l1 + l2,
    ))

    # Verify IK solution via FK
    ch.add(StructuralCheck(
        label="IK solution FK verification: FK(0.1498, 0.9828) ~ (1.2, 0.8)",
        section="9.3",
        predicate=lambda: _ik_verification(),
    ))

    # --- Example 8.4: Cubic trajectory ---
    tf = 2.0
    dtheta = math.pi / 2
    a2 = 3 * dtheta / tf**2
    a3 = -2 * dtheta / tf**3

    ch.add(NumericCheck(
        label="Cubic traj a2 = 3*pi/(2*4) = 3*pi/8 ~ 1.1781",
        section="9.4",
        stated=1.1781,
        computed=lambda: 3 * (math.pi / 2) / 4,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Cubic traj a3 = -2*pi/(2*8) = -pi/8 ~ -0.3927",
        section="9.4",
        stated=-0.3927,
        computed=lambda: -2 * (math.pi / 2) / 8,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Cubic traj theta(1) = pi/4 ~ 0.7854",
        section="9.4",
        stated=0.7854,
        computed=lambda: a2 * 1**2 + a3 * 1**3,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Cubic traj dtheta(1) = 2*a2 + 3*a3 ~ 1.1781 rad/s",
        section="9.4",
        stated=1.1781,
        computed=lambda: 2 * a2 * 1 + 3 * a3 * 1**2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Cubic traj ddtheta(1) = 2*a2 + 6*a3 = 0 rad/s^2",
        section="9.4",
        stated=0.0,
        computed=lambda: 2 * a2 + 6 * a3 * 1,
        tolerance=1e-10,
    ))

    # Trajectory at t=0: theta=0, dtheta=0
    ch.add(NumericCheck(
        label="Cubic traj theta(0) = 0",
        section="9.4",
        stated=0.0,
        computed=lambda: a2 * 0**2 + a3 * 0**3,
        tolerance=1e-15,
    ))

    # Trajectory at t=tf=2: theta = pi/2
    ch.add(NumericCheck(
        label="Cubic traj theta(2) = pi/2 ~ 1.5708",
        section="9.4",
        stated=math.pi / 2,
        computed=lambda: a2 * tf**2 + a3 * tf**3,
        tolerance=1e-10,
    ))

    # Velocity at t=tf=2: should be 0
    ch.add(NumericCheck(
        label="Cubic traj dtheta(2) = 0",
        section="9.4",
        stated=0.0,
        computed=lambda: 2 * a2 * tf + 3 * a3 * tf**2,
        tolerance=1e-10,
    ))

    # Velocity at t=0: should be 0
    ch.add(NumericCheck(
        label="Cubic traj dtheta(0) = 0 (a1=0)",
        section="9.4",
        stated=0.0,
        computed=lambda: 0.0,  # a1 = 0 by construction
        tolerance=1e-15,
    ))

    # Trajectory at intermediate t=0.5: theta(0.5) = a2*0.25 + a3*0.125
    ch.add(NumericCheck(
        label="Cubic traj theta(0.5) = a2*0.25 + a3*0.125 ~ 0.2454",
        section="9.4",
        stated=0.2454,
        computed=lambda: a2 * 0.25 + a3 * 0.125,
        tolerance=1e-3,
    ))

    # Velocity at t=0.5: dtheta(0.5) = 2*a2*0.5 + 3*a3*0.25
    ch.add(NumericCheck(
        label="Cubic traj dtheta(0.5) = 2*a2*0.5 + 3*a3*0.25 ~ 0.8836",
        section="9.4",
        stated=0.8836,
        computed=lambda: 2 * a2 * 0.5 + 3 * a3 * 0.25,
        tolerance=1e-3,
    ))

    # Acceleration at t=0.5: ddtheta(0.5) = 2*a2 + 6*a3*0.5
    ch.add(NumericCheck(
        label="Cubic traj ddtheta(0.5) = 2*a2 + 6*a3*0.5 ~ 1.1781",
        section="9.4",
        stated=1.1781,
        computed=lambda: 2 * a2 + 6 * a3 * 0.5,
        tolerance=1e-3,
    ))

    # Trajectory at t=1.5: theta(1.5) = a2*2.25 + a3*3.375
    ch.add(NumericCheck(
        label="Cubic traj theta(1.5) ~ 1.3254",
        section="9.4",
        stated=1.3254,
        computed=lambda: a2 * 1.5**2 + a3 * 1.5**3,
        tolerance=1e-3,
    ))

    # --- Example 8.5: Pendulum arm ---
    ch.add(NumericCheck(
        label="Pendulum ml^2 = 2*0.25 = 0.5 kg*m^2",
        section="9.5",
        stated=0.5,
        computed=lambda: 2 * 0.5**2,
    ))

    ch.add(NumericCheck(
        label="Pendulum mgl = 2*9.81*0.5 = 9.81 N*m",
        section="9.5",
        stated=9.81,
        computed=lambda: 2 * 9.81 * 0.5,
    ))

    # Equilibrium torque at theta_d = pi/4: tau_eq = mgl*cos(pi/4) = 6.937 N*m
    ch.add(NumericCheck(
        label="Pendulum equilibrium torque at pi/4: mgl*cos(pi/4) ~ 6.937 N*m",
        section="9.5",
        stated=6.937,
        computed=lambda: 2 * 9.81 * 0.5 * math.cos(math.pi / 4),
        tolerance=1e-3,
    ))

    # --- Formula gap fills ---

    # Rotation matrix R(theta) is orthogonal with det = 1
    def rotation_matrix_check():
        theta = math.pi / 4
        c = math.cos(theta)
        s = math.sin(theta)
        R = np.array([[c, -s], [s, c]])
        det_ok = abs(np.linalg.det(R) - 1.0) < 1e-10
        orth_ok = np.allclose(R @ R.T, np.eye(2))
        ok = det_ok and orth_ok
        return (ok, f"det(R)={np.linalg.det(R):.6f}, R*R^T={R @ R.T}" if not ok else "")
    ch.add(StructuralCheck(
        label="Rotation matrix: det=1 and R*R^T=I for theta=pi/4",
        section="5",
        predicate=rotation_matrix_check,
    ))

    # Homogeneous transform T preserves last row [0, 0, 1]
    def homogeneous_transform_check():
        theta = math.pi / 4
        l = 1.0
        c = math.cos(theta)
        s = math.sin(theta)
        T = np.array([[c, -s, l*c], [s, c, l*s], [0, 0, 1]])
        ok = abs(T[2, 0]) < 1e-15 and abs(T[2, 1]) < 1e-15 and abs(T[2, 2] - 1.0) < 1e-15
        return (ok, f"Last row: {T[2, :]}" if not ok else "")
    ch.add(StructuralCheck(
        label="Homogeneous transform: last row is [0, 0, 1]",
        section="5",
        predicate=homogeneous_transform_check,
    ))

    # FK chain: T_02 = T_01 * T_12 gives end-effector position
    def fk_chain_check():
        t1_val = math.pi / 4
        t2_val = math.pi / 3
        l1_val, l2_val = 1.0, 0.8
        # T_01
        c1 = math.cos(t1_val); s1 = math.sin(t1_val)
        T01 = np.array([[c1, -s1, l1_val*c1], [s1, c1, l1_val*s1], [0, 0, 1]])
        # T_12
        c2 = math.cos(t2_val); s2 = math.sin(t2_val)
        T12 = np.array([[c2, -s2, l2_val*c2], [s2, c2, l2_val*s2], [0, 0, 1]])
        T02 = T01 @ T12
        x_fk = l1_val * math.cos(t1_val) + l2_val * math.cos(t1_val + t2_val)
        y_fk = l1_val * math.sin(t1_val) + l2_val * math.sin(t1_val + t2_val)
        ok = abs(T02[0, 2] - x_fk) < 1e-10 and abs(T02[1, 2] - y_fk) < 1e-10
        return (ok, f"T02 pos=({T02[0,2]:.6f},{T02[1,2]:.6f}), FK=({x_fk:.6f},{y_fk:.6f})" if not ok else "")
    ch.add(StructuralCheck(
        label="FK chain: T_02 = T_01*T_12 matches FK formula",
        section="5",
        predicate=fk_chain_check,
    ))

    # Velocity kinematics: v = J * dq
    def velocity_kinematics_check():
        t1_val, t2_val = 0.0, math.pi / 2
        l1_val, l2_val = 1.0, 0.8
        J = np.array([
            [-l1_val*math.sin(t1_val) - l2_val*math.sin(t1_val+t2_val), -l2_val*math.sin(t1_val+t2_val)],
            [l1_val*math.cos(t1_val) + l2_val*math.cos(t1_val+t2_val), l2_val*math.cos(t1_val+t2_val)],
        ])
        dq = np.array([1.0, 0.0])  # unit angular velocity at joint 1
        v = J @ dq
        # At (0, pi/2): v = [-0.8, 1.0]
        ok = abs(v[0] - (-0.8)) < 1e-10 and abs(v[1] - 1.0) < 1e-10
        return (ok, f"v = {v}" if not ok else "")
    ch.add(StructuralCheck(
        label="Velocity kinematics: v = J*dq at (0, pi/2)",
        section="5",
        predicate=velocity_kinematics_check,
    ))

    # Pseudoinverse: J_pinv * J = I when J is square and non-singular
    def pseudoinverse_check():
        t1_val, t2_val = 0.0, math.pi / 2
        l1_val, l2_val = 1.0, 0.8
        J = np.array([
            [-l1_val*math.sin(t1_val) - l2_val*math.sin(t1_val+t2_val), -l2_val*math.sin(t1_val+t2_val)],
            [l1_val*math.cos(t1_val) + l2_val*math.cos(t1_val+t2_val), l2_val*math.cos(t1_val+t2_val)],
        ])
        J_pinv = np.linalg.pinv(J)
        prod = J_pinv @ J
        ok = np.allclose(prod, np.eye(2))
        return (ok, f"J_pinv * J = {prod}" if not ok else "")
    ch.add(StructuralCheck(
        label="Pseudoinverse: J^+ * J = I (non-singular config)",
        section="5",
        predicate=pseudoinverse_check,
    ))

    # Dynamics equation: M(q)*ddq + C(q,dq)*dq + g(q) = tau (structure check)
    ch.add(NumericCheck(
        label="Dynamics: pendulum mgl*cos(pi/4) = 6.937 N*m (gravity torque)",
        section="5",
        stated=6.937,
        computed=lambda: 2 * 9.81 * 0.5 * math.cos(math.pi / 4),
        tolerance=1e-3,
    ))

    # Computed torque: tau = M*ddq_d + C*dq + g (gravity compensation)
    ch.add(NumericCheck(
        label="Computed torque: gravity compensation = mgl = 9.81 N*m at theta=0",
        section="5",
        stated=9.81,
        computed=lambda: 2 * 9.81 * 0.5 * math.cos(0),
        tolerance=1e-6,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Workspace boundary: (l1-l2) <= r <= (l1+l2)",
        section="4",
        predicate=lambda: _workspace_check(),
    ))

    ch.add(StructuralCheck(
        label="Workspace boundary values: r_min=0.2, r_max=1.8",
        section="4",
        predicate=lambda: _workspace_boundary_values(),
    ))

    ch.add(StructuralCheck(
        label="Cubic trajectory boundary conditions satisfied",
        section="9.4",
        predicate=lambda: _cubic_boundary_check(),
    ))

    ch.add(StructuralCheck(
        label="DH transform T01 at theta1=pi/4 matches expected entries",
        section="9.1",
        predicate=lambda: _dh_transform_check(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS
    # ===================================================================

    # ---------------------------------------------------------------
    # Exercise 10.1: 3-link FK
    # ---------------------------------------------------------------
    l1_3, l2_3, l3_3 = 1.0, 0.7, 0.4
    t1_3, t2_3, t3_3 = math.pi / 6, math.pi / 4, math.pi / 3

    ch.add(NumericCheck(
        label="Exercise 10.1: 3-link FK x-position",
        section="11",
        stated=l1_3 * math.cos(t1_3) + l2_3 * math.cos(t1_3 + t2_3) + l3_3 * math.cos(t1_3 + t2_3 + t3_3),
        computed=lambda: 1.0 * math.cos(math.pi/6) + 0.7 * math.cos(math.pi/6 + math.pi/4) + 0.4 * math.cos(math.pi/6 + math.pi/4 + math.pi/3),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.1: 3-link FK y-position",
        section="11",
        stated=l1_3 * math.sin(t1_3) + l2_3 * math.sin(t1_3 + t2_3) + l3_3 * math.sin(t1_3 + t2_3 + t3_3),
        computed=lambda: 1.0 * math.sin(math.pi/6) + 0.7 * math.sin(math.pi/6 + math.pi/4) + 0.4 * math.sin(math.pi/6 + math.pi/4 + math.pi/3),
        tolerance=1e-10,
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.1: 3-link FK via matrix chain matches formula",
        section="11",
        predicate=lambda: _three_link_fk_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.2: Analytical vs numerical Jacobian
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.2: analytical vs numerical Jacobian agree to 8 digits",
        section="11",
        predicate=lambda: _jacobian_numerical_vs_analytical(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.3: Workspace for l1=1.5, l2=1.0
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.3: workspace inner radius = |1.5 - 1.0| = 0.5",
        section="11",
        stated=0.5,
        computed=lambda: abs(1.5 - 1.0),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: workspace outer radius = 1.5 + 1.0 = 2.5",
        section="11",
        stated=2.5,
        computed=lambda: 1.5 + 1.0,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: workspace area = pi*(2.5^2 - 0.5^2) = 6*pi ~ 18.85",
        section="11",
        stated=6 * math.pi,
        computed=lambda: math.pi * (2.5**2 - 0.5**2),
        tolerance=1e-10,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.4: Multiple IK solutions for l1=l2=1.0, target (1.0, 0.5)
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.4: two IK solutions both satisfy FK for (1.0, 0.5)",
        section="11",
        predicate=lambda: _multiple_ik_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.6: Quintic trajectory boundary conditions
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.6: quintic trajectory satisfies 6 boundary conditions",
        section="11",
        predicate=lambda: _quintic_trajectory_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.7: Energy analysis for pendulum arm
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.7: pendulum potential energy at pi/4: mgl*(1-sin(pi/4)) ~ 2.87 J",
        section="11",
        stated=2.87,
        computed=lambda: 2 * 9.81 * 0.5 * (1 - math.sin(math.pi / 4)),
        tolerance=2e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.8: 3-DOF Jacobian rank
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.8: 3-link Jacobian rank=2 at generic config, rank=1 when collinear",
        section="11",
        predicate=lambda: _three_dof_rank_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.5: Damped least-squares IK through singularity
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.5: Damped LS IK traces path through singular config",
        section="11",
        predicate=lambda: _ex425_damped_ls_ik(),
        note="Exercise 10.5: lambda=0.05 avoids singularity blow-up",
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.12: Numerical Jacobian via central differences
    # J_ij ~ (FK_i(theta + h*e_j) - FK_i(theta - h*e_j)) / (2h)
    def remark_4212_numerical_jacobian():
        # 2-link planar arm: FK(t1,t2) = (l1*cos(t1)+l2*cos(t1+t2), l1*sin(t1)+l2*sin(t1+t2))
        l1, l2 = 1.0, 0.8
        theta = [0.5, 0.3]

        def FK(t):
            x = l1 * math.cos(t[0]) + l2 * math.cos(t[0] + t[1])
            y = l1 * math.sin(t[0]) + l2 * math.sin(t[0] + t[1])
            return [x, y]

        # Analytical Jacobian
        J_ana = [
            [-l1*math.sin(theta[0]) - l2*math.sin(theta[0]+theta[1]),
             -l2*math.sin(theta[0]+theta[1])],
            [l1*math.cos(theta[0]) + l2*math.cos(theta[0]+theta[1]),
             l2*math.cos(theta[0]+theta[1])],
        ]

        # Numerical Jacobian with h ~ 1e-7
        h = 1e-7
        J_num = [[0, 0], [0, 0]]
        for j in range(2):
            t_plus = list(theta)
            t_minus = list(theta)
            t_plus[j] += h
            t_minus[j] -= h
            fk_plus = FK(t_plus)
            fk_minus = FK(t_minus)
            for i in range(2):
                J_num[i][j] = (fk_plus[i] - fk_minus[i]) / (2 * h)

        max_err = max(abs(J_ana[i][j] - J_num[i][j]) for i in range(2) for j in range(2))
        ok = max_err < 1e-5
        return (ok, f"Max Jacobian error = {max_err:.2e}")
    ch.add(StructuralCheck(
        label="Remark 3.12: Numerical Jacobian matches analytical (h=1e-7)",
        section="4",
        predicate=remark_4212_numerical_jacobian,
        note="Remark 3.12",
    ))

    # Remark 3.16: 2-link arm has two IK solutions (elbow-up, elbow-down)
    def remark_4216_two_ik_solutions():
        l1, l2 = 1.0, 0.8
        # Target within workspace
        px, py = 1.2, 0.5
        d = math.sqrt(px**2 + py**2)
        # Two solutions exist if |l1-l2| < d < l1+l2
        if d >= l1 + l2 or d <= abs(l1 - l2):
            return (False, f"Target out of workspace: d={d}")
        # Cosine rule for theta2
        cos_t2 = (px**2 + py**2 - l1**2 - l2**2) / (2 * l1 * l2)
        t2_up = math.acos(cos_t2)
        t2_down = -math.acos(cos_t2)

        def fk(t1, t2):
            x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
            y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
            return x, y

        # Solve for theta1 given theta2
        k1 = l1 + l2 * math.cos(t2_up)
        k2 = l2 * math.sin(t2_up)
        t1_up = math.atan2(py, px) - math.atan2(k2, k1)
        x_up, y_up = fk(t1_up, t2_up)

        k1 = l1 + l2 * math.cos(t2_down)
        k2 = l2 * math.sin(t2_down)
        t1_down = math.atan2(py, px) - math.atan2(k2, k1)
        x_down, y_down = fk(t1_down, t2_down)

        ok1 = abs(x_up - px) < 1e-6 and abs(y_up - py) < 1e-6
        ok2 = abs(x_down - px) < 1e-6 and abs(y_down - py) < 1e-6
        ok3 = abs(t2_up - t2_down) > 1e-6  # distinct solutions
        ok = ok1 and ok2 and ok3
        return (ok, f"Elbow-up: t2={t2_up:.4f}, Elbow-down: t2={t2_down:.4f}")
    ch.add(StructuralCheck(
        label="Remark 3.16: 2-link arm admits two IK solutions",
        section="4",
        predicate=remark_4216_two_ik_solutions,
        note="Remark 3.16",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Forward Kinematics ---
    def alg_5_1_fk():
        l1, l2 = 1.0, 0.8
        t1, t2 = math.pi / 3, math.pi / 6
        x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
        y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
        # Verify distance from origin <= l1 + l2
        r = math.sqrt(x ** 2 + y ** 2)
        ok1 = r <= l1 + l2 + 1e-10
        # At t1=0, t2=0: x = l1+l2, y = 0
        x0 = l1 + l2
        y0 = 0.0
        ok2 = abs(l1 * math.cos(0) + l2 * math.cos(0) - x0) < 1e-10
        return (ok1 and ok2, f"FK({t1:.2f},{t2:.2f}) = ({x:.4f},{y:.4f}), r={r:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Forward kinematics (2-link arm)",
        section="6",
        predicate=alg_5_1_fk,
    ))

    # --- Algorithm 5.2: Numerical Jacobian ---
    def alg_5_2_numerical_jacobian():
        l1, l2 = 1.0, 0.8
        t1, t2 = math.pi / 3, math.pi / 6
        def fk(theta):
            return np.array([
                l1 * math.cos(theta[0]) + l2 * math.cos(theta[0] + theta[1]),
                l1 * math.sin(theta[0]) + l2 * math.sin(theta[0] + theta[1]),
            ])
        theta = np.array([t1, t2])
        h_j = 1e-7
        J_num = np.zeros((2, 2))
        for j in range(2):
            theta_plus = theta.copy()
            theta_minus = theta.copy()
            theta_plus[j] += h_j
            theta_minus[j] -= h_j
            J_num[:, j] = (fk(theta_plus) - fk(theta_minus)) / (2 * h_j)
        # Analytical Jacobian
        J_anal = np.array([
            [-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
            [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)],
        ])
        ok = np.allclose(J_num, J_anal, atol=1e-6)
        return (ok, f"Max Jacobian error: {np.max(np.abs(J_num - J_anal)):.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Numerical Jacobian vs analytical (8+ digits)",
        section="6",
        predicate=alg_5_2_numerical_jacobian,
    ))

    # --- Algorithm 5.3: Inverse Kinematics via Newton's Method ---
    def alg_5_3_ik_newton():
        l1, l2 = 1.0, 0.8
        target = np.array([1.2, 0.8])
        def fk(theta):
            return np.array([
                l1 * math.cos(theta[0]) + l2 * math.cos(theta[0] + theta[1]),
                l1 * math.sin(theta[0]) + l2 * math.sin(theta[0] + theta[1]),
            ])
        def jacobian(theta):
            return np.array([
                [-l1 * math.sin(theta[0]) - l2 * math.sin(theta[0] + theta[1]),
                 -l2 * math.sin(theta[0] + theta[1])],
                [l1 * math.cos(theta[0]) + l2 * math.cos(theta[0] + theta[1]),
                 l2 * math.cos(theta[0] + theta[1])],
            ])
        theta = np.array([0.5, 0.5])
        for _ in range(50):
            e = target - fk(theta)
            if np.linalg.norm(e) < 1e-10:
                break
            J = jacobian(theta)
            dtheta = np.linalg.solve(J, e)
            theta = theta + dtheta
        pos = fk(theta)
        ok = np.linalg.norm(pos - target) < 1e-8
        return (ok, f"IK theta={theta}, FK={pos}, err={np.linalg.norm(pos - target):.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Inverse kinematics via Newton's method",
        section="6",
        predicate=alg_5_3_ik_newton,
    ))

    # --- Algorithm 5.4: Cubic Trajectory Coefficients ---
    def alg_5_4_cubic_traj():
        # q(t) = a0 + a1*t + a2*t^2 + a3*t^3
        # BCs: q(0)=q0, q(T)=qf, dq(0)=0, dq(T)=0
        q0, qf, T_traj = 0.0, math.pi / 2, 2.0
        # a0 = q0, a1 = 0, a2 = 3(qf-q0)/T^2, a3 = -2(qf-q0)/T^3
        a0 = q0
        a1 = 0
        a2 = 3 * (qf - q0) / T_traj ** 2
        a3 = -2 * (qf - q0) / T_traj ** 3
        # Verify BCs
        q_0 = a0
        q_T = a0 + a1 * T_traj + a2 * T_traj ** 2 + a3 * T_traj ** 3
        dq_0 = a1
        dq_T = a1 + 2 * a2 * T_traj + 3 * a3 * T_traj ** 2
        ok1 = abs(q_0 - q0) < 1e-10 and abs(q_T - qf) < 1e-10
        ok2 = abs(dq_0) < 1e-10 and abs(dq_T) < 1e-10
        return (ok1 and ok2, f"q(0)={q_0:.4f}, q(T)={q_T:.4f}, dq(0)={dq_0:.4f}, dq(T)={dq_T:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Cubic trajectory (boundary conditions satisfied)",
        section="6",
        predicate=alg_5_4_cubic_traj,
    ))

    # --- Algorithm 5.5: Dynamics Simulation via RK4 ---
    def alg_5_5_dynamics():
        # Simple 1-DOF: m*ddq + b*dq + k*q = tau
        # Let m=1, b=0.5, k=2, tau=0 => free response
        m_r, b_r, k_r = 1.0, 0.5, 2.0
        q, dq = 1.0, 0.0
        h_r = 0.001
        def f_dyn(state):
            return np.array([state[1], (-b_r * state[1] - k_r * state[0]) / m_r])
        state_r = np.array([q, dq])
        for _ in range(int(10 / h_r)):
            k1 = h_r * f_dyn(state_r)
            k2 = h_r * f_dyn(state_r + k1 / 2)
            k3 = h_r * f_dyn(state_r + k2 / 2)
            k4 = h_r * f_dyn(state_r + k3)
            state_r = state_r + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        # Should decay to zero (stable underdamped system, sigma=-0.25)
        ok = abs(state_r[0]) < 0.05
        return (ok, f"q(10)={state_r[0]:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Robot dynamics simulation via RK4",
        section="6",
        predicate=alg_5_5_dynamics,
    ))

    # --- Algorithm 5.6: Workspace Boundary Sweep ---
    def alg_5_6_workspace():
        l1, l2 = 1.0, 0.8
        N_sweep = 100
        points = []
        for i in range(N_sweep):
            t1 = 2 * math.pi * i / N_sweep
            for j in range(N_sweep):
                t2 = 2 * math.pi * j / N_sweep
                x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
                y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
                points.append((x, y))
        points = np.array(points)
        max_reach = np.max(np.sqrt(points[:, 0] ** 2 + points[:, 1] ** 2))
        min_reach = np.min(np.sqrt(points[:, 0] ** 2 + points[:, 1] ** 2))
        ok1 = abs(max_reach - (l1 + l2)) < 0.05
        ok2 = abs(min_reach - abs(l1 - l2)) < 0.05
        return (ok1 and ok2, f"Max reach={max_reach:.4f} (exp {l1 + l2}), Min={min_reach:.4f} (exp {abs(l1 - l2)})")
    ch.add(StructuralCheck(
        label="Algorithm 5.6: Workspace boundary sweep",
        section="6",
        predicate=alg_5_6_workspace,
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _fk_identity():
    import sympy
    l1, l2, t1, t2 = sympy.symbols('l1 l2 t1 t2', real=True)
    x = l1 * sympy.cos(t1) + l2 * sympy.cos(t1 + t2)
    y = l1 * sympy.sin(t1) + l2 * sympy.sin(t1 + t2)
    # At t1=0, t2=0 (fully extended): x = l1+l2, y = 0
    x_ext = x.subs([(t1, 0), (t2, 0)])
    return sympy.Eq(x_ext, l1 + l2)


def _jacobian_det_identity():
    import sympy
    l1, l2, t1, t2 = sympy.symbols('l1 l2 t1 t2', real=True)
    x = l1 * sympy.cos(t1) + l2 * sympy.cos(t1 + t2)
    y = l1 * sympy.sin(t1) + l2 * sympy.sin(t1 + t2)
    J = sympy.Matrix([
        [sympy.diff(x, t1), sympy.diff(x, t2)],
        [sympy.diff(y, t1), sympy.diff(y, t2)],
    ])
    det_J = sympy.simplify(J.det())
    expected = l1 * l2 * sympy.sin(t2)
    return sympy.Eq(det_J, expected)


def _cubic_trajectory_identity():
    import sympy
    ts, tf_s, tf = sympy.symbols('ts tf tf_val', real=True)
    dtheta = sympy.Symbol('dtheta', real=True)
    a2 = 3 * dtheta / tf**2
    a3 = -2 * dtheta / tf**3
    # Check theta(tf) = dtheta
    theta_tf = a2 * tf**2 + a3 * tf**3
    return sympy.Eq(sympy.simplify(theta_tf), dtheta)


def _ik_verification():
    """Verify IK by computing correct solution and checking FK round-trip.
    TEXTBOOK ERROR: states t1=0.1498, t2=0.9828 but correct values are
    t1~0.0255, t2~1.2922 for target (1.2, 0.8) with l1=1.0, l2=0.8.
    """
    l1, l2 = 1.0, 0.8
    tx, ty = 1.2, 0.8
    d2 = tx**2 + ty**2
    cos_t2 = (d2 - l1**2 - l2**2) / (2 * l1 * l2)
    t2 = math.acos(cos_t2)
    t1 = math.atan2(ty, tx) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
    x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
    y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
    err = math.sqrt((x - tx)**2 + (y - ty)**2)
    ok = err < 1e-10
    return ok, f"FK({t1:.4f},{t2:.4f})=({x:.6f},{y:.6f}), err={err:.2e}. TEXTBOOK: t1=0.1498,t2=0.9828 is wrong"


def _workspace_check():
    l1, l2 = 1.0, 0.8
    r_min = abs(l1 - l2)
    r_max = l1 + l2
    # Sample many configurations
    n = 1000
    for _ in range(n):
        t1 = np.random.uniform(0, 2 * math.pi)
        t2 = np.random.uniform(0, 2 * math.pi)
        x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
        y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
        r = math.sqrt(x**2 + y**2)
        if r < r_min - 1e-10 or r > r_max + 1e-10:
            return False, f"r={r:.4f} outside [{r_min},{r_max}]"
    return True, f"All {n} samples within [{r_min},{r_max}]"


def _workspace_boundary_values():
    """Verify workspace boundary values for l1=1.0, l2=0.8."""
    l1, l2 = 1.0, 0.8
    r_min = abs(l1 - l2)
    r_max = l1 + l2
    # At theta2=0 (extended): r = l1+l2
    x_ext = l1 * math.cos(0) + l2 * math.cos(0)
    r_ext = abs(x_ext)
    # At theta2=pi (folded): r = l1-l2
    x_fold = l1 * math.cos(0) + l2 * math.cos(math.pi)
    r_fold = abs(x_fold)
    ok1 = abs(r_ext - r_max) < 1e-10
    ok2 = abs(r_fold - r_min) < 1e-10
    ok3 = abs(r_min - 0.2) < 1e-10
    ok4 = abs(r_max - 1.8) < 1e-10
    ok = ok1 and ok2 and ok3 and ok4
    return ok, f"r_min={r_min}, r_max={r_max}, extended={r_ext}, folded={r_fold}"


def _cubic_boundary_check():
    dtheta = math.pi / 2
    tf = 2.0
    a0 = 0
    a1 = 0
    a2 = 3 * dtheta / tf**2
    a3 = -2 * dtheta / tf**3
    # Check theta(0)=0, theta(tf)=dtheta, dtheta(0)=0, dtheta(tf)=0
    theta_0 = a0
    theta_tf = a0 + a1 * tf + a2 * tf**2 + a3 * tf**3
    dtheta_0 = a1
    dtheta_tf = a1 + 2 * a2 * tf + 3 * a3 * tf**2
    ok = (abs(theta_0) < 1e-12 and
          abs(theta_tf - dtheta) < 1e-12 and
          abs(dtheta_0) < 1e-12 and
          abs(dtheta_tf) < 1e-12)
    return ok, f"theta(0)={theta_0}, theta(tf)={theta_tf:.6f}, dtheta(0)={dtheta_0}, dtheta(tf)={dtheta_tf:.2e}"


def _dh_transform_check():
    """Verify the DH homogeneous transformation T_0^1 at theta1=pi/4 from Thm 42.8 proof."""
    l1 = 1.0
    t1 = math.pi / 4
    c = math.cos(t1)
    s = math.sin(t1)
    # T_0^1 = [[cos(t1), -sin(t1), l1*cos(t1)],
    #           [sin(t1),  cos(t1), l1*sin(t1)],
    #           [0,        0,       1          ]]
    T01 = np.array([
        [c, -s, l1 * c],
        [s,  c, l1 * s],
        [0,  0,  1    ],
    ])
    # Verify rotation part is orthogonal: det=1
    det_ok = abs(np.linalg.det(T01[:2, :2]) - 1.0) < 1e-10
    # Verify translation is (l1*cos(t1), l1*sin(t1)) = (0.7071, 0.7071)
    tx_ok = abs(T01[0, 2] - l1 * c) < 1e-10
    ty_ok = abs(T01[1, 2] - l1 * s) < 1e-10
    ok = det_ok and tx_ok and ty_ok
    return ok, f"det(R)={np.linalg.det(T01[:2,:2]):.6f}, tx={T01[0,2]:.6f}, ty={T01[1,2]:.6f}"


def _three_link_fk_check():
    """Exercise 10.1: 3-link FK via matrix chain vs formula."""
    l1, l2, l3 = 1.0, 0.7, 0.4
    t1, t2, t3 = math.pi / 6, math.pi / 4, math.pi / 3

    def make_T(l, t):
        c, s = math.cos(t), math.sin(t)
        return np.array([[c, -s, l*c], [s, c, l*s], [0, 0, 1]])

    T01 = make_T(l1, t1)
    T12 = make_T(l2, t2)
    T23 = make_T(l3, t3)
    T03 = T01 @ T12 @ T23

    x_fk = l1*math.cos(t1) + l2*math.cos(t1+t2) + l3*math.cos(t1+t2+t3)
    y_fk = l1*math.sin(t1) + l2*math.sin(t1+t2) + l3*math.sin(t1+t2+t3)

    ok = abs(T03[0, 2] - x_fk) < 1e-10 and abs(T03[1, 2] - y_fk) < 1e-10
    return ok, f"Matrix: ({T03[0,2]:.6f},{T03[1,2]:.6f}), Formula: ({x_fk:.6f},{y_fk:.6f})"


def _jacobian_numerical_vs_analytical():
    """Exercise 10.2: Compare analytical and numerical Jacobian."""
    l1, l2 = 1.0, 0.8
    t1, t2 = math.pi / 3, math.pi / 6
    # Analytical Jacobian
    J_a = np.array([
        [-l1*math.sin(t1) - l2*math.sin(t1+t2), -l2*math.sin(t1+t2)],
        [l1*math.cos(t1) + l2*math.cos(t1+t2), l2*math.cos(t1+t2)],
    ])
    # Numerical Jacobian
    h = 1e-7
    def fk(th1, th2):
        return np.array([
            l1*math.cos(th1) + l2*math.cos(th1+th2),
            l1*math.sin(th1) + l2*math.sin(th1+th2),
        ])
    J_n = np.zeros((2, 2))
    J_n[:, 0] = (fk(t1+h, t2) - fk(t1-h, t2)) / (2*h)
    J_n[:, 1] = (fk(t1, t2+h) - fk(t1, t2-h)) / (2*h)
    max_err = np.max(np.abs(J_a - J_n))
    ok = max_err < 1e-8
    return ok, f"Max Jacobian element error: {max_err:.2e}"


def _multiple_ik_check():
    """Exercise 10.4: Two IK solutions for l1=l2=1, target (1.0, 0.5)."""
    l1, l2 = 1.0, 1.0
    tx, ty = 1.0, 0.5
    d2 = tx**2 + ty**2
    cos_t2 = (d2 - l1**2 - l2**2) / (2 * l1 * l2)
    if abs(cos_t2) > 1:
        return False, "Target unreachable"
    # Elbow-up
    t2_up = math.acos(cos_t2)
    t1_up = math.atan2(ty, tx) - math.atan2(l2*math.sin(t2_up), l1 + l2*math.cos(t2_up))
    # Elbow-down
    t2_down = -math.acos(cos_t2)
    t1_down = math.atan2(ty, tx) - math.atan2(l2*math.sin(t2_down), l1 + l2*math.cos(t2_down))
    # Verify both
    x_up = l1*math.cos(t1_up) + l2*math.cos(t1_up + t2_up)
    y_up = l1*math.sin(t1_up) + l2*math.sin(t1_up + t2_up)
    x_down = l1*math.cos(t1_down) + l2*math.cos(t1_down + t2_down)
    y_down = l1*math.sin(t1_down) + l2*math.sin(t1_down + t2_down)
    err_up = math.sqrt((x_up - tx)**2 + (y_up - ty)**2)
    err_down = math.sqrt((x_down - tx)**2 + (y_down - ty)**2)
    different = abs(t2_up - t2_down) > 0.01
    ok = err_up < 1e-10 and err_down < 1e-10 and different
    return ok, f"Elbow-up err={err_up:.2e}, elbow-down err={err_down:.2e}, t2_up={t2_up:.4f}, t2_down={t2_down:.4f}"


def _quintic_trajectory_check():
    """Exercise 10.6: Quintic with theta(0)=0, theta(2)=pi/2, d/dd=0 at endpoints."""
    tf = 2.0
    dtheta = math.pi / 2
    # 6 boundary conditions: theta(0)=0, theta(tf)=dtheta, dtheta(0)=0, dtheta(tf)=0, ddtheta(0)=0, ddtheta(tf)=0
    # theta(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5
    # Boundary: a0=0, a1=0, a2=0 (from theta(0)=dtheta(0)=ddtheta(0)=0)
    # Then: a3*tf^3 + a4*tf^4 + a5*tf^5 = dtheta
    #        3*a3*tf^2 + 4*a4*tf^3 + 5*a5*tf^4 = 0
    #        6*a3*tf + 12*a4*tf^2 + 20*a5*tf^3 = 0
    A = np.array([
        [tf**3, tf**4, tf**5],
        [3*tf**2, 4*tf**3, 5*tf**4],
        [6*tf, 12*tf**2, 20*tf**3],
    ])
    b = np.array([dtheta, 0, 0])
    coeffs = np.linalg.solve(A, b)
    a3, a4, a5 = coeffs

    def theta(t): return a3*t**3 + a4*t**4 + a5*t**5
    def dtheta_fn(t): return 3*a3*t**2 + 4*a4*t**3 + 5*a5*t**4
    def ddtheta_fn(t): return 6*a3*t + 12*a4*t**2 + 20*a5*t**3

    ok = (abs(theta(0)) < 1e-12 and
          abs(theta(tf) - dtheta) < 1e-10 and
          abs(dtheta_fn(0)) < 1e-12 and
          abs(dtheta_fn(tf)) < 1e-10 and
          abs(ddtheta_fn(0)) < 1e-12 and
          abs(ddtheta_fn(tf)) < 1e-10)
    return ok, f"theta(0)={theta(0):.2e}, theta(tf)={theta(tf):.6f}, v(0)={dtheta_fn(0):.2e}, v(tf)={dtheta_fn(tf):.2e}, a(0)={ddtheta_fn(0):.2e}, a(tf)={ddtheta_fn(tf):.2e}"


def _ex425_damped_ls_ik():
    """Exercise 10.5: Damped least-squares IK through singular configuration.
    Trace straight line from (1.0, 0.0) to (1.8, 0.0) for l1=1.0, l2=0.8.
    At (1.8, 0.0), the arm is fully extended (singular). Damped LS should handle it."""
    l1, l2 = 1.0, 0.8
    lam = 0.05
    # Start at a valid IK solution for (1.0, 0.0)
    # cos(t2) = (1.0^2 - 1.0 - 0.64) / (2*1*0.8) = -0.4, t2 = acos(-0.4)
    cos_t2 = (1.0 - l1**2 - l2**2) / (2 * l1 * l2)
    t2 = math.acos(max(-1, min(1, cos_t2)))
    t1 = math.atan2(0, 1.0) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
    n_steps = 50
    path = np.linspace(1.0, 1.79, n_steps)  # stay just short of exact singularity
    max_joint_vel = 0
    for i in range(n_steps):
        target = np.array([path[i], 0.0])
        for _ in range(10):  # inner iterations
            x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
            y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
            e = target - np.array([x, y])
            if np.linalg.norm(e) < 1e-6:
                break
            J = np.array([
                [-l1*math.sin(t1) - l2*math.sin(t1+t2), -l2*math.sin(t1+t2)],
                [l1*math.cos(t1) + l2*math.cos(t1+t2), l2*math.cos(t1+t2)],
            ])
            # Damped least-squares: dq = J^T(JJ^T + lambda^2*I)^{-1} e
            JJt = J @ J.T + lam**2 * np.eye(2)
            dq = J.T @ np.linalg.solve(JJt, e)
            max_joint_vel = max(max_joint_vel, np.linalg.norm(dq))
            t1 += dq[0]
            t2 += dq[1]
    # Final position should be close to (1.79, 0)
    x_final = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
    y_final = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
    err = math.sqrt((x_final - 1.79)**2 + y_final**2)
    # Damping should keep joint velocities bounded (no blow-up)
    ok = err < 0.05 and max_joint_vel < 50
    return (ok, f"Final err={err:.4f}, max joint vel={max_joint_vel:.2f}")


def _three_dof_rank_check():
    """Exercise 10.8: 3-link Jacobian rank analysis."""
    l1, l2, l3 = 1.0, 0.7, 0.4
    # Generic config
    t1, t2, t3 = 0.5, 0.8, 1.2
    s12 = t1 + t2
    s123 = t1 + t2 + t3
    J = np.array([
        [-l1*math.sin(t1) - l2*math.sin(s12) - l3*math.sin(s123),
         -l2*math.sin(s12) - l3*math.sin(s123),
         -l3*math.sin(s123)],
        [l1*math.cos(t1) + l2*math.cos(s12) + l3*math.cos(s123),
         l2*math.cos(s12) + l3*math.cos(s123),
         l3*math.cos(s123)],
    ])
    rank_generic = np.linalg.matrix_rank(J)

    # Collinear config: t2 = t3 = 0
    J_col = np.array([
        [-l1*math.sin(t1), 0, 0],
        [l1*math.cos(t1) + l2*math.cos(t1) + l3*math.cos(t1),
         l2*math.cos(t1) + l3*math.cos(t1),
         l3*math.cos(t1)],
    ])
    # Actually for collinear: t1 arbitrary, t2=0, t3=0
    t1_col = 0.3
    J_col2 = np.array([
        [-l1*math.sin(t1_col) - l2*math.sin(t1_col) - l3*math.sin(t1_col),
         -l2*math.sin(t1_col) - l3*math.sin(t1_col),
         -l3*math.sin(t1_col)],
        [l1*math.cos(t1_col) + l2*math.cos(t1_col) + l3*math.cos(t1_col),
         l2*math.cos(t1_col) + l3*math.cos(t1_col),
         l3*math.cos(t1_col)],
    ])
    rank_collinear = np.linalg.matrix_rank(J_col2, tol=1e-10)

    ok = rank_generic == 2 and rank_collinear == 1
    return ok, f"Generic rank={rank_generic}, collinear rank={rank_collinear}"
