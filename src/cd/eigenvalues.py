"""
Eigenvalue computations for the Creative Determinant framework.

Provides tools for computing the principal eigenvalue λ₁(-Δ - βb; M),
which determines the viability threshold for presence emergence.

Key result (Theorem 3.16 in paper):
    Nontrivial solutions exist when λ₁ < 0.
"""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh

from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet


def principal_eigenvalue_1d(
    N: int,
    L: float,
    beta_b: float,
) -> float:
    """
    Compute principal eigenvalue of (-Δ - βb) on (0, L) with Dirichlet BC.

    For constant b, the analytic result is:
        λ₁ = (π/L)² - βb

    Parameters
    ----------
    N : int
        Number of interior grid points.
    L : float
        Domain length.
    beta_b : float
        Product of viability gain β and potential b (assumed constant).

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue.

    Notes
    -----
    The viability threshold occurs at β* where λ₁ = 0:
        β* = (π/L)² / b

    - λ₁ > 0: Below threshold → only trivial solution Φ ≡ 0
    - λ₁ < 0: Above threshold → nontrivial presence emerges

    Example
    -------
    >>> L, b = 1.0, 0.8
    >>> beta_star = (np.pi / L)**2 / b  # ≈ 12.34
    >>> principal_eigenvalue_1d(400, L, 0.8 * beta_star * b)  # > 0
    >>> principal_eigenvalue_1d(400, L, 1.2 * beta_star * b)  # < 0
    """
    A, _ = laplacian_1d_dirichlet(N, L)

    # Form operator -Δ - βb·I
    M = A - beta_b * diags([np.ones(N)], [0], format="csr")

    # Compute smallest eigenvalue
    lam, _ = eigsh(M, k=1, which="SA")
    return float(lam[0])


def principal_eigenvalue_2d(
    Nx: int,
    Ny: int,
    Lx: float,
    Ly: float,
    beta_b: float,
) -> float:
    """
    Compute principal eigenvalue of (-Δ - βb) on rectangle with Dirichlet BC.

    For constant b on [0,Lx] × [0,Ly], the analytic result is:
        λ₁ = π²(1/Lx² + 1/Ly²) - βb

    Parameters
    ----------
    Nx, Ny : int
        Number of interior grid points in each direction.
    Lx, Ly : float
        Domain lengths.
    beta_b : float
        Product of viability gain β and potential b (assumed constant).

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue.
    """
    A, _, _ = laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)
    n = Nx * Ny

    # Form operator -Δ - βb·I
    M = A - beta_b * diags([np.ones(n)], [0], format="csr")

    # Compute smallest eigenvalue
    lam, _ = eigsh(M, k=1, which="SA")
    return float(lam[0])


def viability_threshold_1d(L: float, b: float) -> float:
    """
    Compute critical viability gain β* for 1D domain.

    Parameters
    ----------
    L : float
        Domain length.
    b : float
        Mean viability potential (assumed constant).

    Returns
    -------
    beta_star : float
        Critical value where λ₁ = 0.

    Notes
    -----
    β* = (π/L)² / b

    For β < β*: trivial solution only
    For β > β*: nontrivial presence emerges
    """
    return (np.pi / L) ** 2 / b


def viability_threshold_2d(Lx: float, Ly: float, b: float) -> float:
    """
    Compute critical viability gain β* for 2D rectangular domain.

    Parameters
    ----------
    Lx, Ly : float
        Domain lengths.
    b : float
        Mean viability potential (assumed constant).

    Returns
    -------
    beta_star : float
        Critical value where λ₁ = 0.
    """
    return np.pi**2 * (1 / Lx**2 + 1 / Ly**2) / b
