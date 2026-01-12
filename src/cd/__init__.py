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

Key result: Nontrivial solutions exist iff λ₁(-Δ - βb; M) < 0
"""

from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet
from .eigenvalues import principal_eigenvalue_1d, principal_eigenvalue_2d
from .solvers import solve_1d_picard, solve_2d_picard
from .analysis import residual_1d, check_convergence
from .fields import viability_canonical, gaussian_bump_2d

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
    # Solvers
    "solve_1d_picard",
    "solve_2d_picard",
    # Analysis
    "residual_1d",
    "check_convergence",
    # Fields
    "viability_canonical",
    "gaussian_bump_2d",
]
