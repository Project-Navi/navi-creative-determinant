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

24 tests validate eigenvalue verification, nonlinear solves, viability threshold crossings, convergence rates, and canonical closure sweeps.

---

## Open the notebook

```bash
uv run jupyter lab notebooks/
```

The Jupyter notebook `cd_pde_demo.ipynb` demonstrates the PDE framework numerically in 1D, 2D, and 3D --- viability thresholds, equilibrium emergence, and canonical closure.

---

## Repository structure

```
paper/                     # The core paper (creative_determinant.pdf)
notebooks/                 # Jupyter notebook with numerical demonstrations
src/cd/                    # Python library (solvers, eigenvalue tools, closures)
tests/                     # 24 tests against analytic solutions
cd_formalization/          # Lean 4 formalization (15 theorems, zero sorry)
experiments/               # Scaffolding for empirical tests
figures/                   # Publication-quality visualizations
```

---

## What's next

- **[Conceptual Primer](../explanation/conceptual-primer.md)** --- gentle introduction without math
- **[Open Problems](../explanation/open-problems.md)** --- where contributions are needed
- **[Research Roadmap](../reference/roadmap.md)** --- open research directions
