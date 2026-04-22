# Tests

Test suite validating the mathematical claims of the Creative Determinant framework.

## Running Tests

```bash
# Install dependencies (project uses uv, not pip)
uv sync --locked

# Run the full suite
uv run pytest tests/ -v

# Or a single file
uv run pytest tests/test_core.py -v

# With coverage (mirrors the `coverage` CI job)
uv run coverage run -m pytest tests/
uv run coverage report --show-missing
```

## Test Coverage — 24 tests across 5 files

| File | Tests | What They Validate |
|------|-------|--------------------|
| **test_core.py** | 12 | Eigenvalue formula, Picard convergence, residual bounds, bifurcation threshold (Theorems 3.12, 3.16), O(h²) grid convergence, edge cases |
| **test_spatial_solver.py** | 3 | Spatially-varying coefficients (1D): scalar/array equivalence, spatially-varying solves, residual parity |
| **test_fields.py** | 4 | 1D Gaussian bump constructor: peak location, amplitude, shape, range |
| **test_eigenvalues.py** | 3 | Spatial eigenvalue solver (1D and 2D): constant-field parity with scalar solver, monotone response to potential |
| **test_2d.py** | 2 | 2D solver with array coefficients; residual on converged 2D solution |

Verify the total count locally:

```bash
grep -R '^[[:space:]]*def test_' tests/ | wc -l
# expected: 24
```

The per-file counts are also visible via `grep -c "def test_" tests/test_*.py`.

## Test Philosophy

These tests validate **mathematical correctness**, not implementation details:

1. **Eigenvalue tests** verify the spectral theory (Definition 3.13, Theorem 3.16)
2. **Threshold tests** verify the bifurcation prediction
3. **Residual tests** verify numerical accuracy against the PDE
4. **Convergence tests** verify solver reliability
5. **Field tests** verify coefficient constructors

A failing test after a change to `src/cd/` means the math is wrong. Fix the solver/operator, not the test assertion. Any contribution that touches `src/cd/` must keep these tests green.

## Adding Tests

When extending the framework:

1. Identify the mathematical claim being made
2. Write a test that would fail if the claim is false
3. Prefer analytic validation (compare to a closed form) over regression (store a number)
4. Document what theorem/result the test validates in the docstring

Example:

```python
def test_2d_eigenvalue_formula(self):
    """Verify λ₁ = π²(1/Lx² + 1/Ly²) - βb for 2D rectangle (Theorem 3.12)."""
    # ... implementation
```

## Continuous Integration

The org ruleset requires these checks to pass on every PR to `main`:
`test`, `lint`, `typecheck`, `security`, `Analyze (python)`, `semgrep`, `quality-gate`.

The `test` check is an aggregator over the matrix job `test-run (3.10|3.11|3.12)` defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). The matrix installs dependencies via `uv sync --locked` and runs `uv run pytest tests/ -v`.
