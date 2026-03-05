"""
Discrete Laplacian operators for the Creative Determinant framework.

Provides sparse matrix constructors for -Δ with Dirichlet boundary conditions
in 1D and 2D domains.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, diags, eye, kron


def laplacian_1d_dirichlet(N: int, L: float) -> tuple[csr_matrix, float]:
    """
    Construct sparse matrix for -d²/dx² on (0, L) with Dirichlet BC.

    Parameters
    ----------
    N : int
        Number of interior grid points.
    L : float
        Domain length.

    Returns
    -------
    A : scipy.sparse.csr_matrix
        Sparse N×N matrix representing -d²/dx².
    h : float
        Grid spacing.

    Notes
    -----
    Uses standard second-order centered differences:
        -Φ''(xᵢ) ≈ (-Φᵢ₋₁ + 2Φᵢ - Φᵢ₊₁) / h²

    Boundary conditions Φ(0) = Φ(L) = 0 are encoded implicitly
    by only solving for interior points.

    Example
    -------
    >>> A, h = laplacian_1d_dirichlet(100, 1.0)
    >>> A.shape
    (100, 100)
    """
    h = L / (N + 1)
    main = 2.0 * np.ones(N) / h**2
    off = -1.0 * np.ones(N - 1) / h**2
    A = diags([off, main, off], offsets=[-1, 0, 1], format="csr")
    return A, h


def laplacian_2d_dirichlet(
    Nx: int, Ny: int, Lx: float, Ly: float
) -> tuple[csr_matrix, float, float]:
    """
    Construct sparse matrix for -Δ on (0,Lx) × (0,Ly) with Dirichlet BC.

    Parameters
    ----------
    Nx : int
        Number of interior grid points in x-direction.
    Ny : int
        Number of interior grid points in y-direction.
    Lx : float
        Domain length in x-direction.
    Ly : float
        Domain length in y-direction.

    Returns
    -------
    A : scipy.sparse.csr_matrix
        Sparse (Nx*Ny) × (Nx*Ny) matrix representing -Δ.
    hx : float
        Grid spacing in x-direction.
    hy : float
        Grid spacing in y-direction.

    Notes
    -----
    Uses Kronecker product structure:
        -Δ = -∂²/∂x² ⊗ Iᵧ - Iₓ ⊗ ∂²/∂y²

    Interior unknowns are ordered row-wise (x varies fastest).

    Example
    -------
    >>> A, hx, hy = laplacian_2d_dirichlet(50, 50, 1.0, 1.0)
    >>> A.shape
    (2500, 2500)
    """
    hx = Lx / (Nx + 1)
    hy = Ly / (Ny + 1)

    # 1D Laplacians
    Ax, _ = laplacian_1d_dirichlet(Nx, Lx)
    Ay, _ = laplacian_1d_dirichlet(Ny, Ly)

    # Identity matrices
    Ix = eye(Nx, format="csr")
    Iy = eye(Ny, format="csr")

    # 2D Laplacian via Kronecker products
    A = kron(Iy, Ax) + kron(Ay, Ix)

    return A, hx, hy


def grid_1d(N: int, L: float) -> np.ndarray:
    """
    Generate 1D grid including boundary points.

    Parameters
    ----------
    N : int
        Number of interior points.
    L : float
        Domain length.

    Returns
    -------
    x : ndarray
        Array of N+2 points from 0 to L (inclusive).
    """
    return np.linspace(0, L, N + 2)


def grid_2d(Nx: int, Ny: int, Lx: float, Ly: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate 2D meshgrid including boundary points.

    Parameters
    ----------
    Nx, Ny : int
        Number of interior points in each direction.
    Lx, Ly : float
        Domain lengths.

    Returns
    -------
    X, Y : ndarray
        Meshgrid arrays of shape (Ny+2, Nx+2).
    """
    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    return np.meshgrid(x, y)
