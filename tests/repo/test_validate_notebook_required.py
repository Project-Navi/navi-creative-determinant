"""The notebook validator must require each essential claim exactly once, in order, before
the completion marker; a missing or duplicated required claim fails even when enough other
CHECK PASSED lines remain."""

from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output

REQUIRED = ["claim alpha", "claim beta", "claim gamma"]


def _nb(names, marker_last=True, extra=10):
    cells = [new_markdown_cell("# demo")]
    k = 1
    for name in names:
        cells.append(
            new_code_cell(
                "x",
                outputs=[new_output("stream", name="stdout", text=f"CHECK PASSED: {name}\n")],
                execution_count=k,
            )
        )
        k += 1
    for i in range(extra):
        cells.append(
            new_code_cell(
                "y",
                outputs=[new_output("stream", name="stdout", text=f"CHECK PASSED: filler {i}\n")],
                execution_count=k,
            )
        )
        k += 1
    marker = new_code_cell(
        "z",
        outputs=[new_output("stream", name="stdout", text="ALL_NOTEBOOK_CHECKS_PASSED\n")],
        execution_count=k,
    )
    if marker_last:
        cells.append(marker)
    else:
        cells.insert(1, marker)
    return new_notebook(cells=cells)


class TestRequiredClaims:
    def test_all_required_present_passes(self, load_script, write_notebook):
        v = load_script("validate_notebook")
        ok, msgs = v.validate(write_notebook(_nb(REQUIRED)), min_checks=5, required=REQUIRED)
        assert ok, msgs

    def test_missing_required_claim_fails_despite_enough_lines(self, load_script, write_notebook):
        v = load_script("validate_notebook")
        ok, msgs = v.validate(
            write_notebook(_nb(REQUIRED[:2], extra=40)), min_checks=5, required=REQUIRED
        )
        assert not ok
        assert any("claim gamma" in m for m in msgs)

    def test_duplicated_required_claim_fails(self, load_script, write_notebook):
        v = load_script("validate_notebook")
        ok, msgs = v.validate(
            write_notebook(_nb(REQUIRED + ["claim alpha"])), min_checks=5, required=REQUIRED
        )
        assert not ok

    def test_marker_before_checks_fails(self, load_script, write_notebook):
        v = load_script("validate_notebook")
        ok, msgs = v.validate(
            write_notebook(_nb(REQUIRED, marker_last=False)), min_checks=5, required=REQUIRED
        )
        assert not ok
        assert any("marker" in m for m in msgs)

    def test_committed_notebook_contains_every_required_claim(self, load_script, repo_root):
        v = load_script("validate_notebook")
        assert len(v.REQUIRED_CHECKS) >= 12
        ok, msgs = v.validate(repo_root / "notebooks" / "cd_pde_demo.ipynb", min_checks=30)
        assert ok, msgs
