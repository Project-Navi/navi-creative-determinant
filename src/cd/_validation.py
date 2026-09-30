"""Input validation shared by the numerical modules.

All checks fail fast with ``ValueError`` at the system boundary: nonfinite inputs, wrong shapes,
non-integer grid sizes and the domain violations each function documents (for example ``p <= 1``
or ``c <= 0``) never reach a solver. The scalar checks reject strings and bools. Array inputs are
converted with ``np.asarray(value, dtype=float)``, which accepts numeric strings and bools; only
their finiteness and shape are checked unless a function documents more.
"""

from __future__ import annotations

import numbers

import numpy as np


def check_positive_int(name: str, value: object) -> int:
    """Return ``value`` as an ``int`` if it is an integer (not ``bool``) and ``>= 1``."""
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f"{name} must be a positive integer, got {value!r}")
    ivalue = int(value)
    if ivalue < 1:
        raise ValueError(f"{name} must be a positive integer, got {value!r}")
    return ivalue


def check_finite_scalar(name: str, value: object) -> float:
    """Return ``value`` as a finite ``float``."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"{name} must be a finite real number, got {value!r}")
    fvalue = float(value)
    if not np.isfinite(fvalue):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return fvalue


def check_positive_scalar(name: str, value: object) -> float:
    """Return ``value`` as a finite ``float`` strictly greater than zero."""
    fvalue = check_finite_scalar(name, value)
    if fvalue <= 0.0:
        raise ValueError(f"{name} must be positive, got {value!r}")
    return fvalue


def check_nonnegative_scalar(name: str, value: object) -> float:
    """Return ``value`` as a finite ``float`` that is ``>= 0``."""
    fvalue = check_finite_scalar(name, value)
    if fvalue < 0.0:
        raise ValueError(f"{name} must be nonnegative, got {value!r}")
    return fvalue


def check_unit_interval_scalar(name: str, value: object) -> float:
    """Return ``value`` as a finite ``float`` in ``[0, 1]`` (the care / coherence intensities)."""
    fvalue = check_finite_scalar(name, value)
    if not 0.0 <= fvalue <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1], got {value!r}")
    return fvalue


def check_exponent(name: str, value: object) -> float:
    """Return the saturation exponent as a finite ``float`` with ``p > 1``."""
    fvalue = check_finite_scalar(name, value)
    if fvalue <= 1.0:
        raise ValueError(f"{name} must be > 1, got {value!r}")
    return fvalue


def check_damping(name: str, value: object) -> float:
    """Return a damping factor in ``(0, 1]``."""
    fvalue = check_finite_scalar(name, value)
    if not 0.0 < fvalue <= 1.0:
        raise ValueError(f"{name} must lie in (0, 1], got {value!r}")
    return fvalue


def check_finite_array(
    name: str, value: object, shape: tuple[int, ...] | None = None
) -> np.ndarray:
    """Return ``value`` as a finite float array, optionally of the given shape.

    The conversion is ``np.asarray(value, dtype=float)``: numeric strings and bools are coerced,
    and the values are not range-checked.
    """
    arr = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite everywhere")
    if shape is not None and arr.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {arr.shape}")
    return arr


def check_finite_field(name: str, value: object) -> float | np.ndarray:
    """A finite real scalar (never a ``bool`` or a string) or a finite float array of any shape.

    The shape-free counterpart of ``coefficient_1d`` / ``coefficient_2d`` for quantities that
    are reduced by ``max`` / ``min`` rather than placed on a grid.
    """
    if np.isscalar(value):
        return check_finite_scalar(name, value)
    return check_finite_array(name, value)


def coefficient_1d(name: str, value: object, N: int) -> float | np.ndarray:
    """A scalar coefficient, or an interior (``N``) or full-grid (``N + 2``) array.

    Full-grid arrays are reduced to their interior part. Returned arrays are finite.
    """
    if np.isscalar(value):
        return check_finite_scalar(name, value)
    arr = check_finite_array(name, value)
    if arr.shape == (N + 2,):
        return arr[1:-1]
    if arr.shape == (N,):
        return arr
    raise ValueError(
        f"{name}: expected a scalar, length {N}, or length {N + 2}; got shape {arr.shape}"
    )


def coefficient_2d(name: str, value: object, Ny: int, Nx: int) -> float | np.ndarray:
    """A scalar coefficient, or an interior ``(Ny, Nx)`` / full ``(Ny+2, Nx+2)`` array, or a
    flat interior array of length ``Ny * Nx`` (row-major, x fastest).

    Returned arrays are flat interior arrays of length ``Ny * Nx``.
    """
    if np.isscalar(value):
        return check_finite_scalar(name, value)
    arr = check_finite_array(name, value)
    if arr.shape == (Ny + 2, Nx + 2):
        return arr[1:-1, 1:-1].reshape(-1)
    if arr.shape == (Ny, Nx):
        return arr.reshape(-1)
    if arr.shape == (Ny * Nx,):
        return arr
    raise ValueError(
        f"{name}: expected a scalar, shape ({Ny}, {Nx}), ({Ny + 2}, {Nx + 2}), or ({Ny * Nx},); got {arr.shape}"
    )


def require_positive_coefficient(name: str, value: float | np.ndarray) -> None:
    """The carrying capacity must be strictly positive everywhere."""
    if float(np.min(value)) <= 0.0:
        raise ValueError(
            f"{name} must be positive everywhere, got min({name})={float(np.min(value))}"
        )
