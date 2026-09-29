"""A positive continuum solution below the linear spectral threshold (paper Proposition 3.21:
the converse of Theorem 3.16 fails with an active gradient term). The barrier identities are
analytic; the library solve and the collocation solve are corroboration, not the proof.

Model: -u'' = |u'| + (3/4) u - u^2 on (0, pi), u(0) = u(pi) = 0; lambda_1(-d^2/dx^2 - 3/4) = 1/4.
"""

import numpy as np
import pytest
from scipy.integrate import solve_bvp

from cd import principal_eigenvalue_1d, residual_1d, solve_1d_picard


def barrier(x):
    """phi(x) = e^{(pi/2 - t)/2} sin(t/2) / sin(pi/4), t = min(x, pi - x); v = phi/4."""
    x = np.asarray(x, dtype=float)
    t = np.minimum(x, np.pi - x)
    factor = np.exp((np.pi / 2 - t) / 2) / np.sin(np.pi / 4)
    phi = factor * np.sin(t / 2)
    dphi = np.where(x <= np.pi / 2, 1.0, -1.0) * 0.5 * factor * (np.cos(t / 2) - np.sin(t / 2))
    ddphi = -0.5 * factor * np.cos(t / 2)
    return phi, dphi, ddphi


class TestBarrierIdentities:
    def test_phi_solves_its_linear_gradient_equation_and_is_c2(self):
        x = np.linspace(0.0, np.pi, 4001)
        phi, dphi, ddphi = barrier(x)
        np.testing.assert_allclose(-ddphi, np.abs(dphi) + phi / 2, atol=1e-13)
        assert phi.max() == pytest.approx(1.0)
        assert phi[0] == 0.0 and abs(phi[-1]) < 1e-15
        # C^2 across the midpoint: value 1, derivative 0, second derivative -1/2 from both sides
        mid = np.pi / 2
        left = barrier(np.array([mid - 1e-9]))
        right = barrier(np.array([mid + 1e-9]))
        assert left[1] == pytest.approx(0.0, abs=1e-8) and right[1] == pytest.approx(0.0, abs=1e-8)
        assert left[2] == pytest.approx(-0.5, abs=1e-8) and right[2] == pytest.approx(
            -0.5, abs=1e-8
        )

    def test_quarter_of_phi_is_a_subsolution_with_residual_v_times_v_minus_quarter(self):
        x = np.linspace(0.0, np.pi, 4001)
        phi, dphi, ddphi = barrier(x)
        v, dv, ddv = phi / 4, dphi / 4, ddphi / 4
        residual = -ddv - (np.abs(dv) + 0.75 * v - v**2)
        np.testing.assert_allclose(residual, v * (v - 0.25), atol=1e-13)
        assert np.max(residual) <= 1e-14
        assert np.all(v[1:-1] > 0) and v.max() == pytest.approx(0.25)

    def test_constant_three_quarters_is_a_supersolution(self):
        U = 0.75
        assert 0.0 >= 0.0 + 0.75 * U - U**2  # -U'' = 0 >= |U'| + (3/4)U - U^2 = 0


class TestNumericalCorroboration:
    def test_linear_eigenvalue_is_positive(self):
        assert principal_eigenvalue_1d(800, np.pi, 0.75) == pytest.approx(0.25, abs=1e-5)
        assert principal_eigenvalue_1d(800, np.pi, 0.75) > 0

    def test_library_solver_finds_positive_branch_between_the_barriers(self):
        N = 800
        x = np.linspace(0.0, np.pi, N + 2)
        v = barrier(x)[0] / 4
        _, u, info = solve_1d_picard(
            np.pi, N, 1.0, 0.75, 1.0, p=2.0, initial_guess=v, max_iter=20000
        )
        assert info["converged"] and info["branch"] == "positive"
        assert np.max(np.abs(residual_1d(x, u, 1.0, 0.75, 1.0, 2.0))) < 1e-7
        assert np.all(u >= v - 1e-12) and u.max() <= 0.75
        assert u.max() == pytest.approx(0.2727, abs=2e-3)

    def test_independent_collocation_agrees(self):
        N = 800
        x = np.linspace(0.0, np.pi, N + 2)
        v, dv, _ = barrier(x)
        _, u, info = solve_1d_picard(
            np.pi, N, 1.0, 0.75, 1.0, p=2.0, initial_guess=v / 4, max_iter=20000
        )
        assert info["converged"]

        def fun(t, y):
            return np.vstack([y[1], -np.abs(y[1]) - 0.75 * y[0] + y[0] ** 2])

        def bc(left, right):
            return np.array([left[0], right[1]])

        t = np.linspace(0.0, np.pi / 2, 401)
        ph, dph, _ = barrier(t)
        sol = solve_bvp(fun, bc, t, np.vstack([0.4 * ph, 0.4 * dph]), tol=1e-9, max_nodes=100000)
        assert sol.status == 0, sol.message
        half = x[x <= np.pi / 2]
        assert np.max(np.abs(u[: half.size] - sol.sol(half)[0])) < 1e-5
