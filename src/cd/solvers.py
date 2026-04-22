"""
Solvers for the Creative Determinant PDE framework.

Implements Picard iteration for the nonlinear elliptic BVP:
    -ΔΦ = a|∇Φ| + βbΦ - cΦᵖ,  Φ|∂M = 0
"""

from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import spsolve

from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet


def _to_interior_1d(val, N):
    """Convert scalar or array to interior array of length N."""
    if np.isscalar(val):
        return val  # scalar broadcasts naturally
    val = np.asarray(val)
    if val.shape == (N + 2,):
        return val[1:-1]
    if val.shape == (N,):
        return val
    raise ValueError(f"Expected scalar, length {N}, or length {N + 2}; got shape {val.shape}")


def solve_1d_picard(
    L: float,
    N: int,
    a: float | np.ndarray,
    beta_b: float | np.ndarray,
    c: float | np.ndarray,
    p: float = 2.0,
    max_iter: int = 8000,
    tol: float = 1e-10,
    damping: float = 0.5,
    initial_amplitude: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Solve 1D Creative Determinant PDE via damped Picard iteration.

    Equation:
        -Φ'' = a|Φ'| + βbΦ - cΦᵖ,  Φ(0) = Φ(L) = 0

    Parameters
    ----------
    L : float
        Domain length.
    N : int
        Number of interior grid points.
    a : float
        Creative drive coefficient (gradient term).
    beta_b : float
        Product of viability gain and potential.
    c : float
        Saturation coefficient.
    p : float, default=2.0
        Saturation exponent (must be > 1).
    max_iter : int, default=8000
        Maximum Picard iterations.
    tol : float, default=1e-10
        Convergence tolerance (L∞ norm of update).
    damping : float, default=0.5
        Damping factor in (0, 1]. Higher = more aggressive updates.
    initial_amplitude : float, default=0.1
        Amplitude of initial guess (sine wave).

    Returns
    -------
    x : ndarray
        Grid points including boundaries, shape (N+2,).
    Phi : ndarray
        Solution including boundary values, shape (N+2,).
    info : dict
        Solver diagnostics:
        - 'iters': number of iterations used
        - 'inf_err': final L∞ error
        - 'maxPhi': maximum value of Φ
        - 'converged': whether tolerance was reached

    Notes
    -----
    The Picard iteration linearizes the nonlinear terms:
        -ΔΦⁿ⁺¹ = a|∇Φⁿ| + βbΦⁿ - c(Φⁿ)ᵖ

    Damping improves stability: Φⁿ⁺¹ ← (1-α)Φⁿ + αΦ̃ⁿ⁺¹

    Example
    -------
    >>> x, Phi, info = solve_1d_picard(L=1.0, N=400, a=0.0, beta_b=15.0, c=10.0)
    >>> info['converged']
    True
    >>> info['maxPhi'] > 0.01  # Nontrivial solution
    True
    """
    if L <= 0:
        raise ValueError(f"Domain length L must be positive, got L={L}")
    if N <= 0:
        raise ValueError(f"Grid points N must be positive, got N={N}")
    if p <= 1:
        raise ValueError(f"Saturation exponent p must be > 1, got p={p}")
    if np.isscalar(c):
        if c <= 0:
            raise ValueError(f"Saturation c must be positive, got c={c}")
    else:
        c_arr = np.asarray(c)
        if c_arr.min() <= 0:
            raise ValueError(f"Saturation c must be positive everywhere, got min(c)={c_arr.min()}")

    A, h = laplacian_1d_dirichlet(N, L)
    x = np.linspace(0, L, N + 2)

    # Initial guess: sine wave satisfying BCs
    Phi = initial_amplitude * np.sin(np.pi * x / L)
    Phi_int = Phi[1:-1].copy()

    # Convert coefficients to interior arrays (or leave as scalar)
    a_int = _to_interior_1d(a, N)
    bb_int = _to_interior_1d(beta_b, N)
    c_int = _to_interior_1d(c, N)

    def grad_abs(Phi_full):
        """Central difference approximation of |Φ'|."""
        d = (Phi_full[2:] - Phi_full[:-2]) / (2 * h)
        return np.abs(d)

    converged = False
    err = float("inf")
    it = 0
    for it in range(max_iter):
        # Build full array with BCs
        Phi_full = np.zeros(N + 2)
        Phi_full[1:-1] = Phi_int

        # Evaluate nonlinear terms at current iterate
        gabs = grad_abs(Phi_full)
        rhs = a_int * gabs + bb_int * Phi_int - c_int * np.maximum(Phi_int, 0.0) ** p

        # Solve linear system
        Phi_new = spsolve(A, rhs)

        # Damped update with positivity enforcement
        Phi_next = (1 - damping) * Phi_int + damping * Phi_new
        Phi_next = np.maximum(Phi_next, 0.0)

        # Check convergence
        err = np.linalg.norm(Phi_next - Phi_int, ord=np.inf)
        Phi_int = Phi_next

        if err < tol:
            converged = True
            break

    # Assemble full solution with BCs
    Phi = np.zeros(N + 2)
    Phi[1:-1] = Phi_int

    info = {
        "iters": it + 1,
        "inf_err": float(err),
        "maxPhi": float(Phi.max()),
        "converged": converged,
    }

    # Post-solve L-infinity bound check (Lemma 3.10)
    # Verified: linfty_bound_algebraic (CdFormal/LinftyAlgebraic.lean:59)
    from .analysis import linfty_bound as _linfty_bound

    try:
        K = _linfty_bound(beta_b, c, p)
        info["linfty_bound"] = K
        if info["maxPhi"] > 0 and K > 0 and info["maxPhi"] > 1.01 * K:
            import warnings

            warnings.warn(
                f"Solution max(Phi)={info['maxPhi']:.6f} exceeds theoretical "
                f"L-infinity bound K={K:.6f} by "
                f"{(info['maxPhi'] / K - 1) * 100:.1f}%. "
                f"Check grid resolution or parameters.",
                stacklevel=2,
            )
    except ValueError:
        info["linfty_bound"] = None  # bound not computable for these parameters

    return x, Phi, info


def solve_2d_picard(
    Lx: float,
    Ly: float,
    Nx: int,
    Ny: int,
    a: float | np.ndarray,
    beta_b: float,
    c: float | np.ndarray,
    p: float = 2.0,
    max_iter: int = 8000,
    tol: float = 1e-8,
    damping: float = 0.5,
    initial_amplitude: float = 0.1,
    b_field: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """
    Solve 2D Creative Determinant PDE via damped Picard iteration.

    Equation:
        -ΔΦ = a|∇Φ| + βb(x,y)Φ - cΦᵖ,  Φ|∂M = 0

    Parameters
    ----------
    Lx, Ly : float
        Domain lengths.
    Nx, Ny : int
        Number of interior grid points in each direction.
    a : float
        Creative drive coefficient.
    beta_b : float
        Viability gain (multiplies b_field if provided).
    c : float
        Saturation coefficient.
    p : float, default=2.0
        Saturation exponent.
    max_iter : int, default=8000
        Maximum iterations.
    tol : float, default=1e-8
        Convergence tolerance.
    damping : float, default=0.5
        Damping factor.
    initial_amplitude : float, default=0.1
        Initial guess amplitude.
    b_field : ndarray, optional
        Spatially-varying viability field on interior grid, shape (Ny, Nx).
        If None, uses constant b=1.

    Returns
    -------
    X, Y : ndarray
        Meshgrid arrays including boundaries, shape (Ny+2, Nx+2).
    Phi : ndarray
        Solution including boundary values, shape (Ny+2, Nx+2).
    info : dict
        Solver diagnostics.
    """
    if Lx <= 0 or Ly <= 0:
        raise ValueError(f"Domain lengths must be positive, got Lx={Lx}, Ly={Ly}")
    if Nx <= 0 or Ny <= 0:
        raise ValueError(f"Grid points must be positive, got Nx={Nx}, Ny={Ny}")
    if p <= 1:
        raise ValueError(f"Saturation exponent p must be > 1, got p={p}")
    if np.isscalar(c):
        if c <= 0:
            raise ValueError(f"Saturation c must be positive, got c={c}")
    else:
        c_arr = np.asarray(c)
        if c_arr.min() <= 0:
            raise ValueError(f"Saturation c must be positive everywhere, got min(c)={c_arr.min()}")

    A, hx, hy = laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)

    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    X, Y = np.meshgrid(x, y)

    # Initial guess: product of sines
    Phi = initial_amplitude * np.sin(np.pi * X / Lx) * np.sin(np.pi * Y / Ly)
    Phi_int = Phi[1:-1, 1:-1].flatten()

    # Convert array coefficients to flat interior arrays
    if hasattr(a, "__len__"):
        a_flat = np.asarray(a).flatten()
    else:
        a_flat = a  # scalar broadcasts
    if hasattr(c, "__len__"):
        c_flat = np.asarray(c).flatten()
    else:
        c_flat = c  # scalar broadcasts

    # Viability field
    if b_field is None:
        b_flat = np.ones(Nx * Ny)
    else:
        b_flat = b_field.flatten()

    def grad_abs_2d(Phi_full):
        """
        Approximate |∇Φ| on interior grid points.

        Parameters
        ----------
        Phi_full : ndarray of shape (Ny + 2, Nx + 2)
            Full field including boundary values.

        Returns
        -------
        ndarray of shape (Ny * Nx,)
            Flattened (row-major) gradient magnitude evaluated only at
            interior points, corresponding to Phi_full[1:-1, 1:-1]. The
            boundary values are not included.
        """
        Phi_x = (Phi_full[1:-1, 2:] - Phi_full[1:-1, :-2]) / (2 * hx)
        Phi_y = (Phi_full[2:, 1:-1] - Phi_full[:-2, 1:-1]) / (2 * hy)
        return np.sqrt(Phi_x**2 + Phi_y**2).flatten()

    converged = False
    err = float("inf")
    it = 0
    for it in range(max_iter):
        # Build full array
        Phi_full = np.zeros((Ny + 2, Nx + 2))
        Phi_full[1:-1, 1:-1] = Phi_int.reshape(Ny, Nx)

        # Nonlinear terms
        gabs = grad_abs_2d(Phi_full)
        rhs = a_flat * gabs + beta_b * b_flat * Phi_int - c_flat * np.maximum(Phi_int, 0.0) ** p

        # Solve
        Phi_new = spsolve(A, rhs)

        # Damped update
        Phi_next = (1 - damping) * Phi_int + damping * Phi_new
        Phi_next = np.maximum(Phi_next, 0.0)

        err = np.linalg.norm(Phi_next - Phi_int, ord=np.inf)
        Phi_int = Phi_next

        if err < tol:
            converged = True
            break

    # Assemble solution
    Phi = np.zeros((Ny + 2, Nx + 2))
    Phi[1:-1, 1:-1] = Phi_int.reshape(Ny, Nx)

    info = {
        "iters": it + 1,
        "inf_err": float(err),
        "maxPhi": float(Phi.max()),
        "converged": converged,
    }

    # Post-solve L-infinity bound check (Lemma 3.10)
    # Verified: linfty_bound_algebraic (CdFormal/LinftyAlgebraic.lean:59)
    from .analysis import linfty_bound as _linfty_bound

    try:
        effective_bb = beta_b * b_flat.max() if b_field is not None else beta_b
        K = _linfty_bound(effective_bb, c, p)
        info["linfty_bound"] = K
        if info["maxPhi"] > 0 and K > 0 and info["maxPhi"] > 1.01 * K:
            import warnings

            warnings.warn(
                f"Solution max(Phi)={info['maxPhi']:.6f} exceeds theoretical "
                f"L-infinity bound K={K:.6f} by "
                f"{(info['maxPhi'] / K - 1) * 100:.1f}%. "
                f"Check grid resolution or parameters.",
                stacklevel=2,
            )
    except ValueError:
        info["linfty_bound"] = None  # bound not computable for these parameters

    return X, Y, Phi, info
