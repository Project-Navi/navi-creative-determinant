"""
Analysis utilities for the Creative Determinant framework.

Provides tools for validating numerical solutions:
- Residual computation (how well does Φ satisfy the PDE?)
- Convergence diagnostics
- Solution characterization
"""

from __future__ import annotations

import numpy as np


def _to_interior_1d(val, N):
    """Convert scalar or array to interior array of length N."""
    if np.isscalar(val):
        return val  # scalar broadcasts naturally
    val = np.asarray(val)
    if val.shape == (N + 2,):
        return val[1:-1]
    if val.shape == (N,):
        return val
    raise ValueError(f"Expected scalar, length {N}, or length {N+2}; got shape {val.shape}")


def residual_1d(
    x: np.ndarray,
    Phi: np.ndarray,
    a: float | np.ndarray,
    beta_b: float | np.ndarray,
    c: float | np.ndarray,
    p: float,
) -> np.ndarray:
    """
    Compute PDE residual on interior nodes.

    Residual R = -Φ'' - (a|Φ'| + βbΦ - cΦᵖ)

    For an exact solution, R ≡ 0.

    Parameters
    ----------
    x : ndarray
        Grid points including boundaries.
    Phi : ndarray
        Solution including boundary values.
    a : float
        Creative drive coefficient.
    beta_b : float
        Viability parameter.
    c : float
        Saturation coefficient.
    p : float
        Saturation exponent.

    Returns
    -------
    res : ndarray
        Residual on interior points, shape (N,).

    Notes
    -----
    Uses second-order centered differences for derivatives.
    Small ||R||_∞ indicates the numerical solution accurately
    satisfies the PDE.
    """
    L = x[-1] - x[0]
    N = len(x) - 2
    h = L / (N + 1)

    # Convert coefficients to interior arrays (or leave as scalar)
    a = _to_interior_1d(a, N)
    beta_b = _to_interior_1d(beta_b, N)
    c = _to_interior_1d(c, N)

    # Second derivative (interior)
    Phi_xx = (Phi[2:] - 2 * Phi[1:-1] + Phi[:-2]) / h**2

    # First derivative magnitude (interior)
    Phi_x = (Phi[2:] - Phi[:-2]) / (2 * h)

    # Residual: should be zero for exact solution
    Phi_int = Phi[1:-1]
    rhs = a * np.abs(Phi_x) + beta_b * Phi_int - c * np.maximum(Phi_int, 0.0) ** p
    res = -Phi_xx - rhs

    return res


def check_convergence(info: dict, tol: float = 1e-8) -> tuple[bool, str]:
    """
    Check solver convergence and provide diagnostic message.

    Parameters
    ----------
    info : dict
        Solver info dictionary with 'inf_err', 'iters', 'converged'.
    tol : float
        Tolerance threshold.

    Returns
    -------
    ok : bool
        True if solution is acceptable.
    message : str
        Diagnostic message.
    """
    if info.get("converged", False):
        return True, f"Converged in {info['iters']} iterations (err={info['inf_err']:.2e})"

    if info["inf_err"] < tol * 10:
        return True, f"Nearly converged in {info['iters']} iterations (err={info['inf_err']:.2e})"

    return False, f"Did not converge after {info['iters']} iterations (err={info['inf_err']:.2e})"


def solution_type(info: dict, threshold: float = 1e-6) -> str:
    """
    Classify solution as trivial or nontrivial.

    Parameters
    ----------
    info : dict
        Solver info with 'maxPhi'.
    threshold : float
        Cutoff for trivial classification.

    Returns
    -------
    classification : str
        'trivial' if maxΦ < threshold, else 'nontrivial'.
    """
    if info["maxPhi"] < threshold:
        return "trivial"
    return "nontrivial"


def presence_statistics(Phi: np.ndarray, x: np.ndarray) -> dict:
    """
    Compute statistics of the presence field.

    Parameters
    ----------
    Phi : ndarray
        Presence field (1D or 2D).
    x : ndarray
        Grid points (for 1D) or None (for 2D, uses uniform spacing).

    Returns
    -------
    stats : dict
        - 'max': maximum presence
        - 'mean': mean presence (interior only)
        - 'total': integrated presence (trapezoid rule)
        - 'support_fraction': fraction of domain with Φ > 0.01*max
    """
    Phi_int = Phi.ravel()[Phi.ravel() > 0]
    max_phi = float(Phi.max())

    # Use actual grid spacing if x is provided
    if x is not None and len(x) > 1:
        dx = float(x.ravel()[1] - x.ravel()[0])
    else:
        dx = 1.0
    stats = {
        "max": max_phi,
        "mean": float(Phi_int.mean()) if len(Phi_int) > 0 else 0.0,
        "total": float(np.trapezoid(Phi.ravel(), dx=dx)),
    }

    if max_phi > 1e-10:
        threshold = 0.01 * max_phi
        stats["support_fraction"] = float((Phi > threshold).sum() / Phi.size)
    else:
        stats["support_fraction"] = 0.0

    return stats
