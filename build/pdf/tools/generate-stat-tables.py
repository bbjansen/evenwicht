#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Generate standard statistical reference tables for the appendix.

Produces markdown tables for:
  - Standard Normal (Z) cumulative probabilities
  - Student's t critical values
  - Chi-squared critical values
  - F-distribution critical values

Output: dist/stat-tables.md
Requires: scipy, pip3 install scipy
"""

from pathlib import Path
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_FILE = PROJECT_ROOT / "dist" / "stat-tables.md"


def scriptsize_start():
    return ["```{=latex}", "\\scriptsize", "```", ""]

def scriptsize_end():
    return ["", "```{=latex}", "\\normalsize", "```", ""]

def small_start():
    return ["```{=latex}", "\\small", "```", ""]

def small_end():
    return ["", "```{=latex}", "\\normalsize", "```", ""]


def z_table():
    """Standard Normal Z-table: P(Z <= z) for z = 0.00 to 3.49."""
    lines = [
        "# Statistical Reference Tables",
        "",
        "## Reading p-Values from These Tables",
        "",
        "A p-value is the probability, under the null hypothesis, of observing a test statistic as extreme as or more extreme than the one computed from the data. It is read directly from the tables below:",
        "",
        "- **Z-test (two-tailed)**: Compute $z = (\\bar{x} - \\mu_0)/(\\sigma/\\sqrt{n})$. Look up $P(Z \\leq |z|)$ in the Z-table. The p-value is $2 \\times (1 - P(Z \\leq |z|))$.",
        "- **Z-test (one-tailed)**: The p-value is $1 - P(Z \\leq z)$ for an upper-tail test.",
        "- **t-test**: Compute $t$ and find which column of the t-table it falls between for your degrees of freedom. The p-value lies between the corresponding $\\alpha$ values. Reject $H_0$ if $|t|$ exceeds the critical value at your chosen $\\alpha$.",
        "- **Chi-squared test**: Compute $\\chi^2$ and compare against the critical values for your degrees of freedom. The p-value is $P(\\chi^2 > \\text{computed value})$, read from the right-tail columns.",
        "- **F-test**: Compute $F$ and compare against the critical values for your numerator and denominator degrees of freedom. Reject $H_0$ if $F$ exceeds the tabled value at your chosen $\\alpha$.",
        "",
        "## Standard Normal Distribution (Z-Table)",
        "",
        "Cumulative probability $P(Z \\leq z)$ for the standard normal distribution. For a two-tailed p-value at significance level $\\alpha$, reject $H_0$ when $P(Z \\leq |z|) > 1 - \\alpha/2$.",
        "",
    ]
    lines.extend(small_start())
    header = "| z | .00 | .01 | .02 | .03 | .04 | .05 | .06 | .07 | .08 | .09 |"
    sep = "|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|"
    lines.append(header)
    lines.append(sep)
    for row in range(0, 35):
        z_base = row / 10.0
        cells = [f"{z_base:.1f}"]
        for col in range(10):
            z = z_base + col / 100.0
            cells.append(f"{stats.norm.cdf(z):.4f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(small_end())
    lines.append("")
    return lines


def t_table():
    """Student's t critical values."""
    lines = [
        "## Student's t Distribution",
        "",
        "Upper-tail critical values $t_{\\alpha, \\nu}$ for selected significance levels.",
        "",
    ]
    alphas = [0.10, 0.05, 0.025, 0.01, 0.005]
    header = "| df | 0.10 | 0.05 | 0.025 | 0.01 | 0.005 |"
    sep = "|---:|---:|---:|---:|---:|---:|"
    lines.append(header)
    lines.append(sep)
    dfs = list(range(1, 31)) + [40, 60, 80, 100, 120]
    for df in dfs:
        cells = [str(df)]
        for a in alphas:
            cells.append(f"{stats.t.ppf(1 - a, df):.3f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def chi2_table():
    """Chi-squared critical values."""
    lines = [
        "## Chi-Squared Distribution",
        "",
        "Critical values $\\chi^2_{\\alpha, \\nu}$ for selected cumulative probabilities.",
        "",
    ]
    lines.extend(scriptsize_start())
    alphas = [0.005, 0.01, 0.025, 0.05, 0.10, 0.90, 0.95, 0.975, 0.99, 0.995]
    header = "| df | .005 | .01 | .025 | .05 | .10 | .90 | .95 | .975 | .99 | .995 |"
    sep = "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines.append(header)
    lines.append(sep)
    dfs = list(range(1, 31)) + [40, 50, 60, 80, 100]
    for df in dfs:
        cells = [str(df)]
        for a in alphas:
            v = stats.chi2.ppf(a, df)
            cells.append(f"{v:.2f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(scriptsize_end())
    lines.append("")
    return lines


def f_table_block(alpha):
    """F-distribution critical values for a given alpha."""
    lines = [
        f"### Upper {int(alpha*100)}% critical values ($\\alpha = {alpha}$)",
        "",
    ]
    df1s = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30]
    header = "| $\\nu_2 \\backslash \\nu_1$ | " + " | ".join(str(d) for d in df1s) + " |"
    sep = "|---:|" + "---:|" * len(df1s)
    lines.append(header)
    lines.append(sep)
    df2s = list(range(1, 21)) + [25, 30, 40, 60, 120]
    for df2 in df2s:
        cells = [str(df2)]
        for df1 in df1s:
            v = stats.f.ppf(1 - alpha, df1, df2)
            cells.append(f"{v:.1f}" if v >= 100 else f"{v:.2f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def f_table():
    """F-distribution critical values."""
    lines = [
        "## F-Distribution",
        "",
        "Critical values $F_{\\alpha, \\nu_1, \\nu_2}$ where $\\nu_1$ = numerator df (columns) and $\\nu_2$ = denominator df (rows).",
        "",
    ]
    lines.extend(scriptsize_start())
    for alpha in [0.05, 0.01]:
        lines.extend(f_table_block(alpha))
    lines.extend(scriptsize_end())
    return lines


def main():
    lines = []
    lines.extend(z_table())
    lines.extend(t_table())
    lines.extend(chi2_table())
    lines.extend(f_table())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Generated statistical reference tables at {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
