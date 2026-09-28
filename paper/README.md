# Paper

The core theoretical paper for the Creative Determinant framework.

## Contents

**creative_determinant.pdf** — *The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions*

## Structure

| Section | Contents | Audience |
|---------|----------|----------|
| §1 | Introduction and motivation | Everyone |
| §2 | Mathematical preliminaries, definitions | PDE/analysis |
| §3 | Existence framework, positive existence, exact threshold for \(a \equiv 0\), finite-graph model (machine-checked) | PDE/analysis |
| §4 | Interpretive layer: care, coherence, contradiction | Cognitive science, philosophy |
| §5 | CD condition, falsifiability criteria | AI safety, empirical researchers |
| §6 | Limitations and open problems | Everyone |
| App. A | Formal verification: what is proved, what is conditional, paper-to-Lean alignment | Lean / formal verification |

## Building

```bash
latexmk -pdf -cd paper/creative_determinant.tex   # PDF with bibliography (pdflatex + bibtex passes)
make -C paper                                     # cd_stack diagrams only
```

CI (`.github/workflows/paper.yml`) rebuilds the PDF from source and checks that the committed PDF's text matches it.

## Citation

```bibtex
@techreport{spence2026creative,
  author = {Spence, Nelson},
  title = {The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with Lean 4-Verified Existence Conditions},
  institution = {Project Navi LLC},
  year = {2026},
  month = {January},
  address = {Austin, Texas}
}
```

## Key Results

- **Theorem 3.12** (Existence framework): a compact fixed-point formulation with a priori bounds for nonnegative weak coherent configurations; the zero field is always one
- **Theorem 3.16** (Positive existence): when viability exceeds dissipation (λ₁ < 0), a solution positive throughout the interior exists, enclosed between εφ₁ and a constant
- **Proposition 3.19** (Exact threshold): for a ≡ 0 the condition λ₁ < 0 is also necessary; with a gradient term it is sufficient only
- **Theorem 3.24** (Finite graph, machine-checked): the analogous positive-existence theorem on finite weighted graphs, with an explicit example, a maximum bound (Proposition 3.28) and a counterexample to the converse (Proposition 3.30)
- **Definition 5.1** (CD Condition): Measurable correlation between coherence and Jacobian dynamics
- **Definition 5.3** (Falsifiability): Five explicit criteria for empirical refutation
