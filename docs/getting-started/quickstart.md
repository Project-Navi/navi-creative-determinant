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

The suite checks the exact discrete eigenvalues, residual-validated nonlinear solves, threshold crossings, convergence rates and the finite-graph model; `tests/repo/` checks the notebook, the scripts and the paper build. [`tests/README.md`](https://github.com/Project-Navi/navi-creative-determinant/blob/main/tests/README.md) lists every file.

---

## Open the notebook

```bash
uv run jupyter lab notebooks/
```

The notebook `cd_pde_demo.ipynb` demonstrates the framework numerically in 1D and 2D, reproduces the verified finite-graph example, ends with a 3D eigenvalue illustration, and asserts every numerical claim it makes.

---

## Repository structure

```
paper/                     # The core paper (creative_determinant.pdf)
notebooks/                 # Jupyter notebook with numerical demonstrations
src/cd/                    # Python library (solvers, eigenvalue tools, closures)
tests/                     # pytest suite (package tests; tests/repo/ covers scripts, notebook and paper)
cd_formalization/          # Lean 4 formalization (finite-graph theorem proved; continuum theorems conditional)
figures/                   # Figure script and its seven figures
```

---

## What's next

- **[Conceptual Primer](../explanation/conceptual-primer.md)** --- gentle introduction without math
- **[Open Problems](../explanation/open-problems.md)** --- where contributions are needed
- **[Research Roadmap](../reference/roadmap.md)** --- open research directions
