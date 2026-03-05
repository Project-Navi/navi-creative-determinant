# Notebooks

Numerical demonstrations of the Creative Determinant PDE framework.

## Contents

**cd_pde_demo.ipynb** — Complete numerical validation of the mathematical claims, with references to the Lean4 formal proofs.

## Running the Notebook

```bash
# From the repository root:
uv sync                           # install dependencies + cd package
uv run jupyter lab notebooks/     # launch Jupyter
```

The notebook imports from `src/cd/` — make sure you've run `uv sync` first.

Or run all cells from command line:

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/cd_pde_demo.ipynb
```

## What the Notebook Demonstrates

| Part | Topic | Paper Reference | Lean4 Proof |
|------|-------|-----------------|-------------|
| 1 | Eigenvalue threshold | Theorem 3.16 | `spectral_characterization_1d` |
| 2 | 1D nonlinear solve + rigor checks | Theorems 3.12, 3.16 | `existence_weak_coherent_configuration`, `existence_nontrivial_coherent_configuration` |
| 3 | Canonical closure sweep | Definition 3.3 | `SemioticContext.canonicalViability` |
| 4 | 2D presence field | Theorems 3.12, 3.16 | Same existence theorems |
| 5 | 3D eigenvalue demo | Spectral theory | Extends to arbitrary dimension |

## Relationship to Paper and Lean4 Proofs

The notebook provides computational evidence for the core claims in the paper. Each part includes interpretive markdown linking the numerical result to the corresponding paper theorem and Lean4 formal proof.

- **Numerical code**: imported from `src/cd/` (operators, solvers, eigenvalues, fields, analysis)
- **Lean4 proofs**: in `cd_formalization/CdFormal/` (Theorems.lean, Basic.lean, Axioms.lean)
- **Paper**: `paper/creative_determinant.pdf`

## Extending the Notebook

To add new experiments:

1. Create a new section at the end
2. Import functions from `cd` rather than reimplementing
3. Include validation (residuals, convergence checks)
4. Reference the relevant paper theorem and Lean4 proof
5. Open a PR with your additions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
