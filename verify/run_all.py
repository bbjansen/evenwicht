#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""
Orchestrator for the Evenwicht textbook mathematical verification suite.

Runs all chapter verification modules and produces:
  - Console report with pass/fail for every check
  - Markdown report at verify/report/verification-report.md

Usage:
    python3 verify/run_all.py                       # run everything
    python3 verify/run_all.py --chapters 13 14      # specific chapters only
    python3 verify/run_all.py --meta                 # only meta-tests
    python3 verify/run_all.py --no-meta              # only chapter tests
    python3 verify/run_all.py --chapters 1 2 --meta  # chapters 1-2 + meta
"""

import argparse
import importlib
import os
import sys
import time

# Ensure the verify directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework import Report

# ---------------------------------------------------------------------------
# Chapter verification modules (1-48)
# ---------------------------------------------------------------------------

CHAPTERS = {
    1: "ch01_expressions",
    2: "ch02_special_functions",
    3: "ch03_limits",
    4: "ch04_derivatives",
    5: "ch05_integrals",
    6: "ch06_series",
    7: "ch07_multivariate",
    8: "ch08_vectors",
    9: "ch09_matrices",
    10: "ch10_eigenvalues",
    11: "ch11_optimization",
    12: "ch12_constrained_optimization",
    13: "ch13_probability",
    14: "ch14_distributions",
    15: "ch15_descriptive_stats",
    16: "ch16_statistical_inference",
    17: "ch17_regression",
    18: "ch18_difference_equations",
    19: "ch19_odes",
    20: "ch20_discrete_operators",
    21: "ch21_time_series",
    22: "ch22_transforms",
    23: "ch23_operator_algebra",
    24: "ch24_fractional_calculus",
    25: "ch25_financial",
    26: "ch26_machine_learning",
    27: "ch27_trading",
    28: "ch28_information_theory",
    29: "ch29_control_systems",
    30: "ch30_epidemiology",
    31: "ch31_networks",
    32: "ch32_energy",
    33: "ch33_equilibrium",
    34: "ch34_kinetics",
    35: "ch35_pharmacokinetics",
    36: "ch36_game_theory",
    37: "ch37_cryptography",
    38: "ch38_climate",
    39: "ch39_mechanics",
    40: "ch40_signal_processing",
    41: "ch41_orbital",
    42: "ch42_robotics",
    43: "ch43_fluid_dynamics",
    44: "ch44_circuits",
    45: "ch45_geology",
    46: "ch46_cosmology",
    47: "ch47_optics",
    48: "ch48_genetics",
}

# ---------------------------------------------------------------------------
# Meta-verification modules (theorems, diagrams, prose, proofs)
# ---------------------------------------------------------------------------

META_MODULES = {
    "theorems_core": "theorem_testing",
    "theorems_applied": "theorem_testing_applied",
    "diagrams": "validate_diagrams",
    "prose": "verify_prose",
    "proofs": "verify_proofs",
    "style": "verify_style",
    "timelines": "verify_timelines",
}


def _run_module(module_name: str, label: str, report: Report) -> None:
    """Import a verification module, build and run its checks, add to report."""
    try:
        mod = importlib.import_module(module_name)
        chapter = mod.build()
        chapter.run()
        report.add_chapter(chapter)
    except Exception as exc:
        print(f"ERROR loading/running {label}: {type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="Evenwicht textbook mathematical verification suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 verify/run_all.py                       # everything\n"
            "  python3 verify/run_all.py --chapters 13 14      # specific chapters\n"
            "  python3 verify/run_all.py --meta                 # meta-tests only\n"
            "  python3 verify/run_all.py --no-meta              # chapter tests only\n"
            "  python3 verify/run_all.py --chapters 1 2 --meta  # chapters 1-2 + meta\n"
        ),
    )
    parser.add_argument("--chapters", nargs="*", type=int, default=None,
                        help="Specific chapter numbers to verify (1-48)")
    parser.add_argument("--meta", action="store_true", default=False,
                        help="Run only meta-verification modules (theorems, diagrams, prose, proofs)")
    parser.add_argument("--no-meta", action="store_true", default=False,
                        help="Exclude meta-verification modules (run only chapter tests)")
    parser.add_argument("--report", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "report", "verification-report.md"),
        help="Path for the markdown report")
    args = parser.parse_args()

    if args.meta and args.no_meta:
        parser.error("--meta and --no-meta are mutually exclusive")

    # Determine what to run
    run_chapters = not args.meta  # skip chapters when --meta is used alone
    run_meta = not args.no_meta   # skip meta when --no-meta is used

    # When --chapters is given without --meta, run those chapters (and meta
    # unless --no-meta).  When --chapters is given WITH --meta, run both
    # the specified chapters and all meta modules.
    if args.chapters is not None:
        run_chapters = True

    report = Report()

    print(f"Starting verification at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # --- Chapter tests ---
    if run_chapters:
        chapters_to_run = args.chapters if args.chapters is not None else sorted(CHAPTERS.keys())
        print(f"Chapters: {chapters_to_run}")
        for ch_num in chapters_to_run:
            if ch_num not in CHAPTERS:
                print(f"WARNING: No verification module for chapter {ch_num}, skipping.")
                continue
            _run_module(CHAPTERS[ch_num], f"chapter {ch_num}", report)

    # --- Meta tests ---
    if run_meta:
        meta_keys = sorted(META_MODULES.keys())
        print(f"Meta modules: {meta_keys}")
        for key in meta_keys:
            _run_module(META_MODULES[key], f"meta/{key}", report)

    print()
    report.print_console()

    # Write markdown report
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    report.write_markdown(args.report)
    print(f"\nMarkdown report written to: {args.report}")

    sys.exit(report.exit_code)


if __name__ == "__main__":
    main()
