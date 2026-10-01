"""Spatial statistics with explicit population, coordinates and quadrature, and the input
domain of the L-infinity reference bound."""

import numpy as np
import pytest

from cd.analysis import linfty_bound, presence_statistics


class TestInteriorMean:
    def test_interior_mean_includes_zeros(self):
        stats = presence_statistics(np.array([0.0, 1.0, 0.0, 0.0]), x=np.linspace(0.0, 1.0, 4))
        assert stats["mean"] == pytest.approx(0.5)
        assert stats["dimension"] == 1
        assert stats["interior_count"] == 2

    def test_2d_interior_mean(self):
        Phi = np.outer([0.0, 1.0, 0.0], [0.0, 1.0, 0.0])
        stats = presence_statistics(Phi, x=np.array([0.0, 0.5, 1.0]), y=np.array([0.0, 0.5, 1.0]))
        assert stats["mean"] == pytest.approx(1.0)
        assert stats["interior_count"] == 1


class TestQuadrature:
    def test_2d_integral_has_area_measure(self):
        Phi = np.outer([0.0, 1.0, 0.0], [0.0, 1.0, 0.0])
        stats = presence_statistics(Phi, x=np.array([0.0, 0.5, 1.0]), y=np.array([0.0, 0.5, 1.0]))
        assert stats["total"] == pytest.approx(0.25)
        assert stats["dimension"] == 2

    def test_1d_integral_of_sine_converges_to_two(self):
        x = np.linspace(0.0, np.pi, 2001)
        stats = presence_statistics(np.sin(x), x=x)
        assert stats["total"] == pytest.approx(2.0, abs=1e-5)

    def test_trapezoid_is_exact_for_linear_field_on_nonuniform_grid(self):
        x = np.array([0.0, 0.1, 0.35, 0.6, 1.0])
        Phi = 3.0 * x + 1.0
        stats = presence_statistics(Phi, x=x)
        assert stats["total"] == pytest.approx(1.5 + 1.0)

    def test_2d_matches_numpy_tensor_trapezoid(self):
        x = np.linspace(0.0, 2.0, 7)
        y = np.linspace(0.0, 1.0, 5)
        X, Y = np.meshgrid(x, y)
        Phi = np.sin(np.pi * X / 2.0) * np.sin(np.pi * Y)
        trap = getattr(np, "trapezoid", None) or getattr(np, "trapz")
        expected = trap(trap(Phi, x, axis=1), y)
        stats = presence_statistics(Phi, x=x, y=y)
        assert stats["total"] == pytest.approx(expected)

    def test_2d_anisotropic_spacing(self):
        x = np.linspace(0.0, 2.0, 3)
        y = np.linspace(0.0, 1.0, 3)
        Phi = np.outer([0.0, 1.0, 0.0], [0.0, 1.0, 0.0])
        stats = presence_statistics(Phi, x=x, y=y)
        assert stats["total"] == pytest.approx(0.5)


class TestSupportFraction:
    def test_support_fraction_over_interior_population(self):
        Phi = np.array([0.0, 1.0, 0.0, 0.0])
        stats = presence_statistics(Phi, x=np.linspace(0.0, 1.0, 4))
        assert stats["support_fraction"] == pytest.approx(0.5)

    def test_zero_field(self):
        stats = presence_statistics(np.zeros(5), x=np.linspace(0.0, 1.0, 5))
        assert stats["support_fraction"] == 0.0
        assert stats["total"] == 0.0
        assert stats["max"] == 0.0

    def test_positive_field_below_the_zero_branch_tolerance_keeps_its_support(self):
        """Maximum 5e-7 is below the zero-branch tolerance 1e-6 of ``classify_branch``, but the
        field is not zero: the support fraction is a separate measurement and counts its
        node."""
        stats = presence_statistics(np.array([0.0, 5e-7, 0.0]), x=np.array([0.0, 0.5, 1.0]))
        assert stats["max"] == pytest.approx(5e-7)
        assert stats["mean"] == pytest.approx(5e-7)
        assert stats["support_fraction"] == 1.0

    def test_field_at_rounding_level_has_no_support(self):
        """At or below the absolute floor 1e-10 the relative 1% rule is not applied."""
        stats = presence_statistics(np.array([0.0, 5e-11, 0.0]), x=np.array([0.0, 0.5, 1.0]))
        assert stats["support_fraction"] == 0.0

    def test_small_field_support_is_relative_to_its_maximum(self):
        Phi = np.array([0.0, 2e-6, 1e-9, 2e-6, 0.0])
        stats = presence_statistics(Phi, x=np.linspace(0.0, 1.0, 5))
        assert stats["max"] == pytest.approx(2e-6)
        assert stats["support_fraction"] == pytest.approx(2.0 / 3.0)


class TestRejections:
    def test_ambiguous_2d_call_is_rejected(self):
        Phi = np.outer([0.0, 1.0, 0.0], [0.0, 1.0, 0.0])
        with pytest.raises(ValueError):
            presence_statistics(Phi, x=np.array([0.0, 0.5, 1.0]))

    def test_missing_coordinates_rejected(self):
        with pytest.raises(ValueError):
            presence_statistics(np.zeros(4))

    def test_coordinate_length_mismatch_rejected(self):
        with pytest.raises(ValueError):
            presence_statistics(np.zeros(4), x=np.linspace(0.0, 1.0, 5))

    def test_non_monotone_coordinates_rejected(self):
        with pytest.raises(ValueError):
            presence_statistics(np.zeros(4), x=np.array([0.0, 0.5, 0.25, 1.0]))

    def test_nonfinite_field_rejected(self):
        with pytest.raises(ValueError):
            presence_statistics(np.array([0.0, np.nan, 0.0]), x=np.linspace(0.0, 1.0, 3))


class TestLinftyBoundValidation:
    """Lemma 3.10 bound ``(max(q)_+ / min(c))^{1/(p-1)}``: the inputs are finite scalars or
    fields, ``c`` positive everywhere; scalar strings and bools are rejected, not coerced, and
    arrays are converted to float."""

    @pytest.mark.parametrize("bad", ["15", True, np.bool_(True), np.nan])
    def test_potential_must_be_a_finite_number_or_field(self, bad):
        with pytest.raises(ValueError):
            linfty_bound(bad, 10.0, 2.0)

    @pytest.mark.parametrize("bad", ["10", True, np.bool_(True), np.nan, 0.0, -1.0])
    def test_saturation_must_be_a_positive_number_or_field(self, bad):
        with pytest.raises(ValueError):
            linfty_bound(15.0, bad, 2.0)

    def test_nonfinite_field_entries_are_rejected(self):
        with pytest.raises(ValueError):
            linfty_bound(np.array([1.0, np.nan]), 1.0, 2.0)
        with pytest.raises(ValueError):
            linfty_bound(1.0, np.array([1.0, np.inf]), 2.0)
        with pytest.raises(ValueError):
            linfty_bound(1.0, np.array([1.0, 0.0]), 2.0)

    def test_closed_form_on_scalars_and_fields(self):
        """Lemma 3.10: the bound is ``(B/c0)^{1/(p-1)}`` with ``B = max(beta_b)_+`` and
        ``c0 = min(c)``, for scalars and for fields; ``B <= 0`` gives 0."""
        assert linfty_bound(15.0, 10.0, 2.0) == pytest.approx(1.5)
        assert linfty_bound(np.array([-1.0, 15.0]), np.array([10.0, 40.0]), 2.0) == pytest.approx(
            1.5
        )
        assert linfty_bound(-3.0, 1.0, 2.0) == 0.0
