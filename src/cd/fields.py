"""
Field constructors for the Creative Determinant framework.

Provides utilities for constructing the characteristic fields:
- Care (κ), Coherence (γ), Contradiction (μ)
- Viability potential b(x) = κγ - λμ (canonical closure)
- Creative drive a(x) = κγμ
"""

import numpy as np


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
        Contradiction field ∈ [0, 1].
    lam : float
        Contradiction cost parameter λ > 0.

    Returns
    -------
    b : ndarray
        Viability potential (same shape as mu).

    Notes
    -----
    The canonical closure encodes:
    - κγ: baseline support from care × coherence
    - λμ: cost imposed by contradiction

    When b(x) > 0: local viability supports presence
    When b(x) < 0: local environment hostile to presence
    """
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

    Notes
    -----
    The gradient term a|∇Φ| contributes to presence
    where all three fields jointly support activity.
    Creative drive requires contradiction to be present
    (μ > 0) — creativity emerges from engaging with
    contradictions, not avoiding them.
    """
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

    Example
    -------
    >>> X, Y = np.meshgrid(np.linspace(0, 1, 50), np.linspace(0, 1, 50))
    >>> mu = gaussian_bump_2d(X, Y, 0.5, 0.5, 0.1)  # Contradiction at center
    """
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
    """
    return amplitude * np.exp(-((x - center) ** 2) / (2 * sigma**2))


def constant_field(shape: tuple[int, ...], value: float) -> np.ndarray:
    """
    Create a constant field.

    Parameters
    ----------
    shape : tuple
        Output shape.
    value : float
        Constant value.

    Returns
    -------
    field : ndarray
        Constant array.
    """
    return np.full(shape, value)


def linear_gradient_1d(N: int, v0: float, v1: float) -> np.ndarray:
    """
    Create a linear gradient in 1D (interior points only).

    Parameters
    ----------
    N : int
        Number of interior points.
    v0, v1 : float
        Values at left and right boundaries.

    Returns
    -------
    field : ndarray
        Linear interpolation, shape (N,).
    """
    return np.linspace(v0, v1, N + 2)[1:-1]


def step_function_1d(N: int, x_step: float, L: float, v_left: float, v_right: float) -> np.ndarray:
    """
    Create a step function in 1D (interior points only).

    Parameters
    ----------
    N : int
        Number of interior points.
    x_step : float
        Location of step.
    L : float
        Domain length.
    v_left : float
        Value for x < x_step.
    v_right : float
        Value for x >= x_step.

    Returns
    -------
    field : ndarray
        Step function, shape (N,).
    """
    x = np.linspace(0, L, N + 2)[1:-1]
    return np.where(x < x_step, v_left, v_right)
