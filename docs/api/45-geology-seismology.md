<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Geology & Seismology — API Reference

This is the API reference for the TypeScript implementation of Geology & Seismology. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/geology/seismic-waves.ts` — P-wave and S-wave velocities, layered travel times
- `src/geology/magnitude.ts` — moment magnitude conversion, seismic energy
- `src/geology/gutenberg-richter.ts` — b-value estimation, G-R law fitting
- `src/geology/dating.ts` — radiocarbon age, isochron dating
- `src/geology/plate-tectonics.ts` — Euler pole plate velocity computation

### Data Representation

Seismograms are stored as `Float64Array` with an associated sampling interval. Earthquake catalogs are arrays of magnitude values. Isotope ratios are scalar `number` values. Plate velocities use the three-component Cartesian vector representation from `evenwicht/linear/vector`. The FFT routines from `evenwicht/transforms/fft` operate on `Float64Array` input.

### API Preview

```typescript
// src/geology/seismic-waves.ts

/** Compute P-wave and S-wave velocities from elastic moduli and density. */
function waveVelocities(
  K: number, mu: number, rho: number,
): { vP: number; vS: number };

/** Compute first-arrival travel times for a horizontally layered Earth. */
function layeredTravelTimes(
  thicknesses: Float64Array, velocities: Float64Array, distances: Float64Array,
): Float64Array;
```

```typescript
// src/geology/magnitude.ts

function momentToMw(M0: number): number;        // seismic moment -> Mw
function mwToMoment(Mw: number): number;        // Mw -> seismic moment (N*m)
function seismicEnergy(Mw: number): number;      // Mw -> radiated energy (J)
```

```typescript
// src/geology/gutenberg-richter.ts

/** Estimate b-value via maximum likelihood (Thm. 45.10). */
function estimateBValue(
  magnitudes: Float64Array, Mc: number,
): { b: number; standardError: number; count: number };

/** Fit Gutenberg–Richter law via least-squares regression on binned data. */
function gutenbergRichterFit(
  magnitudes: Float64Array, Mc: number, binWidth?: number,
): { a: number; b: number; r2: number };
```

```typescript
// src/geology/dating.ts

/** Compute radiocarbon age from measured isotope ratio (default t_1/2 = 5730 yr). */
function radiocarbonAge(ratio: number, halfLife?: number): number;

/** Fit isochron line to parent/stable vs daughter/stable ratios; returns age. */
function isochronAge(
  parentStable: Float64Array, daughterStable: Float64Array, decayConstant: number,
): { age: number; initialRatio: number; slope: number; r2: number };
```

```typescript
// src/geology/plate-tectonics.ts

/** Compute plate velocity (mm/yr) at a surface point from Euler pole parameters. */
function plateVelocity(
  eulerLat: number, eulerLon: number, angularSpeed: number,
  pointLat: number, pointLon: number, radius?: number,
): { vx: number; vy: number; vz: number; speed: number };
```

### Error Handling

All functions validate physical constraints: `waveVelocities` requires $\rho > 0$; `radiocarbonAge` requires $0 < \text{ratio} \leq 1$; `estimateBValue` requires $\geq 2$ events above $M_c$; `isochronAge` requires $\geq 3$ matched data points; `plateVelocity` requires valid lat/lon ranges.

### Dependencies

- `src/linear/vector.ts` — cross product for Euler pole velocity computation
- `src/stats/regression.ts` — linear regression for Gutenberg–Richter, isochrons, travel time inversion
- `src/transforms/fft.ts` — FFT for seismogram spectral analysis
- `src/transforms/spectral.ts` — periodogram and windowing functions
- `src/dynamics/ode.ts` — ODE integration for radioactive decay (validation)
- `src/linear/solve.ts` — least-squares solution for tomographic inversion

### Usage Examples

```typescript
import { momentToMw, seismicEnergy, estimateBValue, radiocarbonAge } from 'evenwicht/geology';

// Moment magnitude from seismic moment (N*m)
momentToMw(1e20);  // ≈ 7.27

// Energy radiated by M7 earthquake
seismicEnergy(7.0);  // ≈ 2e15 Joules

// Radiocarbon age from isotope ratio
radiocarbonAge(0.5);  // ≈ 5730 years (one half-life)

// b-value estimation from earthquake catalog
const magnitudes = new Float64Array([3.1, 3.5, 4.0, 3.2, 5.1, 3.8, 4.2]);
const result = estimateBValue(magnitudes, 3.0);
// result.b ≈ 1.0, result.standardError, result.count
```

### Connections

This chapter synthesises Chapter 8 (cross products compute plate boundary velocities from Euler pole rotations), Chapter 17 (regression fits the Gutenberg–Richter law, isochron lines and travel time curves), Chapter 22 (FFT extracts frequency content from seismograms for source discrimination) and Chapter 32 (radioactive decay provides the ODE for radiometric dating). It connects to Chapter 39 (wave equation foundations), Chapter 40 (signal processing for seismogram filtering) and Chapter 38 (geothermal heat flow parallels climate diffusion models).

- **Vectors** (Chapter 8): The cross product $\boldsymbol{\omega} \times \mathbf{r}$ computes plate velocity from Euler pole angular velocity. Vector dot products compute angular distances on the sphere. The vector decomposition into normal and tangential components at plate boundaries determines the tectonic regime (convergent, divergent or transform).

- **Regression** (Chapter 17): Linear regression fits the Gutenberg–Richter law (log-linear), isochron lines (daughter/stable versus parent/stable), travel time curves (time versus distance for refracted arrivals) and the tomographic inverse problem (least squares). The $R^2$ statistic quantifies the quality of each fit.

- **Transforms** (Chapter 22): The FFT converts seismograms from the time domain to the frequency domain. The periodogram and power spectral density identify dominant frequencies, characterise source spectra and enable source discrimination (earthquake versus explosion). Windowing (Hann) reduces spectral leakage.

- **Energy Systems** (Chapter 32): Radioactive decay is the identical first-order ODE $dN/dt = -\lambda_d N$ encountered in nuclear decay chains. The half-life, exponential solution and age-determination formula transfer directly. The isochron method adds a regression layer on top of the decay equation.

- **Signal Processing** (Chapter 40): Bandpass filtering isolates P-wave and S-wave arrivals in seismograms. Convolution models the seismogram as a source time function convolved with a Green's function, and deconvolution recovers the source.



### What Is Implemented vs. Documented Only

- [x] P-wave and S-wave velocity computation (`waveVelocities`)
- [x] Layered travel time computation (`layeredTravelTimes`)
- [x] Moment magnitude conversions (`momentToMw`, `mwToMoment`, `seismicEnergy`)
- [x] $b$-value estimation (`estimateBValue`)
- [x] Gutenberg–Richter regression fit (`gutenbergRichterFit`)
- [x] Radiocarbon age calculation (`radiocarbonAge`)
- [x] Isochron dating (`isochronAge`)
- [x] Plate velocity from Euler pole (`plateVelocity`)
- [ ] Multi-layer refraction with dipping interfaces (documented — extend `layeredTravelTimes`)
- [ ] Tomographic inversion with regularisation (documented — uses `evenwicht/linear/solve`)
- [ ] Lithosphere cooling profile (documented; uses error function from `evenwicht/special`)

---


### Implementation Context

**Layered travel time computation.** Travel times are computed by Snell's law refraction through horizontal layers. For each distance, the function evaluates direct-wave and head-wave arrivals for all layers, returning the minimum. Complexity is $O(m \cdot n)$ for $m$ distances and $n$ layers. The critical angle computation $\arcsin(v_i/v_k)$ requires $v_i < v_k$; layers with velocity inversions produce no head wave on that interface.

**Maximum-likelihood b-value estimation.** The Aki-Utsu formula $\hat{b} = \log_{10} e / (\bar{M} - M_c)$ is preferred over least-squares regression because it is statistically efficient and avoids binning artefacts. The standard error $\sigma_b = \hat{b}/\sqrt{n'}$ assumes exponentially distributed magnitudes above $M_c$. Setting $M_c$ too low biases $\hat{b}$ downward by including incomplete magnitude ranges.

**Radiocarbon age from logarithm.** The age computation $t = \ln(r_0/r)/\lambda_d$ is a single logarithm evaluation ($O(1)$). The function requires $0 < r \leq 1$; values near zero yield very large ages where the precision of the isotope ratio measurement dominates uncertainty. Raw radiocarbon ages assume constant atmospheric $^{14}$C; calibration (IntCal20) is not applied.

**Euler pole velocity via cross product.** Plate velocity $\mathbf{v} = \boldsymbol{\omega} \times R\hat{\mathbf{r}}$ is computed by converting geographic coordinates to Cartesian unit vectors and evaluating the cross product. The velocity error is $\delta|\mathbf{v}| = R\sin\Delta \cdot \delta|\boldsymbol{\omega}|$, largest far from the Euler pole. Typical angular speed uncertainties of $\pm 0.02$ deg/Myr produce $\pm 1$–2 mm/yr velocity errors.

**Isochron regression.** `isochronAge` fits a line to parent/stable vs. daughter/stable ratios via linear regression, extracting the slope $m = e^{\lambda t} - 1$ and solving for age. The goodness-of-fit $R^2$ quantifies whether the samples are co-genetic; low $R^2$ signals open-system behaviour or analytical scatter.

**Testing strategy.** Magnitude tests verify $M_w = 7.0$ for $M_0 = 3.5 \times 10^{19}$ N$\cdot$m. Radiocarbon tests check that one half-life ($r = 0.5$) yields age $= 5730$ years. b-value tests use synthetic exponential catalogs with known $b = 1.0$. Travel time tests verify that the direct wave is fastest at short distances and head waves overtake at the crossover distance.
