#!/usr/bin/env python3
"""Artifact-identity gate between the committed paper PDF and the PDF rebuilt from source.

The committed ``paper/creative_determinant.pdf`` and the CI rebuild are both produced by
``paper/build_paper.sh`` in the same pinned TeX Live image with a fixed ``SOURCE_DATE_EPOCH``,
so the build is deterministic and the gate requires **byte identity** (equal SHA-256). Nothing
weaker is accepted: no similarity threshold, no bag of characters, no dropped symbols.

When the bytes differ the script explains where, so that the owner can see whether the drift
is a source change that needs a rebuild or an environment change that needs the pin updated:

* an order-preserving comparison of the extracted text (``pdftotext`` in reading order, split
  on whitespace, no other normalization) that lists the first differing token runs with their
  page numbers; and
* a page-by-page render comparison (``pdftoppm`` at a modest resolution) that lists the pages
  whose pixels differ and the fraction of differing pixels.

Both explanations use the same poppler binaries for both files, so they never introduce a
difference of their own. They are diagnostics: the exit status is 0 only for identical bytes.

This gate verifies the relation between the committed artifact and its source. It does not
certify the mathematics in the paper.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import pathlib
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence

DEFAULT_DPI = 50
MAX_HUNKS = 12
CONTEXT = 6


def sha256(path: pathlib.Path) -> str:
    """Hex SHA-256 of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tokens_by_page(text: str) -> list[list[str]]:
    """Whitespace-separated tokens of each page (pages are separated by form feeds)."""
    pages = text.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    return [page.split() for page in pages]


def compare_text(text_a: str, text_b: str) -> tuple[bool, list[str]]:
    """Order-preserving comparison of two extracted texts.

    Returns ``(identical, report)``. The token sequences (with page boundaries) must agree
    exactly; the report lists the first differing runs with page numbers and a little context.
    """
    pages_a, pages_b = tokens_by_page(text_a), tokens_by_page(text_b)
    flat_a = [(i + 1, t) for i, page in enumerate(pages_a) for t in page]
    flat_b = [(i + 1, t) for i, page in enumerate(pages_b) for t in page]
    seq_a = [t for _, t in flat_a]
    seq_b = [t for _, t in flat_b]
    report = [
        f"text: {len(pages_a)} pages / {len(seq_a)} tokens vs {len(pages_b)} pages / {len(seq_b)} tokens"
    ]
    if seq_a == seq_b and len(pages_a) == len(pages_b):
        report.append("text sequence: identical")
        return True, report
    matcher = difflib.SequenceMatcher(a=seq_a, b=seq_b, autojunk=False)
    hunks = [op for op in matcher.get_opcodes() if op[0] != "equal"]
    report.append(f"text sequence: {len(hunks)} differing run(s)")
    for tag, i1, i2, j1, j2 in hunks[:MAX_HUNKS]:
        page_a = flat_a[min(i1, len(flat_a) - 1)][0] if flat_a else 0
        page_b = flat_b[min(j1, len(flat_b) - 1)][0] if flat_b else 0
        before = " ".join(seq_a[max(0, i1 - CONTEXT) : i1])
        old = " ".join(seq_a[i1:i2])
        new = " ".join(seq_b[j1:j2])
        report.append(
            f"  p{page_a}/p{page_b} {tag}: ...{before} [{old}] -> [{new}]"
            if before
            else f"  p{page_a}/p{page_b} {tag}: [{old}] -> [{new}]"
        )
    if len(hunks) > MAX_HUNKS:
        report.append(f"  ... {len(hunks) - MAX_HUNKS} more")
    return False, report


def _read_pgm(path: pathlib.Path) -> tuple[int, int, bytes]:
    """Parse a binary (P5) PGM written by ``pdftoppm -gray``."""
    data = path.read_bytes()
    fields: list[bytes] = []
    pos = 0
    while len(fields) < 4:
        while data[pos : pos + 1].isspace():
            pos += 1
        if data[pos : pos + 1] == b"#":
            while data[pos : pos + 1] not in (b"\n", b""):
                pos += 1
            continue
        start = pos
        while not data[pos : pos + 1].isspace():
            pos += 1
        fields.append(data[start:pos])
    pos += 1  # single whitespace byte after maxval
    if fields[0] != b"P5":
        raise ValueError(f"{path}: not a binary PGM")
    width, height = int(fields[1]), int(fields[2])
    return width, height, data[pos : pos + width * height]


def compare_pages(pages_a: Sequence[pathlib.Path], pages_b: Sequence[pathlib.Path]) -> list[str]:
    """Compare rendered pages pixel for pixel; report the pages that differ."""
    report = [f"render: {len(pages_a)} vs {len(pages_b)} pages"]
    if len(pages_a) != len(pages_b):
        report.append("render: page counts differ")
    differing = 0
    for number, (pa, pb) in enumerate(zip(pages_a, pages_b), start=1):
        wa, ha, ra = _read_pgm(pa)
        wb, hb, rb = _read_pgm(pb)
        if (wa, ha) != (wb, hb):
            report.append(f"  page {number}: size {wa}x{ha} vs {wb}x{hb}")
            differing += 1
            continue
        if ra == rb:
            continue
        diff = sum(1 for x, y in zip(ra, rb) if x != y)
        differing += 1
        report.append(
            f"  page {number}: {diff}/{len(ra)} pixels differ ({100.0 * diff / len(ra):.2f}%)"
        )
    report.append(
        "render: all common pages identical"
        if differing == 0
        else f"render: {differing} page(s) differ"
    )
    return report


def _run(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, check=True, capture_output=True)


def explain(committed: pathlib.Path, rebuilt: pathlib.Path, dpi: int) -> list[str]:
    """Diagnostics for two PDFs whose bytes differ (needs pdftotext and pdftoppm)."""
    report: list[str] = []
    if shutil.which("pdftotext") is None or shutil.which("pdftoppm") is None:
        return ["diagnostics unavailable: pdftotext/pdftoppm not found"]
    try:
        report.extend(_explain_with_poppler(committed, rebuilt, dpi))
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        report.append(f"diagnostics failed: {exc}")
    return report


def _explain_with_poppler(committed: pathlib.Path, rebuilt: pathlib.Path, dpi: int) -> list[str]:
    report: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        texts = []
        for name, pdf in (("committed", committed), ("rebuilt", rebuilt)):
            out = tmp_path / f"{name}.txt"
            _run(["pdftotext", "-enc", "UTF-8", str(pdf), str(out)])
            texts.append(out.read_text(encoding="utf-8", errors="replace"))
        _, text_report = compare_text(texts[0], texts[1])
        report.extend(text_report)
        pages = []
        for name, pdf in (("committed", committed), ("rebuilt", rebuilt)):
            prefix = tmp_path / name
            _run(["pdftoppm", "-gray", "-r", str(dpi), str(pdf), str(prefix)])
            pages.append(sorted(tmp_path.glob(f"{name}-*.pgm")))
        report.extend(compare_pages(pages[0], pages[1]))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("committed", help="the committed paper PDF")
    parser.add_argument("rebuilt", help="the PDF rebuilt by paper/build_paper.sh")
    parser.add_argument(
        "--dpi", type=int, default=DEFAULT_DPI, help="render resolution for diagnostics"
    )
    args = parser.parse_args(argv)
    committed, rebuilt = pathlib.Path(args.committed), pathlib.Path(args.rebuilt)
    digest_a, digest_b = sha256(committed), sha256(rebuilt)
    print(f"committed sha256 {digest_a}")
    print(f"rebuilt   sha256 {digest_b}")
    if digest_a == digest_b:
        print("ARTIFACT IDENTICAL")
        return 0
    print("ARTIFACT MISMATCH: the committed PDF is not the byte-identical build of the source")
    for line in explain(committed, rebuilt, args.dpi):
        print(line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
