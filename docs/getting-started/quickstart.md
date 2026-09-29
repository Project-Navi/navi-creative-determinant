# Quickstart

Install the Creative Determinant framework and run the numerical demonstrations.

---

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (package manager)

---

## Clone and install

```bash
git clone https://github.com/Project-Navi/navi-creative-determinant.git
cd navi-creative-determinant

# Install all dependencies (creates venv, installs package + deps)
uv sync
```

---

## Run the tests

```bash
uv run pytest tests/ -v
```

191 test functions (167 package tests, 24 repository-artefact tests under `tests/repo/`) validate the exact discrete eigenvalues, residual-validated nonlinear solves, viability threshold crossings, convergence rates, the finite-graph model of the Lean development, and the notebook validator.

---

## Open the notebook

```bash
uv run jupyter lab notebooks/
```

The Jupyter notebook `cd_pde_demo.ipynb` demonstrates the PDE framework numerically in 1D and 2D (viability thresholds, equilibrium emergence, canonical closure), reproduces the verified finite-graph example, and ends with a 3D eigenvalue illustration. Each numerical claim is asserted in the notebook itself.

---

## Repository structure

```
paper/                     # The core paper (creative_determinant.pdf)
notebooks/                 # Jupyter notebook with numerical demonstrations
src/cd/                    # Python library (solvers, eigenvalue tools, closures)
tests/                     # 167 package test functions (+ 24 in tests/repo/ for scripts, notebook and paper)
cd_formalization/          # Lean 4 formalization (finite-graph theorem proved; continuum theorems conditional)
figures/                   # Publication-quality visualizations
```

---

## What's next

- **[Conceptual Primer](../explanation/conceptual-primer.md)** --- gentle introduction without math
- **[Open Problems](../explanation/open-problems.md)** --- where contributions are needed
- **[Research Roadmap](../reference/roadmap.md)** --- open research directions
