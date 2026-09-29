#!/usr/bin/env python3
"""Check the statement and section citations of the stack diagram against the rebuilt paper.

``paper/cd_stack.dot`` holds one comment line per cited statement or section, giving its
title as printed in the paper; a statement title runs through the character that closes it::

    // cites: Definition 3.36 = Spectral capacity witness)
    // cites: Section 3.7 = Temporal resilience and coherence debt

The paper workflow extracts the text of the freshly built PDF with ``pdftotext`` and runs::

    python3 scripts/check_stack_citations.py paper/cd_stack.dot rebuilt.txt \\
        --also docs/explanation/cd-stack.md

The check fails when

* a citation in the diagram or in an ``--also`` file has no ``cites:`` line (singular forms
  such as ``Remark 3.37``, plural lists such as ``Definitions 3.34, 3.38, 3.40 and 3.42`` or
  ``Remarks 3.41 and 3.43``, and ``Section 3.7`` / ``Sections 2–3`` are all read; the
  abbreviations ``Def.``, ``Thm``, ``Prop.``, ``Rem.``, ``Lem.`` and ``Cor.`` count as the full
  kind); or
* the paper text has no statement header ``<Kind> <n.m> (<title>`` for a ``cites:`` line
  (the title through its closing character, so a shortened or lengthened title fails), or no
  section header ``<n.m> <title start>`` for a section. Whitespace is normalized first, since
  ``pdftotext`` wraps lines, and a space before the closing character is allowed.

Figure text never has the header form, so a number printed only inside Figures 1 and 2 does
not satisfy the check.
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
    "Section": "Section",
}
PLURALS = {f"{kind}s": kind for kind in set(KINDS.values())}

_NUMBER = r"\d+(?:\.\d+)?"
_SEPARATOR = r"(?:\s*,\s*(?:and\s+)?|\s+and\s+|\s*[–-]\s*|\s+to\s+)"
_KIND_ALTERNATION = "|".join(
    re.escape(k) for k in sorted([*KINDS, *PLURALS], key=len, reverse=True)
)
CITATION_RE = re.compile(
    rf"(?<![\w.])({_KIND_ALTERNATION})\s+({_NUMBER}(?:{_SEPARATOR}{_NUMBER})*)(?![\w.]*\d)"
)
MAP_RE = re.compile(
    rf"^\s*//\s*cites:\s*(\w+)\s+({_NUMBER})\s*=\s*(.+?)\s*$",
    re.M,
)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _strip_map(text: str) -> str:
    # drop the map lines and read the dot line breaks \n and \l inside labels as spaces
    return re.sub(r"\\[nl]", " ", MAP_RE.sub("", text))


def citations(text: str) -> list[str]:
    """Distinct ``Kind n.m`` / ``Section n[.m]`` tokens, in order of first appearance.

    Plural forms are expanded into one token per listed number; the ``cites:`` map lines
    themselves are ignored.
    """
    seen: list[str] = []
    for match in CITATION_RE.finditer(_normalize(_strip_map(text))):
        word, numbers = match.group(1), match.group(2)
        kind = KINDS.get(word) or PLURALS[word]
        listed = re.findall(_NUMBER, numbers)
        if word not in PLURALS:
            listed = listed[:1]  # "Theorem 3.12, 3.16" names one theorem, then a bare number
        for number in listed:
            if kind != "Section" and "." not in number:
                continue  # statements are numbered n.m
            token = f"{kind} {number}"
            if token not in seen:
                seen.append(token)
    return seen


def citation_map(dot_text: str) -> dict[str, str]:
    """``Kind n.m`` (or ``Section n[.m]``) -> expected title, from ``cites:`` lines."""
    entries: dict[str, str] = {}
    for kind, number, title in MAP_RE.findall(dot_text):
        if kind not in KINDS.values():
            raise ValueError(f"unknown kind in cites line: {kind}")
        entries[f"{kind} {number}"] = _normalize(title)
    return entries


def unmapped(cited: list[str], cmap: dict[str, str]) -> list[str]:
    """Cited tokens that have no ``cites:`` line."""
    return [token for token in cited if token not in cmap]


def header_pattern(token: str, title: str) -> re.Pattern[str]:
    """The header a ``cites:`` entry requires in the normalized paper text."""
    kind, number = token.split(" ", 1)
    if kind == "Section":
        return re.compile(rf"(?<![\w.]){re.escape(number)} {re.escape(title)}")
    if title[-1:] in (")", ";", ":"):
        # pdftotext may put a space before the closing character (after a subscript)
        body = re.escape(title[:-1]) + " ?" + re.escape(title[-1])
    else:
        body = re.escape(title)
    return re.compile(rf"(?<![\w.]){kind} {re.escape(number)} \( ?{body}")


def missing_headers(cmap: dict[str, str], paper_text: str) -> list[str]:
    """``cites:`` entries whose header (number and title) is absent from the paper text."""
    text = _normalize(paper_text)
    return [
        f"{token} ({title})"
        for token, title in cmap.items()
        if header_pattern(token, title).search(text) is None
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dot", help="the diagram source (paper/cd_stack.dot)")
    parser.add_argument("text", help="pdftotext output of the rebuilt paper")
    parser.add_argument(
        "--also",
        action="append",
        default=[],
        metavar="FILE",
        help="another file whose citations must be in the map (repeatable)",
    )
    args = parser.parse_args(argv)
    dot_text = pathlib.Path(args.dot).read_text(encoding="utf-8")
    paper_text = pathlib.Path(args.text).read_text(encoding="utf-8", errors="replace")
    cmap = citation_map(dot_text)
    cited = citations(dot_text)
    for extra in args.also:
        for token in citations(pathlib.Path(extra).read_text(encoding="utf-8")):
            if token not in cited:
                cited.append(token)
    no_entry = unmapped(cited, cmap)
    absent = missing_headers(cmap, paper_text)
    print(f"{len(cited)} statements and sections cited; {len(cmap)} expected headers")
    if no_entry:
        print("cited without a 'cites:' line in the diagram source: " + ", ".join(no_entry))
    if absent:
        print("header not found in the paper text: " + ", ".join(absent))
    if no_entry or absent:
        print("STACK CITATIONS MISMATCH")
        return 1
    print("STACK CITATIONS OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
