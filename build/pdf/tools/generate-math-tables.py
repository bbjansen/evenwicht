#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Generate mathematical reference tables for the appendix.

Produces markdown tables for:
  - Greek Alphabet
  - Common Derivatives
  - Common Integrals
  - Taylor Series
  - Trigonometric Identities
  - Laplace Transform Pairs
  - Z-Transform Pairs
  - Physical Constants
  - SI Unit Conversions

Output: dist/math-tables.md
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_FILE = PROJECT_ROOT / "dist" / "math-tables.md"


def greek_alphabet():
    """All 24 Greek letters with uppercase, lowercase, and name."""
    lines = [
        "## Greek Alphabet",
        "",
        "| Uppercase | Lowercase | Name |",
        "|-----------|-----------|------|",
    ]
    letters = [
        ("A",           r"$\alpha$",    "Alpha"),
        ("B",           r"$\beta$",     "Beta"),
        (r"$\Gamma$",   r"$\gamma$",    "Gamma"),
        (r"$\Delta$",   r"$\delta$",    "Delta"),
        ("E",           r"$\epsilon$",  "Epsilon"),
        ("Z",           r"$\zeta$",     "Zeta"),
        ("H",           r"$\eta$",      "Eta"),
        (r"$\Theta$",   r"$\theta$",    "Theta"),
        ("I",           r"$\iota$",     "Iota"),
        ("K",           r"$\kappa$",    "Kappa"),
        (r"$\Lambda$",  r"$\lambda$",   "Lambda"),
        ("M",           r"$\mu$",       "Mu"),
        ("N",           r"$\nu$",       "Nu"),
        (r"$\Xi$",      r"$\xi$",       "Xi"),
        ("O",           r"$o$",         "Omicron"),
        (r"$\Pi$",      r"$\pi$",       "Pi"),
        ("P",           r"$\rho$",      "Rho"),
        (r"$\Sigma$",   r"$\sigma$",    "Sigma"),
        ("T",           r"$\tau$",      "Tau"),
        (r"$\Upsilon$", r"$\upsilon$",  "Upsilon"),
        (r"$\Phi$",     r"$\phi$",      "Phi"),
        ("X",           r"$\chi$",      "Chi"),
        (r"$\Psi$",     r"$\psi$",      "Psi"),
        (r"$\Omega$",   r"$\omega$",    "Omega"),
    ]
    for upper, lower, name in letters:
        lines.append(f"| {upper} | {lower} | {name} |")
    lines.append("")
    return lines


def common_derivatives():
    """Standard derivatives reference table."""
    lines = [
        "## Common Derivatives",
        "",
        "| $f(x)$ | $f'(x)$ |",
        "|--------|---------|",
    ]
    pairs = [
        (r"$c$",                          r"$0$"),
        (r"$x^n$",                        r"$nx^{n-1}$"),
        (r"$e^x$",                        r"$e^x$"),
        (r"$a^x$",                        r"$a^x \ln a$"),
        (r"$\ln x$",                      r"$\frac{1}{x}$"),
        (r"$\log_a x$",                   r"$\frac{1}{x \ln a}$"),
        (r"$\sin x$",                     r"$\cos x$"),
        (r"$\cos x$",                     r"$-\sin x$"),
        (r"$\tan x$",                     r"$\sec^2 x$"),
        (r"$\arcsin x$",                  r"$\frac{1}{\sqrt{1-x^2}}$"),
        (r"$\arccos x$",                  r"$\frac{-1}{\sqrt{1-x^2}}$"),
        (r"$\arctan x$",                  r"$\frac{1}{1+x^2}$"),
        (r"$\sec x$",                     r"$\sec x \tan x$"),
        (r"$\csc x$",                     r"$-\csc x \cot x$"),
        (r"$\cot x$",                     r"$-\csc^2 x$"),
        (r"$\sinh x$",                    r"$\cosh x$"),
        (r"$\cosh x$",                    r"$\sinh x$"),
        (r"$\tanh x$",                    r"$\operatorname{sech}^2 x$"),
    ]
    for f, fp in pairs:
        lines.append(f"| {f} | {fp} |")

    lines.append("")
    lines.append("**Differentiation Rules**")
    lines.append("")
    lines.append("| Rule | Formula |")
    lines.append("|------|---------|")
    rules = [
        ("Chain rule",    r"$\frac{d}{dx}f(g(x)) = f'(g(x)) \cdot g'(x)$"),
        ("Product rule",  r"$(fg)' = f'g + fg'$"),
        ("Quotient rule", r"$\left(\frac{f}{g}\right)' = \frac{f'g - fg'}{g^2}$"),
    ]
    for name, formula in rules:
        lines.append(f"| {name} | {formula} |")
    lines.append("")
    return lines


def common_integrals():
    """Standard integrals reference table."""
    lines = [
        "## Common Integrals",
        "",
        "| $f(x)$ | $\\int f(x)\\,dx$ |",
        "|--------|-----------------|",
    ]
    pairs = [
        (r"$x^n \; (n \neq -1)$",             r"$\frac{x^{n+1}}{n+1} + C$"),
        (r"$\frac{1}{x}$",                    r"$\ln|x| + C$"),
        (r"$e^x$",                             r"$e^x + C$"),
        (r"$a^x$",                             r"$\frac{a^x}{\ln a} + C$"),
        (r"$\sin x$",                          r"$-\cos x + C$"),
        (r"$\cos x$",                          r"$\sin x + C$"),
        (r"$\tan x$",                          r"$-\ln|\cos x| + C$"),
        (r"$\sec x$",                          r"$\ln|\sec x + \tan x| + C$"),
        (r"$\csc x$",                          r"$-\ln|\csc x + \cot x| + C$"),
        (r"$\cot x$",                          r"$\ln|\sin x| + C$"),
        (r"$\sec^2 x$",                        r"$\tan x + C$"),
        (r"$\csc^2 x$",                        r"$-\cot x + C$"),
        (r"$\frac{1}{1+x^2}$",                r"$\arctan x + C$"),
        (r"$\frac{1}{\sqrt{1-x^2}}$",         r"$\arcsin x + C$"),
        (r"$\sinh x$",                         r"$\cosh x + C$"),
        (r"$\cosh x$",                         r"$\sinh x + C$"),
    ]
    for f, intf in pairs:
        lines.append(f"| {f} | {intf} |")
    lines.append("")
    return lines


def taylor_series():
    """Taylor series expansions with convergence radii."""
    lines = [
        "## Taylor Series",
        "",
        "| Function | Series Expansion | Convergence |",
        "|----------|-----------------|-------------|",
    ]
    series = [
        (r"$e^x$",
         r"$\sum_{n=0}^{\infty} \frac{x^n}{n!}$",
         r"$|x| < \infty$"),
        (r"$\sin x$",
         r"$\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!}$",
         r"$|x| < \infty$"),
        (r"$\cos x$",
         r"$\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n}}{(2n)!}$",
         r"$|x| < \infty$"),
        (r"$\ln(1+x)$",
         r"$\sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^n}{n}$",
         r"$|x| \leq 1, \; x \neq -1$"),
        (r"$\frac{1}{1-x}$",
         r"$\sum_{n=0}^{\infty} x^n$",
         r"$|x| < 1$"),
        (r"$(1+x)^\alpha$",
         r"$\sum_{n=0}^{\infty} \binom{\alpha}{n} x^n$",
         r"$|x| < 1$"),
        (r"$\tan x$",
         r"$x + \frac{x^3}{3} + \frac{2x^5}{15} + \frac{17x^7}{315} + \cdots$",
         r"$|x| < \frac{\pi}{2}$"),
        (r"$\arctan x$",
         r"$\sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{2n+1}$",
         r"$|x| \leq 1$"),
        (r"$\sinh x$",
         r"$\sum_{n=0}^{\infty} \frac{x^{2n+1}}{(2n+1)!}$",
         r"$|x| < \infty$"),
        (r"$\cosh x$",
         r"$\sum_{n=0}^{\infty} \frac{x^{2n}}{(2n)!}$",
         r"$|x| < \infty$"),
    ]
    for func, expansion, conv in series:
        lines.append(f"| {func} | {expansion} | {conv} |")
    lines.append("")
    return lines


def trig_identities():
    """Trigonometric identities organized by category."""
    lines = [
        "## Trigonometric Identities",
        "",
        "### Pythagorean Identities",
        "",
        "| Identity | Formula |",
        "|----------|---------|",
        r"| Pythagorean (sin, cos) | $\sin^2\theta + \cos^2\theta = 1$ |",
        r"| Pythagorean (tan, sec) | $1 + \tan^2\theta = \sec^2\theta$ |",
        r"| Pythagorean (cot, csc) | $1 + \cot^2\theta = \csc^2\theta$ |",
        "",
        "### Double Angle Formulas",
        "",
        "| Identity | Formula |",
        "|----------|---------|",
        r"| $\sin(2\theta)$ | $2\sin\theta\cos\theta$ |",
        r"| $\cos(2\theta)$ | $\cos^2\theta - \sin^2\theta$ |",
        r"| $\tan(2\theta)$ | $\frac{2\tan\theta}{1 - \tan^2\theta}$ |",
        "",
        "### Half Angle Formulas",
        "",
        "| Identity | Formula |",
        "|----------|---------|",
        r"| $\sin\frac{\theta}{2}$ | $\pm\sqrt{\frac{1-\cos\theta}{2}}$ |",
        r"| $\cos\frac{\theta}{2}$ | $\pm\sqrt{\frac{1+\cos\theta}{2}}$ |",
        "",
        "### Sum and Difference Formulas",
        "",
        "| Identity | Formula |",
        "|----------|---------|",
        r"| $\sin(\alpha+\beta)$ | $\sin\alpha\cos\beta + \cos\alpha\sin\beta$ |",
        r"| $\sin(\alpha-\beta)$ | $\sin\alpha\cos\beta - \cos\alpha\sin\beta$ |",
        r"| $\cos(\alpha+\beta)$ | $\cos\alpha\cos\beta - \sin\alpha\sin\beta$ |",
        r"| $\cos(\alpha-\beta)$ | $\cos\alpha\cos\beta + \sin\alpha\sin\beta$ |",
        r"| $\tan(\alpha+\beta)$ | $\frac{\tan\alpha + \tan\beta}{1 - \tan\alpha\tan\beta}$ |",
        r"| $\tan(\alpha-\beta)$ | $\frac{\tan\alpha - \tan\beta}{1 + \tan\alpha\tan\beta}$ |",
        "",
        "### Product-to-Sum Formulas",
        "",
        "| Identity | Formula |",
        "|----------|---------|",
        r"| $\sin\alpha\cos\beta$ | $\frac{1}{2}[\sin(\alpha+\beta) + \sin(\alpha-\beta)]$ |",
        r"| $\cos\alpha\cos\beta$ | $\frac{1}{2}[\cos(\alpha-\beta) + \cos(\alpha+\beta)]$ |",
        r"| $\sin\alpha\sin\beta$ | $\frac{1}{2}[\cos(\alpha-\beta) - \cos(\alpha+\beta)]$ |",
        "",
        "### Sum-to-Product Formulas",
        "",
        "| Identity | Formula |",
        "|----------|---------|",
        r"| $\sin\alpha + \sin\beta$ | $2\sin\frac{\alpha+\beta}{2}\cos\frac{\alpha-\beta}{2}$ |",
        r"| $\sin\alpha - \sin\beta$ | $2\cos\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}$ |",
        r"| $\cos\alpha + \cos\beta$ | $2\cos\frac{\alpha+\beta}{2}\cos\frac{\alpha-\beta}{2}$ |",
        r"| $\cos\alpha - \cos\beta$ | $-2\sin\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}$ |",
        "",
    ]
    return lines


def laplace_transforms():
    """Laplace transform pairs table."""
    lines = [
        "## Laplace Transform Pairs",
        "",
        "| $f(t)$ | $F(s) = \\mathcal{L}\\{f(t)\\}$ | Condition |",
        "|--------|-------------------------------|-----------|",
    ]
    pairs = [
        (r"$1$",
         r"$\frac{1}{s}$",
         r"$s > 0$"),
        (r"$t$",
         r"$\frac{1}{s^2}$",
         r"$s > 0$"),
        (r"$t^n$",
         r"$\frac{n!}{s^{n+1}}$",
         r"$s > 0$"),
        (r"$e^{at}$",
         r"$\frac{1}{s-a}$",
         r"$s > a$"),
        (r"$t e^{at}$",
         r"$\frac{1}{(s-a)^2}$",
         r"$s > a$"),
        (r"$t^n e^{at}$",
         r"$\frac{n!}{(s-a)^{n+1}}$",
         r"$s > a$"),
        (r"$\sin(\omega t)$",
         r"$\frac{\omega}{s^2+\omega^2}$",
         r"$s > 0$"),
        (r"$\cos(\omega t)$",
         r"$\frac{s}{s^2+\omega^2}$",
         r"$s > 0$"),
        (r"$e^{at}\sin(\omega t)$",
         r"$\frac{\omega}{(s-a)^2+\omega^2}$",
         r"$s > a$"),
        (r"$e^{at}\cos(\omega t)$",
         r"$\frac{s-a}{(s-a)^2+\omega^2}$",
         r"$s > a$"),
        (r"$\delta(t)$",
         r"$1$",
         r"all $s$"),
        (r"$u(t)$",
         r"$\frac{1}{s}$",
         r"$s > 0$"),
        (r"$t^2$",
         r"$\frac{2}{s^3}$",
         r"$s > 0$"),
        (r"$\sinh(at)$",
         r"$\frac{a}{s^2-a^2}$",
         r"$s > |a|$"),
        (r"$\cosh(at)$",
         r"$\frac{s}{s^2-a^2}$",
         r"$s > |a|$"),
        (r"$t\sin(\omega t)$",
         r"$\frac{2\omega s}{(s^2+\omega^2)^2}$",
         r"$s > 0$"),
        (r"$t\cos(\omega t)$",
         r"$\frac{s^2-\omega^2}{(s^2+\omega^2)^2}$",
         r"$s > 0$"),
        (r"$u(t-a)$",
         r"$\frac{e^{-as}}{s}$",
         r"$s > 0$"),
    ]
    for ft, fs, cond in pairs:
        lines.append(f"| {ft} | {fs} | {cond} |")
    lines.append("")
    return lines


def z_transforms():
    """Z-transform pairs table."""
    lines = [
        "## Z-Transform Pairs",
        "",
        "| $x[n]$ | $X(z)$ | ROC |",
        "|--------|--------|-----|",
    ]
    pairs = [
        (r"$\delta[n]$",
         r"$1$",
         r"all $z$"),
        (r"$u[n]$",
         r"$\frac{z}{z-1}$",
         r"$|z| > 1$"),
        (r"$n \cdot u[n]$",
         r"$\frac{z}{(z-1)^2}$",
         r"$|z| > 1$"),
        (r"$a^n u[n]$",
         r"$\frac{z}{z-a}$",
         r"$|z| > |a|$"),
        (r"$n a^n u[n]$",
         r"$\frac{az}{(z-a)^2}$",
         r"$|z| > |a|$"),
        (r"$n^2 a^n u[n]$",
         r"$\frac{az(z+a)}{(z-a)^3}$",
         r"$|z| > |a|$"),
        (r"$\sin(\omega n) u[n]$",
         r"$\frac{z\sin\omega}{z^2-2z\cos\omega+1}$",
         r"$|z| > 1$"),
        (r"$\cos(\omega n) u[n]$",
         r"$\frac{z(z-\cos\omega)}{z^2-2z\cos\omega+1}$",
         r"$|z| > 1$"),
        (r"$r^n\cos(\omega n) u[n]$",
         r"$\frac{z(z-r\cos\omega)}{z^2-2rz\cos\omega+r^2}$",
         r"$|z| > r$"),
        (r"$r^n\sin(\omega n) u[n]$",
         r"$\frac{zr\sin\omega}{z^2-2rz\cos\omega+r^2}$",
         r"$|z| > r$"),
        (r"$-a^n u[-n-1]$",
         r"$\frac{z}{z-a}$",
         r"$|z| < |a|$"),
        (r"$n(n-1)a^{n-2} u[n]$",
         r"$\frac{2z}{(z-a)^3}$",
         r"$|z| > |a|$"),
    ]
    for xn, xz, roc in pairs:
        lines.append(f"| {xn} | {xz} | {roc} |")
    lines.append("")
    return lines


def physical_constants():
    """Fundamental physical constants table."""
    lines = [
        "## Physical Constants",
        "",
        "| Constant | Symbol | Value |",
        "|----------|--------|-------|",
    ]
    constants = [
        ("Speed of light",
         r"$c$",
         r"$2.998 \times 10^{8}$ m/s"),
        ("Gravitational constant",
         r"$G$",
         r"$6.674 \times 10^{-11}$ m$^3$ kg$^{-1}$ s$^{-2}$"),
        ("Planck constant",
         r"$h$",
         r"$6.626 \times 10^{-34}$ J s"),
        ("Reduced Planck constant",
         r"$\hbar$",
         r"$1.055 \times 10^{-34}$ J s"),
        ("Boltzmann constant",
         r"$k_B$",
         r"$1.381 \times 10^{-23}$ J/K"),
        ("Avogadro number",
         r"$N_A$",
         r"$6.022 \times 10^{23}$ mol$^{-1}$"),
        ("Gas constant",
         r"$R$",
         r"$8.314$ J mol$^{-1}$ K$^{-1}$"),
        ("Electron mass",
         r"$m_e$",
         r"$9.109 \times 10^{-31}$ kg"),
        ("Proton mass",
         r"$m_p$",
         r"$1.673 \times 10^{-27}$ kg"),
        ("Elementary charge",
         r"$e$",
         r"$1.602 \times 10^{-19}$ C"),
        ("Permittivity of free space",
         r"$\varepsilon_0$",
         r"$8.854 \times 10^{-12}$ F/m"),
        ("Permeability of free space",
         r"$\mu_0$",
         r"$1.257 \times 10^{-6}$ H/m"),
        ("Stefan-Boltzmann constant",
         r"$\sigma$",
         r"$5.670 \times 10^{-8}$ W m$^{-2}$ K$^{-4}$"),
        ("Hubble constant",
         r"$H_0$",
         r"$67.4$ km s$^{-1}$ Mpc$^{-1}$"),
    ]
    for name, symbol, value in constants:
        lines.append(f"| {name} | {symbol} | {value} |")
    lines.append("")
    return lines


def si_conversions():
    """SI unit conversions organized by category."""
    lines = [
        "## SI Unit Conversions",
        "",
        "### Length",
        "",
        "| Conversion | Factor | Notes |",
        "|------------|--------|-------|",
        "| 1 in | 2.54 cm | exact |",
        "| 1 ft | 0.3048 m | exact |",
        "| 1 yd | 0.9144 m | exact |",
        "| 1 mi | 1.609 km | statute mile |",
        r"| 1 \AA | $10^{-10}$ m | angstrom |",
        "| 1 nmi | 1.852 km | nautical mile, exact |",
        "| 1 ly | $9.461 \\times 10^{15}$ m | light-year |",
        "",
        "### Mass",
        "",
        "| Conversion | Factor | Notes |",
        "|------------|--------|-------|",
        "| 1 lb | 0.4536 kg | avoirdupois |",
        "| 1 oz | 28.35 g | avoirdupois |",
        "| 1 slug | 14.59 kg | |",
        "| 1 tonne | 1000 kg | metric ton |",
        "| 1 u | $1.661 \\times 10^{-27}$ kg | atomic mass unit |",
        "",
        "### Energy",
        "",
        "| Conversion | Factor | Notes |",
        "|------------|--------|-------|",
        "| 1 eV | $1.602 \\times 10^{-19}$ J | electron volt |",
        "| 1 cal | 4.184 J | thermochemical calorie |",
        "| 1 BTU | 1055 J | British thermal unit |",
        "| 1 kWh | $3.6 \\times 10^{6}$ J | kilowatt-hour |",
        "| 1 erg | $10^{-7}$ J | CGS unit |",
        "",
        "### Temperature",
        "",
        "| Conversion | Factor | Notes |",
        "|------------|--------|-------|",
        r"| F to C | $C = \frac{5}{9}(F - 32)$ | |",
        r"| C to K | $K = C + 273.15$ | |",
        r"| F to K | $K = \frac{5}{9}(F - 32) + 273.15$ | |",
        "",
        "### Pressure",
        "",
        "| Conversion | Factor | Notes |",
        "|------------|--------|-------|",
        "| 1 atm | 101325 Pa | exact |",
        "| 1 bar | $10^{5}$ Pa | exact |",
        "| 1 torr | 133.3 Pa | mmHg |",
        "| 1 psi | 6895 Pa | pounds per square inch |",
        "",
    ]
    return lines


def main():
    lines = ["# Mathematical Reference Tables", ""]
    lines.extend(greek_alphabet())
    lines.extend(common_derivatives())
    lines.extend(common_integrals())
    lines.extend(taylor_series())
    lines.extend(trig_identities())
    lines.extend(laplace_transforms())
    lines.extend(z_transforms())
    lines.extend(physical_constants())
    lines.extend(si_conversions())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
