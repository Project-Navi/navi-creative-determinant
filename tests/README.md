# Tests

Test suite validating the mathematical claims of the Creative Determinant framework.

## Running Tests

```bash
# Install dependencies
pip install pytest numpy scipy

# Run all tests
pytest tests/test_core.py -v

# Or run directly
python tests/test_core.py
```

## Test Coverage

| Category | Tests | What They Validate |
|----------|-------|-------------------|
| **Eigenvalue** | 2 | Numeric λ₁ matches analytic (π/L)² - βb; sign flips at threshold |
| **Convergence** | 2 | Picard iteration converges above and below threshold |
| **Residual** | 1 | Converged solution satisfies PDE (||R||∞ < 10⁻⁴) |
| **Threshold** | 3 | Trivial below, nontrivial above, sharp bifurcation |
| **Grid Refinement** | 2 | O(h²) solution convergence; maxΦ stabilizes |
| **Edge Cases** | 2 | Negative viability → trivial; larger L → easier threshold |

**Total: 12 tests**

## Test Philosophy

These tests validate **mathematical correctness**, not implementation details:

1. **Eigenvalue tests** verify the spectral theory (Theorem 3.12)
2. **Threshold tests** verify the bifurcation prediction
3. **Residual tests** verify numerical accuracy
4. **Convergence tests** verify solver reliability

Any contribution that touches `src/cd/` should pass these tests.

## Adding Tests

When extending the framework:

1. Identify the mathematical claim being made
2. Write a test that would fail if the claim is false
3. Prefer analytic validation over regression testing
4. Document what theorem/result the test validates

Example:
```python
def test_2d_eigenvalue_formula(self):
    """Verify λ₁ = π²(1/Lx² + 1/Ly²) - βb for 2D rectangle."""
    # ... implementation
```

## Continuous Integration

When CI is configured, these tests should run on every PR:

```yaml
# .github/workflows/test.yml
- run: pip install pytest numpy scipy
- run: pytest tests/ -v
```
