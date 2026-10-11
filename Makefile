# Build the Bhagavad Gita PDF.
#   make            -> build/bhagavad-gita.pdf
#   make TRANSLATOR=purohit
#   make clean
TRANSLATOR ?= siva
BUILD      := build
NAME       := bhagavad-gita
TEX        := $(BUILD)/$(NAME).tex
PDF        := $(BUILD)/$(NAME).pdf
JSON       := $(wildcard slok/*.json) $(wildcard chapter/*.json)
TEXINPUTS  := ./tex:

.PHONY: all pdf tex clean

all: pdf
pdf: $(PDF)
tex: $(TEX)

$(TEX): tools/gen_tex.py $(JSON) | $(BUILD)
	python3 tools/gen_tex.py --root . --translator $(TRANSLATOR) -o $@

$(PDF): $(TEX) tex/preamble.tex tex/titlepage.tex
	TEXINPUTS="$(TEXINPUTS)" latexmk -lualatex -interaction=nonstopmode -halt-on-error \
	  -output-directory=$(BUILD) $(TEX)

$(BUILD):
	mkdir -p $(BUILD)

clean:
	rm -rf $(BUILD)
