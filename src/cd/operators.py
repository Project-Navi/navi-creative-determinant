"""
Discrete Laplacian operators for the Creative Determinant framework.

Provides sparse matrix constructors for -Δ with Dirichlet boundary conditions
in 1D and 2D domains.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, diags, eye, kron

from ._validation import check_positive_int, check_positive_scalar


def laplacian_1d_dirichlet(N: int, L: float) -> tuple[csr_matrix, float]:
    """
    Construct sparse matrix for -d²/dx² on (0, L) with Dirichlet BC.

    Parameters
    ----------
    N : int
        Number of interior grid points (``N >= 1``).
    L : float
        Domain length (``L > 0``).

    Returns
    -------
    A : scipy.sparse.csr_matrix
        Sparse N×N matrix representing -d²/dx².
    h : float
        Grid spacing ``L / (N + 1)``.

    Raises
    ------
    ValueError
        If ``N`` is not a positive integer or ``L`` is not a positive finite number.

    Notes
    -----
    Uses standard second-order centered differences:
        -Φ''(xᵢ) ≈ (-Φᵢ₋₁ + 2Φᵢ - Φᵢ₊₁) / h²

    Boundary conditions Φ(0) = Φ(L) = 0 are encoded implicitly
    by only solving for interior points: the first and last rows see a single
    interior neighbour and the (zero) boundary value.

    The exact principal eigenvalue of ``A`` is ``(4/h²) sin²(πh/(2L))``, which tends to
    ``(π/L)²`` at second order in ``h``.

    Example
    -------
    >>> A, h = laplacian_1d_dirichlet(100, 1.0)
    >>> A.shape
    (100, 100)
    """
    N = check_positive_int("N", N)
    L = check_positive_scalar("L", L)
    h = L / (N + 1)
    if N == 1:
        return csr_matrix(np.array([[2.0 / h**2]])), h
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

    Raises
    ------
    ValueError
        If a grid size is not a positive integer or a length is not positive and finite.

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
    Nx = check_positive_int("Nx", Nx)
    Ny = check_positive_int("Ny", Ny)
    Lx = check_positive_scalar("Lx", Lx)
    Ly = check_positive_scalar("Ly", Ly)
    hx = Lx / (Nx + 1)
    hy = Ly / (Ny + 1)

    # 1D Laplacians
    Ax, _ = laplacian_1d_dirichlet(Nx, Lx)
    Ay, _ = laplacian_1d_dirichlet(Ny, Ly)

    # Identity matrices
    Ix = eye(Nx, format="csr")
    Iy = eye(Ny, format="csr")

    # 2D Laplacian via Kronecker products
    A = (kron(Iy, Ax) + kron(Ay, Ix)).tocsr()

    return A, hx, hy


def laplacian_3d_dirichlet(
    Nx: int, Ny: int, Nz: int, Lx: float, Ly: float, Lz: float
) -> tuple[csr_matrix, float, float, float]:
    """
    Construct sparse matrix for -Δ on (0,Lx) × (0,Ly) × (0,Lz) with Dirichlet BC.

    Parameters
    ----------
    Nx, Ny, Nz : int
        Number of interior grid points in each direction.
    Lx, Ly, Lz : float
        Domain lengths.

    Returns
    -------
    A : scipy.sparse.csr_matrix
        Sparse (Nx*Ny*Nz) × (Nx*Ny*Nz) matrix representing -Δ.
    hx, hy, hz : float
        Grid spacings.

    Notes
    -----
    **Array convention.** The flat unknown index is ``(iz * Ny + iy) * Nx + ix``: x varies
    fastest, then y, then z. Interior arrays therefore have shape ``(Nz, Ny, Nx)`` and full
    grids ``(Nz+2, Ny+2, Nx+2)``; ``grid_3d`` returns coordinate arrays in that layout, and
    ``field[1:-1, 1:-1, 1:-1].reshape(-1)`` is the matching flattening. A ``(Ny, Nx, Nz)``
    array (the layout of ``np.meshgrid(x, y, z, indexing="xy")``) is *not* compatible; for
    unequal sizes it is rejected by shape, for equal sizes it silently permutes the axes,
    so build fields from ``grid_3d``.

    Kronecker structure with x fastest:
        -Δ = Iz ⊗ Iy ⊗ Ax + Iz ⊗ Ay ⊗ Ix + Az ⊗ Iy ⊗ Ix
    """
    Nx = check_positive_int("Nx", Nx)
    Ny = check_positive_int("Ny", Ny)
    Nz = check_positive_int("Nz", Nz)
    Lx = check_positive_scalar("Lx", Lx)
    Ly = check_positive_scalar("Ly", Ly)
    Lz = check_positive_scalar("Lz", Lz)
    Ax, hx = laplacian_1d_dirichlet(Nx, Lx)
    Ay, hy = laplacian_1d_dirichlet(Ny, Ly)
    Az, hz = laplacian_1d_dirichlet(Nz, Lz)
    Ix = eye(Nx, format="csr")
    Iy = eye(Ny, format="csr")
    Iz = eye(Nz, format="csr")
    A = (kron(kron(Iz, Iy), Ax) + kron(kron(Iz, Ay), Ix) + kron(kron(Az, Iy), Ix)).tocsr()
    return A, hx, hy, hz


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
    N = check_positive_int("N", N)
    L = check_positive_scalar("L", L)
    return np.linspace(0, L, N + 2)


def grid_3d(
    Nx: int, Ny: int, Nz: int, Lx: float, Ly: float, Lz: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate 3D coordinate arrays including boundary points, in the ``(z, y, x)`` layout of
    ``laplacian_3d_dirichlet``.

    Returns
    -------
    Z, Y, X : ndarray
        Arrays of shape ``(Nz+2, Ny+2, Nx+2)`` with ``X[k, j, i] = x_i``, ``Y[k, j, i] = y_j``,
        ``Z[k, j, i] = z_k``.
    """
    x = grid_1d(Nx, Lx)
    y = grid_1d(Ny, Ly)
    z = grid_1d(Nz, Lz)
    Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
    return Z, Y, X
