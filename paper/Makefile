# The stack diagram: one source (cd_stack.dot) rendered by stack_figures.py as the brand-themed SVG
# for the docs site and as the two print-palette figures of the paper, in the pinned environment of
# figures.Dockerfile (needs docker; see build_figures.sh). Rebuild the paper afterwards
# (paper/build_paper.sh); the figure PDFs are inputs to it.

# render and install the four outputs
all:
	./build_figures.sh update

# render into a temporary directory and require the committed outputs to be identical
check:
	./build_figures.sh check

.PHONY: all check
