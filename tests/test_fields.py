# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nelson Spence
"""Tests for field constructors."""

import numpy as np

from cd.fields import gaussian_bump_1d


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
