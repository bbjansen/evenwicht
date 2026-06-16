<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Climate & Environmental Modelling — API Reference

This is the API reference for the TypeScript implementation of Climate & Environmental Modelling. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/climate/energy-balance.ts` — EBM equilibrium, relaxation, CO2 forcing, simulation
- `src/climate/carbon-cycle.ts` — three-box carbon cycle model, timescales
- `src/climate/trend-analysis.ts` — Mann-Kendall test, Sen slope
- `src/climate/spectral.ts` — climate power spectral density

### Data Representation

Climate state vectors are small (1 component for the EBM, 3 for the carbon cycle), represented as `Float64Array` for compatibility with the ODE solvers in `evenwicht/ode`. Time series are represented as `Float64Array` with an associated sampling interval. Spectral analysis uses the FFT routines from `evenwicht/transforms`.

### API Preview

```typescript
// src/climate/energy-balance.ts

interface EnergyBalanceParams {
  solarConstant: number;   // W m^-2
  albedo: number;          // dimensionless, 0 to 1
  emissivity: number;      // dimensionless, 0 to 1
  heatCapacity: number;    // J m^-2 K^-1
}

function equilibriumTemperature(params: EnergyBalanceParams): number;

function relaxationTimescale(params: EnergyBalanceParams): number;

function co2Forcing(co2Ratio: number): number;

function ebmVectorField(
  params: EnergyBalanceParams,
  forcing?: (t: number) => number,
): (t: number, y: Float64Array) => Float64Array;

function simulateEBM(
  params: EnergyBalanceParams,
  T0: number,
  tEnd: number,
  dt: number,
  forcing?: (t: number) => number,
): { t: Float64Array; T: Float64Array };
```

```typescript
// src/climate/carbon-cycle.ts

interface CarbonCycleParams {
  kAO: number;  // atmosphere-to-ocean (yr^-1)
  kOA: number;  // ocean-to-atmosphere (yr^-1)
  kAL: number;  // atmosphere-to-land (yr^-1)
  kLA: number;  // land-to-atmosphere (yr^-1)
}

function carbonCycleMatrix(params: CarbonCycleParams): Float64Array[];

function carbonCycleTimescales(
  params: CarbonCycleParams,
): { eigenvalues: number[]; timescales: number[] };

function simulateCarbonCycle(
  params: CarbonCycleParams,
  C0: [number, number, number],
  emissions: (t: number) => number,
  tEnd: number,
  dt: number,
): { t: Float64Array; Ca: Float64Array; Co: Float64Array; Cl: Float64Array };
```

```typescript
// src/climate/trend-analysis.ts

function mannKendallTest(
  series: Float64Array,
): { S: number; variance: number; Z: number; pValue: number };

function senSlope(series: Float64Array): number;
```

```typescript
// src/climate/spectral.ts

function climatePSD(
  series: Float64Array,
  dt: number,
  window?: boolean,
): { frequencies: Float64Array; psd: Float64Array };
```

### Error Handling

- `equilibriumTemperature` throws if albedo is outside $[0, 1]$ or emissivity is non-positive.
- `simulateEBM` throws if `tEnd <= 0` or `dt <= 0`.
- `mannKendallTest` throws if the series has fewer than 3 observations.
- `senSlope` throws if the series has fewer than 3 observations.
- `carbonCycleTimescales` returns eigenvalues and the corresponding physical timescales ($1/|\lambda|$).

### Dependencies

- `src/dynamics/ode.ts` — RK4 integration of EBM and carbon cycle ODEs
- `src/linear/eigen.ts` — eigenvalue computation of the carbon cycle matrix
- `src/stats/regression.ts` — linear trend fitting and confidence intervals
- `src/transforms/fft.ts` — FFT-based spectral analysis

### Usage Examples

```typescript
import { equilibriumTemperature, simulateEBM, co2Forcing, mannKendallTest } from 'evenwicht/climate';

// Earth's equilibrium temperature
const T = equilibriumTemperature({
  solarConstant: 1361, albedo: 0.3, emissivity: 0.612, heatCapacity: 5e8,
});  // ≈ 288 K (15 C)

// CO2 radiative forcing: doubling from pre-industrial
co2Forcing(2.0);  // ≈ 3.7 W/m^2

// Simulate EBM with step forcing
const sim = simulateEBM(
  { solarConstant: 1361, albedo: 0.3, emissivity: 0.612, heatCapacity: 5e8 },
  288, 100, 0.1,
  (t) => t > 10 ? 3.7 : 0,  // CO2 doubling at t=10
);

// Trend detection in temperature record
const temp = new Float64Array([14.0, 14.1, 14.2, 14.1, 14.3, 14.4, 14.5]);
const mk = mannKendallTest(temp);
// mk.pValue: significance of warming trend
```

### Connections

This chapter synthesises Chapter 10 (eigenvalues of the carbon cycle system determine $\text{CO}_2$ residence times; linearised stability analysis determines climate relaxation), Chapter 17 (regression detects trends in temperature and $\text{CO}_2$ records), Chapter 19 (energy balance and carbon cycle are ODE systems integrated via RK4), Chapter 21 (seasonal decomposition and autocorrelation characterise climate variability) and Chapter 22 (FFT-based spectral analysis identifies oscillation periods). It connects to Chapter 32 (energy balance parallels nuclear decay energetics), Chapter 29 (climate policy as a control problem) and Chapter 30 (carbon cycle compartments parallel epidemiological compartments).

- **Eigenvalues** (Chapter 10): Carbon cycle eigenvalues determine $\text{CO}_2$ residence times; the Gershgorin theorem guarantees stability of compartmental matrices; linearised EBM stability reduces to the sign of $-1/\tau$.

- **Regression** (Chapter 17): Linear and polynomial regression detect trends in $\text{CO}_2$ and temperature records; confidence intervals quantify uncertainty in observed warming rates.

- **Ordinary Differential Equations** (Chapter 19): The EBM and carbon cycle are first-order ODEs and linear ODE systems. Equilibrium analysis, linearisation and RK4 integration apply directly. Ice-albedo feedback introduces bifurcations.

- **Time Series** (Chapter 21): Climate records exhibit trend, seasonality and autocorrelation. The Mann–Kendall test provides nonparametric trend detection. Autocorrelation structure affects all estimator variances.

- **Transforms** (Chapter 22): DFT-based PSD identifies periodic oscillations (ENSO, AMO). Windowing reduces spectral leakage. The Wiener–Khinchin theorem connects PSD to the autocorrelation function.



### What Is Implemented vs. Documented Only

- [x] Energy balance model: equilibrium temperature, relaxation timescale, CO2 forcing
- [x] EBM vector field and time integration via ODE solver
- [x] Three-box carbon cycle model (atmosphere, ocean, land) with matrix formulation
- [x] Carbon cycle eigenvalue-based timescale analysis
- [x] Carbon cycle simulation with time-dependent emissions
- [x] Mann–Kendall trend test and Sen's slope estimator
- [x] Climate power spectral density estimation via FFT
- [ ] General circulation model (GCM) components (out of scope; the chapter covers reduced-complexity models only)
- [ ] Coupled ocean-atmosphere dynamics (out of scope)
- [ ] Ice-albedo feedback as a dynamic model component (documented conceptually; not implemented as a separate module)
- [ ] Stochastic climate variability and Monte Carlo ensembles (deferred)

---


### Implementation Context

**EBM as a scalar ODE.** The energy balance model integrates a single scalar ODE via RK4. The nonlinear $\sigma T^4$ term requires step sizes of roughly $h \leq 0.04$ years (two weeks) for four-digit accuracy near the equilibrium temperature of 288 K. Ice-albedo feedback, if modelled as a discontinuous $\alpha(T)$, demands smaller steps near the albedo transition.

**Carbon cycle eigenvalue analysis.** The $3 \times 3$ compartmental matrix has one zero eigenvalue (conservation of total carbon) and two negative real eigenvalues whose reciprocals give the adjustment timescales (${\sim}7$ years and ${\sim}300$ years). This moderate stiffness ratio (${\sim}40{:}1$) is manageable with RK4 using $h \leq 0.7$ years, dictated by the fast timescale.

**Mann–Kendall variance correction.** The standard variance formula $n(n-1)(2n+5)/18$ assumes serial independence. Climate time series exhibit positive autocorrelation, which inflates the true variance of $S$. Without an autocorrelation correction (Hamed–Rao), the test produces spuriously significant trend detections. The implementation uses the uncorrected formula; users analysing autocorrelated records should apply external corrections.

**Spectral analysis with windowing.** The climate PSD function optionally applies a Hann window before FFT to reduce spectral leakage from finite record lengths. Without windowing, sharp spectral peaks (e.g., ENSO at ${\sim}0.2$ cycles/year) broaden into adjacent frequency bins. The Hann window reduces leakage at the cost of halving the amplitude and slightly broadening true peaks.

**Equilibrium sensitivity to parameters.** The fourth-root dependence $T^* \propto (S(1-\alpha)/\varepsilon)^{1/4}$ means parameter uncertainties propagate weakly to temperature (1% in $S$ yields ${\sim}0.25\%$ in $T^*$), but climate sensitivity $\lambda$ depends on $T^{*3}$, amplifying uncertainty for policy-relevant quantities.

**Testing strategy.** EBM tests verify the analytical equilibrium temperature against the Stefan–Boltzmann formula. Carbon cycle tests check eigenvalue signs (one zero, two negative) and conservation of total carbon. Mann–Kendall tests use synthetic monotonic and random series with known trend presence or absence.
