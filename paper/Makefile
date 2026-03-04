DIAGRAM=cd_stack
DOT=$(DIAGRAM).dot

all: $(DIAGRAM).svg $(DIAGRAM).pdf $(DIAGRAM).png

$(DIAGRAM).svg: $(DOT)
	dot -Tsvg $(DOT) -o $@

$(DIAGRAM).pdf: $(DOT)
	dot -Tpdf $(DOT) -o $@

$(DIAGRAM).png: $(DOT)
	dot -Tpng -Gdpi=200 $(DOT) -o $@

clean:
	rm -f $(DIAGRAM).svg $(DIAGRAM).pdf $(DIAGRAM).png

.PHONY: all clean
