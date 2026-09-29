"""The stack diagram has one source and its rendered outputs must be current.

``paper/cd_stack.dot`` is the single source of the docs diagram and of the two paper figures.
The renderer (``paper/stack_figures.py``) writes the SHA-256 of the source into the SVG it
produces, so an edit to the source without a regeneration is detectable without graphviz;
the two paper figure PDFs are written by the same run. These tests also check that the
source has the structure the renderer relies on (the five clusters and edges whose endpoints
are defined nodes) and that ``scripts/check_stack_citations.py`` rejects a stale number.
"""

import hashlib
import importlib.util
import re

STACK_CLUSTERS = {"L1", "L2", "L3", "L4", "EXT"}


def _load_renderer(repo_root):
    path = repo_root / "paper" / "stack_figures.py"
    spec = importlib.util.spec_from_file_location("stack_figures", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRenderedOutputsAreCurrent:
    def test_svgs_carry_the_source_hash(self, repo_root):
        """Both SVG copies end with the SHA-256 of the current source."""
        source = (repo_root / "paper" / "cd_stack.dot").read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        for path in (
            repo_root / "paper" / "cd_stack.svg",
            repo_root / "docs" / "assets" / "cd-stack.svg",
        ):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"<!-- source: cd_stack\.dot sha256 ([0-9a-f]{64}) -->\s*$", text)
            assert match, f"{path.name} has no source-hash comment; run make -C paper"
            assert match.group(1) == digest, f"{path.name} is stale; run make -C paper"

    def test_docs_copy_equals_paper_copy(self, repo_root):
        a = (repo_root / "paper" / "cd_stack.svg").read_bytes()
        b = (repo_root / "docs" / "assets" / "cd-stack.svg").read_bytes()
        assert a == b

    def test_paper_figures_exist_and_are_pdfs(self, repo_root):
        for name in ("cd_stack_core.pdf", "cd_stack_loop.pdf"):
            data = (repo_root / "paper" / name).read_bytes()
            assert data.startswith(b"%PDF-"), name


class TestSourceStructure:
    def test_clusters_and_edges_are_well_formed(self, repo_root):
        """The renderer's parser finds the five clusters, and every edge joins defined nodes."""
        renderer = _load_renderer(repo_root)
        text = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        header, clusters, tail = renderer.parse(text)
        assert set(clusters) == STACK_CLUSTERS
        nodes = set()
        for block in clusters.values():
            nodes.update(renderer.node_lines(block))
        for line in text.split("\n"):
            m = renderer.EDGE_RE.match(line)
            if m:
                assert m.group(1) in nodes and m.group(2) in nodes, line.strip()

    def test_figure_subsets_keep_only_internal_edges(self, repo_root):
        """A figure built from a subset of clusters contains no edge to a dropped node."""
        renderer = _load_renderer(repo_root)
        text = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        for keep, context, title in renderer.FIGURES.values():
            sub = renderer.subset(text, keep, context, title)
            defined = set(renderer.NODE_RE.findall(sub))
            for line in sub.split("\n"):
                m = renderer.EDGE_RE.match(line)
                if m:
                    assert m.group(1) in defined and m.group(2) in defined, line.strip()


class TestCitationCheck:
    DOT = 'A [label="Existence (Theorem 3.12)"]\nB [label="Debt (Definition 3.38), bound (Remark 3.39)"]\n'

    def test_all_cited_numbers_present_passes(self, load_script):
        checker = load_script("check_stack_citations")
        text = "Theorem 3.12 (Existence)\nDefinition 3.38 (Coherence debt)\nRemark 3.39 (Bound)\n"
        assert checker.missing(self.DOT, text) == []

    def test_a_stale_number_is_reported(self, load_script):
        checker = load_script("check_stack_citations")
        text = "Theorem 3.12 (Existence)\nDefinition 3.37 (Coherence debt)\nRemark 3.39 (Bound)\n"
        assert checker.missing(self.DOT, text) == ["Definition 3.38"]

    def test_partial_number_does_not_match(self, load_script):
        """'Theorem 3.1' in the text must not satisfy a citation of Theorem 3.12."""
        checker = load_script("check_stack_citations")
        text = "Theorem 3.1 (c = 0)\nDefinition 3.38\nRemark 3.39\n"
        assert checker.missing(self.DOT, text) == ["Theorem 3.12"]

    def test_cli_exit_codes(self, load_script, tmp_path):
        checker = load_script("check_stack_citations")
        dot = tmp_path / "s.dot"
        dot.write_text(self.DOT)
        good = tmp_path / "good.txt"
        good.write_text("Theorem 3.12\nDefinition 3.38\nRemark 3.39\n")
        bad = tmp_path / "bad.txt"
        bad.write_text("Theorem 3.12\nRemark 3.39\n")
        assert checker.main([str(dot), str(good)]) == 0
        assert checker.main([str(dot), str(bad)]) == 1

    def test_the_committed_diagram_cites_only_numbers_of_the_current_kinds(
        self, repo_root, load_script
    ):
        """Every citation in the real source has a recognised kind and a section.number form."""
        checker = load_script("check_stack_citations")
        text = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        cited = checker.citations(text)
        assert len(cited) >= 15
        assert all(
            re.fullmatch(r"(Definition|Theorem|Proposition|Remark) \d+\.\d+", c) for c in cited
        )
