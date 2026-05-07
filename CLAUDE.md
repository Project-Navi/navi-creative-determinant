# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**Creative Determinant (CD)** — a research framework treating "coherent presence" as the solution to a nonlinear elliptic boundary-value problem on a semiotic manifold. The repo ships three coupled artefacts:

1. **Mathematics** — `paper/creative_determinant.pdf` (+ `.tex`, `.bib`, `Makefile`) holds the theorems and proofs.
2. **Numerics** — `src/cd/` Python library, `notebooks/cd_pde_demo.ipynb`, and `figures/`.
3. **Formalization** — `cd_formalization/` Lean 4 project (machine-checked proofs, git submodule).

Tests validate **mathematical claims** (eigenvalue formulas, bifurcation thresholds, O(h²) grid convergence) — not implementation behaviour.

Status: v0.1.0 Alpha. Research seed, intentionally small and auditable.

## Commands

This project uses **uv**, not pip. Do not suggest `pip install …` in session.

```bash
# Install (creates venv, installs cd package editable + dev extras)
uv sync

# Tests (24 total across 5 files)
uv run pytest tests/ -v
uv run pytest tests/test_core.py -v               # eigenvalue / threshold suite
uv run pytest tests/test_2d.py -v                 # 2D solver

# Coverage (mirrors CI's coverage job)
uv run coverage run -m pytest tests/
uv run coverage report --show-missing

# Lint / format — CI runs these in --check mode; won't auto-fix
uv run ruff check src/ tests/
uv run ruff format src/ tests/                    # auto-format locally
uv run ruff format src/ tests/ --check            # CI equivalent

# Type check (mypy informational in CI; `|| true`)
uv run mypy src/cd --ignore-missing-imports

# Notebook
uv run jupyter lab notebooks/
uv run jupyter nbconvert --to notebook --execute notebooks/cd_pde_demo.ipynb

# Figures (regenerates all 7 figures as PNG+PDF — 14 files total — into figures/)
uv run python figures/generate_figures.py

# Paper — two-step build
make -C paper                                     # graphviz diagrams (cd_stack.svg/pdf/png)
latexmk -pdf -cd paper/creative_determinant.tex   # LaTeX PDF (pdflatex + bibtex passes)

# Pre-commit (install once per clone; runs on every commit)
uv run pre-commit install
uv run pre-commit run --all-files
```

## Layout

```
src/cd/                  # Python library (SciPy sparse matrices throughout)
├── __init__.py          # Public API — edit __all__ when adding exports
├── operators.py         # laplacian_1d_dirichlet, laplacian_2d_dirichlet
├── solvers.py           # solve_1d_picard, solve_2d_picard (Picard iteration)
├── eigenvalues.py       # principal_eigenvalue_*, viability_threshold_*
├── fields.py            # viability_canonical, creative_drive, gaussian_bump_*
└── analysis.py          # residual_*, check_convergence, solution_type, linfty_bound

tests/                   # pytest suite — validates theorems, not implementation
├── test_core.py         # 12 tests: eigenvalues, convergence, residuals, thresholds
├── test_2d.py           # 2 tests
├── test_eigenvalues.py  # 3 tests
├── test_fields.py       # 4 tests
└── test_spatial_solver.py  # 3 tests

notebooks/
├── cd_pde_demo.ipynb    # Primary pedagogical artefact; CI executes it
└── alternates/          # Local experimental variants (untracked workspace)

figures/
├── generate_figures.py  # Regenerates all paper figures
├── fig1…fig7_*.png/pdf  # Publication-quality outputs

cd_formalization/        # Git SUBMODULE → Project-Navi/cd-formalization (Lean 4)
paper/                   # creative_determinant.pdf + .tex + bib + Makefile + svg
docs/                    # Diataxis structure, rendered via zensical
experiments/             # Scaffolding for empirical instantiations
.github/workflows/       # ci / codeql / docs / figures / notebooks / semgrep / scorecard
```

## Gotchas

- **`cd_formalization/` is a git submodule.** A bare `git clone` leaves it empty — `ls` shows nothing and it looks like missing code. Run `git submodule update --init --recursive` (or clone with `--recursive`) before touching Lean files.
- **`tests/README.md` may drift from reality.** If the documented test count disagrees with the code (verify with `grep -c "def test_" tests/test_*.py`), treat the code as source of truth **and update `tests/README.md` in the same PR** so the docs stay aligned.
- **Tests are mathematical proofs, not regressions.** If a test fails after editing `src/cd/`, the math is wrong, not the test. Do not "fix" tests to pass — fix the solver/operator.
- **Docs use `zensical`, not MkDocs.** Config is `zensical.toml`. Don't suggest `mkdocs build`.
- **Ruff runs `--no-fix --check` in pre-commit.** It won't auto-repair; formatting violations reject the commit. Run `uv run ruff format src/ tests/` locally before committing.
- **Gitleaks pre-commit hook is enabled.** Files matching secret patterns (API keys, tokens, private keys) block the commit. Do not `--no-verify` to bypass — rotate the secret and commit a redacted version.
- **Large files cap: 1024 KB** (`check-added-large-files`). Existing figures (>200 KB) are tracked because generation is scripted. New binaries ≥1 MB will be rejected.
- **Notebook CI asserts ≥7 code-cell outputs.** If you restructure `cd_pde_demo.ipynb`, make sure executed cells still emit ≥7 outputs or `notebooks.yml` will fail.
- **CI triggers are path-filtered.** `notebooks.yml` only runs on `notebooks/**` or `src/**`; `figures.yml` only on `figures/**` or `src/**`. `ci.yml` runs on every push/PR.
- **CodeQL is advanced setup, not default.** Required check name is `codeql` (the job key in `codeql.yml`), not `Analyze (python)` (the SARIF-upload-side check). The job-level check was chosen because Dependabot's `GITHUB_TOKEN` is forced read-only on `pull_request` events, so the SARIF upload no-ops on Dependabot PRs and `Analyze (python)` never fires — freezing every Dependabot PR. If someone toggles GitHub's default CodeQL setup on, it will silently disable `codeql.yml` and break the required-checks contract — restore advanced via the Actions UI or API.

## Conventions

### Python
- Ruff config: `line-length = 100`, `target-version = "py310"`, selected rules `E, F, W, I, UP`; `E501` is intentionally ignored for linting.
- No black; ruff-format is the only formatter.
- Type hints on all public functions. NumPy-style docstrings.
- SciPy sparse matrices for all linear operators (dense is a correctness bug at scale).
- Python 3.10+ (CI matrix: 3.10 / 3.11 / 3.12).

### Public API
- Exports live in `src/cd/__init__.py` via explicit `__all__`. When adding a symbol, export it there so `from cd import X` works in notebooks and tests.
- Notebook and tests import from `cd`, not relative paths.

### Commits / branches
- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:`, `ci:`, `perf:`.
- Branches: `<type>/<slug>` (e.g. `fix/notebook-section-refs`).
- Stage specific files (`git add src/cd/solvers.py`) — not `git add -A`, to avoid catching `.claude-flow/`, `notebooks/alternates/`, `__pycache__/`, etc.
- Signed commits are required on main (org ruleset).

### Mathematical honesty
- Label results as **Theorem**, **Conjecture**, or **Heuristic** in code comments and docstrings (same rule as `CONTRIBUTING.md`).
- Lean proofs rest on an explicit `PdeInfra` axiom surface — don't claim the framework is axiom-free in docs or commit messages.

## Testing philosophy

Each test documents the theorem or claim it validates. Reference pattern:

```python
def test_2d_eigenvalue_formula(self):
    """Verify λ₁ = π²(1/Lx² + 1/Ly²) - βb for 2D rectangle (Theorem 3.12)."""
```

Before adding a test:
1. Identify the mathematical claim.
2. Write an assertion that fails iff the claim is false.
3. Prefer analytic validation (compare to closed-form) over regression (compare to a stored number).
4. Cite the paper theorem and, if relevant, the Lean lemma.

## CI

Seven workflows. The unified `ci.yml` holds four of the six required checks (`lint`, `typecheck`, `security`, `quality-gate`); `codeql.yml` emits `codeql` and `semgrep.yml` emits `semgrep`.

| Workflow | File | Notes |
|---|---|---|
| CI | `ci.yml` | Job keys mapped to ruleset checks: **`lint`, `typecheck`, `security`, `quality-gate`**. `test-run` is the per-Python matrix; `test` is the aggregator (runs on every PR but is not in the ruleset's required list). Non-required: `numerical-stability`, `eigenvalue-precision`, `threshold-verification`, `coverage`. |
| CodeQL Analysis | `codeql.yml` | Emits **`codeql`** (job key, required by org ruleset). Also emits `Analyze (python)` on `push` events to main and the weekly schedule, but not on Dependabot PRs (token is read-only). Do not rename the job or add a `name:` override. |
| Semgrep | `semgrep.yml` | Emits **`semgrep`** (required). Runs `p/python` + `p/owasp-top-ten`. |
| OpenSSF Scorecard | `scorecard.yml` | Scheduled + on-push to main. Calls the org-shared workflow. |
| Notebook Validation | `notebooks.yml` | Executes `cd_pde_demo.ipynb`, validates ≥7 output cells, lints via nbqa. |
| Figure Validation | `figures.yml` | Runs `generate_figures.py`, verifies all 14 PNG+PDF files exist. |
| Docs | `docs.yml` | Builds zensical site. |

**Org ruleset contract (`CI: Python Tier`)** requires: `lint`, `typecheck`, `security`, `codeql`, `semgrep`, `quality-gate`. Job keys in the workflow files map 1-to-1 to these check names — don't rename jobs without updating the ruleset, and don't add `name:` overrides that would change the emitted check name. (`test` is the aggregator job in `ci.yml` and runs on every PR, but is not in the ruleset's required list.)

## When adding new code

1. Land tests first when the claim is mathematical (write the failing assertion, then the implementation).
2. Export new public functions via `src/cd/__init__.py`.
3. Run `uv run ruff format src/ tests/` and `uv run pytest tests/ -v` before committing.
4. If the change affects numerics, re-run the notebook headlessly (`uv run jupyter nbconvert --to notebook --execute notebooks/cd_pde_demo.ipynb`) before pushing.
5. If you touch the Lean submodule, commit and push in `cd-formalization` first, then bump the submodule pointer here.

## What this repo is not

- Not a production library — API stability is not guaranteed before 1.0.
- Not a finished theory — see `docs/explanation/open-problems.md` and the Research Roadmap.
- Apache 2.0 allows permissive reuse, but you must preserve required copyright/license/NOTICE attributions per the license terms; beyond that, the `CONTRIBUTORS.md` convention still applies socially.
