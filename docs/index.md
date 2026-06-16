<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Evenwicht

Evenwicht is a mathematics textbook in 48 chapters. It starts with
expressions and ends with genetics. Every chapter follows the same
structure. Every formula has been verified.

The first 24 chapters develop the theory: calculus, linear algebra,
probability, statistics, differential equations, operator theory. The
remaining 24 apply that theory to finance, machine learning, epidemiology,
climate science, robotics and 19 other fields. No new mathematics appears
in the application chapters; only new models.

A companion TypeScript [library](library/index.md) implements the
mathematics as typed, pure functions. The
[API reference](api/01-expressions.md) documents every module.

---

## Start Reading

Each chapter states its prerequisites and defines all notation before use.
No prior knowledge beyond secondary-school algebra is required.

| Background | Entry point |
|------------|-------------|
| Beginning university mathematics | [Chapter 1: Expressions & Functions](domains/01-expressions.md) |
| Comfortable with single-variable calculus | [Chapter 8: Vectors](domains/08-vectors.md) or [Chapter 13: Probability](domains/13-probability-theory.md) |
| Looking for a specific topic | The [Subject Index](reference/subject-index.md) or the search bar |
| Interested in the implementation | The [Library](library/index.md) overview |

For guidance on how the chapters are structured and how to navigate between
them, see [How to Read This Book](front/how-to-read.md).

---

## Reading Paths

Not every reader needs all 48 chapters. Five curated paths select the
chapters that serve a particular goal. Each path lists chapters in
reading order; later chapters depend on earlier ones within the same path.

### Finance and Economics

For readers in quantitative finance, economics or econometrics.

1. [Chapter 1: Expressions & Functions](domains/01-expressions.md)
2. [Chapter 2: Special Functions](domains/02-special-functions.md)
3. [Chapter 3: Limits & Continuity](domains/03-limits-continuity.md)
4. [Chapter 4: Differential Calculus](domains/04-differential-calculus.md)
5. [Chapter 5: Integral Calculus](domains/05-integral-calculus.md)
6. [Chapter 7: Multivariate Calculus](domains/07-multivariate-calculus.md)
7. [Chapter 11: Unconstrained Optimization](domains/11-unconstrained-optimization.md)
8. [Chapter 12: Constrained Optimization & LP](domains/12-constrained-optimization.md)
9. [Chapter 13: Probability Theory](domains/13-probability-theory.md)
10. [Chapter 14: Distributions](domains/14-distributions.md)
11. [Chapter 15: Descriptive Statistics](domains/15-descriptive-statistics.md)
12. [Chapter 16: Statistical Inference](domains/16-statistical-inference.md)
13. [Chapter 25: Financial Mathematics](domains/25-financial-mathematics.md)
14. [Chapter 27: Quantitative Trading](domains/27-quantitative-trading.md)
15. [Chapter 36: Game Theory](domains/36-game-theory.md)
16. [Chapter 33: Equilibrium](domains/33-equilibrium.md)

### Machine Learning and Data Science

For readers building or analysing statistical and machine-learning models.

1. [Chapter 1: Expressions & Functions](domains/01-expressions.md)
2. [Chapter 3: Limits & Continuity](domains/03-limits-continuity.md)
3. [Chapter 4: Differential Calculus](domains/04-differential-calculus.md)
4. [Chapter 7: Multivariate Calculus](domains/07-multivariate-calculus.md)
5. [Chapter 8: Vectors](domains/08-vectors.md)
6. [Chapter 9: Matrices](domains/09-matrices.md)
7. [Chapter 10: Eigenvalues](domains/10-eigenvalues.md)
8. [Chapter 11: Unconstrained Optimization](domains/11-unconstrained-optimization.md)
9. [Chapter 13: Probability Theory](domains/13-probability-theory.md)
10. [Chapter 14: Distributions](domains/14-distributions.md)
11. [Chapter 15: Descriptive Statistics](domains/15-descriptive-statistics.md)
12. [Chapter 16: Statistical Inference](domains/16-statistical-inference.md)
13. [Chapter 17: Regression & Econometrics](domains/17-regression.md)
14. [Chapter 26: Machine Learning](domains/26-machine-learning.md)
15. [Chapter 28: Information Theory](domains/28-information-theory.md)
16. [Chapter 21: Time Series](domains/21-time-series.md)

### Physics and Engineering

For readers in mechanics, electrical engineering, fluid dynamics or aerospace.

1. [Chapter 1: Expressions & Functions](domains/01-expressions.md)
2. [Chapter 2: Special Functions](domains/02-special-functions.md)
3. [Chapter 4: Differential Calculus](domains/04-differential-calculus.md)
4. [Chapter 5: Integral Calculus](domains/05-integral-calculus.md)
5. [Chapter 7: Multivariate Calculus](domains/07-multivariate-calculus.md)
6. [Chapter 8: Vectors](domains/08-vectors.md)
7. [Chapter 9: Matrices](domains/09-matrices.md)
8. [Chapter 10: Eigenvalues](domains/10-eigenvalues.md)
9. [Chapter 19: ODEs](domains/19-odes.md)
10. [Chapter 22: Transforms](domains/22-transforms.md)
11. [Chapter 39: Mechanics & Waves](domains/39-mechanics-waves.md)
12. [Chapter 40: Signal Processing](domains/40-signal-processing.md)
13. [Chapter 44: Circuits](domains/44-circuits.md)
14. [Chapter 43: Fluid Dynamics](domains/43-fluid-dynamics.md)
15. [Chapter 41: Orbital Mechanics](domains/41-orbital-mechanics.md)

### Pure Mathematics

For readers interested in the theory itself, without applications.

1. [Chapter 1: Expressions & Functions](domains/01-expressions.md)
2. [Chapter 3: Limits & Continuity](domains/03-limits-continuity.md)
3. [Chapter 4: Differential Calculus](domains/04-differential-calculus.md)
4. [Chapter 5: Integral Calculus](domains/05-integral-calculus.md)
5. [Chapter 6: Series & Approximation](domains/06-series-approximation.md)
6. [Chapter 8: Vectors](domains/08-vectors.md)
7. [Chapter 9: Matrices](domains/09-matrices.md)
8. [Chapter 10: Eigenvalues](domains/10-eigenvalues.md)
9. [Chapter 20: Discrete Operators](domains/20-discrete-operators.md)
10. [Chapter 22: Transforms](domains/22-transforms.md)
11. [Chapter 23: Operator Algebra](domains/23-operator-algebra.md)
12. [Chapter 24: Fractional Calculus](domains/24-fractional-calculus.md)

### Full Sequential

All 48 chapters in order, Parts I through IX. This path covers every topic and
respects all dependencies by construction.

1. [Chapter 1: Expressions & Functions](domains/01-expressions.md)
2. [Chapter 2: Special Functions](domains/02-special-functions.md)
3. [Chapter 3: Limits & Continuity](domains/03-limits-continuity.md)
4. [Chapter 4: Differential Calculus](domains/04-differential-calculus.md)
5. [Chapter 5: Integral Calculus](domains/05-integral-calculus.md)
6. [Chapter 6: Series & Approximation](domains/06-series-approximation.md)
7. [Chapter 7: Multivariate Calculus](domains/07-multivariate-calculus.md)
8. [Chapter 8: Vectors](domains/08-vectors.md)
9. [Chapter 9: Matrices](domains/09-matrices.md)
10. [Chapter 10: Eigenvalues](domains/10-eigenvalues.md)
11. [Chapter 11: Unconstrained Optimization](domains/11-unconstrained-optimization.md)
12. [Chapter 12: Constrained Optimization & LP](domains/12-constrained-optimization.md)
13. [Chapter 13: Probability Theory](domains/13-probability-theory.md)
14. [Chapter 14: Distributions](domains/14-distributions.md)
15. [Chapter 15: Descriptive Statistics](domains/15-descriptive-statistics.md)
16. [Chapter 16: Statistical Inference](domains/16-statistical-inference.md)
17. [Chapter 17: Regression & Econometrics](domains/17-regression.md)
18. [Chapter 18: Difference Equations](domains/18-difference-equations.md)
19. [Chapter 19: ODEs](domains/19-odes.md)
20. [Chapter 20: Discrete Operators](domains/20-discrete-operators.md)
21. [Chapter 21: Time Series](domains/21-time-series.md)
22. [Chapter 22: Transforms](domains/22-transforms.md)
23. [Chapter 23: Operator Algebra](domains/23-operator-algebra.md)
24. [Chapter 24: Fractional Calculus](domains/24-fractional-calculus.md)
25. [Chapter 25: Financial Mathematics](domains/25-financial-mathematics.md)
26. [Chapter 26: Machine Learning](domains/26-machine-learning.md)
27. [Chapter 27: Quantitative Trading](domains/27-quantitative-trading.md)
28. [Chapter 28: Information Theory](domains/28-information-theory.md)
29. [Chapter 29: Control Systems](domains/29-control-systems.md)
30. [Chapter 30: Epidemiology](domains/30-epidemiology.md)
31. [Chapter 31: Network Analysis](domains/31-network-analysis.md)
32. [Chapter 32: Energy Systems](domains/32-energy-systems.md)
33. [Chapter 33: Equilibrium](domains/33-equilibrium.md)
34. [Chapter 34: Chemical Kinetics](domains/34-chemical-kinetics.md)
35. [Chapter 35: Pharmacokinetics](domains/35-pharmacokinetics.md)
36. [Chapter 36: Game Theory](domains/36-game-theory.md)
37. [Chapter 37: Cryptography](domains/37-cryptography.md)
38. [Chapter 38: Climate Modelling](domains/38-climate-modeling.md)
39. [Chapter 39: Mechanics & Waves](domains/39-mechanics-waves.md)
40. [Chapter 40: Signal Processing](domains/40-signal-processing.md)
41. [Chapter 41: Orbital Mechanics](domains/41-orbital-mechanics.md)
42. [Chapter 42: Robotics](domains/42-robotics.md)
43. [Chapter 43: Fluid Dynamics](domains/43-fluid-dynamics.md)
44. [Chapter 44: Circuits](domains/44-circuits.md)
45. [Chapter 45: Geology & Seismology](domains/45-geology-seismology.md)
46. [Chapter 46: Cosmology](domains/46-cosmology.md)
47. [Chapter 47: Optics & Acoustics](domains/47-optics-acoustics.md)
48. [Chapter 48: Genetics](domains/48-genetics.md)

The [Knowledge Graph](graph/index.md) maps every dependency between
chapters.

---

## The Nine Parts

| Part | Chapters | Scope |
|------|----------|-------|
| I | 1–2 | Expressions and special functions |
| II | 3–7 | Limits through multivariate calculus |
| III | 8–10 | Vectors, matrices and eigenvalues |
| IV | 11–12 | Unconstrained and constrained optimisation |
| V | 13–17 | Probability through regression |
| VI | 18–19 | Difference equations and ODEs |
| VII | 20–22 | Discrete operators, time series and transforms |
| VIII | 23–24 | Operator algebra and fractional calculus |
| IX | 25–48 | 24 applied domains |

---

## Reference

- [Bibliography](reference/bibliography.md): 487 cited works
- [Notation Index](reference/notation-index.md): every symbol used in the book
- [Subject Index](reference/subject-index.md): alphabetical term index
- [Math Tables](reference/math-tables.md): Greek alphabet, standard derivatives and integrals
- [Statistical Tables](reference/stat-tables.md): Z, t, $\chi^2$ and F distributions
- [Solutions](solutions/01-expressions.md): worked solutions for all exercises

---

Evenwicht is written by B.B. Jansen. The text has been verified by 4,742
automated checks covering symbolic identities, numerical computations and
structural properties. All results are tested against SciPy, SymPy and
NumPy.

[Download PDF](https://github.com/bbjansen/evenwicht/releases/latest/download/evenwicht.pdf){ .md-button } ·
[Acknowledgments](front/acknowledgments.md) ·
[Errata](front/errata.md) ·
[GitHub](https://github.com/bbjansen/evenwicht)
