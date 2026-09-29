"""Operators and spectra: signs, boundary rows, exact discrete eigenvalues, anisotropy,
smallest grids, and scale-aware errors near lambda_1 = 0."""

import numpy as np
import pytest

from cd import (
    laplacian_1d_dirichlet,
    laplacian_2d_dirichlet,
    principal_eigenvalue_1d,
    principal_eigenvalue_2d,
    principal_eigenvalue_2d_spatial,
)
from cd.eigenvalues import principal_eigenpair_1d, principal_eigenvalue_1d_spatial


def discrete_lambda1_1d(N, L, q):
    """Exact principal eigenvalue of the (N x N) centered-difference Dirichlet matrix minus q."""
    h = L / (N + 1)
    return 4.0 / h**2 * np.sin(np.pi * h / (2.0 * L)) ** 2 - q


class TestOperatorSign:
    def test_1d_operator_is_minus_second_derivative(self):
        N, L = 200, 1.0
        A, h = laplacian_1d_dirichlet(N, L)
        x = np.linspace(0.0, L, N + 2)
        u = np.sin(np.pi * x / L)
        Au = A @ u[1:-1]
        expected = (np.pi / L) ** 2 * u[1:-1]
        assert np.max(np.abs(Au - expected)) < 1e-3
        assert np.all(Au > 0)

    def test_1d_boundary_rows_use_zero_dirichlet_values(self):
        """The first and last rows see only one interior neighbour; the boundary value is 0."""
        A, h = laplacian_1d_dirichlet(4, 1.0)
        A = A.toarray()
        assert A[0, 0] == pytest.approx(2.0 / h**2)
        assert A[0, 1] == pytest.approx(-1.0 / h**2)
        assert A[0, 2] == 0.0
        assert np.allclose(A, A.T)

    def test_smallest_1d_matrix(self):
        A, h = laplacian_1d_dirichlet(1, 1.0)
        assert A.shape == (1, 1)
        assert h == pytest.approx(0.5)
        assert A.toarray()[0, 0] == pytest.approx(8.0)

    def test_smallest_2d_matrix(self):
        A, hx, hy = laplacian_2d_dirichlet(1, 1, 1.0, 2.0)
        assert A.shape == (1, 1)
        assert A.toarray()[0, 0] == pytest.approx(2.0 / hx**2 + 2.0 / hy**2)

    @pytest.mark.parametrize("N", [0, -1, 3.0])
    def test_operator_rejects_invalid_size(self, N):
        with pytest.raises(ValueError):
            laplacian_1d_dirichlet(N, 1.0)

    def test_operator_rejects_invalid_length(self):
        with pytest.raises(ValueError):
            laplacian_1d_dirichlet(5, 0.0)
        with pytest.raises(ValueError):
            laplacian_2d_dirichlet(3, 3, 1.0, -1.0)


class TestExactDiscreteEigenvalues:
    @pytest.mark.parametrize("N", [1, 2, 7, 64, 600])
    def test_1d_matches_closed_form_discrete_eigenvalue(self, N):
        L, q = 1.3, 5.0
        lam = principal_eigenvalue_1d(N, L, q)
        assert lam == pytest.approx(
            discrete_lambda1_1d(N, L, q), abs=1e-7 * max(1.0, 4.0 * (N + 1) ** 2 / L**2)
        )

    def test_1d_eigenvector_is_positive_and_sine_shaped(self):
        N, L, q = 50, 1.0, 3.0
        lam, phi = principal_eigenpair_1d(N, L, q)
        assert phi[0] == 0.0 and phi[-1] == 0.0
        assert np.all(phi[1:-1] > 0)
        assert phi.max() == pytest.approx(1.0)
        x = np.linspace(0.0, L, N + 2)
        sine = np.sin(np.pi * x / L)
        assert np.max(np.abs(phi - sine / sine.max())) < 1e-10
        A, _ = laplacian_1d_dirichlet(N, L)
        np.testing.assert_allclose(A @ phi[1:-1] - q * phi[1:-1], lam * phi[1:-1], atol=1e-9)

    def test_2d_anisotropic_matches_sum_of_discrete_formulas(self):
        Nx, Ny, Lx, Ly, q = 12, 30, 1.0, 2.0, 4.0
        hx, hy = Lx / (Nx + 1), Ly / (Ny + 1)
        expected = (
            4 / hx**2 * np.sin(np.pi * hx / (2 * Lx)) ** 2
            + 4 / hy**2 * np.sin(np.pi * hy / (2 * Ly)) ** 2
            - q
        )
        lam = principal_eigenvalue_2d(Nx, Ny, Lx, Ly, q)
        assert lam == pytest.approx(expected, abs=1e-6)
        field = q * np.ones((Ny + 2, Nx + 2))
        assert principal_eigenvalue_2d_spatial(Nx, Ny, Lx, Ly, field) == pytest.approx(
            expected, abs=1e-6
        )

    def test_2d_smallest_grid(self):
        lam = principal_eigenvalue_2d(1, 1, 1.0, 1.0, 0.0)
        assert lam == pytest.approx(16.0)

    def test_continuum_limit_is_second_order(self):
        L, q = 1.0, 2.0
        errors = []
        for N in (50, 100, 200):
            errors.append(abs(principal_eigenvalue_1d(N, L, q) - ((np.pi / L) ** 2 - q)))
        assert 3.5 < errors[0] / errors[1] < 4.5
        assert 3.5 < errors[1] / errors[2] < 4.5


class TestNearThreshold:
    def test_absolute_error_near_zero_eigenvalue(self):
        """At q equal to the discrete threshold the exact discrete eigenvalue is 0; use an
        absolute tolerance rather than dividing by it."""
        N, L = 300, 1.0
        q_star = discrete_lambda1_1d(N, L, 0.0)
        lam = principal_eigenvalue_1d(N, L, q_star)
        assert abs(lam) < 1e-6
        assert principal_eigenvalue_1d(N, L, q_star - 1.0) > 0.5
        assert principal_eigenvalue_1d(N, L, q_star + 1.0) < -0.5

    def test_spatial_field_shape_validated(self):
        with pytest.raises(ValueError):
            principal_eigenvalue_1d_spatial(10, 1.0, np.zeros(10))
        with pytest.raises(ValueError):
            principal_eigenvalue_2d_spatial(3, 4, 1.0, 1.0, np.zeros((4, 3)))

    def test_spatial_potential_lowers_eigenvalue_where_added(self):
        N, L = 100, 1.0
        x = np.linspace(0.0, L, N + 2)
        base = 2.0 * np.ones(N + 2)
        bump = base + 5.0 * np.exp(-(((x - 0.5) / 0.1) ** 2))
        assert principal_eigenvalue_1d_spatial(N, L, bump) < principal_eigenvalue_1d_spatial(
            N, L, base
        )
