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

Every numerical claim is asserted in the notebook through a `check(condition, name)` helper that prints `CHECK PASSED: name`; the notebook ends with `ALL_NOTEBOOK_CHECKS_PASSED`, and `scripts/validate_notebook.py` (run by CI) rejects any error, unexecuted cell, or missing check.

| § | Topic | Paper reference | Formal status |
|---|-------|-----------------|---------------|
| 1 | Spectral theory — exact discrete eigenvalue, continuum limit, threshold | Definition 3.13, Section 3.5 | `viabilityThreshold_lt_iff` proved (arithmetic; eigenvalue identification classical) |
| 2 | $L^\infty$ bound (exact for the discrete model when $a=0$) | Lemma 3.10 | `linfty_bound_algebraic` proved (algebraic step) |
| 3 | Existence and branches — residual-validated solves, ordered barriers, monotone iteration, refinement, `solve_bvp` cross-check | Theorems 3.12, 3.16, Proposition 3.19 | continuum theorems conditional on `PDEInfra`; classical proofs in the paper |
| 4 | Scaling uniqueness (proportional solutions excluded) | Remark 3.22 | `scaling_uniqueness` proved |
| 5 | Canonical closure sweep ($a > 0$: sufficient condition only) | Definition 3.3, Remark 3.20 | `SemioticContext.canonicalViability` definition |
| 6 | 2D presence field: a positive equilibrium and a collapsed one | Theorem 3.16 | as in §3 |
| 7 | Finite graph: verified triangle, Jacobi iteration from both barriers, converse and bound counterexamples | Section 3.6 | `SemioticGraph.exists_pos_graph`, `triangle_isSolution` proved |
| 8 | 3D eigenvalue illustration (linear, unformalized) | Spectral theory | extension |

## Relationship to Paper and Lean4 Proofs

The notebook provides computational evidence for the core claims in the paper. Each part includes interpretive markdown linking the numerical result to the corresponding paper theorem and Lean4 formal proof.

- **Numerical code**: imported from `src/cd/` (operators, solvers, eigenvalues, fields, analysis, graph); the only inline code is the `solve_bvp` cross-check and the 3D operators
- **Lean4 proofs**: in `cd_formalization/CdFormal/` (Theorems.lean, Basic.lean, Axioms.lean, Graph/*.lean)
- **Paper**: `paper/creative_determinant.pdf`

## Extending the Notebook

To add new experiments:

1. Create a new section at the end
2. Import functions from `cd` rather than reimplementing
3. Assert every numerical claim with `check(condition, name)`; CI rejects unasserted or failed claims
4. Reference the relevant paper theorem and, where one exists, the Lean declaration; label conditional results as such
5. Open a PR with your additions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
