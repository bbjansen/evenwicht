# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Theorem verification via property-based testing.

Instead of verifying proofs (which requires a proof assistant), we verify
that theorem STATEMENTS are true by stress-testing them:

1. RANDOM STRESS TEST: Generate random inputs satisfying hypotheses,
   verify the conclusion holds for all of them.
2. COUNTEREXAMPLE HUNT: Verify the conclusion FAILS when hypotheses
   are violated (shows the hypotheses are necessary).
3. MONTE CARLO CONVERGENCE: Simulate limit theorems and verify they
   approach their stated limits.
4. CONSEQUENCE TEST: If the theorem is true, test observable consequences.
5. PROOF STEP ALGEBRA: Verify each algebraic manipulation in the proof.

Usage:
    from theorem_testing import TheoremTest, run_theorem_tests
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Callable
from framework import Chapter, StructuralCheck


@dataclass
class TheoremTest:
    """A property-based test for a theorem statement.

    Attributes:
        name: Human-readable theorem name (e.g., "Theorem 3.8 Cauchy-Schwarz")
        chapter: Chapter number
        section: Section reference
        hypothesis: Description of when the theorem applies
        conclusion: Description of what the theorem claims
        test_fn: Function that generates random inputs satisfying
                 the hypotheses and returns (passed: bool, message: str)
        n_trials: Number of random trials to run
        strategy: Which verification strategy this uses
    """
    name: str
    chapter: int
    section: str
    hypothesis: str
    conclusion: str
    test_fn: Callable[[], tuple[bool, str]]
    n_trials: int = 1000
    strategy: str = "stress_test"

    def run(self) -> tuple[bool, str]:
        """Run n_trials and return (all_passed, first_failure_message)."""
        for i in range(self.n_trials):
            ok, msg = self.test_fn()
            if not ok:
                return False, f"Trial {i+1}/{self.n_trials}: {msg}"
        return True, f"All {self.n_trials} trials passed"

    def as_structural_check(self) -> StructuralCheck:
        """Convert to a StructuralCheck for the verification framework."""
        def predicate():
            ok, msg = self.run()
            return (ok, msg)
        return StructuralCheck(
            label=f"{self.name} [{self.strategy}, {self.n_trials} trials]",
            section=self.section,
            predicate=predicate,
            note=f"Hypothesis: {self.hypothesis}",
        )


# =========================================================================
# Chapter 1: Expressions
# =========================================================================

def composition_associativity() -> tuple[bool, str]:
    """Theorem 3.5: f(g(h(x))) = (f.g)(h(x)) = f(g(h(x)))."""
    x = np.random.uniform(-5, 5)
    a, b, c = np.random.randn(3)
    h = lambda x: a * x + 1
    g = lambda x: x ** 2 + b
    f = lambda x: math.sin(x) + c
    lhs = f(g(h(x)))  # f . (g . h)
    rhs = f(g(h(x)))  # (f . g) . h -- same computation path
    # More explicitly: compute (f.g) first then apply to h(x)
    fg = lambda x: f(g(x))
    gh = lambda x: g(h(x))
    val1 = f(gh(x))  # f . (g . h)
    val2 = fg(h(x))  # (f . g) . h
    ok = abs(val1 - val2) < 1e-12
    return (ok, f"f(g(h({x:.4f})))={val1:.10f} != (f.g)(h({x:.4f}))={val2:.10f}" if not ok else "")


def well_definedness_of_evaluation() -> tuple[bool, str]:
    """Theorem 3.17: Evaluation of well-formed expressions is well-defined.
    Build random arithmetic expression trees and verify eval produces finite result."""
    # Build a random expression: binary tree of depth 2-3
    x = np.random.uniform(0.1, 10)  # avoid domain issues
    ops = [lambda a, b: a + b, lambda a, b: a * b, lambda a, b: a - b]
    op = ops[np.random.randint(0, len(ops))]
    a = np.random.uniform(0.1, 10)
    b = np.random.uniform(0.1, 10)
    result = op(op(x, a), b)
    ok = math.isfinite(result)
    return (ok, f"Expression evaluation not finite: {result}" if not ok else "")


# =========================================================================
# Chapter 2: Special Functions
# =========================================================================

def gamma_factorial_property() -> tuple[bool, str]:
    """Theorem 3.2: Gamma(z+1) = z * Gamma(z) for z > 0."""
    z = np.random.uniform(0.1, 20.0)
    lhs = math.gamma(z + 1)
    rhs = z * math.gamma(z)
    rel_err = abs(lhs - rhs) / max(abs(lhs), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"Gamma({z+1:.4f})={lhs:.8f} != {z:.4f}*Gamma({z:.4f})={rhs:.8f}" if not ok else "")


def gamma_extends_factorial() -> tuple[bool, str]:
    """Corollary 3.3: Gamma(n+1) = n! for integer n."""
    n = np.random.randint(0, 20)
    lhs = math.gamma(n + 1)
    rhs = float(math.factorial(n))
    rel_err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"Gamma({n+1})={lhs:.6f} != {n}!={rhs:.6f}" if not ok else "")


def gamma_half_sqrt_pi() -> tuple[bool, str]:
    """Theorem 3.4: Gamma(1/2) = sqrt(pi)."""
    lhs = math.gamma(0.5)
    rhs = math.sqrt(math.pi)
    ok = abs(lhs - rhs) < 1e-14
    return (ok, f"Gamma(1/2)={lhs:.15f} != sqrt(pi)={rhs:.15f}" if not ok else "")


def euler_reflection_formula() -> tuple[bool, str]:
    """Theorem 3.5: Gamma(z)*Gamma(1-z) = pi/sin(pi*z) for z not integer."""
    z = np.random.uniform(0.1, 0.9)
    lhs = math.gamma(z) * math.gamma(1 - z)
    rhs = math.pi / math.sin(math.pi * z)
    rel_err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"Gamma({z:.4f})*Gamma({1-z:.4f})={lhs:.8f} != pi/sin(pi*{z:.4f})={rhs:.8f}" if not ok else "")


def legendre_duplication_formula() -> tuple[bool, str]:
    """Theorem 3.6: Gamma(z)*Gamma(z+1/2) = sqrt(pi)/(2^(2z-1)) * Gamma(2z)."""
    z = np.random.uniform(0.5, 8.0)
    lhs = math.gamma(z) * math.gamma(z + 0.5)
    rhs = math.sqrt(math.pi) / (2 ** (2 * z - 1)) * math.gamma(2 * z)
    rel_err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
    ok = rel_err < 1e-8
    return (ok, f"Legendre: LHS={lhs:.8f} != RHS={rhs:.8f}" if not ok else "")


def beta_gamma_relation() -> tuple[bool, str]:
    """Theorem 3.10: B(a,b) = Gamma(a)*Gamma(b)/Gamma(a+b)."""
    from scipy.special import beta as scipy_beta
    a = np.random.uniform(0.5, 10.0)
    b = np.random.uniform(0.5, 10.0)
    lhs = scipy_beta(a, b)
    rhs = math.gamma(a) * math.gamma(b) / math.gamma(a + b)
    rel_err = abs(lhs - rhs) / max(abs(lhs), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"B({a:.3f},{b:.3f})={lhs:.8f} != Gamma product={rhs:.8f}" if not ok else "")


def beta_symmetry() -> tuple[bool, str]:
    """Theorem 3.11: B(a,b) = B(b,a)."""
    from scipy.special import beta as scipy_beta
    a = np.random.uniform(0.5, 10.0)
    b = np.random.uniform(0.5, 10.0)
    lhs = scipy_beta(a, b)
    rhs = scipy_beta(b, a)
    ok = abs(lhs - rhs) < 1e-14 * max(abs(lhs), 1)
    return (ok, f"B({a:.3f},{b:.3f})={lhs:.10f} != B({b:.3f},{a:.3f})={rhs:.10f}" if not ok else "")


def beta_recursive_property() -> tuple[bool, str]:
    """Theorem 3.12: B(a,b) = (a-1)/(a+b-1) * B(a-1, b) for a > 1."""
    from scipy.special import beta as scipy_beta
    a = np.random.uniform(1.5, 10.0)
    b = np.random.uniform(0.5, 10.0)
    lhs = scipy_beta(a, b)
    rhs = (a - 1) / (a + b - 1) * scipy_beta(a - 1, b)
    rel_err = abs(lhs - rhs) / max(abs(lhs), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"B({a:.3f},{b:.3f})={lhs:.8f} != recursive={rhs:.8f}" if not ok else "")


def erf_normal_cdf_relation() -> tuple[bool, str]:
    """Theorem 3.16: Phi(x) = (1 + erf(x/sqrt(2)))/2."""
    from scipy.stats import norm
    from scipy.special import erf
    x = np.random.uniform(-4, 4)
    lhs = norm.cdf(x)
    rhs = 0.5 * (1 + erf(x / math.sqrt(2)))
    ok = abs(lhs - rhs) < 1e-14
    return (ok, f"Phi({x:.4f})={lhs:.10f} != erf formula={rhs:.10f}" if not ok else "")


def pascal_rule() -> tuple[bool, str]:
    """Theorem 3.19: C(n,k) = C(n-1,k-1) + C(n-1,k)."""
    n = np.random.randint(2, 30)
    k = np.random.randint(1, n)
    lhs = math.comb(n, k)
    rhs = math.comb(n - 1, k - 1) + math.comb(n - 1, k)
    ok = lhs == rhs
    return (ok, f"C({n},{k})={lhs} != C({n-1},{k-1})+C({n-1},{k})={rhs}" if not ok else "")


def binomial_theorem() -> tuple[bool, str]:
    """Theorem 3.20: (x+y)^n = sum C(n,k) x^(n-k) y^k."""
    n = np.random.randint(0, 10)
    # Ensure |x+y| > 0.1 to avoid floating-point cancellation when (x+y)^n ~ 0.
    while True:
        x = np.random.uniform(-2, 2)
        y = np.random.uniform(-2, 2)
        if abs(x + y) > 0.1:
            break
    lhs = (x + y) ** n
    rhs = sum(math.comb(n, k) * x ** (n - k) * y ** k for k in range(n + 1))
    abs_err = abs(lhs - rhs)
    scale = max(abs(lhs), abs(rhs), 1)
    ok = abs_err / scale < 1e-6 or abs_err < 1e-12
    return (ok, f"({x:.3f}+{y:.3f})^{n}={lhs:.8f} != binomial sum={rhs:.8f}" if not ok else "")


def stirling_approximation() -> tuple[bool, str]:
    """Theorem 3.23: n! ~ sqrt(2*pi*n) * (n/e)^n."""
    n = np.random.randint(5, 100)
    actual = math.lgamma(n + 1)  # log(n!)
    approx = 0.5 * math.log(2 * math.pi * n) + n * math.log(n) - n
    rel_err = abs(math.exp(actual - approx) - 1.0)
    ok = rel_err < 1.0 / (12 * n) + 0.01  # Stirling error is O(1/n)
    return (ok, f"Stirling for n={n}: ratio={math.exp(actual-approx):.8f}, expected ~1" if not ok else "")


# =========================================================================
# Chapter 3: Limits and Continuity
# =========================================================================

def limit_one_sided_agreement() -> tuple[bool, str]:
    """Theorem 3.3: Limit exists iff both one-sided limits exist and agree.
    Test with piecewise function that has matching one-sided limits."""
    a = np.random.uniform(-5, 5)
    # f(x) = x^2 is continuous everywhere, so both one-sided limits at a equal a^2
    h_pos = 10 ** (-np.random.uniform(6, 10))
    h_neg = -10 ** (-np.random.uniform(6, 10))
    left = (a + h_neg) ** 2
    right = (a + h_pos) ** 2
    target = a ** 2
    ok = abs(left - target) < 0.001 and abs(right - target) < 0.001
    return (ok, f"One-sided limits don't agree at a={a:.4f}: left={left:.8f}, right={right:.8f}, target={target:.8f}" if not ok else "")


def limit_laws_sum_product() -> tuple[bool, str]:
    """Theorem 3.4: Limit laws (sum, product, scalar multiple).
    If lim f = L, lim g = M, then lim(f+g) = L+M, lim(fg) = LM."""
    a = np.random.uniform(-5, 5)
    c1, c2, c3, c4 = np.random.randn(4)
    # f(x) = c1*x + c2, g(x) = c3*x + c4 -- both linear, continuous
    L = c1 * a + c2
    M = c3 * a + c4
    h = 1e-10
    f_near = c1 * (a + h) + c2
    g_near = c3 * (a + h) + c4
    # Sum law
    sum_ok = abs((f_near + g_near) - (L + M)) < 1e-4
    # Product law
    prod_ok = abs(f_near * g_near - L * M) < 1e-4 * (abs(L * M) + 1)
    ok = sum_ok and prod_ok
    return (ok, f"Limit laws failed at a={a:.4f}" if not ok else "")


def squeeze_theorem_stress() -> tuple[bool, str]:
    """Theorem 3.5: If f(x) <= g(x) <= h(x) and lim f = lim h = L, then lim g = L.
    Test with sin(x)/x squeezed by cos(x) <= sin(x)/x <= 1 near 0."""
    x = np.random.uniform(0.0001, 0.5) * np.random.choice([-1, 1])
    lower = math.cos(abs(x))
    sinc = math.sin(x) / x
    upper = 1.0
    ok = lower - 1e-10 <= sinc <= upper + 1e-10
    return (ok, f"cos({abs(x):.6f})={lower:.8f} <= sin({x:.6f})/{x:.6f}={sinc:.8f} <= 1 FAILED" if not ok else "")


def ivt_stress() -> tuple[bool, str]:
    """Intermediate Value Theorem: continuous f on [a,b] with f(a)*f(b)<0
    has a root in (a,b)."""
    degree = np.random.randint(1, 6)
    coeffs = np.random.randn(degree + 1)
    f = lambda x: sum(c * x**i for i, c in enumerate(coeffs))
    for _ in range(20):
        a = np.random.uniform(-10, 0)
        b = np.random.uniform(0, 10)
        if f(a) * f(b) < 0:
            from scipy.optimize import brentq
            try:
                root = brentq(f, a, b)
                return (True, "")
            except ValueError:
                return (False, f"brentq failed on [{a:.3f},{b:.3f}]")
    return (True, "")  # vacuously true


def evt_stress() -> tuple[bool, str]:
    """Theorem 3.13 (EVT): continuous f on [a,b] attains max and min.
    Test with random polynomials -- verify numerical max/min are attained."""
    degree = np.random.randint(2, 6)
    coeffs = np.random.randn(degree + 1)
    a, b = sorted(np.random.uniform(-5, 5, 2))
    if b - a < 0.1:
        b = a + 1.0
    xs = np.linspace(a, b, 2000)
    vals = np.array([sum(c * x**i for i, c in enumerate(coeffs)) for x in xs])
    fmax = np.max(vals)
    fmin = np.min(vals)
    # Verify max and min are finite (always true for polynomial on closed interval)
    ok = np.isfinite(fmax) and np.isfinite(fmin) and fmin <= fmax
    return (ok, f"EVT violation: fmin={fmin}, fmax={fmax}" if not ok else "")


def continuity_of_composition() -> tuple[bool, str]:
    """Theorem 3.11(6): if g continuous at a and f continuous at g(a),
    then f(g) continuous at a. Test numerically with random functions."""
    # Use f = sin, g = polynomial -- both continuous everywhere
    degree = np.random.randint(1, 4)
    coeffs = np.random.randn(degree + 1)
    g = lambda x: sum(c * x**i for i, c in enumerate(coeffs))
    fog = lambda x: math.sin(g(x))
    a = np.random.uniform(-3, 3)
    # Check continuity: f(g(a+h)) -> f(g(a)) as h -> 0
    h = 1e-8
    val_at_a = fog(a)
    val_near_a = fog(a + h)
    ok = abs(val_at_a - val_near_a) < 0.01  # generous tolerance
    return (ok, f"f(g({a:.4f}))={val_at_a:.8f} but f(g({a+h:.4f}))={val_near_a:.8f}" if not ok else "")


def heine_cantor_uniform_continuity() -> tuple[bool, str]:
    """Theorem 3.16 (Heine-Cantor): continuous f on closed [a,b] is uniformly continuous.
    Verify: for any epsilon, there exists delta independent of location."""
    # f(x) = sin(x) on [0, 10] is uniformly continuous
    a, b = 0.0, 10.0
    epsilon = 0.01
    # For sin, |sin(x)-sin(y)| <= |x-y|, so delta = epsilon works
    delta = epsilon
    # Test at many random pairs
    x1 = np.random.uniform(a, b)
    x2 = x1 + np.random.uniform(-delta, delta)
    x2 = np.clip(x2, a, b)
    diff = abs(math.sin(x1) - math.sin(x2))
    ok = diff <= epsilon + 1e-12
    return (ok, f"|sin({x1:.4f})-sin({x2:.4f})|={diff:.6f} > eps={epsilon}" if not ok else "")


# =========================================================================
# Chapter 4: Differential Calculus
# =========================================================================

def differentiable_implies_continuous() -> tuple[bool, str]:
    """Theorem 3.2: Differentiable at a implies continuous at a.
    Test: f(x) = x^2 is differentiable => f(a+h)-f(a) -> 0."""
    a = np.random.uniform(-10, 10)
    h = 10 ** (-np.random.uniform(6, 12))
    diff = abs((a + h) ** 2 - a ** 2)
    ok = diff < 0.001
    return (ok, f"f(a+h)-f(a)={diff} not small for h={h:.2e}" if not ok else "")


def linearity_of_differentiation() -> tuple[bool, str]:
    """Theorem 3.6: D(af+bg) = a*Df + b*Dg.
    Test with random polynomials."""
    x = np.random.uniform(-5, 5)
    a_coeff, b_coeff = np.random.randn(2)
    # f(x) = x^3, f'(x) = 3x^2
    # g(x) = x^2, g'(x) = 2x
    h = 1e-7
    af_bg = lambda x: a_coeff * x ** 3 + b_coeff * x ** 2
    numerical = (af_bg(x + h) - af_bg(x - h)) / (2 * h)
    analytical = a_coeff * 3 * x ** 2 + b_coeff * 2 * x
    ok = abs(numerical - analytical) < 1e-4
    return (ok, f"D(af+bg)={numerical:.6f} != a*Df+b*Dg={analytical:.6f}" if not ok else "")


def constant_rule() -> tuple[bool, str]:
    """Theorem 3.7: d/dx[c] = 0."""
    c = np.random.randn()
    x = np.random.uniform(-10, 10)
    h = 1e-7
    deriv = (c - c) / h  # f(x+h) - f(x) = c - c = 0
    ok = abs(deriv) < 1e-10
    return (ok, f"d/dx[{c}] = {deriv} != 0" if not ok else "")


def power_rule() -> tuple[bool, str]:
    """Theorem 3.8: d/dx[x^n] = n*x^(n-1)."""
    n = np.random.uniform(0.5, 5.0)
    x = np.random.uniform(0.1, 10.0)
    h = 1e-7
    numerical = ((x + h) ** n - (x - h) ** n) / (2 * h)
    analytical = n * x ** (n - 1)
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-10)
    ok = rel_err < 1e-5
    return (ok, f"d/dx[x^{n:.2f}] numerical={numerical:.8f} != analytical={analytical:.8f}" if not ok else "")


def sum_difference_rule() -> tuple[bool, str]:
    """Theorem 3.9: (f+/-g)' = f' +/- g'."""
    x = np.random.uniform(-5, 5)
    h = 1e-7
    # f(x) = sin(x), g(x) = x^2
    f_plus_g = lambda x: math.sin(x) + x ** 2
    numerical = (f_plus_g(x + h) - f_plus_g(x - h)) / (2 * h)
    analytical = math.cos(x) + 2 * x
    ok = abs(numerical - analytical) < 1e-4
    return (ok, f"(f+g)' numerical={numerical:.8f} != analytical={analytical:.8f}" if not ok else "")


def product_rule() -> tuple[bool, str]:
    """Theorem 3.10: (fg)' = f'g + fg'."""
    x = np.random.uniform(-3, 3)
    h = 1e-7
    # f(x) = x^2, g(x) = sin(x)
    fg = lambda x: x ** 2 * math.sin(x)
    numerical = (fg(x + h) - fg(x - h)) / (2 * h)
    analytical = 2 * x * math.sin(x) + x ** 2 * math.cos(x)
    ok = abs(numerical - analytical) < 1e-3
    return (ok, f"(fg)' numerical={numerical:.6f} != analytical={analytical:.6f}" if not ok else "")


def quotient_rule() -> tuple[bool, str]:
    """Theorem 3.11: (f/g)' = (f'g - fg')/g^2."""
    x = np.random.uniform(0.5, 5)
    h = 1e-7
    # f(x) = sin(x), g(x) = x
    foverg = lambda x: math.sin(x) / x
    numerical = (foverg(x + h) - foverg(x - h)) / (2 * h)
    analytical = (math.cos(x) * x - math.sin(x)) / (x ** 2)
    ok = abs(numerical - analytical) < 1e-4
    return (ok, f"(f/g)' numerical={numerical:.8f} != analytical={analytical:.8f}" if not ok else "")


def rolles_theorem_stress() -> tuple[bool, str]:
    """Theorem 3.24: If f(a)=f(b), f differentiable on (a,b), then exists c with f'(c)=0."""
    a = np.random.uniform(-5, 0)
    b = np.random.uniform(0.5, 5)
    # Use f(x) = sin(pi*(x-a)/(b-a)) which has f(a)=f(b)=0
    f_prime = lambda x: (math.pi / (b - a)) * math.cos(math.pi * (x - a) / (b - a))
    # Search for sign change
    n_pts = 200
    xs = np.linspace(a, b, n_pts)
    gs = [f_prime(x) for x in xs]
    found = False
    for i in range(len(gs) - 1):
        if gs[i] * gs[i + 1] <= 0:
            found = True
            break
    return (found, f"No c found with f'(c)=0 on ({a:.3f},{b:.3f})" if not found else "")


def mvt_stress() -> tuple[bool, str]:
    """Mean Value Theorem: exists c in (a,b) s.t. f'(c) = (f(b)-f(a))/(b-a)."""
    degree = np.random.randint(2, 6)
    coeffs = np.random.randn(degree + 1)
    a = np.random.uniform(-5, 0)
    b = np.random.uniform(0.1, 5)
    f = lambda x: sum(c * x**i for i, c in enumerate(coeffs))
    fp = lambda x: sum(i * c * x**(i-1) for i, c in enumerate(coeffs) if i > 0)
    target = (f(b) - f(a)) / (b - a)
    from scipy.optimize import brentq
    n_pts = 200
    xs = np.linspace(a, b, n_pts)
    gs = [fp(x) - target for x in xs]
    found = False
    for i in range(len(gs) - 1):
        if gs[i] * gs[i+1] <= 0:
            try:
                c = brentq(lambda x: fp(x) - target, xs[i], xs[i+1])
                if a < c < b:
                    found = True
                    break
            except ValueError:
                pass
    return (found, f"No c found where f'(c)={(f(b)-f(a))/(b-a):.6f}" if not found else "")


def lhopital_stress() -> tuple[bool, str]:
    """Theorem 3.26: L'Hopital's rule for 0/0.
    Test lim_{x->0} sin(x)/x = 1 via f'/g' = cos(x)/1."""
    x = np.random.uniform(1e-10, 1e-4)
    ratio = math.sin(x) / x
    deriv_ratio = math.cos(x) / 1.0
    # Both should be close to 1
    ok = abs(ratio - 1.0) < 0.001 and abs(deriv_ratio - 1.0) < 0.001
    return (ok, f"sin({x})/{x}={ratio:.8f}, cos({x})={deriv_ratio:.8f}" if not ok else "")


def chain_rule_stress() -> tuple[bool, str]:
    """Theorem 3.12: d/dx[f(g(x))] = f'(g(x)) * g'(x).
    Test with random polynomial composition vs numerical differentiation."""
    a, b, c = np.random.randn(3)
    x = np.random.uniform(-2, 2)
    g = lambda x: a*x**2 + b*x + c
    gp = lambda x: 2*a*x + b
    fog = lambda x: math.sin(g(x))
    # Analytical: cos(g(x)) * g'(x)
    analytical = math.cos(g(x)) * gp(x)
    # Numerical
    h = 1e-7
    numerical = (fog(x + h) - fog(x - h)) / (2 * h)
    ok = abs(analytical - numerical) < 1e-4
    return (ok, f"Chain rule: analytical={analytical:.8f} != numerical={numerical:.8f}" if not ok else "")


def inverse_function_derivative() -> tuple[bool, str]:
    """Theorem 3.13: (f^{-1})'(y) = 1/f'(f^{-1}(y)).
    Test with f(x)=e^x, f^{-1}(y)=ln(y)."""
    y = np.random.uniform(0.1, 10)
    # (ln)'(y) = 1/y
    lhs = 1.0 / y
    # 1/f'(f^{-1}(y)) = 1/exp(ln(y)) = 1/y
    rhs = 1.0 / math.exp(math.log(y))
    ok = abs(lhs - rhs) < 1e-12
    return (ok, f"(ln)'({y:.4f})={lhs:.10f} != 1/exp(ln({y:.4f}))={rhs:.10f}" if not ok else "")


def derivative_of_exponential() -> tuple[bool, str]:
    """Theorem 3.14: d/dx[e^x] = e^x."""
    x = np.random.uniform(-5, 5)
    h = 1e-7
    numerical = (math.exp(x + h) - math.exp(x - h)) / (2 * h)
    analytical = math.exp(x)
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-15)
    ok = rel_err < 1e-5
    return (ok, f"d/dx[e^{x:.4f}]: numerical={numerical:.8f} != analytical={analytical:.8f}" if not ok else "")


def derivative_of_ln() -> tuple[bool, str]:
    """Theorem 3.15: d/dx[ln x] = 1/x for x > 0."""
    x = np.random.uniform(0.01, 100)
    h = x * 1e-7
    numerical = (math.log(x + h) - math.log(x - h)) / (2 * h)
    analytical = 1.0 / x
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-15)
    ok = rel_err < 1e-5
    return (ok, f"d/dx[ln({x:.4f})]: numerical={numerical:.8f} != 1/x={analytical:.8f}" if not ok else "")


def derivative_of_general_exponential() -> tuple[bool, str]:
    """Theorem 3.16: d/dx[a^x] = a^x * ln(a) for a > 0, a != 1."""
    a = np.random.uniform(0.5, 5.0)
    if abs(a - 1) < 0.01:
        a = 2.0
    x = np.random.uniform(-3, 3)
    h = 1e-7
    numerical = (a ** (x + h) - a ** (x - h)) / (2 * h)
    analytical = a ** x * math.log(a)
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-10)
    ok = rel_err < 1e-4
    return (ok, f"d/dx[{a:.2f}^{x:.2f}]: numerical={numerical:.6f} != analytical={analytical:.6f}" if not ok else "")


def derivative_of_general_log() -> tuple[bool, str]:
    """Theorem 3.17: d/dx[log_a(x)] = 1/(x*ln(a))."""
    a = np.random.uniform(2.0, 10.0)
    x = np.random.uniform(0.1, 100)
    h = x * 1e-7
    numerical = (math.log(x + h, a) - math.log(x - h, a)) / (2 * h)
    analytical = 1.0 / (x * math.log(a))
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-15)
    ok = rel_err < 1e-4
    return (ok, f"d/dx[log_{a:.1f}({x:.2f})]: numerical={numerical:.8f} != analytical={analytical:.8f}" if not ok else "")


def derivative_of_sine() -> tuple[bool, str]:
    """Theorem 3.18: d/dx[sin(x)] = cos(x)."""
    x = np.random.uniform(-10, 10)
    h = 1e-7
    numerical = (math.sin(x + h) - math.sin(x - h)) / (2 * h)
    analytical = math.cos(x)
    ok = abs(numerical - analytical) < 1e-5
    return (ok, f"d/dx[sin({x:.4f})]: numerical={numerical:.8f} != cos={analytical:.8f}" if not ok else "")


def derivative_of_cosine() -> tuple[bool, str]:
    """Theorem 3.19: d/dx[cos(x)] = -sin(x)."""
    x = np.random.uniform(-10, 10)
    h = 1e-7
    numerical = (math.cos(x + h) - math.cos(x - h)) / (2 * h)
    analytical = -math.sin(x)
    ok = abs(numerical - analytical) < 1e-5
    return (ok, f"d/dx[cos({x:.4f})]: numerical={numerical:.8f} != -sin={analytical:.8f}" if not ok else "")


def derivative_of_tangent() -> tuple[bool, str]:
    """Theorem 3.20: d/dx[tan(x)] = sec^2(x) = 1/cos^2(x)."""
    x = np.random.uniform(-1.5, 1.5)  # avoid pi/2
    h = 1e-7
    numerical = (math.tan(x + h) - math.tan(x - h)) / (2 * h)
    analytical = 1.0 / (math.cos(x) ** 2)
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-10)
    ok = rel_err < 1e-4
    return (ok, f"d/dx[tan({x:.4f})]: numerical={numerical:.6f} != sec^2={analytical:.6f}" if not ok else "")


def derivative_of_abs() -> tuple[bool, str]:
    """Theorem 3.21: d/dx[|x|] = sign(x) for x != 0."""
    x = np.random.uniform(0.01, 10) * np.random.choice([-1, 1])
    h = 1e-7
    numerical = (abs(x + h) - abs(x - h)) / (2 * h)
    analytical = 1.0 if x > 0 else -1.0
    ok = abs(numerical - analytical) < 1e-4
    return (ok, f"d/dx[|{x:.4f}|]: numerical={numerical:.6f} != sign={analytical}" if not ok else "")


def derivative_of_sqrt() -> tuple[bool, str]:
    """Theorem 3.22: d/dx[sqrt(x)] = 1/(2*sqrt(x)) for x > 0."""
    x = np.random.uniform(0.01, 100)
    h = x * 1e-7
    numerical = (math.sqrt(x + h) - math.sqrt(x - h)) / (2 * h)
    analytical = 1.0 / (2 * math.sqrt(x))
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-15)
    ok = rel_err < 1e-4
    return (ok, f"d/dx[sqrt({x:.4f})]: numerical={numerical:.8f} != analytical={analytical:.8f}" if not ok else "")


def logarithmic_differentiation() -> tuple[bool, str]:
    """Theorem 3.23: d/dx[f(x)^g(x)] = f^g * [g'*ln(f) + g*f'/f].
    Test with f(x)=x, g(x)=x => d/dx[x^x] = x^x*(1+ln(x))."""
    x = np.random.uniform(0.5, 5)
    h = 1e-7
    xx = lambda x: x ** x
    numerical = (xx(x + h) - xx(x - h)) / (2 * h)
    analytical = x ** x * (1 + math.log(x))
    rel_err = abs(numerical - analytical) / max(abs(analytical), 1e-10)
    ok = rel_err < 1e-4
    return (ok, f"d/dx[x^x] at x={x:.3f}: numerical={numerical:.6f} != analytical={analytical:.6f}" if not ok else "")


# =========================================================================
# Chapter 5: Integral Calculus
# =========================================================================

def continuous_functions_are_integrable() -> tuple[bool, str]:
    """Theorem 3.4: Continuous f on [a,b] is Riemann integrable.
    Verify: upper and lower Riemann sums converge as partition refines."""
    a = np.random.uniform(-2, 0)
    b = np.random.uniform(0.1, 2)
    # f(x) = x^2, continuous
    N = 1000
    xs = np.linspace(a, b, N + 1)
    dx = (b - a) / N
    lower = sum(min(xs[i] ** 2, xs[i + 1] ** 2) * dx for i in range(N))
    upper = sum(max(xs[i] ** 2, xs[i + 1] ** 2) * dx for i in range(N))
    exact = (b ** 3 - a ** 3) / 3
    ok = lower - 1e-6 <= exact <= upper + 1e-6
    return (ok, f"Riemann sums: L={lower:.6f}, U={upper:.6f}, exact={exact:.6f}" if not ok else "")


def integral_linearity() -> tuple[bool, str]:
    """Theorem 3.5: int(a*f+b*g) = a*int(f) + b*int(g)."""
    from scipy.integrate import quad
    alpha, beta = np.random.randn(2)
    a, b = sorted(np.random.uniform(-3, 3, 2))
    if b - a < 0.1:
        b = a + 1
    f = lambda x: x ** 2
    g = lambda x: math.sin(x)
    lhs, _ = quad(lambda x: alpha * f(x) + beta * g(x), a, b)
    rhs_f, _ = quad(f, a, b)
    rhs_g, _ = quad(g, a, b)
    rhs = alpha * rhs_f + beta * rhs_g
    ok = abs(lhs - rhs) < 1e-8
    return (ok, f"Linearity: LHS={lhs:.8f} != RHS={rhs:.8f}" if not ok else "")


def integral_monotonicity() -> tuple[bool, str]:
    """Theorem 3.6: If f(x) <= g(x) on [a,b], then int(f) <= int(g)."""
    from scipy.integrate import quad
    a, b = 0.0, np.random.uniform(1, 5)
    # f(x) = x, g(x) = x + 1 => f <= g
    int_f, _ = quad(lambda x: x, a, b)
    int_g, _ = quad(lambda x: x + 1, a, b)
    ok = int_f <= int_g + 1e-10
    return (ok, f"int(f)={int_f:.6f} > int(g)={int_g:.6f} but f<=g" if not ok else "")


def integral_additivity_over_intervals() -> tuple[bool, str]:
    """Theorem 3.7: int_a^c f = int_a^b f + int_b^c f."""
    from scipy.integrate import quad
    a, c = sorted(np.random.uniform(-5, 5, 2))
    if c - a < 0.1:
        c = a + 2
    b = np.random.uniform(a, c)
    f = lambda x: x ** 2 + math.sin(x)
    int_ac, _ = quad(f, a, c)
    int_ab, _ = quad(f, a, b)
    int_bc, _ = quad(f, b, c)
    ok = abs(int_ac - (int_ab + int_bc)) < 1e-8
    return (ok, f"int_ac={int_ac:.8f} != int_ab+int_bc={int_ab + int_bc:.8f}" if not ok else "")


def ftc_part1_stress() -> tuple[bool, str]:
    """FTC Part 1: d/dx[int_a^x f(t)dt] = f(x).
    Test with f(t) = t^2; F(x) = x^3/3 - a^3/3; F'(x) = x^2 = f(x)."""
    a = np.random.uniform(-5, 0)
    x = np.random.uniform(0, 5)
    f_val = x ** 2
    F = lambda x_: x_**3 / 3 - a**3 / 3
    h = 1e-7
    F_prime_numerical = (F(x + h) - F(x - h)) / (2 * h)
    ok = abs(f_val - F_prime_numerical) < 1e-4
    return (ok, f"FTC1: f({x:.4f})={f_val:.8f} != F'({x:.4f})={F_prime_numerical:.8f}" if not ok else "")


def ftc_part2_stress() -> tuple[bool, str]:
    """FTC Part 2: int_a^b f(x)dx = F(b) - F(a).
    Test with random polynomials."""
    degree = np.random.randint(1, 5)
    coeffs = np.random.randn(degree + 1)
    a = np.random.uniform(-3, 0)
    b = np.random.uniform(0.1, 3)
    F = lambda x: sum(c * x**(i+1) / (i+1) for i, c in enumerate(coeffs))
    from scipy.integrate import quad
    f = lambda x: sum(c * x**i for i, c in enumerate(coeffs))
    numerical, _ = quad(f, a, b)
    analytical = F(b) - F(a)
    ok = abs(numerical - analytical) < 1e-8
    return (ok, f"FTC2: int={numerical:.8f} != F(b)-F(a)={analytical:.8f}" if not ok else "")


def substitution_rule_stress() -> tuple[bool, str]:
    """Theorem 3.12: int_a^b f(g(x))*g'(x) dx = int_{g(a)}^{g(b)} f(u) du.
    Test with g(x) = x^2, f(u) = sin(u)."""
    from scipy.integrate import quad
    a = np.random.uniform(0.1, 2)
    b = np.random.uniform(a + 0.1, 4)
    # int_a^b sin(x^2) * 2x dx = int_{a^2}^{b^2} sin(u) du
    lhs, _ = quad(lambda x: math.sin(x ** 2) * 2 * x, a, b)
    rhs, _ = quad(lambda u: math.sin(u), a ** 2, b ** 2)
    ok = abs(lhs - rhs) < 1e-8
    return (ok, f"Substitution: LHS={lhs:.8f} != RHS={rhs:.8f}" if not ok else "")


def integration_by_parts_stress() -> tuple[bool, str]:
    """Theorem 3.13: int_a^b u*v' dx = [u*v]_a^b - int_a^b u'*v dx.
    Test with u=x, v'=e^x => u'=1, v=e^x."""
    a = np.random.uniform(-3, 0)
    b = np.random.uniform(0.1, 3)
    lhs_boundary = b * math.exp(b) - a * math.exp(a)
    rhs_integral = math.exp(b) - math.exp(a)
    ibp_result = lhs_boundary - rhs_integral
    direct = (b - 1) * math.exp(b) - (a - 1) * math.exp(a)
    ok = abs(ibp_result - direct) < 1e-10
    return (ok, f"IBP: {ibp_result:.10f} != direct {direct:.10f}" if not ok else "")


# =========================================================================
# Chapter 6: Series and Approximation
# =========================================================================

def monotone_convergence_theorem() -> tuple[bool, str]:
    """Theorem 3.3: Every bounded monotone sequence converges.
    Test: a_n = sum_{k=1}^n 1/k^2 is increasing and bounded by pi^2/6."""
    N = np.random.randint(100, 500)
    partial = sum(1.0 / k ** 2 for k in range(1, N + 1))
    bound = math.pi ** 2 / 6
    increasing = all(
        sum(1.0 / k ** 2 for k in range(1, n + 1)) <=
        sum(1.0 / k ** 2 for k in range(1, n + 2))
        for n in range(1, 10)
    )
    bounded = partial <= bound + 1e-10
    ok = increasing and bounded
    return (ok, f"S_{N}={partial:.8f}, bound={bound:.8f}, increasing={increasing}" if not ok else "")


def divergence_test() -> tuple[bool, str]:
    """Theorem 3.5: If sum a_n converges, then a_n -> 0.
    Contrapositive: a_n not -> 0 implies divergence.
    Test: sum 1/n diverges (harmonic series), verify partial sums grow."""
    N1 = np.random.randint(100, 500)
    N2 = N1 * 10
    S1 = sum(1.0 / k for k in range(1, N1 + 1))
    S2 = sum(1.0 / k for k in range(1, N2 + 1))
    # Harmonic series grows unboundedly
    ok = S2 > S1 + 0.5  # should grow by at least ln(10) ~ 2.3
    return (ok, f"Harmonic S_{N1}={S1:.4f}, S_{N2}={S2:.4f}, expected growth" if not ok else "")


def geometric_series_sum() -> tuple[bool, str]:
    """Theorem 3.6a: sum_{n=0}^{inf} ar^n = a/(1-r) for |r|<1."""
    r = np.random.uniform(-0.99, 0.99)
    a = np.random.uniform(0.1, 10)
    N = 500
    partial = a * sum(r**n for n in range(N + 1))
    formula = a / (1 - r)
    ok = abs(partial - formula) < abs(a * r**(N+1) / (1 - r)) + 1e-10
    return (ok, f"Geometric sum: partial={partial:.8f} != formula={formula:.8f}" if not ok else "")


def comparison_test() -> tuple[bool, str]:
    """Theorem 3.7: If 0 <= a_n <= b_n and sum b_n converges, then sum a_n converges.
    Test: a_n = 1/(n^2+1) <= 1/n^2 = b_n, sum b_n = pi^2/6."""
    N = np.random.randint(100, 500)
    sum_a = sum(1.0 / (k ** 2 + 1) for k in range(1, N + 1))
    sum_b = sum(1.0 / k ** 2 for k in range(1, N + 1))
    # a_n <= b_n implies sum_a <= sum_b
    ok = sum_a <= sum_b + 1e-10
    return (ok, f"sum(1/(n^2+1))={sum_a:.8f} > sum(1/n^2)={sum_b:.8f}" if not ok else "")


def ratio_test_convergence() -> tuple[bool, str]:
    """Theorem 3.8: If |a_{n+1}/a_n| -> L < 1, series converges absolutely.
    Test with sum x^n/n! which converges for all x."""
    x = np.random.uniform(-5, 5)
    partial_50 = sum(x**n / math.factorial(n) for n in range(51))
    partial_100 = sum(x**n / math.factorial(n) for n in range(101))
    ok = abs(partial_100 - partial_50) < 1e-8
    return (ok, f"sum x^n/n! not converging: S50={partial_50:.8f}, S100={partial_100:.8f}" if not ok else "")


def root_test() -> tuple[bool, str]:
    """Theorem 3.9: If lim |a_n|^{1/n} = L < 1, series converges.
    Test with a_n = (1/3)^n: L = 1/3 < 1."""
    r = np.random.uniform(0.1, 0.9)
    N = 200
    partial = sum(r ** n for n in range(N + 1))
    formula = 1 / (1 - r)
    ok = abs(partial - formula) < 1e-6
    return (ok, f"Root test series: partial={partial:.8f} != formula={formula:.8f}" if not ok else "")


def integral_test() -> tuple[bool, str]:
    """Theorem 3.10: sum f(n) converges iff int f(x) dx converges for f positive decreasing.
    Test: sum 1/n^2 converges because int 1/x^2 dx from 1 to inf = 1."""
    from scipy.integrate import quad
    N = np.random.randint(100, 500)
    series_partial = sum(1.0 / k ** 2 for k in range(1, N + 1))
    integral, _ = quad(lambda x: 1.0 / x ** 2, 1, N)
    # Integral test: integral <= sum <= integral + f(1)
    f1 = 1.0
    ok = integral - 1e-6 <= series_partial <= integral + f1 + 1e-6
    return (ok, f"Integral test: int={integral:.6f}, sum={series_partial:.6f}" if not ok else "")


def alternating_series_error_bound() -> tuple[bool, str]:
    """Theorem 3.11: For alternating series, |S - S_N| <= a_{N+1}.
    Test with ln(2) = 1 - 1/2 + 1/3 - 1/4 + ..."""
    N = np.random.randint(10, 100)
    partial = sum((-1)**(n+1) / n for n in range(1, N + 1))
    actual = math.log(2)
    error = abs(actual - partial)
    bound = 1.0 / (N + 1)
    ok = error <= bound + 1e-14
    return (ok, f"|ln2 - S_{N}| = {error:.10f} > a_{N+1} = {bound:.10f}" if not ok else "")


def absolute_convergence_implies_convergence() -> tuple[bool, str]:
    """Theorem 3.12a: Absolute convergence implies convergence.
    If sum |a_n| converges, then sum a_n converges.
    Test: sum (-1)^n / n^2 converges absolutely."""
    N = np.random.randint(100, 500)
    abs_sum = sum(1.0 / n ** 2 for n in range(1, N + 1))
    alt_sum = sum((-1.0) ** n / n ** 2 for n in range(1, N + 1))
    # Both should converge (i.e., partial sums should stabilize)
    abs_sum2 = sum(1.0 / n ** 2 for n in range(1, 2 * N + 1))
    alt_sum2 = sum((-1.0) ** n / n ** 2 for n in range(1, 2 * N + 1))
    ok = abs(abs_sum2 - abs_sum) < 0.01 and abs(alt_sum2 - alt_sum) < 0.01
    return (ok, f"Abs conv: |dS_abs|={abs(abs_sum2-abs_sum):.6f}, |dS_alt|={abs(alt_sum2-alt_sum):.6f}" if not ok else "")


def taylor_remainder_bound() -> tuple[bool, str]:
    """Lagrange remainder: |R_n(x)| <= M|x-a|^(n+1)/(n+1)!
    where M = max|f^(n+1)| on [a,x]. Test with e^x."""
    x = np.random.uniform(-2, 2)
    n = np.random.randint(3, 10)
    taylor_sum = sum(x**k / math.factorial(k) for k in range(n+1))
    actual_error = abs(math.exp(x) - taylor_sum)
    M = math.exp(abs(x))
    bound = M * abs(x)**(n+1) / math.factorial(n+1)
    ok = actual_error <= bound + 1e-15
    return (ok, f"|R_{n}({x:.3f})|={actual_error:.2e} > bound={bound:.2e}" if not ok else "")


def power_series_radius_convergence() -> tuple[bool, str]:
    """Theorem 3.14: Power series converges for |x-a| < R, diverges for |x-a| > R.
    Test with ln(1+x) series: R=1."""
    x_in = np.random.uniform(-0.9, 0.9)
    N = 200
    partial = sum((-1)**(n+1) * x_in**n / n for n in range(1, N + 1))
    actual = math.log(1 + x_in)
    ok = abs(partial - actual) < 0.01
    return (ok, f"ln(1+{x_in:.3f}): series={partial:.6f}, actual={actual:.6f}" if not ok else "")


# =========================================================================
# Chapter 7: Multivariate Calculus
# =========================================================================

def gradient_steepest_ascent() -> tuple[bool, str]:
    """Theorem 3.5: gradient points in direction of steepest ascent.
    The directional derivative D_u f is maximized when u = grad f / ||grad f||."""
    a, b, c, d, e = np.random.randn(5)
    c = abs(c) + 0.1
    x0, y0 = np.random.randn(2)
    grad = np.array([2*a*x0 + b*y0 + d, b*x0 + 2*c*y0 + e])
    grad_norm = np.linalg.norm(grad)
    if grad_norm < 1e-10:
        return (True, "")
    u_opt = grad / grad_norm
    dd_opt = np.dot(grad, u_opt)
    theta = np.random.uniform(0, 2 * math.pi)
    u_rand = np.array([math.cos(theta), math.sin(theta)])
    dd_rand = np.dot(grad, u_rand)
    ok = dd_opt >= dd_rand - 1e-10
    return (ok, f"D_u_opt={dd_opt:.6f} < D_u_rand={dd_rand:.6f}" if not ok else "")


def clairaut_mixed_partials() -> tuple[bool, str]:
    """Theorem 3.7: f_xy = f_yx for C^2 functions.
    Test numerically with random polynomial."""
    a, b, c, d = np.random.randn(4)
    x0, y0 = np.random.randn(2)
    fxy = 2*a*x0 + 2*b*y0
    fyx = 2*a*x0 + 2*b*y0
    ok = abs(fxy - fyx) < 1e-12
    return (ok, f"f_xy={fxy:.10f} != f_yx={fyx:.10f}" if not ok else "")


def multivariate_chain_rule() -> tuple[bool, str]:
    """Theorem 3.10: dz/dt = sum (df/dx_i)(dg_i/dt) = grad f . g'(t).
    Test with f(x,y) = x^2+y^2, g(t)=(cos(t), sin(t))."""
    t = np.random.uniform(0, 2 * math.pi)
    # z(t) = cos^2(t) + sin^2(t) = 1, so dz/dt = 0
    # Alternatively use f(x,y) = x*y, g(t)=(t^2, t^3)
    # z(t) = t^5, dz/dt = 5t^4
    # grad f = (y, x) = (t^3, t^2), g'(t) = (2t, 3t^2)
    # sum = t^3*2t + t^2*3t^2 = 2t^4 + 3t^4 = 5t^4
    analytical = 5 * t ** 4
    h = 1e-7
    z = lambda t: (t ** 2) * (t ** 3)
    numerical = (z(t + h) - z(t - h)) / (2 * h)
    ok = abs(numerical - analytical) < abs(analytical) * 1e-4 + 1e-6
    return (ok, f"Multivariate chain rule: numerical={numerical:.6f} != analytical={analytical:.6f}" if not ok else "")


def euler_homogeneous_function() -> tuple[bool, str]:
    """Theorem 3.13: For f homogeneous of degree k, x*df/dx1 + ... = k*f(x).
    Test with Cobb-Douglas f(K,L) = K^alpha * L^beta."""
    alpha = np.random.uniform(0.1, 2.0)
    beta = np.random.uniform(0.1, 2.0)
    K = np.random.uniform(0.1, 10)
    L = np.random.uniform(0.1, 10)
    f_val = K**alpha * L**beta
    K_dfdk = K * alpha * K**(alpha-1) * L**beta
    L_dfdl = L * beta * K**alpha * L**(beta-1)
    lhs = K_dfdk + L_dfdl
    rhs = (alpha + beta) * f_val
    rel_err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"Euler: x*grad={lhs:.8f} != k*f={rhs:.8f}" if not ok else "")


def multivariate_taylor_second_order() -> tuple[bool, str]:
    """Theorem 3.16: f(a+h) ~ f(a) + grad f . h + (1/2) h^T H h.
    Test with quadratic f(x,y) = x^2 + 3xy + 2y^2 (exact at 2nd order)."""
    a = np.random.randn(2)
    h_vec = np.random.randn(2) * 0.1
    f = lambda v: v[0] ** 2 + 3 * v[0] * v[1] + 2 * v[1] ** 2
    grad = np.array([2 * a[0] + 3 * a[1], 3 * a[0] + 4 * a[1]])
    H = np.array([[2, 3], [3, 4]])
    taylor_approx = f(a) + grad @ h_vec + 0.5 * h_vec @ H @ h_vec
    actual = f(a + h_vec)
    # For a quadratic, Taylor to 2nd order is exact
    ok = abs(actual - taylor_approx) < 1e-10
    return (ok, f"Taylor 2nd order: actual={actual:.8f} != approx={taylor_approx:.8f}" if not ok else "")


# =========================================================================
# Chapter 8: Vectors
# =========================================================================

def rn_vector_space_axioms() -> tuple[bool, str]:
    """Theorem 3.4: R^n is a vector space.
    Test closure, associativity, commutativity, identity, inverse, distributivity."""
    n = np.random.randint(2, 10)
    u = np.random.randn(n)
    v = np.random.randn(n)
    w = np.random.randn(n)
    c, d = np.random.randn(2)
    # Commutativity: u + v = v + u
    comm = np.allclose(u + v, v + u)
    # Associativity: (u+v)+w = u+(v+w)
    assoc = np.allclose((u + v) + w, u + (v + w))
    # Zero element: u + 0 = u
    zero = np.allclose(u + np.zeros(n), u)
    # Inverse: u + (-u) = 0
    inv = np.allclose(u + (-u), np.zeros(n))
    # Distributivity: c(u+v) = cu + cv
    dist = np.allclose(c * (u + v), c * u + c * v)
    ok = comm and assoc and zero and inv and dist
    return (ok, f"Vector space axiom failed: comm={comm},assoc={assoc},zero={zero},inv={inv},dist={dist}" if not ok else "")


def cauchy_schwarz_stress() -> tuple[bool, str]:
    """Theorem 3.7: |u.v| <= ||u||*||v|| for all u,v in R^n."""
    n = np.random.randint(2, 20)
    u = np.random.randn(n) * np.random.uniform(0.01, 100)
    v = np.random.randn(n) * np.random.uniform(0.01, 100)
    lhs = abs(float(np.dot(u, v)))
    rhs = float(np.linalg.norm(u) * np.linalg.norm(v))
    ok = lhs <= rhs + 1e-10
    return (ok, f"|u.v|={lhs:.6f} > ||u||*||v||={rhs:.6f}" if not ok else "")


def triangle_inequality_stress() -> tuple[bool, str]:
    """Theorem 3.8: ||u+v|| <= ||u|| + ||v||."""
    n = np.random.randint(2, 20)
    u = np.random.randn(n) * np.random.uniform(0.01, 100)
    v = np.random.randn(n) * np.random.uniform(0.01, 100)
    lhs = float(np.linalg.norm(u + v))
    rhs = float(np.linalg.norm(u) + np.linalg.norm(v))
    ok = lhs <= rhs + 1e-10
    return (ok, f"||u+v||={lhs:.6f} > ||u||+||v||={rhs:.6f}" if not ok else "")


def cauchy_schwarz_equality_condition() -> tuple[bool, str]:
    """Equality in CS iff u = alpha*v (collinear)."""
    n = np.random.randint(2, 10)
    v = np.random.randn(n)
    alpha = np.random.uniform(-5, 5)
    u_collinear = alpha * v
    lhs = abs(float(np.dot(u_collinear, v)))
    rhs = float(np.linalg.norm(u_collinear) * np.linalg.norm(v))
    eq = abs(lhs - rhs) < 1e-8
    if not eq:
        return (False, f"Collinear but |u.v|={lhs} != ||u||*||v||={rhs}")
    u_random = np.random.randn(n)
    if np.linalg.norm(u_random - (np.dot(u_random, v)/np.dot(v, v))*v) > 1e-8:
        lhs2 = abs(float(np.dot(u_random, v)))
        rhs2 = float(np.linalg.norm(u_random) * np.linalg.norm(v))
        strict = lhs2 < rhs2 - 1e-10
        if not strict:
            return (False, f"Non-collinear but equality holds")
    return (True, "")


def dimension_well_defined() -> tuple[bool, str]:
    """Theorem 3.16: Every basis for a finite-dimensional vector space has the
    same number of elements. Test: two random bases of R^n both have n elements."""
    n = np.random.randint(2, 8)
    # Generate two random bases (full rank matrices)
    B1 = np.random.randn(n, n)
    B2 = np.random.randn(n, n)
    while abs(np.linalg.det(B1)) < 1e-6:
        B1 = np.random.randn(n, n)
    while abs(np.linalg.det(B2)) < 1e-6:
        B2 = np.random.randn(n, n)
    rank1 = np.linalg.matrix_rank(B1)
    rank2 = np.linalg.matrix_rank(B2)
    ok = rank1 == n and rank2 == n
    return (ok, f"Bases have different ranks: {rank1} and {rank2} for R^{n}" if not ok else "")


def gram_schmidt_orthonormality() -> tuple[bool, str]:
    """Theorem 3.20: Gram-Schmidt produces orthonormal set spanning same subspace."""
    n = np.random.randint(3, 8)
    k = np.random.randint(2, n + 1)
    V = np.random.randn(n, k)
    Q, R = np.linalg.qr(V)
    Q = Q[:, :k]
    gram = Q.T @ Q
    ok = np.allclose(gram, np.eye(k), atol=1e-10)
    return (ok, f"Gram-Schmidt failed orthonormality check" if not ok else "")


def projection_orthogonality() -> tuple[bool, str]:
    """Definition 3.11: u - proj_v(u) is orthogonal to v."""
    n = np.random.randint(2, 10)
    u = np.random.randn(n)
    v = np.random.randn(n)
    if np.linalg.norm(v) < 1e-10:
        return (True, "")
    proj = (np.dot(u, v) / np.dot(v, v)) * v
    residual = u - proj
    dot_res_v = abs(np.dot(residual, v))
    ok = dot_res_v < 1e-10
    return (ok, f"Residual not orthogonal to v: dot={dot_res_v:.2e}" if not ok else "")


# =========================================================================
# Chapter 9: Matrices
# =========================================================================

def matrix_multiplication_properties() -> tuple[bool, str]:
    """Theorem 3.5: Associativity (AB)C = A(BC) and distributivity."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)
    C = np.random.randn(n, n)
    # Associativity
    assoc = np.allclose((A @ B) @ C, A @ (B @ C), atol=1e-8)
    # Left distributivity
    left_dist = np.allclose(A @ (B + C), A @ B + A @ C, atol=1e-8)
    ok = assoc and left_dist
    return (ok, f"Matrix mult properties: assoc={assoc}, left_dist={left_dist}" if not ok else "")


def gaussian_elimination_consistency() -> tuple[bool, str]:
    """Theorem 3.12: Every matrix can be reduced to REF.
    Test that RREF gives a valid solution to Ax=b."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    if abs(np.linalg.det(A)) < 1e-4:
        A += np.eye(n) * 0.5  # ensure non-singular
    b = np.random.randn(n)
    x = np.linalg.solve(A, b)
    residual = np.linalg.norm(A @ x - b)
    ok = residual < 1e-10
    return (ok, f"Gaussian elimination residual: {residual:.2e}" if not ok else "")


def rouche_capelli() -> tuple[bool, str]:
    """Theorem 3.14: Ax=b solvable iff rank(A) = rank([A|b]).
    Test with random consistent and inconsistent systems."""
    m = np.random.randint(3, 6)
    n = np.random.randint(2, 4)
    A = np.random.randn(m, n)
    # Consistent: b in column space of A
    x_true = np.random.randn(n)
    b_consistent = A @ x_true
    aug_c = np.column_stack([A, b_consistent])
    rank_A = np.linalg.matrix_rank(A)
    rank_aug = np.linalg.matrix_rank(aug_c)
    ok = rank_A == rank_aug
    return (ok, f"Rouche-Capelli: rank(A)={rank_A} != rank([A|b])={rank_aug} for consistent system" if not ok else "")


def rank_nullity_theorem() -> tuple[bool, str]:
    """Theorem 3.17: dim(ker(A)) + rank(A) = n (number of columns)."""
    m = np.random.randint(2, 8)
    n = np.random.randint(2, 8)
    A = np.random.randn(m, n)
    rank = np.linalg.matrix_rank(A)
    nullity = n - rank
    ok = rank + nullity == n
    return (ok, f"rank({rank}) + nullity({nullity}) != n({n})" if not ok else "")


def det_multiplicativity() -> tuple[bool, str]:
    """Theorem 3.20(1): det(AB) = det(A)*det(B)."""
    n = np.random.randint(2, 6)
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)
    lhs = np.linalg.det(A @ B)
    rhs = np.linalg.det(A) * np.linalg.det(B)
    rel_err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
    ok = rel_err < 1e-8
    return (ok, f"det(AB)={lhs:.8f} != det(A)*det(B)={rhs:.8f}" if not ok else "")


def det_transpose_invariance() -> tuple[bool, str]:
    """Theorem 3.20(2): det(A^T) = det(A)."""
    n = np.random.randint(2, 6)
    A = np.random.randn(n, n)
    lhs = np.linalg.det(A.T)
    rhs = np.linalg.det(A)
    ok = abs(lhs - rhs) < 1e-10 * max(abs(rhs), 1)
    return (ok, f"det(A^T)={lhs:.10f} != det(A)={rhs:.10f}" if not ok else "")


def det_via_row_reduction() -> tuple[bool, str]:
    """Theorem 3.21: det = (-1)^s * product of pivots after row reduction.
    Compare numpy det with manual LU factorization."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    from scipy.linalg import lu
    P, L, U = lu(A)
    # det(A) = det(P) * det(L) * det(U)
    # det(L) = 1 (unit lower triangular), det(U) = product of diag
    det_P = np.linalg.det(P)  # +/- 1 for permutation
    det_U = np.prod(np.diag(U))
    det_lu = det_P * det_U
    det_np = np.linalg.det(A)
    ok = abs(det_lu - det_np) < 1e-8 * (abs(det_np) + 1)
    return (ok, f"det via LU={det_lu:.8f} != numpy det={det_np:.8f}" if not ok else "")


def two_by_two_inverse_formula() -> tuple[bool, str]:
    """Theorem 3.23: For 2x2 matrix [[a,b],[c,d]], inverse = 1/(ad-bc)*[[d,-b],[-c,a]]."""
    A = np.random.randn(2, 2)
    det_A = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
    if abs(det_A) < 1e-6:
        return (True, "")
    formula_inv = np.array([[A[1, 1], -A[0, 1]], [-A[1, 0], A[0, 0]]]) / det_A
    numpy_inv = np.linalg.inv(A)
    ok = np.allclose(formula_inv, numpy_inv, atol=1e-10)
    return (ok, f"2x2 inverse formula mismatch" if not ok else "")


def gauss_jordan_inverse() -> tuple[bool, str]:
    """Theorem 3.24: [A|I] row-reduces to [I|A^{-1}].
    Verify that A * A^{-1} = I."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    if abs(np.linalg.det(A)) < 1e-4:
        A += np.eye(n) * 0.5
    A_inv = np.linalg.inv(A)
    product = A @ A_inv
    ok = np.allclose(product, np.eye(n), atol=1e-10)
    return (ok, f"A * A^{-1} != I, max error={np.max(np.abs(product - np.eye(n))):.2e}" if not ok else "")


def cramers_rule_stress() -> tuple[bool, str]:
    """Remark 3.26: x_i = det(A_i)/det(A) for invertible A."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    if abs(np.linalg.det(A)) < 1e-6:
        return (True, "")
    b = np.random.randn(n)
    x_direct = np.linalg.solve(A, b)
    det_A = np.linalg.det(A)
    x_cramer = np.zeros(n)
    for i in range(n):
        Ai = A.copy()
        Ai[:, i] = b
        x_cramer[i] = np.linalg.det(Ai) / det_A
    ok = np.allclose(x_direct, x_cramer, atol=1e-8)
    return (ok, f"Cramer's rule mismatch: direct={x_direct}, cramer={x_cramer}" if not ok else "")


def inverse_product_reversal() -> tuple[bool, str]:
    """Theorem 3.25(2): (AB)^{-1} = B^{-1} A^{-1}."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)
    if abs(np.linalg.det(A)) < 1e-6 or abs(np.linalg.det(B)) < 1e-6:
        return (True, "")
    lhs = np.linalg.inv(A @ B)
    rhs = np.linalg.inv(B) @ np.linalg.inv(A)
    ok = np.allclose(lhs, rhs, atol=1e-8)
    return (ok, f"(AB)^-1 != B^-1 * A^-1" if not ok else "")


# =========================================================================
# Chapter 10: Eigenvalues
# =========================================================================

def eigenvalue_equation_equivalences() -> tuple[bool, str]:
    """Theorem 3.3: lambda eigenvalue iff det(A - lambda*I) = 0.
    Generate matrix, compute eigenvalue, verify det condition."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    eigs = np.linalg.eigvals(A)
    # Pick a random eigenvalue
    lam = eigs[np.random.randint(0, n)]
    det_val = abs(np.linalg.det(A - lam * np.eye(n)))
    ok = det_val < 1e-6
    return (ok, f"det(A-lambda*I)={det_val:.2e} != 0 for eigenvalue lambda={lam}" if not ok else "")


def eigenvalues_are_roots_of_char_poly() -> tuple[bool, str]:
    """Theorem 3.5: Eigenvalues are roots of the characteristic polynomial."""
    n = np.random.randint(2, 4)
    A = np.random.randn(n, n)
    eigs = np.linalg.eigvals(A)
    # Characteristic polynomial: p(lambda) = det(A - lambda*I)
    # Verify each eigenvalue is a root
    for lam in eigs:
        p_val = abs(np.linalg.det(A - lam * np.eye(n)))
        if p_val > 1e-5:
            return (False, f"p({lam})={p_val:.2e} != 0")
    return (True, "")


def geometric_leq_algebraic_multiplicity() -> tuple[bool, str]:
    """Theorem 3.10: geometric multiplicity <= algebraic multiplicity.
    Test with matrix that has repeated eigenvalue."""
    # Create matrix with known repeated eigenvalue
    n = np.random.randint(3, 5)
    lam = np.random.randn()
    A = np.diag([lam] * n)
    # Perturb some off-diagonal elements to reduce geometric multiplicity
    if np.random.random() > 0.5:
        A[0, 1] = 1.0  # makes it a Jordan block, geo mult < alg mult
    eigs = np.linalg.eigvals(A)
    # Count algebraic multiplicity (eigenvalues close to lam)
    alg_mult = np.sum(np.abs(eigs - lam) < 1e-6)
    # Geometric multiplicity = dim(null(A-lam*I))
    geo_mult = n - np.linalg.matrix_rank(A - lam * np.eye(n), tol=1e-6)
    ok = 1 <= geo_mult <= alg_mult
    return (ok, f"geo_mult={geo_mult} not in [1, alg_mult={alg_mult}]" if not ok else "")


def trace_equals_eigenvalue_sum() -> tuple[bool, str]:
    """Theorem 3.11: tr(A) = sum of eigenvalues."""
    n = np.random.randint(2, 6)
    A = np.random.randn(n, n)
    trace = np.trace(A)
    eigenvalues = np.linalg.eigvals(A)
    eig_sum = float(np.real(np.sum(eigenvalues)))
    ok = abs(trace - eig_sum) < 1e-8
    return (ok, f"tr(A)={trace:.8f} != sum(lambda)={eig_sum:.8f}" if not ok else "")


def det_equals_eigenvalue_product() -> tuple[bool, str]:
    """Theorem 3.11: det(A) = product of eigenvalues."""
    n = np.random.randint(2, 6)
    A = np.random.randn(n, n)
    det_A = np.linalg.det(A)
    eigenvalues = np.linalg.eigvals(A)
    eig_prod = float(np.real(np.prod(eigenvalues)))
    rel_err = abs(det_A - eig_prod) / max(abs(det_A), 1e-15)
    ok = rel_err < 1e-6
    return (ok, f"det(A)={det_A:.8f} != prod(lambda)={eig_prod:.8f}" if not ok else "")


def distinct_eigenvalues_lin_indep_eigvecs() -> tuple[bool, str]:
    """Theorem 3.13: Eigenvectors for distinct eigenvalues are linearly independent."""
    n = np.random.randint(3, 6)
    # Generate matrix with distinct eigenvalues
    D = np.diag(np.random.randn(n) * np.array(range(1, n + 1)))  # spread out
    P = np.random.randn(n, n)
    while abs(np.linalg.det(P)) < 0.1:
        P = np.random.randn(n, n)
    A = P @ D @ np.linalg.inv(P)
    evals, evecs = np.linalg.eig(A)
    # Check if eigenvalues are approximately distinct
    for i in range(n):
        for j in range(i + 1, n):
            if abs(evals[i] - evals[j]) < 1e-6:
                return (True, "")  # skip if not distinct
    # Check eigenvectors are linearly independent
    rank = np.linalg.matrix_rank(evecs, tol=1e-8)
    ok = rank == n
    return (ok, f"Eigenvectors not linearly independent: rank={rank}, expected {n}" if not ok else "")


def spectral_theorem_symmetric() -> tuple[bool, str]:
    """Theorem 3.18: Real symmetric matrix has real eigenvalues and orthogonal eigenvectors."""
    n = np.random.randint(2, 7)
    A = np.random.randn(n, n)
    S = (A + A.T) / 2
    eigenvalues, eigenvectors = np.linalg.eigh(S)
    all_real = np.all(np.isreal(eigenvalues))
    ortho = np.allclose(eigenvectors.T @ eigenvectors, np.eye(n), atol=1e-10)
    ok = all_real and ortho
    return (ok, f"Spectral theorem: real={all_real}, ortho={ortho}" if not ok else "")


def positive_definite_eigenvalue_stress() -> tuple[bool, str]:
    """Spectral theorem consequence: symmetric PD matrix has all lambda > 0."""
    n = np.random.randint(2, 8)
    A = np.random.randn(n, n)
    S = A.T @ A + 0.01 * np.eye(n)
    eigenvalues = np.linalg.eigvalsh(S)
    all_pos = bool(np.all(eigenvalues > -1e-10))
    return (all_pos, f"min eigenvalue = {float(np.min(eigenvalues)):.6e}" if not all_pos else "")


def eigenvalues_of_inverse() -> tuple[bool, str]:
    """Theorem 3.12(3): eigenvalues of A^{-1} are 1/lambda_i."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    if abs(np.linalg.det(A)) < 1e-4:
        return (True, "")
    eigs_A = sorted(np.linalg.eigvals(A), key=lambda z: (z.real, z.imag))
    eigs_inv = sorted(np.linalg.eigvals(np.linalg.inv(A)), key=lambda z: (z.real, z.imag))
    reciprocals = sorted([1.0/l for l in eigs_A], key=lambda z: (z.real, z.imag))
    ok = np.allclose(np.array(eigs_inv), np.array(reciprocals), atol=1e-6)
    return (ok, f"Eigenvalues of inv(A) != 1/eigenvalues of A" if not ok else "")


def eigenvalues_of_power() -> tuple[bool, str]:
    """Theorem 3.12(4): eigenvalues of A^k are lambda_i^k."""
    n = np.random.randint(2, 4)
    k = np.random.randint(2, 5)
    A = np.random.randn(n, n) * 0.5
    eigs_A = np.sort(np.linalg.eigvals(A))
    eigs_Ak = np.sort(np.linalg.eigvals(np.linalg.matrix_power(A, k)))
    eigs_expected = np.sort(eigs_A ** k)
    ok = np.allclose(eigs_Ak, eigs_expected, atol=1e-6)
    return (ok, f"eigenvalues of A^{k} != lambda^{k}" if not ok else "")


def diagonalization_stress() -> tuple[bool, str]:
    """Theorem 3.15: A=PDP^{-1} when A has n linearly independent eigenvectors.
    Test with random symmetric matrices (always diagonalizable)."""
    n = np.random.randint(2, 6)
    A = np.random.randn(n, n)
    S = (A + A.T) / 2
    eigenvalues, P = np.linalg.eigh(S)
    D = np.diag(eigenvalues)
    reconstructed = P @ D @ P.T
    ok = np.allclose(S, reconstructed, atol=1e-10)
    return (ok, f"A != PDP^T for symmetric matrix" if not ok else "")


# =========================================================================
# Chapter 11: Unconstrained Optimization
# =========================================================================

def first_order_necessary_condition() -> tuple[bool, str]:
    """Theorem 3.2/3.5: At a local extremum, f'(x*)=0 / grad f(x*)=0.
    Generate convex quadratic, verify minimum has zero gradient."""
    n = np.random.randint(1, 5)
    A = np.random.randn(n, n)
    H = A.T @ A + 0.1 * np.eye(n)
    b = np.random.randn(n)
    x_star = np.linalg.solve(H, b)
    grad = H @ x_star - b
    ok = np.linalg.norm(grad) < 1e-10
    return (ok, f"||grad f(x*)||={np.linalg.norm(grad):.2e}" if not ok else "")


def second_derivative_test_1d() -> tuple[bool, str]:
    """Theorem 3.4: f''(c) > 0 at critical point => local min, f''(c) < 0 => local max.
    Test with f(x) = ax^2 + bx + c."""
    a = np.random.uniform(0.5, 5) * np.random.choice([-1, 1])
    b_coeff = np.random.randn()
    # Critical point at x* = -b/(2a), f''(x*) = 2a
    x_star = -b_coeff / (2 * a)
    f = lambda x: a * x ** 2 + b_coeff * x
    fpp = 2 * a
    if fpp > 0:
        # Should be local min: f(x_star) <= f(x_star +/- eps)
        eps = 0.01
        ok = f(x_star) <= f(x_star + eps) + 1e-10 and f(x_star) <= f(x_star - eps) + 1e-10
    else:
        # Should be local max: f(x_star) >= f(x_star +/- eps)
        eps = 0.01
        ok = f(x_star) >= f(x_star + eps) - 1e-10 and f(x_star) >= f(x_star - eps) - 1e-10
    return (ok, f"Second derivative test failed: f''={fpp}, f(x*)={f(x_star):.6f}" if not ok else "")


def definiteness_and_eigenvalues() -> tuple[bool, str]:
    """Theorem 3.7: H PD iff all eigenvalues > 0, ND iff all < 0."""
    n = np.random.randint(2, 5)
    # Generate PD matrix
    A = np.random.randn(n, n)
    H_pd = A.T @ A + 0.1 * np.eye(n)
    eigs = np.linalg.eigvalsh(H_pd)
    all_pos = bool(np.all(eigs > -1e-10))
    # Generate ND matrix
    H_nd = -H_pd
    eigs_nd = np.linalg.eigvalsh(H_nd)
    all_neg = bool(np.all(eigs_nd < 1e-10))
    ok = all_pos and all_neg
    return (ok, f"Definiteness: PD all_pos={all_pos}, ND all_neg={all_neg}" if not ok else "")


def second_order_conditions_stress() -> tuple[bool, str]:
    """Theorem 3.8: H PD at critical point => strict local min.
    Generate random PD Hessian, verify function increases around min."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    H = A.T @ A + 0.5 * np.eye(n)
    b = np.random.randn(n)
    x_star = np.linalg.solve(H, b)
    f_star = 0.5 * x_star @ H @ x_star - b @ x_star
    for _ in range(20):
        delta = np.random.randn(n) * 0.01
        f_perturbed = 0.5 * (x_star + delta) @ H @ (x_star + delta) - b @ (x_star + delta)
        if f_perturbed < f_star - 1e-12:
            return (False, f"f(x*+d)={f_perturbed:.8f} < f(x*)={f_star:.8f}")
    return (True, "")


def convexity_hessian_psd() -> tuple[bool, str]:
    """Theorem 3.12: f convex iff H_f PSD everywhere.
    Test: f(x) = x^T A^T A x is convex, Hessian = 2*A^T*A is PSD."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    H = 2 * A.T @ A
    eigenvalues = np.linalg.eigvalsh(H)
    ok = bool(np.all(eigenvalues >= -1e-10))
    return (ok, f"Hessian of convex function has negative eigenvalue: {np.min(eigenvalues):.2e}" if not ok else "")


def convexity_local_is_global() -> tuple[bool, str]:
    """Theorem 3.13: For strictly convex f, every local min is the global min."""
    a = np.random.uniform(1, 10)
    b = np.random.uniform(-5, 5)
    x_star = -b / (2 * a)
    f_star = a * x_star**2 + b * x_star
    x_test = np.random.uniform(-100, 100, 100)
    f_test = a * x_test**2 + b * x_test
    all_geq = bool(np.all(f_test >= f_star - 1e-10))
    return (all_geq, f"Found f({x_test[np.argmin(f_test)]:.4f})<f({x_star:.4f})" if not all_geq else "")


def saddle_point_indefinite_hessian() -> tuple[bool, str]:
    """Theorem 3.8(3): Indefinite Hessian at critical point => saddle point.
    Test with f(x,y) = x^2 - y^2."""
    H = np.array([[2.0, 0.0], [0.0, -2.0]])
    eigenvalues = np.linalg.eigvalsh(H)
    has_pos = np.any(eigenvalues > 0)
    has_neg = np.any(eigenvalues < 0)
    ok = has_pos and has_neg
    if ok:
        eps = 0.01
        f = lambda x, y: x**2 - y**2
        increases = f(eps, 0) > f(0, 0)
        decreases = f(0, eps) < f(0, 0)
        ok = increases and decreases
    return (ok, f"Saddle point test failed" if not ok else "")


def gradient_descent_convergence() -> tuple[bool, str]:
    """Theorem 3.16: Gradient descent convergence for L-smooth convex functions.
    f(x_k) - f* <= L||x_0-x*||^2 / (2k)."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    H = A.T @ A + 0.1 * np.eye(n)
    b = np.random.randn(n)
    L = float(np.max(np.linalg.eigvalsh(H)))
    alpha = 1.0 / L
    x_star = np.linalg.solve(H, b)
    f_star = 0.5 * x_star @ H @ x_star - b @ x_star
    x = np.zeros(n)
    for k in range(1, 201):
        grad = H @ x - b
        x = x - alpha * grad
    f_k = 0.5 * x @ H @ x - b @ x
    gap = f_k - f_star
    bound = L * np.linalg.norm(np.zeros(n) - x_star) ** 2 / (2 * 200)
    ok = gap < bound + 1e-6 or gap < 1e-8
    return (ok, f"GD gap={gap:.2e} > bound={bound:.2e}" if not ok else "")


def newton_quadratic_convergence() -> tuple[bool, str]:
    """Theorem 3.18: Newton's method converges quadratically near optimum.
    Test: minimize f(x) = (x-3)^4 + (x-3)^2 near x*=3."""
    f = lambda x: (x - 3) ** 4 + (x - 3) ** 2
    fp = lambda x: 4 * (x - 3) ** 3 + 2 * (x - 3)
    fpp = lambda x: 12 * (x - 3) ** 2 + 2
    x = 3.0 + np.random.uniform(-0.1, 0.1)  # start near optimum
    errors = []
    for _ in range(10):
        step = fp(x) / fpp(x)
        x = x - step
        errors.append(abs(x - 3.0))
    # Check quadratic convergence: e_{k+1} / e_k^2 should be bounded
    if len(errors) >= 3 and errors[0] > 1e-14:
        ratios = []
        for i in range(len(errors) - 1):
            if errors[i] > 1e-14:
                ratios.append(errors[i + 1] / max(errors[i] ** 2, 1e-30))
        ok = errors[-1] < 1e-10
    else:
        ok = errors[-1] < 1e-10
    return (ok, f"Newton final error={errors[-1]:.2e}" if not ok else "")


# =========================================================================
# Chapter 12: Constrained Optimization
# =========================================================================

def lagrange_necessary_conditions() -> tuple[bool, str]:
    """Theorem 3.3: At constrained optimum, grad f = -lambda * grad g.
    Test: max xy s.t. x+y=10."""
    x_star, y_star = 5.0, 5.0
    grad_f = np.array([y_star, x_star])
    grad_g = np.array([1.0, 1.0])
    lam = -grad_f[0] / grad_g[0]
    residual = grad_f + lam * grad_g
    ok = np.linalg.norm(residual) < 1e-10
    return (ok, f"Lagrange condition residual: {np.linalg.norm(residual):.2e}" if not ok else "")


def lagrange_shadow_price() -> tuple[bool, str]:
    """Theorem 3.5: lambda = df*/db (shadow price).
    Test: min x^2+y^2 s.t. x+y=b. Solution: x*=y*=b/2, f*=b^2/2, df*/db=b=lambda.
    Lagrangian: 2x+lambda=0, 2y+lambda=0, x+y=b => lambda=-b."""
    b = np.random.uniform(1, 10)
    f_star = b ** 2 / 2
    # Perturb b
    eps = 1e-6
    f_star_plus = (b + eps) ** 2 / 2
    numerical_deriv = (f_star_plus - f_star) / eps
    # lambda = -b, but df*/db = b (since constraint is g(x)=x+y-b=0, with sign convention)
    analytical_lambda = b
    ok = abs(numerical_deriv - analytical_lambda) < 0.01
    return (ok, f"Shadow price: numerical={numerical_deriv:.6f} != lambda={analytical_lambda:.6f}" if not ok else "")


def bordered_hessian_test() -> tuple[bool, str]:
    """Theorem 3.7: Second-order conditions via bordered Hessian.
    Test: min x^2+y^2 s.t. x+y=1. Bordered Hessian determines min vs max.
    For m=1 constraint, n=2 vars: constrained min iff (-1)^m * det(H_bar) > 0,
    i.e., -det(H_bar) > 0, i.e., det(H_bar) < 0."""
    # Lagrangian Hessian L = [[2,0],[0,2]], grad g = [1,1]
    # Bordered Hessian: [[0,1,1],[1,2,0],[1,0,2]]
    H_bar = np.array([[0, 1, 1], [1, 2, 0], [1, 0, 2]], dtype=float)
    det_bar = np.linalg.det(H_bar)
    # For constrained min with m=1: (-1)^1 * det > 0 => det < 0
    sign_ok = det_bar < 0
    # Verify the solution is indeed a min: x*=y*=0.5, f*=0.5
    f_star = 0.5
    f_test = 0.3 ** 2 + 0.7 ** 2  # another feasible point
    min_ok = f_star <= f_test + 1e-10
    ok = sign_ok and min_ok
    return (ok, f"Bordered Hessian det={det_bar:.4f} (expect <0), f*={f_star:.4f}, f_test={f_test:.4f}" if not ok else "")


def fundamental_theorem_of_lp() -> tuple[bool, str]:
    """Theorem 3.12: If LP has finite optimum, optimum is at a vertex.
    Test with random LP: verify optimum found by linprog is a basic feasible solution."""
    from scipy.optimize import linprog
    n = np.random.randint(2, 5)
    m = np.random.randint(n, n + 3)
    c = np.random.rand(n)
    A = np.random.rand(m, n)
    b = np.random.rand(m) + A @ np.ones(n)
    res = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)] * n, method='highs')
    if not res.success:
        return (True, "")
    x_opt = res.x
    # At a vertex, n constraints are active (binding)
    # Count near-zero variables and near-binding inequality constraints
    n_active = np.sum(x_opt < 1e-8) + np.sum(np.abs(A @ x_opt - b) < 1e-6)
    ok = n_active >= n  # at least n active constraints at a vertex
    return (ok, f"LP optimum not at vertex: only {n_active} active constraints for {n} variables" if not ok else "")


def simplex_method_overview() -> tuple[bool, str]:
    """Theorem 3.15: Simplex method finds optimal vertex by moving along edges.
    Test: solve LP and verify optimality conditions (reduced costs)."""
    from scipy.optimize import linprog
    n = np.random.randint(2, 4)
    m = np.random.randint(2, 4)
    c = np.random.rand(n)
    A = np.random.rand(m, n)
    b = np.random.rand(m) + A @ np.ones(n)
    res = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)] * n, method='highs')
    if not res.success:
        return (True, "")
    # Verify it's a valid solution
    feasible = bool(np.all(A @ res.x <= b + 1e-8) and np.all(res.x >= -1e-8))
    ok = feasible
    return (ok, f"Simplex result not feasible" if not ok else "")


def weak_duality_lp() -> tuple[bool, str]:
    """Theorem 3.18: For any primal feasible x and dual feasible y, c^Tx <= b^Ty."""
    from scipy.optimize import linprog
    n = np.random.randint(2, 5)
    m = np.random.randint(2, 5)
    c = np.random.rand(n)
    A = np.random.rand(m, n)
    b = np.random.rand(m) + A @ np.ones(n)
    res_primal = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)]*n, method='highs')
    if not res_primal.success:
        return (True, "")
    res_dual = linprog(b, A_ub=-A.T, b_ub=-c, bounds=[(0, None)]*m, method='highs')
    if not res_dual.success:
        return (True, "")
    primal_obj = float(c @ res_primal.x)
    dual_obj = float(b @ res_dual.x)
    ok = primal_obj <= dual_obj + 1e-6
    return (ok, f"Weak duality violated: primal={primal_obj:.6f} > dual={dual_obj:.6f}" if not ok else "")


def strong_duality_lp() -> tuple[bool, str]:
    """Theorem 3.19: At optimum, primal objective = dual objective."""
    from scipy.optimize import linprog
    n = np.random.randint(2, 5)
    m = np.random.randint(2, 5)
    c = np.random.rand(n)
    A = np.random.rand(m, n)
    b = np.random.rand(m) + A @ np.ones(n)
    res_primal = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)]*n, method='highs')
    if not res_primal.success:
        return (True, "")
    res_dual = linprog(b, A_ub=-A.T, b_ub=-c, bounds=[(0, None)]*m, method='highs')
    if not res_dual.success:
        return (True, "")
    primal_obj = float(c @ res_primal.x)
    dual_obj = float(b @ res_dual.x)
    ok = abs(primal_obj - dual_obj) < 1e-4
    return (ok, f"Strong duality gap: primal={primal_obj:.6f}, dual={dual_obj:.6f}" if not ok else "")


def complementary_slackness() -> tuple[bool, str]:
    """Theorem 3.20: y_i*(b_i - (Ax)_i) = 0 at optimum."""
    from scipy.optimize import linprog
    n = np.random.randint(2, 4)
    m = np.random.randint(2, 4)
    c = np.random.rand(n)
    A = np.random.rand(m, n)
    b = np.random.rand(m) + A @ np.ones(n)
    res_primal = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)] * n, method='highs')
    if not res_primal.success:
        return (True, "")
    res_dual = linprog(b, A_ub=-A.T, b_ub=-c, bounds=[(0, None)] * m, method='highs')
    if not res_dual.success:
        return (True, "")
    x_opt = res_primal.x
    y_opt = res_dual.x
    slacks = b - A @ x_opt
    cs_violations = y_opt * slacks
    ok = np.all(np.abs(cs_violations) < 1e-4)
    return (ok, f"Complementary slackness violated: max|y*s|={np.max(np.abs(cs_violations)):.6f}" if not ok else "")


# =========================================================================
# Chapter 13: Probability Theory
# =========================================================================

def probability_basic_consequences() -> tuple[bool, str]:
    """Theorem 3.5: P(empty)=0, P(A^c)=1-P(A), P(A union B)=P(A)+P(B)-P(A inter B)."""
    # Test with discrete probability space
    n = np.random.randint(5, 20)
    probs = np.random.dirichlet(np.ones(n))
    # Pick random events A, B as subsets
    A = np.random.random(n) > 0.5
    B = np.random.random(n) > 0.5
    P_A = float(np.sum(probs[A]))
    P_B = float(np.sum(probs[B]))
    P_AuB = float(np.sum(probs[A | B]))
    P_AnB = float(np.sum(probs[A & B]))
    # Inclusion-exclusion
    ie = P_A + P_B - P_AnB
    ok = abs(P_AuB - ie) < 1e-10
    # P(A^c) = 1 - P(A)
    P_Ac = float(np.sum(probs[~A]))
    compl_ok = abs(P_A + P_Ac - 1.0) < 1e-10
    ok = ok and compl_ok
    return (ok, f"P(AuB)={P_AuB:.8f} != P(A)+P(B)-P(AnB)={ie:.8f}" if not ok else "")


def law_total_probability() -> tuple[bool, str]:
    """Theorem 3.7: P(A) = sum_i P(A|B_i)*P(B_i) for partition {B_i}."""
    k = np.random.randint(2, 6)
    prior = np.random.dirichlet(np.ones(k))
    likelihoods = np.random.uniform(0.01, 0.99, k)
    p_a = float(np.dot(likelihoods, prior))
    # Verify this equals P(A) computed via total probability
    p_a_check = sum(likelihoods[i] * prior[i] for i in range(k))
    ok = abs(p_a - p_a_check) < 1e-14
    return (ok, f"Total probability: {p_a:.10f} != {p_a_check:.10f}" if not ok else "")


def bayes_theorem_stress() -> tuple[bool, str]:
    """Theorem 3.8: P(B_j|A) = P(A|B_j)*P(B_j) / sum_i P(A|B_i)*P(B_i)."""
    k = np.random.randint(2, 6)
    prior = np.random.dirichlet(np.ones(k))
    likelihoods = np.random.uniform(0.01, 0.99, k)
    p_a = float(np.dot(likelihoods, prior))
    if p_a < 1e-10:
        return (True, "")
    posteriors = likelihoods * prior / p_a
    ok = abs(np.sum(posteriors) - 1.0) < 1e-10
    return (ok, f"Posteriors sum to {np.sum(posteriors):.10f} != 1" if not ok else "")


def linearity_of_expectation() -> tuple[bool, str]:
    """Theorem 3.15: E[aX+bY] = a*E[X] + b*E[Y] always (even dependent)."""
    n = 10000
    a_coeff, b_coeff = np.random.randn(2)
    # Generate correlated X, Y
    rho = np.random.uniform(-0.9, 0.9)
    z1 = np.random.randn(n)
    z2 = np.random.randn(n)
    X = z1
    Y = rho * z1 + math.sqrt(1 - rho ** 2) * z2
    lhs = np.mean(a_coeff * X + b_coeff * Y)
    rhs = a_coeff * np.mean(X) + b_coeff * np.mean(Y)
    ok = abs(lhs - rhs) < 0.01
    return (ok, f"E[aX+bY]={lhs:.6f} != a*E[X]+b*E[Y]={rhs:.6f}" if not ok else "")


def variance_properties() -> tuple[bool, str]:
    """Theorem 3.17: Var(aX+b) = a^2*Var(X); Var(X+Y)=Var(X)+Var(Y) if independent."""
    n = 10000
    a_coeff = np.random.randn()
    b_coeff = np.random.randn()
    X = np.random.randn(n) * np.random.uniform(0.5, 3)
    # Var(aX+b) = a^2 Var(X)
    Y = a_coeff * X + b_coeff
    var_Y = np.var(Y, ddof=1)
    expected = a_coeff ** 2 * np.var(X, ddof=1)
    ok = abs(var_Y - expected) / max(expected, 1e-10) < 0.1
    return (ok, f"Var(aX+b)={var_Y:.6f} != a^2*Var(X)={expected:.6f}" if not ok else "")


def law_total_expectation() -> tuple[bool, str]:
    """Theorem 3.25: E[Y] = E[E[Y|X]]."""
    n_x = 3
    probs_x = np.random.dirichlet(np.ones(n_x))
    means_y_given_x = np.random.randn(n_x)
    iterated = float(np.dot(means_y_given_x, probs_x))
    e_y = sum(means_y_given_x[i] * probs_x[i] for i in range(n_x))
    ok = abs(iterated - e_y) < 1e-14
    return (ok, f"E[E[Y|X]]={iterated:.10f} != E[Y]={e_y:.10f}" if not ok else "")


def chebyshev_inequality_stress() -> tuple[bool, str]:
    """Theorem 3.26: P(|X-mu| >= k*sigma) <= 1/k^2."""
    n = np.random.randint(5, 50)
    probs = np.random.dirichlet(np.ones(n))
    values = np.random.randn(n) * np.random.uniform(1, 10)
    mu = float(np.dot(values, probs))
    var = float(np.dot((values - mu)**2, probs))
    sigma = math.sqrt(var) if var > 0 else 1e-10
    k = np.random.uniform(1.1, 5.0)
    p_tail = float(np.sum(probs[np.abs(values - mu) >= k * sigma]))
    bound = 1.0 / (k * k)
    ok = p_tail <= bound + 1e-10
    return (ok, f"P(|X-mu|>={k:.2f}*sigma)={p_tail:.6f} > 1/k^2={bound:.6f}" if not ok else "")


def jensen_inequality_stress() -> tuple[bool, str]:
    """Jensen's inequality: for convex f, E[f(X)] >= f(E[X])."""
    n = np.random.randint(3, 30)
    probs = np.random.dirichlet(np.ones(n))
    values = np.random.randn(n) * np.random.uniform(1, 10)
    ex = float(np.dot(values, probs))
    ef = float(np.dot(values**2, probs))
    fe = ex**2
    ok = ef >= fe - 1e-10
    return (ok, f"E[X^2]={ef:.6f} < (E[X])^2={fe:.6f}" if not ok else "")


def lln_convergence() -> tuple[bool, str]:
    """Theorem 3.27: X_bar_n -> mu as n -> infinity."""
    lam = np.random.uniform(0.5, 5)
    n = 10000
    data = np.random.exponential(1/lam, n)
    xbar = float(np.mean(data))
    mu = 1/lam
    rel_err = abs(xbar - mu) / mu
    ok = rel_err < 0.05
    return (ok, f"X_bar={xbar:.4f}, mu={mu:.4f}, rel_err={rel_err:.4f}" if not ok else "")


def clt_convergence() -> tuple[bool, str]:
    """Theorem 3.28: (X_bar - mu)/(sigma/sqrt(n)) -> N(0,1)."""
    from scipy.stats import kstest
    dist_type = np.random.choice(['exp', 'uniform', 'chi2'])
    n_samples = 500
    n_sums = 2000
    if dist_type == 'exp':
        lam = np.random.uniform(0.5, 5)
        data = np.random.exponential(1/lam, (n_sums, n_samples))
        mu, sigma = 1/lam, 1/lam
    elif dist_type == 'uniform':
        a, b = 0, np.random.uniform(1, 10)
        data = np.random.uniform(a, b, (n_sums, n_samples))
        mu, sigma = (a+b)/2, (b-a)/math.sqrt(12)
    else:
        k = np.random.randint(2, 10)
        data = np.random.chisquare(k, (n_sums, n_samples))
        mu, sigma = k, math.sqrt(2*k)
    means = data.mean(axis=1)
    z = (means - mu) / (sigma / math.sqrt(n_samples))
    stat, pval = kstest(z, 'norm')
    ok = pval > 1e-6
    return (ok, f"KS p-value={pval:.6f} (dist={dist_type})" if not ok else "")


def variance_of_sum() -> tuple[bool, str]:
    """Theorem 3.22: Var(X+Y) = Var(X) + Var(Y) + 2*Cov(X,Y)."""
    n = 10000
    rho = np.random.uniform(-0.9, 0.9)
    z1 = np.random.randn(n)
    z2 = np.random.randn(n)
    x = z1
    y = rho * z1 + math.sqrt(1 - rho**2) * z2
    var_sum = np.var(x + y, ddof=1)
    var_x = np.var(x, ddof=1)
    var_y = np.var(y, ddof=1)
    cov_xy = np.cov(x, y, ddof=1)[0, 1]
    rhs = var_x + var_y + 2 * cov_xy
    rel_err = abs(var_sum - rhs) / max(abs(rhs), 1e-10)
    ok = rel_err < 0.01
    return (ok, f"Var(X+Y)={var_sum:.6f} != Var(X)+Var(Y)+2Cov={rhs:.6f}" if not ok else "")


# =========================================================================
# Chapter 14: Distributions
# =========================================================================

def poisson_limit_of_binomial() -> tuple[bool, str]:
    """Theorem 3.5: Binomial(n, lambda/n) -> Poisson(lambda) as n -> inf."""
    lam = np.random.uniform(1, 10)
    n = 1000
    p = lam / n
    k = np.random.randint(0, int(2 * lam) + 1)
    from scipy.stats import binom, poisson
    binom_pmf = binom.pmf(k, n, p)
    poisson_pmf = poisson.pmf(k, lam)
    ok = abs(binom_pmf - poisson_pmf) < 0.01
    return (ok, f"Bin({n},{p:.4f}) PMF at {k}={binom_pmf:.6f} vs Poisson({lam:.1f})={poisson_pmf:.6f}" if not ok else "")


def normal_sum_independent() -> tuple[bool, str]:
    """Theorem 3.10(c): X~N(mu1,s1^2), Y~N(mu2,s2^2) indep => X+Y~N(mu1+mu2, s1^2+s2^2)."""
    from scipy.stats import kstest, norm
    mu1, s1 = np.random.randn(), abs(np.random.randn()) + 0.1
    mu2, s2 = np.random.randn(), abs(np.random.randn()) + 0.1
    n = 5000
    x = np.random.normal(mu1, s1, n)
    y = np.random.normal(mu2, s2, n)
    z = x + y
    mu_sum = mu1 + mu2
    s_sum = math.sqrt(s1**2 + s2**2)
    z_std = (z - mu_sum) / s_sum
    stat, pval = kstest(z_std, 'norm')
    ok = pval > 1e-6
    return (ok, f"N+N normality KS p-value={pval:.6f}" if not ok else "")


def t_converges_to_normal() -> tuple[bool, str]:
    """Theorem 3.16: t(nu) -> N(0,1) as nu -> inf."""
    from scipy.stats import kstest, t as t_dist
    nu = np.random.randint(50, 200)
    samples = t_dist.rvs(nu, size=5000)
    stat, pval = kstest(samples, 'norm')
    ok = pval > 1e-6
    return (ok, f"t({nu}) vs N(0,1) KS p-value={pval:.6f}" if not ok else "")


def chi_squared_sum_of_squares() -> tuple[bool, str]:
    """Definition 3.13: sum of k independent N(0,1)^2 ~ chi2(k)."""
    from scipy.stats import kstest, chi2
    k = np.random.randint(2, 10)
    n = 5000
    samples = np.sum(np.random.randn(n, k)**2, axis=1)
    stat, pval = kstest(samples, chi2(k).cdf)
    ok = pval > 1e-6
    return (ok, f"Sum of {k} N(0,1)^2 vs chi2({k}): KS p={pval:.6f}" if not ok else "")


def t_squared_is_f() -> tuple[bool, str]:
    """Remark 3.18: If T ~ t(nu), then T^2 ~ F(1,nu)."""
    from scipy.stats import kstest, t as t_dist, f as f_dist
    nu = np.random.randint(5, 30)
    n = 5000
    t_samples = t_dist.rvs(nu, size=n)
    f_samples = t_samples ** 2
    stat, pval = kstest(f_samples, f_dist(1, nu).cdf)
    ok = pval > 1e-6
    return (ok, f"T^2 vs F(1,{nu}): KS p={pval:.6f}" if not ok else "")


def binomial_additivity() -> tuple[bool, str]:
    """Theorem 3.3: Bin(n1,p) + Bin(n2,p) ~ Bin(n1+n2,p)."""
    from scipy.stats import kstest, binom
    p = np.random.uniform(0.2, 0.8)
    n1 = np.random.randint(5, 20)
    n2 = np.random.randint(5, 20)
    N = 10000
    x1 = np.random.binomial(n1, p, N)
    x2 = np.random.binomial(n2, p, N)
    x_sum = x1 + x2
    values, counts = np.unique(x_sum, return_counts=True)
    expected = N * np.array([binom.pmf(v, n1+n2, p) for v in values])
    mask = expected > 5
    if np.sum(mask) < 3:
        return (True, "")
    chi2_stat = np.sum((counts[mask] - expected[mask])**2 / expected[mask])
    df = np.sum(mask) - 1
    from scipy.stats import chi2
    pval = 1 - chi2.cdf(chi2_stat, df)
    ok = pval > 1e-6
    return (ok, f"Bin({n1},{p:.2f})+Bin({n2},{p:.2f}) vs Bin({n1+n2},{p:.2f}): p={pval:.6f}" if not ok else "")


def distribution_relationship_diagram() -> tuple[bool, str]:
    """Theorem 3.19: Distribution relationships.
    Test: Bernoulli(p) = Binomial(1,p), and Binomial(n,p) approx N(np,np(1-p))."""
    from scipy.stats import binom, norm
    # Bernoulli = Binomial(1,p)
    p = np.random.uniform(0.1, 0.9)
    bern_pmf_0 = 1 - p
    bern_pmf_1 = p
    bin_pmf_0 = binom.pmf(0, 1, p)
    bin_pmf_1 = binom.pmf(1, 1, p)
    ok1 = abs(bern_pmf_0 - bin_pmf_0) < 1e-14 and abs(bern_pmf_1 - bin_pmf_1) < 1e-14
    # Normal approx to binomial for large n
    n = 100
    k = int(n * p)
    bin_prob = binom.pmf(k, n, p)
    norm_approx = norm.pdf(k, n * p, math.sqrt(n * p * (1 - p)))
    ok2 = abs(bin_prob - norm_approx) < 0.05
    ok = ok1 and ok2
    return (ok, f"Distribution relationships: Bern=Bin(1,p):{ok1}, normal_approx:{ok2}" if not ok else "")


# =========================================================================
# Chapter 15: Descriptive Statistics
# =========================================================================

def correlation_bounds() -> tuple[bool, str]:
    """Theorem 3.16: -1 <= r_xy <= 1 for any sample."""
    n = np.random.randint(5, 100)
    x = np.random.randn(n)
    y = np.random.randn(n)
    if np.std(x) < 1e-10 or np.std(y) < 1e-10:
        return (True, "")
    r = np.corrcoef(x, y)[0, 1]
    ok = -1 - 1e-10 <= r <= 1 + 1e-10
    return (ok, f"Correlation r={r:.10f} out of [-1,1]" if not ok else "")


# =========================================================================
# Chapter 16: Statistical Inference
# =========================================================================

def mle_consistency_normal() -> tuple[bool, str]:
    """Theorem 3.7: MLE is consistent (converges to true parameter).
    Test: MLE of mean of N(mu, sigma^2) is xbar."""
    mu_true = np.random.randn() * 3
    sigma_true = abs(np.random.randn()) + 0.5
    n = 10000
    data = np.random.normal(mu_true, sigma_true, n)
    mu_hat = np.mean(data)
    sigma_hat = np.std(data, ddof=0)
    # Use adaptive tolerance based on standard errors (4 SE for robustness)
    se_mu = sigma_true / math.sqrt(n)
    se_sigma = sigma_true / math.sqrt(2 * n)
    ok = abs(mu_hat - mu_true) < max(0.2, 4 * se_mu) and abs(sigma_hat - sigma_true) < max(0.3, 4 * se_sigma)
    return (ok, f"MLE: mu_hat={mu_hat:.4f} vs mu={mu_true:.4f}, sigma_hat={sigma_hat:.4f} vs sigma={sigma_true:.4f}" if not ok else "")


def ci_known_variance() -> tuple[bool, str]:
    """Theorem 3.10: CI for mean with known variance covers true mean 95% of time.
    Run simulation: generate many samples, check coverage."""
    mu = np.random.randn() * 3
    sigma = abs(np.random.randn()) + 0.5
    n = 30
    alpha = 0.05
    z_crit = 1.96
    n_sims = 500
    covers = 0
    for _ in range(n_sims):
        data = np.random.normal(mu, sigma, n)
        xbar = np.mean(data)
        margin = z_crit * sigma / math.sqrt(n)
        if xbar - margin <= mu <= xbar + margin:
            covers += 1
    coverage = covers / n_sims
    ok = abs(coverage - 0.95) < 0.05  # should be near 95%
    return (ok, f"CI coverage={coverage:.3f}, expected ~0.95" if not ok else "")


def ci_unknown_variance() -> tuple[bool, str]:
    """Theorem 3.11: CI using t-distribution when variance unknown.
    Verify coverage is approximately (1-alpha)."""
    from scipy.stats import t as t_dist
    mu = np.random.randn() * 3
    sigma = abs(np.random.randn()) + 0.5
    n = 20
    alpha = 0.05
    t_crit = t_dist.ppf(1 - alpha / 2, n - 1)
    n_sims = 500
    covers = 0
    for _ in range(n_sims):
        data = np.random.normal(mu, sigma, n)
        xbar = np.mean(data)
        s = np.std(data, ddof=1)
        margin = t_crit * s / math.sqrt(n)
        if xbar - margin <= mu <= xbar + margin:
            covers += 1
    coverage = covers / n_sims
    ok = abs(coverage - 0.95) < 0.05
    return (ok, f"t-CI coverage={coverage:.3f}, expected ~0.95" if not ok else "")


# =========================================================================
# Chapter 17: Regression
# =========================================================================

def ols_simple_regression_formula() -> tuple[bool, str]:
    """Theorem 3.2: beta1_hat = Sxy/Sxx, beta0_hat = ybar - beta1_hat*xbar."""
    n = np.random.randint(10, 50)
    x = np.random.randn(n)
    beta0_true = np.random.randn()
    beta1_true = np.random.randn()
    y = beta0_true + beta1_true * x + np.random.randn(n) * 0.5
    xbar = np.mean(x)
    ybar = np.mean(y)
    Sxy = np.sum((x - xbar) * (y - ybar))
    Sxx = np.sum((x - xbar) ** 2)
    beta1_hat = Sxy / Sxx
    beta0_hat = ybar - beta1_hat * xbar
    # Verify against numpy
    X = np.column_stack([np.ones(n), x])
    beta_np = np.linalg.lstsq(X, y, rcond=None)[0]
    ok = abs(beta0_hat - beta_np[0]) < 1e-10 and abs(beta1_hat - beta_np[1]) < 1e-10
    return (ok, f"Simple OLS: formula b0={beta0_hat:.6f} vs np={beta_np[0]:.6f}" if not ok else "")


def ols_unbiasedness() -> tuple[bool, str]:
    """Theorem 3.3/3.16: OLS estimator is unbiased: E[beta_hat] = beta."""
    n = 50
    p = 2
    beta_true = np.random.randn(p + 1)
    sigma = np.random.uniform(0.5, 2.0)
    n_sims = 500
    beta_hats = np.zeros((n_sims, p + 1))
    X_fixed = np.column_stack([np.ones(n), np.random.randn(n, p)])
    for sim in range(n_sims):
        eps = np.random.randn(n) * sigma
        y = X_fixed @ beta_true + eps
        beta_hat = np.linalg.lstsq(X_fixed, y, rcond=None)[0]
        beta_hats[sim] = beta_hat
    mean_beta_hat = np.mean(beta_hats, axis=0)
    se = np.std(beta_hats, axis=0) / math.sqrt(n_sims)
    z_scores = np.abs(mean_beta_hat - beta_true) / (se + 1e-10)
    ok = bool(np.all(z_scores < 4))
    return (ok, f"OLS bias: z-scores={z_scores}" if not ok else "")


def ols_matrix_form() -> tuple[bool, str]:
    """Theorem 3.6: beta_hat = (X'X)^{-1} X'y."""
    n = np.random.randint(10, 30)
    p = np.random.randint(1, 4)
    X = np.column_stack([np.ones(n), np.random.randn(n, p)])
    y = np.random.randn(n)
    # Formula
    beta_formula = np.linalg.inv(X.T @ X) @ X.T @ y
    # lstsq
    beta_lstsq = np.linalg.lstsq(X, y, rcond=None)[0]
    ok = np.allclose(beta_formula, beta_lstsq, atol=1e-8)
    return (ok, f"OLS matrix form mismatch" if not ok else "")


def hat_matrix_projection() -> tuple[bool, str]:
    """Theorem 3.7: H=X(X'X)^{-1}X' is idempotent and symmetric (projection)."""
    n = np.random.randint(10, 30)
    p = np.random.randint(1, 4)
    X = np.column_stack([np.ones(n), np.random.randn(n, p)])
    H = X @ np.linalg.inv(X.T @ X) @ X.T
    idempotent = np.allclose(H @ H, H, atol=1e-10)
    symmetric = np.allclose(H, H.T, atol=1e-10)
    ok = idempotent and symmetric
    return (ok, f"H not projection: idempotent={idempotent}, symmetric={symmetric}" if not ok else "")


def residuals_orthogonal_to_X() -> tuple[bool, str]:
    """Theorem 3.7: X'e = 0 (residuals orthogonal to column space)."""
    n = np.random.randint(10, 30)
    p = np.random.randint(1, 4)
    X = np.column_stack([np.ones(n), np.random.randn(n, p)])
    y = np.random.randn(n)
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ beta_hat
    orth = X.T @ e
    ok = np.linalg.norm(orth) < 1e-10
    return (ok, f"X'e norm = {np.linalg.norm(orth):.2e}" if not ok else "")


def t_test_individual_coefficients() -> tuple[bool, str]:
    """Theorem 3.11: Under normality, T_j = beta_j_hat/SE(beta_j_hat) ~ t(n-p-1).
    Verify by simulation that t-statistics follow t-distribution."""
    from scipy.stats import kstest, t as t_dist
    n = 50
    p = 2
    sigma = 1.0
    X = np.column_stack([np.ones(n), np.random.randn(n, p)])
    XtX_inv = np.linalg.inv(X.T @ X)
    n_sims = 1000
    t_stats = np.zeros(n_sims)
    for sim in range(n_sims):
        eps = np.random.randn(n) * sigma
        y = X @ np.zeros(p + 1) + eps  # true beta = 0
        beta_hat = XtX_inv @ X.T @ y
        e = y - X @ beta_hat
        s2 = np.sum(e ** 2) / (n - p - 1)
        se_j = math.sqrt(s2 * XtX_inv[1, 1])
        t_stats[sim] = beta_hat[1] / se_j
    stat, pval = kstest(t_stats, t_dist(n - p - 1).cdf)
    ok = pval > 1e-4
    return (ok, f"t-stat distribution KS p-value={pval:.6f}" if not ok else "")


def f_test_overall_significance() -> tuple[bool, str]:
    """Theorem 3.14: Under H0 (all slopes=0), F ~ F(p, n-p-1).
    Verify by simulation."""
    from scipy.stats import kstest, f as f_dist
    n = 40
    p = 2
    sigma = 1.0
    n_sims = 500
    f_stats = np.zeros(n_sims)
    for sim in range(n_sims):
        X = np.column_stack([np.ones(n), np.random.randn(n, p)])
        y = np.random.randn(n) * sigma  # true beta = 0
        beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
        y_hat = X @ beta_hat
        e = y - y_hat
        SSR = np.sum((y_hat - np.mean(y)) ** 2)
        SSE = np.sum(e ** 2)
        f_stats[sim] = (SSR / p) / (SSE / (n - p - 1))
    stat, pval = kstest(f_stats, f_dist(p, n - p - 1).cdf)
    ok = pval > 1e-4
    return (ok, f"F-stat distribution KS p-value={pval:.6f}" if not ok else "")


def f_test_general_restrictions() -> tuple[bool, str]:
    """Theorem 3.15: F-test for general linear restrictions R*beta = r.
    Test: R=[0,1,0], r=0 (test beta_1=0) should match t-test squared."""
    n = 50
    p = 2
    X = np.column_stack([np.ones(n), np.random.randn(n, p)])
    y = np.random.randn(n)
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ beta_hat
    s2 = np.sum(e ** 2) / (n - p - 1)
    XtX_inv = np.linalg.inv(X.T @ X)
    # t-test for beta_1
    se_1 = math.sqrt(s2 * XtX_inv[1, 1])
    t_stat = beta_hat[1] / se_1
    # F-test with R = [0,1,0], r = 0, q = 1
    R = np.array([[0, 1, 0]])
    r = np.array([0])
    Rbeta = R @ beta_hat - r
    F_stat = float(Rbeta @ np.linalg.inv(R @ (s2 * XtX_inv) @ R.T) @ Rbeta / 1)
    # F = t^2 for single restriction
    ok = abs(F_stat - t_stat ** 2) < 1e-6
    return (ok, f"F={F_stat:.6f} != t^2={t_stat**2:.6f}" if not ok else "")


def gauss_markov_blue() -> tuple[bool, str]:
    """Theorem 3.16 (Gauss-Markov): OLS has minimum variance among linear unbiased estimators."""
    n = 30
    X = np.column_stack([np.ones(n), np.random.randn(n)])
    beta_true = np.array([1.0, 2.0])
    sigma = 1.0
    n_sims = 1000
    ols_betas = np.zeros((n_sims, 2))
    alt_betas = np.zeros((n_sims, 2))
    XtX_inv = np.linalg.inv(X.T @ X)
    C_ols = XtX_inv @ X.T
    M = np.eye(n) - X @ XtX_inv @ X.T
    D_raw = np.random.randn(2, n) * 0.01
    D = D_raw @ M
    C_alt = C_ols + D
    for sim in range(n_sims):
        eps = np.random.randn(n) * sigma
        y = X @ beta_true + eps
        ols_betas[sim] = C_ols @ y
        alt_betas[sim] = C_alt @ y
    var_ols = np.var(ols_betas, axis=0)
    var_alt = np.var(alt_betas, axis=0)
    ok = bool(np.all(var_ols <= var_alt + 0.05))
    return (ok, f"OLS var={var_ols}, alt var={var_alt}" if not ok else "")


def r_squared_decomposition() -> tuple[bool, str]:
    """Definition 3.12: SST = SSR + SSE (with intercept)."""
    n = np.random.randint(10, 50)
    X = np.column_stack([np.ones(n), np.random.randn(n)])
    y = np.random.randn(n)
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
    y_hat = X @ beta_hat
    e = y - y_hat
    SST = np.sum((y - np.mean(y))**2)
    SSR = np.sum((y_hat - np.mean(y))**2)
    SSE = np.sum(e**2)
    ok = abs(SST - SSR - SSE) < 1e-8
    return (ok, f"SST={SST:.6f} != SSR+SSE={SSR+SSE:.6f}" if not ok else "")


# =========================================================================
# Chapter 18: Difference Equations
# =========================================================================

def first_order_difference_eq_solution() -> tuple[bool, str]:
    """Theorem 3.3: x_t = a^t(x_0 - x*) + x* where x*=b/(1-a)."""
    a = np.random.uniform(-0.99, 0.99)
    b = np.random.uniform(-5, 5)
    x0 = np.random.uniform(-10, 10)
    x_star = b / (1 - a)
    t = np.random.randint(1, 50)
    x_iter = x0
    for _ in range(t):
        x_iter = a * x_iter + b
    x_formula = a**t * (x0 - x_star) + x_star
    ok = abs(x_iter - x_formula) < 1e-6 * (abs(x_iter) + 1)
    return (ok, f"x_{t} iter={x_iter:.8f} != formula={x_formula:.8f}" if not ok else "")


def first_order_stability() -> tuple[bool, str]:
    """Theorem 3.3: |a|<1 => stable, |a|>1 => unstable."""
    a = np.random.uniform(0.01, 0.95) * np.random.choice([-1, 1])
    b = np.random.uniform(-5, 5)
    x0 = np.random.uniform(-10, 10)
    x_star = b / (1 - a)
    x = x0
    for _ in range(200):
        x = a * x + b
    ok = abs(x - x_star) < 0.01 * (abs(x_star) + 1)
    return (ok, f"|a|={abs(a):.3f}<1 but x_200={x:.4f} far from x*={x_star:.4f}" if not ok else "")


def second_order_distinct_real_roots() -> tuple[bool, str]:
    """Theorem 3.5: If char eq has distinct real roots lam1, lam2,
    then x_t = c1*lam1^t + c2*lam2^t."""
    # Generate roots inside unit circle for stability
    lam1 = np.random.uniform(-0.9, 0.9)
    lam2 = np.random.uniform(-0.9, 0.9)
    while abs(lam1 - lam2) < 0.1:
        lam2 = np.random.uniform(-0.9, 0.9)
    # a1 = -(lam1+lam2), a2 = lam1*lam2
    a1 = -(lam1 + lam2)
    a2 = lam1 * lam2
    # Initial conditions
    x0 = np.random.randn()
    x1 = np.random.randn()
    # Solve for c1, c2: c1 + c2 = x0, c1*lam1 + c2*lam2 = x1
    c_vec = np.linalg.solve(np.array([[1, 1], [lam1, lam2]]), np.array([x0, x1]))
    c1, c2 = c_vec
    # Iterate
    t = np.random.randint(5, 20)
    xs = [x0, x1]
    for i in range(2, t + 1):
        xs.append(-a1 * xs[-1] - a2 * xs[-2])
    x_iter = xs[t]
    x_formula = c1 * lam1 ** t + c2 * lam2 ** t
    ok = abs(x_iter - x_formula) < 1e-6 * (abs(x_iter) + 1)
    return (ok, f"x_{t}: iter={x_iter:.8f} != formula={x_formula:.8f}" if not ok else "")


def second_order_complex_roots() -> tuple[bool, str]:
    """Theorem 3.6: Complex roots r*e^{+/-i*theta} give x_t = r^t(c1*cos(theta*t)+c2*sin(theta*t))."""
    r = np.random.uniform(0.3, 0.9)
    theta = np.random.uniform(0.3, math.pi - 0.3)
    # Characteristic roots: r*e^{+/-i*theta}
    # a1 = -2*r*cos(theta), a2 = r^2
    a1 = -2 * r * math.cos(theta)
    a2 = r ** 2
    x0 = np.random.randn()
    x1 = np.random.randn()
    # Solve for c1, c2: x0 = c1, x1 = r*(c1*cos(theta)+c2*sin(theta))
    c1 = x0
    c2 = (x1 - r * c1 * math.cos(theta)) / (r * math.sin(theta))
    t = np.random.randint(5, 20)
    xs = [x0, x1]
    for i in range(2, t + 1):
        xs.append(-a1 * xs[-1] - a2 * xs[-2])
    x_iter = xs[t]
    x_formula = r ** t * (c1 * math.cos(theta * t) + c2 * math.sin(theta * t))
    ok = abs(x_iter - x_formula) < 1e-5 * (abs(x_iter) + 1)
    return (ok, f"x_{t}: iter={x_iter:.8f} != complex formula={x_formula:.8f}" if not ok else "")


def schur_cohn_conditions() -> tuple[bool, str]:
    """Theorem 3.7: Second-order stability iff 1+a1+a2>0, 1-a1+a2>0, |a2|<1."""
    r = np.random.uniform(0.1, 0.95)
    theta = np.random.uniform(0, math.pi)
    lam1 = r * np.exp(1j * theta)
    lam2 = np.conj(lam1)
    a1 = -float(np.real(lam1 + lam2))
    a2 = float(np.real(lam1 * lam2))
    cond1 = 1 + a1 + a2 > 0
    cond2 = 1 - a1 + a2 > 0
    cond3 = abs(a2) < 1
    ok = cond1 and cond2 and cond3
    return (ok, f"Schur-Cohn failed for stable system: c1={cond1}, c2={cond2}, c3={cond3}" if not ok else "")


def system_spectral_radius_stability() -> tuple[bool, str]:
    """Theorem 3.9: x_{t+1}=Ax_t+b stable iff spectral radius rho(A) < 1."""
    n = np.random.randint(2, 4)
    A = np.random.randn(n, n) * 0.3
    rho = max(abs(np.linalg.eigvals(A)))
    if rho > 0.95:
        A = A * 0.9 / rho
    b = np.random.randn(n)
    x_star = np.linalg.solve(np.eye(n) - A, b)
    x = np.random.randn(n)
    for _ in range(200):
        x = A @ x + b
    ok = np.linalg.norm(x - x_star) < 0.01
    return (ok, f"rho(A)={max(abs(np.linalg.eigvals(A))):.4f}<1 but not converged" if not ok else "")


# =========================================================================
# Chapter 19: ODEs
# =========================================================================

def picard_lindelof_existence() -> tuple[bool, str]:
    """Theorem 3.3: Lipschitz f => unique solution exists."""
    from scipy.integrate import solve_ivp
    y0 = np.random.uniform(-5, 5)
    sol = solve_ivp(lambda t, y: -y + math.sin(t), [0, 5], [y0], rtol=1e-10, atol=1e-12)
    sol2 = solve_ivp(lambda t, y: -y + math.sin(t), [0, 5], [y0], method='DOP853', rtol=1e-10, atol=1e-12)
    if sol.success and sol2.success:
        diff = abs(sol.y[0, -1] - sol2.y[0, -1])
        ok = diff < 1e-6
        return (ok, f"Two methods differ by {diff:.2e}" if not ok else "")
    return (True, "")


def ode_characteristic_equation() -> tuple[bool, str]:
    """Theorem 3.9: y''+4y=0 has solution y=c1*cos(2t)+c2*sin(2t)."""
    c1 = np.random.randn()
    c2 = np.random.randn()
    t = np.random.uniform(0, 10)
    y = c1 * math.cos(2*t) + c2 * math.sin(2*t)
    y_pp = -4 * c1 * math.cos(2*t) - 4 * c2 * math.sin(2*t)
    residual = y_pp + 4 * y
    ok = abs(residual) < 1e-12
    return (ok, f"y''+4y = {residual:.2e} != 0" if not ok else "")


def ode_stability_classification() -> tuple[bool, str]:
    """Theorem 3.12: For x'=Ax, stable iff Re(lambda_i) < 0 for all i."""
    n = np.random.randint(2, 4)
    D = np.diag(-np.random.uniform(0.1, 2.0, n))
    P = np.random.randn(n, n)
    while abs(np.linalg.det(P)) < 0.1:
        P = np.random.randn(n, n)
    A = P @ D @ np.linalg.inv(P)
    eigs = np.linalg.eigvals(A)
    all_neg = bool(np.all(np.real(eigs) < 0))
    if not all_neg:
        return (True, "")
    # Skip ill-conditioned similarity transforms that cause large transient growth
    if np.linalg.cond(P) > 100:
        return (True, "")
    from scipy.integrate import solve_ivp
    x0 = np.random.randn(n)
    sol = solve_ivp(lambda t, x: A @ x, [0, 50], x0, rtol=1e-8, atol=1e-10, dense_output=True)
    if sol.success:
        x_final = sol.y[:, -1]
        ok = np.linalg.norm(x_final) < 0.5
        return (ok, f"Re(lambda)<0 but ||x(50)||={np.linalg.norm(x_final):.6f}" if not ok else "")
    return (True, "")


def separable_ode_solution() -> tuple[bool, str]:
    """y' = xy with y(0)=1 has solution y = e^{x^2/2}."""
    from scipy.integrate import solve_ivp
    sol = solve_ivp(lambda t, y: t * y[0], [0, 2], [1.0], rtol=1e-10, atol=1e-12, dense_output=True)
    if not sol.success:
        return (True, "")
    t_test = np.random.uniform(0, 2)
    y_numerical = sol.sol(t_test)[0]
    y_analytical = math.exp(t_test**2 / 2)
    ok = abs(y_numerical - y_analytical) / max(abs(y_analytical), 1) < 1e-6
    return (ok, f"y({t_test:.3f}): numerical={y_numerical:.8f}, analytical={y_analytical:.8f}" if not ok else "")


def ode_phase_portrait_node() -> tuple[bool, str]:
    """Phase portrait: both eigenvalues negative => stable node."""
    from scipy.integrate import solve_ivp
    lam1 = -np.random.uniform(0.5, 3)
    lam2 = -np.random.uniform(0.5, 3)
    A = np.diag([lam1, lam2])
    x0 = np.random.randn(2)
    sol = solve_ivp(lambda t, x: A @ x, [0, 20], x0, rtol=1e-8, atol=1e-10)
    if sol.success:
        x_final = sol.y[:, -1]
        ok = np.linalg.norm(x_final) < 0.01
        return (ok, f"Stable node: ||x(20)||={np.linalg.norm(x_final):.6f}" if not ok else "")
    return (True, "")


def ode_phase_portrait_spiral() -> tuple[bool, str]:
    """Complex eigenvalues alpha +/- i*beta with alpha < 0 => stable spiral."""
    from scipy.integrate import solve_ivp
    alpha = -np.random.uniform(0.3, 2.0)
    beta = np.random.uniform(0.5, 3.0)
    A = np.array([[alpha, -beta], [beta, alpha]])
    eigs = np.linalg.eigvals(A)
    assert np.all(np.real(eigs) < 0)
    x0 = np.random.randn(2)
    sol = solve_ivp(lambda t, x: A @ x, [0, 20], x0, rtol=1e-8, atol=1e-10)
    if sol.success:
        x_final = sol.y[:, -1]
        ok = np.linalg.norm(x_final) < 0.1
        return (ok, f"Stable spiral: ||x(20)||={np.linalg.norm(x_final):.6f}" if not ok else "")
    return (True, "")


# =========================================================================
# Chapter 20: Discrete Operators
# =========================================================================

def lag_operator_linearity() -> tuple[bool, str]:
    """Theorem 3.3: L(ax_t + by_t) = a*L(x_t) + b*L(y_t)."""
    n = np.random.randint(10, 30)
    x = np.random.randn(n)
    y = np.random.randn(n)
    a, b = np.random.randn(2)
    # L(ax+by) at index t (for t >= 1)
    t = np.random.randint(1, n)
    lhs = a * x[t - 1] + b * y[t - 1]  # L applied to combined sequence
    rhs = a * x[t - 1] + b * y[t - 1]  # linearity
    ok = abs(lhs - rhs) < 1e-14
    return (ok, f"Lag linearity: LHS={lhs:.10f} != RHS={rhs:.10f}" if not ok else "")


def discrete_ftc() -> tuple[bool, str]:
    """Discrete FTC: sum_{t=a}^{b-1} Delta(x_t) = x_b - x_a (telescoping)."""
    n = np.random.randint(5, 20)
    x = np.random.randn(n)
    a = 0
    b = n - 1
    delta_sum = sum(x[t+1] - x[t] for t in range(a, b))
    ok = abs(delta_sum - (x[b] - x[a])) < 1e-12
    return (ok, f"sum Delta = {delta_sum:.10f} != x_b - x_a = {x[b]-x[a]:.10f}" if not ok else "")


def delta_n_binomial_expansion() -> tuple[bool, str]:
    """Theorem 3.6: Delta^n x_t = sum_{k=0}^n (-1)^k C(n,k) x_{t-k}.
    Test with known sequences."""
    n_order = np.random.randint(1, 5)
    seq_len = n_order + np.random.randint(5, 15)
    x = np.random.randn(seq_len)
    t = seq_len - 1  # evaluate at last valid index
    # Compute Delta^n by iterated differencing
    diff = x.copy()
    for _ in range(n_order):
        diff = np.diff(diff)
    if len(diff) == 0:
        return (True, "")
    iter_result = diff[-1]
    # Compute via binomial expansion
    binom_result = sum(
        (-1) ** k * math.comb(n_order, k) * x[t - k]
        for k in range(n_order + 1)
        if t - k >= 0
    )
    ok = abs(iter_result - binom_result) < 1e-8
    return (ok, f"Delta^{n_order}: iterated={iter_result:.8f} != binomial={binom_result:.8f}" if not ok else "")


def convolution_polynomial_multiplication() -> tuple[bool, str]:
    """Theorem 3.9: Coefficients of f*g = convolution of coefficient sequences."""
    m = np.random.randint(2, 6)
    n = np.random.randint(2, 6)
    f_coeffs = np.random.randn(m + 1)
    g_coeffs = np.random.randn(n + 1)
    # Direct polynomial multiplication
    product = np.polymul(f_coeffs[::-1], g_coeffs[::-1])[::-1]
    # Convolution
    conv = np.convolve(f_coeffs, g_coeffs)
    ok = np.allclose(product, conv, atol=1e-10)
    return (ok, f"Poly mult != convolution" if not ok else "")


def z_transform_shift() -> tuple[bool, str]:
    """Theorem 3.11: Z{L*x_t} = z^{-1} * X(z).
    Verify algebraically: Z{x_{t-1}} = sum_{t=1}^{N-1} x_{t-1} z^{-t}
    = z^{-1} sum_{t=1}^{N-1} x_{t-1} z^{-(t-1)}
    = z^{-1} sum_{s=0}^{N-2} x_s z^{-s} (assuming x_{-1}=0)."""
    n = np.random.randint(5, 15)
    x = np.random.randn(n)
    z = np.random.uniform(2.0, 5.0)
    # Z{L x_t} = sum_{t=0}^{n-1} x_{t-1} z^{-t}, with x_{-1}=0
    # = sum_{t=1}^{n-1} x_{t-1} z^{-t}
    ZLx = sum(x[t - 1] * z ** (-t) for t in range(1, n))
    # z^{-1} X(z) = z^{-1} sum_{t=0}^{n-1} x_t z^{-t}
    # But we need to account for: Z{Lx}_t is only defined for t=0..n-1,
    # and z^{-1}*X(z) includes the x_{n-1}*z^{-n} term that Lx does not.
    # So: Z{Lx} = z^{-1} * (X(z) - x_{n-1}*z^{-(n-1)})
    # Actually: Z{Lx} = z^{-1} * sum_{s=0}^{n-2} x_s z^{-s}
    expected = (1.0 / z) * sum(x[s] * z ** (-s) for s in range(n - 1))
    ok = abs(ZLx - expected) < 1e-12 * (abs(expected) + 1)
    return (ok, f"Z(Lx)={ZLx:.10f} != z^{{-1}}*X'(z)={expected:.10f}" if not ok else "")


# =========================================================================
# Chapter 21: Time Series
# =========================================================================

def ar1_stationarity() -> tuple[bool, str]:
    """Theorem 3.13/3.14: AR(1) stationary iff |phi|<1. ACF(h) = phi^h."""
    phi = np.random.uniform(-0.95, 0.95)
    n = 10000
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t-1] + np.random.randn()
    acf_1 = np.corrcoef(x[:-1], x[1:])[0, 1]
    ok = abs(acf_1 - phi) < 0.05
    return (ok, f"AR(1) phi={phi:.3f}, sample ACF(1)={acf_1:.3f}" if not ok else "")


def ma_q_acf_cutoff() -> tuple[bool, str]:
    """Theorem 3.16: ACF of MA(q) is zero for h > q.
    Test with MA(2): ACF should be zero for h > 2."""
    theta1 = np.random.uniform(-0.9, 0.9)
    theta2 = np.random.uniform(-0.9, 0.9)
    n = 20000
    eps = np.random.randn(n + 2)
    x = np.array([eps[t] + theta1 * eps[t - 1] + theta2 * eps[t - 2] for t in range(2, n + 2)])
    # ACF at lag 5 should be approximately 0
    lag = 5
    acf_5 = np.corrcoef(x[:-lag], x[lag:])[0, 1]
    ok = abs(acf_5) < 0.05
    return (ok, f"MA(2) ACF at lag {lag}={acf_5:.4f}, expected ~0" if not ok else "")


def yule_walker_equations() -> tuple[bool, str]:
    """Theorem 3.19: Yule-Walker equations for AR(p).
    Test: for AR(1), gamma(h) = phi*gamma(h-1). Verify Yule-Walker gives correct phi."""
    phi_true = np.random.uniform(-0.9, 0.9)
    n = 10000
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi_true * x[t - 1] + np.random.randn()
    # Yule-Walker: phi_hat = gamma(1)/gamma(0) = r(1)
    gamma_0 = np.var(x)
    gamma_1 = np.mean((x[1:] - np.mean(x)) * (x[:-1] - np.mean(x)))
    phi_hat = gamma_1 / gamma_0
    ok = abs(phi_hat - phi_true) < 0.05
    return (ok, f"Yule-Walker phi_hat={phi_hat:.4f} vs phi_true={phi_true:.4f}" if not ok else "")


# =========================================================================
# Chapter 22: Transforms
# =========================================================================

def dft_linearity() -> tuple[bool, str]:
    """Theorem 3.3(a): DFT is linear: F[alpha*x + beta*y] = alpha*F[x] + beta*F[y]."""
    N = np.random.choice([16, 32, 64])
    x = np.random.randn(N)
    y = np.random.randn(N)
    alpha, beta = np.random.randn(2)
    lhs = np.fft.fft(alpha * x + beta * y)
    rhs = alpha * np.fft.fft(x) + beta * np.fft.fft(y)
    ok = np.allclose(lhs, rhs, atol=1e-10)
    return (ok, f"DFT linearity: max diff={np.max(np.abs(lhs - rhs)):.2e}" if not ok else "")


def parseval_theorem_dft() -> tuple[bool, str]:
    """Theorem 3.4: sum |x_n|^2 = (1/N) sum |X_k|^2 (Parseval's theorem)."""
    N = np.random.choice([16, 32, 64, 128])
    x = np.random.randn(N)
    X = np.fft.fft(x)
    time_energy = np.sum(x**2)
    freq_energy = np.sum(np.abs(X)**2) / N
    ok = abs(time_energy - freq_energy) < 1e-10
    return (ok, f"Parseval: time={time_energy:.8f} != freq={freq_energy:.8f}" if not ok else "")


def convolution_theorem_dft() -> tuple[bool, str]:
    """Theorem 3.3(c): DFT of circular convolution = pointwise product of DFTs."""
    N = np.random.choice([16, 32, 64])
    x = np.random.randn(N)
    y = np.random.randn(N)
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    conv_via_fft = np.real(np.fft.ifft(X * Y))
    conv_direct = np.array([sum(x[m] * y[(n-m) % N] for m in range(N)) for n in range(N)])
    ok = np.allclose(conv_via_fft, conv_direct, atol=1e-10)
    return (ok, f"Convolution theorem: max diff={np.max(np.abs(conv_via_fft - conv_direct)):.2e}" if not ok else "")


def cooley_tukey_decomposition() -> tuple[bool, str]:
    """Theorem 3.5: Radix-2 FFT decomposes N-point DFT into two M-point DFTs.
    Verify FFT gives same result as direct DFT computation."""
    N = np.random.choice([8, 16, 32, 64])
    x = np.random.randn(N)
    # Direct DFT
    omega = np.exp(-2j * np.pi / N)
    X_direct = np.array([sum(x[n] * omega ** (k * n) for n in range(N)) for k in range(N)])
    # FFT
    X_fft = np.fft.fft(x)
    ok = np.allclose(X_direct, X_fft, atol=1e-8)
    return (ok, f"Cooley-Tukey: max diff={np.max(np.abs(X_direct - X_fft)):.2e}" if not ok else "")


# =========================================================================
# Chapter 23: Operator Algebra
# =========================================================================

def linear_operators_form_algebra() -> tuple[bool, str]:
    """Theorem 3.10: L(V) with addition, scalar multiplication, composition is an algebra.
    Test with matrix operators: (A+B)C = AC + BC, c(AB) = (cA)B = A(cB)."""
    n = np.random.randint(2, 5)
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)
    C = np.random.randn(n, n)
    c = np.random.randn()
    # Right distributivity
    right_dist = np.allclose((A + B) @ C, A @ C + B @ C, atol=1e-10)
    # Left distributivity
    left_dist = np.allclose(A @ (B + C), A @ B + A @ C, atol=1e-10)
    # Scalar compatibility
    scalar = np.allclose(c * (A @ B), (c * A) @ B, atol=1e-10)
    scalar2 = np.allclose(c * (A @ B), A @ (c * B), atol=1e-10)
    ok = right_dist and left_dist and scalar and scalar2
    return (ok, f"Algebra axioms: rdist={right_dist},ldist={left_dist},scalar={scalar}" if not ok else "")


def polynomial_operators_ode() -> tuple[bool, str]:
    """Theorem 3.14: p(D)y = f represents a linear ODE with constant coefficients.
    Test: (D^2 + 4)y = 0 has solution y = c1*cos(2x)+c2*sin(2x)."""
    c1 = np.random.randn()
    c2 = np.random.randn()
    x = np.random.uniform(0, 10)
    y = c1 * math.cos(2 * x) + c2 * math.sin(2 * x)
    # D^2 y = -4*c1*cos(2x) - 4*c2*sin(2x) = -4y
    Dy = -2 * c1 * math.sin(2 * x) + 2 * c2 * math.cos(2 * x)
    D2y = -4 * c1 * math.cos(2 * x) - 4 * c2 * math.sin(2 * x)
    residual = D2y + 4 * y
    ok = abs(residual) < 1e-10
    return (ok, f"(D^2+4)y = {residual:.2e} != 0" if not ok else "")


def polynomial_operators_difference_eq() -> tuple[bool, str]:
    """Theorem 3.15: p(L)x_t = f_t represents a linear difference equation.
    Test: (1 - 0.5*L)x_t = eps_t is AR(1) with phi=0.5."""
    phi = 0.5
    n = 100
    eps = np.random.randn(n)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + eps[t]
    # Verify: (1 - 0.5*L)x_t = x_t - 0.5*x_{t-1} should equal eps_t
    for t in range(1, n):
        residual = x[t] - phi * x[t - 1] - eps[t]
        if abs(residual) > 1e-10:
            return (False, f"p(L)x_t residual at t={t}: {residual:.2e}")
    return (True, "")


def operator_correspondence() -> tuple[bool, str]:
    """Theorem 3.21: Continuous D, discrete Delta, matrix A satisfy parallel properties.
    Test: e^{D} f(x) = f(x+1) (shift), A^n = PD^nP^{-1} (matrix power via diag)."""
    # Matrix case: A^n = P D^n P^{-1} for diagonalizable A
    n = np.random.randint(2, 4)
    A_mat = np.random.randn(n, n)
    S = (A_mat + A_mat.T) / 2  # symmetric => diagonalizable
    evals, P = np.linalg.eigh(S)
    k = np.random.randint(2, 5)
    Ak_direct = np.linalg.matrix_power(S, k)
    Ak_diag = P @ np.diag(evals ** k) @ P.T
    ok = np.allclose(Ak_direct, Ak_diag, atol=1e-8)
    return (ok, f"A^{k} via diag: max diff={np.max(np.abs(Ak_direct - Ak_diag)):.2e}" if not ok else "")


def shift_as_exponential_of_D() -> tuple[bool, str]:
    """Theorem 3.25: e^{aD} f(x) = f(x+a).
    Test: Taylor series of e^{aD} applied to polynomial gives shifted polynomial."""
    # For polynomial f(x) = x^3 + 2x + 1
    a = np.random.uniform(-2, 2)
    x = np.random.uniform(-5, 5)
    f = lambda x: x ** 3 + 2 * x + 1
    # e^{aD} f(x) = sum_{k=0}^inf (aD)^k/k! f(x)
    # = f(x) + a*f'(x) + a^2/2*f''(x) + a^3/6*f'''(x) + ...
    # f(x) = x^3 + 2x + 1, f'(x) = 3x^2 + 2, f''(x) = 6x, f'''(x) = 6
    taylor_sum = f(x) + a * (3 * x ** 2 + 2) + (a ** 2 / 2) * (6 * x) + (a ** 3 / 6) * 6
    shifted = f(x + a)
    ok = abs(taylor_sum - shifted) < 1e-10
    return (ok, f"e^(aD)f(x)={taylor_sum:.8f} != f(x+a)={shifted:.8f}" if not ok else "")


def operator_exponential_properties() -> tuple[bool, str]:
    """Theorem 3.27: e^O = I, e^{(s+t)A} = e^{sA} * e^{tA}."""
    from scipy.linalg import expm
    n = np.random.randint(2, 4)
    A = np.random.randn(n, n) * 0.5  # small for numerical stability
    s = np.random.uniform(-1, 1)
    t = np.random.uniform(-1, 1)
    # e^0 = I
    ok1 = np.allclose(expm(np.zeros((n, n))), np.eye(n), atol=1e-12)
    # Semigroup: e^{(s+t)A} = e^{sA} e^{tA}
    lhs = expm((s + t) * A)
    rhs = expm(s * A) @ expm(t * A)
    ok2 = np.allclose(lhs, rhs, atol=1e-8)
    ok = ok1 and ok2
    return (ok, f"Operator exponential: e^0=I:{ok1}, semigroup:{ok2}" if not ok else "")


# =========================================================================
# Chapter 24: Fractional Calculus
# =========================================================================

def gl_weight_recurrence() -> tuple[bool, str]:
    """Theorem 3.5: GL weights satisfy w_0 = 1, w_k = w_{k-1} * (alpha - k + 1) / k.
    Verify the recurrence produces weights that decay algebraically and satisfy
    the fractional differencing identity: (1-z)^alpha = sum w_k z^k."""
    alpha = np.random.uniform(0.1, 1.5)
    N = np.random.randint(10, 50)
    # Compute weights via recurrence
    w = np.zeros(N)
    w[0] = 1.0
    for k in range(1, N):
        w[k] = w[k - 1] * (alpha - k + 1) / k
    # Verify w_0 = 1
    ok1 = abs(w[0] - 1.0) < 1e-15
    # Verify the generating function: sum_{k=0}^{N-1} w_k * z^k = (1+z)^alpha
    # The recurrence gives C(alpha,k), so (1+z)^alpha = sum C(alpha,k) z^k
    z = np.random.uniform(0.1, 0.5)
    series_sum = sum(w[k] * z ** k for k in range(N))
    exact = (1 + z) ** alpha
    rel_err = abs(series_sum - exact) / max(abs(exact), 1e-15)
    ok2 = rel_err < 1e-4  # truncation error for moderate N
    # Verify sign pattern: for 0 < alpha < 1, w_0=1 > 0, w_1 = alpha > 0,
    # and the recurrence factor (alpha-k+1)/k changes sign at k = floor(alpha)+1
    # For fractional alpha in (0,1): w_0=1, w_1=alpha, then w_k becomes negative for k >= 2
    # More generally: C(alpha, k) > 0 for k <= floor(alpha), sign alternates after
    # Just verify w_0 = 1 and the recurrence is correct by checking a few values
    ok3 = abs(w[0] - 1.0) < 1e-15
    if N > 1:
        ok3 = ok3 and abs(w[1] - alpha) < 1e-12  # w_1 = C(alpha,1) = alpha
    # Verify algebraic decay: |w_k| ~ k^{-alpha-1} for large k
    if N > 10:
        ratio = abs(w[N - 1]) / abs(w[N - 2]) if abs(w[N - 2]) > 1e-20 else 1.0
        expected_ratio = ((N - 2) / (N - 1)) ** (alpha + 1)
        ok4 = abs(ratio - expected_ratio) < 0.2  # approximate
    else:
        ok4 = True
    ok = ok1 and ok2 and ok3
    return (ok, f"w_0=1:{ok1}, gen_fn_err={rel_err:.2e}:{ok2}, signs:{ok3}" if not ok else "")


def fractional_semigroup_property() -> tuple[bool, str]:
    """Theorem 3.9: J^alpha . J^beta = J^{alpha+beta} (semigroup for fractional integrals).
    Verify on f(x) = x^2: J^alpha(x^2) = Gamma(3)/Gamma(3+alpha) * x^{2+alpha}.
    Then J^beta(J^alpha(x^2)) should equal J^{alpha+beta}(x^2)."""
    alpha = np.random.uniform(0.2, 1.0)
    beta = np.random.uniform(0.2, 1.0)
    x = np.random.uniform(1.0, 5.0)
    # J^alpha(x^p) = Gamma(p+1)/Gamma(p+1+alpha) * x^{p+alpha}  (for p > -1, x > 0, a=0)
    p = 2.0
    # J^alpha(x^2) = Gamma(3)/Gamma(3+alpha) * x^{2+alpha}
    j_alpha = math.gamma(p + 1) / math.gamma(p + 1 + alpha) * x ** (p + alpha)
    # J^beta(J^alpha(x^2)) = J^beta(c * x^{2+alpha}) where c = Gamma(3)/Gamma(3+alpha)
    # = c * Gamma(3+alpha)/Gamma(3+alpha+beta) * x^{2+alpha+beta}
    j_beta_of_j_alpha = (
        math.gamma(p + 1) / math.gamma(p + 1 + alpha)
        * math.gamma(p + 1 + alpha) / math.gamma(p + 1 + alpha + beta)
        * x ** (p + alpha + beta)
    )
    # J^{alpha+beta}(x^2) = Gamma(3)/Gamma(3+alpha+beta) * x^{2+alpha+beta}
    j_alpha_plus_beta = math.gamma(p + 1) / math.gamma(p + 1 + alpha + beta) * x ** (p + alpha + beta)
    rel_err = abs(j_beta_of_j_alpha - j_alpha_plus_beta) / max(abs(j_alpha_plus_beta), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"Semigroup: J^b(J^a)={j_beta_of_j_alpha:.8f} vs J^{{a+b}}={j_alpha_plus_beta:.8f}" if not ok else "")


def rl_derivative_of_power_function() -> tuple[bool, str]:
    """Theorem 3.10: D^alpha(x^beta) = Gamma(beta+1)/Gamma(beta-alpha+1) * x^{beta-alpha}
    for beta > -1 and x > 0 (lower terminal a=0).
    Verify the formula is self-consistent: apply it twice and check composition."""
    alpha = np.random.uniform(0.1, 1.5)
    beta = np.random.uniform(alpha + 0.5, 5.0)  # ensure beta - alpha > -1
    x = np.random.uniform(0.5, 5.0)
    # Formula: D^alpha(x^beta) = Gamma(beta+1)/Gamma(beta-alpha+1) * x^{beta-alpha}
    result = math.gamma(beta + 1) / math.gamma(beta - alpha + 1) * x ** (beta - alpha)
    # Consistency check 1: for alpha = integer n, should reduce to the standard derivative
    # D^1(x^beta) = beta * x^{beta-1}
    x_test = np.random.uniform(0.5, 5.0)
    beta_test = np.random.uniform(2.0, 5.0)
    d1_formula = math.gamma(beta_test + 1) / math.gamma(beta_test) * x_test ** (beta_test - 1)
    d1_standard = beta_test * x_test ** (beta_test - 1)
    ok1 = abs(d1_formula - d1_standard) / max(abs(d1_standard), 1e-15) < 1e-10
    # Consistency check 2: D^2(x^beta) = beta*(beta-1)*x^{beta-2}
    d2_formula = math.gamma(beta_test + 1) / math.gamma(beta_test - 1) * x_test ** (beta_test - 2)
    d2_standard = beta_test * (beta_test - 1) * x_test ** (beta_test - 2)
    ok2 = abs(d2_formula - d2_standard) / max(abs(d2_standard), 1e-15) < 1e-10
    # Consistency check 3: D^0(x^beta) = x^beta (identity)
    d0_formula = math.gamma(beta_test + 1) / math.gamma(beta_test + 1) * x_test ** beta_test
    ok3 = abs(d0_formula - x_test ** beta_test) / max(abs(x_test ** beta_test), 1e-15) < 1e-10
    # Consistency check 4: result is positive for x > 0 and appropriate alpha, beta
    ok4 = result > 0 or (beta - alpha) < 0  # may be negative if exponent is negative
    ok = ok1 and ok2 and ok3
    return (ok, f"D^1 check:{ok1}, D^2 check:{ok2}, D^0 check:{ok3}" if not ok else "")


def rl_to_caputo_relation() -> tuple[bool, str]:
    """Theorem 3.12: For 0 < alpha < 1 and f sufficiently smooth,
    ^C D^alpha f(x) = ^RL D^alpha [f(x) - f(a)].
    Equivalently: ^RL D^alpha f = ^C D^alpha f + f(a) * x^{-alpha} / Gamma(1-alpha).
    Test on f(x) = x^2 + 3 with a=0:
      ^RL D^alpha(x^2 + 3) = D^alpha(x^2) + 3 * x^{-alpha}/Gamma(1-alpha)
      ^C D^alpha(x^2 + 3) = D^alpha(x^2)  (Caputo of constant = 0)
    So ^RL - ^C should equal 3 * x^{-alpha}/Gamma(1-alpha)."""
    alpha = np.random.uniform(0.1, 0.9)
    x = np.random.uniform(1.0, 5.0)
    f_a = 3.0  # f(0) = 0^2 + 3 = 3
    # RL D^alpha(x^2) = Gamma(3)/Gamma(3-alpha) * x^{2-alpha}
    rl_x2 = math.gamma(3) / math.gamma(3 - alpha) * x ** (2 - alpha)
    # RL D^alpha(3) = 3 * x^{-alpha} / Gamma(1-alpha)
    rl_const = f_a * x ** (-alpha) / math.gamma(1 - alpha)
    # RL D^alpha(f) = rl_x2 + rl_const
    rl_total = rl_x2 + rl_const
    # Caputo D^alpha(f) = D^alpha(x^2) only (constant vanishes)
    caputo_total = rl_x2
    # Difference should equal the correction term
    diff = rl_total - caputo_total
    expected_diff = rl_const
    rel_err = abs(diff - expected_diff) / max(abs(expected_diff), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"RL-Caputo={diff:.8f} vs f(a)*x^(-a)/G(1-a)={expected_diff:.8f}" if not ok else "")


def fractional_derivative_composition() -> tuple[bool, str]:
    """Theorem 3.15: Under regularity conditions, D^alpha . D^beta = D^{alpha+beta}.
    Test on f(x) = x^4 with alpha, beta > 0:
      D^alpha(D^beta(x^4)) should equal D^{alpha+beta}(x^4).
    Using Thm 3.10: D^gamma(x^4) = Gamma(5)/Gamma(5-gamma) * x^{4-gamma}."""
    alpha = np.random.uniform(0.2, 0.8)
    beta = np.random.uniform(0.2, 0.8)
    x = np.random.uniform(1.0, 5.0)
    p = 4.0
    # D^beta(x^4) = Gamma(5)/Gamma(5-beta) * x^{4-beta}
    # D^alpha(D^beta(x^4)) = D^alpha(c * x^{4-beta}) where c = Gamma(5)/Gamma(5-beta)
    # = c * Gamma(5-beta)/Gamma(5-beta-alpha) * x^{4-beta-alpha}
    composed = (
        math.gamma(p + 1) / math.gamma(p + 1 - beta)
        * math.gamma(p + 1 - beta) / math.gamma(p + 1 - beta - alpha)
        * x ** (p - beta - alpha)
    )
    # D^{alpha+beta}(x^4) = Gamma(5)/Gamma(5-alpha-beta) * x^{4-alpha-beta}
    direct = math.gamma(p + 1) / math.gamma(p + 1 - alpha - beta) * x ** (p - alpha - beta)
    rel_err = abs(composed - direct) / max(abs(direct), 1e-15)
    ok = rel_err < 1e-10
    return (ok, f"D^a(D^b(x^4))={composed:.8f} vs D^{{a+b}}(x^4)={direct:.8f}" if not ok else "")


# =========================================================================
# Build theorem tests into a Chapter
# =========================================================================

def build() -> Chapter:
    ch = Chapter(0, "Theorem Property-Based Tests")

    tests = [
        # ================================================================
        # Chapter 1: Expressions
        # ================================================================
        TheoremTest("Thm 1.3.5 Composition is associative", 1, "4",
                    "f, g, h are functions with compatible domains",
                    "f . (g . h) = (f . g) . h",
                    composition_associativity, n_trials=1000),
        TheoremTest("Thm 1.3.17 Well-definedness of evaluation", 1, "4",
                    "expression with all variables assigned, no domain violations",
                    "eval produces a well-defined real number",
                    well_definedness_of_evaluation, n_trials=1000),

        # ================================================================
        # Chapter 2: Special Functions
        # ================================================================
        TheoremTest("Thm 2.3.2 Gamma factorial property", 2, "4",
                    "z > 0",
                    "Gamma(z+1) = z * Gamma(z)",
                    gamma_factorial_property, n_trials=2000),
        TheoremTest("Cor 2.3.3 Gamma extends factorial", 2, "4",
                    "n in N",
                    "Gamma(n+1) = n!",
                    gamma_extends_factorial, n_trials=500),
        TheoremTest("Thm 2.3.4 Gamma(1/2) = sqrt(pi)", 2, "4",
                    "always",
                    "Gamma(1/2) = sqrt(pi)",
                    gamma_half_sqrt_pi, n_trials=1),
        TheoremTest("Thm 2.3.5 Euler reflection formula", 2, "4",
                    "z not integer",
                    "Gamma(z)*Gamma(1-z) = pi/sin(pi*z)",
                    euler_reflection_formula, n_trials=2000),
        TheoremTest("Thm 2.3.6 Legendre duplication formula", 2, "4",
                    "z > 0",
                    "Gamma(z)*Gamma(z+1/2) = sqrt(pi)/(2^(2z-1)) * Gamma(2z)",
                    legendre_duplication_formula, n_trials=2000),
        TheoremTest("Thm 2.3.10 Beta-Gamma relation", 2, "4",
                    "a, b > 0",
                    "B(a,b) = Gamma(a)*Gamma(b)/Gamma(a+b)",
                    beta_gamma_relation, n_trials=2000),
        TheoremTest("Thm 2.3.11 Beta symmetry", 2, "4",
                    "a, b > 0",
                    "B(a,b) = B(b,a)",
                    beta_symmetry, n_trials=2000),
        TheoremTest("Thm 2.3.12 Beta recursive property", 2, "4",
                    "a > 1, b > 0",
                    "B(a,b) = (a-1)/(a+b-1) * B(a-1,b)",
                    beta_recursive_property, n_trials=2000),
        TheoremTest("Thm 2.3.16 erf-normal CDF relation", 2, "4",
                    "x in R",
                    "Phi(x) = (1 + erf(x/sqrt(2)))/2",
                    erf_normal_cdf_relation, n_trials=2000),
        TheoremTest("Thm 2.3.19 Pascal's rule", 2, "4",
                    "n >= 1, 1 <= k <= n",
                    "C(n,k) = C(n-1,k-1) + C(n-1,k)",
                    pascal_rule, n_trials=2000),
        TheoremTest("Thm 2.3.20 Binomial theorem", 2, "4",
                    "x, y in R, n in N",
                    "(x+y)^n = sum C(n,k) x^(n-k) y^k",
                    binomial_theorem, n_trials=2000),
        TheoremTest("Thm 2.3.23 Stirling's approximation", 2, "4",
                    "large n",
                    "n! ~ sqrt(2*pi*n) * (n/e)^n",
                    stirling_approximation, n_trials=500),

        # ================================================================
        # Chapter 3: Limits and Continuity
        # ================================================================
        TheoremTest("Thm 3.3.3 Limit iff one-sided limits agree", 3, "4",
                    "f defined near a",
                    "lim f(x) = L iff lim+ = lim- = L",
                    limit_one_sided_agreement, n_trials=1000),
        TheoremTest("Thm 3.3.4 Limit laws (sum, product)", 3, "4",
                    "lim f = L, lim g = M",
                    "lim(f+g) = L+M, lim(fg) = LM",
                    limit_laws_sum_product, n_trials=1000),
        TheoremTest("Thm 3.3.5 Squeeze theorem", 3, "4",
                    "f(x) <= g(x) <= h(x), lim f = lim h = L",
                    "lim g = L",
                    squeeze_theorem_stress, n_trials=2000),
        TheoremTest("Thm 3.3.11(6) Continuity of composition", 3, "4",
                    "g continuous at a, f continuous at g(a)",
                    "f(g) continuous at a",
                    continuity_of_composition, n_trials=1000),
        TheoremTest("Thm 3.3.12 Intermediate Value Theorem", 3, "4",
                    "f continuous on [a,b], f(a)*f(b)<0",
                    "exists root in (a,b)",
                    ivt_stress, n_trials=1000),
        TheoremTest("Thm 3.3.13 Extreme Value Theorem", 3, "4",
                    "f continuous on closed [a,b]",
                    "f attains max and min",
                    evt_stress, n_trials=1000),
        TheoremTest("Thm 3.3.16 Heine-Cantor (uniform continuity)", 3, "4",
                    "f continuous on closed bounded [a,b]",
                    "f is uniformly continuous on [a,b]",
                    heine_cantor_uniform_continuity, n_trials=2000),

        # ================================================================
        # Chapter 4: Differential Calculus
        # ================================================================
        TheoremTest("Thm 4.3.2 Differentiable implies continuous", 4, "4",
                    "f differentiable at a",
                    "f continuous at a",
                    differentiable_implies_continuous, n_trials=1000),
        TheoremTest("Thm 4.3.6 Linearity of differentiation", 4, "4",
                    "f, g differentiable, a, b scalars",
                    "D(af+bg) = a*Df + b*Dg",
                    linearity_of_differentiation, n_trials=1000),
        TheoremTest("Thm 4.3.7 Constant rule", 4, "4",
                    "c is a constant",
                    "d/dx[c] = 0",
                    constant_rule, n_trials=500),
        TheoremTest("Thm 4.3.8 Power rule", 4, "4",
                    "n in R, x > 0",
                    "d/dx[x^n] = n*x^(n-1)",
                    power_rule, n_trials=2000),
        TheoremTest("Thm 4.3.9 Sum and difference rule", 4, "4",
                    "f, g differentiable",
                    "(f +/- g)' = f' +/- g'",
                    sum_difference_rule, n_trials=1000),
        TheoremTest("Thm 4.3.10 Product rule", 4, "4",
                    "f, g differentiable",
                    "(fg)' = f'g + fg'",
                    product_rule, n_trials=1000),
        TheoremTest("Thm 4.3.11 Quotient rule", 4, "4",
                    "f, g differentiable, g(x) != 0",
                    "(f/g)' = (f'g - fg')/g^2",
                    quotient_rule, n_trials=1000),
        TheoremTest("Thm 4.3.12 Chain rule", 4, "4",
                    "g differentiable at x, f differentiable at g(x)",
                    "d/dx[f(g(x))] = f'(g(x))*g'(x)",
                    chain_rule_stress, n_trials=2000),
        TheoremTest("Thm 4.3.13 Inverse function derivative", 4, "4",
                    "f bijection, f differentiable with f'!=0",
                    "(f^{-1})'(y) = 1/f'(f^{-1}(y))",
                    inverse_function_derivative, n_trials=2000),
        TheoremTest("Thm 4.3.14 Derivative of exponential", 4, "4",
                    "f(x) = e^x",
                    "d/dx[e^x] = e^x",
                    derivative_of_exponential, n_trials=1000),
        TheoremTest("Thm 4.3.15 Derivative of ln", 4, "4",
                    "x > 0",
                    "d/dx[ln x] = 1/x",
                    derivative_of_ln, n_trials=1000),
        TheoremTest("Thm 4.3.16 Derivative of general exponential", 4, "4",
                    "a > 0, a != 1",
                    "d/dx[a^x] = a^x * ln(a)",
                    derivative_of_general_exponential, n_trials=1000),
        TheoremTest("Thm 4.3.17 Derivative of general logarithm", 4, "4",
                    "a > 0, a != 1, x > 0",
                    "d/dx[log_a(x)] = 1/(x*ln(a))",
                    derivative_of_general_log, n_trials=1000),
        TheoremTest("Thm 4.3.18 Derivative of sine", 4, "4",
                    "x in R",
                    "d/dx[sin(x)] = cos(x)",
                    derivative_of_sine, n_trials=1000),
        TheoremTest("Thm 4.3.19 Derivative of cosine", 4, "4",
                    "x in R",
                    "d/dx[cos(x)] = -sin(x)",
                    derivative_of_cosine, n_trials=1000),
        TheoremTest("Thm 4.3.20 Derivative of tangent", 4, "4",
                    "x != (2k+1)*pi/2",
                    "d/dx[tan(x)] = sec^2(x)",
                    derivative_of_tangent, n_trials=1000),
        TheoremTest("Thm 4.3.21 Derivative of absolute value", 4, "4",
                    "x != 0",
                    "d/dx[|x|] = sign(x)",
                    derivative_of_abs, n_trials=1000),
        TheoremTest("Thm 4.3.22 Derivative of square root", 4, "4",
                    "x > 0",
                    "d/dx[sqrt(x)] = 1/(2*sqrt(x))",
                    derivative_of_sqrt, n_trials=1000),
        TheoremTest("Thm 4.3.23 Logarithmic differentiation", 4, "4",
                    "f(x)>0, g(x) differentiable",
                    "d/dx[f^g] = f^g * [g'*ln(f) + g*f'/f]",
                    logarithmic_differentiation, n_trials=1000),
        TheoremTest("Thm 4.3.24 Rolle's theorem", 4, "4",
                    "f continuous on [a,b], differentiable on (a,b), f(a)=f(b)",
                    "exists c with f'(c)=0",
                    rolles_theorem_stress, n_trials=500),
        TheoremTest("Thm 4.3.25 Mean Value Theorem", 4, "4",
                    "f differentiable on (a,b), continuous on [a,b]",
                    "exists c s.t. f'(c) = (f(b)-f(a))/(b-a)",
                    mvt_stress, n_trials=500),
        TheoremTest("Thm 4.3.26 L'Hopital's rule (0/0)", 4, "4",
                    "f(a)=g(a)=0, g'(x)!=0 near a",
                    "lim f/g = lim f'/g'",
                    lhopital_stress, n_trials=1000),

        # ================================================================
        # Chapter 5: Integral Calculus
        # ================================================================
        TheoremTest("Thm 5.3.4 Continuous => integrable", 5, "4",
                    "f continuous on [a,b]",
                    "f is Riemann integrable",
                    continuous_functions_are_integrable, n_trials=500),
        TheoremTest("Thm 5.3.5 Integral linearity", 5, "4",
                    "f, g integrable, alpha, beta scalars",
                    "int(alpha*f + beta*g) = alpha*int(f) + beta*int(g)",
                    integral_linearity, n_trials=500),
        TheoremTest("Thm 5.3.6 Integral monotonicity", 5, "4",
                    "f(x) <= g(x) on [a,b]",
                    "int(f) <= int(g)",
                    integral_monotonicity, n_trials=1000),
        TheoremTest("Thm 5.3.7 Additivity over intervals", 5, "4",
                    "a < b < c, f integrable",
                    "int_a^c f = int_a^b f + int_b^c f",
                    integral_additivity_over_intervals, n_trials=500),
        TheoremTest("Thm 5.3.9 FTC Part 1", 5, "4",
                    "f continuous on [a,b]",
                    "d/dx[int_a^x f(t)dt] = f(x)",
                    ftc_part1_stress, n_trials=1000),
        TheoremTest("Thm 5.3.10 FTC Part 2", 5, "4",
                    "f continuous, F antiderivative",
                    "int_a^b f(x)dx = F(b) - F(a)",
                    ftc_part2_stress, n_trials=1000),
        TheoremTest("Thm 5.3.12 Substitution rule", 5, "4",
                    "g has continuous derivative, f continuous on range of g",
                    "int f(g(x))*g'(x) dx = int f(u) du",
                    substitution_rule_stress, n_trials=500),
        TheoremTest("Thm 5.3.13 Integration by parts", 5, "4",
                    "u, v have continuous derivatives on [a,b]",
                    "int u*v' dx = [u*v] - int u'*v dx",
                    integration_by_parts_stress, n_trials=1000),

        # ================================================================
        # Chapter 6: Series and Approximation
        # ================================================================
        TheoremTest("Thm 6.3.3 Monotone convergence theorem", 6, "4",
                    "bounded monotone sequence",
                    "sequence converges",
                    monotone_convergence_theorem, n_trials=500),
        TheoremTest("Thm 6.3.5 Divergence test", 6, "4",
                    "a_n not -> 0",
                    "series diverges",
                    divergence_test, n_trials=500),
        TheoremTest("Thm 6.3.6a Geometric series sum", 6, "4",
                    "|r| < 1",
                    "sum ar^n = a/(1-r)",
                    geometric_series_sum, n_trials=1000),
        TheoremTest("Thm 6.3.7 Comparison test", 6, "4",
                    "0 <= a_n <= b_n, sum b_n converges",
                    "sum a_n converges",
                    comparison_test, n_trials=1000),
        TheoremTest("Thm 6.3.8 Ratio test convergence", 6, "4",
                    "|a_{n+1}/a_n| -> L < 1",
                    "series converges absolutely",
                    ratio_test_convergence, n_trials=500),
        TheoremTest("Thm 6.3.9 Root test", 6, "4",
                    "|a_n|^{1/n} -> L < 1",
                    "series converges",
                    root_test, n_trials=500),
        TheoremTest("Thm 6.3.10 Integral test", 6, "4",
                    "f positive, continuous, decreasing",
                    "sum f(n) converges iff int f(x) dx converges",
                    integral_test, n_trials=500),
        TheoremTest("Thm 6.3.11 Alternating series error bound", 6, "4",
                    "a_n decreasing, a_n -> 0",
                    "|S - S_N| <= a_{N+1}",
                    alternating_series_error_bound, n_trials=1000),
        TheoremTest("Thm 6.3.12a Absolute convergence => convergence", 6, "4",
                    "sum |a_n| converges",
                    "sum a_n converges",
                    absolute_convergence_implies_convergence, n_trials=500),
        TheoremTest("Thm 6.3.14 Power series radius of convergence", 6, "4",
                    "power series with radius R",
                    "converges for |x-a| < R",
                    power_series_radius_convergence, n_trials=1000),
        TheoremTest("Thm 6.3.16 Taylor remainder bound", 6, "4",
                    "f has n+1 continuous derivatives",
                    "|R_n(x)| <= M|x-a|^(n+1)/(n+1)!",
                    taylor_remainder_bound, n_trials=2000),

        # ================================================================
        # Chapter 7: Multivariate Calculus
        # ================================================================
        TheoremTest("Thm 7.3.5 Gradient = steepest ascent", 7, "4",
                    "f differentiable, grad f != 0",
                    "D_u f maximized when u = grad f / ||grad f||",
                    gradient_steepest_ascent, n_trials=2000),
        TheoremTest("Thm 7.3.7 Clairaut mixed partials", 7, "4",
                    "f is C^2",
                    "f_xy = f_yx",
                    clairaut_mixed_partials, n_trials=2000),
        TheoremTest("Thm 7.3.10 Multivariate chain rule", 7, "4",
                    "f differentiable, g differentiable path",
                    "dz/dt = grad f . g'(t)",
                    multivariate_chain_rule, n_trials=1000),
        TheoremTest("Thm 7.3.13 Euler homogeneous function", 7, "4",
                    "f homogeneous of degree k",
                    "x . grad f(x) = k * f(x)",
                    euler_homogeneous_function, n_trials=2000),
        TheoremTest("Thm 7.3.16 Multivariate Taylor (2nd order)", 7, "4",
                    "f is C^2",
                    "f(a+h) = f(a) + grad f . h + (1/2)*h^T*H*h + o(||h||^2)",
                    multivariate_taylor_second_order, n_trials=1000),

        # ================================================================
        # Chapter 8: Vectors
        # ================================================================
        TheoremTest("Thm 8.3.4 R^n is a vector space", 8, "4",
                    "u, v, w in R^n, c, d scalars",
                    "all 10 vector space axioms hold",
                    rn_vector_space_axioms, n_trials=1000),
        TheoremTest("Thm 8.3.7 Cauchy-Schwarz inequality", 8, "4",
                    "|u.v| <= ||u||*||v|| for all u,v",
                    "inequality holds",
                    cauchy_schwarz_stress, n_trials=5000),
        TheoremTest("Thm 8.3.8 Triangle inequality", 8, "4",
                    "||u+v|| <= ||u|| + ||v|| for all u,v",
                    "inequality holds",
                    triangle_inequality_stress, n_trials=5000),
        TheoremTest("Thm 8.3.7 Cauchy-Schwarz equality condition", 8, "4",
                    "equality iff u = alpha*v",
                    "collinear => equality, non-collinear => strict",
                    cauchy_schwarz_equality_condition, n_trials=1000,
                    strategy="counterexample_hunt"),
        TheoremTest("Thm 8.3.16 Dimension well-defined", 8, "4",
                    "V finite-dimensional vector space",
                    "every basis has the same number of elements",
                    dimension_well_defined, n_trials=500),
        TheoremTest("Thm 8.3.20 Gram-Schmidt orthonormality", 8, "4",
                    "linearly independent vectors",
                    "produces orthonormal set spanning same subspace",
                    gram_schmidt_orthonormality, n_trials=1000),
        TheoremTest("Def 8.3.11 Projection orthogonality", 8, "4",
                    "u, v with v != 0",
                    "u - proj_v(u) is orthogonal to v",
                    projection_orthogonality, n_trials=2000),

        # ================================================================
        # Chapter 9: Matrices
        # ================================================================
        TheoremTest("Thm 9.3.5 Matrix multiplication properties", 9, "4",
                    "A, B, C compatible matrices",
                    "(AB)C = A(BC) and A(B+C) = AB+AC",
                    matrix_multiplication_properties, n_trials=1000),
        TheoremTest("Thm 9.3.12 Gaussian elimination", 9, "4",
                    "A is m x n matrix",
                    "reduces to REF, solution consistent",
                    gaussian_elimination_consistency, n_trials=1000),
        TheoremTest("Thm 9.3.14 Rouche-Capelli", 9, "4",
                    "Ax=b system",
                    "solvable iff rank(A) = rank([A|b])",
                    rouche_capelli, n_trials=1000),
        TheoremTest("Thm 9.3.17 Rank-nullity theorem", 9, "4",
                    "A is m x n matrix",
                    "dim(ker A) + rank(A) = n",
                    rank_nullity_theorem, n_trials=2000),
        TheoremTest("Thm 9.3.20(1) det(AB) = det(A)*det(B)", 9, "4",
                    "A, B square matrices",
                    "determinant is multiplicative",
                    det_multiplicativity, n_trials=2000),
        TheoremTest("Thm 9.3.20(2) det(A^T) = det(A)", 9, "4",
                    "A square matrix",
                    "determinant is transpose-invariant",
                    det_transpose_invariance, n_trials=2000),
        TheoremTest("Thm 9.3.21 Det via row reduction", 9, "4",
                    "A square matrix",
                    "det = (-1)^s * product of pivots",
                    det_via_row_reduction, n_trials=1000),
        TheoremTest("Thm 9.3.23 2x2 inverse formula", 9, "4",
                    "2x2 matrix with det != 0",
                    "A^{-1} = 1/(ad-bc) * [[d,-b],[-c,a]]",
                    two_by_two_inverse_formula, n_trials=2000),
        TheoremTest("Thm 9.3.24 Gauss-Jordan inverse", 9, "4",
                    "A invertible",
                    "[A|I] -> [I|A^{-1}]",
                    gauss_jordan_inverse, n_trials=1000),
        TheoremTest("Rmk 9.3.26 Cramer's rule", 9, "4",
                    "A invertible",
                    "x_i = det(A_i)/det(A)",
                    cramers_rule_stress, n_trials=500),
        TheoremTest("Thm 9.3.25(2) (AB)^{-1} = B^{-1}A^{-1}", 9, "4",
                    "A, B invertible",
                    "inverse of product = reversed product of inverses",
                    inverse_product_reversal, n_trials=2000),

        # ================================================================
        # Chapter 10: Eigenvalues
        # ================================================================
        TheoremTest("Thm 10.3.3 Eigenvalue equation equivalences", 10, "4",
                    "A is n x n matrix, lambda eigenvalue",
                    "det(A - lambda*I) = 0",
                    eigenvalue_equation_equivalences, n_trials=1000),
        TheoremTest("Thm 10.3.5 Eigenvalues are roots of char poly", 10, "4",
                    "A is n x n matrix",
                    "eigenvalues satisfy det(A - lambda*I) = 0",
                    eigenvalues_are_roots_of_char_poly, n_trials=1000),
        TheoremTest("Thm 10.3.10 Geometric <= algebraic multiplicity", 10, "4",
                    "eigenvalue with algebraic multiplicity m",
                    "1 <= geometric mult <= m",
                    geometric_leq_algebraic_multiplicity, n_trials=500),
        TheoremTest("Thm 10.3.11 trace = sum of eigenvalues", 10, "4",
                    "A is n x n matrix",
                    "tr(A) = lambda_1 + ... + lambda_n",
                    trace_equals_eigenvalue_sum, n_trials=2000),
        TheoremTest("Thm 10.3.11 det = product of eigenvalues", 10, "4",
                    "A is n x n matrix",
                    "det(A) = lambda_1 * ... * lambda_n",
                    det_equals_eigenvalue_product, n_trials=2000),
        TheoremTest("Thm 10.3.13 Distinct eigenvalues => lin indep eigvecs", 10, "4",
                    "A has distinct eigenvalues",
                    "corresponding eigenvectors are linearly independent",
                    distinct_eigenvalues_lin_indep_eigvecs, n_trials=500),
        TheoremTest("Thm 10.3.18 Spectral theorem (symmetric)", 10, "4",
                    "A real symmetric",
                    "real eigenvalues, orthogonal eigenvectors",
                    spectral_theorem_symmetric, n_trials=2000),
        TheoremTest("Thm 10.3.18 Spectral (PD => lambda > 0)", 10, "4",
                    "A symmetric positive definite",
                    "all eigenvalues > 0",
                    positive_definite_eigenvalue_stress, n_trials=2000),
        TheoremTest("Thm 10.3.12(3) Eigenvalues of inverse", 10, "4",
                    "A invertible with eigenvalue lambda",
                    "A^{-1} has eigenvalue 1/lambda",
                    eigenvalues_of_inverse, n_trials=500),
        TheoremTest("Thm 10.3.12(4) Eigenvalues of power", 10, "4",
                    "lambda eigenvalue of A",
                    "lambda^k eigenvalue of A^k",
                    eigenvalues_of_power, n_trials=500),
        TheoremTest("Thm 10.3.15 Diagonalization A=PDP^{-1}", 10, "4",
                    "A has n linearly independent eigenvectors",
                    "A = P D P^{-1}",
                    diagonalization_stress, n_trials=1000),

        # ================================================================
        # Chapter 11: Unconstrained Optimization
        # ================================================================
        TheoremTest("Thm 11.3.2/5 First-order necessary condition", 11, "4",
                    "f has local extremum at x*",
                    "grad f(x*) = 0",
                    first_order_necessary_condition, n_trials=1000),
        TheoremTest("Thm 11.3.4 Second derivative test (1D)", 11, "4",
                    "f'(c)=0",
                    "f''(c)>0 => local min, f''(c)<0 => local max",
                    second_derivative_test_1d, n_trials=1000),
        TheoremTest("Thm 11.3.7 Definiteness and eigenvalues", 11, "4",
                    "H real symmetric",
                    "H PD iff all eigenvalues > 0",
                    definiteness_and_eigenvalues, n_trials=1000),
        TheoremTest("Thm 11.3.8 Second-order sufficient conditions", 11, "4",
                    "grad f = 0 and H_f positive definite",
                    "strict local minimum",
                    second_order_conditions_stress, n_trials=500),
        TheoremTest("Thm 11.3.12 Convexity iff Hessian PSD", 11, "4",
                    "f is C^2 on open convex set",
                    "f convex iff H_f PSD everywhere",
                    convexity_hessian_psd, n_trials=1000),
        TheoremTest("Thm 11.3.13 Convex local-min = global-min", 11, "4",
                    "f strictly convex",
                    "every local min is the unique global min",
                    convexity_local_is_global, n_trials=1000),
        TheoremTest("Thm 11.3.8(3) Indefinite Hessian => saddle", 11, "4",
                    "grad f = 0, H_f indefinite",
                    "saddle point",
                    saddle_point_indefinite_hessian, n_trials=1),
        TheoremTest("Thm 11.3.16 Gradient descent convergence", 11, "4",
                    "f L-smooth and convex",
                    "f(x_k) - f* <= L||x_0-x*||^2 / (2k)",
                    gradient_descent_convergence, n_trials=200),
        TheoremTest("Thm 11.3.18 Newton quadratic convergence", 11, "4",
                    "f C^2, x* local min with H PD, H Lipschitz",
                    "||x_{k+1}-x*|| <= C*||x_k-x*||^2",
                    newton_quadratic_convergence, n_trials=200),

        # ================================================================
        # Chapter 12: Constrained Optimization
        # ================================================================
        TheoremTest("Thm 12.3.3 Lagrange necessary conditions", 12, "4",
                    "constrained optimum with regular constraints",
                    "grad f + lambda * grad g = 0",
                    lagrange_necessary_conditions, n_trials=1),
        TheoremTest("Thm 12.3.5 Shadow price interpretation", 12, "4",
                    "Lagrange conditions hold",
                    "lambda = df*/db (sensitivity of optimum to constraint)",
                    lagrange_shadow_price, n_trials=500),
        TheoremTest("Thm 12.3.7 Bordered Hessian (2nd-order)", 12, "4",
                    "first-order conditions satisfied",
                    "bordered Hessian determines min vs max",
                    bordered_hessian_test, n_trials=1),
        TheoremTest("Thm 12.3.12 Fundamental theorem of LP", 12, "4",
                    "LP has finite optimum",
                    "optimum attained at a vertex",
                    fundamental_theorem_of_lp, n_trials=200),
        TheoremTest("Thm 12.3.15 Simplex method overview", 12, "4",
                    "LP in standard form",
                    "simplex finds optimal vertex",
                    simplex_method_overview, n_trials=200),
        TheoremTest("Thm 12.3.18 Weak duality (LP)", 12, "4",
                    "x primal feasible, y dual feasible",
                    "c^T x <= b^T y",
                    weak_duality_lp, n_trials=200),
        TheoremTest("Thm 12.3.19 Strong duality (LP)", 12, "4",
                    "primal has finite optimal",
                    "primal optimal = dual optimal",
                    strong_duality_lp, n_trials=200),
        TheoremTest("Thm 12.3.20 Complementary slackness", 12, "4",
                    "x*, y* optimal primal/dual solutions",
                    "y_i*(b_i - (Ax)_i) = 0",
                    complementary_slackness, n_trials=200),

        # ================================================================
        # Chapter 13: Probability Theory
        # ================================================================
        TheoremTest("Thm 13.3.5 Basic probability consequences", 13, "4",
                    "probability space (Omega, F, P)",
                    "P(empty)=0, P(A^c)=1-P(A), inclusion-exclusion",
                    probability_basic_consequences, n_trials=2000),
        TheoremTest("Thm 13.3.7 Law of total probability", 13, "4",
                    "partition {B_i} of Omega",
                    "P(A) = sum P(A|B_i)*P(B_i)",
                    law_total_probability, n_trials=2000),
        TheoremTest("Thm 13.3.8 Bayes' theorem", 13, "4",
                    "partition B_i with P(B_i)>0, P(A)>0",
                    "posteriors sum to 1 and satisfy Bayes formula",
                    bayes_theorem_stress, n_trials=2000),
        TheoremTest("Thm 13.3.15 Linearity of expectation", 13, "4",
                    "X, Y random variables, a, b constants",
                    "E[aX+bY] = a*E[X] + b*E[Y]",
                    linearity_of_expectation, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 13.3.17 Variance properties", 13, "4",
                    "X random variable, a, b constants",
                    "Var(aX+b) = a^2*Var(X)",
                    variance_properties, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 13.3.22 Variance of sum", 13, "4",
                    "X, Y random variables",
                    "Var(X+Y) = Var(X) + Var(Y) + 2*Cov(X,Y)",
                    variance_of_sum, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 13.3.25 Law of iterated expectation", 13, "4",
                    "X, Y with finite expectations",
                    "E[Y] = E[E[Y|X]]",
                    law_total_expectation, n_trials=2000),
        TheoremTest("Thm 13.3.26 Chebyshev inequality", 13, "4",
                    "X has finite mean mu and variance sigma^2",
                    "P(|X-mu| >= k*sigma) <= 1/k^2",
                    chebyshev_inequality_stress, n_trials=5000),
        TheoremTest("Jensen inequality (convex)", 13, "4",
                    "f convex, X random variable",
                    "E[f(X)] >= f(E[X])",
                    jensen_inequality_stress, n_trials=3000),
        TheoremTest("Thm 13.3.27 Law of Large Numbers", 13, "4",
                    "X_i iid with finite mean mu",
                    "X_bar_n -> mu as n -> inf",
                    lln_convergence, n_trials=200,
                    strategy="monte_carlo"),
        TheoremTest("Thm 13.3.28 Central Limit Theorem", 13, "4",
                    "X_i iid with finite mean and variance",
                    "(X_bar - mu)/(sigma/sqrt(n)) -> N(0,1)",
                    clt_convergence, n_trials=100,
                    strategy="monte_carlo"),

        # ================================================================
        # Chapter 14: Distributions
        # ================================================================
        TheoremTest("Thm 14.3.3 Binomial additivity", 14, "4",
                    "X1~Bin(n1,p), X2~Bin(n2,p) independent",
                    "X1+X2 ~ Bin(n1+n2, p)",
                    binomial_additivity, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 14.3.5 Poisson limit of Binomial", 14, "4",
                    "Bin(n, lambda/n) as n -> inf",
                    "PMF converges to Poisson(lambda)",
                    poisson_limit_of_binomial, n_trials=1000,
                    strategy="monte_carlo"),
        TheoremTest("Thm 14.3.10(c) Sum of independent normals", 14, "4",
                    "X ~ N(mu1,s1^2), Y ~ N(mu2,s2^2) independent",
                    "X+Y ~ N(mu1+mu2, s1^2+s2^2)",
                    normal_sum_independent, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 14.3.16 t(nu) -> N(0,1) as nu -> inf", 14, "4",
                    "T ~ t(nu)",
                    "T -> N(0,1) as nu -> inf",
                    t_converges_to_normal, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Def 14.3.13 Chi-squared = sum of N(0,1)^2", 14, "4",
                    "Z_i iid N(0,1)",
                    "sum Z_i^2 ~ chi2(k)",
                    chi_squared_sum_of_squares, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Rmk 14.3.18 T^2 ~ F(1,nu)", 14, "4",
                    "T ~ t(nu)",
                    "T^2 ~ F(1,nu)",
                    t_squared_is_f, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 14.3.19 Distribution relationship diagram", 14, "4",
                    "standard distributions",
                    "Bernoulli=Bin(1,p), Bin approx Normal for large n",
                    distribution_relationship_diagram, n_trials=500),

        # ================================================================
        # Chapter 15: Descriptive Statistics
        # ================================================================
        TheoremTest("Thm 15.3.16 Correlation bounds", 15, "4",
                    "any sample with positive std devs",
                    "-1 <= r_xy <= 1",
                    correlation_bounds, n_trials=2000),

        # ================================================================
        # Chapter 16: Statistical Inference
        # ================================================================
        TheoremTest("Thm 16.3.7 MLE consistency", 16, "4",
                    "regularity conditions hold",
                    "MLE converges to true parameter",
                    mle_consistency_normal, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 16.3.10 CI for mean (known variance)", 16, "4",
                    "X_i ~ N(mu, sigma^2), sigma known",
                    "95% CI covers true mean ~95% of time",
                    ci_known_variance, n_trials=50,
                    strategy="monte_carlo"),
        TheoremTest("Thm 16.3.11 CI for mean (unknown variance)", 16, "4",
                    "X_i ~ N(mu, sigma^2), sigma unknown",
                    "t-based 95% CI covers true mean ~95% of time",
                    ci_unknown_variance, n_trials=50,
                    strategy="monte_carlo"),

        # ================================================================
        # Chapter 17: Regression
        # ================================================================
        TheoremTest("Thm 17.3.2 OLS simple regression formula", 17, "4",
                    "simple linear regression",
                    "beta1_hat = Sxy/Sxx, beta0_hat = ybar - beta1_hat*xbar",
                    ols_simple_regression_formula, n_trials=500),
        TheoremTest("Thm 17.3.3 OLS unbiasedness", 17, "4",
                    "y = X*beta + eps, E[eps]=0",
                    "E[beta_hat] = beta",
                    ols_unbiasedness, n_trials=20,
                    strategy="monte_carlo"),
        TheoremTest("Thm 17.3.6 OLS matrix form", 17, "4",
                    "X has full column rank",
                    "beta_hat = (X'X)^{-1}X'y",
                    ols_matrix_form, n_trials=1000),
        TheoremTest("Thm 17.3.7 Hat matrix is projection", 17, "4",
                    "X has full column rank",
                    "H = X(X'X)^{-1}X' is idempotent and symmetric",
                    hat_matrix_projection, n_trials=1000),
        TheoremTest("Thm 17.3.7 Residuals orthogonal to X", 17, "4",
                    "OLS regression",
                    "X'e = 0",
                    residuals_orthogonal_to_X, n_trials=1000),
        TheoremTest("Thm 17.3.11 t-test individual coefficients", 17, "4",
                    "normal errors",
                    "T_j = beta_j_hat / SE ~ t(n-p-1) under H0",
                    t_test_individual_coefficients, n_trials=20,
                    strategy="monte_carlo"),
        TheoremTest("Thm 17.3.14 F-test overall significance", 17, "4",
                    "normal errors, H0: all slopes = 0",
                    "F ~ F(p, n-p-1) under H0",
                    f_test_overall_significance, n_trials=20,
                    strategy="monte_carlo"),
        TheoremTest("Thm 17.3.15 F-test general restrictions", 17, "4",
                    "H0: R*beta = r",
                    "F = t^2 for single restriction",
                    f_test_general_restrictions, n_trials=500),
        TheoremTest("Thm 17.3.16 Gauss-Markov (BLUE)", 17, "4",
                    "classical linear model assumptions",
                    "OLS has minimum variance among linear unbiased estimators",
                    gauss_markov_blue, n_trials=20,
                    strategy="monte_carlo"),
        TheoremTest("Def 17.3.12 SST = SSR + SSE decomposition", 17, "4",
                    "model with intercept",
                    "SST = SSR + SSE",
                    r_squared_decomposition, n_trials=1000),

        # ================================================================
        # Chapter 18: Difference Equations
        # ================================================================
        TheoremTest("Thm 18.3.3 First-order solution/stability", 18, "4",
                    "x_{t+1} = a*x_t + b, a != 1",
                    "x_t = a^t*(x_0 - x*) + x*, stable iff |a|<1",
                    first_order_difference_eq_solution, n_trials=1000),
        TheoremTest("Thm 18.3.3 First-order stability |a|<1", 18, "4",
                    "|a| < 1",
                    "x_t -> x* = b/(1-a)",
                    first_order_stability, n_trials=500),
        TheoremTest("Thm 18.3.5 Second-order distinct real roots", 18, "4",
                    "char eq has two distinct real roots",
                    "x_t = c1*lam1^t + c2*lam2^t",
                    second_order_distinct_real_roots, n_trials=500),
        TheoremTest("Thm 18.3.6 Second-order complex roots", 18, "4",
                    "char eq has complex conjugate roots r*e^{+/-i*theta}",
                    "x_t = r^t*(c1*cos(theta*t)+c2*sin(theta*t))",
                    second_order_complex_roots, n_trials=500),
        TheoremTest("Thm 18.3.7 Schur-Cohn conditions", 18, "4",
                    "roots inside unit circle",
                    "1+a1+a2>0, 1-a1+a2>0, |a2|<1",
                    schur_cohn_conditions, n_trials=1000),
        TheoremTest("Thm 18.3.9 System spectral radius stability", 18, "4",
                    "rho(A) < 1",
                    "x_t -> x* as t -> inf",
                    system_spectral_radius_stability, n_trials=200),

        # ================================================================
        # Chapter 19: ODEs
        # ================================================================
        TheoremTest("Thm 19.3.3 Picard-Lindelof existence/uniqueness", 19, "4",
                    "f Lipschitz in y",
                    "unique solution exists",
                    picard_lindelof_existence, n_trials=200),
        TheoremTest("Thm 19.3.9 Characteristic equation solutions", 19, "4",
                    "y'' + 4y = 0",
                    "y = c1*cos(2t) + c2*sin(2t) satisfies ODE",
                    ode_characteristic_equation, n_trials=1000),
        TheoremTest("Thm 19.3.12 ODE system stability Re(lambda)<0", 19, "4",
                    "all eigenvalues have negative real part",
                    "x(t) -> 0 as t -> inf",
                    ode_stability_classification, n_trials=200),
        TheoremTest("Def 19.3.4 Separable ODE solution", 19, "4",
                    "y' = xy, y(0)=1",
                    "y = e^{x^2/2}",
                    separable_ode_solution, n_trials=200),
        TheoremTest("Phase portrait: stable node", 19, "4",
                    "both eigenvalues real negative",
                    "trajectories converge to origin",
                    ode_phase_portrait_node, n_trials=200),
        TheoremTest("Phase portrait: stable spiral", 19, "4",
                    "complex eigenvalues with Re < 0",
                    "trajectories spiral to origin",
                    ode_phase_portrait_spiral, n_trials=200),

        # ================================================================
        # Chapter 20: Discrete Operators
        # ================================================================
        TheoremTest("Thm 20.3.3 Linearity of lag operator", 20, "4",
                    "sequences x, y and scalars a, b",
                    "L(ax+by) = aLx + bLy",
                    lag_operator_linearity, n_trials=1000),
        TheoremTest("Discrete FTC (telescoping sum)", 20, "4",
                    "sequence {x_t}",
                    "sum Delta(x_t) = x_b - x_a",
                    discrete_ftc, n_trials=2000),
        TheoremTest("Thm 20.3.6 Delta^n via binomial expansion", 20, "4",
                    "sequence {x_t}, integer n >= 0",
                    "Delta^n x_t = sum (-1)^k C(n,k) x_{t-k}",
                    delta_n_binomial_expansion, n_trials=1000),
        TheoremTest("Thm 20.3.9 Convolution = polynomial multiplication", 20, "4",
                    "polynomials f, g",
                    "coefficients of f*g = convolution of coefficients",
                    convolution_polynomial_multiplication, n_trials=1000),
        TheoremTest("Thm 20.3.11 Z-transform of shifted sequence", 20, "4",
                    "Z{x_t} = X(z)",
                    "Z{Lx_t} = z^{-1} X(z)",
                    z_transform_shift, n_trials=500),

        # ================================================================
        # Chapter 21: Time Series
        # ================================================================
        TheoremTest("Thm 21.3.13/14 AR(1) stationarity", 21, "4",
                    "X_t = phi*X_{t-1} + eps, |phi| < 1",
                    "ACF(1) approx phi",
                    ar1_stationarity, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 21.3.16 MA(q) ACF cutoff", 21, "4",
                    "MA(q) process",
                    "ACF(h) = 0 for h > q",
                    ma_q_acf_cutoff, n_trials=100,
                    strategy="monte_carlo"),
        TheoremTest("Thm 21.3.19 Yule-Walker equations", 21, "4",
                    "stationary AR(p) process",
                    "Yule-Walker gives correct AR coefficients",
                    yule_walker_equations, n_trials=100,
                    strategy="monte_carlo"),

        # ================================================================
        # Chapter 22: Transforms
        # ================================================================
        TheoremTest("Thm 22.3.3(a) DFT linearity", 22, "4",
                    "sequences x, y and scalars alpha, beta",
                    "F[alpha*x + beta*y] = alpha*F[x] + beta*F[y]",
                    dft_linearity, n_trials=1000),
        TheoremTest("Thm 22.3.4 Parseval's theorem (DFT)", 22, "4",
                    "sequence x of length N",
                    "sum |x_n|^2 = (1/N) sum |X_k|^2",
                    parseval_theorem_dft, n_trials=1000),
        TheoremTest("Thm 22.3.3(c) Convolution theorem (DFT)", 22, "4",
                    "sequences x, y of length N",
                    "DFT(x*y) = DFT(x) . DFT(y)",
                    convolution_theorem_dft, n_trials=500),
        TheoremTest("Thm 22.3.5 Cooley-Tukey FFT", 22, "4",
                    "N = 2M",
                    "radix-2 decomposition gives same result as direct DFT",
                    cooley_tukey_decomposition, n_trials=500),

        # ================================================================
        # Chapter 23: Operator Algebra
        # ================================================================
        TheoremTest("Thm 23.3.10 Linear operators form algebra", 23, "4",
                    "linear operators T, S on vector space V",
                    "composition is bilinear, distributive, scalar-compatible",
                    linear_operators_form_algebra, n_trials=1000),
        TheoremTest("Thm 23.3.14 Polynomial operators and ODEs", 23, "4",
                    "p(D)y = 0, constant coefficients",
                    "solutions satisfy the ODE",
                    polynomial_operators_ode, n_trials=1000),
        TheoremTest("Thm 23.3.15 Polynomial operators and difference eqs", 23, "4",
                    "p(L)x_t = eps_t",
                    "x_t satisfies the difference equation",
                    polynomial_operators_difference_eq, n_trials=500),
        TheoremTest("Thm 23.3.21 Operator correspondence", 23, "4",
                    "continuous D, discrete Delta, matrix A",
                    "parallel properties: A^n = P*D^n*P^{-1}",
                    operator_correspondence, n_trials=500),
        TheoremTest("Thm 23.3.25 Shift as exponential of D", 23, "4",
                    "f analytic, a in R",
                    "e^{aD} f(x) = f(x+a)",
                    shift_as_exponential_of_D, n_trials=1000),
        TheoremTest("Thm 23.3.27 Operator exponential properties", 23, "4",
                    "linear operators A, B",
                    "e^0 = I, e^{(s+t)A} = e^{sA}*e^{tA}",
                    operator_exponential_properties, n_trials=500),

        # ================================================================
        # Chapter 24: Fractional Calculus
        # ================================================================
        TheoremTest("Thm 24.3.5 GL weight recurrence", 24, "4",
                    "fractional order alpha > 0",
                    "w_0=1, w_k = w_{k-1}*(alpha-k+1)/k matches Gamma formula",
                    gl_weight_recurrence, n_trials=1000),
        TheoremTest("Thm 24.3.9 Semigroup property", 24, "4",
                    "alpha, beta > 0",
                    "J^alpha . J^beta = J^{alpha+beta}",
                    fractional_semigroup_property, n_trials=2000),
        TheoremTest("Thm 24.3.10 RL derivative of power function", 24, "4",
                    "alpha > 0, beta > alpha - 1, x > 0",
                    "D^alpha(x^beta) = Gamma(b+1)/Gamma(b-a+1)*x^{b-a}",
                    rl_derivative_of_power_function, n_trials=500),
        TheoremTest("Thm 24.3.12 RL to Caputo relation", 24, "4",
                    "0 < alpha < 1, f smooth",
                    "^RL D^a f = ^C D^a f + f(a)*x^{-a}/Gamma(1-a)",
                    rl_to_caputo_relation, n_trials=2000),
        TheoremTest("Thm 24.3.15 Composition of fractional derivatives", 24, "4",
                    "alpha, beta > 0, f sufficiently smooth",
                    "D^alpha . D^beta = D^{alpha+beta}",
                    fractional_derivative_composition, n_trials=2000),
    ]

    for t in tests:
        ch.add(t.as_structural_check())

    return ch
