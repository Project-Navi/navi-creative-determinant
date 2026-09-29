"""Independent numerical validation: manufactured residual, collocation (solve_bvp)
comparison, and mesh refinement with the exact discrete residual."""

import numpy as np
import pytest
from scipy.integrate import solve_bvp

from cd import residual_1d, solve_1d_picard


class TestManufacturedResidual:
    def test_residual_stencil_matches_analytic_residual_to_second_order(self):
        """For Phi = sin(pi x / L) the continuum residual is
        (pi/L)^2 sin - (a |pi/L cos| + q sin - c sin^p). The discrete residual must agree
        to O(h^2), with the error ratio ~4 between grids."""
        L, a, q, c, p = 1.0, 0.7, 15.0, 10.0, 2.0
        errs = []
        for N in (100, 200, 400):
            x = np.linspace(0.0, L, N + 2)
            Phi = np.sin(np.pi * x / L)
            analytic = (np.pi / L) ** 2 * Phi - (
                a * np.abs(np.pi / L * np.cos(np.pi * x / L)) + q * Phi - c * Phi**p
            )
            res = residual_1d(x, Phi, a, q, c, p)
            errs.append(np.max(np.abs(res - analytic[1:-1])))
        assert errs[0] < 1e-2
        assert 3.5 < errs[0] / errs[1] < 4.5
        assert 3.5 < errs[1] / errs[2] < 4.5


def _collocation(L, a, q, c, p, amplitude=0.6, n_mesh=400, tol=1e-9):
    """Independent collocation solve (scipy.integrate.solve_bvp) from a sine start."""
    x = np.linspace(0.0, L, n_mesh)

    def fun(x, y):
        Phi, dPhi = y
        return np.vstack((dPhi, -(a * np.abs(dPhi) + q * Phi - c * np.maximum(Phi, 0.0) ** p)))

    def bc(ya, yb):
        return np.array([ya[0], yb[0]])

    y0 = np.vstack(
        (amplitude * np.sin(np.pi * x / L), amplitude * (np.pi / L) * np.cos(np.pi * x / L))
    )
    return solve_bvp(fun, bc, x, y0, tol=tol, max_nodes=100000)


class TestCollocationCrossCheck:
    @pytest.mark.parametrize("a", [0.0, 0.5])
    def test_fd_solution_agrees_with_independent_collocation(self, a):
        L, q, c, p, N = 1.0, 15.0, 10.0, 2.0, 800
        sol = _collocation(L, a, q, c, p)
        assert sol.status == 0, sol.message
        assert np.max(sol.rms_residuals) < 1e-8
        assert sol.y[0].max() > 0.1, "collocation must also find the positive branch"
        x, u, info = solve_1d_picard(L, N, a, q, c, p=p)
        assert info["converged"]
        diff = np.max(np.abs(u - sol.sol(x)[0]))
        assert diff < 1e-5, f"a={a}: max |FD - collocation| = {diff:.2e}"

    def test_collocation_small_start_collapses_to_zero(self):
        """From a small sine start (amplitude 0.3) the collocation Newton iteration converges to
        the zero solution with status 0. A "converged" collocation run is therefore not by
        itself evidence about the positive branch; the start must be recorded."""
        sol = _collocation(1.0, 0.0, 15.0, 10.0, 2.0, amplitude=0.3)
        assert sol.status == 0
        assert np.max(np.abs(sol.y[0])) < 1e-10

    def test_collocation_zero_start_returns_zero_not_nonexistence(self):
        """Starting the collocation at zero returns the zero solution; that says nothing about
        the positive branch, which ``test_fd_solution_agrees_with_independent_collocation``
        finds from the amplitude-0.6 sine start (the previous test shows that a small start
        collapses to zero as well)."""
        L, q, c, p = 1.0, 15.0, 10.0, 2.0
        x = np.linspace(0.0, L, 200)

        def fun(x, y):
            return np.vstack((y[1], -(q * y[0] - c * np.maximum(y[0], 0.0) ** p)))

        def bc(ya, yb):
            return np.array([ya[0], yb[0]])

        sol = solve_bvp(fun, bc, x, np.zeros((2, x.size)), tol=1e-9)
        assert sol.status == 0
        assert np.max(np.abs(sol.y[0])) < 1e-12


class TestMeshRefinement:
    def test_maximum_converges_at_second_order(self):
        L, q, c, p = 1.0, 15.0, 10.0, 2.0
        maxes = []
        for N in (50, 100, 200, 400):
            _, u, info = solve_1d_picard(L, N, 0.0, q, c, p=p)
            assert info["converged"]
            maxes.append(u.max())
        d1 = abs(maxes[1] - maxes[0])
        d2 = abs(maxes[2] - maxes[1])
        d3 = abs(maxes[3] - maxes[2])
        assert 3.0 < d1 / d2 < 5.0
        assert 3.0 < d2 / d3 < 5.0

    def test_discrete_residual_is_algebraic_not_discretization_error(self):
        """The converged discrete residual is at the solver tolerance on every grid; it does
        not measure the distance to the continuum solution (that is the refinement study)."""
        L, q, c, p = 1.0, 15.0, 10.0, 2.0
        for N in (50, 400):
            x, u, info = solve_1d_picard(L, N, 0.0, q, c, p=p)
            assert info["converged"]
            assert np.max(np.abs(residual_1d(x, u, 0.0, q, c, p))) < 1e-7
