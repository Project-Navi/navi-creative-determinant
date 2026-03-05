# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nelson Spence
"""Tests for eigenvalue computations including spatially-varying fields."""

import numpy as np

from cd.eigenvalues import (
    principal_eigenvalue_1d,
    principal_eigenvalue_1d_spatial,
    principal_eigenvalue_2d_spatial,
)


class TestSpatialEigenvalue1d:
    def test_constant_field_matches_scalar(self):
        """Spatial eigenvalue with constant field should match scalar version."""
        N, L = 200, 1.0
        beta_b = 8.0
        beta_b_field = beta_b * np.ones(N + 2)
        lam_scalar = principal_eigenvalue_1d(N, L, beta_b)
        lam_spatial = principal_eigenvalue_1d_spatial(N, L, beta_b_field)
        assert abs(lam_scalar - lam_spatial) < 0.01

    def test_higher_potential_lowers_eigenvalue(self):
        """Higher beta*b field should lower the eigenvalue."""
        N, L = 200, 1.0
        low = 5.0 * np.ones(N + 2)
        high = 15.0 * np.ones(N + 2)
        lam_low = principal_eigenvalue_1d_spatial(N, L, low)
        lam_high = principal_eigenvalue_1d_spatial(N, L, high)
        assert lam_high < lam_low


class TestSpatialEigenvalue2d:
    def test_constant_field_matches_analytic(self):
        """Spatial 2D eigenvalue with constant field should match analytic formula."""
        Nx, Ny = 30, 30
        Lx, Ly = 1.0, 1.0
        beta_b = 10.0
        beta_b_field = beta_b * np.ones((Ny + 2, Nx + 2))
        lam_spatial = principal_eigenvalue_2d_spatial(Nx, Ny, Lx, Ly, beta_b_field)
        lam_analytic = np.pi**2 * (1 / Lx**2 + 1 / Ly**2) - beta_b
        assert abs(lam_spatial - lam_analytic) < 0.5
