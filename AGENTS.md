# AGENTS.md

Guidance for coding agents and contributors working in this repository.

## Project

**Creative Determinant (CD)** — a research framework treating "coherent presence" as the solution to a nonlinear elliptic boundary-value problem on a semiotic manifold. The repo ships three coupled artefacts:

1. **Mathematics** — `paper/creative_determinant.pdf` (+ `.tex`, `.bib`) holds the theorems and proofs, including the finite-graph model of the Lean development.
2. **Numerics** — `src/cd/` Python library, `notebooks/cd_pde_demo.ipynb`, and `figures/`.
3. **Formalization** — `cd_formalization/` Lean 4 project (machine-checked proofs, git submodule).

Tests check implementation contracts and numerical consequences of the stated mathematics (eigenvalue formulas, viability thresholds, O(h²) grid convergence); the proofs are in the paper and the Lean development.

Status: version 1.2.0.dev0, unreleased; the last tagged release is v1.1.0. Research seed, intentionally small and auditable.

## Commands

This project uses **uv**, not pip. Do not suggest `pip install …`.

```bash
# Install (creates the venv, installs cd editable plus the dev dependency group)
uv sync

# Tests (package tests in tests/, repository-artefact tests in tests/repo/; counts in tests/README.md)
uv run pytest tests/ -v
grep -R '^[[:space:]]*def test_' tests/*.py tests/repo/*.py | wc -l   # current test-function count

# Coverage (mirrors CI's coverage job)
uv run coverage run -m pytest tests/
uv run coverage report --show-missing

# Lint / format — CI runs these in --check mode; won't auto-fix
uv run ruff check src/ tests/
uv run ruff format src/ tests/                    # auto-format locally
uv run ruff format src/ tests/ --check            # CI equivalent

# Type check (required in CI; fails on any error)
uv run mypy src/cd --ignore-missing-imports

# Notebook — execute in place from a fresh kernel, then validate (CI executes on Python 3.12)
uv run jupyter lab notebooks/
uv run jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=1200 --ExecutePreprocessor.record_timing=False \
  notebooks/cd_pde_demo.ipynb
uv run python scripts/validate_notebook.py notebooks/cd_pde_demo.ipynb --min-checks 30
uv run nbqa ruff notebooks/cd_pde_demo.ipynb --ignore E501,E402

# Figures (regenerates all 7 figures as PNG+PDF — 14 files — and prints ALL_FIGURES_OK)
uv run python figures/generate_figures.py

# Stack diagram (Figures 1-2 of the paper and the docs diagram), rendered in a pinned image (needs docker)
make -C paper                                     # cd_stack.dot -> docs/assets/cd-stack.svg + cd_stack_{core,loop}.pdf, installed in place
make -C paper check                               # render into a temporary directory; fails unless the committed outputs are identical

# Paper — reproducible build in the pinned TeX Live image (needs docker); commit the result
paper/build_paper.sh && cp paper/build/creative_determinant.pdf paper/
python3 scripts/check_paper_artifact.py paper/creative_determinant.pdf paper/build/creative_determinant.pdf
latexmk -pdf -cd paper/creative_determinant.tex   # quick local preview only; not the committed artifact

# Pre-commit (install once per clone; runs on every commit)
uv run pre-commit install
uv run pre-commit run --all-files
```

### Regenerating scientific artefacts after a numerics change

After any edit under `src/cd/`, run the figure and notebook commands above. Figures must end with `ALL_FIGURES_OK` and all 14 files must exist; PDF figures that differ only in metadata need not be committed. The notebook is committed **with** its executed outputs (the repository tests validate them), so execute it in place, validate, lint, and commit `notebooks/cd_pde_demo.ipynb` together with the source change. Any `.tex` edit is committed together with the rebuilt PDF. The stack diagram is rendered from `paper/cd_stack.dot` by `paper/stack_figures.py` in the image of `paper/figures.Dockerfile` (Graphviz, cairo and fonts pinned): after editing any of the three run `make -C paper` (regenerates the docs SVG and the paper's stack figures, which are inputs to the paper build) and rebuild the paper. The paper workflow re-renders the four outputs, fails unless the committed copies are byte-identical, builds the paper from the re-rendered figures, and runs `scripts/check_stack_citations.py`, which requires every statement or section the diagram and `docs/explanation/cd-stack.md` cite to have a `// cites:` line in `cd_stack.dot` whose title matches that statement's header in the rebuilt PDF.

### Bumping the Lean submodule

`git -C cd_formalization fetch`, inspect `git -C cd_formalization log --oneline HEAD..origin/main`, look for new `sorry`, changes to the `PDEInfra` hypotheses (structure fields in `CdFormal/Axioms.lean`) or renamed declarations cited from this repository, then `git -C cd_formalization checkout <sha>` and `git add cd_formalization` in a single-purpose `chore:` commit. Never bump to a commit that is not on upstream `main`; never force anything in the submodule.

## Layout

```
src/cd/                  # Python library (SciPy sparse matrices throughout)
├── __init__.py          # Public API — edit __all__ when adding exports
├── operators.py         # laplacian_1d/2d/3d_dirichlet, grid_3d ((z, y, x) layout)
├── solvers.py           # solve_1d_picard, solve_2d_picard (Picard iteration), barriers_1d
├── eigenvalues.py       # principal_eigenvalue_*, principal_eigenpair_*, viability_threshold_*
├── fields.py            # viability_canonical, creative_drive, gaussian_bump_*
├── graph.py             # Lean finite-graph model: SemioticGraph, solve_graph, triangle
├── _validation.py       # input validation shared by the numerical modules
└── analysis.py          # residual_*, check_convergence, classify_branch, presence_statistics, linfty_bound

tests/                   # package tests (ship in the sdist); per-file map in tests/README.md
└── repo/                # repository-artefact tests (scripts/, notebooks/, paper/; excluded from the sdist)

notebooks/cd_pde_demo.ipynb   # the one working companion; CI executes and validates it
scripts/
├── validate_notebook.py      # fail-closed notebook validator (REQUIRED_CHECKS)
├── check_paper_artifact.py   # byte-identity gate between the committed PDF and its rebuild
└── check_stack_citations.py  # the stack diagram's citations match statement headers in the rebuilt paper
figures/                 # generate_figures.py and the 7 PNG+PDF pairs it writes
paper/                   # .tex, .bib, .bbl, the committed PDF, build_paper.sh; cd_stack.dot, stack_figures.py, figures.Dockerfile, build_figures.sh (stack diagram); README
cd_formalization/        # git SUBMODULE → Project-Navi/cd-formalization (Lean 4)
docs/                    # Diataxis structure, rendered via zensical (zensical.toml)
.github/workflows/       # ci / codeql / docs / figures / notebooks / paper / semgrep
```

## Gotchas

- **`cd_formalization/` is a git submodule.** A bare `git clone` leaves it empty — `ls` shows nothing and it looks like missing code. Run `git submodule update --init --recursive` (or clone with `--recursive`) before touching Lean files.
- **`tests/README.md` may drift from reality.** If the documented test count disagrees with the code (verify with the grep command under Commands), treat the code as source of truth **and update `tests/README.md` in the same PR** so the docs stay aligned.
- **A failing test is a finding, not a verdict.** Establish whether the code, the claim or the oracle is wrong. Never weaken an assertion to get a pass; an oracle is corrected only with a stated reason and equivalent or stronger coverage. The rule is in `tests/README.md` (When a test fails).
- **Docs use `zensical`, not MkDocs.** Config is `zensical.toml`. Don't suggest `mkdocs build`.
- **Ruff runs `--no-fix --check` in pre-commit.** It won't auto-repair; formatting violations reject the commit. Run `uv run ruff format src/ tests/` locally before committing.
- **Gitleaks pre-commit hook is enabled.** Files matching secret patterns (API keys, tokens, private keys) block the commit. Do not `--no-verify` to bypass — rotate the secret and commit a redacted version.
- **Large files cap: 1024 KB** (`check-added-large-files`). Figures and the executed notebook are tracked because their generation is scripted; the notebook is close to 0.9 MB, so keep its outputs lean. New binaries ≥1 MB are rejected.
- **Notebook CI validates claims, not output counts.** `notebooks.yml` executes `cd_pde_demo.ipynb` on Python 3.12 and runs `scripts/validate_notebook.py`, which rejects any error output, any unexecuted code cell, any `CHECK FAILED` text, fewer than 30 `CHECK PASSED` lines, a missing or misplaced `ALL_NOTEBOOK_CHECKS_PASSED` marker, or any essential claim (`REQUIRED_CHECKS` in the script) that is missing or duplicated. New numerical claims in the notebook go through the `check(condition, name)` helper; renaming an essential claim requires updating `REQUIRED_CHECKS` and `tests/repo/test_validate_notebook_required.py`. The notebook is also linted fail-closed (`nbqa ruff`, ignoring E501/E402).
- **Statement numbers in the stack diagram are literal.** `paper/cd_stack.dot` and `docs/explanation/cd-stack.md` cite Definitions, Theorems, Propositions, Remarks and Sections by number, and each cited number has a `// cites: <Kind> <n.m> = <title start>` line in `cd_stack.dot`. Inserting a numbered statement in Section 2 or 3 shifts the numbers; `scripts/check_stack_citations.py` then fails because a header no longer matches its title. Fix the numbers and the `cites:` lines, regenerate, rebuild.
- **CI triggers are path-filtered.** `ci.yml` runs on pushes and pull requests to `main`. `notebooks.yml` runs on `notebooks/**`, `src/**`, `scripts/validate_notebook.py`, `pyproject.toml`, `uv.lock`; `figures.yml` on `figures/**`, `src/**`, `pyproject.toml`, `uv.lock`; `paper.yml` on `paper/**`, `scripts/check_paper_artifact.py`, `scripts/check_stack_citations.py`, `docs/explanation/cd-stack.md`, `docs/assets/cd-stack.svg` and itself; `docs.yml` on `docs/**`, `zensical.toml` and itself.
- **CodeQL is advanced setup, not default.** `codeql.yml` emits the check `codeql` (the job key), not `Analyze (python)` (the SARIF-upload-side check, which never fires on Dependabot PRs because their `GITHUB_TOKEN` is read-only). The check is not currently in the ruleset's required list, but keep the job key stable, and if someone toggles GitHub's default CodeQL setup on, it silently disables `codeql.yml` — restore advanced setup via the Actions UI or API.

## Conventions

### Python
- Ruff config: `line-length = 100`, `target-version = "py310"`, selected rules `E, F, W, I, UP`; `E501` is intentionally ignored for linting.
- No black; ruff-format is the only formatter.
- Type hints on all public functions. NumPy-style docstrings.
- SciPy sparse matrices for all linear operators (dense is a correctness bug at scale).
- Python 3.10+ (CI matrix: 3.10 / 3.11 / 3.12).

### Public API
- Exports live in `src/cd/__init__.py` via explicit `__all__`. When adding a symbol, export it there so `from cd import X` works in notebooks and tests, and list it in `src/README.md`.
- Notebook and tests import from `cd`, not relative paths.

### Commits / branches
- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:`, `ci:`, `perf:`.
- Branches: `<type>/<slug>` (e.g. `fix/notebook-section-refs`).
- Stage specific files (`git add src/cd/solvers.py`) — not `git add -A`, so local tool state and caches never land in a commit.
- Signed commits are required on main (org ruleset).

### Mathematical honesty
- Label results in docstrings and comments as **Theorem / Proposition / Lemma** (with the paper number), **Conjecture**, **Heuristic**, or **Observation (numerical)** for facts established only by computation (same rule as the contributing guide).
- The continuum existence theorems in Lean are conditional on the `PDEInfra` hypotheses (structure fields, not Lean axioms); the finite-graph theorem is proved outright. Don't claim the continuum operator instantiates that interface (it does not: see paper Appendix A), and don't describe the framework as axiom-free.
- Three numerical models are distinct: the continuum problem (centered finite differences), the Lean finite-graph model (`cd.graph`, unnormalized weights, square-root gradient), and the 3D eigenvalue illustration. Never relabel one as another.
- A solver run is accepted only by the residual of the discrete equation (`info["converged"]`, `info["termination"]`, `info["branch"]`); `check_convergence` re-validates the recorded numbers rather than trusting the flag (residual criterion, the update criterion against the recorded `tol`, boundary data, and the type, finiteness and sign of every field; a report missing `tol` is unvalidated, never accepted); initial data must be nonnegative; a run that returns zero is not evidence that no positive branch exists.
- The spectral condition λ₁ < 0 is sufficient in general and exact only for a ≡ 0 (Propositions 3.19 and 3.21). Graph eigenvalues are assembled from off-diagonal weights and verified against the direct operator; a value within the floating-point margin of zero is `indeterminate`, never a certificate.

## Testing philosophy

Each test documents the theorem or claim it validates and prefers analytic validation (compare to a closed form) over regression against a stored number; the reference pattern, the per-file map and the count live in `tests/README.md`. Cite the paper statement (for example Definition 3.13 for the eigenvalue formula, Theorem 3.16 for positive existence) and, if relevant, the Lean declaration.

## CI

Seven workflows. The org ruleset on `main` requires five checks — `lint`, `typecheck`, `security`, `quality-gate` (all in `ci.yml`) and `semgrep` (`semgrep.yml`) — plus signed commits and a code-owner review. Job keys map 1-to-1 to the check names: don't rename these jobs or add `name:` overrides that would change the emitted check name.

| Workflow | File | Notes |
|---|---|---|
| CI | `ci.yml` | Required job keys **`lint`, `typecheck`, `security`, `quality-gate`**. `typecheck` (mypy) and `security` (bandit, pip-audit on the locked environment) fail closed. `test-run` is the per-Python matrix and `test` its aggregator; `numerical-stability`, `eigenvalue-precision`, `threshold-verification` and `coverage` run pytest subsets. None of these five is in the required list. |
| CodeQL Analysis | `codeql.yml` | Emits `codeql` (job key; runs on every PR, not currently required). Also emits `Analyze (python)` on pushes to main and the weekly schedule, but not on Dependabot PRs. |
| Semgrep | `semgrep.yml` | Emits **`semgrep`** (required). Runs `p/python` + `p/owasp-top-ten`. |
| Notebook Validation | `notebooks.yml` | Executes `cd_pde_demo.ipynb` from a fresh kernel, validates it with `scripts/validate_notebook.py` (fail-closed), lints via nbqa (fail-closed). |
| Figure Validation | `figures.yml` | Runs `generate_figures.py`, requires the `ALL_FIGURES_OK` marker (every solve converged), verifies all 14 PNG+PDF files exist. |
| Paper | `paper.yml` | Re-renders the stack diagram with `paper/build_figures.sh check` in its pinned image and requires the committed SVGs and figure PDFs to be byte-identical; then rebuilds the PDF from the re-rendered figures with `paper/build_paper.sh` in the pinned TeX Live image (digest + fixed `SOURCE_DATE_EPOCH`, byte-reproducible), fails on unresolved references, and requires the committed PDF to be byte-identical to the rebuild (`scripts/check_paper_artifact.py`; on mismatch it prints an order-preserving text diff and a page render comparison). |
| Docs | `docs.yml` | Builds the zensical site on PRs and deploys it on pushes to main. |

## When adding new code

1. Land tests first when the claim is mathematical (write the failing assertion, then the implementation).
2. Export new public functions via `src/cd/__init__.py` and document them in `src/README.md`.
3. Run `uv run ruff format src/ tests/` and `uv run pytest tests/ -v` before committing.
4. If the change affects numerics, regenerate the figures and re-execute the notebook (see "Regenerating scientific artefacts") before pushing.
5. If you touch the Lean submodule, commit and push in `cd-formalization` first, then bump the submodule pointer here.

## What this repo is not

- Not a production library — the version tracks the repository release, not an API contract; interfaces may still change.
- Not a finished theory — see `docs/explanation/open-problems.md` and the Research Roadmap.
- Apache 2.0 allows permissive reuse, but you must preserve required copyright/license/NOTICE attributions per the license terms; beyond that, the `CONTRIBUTORS.md` convention still applies socially.
