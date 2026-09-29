# The stack diagram: one source (cd_stack.dot) rendered as the brand-themed SVG for the docs
# site and as the two print-palette figures of the paper. Needs graphviz (dot) and python3.
# Rebuild the paper afterwards (paper/build_paper.sh); the figure PDFs are inputs to it.

all:
	python3 stack_figures.py

clean:
	rm -f cd_stack.svg cd_stack_core.pdf cd_stack_loop.pdf cd_stack_core.dot.generated cd_stack_loop.dot.generated ../docs/assets/cd-stack.svg

.PHONY: all clean
