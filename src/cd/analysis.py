"""
Analysis utilities for the Creative Determinant framework.

Provides tools for validating numerical solutions:
- Residual computation (does Φ satisfy the *discrete* equation?)
- Fail-closed convergence diagnostics
- Branch classification (zero / positive / nonnegative / unresolved / invalid)
- Spatial statistics with an explicit population and quadrature measure
"""

from __future__ import annotations

import numbers
from typing import Any

import numpy as np

from ._validation import (
    check_exponent,
    check_finite_array,
    check_finite_field,
    check_positive_scalar,
    coefficient_1d,
    coefficient_2d,
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


def _interior_2d(name: str, value: object, Ny: int, Nx: int) -> float | np.ndarray:
    """Scalar, or an interior ``(Ny, Nx)`` array, from any shape the 2D solver accepts."""
    coeff = coefficient_2d(name, value, Ny, Nx)
    if isinstance(coeff, float):
        return coeff
    return np.reshape(coeff, (Ny, Nx))


def residual_2d(
    Phi: np.ndarray,
    a_full: float | np.ndarray,
    beta_b_full: float | np.ndarray,
    c_full: float | np.ndarray,
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
    a_full, beta_b_full, c_full : float or ndarray
        Coefficients: scalars, full-grid arrays of shape (Ny+2, Nx+2), interior arrays of
        shape (Ny, Nx), or flat interior arrays (the same shapes the 2D solver accepts).
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
    Ny, Nx = Phi.shape[0] - 2, Phi.shape[1] - 2
    a_int = _interior_2d("a_full", a_full, Ny, Nx)
    bb_int = _interior_2d("beta_b_full", beta_b_full, Ny, Nx)
    c_int = _interior_2d("c_full", c_full, Ny, Nx)
    p = check_exponent("p", p)
    hx = check_positive_scalar("hx", hx)
    hy = check_positive_scalar("hy", hy)
    require_positive_coefficient("c_full", c_int)

    Phi_xx = (Phi[1:-1, 2:] - 2 * Phi[1:-1, 1:-1] + Phi[1:-1, :-2]) / hx**2
    Phi_yy = (Phi[2:, 1:-1] - 2 * Phi[1:-1, 1:-1] + Phi[:-2, 1:-1]) / hy**2
    lap = Phi_xx + Phi_yy

    dPhidx = (Phi[1:-1, 2:] - Phi[1:-1, :-2]) / (2 * hx)
    dPhidy = (Phi[2:, 1:-1] - Phi[:-2, 1:-1]) / (2 * hy)
    gmag = np.sqrt(dPhidx**2 + dPhidy**2)

    Phi_int = Phi[1:-1, 1:-1]
    rhs = a_int * gmag + bb_int * Phi_int - c_int * np.maximum(Phi_int, 0.0) ** p
    return -lap - rhs


def _monotone_label(min_step: float, max_step: float, tol: float) -> str:
    """Monotonicity of an iterate sequence from the extreme entrywise steps it recorded.

    Shared by the finite-difference solvers and the finite-graph solver, which record
    ``min_step`` / ``max_step`` over their own (different) iterations; the label itself is a
    property of the recorded steps only.
    """
    nondecreasing = min_step >= -tol
    nonincreasing = max_step <= tol
    if nondecreasing and nonincreasing:
        return "constant"
    if nondecreasing:
        return "nondecreasing"
    if nonincreasing:
        return "nonincreasing"
    return "non-monotone"


def _finite(value: Any) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def _is_real(value: Any) -> bool:
    """A genuine real number (Python or NumPy), never a bool."""
    return isinstance(value, numbers.Real) and not isinstance(value, (bool, np.bool_))


def _is_count(value: Any) -> bool:
    """An integral, non-boolean, nonnegative count (``int`` or ``numpy.integer``)."""
    return (
        isinstance(value, numbers.Integral)
        and not isinstance(value, (bool, np.bool_))
        and int(value) >= 0
    )


_REQUIRED_DIAGNOSTICS = (
    "converged",
    "termination",
    "iters",
    "inf_err",
    "residual_inf",
    "residual_scale",
    "residual_atol",
    "residual_rtol",
    "tol",
    "boundary_err",
    "maxPhi",
)

# Real, finite and >= 0 (norms and tolerances); ``maxPhi`` only needs to be real and finite.
_NONNEGATIVE_DIAGNOSTICS = (
    "inf_err",
    "residual_inf",
    "residual_scale",
    "residual_atol",
    "residual_rtol",
    "boundary_err",
)

_UNVALIDATED = "Not accepted: unvalidated report"


def _report_field_error(info: dict) -> str | None:
    """First violated type/finiteness/sign invariant of a complete report, or ``None``."""
    if not isinstance(info["converged"], (bool, np.bool_)):
        return f"'converged' must be a bool (got {type(info['converged']).__name__})"
    if not isinstance(info["termination"], str):
        return f"'termination' must be a str (got {type(info['termination']).__name__})"
    if not _is_count(info["iters"]):
        return f"'iters' must be a finite nonnegative integer count (got {info['iters']!r})"
    for key in _NONNEGATIVE_DIAGNOSTICS:
        value = info[key]
        if not (_is_real(value) and _finite(value) and float(value) >= 0.0):
            return f"'{key}' must be a finite real number >= 0 (got {value!r})"
    if not (_is_real(info["maxPhi"]) and _finite(info["maxPhi"])):
        return f"'maxPhi' must be a finite real number (got {info['maxPhi']!r})"
    tol = info["tol"]
    if not (_is_real(tol) and _finite(tol) and float(tol) > 0.0):
        return f"'tol' must be a finite real number > 0 (got {tol!r})"
    return None


def check_convergence(info: dict) -> tuple[bool, str]:
    """
    Fail-closed convergence check on a solver ``info`` dictionary.

    The boolean ``converged`` flag is never trusted on its own: the report is accepted only
    when it is complete and every numerical invariant behind the solver's acceptance rule is
    re-validated from the recorded numbers.

    * every key in ``_REQUIRED_DIAGNOSTICS`` is present; a missing key (including ``tol``)
      gives an *unvalidated, incomplete report* result, never a pass;
    * ``converged`` is a genuine bool and ``termination`` a str;
    * ``iters`` is an integral, non-boolean, finite, nonnegative count;
    * ``inf_err``, ``residual_inf``, ``residual_scale``, ``residual_atol``, ``residual_rtol``
      and ``boundary_err`` are real, finite and ``>= 0``; ``maxPhi`` is real and finite;
      ``tol`` is finite and ``> 0``;
    * the residual limit ``residual_atol + residual_rtol * residual_scale`` is finite (finite
      inputs can still overflow to ``inf``, which would accept any residual);
    * ``converged`` is ``True`` and ``termination == "converged"``;
    * residual criterion, exactly as the solver applies it (non-strict):
      ``residual_inf <= residual_atol + residual_rtol * residual_scale``;
    * update criterion, exactly as the solver applies it: after at least one iteration
      (``iters > 0``) the last update satisfies ``inf_err < tol`` (strict); a solved start
      (``iters == 0``, the initial field already solves the discrete equation) records
      ``inf_err == 0.0`` exactly;
    * ``boundary_err <= residual_atol`` (the solvers return exactly zero boundary values).

    Iteration exhaustion, stagnation and nonfinite iterates are never accepted. There is no
    "nearly converged" category.

    A report without ``tol`` cannot have its update criterion re-validated and is reported
    as unvalidated / incomplete, never accepted; re-run the solver for a complete report.

    Parameters
    ----------
    info : dict
        Solver info as returned by ``solve_1d_picard`` / ``solve_2d_picard``. The finite-graph
        solver ``cd.graph.solve_graph`` reports different keys and is not covered.

    Returns
    -------
    ok : bool
        True only for an accepted solution.
    message : str
        Diagnostic message; a rejection says that the report is not accepted and why,
        including the termination reason where it is known.
    """
    iters = info.get("iters", "?")
    term = info.get("termination", "unknown")
    missing = [k for k in _REQUIRED_DIAGNOSTICS if k not in info]
    if missing:
        return (
            False,
            f"{_UNVALIDATED}: incomplete diagnostics (missing {missing}; termination={term})",
        )
    field_error = _report_field_error(info)
    if field_error is not None:
        return False, f"{_UNVALIDATED}: {field_error} (iters={iters!r}, termination={term!r})"
    iters = int(info["iters"])
    inf_err = float(info["inf_err"])
    res = float(info["residual_inf"])
    atol = float(info["residual_atol"])
    rtol = float(info["residual_rtol"])
    scale = float(info["residual_scale"])
    tol = float(info["tol"])
    bound = atol + rtol * scale
    if not np.isfinite(bound):
        return (
            False,
            f"{_UNVALIDATED}: residual limit residual_atol + residual_rtol * residual_scale is "
            f"not finite ({atol:.2e} + {rtol:.2e} * {scale:.2e})",
        )
    if bool(info["converged"]) is not True or term != "converged":
        return (
            False,
            f"Did not converge after {iters} iterations (termination={term}, update={inf_err:.2e}, residual={res:.2e})",
        )
    if res > bound:
        return False, f"Not accepted: residual {res:.2e} exceeds its recorded tolerance {bound:.2e}"
    if iters == 0:
        if inf_err != 0.0:
            return (
                False,
                f"Not accepted: a solved start (iters=0) must record a zero update, got {inf_err:.2e}",
            )
    elif not inf_err < tol:
        return (
            False,
            f"Not accepted: last update {inf_err:.2e} is not below the update tolerance {tol:.2e}",
        )
    if float(info["boundary_err"]) > atol:
        return (
            False,
            f"Not accepted: boundary error {float(info['boundary_err']):.2e} (Dirichlet data violated)",
        )
    return (
        True,
        f"Converged in {iters} iterations (update={inf_err:.2e} < {tol:.2e}, residual={res:.2e} <= {bound:.2e})",
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
    This is an amplitude label only, not a validated solution classification: a missing
    ``converged`` flag is treated as not converged, and
    ``classify_branch`` gives the finer, sign-checked classification used by the notebook
    (``zero`` / ``positive`` / ``nonnegative`` / ``unresolved`` / ``invalid``).
    """
    max_phi = info.get("maxPhi", float("nan"))
    if not _finite(max_phi) or info.get("termination") == "nonfinite":
        return "invalid"
    if "residual_inf" in info and not _finite(info["residual_inf"]):
        return "invalid"
    if info.get("converged", False) is not True:
        return "unresolved"
    return "trivial" if float(max_phi) < threshold else "nontrivial"


def classify_branch(Phi: np.ndarray, info: dict, zero_tol: float = _ZERO_BRANCH_TOL) -> str:
    """
    Classify a returned field together with its solver diagnostics.

    Returns
    -------
    str
        ``'invalid'`` if the field or diagnostics are nonfinite, or if the field has a
        negative entry (the solvers only return nonnegative fields; a negative or
        sign-changing field is never a ``zero`` or ``nonnegative`` branch);
        ``'unresolved'`` if the solver did not converge (near-threshold failure is not
        evidence of nonexistence);
        ``'zero'`` if converged and ``max |Phi| <= zero_tol`` (the zero solution is exact on
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
    if float(np.min(Phi)) < 0.0:
        return "invalid"
    if not info.get("converged", False):
        return "unresolved"
    if float(np.max(np.abs(Phi))) <= zero_tol:
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
        - ``support_fraction``: fraction of interior nodes with ``Phi > 0.01 * max``, or
          ``0.0`` when ``max <= 1e-10``. This floor is not the zero-branch tolerance of
          ``classify_branch``: a positive field below that tolerance keeps its support.
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

    Lemma 3.10: any nonnegative C² solution satisfies ``max(Phi) <= (B/c0)^(1/(p-1))`` where
    ``B = max(beta_b)_+`` and ``c0 = min(c)``. The argument uses ``∇Φ = 0`` at an interior
    maximum, so it holds for every ``a ≥ 0`` in the continuum. Theorem (discrete maximum
    principle): for the *discrete* centered-difference model the same bound holds when
    ``a ≡ 0``. Heuristic: with ``a > 0`` the discrete gradient need not vanish at a grid
    maximum, so the value is only a reference there. For the finite-graph model use
    ``cd.graph.linfty_bound_graph`` instead (Proposition 3.30, a different bound).

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

    Raises
    ------
    ValueError
        If ``beta_b`` or ``c`` is not a finite number or finite array, ``c`` is not positive
        everywhere, or ``p <= 1``.
    """
    B = float(np.max(check_finite_field("beta_b", beta_b)))
    c_field = check_finite_field("c", c)
    require_positive_coefficient("c", c_field)
    c0 = float(np.min(c_field))
    p = check_exponent("p", p)
    if B <= 0:
        return 0.0
    return float((B / c0) ** (1.0 / (p - 1.0)))
