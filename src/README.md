# Source Code

Reusable Python library for the Creative Determinant framework.

## Installation

This project uses **uv**. From the repository root:

```bash
uv sync --locked   # creates venv, installs the `cd` package (editable) + dev deps
```

`--locked` installs exactly the versions pinned in `uv.lock`.

## Structure

```
src/cd/
├── __init__.py       # Public API exports (`__all__`)
├── operators.py      # Laplacian constructors (1D, 2D, 3D) and the 3D grid
├── solvers.py        # Picard iteration solvers and discrete barriers
├── eigenvalues.py    # Principal eigenvalues, eigenpairs and viability thresholds
├── fields.py         # Field constructors (viability, creative drive, Gaussian bumps)
├── graph.py          # Finite-graph model of the Lean development
├── _validation.py    # Input validation shared by the numerical modules
└── analysis.py       # Residuals, convergence checks, branch classification, statistics
```

## Quick Start

```python
import numpy as np
from cd import (
    solve_1d_picard,
    principal_eigenvalue_1d,
    viability_threshold_1d,
)

# Domain and parameters
L = 1.0
N = 400
b = 0.8  # Constant viability potential

# Compute threshold
beta_star = viability_threshold_1d(L, b)
print(f"Viability threshold: β* = {beta_star:.2f}")

# Solve below threshold → trivial
x, Phi_below, info = solve_1d_picard(L, N, a=0.0, beta_b=0.8*beta_star*b, c=10.0)
print(f"Below threshold: maxΦ = {info['maxPhi']:.2e}")

# Solve above threshold → nontrivial
x, Phi_above, info = solve_1d_picard(L, N, a=0.0, beta_b=1.2*beta_star*b, c=10.0)
print(f"Above threshold: maxΦ = {info['maxPhi']:.4f}")
```

## API Reference

Every name exported from `cd` (the `__all__` list in `src/cd/__init__.py`), grouped by module.

### Operators (`operators.py`)

- `laplacian_1d_dirichlet(N, L)` → `(A, h)`: sparse matrix for -d²/dx² on (0, L) with Dirichlet boundary, and the grid spacing
- `laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)` → `(A, hx, hy)`: sparse matrix for -Δ on a rectangle, and the spacings
- `laplacian_3d_dirichlet(Nx, Ny, Nz, Lx, Ly, Lz)` → `(A, hx, hy, hz)`: sparse matrix for -Δ on a box, unknowns in the (z, y, x) layout
- `grid_3d(Nx, Ny, Nz, Lx, Ly, Lz)` → `(Z, Y, X)`: coordinate arrays including boundary points, in the (z, y, x) layout

### Eigenvalues (`eigenvalues.py`)

- `principal_eigenvalue_1d(N, L, beta_b)` → λ₁(-Δ - βb) on (0, L)
- `principal_eigenvalue_1d_spatial(N, L, beta_b_field)` → λ₁ with a spatially varying potential on (0, L)
- `principal_eigenvalue_2d(Nx, Ny, Lx, Ly, beta_b)` → λ₁ on a rectangle
- `principal_eigenvalue_2d_spatial(Nx, Ny, Lx, Ly, beta_b_field)` → λ₁ with a spatially varying potential on a rectangle
- `principal_eigenpair_1d(N, L, beta_b)` → `(λ₁, φ₁)` with a positive unit eigenvector, on (0, L)
- `principal_eigenpair_2d(Nx, Ny, Lx, Ly, beta_b)` → `(λ₁, φ₁)` on a rectangle
- `principal_eigenpair_3d(Nx, Ny, Nz, Lx, Ly, Lz, beta_b)` → `(λ₁, φ₁)` on a box
- `principal_eigenvalue_3d(Nx, Ny, Nz, Lx, Ly, Lz, beta_b)` → λ₁ on a box
- `viability_threshold_1d(L, b)` → critical gain β* = (π/L)²/b
- `viability_threshold_2d(Lx, Ly, b)` → critical gain β* for a rectangle

### Solvers (`solvers.py`)

- `solve_1d_picard(L, N, a, beta_b, c, p=2.0, ...)` → `(x, Φ, info)`: damped, residual-validated Picard iteration in 1D
- `solve_2d_picard(Lx, Ly, Nx, Ny, a, beta_b, c, p=2.0, ...)` → `(X, Y, Φ, info)`: the same on a rectangle
- `barriers_1d(N, L, beta_b, c, p=2.0)` → dict of ordered discrete barriers (εφ₁ and the plateau) for a ≡ 0

### Finite-graph model (`graph.py`)

- `SemioticGraph(w, boundary, a, b, c, p)`: a finite weighted graph with a Dirichlet boundary and the CD coefficients
- `triangle()` → the verified Lean example `SemioticGraph.triangle`
- `solve_graph(G, start="subsolution", ...)` → `(u, info)`: shifted Jacobi iteration validated through its residual
- `linfty_bound_graph(G)` → upper bound for nonnegative solutions on the graph

### Analysis (`analysis.py`)

- `residual_1d(x, Φ, a, beta_b, c, p)` → discrete residual on the interior nodes
- `residual_2d(Φ, a_full, beta_b_full, c_full, p, hx, hy)` → discrete 2D residual on the interior nodes
- `check_convergence(info)` → `(ok, message)`: fail-closed check that re-validates the recorded numbers (see below)
- `solution_type(info)` → `'trivial'` | `'nontrivial'` | `'unresolved'` | `'invalid'`: amplitude label of a solver result
- `classify_branch(Φ, info)` → `'zero'` | `'positive'` | `'nonnegative'` | `'unresolved'` | `'invalid'`: the sign-checked classification used by the notebook
- `presence_statistics(Φ, x=None, y=None)` → dict of interior statistics with an explicit quadrature measure
- `trapezoid_weights(x)` → composite trapezoid weights on an increasing grid
- `linfty_bound(beta_b, c, p)` → theoretical L∞ bound for nonnegative solutions of the continuum equation

`check_convergence` does not trust `info["converged"]`; it re-validates the residual criterion `residual_inf <= residual_atol + residual_rtol * residual_scale` (with a finite limit), the update criterion `inf_err < tol` (strict; a solved start with `iters == 0` must record `inf_err == 0.0`), `boundary_err <= residual_atol`, and the types, finiteness and signs of every diagnostic (`iters` an integral nonnegative count, `converged` a bool). A report missing any required key, including `tol`, is reported as unvalidated, never accepted.

### Fields (`fields.py`)

- `viability_canonical(kappa, gamma, mu, lam)` → b(x) = κγ - λμ
- `creative_drive(kappa, gamma, mu)` → a(x) = κγμ
- `gaussian_bump_1d(x, center, sigma, amplitude=1.0)` → 1D Gaussian field
- `gaussian_bump_2d(X, Y, x0, y0, sigma, amplitude=1.0)` → 2D Gaussian field

## Design Principles

1. **Tested against exact solutions**: the operators and solvers are checked against closed-form and exact discrete solutions in `tests/test_spectra.py`, `tests/test_barriers.py`, `tests/test_independent_checks.py` and `tests/test_continuum_counterexample.py`.

2. **Minimal dependencies**: NumPy, SciPy only. Matplotlib for visualization.

3. **Dimension-agnostic interface**: Same patterns for the 1D, 2D and 3D operators; the nonlinear solvers cover 1D and 2D.

4. **Sparse linear algebra**: All operators are SciPy sparse matrices.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. Key points:

1. Add tests for any new functionality
2. Validate against analytic solutions where possible
3. Use type hints and docstrings (NumPy style)
4. Keep dependencies minimal
