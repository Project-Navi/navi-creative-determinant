"""
Creative Determinant (CD) - A Field Theory of Coherence and Meaning

This package provides numerical tools for studying the Creative Determinant
PDE framework: nonlinear elliptic equations modeling presence emergence
on semiotic manifolds.

Core equation (V1'):
    -ΔΦ = a(x)|∇Φ| + βb(x)Φ - c(x)Φᵖ,  Φ|∂M = 0

Where:
    - Φ(x): presence field (intensity of coherent presence)
    - a(x) = κγμ: creative drive (care × coherence × contradiction)
    - b(x) = κγ - λμ: viability potential (canonical closure)
    - c(x): saturation/carrying capacity
    - β: viability gain parameter
    - p > 1: saturation exponent

Key result (Theorem 3.16): Nontrivial solutions exist when λ₁(-Δ - βb; M) < 0
"""

from .analysis import check_convergence, residual_1d, solution_type
from .eigenvalues import (
    principal_eigenvalue_1d,
    principal_eigenvalue_2d,
    viability_threshold_1d,
    viability_threshold_2d,
)
from .fields import creative_drive, gaussian_bump_2d, viability_canonical
from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet
from .solvers import solve_1d_picard, solve_2d_picard

__version__ = "0.1.0"
__author__ = "Nelson Spence"
__email__ = "nelson@projectnavi.ai"

__all__ = [
    # Operators
    "laplacian_1d_dirichlet",
    "laplacian_2d_dirichlet",
    # Eigenvalues
    "principal_eigenvalue_1d",
    "principal_eigenvalue_2d",
    "viability_threshold_1d",
    "viability_threshold_2d",
    # Solvers
    "solve_1d_picard",
    "solve_2d_picard",
    # Analysis
    "residual_1d",
    "check_convergence",
    "solution_type",
    # Fields
    "viability_canonical",
    "creative_drive",
    "gaussian_bump_2d",
]
