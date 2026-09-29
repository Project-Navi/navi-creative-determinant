"""
Field constructors for the Creative Determinant framework.

Provides utilities for constructing the characteristic fields:
- Care (κ), Coherence (γ), Contradiction (μ)
- Viability potential b(x) = κγ - λμ (canonical closure)
- Creative drive a(x) = κγμ
"""

import numpy as np

from ._validation import (
    check_finite_array,
    check_finite_scalar,
    check_nonnegative_scalar,
    check_positive_scalar,
    check_unit_interval_scalar,
)


def viability_canonical(
    kappa: float,
    gamma: float,
    mu: np.ndarray,
    lam: float,
) -> np.ndarray:
    """
    Compute canonical viability potential.

    b(x) = κγ - λμ(x)

    Parameters
    ----------
    kappa : float
        Care intensity ∈ [0, 1].
    gamma : float
        Coherence intensity ∈ [0, 1].
    mu : ndarray
        Contradiction field ∈ [0, 1] (finite).
    lam : float
        Contradiction cost parameter λ ≥ 0 (λ = 0 switches the contradiction cost off).

    Returns
    -------
    b : ndarray
        Viability potential (same shape as mu).

    Raises
    ------
    ValueError
        If ``kappa`` or ``gamma`` is not a number in ``[0, 1]``, ``lam`` is not a nonnegative
        finite number, or ``mu`` has a nonfinite entry. Strings, bools and NaN are rejected.

    Notes
    -----
    Heuristic (a modelling choice, paper Definition 3.3, the canonical closure; not a theorem).
    The canonical closure encodes:
    - κγ: baseline support from care × coherence
    - λμ: cost imposed by contradiction

    When b(x) > 0: local viability supports presence
    When b(x) < 0: local environment hostile to presence
    """
    kappa = check_unit_interval_scalar("kappa", kappa)
    gamma = check_unit_interval_scalar("gamma", gamma)
    lam = check_nonnegative_scalar("lam", lam)
    mu = check_finite_array("mu", mu)
    return kappa * gamma - lam * mu


def creative_drive(
    kappa: float,
    gamma: float,
    mu: np.ndarray,
) -> np.ndarray:
    """
    Compute creative drive field.

    a(x) = κγμ(x)

    Parameters
    ----------
    kappa : float
        Care intensity.
    gamma : float
        Coherence intensity.
    mu : ndarray
        Contradiction field.

    Returns
    -------
    a : ndarray
        Creative drive (same shape as mu).

    Raises
    ------
    ValueError
        If ``kappa`` or ``gamma`` is not a number in ``[0, 1]`` or ``mu`` has a nonfinite
        entry. Strings, bools and NaN are rejected.

    Notes
    -----
    Heuristic (a modelling choice; the interpretation below is not a theorem).
    The gradient term a|∇Φ| contributes to presence
    where all three fields jointly support activity.
    Creative drive requires contradiction to be present
    (μ > 0) — creativity emerges from engaging with
    contradictions, not avoiding them.
    """
    kappa = check_unit_interval_scalar("kappa", kappa)
    gamma = check_unit_interval_scalar("gamma", gamma)
    mu = check_finite_array("mu", mu)
    return kappa * gamma * mu


def gaussian_bump_2d(
    X: np.ndarray,
    Y: np.ndarray,
    x0: float,
    y0: float,
    sigma: float,
    amplitude: float = 1.0,
) -> np.ndarray:
    """
    Create a 2D Gaussian bump field.

    f(x,y) = amplitude × exp(-((x-x₀)² + (y-y₀)²) / (2σ²))

    Parameters
    ----------
    X, Y : ndarray
        Meshgrid arrays.
    x0, y0 : float
        Center of the bump.
    sigma : float
        Width (standard deviation).
    amplitude : float, default=1.0
        Peak value.

    Returns
    -------
    field : ndarray
        Gaussian bump (same shape as X, Y).

    Raises
    ------
    ValueError
        If ``sigma`` is not a positive finite number, ``x0``, ``y0`` or ``amplitude`` is not a
        finite number, or ``X`` / ``Y`` has a nonfinite entry.

    Example
    -------
    >>> X, Y = np.meshgrid(np.linspace(0, 1, 50), np.linspace(0, 1, 50))
    >>> mu = gaussian_bump_2d(X, Y, 0.5, 0.5, 0.1)  # Contradiction at center
    """
    X = check_finite_array("X", X)
    Y = check_finite_array("Y", Y)
    x0 = check_finite_scalar("x0", x0)
    y0 = check_finite_scalar("y0", y0)
    sigma = check_positive_scalar("sigma", sigma)
    amplitude = check_finite_scalar("amplitude", amplitude)
    r2 = (X - x0) ** 2 + (Y - y0) ** 2
    return amplitude * np.exp(-r2 / (2 * sigma**2))


def gaussian_bump_1d(
    x: np.ndarray,
    center: float,
    sigma: float,
    amplitude: float = 1.0,
) -> np.ndarray:
    """
    Create a 1D Gaussian bump field.

    f(x) = amplitude * exp(-((x - center)^2) / (2 * sigma^2))

    Parameters
    ----------
    x : ndarray
        1D grid points.
    center : float
        Center of the bump.
    sigma : float
        Width (standard deviation).
    amplitude : float, default=1.0
        Peak value.

    Returns
    -------
    field : ndarray
        Gaussian bump (same shape as x).

    Raises
    ------
    ValueError
        If ``sigma`` is not a positive finite number, ``center`` or ``amplitude`` is not a
        finite number, or ``x`` has a nonfinite entry.
    """
    x = check_finite_array("x", x)
    center = check_finite_scalar("center", center)
    sigma = check_positive_scalar("sigma", sigma)
    amplitude = check_finite_scalar("amplitude", amplitude)
    return amplitude * np.exp(-((x - center) ** 2) / (2 * sigma**2))
