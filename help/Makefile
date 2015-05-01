SOURCES := $(wildcard src/*.md)
OUTPUTS := $(subst src,build,$(SOURCES:.md=.html))

all: $(OUTPUTS) build/noise-model.svg

build/%.html: src/%.md
	pandoc -s $< -o $@

print-%:
	@echo '$*=$($*)'

build/%.svg: static/%.svg
	cp $< $@
