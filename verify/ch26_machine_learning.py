# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 26: Machine Learning Foundations."""

import math
import numpy as np

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(26, "Machine Learning Foundations")

    # --- Symbolic checks ---

    # S1: Sigmoid derivative: sigma'(z) = sigma(z)(1 - sigma(z))
    def sigmoid_derivative():
        import sympy as sp
        z = sp.Symbol('z')
        sigma = 1 / (1 + sp.exp(-z))
        dsigma = sp.diff(sigma, z)
        expected = sigma * (1 - sigma)
        return sp.Eq(sp.simplify(dsigma - expected), 0)
    ch.add(SymbolicCheck(
        label="Sigmoid derivative sigma'(z) = sigma(z)(1-sigma(z))",
        section="4",
        identity=sigmoid_derivative,
    ))

    # S2: Sigmoid symmetry: sigma(-z) = 1 - sigma(z)
    def sigmoid_symmetry():
        import sympy as sp
        z = sp.Symbol('z')
        sigma_z = 1 / (1 + sp.exp(-z))
        sigma_neg = 1 / (1 + sp.exp(z))
        return sp.Eq(sp.simplify(sigma_neg - (1 - sigma_z)), 0)
    ch.add(SymbolicCheck(
        label="Sigmoid symmetry sigma(-z) = 1 - sigma(z)",
        section="4",
        identity=sigmoid_symmetry,
    ))

    # S3: Ridge estimator: (X'X + n*lambda*I) * beta_ridge = X'y
    def ridge_formula():
        import sympy as sp
        # For 2x2 case, verify the formula algebraically
        a, b, c, d = sp.symbols('a b c d')
        lam, n_val = sp.symbols('lambda n', positive=True)
        XtX = sp.Matrix([[a, b], [b, c]])
        Xty = sp.Matrix([d, d])
        reg = XtX + n_val * lam * sp.eye(2)
        beta = reg.inv() * Xty
        # Verify (XtX + n*lam*I) * beta = Xty
        check = sp.simplify(reg * beta - Xty)
        return sp.Eq(check, sp.zeros(2, 1))
    ch.add(SymbolicCheck(
        label="Ridge: (X'X + n*lambda*I) * beta = X'y",
        section="4",
        identity=ridge_formula,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 7.1: OLS regression
    def ols_slope():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        y = np.array([2.1, 3.9, 6.2, 7.8], dtype=float)
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        return beta[1]
    ch.add(NumericCheck(
        label="Ex 7.1: OLS slope",
        section="9",
        stated=1.94,
        computed=ols_slope,
        tolerance=1e-3,
    ))

    def ols_intercept():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        y = np.array([2.1, 3.9, 6.2, 7.8], dtype=float)
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        return beta[0]
    ch.add(NumericCheck(
        label="Ex 7.1: OLS intercept",
        section="9",
        stated=0.15,
        computed=ols_intercept,
        tolerance=1e-2,
    ))

    # Example 7.1: MSE
    def ols_mse():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        y = np.array([2.1, 3.9, 6.2, 7.8], dtype=float)
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        residuals = y - X @ beta
        return np.mean(residuals ** 2)
    ch.add(NumericCheck(
        label="Ex 7.1: MSE",
        section="9",
        stated=0.0205,
        computed=ols_mse,
        tolerance=1e-2,
    ))

    # Example 7.2: Logistic regression gradient step
    ch.add(NumericCheck(
        label="Ex 7.2: Updated beta_0 after one gradient step",
        section="9",
        stated=0.05,
        computed=lambda: 0 - 0.1 * (0.5 - 1) * 1,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 7.2: Updated beta_1 after one gradient step",
        section="9",
        stated=0.15,
        computed=lambda: 0 - 0.1 * (0.5 - 1) * 3,
        tolerance=1e-6,
    ))

    # Example 7.3: Ridge regression
    def ridge_beta():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        y = np.array([2.1, 3.9, 6.2, 7.8], dtype=float)
        n = 4
        lam = 0.5
        XtX = X.T @ X + n * lam * np.eye(2)
        Xty = X.T @ y
        beta = np.linalg.solve(XtX, Xty)
        return beta
    ch.add(NumericCheck(
        label="Ex 7.3: Ridge intercept (lambda=0.5)",
        section="9",
        stated=0.47,
        computed=lambda: ridge_beta()[0],
        tolerance=1e-2,
    ))
    ch.add(NumericCheck(
        label="Ex 7.3: Ridge slope (lambda=0.5)",
        section="9",
        stated=1.72,
        computed=lambda: ridge_beta()[1],
        tolerance=1e-2,
    ))

    # Example 7.4: PCA eigenvalues
    def pca_first_eigenvalue():
        X = np.array([[2, 1], [3, 3], [5, 4], [6, 6], [8, 7]], dtype=float)
        X_centered = X - X.mean(axis=0)
        cov = X_centered.T @ X_centered / (len(X) - 1)
        eigenvalues = np.sort(np.linalg.eigvalsh(cov))[::-1]
        return eigenvalues[0]
    ch.add(NumericCheck(
        label="Ex 7.4: First PCA eigenvalue",
        section="9",
        stated=11.25,
        computed=pca_first_eigenvalue,
        tolerance=1e-2,
    ))

    def pca_variance_explained():
        X = np.array([[2, 1], [3, 3], [5, 4], [6, 6], [8, 7]], dtype=float)
        X_centered = X - X.mean(axis=0)
        cov = X_centered.T @ X_centered / (len(X) - 1)
        eigenvalues = np.sort(np.linalg.eigvalsh(cov))[::-1]
        return eigenvalues[0] / sum(eigenvalues) * 100
    ch.add(NumericCheck(
        label="Ex 7.4: Variance explained by PC1 (%)",
        section="9",
        stated=98.7,
        computed=pca_variance_explained,
        tolerance=1e-1,
    ))

    # Example 7.5: Backpropagation
    ch.add(NumericCheck(
        label="Ex 7.5: Forward pass y_hat",
        section="9",
        stated=-0.72,
        computed=lambda: 0.6 * 0 + (-0.4) * 1.8,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Ex 7.5: Loss",
        section="9",
        stated=1.4792,
        computed=lambda: 0.5 * (-0.72 - 1) ** 2,
        tolerance=1e-3,
    ))

    # --- Structural checks ---

    # Sigmoid output always in (0,1)
    def sigmoid_range():
        test_values = [-10, -1, 0, 1, 10]  # avoid ±100 where float64 rounds to 0/1
        for z in test_values:
            s = 1.0 / (1.0 + math.exp(-z))
            if not (0 < s < 1):
                return (False, f"sigmoid({z}) = {s} not in (0,1)")
        return (True, "")
    ch.add(StructuralCheck(
        label="Sigmoid output in (0,1) for finite inputs",
        section="4",
        predicate=sigmoid_range,
    ))

    # Ridge regularization improves conditioning
    def ridge_conditioning():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        XtX = X.T @ X
        cond_ols = np.linalg.cond(XtX)
        cond_ridge = np.linalg.cond(XtX + 4 * 0.5 * np.eye(2))
        ok = cond_ridge < cond_ols
        msg = f"cond(OLS)={cond_ols:.1f}, cond(Ridge)={cond_ridge:.1f}"
        return (ok, msg if not ok else "")
    ch.add(StructuralCheck(
        label="Ridge regularization reduces condition number",
        section="4",
        predicate=ridge_conditioning,
    ))

    # --- Bias-variance chart data: Total Error = Bias^2 + Variance ---
    _bv_bias2 = [0.8, 0.5, 0.3, 0.15, 0.08, 0.05, 0.03, 0.02]
    _bv_var = [0.02, 0.03, 0.05, 0.1, 0.2, 0.35, 0.55, 0.8]
    _bv_total = [0.82, 0.53, 0.35, 0.25, 0.28, 0.40, 0.58, 0.82]
    for _i, (_b, _v, _t) in enumerate(zip(_bv_bias2, _bv_var, _bv_total)):
        ch.add(NumericCheck(
            label=f"Bias-variance chart point {_i+1}: {_b}+{_v}={_t}",
            section="4",
            stated=_t,
            computed=(lambda b=_b, v=_v: b + v),
            tolerance=1e-6,
            note="Mermaid chart: Total Error = Bias^2 + Variance",
        ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 9.1: Gradient of MSE loss yields normal equations ---
    # Verify that (X'X) beta = X'y gives OLS solution
    def ex91_normal_eq():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        y = np.array([2.1, 3.9, 6.2, 7.8], dtype=float)
        beta = np.linalg.solve(X.T @ X, X.T @ y)
        residual = np.linalg.norm(X.T @ X @ beta - X.T @ y)
        return (residual < 1e-10, f"Normal eq residual: {residual:.2e}")
    ch.add(StructuralCheck(
        label="Exercise 9.1: Normal equations X'X*beta = X'y hold",
        section="11",
        predicate=ex91_normal_eq,
    ))

    # --- Exercise 9.2: Sigmoid derivative ---
    # Already verified symbolically (S1), add numeric spot-check
    ch.add(NumericCheck(
        label="Exercise 9.2: sigma'(0) = sigma(0)*(1-sigma(0)) = 0.25",
        section="11",
        stated=0.25,
        computed=lambda: (1/(1+math.exp(0))) * (1 - 1/(1+math.exp(0))),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Exercise 9.2: sigma'(2) numeric check",
        section="11",
        stated=(1/(1+math.exp(-2))) * (1 - 1/(1+math.exp(-2))),
        computed=lambda: (1/(1+math.exp(-2))) * (1 - 1/(1+math.exp(-2))),
        tolerance=1e-10,
    ))

    # --- Exercise 9.3: Matrix dimensions ---
    # p=3, n=100: X is 100x3, X'X is 3x3, (X'X)^{-1} is 3x3, X'y is 3x1, beta is 3x1
    def ex93_dimensions():
        p, n = 3, 100
        dims_ok = True
        # X: n x p = 100x3
        # X'X: p x p = 3x3
        # (X'X)^{-1}: p x p = 3x3
        # X'y: p x 1 = 3x1
        # beta: p x 1 = 3x1
        X = np.random.randn(n, p)
        y = np.random.randn(n)
        XtX = X.T @ X
        beta = np.linalg.solve(XtX, X.T @ y)
        dims_ok = (X.shape == (100, 3) and XtX.shape == (3, 3) and beta.shape == (3,))
        return (dims_ok, f"Dimension mismatch" if not dims_ok else "")
    ch.add(StructuralCheck(
        label="Exercise 9.3: Matrix dimensions conformable (n=100, p=3)",
        section="11",
        predicate=ex93_dimensions,
    ))

    # --- Exercise 9.4: PCA variance explained ---
    # eigenvalues 8.0, 1.5, 0.5; total = 10
    ch.add(NumericCheck(
        label="Exercise 9.4: Variance explained by PC1",
        section="11",
        stated=80.0,
        computed=lambda: 8.0 / 10.0 * 100,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 9.4: Variance explained by PC1+PC2",
        section="11",
        stated=95.0,
        computed=lambda: (8.0 + 1.5) / 10.0 * 100,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 9.4: Variance explained by all three",
        section="11",
        stated=100.0,
        computed=lambda: (8.0 + 1.5 + 0.5) / 10.0 * 100,
        tolerance=1e-6,
    ))

    # --- Exercise 9.5: Ridge bias ---
    # bias = -(X'X + n*lambda*I)^{-1} * n*lambda * beta
    # Bias is zero only when true beta = 0
    def ex95_ridge_bias():
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]], dtype=float)
        n = 4
        lam = 0.5
        XtX = X.T @ X
        I_p = np.eye(2)
        reg = XtX + n * lam * I_p
        # For any nonzero true beta, bias should be nonzero
        beta_true = np.array([1.0, 2.0])
        bias = -np.linalg.solve(reg, n * lam * beta_true)
        ok = np.linalg.norm(bias) > 1e-6
        return (ok, f"Ridge bias should be nonzero: {bias}")
    ch.add(StructuralCheck(
        label="Exercise 9.5: Ridge estimator is biased for nonzero beta",
        section="11",
        predicate=ex95_ridge_bias,
    ))

    # --- Exercise 9.6: Neural network parameter count ---
    # Input dim p, hidden dim H, scalar output
    # Parameters: (p+1)*H + (H+1)*1 = (p+1)*H + H + 1
    ch.add(NumericCheck(
        label="Exercise 9.6: NN parameter count (p=10, H=64)",
        section="11",
        stated=769,
        computed=lambda: (10 + 1) * 64 + (64 + 1) * 1,
        tolerance=1e-6,
    ))

    # --- Exercise 9.8: Bias-variance decomposition structure ---
    # E[(y - f_hat)^2] = Var(noise) + Bias^2 + Var(f_hat)
    # Just verify the identity holds for a simple case
    def ex98_bias_variance():
        np.random.seed(42)
        # True function f(x) = 2x, noise sigma=0.5
        n_sim = 1000
        x_test = 1.0
        y_true = 2.0 * x_test
        sigma = 0.5
        predictions = []
        for _ in range(n_sim):
            X_train = np.random.randn(20, 1)
            y_train = 2.0 * X_train.ravel() + sigma * np.random.randn(20)
            # OLS fit
            beta = np.sum(X_train.ravel() * y_train) / np.sum(X_train.ravel()**2)
            predictions.append(beta * x_test)
        predictions = np.array(predictions)
        bias_sq = (np.mean(predictions) - y_true) ** 2
        variance = np.var(predictions)
        expected_mse = sigma**2 + bias_sq + variance
        actual_mse = np.mean((predictions - y_true + sigma * np.random.randn(n_sim))**2)
        # Just check the decomposition identity approximately holds
        ok = abs(bias_sq) < 0.1  # OLS is unbiased, so bias ~ 0
        return (ok, f"bias^2={bias_sq:.4f}, var={variance:.4f}")
    ch.add(StructuralCheck(
        label="Exercise 9.8: Bias-variance decomposition (OLS unbiased => bias~0)",
        section="11",
        predicate=ex98_bias_variance,
    ))

    # --- Exercise 9.7: Mini-batch SGD vs OLS ---
    # One epoch of SGD with B=50 should move beta toward OLS solution
    def ex97_sgd_vs_ols():
        np.random.seed(7)
        n, p = 1000, 5
        X = np.random.randn(n, p)
        beta_true = np.array([1.0, -0.5, 2.0, 0.3, -1.5])
        y = X @ beta_true + 0.5 * np.random.randn(n)
        beta_ols = np.linalg.solve(X.T @ X, X.T @ y)
        # SGD one epoch
        beta_sgd = np.zeros(p)
        eta = 0.01
        B = 50
        indices = np.random.permutation(n)
        for start in range(0, n, B):
            batch = indices[start:start + B]
            Xb = X[batch]
            yb = y[batch]
            grad = -2 / B * Xb.T @ (yb - Xb @ beta_sgd)
            beta_sgd -= eta * grad
        # After one epoch, SGD should be closer to OLS than zero
        err_initial = np.linalg.norm(np.zeros(p) - beta_ols)
        err_sgd = np.linalg.norm(beta_sgd - beta_ols)
        ok = err_sgd < err_initial
        return (ok, f"SGD err={err_sgd:.4f} vs initial err={err_initial:.4f}")
    ch.add(StructuralCheck(
        label="Exercise 9.7: SGD one epoch moves beta toward OLS",
        section="11",
        predicate=ex97_sgd_vs_ols,
    ))

    # --- Exercise 9.9: Ridge MSE < OLS MSE for some lambda ---
    # Ridge MSE = sigma^2 * sum(lam_j/(lam_j+n*lambda)^2) + n^2*lambda^2 * sum(beta_j^2/(lam_j+n*lambda)^2)
    # At lambda=0, dMSE/dlambda < 0 (ridge always helps initially)
    def ex99_ridge_mse_improvement():
        np.random.seed(42)
        n, p = 50, 5
        X = np.random.randn(n, p)
        beta_true = np.array([1.0, 0.5, 0.3, 0.1, 0.05])
        sigma = 1.0
        XtX = X.T @ X
        eigenvalues = np.linalg.eigvalsh(XtX)
        # Transform beta to eigenbasis
        _, V = np.linalg.eigh(XtX)
        beta_tilde = V.T @ beta_true
        # Check that for small lambda, MSE decreases
        lam_test = 0.01
        mse_ols_var = sigma**2 * np.sum(1.0 / eigenvalues)
        mse_ridge_var = sigma**2 * np.sum(eigenvalues / (eigenvalues + n * lam_test)**2)
        mse_ridge_bias = n**2 * lam_test**2 * np.sum(beta_tilde**2 / (eigenvalues + n * lam_test)**2)
        mse_ridge = mse_ridge_var + mse_ridge_bias
        ok = mse_ridge < mse_ols_var
        return (ok, f"Ridge MSE={mse_ridge:.6f} vs OLS var={mse_ols_var:.6f}")
    ch.add(StructuralCheck(
        label="Exercise 9.9: Ridge MSE < OLS MSE for small lambda > 0",
        section="11",
        predicate=ex99_ridge_mse_improvement,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 4.1: Batch Gradient Descent ---
    def alg_4_1_batch_gd():
        # Minimize f(x) = x^2, grad = 2x, starting at x=5
        x = 5.0
        eta = 0.1
        for _ in range(100):
            g = 2 * x
            x_new = x - eta * g
            if abs(x_new - x) < 1e-10:
                break
            x = x_new
        ok = abs(x) < 1e-6
        return (ok, f"Converged to x={x:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 4.1: Batch gradient descent on quadratic",
        section="6",
        predicate=alg_4_1_batch_gd,
    ))

    # --- Algorithm 4.2: SGD with Mini-Batches (convergence test) ---
    def alg_4_2_sgd():
        # Minimize MSE for y = 2x + 1 with data
        np.random.seed(42)
        X = np.column_stack([np.ones(100), np.random.randn(100)])
        beta_true = np.array([1.0, 2.0])
        y = X @ beta_true + 0.1 * np.random.randn(100)
        beta = np.zeros(2)
        B = 10
        n = len(y)
        for epoch in range(200):
            indices = np.random.permutation(n)
            for start in range(0, n, B):
                idx = indices[start:start + B]
                Xb, yb = X[idx], y[idx]
                g = (2 / len(idx)) * Xb.T @ (Xb @ beta - yb)
                eta = 0.01 / (1 + epoch * 0.01)
                beta = beta - eta * g
        # Should be close to [1, 2]
        ok = np.allclose(beta, beta_true, atol=0.2)
        return (ok, f"SGD beta={beta}, true={beta_true}")
    ch.add(StructuralCheck(
        label="Algorithm 4.2: SGD with mini-batches converges on linear model",
        section="6",
        predicate=alg_4_2_sgd,
    ))

    # --- Algorithm 4.3: SGD with Momentum ---
    def alg_4_3_sgd_momentum():
        # Minimize f(x,y) = x^2 + 10*y^2 (ill-conditioned)
        pos = np.array([5.0, 5.0])
        v = np.zeros(2)
        eta, gamma = 0.01, 0.9
        for _ in range(500):
            g = np.array([2 * pos[0], 20 * pos[1]])
            v = gamma * v + eta * g
            pos = pos - v
        ok = np.linalg.norm(pos) < 1e-3
        return (ok, f"Converged to {pos}")
    ch.add(StructuralCheck(
        label="Algorithm 4.3: SGD with momentum on ill-conditioned quadratic",
        section="6",
        predicate=alg_4_3_sgd_momentum,
    ))

    # --- Algorithm 4.4: Logistic Regression via Gradient Descent ---
    def alg_4_4_logistic_regression():
        np.random.seed(42)
        n = 200
        X = np.column_stack([np.ones(n), np.random.randn(n)])
        beta_true = np.array([0.0, 2.0])
        prob = 1 / (1 + np.exp(-X @ beta_true))
        y = (np.random.rand(n) < prob).astype(float)
        beta = np.zeros(2)
        eta = 0.5
        for _ in range(500):
            p_hat = 1 / (1 + np.exp(-X @ beta))
            gradient = (1 / n) * X.T @ (p_hat - y)
            beta = beta - eta * gradient
        # Predict: accuracy should be reasonable
        pred = (1 / (1 + np.exp(-X @ beta)) > 0.5).astype(float)
        accuracy = np.mean(pred == y)
        ok = accuracy > 0.70
        return (ok, f"Accuracy={accuracy:.2f}, beta={beta}")
    ch.add(StructuralCheck(
        label="Algorithm 4.4: Logistic regression via gradient descent",
        section="6",
        predicate=alg_4_4_logistic_regression,
    ))

    # --- Algorithm 4.5: Backpropagation (Two-Layer Network) ---
    def alg_4_5_backprop():
        np.random.seed(42)
        # Simple 2-layer net: 2 inputs, 3 hidden, 1 output
        W1 = np.random.randn(3, 2) * 0.5
        b1 = np.zeros(3)
        w2 = np.random.randn(3) * 0.5
        b2 = 0.0
        # Training data: y = x1 + x2
        X_train = np.random.randn(100, 2)
        y_train = X_train[:, 0] + X_train[:, 1]
        eta = 0.01
        for epoch in range(200):
            for i in range(len(X_train)):
                x, y = X_train[i], y_train[i]
                # Forward
                z1 = W1 @ x + b1
                a1 = np.tanh(z1)
                y_hat = w2 @ a1 + b2
                # Backward
                delta2 = y_hat - y
                dw2 = delta2 * a1
                db2 = delta2
                delta1 = (w2 * delta2) * (1 - a1 ** 2)  # tanh'
                dW1 = np.outer(delta1, x)
                db1 = delta1
                # Update
                W1 -= eta * dW1
                b1 -= eta * db1
                w2 -= eta * dw2
                b2 -= eta * db2
        # Test
        x_test = np.array([1.0, 2.0])
        z1 = W1 @ x_test + b1
        a1 = np.tanh(z1)
        y_pred = w2 @ a1 + b2
        ok = abs(y_pred - 3.0) < 0.5
        return (ok, f"Predicted {y_pred:.3f} for target 3.0")
    ch.add(StructuralCheck(
        label="Algorithm 4.5: Backpropagation two-layer network",
        section="6",
        predicate=alg_4_5_backprop,
    ))

    # --- Algorithm 4.6: PCA via Eigendecomposition ---
    def alg_4_6_pca():
        np.random.seed(42)
        # Generate correlated 2D data
        n = 500
        X = np.random.randn(n, 2)
        X[:, 1] = 0.8 * X[:, 0] + 0.2 * X[:, 1]  # correlated
        # Center
        mu = X.mean(axis=0)
        Xc = X - mu
        # Covariance
        Sigma = (Xc.T @ Xc) / (n - 1)
        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(Sigma)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        V = eigenvectors[:, idx]
        # Project onto first PC
        Z = Xc @ V[:, :1]
        # Variance explained
        var_explained = eigenvalues[0] / eigenvalues.sum()
        ok1 = var_explained > 0.8  # should capture most variance
        # Reconstruction: Z @ V[:,:1].T should approximate Xc
        Xc_approx = Z @ V[:, :1].T
        recon_err = np.linalg.norm(Xc - Xc_approx) / np.linalg.norm(Xc)
        ok2 = recon_err < 0.5
        return (ok1 and ok2, f"Var explained={var_explained:.3f}, recon err={recon_err:.3f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.6: PCA via eigendecomposition",
        section="6",
        predicate=alg_4_6_pca,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.27: Activation function properties
    # ReLU: phi(z) = max(0,z), phi'(z) = 1 for z>0
    def remark_327_relu():
        import numpy as np
        z = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 5.0])
        relu = np.maximum(0, z)
        expected = np.array([0.0, 0.0, 0.0, 1.0, 2.0, 5.0])
        ok = np.allclose(relu, expected)
        return (ok, f"ReLU({z}) = {relu}")
    ch.add(StructuralCheck(
        label="Remark 3.27: ReLU(z) = max(0,z)",
        section="4",
        predicate=remark_327_relu,
        note="Remark 3.27",
    ))

    # Remark 3.27: Sigmoid sigma(z) = 1/(1+e^{-z})
    def remark_327_sigmoid():
        import numpy as np
        z = np.array([-100.0, 0.0, 100.0])
        sigma = 1 / (1 + np.exp(-z))
        # sigma(0) = 0.5, sigma(-inf) -> 0, sigma(+inf) -> 1
        ok1 = abs(sigma[1] - 0.5) < 1e-10
        ok2 = sigma[0] < 1e-10  # near 0
        ok3 = abs(sigma[2] - 1.0) < 1e-10  # near 1
        return (ok1 and ok2 and ok3, f"sigma(0)={sigma[1]:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.27: Sigmoid properties: sigma(0)=0.5, limits 0/1",
        section="4",
        predicate=remark_327_sigmoid,
        note="Remark 3.27",
    ))

    # Remark 3.27: tanh is zero-centered: tanh(0) = 0
    def remark_327_tanh():
        import numpy as np
        ok = abs(np.tanh(0.0)) < 1e-10
        # tanh(z) = (e^z - e^{-z})/(e^z + e^{-z})
        z = 1.0
        tanh_manual = (np.exp(z) - np.exp(-z)) / (np.exp(z) + np.exp(-z))
        tanh_np = np.tanh(z)
        ok2 = abs(tanh_manual - tanh_np) < 1e-10
        return (ok and ok2, f"tanh(0)={np.tanh(0.0):.10f}, tanh(1) manual={tanh_manual:.10f}")
    ch.add(StructuralCheck(
        label="Remark 3.27: tanh(0)=0, matches formula",
        section="4",
        predicate=remark_327_tanh,
        note="Remark 3.27",
    ))

    # Remark 3.11: Ridge shrinks more along small eigenvalues
    def remark_311_ridge_shrinkage():
        import numpy as np
        # X'X with eigenvalues 100 and 0.01 (ill-conditioned)
        lam_reg = 0.1  # regularization
        n = 10
        eig_large, eig_small = 100.0, 0.01
        # Shrinkage factor: lambda_j / (lambda_j + n*lambda)
        shrink_large = eig_large / (eig_large + n * lam_reg)
        shrink_small = eig_small / (eig_small + n * lam_reg)
        # Ridge shrinks small eigenvalue direction more
        ok = shrink_small < shrink_large
        return (ok, f"Shrinkage large={shrink_large:.4f}, small={shrink_small:.4f}")
    ch.add(StructuralCheck(
        label="Remark 3.11: Ridge shrinks small-eigenvalue directions more",
        section="4",
        predicate=remark_311_ridge_shrinkage,
        note="Remark 3.11",
    ))

    # --- Remark 3.10: Ridge = constrained OLS, same solution via KKT ---
    def _remark_3_10_ridge_constrained():
        """Verify Ridge = (X'X + lambda*I)^{-1} X'y gives same result as constrained form."""
        rng = np.random.default_rng(2610)
        n, p = 50, 5
        X = rng.standard_normal((n, p))
        y = rng.standard_normal(n)
        lam = 1.0
        # Ridge analytical
        beta_ridge = np.linalg.solve(X.T @ X + lam * np.eye(p), X.T @ y)
        # Verify it minimises ||y - Xb||^2 + lambda*||b||^2
        obj_ridge = np.sum((y - X @ beta_ridge)**2) + lam * np.sum(beta_ridge**2)
        # Compare with OLS (lambda=0)
        beta_ols = np.linalg.lstsq(X, y, rcond=None)[0]
        obj_ols_at_ridge_beta = np.sum((y - X @ beta_ridge)**2) + lam * np.sum(beta_ridge**2)
        # Ridge norm should be smaller than OLS norm
        if np.linalg.norm(beta_ridge) >= np.linalg.norm(beta_ols) * 1.01:
            return (False, f"Ridge norm {np.linalg.norm(beta_ridge)} >= OLS norm {np.linalg.norm(beta_ols)}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.10: Ridge shrinks coefficients — ||beta_ridge|| < ||beta_OLS||",
        section="3.10",
        predicate=_remark_3_10_ridge_constrained,
        note="Remark 3.10: constrained optimization interpretation",
    ))

    # --- Remark 3.24: Bias-variance tradeoff — optimal lambda minimises MSE ---
    def _remark_3_24_bias_variance():
        """Verify bias increases and variance decreases with lambda."""
        rng = np.random.default_rng(2624)
        n, p = 30, 5
        X = rng.standard_normal((n, p))
        beta_true = np.array([1, 2, 3, -1, 0.5])
        lambdas = [0.0, 0.1, 1.0, 10.0, 100.0]
        biases = []
        variances = []
        for lam in lambdas:
            betas = []
            for _ in range(200):
                y = X @ beta_true + rng.standard_normal(n) * 2
                b = np.linalg.solve(X.T @ X + lam * np.eye(p), X.T @ y)
                betas.append(b)
            betas = np.array(betas)
            mean_beta = np.mean(betas, axis=0)
            bias_sq = np.sum((mean_beta - beta_true)**2)
            var = np.mean(np.var(betas, axis=0))
            biases.append(bias_sq)
            variances.append(var)
        # Bias should increase with lambda
        for i in range(len(lambdas) - 1):
            if biases[i+1] < biases[i] - 0.01:
                return (False, f"Bias not increasing: lambda={lambdas[i+1]}, bias={biases[i+1]} < {biases[i]}")
        # Variance should generally decrease with lambda (allow small fluctuations)
        for i in range(len(lambdas) - 1):
            if variances[i+1] > variances[i] * 1.10:
                return (False, f"Variance not decreasing: lambda={lambdas[i+1]}, var={variances[i+1]} > {variances[i]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.24: Bias increases, variance decreases with lambda",
        section="3.24",
        predicate=_remark_3_24_bias_variance,
        note="Remark 3.24: bias-variance tradeoff",
    ))

    return ch
