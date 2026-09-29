"""
Eigenvalue computations for the Creative Determinant framework.

Provides the principal Dirichlet eigenvalue λ₁(-Δ - q; M) of the finite-difference operator,
its positive eigenvector, and the constant-coefficient viability threshold.

Mathematical status
-------------------
* For constant q on (0, L) the *discrete* principal eigenvalue is exactly
  ``(4/h²) sin²(πh/(2L)) - q`` and converges to ``(π/L)² - q`` at second order (Theorem: this is
  a closed-form fact about the tridiagonal matrix; validated in ``tests/test_spectra.py``).
* The threshold ``β* = (π/L)²/b`` for ``b > 0`` is the Lean lemma ``viabilityThreshold_lt_iff``
  (``β > β*`` iff ``(π/L)² - βb < 0``); the identification of that expression with the principal
  eigenvalue is classical and not formalized.
* ``λ₁ < 0`` is sufficient for a positive solution (paper Theorem 3.16). It is also necessary
  when ``a ≡ 0`` (Proposition 3.19, the exact threshold); with a gradient term it is not
  necessary in general: Proposition 3.21 gives a positive continuum solution below the linear
  threshold, and Proposition 3.32 the finite-graph counterexample implemented in ``cd.graph``.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import ArpackNoConvergence, eigsh

from ._validation import check_finite_array, check_finite_scalar, check_positive_scalar
from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet, laplacian_3d_dirichlet

_DENSE_LIMIT = 256  # use a dense symmetric eigensolver at or below this size
_DENSE_FALLBACK_LIMIT = 4096  # fall back to dense if ARPACK fails at or below this size


def _potential(name: str, value: object, n: int) -> float | np.ndarray:
    """A scalar potential or a flat array of length ``n``."""
    if np.isscalar(value):
        return check_finite_scalar(name, value)
    arr = check_finite_array(name, value)
    if arr.shape != (n,):
        raise ValueError(f"{name}: expected a scalar or shape ({n},), got {arr.shape}")
    return arr


def _smallest_eigenpair(M: csr_matrix) -> tuple[float, np.ndarray]:
    """Smallest eigenvalue and a unit eigenvector of the symmetric sparse matrix ``M``."""
    n = M.shape[0]
    if n <= _DENSE_LIMIT:
        vals, vecs = np.linalg.eigh(M.toarray())
        return float(vals[0]), vecs[:, 0]
    try:
        vals, vecs = eigsh(M, k=1, which="SA")
    except ArpackNoConvergence as exc:
        if n <= _DENSE_FALLBACK_LIMIT:
            vals_d, vecs_d = np.linalg.eigh(M.toarray())
            return float(vals_d[0]), vecs_d[:, 0]
        raise RuntimeError(f"eigensolver did not converge for n={n}") from exc
    return float(vals[0]), vecs[:, 0]


def _positive_unit_vector(v: np.ndarray) -> np.ndarray:
    """Orient a sign-definite eigenvector to be nonnegative and scale it to ``max = 1``.

    The principal eigenvector of the irreducible finite-difference operator is sign-definite
    (Perron–Frobenius); ``abs`` removes the arbitrary sign of the numerical vector.
    """
    phi = np.abs(v)
    m = float(phi.max())
    if m <= 0.0 or not np.isfinite(m):
        raise RuntimeError("eigensolver returned a degenerate eigenvector")
    return phi / m


def _principal_interior(A: csr_matrix, q: float | np.ndarray, n: int) -> tuple[float, np.ndarray]:
    """Smallest eigenvalue of ``A - diag(q)`` and its positive unit eigenvector on the flat
    interior (length ``n``); the callers place it on their own full grid."""
    M = (A - diags([q * np.ones(n)], [0], format="csr")).tocsr()
    lam, v = _smallest_eigenpair(M)
    return lam, _positive_unit_vector(v)


def principal_eigenpair_1d(
    N: int, L: float, beta_b: float | np.ndarray
) -> tuple[float, np.ndarray]:
    """
    Principal eigenvalue and positive eigenvector of (-Δ - q) on (0, L), Dirichlet.

    Parameters
    ----------
    N : int
        Number of interior grid points.
    L : float
        Domain length.
    beta_b : float or ndarray
        Effective potential ``q = βb``: a scalar, an interior array (``N``), or a full-grid
        array (``N + 2``; only the interior is used).

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue of the discrete operator.
    phi : ndarray
        Eigenvector on the full grid (``N + 2`` points, zero at both ends), nonnegative,
        normalized so that ``max(phi) = 1``; strictly positive on the interior.
    """
    A, _ = laplacian_1d_dirichlet(N, L)
    if not np.isscalar(beta_b):
        arr = check_finite_array("beta_b", beta_b)
        if arr.shape == (N + 2,):
            beta_b = arr[1:-1]
    q = _potential("beta_b", beta_b, N)
    lam, v = _principal_interior(A, q, N)
    phi = np.zeros(N + 2)
    phi[1:-1] = v
    return lam, phi


def principal_eigenvalue_1d(
    N: int,
    L: float,
    beta_b: float | np.ndarray,
) -> float:
    """
    Compute principal eigenvalue of (-Δ - βb) on (0, L) with Dirichlet BC.

    Theorem (closed form for the tridiagonal matrix): for constant b the discrete value is
    exactly ``(4/h²) sin²(πh/(2L)) - βb`` with ``h = L/(N+1)``. The continuum value is
    ``λ₁ = (π/L)² - βb`` (Definition 3.13), approached at second order in ``h``.

    Parameters
    ----------
    N : int
        Number of interior grid points.
    L : float
        Domain length.
    beta_b : float or ndarray
        Effective potential ``q = βb`` (scalar, interior array, or full-grid array).

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue.

    Notes
    -----
    The viability threshold occurs at β* where λ₁ = 0:
        β* = (π/L)² / b   (for b > 0)

    - λ₁ > 0: below threshold; for a ≡ 0 only the zero solution exists (Proposition 3.19)
    - λ₁ < 0: above threshold; a positive solution exists (Theorem 3.16)

    Example
    -------
    >>> L, b = 1.0, 0.8
    >>> beta_star = (np.pi / L)**2 / b  # ≈ 12.34
    >>> principal_eigenvalue_1d(400, L, 0.8 * beta_star * b)  # > 0
    >>> principal_eigenvalue_1d(400, L, 1.2 * beta_star * b)  # < 0
    """
    lam, _ = principal_eigenpair_1d(N, L, beta_b)
    return lam


def principal_eigenpair_2d(
    Nx: int, Ny: int, Lx: float, Ly: float, beta_b: float | np.ndarray
) -> tuple[float, np.ndarray]:
    """
    Principal eigenvalue and positive eigenvector of (-Δ - q) on a rectangle, Dirichlet.

    Parameters
    ----------
    Nx, Ny : int
        Number of interior grid points in each direction.
    Lx, Ly : float
        Domain lengths.
    beta_b : float or ndarray
        Effective potential: scalar, interior ``(Ny, Nx)`` array, or full ``(Ny+2, Nx+2)`` array.

    Returns
    -------
    lam1 : float
        Principal eigenvalue.
    Phi : ndarray
        Eigenvector on the full grid, shape ``(Ny+2, Nx+2)``, zero on the boundary,
        nonnegative, normalized to ``max = 1``.
    """
    A, _, _ = laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)
    n = Nx * Ny
    if not np.isscalar(beta_b):
        arr = check_finite_array("beta_b", beta_b)
        if arr.shape == (Ny + 2, Nx + 2):
            beta_b = arr[1:-1, 1:-1].reshape(-1)
        elif arr.shape == (Ny, Nx):
            beta_b = arr.reshape(-1)
    q = _potential("beta_b", beta_b, n)
    lam, v = _principal_interior(A, q, n)
    Phi = np.zeros((Ny + 2, Nx + 2))
    Phi[1:-1, 1:-1] = v.reshape(Ny, Nx)
    return lam, Phi


def principal_eigenvalue_2d(
    Nx: int,
    Ny: int,
    Lx: float,
    Ly: float,
    beta_b: float | np.ndarray,
) -> float:
    """
    Compute principal eigenvalue of (-Δ - βb) on rectangle with Dirichlet BC.

    For constant b on [0,Lx] × [0,Ly], the continuum value (Definition 3.13) is
        λ₁ = π²(1/Lx² + 1/Ly²) - βb,
    and, by the Kronecker structure of the operator (Theorem: separable eigenvectors), the
    discrete value is the sum of the two one-dimensional discrete eigenvalues minus βb.

    Parameters
    ----------
    Nx, Ny : int
        Number of interior grid points in each direction.
    Lx, Ly : float
        Domain lengths.
    beta_b : float or ndarray
        Effective potential (scalar or field).

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue.
    """
    lam, _ = principal_eigenpair_2d(Nx, Ny, Lx, Ly, beta_b)
    return lam


def principal_eigenpair_3d(
    Nx: int, Ny: int, Nz: int, Lx: float, Ly: float, Lz: float, beta_b: float | np.ndarray
) -> tuple[float, np.ndarray]:
    """
    Principal eigenvalue and positive eigenvector of (-Δ - q) on a box, Dirichlet.

    Parameters
    ----------
    Nx, Ny, Nz : int
        Interior grid points per direction.
    Lx, Ly, Lz : float
        Domain lengths.
    beta_b : float or ndarray
        Effective potential: scalar, interior ``(Nz, Ny, Nx)`` array, or full
        ``(Nz+2, Ny+2, Nx+2)`` array in the ``(z, y, x)`` layout of ``grid_3d`` /
        ``laplacian_3d_dirichlet``. Arrays in another layout are rejected by shape when the
        sizes differ; with equal sizes the layout cannot be detected, so build the field from
        ``grid_3d``.

    Returns
    -------
    lam1 : float
    Phi : ndarray
        Eigenvector on the full grid, shape ``(Nz+2, Ny+2, Nx+2)``, zero on the boundary,
        nonnegative, normalized to ``max = 1``.

    Notes
    -----
    This is the *discrete* eigenvalue of the finite-difference operator. Its sign is numerical
    evidence about the continuum operator, not a certificate: near the threshold the discrete
    and continuum signs can differ (the discrete value converges at second order), and the
    paper's continuum theorem assumes a smooth boundary, which a box does not have.
    """
    A, _, _, _ = laplacian_3d_dirichlet(Nx, Ny, Nz, Lx, Ly, Lz)
    n = Nx * Ny * Nz
    if not np.isscalar(beta_b):
        arr = check_finite_array("beta_b", beta_b)
        if arr.shape == (Nz + 2, Ny + 2, Nx + 2):
            beta_b = arr[1:-1, 1:-1, 1:-1].reshape(-1)
        elif arr.shape == (Nz, Ny, Nx):
            beta_b = arr.reshape(-1)
        else:
            raise ValueError(
                f"beta_b must be a scalar, shape ({Nz}, {Ny}, {Nx}) or ({Nz + 2}, {Ny + 2}, {Nx + 2}) "
                f"in (z, y, x) layout; got {arr.shape}"
            )
    q = _potential("beta_b", beta_b, n)
    lam, v = _principal_interior(A, q, n)
    Phi = np.zeros((Nz + 2, Ny + 2, Nx + 2))
    Phi[1:-1, 1:-1, 1:-1] = v.reshape(Nz, Ny, Nx)
    return lam, Phi


def principal_eigenvalue_3d(
    Nx: int, Ny: int, Nz: int, Lx: float, Ly: float, Lz: float, beta_b: float | np.ndarray
) -> float:
    """Principal eigenvalue of (-Δ - q) on a box with Dirichlet BC; see ``principal_eigenpair_3d``
    for the array convention. Theorem (Kronecker structure, separable eigenvectors): for
    constant q the value is the sum of the three 1D discrete eigenvalues minus q, i.e.
    ``Σ (4/h²) sin²(πh/(2L)) - q``. This is the 3D eigenvalue illustration, a model distinct
    from the 1D/2D continuum solvers and from the finite-graph model."""
    lam, _ = principal_eigenpair_3d(Nx, Ny, Nz, Lx, Ly, Lz, beta_b)
    return lam


def viability_threshold_1d(L: float, b: float) -> float:
    """
    Compute critical viability gain β* for 1D domain.

    Parameters
    ----------
    L : float
        Domain length (``L > 0``).
    b : float
        Constant viability potential (``b > 0``).

    Returns
    -------
    beta_star : float
        Critical value where λ₁ = 0.

    Raises
    ------
    ValueError
        If ``L <= 0`` or ``b <= 0``. For ``b <= 0`` the operator ``-Δ - βb`` has
        ``λ₁ >= (π/L)² > 0`` for every ``β >= 0`` (Theorem: ``λ₁`` is nonincreasing in the
        potential, so ``λ₁(-Δ - βb) >= λ₁(-Δ)``): there is no threshold to cross.

    Notes
    -----
    β* = (π/L)² / b for a *constant* potential b. Lean: ``viabilityThreshold``,
    ``viabilityThreshold_lt_iff`` (b > 0). For a spatially varying potential use the
    computed eigenvalue (``principal_eigenvalue_1d`` with the field); the constant-coefficient
    threshold of a reference level such as ``κγ`` is then only a scale for choosing β.

    For β < β*: λ₁ > 0 (for a ≡ 0 only the zero solution, Proposition 3.19)
    For β > β*: λ₁ < 0 (a positive solution exists, Theorem 3.16)
    """
    L = check_positive_scalar("L", L)
    b = check_finite_scalar("b", b)
    if b <= 0:
        raise ValueError("Viability potential b must be positive for the threshold to exist.")
    return (np.pi / L) ** 2 / b


def viability_threshold_2d(Lx: float, Ly: float, b: float) -> float:
    """
    Compute critical viability gain β* for 2D rectangular domain.

    Parameters
    ----------
    Lx, Ly : float
        Domain lengths (positive).
    b : float
        Constant viability potential (``b > 0``).

    Returns
    -------
    beta_star : float
        Critical value where λ₁ = 0.

    Raises
    ------
    ValueError
        If a length is not positive or ``b <= 0``.
    """
    Lx = check_positive_scalar("Lx", Lx)
    Ly = check_positive_scalar("Ly", Ly)
    b = check_finite_scalar("b", b)
    if b <= 0:
        raise ValueError("Viability potential b must be positive for the threshold to exist.")
    return np.pi**2 * (1 / Lx**2 + 1 / Ly**2) / b


def principal_eigenvalue_1d_spatial(
    N: int,
    L: float,
    beta_b_field: np.ndarray,
) -> float:
    """
    Compute principal eigenvalue of (-Δ - diag(βb(x))) on (0, L) with Dirichlet BC.

    Parameters
    ----------
    N : int
        Number of interior grid points.
    L : float
        Domain length.
    beta_b_field : ndarray
        Spatially-varying βb values on the full grid (N+2 points including boundaries).
        Only interior values [1:-1] are used.

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue.
    """
    field = check_finite_array("beta_b_field", beta_b_field, shape=(N + 2,))
    return principal_eigenvalue_1d(N, L, field[1:-1])


def principal_eigenvalue_2d_spatial(
    Nx: int,
    Ny: int,
    Lx: float,
    Ly: float,
    beta_b_field: np.ndarray,
) -> float:
    """
    Compute principal eigenvalue of (-Δ - diag(βb(x,y))) on rectangle with Dirichlet BC.

    Parameters
    ----------
    Nx, Ny : int
        Number of interior grid points in each direction.
    Lx, Ly : float
        Domain lengths.
    beta_b_field : ndarray
        Spatially-varying βb on the full grid, shape (Ny+2, Nx+2).
        Only interior values [1:-1, 1:-1] are used.

    Returns
    -------
    lam1 : float
        Principal (smallest) eigenvalue.
    """
    field = check_finite_array("beta_b_field", beta_b_field, shape=(Ny + 2, Nx + 2))
    return principal_eigenvalue_2d(Nx, Ny, Lx, Ly, field[1:-1, 1:-1].reshape(-1))
