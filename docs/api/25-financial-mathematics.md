<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Financial Mathematics — API Reference

This is the API reference for the TypeScript implementation of Financial Mathematics. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

Source: `src/financial/`

- `src/financial/interest.ts` — Time value of money, NPV, IRR
- `src/financial/annuity.ts` — Annuities, perpetuities, amortisation

### Data Representation

All monetary values and rates are plain `number` types. Cash flow sequences are `number[]` arrays where `cashFlows[t]` represents the cash flow at time `t`. Amortisation schedules are returned as arrays of structured `AmortisationEntry` objects.

### API Preview

```typescript
// src/financial/interest.ts

function futureValue(principal: number, rate: number, periods: number, compoundingsPerYear?: number): number;
function futureValueContinuous(principal: number, rate: number, time: number): number;
function presentValue(futureVal: number, rate: number, periods: number): number;
function effectiveAnnualRate(nominalRate: number, compoundingsPerYear: number): number;

/** Net present value of a cash flow sequence. cashFlows[0] is at time 0. */
function npv(cashFlows: number[], rate: number): number;

/**
 * Internal rate of return via Newton's method.
 * @param cashFlows - Cash flow sequence (must have at least one sign change).
 * @param guess - Initial guess (default 0.10).
 * @returns Rate r* such that NPV(r*) = 0.
 */
function irr(cashFlows: number[], guess?: number, tolerance?: number, maxIterations?: number): number;

// src/financial/annuity.ts

function annuityPresentValue(payment: number, rate: number, periods: number): number;
function annuityFutureValue(payment: number, rate: number, periods: number): number;
function annuityDuePresentValue(payment: number, rate: number, periods: number): number;
function perpetuityPresentValue(payment: number, rate: number): number;
function growingPerpetuityPresentValue(payment: number, rate: number, growthRate: number): number;
function amortisationPayment(principal: number, rate: number, periods: number): number;

interface AmortisationEntry {
  period: number; payment: number; interest: number; principal: number; balance: number;
}
function amortisationSchedule(principal: number, rate: number, periods: number): AmortisationEntry[];
```

### Error Handling

- `irr` throws if Newton's method does not converge within `maxIterations` (default 100) or if the derivative becomes too small (flat NPV curve near the iterate).
- `perpetuityPresentValue` throws if the discount rate is non-positive.
- `growingPerpetuityPresentValue` throws if `rate <= growthRate` (the Gordon growth model diverges).
- `annuityPresentValue` and `annuityFutureValue` handle `rate === 0` as a special case (simple multiplication by the number of periods).
- `amortisationSchedule` computes the final balance analytically to avoid accumulated rounding drift across periods.

### Dependencies

- `src/numeric/bisect.ts` — bisection as fallback for IRR when Newton's method diverges
- No external module dependencies beyond standard math

### Usage Examples

```typescript
import { npv, irr, futureValue, annuityPresentValue, amortisationSchedule } from 'evenwicht/financial';

// NPV of a project: -1000 initial, then 400, 400, 400 at 10% discount
npv([-1000, 400, 400, 400], 0.10);  // ≈ -5.26 (marginal project)

// IRR of the same cash flows
irr([-1000, 400, 400, 400]);  // ≈ 0.0965 (9.65%)

// Future value of $1000 at 5% for 10 years
futureValue(1000, 0.05, 10);  // ≈ 1628.89

// Present value of 30-year mortgage payment
annuityPresentValue(1500, 0.005, 360);  // ≈ 250,187

// Amortisation schedule for $200,000 at 0.5%/month for 360 months
const schedule = amortisationSchedule(200000, 0.005, 360);
// schedule[0].interest ≈ 1000, schedule[0].principal ≈ 199.10
```

### Connections

This chapter uses Chapter 6 (geometric series for annuity valuation, the limit definition of $e$ for continuous compounding) and Chapter 4 (Newton's method for IRR computation). It connects to Chapter 12 (Optimisation; NPV maximisation under constraints) and Chapter 21 (Time Series; modelling financial data, yield curve estimation).

- **Series & Approximation** (Chapter 6): The annuity formulas are closed-form expressions for finite geometric series. The perpetuity formula is the infinite geometric series sum $a/(1-r)$ applied with $a = C\delta$ and $r = \delta = 1/(1+r)$. Continuous compounding relies on the limit $\lim(1+1/n)^n = e$, which is a special case of the exponential series.

- **Differential Calculus** (Chapter 4): Newton's method for IRR computation is a direct application of the Newton–Raphson iteration. The derivative of NPV with respect to the discount rate is the key quantity; it is also related to *duration* in fixed income mathematics, which measures the sensitivity of bond price to yield changes.

- **Constrained Optimisation** (Chapter 12): Capital budgeting under resource constraints (choosing which projects to fund to maximise total NPV subject to a budget constraint) is a constrained optimisation problem. The Lagrange multiplier on the budget constraint gives the shadow price of capital.

- **Time Series** (Chapter 21): Financial data (asset prices, interest rates, inflation) exhibit time-series structure: autocorrelation, volatility clustering and mean reversion. Fitting models to yield curves and forecasting future rates connects the static valuation formulas of this chapter to dynamic models.



### What Is Implemented vs. Documented Only

- [x] Future value under compound and continuous compounding
- [x] Present value of a single future cash flow
- [x] Effective annual rate conversion
- [x] Net present value (NPV) of a cash flow sequence
- [x] Internal rate of return (IRR) via Newton's method
- [x] Annuity present value and future value
- [x] Amortisation schedule generation
- [ ] Bond pricing and yield-to-maturity computation (documented in theory; deferred)
- [ ] Perpetuity valuation as a standalone function (documented as a limiting case; not separately exported)
- [ ] Option pricing (Black–Scholes) (out of scope for this chapter; referenced in connections only)
- [ ] Day-count conventions and settlement date handling (out of scope)

---


### Implementation Context

The algorithms above map to the Evenwicht library as follows.

**Source files**: `src/financial/interest.ts`, `src/financial/annuity.ts`.
