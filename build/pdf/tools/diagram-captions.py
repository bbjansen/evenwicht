#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Apply figure captions to rendered markdown files.

Replaces generic ![diagram](file.png) with ![Figure N.M: Caption](file.png)
so pandoc generates proper LaTeX figures with captions for the List of Figures.
"""

import re
import sys
import os

# Diagram captions: { "basename-N": "caption" }
# Generated from the full diagram catalog across all 48 chapters.
CAPTIONS = {
    # Chapter 1: Mathematical Expressions & Functions
    "01-expressions-1": "Key milestones in mathematical expressions",
    "01-expressions-2": "Expressions and functions concept map",
    "01-expressions-3": "Expression tree for sin(x²)",
    "01-expressions-4": "Expression tree for sin(x² + 1)",
    "01-expressions-5": "Expression tree for x² + 2x + 1",
    "01-expressions-6": "Evaluation order for (x+1)(x-1) at x=5",
    "01-expressions-7": "Chapter connections and dependencies",
    # Chapter 2: Special Functions
    "02-special-functions-1": "Key milestones in special functions",
    "02-special-functions-2": "Special functions concept map",
    "02-special-functions-3": "Special function landscape",
    "02-special-functions-4": "Gamma function for x = 0.5 to 5",
    "02-special-functions-5": "Error function erf(x)",
    "02-special-functions-6": "Stirling approximation accuracy ratio vs n",
    "02-special-functions-7": "Chapter connections and dependencies",
    # Chapter 3: Limits & Continuity
    "03-limits-continuity-1": "Evolution of the limit concept",
    "03-limits-continuity-2": "Limits and continuity concept map",
    "03-limits-continuity-3": "sin(x)/x approaching 1 as x approaches 0",
    "03-limits-continuity-4": "Classification of discontinuities",
    "03-limits-continuity-5": "Types of discontinuity state transitions",
    "03-limits-continuity-6": "(1 + 1/n)^n approaching e",
    "03-limits-continuity-7": "Chapter connections and dependencies",
    # Chapter 4: Differential Calculus
    "04-differential-calculus-1": "Historical development of the derivative",
    "04-differential-calculus-2": "Differentiation concept map",
    "04-differential-calculus-3": "f(x) = sin(x) and f'(x) = cos(x)",
    "04-differential-calculus-4": "Tangent line approximation for x² at x=1",
    "04-differential-calculus-5": "Symbolic differentiation dispatch",
    "04-differential-calculus-6": "Chapter connections and dependencies",
    # Chapter 5: Integral Calculus
    "05-integral-calculus-1": "Historical development of integration",
    "05-integral-calculus-2": "Integration concept map",
    "05-integral-calculus-3": "Trapezoid rule for sin(x) on [0, pi]",
    "05-integral-calculus-4": "Quadrature error comparison for e^x on [0,1]",
    "05-integral-calculus-5": "Chapter connections and dependencies",
    # Chapter 6: Series & Approximation
    "06-series-approximation-1": "Key milestones in series and approximation",
    "06-series-approximation-2": "Series and approximation concept map",
    "06-series-approximation-3": "Geometric series partial sums approaching 2",
    "06-series-approximation-4": "Convergence test classification",
    "06-series-approximation-5": "Taylor polynomials of e^x vs actual",
    "06-series-approximation-6": "Chapter connections and dependencies",
    # Chapter 7: Multivariate Calculus
    "07-multivariate-calculus-1": "Development of multivariate calculus",
    "07-multivariate-calculus-2": "Multivariate calculus concept map",
    "07-multivariate-calculus-3": "Critical point classification via Hessian",
    "07-multivariate-calculus-4": "Critical point classification via eigenvalues",
    "07-multivariate-calculus-5": "Gradient magnitude vs distance from origin",
    "07-multivariate-calculus-6": "Chapter connections and dependencies",
    # Chapter 8: Vectors
    "08-vectors-1": "Development of vector algebra",
    "08-vectors-2": "Vector operations concept map",
    "08-vectors-3": "Cauchy-Schwarz inequality for unit vectors",
    "08-vectors-4": "Vector projection decomposition",
    "08-vectors-5": "Chapter connections and dependencies",
    # Chapter 9: Matrices
    "09-matrices-1": "Key milestones in matrix theory",
    "09-matrices-2": "Matrix operations concept map",
    "09-matrices-3": "Gaussian elimination steps",
    "09-matrices-4": "Matrix inverse via Gauss-Jordan elimination",
    "09-matrices-5": "Matrix multiplication operations vs size",
    "09-matrices-6": "Chapter connections and dependencies",
    # Chapter 10: Eigenvalues
    "10-eigenvalues-1": "Key milestones in eigenvalue theory",
    "10-eigenvalues-2": "Eigenvalues concept map",
    "10-eigenvalues-3": "Diagonalization process",
    "10-eigenvalues-4": "Power iteration algorithm",
    "10-eigenvalues-5": "Eigenvalue convergence during power iteration",
    "10-eigenvalues-6": "Chapter connections and dependencies",
    # Chapter 11: Unconstrained Optimization
    "11-unconstrained-optimization-1": "Key milestones in unconstrained optimization",
    "11-unconstrained-optimization-2": "Unconstrained optimization concept map",
    "11-unconstrained-optimization-3": "Comparing optimization algorithms",
    "11-unconstrained-optimization-4": "Gradient descent iteration flow",
    "11-unconstrained-optimization-5": "Newton's method for optimization",
    "11-unconstrained-optimization-6": "Gradient descent vs Newton's method",
    "11-unconstrained-optimization-7": "Gradient descent convergence",
    "11-unconstrained-optimization-8": "Chapter connections and dependencies",
    # Chapter 12: Constrained Optimization
    "12-constrained-optimization-1": "Historical development of constrained optimization",
    "12-constrained-optimization-2": "Constrained optimization concept map",
    "12-constrained-optimization-3": "Lagrange multiplier method steps",
    "12-constrained-optimization-4": "The simplex method",
    "12-constrained-optimization-5": "Simplex iterations vs problem size",
    "12-constrained-optimization-6": "Chapter connections and dependencies",
    # Chapter 13: Probability Theory
    "13-probability-theory-1": "Key milestones in probability theory",
    "13-probability-theory-2": "Probability theory concept map",
    "13-probability-theory-3": "Probability flow via total probability",
    "13-probability-theory-4": "Bayes' theorem computation flow",
    "13-probability-theory-5": "Law of large numbers convergence",
    "13-probability-theory-6": "Chapter connections and dependencies",
    # Chapter 14: Distributions
    "14-distributions-1": "Key milestones in probability distributions",
    "14-distributions-2": "Probability distributions concept map",
    "14-distributions-3": "Standard normal PDF N(0,1)",
    "14-distributions-4": "Chi-squared PDFs for different degrees of freedom",
    "14-distributions-5": "Student t(3) vs standard normal N(0,1)",
    "14-distributions-6": "Distribution relationship diagram",
    "14-distributions-7": "Distribution landscape",
    "14-distributions-8": "Chapter connections and dependencies",
    # Chapter 15: Descriptive Statistics
    "15-descriptive-statistics-1": "Key milestones in descriptive statistics",
    "15-descriptive-statistics-2": "Descriptive statistics concept map",
    "15-descriptive-statistics-3": "Right-skewed distribution (positive skewness)",
    "15-descriptive-statistics-4": "Five-number summary structure",
    "15-descriptive-statistics-5": "Box plot construction",
    "15-descriptive-statistics-6": "Chapter connections and dependencies",
    # Chapter 16: Statistical Inference
    "16-statistical-inference-1": "Key milestones in statistical inference",
    "16-statistical-inference-2": "Statistical inference concept map",
    "16-statistical-inference-3": "Inference workflow",
    "16-statistical-inference-4": "Hypothesis testing procedure",
    "16-statistical-inference-5": "Power curve vs true effect size",
    "16-statistical-inference-6": "Hypothesis testing decision outcomes",
    "16-statistical-inference-7": "Statistical test classification",
    "16-statistical-inference-8": "Chapter connections and dependencies",
    # Chapter 17: Regression
    "17-regression-1": "Key milestones in regression and econometrics",
    "17-regression-2": "Regression concept map",
    "17-regression-3": "Simple regression: actual vs fitted",
    "17-regression-4": "OLS regression workflow",
    "17-regression-5": "Chapter connections and dependencies",
    # Chapter 18: Difference Equations
    "18-difference-equations-1": "Key milestones in difference equations",
    "18-difference-equations-2": "Difference equations concept map",
    "18-difference-equations-3": "AR(1) convergence to equilibrium",
    "18-difference-equations-4": "Stability classification for difference equations",
    "18-difference-equations-5": "Stability of first-order difference equations",
    "18-difference-equations-6": "Chapter connections and dependencies",
    # Chapter 19: ODEs
    "19-odes-1": "Key milestones in ordinary differential equations",
    "19-odes-2": "ODEs concept map",
    "19-odes-3": "ODE methods landscape",
    "19-odes-4": "ODE classification and solution methods",
    "19-odes-5": "Euler vs RK4 vs exact for dy/dx = y",
    "19-odes-6": "Chapter connections and dependencies",
    # Chapter 20: Discrete Operators
    "20-discrete-operators-1": "Key milestones in discrete operator theory",
    "20-discrete-operators-2": "Discrete operators concept map",
    "20-discrete-operators-3": "Continuous-discrete operator correspondence",
    "20-discrete-operators-4": "Discrete operator relationships and Z-transform",
    "20-discrete-operators-5": "Differences remove polynomial trends",
    "20-discrete-operators-6": "Chapter connections and dependencies",
    # Chapter 21: Time Series
    "21-time-series-1": "Key milestones in time series analysis",
    "21-time-series-2": "Time series concept map",
    "21-time-series-3": "Autocorrelation function of AR(1)",
    "21-time-series-4": "Box-Jenkins iterative modeling process",
    "21-time-series-5": "Box-Jenkins methodology",
    "21-time-series-6": "Chapter connections and dependencies",
    # Chapter 22: Transforms
    "22-transforms-1": "Key milestones in transform theory",
    "22-transforms-2": "Transforms concept map",
    "22-transforms-3": "Fast convolution via FFT",
    "22-transforms-4": "DFT magnitude spectrum",
    "22-transforms-5": "Chapter connections and dependencies",
    # Chapter 23: Operator Algebra
    "23-operator-algebra-1": "Key milestones in operator algebra",
    "23-operator-algebra-2": "Operator algebra concept map",
    "23-operator-algebra-3": "Operator landscape",
    "23-operator-algebra-4": "Operator unification as LinearOperator",
    "23-operator-algebra-5": "Operator class hierarchy",
    "23-operator-algebra-6": "Operator exponential shifts sin(x) by 1",
    "23-operator-algebra-7": "Chapter connections and dependencies",
    # Chapter 24: Fractional Calculus
    "24-fractional-calculus-1": "Key milestones in fractional calculus",
    "24-fractional-calculus-2": "Fractional calculus concept map",
    "24-fractional-calculus-3": "Chapter connections and dependencies",
    "24-fractional-calculus-4": "Grunwald-Letnikov weights for half-derivative",
    # Chapter 25: Financial Mathematics
    "25-financial-mathematics-1": "Key milestones in financial mathematics",
    "25-financial-mathematics-2": "Financial mathematics concept map",
    "25-financial-mathematics-3": "Compound interest growth",
    "25-financial-mathematics-4": "NPV investment decision rule",
    "25-financial-mathematics-5": "Loan payment cash flow breakdown",
    "25-financial-mathematics-6": "Chapter connections and dependencies",
    # Chapter 26: Machine Learning
    "26-machine-learning-1": "Key milestones in machine learning",
    "26-machine-learning-2": "Machine learning concept map",
    "26-machine-learning-3": "Training loop",
    "26-machine-learning-4": "Backpropagation data flow",
    "26-machine-learning-5": "Bias-variance tradeoff",
    "26-machine-learning-6": "Chapter connections and dependencies",
    # Chapter 27: Quantitative Trading
    "27-quantitative-trading-1": "Key milestones in quantitative trading",
    "27-quantitative-trading-2": "Quantitative trading concept map",
    "27-quantitative-trading-3": "Efficient frontier: return vs risk",
    "27-quantitative-trading-4": "Pairs trading signal generation",
    "27-quantitative-trading-5": "Chapter connections and dependencies",
    # Chapter 28: Information Theory
    "28-information-theory-1": "Key milestones in information theory",
    "28-information-theory-2": "Information theory concept map",
    "28-information-theory-3": "Cross-entropy, KL divergence, and MLE",
    "28-information-theory-4": "Binary entropy function H(p)",
    "28-information-theory-5": "KL divergence: P vs Q distributions",
    "28-information-theory-6": "Chapter connections and dependencies",
    # Chapter 29: Control Systems
    "29-control-systems-1": "Key milestones in control systems",
    "29-control-systems-2": "Control systems concept map",
    "29-control-systems-3": "Control system stability classification",
    "29-control-systems-4": "PID control loop",
    "29-control-systems-5": "Step response (underdamped)",
    "29-control-systems-6": "Chapter connections and dependencies",
    # Chapter 30: Epidemiology
    "30-epidemiology-1": "Key milestones in epidemiology",
    "30-epidemiology-2": "Epidemiology and population dynamics concept map",
    "30-epidemiology-3": "SIR compartment model",
    "30-epidemiology-4": "SIR epidemic dynamics (R0 = 2.5)",
    "30-epidemiology-5": "SIR state transitions",
    "30-epidemiology-6": "Herd immunity threshold vs R0",
    "30-epidemiology-7": "Chapter connections and dependencies",
    # Chapter 31: Network Analysis
    "31-network-analysis-1": "Key milestones in network analysis",
    "31-network-analysis-2": "Network analysis concept map",
    "31-network-analysis-3": "Scale-free degree distribution (power law)",
    "31-network-analysis-4": "PageRank iteration",
    "31-network-analysis-5": "Chapter connections and dependencies",
    # Chapter 32: Energy Systems
    "32-energy-systems-1": "Key milestones in energy systems",
    "32-energy-systems-2": "Energy systems concept map",
    "32-energy-systems-3": "Radioactive decay",
    "32-energy-systems-4": "Radioactive decay (exponential)",
    "32-energy-systems-5": "Energy flow from generation to consumption",
    "32-energy-systems-6": "Economic dispatch via equal incremental cost",
    "32-energy-systems-7": "Chapter connections and dependencies",
    # Chapter 33: Equilibrium
    "33-equilibrium-1": "Key dates in equilibrium theory",
    "33-equilibrium-2": "Equilibrium and steady states concept map",
    "33-equilibrium-3": "Classification of equilibria",
    "33-equilibrium-4": "Solow model: investment vs depreciation",
    "33-equilibrium-5": "Equilibrium classification procedure",
    "33-equilibrium-6": "Chapter connections and dependencies",
    # Chapter 34: Chemical Kinetics
    "34-chemical-kinetics-1": "Key milestones in chemical kinetics",
    "34-chemical-kinetics-2": "Chemical kinetics concept map",
    "34-chemical-kinetics-3": "First-order decay",
    "34-chemical-kinetics-4": "Michaelis-Menten enzyme kinetics",
    "34-chemical-kinetics-5": "Chapter connections and dependencies",
    # Chapter 35: Pharmacokinetics
    "35-pharmacokinetics-1": "Key dates in pharmacokinetics",
    "35-pharmacokinetics-2": "Pharmacokinetics concept map",
    "35-pharmacokinetics-3": "One-compartment pharmacokinetic model",
    "35-pharmacokinetics-4": "Drug concentration after IV bolus",
    "35-pharmacokinetics-5": "Two-compartment model state transitions",
    "35-pharmacokinetics-6": "Chapter connections and dependencies",
    # Chapter 36: Game Theory
    "36-game-theory-1": "Key dates in game theory",
    "36-game-theory-2": "Game theory concept map",
    "36-game-theory-3": "Classification of games",
    "36-game-theory-4": "Finding Nash equilibria",
    "36-game-theory-5": "Replicator dynamics: hawk frequency over time",
    "36-game-theory-6": "Chapter connections and dependencies",
    # Chapter 37: Cryptography
    "37-cryptography-1": "History of cryptography",
    "37-cryptography-2": "Cryptography concept map",
    "37-cryptography-3": "RSA key generation and encryption",
    "37-cryptography-4": "Birthday paradox: collision probability",
    "37-cryptography-5": "Chapter connections and dependencies",
    # Chapter 38: Climate Modeling
    "38-climate-modeling-1": "Key dates in climate science",
    "38-climate-modeling-2": "Climate modeling concept map",
    "38-climate-modeling-3": "CO2 concentration trend (Keeling curve)",
    "38-climate-modeling-4": "Earth's energy budget",
    "38-climate-modeling-5": "Radiative forcing vs CO2 concentration",
    "38-climate-modeling-6": "Chapter connections and dependencies",
    # Chapter 39: Mechanics & Waves
    "39-mechanics-waves-1": "Key dates in classical mechanics",
    "39-mechanics-waves-2": "Classical mechanics concept map",
    "39-mechanics-waves-3": "Mechanics problem landscape",
    "39-mechanics-waves-4": "Simple harmonic motion",
    "39-mechanics-waves-5": "Resonance curve (driven oscillator)",
    "39-mechanics-waves-6": "Chapter connections and dependencies",
    # Chapter 40: Signal Processing
    "40-signal-processing-1": "Key dates in signal processing",
    "40-signal-processing-2": "Signal processing concept map",
    "40-signal-processing-3": "Low-pass filter frequency response",
    "40-signal-processing-4": "Digital filter classification",
    "40-signal-processing-5": "Frequency-domain noise removal",
    "40-signal-processing-6": "Chapter connections and dependencies",
    # Chapter 41: Orbital Mechanics
    "41-orbital-mechanics-1": "Key dates in orbital mechanics",
    "41-orbital-mechanics-2": "Orbital mechanics concept map",
    "41-orbital-mechanics-3": "Orbit classification by energy",
    "41-orbital-mechanics-4": "Orbital velocity vs altitude",
    "41-orbital-mechanics-5": "Hohmann transfer orbit",
    "41-orbital-mechanics-6": "Chapter connections and dependencies",
    # Chapter 42: Robotics
    "42-robotics-1": "Key dates in robotics",
    "42-robotics-2": "Robotics concept map",
    "42-robotics-3": "Robot control loop",
    "42-robotics-4": "Inverse kinematics via Newton's method",
    "42-robotics-5": "2-link arm workspace boundary",
    "42-robotics-6": "Chapter connections and dependencies",
    # Chapter 43: Fluid Dynamics
    "43-fluid-dynamics-1": "Key dates in fluid dynamics",
    "43-fluid-dynamics-2": "Fluid dynamics concept map",
    "43-fluid-dynamics-3": "Poiseuille velocity profile in a pipe",
    "43-fluid-dynamics-4": "Flow regime classification via Reynolds number",
    "43-fluid-dynamics-5": "Chapter connections and dependencies",
    # Chapter 44: Circuits
    "44-circuits-1": "Key dates in circuit theory",
    "44-circuits-2": "Circuit analysis concept map",
    "44-circuits-3": "AC circuit analysis workflow",
    "44-circuits-4": "RC circuit charging curve",
    "44-circuits-5": "RLC response classification",
    "44-circuits-6": "Chapter connections and dependencies",
    # Chapter 45: Geology & Seismology
    "45-geology-seismology-1": "Key milestones in seismology",
    "45-geology-seismology-2": "Geophysics concept map",
    "45-geology-seismology-3": "Gutenberg-Richter frequency-magnitude relation",
    "45-geology-seismology-4": "Radiocarbon dating procedure",
    "45-geology-seismology-5": "Chapter connections and dependencies",
    # Chapter 46: Cosmology
    "46-cosmology-1": "Key milestones in cosmology",
    "46-cosmology-2": "Cosmology concept map",
    "46-cosmology-3": "Scale factor evolution (matter-dominated)",
    "46-cosmology-4": "Solving the Friedmann equation",
    "46-cosmology-5": "Chapter connections and dependencies",
    # Chapter 47: Optics & Acoustics
    "47-optics-acoustics-1": "Key dates in optics and acoustics",
    "47-optics-acoustics-2": "Waves concept map",
    "47-optics-acoustics-3": "Wave phenomena complexity",
    "47-optics-acoustics-4": "Double-slit interference pattern",
    "47-optics-acoustics-5": "ABCD matrix ray tracing",
    "47-optics-acoustics-6": "Chapter connections and dependencies",
    # Chapter 48: Genetics
    "48-genetics-1": "Key dates in genetics and population theory",
    "48-genetics-2": "Population genetics concept map",
    "48-genetics-3": "Hardy-Weinberg equilibrium test",
    "48-genetics-4": "Allele frequency dynamics",
    "48-genetics-5": "Allele frequency under positive selection",
    "48-genetics-6": "Chapter connections and dependencies",
}


def apply_captions(rendered_dir):
    """Replace ![diagram](file.ext) with ![Caption](file.ext) in rendered markdown."""
    import glob

    count = 0
    for md_path in sorted(glob.glob(os.path.join(rendered_dir, "[0-9]*.md"))):
        with open(md_path, "r") as f:
            content = f.read()

        def replace_alt(match):
            nonlocal count
            filename = match.group(2)
            # Extract base name without extension or path prefix
            base = os.path.splitext(os.path.basename(filename))[0]
            if base in CAPTIONS:
                count += 1
                return f"![{CAPTIONS[base]}]({filename})"
            return match.group(0)

        content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_alt, content)

        with open(md_path, "w") as f:
            f.write(content)

    return count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: diagram-captions.py <rendered_dir>")
        sys.exit(1)

    rendered_dir = sys.argv[1]
    n = apply_captions(rendered_dir)
    print(f"  Applied {n} diagram captions")
