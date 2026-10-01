# Paper

The core theoretical paper for the Creative Determinant framework.

## Contents

**creative_determinant.pdf** — *The Creative Determinant: Autopoietic Closure as a Nonlinear Elliptic Boundary Value Problem with a Lean 4 Formalization*

## Structure

| Section | Contents | Audience |
|---------|----------|----------|
| §1 | Introduction and motivation | Everyone |
| §2 | Mathematical preliminaries, definitions | PDE/analysis |
| §3 | Existence framework, positive existence, exact threshold for \(a \equiv 0\), finite-graph model (machine-checked) | PDE/analysis |
| §4 | Interpretive layer: care, coherence, contradiction | Cognitive science, philosophy |
| §5 | CD condition, falsifiability criteria | AI safety, empirical researchers |
| §6 | Discussion and limitations | Everyone |
| App. A | Formal verification: what is proved, what is conditional, paper-to-Lean alignment | Lean / formal verification |
| App. B | Transfer of the cited Euclidean results to the manifold | PDE/analysis |

## Building

`paper/build_paper.sh` builds the committed PDF: it runs `latexmk` inside a pinned TeX Live
image (`texlive/texlive:TL2025-historic`, by digest) with a fixed `SOURCE_DATE_EPOCH`.

```bash
paper/build_paper.sh                              # needs docker; writes paper/build/creative_determinant.pdf
cp paper/build/creative_determinant.pdf paper/    # commit the rebuilt PDF together with the source change
python3 scripts/check_paper_artifact.py paper/creative_determinant.pdf paper/build/creative_determinant.pdf
make -C paper                                     # stack diagram: cd_stack.dot -> docs SVG and the two figure PDFs, in a pinned image (needs docker)
make -C paper check                               # render into a temporary directory and require the committed outputs to be identical
latexmk -pdf -cd paper/creative_determinant.tex   # quick local preview with your own TeX Live (not the committed artifact)
```

`make -C paper` renders `cd_stack.dot` through `stack_figures.py` into the paper's stack figures
and the documentation-site SVG, in the image of `figures.Dockerfile` (Graphviz, cairo and fonts
pinned: base image by digest, packages from a fixed Debian snapshot, fonts by SHA-256), and copies
the four outputs into place; rebuild the paper after regenerating them. A change to the source,
the renderer or the Dockerfile changes the outputs.

CI (`paper.yml`) re-renders the four diagram outputs in that image and fails unless the committed
copies are byte-identical (`build_figures.sh check`); it then builds the paper from the
re-rendered figures and fails unless the committed PDF is byte-identical to that build
(`scripts/check_paper_artifact.py`) and every statement the diagram cites has a matching header
in it (`scripts/check_stack_citations.py`). On a PDF mismatch it prints a text diff and a
page-by-page render comparison.

## Citation

Cite the paper with the metadata in [`CITATION.cff`](../CITATION.cff) at the repository root; its `preferred-citation` entry is the report record, and GitHub renders it as BibTeX or APA.

## Key Results

- **Theorem 3.12** (Existence framework): a compact fixed-point formulation with a priori bounds for nonnegative weak coherent configurations; the zero field is always one
- **Theorem 3.16** (Positive existence): when viability exceeds dissipation (λ₁ < 0), a solution positive throughout the interior exists, enclosed between εφ₁ and a constant
- **Proposition 3.19** (Exact threshold): for a ≡ 0 the condition λ₁ < 0 is also necessary; with a gradient term it is sufficient only
- **Proposition 3.21** (Converse fails with drive): a positive solution exists on an interval with λ₁ = +1/4, enclosed between an explicit subsolution and a constant supersolution (classical barrier construction; the solution itself is not given in closed form)
- **Theorem 3.26** (Finite graph, machine-checked): the analogous positive-existence theorem on finite weighted graphs, with an explicit example, a maximum bound (Proposition 3.30) and a counterexample to the converse (Proposition 3.32)
- **Definition 5.1** (CD Condition): Measurable correlation between coherence and Jacobian dynamics
- **Definition 5.3** (Falsifiability): Five criteria for empirical refutation
