# Creative Determinant (CD): A Field Theory of Coherence and Meaning

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/ci.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/ci.yml)
[![Notebook Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/notebooks.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/notebooks.yml)
[![Figure Validation](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/figures.yml/badge.svg)](https://github.com/Project-Navi/navi-creative-determinant/actions/workflows/figures.yml)
![Lean v4.34.1](https://img.shields.io/badge/Lean-v4.34.1-blue)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Coherent presence as the solution of a nonlinear elliptic boundary value problem on a semiotic manifold: a positive-existence theorem with a spectral viability threshold, a machine-checked finite-graph analogue, and a residual-validated numerical companion.

> Nelson Spence, *The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions*, Project Navi LLC, 2026. [PDF](paper/creative_determinant.pdf)

## What is proved

The model is the Dirichlet problem

```
−ΔΦ = a(x)|∇Φ| + b(x)Φ − c(x)Φ^p   in M,      Φ = 0 on ∂M
```

on a compact Riemannian manifold with boundary, with creative drive `a = κγμ ∈ [0,1]` (care × coherence × contradiction), viability potential `b = κγ − λμ`, saturation `c ≥ c₀ > 0` and `p > 1`.

| Result | Statement | Status |
|---|---|---|
| Existence | Theorem 3.12: a nonnegative weak coherent configuration exists; `Φ ≡ 0` is always one | classical proof; Lean, conditional on `PDEInfra` |
| Positive existence | Theorem 3.16: `λ₁(−Δ − b; M) < 0` gives a solution positive in the interior, enclosed between `εφ₁` and a constant | classical proof; Lean, conditional on `PDEInfra` |
| Exact threshold | Proposition 3.19: for `a ≡ 0` the spectral condition is also necessary | classical proof |
| Converse fails with drive | Proposition 3.21: `a = 1, b = 3/4, c = 1, p = 2` on `(0, π)` has a positive solution with `λ₁ = +1/4` | classical proof |
| Finite-graph theorem | Theorem 3.26, `SemioticGraph.exists_pos_graph`: a positive solution on a finite graph, with the explicit triangle example | proved outright, machine-checked |
| Strong ideal unattainable | Proposition 4.11: no nonzero `C¹` field of either sign satisfies the pointwise ideal with zero boundary data | classical proof |

Uniqueness of the positive solution and the exact threshold with a gradient term are open ([Open Problems](https://docs.projectnavi.ai/navi-creative-determinant/explanation/open-problems/)).

## Assumption boundary

Lean 4 against Mathlib v4.34.1; the submodule `cd_formalization/` is pinned at `ad65a64`. The finite-graph theorem is unconditional. The continuum theorems are conditional on the `PDEInfra` hypotheses, structure fields standing in for the classical elliptic results the paper cites and transfers to the manifold (Appendix B); the paper's operator does not instantiate that interface (Appendix A). Zero `sorry`. The axiom audit in `CdFormal/Verify.lean` requires every audited declaration to depend only on `propext`, `Classical.choice` and `Quot.sound`; hypotheses such as `PDEInfra` appear in the theorem signatures, not as axioms. Details: [cd_formalization/README.md](cd_formalization/README.md).

## Numerics

`src/cd` implements the continuum problem by centered finite differences (1D, 2D, 3D operators; residual-validated Picard iteration; discrete barriers), the Lean finite-graph model exactly (`cd.graph`), and the spectral tools. The finite-difference problem, the graph model and the 3D eigenvalue illustration are distinct models. A solver run counts as converged only when the returned field satisfies the discrete equation to a recorded tolerance. The notebook `notebooks/cd_pde_demo.ipynb` asserts every numerical claim it makes; the tests compare the numerics with analytic and exact discrete values.

## Building

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/); the paper and diagram builds require Docker, the Lean build [elan](https://github.com/leanprover/elan).

```bash
uv sync
uv run pytest tests/ -v
uv run jupyter lab notebooks/
uv run python figures/generate_figures.py
make -C paper                                   # stack diagram (Figures 1-2, docs), in a pinned image
paper/build_paper.sh                            # writes paper/build/creative_determinant.pdf
cd cd_formalization && lake build --wfail       # fails on any warning, including sorry
```

## Project structure

```
paper/                 creative_determinant.tex/.pdf, cd_refs.bib, cd_stack.dot (Figures 1-2 and the docs diagram), build_paper.sh
src/cd/                operators, solvers, eigenvalues, fields, graph, analysis
tests/                 package tests (ship in the sdist); tests/repo/ covers scripts, notebook and paper
notebooks/             cd_pde_demo.ipynb
figures/               generate_figures.py and its seven figures
scripts/               validate_notebook.py, check_paper_artifact.py, check_stack_citations.py
cd_formalization/      Lean 4 submodule (Project-Navi/cd-formalization)
docs/                  documentation site (zensical)
```

## Where to start

- [Documentation site](https://docs.projectnavi.ai/navi-creative-determinant/): entry ramps by background and the core concepts.
- [The CD Stack](https://docs.projectnavi.ai/navi-creative-determinant/explanation/cd-stack/): one diagram of the fields, the operator, the threshold and the temporal closure, with what is proved, defined, interpretive or deferred.
- [Conceptual Primer](https://docs.projectnavi.ai/navi-creative-determinant/explanation/conceptual-primer/) and [Author's Note](https://docs.projectnavi.ai/navi-creative-determinant/explanation/authors-note/).
- [Research Roadmap](https://docs.projectnavi.ai/navi-creative-determinant/reference/roadmap/), [Open Problems](https://docs.projectnavi.ai/navi-creative-determinant/explanation/open-problems/), [FAQ](https://docs.projectnavi.ai/navi-creative-determinant/reference/faq/).

## Citation

[CITATION.cff](CITATION.cff) holds the citation metadata; GitHub renders it as BibTeX or APA.

---

## Get Involved

> *The knowledge is free, the community is open. If you wish to support our mission, [buy a t-shirt](https://projectnavi.printful.me/).* 🐘

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for how to participate. See the **[Research Roadmap](https://docs.projectnavi.ai/navi-creative-determinant/reference/roadmap/)** for open research directions. See **[Open Problems](https://docs.projectnavi.ai/navi-creative-determinant/explanation/open-problems/)** for unresolved theoretical questions.

Please read our **[Code of Conduct](CODE_OF_CONDUCT.md)**—a trauma-informed, peer support-based community covenant that reflects how we work together.

This is a research seed, not a finished theory. The goal is for knowledge to flourish through collective engagement.

---

## Development Process

**What the author did**: the semiotic manifold formulation, the saturated model V1′, the proof strategy for existence and positive existence (the truncated Schaefer framework, ordered barriers and the maximum-principle comparison), the canonical closure, the temporal debt–resilience closure, the CD condition, and the connection between enactivist philosophy and PDE theory. Nelson Spence, April 2025 – March 2026. The classical elliptic theory is cited from Gilbarg–Trudinger and Evans.

**Other contributors**: Andrew Edmark (@aedmark) proposed the finite-graph formulation and its proof route (finite-dimensional inverse positivity and positive principal eigendata, then the order-theoretic fixed-point core). Yongxi (Aaron) Lin suggested the bornological form of `PDEInfra.T_compact` on the Lean Zulip.

**What AI tools did**: Claude Opus assisted with the Python numerics, the tests, the notebook and the documentation, and with Lean 4 syntax, Mathlib API navigation and proof term synthesis, including the finite-graph development. Aristotle (Harmonic) proved algebraic leaf lemmas by automated proof search.

---

## Contact

Nelson Spence
Project Navi LLC
nelson@projectnavi.ai
Austin, Texas

I've carried this as far as I could alone. African wisdom provides our community principle, "If you want to go fast, go alone. If you want to go far, go together." Let's go far.

## License and Ethical Use

Copyright 2026 Nelson Spence. Licensed under **[Apache 2.0](LICENSE)**: use, modification and redistribution, including commercial use, with the copyright notices and the LICENSE file preserved.

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
