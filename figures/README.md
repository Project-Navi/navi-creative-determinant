# Figures

Publication-quality visualizations of the Creative Determinant PDE framework.

These figures provide visual evidence for the core mathematical claims. Each demonstrates a specific aspect of the viability threshold and presence emergence dynamics.

## Figure Index

| Figure | File | Demonstrates | Paper Section |
|--------|------|--------------|---------------|
| **Fig 1** | `fig1_eigenvalue_threshold` | Principal eigenvalue λ₁ crossing zero as β increases; numeric vs analytic agreement | §3 (Definition 3.13, Theorem 3.16) |
| **Fig 2** | `fig2_threshold_comparison` | Below-threshold (flat) vs above-threshold (emergent) presence Φ(x) | §3 (Existence) |
| **Fig 3** | `fig3_canonical_closure_sweep` | Presence collapse and eigenvalue indicator as contradiction cost λ increases | §3 (Canonical closure) |
| **Fig 4** | `fig4_2d_presence_field` | 2D viability field b(x,y) and emergent presence Φ(x,y) with contours | §4 (Spatial heterogeneity) |
| **Fig 5** | `fig5_grid_refinement` | Convergence under grid refinement: discretization error of max Φ at second order; the discrete residual sits at solver tolerance on every grid | §3 (numerical companion) |
| **Fig 6** | `fig6_field_decomposition` | Component fields: κγ, μ(x), b(x), a(x) and their relationships | §2 (Definitions) |
| **Fig 7** | `fig7_2d_phase_transition` | Side-by-side: viable equilibrium (maxΦ > 0) vs collapsed state (maxΦ ≈ 0) | §4/§5 (Phase transition) |

## Key Visual Claims

1. **Threshold is sharp** (Fig 1, 2): The transition from trivial to nontrivial solution is not gradual—it's a bifurcation at β*.

2. **Contradiction kills presence** (Fig 3): As contradiction cost increases, presence collapses to zero. The eigenvalue indicator predicts this.

3. **Spatial structure emerges** (Fig 4, 7): The PDE produces smooth, localized presence fields—not arbitrary point masses.

4. **Numerics are sound** (Fig 5): Second-order convergence of max Φ under refinement confirms the finite-difference scheme; the residual of the discrete equation is at solver tolerance on every grid and is not a convergence measure.

Every solve behind a figure is residual-validated by the `cd` library. A point whose solve did not converge would be drawn as a hollow red marker with no line through it and the script would print `FIGURES_WITH_UNRESOLVED_POINTS`; CI requires `ALL_FIGURES_OK`.

## Regenerating Figures

```bash
uv run python figures/generate_figures.py   # from the repository root
```

**Requirements:** the project environment (`uv sync`); the script uses only the `cd` library, NumPy and Matplotlib. Parameters are recorded in `PARAMETERS` at the top of the script and printed at startup.

**Output:** PNG (300 DPI) and PDF for each figure.

## Using in Publications

All figures are licensed under Apache 2.0. If you use them, please cite:

> Spence, N. (2026). *Creative Determinant PDE Framework: Numerical Demonstrations*. Project Navi LLC.

## Adding New Figures

1. Add generation function to `generate_figures.py`
2. Call it from `main()`
3. Update this README with the new figure's purpose
4. Open a PR
