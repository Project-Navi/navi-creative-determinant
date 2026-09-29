---
hide:
  - navigation
  - toc
---

# navi-creative-determinant

**Autopoietic closure as a nonlinear elliptic BVP on a compact Riemannian manifold.**

A field theory of coherence and meaning, with a machine-checked finite-graph existence theorem and conditionally formalized continuum theorems (Lean 4, Mathlib v4.34.1).

[Get Started](getting-started/quickstart.md){ .md-button .md-button--primary }
[Conceptual Primer](explanation/conceptual-primer.md){ .md-button }

---

## Core concepts

| Concept | Symbol | Role |
|---------|--------|------|
| Semiotic manifold | \(M\) | Space of possible meanings or interpretations |
| Presence field | \(\Phi(x)\) | Intensity of coherent presence at each point on \(M\) |
| Care | \(\kappa\) | Energetic investment sustaining the system |
| Coherence | \(\gamma\) | Structural integrity holding the system together |
| Contradiction | \(\mu\) | Generative tension driving exploration |
| Creative drive | \(a(x) = \kappa\gamma\mu\) | Gradient activity where all three fields jointly support |
| Viability potential | \(b(x) = \kappa\gamma - \lambda\mu\) | Where care-coherence support dominates contradiction cost |
| Viability threshold | \(\lambda_1(-\Delta - b;\, M) < 0\) | A positive coherent configuration exists (Theorem 3.16); exact when \(a \equiv 0\) (Proposition 3.19) |
| CD condition | --- | Coherence observables correlate with Jacobian volume dynamics |

---

## Entry ramps by background

**PDE / analysis** --- Start with Sections 2--3 of the paper (existence and positive-existence theorems) and the eigenvalue verification in the notebook (Part 1). Treat Sections 4--5 as motivation and proposed applications.

**AI / interpretability** --- Start with Section 5 (the CD condition and falsifiability criteria) and skim the notebook plots showing the zero and positive branches on either side of the viability threshold (the solver classifies equilibria; it does not establish a bifurcation type, Remark 3.24). Then read Section 3 for the spectral foundation.

**Lean / formal verification** --- Start with the [`cd_formalization`](https://github.com/Project-Navi/navi-creative-determinant/tree/main/cd_formalization) directory for the assumption boundary and what is proved. `CdFormal/Graph/Existence.lean` holds the unconditional finite-graph theorem (`exists_pos_graph`); `CdFormal/Theorems.lean` holds the continuum theorems, which are conditional on the `PDEInfra` hypotheses.

**Cognitive science / philosophy** --- Start with Sections 1 and 4 (introduction and interpretive layer), which connect the framework to enactivism, semiotics, and phenomenology. Then see Theorem 3.16 (positive existence) to see how "viability exceeds dissipation" is made mathematically precise.

---

## Documentation

| Section | Contents |
|---------|----------|
| [Quickstart](getting-started/quickstart.md) | Install, run tests, open the notebook |
| [Conceptual Primer](explanation/conceptual-primer.md) | Gentle introduction without math |
| [Author's Note](explanation/authors-note.md) | Origin story and motivation |
| [Open Problems](explanation/open-problems.md) | Eleven explicit theoretical gaps |
| [Ethical Covenant](explanation/ethical-covenant.md) | Voluntary ethical commitments |
| [Contributing](how-to/contributing.md) | How to participate, extend, or challenge |
| [FAQ](reference/faq.md) | Quick answers to common questions |
| [Research Roadmap](reference/roadmap.md) | Ten open research directions |
| [Changelog](reference/changelog.md) | Release history |
