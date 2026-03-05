"""Tests for 2D solver extensions and residual."""

import numpy as np
import pytest

from cd import solve_2d_picard
from cd.analysis import residual_2d


class TestSolver2dArrayCoeffs:
    def test_array_a_and_c(self):
        """Solver should accept array-valued a and c."""
        Nx, Ny = 30, 30
        Lx, Ly = 1.0, 1.0
        a_field = np.zeros((Ny, Nx))
        c_field = 10.0 * np.ones((Ny, Nx))
        X, Y, Phi, info = solve_2d_picard(
            Lx, Ly, Nx, Ny, a=a_field, beta_b=20.0, c=c_field, max_iter=2000
        )
        assert info["converged"]


class TestResidual2d:
    def test_residual_small_for_converged(self):
        """Residual should be small for a converged 2D solution."""
        Nx, Ny = 40, 40
        Lx, Ly = 1.0, 1.0
        hx = Lx / (Nx + 1)
        hy = Ly / (Ny + 1)
        X, Y, Phi, info = solve_2d_picard(Lx, Ly, Nx, Ny, a=0.0, beta_b=25.0, c=10.0)

        a_full = np.zeros((Ny + 2, Nx + 2))
        bb_full = 25.0 * np.ones((Ny + 2, Nx + 2))
        c_full = 10.0 * np.ones((Ny + 2, Nx + 2))

        res = residual_2d(Phi, a_full, bb_full, c_full, p=2.0, hx=hx, hy=hy)
        assert np.linalg.norm(res, np.inf) < 0.1
