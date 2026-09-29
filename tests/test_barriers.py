"""Ordered barriers and monotone iteration for the finite-difference lane with a = 0.

Discrete analogue of the paper's barrier argument for Theorem 3.16: eps*phi_1 is a
subsolution when lambda_1 < 0 and c eps^{p-1} <= -lambda_1; the plateau M is a supersolution
when c M^{p-1} >= q_+. With the shift K >= c p M^{p-1} - q the shifted Picard map is monotone on
[0, M], so the iterates from below are nondecreasing and the iterates from above nonincreasing.
Monotonicity is a checked property of these runs; a = 0 is required for the argument.
"""

import numpy as np
import pytest

from cd import residual_1d, solve_1d_picard
from cd.solvers import barriers_1d


class TestBarrierConstruction:
    def test_barriers_are_sub_and_supersolutions(self):
        L, N, q, c, p = 1.0, 63, 15.0, 10.0, 2.0
        bar = barriers_1d(N, L, q, c, p)
        x = np.linspace(0.0, L, N + 2)
        assert bar["lam1"] < 0
        assert 0 < bar["eps"] <= 1
        assert bar["M"] >= 1
        assert bar["K"] > 0
        sub, sup = bar["sub"], bar["sup"]
        assert sub[0] == 0 == sub[-1] and sup[0] == 0 == sup[-1]
        assert np.all(sub <= sup)
        assert np.all(sub[1:-1] > 0)
        # residual = -Phi'' - (q Phi - c Phi^p): <= 0 for a subsolution, >= 0 for a supersolution
        assert np.all(residual_1d(x, sub, 0.0, q, c, p) <= 1e-12)
        assert np.all(residual_1d(x, sup, 0.0, q, c, p) >= -1e-12)

    def test_barriers_require_negative_eigenvalue(self):
        with pytest.raises(ValueError):
            barriers_1d(31, 1.0, 5.0, 10.0, 2.0)


class TestMonotoneIteration:
    def test_iterates_from_below_are_nondecreasing_and_converge(self):
        L, N, q, c, p = 1.0, 63, 15.0, 10.0, 2.0
        x, u, info = solve_1d_picard(
            L, N, 0.0, q, c, p=p, initial_guess="subsolution", shift="auto", damping=1.0
        )
        assert info["converged"]
        assert info["monotone"] == "nondecreasing"
        assert info["shift"] > 0
        assert np.max(np.abs(residual_1d(x, u, 0.0, q, c, p))) < 1e-7
        assert np.all(u[1:-1] > 0)

    def test_iterates_from_above_are_nonincreasing_and_converge(self):
        L, N, q, c, p = 1.0, 63, 15.0, 10.0, 2.0
        x, u, info = solve_1d_picard(
            L, N, 0.0, q, c, p=p, initial_guess="plateau", shift="auto", damping=1.0
        )
        assert info["converged"]
        assert info["monotone"] == "nonincreasing"

    def test_minimal_and_maximal_solutions_coincide_for_logistic_case(self):
        """Observation (not a theorem asserted by the library): for a = 0, p = 2 the least
        fixed point above eps*phi_1 and the greatest below M agree to solver tolerance."""
        L, N, q, c, p = 1.0, 63, 15.0, 10.0, 2.0
        _, lo, _ = solve_1d_picard(
            L, N, 0.0, q, c, p=p, initial_guess="subsolution", shift="auto", damping=1.0
        )
        _, hi, _ = solve_1d_picard(
            L, N, 0.0, q, c, p=p, initial_guess="plateau", shift="auto", damping=1.0
        )
        assert np.max(np.abs(hi - lo)) < 1e-7

    def test_explicit_initial_guess_array_accepted(self):
        L, N = 1.0, 31
        x = np.linspace(0.0, L, N + 2)
        guess = 0.3 * np.sin(np.pi * x / L)
        _, u, info = solve_1d_picard(L, N, 0.0, 15.0, 10.0, initial_guess=guess)
        assert info["converged"]
        with pytest.raises(ValueError):
            solve_1d_picard(L, N, 0.0, 15.0, 10.0, initial_guess=np.zeros(5))
        with pytest.raises(ValueError):
            solve_1d_picard(L, N, 0.0, 15.0, 10.0, initial_guess="nonsense")

    def test_subsolution_start_requires_negative_eigenvalue(self):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 31, 0.0, 5.0, 10.0, initial_guess="subsolution")


class TestExactDiscreteThresholdForZeroDrive:
    """For a = 0 the discrete problem has a positive solution iff lambda_1(A - q) < 0
    (necessity by testing against the positive eigenvector; sufficiency by the barriers)."""

    @pytest.mark.parametrize("ratio", [0.6, 0.8, 0.95, 1.05, 1.2, 1.5])
    def test_branch_agrees_with_eigenvalue_sign_away_from_threshold(
        self, ratio, discrete_lambda1_1d
    ):
        from cd.analysis import classify_branch
        from cd.eigenvalues import principal_eigenvalue_1d

        L, N, c, p = 1.0, 200, 10.0, 2.0
        q_star = discrete_lambda1_1d(N, L, 0.0)
        q = ratio * q_star
        lam = principal_eigenvalue_1d(N, L, q)
        x, u, info = solve_1d_picard(L, N, 0.0, q, c, p=p)
        assert info["converged"]
        branch = classify_branch(u, info)
        if lam < 0:
            assert branch == "positive"
        else:
            assert branch == "zero"

    def test_near_threshold_with_small_budget_is_unresolved_not_a_label(self, discrete_lambda1_1d):
        from cd.analysis import classify_branch

        L, N, c, p = 1.0, 200, 10.0, 2.0
        q_star = discrete_lambda1_1d(N, L, 0.0)
        x, u, info = solve_1d_picard(L, N, 0.0, 1.001 * q_star, c, p=p, max_iter=5)
        assert not info["converged"]
        assert classify_branch(u, info) == "unresolved"
