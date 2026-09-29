"""Tests for field constructors."""

import numpy as np
import pytest

from cd.fields import creative_drive, gaussian_bump_1d, gaussian_bump_2d, viability_canonical

NOT_A_NUMBER = ["0.5", True, np.nan]


class TestGaussianBump1d:
    def test_peak_at_center(self):
        x = np.linspace(0, 1, 102)
        bump = gaussian_bump_1d(x, center=0.5, sigma=0.1)
        peak_idx = np.argmax(bump)
        assert abs(x[peak_idx] - 0.5) < 0.02

    def test_amplitude(self):
        x = np.linspace(0, 1, 1002)
        bump = gaussian_bump_1d(x, center=0.5, sigma=0.1, amplitude=2.0)
        assert abs(bump.max() - 2.0) < 0.01

    def test_shape_matches_input(self):
        x = np.linspace(0, 1, 50)
        bump = gaussian_bump_1d(x, center=0.5, sigma=0.1)
        assert bump.shape == x.shape

    def test_range_01(self):
        x = np.linspace(0, 1, 102)
        bump = gaussian_bump_1d(x, center=0.5, sigma=0.1)
        assert bump.min() >= 0.0
        assert bump.max() <= 1.0 + 1e-10


class TestCanonicalClosureValidation:
    """b = κγ - λμ with κ, γ ∈ [0, 1] and λ >= 0: inputs outside the documented domain, and
    non-numbers (strings, bools, NaN), are rejected at the boundary; λ = 0 is admissible."""

    MU = np.array([0.0, 0.5, 1.0])

    @pytest.mark.parametrize("bad", NOT_A_NUMBER + [-0.1, 1.1])
    def test_kappa_and_gamma_must_be_numbers_in_the_unit_interval(self, bad):
        with pytest.raises(ValueError):
            viability_canonical(bad, 0.5, self.MU, 1.0)
        with pytest.raises(ValueError):
            viability_canonical(0.5, bad, self.MU, 1.0)
        with pytest.raises(ValueError):
            creative_drive(bad, 0.5, self.MU)
        with pytest.raises(ValueError):
            creative_drive(0.5, bad, self.MU)

    @pytest.mark.parametrize("bad", NOT_A_NUMBER + [-1.0])
    def test_lam_must_be_a_nonnegative_number(self, bad):
        with pytest.raises(ValueError):
            viability_canonical(0.5, 0.5, self.MU, bad)

    def test_lam_zero_is_accepted(self):
        np.testing.assert_allclose(viability_canonical(0.5, 0.5, self.MU, 0.0), 0.25)

    def test_nonfinite_mu_is_rejected(self):
        mu = np.array([0.0, np.nan, 1.0])
        with pytest.raises(ValueError):
            viability_canonical(0.5, 0.5, mu, 1.0)
        with pytest.raises(ValueError):
            creative_drive(0.5, 0.5, mu)

    def test_unit_endpoints_are_accepted(self):
        np.testing.assert_allclose(creative_drive(1.0, 1.0, self.MU), self.MU)
        np.testing.assert_allclose(creative_drive(0.0, 1.0, self.MU), 0.0)


class TestGaussianBumpValidation:
    X, Y = np.meshgrid(np.linspace(0, 1, 5), np.linspace(0, 1, 4))
    x = np.linspace(0, 1, 6)

    @pytest.mark.parametrize("bad", NOT_A_NUMBER + [0.0, -1.0])
    def test_sigma_must_be_a_positive_number(self, bad):
        with pytest.raises(ValueError):
            gaussian_bump_1d(self.x, 0.5, bad)
        with pytest.raises(ValueError):
            gaussian_bump_2d(self.X, self.Y, 0.5, 0.5, bad)

    @pytest.mark.parametrize("bad", NOT_A_NUMBER)
    def test_center_and_amplitude_must_be_finite_numbers(self, bad):
        with pytest.raises(ValueError):
            gaussian_bump_1d(self.x, bad, 0.1)
        with pytest.raises(ValueError):
            gaussian_bump_1d(self.x, 0.5, 0.1, amplitude=bad)
        with pytest.raises(ValueError):
            gaussian_bump_2d(self.X, self.Y, bad, 0.5, 0.1)
        with pytest.raises(ValueError):
            gaussian_bump_2d(self.X, self.Y, 0.5, bad, 0.1)
        with pytest.raises(ValueError):
            gaussian_bump_2d(self.X, self.Y, 0.5, 0.5, 0.1, amplitude=bad)

    def test_nonfinite_grid_is_rejected(self):
        with pytest.raises(ValueError):
            gaussian_bump_1d(np.array([0.0, np.inf, 1.0]), 0.5, 0.1)
        with pytest.raises(ValueError):
            gaussian_bump_2d(self.X, np.where(self.Y > 0.5, np.nan, self.Y), 0.5, 0.5, 0.1)
