"""3D Dirichlet Laplacian and principal eigenvalue with an explicit (z, y, x) array convention.

The flat unknown index is (iz * Ny + iy) * Nx + ix (x fastest), so full-grid arrays have shape
(Nz+2, Ny+2, Nx+2). An asymmetric, anisotropic potential is compared with an independently
assembled dense matrix; a wrong layout must be rejected by shape.
"""

import numpy as np
import pytest

from cd import grid_3d, laplacian_3d_dirichlet, principal_eigenpair_3d, principal_eigenvalue_3d


def _independent_matrix(Nx, Ny, Nz, Lx, Ly, Lz):
    shape = (Nz, Ny, Nx)
    n = Nx * Ny * Nz
    A = np.zeros((n, n))
    hs = (Lz / (Nz + 1), Ly / (Ny + 1), Lx / (Nx + 1))
    for ind in np.ndindex(shape):
        i = np.ravel_multi_index(ind, shape)
        for axis, h in enumerate(hs):
            A[i, i] += 2 / h**2
            for direction in (-1, 1):
                nxt = list(ind)
                nxt[axis] += direction
                if 0 <= nxt[axis] < shape[axis]:
                    A[i, np.ravel_multi_index(tuple(nxt), shape)] = -1 / h**2
    return A


class TestLaplacian3d:
    def test_constant_potential_matches_sum_of_discrete_formulas(self):
        Nx, Ny, Nz, Lx, Ly, Lz, q = 3, 4, 5, 1.0, 2.0, 0.5, 7.0
        hx, hy, hz = Lx / (Nx + 1), Ly / (Ny + 1), Lz / (Nz + 1)
        expected = (
            sum(
                4 / h**2 * np.sin(np.pi * h / (2 * L)) ** 2
                for h, L in ((hx, Lx), (hy, Ly), (hz, Lz))
            )
            - q
        )
        assert principal_eigenvalue_3d(Nx, Ny, Nz, Lx, Ly, Lz, q) == pytest.approx(
            expected, abs=1e-9
        )

    def test_asymmetric_anisotropic_potential_matches_independent_assembly(self):
        Nx, Ny, Nz, Lx, Ly, Lz = 2, 3, 4, 1.0, 2.0, 3.0
        Z, Y, X = grid_3d(Nx, Ny, Nz, Lx, Ly, Lz)
        assert X.shape == (Nz + 2, Ny + 2, Nx + 2)
        q = 30 * X / Lx + 20 * (Y / Ly) ** 2 + 10 * (Z / Lz) ** 3
        A = _independent_matrix(Nx, Ny, Nz, Lx, Ly, Lz)
        # Independent assembly indexes physical (z, y, x); q[1:-1,1:-1,1:-1] in that order.
        expected = float(np.linalg.eigvalsh(A - np.diag(q[1:-1, 1:-1, 1:-1].ravel()))[0])
        lam, Phi = principal_eigenpair_3d(Nx, Ny, Nz, Lx, Ly, Lz, q)
        assert lam == pytest.approx(expected, abs=1e-10)
        assert Phi.shape == (Nz + 2, Ny + 2, Nx + 2)
        assert np.all(Phi[1:-1, 1:-1, 1:-1] > 0)
        # eigen-equation with the sparse operator and the same flattening
        Asp, hx, hy, hz = laplacian_3d_dirichlet(Nx, Ny, Nz, Lx, Ly, Lz)
        v = Phi[1:-1, 1:-1, 1:-1].reshape(-1)
        np.testing.assert_allclose(
            Asp @ v - q[1:-1, 1:-1, 1:-1].reshape(-1) * v, lam * v, atol=1e-9
        )

    def test_wrong_layout_is_rejected_by_shape(self):
        Nx, Ny, Nz = 2, 3, 4
        with pytest.raises(ValueError):
            principal_eigenvalue_3d(Nx, Ny, Nz, 1.0, 2.0, 3.0, np.zeros((Ny + 2, Nx + 2, Nz + 2)))
        with pytest.raises(ValueError):
            principal_eigenvalue_3d(Nx, Ny, Nz, 1.0, 2.0, 3.0, np.zeros((Nx, Ny, Nz)))

    def test_discrete_sign_can_differ_from_continuum_sign_near_threshold(self):
        """A negative discrete eigenvalue is numerical evidence, not a continuum certificate."""
        N, L = 18, 1.0
        h = L / (N + 1)
        discrete = 3 * (4 / h**2 * np.sin(np.pi * h / 2) ** 2)
        continuum = 3 * np.pi**2
        q_mid = (discrete + continuum) / 2
        assert principal_eigenvalue_3d(N, N, N, L, L, L, q_mid) < 0
        assert continuum - q_mid > 0

    def test_smallest_grid(self):
        A, hx, hy, hz = laplacian_3d_dirichlet(1, 1, 1, 1.0, 1.0, 1.0)
        assert A.shape == (1, 1)
        assert A.toarray()[0, 0] == pytest.approx(24.0)
