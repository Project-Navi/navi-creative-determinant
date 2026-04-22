# Source Code

Reusable Python library for the Creative Determinant framework.

## Installation

This project uses **uv**. From the repository root:

```bash
uv sync --locked   # creates venv, installs the `cd` package (editable) + dev deps
```

CI pins everything through `uv.lock`; contributors should do the same. `requirements.txt` is kept only for users who cannot run `uv` — it is not the source of truth.

## Structure

```
src/cd/
├── __init__.py       # Public API exports
├── operators.py      # Laplacian constructors (1D, 2D)
├── solvers.py        # Picard iteration solvers
├── eigenvalues.py    # Principal eigenvalue computation
├── fields.py         # Field constructors (viability, creative drive)
└── analysis.py       # Residual computation, convergence checks
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

### Operators

- `laplacian_1d_dirichlet(N, L)` → Sparse matrix for -d²/dx²
- `laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)` → Sparse matrix for -Δ

### Eigenvalues

- `principal_eigenvalue_1d(N, L, beta_b)` → λ₁(-Δ - βb)
- `principal_eigenvalue_2d(Nx, Ny, Lx, Ly, beta_b)` → λ₁ for rectangle
- `viability_threshold_1d(L, b)` → Critical β*
- `viability_threshold_2d(Lx, Ly, b)` → Critical β* for rectangle

### Solvers

- `solve_1d_picard(L, N, a, beta_b, c, ...)` → (x, Φ, info)
- `solve_2d_picard(Lx, Ly, Nx, Ny, a, beta_b, c, ...)` → (X, Y, Φ, info)

### Fields

- `viability_canonical(κ, γ, μ, λ)` → b(x) = κγ - λμ
- `creative_drive(κ, γ, μ)` → a(x) = κγμ
- `gaussian_bump_2d(X, Y, x0, y0, σ)` → Gaussian field

### Analysis

- `residual_1d(x, Φ, a, beta_b, c, p)` → PDE residual
- `check_convergence(info)` → (ok, message)
- `solution_type(info)` → 'trivial' or 'nontrivial'

## Design Principles

1. **Tested against analytic solutions**: Every solver is validated against known exact solutions in `tests/test_core.py`.

2. **Minimal dependencies**: NumPy, SciPy only. Matplotlib for visualization.

3. **Dimension-agnostic interface**: Same patterns for 1D and 2D (3D coming).

4. **Sparse linear algebra**: All operators use SciPy sparse matrices for efficiency.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. Key points:

1. Add tests for any new functionality
2. Validate against analytic solutions where possible
3. Use type hints and docstrings (NumPy style)
4. Keep dependencies minimal
