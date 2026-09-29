"""Regressions for the defects found in the mathematical review of the Stage A candidate.

Each test expresses the corrected behaviour of the real ``cd`` package and failed at the
reviewed head (21c2402) for the stated reason. Graph tests evaluate operators directly from
pair differences so that the spectral assembly is checked against an independent formula.
"""

import numpy as np
import pytest

from cd import graph as G
from cd import solve_1d_picard, solve_2d_picard
from cd.analysis import check_convergence, classify_branch, solution_type


class TestGraphSpectralAssembly:
    """Self weights contribute nothing to L_G; the assembled operator must not see them."""

    def test_self_weights_do_not_change_eigenvalue_or_applicability(self, graph_with_self_weight):
        small = graph_with_self_weight(0.0)
        large = graph_with_self_weight(1e20)
        assert G.principal_eigenpair(small)[0] == pytest.approx(1.0)
        assert G.principal_eigenpair(large)[0] == pytest.approx(1.0)
        assert not G.existence_theorem_applies(large)["applies"]
        assert G.existence_theorem_applies(large)["spectral_status"] == "nonnegative"

    def test_eigenvector_matches_direct_operator_with_large_self_weights(
        self, graph_with_self_weight
    ):
        graph = graph_with_self_weight(1e20)
        lam, phi = G.principal_eigenpair(graph)
        r = G.laplacian(graph, phi) - graph.b * phi - lam * phi
        assert np.max(np.abs(r[graph.interior])) < 1e-10
        assert G.energy(graph, phi) == pytest.approx(lam)

    def test_rayleigh_quotient_of_returned_vector_matches_eigenvalue(self):
        rng = np.random.default_rng(3)
        w = rng.random((6, 6))
        w = np.round(w + w.T, 6)
        w[np.diag_indices(6)] = 1e12
        boundary = np.array([True, False, False, False, False, True])
        graph = G.SemioticGraph(
            w=w, boundary=boundary, a=np.zeros(6), b=rng.random(6), c=np.ones(6), p=2.0
        )
        lam, phi = G.principal_eigenpair(graph)
        assert G.energy(graph, phi) / float(np.sum(phi**2)) == pytest.approx(lam, abs=1e-9)
        report = G.spectral_report(graph)
        assert report["defect"] < 1e-9

    def test_false_edge_condition_is_not_certified_by_additive_slack(self):
        graph = G.SemioticGraph(
            w=np.array([[0.0, 1e-28], [1e-28, 0.0]]),
            boundary=np.zeros(2, dtype=bool),
            a=np.full(2, 5e-13),
            b=np.ones(2),
            c=np.ones(2),
            p=2.0,
        )
        assert not G.edge_condition_holds(graph)
        assert not G.existence_theorem_applies(graph)["applies"]

    def test_edge_condition_is_exact_at_equality(self):
        graph = G.SemioticGraph(
            w=np.array([[0.0, 1.0], [1.0, 0.0]]),
            boundary=np.zeros(2, dtype=bool),
            a=np.ones(2),
            b=np.ones(2),
            c=np.ones(2),
            p=2.0,
        )
        assert G.edge_condition_holds(graph)

    def test_nearly_symmetric_weights_are_rejected_not_silently_symmetrized(self):
        w = np.ones((3, 3))
        w[0, 1] = 1.0 + 1e-13
        with pytest.raises(ValueError):
            G.SemioticGraph(
                w=w,
                boundary=np.array([True, False, False]),
                a=np.ones(3),
                b=np.ones(3),
                c=np.ones(3),
                p=2.0,
            )

    def test_eigenvalue_near_zero_is_indeterminate_not_certified(self):
        """lambda_1 = 0 exactly (b equal to the smallest Dirichlet eigenvalue) must not be
        reported as negative; the theorem needs a definite sign."""
        w = np.array([[0.0, 1.0], [1.0, 0.0]])
        graph = G.SemioticGraph(
            w=w, boundary=np.array([True, False]), a=np.zeros(2), b=np.ones(2), c=np.ones(2), p=2.0
        )
        report = G.existence_theorem_applies(graph)
        assert report["principal_eigenvalue"] == pytest.approx(0.0, abs=1e-14)
        assert report["spectral_status"] == "indeterminate"
        assert not report["applies"]

    def test_clearly_negative_eigenvalue_is_certified_with_rayleigh_witness(self):
        report = G.existence_theorem_applies(G.triangle())
        assert report["spectral_status"] == "negative"
        assert report["rayleigh_upper_bound"] < 0
        assert report["applies"]

    def test_jacobi_map_keeps_exact_self_weight_semantics(self, graph_with_self_weight):
        """Self weights do enter the Jacobi splitting (numerator and denominator) and cancel
        at fixed points; the residual identity must hold with them present."""
        graph = graph_with_self_weight(3.0, a=1.0)
        u = np.array([0.0, 0.7, 1.1])
        K = 5.0
        F = G.jacobi_map(graph, u, K)
        d = graph.w.sum(axis=1)  # includes the self weight, as in Lean's numer/denominator
        np.testing.assert_allclose(((d + K) * (u - F))[1:], G.residual(graph, u)[1:], atol=1e-13)


class TestSolverContract:
    @pytest.mark.parametrize("start", [0.0, 0.7])
    def test_exact_initial_solution_is_accepted_consistently(self, start):
        _, u, info = solve_1d_picard(1.0, 1, 0.0, 15.0, 10.0, initial_guess=np.array([start]))
        assert info["converged"]
        assert info["iters"] == 0
        assert info["inf_err"] == 0.0
        assert check_convergence(info)[0]
        assert np.all(np.isfinite(u))

    def test_negative_initial_data_is_rejected(self):
        with pytest.raises(ValueError):
            solve_1d_picard(1.0, 1, 0.0, 8.0, 1.0, initial_guess=np.array([-1.0]))
        with pytest.raises(ValueError):
            solve_2d_picard(1.0, 1.0, 2, 2, 0.0, 8.0, 1.0, initial_guess=-np.ones((2, 2)))

    def test_mixed_sign_field_is_not_labelled_nonnegative(self):
        info = {"converged": True, "termination": "converged", "maxPhi": 1.0, "residual_inf": 0.0}
        assert classify_branch(np.array([0.0, 1.0, -1.0, 0.0]), info) == "invalid"

    def test_negative_field_is_not_labelled_zero(self):
        info = {"converged": True, "termination": "converged", "maxPhi": 0.0, "residual_inf": 0.0}
        assert classify_branch(np.array([0.0, -1.0, 0.0]), info) == "invalid"

    def test_convergence_checker_rejects_contradictory_diagnostics(self):
        info = {
            "converged": True,
            "termination": "converged",
            "iters": 1,
            "inf_err": 0.0,
            "residual_inf": 100.0,
            "residual_scale": 1.0,
            "residual_atol": 1e-8,
            "residual_rtol": 0.0,
            "tol": 1e-10,
            "boundary_err": 1.0,
            "maxPhi": 1.0,
        }
        ok, msg = check_convergence(info)
        assert not ok
        assert "residual" in msg and "exceeds" in msg

    def test_convergence_checker_rejects_boundary_violation_alone(self):
        info = {
            "converged": True,
            "termination": "converged",
            "iters": 3,
            "inf_err": 0.0,
            "residual_inf": 0.0,
            "residual_scale": 1.0,
            "residual_atol": 1e-8,
            "residual_rtol": 0.0,
            "tol": 1e-10,
            "boundary_err": 1e-3,
            "maxPhi": 1.0,
        }
        ok, msg = check_convergence(info)
        assert not ok
        assert "boundary error" in msg

    def test_convergence_checker_rejects_incomplete_reports(self):
        assert not check_convergence(
            {
                "converged": True,
                "termination": "converged",
                "iters": 3,
                "inf_err": 0.0,
                "residual_inf": 0.0,
            }
        )[0]

    def test_solution_type_without_convergence_flag_is_unresolved(self):
        assert solution_type({"maxPhi": 0.5}) == "unresolved"

    def test_graph_exact_initial_solution_has_defined_update_diagnostic(self):
        _, info = G.solve_graph(G.triangle(), start=np.array([0.0, 2.0, 2.0]))
        assert info["converged"]
        assert info["iters"] == 0
        assert info["update_inf"] == 0.0
