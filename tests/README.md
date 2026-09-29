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

## Test Coverage — 229 test functions across 18 files (parametrized cases expand to more collected tests)

Two populations: **183 package tests in 14 files directly under `tests/`** (shipped in the sdist and runnable against the installed `cd` package alone) and **46 repository-artefact tests in 4 files under `tests/repo/`** (need `scripts/`, `notebooks/` and `paper/`; excluded from the sdist). `uv run pytest tests/` collects both.

Shared fixtures live in `tests/conftest.py` (factory fixtures for the three-vertex Lean graphs, the closed-form discrete 1D eigenvalue, and one real converged solver report) and `tests/repo/conftest.py` (the repository root, a fresh loader for the scripts under `scripts/`, and a synthetic-notebook writer).

| File | Tests | What They Validate |
|------|-------|--------------------|
| **test_core.py** | 12 | Eigenvalue formula, Picard convergence (accepted through `check_convergence`, not the update size), residual bounds, bifurcation threshold (Theorems 3.12, 3.16), O(h²) grid convergence, edge cases |
| **test_spectra.py** | 14 | Operator sign and boundary rows, exact discrete eigenvalue formula (1D, anisotropic 2D, one-point grids), second-order continuum limit, scale-aware errors at λ₁ = 0 |
| **test_solver_diagnostics.py** | 35 | Meaning of numerical success: tiny damping is not convergence, input validation (including a string `initial_guess` in 2D and non-numeric `residual_2d` spacings), termination reasons (max_iter / nonfinite / stagnation), clipping is not nonexistence evidence, smallest and anisotropic grids, fail-closed diagnostics, 2D coefficient shapes; convergence report contract: solved starts (iters = 0, zero update, recorded `tol`) accepted, corrupted or incomplete reports (bad `iters`, negative norms, infinite residual limit, update not below `tol`, missing `tol`) rejected naming the reason |
| **test_barriers.py** | 9 | Discrete ordered barriers εφ₁ and plateau M (a = 0), monotone shifted iteration from below and above, exact discrete threshold for a = 0 (Proposition 3.19), unresolved near-threshold runs |
| **test_independent_checks.py** | 6 | Manufactured residual at second order, independent solve_bvp comparison (a = 0 and a = 0.5) including a zero-start control, mesh refinement, algebraic vs discretization error |
| **test_graph.py** | 38 | Finite-graph lane (Lean model): verified triangle crosswalk, Jacobi residual identity, proof constants, monotone iteration from both barriers, tolerance validation, diagonal-weight and permutation invariances, edge condition at both ends, disconnected interiors, converse counterexample (Proposition 3.32), graph bound counterexample (Proposition 3.30), graph vs centered gradient |
| **test_analysis_statistics.py** | 20 | Spatial statistics: interior mean including zeros, tensor trapezoid quadrature (area measure), nonuniform grids, explicit coordinates, the zero-branch cutoff of the support fraction, rejections; input domain of the L∞ bound (Lemma 3.10) |
| **test_spatial_solver.py** | 3 | Spatially-varying coefficients (1D): scalar/array equivalence, spatially-varying solves, residual parity |
| **test_eigenvalues.py** | 3 | Spatial eigenvalue solver: 1D constant-field parity with the scalar solver, monotone response to the potential, 2D constant field against the analytic formula λ₁ = π²(1/Lx² + 1/Ly²) - βb |
| **test_2d.py** | 2 | 2D solver with array coefficients; residual on converged 2D solution |
| **test_fields.py** | 12 | 1D Gaussian bump constructor: peak location, amplitude, shape, range; input domains of the canonical closure, creative drive and Gaussian bumps (unit-interval intensities, λ ≥ 0, positive width, finite fields; strings, bools and NaN rejected) |
| **test_review_regressions.py** | 18 | Regressions from the mathematical review: spectral assembly is independent of self weights and verified against the direct operator and Rayleigh quotient, exact edge condition without slack, indeterminate status near λ₁ = 0, zero-step accepted roots with defined diagnostics, negative initial data rejected, sign-checked branch labels, a convergence checker that re-validates its own numbers |
| **test_operators_3d.py** | 5 | 3D Dirichlet Laplacian and eigenvalues with an explicit (z, y, x) convention: constant-potential closed form on an anisotropic box, an asymmetric potential against an independent dense assembly, wrong layouts rejected by shape, discrete-vs-continuum sign near threshold |
| **test_continuum_counterexample.py** | 6 | Positive continuum solution below the linear threshold (Proposition 3.21): analytic barrier identities, library solve enclosed between the barriers with λ₁ = +1/4, independent collocation agreement |
| **repo/test_paper_gate.py** | 10 | The paper artifact gate: byte identity between the committed PDF and its pinned-image rebuild; the diagnostics locate a changed sign, reversed inequality operands, swapped numerator/denominator, moved minus, changed digit, moved decimal point, changed multiplication glyph, altered exponent and dropped sentence (order-preserving text comparison) and a changed pixel (page renders) |
| **repo/test_validate_notebook_required.py** | 7 | The notebook validator requires each essential claim exactly once and the completion marker after the last check (negative fixtures: missing, duplicated, misplaced marker); the committed notebook satisfies it, and the required list is complete, duplicate-free and in notebook order |
| **repo/test_validate_notebook.py** | 8 | The notebook validator fails closed on error outputs, unexecuted cells, missing markers, failed or too few checks (negative fixtures), and its CLI exit codes |
| **repo/test_stack_diagram.py** | 21 | The stack diagram has one source: both rendered SVGs carry the SHA-256 of `paper/cd_stack.dot`, the figure PDFs exist, the source parses into its five clusters with well-formed edges, the figure subsets keep only internal edges, Figure 2 draws the path from the fields and the closure back to the eigenvalue, Theorem 3.26 has no edge from the continuum model, and both its docs and print labels state all three hypotheses (connected interior graph, λ₁ᴳ < 0, the edge condition at both ends of every interior edge of positive weight) and the conclusion u(x) > 0; `scripts/check_stack_citations.py` rejects a renumbered or retitled statement header (a title shortened or lengthened past its entry included), a renumbered section, an unmapped citation and a number that occurs only in figure text, expands plural citations, every statement entry of the diagram source runs through the character that closes its title, and every citation in the diagram and on the CD Stack page is mapped |

Verify the total count locally:

```bash
grep -R '^[[:space:]]*def test_' tests/ --include='test_*.py' | wc -l
# expected: 229 (183 in tests/*.py, 46 in tests/repo/*.py); the --include keeps the example below out of the count
```

The per-file counts are also visible via `grep -c "def test_" tests/test_*.py`.

## Test Philosophy

These tests validate **mathematical correctness**, not implementation details:

1. **Eigenvalue tests** verify the spectral theory: the exact discrete formula, the continuum limit, the threshold (Definition 3.13, Theorem 3.16)
2. **Threshold and barrier tests** verify branch classification against the exact discrete criterion for a = 0 (Proposition 3.19) and the monotone iteration between ordered barriers
3. **Residual tests** verify that a run is accepted only when the discrete equation holds; a small update is never enough
4. **Independent checks** compare the finite-difference solver with a collocation solver and a manufactured residual
5. **Graph tests** reproduce the Lean finite-graph model exactly, including its verified example and two counterexamples, with the spectral assembly checked against the operator evaluated from pair differences
6. **Field and statistics tests** verify coefficient constructors and the quadrature measure

A failing test after a change to `src/cd/` usually means the math is wrong. Fix the solver/operator, not the test assertion.

## Adding Tests

When extending the framework:

1. Identify the mathematical claim being made
2. Write a test that would fail if the claim is false
3. Prefer analytic validation (compare to a closed form) over regression (store a number)
4. Document what theorem/result the test validates in the docstring

Example:

```python
def test_2d_eigenvalue_formula(self):
    """Verify λ₁ = π²(1/Lx² + 1/Ly²) - βb for 2D rectangle (Definition 3.13)."""
    # ... implementation
```

## Continuous Integration

CI runs `uv run pytest tests/ -v` after `uv sync --locked` on Python 3.10, 3.11 and 3.12 (the `test-run` matrix in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).
