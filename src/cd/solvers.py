"""
Solvers for the Creative Determinant PDE framework.

Implements damped (optionally shifted) Picard iteration for the nonlinear elliptic BVP:
    -ΔΦ = a|∇Φ| + qΦ - c(Φ₊)ᵖ,  Φ|∂M = 0,    q = βb  (effective potential)

on uniform finite-difference grids with second-order centered stencils.

Meaning of success
------------------
A run is ``converged`` only when the returned field is finite, satisfies the boundary
condition exactly, satisfies the *discrete* equation to the documented residual tolerance
``||R||_∞ <= residual_atol + residual_rtol * scale`` (``scale`` = the larger of ``||A Φ||_∞``
and ``||rhs(Φ)||_∞``), and the last update was below ``tol``. Update size, tiny damping,
positivity clipping, nonfinite iterates and an exhausted budget never produce an accepted
solution; the ``termination`` field says what happened.

The positive-part convention ``(Φ₊)ᵖ`` matches the paper's operator formulation and the Lean
``SemioticBVP``; the iterates are additionally projected onto ``Φ >= 0`` (recorded in
``clipped_iterations``). A fixed point of the projected map is accepted only if its residual
is small, i.e. only if it solves the unprojected discrete equation.

Barriers and monotone iteration (a ≡ 0)
--------------------------------------
``barriers_1d`` builds the discrete analogue of the paper's ordered barriers:
``ε φ₁`` (subsolution when ``λ₁ < 0``) and the plateau ``M`` (supersolution). With the shift
``K >= c p M^{p-1} - q`` the shifted Picard map ``u ↦ (A + K)^{-1}(q u - c u^p + K u)`` is
monotone on ``[0, M]`` because ``(A + K)^{-1}`` is entrywise nonnegative (M-matrix), so the
iterates from the subsolution are nondecreasing and those from the plateau nonincreasing
(Theorem, discrete, ``a = 0``). With ``a > 0`` the centered gradient breaks monotonicity; the
barriers are then only initial guesses and the residual decides.
"""

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
from scipy.sparse import eye
from scipy.sparse.linalg import splu

from ._validation import (
    check_damping,
    check_exponent,
    check_finite_array,
    check_finite_scalar,
    check_nonnegative_scalar,
    check_positive_int,
    coefficient_1d,
    coefficient_2d,
    require_positive_coefficient,
)
from .analysis import classify_branch
from .analysis import linfty_bound as _linfty_bound
from .eigenvalues import principal_eigenpair_1d
from .operators import laplacian_1d_dirichlet, laplacian_2d_dirichlet


def _check_tolerances(
    tol: float, residual_atol: float, residual_rtol: float
) -> tuple[float, float, float]:
    tol_f = check_finite_scalar("tol", tol)
    if tol_f <= 0.0:
        raise ValueError(f"tol must be positive, got {tol!r}")
    atol_f = check_nonnegative_scalar("residual_atol", residual_atol)
    rtol_f = check_nonnegative_scalar("residual_rtol", residual_rtol)
    return tol_f, atol_f, rtol_f


def _plateau_level(q: float | np.ndarray, c: float | np.ndarray, p: float) -> float:
    """Smallest ``M >= 1`` with ``c M^{p-1} >= q_+`` everywhere (supersolution level)."""
    q_plus = float(np.max(np.maximum(q, 0.0)))
    c_min = float(np.min(c))
    return max(1.0, (q_plus / c_min) ** (1.0 / (p - 1.0)))


def _auto_shift(q: float | np.ndarray, c: float | np.ndarray, p: float, M: float) -> float:
    """``K = max(0, c_max p M^{p-1} - q_min) + 1`` makes ``s ↦ q s - c s^p + K s`` nondecreasing
    on ``[0, M]`` and keeps ``A + K`` an invertible M-matrix."""
    c_max = float(np.max(c))
    q_min = float(np.min(q))
    return max(0.0, c_max * p * M ** (p - 1.0) - q_min) + 1.0


def _resolve_shift(shift: object, q: float | np.ndarray, c: float | np.ndarray, p: float) -> float:
    if isinstance(shift, str):
        if shift != "auto":
            raise ValueError("shift must be a nonnegative number or 'auto'")
        return _auto_shift(q, c, p, _plateau_level(q, c, p))
    return check_nonnegative_scalar("shift", shift)


def barriers_1d(
    N: int, L: float, beta_b: float | np.ndarray, c: float | np.ndarray, p: float = 2.0
) -> dict[str, Any]:
    """
    Ordered discrete barriers for the 1D problem with ``a ≡ 0``.

    Parameters
    ----------
    N, L : int, float
        Grid size and domain length.
    beta_b, c : float or ndarray
        Effective potential ``q`` and carrying capacity (scalar, interior or full-grid arrays).
    p : float
        Saturation exponent.

    Returns
    -------
    dict
        ``lam1`` (discrete principal eigenvalue of ``A - q``), ``phi`` (positive eigenvector,
        ``max = 1``, full grid), ``eps`` (``min(1, (-λ₁/c_max)^{1/(p-1)})``, so that
        ``c ε^{p-1} <= -λ₁``), ``sub = ε φ`` (subsolution), ``M`` (plateau level, ``>= 1``),
        ``sup`` (plateau: ``M`` on the interior, ``0`` at the ends; supersolution),
        ``K`` (shift making the shifted Picard map monotone on ``[0, M]``).

    Raises
    ------
    ValueError
        If ``λ₁ >= 0``: no subsolution of this form exists, and for ``a ≡ 0`` no positive
        discrete solution exists either (necessity by testing against ``φ₁ > 0``).

    Notes
    -----
    Theorem (discrete, ``a = 0``). ``A φ = (q + λ₁) φ`` with ``φ > 0`` on the interior, so
    ``A(εφ) - q εφ + c (εφ)^p = εφ(λ₁ + c (εφ)^{p-1}) <= εφ(λ₁ + c ε^{p-1}) <= 0``: ``εφ`` is a
    subsolution. The plateau has ``(A M)_i = M/h² >= 0`` at the two nodes adjacent to the
    boundary and ``0`` elsewhere, and ``q M - c M^p <= 0``: it is a supersolution.
    """
    N = check_positive_int("N", N)
    p = check_exponent("p", p)
    q = coefficient_1d("beta_b", beta_b, N)
    c_i = coefficient_1d("c", c, N)
    require_positive_coefficient("c", c_i)
    lam1, phi = principal_eigenpair_1d(N, L, q)
    if not lam1 < 0.0:
        raise ValueError(
            f"barriers require λ₁ < 0 (got λ₁ = {lam1:.6g}); for a = 0 no positive solution exists"
        )
    c_max = float(np.max(c_i))
    eps = min(1.0, (-lam1 / c_max) ** (1.0 / (p - 1.0)))
    M = _plateau_level(q, c_i, p)
    sup = np.full(N + 2, M)
    sup[0] = sup[-1] = 0.0
    return {
        "lam1": lam1,
        "phi": phi,
        "eps": float(eps),
        "sub": eps * phi,
        "M": M,
        "sup": sup,
        "K": _auto_shift(q, c_i, p, M),
    }


def _monotone_label(min_step: float, max_step: float, tol: float) -> str:
    nondecreasing = min_step >= -tol
    nonincreasing = max_step <= tol
    if nondecreasing and nonincreasing:
        return "constant"
    if nondecreasing:
        return "nondecreasing"
    if nonincreasing:
        return "nonincreasing"
    return "non-monotone"


def _picard_loop(
    A,
    K: float,
    Phi_int: np.ndarray,
    reaction,
    *,
    max_iter: int,
    tol: float,
    residual_atol: float,
    residual_rtol: float,
    damping: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Shared iteration: ``(A + K) Φ_new = reaction(Φ) + K Φ``, damped and projected onto Φ >= 0.

    Convergence is decided by the residual of the *unshifted, unprojected* discrete equation.
    """
    n = A.shape[0]
    lu = splu((A + K * eye(n, format="csr")).tocsc())
    converged = False
    termination = "max_iter"
    it = 0
    err = float("nan")
    clipped_iterations = 0
    clipped_last = False
    min_step = float("inf")
    max_step = float("-inf")

    def _residual_state(v: np.ndarray) -> tuple[float, float, np.ndarray]:
        Av = A @ v
        rhs = reaction(v)
        r = Av - rhs
        s = max(float(np.max(np.abs(Av))), float(np.max(np.abs(rhs))))
        return float(np.max(np.abs(r))), s, rhs

    # Overflow to inf/nan is caught by the finiteness checks below and reported as a
    # "nonfinite" termination; the floating-point warnings would only be noise.
    with np.errstate(over="ignore", invalid="ignore"):
        res_inf, scale, rhs = _residual_state(Phi_int)
    if not np.isfinite(res_inf):
        termination = "nonfinite"
    elif res_inf <= residual_atol + residual_rtol * scale:
        # The (nonnegative) initial field already solves the discrete equation: zero
        # iterations and a zero update, so the accepted result carries finite diagnostics.
        converged = True
        termination = "converged"
        err = 0.0
    else:
        for it in range(1, max_iter + 1):
            with np.errstate(over="ignore", invalid="ignore"):
                Phi_new = lu.solve(rhs + K * Phi_int)
                Phi_next = (1.0 - damping) * Phi_int + damping * Phi_new
            projected = np.maximum(Phi_next, 0.0)
            clipped_last = bool(np.any(projected != Phi_next))
            if clipped_last:
                clipped_iterations += 1
            if not np.all(np.isfinite(projected)):
                termination = "nonfinite"
                Phi_int = projected
                res_inf, scale = float("nan"), float("nan")
                err = float("nan")
                break
            step = projected - Phi_int
            err = float(np.max(np.abs(step)))
            min_step = min(min_step, float(step.min()))
            max_step = max(max_step, float(step.max()))
            Phi_int = projected
            with np.errstate(over="ignore", invalid="ignore"):
                res_inf, scale, rhs = _residual_state(Phi_int)
            if not np.isfinite(res_inf):
                termination = "nonfinite"
                break
            if res_inf <= residual_atol + residual_rtol * scale and err < tol:
                converged = True
                termination = "converged"
                break
            if err == 0.0:
                termination = "stagnation"
                break

    finite = bool(np.all(np.isfinite(Phi_int)))
    step_tol = 1e-12 * max(1.0, float(np.max(np.abs(Phi_int))) if finite else 1.0)
    info: dict[str, Any] = {
        "iters": it,
        "inf_err": err,
        "converged": converged,
        "termination": termination,
        "residual_inf": res_inf,
        "residual_scale": scale,
        "residual_atol": residual_atol,
        "residual_rtol": residual_rtol,
        "clipped_iterations": clipped_iterations,
        "clipped": clipped_last,
        "monotone": _monotone_label(min_step, max_step, step_tol) if it > 0 else "constant",
        "shift": K,
        "damping": damping,
    }
    return Phi_int, info


def _attach_bound(info: dict[str, Any], beta_b, c, p: float, a_is_zero: bool) -> None:
    """Record the continuum L∞ reference bound; warn when a *converged* run exceeds it.

    The bound is a theorem for the discrete model only when ``a ≡ 0``; otherwise it is a
    continuum reference, and exceeding it is reported without warning.
    """
    try:
        K = _linfty_bound(beta_b, c, p)
    except ValueError:
        info["linfty_bound"] = None
        return
    info["linfty_bound"] = K
    if a_is_zero and info["converged"] and K > 0 and info["maxPhi"] > K * (1.0 + 1e-6):
        warnings.warn(
            f"Converged field max(Phi)={info['maxPhi']:.6g} exceeds the discrete maximum-principle "
            f"bound K={K:.6g} for a = 0; this indicates a numerical defect.",
            stacklevel=3,
        )


def _require_nonnegative_initial(arr: np.ndarray) -> None:
    """Policy: the solvers seek nonnegative solutions and project iterates onto Phi >= 0, so
    negative initial data is rejected rather than silently accepted or clipped."""
    if np.any(arr < 0.0):
        raise ValueError(
            "initial_guess must be nonnegative: the solver seeks nonnegative solutions "
            f"(min = {float(np.min(arr))})"
        )


def _initial_1d(
    initial_guess, N: int, L: float, x: np.ndarray, q, c, p: float, initial_amplitude: float
) -> np.ndarray:
    if initial_guess is None:
        amp = check_nonnegative_scalar("initial_amplitude", initial_amplitude)
        return (amp * np.sin(np.pi * x / L))[1:-1].copy()
    if isinstance(initial_guess, str):
        if initial_guess not in ("subsolution", "plateau"):
            raise ValueError("initial_guess must be None, 'subsolution', 'plateau', or an array")
        bar = barriers_1d(N, L, q, c, p)
        return (bar["sub"] if initial_guess == "subsolution" else bar["sup"])[1:-1].copy()
    arr = check_finite_array("initial_guess", initial_guess)
    if arr.shape == (N + 2,):
        arr = arr[1:-1]
    elif arr.shape != (N,):
        raise ValueError(f"initial_guess must have length {N} or {N + 2}, got shape {arr.shape}")
    _require_nonnegative_initial(arr)
    return arr.copy()


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
    *,
    residual_atol: float = 1e-8,
    residual_rtol: float = 1e-8,
    initial_guess: str | np.ndarray | None = None,
    shift: float | str = 0.0,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Solve the 1D Creative Determinant equation by damped, residual-validated Picard iteration.

    Equation:
        -Φ'' = a|Φ'| + qΦ - c(Φ₊)ᵖ,  Φ(0) = Φ(L) = 0,   q = βb.

    Parameters
    ----------
    L : float
        Domain length (> 0).
    N : int
        Number of interior grid points (>= 1).
    a : float or ndarray
        Creative drive coefficient (gradient term), finite; scalar, interior (N) or full (N+2).
    beta_b : float or ndarray
        Effective potential q = βb (same shapes).
    c : float or ndarray
        Saturation coefficient, positive everywhere (same shapes).
    p : float, default=2.0
        Saturation exponent (> 1).
    max_iter : int, default=8000
        Iteration budget (>= 1).
    tol : float, default=1e-10
        Update-size tolerance (L∞ norm of the last update); required in addition to the
        residual criterion. Not sufficient on its own.
    damping : float, default=0.5
        Damping factor in (0, 1].
    initial_amplitude : float, default=0.1
        Amplitude of the default initial guess ``initial_amplitude * sin(πx/L)``.
    residual_atol, residual_rtol : float
        Residual criterion ``||R||_∞ <= residual_atol + residual_rtol * scale``.
    initial_guess : None, "subsolution", "plateau" or ndarray
        Starting field. The barriers are those of ``barriers_1d`` (they need ``λ₁ < 0``).
    shift : float or "auto"
        Shift K of the linear solve ``(A + K)Φ_new = rhs + KΦ``. ``"auto"`` chooses the value
        that makes the iteration monotone on ``[0, M]`` when ``a ≡ 0``.

    Returns
    -------
    x : ndarray
        Grid points including boundaries, shape (N+2,).
    Phi : ndarray
        Field including boundary values, shape (N+2,).
    info : dict
        - 'converged': residual and update criteria met on a finite field
        - 'termination': 'converged' | 'max_iter' | 'nonfinite' | 'stagnation'
        - 'iters': iterations actually performed
        - 'inf_err': L∞ norm of the last update
        - 'residual_inf', 'residual_scale', 'residual_atol', 'residual_rtol'
        - 'boundary_err': max |Φ| on the boundary (0 by construction)
        - 'maxPhi', 'min_interior'
        - 'branch': 'zero' | 'positive' | 'nonnegative' | 'unresolved' | 'invalid'
        - 'clipped_iterations', 'clipped': positivity projection activity
        - 'monotone': monotonicity of the iterate sequence
        - 'shift', 'damping', 'linfty_bound'

    Raises
    ------
    ValueError
        On invalid grid, length, exponent, coefficients (nonfinite, wrong shape, c <= 0),
        damping outside (0, 1], non-positive tolerances, or a non-positive budget.

    Notes
    -----
    Zero is an exact solution above as well as below the threshold; a run that returns the
    zero branch does not show that no positive branch exists. Use ``initial_guess="subsolution"``
    to start from the discrete lower barrier when ``λ₁ < 0``.

    Example
    -------
    >>> x, Phi, info = solve_1d_picard(L=1.0, N=400, a=0.0, beta_b=15.0, c=10.0)
    >>> info['converged'], info['branch']
    (True, 'positive')
    """
    A, h = laplacian_1d_dirichlet(N, L)
    N = int(N)
    L = float(L)
    p = check_exponent("p", p)
    max_iter = check_positive_int("max_iter", max_iter)
    damping = check_damping("damping", damping)
    tol, residual_atol, residual_rtol = _check_tolerances(tol, residual_atol, residual_rtol)
    a_int = coefficient_1d("a", a, N)
    q_int = coefficient_1d("beta_b", beta_b, N)
    c_int = coefficient_1d("c", c, N)
    require_positive_coefficient("c", c_int)
    K = _resolve_shift(shift, q_int, c_int, p)

    x = np.linspace(0, L, N + 2)
    Phi_int = _initial_1d(initial_guess, N, L, x, q_int, c_int, p, initial_amplitude)

    def reaction(v: np.ndarray) -> np.ndarray:
        full = np.zeros(N + 2)
        full[1:-1] = v
        gabs = np.abs((full[2:] - full[:-2]) / (2 * h))
        return a_int * gabs + q_int * v - c_int * np.maximum(v, 0.0) ** p

    Phi_int, info = _picard_loop(
        A,
        K,
        Phi_int,
        reaction,
        max_iter=max_iter,
        tol=tol,
        residual_atol=residual_atol,
        residual_rtol=residual_rtol,
        damping=damping,
    )

    Phi = np.zeros(N + 2)
    Phi[1:-1] = Phi_int
    info["boundary_err"] = 0.0
    info["maxPhi"] = float(np.max(Phi)) if np.all(np.isfinite(Phi)) else float("nan")
    info["min_interior"] = float(np.min(Phi_int)) if np.all(np.isfinite(Phi_int)) else float("nan")
    info["branch"] = classify_branch(Phi, info)
    _attach_bound(info, q_int, c_int, p, a_is_zero=bool(np.all(np.asarray(a_int) == 0.0)))
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
    *,
    residual_atol: float = 1e-8,
    residual_rtol: float = 1e-8,
    initial_guess: np.ndarray | None = None,
    shift: float | str = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """
    Solve the 2D Creative Determinant equation on a rectangle by residual-validated Picard iteration.

    Equation:
        -ΔΦ = a|∇Φ| + β b(x,y) Φ - c(Φ₊)ᵖ,  Φ|∂M = 0.

    Parameters
    ----------
    Lx, Ly : float
        Domain lengths (> 0).
    Nx, Ny : int
        Number of interior grid points in each direction (>= 1).
    a : float or ndarray
        Creative drive: scalar, interior (Ny, Nx), full (Ny+2, Nx+2), or flat interior array.
    beta_b : float or ndarray
        Viability gain β (scalar) or, like the 1D solver, the effective potential itself as
        an interior ``(Ny, Nx)``, full ``(Ny+2, Nx+2)`` or flat interior array. The effective
        potential is ``q = beta_b * b_field`` (``b_field = 1`` if not given, so ``beta_b`` is
        then ``q``).
    c : float or ndarray
        Saturation coefficient (same shapes as ``a``), positive everywhere.
    p : float, default=2.0
        Saturation exponent (> 1).
    max_iter, tol, damping, initial_amplitude
        As in ``solve_1d_picard`` (default ``tol=1e-8``).
    b_field : ndarray, optional
        Viability field on the interior grid, shape (Ny, Nx).
    residual_atol, residual_rtol, initial_guess, shift
        As in ``solve_1d_picard``; ``initial_guess`` is an array of shape (Ny, Nx) or
        (Ny+2, Nx+2).

    Returns
    -------
    X, Y : ndarray
        Meshgrid arrays including boundaries, shape (Ny+2, Nx+2).
    Phi : ndarray
        Field including boundary values, shape (Ny+2, Nx+2).
    info : dict
        Same keys as ``solve_1d_picard``.

    Raises
    ------
    ValueError
        On invalid lengths, grid sizes, exponent, coefficients, damping, tolerances, budget,
        or a ``b_field`` / ``initial_guess`` of the wrong shape.
    """
    A, hx, hy = laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)
    Nx, Ny = int(Nx), int(Ny)
    Lx, Ly = float(Lx), float(Ly)
    p = check_exponent("p", p)
    max_iter = check_positive_int("max_iter", max_iter)
    damping = check_damping("damping", damping)
    tol, residual_atol, residual_rtol = _check_tolerances(tol, residual_atol, residual_rtol)
    beta = coefficient_2d("beta_b", beta_b, Ny, Nx)
    a_flat = coefficient_2d("a", a, Ny, Nx)
    c_flat = coefficient_2d("c", c, Ny, Nx)
    require_positive_coefficient("c", c_flat)
    if b_field is None:
        b_flat: float | np.ndarray = 1.0
    else:
        b_arr = check_finite_array("b_field", b_field)
        if b_arr.shape != (Ny, Nx):
            raise ValueError(f"b_field must have shape (Ny, Nx) = ({Ny}, {Nx}), got {b_arr.shape}")
        b_flat = b_arr.reshape(-1)
    q_flat = beta * b_flat
    K = _resolve_shift(shift, q_flat, c_flat, p)

    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    X, Y = np.meshgrid(x, y)
    if initial_guess is None:
        amp = check_nonnegative_scalar("initial_amplitude", initial_amplitude)
        Phi0 = amp * np.sin(np.pi * X / Lx) * np.sin(np.pi * Y / Ly)
        Phi_int = Phi0[1:-1, 1:-1].reshape(-1).copy()
    else:
        arr = check_finite_array("initial_guess", initial_guess)
        if arr.shape == (Ny + 2, Nx + 2):
            Phi_int = arr[1:-1, 1:-1].reshape(-1).copy()
        elif arr.shape == (Ny, Nx):
            Phi_int = arr.reshape(-1).copy()
        else:
            raise ValueError(
                f"initial_guess must have shape ({Ny}, {Nx}) or ({Ny + 2}, {Nx + 2}), got {arr.shape}"
            )

    _require_nonnegative_initial(Phi_int)

    def reaction(v: np.ndarray) -> np.ndarray:
        full = np.zeros((Ny + 2, Nx + 2))
        full[1:-1, 1:-1] = v.reshape(Ny, Nx)
        Phi_x = (full[1:-1, 2:] - full[1:-1, :-2]) / (2 * hx)
        Phi_y = (full[2:, 1:-1] - full[:-2, 1:-1]) / (2 * hy)
        gabs = np.sqrt(Phi_x**2 + Phi_y**2).reshape(-1)
        return a_flat * gabs + q_flat * v - c_flat * np.maximum(v, 0.0) ** p

    Phi_int, info = _picard_loop(
        A,
        K,
        Phi_int,
        reaction,
        max_iter=max_iter,
        tol=tol,
        residual_atol=residual_atol,
        residual_rtol=residual_rtol,
        damping=damping,
    )

    Phi = np.zeros((Ny + 2, Nx + 2))
    Phi[1:-1, 1:-1] = Phi_int.reshape(Ny, Nx)
    info["boundary_err"] = 0.0
    info["maxPhi"] = float(np.max(Phi)) if np.all(np.isfinite(Phi)) else float("nan")
    info["min_interior"] = float(np.min(Phi_int)) if np.all(np.isfinite(Phi_int)) else float("nan")
    info["branch"] = classify_branch(Phi, info)
    _attach_bound(info, q_flat, c_flat, p, a_is_zero=bool(np.all(np.asarray(a_flat) == 0.0)))
    return X, Y, Phi, info
