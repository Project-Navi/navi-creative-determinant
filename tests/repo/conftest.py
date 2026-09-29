"""Shared fixtures for the repository-artefact tests: the repository root, a loader for the
scripts under ``scripts/`` (a fresh module per call, as the tests always did), and a writer
for synthetic notebooks under ``tmp_path``."""

import importlib.util
import pathlib
import types

import nbformat
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_script(name: str) -> types.ModuleType:
    """Import ``scripts/<name>.py`` as a fresh module."""
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def repo_root() -> pathlib.Path:
    """The repository root (``scripts/``, ``notebooks/`` and ``paper/`` live under it)."""
    return ROOT


@pytest.fixture
def load_script():
    """``load_script("validate_notebook")`` imports ``scripts/validate_notebook.py`` fresh."""
    return _load_script


@pytest.fixture
def write_notebook(tmp_path):
    """``write_notebook(nb, name="nb.ipynb")`` writes ``nb`` under ``tmp_path``; returns the path."""

    def _write(nb, name="nb.ipynb"):
        path = tmp_path / name
        nbformat.write(nb, path)
        return path

    return _write
