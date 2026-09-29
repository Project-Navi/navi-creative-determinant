# Creative Determinant (CD): A Field Theory of Coherence and Meaning

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/ci.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/ci.yml)
[![Notebook Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/notebooks.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/notebooks.yml)
[![Figure Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/figures.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/figures.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](notebooks/cd_pde_demo.ipynb)

Creative Determinant (CD) is a framework for how coherent presence emerges and sustains itself in cognitive and computational systems, developed across three domains: nonlinear elliptic PDEs on Riemannian manifolds (existence theorems, spectral viability thresholds and residual-validated numerics), enactivist and semiotic foundations (care, coherence, contradiction and autopoiesis), and empirical testability (the CD condition, a measurable correlation between coherence observables and phase-space volume dynamics, with explicit falsifiability criteria).

---

## Quick Start

**Requirements:** Python 3.10+, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/Project-Navi/navi-creative-determinant.git
cd navi-creative-determinant
uv sync
uv run pytest tests/ -v
uv run jupyter lab notebooks/
```

See the [Quickstart](https://docs.projectnavi.ai/navi-creative-determinant/getting-started/quickstart/) for details.

---

## What's in This Repository

- **[`creative_determinant.pdf`](paper/creative_determinant.pdf)**: The core paper, presenting the mathematical framework, interpretive layer, and operational proposals.
- **[`cd_formalization/`](cd_formalization/)**: Lean 4 formalization against Mathlib (v4.34.1, pinned at revision `ad65a64`). Definitions (semiotic manifold model, operators, BVP, weak coherent configuration), the algebraic and order-theoretic lemmas, and the finite-graph positive-existence theorem with its explicit example are machine-checked. The continuum existence theorems (3.12, 3.16) are proved conditionally on the `PDEInfra` hypotheses — structure fields standing in for classical elliptic results not yet in Mathlib, which the paper's concrete operator does not instantiate (paper Appendix A). See the [formalization README](cd_formalization/README.md) for build instructions and the assumption boundary.
- **[`cd_pde_demo.ipynb`](notebooks/cd_pde_demo.ipynb)**: Jupyter notebook with residual-validated numerical demonstrations of viability thresholds, equilibrium emergence and canonical closure in 1D and 2D, the verified finite-graph example, and a 3D eigenvalue illustration. Every numerical claim in it is asserted.
- **[Research Roadmap](https://docs.projectnavi.ai/navi-creative-determinant/reference/roadmap/)**: Research directions and open questions—invitations for others to contribute.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to participate, extend, or challenge the framework.
- **[Open Problems](https://docs.projectnavi.ai/navi-creative-determinant/explanation/open-problems/)**: Explicit gaps and unresolved theoretical questions.
- **Experiments**: The proposed empirical instantiations (toy dynamical systems, small neural networks, behavioural tests) are items 2, 6 and 7 of the [Research Roadmap](https://docs.projectnavi.ai/navi-creative-determinant/reference/roadmap/).
- **[FAQ](https://docs.projectnavi.ai/navi-creative-determinant/reference/faq/)**: Short answers to common questions.
- **[Conceptual Primer](https://docs.projectnavi.ai/navi-creative-determinant/explanation/conceptual-primer/)**: A gentle introduction for non-technical audiences.
- **[Author's Note](https://docs.projectnavi.ai/navi-creative-determinant/explanation/authors-note/)**: Origin story and motivation behind the framework.
- **[figures/](figures/)**: Publication-quality visualizations of framework dynamics.

## Where to Start

Entry ramps by background (PDE and analysis, AI and interpretability, Lean, cognitive science and philosophy) and a 30-second summary of the core concepts live on the [documentation landing page](https://docs.projectnavi.ai/navi-creative-determinant/). The key mathematical qualification is the viability threshold: when the principal eigenvalue $λ_1(-Δ - b; M) < 0$, a coherent configuration positive throughout the interior exists (Theorem 3.16); the condition is exact when the creative drive vanishes (Proposition 3.19) and sufficient only in general (Proposition 3.21 gives a positive solution with $λ_1 = +1/4$ when the drive is active).

---

## Citation

If you build on this work, please cite:

> Nelson Spence. *The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions.* Project Navi LLC, 2026.

---

## Get Involved

> *The knowledge is free, the community is open. If you wish to support our mission, [buy a t-shirt](https://projectnavi.printful.me/).* 🐘

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for how to participate. See the **[Research Roadmap](https://docs.projectnavi.ai/navi-creative-determinant/reference/roadmap/)** for open research directions. See **[Open Problems](https://docs.projectnavi.ai/navi-creative-determinant/explanation/open-problems/)** for unresolved theoretical questions.

Please read our **[Code of Conduct](CODE_OF_CONDUCT.md)**—a trauma-informed, peer support-based community covenant that reflects how we work together.

This is a research seed, not a finished theory. The goal is for knowledge to flourish through collective engagement.

---

## Provenance

The theory, the equations, the proof strategy, the canonical closure, the CD condition and the connection between enactivist philosophy and PDE theory are Nelson Spence's original research, developed over 12 months (April 2025 – March 2026). Claude Opus assisted with implementation: the Python numerics, the tests, the notebook, the documentation and the Lean 4 formalization (Mathlib API navigation, proof term synthesis, project scaffolding). Aristotle (Harmonic.fun) automated the proving of algebraic lemmas in Lean.

The results are independently verifiable. `lake build --wfail` type-checks the Lean development with zero `sorry`; the continuum theorems are conditional on the `PDEInfra` interface, whose fields are hypotheses rather than axioms (the `SolutionOperator` structure also carries assumptions), while the finite-graph theorem is unconditional. The numerical claims are tested against analytic and exact discrete solutions, O(h²) convergence, independent `solve_bvp` cross-checks and the verified finite-graph example. See [`cd_formalization/README.md`](cd_formalization/README.md) for the assumption boundary and the [Actions page](https://github.com/Project-Navi/navi-creative-determinant/actions) for the checks that run on every push.

---

## Contact

Nelson Spence
Project Navi LLC
nelson@projectnavi.ai
Austin, Texas

I've carried this as far as I could alone. African wisdom provides our community principle, "If you want to go fast, go alone. If you want to go far, go together." Let's go far.

## License and Ethical Use

The Creative Determinant framework is licensed under **[Apache 2.0](LICENSE)** to maximize accessibility for research, education, and innovation.

### Why Apache 2.0?

We want this framework to be freely usable by:
- Academic researchers exploring cognitive science, AI interpretability, or formal theories of meaning
- AI safety organizations testing new approaches to coherence and alignment
- Independent researchers and students learning at the intersection of math, philosophy, and computation

Apache 2.0 allows you to use, modify, and build upon this work—even commercially—with minimal restrictions. You must preserve copyright notices and include the LICENSE file, but you are not required to release your modifications or derivatives.

### Ethical Covenant (Voluntary)

While the license grants you broad rights, we invite you to honor the **[Ethical Covenant](https://docs.projectnavi.ai/navi-creative-determinant/explanation/ethical-covenant/)**. This invitation is voluntary. It cannot be enforced legally. Its power comes from community norms and scholarly integrity.

### Commercial Services

For organizations seeking:
- Support and co-development (help instantiating CD on your systems)
- Ethical assurance agreements (formal commitments to responsible use)
- IP indemnity or custom extensions

Contact: nelson@projectnavi.ai

Such agreements are available under our standard PNEUL-D dual-license structure but are **not required** to use this framework.

---

The goal is simple: let knowledge flourish through collective engagement, not extraction.
