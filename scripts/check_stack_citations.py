#!/usr/bin/env python3
"""Check that every statement number cited in the stack diagram exists in the rebuilt paper.

The diagram source ``paper/cd_stack.dot`` names paper statements by number (for example
``Definition 3.36`` or ``Theorem 3.16``; the abbreviations ``Def.``, ``Thm``, ``Prop.``, ``Rem.`` and
``Cor.`` are read as the full kind). Numbers drift when statements are inserted, so the
paper workflow extracts the text of the freshly built PDF with ``pdftotext`` and runs::

    python3 scripts/check_stack_citations.py paper/cd_stack.dot rebuilt.txt

Every ``<Kind> <n>.<m>`` token found in the diagram must occur, as a whole token, in the
text; otherwise the missing citations are listed and the exit status is 1. This is a
numbering check, not a check of what the diagram says about each statement.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

KINDS = {
    "Definition": "Definition",
    "Def.": "Definition",
    "Theorem": "Theorem",
    "Thm.": "Theorem",
    "Thm": "Theorem",
    "Proposition": "Proposition",
    "Prop.": "Proposition",
    "Lemma": "Lemma",
    "Lem.": "Lemma",
    "Corollary": "Corollary",
    "Cor.": "Corollary",
    "Remark": "Remark",
    "Rem.": "Remark",
    "Example": "Example",
}
CITATION_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in KINDS) + r") (\d+\.\d+)\b")


def citations(dot_text: str) -> list[str]:
    """Distinct ``Kind n.m`` tokens in the diagram, in order of first appearance."""
    seen: list[str] = []
    for kind, number in CITATION_RE.findall(dot_text):
        token = f"{KINDS[kind]} {number}"
        if token not in seen:
            seen.append(token)
    return seen


def missing(dot_text: str, paper_text: str) -> list[str]:
    """Citations of the diagram that do not occur as whole tokens in the paper text."""
    return [
        token
        for token in citations(dot_text)
        if re.search(rf"\b{re.escape(token)}\b", paper_text) is None
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dot", help="the diagram source (paper/cd_stack.dot)")
    parser.add_argument("text", help="pdftotext output of the rebuilt paper")
    args = parser.parse_args(argv)
    dot_text = pathlib.Path(args.dot).read_text(encoding="utf-8")
    paper_text = pathlib.Path(args.text).read_text(encoding="utf-8", errors="replace")
    cited = citations(dot_text)
    absent = missing(dot_text, paper_text)
    print(f"diagram cites {len(cited)} statement numbers")
    if absent:
        print("not found in the paper text: " + ", ".join(absent))
        print("STACK CITATIONS MISMATCH")
        return 1
    print("STACK CITATIONS OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
