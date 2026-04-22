# Creative Determinant Research Roadmap

This document outlines open research directions stemming from the Creative Determinant (CD) framework. **These are not private plans — they are invitations.** If you pick up any of these, you are doing canonical CD work. Open an issue or PR to coordinate, or just run with it and share results.

---

## 1. Construct Semiotic Manifolds from Real Systems

**Motivation**: The framework assumes a manifold \(M\) of meanings, but how do you extract \(M\) from a real neural network or cognitive system?

**What this involves**:
- Techniques for dimensionality reduction or manifold learning (e.g., UMAP, diffusion maps, autoencoders) applied to activation spaces.
- Riemannian metric inference from local gradients or Hessians.
- Validation: does the inferred manifold structure predict behavioral or representational properties?

**Technical prerequisites**: Python/PyTorch, familiarity with manifold learning, access to model activations.

**Starting point**: Apply simple manifold learning to a toy 2-layer MLP on MNIST; visualize the 2D latent as a candidate \(M\).

---

## 2. Empirically Test the CD Condition on Toy Dynamical Systems

**Motivation**: The CD condition claims coherence observables correlate with Jacobian volume dynamics. Test this on systems where both are computable exactly.

**What this involves**:
- Pick a low-dimensional dynamical system (e.g., 2D or 3D maps, simple ODEs).
- Define a coherence observable (e.g., distance to a known attractor, entropy of trajectory distribution).
- Compute Jacobian determinants along trajectories.
- Measure correlation and variance as in Definition 5.1 of the paper.

**Technical prerequisites**: Basic dynamical systems theory, Python (NumPy/SciPy).

**Starting point**: Logistic map, Henon map, or Lorenz system with hand-chosen coherence metrics.

---

## 3. Alternative Viability Closures

**Motivation**: The canonical closure \(b = \kappa\gamma - \lambda\mu\) is one choice. Are there others that fit different cognitive or computational contexts?

**What this involves**:
- Propose alternative functional forms for \(b(x)\) (e.g., nonlinear couplings, multiplicative terms).
- Analyze how viability thresholds \(\lambda_1^{(b)}\) change under these alternatives.
- Numerical experiments: does changing the closure qualitatively alter bifurcation structure?

**Technical prerequisites**: PDE theory, finite-difference or FEM solvers.

**Starting point**: Try \(b = \kappa\gamma \cdot e^{-\lambda\mu}\) or \(b = \kappa\gamma - \lambda\mu^2\) in the 1D notebook and observe threshold shifts.

---

## 4. Multiplicity of Coherent Configurations

**Motivation**: The existence theorem guarantees at least one solution, but enactivist intuition suggests multiple "interpretive frames" might coexist. Are there regimes with multiple equilibria?

**What this involves**:
- Bifurcation analysis: vary parameters \(\beta\), \(\lambda\) and look for saddle-node, pitchfork, or transcritical bifurcations.
- Numerical experiments: initialize Picard iteration from different seeds and find distinct solutions.
- Theoretical analysis: prove multiplicity using variational or topological methods.

**Technical prerequisites**: Nonlinear analysis, bifurcation theory, numerical continuation.

**Starting point**: Extend the 1D notebook to sweep \(\lambda\) more finely and check for hysteresis.

---

## 5. Master Equation with Nonzero Forcing

**Motivation**: The driven case \(f \neq 0\) (Remark 3.17) models systems receiving exogenous input. What does coherence look like under external driving?

**What this involves**:
- Formulate boundary-value or initial-value problems with \(f(x)\) representing external significance or environmental input.
- Study how \(f\) perturbs equilibria or creates new stable patterns.
- Interpretation: when does external input stabilize vs. destabilize coherence?

**Technical prerequisites**: Elliptic/parabolic PDE theory, numerical time-stepping.

**Starting point**: Add a simple Gaussian forcing term to the 1D V1 model and observe equilibrium shifts.

---

## 6. CD Condition on Small Neural Networks

**Motivation**: Can we actually measure the CD condition on a real (if small) neural network?

**What this involves**:
- Train or fine-tune a small transformer or RNN.
- Define a coherence observable (e.g., intrinsic dimensionality of neural representations, attention entropy).
- Approximate Jacobian determinants using low-rank methods or trace estimators.
- Compute correlations across a dataset or along generated trajectories.

**Technical prerequisites**: ML frameworks (PyTorch/JAX), Jacobian estimation techniques, interpretability tools.

**Starting point**: 2-layer transformer on a toy language task, compute correlations layer-by-layer.

---

## 7. Care-Weighted Metrics and Behavioral Experiments

**Motivation**: The care-weighted homotopy energy principle (Proposition 4.9) suggests care acts as a topological obstruction. Can this be tested behaviorally?

**What this involves**:
- Design a cognitive task where "care" (attention, importance weighting) is experimentally manipulated.
- Measure whether paths through "low-care" conceptual regions are indeed costly (slower, error-prone) even when geometrically short.
- Map results onto a simple manifold model.

**Technical prerequisites**: Experimental design, behavioral data analysis, basic topology.

**Starting point**: Simple lexical decision or category learning task with attention manipulation.

---

## 8. Falsification Experiments

**Motivation**: Definition 5.3 lists five falsifiability criteria. Actively trying to break the framework is a first-class contribution.

**What this involves**:
- Design experiments targeting F1–F5 (e.g., look for coherence without coupling, Hamiltonian systems with CD signatures, contradiction resolution without care).
- Document results honestly: null results or violations are valuable.

**Technical prerequisites**: Depends on the criterion chosen.

**Starting point**: F3 (Hamiltonian coherence) --- construct a volume-preserving map and test for CD coupling.

---

## 9. Extensions to Multi-Modal or Multi-Agent Settings

**Motivation**: Real cognition involves multiple modalities (vision, language, affect) and social interaction. Can CD scale to these?

**What this involves**:
- Vector-valued presence fields \(\mathbf{\Phi}(x)\) with different components for modalities or agents.
- Coupled PDEs on shared or overlapping manifolds.
- Interpretation: multi-modal coherence as alignment across components; social meaning-making as coupled dynamics.

**Technical prerequisites**: Systems of PDEs, multi-agent dynamical systems.

**Starting point**: Two coupled scalar fields on the same domain, representing two agents or two modalities.

---

## 10. Computational Pathology Models

**Motivation**: Can CD formalize cognitive/psychiatric pathologies as breakdown regimes of coherence?

**What this involves**:
- Model depression as \(\kappa \to 0\) (where \(\kappa\) is the care parameter; zero care everywhere).
- Model schizophrenia as high \(\mu\) (contradiction measure) without resolution (contradictions persist).
- Model OCD as failure of saturation (presence fields don't stabilize).

**Technical prerequisites**: Conceptual modeling, clinical intuition, dynamical systems.

**Starting point**: Modify notebook parameters to simulate these regimes; visualize equilibrium behavior.

---

## How to claim a direction

1. Open an issue tagged `roadmap` describing which direction you want to pursue (or propose a new one).
2. Or just start working and open a PR when you have something to share.
3. Collaboration is encouraged --- tag others if you want co-investigators.

**These directions are intentionally open.** There is no central authority. If you make progress on any of these, you are extending the CD research program.

---

## Adding new directions

If you see a direction not listed here, propose it! Open an issue tagged `roadmap-proposal` with:
- One-sentence motivation.
- What the direction involves.
- Suggested starting point.

We'll add it to this document if it aligns with the framework.
