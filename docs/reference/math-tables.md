<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Mathematical Reference Tables

## Greek Alphabet

| Uppercase | Lowercase | Name |
|-----------|-----------|------|
| A | $\alpha$ | Alpha |
| B | $\beta$ | Beta |
| $\Gamma$ | $\gamma$ | Gamma |
| $\Delta$ | $\delta$ | Delta |
| E | $\epsilon$ | Epsilon |
| Z | $\zeta$ | Zeta |
| H | $\eta$ | Eta |
| $\Theta$ | $\theta$ | Theta |
| I | $\iota$ | Iota |
| K | $\kappa$ | Kappa |
| $\Lambda$ | $\lambda$ | Lambda |
| M | $\mu$ | Mu |
| N | $\nu$ | Nu |
| $\Xi$ | $\xi$ | Xi |
| O | $o$ | Omicron |
| $\Pi$ | $\pi$ | Pi |
| P | $\rho$ | Rho |
| $\Sigma$ | $\sigma$ | Sigma |
| T | $\tau$ | Tau |
| $\Upsilon$ | $\upsilon$ | Upsilon |
| $\Phi$ | $\phi$ | Phi |
| X | $\chi$ | Chi |
| $\Psi$ | $\psi$ | Psi |
| $\Omega$ | $\omega$ | Omega |

## Common Derivatives

| $f(x)$ | $f'(x)$ |
|--------|---------|
| $c$ | $0$ |
| $x^n$ | $nx^{n-1}$ |
| $e^x$ | $e^x$ |
| $a^x$ | $a^x \ln a$ |
| $\ln x$ | $\frac{1}{x}$ |
| $\log_a x$ | $\frac{1}{x \ln a}$ |
| $\sin x$ | $\cos x$ |
| $\cos x$ | $-\sin x$ |
| $\tan x$ | $\sec^2 x$ |
| $\arcsin x$ | $\frac{1}{\sqrt{1-x^2}}$ |
| $\arccos x$ | $\frac{-1}{\sqrt{1-x^2}}$ |
| $\arctan x$ | $\frac{1}{1+x^2}$ |
| $\sec x$ | $\sec x \tan x$ |
| $\csc x$ | $-\csc x \cot x$ |
| $\cot x$ | $-\csc^2 x$ |
| $\sinh x$ | $\cosh x$ |
| $\cosh x$ | $\sinh x$ |
| $\tanh x$ | $\operatorname{sech}^2 x$ |

**Differentiation Rules**

| Rule | Formula |
|------|---------|
| Chain rule | $\frac{d}{dx}f(g(x)) = f'(g(x)) \cdot g'(x)$ |
| Product rule | $(fg)' = f'g + fg'$ |
| Quotient rule | $\left(\frac{f}{g}\right)' = \frac{f'g - fg'}{g^2}$ |

## Common Integrals

| $f(x)$ | $\int f(x)\,dx$ |
|--------|-----------------|
| $x^n \; (n \neq -1)$ | $\frac{x^{n+1}}{n+1} + C$ |
| $\frac{1}{x}$ | $\ln|x| + C$ |
| $e^x$ | $e^x + C$ |
| $a^x$ | $\frac{a^x}{\ln a} + C$ |
| $\sin x$ | $-\cos x + C$ |
| $\cos x$ | $\sin x + C$ |
| $\tan x$ | $-\ln|\cos x| + C$ |
| $\sec x$ | $\ln|\sec x + \tan x| + C$ |
| $\csc x$ | $-\ln|\csc x + \cot x| + C$ |
| $\cot x$ | $\ln|\sin x| + C$ |
| $\sec^2 x$ | $\tan x + C$ |
| $\csc^2 x$ | $-\cot x + C$ |
| $\frac{1}{1+x^2}$ | $\arctan x + C$ |
| $\frac{1}{\sqrt{1-x^2}}$ | $\arcsin x + C$ |
| $\sinh x$ | $\cosh x + C$ |
| $\cosh x$ | $\sinh x + C$ |

## Taylor Series

| Function | Series Expansion | Convergence |
|----------|-----------------|-------------|
| $e^x$ | $\sum_{n=0}^{\infty} \frac{x^n}{n!}$ | $|x| < \infty$ |
| $\sin x$ | $\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!}$ | $|x| < \infty$ |
| $\cos x$ | $\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n}}{(2n)!}$ | $|x| < \infty$ |
| $\ln(1+x)$ | $\sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^n}{n}$ | $|x| \leq 1, \; x \neq -1$ |
| $\frac{1}{1-x}$ | $\sum_{n=0}^{\infty} x^n$ | $|x| < 1$ |
| $(1+x)^\alpha$ | $\sum_{n=0}^{\infty} \binom{\alpha}{n} x^n$ | $|x| < 1$ |
| $\tan x$ | $x + \frac{x^3}{3} + \frac{2x^5}{15} + \frac{17x^7}{315} + \cdots$ | $|x| < \frac{\pi}{2}$ |
| $\arctan x$ | $\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{2n+1}$ | $|x| \leq 1$ |
| $\sinh x$ | $\sum_{n=0}^{\infty} \frac{x^{2n+1}}{(2n+1)!}$ | $|x| < \infty$ |
| $\cosh x$ | $\sum_{n=0}^{\infty} \frac{x^{2n}}{(2n)!}$ | $|x| < \infty$ |

## Trigonometric Identities

### Pythagorean Identities

| Identity | Formula |
|----------|---------|
| Pythagorean (sin, cos) | $\sin^2\theta + \cos^2\theta = 1$ |
| Pythagorean (tan, sec) | $1 + \tan^2\theta = \sec^2\theta$ |
| Pythagorean (cot, csc) | $1 + \cot^2\theta = \csc^2\theta$ |

### Double Angle Formulas

| Identity | Formula |
|----------|---------|
| $\sin(2\theta)$ | $2\sin\theta\cos\theta$ |
| $\cos(2\theta)$ | $\cos^2\theta - \sin^2\theta$ |
| $\tan(2\theta)$ | $\frac{2\tan\theta}{1 - \tan^2\theta}$ |

### Half Angle Formulas

| Identity | Formula |
|----------|---------|
| $\sin\frac{\theta}{2}$ | $\pm\sqrt{\frac{1-\cos\theta}{2}}$ |
| $\cos\frac{\theta}{2}$ | $\pm\sqrt{\frac{1+\cos\theta}{2}}$ |

### Sum and Difference Formulas

| Identity | Formula |
|----------|---------|
| $\sin(\alpha+\beta)$ | $\sin\alpha\cos\beta + \cos\alpha\sin\beta$ |
| $\sin(\alpha-\beta)$ | $\sin\alpha\cos\beta - \cos\alpha\sin\beta$ |
| $\cos(\alpha+\beta)$ | $\cos\alpha\cos\beta - \sin\alpha\sin\beta$ |
| $\cos(\alpha-\beta)$ | $\cos\alpha\cos\beta + \sin\alpha\sin\beta$ |
| $\tan(\alpha+\beta)$ | $\frac{\tan\alpha + \tan\beta}{1 - \tan\alpha\tan\beta}$ |
| $\tan(\alpha-\beta)$ | $\frac{\tan\alpha - \tan\beta}{1 + \tan\alpha\tan\beta}$ |

### Product-to-Sum Formulas

| Identity | Formula |
|----------|---------|
| $\sin\alpha\cos\beta$ | $\frac{1}{2}[\sin(\alpha+\beta) + \sin(\alpha-\beta)]$ |
| $\cos\alpha\cos\beta$ | $\frac{1}{2}[\cos(\alpha-\beta) + \cos(\alpha+\beta)]$ |
| $\sin\alpha\sin\beta$ | $\frac{1}{2}[\cos(\alpha-\beta) - \cos(\alpha+\beta)]$ |

### Sum-to-Product Formulas

| Identity | Formula |
|----------|---------|
| $\sin\alpha + \sin\beta$ | $2\sin\frac{\alpha+\beta}{2}\cos\frac{\alpha-\beta}{2}$ |
| $\sin\alpha - \sin\beta$ | $2\cos\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}$ |
| $\cos\alpha + \cos\beta$ | $2\cos\frac{\alpha+\beta}{2}\cos\frac{\alpha-\beta}{2}$ |
| $\cos\alpha - \cos\beta$ | $-2\sin\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}$ |

## Laplace Transform Pairs

| $f(t)$ | $F(s) = \mathcal{L}\{f(t)\}$ | Condition |
|--------|-------------------------------|-----------|
| $1$ | $\frac{1}{s}$ | $s > 0$ |
| $t$ | $\frac{1}{s^2}$ | $s > 0$ |
| $t^n$ | $\frac{n!}{s^{n+1}}$ | $s > 0$ |
| $e^{at}$ | $\frac{1}{s-a}$ | $s > a$ |
| $t e^{at}$ | $\frac{1}{(s-a)^2}$ | $s > a$ |
| $t^n e^{at}$ | $\frac{n!}{(s-a)^{n+1}}$ | $s > a$ |
| $\sin(\omega t)$ | $\frac{\omega}{s^2+\omega^2}$ | $s > 0$ |
| $\cos(\omega t)$ | $\frac{s}{s^2+\omega^2}$ | $s > 0$ |
| $e^{at}\sin(\omega t)$ | $\frac{\omega}{(s-a)^2+\omega^2}$ | $s > a$ |
| $e^{at}\cos(\omega t)$ | $\frac{s-a}{(s-a)^2+\omega^2}$ | $s > a$ |
| $\delta(t)$ | $1$ | all $s$ |
| $u(t)$ | $\frac{1}{s}$ | $s > 0$ |
| $t^2$ | $\frac{2}{s^3}$ | $s > 0$ |
| $\sinh(at)$ | $\frac{a}{s^2-a^2}$ | $s > |a|$ |
| $\cosh(at)$ | $\frac{s}{s^2-a^2}$ | $s > |a|$ |
| $t\sin(\omega t)$ | $\frac{2\omega s}{(s^2+\omega^2)^2}$ | $s > 0$ |
| $t\cos(\omega t)$ | $\frac{s^2-\omega^2}{(s^2+\omega^2)^2}$ | $s > 0$ |
| $u(t-a)$ | $\frac{e^{-as}}{s}$ | $s > 0$ |

## Z-Transform Pairs

| $x[n]$ | $X(z)$ | ROC |
|--------|--------|-----|
| $\delta[n]$ | $1$ | all $z$ |
| $u[n]$ | $\frac{z}{z-1}$ | $|z| > 1$ |
| $n \cdot u[n]$ | $\frac{z}{(z-1)^2}$ | $|z| > 1$ |
| $a^n u[n]$ | $\frac{z}{z-a}$ | $|z| > |a|$ |
| $n a^n u[n]$ | $\frac{az}{(z-a)^2}$ | $|z| > |a|$ |
| $n^2 a^n u[n]$ | $\frac{az(z+a)}{(z-a)^3}$ | $|z| > |a|$ |
| $\sin(\omega n) u[n]$ | $\frac{z\sin\omega}{z^2-2z\cos\omega+1}$ | $|z| > 1$ |
| $\cos(\omega n) u[n]$ | $\frac{z(z-\cos\omega)}{z^2-2z\cos\omega+1}$ | $|z| > 1$ |
| $r^n\cos(\omega n) u[n]$ | $\frac{z(z-r\cos\omega)}{z^2-2rz\cos\omega+r^2}$ | $|z| > r$ |
| $r^n\sin(\omega n) u[n]$ | $\frac{zr\sin\omega}{z^2-2rz\cos\omega+r^2}$ | $|z| > r$ |
| $-a^n u[-n-1]$ | $\frac{z}{z-a}$ | $|z| < |a|$ |
| $n(n-1)a^{n-2} u[n]$ | $\frac{2z}{(z-a)^3}$ | $|z| > |a|$ |

## Physical Constants

| Constant | Symbol | Value |
|----------|--------|-------|
| Speed of light | $c$ | $2.998 \times 10^{8}$ m/s |
| Gravitational constant | $G$ | $6.674 \times 10^{-11}$ m$^3$ kg$^{-1}$ s$^{-2}$ |
| Planck constant | $h$ | $6.626 \times 10^{-34}$ J s |
| Reduced Planck constant | $\hbar$ | $1.055 \times 10^{-34}$ J s |
| Boltzmann constant | $k_B$ | $1.381 \times 10^{-23}$ J/K |
| Avogadro number | $N_A$ | $6.022 \times 10^{23}$ mol$^{-1}$ |
| Gas constant | $R$ | $8.314$ J mol$^{-1}$ K$^{-1}$ |
| Electron mass | $m_e$ | $9.109 \times 10^{-31}$ kg |
| Proton mass | $m_p$ | $1.673 \times 10^{-27}$ kg |
| Elementary charge | $e$ | $1.602 \times 10^{-19}$ C |
| Permittivity of free space | $\varepsilon_0$ | $8.854 \times 10^{-12}$ F/m |
| Permeability of free space | $\mu_0$ | $1.257 \times 10^{-6}$ H/m |
| Stefan–Boltzmann constant | $\sigma$ | $5.670 \times 10^{-8}$ W m$^{-2}$ K$^{-4}$ |
| Hubble constant | $H_0$ | $67.4$ km s$^{-1}$ Mpc$^{-1}$ |

## SI Unit Conversions

### Length

| Conversion | Factor | Notes |
|------------|--------|-------|
| 1 in | 2.54 cm | exact |
| 1 ft | 0.3048 m | exact |
| 1 yd | 0.9144 m | exact |
| 1 mi | 1.609 km | statute mile |
| 1 \AA | $10^{-10}$ m | angstrom |
| 1 nmi | 1.852 km | nautical mile, exact |
| 1 ly | $9.461 \times 10^{15}$ m | light-year |

### Mass

| Conversion | Factor | Notes |
|------------|--------|-------|
| 1 lb | 0.4536 kg | avoirdupois |
| 1 oz | 28.35 g | avoirdupois |
| 1 slug | 14.59 kg | |
| 1 tonne | 1000 kg | metric ton |
| 1 u | $1.661 \times 10^{-27}$ kg | atomic mass unit |

### Energy

| Conversion | Factor | Notes |
|------------|--------|-------|
| 1 eV | $1.602 \times 10^{-19}$ J | electron volt |
| 1 cal | 4.184 J | thermochemical calorie |
| 1 BTU | 1055 J | British thermal unit |
| 1 kWh | $3.6 \times 10^{6}$ J | kilowatt-hour |
| 1 erg | $10^{-7}$ J | CGS unit |

### Temperature

| Conversion | Factor | Notes |
|------------|--------|-------|
| F to C | $C = \frac{5}{9}(F - 32)$ | |
| C to K | $K = C + 273.15$ | |
| F to K | $K = \frac{5}{9}(F - 32) + 273.15$ | |

### Pressure

| Conversion | Factor | Notes |
|------------|--------|-------|
| 1 atm | 101325 Pa | exact |
| 1 bar | $10^{5}$ Pa | exact |
| 1 torr | 133.3 Pa | mmHg |
| 1 psi | 6895 Pa | pounds per square inch |
