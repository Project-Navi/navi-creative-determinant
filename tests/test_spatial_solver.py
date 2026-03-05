"""Tests for spatially-varying coefficient support in solver and residual."""

import numpy as np

from cd import residual_1d, solve_1d_picard
from cd.eigenvalues import viability_threshold_1d


class TestSpatialSolver1d:
    def test_array_coefficients_matches_scalar(self):
        """Array coefficients that are constant should match scalar result."""
        L, N = 1.0, 400
        b = 0.8
        beta_star = viability_threshold_1d(L, b)
        beta_above = 1.2 * beta_star

        # Scalar
        _, Phi_s, info_s = solve_1d_picard(L, N, a=0.0, beta_b=beta_above * b, c=10.0)

        # Array (interior-only length N)
        a_arr = np.zeros(N)
        bb_arr = np.full(N, beta_above * b)
        c_arr = np.full(N, 10.0)
        _, Phi_a, info_a = solve_1d_picard(L, N, a=a_arr, beta_b=bb_arr, c=c_arr)

        assert abs(info_s["maxPhi"] - info_a["maxPhi"]) < 1e-6

    def test_spatially_varying_solves(self):
        """Solver should converge with spatially-varying coefficients."""
        L, N = 1.0, 400
        x_int = np.linspace(0, L, N + 2)[1:-1]
        # Gaussian viability bump
        bb = 15.0 * np.exp(-((x_int - 0.5) / 0.2) ** 2)
        _, _, info = solve_1d_picard(L, N, a=np.zeros(N), beta_b=bb, c=np.full(N, 10.0))
        assert info["converged"]


class TestSpatialResidual1d:
    def test_array_residual_matches_scalar(self):
        """Residual with constant arrays should match scalar version."""
        L, N = 1.0, 800
        b = 0.8
        beta_star = viability_threshold_1d(L, b)
        beta_b_val = 1.2 * beta_star * b

        x, Phi, _ = solve_1d_picard(L, N, a=0.0, beta_b=beta_b_val, c=10.0)

        res_s = residual_1d(x, Phi, a=0.0, beta_b=beta_b_val, c=10.0, p=2.0)
        res_a = residual_1d(x, Phi, a=np.zeros(N), beta_b=np.full(N, beta_b_val),
                           c=np.full(N, 10.0), p=2.0)

        assert np.allclose(res_s, res_a, atol=1e-12)
