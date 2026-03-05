# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nelson Spence
"""
Test suite for Creative Determinant PDE framework.

Validates core mathematical claims:
1. Eigenvalue computation matches analytic formula
2. Picard iteration converges
3. Residuals are small (numerical correctness)
4. Threshold behavior: below → trivial, above → nontrivial
5. Grid refinement shows O(h²) convergence

Run with: pytest tests/test_core.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add src to path for development installs
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cd import (
    principal_eigenvalue_1d,
    residual_1d,
    solve_1d_picard,
)
from cd.eigenvalues import viability_threshold_1d

# =============================================================================
# Test 1: Eigenvalue matches analytic formula
# =============================================================================


class TestEigenvalueComputation:
    """Verify λ₁(-Δ - βb) = (π/L)² - βb for constant b."""

    def test_eigenvalue_analytic_match(self):
        """Numerical eigenvalue should match analytic formula within tolerance."""
        L = 1.0
        N = 600
        b_const = 0.8

        for beta in [5.0, 10.0, 15.0, 20.0]:
            lam_numeric = principal_eigenvalue_1d(N, L, beta * b_const)
            lam_analytic = (np.pi / L) ** 2 - beta * b_const

            # Should match within 0.1% for this grid resolution
            rel_error = abs(lam_numeric - lam_analytic) / abs(lam_analytic)
            assert rel_error < 0.001, (
                f"β={beta}: numeric={lam_numeric:.6f}, analytic={lam_analytic:.6f}, error={rel_error:.2%}"
            )

    def test_eigenvalue_sign_at_threshold(self):
        """Eigenvalue should be positive below threshold, negative above."""
        L = 1.0
        N = 600
        b_const = 0.8
        beta_star = viability_threshold_1d(L, b_const)

        # Below threshold
        lam_below = principal_eigenvalue_1d(N, L, 0.8 * beta_star * b_const)
        assert lam_below > 0, f"Below threshold: λ₁ should be positive, got {lam_below}"

        # Above threshold
        lam_above = principal_eigenvalue_1d(N, L, 1.2 * beta_star * b_const)
        assert lam_above < 0, f"Above threshold: λ₁ should be negative, got {lam_above}"


# =============================================================================
# Test 2: Picard iteration converges
# =============================================================================


class TestPicardConvergence:
    """Verify Picard iteration converges within tolerance."""

    def test_convergence_above_threshold(self):
        """Solver should converge for above-threshold parameters."""
        L = 1.0
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_above = 1.2 * beta_star

        x, Phi, info = solve_1d_picard(L, N, a=a, beta_b=beta_above * b, c=c, p=p)

        assert info["inf_err"] < 1e-8, f"Solver did not converge: final error = {info['inf_err']}"
        assert info["iters"] < 8000, f"Solver took too many iterations: {info['iters']}"

    def test_convergence_below_threshold(self):
        """Solver should converge (to trivial solution) below threshold."""
        L = 1.0
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_below = 0.8 * beta_star

        x, Phi, info = solve_1d_picard(L, N, a=a, beta_b=beta_below * b, c=c, p=p)

        assert info["inf_err"] < 1e-8, f"Solver did not converge: final error = {info['inf_err']}"


# =============================================================================
# Test 3: Residuals are small
# =============================================================================


class TestResidualSmall:
    """Verify computed solutions actually satisfy the PDE."""

    def test_residual_above_threshold(self):
        """Residual should be small for converged solution."""
        L = 1.0
        N = 800
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_above = 1.2 * beta_star

        x, Phi, info = solve_1d_picard(L, N, a=a, beta_b=beta_above * b, c=c, p=p)
        res = residual_1d(x, Phi, a=a, beta_b=beta_above * b, c=c, p=p)
        res_inf = np.linalg.norm(res, np.inf)

        assert res_inf < 1e-4, f"Residual too large: ||R||_∞ = {res_inf}"


# =============================================================================
# Test 4: Threshold behavior
# =============================================================================


class TestThresholdBehavior:
    """Verify bifurcation: trivial below threshold, nontrivial above."""

    def test_trivial_below_threshold(self):
        """Below threshold, solution should be essentially zero."""
        L = 1.0
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_below = 0.8 * beta_star

        x, Phi, info = solve_1d_picard(L, N, a=a, beta_b=beta_below * b, c=c, p=p)

        # Should be essentially zero (< 1e-6)
        assert info["maxPhi"] < 1e-6, (
            f"Below threshold: expected trivial solution, got maxPhi = {info['maxPhi']}"
        )

    def test_nontrivial_above_threshold(self):
        """Above threshold, solution should have significant presence."""
        L = 1.0
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_above = 1.2 * beta_star

        x, Phi, info = solve_1d_picard(L, N, a=a, beta_b=beta_above * b, c=c, p=p)

        # Should be nontrivial (> 0.01)
        assert info["maxPhi"] > 0.01, (
            f"Above threshold: expected nontrivial solution, got maxPhi = {info['maxPhi']}"
        )

    def test_threshold_sharpness(self):
        """Transition should be sharp: small change in β causes large change in maxΦ."""
        L = 1.0
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)

        # Just below
        _, _, info_below = solve_1d_picard(L, N, a=a, beta_b=0.95 * beta_star * b, c=c, p=p)
        # Just above
        _, _, info_above = solve_1d_picard(L, N, a=a, beta_b=1.05 * beta_star * b, c=c, p=p)

        # The ratio should be large (phase transition, not gradual)
        if info_below["maxPhi"] > 1e-10:
            ratio = info_above["maxPhi"] / info_below["maxPhi"]
            assert ratio > 100, f"Transition not sharp enough: ratio = {ratio}"
        else:
            # Below is essentially zero, above should be nonzero
            assert info_above["maxPhi"] > 0.001, "Above threshold should be nontrivial"


# =============================================================================
# Test 5: Grid refinement convergence
# =============================================================================


class TestGridRefinement:
    """Verify O(h²) convergence under grid refinement."""

    def test_solution_convergence_order(self):
        """Solution error should decrease as O(h²) with grid refinement."""
        L = 1.0
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_above = 1.2 * beta_star

        # Use finest grid as "truth"
        N_fine = 1600
        x_fine, Phi_fine, _ = solve_1d_picard(L, N_fine, a=a, beta_b=beta_above * b, c=c, p=p)

        Ns = [100, 200, 400]
        errors = []

        for N in Ns:
            x, Phi, _ = solve_1d_picard(L, N, a=a, beta_b=beta_above * b, c=c, p=p)
            # Interpolate fine solution to coarse grid for comparison
            Phi_fine_interp = np.interp(x, x_fine, Phi_fine)
            err = np.linalg.norm(Phi - Phi_fine_interp, np.inf)
            errors.append(err)

        # Check convergence rate: error should decrease by ~4x when N doubles (O(h²))
        rate_1 = errors[0] / errors[1]  # N: 100 → 200
        rate_2 = errors[1] / errors[2]  # N: 200 → 400

        # Should be approximately 4 (second-order), allow range [2.0, 8.0]
        assert 2.0 < rate_1 < 8.0, f"Convergence rate 100→200: expected ~4, got {rate_1:.2f}"
        assert 2.0 < rate_2 < 8.0, f"Convergence rate 200→400: expected ~4, got {rate_2:.2f}"

    def test_solution_stability(self):
        """Solution maxPhi should stabilize under refinement."""
        L = 1.0
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8

        beta_star = viability_threshold_1d(L, b)
        beta_above = 1.2 * beta_star

        max_phis = []
        for N in [200, 400, 800]:
            _, _, info = solve_1d_picard(L, N, a=a, beta_b=beta_above * b, c=c, p=p)
            max_phis.append(info["maxPhi"])

        # Successive differences should decrease
        diff_1 = abs(max_phis[1] - max_phis[0])
        diff_2 = abs(max_phis[2] - max_phis[1])

        assert diff_2 < diff_1, f"Solution not converging: diff_1={diff_1}, diff_2={diff_2}"
        assert diff_2 < 0.01, f"Solution not stable enough: diff_2={diff_2}"


# =============================================================================
# Test 6: Edge cases
# =============================================================================


class TestEdgeCases:
    """Document and verify edge case behavior."""

    def test_zero_care_coherence(self):
        """When b ≤ 0 everywhere, solution should be trivial."""
        L = 1.0
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        beta_b = -5.0  # Negative viability everywhere

        x, Phi, info = solve_1d_picard(L, N, a=a, beta_b=beta_b, c=c, p=p)

        assert info["maxPhi"] < 1e-6, (
            f"Negative viability: expected trivial, got maxPhi = {info['maxPhi']}"
        )

    def test_large_domain(self):
        """Large domain should lower threshold (larger L → smaller (π/L)²)."""
        N = 400
        p = 2.0
        c = 10.0
        a = 0.0
        b = 0.8
        beta = 5.0  # Fixed β

        # Small domain: might be below threshold
        L_small = 0.5
        _, _, info_small = solve_1d_picard(L_small, N, a=a, beta_b=beta * b, c=c, p=p)

        # Large domain: should be above threshold
        L_large = 2.0
        _, _, info_large = solve_1d_picard(L_large, N, a=a, beta_b=beta * b, c=c, p=p)

        # Larger domain should have higher presence (easier to cross threshold)
        assert info_large["maxPhi"] >= info_small["maxPhi"], (
            f"Larger domain should have >= presence: L=0.5 → {info_small['maxPhi']}, L=2.0 → {info_large['maxPhi']}"
        )


# =============================================================================
# Run directly
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
