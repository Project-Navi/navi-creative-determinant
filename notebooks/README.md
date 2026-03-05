# Notebooks

Numerical demonstrations of the Creative Determinant PDE framework.

## Contents

**cd_pde_demo.ipynb** — Complete numerical validation of the mathematical claims

## Requirements

```bash
pip install numpy scipy matplotlib jupyter
```

Python 3.10+ recommended.

## Running the Notebook

```bash
cd notebooks
jupyter notebook cd_pde_demo.ipynb
```

Or run all cells from command line:

```bash
jupyter nbconvert --to notebook --execute cd_pde_demo.ipynb
```

## What the Notebook Demonstrates

| Part | Topic | Key Output |
|------|-------|------------|
| 1 | Eigenvalue verification | Numeric λ₁ matches analytic formula |
| 2 | 1D equilibrium solving | Picard iteration converges, residuals small |
| 3 | Threshold crossing | Below → trivial, above → nontrivial |
| 4 | Canonical closure sweep | Presence collapses as contradiction cost increases |
| 5 | 2D presence fields | Spatial heterogeneity, localized presence |
| 6 | Grid refinement | O(h²) convergence proof |
| 7 | Phase transition | Side-by-side viable vs collapsed states |

## Relationship to Paper

The notebook provides computational evidence for claims in Sections 2–3 of the paper. Specifically:

- **Theorem 3.12** (existence) and **Theorem 3.16** (nontriviality) are verified numerically in Parts 1–3
- **Canonical closure** (§3.4) is explored in Part 4
- **Spatial structure** (§4) is visualized in Parts 5, 7

## Extending the Notebook

To add new experiments:

1. Create a new section at the end
2. Document what you're testing and why
3. Include validation (residuals, convergence checks)
4. Open a PR with your additions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
