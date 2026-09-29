#!/usr/bin/env python3
"""Compare the extracted text of two builds of the paper and fail on any changed content.

Both inputs are ``pdftotext -layout`` outputs. The comparison is made on the multiset of
content characters: whitespace is ignored (pdftotext places it differently around subscripts
and inside fractions depending on the TeX Live and poppler versions), ASCII hyphens are dropped
(hyphenation at a line break; the Unicode minus sign of typeset mathematics is kept), and
control and format characters (Unicode categories Cc, Cf, Co, Cn) and centred-dot glyphs are
dropped (the same glyph is extracted as U+2022 or as a C0/C1 control by different font maps). Every other character must occur the same number of
times in both texts. Line-breaking, pagination and extraction-order differences therefore pass;
any changed, added or removed letter, digit or sign fails, and the differing characters are
listed.

Limitation: a rearrangement of the same characters (for instance two digits swapped within one
fraction) is not detected. A token-level comparison was tried first and rejected the paper on
a different TeX Live version for extraction-order differences alone.

This is a drift guard between the committed PDF and the PDF rebuilt from source, not a
certificate of the mathematics.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import unicodedata
from collections import Counter

_DOT_GLYPHS = frozenset("\u2022\u00b7\u22c5")  # bullet, middle dot, dot operator


def normalize(text: str) -> Counter[str]:
    """Multiset of the content characters of ``text`` (see the module docstring)."""
    return Counter(
        ch
        for ch in text
        if not ch.isspace()
        and ch != "-"
        and not unicodedata.category(ch).startswith("C")
        and ch not in _DOT_GLYPHS
    )


def compare(text_a: str, text_b: str) -> tuple[bool, list[str]]:
    """Return ``(ok, report)``; ``ok`` iff the normalized character multisets are identical."""
    ca, cb = normalize(text_a), normalize(text_b)
    only_a, only_b = ca - cb, cb - ca
    report = [f"characters: {sum(ca.values())} vs {sum(cb.values())}"]
    if only_a:
        report.append(
            f"only in first ({sum(only_a.values())}): "
            + " ".join(f"{t}x{n}" if n > 1 else t for t, n in list(only_a.items())[:40])
        )
    if only_b:
        report.append(
            f"only in second ({sum(only_b.values())}): "
            + " ".join(f"{t}x{n}" if n > 1 else t for t, n in list(only_b.items())[:40])
        )
    ok = not only_a and not only_b
    report.append("TEXT MATCH" if ok else "TEXT MISMATCH")
    return ok, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("first", help="pdftotext output of the committed PDF")
    parser.add_argument("second", help="pdftotext output of the rebuilt PDF")
    args = parser.parse_args(argv)
    a = pathlib.Path(args.first).read_text(encoding="utf-8", errors="replace")
    b = pathlib.Path(args.second).read_text(encoding="utf-8", errors="replace")
    ok, report = compare(a, b)
    print("\n".join(report))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
