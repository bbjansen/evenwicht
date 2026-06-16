#!/usr/bin/env python3

# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Verify spelling across all documentation chapters.

Checks all Markdown files in docs/domains/, docs/api/, docs/front/, and
docs/solutions/ for misspelled words.  LaTeX math, code blocks, mermaid
diagrams, HTML comments, URLs, and file paths are stripped before checking.

A custom dictionary of math/science terms is maintained at
scripts/.math-dictionary.txt and can be extended with --add-word.

Usage:
  python3 scripts/verify-spelling.py              # check all files
  python3 scripts/verify-spelling.py --quick       # check first 3 chapters only
  python3 scripts/verify-spelling.py --add-word eigendecomposition

Requires: pyspellchecker (pip3 install pyspellchecker)
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DICT_PATH = Path(__file__).resolve().parent / ".math-dictionary.txt"

# ── File discovery ────────────────────────────────

GLOB_PATTERNS = [
    ("docs/domains", "[0-9]*.md"),
    ("docs/api", "[0-9]*.md"),
    ("docs/front", "*.md"),
    ("docs/solutions", "*.md"),
]


def discover_files(quick: bool = False) -> list[Path]:
    """Return sorted list of Markdown files to check."""
    files: list[Path] = []
    for subdir, pattern in GLOB_PATTERNS:
        target = PROJECT_ROOT / subdir
        if target.is_dir():
            files.extend(sorted(target.glob(pattern)))
    files.sort()
    if quick:
        files = files[:3]
    return files


# ── Text stripping ────────────────────────────────

# Order matters: strip broad constructs first, then inline.

# Fenced code blocks (``` ... ```) including language tags.
# Allow leading whitespace so fences inside list items / admonitions are caught.
_RE_FENCED_CODE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.MULTILINE | re.DOTALL)

# Mermaid blocks are a special case of fenced code but match anyway
_RE_MERMAID = re.compile(r"^[ \t]*```mermaid.*?^[ \t]*```", re.MULTILINE | re.DOTALL)

# HTML comments <!-- ... -->
_RE_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

# Display math $$...$$ (possibly multiline)
_RE_DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.DOTALL)

# Inline math $...$  (non-greedy, single line)
_RE_INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)(?!\s)(.+?)(?<!\s)\$(?!\$)")

# URLs  http(s)://...
_RE_URL = re.compile(r"https?://\S+")

# Markdown links — keep link text, drop URL
_RE_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]+\)")

# Markdown image references ![alt](url)
_RE_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")

# HTML tags <tag ...> or </tag>
_RE_HTML_TAG = re.compile(r"</?[a-zA-Z][^>]*>")

# File paths (Unix style)
_RE_FILE_PATH = re.compile(r"(?:\./|/)[a-zA-Z0-9_./-]+")

# Inline code `...`
_RE_INLINE_CODE = re.compile(r"`[^`]+`")

# Markdown heading markers (# ## ### etc.)
_RE_HEADING_MARKER = re.compile(r"^#{1,6}\s+", re.MULTILINE)

# Bold / italic markers
_RE_BOLD_ITALIC = re.compile(r"\*{1,3}|_{1,3}")

# Markdown horizontal rules
_RE_HR = re.compile(r"^---+\s*$", re.MULTILINE)

# Markdown table separators
_RE_TABLE_SEP = re.compile(r"^[|: -]+$", re.MULTILINE)

# Numbers (pure digits, possibly with decimal point)
_RE_NUMBERS = re.compile(r"\b\d+(?:\.\d+)?\b")

# Markdown list markers
_RE_LIST_MARKER = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_RE_ORDERED_LIST = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)

# Footnote-style references [^1]
_RE_FOOTNOTE = re.compile(r"\[\^?\d+\]")

# Pipe characters (tables)
_RE_PIPE = re.compile(r"\|")

# Blockquote markers
_RE_BLOCKQUOTE = re.compile(r"^>\s*", re.MULTILINE)

# LaTeX-style commands that may leak through (e.g., \operatorname, \mathbf)
_RE_LATEX_CMD = re.compile(r"\\[a-zA-Z]+(?:\{[^}]*\})?")

# Remaining special characters
_RE_SPECIAL = re.compile(r"[{}()\[\]<>\"',:;!?=+\\/@#&…—–·×÷≥≤≠≈∈∉⊂⊃∪∩∀∃∞∇∂∑∏∫√±°′″←→↔⇒⇔λμσρθφψωΩΔΓΠΣ]")


def strip_markup(text: str) -> list[tuple[int, str]]:
    """Strip all non-prose content and return (line_number, cleaned_line) pairs.

    We process the full text to handle multiline constructs, then map
    remaining content back to original line numbers.
    """
    # Phase 1: Remove multiline constructs (replace with same number of
    # newlines to preserve line numbering).
    for pattern in [
        _RE_MERMAID,
        _RE_FENCED_CODE,
        _RE_HTML_COMMENT,
        _RE_DISPLAY_MATH,
    ]:
        text = pattern.sub(lambda m: "\n" * m.group().count("\n"), text)

    # Phase 2: Per-line stripping
    lines = text.split("\n")
    result: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        cleaned = line
        for pattern in [
            _RE_INLINE_MATH,
            _RE_MD_IMAGE,
            _RE_MD_LINK,
            _RE_URL,
            _RE_INLINE_CODE,
            _RE_HTML_TAG,
            _RE_FILE_PATH,
            _RE_LATEX_CMD,
            _RE_HEADING_MARKER,
            _RE_BOLD_ITALIC,
            _RE_HR,
            _RE_TABLE_SEP,
            _RE_NUMBERS,
            _RE_LIST_MARKER,
            _RE_ORDERED_LIST,
            _RE_FOOTNOTE,
            _RE_PIPE,
            _RE_BLOCKQUOTE,
            _RE_SPECIAL,
        ]:
            if pattern == _RE_MD_LINK:
                cleaned = pattern.sub(r"\1", cleaned)
            else:
                cleaned = pattern.sub(" ", cleaned)
        result.append((i, cleaned))
    return result


# ── Word extraction ───────────────────────────────

# Match Unicode letters so accented citation words ("Göttingen", "mathématiques")
# tokenise as single words instead of splitting on the accented characters.
_RE_WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)

# Words containing any non-ASCII letter are treated as non-English citations
# (German/French titles, foreign author names) and skipped — checking them
# against an English dictionary is meaningless. Maintain a curated dictionary
# entry only for non-ASCII words that recur in English prose.
_RE_HAS_NON_ASCII = re.compile(r"[^\x00-\x7F]")


def extract_words(line: str) -> list[str]:
    """Extract words from a cleaned line, skipping very short tokens."""
    out: list[str] = []
    for m in _RE_WORD.finditer(line):
        w = m.group()
        if len(w) <= 1:
            continue
        if _RE_HAS_NON_ASCII.search(w):
            continue
        out.append(w)
    return out


# ── Custom dictionary ─────────────────────────────

DEFAULT_TERMS = sorted(set([
    # ── Greek letter names ─────────────────────────
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
    "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
    "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",

    # ── Core math / analysis ───────────────────────
    "eigenvalue", "eigenvalues", "eigenvector", "eigenvectors",
    "eigendecomposition", "eigenspace", "eigenspaces",
    "Hessian", "Jacobian", "Laplacian", "Hamiltonian",
    "bijective", "injective", "surjective", "bijection",
    "homeomorphism", "diffeomorphism", "isomorphism", "homomorphism",
    "codomain", "codomains", "preimage", "preimages",
    "supremum", "infimum", "extremum", "extrema",
    "antiderivative", "antiderivatives",
    "integrand", "integrands",
    "differentiable", "differentiability",
    "nondifferentiable",
    "piecewise",
    "monotonic", "monotonicity", "monotonically",
    "subspace", "subspaces", "subfield", "subgroup",
    "contrapositive", "contravariant", "covariant",
    "bilinear", "multilinear", "sesquilinear",
    "idempotent", "nilpotent", "involutory",
    "commutative", "commutativity", "noncommutative",
    "associative", "associativity",
    "distributive", "distributivity",
    "diagonalizable", "diagonalization", "diagonalize",
    "orthogonal", "orthogonality", "orthonormal",
    "orthogonalize", "orthogonalization",
    "determinantal",
    "invertible", "noninvertible",
    "nonsingular", "nondegenerate",
    "nonnegative", "nonpositive", "nontrivial", "nonzero", "nonlinear",
    "affine", "convex", "concave", "convexity", "concavity",
    "subgradient", "subgradients", "subdifferential",
    "semidefinite", "definiteness",
    "pseudoinverse",
    "quasiconvex", "quasiconcave",
    "equicontinuous",
    "pointwise", "uniformly",
    "parameterize", "parameterized", "parameterization", "parametric",
    "reparameterize", "reparameterized", "reparameterization",
    "discretize", "discretized", "discretization",
    "linearize", "linearized", "linearization",
    "factorize", "factorized", "factorization",
    "decomposable",
    "Hermitian",
    "Cartesian",

    # ── Calculus / analysis terms ──────────────────
    "asymptotics", "asymptotic", "asymptotically",
    "analytic", "analyticity",
    "holomorphic", "meromorphic",
    "solenoidal", "irrotational",
    "divergence", "rotational", "laplacian",
    "integrable", "integrability",
    "summable", "summability",
    "continuity",
    "discontinuity", "discontinuities",
    "removable",
    "subsequence", "subsequences", "subsequential",
    "superlinear", "sublinear", "superquadratic",
    "quadrature", "cubature",
    "interpolant", "interpolants",
    "interpolation", "extrapolation",
    "spline", "splines",
    "multivariate", "univariate", "bivariate",

    # ── Linear algebra ─────────────────────────────
    "eigenpair", "eigenpairs",
    "nullspace", "columnspace", "rowspace",
    "nullity",
    "Cholesky",
    "Householder",
    "Givens",
    "Schur",
    "LU", "QR", "SVD", "LDL",
    "Krylov",
    "tridiagonal", "bidiagonal", "pentadiagonal",
    "sparse", "sparsity",
    "backsubstitution",
    "pivoting",
    "vectorized", "vectorization",

    # ── Probability / statistics ───────────────────
    "stochastic", "stochastically",
    "iid",
    "pdf", "cdf", "pmf", "mgf", "pgf",
    "PDF", "CDF", "PMF", "MGF", "PGF",
    "Bayesian", "frequentist",
    "Bernoulli", "binomial", "multinomial",
    "Poisson", "Gaussian", "Laplace",
    "Dirichlet",
    "heteroscedastic", "homoscedastic",
    "heteroscedasticity", "homoscedasticity",
    "autocorrelation", "autocovariance", "autocorrelogram",
    "covariance", "covariances",
    "kurtosis", "skewness", "skew",
    "quantile", "quantiles", "quartile", "quartiles", "decile", "percentile",
    "estimator", "estimators",
    "unbiased", "biased", "bias",
    "likelihood", "loglikelihood",
    "posterior", "priori", "priors",
    "conjugate",
    "marginalize", "marginalization",
    "multicollinearity",
    "overdispersion", "underdispersion",
    "nonparametric", "semiparametric",

    # ── Differential equations ─────────────────────
    "ODE", "ODEs", "PDE", "PDEs", "SDE", "SDEs",
    "ODE's",
    "nonautonomous", "autonomous",
    "homogeneous", "inhomogeneous", "nonhomogeneous",
    "equilibria",
    "nullcline", "nullclines",
    "isocline", "isoclines",
    "bifurcation", "bifurcations",
    "linearizable",
    "Runge", "Kutta",
    "Euler", "Heun",

    # ── Series / approximation ─────────────────────
    "Taylor", "Maclaurin", "Laurent", "Fourier",
    "Lagrange", "Legendre", "Chebyshev", "Hermite", "Laguerre",
    "Pade",
    "convergent", "divergent",
    "conditionally",
    "truncation",
    "asymptotic",
    "Cauchy",
    "Weierstrass",
    "Abel",

    # ── Optimization ───────────────────────────────
    "unconstrained",
    "quasilinear",
    "Lagrangian",
    "Karush", "Kuhn", "Tucker", "KKT",
    "Hessian",
    "saddle",
    "feasible", "feasibility", "infeasible",
    "primal",
    "simplex",
    "subproblem", "subproblems",
    "Wolfe",
    "Armijo",
    "backtracking",
    "linesearch",

    # ── Transforms / operators ─────────────────────
    "Laplace", "Fourier", "Mellin", "Hilbert",
    "convolution", "convolutions", "convolve",
    "deconvolution",
    "autocorrelation",
    "spectrogram", "spectrograms",
    "bandpass", "highpass", "lowpass",
    "Nyquist",
    "aliasing",
    "DFT", "FFT", "IDFT", "IFFT",
    "DCT", "DST",

    # ── Abbreviations ─────────────────────────────
    "MSE", "RMSE", "MAE", "MLE", "MAP",
    "AIC", "BIC",
    "ARMA", "ARIMA", "ARIMAX", "GARCH",
    "VAR", "VECM",
    "GMM",
    "PCA", "ICA",
    "GLS", "OLS", "WLS",
    "CAS",
    "AST",
    "API", "APIs",
    "NaN", "Inf",
    "CLT", "LLN",
    "GPU", "CPU",
    "ML",
    "RHS", "LHS",
    "iff",
    "resp",
    "wrt",
    "viz",
    "WLOG",

    # ── Mathematician / scientist names ────────────
    "Leibniz", "Newton", "Gauss", "Riemann", "Bolzano",
    "Dirichlet", "Lebesgue", "Hilbert", "Banach", "Sobolev",
    "Hausdorff", "Minkowski", "Markov", "Kolmogorov",
    "Bayes", "Fermat", "Pascal", "Stirling",
    "Fibonacci", "Catalan",
    "Jacobi", "Frobenius", "Kronecker", "Cramer",
    "Hadamard", "Toeplitz", "Vandermonde",
    "Lyapunov", "Liouville", "Lotka", "Volterra",
    "Navier", "Stokes", "Bernoulli", "Poiseuille",
    "Boltzmann", "Planck", "Schrodinger",
    "Shannon", "Kullback", "Leibler",
    "Wiener", "Kalman",
    "Nash", "Pareto", "Stackelberg", "Cournot",
    "Kepler", "Lorentz", "Lorenz",
    "Arrhenius", "Michaelis", "Menten",
    "Hooke", "Rayleigh",
    "Bourbaki", "Dedekind", "Cantor",
    "Turing", "Church",
    "Alonzo",
    "Macsyma", "Mathematica", "SymPy",
    "Wolfram",

    # ── CS / programming ───────────────────────────
    "TypeScript", "JavaScript", "Python",
    "runtime", "runtimes",
    "codebase", "codebases",
    "composable",
    "accessor", "accessors",
    "iterable", "iterables", "iterator", "iterators",
    "memoize", "memoized", "memoization",
    "callback", "callbacks",
    "namespace", "namespaces",
    "struct", "structs",
    "enum", "enums",
    "tuple", "tuples",
    "variadic",
    "polymorphic", "polymorphism",
    "monomorphic",
    "readonly",
    "nullable",
    "boolean", "booleans",
    "bigint",
    "linting",
    "formatter",
    "tokenizer", "tokenize",
    "lexer", "parser",
    "AST",
    "webpack", "rollup", "esbuild",
    "npm", "npx",

    # ── Library / project specific ─────────────────
    "Evenwicht", "leibniz",
    "Expr",
    "Maastricht",

    # ── Application domains ────────────────────────
    "pharmacokinetic", "pharmacokinetics", "pharmacodynamic",
    "bioavailability",
    "epidemiological", "epidemiology",
    "seismology", "seismological", "seismograph",
    "cosmological", "cosmology",
    "astrophysics", "astrophysical",
    "thermodynamic", "thermodynamics",
    "electrodynamics", "electrostatic", "electrostatics",
    "magnetohydrodynamic", "magnetohydrodynamics",
    "semiconductor", "semiconductors",
    "photovoltaic", "photovoltaics",
    "genomic", "genomics", "proteomics",
    "allele", "alleles",
    "genotype", "genotypes", "phenotype", "phenotypes",
    "diploid", "haploid", "polyploid",
    "cryptocurrency", "blockchain",
    "cryptographic", "cryptography",
    "ciphertext", "plaintext",

    # ── Physics / engineering ──────────────────────
    "kinematic", "kinematics",
    "viscosity", "viscous", "inviscid",
    "incompressible", "compressible",
    "turbulence", "turbulent", "laminar",
    "vorticity", "vortex", "vortices",
    "waveguide", "waveguides",
    "inductance", "capacitance", "impedance", "admittance",
    "resistor", "capacitor", "inductor",
    "transistor", "transistors",
    "actuator", "actuators",
    "servomechanism",
    "flywheel",
    "perihelion", "aphelion", "perigee", "apogee",
    "eccentricity",
    "interferometer", "interferometry",
    "refraction", "diffraction",

    # ── Miscellaneous technical ────────────────────
    "workflow", "workflows",
    "dataset", "datasets",
    "datapoint", "datapoints",
    "preprocessing", "postprocessing",
    "lookup", "lookups",
    "timestep", "timesteps",
    "timescale", "timescales",
    "tradeoff", "tradeoffs",
    "linearizable",
    "discretizable",
    "equidistant",
    "pairwise",
    "elementwise",
    "componentwise",
    "entrywise",
    "coordinatewise",
    "blockwise",
    "rowwise", "columnwise",
    "sigmoid", "softmax", "relu",
    "backpropagation", "backpropagate",
    "feedforward",
    "recurrent",
    "overfitting", "underfitting", "overfit", "underfit",
    "regularization", "regularize", "regularized", "regularizer",
    "hyperparameter", "hyperparameters",
    "minibatch",
    "heatmap", "heatmaps",
    "scatterplot", "scatterplots",
    "boxplot", "boxplots",
    "stylesheet",
    "renderer",
    "tooltip", "tooltips",

    # ── Textbook / documentation terms ─────────────
    "textbook", "textbooks",
    "prerequisite", "prerequisites",
    "subsection", "subsections",
    "walkthrough", "walkthroughs",
    "pseudocode",
    "Appendix",
    "errata",
    "frontmatter",
    "backmatter",

    # ── Special functions / named functions ────────
    "erf", "erfc", "erfi",
    "digamma", "trigamma", "polygamma",
    "loggamma", "logbeta",
    "zeta",
    "Pochhammer",
    "fallingfactorial", "generalizedbinomial",

    # ── Numeric / computation ──────────────────────
    "precompute", "precomputed", "precomputation",
    "recompute", "recomputed",
    "sqrt", "cbrt",
    "ldexp",
    "denormalized", "subnormal",
    "roundoff",
    "mantissa",
    "ulp",
    "flop", "flops",

    # ── Additional scientist / author names ────────
    "Abramowitz", "Stegun",
    "Letnikov", "Grunwald",
    "Lanczos",
    "Nwald",
    "SciPy", "scipy",
    "NumPy", "numpy",
    "MATLAB", "Octave",

    # ── Web / JS / tooling terms ───────────────────
    "js", "ts",
    "webworker", "webworkers",
    "filesystem", "filesystems",
    "etc",

    # ── Additional math / analysis terms ───────────
    "subexpression", "subexpressions",
    "unary", "ternary", "nary",
    "multi",
    "antidifferentiation",
    "pdfs", "cdfs", "pmfs",
    "behaviour", "behaviours",

    # ── L'Hopital and related ──────────────────────
    "pital", "Hopital",

    # ── British English spellings ──────────────────
    "colour", "colours", "coloured", "colouring",
    "behaviour", "behaviours", "behavioural",
    "centre", "centres", "centred", "centring",
    "programme", "programmes", "programmed", "programming",
    "labour", "labours", "laboured", "labourer",
    "honour", "honours", "honoured",
    "favour", "favours", "favoured",
    "neighbour", "neighbours", "neighbouring",
    "organisation", "organisations", "organised", "organising",
    "realise", "realised", "realising",
    "recognise", "recognises", "recognised", "recognising",
    "optimise", "optimised", "optimising", "optimises",
    "normalise", "normalised", "normalising", "normalises",
    "minimise", "minimised", "minimising", "minimises",
    "maximise", "maximised", "maximising", "maximises",
    "initialise", "initialised", "initialising", "initialises",
    "generalise", "generalised", "generalising", "generalises",
    "specialise", "specialised", "specialising", "specialises",
    "characterise", "characterised", "characterising", "characterises",
    "penalise", "penalised", "penalising", "penalises",
    "stabilise", "stabilised", "stabilising", "stabilises",
    "circularise", "circularised",
    "popularise", "popularised",
    "residualise", "residualised",
    "analyse", "analysed", "analysing", "analyses",
    "modelling", "modelled",
    "travelling", "travelled", "traveller",
    "signalling", "signalled",
    "labelling", "labelled",
    "cancelling", "cancelled",
    "optimisation", "optimisations",
    "minimisation", "maximisation",
    "normalisation", "initialisations", "initialisation",
    "generalisation", "generalisations",
    "specialisation", "specialisations",
    "characterisation", "characterisations",
    "penalisation", "stabilisation",
    "recognistion",
    "grey", "greys",
    "defence", "defences",
    "licence", "licences",
    "practise", "practised", "practising",
    "enquiry", "enquiries",
    "glamour", "vigour", "valour", "vapour",
    "fibre", "fibres",
    "litre", "litres",
    "metre", "metres", "centimetre", "centimetres", "kilometre", "kilometres",
    "sceptic", "sceptical", "scepticism",
    "catalogue", "catalogues",
    "analogue", "analogues",
    "dialogue", "dialogues",
]))


def load_custom_dict() -> set[str]:
    """Load the custom dictionary, creating it with defaults if missing."""
    if not DICT_PATH.exists():
        save_custom_dict(set(DEFAULT_TERMS))
    words: set[str] = set()
    for line in DICT_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            words.add(stripped)
    return words


def save_custom_dict(words: set[str]) -> None:
    """Save the custom dictionary sorted alphabetically."""
    header = (
        "# Custom dictionary for Evenwicht documentation spell checker.\n"
        "# One word per line.  Lines starting with # are comments.\n"
        "# Add words with:  python3 scripts/verify-spelling.py --add-word WORD\n"
        "#\n"
    )
    body = "\n".join(sorted(words, key=str.lower))
    DICT_PATH.write_text(header + body + "\n", encoding="utf-8")


def add_word(word: str) -> None:
    """Add a word to the custom dictionary."""
    words = load_custom_dict()
    if word in words:
        print(f"'{word}' is already in the custom dictionary.")
        return
    words.add(word)
    save_custom_dict(words)
    print(f"Added '{word}' to {DICT_PATH}")


# ── Spell checking ────────────────────────────────

def check_files(files: list[Path]) -> dict[str, list[tuple[str, int]]]:
    """Check all files and return {misspelled_word: [(file, line), ...]}."""
    try:
        from spellchecker import SpellChecker
    except ImportError:
        print("ERROR: pyspellchecker is not installed.", file=sys.stderr)
        print("  Install with: pip3 install pyspellchecker", file=sys.stderr)
        sys.exit(1)

    spell = SpellChecker()

    # Load custom dictionary words into the spell checker
    custom_words = load_custom_dict()
    # Add lowercase versions so the checker recognises them
    known_additions = set()
    for w in custom_words:
        known_additions.add(w.lower())
        known_additions.add(w)
    spell.word_frequency.load_words(known_additions)

    # Keep a case-sensitive whitelist for proper nouns / acronyms
    whitelist_exact: set[str] = custom_words

    # Mapping: lowered misspelled word -> [(file_display, line_no), ...]
    issues: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for filepath in files:
        rel = filepath.relative_to(PROJECT_ROOT)
        text = filepath.read_text(encoding="utf-8")
        cleaned_lines = strip_markup(text)

        for lineno, cleaned in cleaned_lines:
            words = extract_words(cleaned)
            for word in words:
                # Skip if in exact whitelist (case-sensitive)
                if word in whitelist_exact:
                    continue
                # Skip ALL-CAPS words (likely acronyms)
                if word.isupper() and len(word) <= 6:
                    continue
                # Skip single letters
                if len(word) <= 1:
                    continue
                # Check with spell checker (case-insensitive)
                if spell.unknown([word.lower()]):
                    key = word.lower()
                    issues[key].append((str(rel), lineno))

    return dict(issues)


def format_report(
    issues: dict[str, list[tuple[str, int]]],
    files_checked: int,
) -> str:
    """Format the spell-check results into a human-readable report."""
    try:
        from spellchecker import SpellChecker
    except ImportError:
        return "ERROR: pyspellchecker not available."

    spell = SpellChecker()

    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("  SPELLING VERIFICATION REPORT")
    lines.append("=" * 70)
    lines.append(f"  Files checked: {files_checked}")
    lines.append(f"  Unique misspellings found: {len(issues)}")
    total_occurrences = sum(len(locs) for locs in issues.values())
    lines.append(f"  Total occurrences: {total_occurrences}")
    lines.append("=" * 70)

    if not issues:
        lines.append("")
        lines.append("  No misspellings found.  All clear!")
        lines.append("")
        return "\n".join(lines)

    lines.append("")

    # Sort by number of occurrences (most frequent first), then alphabetically
    sorted_words = sorted(issues.keys(), key=lambda w: (-len(issues[w]), w))

    for word in sorted_words:
        locations = issues[word]
        corrections = spell.candidates(word)
        # Remove the word itself from suggestions
        if corrections:
            corrections = sorted(corrections - {word})[:5]
        suggestion_str = ", ".join(corrections) if corrections else "(no suggestions)"

        lines.append(f"  {word}  ({len(locations)} occurrence{'s' if len(locations) != 1 else ''})")
        lines.append(f"    Suggestions: {suggestion_str}")
        # Show up to 5 locations
        shown = locations[:5]
        for filepath, lineno in shown:
            lines.append(f"      {filepath}:{lineno}")
        if len(locations) > 5:
            lines.append(f"      ... and {len(locations) - 5} more")
        lines.append("")

    lines.append("-" * 70)
    lines.append("  To add a word to the custom dictionary:")
    lines.append("    python3 scripts/verify-spelling.py --add-word WORD")
    lines.append("-" * 70)

    return "\n".join(lines)


# ── American spelling detection ───────────────────

# Known book/paper titles that use American spelling (exempt from flagging)
_AMERICAN_TITLE_EXEMPTIONS = frozenset([
    "convex optimization",
    "numerical optimization",
    "bayesian optimization",
    "dynamic programming and optimal control",
    "the nature of statistical learning theory",
    "pattern recognition and machine learning",
    "reinforcement learning",
    "information theory learning and inference algorithms",
    # Computer science books with "Programs" in the official title
    "structure and interpretation of computer programs",
    "the art of computer programming",
])

# American → British mapping (word-level, case-insensitive keys, case-preserved output)
_AMERICAN_BRITISH = {
    # -ize → -ise
    "optimize": "optimise",
    "optimizes": "optimises",
    "optimized": "optimised",
    "optimizing": "optimising",
    "normalize": "normalise",
    "normalizes": "normalises",
    "normalized": "normalised",
    "normalizing": "normalising",
    "unnormalized": "unnormalised",
    "renormalize": "renormalise",
    "minimize": "minimise",
    "minimizes": "minimises",
    "minimized": "minimised",
    "minimizing": "minimising",
    "maximize": "maximise",
    "maximizes": "maximises",
    "maximized": "maximised",
    "maximizing": "maximising",
    "initialize": "initialise",
    "initializes": "initialises",
    "initialized": "initialised",
    "initializing": "initialising",
    "generalize": "generalise",
    "generalizes": "generalises",
    "generalized": "generalised",
    "generalizing": "generalising",
    "specialize": "specialise",
    "specializes": "specialises",
    "specialized": "specialised",
    "specializing": "specialising",
    "characterize": "characterise",
    "characterizes": "characterises",
    "characterized": "characterised",
    "characterizing": "characterising",
    "penalize": "penalise",
    "penalizes": "penalises",
    "penalized": "penalised",
    "penalizing": "penalising",
    "stabilize": "stabilise",
    "stabilizes": "stabilises",
    "stabilized": "stabilised",
    "stabilizing": "stabilising",
    "circularize": "circularise",
    "popularize": "popularise",
    "residualized": "residualised",
    "recognize": "recognise",
    "recognizes": "recognises",
    "recognized": "recognised",
    "recognizing": "recognising",
    "organization": "organisation",
    "organizations": "organisations",
    "organized": "organised",
    "organize": "organise",
    # -or → -our
    "color": "colour",
    "colors": "colours",
    "colored": "coloured",
    "center": "centre",
    "centers": "centres",
    "centered": "centred",
    "behavior": "behaviour",
    "behaviors": "behaviours",
    # double-l
    "modeling": "modelling",
    "modeled": "modelled",
    "traveling": "travelling",
    "traveled": "travelled",
    "signaling": "signalling",
    "signaled": "signalled",
    "labeling": "labelling",
    "labeled": "labelled",
    "totaling": "totalling",
    "totaled": "totalled",
    "canceling": "cancelling",
    "canceled": "cancelled",
    # programme
    "program": "programme",  # only non-computing contexts — flagged as warning
    "programs": "programmes",
}

_RE_ITALIC = re.compile(r"\*([^*\n]+)\*")


def check_american_spellings(
    files: list[Path],
) -> dict[str, list[tuple[str, int, str]]]:
    """Check prose for American spellings that should be British.

    Returns {american_word: [(file, lineno, british_equivalent), ...]}
    """
    issues: dict[str, list[tuple[str, int, str]]] = defaultdict(list)

    for filepath in files:
        rel = filepath.relative_to(PROJECT_ROOT)
        text = filepath.read_text(encoding="utf-8")
        original_lines = text.split("\n")
        cleaned_lines = strip_markup(text)

        for lineno, cleaned in cleaned_lines:
            # Skip short/empty lines
            if not cleaned.strip():
                continue

            # Extract italic spans from the ORIGINAL line (before markup stripping)
            # so that bold/italic markers are still present for matching.
            original_line = original_lines[lineno - 1] if lineno - 1 < len(original_lines) else ""
            italic_texts = {m.group(1).lower() for m in _RE_ITALIC.finditer(original_line)}
            is_exempt_line = any(
                exemption in " ".join(italic_texts)
                for exemption in _AMERICAN_TITLE_EXEMPTIONS
            )
            if is_exempt_line:
                continue

            words = extract_words(cleaned)
            for word in words:
                lower = word.lower()
                if lower in _AMERICAN_BRITISH:
                    british = _AMERICAN_BRITISH[lower]
                    # Preserve original capitalisation
                    if word[0].isupper() and not word.isupper():
                        british = british[0].upper() + british[1:]
                    key = lower
                    issues[key].append((str(rel), lineno, british))

    return dict(issues)


def format_american_report(
    issues: dict[str, list[tuple[str, int, str]]],
    files_checked: int,
) -> str:
    """Format American spelling issues into a human-readable report."""
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("  BRITISH SPELLING VERIFICATION REPORT")
    lines.append("=" * 70)
    lines.append(f"  Files checked: {files_checked}")
    lines.append(f"  American spellings found: {len(issues)}")
    total = sum(len(v) for v in issues.values())
    lines.append(f"  Total occurrences: {total}")
    lines.append("=" * 70)

    if not issues:
        lines.append("")
        lines.append("  No American spellings found.  All British!")
        lines.append("")
        return "\n".join(lines)

    lines.append("")
    for word in sorted(issues.keys(), key=lambda w: -len(issues[w])):
        locs = issues[word]
        british = locs[0][2]
        lines.append(f"  {word!r} → '{british}'  ({len(locs)} occurrence{'s' if len(locs) != 1 else ''})")
        for path, lineno, _ in locs[:5]:
            lines.append(f"      {path}:{lineno}")
        if len(locs) > 5:
            lines.append(f"      ... and {len(locs) - 5} more")
        lines.append("")

    lines.append("-" * 70)
    lines.append("  Fix: replace American spellings with British equivalents.")
    lines.append("-" * 70)
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify spelling across Evenwicht documentation.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Only check the first 3 chapter files (for testing).",
    )
    parser.add_argument(
        "--add-word",
        metavar="WORD",
        help="Add a word to the custom dictionary and exit.",
    )
    args = parser.parse_args()

    if args.add_word:
        add_word(args.add_word)
        return

    files = discover_files(quick=args.quick)
    if not files:
        print("No files found to check.", file=sys.stderr)
        sys.exit(1)

    mode = "QUICK MODE (3 files)" if args.quick else "full scan"
    print(f"Checking spelling ({mode}) ...")
    for f in files:
        print(f"  {f.relative_to(PROJECT_ROOT)}")

    issues = check_files(files)
    report = format_report(issues, len(files))
    print()
    print(report)

    american_issues = check_american_spellings(files)
    american_report = format_american_report(american_issues, len(files))
    print()
    print(american_report)

    if issues or american_issues:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
