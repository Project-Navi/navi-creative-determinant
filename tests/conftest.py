"""Shared fixtures for the package tests.

The factory fixtures return plain functions, so a test builds the small graph or the exact
discrete eigenvalue reference it needs with explicit arguments; the converged report is one
real solver run shared by every test that validates the report contract.
"""

import numpy as np
import pytest

from cd import solve_1d_picard
from cd.graph import SemioticGraph


def _triangle_with_b(b_value: float) -> SemioticGraph:
    """The Lean triangle (K_3, unit weights including the diagonal, boundary {0}, a = c = 1,
    p = 2) with the constant potential ``b`` replaced by ``b_value``."""
    return SemioticGraph(
        w=np.ones((3, 3)),
        boundary=np.array([True, False, False]),
        a=np.ones(3),
        b=np.full(3, b_value),
        c=np.ones(3),
        p=2.0,
    )


def _graph_with_self_weight(diagonal: float, a: float = 0.0) -> SemioticGraph:
    """K_3 with unit off-diagonal weights and the given self weight on every vertex,
    boundary {0}, constant drive ``a``, b = 0, c = 1, p = 2."""
    w = np.ones((3, 3))
    np.fill_diagonal(w, diagonal)
    return SemioticGraph(
        w=w,
        boundary=np.array([True, False, False]),
        a=np.full(3, a),
        b=np.zeros(3),
        c=np.ones(3),
        p=2.0,
    )


def _discrete_lambda1_1d(N: int, L: float, q: float) -> float:
    """Exact principal eigenvalue of the (N x N) centered-difference Dirichlet matrix minus q:
    ``(4/h²) sin²(πh/(2L)) - q`` with ``h = L/(N+1)``."""
    h = L / (N + 1)
    return 4.0 / h**2 * np.sin(np.pi * h / (2.0 * L)) ** 2 - q


@pytest.fixture
def triangle_with_b():
    """``triangle_with_b(b)``: the Lean triangle with potential ``b``."""
    return _triangle_with_b


@pytest.fixture
def graph_with_self_weight():
    """``graph_with_self_weight(diagonal, a=0.0)``: K_3 with self weights."""
    return _graph_with_self_weight


@pytest.fixture
def discrete_lambda1_1d():
    """``discrete_lambda1_1d(N, L, q)``: the closed-form discrete principal eigenvalue."""
    return _discrete_lambda1_1d


@pytest.fixture(scope="session")
def converged_1d_report():
    """Report of an ordinary converged 1D run (positive branch, iters > 0)."""
    _, _, info = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0, tol=1e-10)
    assert info["converged"] and info["iters"] > 0
    return info
