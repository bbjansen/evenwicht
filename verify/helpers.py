# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Shared utility functions for chapter verification files.

Provides reusable numerical methods that appear across multiple chapters,
reducing code duplication and ensuring consistent implementations.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# RK4 integration
# ---------------------------------------------------------------------------

def rk4_step(f, y, t, h):
    """Perform a single classical RK4 step.

    Parameters
    ----------
    f : callable
        Right-hand side ``f(t, y)`` returning the same type as *y*
        (scalar or array).
    y : float or array-like
        Current state.
    t : float
        Current time.
    h : float
        Step size.

    Returns
    -------
    y_next : same type as *y*
        State after one step of size *h*.
    """
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4_integrate(f, y0, t_span, h):
    """Integrate an ODE using classical RK4 from *t_span[0]* to *t_span[1]*.

    Parameters
    ----------
    f : callable
        Right-hand side ``f(t, y)`` returning the same type as *y0*.
    y0 : float or array-like
        Initial state at ``t_span[0]``.
    t_span : tuple[float, float]
        ``(t_start, t_end)``.
    h : float
        Step size.

    Returns
    -------
    y_final : same type as *y0*
        State at ``t_span[1]`` (or the last completed step before it).
    """
    t, y = t_span[0], y0
    n = int((t_span[1] - t_span[0]) / h)
    for _ in range(n):
        y = rk4_step(f, y, t, h)
        t += h
    return y


# ---------------------------------------------------------------------------
# Quadrature rules
# ---------------------------------------------------------------------------

def simpson(f, a, b, n):
    """Composite Simpson's rule on *n* sub-intervals (must be even).

    Parameters
    ----------
    f : callable
        Integrand ``f(x)``.
    a, b : float
        Integration bounds.
    n : int
        Number of sub-intervals (must be even).

    Returns
    -------
    float
        Approximate integral of *f* from *a* to *b*.
    """
    assert n % 2 == 0
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        coeff = 4 if i % 2 == 1 else 2
        s += coeff * f(a + i * h)
    return s * h / 3


def trapezoid(f, a, b, n):
    """Composite trapezoid rule on *n* sub-intervals.

    Parameters
    ----------
    f : callable
        Integrand ``f(x)``.
    a, b : float
        Integration bounds.
    n : int
        Number of sub-intervals.

    Returns
    -------
    float
        Approximate integral of *f* from *a* to *b*.
    """
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h
