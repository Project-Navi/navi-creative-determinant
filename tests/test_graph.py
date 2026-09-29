"""Finite-graph lane: the exact model of ``cd_formalization`` (CdFormal/Graph/*.lean at the
pinned revision), brought downstream.

Every test here checks either a definition copied from the Lean sources (unnormalized weighted
Laplacian, square-root gradient norm, energy, principal eigenvalue as a Rayleigh infimum, Jacobi
splitting) or a finite witness computed by hand. Nothing here normalizes weights or replaces the
selected gradient with a finite-difference stencil.
"""

import math

import numpy as np
import pytest

from cd.graph import (
    SemioticGraph,
    edge_condition_holds,
    energy,
    existence_theorem_applies,
    grad_norm,
    interior_connected,
    jacobi_map,
    laplacian,
    linfty_bound_graph,
    principal_eigenpair,
    proof_constants,
    residual,
    solve_graph,
    triangle,
)


def _triangle_with_b(b_value: float) -> SemioticGraph:
    return SemioticGraph(
        w=np.ones((3, 3)),
        boundary=np.array([True, False, False]),
        a=np.ones(3),
        b=np.full(3, b_value),
        c=np.ones(3),
        p=2.0,
    )


class TestTriangleCrosswalk:
    """``SemioticGraph.triangle``: K_3, unit weights (diagonal included), boundary {0},
    kappa = gamma = mu = 1, b = 2, c = 1, p = 2."""

    def test_triangle_matches_pinned_definition(self):
        G = triangle()
        np.testing.assert_array_equal(G.w, np.ones((3, 3)))
        np.testing.assert_array_equal(G.boundary, [True, False, False])
        np.testing.assert_array_equal(G.a, [1.0, 1.0, 1.0])
        np.testing.assert_array_equal(G.b, [2.0, 2.0, 2.0])
        np.testing.assert_array_equal(G.c, [1.0, 1.0, 1.0])
        assert G.p == 2.0

    def test_laplacian_of_solution_is_two_at_interior(self):
        """``triangle_isSolution``: (L u)(x) = 2 at both interior vertices for u = (0, 2, 2)."""
        u = np.array([0.0, 2.0, 2.0])
        np.testing.assert_allclose(laplacian(triangle(), u)[1:], [2.0, 2.0])

    def test_grad_norm_of_solution_is_two(self):
        """``triangle_gradNorm``: |grad u|(x) = 2 at both interior vertices (nonzero gradient term)."""
        u = np.array([0.0, 2.0, 2.0])
        np.testing.assert_allclose(grad_norm(triangle(), u)[1:], [2.0, 2.0])

    def test_solution_has_zero_residual_and_zero_boundary(self):
        u = np.array([0.0, 2.0, 2.0])
        np.testing.assert_allclose(residual(triangle(), u), 0.0, atol=1e-14)

    def test_energy_of_witness_is_minus_two(self):
        """``triangle_energy``: E(0, 1, 1) = -2, so lambda_1 < 0 by ``principalEigenvalue_neg``."""
        assert energy(triangle(), np.array([0.0, 1.0, 1.0])) == pytest.approx(-2.0)

    def test_principal_eigenvalue_is_minus_one_with_boundary_degree_retained(self):
        """Interior block of the *full* degree Laplacian minus diag(b) is [[0,-1],[-1,0]]."""
        lam, phi = principal_eigenpair(triangle())
        assert lam == pytest.approx(-1.0)
        assert phi[0] == 0.0
        np.testing.assert_allclose(phi[1:], [1 / math.sqrt(2)] * 2)
        assert np.all(phi[1:] > 0)

    def test_eigenpair_satisfies_eigen_equation_at_interior(self):
        """``exists_pos_eigenvector``: (L phi)(x) = b(x) phi(x) + lambda_1 phi(x) off the boundary."""
        G = triangle()
        lam, phi = principal_eigenpair(G)
        lhs = laplacian(G, phi)[1:]
        rhs = G.b[1:] * phi[1:] + lam * phi[1:]
        np.testing.assert_allclose(lhs, rhs, atol=1e-13)

    def test_existence_theorem_applies(self):
        report = existence_theorem_applies(triangle())
        assert report["interior_nonempty"]
        assert report["interior_connected"]
        assert report["edge_condition"]
        assert report["principal_eigenvalue"] == pytest.approx(-1.0)
        assert report["applies"]


class TestJacobiSplitting:
    def test_residual_identity_mul_sub_numer(self):
        """``mul_sub_numer``: (d(x)+K) u(x) - numer(u)(x) equals the equation residual."""
        G = triangle()
        u = np.array([0.0, 0.7, 1.1])
        K = 20.0
        F = jacobi_map(G, u, K)
        d = G.w.sum(axis=1)
        np.testing.assert_allclose(((d + K) * (u - F))[1:], residual(G, u)[1:], atol=1e-13)

    def test_solution_is_fixed_point(self):
        """``fixedPointMap_eq_iff_isSolution``: (0, 2, 2) is fixed for every K > 0."""
        u = np.array([0.0, 2.0, 2.0])
        for K in (0.5, 7.0, 62.5):
            np.testing.assert_allclose(jacobi_map(triangle(), u, K), u, atol=1e-14)

    def test_map_is_zero_on_boundary(self):
        F = jacobi_map(triangle(), np.array([5.0, 0.7, 1.1]), 3.0)
        assert F[0] == 0.0

    def test_map_requires_positive_shift(self):
        with pytest.raises(ValueError):
            jacobi_map(triangle(), np.zeros(3), 0.0)


class TestProofConstants:
    def test_constants_follow_lean_formulas_for_triangle(self):
        """The constants constructed inside ``exists_pos_graph`` for the triangle:
        t = -lambda_1 / (-lambda_1 + sum c) = 1/4, eps = t^{1/(p-1)} = 1/4,
        M = (1 + sum_y (|b_y| + a_y^2/4)/c_y)^{1/(p-1)} = 7.75,
        K = 1 + sum_x (a_x sum_y sqrt(w_xy) + c_x p M^{p-1} + |b_x|) = 62.5."""
        consts = proof_constants(triangle())
        assert consts["lam1"] == pytest.approx(-1.0)
        assert consts["eps"] == pytest.approx(0.25)
        assert consts["M"] == pytest.approx(7.75)
        assert consts["K"] == pytest.approx(62.5)
        sub, sup = consts["sub"], consts["sup"]
        assert sub[0] == 0.0 and sup[0] == 0.0
        np.testing.assert_allclose(sub[1:], 0.25 / math.sqrt(2))
        np.testing.assert_allclose(sup[1:], 7.75)

    def test_barriers_are_ordered_sub_and_supersolutions(self):
        """``smul_subsolution`` / ``plateau_supersolution`` inequalities hold at interior vertices."""
        G = triangle()
        consts = proof_constants(G)
        sub, sup = consts["sub"], consts["sup"]
        assert np.all(sub <= sup)
        # residual = L u - (a g + b u - c u_+^p); subsolution: residual <= 0, supersolution: >= 0
        assert np.all(residual(G, sub)[1:] <= 1e-13)
        assert np.all(residual(G, sup)[1:] >= -1e-13)

    def test_constants_require_negative_eigenvalue(self):
        with pytest.raises(ValueError):
            proof_constants(_triangle_with_b(0.5))


class TestGraphSolver:
    def test_iteration_from_subsolution_reaches_triangle_solution(self):
        """Monotone iteration of F_K from eps*phi converges to (0, 2, 2), which has a nonzero
        gradient term. Existence is the Lean theorem; the convergence observed here is a
        numerical fact about this run, reported through the residual."""
        u, info = solve_graph(triangle(), start="subsolution")
        assert info["converged"]
        assert info["termination"] == "converged"
        np.testing.assert_allclose(u, [0.0, 2.0, 2.0], atol=1e-8)
        assert info["residual_inf"] < 1e-10
        assert info["monotone"] == "nondecreasing"

    def test_iteration_from_plateau_decreases_to_same_solution(self):
        u, info = solve_graph(triangle(), start="plateau")
        assert info["converged"]
        np.testing.assert_allclose(u, [0.0, 2.0, 2.0], atol=1e-8)
        assert info["monotone"] == "nonincreasing"

    def test_exhausted_budget_is_not_success(self):
        u, info = solve_graph(triangle(), start="subsolution", max_iter=3)
        assert not info["converged"]
        assert info["termination"] == "max_iter"
        assert info["iters"] == 3

    def test_solver_rejects_invalid_budget_and_shift(self):
        with pytest.raises(ValueError):
            solve_graph(triangle(), max_iter=0)
        with pytest.raises(ValueError):
            solve_graph(triangle(), K=0.0)

    @pytest.mark.parametrize("bad", ["1e-12", True, np.bool_(True), np.nan, -1e-12])
    def test_solver_tolerances_must_be_nonnegative_numbers(self, bad):
        """A tolerance is a nonnegative finite real number; strings and bools that ``float``
        would silently convert are rejected like any other non-number."""
        with pytest.raises(ValueError):
            solve_graph(triangle(), atol=bad)
        with pytest.raises(ValueError):
            solve_graph(triangle(), rtol=bad)

    def test_nonfinite_start_terminates_as_nonfinite(self):
        u0 = np.array([0.0, np.nan, 1.0])
        with pytest.raises(ValueError):
            solve_graph(triangle(), start=u0)


class TestInvariances:
    def test_equation_invariant_to_diagonal_weights(self):
        """Self weights contribute zero to L, |grad u| and the energy (they cancel in the map)."""
        u = np.array([0.0, 0.7, 1.4])
        G1 = triangle()
        w2 = np.ones((3, 3))
        np.fill_diagonal(w2, [3.0, 9.0, 0.0])
        G2 = SemioticGraph(w=w2, boundary=G1.boundary, a=G1.a, b=G1.b, c=G1.c, p=G1.p)
        np.testing.assert_allclose(laplacian(G1, u), laplacian(G2, u))
        np.testing.assert_allclose(grad_norm(G1, u), grad_norm(G2, u))
        np.testing.assert_allclose(residual(G1, u), residual(G2, u))
        assert energy(G1, u) == pytest.approx(energy(G2, u))
        assert principal_eigenpair(G1)[0] == pytest.approx(principal_eigenpair(G2)[0])
        # The Jacobi map itself does depend on self weights away from fixed points (they enter
        # its numerator and denominator); they cancel exactly at fixed points, so the two graphs
        # have the same solutions.
        sol = np.array([0.0, 2.0, 2.0])
        for K in (1.0, 50.0):
            np.testing.assert_allclose(jacobi_map(G1, sol, K), sol, atol=1e-14)
            np.testing.assert_allclose(jacobi_map(G2, sol, K), sol, atol=1e-14)

    def test_vertex_permutation_equivariance(self):
        w = np.array([[1.0, 2.0, 0.0], [2.0, 4.0, 1.0], [0.0, 1.0, 0.0]])
        u = np.array([0.0, 0.7, 1.1])
        b = np.array([0.3, 0.5, 2.0])
        a = np.array([0.1, 0.3, 0.5])
        c = np.array([1.0, 2.0, 3.0])
        boundary = np.array([True, False, False])
        perm = np.array([2, 0, 1])
        G = SemioticGraph(w=w, boundary=boundary, a=a, b=b, c=c, p=2.0)
        Gp = SemioticGraph(
            w=w[np.ix_(perm, perm)], boundary=boundary[perm], a=a[perm], b=b[perm], c=c[perm], p=2.0
        )
        np.testing.assert_allclose(laplacian(Gp, u[perm]), laplacian(G, u)[perm])
        np.testing.assert_allclose(grad_norm(Gp, u[perm]), grad_norm(G, u)[perm])
        np.testing.assert_allclose(residual(Gp, u[perm]), residual(G, u)[perm])
        assert energy(Gp, u[perm]) == pytest.approx(energy(G, u))
        assert principal_eigenpair(Gp)[0] == pytest.approx(principal_eigenpair(G)[0])


class TestEdgeConditionAndConnectivity:
    def test_edge_condition_checked_at_both_ends(self):
        w = np.array([[1.0, 1.0, 1.0], [1.0, 0.0, 0.5], [1.0, 0.5, 0.0]])
        boundary = np.array([True, False, False])
        ok = SemioticGraph(
            w=w, boundary=boundary, a=np.array([1.0, 0.5, 0.5]), b=np.ones(3), c=np.ones(3), p=2.0
        )
        assert edge_condition_holds(ok)
        one_end_fails = SemioticGraph(
            w=w, boundary=boundary, a=np.array([1.0, 0.5, 1.0]), b=np.ones(3), c=np.ones(3), p=2.0
        )
        assert not edge_condition_holds(one_end_fails)

    def test_unweighted_graphs_satisfy_edge_condition(self):
        """``exists_pos_graph_of_unweighted``: weights in {0, 1} and a in [0, 1] suffice."""
        w = np.array(
            [[0.0, 1.0, 1.0, 0.0], [1.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0], [0.0, 1.0, 1.0, 0.0]]
        )
        G = SemioticGraph(
            w=w,
            boundary=np.array([True, False, False, False]),
            a=np.ones(4),
            b=np.ones(4),
            c=np.ones(4),
            p=2.0,
        )
        assert edge_condition_holds(G)

    def test_disconnected_interior_makes_theorem_inapplicable_not_nonexistent(self):
        # Star: boundary hub 0 joined to interior leaves 1, 2, 3 with no interior edges.
        w = np.zeros((4, 4))
        w[0, 1:] = 1.0
        w[1:, 0] = 1.0
        G = SemioticGraph(
            w=w,
            boundary=np.array([True, False, False, False]),
            a=np.ones(4),
            b=np.full(4, 3.0),
            c=np.ones(4),
            p=2.0,
        )
        assert not interior_connected(G)
        report = existence_theorem_applies(G)
        assert not report["applies"]
        assert "interior_connected" in report["failed"]
        # A solution still exists here (each leaf is a decoupled scalar problem); the theorem
        # is simply not the tool that proves it. u = 0 on the hub, u = s at each leaf with
        # s = a s + b s - s^2  =>  s = a + b - 1 = 3.
        u = np.array([0.0, 3.0, 3.0, 3.0])
        np.testing.assert_allclose(residual(G, u), 0.0, atol=1e-13)

    def test_single_interior_vertex_is_connected(self):
        G = SemioticGraph(
            w=np.array([[0.0, 0.25], [0.25, 0.0]]),
            boundary=np.array([True, False]),
            a=np.ones(2),
            b=np.ones(2),
            c=np.ones(2),
            p=2.0,
        )
        assert interior_connected(G)


class TestCounterexamples:
    def test_negative_eigenvalue_is_not_necessary_on_graphs(self):
        """Keep the triangle's weights, a = c = 1, p = 2 but set b = 1/2: (0, 1/2, 1/2) solves
        while lambda_1 = +1/2. The converse of the graph theorem is false in general."""
        G = _triangle_with_b(0.5)
        u = np.array([0.0, 0.5, 0.5])
        np.testing.assert_allclose(residual(G, u), 0.0, atol=1e-14)
        lam, _ = principal_eigenpair(G)
        assert lam == pytest.approx(0.5)
        assert lam > 0
        assert not existence_theorem_applies(G)["applies"]

    def test_graph_maximum_bound_differs_from_continuum_cap(self):
        """One boundary vertex joined to one interior vertex by weight 1/4, a = b = c = 1, p = 2:
        u = (0, 5/4) solves. The continuum-style cap (b/c)^{1/(p-1)} = 1 would reject it; the
        graph cap max ((b + a^2/4)_+ / c)^{1/(p-1)} = 5/4 is attained."""
        G = SemioticGraph(
            w=np.array([[0.0, 0.25], [0.25, 0.0]]),
            boundary=np.array([True, False]),
            a=np.ones(2),
            b=np.ones(2),
            c=np.ones(2),
            p=2.0,
        )
        u = np.array([0.0, 1.25])
        np.testing.assert_allclose(residual(G, u), 0.0, atol=1e-14)
        assert principal_eigenpair(G)[0] == pytest.approx(-0.75)
        assert u[1] > 1.0
        assert linfty_bound_graph(G) == pytest.approx(1.25)

    def test_graph_bound_holds_for_computed_solutions(self):
        u, info = solve_graph(triangle(), start="subsolution")
        assert info["converged"]
        assert u.max() <= linfty_bound_graph(triangle()) + 1e-9

    def test_graph_gradient_is_not_the_centered_difference(self):
        """Path 0-1-2 with unit weights and u = (0, 1, 0): centered derivative at the middle is
        zero, the graph gradient norm is sqrt(2)."""
        w = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
        G = SemioticGraph(
            w=w,
            boundary=np.array([True, False, True]),
            a=np.ones(3),
            b=np.zeros(3),
            c=np.ones(3),
            p=2.0,
        )
        u = np.array([0.0, 1.0, 0.0])
        assert (u[2] - u[0]) / 2.0 == 0.0
        assert grad_norm(G, u)[1] == pytest.approx(math.sqrt(2.0))

    def test_grid_graph_gradient_has_leading_term_two_u_prime_squared(self):
        """Nearest-neighbour 1D grid with weights h^-2: |grad_G u|^2 -> 2 (u')^2 at smooth
        nonstationary points, not (u')^2. A local expansion, not a convergence theorem."""
        for n in (50, 100, 200):
            x = np.linspace(0.0, 1.0, n + 2)
            h = x[1] - x[0]
            w = np.zeros((n + 2, n + 2))
            idx = np.arange(n + 1)
            w[idx, idx + 1] = w[idx + 1, idx] = 1.0 / h**2
            boundary = np.zeros(n + 2, dtype=bool)
            boundary[[0, -1]] = True
            G = SemioticGraph(
                w=w,
                boundary=boundary,
                a=np.zeros(n + 2),
                b=np.zeros(n + 2),
                c=np.ones(n + 2),
                p=2.0,
            )
            u = np.exp(x)
            g = grad_norm(G, u)
            ratio = g[1:-1] ** 2 / (np.exp(x[1:-1]) ** 2)
            assert np.max(np.abs(ratio - 2.0)) < 4 * h


class TestValidation:
    def test_rejects_negative_weight(self):
        w = np.ones((3, 3))
        w[0, 1] = w[1, 0] = -1.0
        with pytest.raises(ValueError):
            SemioticGraph(
                w=w,
                boundary=np.array([True, False, False]),
                a=np.ones(3),
                b=np.ones(3),
                c=np.ones(3),
                p=2.0,
            )

    def test_rejects_asymmetric_weight(self):
        w = np.ones((3, 3))
        w[0, 1] = 2.0
        with pytest.raises(ValueError):
            SemioticGraph(
                w=w,
                boundary=np.array([True, False, False]),
                a=np.ones(3),
                b=np.ones(3),
                c=np.ones(3),
                p=2.0,
            )

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"boundary": np.array([True, False])},
            {"a": np.array([1.0, 2.0, 1.0])},
            {"a": np.array([1.0, -0.1, 1.0])},
            {"c": np.array([1.0, 0.0, 1.0])},
            {"p": 1.0},
            {"b": np.array([1.0, np.nan, 1.0])},
            {"w": np.ones((3, 2))},
            {"w": np.full((3, 3), np.inf)},
        ],
    )
    def test_rejects_invalid_data(self, kwargs):
        base = dict(
            w=np.ones((3, 3)),
            boundary=np.array([True, False, False]),
            a=np.ones(3),
            b=np.ones(3),
            c=np.ones(3),
            p=2.0,
        )
        base.update(kwargs)
        with pytest.raises(ValueError):
            SemioticGraph(**base)

    def test_from_fields_builds_a_as_product(self):
        G = SemioticGraph.from_fields(
            w=np.ones((3, 3)),
            boundary=np.array([True, False, False]),
            kappa=np.full(3, 0.5),
            gamma=np.full(3, 0.5),
            mu=np.full(3, 0.5),
            b=np.ones(3),
            c=np.ones(3),
            p=2.0,
        )
        np.testing.assert_allclose(G.a, 0.125)

    def test_empty_interior_rejected_for_eigenvalue(self):
        G = SemioticGraph(
            w=np.ones((2, 2)),
            boundary=np.array([True, True]),
            a=np.ones(2),
            b=np.ones(2),
            c=np.ones(2),
            p=2.0,
        )
        with pytest.raises(ValueError):
            principal_eigenpair(G)
        assert not existence_theorem_applies(G)["applies"]

    def test_weights_are_never_normalized(self):
        G = SemioticGraph(
            w=2.0 * np.ones((3, 3)),
            boundary=np.array([True, False, False]),
            a=np.ones(3),
            b=np.ones(3),
            c=np.ones(3),
            p=2.0,
        )
        np.testing.assert_array_equal(G.w, 2.0)
        np.testing.assert_allclose(laplacian(G, np.array([0.0, 1.0, 1.0]))[1:], [2.0, 2.0])
