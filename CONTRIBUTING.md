# Contributing to Creative Determinant

Thank you for your interest in contributing to the Creative Determinant (CD) framework! This document describes how to participate, what kinds of contributions are welcome, and minimal standards.

---

## Types of Contributions We Actively Want

### 1. Theoretical Extensions
- New theorems, lemmas, or proofs extending the PDE core.
- Alternative coefficient structures, closures, or boundary conditions.
- Bifurcation analysis, multiplicity results, or regularity improvements.

**Standard**: State assumptions clearly. Label results as **Theorem**, **Conjecture**, or **Heuristic**. Cite sources. Be honest about proof gaps.

---

### 2. Numerical and Computational Work
- Improved solvers for the V1 PDE or extensions.
- Parameter sweeps, stability analyses, convergence studies.
- Visualizations, animations, or interactive demos.

**Standard**: Include docstrings and at least one minimal working example. Note numerical tolerances and grid dependencies.

---

### 3. Empirical Tests
- CD condition measurements on real dynamical systems, neural networks, or cognitive data.
- Falsification experiments targeting Definition 5.3 criteria.
- Manifold extraction from model activations or behavioral data.

**Standard**: Describe data sources, metrics, and preprocessing clearly. Note limitations. Null results and failures are valuable—document them honestly.

---

### 4. Conceptual Clarifications
- Expository writing, diagrams, or tutorials explaining CD to new audiences.
- Connections to other frameworks (predictive processing, free energy principle, category theory, etc.).
- Philosophical or interpretive refinements.

**Standard**: Clearly mark what is interpretation vs. what follows from theorems. Cite related work.

---

### 5. Critical Contributions
- Arguments that some aspect of the framework is incomplete, inconsistent, or falsified.
- Identification of serious gaps or overreach.
- Counterexamples or boundary cases where CD predictions fail.

**Standard**: Be specific and constructive. Point to exact claims, definitions, or theorems. Suggest how the framework might be revised or clarified.

**Tag issues as `falsifiability` or `critical`.**

---

## How to Contribute

### Small contributions (typos, small clarifications, minor code fixes):
- Open a pull request directly. Include a one-line description in the PR.

### Medium contributions (new examples, extended numerics, expository docs):
- Open an issue tagged `proposal` describing what you plan to do, or just open a PR with a short summary.

### Large contributions (new theoretical results, major empirical tests, significant extensions):
- Open an issue tagged `proposal` first to discuss scope and avoid duplication.
- Then open a PR when ready.

### Collaborations:
- If you want to work with others on a roadmap item, tag your issue `collaboration-wanted`.

---

## Contribution Standards

All contributions should meet these minimal criteria:

1. **Honesty about status**: Mark clearly what is proved, what is conjectured, what is empirical observation, what is interpretation.

2. **Reproducibility**: For code, include dependencies and a minimal example. For empirical work, describe data and methods enough that someone else could replicate.

3. **Clarity**: Write for someone not already familiar with your subfield. Define non-standard terms.

4. **Civility**: Engage respectfully, even (especially) when disagreeing.

---

## What Happens After You Contribute?

- Small PRs will be merged quickly if they meet standards.
- Larger contributions will be discussed in the PR or associated issue.
- You retain authorship credit for your contributions. We'll maintain a `CONTRIBUTORS.md` file listing everyone who has contributed.

---

## Licensing

By contributing, you agree that your contributions will be licensed under the same license as this repository (Apache 2.0).

If you are contributing substantial original content (e.g., a new theorem, a major empirical study), you may also publish it separately under your own name—no permission needed. We encourage parallel publication.

---

## Related Documents

- **[OPEN_PROBLEMS.md](docs/OPEN_PROBLEMS.md)**: Explicit theoretical gaps where contributions are needed
- **[ROADMAP.md](docs/ROADMAP.md)**: Research directions and proposed experiments
- **[The Paper](paper/spence_creative_determinant_2026.pdf)**: Full theoretical treatment
- **[Jupyter Notebook](notebooks/cd_pde_demo.ipynb)**: Numerical demonstrations to extend

---

## Questions?

Open an issue tagged `question` or contact:

Nelson Spence  
nelson@projectnavi.ai

---

**The CD framework is a research seed meant to grow through collective engagement. Your contributions—whether extensions, tests, or critiques—are what will make it flourish.**
