"""The stack diagram has one source and its rendered outputs must be current.

``paper/cd_stack.dot`` is the single source of the docs diagram and of the two paper figures.
The renderer (``paper/stack_figures.py``) writes the SHA-256 of the source into the SVG it
produces, so an edit to the source without a regeneration is detectable without graphviz;
the two paper figure PDFs are written by the same run. These tests also check that the
source has the structure the renderer relies on (the five clusters and edges whose endpoints
are defined nodes), that Figure 2 draws the feedback path from the fields and the closure
back to the eigenvalue, and that ``scripts/check_stack_citations.py`` rejects a renumbered
or retitled statement header (including a title shortened or lengthened past the entry of
the committed diagram source), an unmapped citation, and a number that occurs only in figure
text.
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

    def test_loop_figure_draws_the_feedback_path(self, repo_root):
        """Figure 2 keeps OP -> LAM, the fields and the effective cost into the closure, and
        the closure into the operator and the interpretation (Definitions 3.36 and 3.42)."""
        renderer = _load_renderer(repo_root)
        text = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        keep, context, title = renderer.FIGURES["loop"]
        sub = renderer.subset(text, keep, context, title)
        edges = set()
        for line in sub.split("\n"):
            m = renderer.EDGE_RE.match(line)
            if m:
                edges.add((m.group(1), m.group(2)))
        for edge in [
            ("OP", "LAM"),
            ("LAM", "PSIS"),
            ("FIELDS", "BDEF"),
            ("LAMEFF", "BDEF"),
            ("OP", "BDEF"),
            ("BDEF", "INTERP"),
        ]:
            assert edge in edges, edge

    def test_finite_graph_theorem_is_not_fed_by_the_continuum(self, repo_root):
        """Theorem 3.26 has its own node with no edge from the continuum model or its
        eigenvalue (Remark 3.33: the models are distinct)."""
        renderer = _load_renderer(repo_root)
        text = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        incoming = [
            m.group(1)
            for m in (renderer.EDGE_RE.match(line) for line in text.split("\n"))
            if m and m.group(2) == "FGRAPH"
        ]
        assert "PDE" not in incoming and "LAM" not in incoming
        assert "Theorem 3.26" not in renderer.node_lines(renderer.parse(text)[1]["L1"])["RESULTS"]

    def test_finite_graph_node_names_all_three_hypotheses(self, repo_root):
        """Theorem 3.26 assumes a connected interior graph, λ₁ᴳ < 0 and the edge condition
        a(x), a(y) ≤ √w(x,y) for distinct interior x, y with w(x,y) > 0, and concludes
        u(x) > 0 at every interior vertex; the full label (docs) and the compact label
        (Figure 1) both state all three hypotheses and the conclusion."""
        renderer = _load_renderer(repo_root)
        text = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        line = renderer.node_lines(renderer.parse(text)[1]["L1"])["FGRAPH"]
        docs = renderer.strip_plabels(line)
        paper = renderer.compact_labels(line)
        assert docs != paper
        for label in (docs, paper):
            assert "interior graph connected" in label, label
            assert "λ₁ᴳ < 0" in label, label
            assert "edge condition a(x), a(y) ≤ √w(x,y)" in label, label
            assert "distinct" in label and "w(x,y) > 0" in label, label
            assert "u(x) > 0" in label, label


class TestCitationCheck:
    DOT = (
        "// cites: Theorem 3.12 = Existence of a nonnegative\n"
        "// cites: Definition 3.38 = Coherence debt dynamics\n"
        "// cites: Remark 3.39 = Interpretation\n"
        "// cites: Section 3.7 = Temporal resilience\n"
        'A [label="Existence (Theorem 3.12)"]\n'
        'B [label="Debt (Definition 3.38),\\nbound (Remark 3.39), Section 3.7"]\n'
    )
    PAPER = (
        "Theorem 3.12 (Existence of a nonnegative weak coherent configuration). Assume\n"
        "text Definition 3.38 (Coherence\ndebt dynamics). Fix parameters\n"
        "Remark 3.39 (Interpretation: asymmetric cost of mismatch). The\n"
        "3.7\n\nTemporal resilience and coherence debt: unpacking\n"
    )

    def _check(self, checker, dot, paper):
        cmap = checker.citation_map(dot)
        return checker.unmapped(checker.citations(dot), cmap), checker.missing_headers(cmap, paper)

    def test_matching_headers_pass(self, load_script):
        """Headers wrapped across lines by pdftotext still match after normalization."""
        checker = load_script("check_stack_citations")
        assert self._check(checker, self.DOT, self.PAPER) == ([], [])

    def test_a_renumbered_header_fails(self, load_script):
        checker = load_script("check_stack_citations")
        paper = self.PAPER.replace("Definition 3.38 (", "Definition 3.37 (")
        assert self._check(checker, self.DOT, paper)[1] == [
            "Definition 3.38 (Coherence debt dynamics)"
        ]

    def test_a_renumbered_section_fails(self, load_script):
        checker = load_script("check_stack_citations")
        paper = self.PAPER.replace("3.7\n", "3.8\n")
        assert self._check(checker, self.DOT, paper)[1] == ["Section 3.7 (Temporal resilience)"]

    def test_a_changed_title_fails(self, load_script):
        """The number exists but now names a different statement of the same kind."""
        checker = load_script("check_stack_citations")
        paper = self.PAPER.replace("(Coherence\ndebt dynamics)", "(Debt bound)")
        assert self._check(checker, self.DOT, paper)[1] == [
            "Definition 3.38 (Coherence debt dynamics)"
        ]

    def test_an_unmapped_citation_fails(self, load_script, tmp_path):
        checker = load_script("check_stack_citations")
        dot = self.DOT + 'C [label="Closure (Definition 3.42)"]\n'
        assert self._check(checker, dot, self.PAPER)[0] == ["Definition 3.42"]
        docs = tmp_path / "page.md"
        docs.write_text("The loop (Remark 3.41) is a tendency.\n")
        dot_file = tmp_path / "s.dot"
        dot_file.write_text(self.DOT)
        paper_file = tmp_path / "paper.txt"
        paper_file.write_text(self.PAPER)
        assert checker.main([str(dot_file), str(paper_file)]) == 0
        assert checker.main([str(dot_file), str(paper_file), "--also", str(docs)]) == 1

    def test_plural_citations_are_expanded(self, load_script):
        checker = load_script("check_stack_citations")
        text = (
            "(Definitions 3.34, 3.38, 3.40 and 3.42) Remarks 3.41 and 3.43; "
            "Theorems 3.12, 3.16; Sections 2–3; Theorem 3.26, 3 more"
        )
        assert checker.citations(text) == [
            "Definition 3.34",
            "Definition 3.38",
            "Definition 3.40",
            "Definition 3.42",
            "Remark 3.41",
            "Remark 3.43",
            "Theorem 3.12",
            "Theorem 3.16",
            "Section 2",
            "Section 3",
            "Theorem 3.26",
        ]

    def test_figure_text_alone_does_not_satisfy_the_check(self, load_script):
        """A number printed only in a figure, "(Definition 3.38)", is not a header."""
        checker = load_script("check_stack_citations")
        paper = self.PAPER.replace(
            "text Definition 3.38 (Coherence\ndebt dynamics). Fix parameters\n",
            "Coherence debt (Definition 3.38)\nḊ = η[ψ − ψₛ]⁺ − ρD\n",
        )
        assert self._check(checker, self.DOT, paper)[1] == [
            "Definition 3.38 (Coherence debt dynamics)"
        ]

    def test_partial_number_does_not_match(self, load_script):
        """A header of Theorem 3.1 does not satisfy the entry for Theorem 3.12."""
        checker = load_script("check_stack_citations")
        paper = self.PAPER.replace("Theorem 3.12 (", "Theorem 3.1 (")
        assert self._check(checker, self.DOT, paper)[1] == [
            "Theorem 3.12 (Existence of a nonnegative)"
        ]

    # Entries in the form of the committed source: a statement title runs through the character
    # that closes it; pdftotext puts a space between the subscript of ψs and the ")", which the
    # check allows.
    ANCHORED_DOT = (
        "// cites: Theorem 3.26 = Positive solution on a finite graph;\n"
        "// cites: Remark 3.37 = Meaning of ψs)\n"
        "// cites: Remark 3.44 = Capacity erosion as a future-work extension)\n"
        'A [label="Theorem 3.26, Remark 3.37, Remark 3.44"]\n'
    )
    ANCHORED_PAPER = (
        "Theorem 3.26 (Positive solution on a finite graph; Lean: SemioticGraph.exists pos graph).\n"
        "Remark 3.37 (Meaning of ψs ). The mapping (8) converts\n"
        "Remark 3.44 (Capacity erosion as a future-work extension). A natural\n"
    )

    def test_anchored_entries_match_the_paper_headers(self, load_script):
        checker = load_script("check_stack_citations")
        assert self._check(checker, self.ANCHORED_DOT, self.ANCHORED_PAPER) == ([], [])

    def test_a_truncated_title_fails(self, load_script):
        """Dropping the subscript of ψs, or a word, is a changed title."""
        checker = load_script("check_stack_citations")
        for old, new, token in [
            ("(Meaning of ψs )", "(Meaning of ψ)", "Remark 3.37"),
            ("(Meaning of ψs )", "(Meaning of ψ and D)", "Remark 3.37"),
            ("(Meaning of ψs )", "(Meaning of ψs and D)", "Remark 3.37"),
            ("on a finite graph;", "on a graph;", "Theorem 3.26"),
            ("future-work extension)", "future-work)", "Remark 3.44"),
        ]:
            paper = self.ANCHORED_PAPER.replace(old, new)
            missing = self._check(checker, self.ANCHORED_DOT, paper)[1]
            assert [m.split(" (")[0] for m in missing] == [token], (new, missing)

    def test_an_extended_title_fails(self, load_script):
        """A title that runs on past the entry is a changed title."""
        checker = load_script("check_stack_citations")
        for old, new, token in [
            ("on a finite graph;", "on a finite graph with a loop;", "Theorem 3.26"),
            ("on a finite graph;", "on finite graphs;", "Theorem 3.26"),
            ("future-work extension)", "future-work extensions)", "Remark 3.44"),
        ]:
            paper = self.ANCHORED_PAPER.replace(old, new)
            missing = self._check(checker, self.ANCHORED_DOT, paper)[1]
            assert [m.split(" (")[0] for m in missing] == [token], (new, missing)

    def test_committed_statement_entries_are_anchored(self, repo_root, load_script):
        """Every statement entry of the committed source ends in the character that closes
        its title (")" or ";")."""
        checker = load_script("check_stack_citations")
        dot = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        for token, title in checker.citation_map(dot).items():
            if token.startswith("Section "):
                continue
            assert title.endswith((")", ";")), (token, title)

    def test_the_committed_sources_cite_only_mapped_statements(self, repo_root, load_script):
        """Every citation in the diagram and on the CD Stack page has a cites: line."""
        checker = load_script("check_stack_citations")
        dot = (repo_root / "paper" / "cd_stack.dot").read_text(encoding="utf-8")
        docs = (repo_root / "docs" / "explanation" / "cd-stack.md").read_text(encoding="utf-8")
        cmap = checker.citation_map(dot)
        cited = checker.citations(dot) + checker.citations(docs)
        assert len(set(cited)) >= 20
        assert checker.unmapped(cited, cmap) == []
        assert all(
            re.fullmatch(r"(Definition|Theorem|Proposition|Remark) \d+\.\d+|Section \d+(\.\d+)?", c)
            for c in cited
        )
