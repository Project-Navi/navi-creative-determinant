#!/usr/bin/env python3
"""Render the Creative Determinant stack diagram from the single source ``cd_stack.dot``.

Outputs (all deterministic; graphviz honours ``SOURCE_DATE_EPOCH``):

* ``paper/cd_stack.svg`` and ``docs/assets/cd-stack.svg`` — the full diagram in the brand
  palette used by the documentation site (dark background, light text, teal accent);
* ``paper/cd_stack_core.pdf`` — Layer 1 only, in a print palette, for Figure 1 of the paper;
* ``paper/cd_stack_loop.pdf`` — Layers 2, 3, 4 and the deferred extension plus the two Layer 1
  nodes they connect to (``OP`` and ``LAM``), in the print palette, for Figure 2.

The source file is parsed by its cluster markers (``// ---------- NAME ----------``), so a
figure is a subset of clusters; cross-layer edges are kept only when both endpoints are in
the subset. The print palette is a fixed substitution of the brand colours, so the two
themes never drift apart in content. The SVG gets a trailing comment with the SHA-256 of
the source so that a repository test can tell when the outputs are stale.

Usage: python3 paper/stack_figures.py   (run from anywhere; paths are relative to this file)
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "cd_stack.dot"
DOCS_SVG = ROOT / "docs" / "assets" / "cd-stack.svg"
EPOCH = "1767225600"  # 2026-01-01T00:00:00Z, the same fixed date as paper/build_paper.sh

# Brand palette (docs) -> print palette (paper figures). Applied as literal substitutions.
PRINT_PALETTE = {
    '"transparent"': '"white"',
    "#1a1a1a": "#ffffff",  # node fill
    "#e8e4de": "#1a1a1a",  # text
    "#2a2a2a": "#4a4a4a",  # borders and cluster frames
    "#7eb8a8": "#2f6f60",  # accent: highlighted nodes, edges, cluster titles
    "#9a958e": "#5f5b55",  # muted: heuristic layer
    "#d4a574": "#8a5a1e",  # deferred extension
}

FIGURES = {
    # name: (clusters to keep, context nodes to keep from other clusters, graph title)
    "core": (["L1"], [], ""),
    "loop": (["L2", "L3", "L4", "EXT"], ["OP", "LAM"], ""),
}

CLUSTER_RE = re.compile(
    r"  // ---------- (\w+) ----------\n  subgraph cluster_\1 \{\n(.*?)\n  \}\n", re.S
)
NODE_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*) \[", re.M)
EDGE_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*) -> ([A-Z][A-Z0-9_]*)(\s*\[[^\]]*\])?\s*$", re.M)


def parse(text: str) -> tuple[str, dict[str, str], str]:
    """Split the source into header, cluster bodies (by marker name) and the cross-edge tail."""
    clusters = {m.group(1): m.group(0) for m in CLUSTER_RE.finditer(text)}
    first = text.index("  // ---------- ")
    header = text[:first]
    last_cluster_end = max(m.end() for m in CLUSTER_RE.finditer(text))
    tail = text[last_cluster_end:]
    return header, clusters, tail


def node_lines(block: str) -> dict[str, str]:
    """Node id -> its full definition line(s) inside a cluster block."""
    lines: dict[str, str] = {}
    current = None
    for line in block.split("\n"):
        m = NODE_RE.match(line)
        if m:
            current = m.group(1)
            lines[current] = line
        elif current and line.strip() and not EDGE_RE.match(line) and line.startswith("     "):
            lines[current] += "\n" + line  # continuation line of a multi-line node definition
        else:
            current = None
    return lines


def subset(text: str, keep: list[str], context: list[str], title: str) -> str:
    """The dot text of a figure: header, kept clusters, context nodes, and edges with both ends."""
    header, clusters, tail = parse(text)
    kept_nodes: set[str] = set()
    body = ""
    for name in keep:
        block = clusters[name]
        kept_nodes.update(node_lines(block))
        body += block
    if context:
        ctx_lines = []
        for name, block in clusters.items():
            if name in keep:
                continue
            for node, line in node_lines(block).items():
                if node in context:
                    ctx_lines.append(line)
                    kept_nodes.add(node)
        body += (
            "  subgraph cluster_context {\n"
            '    label="Layer 1 (see Figure 1)"\n    labeljust=l\n    fontname="Fraunces"\n'
            '    fontsize=14\n    fontcolor="#7eb8a8"\n    color="#2a2a2a"\n    style=dashed\n'
            "    margin=16\n\n" + "\n".join(ctx_lines) + "\n  }\n"
        )
    # cross-layer edges (and edges inside dropped clusters are gone with their clusters)
    edges = []
    for line in tail.split("\n"):
        m = EDGE_RE.match(line)
        if m and m.group(1) in kept_nodes and m.group(2) in kept_nodes:
            edges.append(line)
    # edges declared inside kept clusters whose other endpoint lives elsewhere are removed
    body_lines = []
    for line in body.split("\n"):
        m = EDGE_RE.match(line)
        if m and not (m.group(1) in kept_nodes and m.group(2) in kept_nodes):
            continue
        body_lines.append(line)
    if title:
        header = header.replace(
            "digraph cd_stack {",
            f'digraph cd_stack {{\n  label="{title}"\n  labelloc=t\n  fontname="Fraunces"\n  fontsize=14\n  fontcolor="#7eb8a8"',
        )
    return header + "\n".join(body_lines) + "\n" + "\n".join(edges) + "\n}\n"


PLABEL_RE = re.compile(r'\s*plabel="((?:[^"\\]|\\.)*)"')
LABEL_RE = re.compile(r'label="((?:[^"\\]|\\.)*)"')


def attribute_blocks(text: str) -> list[tuple[int, int]]:
    """Spans of the ``[...]`` attribute lists, ignoring brackets inside quoted strings."""
    spans: list[tuple[int, int]] = []
    i, n = 0, len(text)

    def skip_string(j: int) -> int:
        j += 1  # opening quote
        while j < n and text[j] != '"':
            j += 2 if text[j] == "\\" else 1
        return j + 1

    while i < n:
        ch = text[i]
        if ch == '"':
            i = skip_string(i)
        elif ch == "[":
            start, depth = i, 1
            i += 1
            while i < n and depth:
                c = text[i]
                if c == '"':
                    i = skip_string(i)
                    continue
                depth += (c == "[") - (c == "]")
                i += 1
            spans.append((start, i))
        else:
            i += 1
    return spans


def _map_blocks(text: str, fn) -> str:
    out, last = [], 0
    for start, end in attribute_blocks(text):
        out.append(text[last:start])
        out.append(fn(text[start:end]))
        last = end
    out.append(text[last:])
    return "".join(out)


CLUSTER_PLABEL_RE = re.compile(
    r'(    label=")((?:[^"\\]|\\.)*)("\n)    plabel="((?:[^"\\]|\\.)*)"\n'
)


def compact_labels(text: str) -> str:
    """Use each ``plabel`` (compact print text) in place of its ``label`` and drop the attribute.

    Applies to node and edge attribute lists (possibly spanning lines) and to the
    ``label``/``plabel`` line pair at the top of a cluster.
    """

    def swap(block: str) -> str:
        m = PLABEL_RE.search(block)
        if not m:
            return block
        compact = m.group(1)
        block = block[: m.start()] + block[m.end() :]
        return LABEL_RE.sub(lambda lm: f'label="{compact}"', block, count=1)

    text = _map_blocks(text, swap)
    return CLUSTER_PLABEL_RE.sub(lambda m: f"{m.group(1)}{m.group(4)}{m.group(3)}", text)


def strip_plabels(text: str) -> str:
    """Remove the ``plabel`` attributes (the docs diagram shows the full labels)."""
    text = _map_blocks(text, lambda block: PLABEL_RE.sub("", block))
    return re.sub(r'\n    plabel="(?:[^"\\]|\\.)*"', "", text)


def print_theme(text: str) -> str:
    """Compact labels and the print palette, for the paper figures."""
    text = compact_labels(text)
    for src, dst in PRINT_PALETTE.items():
        text = text.replace(src, dst)
    return text


def render(dot_text: str, fmt: str, out: pathlib.Path) -> None:
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH)
    subprocess.run(
        ["dot", f"-T{fmt}", "-o", str(out)], input=dot_text.encode(), check=True, env=env
    )


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    # Full diagram, brand palette, for the docs site (and a copy next to the source).
    svg_path = HERE / "cd_stack.svg"
    render(strip_plabels(source), "svg", svg_path)
    svg = (
        svg_path.read_text(encoding="utf-8").rstrip("\n")
        + f"\n<!-- source: cd_stack.dot sha256 {digest} -->\n"
    )
    svg_path.write_text(svg, encoding="utf-8")
    DOCS_SVG.parent.mkdir(parents=True, exist_ok=True)
    DOCS_SVG.write_text(svg, encoding="utf-8")
    # Paper figures, print palette.
    for name, (keep, context, title) in FIGURES.items():
        dot_text = print_theme(subset(source, keep, context, title))
        (HERE / f"cd_stack_{name}.dot.generated").write_text(dot_text, encoding="utf-8")
        render(dot_text, "pdf", HERE / f"cd_stack_{name}.pdf")
    print(
        f"rendered cd_stack.svg, docs/assets/cd-stack.svg, cd_stack_core.pdf, cd_stack_loop.pdf (source sha256 {digest[:12]})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
