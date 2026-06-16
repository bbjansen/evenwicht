<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Cosmology — API Reference

This is the API reference for the TypeScript implementation of Cosmology. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/cosmology/hubble.ts` — Hubble regression, Hubble time
- `src/cosmology/friedmann.ts` — Friedmann equation, luminosity distance, cosmic age
- `src/cosmology/cmb.ts` — Planck blackbody function, blackbody fitting
- `src/cosmology/rotation-curves.ts` — NFW halo model, rotation curve fitting

### Data Representation

Cosmological computations operate on scalar state variables (the scale factor $a$, the temperature $T$, mass fractions $X$, $Y$) and arrays of observational data (galaxy distances, velocities, spectral radiances). State vectors are represented as `Float64Array` for consistency with the ODE solver interface in `evenwicht/dynamics/ode`. Observational data arrays use standard JavaScript `number[]`.

### API Preview

```typescript
// src/cosmology/hubble.ts

/**
 * Hubble's law regression through the origin.
 *
 * @param distances - Galaxy distances in Mpc.
 * @param velocities - Recession velocities in km/s.
 * @returns { H0, standardError, residuals }.
 */
function hubbleRegression(
  distances: number[],
  velocities: number[],
): { H0: number; standardError: number; residuals: number[] };

/**
 * Hubble time (age estimate assuming constant expansion).
 *
 * @param H0 - Hubble constant in km/s/Mpc.
 * @returns Age in Gyr.
 */
function hubbleTime(H0: number): number;
```

```typescript
// src/cosmology/friedmann.ts

interface CosmologyParams {
  OmegaM: number;       // Matter density parameter
  OmegaR: number;       // Radiation density parameter
  OmegaLambda: number;  // Dark energy density parameter
  H0: number;           // Hubble constant in km/s/Mpc
}

/** Friedmann ODE right-hand side for use with RK4. */
function friedmannVectorField(
  params: CosmologyParams,
): (t: number, y: Float64Array) => Float64Array;

/** Integrate the Friedmann equation via RK4. */
function integrateFriedmann(
  params: CosmologyParams, aInit: number,
  tStart: number, tEnd: number, dt: number,
): { t: Float64Array; a: Float64Array };

/** Compute H(z) from cosmological parameters (km/s/Mpc). */
function hubbleParameter(params: CosmologyParams, z: number): number;

/** Compute luminosity distance via numerical quadrature (Mpc). */
function luminosityDistance(
  params: CosmologyParams, z: number, nSteps?: number,
): number;

/** Compute distance modulus from luminosity distance (magnitudes). */
function distanceModulus(dL: number): number;

/** Compute the age of the universe by numerical integration (Gyr). */
function cosmicAge(params: CosmologyParams, zMax?: number): number;
```

```typescript
// src/cosmology/cmb.ts

/** Planck blackbody spectral radiance (W sr^-1 m^-2 Hz^-1). */
function planckFunction(nu: number, T: number): number;

/** Fit Planck blackbody to observed spectral data. */
function fitBlackbody(
  frequencies: number[],
  radiances: number[],
): { T: number; chiSquared: number };
```

```typescript
// src/cosmology/rotation-curves.ts

/** NFW halo enclosed mass (solar masses). */
function nfwEnclosedMass(r: number, rhoS: number, rS: number): number;

/** Rotation curve for disk + NFW halo model (km/s). */
function rotationVelocity(
  r: number,
  diskMass: (r: number) => number,
  rhoS: number,
  rS: number,
): number;

/** Fit rotation curve data to disk + NFW halo model. */
function fitRotationCurve(
  radii: number[],
  velocities: number[],
  diskMass: (r: number) => number,
): { rhoS: number; rS: number; chiSquared: number };
```

### Error Handling

- `hubbleRegression` throws if fewer than 2 data points are provided or if all distances are zero.
- `integrateFriedmann` throws if $a_{\text{init}} \leq 0$ or if the density parameters produce a negative value under the square root (non-physical parameters).
- `luminosityDistance` throws if $z < 0$.
- `planckFunction` throws if $\nu \leq 0$ or $T \leq 0$.
- `fitBlackbody` throws if fewer than 3 data points are provided.
- `fitRotationCurve` throws if the optimisation fails to converge within the maximum number of iterations.

### Dependencies

- `src/dynamics/ode.ts` — RK4 for Friedmann equation integration
- `src/numeric/integral.ts` — numerical quadrature for luminosity distance
- `src/stats/regression.ts` — regression for Hubble constant and curve fitting
- `src/optimization/unconstrained.ts` — nonlinear fitting for blackbody and rotation curves

### Usage Examples

```typescript
import { hubbleTime, luminosityDistance, planckFunction, cosmicAge } from 'evenwicht/cosmology';

// Hubble time from H0 = 70 km/s/Mpc
hubbleTime(70);  // ≈ 14.0 Gyr

// Luminosity distance at z = 1 (standard LCDM)
const params = { OmegaM: 0.3, OmegaR: 0, OmegaLambda: 0.7, H0: 70 };
luminosityDistance(params, 1.0);  // ≈ 6700 Mpc

// Age of the universe
cosmicAge(params);  // ≈ 13.5 Gyr

// CMB blackbody at peak frequency
planckFunction(160.2e9, 2.725);  // spectral radiance at 160 GHz, T = 2.725 K
```

### Connections

This chapter synthesises Chapter 5 (numerical quadrature computes comoving and luminosity distances), Chapter 10 (eigenvalues of the baryon-photon oscillation equation determine CMB peak positions), Chapter 17 (linear regression gives $H_0$; nonlinear regression fits supernova and rotation curve data), Chapter 19 (RK4 integrates the Friedmann equation and nucleosynthesis rate equations) and Chapter 22 (Fourier analysis of the CMB spectrum). It extends Chapter 41 (Orbital Mechanics — Newtonian gravity at galactic and cosmological scales) and connects forward to general relativistic corrections and large-scale structure formation.

- **Integral Calculus** (Chapter 5): Luminosity distance $d_L(z)$ and cosmic age $t_0$ are definite integrals over the Hubble parameter, computed via Simpson's rule and adaptive quadrature.

- **Eigenvalues** (Chapter 10): CMB acoustic peak positions are eigenfrequencies of the baryon-photon oscillation equation. Stability of cosmological models under perturbations is determined by eigenvalues of the linearised equations.

- **Regression** (Chapter 17): Hubble's law is linear regression through the origin. Supernova cosmology, CMB blackbody fitting and rotation curve decomposition are nonlinear least-squares problems.

- **Ordinary Differential Equations** (Chapter 19): The Friedmann equation is a first-order ODE integrated by RK4. Nucleosynthesis rate equations are a coupled ODE system. Analytic solutions (matter, radiation dominated) serve as verification benchmarks.

- **Transforms** (Chapter 22): The CMB angular power spectrum $C_\ell$ is analogous to a Fourier power spectral density; spectral analysis techniques from Chapter 22 apply to $C_\ell$ extraction.

- **Orbital Mechanics** (Chapter 41): Galaxy rotation curves use the same $v_c = \sqrt{GM/r}$ as planetary orbits, but at galactic scales where the mass discrepancy reveals dark matter.



### What Is Implemented vs. Documented Only

- [x] Hubble's law regression (`hubbleRegression`, `hubbleTime`)
- [x] Friedmann equation integration (`integrateFriedmann`, `friedmannVectorField`)
- [x] Hubble parameter computation (`hubbleParameter`)
- [x] Luminosity distance (`luminosityDistance`, `distanceModulus`)
- [x] Cosmic age computation (`cosmicAge`)
- [x] Planck blackbody function and fitting (`planckFunction`, `fitBlackbody`)
- [x] NFW halo model (`nfwEnclosedMass`, `rotationVelocity`)
- [x] Rotation curve fitting (`fitRotationCurve`)
- [ ] Full CMB power spectrum computation (deferred — requires spherical harmonic framework)
- [ ] Boltzmann equation solver for anisotropy evolution (deferred — requires PDE framework)
- [ ] Bayesian cosmological parameter estimation (deferred — requires MCMC sampling framework)
- [ ] Gravitational lensing distance computation (deferred; requires general relativistic extensions)

---


### Implementation Context

**Friedmann equation singularity avoidance.** The Friedmann ODE diverges at $a = 0$ (the Big Bang). The integrator must start at a small positive $a_{\text{init}} \sim 10^{-8}$ using the analytic radiation-dominated solution $a \propto t^{1/2}$ for initialisation. The error introduced is $O(a_{\text{init}}^2)$, negligible for practical purposes. The function throws if $a_{\text{init}} \leq 0$ or if the density parameters produce a negative radicand.

**Luminosity distance via Simpson's rule.** The integrand $c/H(z)$ is smooth for $z > 0$, so composite Simpson's rule with $N = 1000$ provides at least 8 significant digits for $z \leq 10$. For $z \gtrsim 5$, the matter-to-radiation transition causes rapid variation, requiring $N \geq 2000$ or adaptive quadrature.

**Blackbody fitting sensitivity.** The Planck function is sensitive to temperature near the spectral peak: a 0.1% change in $T$ shifts peak radiance by ${\sim}0.4\%$, making the single-parameter fit well-conditioned. The initial guess uses Wien's displacement law ($T_0 = h\nu_{\text{peak}}/(2.82 k_B)$). Data points far from the peak (Rayleigh–Jeans and Wien tails) have lower signal-to-noise and should be down-weighted.

**Rotation curve disk-halo degeneracy.** The decomposition into visible disk mass and NFW dark matter halo is subject to a fundamental degeneracy: a heavier disk with a less concentrated halo can mimic a lighter disk with a more concentrated halo. The fitting function minimises $\chi^2$ via Levenberg–Marquardt from `evenwicht/optimization`, but external constraints (mass-to-light ratios) are needed to break the degeneracy.

**Nucleosynthesis stiffness.** Nucleosynthesis rate equations have reaction timescales (${\sim}$seconds) much shorter than the expansion timescale ($1/H \sim 100$ s), producing stiff ODE systems. RK4 requires very small step sizes ($h \leq 0.01$ s) for stability; implicit methods would be preferable but are not implemented.

**Testing strategy.** Hubble regression tests use synthetic datasets with known $H_0$. Friedmann integration is verified against analytic solutions for matter-dominated ($a \propto t^{2/3}$) and radiation-dominated ($a \propto t^{1/2}$) universes. Luminosity distance is checked against published values for standard $\Lambda$CDM parameters. Blackbody fitting is tested against the known CMB temperature $T = 2.725$ K.
