<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Design Principles

The library follows four principles. They are listed in priority order;
when two principles conflict, the one listed first wins.

## Correctness

Every formula is verified symbolically and numerically before
implementation begins. The textbook chapters serve as the specification.
The verification suite (4,742 checks) runs against SciPy, SymPy and NumPy
as reference implementations. A function that returns a wrong answer is
worse than a function that does not exist.

## Purity

All functions are pure. No hidden state, no mutation, no side effects. A
function called twice with the same arguments returns the same result. This
makes the library predictable and easy to test.

Side effects (file I/O, random number generation, logging) are the
caller's responsibility. The library accepts seed values and streams as
arguments where randomness is needed.

## Type Safety

Domain constraints are encoded in the type system where possible. A
function that expects a probability accepts a value in $[0, 1]$; not an
arbitrary number. A function that expects a positive-definite matrix says
so in its type signature.

TypeScript's structural type system cannot enforce every mathematical
constraint at compile time. Where it cannot, runtime validation guards the
boundary and the documentation states the precondition.

## Minimalism

Import only what is needed. Each module is independent and tree-shakeable.
There is no top-level `evenwicht` object that pulls in the entire library.
Internal utilities are not exported. The public API is the smallest surface
that covers the mathematics.
