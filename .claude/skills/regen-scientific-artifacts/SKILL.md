---
name: regen-scientific-artifacts
description: Regenerate all publication figures and the executed notebook after changes to src/cd/ numerics. Runs generate_figures.py and jupyter nbconvert headless, verifies the 7 figure pairs and ≥7 notebook output cells, and reports drift from CI expectations. Use after any change to solvers, eigenvalues, or fields in src/cd/.
---

# Regenerate Scientific Artefacts

Catches figure and notebook drift locally before the `figures.yml` and `notebooks.yml` workflows catch it in CI.

## When to invoke

- After any edit to `src/cd/operators.py`, `src/cd/solvers.py`, `src/cd/eigenvalues.py`, `src/cd/fields.py`, or `src/cd/analysis.py`.
- Before pushing a PR that touches numerics.
- When debugging a CI failure in the Figure Validation or Notebook Validation workflow.

## Steps

1. **Sync environment:**
   ```bash
   uv sync --quiet
   ```

2. **Regenerate figures:**
   ```bash
   uv run python figures/generate_figures.py
   ```

3. **Verify all 14 expected figure files exist** (7 PNGs + 7 PDFs — CI asserts this):
   ```bash
   missing=0
   for stem in fig1_eigenvalue_threshold fig2_threshold_comparison fig3_canonical_closure_sweep \
               fig4_2d_presence_field fig5_grid_refinement fig6_field_decomposition \
               fig7_2d_phase_transition; do
     for ext in png pdf; do
       if [[ ! -f "figures/${stem}.${ext}" ]]; then
         echo "MISSING: figures/${stem}.${ext}"
         missing=$((missing + 1))
       fi
     done
   done
   [[ $missing -eq 0 ]] && echo "All 14 figure files present."
   ```

4. **Execute the notebook headlessly** (matches `notebooks.yml`):
   ```bash
   uv run jupyter nbconvert --to notebook --execute \
     --ExecutePreprocessor.timeout=600 \
     --ExecutePreprocessor.kernel_name=python3 \
     --output /tmp/cd_pde_demo_exec.ipynb \
     notebooks/cd_pde_demo.ipynb
   ```

5. **Count output cells** — CI fails if fewer than 7:
   ```bash
   uv run python -c "
   import json
   with open('/tmp/cd_pde_demo_exec.ipynb') as f:
       nb = json.load(f)
   n = sum(1 for c in nb['cells'] if c['cell_type']=='code' and c.get('outputs'))
   print(f'Code cells with outputs: {n}')
   assert n >= 7, f'Only {n} output cells (CI requires >=7)'
   "
   ```

6. **Report**:
   - List any missing figures.
   - Show notebook output-cell count.
   - Note any execution errors.
   - If figures changed visibly, suggest committing them as part of the same PR with a note in the commit message explaining the visual delta.

## Do NOT

- Auto-commit regenerated figures or notebooks. Figure changes are publication outputs and deserve explicit review.
- Push the executed notebook into `notebooks/` — the executed copy lives in `/tmp/`.
- Skip the notebook execution step when only figures changed, or vice versa — the two workflows share `src/cd/` and drift in lockstep.

## Troubleshooting

- **`ModuleNotFoundError: cd`** — run `uv sync` first; the `cd` package must be installed editable.
- **Timeout during notebook execution** — default is 600s; large 2D/3D sweeps may need more. Raise `--ExecutePreprocessor.timeout`.
- **Figure drift but no src/cd/ change** — check if matplotlib or numpy was updated (`uv.lock` diff); numerical output can shift with backend updates.
