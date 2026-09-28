"""
Analysis utilities for the Creative Determinant framework.

Provides tools for validating numerical solutions:
- Residual computation (does Φ satisfy the *discrete* equation?)
- Fail-closed convergence diagnostics
- Branch classification (zero / positive / nonnegative / unresolved / invalid)
- Spatial statistics with an explicit population and quadrature measure
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ._validation import (
    check_exponent,
    check_finite_array,
    coefficient_1d,
    require_positive_coefficient,
)

_ZERO_BRANCH_TOL = 1e-6


def _uniform_spacing(x: np.ndarray) -> float:
    """Spacing of a uniform grid; rejects nonuniform grids (the stencils assume uniformity)."""
    if x.ndim != 1 or x.size < 3:
        raise ValueError("x must be a 1D grid with at least three points")
    d = np.diff(x)
    h = float(d[0])
    if h <= 0.0 or np.max(np.abs(d - h)) > 1e-10 * h:
        raise ValueError("x must be a uniformly spaced increasing grid")
    return h


def residual_1d(
    x: np.ndarray,
    Phi: np.ndarray,
    a: float | np.ndarray,
    beta_b: float | np.ndarray,
    c: float | np.ndarray,
    p: float,
) -> np.ndarray:
    """
    Compute the discrete PDE residual on interior nodes.

    Residual R = -Φ'' - (a|Φ'| + βbΦ - c(Φ₊)ᵖ) with second-order centered differences.

    For an exact solution of the *discrete* equation, R ≡ 0. A small ``||R||_∞`` certifies the
    discrete equation at the solver tolerance; it is not a bound on the distance to the
    continuum solution, which the grid-refinement studies measure.

    Parameters
    ----------
    x : ndarray
        Uniform grid points including boundaries, shape (N+2,).
    Phi : ndarray
        Field including boundary values, shape (N+2,).
    a, beta_b, c : float or ndarray
        Coefficients: scalars, interior arrays (N) or full-grid arrays (N+2).
    p : float
        Saturation exponent (> 1).

    Returns
    -------
    res : ndarray
        Residual on interior points, shape (N,).

    Raises
    ------
    ValueError
        On shape mismatch, nonuniform grid, nonfinite data, or invalid coefficients.
    """
    x = check_finite_array("x", x)
    h = _uniform_spacing(x)
    Phi = check_finite_array("Phi", Phi, shape=x.shape)
    N = x.size - 2
    p = check_exponent("p", p)
    a_i = coefficient_1d("a", a, N)
    q_i = coefficient_1d("beta_b", beta_b, N)
    c_i = coefficient_1d("c", c, N)
    require_positive_coefficient("c", c_i)

    Phi_xx = (Phi[2:] - 2 * Phi[1:-1] + Phi[:-2]) / h**2
    Phi_x = (Phi[2:] - Phi[:-2]) / (2 * h)
    Phi_int = Phi[1:-1]
    rhs = a_i * np.abs(Phi_x) + q_i * Phi_int - c_i * np.maximum(Phi_int, 0.0) ** p
    return -Phi_xx - rhs


def residual_2d(
    Phi: np.ndarray,
    a_full: np.ndarray,
    beta_b_full: np.ndarray,
    c_full: np.ndarray,
    p: float,
    hx: float,
    hy: float,
) -> np.ndarray:
    """
    Compute the discrete 2D PDE residual on interior nodes.

    Residual R = -Δ_h Φ - (a|∇_h Φ| + βbΦ - c(Φ₊)ᵖ) with centered differences on the tensor grid.

    Parameters
    ----------
    Phi : ndarray
        Field including boundaries, shape (Ny+2, Nx+2).
    a_full, beta_b_full, c_full : ndarray
        Coefficient fields on the full grid, shape (Ny+2, Nx+2).
    p : float
        Saturation exponent.
    hx, hy : float
        Grid spacings (positive).

    Returns
    -------
    res : ndarray
        Residual on interior nodes, shape (Ny, Nx).
    """
    Phi = check_finite_array("Phi", Phi)
    if Phi.ndim != 2 or min(Phi.shape) < 3:
        raise ValueError("Phi must be a 2D array with at least one interior node")
    a_full = check_finite_array("a_full", a_full, shape=Phi.shape)
    beta_b_full = check_finite_array("beta_b_full", beta_b_full, shape=Phi.shape)
    c_full = check_finite_array("c_full", c_full, shape=Phi.shape)
    p = check_exponent("p", p)
    if not (np.isfinite(hx) and np.isfinite(hy) and hx > 0 and hy > 0):
        raise ValueError("hx and hy must be positive")
    c_int = c_full[1:-1, 1:-1]
    require_positive_coefficient("c_full", c_int)

    Phi_xx = (Phi[1:-1, 2:] - 2 * Phi[1:-1, 1:-1] + Phi[1:-1, :-2]) / hx**2
    Phi_yy = (Phi[2:, 1:-1] - 2 * Phi[1:-1, 1:-1] + Phi[:-2, 1:-1]) / hy**2
    lap = Phi_xx + Phi_yy

    dPhidx = (Phi[1:-1, 2:] - Phi[1:-1, :-2]) / (2 * hx)
    dPhidy = (Phi[2:, 1:-1] - Phi[:-2, 1:-1]) / (2 * hy)
    gmag = np.sqrt(dPhidx**2 + dPhidy**2)

    Phi_int = Phi[1:-1, 1:-1]
    a_int = a_full[1:-1, 1:-1]
    bb_int = beta_b_full[1:-1, 1:-1]

    rhs = a_int * gmag + bb_int * Phi_int - c_int * np.maximum(Phi_int, 0.0) ** p
    return -lap - rhs


def _finite(value: Any) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def check_convergence(info: dict) -> tuple[bool, str]:
    """
    Fail-closed convergence check on a solver ``info`` dictionary.

    A run is acceptable only if the solver reports ``converged`` (residual and update criteria
    met) and every reported diagnostic is finite. Iteration exhaustion, stagnation, nonfinite
    iterates and missing residual information are never accepted. There is no "nearly
    converged" category.

    Parameters
    ----------
    info : dict
        Solver info with at least ``converged``, ``iters``, ``inf_err`` and ``residual_inf``.

    Returns
    -------
    ok : bool
        True only for an accepted solution.
    message : str
        Diagnostic message including the termination reason.
    """
    iters = info.get("iters", "?")
    inf_err = info.get("inf_err", float("nan"))
    res = info.get("residual_inf")
    term = info.get("termination", "unknown")
    if res is None:
        return False, f"Not accepted: no residual diagnostic (iters={iters}, termination={term})"
    if not (_finite(inf_err) and _finite(res)):
        return False, f"Not accepted: nonfinite diagnostics (iters={iters}, termination={term})"
    if info.get("converged", False) is True and term in ("converged", "unknown"):
        return True, f"Converged in {iters} iterations (update={inf_err:.2e}, residual={res:.2e})"
    return (
        False,
        f"Did not converge after {iters} iterations (termination={term}, update={inf_err:.2e}, residual={res:.2e})",
    )


def solution_type(info: dict, threshold: float = _ZERO_BRANCH_TOL) -> str:
    """
    Classify a solver result as ``'trivial'`` / ``'nontrivial'`` (converged runs only),
    ``'unresolved'`` (not converged) or ``'invalid'`` (nonfinite maximum).

    Parameters
    ----------
    info : dict
        Solver info with ``maxPhi`` and (optionally) ``converged``.
    threshold : float
        Cutoff on ``maxPhi`` for the trivial classification.

    Notes
    -----
    This keeps the historical labels. ``classify_branch`` gives the finer classification used
    by the notebook (``zero`` / ``positive`` / ``nonnegative`` / ``unresolved`` / ``invalid``).
    """
    max_phi = info.get("maxPhi", float("nan"))
    if not _finite(max_phi) or info.get("termination") == "nonfinite":
        return "invalid"
    if "residual_inf" in info and not _finite(info["residual_inf"]):
        return "invalid"
    if not info.get("converged", True):
        return "unresolved"
    return "trivial" if float(max_phi) < threshold else "nontrivial"


def classify_branch(Phi: np.ndarray, info: dict, zero_tol: float = _ZERO_BRANCH_TOL) -> str:
    """
    Classify a returned field together with its solver diagnostics.

    Returns
    -------
    str
        ``'invalid'`` if the field or diagnostics are nonfinite;
        ``'unresolved'`` if the solver did not converge (near-threshold failure is not
        evidence of nonexistence);
        ``'zero'`` if converged and ``max Phi <= zero_tol`` (the zero solution is exact on
        both sides of the threshold);
        ``'positive'`` if converged and strictly positive at every interior node;
        ``'nonnegative'`` if converged, not zero, but vanishing somewhere in the interior.

    ``zero_tol`` is a classification threshold for the returned field, not a proof that no
    small positive solution exists.
    """
    Phi = np.asarray(Phi, dtype=float)
    if not np.all(np.isfinite(Phi)) or not _finite(info.get("maxPhi", float("nan"))):
        return "invalid"
    if info.get("termination") == "nonfinite":
        return "invalid"
    if "residual_inf" in info and not _finite(info["residual_inf"]):
        return "invalid"
    if not info.get("converged", False):
        return "unresolved"
    if float(np.max(Phi)) <= zero_tol:
        return "zero"
    interior = Phi[1:-1] if Phi.ndim == 1 else Phi[1:-1, 1:-1]
    if interior.size and float(np.min(interior)) > 0.0:
        return "positive"
    return "nonnegative"


def trapezoid_weights(x: np.ndarray) -> np.ndarray:
    """Quadrature weights of the composite trapezoid rule on an increasing grid ``x``
    (nonuniform spacing allowed). Exact for piecewise-linear integrands; independent of the
    NumPy version (``np.trapz`` / ``np.trapezoid`` naming)."""
    x = check_finite_array("x", x)
    if x.ndim != 1 or x.size < 2:
        raise ValueError("coordinates must be a 1D array with at least two points")
    d = np.diff(x)
    if np.any(d <= 0.0):
        raise ValueError("coordinates must be strictly increasing")
    w = np.zeros_like(x)
    w[:-1] += d / 2.0
    w[1:] += d / 2.0
    return w


def presence_statistics(
    Phi: np.ndarray, x: np.ndarray | None = None, y: np.ndarray | None = None
) -> dict:
    """
    Statistics of a presence field with an explicit population and quadrature measure.

    Parameters
    ----------
    Phi : ndarray
        Field on the full grid: shape ``(n,)`` in 1D or ``(ny, nx)`` in 2D, boundary included.
    x : ndarray
        Coordinates along the first axis (1D) or the ``x`` axis (2D, length ``nx``).
    y : ndarray, optional
        Coordinates along the ``y`` axis (2D only, length ``ny``). Required for 2D input; a 2D
        field with a single coordinate array is ambiguous and rejected.

    Returns
    -------
    stats : dict
        - ``max``: maximum of the field over the full grid
        - ``mean``: mean over the *interior* nodes, zeros included
        - ``total``: integral by the composite (tensor) trapezoid rule on the given coordinates
        - ``support_fraction``: fraction of interior nodes with ``Phi > 0.01 * max``
        - ``dimension``: 1 or 2
        - ``interior_count``: number of interior nodes

    Raises
    ------
    ValueError
        On missing or mismatched coordinates, non-monotone coordinates, nonfinite data,
        or the ambiguous 2D call without ``y``.
    """
    Phi = check_finite_array("Phi", Phi)
    if x is None:
        raise ValueError("coordinates x are required (no implicit unit spacing)")
    if Phi.ndim == 1:
        if y is not None:
            raise ValueError("y must not be given for a 1D field")
        if Phi.size < 3:
            raise ValueError("a 1D field needs at least one interior node")
        wx = trapezoid_weights(check_finite_array("x", x, shape=Phi.shape))
        interior = Phi[1:-1]
        total = float(wx @ Phi)
        dimension = 1
    elif Phi.ndim == 2:
        if y is None:
            raise ValueError("2D fields need both x (length nx) and y (length ny) coordinates")
        ny, nx = Phi.shape
        if ny < 3 or nx < 3:
            raise ValueError("a 2D field needs at least one interior node")
        wx = trapezoid_weights(check_finite_array("x", x, shape=(nx,)))
        wy = trapezoid_weights(check_finite_array("y", y, shape=(ny,)))
        interior = Phi[1:-1, 1:-1]
        total = float(wy @ Phi @ wx)
        dimension = 2
    else:
        raise ValueError("Phi must be 1D or 2D")

    max_phi = float(Phi.max())
    stats: dict[str, Any] = {
        "max": max_phi,
        "mean": float(interior.mean()),
        "total": total,
        "dimension": dimension,
        "interior_count": int(interior.size),
    }
    if max_phi > 1e-10:
        stats["support_fraction"] = float((interior > 0.01 * max_phi).sum() / interior.size)
    else:
        stats["support_fraction"] = 0.0
    return stats


def linfty_bound(beta_b: float | np.ndarray, c: float | np.ndarray, p: float) -> float:
    """
    Theoretical L-infinity bound for nonnegative solutions of the continuum equation.

    From Lemma 3.10 (corrected form): any nonnegative C² solution satisfies
    ``max(Phi) <= (B/c0)^(1/(p-1))`` where ``B = max(beta_b)_+`` and ``c0 = min(c)``.
    The argument uses ``∇Φ = 0`` at an interior maximum, so it holds for every ``a ≥ 0`` in the
    continuum. For the *discrete* centered-difference model it is exact when ``a ≡ 0``
    (discrete maximum principle); with ``a > 0`` the discrete gradient need not vanish at a
    grid maximum, so the value is a heuristic reference there. For the finite-graph model use
    ``cd.graph.linfty_bound_graph`` instead (different bound).

    Algebraic step verified in Lean: ``linfty_bound_algebraic`` (CdFormal/LinftyAlgebraic.lean).

    Parameters
    ----------
    beta_b : float or ndarray
        Effective potential (scalar or field).
    c : float or ndarray
        Saturation coefficient (scalar or field).
    p : float
        Saturation exponent (must be > 1).

    Returns
    -------
    K : float
        Upper bound on max(Phi); ``0.0`` when ``beta_b <= 0`` everywhere.
    """
    B = float(np.max(beta_b))
    c0 = float(np.min(c))
    if not np.isfinite(B) or not np.isfinite(c0):
        raise ValueError("beta_b and c must be finite")
    if c0 <= 0:
        raise ValueError(f"Saturation c must be positive, got min(c)={c0}")
    p = check_exponent("p", p)
    if B <= 0:
        return 0.0
    return float((B / c0) ** (1.0 / (p - 1.0)))
