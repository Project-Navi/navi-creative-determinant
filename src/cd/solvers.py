"""
Solvers for the Creative Determinant PDE framework.

Implements Picard iteration for the nonlinear elliptic BVP:
    -ΔΦ = a|∇Φ| + βbΦ - cΦᵖ,  Φ|∂M = 0
"""

import numpy as np
from scipy.sparse.linalg import spsolve

from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet


def solve_1d_picard(
    L: float,
    N: int,
    a: float,
    beta_b: float,
    c: float,
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
    A, h = laplacian_1d_dirichlet(N, L)
    x = np.linspace(0, L, N + 2)

    # Initial guess: sine wave satisfying BCs
    Phi = initial_amplitude * np.sin(np.pi * x / L)
    Phi_int = Phi[1:-1].copy()

    def grad_abs(Phi_full):
        """Central difference approximation of |Φ'|."""
        d = (Phi_full[2:] - Phi_full[:-2]) / (2 * h)
        return np.abs(d)

    converged = False
    for it in range(max_iter):
        # Build full array with BCs
        Phi_full = np.zeros(N + 2)
        Phi_full[1:-1] = Phi_int

        # Evaluate nonlinear terms at current iterate
        gabs = grad_abs(Phi_full)
        rhs = a * gabs + beta_b * Phi_int - c * np.maximum(Phi_int, 0.0) ** p

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

    return x, Phi, info


def solve_2d_picard(
    Lx: float,
    Ly: float,
    Nx: int,
    Ny: int,
    a: float,
    beta_b: float,
    c: float,
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
    A, hx, hy = laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)

    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    X, Y = np.meshgrid(x, y)

    # Initial guess: product of sines
    Phi = initial_amplitude * np.sin(np.pi * X / Lx) * np.sin(np.pi * Y / Ly)
    Phi_int = Phi[1:-1, 1:-1].flatten()

    # Viability field
    if b_field is None:
        b_flat = np.ones(Nx * Ny)
    else:
        b_flat = b_field.flatten()

    def grad_abs_2d(Phi_full):
        """Approximate |∇Φ| on interior."""
        Phi_x = (Phi_full[1:-1, 2:] - Phi_full[1:-1, :-2]) / (2 * hx)
        Phi_y = (Phi_full[2:, 1:-1] - Phi_full[:-2, 1:-1]) / (2 * hy)
        return np.sqrt(Phi_x**2 + Phi_y**2).flatten()

    converged = False
    for it in range(max_iter):
        # Build full array
        Phi_full = np.zeros((Ny + 2, Nx + 2))
        Phi_full[1:-1, 1:-1] = Phi_int.reshape(Ny, Nx)

        # Nonlinear terms
        gabs = grad_abs_2d(Phi_full)
        rhs = a * gabs + beta_b * b_flat * Phi_int - c * np.maximum(Phi_int, 0.0) ** p

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

    return X, Y, Phi, info
