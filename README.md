# Creative Determinant (CD): A Field Theory of Coherence and Meaning

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.md)
[![Mathematical Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/ci.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/ci.yml)
[![Code Quality](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/quality.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/quality.yml)
[![Notebook Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/notebooks.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/notebooks.yml)
[![Figure Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/figures.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/figures.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](notebooks/cd_pde_demo.ipynb)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18225664.svg)](https://doi.org/10.5281/zenodo.18225664)

**Creative Determinant (CD)** is a framework for understanding how coherent presence emerges and sustains itself in cognitive and computational systems. It bridges three traditionally separate domains:

- **Mathematical rigor**: Nonlinear elliptic PDEs on Riemannian manifolds, with existence theorems, spectral viability thresholds, and numerical validation.
- **Philosophical depth**: Enactivist and semiotic foundations connecting care, coherence, contradiction, and autopoiesis.
- **Empirical testability**: The CD condition—a measurable correlation between coherence observables and phase-space volume dynamics—with explicit falsifiability criteria.

The goal is a cognitive theory that is **not three separate things, but one integrated whole**.

---

## Table of Contents

- [Quick Start](#quick-start)
- [What's in This Repository](#whats-in-this-repository)
- [Entry Ramps by Background](#entry-ramps-by-background)
- [Core Concepts](#core-concepts-30-second-version)
- [Citation](#citation)
- [Get Involved](#get-involved)
- [License and Ethical Use](#license-and-ethical-use)
- [Contact](#contact)

---

## Quick Start

**Requirements:** Python 3.10+, [uv](https://docs.astral.sh/uv/)

```bash
# Clone the repository
git clone https://github.com/Project-Navi/navi-creative-determinant.git
cd navi-creative-determinant

# Install all dependencies (creates venv, installs package + deps)
uv sync

# Run the tests
uv run pytest tests/ -v

# Open the notebook
uv run jupyter lab notebooks/
```

---

## What's in This Repository

- **[`creative_determinant.pdf`](paper/creative_determinant.pdf)**: The core paper, presenting the mathematical framework, interpretive layer, and operational proposals.
- **[`cd_formalization/`](cd_formalization/)**: Lean 4 formalization of the Creative Determinant framework against Mathlib. Definitions (semiotic manifold, operators, BVP, weak coherent configuration) are machine-checked. Existence (Theorem 3.12) and nontriviality (Theorem 3.16) are proved conditional on PdeInfra — an explicit axiom surface packaging classical PDE results not yet in Mathlib. See the [formalization README](cd_formalization/README.md) for build instructions and axiom boundary details.
- **[`cd_pde_demo.ipynb`](notebooks/cd_pde_demo.ipynb)**: Jupyter notebook with numerical demonstrations of viability thresholds, equilibrium emergence, and canonical closure in 1D, 2D, and 3D.
- **[Research Roadmap](https://project-navi.github.io/navi-creative-determinant/reference/roadmap/)**: Research directions and open questions—invitations for others to contribute.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to participate, extend, or challenge the framework.
- **[Open Problems](https://project-navi.github.io/navi-creative-determinant/explanation/open-problems/)**: Explicit gaps and unresolved theoretical questions.
- **[experiments/](experiments/)**: Scaffolding for empirical instantiations and tests.
- **[FAQ](https://project-navi.github.io/navi-creative-determinant/reference/faq/)**: Short answers to common questions.
- **[Conceptual Primer](https://project-navi.github.io/navi-creative-determinant/explanation/conceptual-primer/)**: A gentle introduction for non-technical audiences.
- **[Author's Note](https://project-navi.github.io/navi-creative-determinant/explanation/authors-note/)**: Origin story and motivation behind the framework.
- **[figures/](figures/)**: Publication-quality visualizations of framework dynamics.

## Entry Ramps by Background

### If you're a **PDE / analysis person**:
Start with **Sections 2–3** of the paper (existence and nontriviality theorems) and the **eigenvalue verification** in the notebook (Part 1). Treat Sections 4–5 as motivation and proposed applications.

### If you're an **AI / interpretability researcher**:
Start with **Section 5** (the CD condition and falsifiability criteria) and skim the notebook plots showing bifurcations at viability thresholds. Then read Section 3 to see the spectral foundation.

### If you're a **Lean / formal verification person**:
Start with **[`cd_formalization/README.md`](cd_formalization/README.md)** for the axiom boundary and what's proved. Then read `CdFormal/Theorems.lean` for the existence proofs and `CdFormal/Verify.lean` for the axiom audit.

### If you're a **cognitive scientist / philosopher**:
Start with **Sections 1 and 4** (introduction and interpretive layer), which connect the framework to enactivism, semiotics, and phenomenology. Then glance at **Theorem 3.16** (nontriviality) to see how "viability exceeds dissipation" is made mathematically precise.

---

## Core Concepts (30-Second Version)

- **Semiotic manifold** $M$: a space of possible meanings or interpretations.
- **Presence field** $Φ(x)$: intensity of coherent "presence" at each point on $M$.
- **Characteristic fields**: care $κ$, coherence $γ$, contradiction $μ$ — dimensionless fields in $[0,1]$.
- **Creative drive** $a(x) = κγμ$: gradient activity contributes to presence where all three fields jointly support it.
- **Viability potential** $b(x) = κγ - λμ$: where care-coherence support dominates contradiction cost.
- **Viability threshold**: when the principal eigenvalue $λ_1(-Δ - b; M) < 0$, nontrivial coherent configurations exist (Theorem 3.16).
- **CD condition**: coherence observables correlate with Jacobian volume dynamics in structured regimes.

The paper is grounded in PDE theory (Gilbarg–Trudinger, Evans, Schaefer, Leray–Schauder), dynamical systems (Oseledets, Lyapunov, Pesin), and conceptual foundations (Maturana–Varela, Friston, Thompson, Prigogine).

---

## Citation

If you build on this work, please cite:

> Nelson Spence. *The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions.* Project Navi LLC, 2026.

---

## Get Involved

> *The knowledge is free, the community is open. If you wish to support our mission, [buy a t-shirt](https://projectnavi.printful.me/).* 🐘

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for how to participate. See the **[Research Roadmap](https://project-navi.github.io/navi-creative-determinant/reference/roadmap/)** for open research directions. See **[Open Problems](https://project-navi.github.io/navi-creative-determinant/explanation/open-problems/)** for unresolved theoretical questions.

Please read our **[Code of Conduct](CODE_OF_CONDUCT.md)**—a trauma-informed, peer support-based community covenant that reflects how we work together.

**This is a research seed, not a finished theory.** The goal is for knowledge to flourish through collective engagement.

---

## Development Process

**What the author did**: The original equations, mathematical framework, and theory —
semiotic manifold formulation, the nonlinear elliptic BVP (V1'), existence/nontriviality
proof strategy, canonical closure, the CD condition, and the connection between
enactivist philosophy and PDE theory — are original research by Nelson Spence,
developed over 12 months (April 2025 – March 2026).

**What AI tools did**: Claude Opus assisted with implementation — Python numerics,
test infrastructure, notebook pedagogy, documentation, and Lean 4 formalization
(Mathlib API navigation, proof term synthesis, project scaffolding). Aristotle
(Harmonic.fun) automated proving of algebraic lemmas in Lean.

**Why this isn't slop**: The intellectual contribution (theory, equations, proof
strategy) is human-originated. AI helped transcribe those ideas into Python and
Lean 4. The results are independently verifiable:
- **Lean proofs**: `lake build --wfail` — type-checks or it doesn't. Zero `sorry`.
- **Numerical code**: 24 tests against analytic solutions, O(h²) convergence, `solve_bvp` cross-checks.
- **Axiom surface**: Every assumption is explicit in `PdeInfra` — nothing is hidden.

The math doesn't care who typed it. Clone the repo and verify.

---

## Contact

Nelson Spence
Project Navi LLC
nelson@projectnavi.ai
Austin, Texas

**I've carried this as far as I could alone. African wisdom provides our community principle, "If you want to go fast, go alone. If you want to go far, go together." Let's go far.**

## License and Ethical Use

The Creative Determinant framework is licensed under **[Apache 2.0](LICENSE.md)** to maximize accessibility for research, education, and innovation.

### Why Apache 2.0?

We want this framework to be freely usable by:
- Academic researchers exploring cognitive science, AI interpretability, or formal theories of meaning
- AI safety organizations testing new approaches to coherence and alignment
- Independent researchers and students learning at the intersection of math, philosophy, and computation

Apache 2.0 allows you to use, modify, and build upon this work—even commercially—with minimal restrictions. You must preserve copyright notices and include the LICENSE file, but you are not required to release your modifications or derivatives.

### Ethical Covenant (Voluntary)

While the license grants you broad rights, we invite you to honor the **[Ethical Covenant](https://project-navi.github.io/navi-creative-determinant/explanation/ethical-covenant/)**—a voluntary commitment to:
- Use CD responsibly in systems that affect people
- Be intellectually honest about what CD does and doesn't prove
- Contribute back to the research community where feasible
- Consider humanitarian alignment if your work generates commercial value

**This invitation is voluntary.** It cannot be enforced legally. Its power comes from community norms and scholarly integrity.

### Commercial Services

For organizations seeking:
- Support and co-development (help instantiating CD on your systems)
- Ethical assurance agreements (formal commitments to responsible use)
- IP indemnity or custom extensions

Contact: nelson@projectnavi.ai

Such agreements are available under our standard PNEUL-D dual-license structure but are **not required** to use this framework.

---

**The goal is simple: let knowledge flourish through collective engagement, not extraction.**
