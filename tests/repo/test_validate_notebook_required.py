"""The notebook validator must require each essential claim exactly once and the completion
marker after the last check; a missing or duplicated required claim fails even when enough other
CHECK PASSED lines remain. The committed notebook must satisfy the required list, and the list
must be complete, duplicate-free and in the notebook's own order so the two cannot drift apart
silently."""

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
        ok, msgs = v.validate(repo_root / "notebooks" / "cd_pde_demo.ipynb", min_checks=30)
        assert ok, msgs

    def test_required_list_is_complete_and_duplicate_free(self, load_script):
        """The list names 36 essential claims and no name twice (a duplicate would make the
        exactly-once rule unsatisfiable)."""
        v = load_script("validate_notebook")
        assert len(v.REQUIRED_CHECKS) == 36
        assert len(set(v.REQUIRED_CHECKS)) == len(v.REQUIRED_CHECKS)

    def test_required_claims_follow_the_notebook_order(self, load_script, repo_root):
        """The required names occur in the committed notebook in list order, so a reader can
        follow the list against the notebook and a reordering of sections is noticed."""
        import nbformat

        v = load_script("validate_notebook")
        nb = nbformat.read(repo_root / "notebooks" / "cd_pde_demo.ipynb", as_version=4)
        printed = []
        for cell in nb.cells:
            if cell.cell_type != "code":
                continue
            for out in cell.get("outputs", []):
                if out.get("output_type") == "stream":
                    for line in out.get("text", "").splitlines():
                        if line.startswith("CHECK PASSED: "):
                            printed.append(line[len("CHECK PASSED: ") :])
        required = set(v.REQUIRED_CHECKS)
        assert [name for name in printed if name in required] == v.REQUIRED_CHECKS
