<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# How to Read This Book

This book may be read sequentially as a textbook, selectively as a
reference, or along one of the curated reading paths on the
[home page](../index.md).

## The Chapter Template

Every chapter follows the same twelve-section structure. Knowing the
template makes it easy to find what is needed.

1. **Historical Context**: the origin of the ideas and who developed them.
2. **Why This Chapter Matters**: the practical significance; at least one concrete application.
3. **Notation & Conventions**: every symbol defined before use.
4. **Core Theory**: numbered definitions, theorems and proofs.
5. **Formulas & Identities**: key results collected for quick reference.
6. **Algorithms**: computational procedures with complexity analysis.
7. **Numerical Considerations**: precision, stability and edge cases.
8. **Worked Examples**: complete problems traced from statement to answer.
9. **Connections**: how this chapter relates to others; a dependency diagram.
10. **Exercises**: three tiers: routine, intermediate and challenging.
11. **References**: textbooks, historical papers and online resources.
12. **Glossary**: one-sentence definitions of key terms.

Eight chapters carry an optional thirteenth section, **Appendix**, with
supplementary data tables.

## Prerequisites

No prior knowledge beyond secondary-school algebra is required. Chapters
1 through 3 build from scratch. Prior exposure to single-variable calculus
makes the pace of Parts I and II comfortable rather than demanding.

Each chapter states its prerequisites in the front matter. Any chapter may
be read independently given that prerequisite knowledge. The
[Knowledge Graph](../graph/index.md) maps every dependency.

## Numerical Precision

All computations use IEEE 754 double-precision arithmetic. Results are
displayed to the precision standard for each domain.

| Domain | Precision | Rationale |
|--------|-----------|-----------|
| Special functions ($\Gamma$, erf, $B$) | 6 significant figures | Reference-table standard |
| Calculus | 6 significant figures | Matches quadrature accuracy |
| Linear algebra | 4–6 significant figures | Condition-dependent |
| Statistics | 4 significant figures | Reporting convention |
| Probability (CDF, p-values) | 4 decimal places | Matches standard tables |
| Regression coefficients | 3–4 significant figures | Econometric convention |
| Applied domains | 3–4 significant figures | Matches measurement precision |
| Error bounds | 1–2 significant figures | Order of magnitude suffices |

Exact results are presented exactly (e.g. $\Gamma(5) = 24$). Approximate
results carry the $\approx$ symbol. All numerical output has been verified
against SciPy and NumPy.
