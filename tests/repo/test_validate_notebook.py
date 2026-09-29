"""The notebook validator must fail closed: an error output, an unexecuted cell, a missing
final marker, a failed check, or too few passed checks each reject the notebook. Negative
fixtures are built here so that the check itself is tested, not only the happy path."""

import importlib.util
import pathlib
import sys

import nbformat
import pytest
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_notebook.py"


def _load():
    spec = importlib.util.spec_from_file_location("validate_notebook", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _notebook(n_checks=3, *, error=False, unexecuted=False, marker=True, failed=False):
    cells = [new_markdown_cell("# demo")]
    for i in range(n_checks):
        out = new_output("stream", name="stdout", text=f"CHECK PASSED: claim {i}\n")
        cells.append(
            new_code_cell(f"check(True, 'claim {i}')", outputs=[out], execution_count=i + 1)
        )
    if failed:
        cells.append(
            new_code_cell(
                "x",
                outputs=[new_output("stream", name="stdout", text="CHECK FAILED: bad\n")],
                execution_count=90,
            )
        )
    if error:
        err = new_output("error", ename="AssertionError", evalue="boom", traceback=["boom"])
        cells.append(new_code_cell("assert False", outputs=[err], execution_count=91))
    if unexecuted:
        cells.append(new_code_cell("print('never ran')", outputs=[], execution_count=None))
    final_text = "ALL_NOTEBOOK_CHECKS_PASSED\n" if marker else "done\n"
    cells.append(
        new_code_cell(
            "print('end')",
            outputs=[new_output("stream", name="stdout", text=final_text)],
            execution_count=99,
        )
    )
    return new_notebook(cells=cells)


def _write(tmp_path, nb, name="nb.ipynb"):
    path = tmp_path / name
    nbformat.write(nb, path)
    return path


class TestValidator:
    def test_valid_notebook_passes(self, tmp_path):
        v = _load()
        ok, messages = v.validate(_write(tmp_path, _notebook()), min_checks=3, required=[])
        assert ok, messages

    def test_error_output_rejected(self, tmp_path):
        v = _load()
        ok, messages = v.validate(
            _write(tmp_path, _notebook(error=True)), min_checks=3, required=[]
        )
        assert not ok
        assert any("error output" in m for m in messages)

    def test_unexecuted_code_cell_rejected(self, tmp_path):
        v = _load()
        ok, messages = v.validate(
            _write(tmp_path, _notebook(unexecuted=True)), min_checks=3, required=[]
        )
        assert not ok
        assert any("not executed" in m for m in messages)

    def test_missing_final_marker_rejected(self, tmp_path):
        v = _load()
        ok, messages = v.validate(
            _write(tmp_path, _notebook(marker=False)), min_checks=3, required=[]
        )
        assert not ok
        assert any("ALL_NOTEBOOK_CHECKS_PASSED" in m for m in messages)

    def test_failed_check_text_rejected(self, tmp_path):
        v = _load()
        ok, messages = v.validate(
            _write(tmp_path, _notebook(failed=True)), min_checks=3, required=[]
        )
        assert not ok

    def test_too_few_checks_rejected(self, tmp_path):
        v = _load()
        ok, messages = v.validate(
            _write(tmp_path, _notebook(n_checks=2)), min_checks=3, required=[]
        )
        assert not ok
        assert any("checks" in m for m in messages)

    def test_cli_exit_codes(self, tmp_path):
        v = _load()
        good = _write(tmp_path, _notebook(), "good.ipynb")
        bad = _write(tmp_path, _notebook(error=True), "bad.ipynb")
        assert v.main([str(good), "--min-checks", "3", "--no-required"]) == 0
        assert v.main([str(bad), "--min-checks", "3", "--no-required"]) == 1

    def test_committed_notebook_passes_with_stored_outputs(self):
        """The committed notebook carries executed outputs; they must satisfy the validator."""
        v = _load()
        ok, messages = v.validate(ROOT / "notebooks" / "cd_pde_demo.ipynb", min_checks=30)
        assert ok, messages


@pytest.mark.skipif(sys.version_info < (3, 10), reason="project floor")
def test_script_has_main_guard():
    assert 'if __name__ == "__main__"' in SCRIPT.read_text()
