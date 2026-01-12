# Open Problems in Creative Determinant Theory

This document lists explicit theoretical gaps, unresolved questions, and conjectures in the Creative Determinant (CD) framework. These are **honest admissions of what is not yet known**, not weaknesses to hide. Contributions addressing any of these are highly valuable.

---

## 1. Relationship Between Weak and Strong Coherence

**Status**: Open.

**Problem**: The paper distinguishes "weak coherent configurations" (solutions to the PDE) from "strong coherent configurations" (fields satisfying the pointwise CD constraint \(\Phi(x) = \Phi(\theta(x), \phi(x), \mu(x))\)). Under what conditions are these equivalent? When does strong coherence imply weak, and vice versa?

**Why it matters**: This gap determines whether the PDE is a faithful representation of the underlying semiotic/enactivist intuition or merely an analytically tractable approximation.

**Starting point**: Assume a specific functional form for the pointwise constraint and derive the resulting PDE. Check consistency with the V1 model.

---

## 2. Justification of the Canonical Viability Closure

**Status**: Modeling choice, not derived.

**Problem**: The canonical closure \(b(x) = \eta(x) - \lambda\,\mu(x)\) is motivated heuristically but not derived from first principles. Are there contexts where other closures (e.g., multiplicative, nonlinear in \(\mu\)) are more natural?

**Why it matters**: The choice of closure affects viability thresholds and bifurcation structure. A principled way to select closures would strengthen applications.

**Starting point**: Propose alternative closures and compare their spectral and equilibrium properties numerically.

---

## 3. Multiplicity and Uniqueness of Equilibria

**Status**: Partial results.

**Problem**: Theorem 3.11 guarantees existence of at least one solution. Under what conditions are solutions unique? When do multiple distinct equilibria coexist?

**Why it matters**: Multiplicity would correspond to "multi-stable interpretive frames" in cognitive systems—a key enactivist prediction. Uniqueness might suggest strong convergence to a single interpretation.

**Starting point**: Numerical bifurcation analysis varying \(\beta, \lambda\). Theoretical tools: Morse index, degree theory, variational methods.

---

## 4. Master Equation with Exogenous Forcing

**Status**: Defined (Remark 3.15), not analyzed.

**Problem**: The driven case \(-\Delta u + a(x)|\nabla u| + b(x)u - c(x)u^p = f(x)\) encodes external input or environmental significance. How does nonzero \(f\) affect existence, stability, and multiplicity of equilibria?

**Why it matters**: Real cognitive systems are open, not closed. Understanding the driven case is essential for applications.

**Starting point**: Analyze perturbative effects of small \(f\) on known equilibria; numerical experiments with localized forcing.

---

## 5. Regularity and Smoothness of Solutions

**Status**: \(C^{2,\alpha}\) regularity established; higher regularity unclear.

**Problem**: Can solutions be shown to be \(C^\infty\) under stronger assumptions on coefficients? Are there contexts where solutions have singularities or shocks?

**Why it matters**: Smoothness properties affect numerical approximation and physical interpretation (e.g., are "meaning gradients" differentiable?).

**Starting point**: Apply elliptic bootstrapping; investigate boundary regularity near \(\partial M\).

---

## 6. Geometric Interpretation of the Gradient Term

**Status**: Interpretive.

**Problem**: The term \(a(x)|\nabla u|\) introduces nonlinearity and breaks symmetry. What is its precise geometric or dynamical meaning? Is there a variational principle from which it naturally arises?

**Why it matters**: If the PDE can be derived from a Lagrangian or energy functional, it would connect to physics and provide additional analytic tools.

**Starting point**: Investigate whether the V1 equation is the Euler-Lagrange equation of some action functional.

---

## 7. Bridging to Neural Dynamics

**Status**: Operational proposal, not yet instantiated.

**Problem**: How do you map a trained neural network (discrete layers, finite weights) onto a continuous semiotic manifold \((M, g)\)? How do you extract \(\theta, \phi, \mu\) from activations or gradients?

**Why it matters**: Without a concrete mapping, the framework remains abstract. A worked example on even a toy network would be a major advance.

**Starting point**: Apply manifold learning to a 2-layer MLP; hand-label regions as high/low coherence and fit simple \(\phi\) fields.

---

## 8. CD Condition: Sufficient or Necessary?

**Status**: Proposed as sufficient, not proven.

**Problem**: The CD condition (Definition 5.1) claims that high correlation between coherence and Jacobian volume indicates a CD regime. Is this correlation *necessary* for coherence, or only *sufficient*? Could there be coherent systems that don't exhibit the CD coupling?

**Why it matters**: If the condition is only sufficient, CD describes a *subclass* of coherent systems, not all of them.

**Starting point**: Look for counterexamples—systems with high coherence but no CD coupling.

---

## 9. Falsifiability Criteria: Operationalization

**Status**: Defined conceptually (Definition 5.3), not yet tested empirically.

**Problem**: The five falsifiability criteria (F1–F5) are stated qualitatively. What are precise, quantitative thresholds? How do you pre-register experiments to test them without post-hoc fitting?

**Why it matters**: Falsifiability is only meaningful if the criteria are concrete enough to test unambiguously.

**Starting point**: Design one experiment targeting F1 (coherence without coupling) with explicit statistical thresholds.

---

## 10. Time-Dependent Dynamics

**Status**: Not addressed.

**Problem**: The current framework studies equilibria (time-independent solutions). What about transient dynamics, approach to equilibrium, or oscillatory/chaotic regimes?

**Why it matters**: Real cognitive processes are temporal. A dynamical (not just static) CD theory would be more realistic.

**Starting point**: Formulate the parabolic PDE \(\partial_t u = -\Delta u + a(x)|\nabla u| + b(x)u - c(x)u^p\) and study stability of equilibria.

---

## How to Contribute

If you make progress on any of these, please:

1. Open an issue tagged `open-problem` referencing the problem number.
2. Share your results (even partial, even negative).
3. If you resolve a problem, open a PR adding your result to the appropriate section of the repo or a linked document.

**Negative results count.** If you show a problem is harder than expected, or a proposed approach doesn't work, that is valuable information.

---

## Proposing New Open Problems

If you identify a gap or unresolved question not listed here, open an issue tagged `open-problem-proposal` with:
- A clear statement of the problem.
- Why it matters.
- Suggested starting point (if any).

We'll add it to this document if it fits the framework.
