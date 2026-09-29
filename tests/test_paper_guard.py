"""The paper guard must reject a changed mathematical statement, not merely a dissimilar file.

The comparison works on the extracted text of the committed and rebuilt PDFs: hyphenated line
breaks are joined and whitespace is collapsed, then the multisets of tokens must agree exactly.
Line-breaking differences pass; a changed equation or theorem line fails.
"""

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compare_paper_text.py"


def _load():
    spec = importlib.util.spec_from_file_location("compare_paper_text", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BASE = "\n".join(
    [
        f"Theorem 3.{i} (Result {i}). Assume lambda_1 < 0. Then a positive solu-\ntion exists."
        for i in range(1, 40)
    ]
)


class TestPaperTextGuard:
    def test_identical_text_passes(self):
        v = _load()
        ok, report = v.compare(BASE, BASE)
        assert ok, report

    def test_different_line_breaks_and_hyphenation_pass(self):
        v = _load()
        rewrapped = BASE.replace("solu-\ntion", "solution").replace(". Then", ".\nThen")
        ok, report = v.compare(BASE, rewrapped)
        assert ok, report

    def test_one_changed_theorem_line_fails(self):
        v = _load()
        changed = BASE.replace(
            "Theorem 3.20 (Result 20). Assume lambda_1 < 0.",
            "Theorem 3.20 (Result 20). Assume lambda_1 > 0.",
        )
        ok, report = v.compare(BASE, changed)
        assert not ok
        assert any("lambda_1" in line or ">" in line for line in report)

    def test_dropped_sentence_fails(self):
        v = _load()
        ok, _ = v.compare(BASE, BASE.replace("Then a positive solu-\ntion exists.", "", 1))
        assert not ok

    def test_cli(self, tmp_path):
        v = _load()
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text(BASE)
        b.write_text(BASE.replace("lambda_1 < 0", "lambda_1 > 0", 1))
        assert v.main([str(a), str(a)]) == 0
        assert v.main([str(a), str(b)]) == 1
