#!/usr/bin/env python3
"""Compare the extracted text of two builds of the paper and fail on any changed content.

Both inputs are ``pdftotext -layout`` outputs. Normalization is deliberately narrow: words
hyphenated across a line break are re-joined, ASCII hyphens are dropped (so the same compound
word hyphenated at different positions compares equal; the Unicode minus sign of typeset
mathematics is kept), and the text is split on whitespace. The multisets of the resulting
tokens must agree exactly. Line-breaking and pagination differences therefore pass; a changed
theorem statement, equation, number or sentence fails, and the differing tokens are listed.

This is a drift guard between the committed PDF and the PDF rebuilt from source, not a
certificate of the mathematics.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import Counter


def normalize(text: str) -> list[str]:
    """Tokens of ``text`` after joining line-break hyphenation and dropping ASCII hyphens."""
    text = text.replace("\f", "\n")
    text = re.sub(r"-\n\s*(?=\S)", "", text)  # "solu-\ntion" -> "solution"
    text = text.replace("-", "")
    return text.split()


def compare(text_a: str, text_b: str) -> tuple[bool, list[str]]:
    """Return ``(ok, report)``; ``ok`` iff the normalized token multisets are identical."""
    ca, cb = Counter(normalize(text_a)), Counter(normalize(text_b))
    only_a, only_b = ca - cb, cb - ca
    report = [f"tokens: {sum(ca.values())} vs {sum(cb.values())}"]
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
