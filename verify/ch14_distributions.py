# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 14: Probability Distributions — verification."""

import math
import numpy as np
import scipy.stats
import scipy.special
import scipy.integrate
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(14, "Probability Distributions")

    # ===================================================================
    # LAYER 1: Symbolic — distribution mean/variance formulas
    # ===================================================================

    # --- Binomial mean = np, var = np(1-p) ---
    ch.add(SymbolicCheck(
        label="Binomial(n,p) mean = np",
        section="5",
        zero_expr=lambda: _binomial_mean(),
    ))

    ch.add(SymbolicCheck(
        label="Binomial(n,p) var = np(1-p)",
        section="5",
        zero_expr=lambda: _binomial_var(),
    ))

    # --- Poisson mean = var = lambda ---
    ch.add(SymbolicCheck(
        label="Poisson(lam) mean = lam",
        section="5",
        zero_expr=lambda: _poisson_mean(),
    ))

    # --- Uniform(a,b) mean = (a+b)/2, var = (b-a)^2/12 ---
    ch.add(SymbolicCheck(
        label="Uniform(a,b) mean = (a+b)/2",
        section="5",
        zero_expr=lambda: _uniform_mean(),
    ))

    ch.add(SymbolicCheck(
        label="Uniform(a,b) var = (b-a)^2/12",
        section="5",
        zero_expr=lambda: _uniform_var(),
    ))

    # --- Normal CDF identity: Phi(x) = (1 + erf(x/sqrt(2)))/2 ---
    ch.add(SymbolicCheck(
        label="Phi(x) = (1+erf(x/sqrt(2)))/2",
        section="5",
        zero_expr=lambda: _normal_cdf_erf(),
    ))

    # --- Normal symmetry: Phi(-x) = 1 - Phi(x) ---
    ch.add(NumericCheck(
        label="Normal symmetry: Phi(-1.5) = 1-Phi(1.5)",
        section="5",
        stated=float(1.0 - scipy.stats.norm.cdf(1.5)),
        computed=float(scipy.stats.norm.cdf(-1.5)),
        tolerance=1e-14,
    ))

    # --- t-distribution variance = nu/(nu-2) ---
    for nu in [5, 10, 30]:
        ch.add(NumericCheck(
            label=f"t({nu}) var = {nu}/{nu-2}",
            section="5",
            stated=float(nu) / (nu - 2),
            computed=float(scipy.stats.t.var(nu)),
            tolerance=1e-10,
        ))

    # --- Chi-squared mean = k, var = 2k ---
    for k in [3, 10, 20]:
        ch.add(NumericCheck(
            label=f"Chi2({k}) mean = {k}",
            section="5",
            stated=float(k),
            computed=float(scipy.stats.chi2.mean(k)),
            tolerance=1e-12,
        ))
        ch.add(NumericCheck(
            label=f"Chi2({k}) var = {2*k}",
            section="5",
            stated=float(2 * k),
            computed=float(scipy.stats.chi2.var(k)),
            tolerance=1e-12,
        ))

    # --- F distribution mean = d2/(d2-2) ---
    ch.add(NumericCheck(
        label="F(5,20) mean = 20/18",
        section="5",
        stated=20.0 / 18.0,
        computed=float(scipy.stats.f.mean(5, 20)),
        tolerance=1e-10,
    ))

    # --- 68-95-99.7 rule ---
    ch.add(NumericCheck(
        label="68-95-99.7: P(|Z|<1) ~ 0.6827",
        section="5",
        stated=0.6827,
        computed=float(2 * scipy.stats.norm.cdf(1) - 1),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="68-95-99.7: P(|Z|<2) ~ 0.9545",
        section="5",
        stated=0.9545,
        computed=float(2 * scipy.stats.norm.cdf(2) - 1),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="68-95-99.7: P(|Z|<3) ~ 0.9973",
        section="5",
        stated=0.9973,
        computed=float(2 * scipy.stats.norm.cdf(3) - 1),
        tolerance=1e-3,
    ))

    # ===================================================================
    # LAYER 2: Numerical worked examples
    # ===================================================================

    # --- Example 8.1: N(100,225) P(X<120) ---
    z = (120 - 100) / 15.0
    ch.add(NumericCheck(
        label="N(100,225) P(X<120) ~ 0.9088",
        section="8.1",
        stated=0.9088,
        computed=float(scipy.stats.norm.cdf(z)),
        tolerance=2e-3,
    ))

    # --- Example 8.2: Binom(10,0.5) P(X>=7) ---
    binom_upper = float(sum(scipy.stats.binom.pmf(k, 10, 0.5) for k in range(7, 11)))
    ch.add(NumericCheck(
        label="Binom(10,0.5) P(X>=7) = 176/1024",
        section="8.2",
        stated=176.0 / 1024.0,
        computed=binom_upper,
        tolerance=1e-10,
    ))

    # Verify individual terms
    ch.add(NumericCheck(
        label="Binom(10,0.5) P(X=7) = 120/1024",
        section="8.2",
        stated=120.0 / 1024.0,
        computed=float(scipy.stats.binom.pmf(7, 10, 0.5)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Binom(10,0.5) P(X=8) = 45/1024",
        section="8.2",
        stated=45.0 / 1024.0,
        computed=float(scipy.stats.binom.pmf(8, 10, 0.5)),
        tolerance=1e-10,
    ))

    # --- Example 8.3: Poisson(2.5) P(X=3) ---
    ch.add(NumericCheck(
        label="Poisson(2.5) P(X=3) ~ 0.2138",
        section="8.3",
        stated=0.2138,
        computed=float(scipy.stats.poisson.pmf(3, 2.5)),
        tolerance=1e-3,
    ))

    # Verify recurrence values
    ch.add(NumericCheck(
        label="Poisson(2.5) P(X=0) ~ 0.08208",
        section="8.3",
        stated=0.08208,
        computed=float(scipy.stats.poisson.pmf(0, 2.5)),
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Poisson(2.5) P(X=1) ~ 0.2052",
        section="8.3",
        stated=0.2052,
        computed=float(scipy.stats.poisson.pmf(1, 2.5)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Poisson(2.5) P(X=2) ~ 0.2565",
        section="8.3",
        stated=0.2565,
        computed=float(scipy.stats.poisson.pmf(2, 2.5)),
        tolerance=1e-3,
    ))

    # --- Example 8.4: t(10) 97.5th percentile ---
    ch.add(NumericCheck(
        label="t(10) Q(0.975) ~ 2.228",
        section="8.4",
        stated=2.228,
        computed=float(scipy.stats.t.ppf(0.975, 10)),
        tolerance=1e-3,
    ))

    # --- Example 8.5: t convergence table ---
    t_table = [(5, 2.571), (10, 2.228), (30, 2.042), (100, 1.984), (1000, 1.962)]
    for nu, stated_q in t_table:
        ch.add(NumericCheck(
            label=f"t({nu}) Q(0.975) ~ {stated_q}",
            section="8.5",
            stated=stated_q,
            computed=float(scipy.stats.t.ppf(0.975, nu)),
            tolerance=1e-3,
        ))

    # --- Table: relative difference column (Section 8.5, line 594) ---
    # The textbook rounds relative differences to 1 decimal place.
    # nu=1000: actual 0.1212%, textbook states 0.1%. Use wider tolerance.
    z_normal = float(scipy.stats.norm.ppf(0.975))
    stated_rel_diffs = [(5, 31.2, 0.01), (10, 13.7, 0.01), (30, 4.2, 0.02),
                        (100, 1.2, 0.05), (1000, 0.1, 0.25)]
    for nu, stated_pct, tol in stated_rel_diffs:
        q_t = float(scipy.stats.t.ppf(0.975, nu))
        rel_diff_pct = (q_t - z_normal) / z_normal * 100
        ch.add(NumericCheck(
            label=f"Table: t({nu}) vs N(0,1) rel diff = {stated_pct}%",
            section="8.5",
            stated=stated_pct,
            computed=rel_diff_pct,
            tolerance=tol,
            note="t-convergence table relative difference column",
        ))

    # --- Example 8.6: Phi(1.96) ---
    ch.add(NumericCheck(
        label="Phi(1.96) ~ 0.97500",
        section="8.6",
        stated=0.97500,
        computed=float(scipy.stats.norm.cdf(1.96)),
        tolerance=1e-3,
    ))

    # --- Example 8.7: Binom(10,0.5) P(X=5) ---
    ch.add(NumericCheck(
        label="Binom(10,0.5) P(X=5) = 252/1024",
        section="8.7",
        stated=252.0 / 1024.0,
        computed=float(scipy.stats.binom.pmf(5, 10, 0.5)),
        tolerance=1e-10,
    ))

    # ===================================================================
    # Table verification — Distribution parameter table MGFs (Section 5)
    # ===================================================================

    # Bernoulli MGF: M(t) = (1-p) + p*e^t
    p_bern = 0.3
    t_val = 0.5
    ch.add(NumericCheck(
        label="Table: Bernoulli MGF M(0.5) = (1-p)+p*e^0.5",
        section="5",
        stated=(1 - p_bern) + p_bern * math.exp(t_val),
        computed=lambda: float(sum(
            scipy.stats.bernoulli.pmf(k, p_bern) * math.exp(t_val * k)
            for k in range(2)
        )),
        tolerance=1e-10,
        note="Distribution parameter table MGF column",
    ))

    # Binomial MGF: M(t) = ((1-p)+p*e^t)^n
    n_binom, p_binom = 10, 0.4
    ch.add(NumericCheck(
        label="Table: Binomial(10,0.4) MGF M(0.5)",
        section="5",
        stated=((1 - p_binom) + p_binom * math.exp(t_val)) ** n_binom,
        computed=lambda: float(sum(
            scipy.stats.binom.pmf(k, n_binom, p_binom) * math.exp(t_val * k)
            for k in range(n_binom + 1)
        )),
        tolerance=1e-8,
        note="Distribution parameter table MGF column",
    ))

    # Poisson MGF: M(t) = e^{lambda*(e^t - 1)}
    lam_pois = 3.0
    ch.add(NumericCheck(
        label="Table: Poisson(3) MGF M(0.5)",
        section="5",
        stated=math.exp(lam_pois * (math.exp(t_val) - 1)),
        computed=lambda: float(sum(
            scipy.stats.poisson.pmf(k, lam_pois) * math.exp(t_val * k)
            for k in range(100)
        )),
        tolerance=1e-8,
        note="Distribution parameter table MGF column",
    ))

    # Uniform MGF: M(t) = (e^{tb} - e^{ta}) / (t*(b-a))
    a_unif, b_unif = 1.0, 4.0
    ch.add(NumericCheck(
        label="Table: Uniform(1,4) MGF M(0.5)",
        section="5",
        stated=(math.exp(t_val * b_unif) - math.exp(t_val * a_unif)) / (t_val * (b_unif - a_unif)),
        computed=lambda: float(scipy.integrate.quad(
            lambda x: math.exp(t_val * x) / (b_unif - a_unif), a_unif, b_unif
        )[0]),
        tolerance=1e-10,
        note="Distribution parameter table MGF column",
    ))

    # Normal MGF: M(t) = e^{mu*t + sigma^2*t^2/2}
    mu_norm, sigma_norm = 2.0, 1.5
    ch.add(NumericCheck(
        label="Table: N(2,2.25) MGF M(0.5)",
        section="5",
        stated=math.exp(mu_norm * t_val + sigma_norm**2 * t_val**2 / 2),
        computed=lambda: float(scipy.integrate.quad(
            lambda x: math.exp(t_val * x) * scipy.stats.norm.pdf(x, mu_norm, sigma_norm),
            mu_norm - 10 * sigma_norm, mu_norm + 10 * sigma_norm
        )[0]),
        tolerance=1e-8,
        note="Distribution parameter table MGF column",
    ))

    # Chi-squared MGF: M(t) = (1-2t)^{-k/2}
    k_chi2 = 5
    t_chi = 0.1  # must be < 0.5 for convergence
    ch.add(NumericCheck(
        label="Table: Chi2(5) MGF M(0.1)",
        section="5",
        stated=(1 - 2 * t_chi) ** (-k_chi2 / 2),
        computed=lambda: float(scipy.integrate.quad(
            lambda x: math.exp(t_chi * x) * scipy.stats.chi2.pdf(x, k_chi2),
            0, 200
        )[0]),
        tolerance=1e-6,
        note="Distribution parameter table MGF column",
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    # --- Poisson PMF sums to 1 ---
    ch.add(StructuralCheck(
        label="Poisson(2.5) PMF sums to 1",
        section="5",
        predicate=lambda: _pmf_sums_to_one(scipy.stats.poisson(2.5), 100),
    ))

    # --- Binomial PMF sums to 1 ---
    ch.add(StructuralCheck(
        label="Binom(10,0.5) PMF sums to 1",
        section="5",
        predicate=lambda: _binom_sums_to_one(),
    ))

    # --- Normal PDF integrates to 1 ---
    ch.add(StructuralCheck(
        label="N(0,1) PDF integrates to 1",
        section="5",
        predicate=lambda: _normal_integrates_to_one(),
    ))

    # --- t(nu) -> N(0,1) convergence ---
    ch.add(StructuralCheck(
        label="t(1000) quantile within 0.2% of N(0,1)",
        section="6",
        predicate=lambda: _t_converges_to_normal(),
    ))

    # --- Poisson limit of Binomial ---
    ch.add(StructuralCheck(
        label="Binom(1000, 2.5/1000) ~ Poisson(2.5) at k=3",
        section="6",
        predicate=lambda: _poisson_limit(),
    ))

    # ===================================================================
    # Exercise checks (Section 11)
    # ===================================================================

    # --- Exercise 11.1: Binom(20, 0.3) mean, variance, and P(X=6) ---
    n_ex1, p_ex1 = 20, 0.3
    ch.add(NumericCheck(
        label="Ex 11.1: Binom(20,0.3) mean = 6",
        section="11",
        stated=6.0,
        computed=lambda: float(scipy.stats.binom.mean(n_ex1, p_ex1)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.1: Binom(20,0.3) var = 4.2",
        section="11",
        stated=4.2,
        computed=lambda: float(scipy.stats.binom.var(n_ex1, p_ex1)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 11.1: Binom(20,0.3) P(X=6) ~ 0.1916",
        section="11",
        stated=0.1916,
        computed=lambda: float(scipy.stats.binom.pmf(6, n_ex1, p_ex1)),
        tolerance=1e-3,
    ))

    # Log-space computation: log(P(X=6))
    ch.add(NumericCheck(
        label="Ex 11.1: Binom(20,0.3) logP(X=6) ~ -1.653",
        section="11",
        stated=math.log(float(scipy.stats.binom.pmf(6, n_ex1, p_ex1))),
        computed=lambda: float(scipy.stats.binom.logpmf(6, n_ex1, p_ex1)),
        tolerance=1e-10,
    ))

    # --- Exercise 11.2: N(50, 100) P(30 < X < 70) via erf ---
    mu_ex2, sigma_ex2 = 50, 10  # N(50, 100) => sigma = 10
    ch.add(NumericCheck(
        label="Ex 11.2: N(50,100) P(30<X<70) via erf",
        section="11",
        stated=float(scipy.stats.norm.cdf(70, mu_ex2, sigma_ex2) - scipy.stats.norm.cdf(30, mu_ex2, sigma_ex2)),
        computed=lambda: float(
            0.5 * (scipy.special.erf((70 - mu_ex2) / (sigma_ex2 * math.sqrt(2)))
                    - scipy.special.erf((30 - mu_ex2) / (sigma_ex2 * math.sqrt(2))))
        ),
        tolerance=1e-10,
        note="erf form matches CDF form",
    ))

    # P(30 < X < 70) = P(|Z| < 2) ~ 0.9545
    ch.add(NumericCheck(
        label="Ex 11.2: N(50,100) P(30<X<70) ~ 0.9545",
        section="11",
        stated=0.9545,
        computed=lambda: float(scipy.stats.norm.cdf(70, mu_ex2, sigma_ex2) - scipy.stats.norm.cdf(30, mu_ex2, sigma_ex2)),
        tolerance=1e-3,
    ))

    # --- Exercise 11.3: Poisson PMF sums to 1 via Taylor series ---
    def _ex3_poisson_sum():
        lam = 5.0
        total = sum(float(scipy.stats.poisson.pmf(k, lam)) for k in range(200))
        ok = abs(total - 1.0) < 1e-14
        return ok, f"Sum = {total}, expected 1.0"

    ch.add(StructuralCheck(
        label="Ex 11.3: Poisson(5) PMF sums to 1 (Taylor series of e^lambda)",
        section="11",
        predicate=_ex3_poisson_sum,
    ))

    # Verify the algebraic identity: sum e^{-lam}*lam^k/k! = e^{-lam}*e^{lam} = 1
    ch.add(NumericCheck(
        label="Ex 11.3: Partial sum e^{-3}*sum(3^k/k!, k=0..50) ~ 1.0",
        section="11",
        stated=1.0,
        computed=lambda: math.exp(-3) * sum(3.0**k / math.factorial(k) for k in range(51)),
        tolerance=1e-14,
    ))

    # --- Exercise 11.4: Poisson sum property ---
    # X ~ Poisson(lam1), Y ~ Poisson(lam2) indep => X+Y ~ Poisson(lam1+lam2)
    def _ex4_poisson_sum_property():
        lam1, lam2 = 3.0, 4.0
        # P(X+Y = 5) via convolution
        p_conv = sum(
            float(scipy.stats.poisson.pmf(j, lam1)) * float(scipy.stats.poisson.pmf(5 - j, lam2))
            for j in range(6)
        )
        p_direct = float(scipy.stats.poisson.pmf(5, lam1 + lam2))
        ok = abs(p_conv - p_direct) < 1e-12
        return ok, f"P(X+Y=5) conv = {p_conv:.10f}, direct = {p_direct:.10f}"

    ch.add(StructuralCheck(
        label="Ex 11.4: Poisson(3)+Poisson(4) = Poisson(7) via convolution at k=5",
        section="11",
        predicate=_ex4_poisson_sum_property,
    ))

    # Verify MGF product: M_{X+Y}(t) = M_X(t)*M_Y(t) at t=0.5
    ch.add(NumericCheck(
        label="Ex 11.4: Poisson MGF product at t=0.5",
        section="11",
        stated=0.0,
        computed=lambda: (
            math.exp(3 * (math.exp(0.5) - 1)) * math.exp(4 * (math.exp(0.5) - 1))
            - math.exp(7 * (math.exp(0.5) - 1))
        ),
        tolerance=1e-10,
        note="MGF Poisson(lam) = e^{lam*(e^t - 1)}; product identity residual",
    ))

    # --- Exercise 11.5: Sum of 25 standard normals squared ~ Chi2(25) ---
    ch.add(NumericCheck(
        label="Ex 11.5: P(Chi2(25) > 37.65) ~ 0.05",
        section="11",
        stated=0.05,
        computed=lambda: float(1 - scipy.stats.chi2.cdf(37.65, 25)),
        tolerance=5e-2,
        note="chi-squared critical value at 5% with 25 df",
    ))

    ch.add(NumericCheck(
        label="Ex 11.5: Chi2(25) 95th percentile ~ 37.65",
        section="11",
        stated=37.65,
        computed=lambda: float(scipy.stats.chi2.ppf(0.95, 25)),
        tolerance=1e-2,
    ))

    # --- Exercise 11.6: t(nu) variance = nu/(nu-2) ---
    def _ex6_t_variance():
        for nu in [3, 5, 10, 30, 100]:
            stated_var = float(nu) / (nu - 2)
            computed_var = float(scipy.stats.t.var(nu))
            rel_err = abs(computed_var - stated_var) / stated_var
            if rel_err > 1e-10:
                return False, f"t({nu}) var: expected {stated_var:.6f}, got {computed_var:.6f}"
        return True, ""

    ch.add(StructuralCheck(
        label="Ex 11.6: t(nu) variance = nu/(nu-2) for nu=3,5,10,30,100",
        section="11",
        predicate=_ex6_t_variance,
    ))

    # Verify via T = Z/sqrt(V/nu): Var(T) = E[Z^2]*E[nu/V] = 1 * nu/(nu-2)
    ch.add(NumericCheck(
        label="Ex 11.6: t(5) variance = 5/3 ~ 1.6667",
        section="11",
        stated=5.0 / 3.0,
        computed=lambda: float(scipy.stats.t.var(5)),
        tolerance=1e-10,
    ))

    # --- Exercise 11.7: de Moivre-Laplace theorem ---
    # (X - np)/sqrt(np(1-p)) -> N(0,1) for large n
    def _ex7_de_moivre_laplace():
        # Binom(1000, 0.4): P(380 < X < 420) should be close to P(-1.29 < Z < 1.29)
        n, p = 1000, 0.4
        mu = n * p
        sigma = math.sqrt(n * p * (1 - p))
        # Normal approximation
        z_lo = (380 - mu) / sigma
        z_hi = (420 - mu) / sigma
        p_normal = float(scipy.stats.norm.cdf(z_hi) - scipy.stats.norm.cdf(z_lo))
        # Exact binomial
        p_binom = float(sum(scipy.stats.binom.pmf(k, n, p) for k in range(381, 420)))
        rel_err = abs(p_normal - p_binom) / p_binom
        ok = rel_err < 0.02  # within 2% for n=1000
        return ok, f"Normal approx = {p_normal:.6f}, Binom exact = {p_binom:.6f}, rel_err = {rel_err:.4f}"

    ch.add(StructuralCheck(
        label="Ex 11.7: de Moivre-Laplace: Binom(1000,0.4) ~ Normal approximation within 2%",
        section="11",
        predicate=_ex7_de_moivre_laplace,
    ))

    # --- Exercise 11.8: F(d1,d2)^{-1} ~ F(d2,d1) ---
    def _ex8_f_reciprocal():
        d1, d2 = 5, 10
        # If W ~ F(d1,d2), then P(W > x) = P(1/W < 1/x) = P(F(d2,d1) < 1/x)
        # Equivalently: F_{d1,d2}(x) = 1 - F_{d2,d1}(1/x) for the CDF
        # More precisely: P(1/W <= y) = 1 - P(W <= 1/y) for y > 0
        # So CDF of 1/W at y is: 1 - F_{d1,d2}(1/y) = F_{d2,d1}(y)
        test_points = [0.5, 1.0, 2.0, 3.0, 5.0]
        for y in test_points:
            cdf_reciprocal = 1.0 - float(scipy.stats.f.cdf(1.0 / y, d1, d2))
            cdf_f_d2d1 = float(scipy.stats.f.cdf(y, d2, d1))
            if abs(cdf_reciprocal - cdf_f_d2d1) > 1e-10:
                return False, f"At y={y}: CDF(1/F({d1},{d2}))={cdf_reciprocal:.10f} != CDF(F({d2},{d1}))={cdf_f_d2d1:.10f}"
        return True, ""

    ch.add(StructuralCheck(
        label="Ex 11.8: F(5,10)^{-1} ~ F(10,5) reciprocal property",
        section="11",
        predicate=_ex8_f_reciprocal,
    ))

    # Cross-check with moments: E[1/W] for W~F(d1,d2) = d2/(d2+2) * d1/(d1-2) when d1 > 2
    # which should equal E[F(d2,d1)] = d2/(d2-2) ... no, E[F(d2,d1)] = d2/(d2-2) only if d2>2
    # Instead verify quantile relationship: Q_p(F(d1,d2)) = 1/Q_{1-p}(F(d2,d1))
    ch.add(NumericCheck(
        label="Ex 11.8: F quantile reciprocal: Q_{0.95}(F(5,10)) = 1/Q_{0.05}(F(10,5))",
        section="11",
        stated=float(scipy.stats.f.ppf(0.95, 5, 10)),
        computed=lambda: 1.0 / float(scipy.stats.f.ppf(0.05, 10, 5)),
        tolerance=1e-10,
    ))

    # ==================================================================
    # Remark 3.11: 68-95-99.7 rule
    # ==================================================================

    ch.add(NumericCheck(
        label="Remark 3.11: P(|X-mu| < sigma) ~ 0.6827",
        section="3",
        stated=0.6827,
        computed=lambda: float(2 * scipy.stats.norm.cdf(1) - 1),
        tolerance=1e-3,
        note="Remark 3.11: 68-95-99.7 rule",
    ))

    ch.add(NumericCheck(
        label="Remark 3.11: P(|X-mu| < 2*sigma) ~ 0.9545",
        section="3",
        stated=0.9545,
        computed=lambda: float(2 * scipy.stats.norm.cdf(2) - 1),
        tolerance=1e-3,
        note="Remark 3.11: 68-95-99.7 rule",
    ))

    ch.add(NumericCheck(
        label="Remark 3.11: P(|X-mu| < 3*sigma) ~ 0.9973",
        section="3",
        stated=0.9973,
        computed=lambda: float(2 * scipy.stats.norm.cdf(3) - 1),
        tolerance=1e-3,
        note="Remark 3.11: 68-95-99.7 rule",
    ))

    # ==================================================================
    # Remark 3.14: Chi-squared = Gamma(k/2, 2)
    # ==================================================================

    def _remark_3_14_chisq_gamma():
        for k in [1, 2, 5, 10, 30]:
            x_vals = [0.5, 1.0, 2.0, 5.0]
            for x in x_vals:
                chisq_cdf = float(scipy.stats.chi2.cdf(x, k))
                gamma_cdf = float(scipy.stats.gamma.cdf(x, a=k / 2.0, scale=2.0))
                if abs(chisq_cdf - gamma_cdf) > 1e-12:
                    return (False, f"k={k}, x={x}: chi2={chisq_cdf}, gamma={gamma_cdf}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.14: chi2(k) CDF = Gamma(k/2, 2) CDF",
        section="3",
        predicate=_remark_3_14_chisq_gamma,
        note="Remark 3.14: chi-squared as Gamma",
    ))

    # chi-squared k=2 is Exponential(rate=1/2)
    ch.add(NumericCheck(
        label="Remark 3.14: chi2(2) CDF at x=3 = Exp(scale=2) CDF",
        section="3",
        stated=float(scipy.stats.chi2.cdf(3, 2)),
        computed=lambda: float(scipy.stats.expon.cdf(3, scale=2)),
        tolerance=1e-12,
        note="Remark 3.14: chi2(2) = Exp(1/2)",
    ))

    # ==================================================================
    # Remark 3.18: T^2 ~ F(1, nu)
    # ==================================================================

    def _remark_3_18_t_squared_is_f():
        for nu in [5, 10, 30, 100]:
            for t_val in [0.5, 1.0, 1.5, 2.0, 3.0]:
                # P(T^2 <= t^2) = P(-t <= T <= t) = 2*F_t(t) - 1
                p_t2 = float(2 * scipy.stats.t.cdf(t_val, nu) - 1)
                p_f = float(scipy.stats.f.cdf(t_val ** 2, 1, nu))
                if abs(p_t2 - p_f) > 1e-10:
                    return (False, f"nu={nu}, t={t_val}: P(T^2<={t_val**2})={p_t2}, F(1,{nu})={p_f}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.18: T^2 ~ F(1, nu) CDF equivalence",
        section="3",
        predicate=_remark_3_18_t_squared_is_f,
        note="Remark 3.18: relationship between t and F",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Algorithm 5.1: Normal CDF via erf ---
    def _algo_normal_cdf():
        """Implement Algorithm 5.1 and verify against scipy."""
        def normal_cdf(x, mu=0, sigma=1):
            z = (x - mu) / sigma
            return 0.5 * (1 + math.erf(z / math.sqrt(2)))

        test_cases = [
            (0, 0, 1, 0.5),
            (1.96, 0, 1, 0.975),
            (-1.96, 0, 1, 0.025),
            (120, 100, 15, None),  # from worked example
        ]
        for x, mu, sigma, expected in test_cases:
            val = normal_cdf(x, mu, sigma)
            ref = float(scipy.stats.norm.cdf(x, mu, sigma))
            if abs(val - ref) > 1e-10:
                return (False, f"Normal CDF({x}, {mu}, {sigma}) = {val}, scipy = {ref}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.1: Normal CDF via erf matches scipy.stats.norm.cdf",
        section="6",
        predicate=_algo_normal_cdf,
        note="Algorithm 5.1 verified",
    ))

    # --- Algorithm 5.5: Binomial PMF in log-space ---
    def _algo_binomial_logspace():
        """Implement Algorithm 5.5 and verify against scipy."""
        def binom_pmf_log(n, k, p):
            log_pmf = (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                       + k * math.log(p) + (n - k) * math.log(1 - p))
            return math.exp(log_pmf)

        # Test on worked example: Binom(10, 0.5), P(X=7) = C(10,7)/1024 = 120/1024
        val = binom_pmf_log(10, 7, 0.5)
        expected = 120.0 / 1024
        if abs(val - expected) > 1e-10:
            return (False, f"Binom(10,7,0.5) = {val}, expected {expected}")

        # Test large n (where factorial overflow would occur)
        val_large = binom_pmf_log(1000, 500, 0.5)
        ref_large = float(scipy.stats.binom.pmf(500, 1000, 0.5))
        rel_err = abs(val_large - ref_large) / ref_large
        if rel_err > 1e-8:
            return (False, f"Binom(1000,500,0.5) rel_err = {rel_err:.2e}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.5: Binomial PMF log-space handles n=1000 without overflow",
        section="6",
        predicate=_algo_binomial_logspace,
        note="Algorithm 5.5 verified",
    ))

    # --- Algorithm 5.6: Poisson PMF via recurrence ---
    def _algo_poisson_recurrence():
        """Implement Algorithm 5.6 and verify against scipy."""
        def poisson_pmf(lam, k):
            p = math.exp(-lam)
            for j in range(1, k + 1):
                p = p * lam / j
            return p

        # P(X=3) for Poisson(2.5) from worked example
        val = poisson_pmf(2.5, 3)
        ref = float(scipy.stats.poisson.pmf(3, 2.5))
        if abs(val - ref) > 1e-10:
            return (False, f"Poisson(2.5, 3) = {val}, scipy = {ref}")

        # Test recurrence: P(0), P(1), P(2) also
        for k in range(6):
            val = poisson_pmf(2.5, k)
            ref = float(scipy.stats.poisson.pmf(k, 2.5))
            if abs(val - ref) > 1e-10:
                return (False, f"Poisson(2.5, {k}) = {val}, scipy = {ref}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.6: Poisson PMF recurrence matches scipy for k=0..5",
        section="6",
        predicate=_algo_poisson_recurrence,
        note="Algorithm 5.6 verified",
    ))

    # --- Algorithm 5.2: Normal quantile / inverse CDF ---
    def _algo_normal_quantile():
        """Verify normal inverse CDF matches scipy."""
        import scipy.stats
        test_probs = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        for p in test_probs:
            z = float(scipy.stats.norm.ppf(p))
            # Round-trip: Phi(z) should equal p
            p_check = float(scipy.stats.norm.cdf(z))
            if abs(p_check - p) > 1e-12:
                return (False, f"Round-trip failed: ppf({p})={z}, cdf({z})={p_check}")
        # Check specific known values: Phi^{-1}(0.5) = 0
        z_half = float(scipy.stats.norm.ppf(0.5))
        if abs(z_half) > 1e-14:
            return (False, f"ppf(0.5) = {z_half}, expected 0")
        # Phi^{-1}(0.975) ~ 1.96
        z_975 = float(scipy.stats.norm.ppf(0.975))
        if abs(z_975 - 1.959964) > 1e-4:
            return (False, f"ppf(0.975) = {z_975}, expected ~1.96")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.2: Normal quantile (inverse CDF) round-trips correctly",
        section="6",
        predicate=_algo_normal_quantile,
        note="Algorithm 5.2 verified",
    ))

    # --- Algorithm 5.3: Chi-squared CDF via regularized incomplete gamma ---
    def _algo_chi_squared_cdf():
        """Verify chi-squared CDF via incomplete gamma matches scipy."""
        import scipy.stats
        import scipy.special
        test_cases = [(3.84, 1), (5.99, 2), (7.81, 3), (9.49, 4), (11.07, 5)]
        for x, k in test_cases:
            # Direct: regularized incomplete gamma P(k/2, x/2)
            a = k / 2.0
            z = x / 2.0
            cdf_gamma = float(scipy.special.gammainc(a, z))
            cdf_scipy = float(scipy.stats.chi2.cdf(x, k))
            if abs(cdf_gamma - cdf_scipy) > 1e-10:
                return (False, f"chi2({x},{k}): gammainc={cdf_gamma}, scipy={cdf_scipy}")
        # Verify critical value: chi2.cdf(3.841, 1) ~ 0.95
        p = float(scipy.stats.chi2.cdf(3.841, 1))
        if abs(p - 0.95) > 0.001:
            return (False, f"chi2.cdf(3.841, 1) = {p}, expected ~0.95")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.3: Chi-squared CDF via regularized incomplete gamma",
        section="6",
        predicate=_algo_chi_squared_cdf,
        note="Algorithm 5.3 verified",
    ))

    # --- Algorithm 5.4: Student's t CDF via regularized incomplete beta ---
    def _algo_student_t_cdf():
        """Verify Student's t CDF via incomplete beta matches scipy."""
        import scipy.stats
        import scipy.special
        test_cases = [(1.96, 30), (2.576, 10), (0.0, 5), (-2.0, 20)]
        for t_val, nu in test_cases:
            x = nu / (nu + t_val**2)
            Ix = float(scipy.special.betainc(nu / 2.0, 0.5, x))
            if t_val >= 0:
                cdf_beta = 1.0 - 0.5 * Ix
            else:
                cdf_beta = 0.5 * Ix
            cdf_scipy = float(scipy.stats.t.cdf(t_val, nu))
            if abs(cdf_beta - cdf_scipy) > 1e-8:
                return (False, f"t({t_val},{nu}): beta={cdf_beta}, scipy={cdf_scipy}")
        # Check symmetry: t.cdf(-x, nu) = 1 - t.cdf(x, nu)
        cdf_pos = float(scipy.stats.t.cdf(2.0, 10))
        cdf_neg = float(scipy.stats.t.cdf(-2.0, 10))
        if abs(cdf_pos + cdf_neg - 1.0) > 1e-12:
            return (False, f"Symmetry: cdf(2)+cdf(-2)={cdf_pos+cdf_neg}, expected 1")
        return (True, "")

    ch.add(StructuralCheck(
        label="Algorithm 5.4: Student's t CDF via regularized incomplete beta",
        section="6",
        predicate=_algo_student_t_cdf,
        note="Algorithm 5.4 verified",
    ))

    # --- Remark 3.12: CLT — sum of many iid approaches Normal ---
    def _remark_3_12_clt():
        """Verify CLT: sum of n iid uniform r.v.s approaches Normal as n grows."""
        rng = np.random.default_rng(312)
        n = 100
        N_samples = 50000
        # Sum of n Uniform(0,1): mean = n/2, var = n/12
        sums = np.sum(rng.uniform(0, 1, (N_samples, n)), axis=1)
        standardized = (sums - n/2) / np.sqrt(n/12)
        # KS test against standard normal
        from scipy.stats import kstest
        stat, pval = kstest(standardized, 'norm')
        if pval < 0.01:
            return (False, f"KS test rejected normality: stat={stat:.4f}, p={pval:.4f}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.12: CLT — sum of 100 Uniform(0,1) approaches Normal",
        section="3.12",
        predicate=_remark_3_12_clt,
        note="Remark 3.12: ubiquity of normal distribution via CLT",
    ))

    # --- Remark 3.21: Normal quantile via erf inverse ---
    ch.add(NumericCheck(
        label="Remark 3.21: Phi^{-1}(0.975) = sqrt(2)*erfinv(0.95) ~ 1.96",
        section="3.21",
        stated=float(scipy.stats.norm.ppf(0.975)),
        computed=lambda: float(np.sqrt(2) * scipy.special.erfinv(2*0.975 - 1)),
        tolerance=1e-10,
        note="Remark 3.21: quantile via erf inverse",
    ))

    # Newton-Raphson on F(x)-p=0 converges for t-distribution quantile
    def _remark_3_21_newton_quantile():
        """Verify Newton-Raphson finds t-distribution quantile."""
        from scipy.stats import t as t_dist
        nu = 10
        p = 0.975
        # Newton: x_{n+1} = x_n - (F(x_n) - p) / f(x_n)
        x = 2.0  # initial guess
        for _ in range(20):
            Fx = t_dist.cdf(x, nu)
            fx = t_dist.pdf(x, nu)
            x = x - (Fx - p) / fx
        exact = t_dist.ppf(p, nu)
        if abs(x - exact) > 1e-8:
            return (False, f"Newton quantile={x}, exact={exact}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.21: Newton-Raphson finds t(10) quantile to < 1e-8",
        section="3.21",
        predicate=_remark_3_21_newton_quantile,
        note="Remark 3.21: computing quantiles via Newton",
    ))

    return ch


# ---------------------------------------------------------------------------
# Symbolic helpers
# ---------------------------------------------------------------------------

def _binomial_mean():
    """E[X] = np for Binomial, verified symbolically for n=3."""
    import sympy as sp
    p = sp.Symbol('p', positive=True)
    # Binom(3,p): E[X] = sum k * C(3,k) p^k (1-p)^(3-k)
    ex = sum(k * sp.binomial(3, k) * p**k * (1-p)**(3-k) for k in range(4))
    return sp.expand(ex) - 3*p


def _binomial_var():
    """Var[X] = np(1-p) for Binomial, verified symbolically for n=3."""
    import sympy as sp
    p = sp.Symbol('p', positive=True)
    ex = sum(k * sp.binomial(3, k) * p**k * (1-p)**(3-k) for k in range(4))
    ex2 = sum(k**2 * sp.binomial(3, k) * p**k * (1-p)**(3-k) for k in range(4))
    var = sp.expand(ex2 - ex**2)
    return var - 3*p*(1-p)


def _poisson_mean():
    """E[X] = lambda for Poisson, verified for first 20 terms."""
    import sympy as sp
    lam = sp.Symbol('lam', positive=True)
    # Truncated sum: sum k * e^{-lam} lam^k / k! for k=0..19
    # For symbolic purposes, compute without e^{-lam} factor and verify ratio
    ex = sum(k * lam**k / sp.factorial(k) for k in range(20))
    # E[X] = lam * sum lam^{k-1}/(k-1)! for k=1..inf = lam * e^lam
    # So ex should equal lam * sum lam^k/k! for k=0..18
    expected = lam * sum(lam**k / sp.factorial(k) for k in range(19))
    return sp.simplify(ex - expected)


def _uniform_mean():
    """E[X] = (a+b)/2 for Uniform(a,b)."""
    import sympy as sp
    a, b = sp.symbols('a b', real=True)
    # E[X] = integral of x/(b-a) from a to b
    x = sp.Symbol('x')
    ex = sp.integrate(x / (b - a), (x, a, b))
    return sp.simplify(ex - (a + b) / 2)


def _uniform_var():
    """Var(X) = (b-a)^2/12 for Uniform(a,b)."""
    import sympy as sp
    a, b = sp.symbols('a b', real=True)
    x = sp.Symbol('x')
    mu = (a + b) / 2
    var = sp.integrate((x - mu)**2 / (b - a), (x, a, b))
    return sp.simplify(var - (b - a)**2 / 12)


def _normal_cdf_erf():
    """Phi(x) = (1 + erf(x/sqrt(2)))/2, verified numerically at x=1.96."""
    import sympy as sp
    max_err = 0.0
    for x_val in [0.5, 1.0, 1.5, 1.96, 2.5]:
        phi = float(scipy.stats.norm.cdf(x_val))
        erf_form = 0.5 * (1 + float(scipy.special.erf(x_val / math.sqrt(2))))
        max_err = max(max_err, abs(phi - erf_form))
    # Machine epsilon level differences are acceptable
    if max_err < 1e-14:
        return sp.Integer(0)
    return sp.Float(max_err)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------

def _pmf_sums_to_one(dist, n_terms):
    total = sum(float(dist.pmf(k)) for k in range(n_terms))
    ok = abs(total - 1.0) < 1e-10
    return (ok, f"PMF sum = {total}, expected 1.0")


def _binom_sums_to_one():
    total = sum(float(scipy.stats.binom.pmf(k, 10, 0.5)) for k in range(11))
    ok = abs(total - 1.0) < 1e-14
    return (ok, f"Binom(10,0.5) PMF sum = {total}")


def _normal_integrates_to_one():
    from scipy.integrate import quad
    result, err = quad(scipy.stats.norm.pdf, -10, 10)
    ok = abs(result - 1.0) < 1e-10
    return (ok, f"N(0,1) integral = {result}")


def _t_converges_to_normal():
    t_q = float(scipy.stats.t.ppf(0.975, 1000))
    n_q = float(scipy.stats.norm.ppf(0.975))
    rel_diff = abs(t_q - n_q) / n_q
    ok = rel_diff < 0.002  # within 0.2%
    return (ok, f"t(1000)={t_q:.4f} vs N(0,1)={n_q:.4f}, diff={rel_diff:.4%}")


def _poisson_limit():
    lam = 2.5
    n = 1000
    binom_val = float(scipy.stats.binom.pmf(3, n, lam / n))
    poisson_val = float(scipy.stats.poisson.pmf(3, lam))
    rel_diff = abs(binom_val - poisson_val) / poisson_val
    ok = rel_diff < 0.01  # within 1%
    return (ok, f"Binom={binom_val:.6f} vs Poisson={poisson_val:.6f}, diff={rel_diff:.4%}")
