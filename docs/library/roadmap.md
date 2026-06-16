<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Roadmap

The implementation follows the textbook order. Each phase completes a
group of related modules, with the theory chapters serving as the
specification.

## Phases

| Phase | Modules | Chapters | Status |
|-------|---------|----------|--------|
| 1 | `expressions`, `calculus`, `series` | 1, 3–6 | Planned |
| 2 | `special`, `multivariate` | 2, 7 | Planned |
| 3 | `vectors`, `matrices`, `eigen` | 8–10 | Planned |
| 4 | `optimize` | 11–12 | Planned |
| 5 | `probability`, `stats`, `regression` | 13–17 | Planned |
| 6 | `dynamics`, `discrete` | 18–22 | Planned |
| 7 | `operators` | 23–24 | Planned |

## What Exists Today

The mathematical specification is complete. All 48 theory chapters are
written, verified and published. The [API reference](../api/01-expressions.md)
documents the target interface for every module. The verification suite
(4,742 checks) will serve as the test suite for the implementation.

## What Comes Next

Phase 1 begins with the `expressions` module: expression trees, symbolic
differentiation and numeric evaluation. This is the foundation on which
every other module depends.

Each module will be released independently. Install only the modules
that are needed.

## Contributing

The project is not yet accepting external contributions. Once Phase 1 is
released, contribution guidelines will be published here.
