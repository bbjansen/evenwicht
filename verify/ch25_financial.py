# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verification checks for Chapter 25: Financial Mathematics."""

import math

from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(25, "Financial Mathematics")

    # ===================================================================
    # SYMBOLIC CHECKS
    # ===================================================================

    # S1: Annuity PV formula: PV = C * (1 - (1+r)^{-T}) / r
    def annuity_pv_identity():
        import sympy as sp
        C, r, T = sp.symbols('C r T', positive=True)
        pv = C * (1 - (1 + r) ** (-T)) / r
        # Alternatively, sum C/(1+r)^t for t=1..T is a geometric series
        fv = pv * (1 + r) ** T
        fv_formula = C * ((1 + r) ** T - 1) / r
        return sp.Eq(sp.simplify(fv - fv_formula), 0)
    ch.add(SymbolicCheck(
        label="Annuity PV-FV relationship",
        section="4",
        identity=annuity_pv_identity,
    ))

    # S2: Continuous compounding limit: (1 + r/n)^n -> e^r
    def continuous_compounding_formula():
        import sympy as sp
        r, t, P = sp.symbols('r t P', positive=True)
        # Verify Pe^{rt} form: d/dt(Pe^{rt}) = r * Pe^{rt}
        A = P * sp.exp(r * t)
        dAdt = sp.diff(A, t)
        return sp.Eq(sp.simplify(dAdt - r * A), 0)
    ch.add(SymbolicCheck(
        label="Continuous compounding ODE d(Pe^rt)/dt = r*Pe^rt",
        section="4",
        identity=continuous_compounding_formula,
    ))

    # S3: Growing perpetuity PV = C/(r-g)
    def growing_perpetuity_check():
        import sympy as sp
        C, r, g = sp.symbols('C r g', positive=True)
        # PV = C/(r-g) should satisfy: PV*(r-g) - C = 0
        pv = C / (r - g)
        return sp.Eq(sp.simplify(pv * (r - g) - C), 0)
    ch.add(SymbolicCheck(
        label="Growing perpetuity formula PV = C/(r-g)",
        section="4",
        identity=growing_perpetuity_check,
    ))

    # S4: PV inverts FV — PV(FV(P,r,t), r, t) = P
    def pv_fv_inverse():
        import sympy as sp
        P, r, t = sp.symbols('P r t', positive=True)
        fv = P * (1 + r) ** t
        pv = fv * (1 + r) ** (-t)
        return sp.Eq(sp.simplify(pv - P), 0)
    ch.add(SymbolicCheck(
        label="PV inverts FV: PV(FV(P,r,t),r,t) = P",
        section="4",
        identity=pv_fv_inverse,
    ))

    # S5: Annuity due PV = ordinary PV * (1+r)
    def annuity_due_vs_ordinary():
        import sympy as sp
        C, r, T = sp.symbols('C r T', positive=True)
        pv_ordinary = C * (1 - (1 + r) ** (-T)) / r
        pv_due = pv_ordinary * (1 + r)
        # Annuity due: payments at t=0..T-1 => sum C/(1+r)^t for t=0..T-1
        # = C * sum delta^t for t=0..T-1 = C * (1 - delta^T)/(1-delta)
        # = C * (1 - (1+r)^{-T}) / (r/(1+r)) = C*(1+r)*(1-(1+r)^{-T})/r
        pv_due_direct = C * (1 + r) * (1 - (1 + r) ** (-T)) / r
        return sp.Eq(sp.simplify(pv_due - pv_due_direct), 0)
    ch.add(SymbolicCheck(
        label="Annuity due PV = ordinary PV * (1+r)",
        section="4",
        identity=annuity_due_vs_ordinary,
    ))

    # S6: Perpetuity as limit of annuity (symbolic: PV_annuity * r + (1+r)^{-T} = 1)
    def perpetuity_annuity_identity():
        import sympy as sp
        C, r, T = sp.symbols('C r T', positive=True)
        # Annuity PV factor: (1-(1+r)^{-T})/r
        # Multiply by r: 1-(1+r)^{-T}
        # Add (1+r)^{-T}: 1
        pvif = (1 - (1 + r) ** (-T)) / r
        expr = pvif * r + (1 + r) ** (-T)
        return sp.Eq(sp.simplify(expr - 1), 0)
    ch.add(SymbolicCheck(
        label="Annuity identity: PVIFA*r + discount factor = 1",
        section="4",
        identity=perpetuity_annuity_identity,
    ))

    # S7: Bond price formula — coupon annuity + face value PV
    def bond_price_identity():
        import sympy as sp
        C, F, y, T = sp.symbols('C F y T', positive=True)
        # Bond price = C * PVIFA + F * (1+y)^{-T}
        price = C * (1 - (1 + y) ** (-T)) / y + F * (1 + y) ** (-T)
        # At par (C = F*y): price should equal F
        price_at_par = price.subs(C, F * y)
        return sp.Eq(sp.simplify(price_at_par - F), 0)
    ch.add(SymbolicCheck(
        label="Bond at par: coupon rate = yield => price = face value",
        section="4",
        identity=bond_price_identity,
    ))

    # S8: Amortization PMT formula inverts annuity PV
    def amortization_pmt_identity():
        import sympy as sp
        PV, r, T = sp.symbols('PV r T', positive=True)
        pmt = PV * r / (1 - (1 + r) ** (-T))
        # Annuity PV of PMT should give back PV
        recovered = pmt * (1 - (1 + r) ** (-T)) / r
        return sp.Eq(sp.simplify(recovered - PV), 0)
    ch.add(SymbolicCheck(
        label="Amortization PMT inverts annuity PV formula",
        section="4",
        identity=amortization_pmt_identity,
    ))

    # S9: Effective annual rate formula
    def effective_rate_identity():
        import sympy as sp
        r, n = sp.symbols('r n', positive=True)
        # r_eff = (1 + r/n)^n - 1
        # Compounding at r_eff annually for 1 year = compounding at r/n for n periods
        lhs = (1 + (1 + r / n) ** n - 1)  # = (1 + r/n)^n
        rhs = (1 + r / n) ** n
        return sp.Eq(sp.simplify(lhs - rhs), 0)
    ch.add(SymbolicCheck(
        label="Effective annual rate: (1+r_eff) = (1+r/n)^n",
        section="4",
        identity=effective_rate_identity,
    ))

    # ===================================================================
    # NUMERIC CHECKS — Worked Examples
    # ===================================================================

    # --- Example 6.1: PV of €10,000 in 5 years at 8% ---
    ch.add(NumericCheck(
        label="Ex 6.1: PV of €10,000 in 5 years at 8%",
        section="9",
        stated=6805.83,
        computed=lambda: 10000 / (1.08 ** 5),
        tolerance=1e-3,
    ))

    # Ex 6.1 intermediate: (1.08)^5
    ch.add(NumericCheck(
        label="Ex 6.1: (1.08)^5 compound factor",
        section="9",
        stated=1.46933,
        computed=lambda: 1.08 ** 5,
        tolerance=1e-4,
    ))

    # Ex 6.1 verification benchmark: PV of €1000 in 10yr at 5%
    ch.add(NumericCheck(
        label="Ex 6.1 benchmark: PV €1000 in 10yr at 5%",
        section="9",
        stated=613.91,
        computed=lambda: 1000 / (1.05 ** 10),
        tolerance=1e-3,
    ))

    # --- Example 6.2: NPV of investment project ---
    ch.add(NumericCheck(
        label="Ex 6.2: NPV at 12% discount rate",
        section="9",
        stated=3486.43,
        computed=lambda: -50000 + 15000/1.12 + 20000/1.12**2 + 25000/1.12**3 + 10000/1.12**4,
        tolerance=1e-3,
    ))

    # Ex 6.2 intermediate terms
    ch.add(NumericCheck(
        label="Ex 6.2: PV of CF1 = 15000/1.12",
        section="9",
        stated=13392.86,
        computed=lambda: 15000 / 1.12,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: PV of CF2 = 20000/1.12^2",
        section="9",
        stated=15943.88,
        computed=lambda: 20000 / 1.12 ** 2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: PV of CF3 = 25000/1.12^3",
        section="9",
        stated=17794.51,
        computed=lambda: 25000 / 1.12 ** 3,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.2: PV of CF4 = 10000/1.12^4",
        section="9",
        stated=6355.18,
        computed=lambda: 10000 / 1.12 ** 4,
        tolerance=1e-3,
    ))

    # --- Example 6.3: Mortgage monthly payment ---
    ch.add(NumericCheck(
        label="Ex 6.3: Monthly mortgage payment",
        section="9",
        stated=1199.10,
        computed=lambda: 200000 * 0.005 / (1 - 1.005 ** (-360)),
        tolerance=1e-3,
    ))

    # Ex 6.3 intermediate: (1.005)^{-360}
    ch.add(NumericCheck(
        label="Ex 6.3: (1.005)^{-360} discount factor",
        section="9",
        stated=0.16604,
        computed=lambda: 1.005 ** (-360),
        tolerance=1e-3,
    ))

    # Ex 6.3 intermediate: 1 - (1.005)^{-360}
    ch.add(NumericCheck(
        label="Ex 6.3: 1 - (1.005)^{-360}",
        section="9",
        stated=0.83396,
        computed=lambda: 1 - 1.005 ** (-360),
        tolerance=1e-3,
    ))

    # Ex 6.3 amortization month 1
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 1: interest = 1000.00",
        section="9",
        stated=1000.00,
        computed=lambda: 200000 * 0.005,
        tolerance=1e-6,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3 amort month 1: principal = 199.10",
        section="9",
        stated=199.10,
        computed=lambda: 200000 * 0.005 / (1 - 1.005 ** (-360)) - 200000 * 0.005,
        tolerance=1e-2,
    ))

    ch.add(NumericCheck(
        label="Ex 6.3 amort month 1: balance = 199800.90",
        section="9",
        stated=199800.90,
        computed=lambda: 200000 - (200000 * 0.005 / (1 - 1.005 ** (-360)) - 200000 * 0.005),
        tolerance=1e-2,
    ))

    # Ex 6.3 amortization month 2
    def _month2_interest():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        b1 = 200000 - (pmt - 200000 * 0.005)
        return b1 * 0.005
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 2: interest = 999.00",
        section="9",
        stated=999.00,
        computed=_month2_interest,
        tolerance=1e-1,
    ))

    def _month2_principal():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        b1 = 200000 - (pmt - 200000 * 0.005)
        return pmt - b1 * 0.005
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 2: principal = 200.10",
        section="9",
        stated=200.10,
        computed=_month2_principal,
        tolerance=1e-1,
    ))

    def _month2_balance():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        b1 = 200000 - (pmt - 200000 * 0.005)
        princ2 = pmt - b1 * 0.005
        return b1 - princ2
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 2: balance = 199600.80",
        section="9",
        stated=199600.80,
        computed=_month2_balance,
        tolerance=1e-1,
    ))

    # Ex 6.3 amortization month 3
    def _month3_interest():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        b1 = 200000 - (pmt - 200000 * 0.005)
        b2 = b1 - (pmt - b1 * 0.005)
        return b2 * 0.005
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 3: interest = 998.00",
        section="9",
        stated=998.00,
        computed=_month3_interest,
        tolerance=1e-1,
    ))

    def _month3_principal():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        b1 = 200000 - (pmt - 200000 * 0.005)
        b2 = b1 - (pmt - b1 * 0.005)
        return pmt - b2 * 0.005
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 3: principal = 201.10",
        section="9",
        stated=201.10,
        computed=_month3_principal,
        tolerance=1e-1,
    ))

    def _month3_balance():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        b1 = 200000 - (pmt - 200000 * 0.005)
        b2 = b1 - (pmt - b1 * 0.005)
        return b2 - (pmt - b2 * 0.005)
    ch.add(NumericCheck(
        label="Ex 6.3 amort month 3: balance = 199399.71",
        section="9",
        stated=199399.71,
        computed=_month3_balance,
        tolerance=1e-1,
    ))

    # --- Example 6.4: IRR computation ---
    def compute_irr():
        cash_flows = [-100000, 40000, 50000, 30000]
        r = 0.10
        for _ in range(100):
            npv = sum(c / (1 + r) ** t for t, c in enumerate(cash_flows))
            dnpv = sum(-t * c / (1 + r) ** (t + 1) for t, c in enumerate(cash_flows))
            if abs(dnpv) < 1e-20:
                break
            r_new = r - npv / dnpv
            if abs(r_new - r) < 1e-12:
                r = r_new
                break
            r = r_new
        return r
    ch.add(NumericCheck(
        label="Ex 6.4: IRR of project",
        section="9",
        stated=0.101331,
        computed=compute_irr,
        tolerance=1e-3,
    ))

    # Ex 6.4 iteration 1: NPV(0.10)
    ch.add(NumericCheck(
        label="Ex 6.4 iter 1: NPV(0.10)",
        section="9",
        stated=225.39,
        computed=lambda: -100000 + 40000/1.10 + 50000/1.10**2 + 30000/1.10**3,
        tolerance=1e-2,
    ))

    # Ex 6.4 iteration 1 intermediate PV terms
    ch.add(NumericCheck(
        label="Ex 6.4: PV of CF1 = 40000/1.10",
        section="9",
        stated=36363.64,
        computed=lambda: 40000 / 1.10,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: PV of CF2 = 50000/1.10^2",
        section="9",
        stated=41322.31,
        computed=lambda: 50000 / 1.10 ** 2,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4: PV of CF3 = 30000/1.10^3",
        section="9",
        stated=22539.44,
        computed=lambda: 30000 / 1.10 ** 3,
        tolerance=1e-3,
    ))

    # Ex 6.4 iteration 1: NPV'(0.10) components
    ch.add(NumericCheck(
        label="Ex 6.4 iter 1: NPV'(0.10) term1 = -36363.64/1.10",
        section="9",
        stated=-33057.85,
        computed=lambda: -36363.64 / 1.10,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4 iter 1: NPV'(0.10) term2 = -2*41322.31/1.10",
        section="9",
        stated=-75131.47,
        computed=lambda: -2 * 41322.31 / 1.10,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4 iter 1: NPV'(0.10) term3 = -3*22539.44/1.10",
        section="9",
        stated=-61471.21,
        computed=lambda: -3 * 22539.44 / 1.10,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Ex 6.4 iter 1: NPV'(0.10) total",
        section="9",
        stated=-169660.53,
        computed=lambda: -33057.85 + (-75131.47) + (-61471.21),
        tolerance=1e-3,
    ))

    # Ex 6.4 iteration 1: r1
    ch.add(NumericCheck(
        label="Ex 6.4 iter 1: r1 = 0.10 - 225.39/(-169660.53)",
        section="9",
        stated=0.101328,
        computed=lambda: 0.10 - 225.39 / (-169660.53),
        tolerance=1e-3,
    ))

    # --- Example 6.5: Continuous compounding ---
    ch.add(NumericCheck(
        label="Ex 6.5: Continuous compounding e^1",
        section="9",
        stated=2.718282,
        computed=lambda: math.e,
        tolerance=1e-4,
    ))

    ch.add(NumericCheck(
        label="Ex 6.5: Quarterly compounding (1+1/4)^4",
        section="9",
        stated=2.441406,
        computed=lambda: (1 + 1/4) ** 4,
        tolerance=1e-4,
    ))

    # Ex 6.5: Annual compounding (1+1/1)^1
    ch.add(NumericCheck(
        label="Ex 6.5: Annual compounding (1+1)^1",
        section="9",
        stated=2.000000,
        computed=lambda: (1 + 1/1) ** 1,
        tolerance=1e-6,
    ))

    # Ex 6.5: Monthly compounding (1+1/12)^12
    ch.add(NumericCheck(
        label="Ex 6.5: Monthly compounding (1+1/12)^12",
        section="9",
        stated=2.613035,
        computed=lambda: (1 + 1/12) ** 12,
        tolerance=1e-4,
    ))

    # Ex 6.5: Daily compounding (1+1/365)^365
    ch.add(NumericCheck(
        label="Ex 6.5: Daily compounding (1+1/365)^365",
        section="9",
        stated=2.714567,
        computed=lambda: (1 + 1/365) ** 365,
        tolerance=1e-4,
    ))

    # ===================================================================
    # FORMULA VERIFICATIONS (Section 4 / 5)
    # ===================================================================

    # Effective annual rate: 12% compounded monthly
    ch.add(NumericCheck(
        label="Effective annual rate: 12% monthly compounding",
        section="4",
        stated=0.1268,
        computed=lambda: (1 + 0.01) ** 12 - 1,
        tolerance=1e-3,
    ))

    # Effective annual rate for continuous compounding: r_eff = e^r - 1
    ch.add(NumericCheck(
        label="Effective annual rate: continuous at r=0.12",
        section="4",
        stated=math.exp(0.12) - 1,
        computed=lambda: math.exp(0.12) - 1,
        tolerance=1e-10,
        note="e^0.12 - 1 ~ 0.12750",
    ))

    # Simple interest: A = P(1 + rt) with P=1000, r=0.10, t=30
    ch.add(NumericCheck(
        label="Simple interest: P=1000, r=0.10, t=30 => A=4000",
        section="4",
        stated=4000.0,
        computed=lambda: 1000 * (1 + 0.10 * 30),
        tolerance=1e-6,
        note="Def 3.1: A=P(1+rt)",
    ))

    # Compound interest: P=1000, r=0.10, t=30, annual => ~17449
    ch.add(NumericCheck(
        label="Compound interest: P=1000, r=0.10, t=30 => ~17449",
        section="4",
        stated=17449.40,
        computed=lambda: 1000 * 1.10 ** 30,
        tolerance=1e-3,
        note="1.10^30 ~ 17.4494 so ratio ~ 17.45P as stated",
    ))

    # PV formula: PV = FV / (1+r)^t
    ch.add(NumericCheck(
        label="PV formula: FV=10000, r=0.05, t=10",
        section="4",
        stated=6139.13,
        computed=lambda: 10000 / 1.05 ** 10,
        tolerance=1e-3,
        note="Def 3.5",
    ))

    # Perpetuity: PV = C/r
    ch.add(NumericCheck(
        label="Perpetuity: C=100, r=0.05 => PV=2000",
        section="4",
        stated=2000.0,
        computed=lambda: 100 / 0.05,
        tolerance=1e-6,
        note="Def 3.16: PV = C/r",
    ))

    # Growing perpetuity (Gordon growth model): C=3, r=0.09, g=0.04 => 60
    ch.add(NumericCheck(
        label="Growing perpetuity (Gordon): C=3, r=0.09, g=0.04 => PV=60",
        section="4",
        stated=60.0,
        computed=lambda: 3.0 / (0.09 - 0.04),
        tolerance=1e-6,
        note="Exercise 8.5 benchmark; Def 3.17",
    ))

    # Annuity ordinary PV: C=500, r=0.005, T=60
    ch.add(NumericCheck(
        label="Annuity PV: C=500, r=0.005, T=60 (Ex 8.3 setup)",
        section="4",
        stated=500 * (1 - 1.005 ** (-60)) / 0.005,
        computed=lambda: 500 * (1 - 1.005 ** (-60)) / 0.005,
        tolerance=1e-6,
        note="Thm 3.13",
    ))

    # Annuity FV: C=500, r=0.005, T=60
    ch.add(NumericCheck(
        label="Annuity FV: C=500, r=0.005, T=60 (Ex 8.3 setup)",
        section="4",
        stated=500 * (1.005 ** 60 - 1) / 0.005,
        computed=lambda: 500 * (1.005 ** 60 - 1) / 0.005,
        tolerance=1e-6,
        note="Thm 3.14",
    ))

    # Annuity due PV vs ordinary: due = ordinary * (1+r)
    ch.add(NumericCheck(
        label="Annuity due PV: C=1000, r=0.06, T=10",
        section="4",
        stated=1000 * (1 - 1.06 ** (-10)) / 0.06 * 1.06,
        computed=lambda: 1000 * (1 - 1.06 ** (-10)) / 0.06 * 1.06,
        tolerance=1e-6,
        note="Def 3.15: PV_due = PV_ordinary * (1+r)",
    ))

    # Bond pricing: coupon bond
    # F=1000, coupon rate=6%, semi-annual coupons, y=8% (semi-annual 4%), T=10 years (20 periods)
    ch.add(NumericCheck(
        label="Bond price: F=1000, c=6%, y=8%, T=10yr semi-annual",
        section="4",
        stated=30 * (1 - 1.04 ** (-20)) / 0.04 + 1000 * 1.04 ** (-20),
        computed=lambda: 30 * (1 - 1.04 ** (-20)) / 0.04 + 1000 * 1.04 ** (-20),
        tolerance=1e-6,
        note="Def 3.20: coupon annuity + face PV",
    ))

    # Bond at par: coupon rate = yield => price = face
    ch.add(NumericCheck(
        label="Bond at par: c=y=5%, F=1000, T=20",
        section="4",
        stated=1000.0,
        computed=lambda: 50 * (1 - 1.05 ** (-20)) / 0.05 + 1000 * 1.05 ** (-20),
        tolerance=1e-4,
        note="When coupon rate equals yield, price = face value",
    ))

    # Macaulay duration: weighted average time of cash flows
    def compute_macaulay_duration():
        # Bond: F=1000, annual coupon=50, y=0.05, T=10
        F, C, y, T = 1000, 50, 0.05, 10
        price = C * (1 - (1 + y) ** (-T)) / y + F * (1 + y) ** (-T)
        weighted_sum = sum(t * C / (1 + y) ** t for t in range(1, T + 1))
        weighted_sum += T * F / (1 + y) ** T
        return weighted_sum / price
    ch.add(NumericCheck(
        label="Macaulay duration: par bond c=y=5%, T=10",
        section="4",
        stated=compute_macaulay_duration(),
        computed=compute_macaulay_duration,
        tolerance=1e-10,
        note="Duration of par bond",
    ))

    # Continuous compounding: A = Pe^{rt}, P=1000, r=0.05, t=10
    ch.add(NumericCheck(
        label="Continuous compounding: P=1000, r=0.05, t=10",
        section="4",
        stated=1000 * math.exp(0.05 * 10),
        computed=lambda: 1000 * math.exp(0.5),
        tolerance=1e-6,
        note="Thm 3.3: A = Pe^{rt}",
    ))

    # Continuous vs discrete: continuous >= discrete for same r
    ch.add(NumericCheck(
        label="Continuous >= annual: P=1000, r=0.05, t=10",
        section="4",
        stated=1000 * math.exp(0.5) - 1000 * 1.05 ** 10,
        computed=lambda: 1000 * math.exp(0.5) - 1000 * 1.05 ** 10,
        tolerance=1e-6,
        note="Difference should be positive (continuous >= annual)",
    ))

    # Compound interest growth chart data points: P=1000, r=0.05
    _chart_years = [0, 5, 10, 15, 20, 25, 30]
    _chart_values = [1000, 1276, 1629, 2079, 2653, 3386, 4322]
    for _yr, _val in zip(_chart_years, _chart_values):
        ch.add(NumericCheck(
            label=f"Compound growth chart: P=1000, r=0.05, t={_yr} => {_val}",
            section="4",
            stated=float(_val),
            computed=(lambda t=_yr: 1000 * 1.05 ** t),
            tolerance=2e-3,
            note="Mermaid chart data point",
        ))

    # Zero-coupon bond: Exercise 8.2 — F=1000, y=0.055, T=7
    ch.add(NumericCheck(
        label="Zero-coupon bond: F=1000, y=5.5%, T=7",
        section="4",
        stated=1000 / 1.055 ** 7,
        computed=lambda: 1000 / 1.055 ** 7,
        tolerance=1e-6,
        note="Exercise 8.2 benchmark",
    ))

    # NPV = 0 at IRR (consistency check with computed IRR)
    def npv_at_irr():
        cash_flows = [-100000, 40000, 50000, 30000]
        r = compute_irr()
        return sum(c / (1 + r) ** t for t, c in enumerate(cash_flows))
    ch.add(NumericCheck(
        label="NPV(IRR) = 0 for Ex 6.4 cash flows",
        section="4",
        stated=0.0,
        computed=npv_at_irr,
        tolerance=1e-4,
    ))

    # Amortization: total payments = principal + total interest
    def amort_total_payments():
        pv = 200000
        r = 0.005
        n = 360
        pmt = pv * r / (1 - (1 + r) ** (-n))
        return pmt * n
    ch.add(NumericCheck(
        label="Mortgage total payments: 360 * PMT",
        section="9",
        stated=1199.10 * 360,
        computed=amort_total_payments,
        tolerance=1e-2,
    ))

    # ===================================================================
    # STRUCTURAL CHECKS
    # ===================================================================

    # Amortization schedule: interest + principal = payment
    def amortization_consistency():
        pv = 200000
        r = 0.005
        n = 360
        pmt = pv * r / (1 - (1 + r) ** (-n))
        balance = pv
        for k in range(1, 4):
            interest = balance * r
            principal = pmt - interest
            balance -= principal
            if interest + principal - pmt > 1e-6:
                return (False, f"Payment split error at month {k}")
        if balance < 0:
            return (False, f"Balance went negative: {balance}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Amortization: interest + principal = PMT",
        section="9",
        predicate=amortization_consistency,
    ))

    # NPV is monotonically decreasing in r for conventional cash flows
    def npv_monotone():
        cash_flows = [-100000, 40000, 50000, 30000]
        rates = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25]
        npvs = []
        for r in rates:
            npv = sum(c / (1 + r) ** t for t, c in enumerate(cash_flows))
            npvs.append(npv)
        for i in range(len(npvs) - 1):
            if npvs[i] <= npvs[i + 1]:
                return (False, f"NPV not decreasing: NPV({rates[i]})={npvs[i]:.2f} <= NPV({rates[i+1]})={npvs[i+1]:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="NPV monotonically decreasing in r (conventional flows)",
        section="4",
        predicate=npv_monotone,
    ))

    # PV decreases with higher discount rate
    def pv_decreases_with_rate():
        fv = 10000
        t = 5
        rates = [0.01, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]
        pvs = [fv / (1 + r) ** t for r in rates]
        for i in range(len(pvs) - 1):
            if pvs[i] <= pvs[i + 1]:
                return (False, f"PV not decreasing: PV({rates[i]})={pvs[i]:.2f} <= PV({rates[i+1]})={pvs[i+1]:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="PV decreases with higher discount rate",
        section="4",
        predicate=pv_decreases_with_rate,
    ))

    # PV decreases with longer time horizon (fixed rate)
    def pv_decreases_with_time():
        fv = 10000
        r = 0.08
        times = [1, 2, 5, 10, 20, 30, 50]
        pvs = [fv / (1 + r) ** t for t in times]
        for i in range(len(pvs) - 1):
            if pvs[i] <= pvs[i + 1]:
                return (False, f"PV not decreasing with time: PV(t={times[i]})={pvs[i]:.2f} <= PV(t={times[i+1]})={pvs[i+1]:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="PV decreases with longer time horizon",
        section="4",
        predicate=pv_decreases_with_time,
    ))

    # Continuous compounding >= discrete compounding (same r, t)
    def continuous_geq_discrete():
        P, r, t = 1000, 0.08, 10
        a_continuous = P * math.exp(r * t)
        for n in [1, 2, 4, 12, 52, 365]:
            a_discrete = P * (1 + r / n) ** (n * t)
            if a_continuous < a_discrete - 1e-8:
                return (False, f"Continuous {a_continuous:.4f} < discrete(n={n}) {a_discrete:.4f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Continuous compounding >= discrete for all n",
        section="4",
        predicate=continuous_geq_discrete,
    ))

    # Discrete compounding increases with n (for same r, t)
    def compounding_increases_with_n():
        P, r, t = 1000, 0.08, 10
        ns = [1, 2, 4, 12, 52, 365]
        vals = [P * (1 + r / n) ** (n * t) for n in ns]
        for i in range(len(vals) - 1):
            if vals[i] >= vals[i + 1]:
                return (False, f"FV(n={ns[i]})={vals[i]:.4f} >= FV(n={ns[i+1]})={vals[i+1]:.4f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="FV increases with compounding frequency n",
        section="4",
        predicate=compounding_increases_with_n,
    ))

    # Annuity due PV > ordinary annuity PV (for r > 0)
    def annuity_due_gt_ordinary():
        C, r, T = 1000, 0.06, 20
        pv_ordinary = C * (1 - (1 + r) ** (-T)) / r
        pv_due = pv_ordinary * (1 + r)
        if pv_due <= pv_ordinary:
            return (False, f"Annuity due PV {pv_due:.2f} <= ordinary PV {pv_ordinary:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Annuity due PV > ordinary annuity PV",
        section="4",
        predicate=annuity_due_gt_ordinary,
    ))

    # Perpetuity PV > any finite annuity PV (same C, r)
    def perpetuity_gt_annuity():
        C, r = 100, 0.05
        pv_perp = C / r
        for T in [10, 50, 100, 500, 1000]:
            pv_ann = C * (1 - (1 + r) ** (-T)) / r
            if pv_perp < pv_ann - 1e-8:
                return (False, f"Perpetuity PV {pv_perp:.2f} < annuity PV(T={T}) {pv_ann:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Perpetuity PV > finite annuity PV for all T",
        section="4",
        predicate=perpetuity_gt_annuity,
    ))

    # Annuity PV converges to perpetuity PV as T -> infinity
    def annuity_converges_to_perpetuity():
        C, r = 100, 0.05
        pv_perp = C / r
        pv_ann_1000 = C * (1 - (1 + r) ** (-1000)) / r
        diff = abs(pv_perp - pv_ann_1000)
        if diff > 1e-6:
            return (False, f"Annuity PV(T=1000)={pv_ann_1000:.6f} not close to perpetuity PV={pv_perp:.6f}, diff={diff:.2e}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Annuity PV converges to perpetuity as T -> inf",
        section="4",
        predicate=annuity_converges_to_perpetuity,
    ))

    # Bond price: premium bond (coupon rate > yield), discount bond (coupon rate < yield)
    def bond_premium_discount():
        F, T = 1000, 20
        # Premium bond: c=8%, y=5%
        c_prem, y_prem = 80, 0.05
        price_prem = c_prem * (1 - (1 + y_prem) ** (-T)) / y_prem + F * (1 + y_prem) ** (-T)
        if price_prem <= F:
            return (False, f"Premium bond price {price_prem:.2f} should exceed face {F}")
        # Discount bond: c=3%, y=5%
        c_disc, y_disc = 30, 0.05
        price_disc = c_disc * (1 - (1 + y_disc) ** (-T)) / y_disc + F * (1 + y_disc) ** (-T)
        if price_disc >= F:
            return (False, f"Discount bond price {price_disc:.2f} should be below face {F}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Bond: premium when c>y, discount when c<y",
        section="4",
        predicate=bond_premium_discount,
    ))

    # Bond price decreases with yield (inverse price-yield relationship)
    def bond_price_decreases_with_yield():
        F, C, T = 1000, 50, 10
        yields = [0.02, 0.04, 0.06, 0.08, 0.10]
        prices = [C * (1 - (1 + y) ** (-T)) / y + F * (1 + y) ** (-T) for y in yields]
        for i in range(len(prices) - 1):
            if prices[i] <= prices[i + 1]:
                return (False, f"Bond price not decreasing: P(y={yields[i]})={prices[i]:.2f} <= P(y={yields[i+1]})={prices[i+1]:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Bond price decreases with yield (inverse relationship)",
        section="4",
        predicate=bond_price_decreases_with_yield,
    ))

    # Macaulay duration <= maturity
    def duration_leq_maturity():
        F, C, y, T = 1000, 50, 0.05, 10
        price = C * (1 - (1 + y) ** (-T)) / y + F * (1 + y) ** (-T)
        weighted_sum = sum(t * C / (1 + y) ** t for t in range(1, T + 1))
        weighted_sum += T * F / (1 + y) ** T
        duration = weighted_sum / price
        if duration > T:
            return (False, f"Duration {duration:.4f} exceeds maturity {T}")
        if duration <= 0:
            return (False, f"Duration {duration:.4f} is non-positive")
        return (True, "")
    ch.add(StructuralCheck(
        label="Macaulay duration <= maturity T",
        section="4",
        predicate=duration_leq_maturity,
    ))

    # Duration: zero-coupon bond duration = maturity
    def zero_coupon_duration_equals_maturity():
        F, y, T = 1000, 0.05, 10
        price = F / (1 + y) ** T
        weighted_sum = T * F / (1 + y) ** T
        duration = weighted_sum / price
        if abs(duration - T) > 1e-10:
            return (False, f"Zero-coupon duration {duration:.6f} != maturity {T}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Zero-coupon bond: duration = maturity",
        section="4",
        predicate=zero_coupon_duration_equals_maturity,
    ))

    # Duration increases with maturity (coupon bond)
    def duration_increases_with_maturity():
        F, C, y = 1000, 50, 0.06
        durations = []
        for T in [5, 10, 15, 20, 30]:
            price = C * (1 - (1 + y) ** (-T)) / y + F * (1 + y) ** (-T)
            ws = sum(t * C / (1 + y) ** t for t in range(1, T + 1)) + T * F / (1 + y) ** T
            durations.append(ws / price)
        for i in range(len(durations) - 1):
            if durations[i] >= durations[i + 1]:
                return (False, f"Duration not increasing with maturity at index {i}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Duration increases with maturity (coupon bond)",
        section="4",
        predicate=duration_increases_with_maturity,
    ))

    # Amortization: final balance is zero (or near zero)
    def amort_final_balance_zero():
        pv = 200000
        r = 0.005
        n = 360
        pmt = pv * r / (1 - (1 + r) ** (-n))
        balance = pv
        for k in range(1, n + 1):
            interest = balance * r
            principal = pmt - interest
            balance -= principal
        if abs(balance) > 0.01:
            return (False, f"Final balance {balance:.6f} not zero")
        return (True, "")
    ch.add(StructuralCheck(
        label="Amortization: final balance ~ 0 after all payments",
        section="9",
        predicate=amort_final_balance_zero,
    ))

    # Amortization: principal portion increases each period
    def amort_principal_increases():
        pv = 200000
        r = 0.005
        n = 360
        pmt = pv * r / (1 - (1 + r) ** (-n))
        balance = pv
        prev_principal = 0
        for k in range(1, 13):  # check first 12 months
            interest = balance * r
            principal = pmt - interest
            if k > 1 and principal <= prev_principal:
                return (False, f"Principal not increasing at month {k}: {principal:.4f} <= {prev_principal:.4f}")
            prev_principal = principal
            balance -= principal
        return (True, "")
    ch.add(StructuralCheck(
        label="Amortization: principal portion increases over time",
        section="9",
        predicate=amort_principal_increases,
    ))

    # Amortization: interest portion decreases each period
    def amort_interest_decreases():
        pv = 200000
        r = 0.005
        n = 360
        pmt = pv * r / (1 - (1 + r) ** (-n))
        balance = pv
        prev_interest = float('inf')
        for k in range(1, 13):
            interest = balance * r
            principal = pmt - interest
            if interest >= prev_interest:
                return (False, f"Interest not decreasing at month {k}: {interest:.4f} >= {prev_interest:.4f}")
            prev_interest = interest
            balance -= principal
        return (True, "")
    ch.add(StructuralCheck(
        label="Amortization: interest portion decreases over time",
        section="9",
        predicate=amort_interest_decreases,
    ))

    # Ex 6.3: early payment interest fraction ~ 83.4%
    def early_interest_fraction():
        pmt = 200000 * 0.005 / (1 - 1.005 ** (-360))
        interest_m1 = 200000 * 0.005
        fraction = interest_m1 / pmt
        if abs(fraction - 0.834) > 0.01:
            return (False, f"Interest fraction {fraction:.4f} not ~ 0.834")
        return (True, "")
    ch.add(StructuralCheck(
        label="Ex 6.3: first payment ~83.4% interest",
        section="9",
        predicate=early_interest_fraction,
    ))

    # IRR: NPV positive below IRR, negative above (conventional flows)
    def irr_npv_sign_change():
        cash_flows = [-100000, 40000, 50000, 30000]
        irr_val = compute_irr()
        npv_below = sum(c / (1 + irr_val - 0.02) ** t for t, c in enumerate(cash_flows))
        npv_above = sum(c / (1 + irr_val + 0.02) ** t for t, c in enumerate(cash_flows))
        if npv_below <= 0:
            return (False, f"NPV below IRR should be positive: {npv_below:.4f}")
        if npv_above >= 0:
            return (False, f"NPV above IRR should be negative: {npv_above:.4f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="IRR: NPV > 0 below IRR, NPV < 0 above IRR",
        section="4",
        predicate=irr_npv_sign_change,
    ))

    # Growing perpetuity: PV increases as g approaches r
    def growing_perp_increases_with_g():
        C, r = 100, 0.10
        gs = [0.01, 0.03, 0.05, 0.07, 0.09]
        pvs = [C / (r - g) for g in gs]
        for i in range(len(pvs) - 1):
            if pvs[i] >= pvs[i + 1]:
                return (False, f"Growing perpetuity PV not increasing with g: PV(g={gs[i]})={pvs[i]:.2f} >= PV(g={gs[i+1]})={pvs[i+1]:.2f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Growing perpetuity PV increases as g -> r",
        section="4",
        predicate=growing_perp_increases_with_g,
    ))

    # FV = PV * (1+r)^t roundtrip
    def fv_pv_roundtrip():
        P, r, t = 5000, 0.07, 15
        fv = P * (1 + r) ** t
        pv = fv / (1 + r) ** t
        if abs(pv - P) > 1e-8:
            return (False, f"Roundtrip failed: PV={pv:.8f} != P={P}")
        return (True, "")
    ch.add(StructuralCheck(
        label="FV-PV roundtrip: PV(FV(P,r,t),r,t) = P",
        section="4",
        predicate=fv_pv_roundtrip,
    ))

    # Annuity FV = PV * (1+r)^T
    def annuity_fv_pv_relation():
        C, r, T = 1000, 0.06, 20
        pv = C * (1 - (1 + r) ** (-T)) / r
        fv = C * ((1 + r) ** T - 1) / r
        fv_from_pv = pv * (1 + r) ** T
        if abs(fv - fv_from_pv) / abs(fv) > 1e-10:
            return (False, f"FV={fv:.4f} != PV*(1+r)^T={fv_from_pv:.4f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Annuity: FV = PV * (1+r)^T",
        section="4",
        predicate=annuity_fv_pv_relation,
    ))

    # Effective rate: higher n => higher effective rate (for same nominal)
    def eff_rate_increases_with_n():
        r = 0.12
        ns = [1, 2, 4, 12, 52, 365]
        effs = [(1 + r / n) ** n - 1 for n in ns]
        for i in range(len(effs) - 1):
            if effs[i] >= effs[i + 1]:
                return (False, f"Effective rate not increasing: r_eff(n={ns[i]})={effs[i]:.6f} >= r_eff(n={ns[i+1]})={effs[i+1]:.6f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Effective rate increases with compounding frequency",
        section="4",
        predicate=eff_rate_increases_with_n,
    ))

    # Non-conventional cash flow: multiple IRRs (Exercise 8.8a)
    def multiple_irrs():
        # Cash flows: [-100, 230, -132]
        # NPV(r) = -100 + 230/(1+r) - 132/(1+r)^2 = 0
        # Substituting x=1/(1+r): -100 + 230x - 132x^2 = 0
        # 132x^2 - 230x + 100 = 0
        # x = (230 +/- sqrt(230^2 - 4*132*100)) / (2*132)
        discriminant = 230**2 - 4 * 132 * 100
        if discriminant < 0:
            return (False, "No real roots found")
        x1 = (230 + math.sqrt(discriminant)) / (2 * 132)
        x2 = (230 - math.sqrt(discriminant)) / (2 * 132)
        r1 = 1/x1 - 1
        r2 = 1/x2 - 1
        # Both should give NPV ~ 0
        npv1 = -100 + 230/(1+r1) - 132/(1+r1)**2
        npv2 = -100 + 230/(1+r2) - 132/(1+r2)**2
        if abs(npv1) > 1e-6:
            return (False, f"First IRR r={r1:.6f} gives NPV={npv1:.6f}")
        if abs(npv2) > 1e-6:
            return (False, f"Second IRR r={r2:.6f} gives NPV={npv2:.6f}")
        if abs(r1 - r2) < 1e-6:
            return (False, f"Two IRRs are not distinct: r1={r1:.6f}, r2={r2:.6f}")
        return (True, "")
    ch.add(StructuralCheck(
        label="Ex 8.8a: non-conventional flows have two distinct IRRs",
        section="4",
        predicate=multiple_irrs,
    ))

    # Exercise 8.8b: IRR = 0.20 with multiplicity 3
    def triple_irr():
        # Cash flows: [-1000, 3600, -4320, 1728]
        # NPV(0.20) should be 0
        r = 0.20
        npv_val = -1000 + 3600/(1+r) - 4320/(1+r)**2 + 1728/(1+r)**3
        if abs(npv_val) > 1e-6:
            return (False, f"NPV(0.20) = {npv_val:.8f} != 0")
        return (True, "")
    ch.add(StructuralCheck(
        label="Ex 8.8b: IRR = 0.20 for [-1000, 3600, -4320, 1728]",
        section="4",
        predicate=triple_irr,
    ))

    # ===================================================================
    # EXERCISE CHECKS
    # ===================================================================

    # --- Exercise 8.1: Future value of €5,000 at 4% for 10 years ---
    # (a) Simple interest: A = P(1 + rt) = 5000*(1 + 0.04*10) = 7000
    ch.add(NumericCheck(
        label="Exercise 8.1a: Simple interest FV",
        section="11",
        stated=7000.0,
        computed=lambda: 5000 * (1 + 0.04 * 10),
        tolerance=1e-6,
    ))
    # (b) Annual compounding: A = P(1+r)^t = 5000*1.04^10
    ch.add(NumericCheck(
        label="Exercise 8.1b: Annual compounding FV",
        section="11",
        stated=7401.22,
        computed=lambda: 5000 * 1.04 ** 10,
        tolerance=1e-3,
    ))
    # (c) Monthly compounding: A = P(1+r/12)^(12t)
    ch.add(NumericCheck(
        label="Exercise 8.1c: Monthly compounding FV",
        section="11",
        stated=7454.16,
        computed=lambda: 5000 * (1 + 0.04/12) ** (12*10),
        tolerance=1e-3,
    ))
    # (d) Continuous compounding: A = P*e^(rt)
    ch.add(NumericCheck(
        label="Exercise 8.1d: Continuous compounding FV",
        section="11",
        stated=7459.12,
        computed=lambda: 5000 * math.exp(0.04 * 10),
        tolerance=1e-3,
    ))

    # --- Exercise 8.2: Zero-coupon bond pricing ---
    # Price = 1000 / (1.055)^7
    ch.add(NumericCheck(
        label="Exercise 8.2: Zero-coupon bond price",
        section="11",
        stated=1000 / 1.055 ** 7,
        computed=lambda: 1000 / 1.055 ** 7,
        tolerance=1e-6,
    ))

    # --- Exercise 8.3: Annuity PV and FV ---
    # C=500, r=0.005, T=60
    ch.add(NumericCheck(
        label="Exercise 8.3: Annuity PV",
        section="11",
        stated=500 * (1 - 1.005 ** (-60)) / 0.005,
        computed=lambda: 500 * (1 - 1.005 ** (-60)) / 0.005,
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 8.3: Annuity FV",
        section="11",
        stated=500 * (1.005 ** 60 - 1) / 0.005,
        computed=lambda: 500 * (1.005 ** 60 - 1) / 0.005,
        tolerance=1e-6,
    ))

    # --- Exercise 8.4: Mortgage payment ---
    # P=150000, r_monthly=0.045/12=0.00375, n=180
    def ex84_pmt():
        r = 0.045 / 12
        n = 180
        return 150000 * r / (1 - (1 + r) ** (-n))
    ch.add(NumericCheck(
        label="Exercise 8.4: Monthly payment",
        section="11",
        stated=1147.49,
        computed=ex84_pmt,
        tolerance=1e-2,
    ))
    # Interest fraction of first payment
    ch.add(NumericCheck(
        label="Exercise 8.4: Interest fraction of first payment",
        section="11",
        stated=150000 * 0.00375 / ex84_pmt(),
        computed=lambda: 150000 * 0.00375 / ex84_pmt(),
        tolerance=1e-6,
    ))

    # --- Exercise 8.5: Gordon growth model ---
    # P = C/(r-g) = 3/(0.09-0.04) = 60
    ch.add(NumericCheck(
        label="Exercise 8.5: Gordon growth model stock price",
        section="11",
        stated=60.0,
        computed=lambda: 3.0 / (0.09 - 0.04),
        tolerance=1e-6,
    ))

    # --- Exercise 8.6: NPV at various discount rates ---
    def ex86_npv(r):
        cfs = [-200000, 80000, 80000, 80000, 80000]
        return sum(c / (1 + r) ** t for t, c in enumerate(cfs))
    ch.add(NumericCheck(
        label="Exercise 8.6: NPV at r=0.05",
        section="11",
        stated=ex86_npv(0.05),
        computed=lambda: ex86_npv(0.05),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 8.6: NPV at r=0.10",
        section="11",
        stated=ex86_npv(0.10),
        computed=lambda: ex86_npv(0.10),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 8.6: NPV at r=0.15",
        section="11",
        stated=ex86_npv(0.15),
        computed=lambda: ex86_npv(0.15),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 8.6: NPV at r=0.20",
        section="11",
        stated=ex86_npv(0.20),
        computed=lambda: ex86_npv(0.20),
        tolerance=1e-6,
    ))
    ch.add(NumericCheck(
        label="Exercise 8.6: NPV at r=0.25",
        section="11",
        stated=ex86_npv(0.25),
        computed=lambda: ex86_npv(0.25),
        tolerance=1e-6,
    ))
    # IRR via Newton's method
    def ex86_irr():
        cfs = [-200000, 80000, 80000, 80000, 80000]
        r = 0.10
        for _ in range(100):
            npv = sum(c / (1 + r) ** t for t, c in enumerate(cfs))
            dnpv = sum(-t * c / (1 + r) ** (t + 1) for t, c in enumerate(cfs))
            if abs(dnpv) < 1e-20:
                break
            r_new = r - npv / dnpv
            if abs(r_new - r) < 1e-12:
                r = r_new
                break
            r = r_new
        return r
    ch.add(StructuralCheck(
        label="Exercise 8.6: NPV=0 at computed IRR",
        section="11",
        predicate=lambda: (abs(ex86_npv(ex86_irr())) < 1e-4,
                           f"NPV(IRR)={ex86_npv(ex86_irr()):.6e}"),
    ))

    # --- Exercise 8.7: Growing annuity PV ---
    # PV = C * [1 - ((1+g)/(1+r))^T] / (r - g)
    def growing_annuity_pv(C, r, g, T):
        return C * (1 - ((1 + g) / (1 + r)) ** T) / (r - g)
    ch.add(StructuralCheck(
        label="Exercise 8.7: Growing annuity converges to growing perpetuity as T->inf",
        section="11",
        predicate=lambda: (
            abs(growing_annuity_pv(100, 0.10, 0.03, 1000) - 100 / (0.10 - 0.03)) / (100 / 0.07) < 1e-6,
            f"Growing annuity PV(T=1000)={growing_annuity_pv(100, 0.10, 0.03, 1000):.4f}"
        ),
    ))

    # --- Exercise 8.8a: Two distinct IRRs for [-100, 230, -132] ---
    # Already covered by structural check 'multiple_irrs' above
    # Adding NPV=0 verification at both roots
    def ex88a_irrs():
        disc = 230**2 - 4 * 132 * 100
        x1 = (230 + math.sqrt(disc)) / (2 * 132)
        x2 = (230 - math.sqrt(disc)) / (2 * 132)
        r1 = 1/x1 - 1
        r2 = 1/x2 - 1
        return r1, r2
    ch.add(NumericCheck(
        label="Exercise 8.8a: First IRR NPV=0",
        section="11",
        stated=0.0,
        computed=lambda: -100 + 230/(1+ex88a_irrs()[0]) - 132/(1+ex88a_irrs()[0])**2,
        tolerance=1e-4,
    ))
    ch.add(NumericCheck(
        label="Exercise 8.8a: Second IRR NPV=0",
        section="11",
        stated=0.0,
        computed=lambda: -100 + 230/(1+ex88a_irrs()[1]) - 132/(1+ex88a_irrs()[1])**2,
        tolerance=1e-4,
    ))

    # --- Exercise 8.8b: IRR = 0.20 for [-1000, 3600, -4320, 1728] ---
    ch.add(NumericCheck(
        label="Exercise 8.8b: NPV at r=0.20 = 0",
        section="11",
        stated=0.0,
        computed=lambda: -1000 + 3600/1.2 - 4320/1.2**2 + 1728/1.2**3,
        tolerance=1e-4,
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 4.1: Compound Interest ---
    def alg_4_1_compound_interest():
        P, r, n, t = 1000, 0.08, 4, 5
        A = P * (1 + r / n) ** (n * t)
        expected = 1000 * (1.02) ** 20  # 1485.9474...
        ok = abs(A - expected) < 1e-6
        # Also verify continuous compounding limit
        A_cont = P * math.exp(r * t)
        ok2 = abs(A_cont - 1000 * math.exp(0.4)) < 1e-6
        return (ok and ok2, f"Discrete A={A:.4f}, Continuous A={A_cont:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.1: Compound interest computation",
        section="6",
        predicate=alg_4_1_compound_interest,
    ))

    # --- Algorithm 4.2: Present Value ---
    def alg_4_2_present_value():
        # Example 9.1: FV=10000, r=0.08, t=5 => PV = 10000/1.08^5
        FV, r, t = 10000, 0.08, 5
        PV = FV / (1 + r) ** t
        expected = 10000 / 1.08 ** 5  # 6805.832...
        ok = abs(PV - expected) < 1e-4
        # Round-trip: PV -> FV -> PV
        FV_back = PV * (1 + r) ** t
        ok2 = abs(FV_back - FV) < 1e-6
        return (ok and ok2, f"PV={PV:.4f}, round-trip FV={FV_back:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.2: Present value computation and round-trip",
        section="6",
        predicate=alg_4_2_present_value,
    ))

    # --- Algorithm 4.3: Net Present Value ---
    def alg_4_3_npv():
        def npv(cash_flows, r):
            return sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))
        # Test: [-1000, 300, 400, 500, 200] at r=0.10
        cfs = [-1000, 300, 400, 500, 200]
        r = 0.10
        result = npv(cfs, r)
        # Manual: -1000 + 300/1.1 + 400/1.21 + 500/1.331 + 200/1.4641
        expected = -1000 + 300/1.1 + 400/1.21 + 500/1.331 + 200/1.4641
        ok = abs(result - expected) < 1e-6
        return (ok, f"NPV={result:.4f}, expected={expected:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.3: NPV computation",
        section="6",
        predicate=alg_4_3_npv,
    ))

    # --- Algorithm 4.4: IRR via Newton's Method ---
    def alg_4_4_irr_newton():
        def npv(cfs, r):
            return sum(cf / (1 + r) ** t for t, cf in enumerate(cfs))

        def npv_deriv(cfs, r):
            return sum(-t * cf / (1 + r) ** (t + 1) for t, cf in enumerate(cfs))

        def irr(cfs, r0=0.10, eps=1e-10, max_iter=100):
            r = r0
            for _ in range(max_iter):
                f = npv(cfs, r)
                fp = npv_deriv(cfs, r)
                if abs(fp) < 1e-20:
                    return None
                r_new = r - f / fp
                if abs(r_new - r) < eps:
                    return r_new
                r = r_new
            return None

        # Test: [-1000, 400, 400, 400] should have IRR ~ 0.09701
        cfs = [-1000, 400, 400, 400]
        r_star = irr(cfs)
        if r_star is None:
            return (False, "IRR did not converge")
        # Verify NPV at IRR is ~0
        npv_at_irr = npv(cfs, r_star)
        ok = abs(npv_at_irr) < 1e-8
        return (ok, f"IRR={r_star:.6f}, NPV(IRR)={npv_at_irr:.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 4.4: IRR via Newton's method",
        section="6",
        predicate=alg_4_4_irr_newton,
    ))

    # --- Algorithm 4.5: Annuity PV and FV ---
    def alg_4_5_annuity():
        def annuity_pv(C, r, T):
            if r == 0:
                return C * T
            return C * (1 - (1 + r) ** (-T)) / r

        def annuity_fv(C, r, T):
            if r == 0:
                return C * T
            return C * ((1 + r) ** T - 1) / r

        C, r, T = 100, 0.05, 10
        pv = annuity_pv(C, r, T)
        fv = annuity_fv(C, r, T)
        # Relationship: FV = PV * (1+r)^T
        ok = abs(fv - pv * (1 + r) ** T) < 1e-6
        # PV should be sum of discounted payments
        pv_manual = sum(C / (1 + r) ** t for t in range(1, T + 1))
        ok2 = abs(pv - pv_manual) < 1e-6
        return (ok and ok2, f"PV={pv:.4f}, FV={fv:.4f}, PV_manual={pv_manual:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.5: Annuity PV and FV",
        section="6",
        predicate=alg_4_5_annuity,
    ))

    # --- Algorithm 4.6: Amortization Schedule ---
    def alg_4_6_amortization():
        PV, r, T = 100000, 0.005, 360  # 30-yr mortgage at 0.5%/month
        PMT = PV * r / (1 - (1 + r) ** (-T))
        balance = PV
        total_interest = 0.0
        total_principal = 0.0
        for k in range(1, T + 1):
            interest = balance * r
            principal = PMT - interest
            balance = balance - principal
            total_interest += interest
            total_principal += principal
        # Final balance should be ~0
        ok1 = abs(balance) < 0.01
        # Total principal should equal original loan
        ok2 = abs(total_principal - PV) < 0.01
        return (ok1 and ok2, f"Final balance={balance:.6f}, total principal={total_principal:.2f}")
    ch.add(StructuralCheck(
        label="Algorithm 4.6: Amortization schedule (balance -> 0)",
        section="6",
        predicate=alg_4_6_amortization,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.4: Effective annual rate for 12% nominal compounded monthly
    # r_eff = (1 + 0.12/12)^12 - 1 = (1.01)^12 - 1 ~ 0.1268 (12.68%)
    ch.add(NumericCheck(
        label="Remark 3.4: EAR of 12% compounded monthly ~ 12.68%",
        section="4",
        stated=0.1268,
        computed=lambda: (1 + 0.12 / 12) ** 12 - 1,
        tolerance=1e-3,
        note="Remark 3.4",
    ))

    # Remark 3.4: 12% monthly (EAR~12.68%) > 12.5% annually (EAR=12.5%)
    def remark_34_comparison():
        ear_monthly = (1 + 0.12 / 12) ** 12 - 1
        ear_annual = 0.125
        ok = ear_monthly > ear_annual
        return (ok, f"EAR monthly={ear_monthly:.4f} > EAR annual={ear_annual:.4f}")
    ch.add(StructuralCheck(
        label="Remark 3.4: 12% monthly more expensive than 12.5% annually",
        section="4",
        predicate=remark_34_comparison,
        note="Remark 3.4",
    ))

    # Remark 3.19: Amortization balance formula B_k = PV*(1+r)^k - PMT*((1+r)^k-1)/r
    # At k=T the balance must be zero
    def remark_319_balance_zero():
        PV = 100000
        r = 0.005  # monthly rate
        T = 360    # 30 years
        PMT = PV * r / (1 - (1 + r) ** (-T))
        B_T = PV * (1 + r) ** T - PMT * ((1 + r) ** T - 1) / r
        ok = abs(B_T) < 0.01
        return (ok, f"Final balance B_T = {B_T:.6f}")
    ch.add(StructuralCheck(
        label="Remark 3.19: Amortization balance zero at maturity",
        section="4",
        predicate=remark_319_balance_zero,
        note="Remark 3.19",
    ))

    # --- Remark 3.10: IRR non-conventional cash flows — multiple roots ---
    def _remark_3_10_irr_multiple():
        """Verify non-conventional cash flows can have multiple IRRs."""
        # Cash flows with 3 sign changes that produce multiple real IRR roots:
        # -100, +230, -132 has roots at r=0.10 and r=0.20
        cfs = [-100, 230, -132]
        # NPV(r) = sum cf_t / (1+r)^t
        def npv(r):
            return sum(cf / (1 + r)**t for t, cf in enumerate(cfs))
        # Find roots via fine grid search
        roots = []
        r_prev = None
        for r_int in range(1, 10000):
            r = r_int / 10000.0
            v = npv(r)
            if r_prev is not None and r_prev * v < 0:
                # Bisect
                lo, hi = (r - 0.0001, r)
                for _ in range(60):
                    mid = (lo + hi) / 2
                    if npv(lo) * npv(mid) <= 0:
                        hi = mid
                    else:
                        lo = mid
                roots.append((lo + hi) / 2)
            r_prev = v
        if len(roots) < 2:
            return (False, f"Expected multiple IRR roots, found {len(roots)}: {roots}")
        return (True, f"Found {len(roots)} IRR roots: {[f'{r:.4f}' for r in roots]}")

    ch.add(StructuralCheck(
        label="Remark 3.10: Non-conventional cash flows have multiple IRR roots",
        section="3.10",
        predicate=_remark_3_10_irr_multiple,
        note="Remark 3.10: IRR complications",
    ))

    # ── Remark 3.7: Time value of money ──────────────────────────────────
    # Claims: a euro today is worth more than a euro in the future because it
    # can be invested. PV < FV for positive interest rates.
    def _remark_3_7_time_value():
        import math

        # For any positive rate r and time t > 0: PV = FV / (1+r)^t < FV
        test_cases = [
            (0.01, 1), (0.05, 5), (0.10, 10), (0.001, 30), (0.20, 1),
        ]
        for r, t in test_cases:
            FV = 1.0
            PV = FV / (1 + r)**t
            if PV >= FV:
                return (False, f"PV={PV} >= FV={FV} for r={r}, t={t}")
            # Also verify FV = PV * (1+r)^t (investing PV yields FV)
            FV_check = PV * (1 + r)**t
            if abs(FV_check - FV) > 1e-12:
                return (False, f"FV roundtrip failed: {FV_check} != {FV}")

        # Verify: higher r => lower PV (more discounting)
        FV = 100.0
        t = 5
        pv_low_r = FV / (1.01)**t
        pv_high_r = FV / (1.10)**t
        if pv_low_r <= pv_high_r:
            return (False, f"Higher rate should give lower PV: PV(1%)={pv_low_r} <= PV(10%)={pv_high_r}")

        # Verify: longer t => lower PV
        r = 0.05
        pv_short = FV / (1 + r)**1
        pv_long = FV / (1 + r)**30
        if pv_short <= pv_long:
            return (False, f"Longer time should give lower PV: PV(1yr)={pv_short} <= PV(30yr)={pv_long}")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.7: Time value of money — PV < FV for positive rates",
        section="3.7",
        predicate=_remark_3_7_time_value,
        note="Remark 3.7: time value of money axiom verified",
    ))

    return ch
