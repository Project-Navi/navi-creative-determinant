"""
Creative Determinant (CD) - A Field Theory of Coherence and Meaning

This package provides numerical tools for studying the Creative Determinant
PDE framework: nonlinear elliptic equations modeling presence emergence
on semiotic manifolds, and the finite-graph model checked in Lean.

Core equation (V1'):
    -ΔΦ = a(x)|∇Φ| + q(x)Φ - c(x)(Φ₊)ᵖ,  Φ|∂M = 0

Where:
    - Φ(x): presence field (intensity of coherent presence)
    - a(x) = κγμ: creative drive (care × coherence × contradiction), values in [0, 1]
    - q(x) = βb(x): effective viability potential; b = κγ - λμ under canonical closure,
      β a dimensionless gain (β = 1 recovers the paper's base equation)
    - c(x) >= c₀ > 0: saturation / carrying capacity
    - p > 1: saturation exponent

Key results (status labelled as in the paper):
    - Theorem 3.16 (classical proof in the paper): λ₁(-Δ - q; M) < 0 implies a solution
      positive in the interior. The Lean statement of this theorem is conditional on the
      `PDEInfra` interface; the finite-graph analogue `SemioticGraph.exists_pos_graph` is
      proved outright in Lean and implemented in `cd.graph`.
    - Proposition (a ≡ 0): λ₁ < 0 is also necessary, so the threshold is exact in that regime.
"""

from .analysis import (
    check_convergence,
    classify_branch,
    linfty_bound,
    presence_statistics,
    residual_1d,
    residual_2d,
    solution_type,
    trapezoid_weights,
)
from .eigenvalues import (
    principal_eigenpair_1d,
    principal_eigenpair_2d,
    principal_eigenvalue_1d,
    principal_eigenvalue_1d_spatial,
    principal_eigenvalue_2d,
    principal_eigenvalue_2d_spatial,
    viability_threshold_1d,
    viability_threshold_2d,
)
from .fields import creative_drive, gaussian_bump_1d, gaussian_bump_2d, viability_canonical
from .graph import SemioticGraph, linfty_bound_graph, solve_graph, triangle
from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet
from .solvers import barriers_1d, solve_1d_picard, solve_2d_picard

__version__ = "0.1.0"
__author__ = "Nelson Spence"
__email__ = "nelson@projectnavi.ai"

__all__ = [
    # Operators
    "laplacian_1d_dirichlet",
    "laplacian_2d_dirichlet",
    # Eigenvalues
    "principal_eigenvalue_1d",
    "principal_eigenvalue_1d_spatial",
    "principal_eigenvalue_2d",
    "principal_eigenvalue_2d_spatial",
    "principal_eigenpair_1d",
    "principal_eigenpair_2d",
    "viability_threshold_1d",
    "viability_threshold_2d",
    # Solvers
    "solve_1d_picard",
    "solve_2d_picard",
    "barriers_1d",
    # Finite-graph lane
    "SemioticGraph",
    "triangle",
    "solve_graph",
    "linfty_bound_graph",
    # Analysis
    "residual_1d",
    "residual_2d",
    "check_convergence",
    "solution_type",
    "classify_branch",
    "presence_statistics",
    "trapezoid_weights",
    "linfty_bound",
    # Fields
    "viability_canonical",
    "creative_drive",
    "gaussian_bump_1d",
    "gaussian_bump_2d",
]
