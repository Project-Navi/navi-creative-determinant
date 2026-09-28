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

## Test Coverage — 140 tests across 12 files

| File | Tests | What They Validate |
|------|-------|--------------------|
| **test_core.py** | 12 | Eigenvalue formula, Picard convergence, residual bounds, bifurcation threshold (Theorems 3.12, 3.16), O(h²) grid convergence, edge cases |
| **test_spectra.py** | 14 | Operator sign and boundary rows, exact discrete eigenvalue formula (1D, anisotropic 2D, one-point grids), second-order continuum limit, scale-aware errors at λ₁ = 0 |
| **test_solver_diagnostics.py** | 27 | Meaning of numerical success: tiny damping is not convergence, input validation, termination reasons (max_iter / nonfinite / stagnation), clipping is not nonexistence evidence, smallest and anisotropic grids, fail-closed diagnostics, 2D coefficient shapes |
| **test_barriers.py** | 9 | Discrete ordered barriers εφ₁ and plateau M (a = 0), monotone shifted iteration from below and above, exact discrete threshold for a = 0 (Proposition 3.19), unresolved near-threshold runs |
| **test_independent_checks.py** | 6 | Manufactured residual at second order, independent solve_bvp comparison (a = 0 and a = 0.5) including a zero-start control, mesh refinement, algebraic vs discretization error |
| **test_graph.py** | 37 | Finite-graph lane (Lean model): verified triangle crosswalk, Jacobi residual identity, proof constants, monotone iteration from both barriers, diagonal-weight and permutation invariances, edge condition at both ends, disconnected interiors, converse counterexample (Proposition 3.30), graph bound counterexample (Proposition 3.28), graph vs centered gradient |
| **test_analysis_statistics.py** | 14 | Spatial statistics: interior mean including zeros, tensor trapezoid quadrature (area measure), nonuniform grids, explicit coordinates, rejections |
| **test_spatial_solver.py** | 3 | Spatially-varying coefficients (1D): scalar/array equivalence, spatially-varying solves, residual parity |
| **test_eigenvalues.py** | 3 | Spatial eigenvalue solver (1D and 2D): constant-field parity with scalar solver, monotone response to potential |
| **test_2d.py** | 2 | 2D solver with array coefficients; residual on converged 2D solution |
| **test_fields.py** | 4 | 1D Gaussian bump constructor: peak location, amplitude, shape, range |
| **test_validate_notebook.py** | 9 | The notebook validator fails closed on error outputs, unexecuted cells, missing markers, failed or too few checks (negative fixtures); the committed notebook passes |

Verify the total count locally:

```bash
grep -R '^[[:space:]]*def test_' tests/ | wc -l
# expected: 140
```

The per-file counts are also visible via `grep -c "def test_" tests/test_*.py`.

## Test Philosophy

These tests validate **mathematical correctness**, not implementation details:

1. **Eigenvalue tests** verify the spectral theory: the exact discrete formula, the continuum limit, the threshold (Definition 3.13, Theorem 3.16)
2. **Threshold and barrier tests** verify branch classification against the exact discrete criterion for a = 0 (Proposition 3.19) and the monotone iteration between ordered barriers
3. **Residual tests** verify that a run is accepted only when the discrete equation holds; a small update is never enough
4. **Independent checks** compare the finite-difference solver with a collocation solver and a manufactured residual
5. **Graph tests** reproduce the Lean finite-graph model exactly, including its verified example and two counterexamples
6. **Field and statistics tests** verify coefficient constructors and the quadrature measure

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
`lint`, `typecheck`, `security`, `codeql`, `semgrep`, `quality-gate`.

The `test` aggregator job (over the matrix `test-run (3.10|3.11|3.12)` defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) runs on every PR but is not in the ruleset's required list. The matrix installs dependencies via `uv sync --locked` and runs `uv run pytest tests/ -v`.
