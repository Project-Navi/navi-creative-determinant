"""The paper artifact gate must reject every changed statement and accept only identical builds.

``scripts/check_paper_artifact.py`` requires byte identity between the committed PDF and the
PDF rebuilt in the pinned TeX Live image. Its diagnostics (order-preserving text comparison and
page renders) must locate each of the changes a reviewer could make to a theorem: a changed
sign, reversed inequality operands, a swapped numerator and denominator, a moved minus sign, a
changed digit, a moved decimal point, a changed multiplication glyph, an altered exponent and a
dropped sentence. None of these may pass because the document is long.

These tests exercise the repository script, not the ``cd`` package, so they live in
``tests/repo`` and are not shipped in the sdist.
"""

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_paper_artifact.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_paper_artifact", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


FILLER = "\n".join(
    f"Remark 3.{i}. The estimate is uniform in the truncation level and the proof is routine."
    for i in range(1, 400)
)
PAGE1 = (
    "Proposition 3.19. Assume a ≡ 0. Then a positive solution exists if and only if λ1 < 0.\n"
    "Proposition 3.21. With a = 1, b = 3/4, c = 1 and p = 2 the eigenvalue is 1 − 3/4 = 1/4 > 0.\n"
    "Example. Take a = −1; b = 1 and the constant 7.75; the product a ⋅ b and the power u^2.\n"
)
BASE = PAGE1 + FILLER + "\f" + FILLER + "\nLast page sentence.\n\f"

MUTATIONS = {
    "changed theorem sign": ("λ1 < 0", "λ1 > 0"),
    "reversed inequality operands": ("λ1 < 0", "0 < λ1"),
    "swapped numerator and denominator": ("= 1/4 > 0", "= 4/1 > 0"),
    "moved minus sign": ("a = −1; b = 1", "a = 1; b = −1"),
    "changed digit": ("p = 2", "p = 3"),
    "moved decimal point": ("7.75", "77.5"),
    "changed multiplication glyph": ("a ⋅ b", "a b"),
    "altered exponent": ("u^2", "u^3"),
    "dropped sentence": ("Last page sentence.\n", ""),
}


class TestTextSequence:
    def test_identical_text_is_identical(self):
        gate = _load()
        ok, report = gate.compare_text(BASE, BASE)
        assert ok, report

    def test_rewrapped_lines_are_the_same_sequence(self):
        gate = _load()
        rewrapped = BASE.replace("if and only if λ1 < 0.", "if and only if\nλ1 < 0.")
        ok, _ = gate.compare_text(BASE, rewrapped)
        assert ok

    @pytest.mark.parametrize("name", sorted(MUTATIONS))
    def test_each_statement_change_is_detected_and_located(self, name):
        gate = _load()
        old, new = MUTATIONS[name]
        assert BASE.count(old) == 1, name
        mutated = BASE.replace(old, new)
        ok, report = gate.compare_text(BASE, mutated)
        assert not ok, name
        located = [line for line in report if line.startswith("  p")]
        assert located, report
        page = "p2" if name == "dropped sentence" else "p1"
        assert located[0].startswith(f"  {page}/"), report

    def test_a_dropped_page_is_detected(self):
        gate = _load()
        ok, report = gate.compare_text(BASE, BASE.replace("\f" + FILLER, "", 1))
        assert not ok
        assert report[0].startswith("text: 2 pages") and "vs 1 pages" in report[0]


def _pgm(width: int, height: int, fill: int) -> bytes:
    return b"P5\n# comment\n%d %d\n255\n" % (width, height) + bytes([fill]) * (width * height)


class TestPageRenders:
    def test_identical_pages_report_no_difference(self, tmp_path):
        gate = _load()
        a = tmp_path / "a-01.pgm"
        b = tmp_path / "b-01.pgm"
        a.write_bytes(_pgm(4, 3, 255))
        b.write_bytes(_pgm(4, 3, 255))
        report = gate.compare_pages([a], [b])
        assert report[-1] == "render: all common pages identical"

    def test_a_single_changed_pixel_is_reported_with_its_page(self, tmp_path):
        gate = _load()
        a = tmp_path / "a-01.pgm"
        b = tmp_path / "b-01.pgm"
        a.write_bytes(_pgm(4, 3, 255))
        b.write_bytes(_pgm(4, 3, 255)[:-1] + b"\x00")
        report = gate.compare_pages([a], [b])
        assert "  page 1: 1/12 pixels differ" in report[1]
        assert report[-1] == "render: 1 page(s) differ"

    def test_different_page_counts_are_reported(self, tmp_path):
        gate = _load()
        a = tmp_path / "a-01.pgm"
        a.write_bytes(_pgm(2, 2, 0))
        report = gate.compare_pages([a], [])
        assert "render: page counts differ" in report


def _minimal_pdf(text: str) -> bytes:
    """A valid one-page PDF with a text string (enough for pdftotext and pdftoppm)."""
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
            + b"/Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return bytes(out)


class TestByteIdentityGate:
    def test_identical_files_pass(self, tmp_path, capsys):
        gate = _load()
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(_minimal_pdf("lambda_1 < 0"))
        b.write_bytes(a.read_bytes())
        assert gate.main([str(a), str(b)]) == 0
        assert "ARTIFACT IDENTICAL" in capsys.readouterr().out

    def test_any_byte_difference_fails_and_is_explained(self, tmp_path, capsys):
        gate = _load()
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(_minimal_pdf("lambda_1 < 0"))
        b.write_bytes(_minimal_pdf("0 < lambda_1"))
        assert gate.main([str(a), str(b)]) == 1
        out = capsys.readouterr().out
        assert "ARTIFACT MISMATCH" in out
        assert "diagnostics unavailable" in out or "differing run(s)" in out

    def test_metadata_only_difference_still_fails(self, tmp_path, capsys):
        """Byte identity is the rule: a change confined to metadata is not accepted."""
        gate = _load()
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(_minimal_pdf("same text"))
        b.write_bytes(a.read_bytes().replace(b"/Root 1 0 R", b"/Root 1 0 R /Info null"))
        assert gate.main([str(a), str(b)]) == 1
        out = capsys.readouterr().out
        assert "ARTIFACT MISMATCH" in out
        assert "diagnostics unavailable" in out or "text sequence: identical" in out
