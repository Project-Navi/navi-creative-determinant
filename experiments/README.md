# CD Experiments

This directory is a workspace for empirical instantiations and tests of the Creative Determinant (CD) framework. The goal is to move from theory to data: can we measure the CD condition, viability thresholds, or coherence dynamics in real systems?

---

## Proposed Experiments

### 1. Toy Dynamical System: Hénon Map with Coherence Observable

**Goal**: Test the CD condition (Definition 5.1) on a simple 2D map where Jacobians are computable exactly.

**Setup**:
- Iterate the Hénon map: \(x_{n+1} = 1 - a x_n^2 + y_n\), \(y_{n+1} = b x_n\).
- Define a coherence observable, e.g., inverse distance to the attractor or local Lyapunov exponent sign stability.
- Compute \(\log|\det J|\) at each step.
- Measure correlation across a long trajectory.

**Expected outcome**: In chaotic regimes, low correlation. In periodic or quasi-periodic regimes, higher correlation if coherence is well-chosen.

**Technical requirements**: Python (NumPy), basic dynamical systems knowledge.

**Status**: Not yet implemented. **Contributions welcome.**

---

### 2. Small Neural Network: CD Condition on a 2-Layer Transformer

**Goal**: Measure the CD condition on a real (if small) neural network processing sequential data.

**Setup**:
- Train or fine-tune a 2-layer transformer on a toy task (e.g., next-token prediction on a small vocabulary).
- Define coherence observable: intrinsic dimension of hidden activations, attention entropy, or perplexity inverse.
- Estimate layer-wise Jacobian log-determinants using low-rank trace estimators or factorization.
- Compute correlation across a dataset.

**Expected outcome**: Layers processing "coherent" sequences (low perplexity, high predictability) should show higher CD correlation than layers processing noise.

**Technical requirements**: PyTorch or JAX, Jacobian approximation tools, interpretability frameworks.

**Status**: Not yet implemented. **Contributions welcome.**

---

### 3. Behavioral Experiment: Care-Weighted Accessibility

**Goal**: Test whether paths through "low-care" conceptual regions are indeed costly, even if geometrically short (Proposition 4.9).

**Setup**:
- Design a category learning or semantic priming task.
- Manipulate attention/importance (care) on certain dimensions.
- Measure reaction times or error rates for transitions through high-care vs. low-care regions.
- Map results onto a simple 2D manifold model.

**Expected outcome**: Transitions forced through low-care regions should be slower/more error-prone than geometrically equivalent transitions through high-care regions.

**Technical requirements**: Experimental design, behavioral data collection, basic topology.

**Status**: Conceptual stage. **Collaborators needed.**

---

## How to Add an Experiment

1. Create a subdirectory under `experiments/` (e.g., `experiments/henon_map_cd/`).
2. Include:
   - `README.md` describing the experiment.
   - Code (scripts, notebooks).
   - Data or links to data.
   - Results (plots, tables, summary).
3. Open a PR with a summary.

Even **negative results** (experiments that don't confirm CD predictions) are valuable. Document them honestly.

---

## Running Existing Experiments

[Once experiments are added, this section will provide instructions for reproducing them.]

---

## Proposing New Experiments

Open an issue tagged `experiment-proposal` with:
- One-sentence goal.
- Brief setup description.
- Expected outcome.
- Technical requirements.

We'll add it to this README and create a subdirectory scaffold.

---

**Empirical grounding is essential for the CD framework to move from theory to practice. Your experimental contributions are crucial.**
