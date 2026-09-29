# Repository-artefact tests

The tests in this directory exercise repository artefacts that live outside the
Python package: `scripts/` (the notebook validator and the paper artifact gate),
`notebooks/cd_pde_demo.ipynb` and, through the gate, `paper/`. They resolve the
repository root as `Path(__file__).resolve().parents[2]` and need a full checkout,
plus `nbformat` from the dev dependency group (the paper gate's unit tests need only the standard library; its diagnostics use poppler when present).

They are excluded from the source distribution (`[tool.hatch.build.targets.sdist]`
in `pyproject.toml`). The package tests that ship in the sdist, and that run against
the installed `cd` package alone, live one level up in `tests/`.

`uv run pytest tests/` from the repository root collects both populations.

| File | What it checks |
|---|---|
| `test_paper_gate.py` | `scripts/check_paper_artifact.py` accepts only a byte-identical rebuild; its order-preserving text diagnostics locate every statement change a reviewer could make (sign, operand order, fraction, minus position, digit, decimal point, multiplication glyph, exponent, dropped sentence) and its page renders locate a changed pixel |
| `test_validate_notebook.py` | `scripts/validate_notebook.py` fails closed on error outputs, unexecuted cells, missing markers and too few checks; the committed notebook passes |
| `test_validate_notebook_required.py` | the validator requires each essential claim exactly once and the completion marker after the last check; the committed notebook satisfies it |
