# Creative Determinant (CD): A Field Theory of Coherence and Meaning

**Creative Determinant (CD)** is a framework for understanding how coherent presence emerges and sustains itself in cognitive and computational systems. It bridges three traditionally separate domains:

- **Mathematical rigor**: Nonlinear elliptic PDEs on Riemannian manifolds, with existence theorems, spectral viability thresholds, and numerical validation.
- **Philosophical depth**: Enactivist and semiotic foundations connecting care, coherence, contradiction, and autopoiesis.
- **Empirical testability**: The CD condition—a measurable correlation between coherence observables and phase-space volume dynamics—with explicit falsifiability criteria.

The goal is a cognitive theory that is **not three separate things, but one integrated whole**.

---

## What's in This Repository

- **[`spence_creative_determinant_2026.pdf`](spence_creative_determinant_2026.pdf)**: The core paper, presenting the mathematical framework, interpretive layer, and operational proposals.
- **[`cd_pde_demo.ipynb`](cd_pde_demo.ipynb)**: Jupyter notebook with numerical demonstrations of viability thresholds, equilibrium emergence, and canonical closure in 1D, 2D, and 3D.
- **[ROADMAP.md](ROADMAP.md)**: Research directions and open questions—invitations for others to contribute.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to participate, extend, or challenge the framework.
- **[OPEN_PROBLEMS.md](OPEN_PROBLEMS.md)**: Explicit gaps and unresolved theoretical questions.
- **[experiments/](experiments/)**: Scaffolding for empirical instantiations and tests.
- **[FAQ.md](FAQ.md)**: Short answers to common questions.

---

## Entry Ramps by Background

### If you're a **PDE / analysis person**:
Start with **Sections 2–3** of the paper (existence and nontriviality theorems) and the **eigenvalue verification** in the notebook (Part 1). Treat Sections 4–5 as motivation and proposed applications.

### If you're an **AI / interpretability researcher**:
Start with **Section 5** (the CD condition and falsifiability criteria) and skim the notebook plots showing bifurcations at viability thresholds. Then read Section 3 to see the spectral foundation.

### If you're a **cognitive scientist / philosopher**:
Start with **Sections 1 and 4** (introduction and interpretive layer), which connect the framework to enactivism, semiotics, and phenomenology. Then glance at **Theorem 3.12** (nontriviality) to see how "viability exceeds dissipation" is made mathematically precise.

---

## Core Concepts (30-Second Version)

- **Semiotic manifold** \(M\): a space of possible meanings or interpretations.
- **Presence field** \(\Phi(x)\): intensity of coherent "presence" at each point on \(M\).
- **Characteristic fields**: care \(\kappa\), coherence \(\gamma\), contradiction \(\mu\)—dimensionless fields in \([0,1]\).
- **Creative drive** \(a(x) = \kappa\gamma\mu\): gradient activity contributes to presence where all three fields jointly support it.
- **Viability potential** \(b(x) = \kappa\gamma - \lambda\mu\): where care-coherence support dominates contradiction cost.
- **Viability threshold**: when the principal eigenvalue \(\lambda_1(-\Delta - b; M) < 0\), nontrivial coherent configurations exist.
- **CD condition**: coherence observables correlate with Jacobian volume dynamics in structured regimes.

The paper establishes **17 citations** grounding this framework in PDE theory (Gilbarg-Trudinger, Evans, Schaefer, Leray-Schauder), dynamical systems (Oseledets, Lyapunov, Pesin), and conceptual foundations (Maturana-Varela, Friston, Thompson, Prigogine).

---

## Citation

If you build on this work, please cite:

> Nelson Spence. *On the Existence and Stability of Recursive Semiotic Fields: A Formalization of the Creative Determinant.* Project Navi LLC, January 2026.

---

## Get Involved

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for how to participate. See **[ROADMAP.md](ROADMAP.md)** for open research directions. See **[OPEN_PROBLEMS.md](OPEN_PROBLEMS.md)** for unresolved theoretical questions.

**This is a research seed, not a finished theory.** The goal is for knowledge to flourish through collective engagement.

---

## Contact

Nelson Spence  
Project Navi LLC  
nelson@projectnavi.ai  
Austin, Texas

## License and Ethical Use

The Creative Determinant framework is licensed under **[Apache 2.0](LICENSE)** to maximize accessibility for research, education, and innovation.

### Why Apache 2.0?

We want this framework to be freely usable by:
- Academic researchers exploring cognitive science, AI interpretability, or formal theories of meaning
- AI safety organizations testing new approaches to coherence and alignment
- Independent researchers and students learning at the intersection of math, philosophy, and computation

Apache 2.0 allows you to use, modify, and build upon this work—even commercially—with minimal restrictions. You must preserve copyright notices and include the LICENSE file, but you are not required to release your modifications or derivatives.

### Ethical Covenant (Voluntary)

While the license grants you broad rights, we invite you to honor the **[Ethical Covenant](ETHICAL_COVENANT.md)**—a voluntary commitment to:
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
