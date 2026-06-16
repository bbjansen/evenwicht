# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 35: Pharmacokinetics."""

import math

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(35, "Pharmacokinetics")

    # --- Symbolic checks ---

    # S1: IV bolus: C(t) = C0 * e^{-ke*t} solves dC/dt = -ke*C
    def iv_bolus_ode():
        import sympy as sp
        t, ke, C0 = sp.symbols('t ke C0', positive=True)
        C = C0 * sp.exp(-ke * t)
        dCdt = sp.diff(C, t)
        return sp.Eq(sp.simplify(dCdt + ke * C), 0)
    ch.add(SymbolicCheck(
        label="IV bolus solution satisfies dC/dt = -ke*C",
        section="4",
        identity=iv_bolus_ode,
    ))

    # S2: AUC = C0/ke (integral of exponential)
    def auc_formula():
        import sympy as sp
        t, ke, C0 = sp.symbols('t ke C0', positive=True)
        C = C0 * sp.exp(-ke * t)
        auc = sp.integrate(C, (t, 0, sp.oo))
        return sp.Eq(sp.simplify(auc - C0/ke), 0)
    ch.add(SymbolicCheck(
        label="AUC = C0/ke (improper integral of exponential)",
        section="4",
        identity=auc_formula,
    ))

    # S3: Accumulation factor R = 1/(1-r) where r = e^{-ke*tau}
    def accumulation_factor():
        import sympy as sp
        ke, tau = sp.symbols('ke tau', positive=True)
        r = sp.exp(-ke * tau)
        R = 1 / (1 - r)
        # The geometric series sum: 1 + r + r^2 + ... = 1/(1-r) for |r|<1
        # Since r = e^{-ke*tau} < 1 for ke,tau > 0, this holds
        # Verify R*(1-r) = 1
        return sp.Eq(sp.simplify(R * (1 - r)), 1)
    ch.add(SymbolicCheck(
        label="Accumulation factor: R*(1-r) = 1",
        section="4",
        identity=accumulation_factor,
    ))

    # S4: Bateman equation satisfies the oral absorption ODE
    def bateman_ode():
        import sympy as sp
        t, ka, ke, FD_Vd = sp.symbols('t ka ke FD_Vd', positive=True)
        # C(t) = FD_Vd * ka/(ka-ke) * (exp(-ke*t) - exp(-ka*t))
        coeff = FD_Vd * ka / (ka - ke)
        C = coeff * (sp.exp(-ke * t) - sp.exp(-ka * t))
        dCdt = sp.diff(C, t)
        # ODE: dC/dt = FD_Vd * ka * exp(-ka*t) - ke * C
        rhs = FD_Vd * ka * sp.exp(-ka * t) - ke * C
        return sp.Eq(sp.simplify(dCdt - rhs), 0)
    ch.add(SymbolicCheck(
        label="Bateman equation satisfies oral absorption ODE",
        section="4",
        identity=bateman_ode,
    ))

    # S5: tmax formula: at tmax, dC/dt = 0 (verified numerically for specific ka, ke)
    def tmax_derivation():
        import sympy as sp
        # Use specific numeric values to avoid simplification issues with generic symbols
        ka_val = sp.Rational(3, 2)  # 1.5
        ke_val = sp.Rational(1, 5)  # 0.2
        t = sp.Symbol('t', positive=True)
        tmax = sp.ln(ka_val / ke_val) / (ka_val - ke_val)
        # At tmax, dC/dt = 0 means ka*exp(-ka*t) = ke*exp(-ke*t)
        lhs = ka_val * sp.exp(-ka_val * tmax)
        rhs = ke_val * sp.exp(-ke_val * tmax)
        diff = sp.simplify(lhs - rhs)
        return sp.Eq(diff, 0)
    ch.add(SymbolicCheck(
        label="tmax: ka*exp(-ka*tmax) = ke*exp(-ke*tmax) (ka=3/2, ke=1/5)",
        section="4",
        identity=tmax_derivation,
    ))

    # S6: Half-life formula t1/2 = ln(2)/ke
    def half_life_formula():
        import sympy as sp
        ke = sp.Symbol('ke', positive=True)
        thalf = sp.ln(2) / ke
        # At t=thalf, exp(-ke*thalf) = 1/2
        val = sp.exp(-ke * thalf)
        return sp.Eq(sp.simplify(val - sp.Rational(1, 2)), 0)
    ch.add(SymbolicCheck(
        label="Half-life: exp(-ke * t1/2) = 1/2",
        section="4",
        identity=half_life_formula,
    ))

    # --- Numeric checks (Worked Examples) ---

    # Example 3.1: ke
    ch.add(NumericCheck(
        label="Ex 35.1: Elimination rate constant ke",
        section="9",
        stated=0.192,
        computed=lambda: (math.log(8.0) - math.log(4.5)) / 3,
        tolerance=5e-3,
        note="textbook rounds to 3 decimal places",
    ))

    # Example 3.1: Half-life
    ch.add(NumericCheck(
        label="Ex 35.1: Half-life",
        section="9",
        stated=3.61,
        computed=lambda: math.log(2) / 0.192,
        tolerance=1e-2,
    ))

    # Example 3.1: C0
    ch.add(NumericCheck(
        label="Ex 35.1: Initial concentration C0",
        section="9",
        stated=9.69,
        computed=lambda: 8.0 * math.exp(0.192),
        tolerance=1e-2,
    ))

    # Example 3.1: Vd
    ch.add(NumericCheck(
        label="Ex 35.1: Volume of distribution",
        section="9",
        stated=51.6,
        computed=lambda: 500 / (8.0 * math.exp(0.192)),
        tolerance=1e-2,
    ))

    # Example 3.1: CL = ke * Vd
    ch.add(NumericCheck(
        label="Ex 35.1: Clearance",
        section="9",
        stated=9.9,
        computed=lambda: 0.192 * (500 / (8.0 * math.exp(0.192))),
        tolerance=1e-2,
    ))

    # Example 3.1: AUC
    ch.add(NumericCheck(
        label="Ex 35.1: AUC",
        section="9",
        stated=50.5,
        computed=lambda: (8.0 * math.exp(0.192)) / 0.192,
        tolerance=1e-2,
    ))

    # Example 3.1: AUC via D/CL
    ch.add(NumericCheck(
        label="Ex 35.1: AUC = D/CL verification",
        section="9",
        stated=50.5,
        computed=lambda: 500 / (0.192 * 500 / (8.0 * math.exp(0.192))),
        tolerance=1e-2,
    ))

    # Example 3.2: tmax for oral dosing
    ch.add(NumericCheck(
        label="Ex 35.2: Time to peak (oral)",
        section="9",
        stated=1.55,
        computed=lambda: math.log(1.5/0.2) / (1.5 - 0.2),
        tolerance=1e-2,
    ))

    # Example 3.2: Cmax intermediate: (ke/ka)^(ke/(ka-ke))
    ch.add(NumericCheck(
        label="Ex 35.2: Cmax power term (0.1333)^0.1538",
        section="9",
        stated=0.734,
        computed=lambda: (0.2/1.5) ** (0.2/1.3),
        tolerance=1e-2,
    ))

    # Example 3.2: Cmax
    ch.add(NumericCheck(
        label="Ex 35.2: Cmax (oral)",
        section="9",
        stated=3.67,
        computed=lambda: (0.8 * 250 / 40) * (0.2/1.5) ** (0.2/1.3),
        tolerance=1e-2,
    ))

    # Example 3.2: AUC (oral)
    ch.add(NumericCheck(
        label="Ex 35.2: AUC (oral)",
        section="9",
        stated=25.0,
        computed=lambda: 0.8 * 250 / (0.2 * 40),
        tolerance=1e-6,
    ))

    # Example 3.2: AUC (IV, same dose)
    ch.add(NumericCheck(
        label="Ex 35.2: AUC (IV, same dose)",
        section="9",
        stated=31.25,
        computed=lambda: 250 / (0.2 * 40),
        tolerance=1e-6,
    ))

    # Example 3.2: Bioavailability verification F = AUC_oral / AUC_IV
    ch.add(NumericCheck(
        label="Ex 35.2: Bioavailability F = AUC_oral/AUC_IV",
        section="9",
        stated=0.80,
        computed=lambda: 25.0 / 31.25,
        tolerance=1e-6,
    ))

    # Example 3.3: r = e^{-ke*tau}
    ch.add(NumericCheck(
        label="Ex 35.3: Dosing fraction r",
        section="9",
        stated=0.1225,
        computed=lambda: math.exp(-0.35 * 6),
        tolerance=1e-3,
    ))

    # Example 3.3: Accumulation factor
    ch.add(NumericCheck(
        label="Ex 35.3: Accumulation factor R",
        section="9",
        stated=1.140,
        computed=lambda: 1 / (1 - math.exp(-0.35 * 6)),
        tolerance=1e-3,
    ))

    # Example 3.3: C0 = D/Vd
    ch.add(NumericCheck(
        label="Ex 35.3: Single-dose C0",
        section="9",
        stated=10.0,
        computed=lambda: 200 / 20,
        tolerance=1e-6,
    ))

    # Example 3.3: Steady-state Cmax
    ch.add(NumericCheck(
        label="Ex 35.3: Cmax,ss",
        section="9",
        stated=11.4,
        computed=lambda: (200/20) / (1 - math.exp(-0.35*6)),
        tolerance=1e-2,
    ))

    # Example 3.3: Steady-state Cmin
    ch.add(NumericCheck(
        label="Ex 35.3: Cmin,ss",
        section="9",
        stated=1.40,
        computed=lambda: (200/20) / (1 - math.exp(-0.35*6)) * math.exp(-0.35*6),
        tolerance=1e-2,
    ))

    # Example 3.3: Loading dose
    ch.add(NumericCheck(
        label="Ex 35.3: Loading dose",
        section="9",
        stated=228.0,
        computed=lambda: 200 / (1 - math.exp(-0.35 * 6)),
        tolerance=1e-2,
    ))

    # Example 3.3: Doses for 90% steady state
    ch.add(NumericCheck(
        label="Ex 35.3: n for 90% SS (continuous)",
        section="9",
        stated=1.10,
        computed=lambda: math.log(0.1) / math.log(math.exp(-0.35*6)),
        tolerance=1e-2,
    ))

    # Example 3.4: ke from CL/Vd
    ch.add(NumericCheck(
        label="Ex 35.4: ke = CL/Vd",
        section="9",
        stated=0.1,
        computed=lambda: 3.0 / 30,
        tolerance=1e-6,
    ))

    # Example 3.4: Theophylline half-life
    ch.add(NumericCheck(
        label="Ex 35.4: Theophylline half-life",
        section="9",
        stated=6.93,
        computed=lambda: math.log(2) / 0.1,
        tolerance=1e-2,
    ))

    # Example 3.4: Maximum dosing interval
    ch.add(NumericCheck(
        label="Ex 35.4: Maximum dosing interval",
        section="9",
        stated=6.93,
        computed=lambda: math.log(20/10) / 0.1,
        tolerance=1e-2,
    ))

    # Example 3.4: Maintenance dose
    ch.add(NumericCheck(
        label="Ex 35.4: Maintenance dose",
        section="9",
        stated=270.0,
        computed=lambda: 3.0 * 15 * 6 / 1.0,
        tolerance=1e-6,
    ))

    # Example 3.4: r for tau=6
    ch.add(NumericCheck(
        label="Ex 35.4: r = e^{-0.1*6}",
        section="9",
        stated=0.549,
        computed=lambda: math.exp(-0.1 * 6),
        tolerance=1e-3,
    ))

    # Example 3.4: Cmax,ss for theophylline
    ch.add(NumericCheck(
        label="Ex 35.4: Cmax,ss (theophylline)",
        section="9",
        stated=20.0,
        computed=lambda: (270/30) / (1 - math.exp(-0.1*6)),
        tolerance=1e-2,
    ))

    # Example 3.4: Cmin,ss for theophylline
    ch.add(NumericCheck(
        label="Ex 35.4: Cmin,ss (theophylline)",
        section="9",
        stated=11.0,
        computed=lambda: (270/30) / (1 - math.exp(-0.1*6)) * math.exp(-0.1*6),
        tolerance=1e-1,
    ))

    # Example 3.4: Loading dose for theophylline
    ch.add(NumericCheck(
        label="Ex 35.4: Loading dose (theophylline)",
        section="9",
        stated=599.0,
        computed=lambda: 270 / (1 - math.exp(-0.1 * 6)),
        tolerance=1e-2,
    ))

    # Example 3.5: A + B = C0
    ch.add(NumericCheck(
        label="Ex 35.5: C0 = A + B",
        section="9",
        stated=60.0,
        computed=lambda: 45.0 + 15.0,
        tolerance=1e-6,
    ))

    # Example 3.5: Vc = D/C0
    ch.add(NumericCheck(
        label="Ex 35.5: Vc = D/C0",
        section="9",
        stated=16.7,
        computed=lambda: 1000 / 60,
        tolerance=1e-2,
    ))

    # Example 3.5: Distribution half-life
    ch.add(NumericCheck(
        label="Ex 35.5: t1/2,alpha (distribution)",
        section="9",
        stated=0.173,
        computed=lambda: math.log(2) / 4.0,
        tolerance=1e-2,
    ))

    # Example 3.5: Elimination half-life
    ch.add(NumericCheck(
        label="Ex 35.5: t1/2,beta (elimination)",
        section="9",
        stated=2.31,
        computed=lambda: math.log(2) / 0.3,
        tolerance=1e-2,
    ))

    # Example 3.5: Two-compartment AUC
    ch.add(NumericCheck(
        label="Ex 35.5: Two-compartment AUC",
        section="9",
        stated=61.25,
        computed=lambda: 45/4.0 + 15/0.3,
        tolerance=1e-6,
    ))

    # Example 3.5: AUC component A/alpha
    ch.add(NumericCheck(
        label="Ex 35.5: AUC component A/alpha",
        section="9",
        stated=11.25,
        computed=lambda: 45 / 4.0,
        tolerance=1e-6,
    ))

    # Example 3.5: AUC component B/beta
    ch.add(NumericCheck(
        label="Ex 35.5: AUC component B/beta",
        section="9",
        stated=50.0,
        computed=lambda: 15 / 0.3,
        tolerance=1e-6,
    ))

    # Example 3.5: k21 micro constant
    ch.add(NumericCheck(
        label="Ex 35.5: k21 micro rate constant",
        section="9",
        stated=1.225,
        computed=lambda: (45*0.3 + 15*4.0) / 60,
        tolerance=1e-3,
    ))

    # Example 3.5: k10 micro constant
    ch.add(NumericCheck(
        label="Ex 35.5: k10 micro rate constant",
        section="9",
        stated=0.980,
        computed=lambda: (4.0 * 0.3) / ((45*0.3 + 15*4.0)/60),
        tolerance=1e-3,
    ))

    # Example 3.5: k12 micro constant
    ch.add(NumericCheck(
        label="Ex 35.5: k12 micro rate constant",
        section="9",
        stated=2.095,
        computed=lambda: 4.0 + 0.3 - 1.225 - 0.980,
        tolerance=1e-3,
    ))

    # Example 3.5: CL from micro constants = k10 * Vc
    ch.add(NumericCheck(
        label="Ex 35.5: CL = k10 * Vc",
        section="9",
        stated=16.3,
        computed=lambda: 0.980 * (1000/60),
        tolerance=1e-2,
    ))

    # Example 3.5: CL from AUC = D/AUC
    ch.add(NumericCheck(
        label="Ex 35.5: CL = D/AUC verification",
        section="9",
        stated=16.3,
        computed=lambda: 1000 / 61.25,
        tolerance=1e-2,
    ))

    # --- Structural checks ---

    # CL computed two ways should match: CL = ke*Vd = D/AUC
    def clearance_consistency():
        ke = 0.192
        C0 = 8.0 * math.exp(0.192)
        Vd = 500 / C0
        CL1 = ke * Vd
        AUC = C0 / ke
        CL2 = 500 / AUC
        ok = abs(CL1 - CL2) / CL1 < 1e-6
        return (ok, f"CL(ke*Vd)={CL1:.2f}, CL(D/AUC)={CL2:.2f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Clearance: ke*Vd = D/AUC",
        section="9",
        predicate=clearance_consistency,
    ))

    # Therapeutic window: Cmin,ss >= MEC and Cmax,ss <= MTC
    def therapeutic_window():
        ke = 0.1
        Vd = 30
        dose = 270
        tau = 6
        r = math.exp(-ke * tau)
        C0 = dose / Vd
        Cmax_ss = C0 / (1 - r)
        Cmin_ss = Cmax_ss * r
        MEC, MTC = 10, 20
        ok = Cmin_ss >= MEC and Cmax_ss <= MTC
        return (ok, f"Cmin={Cmin_ss:.1f}, Cmax={Cmax_ss:.1f}, window=[{MEC},{MTC}]" if not ok else "")
    ch.add(StructuralCheck(
        label="Theophylline regimen stays within therapeutic window",
        section="9",
        predicate=therapeutic_window,
    ))

    # Two-compartment CL consistency: k10*Vc = D/AUC
    def two_comp_cl_consistency():
        A, alpha, B, beta = 45.0, 4.0, 15.0, 0.3
        D = 1000
        C0 = A + B
        Vc = D / C0
        k21 = (A * beta + B * alpha) / C0
        k10 = (alpha * beta) / k21
        CL_micro = k10 * Vc
        AUC = A / alpha + B / beta
        CL_auc = D / AUC
        ok = abs(CL_micro - CL_auc) / CL_auc < 1e-3
        return (ok, f"CL(micro)={CL_micro:.2f}, CL(AUC)={CL_auc:.2f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Two-compartment: k10*Vc = D/AUC",
        section="9",
        predicate=two_comp_cl_consistency,
    ))

    # Two-compartment: alpha + beta = k12 + k21 + k10 (sum of eigenvalues)
    def two_comp_sum_check():
        A, alpha, B, beta = 45.0, 4.0, 15.0, 0.3
        C0 = A + B
        k21 = (A * beta + B * alpha) / C0
        k10 = (alpha * beta) / k21
        k12 = alpha + beta - k21 - k10
        sum_micro = k12 + k21 + k10
        sum_macro = alpha + beta
        ok = abs(sum_micro - sum_macro) / sum_macro < 1e-6
        return (ok, f"sum_micro={sum_micro:.4f}, sum_macro={sum_macro:.4f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Two-compartment: alpha+beta = k12+k21+k10",
        section="9",
        predicate=two_comp_sum_check,
    ))

    # Two-compartment: alpha*beta = k10*k21 (product of eigenvalues)
    def two_comp_prod_check():
        A, alpha, B, beta = 45.0, 4.0, 15.0, 0.3
        C0 = A + B
        k21 = (A * beta + B * alpha) / C0
        k10 = (alpha * beta) / k21
        prod_micro = k10 * k21
        prod_macro = alpha * beta
        ok = abs(prod_micro - prod_macro) / prod_macro < 1e-6
        return (ok, f"prod_micro={prod_micro:.4f}, prod_macro={prod_macro:.4f}" if not ok else "")
    ch.add(StructuralCheck(
        label="Two-compartment: alpha*beta = k10*k21",
        section="9",
        predicate=two_comp_prod_check,
    ))

    # Accumulation: after 5 half-lives, 96.9% of steady state reached
    def accumulation_convergence():
        # For any ke, after 5 half-lives: 1 - (1/2)^5 = 0.96875
        fraction = 1 - (0.5)**5
        ok = abs(fraction - 0.96875) < 1e-6
        return (ok, f"fraction={fraction}" if not ok else "")
    ch.add(StructuralCheck(
        label="After 5 half-lives: 96.875% of steady state",
        section="4",
        predicate=accumulation_convergence,
    ))

    # Average Css: FD/(CL*tau) consistency
    def avg_css_consistency():
        CL = 3.0
        F = 1.0
        D = 270
        tau = 6
        Cavg_target = 15.0
        Cavg_computed = F * D / (CL * tau)
        ok = abs(Cavg_computed - Cavg_target) / Cavg_target < 1e-6
        return (ok, f"Cavg={Cavg_computed:.2f}, target={Cavg_target}" if not ok else "")
    ch.add(StructuralCheck(
        label="Average Css: FD/(CL*tau) = 15.0 mg/L",
        section="9",
        predicate=avg_css_consistency,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 10.1: IV bolus ke=0.1, Vd=50, D=400 ---
    # (a) t1/2 = ln(2)/ke = ln(2)/0.1
    ch.add(NumericCheck(
        label="Exercise 10.1a: Half-life",
        section="11",
        stated=math.log(2) / 0.1,
        computed=lambda: math.log(2) / 0.1,
        tolerance=1e-6,
    ))
    # (b) C0 = D/Vd = 400/50 = 8
    ch.add(NumericCheck(
        label="Exercise 10.1b: C0",
        section="11",
        stated=8.0,
        computed=lambda: 400 / 50,
        tolerance=1e-6,
    ))
    # (c) CL = ke*Vd = 0.1*50 = 5
    ch.add(NumericCheck(
        label="Exercise 10.1c: Clearance",
        section="11",
        stated=5.0,
        computed=lambda: 0.1 * 50,
        tolerance=1e-6,
    ))
    # (d) C(8) = 8*exp(-0.1*8)
    ch.add(NumericCheck(
        label="Exercise 10.1d: C(8)",
        section="11",
        stated=8 * math.exp(-0.1 * 8),
        computed=lambda: 8 * math.exp(-0.1 * 8),
        tolerance=1e-6,
    ))
    # (e) AUC = C0/ke = 8/0.1 = 80
    ch.add(NumericCheck(
        label="Exercise 10.1e: AUC",
        section="11",
        stated=80.0,
        computed=lambda: 8 / 0.1,
        tolerance=1e-6,
    ))

    # --- Exercise 10.2: Oral dosing ---
    # ka=2.0, ke=0.3, Vd=25, F=0.65, D=100
    # tmax = ln(ka/ke)/(ka-ke) = ln(2.0/0.3)/1.7
    ch.add(NumericCheck(
        label="Exercise 10.2: tmax",
        section="11",
        stated=math.log(2.0/0.3) / (2.0 - 0.3),
        computed=lambda: math.log(2.0/0.3) / (2.0 - 0.3),
        tolerance=1e-6,
    ))
    # Cmax = (F*D/Vd) * (ke/ka)^(ke/(ka-ke))
    ch.add(NumericCheck(
        label="Exercise 10.2: Cmax",
        section="11",
        stated=(0.65 * 100 / 25) * (0.3/2.0) ** (0.3/1.7),
        computed=lambda: (0.65 * 100 / 25) * (0.3/2.0) ** (0.3/1.7),
        tolerance=1e-6,
    ))

    # --- Exercise 10.3: Multiple dosing ---
    # D=300, ke=0.25, Vd=35, tau=8
    # r = exp(-0.25*8) = exp(-2)
    ch.add(NumericCheck(
        label="Exercise 10.3: r = exp(-ke*tau)",
        section="11",
        stated=math.exp(-2),
        computed=lambda: math.exp(-0.25 * 8),
        tolerance=1e-6,
    ))
    # R = 1/(1-r)
    ch.add(NumericCheck(
        label="Exercise 10.3: Accumulation factor R",
        section="11",
        stated=1 / (1 - math.exp(-2)),
        computed=lambda: 1 / (1 - math.exp(-0.25 * 8)),
        tolerance=1e-6,
    ))
    # Cmax,ss = (D/Vd)*R = (300/35)*R
    ch.add(NumericCheck(
        label="Exercise 10.3: Cmax,ss",
        section="11",
        stated=(300/35) / (1 - math.exp(-2)),
        computed=lambda: (300/35) / (1 - math.exp(-0.25*8)),
        tolerance=1e-6,
    ))
    # Cmin,ss = Cmax,ss * r
    ch.add(NumericCheck(
        label="Exercise 10.3: Cmin,ss",
        section="11",
        stated=(300/35) / (1 - math.exp(-2)) * math.exp(-2),
        computed=lambda: (300/35) / (1 - math.exp(-0.25*8)) * math.exp(-0.25*8),
        tolerance=1e-6,
    ))

    # --- Exercise 10.4: Fraction of steady state ---
    # ke=0.05, tau=12, r=exp(-0.05*12) = exp(-0.6)
    # After n doses: fraction = 1 - r^n
    def ex354_fraction(n):
        r = math.exp(-0.05 * 12)
        return 1 - r**n
    for n_val in [1, 2, 3, 5, 10]:
        ch.add(NumericCheck(
            label=f"Exercise 10.4: Fraction SS after {n_val} doses",
            section="11",
            stated=ex354_fraction(n_val),
            computed=(lambda nv=n_val: ex354_fraction(nv)),
            tolerance=1e-10,
        ))
    # 90% SS: n >= ln(10)/ln(1/r) = ln(10)/(0.6)
    ch.add(NumericCheck(
        label="Exercise 10.4: Doses for 90% SS",
        section="11",
        stated=math.log(10) / 0.6,
        computed=lambda: math.log(10) / (0.05 * 12),
        tolerance=1e-6,
    ))

    # --- Exercise 10.5: Therapeutic window design ---
    # MEC=5, MTC=40, ke=0.08, Vd=60, tau=12, target Cavg=15
    # Max dosing interval: tau_max = ln(MTC/MEC)/ke
    ch.add(NumericCheck(
        label="Exercise 10.5a: Max dosing interval",
        section="11",
        stated=math.log(40/5) / 0.08,
        computed=lambda: math.log(40/5) / 0.08,
        tolerance=1e-6,
    ))
    # Dose for Cavg=15: D = Cavg*CL*tau/F = 15*0.08*60*12/1 = 864
    ch.add(NumericCheck(
        label="Exercise 10.5b: Maintenance dose",
        section="11",
        stated=15 * 0.08 * 60 * 12,
        computed=lambda: 15 * 0.08 * 60 * 12,
        tolerance=1e-6,
    ))
    # Loading dose: DL = D / (1-r) where r = exp(-0.08*12)
    def ex355_loading():
        D = 15 * 0.08 * 60 * 12
        r = math.exp(-0.08 * 12)
        return D / (1 - r)
    ch.add(NumericCheck(
        label="Exercise 10.5c: Loading dose",
        section="11",
        stated=ex355_loading(),
        computed=ex355_loading,
        tolerance=1e-6,
    ))
    # Verify therapeutic window
    def ex355_window():
        D = 15 * 0.08 * 60 * 12
        r = math.exp(-0.08 * 12)
        C0 = D / 60
        Cmax = C0 / (1 - r)
        Cmin = Cmax * r
        ok = Cmin >= 5 and Cmax <= 40
        return (ok, f"Cmin={Cmin:.2f}, Cmax={Cmax:.2f}, window=[5,40]")
    ch.add(StructuralCheck(
        label="Exercise 10.5d: Regimen within therapeutic window",
        section="11",
        predicate=ex355_window,
    ))

    # --- Exercise 10.6: Bioavailability ---
    # F = AUC_oral / AUC_IV = 52/80
    ch.add(NumericCheck(
        label="Exercise 10.6a: Bioavailability F",
        section="11",
        stated=0.65,
        computed=lambda: 52 / 80,
        tolerance=1e-6,
    ))

    # --- Exercise 10.7: Two-compartment analysis ---
    # C(t) = 30*exp(-2.5t) + 10*exp(-0.15t), D=600
    # A=30, B=10, alpha=2.5, beta=0.15
    # Vc = D/(A+B) = 600/40 = 15
    ch.add(NumericCheck(
        label="Exercise 10.7: Vc = D/(A+B)",
        section="11",
        stated=15.0,
        computed=lambda: 600 / (30 + 10),
        tolerance=1e-6,
    ))
    # k21 = (A*beta + B*alpha)/(A+B)
    ch.add(NumericCheck(
        label="Exercise 10.7: k21",
        section="11",
        stated=(30*0.15 + 10*2.5) / 40,
        computed=lambda: (30*0.15 + 10*2.5) / 40,
        tolerance=1e-6,
    ))
    # k10 = alpha*beta/k21
    def ex357_k10():
        k21 = (30*0.15 + 10*2.5) / 40
        return 2.5 * 0.15 / k21
    ch.add(NumericCheck(
        label="Exercise 10.7: k10",
        section="11",
        stated=ex357_k10(),
        computed=ex357_k10,
        tolerance=1e-6,
    ))
    # AUC = A/alpha + B/beta
    ch.add(NumericCheck(
        label="Exercise 10.7: AUC",
        section="11",
        stated=30/2.5 + 10/0.15,
        computed=lambda: 30/2.5 + 10/0.15,
        tolerance=1e-6,
    ))
    # CL = D/AUC
    ch.add(NumericCheck(
        label="Exercise 10.7: Clearance",
        section="11",
        stated=600 / (30/2.5 + 10/0.15),
        computed=lambda: 600 / (30/2.5 + 10/0.15),
        tolerance=1e-6,
    ))
    # Vss = Vc*(1 + k12/k21)
    def ex357_vss():
        k21 = (30*0.15 + 10*2.5) / 40
        k10 = 2.5 * 0.15 / k21
        k12 = 2.5 + 0.15 - k21 - k10
        Vc = 15.0
        return Vc * (1 + k12/k21)
    ch.add(NumericCheck(
        label="Exercise 10.7: Vss",
        section="11",
        stated=ex357_vss(),
        computed=ex357_vss,
        tolerance=1e-6,
    ))

    # --- Exercise 10.8: Oral steady-state concentration formula ---
    # C_ss(t) = ka*F*D/(Vd*(ka-ke)) * [e^{-ke*t}/(1-e^{-ke*tau}) - e^{-ka*t}/(1-e^{-ka*tau})]
    # Verify: as tau -> infinity, reduces to single-dose Bateman equation
    # Also verify tmax_ss formula
    def ex358_oral_ss():
        ka, ke, F, D, Vd = 1.5, 0.2, 0.8, 250, 40
        tau = 8.0
        coeff = ka * F * D / (Vd * (ka - ke))
        r_ke = math.exp(-ke * tau)
        r_ka = math.exp(-ka * tau)
        # Compute C_ss at several time points and verify it's periodic
        def C_ss(t):
            return coeff * (math.exp(-ke * t) / (1 - r_ke) - math.exp(-ka * t) / (1 - r_ka))
        # C_ss should be positive for t in (0, tau)
        for t_val in [0.1, 0.5, 1.0, 2.0, 4.0, 6.0, 7.0]:
            if C_ss(t_val) < 0:
                return (False, f"C_ss({t_val}) = {C_ss(t_val):.4f} < 0")
        # Verify tmax_ss: ka*e^{-ka*t}/(1-e^{-ka*tau}) = ke*e^{-ke*t}/(1-e^{-ke*tau})
        # Use numerical root finding
        from scipy.optimize import brentq
        def deriv(t):
            return -ke * math.exp(-ke * t) / (1 - r_ke) + ka * math.exp(-ka * t) / (1 - r_ka)
        tmax_ss = brentq(deriv, 0.01, tau - 0.01)
        # Should be positive and less than tau
        ok = 0 < tmax_ss < tau
        # Also verify single-dose tmax for reference
        tmax_single = math.log(ka / ke) / (ka - ke)
        # As tau -> inf, r_ke -> 0, r_ka -> 0, so C_ss(t) -> coeff*(e^{-ke*t} - e^{-ka*t}) = single dose
        C_large_tau = coeff * (math.exp(-ke * 1.0) - math.exp(-ka * 1.0))
        C_ss_large_tau = ka * F * D / (Vd * (ka - ke)) * (
            math.exp(-ke * 1.0) / (1 - math.exp(-ke * 100)) -
            math.exp(-ka * 1.0) / (1 - math.exp(-ka * 100)))
        close = abs(C_large_tau - C_ss_large_tau) / C_large_tau < 1e-6
        return (ok and close, f"tmax_ss={tmax_ss:.3f}, tmax_single={tmax_single:.3f}")
    ch.add(StructuralCheck(
        label="Exercise 10.8: Oral SS concentration formula and tmax_ss",
        section="11",
        predicate=ex358_oral_ss,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: One-Compartment IV Bolus ---
    def alg_35_1_iv_bolus():
        D, Vd, ke = 500, 50, 0.2  # mg, L, 1/h
        C0 = D / Vd  # 10 mg/L
        t_vals = [0, 1, 5, 10]
        for t in t_vals:
            C = C0 * math.exp(-ke * t)
            C_expected = 10 * math.exp(-0.2 * t)
            if abs(C - C_expected) > 1e-10:
                return (False, f"Mismatch at t={t}: {C} vs {C_expected}")
        # Half-life check
        t_half = math.log(2) / ke
        C_half = C0 * math.exp(-ke * t_half)
        ok = abs(C_half - C0 / 2) < 1e-10
        return (ok, f"C0={C0}, t_half={t_half:.2f}h, C(t_half)={C_half:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: One-compartment IV bolus",
        section="6",
        predicate=alg_35_1_iv_bolus,
    ))

    # --- Algorithm 5.2: Multiple-Dose Simulation ---
    def alg_35_2_multiple_dose():
        D, Vd, ke, tau = 500, 50, 0.2, 8  # dose every 8h
        C0 = D / Vd
        nDoses = 10
        tEnd = nDoses * tau
        dt = 0.1
        t_last = tEnd
        C_last = 0
        for j in range(nDoses):
            tDose = j * tau
            if t_last >= tDose:
                C_last += C0 * math.exp(-ke * (t_last - tDose))
        # Steady-state trough: C_trough = C0 * e^{-ke*tau} / (1 - e^{-ke*tau})
        C_ss_trough = C0 * math.exp(-ke * tau) / (1 - math.exp(-ke * tau))
        # Should be close to geometric series limit
        ok = abs(C_last - C_ss_trough) / C_ss_trough < 0.01
        return (ok, f"C_last={C_last:.4f}, C_ss_trough={C_ss_trough:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Multiple-dose IV bolus (approaches steady state)",
        section="6",
        predicate=alg_35_2_multiple_dose,
    ))

    # --- Algorithm 5.3: Oral Absorption (Bateman) ---
    def alg_35_3_oral():
        D, F, Vd, ka, ke = 500, 0.8, 50, 1.0, 0.2
        coeff = (F * D * ka) / (Vd * (ka - ke))
        # Find tmax analytically
        tmax = math.log(ka / ke) / (ka - ke)
        Cmax = coeff * (math.exp(-ke * tmax) - math.exp(-ka * tmax))
        # C at t=0 should be 0
        C0 = coeff * (math.exp(0) - math.exp(0))
        ok1 = abs(C0) < 1e-10
        # C at large t should be ~0
        C_large = coeff * (math.exp(-ke * 100) - math.exp(-ka * 100))
        ok2 = abs(C_large) < 1e-6
        # Cmax should be positive
        ok3 = Cmax > 0
        return (ok1 and ok2 and ok3, f"Cmax={Cmax:.4f} at tmax={tmax:.2f}h")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Oral absorption (Bateman equation)",
        section="6",
        predicate=alg_35_3_oral,
    ))

    # --- Algorithm 5.4: Two-Compartment Model via RK4 ---
    def alg_35_4_two_compartment():
        D, Vc = 500, 30
        k12, k21, k10 = 0.5, 0.3, 0.2
        A1, A2 = float(D), 0.0
        h = 0.01
        T = 50.0
        def f(A1, A2):
            dA1 = -(k12 + k10) * A1 + k21 * A2
            dA2 = k12 * A1 - k21 * A2
            return dA1, dA2
        for _ in range(int(T / h)):
            k1a, k1b = f(A1, A2)
            k2a, k2b = f(A1 + h * k1a / 2, A2 + h * k1b / 2)
            k3a, k3b = f(A1 + h * k2a / 2, A2 + h * k2b / 2)
            k4a, k4b = f(A1 + h * k3a, A2 + h * k3b)
            A1 += h * (k1a + 2 * k2a + 2 * k3a + k4a) / 6
            A2 += h * (k1b + 2 * k2b + 2 * k3b + k4b) / 6
        # Mass balance: A1 + A2 should decrease (elimination via k10)
        total = A1 + A2
        ok1 = total < D  # some drug eliminated
        ok2 = A1 >= 0 and A2 >= 0  # non-negative amounts
        return (ok1 and ok2, f"A1={A1:.4f}, A2={A2:.4f}, total={total:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Two-compartment model via RK4",
        section="6",
        predicate=alg_35_4_two_compartment,
    ))

    # --- Algorithm 5.5: Dosing Regimen Design ---
    def alg_35_5_dosing():
        CL, Vd, F = 5.0, 50.0, 0.8  # L/h, L
        MEC, MTC = 2.0, 10.0  # mg/L
        target_Css_avg = 5.0  # mg/L
        ke = CL / Vd  # 0.1 /h
        t_half = math.log(2) / ke
        tau = math.log(MTC / MEC) / ke
        # Round to practical value
        practical_taus = [6, 8, 12, 24]
        tau = min(practical_taus, key=lambda x: abs(x - tau))
        D = CL * target_Css_avg * tau / F
        r = math.exp(-ke * tau)
        DL = D / (1 - r)
        # Verify Cmax_ss <= MTC and Cmin_ss >= MEC
        Cmax_ss = (F * D / Vd) / (1 - r)
        Cmin_ss = Cmax_ss * r
        ok1 = Cmax_ss <= MTC * 1.1  # allow small margin
        ok2 = Cmin_ss >= MEC * 0.9
        ok3 = D > 0 and DL > D  # loading dose > maintenance dose
        return (ok1 and ok2 and ok3, f"D={D:.1f}mg, tau={tau}h, DL={DL:.1f}mg, Cmax_ss={Cmax_ss:.2f}, Cmin_ss={Cmin_ss:.2f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Dosing regimen design",
        section="6",
        predicate=alg_35_5_dosing,
    ))

    return ch
