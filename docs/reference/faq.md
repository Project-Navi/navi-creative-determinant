# Frequently Asked Questions

Short answers to common questions about the Creative Determinant (CD) framework.

---

## Is this supposed to be a full theory of mind?

**No.** CD is a framework for certain aspects of coherence, viability, and meaning-making in cognitive and computational systems. It has explicit limitations (see Section 6 of the paper and [Open Problems](../explanation/open-problems.md)). It is not intended as a complete theory of consciousness, phenomenology, or intelligence.

---

## Does the PDE "explain" semiotics or enactivism?

**Not directly.** The PDE is a mathematically tractable *proxy* motivated by semiotic and enactivist ideas (care, coherence, contradiction, autopoiesis). The relationship between the PDE model (weak coherence) and the pointwise CD constraint (strong coherence) is an open problem. See [Open Problems](../explanation/open-problems.md) #1.

---

## Can I use this framework without accepting the philosophical interpretation?

**Yes.** The PDE structure, existence/nontriviality theorems, and spectral results stand on their own as nonlinear analysis. You can treat the interpretive layer (Section 4) as motivation only and work purely within the mathematical framework.

---

## Is the CD condition testable on real systems?

**Yes, in principle.** Definition 5.1 specifies measurable quantities: a coherence observable and Jacobian determinants. The challenge is operationalizing these on high-dimensional systems (e.g., neural networks). See the [Research Roadmap](roadmap.md) for proposed tests.

---

## What is the "semiotic manifold" \(M\) in a real neural network?

**Open question.** \(M\) is an abstract space of meanings or interpretations. Extracting it from a trained network requires manifold learning, dimensionality reduction, or other techniques. This is an active research direction. See [Open Problems](../explanation/open-problems.md) #7 and [Research Roadmap](roadmap.md) #1.

---

## How do I extract the fields \(\kappa\), \(\gamma\), \(\mu\) from data?

**No general method yet.** The canonical closure \(b = \kappa\gamma - \lambda\mu\) provides a structure, but inferring \(\kappa\) (care), \(\gamma\) (coherence), and \(\mu\) (contradiction) from observables is system-dependent and currently requires hand-crafted proxies. Developing principled extraction methods is a key open problem.

---

## Is there existing code I can run?

**Yes.** The Jupyter notebook [`cd_pde_demo.ipynb`](https://github.com/Project-Navi/navi-creative-determinant/blob/main/notebooks/cd_pde_demo.ipynb) demonstrates the PDE framework numerically in 1D, 2D, and 3D. It includes eigenvalue verification, nonlinear solves, viability threshold crossings, and canonical closure sweeps. You can run it locally with Python, NumPy, SciPy, and Matplotlib.

---

## Can I propose changes to the core framework?

**Yes.** Open an issue tagged `proposal` or `critical` describing your proposed change or challenge. Constructive critiques and falsification attempts are first-class contributions. See [Contributing](../how-to/contributing.md).

---

## What license is this under?

Apache 2.0. See [LICENSE.md](https://github.com/Project-Navi/navi-creative-determinant/blob/main/LICENSE.md) for full terms.

All contributions are licensed under the same terms. If you contribute substantial original work, you may also publish it separately under your own name without asking permission.

---

## Who is this for?

CD is intended for:
- **Researchers** in PDE theory, dynamical systems, AI interpretability, cognitive science, or philosophy of mind looking for cross-disciplinary synthesis.
- **Practitioners** wanting to operationalize "coherence" or "viability" in computational systems.
- **Students** seeking a worked example of how to bridge rigorous mathematics and conceptual interpretation.

---

## How do I cite this work?

> Nelson Spence. *The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions.* Project Navi LLC, 2026.

```bibtex
@techreport{spence2026creative,
  author = {Spence, Nelson},
  title = {The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions},
  institution = {Project Navi LLC},
  year = {2026},
  address = {Austin, Texas}
}
```

---

## I have a question not answered here.

Open an issue tagged `question` or contact:

Nelson Spence
nelson@projectnavi.ai

---

**These are starting answers. As the community engages with the framework, this FAQ will evolve.**
