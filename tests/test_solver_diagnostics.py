"""Meaning of numerical success (MATH-REPAIR M05).

Convergence means: a finite field satisfying the declared discrete equation to a documented
residual tolerance, with the boundary condition met. Update size alone is not convergence.
"""

import numpy as np
import pytest

from cd import residual_1d, residual_2d, solve_1d_picard, solve_2d_picard
from cd.analysis import check_convergence, classify_branch, solution_type


def _residual_1d_independent(x, u, a, q, c, p):
    """Independent evaluation of the discrete equation (not the solver's own flag)."""
    h = float(x[1] - x[0])
    v = u[1:-1]
    lap = (-u[2:] + 2 * v - u[:-2]) / h**2
    grad = np.abs((u[2:] - u[:-2]) / (2 * h))
    return lap - (a * grad + q * v - c * np.maximum(v, 0.0) ** p)


class TestTinyDampingIsNotConvergence:
    def test_1d_tiny_damping_does_not_report_convergence(self):
        x, u, info = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0, max_iter=8, damping=1e-14)
        res = float(np.max(np.abs(_residual_1d_independent(x, u, 0.0, 15.0, 10.0, 2.0))))
        assert np.all(np.isfinite(u))
        assert res > 1e-3, "the initial sine is far from solving the equation"
        assert not info["converged"]
        assert info["termination"] == "max_iter"
        assert info["residual_inf"] == pytest.approx(res, rel=1e-12)
        assert info["inf_err"] < 1e-12, "update size is tiny; that is exactly why it is not enough"

    def test_2d_tiny_damping_does_not_report_convergence(self):
        X, Y, u, info = solve_2d_picard(1.0, 1.0, 7, 9, 0.0, 30.0, 10.0, max_iter=8, damping=1e-14)
        assert np.all(np.isfinite(u))
        assert not info["converged"]
        assert info["termination"] == "max_iter"
        assert info["residual_inf"] > 1e-3


class TestInputValidation:
    @pytest.mark.parametrize("damping", [0.0, -0.5, 1.5, np.nan])
    def test_rejects_invalid_damping(self, damping):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 7, 0.0, 15.0, 10.0, damping=damping, max_iter=1)

    @pytest.mark.parametrize("max_iter", [0, -1, 2.5])
    def test_rejects_invalid_budget(self, max_iter):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 7, 0.0, 15.0, 10.0, max_iter=max_iter)

    @pytest.mark.parametrize("N", [0, -3, 2.0, True])
    def test_rejects_invalid_grid_size(self, N):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, N, 0.0, 15.0, 10.0)

    @pytest.mark.parametrize("L", [0.0, -1.0, np.inf, np.nan])
    def test_rejects_invalid_length(self, L):
        with pytest.raises(ValueError):
            solve_1d_picard(L, 7, 0.0, 15.0, 10.0)

    @pytest.mark.parametrize(
        "kw",
        [{"a": np.nan}, {"beta_b": np.inf}, {"c": np.nan}, {"p": np.nan}, {"p": 1.0}, {"c": 0.0}],
    )
    def test_rejects_nonfinite_or_invalid_coefficients(self, kw):
        args = dict(a=0.0, beta_b=15.0, c=10.0, p=2.0)
        args.update(kw)
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 7, **args)

    def test_rejects_wrong_array_shape(self):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 7, a=np.zeros(5), beta_b=15.0, c=10.0)
        with pytest.raises(ValueError):
            solve_2d_picard(1.0, 1.0, 4, 5, a=np.zeros((5, 5)), beta_b=20.0, c=10.0)
        with pytest.raises(ValueError):
            solve_2d_picard(1.0, 1.0, 4, 5, a=0.0, beta_b=20.0, c=10.0, b_field=np.ones((4, 5)))

    def test_rejects_invalid_tolerances(self):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 7, 0.0, 15.0, 10.0, tol=0.0)
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 7, 0.0, 15.0, 10.0, residual_atol=-1.0)
        with pytest.raises(ValueError):
            solve_2d_picard(1.0, 1.0, 4, 5, 0.0, 20.0, 10.0, residual_rtol=np.nan)


class TestTerminationReasons:
    def test_nonfinite_iterate_terminates_and_is_not_accepted(self):
        x, u, info = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0, initial_amplitude=1e200, damping=1.0)
        assert not info["converged"]
        assert info["termination"] == "nonfinite"
        assert classify_branch(u, info) == "invalid"
        assert solution_type(info) == "invalid"
        assert check_convergence(info)[0] is False

    def test_exhausted_budget_reports_actual_iteration_count(self):
        x, u, info = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0, max_iter=3)
        assert info["iters"] == 3
        assert not info["converged"]
        assert info["termination"] == "max_iter"
        assert classify_branch(u, info) == "unresolved"
        assert solution_type(info) == "unresolved"

    def test_converged_solve_has_small_independent_residual_and_zero_boundary(self):
        x, u, info = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0)
        assert info["converged"]
        assert info["termination"] == "converged"
        res = float(np.max(np.abs(_residual_1d_independent(x, u, 0.0, 15.0, 10.0, 2.0))))
        assert res <= info["residual_atol"] + info["residual_rtol"] * info["residual_scale"]
        assert u[0] == 0.0 and u[-1] == 0.0
        assert info["boundary_err"] == 0.0
        assert 0.1 < info["maxPhi"] < 1.5
        assert classify_branch(u, info) == "positive"

    def test_clipped_collapse_is_recorded_and_is_not_nonexistence_evidence(self):
        """A bad start (amplitude 3, undamped) is clipped to zero and the projected iteration
        then stays at the zero solution although lambda_1 < 0. The solver must say so."""
        x, u, info = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0, initial_amplitude=3.0, damping=1.0)
        assert info["clipped_iterations"] > 0
        assert info["converged"]
        assert classify_branch(u, info) == "zero"
        # The positive branch exists and is reached from the subsolution barrier.
        x2, u2, info2 = solve_1d_picard(1.0, 31, 0.0, 15.0, 10.0, initial_guess="subsolution")
        assert info2["converged"]
        assert classify_branch(u2, info2) == "positive"


class TestSmallestAndAnisotropicGrids:
    def test_single_interior_point_solves_scalar_equation(self):
        """N = 1, h = L/2: 8 u = 15 u - 10 u^2 has the positive root u = 0.7."""
        x, u, info = solve_1d_picard(1.0, 1, 0.0, 15.0, 10.0)
        assert info["converged"]
        assert u[1] == pytest.approx(0.7, abs=1e-8)
        assert len(x) == 3

    def test_2d_single_interior_point(self):
        """Nx = Ny = 1 on the unit square: (8 + 8) u = 30 u - 10 u^2 gives u = 1.4."""
        X, Y, u, info = solve_2d_picard(1.0, 1.0, 1, 1, 0.0, 30.0, 10.0)
        assert info["converged"]
        assert u[1, 1] == pytest.approx(1.4, abs=1e-8)

    def test_anisotropic_rectangle_converges_with_small_residual(self):
        Lx, Ly, Nx, Ny = 1.0, 2.0, 7, 9
        X, Y, u, info = solve_2d_picard(Lx, Ly, Nx, Ny, 0.0, 30.0, 10.0)
        assert info["converged"]
        assert u.shape == (Ny + 2, Nx + 2)
        hx, hy = Lx / (Nx + 1), Ly / (Ny + 1)
        full = np.ones_like(u)
        res = residual_2d(u, 0.0 * full, 30.0 * full, 10.0 * full, p=2.0, hx=hx, hy=hy)
        assert np.max(np.abs(res)) < 1e-6
        assert info["maxPhi"] > 0.5


class TestAnalysisFailClosed:
    def test_nan_update_is_not_accepted(self):
        ok, msg = check_convergence({"converged": True, "iters": 1, "inf_err": float("nan")})
        assert ok is False

    def test_missing_residual_is_not_accepted(self):
        ok, msg = check_convergence({"converged": True, "iters": 5, "inf_err": 1e-12})
        assert ok is False

    def test_nearly_converged_is_not_accepted(self):
        info = {
            "converged": False,
            "iters": 8000,
            "inf_err": 5e-8,
            "residual_inf": 1e-3,
            "termination": "max_iter",
        }
        ok, msg = check_convergence(info)
        assert ok is False
        assert "max_iter" in msg

    def test_nan_max_is_not_classified(self):
        assert solution_type({"maxPhi": float("nan")}) == "invalid"

    def test_unconverged_is_unresolved_not_trivial(self):
        assert solution_type({"maxPhi": 1e-9, "converged": False}) == "unresolved"

    def test_converged_labels_kept_for_compatibility(self):
        assert solution_type({"maxPhi": 1e-9, "converged": True}) == "trivial"
        assert solution_type({"maxPhi": 0.5, "converged": True}) == "nontrivial"


class TestResidualValidation:
    def test_residual_1d_rejects_nonuniform_grid(self):
        x = np.array([0.0, 0.1, 0.5, 1.0])
        with pytest.raises(ValueError):
            residual_1d(x, np.zeros(4), 0.0, 1.0, 1.0, 2.0)

    def test_residual_1d_rejects_shape_mismatch(self):
        with pytest.raises(ValueError):
            residual_1d(np.linspace(0, 1, 5), np.zeros(4), 0.0, 1.0, 1.0, 2.0)
