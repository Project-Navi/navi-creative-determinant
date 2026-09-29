# Repository-artefact tests

The tests in this directory exercise repository artefacts that live outside the
Python package: `scripts/` (the notebook validator, the paper artifact gate and the stack
citation check `scripts/check_stack_citations.py`), `notebooks/cd_pde_demo.ipynb`, and
`paper/` (through the gate, and the stack diagram source `cd_stack.dot` with its renderer
`stack_figures.py`). The shared
`conftest.py` here resolves the repository root as `Path(__file__).resolve().parents[2]`
(the `repo_root` fixture), loads a script under `scripts/` as a fresh module
(`load_script`) and writes synthetic notebooks under `tmp_path` (`write_notebook`).
They need a full checkout, plus `nbformat` from the dev dependency group (the paper
gate's unit tests need only the standard library; its diagnostics use poppler when present).

They are excluded from the source distribution (`[tool.hatch.build.targets.sdist]`
in `pyproject.toml`). The package tests that ship in the sdist, and that run against
the installed `cd` package alone, live one level up in `tests/`.

`uv run pytest tests/` from the repository root collects both populations.

| File | What it checks |
|---|---|
| `test_paper_gate.py` | `scripts/check_paper_artifact.py` accepts only a byte-identical rebuild; its order-preserving text diagnostics locate a changed sign, operand order, fraction, minus position, digit, decimal point, multiplication glyph, exponent or dropped sentence, and its page renders locate a changed pixel |
| `test_stack_diagram.py` | the rendered SVGs carry the SHA-256 of `paper/cd_stack.dot` and the figure PDFs exist; the source parses into its five clusters with well-formed edges; Figure 2 draws the feedback path; `scripts/check_stack_citations.py` rejects a renumbered or retitled header, an unmapped citation and a number found only in figure text, and expands plural citations |
| `test_validate_notebook.py` | `scripts/validate_notebook.py` fails closed on error outputs, unexecuted cells, missing markers and too few checks, and its CLI exit codes |
| `test_validate_notebook_required.py` | the validator requires each essential claim exactly once and the completion marker after the last check; the committed notebook satisfies it |
